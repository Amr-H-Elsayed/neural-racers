
import pygame
import math
from settings import SENSOR_COUNT, SENSOR_LENGTH, SENSOR_ANGLE


class Car:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.angle = 0

        self.sensors = [SENSOR_LENGTH] * SENSOR_COUNT

        self.speed = 0
        self.acceleration = 250
        self.max_speed = 300
        self.max_reverse = -100
        self.friction = 120

        self.steering_speed = 180  # Degrees per second

        self.width = 36
        self.height = 20

        self.alive = True

    def update(self, keys, dt):
        # Acceleration and braking
        if keys[pygame.K_w]:
            self.speed += self.acceleration * dt

        elif keys[pygame.K_s]:
            self.speed -= self.acceleration * dt

        else:
            if self.speed > 0:
                self.speed = max(0, self.speed - self.friction * dt)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.friction * dt)

        self.speed = max(
            self.max_reverse,
            min(self.speed, self.max_speed)
        )

        # Steering
        if abs(self.speed) > 5:
            steering = 0

            if keys[pygame.K_a]:
                steering -= 1
            if keys[pygame.K_d]:
                steering += 1

            speed_factor = min(abs(self.speed) / 150, 1)

            self.angle += (
                steering
                * self.steering_speed
                * speed_factor
                * (1 if self.speed > 0 else -1)
                * dt
            )

        # Movement
        direction = pygame.Vector2(1, 0).rotate(self.angle)
        self.position += direction * self.speed * dt

    def get_corners(self):
        half_width = self.width / 2
        half_height = self.height / 2

        corners = [
            pygame.Vector2(-half_width, -half_height),
            pygame.Vector2(half_width, -half_height),
            pygame.Vector2(half_width, half_height),
            pygame.Vector2(-half_width, half_height)
        ]

        return [
            self.position + corner.rotate(self.angle)
            for corner in corners
        ]


    def cast_sensor(self, angle, track_mask):
        direction = pygame.Vector2(1, 0).rotate(angle)

        for distance in range(0, SENSOR_LENGTH + 1, 2):
            point = self.position + direction * distance
            x, y = int(point.x), int(point.y)

            # Out of screen bounds
            if not (0 <= x < track_mask.get_width()
                 and 0 <= y < track_mask.get_height()):
                return distance

            # The sensor has reached grass / outside the track
            if track_mask.get_at((x, y)) == 0:
                return distance

        return SENSOR_LENGTH


    def update_sensors(self, track_mask):
        sensor_angles = [
            self.angle - SENSOR_ANGLE,
            self.angle - SENSOR_ANGLE / 2,
            self.angle,
            self.angle + SENSOR_ANGLE / 2,
            self.angle + SENSOR_ANGLE
        ]

        self.sensors = [
            self.cast_sensor(angle, track_mask)
            for angle in sensor_angles
        ]


    def draw_sensors(self, surface):
        for distance, angle_offset in zip(
            self.sensors,
            [-SENSOR_ANGLE, -SENSOR_ANGLE / 2, 0,
             SENSOR_ANGLE / 2, SENSOR_ANGLE]
        ):
            direction = pygame.Vector2(1, 0).rotate(
                self.angle + angle_offset
            )

            endpoint = self.position + direction * distance

            pygame.draw.line(
                surface,
                (0, 255, 100),
                self.position,
                endpoint,
                2
            )

            pygame.draw.circle(
                surface,
                (255, 255, 0),
                (int(endpoint.x), int(endpoint.y)),
                4
            )


    def draw(self, surface):
        car_surface = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            car_surface,
            (220, 45, 45),
            (0, 0, self.width, self.height),
            border_radius=5
        )

        # Windshield
        pygame.draw.rect(
            car_surface,
            (120, 200, 230),
            (23, 3, 9, 14),
            border_radius=2
        )

        rotated = pygame.transform.rotate(
            car_surface,
            -self.angle
        )

        rect = rotated.get_rect(center=self.position)
        surface.blit(rotated, rect)
