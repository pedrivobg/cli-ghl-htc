# -*- coding: utf-8 -*-
"""Tira João Alves e Gabriel dos avisos de lead e de membro da HTC: tudo vai para o John.

Só mexe nos workflows da operação de leads e membros da HTC, listados em ALVOS. Em
cada aviso interno (SMS, e-mail ou notificação do app) e em cada divisão de
atribuição, os ids do João e dos dois Gabriel saem e o John entra se ainda não
estiver. Outros destinatários ficam como estão.

Fora de propósito, e por isso fora da lista: contratação (Aplicação para Contratação,
Reunião HTC Tech), consultoria/implementação, Auxílio Acidente, Empresa Solar e
CrewSystems.

Uso: python tools/htc_notificacoes_john.py [--dry]
"""
import os, sys, json, time, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager

DRY = "--dry" in sys.argv
B = "https://backend.leadconnectorhq.com"
LOC = os.environ["GHL_LOCATION_ID"]
JOHN = "wmlzZtJRtlFzilmaSojj"
SAEM = {"AoRfnKsAmrFW57EiadNQ": "João Alves", "wMgwPMadyjA8AK9yf6ud": "Gabriel HTCLUBE",
        "4zth6nbXm83uGB8McW2L": "Gabriel Oliveira"}
# usuário apagado da conta: o GHL recusa salvar workflow que ainda aponta para ele
INEXISTENTES = {"ocec1DGKusgkahOiPMN3"}
ALVOS = {
    "65b4805f-af61-4dd9-b0bc-2692cc7dd2e1": "HTC | Halo -> Transferencia Humana (John)",
    "01c3ea02-402c-4cee-b2cf-2e3e8e45363e": None,   # Reminders Agendamento IA Halo
    "3486c6fd-c86e-462c-8542-a628302c4ee8": "HTC | Chat do Site -> Notificar John",
    "af7ec407-ff3d-4005-aac6-17dc00f819a2": None,   # Halo -> Ticket Afiliado (enviado)
    "983fd918": None,                                # NPS - HTC
    "8cbcf34b": None,                                # HTC Onboarding PPL - Appointment Confirmation
    "e1148c12-a71a-4665-80b7-278816220ed1": None,   # SaaS New Reward
    "d428b6c8": None,                                # Assign Calling Leads
}
TEXTOS = [("Avisar Joao e Gabriel", "Avisar John"), ("Avisar Joao - chat do site", "Avisar John - chat do site"),
          ("HALO PASSOU UM LEAD PARA VOCES", "HALO PASSOU UM LEAD PARA VOCE")]

tm = TokenManager()
for _ in range(6):
    try:
        tok = tm.get_token(); break
    except SystemExit:
        time.sleep(4)
H = {"token-id": tok, "channel": "APP", "source": "WEB_USER", "Version": "2021-07-28",
     "Accept": "application/json", "Content-Type": "application/json"}

todos = requests.get(B + "/workflow/" + LOC, headers=H, timeout=60).json()


def trocar_lista(lst):
    novo = [u for u in lst if u not in SAEM and u not in INEXISTENTES]
    if JOHN not in novo:
        novo.insert(0, JOHN)
    return novo


for prefixo, novo_nome in ALVOS.items():
    ws = [w for w in todos if w["_id"].startswith(prefixo.split("-")[0])]
    if len(ws) != 1:
        print("?? %s não encontrado" % prefixo); continue
    w = ws[0]
    steps = requests.get(w["fileUrl"], timeout=40).json()["templates"]
    feito = []
    for s in steps:
        a = s.get("attributes") or {}
        if s["type"] == "internal_notification":
            for canal in ("sms", "email", "notification"):
                c = a.get(canal)
                if not isinstance(c, dict):
                    continue
                sel = c.get("selectedUser")
                if isinstance(sel, list) and any(u in SAEM for u in sel):
                    c["selectedUser"] = trocar_lista(sel)
                    feito.append("%s: %s" % (s["name"], [SAEM[u] for u in sel if u in SAEM]))
                elif isinstance(sel, str) and sel in SAEM:
                    c["selectedUser"] = JOHN
                    feito.append("%s: %s" % (s["name"], SAEM[sel]))
                for velho, novo in TEXTOS:
                    if velho in (c.get("body") or ""):
                        c["body"] = c["body"].replace(velho, novo)
        if s["type"] == "assign_user" and any(u in SAEM for u in a.get("user_list") or []):
            antes = a["user_list"]
            lista = trocar_lista(antes)
            a["user_list"] = lista
            a["traffic_weightage"] = {u: 1 for u in lista}
            a["traffic_index"] = [{"id": u, "indexes": [i + 1]} for i, u in enumerate(lista)]
            a["total_index"] = len(lista)
            feito.append("%s: %s" % (s["name"], [SAEM[u] for u in antes if u in SAEM]))
        for velho, novo in TEXTOS:
            if s.get("name") == velho:
                s["name"] = novo
    nome = novo_nome or w["name"]
    print("%-60s %s" % (w["name"][:60], "; ".join(feito) or "nada a mudar"))
    if (feito or nome != w["name"]) and not DRY:
        tr = requests.get(B + "/workflow/%s/trigger" % LOC, headers=H, params={"workflowId": w["_id"]}, timeout=30).json()
        tr = tr if isinstance(tr, list) else []
        body = {"name": nome, "version": w["version"], "status": w.get("status", "published"),
                "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
        if tr:
            body.update({"triggersChanged": True, "oldTriggers": tr, "newTriggers": tr})
        r = requests.put(B + "/workflow/%s/%s" % (LOC, w["_id"]), headers=H, json=body, timeout=40)
        print("   -> %s" % (r.status_code if r.status_code in (200, 201) else r.text[:300]))
