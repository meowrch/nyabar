import json
import subprocess
import threading

from fabric.widgets.button import Button
from gi.repository import GLib

from shared.widget_container import BoxWidget
from utils.functions import unique_list
from utils.widget_settings import BarConfig


def execute(command, shell=True):
    """Выполняет команду в shell и возвращает результат."""
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    return result.stdout.strip()


class BspwmWorkspaceButton(Button):
    def __init__(self, desktop_id, icon_map, **kwargs):
        super().__init__(label=icon_map.get(str(desktop_id), desktop_id), **kwargs)
        self.desktop_id = desktop_id
        self.icon_map = icon_map

    def update_label(self):
        self.label = f"{self.icon_map.get(str(self.desktop_id), self.desktop_id)}"


class BspwmdWorkSpacesWidget(BoxWidget):
    def __init__(self, widget_config: BarConfig, **kwargs):
        super().__init__(name="workspaces", **kwargs)
        self.config = widget_config["workspaces"]
        self.ignored_ws = unique_list(self.config["ignored"])
        self.buttons = []
        self.monitor = ""

        # Инициализация кнопок
        self.init_workspaces()

        # Запуск потока для отслеживания изменений
        self.update_thread = threading.Thread(target=self.listen_bspwm, daemon=True)
        self.update_thread.start()

    def init_workspaces(self):
        # Получаем информацию о рабочих столах
        desktops = execute("bspc query -D --names", shell=True).split("\n")

        # Создаем кнопки
        for desktop in desktops:
            if desktop in self.ignored_ws:
                continue
            button = BspwmWorkspaceButton(
                desktop_id=desktop,
                icon_map=self.config["icon_map"],
                name=f"workspace-{desktop}",
                visible=True,
            )
            button.connect("button-press-event", self.on_workspace_click)
            self.buttons.append(button)
            self.add(button)

        self.update_state()

    def update_state(self):
        # Получаем текущее состояние
        status = json.loads(
            subprocess.check_output(
                ["bspc", "wm", "--dump-state"], universal_newlines=True
            )
        )

        for monitor in status["monitors"]:
            for desktop in monitor["desktops"]:
                for button in self.buttons:
                    if button.desktop_id == str(desktop["name"]):
                        # Определяем статусы рабочего стола
                        is_focused = monitor["focusedDesktopId"] == desktop["id"]
                        is_occupied = desktop["root"] is not None

                        # Определяем видимость кнопки
                        if desktop["root"] or is_focused:
                            button.set_visible(True)
                        else:
                            button.set_visible(False)

                        if desktop["root"] is not None:
                            is_urgent = self.check_if_urgent(desktop["root"])
                        else:
                            is_urgent = False

                        # Обновляем стили
                        button.get_style_context().remove_class("active")
                        button.get_style_context().remove_class("occupied")
                        button.get_style_context().remove_class("urgent")

                        if is_focused:
                            button.get_style_context().add_class("active")
                        if is_occupied:
                            button.get_style_context().add_class("occupied")
                        if is_urgent:
                            button.get_style_context().add_class("urgent")
                        button.update_label()

    def check_if_urgent(self, root_node: dict):
        """Рекурсивно проверяет, есть ли срочные окна в дереве узлов."""
        if root_node is None:
            return False
        if root_node.get("client") and "urgent" in root_node["client"]:
            return True
        if "firstChild" in root_node and self.check_if_urgent(root_node["firstChild"]):
            return True
        if "secondChild" in root_node and self.check_if_urgent(
            root_node["secondChild"]
        ):
            return True

        return False

    def listen_bspwm(self):
        # Слушаем события bspwm
        process = subprocess.Popen(
            ["bspc", "subscribe", "report"],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )

        while True:
            output = process.stdout.readline()
            if output:
                GLib.idle_add(self.update_state)

    def on_workspace_click(self, widget, event):
        # Обработка клика для переключения рабочего стола
        execute(f"bspc desktop -f {widget.desktop_id}", shell=True)
