"""
GUIA DE INÍCIO RÁPIDO - GRANJA MANAGER MVP
===========================================

Bem-vindo! Este é o MVP completo e funcional da aplicação Granja Manager.
Siga os passos abaixo para começar.
"""

# PASSO 1: INSTALAR DEPENDÊNCIAS
# ==============================

print("""
PASSO 1️⃣: INSTALAR DEPENDÊNCIAS

Execute no terminal:
    pip install -r requirements.txt

Ou manualmente:
    pip install flet>=0.20.0

Isso pode levar alguns minutos na primeira vez.
""")

# PASSO 2: VERIFICAR INTEGRIDADE
# ==============================

print("""
PASSO 2️⃣: VERIFICAR INTEGRIDADE

Verifique se tudo está instalado corretamente:
    python verify.py

Você deve ver:
    ✅ VERIFICAÇÃO CONCLUÍDA COM SUCESSO!
""")

# PASSO 3: EXECUTAR TESTES (Opcional)
# ===================================

print("""
PASSO 3️⃣: EXECUTAR TESTES (Opcional mas recomendado)

Para testar o funcionamento sem a UI:
    python test.py

Você verá:
    ✅ TESTE 1: BANCO DE DADOS
    ✅ TESTE 2: SERVICES  
    ✅ TESTE 3: VALIDADORES
    ✅ TESTE 4: CRIAR PEDIDO

Todos os testes devem passar antes de executar a aplicação.
""")

# PASSO 4: EXECUTAR A APLICAÇÃO
# ==============================

print("""
PASSO 4️⃣: EXECUTAR A APLICAÇÃO

Opção A (Recomendado):
    python run.py

Opção B:
    python -m granja_manager.app

Opção C (Bash):
    bash start.sh

A aplicação abrirá em uma janela Flet!
""")

# PRIMEIROS PASSOS NA APLICAÇÃO
# =============================

print("""
PRIMEIROS PASSOS NA APLICAÇÃO
=============================

1️⃣ CONHECER O DASHBOARD
   - Abra a aplicação
   - Veja o Dashboard com métricas
   - Todas as métricas vêm do banco SQLite em tempo real

2️⃣ VER PRODUTOS PRÉ-CARREGADOS
   - Clique em "Produtos"
   - Você verá 5 produtos pré-carregados (seed)
   - Pode editar, deletar ou criar novos

3️⃣ CRIAR UM PEDIDO
   - Clique em "Pedidos"
   - Clique em "Novo pedido"
   - Informe:
     Nome cliente: "João Silva"
     Telefone: "5511987654321"
     Produto: Selecione um
     Quantidade: 2
   - Clique "Criar"
   
   O sistema:
   ✅ Verifica cliente (cria se não existir)
   ✅ Valida estoque
   ✅ Persiste no banco
   ✅ Atualiza estoque
   ✅ Atualiza dashboard

4️⃣ VERIFICAR PENDÊNCIAS
   - Clique em "Clientes"
   - Veja clientes com pagamentos pendentes
   - Clique "WhatsApp" para enviar cobrança
   - Clique "Marcar pago" para receber

5️⃣ CRIAR GASTOS
   - Clique em "Gastos"
   - Clique em "Novo gasto"
   - Informe: Descrição, Categoria, Valor
   - Clique "Salvar"
   
   O dashboard recalcula o lucro automaticamente!

6️⃣ VERIFICAR LUCRO
   - Volte ao Dashboard
   - Veja "Lucro no mês" atualizado
   - Baseado em vendas - gastos
""")

# FLUXO OBRIGATÓRIO EXPLICADO
# ============================

print("""
FLUXO OBRIGATÓRIO DE PEDIDOS (PRINCIPAL FUNCIONALIDADE)
=======================================================

Quando você cria um pedido:

1. Usuário informa:
   - Nome do cliente
   - Telefone do cliente
   - Produtos e quantidades

2. Sistema verifica cliente:
   - JÁ EXISTE?   → Usa cliente existente
   - NÃO EXISTE?  → Cria cliente automaticamente

3. Sistema valida:
   - Estoque suficiente?
   - Preços válidos?
   - Dados obrigatórios preenchidos?

4. Sistema persiste NO BANCO:
   - Cria pedido
   - Cria itens do pedido
   - Cria/atualiza cliente
   - REDUZ estoque (-quantidade)

5. Dashboard atualiza:
   - Vendas de hoje aumenta
   - Estoque do produto reduz
   - Total de clientes atualiza

ISSO TUDO ACONTECE AUTOMATICAMENTE!
Você só clica em "Criar Pedido"
""")

# ESTRUTURA DE ARQUIVOS
# ======================

print("""
ESTRUTURA DE ARQUIVOS CRIADA
=============================

granja_manager/
├── app.py                    ← App principal com UI
├── database/
│   └── connection.py         ← Conexão SQLite
│   ├── migrations.py         ← Cria tabelas automaticamente
│   ├── seed.py               ← Produtos iniciais
│   └── repositories/         ← Acesso a dados
├── models/                   ← Dataclasses
├── services/                 ← Lógica de negócio
├── utils/                    ← Validadores, formatadores
├── logs/                     ← Logs da aplicação
└── data/
    └── granja.db             ← Banco SQLite (criado automaticamente)

TOTAL: 35+ arquivos, ~6500 linhas de código profissional
""")

# BANCO DE DADOS
# ==============

print("""
BANCO DE DADOS SQLITE
=====================

Localizado em:
    granja_manager/data/granja.db

Tabelas criadas automaticamente:
  - clientes (nome, telefone, data criação)
  - produtos (nome, preço, estoque, status)
  - pedidos (cliente, data, total, status)
  - itens_pedido (produtos do pedido)
  - gastos (descrição, categoria, valor)

Todos os dados persistem no banco!
Nada fica apenas em memória.
""")

# LOGS
# ====

print("""
LOGS DA APLICAÇÃO
=================

Localizado em:
    granja_manager/logs/app.log

Registra:
  - Inicialização da aplicação
  - Criação/atualização/deleção de registros
  - Erros e exceções
  - Operações de estoque
  - Operações de banco de dados

Útil para debugar problemas!
""")

# COMANDOS ÚTEIS
# ==============

print("""
COMANDOS ÚTEIS
==============

# Verificar se tudo está OK
python verify.py

# Executar testes
python test.py

# Executar a aplicação
python run.py

# Resetar banco de dados (CUIDADO!)
python -c "from granja_manager.database import Migrations; Migrations.resetar_banco()"

# Ver relatório do dashboard via CLI
python -c "from granja_manager.services import DashboardService; import json; ds = DashboardService(); r = ds.gerar_relatorio_completo(); print(json.dumps({k:v for k,v in r.items() if k!='top_produtos'}, indent=2, default=str))"
""")

# TROUBLESHOOTING
# ===============

print("""
TROUBLESHOOTING
===============

❓ Erro: "ModuleNotFoundError: No module named 'flet'"
✅ Solução: pip install flet

❓ Erro: "ModuleNotFoundError: No module named 'granja_manager'"
✅ Solução: Certifique-se de estar no diretório correto

❓ Banco de dados não encontrado
✅ Solução: Será criado automaticamente na primeira execução

❓ Porta 8550 já em uso (Flet)
✅ Solução: Flet abrirá em outra porta automaticamente

❓ Aplicação lenta com muitos dados
✅ Solução: Banco SQLite tem índices para performance

❓ Preciso resetar os dados
✅ Solução: 
   rm granja_manager/data/granja.db
   Depois execute a aplicação novamente
""")

# PRÓXIMAS EXPANSÕES
# ==================

print("""
PRÓXIMAS EXPANSÕES (Arquitetura preparada para)
================================================

✅ Já implementado e funcionando:
   - SQLite persistence
   - Repository Pattern
   - Services Layer
   - Validações
   - Logs estruturados

🔄 Fácil de implementar (graças à arquitetura):
   - [ ] PostgreSQL (trocar apenas connection.py)
   - [ ] FastAPI (services reutilizáveis)
   - [ ] Autenticação de usuários
   - [ ] Relatórios em PDF
   - [ ] Export em Excel
   - [ ] Gráficos avançados
   - [ ] Backup automático
   - [ ] API REST

🚀 Futuros (estrutura preparada):
   - [ ] App mobile (Flet mobile ou React Native)
   - [ ] Cloud deployment
   - [ ] Multiusuário
   - [ ] Sincronização em tempo real
""")

# PRÓXIMOS PASSOS
# ===============

print("""
🎯 PRÓXIMOS PASSOS
==================

1. Instale as dependências:
   pip install -r requirements.txt

2. Verifique integridade:
   python verify.py

3. Execute os testes (opcional):
   python test.py

4. Inicie a aplicação:
   python run.py

5. Teste o fluxo obrigatório:
   - Crie um pedido novo
   - Veja cliente ser criado automaticamente
   - Veja estoque reduzir
   - Veja dashboard atualizar

6. Explore todas as funcionalidades:
   - Edite produtos
   - Crie gastos
   - Veja pendências de clientes
   - Envie mensagens WhatsApp

Aproveite! 🐔
""")

# SUPORTE
# =======

print("""
SUPORTE
=======

Documentação completa em:
  - README.md (instruções de uso)
  - SUMARIO.md (resumo técnico)
  - Código comentado em granja_manager/

Logs detalhados em:
  - granja_manager/logs/app.log

Código-fonte está bem estruturado:
  - Fácil de entender
  - Bem documentado
  - Segue PEP 8 (style guide Python)
  - Type hints em tudo
  - Docstrings em classes/métodos
""")

# CONCLUSÃO
# =========

print("""
═══════════════════════════════════════════════════════════════
✅ PARABÉNS! Você tem um MVP COMPLETO e FUNCIONAL de Granja Manager
═══════════════════════════════════════════════════════════════

Desenvolvido com:
✅ Persistência real em SQLite
✅ Fluxo obrigatório de pedidos
✅ Clientes automáticos
✅ Controle financeiro completo
✅ Dashboard com dados reais
✅ UI Flet mantida intacta
✅ Arquitetura profissional
✅ Código bem documentado

Comece agora:
  python run.py

Aproveite! 🐔
═══════════════════════════════════════════════════════════════
""")
