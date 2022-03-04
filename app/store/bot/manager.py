import typing
import random
import json
from logging import getLogger

from app.store.vk_api.dataclasses import Update, Message
from app.blackjack.models import User, Player, Table
from app.store.bot.state import TableState, PlayerState, Buttons
from app.store.bot.deck import Deck

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        # TODO: добавить кнопки между раундами
        # TODO: добавить таймер
        for update in updates:
            current_table = await self.app.store.blackjack.get_table_by_peer_id(update.object.peer_id)
            if current_table is None:
                deck = Deck()
                deck.generate_deck()
                deck.shuffle_deck()
                await self.app.store.blackjack.create_table(peer_id=update.object.peer_id, deck = deck, state=TableState.WAITING_REG.str)
                current_table = await self.app.store.blackjack.get_table_by_peer_id(update.object.peer_id)
            
            table_state = TableState(current_table.state)
            # обработка нажатия на кнопку
            if update.type == 'message_event':
                button_type = update.object.body['payload']['button']
                if button_type == "reg":
                    await self.handle_registration(update, current_table)
                if button_type == "add_card":
                    await self.draw_card(update, current_table)
                if button_type == "end_turn":
                    await self.end_turn(update, current_table)
                if button_type == "bet":
                    await self.register_bets(update, current_table)

            # обработка команды из чата
            if update.type == 'message_new':
                command = update.object.body["message"]["text"]
                if "payload" in update.object.body["message"].keys(): 
                    command = json.loads(update.object.body["message"]["payload"])["button"]
                if await self.check_state(command, table_state):
                    keyboard = {  
                        "one_time": False,
                        "inline": False, 
                        "buttons": await self.button_manager(TableState(command))}
                    update_handler = await self.context_manager(TableState(command))
                    await update_handler(update, current_table, keyboard)

                # TODO: обработка неправильной комманды от пользователя
                elif len(command) == 1:
                    if len(command[0]) > 0 and command[0][0] == "/" :
                        text = f"Доступны следующие команды:\n"
                        for i, state in  enumerate(table_state.next_state):
                            text += f"{i+1}. {state}\n"
                        await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update.object.user_id,
                                text=text,#update.object.body,
                                peer_id = update.object.peer_id
                            ))
    
    async def button_manager(self, table_state: TableState):
        button_to_send = {  TableState.WAITING_REG: [[Buttons.START_REG.value],
                                                     [Buttons.INFO.value]],
                            TableState.START_REG: [[Buttons.REG_USER.value], 
                                                   [Buttons.STOP_REG.value],
                                                   [Buttons.INFO.value]],
                            TableState.STOP_REG: [[Buttons.START_BETS.value],
                                                  [Buttons.INFO.value],
                                                  [Buttons.END_GAME.value]],
                            TableState.START_BETS: [[Buttons.BET_1.value, Buttons.BET_2.value, Buttons.BET_3.value, Buttons.BET_4.value],
                                                    [Buttons.INFO.value],
                                                    [Buttons.END_GAME.value]],
                            TableState.STOP_BETS: [[Buttons.START_GAME.value],
                                                   [Buttons.INFO.value],
                                                   [Buttons.END_GAME.value]],
                            TableState.START_GAME: [[Buttons.ADD_CARD.value, Buttons.END_TURN.value],
                                                   [Buttons.INFO.value],
                                                   [Buttons.END_GAME.value]],
                            TableState.END_GAME: [[Buttons.START_REG.value],
                                                     [Buttons.INFO.value]],
                            TableState.INFO: []                          
                            #TableState.START_BETS: self.handle_start_bets,
                            #TableState.STOP_BETS: self.handle_stop_bets,
                            #TableState.START_GAME: self.handle_start_game,
                            #TableState.INFO: self.handle_info,
                            #TableState.END_GAME: self.handle_end_game,
                            }
        return button_to_send[table_state]
        

    async def context_manager(self, table_state: TableState):
        function_to_call = {TableState.START_REG: self.handle_start_reg,
                            TableState.STOP_REG: self.handle_stop_reg,
                            TableState.START_BETS: self.handle_start_bets,
                            TableState.STOP_BETS: self.handle_stop_bets,
                            TableState.START_GAME: self.handle_start_game,
                            TableState.INFO: self.handle_info,
                            TableState.END_GAME: self.handle_end_game,}
        return function_to_call[table_state]

    async def check_state(self, command: str, table_state: TableState) -> bool:
        return command in table_state.next_state

    async def handle_info(self, update: Update, current_table: Table, keyboard):
        user = await self.app.store.blackjack.get_user_by_id(update.object.user_id)
        text = f"Статистика пользователя @id{user.vk_id} ({user.username})\n"
        text += f"Победы: {user.num_of_wins} 🏆\n"
        text += f"Банк: {user.cash} 💵\n"
        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ),)

    async def handle_end_game(self, update: Update, current_table: Table, keyboard):
        # Изменяем состояние игрового стола
        await self.app.store.blackjack.set_table_state(current_table.id, TableState.END_GAME.str)
        user = await self.app.store.blackjack.get_user_by_id(update.object.user_id)
        text = f"Игрок @id{user.vk_id} ({user.username}) досрочно завершил матч!\n"

        # высылаем уведомление об окончании игры
        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ),keyboard=keyboard)


    async def handle_registration(self, update: Update, current_table: Table):
        vk_id = update.object.user_id
        username = await self.app.store.vk_api.get_username(update.object.user_id)
        await self.app.store.blackjack.create_user(User(vk_id, username, str({}), 1000, 0))
        await self.app.store.blackjack.create_player(Player(vk_id, current_table.id, Deck(), PlayerState.WAITING_TURN.str, 0))
        
        event_data = {"type": "show_snackbar",
                      "text": "Вы зарегистрировались"}
        params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                  "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
        await self.app.store.vk_api.send_snackbar(params, event_data)

        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=f"@id{vk_id} ({username}) садится за стол!\n",
                            peer_id = update.object.peer_id
                        ),)

    async def handle_start_game(self, update: Update, current_table: Table, keyboard):
        players = await self.app.store.blackjack.get_players_on_table(current_table.id)
        text = "После раздачи игрокам выпали следующие карты:\n"
        # Получаем текущую колоду
        deck = current_table.deck

        for i, player in enumerate(players):
            # Переводим всех игроков, кроме диллера в состояние начала хода
            if player.vk_id != 1:
                await self.app.store.blackjack.set_player_state(player.vk_id, player.table_id, PlayerState.WAITING_TURN.str)
            
            # Высылаем кнопки и сообщение о регистрации
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            text += f"{i+1}. @id{player.vk_id} ({user.username})\n"
            cards = Deck()
            
            # обрабатываем случай диллера
            if player.vk_id == 1:
                for i in range(1):
                    card = deck.deck.pop()
                    cards.deck.append(card)
                    text += f"📜 {card}\n"
            else:    
                for i in range(2):
                    card = deck.deck.pop()
                    cards.deck.append(card)
                    text += f"📜 {card}\n"
        
            # Добавляем выпавшие карты в БД игрока
            await self.app.store.blackjack.set_player_cards(player.vk_id, player.table_id, cards)

        # Обновляем колоду в базе данных, в соответствии со взятыми картами
        await self.app.store.blackjack.set_table_cards(current_table.id, deck)

        # определяем игрока, который будет ходить первым
        player = await self.app.store.blackjack.get_next_waiting_player(current_table.id)
        await self.app.store.blackjack.set_player_state(player.vk_id,player.table_id, PlayerState.TURN_ACTIVE.str)

        user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
        text += f"Ход игрока @id{user.vk_id} ({user.username}) !"

        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ), keyboard=keyboard)

    async def handle_stop_reg(self, update: Update, current_table: Table, keyboard):
        # TODO: обработать кейс когда никто не зарегистрировался
        players = await self.app.store.blackjack.get_players_on_table(current_table.id)
        if len(players) == 0:
            text = "Никто не зарегистрировался, регистрация продолжается!\n" 
            await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update.object.user_id,
                                text=text,#update.object.body,
                                peer_id = update.object.peer_id
                            ),)
        else:
            # Изменяем состояние игрового стола
            await self.app.store.blackjack.set_table_state(current_table.id, TableState.STOP_REG.str)
            
            # создаем диллера
            await self.app.store.blackjack.create_player(Player(1, current_table.id, [], PlayerState.TURN_ENDED.str, 0))

            # Высылаем сообщение об окончании регистрации
            players = await self.app.store.blackjack.get_players_on_table(current_table.id)
            text = "Регистрация участников окончена.\nСписок игроков:\n"        
            for i, player in enumerate(players):
                user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
                text += f"{i+1}. @id{player.vk_id} ({user.username})\n"

            await self.app.store.vk_api.send_message(
                            Message(
                                user_id=update.object.user_id,
                                text=text,#update.object.body,
                                peer_id = update.object.peer_id
                            ),
                            keyboard = keyboard)

    async def handle_start_reg(self, update: Update, current_table: Table, keyboard):
        # создаем игровой стол и определяем в нем колоду-стек
        #deck = Deck()
        await self.app.store.blackjack.set_table_state(id=current_table.id, state=TableState.START_REG.str)
        await self.app.store.vk_api.send_message(
                Message(
                    user_id=1,
                    text="Привет, Сыграем в BlackJack?",
                    peer_id = update.object.peer_id
                ),
                keyboard=keyboard)

    async def end_turn(self, update: Update, current_table: Table):
        vk_id = update.object.user_id
        peer_id = current_table.id
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)

        if player.state == PlayerState.TURN_ACTIVE.str:
            # завершаем ход игрока
            await self.app.store.blackjack.set_player_state(vk_id, peer_id, PlayerState.TURN_ENDED.str)
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            cards = player.cards.deck
            text = f"Игрок @id{vk_id} ({user.username}) заврешил ход с картами:\n"

            for card in cards:
                    text += f"📜 {card}\n"

            # определяем игрока, который будет ходить cледующим
            next_player = await self.app.store.blackjack.get_next_waiting_player(current_table.id)
            if next_player is not None:
                await self.app.store.blackjack.set_player_state(next_player.vk_id,next_player.table_id, PlayerState.TURN_ACTIVE.str)
                next_user = await self.app.store.blackjack.get_user_by_id(next_player.vk_id)
                text += f"Ход игрока @id{next_user.vk_id} ({next_user.username}) !"

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
            players = await self.app.store.blackjack.get_players_on_table(peer_id)
            if await self.check_all_players_state(players, PlayerState.TURN_ENDED):
                await self.summarize(update, current_table)

        elif player.state == PlayerState.WAITING_TURN.str:
            # Высылаем snackbar о том что сейчас не ваш ход
            event_data = {"type": "show_snackbar",
                        "text": f"Сейчас не ваш ход!"}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)

        # обрабатываем случаи когда игрок уже закончил ход
        elif player.state == PlayerState.TURN_ENDED.str:
            # Высылаем snackbar о том что игрок закончил ход
            event_data = {"type": "show_snackbar",
                        "text": "Ваш ход окончен. Дождитесь конца хода других игроков."}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)
        
    
    async def draw_card(self, update: Update, current_table: Table):
        vk_id = update.object.user_id
        peer_id = current_table.id

        # Получаем текущую колоду-стек
        deck = current_table.deck

        # TODO: Сделать проверку состояния игрока, если состояние игрока не 2 то добрать, иначе pass
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)
        if player.state == PlayerState.TURN_ACTIVE.str or vk_id == 1:
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            text = f"Игрок @id{vk_id} ({user.username}) добрал карту:\n"
            cards = player.cards
            card = deck.deck.pop()
            text += f"📜 {card}\n"
            cards.deck.append(card)

            await self.app.store.blackjack.set_player_cards(vk_id, peer_id, cards)
            await self.app.store.blackjack.set_table_cards(peer_id, deck)

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
            # Если сумма карт больше 21, перевести игрока в состояние 2
            card_values = [card.value for card in cards.deck]
            if sum(card_values) > 20:
                await self.end_turn(update, current_table)
        
        elif player.state == PlayerState.WAITING_TURN.str:
            # Высылаем snackbar о том что сейчас не ваш ход
            event_data = {"type": "show_snackbar",
                        "text": f"Сейчас не ваш ход!"}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)

        elif player.state == PlayerState.TURN_ENDED.str:
            # Высылаем snackbar о том что игрок закончил ход
            event_data = {"type": "show_snackbar",
                        "text": "Ваш ход окончен. Дождитесь конца хода других игроков."}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)


    async def summarize(self, update: Update, current_table: Table):
        peer_id = current_table.id
        update.object.user_id = 1
        diler = await self.app.store.blackjack.get_player_by_id(1, peer_id)
        
        while sum([card.value for card in diler.cards.deck]) < 14:
            await self.draw_card(update, current_table)
            diler = await self.app.store.blackjack.get_player_by_id(1, peer_id)
        
        # высылаем сообщение о конце хода диллера
        cards = diler.cards.deck
        diler_user = await self.app.store.blackjack.get_user_by_id(1)
        text = f"Игрок @id{diler.vk_id} ({diler_user.username}) заврешил ход с картами:\n"

        for card in cards:
                text += f"📜 {card}\n"

        await self.app.store.vk_api.send_message(
                        Message(
                            user_id=update.object.user_id,
                            text=text,#update.object.body,
                            peer_id = update.object.peer_id
                        ))
    
        # Подводим итоги матча
        diler_sum = sum([card.value for card in diler.cards.deck])
        players = await self.app.store.blackjack.get_players_on_table(peer_id)
        text = f"Все игроки завершили ход, результаты:\n"
        for i, player in enumerate(players):
            if player.vk_id != 1:
                user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
                user_sum = sum([card.value for card in player.cards.deck])
                
                # TODO: сделать сравнение с диллером
                if user_sum > 21:
                    result = "Поражение 💩"
                elif user_sum == 21 and diler_sum == 21:
                    result = "Ничья"
                elif user_sum == 21 and diler_sum != 21:
                    result = "Победа 🥇"
                elif user_sum < 21 and diler_sum > 21:
                    result = "Победа 🥇"
                elif user_sum < 21 and diler_sum == 21:
                    result = "Поражение 💩"
                elif user_sum < 21 and user_sum <= diler_sum:
                    result = "Поражение 💩"
                elif user_sum < 21 and user_sum > diler_sum:
                    result = "Победа 🥇"
                
                bet = player.bet
                # TODO: Добавляем победу в рейтинг пользвоателя, изменяем кошелек
                if result == "Победа 🥇":
                    await self.app.store.blackjack.add_win_to_user(player.vk_id)
                    await self.app.store.blackjack.set_user_cash(player.vk_id, 2*bet)
                    text += f"{i+1}. @id{player.vk_id} ({user.username}) - {result}! + {2*bet}💵\n"
                if result == "Поражение 💩":
                    await self.app.store.blackjack.set_user_cash(player.vk_id, -bet)
                    text += f"{i+1}. @id{player.vk_id} ({user.username}) - {result}! - {bet}💵\n"
                
        # переводим стол в конечное состояние
        await self.app.store.blackjack.set_table_state(peer_id, TableState.END_GAME.str)
        
        keyboard = {  
                    "one_time": False,
                    "inline": False, 
                    "buttons": await self.button_manager(TableState.END_GAME)}
        await self.app.store.vk_api.send_message(
                Message(
                    user_id=1,
                    text=text,
                    peer_id = update.object.peer_id
                ),
                keyboard=keyboard)

    async def check_all_players_state(self, players : list[Player], state: PlayerState) -> bool:
        flag = True
        for player in players:
            if player.state != state.str and player.vk_id != 1:
                flag = False
        return flag

    async def register_bets(self,update: Update, current_table: Table):
        # TODO: сделать проверку состояния игрока, если он уже поставил не ставить
        # перевести игрока в состояние /placed_bet
        vk_id = update.object.user_id
        peer_id = current_table.id
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)

        if player.state == PlayerState.TURN_ACTIVE.str:
            user = await self.app.store.blackjack.get_user_by_id(vk_id)
            val = update.object.body['payload']['bet']
            bet = user.cash*val 
            
            # переводим игрока в некст состояние и заполняем его ставку
            await self.app.store.blackjack.set_player_state(vk_id, peer_id, PlayerState.TURN_ENDED.str)
            await self.app.store.blackjack.set_player_bet(vk_id, peer_id, bet)
            
            # Высылаем snackbar с размером ставки
            event_data = {"type": "show_snackbar",
                        "text": f"Размер вашей ставки {bet} 💵!"}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)
            
            text = f"@id{player.vk_id} ({user.username}) делает ставку {bet} 💵!\n"
            text += "\n"

            # get_players_on_table -> находим первого игрока, у которого state = waiting_turn, меняем состояние, 
            #Определяем следующего игрока TODO: Изменить состояние стола
            # определяем игрока, который будет ходить cледующим
            next_player = await self.app.store.blackjack.get_next_waiting_player(current_table.id)
            if next_player is not None:
                await self.app.store.blackjack.set_player_state(next_player.vk_id,next_player.table_id, PlayerState.TURN_ACTIVE.str)
                next_user = await self.app.store.blackjack.get_user_by_id(next_player.vk_id)
                text += f"Ход игрока @id{next_user.vk_id} ({next_user.username}) !"

            # Высылаем сообщение о ставке в чат
            await self.app.store.vk_api.send_message(
                    Message(
                        user_id=1,
                        text=text,
                        peer_id = update.object.peer_id
                    ),)

            if next_player is None:
                # TODO: перевести стол в фазу конца ставок
                await self.handle_stop_bets(update, current_table)


        elif player.state == PlayerState.WAITING_TURN.str:
            # Высылаем snackbar о том что сейчас не ваш ход
            event_data = {"type": "show_snackbar",
                        "text": f"Сейчас не ваш ход!"}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)

        elif player.state == PlayerState.TURN_ENDED.str:
            # Высылаем snackbar о том что игрок уже поставил
            event_data = {"type": "show_snackbar",
                        "text": f"Вы уже сделали ставку {player.bet} 💵!"}
            params = {"event_id": update.object.body['event_id'], "user_id":update.object.body['user_id'],
                    "peer_id": update.object.body['peer_id']}#, "event_data": event_data}
            await self.app.store.vk_api.send_snackbar(params, event_data)

    async def handle_stop_bets(self, update: Update, current_table: Table):
        # проверить все ли сделали ставки
        players = await self.app.store.blackjack.get_players_on_table(current_table.id)
        if await self.check_all_players_state(players, PlayerState.TURN_ENDED):
            # убрать кнопки и перевести стол в сосотояние конец ставок
            await self.app.store.blackjack.set_table_state(current_table.id, TableState.STOP_BETS.str)
            text = "Фаза ставок окончена!\nИгроки сделали следующие ставки:\n"
            for i, player in enumerate(players):
                if player.vk_id != 1:
                    user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
                    text += f"{i}. @id{player.vk_id} ({user.username}) - {player.bet} 💵!\n"
                    
            keyboard = {  
                        "one_time": False,
                        "inline": False, 
                        "buttons": await self.button_manager(TableState.STOP_BETS)}
            await self.app.store.vk_api.send_message(
                    Message(
                        user_id=1,
                        text=text,
                        peer_id = update.object.peer_id
                    ),
                    keyboard=keyboard)
        else:
            await self.app.store.vk_api.send_message(
                    Message(
                        user_id=1,
                        text="Не все игроки сделали ставки!",
                        peer_id = update.object.peer_id
                    ),)


    async def handle_start_bets(self, update: Update, current_table: Table, keyboard):
        # Переводим стол в фазу ставок
        await self.app.store.blackjack.set_table_state(current_table.id, TableState.START_BETS.str)
        
        players = await self.app.store.blackjack.get_players_on_table(current_table.id)
        # переводим игроков в фазу ставок
        for i, player in enumerate(players):
            if player.vk_id != 1:
                await self.app.store.blackjack.set_player_state(player.vk_id,player.table_id, PlayerState.WAITING_TURN.str)
        
        # определяем игрока, который будет ходить первым
        player = await self.app.store.blackjack.get_next_waiting_player(current_table.id)
        await self.app.store.blackjack.set_player_state(player.vk_id,player.table_id, PlayerState.TURN_ACTIVE.str)

        user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
        text = f"Размещайте ставки!\nВеличина ставки в размере от твоего банка!\nХод игрока @id{user.vk_id} ({user.username}) !"
        await self.app.store.vk_api.send_message(
                Message(
                    user_id=1,
                    text=text,
                    peer_id = update.object.peer_id
                ),
                keyboard=keyboard)

