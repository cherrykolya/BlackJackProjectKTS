import typing
import random
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message


if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        for update in updates:

            if update.type == 'message_event':
                await self.handle_registration(update)
            if update.type == 'message_new':
                if update.object.body["message"]["text"] == "/start_reg":
                    await self.handle_start_reg(update)
                elif update.object.body["message"]["text"] == "/stop_reg":
                    await self.handle_stop_reg(update)
                elif update.object.body["message"]["text"] == "/start_game":
                    await self.game_process(update)
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text="test",#update.object.body,
                            peer_id = update.object.peer_id
                        )
                    )

    async def handle_registration(self, update: Update):
        vk_id = update.object.user_id
        await self.app.store.blackjack.create_user(vk_id=vk_id,username=f"Noname {vk_id}",info=str({}))
        await self.app.store.blackjack.create_player(vk_id=vk_id,table_id=update.object.peer_id)
        event_data = {"type": "show_snackbar",
                      "text": "Вы зарегистрировались"}
        params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                  "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
        await self.app.store.vk_api.registered(params, event_data)

    async def game_process(self, update: Update):
        players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
        text = "После раздачи игрокам выпали следующие карты:\n"
        for i, player in enumerate(players):
            text += f"{i+1}. @id{player.vk_id}\n"
            card_sum = 0
            for i in range(2):
                card = random.randint(0,10)
                card_sum += card
                text += f"📜 Карта {card}\n"
        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        )
                    )
        

    async def handle_stop_reg(self, update: Update):
        # TODO: Изменить состояние игрового стола
        players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
        text = "Регистрация участников окончена.\nСписок игроков:\n"
        for i, player in enumerate(players):
            text += f"{i+1}. @id{player.vk_id}\n"
        keyboard = {  
            "one_time": False,
            "inline": False, 
            "buttons": []}
        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ),
                        keyboard = keyboard
                    )

    async def handle_start_reg(self, update: Update):
        print(update.object.peer_id)
        await self.app.store.blackjack.create_table(id=update.object.peer_id, state=0)
        buttons = [[]]
        button ={"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"reg":"reg"},
            "label":"Сесть за стол"}
                }
        buttons[-1].append(button)
        keyboard = {  
            "one_time": False,
            "inline": False, 
            "buttons": buttons}
        await self.app.store.vk_api.send_message(
                Message(
                    user_id=1,
                    text="Привет, Сыграем в BlackJack?",
                    peer_id = update.object.peer_id
                ),
                keyboard=keyboard
            )
