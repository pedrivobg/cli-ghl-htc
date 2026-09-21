#!/usr/bin/env python
"""Testa a IA Halo simulando uma conversa real pela API do GoHighLevel.

LIMITACAO CONFIRMADA POR EXPERIMENTO (21/09/2026): o gatilho "Customer Replied"
NAO dispara com mensagem inserida por esta API. Verificado com um workflow
descartavel que so aplicava uma tag: a mensagem entra na conversa, aparece como
inbound no canal certo, e o gatilho nao roda. Ou seja, este script monta o
cenario e registra a mensagem, mas nao consegue acordar a IA.

Para testar a Halo de verdade, mande a mensagem pelo canal real (WhatsApp,
Instagram ou o chat do site). Este script continua util para preparar o contato
de teste e para conferir o que chega na conversa.

Cria um contato descartável, coloca ele no estagio que liga a Halo, manda uma
mensagem como se fosse o lead e fica ouvindo a resposta. No fim apaga tudo.

    python tools/test_halo.py "sua mensagem aqui"
    python tools/test_halo.py --canal Live_Chat "oi, quanto custa?"
    python tools/test_halo.py --manter "..."     # nao apaga o contato no fim

Le GHL_API_KEY e GHL_LOCATION_ID do ambiente (o wrapper ./ghl carrega o .env).
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import requests

BASE = "https://services.leadconnectorhq.com"
PIPELINE = "d2UrqygBbHikBX4gKH3F"          # Afiliado Pipeline
STAGE_OPT_IN = "d2891e74-0fb0-41ee-a583-af7351de8c21"
AI_FIELD = "btqf4ZzVvUEZnqKMhE2z"          # AI Activation

# Canais aceitos pelo endpoint de mensagem recebida, com o codigo numerico que
# o GHL usa no filtro "Reply channel" dos gatilhos.
CANAIS = {"WhatsApp": 19, "IG": 18, "FB": 11, "SMS": 2, "Live_Chat": 29}


def headers(version: str = "2021-07-28") -> dict:
    key = os.environ.get("GHL_API_KEY", "").strip()
    if not key:
        sys.exit("GHL_API_KEY nao esta no ambiente. Rode pelo ./ghl ou carregue o .env.")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
            "Accept": "application/json", "Version": version}


def location() -> str:
    loc = os.environ.get("GHL_LOCATION_ID", "").strip()
    if not loc:
        sys.exit("GHL_LOCATION_ID nao esta no ambiente.")
    return loc


def janela_aberta() -> tuple[bool, str]:
    """A janela do workflow foi aberta para 24h em 21/09/2026, entao sempre passa."""
    import datetime
    agora = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
    return True, agora.strftime("%d/%m %H:%M (%a)")


def criar_contato(loc: str) -> tuple[str, str]:
    marca = str(int(time.time()))[-6:]
    r = requests.post(f"{BASE}/contacts/", headers=headers(), timeout=30, json={
        "locationId": loc,
        "firstName": "ZZ TESTE",
        "lastName": f"Halo {marca}",
        "email": f"zz.teste.halo.{marca}@example.com",
        "phone": f"+5511999{marca}",
        "tags": ["zz-teste-claude"],
        "source": "teste-halo",
    })
    r.raise_for_status()
    cid = r.json()["contact"]["id"]

    r = requests.post(f"{BASE}/conversations/", headers=headers("2021-04-15"), timeout=30,
                      json={"locationId": loc, "contactId": cid})
    r.raise_for_status()
    return cid, r.json()["conversation"]["id"]


def por_no_funil(loc: str, cid: str) -> None:
    """A Halo so atende quem tem oportunidade no estagio de entrada do funil."""
    requests.post(f"{BASE}/opportunities/", headers=headers(), timeout=30, json={
        "locationId": loc, "contactId": cid, "pipelineId": PIPELINE,
        "pipelineStageId": STAGE_OPT_IN, "name": "ZZ TESTE Halo", "status": "open",
    })


def mandar(conv: str, canal: str, texto: str) -> None:
    r = requests.post(f"{BASE}/conversations/messages/inbound", headers=headers("2021-04-15"),
                      timeout=30, json={"type": canal, "conversationId": conv,
                                        "message": texto, "direction": "inbound"})
    r.raise_for_status()


def ouvir(conv: str, segundos: int) -> list[str]:
    """Poll na conversa ate aparecer resposta de saida da IA."""
    alvo = set(CANAIS.values())
    esperou = 0
    while esperou < segundos:
        time.sleep(10)
        esperou += 10
        r = requests.get(f"{BASE}/conversations/{conv}/messages",
                         headers=headers("2021-04-15"), params={"limit": 40}, timeout=25)
        msgs = r.json().get("messages", {}).get("messages", [])
        saida = [m.get("body") or "" for m in msgs
                 if m.get("direction") == "outbound" and m.get("type") in alvo]
        if saida:
            return saida
        print(f"   ... {esperou}s sem resposta", flush=True)
    return []


def limpar(loc: str, cid: str) -> None:
    o = requests.get(f"{BASE}/opportunities/search", headers=headers(), timeout=30,
                     params={"location_id": loc, "contact_id": cid}).json()
    for op in o.get("opportunities", []):
        requests.delete(f"{BASE}/opportunities/{op['id']}", headers=headers(), timeout=30)
    requests.delete(f"{BASE}/contacts/{cid}", headers=headers(), timeout=30)


def main() -> None:
    ap = argparse.ArgumentParser(description="Simula uma conversa com a IA Halo.")
    ap.add_argument("mensagem", help="o que o lead diz")
    ap.add_argument("--canal", default="WhatsApp", choices=sorted(CANAIS),
                    help="canal de entrada (padrao: WhatsApp)")
    ap.add_argument("--esperar", type=int, default=120, help="segundos de espera (padrao: 120)")
    ap.add_argument("--manter", action="store_true", help="nao apagar o contato no fim")
    args = ap.parse_args()

    loc = location()
    aberta, quando = janela_aberta()
    print(f"agora: {quando}")
    print("AVISO: o gatilho do GoHighLevel nao dispara com mensagem vinda desta API.")
    print("       O cenario e montado e a mensagem entra na conversa, mas a IA nao")
    print("       acorda. Para testar de verdade, mande pelo canal real.\n")

    cid, conv = criar_contato(loc)
    print(f"contato de teste: {cid}")
    por_no_funil(loc, cid)
    time.sleep(3)

    print(f"enviando por {args.canal}: {args.mensagem!r}")
    mandar(conv, args.canal, args.mensagem)

    respostas = ouvir(conv, args.esperar)
    print()
    if respostas:
        print("=== A HALO RESPONDEU ===")
        for r in respostas:
            print(f"   {r}")
    else:
        print("=== SEM RESPOSTA ===")
        print("   Esperado: o gatilho nao dispara por API. Veja a nota no topo do arquivo.")

    if args.manter:
        print(f"\ncontato mantido: {cid}")
    else:
        limpar(loc, cid)
        print("\ncontato de teste removido.")


if __name__ == "__main__":
    main()
