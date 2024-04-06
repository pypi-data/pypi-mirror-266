import asyncio

from textual import on, work
from textual.app import App, UnknownModeError
from textual.binding import Binding
from textual.reactive import var

from systema.management import Settings
from systema.models.project import ProjectRead
from systema.proxies.card import CardProxy
from systema.proxies.item import ItemProxy
from systema.proxies.project import ProjectProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.screens.checklist import ChecklistScreen
from systema.tui.screens.config import Config
from systema.tui.screens.dashboard import Dashboard
from systema.tui.screens.kanban import KanbanScreen
from systema.tui.screens.mode_modal import Mode, ModeModal
from systema.tui.screens.project_list import ProjectList

PROJECT_SCREENS: dict[Mode, ProjectScreen] = {
    Mode.CHECKLIST: ChecklistScreen(ItemProxy),
    Mode.KANBAN: KanbanScreen(CardProxy),
}


class SystemaTUIApp(App[None]):
    TITLE = "Systema"
    BINDINGS = [
        Binding("q,escape", "quit", "Quit", show=True),
        Binding("up,k", "focus_previous", "Focus previous", show=False),
        Binding("down,j", "focus_next", "Focus next", show=False),
    ]
    CSS_PATH = "style.css"
    SCREENS = {
        "projects": ProjectList,
        "mode": ModeModal,
        **PROJECT_SCREENS,
    }
    MODES = {
        "main": Dashboard,
        "config": Config,
        **PROJECT_SCREENS,
    }
    project: var[ProjectRead | None] = var(None)

    async def on_mount(self):
        await self.switch_mode("main")

    def watch_project(self, project: ProjectRead | None):
        for mode in Mode:
            if screen := PROJECT_SCREENS.get(mode):
                screen.project = project

    @on(ProjectList.Selected)
    async def handle_project_selection(self, message: ProjectList.Selected):
        self.project = message.project
        await self.switch_to_project_mode(
            self.project.id,
            self.project.mode or Settings().default_mode,
            refresh=False,  # we musn't refresh, we are implicitly doing it when setting self.project
        )

    @work
    async def action_select_mode(self):
        if not self.project:
            return

        mode = await self.push_screen_wait("mode")
        if mode == self.current_mode:
            return

        await self.switch_to_project_mode(self.project.id, mode, True)

    async def switch_to_project_mode(self, id: str, mode: Mode, refresh: bool = True):
        try:
            screen = PROJECT_SCREENS[mode]

            with self.batch_update():
                if refresh:
                    await screen.safe_refresh()

                await asyncio.gather(
                    self.switch_mode(mode),
                    self.save_mode(id, mode),
                )
        except (UnknownModeError, KeyError):
            self.notify("Mode not implemented yet", severity="error")

    async def save_mode(self, project_id: str, mode: Mode):
        ProjectProxy().save_mode(project_id, mode)
