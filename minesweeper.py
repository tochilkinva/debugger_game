from random import randint


class Cell:
    """Класс одной клетки поля"""

    def __init__(self):
        self.is_mine: bool = False  # установлена ли мина на клетку
        self.is_revealed: bool = False  # открыта ли клетка или еще нет
        self.num_of_mines_around: int = 0  # кол-во мин вокруг клетки

class DrawBoard:
    """Класс отображения поля с клетками"""

    def __init__(self, rows: int, cols: int, max_col_simbls: int):
        self.rows: int = rows
        self.cols: int = cols
        self.max_col_simbls = max_col_simbls  # Максимальная длина цифры столбца

    def print_board(self,board: list[list[Cell]], reveal_mines: bool = False) -> None:
        """
        Выводит на экран игровое поле.

        :param board: игровое поле с клетками
        :param reveal_mines: флаг истины отображает мины на поле
        :return: None
        """
        print(" ")

        # Выводим первую строку с номерами столбцов поля
        first_string = [' '] + [' '] * len(str(self.cols)) + [f"{self.draw_cell(str(num))}" for num in range(self.cols)]
        print(''.join(first_string))

        # Выводим остальные строки
        for row_index in range(self.rows):
            row = board[row_index]  # Берем строку с клетками
            last_row_string = []  # Список для отображения клеток строки
            for cell in row:
                # Если отображаем мины
                if reveal_mines:
                    last_row_string.append(
                        # Отображаем число мин вокруг, если это не мина
                        self.draw_cell(self.draw_num(cell.num_of_mines_around))
                        if not cell.is_mine
                        else self.draw_cell(self.draw_mine())  # Или отображаем мину
                    )
                # Если скрываем мины
                else:
                    last_row_string.append(
                        # Отображаем число мин вокруг, если это не мина и клетка не открыта
                        self.draw_cell(self.draw_num(cell.num_of_mines_around))
                        if (not cell.is_mine and cell.is_revealed)
                        else self.draw_cell(self.draw_question_mark())  # Или отображаем знак вопроса
                    )

            # Указываем номер строки и добавляем список с клетками
            row_string = [self.draw_cell(str(row_index))] + last_row_string
            print(''.join(row_string))

    def draw_cell(self, simbl: str) -> str:
        """
        Возвращает строковое представление ячейки

        :return: строковое представление ячейки
        """
        curr_simbls = len(simbl)

        # Если длинна строки совпадает с максимальной длинной цифры столбца, то возвращаем как есть
        if curr_simbls == self.max_col_simbls:
            return f" {simbl}"

        new_simbl = [" "]
        new_simbl.extend([" "] * (self.max_col_simbls - curr_simbls))
        new_simbl.append(simbl)
        return "".join(new_simbl)

    @staticmethod
    def draw_mine() -> str:
        """
        Возвращает строковое представление мины

        :return: строковое представление
        """
        return "M"

    @staticmethod
    def draw_question_mark() -> str:
        """
        Возвращает строковое представление неизвестной клетки

        :return: строковое представление
        """
        return "?"

    @staticmethod
    def draw_num(num: int) -> str:
        """
        Возвращает строковое представление числа или пустоты

        :param num: число (кол-во мин вокруг)
        :return: строковое представление
        """
        if num == 0:
            return " "

        return str(num)

class Minesweeper:
    """Класс игры сапер"""

    def __init__(self, rows: int, cols: int, mines: int = 10) -> None:
        """
        :param rows: кол-во строк
        :param cols: кол-во столбцов
        :param mines: кол-во мин
        :return: None
        """
        self.rows: int = rows
        self.cols: int = cols
        self.mines: int = mines if mines < rows * cols else (rows * cols) // 2
        self.first_step: bool = True

        # Создали поле с клетками
        self.board: list[list[Cell]] = [[self.get_new_cell() for _ in range(cols)] for _ in range(rows)]
        self.max_col_simbls: int = len(str(self.cols - 1))  # Максимальная длина цифры столбца

        # Класс для отображения игрового поля
        self.draw_board = DrawBoard(
            rows=self.rows,
            cols=self.cols,
            max_col_simbls=self.max_col_simbls
        )

    @staticmethod
    def get_new_cell() -> Cell:
        """Возвращает инстанс клетки поля"""
        return Cell()

    def play(self) -> None:
        """
        Игровой цикл.

        :return: None
        """
        while True:
            # Отображаем игровое поле
            self.draw_board.print_board(board=self.board)

            # Просим игрока выбрать клетку
            try:
                row, col = map(int, input("Enter row and column: ").split())
                assert 0 <= row < self.rows and 0 <= col < self.cols
            except (ValueError, AssertionError):
                print(f"Invalid input. Please enter numbers between {self.rows - 1} and {self.cols - 1}.")
                continue

            # При первом выборе клетки расставляем мины и подсчитываем кол-во мин вокруг клеток
            if self.first_step:
                self.first_step = False
                self.place_mines(row, col)
                self.set_num_of_mines_around()

            # Если открыли мину, то проиграли
            if self.board[row][col].is_mine:
                print("You hit a mine! Game Over.")
                self.draw_board.print_board(board=self.board, reveal_mines=True)
                break

            # Отобразили клетку и пустые клетки вокруг
            self.reveal(row, col)

            # Проверили условие победы
            if self.is_win():
                print("Congratulations! You've cleared the minefield.")
                self.draw_board.print_board(board=self.board, reveal_mines=True)
                break

    def is_win(self) -> bool:
        """
        Проверяет условие победы: количество не открытых клеток == количеству мин.

        :return: истина = победа, ложь = игра не закончена
        """
        unrevealed_cells = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.board[row][col].is_revealed:
                    unrevealed_cells += 1

        if unrevealed_cells == self.mines:
            return True

        return False

    def set_num_of_mines_around(self) -> None:
        """
        Рассчитывает количество мин вокруг клетки и записывает в поле клетку.

        :return: None
        """
        for row in range(self.rows):
            for col in range(self.cols):
                # Если клетка с миной, то пропускаем ее
                if self.board[row][col].is_mine:
                    self.board[row][col].num_of_mines_around = -1
                    continue

                _mines = 0
                neighbors = self.get_neighbors(row, col)  # Берем список всех соседних клеток (их индексы)
                for neighbor in neighbors:
                    _row, _col = neighbor
                    # Если соседняя клетка с миной, то увеличиваем счетчик мин вокруг
                    if self.board[_row][_col].is_mine:
                        _mines += 1

                # Записываем кол-во мин в поле клетки
                self.board[row][col].num_of_mines_around = _mines

    def place_mines(self, row: int, col: int) -> None:
        """
        Размещает мины на поле случайным образом исключая указанную клетку.

        :param row: индекс строки
        :param col: индекс столбца
        :return: None
        """
        # Помечаем клетку открытой
        self.board[row][col].is_revealed = True

        # Заполняем поле минами случайным образом
        placed_mines = 0
        while placed_mines < self.mines:
            random_row = randint(0, self.rows - 1)
            random_col = randint(0, self.cols - 1)

            # Ставим мину на клетку если на ней нет мины и она еще не открыта
            if not self.board[random_row][random_col].is_mine and not self.board[random_row][random_col].is_revealed:
                self.board[random_row][random_col].is_mine = True
                placed_mines += 1

    def get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        """
        Возвращает список соседних клеток по указанной клетке.

        :param row: индекс строки
        :param col: индекс столбца
        :return: список из кортежей (индекс строки, индекс столбца)
        """
        # Определяем границы вокруг клетки
        min_row = row - 1 if row > 0 else 0
        max_row = row + 1 if row < self.rows - 1 else self.rows - 1
        min_col = col - 1 if col > 0 else 0
        max_col = col + 1 if col < self.cols - 1 else self.cols - 1

        neighbors = []
        for _row in range(min_row, max_row + 1):
            for _col in range(min_col, max_col + 1):
                if (_row, _col) != (row, col):  # Исключаем текущую клетку
                    neighbors.append((_row, _col))
        return neighbors

    def reveal(self, row: int, col: int) -> None:
        """
        Открывает соседние клетки если в них нет мин в пределах указанной клетки.

        :param row: индекс строки
        :param col: индекс столбца
        :return: None
        """
        stack = [(row, col)]
        first_cell = True

        # Формируем стэк на базе списка
        while stack:
            current_cell = stack.pop()  # Берем последнюю клетку из стэка
            _row, _col = current_cell
            self.board[_row][_col].is_revealed = True  # Открываем текущую клетку

            # Ищем соседние клетки вокруг текущей клетки или если клетка не имеет вокруг мин
            if first_cell or self.board[_row][_col].num_of_mines_around == 0:
                first_cell = False

                # Берем список всех соседних клеток (их индексы)
                neighbors = self.get_neighbors(_row, _col)
                for neighbor in neighbors:
                    neighbor_row, neighbor_col = neighbor

                    # Если соседняя клетка без мины и еще не открыта, то добавляем ее в стэк для открытия
                    if (
                            not self.board[neighbor_row][neighbor_col].is_mine
                            and not self.board[neighbor_row][neighbor_col].is_revealed
                    ):
                        stack.append((neighbor_row, neighbor_col))


if __name__ == "__main__":
    rows, cols, mines = 11, 21, 5
    game = Minesweeper(rows, cols, mines)
    try:
        game.play()
    except KeyboardInterrupt:
        pass
