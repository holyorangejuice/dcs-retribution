from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Type

from game.utils import feet
from .ibuilder import IBuilder
from .planningerror import PlanningError
from .standard import StandardFlightPlan, StandardLayout
from .waypointbuilder import WaypointBuilder

if TYPE_CHECKING:
    from ..flightwaypoint import FlightWaypoint


@dataclass
class FerryLayout(StandardLayout):
    def iter_waypoints(self) -> Iterator[FlightWaypoint]:
        yield self.departure
        yield from self.nav_to
        yield self.arrival
        if self.divert is not None:
            yield self.divert
        yield self.bullseye


class FerryFlightPlan(StandardFlightPlan[FerryLayout]):
    @staticmethod
    def builder_type() -> Type[Builder]:
        return Builder

    @property
    def tot_waypoint(self) -> FlightWaypoint:
        return self.layout.arrival

    def tot_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        # TOT planning isn't really useful for ferries. They're behind the front
        # lines so no need to wait for escorts or for other missions to complete.
        return None

    def depart_time_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        return None

    @property
    def mission_begin_on_station_time(self) -> datetime | None:
        return None

    @property
    def mission_departure_time(self) -> datetime:
        return self.package.time_over_target


class Builder(IBuilder[FerryFlightPlan, FerryLayout]):
    def layout(self) -> FerryLayout:
        if self.flight.departure == self.flight.arrival:
            raise PlanningError(
                f"Cannot plan ferry self.flight: departure and arrival are both "
                f"{self.flight.departure}"
            )

        altitude_is_agl = self.flight.is_helo
        altitude = (
            feet(self.coalition.game.settings.heli_cruise_alt_agl)
            if altitude_is_agl
            else self.flight.unit_type.preferred_patrol_altitude
        )

        builder = WaypointBuilder(self.flight)
        return FerryLayout(
            departure=builder.takeoff(self.flight.departure),
            nav_to=builder.nav_path(
                self.flight.departure.position,
                self.flight.arrival.position,
                altitude,
                altitude_is_agl,
            ),
            arrival=builder.land(self.flight.arrival),
            divert=builder.divert(self.flight.divert),
            bullseye=builder.bullseye(),
            nav_from=[],
        )

    def build(self, dump_debug_info: bool = False) -> FerryFlightPlan:
        return FerryFlightPlan(self.flight, self.layout())
