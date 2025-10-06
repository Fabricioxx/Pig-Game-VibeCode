# 🚀 Guia Rápido de Instalação - Jogo do Porquinho

## ⚠️ IMPORTANTE - LEIA PRIMEIRO!

O Python foi instalado no seu sistema, mas você precisa **FECHAR e REABRIR o terminal** para que funcione!

---

## 📋 Passo a Passo

### 1️⃣ Fechar o Terminal Atual
- Clique no **X** ou digite `exit`
- Isso é necessário para atualizar o PATH do sistema

### 2️⃣ Abrir Novo Terminal
- Pressione `Ctrl + Shift + '` (abre novo terminal no VS Code)
- OU: Menu > Terminal > Novo Terminal

### 3️⃣ Verificar Python
```powershell
python --version
```
**Resultado esperado:** `Python 3.12.10` (ou similar)

### 4️⃣ Instalar Pygame
```powershell
python -m pip install pygame
```
**Aguarde a instalação (pode demorar 1-2 minutos)**

### 5️⃣ Executar o Jogo! 🎮
```powershell
python game.py
```

---

## ❓ Problemas Comuns

### "Python não foi encontrado"
**Solução:**
1. Feche TODOS os terminais abertos
2. Feche o VS Code completamente
3. Abra o VS Code novamente
4. Tente novamente

### "No module named 'pygame'"
**Solução:**
```powershell
python -m pip install --upgrade pygame
```

### Jogo não abre janela
**Solução:**
- Verifique se tem placa de vídeo funcionando
- Tente atualizar drivers de vídeo

---

## 🎮 Controles do Jogo

| Tecla | Ação |
|-------|------|
| ← → | Mover esquerda/direita |
| ESPAÇO | Pular (primeiro pulo) |
| ESPAÇO (no ar) | Pulo duplo |
| F3 | Ativar/desativar modo debug |
| ESC | Fechar jogo |

---

## 🎯 Dicas de Jogo

1. **Use o pulo duplo com sabedoria** - Você só tem um por pulo!
2. **Procure molas azuis** - Elas dão super pulo!
3. **Cuidado com plataformas marrons escuras** - São quebráveis!
4. **Evite quedas longas** - Mais de 60m é fatal!
5. **Voltar ao chão** - Regenera o mapa (se você subiu antes)

---

## ✅ Checklist de Verificação

- [ ] Terminal fechado e reaberto
- [ ] `python --version` funciona
- [ ] Pygame instalado sem erros
- [ ] Jogo executando
- [ ] Porquinho aparece na tela
- [ ] Controles funcionam
- [ ] Imagens carregadas (✅ ou 🎯 para formas)

---

## 📞 Arquivos Necessários

Verifique se você tem:
- ✅ `game.py` - Código principal
- ✅ `pig.png` - Imagem do porquinho
- ⚠️ `smoke.png` - (Opcional) Efeito de fumaça

**OBS:** Se faltar `smoke.png`, o jogo usará formas geométricas automaticamente!

---

## 🔧 Comandos Úteis

### Atualizar pip
```powershell
python -m pip install --upgrade pip
```

### Verificar pacotes instalados
```powershell
python -m pip list
```

### Reinstalar Pygame (se necessário)
```powershell
python -m pip uninstall pygame
python -m pip install pygame
```

---

## 🎉 Tudo Pronto!

Quando você ver essa mensagem no terminal:
```
✅ Imagem do porquinho carregada com sucesso!
```

**O jogo está funcionando perfeitamente!** 🐷🎮

---

**Boa sorte alcançando o topo! 🚀**
