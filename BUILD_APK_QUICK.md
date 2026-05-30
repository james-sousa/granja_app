# ⚡ Quick Start: Build APK

## 🚀 Opção 1: Build Local em 3 Passos (MAIS RÁPIDO)

### 1️⃣ Dar permissão de execução ao script
```bash
chmod +x build_apk.sh
```

### 2️⃣ Executar o script
```bash
./build_apk.sh
```

### 3️⃣ Pronto! 🎉
Seu APK estará em:
```
granja/build/outputs/granja-app.apk
```

---

## 🔧 Build Local Avançado

### Apenas testar se está tudo OK (sem gerar APK)
```bash
./build_apk.sh --test
```

### Build limpo (remove tudo e reconstrói)
```bash
./build_apk.sh --clean
```

### Build com nome customizado
```bash
./build_apk.sh --output meu-app-v1.0.apk
```

---

## 🌐 Opção 2: Build Automatizado com GitHub

### 1️⃣ Adicionar o código ao GitHub
```bash
git add .github/workflows/build-apk.yml GUIA_BUILD_APK.md build_apk.sh
git commit -m "feat: adicionar workflow de build APK"
git push
```

### 2️⃣ Configurar Secrets no GitHub
1. Vá para seu repositório → **Settings** 
2. → **Secrets and variables** → **Actions**
3. Clique **New repository secret** e adicione:

**Secret 1:**
```
Nome: SUPABASE_URL
Valor: https://seu-projeto.supabase.co
```

**Secret 2:**
```
Nome: SUPABASE_ANON_KEY
Valor: sua_chave_anonima_aqui
```

### 3️⃣ Criar uma TAG para ativar o build
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 4️⃣ Acompanhar o build
1. Vá para **GitHub** → **Actions**
2. Clique na workflow em progresso
3. Veja os logs em tempo real

### 5️⃣ Baixar o APK
Após o build terminar:
- **Releases** → encontre a tag v1.0.0 → baixe o `granja-app.apk`
- **OU em Actions** → clique no último workflow → **Artifacts** → baixe `granja-app-apk`

---

## 📋 Checklist

- [ ] `.env` criado com `SUPABASE_URL` e `SUPABASE_ANON_KEY`
- [ ] `run.py` testado localmente: `python granja/run.py` (funciona?)
- [ ] Para build local: `./build_apk.sh`
- [ ] Para GitHub: Secrets configurados no repositório

---

## 🐛 Problemas Comuns

### ❌ "command not found: flet"
```bash
pip install flet-cli==0.25.2
```

### ❌ "build_apk.sh: permission denied"
```bash
chmod +x build_apk.sh
./build_apk.sh
```

### ❌ ".env not found"
```bash
cd granja
cp .env.example .env
# Edite .env com suas credenciais
```

### ❌ "APK não encontrado"
- Verificar se Python 3.10+ está instalado: `python --version`
- Tentar com `--clean`: `./build_apk.sh --clean`

---

## 💡 Dicas

- **Build local é mais rápido** para testes (5-10 minutos)
- **GitHub Actions é melhor** para distribução automática
- Transferir para Android: `adb install granja/build/outputs/granja-app.apk`

---

📖 **Para mais detalhes**: veja [GUIA_BUILD_APK.md](GUIA_BUILD_APK.md)

