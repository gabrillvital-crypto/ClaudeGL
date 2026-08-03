# 6. Tarefas, Jornadas e Pesquisas - CustomerX API

Módulo focado no acompanhamento de tarefas operacionais de CS, etapas de onboarding/jornadas e feedbacks de pesquisas.

---

## 1. Tarefas do Cliente

`GET /clients/tasks_clients/:id`

Lista todas as tarefas vinculadas a um cliente específico (incluindo tarefas manuais de CSM e tarefas automáticas geradas por Playbooks/Jornadas).

### Retorno inclui:
* Título e descrição da tarefa.
* Data de vencimento e data de conclusão.
* Status (`pending`, `completed`, `canceled`).
* Responsável (CSM).

---

## 2. Respostas de Pesquisas (NPS e CSAT)

`GET /surveys/answers`

Obtém os resultados e pontuações das pesquisas enviadas aos clientes.

### Parâmetros de Query:
* `client_id` (integer): Filtrar por cliente.
* `type` (string): Tipo de pesquisa (`nps`, `csat`).
* `start_date` / `end_date`: Período das respostas.

### Estrutura de Retorno:
* Pontuação (Score de 0 a 10 no NPS / 1 a 5 no CSAT).
* Classificação (Promotor, Neutro, Detrator).
* Comentários/Feedback textual do cliente.
* Data e hora do preenchimento.
