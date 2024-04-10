from .auth import AuthCommands
from .base_commands import BaseCommands
from .cde import CdeCommands
from .config import ConfigCommands
from .pdd import PddCommands
from .users import UsersCommands


class Commands(BaseCommands):
    auth = AuthCommands
    cdeset = CdeCommands
    config = ConfigCommands
    pdd = PddCommands
    users = UsersCommands
