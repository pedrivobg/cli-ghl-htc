# -*- coding: utf-8 -*-
"""Liga a Halo nas DMs do Instagram.

Diagnostico: o workflow 'HTC | Atendimento IA Halo' comeca com find_opportunity
no pipeline Afiliado e so segue se a oportunidade estiver em 'Opt In Leads' ou
'Afiliado Lead(1st step)'. As DMs do Instagram caem no estagio 'Instagram Leads'
(criado pelo workflow 'IG DM -> Add Pipeline'), que nao estava na lista -> a
Halo nunca era ligada. Alem disso os dois workflows disparam no mesmo evento,
entao o find_opportunity podia rodar antes da oportunidade existir.

Correcao: (1) aceitar o estagio Instagram Leads; (2) o proprio workflow do IG
inscreve o contato no atendimento da Halo depois de criar a oportunidade,
garantindo a ordem.
"""
import os, json, time, uuid, requests
from cli_anything.gohighlevel.utils.ghl_internal_client import TokenManager, InternalGHLClient

HTC = os.environ["GHL_LOCATION_ID"]
WF_HALO = "0076f038-9f10-4b14-9a26-9f3badacc597"
WF_IG = "b02d1c09-508a-4309-9320-8119683d13e3"
IF_NODE = "7fc09b43-d410-4b3b-b8f1-7563d3e1abf5"
STAGE_IG = "422a0d12-f6c9-4b09-8e04-924222a4ca55"
A = "/tmp/claude-0/-home-user-cli-ghl-htc/e5755955-47c9-5ed4-987a-fd68342e9ea2/scratchpad/"

tm = TokenManager()
for _ in range(6):
    try:
        tm.get_token(); break
    except SystemExit:
        time.sleep(4)
c = InternalGHLClient(tm, HTC)
todos = c.get("/workflow/" + HTC)


def carregar(wid):
    w = [x for x in c.get("/workflow/" + HTC) if x.get("_id") == wid][0]
    return w, requests.get(w["fileUrl"], timeout=40).json()["templates"]


def publicar(w, steps, wid):
    trigs = c.get("/workflow/%s/trigger?workflowId=%s" % (HTC, wid))
    trigs = trigs if isinstance(trigs, list) else []
    body = {"name": w.get("name"), "version": w.get("version"), "status": "published",
            "meta": w.get("meta") or {}, "workflowData": {"templates": steps}}
    if trigs:
        body["triggersChanged"] = True
        body["oldTriggers"] = trigs
        body["newTriggers"] = trigs
    r = c.put("/workflow/%s/%s" % (HTC, wid), body)
    ok = r and not r.get("_error")
    print("PUT %-40s -> %s" % (w.get("name")[:40], "OK" if ok else json.dumps(r, ensure_ascii=False)[:300]))
    return ok


# ---------- 1) aceitar o estagio Instagram Leads ----------
wh, sh = carregar(WF_HALO)
json.dump(sh, open(A + "bkp_halo_steps.json", "w"), ensure_ascii=False, indent=1)
node = [n for n in sh if n["id"] == IF_NODE][0]
seg = node["attributes"]["branches"][0]["segments"][0]
modelo = seg["conditions"][0]
ja = [x.get("conditionValue") for x in seg["conditions"]]
print("estagios aceitos antes:", ja)
if STAGE_IG not in ja:
    nova = json.loads(json.dumps(modelo))
    nova["conditionValue"] = STAGE_IG
    nova["__conditionId"] = str(uuid.uuid4())
    seg["conditions"].append(nova)
    print("estagios aceitos depois:", [x.get("conditionValue") for x in seg["conditions"]])
    publicar(wh, sh, WF_HALO)
else:
    print("estagio ja estava na lista; nada a fazer")

# ---------- 2) o workflow do IG inscreve na Halo ----------
wi, si = carregar(WF_IG)
json.dump(si, open(A + "bkp_igdm_steps.json", "w"), ensure_ascii=False, indent=1)
tem = any((n.get("attributes") or {}).get("workflow_id") == WF_HALO for n in si)
if tem:
    print("workflow do IG ja inscreve na Halo; nada a fazer")
else:
    ultimo = si[-1]
    novo_id = str(uuid.uuid4())
    ultimo["next"] = novo_id
    si.append({"id": novo_id, "order": len(si),
               "name": "Inscrever no Atendimento IA Halo",
               "type": "add_to_workflow",
               "parentKey": ultimo["id"],
               "attributes": {"input_trigger_params": False,
                              "type": "add_to_workflow",
                              "workflow_id": WF_HALO}})
    publicar(wi, si, WF_IG)

# ---------- verificacao ----------
print("\n### VERIFICACAO")
time.sleep(3)
_, sh2 = carregar(WF_HALO)
n2 = [n for n in sh2 if n["id"] == IF_NODE][0]
vals = [x.get("conditionValue") for x in n2["attributes"]["branches"][0]["segments"][0]["conditions"]]
print("Halo aceita os estagios:", vals, "->", "INCLUI Instagram Leads" if STAGE_IG in vals else "FALTA")
_, si2 = carregar(WF_IG)
for n in si2:
    print("  IG DM: [%s] %s -> %s" % (n.get("type"), n.get("name"), (n.get("attributes") or {}).get("workflow_id", "")))
