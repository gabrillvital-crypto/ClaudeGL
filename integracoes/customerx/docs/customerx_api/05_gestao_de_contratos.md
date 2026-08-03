# 5. Gestão de Contratos - CustomerX API

O módulo de contratos permite gerenciar termos contratuais, valores, recorrências, produtos vinculados e vigências dos clientes.

---

## 1. Buscar Contratos

`GET /contracts`

Lista os contratos vigentes e históricos.

### Parâmetros de Query:
* `page` (integer): Página solicitada.
* `client_id` (integer): ID do cliente.
* `external_id_client` (string): ID externo do cliente.
* `status` (string): Status do contrato (`active`, `canceled`, `renewed`, `finished`).

---

## 2. Cadastrar Contrato

`POST /contracts`

Registra um novo contrato financeiro/operacional para o cliente.

### Exemplo de Payload JSON:

```json
{
  "external_id_client": "CLI-10023",
  "external_id_contract": "CONT-2026-01",
  "value": 2500.00,
  "start_date": "01/08/2026",
  "end_date": "01/08/2027",
  "billing_cycle": "monthly",
  "product_id": 5,
  "journey_id": 2
}
```

---

## 3. Reativar Contrato Cancelado

`PUT /contracts/reactivate_contract`

Reativa um contrato previamente cancelado no sistema.

### Exemplo de Payload:
```json
{
  "external_id_contract": "CONT-2026-01",
  "reactivation_date": "28/07/2026"
}
```
