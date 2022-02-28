import typing
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.blackjack.models import User, Player, Table, TableModel, UserModel, PlayerModel
from app.store.database.gino import db
from typing import List
from asyncpg import ForeignKeyViolationError, NotNullViolationError
from sqlalchemy import and_


if typing.TYPE_CHECKING:
    from app.web.app import Application

class BlackJackAccessor(BaseAccessor):
    # TODO: реализовать функции работы с БД
    # TODO: обработать else сценарии
    async def create_player(self, player: Player):# vk_id: int, table_id: int, cash: int=None, cards = [],num_of_wins: int=None, state: int = 0):
        
        if await self.get_player_by_id(player.vk_id, player.table_id) is None:
            await PlayerModel.create(vk_id=player.vk_id, table_id=player.table_id,
                                     cash=player.cash, cards=player.cards,
                                     num_of_wins=player.num_of_wins, state=player.state)
        else:
            pass
        

    async def create_table(self, id: int, state: int):
        # TODO: изменить состояния
        if await self.get_table_by_id(id) is None:
            await TableModel.create(id=id, state=state)
        else:
            pass

    async def create_user(self, user: User):# vk_id: int, username: str, info: dict):
        
        if await self.get_user_by_id(user.vk_id) is None:
            await UserModel.create(vk_id=user.vk_id, username=user.username, info=user.info)
        else:
            pass
    
    async def get_player_by_id(self, vk_id: int, table_id:int):
        player = await PlayerModel.query.where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()
        if len(player) == 0:
            return None
        if len(player) == 1:
            return Player(player[0].vk_id, player[0].table_id, player[0].cash,  player[0].num_of_wins, player[0].cards, player[0].state)

    async def get_players_on_table(self, table_id: int):
        players = await PlayerModel.query.where(PlayerModel.table_id == table_id).gino.all()
        return players

    
    async def get_table_by_id(self, id_:int) -> Optional[Table]:
        table = await TableModel.query.where(TableModel.id == id_).gino.all()
        if len(table) == 0:
            return None
        if len(table) == 1:
            return table[0]

    async def get_user_by_id(self, vk_id:int) -> Optional[User]:
        user = await UserModel.query.where(UserModel.vk_id == vk_id).gino.all()
        if len(user) == 0:
            return None
        if len(user) == 1:
            return user[0]

    async def set_player_cards(self, vk_id: int, table_id: int, cards: list):
        # modification here
        await PlayerModel.update.values(cards=cards).where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()

    #async def get_player_cards(self, vk_id: int, table_id: int):
    #    player = await PlayerModel.query.where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()


    
    # TODO: Эта часть работает как стейт ацессор 
    async def get_player_state(self, vk_id: int, table_id: int) -> int:
        player = await self.get_player_by_id(vk_id, table_id)
        return player.state

    async def set_player_state(self, vk_id: int, table_id: int, state: int):
        # modification here
        await PlayerModel.update.values(state=state).where(and_(PlayerModel.vk_id == vk_id, PlayerModel.table_id == table_id)).gino.all()

    async def get_table_state(self, table_id: int) -> int:
        table = await TableModel.query.where(TableModel.id == table_id).gino.all()
        if len(table) == 0:
            return None
        if len(table) == 1:
            return table[0]

    async def set_table_state(self, table_id: int, state):
        await TableModel.update.values(state=state).where(TableModel.id == table_id).gino.all()
        
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
