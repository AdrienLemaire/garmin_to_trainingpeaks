#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tp
import json
from pathlib import Path

WORKOUT_URL = 'https://tpapi.trainingpeaks.com/fitness/v5/athletes/{}/workouts/{}'



def update_distance_if_indoor_cycling(activity):
    if activity['activityName'] == "Indoor Cycling":
        distance = activity['distance']
        day, start_time = activity['startTimeLocal'].split()
        tp_activities = json.loads(tpconnect.get_workouts_for_day(day))
        try:
            indoor_cycling = [a for a in tp_activities 
                    if a['title'] == 'Indoor Cycling'
                    and a['startTime'] == '{}T{}'.format(day, start_time)
            ][0]
        except:
            print("[indoor cycling] Couldn't find the workout startTime={}T{} in trainingpeaks".format(
               day, start_time 
            ))
            return
        workout_id = indoor_cycling['workoutId']

        if indoor_cycling['distance'] == distance:
            print('.', end='')
            return  # no point sending a request with the same data

        indoor_cycling['distance'] = distance
        url = WORKOUT_URL.format(tpconnect.athlete_id, workout_id)

        res = tpconnect.session.put(url, indoor_cycling)
        if res.status_code != 200:
            print("[{}] Error when updating".format(workout_id))
            return

        print("[{}] distance: {}".format(workout_id, distance))



if __name__ == '__main__':

    path = input("path to the garmin activities.json file:")
    garmin_activities = json.loads(open(Path(path).resolve()).read())

    username, password = open("trainingpeaks.key").read().rstrip().split(':')
    tpconnect = tp.TPconnect(username, password)


    for activity in garmin_activities:
        update_distance_if_indoor_cycling(activity)
