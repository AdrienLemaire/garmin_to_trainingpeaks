#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tp
import json
from pathlib import Path

TP_DOMAIN = 'https://tpapi.trainingpeaks.com/'
WORKOUT_URL = TP_DOMAIN + 'fitness/v5/athletes/{}/workouts/{}'
RECALC_TSS = TP_DOMAIN + 'fitness/v1/athletes/{}/commands/workouts/{}/recalctss'


def get_tp_equivalent_activity(title, garmin_activity):
    day, start_time = garmin_activity['startTimeLocal'].split()
    tp_activities = json.loads(tpconnect.get_workouts_for_day(day))
    try:
        return [a for a in tp_activities 
                if a['title'] == title
                and a['startTime'] == '{}T{}'.format(day, start_time)
        ][0]
    except:
        print("[{}] Couldn't find the workout startTime={}T{} in trainingpeaks".format(
           title, day, start_time 
        ))
        return


def update_distance_if_indoor_cycling(activity):
    """
    Distances for indoor cycling are updated after the session is completed, but
    Garmin will have already sent the activity to TrainingPeaks with 0km
    """
    indoor_cycling = get_tp_equivalent_activity('Indoor Cycling', activity)
    if not indoor_cycling:
        return
    workout_id = indoor_cycling['workoutId']
    distance = activity['distance']

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


def recalculate_tss_if_running(activity):
    """
    Somehow, I get insane TSS values for running activities. Recalculating rTSS
    looks reasonable.
    """
    running = get_tp_equivalent_activity('Running', activity)
    if not running or running['tssSource'] == 2:  # 2 = rTSS
        return

    workout_id = running['workoutId']
    payload = {"value": "runPace"}
    url = RECALC_TSS.format(tpconnect.athlete_id, workout_id)

    res = tpconnect.session.post(url, payload)
    if res.status_code != 200:
        print("[{}] Error when recalculating tss".format(workout_id))
        return

    print("[{}] {}TSS => {}rTSS".format(workout_id, running['tssActual'], res.json()['tssActual']))


if __name__ == '__main__':

    path = input("path to the garmin activities.json file:")
    garmin_activities = json.loads(open(Path(path).resolve()).read())
    print("{} garmin activities found".format(len(garmin_activities)))

    username, password = open("trainingpeaks.key").read().rstrip().split(':')
    tpconnect = tp.TPconnect(username, password)
    print("Connected to TrainingPeaks")


    for activity in garmin_activities:
        if activity['activityName'] == "Indoor Cycling":
            update_distance_if_indoor_cycling(activity)
        if activity['activityType']['typeKey'] == 'running':
            recalculate_tss_if_running(activity)
