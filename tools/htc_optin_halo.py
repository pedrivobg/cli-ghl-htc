# -*- coding: utf-8 -*-
"""1.2 Opt In (Wpp): primeira mensagem pelo WhatsApp oficial e Halo ligada na entrada.

Em 28/09 o fluxo passou a mandar tudo por passos de SMS, que nesta conta saem pelo
STEVO. A Halo não responde mensagem que chega pelo STEVO, e resposta pelo STEVO não
dispara "Customer replied", então o lead respondia e não era atendido, e a sequência
não parava. Até a versão 27 os SMS ficavam desligados e só os templates saíam.

Este script:
1. volta a primeira mensagem para o template aprovado (1187753286790883), com o nome
   "John" no lugar de {{user.name}}, que chegava em branco ("Fala Ana!  aqui do HTC");
2. liga a Halo antes de mandar (workflow "HTC | Ativar Halo"); ela só fala quando o lead
   responde;
3. religa os templates de follow-up (materiais em 23h, cases em +5 dias);
4. deixa os passos de SMS no fluxo, desligados, para voltar com um clique se o time quiser.

Uso: python tools/htc_optin_halo.py [--dry]
"""
import os, sys, json, time, uuid, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
LOC = os.environ["GHL_LOCATION_ID"]
WF = "20022e2a-53b8-48ba-85d4-83335d93a1f4"
ATIVAR = "85ad46cd-404c-49a7-9b87-024aca1d107a"   # HTC | Ativar Halo
NUMERO = "921014717756181"
PRIMEIRA = "1187753286790883"

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}

w = [x for x in requests.get(B + "/workflow/" + LOC, headers=H, timeout=60).json() if x["_id"] == WF][0]
steps = requests.get(w["fileUrl"], timeout=40).json()["templates"]
if any(s["type"] == "whatsapp_v2" and s["attributes"].get("template_id") == PRIMEIRA for s in steps):
    sys.exit("o template de primeira mensagem já está no fluxo; nada a fazer")

id_ativar, id_zap = str(uuid.uuid4()), str(uuid.uuid4())
id_ok, id_falhou = str(uuid.uuid4()), str(uuid.uuid4())
primeiro = steps[0]
novos = [
    {"id": id_ativar, "order": 0, "name": "Ativar Halo", "type": "add_to_workflow", "next": id_zap,
     "attributes": {"input_trigger_params": False, "type": "add_to_workflow", "workflow_id": ATIVAR}},
    {"id": id_zap, "order": 1, "name": "WhatsApp #1", "type": "whatsapp_v2", "parentKey": id_ativar,
     "workflowsActionType": "INTERNAL", "next": [id_ok, id_falhou],
     "attributes": {
         "template_id": PRIMEIRA, "toggle_branch": True, "from_phone_number": NUMERO,
         "message": "Fala {{contact.first_name}}! John aqui do HTC. Vi que você estava pesquisado sobre "
                    "GoHighLevel.. Hoje você tem uma agência ou trabalha com marketing/IA ?",
         "{{contact.first_name}}": "{{contact.first_name}}", "{{user.name}}": "John",
         "type": "whatsapp_v2", "__customInputs__": {}, "cat": "multi-path", "convertToMultipath": True,
         "transitions": [
             {"id": id_ok, "name": "Delivered", "fields": {"condition": "Is Message Delivered to the user"},
              "meta": {"key": "is_delivered", "__branchKey__": "predefined_Delivered"}, "conditionType": "pre-defined"},
             {"id": id_falhou, "name": "Undelivered", "fields": {"condition": "Is Message not delivered to the user"},
              "meta": {"key": "is_not_delivered", "__branchKey__": "predefined_Undelivered"}, "conditionType": "pre-defined"}],
         "__name__": "WhatsApp #1"}},
    {"id": id_ok, "order": 2, "name": "Delivered", "type": "transition", "parentKey": id_zap,
     "next": primeiro["id"], "attributes": {}},
    {"id": id_falhou, "order": 3, "name": "Undelivered", "type": "transition", "parentKey": id_zap,
     "next": None, "attributes": {}},
]
primeiro["parentKey"] = id_ok
for s in steps:
    liga = s["type"] == "whatsapp_v2"
    if s["type"] in ("sms", "whatsapp_v2"):
        s["advanceCanvasMeta"] = {"isDisabled": not liga}
for i, s in enumerate(novos + steps):
    s["order"] = i
steps = novos + steps

for s in steps:
    print("  %-12s %-22s %s" % (s["type"], s.get("name"),
                                "DESLIGADO" if (s.get("advanceCanvasMeta") or {}).get("isDisabled") else ""))
if not DRY:
    print("versão anterior no histórico do GHL: %s" % w["version"])
    tr = requests.get(B + "/workflow/%s/trigger" % LOC, headers=H, params={"workflowId": WF}, timeout=30).json()
    tr = tr if isinstance(tr, list) else []
    body = {"name": w["name"], "version": w["version"], "status": "published",
            "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
    if tr:
        body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
    r = requests.put(B + "/workflow/%s/%s" % (LOC, WF), headers=H, json=body, timeout=40)
    print("PUT -> %s" % (r.status_code if r.status_code in (200, 201) else r.text[:400]))
