from fabric.widgets.box import Box
from fabric.widgets.shapes import Corner
from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.x11 import X11Window


class MyCorner(Box):
    """A container for a corner shape."""

    def __init__(self, corner):
        super().__init__(
            name="corner-container",
            children=Corner(
                name="corner",
                orientation=corner,
                size=20,
            ),
        )


class ScreenCorners:
    """A window that displays all four corners."""

    def __init__(self):
        self.all_corners = Box(
            name="all-corners",
            orientation="v",
            h_expand=True,
            v_expand=True,
            h_align="fill",
            v_align="fill",
            children=[
                Box(
                    name="top-corners",
                    orientation="h",
                    h_align="fill",
                    children=[
                        MyCorner("top-left"),
                        Box(h_expand=True),
                        MyCorner("top-right"),
                    ],
                ),
                Box(v_expand=True),
                Box(
                    name="bottom-corners",
                    orientation="h",
                    h_align="fill",
                    children=[
                        MyCorner("bottom-left"),
                        Box(h_expand=True),
                        MyCorner("bottom-right"),
                    ],
                ),
            ],
        )


class X11ScreenCorners(X11Window, ScreenCorners):
    def __init__(self):
        X11Window.__init__(
            self,
            type_hint="dock",
            name="corners",
            geometry="top",
            visible=True,
            all_visible=False,
        )
        ScreenCorners.__init__(self)
        self.add(self.all_corners)
        self.show_all()


class WaylandScreenCorners(WaylandWindow, ScreenCorners):
    def __init__(self):
        WaylandWindow.__init__(
            self,
            name="corners",
            layer="top",
            anchor="top bottom left right",
            exclusivity="normal",
            pass_through=True,
            visible=False,
            all_visible=False,
        )
        ScreenCorners.__init__(self)
        self.add(self.all_corners)
        self.show_all()
