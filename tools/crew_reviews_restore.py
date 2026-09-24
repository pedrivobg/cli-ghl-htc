# -*- coding: utf-8 -*-
"""Volta os 4 SMS de pedido de review ao texto original do snapshot (com a doação).

O time decidiu manter a doação por review. Em vez de reescrever de memória, lê a
versão anterior de cada workflow no histórico do GHL e copia de lá o corpo exato de
cada SMS, conta por conta. Só mexe nos 4 SMS de review; o resto do workflow fica
como está agora.

Uso: python tools/crew_reviews_restore.py [--dry]
"""
import sys, time, json, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
WF_NOME = "Review Request Sent -> 1 Month Review Followup"
CONTAS = {"OapfddiSt8scplnWw4oI": "Best Painting", "emq5z0PS5ddzVY2lGz74": "WN Painting",
          "D5c3tvzXVueuFdF19ib6": "SV Rental", "6KW7de8zxEIekNQUTAUO": "VIX",
          "LHJ8vLSVTQXFwtPVFcB6": "MK Freitas", "XkXTjVzjcoDmLOnKGLiH": "Snapshot Las Vegas"}

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}


def corpo(s):
    a = s["attributes"]
    return a["sms"] if isinstance(a.get("sms"), dict) and "body" in a["sms"] else a


for loc, nome in CONTAS.items():
    w = [x for x in requests.get(B + "/workflow/" + loc, headers=H, timeout=30).json() if x["name"] == WF_NOME][0]
    hist = requests.get(B + "/workflow/%s/%s/history" % (loc, w["_id"]), headers=H, timeout=30).json()
    # a versão mais recente que ainda tinha a doação
    orig = None
    for v in sorted(hist, key=lambda v: -int(v.get("version") or 0)):
        st = requests.get(v["fileUrl"], timeout=30).json().get("templates", [])
        txt = {s["id"]: corpo(s).get("body", "") for s in st if s.get("type") == "sms"}
        if any("donate" in t.lower() or "meal" in t.lower() for t in txt.values()):
            orig = (v.get("version"), txt); break
    if not orig:
        print("%-18s sem versao com doacao no historico; nada feito" % nome); continue
    atual = requests.get(w["fileUrl"], timeout=30).json()["templates"]
    mudou = 0
    for s in atual:
        if s.get("type") == "sms" and s["id"] in orig[1] and corpo(s).get("body") != orig[1][s["id"]]:
            corpo(s)["body"] = orig[1][s["id"]]; mudou += 1
    if mudou and not DRY:
        tr = requests.get(B + "/workflow/%s/trigger" % loc, headers=H, params={"workflowId": w["_id"]}, timeout=30).json()
        tr = tr if isinstance(tr, list) else []
        body = {"name": w["name"], "version": w["version"], "status": w.get("status", "published"),
                "meta": w.get("meta") or {}, "workflowData": {"templates": atual}}
        if tr:
            body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
        r = requests.put(B + "/workflow/%s/%s" % (loc, w["_id"]), headers=H, json=body, timeout=40)
        assert r.status_code in (200, 201), r.text[:300]
    print("%-18s restaurado da v%s: %d SMS%s" % (nome, orig[0], mudou, " (dry)" if DRY else ""))
