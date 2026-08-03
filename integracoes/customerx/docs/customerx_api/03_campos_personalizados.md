# 3. Campos Personalizados (Custom Attributes) - CustomerX API

Os atributos personalizados permitem enriquecer o perfil do cliente e dos contatos com variáveis específicas do seu modelo de negócio (ex: número de licenças ativas, versão do software, link do dashboard interno).

---

## 1. Consultar Atributos Personalizados do Cliente

`GET /clients/custom_attributes`

Retorna todos os campos e valores personalizados associados a um determinado cliente.

### Parâmetros de Query:
* `client_id` (integer): ID do cliente no CustomerX.
* `external_id_client` (string): ID do cliente no sistema externo.

---

## 2. Cadastrar ou Atualizar Atributo Personalizado de Cliente

`POST /clients/custom_attributes`

Cria ou altera o valor de um campo personalizado existente para o cliente.

### Exemplo de Payload:

```json
{
  "external_id_client": "CLI-10023",
  "custom_attribute_id": 15,
  "value": "Enterprise Tier 1"
}
```

---

## 3. Gerenciamento Global de Campos Personalizados

* `GET /custom_attributes`: Lista todas as definições de campos personalizados criados na conta.
* `POST /custom_attributes`: Cria uma nova estrutura de campo personalizado (definindo nome, tipo de dado como texto, número, data ou seleção).
* `PUT /custom_attributes/:id`: Atualiza a configuração do campo.
* `DELETE /custom_attributes/:id`: Exclui a definição do campo personalizado.
