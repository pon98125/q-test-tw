import pygame
import sys
import random
import time
import os

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
POOP_SIZE = 40
PLAYER_SPEED = 8
POOP_SPEED = 10  # 2x faster than original (was 5)
POOP_SPAWN_RATE = 20  # New poop every 20 frames (about 1/3 second)
MIN_ACTIVE_POOPS = 5  # Minimum number of active poops
MAX_ACTIVE_POOPS = 10  # Maximum number of active poops at once
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
RANKING_FILE = "ranking.txt"

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Poop Dodge Game")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

# Import math module for animation
import math

# We'll create custom poop and player images instead of downloading them
poop_image = None
player_image = None

class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = PLAYER_SPEED
        self.color = BLUE
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.direction = 0  # 0 = stationary, -1 = left, 1 = right
    
    def draw(self):
        # Create a running animation effect
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction = -1
            self.animation_frame += self.animation_speed
        elif keys[pygame.K_RIGHT]:
            self.direction = 1
            self.animation_frame += self.animation_speed
        else:
            self.direction = 0
            self.animation_frame = 0
        
        # Calculate animation offsets
        leg_offset = 5 * math.sin(self.animation_frame * 2) if self.direction != 0 else 0
        arm_offset = 5 * math.sin(self.animation_frame * 2 + math.pi) if self.direction != 0 else 0
        
        # Colors
        skin_color = (255, 218, 185)
        shirt_color = self.color
        pants_color = (0, 0, 128)  # Dark blue
        
        # Head
        head_size = self.width // 2.5
        head_x = self.x + self.width // 2
        head_y = self.y + head_size // 2
        pygame.draw.circle(screen, skin_color, (head_x, head_y), head_size // 2)
        
        # Eyes
        eye_size = head_size // 8
        pygame.draw.circle(screen, WHITE, (head_x - head_size // 4, head_y - head_size // 8), eye_size)
        pygame.draw.circle(screen, WHITE, (head_x + head_size // 4, head_y - head_size // 8), eye_size)
        pygame.draw.circle(screen, BLACK, (head_x - head_size // 4, head_y - head_size // 8), eye_size // 2)
        pygame.draw.circle(screen, BLACK, (head_x + head_size // 4, head_y - head_size // 8), eye_size // 2)
        
        # Smile
        smile_rect = pygame.Rect(head_x - head_size // 4, head_y, head_size // 2, head_size // 4)
        pygame.draw.arc(screen, BLACK, smile_rect, 0, math.pi, 2)
        
        # Torso (trapezoid shape)
        torso_width_top = self.width // 1.5
        torso_width_bottom = self.width // 2
        torso_height = self.height // 2.5
        torso_x = self.x + (self.width - torso_width_top) // 2
        torso_y = head_y + head_size // 2
        
        torso_points = [
            (torso_x, torso_y),
            (torso_x + torso_width_top, torso_y),
            (torso_x + torso_width_top + (torso_width_bottom - torso_width_top) // 2, torso_y + torso_height),
            (torso_x - (torso_width_bottom - torso_width_top) // 2, torso_y + torso_height)
        ]
        pygame.draw.polygon(screen, shirt_color, torso_points)
        
        # Legs
        leg_width = torso_width_bottom // 3
        leg_height = self.height // 2.5
        left_leg_x = torso_x + (torso_width_bottom - leg_width * 2) // 3
        right_leg_x = torso_x + torso_width_bottom - leg_width - (torso_width_bottom - leg_width * 2) // 3
        leg_y = torso_y + torso_height
        
        # Left leg with animation
        left_leg_points = [
            (left_leg_x, leg_y),
            (left_leg_x + leg_width, leg_y),
            (left_leg_x + leg_width - int(leg_offset), leg_y + leg_height),
            (left_leg_x - int(leg_offset), leg_y + leg_height)
        ]
        pygame.draw.polygon(screen, pants_color, left_leg_points)
        
        # Right leg with animation
        right_leg_points = [
            (right_leg_x, leg_y),
            (right_leg_x + leg_width, leg_y),
            (right_leg_x + leg_width + int(leg_offset), leg_y + leg_height),
            (right_leg_x + int(leg_offset), leg_y + leg_height)
        ]
        pygame.draw.polygon(screen, pants_color, right_leg_points)
        
        # Feet
        foot_width = int(leg_width * 1.2)
        foot_height = leg_height // 4
        pygame.draw.ellipse(screen, BLACK, 
                           (left_leg_x - int(leg_offset) - foot_width // 4, leg_y + leg_height - foot_height // 2, 
                            foot_width, foot_height))
        pygame.draw.ellipse(screen, BLACK, 
                           (right_leg_x + int(leg_offset) - foot_width // 4, leg_y + leg_height - foot_height // 2, 
                            foot_width, foot_height))
        
        # Arms - using polygons instead of lines to avoid float issues
        arm_width = torso_width_top // 6
        arm_length = int(torso_height * 0.8)
        
        # Left arm with animation
        left_arm_x = torso_x
        left_arm_y = torso_y + torso_height // 4
        left_hand_x = left_arm_x - arm_width - int(arm_offset)
        left_hand_y = left_arm_y + arm_length
        
        # Draw arm as a polygon
        left_arm_points = [
            (left_arm_x, left_arm_y - arm_width//2),
            (left_arm_x, left_arm_y + arm_width//2),
            (left_hand_x, left_hand_y + arm_width//2),
            (left_hand_x, left_hand_y - arm_width//2)
        ]
        pygame.draw.polygon(screen, skin_color, left_arm_points)
        pygame.draw.circle(screen, skin_color, (left_hand_x, left_hand_y), arm_width // 2)
        
        # Right arm with animation
        right_arm_x = torso_x + torso_width_top
        right_arm_y = torso_y + torso_height // 4
        right_hand_x = right_arm_x + arm_width + int(arm_offset)
        right_hand_y = right_arm_y + arm_length
        
        # Draw arm as a polygon
        right_arm_points = [
            (right_arm_x, right_arm_y - arm_width//2),
            (right_arm_x, right_arm_y + arm_width//2),
            (right_hand_x, right_hand_y + arm_width//2),
            (right_hand_x, right_hand_y - arm_width//2)
        ]
        pygame.draw.polygon(screen, skin_color, right_arm_points)
        pygame.draw.circle(screen, skin_color, (right_hand_x, right_hand_y), arm_width // 2)
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.animation_frame = 0
        self.direction = 0

class Poop:
    def __init__(self):
        self.width = POOP_SIZE
        self.height = POOP_SIZE
        self.reset()
        self.speed = POOP_SPEED
        self.color = BROWN
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)  # Random rotation speed
    
    def draw(self):
        # Draw a more detailed poop emoji
        # Main body
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)
        
        # Top part
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y + self.height // 4), self.width // 3)
        
        # Eyes (white part)
        eye_size = self.width // 8
        pygame.draw.circle(screen, WHITE, (self.x + self.width // 3, self.y + self.height // 3), eye_size)
        pygame.draw.circle(screen, WHITE, (self.x + 2 * self.width // 3, self.y + self.height // 3), eye_size)
        
        # Pupils (black part)
        pupil_size = eye_size // 2
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 3, self.y + self.height // 3), pupil_size)
        pygame.draw.circle(screen, BLACK, (self.x + 2 * self.width // 3, self.y + self.height // 3), pupil_size)
        
        # Smile
        smile_rect = pygame.Rect(self.x + self.width // 4, self.y + self.height // 2, self.width // 2, self.height // 4)
        pygame.draw.arc(screen, BLACK, smile_rect, 0, math.pi, 2)
    
    def move(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
    
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)  # New random rotation speed
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

def check_collision(player, poop):
    # Use a slightly smaller collision box for better gameplay feel
    collision_margin = 10
    if (player.x + collision_margin < poop.x + poop.width - collision_margin and
        player.x + player.width - collision_margin > poop.x + collision_margin and
        player.y + collision_margin < poop.y + poop.height - collision_margin and
        player.y + player.height - collision_margin > poop.y + collision_margin):
        return True
    return False

def get_high_scores():
    if not os.path.exists(RANKING_FILE):
        return []
    
    scores = []
    try:
        with open(RANKING_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    name, score = parts
                    scores.append((name, float(score)))
    except Exception as e:
        print(f"Error reading scores: {e}")
    
    # Sort by score (highest first)
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def save_score(name, score):
    scores = get_high_scores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    
    try:
        with open(RANKING_FILE, "w") as file:
            for name, score in scores:
                file.write(f"{name},{score}\n")
    except Exception as e:
        print(f"Error saving score: {e}")

def display_high_scores():
    scores = get_high_scores()
    y_pos = 200
    
    title_text = large_font.render("HIGH SCORES", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 120))
    
    for i, (name, score) in enumerate(scores[:5]):  # Show top 5 scores
        score_text = font.render(f"{i+1}. {name}: {score:.1f}s", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_pos))
        y_pos += 40

def get_nickname():
    nickname = ""
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and nickname:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif len(nickname) < 10:  # Limit nickname length
                    if event.unicode.isalnum() or event.unicode == "_":
                        nickname += event.unicode
        
        # Clear screen
        screen.fill(BLACK)
        
        # Display prompt
        prompt_text = font.render("Enter your nickname:", True, WHITE)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 200))
        
        # Display current input
        input_text = font.render(nickname + "_", True, WHITE)
        screen.blit(input_text, (SCREEN_WIDTH // 2 - input_text.get_width() // 2, 250))
        
        # Display instructions
        instr_text = font.render("Press ENTER when done", True, WHITE)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 300))
        
        pygame.display.flip()
        clock.tick(30)
    
    return nickname

def main():
    player = Player()
    active_poops = []  # List to store active poops
    
    game_over = False
    show_high_scores = False
    start_time = time.time()
    survival_time = 0
    spawn_counter = 0  # Counter for poop spawning
    
    # Initial poop generation to meet minimum requirement
    for _ in range(MIN_ACTIVE_POOPS):
        new_poop = Poop()
        new_poop.y = random.randint(-300, -40)  # Stagger initial positions
        active_poops.append(new_poop)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and (game_over or show_high_scores):
                    # Reset the game
                    player.reset()
                    active_poops.clear()
                    # Initial poop generation to meet minimum requirement
                    for _ in range(MIN_ACTIVE_POOPS):
                        new_poop = Poop()
                        new_poop.y = random.randint(-300, -40)  # Stagger initial positions
                        active_poops.append(new_poop)
                    game_over = False
                    show_high_scores = False
                    start_time = time.time()
                    spawn_counter = 0
        
        if not game_over and not show_high_scores:
            # Handle player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")
            
            # Spawn new poops to maintain the flow
            spawn_counter += 1
            if spawn_counter >= POOP_SPAWN_RATE and len(active_poops) < MAX_ACTIVE_POOPS:
                new_poop = Poop()
                active_poops.append(new_poop)
                spawn_counter = 0
            
            # Move and check all poops
            poops_to_remove = []
            for poop in active_poops:
                poop.move()
                
                # Check if poop is off screen
                if poop.is_off_screen():
                    poops_to_remove.append(poop)
                
                # Check for collision
                if check_collision(player, poop):
                    game_over = True
                    survival_time = time.time() - start_time
                    break
            
            # Remove poops that went off screen
            for poop in poops_to_remove:
                active_poops.remove(poop)
            
            # Ensure we maintain the minimum number of poops
            while len(active_poops) < MIN_ACTIVE_POOPS:
                new_poop = Poop()
                active_poops.append(new_poop)
            
            # Update timer
            current_time = time.time() - start_time
            
            # Draw everything
            screen.fill(BLACK)
            player.draw()
            for poop in active_poops:
                poop.draw()
            
            # Display timer and active poop count
            timer_text = font.render(f"Time: {current_time:.1f}s", True, WHITE)
            screen.blit(timer_text, (10, 10))
            poop_text = font.render(f"Active Poops: {len(active_poops)}", True, WHITE)
            screen.blit(poop_text, (10, 50))
        
        elif game_over and not show_high_scores:
            # Game over screen
            screen.fill(BLACK)
            
            game_over_text = large_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
            
            score_text = font.render(f"You survived for {survival_time:.1f} seconds", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
            
            # Get nickname and save score
            nickname = get_nickname()
            save_score(nickname, survival_time)
            
            game_over = False
            show_high_scores = True
        
        elif show_high_scores:
            # High scores screen
            screen.fill(BLACK)
            display_high_scores()
            
            restart_text = font.render("Press R to play again", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 500))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

class Player:
    def __init__(self):
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = PLAYER_SPEED
        self.color = BLUE
        self.animation_frame = 0
        self.animation_speed = 0.2
    
    def draw(self):
        if player_image:
            # If we have an image, use it
            # Create a running animation effect by slightly rotating the image based on movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.animation_frame += self.animation_speed
                angle = 10 * math.sin(self.animation_frame)
                rotated_image = pygame.transform.rotate(player_image, angle)
                screen.blit(rotated_image, (self.x, self.y))
            else:
                screen.blit(player_image, (self.x, self.y))
        else:
            # Fallback to rectangle if image fails
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.animation_frame = 0

class Poop:
    def __init__(self):
        self.width = POOP_SIZE
        self.height = POOP_SIZE
        self.reset()
        self.speed = POOP_SPEED
        self.color = BROWN
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)  # Random rotation speed
    
    def draw(self):
        if poop_image:
            # If we have an image, use it with rotation for a falling effect
            self.rotation += self.rotation_speed
            rotated_image = pygame.transform.rotate(poop_image, self.rotation)
            # Get the rect of the rotated image to center it properly
            rect = rotated_image.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(rotated_image, rect.topleft)
        else:
            # Fallback to the original poop shape if image fails
            pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height // 2))
            pygame.draw.circle(screen, (160, 82, 45), (self.x + self.width // 4, self.y + self.height // 4), 5)
            pygame.draw.circle(screen, (160, 82, 45), (self.x + 3 * self.width // 4, self.y + self.height // 3), 4)
    
    def move(self):
        self.y += self.speed
    
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)  # New random rotation speed
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

def check_collision(player, poop):
    # Use a slightly smaller collision box for better gameplay feel
    collision_margin = 10
    if (player.x + collision_margin < poop.x + poop.width - collision_margin and
        player.x + player.width - collision_margin > poop.x + collision_margin and
        player.y + collision_margin < poop.y + poop.height - collision_margin and
        player.y + player.height - collision_margin > poop.y + collision_margin):
        return True
    return False

def get_high_scores():
    if not os.path.exists(RANKING_FILE):
        return []
    
    scores = []
    try:
        with open(RANKING_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    name, score = parts
                    scores.append((name, float(score)))
    except Exception as e:
        print(f"Error reading scores: {e}")
    
    # Sort by score (highest first)
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def save_score(name, score):
    scores = get_high_scores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    
    try:
        with open(RANKING_FILE, "w") as file:
            for name, score in scores:
                file.write(f"{name},{score}\n")
    except Exception as e:
        print(f"Error saving score: {e}")

def display_high_scores():
    scores = get_high_scores()
    y_pos = 200
    
    title_text = large_font.render("HIGH SCORES", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 120))
    
    for i, (name, score) in enumerate(scores[:5]):  # Show top 5 scores
        score_text = font.render(f"{i+1}. {name}: {score:.1f}s", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, y_pos))
        y_pos += 40

def get_nickname():
    nickname = ""
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and nickname:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif len(nickname) < 10:  # Limit nickname length
                    if event.unicode.isalnum() or event.unicode == "_":
                        nickname += event.unicode
        
        # Clear screen
        screen.fill(BLACK)
        
        # Display prompt
        prompt_text = font.render("Enter your nickname:", True, WHITE)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 200))
        
        # Display current input
        input_text = font.render(nickname + "_", True, WHITE)
        screen.blit(input_text, (SCREEN_WIDTH // 2 - input_text.get_width() // 2, 250))
        
        # Display instructions
        instr_text = font.render("Press ENTER when done", True, WHITE)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 300))
        
        pygame.display.flip()
        clock.tick(30)
    
    return nickname

def main():
    player = Player()
    active_poops = []  # List to store active poops
    
    game_over = False
    show_high_scores = False
    start_time = time.time()
    survival_time = 0
    spawn_counter = 0  # Counter for poop spawning
    
    # Initial poop generation to meet minimum requirement
    for _ in range(MIN_ACTIVE_POOPS):
        new_poop = Poop()
        new_poop.y = random.randint(-300, -40)  # Stagger initial positions
        active_poops.append(new_poop)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and (game_over or show_high_scores):
                    # Reset the game
                    player.reset()
                    active_poops.clear()
                    # Initial poop generation to meet minimum requirement
                    for _ in range(MIN_ACTIVE_POOPS):
                        new_poop = Poop()
                        new_poop.y = random.randint(-300, -40)  # Stagger initial positions
                        active_poops.append(new_poop)
                    game_over = False
                    show_high_scores = False
                    start_time = time.time()
                    spawn_counter = 0
        
        if not game_over and not show_high_scores:
            # Handle player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")
            
            # Spawn new poops to maintain the flow
            spawn_counter += 1
            if spawn_counter >= POOP_SPAWN_RATE and len(active_poops) < MAX_ACTIVE_POOPS:
                new_poop = Poop()
                active_poops.append(new_poop)
                spawn_counter = 0
            
            # Move and check all poops
            poops_to_remove = []
            for poop in active_poops:
                poop.move()
                
                # Check if poop is off screen
                if poop.is_off_screen():
                    poops_to_remove.append(poop)
                
                # Check for collision
                if check_collision(player, poop):
                    game_over = True
                    survival_time = time.time() - start_time
                    break
            
            # Remove poops that went off screen
            for poop in poops_to_remove:
                active_poops.remove(poop)
            
            # Ensure we maintain the minimum number of poops
            while len(active_poops) < MIN_ACTIVE_POOPS:
                new_poop = Poop()
                active_poops.append(new_poop)
            
            # Update timer
            current_time = time.time() - start_time
            
            # Draw everything
            screen.fill(BLACK)
            player.draw()
            for poop in active_poops:
                poop.draw()
            
            # Display timer and active poop count
            timer_text = font.render(f"Time: {current_time:.1f}s", True, WHITE)
            screen.blit(timer_text, (10, 10))
            poop_text = font.render(f"Active Poops: {len(active_poops)}", True, WHITE)
            screen.blit(poop_text, (10, 50))
        
        elif game_over and not show_high_scores:
            # Game over screen
            screen.fill(BLACK)
            
            game_over_text = large_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
            
            score_text = font.render(f"You survived for {survival_time:.1f} seconds", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
            
            # Get nickname and save score
            nickname = get_nickname()
            save_score(nickname, survival_time)
            
            game_over = False
            show_high_scores = True
        
        elif show_high_scores:
            # High scores screen
            screen.fill(BLACK)
            display_high_scores()
            
            restart_text = font.render("Press R to play again", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 500))
        
        pygame.display.flip()
        clock.tick(60)

# Import math module for animation
import math

if __name__ == "__main__":
    main()
