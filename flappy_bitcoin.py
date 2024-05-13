import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game Variables
screen_width = 400
screen_height = 600
gravity = 0.25
bird_movement = 0
game_active = False
score = 0
high_score = 0
gap = 180  # Tighter gap between the pipes
floor_scroll = 0
scroll_speed = 3  # Initial scroll speed
pipe_frequency = 1800  # Time between pipe creation
last_pipe = pygame.time.get_ticks()
difficulty_increase_factor = 0.1  # How much to increase difficulty each time

# Launch Variables
first_time_playing = True

# Flyby bird variables
flyby_bird = None
flyby_bird_x = screen_width
flyby_bird_y = random.randint(50, screen_height // 3)
flyby_bird_speed = 5
next_flyby_time = 0
bird_sound_played = False

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 235)
GREY = (200, 200, 200)

# Screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flappy Bitcoin")

# Clock
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 40)

# Load images
bitcoin_logo = pygame.image.load('bitcoin_logo.png')
bitcoin_logo = pygame.transform.scale(bitcoin_logo, (50, 50))

bitcoin2_logo = pygame.image.load('bitcoin2.png')
bitcoin2_logo = pygame.transform.scale(bitcoin2_logo, (100, 100))

# Load the flying bird image
flyby_bird = pygame.image.load('bird.png')
flyby_bird = pygame.transform.scale(flyby_bird, (50, 50))  # Adjust size as needed

# Load sounds
flap_sound = pygame.mixer.Sound('click.mp3')
end_sound = pygame.mixer.Sound('endgame.mp3')
pygame.mixer.music.load('music.mp3')
flyby_sound = pygame.mixer.Sound('birdsound.mp3')
start_sound = pygame.mixer.Sound('start.mp3')

# Set sound volumes
pygame.mixer.music.set_volume(0.6)
end_sound.set_volume(1.0)
flyby_sound.set_volume(0.9)
start_sound.set_volume(1.0)

# Background elements
background = pygame.Surface((screen_width, screen_height))
background.fill(SKY_BLUE)
floor_surface = pygame.Surface((screen_width, 100))
floor_surface.fill(GREEN)

# Initialize the bitcoin_rect
bitcoin_rect = bitcoin_logo.get_rect(center=(100, screen_height // 2))

# Function to draw the floor
def draw_floor():
    screen.blit(floor_surface, (floor_scroll, screen_height - 100))
    screen.blit(floor_surface, (floor_scroll + screen_width, screen_height - 100))

# Clouds and Buildings
clouds = []
for i in range(5):
    clouds.append(pygame.Rect(random.randint(0, screen_width), random.randint(0, 200), 60, 40))

buildings = []
for i in range(6):
    buildings.append(pygame.Rect(i * 100, screen_height - 200, 70, 120))

# Draw Clouds and Buildings
def draw_background_elements():
    for cloud in clouds:
        pygame.draw.ellipse(screen, GREY, cloud)
    for building in buildings:
        pygame.draw.rect(screen, (100, 100, 100), building)

# Pipes - using dictionaries to handle pipe properties
pipes = []

def create_pipe():
    random_pipe_pos = random.choice([250, 300, 350, 400, 450])
    pipe_color = random.choice([(100, 20, 20), (20, 100, 20), (20, 20, 100), (100, 100, 20)])
    bottom_pipe = pygame.Surface((80, screen_height))
    top_pipe = pygame.Surface((80, screen_height))
    bottom_pipe.fill(pipe_color)
    top_pipe.fill(pipe_color)
    bottom_pipe_rect = bottom_pipe.get_rect(midtop=(700, random_pipe_pos))
    top_pipe_rect = top_pipe.get_rect(midbottom=(700, random_pipe_pos - gap))
    
    return {
        'bottom_pipe': bottom_pipe,
        'bottom_rect': bottom_pipe_rect,
        'top_pipe': top_pipe,
        'top_rect': top_pipe_rect,
        'passed': False
    }

def move_pipes(pipes):
    for pipe in pipes:
        pipe['bottom_rect'].centerx -= scroll_speed
        pipe['top_rect'].centerx -= scroll_speed
    return [pipe for pipe in pipes if pipe['bottom_rect'].right > -50]

def draw_pipes(pipes):
    for pipe in pipes:
        screen.blit(pipe['bottom_pipe'], pipe['bottom_rect'])
        screen.blit(pipe['top_pipe'], pipe['top_rect'])

def check_collision(pipes):
    for pipe in pipes:
        if bitcoin_rect.colliderect(pipe['bottom_rect']) or bitcoin_rect.colliderect(pipe['top_rect']):
            return False
    if bitcoin_rect.top <= -100 or bitcoin_rect.bottom >= screen_height - 100:
        return False
    return True

def rotate_bitcoin(bitcoin):
    new_bitcoin = pygame.transform.rotozoom(bitcoin, -bird_movement * 3, 1)
    return new_bitcoin

def score_display(game_active):
    if game_active:
        score_surface = font.render(str(int(score)), True, WHITE)
        score_rect = score_surface.get_rect(center=(screen_width // 2, 50))
        screen.blit(score_surface, score_rect)
    else:
        screen.blit(bitcoin2_logo, (screen_width // 2 - bitcoin2_logo.get_width() // 2, screen_height // 2 - bitcoin2_logo.get_height() // 2 - 30))
        
        score_surface = font.render(f'Score: {int(score)}', True, WHITE)
        score_rect = score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 60))
        screen.blit(score_surface, score_rect)

        high_score_surface = font.render(f'High Score: {int(high_score)}', True, WHITE)
        high_score_rect = high_score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
        screen.blit(high_score_surface, high_score_rect)

# Function to manage the flyby bird
def manage_flyby_bird():
    global flyby_bird_x, flyby_bird_y, next_flyby_time, bird_sound_played
    current_time = pygame.time.get_ticks()
    
    # Check if it's time to start a new flyby
    if current_time >= next_flyby_time and game_active:
        if flyby_bird_x > screen_width:
            # Reset the bird position off-screen to the left and randomize its y position
            flyby_bird_x = -50
            flyby_bird_y = random.randint(50, screen_height // 3)
            # Schedule the next flyby
            next_flyby_time = current_time + random.randint(6000, 11000)
            bird_sound_played = False

    # Update the flyby bird's position if it's time for it to move
    if -50 <= flyby_bird_x < screen_width + 100:
        flyby_bird_x += flyby_bird_speed
        screen.blit(flyby_bird, (flyby_bird_x, flyby_bird_y))
        
        # Play the sound once as the bird appears
        if not bird_sound_played and game_active:
            flyby_sound.play()
            bird_sound_played = True

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_active:
                # Stop the endgame sound when starting a new game
                end_sound.stop() 

                game_active = True
                pipes = []
                bitcoin_rect.center = (100, screen_height // 2)
                bird_movement = 0
                score = 0
                scroll_speed = 3
                gap = 180

                # Play the start sound only the first time the player starts the game
                if first_time_playing:
                    start_sound.play()
                    pygame.mixer.music.play(-1)
                    first_time_playing = False
                else:
                    pygame.mixer.music.play(-1)

            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 6
                flap_sound.play()

    screen.blit(background, (0, 0))
    draw_background_elements()

    if game_active:
        # Manage bird movement
        bird_movement += gravity
        rotated_bitcoin = rotate_bitcoin(bitcoin_logo)
        bitcoin_rect.centery += bird_movement
        screen.blit(rotated_bitcoin, bitcoin_rect)

        # Manage pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            last_pipe = time_now
            pipes.append(create_pipe())

        pipes = move_pipes(pipes)
        draw_pipes(pipes)

        # Check for collisions
        game_active = check_collision(pipes)

        # Update and display score
        for pipe in pipes:
            if not pipe['passed'] and pipe['bottom_rect'].centerx < bitcoin_rect.centerx:
                pipe['passed'] = True
                score += 1

        score_display(game_active)

    else:
        # Game is not active, show end game scenario
        if high_score < score:
            high_score = score

        # Display the score
        score_display(game_active)

        # Reset the flyby bird for the next game
        flyby_bird_x = screen_width
        next_flyby_time = pygame.time.get_ticks() + random.randint(6000, 11000)
        bird_sound_played = False

        # Ensure the endgame sound is played just once after the game is over
        if not first_time_playing:
            end_sound.play()
            pygame.mixer.music.stop()
            first_time_playing = True  # Ensure this to prevent multiple plays of the end sound

    # Manage the flyby bird
    manage_flyby_bird()

    # Floor scrolling management
    floor_scroll -= scroll_speed
    if floor_scroll <= -screen_width:
        floor_scroll = 0
    draw_floor()

    pygame.display.update()
    clock.tick(60)  # Ensure the game runs at 60 frames per second