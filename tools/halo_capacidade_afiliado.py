# -*- coding: utf-8 -*-
"""Adiciona a capacidade 'entrou pelo link de afiliado e nao recebeu nada' na Halo.

O agente aceita PUT em /conversation-ai/agents/{id} com o PIT (o token do
Firebase da 403 nessa rota). O fullPrompt NAO e regenerado pelo servidor, entao
ele precisa ser remontado aqui no formato ## Personality / ## Goal /
## Instructions.

Rode com --dry para so gravar o resultado em disco sem tocar na conta.
"""
import os, sys, json, requests

PIT = os.environ["GHL_API_KEY"]
HTC = os.environ["GHL_LOCATION_ID"]
BOT = "qQ36rFQsb7MncdXLNCFZ"
B = "https://services.leadconnectorhq.com"
A = "/tmp/claude-0/-home-user-cli-ghl-htc/e5755955-47c9-5ed4-987a-fd68342e9ea2/scratchpad/"
H = {"Authorization": "Bearer " + PIT, "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}
DRY = "--dry" in sys.argv

FORM = "https://www.gohighlevel.com/affiliate-support-cus-form"
LINK_AFILIADO = "https://www.gohighlevel.com/high-ticket-clube?fp_ref=high-ticket-clube54"
CC = "joaognogueiracardoso@gmail.com"
DETALHES = ("I signed up through the following affiliate link, however my affiliate "
            "is not seeing me in the dashboard. Please tell me why this is happening "
            "and who I am under.")

BLOCO = """ENTROU PELO LINK DE AFILIADO E NÃO RECEBEU NADA, PRIORIDADE MÁXIMA:

Quando a pessoa disser que criou a conta pelo nosso link mas não recebeu os bônus, não entrou no grupo, ou que o HTC não está vendo ela como indicação, essa é a PRIMEIRA coisa que você faz. Qualquer outro assunto da conversa fica para depois.

Isso acontece porque o GoHighLevel não vinculou a conta dela ao nosso link de afiliado. Só o suporte de afiliados do GoHighLevel corrige, e quem precisa abrir o pedido é ela mesma, porque a conta está no nome dela.

Conduza o passo a passo abaixo uma etapa por mensagem, esperando a confirmação antes de seguir para a próxima.

ETAPA 1, antes de qualquer resposta, acione a ação "Afiliado sem vínculo - abrir ticket". Ela abre o card do contato no pipeline Tickets GHL com a nota explicando o caso, para o time ver esse atendimento mesmo que a pessoa suma no meio do caminho.

ETAPA 2, abrir o formulário:

---
Consigo resolver isso com você agora.

O GoHighLevel não vinculou sua conta ao nosso link, e quem corrige isso é o suporte de afiliados deles. Leva uns 2 minutos.

Abre esse formulário: {form}
---

ETAPA 3, dizer campo por campo o que preencher:

- First Name e Last Name: o nome e o sobrenome dela
- Email: o MESMO e-mail que ela usou para criar a conta do GoHighLevel. Esse é o campo mais importante do formulário, se estiver errado o suporte não acha a conta
- Add a CC Email: {cc}
- Phone: o telefone dela, com o código do país
- Affiliate Customer Support Request: selecionar a opção "Other"
- Other / Additional Details: copiar e colar exatamente este texto, em inglês, sem traduzir e sem mudar nada:

{detalhes}

- Affiliate Link You Are Requesting To Move To OR Link You Are Wanting To Check For: copiar e colar exatamente este link:

{link}

- File Upload: se ela tiver um print da conta ou do e-mail de confirmação da assinatura, anexar. É opcional, mas com o print o suporte responde mais rápido

ETAPA 4, pedir para ela enviar o formulário e avisar quando terminar.

ETAPA 5, quando ela confirmar que enviou, encerrar assim:

---
Pronto, é exatamente isso.

Já avisei o John aqui do time. Ele vai acompanhar seu caso junto ao GoHighLevel e entra em contato com você em breve.
---

Assim que a pessoa confirmar que enviou o formulário, faça nesta ordem:
1. Salve em Status do Ticket: "Entrou pelo link de afiliado do HTC e não foi vinculado; formulário de suporte de afiliados enviado"
2. Salve em Resumo da Conversa o que aconteceu, incluindo o e-mail que ela usou na conta do GoHighLevel se ela tiver informado
3. Acione a ação "Afiliado - formulário enviado, avisar o John"

É essa ação que avisa o John de verdade, move o card do contato para "Ticket Enviado" no pipeline Tickets GHL e registra a nota com o que aconteceu. Só diga que o John foi avisado depois de acioná-la.

REGRAS DESSE ATENDIMENTO:
- Mande os campos em partes, nunca despeje o formulário inteiro em uma mensagem só
- Os dois textos em inglês, o de Additional Details e o link de afiliado, são copiados letra por letra. Não traduza, não resuma, não adapte
- Se ela não lembrar qual e-mail usou, peça para procurar na caixa de entrada o e-mail de boas-vindas do GoHighLevel
- Nunca peça dados de cartão, senha ou documento, nem para preencher o formulário nem fora dele
- Nunca prometa prazo de resposta do GoHighLevel. Você garante que o John vai acompanhar, não que o suporte responde em X dias
- Se ela já tiver enviado o formulário antes e continuar sem resposta, não mande preencher de novo: acione a ação "Afiliado - formulário enviado, avisar o John" na hora e diga que o John vai assumir daqui
""".format(form=FORM, cc=CC, detalhes=DETALHES, link=LINK_AFILIADO)

ANCORA = "OBJEÇÕES, COMO RESPONDER:"
LINK_ANTIGO = "* Grupo de WhatsApp da comunidade, só depois de criar a conta:"
LINK_NOVO = ("* Suporte de afiliados do GoHighLevel, para quem entrou pelo link e não foi vinculado: "
             + FORM + "\n* Link de afiliado do HTC para o formulário de suporte: " + LINK_AFILIADO
             + "\n" + LINK_ANTIGO)

GOAL_ANCORA = "Você conduz sozinha até o fim. Só chama humano nos casos listados nas instruções."
GOAL_NOVO = (GOAL_ANCORA + "\n\nEXCEÇÃO DE PRIORIDADE: se a pessoa disser que já criou a conta pelo "
             "nosso link e não recebeu os bônus, ou que o HTC não está vendo ela como indicação, "
             "pare de vender e vá direto para o passo a passo do suporte de afiliados descrito nas "
             "instruções. Ela já é cliente, o que ela precisa é de resolução, não de oferta.")

# ---------------------------------------------------------------- montagem
r = requests.get(B + "/conversation-ai/agents/%s?locationId=%s" % (BOT, HTC), headers=H, timeout=30)
r.raise_for_status()
ag = r.json().get("data", r.json())
json.dump(ag, open(A + "bkp_agente_antes.json", "w"), ensure_ascii=False, indent=1)

pers = ag["personality"]
goal = ag["goal"]
inst = ag["instructions"]

if "affiliate-support-cus-form" in inst:
    print("a capacidade ja esta no prompt; nada a fazer")
    sys.exit(0)

assert ANCORA in inst, "ancora das objecoes nao encontrada"
assert LINK_ANTIGO in inst, "ancora dos links nao encontrada"
assert GOAL_ANCORA in goal, "ancora do goal nao encontrada"

inst = inst.replace(ANCORA, BLOCO + "\n" + ANCORA, 1)
inst = inst.replace(LINK_ANTIGO, LINK_NOVO, 1)
goal = goal.replace(GOAL_ANCORA, GOAL_NOVO, 1)

full = "## Personality\n\n%s\n\n## Goal\n\n%s\n\n## Instructions\n\n%s" % (pers, goal, inst)

# o servidor ignora os tres campos quando fullPrompt vem junto, entao vai em dois PUTs
payload = {"personality": pers, "goal": goal, "instructions": inst,
           "fullPrompt": full}
json.dump(payload, open(A + "agente_novo.json", "w"), ensure_ascii=False, indent=1)
print("personality %5d  goal %5d  instructions %5d  fullPrompt %5d"
      % (len(pers), len(goal), len(inst), len(full)))

if DRY:
    print("\n--dry: nada foi enviado. Resultado em agente_novo.json")
    sys.exit(0)

p = requests.put(B + "/conversation-ai/agents/%s?locationId=%s" % (BOT, HTC),
                 headers=H, json=payload, timeout=40)
print("PUT -> %s %s" % (p.status_code, p.text[:200].replace("\n", " ")))

# ---------------------------------------------------------------- conferencia
v = requests.get(B + "/conversation-ai/agents/%s?locationId=%s" % (BOT, HTC), headers=H, timeout=30)
d = v.json().get("data", v.json())
print("\n### VERIFICACAO")
for campo in ("instructions", "goal", "fullPrompt"):
    txt = d.get(campo) or ""
    print("  %-13s %5d chars  formulario=%s  cc=%s  link=%s"
          % (campo, len(txt), FORM in txt, CC in txt, LINK_AFILIADO in txt))
print("  texto em ingles presente:", DETALHES[:40] in (d.get("instructions") or ""))
