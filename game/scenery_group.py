from __future__ import annotations

from typing import Iterable, List, TYPE_CHECKING, Optional

from dcs.mapping import Polygon
from dcs.triggers import TriggerZone, TriggerZoneCircular, TriggerZoneQuadPoint

from game.data.groups import GroupTask
from game.theater.theatergroundobject import NAME_BY_CATEGORY

if TYPE_CHECKING:
    from dcs.mapping import Point


def _point_in_zone(zone: TriggerZone, pos: Point) -> bool:
    if isinstance(zone, TriggerZoneCircular):
        return zone.position.distance_to_point(pos) < zone.radius
    elif isinstance(zone, TriggerZoneQuadPoint):
        return Polygon(pos._terrain, zone.verticies).point_in_poly(pos)
    raise RuntimeError(f"Invalid trigger-zone: {zone.name}")


class SceneryGroupError(RuntimeError):
    """Error for when there are insufficient conditions to create a SceneryGroup."""

    pass


class SceneryGroup:
    """Store information about a scenery objective."""

    def __init__(
        self, zone_def: TriggerZone, zones: Iterable[TriggerZone], category: str
    ) -> None:
        self.zone_def = zone_def
        self.zones = zones
        self.position = zone_def.position
        self.category = category

    @staticmethod
    def from_trigger_zones(trigger_zones: Iterable[TriggerZone]) -> List[SceneryGroup]:
        """Define scenery objectives based on their encompassing blue/red circle."""
        zone_definitions = []
        white_zones = []

        scenery_groups = []

        # Aggregate trigger zones into different groups based on color.
        for zone in trigger_zones:
            if SceneryGroup.is_blue(zone):
                zone_definitions.append(zone)
            if SceneryGroup.is_white(zone):
                white_zones.append(zone)

        # For each objective definition.
        for zone_def in zone_definitions:
            zone_def_name = zone_def.name

            if len(zone_def.properties) == 0:
                raise SceneryGroupError(
                    "Undefined SceneryGroup category in TriggerZone: " + zone_def_name
                )

            # Arbitrary campaign design requirement:  First property must define the category.
            zone_def_category = zone_def.properties[1].get("value").lower()

            valid_white_zones = []

            for zone in list(white_zones):
                if _point_in_zone(zone_def, zone.position):
                    valid_white_zones.append(zone)
                    white_zones.remove(zone)

            if len(valid_white_zones) > 0 and zone_def_category in NAME_BY_CATEGORY:
                scenery_groups.append(
                    SceneryGroup(zone_def, valid_white_zones, zone_def_category)
                )
            elif len(valid_white_zones) == 0:
                raise SceneryGroupError(
                    "No white triggerzones found in: " + zone_def_name
                )
            elif zone_def_category not in NAME_BY_CATEGORY:
                raise SceneryGroupError(
                    "Incorrect TriggerZone category definition for: "
                    + zone_def_name
                    + " in campaign definition.  TriggerZone category: "
                    + zone_def_category
                )

        return scenery_groups

    @staticmethod
    def group_task_for_scenery_group_category(category: str) -> Optional[GroupTask]:
        if category == "allycamp":
            return GroupTask.ALLY_CAMP
        elif category == "ammo":
            return GroupTask.AMMO
        elif category == "commandcenter":
            return GroupTask.COMMAND_CENTER
        elif category == "comms":
            return GroupTask.COMMS
        elif category == "derrick":
            return GroupTask.DERRICK
        elif category == "factory":
            return GroupTask.FACTORY
        elif category == "farp":
            return GroupTask.FARP
        elif category == "fob":
            return GroupTask.FOB
        elif category == "fuel":
            return GroupTask.FUEL
        elif category == "oil":
            return GroupTask.OIL
        elif category == "power":
            return GroupTask.POWER
        elif category == "village":
            return GroupTask.VILLAGE
        elif category == "ware":
            return GroupTask.WARE
        elif category == "ww2bunker":
            return GroupTask.WW2_BUNKER
        return None

    @staticmethod
    def is_blue(zone: TriggerZone) -> bool:
        # Blue in RGB is [0 Red], [0 Green], [1 Blue]. Ignore the fourth position: Transparency.
        return zone.color[1] == 0 and zone.color[2] == 0 and zone.color[3] == 1

    @staticmethod
    def is_white(zone: TriggerZone) -> bool:
        # White in RGB is [1 Red], [1 Green], [1 Blue]. Ignore the fourth position: Transparency.
        return zone.color[1] == 1 and zone.color[2] == 1 and zone.color[3] == 1
