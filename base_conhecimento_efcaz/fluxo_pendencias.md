# Fluxo de Pendências — Plataforma Efcaz
**Fonte:** KB90020 — "Como tratar pendências" (Movidesk)
**Atualizado em:** 24/07/2026

---

## O que é uma pendência?

Quando o BPO/cliente analisa uma solicitação (novo cadastro ou atualização) e identifica problemas em algum documento ou informação, o status da solicitação muda para **"Pendência"**. Isso não significa que todo o cadastro está incorreto — apenas que pontos específicos precisam ser corrigidos.

**Exemplo prático (Zurich Airport):** o fornecedor enviou a folha ponto de maio errada → o BPO sinaliza o problema → envia as pendências via sistema → fornecedor precisa reenviar o documento correto.

---

## Ciclo completo

```
Fornecedor envia solicitação
        ↓
BPO analisa
        ↓
   [problema?]
   SIM ──→ Status: "Pendência"
            ↓
         BPO envia pendências ao fornecedor (detalha o que corrigir)
            ↓
         Fornecedor acessa "Histórico de Solicitações"
            ↓
         Localiza solicitação com status Pendência → clica "Resolver"
            ↓
         Vai em "Dados da Solicitação" → lê o que precisa corrigir
            ↓
         Vai em "Dados da Empresa" → faz as correções
            ↓
         Clica "Enviar para Aprovação"
            ↓
         Status: "Aguardando Nova Análise"
            ↓
         BPO analisa novamente
            ↓
        Aprovado ──→ fim
        Pendência ──→ ciclo recomeça
   NÃO ──→ Status: "Aprovado"
```

---

## Como o fornecedor resolve a pendência (passo a passo)

1. Menu lateral esquerdo → **Histórico de Solicitações**
2. Localizar solicitação com status **Pendência** → clicar em **Resolver**
   - Alternativa: na página inicial, clicar em **"Resolver Pendências"**
3. Acessar aba **Dados da Solicitação** → ler a lista de pendências apontadas
4. Acessar aba **Dados da Empresa** → realizar os ajustes solicitados
   - Para atualizar documentos: expandir a aba (seta direita) → clicar **Novo** → preencher novamente
5. Clicar **Enviar para Aprovação** → confirmar no popup → status muda para **"Aguardando Nova Análise"**

---

## Mapeamento de status: dashboard Zurich ↔ plataforma Efcaz

| Status no dashboard | Significado na plataforma |
|---|---|
| **Reprovado** | Solicitação com status "Pendência" — BPO apontou problemas, aguarda ação do fornecedor |
| **Aguardando submissão** | Fornecedor recebeu a pendência mas ainda não clicou em "Resolver" e resubmeteu |
| **Em análise** | Fornecedor resubmeteu → status "Aguardando Nova Análise" — BPO revisando |
| **Aprovado** | BPO aprovou (na análise inicial ou após resubmissão) |
| **Não enviado** | Fornecedor ainda não anexou o documento na plataforma |

---

## Como interpretar variações no comparativo semanal

- **Queda em "Reprovados"** → fornecedores clicaram em "Resolver" e resubmeteram. Sinal positivo — ciclo andando.
- **Queda em "Aguardando submissão"** → fornecedores que estavam parados responderam à pendência.
- **Aumento em "Aprovados"** → resubmissões aprovadas pelo BPO na nova análise.
- **Aumento em "Pendências totais"** → novas rodadas de análise gerando novos pontos a corrigir. Normal em volume crescente.

> Um "-193 reprovados" em uma semana **não é dado suspeito** — é o ciclo de BPO funcionando corretamente.

---

## Dúvidas frequentes (KB90020)

**O que significa quando o cadastro está em pendência?**
Apenas algumas informações precisam ser corrigidas; o restante pode estar correto.

**Onde vejo o que precisa ser corrigido?**
Na aba "Dados da Solicitação", onde são listadas todas as pendências apontadas.

**Posso corrigir apenas os itens solicitados?**
Sim, mas é recomendável revisar todo o cadastro antes de reenviar.

**O que acontece depois que envio para aprovação novamente?**
O status muda para "Aguardando Nova Análise" e o BPO/cliente revisa novamente.

**Posso deixar a pendência sem resolver?**
Não é recomendado. Enquanto houver pendências, o cadastro pode ficar incompleto ou não aprovado, impedindo o andamento de processos.
