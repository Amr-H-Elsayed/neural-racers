import pygame
import sys

from settings import WIDTH, HEIGHT, FPS, BACKGROUND
from car import Car


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neural Racers")

clock = pygame.time.Clock()


# Track Settings

TRACK_GRAY = (60, 60, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CENTER_LINE_YELLOW = (230, 230, 0)

margin_x = int(WIDTH * 0.12)
margin_y = int(HEIGHT * 0.1)

track_width = 120
outer_radius = 120
inner_radius = max(10, outer_radius - track_width)

outer_rect = pygame.Rect(
    margin_x,
    margin_y,
    WIDTH - 2 * margin_x,
    HEIGHT - 2 * margin_y
)

inner_rect = pygame.Rect(
    outer_rect.left + track_width,
    outer_rect.top + track_width,
    outer_rect.width - 2 * track_width,
    outer_rect.height - 2 * track_width
)

mid_rect = pygame.Rect(
    outer_rect.left + track_width // 2,
    outer_rect.top + track_width // 2,
    outer_rect.width - track_width,
    outer_rect.height - track_width
)

mid_radius = outer_radius - track_width // 2


# Track

def draw_finish_line(surface):
    square_size = 12

    start_y = outer_rect.top
    end_y = inner_rect.top

    rows = (end_y - start_y) // square_size

    for row in range(rows):
        for col in range(2):
            color = WHITE if (row + col) % 2 == 0 else BLACK

            pygame.draw.rect(
                surface,
                color,
                (
                    WIDTH // 2 + col * square_size,
                    start_y + row * square_size,
                    square_size,
                    square_size
                )
            )


def draw_track(surface):
    surface.fill(BACKGROUND)

    # Outer track
    pygame.draw.rect(
        surface,
        TRACK_GRAY,
        outer_rect,
        border_radius=outer_radius
    )

    pygame.draw.rect(
        surface,
        WHITE,
        outer_rect,
        width=3,
        border_radius=outer_radius
    )

    # Inner grass
    pygame.draw.rect(
        surface,
        BACKGROUND,
        inner_rect,
        border_radius=inner_radius
    )

    pygame.draw.rect(
        surface,
        WHITE,
        inner_rect,
        width=3,
        border_radius=inner_radius
    )

    # Center line
    pygame.draw.rect(
        surface,
        CENTER_LINE_YELLOW,
        mid_rect,
        width=2,
        border_radius=mid_radius
    )

    draw_finish_line(surface)

def create_track_mask():
    mask_surface = pygame.Surface((WIDTH, HEIGHT))
    mask_surface.fill((0, 0, 0))

    pygame.draw.rect(
        mask_surface,
        (255, 255, 255),
        outer_rect,
        border_radius=outer_radius
    )

    pygame.draw.rect(
        mask_surface,
        (0, 0, 0),
        inner_rect,
        border_radius=inner_radius
    )

    return pygame.mask.from_surface(mask_surface)

track_mask = create_track_mask()


# Collision Detection

def point_in_rounded_rect(point, rect, radius):
    x, y = point

    closest_x = max(rect.left + radius, min(x, rect.right - radius))
    closest_y = max(rect.top + radius, min(y, rect.bottom - radius))

    dx = x - closest_x
    dy = y - closest_y

    return dx * dx + dy * dy <= radius * radius


def is_on_track(car):
    for corner in car.get_corners():

        inside_outer = point_in_rounded_rect(
            corner, outer_rect, outer_radius
        )

        inside_inner = point_in_rounded_rect(
            corner, inner_rect, inner_radius
        )

        if not inside_outer or inside_inner:
            return False

    return True


# Car

car = Car(
    WIDTH // 2 - 100,
    outer_rect.top + track_width // 2
)


# Main loop

running = True

while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                car = Car(
                    WIDTH // 2 - 100,
                    outer_rect.top + track_width // 2
                )

    keys = pygame.key.get_pressed()

    if car.alive:
        car.update(keys, dt)
        car.update_sensors(track_mask)

        if not is_on_track(car):
            car.alive = False

    draw_track(screen)

    if car.alive:
        car.draw(screen)
        car.draw_sensors(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()