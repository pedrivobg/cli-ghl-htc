# -*- coding: utf-8 -*-
"""Devolve ao estado anterior os workflows fora da Halo que o htc_notificacoes_john.py mexeu.

Regra do time (28/09): só o que é da Halo vai para o John. NPS - HTC, SaaS New Reward e
Assign Calling Leads voltam para a versão de antes da troca, com os mesmos
destinatários de antes.

Uso: python tools/htc_reverter_nao_halo.py [--dry]
"""
import os, sys, time, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
LOC = os.environ["GHL_LOCATION_ID"]
# workflow -> versão anterior à troca
APAGADO = "ocec1DGKusgkahOiPMN3"
CONFIG = ["stopOnResponse", "allowMultiple", "window", "allowMultipleOpportunity",
          "removeContactFromLastStep", "autoMarkAsRead", "timezone"]
VOLTAR = {"983fd918": 21, "e1148c12": 46, "d428b6c8": 2}

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}

todos = requests.get(B + "/workflow/" + LOC, headers=H, timeout=60).json()
for pre, versao in VOLTAR.items():
    w = [x for x in todos if x["_id"].startswith(pre)][0]
    hist = requests.get(B + "/workflow/%s/%s/history" % (LOC, w["_id"]), headers=H, timeout=40).json()
    v = [x for x in hist if x["version"] == versao][0]
    steps = requests.get(v["fileUrl"], timeout=40).json()["templates"]
    for s in steps:
        a = s.get("attributes") or {}
        if s["type"] == "assign_user" and APAGADO in (a.get("user_list") or []):
            # o GHL não salva workflow apontando para usuário apagado; os demais voltam
            lista = [u for u in a["user_list"] if u != APAGADO]
            a["user_list"] = lista
            a["traffic_weightage"] = {u: 1 for u in lista}
            a["traffic_index"] = [{"id": u, "indexes": [i + 1]} for i, u in enumerate(lista)]
            a["total_index"] = len(lista)
    print("%-22s versão %s -> conteúdo da %s" % (w["name"], w["version"], versao))
    if DRY:
        continue
    tr = requests.get(B + "/workflow/%s/trigger" % LOC, headers=H, params={"workflowId": w["_id"]}, timeout=30).json()
    tr = tr if isinstance(tr, list) else []
    body = {"name": w["name"], "version": w["version"], "status": w.get("status", "published"),
            "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
    # o PUT zera as configurações que não vêm no corpo; voltam as da versão anterior
    body.update({k: v.get(k) for k in CONFIG})
    if tr:
        body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
    r = requests.put(B + "/workflow/%s/%s" % (LOC, w["_id"]), headers=H, json=body, timeout=40)
    print("   -> %s" % (r.status_code if r.status_code in (200, 201) else r.text[:300]))
