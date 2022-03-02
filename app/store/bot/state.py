import typing
from enum import Enum, EnumMeta


class TableEnumMeta(EnumMeta):
    def __call__(cls, value, *args, **kw):
        if isinstance(value, str):
            # map strings to enum values, defaults to Unknown
            value = {'/waiting_reg': {
                        'str': "/waiting_reg",
                        'next_state': ['/start_reg'],}, 
                     '/start_reg': {
                        'str': "/start_reg",
                        'next_state': ['/stop_reg'],},
                     '/stop_reg': {
                        'str': "/stop_reg",
                        'next_state': ['/start_game'],},
                     '/start_game': {
                        'str': '/start_game',
                        'next_state': ['/end_game'],},
                     '/end_game': {
                        'str': '/end_game',
                        'next_state': [],}}.get(value, 0)
        return super().__call__(value, *args, **kw)
    
class TableState(Enum, metaclass=TableEnumMeta):

    WAITING_REG = {
        'str': "/waiting_reg",
        'next_state': ['/start_reg'],
    }

    START_REG = {
        'str': "/start_reg",
        'next_state': ['/stop_reg'],
    }
    STOP_REG = {
        'str': "/stop_reg",
        'next_state': ['/start_game'],
    }
    START_GAME = {
        'str': '/start_game',
        'next_state': ['/end_game'],
    }
    END_GAME = {
        'str': '/end_game',
        'next_state': [],
    }

    def __init__(self, vals):
        self.str = vals['str']
        self.next_state = vals['next_state']
    

    def can_transition(self, new_state):
        return new_state.str in self.next_state


# how to use
#print('Name:', BugStatus.START_REG)
#print('Value:', BugStatus.START_REG.value)
#print('Str:', BugStatus.START_REG.str)
#print('Custom attribute:', BugStatus.START_REG.next_state)
#print('Using attribute:',
#      BugStatus.START_REG.can_transition(BugStatus.STOP_REG))
