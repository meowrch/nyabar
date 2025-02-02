from fabric.utils import exec_shell_command_async, get_relative_path, invoke_repeater
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.x11 import X11Window

from utils.config import widget_config
from utils.functions import convert_seconds_to_milliseconds
from utils.monitors import HyprlandWithMonitors
from widgets import (
    Battery,
    BlueToothWidget,
    BrightnessWidget,
    BspwmdWorkSpacesWidget,
    CavaWidget,
    ClickCounterWidget,
    CpuWidget,
    DashBoardWidget,
    DateTimeWidget,
    DividerWidget,
    HyprIdleWidget,
    HyprlandWorkSpacesWidget,
    HyprSunsetWidget,
    KeyboardLayoutWidget,
    LanguageWidget,
    MemoryWidget,
    MicrophoneIndicatorWidget,
    Mpris,
    PowerButton,
    Recorder,
    SpacingWidget,
    StopWatchWidget,
    StorageWidget,
    SystemTray,
    TaskBarWidget,
    ThemeSwitcherWidget,
    UpdatesWidget,
    VolumeWidget,
    WeatherWidget,
    WindowTitleWidget,
)


class StatusBar:
    """A widget to display the status bar panel."""

    widgets_list: dict

    def __init__(self, **kwargs):
        self.widgets_list = {
            "battery": Battery,
            "bluetooth": BlueToothWidget,
            "brightness": BrightnessWidget,
            "cava": CavaWidget,
            "click_counter": ClickCounterWidget,
            "cpu": CpuWidget,
            "date_time": DateTimeWidget,
            "hypr_idle": HyprIdleWidget,
            "hypr_sunset": HyprSunsetWidget,
            "keyboard": KeyboardLayoutWidget,
            "language": LanguageWidget,
            "dashboard": DashBoardWidget,
            "memory": MemoryWidget,
            "microphone": MicrophoneIndicatorWidget,
            "mpris": Mpris,
            "power": PowerButton,
            "recorder": Recorder,
            "storage": StorageWidget,
            "system_tray": SystemTray,
            "task_bar": TaskBarWidget,
            "theme_switcher": ThemeSwitcherWidget,
            "updates": UpdatesWidget,
            "volume": VolumeWidget,
            "weather": WeatherWidget,
            "window_title": WindowTitleWidget,
            "workspaces": HyprlandWorkSpacesWidget,
            "spacing": SpacingWidget,
            "stop_watch": StopWatchWidget,
            "divider": DividerWidget,
        }

        if widget_config["options"]["check_updates"]:
            invoke_repeater(
                convert_seconds_to_milliseconds(3600),
                self.check_for_bar_updates,
                initial_call=True,
            )

    def check_for_bar_updates(self):
        exec_shell_command_async(
            get_relative_path("../assets/scripts/barupdate.sh"),
            lambda _: None,
        )
        return True

    def make_layout(self):
        """assigns the three sections their respective widgets"""

        layout = {"left_section": [], "middle_section": [], "right_section": []}

        for key in layout:
            layout[key].extend(
                self.widgets_list[widget](widget_config, bar=self)
                for widget in widget_config["layout"][key]
            )

        return layout

    def make_box(self) -> CenterBox:
        layout = self.make_layout()
        return CenterBox(
            name="panel-inner",
            start_children=Box(
                spacing=4,
                orientation="h",
                children=layout["left_section"],
            ),
            center_children=Box(
                spacing=4,
                orientation="h",
                children=layout["middle_section"],
            ),
            end_children=Box(
                spacing=4,
                orientation="h",
                children=layout["right_section"],
            ),
        )


class X11StatusBar(X11Window, StatusBar):
    def __init__(self, **kwargs) -> None:
        StatusBar.__init__(self, **kwargs)

        if "workspaces" in self.widgets_list:
            self.widgets_list["workspaces"] = BspwmdWorkSpacesWidget

        box = self.make_box()

        X11Window.__init__(
            self,
            name="panel",
            geometry="top",
            layer=widget_config["options"]["layer"],
            visible=True,
            all_visible=False,
            child=box,
            **kwargs,
        )


class WaylandStatusBar(WaylandWindow, StatusBar):
    def __init__(self, **kwargs) -> None:
        StatusBar.__init__(self, **kwargs)

        box = self.make_box()
        acnhor = f"left {widget_config['options']['location']} right"

        WaylandWindow.__init__(
            self,
            name="panel",
            layer=widget_config["options"]["layer"],
            anchor=acnhor,
            pass_through=False,
            monitor=HyprlandWithMonitors().get_current_gdk_monitor_id(),
            exclusivity="auto",
            visible=True,
            all_visible=False,
            child=box,
            **kwargs,
        )
