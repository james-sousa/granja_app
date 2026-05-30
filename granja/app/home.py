"""
Dashboard - Granja Manager
Convertido de React para Python Flet
Com sidebar lateral de navegação
Para executar:
    pip install flet
    flet run dashboard.py
"""
import flet as ft
import urllib.parse
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Callable, Optional
@dataclass
class ItemPedido:
    produto_id: str
    quantidade: int
    preco_unitario: float
@dataclass
class Pedido:
    id: str
    cliente_id: str
    cliente_nome: str
    data: datetime
    itens: List[ItemPedido]
    pago: bool = False
    concluido: bool = False
    @property
    def total(self) -> float:
        return sum(i.quantidade * i.preco_unitario for i in self.itens)
@dataclass
class Cliente:
    id: str
    nome: str
    telefone: str
@dataclass
class Produto:
    id: str
    nome: str
    preco: float
    estoque: int = 0
@dataclass
class Gasto:
    id: str
    descricao: str
    valor: float
    data: datetime
    categoria: str = "Outros"
class GranjaStore:
    def __init__(self):
        agora = datetime.now()
        self.clientes: List[Cliente] = [
            Cliente("c1", "Ana Oliveira",   "5511987654321"),
            Cliente("c2", "Joao Santos",    "5511912345678"),
            Cliente("c3", "Maria Silva",    "5511998765432"),
            Cliente("c4", "Carlos Lima",    "5511955443322"),
            Cliente("c5", "Beatriz Ramos",  "5511966778899"),
        ]
        self.produtos: List[Produto] = [
            Produto("p1", "Dúzia de Ovos Caipira",  18.00, estoque=120),
            Produto("p2", "Dúzia de Ovos Brancos",  12.50, estoque=200),
            Produto("p3", "Frango Inteiro (kg)",    22.00, estoque=35),
            Produto("p4", "Filé de Frango (kg)",    28.00, estoque=20),
            Produto("p5", "Coxa de Frango (kg)",    18.50, estoque=40),
        ]
        self.pedidos: List[Pedido] = [
            Pedido("o1", "c3", "Maria Silva", agora,
                   [ItemPedido("p1", 2, 18.00), ItemPedido("p3", 1, 22.00)],
                   pago=True, concluido=True),
            Pedido("o2", "c2", "João Santos", agora,
                   [ItemPedido("p2", 5, 12.50)],
                   pago=False, concluido=False),
            Pedido("o3", "c1", "Ana Oliveira", agora,
                   [ItemPedido("p4", 2, 28.00), ItemPedido("p1", 1, 18.00)],
                   pago=False, concluido=True),
        ]
        self.gastos: List[Gasto] = [
            Gasto("g1", "Ração",        320.00, agora, "Insumos"),
            Gasto("g2", "Conta de luz", 180.00, agora, "Contas"),
        ]
    def get_cliente(self, cliente_id: str) -> Optional[Cliente]:
        return next((c for c in self.clientes if c.id == cliente_id), None)
    def pedidos_pendentes_por_cliente(self) -> List[dict]:
        grupos: dict = {}
        for p in self.pedidos:
            if not p.pago:
                if p.cliente_id not in grupos:
                    cliente = self.get_cliente(p.cliente_id)
                    grupos[p.cliente_id] = {
                        "cliente": cliente,
                        "pedidos": [],
                        "total_pendente": 0.0,
                    }
                grupos[p.cliente_id]["pedidos"].append(p)
                grupos[p.cliente_id]["total_pendente"] += p.total
        return list(grupos.values())
    def marcar_cliente_pago(self, cliente_id: str):
        for p in self.pedidos:
            if p.cliente_id == cliente_id and not p.pago:
                p.pago = True
    def marcar_pedido_pago(self, pedido_id: str):
        for p in self.pedidos:
            if p.id == pedido_id:
                p.pago = True
                break
    def marcar_pedido_nao_pago(self, pedido_id: str):
        for p in self.pedidos:
            if p.id == pedido_id:
                p.pago = False
                break
    def concluir_pedido(self, pedido_id: str):
        for p in self.pedidos:
            if p.id == pedido_id:
                p.concluido = True
                break
    def reabrir_pedido(self, pedido_id: str):
        for p in self.pedidos:
            if p.id == pedido_id:
                p.concluido = False
                break
    def remover_pedido(self, pedido_id: str):
        self.pedidos = [p for p in self.pedidos if p.id != pedido_id]
    def remover_produto(self, produto_id: str):
        self.produtos = [p for p in self.produtos if p.id != produto_id]
    def adicionar_produto(self, nome: str, preco: float, estoque: int):
        novo_id = "p" + str(uuid.uuid4())[:6]
        self.produtos.append(Produto(novo_id, nome, preco, estoque))
    def editar_produto(self, produto_id: str, nome: str, preco: float, estoque: int):
        for p in self.produtos:
            if p.id == produto_id:
                p.nome    = nome
                p.preco   = preco
                p.estoque = estoque
                break
    def remover_gasto(self, gasto_id: str):
        self.gastos = [g for g in self.gastos if g.id != gasto_id]
    def adicionar_gasto(self, descricao: str, valor: float, categoria: str):
        novo_id = "g" + str(uuid.uuid4())[:6]
        self.gastos.append(Gasto(novo_id, descricao, valor, datetime.now(), categoria))
    def calcular_stats(self) -> dict:
        agora     = datetime.now()
        mes_atual = agora.month
        ano_atual = agora.year
        hoje_str  = agora.strftime("%Y-%m-%d")
        pedidos_hoje = [p for p in self.pedidos
                        if p.data.strftime("%Y-%m-%d") == hoje_str and p.pago]
        total_vendas = sum(p.total for p in pedidos_hoje)
        qtd_pedidos  = len(pedidos_hoje)
        pedidos_mes = [p for p in self.pedidos
                       if p.data.month == mes_atual and p.data.year == ano_atual and p.pago]
        vendas_mes  = sum(p.total for p in pedidos_mes)
        gastos_mes  = sum(g.valor for g in self.gastos
                          if g.data.month == mes_atual and g.data.year == ano_atual)
        lucro_mes   = vendas_mes - gastos_mes
        ranking: dict = {}
        for p in self.pedidos:
            for i in p.itens:
                ranking[i.produto_id] = ranking.get(i.produto_id, 0) + i.quantidade
        top_ids = sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:5]
        top_produtos = []
        for pid, qtd in top_ids:
            prod = next((pr for pr in self.produtos if pr.id == pid), None)
            if prod:
                top_produtos.append((prod, qtd))
        clientes_ativos = len(
            set(p.cliente_nome.strip().lower() for p in self.pedidos if p.cliente_nome.strip())
        )
        return {
            "total_vendas":    total_vendas,
            "qtd_pedidos":     qtd_pedidos,
            "vendas_mes":      vendas_mes,
            "gastos_mes":      gastos_mes,
            "lucro_mes":       lucro_mes,
            "top_produtos":    top_produtos,
            "clientes_ativos": clientes_ativos,
            "num_produtos":    len(self.produtos),
        }
def format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def mes_nome() -> str:
    meses = ["janeiro","fevereiro","março","abril","maio","junho",
              "julho","agosto","setembro","outubro","novembro","dezembro"]
    return meses[datetime.now().month - 1]
C = {
    "bg":               "#f0faf4",
    "sidebar":          "#1a5c30",
    "surface":          "#ffffff",
    "border":           "#e2e8f0",
    "text":             "#1a1a1a",
    "text_label":       "#6b7280",
    "muted":            "#9ca3af",
    "success":          "#16a34a",
    "success_bg":       "#dcfce7",
    "warning":          "#d97706",
    "warning_bg":       "#fef3c7",
    "danger":           "#dc2626",
    "danger_bg":        "#fee2e2",
    "sidebar_text":     "#ffffff",
    "sidebar_muted":    "#a7f3d0",
    "sidebar_active_bg":"#16a34a",
    "rank_bg":          "#16a34a",
    "rank_text":        "#ffffff",
    "qty_text":         "#16a34a",
    "white":            "#ffffff",
    "transparent":      ft.Colors.TRANSPARENT,
    "wa_green":         "#25D366",
    "wa_bg":            "#e9faf0",
}
SIDEBAR_W = 220
NAV_ITEMS = [
    ("dashboard",          "Dashboard",  ft.icons.Icons.DASHBOARD),
    ("clientes_pendentes", "Clientes",   ft.icons.Icons.PEOPLE_ALT),
    ("produtos",           "Produtos",   ft.icons.Icons.INVENTORY_2),
    ("pedidos",            "Pedidos",    ft.icons.Icons.SHOPPING_CART),
    ("gastos",             "Gastos",     ft.icons.Icons.RECEIPT_LONG),
]
def build_sidebar(current_route: str, on_navigate: Callable) -> ft.Container:
    def nav_item(route, label, icon):
        active = route == current_route
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=18,
                            color=C["sidebar_text"] if active else C["sidebar_muted"]),
                    ft.Text(label, size=13,
                            weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                            color=C["sidebar_text"] if active else C["sidebar_muted"]),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, top=11, right=16, bottom=11),
            border_radius=10,
            bgcolor=C["sidebar_active_bg"] if active else C["transparent"],
            on_click=lambda e, r=route: on_navigate(r),
            ink=not active,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )
    logo = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("GR", size=18, weight=ft.FontWeight.BOLD, color=C["white"]),
                    width=40, height=40, border_radius=10, bgcolor=C["rank_bg"],
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text("Granja", size=15, weight=ft.FontWeight.BOLD, color=C["white"]),
                        ft.Text("Manager", size=11, color=C["sidebar_muted"]),
                    ],
                    spacing=0, tight=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, top=24, right=16, bottom=24),
    )
    footer = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("AD", size=11, weight=ft.FontWeight.BOLD, color=C["white"]),
                    width=32, height=32, border_radius=16, bgcolor=C["rank_bg"],
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text("Admin", size=12, color=C["sidebar_text"], weight=ft.FontWeight.W_500),
                        ft.Text("Gerente", size=10, color=C["sidebar_muted"]),
                    ],
                    spacing=0, tight=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, top=16, right=16, bottom=16),
        border=ft.Border(top=ft.BorderSide(1, "#2d7a4a")),
    )
    return ft.Container(
        content=ft.Column(
            controls=[
                logo,
                ft.Container(ft.Divider(height=1, color="#2d7a4a"),
                             padding=ft.Padding(left=0, top=0, right=0, bottom=10)),
                ft.Container(
                    content=ft.Text("MENU", size=10, color=C["sidebar_muted"],
                                    weight=ft.FontWeight.W_600),
                    padding=ft.Padding(left=16, top=0, right=0, bottom=8),
                ),
                ft.Column(
                    controls=[nav_item(r, l, i) for r, l, i in NAV_ITEMS],
                    spacing=4,
                ),
                ft.Container(expand=True),
                footer,
            ],
            spacing=0, expand=True,
        ),
        width=SIDEBAR_W,
        bgcolor=C["sidebar"],
        border=ft.Border(right=ft.BorderSide(1, C["border"])),
    )
def _btn_primary(label: str, icon, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=16, color=C["white"]),
                ft.Text(label, size=13, color=C["white"], weight=ft.FontWeight.W_600),
            ],
            spacing=6, tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=18, top=10, right=18, bottom=10),
        border_radius=10,
        bgcolor=C["success"],
        on_click=on_click,
        ink=True,
    )
def _btn_outline(label: str, icon, on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=14, color=C["text"]),
                ft.Text(label, size=12, color=C["text"], weight=ft.FontWeight.W_500),
            ],
            spacing=5, tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=14, top=8, right=14, bottom=8),
        border_radius=8,
        border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        bgcolor=C["surface"],
        on_click=on_click,
        ink=True,
    )
def _btn_filled(label: str, icon, on_click, bgcolor=None, text_color=None) -> ft.Container:
    bg = bgcolor or C["success"]
    tc = text_color or C["white"]
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, size=14, color=tc),
                ft.Text(label, size=12, color=tc, weight=ft.FontWeight.W_600),
            ],
            spacing=5, tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=14, top=8, right=14, bottom=8),
        border_radius=8,
        bgcolor=bg,
        on_click=on_click,
        ink=True,
    )
def stat_card(label, value, icon, icon_color, icon_bg) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color=icon_color, size=22),
                    width=48, height=48, border_radius=12, bgcolor=icon_bg,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text(label, size=11, color=C["text_label"]),
                        ft.Text(str(value), size=20, weight=ft.FontWeight.BOLD, color=C["text"]),
                    ],
                    spacing=2, tight=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=18, top=18, right=18, bottom=18),
        bgcolor=C["surface"],
        border_radius=14,
        border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
    )
def resumo_tile(label, value_str, icon, icon_color, icon_bg, tile_bg, value_color) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color=icon_color, size=20),
                    width=44, height=44, border_radius=10, bgcolor=icon_bg,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text(label, size=11, color=C["text_label"]),
                        ft.Text(value_str, size=19, weight=ft.FontWeight.BOLD, color=value_color),
                    ],
                    spacing=2, tight=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, top=16, right=16, bottom=16),
        bgcolor=tile_bg,
        border_radius=14,
        expand=True,
    )
def top_produto_item(rank, produto, qtd) -> ft.Row:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(str(rank), size=13, weight=ft.FontWeight.BOLD,
                                color=C["rank_text"]),
                width=36, height=36, border_radius=18, bgcolor=C["rank_bg"],
                alignment=ft.Alignment(0, 0),
            ),
            ft.Column(
                controls=[
                    ft.Text(produto.nome, size=14, weight=ft.FontWeight.W_500, color=C["text"]),
                    ft.Text(format_brl(produto.preco), size=11, color=C["muted"]),
                ],
                spacing=1, tight=True, expand=True,
            ),
            ft.Text(f"{qtd} un.", size=13, weight=ft.FontWeight.BOLD, color=C["qty_text"]),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
def card_wrapper(title, content) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=C["text"]),
                    padding=ft.Padding(left=20, top=18, right=20, bottom=12),
                ),
                ft.Divider(height=1, color=C["border"]),
                ft.Container(content=content, padding=ft.Padding(left=20, top=20, right=20, bottom=20)),
            ],
            spacing=0, tight=True,
        ),
        bgcolor=C["surface"],
        border_radius=14,
        border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
    )
def view_dashboard(store: GranjaStore) -> ft.Control:
    Icons  = ft.icons.Icons
    stats  = store.calcular_stats()
    lucro  = stats["lucro_mes"]
    lucro_label    = "Lucro no mês" if lucro >= 0 else "Prejuízo no mês"
    lucro_color    = C["success"] if lucro >= 0 else C["danger"]
    lucro_icon_bg  = C["success_bg"] if lucro >= 0 else C["danger_bg"]
    lucro_tile_bg  = "#f0fdf4" if lucro >= 0 else "#fff1f2"
    metric_cards = [
        stat_card("Vendas de hoje",  format_brl(stats["total_vendas"]),
                  Icons.ATTACH_MONEY,  C["success"], C["success_bg"]),
        stat_card("Pedidos de hoje", stats["qtd_pedidos"],
                  Icons.SHOPPING_CART, C["success"], C["success_bg"]),
        stat_card("Clientes ativos", stats["clientes_ativos"],
                  Icons.PEOPLE,        C["success"], C["success_bg"]),
        stat_card("Produtos ativos", stats["num_produtos"],
                  Icons.TRENDING_UP,   C["warning"], C["warning_bg"]),
    ]
    cards_row = ft.ResponsiveRow(
        controls=[ft.Column([c], col={"xs": 12, "sm": 6, "lg": 3}) for c in metric_cards],
        run_spacing=16, spacing=16,
    )
    resumo_row = ft.ResponsiveRow(
        controls=[
            ft.Column([resumo_tile(
                "Vendas no mês", format_brl(stats["vendas_mes"]),
                Icons.ATTACH_MONEY, C["success"], C["success_bg"], "#f0fdf4", C["success"],
            )], col={"xs": 12, "sm": 4}, expand=True),
            ft.Column([resumo_tile(
                "Gastos no mês", format_brl(stats["gastos_mes"]),
                Icons.RECEIPT, C["danger"], C["danger_bg"], "#fff1f2", C["danger"],
            )], col={"xs": 12, "sm": 4}, expand=True),
            ft.Column([resumo_tile(
                lucro_label, format_brl(abs(lucro)),
                Icons.ACCOUNT_BALANCE_WALLET, lucro_color, lucro_icon_bg, lucro_tile_bg, lucro_color,
            )], col={"xs": 12, "sm": 4}, expand=True),
        ],
        run_spacing=12, spacing=12,
    )
    top_content = (
        ft.Text("Nenhum pedido ainda.", size=13, color=C["muted"])
        if not stats["top_produtos"]
        else ft.Column(
            controls=[top_produto_item(i + 1, p, q)
                      for i, (p, q) in enumerate(stats["top_produtos"])],
            spacing=16,
        )
    )
    return ft.Column(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Olá, bem-vindo!", size=24,
                            weight=ft.FontWeight.BOLD, color=C["text"]),
                    ft.Text("Resumo do seu dia na granja.", size=14, color=C["text_label"]),
                ],
                spacing=4,
            ),
            cards_row,
            card_wrapper(f"Resumo de {mes_nome().capitalize()}", resumo_row),
            card_wrapper("Produtos mais vendidos", top_content),
        ],
        spacing=24,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
def view_clientes_pendentes(store: GranjaStore, page: ft.Page, refresh_fn: Callable) -> ft.Control:
    Icons = ft.icons.Icons
    lista_ref = ft.Ref[ft.Column]()
    total_ref = ft.Ref[ft.Text]()
    qtd_ref   = ft.Ref[ft.Text]()
    def _whatsapp_url(telefone: str, nome: str, valor: float) -> str:
        msg = (
            f"Olá {nome}! 👋\n"
            f"Passando para lembrar que você tem um pagamento pendente "
            f"de *{format_brl(valor)}* na Granja. 🐔\n"
            f"Quando puder, por favor efetue o pagamento. Obrigado! 😊"
        )
        return f"https://web.whatsapp.com/send?phone={telefone}&text={urllib.parse.quote(msg)}"
    def _build_card(grupo: dict) -> ft.Container:
        cliente    = grupo["cliente"]
        pedidos_ab = grupo["pedidos"]
        total_dev  = grupo["total_pendente"]
        telefone   = cliente.telefone if cliente else "5500000000000"
        nome       = cliente.nome     if cliente else "Desconhecido"
        def on_marcar_pago(e, cid=cliente.id):
            store.marcar_cliente_pago(cid)
            lista_ref.current.controls = [
                c for c in lista_ref.current.controls
                if getattr(c, "data", None) != cid
            ]
            novos = store.pedidos_pendentes_por_cliente()
            total_ref.current.value = format_brl(sum(g["total_pendente"] for g in novos))
            qtd_ref.current.value   = f"{len(novos)} cliente(s) com pendência"
            if not lista_ref.current.controls:
                lista_ref.current.controls = [_empty_state()]
            page.update()
        def on_whatsapp(e, tel=telefone, n=nome, v=total_dev):
            page.launch_url(_whatsapp_url(tel, n, v))
        pedido_widgets = []
        for ped in pedidos_ab:
            total_itens = sum(i.quantidade for i in ped.itens)
            pedido_widgets.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(format_brl(ped.total), size=14,
                                            weight=ft.FontWeight.W_600, color=C["text"]),
                                    ft.Text(
                                        f"{ped.data.strftime('%d/%m/%Y')} — {total_itens} item(s)",
                                        size=11, color=C["muted"],
                                    ),
                                ],
                                spacing=2, tight=True, expand=True,
                            ),
                            ft.Container(
                                tooltip="Enviar mensagem no WhatsApp Web",
                                content=ft.Row(
                                    controls=[
                                        ft.Stack(
                                            controls=[
                                                ft.Container(width=18, height=18,
                                                             border_radius=9,
                                                             bgcolor=C["wa_green"]),
                                                ft.Container(
                                                    content=ft.Icon(Icons.CHAT_BUBBLE,
                                                                    size=11, color=C["white"]),
                                                    width=18, height=18,
                                                    alignment=ft.Alignment(0, 0),
                                                ),
                                            ],
                                            width=18, height=18,
                                        ),
                                        ft.Text("WhatsApp", size=12, color=C["wa_green"],
                                                weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=6, tight=True,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=ft.Padding(left=14, top=9, right=14, bottom=9),
                                border_radius=8,
                                border=ft.Border(left=ft.BorderSide(1.5, C["wa_green"]), top=ft.BorderSide(1.5, C["wa_green"]), right=ft.BorderSide(1.5, C["wa_green"]), bottom=ft.BorderSide(1.5, C["wa_green"])),
                                bgcolor=C["wa_bg"],
                                on_click=on_whatsapp,
                                ink=True,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(Icons.CHECK_CIRCLE_OUTLINE, size=16,
                                                color=C["white"]),
                                        ft.Text("Marcar pago", size=12, color=C["white"],
                                                weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=6, tight=True,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=ft.Padding(left=14, top=9, right=14, bottom=9),
                                border_radius=8,
                                bgcolor=C["success"],
                                on_click=on_marcar_pago,
                                ink=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=ft.Padding(left=14, top=12, right=14, bottom=12),
                    bgcolor=C["surface"],
                    border_radius=10,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                )
            )
        return ft.Container(
            data=cliente.id,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(nome, size=16, weight=ft.FontWeight.BOLD,
                                                    color=C["text"]),
                                            ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(Icons.ERROR_OUTLINE, size=13,
                                                                color=C["danger"]),
                                                        ft.Text(f"Devendo {format_brl(total_dev)}",
                                                                size=12, color=C["danger"],
                                                                weight=ft.FontWeight.W_500),
                                                    ],
                                                    spacing=4, tight=True,
                                                ),
                                                padding=ft.Padding(left=10, top=4, right=10, bottom=4),
                                                border_radius=20,
                                                bgcolor=C["danger_bg"],
                                            ),
                                        ],
                                        spacing=10,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Text(f"📞 {cliente.telefone}" if cliente else "",
                                            size=11, color=C["muted"]),
                                ],
                                spacing=2, tight=True, expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(f"{len(pedidos_ab)} pedido(s)", size=11,
                                            color=C["muted"], text_align=ft.TextAlign.RIGHT),
                                    ft.Text(f"Total: {format_brl(total_dev)}", size=13,
                                            weight=ft.FontWeight.BOLD, color=C["text"],
                                            text_align=ft.TextAlign.RIGHT),
                                ],
                                spacing=2, tight=True,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Divider(height=1, color=C["border"]),
                    ft.Text("PEDIDOS EM ABERTO", size=10, color=C["muted"],
                            weight=ft.FontWeight.W_600),
                    ft.Column(controls=pedido_widgets, spacing=8),
                ],
                spacing=12,
            ),
            padding=ft.Padding(left=18, top=18, right=18, bottom=18),
            bgcolor=C["surface"],
            border_radius=14,
            border=ft.Border(left=ft.BorderSide(1.5, "#fca5a5"), top=ft.BorderSide(1.5, "#fca5a5"), right=ft.BorderSide(1.5, "#fca5a5"), bottom=ft.BorderSide(1.5, "#fca5a5")),
        )
    def _empty_state() -> ft.Container:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(Icons.CHECK_CIRCLE, size=52, color=C["success"]),
                    ft.Text("Tudo em dia!", size=18, weight=ft.FontWeight.BOLD, color=C["text"]),
                    ft.Text("Nenhum cliente com pagamento pendente.",
                            size=13, color=C["text_label"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding(left=0, top=60, right=0, bottom=60),
        )
    def on_busca(e):
        filtro = e.control.value.strip().lower()
        grupos = store.pedidos_pendentes_por_cliente()
        if filtro:
            grupos = [g for g in grupos
                      if g["cliente"] and (
                          filtro in g["cliente"].nome.lower()
                          or filtro in g["cliente"].telefone)]
        lista_ref.current.controls = (
            [_build_card(g) for g in grupos] if grupos else [_empty_state()]
        )
        page.update()
    grupos_init    = store.pedidos_pendentes_por_cliente()
    total_pendente = sum(g["total_pendente"] for g in grupos_init)
    qtd_pendentes  = len(grupos_init)
    total_clientes = len(store.clientes)
    card_total = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(Icons.ERROR_OUTLINE, color=C["danger"], size=22),
                    width=48, height=48, border_radius=12, bgcolor=C["danger_bg"],
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text("Total a receber", size=11, color=C["text_label"]),
                        ft.Text(ref=total_ref, value=format_brl(total_pendente),
                                size=20, weight=ft.FontWeight.BOLD, color=C["danger"]),
                        ft.Text(ref=qtd_ref,
                                value=f"{qtd_pendentes} cliente(s) com pendência",
                                size=11, color=C["muted"]),
                    ],
                    spacing=2, tight=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=18, top=18, right=18, bottom=18),
        bgcolor="#fff1f2",
        border_radius=14,
        border=ft.Border(left=ft.BorderSide(1.5, "#fca5a5"), top=ft.BorderSide(1.5, "#fca5a5"), right=ft.BorderSide(1.5, "#fca5a5"), bottom=ft.BorderSide(1.5, "#fca5a5")),
        expand=True,
    )
    card_ativos = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(Icons.SHOPPING_BAG_OUTLINED, color=C["success"], size=22),
                    width=48, height=48, border_radius=12, bgcolor=C["success_bg"],
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text("Clientes ativos", size=11, color=C["text_label"]),
                        ft.Text(str(total_clientes), size=20,
                                weight=ft.FontWeight.BOLD, color=C["text"]),
                        ft.Text("já fizeram pedidos", size=11, color=C["muted"]),
                    ],
                    spacing=2, tight=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=18, top=18, right=18, bottom=18),
        bgcolor=C["surface"],
        border_radius=14,
        border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        expand=True,
    )
    cards_init = ([_build_card(g) for g in grupos_init]
                  if grupos_init else [_empty_state()])
    return ft.Column(
        controls=[
            ft.Column(
                controls=[
                    ft.Text("Clientes", size=24, weight=ft.FontWeight.BOLD, color=C["text"]),
                    ft.Text("Quem comprou e quem está com pagamento pendente.",
                            size=14, color=C["text_label"]),
                ],
                spacing=4,
            ),
            ft.Row(controls=[card_total, card_ativos], spacing=16),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(Icons.SEARCH, size=18, color=C["muted"]),
                        ft.TextField(
                            hint_text="Buscar por nome ou telefone...",
                            hint_style=ft.TextStyle(color=C["muted"], size=13),
                            border=ft.InputBorder.NONE,
                            expand=True, height=40, text_size=13,
                            content_padding=ft.Padding(left=0, top=0, right=0, bottom=0),
                            on_change=on_busca,
                            color=C["text"],
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, top=8, right=16, bottom=8),
                bgcolor=C["surface"],
                border_radius=12,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
            ),
            ft.Column(ref=lista_ref, controls=cards_init, spacing=16),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
def view_gastos(store: GranjaStore, page: ft.Page) -> ft.Control:
    Icons     = ft.icons.Icons
    lista_ref = ft.Ref[ft.Column]()
    total_ref = ft.Ref[ft.Text]()
    def _total() -> float:
        return sum(g.valor for g in store.gastos)
    def _build_card(gasto) -> ft.Container:
        def on_excluir(e, gid=gasto.id):
            store.remover_gasto(gid)
            lista_ref.current.controls = _build_lista()
            total_ref.current.value = format_brl(_total())
            page.update()
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(Icons.ATTACH_MONEY, color=C["danger"], size=20),
                        width=44, height=44, border_radius=10, bgcolor=C["danger_bg"],
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(gasto.descricao, size=15,
                                    weight=ft.FontWeight.W_600, color=C["text"]),
                            ft.Text(
                                f"{gasto.categoria} • {gasto.data.strftime('%d/%m/%Y')}",
                                size=12, color=C["muted"],
                            ),
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                    ft.Text(format_brl(gasto.valor), size=15,
                            weight=ft.FontWeight.BOLD, color=C["danger"]),
                    ft.IconButton(
                        icon=Icons.DELETE_OUTLINE,
                        icon_color=C["danger"],
                        icon_size=20,
                        tooltip="Excluir gasto",
                        on_click=on_excluir,
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=18, top=14, right=18, bottom=14),
            bgcolor=C["surface"],
            border_radius=12,
            border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        )
    def _build_lista() -> list:
        if not store.gastos:
            return [ft.Container(
                content=ft.Text("Nenhum gasto cadastrado.", size=13, color=C["muted"]),
                padding=ft.Padding(left=0, top=40, right=0, bottom=40),
                alignment=ft.Alignment(0, 0),
            )]
        return [_build_card(g) for g in store.gastos]
    desc_field  = ft.TextField(label="Descrição", hint_text="Ex: Ração", border_radius=8)
    valor_field = ft.TextField(label="Valor (R$)", hint_text="Ex: 150.00",
                                keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
    categ_field = ft.TextField(label="Categoria", hint_text="Ex: Insumos", border_radius=8)
    erro_ref    = ft.Ref[ft.Text]()
    def on_salvar(e):
        desc  = desc_field.value.strip()
        categ = categ_field.value.strip() or "Outros"
        try:
            valor = float(valor_field.value.replace(",", "."))
        except (ValueError, AttributeError):
            erro_ref.current.value = "Informe um valor numérico válido."
            page.update()
            return
        if not desc:
            erro_ref.current.value = "Informe a descrição."
            page.update()
            return
        store.adicionar_gasto(desc, valor, categ)
        desc_field.value = valor_field.value = categ_field.value = ""
        erro_ref.current.value = ""
        lista_ref.current.controls = _build_lista()
        total_ref.current.value = format_brl(_total())
        page.close(dialogo)
        page.update()
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text("Novo Gasto", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                desc_field, valor_field, categ_field,
                ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
            ],
            spacing=12, tight=True, width=340,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(dialogo)),
            ft.FilledButton("Salvar", on_click=on_salvar,
                            style=ft.ButtonStyle(bgcolor=C["success"])),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Gastos", size=24,
                                    weight=ft.FontWeight.BOLD, color=C["text"]),
                            ft.Row(
                                controls=[
                                    ft.Text("Total acumulado: ", size=13, color=C["text_label"]),
                                    ft.Text(ref=total_ref, value=format_brl(_total()),
                                            size=13, weight=ft.FontWeight.BOLD, color=C["danger"]),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=2, expand=True,
                    ),
                    _btn_primary("Novo gasto", Icons.ADD,
                                 lambda e: page.open(dialogo)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Column(ref=lista_ref, controls=_build_lista(), spacing=12),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
def view_produtos(store: GranjaStore, page: ft.Page) -> ft.Control:
    Icons    = ft.icons.Icons
    grid_ref = ft.Ref[ft.ResponsiveRow]()
    nome_field    = ft.TextField(label="Nome do produto", border_radius=8)
    preco_field   = ft.TextField(label="Preço (R$)", keyboard_type=ft.KeyboardType.NUMBER,
                                  border_radius=8)
    estoque_field = ft.TextField(label="Estoque (unidades)",
                                  keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
    erro_ref      = ft.Ref[ft.Text]()
    titulo_ref    = ft.Ref[ft.Text]()
    editando_id   = [None]
    def _rebuild():
        grid_ref.current.controls = [_build_card(p) for p in store.produtos]
    def _build_card(prod) -> ft.Column:
        def on_editar(e, pid=prod.id):
            p = next((x for x in store.produtos if x.id == pid), None)
            if not p:
                return
            editando_id[0] = pid
            titulo_ref.current.value = "Editar Produto"
            nome_field.value    = p.nome
            preco_field.value   = str(p.preco)
            estoque_field.value = str(p.estoque)
            erro_ref.current.value = ""
            page.open(dialogo)
        def on_excluir(e, pid=prod.id):
            store.remover_produto(pid)
            _rebuild()
            page.update()
        return ft.Column(
            col={"xs": 12, "sm": 6, "md": 4},
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(Icons.INVENTORY_2_OUTLINED,
                                                color=C["success"], size=22),
                                width=44, height=44, border_radius=10, bgcolor=C["success_bg"],
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text(prod.nome, size=14,
                                    weight=ft.FontWeight.W_600, color=C["text"]),
                            ft.Text(format_brl(prod.preco), size=16,
                                    weight=ft.FontWeight.BOLD, color=C["success"]),
                            ft.Text(f"Estoque: {prod.estoque}", size=12, color=C["muted"]),
                            ft.Divider(height=1, color=C["border"]),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(Icons.EDIT_OUTLINED, size=14,
                                                        color=C["text"]),
                                                ft.Text("Editar", size=12, color=C["text"]),
                                            ],
                                            spacing=4, tight=True,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        padding=ft.Padding(left=14, top=8, right=14, bottom=8),
                                        border_radius=8,
                                        border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                                        expand=True,
                                        on_click=on_editar,
                                        ink=True,
                                        alignment=ft.Alignment(0, 0),
                                    ),
                                    ft.IconButton(
                                        icon=Icons.DELETE_OUTLINE,
                                        icon_color=C["danger"],
                                        icon_size=18,
                                        tooltip="Excluir produto",
                                        on_click=on_excluir,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding(left=16, top=16, right=16, bottom=16),
                    bgcolor=C["surface"],
                    border_radius=14,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                )
            ],
        )
    def on_salvar(e):
        nome = nome_field.value.strip()
        try:
            preco   = float(preco_field.value.replace(",", "."))
            estoque = int(estoque_field.value)
        except (ValueError, AttributeError):
            erro_ref.current.value = "Preencha preço e estoque corretamente."
            page.update()
            return
        if not nome:
            erro_ref.current.value = "Informe o nome do produto."
            page.update()
            return
        if editando_id[0]:
            store.editar_produto(editando_id[0], nome, preco, estoque)
        else:
            store.adicionar_produto(nome, preco, estoque)
        nome_field.value = preco_field.value = estoque_field.value = ""
        erro_ref.current.value = ""
        editando_id[0] = None
        _rebuild()
        page.close(dialogo)
        page.update()
    dialogo = ft.AlertDialog(
        modal=True,
        title=ft.Text(ref=titulo_ref, value="Novo Produto", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                nome_field, preco_field, estoque_field,
                ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
            ],
            spacing=12, tight=True, width=340,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(dialogo)),
            ft.FilledButton("Salvar", on_click=on_salvar,
                            style=ft.ButtonStyle(bgcolor=C["success"])),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    def on_novo(e):
        editando_id[0] = None
        titulo_ref.current.value = "Novo Produto"
        nome_field.value = preco_field.value = estoque_field.value = ""
        erro_ref.current.value = ""
        page.open(dialogo)
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Produtos", size=24,
                                    weight=ft.FontWeight.BOLD, color=C["text"]),
                            ft.Text("Catálogo da granja.", size=13, color=C["text_label"]),
                        ],
                        spacing=2, expand=True,
                    ),
                    _btn_primary("Novo produto", Icons.ADD, on_novo),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.ResponsiveRow(
                ref=grid_ref,
                controls=[_build_card(p) for p in store.produtos],
                run_spacing=16, spacing=16,
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
def view_pedidos(store: GranjaStore, page: ft.Page) -> ft.Control:
    Icons     = ft.icons.Icons
    lista_ref = ft.Ref[ft.Column]()
    def _tel_fmt(cliente_id: str) -> str:
        c = store.get_cliente(cliente_id)
        if not c:
            return ""
        d = c.telefone
        d = d[2:] if d.startswith("55") else d
        if len(d) == 11:
            return f"({d[:2]}) {d[2:7]}-{d[7:]}"
        return c.telefone
    def _badge(label, bg, color) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=11, color=color, weight=ft.FontWeight.W_600),
            padding=ft.Padding(left=10, top=4, right=10, bottom=4),
            border_radius=20, bgcolor=bg,
        )
    def _rebuild(e=None):
        lista_ref.current.controls = _build_lista()
        page.update()
    def _build_card(ped) -> ft.Container:
        concluido = ped.concluido
        pago      = ped.pago
        status_label = "Concluído" if concluido else "Pendente"
        status_bg    = C["success_bg"] if concluido else "#fef3c7"
        status_color = C["success"]    if concluido else C["warning"]
        pago_label   = "Pago"     if pago else "Não pago"
        pago_bg      = C["success_bg"] if pago else C["danger_bg"]
        pago_color   = C["success"]    if pago else C["danger"]
        itens_txt = []
        for item in ped.itens:
            prod = next((p for p in store.produtos if p.id == item.produto_id), None)
            nome_prod = prod.nome if prod else item.produto_id
            itens_txt.append(f"• {item.quantidade}× {nome_prod}")
        tel  = _tel_fmt(ped.cliente_id)
        meta = (f"{tel} • " if tel else "") + ped.data.strftime("%d/%m/%Y, %H:%M:%S")
        botoes = []
        if pago:
            botoes.append(_btn_outline(
                "Marcar não pago", Icons.REMOVE_CIRCLE_OUTLINE,
                lambda e, pid=ped.id: [store.marcar_pedido_nao_pago(pid), _rebuild()],
            ))
            botoes.append(_btn_outline(
                "Reabrir", Icons.REFRESH,
                lambda e, pid=ped.id: [store.reabrir_pedido(pid), _rebuild()],
            ))
        else:
            botoes.append(_btn_filled(
                "Marcar pago", Icons.CHECK_CIRCLE_OUTLINE,
                lambda e, pid=ped.id: [store.marcar_pedido_pago(pid), _rebuild()],
            ))
            botoes.append(_btn_outline(
                "Concluir", Icons.CHECK,
                lambda e, pid=ped.id: [store.concluir_pedido(pid), _rebuild()],
            ))
        botoes.append(ft.IconButton(
            icon=Icons.DELETE_OUTLINE,
            icon_color=C["danger"],
            icon_size=18,
            tooltip="Excluir pedido",
            on_click=lambda e, pid=ped.id: [store.remover_pedido(pid), _rebuild()],
        ))
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(ped.cliente_nome, size=15,
                                                    weight=ft.FontWeight.BOLD, color=C["text"]),
                                            _badge(status_label, status_bg, status_color),
                                            _badge(pago_label, pago_bg, pago_color),
                                        ],
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        wrap=True,
                                    ),
                                    ft.Text(meta, size=11, color=C["muted"]),
                                ],
                                spacing=4, tight=True, expand=True,
                            ),
                            ft.Text(format_brl(ped.total), size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=C["success"] if pago else C["danger"]),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Column(
                        controls=[ft.Text(t, size=12, color=C["text_label"]) for t in itens_txt],
                        spacing=2,
                    ),
                    ft.Row(
                        controls=botoes,
                        spacing=8,
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding(left=18, top=18, right=18, bottom=18),
            bgcolor=C["surface"],
            border_radius=14,
            border=ft.Border(left=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        )
    def _build_lista() -> list:
        if not store.pedidos:
            return [ft.Container(
                content=ft.Text("Nenhum pedido registrado.", size=13, color=C["muted"]),
                padding=ft.Padding(left=0, top=40, right=0, bottom=40),
                alignment=ft.Alignment(0, 0),
            )]
        return [_build_card(p) for p in store.pedidos]
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Pedidos", size=24,
                                    weight=ft.FontWeight.BOLD, color=C["text"]),
                            ft.Text("Acompanhe e crie pedidos.",
                                    size=13, color=C["text_label"]),
                        ],
                        spacing=2, expand=True,
                    ),
                    _btn_primary("Novo pedido", Icons.ADD, lambda e: None),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Column(ref=lista_ref, controls=_build_lista(), spacing=12),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
def main(page: ft.Page):
    page.title       = "Granja Manager"
    page.bgcolor     = C["bg"]
    page.padding     = 0
    page.theme_mode  = ft.ThemeMode.LIGHT
    page.window_width     = 1100
    page.window_height    = 800
    page.window_min_width = 700
    store         = GranjaStore()
    current_route = ["dashboard"]
    content_area  = ft.Container(expand=True, padding=ft.Padding(left=28, top=28, right=28, bottom=28))
    def get_view(route: str) -> ft.Control:
        if route == "dashboard":
            return view_dashboard(store)
        elif route == "clientes_pendentes":
            def refresh():
                content_area.content = view_clientes_pendentes(store, page, refresh)
                page.update()
            return view_clientes_pendentes(store, page, refresh)
        elif route == "produtos":
            return view_produtos(store, page)
        elif route == "pedidos":
            return view_pedidos(store, page)
        elif route == "gastos":
            return view_gastos(store, page)
        return view_dashboard(store)
    def navigate(route: str):
        current_route[0] = route
        content_area.content = get_view(route)
        layout.controls[0]   = build_sidebar(current_route[0], navigate)
        page.update()
    layout = ft.Row(
        controls=[
            build_sidebar(current_route[0], navigate),
            content_area,
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    content_area.content = get_view(current_route[0])
    page.add(layout)
if __name__ == "__main__":
    ft.app(target=main)