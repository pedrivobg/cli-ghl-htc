# -*- coding: utf-8 -*-
"""Caso de afiliacao nao atribuida: abre card no pipeline Tickets GHL e avisa o John.

Dois workflows, porque o caso tem dois momentos:
  A) a Halo detecta o caso            -> card em 'Enviar Ticket Suporte' + nota
  B) o contato confirma que enviou    -> card vai para 'Ticket Enviado', nota
                                         com o que aconteceu e aviso pro John

Os dois entram so pela acao do agente (triggerWorkflow), nao tem gatilho proprio.
"""
import os, json, time, uuid, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager, InternalGHLClient

HTC = os.environ["GHL_LOCATION_ID"]
A = "/tmp/claude-0/-home-user-cli-ghl-htc/e5755955-47c9-5ed4-987a-fd68342e9ea2/scratchpad/"

PIPE = "kBAMxq13EkXGXrccljKf"                     # Tickets GHL
ST_ABRIR = "31107f30-c4e6-48ea-b3e8-c7656da1ef7a"  # Enviar Ticket Suporte
ST_ENVIADO = "a72c1272-ad37-41cd-8d39-7c0403bca334"  # Ticket Enviado
JOHN = "wmlzZtJRtlFzilmaSojj"                      # John Nogueira, o dono dos casos de afiliado
GABRIEL = "4zth6nbXm83uGB8McW2L"                   # Gabriel Oliveira
BOT = "qQ36rFQsb7MncdXLNCFZ"
AI_FIELD = "btqf4ZzVvUEZnqKMhE2z"
CRM = "https://app.gohighlevel.com/v2/location/%s/contacts/detail/{{contact.id}}" % HTC
FORM = "https://www.gohighlevel.com/affiliate-support-cus-form"
LINK = "https://www.gohighlevel.com/high-ticket-clube?fp_ref=high-ticket-clube54"

tm = TokenManager()
for _ in range(6):                      # o refresh falha de vez em quando
    try:
        tm.get_token(); break
    except SystemExit:
        time.sleep(4)
c = InternalGHLClient(tm, HTC)


def no(tipo, nome, attrs, order):
    n = {"id": str(uuid.uuid4()), "order": order, "name": nome, "type": tipo, "attributes": attrs}
    # sem isso o builder recusa o passo com "action has a corrupted type"
    if tipo in ("update_conversation_ai_status", "find_opportunity"):
        n["workflowsActionType"] = "INTERNAL"
    return n


def encadear(passos):
    for i in range(len(passos) - 1):
        passos[i]["next"] = passos[i + 1]["id"]
        passos[i + 1]["parentKey"] = passos[i]["id"]
    return passos


def opp(stage):
    return {"fields": [], "type": "create_opportunity", "pipeline_id": PIPE,
            "pipeline_stage_id": stage, "opportunity_name": "{{contact.name}}",
            "opportunity_source": "halo-afiliado", "monetary_value": "",
            "opportunity_status": "open", "allow_backward": True}


NOTA_A = (
    "<p><strong>Caso de afiliacao nao atribuida, detectado pela Halo</strong></p>"
    "<p>O contato disse que criou a conta do GoHighLevel pelo link do HTC mas nao recebeu os bonus, "
    "ou que o afiliado nao esta vendo ele no dashboard.</p>"
    "<p>A Halo esta conduzindo o preenchimento do formulario de suporte de afiliados do GoHighLevel, "
    "campo por campo, dentro da propria conversa.</p>"
    "<p>Formulario: " + FORM + "<br>Link de afiliado usado no pedido: " + LINK + "</p>"
    "<p>Enquanto o card estiver em <strong>Enviar Ticket Suporte</strong>, o contato ainda nao "
    "confirmou o envio. Se ele sumir no meio, o card fica aqui para alguem retomar.</p>")

NOTA_B = (
    "<p><strong>Formulario de suporte de afiliados enviado</strong></p>"
    "<p>O contato confirmou para a Halo que preencheu e enviou o formulario, com o John em copia "
    "(joaognogueiracardoso@gmail.com).</p>"
    "<p>Motivo: {{contact.status_do_ticket}}<br>Resumo da conversa: {{contact.resumo_ai_call}}</p>"
    "<p>Proximo passo: acompanhar a resposta do GoHighLevel e mover este card para "
    "<strong>Afiliacao Atribuida</strong> ou <strong>Afiliacao Negada</strong>.</p>")

SMS = ("HALO - AFILIACAO NAO ATRIBUIDA\n\n"
       "Contato: {{contact.name}}\nTelefone: {{contact.phone}}\nEmail: {{contact.email}}\n\n"
       "Entrou pelo link do HTC e nao foi vinculado. Ja preencheu e enviou o formulario de "
       "suporte de afiliados do GoHighLevel, com voce em copia.\n\n"
       "Resumo: {{contact.resumo_ai_call}}\n\n"
       "Card criado em Tickets GHL > Ticket Enviado.\n"
       "O bot foi desligado, responda direto na conversa:\n" + CRM)

PLANOS = [
    ("HTC | Halo -> Ticket Afiliado (abrir)", [
        ("create_opportunity", "Card em Enviar Ticket Suporte", opp(ST_ABRIR)),
        ("add_notes", "Nota - caso detectado", {"type": "add_notes", "html": NOTA_A}),
    ]),
    ("HTC | Halo -> Ticket Afiliado (enviado)", [
        ("update_conversation_ai_status", "Desligar Bot - Halo",
         {"assignedEmployeeId": BOT, "status": "inactive", "shouldReactivateAfterTimeOut": False,
          "type": "update_conversation_ai_status", "__customInputs__": {}}),
        ("update_contact_field", "Campo - IA Desativada",
         {"type": "update_contact_field", "actionType": "update_field_data",
          "fields": [{"field": AI_FIELD, "value": "Off", "title": "AI Activation",
                      "type": "select", "date": ""}]}),
        ("wait", "Esperar os campos gravarem",
         {"type": "time", "startAfter": {"type": "minutes", "value": 2, "when": "after"},
          "name": "Esperar os campos gravarem", "cat": "", "isHybridAction": True,
          "hybridActionType": "wait", "convertToMultipath": False, "transitions": []}),
        ("create_opportunity", "Card para Ticket Enviado", opp(ST_ENVIADO)),
        ("add_notes", "Nota - formulario enviado", {"type": "add_notes", "html": NOTA_B}),
        ("internal_notification", "Avisar o John",
         {"type": "sms", "sms": {"body": SMS, "selectedUser": [JOHN, GABRIEL],
                                 "userType": "user", "attachments": []}}),
    ]),
]

existentes = {w["name"]: w for w in c.get("/workflow/" + HTC)}
criados = {}
for nome, plano in PLANOS:
    w = existentes.get(nome)
    if w:
        wid = w["_id"]
        print("ja existe: %s" % nome)
    else:
        wid = c.post("/workflow/" + HTC, {"name": nome, "status": "draft"})["id"]
        print("criado:    %s  %s" % (nome, wid))
    passos = encadear([no(t, n, a, i) for i, (t, n, a) in enumerate(plano)])
    w = [x for x in c.get("/workflow/" + HTC) if x["_id"] == wid][0]
    r = c.put("/workflow/%s/%s" % (HTC, wid), {
        "name": nome, "version": w.get("version"), "status": "published",
        "meta": w.get("meta") or {}, "workflowData": {"templates": passos}})
    print("   PUT -> %s" % ("OK" if r and not r.get("_error") else json.dumps(r, ensure_ascii=False)[:300]))
    criados[nome] = wid

json.dump(criados, open(A + "ticket_wfs.json", "w"), indent=1)
time.sleep(3)
print("\n### VERIFICACAO")
todos = c.get("/workflow/" + HTC)
for nome, wid in criados.items():
    w = [x for x in todos if x["_id"] == wid][0]
    t = requests.get(w["fileUrl"], timeout=40).json().get("templates", [])
    print("\n%-42s status=%s passos=%d" % (nome, w["status"], len(t)))
    for s in t:
        print("   [%-28s] %s" % (s.get("type"), s.get("name")))
