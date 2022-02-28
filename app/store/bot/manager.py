import typing
import random
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message
from app.blackjack.models import User, Player, Table
from app.store.bot.state import StateManager


if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")
        self.table_states = ['/start_reg', '/stop_reg', '/start_game', '/stop_game']
        #self.statemanager = StateManager(self.app.store.blackjack)

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            table_state = await self.app.store.blackjack.get_table_state(update.object.peer_id)
            # обработка нажатия на кнопку
            if update.type == 'message_event':
                button_type = update.object.body['payload']['button']
                if button_type == "reg":
                    await self.handle_registration(update)
                if button_type == "add_card":
                    await self.draw_card(update)
                if button_type == "end_turn":
                    await self.end_turn(update)

            # обработка команды из чата
            if update.type == 'message_new':
                command = update.object.body["message"]["text"]
                # TODO: обработка неправильной комманды от пользователя
                if command == "/start_reg":
                    await self.handle_start_reg(update)
                elif command == "/stop_reg":
                    await self.handle_stop_reg(update)
                elif command == "/start_game":
                    await self.game_process(update)
                else:
                    await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text="test",#update.object.body,
                            peer_id = update.object.peer_id
                        )
                    )

    async def check_state(self, command: str, table_state: str) -> bool:
        ind = self.table_states.index(table_state)
        return self.table_states[ind+1] == command

    async def handle_registration(self, update: Update):
        vk_id = update.object.user_id
        username = await self.app.store.vk_api.get_username(update.object.user_id)
        await self.app.store.blackjack.create_user(User(vk_id, username, info=str({})))
        await self.app.store.blackjack.create_player(Player(vk_id, update.object.peer_id, 0, 0, [], 0))
        event_data = {"type": "show_snackbar",
                      "text": "Вы зарегистрировались"}
        params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                  "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
        await self.app.store.vk_api.send_snackbar(params, event_data)

    async def game_process(self, update: Update):
        players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
        text = "После раздачи игрокам выпали следующие карты:\n"
        for i, player in enumerate(players):
            # Переводим всех игроков, кроме диллера в состояние 1
            if player.vk_id != 1:
                await self.app.store.blackjack.set_player_state(player.vk_id, player.table_id, 1)
            
            # Высылаем кнопки и сообщение о регистрации
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            text += f"{i+1}. @id{player.vk_id} ({user.username})\n"
            cards = []
            
            # обрабатываем случай диллера
            if player.vk_id == 1:
                for i in range(1):
                    card = random.randint(0,10)
                    cards.append(card)
                    text += f"📜 Карта {card}\n"
            else:    
                for i in range(2):
                    card = random.randint(0,10)
                    cards.append(card)
                    text += f"📜 Карта {card}\n"
        
            # Добавляем выпавшие карты в БД игрока
            await self.app.store.blackjack.set_player_cards(player.vk_id, player.table_id, cards)

        button1 ={"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"add_card"},
            "label":"Добрать карту"}
                }
        button2 ={"color": "negative",
            "action":{  
            "type":"callback",
            "payload":{"button":"end_turn"},
            "label":"Завершить ход"}
                }
        buttons = [[button1, button2]]
        keyboard = {  
            "one_time": False,
            "inline": False, 
            "buttons": buttons}

        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ), keyboard=keyboard)

    async def handle_stop_reg(self, update: Update):
        # TODO: обработать кейс когда никто не зарегистрировался
        # Изменяем состояние игрового стола
        await self.app.store.blackjack.set_table_state(update.object.peer_id, self.table_states[1])
        
        # создаем диллера
        await self.app.store.blackjack.create_player(Player(1, update.object.peer_id, 0, 0, [], 2))

        # Высылаем сообщение об окончании регистрации
        players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
        text = "Регистрация участников окончена.\nСписок игроков:\n"        
        for i, player in enumerate(players):
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            text += f"{i+1}. @id{player.vk_id} ({user.username})\n"
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
        await self.app.store.blackjack.create_table(id=update.object.peer_id, state=self.table_states[0])
        button ={"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"reg"},
            "label":"Сесть за стол"}
                }
        buttons = [[button]]
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
                keyboard=keyboard)

    async def end_turn(self, update: Update):
        vk_id = update.object.user_id
        peer_id = update.object.peer_id
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)
        if player.state == 2:
            # Высылаем snackbar о том что игрок закончил ход
            event_data = {"type": "show_snackbar",
                        "text": "Ваш ход окончен. Дождитесь конца хода других игроков."}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)

            # TODO: если все игроки в состоянии 2, перевести стол к состоянию 3 и подвести итоги
            players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
            if await self.check_all_players_state(players):
                await self.summarize(update)
        else:
            await self.app.store.blackjack.set_player_state(vk_id, peer_id, 2)
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            cards = player.cards
            text = f"Игрок @id{vk_id} ({user.username}) заврешил ход с картами:\n"

            for card in cards:
                    text += f"📜 Карта {card}\n"

            await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update.object.user_id,
                                text=text,#update.object.body,
                                peer_id = update.object.peer_id
                            ))

            # Высылаем snackbar о конце ход
            event_data = {"type": "show_snackbar",
                        "text": "Вы закончили ход"}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)

            # TODO: если все игроки в состоянии 2, перевести стол к состоянию 3 и подвести итоги
            players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
            if await self.check_all_players_state(players):
                await self.summarize(update)
    

    async def draw_card(self, update: Update):
        vk_id = update.object.user_id
        peer_id = update.object.peer_id
        
        # TODO: Сделать проверку состояния игрока, если состояние игрока не 2 то добрать, иначе pass
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)
        if player.state != 2 or vk_id == 1:
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            text = f"Игрок @id{vk_id} ({user.username}) добрал карту:\n"
            cards = player.cards 
            card = random.randint(0,10)
            text += f"📜 Карта {card}\n"
            cards.append(card)

            await self.app.store.blackjack.set_player_cards(vk_id, peer_id, cards)

            await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update.object.user_id,
                                text=text,#update.object.body,
                                peer_id = update.object.peer_id
                            ))
            
            # Высылаем snackbar о доборе карты
            if vk_id != 1:
                event_data = {"type": "show_snackbar",
                            "text": "Вы добрали карту"}
                params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                        "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
                await self.app.store.vk_api.send_snackbar(params, event_data)
            # TODO: Если сумма карт больше 21, перевести игрока в состояние 2
            if sum(cards) > 20:
                await self.end_turn(update)
        
        if player.state == 2:
            # Высылаем snackbar о том что игрок закончил ход
            event_data = {"type": "show_snackbar",
                        "text": "Ваш ход окончен. Дождитесь конца хода других игроков."}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)


    async def summarize(self, update: Update):
        update.object.user_id = 1
        diler = await self.app.store.blackjack.get_player_by_id(1, update.object.peer_id)
        
        while sum(diler.cards) < 14:
            await self.draw_card(update)
            diler = await self.app.store.blackjack.get_player_by_id(1, update.object.peer_id)
        
        # высылаем сообщение о конце хода диллера
        cards = diler.cards
        diler_user = await self.app.store.blackjack.get_user_by_id(1)
        text = f"Игрок @id{diler.vk_id} ({diler_user.username}) заврешил ход с картами:\n"

        for card in cards:
                text += f"📜 Карта {card}\n"

        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ))
    
        # Подводим итоги матча
        diler_sum = sum(diler.cards)
        players = await self.app.store.blackjack.get_players_on_table(update.object.peer_id)
        text = f"Все игроки завершили ход, результаты:\n"
        for i, player in enumerate(players):
            if player.vk_id != 1:
                user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
                user_sum = sum(player.cards)
                
                # TODO: сделать сравнение с диллером
                if user_sum > 21:
                    result = "Поражение"
                elif user_sum == 21 and diler_sum == 21:
                    result = "Ничья"
                elif user_sum == 21 and diler_sum != 21:
                    result = "Победа"
                elif user_sum < 21 and diler_sum > 21:
                    result = "Победа"
                elif user_sum < 21 and diler_sum == 21:
                    result = "Поражение"
                elif user_sum < 21 and user_sum < diler_sum:
                    result = "Поражение"
                elif user_sum < 21 and user_sum > diler_sum:
                    result = "Победа"
                text += f"{i+1}. @id{player.vk_id} ({user.username}) - {result}!\n"

        await self.app.store.blackjack.set_table_state(update.object.peer_id, "/game_over")
        
        buttons = []
        keyboard = {  
            "one_time": False,
            "inline": False, 
            "buttons": buttons}
        await self.app.store.vk_api.send_message(
                Message(
                    user_id=1,
                    text=text,
                    peer_id = update.object.peer_id
                ),
                keyboard=keyboard)

    async def check_all_players_state(self, players : list[Player]) -> bool:
        flag = True
        for player in players:
            if player.state != 2:
                flag = False
        return flag


