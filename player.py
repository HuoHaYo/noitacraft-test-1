import pygame
import math
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

class BasePlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = 5
        self.color = BLUE
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.angle = 0
        
        self.experience = 0
        self.level = 1
        self.experience_to_next_level = 100
        self.upgrade_points = 0
        
        self.bullet_speed = 10
        self.bullet_damage = 10
        self.fire_rate = 10
        self.fire_cooldown = 0
        
        self.player_type = "普通"
        self.description = "基础角色，发射单发子弹"

    def move(self, keys, width, height):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.x = max(self.radius, min(width - self.radius, self.x))
        self.y = max(self.radius, min(height - self.radius, self.y))

    def aim(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.atan2(dy, dx)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        end_x = self.x + math.cos(self.angle) * (self.radius + 10)
        end_y = self.y + math.sin(self.angle) * (self.radius + 10)
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def add_experience(self, amount):
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level += 1
            self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
            self.upgrade_points += 1
            return True
        return False

    def upgrade_max_health(self):
        self.max_health += 20
        self.health = min(self.health + 20, self.max_health)
        self.upgrade_points -= 1

    def upgrade_speed(self):
        self.speed += 0.5
        self.upgrade_points -= 1

    def upgrade_bullet_speed(self):
        self.bullet_speed += 1
        self.upgrade_points -= 1

    def upgrade_bullet_damage(self):
        self.bullet_damage += 2
        self.upgrade_points -= 1

    def upgrade_fire_rate(self):
        self.fire_rate = max(3, self.fire_rate - 1)
        self.upgrade_points -= 1

    def can_shoot(self):
        if self.fire_cooldown <= 0:
            self.fire_cooldown = self.fire_rate
            return True
        return False

    def update_cooldown(self):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def shoot(self):
        return []

class NormalPlayer(BasePlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = BLUE
        self.player_type = "普通"
        self.description = "基础角色，发射单发子弹"

    def shoot(self):
        if self.can_shoot():
            from projectile import Bullet
            return [Bullet(self.x, self.y, self.angle, self.bullet_damage, self.bullet_speed)]
        return []

class ShotgunPlayer(BasePlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = ORANGE
        self.radius = 22
        self.player_type = "散弹"
        self.description = "一次发射3发子弹，伤害较低"
        self.bullet_damage = 6
        self.fire_rate = 15
        self.spread = 0.3

    def shoot(self):
        if self.can_shoot():
            from projectile import Bullet
            bullets = []
            for i in range(3):
                angle = self.angle + (i - 1) * self.spread
                bullets.append(Bullet(self.x, self.y, angle, self.bullet_damage, self.bullet_speed))
            return bullets
        return []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 5, 2)
        
        for i in range(3):
            angle = self.angle + (i - 1) * self.spread
            end_x = self.x + math.cos(angle) * (self.radius + 10)
            end_y = self.y + math.sin(angle) * (self.radius + 10)
            pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)

class LaserPlayer(BasePlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = CYAN
        self.radius = 18
        self.player_type = "激光"
        self.description = "发射连续激光束，高伤害"
        self.bullet_damage = 15
        self.fire_rate = 5

    def shoot(self, mouse_pos=None):
        if self.can_shoot():
            from projectile import LaserBeam
            if mouse_pos is None:
                mouse_pos = (self.x + math.cos(self.angle) * 100, self.y + math.sin(self.angle) * 100)
            return [LaserBeam(self.x, self.y, mouse_pos[0], mouse_pos[1], self.bullet_damage)]
        return []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 3, 2)
        
        end_x = self.x + math.cos(self.angle) * (self.radius + 15)
        end_y = self.y + math.sin(self.angle) * (self.radius + 15)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 4)

class MissilePlayer(BasePlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = PURPLE
        self.radius = 20
        self.player_type = "导弹"
        self.description = "发射追踪导弹，自动锁定敌人"
        self.bullet_damage = 20
        self.fire_rate = 20
        self.missile_speed = 6

    def shoot(self, enemies):
        if self.can_shoot():
            from projectile import Missile
            target = None
            min_distance = 500
            
            for enemy in enemies:
                distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if distance < min_distance:
                    min_distance = distance
                    target = enemy
            
            if target:
                return [Missile(self.x, self.y, target, self.bullet_damage, self.missile_speed)]
            else:
                from projectile import Bullet
                return [Bullet(self.x, self.y, self.angle, self.bullet_damage, self.missile_speed)]
        return []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 4, 3)
        
        end_x = self.x + math.cos(self.angle) * (self.radius + 12)
        end_y = self.y + math.sin(self.angle) * (self.radius + 12)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 3)

class RapidFirePlayer(BasePlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = GREEN
        self.radius = 19
        self.player_type = "速射"
        self.description = "极快射速，但伤害较低"
        self.bullet_damage = 5
        self.fire_rate = 3
        self.bullet_speed = 12

    def shoot(self):
        if self.can_shoot():
            from projectile import Bullet
            return [Bullet(self.x, self.y, self.angle, self.bullet_damage, self.bullet_speed)]
        return []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 2, 2)
        
        end_x = self.x + math.cos(self.angle) * (self.radius + 8)
        end_y = self.y + math.sin(self.angle) * (self.radius + 8)
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)

PLAYER_TYPES = {
    "normal": NormalPlayer,
    "shotgun": ShotgunPlayer,
    "laser": LaserPlayer,
    "missile": MissilePlayer,
    "rapid": RapidFirePlayer
}

def create_player(player_type, x, y):
    if player_type in PLAYER_TYPES:
        return PLAYER_TYPES[player_type](x, y)
    return NormalPlayer(x, y)
