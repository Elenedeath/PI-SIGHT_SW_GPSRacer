#!/usr/bin/python3
# Copyright 2021 Google LLC
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
"""Track list and helper functions."""
from typing import Tuple

import gps

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import common_lib
import exit_speed_pb2
from tracks import base
from tracks import map_1
from tracks import map_2
from tracks import portland_international_raceway
from tracks import taebaek_speedway
from tracks import pocheon_raceway
from tracks import paju_speedpark
from tracks import kic_national
from tracks import kic_gp
from tracks import kic_kart
from tracks import inje_speedium
from tracks import amg_everland_speedway

TRACK_LIST = (
    map_1.Map1,
    map_2.Map2,
    portland_international_raceway.PortlandInternationalRaceway,
    amg_everland_speedway.AMGEverlandSpeedway,
    inje_speedium.InjeSpeedium,
    kic_gp.KICgp,
    kic_kart.KICkart,
    kic_national.KICnational,
    paju_speedpark.PajuSpeedpark,
    pocheon_raceway.PocheonRaceway,
    taebaek_speedway.TaebaekSpeedway
    )


def FindClosestTrack(report: gps.client.dictwrapper) -> base.Track:
  """Returns the distance, track and start/finish of the closest track."""
  distance_track = []
  for track in TRACK_LIST:
    lat, lon = track.start_finish
    track_point = exit_speed_pb2.Gps(lat=lat, lon=lon)
    report_point = exit_speed_pb2.Gps(lat=report['lat'],
																			lon=report['lon'])
    distance = common_lib.PointDelta(report_point, track_point)
    distance_track.append((distance, track))
  return sorted(distance_track)[0][1]
