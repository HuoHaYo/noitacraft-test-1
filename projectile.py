import pygame
import math

WIDTH, HEIGHT = 800, 600

class Bullet:
    def __init__(self, x, y, angle, damage=10, speed=10):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = speed
        self.angle = angle
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.color = (255, 255, 0)
        self.damage = damage

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        return (self.x < 0 or self.x > WIDTH or 
                self.y < 0 or self.y > HEIGHT)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class LaserBeam:
    def __init__(self, x, y, mouse_x, mouse_y, damage=15):
        self.x = x
        self.y = y
        self.damage = damage*0.1
        self.width = 4
        self.color = (0, 255, 255)
        self.lifetime = 10
        self.hit_enemies = set()
        
        dx = mouse_x - x
        dy = mouse_y - y
        self.angle = math.atan2(dy, dx)
        
        self.end_x, self.end_y = self.calculate_screen_edge_intersection(x, y, self.angle)

    def calculate_screen_edge_intersection(self, x, y, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        if abs(cos_a) < 0.0001:
            if sin_a > 0:
                return x, HEIGHT
            else:
                return x, 0
        
        if abs(sin_a) < 0.0001:
            if cos_a > 0:
                return WIDTH, y
            else:
                return 0, y
        
        t_candidates = []
        
        if cos_a > 0:
            t_right = (WIDTH - x) / cos_a
            t_candidates.append(t_right)
        elif cos_a < 0:
            t_left = -x / cos_a
            t_candidates.append(t_left)
        
        if sin_a > 0:
            t_bottom = (HEIGHT - y) / sin_a
            t_candidates.append(t_bottom)
        elif sin_a < 0:
            t_top = -y / sin_a
            t_candidates.append(t_top)
        
        t = min(t for t in t_candidates if t > 0)
        
        return x + cos_a * t, y + sin_a * t

    def update(self):
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.end_x, self.end_y), self.width)
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (self.end_x, self.end_y), 2)

    def get_rect(self):
        min_x = min(self.x, self.end_x)
        min_y = min(self.y, self.end_y)
        max_x = max(self.x, self.end_x)
        max_y = max(self.y, self.end_y)
        return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def check_circle_collision(self, circle_x, circle_y, radius):
        dx = self.end_x - self.x
        dy = self.end_y - self.y
        fx = circle_x - self.x
        fy = circle_y - self.y
        
        line_length_sq = dx * dx + dy * dy
        if line_length_sq == 0:
            return False
        
        t = max(0, min(1, (fx * dx + fy * dy) / line_length_sq))
        
        closest_x = self.x + t * dx
        closest_y = self.y + t * dy
        
        distance_sq = (circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2
        
        return distance_sq <= radius * radius

class Missile:
    def __init__(self, x, y, target, damage=20, speed=6):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.radius = 6
        self.color = (128, 0, 128)
        self.turn_rate = 0.1
        self.angle = math.atan2(target.y - y, target.x - x)
        self.dx = math.cos(self.angle) * speed
        self.dy = math.sin(self.angle) * speed
        self.lifetime = 300

    def update(self):
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            target_angle = math.atan2(dy, dx)
            
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            self.angle += max(-self.turn_rate, min(self.turn_rate, angle_diff))
        
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        
        return self.lifetime > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius - 2, 1)

    def is_off_screen(self):
        return (self.x < -50 or self.x > WIDTH + 50 or 
                self.y < -50 or self.y > HEIGHT + 50)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
