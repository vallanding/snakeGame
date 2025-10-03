import random
import time
import tkinter as tk
import math


class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.window.resizable(False, False)

        # Увеличиваем размер поля
        self.CELL_SIZE = 25  # Чуть меньше ячейки чтобы поместилось на экране
        self.GRID_WIDTH = 30  # Шире!
        self.GRID_HEIGHT = 20  # Выше!
        self.GAME_SPEED = 150
        self.FPS = 60

        # Создание холста
        self.canvas = tk.Canvas(
            self.window,
            width=self.GRID_WIDTH * self.CELL_SIZE,
            height=self.GRID_HEIGHT * self.CELL_SIZE + 60,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.canvas.pack()

        # Переменные для плавной анимации
        self.animation_progress = 0
        self.last_head_position = None
        self.last_update_time = time.time()

        self.reset_game()
        self.setup_controls()
        self.update()

    def reset_game(self):
        """Сброс игры в начальное состояние"""
        # Стартуем ближе к центру
        self.snake = [(self.GRID_HEIGHT // 2, self.GRID_WIDTH // 2)]
        self.direction = (0, 1)
        self.next_direction = self.direction
        self.score = 0
        self.game_speed = self.GAME_SPEED
        self.game_over = False
        self.animation_progress = 0
        self.last_head_position = None
        self.last_update_time = time.time()
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
        self.window.bind('<space>', lambda e: self.reset_game())
        self.window.focus_set()

    def change_direction(self, new_dir):
        """Изменение направления с проверкой на противоположное"""
        if self.game_over:
            return

        opposite_dir = (new_dir[0] * -1, new_dir[1] * -1)
        if opposite_dir != self.direction:
            self.next_direction = new_dir

    def move_snake(self):
        """Движение змейки с проверкой столкновения со стенами"""
        if self.game_over:
            return False

        # Сохраняем позицию головы для анимации
        self.last_head_position = self.snake[0]

        # Обновляем направление
        self.direction = self.next_direction

        # Вычисляем новую позицию головы
        head = self.snake[0]
        new_head = (
            head[0] + self.direction[0],  # Убрал телепорт через границы
            head[1] + self.direction[1]
        )

        # ПРОВЕРКА СТОЛКНОВЕНИЯ СО СТЕНАМИ - Game Over!
        if (new_head[0] < 0 or new_head[0] >= self.GRID_HEIGHT or
                new_head[1] < 0 or new_head[1] >= self.GRID_WIDTH):
            self.game_over = True
            return False

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
            self.game_speed = max(50, self.GAME_SPEED - (self.score * 8))
            self.generate_food()
        else:
            # Удаляем хвост, если не съели еду
            self.snake.pop()

        return True

    def draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Рисует прямоугольник со скругленными углами"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def draw_walls(self):
        """Рисует границы поля"""
        wall_color = "#555555"
        wall_width = 3

        # Верхняя граница
        self.canvas.create_line(
            0, 40,
            self.GRID_WIDTH * self.CELL_SIZE, 40,
            fill=wall_color, width=wall_width
        )

        # Нижняя граница
        self.canvas.create_line(
            0, self.GRID_HEIGHT * self.CELL_SIZE + 40,
               self.GRID_WIDTH * self.CELL_SIZE, self.GRID_HEIGHT * self.CELL_SIZE + 40,
            fill=wall_color, width=wall_width
        )

        # Левая граница
        self.canvas.create_line(
            0, 40,
            0, self.GRID_HEIGHT * self.CELL_SIZE + 40,
            fill=wall_color, width=wall_width
        )

        # Правая граница
        self.canvas.create_line(
            self.GRID_WIDTH * self.CELL_SIZE, 40,
            self.GRID_WIDTH * self.CELL_SIZE, self.GRID_HEIGHT * self.CELL_SIZE + 40,
            fill=wall_color, width=wall_width
        )

    def draw_snake_segment(self, row, col, is_head=False, progress=1.0):
        """Рисует сегмент змейки с анимацией"""
        x1 = col * self.CELL_SIZE + 2
        y1 = row * self.CELL_SIZE + 40 + 2  # +40 для панели счета, +2 для отступа
        x2 = x1 + self.CELL_SIZE - 4
        y2 = y1 + self.CELL_SIZE - 4

        if is_head:
            # Анимированная голова
            if progress < 1.0 and self.last_head_position:
                old_row, old_col = self.last_head_position
                old_x1 = old_col * self.CELL_SIZE + 2
                old_y1 = old_row * self.CELL_SIZE + 42
                old_x2 = old_x1 + self.CELL_SIZE - 4
                old_y2 = old_y1 + self.CELL_SIZE - 4

                # Интерполяция позиции
                current_x1 = old_x1 + (x1 - old_x1) * progress
                current_y1 = old_y1 + (y1 - old_y1) * progress
                current_x2 = old_x2 + (x2 - old_x2) * progress
                current_y2 = old_y2 + (y2 - old_y2) * progress
            else:
                current_x1, current_y1, current_x2, current_y2 = x1, y1, x2, y2

            # Голова
            self.draw_rounded_rect(
                current_x1, current_y1, current_x2, current_y2, 5,
                fill="#4CAF50", outline="#2E7D32", width=2
            )

            # Глаза змейки
            eye_size = 2
            if self.direction == (0, 1):  # Вправо
                eye_x = current_x2 - 6
                eye_y1 = current_y1 + 6
                eye_y2 = current_y2 - 6
            elif self.direction == (0, -1):  # Влево
                eye_x = current_x1 + 6
                eye_y1 = current_y1 + 6
                eye_y2 = current_y2 - 6
            elif self.direction == (-1, 0):  # Вверх
                eye_x1 = current_x1 + 6
                eye_x2 = current_x2 - 6
                eye_y = current_y1 + 6
            else:  # Вниз
                eye_x1 = current_x1 + 6
                eye_x2 = current_x2 - 6
                eye_y = current_y2 - 6

            if self.direction[0] == 0:  # Горизонтальное движение
                self.canvas.create_oval(eye_x - eye_size, eye_y1 - eye_size,
                                        eye_x + eye_size, eye_y1 + eye_size,
                                        fill="#FFEB3B", outline="#FBC02D")
                self.canvas.create_oval(eye_x - eye_size, eye_y2 - eye_size,
                                        eye_x + eye_size, eye_y2 + eye_size,
                                        fill="#FFEB3B", outline="#FBC02D")
            else:  # Вертикальное движение
                self.canvas.create_oval(eye_x1 - eye_size, eye_y - eye_size,
                                        eye_x1 + eye_size, eye_y + eye_size,
                                        fill="#FFEB3B", outline="#FBC02D")
                self.canvas.create_oval(eye_x2 - eye_size, eye_y - eye_size,
                                        eye_x2 + eye_size, eye_y + eye_size,
                                        fill="#FFEB3B", outline="#FBC02D")

        else:
            # Тело
            self.draw_rounded_rect(
                x1, y1, x2, y2, 3,
                fill="#8BC34A", outline="#689F38", width=1
            )

    def draw_food(self):
        """Рисует анимированную еду"""
        food_x = self.food[1] * self.CELL_SIZE + self.CELL_SIZE // 2
        food_y = self.food[0] * self.CELL_SIZE + 40 + self.CELL_SIZE // 2
        food_radius = self.CELL_SIZE // 3

        # Пульсирующая анимация еды
        pulse = (math.sin(time.time() * 5) + 1) * 0.1 + 0.9
        current_radius = food_radius * pulse

        # Еда
        self.canvas.create_oval(
            food_x - current_radius, food_y - current_radius,
            food_x + current_radius, food_y + current_radius,
            fill="#FF5252", outline="#D32F2F", width=2
        )

    def draw_background(self):
        """Рисует фон с сеткой"""
        # Темный фон
        self.canvas.create_rectangle(
            0, 40, self.GRID_WIDTH * self.CELL_SIZE,
                   self.GRID_HEIGHT * self.CELL_SIZE + 40,
            fill="#1a1a1a", outline=""
        )

        # Сетка с тонкими линиями
        for i in range(self.GRID_HEIGHT + 1):
            y = i * self.CELL_SIZE + 40
            self.canvas.create_line(
                0, y, self.GRID_WIDTH * self.CELL_SIZE, y,
                fill="#333333", width=1
            )

        for j in range(self.GRID_WIDTH + 1):
            x = j * self.CELL_SIZE
            self.canvas.create_line(
                x, 40, x, self.GRID_HEIGHT * self.CELL_SIZE + 40,
                fill="#333333", width=1
            )

    def draw(self):
        """Отрисовка игрового поля"""
        self.canvas.delete("all")

        # Рисуем фон и стены
        self.draw_background()
        self.draw_walls()

        # Рисуем панель счета
        speed_multiplier = self.GAME_SPEED / self.game_speed
        self.canvas.create_rectangle(
            0, 0, self.GRID_WIDTH * self.CELL_SIZE, 40,
            fill="#2d2d2d", outline=""
        )

        self.canvas.create_text(
            self.GRID_WIDTH * self.CELL_SIZE // 2, 20,
            text=f"Score: {self.score} | Speed: {speed_multiplier:.1f}x | Field: {self.GRID_WIDTH}x{self.GRID_HEIGHT}",
            fill="#ffffff",
            font=("Arial", 12, "bold")
        )

        # Рисуем змейку с анимацией
        for i, (row, col) in enumerate(self.snake):
            is_head = (i == 0)
            progress = self.animation_progress if is_head else 1.0
            self.draw_snake_segment(row, col, is_head, progress)

        # Рисуем еду
        self.draw_food()

        # Сообщение о Game Over
        if self.game_over:
            # Полупрозрачный overlay
            self.canvas.create_rectangle(
                0, 40, self.GRID_WIDTH * self.CELL_SIZE,
                       self.GRID_HEIGHT * self.CELL_SIZE + 40,
                fill="#000000", stipple="gray50"
            )

            self.canvas.create_text(
                self.GRID_WIDTH * self.CELL_SIZE // 2,
                self.GRID_HEIGHT * self.CELL_SIZE // 2 + 20,
                text="GAME OVER",
                fill="#FF5252",
                font=("Arial", 24, "bold"),
                justify="center"
            )

            self.canvas.create_text(
                self.GRID_WIDTH * self.CELL_SIZE // 2,
                self.GRID_HEIGHT * self.CELL_SIZE // 2 + 60,
                text=f"Final Score: {self.score}",
                fill="#FFFFFF",
                font=("Arial", 16, "bold"),
                justify="center"
            )

            self.canvas.create_text(
                self.GRID_WIDTH * self.CELL_SIZE // 2,
                self.GRID_HEIGHT * self.CELL_SIZE // 2 + 90,
                text="Press SPACE or R to restart",
                fill="#CCCCCC",
                font=("Arial", 12),
                justify="center"
            )

    def update(self):
        """Основной игровой цикл с 60 FPS"""
        current_time = time.time()
        delta_time = current_time - self.last_update_time

        if not self.game_over:
            # Обновляем анимацию
            self.animation_progress += 0.15

            # Двигаем змейку по таймеру
            if delta_time * 1000 >= self.game_speed:
                if self.move_snake():
                    self.animation_progress = 0.0
                self.last_update_time = current_time

        # Всегда перерисовываем для 60 FPS
        self.draw()

        # 60 FPS (16.67 мс между кадрами)
        self.window.after(16, self.update)

    def run(self):
        """Запуск игры"""
        self.window.mainloop()


# Запуск игры
if __name__ == "__main__":
    game = SnakeGame()
    game.run()