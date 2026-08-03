# 1. Introdução e Autenticação - CustomerX API

## Visão Geral
A API REST da CustomerX (ClienteX) possibilita a integração completa entre seus sistemas internos (CRM, ERP, Billing, SaaS) e a plataforma CustomerX. Com ela, é possível automatizar o gerenciamento de clientes, contatos, contratos, tarefas, pesquisas e métricas de Customer Success.

## Ambientes disponíveis

| Ambiente | Base URL | Observações |
| :--- | :--- | :--- |
| **Sandbox (Testes)** | `https://sandbox.api.customerx.com.br/api/v1` | Base de dados reiniciada e limpa no dia 1º de cada mês. |
| **Produção** | `https://api.customerx.com.br/api/v1` | Ambiente oficial para sincronização real de dados. |

---

## Autenticação

Todas as chamadas à API da CustomerX exigem um **Token de API** válido passado via cabeçalho HTTP (**HTTP Bearer Token**) ou parâmetro de query/header específico.

### Cabeçalhos Padrão (Headers)

```http
Authorization: Bearer <SEU_API_TOKEN>
Content-Type: application/json
Accept: application/json
```

*Caso o envio via Bearer Token não funcione no seu cliente HTTP, você também pode utilizar:*
* **Header alternativo:** `token_api: <SEU_API_TOKEN>`
* **Query Parameter:** `?token_api=<SEU_API_TOKEN>`

---

## Padrões de Dados e Formatação

* **Codificação:** UTF-8
* **Formato de Dados:** JSON
* **Formato de Datas:** `DD/MM/AAAA` (Exemplo: `28/07/2026`) ou padrão ISO8601 dependendo do campo especificador.
* **Valores Monetários e Numéricos:** Ponto como separador decimal, sem separadores de milhar (Exemplo: `1250.50`).
* **Formatos de Booleano:** `true` / `false` ou `1` / `0`.

---

## Paginamento e Rate Limit

### Paginamento
* Por padrão, os endpoints de listagem retornam **20 registros por página**.
* Parâmetros de Query para controle:
  * `page`: Número da página (Início em `1`).
  * `per_page`: Quantidade de itens por página (máximo permitido varia por rota).

#### Headers de Resposta de Paginamento:
* `X-Page`: Página atual.
* `X-Per-Page`: Itens por página.
* `X-Pages`: Total de páginas.
* `X-Total`: Total de registros encontrados.

### Rate Limiting (Limite de Requisições)
A API impõe um limite padrão de **60 requisições por minuto** por token de API.
* Headers retornados:
  * `X-RateLimit-Limit`: Limite máximo permitido na janela de tempo.
  * `X-RateLimit-Remaining`: Requisições restantes na janela atual.
  * `X-RateLimit-Reset`: Timestamp UTC de quando o limite será resetado.

---

## Códigos de Resposta HTTP

| Código | Descrição |
| :--- | :--- |
| **200 OK** | Requisição executada com sucesso. |
| **201 Created** | Recurso criado com sucesso. |
| **400 Bad Request** | Dados enviados inválidos ou ausência de campos obrigatórios. |
| **401 Unauthorized** | Token de API ausente, inválido ou expirado. |
| **404 Not Found** | Recurso consultado não foi encontrado. |
| **422 Unprocessable Entity** | Erro de validação de negócio nos dados enviados. |
| **429 Too Many Requests** | Limite de requisições excedido (Rate limit). |
| **500 Internal Server Error** | Erro interno nos servidores da CustomerX. |
