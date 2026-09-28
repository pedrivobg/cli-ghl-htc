# -*- coding: utf-8 -*-
"""WN Painting: corrige na conta do GHL os itens do checklist "2 · Build" (28/09/2026).

1. Custom values:
   - Company Website Link sem a "/" do fim. Com a barra, todo link montado com ela
     sai com "//" (…com//review, …com//thank-you).
   - Company Email: e-mail da empresa informado no formulário de onboarding.
   - Company Phone (Functional e Aesthetic): telefone da empresa do mesmo formulário.
   Os custom values do A2P (já aprovado) não são mexidos.
2. Workflow 0.0: o formulário de orçamento do site (AI Studio) não é um formulário do
   GHL. Ele manda um evento externo com formId "estimate-request-form". Entra um
   gatilho External Tracking Event para esse form; o gatilho antigo continua.
3. Avisos internos que iam para "All users" passam a ir para o usuário do dono.

Os PUT de workflow levam os sete campos de configuração, que o endpoint zera
quando não vêm no corpo.

Uso: python tools/crew_wn_build_fix.py [--dry]
"""
import sys, json, time, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
LOC = "emq5z0PS5ddzVY2lGz74"            # WN Painting & Remodeling
DONO = "MRqMbnHIdJ0gKEre9bek"           # Wesley Ferreira Neves
FORM_SITE = "estimate-request-form"
CONFIG = ["stopOnResponse", "allowMultiple", "window", "allowMultipleOpportunity",
          "removeContactFromLastStep", "autoMarkAsRead", "timezone"]
VALORES = {
    "company_website_link": "https://wnpaintingremodeling.com",
    "company_email": "wesleynevespainting@gmail.com",
    "company_phone_functional": "+12674399848",
    "company_twilio_phone": "(267) 439-9848",
}

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}


def chave(fk):
    return (fk or "").replace(" ", "").replace("{{custom_values.", "").replace("}}", "")


# 1) custom values
cvs = {chave(v.get("fieldKey")): v for v in
       requests.get(B + "/locations/%s/customValues" % LOC, headers=H, timeout=30).json()["customValues"]}
for k, novo in VALORES.items():
    v = cvs[k]
    if (v.get("value") or "") == novo:
        continue
    print("custom value %-26s %r -> %r" % (k, v.get("value"), novo))
    if not DRY:
        r = requests.put(B + "/locations/%s/customValues/%s" % (LOC, v["id"]), headers=H,
                         json={"name": v["name"], "value": novo}, timeout=30)
        assert r.status_code == 200, r.text[:200]


def salvar(w, steps, triggers=None):
    atuais = requests.get(B + "/workflow/%s/trigger" % LOC, headers=H,
                          params={"workflowId": w["_id"]}, timeout=30).json()
    atuais = atuais if isinstance(atuais, list) else []
    body = {"name": w["name"], "version": w["version"], "status": w.get("status", "published"),
            "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
    body.update({k: w.get(k) for k in CONFIG})
    novos = triggers if triggers is not None else atuais
    if atuais or novos:
        body.update({"triggersChanged": True, "oldTriggers": atuais, "newTriggers": novos})
    r = requests.put(B + "/workflow/%s/%s" % (LOC, w["_id"]), headers=H, json=body, timeout=40)
    assert r.status_code in (200, 201), r.text[:300]


ws = [w for w in requests.get(B + "/workflow/" + LOC, headers=H, timeout=60).json()
      if w.get("type") != "directory"]

# 2) gatilho do formulário do site na 0.0
w0 = [w for w in ws if w["name"].startswith("0.0 ")][0]
tr0 = requests.get(B + "/workflow/%s/trigger" % LOC, headers=H, params={"workflowId": w0["_id"]}, timeout=30).json()
if not any(t.get("type") == "external_tracking" for t in tr0):
    # O POST só cria o gatilho; ele passa a valer quando entra na lista de gatilhos
    # do workflow (newTriggers no PUT). Sem isso responde 200 e não aparece.
    novo = {"status": "published", "workflowId": w0["_id"], "schedule_config": {},
            "type": "external_tracking", "masterType": "internal", "name": "Site - Estimate Request Form",
            "actions": [{"workflow_id": w0["_id"], "type": "add_to_workflow"}], "active": True,
            "triggersChanged": True, "location_id": LOC,
            "conditions": [
                {"operator": "is-any-of", "field": "eventType", "value": ["form"], "title": "Event",
                 "type": "multiselect", "id": "eventType"},
                {"operator": "==", "field": "formIdentifier", "value": FORM_SITE, "title": "External Form",
                 "type": "select", "id": "formIdentifier"}]}
    print("0.0: gatilho External Tracking Event -> %s" % FORM_SITE)
    if not DRY:
        tid = requests.post(B + "/workflow/%s/trigger" % LOC, headers=H, json=novo, timeout=30).json()["id"]
        steps0 = requests.get(w0["fileUrl"], timeout=40).json()["templates"]
        primeiro = [s for s in steps0 if not s.get("parentKey")][0]["id"]
        novo.update({"id": tid, "workflow_id": w0["_id"], "belongs_to": "workflow", "deleted": False,
                     "targetActionId": primeiro})
        requests.put(B + "/workflow/%s/trigger/%s" % (LOC, tid), headers=H, json=novo, timeout=30)
        salvar(w0, steps0, triggers=tr0 + [novo])

# 3) avisos internos para o dono
for w in ws:
    if w.get("status") != "published":
        continue
    steps = requests.get(w["fileUrl"], timeout=40).json()["templates"]
    n = 0
    for s in steps:
        if s["type"] != "internal_notification":
            continue
        for canal in ("sms", "email", "notification"):
            c = s["attributes"].get(canal)
            if isinstance(c, dict) and c.get("userType") == "all":
                c["userType"] = "user"
                c["selectedUser"] = DONO if canal == "notification" else [DONO]
                n += 1
    if n:
        print("%-60s %d aviso(s) All users -> Wesley" % (w["name"][:60], n))
        if not DRY:
            salvar(w, steps)
