# ✅ Checklist de Deployment - Railway.app

## 📦 Preparação do Ambiente

- [x] **Procfile** - Configurado para `flet run --web`
- [x] **requirements.txt** - Todas as dependências listadas
- [x] **runtime.txt** - Python 3.11.8 especificado
- [x] **.env.example** - Template de variáveis de ambiente
- [ ] **.env** - Arquivo local com credenciais (NUNCA fazer commit)

## 🔐 Variáveis de Ambiente Obrigatórias

Configure estas no Railway:

```
SUPABASE_URL          = https://seu-projeto.supabase.co
SUPABASE_ANON_KEY     = sua-chave-anonima-aqui
```

## 📋 Passos Finais Antes do Deploy

### 1. Verificar Git
```bash
# Confirmar que .env está em .gitignore
grep ".env" .gitignore

# Fazer último commit
git add Procfile runtime.txt .env.example DEPLOY_RAILWAY.md CHECKLIST_DEPLOY.md
git commit -m "Preparar para deploy em Railway"
git push origin main
```

### 2. Verificar Dependências
```bash
# Dentro de granja/
pip install -r requirements.txt
python3 -m py_compile granja_manager/app.py
```

### 3. Testar Localmente
```bash
# Teste em modo web
flet run --web run.py

# Acesse http://localhost:8000
# Verifique se as credenciais Supabase funcionam
```

### 4. No Railway Dashboard

**Novo Projeto:**
1. Clique "New Project" → "Deploy from GitHub"
2. Selecione repositório `granja_app`
3. Railway detectará Procfile automaticamente

**Variáveis de Ambiente:**
1. Vá para "Variables"
2. Adicione cada variável do checklist acima
3. Clique "Add Variable"

**Deploy:**
1. Railway fará build automaticamente
2. Observar logs em "Deployments"
3. Aguardar status ✅

### 5. Validar Após Deploy

- [ ] Acessar URL fornecida pelo Railway
- [ ] Testar login com credenciais Supabase
- [ ] Testar "Esqueci a senha" 
- [ ] Verificar redireccionamento de recovery
- [ ] Testar CRUD básico
- [ ] Verificar logs para erros

## 🚨 Problemas Comuns

### Porta inválida
**Erro**: `Address already in use`
- Railway passa `$PORT` automaticamente
- Procfile deve usar `--port $PORT`

### Supabase conexão recusada
**Erro**: `Failed to connect to Supabase`
- Verificar SUPABASE_URL e SUPABASE_ANON_KEY
- Confirmar que credenciais estão no Railway (não no código)
- Revisar CORS no Supabase

### Módulos não encontrados
**Erro**: `ModuleNotFoundError: No module named 'flet'`
- Confirmar requirements.txt está no diretório raiz
- Railway executa `pip install -r requirements.txt` automaticamente

### Timeout na inicialização
**Erro**: `Application startup failed`
- Flet demora para compilar web assets
- Railway tem timeout de 60s, pode aumentar em Settings
- Considere usar `flet build web` previamente

## 📞 Suporte

- **Railway Docs**: https://docs.railway.app
- **Flet Docs**: https://flet.dev
- **Supabase Docs**: https://supabase.com/docs

## 🎯 Próximas Melhorias Pós-Deploy

- [ ] Configurar domínio personalizado
- [ ] Adicionar observability (Sentry/NewRelic)
- [ ] Implementar CI/CD avançado
- [ ] Configurar auto-scaling
- [ ] Adicionar cache (Redis)
- [ ] Monitoramento de performance

---

**Status**: Pronto para deploy! ✅
