"""
Plano de Ação BPO — Avancis / Vinci Airports
Gerado do zero com paleta oficial Efcaz (#0E8FA3)
3 slides: Contexto + Etapas 1-3 + Etapas 4-5
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ─────────────────────────────────────────────────────────────
# Paleta Efcaz
# ─────────────────────────────────────────────────────────────
TEAL       = RGBColor(0x0E, 0x8F, 0xA3)   # cor institucional
TEAL_DARK  = RGBColor(0x09, 0x6A, 0x7A)   # hover / accent
TEAL_PALE  = RGBColor(0xE6, 0xF5, 0xF7)   # fundo card
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GRAY       = RGBColor(0x55, 0x65, 0x70)
DARK       = RGBColor(0x17, 0x20, 0x2A)
OFFWHITE   = RGBColor(0xF6, 0xFB, 0xFC)
BORDER_CLR = RGBColor(0xB2, 0xDE, 0xE5)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def rect(slide, x, y, w, h, fill_rgb, border_rgb=None, border_pt=0.75):
    s = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill_rgb
    if border_rgb:
        s.line.color.rgb = border_rgb
        s.line.width = Pt(border_pt)
    else:
        s.line.fill.background()
    return s


def tb(slide, text, x, y, w, h, size=11, bold=False,
       color=DARK, align=PP_ALIGN.LEFT, wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def tb_lines(slide, lines, x, y, w, h, wrap=True):
    """
    lines: list of dict(text, size, bold, color, align, space_before)
    """
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln.get('align', PP_ALIGN.LEFT)
        sb = ln.get('space_before', 0)
        if sb:
            p.space_before = Pt(sb)
        run = p.add_run()
        run.text = ln['text']
        run.font.size = Pt(ln.get('size', 11))
        run.font.bold = ln.get('bold', False)
        run.font.color.rgb = ln.get('color', DARK)
    return box

# ─────────────────────────────────────────────────────────────
# Componentes reutilizáveis
# ─────────────────────────────────────────────────────────────

def header_band(slide, title, subtitle):
    """Faixa de cabeçalho teal com título e subtítulo."""
    rect(slide, 0, 0, 10, 0.95, TEAL)
    tb(slide, title,    0.35, 0.07, 9.3, 0.47, size=21, bold=True,  color=WHITE)
    tb(slide, subtitle, 0.35, 0.57, 9.3, 0.34, size=9.5, bold=False, color=WHITE)


def metric_card(slide, x, y, w, h, label, value):
    """Card de métrica: fundo teal claro, borda teal, label + valor."""
    rect(slide, x, y, w, h, TEAL_PALE, TEAL, border_pt=1.0)
    # label pequeno no topo
    tb(slide, label, x+0.16, y+0.18, w-0.28, 0.42,
       size=8.5, bold=False, color=GRAY)
    # valor grande abaixo
    tb(slide, value, x+0.16, y+0.63, w-0.28, 1.2,
       size=16, bold=True, color=TEAL)


def action_card(slide, x, y, w, h, number, title, bullets):
    """
    Card de etapa: stripe lateral teal, badge, título e bullets.
    bullets: list of str
    """
    # fundo off-white com borda teal claro
    rect(slide, x, y, w, h, OFFWHITE, BORDER_CLR, border_pt=0.75)
    # stripe lateral esquerda
    rect(slide, x, y, 0.07, h, TEAL)

    # badge numerado
    bs = 0.40  # tamanho do badge
    bx, by = x + 0.16, y + 0.18
    rect(slide, bx, by, bs, bs, TEAL)
    tb(slide, number, bx, by + 0.03, bs, bs - 0.04,
       size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # título
    tb(slide, title, x + 0.65, y + 0.20, w - 0.75, 0.55,
       size=10.5, bold=True, color=TEAL_DARK)

    # separador fino
    rect(slide, x + 0.16, y + 0.77, w - 0.26, 0.01, BORDER_CLR)

    # bullets
    if bullets:
        lines = []
        for i, b in enumerate(bullets):
            lines.append({
                'text': '•  ' + b,
                'size': 9,
                'bold': False,
                'color': GRAY,
                'align': PP_ALIGN.LEFT,
                'space_before': 6 if i > 0 else 0,
            })
        tb_lines(slide, lines, x + 0.18, y + 0.83, w - 0.28, h - 0.93)


# ─────────────────────────────────────────────────────────────
# Criar apresentação
# ─────────────────────────────────────────────────────────────

prs = Presentation()
prs.slide_width  = Inches(10)
prs.slide_height = Inches(5.62)

# Encontrar layout em branco
blank = next(l for l in prs.slide_layouts if l.name == 'Blank')

# ═════════════════════════════════════════════════════════════
# SLIDE 1 — CONTEXTO DO PROJETO
# ═════════════════════════════════════════════════════════════

sl1 = prs.slides.add_slide(blank)
sl1.background.fill.solid()
sl1.background.fill.fore_color.rgb = WHITE

header_band(sl1,
    'Contexto do Projeto — Avancis / Vinci Airports',
    'Levantamento de necessidades  •  Reunião 11/Set/2026')

# Grid 3×2 de métricas
cx   = [0.28, 3.44, 6.60]   # x de cada coluna
cy   = [1.08, 3.18]         # y de cada linha
cw, ch = 3.0, 1.97

metrics = [
    ('Fornecedores na base SAP',        '5.634'),
    ('Contrato Efcaz',                   '500 fornecedores'),
    ('Fornecedores ativos em operação', '300 ativos'),
    ('Perguntas — Reforma Tributária',   '14 perguntas'),
    ('Campos novos não mapeados',        '~6 campos'),
    ('Prazo de saneamento',             'Antes da calculadora KPMG'),
]

for i, (label, value) in enumerate(metrics):
    row, col = divmod(i, 3)
    metric_card(sl1, cx[col], cy[row], cw, ch, label, value)


# ═════════════════════════════════════════════════════════════
# SLIDE 2 — PLANO DE AÇÃO: ETAPAS 1, 2 e 3
# ═════════════════════════════════════════════════════════════

sl2 = prs.slides.add_slide(blank)
sl2.background.fill.solid()
sl2.background.fill.fore_color.rgb = WHITE

header_band(sl2,
    'Plano de Ação — Etapas 1, 2 e 3',
    'Saneamento da Base  •  Avancis / Vinci Airports  •  Set/2026')

ax = [0.28, 3.44, 6.60]
ay, aw, ah = 1.07, 3.0, 4.37

action_card(sl2, ax[0], ay, aw, ah,
    '01',
    'Estruturação na plataforma',
    [
        'Criar linha de fornecimento específica, sem documentos, para esta fase inicial.',
        'Ativar apenas consulta de CNPJ na Receita Federal (status ativo/inativo).',
        'Bloquear a edição da linha pelo fornecedor.',
    ])

action_card(sl2, ax[1], ay, aw, ah,
    '02',
    'Campos dinâmicos obrigatórios',
    [
        'Incluir os ~6 novos campos da Reforma Tributária como campos dinâmicos.',
        'Dados bancários capturados na tela de identificação do fornecedor.',
        'Fornecedor acessa → altera cadastro → submete para análise.',
    ])

action_card(sl2, ax[2], ay, aw, ah,
    '03',
    'Comunicação BPO em massa',
    [
        'Envio de e-mail (BCC) para todos os fornecedores com link à plataforma.',
        'Comunicado estilo atualização cadastral com instrução de acesso.',
        'CNPJs sem retorno reportados à Avancis para tratativa.',
    ])


# ═════════════════════════════════════════════════════════════
# SLIDE 3 — PLANO DE AÇÃO: ETAPAS 4 e 5
# ═════════════════════════════════════════════════════════════

sl3 = prs.slides.add_slide(blank)
sl3.background.fill.solid()
sl3.background.fill.fore_color.rgb = WHITE

header_band(sl3,
    'Plano de Ação — Etapas 4 e 5',
    'Saneamento da Base  •  Avancis / Vinci Airports  •  Set/2026')

action_card(sl3, ax[0], ay, aw, ah,
    '04',
    'Análise e aprovação',
    [
        'A equipe analisa cada submissão e aprova o cadastro atualizado.',
        'Após aprovação, o fornecedor é vinculado à linha de fornecimento definitiva.',
        'Homologação completa com abertura dos documentos necessários.',
    ])

action_card(sl3, ax[1], ay, aw, ah,
    '05',
    'Validação bancária',
    [
        'Funcionalidade disponível na plataforma Efcaz.',
        '~R$0,50 por conta validada — ~R$600 para 1.000 fornecedores.',
        'Inclusão no escopo a ser alinhada internamente antes da apresentação.',
    ])

action_card(sl3, ax[2], ay, aw, ah,
    '→',
    'Próximo passo',
    [
        'Alinhar escopo internamente com Marielle antes de avançar.',
        'Apresentar o plano ao Elcio para validação e alinhamento de expectativas.',
    ])


# ─────────────────────────────────────────────────────────────
# Salvar
# ─────────────────────────────────────────────────────────────

output = (
    r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\clientes\vinci_airports"
    r"\VinciAirports_PlanoAcao_BPO_15-09-2026.pptx"
)
prs.save(output)
print(f"✅  Arquivo salvo: {output}")
print(f"    Slides gerados: {len(prs.slides)}")
