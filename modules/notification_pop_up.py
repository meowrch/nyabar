from fabric.notifications import (
    Notification,
    NotificationAction,
    NotificationCloseReason,
)
from fabric.utils import bulk_connect
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.wayland import WaylandWindow
from fabric.widgets.x11 import X11Window
from gi.repository import Gdk, GdkPixbuf, GLib

import utils.constants as constants
import utils.functions as helpers
import utils.icons as icons
from services import cache_notification_service, notification_service
from shared import CustomImage
from utils.config import widget_config
from utils.monitors import HyprlandWithMonitors
from utils.widget_settings import BarConfig
from utils.widget_utils import get_icon


class NotificationPopup:
    """A widget to grab and display notifications."""

    def __init__(self, widget_config: BarConfig, **kwargs):
        self._server = notification_service

        self.config = widget_config["notification"]

        self.ignored_apps = helpers.unique_list(self.config["ignored"])

        self.notifications = Box(
            v_expand=True,
            h_expand=True,
            style="margin: 1px 0px 1px 1px;",
            orientation="v",
            spacing=5,
        )
        self._server.connect("notification-added", self.on_new_notification)

    def on_new_notification(self, fabric_notif, id):
        notification: Notification = fabric_notif.get_notification_from_id(id)

        # Check if the notification is in the "do not disturb" mode, hacky way
        if (
            cache_notification_service.dont_disturb
            or notification.app_name in self.ignored_apps
        ):
            return

        new_box = NotificationRevealer(notification)
        self.notifications.add(new_box)
        new_box.set_reveal_child(True)
        cache_notification_service.cache_notification(notification)


class X11NotificationPopup(X11Window, NotificationPopup):
    """An X11 version of the notification popup."""

    def __init__(self, widget_config: BarConfig, **kwargs):
        NotificationPopup.__init__(self, widget_config, **kwargs)
        X11Window.__init__(
            self,
            name="panel",
            geometry="top",
            layer="top",
            visible=True,
            all_visible=False,
            child=self.notifications,
            **kwargs,
        )

class HyprlandNotificationPopup(WaylandWindow, NotificationPopup):
    """A Wayland version of the notification popup."""

    def __init__(self, widget_config: BarConfig, **kwargs):
        NotificationPopup.__init__(self, widget_config, **kwargs)
        super().__init__(
            anchor=self.config["anchor"],
            layer="overlay",
            all_visible=True,
            monitor=HyprlandWithMonitors().get_current_gdk_monitor_id(),
            visible=True,
            exclusive=False,
            child=self.notifications,
            **kwargs,
        )


class NotificationWidget(EventBox):
    """A widget to display a notification."""

    def __init__(
        self,
        notification: Notification,
        **kwargs,
    ):
        super().__init__(
            size=(constants.NOTIFICATION_WIDTH, -1),
            name="notification-eventbox",
            **kwargs,
        )

        self._notification = notification

        self._timeout_id = None

        self.notification_box = Box(
            spacing=8,
            name="notification",
            orientation="v",
        )

        if notification.urgency == 2:
            self.notification_box.add_style_class("critical")

        bulk_connect(
            self,
            {
                "button-press-event": self.on_button_press,
                "enter-notify-event": lambda *_: self.on_hover(),
                "leave-notify-event": lambda *_: self.on_unhover(),
            },
        )

        header_container = Box(
            spacing=8, orientation="h", style_classes="notification-header"
        )

        header_container.children = (
            get_icon(notification.app_icon),
            Label(
                markup=helpers.parse_markup(
                    str(
                        self._notification.summary
                        if self._notification.summary
                        else notification.app_name,
                    )
                ),
                h_align="start",
                style_classes="summary",
                line_wrap="word-char",
                ellipsization="end",
                v_align="start",
                h_expand=True,
            ),
        )

        header_container.pack_end(
            Box(
                v_align="start",
                children=(
                    Button(
                        image=Image(
                            icon_name=helpers.check_icon_exists(
                                "close-symbolic",
                                icons.icons["ui"]["close"],
                            ),
                            icon_size=16,
                        ),
                        style_classes="close-button",
                        on_clicked=lambda *_: self._notification.close(
                            "dismissed-by-user"
                        ),
                    ),
                ),
            ),
            False,
            False,
            0,
        )

        body_container = Box(
            spacing=4, orientation="h", style_classes="notification-body"
        )

        # Use provided image if available, otherwise use "notification-symbolic" icon
        if image_pixbuf := self._notification.image_pixbuf:
            body_container.add(
                CustomImage(
                    pixbuf=image_pixbuf.scale_simple(
                        constants.NOTIFICATION_IMAGE_SIZE,
                        constants.NOTIFICATION_IMAGE_SIZE,
                        GdkPixbuf.InterpType.BILINEAR,
                    ),
                    style_classes="image",
                ),
            )

        body_container.add(
            Label(
                markup=helpers.parse_markup(self._notification.body),
                line_wrap="word-char",
                ellipsization="end",
                v_align="start",
                h_expand=True,
                h_align="start",
                style_classes="body",
            ),
        )

        actions_container = Box(
            spacing=4,
            orientation="h",
            name="notification-action-box",
            children=[
                ActionButton(action, i, len(self._notification.actions))
                for i, action in enumerate(self._notification.actions)
            ],
            h_expand=True,
        )

        # Add the header, body, and actions to the notification box
        self.notification_box.children = (
            header_container,
            body_container,
            actions_container,
        )

        # Add the notification box to the EventBox
        self.add(self.notification_box)

        # Destroy this widget once the notification is closed
        self._notification.connect(
            "closed",
            lambda *_: (
                parent.remove(self) if (parent := self.get_parent()) else None,  # type: ignore
                self.destroy(),
            ),
        )

        if widget_config["notification"]["auto_dismiss"]:
            self.start_timeout()

    def start_timeout(self):
        self.stop_timeout()
        self._timeout_id = GLib.timeout_add(self.get_timeout(), self.close_notification)

    def stop_timeout(self):
        if self._timeout_id is not None:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = None

    def close_notification(self):
        self._notification.close("expired")
        self.stop_timeout()
        return False

    def on_button_press(self, _, event):
        if event.button != 1:
            self._notification.close("dismissed-by-user")

    def get_timeout(self):
        return (
            self._notification.timeout
            if self._notification.timeout != -1
            else widget_config["notification"]["timeout"]
        )

    def pause_timeout(self):
        self.stop_timeout()

    def resume_timeout(self):
        self.start_timeout()

    def on_hover(self):
        self.pause_timeout()
        self.set_pointer_cursor(self, "hand2")

    def on_unhover(self):
        self.resume_timeout()
        self.set_pointer_cursor(self, "arrow")

    @staticmethod
    def set_pointer_cursor(widget, cursor_name):
        window = widget.get_window()
        if window:
            cursor = Gdk.Cursor.new_from_name(widget.get_display(), cursor_name)
            window.set_cursor(cursor)


class NotificationRevealer(Revealer):
    """A widget to reveal a notification."""

    def __init__(self, notification: Notification, **kwargs):
        self.notif_box = NotificationWidget(notification)
        self._notification = notification

        super().__init__(
            child=Box(
                style="margin: 12px;",
                children=[self.notif_box],
            ),
            transition_duration=500,
            transition_type="crossfade",
            **kwargs,
        )

        self.connect(
            "notify::child-revealed",
            lambda *_: self.destroy() if not self.get_child_revealed() else None,
        )

        self._notification.connect("closed", self.on_resolved)

    def on_resolved(
        self,
        notification: Notification,
        reason: NotificationCloseReason,
    ):
        self.set_reveal_child(False)


class ActionButton(Button):
    """A button widget to represent a notification action."""

    def __init__(
        self,
        action: NotificationAction,
        action_number: int,
        total_actions: int,
        **kwargs,
    ):
        super().__init__(
            label=action.label,
            h_expand=True,
            on_clicked=self.on_clicked,
            style_classes="notification-action",
            **kwargs,
        )

        self.action = action

        if action_number == 0:
            self.add_style_class("start-action")
        elif action_number == total_actions - 1:
            self.add_style_class("end-action")
        else:
            self.add_style_class("middle-action")

    def on_clicked(self, *_):
        self.action.invoke()
        self.action.parent.close("dismissed-by-user")
