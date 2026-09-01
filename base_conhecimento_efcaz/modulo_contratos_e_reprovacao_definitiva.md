# Módulo de Contratos, Reprovação Definitiva e Fase 2

**Fontes:** News interna Efcaz — Ricardo Pedroso (PO), 21/07/2026 (Fase 1) | 27/08/2026 (Fase 2)
**Seção:** Configurações / Homologação
**Público:** Usuários contratantes (clientes)

---

## Novo Módulo de Contratos

### O que é

O módulo **Contratos** centraliza contratos vinculados a fornecedores e terceiros dentro da plataforma, permitindo:

- Controle de vigência contratual e aditivos
- Controle de medições, anexos e evidências operacionais
- Gestão de documentos obrigatórios do contrato e do fornecedor

### Fase 1 (liberação atual — jul/2026)

O módulo está disponível **somente dentro do fornecedor** — ainda não faz parte de uma solicitação. O fornecedor pode visualizar e inserir documentos de contrato, mas a análise dentro da solicitação ainda não está disponível.

### Fase 2 (liberada em ago/2026)

Contratos agora são **gerados e alterados dentro da solicitação**, como é o fluxo padrão da plataforma. Notificações de vencimento também passaram a funcionar:
- **Contratos internos:** notificação enviada aos administradores
- **Contratos - fornecedor:** notificação enviada ao fornecedor quando o documento vencer

---

### Como configurar e usar

**Passo a passo de ativação:**

1. **Defina se haverá documentos no módulo de contratos.** Se sim, acesse **Configurações > Documentos** e crie:
   - Documentos de **controle interno** (visíveis só para você — não para o fornecedor)
   - Documentos que o **fornecedor deve inserir** (visíveis e obrigatórios para ele)

2. **Vincule as linhas de fornecimento** que estarão associadas a cada documento — mesma lógica dos demais módulos.

3. **Acesse o menu Fornecedor**, busque o fornecedor desejado e abra a aba **"Contratos"**. Clique em **Adicionar** e preencha os dados do contrato:
   - Nome do contrato
   - Local de referência
   - Vigências
   - Valor e tipo de reajuste
   - Linha de fornecimento vinculada

4. **Defina se o contrato será exibido ao fornecedor/terceiro.** Se sim:
   - O fornecedor visualiza a aba Contratos — mas **não pode alterar dados gerais**
   - Documentos que o fornecedor deve inserir ficam na aba **"Documentos contrato/obras/outros"**
   - O fornecedor insere os documentos pelo menu Empresas > visualizar > aba Contratos

5. **Se o módulo de Terceiros estiver ativo:** o contrato pode ser vinculado ao terceiro dentro da aba de Contratações, a partir de uma solicitação de novo fornecedor.

---

### Status atual (ago/2026)

| Item | Situação |
|---|---|
| Contratos dentro da solicitação (Fase 2) | ✅ Disponível |
| Notificações de vencimento (admin/fornecedor) | ✅ Disponível |
| Fornecedor originar dados do contrato | ❌ Nunca — quem insere é o cliente |
| Análise de documentos de contrato dentro da solicitação | ❌ Ainda indisponível |
| Exibição ao fornecedor | ✅ Disponível (opcional por contrato) |

> **Workaround enquanto análise de docs de contrato não está disponível:** use o módulo de **Ocorrências** (gerar uma ocorrência ao fornecedor) ou crie uma solicitação e **indira**, orientando o passo a passo.

> **Ativação:** o módulo está disponível mediante contratação. Agendar com o CS da conta para cotação e ativação.

---

## Nova Situação de Análise: "Reprovação Definitiva"

### O que é

Status de análise que **reprova definitivamente** um novo fornecedor, impedindo a criação de novas solicitações para ele.

### Quando usar

Use **apenas** quando o fornecedor não será homologado e **não poderá retornar com correções**. Exemplos:

- Fornecedor com irregularidades graves e definitivas
- Fornecedor que não atende critérios mínimos de homologação de forma permanente

> ⚠️ **Antes de usar:** gere uma pendência ao fornecedor descrevendo os motivos da reprovação total. A plataforma enviará um e-mail ao fornecedor notificando a reprovação definitiva e as pendências.

### Onde aparece

Disponível **somente em solicitações de novo fornecedor** — não aparece em solicitações de atualização.

### Como reverter (se necessário)

Se em algum momento quiser retomar o fornecedor:

1. **Cancele o encaminhamento** — a solicitação volta para análise
2. A partir daí é possível **indeferir** normalmente, permitindo que o fornecedor retorne com correções

---

## Novo Filtro: Responsável pela Análise

Na tela de **Solicitações**, há um novo filtro chamado **"Responsável análise"** que permite filtrar solicitações pelo analista responsável pela análise.

Útil para gestão de fila de análise em equipes com múltiplos analistas.

---

## Outras melhorias (jul/2026)

| Melhoria | Detalhe |
|---|---|
| Mensagem de cadastro sem telefone | Usuário que não inseriu telefone no login agora recebe orientação de onde clicar para complementar |
| Texto do dossiê em falha de certidão | Texto ajustado para ser mais claro quando há falha na obtenção de certidão automática |
| Botão "Enviar para análise" | Cor e texto ajustados para dar mais ênfase ao fornecedor — incentiva o clique |
| Modal de orientação ao resolver pendência | Ao clicar em "Resolver" após indeferimento, aparece um modal com passo a passo do que o fornecedor deve fazer |

---

## Relação com outros artigos da KB

- [`documentos_exigidos.md`](documentos_exigidos.md) — como criar e configurar documentos (pré-requisito para o módulo de contratos)
- [`linha_de_fornecimento.md`](linha_de_fornecimento.md) — como vincular linhas aos documentos de contrato

---

*Fonte: News interna Efcaz — Ricardo Pedroso (PO), 21/07/2026*
