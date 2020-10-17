# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import tp
import json
import geopy.geocoders as geo

MAX_DISTANCE = 10000
WORKOUT_URL = 'https://tpapi.trainingpeaks.com' + \
              '/fitness/v4/athletes/%d/workouts/%s'

POSTCODE_COMMUTE = ('75008', '93310', '75019', '93500')

if __name__ == '__main__':

    geolocator = geo.Nominatim()
    username = 'chmouel'
    password = subprocess.Popen(
        ["security", "find-generic-password", "-a",
         "chmouel", "-s", "trainingpeaks", "-w"],
        stdout=subprocess.PIPE
    ).communicate()[0].strip()

    tpconnect = tp.TPconnect(username, password)
    datetoption = {
        'back': {'days': -7},
        'front': {'days': 0}
    }
    activities = json.loads(tpconnect.get_workouts(datetoption))

    for jeez in activities:
        workout_id = jeez['workoutId']
        url = WORKOUT_URL % (tpconnect.athlete_id, workout_id)

        if 'workoutTypeValueId' not in jeez:
            continue

        if int(jeez['workoutTypeValueId']) != 2:  # not a cycling
            continue

        # only parse small distances
        if jeez['distance'] and int(jeez['distance']) >= MAX_DISTANCE:
            continue

        detailUrl = "https://tpapi.trainingpeaks.com/" + \
                    "fitness/v2/athletes/%s/workouts/%s/detaildata" % (
                        tpconnect.athlete_id,
                        jeez['workoutId'])
        resp = tpconnect.session.get(detailUrl)
        if resp.status_code != 200:
            print(resp)
            print(resp._content)
            raise Exception("Cannot get athlete activities")

        if not jeez['title'] or jeez['title'] == 'Commute':
            detaildata = json.loads(resp._content)
            gpsd = detaildata['boundingBox']
            start = geolocator.reverse("%s, %s" %
                                       (gpsd[0][0], gpsd[0][1]), language='en')
            end = geolocator.reverse("%s, %s" %
                                     (gpsd[1][0], gpsd[1][1]), language='en')

            if start.raw['address']['postcode'] in POSTCODE_COMMUTE and \
               end.raw['address']['postcode'] in POSTCODE_COMMUTE:
                jeez['title'] = 'Velotaf'
            else:
                jeez['title'] = 'Commute'

            res = tpconnect.session.put(url, jeez)
            if res.status_code != 200:
                print("There was an error updating workout id: " + str(
                    workout_id))
                break

        # only parse activities without power
        if jeez['powerAverage']:
            continue

        # only do when we have hr
        if not jeez['heartRateAverage']:
            continue

        # only do it when we have a TSS
        if not jeez['tssActual']:
            continue

        jeez['tssActual'] = "0"

        res = tpconnect.session.put(url, jeez)
        if res.status_code != 200:
            print("There was an error updating workout id: " + str(workout_id))
            break
