# Integração CustomerX — Progresso

**Data:** 28/07/2026  
**Status:** Em construção — aguardando token de API e external_id de cliente para teste

---

## Objetivo

Automatizar registros no CustomerX a partir do agente Claude, sem precisar entrar na plataforma manualmente.

---

## Endpoints confirmados

| Ação | Endpoint | Observação |
|---|---|---|
| Criar tarefa na jornada | `POST /tasks_follow_ups` | Confirmado pelo suporte CustomerX |
| Criar tarefa no board do CSM | `POST /tasks` | Requer `dashboard_activities_step_id` + `title` |
| Adicionar comentário em tarefa | `POST` (link suporte) | Endpoint não estava no split da doc |
| Listar tarefas do cliente | `GET /clients/tasks_clients/:id` | Funciona por `external_id_client` |
| Listar board steps | `GET /board_csm_steps` | Retorna os IDs das colunas do kanban |
| Mover stage (coluna do board) | `PUT /tasks/:id` | Muda `dashboard_activities_step_id` |
| Health Score | `GET /indicators/health_score` | Só leitura — sem endpoint de escrita |
| NPS | `POST /net_promoter_scores` | Cadastro e atualização disponíveis |

## Endpoints NÃO disponíveis

- **Registrar reunião como entidade própria** — não existe na API. Alternativa: criar comentário em tarefa do board.
- **Atualizar Health Score via API** — indicador calculado pela plataforma, sem escrita direta.

---

## Links da documentação (suporte CustomerX - Paulo)

- Tarefa na jornada: https://doc.api.customerx.com.br/#bad315a7-dce8-45be-bc1d-9edb78fa8d65
- Comentário em tarefa: https://doc.api.customerx.com.br/#ae209b94-a604-4279-b980-ec80a74538c0
- Tarefa no board CSM: https://doc.api.customerx.com.br/#778e2927-b80f-4cf7-960e-0bf7abe4557d

---

## Pendências para retomar

1. **Token de API do CustomerX** — Gabriel precisa pegar em Configurações → API
2. **external_id_client** de um cliente para teste no sandbox
3. **IDs dos board_csm_steps** — nomes/colunas do kanban do Gabriel
4. Ler os 3 endpoints confirmados pelo suporte para montar o payload correto
5. Construir módulo Python `customerx_client.py` com as funções prontas

---

## Estrutura planejada do módulo

```
integracoes/customerx/
  customerx_client.py     ← módulo principal com funções da API
  config.py               ← token e base URL (não commitar)
  exemplos/               ← exemplos de uso por ação
  docs/                   ← documentação da API
```
