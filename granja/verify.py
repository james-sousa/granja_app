#!/usr/bin/env python3
"""
Script de verificação de integridade da instalação Granja Manager
Verifica se todos os arquivos e dependências estão presentes
"""

import os
import sys
import importlib.util

def check_file(path, description):
    """Verifica se um arquivo existe."""
    exists = os.path.isfile(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_dir(path, description):
    """Verifica se um diretório existe."""
    exists = os.path.isdir(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_import(module_name, description):
    """Verifica se um módulo pode ser importado."""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError:
        print(f"❌ {description}: {module_name} não instalado")
        return False

def main():
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE INTEGRIDADE - GRANJA MANAGER")
    print("=" * 60)
    print()
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    all_good = True
    
    # 1. Verificar diretórios
    print("📁 DIRETÓRIOS")
    print("-" * 60)
    dirs_to_check = [
        ("granja_manager/database", "Camada de banco de dados"),
        ("granja_manager/database/repositories", "Repositórios"),
        ("granja_manager/models", "Modelos"),
        ("granja_manager/services", "Serviços"),
        ("granja_manager/utils", "Utilitários"),
        ("granja_manager/logs", "Logs"),
        ("granja_manager/data", "Dados (SQLite)"),
    ]
    
    for dir_path, desc in dirs_to_check:
        full_path = os.path.join(base_path, dir_path)
        all_good &= check_dir(full_path, desc)
    print()
    
    # 2. Verificar arquivos principais
    print("📄 ARQUIVOS PRINCIPAIS")
    print("-" * 60)
    files_to_check = [
        ("granja_manager/app.py", "App principal"),
        ("granja_manager/__init__.py", "Package init"),
        ("granja_manager/config.py", "Configurações"),
        ("run.py", "Script de execução"),
        ("README.md", "Documentação"),
        ("requirements.txt", "Dependências"),
    ]
    
    for file_path, desc in files_to_check:
        full_path = os.path.join(base_path, file_path)
        all_good &= check_file(full_path, desc)
    print()
    
    # 3. Verificar módulos granja_manager
    print("🐍 MÓDULOS GRANJA MANAGER")
    print("-" * 60)
    modules_to_check = [
        ("granja_manager.database", "Database module"),
        ("granja_manager.models", "Models module"),
        ("granja_manager.services", "Services module"),
        ("granja_manager.utils", "Utils module"),
    ]
    
    for module, desc in modules_to_check:
        # Tenta encontrar o módulo no path
        try:
            spec = importlib.util.find_spec(module)
            if spec:
                print(f"✅ {desc}: {module}")
            else:
                print(f"❌ {desc}: {module} não encontrado")
                all_good = False
        except (ImportError, ModuleNotFoundError):
            print(f"❌ {desc}: {module} não encontrado")
            all_good = False
    print()
    
    # 4. Verificar dependências externas
    print("📦 DEPENDÊNCIAS EXTERNAS")
    print("-" * 60)
    external_deps = [
        ("flet", "Flet (UI framework)"),
    ]
    
    for module, desc in external_deps:
        all_good &= check_import(module, desc)
    print()
    
    # 5. Verificar banco de dados
    print("💾 BANCO DE DADOS")
    print("-" * 60)
    db_path = os.path.join(base_path, "granja_manager/data/granja.db")
    if os.path.isfile(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ Banco de dados existente ({size} bytes): {db_path}")
    else:
        print(f"⚠️  Banco de dados ainda não criado (será criado na primeira execução)")
        print(f"   Caminho: {db_path}")
    print()
    
    # 6. Verificar logs
    print("📋 LOGS")
    print("-" * 60)
    log_path = os.path.join(base_path, "granja_manager/logs/app.log")
    if os.path.isfile(log_path):
        print(f"✅ Log file encontrado: {log_path}")
    else:
        print(f"⚠️  Log file ainda não criado (será criado na primeira execução)")
        print(f"   Caminho: {log_path}")
    print()
    
    # 7. Resumo final
    print("=" * 60)
    if all_good:
        print("✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Para executar a aplicação:")
        print("  python run.py")
        print()
        print("Ou:")
        print("  python3 -m granja_manager.app")
        return 0
    else:
        print("❌ VERIFICAÇÃO ENCONTROU PROBLEMAS")
        print()
        print("Instale as dependências:")
        print("  pip install -r requirements.txt")
        print()
        print("Ou execute o arquivo requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
