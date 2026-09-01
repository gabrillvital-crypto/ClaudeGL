# Competências no Módulo de Terceiros

**Fonte:** News interna Efcaz — Ricardo Pedroso (PO), 27/08/2026
**Seção:** Gestão de Terceiros / Configurações
**Público:** Usuários contratantes (clientes) com módulo de Terceiros ativo

---

## O que é

Nova funcionalidade que permite incluir **competências** dentro do módulo de terceiros, adicionando uma camada de controle periódico (mensal, por exemplo) sobre a documentação dos colaboradores terceirizados.

Permite:
- Gerir terceiros por competência (mês, período, contrato) e não apenas pelo cadastro geral
- Solicitar documentos específicos da competência (ficha ponto, folha de pagamento, etc.)
- Aprovar por terceiro dentro de cada competência específica
- Receber declaração de **não atividade** do fornecedor quando não houve movimentação na competência

> **Relevância imediata:** clientes BPO como **Zurich Airport** (que já usa conceito de competências mensais) são os principais candidatos. A funcionalidade resolve diretamente a dor de controle documental periódico de prestadores.

---

## Como configurar (4 passos)

### 1. Criar as competências
- Acesse **Configurações > Competências**
- Crie todas as competências que estarão ativas no ambiente (ex: JULHO/2026, AGOSTO/2026, SETEMBRO/2026)
- ⚠️ **Regra mensal:** se forem competências mensais, o mês anterior precisa ser criado todo mês para que fique ativo e visível ao fornecedor

### 2. Habilitar a opção globalmente
- Acesse **Configurações > Configurações Gerais**
- Ative: **"Habilitar competências na solicitação de terceiros"**

### 3. Configurar os documentos de competência
- Acesse **Configurações > Documentos**
- Selecione um documento do tipo **Terceiro**
- O campo **"Solicitar dentro da competência do terceiro"** ficará visível → marcar **Sim**
- Vincule o documento à linha de fornecimento correspondente (obrigatório)
- Exemplos de documentos típicos: ficha ponto, folha de pagamento, recibo de férias, comprovante de EPI

### 4. Resultado na interface
Após ativar, a aba **Gestão de Terceiros** se subdivide em duas sub-abas:

| Sub-aba | O que contém |
|---|---|
| **Dados Gerais** | Cadastro do terceiro: dados pessoais, endereço, contatos, contratações, documentos gerais cadastrais |
| **Documentos por Competência** | Vínculo do terceiro às competências + documentação exigida por competência (ficha ponto, folha de pagamento etc.) |

---

## Funcionalidades da aba de Competências

- **Aprovações por competência:** é possível aprovar a documentação de cada terceiro dentro de uma competência específica (ex: aprovar a folha de pagamento do terceiro João em Agosto/2026)
- **Declaração de não atividade:** o fornecedor pode informar que não houve atividade naquela competência — sem precisar enviar documentos
- **Visualização resumida:** a listagem mostra, por competência, a quantidade de terceiros e o status (regulares vs. com pendências)

---

## ⚠️ IMPORTANTE — Impacto ao ativar

> **Ao ativar competências, a interface muda imediatamente para o fornecedor.** A Efcaz recomenda **comunicar os fornecedores previamente** antes de ativar, para evitar confusão.

---

## Dor que resolve

| Problema do cliente | Como a funcionalidade resolve |
|---|---|
| Controle mensal de documentação de terceiros feito em planilha | Centraliza na plataforma, com histórico por competência |
| Fornecedor não envia ficha ponto e folha de pagamento mensalmente | Solicitação automática por competência, fornecedor recebe notificação |
| Dificuldade em identificar terceiros com pendências em competências específicas | Dashboard por competência mostra regulares vs. com pendências |
| Auditoria de conformidade trabalhista por período | Histórico de aprovação por competência rastreável |

---

## Comercial

- Funcionalidade disponível para clientes com o **módulo de Terceiros ativo**
- Verificar se a ativação de competências requer configuração adicional ou se está inclusa no contrato de Terceiros
- Candidatos imediatos: **Zurich Airport**, Lactalis, qualquer cliente com BPO de mão de obra

---

## Artigos relacionados

- [`terceiros_colaboradores.md`](terceiros_colaboradores.md) — cadastro e atualização de colaboradores
- [`modulo_contratos_e_reprovacao_definitiva.md`](modulo_contratos_e_reprovacao_definitiva.md) — contratos vinculáveis a terceiros na aba de contratações
- [`fluxo_pendencias.md`](fluxo_pendencias.md) — fluxo quando há pendência em documentos de competência

---

*Fonte: News interna Efcaz — Ricardo Pedroso (PO), 27/08/2026*
