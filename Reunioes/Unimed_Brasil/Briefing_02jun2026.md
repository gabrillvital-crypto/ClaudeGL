# Briefing — Unimed Brasil
**Data:** 02/06/2026 (tarde)
**Tipo:** Reunião de Privacidade + SI — Renovação contratual em risco
**Participantes Efcaz:** Gabriel + Renato Pedroso
**Participantes Unimed:** Amanda Franqueiro Soares + Caroline Cariati Sedano

---

## Contexto rápido

Contrato vencido desde out/2025 (8º Aditivo — R$2.405,80/mês). Operação continua tacitamente. Processo de renovação desencadeou avaliação PPD & SI pela Unimed Brasil. Resultado: **duas avaliações distintas com achados que bloqueiam a renovação**.

---

## Documentos recebidos (cronologia)

| Data | Documento | Origem | Foco |
|---|---|---|---|
| 01/06 (e-mail) | Parecer de Privacidade — Caroline Sedano | Gestão de Privacidade de Dados | DPO substituto + duas políticas + AWS/EUA → DIREX |
| 02/06 (anexo) | Parecer #33/2026 (PDF) | SI — Celso + Gabrielly + Odilon | Risco Médio: DKIM/DMARC, PHP, HTTP headers, pentest |
| 02/06 (anexo) | Plano de Ação FB.583 REV04 (DOC) | Homologação — Amanda | Template em branco para Efcaz preencher e devolver |

---

## Frente 1 — Privacidade (Caroline Sedano)

| # | Achado | Natureza | Status |
|---|---|---|---|
| 1 | Sem DPO substituto | Corrigível | Mariana (AZI) vai nomear Renato |
| 2 | Duas políticas de privacidade no site | Corrigível | Alison (tech) acionado |
| 3 | Armazenamento AWS/EUA — vedado por política interna | Estrutural | DIREX precisa aceitar o risco formalmente |

**Desbloqueador:** DIREX aceita o risco → envia ata para Gestão de Privacidade → Plano de Ação vinculado ao contrato.

---

## Frente 2 — Segurança da Informação (Parecer #33/2026)

**Classificação: Risco Médio**

| Achado | Criticidade |
|---|---|
| DKIM não configurado | Média |
| DMARC não configurado | Média |
| PHP desatualizado | Alta — "atualização imediata" |
| Cabeçalhos HTTP de segurança ausentes | Baixa |
| Exposição de informações do servidor | Baixa |
| Vulnerabilidades detectadas (pentest) | Baixa |

Positivo: HTTPS obrigatório ✅ + FB.906 completo ✅

**Desbloqueador:** preencher e devolver o Plano de Ação (FB.583) com datas comprometidas. Mariana (AZI) já está no circuito desde hoje 12:03.

---

## Argumentos centrais

**Sobre o risco AWS/DIREX:**
> "Os dados que tratamos são exclusivamente cadastrais de fornecedores — CNPJ, nome, e-mail, certidões fiscais. Nenhum dado de saúde. A própria régua da Unimed classificou o risco de privacidade como IRRELEVANTE (10 pontos). O que pedimos é a formalização da aceitação, procedimento que a política interna de vocês prevê."

**Custo de saída:**
> "Sair da Efcaz não é trocar de SaaS. São 7 módulos customizados + API bidirecional com o Pirâmide. O custo de reconstrução supera em muito o risco classificado como irrelevante."

**Sobre os achados de SI:**
> "Já temos nossa especialista técnica (Mariana/AZI) analisando os achados. Saímos daqui com um prazo comprometido para devolver o Plano de Ação preenchido."

---

## Perguntas estratégicas para a reunião

1. "Qual é o processo formal para a DIREX registrar a aceitação de risco — formulário específico, ata de reunião ou e-mail da Caroline basta?"
2. "Qual o prazo esperado para a resposta da DIREX após o encaminhamento?"
3. "Para o Plano de Ação de SI, qual o prazo máximo aceitável para devolução do formulário preenchido?"
4. "Além desses pontos, existe outra barreira para a renovação?"

---

## Alerta: regularização contratual

Renato deve sinalizar intenção de formalizar o **9º Aditivo** — não sair sem definir próximo passo com data.

---

## Pós-reunião — acionar

- `/follow-up` — registrar no CustomerX + e-mail para Amanda e Caroline
- Preencher Plano de Ação (FB.583) com Mariana/AZI
- Iniciar 9º Aditivo se aprovado

---

> ⏳ Resumo pós-call pendente — Gabriel retorna após a reunião.
