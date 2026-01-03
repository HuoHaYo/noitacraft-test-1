import pygame
import math
import random
from enemy import *
from projectile import *

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("俯视角射击游戏")

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

clock = pygame.time.Clock()
FPS = 60

font_names = ["SimHei", "Microsoft YaHei", "SimSun", "Arial"]
font_path = None
for font_name in font_names:
    try:
        font = pygame.font.SysFont(font_name, 36)
        test_text = font.render("测试", True, WHITE)
        font_path = font_name
        break
    except:
        continue

if font_path:
    font_ui = pygame.font.SysFont(font_path, 36)
    font_large = pygame.font.SysFont(font_path, 72)
else:
    font_ui = pygame.font.Font(None, 36)
    font_large = pygame.font.Font(None, 72)

class Player:
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

def draw_ui(screen, player):
    score_text = font_ui.render(f"分数: {player.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    health_text = font_ui.render(f"生命值: {player.health}/{player.max_health}", True, WHITE)
    screen.blit(health_text, (10, 50))
    
    health_bar_width = 200
    health_bar_height = 20
    health_percentage = player.health / player.max_health
    pygame.draw.rect(screen, GRAY, (10, 90, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, GREEN, (10, 90, health_bar_width * health_percentage, health_bar_height))
    
    level_text = font_ui.render(f"等级: {player.level}", True, WHITE)
    screen.blit(level_text, (10, 120))
    
    exp_text = font_ui.render(f"经验: {player.experience}/{player.experience_to_next_level}", True, WHITE)
    screen.blit(exp_text, (10, 160))
    
    exp_bar_width = 200
    exp_bar_height = 15
    exp_percentage = player.experience / player.experience_to_next_level
    pygame.draw.rect(screen, GRAY, (10, 200, exp_bar_width, exp_bar_height))
    pygame.draw.rect(screen, BLUE, (10, 200, exp_bar_width * exp_percentage, exp_bar_height))
    
    if player.upgrade_points > 0:
        upgrade_text = font_ui.render(f"升级点: {player.upgrade_points} (按U升级)", True, YELLOW)
        screen.blit(upgrade_text, (10, 230))
    
    if hasattr(player, 'player_type'):
        type_text = font_ui.render(f"角色: {player.player_type}", True, CYAN)
        screen.blit(type_text, (10, 260))

def upgrade_screen(screen, player):
    from player import PLAYER_TYPES, create_player
    
    screen.fill((30, 30, 30))
    
    title_text = font_large.render("升级界面", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
    
    points_text = font_ui.render(f"可用升级点: {player.upgrade_points}", True, YELLOW)
    screen.blit(points_text, (WIDTH//2 - points_text.get_width()//2, 100))
    
    type_text = font_ui.render(f"当前角色: {player.player_type}", True, CYAN)
    screen.blit(type_text, (WIDTH//2 - type_text.get_width()//2, 140))
    
    desc_text = font_ui.render(player.description, True, GRAY)
    screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, 175))
    
    upgrade_options = [
        ("1. 最大生命值 +20", f"当前: {player.max_health}"),
        ("2. 移动速度 +0.5", f"当前: {player.speed}"),
        ("3. 子弹速度 +1", f"当前: {player.bullet_speed}"),
        ("4. 子弹伤害 +2", f"当前: {player.bullet_damage}"),
        ("5. 射击速度提升", f"当前: {11 - player.fire_rate}"),
    ]
    
    y_offset = 210
    for i, (option, current) in enumerate(upgrade_options):
        option_text = font_ui.render(option, True, WHITE)
        current_text = font_ui.render(current, True, GRAY)
        screen.blit(option_text, (WIDTH//2 - 200, y_offset))
        screen.blit(current_text, (WIDTH//2 + 100, y_offset))
        y_offset += 50
    
    character_options = [
        ("6. 普通角色", "基础单发子弹"),
        ("7. 散弹角色", "一次3发子弹"),
        ("8. 激光角色", "连续激光束"),
        ("9. 导弹角色", "追踪导弹"),
        ("0. 速射角色", "极快射速"),
    ]
    
    y_offset += 20
    pygame.draw.line(screen, GRAY, (100, y_offset), (700, y_offset), 2)
    y_offset += 30
    
    char_title = font_ui.render("切换角色", True, ORANGE)
    screen.blit(char_title, (WIDTH//2 - char_title.get_width()//2, y_offset))
    y_offset += 40
    
    for i, (option, desc) in enumerate(character_options):
        option_text = font_ui.render(option, True, WHITE)
        desc_text = font_ui.render(desc, True, GRAY)
        screen.blit(option_text, (WIDTH//2 - 200, y_offset))
        screen.blit(desc_text, (WIDTH//2 + 100, y_offset))
        y_offset += 45
    
    hint_text = font_ui.render("按数字键1-5升级，按0-9切换角色，按ESC返回游戏", True, GREEN)
    screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT - 50))

def switch_character(player, char_type):
    from player import create_player
    new_player = create_player(char_type, player.x, player.y)
    new_player.health = player.health
    new_player.max_health = player.max_health
    new_player.score = player.score
    new_player.experience = player.experience
    new_player.level = player.level
    new_player.experience_to_next_level = player.experience_to_next_level
    new_player.upgrade_points = player.upgrade_points
    new_player.speed = player.speed
    new_player.bullet_speed = player.bullet_speed
    new_player.bullet_damage = player.bullet_damage
    new_player.fire_rate = player.fire_rate
    return new_player

def pause_menu(screen):
    screen.fill((30, 30, 30))
    
    title_text = font_large.render("游戏暂停", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
    
    continue_text = font_ui.render("按 ESC 继续游戏", True, GREEN)
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2))
    
    quit_text = font_ui.render("按 Q 退出游戏", True, RED)
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 60))

def game_over_screen(screen, score):
    game_over_text = font_large.render("游戏结束", True, RED)
    score_text = font_ui.render(f"最终分数: {score}", True, WHITE)
    restart_text = font_ui.render("按 R 重新开始", True, WHITE)
    quit_text = font_ui.render("按 Q 退出", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 100))

def main():
    player = Player(WIDTH // 2, HEIGHT // 2)
    bullets = []
    enemies = []
    enemy_bullets = []
    
    enemy_spawn_timer = 0
    enemy_spawn_delay = 60
    score_threshold = 0
    boss_spawned = False
    
    game_over = False
    upgrade_screen_open = False
    pause_menu_open = False
    mouse_held = False
    
    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over and not upgrade_screen_open and not pause_menu_open:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_held = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_held = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u and player.upgrade_points > 0:
                        upgrade_screen_open = True
                    elif event.key == pygame.K_ESCAPE:
                        pause_menu_open = True
            elif upgrade_screen_open:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        upgrade_screen_open = False
                    elif event.key == pygame.K_1 and player.upgrade_points > 0:
                        player.upgrade_max_health()
                    elif event.key == pygame.K_2 and player.upgrade_points > 0:
                        player.upgrade_speed()
                    elif event.key == pygame.K_3 and player.upgrade_points > 0:
                        player.upgrade_bullet_speed()
                    elif event.key == pygame.K_4 and player.upgrade_points > 0:
                        player.upgrade_bullet_damage()
                    elif event.key == pygame.K_5 and player.upgrade_points > 0:
                        player.upgrade_fire_rate()
                    elif event.key == pygame.K_6:
                        player = switch_character(player, "normal")
                    elif event.key == pygame.K_7:
                        player = switch_character(player, "shotgun")
                    elif event.key == pygame.K_8:
                        player = switch_character(player, "laser")
                    elif event.key == pygame.K_9:
                        player = switch_character(player, "missile")
                    elif event.key == pygame.K_0:
                        player = switch_character(player, "rapid")
            elif pause_menu_open:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause_menu_open = False
                    elif event.key == pygame.K_q:
                        running = False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        from player import create_player
                        player = create_player("normal", WIDTH // 2, HEIGHT // 2)
                        bullets = []
                        enemies = []
                        enemy_bullets = []
                        enemy_spawn_delay = 60
                        score_threshold = 0
                        boss_spawned = False
                        game_over = False
                        upgrade_screen_open = False
                        pause_menu_open = False
                        mouse_held = False
                    elif event.key == pygame.K_q:
                        running = False
        
        if not game_over and not upgrade_screen_open and not pause_menu_open:
            keys = pygame.key.get_pressed()
            player.move(keys, WIDTH, HEIGHT)
            player.aim(pygame.mouse.get_pos())
            player.update_cooldown()
            
            if mouse_held:
                if hasattr(player, 'shoot'):
                    if player.player_type == "导弹":
                        new_bullets = player.shoot(enemies)
                    elif player.player_type == "激光":
                        new_bullets = player.shoot(pygame.mouse.get_pos())
                    else:
                        new_bullets = player.shoot()
                    bullets.extend(new_bullets)
                elif player.can_shoot():
                    bullet = Bullet(player.x, player.y, player.angle, player.bullet_damage, player.bullet_speed)
                    bullets.append(bullet)
            
            for bullet in bullets[:]:
                if isinstance(bullet, LaserBeam):
                    if not bullet.update():
                        bullets.remove(bullet)
                else:
                    bullet.update()
                    if bullet.is_off_screen():
                        bullets.remove(bullet)
            
            for enemy_bullet in enemy_bullets[:]:
                enemy_bullet.update()
                if enemy_bullet.is_off_screen():
                    enemy_bullets.remove(enemy_bullet)
            
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_delay:
                if player.score >= score_threshold + 200 and not boss_spawned:
                    enemies.append(spawn_enemy('boss'))
                    boss_spawned = True
                    score_threshold = player.score
                else:
                    enemies.append(spawn_enemy())
                enemy_spawn_timer = 0
                if enemy_spawn_delay > 20:
                    enemy_spawn_delay -= 0.3
            
            for enemy in enemies[:]:
                enemy.update(player)
                
                if hasattr(enemy, 'bullets'):
                    enemy.update_bullets()
                    enemy_bullets.extend(enemy.bullets)
                    enemy.bullets.clear()
                
                player_rect = player.get_rect()
                enemy_rect = enemy.get_rect()
                
                if player_rect.colliderect(enemy_rect):
                    player.health -= enemy.damage
                    enemies.remove(enemy)
                    if player.health <= 0:
                        game_over = True
            
            for bullet in bullets[:]:
                if isinstance(bullet, LaserBeam):
                    bullet.hit_enemies.clear()
                    for enemy in enemies[:]:
                        if enemy not in bullet.hit_enemies and bullet.check_circle_collision(enemy.x, enemy.y, enemy.radius):
                            enemy.health -= bullet.damage
                            bullet.hit_enemies.add(enemy)
                            if enemy.health <= 0:
                                if enemy in enemies:
                                    enemies.remove(enemy)
                                player.score += enemy.score_value
                                player.add_experience(enemy.score_value)
                                if isinstance(enemy, BossEnemy):
                                    boss_spawned = False
                else:
                    bullet_rect = bullet.get_rect()
                    for enemy in enemies[:]:
                        enemy_rect = enemy.get_rect()
                        if bullet_rect.colliderect(enemy_rect):
                            enemy.health -= bullet.damage
                            bullets.remove(bullet)
                            if enemy.health <= 0:
                                if enemy in enemies:
                                    enemies.remove(enemy)
                                player.score += enemy.score_value
                                player.add_experience(enemy.score_value)
                                if isinstance(enemy, BossEnemy):
                                    boss_spawned = False
                            break
            
            for enemy_bullet in enemy_bullets[:]:
                bullet_rect = enemy_bullet.get_rect()
                player_rect = player.get_rect()
                if bullet_rect.colliderect(player_rect):
                    player.health -= enemy_bullet.damage
                    enemy_bullets.remove(enemy_bullet)
                    if player.health <= 0:
                        game_over = True
        
        screen.fill(BLACK)
        
        if upgrade_screen_open:
            upgrade_screen(screen, player)
        elif pause_menu_open:
            player.draw(screen)
            
            for bullet in bullets:
                bullet.draw(screen)
            
            for enemy_bullet in enemy_bullets:
                enemy_bullet.draw(screen)
            
            for enemy in enemies:
                enemy.draw(screen)
            
            draw_ui(screen, player)
            pause_menu(screen)
        elif not game_over:
            player.draw(screen)
            
            for bullet in bullets:
                bullet.draw(screen)
            
            for enemy_bullet in enemy_bullets:
                enemy_bullet.draw(screen)
            
            for enemy in enemies:
                enemy.draw(screen)
            
            draw_ui(screen, player)
        else:
            game_over_screen(screen, player.score)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
