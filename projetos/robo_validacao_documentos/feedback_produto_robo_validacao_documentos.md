# Feedback de Produto — Robô de Validação de Documentos

**Origem:** Ideia levantada pela Afonso França (Tier A) — validada como dor generalizada na carteira
**Data:** 17/07/2026
**CSM:** Gabriel Vital

---

## A dor

Todos os clientes da Efcaz possuem equipes dedicadas à validação manual de documentos enviados por fornecedores. Essas equipes — com **2 a 15 pessoas** por cliente, às vezes com dedicação exclusiva — abrem, leem e verificam documento por documento.

O módulo de buscas automáticas da plataforma já resolve as **certidões públicas** (FGTS, CND Federal, Estadual, CNDT, IBAMA etc.). Mas tudo o que vai além disso — apólices de seguro, alvarás, registros de classe, habilitações técnicas, ASOs, contratos, certificados ISO, entre outros — **é enviado pelo fornecedor e validado manualmente** por alguém do cliente.

### Custo operacional estimado por cliente

| Perfil | Pessoas na validação | Custo mensal estimado |
|---|---|---|
| Cliente médio | 3–5 pessoas | R$ 9.000 – R$ 15.000/mês |
| Cliente grande (ex.: Zurich, Afonso França) | 8–15 pessoas | R$ 24.000 – R$ 45.000/mês |

Esse custo é **recorrente, invisível e eliminável** — e está acontecendo dentro de plataformas como a Efcaz que foram contratadas justamente para automatizar a gestão de documentos.

---

## Caso de uso real — Zurich Airport Brasil

Na Zurich, os documentos cobertos pelas buscas automáticas representam apenas uma fração do total exigido. Toda a documentação complementar (registros, habilitações, apólices) é enviada pelo fornecedor via portal e validada manualmente pela equipe interna.

Com ~50 fornecedores ativos e múltiplos documentos por fornecedor, o volume de validações manuais mensais é alto — e cresce proporcionalmente ao número de fornecedores na base.

---

## Proposta de solução — Robô de Validação de Documentos

Um módulo automatizado que, ao receber um documento enviado pelo fornecedor, executa validações sem intervenção humana.

### Funcionalidades priorizadas por complexidade

| Prioridade | Funcionalidade | Complexidade | Descrição |
|---|---|---|---|
| 🥇 1 | **Leitura de data de validade** | Baixa | OCR extrai a data de validade do próprio PDF e popula automaticamente o campo na plataforma — sem depender do fornecedor informar |
| 🥈 2 | **Verificação de tipo de documento** | Média | Classifica se o PDF enviado é realmente o documento esperado no campo (ex.: enviou uma NF no campo de CND Federal) |
| 🥉 3 | **Cruzamento com dados do cadastro** | Média-alta | OCR extrai CNPJ, razão social e outros dados do documento e valida se batem com o cadastro do fornecedor na plataforma |
| 4 | **Detecção de adulteração/fraude** | Alta | Análise de integridade do PDF (metadados, assinaturas digitais, edições) — sinaliza documentos potencialmente fraudados |

> As funcionalidades 1 e 2 já justificam o produto e entregam valor imediato. As funcionalidades 3 e 4 ampliam o escopo e o argumento comercial.

---

## Impacto esperado

- **Para o cliente:** redução drástica de horas de trabalho manual na validação; diminuição do risco de documentos incorretos ou fraudados passarem despercebidos
- **Para a Efcaz:** diferencial competitivo no mercado SRM; argumento de ROI tangível e mensurável para vendas e renovações
- **Para o CSM:** fortalece argumento de retenção e abre oportunidade de upsell como módulo adicional

---

## Pergunta para o produto

1. Existe alguma iniciativa parecida já em roadmap ou explorada anteriormente?
2. Qual seria o nível de esforço para implementar as funcionalidades 1 e 2 como MVP?
3. Faz sentido como módulo adicional (upsell) ou como evolução da plataforma base?
4. Quais clientes poderiam participar de um piloto?

---

## Clientes potenciais para piloto / validação

| Cliente | Tier | Por quê |
|---|---|---|
| Afonso França | A | Origem da ideia; Karine é referência operacional, aberta a testes |
| Zurich Airport Brasil | A | Volume alto de documentos manuais; base mapeada |
| Grupo Sábara | B | Múltiplos tipos de fornecedor; fluxo de segurança ativo |

---

## Próximo passo sugerido

Agendar 30 min com o time de produto para apresentar o caso de uso e mapear viabilidade do MVP (funcionalidades 1 e 2). Gabriel pode participar para trazer a voz do cliente.
