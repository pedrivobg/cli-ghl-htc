# -*- coding: utf-8 -*-
"""Halo: prompt abaixo de 2.000 palavras e todo atendimento humano indo para o John.

O GoHighLevel não salva prompt de agente acima de 2.000 palavras, e o da Halo tinha
2.463. O texto novo (tools/halo_prompt/) mantém todas as regras e o passo a passo de
afiliado, só sem repetição.

João Alves e Gabriel deixam de receber lead: tudo passa para o John Nogueira.
- as 3 transferências (Human Handover) atribuem ao John
- a mensagem de despedida citava o Léo, que saiu da conta
- o calendário "Halo - Call de Ativacao GHL" fica só com o John
- a Halo ganha a ação de agendamento nesse calendário; o prompt mandava agendar, mas
  a ação não existia, então nenhuma call foi marcada por ela

Uso: python tools/htc_halo_john.py [--dry]
"""
import os, sys, json, time, requests

DRY = "--dry" in sys.argv
S = "https://services.leadconnectorhq.com"
LOC = os.environ["GHL_LOCATION_ID"]
BOT = "qQ36rFQsb7MncdXLNCFZ"
JOHN = "wmlzZtJRtlFzilmaSojj"
CAL = "f0K54GMXBWkoqYqx219X"
AQUI = os.path.dirname(os.path.abspath(__file__))
H = {"Authorization": "Bearer " + os.environ["GHL_API_KEY"].strip(), "Version": "2021-04-15",
     "Accept": "application/json", "Content-Type": "application/json"}


def api(m, p, body=None, **kw):
    r = requests.request(m, S + p, headers=H, json=body, timeout=60, **kw)
    try:
        j = r.json()
    except Exception:
        j = {"_text": r.text[:300]}
    if r.status_code >= 300:
        print("   ERRO %s %s -> %s %s" % (m, p, r.status_code, json.dumps(j, ensure_ascii=False)[:400]))
    return r.status_code, j


def ler(nome):
    return open(os.path.join(AQUI, "halo_prompt", nome), encoding="utf-8").read().strip()


# ---------- 1) prompt ----------
p, g, i = ler("personality.txt"), ler("goal.txt"), ler("instructions.txt")
full = "## Personality\n\n" + p + "\n\n## Goal\n\n" + g + "\n\n## Instructions\n\n" + i
print("prompt novo: %d palavras" % len(full.split()))
assert len(full.split()) < 2000
if not DRY:
    # o servidor grava só o fullPrompt quando ele vai junto dos três campos
    api("PUT", "/conversation-ai/agents/%s" % BOT, {"personality": p, "goal": g, "instructions": i})
    api("PUT", "/conversation-ai/agents/%s" % BOT, {"fullPrompt": full})

# ---------- 2) ações ----------
_, ag = api("GET", "/conversation-ai/agents/%s" % BOT, params={"locationId": LOC})
acoes = {}
for a in ag["actions"]:
    _, d = api("GET", "/conversation-ai/agents/%s/actions/%s" % (BOT, a["id"]))
    acoes[a["id"]] = d["data"]


def salvar(a):
    if DRY:
        return
    api("PUT", "/conversation-ai/agents/%s/actions/%s?locationId=%s" % (BOT, a["id"], LOC),
        {"name": a["name"], "type": a["type"], "details": a["details"]})


for a in acoes.values():
    d, mudou = a["details"], False
    if a["type"] == "humanHandOver" and d.get("assignToUserId") != JOHN:
        d["assignToUserId"] = JOHN; mudou = True
    if a["type"] == "stopBot" and "Léo" in (d.get("finalMessage") or ""):
        d["finalMessage"] = d["finalMessage"].replace("O Léo já foi notificado", "O John já foi avisado")
        d["stopBotExamples"] = [x.replace("Aguardar o Léo", "Aguardar o John") for x in d.get("stopBotExamples") or []]
        mudou = True
    if a["type"] == "updateContactField" and "Joao ou o Gabriel" in (d.get("description") or ""):
        d["description"] = d["description"].replace("para o Joao ou o Gabriel", "para o John")
        mudou = True
    if mudou:
        print("ação: %s" % a["name"])
        salvar(a)

if not any(a["type"] == "appointmentBooking" for a in acoes.values()):
    print("ação nova: agendamento no calendário da Halo")
    if not DRY:
        api("POST", "/conversation-ai/agents/%s/actions?locationId=%s" % (BOT, LOC),
            {"name": "Agendar call com o John", "type": "appointmentBooking",
             "details": {"calendarId": CAL, "onlySendLink": False, "triggerWorkflow": False,
                         "sleepAfterBooking": False, "transferBot": False,
                         "rescheduleEnabled": True, "cancelEnabled": True}})

# ---------- 3) calendário ----------
_, c = api("GET", "/calendars/%s" % CAL)
c = c["calendar"]
if [m["userId"] for m in c["teamMembers"]] != [JOHN]:
    modelo = c["teamMembers"][0]
    novo = dict(modelo, userId=JOHN, isPrimary=True, priority=0.5)
    print("calendário: %s -> John" % [m["userId"] for m in c["teamMembers"]])
    if not DRY:
        api("PUT", "/calendars/%s" % CAL, {"teamMembers": [novo]})
