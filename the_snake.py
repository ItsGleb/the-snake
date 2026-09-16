from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки:
BORDER_COLOR = (93, 216, 228)

# Цвет яблока:
APPLE_COLOR = (255, 0, 0)

# Цвет змейки:
SNAKE_COLOR = (0, 255, 0)

# Цвет по умолчанию:
DEFAULT_COLOR = (255, 255, 255)

# Скорость движения змейки:
SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 40
SPEED_STEP = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption(
    f'Змейка. Для выхода из игры нажмите на кнопку Х '
    f'(скорость: {SPEED})'
)
# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=DEFAULT_COLOR):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.body_color = body_color

    def draw(self):
        """Отрисовка объекта. Переопределяется в наследниках."""


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, body_color=APPLE_COLOR, snake_positions=None):
        super().__init__(body_color)
        self.randomize_position(snake_positions or [])  # Позиция яблочка

    def randomize_position(self, snake_positions):
        """Возвращает случайную свободную позицию на поле."""
        occupied = set(snake_positions)
        while True:
            self.position = (
                choice(range(GRID_WIDTH)) * GRID_SIZE,
                choice(range(GRID_HEIGHT)) * GRID_SIZE,
            )
            if self.position not in occupied:
                break

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()
        self.direction = RIGHT

    def reset(self):
        """Сброс змейки в начальное состояние."""
        self.positions = [self.position]
        self.length = 1
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Двигает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        delta_x, delta_y = self.direction
        self.position = (
            (head_x + delta_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + delta_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, self.position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def update_direction(self):
        """Применяет отложенное направление."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает все сегменты змейки и затирает хвост."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object, speed):
    """Обработка действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            # Логика управления движением
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            # Логика управления скоростью
            elif event.key in (pg.K_PLUS, pg.K_EQUALS, pg.K_KP_PLUS):
                speed = min(speed + SPEED_STEP, MAX_SPEED)
            elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                speed = max(speed - SPEED_STEP, MIN_SPEED)
    return speed


def main():
    """Точка входа: запускает игровой цикл."""
    pg.init()

    snake = Snake(SNAKE_COLOR)
    apple = Apple(APPLE_COLOR, snake.positions)
    speed = SPEED

    # Очищаем экран один раз при запуске игры
    screen.fill(BOARD_BACKGROUND_COLOR)
    while True:
        clock.tick(speed)
        speed = handle_keys(snake, speed)
        pg.display.set_caption(
            f'Змейка. Для выхода из игры нажмите на кнопку Х '
            f'(скорость: {speed})'
        )
        snake.update_direction()

        # Победа: змейка заполнила всё поле
        if snake.length >= GRID_WIDTH * GRID_HEIGHT:
            pg.quit()
            raise SystemExit

        snake.move()
        # Проверяем, съест ли змейка яблоко на следующем шаге
        if snake.get_head_position() == apple.position:
            snake.length += 1
            # Победа: змейка заполнила всё поле
            if snake.length >= GRID_WIDTH * GRID_HEIGHT:
                pg.quit()
                raise SystemExit
            apple.randomize_position(snake.positions)
        # Если не съела — проверяем столкновение с собой
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
