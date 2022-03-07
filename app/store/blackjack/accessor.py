import typing
import pickle
from typing import Optional, List

from app.base.base_accessor import BaseAccessor
from app.blackjack.models import User, Player, Table, TableModel, UserModel, PlayerModel
from app.store.bot.deck import Deck
from app.store.bot.state import PlayerState
from asyncpg import ForeignKeyViolationError, NotNullViolationError
from sqlalchemy import and_


if typing.TYPE_CHECKING:
    from app.web.app import Application


class BlackJackAccessor(BaseAccessor):
    async def create_player(self, player: Player):
        """Создает игрока в БД"""
        if await self.get_player_by_id(player.vk_id, player.table_id) is None:
            await PlayerModel.create(
                vk_id=player.vk_id,
                table_id=player.table_id,
                cards=pickle.dumps(player.cards),
                state=player.state,
                bet=player.bet,
            )
        else:
            pass

    async def create_table(self, table: Table):
        # TODO: изменить входные параметры на Table
        """Создает стол в БД"""
        if await self.get_table_by_peer_id(table.peer_id) is None:
            tables = await TableModel.query.gino.all()
            await TableModel.create(
                id=len(tables) + 1, 
                peer_id=table.peer_id,
                created_at= table.created_at,
                deck=pickle.dumps(table.deck), 
                state=table.state
            )
        else:
            pass

    async def create_user(self, user: User):
        """Создает пользователя в БД"""
        if await self.get_user_by_id(user.vk_id) is None:
            await UserModel.create(
                vk_id=user.vk_id,
                username=user.username,
                info=user.info,
                num_of_wins=user.num_of_wins,
                cash=user.cash,
            )
        else:
            pass

    async def get_player_by_id(self, vk_id: int, table_id: int) -> Player:
        players = await PlayerModel.query.where(
            and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)
        ).gino.all()
        if len(players) == 0:
            return None
        if len(players) == 1:
            return Player.from_database(players[0])

    async def get_players_on_table(self, table_id: int) -> list[Player]:
        players = await PlayerModel.query.where(
            PlayerModel.table_id == table_id
        ).gino.all()
        return [Player.from_database(player) for player in players]

    async def get_next_waiting_player(self, table_id: int) -> Optional[Player]:
        players = await PlayerModel.query.where(
            and_(
                PlayerModel.table_id == table_id,
                PlayerModel.state == PlayerState.WAITING_TURN.str,
            )
        ).gino.all()
        if len(players) == 0:
            return None
        else:
            return Player.from_database(players[0])

    async def get_table_by_peer_id(self, id_: int) -> Optional[Table]:
        # Находим незавершенный стол с таким айди, если он сущесвтует
        table = await TableModel.query.where(
            and_(TableModel.peer_id == id_, TableModel.state != "/end_game")
        ).gino.all()
        if len(table) == 0:
            return None
        if len(table) == 1:
            return Table.from_database(table[0])

    async def get_user_by_id(self, vk_id: int) -> Optional[User]:
        user = await UserModel.query.where(UserModel.vk_id == vk_id).gino.all()
        if len(user) == 0:
            return None
        if len(user) == 1:
            return User.from_database(user[0])

    async def add_win_to_user(self, vk_id: int):
        user = await self.get_user_by_id(vk_id)
        await UserModel.update.values(num_of_wins=user.num_of_wins + 1).where(
            UserModel.vk_id == vk_id
        ).gino.all()

    async def set_player_cards(self, vk_id: int, table_id: int, cards: Deck):
        # modification here
        cards = pickle.dumps(cards)
        await PlayerModel.update.values(cards=cards).where(
            and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)
        ).gino.all()

    async def set_player_bet(self, vk_id: int, table_id: int, bet: float):
        # modification here
        await PlayerModel.update.values(bet=bet).where(
            and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)
        ).gino.all()

    async def set_table_cards(self, id: int, cards: Deck):
        cards = pickle.dumps(cards)
        await TableModel.update.values(deck=cards).where(TableModel.id == id).gino.all()

    async def delete_table(self, table_id: int):
        await TableModel.delete.where(TableModel.id == table_id).gino.all()

    async def set_user_cash(self, vk_id: int, cash: int):
        user = await self.get_user_by_id(vk_id)
        await UserModel.update.values(cash=user.cash + cash).where(
            UserModel.vk_id == vk_id
        ).gino.all()

    # ЭТА ЧАСТЬ РАБОТАЕТ КАК СТЕЙТ АЦЕССОР
    async def get_player_state(self, vk_id: int, table_id: int) -> int:
        player = await self.get_player_by_id(vk_id, table_id)
        return player.state

    async def set_player_state(self, vk_id: int, table_id: int, state: str):
        # modification here
        await PlayerModel.update.values(state=state).where(
            and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)
        ).gino.all()

    async def get_table_state(self, table_id: int) -> int:
        table = await TableModel.query.where(TableModel.id == table_id).gino.all()
        if len(table) == 0:
            return None
        if len(table) == 1:
            return table[0]

    async def set_table_state(self, id: int, state):
        await TableModel.update.values(state=state).where(
            TableModel.id == id
        ).gino.all()
