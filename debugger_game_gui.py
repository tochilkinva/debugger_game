import tkinter as tk
from enum import StrEnum
from random import randint
from tkinter import ttk, messagebox


class MouseClickType(StrEnum):
    """Тип клика мышкой"""

    LEFT= "left"
    RIGHT= "right"

class Cell:
    """Класс одной клетки поля"""

    def __init__(self):
        self.is_bug: bool = False  # установлен ли баг на клетку
        self.is_revealed: bool = False  # открыта ли клетка или еще нет
        self.is_set_flag = False # установлен ли флаг в клетку
        self.num_of_bugs_around: int = 0  # кол-во багов вокруг клетки

class DebuggerGameResponse:
    """Класс результата игры после клика по клетке"""

    def __init__(self, is_win: bool, is_gameover: bool, board: list[list[Cell]]) -> None:
        """
        :param is_win: флаг победы
        :param is_gameover: флаг конца игры
        :param board: список списков с игровым полем из клеток
        :return: None
        """
        self.is_win: bool = is_win
        self.is_gameover: bool = is_gameover
        self.board: list[list[Cell]] = board

class DebuggerGame:
    """Класс игры Дебаггер"""

    def __init__(self, rows: int = 10, cols: int = 10, bugs: int = 10) -> None:
        """
        :param rows: кол-во строк игровых клеток
        :param cols: кол-во столбцов игровых клеток
        :param bugs: кол-во баг
        :return: None
        """
        self.rows: int = rows
        self.cols: int = cols
        self.bugs: int = bugs if bugs < rows * cols else (rows * cols) // 2
        self.is_first_click: bool = True # флаг определяет это первый клик по игровому полю или нет

        # Создали поле с клетками
        self.board: list[list[Cell]] = [[self.get_new_cell() for _ in range(cols)] for _ in range(rows)]

        self.is_win: bool = False
        self.is_gameover: bool = False

    @staticmethod
    def get_new_cell() -> Cell:
        """Возвращает инстанс клетки поля"""
        return Cell()

    def play_game(self, row: int, col: int, mouse_click_type: MouseClickType) -> DebuggerGameResponse:
        """
        Игровой цикл.
        :param row: индекс строки клетки
        :param col: индекс столбца клетки
        :param mouse_click_type: тип клика (левый или правый)
        :return: модель результата игры после клика по клетке
        """
        # Если игра закончена победой и поражением, то выходим
        if self.is_win or self.is_gameover:
            print("Game Over!")
            return DebuggerGameResponse(
                is_win=self.is_win,
                is_gameover=self.is_gameover,
                board=self.board
            )

        # При первом выборе клетки расставляем баги и подсчитываем кол-во багов вокруг клеток
        if self.is_first_click:
            self.is_first_click = False
            self.place_bugs(row, col)
            self.set_num_of_bugs_around()

        # При правом клике мыши помечаем клетку флагом
        if mouse_click_type == MouseClickType.RIGHT:
            self.board[row][col].is_set_flag = not self.board[row][col].is_set_flag
            return DebuggerGameResponse(
                is_win=self.is_win,
                is_gameover=self.is_gameover,
                board=self.board
            )

        # Отобразили клетку и пустые клетки вокруг
        self.reveal(row, col)

        # Если открыли баг, то проиграли
        if self.board[row][col].is_bug:
            print("You hit a bug! Game over!")
            self.is_gameover = True
            self.show_all_cells()

        # Проверили условие победы
        if self.is_game_win():
            print("Congratulations! You win!")
            self.is_win = True
            self.is_gameover = True
            self.show_all_cells()

        return DebuggerGameResponse(
            is_win=self.is_win,
            is_gameover=self.is_gameover,
            board=self.board
        )

    def show_all_cells(self) -> None:
        """
        Помечает все клетки открытыми.

        :return: None
        """
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col].is_revealed = True
                self.board[row][col].is_set_flag = False

    def is_game_win(self) -> bool:
        """
        Проверяет условие победы: количество не открытых клеток == количеству багов.

        :return: истина = победа, ложь = игра не закончена
        """
        unrevealed_cells = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.board[row][col].is_revealed:
                    unrevealed_cells += 1

        if unrevealed_cells == self.bugs:
            return True

        return False

    def set_num_of_bugs_around(self) -> None:
        """
        Рассчитывает количество багов вокруг клетки и записывает значение в num_of_bugs_around клетки.

        :return: None
        """
        for row in range(self.rows):
            for col in range(self.cols):
                # Если клетка с багом, то пропускаем ее
                if self.board[row][col].is_bug:
                    self.board[row][col].num_of_bugs_around = -1
                    continue

                _bugs = 0
                neighbors = self.get_neighbors(row, col)  # Берем список всех соседних клеток (их индексы)
                for neighbor in neighbors:
                    _row, _col = neighbor
                    # Если соседняя клетка с багом, то увеличиваем счетчик багов вокруг
                    if self.board[_row][_col].is_bug:
                        _bugs += 1

                # Записываем кол-во багов в поле клетки
                self.board[row][col].num_of_bugs_around = _bugs

    def place_bugs(self, row: int, col: int) -> None:
        """
        Размещает баги на поле случайным образом исключая указанную клетку.

        :param row: индекс строки
        :param col: индекс столбца
        :return: None
        """
        # Помечаем клетку открытой
        self.board[row][col].is_revealed = True

        # Заполняем поле багами случайным образом
        placed_bugs = 0
        while placed_bugs < self.bugs:
            random_row = randint(0, self.rows - 1)
            random_col = randint(0, self.cols - 1)

            # Ставим баг на клетку если на ней нет бага и она еще не открыта
            if not self.board[random_row][random_col].is_bug and not self.board[random_row][random_col].is_revealed:
                self.board[random_row][random_col].is_bug = True
                placed_bugs += 1

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
        Открывает соседние клетки если в них нет багов в пределах указанной клетки.

        :param row: индекс строки
        :param col: индекс столбца
        :return: None
        """
        first_cell = True

        # Формируем стэк на базе списка
        stack = [(row, col)]
        while stack:
            current_cell = stack.pop()  # Берем последнюю клетку из стэка
            _row, _col = current_cell

            # Если клетка уже открыта, то игнорируем ее
            if self.board[_row][_col].is_set_flag:
                continue

            self.board[_row][_col].is_revealed = True  # Открываем текущую клетку

            # Ищем соседние клетки вокруг текущей клетки и если клетка не имеет вокруг багов
            if first_cell or self.board[_row][_col].num_of_bugs_around == 0:
                first_cell = False

                # Берем список всех соседних клеток (их индексы)
                neighbors = self.get_neighbors(_row, _col)
                for neighbor_row, neighbor_col in neighbors:
                    # neighbor_row, neighbor_col = neighbor

                    # Если соседняя клетка без багов и еще не открыта, то добавляем ее в стэк для открытия
                    if (
                            not self.board[neighbor_row][neighbor_col].is_bug
                            and not self.board[neighbor_row][neighbor_col].is_revealed
                            and not self.board[neighbor_row][neighbor_col].is_set_flag
                    ):
                        stack.append((neighbor_row, neighbor_col))

class CellGUI:
    """Класс одной клетки поля"""

    def __init__(self, master, row: int, col: int, game_func):
        self.master = master
        self.row = row
        self.col = col

        self.button = ttk.Button(self.master, text=" ", width=2)
        self.button.grid(row=self.row, column=self.col)
        self.button.bind("<ButtonPress-1>", lambda e, r=self.row, c=self.col, mck=MouseClickType.LEFT: game_func(e, r, c, mck))
        self.button.bind("<ButtonPress-3>", lambda e, r=self.row, c=self.col, mck=MouseClickType.RIGHT: game_func(e, r, c, mck))

class DebuggerGameGUI:
    """Класс графической оболочки и интерфейса взаимодействия игры Дебаггер"""

    def __init__(self):
        self.root = tk.Tk()  # создаем главное окно игры
        self.root.title("Дебаггер")

        self.debugger_game: DebuggerGame | None = None  # ядро игры
        self.board_gui: list[list[CellGUI]] | None = None  # список клеток для отображения в окне

        self.mainmenu: tk.Menu | None = None
        self.filemenu: tk.Menu | None = None
        self.helpmenu: tk.Menu | None = None
        self.add_menu()

        self.info_button: ttk.Button | None = None  # кнопка для отображения текстовой информации
        self.init_game(10, 10, 10)

    def add_menu(self) -> None:
        """
        Добавляет меню.

        :return: None
        """
        self.mainmenu = tk.Menu(self.root)
        self.root.config(menu=self.mainmenu)

        self.filemenu = tk.Menu(self.mainmenu, tearoff=0)
        self.filemenu.add_command(label="Легко", command=lambda r=10, c=10, m=10: self.init_game(r, c, m))
        self.filemenu.add_command(label="Нормально", command=lambda r=10, c=15, m=30: self.init_game(r, c, m))
        self.filemenu.add_command(label="Сложно", command=lambda r=10, c=20, m=40: self.init_game(r, c, m))
        self.filemenu.add_command(label="Выход", command=lambda: self.root.destroy())

        self.helpmenu = tk.Menu(self.mainmenu, tearoff=0)
        self.helpmenu.add_command(label="О программе", command=self.gui_about)

        self.mainmenu.add_cascade(label="Сложность", menu=self.filemenu)
        self.mainmenu.add_cascade(label="Справка", menu=self.helpmenu)

    def run(self) -> None:
        """
        Запускает графический интерфейс игры Дебаггер.

        :return: None
        """
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

    def play_game(self, event, row: int, col: int, mouse_click_type: MouseClickType) -> None:
        """
        Функция, которая вызывается при клике по игровой клетке.

        :param event: событие
        :param row: индекс строки клетки
        :param col: индекс столбца клетки
        :param mouse_click_type: тип клика (левый или правый)
        :return: None
        """
        # Не обрабатываем нажатие на выключенную кнопку
        if str(self.board_gui[row][col].button['state']) == tk.DISABLED:
            return

        # Обращаемся к ядру игры за результатом
        debugger_game_response = self.debugger_game.play_game(row=row, col=col, mouse_click_type=mouse_click_type)

        # Отображаем текст, если выиграли или проиграли
        if debugger_game_response.is_win:
            print(f"{debugger_game_response.is_win=}")
            self.info_button.configure(text="Победа! Вы нашли все баги!")

        elif debugger_game_response.is_gameover:
            print(f"{debugger_game_response.is_gameover=}")
            self.info_button.configure(text="Поражение! Баг сломал код!")

        # Обновляем отображение игрового поля
        self.update_gui(debugger_game_response)

    def update_gui(self, debugger_game_response: DebuggerGameResponse) -> None:
        """
        Функция визуального обновления игрового поля после клика.

        :param debugger_game_response: модель результата игры после клика по клетке
        :return: None
        """
        for board_row_gui in self.board_gui:
            for board_cell_gui in board_row_gui:
                debugger_game_cell = debugger_game_response.board[board_cell_gui.row][board_cell_gui.col]
                if debugger_game_cell.is_set_flag:
                    text = "?"
                    board_cell_gui.button.configure(text=text)
                    continue

                if debugger_game_cell.is_revealed:
                    if debugger_game_cell.is_bug:
                        text = "Б"
                    elif debugger_game_cell.num_of_bugs_around != 0:
                        text = str(debugger_game_cell.num_of_bugs_around)
                    else:
                        text = " "  # Если пустая ячейка

                    board_cell_gui.button.configure(state=tk.DISABLED)
                    board_cell_gui.button.configure(text=text)
                    continue

                text = " "  # Если пустая ячейка
                board_cell_gui.button.configure(text=text)

    @staticmethod
    def gui_about() -> None:
        """
        Выводит окно справки с сообщением об игре

        :return: None
        """
        messagebox.showinfo(
            title="О программе",
            message="Игра Дебаггер - нужно отметить все баги в коде.\n\n"
            "Для отметки бага нажмите правую клавишу мыши.\n"
            "Для открытия клетки нажмите левую клавишу мыши.\n\n"
            "Число показывает количество багов вокруг клетки.\n\n"
            "Если отметить все баги, то игра завершится победой.\n"
            "При попадании на баг игра завершится проигрышем.\n"
        )

    def init_game(self, rows: int, cols: int, bugs: int) -> None:
        """
        Метод создания всего необходимого для игры

        :param rows: кол-во строк игровых клеток
        :param cols: кол-во столбцов игровых клеток
        :param bugs: кол-во багов
        :return: None
        """
        self.uninit_game()  # Сначала все чистим от старых клеток

        self.debugger_game = DebuggerGame(rows, cols, bugs)  # Создаем ядро игры
        self.board_gui: list[list[CellGUI]] = [
            [CellGUI(self.root, row, col, self.play_game) for col in range(cols)] for row in range(rows)
        ] # Создаем графическое отображение клеток

        # Добавляем кнопку для отображения текстовой информации
        self.info_button = ttk.Button(self.root, text="Отметьте все баги", state=tk.DISABLED, width=3 * cols)
        self.info_button.grid(row=rows + 1, columnspan=cols)

    def uninit_game(self) -> None:
        """
        Метод приведения игры к начальному состоянию

        :return: None
        """
        # Удаляем кнопки игровых клеток
        if self.board_gui is not None:
            for row in self.board_gui:
                for col in row:
                    col.button.destroy()
            self.board_gui = None

        # Удаляем кнопку для отображения текстовой информации
        if self.info_button is not None:
            self.info_button.destroy()
            self.info_button = None



if __name__ == '__main__':
    game = DebuggerGameGUI()
    game.run()
