from datetime import date, datetime, timedelta

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical
from textual.reactive import var
from textual.widgets import Button, Footer, Header, Label, ListItem, Static

from systema.proxies.item import ItemProxy
from systema.tui.screens.base import ProjectScreen
from systema.tui.widgets import ListView


class CalendarScreen(ProjectScreen):
    BINDINGS = [
        Binding("q,escape", "dismiss", "Quit"),
        Binding("n", "next_month", "Next month", show=True),
        Binding("p", "previous_month", "Previous month", show=True),
        # Binding("a", "add_item", "Add", show=True),
        # Binding("e", "edit_item", "Edit", show=True),
        # Binding("d", "delete_item", "Delete", show=True),
        # Binding("shift+down,J", "move_down", "Move down", show=True),
        # Binding("shift+up,K", "move_up", "Move up", show=True),
        Binding("t", "toggle_collapsible", "Show/Hide side panel", show=True),
        Binding("m", "select_mode", "Select mode", show=True),
    ]
    CSS_PATH = "styles/calendar.css"

    proxy: ItemProxy
    datetime_label: Label = Label()
    days: list[Static] = [Static(str(i), classes="day") for i in range(7 * 6)]
    grid: Grid

    month_year: var[tuple[int, int]] = var(
        (datetime.today().month, datetime.today().year)
    )

    def compose(self) -> ComposeResult:
        today = datetime.today()
        self.grid = Grid(*self.days)
        self.month_year = (today.month, today.year)

        yield Header()
        with Horizontal():
            self.lv = ListView()
            yield self.lv
            with Vertical(classes="calendar-container"):
                with Horizontal(classes="topbar"):
                    yield Button("Previous", classes="previous")
                    yield self.datetime_label
                    yield Button("Next", classes="next")

                yield self.grid
        yield Footer()

    @property
    def reference_date(self):
        month, year = self.month_year
        return date(year, month, 1)

    def watch_month_year(self, month_year: tuple[int, int]):
        month, year = month_year

        self.datetime_label.update(date(year, month, 1).strftime("%b %Y"))

        initial_date = get_initial_date_of_monthly_calendar(year, month)
        final_date = get_final_date_of_monthly_calendar(year, month)

        qty_days = (final_date - initial_date).days
        weeks = qty_days // 7
        if qty_days % 7:
            weeks += 1

        self.grid.styles.grid_size_rows = weeks

        for day, offset in zip(self.days, range((final_date - initial_date).days + 1)):
            date_ = initial_date + timedelta(days=offset)
            day.update(str(date_.day))
            day.set_class(date_.month == month, "current-month")

    def get_items(self):
        return [ListItem(Static("asdf")) for _ in range(10)]

    async def populate(self):
        for i in self.proxy.all():
            self.lv.append(ListItem(Label(i.name)))

    async def clear(self):
        await self.lv.clear()

    def action_toggle_collapsible(self):
        self.lv.toggle_class("collapsed")

    @on(Button.Pressed, ".previous")
    async def go_to_previous_month(self):
        await self.action_previous_month()

    async def action_previous_month(self):
        month, year = self.month_year
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        self.month_year = (month, year)

    @on(Button.Pressed, ".next")
    async def go_to_next_month(self):
        await self.action_next_month()

    async def action_next_month(self):
        month, year = self.month_year
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        self.month_year = (month, year)


def get_last_day_of_month(year: int, month: int):
    if month == 12:
        last_day_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day_of_month = date(year, month + 1, 1) - timedelta(days=1)
    return last_day_of_month


def get_initial_date_of_monthly_calendar(year: int, month: int):
    first_day_of_month = date(year, month, 1)
    week_of_first_day = first_day_of_month.isocalendar().week
    if first_day_of_month.weekday() != 6:
        week_of_first_day -= 1
        if week_of_first_day == 0:
            week_of_first_day = 52
            year -= 1
    initial_date = date.fromisocalendar(year, week_of_first_day, 7)
    return initial_date


def get_final_date_of_monthly_calendar(year: int, month: int):
    last_day_of_month = get_last_day_of_month(year, month)
    week_of_last_day = last_day_of_month.isocalendar().week
    if last_day_of_month.weekday() == 6:
        week_of_last_day += 1
        if week_of_last_day == 53:
            week_of_last_day = 1
            year += 1
    final_date = date.fromisocalendar(year, week_of_last_day, 6)
    return final_date
