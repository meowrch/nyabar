from fabric.hyprland.widgets import WorkspaceButton, Workspaces

from shared.widget_container import BoxWidget
from utils.functions import unique_list
from utils.widget_settings import BarConfig


class HyprlandWorkSpacesWidget(BoxWidget):
    """A widget to display the current workspaces."""

    def __init__(self, widget_config: BarConfig, **kwargs):
        super().__init__(name="workspaces-box", **kwargs)

        self.config = widget_config["workspaces"]
        ignored_ws = unique_list(self.config["ignored"])

        # Create a HyperlandWorkspace widget to manage workspace buttons
        self.workspace = Workspaces(
            name="workspaces",
            spacing=4,
            # Create buttons for each workspace if occupied
            buttons=None  # sending None to buttons will create occupied workspaces only
            if self.config["hide_unoccupied"]
            else [
                WorkspaceButton(id=i, label=str(i))
                for i in range(1, self.config["count"] + 1)
            ],
            # Factory function to create buttons for each workspace
            buttons_factory=lambda ws_id: WorkspaceButton(
                id=ws_id,
                label=f"{self.config['icon_map'].get(str(ws_id), ws_id)}",
                visible=ws_id not in ignored_ws,
            ),
            invert_scroll=self.config["reverse_scroll"],
            empty_scroll=self.config["empty_scroll"],
        )
        # Add the HyperlandWorkspace widget as a child
        self.children = self.workspace
