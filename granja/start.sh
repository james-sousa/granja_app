#!/bin/bash
# Script para iniciar Granja Manager rapidamente

echo "🐔 Granja Manager - MVP Completo"
echo "=================================="
echo ""

# Verifica se Flet está instalado
if ! python3 -c "import flet" 2>/dev/null; then
    echo "⚠️  Flet não encontrado. Instalando dependências..."
    pip install -r requirements.txt
fi

# Executa a aplicação
echo "🚀 Iniciando aplicação..."
python3 run.py
