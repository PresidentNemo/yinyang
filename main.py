import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Energy Field Game")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)

BALL_RADIUS = 20
INITIAL_MAX_DISTANCE = 300
MIN_MAX_DISTANCE = 150
MIN_DISTANCE = BALL_RADIUS * 2

BASE_AI_SPEED = 2.0
MAX_SPEED_MULTIPLIER = 5
DISTANCE_SHRINK_DURATION = 120  # seconds

# Load and scale background image
background = pygame.image.load("yin_yang_background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

def reset_game():
    angle = random.uniform(0, 2 * math.pi)
    angle_velocity = random.uniform(-1, 1)
    # Initial random delay with quicker switches possible
    if random.random() < 0.4:
        next_switch_delay = random.randint(1000, 3000)
    else:
        next_switch_delay = random.randint(3000, 8000)

    return (pygame.Vector2(WIDTH // 2, HEIGHT // 2 - 50),   # player_pos
            pygame.Vector2(WIDTH // 2, HEIGHT // 2 + 50),   # ai_pos
            pygame.Vector2(math.cos(angle), math.sin(angle)),  # ai_velocity
            angle, angle_velocity,
            True,  # player_lead
            pygame.time.get_ticks(),  # last_switch_time
            pygame.time.get_ticks(),  # game_start_time
            False,  # game_started
            0.0,    # points
            next_switch_delay)

def move_ai_smooth(pos, velocity, speed, ai_angle, angle_velocity, dt):
    ai_angle += angle_velocity * dt
    angle_velocity += random.uniform(-0.5, 0.5) * dt
    angle_velocity = max(min(angle_velocity, 1.5), -1.5)

    velocity = pygame.Vector2(math.cos(ai_angle), math.sin(ai_angle)) * speed
    new_pos = pos + velocity

    if new_pos.x < BALL_RADIUS or new_pos.x > WIDTH - BALL_RADIUS:
        angle_velocity = -angle_velocity
        ai_angle = math.pi - ai_angle
    if new_pos.y < BALL_RADIUS or new_pos.y > HEIGHT - BALL_RADIUS:
        angle_velocity = -angle_velocity
        ai_angle = -ai_angle

    return new_pos, velocity, ai_angle, angle_velocity

def check_game_over(pos1, pos2, max_distance):
    distance = pos1.distance_to(pos2)
    if distance < MIN_DISTANCE:
        return True, "Balls touched! Game Over."
    if distance > max_distance:
        return True, "Balls too far apart! Game Over."
    return False, ""

def draw_ball(pos, color):
    pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), BALL_RADIUS)

def draw_energy_field_fading(pos1, pos2, max_distance):
    distance = pos1.distance_to(pos2)
    clamped_dist = min(distance, max_distance)
    base_alpha = int(255 * (1 - clamped_dist / max_distance))
    if base_alpha <= 0:
        return

    length = int(distance)
    angle = math.atan2(pos2.y - pos1.y, pos2.x - pos1.x)

    line_surf = pygame.Surface((length + 20, 20), pygame.SRCALPHA)
    gold = (255, 215, 0)

    for i, alpha_factor in enumerate([0.2, 0.4, 0.7, 1.0]):
        alpha = int(base_alpha * alpha_factor)
        color = (gold[0], gold[1], gold[2], alpha)
        thickness = 2 + i * 2
        pygame.draw.rect(line_surf, color, (10, 10 - thickness // 2, length, thickness), border_radius=thickness//2)

    rotated_surf = pygame.transform.rotate(line_surf, -math.degrees(angle))
    rect = rotated_surf.get_rect(center=((pos1.x + pos2.x) / 2, (pos1.y + pos2.y) / 2))
    screen.blit(rotated_surf, rect.topleft)

(player_pos, ai_pos, ai_velocity, ai_angle, angle_velocity,
 player_lead, last_switch_time, game_start_time,
 game_started, points, next_switch_delay) = reset_game()

game_over = False
game_over_message = ""

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 24)

running = True
while running:
    dt = clock.tick(60) / 1000.0

    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION and not game_started:
            game_started = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                (player_pos, ai_pos, ai_velocity, ai_angle, angle_velocity,
                 player_lead, last_switch_time, game_start_time,
                 game_started, points, next_switch_delay) = reset_game()
                game_over = False
                game_over_message = ""

    if not game_started:
        start_msg = font.render("Move your mouse to start", True, WHITE)
        screen.blit(start_msg, (WIDTH // 2 - start_msg.get_width() // 2, HEIGHT // 2 - start_msg.get_height() // 2))
        pygame.display.flip()
        continue

    if not game_over:
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - game_start_time) / 1000.0

        if elapsed_seconds < DISTANCE_SHRINK_DURATION:
            max_distance = INITIAL_MAX_DISTANCE - ((INITIAL_MAX_DISTANCE - MIN_MAX_DISTANCE) * (elapsed_seconds / DISTANCE_SHRINK_DURATION))
        else:
            max_distance = MIN_MAX_DISTANCE

        if current_time - last_switch_time > next_switch_delay:
            player_lead = not player_lead
            last_switch_time = current_time
            # 40% chance to switch quicker (1-3s), else normal (3-8s)
            if random.random() < 0.4:
                next_switch_delay = random.randint(1000, 3000)
            else:
                next_switch_delay = random.randint(3000, 8000)

        speed_multiplier = min(1 + elapsed_seconds / 20, MAX_SPEED_MULTIPLIER)
        ai_speed = BASE_AI_SPEED * speed_multiplier

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_pos.update(mouse_x, mouse_y)

        if player_lead:
            direction = player_pos - ai_pos
            dist = direction.length()
            if dist > 0:
                direction.scale_to_length(min(ai_speed, dist))
                ai_pos += direction
            lead_text = "Player Lead"
        else:
            ai_pos, ai_velocity, ai_angle, angle_velocity = move_ai_smooth(
                ai_pos, ai_velocity, ai_speed, ai_angle, angle_velocity, dt)
            lead_text = "AI Lead"

        points += speed_multiplier * dt * 10

        draw_energy_field_fading(player_pos, ai_pos, max_distance)
        draw_ball(player_pos, BLUE)
        draw_ball(ai_pos, RED)

        game_over, game_over_message = check_game_over(player_pos, ai_pos, max_distance)

        screen.blit(small_font.render(lead_text, True, WHITE), (10, 10))
        screen.blit(small_font.render(f"Points: {int(points)}", True, WHITE), (10, 35))
        screen.blit(small_font.render(f"Max Distance: {int(max_distance)}", True, WHITE), (10, 60))

    else:
        msg = font.render(game_over_message, True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height()))
        screen.blit(small_font.render("Press R to Restart", True, WHITE), (WIDTH // 2 - 80, HEIGHT // 2 + 10))
        screen.blit(small_font.render(f"Final Points: {int(points)}", True, WHITE), (WIDTH // 2 - 70, HEIGHT // 2 + 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
