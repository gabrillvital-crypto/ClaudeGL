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

| Indicador | Valor | Fonte | Status |
|---|---|---|---|
| Solicitações abertas (total) | 102 | Metabase | 🔴 |
| Solicitações pendentes (visão homepage) | 9 | Portal Bunker One | 🟡 |
| Fornecedores ativos | 20 / 300 (6,7%) | Metabase | 🔴 |
| Certificados cadastrais válidos | 8 / 20 (40%) | Portal Bunker One | 🔴 |
| Fornecedores não certificados | 12 / 20 (60%) | Portal Bunker One | 🔴 |
| Avaliações abertas | 0 | Metabase | 🔴 (módulo inativo) |
| Ocorrências abertas (total) | 19 | Metabase | 🟡 |
| Ocorrências para análise Bunker One | 12 | Portal Bunker One | 🟡 |
| Ocorrências pendentes fornecedor | 0 | Portal Bunker One | 🟢 |
| Média de homologação | 74 dias 9h | Metabase | 🔴 |
| Média homologação com indeferimento | 74 dias 9h | Metabase | 🔴 |
| Média homologação sem indeferimento | N/D (campo vazio) | Metabase | — |

> Interpretação: a média de homologação de 74 dias é puxada apenas pelos casos com indeferimento — nenhum fornecedor foi aprovado sem ao menos uma rejeição anterior. Isso indica que o processo de documentação está mal calibrado ou os fornecedores não sabem o que enviar.

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

## Perfis completos de usuários — 20 cadastrados (Metabase 15/06/2026)

> ⚠ **Alerta de conformidade:** contrato prevê 2 UC — mas há **7 usuários com perfil UC** cadastrados (excluindo EFCAZ interno). Investigar se é erro de role assignment ou uso intencional.

### Tabela completa

| Nome | E-mail | Telefone | Empresa | Perfil(s) | Acesso abr–jun/26 |
|---|---|---|---|---|---|
| André Faustino | anfa@bunkerone.com | 11 99999-9999 (placeholder) | Bunker One | Consulta fornecedor | — |
| Marco Aurelio | marco.aurelio@novaoffshore.com.br | 0000000000 (placeholder) | Nova Offshore | Comprador, Solicitante, Homologador | — |
| Usuario Integração Setup | — | placeholder | Sistema | Integração | — |
| Carvalho Junior | carvalho.junior@novaoffshore.com.br | 0000000000 (placeholder) | Nova Offshore | Comprador, Solicitante, Homologador | — |
| Diego Tavares | dipt@bunkerone.com | 0000000000 (placeholder) | Bunker One | Comprador, Solicitante, Homologador | — |
| **Rafaella Perdone** | raco@bunkerone.com | **55 21 99866-7852** | Bunker One | Consulta fornecedor + **UC** | 1 acesso (01/abr) |
| Andre Luis Reis Silva | anlu@bunkerone.com | 11111111111 (placeholder) | Bunker One | **UC** | 2 acessos (último: 22/abr) |
| Thiago Santos | thsa@bunkerone.com | 5511000000 (placeholder) | Bunker One | Consulta fornecedor | — |
| **Daniel Caldas da Silva** | dcs@bunkerone.com | **21 97673-6903** | Bunker One | **UC** | 1 acesso (09/abr) |
| Clara Zacche | anlo@bunkerone.com | 5511999999999 (placeholder) | Bunker One | Consulta fornecedor | — |
| Ricardo Silva | ricardo.silva@azi.com.br | — | AZI/Efcaz (interno) | Consulta fornecedor | — |
| Heber Bispo | hebi@bunkerone.com | 0000000000 (placeholder) | Bunker One | Comprador, Solicitante, Homologador | — |
| **Rodrigo Moura** | rodrigo.moura@novaoffshore.com.br | — | Nova Offshore | **UC** ⭐ | **25 acessos (11/06)** |
| Roney Gatto | rong@bunkerone.com | **55 21 99742-4014** | Bunker One | Consulta fornecedor | 12 acessos (05/06) |
| **Rodrigo Lopes** | rodrigo@rlopesconsultoria.com | 0000000000 (placeholder) | Consultoria externa | **UC** | 1 acesso (22/abr) |
| EFCAZ *(interno)* | administrador@efcaz.com.br | — | Efcaz | Administrador + UC | ⚠ não contabilizar |
| **José Ronaldo** | jose.filho@novaoffshore.com.br | **21 99717-9333** | Nova Offshore | **UC** | 5 acessos (12/06) |
| **Mariana Silva Amorim** | masm@bunkerone.com | **55 21 97116-8257** | Bunker One | **UC** | 0 acessos no período |
| João Borges | — | — | — | — | 1 acesso (16/abr) |
| Antonio Mendes | — | — | — | — | 6 acessos (02/06) |

> **Telefones reais identificados (DDD 21 — Rio de Janeiro):** Rafaella, Daniel, Roney Gatto, José Ronaldo, Mariana.

---

## Unidades Cadastradoras — análise específica

**Contratado:** 2 UC | **Cadastrado:** 7 UC (excluindo EFCAZ interno)

| UC | Empresa | Telefone real | Acessos abr–jun/26 | Status |
|---|---|---|---|---|
| Rodrigo Moura | Nova Offshore | — | **25** ⭐ | 🟢 Mais ativo da conta inteira |
| José Ronaldo | Nova Offshore | 21 99717-9333 | **5** | 🟢 Ativo |
| Rafaella Perdone | Bunker One | 55 21 99866-7852 | 1 (01/abr) | 🟡 Praticamente inativa |
| Andre Luis Reis Silva | Bunker One | placeholder | 2 (22/abr) | 🟡 Inativo há 53d |
| Daniel Caldas da Silva | Bunker One | 21 97673-6903 | 1 (09/abr) | 🔴 Inativo há 66d |
| Rodrigo Lopes | Consultoria externa | placeholder | 1 (22/abr) | 🔴 Inativo há 53d |
| Mariana Silva Amorim | Bunker One | 55 21 97116-8257 | **0** | 🔴 Zero acessos no período |

### Interpretação crítica

**A plataforma é operada pela Nova Offshore, não pelo Bunker One.**

Os dois UCs mais ativos (Rodrigo Moura e José Ronaldo) são da **Nova Offshore** — parceira da Bunker One, não funcionários diretos. Os 5 UCs do lado Bunker One têm engajamento quase zero no período.

Isso cria um risco real: se a Nova Offshore mudar de foco ou encerrar a parceria, a Bunker One perde o "motor" da plataforma.

Mariana Silva Amorim (única UC interna da Bunker One com telefone real) **não teve nenhum acesso no período analisado** — e deveria ser a responsável pela gestão.

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

## Fornecedores cadastrados — dados de contato (Metabase 15/06/2026)

| Razão Social | Nome Fantasia | CNPJ | Porte | Telefone(s) | E-mail | Capital Social |
|---|---|---|---|---|---|---|
| PINAMAK COMERCIAL DE MAQUINAS E EQUIPAMENTOS INDUSTRIAIS LTDA | PINACOMAK | 28.117.851/0001-19 | Grande | 21 2126-2800 / 2126-2822 | moyseis.lopes@pinamak.com.br | 0 |
| SHIPLOG SERVICOS DE AGENCIAMENTO MARITIMO E LOGISTICA LTDA | SHIPLOG AGENCY | 29.362.436/0001-02 | Pequeno | 21 2135-7521 | luciano.oliveira@shiplogagency.com | 10.000 |
| NOVA OFFSHORE NAVEGACAO LTDA | — | 23.625.377/0001-31 | Grande | 21 3550-1280 | finance@bonoshipping.com | 9.031.000 |
| J B C TRANSPORTES LTDA | — | 19.056.147/0001-21 | Microempresa | 21 9999-9999 | xxxxxxxxxx@gmail.com | 100.000 |
| AMBIPAR RESPONSE MARITIME SERVICES PDA S/A | — | 04.978.039/0001-39 | Grande | 27 3376-7172 / 2781-2558 | fabio@zenithmaritima.com.br | 1.637.998 |
| SUPPLY CONTROL GERENCIAMENTO E SERVICOS LTDA | SUPPLY CONTROL | 34.803.572/0001-20 | Pequeno | 47 2033-6788 | supplycontrolbunker@gmail.com | 400.000 |
| ALCANCE ASSESSORIA EM COMERCIO EXTERIOR LTDA | ALCANCE COMEX | 07.989.076/0001-30 | Pequeno | 81 3467-3467 / 3426-5047 | marcos@alcancecomex.com.br | 100.000 |
| AMSP BRASIL SERVICOS PORTUARIOS E LOGISTICA LTDA | AMSP BRASIL - COMBUSTIVEIS & ENERGIAS SUSTENTAVEIS | 45.926.568/0001-76 | Pequeno | 53 8421-7232 | diretoria@amspbrasil.com.br | 4.500.000 |
| QUIMITRANS LOGISTICA & TRANSPORTES LTDA | — | 74.445.099/0002-52 | Grande | 21 2676-4410 | controladoria03.sp@qltlog.com | 1.500.000 |
| MASTER TRANSPORTADORA E LOGISTICA LTDA | BEL-MASTER | 21.102.732/0001-62 | Microempresa | 21 7891-3525 | apereiradasilva49@yahoo.com.br | 110.000 |
| VANS ASSESSORIA ADUANEIRA LTDA | — | 40.018.508/0001-31 | Pequeno | 21 6425-3194 | vans.assessoria@gmail.com | 15.000 |
| COMPANHIA PORTUARIA VILA VELHA | — | 39.826.482/0001-79 | Grande | 27 3399-4121 | cpvv@cpvv.com.br | 20.409.860 |
| INTERTEK DO BRASIL INSPECOES LTDA | — | 42.565.697/0011-60 | Grande | 11 2842-0444 | mi.adm@intertek.com | 389.474.065 |
| SEA LINE AGENCIA MARITIMA LTDA | — | 82.885.716/0001-88 | Pequeno | 47 3471-4500 | marlene@sealine.com.br | 444.243 |
| SEG ENGENHARIA LTDA | SEG - SERVICO DE ENGENHARIA E GESTAO DE SSMA | 28.399.575/0001-48 | Microempresa | 82 9341-7661 | engmarciomarques@hotmail.com | 1.000.000 |
| C.L.A TRANSPORTES LTDA | — | 13.454.736/0001-81 | Grande | 47 3343-0303 / 3343-7379 | financeiro@clatransportes.com | 20.000 |
| INNOVINE SISTEMAS E CONSULTORIA LTDA | GRUPO IDEIAS TECNOLOGIA | 13.125.492/0001-93 | Microempresa | 21 2018-6919 | comercial@ideastecnologia.com.br | 300.000 |
| NOVA JBC LTDA | — | 52.016.808/0001-60 | Microempresa | 21 6435-5510 | jbctransportes2013@gmail.com | 100.000 |
| OCEANPACT SERVICOS MARITIMOS S.A. | — | 09.114.805/0002-11 | Grande | 21 3032-6700 / 3950-8550 | administrativo@oceanpact.com | 0 |
| ALE COMBUSTIVEIS S.A. | — | 23.314.594/0001-00 | Grande | 84 3204-5050 / 8498-9433 | fiscalizacoes@ale.com.br | 834.123.735 |

> Total visível: 20 fornecedores — confirma os 20 ativos cadastrados. Perfil da base: agenciamento marítimo, transportadoras, inspeção (Intertek), portos (Vila Velha, AMSP), combustíveis (ALE), comércio exterior.

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
