# -*- coding: utf-8 -*-
"""A notificacao de transferencia chegava com os campos vazios.

A Halo grava os campos (Status do Ticket, Resumo, etc) e dispara o workflow de
transferencia praticamente ao mesmo tempo. O passo de notificacao renderizava
{{contact.status_do_ticket}} antes dos valores propagarem. Mesma corrida do bug
de comissao do afiliado.

Correcao: 2 minutos de espera entre desligar o bot e avisar o time.
"""
import os, json, time, uuid, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager, InternalGHLClient

HTC = os.environ["GHL_LOCATION_ID"]
WF = "65b4805f-af61-4dd9-b0bc-2692cc7dd2e1"
A = "/tmp/claude-0/-home-user-cli-ghl-htc/e5755955-47c9-5ed4-987a-fd68342e9ea2/scratchpad/"

c = InternalGHLClient(TokenManager(), HTC)
w = [x for x in c.get("/workflow/" + HTC) if x["_id"] == WF][0]
steps = requests.get(w["fileUrl"], timeout=40).json()["templates"]
json.dump(steps, open(A + "bkp_transfer_steps.json", "w"), ensure_ascii=False, indent=1)

if any(s.get("type") == "wait" for s in steps):
    print("ja tem espera; nada a fazer")
    raise SystemExit

campo = [s for s in steps if s.get("name") == "Campo - IA Desativada"][0]
notif = [s for s in steps if s.get("type") == "internal_notification"][0]
wid = str(uuid.uuid4())
espera = {"id": wid, "parentKey": campo["id"], "type": "wait", "name": "Esperar os campos gravarem",
          "attributes": {"type": "time", "startAfter": {"type": "minutes", "value": 2, "when": "after"},
                         "name": "Esperar os campos gravarem", "cat": "",
                         "isHybridAction": True, "hybridActionType": "wait",
                         "convertToMultipath": False, "transitions": []},
          "order": 0, "cat": "", "next": notif["id"]}
campo["next"] = wid
notif["parentKey"] = wid

saida = []
for s in steps:
    saida.append(s)
    if s["id"] == campo["id"]:
        saida.append(espera)
for i, s in enumerate(saida):
    s["order"] = i

trigs = c.get("/workflow/%s/trigger?workflowId=%s" % (HTC, WF))
trigs = trigs if isinstance(trigs, list) else []
body = {"name": w["name"], "version": w["version"], "status": "published",
        "meta": w.get("meta") or {}, "workflowData": {"templates": saida}}
if trigs:
    body["triggersChanged"] = True
    body["oldTriggers"] = trigs
    body["newTriggers"] = trigs
r = c.put("/workflow/%s/%s" % (HTC, WF), body)
print("PUT ->", "OK" if r and not r.get("_error") else json.dumps(r, ensure_ascii=False)[:300])

time.sleep(3)
w2 = [x for x in c.get("/workflow/" + HTC) if x["_id"] == WF][0]
print("\nstatus=%s versao=%s" % (w2["status"], w2["version"]))
for s in requests.get(w2["fileUrl"], timeout=40).json()["templates"]:
    print("  [%-28s] %s" % (s.get("type"), s.get("name")))
