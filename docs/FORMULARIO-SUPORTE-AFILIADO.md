# Formulário de suporte de afiliado do GoHighLevel

Link: https://www.gohighlevel.com/affiliate-support-cus-form

A página avisa que ela é **só** para pedidos relacionados a afiliado. Pedidos de
suporte normal da plataforma são descartados.

## Campos, na ordem em que aparecem

| Campo | Obrigatório | O que vai |
|---|---|---|
| First Name | sim | nome do cliente, como está na conta dele |
| Last Name | sim | sobrenome do cliente |
| Email | sim | **o mesmo e-mail usado para criar a conta do GoHighLevel** |
| Add a CC Email | não | `joaognogueiracardoso@gmail.com` |
| Phone | sim | telefone do cliente, com código do país |
| Affiliate Customer Support Request | sim | selecionar `Other` |
| Other / Additional Details | não | o texto em inglês abaixo |
| Additional Details (segunda caixa) | não | pode repetir o mesmo texto |
| Affiliate Link You Are Requesting To Move To OR Link You Are Wanting To Check For | sim | o link abaixo |
| File Upload | não, mas recomendado | print da conta ou do e-mail de confirmação |

## Textos para copiar

Additional Details, em inglês, sem traduzir:

```
I signed up through the following affiliate link, however my affiliate is not seeing me in the dashboard. Please tell me why this is happening and who I am under.
```

Affiliate Link:

```
https://www.gohighlevel.com/high-ticket-clube?fp_ref=high-ticket-clube54
```

## O campo que decide o caso

`Email`. É por ele que o suporte acha a conta. Se vier o e-mail de contato em
vez do e-mail do login do GoHighLevel, o ticket volta sem resposta útil.

## Quem preenche

O formulário é do titular da conta, não do afiliado — os três campos de
identidade (nome, e-mail, telefone) são do cliente. Por isso a Halo agora
conduz o cliente pelo formulário dentro da própria conversa, campo por campo,
e avisa o João no fim. Ver `tools/halo_capacidade_afiliado.py`.
