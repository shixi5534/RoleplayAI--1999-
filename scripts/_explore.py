import os, json
ROOT = "C:/Users/Lenovo/WorkBuddy/2026-07-27-16-45-03/roleplay-ai"
out = []
# corpus
corpus_path = os.path.join(ROOT, "data/knowledge/plot_corpus_wu_ming_zhe.json")
out.append("corpus exists: " + str(os.path.exists(corpus_path)))
if os.path.exists(corpus_path):
    corpus = json.loads(open(corpus_path, encoding="utf-8").read())
    out.append("corpus keys: " + str(list(corpus.keys())))
    chunks = corpus.get("chunks", [])
    out.append("num chunks: " + str(len(chunks)))
    # hashes of our batch
    batch_hashes = []
    for fn in ["batch_midhigh_06.txt", "batch_midhigh_07.txt"]:
        p = os.path.join(ROOT, "data/knowledge/_audit/backfill3", fn)
        for line in open(p, encoding="utf-8"):
            line = line.rstrip("\n")
            if "\t" in line and len(line.split("\t")[0]) == 16:
                batch_hashes.append(line.split("\t")[0])
    out.append("batch hashes count: " + str(len(batch_hashes)))
    corpus_hashes = {c["hash"] for c in chunks}
    missing = [h for h in batch_hashes if h not in corpus_hashes]
    out.append("missing in corpus: " + str(missing))
    # show sample chunk for one hash
    for c in chunks:
        if c["hash"] == "c72bcd320fbf4c4e":
            out.append("SAMPLE text (c72) repr len=" + str(len(c.get("text",""))))
            out.append(repr(c.get("text",""))[:500])
            break
# cache
cache_dir = os.path.join(ROOT, "data/knowledge/plot_cache/wu_ming_zhe")
out.append("cache exists: " + str(os.path.exists(cache_dir)))
if os.path.exists(cache_dir):
    files = os.listdir(cache_dir)
    out.append("cache file count: " + str(len(files)))
    # show a couple of our batch caches
    for h in batch_hashes[:3]:
        fp = os.path.join(cache_dir, h + ".json")
        if os.path.exists(fp):
            out.append(h + " cache: " + open(fp, encoding="utf-8").read()[:300])
        else:
            out.append(h + " cache: MISSING")
open(os.path.join(ROOT, "scripts/_explore_log.txt"), "w", encoding="utf-8").write("\n".join(out))
print("DONE")
