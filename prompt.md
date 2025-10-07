# 🐷 PROMPT COMPLETO: Jogo do Porquinho

## 📋 Visão Geral

Este documento contém um prompt completo e detalhado para recriar o "Jogo do Porquinho" do zero usando apenas IA. Copie e cole este prompt em qualquer assistente de IA para gerar o jogo completo.

---

## 🎮 PROMPT PARA COPIAR E COLAR

```
Crie um jogo completo em Python usando Pygame chamado "Jogo do Porquinho" com as seguintes especificações EXATAS:

═══════════════════════════════════════════════════════════════════
📦 REQUISITOS TÉCNICOS
═══════════════════════════════════════════════════════════════════

CONFIGURAÇÕES BÁSICAS:
- Resolução: 800x600 pixels
- FPS: 60
- Física: Gravidade 0.8, Pulo -15, Super pulo -30
- Câmera: Seguimento suave do jogador

ARQUIVOS NECESSÁRIOS:
- game.py (código principal)
- pig.png (sprite 50x50 do porquinho rosa)
- highscore.json (persistência automática)

═══════════════════════════════════════════════════════════════════
🎨 PALETA DE CORES
═══════════════════════════════════════════════════════════════════

SKY_BLUE = (135, 206, 235)      # Fundo do céu
GRASS_GREEN = (34, 139, 34)     # Plataformas normais
DIRT_BROWN = (139, 69, 19)      # Plataformas quebráveis
WHITE = (255, 255, 255)         # Texto e elementos
PINK = (255, 182, 193)          # Porquinho (se sem sprite)
BLACK = (0, 0, 0)               # Contornos
GRAY = (128, 128, 128)          # Partículas de pulo
LIGHT_GRAY = (200, 200, 200)    # UI elements
YELLOW = (255, 255, 0)          # Pulo duplo / novo recorde
DARK_GRAY = (64, 64, 64)        # Plataformas quebráveis escuras
BLUE = (0, 100, 255)            # Molas
ORANGE = (255, 165, 0)          # Partículas de mola
RED = (255, 0, 0)               # Game over / crash

═══════════════════════════════════════════════════════════════════
🐷 SISTEMA DO PERSONAGEM
═══════════════════════════════════════════════════════════════════

PROPRIEDADES:
- Tamanho: 50x50 pixels
- Velocidade horizontal: 5 pixels/frame
- Sprite espelhado automaticamente conforme direção
- Carregamento de pig.png com fallback para retângulo rosa

CONTROLES:
- Seta ESQUERDA/DIREITA: Movimento horizontal
- ESPAÇO: Pulo (força -15) / Pulo duplo (força -12)
- F3: Toggle debug mode
- ESC: Sair do jogo

MECÂNICAS DE PULO:
1. Pulo Normal (-15):
   - Disponível quando on_ground = True
   - Gera 5 partículas cinzas
   - Habilita pulo duplo

2. Pulo Duplo (-12):
   - Disponível após primeiro pulo
   - Só pode ser usado 1 vez por salto
   - Gera 8 partículas amarelas
   - Requer soltar ESPAÇO após primeiro pulo

3. Super Pulo de Mola (-30):
   - Ativado ao tocar plataforma com mola
   - Gera 15 partículas azuis/laranjas
   - Ignora input do jogador
   - Som de "BOING!" no console

DIREÇÃO DO SPRITE:
- Atualizar pig_facing_right baseado em movimento
- Espelhar sprite horizontalmente quando necessário
- Usar pygame.transform.flip(pig_image, True, False)

═══════════════════════════════════════════════════════════════════
🏗️ SISTEMA DE PLATAFORMAS
═══════════════════════════════════════════════════════════════════

TIPOS DE PLATAFORMAS:

1. NORMAL (Verde):
   - Cor: GRASS_GREEN
   - Largura: 100-150 pixels (aleatória)
   - Altura: 20 pixels
   - Sólida permanente
   - 60% de chance de aparecer

2. QUEBRÁVEL (Marrom/Cinza Escuro):
   - Cor: DARK_GRAY
   - Largura: 80-120 pixels
   - Quebra após 1 uso
   - Gera 8 partículas marrons ao quebrar
   - 30% de chance de aparecer
   - Visual diferenciado (mais escura)

3. COM MOLA (Verde + Círculo Azul):
   - Base igual plataforma normal
   - Mola: Círculo azul (raio 15) no centro
   - Super pulo automático (-30)
   - 10% de chance de aparecer
   - Mola especial no chão (25% chance ao regenerar)

GERAÇÃO PROCEDURAL:
- Criar plataformas infinitamente acima do jogador
- Espaçamento vertical: 80-150 pixels (aleatório)
- Espaçamento horizontal: Centralizado com variação ±200 pixels
- Manter buffer de 10 plataformas acima da câmera
- Remover plataformas 200 pixels abaixo da câmera

REGENERAÇÃO COMPLETA:
- Acontece quando jogador toca o chão APÓS ter subido
- Limpar todas as plataformas existentes
- Criar novo layout procedural
- 25% de chance de mola no chão
- Resetar flag reached_platform_this_cycle

ESTRUTURA DE PLATAFORMA:
{
    "rect": pygame.Rect(x, y, width, height),
    "type": "normal" | "breakable" | "spring",
    "spring_rect": pygame.Rect ou None,
    "broken": False | True
}

═══════════════════════════════════════════════════════════════════
📷 SISTEMA DE CÂMERA
═══════════════════════════════════════════════════════════════════

COMPORTAMENTO:
- Seguir jogador suavemente (lerp com fator 0.1)
- Só seguir quando jogador está acima do centro da tela
- Não seguir quando jogador está caindo
- Usar camera_y para offset global de desenho

CÁLCULO:
```python
if pig_y < HEIGHT // 2 and pig_vel_y < 0:
    camera_target_y = pig_y - HEIGHT // 2
    camera_y += (camera_target_y - camera_y) * 0.1
```

APLICAÇÃO:
- Subtrair camera_y de todas as posições Y ao desenhar
- Aplicar a: jogador, plataformas, partículas, nuvens

═══════════════════════════════════════════════════════════════════
✨ SISTEMA DE PARTÍCULAS
═══════════════════════════════════════════════════════════════════

ESTRUTURA:
{
    "x": float,
    "y": float,
    "vel_x": float,
    "vel_y": float,
    "life": int (0-30),
    "color": tuple,
    "size": int
}

TIPOS:

1. PULO NORMAL (Cinza):
   - 5 partículas
   - Cor: GRAY
   - Velocidade: vel_x aleatório ±3, vel_y -4 a -2
   - Vida: 30 frames
   - Tamanho: 4 pixels

2. PULO DUPLO (Amarelo):
   - 8 partículas
   - Cor: YELLOW
   - Velocidade: vel_x aleatório ±4, vel_y -5 a -3
   - Vida: 30 frames
   - Tamanho: 5 pixels

3. SUPER PULO/MOLA (Azul/Laranja):
   - 15 partículas
   - Cores: BLUE e ORANGE alternadas
   - Velocidade: vel_x aleatório ±5, vel_y -8 a -4
   - Vida: 40 frames
   - Tamanho: 6 pixels

4. PLATAFORMA QUEBRADA (Marrom):
   - 8 partículas
   - Cor: DIRT_BROWN
   - Velocidade: vel_x aleatório ±4, vel_y -6 a -2
   - Vida: 30 frames
   - Tamanho: 4 pixels

5. CRASH (Vermelho):
   - 20 partículas
   - Cor: RED
   - Velocidade: vel_x aleatório ±6, vel_y -8 a -4
   - Vida: 50 frames
   - Tamanho: 8-12 pixels (aleatório)

FÍSICA:
- Aplicar gravidade 0.3 a vel_y
- Atualizar posição: x += vel_x, y += vel_y
- Reduzir vida em 1 por frame
- Remover quando life <= 0
- Limitar array a 200 partículas máximo

═══════════════════════════════════════════════════════════════════
💯 SISTEMA DE PONTUAÇÃO E ALTURA
═══════════════════════════════════════════════════════════════════

CÁLCULO DA ALTURA:
```python
current_height = max(0, int((ground_y - pig_y) / 10))  # 1m = 10px
```

RECORDE:
- Carregar de highscore.json ao iniciar
- Atualizar max_height_reached continuamente
- Salvar automaticamente a cada 10m de progresso
- Salvar no game over
- Salvar ao fechar o jogo
- Salvar ao resetar (ESPAÇO)

FORMATO JSON:
```json
{
    "highscore": 209,
    "last_updated": "2025-10-07 15:30:45"
}
```

FUNÇÕES NECESSÁRIAS:
```python
def load_high_score():
    # Carregar de highscore.json
    # Retornar 0 se arquivo não existir

def save_high_score(score):
    # Salvar score e timestamp em highscore.json
    # Criar arquivo se não existir

def check_and_save_high_score(current, previous):
    # Salvar se current > previous
    # Retornar True se salvou
```

═══════════════════════════════════════════════════════════════════
💀 SISTEMA DE GAME OVER
═══════════════════════════════════════════════════════════════════

CONDIÇÕES DE MORTE:
1. Queda maior que 60m (600px):
   - Medir desde último pouso seguro (last_safe_y)
   - Não contar quedas pequenas
   - Só ativar se já pisou em plataforma

2. Cálculo:
```python
if not on_ground and pig_vel_y > 0:
    fall_distance = abs(pig_y - last_safe_y)
    if fall_distance > max_safe_fall and reached_platform_this_cycle:
        game_over = True
```

TELA DE GAME OVER:
- Retângulo semi-transparente BLACK (alpha 200)
- Texto "GAME OVER" branco, tamanho 72, centralizado
- "Altura Final: Xm" branco, tamanho 36
- "Recorde: Xm" amarelo/branco, tamanho 36
- "NOVO RECORDE SALVO!" em amarelo se bateu recorde
- "Pressione ESPAÇO para Reiniciar" branco, tamanho 24
- Timer de 60 frames antes de permitir reiniciar
- 20 partículas vermelhas de crash

RESET:
- Chamar reset_game()
- Limpar todas as plataformas
- Resetar posição do jogador
- Limpar partículas
- Gerar novo layout
- Salvar recorde

═══════════════════════════════════════════════════════════════════
🎨 HUD (Interface)
═══════════════════════════════════════════════════════════════════

ELEMENTOS:

1. ALTURA ATUAL (Topo Esquerdo):
   - "Altura: XXm"
   - Cor: WHITE
   - Tamanho: 32
   - Posição: (10, 10)

2. RECORDE (Topo Direito):
   - "Recorde: XXm"
   - Cor: WHITE ou YELLOW (se batendo recorde)
   - Tamanho: 32
   - Posição: (WIDTH - 200, 10)

3. NOVO RECORDE (Centro Superior):
   - "🔥 NOVO RECORDE! 🔥"
   - Cor: YELLOW
   - Tamanho: 48
   - Mostrar quando current_height > max_height_reached
   - Piscar a cada 20 frames

4. BARRA DE PROGRESSO:
   - Altura: 20 pixels
   - Largura: 400 pixels
   - Posição: Centro superior (Y=50)
   - Preenchimento proporcional ao progresso
   - Cor: YELLOW quando subindo, GRAY quando descendo

5. INDICADOR DE PULO DUPLO:
   - Círculo amarelo no canto inferior esquerdo
   - Tamanho: 20 pixels
   - Mostrar quando can_double_jump = True
   - Texto: "DUPLO OK"

6. BOTÕES VIRTUAIS (Inferior):
   - Esquerda: (10, HEIGHT-60), 50x50
   - Direita: (70, HEIGHT-60), 50x50
   - Espaço: (WIDTH-60, HEIGHT-60), 50x50
   - Cor: LIGHT_GRAY com alpha 128
   - Desenhar setas e "SP"

═══════════════════════════════════════════════════════════════════
🐛 DEBUG MODE (F3)
═══════════════════════════════════════════════════════════════════

INFORMAÇÕES A MOSTRAR:
- Altura atual em metros
- Velocidade Y atual
- Queda desde último pouso (em metros)
- Status: on_ground, can_double_jump, has_double_jumped
- Câmera Y
- Número de plataformas ativas
- Número de partículas ativas
- FPS atual

FORMATO:
```
DEBUG INFO:
Altura: XXm | Vel Y: X.X | Queda: XXm
Ground: True/False | Duplo: True/False
Câmera: XXXX | Plataformas: XX | Partículas: XXX
FPS: XX
```

POSIÇÃO: Canto superior esquerdo, abaixo da altura
COR: WHITE com fundo BLACK semi-transparente

═══════════════════════════════════════════════════════════════════
🌥️ ELEMENTOS DECORATIVOS
═══════════════════════════════════════════════════════════════════

NUVENS:
- 5 nuvens estáticas em posições fixas
- Formato: 3 círculos brancos sobrepostos
- Círculo central: raio 30
- Círculos laterais: raio 20
- Posições Y fixas: [100, 200, 150, 250, 180]
- Posições X: Distribuídas pela tela
- Seguem câmera (subtraem camera_y ao desenhar)

CHÃO:
- Retângulo marrom de 100 pixels de altura
- Sempre na parte inferior da tela
- Não move com câmera
- Base da física do jogo

═══════════════════════════════════════════════════════════════════
🔄 LOOP PRINCIPAL
═══════════════════════════════════════════════════════════════════

ESTRUTURA:

```python
running = True
while running:
    clock.tick(FPS)
    
    # 1. EVENTOS
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
                elif not game_over:
                    # Lógica de pulo
    
    if not game_over:
        # 2. INPUT
        keys = pygame.key.get_pressed()
        # Movimento horizontal
        # Pulo (com detecção de soltar tecla)
        
        # 3. FÍSICA
        pig_vel_y += gravity
        pig_y += pig_vel_y
        
        # 4. COLISÕES
        check_platform_collision()
        
        # 5. LIMITES
        # Lateral: wrap around
        # Inferior: regenerar se voltou ao chão
        
        # 6. ALTURA E RECORDE
        current_height = max(0, int((ground_y - pig_y) / 10))
        if current_height > max_height_reached:
            if current_height % 10 == 0:  # Salvar a cada 10m
                save_high_score(current_height)
            max_height_reached = current_height
        
        # 7. GAME OVER
        # Verificar queda fatal
        
        # 8. PLATAFORMAS
        manage_platforms()
        
        # 9. CÂMERA
        update_camera()
        
        # 10. PARTÍCULAS
        update_particles()
    
    else:
        game_over_timer += 1
    
    # 11. DESENHO
    draw_everything()
    
    pygame.display.flip()

pygame.quit()
```

═══════════════════════════════════════════════════════════════════
📦 ESTRUTURA DE CÓDIGO COMPLETA
═══════════════════════════════════════════════════════════════════

IMPORTS:
```python
import pygame
import random
import sys
import json
from datetime import datetime
```

ORDEM DAS SEÇÕES:
1. Inicialização Pygame
2. Configurações da tela
3. Carregamento de imagens (com try/except)
4. Definição de cores
5. Variáveis globais (jogador, física, plataformas, câmera, etc)
6. Funções de persistência (load/save highscore)
7. Funções de plataformas (create, generate, manage)
8. Funções de colisão
9. Funções de desenho
10. Função de reset
11. Função de câmera
12. Loop principal

BOAS PRÁTICAS:
- Comentários em português
- Nomes de variáveis descritivos
- Separar lógica em funções
- Try/except para carregamento de arquivos
- Feedback no console (prints informativos)

═══════════════════════════════════════════════════════════════════
🎯 REQUISITOS FINAIS
═══════════════════════════════════════════════════════════════════

FUNCIONALIDADES OBRIGATÓRIAS:
✅ Movimento fluido com setas
✅ Pulo simples e duplo
✅ 3 tipos de plataformas (normal, quebrável, mola)
✅ Geração procedural infinita
✅ Câmera que segue o jogador
✅ Sistema de partículas completo
✅ HUD com altura e recorde
✅ Persistência de recorde em JSON
✅ Game over por queda > 60m
✅ Regeneração de mapa ao voltar ao chão
✅ Debug mode (F3)
✅ Sprite espelhado
✅ Mola aleatória no chão
✅ Feedback visual e no console

QUALIDADE:
- Código limpo e organizado
- Sem erros ou warnings
- Performance estável (60 FPS)
- Jogabilidade suave
- Controles responsivos

ARQUIVO FINAL:
- Nome: game.py
- Linhas: ~1000-1200
- Pronto para executar com: python game.py
- Funcional em Windows, Mac e Linux

═══════════════════════════════════════════════════════════════════

IMPORTANTE: 
- Gerar código COMPLETO e FUNCIONAL
- Incluir TODOS os sistemas descritos
- Testar mentalmente cada funcionalidade
- Garantir que não há erros de sintaxe
- Comentar seções importantes
- Seguir EXATAMENTE as especificações acima
```

---

## 📝 Como Usar Este Prompt

### Opção 1: GitHub Copilot / ChatGPT / Claude
1. Copie todo o conteúdo entre as aspas acima
2. Cole no chat da IA
3. Aguarde a geração do código completo
4. Salve como `game.py`
5. Execute com `python game.py`

### Opção 2: Geração Incremental
Se a IA tiver limite de tokens, divida em partes:
1. "Crie a estrutura básica e sistema do personagem"
2. "Adicione o sistema de plataformas"
3. "Implemente câmera e partículas"
4. "Adicione HUD e persistência"
5. "Finalize com game over e debug"

### Opção 3: Refinamento
Após gerar o código inicial:
- "Adicione mais comentários"
- "Otimize a performance"
- "Melhore o feedback visual"
- "Adicione mais tipos de plataformas"

---

## ✅ Checklist de Validação

Após gerar o código, verifique:

- [ ] Jogo inicia sem erros
- [ ] Movimento funciona (← →)
- [ ] Pulo simples funciona (ESPAÇO)
- [ ] Pulo duplo funciona (ESPAÇO no ar)
- [ ] Plataformas geram infinitamente
- [ ] Plataformas quebráveis quebram
- [ ] Molas dão super pulo
- [ ] Câmera segue o jogador
- [ ] HUD mostra altura e recorde
- [ ] Recorde salva em highscore.json
- [ ] Game over funciona (queda > 60m)
- [ ] Reiniciar funciona (ESPAÇO após game over)
- [ ] Debug mode funciona (F3)
- [ ] FPS estável em 60
- [ ] Sem warnings no console

---

## 🎮 Resultado Esperado

Após usar este prompt, você deve ter:

✅ **Arquivo:** `game.py` (~1000-1200 linhas)  
✅ **Funcionalidade:** 100% operacional  
✅ **Performance:** 60 FPS estável  
✅ **Jogabilidade:** Suave e divertida  
✅ **Persistência:** Recorde salvo automaticamente  

---

## 📚 Documentação Adicional

Para mais informações sobre o jogo:
- `README.md` - Visão geral e controles
- `ANALISE_E_MELHORIAS.md` - Análise técnica
- `SISTEMA_PERSISTENCIA.md` - Detalhes do save system

---

## 🤝 Créditos

**Jogo Original:** Fabricio (Pig Game VibeCode)  
**Prompt Engineering:** GitHub Copilot  
**Data:** Outubro 2025  

---

## 📄 Licença

Este prompt é de uso livre para fins educacionais e criativos.

---

**🎯 Use este prompt para criar seu próprio "Jogo do Porquinho" do zero! 🐷🚀**