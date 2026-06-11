# Reuniões e Planos de Ação — Carteira Efcaz

Registro centralizado de resumos de reuniões e planos de ação sugeridos.
Atualizado por Gabriel com apoio do agente CS.

---

## Índice

| Data | Cliente | Tipo | Status PA |
|---|---|---|---|
| 22/05/2026 | Zurich Airport | Ajuste de relatórios / Dores da cliente | Em andamento — follow-up 29/05 |
| 18/05/2026 | Bom Futuro × Afonso França | Bench (peer learning) | Em andamento |
| ~18/05/2026 | ISG | Ongoing / Risco | Em andamento |

---

## 22/05/2026 — Zurich Airport: Ajuste de Relatórios

**Tipo:** Alinhamento de produto / Gestão de dores — Módulo Terceiros
**Horário:** 10h00 (GMT-03:00)
**Follow-up marcado:** 29/05/2026 às 11h

### Participantes

| Empresa | Participante | Papel |
|---|---|---|
| **Zurich Airport** | Débora Coelho de Jesus | Gestão de terceiros (champion) |
| **Efcaz** | Gabriel Lucas Vital Evangelista | CS Specialist |
| **Efcaz** | Thais Jayne Biscaia | CS / Operações |
| **Efcaz** | Marielle Silva de Cuellar | CS / Operações |
| **Efcaz** | Renato Pedroso | Gerência |
| **Efcaz** | Ricardo Pedroso da Silva | Produto |
| **Efcaz** | Janaina Ventura | Presente |

---

### Contexto

Débora vem pedindo os mesmos ajustes desde dezembro/2025 — são **5 meses sem resolução**. A reunião foi convocada para ela apresentar ao vivo o que não está funcionando. Tom da reunião foi mais firme do que o usual (Cláudia não estava presente desta vez).

---

### Pontos de melhoria levantados pela Débora (transcrição literal)

#### 1. Falta de competência nos relatórios — dor principal

> *"Competência é uma coisa que a gente tá batendo já há algum tempo e não tá vindo."*
> *"Se vocês não trazem a competência do que tá pendente, em que momento que o fornecedor vai inserir? Aonde que ele vai inserir? Qual é a janela, qual é a linha que ele vai inserir? Qual que é a caixinha?"*

Ela mostrou documentos de Ficha de EPI, Ordens de Serviço, SESMT na tela e perguntou "de qual competência é esse aqui?" — sem conseguir responder. Sem saber o mês de referência, nem ela nem o fornecedor sabe o que fazer.

**Impacto:** os fornecedores ficam perdidos e acabam não corrigindo. Débora acredita que **grande parte da inadimplência é causada por essa confusão**.

---

#### 2. Coluna "Marcas e representações" não é intuitiva

> *"Concorda comigo que marca e representação, ela não me lembra em nenhum momento competência. Eu não posso dizer que essa coluna de marca e representação se refere à competência. Em que momento o fornecedor vai descobrir isso?"*

Ricardo confirmou que "Marcas e representações" é a coluna de competência. Débora pediu que o nome seja alterado para algo óbvio. Ela estendeu o argumento para outros elementos de UX da plataforma.

---

#### 3. UX não intuitiva — os "três pontinhos"

> *"Não, eu não posso ficar imaginando que aqui vai ter alguma coisa para eu clicar. Eu também não posso esperar que o fornecedor fique adivinhando."*

Funcionalidades escondidas atrás de menus contextuais (os "três pontinhos") foram citadas como barreira tanto para ela quanto para os fornecedores. Ela comparou: assim como ela não deveria precisar adivinhar, o fornecedor também não consegue.

---

#### 4. Relatório não visual — impossível de fazer leitura gerencial

> *"Não é visual, sabe? Eu vejo um monte de letrinhas assim. Eu não consigo identificar. Isso aqui é de SESMT. Ele poderia vir aqui alguma coisa referente o que que é SESMT, entendeu?"*
> *"Eu confesso que isso para mim tá bem confuso."*

A nomenclatura dos documentos é muito técnica e internamente gerada (ex: "Capacitação de acordo com a ordem de serviço. Assinatura deve ser manuscrita."). Débora não consegue identificar o que é cada pendência só pelo nome que aparece no relatório.

---

#### 5. Dashboard apenas informativo — sem drill-down

> *"Ele só é informativo, tá? Não consigo clicar e visualizar nada. Ele não tá aí aqui eu... OK."*

O dashboard existente na plataforma mostra números agregados mas não permite clicar para ver o detalhe. Para Débora, isso não resolve — ela precisa saber **o quê** está pendente, **de quem**, **de qual mês**.

---

#### 6. Percentual de não conformidade por fornecedor

> *"Eu preciso saber o percentual do fornecedor para eu chegar o fornecedor: 'Você tá ali, ó, com 40% de não conformidade. São esses documentos que você precisa atuar.'"*
> *"Como que eu vou colocar um relatório assim numa notificação?"*

Ela quer poder enviar ao fornecedor um número direto de não conformidade para usar nas cobranças. Hoje isso não existe na plataforma nem nos relatórios.

---

#### 7. Status em 3 camadas — não 2

Marielle sintetizou o que Débora quer:

> *"O documento tá vencido, se o documento tá pendente de postagem ou se o documento está aprovado."*

Mapeamento:
- **Conforme / Aprovado** — documento analisado e regular
- **Pendente** — documento esperado mas ainda não postado pelo fornecedor
- **Vencido** — documento vencido (risco real)

A plataforma hoje só distingue EM_ELABORAÇÃO e APROVADO — não separa "não postou" de "vencido".

---

#### 8. Relatório precisa ter data

> *"Todo relatório, sendo o PDF, o Excel, enfim, eu prefiro que seja em PDF ou que seja assim no corpo do e-mail, né? Mas ele precisa ter data."*

O motivo é jurídico: ela precisa provar em processo trabalhista que em determinado dia ela solicitou e o fornecedor não entregou. Sem data, o relatório não tem valor como evidência.

---

#### 9. Extração de relatório on-demand a qualquer momento

> *"Eu preciso ter a opção de: aqui, agora eu quero tirar um relatório."*

Ela quer autonomia para gerar o relatório quando precisar — não apenas receber o que a Thaís envia por e-mail. O fluxo atual é dependente de uma pessoa da Efcaz fazer isso manualmente.

---

#### 10. Histórico de 2 anos por competência

> *"Eu preciso saber desse histórico... Nas próximas atuações com fornecedor, eu vou falar assim: 'Fornecedor, dezembro tu tá faltando isso, isso e aquilo, janeiro tu tá faltando isso e isso, fevereiro tá faltando isso e isso.'"*

Ela apresentou um gráfico do modelo antigo que mostrava o % de não conformidade mês a mês. Quer ver a evolução histórica para usar em reuniões de cobrança e em apresentações para a diretoria.

---

#### 11. Relatório mesmo quando o fornecedor não postou nada

> *"Independente do fornecedor enviar a solicitação ou não, ele tem que receber relatório. Mesmo que ele não tenha feito nada na plataforma, eu preciso receber. Ele precisa receber: 'Ó, você está na calência [pendência] de dezembro, janeiro, fevereiro, março, abril e maio.'"*

Ela quer que o relatório seja enviado automaticamente todo mês, independentemente de ação do fornecedor. Isso serve como prova de que a Zurich está fiscalizando. Sem esse registro: "A gente tá ficando muito exposto."

---

#### 12. Lista de colaboradores por competência — benefício fiscal Prefeitura de Natal

> *"Eu preciso ter um eu tirar um relatório da quantidade de colaboradores. Eu quero lista de colaboradores que atuaram no mês de dezembro ou no mês de janeiro."*
> *"A gente tem o benefício fiscal Natal e a gente precisa apresentar relatórios de colaboradores. Isso já virou um problema pra gente."*

Colunas necessárias no relatório: contrato, filial, razão social do fornecedor, competência, CPF, nome do colaborador. Periodicidade: a cada 3–4 meses. Ricardo confirmou que os dados estão na plataforma — falta só a filtragem por competência.

---

#### 13. CNPJs duplicados — Graber e Caruana

> *"A Graber eu tenho um contrato só com eles."*

Dois fornecedores aparecem com 2 CNPJs no sistema. Débora sinaliza que a Graber tem apenas um contrato — o segundo CNPJ provavelmente é um cadastro antigo. Pede limpeza/investigação.

---

#### 14. Relatório deve ter identificação de contrato (múltiplos contratos por fornecedor)

> *"Eu tenho a Focus, eu tenho vários contratos: contrato de recepção, contrato de vigilância, contrato de terminal de cargas. É importante que a gente identifique."*

Fornecedores com múltiplos contratos precisam que o relatório filtre por número de contrato, não só por razão social.

---

#### 15. Webinar só depois dos ajustes — não antes

> *"Eu acredito que o webinar ele vai fazer mais sentido quando todos esses ajustes na plataforma estiverem realizados. Não adianta a gente ficar fazendo o webinar explicando e chega na hora de executar o fornecedor ele não consegue."*

Débora vetou novos treinamentos enquanto as questões acima não estiverem resolvidas. Webinar agora geraria frustração, não engajamento.

---

### Diagnóstico interno (após saída da Débora)

- **Renato:** *"Basicamente eles não conseguem cobrar os fornecedores porque eles não sabem o que cobrar. Eles ficam de mãos atadas."*
- **Ricardo (produto):** A questão da competência é **estrutural** — a plataforma foi adaptada para receber documentos à medida que chegam, não para abrir competências previamente como a plataforma anterior da Zurich fazia. Mudar isso exige desenvolvimento.
- **Gabriel (CS):** Propôs criar um relatório/BI mais robusto como **paliativo** para ganhar tempo enquanto o produto evolui. Ricardo validou: os dados estão na base, é viável extrair.
- **Thaís:** Já envia um relatório compilado manualmente toda semana, baseado em um print parcial do modelo que a Débora enviou. Ele é parecido com o que ela quer, mas falta competência visível e os gráficos de % conformidade.
- **Ação interna:** Thaís vai compartilhar acesso ao SG3 (concorrente) para Ricardo analisar como estruturam os relatórios de terceiros.

---

### Plano de Ação

| # | Ação | Responsável | Prazo |
|---|---|---|---|
| 1 | Apresentar dashboard como solução interim na reunião de follow-up | Gabriel | 29/05/2026, 11h |
| 2 | Adicionar % de não conformidade por fornecedor no dashboard HTML | Gabriel | Antes de 29/05 |
| 3 | Solicitar à Débora o PDF completo do modelo de relatório que ela usa | Thaís / Gabriel | Imediato (por e-mail — ela tá sem celular) |
| 4 | Mapear o que o relatório manual da Thaís já entrega vs. o que falta | Thaís | Antes de 29/05 |
| 5 | Ricardo analisar SG3 (concorrente) para benchmark de relatórios de terceiros | Ricardo | Final de semana 24–25/05 |
| 6 | Definir escopo de desenvolvimento da plataforma para competências | Ricardo + Renato | Após 29/05 |
| 7 | Investigar CNPJs duplicados de Graber e limpar cadastro | Thaís | A definir |
| 8 | Ajustar nome da coluna "Marcas e representações" → algo intuitivo relacionado a competência | Ricardo (produto) | A definir |
| 9 | Criar relatório automático mensal de colaboradores por competência (Prefeitura de Natal) | Ricardo | A definir — urgente para Débora |

---

### Sinais de risco

- 🔴 **5 meses sem entrega** da necessidade principal (competência nos relatórios)
- 🔴 Débora usou a palavra "objeto da plataforma se perde" — questiona o valor do produto
- 🔴 Zurich tem prazo com fornecedores estipulado e a plataforma não está apta para suportar a cobrança
- 🟡 Benefício fiscal com Prefeitura de Natal em risco por falta do relatório de colaboradores
- 🟡 Fornecedores "perdidos" — inadimplência pode ser consequência da falta de clareza, não de má vontade

---

## 18/05/2026 — Bench: Bom Futuro × Afonso França

**Tipo:** Peer learning — gestão de documentos
**Facilitador:** Gabriel (Efcaz)
**Duração:** ~44 min

### Participantes

| Empresa | Participantes |
|---|---|
| **Afonso França** (referência) | Karine (analista de homologação) |
| **Bom Futuro** | Cairo Fabricio, Camila Borges Queiroz, Patricia Nascimento, Sherman Vendramini, Hevair Rodrigues, Mairon Silva Marques da Conceição, Yasmin Ribeiro |

### O que a Karine apresentou

**Fluxo de pré-cadastro**
Afonso França faz o pré-cadastro internamente (não deixa o fornecedor submeter sozinho). O canal oficial é a plataforma; e-mail é complementar. Motivo: controle e rastreabilidade.

**Estrutura de categorização de documentos**
Desenvolvida em reunião com jurídico e contábil. Dois níveis:
- **Ramo de atividade** (macro) → documentos básicos obrigatórios para todos
- **Linha de fornecimento** (micro) → documentos específicos por segmento

Hoje: **269 linhas** e **45 documentos ativos**. A estrutura é "viva" — muda continuamente conforme novas demandas aparecem. Conselho da Karine: *comece pelo macro, depois vá pro micro.*

**Integração com o ERP (Lumina)**
O Efcaz alimenta diretamente o Lumina (sistema de orçamentos e pagamentos). Quando um documento vence no Efcaz, a qualificação cai automaticamente no Lumina — o comprador não consegue usar aquele fornecedor até regularizar.

**Outras práticas destacadas**
- Três status de análise: deferido / deferido com ressalva / indeferido
- Ressalva baseada em CND Federal (alguma anotação = não passa 100%)
- Chamado de "socorro" para contábil, jurídico ou SGI quando há dúvida em análise
- Dossiê do fornecedor: documentos + datas de vencimento + extrato Serasa
- Atualização automática: CND Federal (180 dias) e Estadual funcionam; Municipal não

### Dores confirmadas do Bom Futuro

1. **Estrutura de categorização ainda não definida** — Tentaram trabalhar só por linha de fornecimento, mas ficou granular demais para a complexidade do negócio deles (agricultura + obras + usina hidrelétrica + material civil). Estão tentando migrar para ramo de atividade.
2. **Licenças vs. volume de trabalho** — Cairo levantou preocupação com custo de licenças vs. esforço de cobrar fornecedores e acompanhar certificações.
3. **Inconsistência na consulta de Simples Nacional** — Caso em que a plataforma exibiu informação divergente da API pública (optante vs. não optante). Patricia confirma que consulta manualmente para garantir. Sherman: dado divergente é mais crítico do que dado não carregado.
4. **Bloqueio judicial em contas bancárias** — Cadastraram fornecedor com conta bloqueada judicialmente, gerou transtorno. Cairo perguntou se existe consulta preventiva para isso na plataforma.

### Plano de Ação

| Ação | Responsável | Prazo | Status |
|---|---|---|---|
| Call de BPO com Thaís (líder de BPO Efcaz) | Gabriel agenda | 19/05 — 14h30–15h30 Brasília | Agendada ✓ |
| Verificar se existe consulta de bloqueio judicial na plataforma | Gabriel | Trazer na call de 19/05 | Pendente |
| Trazer exemplo concreto da inconsistência do Simples Nacional | Cairo / Patricia | Na call de 19/05 | Pendente |
| Enviar gravação da bench para Bom Futuro | Gabriel | 18–19/05 | Pendente |

### Sinais estratégicos

- **Oportunidade BPO real:** Cairo reconhece que o volume e complexidade do negócio favorecem o BPO. Camila está engajada. Cairo entra de férias em 25/05 — urgência para avançar antes.
- **Gestão de Terceiros não usada:** Bom Futuro usa o Lumina para terceiros, não o Efcaz. Oportunidade futura.
- **Risco de confiança:** O caso do Simples Nacional gerou desconfiança — Sherman é o mais cético. Thaís precisa chegar com resposta clara sobre confiabilidade das consultas.

---

## ~18/05/2026 — ISG × Efcaz

**Tipo:** Ongoing — reunião de risco
**Participantes:** Equipe ISG + Gabriel (Efcaz)
**Contexto:** Proposta de BPO rejeitada pelo cliente. Contato principal (Carlos) ausente na reunião — sinal de alerta.

### Dores identificadas

- Baixa adesão dos fornecedores ao portal
- Sobrecarga de análise manual
- Confiabilidade de certidões questionada (Cadin + Idônia)
- Restrição orçamentária limitando expansão

### Posição da Efcaz

- Comprometeu-se com suporte para adesão de fornecedores
- Apresentou valor do BPO como serviço para reduzir carga operacional
- Identificou Cruzeiro (hospital da base) como oportunidade de expansão e argumento para BPO

### Plano de Ação

| Ação | Responsável | Prazo | Status |
|---|---|---|---|
| Follow-up com Carlos (contato principal ausente) | Gabriel | A definir | Pendente |
| Apresentar proposta revisada considerando restrição orçamentária | Gabriel | A definir | Pendente |
| Explorar oportunidade Cruzeiro como argumento para BPO | Gabriel | A definir | Pendente |

### Sinais estratégicos

- **Risco de churn:** Alto. Carlos ausente + proposta BPO rejeitada + restrições orçamentárias.
- **Ponto de atenção:** Sem engajamento renovado, renovação pode estar em risco.

---

*Para adicionar nova reunião: copie o bloco de template abaixo e preencha.*

---

## TEMPLATE — Nova Reunião

```
## DD/MM/AAAA — [Cliente] × Efcaz

**Tipo:** [Ongoing / QBR / Bench / Risco / BPO]
**Participantes:** [Nome, cargo]
**Contexto:** [Uma frase sobre o motivo da reunião]

### Dores identificadas
-

### Pontos discutidos
-

### Plano de Ação

| Ação | Responsável | Prazo | Status |
|---|---|---|---|
| | | | Pendente |

### Sinais estratégicos
- **Risco/Oportunidade:**
```
