# O que este CLI consegue fazer no GoHighLevel

Mapa **verificado na conta High Ticket Clube** (`CNK54gfLcK1jQllAu8Xm`) em 21/08/2026.
Cada linha abaixo foi testada de verdade contra a API — não é cópia de documentação.

O CLI fala com **duas APIs diferentes**. Entender a divisão é o ponto principal:

| | API Pública | API Interna |
|---|---|---|
| Host | `services.leadconnectorhq.com` | `backend.leadconnectorhq.com` |
| Autenticação | `GHL_API_KEY` (Private Integration Token) | JWT do Firebase, renovado a partir de `GHL_FIREBASE_REFRESH_TOKEN` |
| Permissões | limitada aos escopos marcados no token | **tudo que o seu usuário enxerga na interface web** |
| Nível | sub-conta | sub-conta **e agência** |
| Como chamar | `ghl api ...` | `ghl --experimental internal ...` |

A API interna é a mesma que o app web do GHL usa. Por isso ela alcança coisas
que a pública recusa — e é também por isso que o token dela é sensível.

---

## Estado atual da ativação

Tudo abaixo já está configurado e testado nesta máquina:

- `GHL_API_KEY` — token de integração privada, válido, com escopo amplo de sub-conta.
- `GHL_LOCATION_ID` — `CNK54gfLcK1jQllAu8Xm` (High Ticket Clube, fuso `America/Sao_Paulo`).
- `GHL_FIREBASE_REFRESH_TOKEN` — troca por JWT com sucesso (usuário `LMKviQZ675zvZr7TAtMf`), renovação automática a cada 50 min.

Tamanho da conta, medido pelo próprio CLI: **6.558 contatos**, **248 workflows**,
**9 pipelines**, **16 calendários**, **105 tags**, **115 campos personalizados**,
**6.496 conversas**, **22 formulários**, **11 contas sociais**, **95 transações**.

---

## Os 11 grupos de comandos prontos

Todos testados e respondendo:

```bash
ghl contacts list --limit 5             # 6.558 contatos
ghl contacts search "joao@"
ghl contacts create --first-name X --email x@y.com --tag lead
ghl contacts add-tag <id> tag1 tag2
ghl opportunities pipelines             # 9 pipelines
ghl opportunities list --pipeline-id <id> --status open
ghl calendars list                      # 16 calendários
ghl calendars slots <id> --start 2026-08-22 --end 2026-08-29
ghl calendars book --calendar-id <id> --contact-id <id> ...
ghl workflows list                      # 248 workflows
ghl workflows enroll --contact-id <id> --workflow-id <id>
ghl conversations list --limit 5
ghl conversations send <conv-id> --type SMS --message "..."
ghl emails list-campaigns               # 7 campanhas
ghl payments transactions               # 95 transações
ghl payments create-invoice --contact-id <id> --amount ... --due-date ...
ghl forms list / forms submissions <id>
ghl social accounts / social create-post
ghl locations get / tags / custom-fields / custom-values
ghl documents list / send / send-template
ghl                                     # REPL interativo com autocomplete
```

`--json` funciona na maioria das leituras e encadeia bem com `jq`.

---

## O que a API pública alcança além dos comandos prontos

Estes endpoints respondem `200` com o token atual, mas **não têm comando dedicado**.
Use `ghl api` para chegar neles. O `{loc}` é substituído pelo location ID automaticamente.

```bash
ghl --json api GET /users/ --query locationId={loc}            # usuários da sub-conta
ghl --json api GET /links/ --query locationId={loc}            # trigger links
ghl --json api GET /surveys/ --query locationId={loc}          # pesquisas
ghl --json api GET /blogs/site/all --query locationId={loc} --query limit=10 --query skip=0
ghl --json api GET /objects/ --query locationId={loc}          # objetos personalizados
ghl --json api GET /products/ --query locationId={loc}         # produtos
ghl --json api GET /voice-ai/agents --query locationId={loc}   # agentes de voz IA
ghl --json api GET /funnels/funnel/list --query locationId={loc}
ghl --json api GET /emails/builder --query locationId={loc}    # templates de e-mail
ghl --json api GET /businesses/ --query locationId={loc}
ghl --json api GET /store/shipping-zone --query altId={loc} --query altType=location
ghl --json api GET /locations/{loc}/templates --query originId={loc}
```

Escrita também funciona pelo mesmo comando:

```bash
ghl api POST /contacts/ --data '{"locationId":"...","email":"a@b.com"}'
ghl api PUT  /contacts/<id> --data @contato.json
ghl api DELETE /contacts/<id>
```

### O que a API pública **recusa**

Testado, retorna `401 "The token is not authorized for this scope"`:

- `/companies/{companyId}` — dados da agência
- `/custom-menus/` — menus personalizados
- `/snapshots/` — snapshots da agência

E, por desenho da plataforma: **workflows são somente-leitura na API pública**.
Você lista e inscreve contatos, mas não cria nem edita.

---

## O que só a API interna libera

É aqui que está a diferença real. Tudo abaixo foi confirmado respondendo `200`
com o token Firebase — e boa parte é inacessível pela API pública.

### Workflows: criar, editar, versionar

O motivo original de existir a camada interna.

```bash
ghl --experimental --json internal GET /workflow/{loc}           # 248 workflows completos, com todos os passos
ghl --experimental --json internal GET /workflow/{loc}/list      # árvore de pastas + workflows
ghl --experimental --json internal GET /workflow/{loc}/<wf-id>   # definição completa de um workflow
```

Escrita (é o que os `builders/` fazem por baixo):

| Ação | Chamada |
|---|---|
| Criar pasta | `POST /workflow/{loc}` com `{"type":"directory","name":"..."}` |
| Criar workflow | `POST /workflow/{loc}` |
| Atualizar passos | `PUT /workflow/{loc}/<wf-id>` |
| Criar gatilho | `POST /workflow/{loc}/trigger` |
| Atualizar gatilho | `PUT /workflow/{loc}/trigger/<trigger-id>` |
| Criar tag na location | `POST /workflow/{loc}/tags/create` |

Tipos de passo suportados pelo builder do CLI: **e-mail, SMS, espera, tag
(adicionar/remover), webhook e passo de IA** (`workflow_builder.py`).

Pelo CLI, sem escrever Python:

```bash
ghl --experimental workflows create-step --type email --name "D1" \
    --subject "Bem-vindo" --body "..." --output-file passo1.json
ghl --experimental workflows create --name "Nurture HTC" --folder "Vendas" --from-json passos.json
ghl --experimental workflows create-n8n --name "Ponte n8n" --webhook-url https://... --tag trigger_tag
```

### Nível agência — a pública não chega aqui

```bash
ghl --experimental --json internal GET /companies/CmWi7ZwgNIb2nFTVXvhS
ghl --experimental --json internal GET "/users/search?companyId=CmWi7ZwgNIb2nFTVXvhS&limit=50"
ghl --experimental --json internal GET "/custom-menus/?locationId={loc}"
```

### Gatilhos (a aba "Triggers" antiga)

Não existe na API pública. Só aqui:

```bash
ghl --experimental --json internal GET "/triggers/?locationId={loc}"
```

### Demais superfícies confirmadas na interna

```bash
ghl --experimental --json internal GET "/funnels/funnel/list?locationId={loc}"
ghl --experimental --json internal GET "/forms/?locationId={loc}"          # definição completa dos campos
ghl --experimental --json internal GET "/surveys/?locationId={loc}"
ghl --experimental --json internal GET "/campaigns/?locationId={loc}"
ghl --experimental --json internal GET "/emails/builder?locationId={loc}&limit=20"
ghl --experimental --json internal GET "/emails/schedule?locationId={loc}&limit=20"
ghl --experimental --json internal GET "/calendars/?locationId={loc}"
ghl --experimental --json internal GET "/products/?locationId={loc}"
ghl --experimental --json internal GET "/opportunities/pipelines?locationId={loc}"
ghl --experimental --json internal GET "/locations/{loc}/customFields"
ghl --experimental --json internal GET "/locations/{loc}/customValues"
ghl --experimental --json internal GET "/locations/{loc}/tags"
ghl --experimental --json internal GET "/objects/?locationId={loc}"
ghl --experimental --json internal GET "/associations/?locationId={loc}&limit=20&skip=0"
ghl --experimental --json internal GET "/proposals/document?locationId={loc}&limit=20"
ghl --experimental --json internal GET "/voice-ai/agents?locationId={loc}"
ghl --experimental --json internal GET "/phone-system/number-pools?locationId={loc}"
ghl --experimental --json internal GET "/store/store-setting?altId={loc}&altType=location"
ghl --experimental --json internal GET "/blogs/site/all?locationId={loc}&limit=20&skip=0"
ghl --experimental --json internal GET "/social-media-posting/{loc}/accounts"
ghl --experimental --json internal GET "/conversations/search?locationId={loc}&limit=20"
ghl --experimental --json internal GET "/links/?locationId={loc}"
```

Endpoints que responderam `422` (existem, só faltam parâmetros obrigatórios):
`/medias/files` (biblioteca de mídia — exige `sortBy`/`sortOrder`) e
`/funnels/page` (exige `offset`).

Não disponível nem pela interna com este token: `/snapshots/` (`401`).

---

## Detalhe técnico que estava travando a API interna

O cliente interno original mandava só `token-id`, `channel` e `source`. Isso
funciona em `/workflow/*`, mas **todo o resto do backend responde
`401 "version header was not found"`** — o que parece falta de permissão e não é.

O cliente agora envia `Version: 2021-07-28` em toda requisição
(`ghl_internal_client.py`). Foi essa única linha que abriu as superfícies de
agência, gatilhos, funis, formulários e o resto da lista acima. Confirmado que
o header não afeta os endpoints de `/workflow`, que continuam idênticos.

---

## Renovação do token Firebase

O refresh token é a sua sessão inteira do GHL. Ele **expira ou é revogado**
quando você troca a senha, sai da conta em todos os dispositivos, ou depois de
um período de inatividade. Quando isso acontecer, o CLI diz:

```
Error: Firebase refresh token is set but token refresh failed.
```

Para pegar um novo: `docs/get-firebase-token.md` (snippet de console do DevTools,
só lê o IndexedDB do próprio navegador, não faz chamada de rede).

Enquanto o token é válido, o CLI troca por um JWT novo sozinho a cada 50 minutos.

---

## Segurança

- `.env` está no `.gitignore` e **nunca** deve ser commitado. Verificado neste repositório.
- O `GHL_FIREBASE_REFRESH_TOKEN` equivale à sua senha do GHL: qualquer um com
  ele age como você, inclusive em nível de agência.
- O `GHL_API_KEY` (`pit-...`) é limitado aos escopos marcados na criação — mais
  seguro. Prefira ele para tudo que a API pública já resolve, e guarde a interna
  para o que só ela alcança.
- Como as credenciais deste repositório já circularam por chat, vale rotacioná-las
  quando a operação terminar: gerar um novo Private Integration Token em
  Settings → Private Integrations e sair da sessão do GHL para invalidar o refresh token.
