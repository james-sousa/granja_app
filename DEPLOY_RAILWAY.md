# Deploy na Railway.app - Guia Completo

## 📋 Pré-requisitos

- Conta no [Railway.app](https://railway.app)
- GitHub configurado com o repositório
- Variáveis de ambiente do Supabase prontas

## 🚀 Passo a Passo para Deploy

### 1. Preparar Variáveis de Ambiente

Copie o arquivo `.env.example` para referência:

```bash
cp .env.example .env
```

Atualize com suas credenciais:
```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-anonima
```

### 2. Conectar ao Railway

1. Acesse [railway.app](https://railway.app)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub"**
4. Autorize o acesso ao GitHub
5. Selecione o repositório `granja_app`

### 3. Configurar o Projeto

1. Railway detectará automaticamente o `Procfile`
2. Configure as variáveis de ambiente:
   - Na aba "Variables" do projeto
   - Adicione: `SUPABASE_URL` e `SUPABASE_ANON_KEY`

### 4. Deploy

1. Clique em **"Deploy"**
2. Railway fará:
   - Build da imagem Docker
   - Instalação do `requirements.txt`
   - Execução do Procfile

### 5. Verificar Status

- Abra a aba "Deployments"
- Aguarde o build terminar (indicado por ✅)
- Clique no URL da aplicação

## 📝 Arquivo de Configuração

### Procfile
```
web: cd granja && flet run --web --host 0.0.0.0 --port $PORT run.py
```

### runtime.txt
```
python-3.11.8
```

## ⚙️ Troubleshooting

### Porta não encontrada
Se a aplicação não iniciar, verifique se `$PORT` é capturada corretamente em `run.py`

### Variáveis não carregam
Confirme que `.env` não está no `.gitignore` (as vars devem estar no Railway, não no git)

### Supabase conexão falha
- Verifique SUPABASE_URL e SUPABASE_ANON_KEY
- Confirme que o Supabase aceita requisições HTTP
- Adicione seu domínio Railway nas origens permitidas do Supabase

## 🔗 Domínio Personalizado (Opcional)

1. Vá para **Projeto > Settings > Domains**
2. Clique em **"Add Domain"**
3. Configure seu domínio customizado

## 📊 Monitorar em Produção

- **Logs**: Aba "Deployments" > ver logs em tempo real
- **Performance**: Verifique uso de CPU/Memória
- **Alertas**: Configure notificações para falhas

## 🔄 Atualizar Após Mudanças

Cada push para o GitHub redeploy automaticamente:

```bash
git add .
git commit -m "Atualizar features"
git push origin main
```

Railway detectará automaticamente e redeployará!

## 📌 Próximos Passos

- [ ] Teste a aplicação em staging primeiro
- [ ] Configure CORS no Supabase para seu domínio Railway
- [ ] Adicione logging centralizado (Sentry, LogRocket)
- [ ] Configure backup automático do banco Supabase
