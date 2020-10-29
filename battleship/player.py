import random
from typing import Tuple

from battleship.board import Board, BoardAutomatic
from battleship.ship import Ship
from battleship.convert import get_tuple_coordinates_from_str, get_str_coordinates_from_tuple


class Player(object):
    """
    Class representing the player
    - chooses where to perform an attack
    """
    index_player = 0

    def __init__(self,
                 board: Board,
                 name_player: str = None,
                 ):
        Player.index_player += 1

        self.board = board
        self.successful_hits = set()

        if name_player is None:
            self.name_player = "player_" + str(self.index_player)
        else:
            self.name_player = name_player

    def __str__(self):
        return self.name_player

    def attacks(self,
                opponent) -> Tuple[bool, bool]:
        """
        :param opponent: object of class Player representing the person to attack
        :return: a tuple of bool variables (is_ship_hit, has_ship_sunk) where:
                    - is_ship_hit is True if and only if the attack was performed at a set of coordinates where an
                    opponent's ship is.
                    - has_ship_sunk is True if and only if that attack made the ship sink.
        """

        assert isinstance(opponent, Player)

        print(f"Here is the current state of {opponent}'s board before {self}'s attack:\n")
        opponent.print_board_without_ships()

        coord_x, coord_y = self.select_coordinates_to_attack(opponent)

        print(f"{self} attacks {opponent} "
              f"at position {get_str_coordinates_from_tuple(coord_x, coord_y)}")

        is_ship_hit, has_ship_sunk = opponent.is_attacked_at(coord_x, coord_y)
        if is_ship_hit:
            self.successful_hits.add((coord_x, coord_y))

        if has_ship_sunk:
            print(f"\nA ship of {opponent} HAS SUNK. {self} can play another time.")
        elif is_ship_hit:
            print(f"\nA ship of {opponent} HAS BEEN HIT. {self} can play another time.")
        else:
            print("\nMissed".upper())

        return is_ship_hit, has_ship_sunk

    def is_attacked_at(self,
                       coord_x: int,
                       coord_y: int
                       ) -> Tuple[bool, bool]:
        """
        :param coord_x: integer representing the projection of a coordinate on the x-axis
        :param coord_y: integer representing the projection of a coordinate on the y-axis
        :return: a tuple of bool variables (is_ship_hit, has_ship_sunk) where:
                    - is_ship_hit is True if and only if the attack was performed at a set of coordinates where a
                    ship is (on the board owned by the player).
                    - has_ship_sunk is True if and only if that attack made the ship sink.
        """
        return self.board.is_attacked_at(coord_x, coord_y)


    def select_coordinates_to_attack(self, opponent) -> Tuple[int, int]:
        """
        Abstract method, for choosing where to perform the attack
        :param opponent: object of class Player representing the player under attack
        :return: a tuple of coordinates (coord_x, coord_y) at which the next attack will be performed
        """
        raise NotImplementedError

    def has_lost(self) -> bool:
        """
        :return: True if and only if all the ships of the player have sunk
        """
        return self.board.has_no_ships_left()

    def print_board_with_ships(self):
        self.board.print_board_with_ships_positions()

    def print_board_without_ships(self):
        self.board.print_board_without_ships_positions()



class PlayerUser(Player):
    """
    Player representing a user playing manually
    """

    def select_coordinates_to_attack(self, opponent: Player) -> Tuple[int, int]:
        """
        Overrides the abstract method of the parent class.
        :param opponent: object of class Player representing the player under attack
        :return: a tuple of coordinates (coord_x, coord_y) at which the next attack will be performed
        """
        print(f"It is now {self}'s turn.")

        while True:
            try:
                coord_str = input('coordinates target = ')
                coord_x, coord_y = get_tuple_coordinates_from_str(coord_str)
                return coord_x, coord_y
            except ValueError as value_error:
                print(value_error)


class PlayerAI(Player):
    """
    Base class for an automated Player
    """
    def __init__(self, name_player: str = None):
        board = BoardAutomatic()
        self.set_ships_opponent_previously_sunk = set()
        self.set_positions_previously_attacked = set()
        self.last_attack_coord = None
        super().__init__(board, name_player)
    
    def select_random_coordinates_to_attack(self) -> tuple:
        has_position_been_previously_attacked = True
        is_position_near_previously_sunk_ship = True
        coord_random = None

        while has_position_been_previously_attacked or is_position_near_previously_sunk_ship:
            coord_random = self._get_random_coordinates()

            has_position_been_previously_attacked = coord_random in self.set_positions_previously_attacked
            is_position_near_previously_sunk_ship = self._is_position_near_previously_sunk_ship(coord_random)

        return coord_random
        
    def _get_random_coordinates(self) -> tuple:
        coord_random_x = random.randint(1, self.board.SIZE_X)
        coord_random_y = random.randint(1, self.board.SIZE_Y)

        coord_random = (coord_random_x, coord_random_y)

        return coord_random

    def _is_position_near_previously_sunk_ship(self, coord: tuple) -> bool:
        for ship_opponent in self.set_ships_opponent_previously_sunk:  # type: Ship
            if ship_opponent.has_sunk() and ship_opponent.is_near_coordinate(*coord):
                return True
        return False


class PlayerAutomatic(PlayerAI):
    """
    Player playing automatically targetting positions near previous successful hits
    ignoring positions near sunk ships and previously hit positions
    """

    def __init__(self, name_player: str = None):
        super().__init__(name_player)

    def _get_positions_near_hits(self) -> set:
        pos = set()
        for hit in self.successful_hits:
            u, v = hit 
            for i in [-1, 0 ,1]:
                for j in [-1, 0, 1]:
                    if (i != 0 or j != 0) and self.board.valid_coordinates(u+i, v+j):
                        pos.add((u+i, v+j))
        return pos

    # keeping track of enemy ships that have been sunk
    def _update_sunk_ships(self, opponent: Player) -> None:
        opponent_ships = opponent.board.list_ships
        for ship in opponent_ships:
            if ship.has_sunk():
                self.set_ships_opponent_previously_sunk.add(ship)

    def _get_positions_near_ships(self, ships: set) -> set:
        positions = set()
        for x in range(1, 1 + self.board.SIZE_X):
            for y in range(1, 1 + self.board.SIZE_Y):
                for ship in ships:
                    if ship.is_near_coordinate(x, y):
                        positions.add((x,y))        
        return positions 

    # positions near successful hits less any positions near sunk ships and previously targetted positions
    def _get_likely_targets(self) -> set:
        targets = self._get_positions_near_hits()
        duds = self._get_positions_near_ships(self.set_ships_opponent_previously_sunk)
        previous_attacks = self.set_positions_previously_attacked
        return targets - duds - previous_attacks

    def select_coordinates_to_attack(self, opponent: Player) -> tuple:
        self._update_sunk_ships(opponent)
        likely_targets = self._get_likely_targets()
        if likely_targets:
            position_to_attack = likely_targets.pop()
        else:
            position_to_attack = self.select_random_coordinates_to_attack()

        self.set_positions_previously_attacked.add(position_to_attack)
        return position_to_attack

class PlayerRandom(PlayerAI):
    def __init__(self, name_player: str = None):
        super().__init__(name_player)

    def select_coordinates_to_attack(self, opponent: Player) -> tuple:
        position_to_attack = self.select_random_coordinates_to_attack()

        self.set_positions_previously_attacked.add(position_to_attack)
        self.last_attack_coord = position_to_attack
        return position_to_attack


if __name__ == '__main__':
    # SANDBOX for you to play and test your functions

    list_ships = [
        Ship(coord_start=(1, 1), coord_end=(1, 1)),
        Ship(coord_start=(3, 3), coord_end=(3, 4)),
        Ship(coord_start=(5, 3), coord_end=(5, 5)),
        Ship(coord_start=(7, 1), coord_end=(7, 4)),
        Ship(coord_start=(9, 3), coord_end=(9, 7)),
    ]

    board = Board(list_ships)
    player = PlayerUser(board)
    print(player.is_attacked_at(5, 4))
    print(player.has_lost())

