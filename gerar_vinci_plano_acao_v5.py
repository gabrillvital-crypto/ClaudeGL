# -*- coding: utf-8 -*-
"""
Plano de Ação BPO — Vinci Airports
Versão 5 — 16/09/2026

Mudanças v5 vs v4:
  · Paleta: AZUL_CLARO como constante (era inline + valor inconsistente na capa)
  · Slide 2: frase introdutória de contexto antes dos cards de métrica
  · Slide 4: badge "i" (era "+") + título "Critérios de Aprovação" (capitalização)
  · Slide 5: section_card com header navy — sem badge numérico (mais adequado
              para conteúdo não-etapa). Título do card direito encurtado.
  · Slide 6 (NOVO): encerramento navy — "Ficou alguma dúvida?" + contato
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ─────────────────────────────────────────────────────────────
# Paleta oficial Efcaz
# ─────────────────────────────────────────────────────────────
CIANO      = RGBColor(0x14, 0xB3, 0xCC)   # cor institucional principal
NAVY       = RGBColor(0x3A, 0x3F, 0x5C)   # contraste / badges
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
FUNDO_ALT  = RGBColor(0xF9, 0xF9, 0xF9)
TEXTO      = RGBColor(0x21, 0x25, 0x29)
TEXTO_SEC  = RGBColor(0x69, 0x69, 0x69)
BORDA      = RGBColor(0xD1, 0xD9, 0xE0)
NAVY_DARK  = RGBColor(0x2A, 0x2F, 0x4C)   # navy mais escuro para card de encerramento
AZUL_CLARO = RGBColor(0xB0, 0xC8, 0xE8)   # texto secundário sobre fundo navy (era inline)

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
    """Cabeçalho padrão: acento ciano vertical, título navy, subtítulo cinza, logo."""
    rect(slide, 0.28, 0.12, 0.07, 0.78, CIANO)
    tb(slide, title,    0.46, 0.12, 7.75, 0.46, size=18, bold=True,  color=NAVY)
    tb(slide, subtitle, 0.46, 0.58, 7.75, 0.30, size=9,  bold=False, color=TEXTO_SEC)
    rect(slide, 0.28, 0.97, 9.44, 0.02, BORDA)
    slide.shapes.add_picture(LOGO, Inches(8.48), Inches(0.09), width=Inches(1.30))


def metric_card(slide, x, y, w, h, label, value):
    """Card de métrica: fundo branco, borda sutil, tarja ciano no topo."""
    rect(slide, x, y, w, h, WHITE, BORDA, border_pt=1.0)
    rect(slide, x, y, w, 0.07, CIANO)
    tb(slide, label, x+0.16, y+0.20, w-0.28, 0.42, size=8.5, bold=False, color=TEXTO_SEC)
    tb(slide, value, x+0.16, y+0.67, w-0.28, 1.10, size=16, bold=True,  color=NAVY)


def action_card(slide, x, y, w, h, number, title, bullets):
    """Card de etapa numerada: fundo alt, acento ciano lateral, badge navy."""
    rect(slide, x, y, w, h, FUNDO_ALT, BORDA, border_pt=0.75)
    rect(slide, x, y, 0.07, h, CIANO)

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


def section_card(slide, x, y, w, h, title, bullets):
    """Card de seção (sem badge numérico): fundo alt com borda, header navy,
    acento ciano lateral — para conteúdo de cronograma e próximos passos."""
    # 1. Card inteiro com borda (define a caixa externa)
    rect(slide, x, y, w, h, FUNDO_ALT, BORDA, border_pt=0.75)
    # 2. Header navy cobrindo o topo
    rect(slide, x, y, w, 0.60, NAVY)
    # 3. Acento ciano lateral (fica na frente de tudo — camada mais alta)
    rect(slide, x, y, 0.07, h, CIANO)
    # 4. Linha ciano separando header do corpo
    rect(slide, x + 0.07, y + 0.60, w - 0.07, 0.015, CIANO)
    # 5. Título no header
    tb(slide, title, x + 0.20, y + 0.13, w - 0.28, 0.40,
       size=11, bold=True, color=WHITE)

    if bullets:
        lines = []
        for i, b in enumerate(bullets):
            lines.append({
                'text': '\u2022  ' + b,
                'size': 9,
                'bold': False,
                'color': TEXTO_SEC,
                'align': PP_ALIGN.LEFT,
                'space_before': 6 if i > 0 else 0,
            })
        tb_lines(slide, lines, x + 0.18, y + 0.72, w - 0.28, h - 0.82)


# ─────────────────────────────────────────────────────────────
# Apresentação
# ─────────────────────────────────────────────────────────────

prs = Presentation()
prs.slide_width  = Inches(10)
prs.slide_height = Inches(5.62)

blank = next(l for l in prs.slide_layouts if l.name == 'Blank')


# ═════════════════════════════════════════════════════════════
# SLIDE 1 — CAPA
# Fundo ciano, texto branco, banda navy na base
# ═════════════════════════════════════════════════════════════

sl1 = prs.slides.add_slide(blank)
sl1.background.fill.solid()
sl1.background.fill.fore_color.rgb = CIANO

# Banda inferior navy
rect(sl1, 0, 4.50, 10, 1.12, NAVY)

# Barra vertical branca de acento
rect(sl1, 0.85, 1.10, 0.08, 2.15, WHITE)

# Título principal
tb(sl1, 'Saneamento da Base\nde Fornecedores',
   1.06, 1.10, 7.80, 2.10, size=32, bold=True, color=WHITE)

# Linha de separação (consistente: AZUL_CLARO)
rect(sl1, 1.06, 3.35, 3.60, 0.03, AZUL_CLARO)

# Subtítulo
tb(sl1, 'Plano de Ação — BPO Documental',
   1.06, 3.50, 7.50, 0.46, size=13, bold=False, color=WHITE)

# Cliente e data — dentro da banda navy
tb(sl1, 'Vinci Airports  \u2022  Setembro / 2026',
   0.45, 4.65, 7.0, 0.40, size=10, bold=False, color=AZUL_CLARO)

# Rodapé direito
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

# Frase introdutória de contexto — ausente no v4
tb(sl2,
   'Levantamento realizado junto ao time Vinci em set/2026. '
   'Os dados abaixo embasam o escopo, os critérios e o prazo do projeto.',
   0.28, 1.07, 9.44, 0.28, size=8.5, bold=False, color=TEXTO_SEC)

# Cards deslocados +0.32 para acomodar o texto introdutório
cx      = [0.28, 3.44, 6.60]
cy      = [1.42, 3.48]   # era [1.10, 3.18]
cw, ch  = 3.0, 1.90      # ch reduzido 0.05 para manter margem inferior

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
# (sem alterações de conteúdo)
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
# Mudança: badge "+" → "i" | título com A maiúsculo
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
    'Análise e Aprovação',
    [
        'Equipe analisa cada submissão individualmente.',
        'Aprovado: vinculado à linha definitiva e homologação completa.',
        'Aprovado com ressalva: pendência gerada para complemento.',
        'Reprovado definitivamente: fornecedor inativado (histórico preservado).',
    ])

# Era badge "+": substituído por "i" (informação complementar, não etapa numerada)
action_card(sl4, ax[2], ay, aw, ah,
    'i',
    'Critérios de Aprovação',
    [
        'Definidos em conjunto com a Vinci — não de forma unilateral.',
        'Referência: parâmetros em alinhamento com a KPMG.',
        'Consistência com as exigências da Reforma Tributária.',
    ])


# ═════════════════════════════════════════════════════════════
# SLIDE 5 — CRONOGRAMA E PRÓXIMOS PASSOS
# Mudança: section_card (header navy, sem badge numérico)
# ═════════════════════════════════════════════════════════════

sl5 = prs.slides.add_slide(blank)
sl5.background.fill.solid()
sl5.background.fill.fore_color.rgb = WHITE

header_band(sl5,
    'Cronograma e Próximos Passos',
    'Saneamento da Base  \u2022  Vinci Airports  \u2022  Set/2026')

section_card(sl5, 0.28, 1.07, 4.50, 4.37,
    'Cronograma estimado',
    [
        '8 semanas a partir do OK formal e entrega da base de contatos.',
        'Início previsto: 2\u00aa quinzena de setembro/2026.',
        'Entrega estimada: novembro/2026.',
        'Reuniões quinzenais de acompanhamento com a Vinci.',
        'Relatórios disponíveis a qualquer momento: envios \u00d7 cadastros \u00d7 aprovações.',
    ])

section_card(sl5, 5.22, 1.07, 4.50, 4.37,
    'Para iniciarmos',
    [
        'Critérios de aprovação e reprovação (em alinhamento com a KPMG).',
        'Planilha de fornecedores com e-mails de contato atualizados.',
        'OK formal da Vinci para início do projeto.',
    ])


# ═════════════════════════════════════════════════════════════
# SLIDE 6 (NOVO) — ENCERRAMENTO
# Fundo navy, padrão "Ficou alguma dúvida?" do deck Efcaz
# ═════════════════════════════════════════════════════════════

sl6 = prs.slides.add_slide(blank)
sl6.background.fill.solid()
sl6.background.fill.fore_color.rgb = NAVY

# Barra ciano no topo (espelhando a banda navy da capa)
rect(sl6, 0, 0, 10, 0.20, CIANO)

# Acento vertical branco (espelhando a capa)
rect(sl6, 0.85, 1.35, 0.08, 1.80, WHITE)

# Título
tb(sl6, 'Ficou alguma dúvida?',
   1.06, 1.35, 7.50, 0.68, size=28, bold=True, color=WHITE)

# Subtítulo
tb(sl6,
   'Estamos prontos para iniciar assim que recebermos o alinhamento da Vinci.',
   1.06, 2.05, 7.50, 0.40, size=10.5, bold=False, color=AZUL_CLARO)

# Linha divisória
rect(sl6, 1.06, 2.58, 5.20, 0.025, RGBColor(0x55, 0x60, 0x80))

# Card de contato (navy mais escuro, borda sutil)
rect(sl6, 0.85, 3.05, 5.00, 2.00, NAVY_DARK, BORDA, border_pt=0.75)
rect(sl6, 0.85, 3.05, 5.00, 0.07, CIANO)   # tarja ciano no topo do card

tb_lines(sl6, [
    {'text': 'Gabriel Vital',
     'size': 14, 'bold': True, 'color': WHITE},
    {'text': 'Customer Success Specialist — Efcaz',
     'size': 9, 'bold': False, 'color': AZUL_CLARO, 'space_before': 5},
    {'text': 'gabriel.vital@efcaz.com.br',          # [A CONFIRMAR] e-mail corporativo
     'size': 9, 'bold': False, 'color': CIANO, 'space_before': 12},
    {'text': 'efcaz.com.br',
     'size': 9, 'bold': False, 'color': AZUL_CLARO, 'space_before': 5},
], 1.08, 3.28, 4.60, 1.65)

# Rodapé direito
tb(sl6, 'efcaz.com.br',
   8.20, 5.22, 1.60, 0.32, size=9, bold=False, color=WHITE, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────
# Salvar  (nova cópia — nunca sobrescrever)
# ─────────────────────────────────────────────────────────────

output = (
    r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\clientes\vinci_airports"
    r"\VinciAirports_PlanoAcao_BPO_16-09-2026_v2.pptx"
)
prs.save(output)
print(f"Arquivo salvo: {output}")
print(f"Slides gerados: {len(prs.slides)}")
