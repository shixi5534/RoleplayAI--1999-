# -*- coding: utf-8 -*-
"""最后 1 块（8d54aeb7，2.0 飞驰明日之城 p2）的补抽缓存。"""
import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "data/knowledge/graph_cache/wu_ming_zhe/8d54aeb70b0e2373.json"
d = {
    "entities": [
        {"name": "莱杰斯", "type": "角色", "aliases": ["Legers"]},
        {"name": "哈勒克先生", "type": "角色", "aliases": ["Mr.Halleck"]},
        {"name": "猎人角", "type": "地点", "aliases": ["Hunters Point"]},
        {"name": "警察", "type": "角色", "aliases": ["Cops"]},
        {"name": "街头朋克", "type": "角色", "aliases": ["street punks"]},
    ],
    "relations": [
        {"src": "莱杰斯", "dst": "猎人角", "relation": "关联", "confidence": 0.7},
        {"src": "莱杰斯", "dst": "警察", "relation": "对立", "confidence": 0.7},
        {"src": "街头朋克", "dst": "莱杰斯", "relation": "信任", "confidence": 0.7},
        {"src": "莱杰斯", "dst": "哈勒克先生", "relation": "遇见", "confidence": 0.6},
    ],
}
p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("written", p)
