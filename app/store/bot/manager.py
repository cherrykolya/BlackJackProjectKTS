import typing
import json

from logging import getLogger
from datetime import datetime
from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.blackjack.models import User, Player, Table
from app.store.bot.state import TableState, PlayerState, Buttons, CallbackButtons
from app.store.bot.deck import Deck

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]):
        # TODO: декоратор для проверки нажатия кнопок игроком, не участвующим в матче
        # TODO: вставить в декоратор обработку снэкбара
        # TODO: Вынести логику из handle_updates
        # TODO: Посмотреть на функции больше чем 20 строк, вынести из них логику
        # TODO: Пересмотреть логику в dataclasses.py
        # TODO: добавить таймер
        for update in updates:
            current_table = await self.app.store.blackjack.get_table_by_peer_id(update.peer_id)
            if current_table is None:
                current_table = await self.create_table(update.peer_id)
            
            # обработка нажатия на callback кнопку
            if update.type == 'message_event':
                await self.process_callback_button_pressed(update, current_table)
                
            # обработка команды из чата
            if update.type == 'message_new':
                await self.process_new_command(update, current_table)


    async def button_response_handler(self, response_button: CallbackButtons):
        button_handler = { CallbackButtons.REG: self.handle_registration,
                           CallbackButtons.ADD_CARD: self.draw_card, 
                           CallbackButtons.END_TURN: self.end_turn,
                           CallbackButtons.PLACE_BET: self.register_bets} 
        return button_handler[response_button]


    
    async def button_sender(self, table_state: TableState):
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

    async def process_new_command(self, update: Update, current_table: Table):
        command = update.text
        
        if update.payload:
            command = json.loads(update.payload)["button"]

        if await self.check_state(command, TableState(current_table.state)):
            keyboard = await self.keyboard_constructor(command)
            update_handler = await self.context_manager(TableState(command))
            await update_handler(update=update, 
                                 current_table=current_table, 
                                 keyboard=keyboard)

        # TODO: обработка неправильной команды от пользователя
        elif len(command) > 0 and command[0] == "/":
            text = f"Доступны следующие команды:\n"
            for i, state in  enumerate(TableState(current_table.state).next_state):
                text += f"{i+1}. {state}\n"
            await self.send_message(update, text)


    async def process_callback_button_pressed(self, update: Update, current_table: Table):
        if update.payload: 
            command = update.payload["button"]
        update_handler = await self.button_response_handler(CallbackButtons(command))
        await update_handler(update=update, current_table=current_table)


    async def create_table(self, peer_id: int) -> Table:
        deck = Deck()
        deck.generate_deck()
        deck.shuffle_deck()
        deck = [card.to_dict() for card in deck.deck]
        table = Table(0,peer_id, datetime.now(), deck, TableState.WAITING_REG.str)
        await self.app.store.blackjack.create_table(table)
        return await self.app.store.blackjack.get_table_by_peer_id(peer_id)
        

    def player_checker(func):
        async def wrapper(self, *args, **kwargs):
            update, current_table = kwargs['update'], kwargs['current_table']
            current_player = await self.app.store.blackjack.get_player_by_id(update.user_id,current_table.id)
            if current_player is not None:
                await func(self, *args, **kwargs)
            elif update.type == 'message_event':
                text = "Вы не в игре!"
                event_data, params = await self.snackbar_params_constructor(update, text)
                await self.app.store.vk_api.send_snackbar(params, event_data)
        return wrapper

    async def check_state(self, command: str, table_state: TableState) -> bool:
        return command in table_state.next_state

    async def handle_info(self, update: Update, current_table: Table, keyboard):
        user = await self.app.store.blackjack.get_user_by_id(update.user_id)
        text = f"Статистика пользователя @id{user.vk_id} ({user.username})\n"
        text += f"Победы: {user.num_of_wins} 🏆\n"
        text += f"Банк: {user.cash} 💵\n"

        await self.send_message(update, text)


    @player_checker
    async def handle_end_game(self, update: Update, current_table: Table, keyboard):
        # Изменяем состояние игрового стола
        await self.app.store.blackjack.set_table_state(current_table.id, TableState.END_GAME.str)
        user = await self.app.store.blackjack.get_user_by_id(update.user_id)
        text = f"Игрок @id{user.vk_id} ({user.username}) досрочно завершил матч!\n"

        # высылаем уведомление об окончании игры
        await self.send_message(update, text, keyboard)


    async def handle_registration(self, update: Update, current_table: Table):
        vk_id = update.user_id
        # Проверяем зарегистрировался ли уже игрок
        if await self.app.store.blackjack.get_player_by_id(vk_id, current_table.id) is None:
            username = await self.app.store.vk_api.get_username(update.user_id)
            await self.app.store.blackjack.create_user(User(vk_id, username, str({}), 1000, 0))
            await self.app.store.blackjack.create_player(Player(vk_id, current_table.id, [], PlayerState.WAITING_TURN.str, 0))
            
            # высылаем снэкбар и сообщение о регистрации
            text = "Вы зарегистрировались!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)
            text=f"@id{vk_id} ({username}) садится за стол!\n"
            await self.send_message(update, text)
        else:
            # высылаем снэкбар и сообщение о регистрации
            text = "Вы уже зарегистрировались!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)

    @player_checker
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
            cards = []
            
            # обрабатываем случай диллера
            if player.vk_id == 1:
                for i in range(1):
                    card = deck.pop()
                    cards.append(card)
                    text += f"📜 {card}\n"
            else:    
                for i in range(2):
                    card = deck.pop()
                    cards.append(card)
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

        await self.send_message(update, text, keyboard)


    @player_checker
    async def handle_stop_reg(self, update: Update, current_table: Table, keyboard):
        # TODO: обработать кейс когда никто не зарегистрировался
        players = await self.app.store.blackjack.get_players_on_table(current_table.id)
        if len(players) == 0:
            text = "Никто не зарегистрировался, регистрация продолжается!\n"
            await self.send_message(update, text)

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
            
            await self.send_message(update, text, keyboard)

    async def handle_start_reg(self, update: Update, current_table: Table, keyboard):
        # создаем игровой стол и определяем в нем колоду-стек
        #deck = Deck()
        await self.app.store.blackjack.set_table_state(id=current_table.id, state=TableState.START_REG.str)
        text = "Сыграем в BlackJack?"
        await self.send_message(update, text, keyboard)

    @player_checker
    async def end_turn(self, update: Update, current_table: Table):
        # получаем текущего игрока
        vk_id = update.user_id
        peer_id = current_table.id
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)

        if player.state == PlayerState.TURN_ACTIVE.str:
            # завершаем ход игрока
            await self.app.store.blackjack.set_player_state(vk_id, peer_id, PlayerState.TURN_ENDED.str)
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            cards = player.cards
            text = f"Игрок @id{vk_id} ({user.username}) заврешил ход с картами:\n"

            for card in cards:
                    text += f"📜 {card}\n"

            # определяем игрока, который будет ходить cледующим
            next_player = await self.app.store.blackjack.get_next_waiting_player(current_table.id)
            if next_player is not None:
                await self.app.store.blackjack.set_player_state(next_player.vk_id,next_player.table_id, PlayerState.TURN_ACTIVE.str)
                next_user = await self.app.store.blackjack.get_user_by_id(next_player.vk_id)
                text += f"Ход игрока @id{next_user.vk_id} ({next_user.username}) !"

            await self.send_message(update, text)

            # Высылаем snackbar о конце ход
            text = "Ваш ход окончен!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)

            # TODO: если все игроки в состоянии 2, перевести стол к состоянию 3 и подвести итоги
            players = await self.app.store.blackjack.get_players_on_table(peer_id)
            if await self.check_all_players_state(players, PlayerState.TURN_ENDED):
                await self.summarize(update, current_table)

        elif player.state == PlayerState.WAITING_TURN.str:
            # Высылаем snackbar о том что сейчас не ваш ход
            text = f"Сейчас не ваш ход!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)

        # обрабатываем случаи когда игрок уже закончил ход
        elif player.state == PlayerState.TURN_ENDED.str:
            # Высылаем snackbar о том что игрок закончил ход
            text = "Ваш ход окончен. Дождитесь конца хода других игроков."
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)
        
    @player_checker
    async def draw_card(self, update: Update, current_table: Table):
        vk_id = update.user_id
        peer_id = current_table.id

        # Получаем текущую колоду-стек
        deck = current_table.deck

        # Проверяем состояние игрока
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)
        if player.state == PlayerState.TURN_ACTIVE.str or vk_id == 1:
            # добиарем карту
            user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
            text = f"Игрок @id{vk_id} ({user.username}) добрал карту:\n"
            cards = player.cards
            # удаляем карту из стек-колоды
            card = deck.pop()
            text += f"📜 {card}\n"
            cards.append(card)

            # обновляем колоду игркоа и стола в БД
            await self.app.store.blackjack.set_player_cards(vk_id, peer_id, cards)
            await self.app.store.blackjack.set_table_cards(peer_id, deck)
            
            await self.send_message(update, text)
            
            # Высылаем snackbar о доборе карты
            if vk_id != 1:
                text = "Вы добрали карту"
                event_data, params = await self.snackbar_params_constructor(update, text)
                await self.app.store.vk_api.send_snackbar(params, event_data)
            # Если сумма карт больше 21, перевести игрока в состояние 2
            card_values = [card.value for card in cards]
            if sum(card_values) > 20:
                await self.end_turn(update=update, current_table=current_table)
        
        elif player.state == PlayerState.WAITING_TURN.str:
            # Высылаем snackbar о том что сейчас не ваш ход
            text = f"Сейчас не ваш ход!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)

        elif player.state == PlayerState.TURN_ENDED.str:
            # Высылаем snackbar о том что игрок закончил ход
            text = "Ваш ход окончен. Дождитесь конца хода других игроков."
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)


    async def summarize(self, update: Update, current_table: Table):
        peer_id = current_table.id
        diler = await self.app.store.blackjack.get_player_by_id(1, peer_id)
        
        # КОСТЫЛЬ
        diler_update = Update('',UpdateObject(0, Message(1, peer_id, '', None, None)))
        
        while sum([card.value for card in diler.cards]) < 14:
            await self.draw_card(update=diler_update, current_table=current_table)
            diler = await self.app.store.blackjack.get_player_by_id(1, peer_id)
        
        # высылаем сообщение о конце хода диллера
        cards = diler.cards
        diler_user = await self.app.store.blackjack.get_user_by_id(1)
        text = f"Игрок @id{diler.vk_id} ({diler_user.username}) заврешил ход с картами:\n"

        for card in cards:
                text += f"📜 {card}\n"
                
        await self.send_message(update, text)

    
        # Подводим итоги матча
        diler_sum = sum([card.value for card in diler.cards])
        players = await self.app.store.blackjack.get_players_on_table(peer_id)
        text = f"Все игроки завершили ход, результаты:\n"
        for i, player in enumerate(players):
            if player.vk_id != 1:
                user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
                user_sum = sum([card.value for card in player.cards])
                
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
        
        keyboard = await self.keyboard_constructor(TableState.END_GAME.str)
        await self.send_message(update, text, keyboard)


    async def check_all_players_state(self, players : list[Player], state: PlayerState) -> bool:
        flag = True
        for player in players:
            if player.state != state.str and player.vk_id != 1:
                flag = False
        return flag

    @player_checker
    async def register_bets(self, update: Update, current_table: Table, keyboard=None):
        # получаем текущего игрока
        vk_id = update.user_id
        peer_id = current_table.id
        player = await self.app.store.blackjack.get_player_by_id(vk_id, peer_id)

        # Проверяем состояние игркоа
        if player.state == PlayerState.TURN_ACTIVE.str:
            user = await self.app.store.blackjack.get_user_by_id(vk_id)
            val = update.payload['bet']
            bet = user.cash*val 
            
            # переводим игрока в некст состояние и заполняем его ставку
            await self.app.store.blackjack.set_player_state(vk_id, peer_id, PlayerState.TURN_ENDED.str)
            await self.app.store.blackjack.set_player_bet(vk_id, peer_id, bet)
            
            # Высылаем snackbar с размером ставки
            text = f"Размер вашей ставки {bet} 💵!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)
            
            text = f"@id{player.vk_id} ({user.username}) делает ставку {bet} 💵!\n"
            text += "\n"

            # определяем игрока, который будет ходить cледующим
            next_player = await self.app.store.blackjack.get_next_waiting_player(current_table.id)
            if next_player is not None:
                await self.app.store.blackjack.set_player_state(next_player.vk_id,next_player.table_id, PlayerState.TURN_ACTIVE.str)
                next_user = await self.app.store.blackjack.get_user_by_id(next_player.vk_id)
                text += f"Ход игрока @id{next_user.vk_id} ({next_user.username}) !"

            # Высылаем сообщение о ставке в чат
            await self.send_message(update, text)

            if next_player is None:
                # TODO: перевести стол в фазу конца ставок
                await self.handle_stop_bets(update, current_table)


        elif player.state == PlayerState.WAITING_TURN.str:
            # Высылаем snackbar о том что сейчас не ваш ход
            text = f"Сейчас не ваш ход!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)

        elif player.state == PlayerState.TURN_ENDED.str:
            # Высылаем snackbar о том что игрок уже поставил
            text = f"Вы уже сделали ставку {player.bet} 💵!"
            event_data, params = await self.snackbar_params_constructor(update, text)
            await self.app.store.vk_api.send_snackbar(params, event_data)


    async def handle_stop_bets(self, update: Update, current_table: Table):
        # проверить все ли сделали ставки
        players = await self.app.store.blackjack.get_players_on_table(current_table.id)
        if await self.check_all_players_state(players, PlayerState.TURN_ENDED):
            # перевести стол в сосотояние конец ставок
            await self.app.store.blackjack.set_table_state(current_table.id, TableState.STOP_BETS.str)
            text = "Фаза ставок окончена!\nИгроки сделали следующие ставки:\n"
            for i, player in enumerate(players):
                if player.vk_id != 1:
                    user = await self.app.store.blackjack.get_user_by_id(player.vk_id)
                    text += f"{i+1}. @id{player.vk_id} ({user.username}) - {player.bet} 💵!\n"
                    
            keyboard = await self.keyboard_constructor(TableState.STOP_BETS.str)
            await self.send_message(update, text, keyboard)

        else:
            text="Не все игроки сделали ставки!"
            await self.send_message(update, text)


    async def keyboard_constructor(self, command: str) -> dict:
        return {"one_time": False,
                "inline": False, 
                "buttons": await self.button_sender(TableState(command))}

    async def snackbar_params_constructor(self, update: Update, text: str) -> tuple[dict, dict]:
        event_data = {"type": "show_snackbar",
                        "text": text}
        params = {"event_id": update.object.body.event_id, "user_id":update.user_id,
                    "peer_id": update.peer_id}
        return event_data, params

    @player_checker
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
        await self.send_message(update, text, keyboard)

    async def send_message(self, update: Update, text: str, keyboard=None):
        await self.app.store.vk_api.send_message(
                Message(
                    user_id=1,
                    text=text,
                    peer_id = update.peer_id,
                    payload=None,
                    event_id=None
                ),
                keyboard=keyboard)








