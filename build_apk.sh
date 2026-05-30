#!/bin/bash

# Script para Build APK do Granja Manager
# Uso: ./build_apk.sh [--help]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de ajuda
show_help() {
    cat << EOF
${BLUE}📱 Build APK - Granja Manager${NC}

Uso: ./build_apk.sh [opções]

Opções:
  --help              Mostra esta mensagem
  --clean             Remove build anterior e recria
  --test              Apenas testa dependências
  --output NAME       Nome customizado do APK (padrão: granja-app.apk)

Exemplos:
  ./build_apk.sh                          # Build padrão
  ./build_apk.sh --clean                  # Build limpo
  ./build_apk.sh --output meu-app.apk    # Build com nome customizado
  ./build_apk.sh --test                   # Apenas testa

${YELLOW}Pré-requisitos:${NC}
  ✅ Python 3.10+
  ✅ pip instalado
  ✅ .env com SUPABASE_URL e SUPABASE_ANON_KEY

EOF
}

# Variáveis
OUTPUT_FILE="granja-app.apk"
CLEAN_BUILD=false
TEST_ONLY=false
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/granja" && pwd)"

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --test)
            TEST_ONLY=true
            shift
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}❌ Opção desconhecida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Verificar se estamos no diretório correto
if [ ! -f "$PROJECT_DIR/run.py" ]; then
    echo -e "${RED}❌ Erro: arquivo run.py não encontrado${NC}"
    echo "Certifique-se de executar este script da raiz do repositório"
    exit 1
fi

echo -e "${BLUE}🚀 Build APK - Granja Manager${NC}\n"

# Step 1: Verificar .env
echo -e "${YELLOW}[1/5]${NC} Verificando configurações..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
    echo "Crie um arquivo .env baseado em .env.example:"
    echo "  cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env"
    echo "  nano $PROJECT_DIR/.env  # edite com suas credenciais"
    exit 1
fi

if ! grep -q "SUPABASE_URL" "$PROJECT_DIR/.env"; then
    echo -e "${RED}❌ SUPABASE_URL não configurada no .env${NC}"
    exit 1
fi

if ! grep -q "SUPABASE_ANON_KEY" "$PROJECT_DIR/.env"; then
    echo -e "${RED}❌ SUPABASE_ANON_KEY não configurada no .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configurações OK${NC}\n"

# Step 2: Instalar/Atualizar dependências
echo -e "${YELLOW}[2/5]${NC} Instalando dependências..."
cd "$PROJECT_DIR"
pip install --upgrade pip > /dev/null 2>&1
pip install -q -r requirements.txt
pip install -q flet-cli==0.25.2

if ! command -v flet &> /dev/null; then
    echo -e "${RED}❌ Falha ao instalar flet-cli${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependências instaladas${NC}\n"

# Se apenas teste, parar aqui
if [ "$TEST_ONLY" = true ]; then
    echo -e "${GREEN}✅ Teste concluído com sucesso!${NC}"
    echo "Pronto para fazer build. Execute: ./build_apk.sh"
    exit 0
fi

# Step 3: Verificar/Limpar build anterior
echo -e "${YELLOW}[3/5]${NC} Preparando ambiente..."
if [ "$CLEAN_BUILD" = true ] && [ -d "build" ]; then
    rm -rf build
    echo "  Limpeza de build anterior OK"
fi

echo -e "${GREEN}✅ Ambiente pronto${NC}\n"

# Step 4: Build APK
echo -e "${YELLOW}[4/5]${NC} Construindo APK..."
echo "  Nota: Este processo pode levar 5-10 minutos..."

if flet build apk --output "$OUTPUT_FILE"; then
    echo -e "${GREEN}✅ Build concluído${NC}\n"
else
    echo -e "${RED}❌ Falha no build${NC}"
    exit 1
fi

# Step 5: Verificar saída
echo -e "${YELLOW}[5/5]${NC} Finalizando..."

APK_PATH="build/outputs/$OUTPUT_FILE"
if [ -f "$APK_PATH" ]; then
    SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo -e "${GREEN}✅ APK gerado com sucesso!${NC}\n"
    echo -e "${BLUE}📦 Informações:${NC}"
    echo "  Caminho: $APK_PATH"
    echo "  Tamanho: $SIZE"
    echo ""
    echo -e "${BLUE}📱 Próximos passos:${NC}"
    echo "  1. Transferir para seu Android:"
    echo "     adb install $APK_PATH"
    echo ""
    echo "  2. Ou enviar para nuvem/email:"
    echo "     Arquivo pronto em: $(pwd)/$APK_PATH"
    echo ""
    exit 0
else
    echo -e "${RED}❌ APK não encontrado em $APK_PATH${NC}"
    exit 1
fi
