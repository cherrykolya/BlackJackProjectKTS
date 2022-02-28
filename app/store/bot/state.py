import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application
from app.store.blackjack.accessor import BlackJackAccessor

class StateManager:
    # TODO: realise State Manager
    def __init__(self, accessor: BlackJackAccessor):
        self.accessor = accessor

    async def get_player_state(self, vk_id: int, table_id: int) -> int:
        pass

    async def set_player_state(self, vk_id: int, table_id: int, state: int):
        pass

    async def get_table_state(self, table_id: int) -> int:
        pass

    async def set_table_state(self, table_id: int, state):
        pass