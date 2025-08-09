# 🐷 Jogo do Porquinho

Um jogo 2D simples e divertido desenvolvido em Python usando a biblioteca Pygame.

## 📝 Descrição

O Jogo do Porquinho é um jogo de plataforma básico onde você controla um adorável porquinho rosa que pode se mover horizontalmente em uma plataforma de terra com grama. O jogo apresenta um cenário colorido com céu azul, nuvens brancas flutuantes e uma base sólida para o porquinho explorar.

## 🎮 Como Jogar

### Controles
- **Seta Esquerda (←)**: Move o porquinho para a esquerda
- **Seta Direita (→)**: Move o porquinho para a direita
- **Espaço**: Pular (primeiro pulo)
- **Espaço (no ar)**: Pulo duplo (disponível após o primeiro pulo)
- **Fechar janela (X)**: Sair do jogo

### Objetivo
**ESCALE O MAIS ALTO POSSÍVEL!** Use o sistema de movimento horizontal e pulo duplo para subir pelas plataformas suspensas. Cada plataforma alcançada aumenta sua pontuação de altura. O desafio é não cair enquanto tenta alcançar plataformas cada vez mais altas e distantes!

## 🛠️ Especificações Técnicas

### Requisitos do Sistema
- **Python**: 3.6 ou superior
- **Pygame**: 2.0 ou superior
- **Sistema Operacional**: Windows, macOS, ou Linux

### Configurações do Jogo
- **Resolução**: 800x600 pixels
- **Taxa de Quadros**: 60 FPS
- **Estilo Gráfico**: 2D com formas geométricas simples

### Elementos do Jogo

#### Personagem Principal
- **Porquinho**: Sprite PNG personalizado (50x50 pixels)
- **Animação Direcional**: Sprite espelhado automaticamente baseado na direção
- **Velocidade**: 5 pixels por frame
- **Posição Inicial**: Centro-inferior da tela
- **Fallback**: Retângulo rosa caso a imagem não carregue

#### Cenário
- **Céu**: Azul céu (RGB: 135, 206, 235)
- **Nuvens**: 3 nuvens brancas estáticas em posições fixas
- **Plataforma**: Base marrom (terra) com cobertura verde (grama)
- **Altura da Plataforma**: 100 pixels

#### Sistema de Partículas
- **Pulo Normal**: 8 partículas cinzas
- **Pulo Duplo**: 12 partículas amareladas (mais vistoso)
- **Física Realista**: Gravidade, velocidade e fade-out
- **Posições Aleatórias**: Efeito natural e orgânico
- **Vida Útil**: 15-35 frames dependendo do tipo de pulo

#### Sistema de Pontuação
- **Altura em tempo real**: Medida em metros baseada na posição Y
- **Recorde pessoal**: Altura máxima alcançada é salva
- **Barra de progresso visual**: Indicador gráfico do progresso
- **HUD no canto superior direito**: Sempre visível durante o jogo
- **10 plataformas** estrategicamente posicionadas em alturas diferentes
- **Colisão precisa** permite pousar em qualquer plataforma
- **Design escalonado** com distâncias que requerem pulo duplo
- **Câmera dinâmica** segue o porquinho automaticamente
- **Plataforma especial** no topo com cor diferenciada
- **Reset de habilidades** ao pousar (pulo duplo recarrega)
- **Pulo Normal**: 8 partículas cinzas
- **Pulo Duplo**: 12 partículas amareladas (mais vistoso)
- **Física Realista**: Gravidade, velocidade e fade-out
- **Posições Aleatórias**: Efeito natural e orgânico
- **Vida Útil**: 15-35 frames dependendo do tipo de pulo
- **Pulo Normal**: Força de -15 pixels/frame (mais alto)
- **Pulo Duplo**: Força de -12 pixels/frame (um pouco menor)
- **Disponibilidade**: Pulo duplo só fica disponível após o primeiro pulo
- **Reset**: Sistema reseta quando o porquinho toca o chão
- **Feedback Visual**: Indicadores na interface mostram disponibilidade
- **Céu**: Azul céu (RGB: 135, 206, 235)
- **Nuvens**: 3 nuvens brancas estáticas em posições fixas
- **Plataforma**: Base marrom (terra) com cobertura verde (grama)
- **Altura da Plataforma**: 100 pixels

#### Cores Utilizadas
- **Azul Céu**: `(135, 206, 235)`
- **Verde Grama**: `(34, 139, 34)`
- **Marrom Terra**: `(139, 69, 19)`
- **Branco Nuvens**: `(255, 255, 255)`
- **Rosa Porquinho**: `(255, 182, 193)`

## 🚀 Como Executar

### 1. Instalação das Dependências
```bash
pip install pygame
```

### 2. Executar o Jogo
```bash
python game.py
```

### 3. Instalação Alternativa (Windows)
Se você estiver usando Windows com Python instalado via Microsoft Store:
```powershell
python3.11 -m pip install pygame
python3.11 game.py
```

## 📁 Estrutura do Projeto

```
gamePig/
│
├── game.py          # Arquivo principal do jogo
├── pig.png          # Sprite do personagem porquinho
└── README.md        # Este arquivo de documentação
```

## 🔧 Funcionalidades Implementadas

- ✅ Sistema de movimento horizontal do personagem
- ✅ Detecção de limites da tela
- ✅ Renderização de cenário dinâmico
- ✅ Loop principal do jogo com controle de FPS
- ✅ Sistema de eventos para fechar o jogo
- ✅ Sistema de pulo com física realista
- ✅ **Sistema de pulo duplo** com mecânicas avançadas
- ✅ **10 plataformas suspensas** em diferentes alturas
- ✅ **Sistema de câmera dinâmica** que segue o porquinho
- ✅ **Sistema de pontuação por altura** alcançada
- ✅ **HUD em tempo real** com altura atual e recorde
- ✅ Controles visuais na tela com feedback
- ✅ **Sprite personalizado PNG do porquinho**
- ✅ **Sprite espelhado baseado na direção do movimento**
- ✅ Sistema de fallback para retângulo básico
- ✅ **Sistema de partículas de fumaça** para pulos
- ✅ **Efeitos visuais diferenciados** para pulo normal vs. duplo
- ✅ **Colisão precisa** com plataformas e chão
- ✅ **Sprite espelhado baseado na direção do movimento**
- ✅ Sistema de fallback para retângulo básico
- ✅ **Sistema de partículas de fumaça** para pulos
- ✅ **Efeitos visuais diferenciados** para pulo normal vs. duplo

## 🎯 Possíveis Melhorias Futuras

- 🎨 Backgrounds em camadas (parallax scrolling)
- 🎵 Efeitos sonoros e música de fundo
-  Coleta de itens (frutas, moedas, power-ups)
- 👾 Inimigos e obstáculos móveis
- 🏆 Sistema de conquistas e desafios
- 🎨 Gráficos mais detalhados e sprites animados
- 🌟 **Plataformas móveis e quebráveis**
- 💾 Sistema de save/load de recordes
- 🏃‍♂️ **Modo contrarrelógio**
- ⚡ **Power-ups de pulo triplo**

## 🐛 Problemas Conhecidos

Nenhum problema conhecido no momento. O jogo está funcionando conforme esperado.

## 👨‍💻 Desenvolvimento

### Arquitetura do Código
- **Loop Principal**: Controla o fluxo principal do jogo
- **Sistema de Eventos**: Gerencia entrada do usuário
- **Renderização**: Desenha todos os elementos na tela
- **Física Simples**: Movimento básico e detecção de limites

### Dependências
- `pygame`: Biblioteca principal para desenvolvimento de jogos
- `sys`: Biblioteca padrão do Python para funções do sistema

## 📜 Licença

Este é um projeto educacional e está disponível para uso livre.

## 🤝 Contribuições

Sinta-se à vontade para fazer fork do projeto e implementar melhorias!

---

**Desenvolvido com ❤️ usando Python e Pygame**
