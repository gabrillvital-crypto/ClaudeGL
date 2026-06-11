# Dashboard de Gestão de Terceiros — Visão de Produto
**Origem:** Prova de conceito desenvolvida para Zurich Airport | Mai/2026
**Status:** Validado por Ricardo e João em 26/05/2026 — automação N8N mapeada — apresentação Débora em 29/05/2026

---

## O que é

Dashboard interativo de conformidade documental de terceiros, gerado a partir dos 4 relatórios exportados da plataforma Efcaz. HTML standalone — sem servidor, sem login, abre direto no navegador.

Resolve um conjunto de dores que nenhuma tela da plataforma atual resolve hoje:
- Visão gerencial em um só lugar (% conformidade, pendências, terceiros ativos)
- Drill-down de 3 níveis: Fornecedor → Terceiro → Documento
- Status em 3 camadas: Conforme / Vencido / Pendente
- Exportação on-demand (Excel, PDF, CSV) sem depender da equipe Efcaz
- Alertas visuais de auditoria (fornecedor reprovado em destaque)
- Situação documental da empresa separada da situação dos terceiros

---

## Dores que resolve

Mapeadas diretamente da fala da cliente Débora (Zurich Airport):

| Dor | Como o dashboard resolve |
|---|---|
| Não sabe o % de não conformidade por fornecedor | KPI card + gráfico por fornecedor com cor (verde/amarelo/vermelho) |
| Não consegue drill-down — só vê totais | 3 níveis: fornecedor → terceiro → documento |
| Relatório não tem data (sem valor jurídico) | Data e hora de geração no header |
| Precisa de relatório on-demand, não depender da Thaís | Botão exportar Excel/PDF/CSV direto no dashboard |
| Não distingue "vencido" de "não enviado" | Status separado em 3 camadas |
| Relatório não é visual — "monte de letrinhas" | 8 gráficos interativos + tabelas com filtros |
| Não vê docs da empresa separados dos docs dos terceiros | Seção própria para R4 — docs corporativos por fornecedor |

---

## Estrutura técnica atual

```
4 relatórios Metabase (R1 CSV + R2 CSV + R3 CSV + R4 XLSX)
        ↓
Python (pandas + plotly) — dashboard_zurich.py
        ↓
HTML standalone — dashboard_zurich_airport.html
        ↓
Cliente acessa no navegador
```

**Fontes de dados:**
- R1: Pendências por solicitação (TERCEIROS / DOCUMENTOS, EM_ELABORACAO / APROVADO)
- R2: Terceiros cadastrados (Ativo / Inativo por fornecedor)
- R3: Situação documental por terceiro — última solicitação (A vencer / Vencido / Não anexado)
- R4: Situação documental por empresa/fornecedor — última solicitação (mesma regra do R3)

---

## Camadas de evolução

### Camada 1 — Hoje (prova de conceito manual)
Script + HTML gerado manualmente. Cliente exporta os relatórios, roda o script, abre o HTML.
**Status:** funcional, apresentando para Débora em 29/05/2026.

### Camada 1.5 — Automação N8N (próximo passo imediato)
N8N chama API do Metabase (controlado pela Efcaz), baixa os 4 relatórios com nomes fixos, roda o script Python e serve o HTML em um endpoint estático no servidor da Efcaz.

```
N8N agenda → API Metabase → arquivos fixos → python script → HTML → servidor estático
Débora acessa: http://servidor-efcaz/zurich/dashboard.html (sempre atualizado)
```

**Frequência:** 2x por semana (prevista) → diária em junho se validado.
**Custo:** zero. **Responsável N8N:** Ricardo/João. **Responsável script:** Gabriel.
**Pré-requisito:** Ricardo configurar API token Metabase + endpoint estático no servidor.

### Camada 2 — Médio prazo (tempo real via Looker Studio)
Conectar Looker Studio ao BD via token API do Metabase.
Cliente acessa com conta Google — dados sempre em tempo real.
Custo: zero (Google Workspace já contratado pela Efcaz).
Depende de: credencial de leitura ao BD por cliente (Ricardo).

### Camada 3 — Longo prazo (produto nativo)
Dashboard dentro da plataforma Efcaz, acessado pelo login já existente do cliente.
Opção técnica: Power BI Embedded via API — white-label, sem licença adicional para o cliente.
Custo: baseado em capacidade de uso, não por usuário — escalável para toda a carteira.

---

## Alerta de Auditoria — evolução planejada

**Situação atual:** card NEPOS SISTEMAS hardcoded no script — dados transcritos manualmente do PDF de auditoria do BPO (Thaís).

**Insight confirmado:** todos os dados do card de auditoria já estão nos relatórios que usamos:
- Documentação da Empresa → R4 (já incorporado)
- Prontuários de Trabalhadores → R3 (já no drill-down)

**A Thaís lê esses dados e escreve o relatório narrativo** — mas a matéria-prima já está nos CSVs.

**Plano pós-validação:**
1. Gerar card de auditoria automaticamente por fornecedor (R4 + R3, filtrando Vencido/Pendente)
2. Criar `auditoria_zurich.csv` mínimo que o BPO preenche: Fornecedor, Veredicto (REPROVADO/APROVADO/ATENÇÃO), Observação geral
3. Script lê o CSV → monta o card com header (veredicto) + conclusão (observação da Thaís) + tabela de docs + tabela de trabalhadores críticos
4. Eliminar hardcode do NEPOS completamente — escalável para qualquer fornecedor auditado

---

## Perfil de cliente ideal

Clientes com módulo **Gestão de Terceiros** ativo que:
- Têm volume relevante de terceiros (>100 pessoas)
- Têm múltiplos fornecedores prestadores de serviço
- Precisam reportar conformidade para diretoria ou auditorias externas
- Têm gestão ativa de documentos (SST, trabalhistas, fiscais)

Exemplos na carteira atual: Zurich Airport, clientes do setor de infraestrutura, saúde, logística.

---

## Diferenciais competitivos

- **Drill-down 3 níveis** — nenhum concorrente SRM entrega isso nativamente sem BI dedicado
- **Valor jurídico** — relatório com data e hora, exportável em PDF, serve como evidência
- **Custo zero de adoção** — não exige nova ferramenta, novo login ou nova licença para o cliente
- **Gerado pelos próprios dados da plataforma** — extensão do que já existe, não ferramenta paralela
- **Automação via N8N** — atualização automática sem intervenção manual, acesso por URL fixa

---

## Próximos passos

| # | Ação | Responsável | Prazo |
|---|---|---|---|
| 1 | Validar com Débora se o dashboard resolve as dores mapeadas | Gabriel | Reunião 29/05/2026 |
| 2 | Ricardo configurar API token Metabase + endpoint estático no servidor | Ricardo | Após 29/05 |
| 3 | Atualizar BASE_DIR no script para caminho do servidor | Gabriel | Após Ricardo confirmar caminho |
| 4 | Ricardo/João configurar fluxo N8N completo | Ricardo/João | A definir |
| 5 | Testar ciclo completo N8N → HTML → URL | Gabriel + Ricardo | A definir |
| 6 | Parametrizar seção de auditoria (auditoria_zurich.csv) | Gabriel | Pós-validação |
| 7 | Mapear outros clientes da carteira com perfil ideal | Gabriel | A definir |
| 8 | Apresentar visão de produto para Renato como roadmap | Gabriel | A definir |

---

*Documento criado em 26/05/2026 | Atualizado 26/05/2026 | Efcaz CS — Gabriel Vital*
