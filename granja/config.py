"""Arquivo de configuração do projeto Granja Manager"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# ═══════════════════════════════════════════════════════════════
# BANCO DE DADOS - SUPABASE (Remoto PostgreSQL)
# ═══════════════════════════════════════════════════════════════
# Obtenha estas credenciais em https://supabase.com:
# 1. Faça login/crie conta
# 2. Crie novo projeto "Granja Manager" 
# 3. Em Settings → API → copie URL e ANON KEY (não service_role_key!)
# 4. Crie arquivo .env com:
#    SUPABASE_URL=sua_url
#    SUPABASE_ANON_KEY=sua_anon_key

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Usar Supabase (remoto) ou SQLite (local para dev)
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_ANON_KEY)

# Fallback para SQLite se Supabase não estiver configurado
if not USE_SUPABASE:
    import warnings
    warnings.warn("⚠️  Supabase não configurado. Usando SQLite local (só para desenvolvimento).")
    
DATABASE_PATH = "granja_manager/data/granja.db"
LOGS_PATH = "granja_manager/logs/app.log"

# Configurações de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configurações da aplicação
APP_NAME = "Granja Manager"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 700

# Configurações de validação
TELEFONE_MIN_DIGITS = 10
TELEFONE_MAX_DIGITS = 13
NOME_MIN_LENGTH = 3
DESCRICAO_MIN_LENGTH = 3

# Configurações de estoque
ALERTA_ESTOQUE_LIMITE_PADRAO = 10

# Configurações de categorias de gastos
CATEGORIAS_GASTOS = [
    "Insumos",
    "Energia",
    "Funcionários",
    "Medicamentos",
    "Transporte",
    "Outros"
]
