# ═══════════════════════════════════════════════════════════════════
# JOGO DO PORQUINHO
# Gerado por IA(gpt5 mini) com base em prompt detalhado.
# ═══════════════════════════════════════════════════════════════════

# 1. IMPORTS
import pygame
import random
import sys
import json
from datetime import datetime

# 2. INICIALIZAÇÃO PYGAME
pygame.init()
pygame.font.init()

# 3. CONFIGURAÇÕES BÁSICAS
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Porquinho")
clock = pygame.time.Clock()
FPS = 60

# 4. PALETA DE CORES
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

# 5. CARREGAMENTO DE RECURSOS (IMAGEM E FONTES)
try:
    original_pig_image = pygame.image.load('pig.png').convert_alpha()
    pig_image = pygame.transform.scale(original_pig_image, (50, 50))
    use_sprite = True
    print("Sprite 'pig.png' carregado com sucesso.")
except FileNotFoundError:
    pig_image = pygame.Surface((50, 50))
    pig_image.fill(PINK)
    use_sprite = False
    print("AVISO: 'pig.png' não encontrado. Usando um retângulo rosa como fallback.")

font_small = pygame.font.SysFont('Consolas', 24)
font_medium = pygame.font.SysFont('Consolas', 32)
font_large = pygame.font.SysFont('Consolas', 48)
font_xlarge = pygame.font.SysFont('Consolas', 72)

# 6. VARIÁVEIS GLOBAIS DO JOGO

# Física
gravity = 0.8
jump_force = -15
double_jump_force = -12
super_jump_force = -30

# Jogador
pig_width, pig_height = 50, 50
pig_x, pig_y = 0, 0
pig_vel_x, pig_vel_y = 0, 0
pig_speed = 5
pig_facing_right = True
on_ground = True
can_double_jump = False
has_double_jumped = False
space_released_since_jump = True

# Câmera
camera_y = 0.0
camera_target_y = 0.0

# Plataformas
platforms = []
ground_y = HEIGHT - 100
platform_buffer = 10 # Manter 10 plataformas acima da câmera

# Pontuação e Estado
current_height = 0
max_height_reached = 0
last_safe_y = ground_y
max_safe_fall = 600 # 60 metros * 10px/m
reached_platform_this_cycle = False

# Partículas
particles = []

# Estado do Jogo
game_over = False
game_over_timer = 0
debug_mode = False
running = True

# 7. FUNÇÕES DE PERSISTÊNCIA (HIGHSCORE)

def load_high_score():
    """Carrega o recorde do arquivo highscore.json."""
    try:
        with open('highscore.json', 'r') as f:
            data = json.load(f)
            print(f"Recorde carregado: {data['highscore']}m")
            return int(data['highscore'])
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        print("Arquivo de recorde não encontrado ou inválido. Começando com 0.")
        return 0

def save_high_score(score):
    """Salva o recorde e o timestamp em highscore.json."""
    data = {
        "highscore": score,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open('highscore.json', 'w') as f:
        json.dump(data, f, indent=4)
    # print(f"Novo recorde salvo: {score}m")

def check_and_save_high_score(current_score, high_score):
    """Verifica se o recorde foi batido e salva se necessário."""
    if current_score > high_score:
        save_high_score(current_score)
        return True
    return False

# 8. FUNÇÕES DE PARTÍCULAS

def create_particles(x, y, p_type):
    """Gera uma rajada de partículas baseada em um evento."""
    particle_specs = {
        "jump": {"count": 5, "color": GRAY, "vel_range_x": (-3, 3), "vel_range_y": (-4, -2), "life": 30, "size": 4},
        "double_jump": {"count": 8, "color": YELLOW, "vel_range_x": (-4, 4), "vel_range_y": (-5, -3), "life": 30, "size": 5},
        "spring": {"count": 15, "colors": [BLUE, ORANGE], "vel_range_x": (-5, 5), "vel_range_y": (-8, -4), "life": 40, "size": 6},
        "break": {"count": 8, "color": DIRT_BROWN, "vel_range_x": (-4, 4), "vel_range_y": (-6, -2), "life": 30, "size": 4},
        "crash": {"count": 20, "color": RED, "vel_range_x": (-6, 6), "vel_range_y": (-8, -4), "life": 50, "size": (8, 12)}
    }
    spec = particle_specs.get(p_type)
    if not spec: return

    for _ in range(spec["count"]):
        if len(particles) >= 200: break # Limite de partículas
        
        particle = {
            "x": x, "y": y,
            "vel_x": random.uniform(*spec["vel_range_x"]),
            "vel_y": random.uniform(*spec["vel_range_y"]),
            "life": spec["life"],
            "color": random.choice(spec["colors"]) if "colors" in spec else spec["color"],
            "size": random.randint(*spec["size"]) if isinstance(spec["size"], tuple) else spec["size"]
        }
        particles.append(particle)

def update_particles():
    """Atualiza a posição, vida e física de todas as partículas."""
    for p in particles[:]:
        p["vel_y"] += 0.3 # Gravidade das partículas
        p["x"] += p["vel_x"]
        p["y"] += p["vel_y"]
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)

# 9. FUNÇÕES DE PLATAFORMAS

def create_platform(y_pos):
    """Cria uma única plataforma com tipo, largura e posição aleatórios."""
    rand_val = random.random()
    if rand_val < 0.6:
        p_type = "normal"
        width = random.randint(100, 150)
    elif rand_val < 0.9:
        p_type = "breakable"
        width = random.randint(80, 120)
    else:
        p_type = "spring"
        width = random.randint(100, 150)

    x = random.randint(-width // 2, WIDTH - width // 2)
    x = max(0, min(WIDTH - width, x + random.randint(-200, 200))) # Variação horizontal

    platform = {
        "rect": pygame.Rect(x, y_pos, width, 20),
        "type": p_type,
        "broken": False
    }
    if p_type == "spring":
        platform["spring_rect"] = pygame.Rect(x + width/2 - 15, y_pos - 15, 30, 15)
    else:
        platform["spring_rect"] = None
        
    return platform

def generate_initial_platforms():
    """Gera o layout inicial de plataformas."""
    global platforms
    platforms = []
    
    # Plataforma inicial segura
    platforms.append({"rect": pygame.Rect(WIDTH//2 - 50, ground_y - 80, 100, 20), "type": "normal", "broken": False, "spring_rect": None})
    
    last_y = ground_y - 80
    for _ in range(20): # Gerar um bom número inicial
        y_spacing = random.randint(80, 150)
        new_y = last_y - y_spacing
        platforms.append(create_platform(new_y))
        last_y = new_y

def manage_platforms():
    """Remove plataformas antigas e gera novas conforme o jogador sobe."""
    global platforms
    
    # Remove plataformas muito abaixo da câmera
    platforms = [p for p in platforms if p["rect"].top < ground_y - camera_y + HEIGHT + 200]
    
    # Gera novas plataformas se necessário
    highest_platform_y = min(p["rect"].y for p in platforms) if platforms else ground_y
    while highest_platform_y > camera_y - platform_buffer * 150:
        y_spacing = random.randint(80, 150)
        new_y = highest_platform_y - y_spacing
        platforms.append(create_platform(new_y))
        highest_platform_y = new_y

def regenerate_all_platforms():
    """Limpa todas as plataformas e cria um novo layout."""
    global platforms, reached_platform_this_cycle
    platforms = []
    reached_platform_this_cycle = False
    
    # Chance de mola no chão
    if random.random() < 0.25:
        width = 120
        x = WIDTH // 2 - width // 2
        platforms.append({
            "rect": pygame.Rect(x, ground_y - 20, width, 20),
            "type": "spring",
            "broken": False,
            "spring_rect": pygame.Rect(x + width/2 - 15, ground_y - 20 - 15, 30, 15)
        })
        print("Mola especial gerada no chão!")
    
    generate_initial_platforms()


# 10. FUNÇÃO DE RESET

def reset_game():
    """Reseta o estado do jogo para o início."""
    global pig_x, pig_y, pig_vel_x, pig_vel_y, on_ground, can_double_jump, has_double_jumped
    global camera_y, particles, game_over, game_over_timer, current_height, last_safe_y
    
    # Salva o recorde final
    check_and_save_high_score(max_height_reached, high_score)

    pig_x = WIDTH // 2 - pig_width // 2
    pig_y = ground_y - pig_height
    pig_vel_x = 0
    pig_vel_y = 0
    on_ground = True
    can_double_jump = False
    has_double_jumped = False
    
    camera_y = 0
    particles = []
    
    game_over = False
    game_over_timer = 0
    
    current_height = 0
    last_safe_y = ground_y
    
    regenerate_all_platforms()
    print("Jogo reiniciado.")


# 11. FUNÇÕES DE DESENHO

def draw_text(text, font, color, surface, x, y, center=False):
    """Função auxiliar para desenhar texto na tela."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

def draw_elements():
    """Desenha todos os elementos do jogo (jogador, plataformas, etc.)."""
    # Céu
    screen.fill(SKY_BLUE)
    
    # Chão
    pygame.draw.rect(screen, DIRT_BROWN, (0, ground_y - camera_y, WIDTH, HEIGHT - (ground_y - camera_y)))
    pygame.draw.rect(screen, GRASS_GREEN, (0, ground_y - camera_y, WIDTH, 20))

    # Nuvens (posições fixas que se movem com a câmera)
    cloud_positions = [(100, 100), (500, 200), (250, 150), (650, 250), (400, 180)]
    for cx, cy in cloud_positions:
        pygame.draw.circle(screen, WHITE, (cx, cy - camera_y * 0.5), 30) # Movimento parallax
        pygame.draw.circle(screen, WHITE, (cx - 25, cy - camera_y * 0.5 + 10), 20)
        pygame.draw.circle(screen, WHITE, (cx + 25, cy - camera_y * 0.5 + 10), 20)

    # Partículas
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"] - camera_y)), p["size"])
        
    # Plataformas
    for p in platforms:
        if not p["broken"]:
            color = GRASS_GREEN if p["type"] in ["normal", "spring"] else DARK_GRAY
            pygame.draw.rect(screen, color, (p["rect"].x, p["rect"].y - camera_y, p["rect"].width, p["rect"].height))
            pygame.draw.rect(screen, BLACK, (p["rect"].x, p["rect"].y - camera_y, p["rect"].width, p["rect"].height), 1)
            if p["type"] == "spring" and p["spring_rect"]:
                pygame.draw.ellipse(screen, BLUE, (p["spring_rect"].x, p["spring_rect"].y - camera_y, p["spring_rect"].width, p["spring_rect"].height))

    # Jogador
    current_pig_image = pig_image
    if not pig_facing_right and use_sprite:
        current_pig_image = pygame.transform.flip(pig_image, True, False)
    screen.blit(current_pig_image, (pig_x, pig_y - camera_y))

def draw_hud():
    """Desenha a interface do usuário (HUD)."""
    # Altura e Recorde
    draw_text(f"Altura: {current_height}m", font_medium, WHITE, screen, 10, 10)
    recorde_color = YELLOW if current_height > high_score else WHITE
    draw_text(f"Recorde: {high_score}m", font_medium, recorde_color, screen, WIDTH - 210, 10)

    # Indicador de Novo Recorde
    if current_height > high_score and (pygame.time.get_ticks() // 300) % 2 == 0:
        draw_text("🔥 NOVO RECORDE! 🔥", font_large, YELLOW, screen, WIDTH // 2, 20, center=True)
    
    # Barra de Progresso
    progress = min(1, max(0, (last_safe_y - pig_y) / max_safe_fall))
    progress_color = YELLOW if pig_vel_y < 0 else GRAY
    pygame.draw.rect(screen, DARK_GRAY, (WIDTH/2 - 200, 50, 400, 20))
    pygame.draw.rect(screen, progress_color, (WIDTH/2 - 200, 50, 400 * progress, 20))

    # Indicador de Pulo Duplo
    if can_double_jump:
        pygame.draw.circle(screen, YELLOW, (35, HEIGHT - 85), 20)
        draw_text("DUPLO OK", font_small, BLACK, screen, 65, HEIGHT - 95)
        
    # Botões Virtuais
    s = pygame.Surface((50, 50), pygame.SRCALPHA)
    s.fill((*LIGHT_GRAY, 128))
    # Esquerda
    screen.blit(s, (10, HEIGHT - 60))
    draw_text("<", font_large, BLACK, screen, 35, HEIGHT - 45, center=True)
    # Direita
    screen.blit(s, (70, HEIGHT - 60))
    draw_text(">", font_large, BLACK, screen, 95, HEIGHT - 45, center=True)
    # Espaço
    screen.blit(s, (WIDTH - 60, HEIGHT - 60))
    draw_text("SP", font_medium, BLACK, screen, WIDTH - 35, HEIGHT - 45, center=True)


def draw_debug_info():
    """Desenha a sobreposição de informações de debug."""
    fall_distance = max(0, int((pig_y - last_safe_y) / 10))
    info = [
        "--- DEBUG INFO (F3) ---",
        f"Altura: {current_height}m | Vel Y: {pig_vel_y:.1f} | Queda: {fall_distance}m",
        f"Ground: {on_ground} | Duplo OK: {can_double_jump} | Duplo Usado: {has_double_jumped}",
        f"Câmera Y: {int(camera_y)} | Plataformas: {len(platforms)} | Partículas: {len(particles)}",
        f"FPS: {int(clock.get_fps())}"
    ]
    
    bg_surface = pygame.Surface((450, 120), pygame.SRCALPHA)
    bg_surface.fill((*BLACK, 180))
    screen.blit(bg_surface, (5, 50))
    
    for i, line in enumerate(info):
        draw_text(line, font_small, WHITE, screen, 10, 55 + i * 25)

def draw_game_over_screen():
    """Desenha a tela de Game Over."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((*BLACK, 200))
    screen.blit(overlay, (0, 0))
    
    draw_text("GAME OVER", font_xlarge, RED, screen, WIDTH // 2, HEIGHT // 4, center=True)
    draw_text(f"Altura Final: {current_height}m", font_medium, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 40, center=True)
    
    recorde_color = YELLOW if max_height_reached > high_score else WHITE
    draw_text(f"Recorde: {high_score}m", font_medium, recorde_color, screen, WIDTH // 2, HEIGHT // 2, center=True)
    
    if max_height_reached > high_score:
        draw_text("NOVO RECORDE SALVO!", font_large, YELLOW, screen, WIDTH // 2, HEIGHT // 2 + 50, center=True)
    
    if game_over_timer > 60:
        if (pygame.time.get_ticks() // 500) % 2 == 0: # Piscar texto
            draw_text("Pressione ESPAÇO para Reiniciar", font_small, WHITE, screen, WIDTH // 2, HEIGHT * 0.75, center=True)


# 12. INÍCIO DO JOGO
high_score = load_high_score()
reset_game()

# 13. LOOP PRINCIPAL
while running:
    clock.tick(FPS)
    
    # --- 1. EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_released_since_jump = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_F3:
                debug_mode = not debug_mode
                print(f"Debug mode {'ativado' if debug_mode else 'desativado'}.")
            if event.key == pygame.K_SPACE:
                if game_over and game_over_timer > 60:
                    reset_game()
                    high_score = load_high_score() # Recarregar caso tenha mudado
                elif not game_over:
                    # Pulo Normal
                    if on_ground:
                        pig_vel_y = jump_force
                        on_ground = False
                        can_double_jump = True
                        has_double_jumped = False
                        space_released_since_jump = False
                        create_particles(pig_x + pig_width / 2, pig_y + pig_height, "jump")
                    # Pulo Duplo
                    elif can_double_jump and not has_double_jumped and space_released_since_jump:
                        pig_vel_y = double_jump_force
                        has_double_jumped = True
                        create_particles(pig_x + pig_width / 2, pig_y, "double_jump")
    
    if not game_over:
        # --- 2. INPUT ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            pig_x -= pig_speed
            pig_facing_right = False
        if keys[pygame.K_RIGHT]:
            pig_x += pig_speed
            pig_facing_right = True
            
        # --- 3. FÍSICA ---
        if not on_ground:
            pig_vel_y += gravity
        pig_y += pig_vel_y
        
        # --- 4. COLISÕES ---
        pig_rect = pygame.Rect(pig_x, pig_y, pig_width, pig_height)
        
        if pig_vel_y > 0: # Só checar colisão ao cair
            for p in platforms:
                if not p["broken"] and pig_rect.colliderect(p["rect"]):
                    # Checar se o porco está acima da plataforma
                    if pig_rect.bottom < p["rect"].bottom:
                        pig_y = p["rect"].top - pig_height
                        pig_vel_y = 0
                        on_ground = True
                        can_double_jump = False
                        has_double_jumped = False
                        last_safe_y = pig_y
                        reached_platform_this_cycle = True
                        
                        # Efeitos da plataforma
                        if p["type"] == "breakable":
                            p["broken"] = True
                            create_particles(p["rect"].centerx, p["rect"].centery, "break")
                        elif p["type"] == "spring":
                            pig_vel_y = super_jump_force
                            on_ground = False
                            can_double_jump = True # Permite pulo duplo após mola
                            has_double_jumped = False
                            create_particles(p["rect"].centerx, p["rect"].y, "spring")
                            print("BOING!")
                        break # Evitar colisões múltiplas no mesmo frame

        # --- 5. LIMITES DE TELA ---
        # Wrap around horizontal
        if pig_x > WIDTH:
            pig_x = -pig_width
        elif pig_x < -pig_width:
            pig_x = WIDTH
            
        # Tocou o chão (após ter subido)
        if pig_y + pig_height >= ground_y:
            pig_y = ground_y - pig_height
            pig_vel_y = 0
            if not on_ground: # Se estava no ar antes de tocar o chão
                if reached_platform_this_cycle:
                    print("Retornou ao chão. Regenerando mapa...")
                    regenerate_all_platforms()
                on_ground = True
                can_double_jump = False
                has_double_jumped = False
                last_safe_y = pig_y

        # --- 6. ALTURA E RECORDE ---
        current_height = max(0, int((ground_y - pig_y) / 10))
        if current_height > max_height_reached:
            max_height_reached = current_height
            # Salvar a cada 10m de novo recorde
            if max_height_reached > high_score and max_height_reached % 10 == 0:
                 save_high_score(max_height_reached)

        # --- 7. CONDIÇÃO DE GAME OVER ---
        if not on_ground and pig_vel_y > 0:
            fall_distance = pig_y - last_safe_y
            if fall_distance > max_safe_fall and reached_platform_this_cycle:
                game_over = True
                create_particles(pig_x + pig_width/2, pig_y + pig_height/2, "crash")
                print(f"GAME OVER: Queda fatal de {int(fall_distance/10)}m.")
                check_and_save_high_score(max_height_reached, high_score)
                high_score = load_high_score() # Atualiza o recorde para a tela de game over

        # --- 8. GERENCIAMENTO DE PLATAFORMAS ---
        manage_platforms()
        
        # --- 9. CÂMERA ---
        if pig_y < HEIGHT // 2 and pig_vel_y < 0:
            camera_target_y = pig_y - HEIGHT // 2
            camera_y += (camera_target_y - camera_y) * 0.1

        # --- 10. PARTÍCULAS ---
        update_particles()
        
    else: # Se game_over == True
        game_over_timer += 1
        
    # --- 11. DESENHO ---
    draw_elements()
    draw_hud()
    
    if debug_mode:
        draw_debug_info()
        
    if game_over:
        draw_game_over_screen()
        
    pygame.display.flip()

# 14. FINALIZAÇÃO
print("Saindo do jogo...")
# Salva o recorde final ao fechar
check_and_save_high_score(max_height_reached, high_score)
pygame.quit()
sys.exit()