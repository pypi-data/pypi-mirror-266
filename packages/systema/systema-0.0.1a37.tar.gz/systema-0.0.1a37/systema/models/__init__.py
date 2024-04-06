from systema.models.auth import User
from systema.models.bin import Bin
from systema.models.board import Board
from systema.models.card import Card
from systema.models.checklist import Checklist
from systema.models.item import Item
from systema.models.project import Project
from systema.models.task import Task


def get_all_db_models():
    return (
        Project,
        Task,
        Checklist,
        Item,
        Board,
        Bin,
        Card,
        User,
    )
