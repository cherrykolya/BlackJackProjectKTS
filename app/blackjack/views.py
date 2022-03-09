from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema, querystring_schema

from app.quiz.models import Answer
from app.blackjack.schemes import UserCashSchema
from app.quiz.schemes import (
    ThemeSchema,)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class CashAddView(AuthRequiredMixin, View):
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