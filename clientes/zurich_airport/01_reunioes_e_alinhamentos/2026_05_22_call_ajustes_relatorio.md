# Reunião — Ajustes de Relatório de Terceiros
**Data:** 22/05/2026
**Tipo:** Call técnica — alinhamento de dashboard BI
**Participantes Efcaz:** Gabriel + Ricardo (produto) + João (técnico)
**Contato Zurich:** Débora

---

## Contexto

Reunião para apresentar o dashboard de terceiros e coletar feedback. O dashboard foi aprovado como prova de conceito pelo time interno (Ricardo e João). Débora é a gestora da Zurich que vai usar o relatório.

---

## Transcrição disponível

Arquivo: `Reunião Efcaz - Zurich - Ajustes de relatório - 2026_05_22 10_00 GMT-03_00 - Transcript.pdf` (52 páginas)

---

## Decisões tomadas

1. Dashboard aprovado como prova de conceito
2. **Automação via N8N** (HTTP request à API Metabase) — já configurada e funcionando
3. Frequência de atualização: 1x ao dia, cron `0 7 * * *` (às 07h)
4. Hospedagem: servidor cloud da Efcaz (responsável: Ricardo/João)
5. Acesso Débora: URL externa com usuário + senha (htpasswd)

---

## Pedidos da Débora registrados

| # | Pedido | Status |
|---|---|---|
| 1 | Filtro por competência (mês) | ⚠️ Limitação estrutural da plataforma — dados não têm vínculo documento×competência |
| 2 | Histórico mês a mês (2 anos) | ⚠️ Não há dados históricos nos CSVs exportados |
| 3 | Gráfico de pizza para conformidade | ✅ Implementado (sessão 8) |
| 4 | Subtítulo nos gráficos estáticos | ⏳ Pendente (P5) |

---

## Próximos passos

| # | Ação | Responsável | Status |
|---|---|---|---|
| 1 | Apresentar dashboard para Débora | Gabriel | 29/05/2026 às 16h |
| 2 | João implementar fluxo N8N de envio por e-mail | João | ⏳ |
| 3 | Confirmar se Zurich usa Google ou Microsoft (para escolha de deploy) | Gabriel | ⏳ |
