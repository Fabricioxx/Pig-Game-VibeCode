# 💨 Como Adicionar Imagem de Fumaça Personalizada

## 🎨 Opção Atual
O jogo está usando **formas geométricas** (círculos cinzas) para criar o efeito de fumaça. Isso funciona perfeitamente e não requer imagens adicionais!

## 🖼️ Para Usar Imagem Personalizada (Opcional)

Se você quiser usar uma imagem PNG personalizada para a fumaça:

### 1. **Criar/Obter Imagem de Fumaça**
- **Nome do arquivo**: `smoke.png`
- **Tamanho recomendado**: 16x16 até 32x32 pixels
- **Fundo**: Transparente (PNG com alpha)
- **Estilo**: Nuvenzinha de fumaça, puff, ou similar

### 2. **Onde Encontrar/Criar**
- **Criar no Paint/GIMP**: Desenhe uma pequena nuvem cinza
- **Sites gratuitos**: 
  - OpenGameArt.org
  - Itch.io (assets gratuitos)
  - Pixabay (sprites de jogos)
- **Gerar com IA**: Usar DALL-E, Midjourney para "pixel art smoke puff transparent background"

### 3. **Como Usar**
1. Coloque o arquivo `smoke.png` no mesmo diretório do `game.py`
2. Execute o jogo
3. Você verá: "✅ Imagem de fumaça carregada com sucesso!"

### 4. **Especificações Técnicas da Imagem**
```
- Formato: PNG
- Transparência: Sim (fundo transparente)
- Tamanho: Será redimensionado para 16x16 pixels
- Cores: Cinza claro/branco para melhor efeito
- Estilo: Simples, não muito detalhado
```

## 🎮 Efeito Atual (Sem Imagem)
- ✅ 8 partículas por pulo
- ✅ Movimento realista com gravidade
- ✅ Fade out gradual
- ✅ Tamanhos variados
- ✅ Posições aleatórias
- ✅ Contador de partículas ativas na tela

## 🔧 Como Funciona
O jogo detecta automaticamente se existe `smoke.png`:
- **Com imagem**: Usa a imagem PNG com transparência
- **Sem imagem**: Usa círculos geométricos (como está agora)

**Ambas as opções funcionam perfeitamente!** 🎉
