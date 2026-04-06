import pygame
import random

# --- 1. INITIALIZATION ---
pygame.init()

# Define screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Brick Breaker")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Game settings
FPS = 60
SCORE = 0
LIVES = 3
FONT = pygame.font.Font(None, 36)  # Default font, size 36

# Clock for frame rate
CLOCK = pygame.time.Clock()


# --- 2. GAME OBJECT CLASSES ---

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 15
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        # Initial position
        self.rect.x = (WIDTH - self.width) // 2
        self.rect.y = HEIGHT - 40
        self.speed = 8

    def update(self):
        # Get mouse position
        pos = pygame.mouse.get_pos()
        # Set paddle center x to mouse x
        self.rect.x = pos[0] - self.width // 2

        # Keep paddle within screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH


class Ball(pygame.sprite.Sprite):
    def __init__(self, paddle_rect):
        super().__init__()
        self.radius = 8
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()

        # Start centered on the paddle
        self.rect.center = paddle_rect.center
        self.rect.y -= paddle_rect.height  # Move above the paddle

        self.speed = 5
        # Initial random direction (45 to 135 degrees, ensuring it moves up)
        angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
        self.dx = self.speed * math.cos(angle)
        self.dy = -self.speed * math.sin(angle)  # Negative for upward movement

        self.moving = False  # Control state: True after initial launch

    def launch(self):
        self.moving = True

    def update(self):
        if not self.moving:
            return

        # Move the ball
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Wall collision detection (left/right)
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.dx *= -1  # Reverse horizontal direction

        # Wall collision detection (top)
        if self.rect.top <= 0:
            self.dy *= -1  # Reverse vertical direction


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.width = 70
        self.height = 20
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(color)
        # Add a black border for definition
        pygame.draw.rect(self.image, BLACK, [0, 0, self.width, self.height], 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# --- 3. HELPER FUNCTIONS ---

def create_bricks():
    """Generates the initial layout of bricks."""
    bricks = pygame.sprite.Group()
    brick_colors = [RED, YELLOW, GREEN]
    rows = 5
    cols = WIDTH // 75  # Max columns that fit

    for row in range(rows):
        color = brick_colors[row % len(brick_colors)]
        for col in range(cols):
            x = col * 75 + 15
            y = row * 30 + 50
            brick = Brick(x, y, color)
            bricks.add(brick)
    return bricks


def display_info():
    """Draws the score and lives onto the screen."""
    score_text = FONT.render(f"Score: {SCORE}", True, WHITE)
    lives_text = FONT.render(f"Lives: {LIVES}", True, WHITE)

    SCREEN.blit(score_text, (10, 10))
    SCREEN.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))


def reset_ball(paddle):
    """Resets the ball to the center of the paddle."""
    global LIVES
    LIVES -= 1

    # If out of lives, end the game
    if LIVES <= 0:
        return False  # Signal game over

    # Otherwise, reset the ball position and state
    ball.rect.center = paddle.rect.center
    ball.rect.y -= paddle.rect.height
    ball.moving = False
    return True  # Signal game continues


def ball_paddle_collision(ball, paddle):
    """Handles collision between the ball and the paddle."""
    if pygame.sprite.collide_rect(ball, paddle) and ball.dy > 0:
        ball.dy *= -1  # Reverse vertical direction

        # Adjust horizontal direction based on where the ball hit the paddle
        hit_point = ball.rect.centerx - paddle.rect.centerx
        relative_position = hit_point / (paddle.width / 2)

        # Max angle change (e.g., up to 45 degrees offset)
        new_angle = relative_position * (math.pi / 4)

        # Calculate new horizontal velocity
        ball.dx = ball.speed * math.sin(new_angle)


def ball_brick_collision(ball, brick):
    """Handles collision between the ball and a single brick."""
    global SCORE

    # Remove the brick
    brick.kill()
    SCORE += 10

    # Basic bounce: always reverse vertical direction for simplicity
    ball.dy *= -1

    # For more complexity, you'd check which side of the brick was hit
    # and reverse dx or dy accordingly.


# --- 4. GAME OBJECT SETUP ---

# Create sprite groups
all_sprites = pygame.sprite.Group()
bricks = create_bricks()
all_sprites.add(bricks)

# Create paddle and ball
paddle = Paddle()
all_sprites.add(paddle)

# Use math import for trig functions in Ball class
import math

ball = Ball(paddle.rect)
all_sprites.add(ball)


# --- 5. MAIN GAME LOOP ---

def main():
    global LIVES
    running = True
    game_over = False

    while running:
        # --- A. Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Launch the ball on mouse click if it's not moving
            if event.type == pygame.MOUSEBUTTONDOWN and not ball.moving:
                ball.launch()

        # --- B. Game Logic (Only run if the game is not over) ---
        if not game_over:
            # 1. Update positions
            paddle.update()
            ball.update()

            # 2. Collision detection

            # Ball-Paddle collision
            ball_paddle_collision(ball, paddle)

            # Ball-Brick collision
            # Check for collision between the ball and ANY brick in the group
            hit_bricks = pygame.sprite.spritecollide(ball, bricks, False)  # False means don't remove immediately
            for brick in hit_bricks:
                ball_brick_collision(ball, brick)

            # 3. Check for Game State Changes

            # Check if ball fell off the bottom edge
            if ball.rect.top > HEIGHT:
                if not reset_ball(paddle):
                    game_over = True  # LIVES hit 0

            # Check for Win Condition (all bricks cleared)
            if not bricks:
                game_over = True  # Win condition

        # --- C. Drawing ---
        SCREEN.fill(BLACK)  # Clear screen

        all_sprites.draw(SCREEN)  # Draw all game objects

        display_info()  # Draw score and lives

        if game_over:
            if LIVES > 0:
                final_text = FONT.render("YOU WIN!", True, GREEN)
            else:
                final_text = FONT.render("GAME OVER", True, RED)

            text_rect = final_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            SCREEN.blit(final_text, text_rect)

        # --- D. Update Display and Clock ---
        pygame.display.flip()
        CLOCK.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()