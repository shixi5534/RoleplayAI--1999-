# -*- coding: utf-8 -*-
"""R3 inspect: current graph state + corpus verbatim checks. READ-ONLY."""
import io, sys, json, os, re

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

GRAPH = os.path.join(ROOT, "data", "compendium_rag", "graph.json")
CORPUS = os.path.join(ROOT, "data", "compendium_rag", "corpus.json")


def load_graph():
    with open(GRAPH, encoding="utf-8") as f:
        return json.load(f)


def load_corpus_chunks():
    with open(CORPUS, encoding="utf-8") as f:
        corpus = json.load(f)
    # corpus.json structure: find chunks
    if isinstance(corpus, dict) and "chunks" in corpus:
        return corpus["chunks"]
    return corpus


def gtop(g):
    ents = g["entities"] if isinstance(g, dict) and "entities" in g else g
    if isinstance(ents, dict):
        return ents
    return {e["eid"]: e for e in ents}


def show(g, name):
    ents = gtop(g)
    if name not in ents:
        print(f"!! entity not in graph: {name!r}")
        return
    e = ents[name]
    out = {k: e.get(k) for k in ("eid", "name", "type", "desc", "aliases")}
    if isinstance(e.get("aliases"), list) and e["aliases"] and isinstance(e["aliases"][0], dict):
        out["aliases"] = [a.get("name") or a.get("alias") for a in e["aliases"]]
    print(f"== {name}: mentions={e.get('mentions')} n_chunks={len(e.get('chunk_ids') or [])} n_edges={len(e.get('edges') or [])}")
    print(json.dumps(out, ensure_ascii=False))
    # edge endpoints sample
    edges = e.get("edges") or []
    if edges:
        print("  edge keys:", list(edges[0].keys()) if isinstance(edges[0], dict) else type(edges[0]))


def search_names(g, pat):
    ents = gtop(g)
    rx = re.compile(pat)
    hits = [n for n in ents if rx.search(n)]
    print(f"names matching {pat!r}: {len(hits)}")
    for n in sorted(hits):
        e = ents[n]
        al = e.get("aliases") or []
        if al and isinstance(al[0], dict):
            al = [a.get("name") or a.get("alias") for a in al]
        print(f"  {n}  chunks={len(e.get('chunk_ids') or [])} mentions={e.get('mentions')} aliases={al}")


def grep_corpus(chunks, term, max_show=10, only_owner=None):
    hits = []
    for cid, c in chunks.items():
        t = c["text"] if isinstance(c, dict) and "text" in c else str(c)
        if term in t:
            hits.append(cid)
    print(f"corpus DF[{term!r}] = {len(hits)}")
    if only_owner:
        hits = [h for h in hits if h.startswith(only_owner)]
        print(f"  in owner prefix {only_owner!r}: {len(hits)}")
    for h in hits[:max_show]:
        t = chunks[h]["text"] if isinstance(chunks.get(h), dict) and "text" in chunks[h] else str(chunks[h])
        i = t.find(term)
        print(f"  {h}: ...{t[max(0,i-40):i+len(term)+40]}...")
    return hits


def main():
    g = load_graph()
    ents = gtop(g)
    print("graph entities:", len(ents))
    edges_top = g.get("edges") if isinstance(g, dict) else None
    if edges_top is not None:
        print("graph top-level edges:", len(edges_top))
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "show":
        for n in sys.argv[2:]:
            show(g, n)
    elif cmd == "search":
        search_names(g, sys.argv[2])
    elif cmd == "grep":
        chunks = load_corpus_chunks()
        print("chunks:", len(chunks))
        for term in sys.argv[2:]:
            grep_corpus(chunks, term)
    elif cmd == "chunk":
        chunks = load_corpus_chunks()
        for cid in sys.argv[2:]:
            c = chunks.get(cid)
            if c is None:
                print(f"!! chunk not found: {cid}")
            else:
                t = c["text"] if isinstance(c, dict) else str(c)
                print(f"--- {cid} ---")
                print(t)


if __name__ == "__main__":
    main()
