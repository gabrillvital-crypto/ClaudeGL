# Inteligência Competitiva — Executiva & Bernhoeft
**Data base:** 20/08/2026  
**Preparado por:** Gabriel Vital / Claude  
**Fontes:** Transcrição reunião Executiva (14/07/26) · Transcrição reunião Bernhoeft (04/08/26) · Apresentação Institucional PDF Executiva  
**Artifact publicado:** https://claude.ai/code/artifact/0a89c9bf-ce5b-424c-ae6c-06936de9ba7b

---

## 1. Resumo dos Concorrentes

### Executiva — Plataforma SG3
- **Modelo:** BPO + SaaS proprietário. Plataforma é o meio; 300+ auditores especializados são o diferencial declarado.
- **Proposta:** "Gestão de risco de terceiros com inteligência, tecnologia e pessoas."
- **Foco:** Terceirizados operacionais — estaleiros, montadoras, indústria pesada, cosméticos, energia.
- **Escala:** +50k fornecedores, +6,5M documentos analisados, +3M vidas auditadas, +300 clientes.
- **Clientes:** Volvo, VW, GM, Renault, Stellantis, Coca-Cola (35k vidas), Natura, Boticário, estaleiros CLI e FIPS.
- **Preço:** Por vida alocada (variável mensal). Requer "caderno de documentos" para precificar — sem isso, não conseguem dar proposta.
- **SLA:** 8h úteis para documentos de bloqueio (declarado como menor do mercado).
- **Internacionalização:** Espanhol + Inglês; operação no México em andamento.

### Bernhoeft
- **Modelo:** BPO + SaaS proprietário. Plataforma e consultoria são indissociáveis — "sem a consultoria, não teria esses dados."
- **Proposta:** Pioneira em gestão de riscos com terceiros. 5x Prêmio Bras consecutivo.
- **Foco:** Compliance trabalhista e homologação financeira — mineração, energia, grandes corporações.
- **Escala:** ~950k vidas/mês, +45k fornecedores, +10M documentos, +240 clientes.
- **Clientes:** Petrobrás (case fundador), Samarco, Siemens. Maioria não divulgada.
- **Preço:** R$350–500/fornecedor/ano + R$1.500–2.000/mês plataforma + faturamento mínimo R$7–10k/módulo operacional.
- **SLA:** 1 dia útil na mobilização (IA + time técnico).
- **4 quadrantes independentes:** Homologação · Mobilização (seg. trabalho) · Trabalhista · Auditoria em campo.

---

## 2. Pontos Fortes e Fracos

### Executiva — Forças
- 300+ auditores: técnicos de SESMT e peritos trabalhistas dedicados (não analistas genéricos)
- 3 modalidades de auditoria: Administrativa, Técnica SESMT, Pericial Trabalhista + Ambiental
- Auditoria 100% dos documentos, sem franquia de volume
- SLA 8h úteis para documentos de bloqueio
- Módulos avançados: ANA (blacklist de pessoas), Crachá, App móvel SG3 Audita (offline)
- Formulários dinâmicos: ESG, APR (Análise Preliminar de Risco)
- SSO via AD/LDAP/OAuth; integração SAP/Oracle
- UniEx: EAD com reconhecimento facial + captura periódica anti-fraude
- Dashboard com 50+ indicadores personalizáveis por perfil
- Reunião mensal de indicadores incluída no contrato (até 5º dia útil)
- Internacionalização real (México, espanhol/inglês)
- Cobrança justa: por vida alocada, sem mínimo declarado

### Executiva — Fraquezas (vulnerabilidades exploráveis)
- Precificação opaca: requer caderno de documentos para qualquer proposta — processo comercial lento
- Modelo BPO-intensivo: custo escala junto com o crescimento do cliente
- IA ainda em amadurecimento: previsão de 5h de SLA até fim de 2026, mas não é realidade ainda
- Foco estreito: não atende SRM amplo (fornecedores de produtos/serviços)
- **Não faz busca automática de certidões** — depende inteiramente da postagem do fornecedor
- Sem análise financeira (Serasa, balanço) identificada
- Sem listas restritivas identificadas
- Sem avaliação de performance (RFI)

### Bernhoeft — Forças
- Pioneira (Petrobrás, 23+ anos); maior reconhecimento de mercado identificado
- Consultoria especializada integrada ao produto — cliente compra o time, não só a plataforma
- **Monetização do risco trabalhista em R$** — calcula passivo financeiro para apresentar ao C-level (argumento muito eficaz)
- BI diário consolidado (D+1) — dashboard atualizado toda manhã
- Homologação financeira robusta: balanço, faturamento, score com zero automático em lista suja
- Maior escala: 950k vidas/mês
- Módulo trabalhista completo: cartão ponto, horas extras, convenção coletiva, férias, rescisão — mensal
- Auditoria em campo sob demanda
- Diversificação: contabilidade + BPO de folha → pode vender ecossistema

### Bernhoeft — Fraquezas (vulnerabilidades exploráveis)
- **Faturamento mínimo R$7–10k/módulo** — exclui PMEs e operações menores, admitido pela própria empresa
- Processo de qualificação interno rígido: barram clientes pequenos antes do comercial
- Módulos acumulativos: custo total pode se tornar proibitivo
- Dificuldade em atender nichos novos/atípicos — admitida na reunião ("o ramo de vocês é muito novo para mim")
- **Não faz busca automática de certidões**
- Sem avaliação de performance (RFI)
- Sem app móvel identificado
- Não consegue ser canal/parceiro de distribuição — impossibilidade declarada na reunião

---

## 3. Benchmark — Cobertura por Dimensão

| Dimensão | Executiva | Bernhoeft | Efcaz |
|---|:---:|:---:|:---:|
| **PRODUTO & MODELO** | | | |
| Tipo de produto | BPO + SaaS | BPO + SaaS | SaaS puro |
| Modelo comercial | Por vida alocada | Por vida + min/módulo | MRR fixo por fornecedores/usuários |
| **GESTÃO DOCUMENTAL** | | | |
| Portal / Autocadastro de fornecedor | ✅ | ✅ | ✅ |
| Gestão de validade e alertas | ✅ | ✅ | ✅ |
| Busca automática de certidões | ❌ | ❌ | ✅ **Exclusivo** |
| Auditoria humana de documentos | ✅ 8h úteis | ✅ 1 dia útil | — (SaaS puro) |
| **AUDITORIA & COMPLIANCE** | | | |
| Auditoria SESMT / NRs / ASO | ✅ Técnicos dedicados | ✅ | ❌ |
| Auditoria Pericial Trabalhista | ✅ Peritos dedicados | ✅ + monetização em R$ | ❌ |
| Monetização do risco trabalhista em R$ | ❌ | ✅ **Exclusivo BNH** | ❌ Gap identificado |
| Auditoria Ambiental / ESG documental | ✅ | ◑ | ❌ |
| Background Check / Listas restritivas | ❌ | ✅ | ✅ |
| **HOMOLOGAÇÃO & SCORING** | | | |
| Homologação de fornecedores | ◑ | ✅ (financeira + técnica) | ✅ |
| Score / Análise cadastral | ◑ (conformidade) | ✅ | ✅ |
| Análise financeira (Serasa/balanço) | ❌ | ✅ | ✅ |
| Avaliação de Performance (RFI) | ❌ | ❌ | ✅ **Exclusivo** |
| Selo de Confiabilidade | ❌ | ❌ | ✅ **Exclusivo** |
| **FUNCIONALIDADES AVANÇADAS** | | | |
| Controle de acesso físico (catraca/crachá) | ✅ | ✅ | ❌ |
| Módulo ANA (blacklist de pessoas) | ✅ | ❌ | ❌ |
| App móvel (campo/offline) | ✅ SG3 Audita | ❌ | ❌ |
| BI / Dashboard dinâmico | ✅ 50+ indicadores | ✅ D+1 diário | ◑ (relatórios + API externa) |
| Integração via API | ✅ SAP/Oracle/SSO | ◑ | ✅ |
| Plataforma EAD com reconhecimento facial | ✅ UniEx | ❌ | ❌ |
| **CUSTOMER SUCCESS** | | | |
| Reuniões periódicas de indicadores | ✅ Mensal incluída | ◑ | ✅ Por tier |
| Suporte ao fornecedor | ✅ Chat/WhatsApp/sala diária | ✅ Via consultoria | ◑ Via portal |

---

## 4. Battlecard Comercial

### Vs. Executiva — Argumentos de Ataque

1. **Certidões automáticas** — Executiva depende do fornecedor postar manualmente. Efcaz busca automaticamente nas fontes. Para gestores com centenas de fornecedores, elimina carga operacional que a concorrente não resolve.

2. **Preço previsível vs. preço variável** — Executiva cobra por vida alocada (MRR flutua) e requer caderno de documentos para orçar. Efcaz tem MRR fixo por fornecedores/usuários — o cliente sabe exatamente o que paga.

3. **RFI fecha o ciclo SRM** — Executiva controla documentação, mas não avalia qualidade da entrega. Efcaz tem RFI integrado — passa da conformidade para gestão estratégica.

4. **Análise financeira (Serasa) integrada** — Executiva não tem. Efcaz avalia risco financeiro antes de homologar.

5. **Implantação sem BPO** — Executiva precisa montar estrutura de auditoria interna. Efcaz é SaaS autônomo.

6. **Foco SRM amplo** — Executiva é especialista em terceiros operacionais. Efcaz cobre fornecedores de produtos e serviços além de mão de obra alocada.

### Vs. Executiva — Respostas a Objeções

| Objeção | Resposta |
|---|---|
| "300 auditores especializados em SESMT" | Resolve terceiros operacionais de alto risco físico. Para fornecedores de produtos/serviços, certidões automáticas + análise cadastral da Efcaz resolvem sem custo de BPO. |
| "App móvel, crachá, catraca integrados" | Módulos para controle físico em ambientes industriais. Quem não tem essa necessidade paga por complexidade que não usa. |
| "SLA de 8h para documentos de bloqueio" | Efcaz não depende de análise humana — certidões são buscadas na fonte em tempo real. |

### Quando a Executiva pode vencer
Operação com 500+ terceirizados físicos alocados, necessidade de auditoria técnica SESMT/NRs, estaleiros/indústria pesada com controle de acesso físico.

---

### Vs. Bernhoeft — Argumentos de Ataque

1. **Acessibilidade para PMEs** — Bernhoeft tem mínimo R$7–10k/módulo e barra clientes pequenos internamente. Efcaz não tem essa barreira.

2. **Certidões automáticas** — Bernhoeft também depende de postagem manual do fornecedor.

3. **RFI + Avaliação de Performance** — Bernhoeft não tem. Efcaz fecha o ciclo SRM completo.

4. **Custo total previsível** — Bernhoeft: homologação + mobilização + trabalhista + campo = mínimos acumulados. Efcaz: MRR fixo transparente por módulo.

5. **Autonomia operacional** — Bernhoeft cria dependência do time de consultoria. Efcaz: cliente opera autonomamente, CS apoia estrategicamente sem lock-in de BPO.

6. **Flexibilidade de nicho** — Bernhoeft admite dificuldade em mercados atípicos. Efcaz se adapta a diferentes setores e modelos de negócio.

### Vs. Bernhoeft — Respostas a Objeções

| Objeção | Resposta |
|---|---|
| "Monetiza risco trabalhista em R$ para a diretoria" | Efcaz atua na prevenção: Serasa + Background Check + listas restritivas identificam o fornecedor irregular antes de contratar. O risco começa na seleção, não só na gestão. API permite integrar com BI para análises avançadas. |
| "BI diário consolidado (D+1)" | BI da Bernhoeft serve compliance de terceiros operacionais. Efcaz tem relatórios nativos + API aberta para Power BI — cliente não fica preso em BI proprietário. |
| "5x Prêmio Bras, 23 anos, referência" | Referência em compliance de terceiros em mineração/energia. SRM está evoluindo para além de terceiros de obra — Efcaz cobre RFI, certidões automáticas e Selo de Confiabilidade que a Bernhoeft não tem. |
| "Consultoria integrada é o grande diferencial" | Cliente paga pela consultoria embutida mesmo sem usar todo o suporte. Efcaz tem CS dedicado por tier — apoio estratégico sem custo de BPO de 950k vidas. |

### Quando a Bernhoeft pode vencer
Grande empresa com 1000+ vidas mensais, alto risco de passivo trabalhista, mineração/energia com exigência de auditoria especializada, cliente que já usa BPO de folha da Bernhoeft.

---

## 5. Gaps da Efcaz — Oportunidades de Produto

### Explorar comercialmente (diferenciais exclusivos)
- **Busca automática de certidões** — nenhum concorrente tem. Lead de qualquer demo.
- **RFI / Avaliação de Performance** — nenhum concorrente tem. Argumento de maturidade de SRM.
- **Selo de Confiabilidade** — nenhum concorrente tem. Diferenciador de ecossistema.
- **Preço previsível (MRR fixo)** — contra variabilidade da Executiva e mínimos elevados da Bernhoeft.

### Gaps de produto a desenvolver
- **Monetização de risco em R$** — relatório de "passivo estimado de fornecedor irregular" seria argumento de C-level sem paralelo.
- **BI dinâmico consolidado** — painel D+1 nativo aumentaria percepção de valor no mid-market.
- **Parceria para SESMT** — nicho de terceiros operacionais não atendido; parceria com especialista poderia cobrir sem desenvolver internamente.
- **App móvel** — ponto cego para operações físicas; relevante em expansão para clientes industriais.

---

## Links úteis
- **Artifact publicado:** https://claude.ai/code/artifact/0a89c9bf-ce5b-424c-ae6c-06936de9ba7b
- **Documentos de origem:**
  - `Documentos/Executiva_14-07-26.txt`
  - `Documentos/Bernhoeft_04-08-26.txt`
  - `Documentos/Apresentação Institucional Executiva.pdf`
