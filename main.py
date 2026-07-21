import pygame
import sys

pygame.init()

WIDTH = 720
HEIGHT = 1280
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 28)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 120, 15)
        self.target_x = x
        self.speed = 8
    
    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)
    
    def update(self):
        if abs(self.rect.centerx - self.target_x) > self.speed:
            if self.rect.centerx < self.target_x:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
        else:
            self.rect.centerx = self.target_x
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
    
    def move_to(self, x):
        self.target_x = max(60, min(x, WIDTH - 60))

class Ball:
    def __init__(self):
        self.x = WIDTH / 2.0
        self.y = HEIGHT / 2.0
        self.radius = 10
        self.base_speed = 5
        self.vx = self.base_speed
        self.vy = self.base_speed
        self.last_y = self.y
    
    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius)
    
    def check_score(self):
        if self.y < 0 and self.last_y >= 0:
            return 2
        if self.y > HEIGHT and self.last_y <= HEIGHT:
            return 1
        return 0
    
    def update(self, paddle1, paddle2):
        self.last_y = self.y
        self.x += self.vx
        self.y += self.vy
        
        # Rebote en paleta superior
        if self.vy < 0 and self.y - self.radius <= paddle1.rect.bottom and self.y - self.radius >= paddle1.rect.top and self.x >= paddle1.rect.left and self.x <= paddle1.rect.right:
            self.vy = abs(self.vy)
            hit_pos = (self.x - paddle1.rect.centerx) / (paddle1.rect.width / 2.0)
            self.vx = self.base_speed * 1.5 * hit_pos
            self.y = paddle1.rect.bottom + self.radius
        
        # Rebote en paleta inferior
        if self.vy > 0 and self.y + self.radius >= paddle2.rect.top and self.y + self.radius <= paddle2.rect.bottom and self.x >= paddle2.rect.left and self.x <= paddle2.rect.right:
            self.vy = -abs(self.vy)
            hit_pos = (self.x - paddle2.rect.centerx) / (paddle2.rect.width / 2.0)
            self.vx = self.base_speed * 1.5 * hit_pos
            self.y = paddle2.rect.top - self.radius
        
        # Rebote en paredes laterales
        if self.x - self.radius <= 0:
            self.vx = abs(self.vx)
            self.x = self.radius
        if self.x + self.radius >= WIDTH:
            self.vx = -abs(self.vx)
            self.x = WIDTH - self.radius
    
    def reset(self):
        self.x = WIDTH / 2.0
        self.y = HEIGHT / 2.0
        self.vx = self.base_speed
        self.vy = self.base_speed
        self.last_y = self.y
    
    def set_speed(self, speed):
        if speed > 10:
            self.base_speed = 1
        else:
            self.base_speed = max(1, min(speed, 10))

def main():
    paddle1 = Paddle(WIDTH // 2 - 60, 50)
    paddle2 = Paddle(WIDTH // 2 - 60, HEIGHT - 65)
    ball = Ball()
    
    score1 = 0
    score2 = 0
    game_running = True
    
    touches = {}
    
    while game_running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                if mouse_y < HEIGHT // 2:
                    paddle1.move_to(mouse_x)
                else:
                    paddle2.move_to(mouse_x)
            
            if event.type == pygame.FINGERDOWN:
                touch_id = event.finger_id
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                touches[touch_id] = (touch_x, touch_y)
                
                if touch_y < HEIGHT // 2:
                    paddle1.move_to(touch_x)
                else:
                    paddle2.move_to(touch_x)
            
            if event.type == pygame.FINGERMOTION:
                touch_id = event.finger_id
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                touches[touch_id] = (touch_x, touch_y)
                
                if touch_y < HEIGHT // 2:
                    paddle1.move_to(touch_x)
                else:
                    paddle2.move_to(touch_x)
            
            if event.type == pygame.FINGERUP:
                touch_id = event.finger_id
                if touch_id in touches:
                    del touches[touch_id]
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_running = False
                if event.key == pygame.K_SPACE:
                    ball.reset()
                    score1 = 0
                    score2 = 0
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    ball.set_speed(ball.base_speed + 1)
                if event.key == pygame.K_MINUS:
                    ball.set_speed(ball.base_speed - 1)
        
        paddle1.update()
        paddle2.update()
        ball.update(paddle1, paddle2)
        
        score = ball.check_score()
        if score == 1:
            score1 += 1
            ball.reset()
        elif score == 2:
            score2 += 1
            ball.reset()
        
        screen.fill(BLACK)
        
        for y in range(0, HEIGHT, 30):
            pygame.draw.line(screen, GRAY, (WIDTH // 2 - 10, y), (WIDTH // 2 + 10, y), 1)
        
        paddle1.draw(screen)
        paddle2.draw(screen)
        ball.draw(screen)
        
        score_text = font.render(f"{score1}  |  {score2}", True, WHITE)
        
        score_surf = pygame.Surface((180, 80))
        score_surf.set_colorkey(BLACK)
        score_surf.fill(BLACK)
        score_surf.set_alpha(180)
        score_surf.blit(score_text, (10, 10))
        screen.blit(score_surf, (WIDTH - 190, HEIGHT - 90))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()