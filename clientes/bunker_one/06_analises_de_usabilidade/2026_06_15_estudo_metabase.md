# Estudo de Usabilidade — Bunker One
**Data:** 15/06/2026 | **Fonte:** Metabase
**Classificação de risco:** 🟡 Amarelo — engajamento parcial com gaps críticos de adoção

---

## Contrato

| Item | Contratado | Em uso |
|---|---|---|
| Fornecedores | 300 | 20 ativos (6,7%) |
| Usuários | 6 (4 aux + 2 UC) | 20 cadastrados / 30 total |
| Módulos | Avaliação, Integração, Solicitação, Ocorrências | Solicitação e Ocorrências em uso — Avaliação: zero |
| Integrações | 63 disponíveis | 5 ativas |
| OCR | 136 documentos configurados | 0 com OCR ativo |

---

## KPIs

| Indicador | Valor | Status |
|---|---|---|
| Solicitações abertas | 102 | 🔴 |
| Fornecedores ativos | 20 / 300 | 🔴 |
| Avaliações abertas | 0 | 🔴 (módulo inativo) |
| Ocorrências abertas | 19 | 🟡 |
| Média de homologação | 74 dias 9h | 🔴 |

---

## Sinais identificados

**🔴 Críticos:**
- 20 fornecedores ativos de 300 contratados — 6,7% de ocupação
- 102 solicitações em aberto — backlog represado
- 74 dias de média de homologação — processo com gargalo
- Módulo de Avaliação: contratado e completamente inativo
- Todas as integrações TRT desligadas (TRT1 ao TRT24 = false)
- OCR zerado — 136 documentos configurados, nenhum com leitura automática ativa
- Cancelamentos de solicitação crescendo em 2026

**🟡 Atenção:**
- 19 ocorrências abertas sem resolução
- Pico de ocorrências em fev e abr/2024, zerou depois — causa não identificada

**🟢 Positivos:**
- Solicitações crescendo desde jul/2025 (9 → 15 → 10 → 9/mês)
- 20 usuários com perfis bem distribuídos
- Nova Offshore integrada como usuária e fornecedora — parceiro estratégico

---

## Usuários-chave — Contatos completos (Metabase)

| Nome | E-mail | Telefone | Empresa | Observação |
|---|---|---|---|---|
| Rafaella Perdone | raco@bunkerone.com | 55 21 99866-7852 | Bunker One | Telefone real |
| Andre Luis Reis Silva | anlu@bunkerone.com | — (placeholder) | Bunker One | Inativo desde abril |
| Daniel Caldas da Silva | dcs@bunkerone.com | 21 97673-6903 | Bunker One | Telefone real |
| **Rodrigo Moura** | rodrigo.moura@novaoffshore.com.br | — | **Nova Offshore** | ⭐ Power user (25 acessos) — é da Nova Offshore, não Bunker One |
| Rodrigo Lopes | rodrigo@rlopesconsultoria.com | — (placeholder) | Consultoria externa | Acesso pontual |
| José Ronaldo | jose.filho@novaoffshore.com.br | 21 99717-9333 | **Nova Offshore** | Telefone real — último login interno (12/06) |
| Mariana Silva Amorim | masm@bunkerone.com | 55 21 97116-8257 | Bunker One | Unidade Cadastradora — telefone real |
| EFCAZ | administrador@efcaz.com.br | — | Efcaz (interno) | ⚠ Conta interna — não contabilizar |

> **Contatos com telefone real (DDD 21 — Rio de Janeiro):** Rafaella, Daniel, José Ronaldo e Mariana.
> **Cadastro incompleto:** Andre Luis (placeholder), Rodrigo Lopes (placeholder), Rodrigo Moura (sem telefone).

> ⚠ **Insight crítico:** Rodrigo Moura (25 acessos) e José Ronaldo são da **Nova Offshore** — não do Bunker One diretamente. A Nova Offshore é parceira estratégica integrada como usuária e fornecedora na plataforma.

> ⚠ Renato (Efcaz) indicou que o contato para abertura com Gabriel é André (executivo interno da Efcaz) — não entrar direto sem passar por ele primeiro.

---

## Relatório de acesso — período analisado (abr–jun/2026)

**Fonte:** `Relatório SRM_Último Acesso por tenant_Tabela.csv` | **Data do relatório:** 15/06/2026

### Usuários internos (Bunker One) — por frequência de acesso

| Usuário | Acessos | Último acesso | Dias atrás | Observação |
| --- | --- | --- | --- | --- |
| **Rodrigo Moura** | **25** | 11/06/2026 | 3d | ⭐ Power user — principal operacional da plataforma |
| Roney Gatto | 12 | 05/06/2026 | 9d | Acesso regular |
| Antonio Mendes | 6 | 02/06/2026 | 12d | Acesso regular |
| José Ronaldo | 5 | 12/06/2026 | 2d | **Último login interno** |
| Andre Luis Reis Silva | 2 | 22/04/2026 | 53d | Inativo desde abril |
| Rodrigo Lopes | 1 | 22/04/2026 | 53d | Acesso pontual |
| João Borges | 1 | 16/04/2026 | 59d | Acesso pontual |
| Daniel Caldas da Silva | 1 | 09/04/2026 | 66d | Acesso pontual |
| Rafaella Perdone | 1 | 01/04/2026 | 74d | Acesso pontual |

> ⚠ **Conta EFCAZ (ID 1):** é a conta interna da Efcaz usada para suporte/configuração — **não contabilizar como engajamento do cliente**. Os 12 acessos dela no período refletem suporte prestado, não uso autônomo do Bunker One.

### Fornecedores ativos no período

| Fornecedor | Acessos | Último acesso | Dias atrás |
| --- | --- | --- | --- |
| Camila Sanjour | 14 | 08/06/2026 | 6d |
| Maria Isabel | 11 | 10/06/2026 | 4d |
| Leonardo Henrique Fernandes Groppo | 8 | 15/06/2026 | 0d — **hoje** |
| Marcelo Pereira Olimpio | 6 | 28/04/2026 | 47d |
| Lucas Boaretto | 6 | 10/06/2026 | 4d |
| LUIZ CARLOS FRANÇA | 5 | 03/05/2026 | 42d |
| Adriana Pina | 4 | 27/04/2026 | 48d |

### Sinais do relatório de acesso

**🟢 Positivos:**

- Rodrigo Moura (25 acessos) é claramente o gestor operacional da plataforma — forte engajamento
- 4 usuários internos ativos nos últimos 15 dias
- Fornecedores acessando com frequência — Camila Sanjour, Maria Isabel e Leonardo Henrique são fornecedores recorrentes
- Plataforma acessada hoje (15/06) por Leonardo Henrique

**🟡 Atenção:**

- Os perfis listados no Metabase (Heber Bispo, Diego Tavares, André Faustino) não aparecem no relatório de acesso — podem ser usuários cadastrados mas que não usam diretamente, ou nomes/aliases diferentes
- Conta EFCAZ (suporte interno) deve ser ignorada para fins de análise de engajamento do cliente

**🔴 Alerta:**

- Andre Luis Reis Silva (possivelmente o "André" referenciado por Renato como ponto de contato) parou de acessar em abril — 53 dias sem login

### Contato recomendado para abertura

Com base no relatório, o contato operacional certo é **Rodrigo Moura** — não os nomes que apareceram no Metabase. Mas a instrução do Renato segue válida: entrar primeiro pelo executivo interno da Efcaz (André) para fazer a introdução, e após a abertura, direcionar a Rodrigo Moura como power user.

---

## Contexto do segmento

Bunker One atua em **combustíveis e lubrificantes marítimos** (abastecimento de navios). Base de fornecedores: agentes marítimos, transportadoras, empresas portuárias, inspeção técnica (Intertek), distribuidoras de combustível (ALE Combustíveis). Operação multi-estado/porto — o que torna as integrações TRT regionais especialmente relevantes.

---

## Oportunidades

| Oportunidade | Potencial | Gancho |
|---|---|---|
| Ativar TRTs regionais | Alto | "Como vocês controlam trabalhistas de fornecedores em outros portos hoje?" |
| Ativar módulo de Avaliação | Alto | Mostrar fluxo Avaliação → Ocorrência → Plano de Ação |
| Reduzir 74 dias de homologação | Alto | Entender onde está o gargalo — operacional ou configuração? |
| Aumentar base ativa (20/300) | Alto | Quantos fornecedores reais têm vs. o que está cadastrado? |
| Ativar OCR | Médio | Reduzir análise manual de documentos |

---

## Abordagem recomendada

**Pré-requisito:** acionar André (executivo Efcaz) para abertura — cliente sem relação com Gabriel ainda.

**Gancho de entrada:**
> "Olha o que identificamos na plataforma de vocês — 74 dias de média de homologação e 102 solicitações em aberto. Queria entender o que está travando e ver se conseguimos resolver juntos."

Tom: consultivo, não comercial. Os dados sustentam a conversa.
