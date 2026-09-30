# Trial: zurich-js
**Branch:** `teste/zurich-js`
**Data:** 28/09/2026
**Status:** Em avaliação — NÃO aplicar ao main sem validação

---

## O que foi construído

Duas features novas no dashboard React da Zurich Airport, testadas em branch isolada:

| Feature | Status | Pronto para produção? |
|---|---|---|
| [Exportação Personalizada](#1-exportação-personalizada-e-contextual) | ✅ Funcional | Sim — validar UX |
| [Seção Competências](#2-seção-evolução-por-competência) | ⚠️ Dados ambíguos | Não — validar com Débora antes |

---

## Como aplicar ao main quando pronto

```bash
git checkout main
git merge teste/zurich-js
git push
```

Ou cherry-pick por feature (ver commits abaixo):

| Feature | Commit |
|---|---|
| Exportação Modal | `3e5fcc9` |
| Competências (gráfico) | `c9c4e59` |
| Competências (tabela final) | `0425bd7` |
| Competências (filtro global de fornecedor) | ver `git log` — 30/09/2026 |

```bash
# Aplicar só a exportação modal, por exemplo:
git checkout main
git cherry-pick 3e5fcc9
```

---

## Arquivos criados/modificados

### Novos
- `dashboard-react/src/components/ExportModal.tsx`
- `dashboard-react/src/components/CompetenciasSection.tsx`
- `dashboard-react/public/data/competencias_zurich.csv`

### Modificados
- `dashboard-react/src/App.tsx`
- `dashboard-react/src/components/GlobalFilter.tsx`
- `dashboard-react/src/utils/exportUtils.ts`

---

Veja os detalhes de cada feature nos arquivos desta pasta.

---

## Ajuste 30/09/2026 — Competência do R3 (Situação Documental por Terceiro)

**Problema:** ao filtrar pendências por competência, os gráficos do R3 vinham zerados de agosto/2026 em diante.

**Causa:** o R3 lia a competência só da coluna G "Marcas e Representações" (campo antigo). A plataforma passou a preencher a coluna H "Competência", que tinha 221 documentos em agosto contra 16 na coluna G.

**Regra nova (só no trial):**
- Fonte principal: coluna H "Competência".
- Reserva: coluna G, apenas quando a H vier vazia ou não existir (exports antigos).
- Mantidas as regras de documentos sem competência (ASO, Ordens de Serviço, Capacitação) e o "A classificar".

**Impacto na base de 25/09:** agosto passa de 16 para 221 documentos; julho de 437 para 594; junho de 693 para 818; "A classificar" cai de 1.728 para 1.115.

**Pendente antes do main:** espelhar a mesma regra no relatório Python (`Dashboard/relatorio_fornecedores_zurich.py`), que continua lendo a coluna G.

Arquivo: `dashboard-react/src/utils/dataProcessing.ts` (bloco R3 — Situação por Terceiro).
