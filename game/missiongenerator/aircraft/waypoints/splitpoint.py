from dcs.point import MovingPoint
from dcs.task import (
    OptECMUsing,
    OptFormation,
    RunScript,
    SetUnlimitedFuelCommand,
    SwitchWaypoint,
)

from game.utils import knots
from .pydcswaypointbuilder import PydcsWaypointBuilder


class SplitPointBuilder(PydcsWaypointBuilder):
    def add_tasks(self, waypoint: MovingPoint) -> None:
        # Unlimited fuel option : enable at split. Must be first option to work.
        if self.flight.squadron.coalition.game.settings.ai_unlimited_fuel:
            waypoint.tasks.insert(0, SetUnlimitedFuelCommand(True))

        if not self.flight.flight_type.is_air_to_air:
            # Capture any non A/A type to avoid issues with SPJs that use the primary radar such as the F/A-18C.
            # You can bully them with STT to not be able to fire radar guided missiles at you,
            # so best choice is to not let them perform jamming for now.

            # Let the AI use ECM to defend themselves.
            ecm_option = OptECMUsing(value=OptECMUsing.Values.UseIfOnlyLockByRadar)
            waypoint.tasks.append(ecm_option)

        if self.flight.is_helo:
            waypoint.tasks.append(OptFormation.rotary_wedge())
        else:
            waypoint.tasks.append(OptFormation.finger_four_close())
        waypoint.speed_locked = True
        waypoint.ETA_locked = False
        if self.flight.is_helo:
            waypoint.speed = knots(100).meters_per_second
        else:
            waypoint.speed = self.flight.coalition.doctrine.rtb_speed.meters_per_second
        if self.flight is self.package.primary_flight:
            script = RunScript(
                f'trigger.action.setUserFlag("split-{id(self.package)}", true)'
            )
            waypoint.tasks.append(script)
        elif self.flight.flight_type.is_escort_type:
            index = len(self.group.points)
            self.group.add_trigger_action(SwitchWaypoint(None, index))
