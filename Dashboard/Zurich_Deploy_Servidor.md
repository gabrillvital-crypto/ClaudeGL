# Deploy do Dashboard Zurich — Servidor Cloud Efcaz
**Guia de configuração para o Ricardo**
Elaborado por: Gabriel Vital | Efcaz CS | 28/05/2026

---

## Cenário

O servidor cloud da Efcaz já roda o N8N. O objetivo é fazer o N8N, depois de gerar o HTML do dashboard, salvar o arquivo em um caminho que o servidor já sirva via HTTP.

**Usuárias:** apenas Débora e Claudinha (duas gestoras da Zurich Airport).
**Acesso:** URL protegida por usuário e senha — cada uma tem credencial própria.
**Atualização:** automática, pelo menos 1x por dia (sugestão: todo dia às 07h, antes do início do expediente delas).

```
N8N agendado — todo dia às 07h
    ↓
Baixa os 4 CSVs do Metabase
    ↓
Roda o script Python → gera o HTML atualizado
    ↓
Salva em /srv/static/zurich/relatorio_fornecedores_zurich.html
    ↓
Débora e Claudinha abrem a URL no Chrome — dashboard do dia
```

---

## Passo 1 — Criar a pasta de arquivos estáticos

No servidor, criar o diretório onde o HTML será salvo:

```bash
mkdir -p /srv/static/zurich
```

Garantir que o usuário que roda o N8N tem permissão de escrita nessa pasta:

```bash
chown -R usuario-n8n:usuario-n8n /srv/static/zurich
```

---

## Passo 2 — Configurar o servidor web para servir a pasta

### Se o servidor usa nginx (mais comum)

Adicionar um bloco `location` no arquivo de configuração do nginx (normalmente em `/etc/nginx/sites-available/efcaz` ou `/etc/nginx/nginx.conf`):

```nginx
location /zurich/ {
    alias /srv/static/zurich/;
    autoindex off;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

Recarregar o nginx:

```bash
nginx -t && systemctl reload nginx
```

### Se o servidor usa Apache

Adicionar no VirtualHost ativo:

```apache
Alias /zurich /srv/static/zurich
<Directory /srv/static/zurich>
    Options -Indexes
    AllowOverride None
    Require all granted
</Directory>
```

Recarregar o Apache:

```bash
apachectl configtest && systemctl reload apache2
```

> Se o servidor usar outra stack (Node, Caddy, etc.), me avisa que adapto.

---

## Passo 3 — Ajustar o script Python para o caminho do servidor

No topo do arquivo `relatorio_fornecedores_zurich.py`, alterar a variável `OUTPUT_HTML`:

```python
# Linha atual (máquina local Gabriel):
OUTPUT_HTML = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\relatorio_fornecedores_zurich.html"

# Alterar para (servidor):
OUTPUT_HTML = "/srv/static/zurich/relatorio_fornecedores_zurich.html"
```

E também atualizar `BASE_DIR` para apontar para onde os CSVs ficam no servidor:

```python
# Linha atual:
BASE_DIR = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Dashboard\data"

# Alterar para (servidor):
BASE_DIR = "/srv/zurich/data"
```

---

## Passo 4 — Ajustar o fluxo N8N

### Agendamento

Configurar o nó Trigger do N8N para rodar **todo dia às 07h** (antes do início do expediente das gestoras):

```
Cron expression: 0 7 * * *
```

Se quiser garantia maior de dados frescos, pode rodar 2x por dia — 07h e 13h:

```
Cron expression: 0 7,13 * * *
```

### Nós do fluxo

1. **Baixar os 4 CSVs do Metabase** via HTTP Request (já configurado)
2. **Salvar os CSVs** em `/srv/zurich/data/` com os nomes fixos:
   - `pendencias_zurich.csv`
   - `terceiros_zurich.csv`
   - `situacao_terceiro_zurich.csv`
   - `situacao_fornecedor_zurich.csv`
3. **Executar o script Python**:

```bash
python3 /srv/zurich/relatorio_fornecedores_zurich.py
```

4. O script já salva o HTML direto em `/srv/static/zurich/` — nenhum nó adicional necessário.

---

## Passo 5 — Testar

Após configurar, verificar:

```bash
# O HTML foi gerado no lugar certo?
ls -lh /srv/static/zurich/

# O nginx/Apache serve corretamente?
curl -I http://localhost/zurich/relatorio_fornecedores_zurich.html
```

Abrir no navegador:

```
http://[domínio-efcaz]/zurich/relatorio_fornecedores_zurich.html
```

---

## Passo 6 — Compartilhar com a Débora

Enviar a URL final para a Débora e Claudinha. Elas salvam como favorito no Chrome. A partir desse momento, toda atualização do N8N aparece automaticamente na próxima vez que abrirem ou derem F5.

Sugestão de mensagem:

> "Débora, segue o link do dashboard de conformidade de fornecedores. Ele é atualizado automaticamente duas vezes por semana (segunda e quinta). Basta abrir o link ou dar F5 para ver os dados mais recentes: [URL]"

---

## Segurança — acesso por perfil

| Quem | Como acessa | Precisa de senha? |
|---|---|---|
| Time Efcaz (rede interna) | Pelo domínio/rede da Efcaz | Não — acesso direto |
| Débora (Zurich) | URL externa | Sim — usuário e senha próprios |
| Claudinha (Zurich) | URL externa | Sim — usuário e senha próprios |
| Qualquer outro | URL externa | Bloqueado |

### Configuração nginx com `satisfy any`

O `satisfy any` libera o acesso se o usuário atender **qualquer uma** das condições: vem da rede interna **ou** apresenta credencial válida.

```bash
# Instalar utilitário de senha
apt install apache2-utils

# Criar credencial da Débora
htpasswd -c /etc/nginx/.htpasswd debora

# Adicionar credencial da Claudinha (sem -c para não sobrescrever)
htpasswd /etc/nginx/.htpasswd claudinha
```

```nginx
location /zurich/ {
    alias /srv/static/zurich/;

    satisfy any;

    # Rede interna Efcaz — acesso direto sem senha
    allow 10.0.0.0/8;      # ajustar para o range real da rede Efcaz
    allow 192.168.0.0/16;  # incluir se usar esse range também
    deny all;

    # Externo — exige usuário e senha
    auth_basic "Dashboard Zurich Airport";
    auth_basic_user_file /etc/nginx/.htpasswd;

    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

> **Ricardo:** substituir os ranges `10.0.0.0/8` e `192.168.0.0/16` pelos IPs reais da rede interna da Efcaz. Se o time acessa via VPN, incluir o range da VPN também.

### Como funciona na prática

- **Time Efcaz abre a URL** → nginx identifica IP interno → acesso liberado automaticamente
- **Débora abre a URL** → nginx pede usuário e senha → ela entra com as credenciais dela
- **Qualquer outra pessoa** sem IP interno e sem credencial → bloqueado com 401

---

## Resumo para o Ricardo

| O que fazer | Quem | Estimativa |
|---|---|---|
| Criar pasta `/srv/static/zurich/` | Ricardo | 2 min |
| Configurar bloco nginx/Apache com auth_basic | Ricardo | 10 min |
| Criar credenciais Débora e Claudinha (htpasswd) | Ricardo | 3 min |
| Ajustar caminhos no script Python (`OUTPUT_HTML` e `BASE_DIR`) | Gabriel | 2 min |
| Ajustar agendamento N8N para diário às 07h | Ricardo | 2 min |
| Ajustar nó Execute Command no N8N | Ricardo | 2 min |
| Teste e validação | Ricardo + Gabriel | 5 min |

**Total estimado: menos de 30 minutos.**

---

## O que Gabriel entrega para Ricardo antes da configuração

- Arquivo `relatorio_fornecedores_zurich.py` com os caminhos já ajustados para o servidor
- Nomes fixos dos 4 CSVs (seção 4 deste documento)
- Credenciais sugeridas para Débora e Claudinha (combinadas internamente)

---

*Dashboard: `relatorio_fornecedores_zurich.py` | Documentação operacional: `Dashboard_Zurich_Documentacao.md`*
