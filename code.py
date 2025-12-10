import pygame
import sys
import random
import time

# инициализация PyGame
pygame.init()

# константы игры
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 60

# цвета по умолчанию 
BACKGROUND_COLOR = (10, 20, 30)
GRID_COLOR = (30, 40, 50)
SNAKE_COLOR = (15, 206, 124)
SNAKE_HEAD_COLOR = (20, 230, 140)
APPLE_COLOR = (220, 60, 60)
BAD_FOOD_COLOR = (255, 165, 0)
STONE_COLOR = (120, 120, 120)
TEXT_COLOR = (220, 220, 220)
GAME_OVER_COLOR = (220, 60, 60)

# направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # начальная позиция змейки
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.score = 0
        self.grow_pending = 2  # начальная длина 3 сегмента
        
    def get_head_position(self):
        return self.positions[0]
    
    def turn(self, direction):
        # проверка, чтобы змейка не могла развернуться на 180 градусов
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def move(self):
        head = self.get_head_position()
        x, y = self.direction
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_position = (new_x, new_y)
        
        # проверка на столкновение с собой
        if new_position in self.positions[1:]:
            return False  # столкновение
            
        self.positions.insert(0, new_position)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
            
        return True  # успешное движение
    
    def grow(self):
        self.grow_pending += 1
        self.score += 10
        
    def shrink(self):
        if len(self.positions) > 1:
            self.positions.pop()
            self.score = max(0, self.score - 5)
    
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            rect = pygame.Rect(
                pos[0] * GRID_SIZE, 
                pos[1] * GRID_SIZE, 
                GRID_SIZE, 
                GRID_SIZE
            )
            
            # голова змейки другого цвета
            if i == 0:
                pygame.draw.rect(surface, SNAKE_HEAD_COLOR, rect)
                pygame.draw.rect(surface, (255, 255, 255), rect, 1)
            else:
                pygame.draw.rect(surface, SNAKE_COLOR, rect)
                pygame.draw.rect(surface, (255, 255, 255), rect, 1)
                
            # глаза у головы змейки
            if i == 0:
                eye_size = GRID_SIZE // 5
                # левый глаз
                left_eye_x = pos[0] * GRID_SIZE + GRID_SIZE // 4
                right_eye_x = pos[0] * GRID_SIZE + 3 * GRID_SIZE // 4
                eye_y = pos[1] * GRID_SIZE + GRID_SIZE // 3
                
                # определяем направление глаз
                if self.direction == RIGHT:
                    left_eye_x = pos[0] * GRID_SIZE + 3 * GRID_SIZE // 4
                    right_eye_x = pos[0] * GRID_SIZE + 3 * GRID_SIZE // 4
                    eye_y = pos[1] * GRID_SIZE + GRID_SIZE // 3
                elif self.direction == LEFT:
                    left_eye_x = pos[0] * GRID_SIZE + GRID_SIZE // 4
                    right_eye_x = pos[0] * GRID_SIZE + GRID_SIZE // 4
                    eye_y = pos[1] * GRID_SIZE + GRID_SIZE // 3
                elif self.direction == UP:
                    left_eye_x = pos[0] * GRID_SIZE + GRID_SIZE // 4
                    right_eye_x = pos[0] * GRID_SIZE + 3 * GRID_SIZE // 4
                    eye_y = pos[1] * GRID_SIZE + GRID_SIZE // 4
                elif self.direction == DOWN:
                    left_eye_x = pos[0] * GRID_SIZE + GRID_SIZE // 4
                    right_eye_x = pos[0] * GRID_SIZE + 3 * GRID_SIZE // 4
                    eye_y = pos[1] * GRID_SIZE + 3 * GRID_SIZE // 4
                
                pygame.draw.circle(surface, (0, 0, 0), (left_eye_x, eye_y), eye_size)
                pygame.draw.circle(surface, (0, 0, 0), (right_eye_x, eye_y), eye_size)

class Food:
    def __init__(self, is_bad=False):
        self.position = (0, 0)
        self.is_bad = is_bad
        self.randomize_position()
        
    def randomize_position(self, snake_positions=None, stone_positions=None):
        if snake_positions is None:
            snake_positions = []
        if stone_positions is None:
            stone_positions = []
            
        # пытаемся найти свободную позицию
        attempts = 0
        while attempts < 100:  # ограничиваем количество попыток
            self.position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            
            # проверяем, что еда не появится на змейке или камне
            if (self.position not in snake_positions and 
                self.position not in stone_positions):
                return
                
            attempts += 1
            
        # если не нашли свободную позицию, ставим в угол
        self.position = (0, 0)
    
    def draw(self, surface):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        
        if self.is_bad:
            # неправильная еда - оранжевый треугольник
            points = [
                (rect.centerx, rect.top + 3),
                (rect.left + 3, rect.bottom - 3),
                (rect.right - 3, rect.bottom - 3)
            ]
            pygame.draw.polygon(surface, BAD_FOOD_COLOR, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 1)
        else:
            # обычное яблоко - красный круг с зеленым листиком
            pygame.draw.circle(surface, APPLE_COLOR, rect.center, GRID_SIZE // 2 - 2)
            pygame.draw.circle(surface, (255, 255, 255), rect.center, GRID_SIZE // 2 - 2, 1)
            
            # листик
            leaf_rect = pygame.Rect(
                rect.centerx - 2,
                rect.top + 2,
                GRID_SIZE // 3,
                GRID_SIZE // 3
            )
            pygame.draw.ellipse(surface, (50, 200, 50), leaf_rect)

class Stone:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self, snake_positions=None, food_positions=None):
        if snake_positions is None:
            snake_positions = []
        if food_positions is None:
            food_positions = []
            
        # пытаемся найти свободную позицию
        attempts = 0
        while attempts < 100:  # ограничиваем количество попыток
            self.position = (
                random.randint(2, GRID_WIDTH - 3),
                random.randint(2, GRID_HEIGHT - 3)
            )
            
            # проверяем, что камень не появится на змейке или еде
            if (self.position not in snake_positions and 
                self.position not in food_positions):
                return
                
            attempts += 1
            
        # если не нашли свободную позицию, ставим в угол
        self.position = (5, 5)
    
    def draw(self, surface):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        
        # рисуем камень - серый квадрат с текстурой
        pygame.draw.rect(surface, STONE_COLOR, rect)
        
        # добавляем текстуру камня
        pygame.draw.line(surface, (100, 100, 100), 
                         rect.topleft, rect.bottomright, 1)
        pygame.draw.line(surface, (150, 150, 150), 
                         rect.topright, rect.bottomleft, 1)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Змейка с дополнительными возможностями")
        self.clock = pygame.time.Clock()
        
        # настройки игры (можно менять)
        self.speed = 10  # скорость змейки (обновлений в секунду)
        self.enable_bad_food = True  # включить неправильную еду
        self.enable_stones = True  # включить камни
        self.bad_food_probability = 0.2  # вероятность появления плохой еды (20%)
        self.stone_probability = 0.1  # вероятность появления камня (10%)
        
        # Игровые объекты
        self.snake = Snake()
        self.foods = []  # список всей еды (хорошей и плохой)
        self.stones = []  # список камней
        self.game_over = False
        self.paused = False
        
        # таймеры
        self.food_timer = 0
        self.stone_timer = 0
        
        # шрифты
        self.font = pygame.font.SysFont('arial', 24)
        self.big_font = pygame.font.SysFont('arial', 48)
        
        # создаем первую еду
        self.add_food()
        
        # создаем первый камень, если включены
        if self.enable_stones and random.random() < self.stone_probability:
            self.add_stone()
    
    def add_food(self):
        # определяем, будет ли еда плохой
        is_bad = False
        if self.enable_bad_food and random.random() < self.bad_food_probability:
            is_bad = True
            
        # получаем позиции всех объектов для проверки коллизий
        snake_positions = self.snake.positions
        stone_positions = [stone.position for stone in self.stones]
        food_positions = [food.position for food in self.foods]
        
        # создаем еду
        food = Food(is_bad)
        food.randomize_position(snake_positions, stone_positions + food_positions)
        self.foods.append(food)
    
    def add_stone(self):
        # получаем позиции всех объектов для проверки коллизий
        snake_positions = self.snake.positions
        food_positions = [food.position for food in self.foods]
        
        # создаем камень
        stone = Stone()
        stone.randomize_position(snake_positions, food_positions)
        self.stones.append(stone)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                # управление змейкой
                if not self.paused and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.snake.turn(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.turn(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.turn(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.turn(RIGHT)
                
                # пауза
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                
                # рестарт игры
                if event.key == pygame.K_r:
                    self.reset_game()
                
                # выход
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                # настройки (для демонстрации)
                if event.key == pygame.K_1:
                    self.speed = max(5, self.speed - 2)  # Уменьшаем скорость
                if event.key == pygame.K_2:
                    self.speed = min(20, self.speed + 2)  # Увеличиваем скорость
                if event.key == pygame.K_3:
                    self.enable_bad_food = not self.enable_bad_food  # Вкл/выкл плохую еду
                if event.key == pygame.K_4:
                    self.enable_stones = not self.enable_stones  # Вкл/выкл камни
    
    def update(self):
        if self.paused or self.game_over:
            return
            
        # двигаем змейку
        if not self.snake.move():
            self.game_over = True
            return
            
        # проверяем столкновение с камнями
        head = self.snake.get_head_position()
        for stone in self.stones:
            if head == stone.position:
                self.game_over = True
                return
        
        # проверяем столкновение с едой
        for food in self.foods[:]:  # используем копию списка для безопасного удаления
            if head == food.position:
                if food.is_bad:
                    # плохая еда уменьшает змейку
                    self.snake.shrink()
                else:
                    # хорошая еда увеличивает змейку
                    self.snake.grow()
                
                # удаляем съеденную еду
                self.foods.remove(food)
                # добавляем новую еду
                self.add_food()
                
                # с вероятностью добавляем камень
                if self.enable_stones and random.random() < self.stone_probability:
                    self.add_stone()
        
        # периодически добавляем еду (чтобы она не кончалась)
        self.food_timer += 1
        if self.food_timer > 100:  # каждые 100 кадров
            if len(self.foods) < 3:  # если еды меньше 3
                self.add_food()
            self.food_timer = 0
    
    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y), 1)
    
    def draw_ui(self):
        # счет
        score_text = self.font.render(f"Счет: {self.snake.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        
        # длина змейки
        length_text = self.font.render(f"Длина: {len(self.snake.positions)}", True, TEXT_COLOR)
        self.screen.blit(length_text, (10, 40))
        
        # скорость
        speed_text = self.font.render(f"Скорость: {self.speed}", True, TEXT_COLOR)
        self.screen.blit(speed_text, (10, 70))
        
        # настройки
        settings_text = self.font.render(
            f"Плохая еда: {'ВКЛ' if self.enable_bad_food else 'ВЫКЛ'}, "
            f"Камни: {'ВКЛ' if self.enable_stones else 'ВЫКЛ'}",
            True, TEXT_COLOR
        )
        self.screen.blit(settings_text, (10, HEIGHT - 40))
        
        # управление
        controls_text = self.font.render(
            "Управление: Стрелки, P-пауза, R-рестарт, ESC-выход", 
            True, TEXT_COLOR
        )
        self.screen.blit(controls_text, (10, HEIGHT - 70))
        
        # настройки скорости
        speed_controls = self.font.render(
            "1-медленнее, 2-быстрее, 3-плохая еда вкл/выкл, 4-камни вкл/выкл", 
            True, TEXT_COLOR
        )
        self.screen.blit(speed_controls, (10, HEIGHT - 100))
        
        # легенда
        legend_y = HEIGHT - 180
        pygame.draw.rect(self.screen, SNAKE_HEAD_COLOR, (WIDTH - 180, legend_y, 20, 20))
        legend_text = self.font.render("- голова змейки", True, TEXT_COLOR)
        self.screen.blit(legend_text, (WIDTH - 150, legend_y))
        
        pygame.draw.rect(self.screen, APPLE_COLOR, (WIDTH - 180, legend_y + 30, 20, 20))
        legend_text = self.font.render("- хорошая еда (+10)", True, TEXT_COLOR)
        self.screen.blit(legend_text, (WIDTH - 150, legend_y + 30))
        
        pygame.draw.rect(self.screen, BAD_FOOD_COLOR, (WIDTH - 180, legend_y + 60, 20, 20))
        legend_text = self.font.render("- плохая еда (-5, -1 сегмент)", True, TEXT_COLOR)
        self.screen.blit(legend_text, (WIDTH - 150, legend_y + 60))
        
        pygame.draw.rect(self.screen, STONE_COLOR, (WIDTH - 180, legend_y + 90, 20, 20))
        legend_text = self.font.render("- камень (смерть)", True, TEXT_COLOR)
        self.screen.blit(legend_text, (WIDTH - 150, legend_y + 90))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # полупрозрачный черный
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("ИГРА ОКОНЧЕНА", True, GAME_OVER_COLOR)
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        
        score_text = self.font.render(f"Ваш счет: {self.snake.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 20))
        
        restart_text = self.font.render("Нажмите R для перезапуска или ESC для выхода", True, TEXT_COLOR)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 70))
    
    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  # полупрозрачный черный
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.big_font.render("ПАУЗА", True, TEXT_COLOR)
        self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
        
        continue_text = self.font.render("Нажмите P для продолжения", True, TEXT_COLOR)
        self.screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 20))
    
    def reset_game(self):
        self.snake.reset()
        self.foods = []
        self.stones = []
        self.game_over = False
        self.paused = False
        
        # создаем первую еду
        self.add_food()
        
        # создаем первый камень, если включены
        if self.enable_stones and random.random() < self.stone_probability:
            self.add_stone()
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # рисуем сетку
        self.draw_grid()
        
        # рисуем камни
        for stone in self.stones:
            stone.draw(self.screen)
        
        # рисуем еду
        for food in self.foods:
            food.draw(self.screen)
        
        # рисуем змейку
        self.snake.draw(self.screen)
        
        # рисуем интерфейс
        self.draw_ui()
        
        # рисуем экран окончания игры или паузы
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
        
        pygame.display.flip()
    
    def run(self):
        last_update_time = time.time()
        
        while True:
            self.handle_events()
            
            # ограничиваем обновление игры для контроля скорости
            current_time = time.time()
            if current_time - last_update_time >= 1.0 / self.speed:
                self.update()
                last_update_time = current_time
            
            self.draw()
            self.clock.tick(FPS)

# запуск игры
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        pygame.quit()
