import pgzrun
from pygame import Rect

TITLE = "A Jornada da Estrela"
WIDTH = 800
HEIGHT = 600

game_state = "menu"
enemies_active = False
music_playing = True

score = 0
scroll_x = 0

star = Actor("star", (100, HEIGHT - 150))
star.invulnerable_timer = 0  
star.vy = 0
star.on_ground = False
star.lives = 3
can_fire = True 

powers = []

platforms = [Rect(0, HEIGHT - 50, 3000, 50)]  
map_width = 3000

enemies = [
    Actor("enemy", (400, 0)),  
    Actor("enemy", (800, 0)),  
    Actor("enemy", (1200, 0))  
]

for enemy in enemies:
    for platform in platforms:
        if platform.x <= enemy.x <= platform.x + platform.width:
            enemy.y = platform.y - enemy.height
            break
    enemy.vx = 2 

portal = Actor("portal", (map_width - 350, 0))
portal.y = platforms[0].y - portal.height + 10


def update():
    global scroll_x, game_state, powers, score, enemies_active
    if game_state == "jogando":
        apply_gravity()
        check_collisions()
        handle_movement()
        update_scroll()
        update_powers()
        update_enemies()
        check_portal()
        check_fall()

def apply_gravity():
    if not star.on_ground:
        star.vy += 0.5
    star.y += star.vy

def check_collisions():
    global game_state, score

    star.on_ground = False
    star_rect = Rect(star.x, star.y, star.width, star.height)

    for platform in platforms:
        if platform.colliderect(star_rect):
            if star.vy >= 0:
                star.on_ground = True
                star.vy = 0
                star.y = platform.y - star.height + 1

    if enemies_active:
        if not hasattr(star, "invulnerable_timer"):
            star.invulnerable_timer = 0

        for enemy in enemies:
            enemy_rect = Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if star_rect.colliderect(enemy_rect):
                if star.invulnerable_timer <= 0:
                    star.lives -= 1
                    star.invulnerable_timer = 30
                    if star.lives <= 0:
                        game_state = "game_over"
                        reset_star()

    if star.invulnerable_timer > 0:
        star.invulnerable_timer -= 1

    for power in powers[:]:
        power_rect = Rect(power['x'], power['y'], 10, 10)
        for enemy in enemies[:]:
            enemy_rect = Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if power_rect.colliderect(enemy_rect):
                enemies.remove(enemy)
                powers.remove(power)
                score += 100
                break

def update_enemies():
    for enemy in enemies:
        enemy.x += enemy.vx
        if enemy.x <= 0 or enemy.x >= map_width - enemy.width:
            enemy.vx *= -1

def check_portal():
    global game_state
    portal_center = Rect(portal.x + portal.width // 4, portal.y, portal.width // 2, portal.height)
    if star.colliderect(portal_center) and not enemies:
        game_state = "venceu"
        star.vy = 0
        star.on_ground = True

def reset_star():
    star.x, star.y = 100, platforms[0].y - star.height
    star.vy = 0
    star.on_ground = False

def handle_movement():
    global enemies_active, can_fire
    if keyboard.left or keyboard.right:
        enemies_active = True

    if keyboard.left:
        star.image = "star_left"
        star.x = max(star.x - 5, 0)
    if keyboard.right:
        star.image = "star_right"
        star.x = min(star.x + 5, map_width)

    if (keyboard.up or keyboard.w) and star.on_ground:
        star.vy = -10

    if keyboard.space and can_fire:
        fire_projectile()
        can_fire = False

def fire_projectile():
    powers.append({'x': star.x + star.width, 'y': star.y + star.height // 2, 'vx': 7})

def update_powers():
    global can_fire
    for power in powers:
        power['x'] += power['vx']

    powers[:] = [power for power in powers if power['x'] < map_width]
    if not powers:
        can_fire = True

def update_scroll():
    global scroll_x
    if star.x > WIDTH // 2 and star.x < map_width - WIDTH // 2:
        scroll_x = star.x - WIDTH // 2
    elif star.x <= WIDTH // 2:
        scroll_x = 0
    elif star.x >= map_width - WIDTH // 2:
        scroll_x = map_width - WIDTH

def check_fall():
    if star.y > HEIGHT and game_state != "venceu":
        star.lives -= 1
        if star.lives <= 0:
            game_state = "game_over"
        else:
            reset_star()

def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "jogando":
        draw_game()
    elif game_state == "venceu":
        draw_win()
    elif game_state == "game_over":
        draw_game_over()

def draw_menu():
    screen.blit("menu_background", (0, 0))
    screen.draw.text("A Jornada da Estrela", center=(WIDTH // 2, HEIGHT // 3), fontsize=50, color="white")
    screen.draw.text("Pressione ENTER para começar", center=(WIDTH // 2, HEIGHT // 2), fontsize=30, color="yellow")
    screen.draw.text("Pressione ESC para sair", center=(WIDTH // 2, HEIGHT // 1.7), fontsize=30, color="red")
    draw_music_button()

def draw_game():
    draw_background()
    for platform in platforms:
        screen.draw.filled_rect(Rect(platform.x - scroll_x, platform.y, platform.width, platform.height), "purple")
    screen.blit(star.image, (star.x - scroll_x, star.y))
    screen.blit(portal.image, (portal.x - scroll_x, portal.y))
    for power in powers:
        screen.draw.filled_circle((power['x'] - scroll_x, power['y']), 5, "yellow")
    for enemy in enemies:
        screen.blit(enemy.image, (enemy.x - scroll_x, enemy.y))

    draw_music_button()
    draw_hud()

def draw_background():
    bg_width = images.background_image.get_width()
    for x in range(-1, (map_width // bg_width) + 2):
        screen.blit("background_image", (x * bg_width - scroll_x % bg_width, 0))

def draw_win():
    screen.fill("blue")
    screen.draw.text("Parabéns, você venceu!", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=50, color="white")
    screen.draw.text("Pressione ESC para sair", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="yellow")
    draw_music_button()

def draw_game_over():
    screen.fill("red")
    screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=50, color="white")
    screen.draw.text("Pressione ESC para sair", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="yellow")
    draw_music_button()

def draw_music_button():
    button_color = "green" if music_playing else "red"
    screen.draw.filled_rect(Rect(WIDTH - 120, 20, 100, 40), button_color)
    text = "Pausa" if music_playing else "Tocar"
    screen.draw.text(text, center=(WIDTH - 70, 40), fontsize=20, color="white")

def draw_hud():
    screen.draw.text(f"Vidas: {star.lives}  Pontuação: {score}", (20, 20), fontsize=30, color="white")

def on_key_down(key):
    global game_state, music_playing
    if key == keys.ESCAPE:
        if game_state in ["menu", "venceu", "game_over"]:
            exit()
        else:
            game_state = "menu"
    elif game_state == "menu" and key == keys.RETURN:
        game_state = "jogando"

def toggle_pause():
    global music_playing
    if music_playing:
        music.pause()
    else:
        music.unpause()
    music_playing = not music_playing

def on_mouse_down(pos):
    global music_playing
    if Rect(WIDTH - 120, 20, 100, 40).collidepoint(pos):
        toggle_pause()

music.set_volume(0.5)
music.play("background_music")
pgzrun.go()