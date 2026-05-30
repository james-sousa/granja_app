"""
Granja Manager - MVP Completo
Sistema de Gestão para Granja com Persistência em SQLite

Arquitetura:
- Models: Dataclasses dos objetos
- Database: Camada de acesso a dados (SQLite)
- Repositories: Padrão Repository para abstrair dados
- Services: Lógica de negócio
- Views: Interface Flet
- Utils: Validadores, formatadores, helpers

Fluxo obrigatório de pedidos:
1. Usuário cria pedido
2. Sistema verifica cliente (cria se não existir)
3. Sistema valida estoque
4. Sistema persiste no banco
5. Sistema atualiza estoque
6. Sistema atualiza dashboard

Para executar:
    pip install flet
    python app.py
"""

import flet as ft
import urllib.parse
from datetime import datetime
import logging

# Importa o sistema de inicialização
# Removido SQLite local - usando apenas Supabase
# from granja_manager.database import db, Migrations, Seed
from granja_manager.services import (
    ClienteService,
    ProdutoService,
    PedidoService,
    GastoService,
    DashboardService,
    FinanceiroService,
    EstoqueService,
)
from granja_manager.utils import Formatters, Validators, setup_logging

# Configura logging
setup_logging("granja_manager/logs/app.log")
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# PALETA DE CORES (mantida do original)
# ══════════════════════════════════════════════════════════════════

C = {
    "bg":               "#fdfdfd",
    "sidebar":          "#1a5c30",
    "surface":          "#ffffff",
    "border":           "#e8e8e8",
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
    "transparent":      "transparent",
    "wa_green":         "#25D366",
    "wa_bg":            "#e9faf0",
}

SIDEBAR_W = 220
SIDEBAR_W_COLLAPSED = 64

NAV_ITEMS = [
    ("dashboard",          "Dashboard",  ft.icons.DASHBOARD),
    ("clientes_pendentes", "Clientes",   ft.icons.PEOPLE_ALT),
    ("produtos",           "Produtos",   ft.icons.INVENTORY_2),
    ("estoque",            "Estoque",    ft.icons.WAREHOUSE),
    ("pedidos",            "Pedidos",    ft.icons.SHOPPING_CART),
    ("gastos",             "Gastos",     ft.icons.RECEIPT_LONG),
]


# ══════════════════════════════════════════════════════════════════
# HELPERS DE DIÁLOGO
# ══════════════════════════════════════════════════════════════════

def _abrir_dialogo(page: ft.Page, dialogo: ft.AlertDialog):
    """Abre um AlertDialog compatível com qualquer versão do Flet.
    Versões >= 0.23 usam page.open(); versões anteriores usam overlay."""
    if hasattr(page, "open"):
        # Flet >= 0.23
        page.open(dialogo)
    else:
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()


def _fechar_dialogo(page: ft.Page, dialogo: ft.AlertDialog):
    """Fecha um AlertDialog SEM chamar page.update().
    Versões >= 0.23 usam page.close(); versões anteriores setam open=False.
    O chamador é responsável pelo page.update() final."""
    if hasattr(page, "close"):
        # Flet >= 0.23 — page.close() já chama update internamente,
        # mas como queremos um único ciclo, usamos apenas open=False aqui
        # e deixamos o page.update() do chamador fechar o ciclo.
        dialogo.open = False
    else:
        dialogo.open = False


# ══════════════════════════════════════════════════════════════════
# COMPONENTES REUTILIZÁVEIS
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════

def extrair_iniciais(nome: str) -> str:
    """Extrai as iniciais do nome do usuário.
    Ex: 'Rafael da Silva' -> 'RS'"""
    if not nome:
        return "U"
    palavras = nome.strip().split()
    iniciais = "".join([p[0].upper() for p in palavras if p])
    return iniciais[:2]  # Retorna até 2 iniciais


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
        padding=ft.Padding(left=18, right=18, top=10, bottom=10),
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
        padding=ft.Padding(left=14, right=14, top=8, bottom=8),
        border_radius=8,
        border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
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
                ft.Icon(icon, size=13, color=tc),
                ft.Text(label, size=12, color=tc, weight=ft.FontWeight.W_600),
            ],
            spacing=5, tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=13, right=13, top=7, bottom=7),
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
        border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
    )


def resumo_tile(label, value_str, icon, icon_color, icon_bg, tile_bg, value_color) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color=icon_color, size=24),
                    width=52, height=52, border_radius=12, bgcolor=icon_bg,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text(label, size=12, color=C["text_label"]),
                        ft.Text(value_str, size=21, weight=ft.FontWeight.BOLD, color=value_color),
                    ],
                    spacing=3, tight=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=20, top=20, right=20, bottom=20),
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
                    ft.Text(Formatters.formato_brl(produto.preco), size=11, color=C["muted"]),
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
        border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
    )


def build_sidebar(current_route: str, on_navigate, collapsed: bool = False, usuario: dict = None) -> ft.Container:
    """Constrói o sidebar de navegação. collapsed=True mostra só ícones."""

    def nav_item(route, label, icon):
        active = route == current_route
        if collapsed:
            return ft.Container(
                content=ft.Icon(icon, size=20,
                                color=C["sidebar_text"] if active else C["sidebar_muted"]),
                width=64, height=44,
                border_radius=10,
                bgcolor=C["sidebar_active_bg"] if active else C["transparent"],
                alignment=ft.Alignment(0, 0),
                on_click=lambda e, r=route: on_navigate(r),
                ink=not active,
                tooltip=label,
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            )
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
            padding=ft.Padding(left=16, right=16, top=11, bottom=11),
            border_radius=10,
            bgcolor=C["sidebar_active_bg"] if active else C["transparent"],
            on_click=lambda e, r=route: on_navigate(r),
            ink=not active,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

    if collapsed:
        # Modo colapsado: ícone + nome em texto pequeno
        logo = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text("🐔", size=20),
                        width=40, height=40, border_radius=10, bgcolor=C["rank_bg"],
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text("Granja", size=9, weight=ft.FontWeight.BOLD,
                            color=C["white"], text_align=ft.TextAlign.CENTER),
                    ft.Text("Manager", size=8, color=C["sidebar_muted"],
                            text_align=ft.TextAlign.CENTER),
                ],
                spacing=3,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=8, top=14, right=8, bottom=14),
            alignment=ft.Alignment(0, 0),
        )
        footer = ft.Container(
            content=ft.Container(
                content=ft.Text(extrair_iniciais(usuario.get('nome')) if usuario else 'U', size=11, weight=ft.FontWeight.BOLD, color=C["white"]),
                width=32, height=32, border_radius=16, bgcolor=C["rank_bg"],
                alignment=ft.Alignment(0, 0),
            ),
            padding=ft.Padding(left=16, top=12, right=16, bottom=12),
            border=ft.Border(top=ft.BorderSide(1, "#2d7a4a")),
            alignment=ft.Alignment(0, 0),
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    logo,
                    ft.Container(ft.Divider(height=1, color="#2d7a4a"),
                                 padding=ft.Padding(left=0, top=0, right=0, bottom=8)),
                    ft.Column(
                        controls=[nav_item(r, l, i) for r, l, i in NAV_ITEMS],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(expand=True),
                    footer,
                ],
                spacing=0, expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=SIDEBAR_W_COLLAPSED,
            bgcolor=C["sidebar"],
            border=ft.Border(right=ft.BorderSide(1, C["border"])),
        )

    # Modo expandido (normal)
    logo = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("🐔", size=20),
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
                    content=ft.Text(extrair_iniciais(usuario.get('nome')) if usuario else 'U', size=11, weight=ft.FontWeight.BOLD, color=C["white"]),
                    width=32, height=32, border_radius=16, bgcolor=C["rank_bg"],
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    controls=[
                        ft.Text(usuario.get('nome') if usuario else 'Usuário', size=12, color=C["sidebar_text"], weight=ft.FontWeight.W_500),
                        ft.Text('Operador', size=10, color=C["sidebar_muted"]),
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
                    padding=ft.Padding(left=16, top=8, right=0, bottom=8),
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


# ══════════════════════════════════════════════════════════════════
# VIEWS
# ══════════════════════════════════════════════════════════════════

def view_dashboard(dashboard_service: DashboardService, page: ft.Page, usuario: dict = None) -> ft.Control:
    """View de Dashboard com dados reais do banco.
    
    Args:
        dashboard_service: Serviço de dashboard
        page: Página Flet
        usuario: Dicionário com dados do usuário logado
    """
    Icons = ft.icons
    nome_usuario = usuario.get('nome', 'Usuário') if usuario else 'Usuário'

    try:
        relatorio = dashboard_service.gerar_relatorio_completo()

        total_vendas = relatorio["metricas_dia"]["vendas_dia"]
        qtd_pedidos  = relatorio["metricas_dia"]["pedidos_dia"]
        vendas_mes   = relatorio["metricas_mes"]["vendas_mes"]
        gastos_mes   = relatorio["metricas_mes"]["gastos_mes"]
        lucro        = relatorio["metricas_mes"]["lucro_mes"]

        # ── Métricas de semana - Usando Supabase via dashboard_service ────────────────────
        metricas_dia = dashboard_service.obter_metricas_dia()
        gastos_dia = metricas_dia.get("gastos_dia", 0)
        
        metricas_semana = dashboard_service.obter_metricas_semana()
        vendas_semana = metricas_semana.get("vendas_semana", 0)
        pedidos_semana = metricas_semana.get("pedidos_semana", 0)
        gastos_semana = metricas_semana.get("gastos_semana", 0)

        lucro_dia    = total_vendas - gastos_dia
        lucro_semana = vendas_semana - gastos_semana
        lucro_mes    = lucro

        # ── Carrossel de períodos ─────────────────────────────────
        periodo_idx   = [1]   # 0=dia, 1=semana, 2=mês  (inicia em semana)
        carousel_ref  = ft.Ref[ft.Container]()

        periodos = [
            {
                "label":   "Hoje",
                "vendas":  total_vendas,
                "gastos":  gastos_dia,
                "lucro":   lucro_dia,
                "pedidos": qtd_pedidos,
            },
            {
                "label":   "Esta semana",
                "vendas":  vendas_semana,
                "gastos":  gastos_semana,
                "lucro":   lucro_semana,
                "pedidos": pedidos_semana,
            },
            {
                "label":   f"Mês — {Formatters.mes_ano_atual()}",
                "vendas":  vendas_mes,
                "gastos":  gastos_mes,
                "lucro":   lucro_mes,
                "pedidos": None,
            },
        ]

        def _build_carousel(idx: int) -> ft.Control:
            p         = periodos[idx]
            lbl       = p["label"]
            lc        = C["success"] if p["lucro"] >= 0 else C["danger"]
            lbg       = C["success_bg"] if p["lucro"] >= 0 else C["danger_bg"]
            ltbg      = "#f0fdf4" if p["lucro"] >= 0 else "#fff1f2"
            ll        = "Lucro" if p["lucro"] >= 0 else "Prejuízo"
            mobile    = (page.width or 0) < 600

            indicadores = ft.Row(
                controls=[
                    ft.Container(
                        width=8, height=8, border_radius=4,
                        bgcolor=C["sidebar"] if i == idx else C["border"],
                    )
                    for i in range(len(periodos))
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            tiles = ft.ResponsiveRow(
                controls=[
                    ft.Column([resumo_tile(
                        "Vendas", Formatters.formato_brl(p["vendas"]),
                        Icons.ATTACH_MONEY, C["success"], C["success_bg"], "#f0fdf4", C["success"],
                    )], col={"xs": 12, "sm": 4}),
                    ft.Column([resumo_tile(
                        "Gastos", Formatters.formato_brl(p["gastos"]),
                        Icons.RECEIPT, C["danger"], C["danger_bg"], "#fff1f2", C["danger"],
                    )], col={"xs": 12, "sm": 4}),
                    ft.Column([resumo_tile(
                        ll, Formatters.formato_brl(abs(p["lucro"])),
                        Icons.ACCOUNT_BALANCE_WALLET, lc, lbg, ltbg, lc,
                    )], col={"xs": 12, "sm": 4}),
                ],
                run_spacing=16, spacing=16,
            )

            btn_prev = ft.IconButton(
                icon=Icons.CHEVRON_LEFT,
                icon_color=C["sidebar"] if idx > 0 else C["border"],
                icon_size=24,
                disabled=idx == 0,
                on_click=lambda e: _nav(-1),
                visible=not mobile,
            )
            btn_next = ft.IconButton(
                icon=Icons.CHEVRON_RIGHT,
                icon_color=C["sidebar"] if idx < len(periodos) - 1 else C["border"],
                icon_size=24,
                disabled=idx == len(periodos) - 1,
                on_click=lambda e: _nav(+1),
                visible=not mobile,
            )

            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                btn_prev,
                                ft.Text(lbl, size=15, weight=ft.FontWeight.BOLD,
                                        color=C["text"], expand=True,
                                        text_align=ft.TextAlign.CENTER),
                                btn_next,
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),
                        tiles,
                        indicadores,
                    ],
                    spacing=18,
                ),
                padding=20,
                bgcolor=C["surface"],
                border_radius=14,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
            )

        def _build_carousel_mobile() -> ft.Control:
            """Versão mobile: swipe com snap estilo Instagram."""
            slide_idx   = [1]  # começa na semana
            slide_ref   = ft.Ref[ft.Container]()
            dots_ref    = ft.Ref[ft.Row]()
            label_ref   = ft.Ref[ft.Text]()
            drag_start  = [0.0]

            def _make_tiles(p):
                lc   = C["success"] if p["lucro"] >= 0 else C["danger"]
                lbg  = C["success_bg"] if p["lucro"] >= 0 else C["danger_bg"]
                ltbg = "#f0fdf4" if p["lucro"] >= 0 else "#fff1f2"
                ll   = "Lucro" if p["lucro"] >= 0 else "Prejuízo"
                return ft.Column(
                    controls=[
                        resumo_tile("Vendas", Formatters.formato_brl(p["vendas"]),
                            ft.icons.ATTACH_MONEY, C["success"], C["success_bg"], "#f0fdf4", C["success"]),
                        resumo_tile("Gastos", Formatters.formato_brl(p["gastos"]),
                            ft.icons.RECEIPT, C["danger"], C["danger_bg"], "#fff1f2", C["danger"]),
                        resumo_tile(ll, Formatters.formato_brl(abs(p["lucro"])),
                            ft.icons.ACCOUNT_BALANCE_WALLET, lc, lbg, ltbg, lc),
                    ],
                    spacing=10,
                )

            def _update_slide():
                p = periodos[slide_idx[0]]
                slide_ref.current.content  = _make_tiles(p)
                label_ref.current.value    = p["label"]
                dots_ref.current.controls  = [
                    ft.Container(
                        width=24 if j == slide_idx[0] else 8,
                        height=8, border_radius=4,
                        bgcolor=C["sidebar"] if j == slide_idx[0] else C["border"],
                        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                    )
                    for j in range(len(periodos))
                ]
                slide_ref.current.update()
                label_ref.current.update()
                dots_ref.current.update()

            drag_accum = [0.0]

            def on_h_drag_start(e):
                drag_accum[0] = 0.0

            def on_h_drag_update(e):
                try:
                    drag_accum[0] += e.delta_x if hasattr(e, 'delta_x') else (e.dx if hasattr(e, 'dx') else 0)
                    print(f"Drag update: delta={drag_accum[0]}")
                except Exception as ex:
                    print(f"Drag error: {ex}")

            def on_h_drag_end(e):
                delta = drag_accum[0]
                drag_accum[0] = 0.0
                # detecta tanto arrasto lento (>50px) quanto flick rápido (velocity)
                vel = e.velocity_x if hasattr(e, 'velocity_x') and e.velocity_x else 0
                print(f"Drag end: delta={delta}, vel={vel}, slide_idx={slide_idx[0]}, len={len(periodos)}")
                if (delta < -50 or vel < -300) and slide_idx[0] < len(periodos) - 1:
                    slide_idx[0] += 1
                    _update_slide()
                elif (delta > 50 or vel > 300) and slide_idx[0] > 0:
                    slide_idx[0] -= 1
                    _update_slide()

            return ft.GestureDetector(
                on_horizontal_drag_start=on_h_drag_start,
                on_horizontal_drag_update=on_h_drag_update,
                on_horizontal_drag_end=on_h_drag_end,
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                ref=label_ref,
                                value=periodos[slide_idx[0]]["label"],
                                size=15, weight=ft.FontWeight.BOLD,
                                color=C["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(
                                ref=slide_ref,
                                content=_make_tiles(periodos[slide_idx[0]]),
                                animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
                            ),
                            ft.Row(
                                ref=dots_ref,
                                controls=[
                                    ft.Container(
                                        width=24 if j == slide_idx[0] else 8,
                                        height=8, border_radius=4,
                                        bgcolor=C["sidebar"] if j == slide_idx[0] else C["border"],
                                    )
                                    for j in range(len(periodos))
                                ],
                                spacing=6,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    bgcolor=C["surface"],
                    border_radius=14,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                ),
            )

        mobile = (page.width or 0) < 600

        def _nav(delta: int):
            periodo_idx[0] = max(0, min(len(periodos) - 1, periodo_idx[0] + delta))
            carousel_ref.current.content = _build_carousel(periodo_idx[0]).content
            carousel_ref.current.update()

        if mobile:
            carousel_container = _build_carousel_mobile()
        else:
            carousel_container = ft.Container(
                ref=carousel_ref,
                content=_build_carousel(periodo_idx[0]).content,
                padding=16,
                bgcolor=C["surface"],
                border_radius=14,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
            )

        lucro_label  = "Lucro no mês" if lucro >= 0 else "Prejuízo no mês"
        lucro_color  = C["success"] if lucro >= 0 else C["danger"]

        metric_cards = [
            stat_card("Vendas de hoje", Formatters.formato_brl(total_vendas),
                     Icons.ATTACH_MONEY, C["success"], C["success_bg"]),
            stat_card("Pedidos de hoje", qtd_pedidos,
                     Icons.SHOPPING_CART, C["success"], C["success_bg"]),
            stat_card("Clientes ativos", relatorio["clientes_ativos"],
                     Icons.PEOPLE, C["success"], C["success_bg"]),
            stat_card("Produtos ativos", relatorio["produtos_ativos"],
                     Icons.TRENDING_UP, C["warning"], C["warning_bg"]),
        ]

        cards_row = ft.ResponsiveRow(
            controls=[ft.Column([c], col={"xs": 12, "sm": 6, "lg": 3}) for c in metric_cards],
            run_spacing=16, spacing=16,
        )

        top_produtos = relatorio["top_produtos"]
        top_content = (
            ft.Text("Nenhum pedido ainda.", size=13, color=C["muted"])
            if not top_produtos
            else ft.Column(
                controls=[top_produto_item(i + 1, p, q)
                         for i, (p, q) in enumerate(top_produtos)],
                spacing=16,
            )
        )

        return ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("👋", size=28),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"Olá, {nome_usuario.split()[0]}! 👋", size=24,
                                                weight=ft.FontWeight.BOLD, color=C["text"]),
                                        ft.Text("Resumo do seu dia na Granja Santo Antonio.",
                                                size=14, color=C["text_label"]),
                                    ],
                                    spacing=2, tight=True,
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=4,
                ),
                cards_row,
                carousel_container,
                card_wrapper("Produtos mais vendidos", top_content),
            ],
            spacing=24,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return ft.Container(
            content=ft.Text(f"Erro ao carregar dashboard: {e}", color=C["danger"]),
            padding=20,
        )


def view_produtos(produto_service: ProdutoService, page: ft.Page) -> ft.Control:
    """View de Produtos com CRUD completo."""
    Icons = ft.icons
    grid_ref = ft.Ref[ft.ResponsiveRow]()

    nome_field = ft.TextField(label="Nome do produto", border_radius=8)
    preco_field = ft.TextField(label="Preço (R$)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
    estoque_field = ft.TextField(label="Estoque (unidades)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
    erro_ref = ft.Ref[ft.Text]()
    titulo_ref = ft.Ref[ft.Text]()
    editando_id = [None]

    def _rebuild():
        produtos = produto_service.listar_produtos()
        grid_ref.current.controls = [_build_card(p) for p in produtos]
        page.update()

    def _build_card(prod) -> ft.Column:
        def on_editar(e, pid=prod.id):
            p = produto_service.obter_produto(pid)
            if not p:
                return
            editando_id[0] = pid
            titulo_ref.current.value = "Editar Produto"
            nome_field.value = p.nome
            preco_field.value = str(p.preco)
            estoque_field.value = str(p.estoque)
            erro_ref.current.value = ""
            _abrir_dialogo(page, dialogo)

        def on_excluir(e, pid=prod.id):
            try:
                produto_service.deletar_produto(pid)
                _rebuild()
                page.snack_bar = ft.SnackBar(ft.Text("Produto removido com sucesso"))
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"))
                page.snack_bar.open = True
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
                            ft.Text(Formatters.formato_brl(prod.preco), size=16,
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
                                        padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                                        border_radius=8,
                                        border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
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
                    padding=16,
                    bgcolor=C["surface"],
                    border_radius=14,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                )
            ],
        )

    def on_salvar(e):
        nome = nome_field.value.strip()
        try:
            preco = float(preco_field.value.replace(",", "."))
            estoque = int(estoque_field.value)
        except (ValueError, AttributeError):
            erro_ref.current.value = "Preencha preço e estoque corretamente."
            page.update()
            return
        if not nome:
            erro_ref.current.value = "Informe o nome do produto."
            page.update()
            return

        try:
            if editando_id[0]:
                produto_service.atualizar_produto(editando_id[0], nome, preco, estoque)
            else:
                produto_service.criar_produto(nome, preco, estoque)

            nome_field.value = ""
            preco_field.value = ""
            estoque_field.value = ""
            erro_ref.current.value = ""
            editando_id[0] = None
            # Reconstrói grid antes de fechar
            produtos = produto_service.listar_produtos()
            grid_ref.current.controls = [_build_card(p) for p in produtos]
            # Fecha diálogo (sem page.update interno)
            _fechar_dialogo(page, dialogo)
            page.snack_bar = ft.SnackBar(ft.Text("Produto salvo com sucesso!"))
            page.snack_bar.open = True
            # Um único page.update para tudo
            page.update()
        except Exception as ex:
            erro_ref.current.value = str(ex)
            page.update()

    def on_fechar_produto(e):
        _fechar_dialogo(page, dialogo)
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=C["surface"],
        title=ft.Text(ref=titulo_ref, value="Novo Produto", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                nome_field, preco_field, estoque_field,
                ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
            ],
            spacing=12, tight=True, width=340,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=on_fechar_produto),
            ft.FilledButton("Salvar", on_click=on_salvar,
                           style=ft.ButtonStyle(bgcolor=C["success"])),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def on_novo(e):
        try:
            editando_id[0] = None
            titulo_ref.current.value = "Novo Produto"
            nome_field.value = ""
            preco_field.value = ""
            estoque_field.value = ""
            erro_ref.current.value = ""
            _abrir_dialogo(page, dialogo)
        except Exception as ex:
            logger.error(f"Erro ao abrir diálogo: {ex}")

    produtos = produto_service.listar_produtos()

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
                controls=[_build_card(p) for p in produtos],
                run_spacing=16, spacing=16,
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def view_clientes_pendentes(cliente_service: ClienteService, page: ft.Page) -> ft.Control:
    """View de Clientes com pendências."""
    Icons = ft.icons

    lista_ref = ft.Ref[ft.Column]()
    total_ref = ft.Ref[ft.Text]()
    qtd_ref = ft.Ref[ft.Text]()

    def _whatsapp_url(telefone: str, nome: str, valor: float) -> str:
        msg = (
            f"Olá {nome}! 👋\n"
            f"Passando para lembrar que você tem um pagamento pendente "
            f"de *{Formatters.formato_brl(valor)}* na Granja. 🐔\n"
            f"Quando puder, por favor efetue o pagamento. Obrigado! 😊"
        )
        texto = urllib.parse.quote(msg)
        # Remove tudo que não for dígito e garante código do país (55 = Brasil)
        numero = "".join(filter(str.isdigit, telefone))
        if not numero.startswith("55"):
            numero = "55" + numero
        mobile = (page.width or 0) < 600
        if mobile:
            return f"https://wa.me/{numero}?text={texto}"
        else:
            return f"https://web.whatsapp.com/send?phone={numero}&text={texto}"

    def _build_card(grupo: dict) -> ft.Container:
        cliente = grupo["cliente"]
        pedidos_ab = grupo["pedidos"]
        total_dev = grupo["total_pendente"]
        telefone = cliente.telefone if cliente else "5500000000000"
        nome = cliente.nome if cliente else "Desconhecido"

        def on_marcar_pago(e, cid=cliente.id):
            for ped in pedidos_ab:
                from granja_manager.services import PedidoService
                pedido_service = PedidoService()
                pedido_service.marcar_pago(ped.id)

            grupos = cliente_service.obter_clientes_com_pendencias()
            lista_ref.current.controls = (
                [_build_card(g) for g in grupos] if grupos else [_empty_state()]
            )
            novos = cliente_service.obter_clientes_com_pendencias()
            total_ref.current.value = Formatters.formato_brl(sum(g["total_pendente"] for g in novos))
            qtd_ref.current.value = f"{len(novos)} cliente(s) com pendência"
            page.update()

        async def on_whatsapp(e, tel=telefone, n=nome, v=total_dev):
            url = _whatsapp_url(tel, n, v)
            # Abre URL em navegador padrão
            try:
                await page.launch_url(url)
            except:
                # Fallback para webbrowser
                import webbrowser
                webbrowser.open(url)

        pedido_widgets = []
        for ped in pedidos_ab:
            total_itens = sum(i.quantidade for i in ped.itens)
            pedido_widgets.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # valor + data
                            ft.Row(
                                controls=[
                                    ft.Text(Formatters.formato_brl(ped.total), size=15,
                                            weight=ft.FontWeight.W_600, color=C["text"]),
                                    ft.Text(
                                        f"{Formatters.formato_data(ped.data)} — {total_itens} item(s)",
                                        size=12, color=C["muted"], expand=True,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            # botões em wrap para mobile
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        tooltip="Enviar mensagem no WhatsApp Web",
                                        content=ft.Row(
                                            controls=[
                                                ft.Stack(
                                                    controls=[
                                                        ft.Container(width=16, height=16,
                                                                   border_radius=8,
                                                                   bgcolor=C["wa_green"]),
                                                        ft.Container(
                                                            content=ft.Icon(Icons.CHAT_BUBBLE,
                                                                          size=10, color=C["white"]),
                                                            width=16, height=16,
                                                            alignment=ft.Alignment(0, 0),
                                                        ),
                                                    ],
                                                    width=16, height=16,
                                                ),
                                                ft.Text("WhatsApp", size=13, color=C["wa_green"],
                                                       weight=ft.FontWeight.W_600),
                                            ],
                                            spacing=6, tight=True,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                                        border_radius=8,
                                        border=ft.Border(left=ft.BorderSide(1.5, C["wa_green"]), right=ft.BorderSide(1.5, C["wa_green"]), top=ft.BorderSide(1.5, C["wa_green"]), bottom=ft.BorderSide(1.5, C["wa_green"])),
                                        bgcolor=C["wa_bg"],
                                        on_click=on_whatsapp,
                                        ink=True,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(Icons.CHECK_CIRCLE_OUTLINE, size=15,
                                                       color=C["white"]),
                                                ft.Text("Marcar pago", size=13, color=C["white"],
                                                       weight=ft.FontWeight.W_600),
                                            ],
                                            spacing=6, tight=True,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                                        border_radius=8,
                                        bgcolor=C["success"],
                                        on_click=on_marcar_pago,
                                        ink=True,
                                        expand=True,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.Padding(left=14, right=14, top=12, bottom=12),
                    bgcolor=C["surface"],
                    border_radius=10,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # ── Nome + total devendo ───────────────────────
                    ft.Row(
                        controls=[
                            ft.Text(nome, size=17, weight=ft.FontWeight.BOLD,
                                    color=C["text"], expand=True),
                            ft.Text(Formatters.formato_brl(total_dev), size=16,
                                    weight=ft.FontWeight.BOLD, color=C["danger"]),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    # ── Telefone + badge pendência ─────────────────
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"📞 {Formatters.formato_telefone(cliente.telefone)}" if cliente else "",
                                size=12, color=C["muted"], expand=True,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(Icons.ERROR_OUTLINE, size=12, color=C["danger"]),
                                        ft.Text(f"{len(pedidos_ab)} pedido(s) em aberto",
                                                size=11, color=C["danger"],
                                                weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=4, tight=True,
                                ),
                                padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                                border_radius=20,
                                bgcolor=C["danger_bg"],
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=C["border"]),
                    ft.Text("PEDIDOS EM ABERTO", size=10, color=C["muted"],
                            weight=ft.FontWeight.W_600),
                    ft.Column(controls=pedido_widgets, spacing=8),
                ],
                spacing=10,
            ),
            padding=16,
            bgcolor=C["surface"],
            border_radius=14,
            border=ft.Border(left=ft.BorderSide(1.5, "#fca5a5"), right=ft.BorderSide(1.5, "#fca5a5"), top=ft.BorderSide(1.5, "#fca5a5"), bottom=ft.BorderSide(1.5, "#fca5a5")),
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
            padding=ft.Padding(left=0, right=0, top=60, bottom=60),
        )

    def on_busca(e):
        filtro = e.control.value.strip().lower()
        grupos = cliente_service.obter_clientes_com_pendencias()
        if filtro:
            grupos = [g for g in grupos
                     if g["cliente"] and (
                         filtro in g["cliente"].nome.lower()
                         or filtro in g["cliente"].telefone)]
        lista_ref.current.controls = (
            [_build_card(g) for g in grupos] if grupos else [_empty_state()]
        )
        page.update()

    grupos_init = cliente_service.obter_clientes_com_pendencias()
    total_pendente = sum(g["total_pendente"] for g in grupos_init)
    qtd_pendentes = len(grupos_init)
    total_clientes = len(cliente_service.listar_clientes())

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
                        ft.Text(ref=total_ref, value=Formatters.formato_brl(total_pendente),
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
        padding=18,
        bgcolor="#fff1f2",
        border_radius=14,
        border=ft.Border(left=ft.BorderSide(1.5, "#fca5a5"), right=ft.BorderSide(1.5, "#fca5a5"), top=ft.BorderSide(1.5, "#fca5a5"), bottom=ft.BorderSide(1.5, "#fca5a5")),
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
        padding=18,
        bgcolor=C["surface"],
        border_radius=14,
        border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
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
            ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"xs": 12, "sm": 6}, controls=[card_total]),
                    ft.Column(col={"xs": 12, "sm": 6}, controls=[card_ativos]),
                ],
                spacing=16, run_spacing=12,
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(Icons.SEARCH, size=18, color=C["muted"]),
                        ft.TextField(
                            hint_text="Buscar por nome ou telefone...",
                            hint_style=ft.TextStyle(color=C["muted"], size=13),
                            border=ft.InputBorder.NONE,
                            expand=True, height=40, text_size=13,
                            content_padding=ft.Padding(left=0, right=0, top=0, bottom=0),
                            on_change=on_busca,
                            color=C["text"],
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=8, bottom=8),
                bgcolor=C["surface"],
                border_radius=12,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
            ),
            ft.Column(ref=lista_ref, controls=cards_init, spacing=16),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def view_estoque(estoque_service, produto_service: ProdutoService, page: ft.Page) -> ft.Control:
    """View de Estoque — controle de insumos como ração, medicamentos, etc."""
    from granja_manager.database.repositories import InsumoRepository
    from granja_manager.models import Insumo
    import uuid
    
    Icons = ft.icons
    insumo_repo = InsumoRepository()
    lista_ref  = ft.Ref[ft.Column]()
    busca_ref  = ft.Ref[ft.TextField]()

    # ── Diálogo de novo insumo ─────────────────────────────────────
    nome_field  = ft.TextField(label="Nome do insumo", hint_text="Ex: Ração, Vacina...", border_radius=8)
    unid_field  = ft.TextField(label="Unidade", hint_text="Ex: kg, litros, doses", border_radius=8)
    qtd_field   = ft.TextField(label="Quantidade inicial", value="0",
                               keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
    erro_ref    = ft.Ref[ft.Text]()

    def _get_insumos(filtro=""):
        """Busca insumos do Supabase."""
        if filtro:
            return insumo_repo.search(filtro)
        return insumo_repo.find_all()

    def _rebuild(filtro=""):
        """Reconstrói a lista de insumos."""
        insumos = _get_insumos(filtro)
        lista_ref.current.controls = (
            [_build_card(i) for i in insumos] if insumos else [_empty()]
        )
        page.update()

    def _empty():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(Icons.WAREHOUSE, size=48, color=C["muted"]),
                    ft.Text("Nenhum insumo cadastrado.", size=14, color=C["muted"]),
                    ft.Text("Clique em '+ Novo insumo' para começar.", size=12, color=C["muted"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding(0, 60, 0, 60),
        )

    def _build_card(insumo) -> ft.Container:
        """Constrói o card de um insumo."""
        iid = insumo["id"]
        nome = insumo["nome"]
        unidade = insumo["unidade"]
        quantidade = insumo["quantidade"]
        
        mov_field = ft.TextField(
            value="1", keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8, width=72, text_align=ft.TextAlign.CENTER,
        )
        status_ref = ft.Ref[ft.Text]()

        if quantidade == 0:
            estoque_color, estoque_label = C["danger"], "ZERO"
        elif quantidade < 5:
            estoque_color, estoque_label = C["warning"], "BAIXO"
        else:
            estoque_color, estoque_label = C["success"], "OK"

        def on_entrada(e, _id=iid, _qtd=quantidade):
            try:
                qtd = float(mov_field.value or 1)
                if qtd <= 0:
                    raise ValueError("Quantidade deve ser > 0")
                insumo_repo.atualizar_quantidade(_id, qtd)
                _rebuild(busca_ref.current.value or "")
            except ValueError as ex:
                status_ref.current.value = str(ex)
                page.update()

        def on_saida(e, _id=iid, _qtd=quantidade):
            try:
                qtd = float(mov_field.value or 1)
                if qtd <= 0:
                    raise ValueError("Quantidade deve ser > 0")
                if _qtd < qtd:
                    raise ValueError(f"Estoque insuficiente ({_qtd} {unidade})")
                insumo_repo.atualizar_quantidade(_id, -qtd)
                _rebuild(busca_ref.current.value or "")
            except ValueError as ex:
                status_ref.current.value = str(ex)
                page.update()

        def on_excluir(e, _id=iid):
            insumo_repo.delete(_id)
            _rebuild(busca_ref.current.value or "")

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(Icons.INVENTORY_2_OUTLINED,
                                                color=C["warning"], size=20),
                                width=44, height=44, border_radius=10,
                                bgcolor=C["warning_bg"], alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(nome, size=14, weight=ft.FontWeight.W_600,
                                            color=C["text"]),
                                    ft.Text(f"Unidade: {unidade}", size=12, color=C["muted"]),
                                ],
                                spacing=2, tight=True, expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(estoque_label, size=9,
                                                weight=ft.FontWeight.BOLD, color=C["white"]),
                                        ft.Text(f"{quantidade:.1f}", size=14,
                                                weight=ft.FontWeight.BOLD, color=C["white"]),
                                        ft.Text(unidade, size=9, color=C["white"]),
                                    ],
                                    spacing=0, tight=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                width=64, height=56, border_radius=10,
                                bgcolor=estoque_color, alignment=ft.Alignment(0, 0),
                            ),
                            ft.IconButton(
                                icon=Icons.DELETE_OUTLINE,
                                icon_color=C["danger"], icon_size=18,
                                tooltip="Excluir insumo",
                                on_click=on_excluir,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Qtd:", size=12, color=C["text_label"]),
                            mov_field,
                            _btn_filled("+ Entrada", Icons.ADD_CIRCLE, on_entrada,
                                        bgcolor=C["success"], text_color=C["white"]),
                            _btn_filled("− Saída", Icons.REMOVE_CIRCLE, on_saida,
                                        bgcolor=C["warning"], text_color=C["white"]),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                    ),
                    ft.Text(ref=status_ref, value="", size=11, color=C["danger"]),
                ],
                spacing=10,
            ),
            padding=16,
            bgcolor=C["surface"],
            border_radius=12,
            border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        )

    def on_salvar_insumo(e):
        """Salva um novo insumo no Supabase."""
        nome = nome_field.value.strip()
        unid = unid_field.value.strip() or "un."
        if not nome:
            erro_ref.current.value = "Informe o nome do insumo."
            page.update()
            return
        try:
            qtd = float(qtd_field.value.replace(",", ".") or 0)
        except ValueError:
            erro_ref.current.value = "Quantidade inválida."
            page.update()
            return
        
        novo_insumo = Insumo(
            id=str(uuid.uuid4()),
            nome=nome,
            unidade=unid,
            quantidade=qtd
        )
        
        if insumo_repo.create(novo_insumo):
            nome_field.value = unid_field.value = qtd_field.value = ""
            erro_ref.current.value = ""
            _fechar_dialogo(page, dialogo)
            _rebuild()
            page.update()
        else:
            erro_ref.current.value = "Erro ao salvar insumo"
            page.update()

    def on_fechar(e):
        _fechar_dialogo(page, dialogo)
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=C["surface"],
        title=ft.Text("Novo Insumo", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                nome_field, unid_field, qtd_field,
                ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
            ],
            spacing=12, tight=True, width=320,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=on_fechar),
            ft.FilledButton("Salvar", on_click=on_salvar_insumo,
                            style=ft.ButtonStyle(bgcolor=C["success"])),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def on_novo(e):
        nome_field.value = unid_field.value = ""
        qtd_field.value = "0"
        erro_ref.current.value = ""
        _abrir_dialogo(page, dialogo)

    def on_busca(e):
        _rebuild(e.control.value.strip())

    insumos_init = _get_insumos()

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Estoque de Insumos", size=24,
                                    weight=ft.FontWeight.BOLD, color=C["text"]),
                            ft.Text("Ração, medicamentos, vacinas e outros insumos.",
                                    size=13, color=C["text_label"]),
                        ],
                        spacing=4, expand=True,
                    ),
                    _btn_primary("Novo insumo", Icons.ADD, on_novo),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(Icons.SEARCH, size=18, color=C["muted"]),
                        ft.TextField(
                            ref=busca_ref,
                            hint_text="Buscar insumo...",
                            hint_style=ft.TextStyle(color=C["muted"], size=13),
                            border=ft.InputBorder.NONE,
                            expand=True, height=40, text_size=13,
                            content_padding=ft.Padding(0, 0, 0, 0),
                            on_change=on_busca,
                            color=C["text"],
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=8, bottom=8),
                bgcolor=C["surface"],
                border_radius=12,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
            ),
            ft.Column(
                ref=lista_ref,
                controls=[_build_card(i) for i in insumos_init] if insumos_init else [_empty()],
                spacing=12,
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def view_gastos(gasto_service: GastoService, page: ft.Page) -> ft.Control:
    """View de Gastos com CRUD completo."""
    Icons = ft.icons
    lista_ref = ft.Ref[ft.Column]()
    total_ref = ft.Ref[ft.Text]()

    def _total() -> float:
        return sum(g.valor for g in gasto_service.listar_gastos())

    def _build_card(gasto) -> ft.Container:
        def on_excluir(e, gid=gasto.id):
            gasto_service.deletar_gasto(gid)
            lista_ref.current.controls = _build_lista()
            total_ref.current.value = Formatters.formato_brl(_total())
            page.snack_bar = ft.SnackBar(ft.Text("Gasto removido com sucesso"))
            page.snack_bar.open = True
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
                                f"{gasto.categoria} • {Formatters.formato_data(gasto.data)}",
                                size=12, color=C["muted"],
                            ),
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                    ft.Text(Formatters.formato_brl(gasto.valor), size=15,
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
            padding=ft.Padding(left=18, right=18, top=14, bottom=14),
            bgcolor=C["surface"],
            border_radius=12,
            border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        )

    def _build_lista() -> list:
        gastos = gasto_service.listar_gastos()
        if not gastos:
            return [ft.Container(
                content=ft.Text("Nenhum gasto cadastrado.", size=13, color=C["muted"]),
                padding=ft.Padding(left=0, right=0, top=40, bottom=40),
                alignment=ft.Alignment(0, 0),
            )]
        return [_build_card(g) for g in gastos]

    desc_field = ft.TextField(label="Descrição", hint_text="Ex: Ração", border_radius=8)
    valor_field = ft.TextField(label="Valor (R$)", hint_text="Ex: 150.00",
                               keyboard_type=ft.KeyboardType.NUMBER, border_radius=8)
    categ_field = ft.TextField(label="Categoria", hint_text="Ex: Insumos", border_radius=8)
    erro_ref = ft.Ref[ft.Text]()

    def on_salvar(e):
        desc = desc_field.value.strip()
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

        try:
            gasto_service.criar_gasto(desc, categ, valor)
            desc_field.value = ""
            valor_field.value = ""
            categ_field.value = ""
            erro_ref.current.value = ""
            lista_ref.current.controls = _build_lista()
            total_ref.current.value = Formatters.formato_brl(_total())
            # Fecha diálogo sem page.update interno
            _fechar_dialogo(page, dialogo)
            page.snack_bar = ft.SnackBar(ft.Text("Gasto criado com sucesso!"))
            page.snack_bar.open = True
            # Um único page.update para tudo
            page.update()
        except Exception as ex:
            erro_ref.current.value = str(ex)
            page.update()

    def on_novo_gasto(e):
        desc_field.value = ""
        valor_field.value = ""
        categ_field.value = ""
        erro_ref.current.value = ""
        _abrir_dialogo(page, dialogo)

    def on_fechar_gasto(e):
        _fechar_dialogo(page, dialogo)
        page.update()

    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=C["surface"],
        title=ft.Text("Novo Gasto", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                desc_field, valor_field, categ_field,
                ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
            ],
            spacing=12, tight=True, width=340,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=on_fechar_gasto),
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
                                    ft.Text(ref=total_ref, value=Formatters.formato_brl(_total()),
                                           size=13, weight=ft.FontWeight.BOLD, color=C["danger"]),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=2, expand=True,
                    ),
                    _btn_primary("Novo gasto", Icons.ADD, on_novo_gasto),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Column(ref=lista_ref, controls=_build_lista(), spacing=12),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def view_pedidos(pedido_service: PedidoService, produto_service: ProdutoService, page: ft.Page) -> ft.Control:
    """View de Pedidos."""
    Icons = ft.icons
    lista_ref = ft.Ref[ft.Column]()

    def _rebuild(e=None):
        lista_ref.current.controls = _build_lista()
        page.update()

    def _tel_fmt(cliente_id: str) -> str:
        from granja_manager.services import ClienteService
        cliente_service = ClienteService()
        c = cliente_service.obter_cliente(cliente_id)
        if not c:
            return ""
        return Formatters.formato_telefone(c.telefone)

    def _nome_cliente(cliente_id: str) -> str:
        from granja_manager.services import ClienteService
        cliente_service = ClienteService()
        c = cliente_service.obter_cliente(cliente_id)
        if not c:
            return "Desconhecido"
        return c.nome

    def _badge(label, bg, color) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=11, color=color, weight=ft.FontWeight.W_600),
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            border_radius=20, bgcolor=bg,
        )

    def _build_card(ped) -> ft.Container:
        concluido = ped.concluido
        pago = ped.pago

        status_label = "Concluído" if concluido else "Pendente"
        status_bg = C["success_bg"] if concluido else "#fef3c7"
        status_color = C["success"] if concluido else C["warning"]
        pago_label = "Pago" if pago else "Não pago"
        pago_bg = C["success_bg"] if pago else C["danger_bg"]
        pago_color = C["success"] if pago else C["danger"]

        itens_txt = []
        for item in ped.itens:
            prod = produto_service.obter_produto(item.produto_id)
            nome_prod = prod.nome if prod else item.produto_id
            itens_txt.append(f"• {item.quantidade}× {nome_prod}")

        tel = _tel_fmt(ped.cliente_id)
        meta = (f"{tel} • " if tel else "") + Formatters.formato_data_hora(ped.data)

        def on_marcar_pago(e, pid=ped.id):
            pedido_service.marcar_pago(pid)
            _rebuild()

        def on_marcar_nao_pago(e, pid=ped.id):
            pedido_service.marcar_nao_pago(pid)
            _rebuild()

        def on_concluir(e, pid=ped.id):
            pedido_service.marcar_concluido(pid)
            _rebuild()

        def on_reabrir(e, pid=ped.id):
            pedido_service.reabrir_pedido(pid)
            _rebuild()

        def on_excluir_pedido(e, pid=ped.id):
            pedido_service.deletar_pedido(pid)
            _rebuild()

        botoes = []
        if pago:
            botoes.append(_btn_outline(
                "Marcar não pago", Icons.REMOVE_CIRCLE_OUTLINE, on_marcar_nao_pago,
            ))
            botoes.append(_btn_outline(
                "Reabrir", Icons.REFRESH, on_reabrir,
            ))
        else:
            botoes.append(_btn_filled(
                "Marcar pago", Icons.CHECK_CIRCLE_OUTLINE, on_marcar_pago,
            ))
            botoes.append(_btn_outline(
                "Concluir", Icons.CHECK, on_concluir,
            ))

        botoes.append(ft.IconButton(
            icon=Icons.DELETE_OUTLINE,
            icon_color=C["danger"],
            icon_size=18,
            tooltip="Excluir pedido",
            on_click=on_excluir_pedido,
        ))

        return ft.Container(
            content=ft.Column(
                controls=[
                    # ── nome + valor ───────────────────────────────
                    ft.Row(
                        controls=[
                            ft.Text(
                                _nome_cliente(ped.cliente_id),
                                size=17,
                                weight=ft.FontWeight.BOLD,
                                color=C["text"],
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    Formatters.formato_brl(ped.total),
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                    color=C["success"] if pago else C["danger"],
                                ),
                                padding=ft.Padding(left=12, right=0, top=0, bottom=0),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    # ── badges + meta ──────────────────────────────
                    ft.Row(
                        controls=[
                            _badge(status_label, status_bg, status_color),
                            _badge(pago_label, pago_bg, pago_color),
                            ft.Text(meta, size=12, color=C["muted"]),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        wrap=True,
                    ),
                    # ── itens ──────────────────────────────────────
                    ft.Column(
                        controls=[
                            ft.Text(t, size=13, color=C["text_label"])
                            for t in itens_txt
                        ],
                        spacing=2,
                    ),
                    # ── botões ─────────────────────────────────────
                    ft.Row(
                        controls=botoes,
                        spacing=6,
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            bgcolor=C["surface"],
            border_radius=12,
            border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
        )

    def _build_lista() -> list:
        pedidos = pedido_service.listar_pedidos()
        if not pedidos:
            return [ft.Container(
                content=ft.Text("Nenhum pedido registrado.", size=13, color=C["muted"]),
                padding=ft.Padding(left=0, right=0, top=40, bottom=40),
                alignment=ft.Alignment(0, 0),
            )]
        return [_build_card(p) for p in pedidos]

    # ── Campos do diálogo ──────────────────────────────────────────
    cliente_nome_field = ft.TextField(label="Nome do Cliente", hint_text="Ex: João Silva", border_radius=8)
    cliente_tel_field  = ft.TextField(label="Telefone", hint_text="Ex: 11987654321", border_radius=8)
    produtos_list      = produto_service.listar_produtos()
    itens_pedido_ref   = ft.Ref[ft.Column]()
    erro_pedido_text   = ft.Text(value="", color=C["white"], size=12)
    total_pedido_text  = ft.Text(value="Total: R$ 0,00", size=14,
                                 weight=ft.FontWeight.BOLD, color=C["success"])

    def _adicionar_item_pedido(prod_id, prod_nome, prod_preco):
        def handler(e):
            # Impede duplicata
            if itens_pedido_ref.current:
                for existing in itens_pedido_ref.current.controls:
                    if getattr(existing, "data", None) == prod_id:
                        return

            qtd_field = ft.TextField(
                label="Qtd",
                value="1",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=60,
                border_radius=8,
            )

            def on_remove(e):
                if itens_pedido_ref.current:
                    itens_pedido_ref.current.controls = [
                        c for c in itens_pedido_ref.current.controls
                        if getattr(c, "data", None) != prod_id
                    ]
                _calc_total_pedido()

            def on_change(e):
                _calc_total_pedido()

            qtd_field.on_change = on_change

            item_container = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(prod_nome, size=11, expand=True),
                        ft.Text(Formatters.formato_brl(prod_preco), size=11, width=60),
                        qtd_field,
                        ft.IconButton(
                            icon=Icons.DELETE_OUTLINE,
                            icon_color=C["danger"],
                            icon_size=16,
                            on_click=on_remove,
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                bgcolor=C["surface"],
                border_radius=6,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                data=prod_id,
            )
            if itens_pedido_ref.current is not None:
                itens_pedido_ref.current.controls.append(item_container)
            _calc_total_pedido()
        return handler

    def _calc_total_pedido():
        total = 0
        if itens_pedido_ref.current:
            for item in itens_pedido_ref.current.controls:
                for ctrl in item.content.controls:
                    if isinstance(ctrl, ft.TextField) and ctrl.label == "Qtd":
                        try:
                            qtd = int(ctrl.value or 1)
                            for p in produtos_list:
                                if p.id == item.data:
                                    total += p.preco * qtd
                        except Exception:
                            pass
        total_pedido_text.value = f"Total: {Formatters.formato_brl(total)}"
        page.update()

    def on_salvar_pedido(e):
        nome = cliente_nome_field.value.strip()
        tel  = cliente_tel_field.value.strip()

        if not nome or not tel:
            erro_pedido_text.value = "Informe nome e telefone."
            page.update()
            return

        if not itens_pedido_ref.current or not itens_pedido_ref.current.controls:
            erro_pedido_text.value = "Adicione pelo menos um produto."
            page.update()
            return

        itens_data = []
        for item in itens_pedido_ref.current.controls:
            for ctrl in item.content.controls:
                if isinstance(ctrl, ft.TextField) and ctrl.label == "Qtd":
                    try:
                        qtd = int(ctrl.value or 1)
                        for p in produtos_list:
                            if p.id == item.data:
                                # PedidoService.criar_pedido espera tuplas
                                # (produto_id, quantidade, preco_unitario)
                                itens_data.append((p.id, qtd, p.preco))
                    except Exception:
                        pass

        try:
            pedido_service.criar_pedido(nome, tel, itens_data)
            logger.info(f"Pedido criado com sucesso para {nome}")

            # Limpa campos
            cliente_nome_field.value = ""
            cliente_tel_field.value  = ""
            itens_pedido_ref.current.controls = []
            erro_pedido_text.value   = ""
            total_pedido_text.value  = "Total: R$ 0,00"

            # Reconstrói lista de pedidos na tela
            lista_ref.current.controls = _build_lista()

            # Fecha o diálogo — usa page.close() se disponível (Flet >= 0.23),
            # caso contrário manipula open + overlay manualmente
            if hasattr(page, "close"):
                logger.info("Fechando diálogo via page.close()")
                # Atualiza a lista antes de fechar
                page.update()
                page.close(dialogo_pedido)
            else:
                logger.info("Fechando diálogo via open=False + page.update()")
                dialogo_pedido.open = False
                page.update()

        except Exception as ex:
            logger.error(f"Erro ao criar pedido: {ex}")
            erro_pedido_text.value = str(ex)
            page.update()

    def on_fechar_dialogo_pedido(e):
        _fechar_dialogo(page, dialogo_pedido)
        page.update()

    def on_novo_pedido(e):
        cliente_nome_field.value = ""
        cliente_tel_field.value  = ""
        if itens_pedido_ref.current is not None:
            itens_pedido_ref.current.controls = []
        erro_pedido_text.value  = ""
        total_pedido_text.value = "Total: R$ 0,00"
        _abrir_dialogo(page, dialogo_pedido)

    dialogo_pedido = ft.AlertDialog(
        modal=True,
        bgcolor=C["surface"],
        title=ft.Text("Novo Pedido", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            controls=[
                ft.Text("Dados do Cliente", size=13, weight=ft.FontWeight.BOLD, color=C["text"]),
                cliente_nome_field,
                cliente_tel_field,
                ft.Divider(color=C["border"], height=16),
                ft.Text("Produtos (clique no botão +)", size=13, weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(p.nome, size=11, expand=True),
                                ft.Text(Formatters.formato_brl(p.preco), size=11, width=60),
                                _btn_outline("+", Icons.ADD,
                                             _adicionar_item_pedido(p.id, p.nome, p.preco)),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                        for p in produtos_list
                    ],
                    spacing=4,
                    height=120,
                    scroll=ft.ScrollMode.AUTO,
                ),
                ft.Divider(color=C["border"], height=16),
                ft.Text("Itens", size=13, weight=ft.FontWeight.BOLD, color=C["text"]),
                ft.Column(
                    ref=itens_pedido_ref,
                    controls=[],
                    spacing=4,
                    height=120,
                    scroll=ft.ScrollMode.AUTO,
                ),
                total_pedido_text,
                erro_pedido_text,
            ],
            spacing=8,
            tight=True,
            width=380,
            height=500,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=on_fechar_dialogo_pedido),
            ft.FilledButton("Criar Pedido", on_click=on_salvar_pedido,
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
                            ft.Text("Pedidos", size=24,
                                    weight=ft.FontWeight.BOLD, color=C["text"]),
                            ft.Text("Acompanhe e crie pedidos.",
                                   size=13, color=C["text_label"]),
                        ],
                        spacing=2, expand=True,
                    ),
                    _btn_primary("Novo pedido", Icons.ADD, on_novo_pedido),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Column(ref=lista_ref, controls=_build_lista(), spacing=12),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def view_login(auth_service, page: ft.Page, on_login_success, on_navigate) -> ft.Control:
    """View de Login"""
    Icons = ft.icons
    
    email_field = ft.TextField(label="Email", border_radius=8, 
                              keyboard_type=ft.KeyboardType.EMAIL)
    senha_field = ft.TextField(label="Senha", border_radius=8, 
                              password=True)
    erro_ref = ft.Ref[ft.Text]()
    
    def on_login(e):
        email = email_field.value.strip()
        senha = senha_field.value
        
        if not email or not senha:
            erro_ref.current.value = "Preencha todos os campos"
            page.update()
            return
        
        sucesso, usuario, msg_erro = auth_service.login(email, senha)
        
        if sucesso:
            logger.info(f"✅ Login bem-sucedido: {email}")
            page.snack_bar = ft.SnackBar(ft.Text(f"Bem-vindo, {usuario['nome']}!"))
            page.snack_bar.open = True
            on_login_success(usuario)
            page.update()
        else:
            erro_ref.current.value = msg_erro or "Email ou senha incorretos"
            page.update()
    
    def on_ir_cadastro(e):
        on_navigate("/cadastro")
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("🐔 Granja Santo Antonio", size=28, 
                                   weight=ft.FontWeight.BOLD, color=C["success"]),
                            ft.Text("Bem-vindo ao sistema de gestão", size=14, 
                                   color=C["text_label"]),
                        ],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=0, top=40, right=0, bottom=40),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            email_field,
                            senha_field,
                            ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
                            ft.Row(
                                controls=[_btn_primary("Entrar", Icons.LOGIN, on_login)],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=20, color=C["border"]),
                            ft.Row(
                                controls=[
                                    ft.Text("Não tem conta?", size=12, color=C["text_label"]),
                                    ft.Container(
                                        content=ft.Text("Cadastre-se aqui", size=12, 
                                                      color=C["success"],
                                                      weight=ft.FontWeight.BOLD),
                                        on_click=on_ir_cadastro,
                                        ink=True,
                                    ),
                                ],
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=16,
                        tight=True,
                        width=340,
                    ),
                    padding=40,
                    border_radius=14,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                    bgcolor=C["surface"],
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
        bgcolor=C["bg"],
        expand=True,
    )


def view_cadastro(auth_service, page: ft.Page, on_login_success, on_navigate) -> ft.Control:
    """View de Cadastro"""
    Icons = ft.icons
    
    nome_field = ft.TextField(label="Nome completo", border_radius=8)
    email_field = ft.TextField(label="Email", border_radius=8,
                              keyboard_type=ft.KeyboardType.EMAIL)
    senha_field = ft.TextField(label="Senha", border_radius=8, password=True)
    senha_conf_field = ft.TextField(label="Confirmar senha", border_radius=8, password=True)
    erro_ref = ft.Ref[ft.Text]()
    
    def on_cadastro(e):
        nome = nome_field.value.strip()
        email = email_field.value.strip()
        senha = senha_field.value
        senha_conf = senha_conf_field.value
        
        if not all([nome, email, senha, senha_conf]):
            erro_ref.current.value = "Preencha todos os campos"
            page.update()
            return
        
        if senha != senha_conf:
            erro_ref.current.value = "As senhas não coincidem"
            page.update()
            return
        
        sucesso, usuario_id, msg_erro = auth_service.cadastrar(email, nome, senha)
        
        if sucesso:
            logger.info(f"✅ Cadastro bem-sucedido: {email}")
            page.snack_bar = ft.SnackBar(ft.Text("Cadastro realizado com sucesso! Faça login."))
            page.snack_bar.open = True
            page.update()
            # Voltar para login
            page.route = "/login"
            page.update()
        else:
            erro_ref.current.value = msg_erro
            page.update()
    
    def on_ir_login(e):
        on_navigate("/login")
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("🐔 Granja Santo Antonio", size=28, 
                                   weight=ft.FontWeight.BOLD, color=C["success"]),
                            ft.Text("Criar nova conta", size=14, 
                                   color=C["text_label"]),
                        ],
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=0, top=40, right=0, bottom=40),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            nome_field,
                            email_field,
                            senha_field,
                            senha_conf_field,
                            ft.Text(ref=erro_ref, value="", color=C["danger"], size=12),
                            ft.Row(
                                controls=[_btn_primary("Cadastrar", Icons.PERSON_ADD, on_cadastro)],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=20, color=C["border"]),
                            ft.Row(
                                controls=[
                                    ft.Text("Já tem conta?", size=12, color=C["text_label"]),
                                    ft.Container(
                                        content=ft.Text("Faça login", size=12, 
                                                      color=C["success"],
                                                      weight=ft.FontWeight.BOLD),
                                        on_click=on_ir_login,
                                        ink=True,
                                    ),
                                ],
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=16,
                        tight=True,
                        width=340,
                    ),
                    padding=40,
                    border_radius=14,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                    bgcolor=C["surface"],
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
        bgcolor=C["bg"],
        expand=True,
    )


# ══════════════════════════════════════════════════════════════════
# APLICAÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════

def main(page: ft.Page):
    """Função principal da aplicação."""
    page.title = "Granja Manager"
    page.bgcolor = C["sidebar"]  # fundo verde cobre área do sidebar sem corte
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1100
    page.window.height = 800
    page.window.min_width = 360  # suporte mobile

    # ✅ Usando Supabase ao invés de SQLite local
    logger.info("Inicializando com Supabase...")

    from granja_manager.services import AuthService
    auth_service    = AuthService()
    cliente_service   = ClienteService()
    produto_service   = ProdutoService()
    pedido_service    = PedidoService()
    gasto_service     = GastoService()
    estoque_service   = EstoqueService()
    dashboard_service = DashboardService()
    
    # Estado de autenticação
    usuario_logado = [None]  # [usuario_dict ou None]
    
    def on_login_success(usuario):
        """Callback quando login é bem-sucedido."""
        usuario_logado[0] = usuario
        page.route = "/dashboard"
        _refresh_page()
    
    def on_logout():
        """Realiza logout do usuário."""
        auth_service.logout()
        usuario_logado[0] = None
        page.route = "/login"
        _refresh_page()
    
    def _refresh_page():
        """Atualiza a página com o novo roteamento."""
        def navigate(route: str):
            """Navega para uma rota específica."""
            page.route = route
            _refresh_page()
        
        if page.route == "/login":
            page.clean()
            page.add(view_login(auth_service, page, on_login_success, navigate))
        elif page.route == "/cadastro":
            page.clean()
            page.add(view_cadastro(auth_service, page, on_login_success, navigate))
        elif usuario_logado[0]:
            # Mostrar dashboard (logado)
            page.clean()
            inner_ref.current.content = get_view(current_route[0])
            page.add(main_layout)
            _atualizar_topbar_usuario()
            _rebuild_sidebar()
        else:
            # Redirecionar para login
            page.route = "/login"
            _refresh_page()
            return
    
    # Handler para mudança de rota
    def route_change(e):
        _refresh_page()
    
    page.on_route_change = route_change
    
    # Iniciar no login
    page.route = "/login"

    current_route     = ["dashboard"]
    sidebar_collapsed = [False]  # será ajustado após page.width estar disponível
    sidebar_ref       = ft.Ref[ft.Container]()
    inner_ref         = ft.Ref[ft.Container]()
    bottom_nav_ref    = ft.Ref[ft.Container]()
    topbar_ref        = ft.Ref[ft.Container]()

    MOBILE_BREAKPOINT = 600
    BOTTOM_NAV_H      = 64

    def _is_mobile() -> bool:
        return (page.width or 0) < MOBILE_BREAKPOINT

    def get_view(route: str) -> ft.Control:
        try:
            if route == "dashboard":
                return view_dashboard(dashboard_service, page, usuario_logado[0])
            elif route == "clientes_pendentes":
                return view_clientes_pendentes(cliente_service, page)
            elif route == "produtos":
                return view_produtos(produto_service, page)
            elif route == "estoque":
                return view_estoque(estoque_service, produto_service, page)
            elif route == "pedidos":
                return view_pedidos(pedido_service, produto_service, page)
            elif route == "gastos":
                return view_gastos(gasto_service, page)
            return view_dashboard(dashboard_service, page, usuario_logado[0])
        except Exception as e:
            logger.error(f"Erro ao gerar view: {e}")
            return ft.Container(
                content=ft.Text(f"Erro: {e}", color=C["danger"]),
                padding=20,
            )

    # ── Bottom nav (mobile) ────────────────────────────────────────
    def _build_bottom_nav() -> ft.Container:
        """Barra de navegação inferior para mobile."""
        route = current_route[0]

        def nav_btn(r, label, icon):
            active = r == route
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            icon,
                            size=22,
                            color=C["white"] if active else C["sidebar_muted"],
                        ),
                        ft.Text(
                            label,
                            size=10,
                            weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                            color=C["white"] if active else C["sidebar_muted"],
                        ),
                    ],
                    spacing=2,
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
                height=BOTTOM_NAV_H,
                alignment=ft.Alignment(0, 0),
                on_click=lambda e, rr=r: navigate(rr),
                ink=True,
                border_radius=0,
            )

        return ft.Container(
            ref=bottom_nav_ref,
            content=ft.Row(
                controls=[nav_btn(r, l, i) for r, l, i in NAV_ITEMS],
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            ),
            height=BOTTOM_NAV_H,
            bgcolor=C["sidebar"],
            border=ft.Border(top=ft.BorderSide(1, "#2d7a4a")),
            visible=_is_mobile(),
        )

    # ── Sidebar (desktop) ──────────────────────────────────────────
    def _rebuild_sidebar():
        collapsed = sidebar_collapsed[0]
        nova = build_sidebar(current_route[0], navigate, collapsed=collapsed, usuario=usuario_logado[0])
        sidebar_ref.current.content = nova.content
        sidebar_ref.current.width   = SIDEBAR_W_COLLAPSED if collapsed else SIDEBAR_W
        sidebar_ref.current.visible = not _is_mobile()

    def toggle_sidebar(e):
        sidebar_collapsed[0] = not sidebar_collapsed[0]
        _rebuild_sidebar()
        page.update()

    def navigate(route: str):
        current_route[0] = route
        inner_ref.current.content = get_view(route)
        _rebuild_sidebar()
        # Atualiza badge do sino (índice 3: toggle, nome, home, sino)
        topbar_ref.current.content.controls[3] = _build_bell()
        # Atualiza bottom nav highlight
        bottom_nav_ref.current.content = ft.Row(
            controls=[
                _make_bottom_nav_btn(r, l, i)
                for r, l, i in NAV_ITEMS
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )
        page.update()

    def _make_bottom_nav_btn(r, label, icon):
        active = r == current_route[0]
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=22,
                            color=C["white"] if active else C["sidebar_muted"]),
                    ft.Text(label, size=10,
                            weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                            color=C["white"] if active else C["sidebar_muted"]),
                ],
                spacing=2, tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            height=BOTTOM_NAV_H,
            alignment=ft.Alignment(0, 0),
            on_click=lambda e, rr=r: navigate(rr),
            ink=True,
            border_radius=0,
        )

    def _apply_responsive_layout():
        """Ajusta visibilidade e padding conforme tamanho da tela."""
        mobile = _is_mobile()

        # Colapsa sidebar ao entrar em mobile; expande ao voltar pro desktop
        if mobile and not sidebar_collapsed[0]:
            sidebar_collapsed[0] = True
            _rebuild_sidebar()
        elif not mobile and sidebar_collapsed[0]:
            sidebar_collapsed[0] = False
            _rebuild_sidebar()

        # Sidebar e topbar: visíveis só no desktop
        sidebar_ref.current.visible      = not mobile
        topbar_ref.current.visible       = not mobile
        mobile_header_ref.current.visible = mobile

        # Bottom nav: visível só no mobile
        bottom_nav_ref.current.visible = mobile

        # Padding do conteúdo: menor em mobile
        inner_ref.current.padding = (
            ft.Padding(12, 12, 12, BOTTOM_NAV_H + 8)
            if mobile
            else ft.Padding(28, 28, 28, 28)
        )

    def on_resize(e):
        _apply_responsive_layout()
        page.update()

    page.on_resized = on_resize

    # ── Sidebar ────────────────────────────────────────────────────
    # Inicia colapsada em mobile
    sidebar_collapsed[0] = _is_mobile()
    _init_collapsed = sidebar_collapsed[0]

    sidebar_body = ft.Container(
        ref=sidebar_ref,
        content=build_sidebar(current_route[0], navigate, collapsed=_init_collapsed, usuario=usuario_logado[0]).content,
        width=SIDEBAR_W_COLLAPSED if _init_collapsed else SIDEBAR_W,
        bgcolor=C["sidebar"],
        border=ft.Border(right=ft.BorderSide(1, C["border"])),
        visible=not _is_mobile(),
    )

    # ── Painel de alertas ──────────────────────────────────────────
    def _gerar_alertas() -> list:
        """Analisa dados da granja e gera lista de alertas contextuais."""
        alertas = []
        Icons = ft.icons

        # 1. Clientes com pagamento pendente
        pendencias = cliente_service.obter_clientes_com_pendencias()
        if pendencias:
            total_dev = sum(g["total_pendente"] for g in pendencias)
            alertas.append({
                "tipo": "danger",
                "icon": Icons.PERSON_OFF_OUTLINED,
                "titulo": f"{len(pendencias)} cliente(s) com pagamento pendente",
                "detalhe": f"Total a receber: {Formatters.formato_brl(total_dev)}",
                "acao": "clientes_pendentes",
            })

        # 2. Estoque baixo (≤ 5 unidades)
        try:
            produtos = produto_service.listar_produtos()
            baixos = [p for p in produtos if p.estoque <= 5]
            criticos = [p for p in baixos if p.estoque == 0]
            if criticos:
                nomes = ", ".join(p.nome for p in criticos[:3])
                alertas.append({
                    "tipo": "danger",
                    "icon": Icons.INVENTORY_2_OUTLINED,
                    "titulo": f"{len(criticos)} animal(is) sem unidades em estoque",
                    "detalhe": nomes + ("..." if len(criticos) > 3 else ""),
                    "acao": "produtos",
                })
            elif baixos:
                nomes = ", ".join(f"{p.nome} ({p.estoque})" for p in baixos[:3])
                alertas.append({
                    "tipo": "warning",
                    "icon": Icons.INVENTORY_2_OUTLINED,
                    "titulo": f"{len(baixos)} animal(is) com estoque baixo",
                    "detalhe": nomes + ("..." if len(baixos) > 3 else ""),
                    "acao": "produtos",
                })
        except Exception:
            pass

        # 3. Pedidos pendentes (não pagos) - DESABILITADO: usar Supabase
        # TODO: Implementar cálculo de pedidos no dashboard_service com Supabase
        try:
            # Comentado - SQLite foi removido, usar apenas Supabase
            pass
        except Exception:
            pass

        if not alertas:
            alertas.append({
                "tipo": "success",
                "icon": Icons.CHECK_CIRCLE_OUTLINE,
                "titulo": "Tudo certo por aqui!",
                "detalhe": "Nenhum alerta no momento.",
                "acao": None,
            })

        return alertas

    def _abrir_alertas(e):
        alertas = _gerar_alertas()

        cor_map = {
            "danger":  (C["danger"],  C["danger_bg"]),
            "warning": (C["warning"], C["warning_bg"]),
            "success": (C["success"], C["success_bg"]),
        }

        def _alerta_item(a):
            cor, bg = cor_map[a["tipo"]]
            def _on_click(e, rota=a["acao"]):
                if rota:
                    _fechar_dialogo(page, bs)
                    navigate(rota)
                    page.update()
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(a["icon"], size=20, color=cor),
                            width=40, height=40, border_radius=10,
                            bgcolor=bg, alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(a["titulo"], size=13,
                                        weight=ft.FontWeight.W_600, color=C["text"]),
                                ft.Text(a["detalhe"], size=11, color=C["muted"]),
                            ],
                            spacing=2, tight=True, expand=True,
                        ),
                        ft.Icon(ft.icons.CHEVRON_RIGHT, size=16, color=C["muted"])
                        if a["acao"] else ft.Container(width=0),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=14,
                bgcolor=C["surface"],
                border_radius=12,
                border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                on_click=_on_click if a["acao"] else None,
                ink=bool(a["acao"]),
            )

        total_alertas = sum(1 for a in alertas if a["tipo"] in ("danger", "warning"))
        badge_txt = f"{total_alertas} alerta(s) ativo(s)" if total_alertas else "Sem alertas"

        bs = ft.AlertDialog(
            modal=False,
            bgcolor=C["surface"],
            title=ft.Row(
                controls=[
                    ft.Icon(ft.icons.NOTIFICATIONS_OUTLINED,
                            color=C["sidebar"], size=20),
                    ft.Text("Central de Alertas", size=16,
                            weight=ft.FontWeight.BOLD, color=C["text"],
                            expand=True),
                    ft.Container(
                        content=ft.Text(badge_txt, size=11,
                                        color=C["warning"] if total_alertas else C["success"],
                                        weight=ft.FontWeight.W_600),
                        padding=ft.Padding(8, 4, 8, 4),
                        border_radius=20,
                        bgcolor=C["warning_bg"] if total_alertas else C["success_bg"],
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            content=ft.Column(
                controls=[_alerta_item(a) for a in alertas],
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                width=420,
                height=min(len(alertas) * 90, 420),
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda e: _fechar_dialogo(page, bs) or page.update())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        _abrir_dialogo(page, bs)

    def _build_bell(icon_color=None) -> ft.Control:
        alertas = _gerar_alertas()
        count = sum(1 for a in alertas if a["tipo"] in ("danger", "warning"))
        color = icon_color or C["text"]
        badge = ft.Container(
            content=ft.Text(str(count), size=9, color=C["white"],
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER),
            width=16, height=16, border_radius=8,
            bgcolor=C["danger"],
            alignment=ft.Alignment(0, 0),
            visible=count > 0,
            right=0, top=0,
        )
        return ft.Stack(
            controls=[
                ft.IconButton(
                    icon=ft.icons.NOTIFICATIONS_OUTLINED,
                    icon_color=color,
                    icon_size=22,
                    tooltip="Ver alertas",
                    on_click=_abrir_alertas,
                ),
                badge,
            ],
            width=40, height=40,
        )

    refresh_spinning = [False]

    # Refs para atualizar nome/iniciais do usuário após login
    topbar_iniciais_ref = ft.Ref[ft.Container]()
    topbar_nome_ref     = ft.Ref[ft.Text]()
    mobile_iniciais_ref = ft.Ref[ft.Container]()

    def _atualizar_topbar_usuario():
        u = usuario_logado[0]
        if not u:
            return
        nome     = u.get('nome', 'Usuário')
        iniciais = extrair_iniciais(nome)
        try:
            if topbar_iniciais_ref.current:
                topbar_iniciais_ref.current.content.value = iniciais
            if topbar_nome_ref.current:
                topbar_nome_ref.current.value = nome
            if mobile_iniciais_ref.current:
                mobile_iniciais_ref.current.content.value = iniciais
            page.update()
        except Exception as ex:
            logger.warning(f"Erro ao atualizar topbar: {ex}")

    def _do_refresh_topbar(e=None):
        if refresh_spinning[0]:
            return
        refresh_spinning[0] = True

        # 1. Mostra loading ring na thread principal
        inner_ref.current.content = ft.Column(
            controls=[
                ft.ProgressRing(width=40, height=40, stroke_width=3, color=C["sidebar"]),
                ft.Text("Atualizando...", size=13, color=C["muted"]),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        page.update()

        # 2. Carrega dados na thread principal (SQLite exige isso)
        nova_view = get_view(current_route[0])

        # 3. Delay visual e troca — tudo na thread principal via timer
        import threading, time

        def _mostrar():
            time.sleep(1.0)
            inner_ref.current.content = nova_view
            page.update()
            refresh_spinning[0] = False

        threading.Thread(target=_mostrar, daemon=True).start()

    topbar = ft.Container(
        ref=topbar_ref,
        content=ft.Row(
            controls=[
                # esquerda: toggle + nome
                ft.IconButton(
                    icon=ft.icons.SPACE_DASHBOARD_OUTLINED,
                    icon_color=C["text"],
                    icon_size=20,
                    tooltip="Expandir/colapsar menu",
                    on_click=toggle_sidebar,
                ),
                ft.Text("Granja Santo Antonio", size=13,
                        weight=ft.FontWeight.BOLD, color=C["text"],
                        expand=True),
                # direita: home(refresh) + sino + avatar
                ft.IconButton(
                    icon=ft.icons.HOME_OUTLINED,
                    icon_color=C["muted"],
                    icon_size=22,
                    tooltip="Atualizar página",
                    on_click=_do_refresh_topbar,
                ),
                _build_bell(),   # índice 3
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                ref=topbar_iniciais_ref,
                                content=ft.Text(
                                    extrair_iniciais(usuario_logado[0].get('nome')) if usuario_logado[0] else 'U',
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=C["white"]
                                ),
                                width=32, height=32, border_radius=16,
                                bgcolor=C["sidebar"],
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text(
                                ref=topbar_nome_ref,
                                value=usuario_logado[0].get('nome') if usuario_logado[0] else 'Usuário',
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=C["text"]
                            ),
                            ft.IconButton(
                                icon=ft.icons.LOGOUT,
                                icon_color=C["danger"],
                                icon_size=18,
                                tooltip="Fazer logout",
                                on_click=lambda e: on_logout(),
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                    border_radius=10,
                    border=ft.Border(left=ft.BorderSide(1, C["border"]), right=ft.BorderSide(1, C["border"]), top=ft.BorderSide(1, C["border"]), bottom=ft.BorderSide(1, C["border"])),
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=56,
        bgcolor=C["surface"],
        padding=ft.Padding(left=12, right=16, top=0, bottom=0),
        border=ft.Border(bottom=ft.BorderSide(1, C["border"])),
        visible=not _is_mobile(),
    )

    # ── Header mobile (só no celular) ─────────────────────────────
    mobile_header_ref = ft.Ref[ft.Container]()
    mobile_header = ft.Container(
        ref=mobile_header_ref,
        content=ft.Row(
            controls=[
                ft.Text("🐔", size=20),
                ft.Column(
                    controls=[
                        ft.Text("Granja Santo Antonio", size=13,
                                weight=ft.FontWeight.BOLD, color=C["white"]),
                        ft.Text("Gestão da granja", size=10, color=C["sidebar_muted"]),
                    ],
                    spacing=0, tight=True, expand=True,
                ),
                # home (refresh)
                ft.IconButton(
                    icon=ft.icons.HOME_OUTLINED,
                    icon_color=C["white"],
                    icon_size=22,
                    tooltip="Atualizar página",
                    on_click=_do_refresh_topbar,
                ),
                # sino
                _build_bell(C["white"]),
                # avatar
                ft.Container(
                    ref=mobile_iniciais_ref,
                    content=ft.Text(
                        extrair_iniciais(usuario_logado[0].get('nome')) if usuario_logado[0] else 'U',
                        size=11, weight=ft.FontWeight.BOLD, color=C["sidebar"]
                    ),
                    width=32, height=32, border_radius=16,
                    bgcolor=C["white"],
                    alignment=ft.Alignment(0, 0),
                ),
                # logout
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    icon_color=C["white"],
                    icon_size=20,
                    tooltip="Sair",
                    on_click=lambda e: on_logout(),
                ),
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=68,
        bgcolor=C["sidebar"],
        padding=ft.Padding(left=12, right=12, top=4, bottom=4),
        visible=_is_mobile(),
    )

    # ── Conteúdo principal ─────────────────────────────────────────
    mobile_init = _is_mobile()
    content_area = ft.Container(
        ref=inner_ref,
        content=None,
        padding=(
            ft.Padding(12, 12, 12, BOTTOM_NAV_H + 8)
            if mobile_init
            else ft.Padding(28, 28, 28, 28)
        ),
        expand=True,
    )

    right_panel = ft.Column(
        controls=[topbar, mobile_header, content_area],
        spacing=0,
        expand=True,
    )
    # Garante fundo branco no painel direito (page.bgcolor é verde para cobrir sidebar)
    right_panel_wrap = ft.Container(
        content=right_panel,
        bgcolor=C["bg"],
        expand=True,
    )

    # ── Bottom navigation (mobile) ─────────────────────────────────
    bottom_nav = _build_bottom_nav()

    # ── Layout principal com Stack para bottom nav sobreposto ──────
    # O Stack permite que a bottom nav fique "pinada" no rodapé
    # enquanto o conteúdo ocupa o restante da tela.
    desktop_row = ft.Row(
        controls=[sidebar_body, right_panel_wrap],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    main_layout = ft.Column(
        controls=[
            ft.Container(content=desktop_row, expand=True),
            bottom_nav,
        ],
        spacing=0,
        expand=True,
    )

    inner_ref.current.content = get_view(current_route[0])
    
    # Iniciar o sistema de roteamento
    _refresh_page()

    logger.info("Aplicação iniciada com sucesso")


if __name__ == "__main__":
    ft.app(target=main)