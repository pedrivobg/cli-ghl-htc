# -*- coding: utf-8 -*-
"""Cria o workflow "HTC | Ativar Halo" e, com --inscrever, liga a Halo para leads parados.

A Halo só responde quem está com ela ativa, e até agora ela só era ligada depois que o
lead respondia. Com a Halo ativa desde a entrada, ela continua quieta: agente do
Conversation AI só fala quando recebe mensagem. A primeira resposta do lead já cai
nela, e o follow-up de IA dela só começa depois disso.

O workflow tem dois passos, sem gatilho: liga o bot e marca AI Activation = On. Serve
para os fluxos de entrada chamarem ("Add to workflow") e para ligar em lote os leads
que entraram e nunca responderam.

    python tools/htc_ativar_halo.py                 # cria/confere o workflow
    python tools/htc_ativar_halo.py --listar        # mostra quem seria ligado
    python tools/htc_ativar_halo.py --inscrever     # liga a Halo para esses leads

Critério do lote: oportunidade aberta no Afiliado Pipeline nos estágios de entrada
(Opt In Leads, Afiliado Lead 1st step, Instagram Leads), criada nos últimos DIAS dias,
sem nenhuma mensagem recebida do lead, sem DND.
"""
import os, sys, json, time, uuid, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

B = "https://backend.leadconnectorhq.com"
S = "https://services.leadconnectorhq.com"
LOC = os.environ["GHL_LOCATION_ID"]
BOT = "qQ36rFQsb7MncdXLNCFZ"
CAMPO_IA = "btqf4ZzVvUEZnqKMhE2z"
NOME = "HTC | Ativar Halo"
PIPE = "d2UrqygBbHikBX4gKH3F"
ENTRADA = {"d2891e74-0fb0-41ee-a583-af7351de8c21": "Opt In Leads",
           "0f221a5c-d5c3-4a42-a75c-25d8b4db9507": "Afiliado Lead (1st step)",
           "422a0d12-f6c9-4b09-8e04-924222a4ca55": "Instagram Leads"}
DIAS = 30

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}
P = {"Authorization": "Bearer " + os.environ["GHL_API_KEY"].strip(), "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}


def passos():
    a, b = str(uuid.uuid4()), str(uuid.uuid4())
    return [
        {"id": a, "order": 0, "name": "Ativar Bot - Halo", "type": "update_conversation_ai_status",
         "workflowsActionType": "INTERNAL", "next": b,
         "attributes": {"assignedEmployeeId": BOT, "status": "active",
                        "type": "update_conversation_ai_status", "__customInputs__": {}}},
        {"id": b, "order": 1, "name": "Campo - IA Ativada", "type": "update_contact_field",
         "parentKey": a,
         "attributes": {"type": "update_contact_field", "actionType": "update_field_data",
                        "fields": [{"field": CAMPO_IA, "value": "On", "title": "AI Activation",
                                    "type": "select", "date": ""}]}},
    ]


def workflow():
    ws = [w for w in requests.get(B + "/workflow/" + LOC, headers=H, timeout=60).json()
          if w.get("name") == NOME and not w.get("deleted")]
    if ws:
        return ws[0]["_id"]
    wid = requests.post(B + "/workflow/" + LOC, headers=H, timeout=40,
                        json={"name": NOME, "status": "draft"}).json()["id"]
    w = [x for x in requests.get(B + "/workflow/" + LOC, headers=H, timeout=60).json() if x["_id"] == wid][0]
    r = requests.put(B + "/workflow/%s/%s" % (LOC, wid), headers=H, timeout=40, json={
        "name": NOME, "version": w["version"], "status": "published", "meta": w.get("meta") or {},
        "workflowData": {"templates": passos()}})
    assert r.status_code in (200, 201), r.text[:300]
    return wid


def parados():
    desde = time.strftime("%Y-%m-%d", time.gmtime(time.time() - DIAS * 86400))
    ops, pagina = [], 1
    while True:
        j = requests.get(S + "/opportunities/search", headers=P, timeout=60, params={
            "location_id": LOC, "pipeline_id": PIPE, "status": "open", "limit": 100, "page": pagina}).json()
        o = j.get("opportunities", [])
        ops += o
        if len(o) < 100:
            break
        pagina += 1
    ops = [o for o in ops if o["pipelineStageId"] in ENTRADA and (o.get("createdAt") or "") >= desde]
    saida = []
    for o in ops:
        c = requests.get(S + "/contacts/" + o["contactId"], headers=P, timeout=30).json().get("contact", {})
        if c.get("dnd"):
            continue
        conv = requests.get(S + "/conversations/search", headers=dict(P, Version="2021-04-15"), timeout=30,
                            params={"locationId": LOC, "contactId": o["contactId"]}).json().get("conversations", [])
        recebeu = False
        for cv in conv:
            ms = requests.get(S + "/conversations/%s/messages" % cv["id"], headers=dict(P, Version="2021-04-15"),
                              timeout=30, params={"limit": 100}).json().get("messages", {}).get("messages", [])
            if any(m.get("direction") == "inbound" for m in ms):
                recebeu = True; break
        if not recebeu:
            saida.append((o, c))
        time.sleep(0.2)
    return saida


if __name__ == "__main__":
    wid = workflow()
    print("workflow %s: %s" % (NOME, wid))
    if "--listar" in sys.argv or "--inscrever" in sys.argv:
        lista = parados()
        print("%d leads parados nos últimos %d dias" % (len(lista), DIAS))
        for o, c in lista:
            print("  %s  %-24s %-28s %s" % (o["createdAt"][:10], ENTRADA[o["pipelineStageId"]],
                                           (c.get("contactName") or c.get("firstName") or "")[:28], c.get("id")))
        if "--inscrever" in sys.argv:
            ok = 0
            for o, c in lista:
                r = requests.post(S + "/contacts/%s/workflow/%s" % (c["id"], wid), headers=P, timeout=30, json={})
                ok += r.status_code in (200, 201)
                time.sleep(0.3)
            print("Halo ligada para %d de %d" % (ok, len(lista)))
