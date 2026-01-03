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

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 3
        self.color = RED
        self.health = 30
        self.max_health = 30
        self.score_value = 10
        self.damage = 10

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class FastEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 12
        self.speed = 6
        self.color = ORANGE
        self.health = 15
        self.max_health = 15
        self.score_value = 15
        self.damage = 5

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)

class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 25
        self.speed = 1.5
        self.color = PURPLE
        self.health = 100
        self.max_health = 100
        self.score_value = 30
        self.damage = 20

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 5, 3)
        
        health_percentage = self.health / self.max_health
        bar_width = 40
        bar_height = 5
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 10
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_percentage, bar_height))

class ShooterEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 18
        self.speed = 2
        self.color = CYAN
        self.health = 40
        self.max_health = 40
        self.score_value = 20
        self.damage = 10
        self.shoot_cooldown = 0
        self.shoot_delay = 120
        self.bullets = []

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 200:
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and distance <= 400:
            self.shoot(player)
            self.shoot_cooldown = self.shoot_delay

    def shoot(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        angle = math.atan2(dy, dx)
        bullet = EnemyBullet(self.x, self.y, angle)
        self.bullets.append(bullet)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 3, 2)
        
        for bullet in self.bullets:
            bullet.draw(screen)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

class WanderingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 16
        self.speed = 2.5
        self.color = YELLOW
        self.health = 25
        self.max_health = 25
        self.score_value = 12
        self.damage = 8
        self.change_direction_timer = 0
        self.change_direction_delay = 60
        self.target_x = x
        self.target_y = y

    def update(self, player):
        self.change_direction_timer -= 1
        
        if self.change_direction_timer <= 0:
            self.change_direction_timer = self.change_direction_delay
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 150)
            self.target_x = self.x + math.cos(angle) * distance
            self.target_y = self.y + math.sin(angle) * distance
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 5:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 4, 2)

class SwarmEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 10
        self.speed = 4
        self.color = GREEN
        self.health = 10
        self.max_health = 10
        self.score_value = 5
        self.damage = 3

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 1)

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.radius = 40
        self.speed = 1
        self.color = (139, 0, 0)
        self.health = 300
        self.max_health = 300
        self.score_value = 100
        self.damage = 30
        self.shoot_cooldown = 0
        self.shoot_delay = 60
        self.bullets = []
        self.phase = 1
        self.special_attack_cooldown = 0
        self.special_attack_delay = 180

    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 300:
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
        
        self.shoot_cooldown -= 1
        self.special_attack_cooldown -= 1
        
        if self.shoot_cooldown <= 0:
            self.shoot(player)
            self.shoot_cooldown = self.shoot_delay
        
        if self.special_attack_cooldown <= 0:
            self.special_attack()
            self.special_attack_cooldown = self.special_attack_delay
        
        if self.health < self.max_health * 0.5:
            self.phase = 2
            self.shoot_delay = 40
            self.speed = 1.5

    def shoot(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        angle = math.atan2(dy, dx)
        
        if self.phase == 1:
            bullet = EnemyBullet(self.x, self.y, angle)
            self.bullets.append(bullet)
        else:
            for i in range(3):
                offset_angle = angle + (i - 1) * 0.3
                bullet = EnemyBullet(self.x, self.y, offset_angle)
                self.bullets.append(bullet)

    def special_attack(self):
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            bullet = EnemyBullet(self.x, self.y, angle)
            self.bullets.append(bullet)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 5, 4)
        
        health_percentage = self.health / self.max_health
        bar_width = 80
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 15
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width * health_percentage, bar_height))
        
        for bullet in self.bullets:
            bullet.draw(screen)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

class EnemyBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 5
        self.angle = angle
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.color = WHITE
        self.damage = 5

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        return (self.x < 0 or self.x > 800 or 
                self.y < 0 or self.y > 600)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

def spawn_enemy(enemy_type=None):
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, 800)
        y = -50
    elif side == 'bottom':
        x = random.randint(0, 800)
        y = 650
    elif side == 'left':
        x = -50
        y = random.randint(0, 600)
    else:
        x = 850
        y = random.randint(0, 600)
    
    if enemy_type is None:
        enemy_type = random.choice(['normal', 'fast', 'tank', 'shooter', 'wandering', 'swarm'])
    
    if enemy_type == 'normal':
        return Enemy(x, y)
    elif enemy_type == 'fast':
        return FastEnemy(x, y)
    elif enemy_type == 'tank':
        return TankEnemy(x, y)
    elif enemy_type == 'shooter':
        return ShooterEnemy(x, y)
    elif enemy_type == 'wandering':
        return WanderingEnemy(x, y)
    elif enemy_type == 'swarm':
        return SwarmEnemy(x, y)
    elif enemy_type == 'boss':
        return BossEnemy(400, -50)
