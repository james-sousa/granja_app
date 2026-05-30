# 🚀 Granja Manager - Supabase Quick Start

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Criar Projeto Supabase
```
https://supabase.com → New Project
Name: "Granja Manager"
Region: "Brazil (São Paulo)"
```

### 2️⃣ Executar SQL Migrations
1. Em Supabase: **SQL Editor** → **New query**
2. Copie todo o arquivo: `granja_manager/database/supabase_migrations.sql`
3. Cole e execute (Ctrl+Enter)

### 3️⃣ Configurar Credenciais
```bash
# Copie o template
cp .env.example .env

# Edite .env e preencha:
# SUPABASE_URL=sua_url
# SUPABASE_KEY=sua_chave
```

### 4️⃣ Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5️⃣ Executar Setup
```bash
python setup_supabase.py
```

### 6️⃣ Iniciar App
```bash
python run.py
```

✅ **Pronto! Seu sistema agora usa Supabase remoto!**

---

## 📖 Documentação Completa
Ver arquivo: `SUPABASE_SETUP.md`

---

## 🔄 Arquitetura Híbrida

- ✅ **Supabase configurado?** → Usa banco remoto
- ❌ **Sem .env?** → Cai para SQLite local (dev only)

Isso permite desenvolver offline e migrar depois!

---

## 📊 Múltiplos Usuários

Todos na mesma granja acessam o **mesmo banco**:

```
Usuário A (Desktop)  ┐
Usuário B (Tablet)   ├─ → Supabase → PostgreSQL Remoto
Usuário C (Web)      ┘
```

Dados sincronizados em tempo real! ⚡

---

## 🐛 Problemas?

1. Verifique logs: `granja_manager/logs/app.log`
2. Teste no Supabase Dashboard: **Table Editor**
3. Releia `SUPABASE_SETUP.md` → Troubleshooting
