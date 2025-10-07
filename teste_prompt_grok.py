# ═══════════════════════════════════════════════════════════════════
# JOGO DO PORQUINHO
# Gerado por IA(Grok 4 Fast) com base em prompt detalhado.
# ═══════════════════════════════════════════════════════════════════


import pygame
import random
import sys
import json
from datetime import datetime

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Porquinho")
clock = pygame.time.Clock()
FPS = 60

# Carregamento de imagens (com fallback)
try:
    pig_image = pygame.image.load('pig.png')
    pig_image = pygame.transform.scale(pig_image, (50, 50))
except FileNotFoundError:
    pig_image = pygame.Surface((50, 50))
    pig_image.fill((255, 182, 193))  # PINK
pig_facing_right = True

# Definição de cores
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DIRT_BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
PINK = (255, 182, 193)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)

# Variáveis globais do jogador
pig_x = WIDTH // 2 - 25
pig_y = HEIGHT - 150
pig_vel_x = 0
pig_vel_y = 0
pig_width = 50
pig_height = 50
on_ground = True
can_double_jump = False
has_double_jumped = False
last_safe_y = pig_y
max_safe_fall = 600  # 60m * 10px
reached_platform_this_cycle = False
space_pressed = False
pig_facing_right = True

# Física
gravity = 0.8
jump_force = -15
double_jump_force = -12
super_jump_force = -30

# Câmera
camera_y = 0.0

# Plataformas
platforms = []
ground_y = HEIGHT - 100

# Partículas
particles = []
max_particles = 200

# Pontuação
current_height = 0
max_height_reached = 0
highscore = 0
game_over = False
game_over_timer = 0
debug_mode = False
frame_count = 0  # Para piscar

# Carregar highscore
def load_high_score():
    """Carrega o highscore de highscore.json, retorna 0 se não existir"""
    try:
        with open('highscore.json', 'r') as f:
            data = json.load(f)
            return data.get('highscore', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

highscore = load_high_score()
max_height_reached = highscore

def save_high_score(score):
    """Salva o score e timestamp em highscore.json"""
    data = {
        'highscore': score,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open('highscore.json', 'w') as f:
        json.dump(data, f)

def check_and_save_high_score(current, previous):
    """Verifica e salva se current > previous, retorna True se salvou"""
    if current > previous:
        if current % 10 == 0:  # Salvar a cada 10m
            save_high_score(current)
            global highscore
            highscore = current
            return True
    return False

# Funções de plataformas
def create_platform(x, y):
    """Cria uma plataforma aleatória com tipo baseado em chances"""
    if random.random() < 0.6:
        width = random.randint(100, 150)
        p_type = 'normal'
        spring_rect = None
    else:
        r = random.random()
        if r < 0.75:  # 30% total quebravel (0.4 * 0.75 = 0.3)
            width = random.randint(80, 120)
            p_type = 'breakable'
            spring_rect = None
        else:  # 10% spring
            width = random.randint(100, 150)
            p_type = 'spring'
            spring_rect = pygame.Rect(x + (width - 30) // 2, y - 15, 30, 30)
    rect = pygame.Rect(x, y, width, 20)
    return {
        'rect': rect,
        'type': p_type,
        'spring_rect': spring_rect,
        'broken': False
    }

def generate_platforms():
    """Gera plataformas iniciais"""
    global platforms
    platforms = []
    y = ground_y - 100
    x = WIDTH // 2 - 75
    for _ in range(10):
        plat = create_platform(x, y)
        platforms.append(plat)
        y -= random.randint(80, 150)
        x += random.randint(-200, 200)

generate_platforms()  # Geração inicial

def manage_platforms():
    """Gerencia plataformas: remove antigas e gera novas"""
    global platforms
    # Remove plataformas abaixo da câmera
    platforms = [p for p in platforms if p['rect'].bottom > camera_y - 200]
    # Gera novas se necessário
    while len(platforms) < 10:
        last_plat = max(platforms, key=lambda p: p['rect'].top, default={'rect': pygame.Rect(WIDTH//2, ground_y, 100, 20)})
        new_y = last_plat['rect'].top - random.randint(80, 150)
        new_x = max(0, min(last_plat['rect'].centerx + random.randint(-200, 200), WIDTH - 100))
        new_plat = create_platform(new_x, new_y)
        platforms.append(new_plat)

def regenerate_map():
    """Regenera o mapa completo ao tocar o chão após subir"""
    global platforms, camera_y, reached_platform_this_cycle
    platforms = []
    y = ground_y - 100
    x = WIDTH // 2 - 75
    for i in range(10):
        plat = create_platform(x, y)
        # 25% chance de mola na primeira plataforma (chão especial)
        if i == 0 and random.random() < 0.25:
            plat['type'] = 'spring'
            plat['spring_rect'] = pygame.Rect(plat['rect'].centerx - 15, plat['rect'].top - 15, 30, 30)
        platforms.append(plat)
        y -= random.randint(80, 150)
        x += random.randint(-200, 200)
    camera_y = 0
    reached_platform_this_cycle = False

# Funções de colisão
def check_platform_collision():
    """Verifica colisões com plataformas e chão"""
    global on_ground, can_double_jump, has_double_jumped, pig_vel_y, pig_y, last_safe_y, reached_platform_this_cycle, game_over
    pig_rect = pygame.Rect(pig_x, pig_y, pig_width, pig_height)
    on_ground_new = False
    collided = False
    for plat in platforms:
        if (plat['type'] == 'breakable' and plat['broken']):
            continue  # Ignora quebradas
        if plat['rect'].colliderect(pig_rect) and pig_vel_y > 0:
            pig_y = plat['rect'].top - pig_height
            pig_vel_y = 0
            on_ground_new = True
            last_safe_y = pig_y
            collided = True
            reached_platform_this_cycle = True
            if plat['type'] == 'breakable':
                plat['broken'] = True
                create_particles(plat['rect'].centerx, plat['rect'].bottom, 8, DIRT_BROWN, 'break')
            if plat['type'] == 'spring':
                pig_vel_y = super_jump_force
                create_particles(plat['rect'].centerx, plat['rect'].top, 15, None, 'super')
                print("BOING!")
                on_ground_new = False  # Não fica no chão na mola
            break  # Uma colisão por frame
    # Colisão com o chão
    if pig_rect.bottom >= ground_y:
        pig_y = ground_y - pig_height
        pig_vel_y = 0
        on_ground_new = True
        last_safe_y = pig_y
        collided = True
        if reached_platform_this_cycle:
            regenerate_map()
            reached_platform_this_cycle = False
    on_ground = on_ground_new
    if on_ground:
        can_double_jump = False
        has_double_jumped = False
    # Verificar game over por queda
    if not on_ground and pig_vel_y > 0 and reached_platform_this_cycle:
        fall_distance = abs(pig_y - last_safe_y)
        if fall_distance > max_safe_fall:
            game_over = True
            create_particles(pig_x + 25, pig_y + 25, 20, RED, 'crash')
            save_high_score(max_height_reached)
            global highscore
            highscore = max_height_reached

# Funções de partículas
def create_particles(x, y, count, color, p_type):
    """Cria partículas baseadas no tipo"""
    global particles
    if len(particles) + count > max_particles:
        return
    if p_type == 'super':
        colors = [BLUE if i % 2 == 0 else ORANGE for i in range(count)]
    elif p_type == 'double':
        colors = [YELLOW] * count
    elif p_type == 'normal':
        colors = [GRAY] * count
    elif p_type == 'break':
        colors = [DIRT_BROWN] * count
    elif p_type == 'crash':
        colors = [RED] * count
    else:
        colors = [color] * count if isinstance(color, tuple) else [color] * count
    for i in range(count):
        vel_x = random.uniform(-3, 3) if p_type in ['normal', 'double'] else random.uniform(-4, 4) if p_type == 'break' else random.uniform(-5, 5) if p_type == 'super' else random.uniform(-6, 6)
        if p_type == 'normal':
            vel_y = random.uniform(-4, -2)
            size = 4
            life = 30
        elif p_type == 'double':
            vel_y = random.uniform(-5, -3)
            size = 5
            life = 30
        elif p_type == 'super':
            vel_y = random.uniform(-8, -4)
            size = 6
            life = 40
        elif p_type == 'break':
            vel_y = random.uniform(-6, -2)
            size = 4
            life = 30
        elif p_type == 'crash':
            vel_y = random.uniform(-8, -4)
            size = random.randint(8, 12)
            life = 50
        particles.append({
            'x': float(x),
            'y': float(y),
            'vel_x': vel_x,
            'vel_y': vel_y,
            'life': life,
            'color': colors[i],
            'size': size
        })

def update_particles():
    """Atualiza física das partículas"""
    global particles
    for p in particles[:]:
        p['vel_y'] += 0.3  # Gravidade leve
        p['x'] += p['vel_x']
        p['y'] += p['vel_y']
        p['life'] -= 1
        if p['life'] <= 0:
            particles.remove(p)

# Função de câmera
def update_camera():
    """Atualiza posição da câmera com lerp suave"""
    global camera_y
    if pig_y < HEIGHT // 2 and pig_vel_y < 0:
        camera_target_y = pig_y - HEIGHT // 2
        camera_y += (camera_target_y - camera_y) * 0.1
    camera_y = max(0, camera_y)

# Função de input
def handle_input():
    """Processa input do jogador"""
    global pig_vel_x, on_ground, can_double_jump, has_double_jumped, pig_vel_y, space_pressed, pig_facing_right
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pig_vel_x = -5
        pig_facing_right = False
    elif keys[pygame.K_RIGHT]:
        pig_vel_x = 5
        pig_facing_right = True
    else:
        pig_vel_x = 0
    current_space = keys[pygame.K_SPACE]
    if current_space and not space_pressed and not game_over:
        if on_ground:
            pig_vel_y = jump_force
            create_particles(pig_x + 25, pig_y + 50, 5, GRAY, 'normal')
            can_double_jump = True
            has_double_jumped = False
        elif can_double_jump and not has_double_jumped:
            pig_vel_y = double_jump_force
            create_particles(pig_x + 25, pig_y + 25, 8, YELLOW, 'double')
            has_double_jumped = True
            can_double_jump = False
        space_pressed = True
    if not current_space:
        space_pressed = False
    pig_x += pig_vel_x
    # Wrap around lateral
    if pig_x < -pig_width:
        pig_x = WIDTH
    elif pig_x > WIDTH:
        pig_x = -pig_width

# Funções de desenho
def draw_platforms():
    """Desenha todas as plataformas"""
    for plat in platforms:
        rect = plat['rect']
        color = GRASS_GREEN if plat['type'] == 'normal' else DARK_GRAY if plat['type'] == 'breakable' else GRASS_GREEN
        screen_y = rect.y - camera_y
        pygame.draw.rect(screen, color, (rect.x, screen_y, rect.width, rect.height))
        if plat['type'] == 'spring' and plat['spring_rect']:
            s_rect = plat['spring_rect']
            screen_s_y = s_rect.y - camera_y
            pygame.draw.circle(screen, BLUE, (s_rect.centerx, int(screen_s_y + 15)), 15)
            pygame.draw.circle(screen, BLACK, (s_rect.centerx, int(screen_s_y + 15)), 15, 2)

def draw_player():
    """Desenha o porquinho com espelhamento"""
    img = pig_image
    if not pig_facing_right:
        img = pygame.transform.flip(img, True, False)
    screen.blit(img, (pig_x, pig_y - camera_y))

def draw_particles():
    """Desenha partículas"""
    for p in particles:
        screen_y = p['y'] - camera_y
        pygame.draw.circle(screen, p['color'], (int(p['x']), int(screen_y)), p['size'])

def draw_hud():
    """Desenha a HUD"""
    font = pygame.font.Font(None, 32)
    height_text = font.render(f"Altura: {current_height}m", True, WHITE)
    screen.blit(height_text, (10, 10))
    record_color = YELLOW if current_height > highscore else WHITE
    record_text = font.render(f"Recorde: {highscore}m", True, record_color)
    screen.blit(record_text, (WIDTH - 200, 10))
    # Novo recorde piscando
    if current_height > highscore and frame_count % 20 < 10:
        big_font = pygame.font.Font(None, 48)
        new_record = big_font.render("🔥 NOVO RECORDE! 🔥", True, YELLOW)
        screen.blit(new_record, (WIDTH // 2 - 150, 50))
    # Barra de progresso (proporcional à altura vs recorde, cor baseada em subida/descida)
    bar_x = WIDTH // 2 - 200
    bar_y = 80
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, 400, 20))
    fill_ratio = min(1.0, current_height / max(1, highscore))
    fill_width = int(400 * fill_ratio)
    bar_color = YELLOW if pig_vel_y < 0 else GRAY
    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, 20))
    # Indicador de pulo duplo
    if can_double_jump and not has_double_jumped:
        pygame.draw.circle(screen, YELLOW, (50, HEIGHT - 50), 20)
        small_font = pygame.font.Font(None, 20)
        text = small_font.render("DUPLO OK", True, BLACK)
        screen.blit(text, (30, HEIGHT - 55))
    # Botões virtuais
    btn_font = pygame.font.Font(None, 24)
    # Esquerda
    pygame.draw.rect(screen, LIGHT_GRAY, (10, HEIGHT - 60, 50, 50))
    left_text = btn_font.render("<", True, BLACK)
    screen.blit(left_text, (25, HEIGHT - 45))
    # Direita
    pygame.draw.rect(screen, LIGHT_GRAY, (70, HEIGHT - 60, 50, 50))
    right_text = btn_font.render(">", True, BLACK)
    screen.blit(right_text, (85, HEIGHT - 45))
    # Espaço
    pygame.draw.rect(screen, LIGHT_GRAY, (WIDTH - 60, HEIGHT - 60, 50, 50))
    sp_text = btn_font.render("SP", True, BLACK)
    screen.blit(sp_text, (WIDTH - 50, HEIGHT - 45))

def draw_debug():
    """Desenha informações de debug"""
    if debug_mode:
        font = pygame.font.Font(None, 24)
        y_pos = 50
        texts = [
            f"Altura: {current_height}m | Vel Y: {pig_vel_y:.1f} | Queda: {abs(pig_y - last_safe_y)/10:.0f}m",
            f"Ground: {on_ground} | Duplo: {can_double_jump and not has_double_jumped}",
            f"Câmera: {camera_y:.0f} | Plataformas: {len(platforms)} | Partículas: {len(particles)}",
            f"FPS: {clock.get_fps():.0f}"
        ]
        # Fundo semi-transparente
        bg_surf = pygame.Surface((400, len(texts) * 25 + 10))
        bg_surf.set_alpha(200)
        bg_surf.fill(BLACK)
        screen.blit(bg_surf, (10, y_pos - 5))
        for text in texts:
            txt = font.render(text, True, WHITE)
            screen.blit(txt, (15, y_pos))
            y_pos += 25

def draw_nuvens():
    """Desenha nuvens decorativas"""
    cloud_positions = [(100, 100), (300, 200), (500, 150), (200, 250), (600, 180)]
    for cx, cy in cloud_positions:
        screen_y = cy - camera_y
        if -100 < screen_y < HEIGHT + 100:
            # 3 círculos para nuvem
            pygame.draw.circle(screen, WHITE, (cx, int(screen_y)), 30)
            pygame.draw.circle(screen, WHITE, (cx - 25, int(screen_y)), 20)
            pygame.draw.circle(screen, WHITE, (cx + 25, int(screen_y)), 20)

def draw_chao():
    """Desenha o chão fixo na parte inferior"""
    pygame.draw.rect(screen, DIRT_BROWN, (0, HEIGHT - 100, WIDTH, 100))

def draw_game_over():
    """Desenha tela de game over"""
    if game_over:
        # Overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        # Textos
        font_big = pygame.font.Font(None, 72)
        go_text = font_big.render("GAME OVER", True, WHITE)
        screen.blit(go_text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
        font_med = pygame.font.Font(None, 36)
        height_text = font_med.render(f"Altura Final: {current_height}m", True, WHITE)
        screen.blit(height_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        record_text = font_med.render(f"Recorde: {highscore}m", True, WHITE)
        screen.blit(record_text, (WIDTH // 2 - 80, HEIGHT // 2))
        if current_height > load_high_score():  # Verifica original, mas já salvo
            new_record_text = font_med.render("NOVO RECORDE SALVO!", True, YELLOW)
            screen.blit(new_record_text, (WIDTH // 2 - 140, HEIGHT // 2 + 50))
        font_small = pygame.font.Font(None, 24)
        restart_text = font_small.render("Pressione ESPAÇO para Reiniciar", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - 140, HEIGHT // 2 + 100))

def draw_everything():
    """Desenha tudo na tela"""
    screen.fill(SKY_BLUE)
    draw_nuvens()
    draw_platforms()
    draw_player()
    draw_particles()
    draw_chao()
    draw_hud()
    draw_debug()
    draw_game_over()

# Função de reset
def reset_game():
    """Reseta o jogo para estado inicial"""
    global pig_x, pig_y, pig_vel_y, pig_vel_x, on_ground, can_double_jump, has_double_jumped, last_safe_y, game_over, game_over_timer, camera_y, particles, current_height, reached_platform_this_cycle, platforms, max_height_reached
    save_high_score(max_height_reached)  # Salva ao resetar
    pig_x = WIDTH // 2 - 25
    pig_y = HEIGHT - 150
    pig_vel_y = 0
    pig_vel_x = 0
    on_ground = True
    can_double_jump = False
    has_double_jumped = False
    last_safe_y = pig_y
    game_over = False
    game_over_timer = 0
    camera_y = 0
    particles = []
    current_height = 0
    reached_platform_this_cycle = False
    regenerate_map()
    max_height_reached = highscore  # Reset para session

# Loop principal
running = True
while running:
    frame_count += 1
    clock.tick(FPS)
    
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score(max_height_reached)
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_high_score(max_height_reached)
                running = False
            if event.key == pygame.K_F3:
                debug_mode = not debug_mode
            if event.key == pygame.K_SPACE:
                if game_over and game_over_timer > 60:
                    reset_game()
    
    if not game_over:
        # Input
        handle_input()
        # Física
        pig_vel_y += gravity
        pig_y += pig_vel_y
        # Colisões
        check_platform_collision()
        # Altura e recorde
        current_height = max(0, int((ground_y - pig_y) / 10))
        if current_height > max_height_reached:
            max_height_reached = current_height
            check_and_save_high_score(current_height, highscore)
        # Plataformas
        manage_platforms()
        # Câmera
        update_camera()
        # Partículas
        update_particles()
    else:
        game_over_timer += 1
    
    # Desenho
    draw_everything()
    pygame.display.flip()

# Finalização
save_high_score(max_height_reached)  # Salva ao fechar
pygame.quit()
sys.exit()