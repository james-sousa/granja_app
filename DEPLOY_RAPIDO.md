# 🚀 Deploy Rápido - Railway.app

## 1️⃣ Preparação Local (5 min)

```bash
# Navegar ao projeto
cd /home/bart/Área\ de\ trabalho/james_ubuntu/Área\ de\ trabalho/Área_de_Trabalho/Area_de_trabalho/app_desktop/granja_app

# Fazer commit
git add Procfile requirements.txt runtime.txt .env.example DEPLOY_RAILWAY.md CHECKLIST_DEPLOY.md
git commit -m "Preparar para deploy Railway"
git push origin main
```

## 2️⃣ No Railway (10 min)

### Criar Projeto
1. Abra https://railway.app
2. Clique **"New Project"**
3. Selecione **"Deploy from GitHub"**
4. Autorize e selecione repositório `granja_app`

### Configurar Variáveis
1. No dashboard do projeto, clique **"Variables"**
2. Adicione estas variáveis (**importante: não fazer commit!**):

```
SUPABASE_URL=https://sua-url.supabase.co
SUPABASE_ANON_KEY=sua-chave-anonima
```

### Deploy
1. Railway detectará `Procfile` automaticamente
2. Clique **"Deploy"** e aguarde ✅

## 3️⃣ Testar (5 min)

1. Clique no URL gerado (ex: `https://granja-prod.up.railway.app`)
2. Teste:
   - ✅ Fazer login
   - ✅ Testar "Esqueci a senha"
   - ✅ CRUD básico

## ⚙️ O Que foi Configurado

| Arquivo | Propósito |
|---------|-----------|
| `Procfile` | Instrui Railway como iniciar a app |
| `requirements.txt` (raiz) | Dependências Python |
| `runtime.txt` | Versão do Python (3.11.8) |
| `.env.example` | Template de variáveis |
| `DEPLOY_RAILWAY.md` | Guia detalhado |
| `CHECKLIST_DEPLOY.md` | Checklist completo |

## 🆘 Problema?

Se der erro:

1. **Verificar logs**: Dashboard → Deployments → ver logs
2. **Variáveis**: Confirmar SUPABASE_URL e SUPABASE_ANON_KEY estão corretas
3. **Porta**: Procfile usa `$PORT` do Railway
4. **Git**: `git push` dispara redeploy automático

## 📊 Monitoramento

- Railway monitora logs em tempo real
- Redeploy automático a cada push no GitHub
- Adicione domínio customizado em Settings → Domains

---

**Pronto para ir ao ar!** 🎉
