class BoardError(Exception):
    def __init__(self, msg):
        # pylint: disable=useless-super-delegation
        super().__init__(msg)

class Board:
    def __init__(self):
        self.connected = False
        self.serial = None

    def connect(self):
        """(re)connect to board and enter raw repl
        """
        if self.connected:
            return
        
        # pylint : disable=too-many-function-args
        device = self._find_board()

    def _find_board(self):
        """Return the FBQN of the connected Arduino boards"""