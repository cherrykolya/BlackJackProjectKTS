from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema, querystring_schema, docs

from app.blackjack.models import User, Table, Player
from app.blackjack.schemes import UserCashSchema, PlayerGetSchema, PlayersSchema, UserGetSchema, UserSchema, TableSchema, TableGetSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class CashAddView(AuthRequiredMixin, View):
    @docs(tags=["BlackJack"], summary="Adds cash to user", description="Adds cash to user by vk_id")
    @request_schema(UserCashSchema)
    #@response_schema(UserCashSchema)
    async def post(self):
        vk_id = self.data["vk_id"]
        cash = self.data["cash"]
        user = await self.store.blackjack.get_user_by_id(vk_id)
        if not user:
            raise HTTPConflict
        await self.store.blackjack.set_user_cash(vk_id, cash)

        return json_response(data=UserCashSchema().dump({"vk_id": vk_id, "cash": cash}))

class GetPlayersView(AuthRequiredMixin, View):
    @docs(tags=["BlackJack"], summary="Returns players on the table", description="Returns players by table_id")
    @request_schema(PlayerGetSchema)
    @response_schema(PlayersSchema)
    async def get(self):
        table_id = self.data["table_id"]

        players = await self.store.blackjack.get_players_on_table(table_id)
        if len(players) == 0:
            raise HTTPConflict

        return json_response(data=PlayersSchema().dump({"players": players}))

class GetUserView(AuthRequiredMixin, View):
    @docs(tags=["BlackJack"], summary="Returns user", description="Return user by vk_id")
    @request_schema(UserGetSchema)
    @response_schema(UserSchema)
    async def get(self):
        vk_id = self.data["vk_id"]

        user = await self.store.blackjack.get_user_by_id(vk_id)
        if not user:
            raise HTTPConflict

        return json_response(data=UserSchema().dump(user))

class GetTableView(AuthRequiredMixin, View):
    @docs(tags=["BlackJack"], summary="Returns table", description="Returns table by table_id")
    @request_schema(TableGetSchema)
    @response_schema(TableSchema)
    async def get(self):
        table_id = self.data["table_id"]

        table = await self.store.blackjack.get_table_by_id(table_id)
        if not table:
            raise HTTPConflict

        return json_response(data=TableSchema().dump(table))
    