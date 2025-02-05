from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Type

from game.utils import feet
from .ibuilder import IBuilder
from .standard import StandardFlightPlan, StandardLayout
from .waypointbuilder import WaypointBuilder
from ..flightstate import InFlight

if TYPE_CHECKING:
    from ..flightwaypoint import FlightWaypoint


@dataclass
class RtbLayout(StandardLayout):
    abort_location: FlightWaypoint

    def iter_waypoints(self) -> Iterator[FlightWaypoint]:
        yield self.departure
        yield self.abort_location
        yield from self.nav_to
        yield self.arrival
        if self.divert is not None:
            yield self.divert
        yield self.bullseye


class RtbFlightPlan(StandardFlightPlan[RtbLayout]):
    @staticmethod
    def builder_type() -> Type[Builder]:
        return Builder

    @property
    def abort_index(self) -> int:
        return 1

    @property
    def tot_waypoint(self) -> FlightWaypoint:
        return self.layout.abort_location

    def tot_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        return None

    def depart_time_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        return None

    @property
    def mission_begin_on_station_time(self) -> datetime | None:
        return None

    @property
    def mission_departure_time(self) -> datetime:
        return self.tot


class Builder(IBuilder[RtbFlightPlan, RtbLayout]):
    def layout(self) -> RtbLayout:
        if not isinstance(self.flight.state, InFlight):
            raise RuntimeError(f"Cannot abort {self} because it is not in flight")

        current_position = self.flight.state.estimate_position()
        current_altitude, altitude_reference = self.flight.state.estimate_altitude()

        altitude_is_agl = self.flight.is_helo
        altitude = (
            feet(self.coalition.game.settings.heli_cruise_alt_agl)
            if altitude_is_agl
            else self.flight.unit_type.preferred_patrol_altitude
        )
        builder = WaypointBuilder(self.flight)
        abort_point = builder.nav(
            current_position, current_altitude, altitude_reference == "RADIO"
        )
        abort_point.name = "ABORT AND RTB"
        abort_point.pretty_name = "Abort and RTB"
        abort_point.description = "Abort mission and return to base"
        return RtbLayout(
            departure=builder.takeoff(self.flight.departure),
            abort_location=abort_point,
            nav_to=builder.nav_path(
                current_position,
                self.flight.arrival.position,
                altitude,
                altitude_is_agl,
            ),
            arrival=builder.land(self.flight.arrival),
            divert=builder.divert(self.flight.divert),
            bullseye=builder.bullseye(),
            nav_from=[],
        )

    def build(self, dump_debug_info: bool = False) -> RtbFlightPlan:
        return RtbFlightPlan(self.flight, self.layout())
