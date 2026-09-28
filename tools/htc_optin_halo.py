# -*- coding: utf-8 -*-
"""1.2 Opt In (Wpp): Halo ligada na entrada, sequência por SMS (STEVO).

Decisão do time (28/09): por enquanto a sequência sai pelos passos de SMS, que nesta
conta vão pelo STEVO (WhatsApp não oficial). Os passos de template do WhatsApp
oficial ficam no fluxo, desligados; quando os templates forem aprovados, é só trocar
os nós.

Este script:
1. liga a Halo antes da primeira mensagem (workflow "HTC | Ativar Halo"). Ela só fala
   quando o lead responde, e o follow-up de IA dela só começa depois disso;
2. corrige o texto do Wpp #1 ("pesquisado" -> "pesquisando", "trabahla" -> "trabalha");
3. põe 2 dias de espera entre o Wpp #4 (materiais) e o Wpp #5 ("minha ex me deixando
   no vácuo"), que saíam grudados. Era assim até a versão 24.

Não liga nem desliga nenhum passo: SMS continuam ligados, templates desligados.

Uso: python tools/htc_optin_halo.py [--dry]
"""
import os, sys, time, uuid, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
LOC = os.environ["GHL_LOCATION_ID"]
WF = "20022e2a-53b8-48ba-85d4-83335d93a1f4"
ATIVAR = "85ad46cd-404c-49a7-9b87-024aca1d107a"   # HTC | Ativar Halo
CONFIG = ["stopOnResponse", "allowMultiple", "window", "allowMultipleOpportunity",
          "removeContactFromLastStep", "autoMarkAsRead", "timezone"]
TEXTO = [("estava pesquisado sobre", "estava pesquisando sobre"), ("trabahla", "trabalha")]

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
por_id = {s["id"]: s for s in steps}
por_nome = {s.get("name"): s for s in steps}
mudou = []

# 1) Halo ligada antes da primeira mensagem
if not any((s.get("attributes") or {}).get("workflow_id") == ATIVAR for s in steps):
    primeiro = [s for s in steps if not s.get("parentKey")][0]
    novo = {"id": str(uuid.uuid4()), "name": "Ativar Halo", "type": "add_to_workflow",
            "next": primeiro["id"],
            "attributes": {"input_trigger_params": False, "type": "add_to_workflow", "workflow_id": ATIVAR}}
    primeiro["parentKey"] = novo["id"]
    steps.insert(0, novo)
    mudou.append("Ativar Halo antes de %s" % primeiro["name"])

# 2) texto do Wpp #1
a = por_nome["Wpp #1"]["attributes"]
corpo = a["body"]
for velho, novo_txt in TEXTO:
    corpo = corpo.replace(velho, novo_txt)
if corpo != a["body"]:
    a["body"] = corpo
    mudou.append("texto do Wpp #1")

# 3) espera entre Wpp #4 e Wpp #5
w4, w5 = por_nome["Wpp #4"], por_nome["Wpp #5"]
if w4.get("next") == w5["id"]:
    espera = {"id": str(uuid.uuid4()), "name": "Wait - 2d", "type": "wait", "parentKey": w4["id"],
              "next": w5["id"],
              "attributes": {"type": "time", "startAfter": {"type": "days", "value": 2, "when": "after"},
                             "name": "Wait - 2d", "cat": "", "isHybridAction": True,
                             "hybridActionType": "wait", "convertToMultipath": False, "transitions": []}}
    w4["next"] = espera["id"]
    w5["parentKey"] = espera["id"]
    steps.insert(steps.index(w5), espera)
    mudou.append("2 dias entre Wpp #4 e Wpp #5")

for i, s in enumerate(steps):
    s["order"] = i
for s in steps:
    print("  %-16s %-14s %s" % (s["type"], s.get("name"),
                                "desligado" if (s.get("advanceCanvasMeta") or {}).get("isDisabled") else ""))
print("mudanças: %s" % ("; ".join(mudou) or "nenhuma"))
if mudou and not DRY:
    print("versão anterior no histórico do GHL: %s" % w["version"])
    tr = requests.get(B + "/workflow/%s/trigger" % LOC, headers=H, params={"workflowId": WF}, timeout=30).json()
    tr = tr if isinstance(tr, list) else []
    body = {"name": w["name"], "version": w["version"], "status": "published",
            "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
    # o PUT zera as configurações que não vêm no corpo (parar ao responder, janela...)
    body.update({k: w.get(k) for k in CONFIG})
    if tr:
        body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
    r = requests.put(B + "/workflow/%s/%s" % (LOC, WF), headers=H, json=body, timeout=40)
    print("PUT -> %s" % (r.status_code if r.status_code in (200, 201) else r.text[:400]))
