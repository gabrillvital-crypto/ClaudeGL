# Reunião — Call de Usabilidade
**Data:** 02/06/2026
**Tipo:** Call operacional com Unidade Cadastradora
**Contato:** Júlia Leite Quaresma Pimentel (julia.quaresma@dof.com)

---

## Participantes

| Empresa | Participante |
|---|---|
| DOF / Norskan | Júlia Leite Quaresma Pimentel (Unidade Cadastradora) |
| Efcaz | Gabriel |

---

## Dados da conta (pré-call)

| Indicador | Contratado | Atual | Status |
|---|---|---|---|
| Fornecedores | 1.300 | 1.003 ativos | 🟡 77% |
| Usuários | 8 (6 admin + 2 aux) | 10-11 perfis | ⚠️ Acima do contrato |
| Terceiros | Módulo bonificado 6 meses | 2 cadastrados | 🔴 Bônus vence jun/2026 |
| Integrações ativas | 63 configuradas | 2 ativas (Receita Fed + FGTS) | 🔴 61 inativas |
| Solicitações abertas | — | 16.420 | ℹ️ Volume alto |
| Tempo médio homologação | — | 45 dias | 12 sem indeferimento / 56 com |

---

## Objetivo da call

1. Comunicar solução de contorno para troca de e-mail de fornecedores (fechar Tarefa #33)
2. Entender o dia a dia operacional e o que gera mais atrito
3. Resolver a questão do módulo Terceiros antes do fim do bônus
4. Explorar integrações subutilizadas (61 de 63 inativas)

---

## Pontos de atenção

**1. Módulo de Terceiros — bônus vencendo**
Bonificado por 6 meses desde dez/2025 = vence jun/2026. Apenas 2 terceiros cadastrados. Decidir: cliente usa ou quer manter o módulo?

**2. Indeferimento inflando o tempo de homologação 4×**
12 dias sem indeferimento vs. 56 dias com. Investigar causa — oportunidade de configurar alertas preventivos para reduzir retrabalho.

**3. Usuários acima do contrato**
Contrato: 6 admin + 2 aux = 8. Ativos: 10-11 perfis. Ricardo Silva tem e-mail @azi.com.br (usuário de setup/integração). Matheus tem perfil duplo. Verificar ajuste ou oportunidade de expansão.

---

## Comprimento pendente a resolver

**Tarefa #33:** Comunicar solução de contorno para troca de e-mail de fornecedores.
A customização completa exigiria desenvolvimento pesado. O time técnico encontrou alternativa dentro da plataforma atual — apresentar para Júlia.

---

## Perguntas planejadas para a call

- *"Das 16 mil solicitações abertas, qual é a maior dor hoje — é fornecedor que não atualiza, documento que volta por indeferimento, ou outra coisa?"*
- *"Os casos que voltam por indeferimento — o motivo mais comum é documento errado ou faltando?"*
- *"Vocês usam o módulo de Terceiros? Vi que tem 2 cadastrados — como é esse processo para vocês hoje?"*
- *"Tem alguma funcionalidade que vocês queriam usar e ainda não conseguiram configurar?"*

---

## Plano de Ação (pós-call)

| # | Ação | Responsável | Status |
|---|---|---|---|
| 1 | Registrar resumo no CustomerX | Gabriel | ⏳ Pendente |
| 2 | Enviar e-mail de follow-up com próximos passos datados | Gabriel | ⏳ Pendente |
| 3 | Definir situação do módulo Terceiros (renovar ou encerrar bônus) | Gabriel + Júlia | ⏳ Pendente |
| 4 | Atualizar este arquivo com resultado da call | Gabriel | ⏳ Pendente |

---

---

## Resumo Pós-Call

**Sentimento:** 🟢 Positivo | **Duração real:** 47min

**Participantes confirmados na call**

| Nome | Empresa | Papel |
|---|---|---|
| Gabriel Vital | Efcaz | CS Specialist |
| Ricardo Pedroso | Efcaz | Suporte / Produto |
| André Macedo | Grupo DOF | Gestor / Decisor |
| Júlia Quaresma | Grupo DOF | Analista (operacional) |
| Rosilene Rangel | Grupo DOF | Analista (operacional) |

---

### Pontos discutidos

1. **Status geral — 🟢**
Plataforma estável. Lentidões de sexta resolvidas. Sentiment positivo de uso geral.

2. **Bug: botão "Reprovar" não inicia análise automaticamente**
Resolvido parcialmente — agora avisa que é necessário iniciar antes. Não é mais crítico para a operação.

3. **Filtro por analista na aba de solicitações**
Júlia pediu filtro por analista responsável (Júlia ou Rosilene) na fila de análise. Não existe hoje — filtro atual é por setor, que a DOF não utiliza. Ricardo: não é customização, é evolução de produto. Não urgente para a DOF, mas seria útil.

4. **Cadastro de novos CNPJs por fornecedores (recorrência)**
DOF tem processo interno de aprovação — fornecedor não deve se cadastrar diretamente. Suporte da Efcaz estava orientando fornecedores a criar novos CNPJs, contrariando o procedimento. André reforçou que isso já tinha sido alinhado com Ana Paula e voltou a acontecer. Tela de login da DOF já não tem a opção habilitada, mas o problema ocorre também dentro do portal do fornecedor logado (opção "nova empresa").

5. **Duplicidade de item no cadastro do fornecedor**
Rosilene compartilhou a tela ao vivo: JMT Transporte com "Cartão do CNPJ" aparecendo duas vezes. Pontual e intermitente — não recorrente em todos os cadastros. Ricardo registrou para investigar.

6. **Gargalo em indeferimentos**
Morosidade é do fornecedor, não da plataforma. DOF tem política de priorizar fornecedores ativos. Alguns cadastros aguardam por meses porque o fornecedor não retorna — é um comportamento esperado da operação deles.

7. **Material de educação para fornecedores**
Júlia sugeriu melhorar o guia do portal: passo a passo de como alterar dados e enviar para aprovação ainda gera confusão (fornecedor anexa documento mas não clica em "enviar para análise"). Gabriel mostrou novo material com vídeo recém publicado — Júlia não conhecia. Júlia vai enviar o PDF que usa hoje para avaliação e possível atualização.

8. **Módulo de Terceiros**
Os dois cadastros identificados foram feitos pela Ana Paula (Efcaz) como demonstração de venda, não pela DOF. Módulo bonificado no 1º semestre — DOF não utiliza ativamente.

9. **Módulo de Avaliações + Ocorrências — Oportunidade de expansão**
André trouxe dois casos de uso hoje feitos manualmente em outro sistema:
- **Ocorrências / Não conformidades:** 1 pessoa centraliza o processo de registrar não conformidades e direcionar plano de ação ao fornecedor. Ricardo apresentou o módulo — André: *"atende perfeitamente."* 1 licença suficiente.
- **Auditoria em campo:** DOF envia equipe para auditoria presencial com checklist. Ricardo mapeou que o módulo de Avaliações cobre esse fluxo. Limitação levantada: DOF tem 2.000+ funcionários como avaliadores potenciais — mas para o caso de auditoria (1 auditor), totalmente viável.
- Ambos os módulos são adicionais. André pediu período de teste e agendou reunião de demo.

---

### Registro CustomerX

> Reunião de alinhamento 02/06 com André, Júlia e Rosilene. Plataforma estável — cliente satisfeito com funcionamento geral. Três pontos operacionais levantados: filtro por analista (roadmap), recorrência de fornecedores criando CNPJs sem aprovação interna (alinhar com suporte), bug de duplicidade de item (investigação em andamento). Oportunidade clara de expansão: módulos de Ocorrências e Avaliações — André validou o fit do módulo de Ocorrências como "atende perfeitamente". Próxima reunião agendada para 08/06 às 14h para demo direcionada com o formulário real da DOF.
> **Sentimento: 🟢 Positivo**

---

### Nota estratégica (uso interno)

O módulo de Ocorrências é o de menor atrito para fechar — André já validou o fit. Para a demo de 08/06, separar claramente os dois casos de uso:
1. **Ocorrências** → 1 licença, 1 pessoa, implementação simples → foco em fechar
2. **Avaliações para auditoria em campo** → 1 auditor interno → viável, não precisa das 2.000 licenças que André imaginou

Não misturar os dois na apresentação — o medo das licenças pode contaminar a percepção do módulo de Ocorrências.

---

### Plano de Ação Atualizado

| # | Ação | Responsável | Prazo | Status |
|---|---|---|---|---|
| 1 | Enviar formulário de auditoria + estrutura de não conformidades por e-mail | André Macedo | Antes de 08/06 | ⏳ Pendente |
| 2 | Alinhar com time de suporte para não orientar fornecedores DOF a criar novos CNPJs | Ricardo | Imediato | ⏳ Pendente |
| 3 | Investigar duplicidade de item no JMT Transporte (Cartão do CNPJ) | Ricardo | Até 08/06 | ⏳ Pendente |
| 4 | Tratar internamente bloqueio da opção "nova empresa" para fornecedores logados | Gabriel | Até 08/06 | ⏳ Pendente |
| 5 | Enviar convite para reunião de demo — segunda 08/06 às 14h | Gabriel | 02/06 | ✅ Feito |
| 6 | Verificar viabilidade de período de teste + preparar proposta de investimento | Gabriel | Até 08/06 | ⏳ Pendente |
| 7 | Enviar PDF do guia atual de fornecedores via WhatsApp | Júlia | Sem prazo | ⏳ Pendente |
| 8 | Retorno a Rosilene sobre bug de duplicidade | Gabriel | Até 08/06 | ⏳ Pendente |

---

### E-mail de Follow-up Enviado

**Para:** André Macedo, Júlia Quaresma, Rosilene Rangel | **Data:** 02/06/2026

> André, Júlia, Rosilene — bom dia!
>
> Foi muito bom falar com vocês hoje. Segue o resumo do que a gente cobriu e o que ficou combinado para não perder nada no caminho.
>
> **O que passamos:**
> - Plataforma estável — lentidões de sexta resolvidas, funcionamento geral ok
> - Filtro por analista na fila de análise — ainda não existe, mas Ricardo já mapeou como evolução de produto
> - Novo CNPJ por fornecedores — vamos reforçar internamente para não ocorrer mais. A tela de login já não permite, mas vamos tratar a opção dentro do portal também
> - Duplicidade de item no JMT Transporte (Cartão do CNPJ) — Ricardo já está verificando
> - Guia do portal — vamos avaliar o PDF que a Júlia usa com os fornecedores e verificar o que dá para atualizar
> - Módulos de Ocorrências e Avaliações — demonstração feita, André gostou do fit. Seguimos na próxima semana
>
> **Próximos passos:**
>
> | O quê | Quem | Quando |
> |---|---|---|
> | Enviar formulário de auditoria + estrutura de não conformidades | André | Antes de 08/06 |
> | Enviar PDF do guia atual de fornecedores | Júlia | Quando puder |
> | Convite da reunião de segunda | Gabriel | Hoje |
> | Retorno sobre duplicidade (Rosilene) | Gabriel | Até 08/06 |
>
> **Próxima reunião: segunda-feira, 08/06 às 14h**
> Vamos fazer a demonstração dos módulos com o formulário real de vocês — já fica mais concreto.
>
> Qualquer dúvida nesse meio tempo, é só me chamar.
>
> Um abraço,
> Gabriel Vital — Customer Success Efcaz
