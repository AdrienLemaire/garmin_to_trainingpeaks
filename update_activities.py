#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tp
import json

WORKOUT_URL = 'https://tpapi.trainingpeaks.com' + \
              '/fitness/v4/athletes/%d/workouts/%s'


if __name__ == '__main__':

    username, password = open("trainingpeaks.key").read().rstrip().split(':')
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

            res = tpconnect.session.put(url, jeez)
            if res.status_code != 200:
                print("There was an error updating workout id: " + str(
                    workout_id))
                break

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
