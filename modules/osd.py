import time
from typing import ClassVar, Literal

from fabric.utils import invoke_repeater
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.x11 import X11Window
from gi.repository import GObject

import utils.functions as helpers
import utils.icons as icons
from services import audio_service
from services.brightness import Brightness
from utils.widget_settings import BarConfig
from utils.widget_utils import (
    create_scale,
    get_audio_icon_name,
    get_brightness_icon_name,
)


class GenericOSDContainer(Box):
    """A generic OSD container to display the OSD for brightness and audio."""

    def __init__(self, config, **kwargs):
        super().__init__(
            orientation="h",
            spacing=10,
            name="osd-container",
            **kwargs,
        )
        self.level = Label(
            name="osd-level", h_align="center", h_expand=True, visible=False
        )
        self.icon = Image(icon_name=icons.icons["brightness"]["screen"], icon_size=28)
        self.scale = create_scale()

        self.children = (self.icon, self.scale, self.level)

        if config["show_percentage"]:
            self.level.set_visible(True)


class BrightnessOSDContainer(GenericOSDContainer):
    """A widget to display the OSD for brightness."""

    def __init__(self, config, **kwargs):
        super().__init__(
            config=config,
            **kwargs,
        )
        self.brightness_service = Brightness().get_initial()
        self.update_brightness()

        self.scale.connect("value-changed", lambda *_: self.update_brightness())
        self.brightness_service.connect("screen", self.on_brightness_changed)

    def update_brightness(self):
        normalized_brightness = helpers.convert_to_percent(
            self.brightness_service.screen_brightness,
            self.brightness_service.max_screen,
        )
        self.scale.animate_value(normalized_brightness)
        self.update_icon(int(normalized_brightness))

    def update_icon(self, current_brightness):
        icon_name = get_brightness_icon_name(current_brightness)["icon"]
        self.level.set_label(f"{current_brightness}%")
        self.icon.set_from_icon_name(icon_name)

    def on_brightness_changed(self, sender, value, *args):
        normalized_brightness = (value / self.brightness_service.max_screen) * 101
        self.scale.animate_value(normalized_brightness)


class AudioOSDContainer(GenericOSDContainer):
    """A widget to display the OSD for audio."""

    __gsignals__: ClassVar[dict] = {
        "volume-changed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, config, **kwargs):
        super().__init__(
            config=config,
            **kwargs,
        )
        self.audio = audio_service

        self.sync_with_audio()

        self.scale.connect("value-changed", self.on_volume_changed)
        self.audio.connect("notify::speaker", self.on_audio_speaker_changed)

    def sync_with_audio(self):
        if self.audio.speaker:
            volume = round(self.audio.speaker.volume)
            self.scale.set_value(volume)
            self.update_icon(volume)

    def on_volume_changed(self, *_):
        if self.audio.speaker:
            volume = int(self.scale.value)
            if 0 <= volume <= 100:
                self.audio.speaker.set_volume(volume)
                self.update_icon(volume)
                self.emit("volume-changed")

    def on_audio_speaker_changed(self, *_):
        if self.audio.speaker:
            self.audio.speaker.connect("notify::volume", self.update_volume)
            self.update_volume()

    def update_volume(self, *_):
        if self.audio.speaker and not self.is_hovered():
            volume = round(self.audio.speaker.volume)
            self.scale.set_value(volume)
            self.update_icon(volume)

    def update_icon(self, volume):
        icon_name = get_audio_icon_name(volume, self.audio.speaker.muted)["icon"]
        self.level.set_label(f"{volume}%")
        self.icon.set_from_icon_name(icon_name)


class OSDContainer:
    """A widget to display the OSD for audio and brightness."""

    def __init__(
        self,
        widget_config: BarConfig,
        transition_duration=200,
        **kwargs,
    ):
        self.config = widget_config["osd"]

        self.audio_container = AudioOSDContainer(config=self.config)
        self.brightness_container = BrightnessOSDContainer(config=self.config)

        self.timeout = self.config["timeout"]

        self.revealer = Revealer(
            name="osd-revealer",
            transition_type="slide-right",
            transition_duration=transition_duration,
            child_revealed=False,
        )

        self.last_activity_time = time.time()

        self.audio_container.audio.connect("notify::speaker", self.show_audio)
        self.brightness_container.brightness_service.connect(
            "screen",
            self.show_brightness,
        )
        self.audio_container.connect("volume-changed", self.show_audio)

        invoke_repeater(100, self.check_inactivity, initial_call=True)

    def show_audio(self, *_):
        self.show_box(box_to_show="audio")
        self.reset_inactivity_timer()

    def show_brightness(self, *_):
        self.show_box(box_to_show="brightness")
        self.reset_inactivity_timer()

    def show_box(self, box_to_show: Literal["audio", "brightness"]):
        self.set_visible(True)
        if box_to_show == "audio":
            self.revealer.children = self.audio_container
        elif box_to_show == "brightness":
            self.revealer.children = self.brightness_container
        self.revealer.set_reveal_child(True)
        self.reset_inactivity_timer()

    def start_hide_timer(self):
        self.set_visible(False)

    def reset_inactivity_timer(self):
        self.last_activity_time = time.time()

    def check_inactivity(self):
        if time.time() - self.last_activity_time >= (self.timeout / 1000):
            self.start_hide_timer()
        return True


class X11OSDContainer(X11Window, OSDContainer):
    def __init__(
        self,
        widget_config: BarConfig,
        transition_duration=200,
        **kwargs,
    ):
        OSDContainer.__init__(
            self,
            widget_config=widget_config,
            transition_duration=transition_duration,
        )
        X11Window.__init__(
            self,
            type_hint="dock",
            geometry="bottom",
            layer=widget_config["options"]["layer"],
            visible=True,
            all_visible=False,
            child=self.revealer,
            **kwargs,
        )


class WaylandOSDContainer(WaylandWindow, OSDContainer):
    def __init__(
        self,
        widget_config: BarConfig,
        transition_duration=200,
        keyboard_mode: Literal["none", "exclusive", "on-demand"] = "on-demand",
        **kwargs,
    ):
        OSDContainer.__init__(
            self,
            widget_config=widget_config,
            transition_duration=transition_duration,
        )
        WaylandWindow.__init__(
            self,
            layer="overlay",
            anchor=self.config["anchor"],
            child=self.revealer,
            visible=False,
            pass_through=True,
            keyboard_mode=keyboard_mode,
            **kwargs,
        )
