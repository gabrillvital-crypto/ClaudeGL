# Base de Conhecimento Efcaz — Local
**Criada em:** 17/06/2026
**Fonte:** Exportações PDF da base Movidesk (https://efcaz.movidesk.com/kb/)

---

## PDFs disponíveis em `pdfs/`

| Arquivo | Conteúdo | Módulo |
|---|---|---|
| `Guia do Cliente - EFCAZ TECNOLOGIA LTDA.pdf` | Índice completo da KB com links para todos os artigos | Geral |
| `1. Conhecendo o SRM EFCAZ - EFCAZ TECNOLOGIA LTDA.pdf` | O que é SRM, tipos de acesso, fases onboarding/ongoing | Primeiros Passos |
| `7. Página inicial - Dashboard e indicadores - EFCAZ TECNOLOGIA LTDA.pdf` | Painéis do dashboard: Meus Fornecedores, Meus Terceiros, Buscas Automáticas | Primeiros Passos |
| `8. API EFCAZ – Visão Geral e Funcionalidades - EFCAZ TECNOLOGIA LTDA.pdf` | Endpoints disponíveis, autenticação, casos de uso | Integração |
| `1. Módulo pré-cadastro - Como funciona - EFCAZ TECNOLOGIA LTDA.pdf` | Fluxo de pré-cadastro: convite → fornecedor preenche → vínculo criado | Pré-cadastro |
| `2. Como criar pré-cadastro - EFCAZ TECNOLOGIA LTDA.pdf` | KB90011: passo a passo criação (4 partes: dados, contato, adicionais, mensagem/anexo), aprovação por Homologador, dúvidas frequentes | Pré-cadastro |
| `3. Pré-cadastro_ problemas relacionados a e-mail - EFCAZ TECNOLOGIA LTDA.pdf` | Problemas com e-mail no convite de pré-cadastro | Pré-cadastro |
| `1. Criação de acesso (Fornecedor) - EFCAZ TECNOLOGIA LTDA.pdf` | Como o fornecedor cria o próprio acesso | Jornada do Fornecedor |
| `2. Como cadastrar minha empresa - EFCAZ TECNOLOGIA LTDA.pdf` | Cadastro da empresa pelo fornecedor no portal | Jornada do Fornecedor |
| `3. Como inserir linha de fornecimento no cadastro - EFCAZ TECNOLOGIA LTDA.pdf` | KB90015: inserção de linha de fornecimento pelo fornecedor | Jornada do Fornecedor |
| `4. Como declarar fabricantes - EFCAZ TECNOLOGIA LTDA.pdf` | KB90016: declaração de fabricantes — própria empresa ou terceirizado, por linha de fornecimento | Jornada do Fornecedor |
| `5. Como cadastrar ou atualizar colaboradores (Gestão de Terceiros) - EFCAZ TECNOLOGIA LTDA.pdf` | KB90017: cadastro novo colaborador (10 passos) + atualização de existente (5 passos), opção N/A, contratações, regras de documentos | Gestão de Terceiros |
| `6. Como atualizar documentos - EFCAZ TECNOLOGIA LTDA.pdf` | Atualização de documentos pelo fornecedor | Jornada do Fornecedor |
| `7. Como responder RFIs (Avaliações) - EFCAZ TECNOLOGIA LTDA.pdf` | Como o fornecedor responde avaliações/RFIs | Jornada do Fornecedor |
| `8. Como tratar pendências - EFCAZ TECNOLOGIA LTDA.pdf` | Como o fornecedor trata pendências enviadas pelo cliente | Jornada do Fornecedor |
| `__ 6. Como configurar os documentos exigidos - EFCAZ TECNOLOGIA LTDA.pdf` | KB90038: criar/editar documentos, vincular a linhas de fornecimento, busca automática de certidões | Configurações |
| `__ 1. Como localizar fornecedores - EFCAZ TECNOLOGIA LTDA.pdf` | Como localizar fornecedores na plataforma (cliente) | Homologação |
| `1. Como inativar ou ativar fornecedor - EFCAZ TECNOLOGIA LTDA.pdf` | Como inativar ou reativar um fornecedor | Manutenção |

---

## Estrutura da KB Efcaz (10 seções)

1. **Primeiros Passos** — visão geral da plataforma, conceitos, tipos de acesso
2. **Pré-cadastro** — criação do primeiro vínculo com fornecedor
3. **Jornada do Fornecedor** — como o fornecedor usa o portal
4. **Homologação** — solicitações, análise, pareceres
5. **Manutenção** — atualização de documentos, renovação de certidões
6. **Configurações** — parametrização da conta, usuários, documentos obrigatórios
7. **Relatórios** — relatórios nativos e customizados
8. **Avaliações** — módulo de performance (RFI)
9. **Ocorrências** — registro e gestão de falhas de fornecimento
10. **Suporte** — canais de atendimento e abertura de chamados

---

## Artigos-chave por tema

### Linha de Fornecimento (KB90015 / KB99015)

**Artigo local:** [`linha_de_fornecimento.md`](linha_de_fornecimento.md)

- **O que é:** categoria específica do produto ou serviço que o fornecedor oferece (diferente do ramo de atividade, que é genérico)
- **Quem define o catálogo:** a empresa contratante (cliente), via Configurações > Linhas de Fornecimento
- **Quem seleciona:** o fornecedor, durante o cadastro em Geral > Linha de Fornecimento > Adicionar Linha
- **Tipos:** Material (produto físico) ou Serviço
- **Vínculo com Terceiros:** colaboradores devem ser associados a uma linha de fornecimento; cada linha com prestação deve ter ao menos 1 colaborador
- **Bloqueio:** o cliente pode bloquear a edição pelo fornecedor
- **Pré-requisito para alterar:** solicitação em aberto (botão Continuar Preenchimento / Resolver / Alterar visível); se status for "Aguardando análise" ou "Em análise" → não é possível alterar
- **Analogia para clientes:** "etiqueta de categoria" — em vez de saber só o setor, você sabe exatamente o que a empresa fornece

---

### Pré-cadastro de Fornecedores (KB90011)

- **Criação:** Menu lateral > Pré cadastro - Pedido de Homologação > Novo
- Tela tem 4 partes: (1) Dados do fornecedor — ao informar CNPJ/CPF, sistema faz análise de risco automática; (2) Dados de contato — e-mail é obrigatório, é pelo e-mail que o convite é enviado; (3) Informações adicionais — linha de fornecimento (pode adicionar múltiplas); (4) Mensagem e anexos — vai apenas para o aprovador, NÃO para o fornecedor
- Finalização: **Salvar** = rascunho; **Enviar para análise** = envia para aprovação
- **Aprovação:** apenas usuários com perfil **Homologador** podem aprovar; ao aprovar, mensagem é enviada ao fornecedor por e-mail
- Dado errado antes da aprovação: pode editar livremente. Após aprovado: apenas o fornecedor pode atualizar (com limitações)
- E-mail errado após envio: excluir o pré-cadastro e recriar
- **Ramo de atividade** (geral, ex: Indústria farmacêutica) ≠ **Linha de fornecimento** (específica, ex: Vitaminas)

### Documentos e Vencimento
- KB sobre Homologação → fluxo: Solicitação → Análise → Parecer → status atualizado
- Dashboard (KB90007) → "Terceiros com Certidões Vencidas" só reflete certidões com análise concluída

### Terceiros — Gestão de Colaboradores (KB90017)

**Conceito:** Terceiros = colaboradores (pessoas físicas) da empresa fornecedora que prestam serviço diretamente para a contratante.

**Pré-requisito:** Precisa existir uma solicitação em aberto (botões "Continuar Preenchimento", "Resolver" ou "Alterar" visíveis). Se status for "Aguardando análise" ou "Em análise" → não é possível fazer alterações.

**Cadastrar NOVO colaborador:**

1. Dados da Empresa > Colaboradores > **Adicionar**
2. Selecionar linha de fornecimento (se não tiver opção, precisa adicionar na empresa primeiro)
3. Preencher identificação: CPF + nome completo (pessoa física), Salvar e Avançar
4. Endereço (CEP preenche campos automaticamente), Salvar e Avançar
5. Contato: telefone + e-mail (pode adicionar múltiplos clicando em Adicionar), Salvar e Avançar
6. Documentos: asterisco vermelho = obrigatório; apenas **1 arquivo por aba** (zipar ou unir PDFs se necessário); opção **N/A** (Não se aplica) com justificativa obrigatória se documento não se aplica
7. Contratações (opcional): Nova contratação > preencher > Salvar
8. Fechar janela do colaborador (X canto superior direito)
9. Enviar para Aprovação

**Atualizar colaborador existente:**

1. Dados da Empresa > Colaboradores > ícone de lápis (pesquisar por nome ou CPF)
2. Editar abas Identificação, Endereço, Contato → clicar "Salvar e Avançar" em cada uma
3. Para atualizar Documentos: expandir aba, clicar **"Novo"** para desbloquear campos, preencher, Salvar
4. Fechar janela (X) > Enviar para Aprovação

**Regras importantes:**

- Cada linha de fornecimento com prestação de serviço deve ter ao menos 1 colaborador associado
- Um mesmo colaborador pode estar em várias linhas de fornecimento
- Vários colaboradores podem estar na mesma linha de fornecimento
- Após envio: empresa contratante analisa; se houver pendências, fornecedor é notificado para corrigir

Dashboard mostra painel "Meus Terceiros" separado de "Meus Fornecedores"

- Indicadores: Terceiros Cadastrados / Terceiros com Certidões Vencidas

### Relatórios Customizados
- Disponível em Relatórios > Customizados (funcionalidade em desenvolvimento/entregue 2026)
- Exportação em Excel

### API
- Endpoints: buscar fornecedores, fornecedor com documento vencido, solicitações, pedido de homologação, avaliações
- Autenticação via token fornecido pela Efcaz

### Módulo de Contratos e Reprovação Definitiva (jul/2026)

**Artigo local:** [`modulo_contratos_e_reprovacao_definitiva.md`](modulo_contratos_e_reprovacao_definitiva.md)

- **Módulo Contratos:** centraliza contratos de fornecedores/terceiros — vigências, aditivos, medições, documentos
- **Fase 1 (jul/2026):** disponível somente dentro do fornecedor; sem análise na solicitação; sem notificações de vencimento
- **Fase 2 (ago/2026):** integração com histórico de solicitações prevista para 2ª quinzena de agosto
- **Configuração:** Configurações > Documentos (criar docs internos e do fornecedor) → vincular linhas → menu Fornecedor > aba Contratos
- **Reprovação Definitiva:** novo status de análise que bloqueia permanentemente novo fornecedor; apenas em solicitações de novo fornecedor; workaround para reverter: cancelar encaminhamento
- **Filtro Responsável análise:** novo filtro na tela de Solicitações para filtrar por analista

---

> **Como adicionar:** salvar o PDF do artigo Movidesk em `../Documentos/` e registrar neste índice.
