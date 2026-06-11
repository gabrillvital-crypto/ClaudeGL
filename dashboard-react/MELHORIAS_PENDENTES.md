# Melhorias Pendentes — Dashboard React Zurich Airport

Identificadas em 10/06/2026. Ordenadas por prioridade de impacto.

---

## 1. "Em Análise" contabilizado como Não Conforme nos donuts

**Arquivo:** `src/components/ConformidadeCharts.tsx`

**Problema atual:**
```
Conforme     = Aprovado
Não Conforme = tudo o resto (Reprovado + Não Anexado + Aguardando Submissão + Em Análise + Vencido)
```
Documentos Em Análise estão em processo — o fornecedor fez sua parte, a equipe ainda não validou.
Aparecem no vermelho do donut, inflando o % de não conformidade artificialmente.
Numa apresentação para a Zurich pode gerar pressão indevida sobre fornecedor que está em dia.

**Solução sugerida:** Excluir "Em Análise" e "Aguardando Submissão" do cômputo negativo do donut.
Ou separar em 3 categorias: Conforme / Em Processo / Não Conforme.

**Impacto:** Alto — distorce o % apresentado. **Esforço:** Baixo (1–2 linhas).

---

## 2. Drill-Down não inclui documentos corporativos (R4)

**Arquivo:** `src/components/DrillDown.tsx` + `src/components/R3Section.tsx`

**Problema atual:**
Ao clicar num fornecedor no Drill-Down, aparecem apenas os terceiros (R3).
Os documentos corporativos do próprio fornecedor (R4 — FGTS, CND, alvarás etc.) ficam de fora.
Para ver o quadro completo de conformidade de uma empresa é preciso ir na seção R4 separada.

**Solução sugerida:**
No Nível 2 do Drill-Down, acrescentar um bloco "Documentos Corporativos" antes da lista de terceiros,
com os docs R4 daquele fornecedor (vindo de `data.forn_sit` filtrado por `r.Fornecedor === selForn`).

**Impacto:** Médio — visão incompleta do fornecedor no drill. **Esforço:** Médio.

---

## 3. R3 não tem status "Vencido" — documentos expirados de terceiros somem

**Arquivo:** `src/utils/dataProcessing.ts` — função `mapStatusR3`

**Problema atual:**
A lógica R3 não tem path para "Vencido". Se um documento de terceiro foi aprovado, venceu,
e o fornecedor ainda não resubmeteu — ele cai em "Em Análise" ou "Não Anexado", não em "Vencido".
O campo `Data de Vencimento` existe no CSV mas não é usado como critério de status no R3.
O R4 tem "Vencido" explícito; o R3 não.

**Solução sugerida:**
Validar com Zurich/Efcaz se o CSV `situacao_terceiro_zurich.csv` pode conter "A vencer" ou "Vencido"
no campo `Status`. Se sim, acrescentar esse path na função `mapStatusR3` em `dataProcessing.ts`
e adicionar o card "Docs Vencidos R3" no KPIGrid.

**Impacto:** Médio — depende de validação com a plataforma. **Esforço:** Médio (requer confirmação de dado).

---

## 4. Card "Fornecedores com Execução" tem nome enganoso

**Arquivo:** `src/components/KPIGrid.tsx`

**Problema atual:**
O card mostra fornecedores que têm qualquer documento em R3 ou R4 — mesmo que 100% estejam reprovados.
"Com Execução" soa positivo mas não diz nada sobre conformidade.

**Solução sugerida:**
Renomear para "Fornecedores Ativos na Plataforma" ou acrescentar um segundo número `(X% conformes)`
calculado sobre o total de fornecedores com execução.

**Impacto:** Baixo — só nomenclatura/UX. **Esforço:** Mínimo.

---

## 5. Sort do Nível 2 no Drill-Down é por ordem de inserção

**Arquivo:** `src/components/DrillDown.tsx` — bloco `level === 2`

**Problema atual:**
Ao clicar num fornecedor e ver os terceiros, eles aparecem na ordem de processamento do CSV
(ordem do objeto `drillData[selForn]`). O `GrupoEmpresaView` tem sort, mas o `DrillDown` não.

**Solução sugerida:**
Ordenar os terceiros do Nível 2 por % de não conformidade decrescente — os mais problemáticos primeiro.
No bloco `level === 2`, substituir `Object.entries(drillData[selForn] || {})` por versão ordenada:
```ts
Object.entries(drillData[selForn] || {})
  .map(([terc, docs]) => {
    const nc = docs.filter(d => d.status !== 'Aprovado').length
    const pct = docs.length > 0 ? nc / docs.length : 0
    return { terc, docs, pct }
  })
  .sort((a, b) => b.pct - a.pct)
```

**Impacto:** Baixo — melhoria de UX. **Esforço:** Mínimo (5 linhas).

---

## Resumo executivo

| # | Problema | Impacto | Esforço | Arquivo principal |
|---|---|---|---|---|
| 1 | Em Análise como Não Conforme nos donuts | **Alto** | Baixo | ConformidadeCharts.tsx |
| 2 | R4 fora do Drill-Down | Médio | Médio | DrillDown.tsx |
| 3 | R3 sem "Vencido" | Médio | Médio* | dataProcessing.ts |
| 4 | "Com Execução" enganoso | Baixo | Mínimo | KPIGrid.tsx |
| 5 | Sort do Nível 2 no Drill-Down | Baixo | Mínimo | DrillDown.tsx |

\* Item 3 requer validação com Zurich/Efcaz antes de implementar.

**Recomendação para começar:** Item 1 — maior impacto, menor esforço.
