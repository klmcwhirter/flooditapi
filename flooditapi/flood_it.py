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
import logging
import random
import sys

from docopt import docopt

# ------------------------------
# Variables
# ------------------------------

COLOR_CHOICES = ['black', 'darkgray', 'gray', 'white', 'red',
                 'orange', 'yellow', 'tan', 'green', 'cyan',
                 'lightblue', 'blue', 'violet', 'purple']
BOARD_SIZE = 14
MOVES_LIMIT = 26


def config_logging(verbose=False, use_stdout=False):
    ''' Configure logging based on command line params '''
    logging.basicConfig(stream=sys.stdout if use_stdout else sys.stderr,
                        format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO if not verbose else logging.DEBUG)


def randomize_colors(color_choices):
    random.shuffle(color_choices)
    return color_choices[:6]


class FloodItStrategy(object):
    def __init__(self, move=0, board=None, colors=None, board_size=BOARD_SIZE, color_choices=COLOR_CHOICES):
        self.move = move

        self.board_size = board_size
        self.color_choices = color_choices
        self.win_text = f'{MOVES_LIMIT - self.move} moves left ...'

        logging.debug(f'FloodItStrategy.__init__: colors={colors}, board={board}')
        if board:
            self.board = board
            self.colors = colors
        else:
            logging.debug('FloodItStrategy.__init__: board not provided - resetting game ...')
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
        logging.debug(f'FloodItStrategy.from_json: state={state}, type={type(state)}')
        if '__type__' in state and state['__type__'] == 'state':
            logging.debug('FloodItStrategy.from_json: loading state via init ...')
            strategy = FloodItStrategy(state['move'],
                                       state['board'],
                                       state['colors'],
                                       state['board_size'],
                                       state['color_choices'])
            logging.debug(f'FloodItStrategy.from_json: strategy={type(strategy)}')
        else:
            logging.debug('FloodItStrategy.from_json: clearing game')
            strategy = FloodItStrategy()

        return strategy


class FloodItRequest(object):
    def __init__(self, color, state):
        self.color = color
        self.state = state

    def __str__(self):
        return f'{{ "__type__": "req", "color": {self.color}, "state": {self.state} }}'


def request_object_handler(dct):
    logging.debug(f'request_object_handler: dct={dct}')

    if '__type__' in dct and dct['__type__'] == 'req':
        request = FloodItRequest(dct['color'], FloodItStrategy.from_json(dct['state']))
        logging.debug(f'request_object_handler: hook returning request ... state={type(request.state)}')
        return request

    logging.debug('request_object_handler: hook returning')

    return dct


def handle_request(json_req):
    py_req = ''
    if json_req and len(json_req) > 0:
        py_req = json.loads(json_req, object_hook=request_object_handler)

    logging.debug(f'handle_request: py_req={py_req}')

    if py_req and hasattr(py_req, 'color') and hasattr(py_req, 'state'):
        # continue game
        strategy = py_req.state
        flood_color = strategy.colors[py_req.color]
        strategy.select_color(flood_color)
        py_req.state = strategy
        print(py_req)
    else:
        # start a new game
        strategy = FloodItStrategy()
        print(FloodItRequest(0, strategy))


if __name__ == "__main__":
    opts = docopt(__doc__, version='0.1')
    # print(opts)
    config_logging(opts['-v'])

    json_req = ''
    with open(opts['-f'], 'r', encoding='utf-8') as req:
        json_req = req.read()

    handle_request(json_req)
