# 🚀 Guia de Configuração: Supabase para Granja Manager

## 📋 Visão Geral

Este projeto foi configurado para usar **Supabase** (banco remoto PostgreSQL) ao invés de SQLite local. Isso permite que **múltiplos usuários** acessem os dados da granja simultaneamente.

---

## 🎯 Passo 1: Criar Projeto no Supabase

### 1.1 Acesse Supabase
- Abra [https://supabase.com](https://supabase.com)
- Clique em **"Sign Up"**
- Use email ou GitHub para criar conta

### 1.2 Crie um Novo Projeto
1. Após criar conta, clique **"New Project"**
2. Preencha:
   - **Project name**: `Granja Manager`
   - **Database password**: Crie uma senha forte (copie para lugar seguro!)
   - **Region**: `Brazil (São Paulo)` ← **IMPORTANTE para performance**
3. Clique **"Create new project"**
4. Aguarde 2-3 minutos para o projeto ficar pronto ✅

---

## 🔑 Passo 2: Obter Credenciais

### 2.1 Copie a URL do Projeto
1. Vá em **Settings** (ícone de engrenagem)
2. Clique em **API**
3. Copie o valor de **Project URL** (começa com `https://`)
4. Cole em lugar seguro

### 2.2 Copie a API Key
1. Ainda em **Settings → API**
2. Copie o valor de **"anon public"** (a chave pública)
3. Cole em lugar seguro

**Suas credenciais são como senhas: NUNCA compartilhe com ninguém!**

---

## 📊 Passo 3: Criar Tabelas no Supabase

### 3.1 Acesse SQL Editor
1. No painel do Supabase, clique em **SQL Editor** (ícone de chave inglesa)
2. Clique em **"New query"**

### 3.2 Execute as Migrações
1. Abra o arquivo:
   ```
   granja_manager/database/supabase_migrations.sql
   ```
2. **Copie TODO o conteúdo** do arquivo
3. Cole no SQL Editor do Supabase
4. Clique **"Run"** (ou Ctrl+Enter)
5. Aguarde até aparecer ✅ **"Success"**

**Agora as tabelas foram criadas!**

---

## 🔐 Passo 4: Configurar Arquivo .env

### 4.1 Crie arquivo `.env` na raiz do projeto
Copie de `.env.example`:

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

### 4.2 Edite `.env`
Abra o arquivo `.env` e preencha com suas credenciais:

```env
SUPABASE_URL=https://seu-projeto-aqui.supabase.co
SUPABASE_KEY=sua-chave-publica-aqui
```

**Exemplo:**
```env
SUPABASE_URL=https://myproject123.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ NUNCA commit o .env para Git!** Ele já está no `.gitignore`

---

## 📦 Passo 5: Instalar Dependências

```bash
pip install -r requirements.txt
```

Isso vai instalar:
- `flet` - Interface gráfica
- `supabase` - Cliente Supabase
- `python-dotenv` - Carrega variáveis de ambiente

---

## ▶️ Passo 6: Executar a Aplicação

```bash
# Via Python direto
python run.py

# Ou com Flet
flet run run.py

# Para teste na web
flet run --web run.py
```

### Primeira Execução
- Na primeira vez, o app vai tentar conectar ao Supabase
- Se as credenciais estão corretas: **✅ Conectado ao Supabase com sucesso**
- Se houver erro: Verifique se:
  - ✓ Arquivo `.env` existe
  - ✓ Credenciais estão corretas (sem espaços extras)
  - ✓ Projeto Supabase foi criado com sucesso

---

## 🔄 Modo Híbrido: SQLite + Supabase

Se Supabase não estiver configurado, a app **automaticamente cai para SQLite local**:

```
⚠️  Supabase não configurado. Usando SQLite local (só para desenvolvimento).
```

Isso permite:
- 🧪 Desenvolvimento offline
- 🚀 Transição gradual para Supabase
- 📦 Fallback automático

---

## ✅ Checklist Final

- [ ] Conta Supabase criada
- [ ] Projeto "Granja Manager" criado
- [ ] SQL migrations executadas (✅ no SQL Editor)
- [ ] Arquivo `.env` criado e preenchido
- [ ] `pip install -r requirements.txt` executado
- [ ] App rodando com sucesso
- [ ] Vendo dados sincronizados no Supabase

---

## 🐛 Troubleshooting

### Erro: "Supabase not configured"
**Solução**: Verifique se:
```python
# config.py deve ter:
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
```

### Erro: "Connection refused"
**Solução**: 
- Verifique internet
- Confirme credenciais em `.env`
- Teste conectividade: `ping supabase.com`

### Erro: "Table not found"
**Solução**:
- Re-execute o SQL em `supabase_migrations.sql`
- Confirme em **SQL Editor → select** (deve listar as tabelas)

### App fica lento
**Solução**:
- Supabase usa plano gratuito: limite de 50 mil linhas
- Se exceder, migre para plano **Pro** (R$ 25/mês)

---

## 📱 Usando em Múltiplos Dispositivos

Com Supabase, todos os usuários da granja podem acessar:

1. **Desktop**: `python run.py` em qualquer máquina
2. **Tablet**: `flet run --web --host 0.0.0.0 run.py`
3. **Smartphone**: Acesse `http://seu-ip:8550`

Os dados são **sincronizados em tempo real**! ⚡

---

## 🔒 Segurança

### Credenciais Seguras
- **`SUPABASE_URL`**: Pode ser pública
- **`SUPABASE_KEY`**: Deve ser secreta (como uma senha)
- Nunca compartilhe a **Service Role Key** (é super admin)

### Row Level Security (RLS)
Para produção, habilite RLS em `supabase_migrations.sql`:
```sql
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
-- ... etc
```

---

## 📚 Documentação Adicional

- Supabase Docs: [https://supabase.com/docs](https://supabase.com/docs)
- Python Client: [https://github.com/supabase-community/supabase-py](https://github.com/supabase-community/supabase-py)
- PostgreSQL Docs: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)

---

## ❓ Dúvidas?

Se algo não funcionar:
1. Revise os logs em `granja_manager/logs/app.log`
2. Verifique os dados em `Supabase Dashboard → Table Editor`
3. Teste queries em `SQL Editor`

---

**Pronto! Seu sistema agora está preparado para múltiplos usuários! 🎉**
