#!/usr/bin/env python3
"""
Script de Configuração Inicial do Supabase
Executa as migrações e dados iniciais automaticamente
"""

import os
import sys
from pathlib import Path

def check_env():
    """Verifica se arquivo .env existe e está preenchido."""
    print("\n" + "="*60)
    print("🔍 Verificando configuração do Supabase...")
    print("="*60)
    
    if not Path(".env").exists():
        print("❌ Arquivo .env não encontrado!")
        print("\nCrie o arquivo .env com:")
        print("  SUPABASE_URL=sua_url")
        print("  SUPABASE_KEY=sua_chave")
        print("\nOu copie de .env.example:")
        print("  cp .env.example .env")
        return False
    
    # Carrega ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Variáveis SUPABASE_URL ou SUPABASE_KEY não preenchidas!")
        print("\nEdite .env e preencha as credenciais do Supabase")
        return False
    
    print(f"✅ SUPABASE_URL: {url[:30]}...")
    print(f"✅ SUPABASE_KEY: {key[:20]}...")
    return True

def test_connection():
    """Testa conexão com Supabase."""
    print("\n" + "="*60)
    print("🔗 Testando conexão com Supabase...")
    print("="*60)
    
    try:
        from supabase import create_client
        from dotenv import load_dotenv
        load_dotenv()
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        client = create_client(url, key)
        
        # Tenta listar tabelas
        result = client.table("produtos").select("id").limit(1).execute()
        print("✅ Conectado com sucesso ao Supabase!")
        return client
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("\nDica: Verifique se:")
        print("  1. URL e KEY estão corretas")
        print("  2. As tabelas foram criadas no SQL Editor")
        print("  3. Sua internet está funcionando")
        return None

def create_initial_data(client):
    """Cria dados iniciais."""
    print("\n" + "="*60)
    print("📦 Criando dados iniciais...")
    print("="*60)
    
    try:
        # Verifica se já existem produtos
        existing = client.table("produtos").select("id").execute()
        if existing.data and len(existing.data) > 0:
            print("ℹ️  Produtos já existem no banco. Pulando...")
            return True
        
        # Cria produtos iniciais
        produtos = [
            {"id": "prod-001", "nome": "Ração Premium", "preco": 45.50, "estoque": 100, "ativo": 1},
            {"id": "prod-002", "nome": "Vitaminas para Aves", "preco": 120.00, "estoque": 50, "ativo": 1},
            {"id": "prod-003", "nome": "Medicamento Geral", "preco": 75.99, "estoque": 30, "ativo": 1},
            {"id": "prod-004", "nome": "Grão Misto", "preco": 38.50, "estoque": 150, "ativo": 1},
            {"id": "prod-005", "nome": "Suplemento Calcário", "preco": 25.00, "estoque": 80, "ativo": 1},
        ]
        
        for prod in produtos:
            result = client.table("produtos").insert(prod).execute()
            print(f"  ✅ {prod['nome']}")
        
        print(f"\n✅ {len(produtos)} produtos criados com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        return False

def main():
    """Executa o setup completo."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🚀 SETUP INICIAL - GRANJA MANAGER COM SUPABASE 🚀       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Step 1: Verificar .env
    if not check_env():
        sys.exit(1)
    
    # Step 2: Testar conexão
    client = test_connection()
    if not client:
        print("\n❌ Não foi possível conectar ao Supabase")
        print("\nVerifique o arquivo SUPABASE_SETUP.md para instruções completas")
        sys.exit(1)
    
    # Step 3: Criar dados iniciais
    if not create_initial_data(client):
        print("\n⚠️  Alguns dados não puderam ser criados")
        print("(Mas a conexão funciona, então você pode usar a app normalmente)")
    
    # Sucesso!
    print("\n" + "="*60)
    print("✅ SETUP CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\nAgora você pode executar:")
    print("  python run.py")
    print("\nOu:")
    print("  flet run run.py")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
