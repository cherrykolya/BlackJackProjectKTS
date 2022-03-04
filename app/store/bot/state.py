import typing
from enum import Enum, EnumMeta

# СОСТОЯНИЯ СТОЛА
class TableEnumMeta(EnumMeta):
    def __call__(cls, value, *args, **kw):
        if isinstance(value, str):
            # map strings to enum values, defaults to Unknown
            value = {'/info': {
                        'str': "/info",
                        'next_state': [], },
                     '/waiting_reg': {
                        'str': "/waiting_reg",
                        'next_state': ['/start_reg', '/info'],}, 
                     '/start_reg': {
                        'str': "/start_reg",
                        'next_state': ['/stop_reg', '/info', '/end_game'],},
                     '/stop_reg': {
                        'str': "/stop_reg",
                        'next_state': ['/start_bets', '/info', '/end_game'],},
                     '/start_bets': {
                        'str': "/start_bets",
                        'next_state': ['/stop_bets', '/info', '/end_game'],},
                     '/stop_bets': {
                        'str': "/stop_bets",
                        'next_state': ['/start_game', '/info', '/end_game'],},
                     '/start_game': {
                        'str': '/start_game',
                        'next_state': ['/end_game', '/info', '/end_game'],},
                     '/end_game': {
                        'str': '/end_game',
                        'next_state': [],}}.get(value, 0)
        return super().__call__(value, *args, **kw)
    
class TableState(Enum, metaclass=TableEnumMeta):

    WAITING_REG = {
        'str': "/waiting_reg",
        'next_state': ['/start_reg', '/info'],
    }
    START_REG = {
        'str': "/start_reg",
        'next_state': ['/stop_reg', '/info', '/end_game'],
    }
    STOP_REG = {
        'str': "/stop_reg",
        'next_state': ['/start_bets', '/info', '/end_game'],
    }
    START_BETS = {
        'str': "/start_bets",
        'next_state': ['/stop_bets', '/info', '/end_game'],
    }
    STOP_BETS = {
        'str': "/stop_bets",
        'next_state': ['/start_game', '/info', '/end_game'],
    }
    START_GAME = {
        'str': '/start_game',
        'next_state': ['/end_game', '/info', '/end_game'],
    }
    
    # UTILS STATES
    END_GAME = {
        'str': '/end_game',
        'next_state': [],
    }
    INFO = {
        'str': '/info',
        'next_state': [],
    }

    def __init__(self, vals):
        self.str = vals['str']
        self.next_state = vals['next_state']
    
    def can_transition(self, new_state):
        return new_state.str in self.next_state

# СОСТОЯНИЯ ИГРОКА

class PlayerEnumMeta(EnumMeta):
    def __call__(cls, value, *args, **kw):
        if isinstance(value, str):
            # map strings to enum values, defaults to Unknown
            value = {
                     '/waiting_turn': {
                        'str': "/waiting_turn",
                        'next_state': ['/turn_active'],},
                     '/turn_active': {
                        'str': '/turn_active',
                        'next_state': ['/turn_ended'],},
                     '/turn_ended': {
                        'str': '/turn_ended',
                        'next_state': [],}}.get(value, 0)
        return super().__call__(value, *args, **kw)
    
class PlayerState(Enum, metaclass=PlayerEnumMeta):

    WAITING_TURN = {
        'str': "/waiting_turn",
        'next_state': ['/turn_active'],
    }
    TURN_ACTIVE = {
        'str': '/turn_active',
        'next_state': ['/turn_ended'],
    }
    TURN_ENDED = {
        'str': '/turn_ended',
        'next_state': [],
    }

    def __init__(self, vals):
        self.str = vals['str']
        self.next_state = vals['next_state']
    

    def can_transition(self, new_state):
        return new_state.str in self.next_state

# КНОПКИ
class Buttons(Enum):

    # TEXT BUTTONS
    START_REG = {"color": "positive",
            "action":{  
            "type":"text",
            "payload":{"button":"/start_reg"},
            "label":"Начать регистрацию"}
            }

    STOP_REG = {"color": "negative",
            "action":{  
            "type":"text",
            "payload":{"button":"/stop_reg"},
            "label":"Закончить регистрацию"}
            }
    
    START_BETS = {"color": "positive",
            "action":{  
            "type":"text",
            "payload":{"button":"/start_bets"},
            "label":"Сделать ставки"}
            }
    
    STOP_BETS = {"color": "positive",
            "action":{  
            "type":"text",
            "payload":{"button":"/stop_bets"},
            "label":"/stop_bets"}
            }

    START_GAME = {"color": "positive",
            "action":{  
            "type":"text",
            "payload":{"button":"/start_game"},
            "label":"Раздать карты"}
            }

    END_GAME = {"color": "secondary",
            "action":{  
            "type":"text",
            "payload":{"button":"/end_game"},
            "label":"Прервать игру"}
            }

    INFO = {"color": "secondary",
            "action":{  
            "type":"text",
            "payload":{"button":"/info"},
            "label":"Моя статистика"}
            }

    # CALLBACK BUTTONS
    REG_USER = {"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"reg"},
            "label":"Сесть за стол"}
                }

    ADD_CARD ={"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"add_card"},
            "label":"Добрать карту"}
                }

    END_TURN ={"color": "negative",
            "action":{  
            "type":"callback",
            "payload":{"button":"end_turn"},
            "label":"Завершить ход"}
                }
    
    BET_1 = {"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"bet",
                       "bet": 0.25},
            "label":"25%"}}

    BET_2 = {"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"bet",
                       "bet": 0.5},
            "label":"50%"}}
            
    BET_3 = {"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"bet",
                       "bet": 0.75},
            "label":"75%"}}
        
    BET_4 = {"color": "positive",
            "action":{  
            "type":"callback",
            "payload":{"button":"bet",
                       "bet": 1},
            "label":"100%"}}

# how to use
#print('Name:', BugStatus.START_REG)
#print('Value:', BugStatus.START_REG.value)
#print('Str:', BugStatus.START_REG.str)
#print('Custom attribute:', BugStatus.START_REG.next_state)
#print('Using attribute:',
#      BugStatus.START_REG.can_transition(BugStatus.STOP_REG))
