import typing
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.blackjack.models import User, Player, Table, TableModel, UserModel, PlayerModel
from app.store.database.gino import db
from typing import List
from asyncpg import ForeignKeyViolationError, NotNullViolationError

if typing.TYPE_CHECKING:
    from app.web.app import Application

class BlackJackAccessor(BaseAccessor):
    # TODO: реализовать функции работы с БД
    # TODO: обработать else сценарии
    async def create_player(self, vk_id: int, table_id: int, cash: int=None, num_of_wins: int=None):
        if await self.get_player_by_id(vk_id, table_id) is None:
            await PlayerModel.create(vk_id=vk_id, table_id=table_id, cash=0, num_of_wins=0)
        else:
            pass
        

    async def create_table(self, id: int, state: int):
        # TODO: изменить состояния
        if await self.get_table_by_id(id) is None:
            await TableModel.create(id=id, state=0)
        else:
            pass

    async def create_user(self, vk_id: int, username: str, info: dict):
        if await self.get_user_by_id(vk_id) is None:
            await UserModel.create(vk_id=vk_id, username=username, info=info)
        else:
            pass
    
    async def get_player_by_id(self, vk_id: int, table_id:int):
        query = db.text('SELECT * FROM player WHERE vk_id = :vk_id AND table_id = :table_id')
        #query = db.text('SELECT * FROM users WHERE id = :id_val')
        player = await db.all(query, vk_id=vk_id, table_id=table_id)
        #player = await PlayerModel.query.where(PlayerModel.vk_id == vk_id, PlayerModel.table == table_id).gino.all()
        if len(player) == 0:
            return None
        if len(player) == 1:
            return player[0]

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
