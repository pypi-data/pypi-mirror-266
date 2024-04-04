from __future__ import annotations
import datetime
from typing import Dict, Any, List, Optional
from .base_ikea_model import BaseIkeaModel
from .device import Attributes
from ..hub.abstract_smart_home_hub import AbstractSmartHomeHub


class SceneAttributes(Attributes):
    scene_id: str
    name: str
    icon: str
    last_completed: Optional[str] = None
    last_triggered: Optional[str] = None
    last_undo: Optional[str] = None


class Info(BaseIkeaModel):
    name: str
    icon: str


class Trigger(BaseIkeaModel):
    id: str
    type: str
    triggered_at: datetime.datetime
    disabled: bool


class ActionAttributes(BaseIkeaModel, extra="allow"):
    pass


class Action(BaseIkeaModel):
    id: str
    type: str
    attributes: ActionAttributes


class Scene(BaseIkeaModel):
    dirigera_client: AbstractSmartHomeHub
    id: str
    type: str
    info: Info
    triggers: List[Trigger]
    actions: List[Action]
    created_at: datetime.datetime
    last_completed: Optional[datetime.datetime] = None
    last_triggered: Optional[datetime.datetime] = None
    last_undo: Optional[datetime.datetime] = None
    commands: List[str]
    undo_allowed_duration: int

    def reload(self) -> Scene:
        data = self.dirigera_client.get(route=f"/scenes/{self.id}")
        return Scene(dirigeraClient=self.dirigera_client, **data)

    def trigger(self) -> None:
        self.dirigera_client.post(route=f"/scenes/{self.id}/trigger")

    def undo(self) -> None:
        self.dirigera_client.post(route=f"/scenes/{self.id}/undo")


def dict_to_scene(data: Dict[str, Any], dirigera_client: AbstractSmartHomeHub) -> Scene:
    return Scene(dirigeraClient=dirigera_client, **data)
