from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class Dashboard(Screen[None]):
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("p", "projects", "Projects", show=True),
        Binding("c", "config", "Config", show=True),
    ]
    CSS_PATH = "styles/dashboard.css"

    def compose(self) -> ComposeResult:
        self.buttons_and_actions = {
            Button("Projects", id="projects"): self.action_projects,
            Button("Users", id="users"): None,
            Button("Config", id="config"): self.action_config,
        }
        yield Header()
        with Vertical():
            for button in self.buttons_and_actions:
                yield button
        yield Footer()

    def action_projects(self):
        self.app.push_screen("projects")

    def action_config(self):
        self.app.switch_mode("config")

    @on(Button.Pressed)
    def handle_button_pressed(self, message: Button.Pressed):
        if action := self.buttons_and_actions.get(message.button):
            return action()
        self.notify("Button not implemented yet", severity="error")
