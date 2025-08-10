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
super_jump_strength = -30  # Pulo super forte das molas!
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

# Sistema de Game Over
game_over = False
game_over_timer = 0
fall_start_height = 0
SAFE_FALL_METERS = 60  # Queda segura máxima antes de Game Over em metros
max_safe_fall = SAFE_FALL_METERS * 10  # Conversão: 1m = 10px na nossa escala de HUD
last_safe_y = 0  # Última posição segura (aterrissagem) para comparar quedas
debug_mode = True  # Mostrar informações de debug (F3 para alternar)
ground_spring_active = False  # Se há mola no chão
ground_spring_rect = None     # Retângulo da mola no chão

GROUND_SPRING_CHANCE = 0.25   # 25% de chance de aparecer mola ao regenerar
reached_platform_this_cycle = False  # Indicador se já pisou em alguma plataforma desde o último reset de layout
was_on_ground_last_frame = True      # Estado de "no chão" do frame anterior

# Sistema de câmera
camera_y = 0
camera_target_y = 0

# Sistema de partículas de fumaça para o pulo
smoke_particles = []

# Sistema de plataformas suspensas
platforms = []
last_platform_y = 0  # Controla a altura da plataforma mais alta criada

import random

# Função para criar plataformas
def create_platforms():
    """Cria as plataformas INICIAIS e define a altura máxima inicial."""
    global platforms, last_platform_y
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
        [300, HEIGHT - 720, 150, 20, (139, 100, 19)], # Plataforma mais alta
    ]
    
    min_y = HEIGHT  # Começamos com um valor 'y' alto
    
    for config in platform_configs:
        platform = {
            'x': config[0],
            'y': config[1],
            'width': config[2],
            'height': config[3],
            'color': config[4],
            'type': 'normal',  # Plataformas iniciais são sempre normais
            'special_item': None,  # Plataformas iniciais não têm itens especiais
            'rect': pygame.Rect(config[0], config[1], config[2], config[3])
        }
        platforms.append(platform)
        # Guarda a coordenada Y da plataforma mais alta (menor valor de Y)
        if platform['y'] < min_y:
            min_y = platform['y']
    
    # Define a variável global com a altura da plataforma mais alta
    last_platform_y = min_y

def generate_random_platforms():
    """Gera um conjunto totalmente novo de plataformas aleatórias acima do chão."""
    global platforms, last_platform_y
    platforms = []
    current_y = ground_y - 200  # Primeiras plataformas acima do chão
    min_y = current_y
    for i in range(10):
        width_rand = random.randint(80, 140)
        x_rand = random.randint(0, WIDTH - width_rand)
        is_breakable = random.random() < 0.2
        has_spring = (not is_breakable) and (random.random() < 0.1)
        if is_breakable:
            color = (139, 92, 56)
        elif random.random() < 0.1:
            color = (139, 100, 19)
        else:
            color = DIRT_BROWN
        platform = {
            'x': x_rand,
            'y': current_y,
            'width': width_rand,
            'height': 20,
            'color': color,
            'type': 'breakable' if is_breakable else 'normal',
            'special_item': 'spring' if has_spring else None,
            'rect': pygame.Rect(x_rand, current_y, width_rand, 20)
        }
        platforms.append(platform)
        if current_y < min_y:
            min_y = current_y
        current_y -= random.randint(60, 110)
    last_platform_y = min_y

# Função para resetar o jogo
def reset_game():
    """Reseta todas as variáveis do jogo para o estado inicial"""
    global pig_x, pig_y, pig_vel_y, on_ground, can_double_jump, has_double_jumped
    global camera_y, camera_target_y, smoke_particles, game_over, game_over_timer
    global fall_start_height, current_height, last_safe_y, reached_platform_this_cycle, was_on_ground_last_frame
    
    # Reset da posição do porco
    pig_x, pig_y = WIDTH // 2, HEIGHT - 150
    pig_vel_y = 0
    on_ground = True
    
    # Reset do sistema de pulo
    can_double_jump = False
    has_double_jumped = False
    
    # Reset da câmera
    camera_y = 0
    camera_target_y = 0
    
    # Limpar partículas
    smoke_particles.clear()
    
    # Reset do game over
    game_over = False
    game_over_timer = 0
    fall_start_height = pig_y  # Altura inicial de referência
    last_safe_y = pig_y        # Posição segura inicial
    current_height = 0
    
    # Recriar plataformas
    create_platforms()
    # Decidir mola no chão inicial
    spawn_ground_spring()
    reached_platform_this_cycle = False
    was_on_ground_last_frame = True

def spawn_ground_spring():
    """Decide se haverá mola no chão e posiciona."""
    global ground_spring_active, ground_spring_rect
    if random.random() < GROUND_SPRING_CHANCE:
        spring_x = random.randint(40, WIDTH - 40 - 30)  # 30 largura da mola
        # A parte superior do chão é HEIGHT - platform_height
        spring_top_y = HEIGHT - platform_height - 20  # elevar um pouco
        ground_spring_rect = pygame.Rect(spring_x, spring_top_y, 30, 20)
        ground_spring_active = True
    else:
        ground_spring_active = False
        ground_spring_rect = None

def manage_platforms():
    """Gera novas plataformas no topo e remove as antigas na base."""
    global platforms, last_platform_y

    # --- 1. GERAÇÃO DE NOVAS PLATAFORMAS ---
    # Gera múltiplas plataformas quando necessário para garantir subida infinita
    # Condição: se não há plataformas suficientes acima do porco
    
    # Contar quantas plataformas existem acima da posição atual do porco
    platforms_above = [p for p in platforms if p['y'] < pig_y - 200]
    
    # Se há menos de 5 plataformas acima do porco, gerar mais
    while len(platforms_above) < 5:
        # Gera uma nova plataforma acima da última
        new_y = last_platform_y - random.randint(60, 110)  # Distância vertical aleatória
        new_x = random.randint(0, WIDTH - 130)             # Posição X aleatória (com margem)
        new_width = random.randint(80, 130)                # Largura aleatória
        
        # Determinar tipo da plataforma e itens especiais
        is_breakable = random.random() < 0.2  # 20% de chance de ser quebrável
        has_spring = not is_breakable and random.random() < 0.1  # 10% de chance de ter mola (só em normais)
        
        # Escolher cor baseada no tipo e ocasionalmente especial
        if is_breakable:
            new_color = (139, 92, 56)  # Cor marrom mais escura para plataformas quebráveis
        elif random.random() < 0.1:
            new_color = (139, 100, 19)  # Cor especial dourada (apenas para normais)
        else:
            new_color = DIRT_BROWN      # Cor normal

        new_platform = {
            'x': new_x,
            'y': new_y,
            'width': new_width,
            'height': 20,
            'color': new_color,
            'type': 'breakable' if is_breakable else 'normal',
            'special_item': 'spring' if has_spring else None,  # Item especial na plataforma
            'rect': pygame.Rect(new_x, new_y, new_width, 20)
        }
        platforms.append(new_platform)
        
        # Atualiza a referência da plataforma mais alta
        last_platform_y = new_y
        
        # Atualizar lista de plataformas acima para o próximo loop
        platforms_above = [p for p in platforms if p['y'] < pig_y - 200]

    # --- 2. REMOÇÃO DE PLATAFORMAS ANTIGAS ---
    # Remove plataformas que estão muito abaixo da tela (otimização de performance)
    # Uma plataforma deve ser removida quando seu topo passou 100 pixels abaixo da base da tela
    # Usamos camera_target_y para ter a posição instantânea e precisa
    platforms[:] = [p for p in platforms if p['y'] + camera_target_y < HEIGHT + 100]

    # --- 3. REMOÇÃO DE PLATAFORMAS QUEBRADAS ---
    platforms[:] = [p for p in platforms if not p.get('to_be_removed')]

# Função para verificar colisão com plataformas
def check_platform_collision():
    """Verifica se o porquinho está colidindo com alguma plataforma"""
    global pig_y, pig_vel_y, on_ground, can_double_jump, has_double_jumped, last_safe_y, fall_start_height, reached_platform_this_cycle
    
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
                    # --- LÓGICA DO SUPER PULO COM MOLA ---
                    if platform.get('special_item') == 'spring':
                        pig_y = platform_top - pig_height
                        pig_vel_y = super_jump_strength  # PULO ESPECIAL!
                        on_ground = False  # Já sai pulando de novo
                        # Atualiza bases de queda após usar mola (novo ciclo de subida)
                        last_safe_y = pig_y
                        fall_start_height = pig_y
                        # Já tocou uma plataforma neste ciclo
                        reached_platform_this_cycle = True
                        # Remover a mola após o uso
                        platform['special_item'] = None
                        # Efeito especial para o super pulo
                        create_spring_effect(platform['x'] + platform['width']//2, platform['y'])
                        # Reset do sistema de pulo duplo
                        can_double_jump = True  # Ganha pulo duplo com a mola!
                        has_double_jumped = False
                    
                    # --- LÓGICA NORMAL DE POUSO ---
                    else:
                        pig_y = platform_top - pig_height
                        pig_vel_y = 0
                        on_ground = True
                        # Reset do sistema de pulo duplo quando pousa em plataforma
                        can_double_jump = False
                        has_double_jumped = False
                        # Atualiza posições seguras para cálculo de queda futura
                        last_safe_y = pig_y
                        fall_start_height = pig_y
                        reached_platform_this_cycle = True
                    
                    # ---- LÓGICA DA PLATAFORMA QUEBRÁVEL ----
                    # Só quebra se NÃO teve mola (molas são só em plataformas normais)
                    if platform.get('type') == 'breakable':
                        # Marcar a plataforma para ser removida
                        platform['to_be_removed'] = True
                        # Criar efeito visual especial para quebra
                        create_break_effect(platform['x'] + platform['width']//2, platform['y'])
                    # ----------------------------------------
                    
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
            if pig_on_platform:
                platform_color = (200, 150, 50)
            elif platform.get('type') == 'breakable':
                platform_color = platform['color']  # Manter cor original das quebráveis
            else:
                platform_color = platform['color']
            
            # Desenhar plataforma principal
            pygame.draw.rect(screen, platform_color, adjusted_rect)
            
            # Desenhar grama em cima (diferentes para quebráveis)
            grass_rect = pygame.Rect(platform['x'], adjusted_y - 5, platform['width'], 5)
            if pig_on_platform:
                grass_color = (50, 200, 50)
            elif platform.get('type') == 'breakable':
                grass_color = (100, 69, 19)  # Grama seca para plataformas quebráveis
            else:
                grass_color = GRASS_GREEN
            pygame.draw.rect(screen, grass_color, grass_rect)
            
            # Adicionar bordas para melhor visual
            if platform.get('type') == 'breakable':
                # Bordas pontilhadas para plataformas quebráveis
                border_color = (200, 100, 50) if pig_on_platform else (100, 50, 25)
                pygame.draw.rect(screen, border_color, adjusted_rect, 3)
                # Adicionar marcas de rachadura
                mid_x = platform['x'] + platform['width'] // 2
                pygame.draw.line(screen, (80, 40, 20), 
                               (mid_x - 10, adjusted_y), (mid_x + 10, adjusted_y + 20), 2)
                pygame.draw.line(screen, (80, 40, 20), 
                               (mid_x + 5, adjusted_y), (mid_x - 5, adjusted_y + 20), 1)
            else:
                border_color = YELLOW if pig_on_platform else BLACK
                pygame.draw.rect(screen, border_color, adjusted_rect, 2)
            
            # --- DESENHAR ITENS ESPECIAIS ---
            if platform.get('special_item') == 'spring':
                # Desenhar mola em azul vibrante
                spring_color = (0, 150, 255)  # Azul vibrante
                spring_x = platform['x'] + platform['width']//2 - 10
                spring_y = adjusted_y - 15
                spring_rect = pygame.Rect(spring_x, spring_y, 20, 15)
                
                # Mola principal
                pygame.draw.rect(screen, spring_color, spring_rect)
                pygame.draw.rect(screen, (200, 255, 255), spring_rect, 2)  # Borda clara
                
                # Efeito de "espirais" na mola
                for i in range(3):
                    spiral_y = spring_y + 3 + i * 3
                    pygame.draw.line(screen, (255, 255, 255), 
                                   (spring_x + 2, spiral_y), (spring_x + 18, spiral_y), 1)

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

# Função para criar efeito de quebra de plataforma
def create_break_effect(x, y):
    """Cria partículas de quebra quando uma plataforma se desfaz"""
    particle_count = 15  # Mais partículas para um efeito dramático
    
    for i in range(particle_count):
        particle = {
            'x': x + random.randint(-40, 40),
            'y': y + random.randint(-10, 20),
            'vel_x': random.uniform(-4, 4),
            'vel_y': random.uniform(-3, 1),
            'size': random.randint(3, 8),
            'life': random.randint(25, 40),
            'max_life': random.randint(25, 40),
            'color_type': 'break'
        }
        particle['max_life'] = particle['life']
        smoke_particles.append(particle)

# Função para criar efeito de crash (game over)
def create_crash_effect(x, y):
    """Cria um efeito dramático de crash para o game over"""
    particle_count = 25  # Muitas partículas para efeito dramático
    
    for i in range(particle_count):
        particle = {
            'x': x + random.randint(-30, 30),
            'y': y + random.randint(-20, 10),
            'vel_x': random.uniform(-6, 6),
            'vel_y': random.uniform(-8, -2),
            'size': random.randint(4, 12),
            'life': random.randint(40, 60),
            'max_life': random.randint(40, 60),
            'color_type': 'crash'
        }
        particle['max_life'] = particle['life']
        smoke_particles.append(particle)

# Função para criar efeito da mola (super pulo)
def create_spring_effect(x, y):
    """Cria um efeito especial quando a mola é ativada"""
    particle_count = 20  # Bastante partículas para um efeito espetacular
    
    for i in range(particle_count):
        particle = {
            'x': x + random.randint(-25, 25),
            'y': y + random.randint(-5, 15),
            'vel_x': random.uniform(-3, 3),
            'vel_y': random.uniform(-8, -4),  # Partículas que voam para cima
            'size': random.randint(3, 8),
            'life': random.randint(30, 45),
            'max_life': random.randint(30, 45),
            'color_type': 'spring'
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
            # Usar círculo se não tiver imagem - cores diferentes para cada tipo
            if particle.get('color_type') == 'double':
                color = (255, 255, 150) if alpha > 128 else (200, 200, 100)  # Amarelado para pulo duplo
            elif particle.get('color_type') == 'break':
                color = (139, 92, 56) if alpha > 128 else (101, 67, 33)  # Marrom para quebra
            elif particle.get('color_type') == 'crash':
                color = (255, 50, 50) if alpha > 128 else (200, 0, 0)  # Vermelho para crash
            elif particle.get('color_type') == 'spring':
                color = (0, 150, 255) if alpha > 128 else (0, 100, 200)  # Azul para mola
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
# Inicializar o jogo em estado limpo
reset_game()

while True:
    # Verificar se não está em game over
    if not game_over:
        screen.fill(SKY_BLUE)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    debug_mode = not debug_mode

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
                # Verificar se está sobre mola do chão
                used_ground_spring = False
                if ground_spring_active and ground_spring_rect:
                    if pig_x + pig_width > ground_spring_rect.x and pig_x < ground_spring_rect.x + ground_spring_rect.width:
                        pig_vel_y = super_jump_strength
                        on_ground = False
                        can_double_jump = True
                        has_double_jumped = False
                        create_spring_effect(ground_spring_rect.x + ground_spring_rect.width//2, ground_spring_rect.y)
                        ground_spring_active = False
                        used_ground_spring = True
                if not used_ground_spring:
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
        
        # Registrar pico de subida: quando a velocidade muda de negativa (subindo) para positiva (começa a cair)
        # Precisamos de uma flag derivada do frame anterior. Simplificação: se velocidade agora > 0 e antes era <=0
        # Armazenamos a velocidade anterior em uma variável local estática usando atributo da função (hack simples)
        if not hasattr(pygame, '_prev_vel_y'):
            pygame._prev_vel_y = pig_vel_y
        if pig_vel_y > 0 and pygame._prev_vel_y <= 0:
            # Começou a cair: registrar altura máxima atingida
            fall_start_height = pig_y
        pygame._prev_vel_y = pig_vel_y
    
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
            falling = pig_vel_y > 0
            if falling:
                fall_distance = pig_y - fall_start_height
                real_drop = pig_y - last_safe_y
                if fall_distance > max_safe_fall and real_drop > max_safe_fall:
                    game_over = True
                    game_over_timer = 180
                    create_crash_effect(pig_x + pig_width//2, pig_y + pig_height//2)
                else:
                    pig_y = ground_y
                    pig_vel_y = 0
                    on_ground = True
                    can_double_jump = False
                    has_double_jumped = False
                    last_safe_y = pig_y
                    fall_start_height = pig_y
                    if not was_on_ground_last_frame and reached_platform_this_cycle:
                        generate_random_platforms()
                        spawn_ground_spring()
                        reached_platform_this_cycle = False
            else:
                pig_y = ground_y
                pig_vel_y = 0
                on_ground = True
                can_double_jump = False
                has_double_jumped = False
                last_safe_y = pig_y
                fall_start_height = pig_y
                if not was_on_ground_last_frame and reached_platform_this_cycle:
                    generate_random_platforms()
                    spawn_ground_spring()
                    reached_platform_this_cycle = False

        # Atualizar câmera
        update_camera()
        
        # Sistema de plataformas infinitas
        manage_platforms()

        # Calcular métricas de debug de queda
        current_fall_distance = pig_y - fall_start_height if pig_vel_y > 0 else 0
        real_drop = pig_y - last_safe_y
    else:
        # Mesmo em game over queremos valores para exibir
        current_fall_distance = pig_y - fall_start_height
        real_drop = pig_y - last_safe_y

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
        # Desenhar mola no chão se ativa
        if ground_spring_active and ground_spring_rect:
            spring_draw_y = ground_spring_rect.y + camera_y
            spring_rect_draw = pygame.Rect(ground_spring_rect.x, spring_draw_y, ground_spring_rect.width, ground_spring_rect.height)
            pygame.draw.rect(screen, (0,150,255), spring_rect_draw)
            pygame.draw.rect(screen, (200,255,255), spring_rect_draw, 2)
            # Espirais
            for i in range(3):
                y_line = spring_draw_y + 4 + i*4
                pygame.draw.line(screen, WHITE, (ground_spring_rect.x + 3, y_line), (ground_spring_rect.x + ground_spring_rect.width - 3, y_line), 2)

    # Desenhar plataformas suspensas
    draw_platforms()

    # Atualizar e desenhar partículas de fumaça
    update_smoke_particles()

    # Desenhar porquinho e interfaces dependendo do estado de game_over
    if not game_over:
        adjusted_pig_y = pig_y + camera_y
        if using_image and pig_image:
            current_pig_image = pig_image if pig_facing_right else pig_image_flipped
            screen.blit(current_pig_image, (pig_x, adjusted_pig_y))
        else:
            pygame.draw.rect(screen, PINK, (pig_x, adjusted_pig_y, pig_width, pig_height))

        # Linha de debug no pé quando está tocando alguma superfície
        if on_ground:
            pygame.draw.line(screen, (0, 255, 0),
                              (pig_x, adjusted_pig_y + pig_height),
                              (pig_x + pig_width, adjusted_pig_y + pig_height), 2)

        # HUD e UI (sempre que não estiver em game over)
        draw_instructions()
        draw_objective()
        draw_hud()
        draw_arrow_button(left_button_x, buttons_y, "left", left_pressed)
        draw_arrow_button(right_button_x, buttons_y, "right", right_pressed)
        draw_space_button(space_button_x, buttons_y, space_pressed)
        draw_key_effect()

        # Overlay de debug
        if debug_mode:
            font_dbg = pygame.font.Font(None, 22)
            dbg_lines = [
                f"DEBUG (F3): pig_y={pig_y:.1f}",
                f"vel_y={pig_vel_y:.2f} on_ground={on_ground}",
                f"fall_start={fall_start_height:.1f} last_safe={last_safe_y:.1f}",
                f"fall_dist={current_fall_distance:.1f} real_drop={real_drop:.1f}",
                f"threshold={max_safe_fall} game_over={game_over}"
            ]
            for i, line in enumerate(dbg_lines):
                txt = font_dbg.render(line, True, (20,20,20))
                screen.blit(txt, (WIDTH-290, HEIGHT-150 + i*18))
    else:
        # TELA DE GAME OVER verdadeira
        screen.fill((50, 0, 0))
        update_smoke_particles()
        adjusted_pig_y = pig_y + camera_y
        if using_image and pig_image:
            rotated_pig = pygame.transform.rotate(pig_image, 90)
            screen.blit(rotated_pig, (pig_x, adjusted_pig_y))
        else:
            pygame.draw.rect(screen, (255, 100, 100), (pig_x, adjusted_pig_y, pig_width, pig_height))

        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        game_over_text = font_large.render("GAME OVER", True, (255, 50, 50))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(game_over_text, game_over_rect)
        reason_text = font_medium.render(f"Queda de {int((pig_y - fall_start_height)/10)}m foi fatal!", True, WHITE)
        reason_rect = reason_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(reason_text, reason_rect)
        if game_over_timer > 60:  # (Comentário estava invertido antes, mantendo lógica existente)
            restart_text = font_small.render("Pressione ESPAÇO para recomeçar", True, YELLOW)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)
        stats_text = font_small.render(f"Altura máxima alcançada: {max_height_reached}m", True, LIGHT_GRAY)
        stats_rect = stats_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(stats_text, stats_rect)
        game_over_timer -= 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and game_over_timer <= 60:
            reset_game()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                debug_mode = not debug_mode

        # Overlay debug também na tela de game over
        if debug_mode:
            font_dbg = pygame.font.Font(None, 24)
            dbg_text = [
                f"fall_start={fall_start_height:.1f}",
                f"last_safe={last_safe_y:.1f}",
                f"queda_total={current_fall_distance:.1f}",
                f"queda_real={real_drop:.1f}",
                f"limite={max_safe_fall}"
            ]
            for i, line in enumerate(dbg_text):
                txt = font_dbg.render(line, True, WHITE)
                screen.blit(txt, (10, HEIGHT - 140 + i*22))
    pygame.display.flip()
    clock.tick(FPS)
    # Atualizar flag de estado de chão para o próximo loop
    was_on_ground_last_frame = on_ground
