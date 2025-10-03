import random
import time
import tkinter as tk
from tkinter import messagebox


class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.window.resizable(False, False)

        # Константы игры
        self.CELL_SIZE = 30
        self.GRID_WIDTH = 20
        self.GRID_HEIGHT = 15
        self.GAME_SPEED = 200  # начальная скорость (мс)

        # Создание холста
        self.canvas = tk.Canvas(
            self.window,
            width=self.GRID_WIDTH * self.CELL_SIZE,
            height=self.GRID_HEIGHT * self.CELL_SIZE + 40,  # +40 для панели счета
            bg="black"
        )
        self.canvas.pack()

        # Панель счета
        self.score_label = self.canvas.create_text(
            10, 10,
            text="Score: 0 | Speed: 1.0x",
            anchor="nw",
            fill="white",
            font=("Arial", 12)
        )

        self.reset_game()
        self.setup_controls()
        self.update()

    def reset_game(self):
        """Сброс игры в начальное состояние"""
        self.snake = [(self.GRID_HEIGHT // 2, self.GRID_WIDTH // 2)]
        self.direction = (0, 1)  # начальное направление: вправо
        self.next_direction = self.direction
        self.score = 0
        self.game_speed = self.GAME_SPEED
        self.game_over = False
        self.generate_food()

    def generate_food(self):
        """Генерация еды в случайной позиции"""
        while True:
            self.food = (
                random.randint(0, self.GRID_HEIGHT - 1),
                random.randint(0, self.GRID_WIDTH - 1)
            )
            if self.food not in self.snake:
                break

    def setup_controls(self):
        """Настройка управления"""
        self.window.bind('<Up>', lambda e: self.change_direction((-1, 0)))
        self.window.bind('<Down>', lambda e: self.change_direction((1, 0)))
        self.window.bind('<Left>', lambda e: self.change_direction((0, -1)))
        self.window.bind('<Right>', lambda e: self.change_direction((0, 1)))
        self.window.bind('<w>', lambda e: self.change_direction((-1, 0)))
        self.window.bind('<s>', lambda e: self.change_direction((1, 0)))
        self.window.bind('<a>', lambda e: self.change_direction((0, -1)))
        self.window.bind('<d>', lambda e: self.change_direction((0, 1)))
        self.window.bind('<r>', lambda e: self.reset_game())
        self.window.focus_set()

    def change_direction(self, new_dir):
        """Изменение направления с проверкой на противоположное"""
        opposite_dir = (new_dir[0] * -1, new_dir[1] * -1)
        if opposite_dir != self.direction:
            self.next_direction = new_dir

    def move_snake(self):
        """Движение змейки"""
        if self.game_over:
            return False

        # Обновляем направление
        self.direction = self.next_direction

        # Вычисляем новую позицию головы
        head = self.snake[0]
        new_head = (
            (head[0] + self.direction[0]) % self.GRID_HEIGHT,
            (head[1] + self.direction[1]) % self.GRID_WIDTH
        )

        # Проверка столкновения с собой
        if new_head in self.snake:
            self.game_over = True
            return False

        # Добавляем новую голову
        self.snake.insert(0, new_head)

        # Проверка съедания еды
        if new_head == self.food:
            self.score += 1
            # Увеличиваем скорость (уменьшаем интервал)
            self.game_speed = max(50, self.GAME_SPEED - (self.score * 10))
            self.generate_food()
        else:
            # Удаляем хвост, если не съели еду
            self.snake.pop()

        return True

    def draw(self):
        """Отрисовка игрового поля"""
        self.canvas.delete("all")

        # Рисуем панель счета
        speed_multiplier = self.GAME_SPEED / self.game_speed
        self.canvas.create_text(
            10, 10,
            text=f"Score: {self.score} | Speed: {speed_multiplier:.1f}x",
            anchor="nw",
            fill="white",
            font=("Arial", 12, "bold")
        )

        # Рисуем змейку
        for i, (row, col) in enumerate(self.snake):
            x1 = col * self.CELL_SIZE
            y1 = row * self.CELL_SIZE + 40  # +40 для смещения под панель счета
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE

            if i == 0:  # Голова
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#4CAF50",  # Зеленый
                    outline="#2E7D32",
                    width=2
                )
            else:  # Тело
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#8BC34A",  # Светло-зеленый
                    outline="#2E7D32",
                    width=1
                )

        # Рисуем еду
        food_x1 = self.food[1] * self.CELL_SIZE
        food_y1 = self.food[0] * self.CELL_SIZE + 40
        food_x2 = food_x1 + self.CELL_SIZE
        food_y2 = food_y1 + self.CELL_SIZE

        self.canvas.create_oval(
            food_x1, food_y1, food_x2, food_y2,
            fill="#FF5252",  # Красный
            outline="#D32F2F",
            width=2
        )

        # Рисуем сетку (опционально)
        for i in range(self.GRID_HEIGHT):
            for j in range(self.GRID_WIDTH):
                x1 = j * self.CELL_SIZE
                y1 = i * self.CELL_SIZE + 40
                self.canvas.create_rectangle(
                    x1, y1, x1 + self.CELL_SIZE, y1 + self.CELL_SIZE,
                    outline="#333333",
                    width=1
                )

        # Сообщение о Game Over
        if self.game_over:
            self.canvas.create_text(
                self.GRID_WIDTH * self.CELL_SIZE // 2,
                self.GRID_HEIGHT * self.CELL_SIZE // 2 + 40,
                text="GAME OVER!\nPress R to restart",
                fill="white",
                font=("Arial", 16, "bold"),
                justify="center"
            )

    def update(self):
        """Основной игровой цикл"""
        if not self.game_over:
            self.move_snake()

        self.draw()

        # Продолжаем игровой цикл
        self.window.after(self.game_speed, self.update)

    def run(self):
        """Запуск игры"""
        self.window.mainloop()


# Запуск игры
if __name__ == "__main__":
    game = SnakeGame()
    game.run()