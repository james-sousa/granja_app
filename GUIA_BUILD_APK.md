# 📱 Guia Completo: Build APK para Android

## 🎯 Opção 1: Build Local (Na Sua Máquina)

### Requisitos:
- Python 3.10+
- Flet CLI instalado
- AndroidSDK (opcional, Flet gerencia automaticamente)

### Passo 1: Instalar Dependências

```bash
# Ir para pasta do projeto
cd granja

# Instalar flet-cli
pip install flet-cli==0.25.2

# Verificar instalação
flet --version
```

### Passo 2: Preparar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas credenciais Supabase
nano .env
```

Seu `.env` deve ter:
```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima_aqui
```

### Passo 3: Executar Build

```bash
# Fazer build do APK
flet build apk --output granja-app.apk

# Saída esperada:
# ✅ build/outputs/granja-app.apk (~ 50-100MB)
```

### Passo 4: Localizar o APK

O arquivo gerado ficará em:
```
granja/build/outputs/granja-app.apk
```

### Transferir para Android:
```bash
# Usar ADB (Android Debug Bridge)
adb install build/outputs/granja-app.apk

# Ou transferir via USB/nuvem para instalar no celular
```

---

## 🚀 Opção 2: Build Automatizado com GitHub Actions

### Requisitos:
- Repositório GitHub
- Secrets configurados no GitHub

### Passo 1: Copiar Workflow para `.github/workflows`

Se ainda não tiver a pasta `.github/workflows`:

```bash
mkdir -p .github/workflows
cp granja/granja_app/workflows/build-apk.yml .github/workflows/
```

### Passo 2: Adicionar Secrets no GitHub

1. Vá para seu repositório no GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret** e adicione:

```
SUPABASE_URL
Valor: https://seu-projeto.supabase.co

SUPABASE_ANON_KEY  
Valor: sua_chave_anonima_aqui
```

### Passo 3: Ativar o Workflow

**Opção A - Criar uma TAG (Recomendado)**
```bash
git add .github/workflows/build-apk.yml
git commit -m "feat: add GitHub Actions APK build workflow"
git tag v1.0.0
git push origin v1.0.0
```

**Opção B - Executar Manualmente**
1. GitHub → **Actions**
2. Selecionar **Build APK** (à esquerda)
3. Clicar **Run workflow**

### Passo 4: Acompanhar o Build

1. Vá para **GitHub** → **Actions**
2. Clique no workflow em progresso
3. Veja logs em tempo real

### Passo 5: Baixar o APK

**Se criou uma TAG:**
- Vá para **Releases** → selecione a release
- Download do `granja-app.apk`

**Sempre disponível:**
- **Actions** → último workflow → **Artifacts**
- Download do `granja-app-apk.zip`

---

## ✅ Checklist Pré-Build

- [ ] `.env` com SUPABASE_URL e SUPABASE_ANON_KEY
- [ ] `requirements.txt` atualizado
- [ ] `run.py` testado localmente (`python run.py`)
- [ ] Git commitado (se usar GitHub Actions)
- [ ] Flet CLI instalado (se usar build local)

---

## 🔧 Troubleshooting

### ❌ "flet-cli not found"
```bash
pip install --upgrade flet-cli
```

### ❌ "Build failed - dependencies missing"
```bash
pip install -r requirements.txt
flet build apk --output granja-app.apk
```

### ❌ "APK muito grande"
```bash
# Adicione --split-debug-info para reduzir tamanho
flet build apk --output granja-app.apk --split-debug-info
```

### ❌ "Supabase connection errors"
- Verificar SUPABASE_URL e SUPABASE_ANON_KEY nos Secrets
- Confirmar projeto está ativo em supabase.com

### ❌ "JAVA_HOME not found" (alguns sistemas)
```bash
# Flet geralmente instala Java automaticamente
# Se problema persistir, instale JDK 17+
# Ubuntu:
sudo apt install openjdk-17-jdk

# macOS:
brew install openjdk@17
```

---

## 📦 Customizações

### Mudar Nome do APK
Editar em `.github/workflows/build-apk.yml`:
```yaml
- name: Build APK with Flet
  run: |
    flet build apk --output meu-app-customizado.apk
```

### Versão Automática no Nome
```yaml
flet build apk --output granja-app-v${{ github.ref_name }}.apk
```

### Notificações de Sucesso
Adicionar ao final do workflow:
```yaml
- name: Notify on Success
  run: echo "✅ APK gerado com sucesso!"
```

---

## 📊 Tamanho Esperado do APK
- Sem otimizações: ~80MB
- Com `--split-debug-info`: ~50-60MB
- Para distribuição: comprimir com 7-Zip (~20-30MB)

---

## 🎓 Referências
- [Flet Documentação](https://flet.dev)
- [Supabase](https://supabase.com)
- [GitHub Actions](https://docs.github.com/actions)

