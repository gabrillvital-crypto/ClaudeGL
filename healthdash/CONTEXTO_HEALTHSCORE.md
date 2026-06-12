# Health Score — Contexto e Modelo

**Iniciado em:** 11/06/2026
**Status:** Em pausa — modelo definido, implementação pendente

---

## Objetivo

Dashboard interno para Gabriel Vital (CS Specialist — Efcaz) monitorar a saúde da carteira de clientes ongoing.

**Escopo:**
- Uso: interno, monitoramento da carteira
- Formato: dashboard (React, similar ao Zurich)
- Abordagem: modelar o HS ideal → mapear o que está disponível → implementar

---

## Modelo de Health Score

**Escala:** 0–100

| Score | Status |
|---|---|
| 80–100 | 🟢 Saudável |
| 60–79 | 🟡 Em atenção |
| 0–59 | 🔴 Em risco |

---

### Dimensão 1 — Adoção (30%)

| Métrica | Peso | 🟢 100pts | 🟡 70pts | 🔴 40pts |
|---|---|---|---|---|
| Último login (dias) | 35% | <15 dias | 15–45 dias | >45 dias |
| Usuários ativos / contratados | 30% | >80% | 50–80% | <50% |
| Módulos em uso / contratados | 20% | >80% | 50–80% | <50% |
| Buscas automáticas nos últimos 30d | 15% | Executou | Config ok, sem exec | Nunca executou |

### Dimensão 2 — Maturidade (25%)

| Métrica | Peso | 🟢 | 🟡 | 🔴 |
|---|---|---|---|---|
| Fornecedores cadastrados / meta | 40% | >75% | 50–75% | <50% |
| Documentos vencidos | 35% | <10% | 10–30% | >30% |
| Configuração do sistema | 25% | ≥90% | 70–90% | <70% |

### Dimensão 3 — Valor Gerado (20%)

| Métrica | Peso | 🟢 | 🟡 | 🔴 |
|---|---|---|---|---|
| Conformidade documental (% aprovados) | 50% | >80% | 60–80% | <60% |
| Certidões automáticas executadas (últimos 90d) | 30% | Ativo | Execução há >90d | Nunca executou |
| RFI realizados (se módulo contratado) | 20% | ≥1 no trimestre | Nenhum há 90d | Nunca realizou |

### Dimensão 4 — Relacionamento (15%)

| Métrica | Peso | 🟢 | 🟡 | 🔴 |
|---|---|---|---|---|
| NPS | 40% | ≥8 | 6–7 | ≤5 |
| Dias desde última interação | 35% | <15 dias | 15–30 dias | >30 dias |
| Tickets sem resolução >5 dias úteis | 25% | 0 | 1 | >1 |

### Dimensão 5 — Risco Comercial (10%)

| Métrica | Peso | 🟢 | 🟡 | 🔴 |
|---|---|---|---|---|
| Dias para renovação | 60% | >90 dias | 30–90 dias | <30 dias |
| Engajamento na renovação | 40% | Reunião feita/agendada | Contato feito | Sem resposta |

---

## Cálculo do score

```
Score_dimensão = Σ(métrica × peso_métrica)
Score_total = Σ(score_dimensão × peso_dimensão)
```

**Exemplo:**
Cliente com Adoção 85, Maturidade 60, Valor 70, Relacionamento 90, Risco 80:
`(85×0.30) + (60×0.25) + (70×0.20) + (90×0.15) + (80×0.10) = 75 → 🟡 Em atenção`

---

## Mapeamento de fontes

| Fonte | Métricas |
|---|---|
| **Metabase (automático)** | Último login, usuários ativos, fornecedores cadastrados, docs vencidos, conformidade, certidões, RFI |
| **Manual — Gabriel insere** | NPS, última interação, tickets em aberto, dias para renovação, engajamento na renovação |
| **Gap — não existe ainda** | Módulos contratados vs. em uso (cruzar contrato × Metabase), meta de fornecedores por cliente |

---

## Próximos passos quando retomar

1. Validar pesos das dimensões com Gabriel — alguma mais crítica?
2. Definir formato exato do input manual (planilha CSV? formulário no dash?)
3. Resolver gap de "módulos contratados vs. em uso" — mapear manualmente por cliente ou via contrato
4. Decidir stack do dashboard (React standalone ou integrar ao app gestão_efcaz existente)
5. Criar estrutura de dados: schema de clientes + scores históricos
6. Implementar cálculo e visualização

---

## Perguntas em aberto

- Os pesos das dimensões fazem sentido para o seu contexto? Alguma mais crítica?
- Alguma métrica que seu dia a dia mostra que é mais importante do que está aqui?
- Input manual: prefere editar via planilha ou formulário dentro do dashboard?
