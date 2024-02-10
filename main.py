import pygame
import random

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BIRD_SIZE = 20
PIPE_WIDTH = 70
PIPE_HEIGHT = 500
PIPE_GAP = 200
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_SPEED = 3
MENU_FONT_SIZE = 40
GAME_FONT_SIZE = 30

# Игрок (птица)
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((BIRD_SIZE, BIRD_SIZE))
        self.surf.fill((255, 255, 0))  # Желтый цвет
        self.rect = self.surf.get_rect(center=(50, SCREEN_HEIGHT // 2))
        self.vy = 0

    def update(self):
        self.vy += GRAVITY
        self.rect.move_ip(0, self.vy)
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def flap(self):
        self.vy = FLAP_STRENGTH

# Трубы
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, is_top):
        super().__init__()
        self.surf = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT))
        self.surf.fill((0, 255, 0))  # Зеленый цвет
        self.rect = self.surf.get_rect(topleft=(x, y))
        if is_top:
            self.surf = pygame.transform.flip(self.surf, False, True)
            self.rect.bottom = y

    def update(self):
        self.rect.move_ip(-PIPE_SPEED, 0)
        if self.rect.right < 0:
            self.kill()

# Класс Игры
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.menu_font = pygame.font.SysFont(None, MENU_FONT_SIZE)
        self.game_font = pygame.font.SysFont(None, GAME_FONT_SIZE)
        self.score = 0
        self.high_score = self.load_high_score()
        self.reset_game()

    def reset_game(self):
        self.bird = Bird()
        self.pipes = pygame.sprite.Group()
        self.spawn_pipe_timer = 0
        self.score = 0
        self.running = True
        self.in_menu = True
        self.passed_pipe = False

    def load_high_score(self):
        try:
            with open('record.txt', 'r') as f:
                return int(f.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        with open('record.txt', 'w') as f:
            f.write(str(self.high_score))

    def show_menu(self):
        self.screen.fill((135, 206, 250))  # Светло-голубой фон
        menu_text = self.menu_font.render("Нажмите Пробел, чтобы начать", True, (0, 0, 0))
        high_score_text = self.game_font.render(f"Рекорд: {self.high_score}", True, (0, 0, 0))
        self.screen.blit(menu_text, (50, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(high_score_text, (50, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()

    def run(self):
        while self.running:
            if self.in_menu:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.in_menu = False
                self.show_menu()
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.bird.flap()

            self.screen.fill((111, 176, 255))  # Светло-голубой фон

            # Обновление
            self.bird.update()
            self.pipes.update()

            # Рисование
            self.screen.blit(self.bird.surf, self.bird.rect)
            for pipe in self.pipes:
                self.screen.blit(pipe.surf, pipe.rect)

            # Генерация труб
            self.spawn_pipe_timer += 1
            if self.spawn_pipe_timer > 90:
                self.spawn_pipe_timer = 0
                gap_y = random.randint(100, SCREEN_HEIGHT - 300)
                top_pipe = Pipe(SCREEN_WIDTH, gap_y - PIPE_GAP, True)
                bottom_pipe = Pipe(SCREEN_WIDTH, gap_y, False)
                self.pipes.add(top_pipe, bottom_pipe)
                self.passed_pipe = False

            # Проверка столкновений и увеличение счета
            if pygame.sprite.spritecollideany(self.bird, self.pipes):
                # Округляем счет до ближайшего целого числа перед сравнением и сохранением
                rounded_score = int(round(self.score))
                if rounded_score > self.high_score:
                    self.high_score = rounded_score
                    self.save_high_score()
                self.reset_game()
            else:
                for pipe in self.pipes:
                    if pipe.rect.right < self.bird.rect.left and not self.passed_pipe:
                        self.score += 1  # Увеличиваем на 1 для каждой трубы (всего будет +1 за пару)
                        self.passed_pipe = True

            # Отображение счета
            score_text = self.game_font.render(str(int(self.score)), True, (255, 255, 255))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2, 20))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
