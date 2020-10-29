import random

from itertools import combinations
from typing import List, Tuple

from battleship.ship import Ship

OFFSET_UPPER_CASE_CHAR_CONVERSION = 64

class Board(object):
    """
    Class representing the board of the player. Interface between the player and its ships.
    """
    SIZE_X = 10  # length of the rectangular board, along the x axis
    SIZE_Y = 10  # length of the rectangular board, along the y axis

    # dict: length -> number of ships of that length
    DICT_NUMBER_SHIPS_PER_LENGTH = {1: 1,
                                    2: 1,
                                    3: 1,
                                    4: 1,
                                    5: 1}

    def __init__(self,
                 list_ships: List[Ship]):
        """
        :param list_ships: list of ships for the board.
        :raise ValueError if the list of ships is in contradiction with Board.DICT_NUMBER_SHIPS_PER_LENGTH.
        :raise ValueError if there are some ships that are too close from each other
        """
        self.list_ships = list_ships
        self.set_coordinates_previous_shots = set()

        if not self.lengths_of_ships_correct():
            total_number_of_ships = sum(self.DICT_NUMBER_SHIPS_PER_LENGTH.values())

            error_message = f"There should be {total_number_of_ships} ships in total:\n"

            for length_ship, number_ships in self.DICT_NUMBER_SHIPS_PER_LENGTH.items():
                error_message += f" - {number_ships} of length {length_ship}\n"

            raise ValueError(error_message)

        if self.are_some_ships_too_close_from_each_other():
            raise ValueError("There are some ships that are too close from each other.")

    def has_no_ships_left(self) -> bool:
        for s in self.list_ships:
            if not s.has_sunk():
                return False
        return True

    def is_attacked_at(self, coord_x: int, coord_y: int) -> Tuple[bool, bool]:
        self.set_coordinates_previous_shots.add((coord_x, coord_y))
        for s in self.list_ships:
            if (coord_x, coord_y) in s.get_all_coordinates():
                s.gets_damage_at(coord_x, coord_y)
                return (s.is_damaged_at(coord_x, coord_y), s.has_sunk())
        return (False, False)

    def print_board_with_ships_positions(self) -> None:
        array_board = [[' ' for _ in range(self.SIZE_X)] for _ in range(self.SIZE_Y)]

        for x_shot, y_shot in self.set_coordinates_previous_shots:
            array_board[y_shot - 1][x_shot - 1] = 'O'

        for ship in self.list_ships:
            if ship.has_sunk():
                for x_ship, y_ship in ship.set_all_coordinates:
                    array_board[y_ship - 1][x_ship - 1] = '$'
                continue

            for x_ship, y_ship in ship.set_all_coordinates:
                array_board[y_ship - 1][x_ship - 1] = 'S'

            for x_ship, y_ship in ship.set_coordinates_damages:
                array_board[y_ship - 1][x_ship - 1] = 'X'

        board_str = self._get_board_string_from_array_chars(array_board)

        print(board_str)

    def print_board_without_ships_positions(self) -> None:
        array_board = [[' ' for _ in range(self.SIZE_X)] for _ in range(self.SIZE_Y)]

        for x_shot, y_shot in self.set_coordinates_previous_shots:
            array_board[y_shot - 1][x_shot - 1] = 'O'

        for ship in self.list_ships:
            if ship.has_sunk():
                for x_ship, y_ship in ship.set_all_coordinates:
                    array_board[y_ship - 1][x_ship - 1] = '$'
                continue

            for x_ship, y_ship in ship.set_coordinates_damages:
                array_board[y_ship - 1][x_ship - 1] = 'X'

        board_str = self._get_board_string_from_array_chars(array_board)

        print(board_str)

    def _get_board_string_from_array_chars(self, array_board: List[List[str]]) -> str:
        list_lines = []

        array_first_line = [chr(code + OFFSET_UPPER_CASE_CHAR_CONVERSION) for code in range(1, self.SIZE_X + 1)]
        first_line = ' ' * 6 + (' ' * 5).join(array_first_line) + ' \n'

        for index_line, array_line in enumerate(array_board, 1):
            number_spaces_before_line = 2 - len(str(index_line))
            space_before_line = number_spaces_before_line * ' '
            list_lines.append(f'{space_before_line}{index_line} |  ' + '  |  '.join(array_line) + '  |\n')

        line_dashes = '   ' + '-' * 6 * self.SIZE_X + '-\n'

        board_str = first_line + line_dashes + line_dashes.join(list_lines) + line_dashes

        return board_str

    def lengths_of_ships_correct(self) -> bool:
        ships = {}
        for s in self.list_ships:
            ships[len(s)] = ships.get(len(s), 0) + 1
        return ships == self.DICT_NUMBER_SHIPS_PER_LENGTH

    def valid_ship_placements(self, list_ships) -> bool:
        pairs = combinations(list_ships, 2)
        for p in pairs:
            if p[0].is_near_ship(p[1]) and p[0] != p[1]:
                return False
        return True

    def are_some_ships_too_close_from_each_other(self) -> bool:
        return not self.valid_ship_placements(self.list_ships)

    def valid_coordinates(self, x, y) -> bool:
        return 1 <= x <= self.SIZE_X and 1 <= y <= self.SIZE_Y

class BoardAutomatic(Board):
    
    _MAX_TRIES = 100

    def __init__(self):
        super().__init__(list_ships=self.generate_ships_automatically())

    def _generate_random_ship(self, length) -> Ship:
        t = 0
        valid = False
        while not valid and t < self._MAX_TRIES:
            x_start = random.randint(1, self.SIZE_X)
            y_start = random.randint(1, self.SIZE_Y)
            is_vertical = random.choice([True, False])
            l = random.choice([-length + 1, length - 1])
            if is_vertical:
                x_end = x_start
                y_end = y_start + l
            else:
                x_end = x_start + l
                y_end = y_start
            valid = self.valid_coordinates(x_end, y_end)
                   
            t += 1
        return Ship((x_start, y_start), (x_end, y_end))        

    def generate_ships_automatically(self) -> List[Ship]:
        """
        :return: A list of automatically (randomly) generated ships for the board
        """
        list_ships = []
        for l in self.DICT_NUMBER_SHIPS_PER_LENGTH.keys():
            t = 0
            valid_list = False
            while not valid_list and t < self._MAX_TRIES:
                ship = self._generate_random_ship(l)
                list_ships.append(ship)
                valid_list = self.valid_ship_placements(list_ships)
                if not valid_list: 
                    list_ships.pop()
                t += 1
        return list_ships


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
    board.print_board_with_ships_positions()
    board.print_board_without_ships_positions()
    print(board.is_attacked_at(5, 4),
          board.is_attacked_at(10, 9))
    print(board.set_coordinates_previous_shots)
    print(board.lengths_of_ships_correct())
    print(board.are_some_ships_too_close_from_each_other())
