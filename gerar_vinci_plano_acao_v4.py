# -*- coding: utf-8 -*-
"""
Plano de Ação BPO — Vinci Airports
Versão 4 (rev) — 16/09/2026
Paleta Efcaz: ciano #14B3CC + navy #3A3F5C
Capa em ciano | Conteúdo em branco | Logo nos slides de conteúdo
5 slides: Capa + Contexto + Etapas 1-3 + Etapas 4-5 + Cronograma
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ─────────────────────────────────────────────────────────────
# Paleta oficial Efcaz
# ─────────────────────────────────────────────────────────────
CIANO     = RGBColor(0x14, 0xB3, 0xCC)   # cor institucional principal
NAVY      = RGBColor(0x3A, 0x3F, 0x5C)   # contraste / badges
CIANO_ESC = RGBColor(0x0D, 0x8A, 0xA0)   # ciano escuro para banda inferior
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
FUNDO_ALT = RGBColor(0xF9, 0xF9, 0xF9)
TEXTO     = RGBColor(0x21, 0x25, 0x29)
TEXTO_SEC = RGBColor(0x69, 0x69, 0x69)
BORDA     = RGBColor(0xD1, 0xD9, 0xE0)

FONT = 'Barlow'
LOGO = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Geral\logo_efcaz_clean.png"


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
       color=TEXTO, align=PP_ALIGN.LEFT, wrap=True):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def tb_lines(slide, lines, x, y, w, h, wrap=True):
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
        run.font.name = FONT
        run.font.size = Pt(ln.get('size', 11))
        run.font.bold = ln.get('bold', False)
        run.font.color.rgb = ln.get('color', TEXTO)
    return box


# ─────────────────────────────────────────────────────────────
# Componentes
# ─────────────────────────────────────────────────────────────

def header_band(slide, title, subtitle):
    """Cabeçalho para slides de conteúdo: fundo branco, acento ciano vertical,
    título navy, subtítulo cinza, logo no canto superior direito."""
    # Acento vertical ciano
    rect(slide, 0.28, 0.12, 0.07, 0.78, CIANO)
    # Título
    tb(slide, title,    0.46, 0.12, 7.75, 0.46, size=18, bold=True,  color=NAVY)
    # Subtítulo
    tb(slide, subtitle, 0.46, 0.58, 7.75, 0.30, size=9,  bold=False, color=TEXTO_SEC)
    # Linha divisória
    rect(slide, 0.28, 0.97, 9.44, 0.02, BORDA)
    # Logo — fundo branco, logo sempre visível
    slide.shapes.add_picture(LOGO, Inches(8.48), Inches(0.09), width=Inches(1.30))


def metric_card(slide, x, y, w, h, label, value):
    """Card de métrica: fundo branco, borda sutil, tarja ciano no topo."""
    rect(slide, x, y, w, h, WHITE, BORDA, border_pt=1.0)
    rect(slide, x, y, w, 0.07, CIANO)   # tarja ciano
    tb(slide, label, x+0.16, y+0.20, w-0.28, 0.42, size=8.5, bold=False, color=TEXTO_SEC)
    tb(slide, value, x+0.16, y+0.67, w-0.28, 1.10, size=16, bold=True,  color=NAVY)


def action_card(slide, x, y, w, h, number, title, bullets):
    """Card de etapa: fundo alt, acento ciano lateral, badge navy."""
    rect(slide, x, y, w, h, FUNDO_ALT, BORDA, border_pt=0.75)
    rect(slide, x, y, 0.07, h, CIANO)   # acento lateral

    bs = 0.40
    bx, by = x + 0.16, y + 0.18
    rect(slide, bx, by, bs, bs, NAVY)
    tb(slide, number, bx, by + 0.03, bs, bs - 0.04,
       size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    tb(slide, title, x + 0.65, y + 0.20, w - 0.75, 0.55,
       size=10.5, bold=True, color=NAVY)

    rect(slide, x + 0.16, y + 0.77, w - 0.26, 0.01, BORDA)

    if bullets:
        lines = []
        for i, b in enumerate(bullets):
            lines.append({
                'text': '\u2022  ' + b,
                'size': 9,
                'bold': False,
                'color': TEXTO_SEC,
                'align': PP_ALIGN.LEFT,
                'space_before': 5 if i > 0 else 0,
            })
        tb_lines(slide, lines, x + 0.18, y + 0.83, w - 0.28, h - 0.93)


# ─────────────────────────────────────────────────────────────
# Apresentação
# ─────────────────────────────────────────────────────────────

prs = Presentation()
prs.slide_width  = Inches(10)
prs.slide_height = Inches(5.62)

blank = next(l for l in prs.slide_layouts if l.name == 'Blank')


# ═════════════════════════════════════════════════════════════
# SLIDE 1 — CAPA
# Fundo ciano (cor institucional), texto branco,
# banda navy na base, sem logo (evita problema de contraste)
# ═════════════════════════════════════════════════════════════

sl1 = prs.slides.add_slide(blank)
sl1.background.fill.solid()
sl1.background.fill.fore_color.rgb = CIANO

# Banda inferior navy
rect(sl1, 0, 4.50, 10, 1.12, NAVY)

# Barra vertical branca de acento — à esquerda do título
rect(sl1, 0.85, 1.10, 0.08, 2.15, WHITE)

# Título principal
tb(sl1, 'Saneamento da Base\nde Fornecedores',
   1.06, 1.10, 7.80, 2.10, size=32, bold=True, color=WHITE)

# Linha de separação entre título e subtítulo
rect(sl1, 1.06, 3.35, 3.60, 0.03, RGBColor(0xA0, 0xE2, 0xF0))

# Subtítulo
tb(sl1, 'Plano de Ação — BPO Documental',
   1.06, 3.50, 7.50, 0.46, size=13, bold=False, color=WHITE)

# Cliente e data — dentro da banda navy
tb(sl1, 'Vinci Airports  \u2022  Setembro / 2026',
   0.45, 4.65, 7.0, 0.40, size=10, bold=False, color=RGBColor(0xB0, 0xC8, 0xE8))

# Efcaz — canto inferior direito da banda navy
tb(sl1, 'efcaz.com.br',
   8.20, 4.65, 1.60, 0.40, size=9, bold=False, color=WHITE, align=PP_ALIGN.RIGHT)


# ═════════════════════════════════════════════════════════════
# SLIDE 2 — CONTEXTO DO PROJETO
# ═════════════════════════════════════════════════════════════

sl2 = prs.slides.add_slide(blank)
sl2.background.fill.solid()
sl2.background.fill.fore_color.rgb = WHITE

header_band(sl2,
    'Contexto do Projeto',
    'Levantamento de necessidades  \u2022  Vinci Airports  \u2022  Set/2026')

cx   = [0.28, 3.44, 6.60]
cy   = [1.10, 3.18]
cw, ch = 3.0, 1.95

metrics = [
    ('Fornecedores na base (SAP)',        '5.634'),
    ('Contrato Efcaz',                    '500 fornecedores'),
    ('Fornecedores ativos em operação',   '300 ativos'),
    ('Perguntas — Reforma Tributária',    '14 perguntas'),
    ('Campos novos não mapeados',         '~6 campos'),
    ('Prazo de saneamento',               'Antes da calculadora KPMG'),
]

for i, (label, value) in enumerate(metrics):
    row, col = divmod(i, 3)
    metric_card(sl2, cx[col], cy[row], cw, ch, label, value)


# ═════════════════════════════════════════════════════════════
# SLIDE 3 — PLANO DE AÇÃO: ETAPAS 1, 2 e 3
# ═════════════════════════════════════════════════════════════

sl3 = prs.slides.add_slide(blank)
sl3.background.fill.solid()
sl3.background.fill.fore_color.rgb = WHITE

header_band(sl3,
    'Plano de Ação — Etapas 1, 2 e 3',
    'Saneamento da Base  \u2022  Vinci Airports  \u2022  Set/2026')

ax = [0.28, 3.44, 6.60]
ay, aw, ah = 1.07, 3.0, 4.37

action_card(sl3, ax[0], ay, aw, ah,
    '01',
    'Estruturação na plataforma',
    [
        'Criação de linha de fornecimento temporária, sem documentos e sem buscas automáticas.',
        'Consulta de CNPJ (Receita Federal) para triagem de status ativo/inativo.',
        'Buscas automáticas completas ativadas após a conclusão do saneamento.',
    ])

action_card(sl3, ax[1], ay, aw, ah,
    '02',
    'Campos dinâmicos obrigatórios',
    [
        '~6 novos campos da Reforma Tributária incluídos como campos dinâmicos.',
        'Dados bancários (conta e PIX) obrigatórios na ficha de cadastro.',
        'Fornecedor não consegue submeter sem preencher todos os campos.',
    ])

action_card(sl3, ax[2], ay, aw, ah,
    '03',
    'Convite BPO — novo cadastro',
    [
        'Fornecedores convidados a se cadastrar como novos — não apenas a atualizar.',
        'Rastreamento via RD Station: envio, abertura e cadastro monitorados.',
        'Até 3 tentativas por CNPJ, com lembretes semanais.',
        'CNPJs sem retorno reportados à Vinci para decisão sobre tratativa.',
    ])


# ═════════════════════════════════════════════════════════════
# SLIDE 4 — PLANO DE AÇÃO: ETAPAS 4 e 5
# ═════════════════════════════════════════════════════════════

sl4 = prs.slides.add_slide(blank)
sl4.background.fill.solid()
sl4.background.fill.fore_color.rgb = WHITE

header_band(sl4,
    'Plano de Ação — Etapas 4 e 5',
    'Saneamento da Base  \u2022  Vinci Airports  \u2022  Set/2026')

action_card(sl4, ax[0], ay, aw, ah,
    '04',
    'Validação bancária',
    [
        'Validação de conta bancária e chave PIX como critério de bloqueio para submissão.',
        'Fornecedor sem dado bancário validado não avança no fluxo de cadastro.',
        'Validação realizada conforme os dados são preenchidos na plataforma.',
    ])

action_card(sl4, ax[1], ay, aw, ah,
    '05',
    'Análise e aprovação',
    [
        'Equipe analisa cada submissão individualmente.',
        'Aprovado: vinculado à linha definitiva e homologação completa.',
        'Aprovado com ressalva: pendência gerada para complemento.',
        'Reprovado definitivamente: fornecedor inativado (histórico preservado).',
    ])

action_card(sl4, ax[2], ay, aw, ah,
    '+',
    'Critérios de aprovação',
    [
        'Definidos em conjunto com a Vinci — não de forma unilateral.',
        'Referência: parâmetros em alinhamento com a KPMG.',
        'Consistência com as exigências da Reforma Tributária.',
    ])


# ═════════════════════════════════════════════════════════════
# SLIDE 5 — CRONOGRAMA E PRÓXIMOS PASSOS
# ═════════════════════════════════════════════════════════════

sl5 = prs.slides.add_slide(blank)
sl5.background.fill.solid()
sl5.background.fill.fore_color.rgb = WHITE

header_band(sl5,
    'Cronograma e Próximos Passos',
    'Saneamento da Base  \u2022  Vinci Airports  \u2022  Set/2026')

action_card(sl5, 0.28, 1.07, 4.5, 4.37,
    'T',
    'Cronograma',
    [
        '8 semanas a partir do OK formal e entrega da base de contatos.',
        'Início previsto: 2ª quinzena de setembro/2026.',
        'Entrega estimada: novembro/2026.',
        'Reuniões quinzenais de acompanhamento com a Vinci.',
        'Relatórios disponíveis a qualquer momento: envios × cadastros × aprovações.',
    ])

action_card(sl5, 5.22, 1.07, 4.5, 4.37,
    'P',
    'Para iniciarmos',
    [
        'Critérios de aprovação e reprovação (em alinhamento com a KPMG).',
        'Planilha de fornecedores com e-mails de contato atualizados.',
        'OK formal da Vinci para início do projeto.',
    ])


# ─────────────────────────────────────────────────────────────
# Salvar
# ─────────────────────────────────────────────────────────────

output = (
    r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\clientes\vinci_airports"
    r"\VinciAirports_PlanoAcao_BPO_16-09-2026.pptx"
)
prs.save(output)
print(f"Arquivo salvo: {output}")
print(f"Slides gerados: {len(prs.slides)}")
