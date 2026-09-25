# -*- coding: utf-8 -*-
"""Agenda posts no Perfil da Empresa no Google de um cliente da Crew, pelo Social Planner.

Pré-requisito: o Google conectado no Social Planner da subconta (Marketing →
Social Planner → Google Business Profile). A foto vai por link público que devolve
image/jpeg direto (drive.usercontent.google.com/download?id=…&export=download): o
GHL guarda o link e o Google busca a imagem na hora de publicar, então a pasta do
Drive precisa continuar pública até o último post sair.

O texto de cada post só usa o que o site do cliente afirma. Nada de telefone no
texto: o Google recusa post com número.

Uso: python tools/crew_gbp_posts.py [--dry] [--so N]   (N = publicar só o post N)
"""
import sys, time, json, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
SO = int(sys.argv[sys.argv.index("--so") + 1]) if "--so" in sys.argv else None
B = "https://backend.leadconnectorhq.com"
LOC = "OapfddiSt8scplnWw4oI"                      # Best Painting Boston
ACC = "6ab6cd269a432b231baa7e4a_OapfddiSt8scplnWw4oI_3687126682747337827"
USER = "LMKviQZ675zvZr7TAtMf"
SITE = "https://bestpaintingboston.com"
UTM = "?utm_source=google&utm_medium=organic&utm_campaign=gbp_post"
IMG = "https://drive.usercontent.google.com/download?id=%s&export=download"

# quintas, 10h em Boston (EDT = UTC-4 até 2 de novembro)
POSTS = [
    ("2026-10-02T14:00:00.000Z", "1JzftPmi_cfBlLACPLHJEintrLsBQsdDk", "/services/masonry",
     "Front steps and walkways are the first thing anyone sees, and New England winters are hard on them. "
     "We rebuild steps and walkways, repoint brick and stone, and handle the painting in the same job. "
     "Now is the time to fix loose or cracked steps, before the freeze. Free written estimates."),
    ("2026-10-09T14:00:00.000Z", "1h1nsmDGQuF5E1nHTKZunwYrkaFhx8VMp", "/services/finish-flooring",
     "From bare subfloor to finished hardwood. Most flooring problems, like squeaks, gaps and lifting edges, "
     "start under the floor, so that is where we spend the time: the subfloor is prepped before anything "
     "goes down. Hardwood, LVP and tile. Free written estimates."),
    ("2026-10-16T14:00:00.000Z", "1v2DJZ1KuAKUG3vJwblkp9kjA__gzFwnA", "/services/commercial-painting",
     "Peeling stairs and railings, scraped back, primed and repainted. We paint stairwells, hallways and "
     "common areas in multi-family buildings with the building still in use, and turn rental units around "
     "between tenants on a schedule that fits the vacancy. Free written estimates."),
    ("2026-10-23T14:00:00.000Z", "1iHWrTyD-kt0z5nNKFCUi8KNQ_v2Zn8qk", "/services/exterior-painting",
     "The exterior painting season is closing. Exterior coatings need dry surfaces and the right "
     "temperatures, so around Boston the window runs from spring through fall. If your siding or trim is "
     "peeling, get it on the list now or first thing in spring. Free written estimates."),
]

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}


def agendados():
    j = requests.post(B + "/social-media-posting/%s/posts/list" % LOC, headers=H, timeout=40,
                      json={"type": "all", "skip": "0", "limit": "50", "includeUsers": "false",
                            "fromDate": "2026-09-01T00:00:00.000Z", "toDate": "2027-01-31T00:00:00.000Z"}).json()
    return j["results"]["posts"]


ja = {(p.get("summary") or "")[:60] for p in agendados() if not p.get("deleted")}
for i, (quando, foto, pagina, texto) in enumerate(POSTS, 1):
    if SO and i != SO:
        continue
    if texto[:60] in ja:
        print("post %d já existe; pulado" % i); continue
    body = {"accountIds": [ACC], "summary": texto, "status": "scheduled", "scheduleDate": quando,
            "type": "post", "userId": USER, "media": [{"url": IMG % foto, "type": "image/jpeg"}],
            "gmbPostDetails": {"gmbEventType": "STANDARD", "actionType": "learn_more",
                               "url": SITE + pagina + UTM}}
    if DRY:
        print("post %d (dry) %s  %d caracteres" % (i, quando, len(texto))); continue
    r = requests.post(B + "/social-media-posting/%s/posts" % LOC, headers=H, json=body, timeout=60)
    print("post %d %s -> %s %s" % (i, quando, r.status_code, "" if r.status_code in (200, 201) else r.text[:200]))

print("\n### NO SOCIAL PLANNER")
for p in sorted(agendados(), key=lambda p: p.get("displayDate") or ""):
    print("  %-10s %s  %s" % (p.get("status"), (p.get("displayDate") or "")[:16], (p.get("summary") or "")[:70]))
