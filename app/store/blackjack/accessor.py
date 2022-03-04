import typing
import pickle
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.blackjack.models import User, Player, Table, TableModel, UserModel, PlayerModel
from app.store.database.gino import db
from app.store.bot.deck import Deck
from app.store.bot.state import PlayerState
from typing import List
from asyncpg import ForeignKeyViolationError, NotNullViolationError
from sqlalchemy import and_


if typing.TYPE_CHECKING:
    from app.web.app import Application

class BlackJackAccessor(BaseAccessor):
    # TODO: сделать очередность хода игроков
    # TODO: сделать таймер?
    async def create_player(self, player: Player):
        if await self.get_player_by_id(player.vk_id, player.table_id) is None:
            await PlayerModel.create(vk_id=player.vk_id, table_id=player.table_id,
                                     cards=pickle.dumps(player.cards),
                                     state=player.state, bet = player.bet)
        else:
            pass
        

    async def create_table(self, peer_id: int, deck: Deck, state: int):
        # TODO: изменить состояния
        if await self.get_table_by_peer_id(peer_id) is None:
            tables = await TableModel.query.gino.all()
            deck = pickle.dumps(deck)
            await TableModel.create(id=len(tables)+1,peer_id=peer_id, deck=deck, state=state)
        else:
            pass

    async def create_user(self, user: User):# vk_id: int, username: str, info: dict):
        if await self.get_user_by_id(user.vk_id) is None:
            await UserModel.create(vk_id=user.vk_id,
                                   username=user.username,
                                   info=user.info,
                                   num_of_wins=user.num_of_wins,
                                   cash=user.cash)
        else:
            pass
    
    async def add_win_to_user(self, vk_id: int):
        user = await self.get_user_by_id(vk_id)
        await UserModel.update.values(num_of_wins=user.num_of_wins+1).where(UserModel.vk_id == vk_id).gino.all()

    
    async def get_player_by_id(self, vk_id: int, table_id:int):
        player = await PlayerModel.query.where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()
        if len(player) == 0:
            return None
        if len(player) == 1:
            return Player(player[0].vk_id, player[0].table_id, pickle.loads(player[0].cards), player[0].state, player[0].bet)

    async def get_players_on_table(self, table_id: int):
        players = await PlayerModel.query.where(PlayerModel.table_id == table_id).gino.all()
        for i in range(len(players)):
            players[i].cards = pickle.loads(players[i].cards)
        return players

    async def get_next_waiting_player(self, table_id: int):
        players = await PlayerModel.query.where(and_(PlayerModel.table_id == table_id, PlayerModel.state == PlayerState.WAITING_TURN.str)).gino.all()
        if len(players) == 0:
            return None
        else:
            player = players[0]
            player.cards = pickle.loads(player.cards)
            return player

    
    async def get_table_by_peer_id(self, id_:int) -> Optional[Table]:
        # Находим незавершенный стол в беседе peer_id
        #table = await TableModel.query.where(TableModel.id == id_)).gino.all()
        table = await TableModel.query.where(and_(TableModel.peer_id == id_, TableModel.state != '/end_game')).gino.all()
        if len(table) == 0:
            return None
        if len(table) == 1:
            table = table[0]
            return Table(table.id, table.peer_id, table.created_at, pickle.loads(table.deck), table.state)

    async def get_user_by_id(self, vk_id:int) -> Optional[User]:
        user = await UserModel.query.where(UserModel.vk_id == vk_id).gino.all()
        if len(user) == 0:
            return None
        if len(user) == 1:
            return User(user[0].vk_id, user[0].username, user[0].info, user[0].cash, user[0].num_of_wins)

    async def set_player_cards(self, vk_id: int, table_id: int, cards: Deck):
        # modification here
        cards = pickle.dumps(cards)
        await PlayerModel.update.values(cards=cards).where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()

    async def set_player_bet(self, vk_id: int, table_id: int, bet: float):
        # modification here
        await PlayerModel.update.values(bet=bet).where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()

    async def set_table_cards(self, id: int, cards: Deck):
        cards = pickle.dumps(cards)
        await TableModel.update.values(deck=cards).where(TableModel.id == id).gino.all()

    async def delete_table(self, table_id: int):
        await TableModel.delete.where(TableModel.id == table_id).gino.all()

    async def set_user_cash(self, vk_id: int, cash: int):
        user = await self.get_user_by_id(vk_id)
        await UserModel.update.values(cash=user.cash + cash).where(UserModel.vk_id == vk_id).gino.all()
    
    #async def get_player_cards(self, vk_id: int, table_id: int):
    #    player = await PlayerModel.query.where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()


    
    # TODO: Эта часть работает как стейт ацессор 
    async def get_player_state(self, vk_id: int, table_id: int) -> int:
        player = await self.get_player_by_id(vk_id, table_id)
        return player.state

    async def set_player_state(self, vk_id: int, table_id: int, state: str):
        # modification here
        await PlayerModel.update.values(state=state).where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()

    async def get_table_state(self, table_id: int) -> int:
        table = await TableModel.query.where(TableModel.id == table_id).gino.all()
        if len(table) == 0:
            return None
        if len(table) == 1:
            return table[0]

    async def set_table_state(self, id: int, state):
        await TableModel.update.values(state=state).where(TableModel.id == id).gino.all()
        
    # async def create_theme(self, title: str) -> Theme:
    #     return theme

    # async def get_theme_by_title(self, title: str) -> Optional[Theme]:
    #     for theme in await self.list_themes():
    #         if theme.title == title:
    #             return theme
    #     else:
    #         return None


    # async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
    #     for theme in await self.list_themes():
    #         if theme.id == id_:
    #             return theme
    #     else:
    #         return None


    # async def list_themes(self) -> List[Theme]:
    #     themes =  await ThemeModel.query.gino.all()
    #     if len(themes) == 0:
    #         return []
    #     else:
    #         return [Theme(id=theme.id, title=theme.title) for theme in themes]

    # async def create_answers(self, question_title: str, question_id: int, answers: List[Answer]):        
    #     for answer in answers:
            
    #         await AnswerModel.create(question_title=question_title, question_id=question_id, title=answer.title, is_correct=int(answer.is_correct))


    # async def create_question(
    #     self, title: str, theme_id: int, answers: List[Answer]
    # ) -> Question:
    #     if theme_id is None:
    #         raise NotNullViolationError
    #     if await self.get_theme_by_id(theme_id) is None:
    #         raise ForeignKeyViolationError
    #     #theme = await self.get_theme_by_id(theme_id)
    #     #if theme.title is None:
    #     #    raise NotNullViolationError
    #     question_id = len(await self.list_questions())+1
    #     theme = await self.get_theme_by_id(theme_id)
    #     await QuestionModel.create(theme_title=theme.title,id=question_id, title=title, theme_id=theme_id)
    #     await self.create_answers(title, question_id, answers)
    #     q = Question(id=question_id, title=title,theme_id=theme_id, answers=answers)
    #     return q


    # async def get_question_by_title(self, title: str) -> Optional[Question]:
    #     questions =  await QuestionModel.query.gino.all()
    #     for q in questions:
    #         if q.title == title:
    #             answers = await AnswerModel.query.where(AnswerModel.question_id == q.id).gino.all()
    #             answers = [Answer(answer.title,answer.is_correct) for answer in answers]
    #             return Question(id=q.id, title=q.title,theme_id=q.theme_id, answers=answers)


    # async def list_questions(self, theme_id: Optional[int] = None) -> List[Question]:
    #     questions =  await QuestionModel.query.gino.all()
    #     output =[]
    #     if len(questions) == 0:
    #         return output
    #     else:
    #         for q in questions:
    #             answers = await AnswerModel.query.where(AnswerModel.question_id == q.id).gino.all()
    #             answers = [Answer(answer.title,answer.is_correct) for answer in answers]
    #             output.append(Question(id=q.id, title=q.title,theme_id=q.theme_id, answers=answers))
    #         return output
