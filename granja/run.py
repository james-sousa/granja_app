#!/usr/bin/env python3
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    from granja_manager.app import main
    import flet as ft
    
    try:
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 8550))
        )
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário")
    except Exception as e:
        print(f"Erro ao executar a aplicação: {e}")
        sys.exit(1)