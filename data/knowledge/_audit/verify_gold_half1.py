# -*- coding: utf-8 -*-
"""Self-check for l1_gold_half1.json against l1_arb_input_1.json + the annotation rules.

Checks (required):
  * chunk count == 16 and order identical to the input
  * every relation endpoint is a gold entity name of the same chunk
  * every entity name (or one of its aliases) occurs verbatim in that chunk text
  * relation phrase length 2..6 chinese chars
  * entity type inside the six controlled classes
Additional integrity checks: evidence verbatim + <=40 chars, desc <=30 chars,
no duplicate entity names, no alias re-listed as an entity, no duplicate
(src,dst) pair, meta numbers recomputed independently from the two annotations.
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(BASE, "l1_arb_input_1.json")
GOLD_PATH = os.path.join(BASE, "l1_gold_half1.json")
TYPES = {"角色", "组织", "地点", "物品", "概念", "事件"}

errors, warnings = [], []

raw = open(GOLD_PATH, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    errors.append("gold file starts with a BOM")
gold = json.loads(raw.decode("utf-8"))
data = json.loads(open(IN_PATH, "rb").read().decode("utf-8-sig"))
src = {c["chunk_id"]: c for c in data["chunks"]}

# ---- schema -----------------------------------------------------------------
if list(gold.keys()) != ["schema", "half", "meta", "chunks"]:
    errors.append("top-level keys: %r" % (list(gold.keys()),))
if gold.get("schema") != "audit.l1_gold/v1" or gold.get("half") != "1":
    errors.append("schema/half literal mismatch")
if list(gold["meta"].keys()) != ["n_chunks", "entity_agree", "entity_a_only", "entity_b_only",
                                 "entity_dropped", "relation_agree", "relation_added_single",
                                 "relation_dropped", "notes"]:
    errors.append("meta keys: %r" % (list(gold["meta"].keys()),))
if len(gold["meta"]["notes"]) > 5:
    errors.append("more than 5 notes")

# ---- chunk count & order ----------------------------------------------------
ids_in = [c["chunk_id"] for c in data["chunks"]]
ids_gold = [c["chunk_id"] for c in gold["chunks"]]
order_ok = ids_gold == ids_in
if len(ids_gold) != 16 or gold["meta"]["n_chunks"] != 16:
    errors.append("n_chunks != 16 (%d)" % len(ids_gold))
if not order_ok:
    errors.append("chunk order differs from input")

# ---- per chunk checks -------------------------------------------------------
for c in gold["chunks"]:
    cid = c["chunk_id"]
    text = src[cid]["text"]
    names = [e["name"] for e in c["entities"]]
    nset = set(names)
    if len(names) != len(nset):
        errors.append("%s: duplicate entity name" % cid)

    for e in c["entities"]:
        if e["type"] not in TYPES:
            errors.append("%s/%s: type %r not in six classes" % (cid, e["name"], e["type"]))
        if not isinstance(e["aliases"], list):
            errors.append("%s/%s: aliases not a list" % (cid, e["name"]))
        forms = [e["name"]] + list(e["aliases"])
        if not any(f in text for f in forms):
            errors.append("%s/%s: neither name nor alias is a substring of text" % (cid, e["name"]))
        if len(e["desc"]) > 30:
            warnings.append("%s/%s: desc %d chars > 30" % (cid, e["name"], len(e["desc"])))
        for other in c["entities"]:
            if other is not e and other["name"] in forms:
                errors.append("%s: entity %r also listed as an alias of %r"
                              % (cid, other["name"], e["name"]))

    seen = set()
    for r in c["relations"]:
        for side in ("src", "dst"):
            if r[side] not in nset:
                errors.append("%s: endpoint %r=%r is not a gold entity" % (cid, side, r[side]))
        if not (2 <= len(r["relation"]) <= 6):
            errors.append("%s/%s: relation length %d outside 2..6"
                          % (cid, r["relation"], len(r["relation"])))
        if r["evidence"] not in text:
            errors.append("%s: evidence not verbatim: %r" % (cid, r["evidence"]))
        if len(r["evidence"]) > 40:
            errors.append("%s: evidence %d chars > 40" % (cid, len(r["evidence"])))
        if not isinstance(r["confidence"], float) or not (0.0 <= r["confidence"] <= 1.0):
            errors.append("%s/%s: confidence %r out of range" % (cid, r["relation"], r["confidence"]))
        pair = (r["src"], r["dst"])
        if pair in seen:
            errors.append("%s: duplicate (src,dst) pair %r" % (cid, pair,))
        seen.add(pair)


# gold relations merged from two annotators who drew the *same* fact with
# reversed endpoints (A is B's superior  ==  B reports to A). Everything else is
# matched on the exact ordered (src, dst) pair.
MIRROR_MERGES = {
    ("mainline__103_故事一无所有:4.1.0", ("十四行诗", "维尔汀")),
}

# ---- independent recount of the agree / single-side split -------------------
ent_split = [0, 0, 0]      # agree, a_only, b_only
rel_split = [0, 0]         # agree, single
for c in gold["chunks"]:
    cid = c["chunk_id"]
    ann = {s: src[cid]["ann_" + s]["entities"] for s in "ab"}
    rel_ann = {s: src[cid]["ann_" + s]["relations"] for s in "ab"}
    # surface forms -> gold name, per annotator
    def match(e, entities):
        e_forms = set(e["aliases"]) | {e["name"]}
        for g in entities:                      # 1) exact name wins
            if e["name"] == g["name"]:
                return g["name"]
        for g in entities:                      # 2) any shared surface form
            if e_forms & (set(g["aliases"]) | {g["name"]}):
                return g["name"]
        return None

    mapping = {}
    for s in "ab":
        mp = {}
        for e in ann[s]:
            target = match(e, c["entities"])
            if target:
                for f in set(e["aliases"]) | {e["name"]}:
                    mp[f] = target
        mapping[s] = mp

    for g in c["entities"]:
        hit = {s for s in "ab" if g["name"] in set(mapping[s].values())}
        if len(hit) == 2:
            ent_split[0] += 1
        elif hit == {"a"}:
            ent_split[1] += 1
        elif hit == {"b"}:
            ent_split[2] += 1
        else:
            errors.append("%s/%s: gold entity proposed by neither annotator" % (cid, g["name"]))

    gold_pairs = {(r["src"], r["dst"]) for r in c["relations"]}
    mapped = {}
    for s in "ab":
        p = set()
        for r in rel_ann[s]:
            a = mapping[s].get(r["src"])
            b = mapping[s].get(r["dst"])
            if a and b:
                p.add((a, b))
        mapped[s] = p
    for pair in gold_pairs:
        n = sum(pair in mapped[s] for s in "ab")
        rev = (pair[1], pair[0])
        if n == 1 and (cid, pair) in MIRROR_MERGES and any(rev in mapped[s] for s in "ab"):
            n = 2              # one documented mirror merge of the same fact
        if n == 2:
            rel_split[0] += 1
        elif n == 1:
            rel_split[1] += 1
        else:
            errors.append("%s: gold relation %r unsupported by either annotation" % (cid, pair))

m = gold["meta"]
n_e = sum(len(c["entities"]) for c in gold["chunks"])
n_r = sum(len(c["relations"]) for c in gold["chunks"])
if m["entity_agree"] + m["entity_a_only"] + m["entity_b_only"] != n_e:
    errors.append("meta entity split %d+%d+%d != gold %d"
                  % (m["entity_agree"], m["entity_a_only"], m["entity_b_only"], n_e))
if m["relation_agree"] + m["relation_added_single"] != n_r:
    errors.append("meta relation split %d+%d != gold %d"
                  % (m["relation_agree"], m["relation_added_single"], n_r))
if tuple(ent_split) != (m["entity_agree"], m["entity_a_only"], m["entity_b_only"]):
    errors.append("recomputed entity split %s != meta %s"
                  % (tuple(ent_split), (m["entity_agree"], m["entity_a_only"], m["entity_b_only"])))
if tuple(rel_split) != (m["relation_agree"], m["relation_added_single"]):
    errors.append("recomputed relation split %s != meta %s"
                  % (tuple(rel_split), (m["relation_agree"], m["relation_added_single"])))

print("chunks=%d  order_matches_input=%s" % (len(ids_gold), order_ok))
print("gold entities=%d  gold relations=%d" % (n_e, n_r))
print("meta=%s" % json.dumps({k: v for k, v in m.items() if k != "notes"}, ensure_ascii=False))
print("recomputed entity split (agree/a_only/b_only)=%s" % (tuple(ent_split),))
print("recomputed relation split (agree/single)=%s" % (tuple(rel_split),))
print("relations per chunk=%s" % [len(c["relations"]) for c in gold["chunks"]])
print("warnings=%d" % len(warnings))
for w in warnings:
    print("  -", w)
print("ERRORS=%d" % len(errors))
for e in errors:
    print("  -", e)
sys.exit(1 if errors else 0)
