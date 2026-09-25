#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 backfill3 两个批次（batch_midhigh_02 / batch_midhigh_03）共 50 块的未抽取剧情。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

# 无剧情信息块（纯对话/科学讲解，无命名实体）
NOOP = {
    "ab4e0230c02d3c4a": {"entities": [], "relations": []},  # 纯审讯对话，无专有名词
    "382e7b358d50a033": {"entities": [], "relations": []},  # 仅 Sir/madam 泛称，无命名实体
    "04cdf08b7ba55515": {"entities": [], "relations": []},  # 纯天文数据，无剧情命名实体
}

RESULTS = {
    # ===== batch_midhigh_02 =====
    "110e4716e7567e0f": {
        "entities": [
            {"name": "International Astronomical Union", "type": "组织", "aliases": ["IAU"]},
        ],
        "relations": [],
    },
    "ca0b730003d60c3e": {
        "entities": [
            {"name": "Arathlattus", "type": "角色", "aliases": []},
            {"name": "Covertina", "type": "角色", "aliases": []},
            {"name": "Boratio", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Covertina", "dst": "Boratio", "relation": "战胜", "confidence": 0.8},
        ],
    },
    "76f345e5ae3140a7": {
        "entities": [
            {"name": "Tim", "type": "角色", "aliases": []},
            {"name": "Mr.Slouch Hat", "type": "角色", "aliases": ["Slouch Hat"]},
            {"name": "Thursday", "type": "时间", "aliases": []},
        ],
        "relations": [],
    },
    "15c28fcd6fafb4cb": {
        "entities": [
            {"name": "祥瑞", "type": "角色", "aliases": ["Xiangrui"]},
            {"name": "Xiaorui", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Xiaorui", "dst": "祥瑞", "relation": "虚构为母亲", "confidence": 0.75},
        ],
    },
    "6ffc7e060c7f2b1b": {
        "entities": [
            {"name": "Arkenum", "type": "地点", "aliases": []},
            {"name": "Big Shots", "type": "组织", "aliases": []},
            {"name": "Comrade Evgeny", "type": "角色", "aliases": ["Evgeny"]},
        ],
        "relations": [],
    },
    "c85b33bf28322cc5": {
        "entities": [
            {"name": "carbuncle", "type": "物品", "aliases": []},
            {"name": "the visitor guide", "type": "物品", "aliases": ["visitor guide"]},
            {"name": "the ward", "type": "地点", "aliases": []},
        ],
        "relations": [],
    },
    "dcb2f2c89a4f2718": {
        "entities": [
            {"name": "Uluru Fair", "type": "事件", "aliases": []},
            {"name": "London", "type": "地点", "aliases": []},
            {"name": "the Thames", "type": "地点", "aliases": []},
            {"name": "arcanist", "type": "概念", "aliases": []},
            {"name": "fog", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "London", "dst": "fog", "relation": "出现", "confidence": 0.8},
            {"src": "Uluru Fair", "dst": "fog", "relation": "受雾影响", "confidence": 0.7},
        ],
    },
    "9e7ce7f514cf984f": {
        "entities": [
            {"name": "Mr.Fogg", "type": "角色", "aliases": ["Fogg"]},
            {"name": "Ms.Tooth Fairy", "type": "角色", "aliases": ["Tooth Fairy"]},
            {"name": "Arthur", "type": "角色", "aliases": []},
            {"name": "black fog", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "Arthur", "dst": "Ms.Tooth Fairy", "relation": "请求帮助", "confidence": 0.8},
        ],
    },
    "f1d35ec6f629264d": {
        "entities": [
            {"name": "Freddy", "type": "角色", "aliases": []},
            {"name": "the machine", "type": "物品", "aliases": []},
            {"name": "the pipe", "type": "物品", "aliases": []},
            {"name": "the mechanical lung", "type": "物品", "aliases": []},
            {"name": "black blood", "type": "现象", "aliases": []},
        ],
        "relations": [
            {"src": "the machine", "dst": "the mechanical lung", "relation": "包含", "confidence": 0.85},
            {"src": "the machine", "dst": "the pipe", "relation": "包含", "confidence": 0.7},
            {"src": "the machine", "dst": "black blood", "relation": "吐出", "confidence": 0.8},
        ],
    },
    "d6b1fc32944db725": {
        "entities": [
            {"name": "Fusebox", "type": "角色", "aliases": []},
            {"name": "the central tower", "type": "地点", "aliases": []},
            {"name": "the library", "type": "地点", "aliases": []},
            {"name": "Isabella", "type": "角色", "aliases": []},
            {"name": "the supervisor", "type": "角色", "aliases": ["the dorm supervisor"]},
            {"name": "Double Beta 3", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "Isabella", "dst": "the supervisor", "relation": "可能冲突", "confidence": 0.7},
            {"src": "Double Beta 3", "dst": "the supervisor", "relation": "献给", "confidence": 0.7},
        ],
    },
    "9b613d4740cd58dc": {
        "entities": [
            {"name": "the inspector", "type": "角色", "aliases": []},
            {"name": "Seed", "type": "角色", "aliases": []},
            {"name": "Ward", "type": "角色", "aliases": []},
            {"name": "the cast", "type": "组织", "aliases": []},
            {"name": "the agreement", "type": "物品", "aliases": []},
        ],
        "relations": [],
    },
    "7b1bdd1d0ed78842": {
        "entities": [
            {"name": "a minotaur", "type": "概念", "aliases": []},
            {"name": "the Ford Circle", "type": "概念", "aliases": []},
            {"name": "the Monster Group", "type": "概念", "aliases": []},
            {"name": "Hilbert's Infinite Grand Hotel", "type": "概念", "aliases": []},
        ],
        "relations": [],
    },
    "2421b255c518eaca": {
        "entities": [
            {"name": "Mama", "type": "角色", "aliases": []},
            {"name": "the Transcendental Realm", "type": "地点", "aliases": []},
            {"name": "the last visitor", "type": "角色", "aliases": []},
        ],
        "relations": [],
    },
    "244b613a43e4cf9c": {
        "entities": [
            {"name": "Voldifauro", "type": "角色", "aliases": []},
            {"name": "Le Désir", "type": "概念", "aliases": []},
            {"name": "The circle of everything", "type": "概念", "aliases": []},
            {"name": "The tip of the great tail", "type": "概念", "aliases": []},
            {"name": "the serpent's tail", "type": "概念", "aliases": []},
            {"name": "cette statue", "type": "物品", "aliases": []},
            {"name": "the senior", "type": "角色", "aliases": []},
        ],
        "relations": [],
    },
    "7162901ba31dde22": {
        "entities": [
            {"name": "Qi Xin", "type": "角色", "aliases": ["Ms.Qi Xin"]},
            {"name": "He Rijun", "type": "角色", "aliases": []},
            {"name": "Reunion of the Three Swallows", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "He Rijun", "dst": "Reunion of the Three Swallows", "relation": "创作", "confidence": 0.9},
            {"src": "Qi Xin", "dst": "He Rijun", "relation": "有关联", "confidence": 0.7},
            {"src": "Qi Xin", "dst": "Reunion of the Three Swallows", "relation": "想要", "confidence": 0.8},
        ],
    },
    "963e95585f94c45a": {
        "entities": [
            {"name": "Visual Liang", "type": "角色", "aliases": ["Liang"]},
        ],
        "relations": [],
    },
    "aba293304946b678": {
        "entities": [
            {"name": "a witch", "type": "角色", "aliases": []},
            {"name": "a dagger", "type": "物品", "aliases": []},
            {"name": "a diamond-covered key", "type": "物品", "aliases": []},
            {"name": "a knife", "type": "物品", "aliases": []},
        ],
        "relations": [],
    },
    "06e4abf99adcdf00": {
        "entities": [
            {"name": "that dagger", "type": "物品", "aliases": []},
            {"name": "a cage", "type": "物品", "aliases": []},
            {"name": "La porte", "type": "物品", "aliases": ["Une porte entourée par la douleur"]},
        ],
        "relations": [],
    },
    "97147ef92383e52f": {
        "entities": [
            {"name": "Jay", "type": "角色", "aliases": []},
            {"name": "Mandrake", "type": "物品", "aliases": []},
            {"name": "Miss Wanish", "type": "角色", "aliases": ["Wanish"]},
            {"name": "the Foundation", "type": "组织", "aliases": ["Foundation"]},
        ],
        "relations": [],
    },
    "0d27503d7d91b77b": {
        "entities": [
            {"name": "Jay", "type": "角色", "aliases": []},
            {"name": "the orb", "type": "物品", "aliases": []},
            {"name": "the divination", "type": "事件", "aliases": []},
            {"name": "the Foundation", "type": "组织", "aliases": ["foundation"]},
        ],
        "relations": [
            {"src": "Jay", "dst": "the divination", "relation": "施行", "confidence": 0.7},
            {"src": "Jay", "dst": "the orb", "relation": "接触", "confidence": 0.7},
        ],
    },
    "3a2f854749939005": {
        "entities": [
            {"name": "Polly", "type": "角色", "aliases": []},
            {"name": "sis", "type": "角色", "aliases": []},
            {"name": "Peace Be With Us", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "Peace Be With Us", "dst": "sis", "relation": "欺骗", "confidence": 0.7},
            {"src": "Peace Be With Us", "dst": "Polly", "relation": "欺骗", "confidence": 0.7},
        ],
    },
    "f576c3785b43377c": {
        "entities": [
            {"name": "the bell ringer", "type": "角色", "aliases": []},
            {"name": "Elysium", "type": "地点", "aliases": []},
            {"name": "the Foundation", "type": "组织", "aliases": []},
            {"name": "Apostle Matthews", "type": "角色", "aliases": ["Matthews"]},
            {"name": "the gate", "type": "物品", "aliases": []},
            {"name": "the key", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "the gate", "dst": "Elysium", "relation": "通往", "confidence": 0.9},
            {"src": "the key", "dst": "the gate", "relation": "开启", "confidence": 0.8},
        ],
    },
    "ff2858a316bc6000": {
        "entities": [
            {"name": "Jay", "type": "角色", "aliases": []},
            {"name": "Mendes", "type": "角色", "aliases": []},
            {"name": "Elysium", "type": "地点", "aliases": []},
            {"name": "Mercuria", "type": "角色", "aliases": []},
            {"name": "their hideout", "type": "地点", "aliases": []},
            {"name": "their apostle", "type": "角色", "aliases": []},
            {"name": "the key", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "Mendes", "dst": "Elysium", "relation": "拥有", "confidence": 0.8},
            {"src": "the key", "dst": "Elysium", "relation": "开启", "confidence": 0.7},
            {"src": "the key", "dst": "their hideout", "relation": "开启", "confidence": 0.7},
        ],
    },
    # ===== batch_midhigh_03 =====
    "39ae518316a1618b": {
        "entities": [
            {"name": "That ceremony", "type": "事件", "aliases": []},
            {"name": "the last revelation", "type": "事件", "aliases": []},
            {"name": "Manus", "type": "组织", "aliases": []},
            {"name": "Elysium", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "Manus", "dst": "Elysium", "relation": "计划开启", "confidence": 0.8},
            {"src": "Manus", "dst": "That ceremony", "relation": "举办", "confidence": 0.7},
            {"src": "Manus", "dst": "the last revelation", "relation": "宣扬", "confidence": 0.7},
        ],
    },
    "dabf162e3e73538e": {
        "entities": [
            {"name": "Tildy", "type": "角色", "aliases": []},
            {"name": "the New Age Market", "type": "地点", "aliases": []},
            {"name": "the Saint Pavlov Foundation", "type": "组织", "aliases": ["Saint Pavlov Foundation"]},
            {"name": "the followers", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "Tildy", "dst": "the New Age Market", "relation": "前往", "confidence": 0.7},
            {"src": "Tildy", "dst": "the Saint Pavlov Foundation", "relation": "回避", "confidence": 0.7},
        ],
    },
    "25e2c8e9a8d834f7": {
        "entities": [
            {"name": "the Panopticon", "type": "地点", "aliases": []},
            {"name": "Roberta", "type": "角色", "aliases": []},
            {"name": "10th of July", "type": "时间", "aliases": []},
            {"name": "Spain", "type": "地点", "aliases": []},
            {"name": "France", "type": "地点", "aliases": []},
            {"name": "literature", "type": "概念", "aliases": []},
            {"name": "a kaleidoscope", "type": "物品", "aliases": []},
        ],
        "relations": [],
    },
    "7b388768edbaad31": {
        "entities": [
            {"name": "secession groups", "type": "组织", "aliases": []},
            {"name": "our venerable branch", "type": "组织", "aliases": []},
            {"name": "Vienna", "type": "地点", "aliases": []},
            {"name": "the guard", "type": "角色", "aliases": []},
            {"name": "knight of Vienna", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "the guard", "dst": "knight of Vienna", "relation": "即是", "confidence": 0.9},
        ],
    },
    "b2d5a4e063b0c406": {
        "entities": [
            {"name": "comrades", "type": "组织", "aliases": []},
            {"name": "the critters", "type": "角色", "aliases": []},
            {"name": "the self-purification system", "type": "物品", "aliases": []},
            {"name": "the ore", "type": "物品", "aliases": []},
            {"name": "that stone", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "comrades", "dst": "the critters", "relation": "驱离", "confidence": 0.8},
            {"src": "the ore", "dst": "the self-purification system", "relation": "供能", "confidence": 0.85},
            {"src": "the ore", "dst": "that stone", "relation": "位于", "confidence": 0.7},
        ],
    },
    "a809d54be47d8a33": {
        "entities": [
            {"name": "the adults", "type": "角色", "aliases": []},
            {"name": "the kids", "type": "角色", "aliases": ["children"]},
            {"name": "town", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "the kids", "dst": "town", "relation": "留守", "confidence": 0.8},
        ],
    },
    "10d1f3f9e162c472": {
        "entities": [
            {"name": "our police officers", "type": "组织", "aliases": []},
            {"name": "robot", "type": "物品", "aliases": []},
            {"name": "Thompson", "type": "角色", "aliases": []},
            {"name": "the watering car", "type": "物品", "aliases": []},
            {"name": "sensor", "type": "物品", "aliases": []},
            {"name": "the first office desk", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "robot", "dst": "our police officers", "relation": "协助", "confidence": 0.85},
        ],
    },
    "906cdb570d91c2f2": {
        "entities": [
            {"name": "Sergeant Williams", "type": "角色", "aliases": ["Williams"]},
            {"name": "Mr.Iverson", "type": "角色", "aliases": ["Iverson"]},
            {"name": "the New Humans Company", "type": "组织", "aliases": ["the company", "New Humans Company"]},
            {"name": "Rimmick Cup", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "Mr.Iverson", "dst": "the New Humans Company", "relation": "隶属", "confidence": 0.9},
            {"src": "the New Humans Company", "dst": "Rimmick Cup", "relation": "提供安保", "confidence": 0.85},
        ],
    },
    "2b67ce6c8405a2ef": {
        "entities": [
            {"name": "the Rimmet Cuff", "type": "事件", "aliases": []},
            {"name": "Wendy", "type": "角色", "aliases": []},
            {"name": "exhibition hall", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "exhibition hall", "dst": "the Rimmet Cuff", "relation": "举办", "confidence": 0.8},
        ],
    },
    "fb1b6c7d02abf67f": {
        "entities": [
            {"name": "Wendy", "type": "角色", "aliases": []},
            {"name": "the Rimmick Cup", "type": "事件", "aliases": []},
            {"name": "the exhibition", "type": "地点", "aliases": []},
            {"name": "the World Cup", "type": "事件", "aliases": []},
            {"name": "Pickles", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "the Rimmick Cup", "dst": "the exhibition", "relation": "举办", "confidence": 0.85},
        ],
    },
    "b1ec9ba0b9b1cc44": {
        "entities": [
            {"name": "a pet dog", "type": "角色", "aliases": []},
            {"name": "the World Cup", "type": "事件", "aliases": []},
            {"name": "Pickles", "type": "角色", "aliases": []},
            {"name": "blacklist", "type": "物品", "aliases": []},
        ],
        "relations": [
            {"src": "the World Cup", "dst": "blacklist", "relation": "拥有", "confidence": 0.7},
        ],
    },
    "69a63ddb4dbbba65": {
        "entities": [
            {"name": "the remote control", "type": "物品", "aliases": []},
            {"name": "the water collie", "type": "角色", "aliases": []},
            {"name": "the Rimmick Cup", "type": "事件", "aliases": []},
            {"name": "Miss A.C.", "type": "角色", "aliases": ["A.C."]},
            {"name": "that dog", "type": "角色", "aliases": []},
            {"name": "that puppy", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "the water collie", "dst": "the Rimmick Cup", "relation": "找到", "confidence": 0.85},
        ],
    },
    "b8f1097e42cc6ff0": {
        "entities": [
            {"name": "this shrine", "type": "地点", "aliases": []},
            {"name": "the locals", "type": "角色", "aliases": []},
            {"name": "North Cave", "type": "地点", "aliases": []},
            {"name": "caves", "type": "地点", "aliases": []},
        ],
        "relations": [
            {"src": "this shrine", "dst": "caves", "relation": "包含", "confidence": 0.8},
            {"src": "this shrine", "dst": "North Cave", "relation": "包含", "confidence": 0.85},
            {"src": "the locals", "dst": "this shrine", "relation": "知晓", "confidence": 0.7},
        ],
    },
    "09fc467981104642": {
        "entities": [
            {"name": "others' bones", "type": "物品", "aliases": []},
            {"name": "these stupid birds", "type": "角色", "aliases": []},
        ],
        "relations": [],
    },
    "ae2a5c933b5dfe0b": {
        "entities": [
            {"name": "the Maghavs", "type": "组织", "aliases": []},
            {"name": "the Bohemians", "type": "组织", "aliases": []},
            {"name": "Austria", "type": "地点", "aliases": []},
            {"name": "Romania", "type": "地点", "aliases": []},
            {"name": "the storm", "type": "现象", "aliases": []},
            {"name": "the era", "type": "时间", "aliases": []},
        ],
        "relations": [
            {"src": "the Maghavs", "dst": "the Bohemians", "relation": "同为团体", "confidence": 0.8},
            {"src": "Austria", "dst": "Romania", "relation": "政策相异", "confidence": 0.7},
            {"src": "the storm", "dst": "the era", "relation": "关联", "confidence": 0.7},
        ],
    },
    "567ffc976ff33554": {
        "entities": [
            {"name": "Mr.Thomas", "type": "角色", "aliases": ["Thomas"]},
            {"name": "Expressionism", "type": "概念", "aliases": []},
            {"name": "Impressionism", "type": "概念", "aliases": []},
            {"name": "the New Free Press", "type": "组织", "aliases": []},
            {"name": "that major", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Mr.Thomas", "dst": "Expressionism", "relation": "谈论", "confidence": 0.8},
            {"src": "Expressionism", "dst": "Impressionism", "relation": "同为艺术流派", "confidence": 0.7},
            {"src": "the New Free Press", "dst": "that major", "relation": "讨论", "confidence": 0.7},
        ],
    },
    "208fe4959298cf3f": {
        "entities": [
            {"name": "Keith", "type": "角色", "aliases": []},
            {"name": "Keen", "type": "角色", "aliases": []},
            {"name": "scarpia", "type": "角色", "aliases": []},
            {"name": "Zilla", "type": "角色", "aliases": []},
            {"name": "Wolf", "type": "角色", "aliases": []},
            {"name": "the show", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "Keith", "dst": "scarpia", "relation": "计划击杀", "confidence": 0.8},
            {"src": "Keen", "dst": "scarpia", "relation": "计划击杀", "confidence": 0.8},
        ],
    },
    "06495406b870da83": {
        "entities": [
            {"name": "Miss Villa", "type": "角色", "aliases": ["Villa"]},
            {"name": "Rajaski", "type": "组织", "aliases": []},
            {"name": "Mr.Boto", "type": "角色", "aliases": ["Boto"]},
            {"name": "Pryroda", "type": "组织", "aliases": []},
        ],
        "relations": [
            {"src": "Rajaski", "dst": "Pryroda", "relation": "关联", "confidence": 0.7},
            {"src": "Mr.Boto", "dst": "Rajaski", "relation": "关联", "confidence": 0.7},
        ],
    },
    "f6188f6abc62f8b7": {
        "entities": [
            {"name": "Short Stuff", "type": "角色", "aliases": ["shortstuff"]},
        ],
        "relations": [],
    },
    "19f9ee1518221354": {
        "entities": [
            {"name": "office", "type": "地点", "aliases": []},
            {"name": "the mall", "type": "地点", "aliases": []},
            {"name": "girls and boys", "type": "角色", "aliases": []},
            {"name": "gentlemen", "type": "角色", "aliases": []},
        ],
        "relations": [],
    },
    "22dcf6741f16105b": {
        "entities": [
            {"name": "this wallet", "type": "物品", "aliases": []},
            {"name": "Bogey", "type": "角色", "aliases": []},
            {"name": "Breton", "type": "角色", "aliases": []},
            {"name": "Brian", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "Bogey", "dst": "this wallet", "relation": "夺回", "confidence": 0.8},
        ],
    },
    "f023f8b8ffa1c0e1": {
        "entities": [
            {"name": "the farm", "type": "地点", "aliases": []},
            {"name": "Texan man", "type": "角色", "aliases": []},
            {"name": "my father", "type": "角色", "aliases": []},
            {"name": "my brother", "type": "角色", "aliases": []},
            {"name": "Los Angeles", "type": "地点", "aliases": []},
            {"name": "the riots", "type": "事件", "aliases": []},
        ],
        "relations": [
            {"src": "my brother", "dst": "the riots", "relation": "避开", "confidence": 0.7},
            {"src": "my brother", "dst": "Los Angeles", "relation": "前往", "confidence": 0.7},
        ],
    },
    "ffe828ddc6a46bdc": {
        "entities": [
            {"name": "Flutterpage", "type": "角色", "aliases": ["Miss Flutterpage"]},
            {"name": "a book", "type": "物品", "aliases": []},
            {"name": "a carbuncle", "type": "物品", "aliases": []},
            {"name": "Mr.Hat", "type": "角色", "aliases": ["Hat"]},
        ],
        "relations": [
            {"src": "a book", "dst": "a carbuncle", "relation": "镶嵌", "confidence": 0.85},
            {"src": "Flutterpage", "dst": "Mr.Hat", "relation": "是朋友", "confidence": 0.85},
        ],
    },
    "9e1a1b599b3ea5f0": {
        "entities": [
            {"name": "Miss Tooth Fairy", "type": "角色", "aliases": ["Tooth Fairy"]},
            {"name": "a haunted hide mansion", "type": "地点", "aliases": []},
            {"name": "the Black Fog", "type": "现象", "aliases": []},
            {"name": "this lady", "type": "角色", "aliases": []},
        ],
        "relations": [
            {"src": "this lady", "dst": "a haunted hide mansion", "relation": "拥有", "confidence": 0.85},
            {"src": "this lady", "dst": "the Black Fog", "relation": "关联", "confidence": 0.7},
            {"src": "Miss Tooth Fairy", "dst": "this lady", "relation": "拜访", "confidence": 0.8},
        ],
    },
}

# 合并无内容块
for h, d in NOOP.items():
    RESULTS[h] = d


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("\n", "").replace("\r", "")


def validate() -> int:
    bad = 0
    for h, d in RESULTS.items():
        pool = set()
        for e in d.get("entities") or []:
            nm = e.get("name") or ""
            pool.add(nm)
            pool |= set(e.get("aliases") or [])
        for r in d.get("relations") or []:
            if r.get("src") not in pool or r.get("dst") not in pool:
                print(f"[dangling] {h} {r.get('src')} -> {r.get('dst')}")
                bad += 1
    return bad


def landing() -> int:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    text_by_hash = {c["hash"]: c.get("text", "") for c in corpus["chunks"]}
    bad = 0
    for h, d in RESULTS.items():
        ntext = _norm(text_by_hash.get(h, ""))
        if not ntext:
            print(f"[landing-missing-corpus] {h}")
            bad += 1
            continue
        for e in d.get("entities") or []:
            cands = [e.get("name") or ""] + list(e.get("aliases") or [])
            if not any(_norm(c) in ntext for c in cands):
                print(f"[landing-fail] {h} entity={e.get('name')} aliases={e.get('aliases')}")
                bad += 1
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    v, m = validate(), landing()
    total_e = sum(len(d.get("entities") or []) for d in RESULTS.values())
    total_r = sum(len(d.get("relations") or []) for d in RESULTS.values())
    nonempty = sum(1 for d in RESULTS.values() if d.get("entities") or d.get("relations"))
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}，有内容块 {nonempty}")
    if v or m:
        print("[ABORT] 存在悬空或未落地，未写盘")
        return 1
    if not args.apply:
        print("[dry-run] 加 --apply 写盘")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    for h, d in RESULTS.items():
        (CACHE / f"{h}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"[apply-missing-p35] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
