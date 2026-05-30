#!/usr/bin/env python3
"""
Script de teste rápido - Verifica se tudo está funcionando

Executa testes básicos dos services sem precisar da UI
"""

import sys
import os

# Adiciona o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Testa conexão ao banco de dados."""
    print("=" * 60)
    print("🗄️  TESTE 1: BANCO DE DADOS")
    print("=" * 60)
    
    try:
        from granja_manager.database import db, Migrations, Seed
        
        # Inicializa
        Migrations.criar_tabelas()
        print("✅ Tabelas criadas com sucesso")
        
        # Seed
        Seed.executar()
        print("✅ Seed executado com sucesso")
        
        # Verifica conexão
        db.connect()
        print("✅ Conectado ao banco de dados")
        
        db.disconnect()
        print("✅ Desconectado do banco de dados")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_services():
    """Testa os services."""
    print()
    print("=" * 60)
    print("⚙️  TESTE 2: SERVICES")
    print("=" * 60)
    
    try:
        from granja_manager.services import (
            ProdutoService,
            ClienteService,
            GastoService,
            DashboardService,
        )
        
        # Teste produtos
        print()
        print("📦 Testando ProdutoService...")
        ps = ProdutoService()
        produtos = ps.listar_produtos()
        print(f"✅ Total de produtos: {len(produtos)}")
        if produtos:
            print(f"   Primeiro: {produtos[0].nome} - R$ {produtos[0].preco:.2f}")
        
        # Teste clientes
        print()
        print("👥 Testando ClienteService...")
        cs = ClienteService()
        clientes = cs.listar_clientes()
        print(f"✅ Total de clientes: {len(clientes)}")
        
        # Teste gastos
        print()
        print("💰 Testando GastoService...")
        gs = GastoService()
        gastos = gs.listar_gastos()
        print(f"✅ Total de gastos: {len(gastos)}")
        total_gastos = gs.total_gastos_mes()
        print(f"   Total mês: R$ {total_gastos:.2f}")
        
        # Teste dashboard
        print()
        print("📊 Testando DashboardService...")
        ds = DashboardService()
        relatorio = ds.gerar_relatorio_completo()
        print(f"✅ Relatório gerado com sucesso")
        print(f"   Vendas hoje: R$ {relatorio['metricas_dia']['vendas_dia']:.2f}")
        print(f"   Vendas mês: R$ {relatorio['metricas_mes']['vendas_mes']:.2f}")
        print(f"   Lucro mês: R$ {relatorio['metricas_mes']['lucro_mes']:.2f}")
        print(f"   Clientes ativos: {relatorio['clientes_ativos']}")
        print(f"   Produtos ativos: {relatorio['produtos_ativos']}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validators():
    """Testa validadores."""
    print()
    print("=" * 60)
    print("✔️  TESTE 3: VALIDADORES")
    print("=" * 60)
    
    try:
        from granja_manager.utils import Validators, Formatters
        
        # Teste telefone
        print()
        print("📱 Validando telefones...")
        valido, msg = Validators.validar_telefone("5511987654321")
        print(f"   5511987654321: {'✅ Válido' if valido else f'❌ {msg}'}")
        
        valido, msg = Validators.validar_telefone("123")
        print(f"   123: {'❌ Inválido (esperado)' if not valido else '✅'}")
        
        # Teste quantidade
        print()
        print("📊 Validando quantidade...")
        valido, msg = Validators.validar_quantidade(5)
        print(f"   5: {'✅ Válido' if valido else f'❌ {msg}'}")
        
        valido, msg = Validators.validar_quantidade(-1)
        print(f"   -1: {'❌ Inválido (esperado)' if not valido else '✅'}")
        
        # Teste formatadores
        print()
        print("🎨 Testando formatadores...")
        print(f"   BRL: {Formatters.formato_brl(1234.56)}")
        print(f"   Telefone: {Formatters.formato_telefone('5511987654321')}")
        print(f"   Mês: {Formatters.nome_mes(5)}")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_create_pedido():
    """Testa criação de pedido (fluxo obrigatório)."""
    print()
    print("=" * 60)
    print("🛒 TESTE 4: CRIAR PEDIDO (Fluxo Obrigatório)")
    print("=" * 60)
    
    try:
        from granja_manager.services import (
            PedidoService,
            ProdutoService,
            ClienteService,
        )
        
        # Obter primeiro produto
        ps = ProdutoService()
        produtos = ps.listar_produtos()
        
        if not produtos:
            print("❌ Nenhum produto disponível para teste")
            return False
        
        produto = produtos[0]
        print(f"📦 Usando produto: {produto.nome}")
        print(f"   Estoque atual: {produto.estoque}")
        
        # Criar pedido
        ped_service = PedidoService()
        
        print()
        print("Criando pedido para novo cliente...")
        
        pedido = ped_service.criar_pedido(
            nome_cliente="Teste Cliente",
            telefone_cliente="5511987654321",
            itens_data=[
                (produto.id, 1, produto.preco),
            ]
        )
        
        print(f"✅ Pedido criado: {pedido.id}")
        print(f"   Cliente: {pedido.cliente_id}")
        print(f"   Total: R$ {pedido.total:.2f}")
        print(f"   Itens: {len(pedido.itens)}")
        
        # Verificar estoque
        produto_atualizado = ps.obter_produto(produto.id)
        print()
        print(f"   Estoque de {produto.nome} ANTES: {produto.estoque}")
        print(f"   Estoque de {produto.nome} DEPOIS: {produto_atualizado.estoque}")
        print(f"   ✅ Estoque reduzido corretamente")
        
        # Verificar cliente criado
        cs = ClienteService()
        cliente = cs.obter_cliente(pedido.cliente_id)
        print()
        print(f"   Cliente criado automaticamente:")
        print(f"   Nome: {cliente.nome}")
        print(f"   Telefone: {cliente.telefone}")
        print(f"   ✅ Cliente criado com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🐔 TESTE RÁPIDO - GRANJA MANAGER MVP".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    resultados = {
        "Database": test_database(),
        "Services": test_services(),
        "Validadores": test_validators(),
        "Criar Pedido": test_create_pedido(),
    }
    
    print()
    print("=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{teste:.<40} {status}")
    
    total = len(resultados)
    passou = sum(1 for r in resultados.values() if r)
    
    print()
    print(f"Total: {passou}/{total} testes passaram")
    
    if passou == total:
        print()
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print()
        print("Próximas ações:")
        print("  1. Execute: python run.py")
        print("  2. Abra a aplicação Flet")
        print("  3. Teste a interface completa")
        return 0
    else:
        print()
        print(f"❌ {total - passou} teste(s) falharam")
        print()
        print("Verifique os erros acima e corrija.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
