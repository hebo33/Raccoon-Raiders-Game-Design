from __future__ import annotations
from random import shuffle


# Each raccoon moves every this many turns
RACCOON_TURN_FREQUENCY = 20

# Directions dx, dy
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [LEFT, UP, RIGHT, DOWN]


def get_shuffled_directions() -> list[tuple[int, int]]:
    """Helper that returns a shuffled copy of DIRECTIONS.
    """
    to_return = DIRECTIONS[:]
    shuffle(to_return)
    return to_return

def neighbours(x: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Return the four coordinates adjacent to x.

    Note: this function does NOT do any checking for whether the
          four adjacent coordinates are actually on a board or not though,
          so the client of this function would need to confirm that for
          themselves.

    This function is helpful when implementing GameBoard.adjacent_bin_score.

    >>> ns = set(neighbours((2, 3)))
    >>> {(2, 2), (2, 4), (1, 3), (3, 3)} == ns
    True
    """
    rslt = []
    for direction in DIRECTIONS:
        rslt.append((x[0] + direction[0], x[1] + direction[1]))
    return rslt


@check_contracts
class GameBoard:
    """A game board on which the game is played.

    Public Attributes:
    - ended: whether this game has ended or not
    - turns: how many turns have passed in the game
    - width: how many squares wide this board is
    - height: how many squares high this board is

    Private Attributes:
    - _player: the player of the game
    - _chars: a list which stores all characters on the game board
    - _num_total_chars: number of total characters on the game board

    Representation Invariants:
    - self.turns >= 0
    - self.width > 0
    - self.height > 0
    - self.ended is True if and only if the game has ended
    - No tile in the game contains more than 1 character, except that a tile
      may contain both a Raccoon and an open GarbageCan.
    - At most one Player can be on the board; self._player is None if there is
      no Player on the board.

    Sample Usage:
    See examples in individual method docstrings.
    """
    ended: bool
    turns: int
    width: int
    height: int
    _player: Player | None
    _chars: list[Character]
    _num_total_chars: int

    def __init__(self, w: int, h: int) -> None:
        """Initialize this Board to be of the given width <w> and height <h> in
        squares. A board is initially empty (no characters) and no turns have
        been taken.

        >>> b = GameBoard(3, 3)
        >>> b.width == 3
        True
        >>> b.height == 3
        True
        >>> b.turns == 0
        True
        >>> b.ended
        False
        """
        self.ended = False
        self.turns = 0
        self.width = w
        self.height = h
        self._player = None

        # start initializing private attributes
        self._chars = []
        self._num_total_chars = 0

    def place_character(self, c: Character) -> None:
        """Record that character <c> is on this board.

        Note: This method should only be called from Character.__init__.

        IMPORTANT:
        The decisions made about new private attributes for class GameBoard
        will determine what you do here.

        Preconditions:
        - c.board == self
        - self.on_board(c.x, c.y)
        - If <c> is a Player, then there must not be any other players on this
            board yet.
        - Character <c> has not already been placed on this board.
        - The tile (c.x, c.y) does not already contain a character, with the
            exception being that a raccoon can be placed on the same tile where
            an unlocked GarbageCan is already present.

        Note: The testing will depend on this method to set up the board,
        as the Character.__init__ method calls this method.

        >>> b = GameBoard(3, 2)
        >>> r = Raccoon(b, 1, 1)  # when a Raccoon is created, it is placed on b
        >>> b.at(1, 1)[0] == r  # requires GameBoard.at be implemented to work
        True
        """
        self._num_total_chars += 1
        self._chars.append(c)
        if isinstance(c, Player):
            self._player = c

    def at(self, x: int, y: int) -> list[Character]:
        """Return the characters at tile (x, y).

        If there are no characters or if the (x, y) coordinates are not
        on the board, return an empty list.

        Note: There may be as many as two characters at one tile,
        since a raccoon can climb into a garbage can.

        Note: The testing will depend on this method to allow us to
        access the Characters on your board, since we don't know how
        you have chosen to store them in your private attributes,
        so make sure this method is working properly!

        >>> b = GameBoard(3, 2)
        >>> r = Raccoon(b, 1, 1)
        >>> b.at(1, 1)[0] == r
        True
        >>> p = Player(b, 0, 1)
        >>> b.at(0, 1)[0] == p
        True
        """
        lst = []
        # check if the coordinate is out of boundary
        if not self.on_board(x, y):
            return lst
        # coordinate is in the boundary
        else:
            for char in self._chars:
                if char.x == x and char.y == y:
                    lst.append(char)
        return lst

    def _add_char(self, blank: dict[tuple[int, int], list]) -> None:
        """
        Mutate <blank> by adding the Characters in the tile of the key.

        >>> b = GameBoard(2, 2)
        >>> p = Player(b, 0, 0)
        >>> r = Raccoon(b, 1, 1)
        >>> the_dict = {(0, 0): [], (1, 0): [], (0, 1): [], (1, 1): []}
        >>> b._add_char(the_dict)
        >>> the_dict[(0, 0)] == b.at(0, 0)
        True
        """
        for key in blank:
            blank[key].extend(self.at(key[0], key[1]))

    def _to_grid_helper(
            self,
            blank: list[list[str]],
            storage: dict[tuple[int, int], list]) -> list[list[str]]:
        """Return a list of lists of integers based on <blank>, the strings
        in the sublist are determined by storage, with the instructions
        provided in the to_grid docstring.

        >>> b = GameBoard(2, 2)
        >>> p = Player(b, 0, 0)
        >>> r = Raccoon(b, 1, 1)
        >>> the_dict = {(0, 0): [], (1, 0): [],
        ... (0, 1): [], (1, 1): []}
        >>> b._add_char(the_dict)
        >>> empty = [['-', '-'], ['-', '-']]
        >>> b._to_grid_helper(empty, the_dict)
        [['P', '-'], ['-', 'R']]
        """
        the_copy = blank
        garb_tiles = {}
        for key in storage:
            if len(storage[key]) == 2:
                the_copy[key[1]][key[0]] = '@'  # raccoon in garbage bin
            elif len(storage[key]) == 1:
                if isinstance(storage[key][0], SmartRaccoon):
                    the_copy[key[1]][key[0]] = 'S'
                elif isinstance(storage[key][0], Raccoon):
                    the_copy[key[1]][key[0]] = 'R'
                elif isinstance(storage[key][0], Player):
                    the_copy[key[1]][key[0]] = 'P'
                elif isinstance(storage[key][0], RecyclingBin):
                    the_copy[key[1]][key[0]] = 'B'
                elif isinstance(storage[key][0], GarbageCan):
                    garb_tiles[key] = storage[key][0]
        for key in garb_tiles:
            if garb_tiles[key].locked is True:
                the_copy[key[1]][key[0]] = 'C'
            else:
                the_copy[key[1]][key[0]] = 'O'
        return the_copy

    def to_grid(self) -> list[list[str]]:
        """
        Return the game state as a list of lists of letters where:

        'R' = Raccoon
        'S' = SmartRaccoon
        'P' = Player
        'C' = closed GarbageCan
        'O' = open GarbageCan
        'B' = RecyclingBin
        '@' = Raccoon in GarbageCan
        '-' = Empty tile

        Each inner list represents one row of the game board.

        >>> b = GameBoard(3, 2)
        >>> _ = Player(b, 0, 0)
        >>> _ = Raccoon(b, 1, 1)
        >>> _ = GarbageCan(b, 2, 1, True)
        >>> b.to_grid()
        [['P', '-', '-'], ['-', 'R', 'C']]
        """
        lst = []  # big list
        i = 0
        # create an emtpy grid
        while i < self.height:
            row = []
            j = 0
            while j < self.width:
                row.append('-')
                j += 1
            lst.append(row)
            i += 1

        tile_to_chars = {}
        for i in range(self.height):
            for j in range(self.width):
                # create empty list for each tile to store chars
                tile_to_chars[(j, i)] = []

        # add characters to list
        self._add_char(tile_to_chars)
        result = self._to_grid_helper(lst, tile_to_chars)  # update empty grid
        return result

    def __str__(self) -> str:
        """
        Return a string representation of this board.

        The format is the same as expected by the setup_from_grid method.

        >>> b = GameBoard(3, 2)
        >>> _ = Raccoon(b, 1, 1)
        >>> print(b)
        ---
        -R-
        >>> _ = Player(b, 0, 0)
        >>> _ = GarbageCan(b, 2, 1, False)
        >>> print(b)
        P--
        -RO
        >>> str(b)
        'P--\\n-RO'
        """
        count = 0
        grid = self.to_grid()
        cap = len(grid)
        string = ''
        for sublist in grid:
            if count < cap - 1:
                i = 0
                while i < len(sublist):
                    string += sublist[i]
                    i += 1
                string += '\n'
                count += 1
            else:
                i = 0
                while i < len(sublist):
                    string += sublist[i]
                    i += 1
        return string

    def setup_from_grid(self, grid: str) -> None:
        """
        Set the state of this GameBoard to correspond to the string <grid>,
        which represents a game board using the following symbols:

        'R' = Raccoon not in a GarbageCan
        'P' = Player
        'C' = closed GarbageCan
        'O' = open GarbageCan
        'B' = RecyclingBin
        '@' = Raccoon in GarbageCan
        '-' = Empty tile

        Note: There is a newline character between each board row.
              This character appears as '\\nn' in the doctest example below.

              Visually, the board is as shown below.
              P-B-
              -BRB
              --BB
              -C--

        >>> b = GameBoard(4, 4)
        >>> b.setup_from_grid('P-B-\\n-BRB\\n--BB\\n-C--')
        >>> str(b)
        'P-B-\\n-BRB\\n--BB\\n-C--'
        >>> print(b)
        P-B-
        -BRB
        --BB
        -C--
        """
        lines = grid.split('\n')
        width = len(lines[0])
        height = len(lines)
        self.__init__(width, height)  # reset the board to an empty board
        y = 0
        for line in lines:
            x = 0
            for char in line:
                if char == 'R':
                    Raccoon(self, x, y)
                elif char == 'S':
                    SmartRaccoon(self, x, y)
                elif char == 'P':
                    Player(self, x, y)
                elif char == 'O':
                    GarbageCan(self, x, y, False)
                elif char == 'C':
                    GarbageCan(self, x, y, True)
                elif char == 'B':
                    RecyclingBin(self, x, y)
                elif char == '@':
                    GarbageCan(self, x, y, False)
                    Raccoon(self, x, y)  # Note: assumes not a SmartRaccoon.
                    # Note: the order mattered above, as we have to place the
                    # GarbageCan before the Raccoon!
                    # (see the place_character method precondition)
                x += 1
            y += 1

    # a helper method you may find useful in places
    def on_board(self, x: int, y: int) -> bool:
        """Return True iff the position x, y is within the boundaries of this
        board (based on its width and height), and False otherwise.
        """
        return 0 <= x <= self.width - 1 and 0 <= y <= self.height - 1

    def give_turns(self) -> None:
        """Give every turn-taking character one turn in the game.

        The Player should take their turn first and the number of turns
        should be incremented by one. Then each other TurnTaker
        should be given a turn if RACCOON_TURN_FREQUENCY turns have occurred
        since the last time the TurnTakers were given their turn.

        After all turns are taken, check_game_ended should be called to
        determine if the game is over.

        Precondition:
        self._player is not None

        >>> b = GameBoard(4, 3)
        >>> p = Player(b, 0, 0)
        >>> r = Raccoon(b, 1, 1)
        >>> b.turns
        0
        >>> for _ in range(RACCOON_TURN_FREQUENCY - 1):
        ...     b.give_turns()
        >>> b.turns == RACCOON_TURN_FREQUENCY - 1  # confirm b.turns is correct
        True
        >>> (r.x, r.y) == (1, 1)  # Raccoon hasn't had a turn yet
        True
        >>> (p.x, p.y) == (0, 0)  # Player hasn't had any inputs
        True
        >>> p.record_event(RIGHT)
        >>> b.give_turns()
        >>> (r.x, r.y) != (1, 1)  # Raccoon has had a turn, so must have moved!
        True
        >>> (p.x, p.y) == (1, 0)  # Player moved right!
        True
        """
        # make the player take a turn
        self.turns += 1
        self._player.take_turn()

        # 20 turns reached
        if self.turns % RACCOON_TURN_FREQUENCY == 0:
            for char in self._chars:
                if isinstance(char, Raccoon):
                    char.take_turn()

        self.check_game_ended()

    def handle_event(self, event: tuple[int, int]) -> None:
        """Handle a user-input event.

        The board's Player records the event that happened, so that when the
        Player gets a turn, it can make the move that the user input indicated.

        Preconditions:
        - event in DIRECTIONS
        """
        self._player.record_event(event)

    def check_game_ended(self) -> int | None:
        """Check if this game has ended. A game ends when all the raccoons on
        this game board are either inside a can or trapped.

        If the game has ended:
        - update the ended attribute to be True
        - Return the score, where the score is given by:
            (number of raccoons trapped) * 10 + the adjacent_bin_score
            - Note: Any raccoons inside a garbage can do not contribute
            to the above score

        If the game has not ended:
        - update the ended attribute to be False
        - return None

        >>> b = GameBoard(3, 2)
        >>> _ = Raccoon(b, 1, 0)
        >>> _ = Player(b, 0, 0)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> b.check_game_ended() is None
        True
        >>> b.ended
        False
        >>> _ = RecyclingBin(b, 2, 0)
        >>> b.check_game_ended()
        11
        >>> b.ended
        True
        """
        # check if all raccoons are trapped or in garbage can
        score = 0
        lst = []
        for char in self._chars:
            # check all raccoons status
            if isinstance(char, Raccoon):
                if char.check_trapped():
                    score += 10
                    lst.append(True)
                elif char.inside_can is True:
                    lst.append(True)
                else:
                    lst.append(False)

        # check if game is over
        if False not in lst:  # game is over
            score += self.adjacent_bin_score()
            self.ended = True
            return score
        else:  # game is not over
            self.ended = False
            return None

    def _count_bins(self, the_grid: list[list[str]], the_tile: tuple[int, int],
                    checked: list[tuple[int, int]]) -> int:
        """Return the number of RecyclingBin in the biggest cluster of
        RecyclingBin.

        The search starts from <the_tile>, the adjacent RecyclingBin will be
        recorded in <checked> while going deep in <the_grid>.

        >>> b = GameBoard(3, 3)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> _ = RecyclingBin(b, 0, 0)
        >>> _ = RecyclingBin(b, 2, 2)
        >>> _ = RecyclingBin(b, 2, 1)
        >>> _ = RecyclingBin(b, 0, 1)
        >>> print(b)
        B--
        BBB
        --B
        >>> grid = b.to_grid()
        >>> tile = (1, 1)
        >>> checkedd = []
        >>> b._count_bins(grid, tile, checkedd)
        5
        """
        checked.append(the_tile)
        count = 1

        count += sum(self._count_bins(the_grid, ngbr, checked)
                     for ngbr in neighbours(the_tile)
                     if ((self.on_board(ngbr[0], ngbr[1])
                          and the_grid[ngbr[1]][ngbr[0]] == 'B'
                          and ngbr not in checked)))
        return count

    def adjacent_bin_score(self) -> int:
        """
        Return the size of the largest cluster of adjacent recycling bins
        on this board.

        Two recycling bins are adjacent when they are directly beside each other
        in one of the four directions (up, down, left, right).

        >>> b = GameBoard(3, 3)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> _ = RecyclingBin(b, 0, 0)
        >>> _ = RecyclingBin(b, 2, 2)
        >>> print(b)
        B--
        -B-
        --B
        >>> b.adjacent_bin_score()
        1
        >>> _ = RecyclingBin(b, 2, 1)
        >>> print(b)
        B--
        -BB
        --B
        >>> b.adjacent_bin_score()
        3
        >>> _ = RecyclingBin(b, 0, 1)
        >>> print(b)
        B--
        BBB
        --B
        >>> b.adjacent_bin_score()
        5
        """
        # accumulators
        the_max = 0
        checked = []

        # Get the grid
        grid = self.to_grid()

        # iterate through all tiles in the grid
        for i in range(len(grid)):  # row index
            for j in range(len(grid[0])):  # column index
                tile = (j, i)
                if (tile not in checked
                        and grid[i][j] == 'B'
                        and self.on_board(tile[1], tile[0])):
                    result = self._count_bins(grid, tile, checked)
                    the_max = max(the_max, result)
        return the_max


@check_contracts
class Character:
    """A character that has (x,y) coordinates and is associated with a given
    board.

    This class is abstract and should not be directly instantiated.

    NOTE: To reduce the amount of documentation in subclasses, we have chosen
    not to repeat information about the public attributes in each subclass.
    Remember that the attributes are not inherited, but only exist once we call
    the __init__ of the parent class.

    Attributes:
    - board: the game board that this Character is on
    - x: the x-coordinate of this Character on the board
    - y: the y-coordinate of this Character on the board

    Representation Invariants:
    - self.board.on_board(x, y)
    - self is on self.board
    """
    board: GameBoard
    x: int
    y: int

    def __init__(self, board: GameBoard, x: int, y: int) -> None:
        """Initialize this Character on the given <board>, and
        at tile (<x>, <y>).

        When a Character is initialized, it is placed on <board>
        by calling the board's place_character method.

        Preconditions:
        - board.on_board(x, y)
        - If self is a Player, then there must not be any other players on <board> yet.
        - The tile (x, y) of <board> does not already contain a character, with the
        exception being that a raccoon can be placed on the same tile where
        an empty, unlocked GarbageCan is already present.
        """
        self.board = board
        self.x, self.y = x, y
        self.board.place_character(self)  # this associates self with the board!

    def move(self, direction: tuple[int, int]) -> bool:
        """
        If possible, move this character to the tile:

        (self.x + direction[0], self.y + direction[1]).

        Note: Each child class defines its own version of what is possible.

        Return True if the move was successful and False otherwise.
        """
        raise NotImplementedError

    def get_symbol(self) -> str:
        """
        Return a single letter representing this Character.
        """
        raise NotImplementedError


@check_contracts
class TurnTaker(Character):
    """
    A Character that can take a turn in the game.

    This class is abstract and should not be directly instantiated.
    """

    def take_turn(self) -> None:
        """
        Take a turn in the game. This method must be implemented in any subclass.
        """
        raise NotImplementedError


@check_contracts
class RecyclingBin(Character):
    """A recycling bin in the game.

    === Sample Usage ===
    >>> rb = RecyclingBin(GameBoard(4, 4), 2, 1)
    >>> rb.x, rb.y
    (2, 1)
    """

    def move(self, direction: tuple[int, int]) -> bool:
        """Move this recycling bin to tile:
                (self.x + direction[0], self.y + direction[1])
        if possible and return whether this move was successful.

        If the new tile is occupied by another RecyclingBin, push
        that RecyclingBin one tile away in the same direction and take
        its tile.

        If the new tile is occupied by any other Character or if it
        is beyond the boundaries of the board, do nothing and return False.

        Preconditions:
        - direction in DIRECTIONS

        >>> b = GameBoard(4, 2)
        >>> rb = RecyclingBin(b, 0, 0)
        >>> rb.move(UP)
        False
        >>> rb.move(DOWN)
        True
        >>> b.at(0, 1) == [rb]
        True
        """
        # new location
        new_loc = (self.x + direction[0], self.y + direction[1])
        # check if new location is out of boundary
        if not self.board.on_board(new_loc[0], new_loc[1]):
            return False
        # check if there is other characters at new location
        char_list = self.board.at(new_loc[0], new_loc[1])
        # tile is empty
        if len(char_list) == 0:
            self.x = new_loc[0]
            self.y = new_loc[1]
            return True
        # tile is not emtpy
        else:
            if isinstance(char_list[0], RecyclingBin):  # another recycling bin
                # check if the second recycling bin can be moved
                if char_list[0].move(direction):
                    self.x = new_loc[0]
                    self.y = new_loc[1]
                    return True
                return False
            return False

    def get_symbol(self) -> str:
        """
        Return the character 'B' representing a RecyclingBin.
        """
        return 'B'


@check_contracts
class Player(TurnTaker):
    """The Player of this game.

    Attributes:
    - _last_event: The direction corresponding to the last keypress event that
    the user made, or None if there is currently no keypress event to process.

    Sample Usage:
    >>> b = GameBoard(3, 1)
    >>> p = Player(b, 0, 0)
    >>> p.record_event(RIGHT)
    >>> p.take_turn()
    >>> (p.x, p.y) == (1, 0)
    True
    >>> g = GarbageCan(b, 0, 0, False)
    >>> p.move(LEFT)
    True
    >>> g.locked
    True
    """
    _last_event: tuple[int, int] | None

    def __init__(self, b: GameBoard, x: int, y: int) -> None:
        """Initialize this Player with board <b>,
        and at tile (<x>, <y>).

        Preconditions:
        - the parameters are consistent with the preconditions of Character.__init__
        """

        TurnTaker.__init__(self, b, x, y)
        self._last_event = None

    def record_event(self, direction: tuple[int, int]) -> None:
        """Record that <direction> is the last direction that the user
        has specified for this Player to move. Next time take_turn is called,
        this direction will be used.
        Preconditions:
        - direction in DIRECTIONS
        """
        self._last_event = direction

    def take_turn(self) -> None:
        """Take a turn in the game.

        For a Player, this means responding to the last user input recorded
        by a call to record_event.
        """
        if self._last_event is not None:
            self.move(self._last_event)
            self._last_event = None

    def move(self, direction: tuple[int, int]) -> bool:
        """Attempt to move this Player to the tile:
                (self.x + direction[0], self.y + direction[1])
        if possible and return True if the move is successful.

        If the new tile is occupied by a Racooon, a locked GarbageCan, or if it
        is beyond the boundaries of the board, do nothing and return False.

        If the new tile is occupied by a movable RecyclingBin, the player moves
        the RecyclingBin and moves to the new tile.

        If the new tile is unoccupied, the player moves to that tile.

        If a Player attempts to move towards an empty, unlocked GarbageCan, the
        GarbageCan becomes locked. The player's position remains unchanged in
        this case. Also return True in this case, as the Player has performed
        the action of locking the GarbageCan.

        Preconditions:
        - direction in DIRECTIONS

        >>> b = GameBoard(4, 2)
        >>> p = Player(b, 0, 0)
        >>> p.move(UP)
        False
        >>> p.move(DOWN)
        True
        >>> b.at(0, 1) == [p]
        True
        >>> _ = RecyclingBin(b, 1, 1)
        >>> p.move(RIGHT)
        True
        >>> b.at(1, 1) == [p]
        True
        """
        # new location (supposition)
        new_loc = (self.x + direction[0], self.y + direction[1])

        # check if new location is out of boundary
        if not self.board.on_board(new_loc[0], new_loc[1]):
            return False

        # check if new location has obstacle
        char_list = self.board.at(new_loc[0], new_loc[1])
        # new location is an emtpy tile
        if len(char_list) == 0:
            self.x = new_loc[0]
            self.y = new_loc[1]
            return True
        # character on the new location
        elif len(char_list) != 0:
            # if the character is a recycling bin
            if isinstance(char_list[0], RecyclingBin):
                    # try to move the recycling bin
                if char_list[0].move(direction):
                    self.x = new_loc[0]
                    self.y = new_loc[1]
                    return True
            elif isinstance(char_list[0], GarbageCan):
                if char_list[0].locked is False:
                    char_list[0].locked = True
                    return True
        return False

    def get_symbol(self) -> str:
        """
        Return the character 'P' representing this Player.
        """
        return 'P'


@check_contracts
class Raccoon(TurnTaker):
    """A raccoon in the game.

    Attributes:
    - inside_can: whether this Raccoon is inside a garbage can

    Representation Invariants:
    - inside_can is True iff this Raccoon is on the same tile as an open
    GarbageCan.

    Sample Usage:
    >>> r = Raccoon(GameBoard(11, 11), 5, 10)
    >>> r.x, r.y
    (5, 10)
    >>> r.inside_can
    False
    """
    inside_can: bool

    def __init__(self, b: GameBoard, x: int, y: int) -> None:
        """Initialize this Raccoon with board <b>, and
        at tile (<x>, <y>). Initially a Raccoon is not inside a GarbageCan,
        unless it is placed directly inside an open GarbageCan.

        Preconditions:
        - the parameters are consistent with the preconditions of Character.__init__

        >>> b = GameBoard(5, 5)
        >>> r = Raccoon(b, 4, 3)
        >>> r.x == 4 and r.y == 3
        True
        >>> r.board is b
        True
        """
        # If we do not need inside_can, we do not even need this initializer
        # however, since we need to override, we need to override (extra code
        # and call the parent class initializer. Also, notice that TurnTaker
        # does not have an initializer, but based on Python rule, Raccoon must
        # call the first most parent class' initializer (which is
        # TurnTaker.__init__ in this case)

        # check if raccoon is placed in a garbage can
        lst = b.at(x, y)
        if lst == []:   # empty tile
            self.inside_can = False
        else:
            if (len(lst) == 1 and isinstance(lst[0], GarbageCan)
                    and lst[0].locked is False):
                self.inside_can = True
        TurnTaker.__init__(self, b, x, y)

    def check_trapped(self) -> bool:
        """Return True iff this raccoon is trapped. A trapped raccoon is
        surrounded on 4 sides (diagonals don't matter) by recycling bins, other
        raccoons (including ones in garbage cans), the player, and/or board
        edges. Said another way, a raccoon is trapped when it has nowhere it
        could move.

        Reminder: A racooon cannot move diagonally.

        >>> b = GameBoard(3, 3)
        >>> r = Raccoon(b, 2, 1)
        >>> _ = Raccoon(b, 2, 2)
        >>> _ = Player(b, 2, 0)
        >>> r.check_trapped()
        False
        >>> _ = RecyclingBin(b, 1, 1)
        >>> r.check_trapped()
        True
        """
        count = 0
        # tile for all four directions
        lst = [(self.x + LEFT[0], self.y + LEFT[1]),
               (self.x + UP[0], self.y + UP[1]),
               (self.x + RIGHT[0], self.y + RIGHT[1]),
               (self.x + DOWN[0], self.y + DOWN[1])]

        for tile in lst:
            # check if the tile is out of boundary
            if self.board.on_board(tile[0], tile[1]) is False:
                count += 1
            # check if the tile is occupied by other character
            else:
                lst1 = self.board.at(tile[0], tile[1])
                if lst1 == []:
                    return False
                elif not isinstance(lst1[0], GarbageCan):
                    count += 1
                else:
                    return False
        return count == 4

    def move(self, direction: tuple[int, int]) -> bool:
        """Attempt to move this Raccoon in <direction> and return whether
        this was successful.

        If the tile one tile over in that direction is occupied by the Player,
        a RecyclingBin, or another Raccoon, OR if the tile is not within the
        boundaries of the board, do nothing and return False.

        If the tile is occupied by an unlocked GarbageCan that has no Raccoon
        in it, this Raccoon moves there, and we have two characters on one tile
        (the GarbageCan and the Raccoon). If the GarbageCan is locked, this
        Raccoon uses this turn to unlock it and return True.

        If a Raccoon is inside a GarbageCan, it will not move (note that
        this does not mean that the raccoon is necessarily 'trapped'; it just chooses not
        to move, even if there are available spots beside it). In this case, do
        nothing and return False.

        Return True if the Raccoon unlocks a GarbageCan or moves from its
        current tile.

        Preconditions:
        - direction in DIRECTIONS

        >>> b = GameBoard(4, 2)
        >>> r = Raccoon(b, 0, 0)
        >>> r.move(UP)
        False
        >>> r.move(DOWN)
        True
        >>> b.at(0, 1) == [r]
        True
        >>> g = GarbageCan(b, 1, 1, True)
        >>> r.move(RIGHT)
        True
        >>> r.x, r.y  # Raccoon didn't change its position
        (0, 1)
        >>> not g.locked  # Raccoon unlocked the garbage can!
        True
        >>> r.move(RIGHT)
        True
        >>> r.inside_can
        True
        >>> len(b.at(1, 1)) == 2  # Raccoon and GarbageCan are both at (1, 1)!
        True
        """
        # raccoon is in the garbage can
        if self.inside_can:
            return False
        # raccoon is not in the garbage can
        new_loc = (self.x + direction[0], self.y + direction[1])
        # check if the new location is out of bounds
        if not self.board.on_board(new_loc[0], new_loc[1]):
            return False
        # check if other characters are at new location
        lst = self.board.at(new_loc[0], new_loc[1])
        # empty tile
        if len(lst) == 0:
            self.x = new_loc[0]
            self.y = new_loc[1]
            return True
        # garbage can
        elif len(lst) == 1 and isinstance(lst[0], GarbageCan):
            # closed garbage can
            if lst[0].locked:
                lst[0].locked = False
                return True
            # opened garbage can
            else:
                self.x = new_loc[0]
                self.y = new_loc[1]
                self.inside_can = True
                return True
        return False

    def take_turn(self) -> None:
        """Take a turn in the game.

        If a Raccoon is in a GarbageCan, it happily stays where it is.

        Otherwise, it will move in one of the four directions which aren't
        blocked. If multiple directions aren't blocked, a Raccoon will move in
        one of these directions with equal probability.

        If a Raccoon can't move, then it remains at the same position.

        >>> b = GameBoard(3, 4)
        >>> r1 = Raccoon(b, 0, 0)
        >>> r1.take_turn()
        >>> (r1.x, r1.y) in [(0, 1), (1, 0)]  # will have moved to one of these.
        True
        >>> r2 = Raccoon(b, 2, 1)
        >>> _ = RecyclingBin(b, 2, 0)
        >>> _ = RecyclingBin(b, 1, 1)
        >>> _ = RecyclingBin(b, 2, 2)
        >>> r2.take_turn()  # Raccoon is trapped is won't move
        >>> r2.x, r2.y
        (2, 1)
        """
        # raccoon in a garage can
        if self.inside_can is True:
            return None
        lst = self.board.to_grid()
        options = []
        # find all possible directions for a turn
        for direction in DIRECTIONS:
            potential_pos = (self.x + direction[0], self.y + direction[1])
            if (self.board.on_board(potential_pos[0], potential_pos[1])
                    and (lst[potential_pos[1]][potential_pos[0]])
                    in ['-', 'O']):
                options.append(direction)
        if len(options) != 0:
            shuffle(options)
            self.move(options[0])

    def get_symbol(self) -> str:
        """
        Return '@' to represent that this Raccoon is inside a garbage can
        or 'R' otherwise.
        """
        if self.inside_can:
            return '@'
        return 'R'


@check_contracts
class SmartRaccoon(Raccoon):
    """A smart raccoon in the game.

    Behaves like a Raccoon, but when it takes a turn, it will move towards
    a GarbageCan if it can see that GarbageCan in its line of sight.
    See the take_turn method for details.

    SmartRaccoons move in the same way as Raccoons.

    Sample Usage:
    >>> b = GameBoard(8, 1)
    >>> s = SmartRaccoon(b, 4, 0)
    >>> s.x, s.y
    (4, 0)
    >>> s.inside_can
    False
    """

    def _optimize_left(self) -> tuple[int, bool]:
        """Find the distance between the SmartRaccoon and the closest
        unoccupied GarbageCan on its left direction (if any).

        >>> b = GameBoard(8, 2)
        >>> s = SmartRaccoon(b, 4, 0)
        >>> _ = GarbageCan(b, 3, 1, False)
        >>> _ = GarbageCan(b, 0, 0, False)
        >>> s._optimize_left()
        (4, True)
        """

        grid = self.board.to_grid()
        dist = 0
        is_can = False
        count = 1
        while (self.board.on_board(self.x - count, self.y)
                and grid[self.y][self.x - count] in ['P', '-']):
            dist += 1
            count += 1
        if self.board.on_board(self.x - count, self.y):  # in boundary
            if grid[self.y][self.x - count] in ['R', 'B', '@']:
                dist += 1
            if grid[self.y][self.x - count] in ['O', 'C']:
                dist += 1
                is_can = True
        return dist, is_can

    def _optimize_up(self) -> tuple[int, bool]:
        """Find the distance between the SmartRaccoon and the closest
        unoccupied GarbageCan on its up direction (if any).

        >>> b = GameBoard(8, 2)
        >>> s = SmartRaccoon(b, 4, 0)
        >>> _ = GarbageCan(b, 3, 1, False)
        >>> _ = GarbageCan(b, 0, 0, False)
        >>> s._optimize_up()
        (0, False)
        """
        grid = self.board.to_grid()
        dist = 0
        is_can = False
        count = 1
        while (self.board.on_board(self.x, self.y - count)
               and grid[self.y - count][self.x] in ['P', '-']):
            dist += 1
            count += 1
        if self.board.on_board(self.x, self.y - count):  # in boundary
            if grid[self.y - count][self.x] in ['R', 'B', '@']:
                dist += 1
            if grid[self.y - count][self.x] in ['O', 'C']:
                dist += 1
                is_can = True
        return dist, is_can

    def _optimize_right(self) -> tuple[int, bool]:
        """Find the distance between the SmartRaccoon and the closest
        unoccupied GarbageCan on its right direction (if any).

        >>> b = GameBoard(8, 2)
        >>> s = SmartRaccoon(b, 4, 0)
        >>> _ = GarbageCan(b, 3, 1, False)
        >>> _ = GarbageCan(b, 7, 0, False)
        >>> s._optimize_right()
        (3, True)
        """
        grid = self.board.to_grid()
        dist = 0
        is_can = False
        count = 1
        while (self.board.on_board(self.x + count, self.y)
               and grid[self.y][self.x + count] in ['P', '-']):
            dist += 1
            count += 1
        if self.board.on_board(self.x + count, self.y):  # in boundary
            if grid[self.y][self.x + count] in ['R', 'B', '@']:
                dist += 1
            if grid[self.y][self.x + count] in ['O', 'C']:
                dist += 1
                is_can = True
        return dist, is_can

    def _optimize_down(self) -> tuple[int, bool]:
        """
        Find the distance between the SmartRaccoon and the closest
        unoccupied GarbageCan on its down direction (if any).

        >>> b = GameBoard(8, 2)
        >>> s = SmartRaccoon(b, 4, 0)
        >>> _ = GarbageCan(b, 3, 1, False)
        >>> _ = GarbageCan(b, 4, 1, False)
        >>> s._optimize_down()
        (1, True)
        """
        grid = self.board.to_grid()
        dist = 0
        is_can = False
        count = 1
        while (self.board.on_board(self.x, self.y + count)
               and grid[self.y + count][self.x] in ['P', '-']):
            dist += 1
            count += 1
        if self.board.on_board(self.x, self.y + count):  # in boundary
            if grid[self.y + count][self.x] in ['R', 'B', '@']:
                dist += 1
            if grid[self.y + count][self.x] in ['O', 'C']:
                dist += 1
                is_can = True
        return dist, is_can

    def take_turn(self) -> None:
        """Take a turn in the game.

        If a SmartRaccoon is in a GarbageCan, it stays where it is.

        A SmartRaccoon checks along the four directions for
        the closest non-occupied GarbageCan in its "line of sight".

        Note about line of sight:
        A GarbageCan is in the SmartRaccoon's line of sight if there are no other
        raccoons, RecyclingBins, or other GarbageCans between this SmartRaccoon
        and the non-occupied GarbageCan. The Player may be between this SmartRaccoon and the
        GarbageCan though, as the SmartRaccoon knows that eventually the Player
        will have to move.

        If there is a tie for the closest GarbageCan, a SmartRaccoon
        will prioritize the directions in the order indicated in DIRECTIONS.

        If there are no GarbageCans in its line of sight along one of the four
        directions, it moves exactly like a Raccoon.

        >>> b = GameBoard(8, 2)
        >>> s = SmartRaccoon(b, 4, 0)
        >>> _ = GarbageCan(b, 3, 1, False)
        >>> _ = GarbageCan(b, 0, 0, False)
        >>> _ = GarbageCan(b, 7, 0, False)
        >>> s.take_turn()
        >>> s.x == 5
        True
        >>> s.take_turn()
        >>> s.x == 6
        True
        """
        # collect all optimizations
        all_opt = {LEFT: self._optimize_left(),
                   UP: self._optimize_up(),
                   RIGHT: self._optimize_right(),
                   DOWN: self._optimize_down()
                   }
        # possible directions for garbage cans
        is_cans = []
        for key in all_opt:
            if all_opt[key][1] is True:
                is_cans.append(key)
        # no garbage can
        if is_cans == []:
            self.move(get_shuffled_directions()[0])  # move like a Raccoon (randomly)
        else:
            min_dist = all_opt[is_cans[0]][0]
            best_dir = is_cans[0]
            for item in is_cans:
                if all_opt[item][0] <= min_dist:
                    min_dist = all_opt[item][0]
                    best_dir = item
            self.move(best_dir)

    def get_symbol(self) -> str:
        """
        Return '@' to represent that this SmartRaccoon is inside a Garbage Can
        and 'S' otherwise.
        """
        if self.inside_can:
            return '@'
        return 'S'


@check_contracts
class GarbageCan(Character):
    """A garbage can in the game.

    Attributes:
    - locked: whether this GarbageCan is locked.

    === Sample Usage ===
    >>> b = GameBoard(2, 2)
    >>> g = GarbageCan(b, 0, 0, False)
    >>> g.x, g.y
    (0, 0)
    >>> g.locked
    False
    """
    locked: bool

    def __init__(self, b: GameBoard, x: int, y: int, locked: bool) -> None:
        """Initialize this GarbageCan to be at tile (<x>, <y>) and store
        whether it is locked or not based on <locked>.

        Preconditions:
        - the parameters are consistent with the preconditions of Character.__init__
        """
        Character.__init__(self, b, x, y)
        self.locked = locked

    def get_symbol(self) -> str:
        """
        Return 'C' to represent a closed garbage can and 'O' to represent
        an open (unlocked) garbage can.
        """
        if self.locked:
            return 'C'
        return 'O'

    def move(self, direction: tuple[int, int]) -> bool:
        """
        Garbage cans cannot move, so always return False.
        """
        return False


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    check_pyta = True  # set to False if you don't want to run pyTA
    if check_pyta:
        python_ta.check_all(config=pyta_config)
