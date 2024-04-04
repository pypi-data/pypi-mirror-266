from .geo import AitoffAxes, HammerAxes, LambertAxes, MollweideAxes
from .polar import PolarAxes
from ..axes import Axes

class ProjectionRegistry:
    def __init__(self) -> None: ...
    def register(self, *projections: type[Axes]) -> None: ...
    def get_projection_class(self, name: str) -> type[Axes]: ...
    def get_projection_names(self) -> list[str]: ...

projection_registry: ProjectionRegistry

def register_projection(cls: type[Axes]) -> None: ...
def get_projection_class(projection: str | None = ...) -> type[Axes]: ...
def get_projection_names() -> list[str]: ...
