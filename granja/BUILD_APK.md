# 📱 Guia: Build APK com GitHub Actions

## 🚀 Setup Inicial

### Passo 1: Adicionar Secrets no GitHub

1. Vá para seu repositório GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret** e adicione:

```
SUPABASE_URL = https://rxhtfvelzqofzpbzgqfw.supabase.co
SUPABASE_ANON_KEY = sua_chave_publica_aqui
```

### Passo 2: Commit e Push do Workflow

O arquivo `.github/workflows/build-apk.yml` já está no repositório.

Para ativar o workflow, você pode:

**Opção A - Criar uma TAG (Recomendado)**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Opção B - Executar Manualmente**
- GitHub → **Actions** → **Build APK** → **Run workflow**

### Passo 3: Acompanhar o Build

1. Vá para **GitHub Actions**
2. Clique no workflow em progresso
3. Veja logs em tempo real

## 📥 Baixar o APK

Após o build completar com sucesso:

**Se criou uma TAG:**
- Vá para **Releases** (lado direito do repo)
- O APK estará anexado à release

**Sempre disponível:**
- **Actions** → último workflow → **Artifacts**
- Download do `granja-app-apk.zip`

## ⚙️ Customizações

### Mudar o nome do APK
No `build-apk.yml`, linha 26:
```yaml
flet build apk --output seu-nome-aqui.apk
```

### Adicionar Versão Automática
```yaml
flet build apk --output granja-app-v${{ github.ref_name }}.apk
```

### Build em múltiplas plataformas
Criar outro arquivo `.github/workflows/build-web.yml` para web build.

## 🔧 Troubleshooting

**"Build failed"**
- Verificar requirements.txt está correto
- Conferir SUPABASE_URL e SUPABASE_ANON_KEY nos Secrets

**"flet-cli not found"**
- Adicione na seção de dependências:
```bash
pip install flet-cli==0.25.2
```

**APK muito grande**
- Adicione flag ao build:
```yaml
flet build apk --output granja-app.apk --split-debug-info
```

## 📦 Configuração do Flet (Opcional)

Se precisar de configurações extras, crie `pubspec.yaml` no root:

```yaml
name: granja_manager
description: Gerenciador de Granja com Supabase
version: 1.0.0+1
```

## ✅ Checklist Final

- [ ] `.github/workflows/build-apk.yml` commitado
- [ ] Secrets (SUPABASE_URL, SUPABASE_ANON_KEY) adicionados no GitHub
- [ ] `requirements.txt` atualizado
- [ ] `run.py` pronto para rodar
- [ ] TAG criada (v1.0.0) ou workflow executado manualmente

Pronto! Seu APK será gerado automaticamente! 🎉
