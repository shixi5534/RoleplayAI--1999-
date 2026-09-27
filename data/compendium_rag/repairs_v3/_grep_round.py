# -*- coding: utf-8 -*-
"""R3 grep round: verbatim DF + owner-chunk containment for all candidate aliases.
READ-ONLY. Output to repairs_v3/_grep_results.txt"""
import io, sys, json, os, re
from collections import Counter

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

G = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "graph.json"), encoding="utf-8"))
C = json.load(open(os.path.join(ROOT, "data", "compendium_rag", "corpus.json"), encoding="utf-8"))

# normalize graph entities
gents = G["entities"] if isinstance(G.get("entities"), dict) else {e["eid"]: e for e in G["entities"]}

chunks = C["chunks"] if isinstance(C, dict) and "chunks" in C else C
print("corpus top keys:", list(C.keys())[:10] if isinstance(C, dict) else "list")
print("n chunks:", len(chunks))
sample = next(iter(chunks.items()))
print("chunk sample key:", sample[0], "type:", type(sample[1]))
if isinstance(sample[1], dict):
    print("chunk fields:", list(sample[1].keys()))
    print("text head:", sample[1].get("text", "")[:120])
elif isinstance(sample[1], str):
    print("str head:", sample[1][:120])
