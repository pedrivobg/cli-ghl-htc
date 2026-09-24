# -*- coding: utf-8 -*-
"""Conserta os 5 SMS de indicação ("Refer a Friend + Return Customer + Review request").

No snapshot e em todos os clientes (iguais entre si) o link era montado na mão:
    {{custom_values.company_website_link}}/get-your-discount
Quando o site termina com barra sai "...com//get-your-discount", e em quem não tem a
página o link cai num 404. O snapshot já tem o campo discount_form_link para isso;
passa a ser usado. Também conserta o texto quebrado do SMS #5.

O resto do texto fica igual ao do snapshot. Primeiro o snapshot, depois os clientes.

Uso: python tools/crew_referral_fix.py [--dry]
"""
import sys, time, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
WF = "Refer a Friend + Return Customer + Review request -> 1 Year Followup"
CONTAS = {"XkXTjVzjcoDmLOnKGLiH": "Snapshot Las Vegas", "OapfddiSt8scplnWw4oI": "Best Painting",
          "emq5z0PS5ddzVY2lGz74": "WN Painting", "D5c3tvzXVueuFdF19ib6": "SV Rental",
          "6KW7de8zxEIekNQUTAUO": "VIX", "LHJ8vLSVTQXFwtPVFcB6": "MK Freitas",
          "8Y1C3Sjz7Ow1pzJ6ZJGp": "ALI"}
TROCAS = [
    ("{{custom_values.company_website_link}}/get-your-discount", "{{custom_values.discount_form_link}}"),
    ("I’m running an anniversary special  giving", "I’m running an anniversary special and giving"),
    ("It’s only for the first next 6 days", "It’s only for the next 6 days"),
]
# campos que a mensagem usa; preenchidos só se estiverem vazios (página conferida no site)
VALORES = {
    "6KW7de8zxEIekNQUTAUO": {"discount_form_link": ("Discount Form Link", "https://vixgeneralservices.com/get-your-discount"),
                             "review_survey_link": ("Review Survey Link", "https://vixgeneralservices.com/review")},
    "8Y1C3Sjz7Ow1pzJ6ZJGp": {"company_owner_first_name": ("Company Owner First Name", "Carlos")},
}

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
    w = [x for x in requests.get(B + "/workflow/" + loc, headers=H, timeout=30).json() if x.get("name") == WF]
    if not w:
        print("%-18s sem o workflow" % nome); continue
    w = w[0]
    steps = requests.get(w["fileUrl"], timeout=30).json()["templates"]
    mudou = 0
    for s in steps:
        if s.get("type") != "sms":
            continue
        c = corpo(s); b = c.get("body", "")
        for velho, novo in TROCAS:
            b = b.replace(velho, novo)
        if b != c.get("body"):
            c["body"] = b; mudou += 1
    if mudou and not DRY:
        tr = requests.get(B + "/workflow/%s/trigger" % loc, headers=H, params={"workflowId": w["_id"]}, timeout=30).json()
        tr = tr if isinstance(tr, list) else []
        body = {"name": w["name"], "version": w["version"], "status": w.get("status", "published"),
                "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
        if tr:
            body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
        r = requests.put(B + "/workflow/%s/%s" % (loc, w["_id"]), headers=H, json=body, timeout=40)
        assert r.status_code in (200, 201), r.text[:300]
    feitos = []
    cvs = {(v.get("fieldKey") or "").replace(" ", "").replace("{{custom_values.", "").replace("}}", ""): v
           for v in requests.get(B + "/locations/%s/customValues" % loc, headers=H, timeout=30).json()["customValues"]}
    for k, (rotulo, val) in VALORES.get(loc, {}).items():
        v = cvs.get(k)
        if v and (v.get("value") or "").strip():
            continue
        if not DRY:
            if v:
                r = requests.put(B + "/locations/%s/customValues/%s" % (loc, v["id"]), headers=H,
                                 json={"name": v["name"], "value": val}, timeout=30)
            else:
                r = requests.post(B + "/locations/%s/customValues" % loc, headers=H,
                                  json={"name": rotulo, "value": val}, timeout=30)
            assert r.status_code in (200, 201), r.text[:200]
        feitos.append("%s=%s" % (k, val))
    print("%-18s SMS alterados: %d%s%s" % (nome, mudou, ("  | " + ", ".join(feitos)) if feitos else "", " (dry)" if DRY else ""))
