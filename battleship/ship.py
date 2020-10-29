class Ship(object):
    """
    Representing the ships that are placed on the board
    """

    def __init__(self,
                 coord_start: tuple,
                 coord_end: tuple):
        """
        Creates a ship given its start and end coordinates on board (the order does not matter)
        :param coord_start: tuple of 2 positive integers representing the starting position of the Ship on the board
        :param coord_end: tuple of 2 positive integers representing the ending position of the Ship on the board
        :raise ValueError: if the ship is neither horizontal nor vertical
        """

        self.x_start, self.y_start = coord_start
        self.x_end, self.y_end = coord_end

        self.x_start, self.x_end = min(self.x_start, self.x_end), max(self.x_start, self.x_end)
        self.y_start, self.y_end = min(self.y_start, self.y_end), max(self.y_start, self.y_end)

        if not self.is_horizontal() and not self.is_vertical():
            raise ValueError("The ship_1 needs to have either a horizontal or a vertical orientation.")

        self.set_coordinates_damages = set()
        self.set_all_coordinates = self.get_all_coordinates()

    def __len__(self):
        return self.length()

    def __repr__(self):
        return f"Ship(start=({self.x_start},{self.y_start}), end=({self.x_end},{self.y_end}))"

    @classmethod
    def get_ship_from_str_coordinates(cls, coord_str_start: str, coord_str_end: str) -> 'Ship':
        from battleship.convert import get_tuple_coordinates_from_str
        return cls(coord_start=get_tuple_coordinates_from_str(coord_str_start),
                   coord_end=get_tuple_coordinates_from_str(coord_str_end))

    def is_vertical(self) -> bool:
        return self.x_start == self.x_end 

    def is_horizontal(self) -> bool:
        return self.y_start == self.y_end

    def length(self) -> int:
        if self.is_horizontal():
            return self.x_end - self.x_start + 1
        return self.y_end - self.y_start + 1

    def is_on_coordinate(self,
                         coord_x: int,
                         coord_y: int
                         ) -> bool:
        return (coord_x, coord_y) in self.set_all_coordinates

    def gets_damage_at(self,
                       coord_damage_x: int,
                       coord_damage_y: int
                       ) -> None:
        if (coord_damage_x, coord_damage_y) in self.set_all_coordinates:
            self.set_coordinates_damages.add((coord_damage_x, coord_damage_y))

    def is_damaged_at(self,
                      coord_x: int,
                      coord_y: int,
                      ) -> bool:
        return (coord_x, coord_y) in self.set_coordinates_damages

    def number_damages(self) -> int:
        return len(self.set_coordinates_damages)

    def has_sunk(self) -> bool:
        return len(self) == len(self.set_coordinates_damages)
        
    def get_all_coordinates(self) -> set:
        coords = set()
    
        if self.is_vertical():
            x = [self.x_start for _ in range(len(self))]
            y = list(range(self.y_start, self.y_end + 1, 1))
        else:
            x = list(range(self.x_start, self.x_end + 1, 1))
            y = [self.y_start for _ in range(len(self))]
        
        for i in range(len(self)):
            coords.add((x[i], y[i]))

        return coords


    def is_near_coordinate(self, coord_x: int, coord_y: int) -> bool:
        return self.x_start - 1 <= coord_x <= self.x_end + 1 \
               and self.y_start - 1 <= coord_y <= self.y_end + 1

    def is_near_ship(self, other_ship: 'Ship') -> bool:
        other_ship_coords = other_ship.get_all_coordinates()
        for c in other_ship_coords:
            if self.is_near_coordinate(c[0], c[1]):
                return True
        return False

if __name__ == '__main__':
    ship = Ship(coord_start=(3, 3), coord_end=(5, 3))
    print(ship.is_vertical())
    print(ship.is_near_coordinate(5, 3))
    ship.gets_damage_at(4, 3)
    ship.gets_damage_at(10, 3)
    print(ship.is_damaged_at(4, 3), ship.is_damaged_at(5, 3), ship.is_damaged_at(10, 3))
    
    ship_2 = Ship(coord_start=(4, 1), coord_end=(4, 5))
    print(ship.is_near_ship(ship_2))
