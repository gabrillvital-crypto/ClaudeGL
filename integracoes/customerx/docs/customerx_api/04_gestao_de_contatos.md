# 4. Gestão de Contatos - CustomerX API

O módulo de contatos gerencia os interlocutores, decisores e usuários chave vinculados a cada cliente cadastrado.

---

## 1. Listar Contatos

`GET /contacts`

Retorna contatos cadastrados, permitindo filtros por cliente.

### Parâmetros de Query:
* `page` (integer): Número da página.
* `client_id` (integer): ID do cliente.
* `external_id_client` (string): ID externo do cliente.
* `email` (string): E-mail do contato.

---

## 2. Cadastrar Contato

`POST /contacts`

Cadastra um novo contato associado a um cliente.

### Exemplo de Payload JSON:

```json
{
  "external_id_client": "CLI-10023",
  "name": "Maria Silva",
  "email": "maria.silva@exemplotech.com.br",
  "phone": "11988887777",
  "cellphone": "11977776666",
  "job_title": "Diretora de Operações",
  "type_contact_id": 2,
  "decision_maker": true
}
```

---

## 3. Criar ou Atualizar Contato (Upsert)

`POST /contacts/create_or_update`

Atualiza as informações do contato com base no `email` ou `external_id_contact`, ou cria um novo registro caso não exista.

---

## 4. Tipos de Contato

* `GET /type_contacts`: Lista os tipos de contatos cadastrados na plataforma (ex: Financeiro, Sponsor, Usuário Chave, Técnico).
* `POST /type_contacts`: Cadastra um novo tipo de contato.
