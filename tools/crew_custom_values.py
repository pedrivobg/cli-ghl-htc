# -*- coding: utf-8 -*-
"""Alinha os Custom Values das subcontas dos clientes com o Snapshot Crew [LAS VEGAS].

Regra do time: tudo que está preenchido no snapshot tem que estar preenchido em cada
cliente. Este script só CRIA campos que não existem ou PREENCHE campos vazios, com
valores conferidos (sites abertos, rotas presentes no bundle do site, dados do
questionário). Nunca sobrescreve um valor que alguém já colocou.

Também limpa o review_google_url do snapshot: ele guardava o link de review da Best
Painting, e todo cliente novo criado a partir dele herdaria esse link.

Uso: python tools/crew_custom_values.py [--dry]
"""
import sys, time, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
SNAPSHOT = "XkXTjVzjcoDmLOnKGLiH"

# chave -> nome exibido no snapshot (o nome gera a chave)
NOMES = {"discount_form_link": "Discount Form Link", "quote_form_link": "Quote Form Link",
         "review_survey_link": "Review Survey Link", "legal_business_name": "Legal Business Name",
         "business_email": "Business Email", "business_phone": "Business Phone",
         "company_website_link": "Company Website Link"}

VALORES = {
    "OapfddiSt8scplnWw4oI": ("Best Painting", {
        "discount_form_link": "https://bestpaintingboston.com/get-your-discount",
        "quote_form_link": "https://bestpaintingboston.com/contact",
        "review_survey_link": "https://bestpaintingboston.com/review"}),
    "emq5z0PS5ddzVY2lGz74": ("WN Painting", {
        "discount_form_link": "https://wnpaintingremodeling.com/get-your-discount",
        "quote_form_link": "https://wnpaintingremodeling.com/contact",
        "review_survey_link": "https://wnpaintingremodeling.com/review"}),
    "6KW7de8zxEIekNQUTAUO": ("VIX", {
        "quote_form_link": "https://vixgeneralservices.com/contact"}),
    "LHJ8vLSVTQXFwtPVFcB6": ("MK Freitas", {
        "quote_form_link": "https://go.mkfreitasremodeling.com/contact",
        "review_survey_link": "https://go.mkfreitasremodeling.com/review"}),
    "8Y1C3Sjz7Ow1pzJ6ZJGp": ("ALI Construction", {
        "legal_business_name": "ALI CONSTRUCTION LLC",
        "business_email": "aliconstruction_@outlook.com",
        "business_phone": "+17326939101",
        "company_website_link": "https://aliconstructionpro.com",
        "quote_form_link": "https://aliconstructionpro.com/contact"}),
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


def lista(loc):
    c = requests.get(B + "/locations/%s/customValues" % loc, headers=H, timeout=30).json()["customValues"]
    return {chave(v.get("fieldKey")): v for v in c}


for loc, (nome, vals) in VALORES.items():
    atual = lista(loc)
    print("\n=== %s" % nome)
    for k, val in vals.items():
        v = atual.get(k)
        if v and (v.get("value") or "").strip():
            print("   %-22s ja tinha: %s" % (k, v["value"])); continue
        if not DRY:
            if v:
                r = requests.put(B + "/locations/%s/customValues/%s" % (loc, v["id"]), headers=H,
                                 json={"name": v["name"], "value": val}, timeout=30)
            else:
                r = requests.post(B + "/locations/%s/customValues" % loc, headers=H,
                                  json={"name": NOMES[k], "value": val}, timeout=30)
            assert r.status_code in (200, 201), r.text[:200]
        print("   %-22s %s -> %s" % (k, "preenchido" if v else "criado", val))
    if not DRY:
        # a leitura logo depois da escrita às vezes ainda não enxerga o campo novo
        for _ in range(5):
            depois = lista(loc)
            faltando = [k for k in vals if not (depois.get(k) or {}).get("value", "").strip()]
            if not faltando:
                break
            time.sleep(3)
        assert not faltando, "falhou: %s em %s" % (faltando, nome)

# snapshot: tira o link de review da Best Painting
s = lista(SNAPSHOT).get("review_google_url")
if s and "CS6Ar4o0mi_yEBM" in (s.get("value") or ""):
    if not DRY:
        r = requests.put(B + "/locations/%s/customValues/%s" % (SNAPSHOT, s["id"]), headers=H,
                         json={"name": s["name"], "value": ""}, timeout=30)
        print("\nsnapshot review_google_url limpo -> %s" % r.status_code)
    else:
        print("\nsnapshot review_google_url seria limpo (hoje: %s)" % s["value"])
