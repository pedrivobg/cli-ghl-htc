# -*- coding: utf-8 -*-
"""Conserta a sequência de pedido de review nas subcontas dos clientes da Crew Systems.

O snapshot da Crew traz três problemas que valem para toda subconta criada a partir dele:

1. Os 4 SMS de pedido de review prometem doar uma refeição por avaliação. O Google
   proíbe oferecer incentivo em troca de review.
2. O trigger link do SMS leva para <site>/review, uma pesquisa que pergunta a nota
   primeiro e só manda 4-5 estrelas para o Google (1-3 vão para um formulário
   privado). Isso é filtrar avaliação, proibido pelo Google e pela FTC. O link passa a
   ir direto para o review_google_url.
3. company_name, company_owner_first_name e company_website_link vazios deixam o SMS
   com nome em branco. Só preenche o que está vazio; nunca sobrescreve.

Nada aqui dispara mensagem: a sequência só envia quando o contato recebe a tag
"customer" e o review_google_url está preenchido, e este script não mexe em nenhum dos
dois.

Uso: python tools/crew_reviews_fix.py [--dry] [--link]
  --link  também aponta o trigger link direto para o Google (desliga a pesquisa)
"""
import os, sys, json, time, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
# trocar o trigger link desliga a pesquisa de estrelas; é decisão do time, fica opcional
TROCAR_LINK = "--link" in sys.argv
B = "https://backend.leadconnectorhq.com"
LINK = "{{ custom_values.review_google_url }}"
WF_NOME = "Review Request Sent -> 1 Month Review Followup"

# valores preenchidos só quando o campo está vazio
CONTAS = {
    "OapfddiSt8scplnWw4oI": ("Best Painting Boston", {"company_name": "Best Painting Boston",
                             "company_owner_first_name": "Marcelo",
                             "company_website_link": "https://bestpaintingboston.com"}),
    "emq5z0PS5ddzVY2lGz74": ("WN Painting", {"company_name": "WN Painting & Remodeling",
                             "company_owner_first_name": "Wesley",
                             "company_website_link": "https://wnpaintingremodeling.com"}),
    "D5c3tvzXVueuFdF19ib6": ("SV Rental Car", {"company_name": "SV Rental Car",
                             "company_owner_first_name": "João",
                             "company_website_link": "https://svrentalcar.com"}),
    "8Y1C3Sjz7Ow1pzJ6ZJGp": ("ALI Construction", {"company_name": "ALI Construction",
                             "company_owner_first_name": "Carlos",
                             "company_website_link": "https://aliconstructionpro.com"}),
    "6KW7de8zxEIekNQUTAUO": ("VIX General Services", {"company_owner_first_name": "Kristyan"}),
    "LHJ8vLSVTQXFwtPVFcB6": ("MK Freitas", {}),
    "XkXTjVzjcoDmLOnKGLiH": ("Snapshot Las Vegas", {}),
}

L = "{{trigger_link.%s}}"
SMS = {
    "⭐SMS Review request #1": (
        "Hey {{contact.first_name}}, this is {{custom_values.company_owner_first_name}} from "
        "{{custom_values.company_name}}. Thanks for trusting us with your project! If you have a "
        "minute, a quick review about the work we did would mean a lot to a small local "
        "business like ours: %s"),
    "⭐SMS w REVIEW request #2": (
        "Hey {{contact.first_name}}! Following up in case my last message got buried. A quick "
        "review about how your project went helps other families in the area find us: %s "
        "Reply STOP if you'd rather not get these texts."),
    "⭐SMS review request #3": (
        "Quick reminder in case the week got busy. Here's the link to share how your project "
        "went: %s"),
    "⭐SMS review request #4": (
        "Hey {{contact.first_name}}! Last reminder, I promise. If you have a second to share how "
        "your project went, here's the link. Thank you either way! %s"),
}


def chave(fk):
    return (fk or "").replace(" ", "").replace("{{custom_values.", "").replace("}}", "")


tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}
relatorio = {}

for loc, (nome, valores) in CONTAS.items():
    feito = []
    print("\n=== %s" % nome)

    # 1) custom values vazios
    cvs = requests.get(B + "/locations/%s/customValues" % loc, headers=H, timeout=30).json()["customValues"]
    por = {chave(v.get("fieldKey")): v for v in cvs}
    for k, novo in valores.items():
        v = por.get(k)
        if not v:
            print("   %-26s nao existe na subconta" % k); continue
        if (v.get("value") or "").strip():
            print("   %-26s ja tinha: %s (mantido)" % (k, v["value"])); continue
        if not DRY:
            r = requests.put(B + "/locations/%s/customValues/%s" % (loc, v["id"]), headers=H,
                             json={"name": v["name"], "value": novo}, timeout=30)
            assert r.status_code == 200, r.text[:200]
        feito.append("%s = %s" % (k, novo))
        print("   %-26s -> %s" % (k, novo))

    # 2) trigger link direto para o Google
    links = requests.get(B + "/links/", headers=H, params={"locationId": loc}, timeout=30).json().get("links", [])
    tl = [x for x in links if x.get("name") == "5 star funnel TRIGGER LINK"]
    link_id = tl[0]["id"] if tl else None
    if tl and TROCAR_LINK and tl[0].get("redirectTo") != LINK:
        if not DRY:
            r = requests.put(B + "/links/%s" % link_id, headers=H,
                             json={"locationId": loc, "name": tl[0]["name"], "redirectTo": LINK}, timeout=30)
            assert r.status_code in (200, 201), r.text[:200]
        feito.append("trigger link -> review_google_url")
        print("   trigger link: %s -> %s" % (tl[0].get("redirectTo"), LINK))

    # 3) texto dos 4 SMS
    ws = requests.get(B + "/workflow/" + loc, headers=H, timeout=30).json()
    w = [x for x in ws if x.get("name") == WF_NOME]
    if not w or not link_id:
        print("   workflow ou trigger link nao encontrado; SMS nao alterado")
    else:
        w = w[0]
        steps = requests.get(w["fileUrl"], timeout=30).json()["templates"]
        mudou = 0
        for s in steps:
            if s.get("type") != "sms" or s.get("name") not in SMS:
                continue
            novo = SMS[s["name"]] % (L % link_id)
            a = s["attributes"]
            alvo = a["sms"] if isinstance(a.get("sms"), dict) and "body" in a["sms"] else a
            if alvo.get("body") != novo:
                alvo["body"] = novo; mudou += 1
        if mudou and not DRY:
            tr = requests.get(B + "/workflow/%s/trigger" % loc, headers=H,
                              params={"workflowId": w["_id"]}, timeout=30).json()
            tr = tr if isinstance(tr, list) else []
            body = {"name": w["name"], "version": w["version"], "status": w.get("status", "published"),
                    "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
            if tr:
                body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
            r = requests.put(B + "/workflow/%s/%s" % (loc, w["_id"]), headers=H, json=body, timeout=40)
            assert r.status_code in (200, 201), r.text[:300]
        if mudou:
            feito.append("%d SMS de review reescritos" % mudou)
        print("   SMS reescritos: %d" % mudou)
    relatorio[nome] = feito

print("\n### RESUMO%s" % (" (dry run)" if DRY else ""))
for n, f in relatorio.items():
    print("  %-22s %s" % (n, "; ".join(f) or "nada a mudar"))
