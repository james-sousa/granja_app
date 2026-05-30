"""README - Granja Manager MVP

## 🐔 Granja Manager - Sistema de Gestão Completo

MVP funcional com persistência real em SQLite, desenvolvido com Flet.

### 📋 Características Implementadas

#### ✅ Persistência de Dados
- Banco SQLite com migrações automáticas
- Tabelas: clientes, produtos, pedidos, itens_pedido, gastos
- Índices para performance
- Transações e rollback

#### ✅ Gestão de Clientes
- Criação AUTOMÁTICA ao realizar pedidos
- NUNCA cadastro manual
- Histórico de compras
- Pendências de pagamento
- Filtros por nome/telefone

#### ✅ Gestão de Produtos
- CRUD completo
- Controle de estoque
- Alertas de estoque baixo
- Busca e filtros

#### ✅ Gestão de Pedidos
- Fluxo obrigatório:
  1. Criar pedido
  2. Verificar/criar cliente
  3. Validar estoque
  4. Atualizar BD
  5. Atualizar estoque
  6. Atualizar dashboard
- Múltiplos itens por pedido
- Cálculo automático de totais
- Estados: pendente, pago, concluído
- Restauração de estoque ao deletar

#### ✅ Controle Financeiro
- Vendas do dia e do mês
- Gastos por categoria
- Lucro/prejuízo
- Valor pendente de recebimento
- Previsão de caixa

#### ✅ Gastos/Despesas
- CRUD completo
- Categorias pré-definidas
- Filtros por data e categoria
- Total acumulado

#### ✅ Dashboard Real
- Métricas em tempo real (banco SQLite)
- Vendas de hoje
- Pedidos de hoje
- Clientes ativos
- Top produtos mais vendidos
- Lucro do mês
- Gráficos (preparados para expansão)

#### ✅ WhatsApp Integration
- Mensagens de cobrança
- Link direto para WhatsApp Web
- Mensagem pré-formatada

#### ✅ Arquitetura Profissional
- Repository Pattern
- Services Layer
- Models (Dataclasses)
- Validadores e Formatadores
- Logging estruturado
- Tratamento de exceções
- Tipagem forte

### 📂 Estrutura do Projeto

```
granja_manager/
├── app.py                    # Aplicação principal com UI
├── __init__.py              # Package init
├── config.py                # Configurações globais
├── database/
│   ├── connection.py        # Conexão SQLite
│   ├── migrations.py        # Criação de tabelas
│   ├── seed.py              # Dados iniciais
│   └── repositories/
│       ├── base.py          # Classe abstrata
│       ├── cliente_repository.py
│       ├── produto_repository.py
│       ├── pedido_repository.py
│       ├── item_repository.py
│       └── gasto_repository.py
├── models/
│   ├── cliente.py
│   ├── produto.py
│   ├── pedido.py
│   ├── item_pedido.py
│   └── gasto.py
├── services/
│   ├── cliente_service.py     # Lógica de clientes
│   ├── produto_service.py     # Lógica de produtos
│   ├── pedido_service.py      # Lógica de pedidos (fluxo obrigatório)
│   ├── estoque_service.py     # Lógica de estoque
│   ├── gasto_service.py       # Lógica de gastos
│   ├── dashboard_service.py   # Métricas e dashboard
│   └── financeiro_service.py  # Controle financeiro
├── utils/
│   ├── validators.py         # Validadores
│   ├── formatters.py         # Formatadores (BRL, telefone, data)
│   └── helpers.py            # Helpers e logging
├── logs/
│   └── app.log              # Logs da aplicação
└── data/
    └── granja.db            # Banco SQLite (criado automaticamente)
```

### 🚀 Como Executar

#### Pré-requisitos
```bash
pip install flet
```

#### Executar a Aplicação
```bash
# Opção 1: Via script run.py
python run.py

# Opção 2: Via módulo direto
python -m granja_manager.app

# Opção 3: Direto no Flet
flet run granja_manager/app.py
```

### 📊 Fluxo Obrigatório de Pedidos

```
Usuario cria pedido
        ↓
Inforna nome e telefone
        ↓
Sistema verifica cliente
        ├─ Existe? → Usa cliente existente
        └─ Não existe? → Cria cliente automaticamente
        ↓
Sistema valida estoque
        ├─ OK? → Continua
        └─ Insuficiente? → Erro
        ↓
Sistema calcula total
        ↓
Sistema persiste no BD
        ├─ Pedido
        ├─ Itens
        ├─ Cliente (se novo)
        └─ Estoque (-quantidade)
        ↓
Dashboard atualiza automaticamente
```

### 💾 Banco de Dados

#### Tabelas Criadas Automaticamente

**clientes**
```sql
id (UUID PK)
nome (TEXT NOT NULL)
telefone (TEXT)
criado_em (TIMESTAMP)
```

**produtos**
```sql
id (UUID PK)
nome (TEXT NOT NULL)
preco (REAL NOT NULL)
estoque (INTEGER)
ativo (INTEGER)
criado_em (TIMESTAMP)
```

**pedidos**
```sql
id (UUID PK)
cliente_id (FK)
data (TIMESTAMP)
total (REAL)
pago (INTEGER: 0=não, 1=sim)
concluido (INTEGER: 0=pendente, 1=concluído)
```

**itens_pedido**
```sql
id (UUID PK)
pedido_id (FK)
produto_id (FK)
quantidade (INTEGER)
preco_unitario (REAL)
```

**gastos**
```sql
id (UUID PK)
descricao (TEXT)
categoria (TEXT)
valor (REAL)
data (TIMESTAMP)
```

### 🔧 Exemplos de Uso

#### Criar Pedido (Fluxo Obrigatório)
```python
pedido_service = PedidoService()

# Cliente é criado automaticamente se não existir
pedido = pedido_service.criar_pedido(
    nome_cliente="João Silva",
    telefone_cliente="5511987654321",
    itens_data=[
        ("produto_id_1", 2, 18.00),  # (id_produto, qtd, preco)
        ("produto_id_2", 1, 22.00),
    ]
)
# Resultado:
# 1. Cliente verificado/criado
# 2. Estoque validado
# 3. Pedido criado
# 4. Estoque atualizado
# 5. Dashboard atualizado
```

#### Criar Produto
```python
produto_service = ProdutoService()

produto = produto_service.criar_produto(
    nome="Dúzia de Ovos Caipira",
    preco=18.00,
    estoque=120
)
```

#### Criar Gasto
```python
gasto_service = GastoService()

gasto = gasto_service.criar_gasto(
    descricao="Ração para galinhas",
    categoria="Insumos",
    valor=320.00
)
```

#### Obter Métricas Dashboard
```python
dashboard_service = DashboardService()

relatorio = dashboard_service.gerar_relatorio_completo()
print(f"Vendas do dia: {relatorio['metricas_dia']['vendas_dia']}")
print(f"Lucro do mês: {relatorio['metricas_mes']['lucro_mes']}")
```

### 🎨 UI/UX Mantidos

- ✅ Sidebar com navegação (200px largura fixa)
- ✅ Logo e footer
- ✅ 5 seções: Dashboard, Clientes, Produtos, Pedidos, Gastos
- ✅ Paleta de cores original
- ✅ Cards, badges, botões
- ✅ Responsividade
- ✅ SnackBars para feedback
- ✅ AlertDialogs para confirmação

### 📝 Validações Implementadas

- ✅ Telefone: 10-13 dígitos
- ✅ Quantidade: > 0
- ✅ Preço: >= 0
- ✅ Estoque: >= 0
- ✅ Nome obrigatório (min 3 caracteres)
- ✅ Descrição obrigatória
- ✅ Campos obrigatórios

### 📊 Formatadores Disponíveis

```python
from granja_manager.utils import Formatters

Formatters.formato_brl(1234.56)           # "R$ 1.234,56"
Formatters.formato_telefone("5511987654321")  # "(11) 98765-4321"
Formatters.formato_data(datetime.now())   # "18/05/2026"
Formatters.nome_mes(5)                     # "Maio"
```

### 🎯 Próximas Expansões (Arquitetura Preparada)

- [ ] PostgreSQL (já preparado com interfaces)
- [ ] FastAPI (services reutilizáveis)
- [ ] Multiusuário e login
- [ ] PDF de pedidos e relatórios
- [ ] Excel export
- [ ] Gráficos avançados
- [ ] API REST
- [ ] Mobile app

### 📜 Logs

Logs são salvos em `granja_manager/logs/app.log` e exibidos no console.

Registra:
- Inicialização do app
- Criação/atualização/deleção de registros
- Erros e exceções
- Operações de estoque
- Operações de banco de dados

### 🆘 Troubleshooting

**Erro: "ModuleNotFoundError: No module named 'flet'"**
```bash
pip install flet
```

**Erro: "ModuleNotFoundError: No module named 'granja_manager'"**
```bash
# Certifique-se de estar no diretório correto
cd /caminho/para/projeto
python run.py
```

**Banco de dados não encontrado**
- O banco é criado automaticamente na primeira execução
- Localizado em `granja_manager/data/granja.db`

### 📄 Licença

MVP desenvolvido para Granja Manager

### 👨‍💻 Suporte

Para reportar bugs ou solicitar features, verifique os logs em `granja_manager/logs/app.log`
"""

