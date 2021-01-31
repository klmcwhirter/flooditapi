'''
flood_it - play a game of flood it

Usage:
    flood_it [-v] [-f <file>]

Options:
    -f <file>   optional request file [default: data/flood_it_req.json]
    -h, --help  Print this help text
    -v          Set verbose mode
    --version   Print the version and exit
'''

import json
import random

from docopt import docopt

# ------------------------------
# Variables
# ------------------------------

COLOR_CHOICES = ['black', 'darkgray', 'gray', 'white', 'red',
                 'orange', 'yellow', 'tan', 'green', 'cyan',
                 'lightblue', 'blue', 'violet', 'purple']
BOARD_SIZE = 14
MOVES_LIMIT = 26


def randomize_colors(color_choices):
    random.shuffle(color_choices)
    return color_choices[:6]


messages = []


def log(message):
    messages.append(message)


def null_logger(message):
    pass


def set_null_logger():
    global log
    log = null_logger


class FloodItStrategy(object):
    def __init__(self, move=0, board=None, colors=None, board_size=BOARD_SIZE, color_choices=COLOR_CHOICES):
        self.move = move

        self.board_size = board_size
        self.color_choices = color_choices
        self.win_text = f'{MOVES_LIMIT - self.move} moves left ...'

        log(f'FloodItStrategy.__init__: colors={colors}')

        if board:
            self.board = board
            self.colors = colors
        else:
            log('FloodItStrategy.__init__: board not provided - resetting game ...')

            self.board = [[None for x in range(board_size)]
                          for y in range(board_size)]
            self.colors = randomize_colors(self.color_choices)
            self.fill_board()

    def __str__(self):
        import json
        return f'{{ "__type__": "state", "move": {self.move}, "win_text": "{self.win_text}", ' + \
            f'"board_size": {self.board_size}, "board": {json.dumps(self.board)}, ' + \
            f'"colors": {json.dumps(self.colors)}, "color_choices": {json.dumps(self.color_choices)} }}'

    def all_squares_are_the_same(self):
        ''' Check whether all squares are the same
            Note this just compares all rows for equality
        '''
        squares = self.board
        return all(colour == squares[0] for colour in squares)

    def fill_board(self):
        for x in range(self.board_size):
            for y in range(self.board_size):
                self.board[x][y] = random.choice(self.colors)

    def flood(self, x, y, target, replacement):
        ''' Recursively floods adjacent squares '''
        # Algorithm from https://en.wikipedia.org/wiki/Flood_fill
        if target == replacement:
            return False
        if self.board[x][y] != target:
            return False
        self.board[x][y] = replacement
        if y+1 <= self.board_size-1:   # South
            self.flood(x, y+1, target, replacement)
        if y-1 >= 0:                    # North
            self.flood(x, y-1, target, replacement)
        if x+1 <= self.board_size-1:    # East
            self.flood(x+1, y, target, replacement)
        if x-1 >= 0:                    # West
            self.flood(x-1, y, target, replacement)

    def select_color(self, flood_color):
        target = self.board[0][0]
        if flood_color != target:
            # don't count double-click as a turn
            self.flood(0, 0, target, flood_color)
            self.win_check()

    def win_check(self):
        self.move += 1
        if self.move <= MOVES_LIMIT:
            if self.all_squares_are_the_same():
                self.win_text = "You win!"
            else:
                self.win_text = f'{MOVES_LIMIT - self.move} moves left ...'
        else:
            self.win_text = f'You lost :( {self.win_text}'

    @staticmethod
    def from_json(state):
        ''' Convert json to FloodItStrategy instance '''
        log(f'FloodItStrategy.from_json: state={state}, type={type(state)}')

        if state and '__type__' in state and state['__type__'] == 'state':
            log('FloodItStrategy.from_json: loading state via init ...')

            log(f'FloodItStrategy.from_json: type(state["board"])={type(state["board"])}')

            strategy = FloodItStrategy(state['move'],
                                       state['board'],
                                       state['colors'],
                                       state['board_size'],
                                       state['color_choices'])
            log(f'FloodItStrategy.from_json: strategy={type(strategy)}')
        else:
            log('FloodItStrategy.from_json: clearing game')
            strategy = FloodItStrategy()

        return strategy


class FloodItRequest(object):
    def __init__(self, __type__, color, state, verbose=False):
        self.__type__ = __type__
        self.color = color
        self.state = state
        self.verbose = verbose
        self.messages = []

    def __str__(self):
        return f'{{ "__type__": "{self.__type__}", "messages": {self.messages}, "color": {self.color}, ' + \
            f'"state": {self.state}, "verbose": {json.dumps(self.verbose)} }}'


def request_object_handler(dct):
    log('in request_object_handler')

    if '__type__' in dct and dct['__type__'] == 'color':
        request = FloodItRequest('color',
                                 dct.get('color', 0),
                                 FloodItStrategy.from_json(dct.get('state')),
                                 dct.get('verbose'))

        log(f'request_object_handler: hook returning request ... state={type(request.state)}')

        return request

    if '__type__' in dct and dct['__type__'] == 'reset':
        request = FloodItRequest('reset', 0, FloodItStrategy(), dct.get('verbose', False))

        log('request_object_handler: hook returning reset')

        return request

    log('request_object_handler: hook returning')

    return dct


def handle_request(json_req):
    py_req = {}
    if json_req and len(json_req) > 0:
        py_req = json.loads(json_req, object_hook=request_object_handler)

    verbose = False
    if py_req is FloodItRequest:
        verbose = py_req.verbose

    if not verbose:
        set_null_logger()

    log(f'handle_request: py_req={py_req}')

    if py_req and hasattr(py_req, '__type__') and py_req.__type__ == 'color':
        # continue game
        flood_color = py_req.state.colors[py_req.color]
        py_req.state.select_color(flood_color)

    if verbose:
        py_req.messages = json.dumps(messages)

    print(py_req)


if __name__ == "__main__":
    opts = docopt(__doc__, version='0.1')
    # print(opts)

    json_req = ''
    with open(opts['-f'], 'r', encoding='utf-8') as req:
        json_req = req.read()

    handle_request(json_req)
