#!/usr/bin/python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The main script for starting exit speed."""
import datetime
import multiprocessing
import os
from time import sleep

import pytz
import sdnotify
from absl import app
from absl import logging

#import accelerometer
import common_lib
import config_lib
import exit_speed_pb2
import gps_sensor
#import gyroscope
#import labjack
import lap_lib
import leds
import postgres
#import tire_temperature
import tracks
#import wbo2


class ExitSpeed(object):
  """Main object which loops and logs data."""

  trackname = "Finding"
  carname = "Identifying"
  starttime = 1
  lapnumber = 0
  lapminutes = 1
  lapseconds = 1
  blap_starttime_ns = 0
  lap_starttime_ns = 0

  def __init__(
      self,
      start_finish_range=20,  # Meters, ~4x the width of straightaways.
      live_data=True,
      min_points_per_lap=60 * 10):  # 60 seconds @ gps 10hz):
    """Initializer.

    Args:
      start_finish_range: Maximum distance a point can be considered when
                          determining if the car crosses the start/finish.
      live_data: A boolean, if True indicates that this session's data should be
                 tagged as live.
      min_points_per_lap:  Used to prevent laps from prematurely ending.
    """
    self.start_finish_range = start_finish_range
    self.live_data = live_data
    self.min_points_per_lap = min_points_per_lap
    self.point_queue = multiprocessing.Queue()

    self.config = config_lib.LoadConfig()
    self.leds = leds.LEDs()
    self.postgres = None
    self.session = None
    self.lap_number = 1
    self.current_lap = []
    self.laps = {self.lap_number: self.current_lap}
    self.point = None
    self.sdnotify = sdnotify.SystemdNotifier()
    self.sdnotify.notify('READY=1')
    self.lap_minutes = 0
    self.lap_seconds = 0
    self.lap_start_time_ns = 0


  def InitializeSubProcesses(self):
    """Initialize subprocess modules based on config.yaml."""
    if self.config.get('postgres'):
      self.postgres = postgres.PostgresWithoutPrepare()
    self.ProcessSession()
    if self.config.get('gps'):
      self.gps = gps_sensor.GPSProcess(
          self.session, self.config, self.point_queue)

  def AddNewLap(self) -> None:
    """Adds a new lap to the current session."""
    self.lap_number += 1
    self.current_lap = []
    self.laps[self.lap_number] = self.current_lap
    lapnumber = self.lap_number
    print('Lap number:', lapnumber)
    self.lap_start_time_ns = self.point.time.ToNanoseconds()
    print("New lap starttime " + str(self.lap_start_time_ns))
    if self.config.get('postgres'):
      self.postgres.AddToQueue(
          postgres.LapStart(number=self.lap_number,
                            start_time=self.point.time.ToDatetime(
                                tzinfo=pytz.UTC)))

  def ProcessPoint(self) -> None:
    """Updates LEDs, logs point and writes data to PostgresSQL."""
    point = self.point
    self.leds.UpdateLeds(point)

  def SetLapTime(self) -> None:
    """Sets the lap duration based on the first and last point time delta."""
    duration_ns = lap_lib.CalcLastLapDuration(self.session.track, self.laps)
    self.leds.SetBestLap(self.current_lap, duration_ns)
    leds.LEDs.setbestlap_identify = self.leds.set_bestlap
    if leds.LEDs.setbestlap_identify == 1:
      ExitSpeed.blap_starttime_ns = self.lap_start_time_ns
      print("New bestlap starttime " + str(ExitSpeed.blap_starttime_ns))
    minutes = duration_ns / 1e9 // 60
    seconds = (duration_ns / 1e6 % 60000) / 1000.0
    self.lap_minutes = minutes
    self.lap_seconds = seconds
    logging.info('New Lap %d:%.03f', minutes, seconds)
    print('New Lap %d:%.03f' % (minutes, seconds))
    if self.config.get('postgres'):
      self.postgres.AddToQueue(postgres.LapEnd(
          end_time=self.point.time.ToDatetime(tzinfo=pytz.UTC),
          duration_ns=int(duration_ns)))

  def CrossStartFinish(self) -> None:
    """Checks and handles when the car crosses the start/finish."""
    logging.log_every_n_seconds(
        logging.INFO,
        'Current lap length: %s',
        10,
        len(self.current_lap))
    if len(self.current_lap) >= self.min_points_per_lap:
      prior_point = lap_lib.GetPriorUniquePoint(self.current_lap, self.point)
      start_finish_distance = common_lib.PointDeltaFromTrack(
          self.session.track, self.point)
      if (start_finish_distance < self.start_finish_range and
          # First point past start/finish has an obtuse angle.
          lap_lib.SolvePointBAngle(
              self.session.track, prior_point, self.point) > 90):
        logging.info('Start/Finish')
        print('Start/Finish')
        self.leds.CrossStartFinish()
        self.SetLapTime()
        self.AddNewLap()
        # Start and end laps on the same point just past start/finish.
        self.current_lap.append(prior_point)
    self.current_lap.append(self.point)

  def ProcessLap(self) -> None:
    """Adds the point to the lap and checks if we crossed start/finish."""
    self.ProcessPoint()
    self.CrossStartFinish()

  def ProcessSession(self) -> None:
    """Populates the session proto."""
    gps = gps_sensor.GPS()
    report = None
    while not report:
      report = gps.GetReport()
    track = tracks.FindClosestTrack(report)
    session_time = datetime.datetime.today().astimezone(pytz.UTC)
    self.session = common_lib.Session(
      time=session_time,
      track=track,
      car=self.config['car'],
      live_data=self.live_data)
    logging.info('Closest track: %s', track.name)
    print('Closest track:', track.name)
    if self.config.get('postgres'):
      self.postgres.AddToQueue(self.session)
      self.postgres.AddToQueue(
          postgres.LapStart(number=self.lap_number,
                            start_time=self.session.time))

  def Run(self) -> None:
    """Runs exit speed in a loop."""
    self.InitializeSubProcesses()
    while True:
      self.point = exit_speed_pb2.Gps().FromString(self.point_queue.get())
      self.ProcessLap()
      logging.log_every_n_seconds(
          logging.INFO,
          'Main: Point queue size currently at %d.',
          10,
          self.point_queue.qsize())
      self.sdnotify.notify(
          'STATUS=Last report time:%s' % self.point.time.ToJsonString())
      self.sdnotify.notify('WATCHDOG=1')
      
      ExitSpeed.trackname = self.session.track.name
      ExitSpeed.carname = self.config['car']
      ExitSpeed.starttime = self.session.time
      ExitSpeed.lapnumber = self.lap_number
      ExitSpeed.lapminutes = self.lap_minutes
      ExitSpeed.lapseconds = self.lap_seconds
      leds.LEDs.comparedata = self.leds.median_delta
      leds.LEDs.bestlapminutes = self.leds.best_lap_minutes
      leds.LEDs.bestlapseconds = self.leds.best_lap_seconds
      leds.LEDs.bestspeed = self.leds.best_speed_kph
      ExitSpeed.lap_starttime_ns = self.lap_start_time_ns
      leds.LEDs.bptime_ns = self.leds.best_point_time_ns
      leds.LEDs.ptime_ns = self.leds.point_time_ns

      if terminate == True:
        break

def main(unused_argv) -> None:
  logging.get_absl_handler().use_absl_log_file()
  es = None
  
  global terminate
  terminate = False

  try:
      logging.info('Starting Run')
      print('Starting Run')
      es = ExitSpeed()
      es.Run()
  except KeyboardInterrupt:
    logging.info('Keyboard interrupt')
  finally:
    if hasattr(es, 'point'):
      logging.info('Logging last point\n %s', es.point)
      print('Logging last point\n %s' % (es.point))
    logging.info('Done.\nExiting.')
    print('Done.\nExiting.')
    logging.exception('Ensure we log any exceptions')

    print('Comparison mode terminated')
    sleep (0.5)
    os.system('sudo systemctl stop gpsd')

def start():
  os.system('sudo systemctl start gpsd')
  sleep (0.5)
  app.run(main)

def termination():
  global terminate
  terminate = True
  print('termination on')

def get_trackname():
  return ExitSpeed.trackname
def get_carname():
  return ExitSpeed.carname
def get_start_time():
  return ExitSpeed.starttime
def get_lap_number():
  return ExitSpeed.lapnumber
def get_lap_minutes():
  return ExitSpeed.lapminutes
def get_lap_seconds():
  return ExitSpeed.lapseconds
def get_compare_data():
  return leds.LEDs.comparedata
def get_bestlap_minutes():
  return leds.LEDs.bestlapminutes
def get_bestlap_seconds():
  return leds.LEDs.bestlapseconds
def get_bestspeed():
  return leds.LEDs.bestspeed
def get_time_compare_data():
  bestlap_duration_ns = leds.LEDs.bptime_ns - ExitSpeed.blap_starttime_ns
  lap_duration_ns = leds.LEDs.ptime_ns - ExitSpeed.lap_starttime_ns
  time_compare_data = (lap_duration_ns - bestlap_duration_ns) / 1e9
  return time_compare_data


if __name__ == '__main__':
  start()