from enum import Enum

from dcs import task
from dcs.planes import PlaneType

from game.modsupport import planemod


@planemod
class Superbug_AITanker(PlaneType):
    id = "Superbug_AITanker"
    group_size_max = 1
    height = 4.66
    width = 13.62456
    length = 17.07
    fuel_max = 13154
    max_speed = 1950.12
    chaff = 120
    flare = 60
    charge_total = 240
    chaff_charge_size = 1
    flare_charge_size = 2
    tacan = True
    radio_frequency = 305

    livery_name = "SUPERBUG_AITANKER"  # from type

    pylons = set()

    tasks = [task.Refueling]
    task_default = task.Refueling
