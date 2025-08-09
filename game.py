import pygame
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Porquinho")

# Carregar imagem do porquinho
try:
    pig_image_original = pygame.image.load("pig.png")
    # Redimensionar a imagem para o tamanho desejado
    pig_image = pygame.transform.scale(pig_image_original, (50, 50))
    # Criar versão espelhada para quando move para a esquerda
    pig_image_flipped = pygame.transform.flip(pig_image, True, False)
    using_image = True
    print("✅ Imagem do porquinho carregada com sucesso!")
except pygame.error as e:
    print(f"❌ Não foi possível carregar a imagem: {e}")
    pig_image = None
    pig_image_flipped = None
    using_image = False

# Tentar carregar imagem de fumaça (opcional)
try:
    smoke_image = pygame.image.load("smoke.png")
    smoke_image = pygame.transform.scale(smoke_image, (16, 16))
    using_smoke_image = True
    print("✅ Imagem de fumaça carregada com sucesso!")
except (pygame.error, FileNotFoundError):
    smoke_image = None
    using_smoke_image = False
    print("ℹ️ Usando efeito de fumaça com formas geométricas")

# Cores
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

# FPS
clock = pygame.time.Clock()
FPS = 60

# Plataforma
platform_height = 100

# Porquinho
pig_width, pig_height = 50, 50
pig_x, pig_y = WIDTH // 2, HEIGHT - 150
pig_speed = 5

# Sistema de pulo e gravidade
pig_vel_y = 0
gravity = 0.8
jump_strength = -15
on_ground = True
ground_y = HEIGHT - platform_height - pig_height

# Sistema de pulo duplo
can_double_jump = False
has_double_jumped = False
double_jump_strength = -12  # Pulo duplo é um pouco mais fraco
space_was_pressed = False   # Para detectar quando a tecla foi soltada

# Direção do porquinho (para sprite espelhado)
pig_facing_right = True

# Sistema de pontuação por altura
max_height_reached = 0
current_height = 0

# Sistema de câmera
camera_y = 0
camera_target_y = 0

# Sistema de partículas de fumaça para o pulo
smoke_particles = []
import random

# Sistema de plataformas suspensas
platforms = []

# Função para criar plataformas
def create_platforms():
    """Cria plataformas suspensas em diferentes alturas"""
    global platforms
    platforms = []
    
    # Plataformas em diferentes níveis
    platform_configs = [
        # [x, y, width, height, cor]
        [150, HEIGHT - 200, 120, 20, DIRT_BROWN],  # Primeira plataforma
        [350, HEIGHT - 280, 100, 20, DIRT_BROWN],  # Segunda plataforma
        [550, HEIGHT - 240, 110, 20, DIRT_BROWN],  # Terceira plataforma (mais baixa)
        [80, HEIGHT - 360, 90, 20, DIRT_BROWN],    # Quarta plataforma
        [450, HEIGHT - 420, 100, 20, DIRT_BROWN],  # Quinta plataforma
        [200, HEIGHT - 500, 120, 20, DIRT_BROWN],  # Sexta plataforma
        [600, HEIGHT - 380, 80, 20, DIRT_BROWN],   # Sétima plataforma
        [100, HEIGHT - 580, 100, 20, DIRT_BROWN],  # Oitava plataforma
        [400, HEIGHT - 650, 90, 20, DIRT_BROWN],   # Nona plataforma
        [300, HEIGHT - 720, 150, 20, (139, 100, 19)], # Plataforma especial (cor diferente)
    ]
    
    for config in platform_configs:
        platform = {
            'x': config[0],
            'y': config[1],
            'width': config[2],
            'height': config[3],
            'color': config[4],
            'rect': pygame.Rect(config[0], config[1], config[2], config[3])
        }
        platforms.append(platform)

# Função para verificar colisão com plataformas
def check_platform_collision():
    """Verifica se o porquinho está colidindo com alguma plataforma"""
    global pig_y, pig_vel_y, on_ground, can_double_jump, has_double_jumped
    
    # Área de colisão do porquinho
    pig_left = pig_x
    pig_right = pig_x + pig_width
    pig_bottom = pig_y + pig_height
    pig_top = pig_y
    
    for platform in platforms:
        platform_left = platform['x']
        platform_right = platform['x'] + platform['width']
        platform_top = platform['y']
        platform_bottom = platform['y'] + platform['height']
        
        # Verificar se há sobreposição horizontal
        if pig_right > platform_left and pig_left < platform_right:
            
            # Verificar se está caindo sobre a plataforma (aproximando-se do topo)
            if pig_vel_y > 0:  # Caindo
                # Verificar se o porquinho estava acima da plataforma no frame anterior
                # e agora está na posição de aterrissagem
                if pig_bottom >= platform_top and pig_top < platform_bottom:
                    # Posicionar o porquinho exatamente em cima da plataforma
                    pig_y = platform_top - pig_height
                    pig_vel_y = 0
                    on_ground = True
                    # Reset do sistema de pulo duplo quando pousa em plataforma
                    can_double_jump = False
                    has_double_jumped = False
                    return True
    
    return False

# Função para desenhar plataformas
def draw_platforms():
    """Desenha todas as plataformas suspensas"""
    for platform in platforms:
        # Ajustar posição baseada na câmera
        adjusted_y = platform['y'] + camera_y
        
        # Só desenhar se estiver visível na tela
        if -50 <= adjusted_y <= HEIGHT + 50:
            adjusted_rect = pygame.Rect(platform['x'], adjusted_y, platform['width'], platform['height'])
            
            # Verificar se o porquinho está em cima desta plataforma
            pig_on_platform = (on_ground and 
                             pig_x + pig_width > platform['x'] and 
                             pig_x < platform['x'] + platform['width'] and
                             abs((pig_y + pig_height) - platform['y']) < 5)
            
            # Destacar plataforma se porquinho estiver em cima
            platform_color = (200, 150, 50) if pig_on_platform else platform['color']
            
            # Desenhar plataforma principal
            pygame.draw.rect(screen, platform_color, adjusted_rect)
            # Desenhar grama em cima
            grass_rect = pygame.Rect(platform['x'], adjusted_y - 5, platform['width'], 5)
            grass_color = (50, 200, 50) if pig_on_platform else GRASS_GREEN
            pygame.draw.rect(screen, grass_color, grass_rect)
            
            # Adicionar bordas para melhor visual
            border_color = YELLOW if pig_on_platform else BLACK
            pygame.draw.rect(screen, border_color, adjusted_rect, 2)

# Função para atualizar câmera
def update_camera():
    """Atualiza a posição da câmera para seguir o porquinho"""
    global camera_y, camera_target_y
    
    # Câmera deve seguir o porquinho quando ele sobe
    camera_target_y = max(0, -(pig_y - HEIGHT + 200))  # Mantém o porquinho na parte inferior da tela
    
    # Suavizar movimento da câmera
    camera_y += (camera_target_y - camera_y) * 0.1

# Variáveis para controle de teclas pressionadas
left_pressed = False
right_pressed = False
space_pressed = False

# Configurações dos botões de controle na tela
button_size = 50
button_margin = 10
left_button_x = button_margin
right_button_x = left_button_x + button_size + button_margin
space_button_x = right_button_x + button_size + button_margin
buttons_y = HEIGHT - button_size - button_margin

# Função para criar partículas de fumaça quando pula
def create_jump_smoke(x, y, is_double_jump=False):
    """Cria partículas de fumaça na posição do pulo"""
    particle_count = 12 if is_double_jump else 8  # Mais partículas no pulo duplo
    
    for i in range(particle_count):
        particle = {
            'x': x + pig_width // 2 + random.randint(-15, 15),
            'y': y + pig_height // 2 + random.randint(-10, 10) if is_double_jump else y + pig_height + random.randint(-5, 5),
            'vel_x': random.uniform(-3, 3) if is_double_jump else random.uniform(-2, 2),
            'vel_y': random.uniform(-2, -4) if is_double_jump else random.uniform(-1, -3),
            'size': random.randint(4, 10) if is_double_jump else random.randint(3, 8),
            'life': random.randint(20, 35) if is_double_jump else random.randint(15, 30),
            'max_life': random.randint(20, 35) if is_double_jump else random.randint(15, 30),
            'color_type': 'double' if is_double_jump else 'normal'
        }
        particle['max_life'] = particle['life']
        smoke_particles.append(particle)

# Função para atualizar e desenhar partículas de fumaça
def update_smoke_particles():
    """Atualiza e desenha todas as partículas de fumaça"""
    global smoke_particles
    
    # Atualizar partículas existentes
    for particle in smoke_particles[:]:  # Usar slice para poder remover durante iteração
        # Atualizar posição
        particle['x'] += particle['vel_x']
        particle['y'] += particle['vel_y']
        particle['vel_y'] += 0.1  # Leve gravidade para baixo
        particle['life'] -= 1
        
        # Calcular transparência baseada na vida restante
        alpha = int(255 * (particle['life'] / particle['max_life']))
        alpha = max(0, min(255, alpha))
        
        # Remover partícula se vida acabou
        if particle['life'] <= 0:
            smoke_particles.remove(particle)
            continue
        
        # Desenhar partícula (ajustada pela câmera)
        adjusted_particle_y = particle['y'] + camera_y
        
        if using_smoke_image and smoke_image:
            # Usar imagem de fumaça se disponível
            # Criar superfície com transparência
            temp_surface = smoke_image.copy()
            temp_surface.set_alpha(alpha)
            screen.blit(temp_surface, (int(particle['x'] - 8), int(adjusted_particle_y - 8)))
        else:
            # Usar círculo se não tiver imagem - cores diferentes para pulo duplo
            if particle.get('color_type') == 'double':
                color = (255, 255, 150) if alpha > 128 else (200, 200, 100)  # Amarelado para pulo duplo
            else:
                color = (200, 200, 200) if alpha > 128 else (150, 150, 150)  # Cinza para pulo normal
            
            size = max(1, int(particle['size'] * (particle['life'] / particle['max_life'])))
            pygame.draw.circle(screen, color, (int(particle['x']), int(adjusted_particle_y)), size)

# Função para desenhar HUD (pontuação e altura)
def draw_hud():
    """Desenha informações do jogo (altura, pontuação)"""
    font_large = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    
    # Calcular altura atual (quanto mais alto, maior o valor)
    current_height = max(0, int((ground_y - pig_y) / 10))  # Dividir por 10 para valores mais legíveis
    
    # Atualizar altura máxima
    global max_height_reached
    if current_height > max_height_reached:
        max_height_reached = current_height
    
    # Desenhar altura atual
    height_text = font_large.render(f"Altura: {current_height}m", True, WHITE)
    screen.blit(height_text, (WIDTH - 250, 10))
    
    # Desenhar recorde
    record_text = font_small.render(f"Recorde: {max_height_reached}m", True, YELLOW)
    screen.blit(record_text, (WIDTH - 250, 50))
    
    # Indicador de progresso visual
    if current_height > 0:
        progress_width = min(200, current_height * 2)
        pygame.draw.rect(screen, (0, 255, 0), (WIDTH - 250, 80, progress_width, 10))
        pygame.draw.rect(screen, WHITE, (WIDTH - 250, 80, 200, 10), 2)

# Função para desenhar indicador de objetivo
def draw_objective():
    """Desenha o objetivo do jogo"""
    font = pygame.font.Font(None, 28)
    objective_text = font.render("OBJETIVO: Suba o mais alto possível!", True, (255, 215, 0))
    text_rect = objective_text.get_rect(center=(WIDTH // 2, 30))
    
    # Fundo semi-transparente
    pygame.draw.rect(screen, (0, 0, 0, 150), text_rect.inflate(20, 10))
    screen.blit(objective_text, text_rect)

# Função para desenhar nuvens
def draw_cloud(x, y):
    pygame.draw.circle(screen, WHITE, (x, y), 20)
    pygame.draw.circle(screen, WHITE, (x + 20, y), 25)
    pygame.draw.circle(screen, WHITE, (x + 40, y), 20)

# Função para desenhar botão de seta
def draw_arrow_button(x, y, direction, pressed):
    # Cor do botão baseada se está pressionado
    button_color = YELLOW if pressed else LIGHT_GRAY
    border_color = BLACK
    
    # Desenhar botão
    pygame.draw.rect(screen, button_color, (x, y, button_size, button_size))
    pygame.draw.rect(screen, border_color, (x, y, button_size, button_size), 2)
    
    # Desenhar seta
    center_x = x + button_size // 2
    center_y = y + button_size // 2
    arrow_size = 15
    
    if direction == "left":
        # Seta para esquerda
        points = [
            (center_x + arrow_size//2, center_y - arrow_size),
            (center_x - arrow_size//2, center_y),
            (center_x + arrow_size//2, center_y + arrow_size)
        ]
    else:  # direction == "right"
        # Seta para direita
        points = [
            (center_x - arrow_size//2, center_y - arrow_size),
            (center_x + arrow_size//2, center_y),
            (center_x - arrow_size//2, center_y + arrow_size)
        ]
    
    pygame.draw.polygon(screen, BLACK, points)

# Função para desenhar botão de espaço (pulo)
def draw_space_button(x, y, pressed):
    # Cor do botão baseada se está pressionado
    button_color = YELLOW if pressed else LIGHT_GRAY
    border_color = BLACK
    
    # Desenhar botão
    pygame.draw.rect(screen, button_color, (x, y, button_size, button_size))
    pygame.draw.rect(screen, border_color, (x, y, button_size, button_size), 2)
    
    # Desenhar texto "SPACE"
    font = pygame.font.Font(None, 18)
    text = font.render("SPACE", True, BLACK)
    text_rect = text.get_rect(center=(x + button_size//2, y + button_size//2))
    screen.blit(text, text_rect)

# Função para desenhar instruções na tela
def draw_instructions():
    font = pygame.font.Font(None, 20)  # Fonte menor para economizar espaço
    instructions = [
        "Controles:",
        "← → Mover | ESPAÇO Pular/Duplo",
        "🎯 Use plataformas para subir!"
    ]
    
    # Adicionar informação sobre pulo duplo
    if can_double_jump:
        instructions.append("⭐ Pulo duplo disponível!")
    elif has_double_jumped:
        instructions.append("🚫 Pulo duplo usado")
    
    y_offset = 10
    for i, instruction in enumerate(instructions):
        if i == 0:
            color = WHITE
        elif "Pulo duplo disponível" in instruction:
            color = (100, 255, 100)  # Verde brilhante
        elif "Pulo duplo usado" in instruction:
            color = (255, 100, 100)  # Vermelho
        elif "plataformas" in instruction:
            color = (100, 200, 255)  # Azul claro
        else:
            color = LIGHT_GRAY
        text = font.render(instruction, True, color)
        screen.blit(text, (10, y_offset + i * 20))

# Função para mostrar efeito de tecla pressionada
def draw_key_effect():
    font = pygame.font.Font(None, 36)
    effect_y = HEIGHT // 2 - 100
    
    if left_pressed:
        text = font.render("← ESQUERDA", True, YELLOW)
        text_rect = text.get_rect(center=(WIDTH // 2, effect_y))
        # Fundo semi-transparente
        pygame.draw.rect(screen, (0, 0, 0, 128), text_rect.inflate(20, 10))
        screen.blit(text, text_rect)
    
    if right_pressed:
        text = font.render("DIREITA →", True, YELLOW)
        text_rect = text.get_rect(center=(WIDTH // 2, effect_y))
        # Fundo semi-transparente
        pygame.draw.rect(screen, (0, 0, 0, 128), text_rect.inflate(20, 10))
        screen.blit(text, text_rect)
    
    if space_pressed and on_ground:
        text = font.render("↑ PULO ↑", True, YELLOW)
        text_rect = text.get_rect(center=(WIDTH // 2, effect_y - 40))
        # Fundo semi-transparente
        pygame.draw.rect(screen, (0, 0, 0, 128), text_rect.inflate(20, 10))
        screen.blit(text, text_rect)
    elif space_pressed and can_double_jump and not on_ground:
        text = font.render("⭐ PULO DUPLO ⭐", True, (255, 215, 0))  # Dourado
        text_rect = text.get_rect(center=(WIDTH // 2, effect_y - 40))
        # Fundo semi-transparente dourado
        pygame.draw.rect(screen, (50, 50, 0, 128), text_rect.inflate(20, 10))
        screen.blit(text, text_rect)

# Loop principal
# Criar plataformas no início
create_platforms()

while True:
    screen.fill(SKY_BLUE)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movimento do porquinho
    keys = pygame.key.get_pressed()
    left_pressed = keys[pygame.K_LEFT]
    right_pressed = keys[pygame.K_RIGHT]
    space_pressed = keys[pygame.K_SPACE]
    
    # Movimento horizontal
    if left_pressed:
        pig_x -= pig_speed
        pig_facing_right = False  # Virado para esquerda
    if right_pressed:
        pig_x += pig_speed
        pig_facing_right = True   # Virado para direita
    
    # Sistema de pulo e pulo duplo
    if space_pressed and not space_was_pressed:  # Detecta quando a tecla foi pressionada (não mantida)
        if on_ground:
            # Pulo normal do chão
            pig_vel_y = jump_strength
            on_ground = False
            can_double_jump = True  # Ativa a possibilidade de pulo duplo
            has_double_jumped = False
            create_jump_smoke(pig_x, pig_y, False)  # Fumaça normal
        elif can_double_jump and not has_double_jumped:
            # Pulo duplo no ar
            pig_vel_y = double_jump_strength
            can_double_jump = False
            has_double_jumped = True
            create_jump_smoke(pig_x, pig_y, True)  # Fumaça especial do pulo duplo
    
    # Atualizar estado da tecla espaço
    space_was_pressed = space_pressed
    
    # Aplicar gravidade
    pig_vel_y += gravity
    pig_y += pig_vel_y
    
    # A cada quadro, primeiro assumimos que o porco não está no chão
    # A colisão com uma plataforma ou com o solo provará o contrário
    on_ground = False
    
    # Verificar colisão com plataformas
    platform_collision = check_platform_collision()
    
    # Se colidiu com uma plataforma, está no chão
    if platform_collision:
        on_ground = True
    
    # Se não colidiu com uma plataforma, verificar colisão com o chão principal
    elif pig_y >= ground_y:
        pig_y = ground_y
        pig_vel_y = 0
        on_ground = True
        # Reset do sistema de pulo duplo quando toca o chão
        can_double_jump = False
        has_double_jumped = False

    # Atualizar câmera
    update_camera()

    # Limites da tela
    pig_x = max(0, min(WIDTH - pig_width, pig_x))

    # Desenhar nuvens (ajustadas pela câmera)
    draw_cloud(100, 100 + camera_y)
    draw_cloud(300, 80 + camera_y)
    draw_cloud(600, 120 + camera_y)

    # Desenhar plataforma base (ajustada pela câmera)
    base_platform_y = HEIGHT - platform_height + camera_y
    if base_platform_y < HEIGHT:  # Só desenhar se visível
        pygame.draw.rect(screen, DIRT_BROWN, (0, base_platform_y, WIDTH, platform_height))
        pygame.draw.rect(screen, GRASS_GREEN, (0, base_platform_y - 20, WIDTH, 20))

    # Desenhar plataformas suspensas
    draw_platforms()

    # Atualizar e desenhar partículas de fumaça
    update_smoke_particles()

    # Desenhar porquinho (ajustado pela câmera)
    adjusted_pig_y = pig_y + camera_y
    if using_image and pig_image:
        # Escolher a imagem baseada na direção
        current_pig_image = pig_image if pig_facing_right else pig_image_flipped
        screen.blit(current_pig_image, (pig_x, adjusted_pig_y))
    else:
        # Fallback para retângulo rosa se a imagem não carregar (ajustado pela câmera)
        pygame.draw.rect(screen, PINK, (pig_x, adjusted_pig_y, pig_width, pig_height))
    
    # Linha de debug: mostrar área de colisão (ajustada pela câmera)
    if on_ground:
        pygame.draw.line(screen, (0, 255, 0), 
                        (pig_x, adjusted_pig_y + pig_height), 
                        (pig_x + pig_width, adjusted_pig_y + pig_height), 2)

    # Desenhar controles na tela
    draw_instructions()
    
    # Desenhar objetivo e HUD
    draw_objective()
    draw_hud()
    
    # Desenhar botões de controle
    draw_arrow_button(left_button_x, buttons_y, "left", left_pressed)
    draw_arrow_button(right_button_x, buttons_y, "right", right_pressed)
    draw_space_button(space_button_x, buttons_y, space_pressed)
    
    # Desenhar efeito de tecla pressionada
    draw_key_effect()

    # Atualizar tela
    pygame.display.flip()
    clock.tick(FPS)
