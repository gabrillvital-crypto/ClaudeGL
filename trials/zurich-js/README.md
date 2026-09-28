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
