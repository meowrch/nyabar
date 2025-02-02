import argparse

import setproctitle
from fabric import Application
from fabric.utils import exec_shell_command, get_relative_path, monitor_file
from loguru import logger

import utils.functions as helpers
from modules.bar import WaylandStatusBar, X11StatusBar
from modules.notification_pop_up import HyprlandNotificationPopup, X11NotificationPopup
from modules.osd import WaylandOSDContainer, X11OSDContainer
from utils.colors import Colors
from utils.config import widget_config
from utils.constants import APP_CACHE_DIRECTORY, APPLICATION_NAME
from utils.enums import WMEnum
from widgets.corners import WaylandScreenCorners, X11ScreenCorners


def process_and_apply_css(app: Application):
    if not helpers.executable_exists("sass"):
        raise helpers.ExecutableNotFoundError(
            "sass"
        )  # Raise an error if sass is not found and exit the application

    logger.info(f"{Colors.INFO}[Main] Compiling CSS")
    exec_shell_command("sass styles/main.scss dist/main.css --no-source-map")
    logger.info(f"{Colors.INFO}[Main] CSS applied")
    app.set_stylesheet_from_file(get_relative_path("dist/main.css"))


for log in [
    "fabric.hyprland.widgets",
    "fabric.audio.service",
    "fabric.bluetooth.service",
]:
    logger.disable(log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Пример парсинга аргументов командной строки."
    )

    parser.add_argument(
        "--wm",
        type=str,
        choices=[wm.value for wm in WMEnum],
        required=True,
        help="Выберите оконный менеджер: hyprland или bspwm",
    )

    args = parser.parse_args()

    try:
        wm = WMEnum(args.wm)
    except ValueError as e:
        raise ValueError(f"Недопустимое значение для --wm: {args.wm}") from e

    # Create the status bar and notifications
    if wm in [WMEnum.HYPRLAND]:
        bar = WaylandStatusBar()
        notifications = HyprlandNotificationPopup(widget_config)
    elif wm in [WMEnum.BSPWM]:
        bar = X11StatusBar()
        notifications = X11NotificationPopup(widget_config)
    else:
        raise ValueError(f"Недопустимое значение для --wm: {args.wm}")

    windows = [notifications, bar]

    if widget_config["options"]["screen_corners"]:
        if wm in [WMEnum.HYPRLAND]:
            windows.append(WaylandScreenCorners())
        elif wm in [WMEnum.BSPWM]:
            windows.append(X11ScreenCorners())
        else:
            raise ValueError(f"Недопустимое значение для --wm: {args.wm}")

    if widget_config["osd"]["enabled"]:
        if wm in [WMEnum.HYPRLAND]:
            windows.append(WaylandOSDContainer(widget_config))
        elif wm in [WMEnum.BSPWM]:
            windows.append(X11OSDContainer(widget_config))
        else:
            raise ValueError(f"Недопустимое значение для --wm: {args.wm}")

    # Initialize the application with the status bar
    app = Application(APPLICATION_NAME, windows=windows)

    setproctitle.setproctitle(APPLICATION_NAME)

    helpers.ensure_dir_exists(APP_CACHE_DIRECTORY)

    helpers.copy_theme(widget_config["theme"]["name"])

    # Monitor styles folder for changes
    main_css_file = monitor_file(get_relative_path("styles"))
    main_css_file.connect("changed", lambda *_: process_and_apply_css(app))

    process_and_apply_css(app)

    # Run the application
    app.run()
