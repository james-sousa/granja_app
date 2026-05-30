#!/usr/bin/env python3
"""
Script para executar a aplicação Granja Manager

Uso:
    python run.py          # Executa a aplicação
"""

import sys
import os

# Adiciona o diretório do projeto ao path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    from granja_manager.app import main
    import flet as ft
    
    try:
        ft.app(target=main)
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário")
    except Exception as e:
        print(f"Erro ao executar a aplicação: {e}")
        sys.exit(1)
