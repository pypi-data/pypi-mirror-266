import matplotlib.artist as martist

import datetime
from collections.abc import Callable, Iterable, Iterator, Sequence
from matplotlib import cbook
from matplotlib.artist import Artist
from matplotlib.axis import XAxis, YAxis, Tick
from matplotlib.backend_bases import RendererBase, MouseButton, MouseEvent
from matplotlib.cbook import CallbackRegistry
from matplotlib.container import Container
from matplotlib.collections import Collection
from matplotlib.cm import ScalarMappable
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.gridspec import SubplotSpec, GridSpec
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.patches import Patch
from matplotlib.scale import ScaleBase
from matplotlib.spines import Spines
from matplotlib.table import Table
from matplotlib.text import Text
from matplotlib.transforms import Transform, Bbox

from cycler import Cycler

import numpy as np
from numpy.typing import ArrayLike
from typing import Any, Literal, TypeVar, overload
from matplotlib.typing import ColorType

_T = TypeVar("_T", bound=Artist)

class _axis_method_wrapper:
    attr_name: str
    method_name: str
    __doc__: str
    def __init__(
        self, attr_name: str, method_name: str, *, doc_sub: dict[str, str] | None = ...
    ) -> None: ...
    def __set_name__(self, owner: Any, name: str) -> None: ...

class _AxesBase(martist.Artist):
    name: str
    patch: Patch
    spines: Spines
    fmt_xdata: Callable[[float], str] | None
    fmt_ydata: Callable[[float], str] | None
    xaxis: XAxis
    yaxis: YAxis
    bbox: Bbox
    dataLim: Bbox
    transAxes: Transform
    transScale: Transform
    transLimits: Transform
    transData: Transform
    ignore_existing_data_limits: bool
    axison: bool
    containers: list[Container]
    callbacks: CallbackRegistry
    child_axes: list[_AxesBase]
    legend_: Legend | None
    title: Text
    _projection_init: Any

    def __init__(
        self,
        fig: Figure,
        *args: tuple[float, float, float, float] | Bbox | int,
        facecolor: ColorType | None = ...,
        frameon: bool = ...,
        sharex: _AxesBase | None = ...,
        sharey: _AxesBase | None = ...,
        label: Any = ...,
        xscale: str | ScaleBase | None = ...,
        yscale: str | ScaleBase | None = ...,
        box_aspect: float | None = ...,
        **kwargs
    ) -> None: ...
    def get_subplotspec(self) -> SubplotSpec | None: ...
    def set_subplotspec(self, subplotspec: SubplotSpec) -> None: ...
    def get_gridspec(self) -> GridSpec | None: ...
    def set_figure(self, fig: Figure) -> None: ...
    @property
    def viewLim(self) -> Bbox: ...
    def get_xaxis_transform(
        self, which: Literal["grid", "tick1", "tick2"] = ...
    ) -> Transform: ...
    def get_xaxis_text1_transform(
        self, pad_points: float
    ) -> tuple[
        Transform,
        Literal["center", "top", "bottom", "baseline", "center_baseline"],
        Literal["center", "left", "right"],
    ]: ...
    def get_xaxis_text2_transform(
        self, pad_points
    ) -> tuple[
        Transform,
        Literal["center", "top", "bottom", "baseline", "center_baseline"],
        Literal["center", "left", "right"],
    ]: ...
    def get_yaxis_transform(
        self, which: Literal["grid", "tick1", "tick2"] = ...
    ) -> Transform: ...
    def get_yaxis_text1_transform(
        self, pad_points
    ) -> tuple[
        Transform,
        Literal["center", "top", "bottom", "baseline", "center_baseline"],
        Literal["center", "left", "right"],
    ]: ...
    def get_yaxis_text2_transform(
        self, pad_points
    ) -> tuple[
        Transform,
        Literal["center", "top", "bottom", "baseline", "center_baseline"],
        Literal["center", "left", "right"],
    ]: ...
    def get_position(self, original: bool = ...) -> Bbox: ...
    def set_position(
        self,
        pos: Bbox | tuple[float, float, float, float],
        which: Literal["both", "active", "original"] = ...,
    ) -> None: ...
    def reset_position(self) -> None: ...
    def set_axes_locator(
        self, locator: Callable[[_AxesBase, RendererBase], Bbox]
    ) -> None: ...
    def get_axes_locator(self) -> Callable[[_AxesBase, RendererBase], Bbox]: ...
    def sharex(self, other: _AxesBase) -> None: ...
    def sharey(self, other: _AxesBase) -> None: ...
    def clear(self) -> None: ...
    def cla(self) -> None: ...

    class ArtistList(Sequence[_T]):
        def __init__(
            self,
            axes: _AxesBase,
            prop_name: str,
            valid_types: type | Iterable[type] | None = ...,
            invalid_types: type | Iterable[type] | None = ...,
        ) -> None: ...
        def __len__(self) -> int: ...
        def __iter__(self) -> Iterator[_T]: ...
        @overload
        def __getitem__(self, key: int) -> _T: ...
        @overload
        def __getitem__(self, key: slice) -> list[_T]: ...

        @overload
        def __add__(self, other: _AxesBase.ArtistList[_T]) -> list[_T]: ...
        @overload
        def __add__(self, other: list[Any]) -> list[Any]: ...
        @overload
        def __add__(self, other: tuple[Any]) -> tuple[Any]: ...

        @overload
        def __radd__(self, other: _AxesBase.ArtistList[_T]) -> list[_T]: ...
        @overload
        def __radd__(self, other: list[Any]) -> list[Any]: ...
        @overload
        def __radd__(self, other: tuple[Any]) -> tuple[Any]: ...

    @property
    def artists(self) -> _AxesBase.ArtistList[Artist]: ...
    @property
    def collections(self) -> _AxesBase.ArtistList[Collection]: ...
    @property
    def images(self) -> _AxesBase.ArtistList[AxesImage]: ...
    @property
    def lines(self) -> _AxesBase.ArtistList[Line2D]: ...
    @property
    def patches(self) -> _AxesBase.ArtistList[Patch]: ...
    @property
    def tables(self) -> _AxesBase.ArtistList[Table]: ...
    @property
    def texts(self) -> _AxesBase.ArtistList[Text]: ...
    def get_facecolor(self) -> ColorType: ...
    def set_facecolor(self, color: ColorType | None) -> None: ...
    @overload
    def set_prop_cycle(self, cycler: Cycler) -> None: ...
    @overload
    def set_prop_cycle(self, label: str, values: Iterable[Any]) -> None: ...
    @overload
    def set_prop_cycle(self, **kwargs: Iterable[Any]) -> None: ...
    def get_aspect(self) -> float | Literal["auto"]: ...
    def set_aspect(
        self,
        aspect: float | Literal["auto", "equal"],
        adjustable: Literal["box", "datalim"] | None = ...,
        anchor: str | tuple[float, float] | None = ...,
        share: bool = ...,
    ) -> None: ...
    def get_adjustable(self) -> Literal["box", "datalim"]: ...
    def set_adjustable(
        self, adjustable: Literal["box", "datalim"], share: bool = ...
    ) -> None: ...
    def get_box_aspect(self) -> float | None: ...
    def set_box_aspect(self, aspect: float | None = ...) -> None: ...
    def get_anchor(self) -> str | tuple[float, float]: ...
    def set_anchor(
        self, anchor: str | tuple[float, float], share: bool = ...
    ) -> None: ...
    def get_data_ratio(self) -> float: ...
    def apply_aspect(self, position: Bbox | None = ...) -> None: ...
    @overload
    def axis(
        self,
        arg: tuple[float, float, float, float] | bool | str | None = ...,
        /,
        *,
        emit: bool = ...
    ) -> tuple[float, float, float, float]: ...
    @overload
    def axis(
        self,
        *,
        emit: bool = ...,
        xmin: float | None = ...,
        xmax: float | None = ...,
        ymin: float | None = ...,
        ymax: float | None = ...
    ) -> tuple[float, float, float, float]: ...
    def get_legend(self) -> Legend: ...
    def get_images(self) -> list[AxesImage]: ...
    def get_lines(self) -> list[Line2D]: ...
    def get_xaxis(self) -> XAxis: ...
    def get_yaxis(self) -> YAxis: ...
    def has_data(self) -> bool: ...
    def add_artist(self, a: Artist) -> Artist: ...
    def add_child_axes(self, ax: _AxesBase) -> _AxesBase: ...
    def add_collection(
        self, collection: Collection, autolim: bool = ...
    ) -> Collection: ...
    def add_image(self, image: AxesImage) -> AxesImage: ...
    def add_line(self, line: Line2D) -> Line2D: ...
    def add_patch(self, p: Patch) -> Patch: ...
    def add_table(self, tab: Table) -> Table: ...
    def add_container(self, container: Container) -> Container: ...
    def relim(self, visible_only: bool = ...) -> None: ...
    def update_datalim(
        self, xys: ArrayLike, updatex: bool = ..., updatey: bool = ...
    ) -> None: ...
    def in_axes(self, mouseevent: MouseEvent) -> bool: ...
    def get_autoscale_on(self) -> bool: ...
    def set_autoscale_on(self, b: bool) -> None: ...
    @property
    def use_sticky_edges(self) -> bool: ...
    @use_sticky_edges.setter
    def use_sticky_edges(self, b: bool) -> None: ...
    def set_xmargin(self, m: float) -> None: ...
    def set_ymargin(self, m: float) -> None: ...

    # Probably could be made better with overloads
    def margins(
        self,
        *margins: float,
        x: float | None = ...,
        y: float | None = ...,
        tight: bool | None = ...
    ) -> tuple[float, float] | None: ...
    def set_rasterization_zorder(self, z: float | None) -> None: ...
    def get_rasterization_zorder(self) -> float | None: ...
    def autoscale(
        self,
        enable: bool = ...,
        axis: Literal["both", "x", "y"] = ...,
        tight: bool | None = ...,
    ) -> None: ...
    def autoscale_view(
        self, tight: bool | None = ..., scalex: bool = ..., scaley: bool = ...
    ) -> None: ...
    def draw_artist(self, a: Artist) -> None: ...
    def redraw_in_frame(self) -> None: ...
    def get_frame_on(self) -> bool: ...
    def set_frame_on(self, b: bool) -> None: ...
    def get_axisbelow(self) -> bool | Literal["line"]: ...
    def set_axisbelow(self, b: bool | Literal["line"]) -> None: ...
    def grid(
        self,
        visible: bool | None = ...,
        which: Literal["major", "minor", "both"] = ...,
        axis: Literal["both", "x", "y"] = ...,
        **kwargs
    ) -> None: ...
    def ticklabel_format(
        self,
        *,
        axis: Literal["both", "x", "y"] = ...,
        style: Literal["", "sci", "scientific", "plain"] = ...,
        scilimits: tuple[int, int] | None = ...,
        useOffset: bool | float | None = ...,
        useLocale: bool | None = ...,
        useMathText: bool | None = ...
    ) -> None: ...
    def locator_params(
        self, axis: Literal["both", "x", "y"] = ..., tight: bool | None = ..., **kwargs
    ) -> None: ...
    def tick_params(self, axis: Literal["both", "x", "y"] = ..., **kwargs) -> None: ...
    def set_axis_off(self) -> None: ...
    def set_axis_on(self) -> None: ...
    def get_xlabel(self) -> str: ...
    def set_xlabel(
        self,
        xlabel: str,
        fontdict: dict[str, Any] | None = ...,
        labelpad: float | None = ...,
        *,
        loc: Literal["left", "center", "right"] | None = ...,
        **kwargs
    ) -> Text: ...
    def invert_xaxis(self) -> None: ...
    def get_xbound(self) -> tuple[float, float]: ...
    def set_xbound(
        self, lower: float | None = ..., upper: float | None = ...
    ) -> None: ...
    def get_xlim(self) -> tuple[float, float]: ...
    def set_xlim(
        self,
        left: float | tuple[float, float] | None = ...,
        right: float | None = ...,
        *,
        emit: bool = ...,
        auto: bool | None = ...,
        xmin: float | None = ...,
        xmax: float | None = ...
    ) -> tuple[float, float]: ...
    def get_ylabel(self) -> str: ...
    def set_ylabel(
        self,
        ylabel: str,
        fontdict: dict[str, Any] | None = ...,
        labelpad: float | None = ...,
        *,
        loc: Literal["bottom", "center", "top"] | None = ...,
        **kwargs
    ) -> Text: ...
    def invert_yaxis(self) -> None: ...
    def get_ybound(self) -> tuple[float, float]: ...
    def set_ybound(
        self, lower: float | None = ..., upper: float | None = ...
    ) -> None: ...
    def get_ylim(self) -> tuple[float, float]: ...
    def set_ylim(
        self,
        bottom: float | tuple[float, float] | None = ...,
        top: float | None = ...,
        *,
        emit: bool = ...,
        auto: bool | None = ...,
        ymin: float | None = ...,
        ymax: float | None = ...
    ) -> tuple[float, float]: ...
    def format_xdata(self, x: float) -> str: ...
    def format_ydata(self, y: float) -> str: ...
    def format_coord(self, x: float, y: float) -> str: ...
    def minorticks_on(self) -> None: ...
    def minorticks_off(self) -> None: ...
    def can_zoom(self) -> bool: ...
    def can_pan(self) -> bool: ...
    def get_navigate(self) -> bool: ...
    def set_navigate(self, b: bool) -> None: ...
    def get_navigate_mode(self) -> Literal["PAN", "ZOOM"] | None: ...
    def set_navigate_mode(self, b: Literal["PAN", "ZOOM"] | None) -> None: ...
    def start_pan(self, x: float, y: float, button: MouseButton) -> None: ...
    def end_pan(self) -> None: ...
    def drag_pan(
        self, button: MouseButton, key: str | None, x: float, y: float
    ) -> None: ...
    def get_children(self) -> list[Artist]: ...
    def contains_point(self, point: tuple[int, int]) -> bool: ...
    def get_default_bbox_extra_artists(self) -> list[Artist]: ...
    def get_tightbbox(
        self,
        renderer: RendererBase | None = ...,
        *,
        call_axes_locator: bool = ...,
        bbox_extra_artists: Sequence[Artist] | None = ...,
        for_layout_only: bool = ...
    ) -> Bbox | None: ...
    def twinx(self) -> _AxesBase: ...
    def twiny(self) -> _AxesBase: ...
    def get_shared_x_axes(self) -> cbook.GrouperView: ...
    def get_shared_y_axes(self) -> cbook.GrouperView: ...
    def label_outer(self, remove_inner_ticks: bool = ...) -> None: ...

    # The methods underneath this line are added via the `_axis_method_wrapper` class
    # Initially they are set to an object, but that object uses `__set_name__` to override
    # itself with a method modified from the Axis methods for the x or y Axis.
    # As such, they are typed according to the resultant method rather than as that object.

    def get_xgridlines(self) -> list[Line2D]: ...
    def get_xticklines(self, minor: bool = ...) -> list[Line2D]: ...
    def get_ygridlines(self) -> list[Line2D]: ...
    def get_yticklines(self, minor: bool = ...) -> list[Line2D]: ...
    def _sci(self, im: ScalarMappable) -> None: ...
    def get_autoscalex_on(self) -> bool: ...
    def get_autoscaley_on(self) -> bool: ...
    def set_autoscalex_on(self, b: bool) -> None: ...
    def set_autoscaley_on(self, b: bool) -> None: ...
    def xaxis_inverted(self) -> bool: ...
    def get_xscale(self) -> str: ...
    def set_xscale(self, value: str | ScaleBase, **kwargs) -> None: ...
    def get_xticks(self, *, minor: bool = ...) -> np.ndarray: ...
    def set_xticks(
        self,
        ticks: ArrayLike,
        labels: Iterable[str] | None = ...,
        *,
        minor: bool = ...,
        **kwargs
    ) -> list[Tick]: ...
    def get_xmajorticklabels(self) -> list[Text]: ...
    def get_xminorticklabels(self) -> list[Text]: ...
    def get_xticklabels(
        self, minor: bool = ..., which: Literal["major", "minor", "both"] | None = ...
    ) -> list[Text]: ...
    def set_xticklabels(
        self,
        labels: Iterable[str | Text],
        *,
        minor: bool = ...,
        fontdict: dict[str, Any] | None = ...,
        **kwargs
    ) -> list[Text]: ...
    def yaxis_inverted(self) -> bool: ...
    def get_yscale(self) -> str: ...
    def set_yscale(self, value: str | ScaleBase, **kwargs) -> None: ...
    def get_yticks(self, *, minor: bool = ...) -> np.ndarray: ...
    def set_yticks(
        self,
        ticks: ArrayLike,
        labels: Iterable[str] | None = ...,
        *,
        minor: bool = ...,
        **kwargs
    ) -> list[Tick]: ...
    def get_ymajorticklabels(self) -> list[Text]: ...
    def get_yminorticklabels(self) -> list[Text]: ...
    def get_yticklabels(
        self, minor: bool = ..., which: Literal["major", "minor", "both"] | None = ...
    ) -> list[Text]: ...
    def set_yticklabels(
        self,
        labels: Iterable[str | Text],
        *,
        minor: bool = ...,
        fontdict: dict[str, Any] | None = ...,
        **kwargs
    ) -> list[Text]: ...
    def xaxis_date(self, tz: str | datetime.tzinfo | None = ...) -> None: ...
    def yaxis_date(self, tz: str | datetime.tzinfo | None = ...) -> None: ...
