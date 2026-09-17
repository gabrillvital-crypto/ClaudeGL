from pptx import Presentation

# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def get_para_text(paragraph):
    return "".join(run.text for run in paragraph.runs)

def set_para_text(paragraph, new_text):
    """Substitui o texto de um parágrafo preservando a formatação do primeiro run."""
    if paragraph.runs:
        paragraph.runs[0].text = new_text
        for run in paragraph.runs[1:]:
            run.text = ""

def get_shape_full_text(shape):
    if shape.has_text_frame:
        return "".join(get_para_text(p) for p in shape.text_frame.paragraphs)
    return ""

def replace_in_para(paragraph, substituicoes):
    texto = get_para_text(paragraph)
    for old, new in substituicoes.items():
        texto = texto.replace(old, new)
    set_para_text(paragraph, texto)

def replace_in_shape(shape, substituicoes):
    if not shape.has_text_frame:
        return
    for para in shape.text_frame.paragraphs:
        replace_in_para(para, substituicoes)

def delete_slides(prs, indices):
    """Remove slides pelos índices (0-based), do maior para o menor."""
    xml_slides = prs.slides._sldIdLst
    for idx in sorted(indices, reverse=True):
        xml_slides.remove(xml_slides[idx])


# ─────────────────────────────────────────
# Abrir template
# ─────────────────────────────────────────

prs = Presentation(
    r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Documentos\Plano de Ação Efcaz _ DockBrasil - modelo.pptx"
)

# Ordem dos slides no template (0-based):
# 0 = capa (não usar)
# 1 = Situação Atual / métricas  → SLIDE 1 — Contexto
# 2 = Contexto da Renovação / cards → SLIDE 2 — Plano Etapas 1–3
# 3 = Portfólio de Expansão          → SLIDE 3 — Plano Etapas 4–5
# 4,5,6 = outros (deletar)

s_contexto   = prs.slides[1]
s_plano_1    = prs.slides[2]
s_plano_2    = prs.slides[3]


# ═══════════════════════════════════════════════════════════════
# SLIDE 1 — CONTEXTO DO PROJETO (métricas)
# ═══════════════════════════════════════════════════════════════

for shape in s_contexto.shapes:
    if not shape.has_text_frame:
        continue
    nome  = shape.name
    texto = get_shape_full_text(shape)

    # Título principal
    if 'Situação Atual — Dock Brasil' in texto:
        replace_in_shape(shape, {'Situação Atual — Dock Brasil': 'Contexto do Projeto — Avancis / Vinci Airports'})

    # Subtítulo
    elif 'Diagnóstico do momento de renovação' in texto:
        replace_in_shape(shape, {'Diagnóstico do momento de renovação  •  Mai/2026': 'Levantamento de necessidades  •  Set/2026'})

    # Card 1 — Fornecedores no SAP
    elif 'Vencimento do contrato' in texto:
        for para in shape.text_frame.paragraphs:
            t = get_para_text(para)
            if 'Vencimento do contrato' in t:
                set_para_text(para, 'Fornecedores na base SAP')
            elif '31/mai/2026' in t:
                set_para_text(para, '5.634')

    # Card 2 — Contrato Efcaz
    elif 'Fornecedores ativos (95,4%)' in texto:
        for para in shape.text_frame.paragraphs:
            t = get_para_text(para)
            if 'Fornecedores ativos' in t:
                set_para_text(para, 'Contrato Efcaz')
            elif '763 / 800' in t:
                set_para_text(para, '500 fornecedores')

    # Card 3 — Fornecedores ativos hoje
    elif 'Usuários em uso vs. contratados' in texto:
        for para in shape.text_frame.paragraphs:
            t = get_para_text(para)
            if 'Usuários em uso' in t:
                set_para_text(para, 'Fornecedores ativos hoje')
            elif '25 / 15' in t:
                set_para_text(para, '300 ativos')

    # Card 4 — Reforma Tributária
    elif 'Bônus que expiram' in texto:
        for para in shape.text_frame.paragraphs:
            t = get_para_text(para)
            if 'Bônus que expiram' in t:
                set_para_text(para, 'Perguntas — Reforma Tributária')
            elif '8 usu. + 4 buscas' in t:
                set_para_text(para, '14 perguntas')

    # Card 5 — Campos novos
    elif '53 fornecedores' in texto:
        for para in shape.text_frame.paragraphs:
            t = get_para_text(para)
            if '53 fornecedores' in t:
                set_para_text(para, 'Campos novos não mapeados')
            elif 'com documentos vencidos' in t:
                set_para_text(para, '~6 campos')

    # Card 6 — Prazo
    elif 'Módulo de Avaliação (RFI)' in texto:
        for para in shape.text_frame.paragraphs:
            t = get_para_text(para)
            if 'Módulo de Avaliação' in t:
                set_para_text(para, 'Prazo de saneamento')
            elif 'Parado set/2025' in t:
                set_para_text(para, 'Antes da calculadora KPMG')


# ═══════════════════════════════════════════════════════════════
# SLIDE 2 — PLANO DE AÇÃO — Etapas 1, 2 e 3
# ═══════════════════════════════════════════════════════════════

for shape in s_plano_1.shapes:
    if not shape.has_text_frame:
        continue
    nome  = shape.name
    texto = get_shape_full_text(shape)

    # Título
    if 'Contexto da Renovação — O Momento de Decidir' in texto:
        replace_in_shape(shape, {'Contexto da Renovação — O Momento de Decidir': 'Plano de Ação — Etapas 1, 2 e 3'})

    # Badge "Atenção" — diferenciar pelos nomes dos shapes
    elif texto.strip() == 'Atenção':
        if '1115' in nome:
            set_para_text(shape.text_frame.paragraphs[0], '01')
        elif '1119' in nome:
            set_para_text(shape.text_frame.paragraphs[0], '02')
        elif '1123' in nome:
            set_para_text(shape.text_frame.paragraphs[0], '03')

    # Título card 1 — Etapa 1
    elif 'Acesso da equipe — garantir continuidade' in texto:
        replace_in_shape(shape, {'Acesso da equipe — garantir continuidade': 'Estruturação na plataforma'})

    # Corpo card 1
    elif '25 usuários ativos hoje' in texto or 'Renovar agora garante' in texto:
        paras = shape.text_frame.paragraphs
        conteudo = [
            'Criar linha de fornecimento específica, sem documentos, para esta fase inicial.',
            'Ativar apenas consulta de CNPJ na Receita Federal (validação de status ativo/inativo).'
        ]
        for i, para in enumerate(paras):
            set_para_text(para, conteudo[i] if i < len(conteudo) else '')

    # Título card 2 — Etapa 2
    elif 'Buscas automáticas — manter ativas' in texto:
        replace_in_shape(shape, {'Buscas automáticas — manter ativas': 'Campos dinâmicos obrigatórios'})

    # Corpo card 2
    elif 'CNDT, CND, CNPJ e FGTS' in texto or 'certidões continuam' in texto:
        paras = shape.text_frame.paragraphs
        conteudo = [
            'Incluir os ~6 novos campos da Reforma Tributária como campos dinâmicos obrigatórios.',
            'Dados bancários capturados diretamente na tela de identificação do fornecedor.'
        ]
        for i, para in enumerate(paras):
            set_para_text(para, conteudo[i] if i < len(conteudo) else '')

    # Título card 3 — Etapa 3
    elif 'Capacidade de fornecedores próxima do limite' in texto:
        replace_in_shape(shape, {'Capacidade de fornecedores próxima do limite': 'Comunicação BPO em massa'})

    # Corpo card 3
    elif '763 de 800' in texto or 'Expandir agora para 1.120' in texto:
        paras = shape.text_frame.paragraphs
        conteudo = [
            'Envio de e-mail (BCC) para todos os fornecedores com link de acesso à plataforma.',
            'CNPJs ativos sem retorno são reportados à Avancis para tratativa.'
        ]
        for i, para in enumerate(paras):
            set_para_text(para, conteudo[i] if i < len(conteudo) else '')


# ═══════════════════════════════════════════════════════════════
# SLIDE 3 — PLANO DE AÇÃO — Etapas 4 e 5
# ═══════════════════════════════════════════════════════════════

for shape in s_plano_2.shapes:
    if not shape.has_text_frame:
        continue
    nome  = shape.name
    texto = get_shape_full_text(shape)

    # Título
    if 'Portfólio de Expansão' in texto:
        replace_in_shape(shape, {'Portfólio de Expansão': 'Plano de Ação — Etapas 4 e 5'})

    # Números das seções
    elif '01. Expansão de usuários' in texto:
        replace_in_shape(shape, {'01. Expansão de usuários': '04. Análise e aprovação'})
    elif '02. Expansão de fornecedores' in texto:
        replace_in_shape(shape, {'02. Expansão de fornecedores': '05. Validação bancária'})
    elif '03. Buscas IBAMA' in texto:
        replace_in_shape(shape, {'03. Buscas IBAMA': '→  Apresentação ao cliente'})

    # Subtítulo seção 4
    elif '15 → 25 usuários' in texto:
        replace_in_shape(shape, {'15 → 25 usuários': 'Submissão recebida'})

    # Corpo seção 4
    elif 'Formaliza o que já é a realidade' in texto or 'Garante acesso contínuo' in texto or 'R$ 300,00/mês' in texto:
        paras = shape.text_frame.paragraphs
        conteudo = [
            'A equipe analisa cada submissão e aprova o cadastro atualizado.',
            'Após aprovação, o fornecedor é vinculado à linha de fornecimento definitiva.',
            'Homologação completa com abertura dos documentos necessários.',
            ''
        ]
        for i, para in enumerate(paras):
            set_para_text(para, conteudo[i] if i < len(conteudo) else '')

    # Subtítulo seção 5
    elif '800 → 1.120 (+40%)' in texto:
        replace_in_shape(shape, {'800 → 1.120 (+40%)': 'Plataforma habilitada'})

    # Corpo seção 5
    elif '763 ativos hoje' in texto or 'Expansão de 40%' in texto or 'Expansão planejada' in texto:
        paras = shape.text_frame.paragraphs
        conteudo = [
            'Funcionalidade de validação bancária disponível na plataforma.',
            '~R$0,50 por conta validada — ~R$600 para 1.000 fornecedores.',
            'Definição de inclusão no escopo a ser alinhada internamente.',
            ''
        ]
        for i, para in enumerate(paras):
            set_para_text(para, conteudo[i] if i < len(conteudo) else '')

    # Subtítulo seção →
    elif '3 consultas automáticas/mês' in texto:
        replace_in_shape(shape, {'3 consultas automáticas/mês': 'Validar plano com Elcio'})

    # Corpo seção →
    elif 'Certidão IBAMA: obrigatória' in texto or 'Automação protege' in texto or 'bonificado nesta proposta' in texto:
        paras = shape.text_frame.paragraphs
        conteudo = [
            'Apresentar este plano ao cliente para validação e alinhamento de expectativas.',
            'Garantir alinhamento sobre escopo, canais de comunicação e próximos marcos.',
            '',
            ''
        ]
        for i, para in enumerate(paras):
            set_para_text(para, conteudo[i] if i < len(conteudo) else '')

    # Rodapé / tagline
    elif '3 oportunidades concretas para esta renovação' in texto:
        replace_in_shape(shape, {'3 oportunidades concretas para esta renovação': 'Efcaz  |  Avancis / Vinci Airports  •  Set/2026'})


# ═══════════════════════════════════════════════════════════════
# Deletar slides desnecessários (capa + slides 5, 6, 7)
# Índices 0-based: 0 = capa, 4 = Por que Expandir, 5 = Proposta, 6 = encerramento
# ═══════════════════════════════════════════════════════════════

delete_slides(prs, [0, 4, 5, 6])


# ═══════════════════════════════════════════════════════════════
# Salvar
# ═══════════════════════════════════════════════════════════════

output = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\clientes\vinci_airports\VinciAirports_PlanoAcao_BPO_Set2026.pptx"
prs.save(output)
print(f"✅  Arquivo salvo em: {output}")
print(f"    Slides gerados: {len(prs.slides)}")
