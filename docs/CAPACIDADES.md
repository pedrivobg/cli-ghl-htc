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

## Halo no Instagram e suporte de afiliado (set/2026)

### Por que a Halo não respondia no Instagram
O workflow `HTC | Atendimento IA Halo` (`0076f038-…`) começa com um
`find_opportunity` no pipeline Afiliado e só liga o bot se a oportunidade
estiver em `Opt In Leads` ou `Afiliado Lead(1st step)`. As DMs do Instagram
caem em **`Instagram Leads`** (`422a0d12-…`), criado pelo workflow
`IG DM -> Add Pipeline` — estágio que não estava na lista. Resultado: o ramo
"Opportunity Not Found"/"NÃO" é um beco sem saída e o bot nunca era ligado.
O gatilho e os canais do agente (`channels` inclui `IG`) sempre estiveram
certos; o problema era só a condição de estágio.

Correções aplicadas (`tools/fix_instagram_halo.py`):
1. `Instagram Leads` entrou na lista de estágios aceitos;
2. `IG DM -> Add Pipeline` passou a inscrever o contato no atendimento da Halo
   logo depois de criar a oportunidade — os dois workflows disparavam no mesmo
   `customer_reply`, então o `find_opportunity` podia rodar antes de a
   oportunidade existir.

### Ações do agente têm gatilho próprio
O texto do prompt **não** aciona uma ação. Quem decide é o `triggerCondition`
da própria ação. Nos `humanHandOver` esse texto é gerado pelo `handoverType`
(`contactRequest`, `lackOfInformation`, `failedToResolveIssue`) e qualquer
edição manual volta ao padrão. Para uma condição própria, use `triggerWorkflow`:

    POST /conversation-ai/agents/{bot}/actions?locationId={loc}
    {"name": "...", "type": "triggerWorkflow",
     "details": {"triggerCondition": "...", "workflowIds": ["<wf>"]}}

`details` de `triggerWorkflow` aceita só `triggerCondition` e `workflowIds`
(array); `enabled`, `examples` e `workflowId` são rejeitados com 422.

### PUT do agente
`PUT /conversation-ai/agents/{bot}?locationId={loc}` recusa `locationId` no
corpo (422). E quando `fullPrompt` vai junto dos três campos, o servidor grava
só o `fullPrompt`: mande `personality`/`goal`/`instructions` em um PUT e o
`fullPrompt` remontado em outro.

### Corrida entre gravar campo e notificar
A Halo grava os campos e dispara o workflow de transferência quase ao mesmo
tempo, e a notificação renderizava `{{contact.status_do_ticket}}` vazio. Mesma
corrida do bug de comissão. Resolvido com 2 minutos de espera antes de avisar o
time (`tools/fix_transferencia_corrida.py`).

### Caso de afiliação não atribuída vira card no pipeline Tickets GHL

`Tickets GHL` (`kBAMxq13EkXGXrccljKf`) já era o pipeline onde o time tocava
esse caso na mão — os estágios são `Enviar Ticket Suporte`, `Ticket Enviado`,
`Afiliacao Atribuida` e `Afiliacao Negada`. Nenhum workflow publicado tocava
nele até agora. Dois workflows novos (`tools/ticket_afiliado.py`) automatizam
os dois primeiros estágios, acionados pelo agente:

| Momento | Ação do agente | Workflow | Resultado |
|---|---|---|---|
| Halo detecta o caso | `Afiliado sem vínculo - abrir ticket` | `HTC \| Halo -> Ticket Afiliado (abrir)` | card em `Enviar Ticket Suporte` + nota |
| contato confirma o envio | `Afiliado - formulário enviado, avisar o John` | `HTC \| Halo -> Ticket Afiliado (enviado)` | card para `Ticket Enviado`, nota, bot desligado, SMS pro John |

`create_opportunity` sem `allow_multiple` atualiza a oportunidade existente do
contato naquele pipeline em vez de duplicar, então o segundo workflow move o
mesmo card.

### Dois "João" na conta
- `AoRfnKsAmrFW57EiadNQ` — **João Alves**, contato.arboled@gmail.com, +1 407 684 3440
- `wmlzZtJRtlFzilmaSojj` — **John Nogueira**, joaognogueiracardoso@gmail.com, +55 35 99208 3583

O e-mail de CC do formulário de afiliado é o do **John Nogueira**, então é ele
que recebe os avisos do fluxo de afiliado. Os três `humanHandOver` genéricos da
Halo continuam apontando para o João Alves.

### Criar workflow pela API interna
`POST /workflow/{loc}` com `{"name": ..., "status": "draft"}` devolve o id; os
passos entram depois pelo PUT normal. `DELETE /workflow/{loc}/{id}` apaga.
Passos `update_conversation_ai_status` e `find_opportunity` precisam de
`workflowsActionType: "INTERNAL"`, senão o PUT recusa com "action has a
corrupted type".

## Por que a Halo quase não ativa (auditoria 18–23/09/2026)

### A Halo funciona
Três leads reais foram atendidos por ela em 22–23/09 (Jeiselaine, Ranielly, Ana),
com conversa completa e follow-up. O problema não é o agente, é por onde a
mensagem entra.

### Volume real recebido no período
| Canal | msgs | % | pessoas |
|---|---|---|---|
| WhatsApp via STEVO (`TYPE_CUSTOM_SMS`, tipo 20) | 272 | 86% | 26 |
| Instagram (tipo 18) | 26 | 8% | 8 |
| WhatsApp oficial (tipo 19) | 17 | 5% | 5 |

### O gatilho `customer_reply` não dispara para provedor customizado
Toda mensagem do STEVO chega com `source: "api"` e `conversationProviderId`
(`682cdb5dc127505befd9fc7e`, app `STEVO`) — ou seja, é injetada pelo endpoint
`POST /conversations/messages/inbound`. Mensagens nativas (tipos 18 e 19) vêm
sem `source`. Já estava provado nesta base que **mensagem injetada pela API não
dispara `customer_reply`** (ver `tools/test_halo.py`), e os dados confirmam:

- dos **101 contatos que já receberam a tag `demo-halo`** (todos que a Halo já
  atendeu na vida), **100% têm WhatsApp oficial na conversa**;
- **zero** foram atendidos tendo só STEVO — apesar de 50 deles terem mensagens
  STEVO junto.

Nenhum workflow da conta filtra `message.type == 20`, então não há precedente de
automação reagindo a esse canal.

O `channels` do agente também não tem valor para provedor customizado. Os
válidos são `GMB, IG, FB, SMS, WebChat, WhatsApp, Live_Chat, Email, TIKTOK`
(descoberto por 422 num PUT com valor inválido). A Halo usa
`WhatsApp, SMS, IG, WebChat` — `SMS` não cobre o `TYPE_CUSTOM_SMS` do STEVO.

Saída possível: o STEVO já manda webhook para a conta (`Alerta Desconexao -
STEVO` usa `inbound_webhook`). Se ele puder postar um webhook por mensagem
recebida, um workflow de `inbound_webhook` inscreve o contato no atendimento da
Halo e contorna o gatilho.

### Instagram: confirmado em produção que era o estágio
Jaiane (22/09 13:55) e Dudu Adry (23/09 09:30) mandaram DM fria e receberam
`Opportunity created` **no mesmo minuto**, pelo `IG DM -> Add Pipeline`, que
dispara no mesmo `customer_reply` tipo 18. Ou seja: o gatilho da Halo também
disparou, e o fluxo morreu na condição de estágio — exatamente o que a correção
de hoje resolve. Não houve DM de Instagram depois da correção, então isso ainda
não foi visto rodando em produção, só no teste.

### A tag `demo-halo` é de uso único
A condição é `tags index-of-false ['demo-halo']` e o próprio fluxo aplica a tag.
Quem já foi atendido uma vez nunca mais entra. Dos leads do período, 4 já
estavam bloqueados por isso.
