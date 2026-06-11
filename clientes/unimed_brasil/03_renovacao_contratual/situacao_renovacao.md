# Situação da Renovação — Unimed Brasil
**Atualizado em:** 02/06/2026

---

## Status

🔴 **Renovação bloqueada por dois pareceres técnicos**

---

## Histórico contratual

| Contrato | Valor | Vigência | Status |
|---|---|---|---|
| 8º Aditivo | R$ 2.405,80/mês | Até 27/10/2025 | **Vencido** — operação continua tacitamente |
| 9º Aditivo | A ser negociado | A definir | ⏳ Pendente aprovação |

---

## Barreiras ativas à renovação

### Barreira 1 — Privacidade (Caroline Sedano)

| Achado | Natureza | Ação necessária |
|---|---|---|
| Sem DPO substituto | Corrigível | Mariana nomeia Renato |
| Duas políticas de privacidade no site | Corrigível | Alison (tech) unifica |
| Armazenamento AWS/EUA | **Estrutural** | **DIREX aceita o risco formalmente** |

**Desbloqueador principal:** ata formal da DIREX aceitando o risco de transferência internacional.

### Barreira 2 — SI (Parecer #33/2026 — Risco Médio)

| Achado | Criticidade | Ação |
|---|---|---|
| DKIM não configurado | Média | Configurar |
| DMARC não configurado | Média | Configurar |
| PHP desatualizado | **Alta** | Atualizar imediatamente |
| Cabeçalhos HTTP ausentes | Baixa | Implementar |

**Desbloqueador:** preencher e devolver FB.583 (Plano de Ação) com datas comprometidas — prazo alvo: 09/06/2026.

---

## Argumentos de retenção

**1. Risco IRRELEVANTE pela própria régua da Unimed**
A avaliação interna classificou a Efcaz como IRRELEVANTE (10 pontos) — categoria mais baixa. O que está em jogo é formalização, não risco real.

**2. Dados tratados são apenas cadastrais**
CNPJ, nome, e-mail, certidões fiscais — nenhum dado de saúde, biometria ou informação sensível de cooperados.

**3. Custo de saída altíssimo**
7 módulos customizados + API bidirecional com o Pirâmide. Reconstrução = projeto de meses. Nenhum SRM genérico tem isso pronto.

**4. Parceria de 5 anos sem incidentes**
Contrato vencido em out/2025 — operação continuou por 7 meses sem fricção. Confiança mútua demonstrada na prática.

---

## Próximos passos

| # | Ação | Responsável | Prazo | Status |
|---|---|---|---|---|
| 1 | Preencher FB.583 com Mariana/AZI | Gabriel + Mariana | 09/06/2026 | ⏳ |
| 2 | Acompanhar encaminhamento para DIREX | Gabriel | Pós-reunião | ⏳ |
| 3 | Formalizar 9º Aditivo (quando aprovado) | Renato + Gabriel | A definir | ⏳ |
