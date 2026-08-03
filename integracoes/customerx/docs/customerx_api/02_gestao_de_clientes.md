# 2. Gestão de Clientes - CustomerX API

O módulo de clientes permite criar, consultar, atualizar e reativar empresas/clientes dentro da plataforma CustomerX.

---

## 1. Listar / Buscar Clientes

`GET /clients`

Retorna uma lista paginada com os clientes cadastrados.

### Parâmetros de Busca (Query String):
* `page` (integer): Número da página.
* `id` (integer): ID interno do cliente no CustomerX.
* `external_id_client` (string): ID externo do cliente no seu sistema de origem.
* `company_name` (string): Razão Social do cliente.
* `trading_name` (string): Nome Fantasia.
* `cnpj_cpf` (string): CNPJ ou CPF (apenas números ou formatado).
* `contract_status` (string): Status do contrato (`without_contract`, `active_contract`, `contract_canceled`, `contract_finalized`).

---

## 2. Cadastrar Cliente

`POST /clients`

Cadastra um novo cliente na base.

### Exemplo de Payload JSON:

```json
{
  "external_id_client": "CLI-10023",
  "company_name": "Empresa Exemplo Tecnologia LTDA",
  "trading_name": "Exemplo Tech",
  "cnpj_cpf": "12.345.678/0001-90",
  "date_register": "28/07/2026",
  "email": "contato@exemplotech.com.br",
  "phone": "11999998888",
  "segment_id": 4,
  "user_id": 12,
  "status": true
}
```

---

## 3. Criar ou Atualizar Cliente (Upsert)

`POST /clients/create_or_update`

Se o cliente já existir (com base no `id` ou `external_id_client`), seus dados serão atualizados; caso contrário, um novo registro será criado.

---

## 4. Reativar Cliente Cancelado

`PUT /clients/reactivate`

Altera o status de um cliente previamente cancelado para ativo.

### Exemplo de Payload:
```json
{
  "external_id_client": "CLI-10023"
}
```

---

## 5. Tags de Clientes

* `POST /clients/client_tags`: Associa uma tag ao cliente (`client_id` ou `external_id_client` + `tag_id` ou `description`).
* `DELETE /clients/client_tags`: Remove a associação de uma tag do cliente.
