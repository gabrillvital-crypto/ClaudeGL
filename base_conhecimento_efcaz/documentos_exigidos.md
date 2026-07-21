# Como configurar os documentos exigidos

**KB de referência:** KB90038
**Seção:** Configurações e parametrizações gerais (Guia do Cliente)
**Público:** Usuários com perfil de administrador/configurador

---

## O que este artigo cobre

- Criar ou editar documentos solicitados aos fornecedores
- Vincular documentos a linhas de fornecimento ou ramos de atividade específicas
- Ativar modelos prontos e busca automática de certidões

---

## Como criar um novo documento

**Caminho:** Menu lateral > **Configurações > Documentos**

A tela exibe todos os documentos já cadastrados.

- Clique em **Novo** para cadastrar um novo documento
- Clique no **ícone de lápis** para editar um documento existente

> **Dica:** a coluna "Background Check" indica quais documentos são de busca automática (certidões) e quais são manuais (upload pelo fornecedor).

---

### Campos obrigatórios

| Campo | O que preencher |
|---|---|
| **Título** | Nome do documento exibido ao fornecedor |
| **Subtítulo** | Complemento opcional do nome |
| **Descrição** | Orientação adicional para o fornecedor |
| **Situação** | Ativo (visível) ou Inativo (oculto) |
| **Texto de pendência de reprovação** | Texto pré-carregado automaticamente quando o documento for reprovado — agiliza o processo de análise |
| **Ordem** | Define prioridade de exibição — quanto menor o número, mais acima aparece |
| **Tipo de Documento** | Usado para Marcas e Representações |
| **Solicitar documento ao** | Fornecedor, Fabricante ou Terceiro (conforme módulo ativo) |

---

### Opções adicionais

| Opção | Efeito |
|---|---|
| Exigir data de validade | Fornecedor deve informar a validade do documento |
| Exigir número | Fornecedor deve informar o número do documento |
| Exigir anexo | Fornecedor deve obrigatoriamente anexar o arquivo |
| Exibir no Certificado Cadastral | Documento aparece no certificado emitido |
| Restringir a fornecedores brasileiros / estrangeiros | Filtra por nacionalidade do fornecedor |
| Permitir N/A (Não se aplica) | Fornecedor pode marcar como não aplicável com justificativa |
| Categorizar documento | Agrupa por categoria na listagem |
| Tipo de pessoa | Exibir para pessoa física e/ou jurídica |
| Restringir a determinados usuários | Apenas usuários selecionados visualizam o documento |
| **Link de acesso** | Inclui link direto para o fornecedor obter o documento (ex: site da Receita Federal) |
| **Anexar modelo** | Permite subir um documento modelo para o fornecedor baixar e preencher |

> Se o usuário que deseja remover da visualização não aparecer na lista, entre em contato com o suporte.

---

## Como vincular documentos a linhas de fornecimento

Esse vínculo faz com que o documento seja exibido **somente** para fornecedores daquela categoria — tornando a homologação mais direcionada e eficiente.

**Passos:**

1. Em **Configurações > Documentos**, clique no ícone de lápis do documento desejado
2. Desça a página até as seções **Ramos de Atividade** e **Linhas de Fornecimento**
3. Para cada linha ou ramo:
   - **Quadradinho da esquerda (Apresentar):** marca o vínculo — o documento será exibido para essa categoria
   - **Quadradinho da direita (Obrigatório):** se marcado, o fornecedor não consegue concluir o cadastro sem preencher ou anexar o documento
4. Clique em **Salvar**

> Um documento pode ser vinculado (apresentado) sem ser obrigatório — ele aparece, mas o fornecedor pode ignorar.

---

## Modelos prontos + Busca automática de certidões

A Efcaz coleta automaticamente diversos documentos diretamente dos órgãos governamentais — o fornecedor não precisa enviar manualmente.

**Para ativar:** entrar em contato com o analista de CS ou com o suporte.

**Documentos obtidos automaticamente:**

- Cartão CNPJ / Cartão CPF
- CRF – FGTS
- CND Federal
- CND Estadual
- Certidão Negativa de Débitos Trabalhistas (CNDT)
- Comprovante de Inscrição Sintegra
- IBAMA – Certidão Negativa de Débitos
- IBAMA – Certidão Negativa de Embargos
- IBAMA – Consulta de Regularidade
- CGU – Certidão Negativa Correcional (CEIS)
- TJSP – Certidão de Distribuição Cível em Geral
- CERTIDÃO CÍVEL – TRF3 (Abrangência Regional, SP, MS, Tribunal da 3ª região)
- CERTIDÃO CRIMINAL – TRF3 (Abrangência Regional, SP, MS, Tribunal da 3ª região)

---

## Dúvidas frequentes

**Posso editar um documento já criado?**
Sim. As alterações passam a valer imediatamente após salvar.

**Posso desativar um documento sem excluir?**
Sim. Defina a situação como **Inativo** — ele deixa de aparecer para os fornecedores mas permanece no histórico.

**O que acontece se marcar um documento como obrigatório?**
O fornecedor não consegue concluir o cadastro sem preencher ou anexar esse documento.

**É possível ter documentos diferentes por tipo de fornecedor?**
Sim. Crie linhas de fornecimento específicas e vincule os documentos correspondentes a cada uma delas.

---

## Relação com outros artigos da KB

- **KB90039** — Como configurar documentos de outros módulos (Terceiros, Fabricantes)
- **KB90077** — Como configurar a obrigatoriedade dos módulos exibidos no cadastro
- **KB90036** — Como cadastrar linhas de fornecimento (pré-requisito para vinculação)
- **KB90037** — Como cadastrar ramos de atividade

---

*Fonte: KB90038 — Base de Conhecimento Efcaz (Movidesk)*
