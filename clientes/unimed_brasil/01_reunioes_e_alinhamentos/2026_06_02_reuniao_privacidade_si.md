# Reunião — Privacidade de Dados + Segurança da Informação
**Data:** 02/06/2026 (tarde)
**Tipo:** Reunião estratégica — renovação em risco (dois pareceres técnicos)
**Sentimento:** ✅ Reunião realizada — transcrição pendente de envio

---

## Participantes

| Empresa | Participante | E-mail |
|---|---|---|
| Unimed Brasil | Amanda Franqueiro Soares | homologacaobrasil@unimed.coop.br |
| Unimed Brasil | Caroline Cariati Sedano | caroline.sedano@unimed.coop.br |
| Efcaz | Gabriel | — |
| Efcaz | Renato Pedroso | renato.pedroso@efcaz.com.br |
| AZI (parceira técnica Efcaz) | Mariana Benjamin Costa | mariana.costa@azi.com.br |

---

## Contexto

Contrato vencido desde out/2025 (8º Aditivo — R$ 2.405,80/mês). Operação continua tacitamente há 7+ meses. O processo de renovação desencadeou avaliação PPD & SI pela Unimed, resultando em **dois pareceres técnicos** que bloqueiam a renovação formal.

---

## Frente 1 — Privacidade (Caroline Sedano / Gestão de Privacidade)

| # | Achado | Natureza | Status |
|---|---|---|---|
| 1 | Sem DPO substituto (campo N/A no questionário) | Corrigível | Mariana nomeia Renato como substituto |
| 2 | Duas políticas de privacidade no site da Efcaz | Corrigível | Alison (tech) acionado para unificar |
| 3 | Armazenamento AWS/EUA — vedado por política interna Unimed | **Estrutural** | DIREX precisa aceitar o risco formalmente |

**Desbloqueador:** DIREX aceita o risco → envia ata → Plano de Ação vinculado ao contrato.

---

## Frente 2 — Segurança da Informação (Parecer #33/2026)

**Classificação Unimed:** RISCO MÉDIO
**Emitido por:** Celso de Almeida Polvora Junior + Gabrielly de Andrade Pechin + Odilon de Oliveira

| Achado | Criticidade |
|---|---|
| DKIM não configurado | Média |
| DMARC não configurado | Média |
| PHP desatualizado | Alta — *"atualização imediata"* |
| Cabeçalhos HTTP de segurança ausentes | Baixa |
| Exposição de informações do servidor | Baixa |
| Vulnerabilidades detectadas (pentest) | Baixa |

**Positivo:** HTTPS obrigatório ✅ + questionário FB.906 totalmente preenchido ✅

**Desbloqueador:** preencher e devolver o Plano de Ação (FB.583 REV04) com datas comprometidas. Mariana/AZI no circuito desde 12:03 de 02/06.

---

## Argumentos centrais usados na reunião

> **AWS/DIREX:** "Os dados que tratamos são exclusivamente cadastrais de fornecedores — CNPJ, nome, e-mail, certidões fiscais. Nenhum dado de saúde. A própria régua da Unimed classificou o risco como IRRELEVANTE (10 pontos). O que pedimos é a formalização da aceitação, procedimento que a política interna de vocês prevê."

> **Custo de saída:** "Sair da Efcaz não é trocar de SaaS. São 7 módulos customizados + API bidirecional com o Pirâmide. O custo de reconstrução supera em muito o risco classificado como irrelevante."

> **SI:** "Já temos nossa especialista técnica (Mariana/AZI) analisando os achados. Saímos daqui com um prazo comprometido para devolver o Plano de Ação preenchido."

---

## Perguntas estratégicas

1. "Qual é o processo formal para a DIREX registrar a aceitação de risco — formulário específico, ata de reunião ou e-mail da Caroline basta?"
2. "Qual o prazo esperado para a resposta da DIREX após o encaminhamento?"
3. "Para o Plano de Ação de SI, qual o prazo máximo aceitável para devolução do formulário preenchido?"
4. "Além desses pontos, existe outra barreira para a renovação?"

---

## Alerta contratual

Renato deve sinalizar intenção de formalizar o **9º Aditivo** — não sair sem definir próximo passo com data.

---

## Plano de Ação (pós-reunião)

| # | Ação | Responsável | Prazo | Status |
|---|---|---|---|---|
| 1 | Registrar reunião no CustomerX + e-mail follow-up | Gabriel | 1–2 dias úteis | ⏳ |
| 2 | Preencher Plano de Ação FB.583 com Mariana/AZI | Gabriel + Mariana | Até 09/06/2026 (5 dias úteis) | ⏳ |
| 3 | Iniciar 9º Aditivo (se aprovado na reunião) | Renato + Gabriel | A definir | ⏳ |
| 4 | Acompanhar encaminhamento para DIREX | Gabriel | Após reunião | ⏳ |

---

> ✅ Reunião realizada em 02/06/2026. Transcrição a ser enviada por Gabriel — resumo completo e follow-up pendentes.
