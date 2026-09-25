#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补抽 backfill3 第6/7批共50个漏网块（信息量分8~9）。
手工抽取，写盘前 validate() 悬空自检 + landing() 落地自检。
仅抽正文明确出现的词，英文原文作 name/alias 保证落地，不外推背景知识。"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "knowledge" / "plot_cache" / "wu_ming_zhe"
CORPUS = ROOT / "data" / "knowledge" / "plot_corpus_wu_ming_zhe.json"

RESULTS = {
    "c72bcd320fbf4c4e": {
        "entities": [
            {"name": "黑天鹅", "type": "角色", "aliases": ["black swan"]},
            {"name": "Caroline Bartley", "type": "角色", "aliases": ["caroline bardley"]},
            {"name": "floor ritualist", "type": "概念", "aliases": ["floor ritualist"]},
        ],
        "relations": [
            {"src": "黑天鹅", "dst": "floor ritualist", "relation": "启发", "confidence": 0.8},
        ],
    },
    "2c3c59a99833e1fa": {
        "entities": [
            {"name": "Zugswang", "type": "角色", "aliases": ["Zugswang"]},
            {"name": "clinic", "type": "地点", "aliases": ["clinic"]},
            {"name": "girl's dorm", "type": "地点", "aliases": ["girl's dorm"]},
            {"name": "SelfiesWatchtower", "type": "地点", "aliases": ["SelfiesWatchtower"]},
            {"name": "classroom", "type": "地点", "aliases": ["classroom"]},
            {"name": "airway tunnel", "type": "地点", "aliases": ["airway tunnel"]},
            {"name": "library", "type": "地点", "aliases": ["library"]},
            {"name": "North West Tower", "type": "地点", "aliases": ["North West Tower"]},
            {"name": "first floor", "type": "地点", "aliases": ["first floor"]},
        ],
        "relations": [
            {"src": "classroom", "dst": "airway tunnel", "relation": "通往", "confidence": 0.85},
            {"src": "library", "dst": "airway tunnel", "relation": "通往", "confidence": 0.85},
            {"src": "North West Tower", "dst": "airway tunnel", "relation": "经", "confidence": 0.75},
        ],
    },
    "abe402d3d97ca3bd": {
        "entities": [
            {"name": "patrol teams", "type": "组织", "aliases": ["patrol teams", "blind patrol teams"]},
            {"name": "malpractice show", "type": "事件", "aliases": ["malpractice show"]},
            {"name": "vodka", "type": "物品", "aliases": ["vodka"]},
            {"name": "children", "type": "角色", "aliases": ["children"]},
            {"name": "flying ace", "type": "角色", "aliases": ["flying ace"]},
            {"name": "library", "type": "地点", "aliases": ["library"]},
            {"name": "sports field", "type": "地点", "aliases": ["sports field"]},
            {"name": "classroom windows", "type": "地点", "aliases": ["classroom windows"]},
        ],
        "relations": [
            {"src": "patrol teams", "dst": "malpractice show", "relation": "策划", "confidence": 0.7},
        ],
    },
    "db882fc283994728": {
        "entities": [
            {"name": "hidden side door", "type": "地点", "aliases": ["hidden side door"]},
            {"name": "closed cave", "type": "地点", "aliases": ["closed cave"]},
            {"name": "tuk-tuk", "type": "物品", "aliases": ["tuk-tuk"]},
            {"name": "village", "type": "地点", "aliases": ["village"]},
            {"name": "Uncle Sinha", "type": "角色", "aliases": ["Uncle Sinha"]},
            {"name": "lunch money", "type": "物品", "aliases": ["lunch money"]},
        ],
        "relations": [
            {"src": "Uncle Sinha", "dst": "lunch money", "relation": "索取", "confidence": 0.75},
            {"src": "hidden side door", "dst": "closed cave", "relation": "通往", "confidence": 0.7},
        ],
    },
    "6e7a6c93f20cbc85": {
        "entities": [
            {"name": "Walk of Fame", "type": "地点", "aliases": ["Walk of Fame"]},
            {"name": "Laura", "type": "角色", "aliases": ["Laura"]},
            {"name": "director", "type": "概念", "aliases": ["director"]},
            {"name": "movies", "type": "概念", "aliases": ["movies"]},
        ],
        "relations": [
            {"src": "Laura", "dst": "Walk of Fame", "relation": "带往", "confidence": 0.85},
            {"src": "Laura", "dst": "director", "relation": "是", "confidence": 0.9},
            {"src": "Laura", "dst": "movies", "relation": "谈论", "confidence": 0.8},
        ],
    },
    "f8eff277fe14edfb": {
        "entities": [
            {"name": "Arcanum Containment Department", "type": "组织", "aliases": ["Arcanum Containment Department"]},
            {"name": "film reel", "type": "物品", "aliases": ["film reel", "the film"]},
        ],
        "relations": [
            {"src": "Arcanum Containment Department", "dst": "film reel", "relation": "处理", "confidence": 0.8},
        ],
    },
    "a19a01b5d170d215": {
        "entities": [
            {"name": "curse film crazies", "type": "角色", "aliases": ["curse film crazies"]},
            {"name": "victims", "type": "角色", "aliases": ["victims"]},
            {"name": "parade", "type": "事件", "aliases": ["parade"]},
            {"name": "Sam", "type": "概念", "aliases": []},
        ],
        "relations": [
            {"src": "victims", "dst": "parade", "relation": "出自", "confidence": 0.75},
            {"src": "victims", "dst": "Sam", "relation": "恢复", "confidence": 0.7},
        ],
    },
    "edc7593b12e156a1": {
        "entities": [
            {"name": "beat cops", "type": "角色", "aliases": ["beat cops"]},
            {"name": "Arcanum", "type": "概念", "aliases": ["Arcanum"]},
            {"name": "dispatch", "type": "组织", "aliases": ["dispatch"]},
            {"name": "Arcanum incident", "type": "事件", "aliases": ["Arcanum incident"]},
            {"name": "rookie", "type": "角色", "aliases": ["rookie"]},
        ],
        "relations": [
            {"src": "beat cops", "dst": "dispatch", "relation": "上报", "confidence": 0.8},
            {"src": "beat cops", "dst": "Arcanum incident", "relation": "上报", "confidence": 0.8},
            {"src": "dispatch", "dst": "Arcanum incident", "relation": "派遣处理", "confidence": 0.8},
            {"src": "Arcanum", "dst": "Arcanum incident", "relation": "涉及", "confidence": 0.85},
        ],
    },
    "eaf2ba11aaacb6d7": {
        "entities": [
            {"name": "civvy", "type": "角色", "aliases": ["civvy"]},
            {"name": "suspect", "type": "角色", "aliases": ["suspect"]},
            {"name": "that woman", "type": "角色", "aliases": ["that woman"]},
            {"name": "this guy", "type": "角色", "aliases": ["this guy"]},
        ],
        "relations": [
            {"src": "that woman", "dst": "suspect", "relation": "交谈", "confidence": 0.8},
        ],
    },
    "3d501a7c2b80bc8d": {
        "entities": [
            {"name": "drugs", "type": "物品", "aliases": ["drugs"]},
            {"name": "arching skill", "type": "概念", "aliases": ["arching skill"]},
            {"name": "evil spirit", "type": "现象", "aliases": ["evil spirit"]},
        ],
        "relations": [
            {"src": "arching skill", "dst": "evil spirit", "relation": "驱退", "confidence": 0.7},
        ],
    },
    "59a483a0bedac3e0": {
        "entities": [
            {"name": "car", "type": "物品", "aliases": ["car"]},
            {"name": "crime scene", "type": "地点", "aliases": ["crime scene"]},
            {"name": "potatoes", "type": "物品", "aliases": ["potatoes"]},
            {"name": "carrots", "type": "物品", "aliases": ["carrots"]},
            {"name": "wholesalers", "type": "组织", "aliases": ["wholesalers"]},
            {"name": "Liang", "type": "角色", "aliases": ["Liang"]},
            {"name": "Officer Podia", "type": "角色", "aliases": ["Officer Podia"]},
            {"name": "hospital", "type": "地点", "aliases": ["hospital"]},
            {"name": "wife", "type": "角色", "aliases": ["wife"]},
        ],
        "relations": [
            {"src": "car", "dst": "crime scene", "relation": "发现于", "confidence": 0.8},
            {"src": "car", "dst": "potatoes", "relation": "装载", "confidence": 0.8},
            {"src": "car", "dst": "carrots", "relation": "装载", "confidence": 0.8},
            {"src": "Officer Podia", "dst": "hospital", "relation": "位于", "confidence": 0.8},
            {"src": "Liang", "dst": "hospital", "relation": "位于", "confidence": 0.8},
        ],
    },
    "f865aaa6447c6414": {
        "entities": [
            {"name": "space cadet", "type": "角色", "aliases": ["space cadet"]},
            {"name": "Miss Qi Xin", "type": "角色", "aliases": ["Miss Qi Xin"]},
            {"name": "movies", "type": "概念", "aliases": ["movies"]},
            {"name": "CO7", "type": "概念", "aliases": ["CO7"]},
            {"name": "cinema", "type": "地点", "aliases": ["cinema"]},
            {"name": "Boo", "type": "角色", "aliases": ["Boo"]},
            {"name": "Princess", "type": "角色", "aliases": ["Princess"]},
        ],
        "relations": [
            {"src": "space cadet", "dst": "Miss Qi Xin", "relation": "想念", "confidence": 0.75},
            {"src": "space cadet", "dst": "CO7", "relation": "迷恋", "confidence": 0.75},
        ],
    },
    "ae09f67cc0b38ebc": {
        "entities": [
            {"name": "Halloween", "type": "时间", "aliases": ["Halloween"]},
            {"name": "aerial stunts", "type": "事件", "aliases": ["aerial stunts"]},
            {"name": "motel", "type": "地点", "aliases": ["motel"]},
        ],
        "relations": [],
    },
    "d3cac9f9caeacb6b": {
        "entities": [
            {"name": "Egyptians", "type": "角色", "aliases": ["Egyptians"]},
            {"name": "Greeks", "type": "角色", "aliases": ["Greeks"]},
            {"name": "Chinese", "type": "角色", "aliases": ["Chinese"]},
            {"name": "Babylonians", "type": "角色", "aliases": ["Babylonians"]},
            {"name": "pi", "type": "概念", "aliases": ["pi"]},
            {"name": "circle", "type": "概念", "aliases": ["circle"]},
        ],
        "relations": [
            {"src": "Egyptians", "dst": "circle", "relation": "尝试绘制", "confidence": 0.8},
            {"src": "Greeks", "dst": "circle", "relation": "尝试绘制", "confidence": 0.8},
            {"src": "Chinese", "dst": "circle", "relation": "尝试绘制", "confidence": 0.8},
            {"src": "Babylonians", "dst": "circle", "relation": "尝试绘制", "confidence": 0.8},
            {"src": "pi", "dst": "circle", "relation": "近似", "confidence": 0.75},
        ],
    },
    "2a26aa62a0ae5999": {
        "entities": [
            {"name": "Miss Miragara", "type": "角色", "aliases": ["Miss Miragara"]},
        ],
        "relations": [],
    },
    "456b95158ab48375": {
        "entities": [
            {"name": "irrational number", "type": "概念", "aliases": ["irrational number"]},
            {"name": "soybeans", "type": "物品", "aliases": ["soybeans"]},
            {"name": "broad beans", "type": "物品", "aliases": ["broad beans"]},
            {"name": "Snow peas", "type": "物品", "aliases": ["Snow peas"]},
            {"name": "Chickpeas", "type": "物品", "aliases": ["Chickpeas"]},
            {"name": "rule", "type": "概念", "aliases": ["rule"]},
        ],
        "relations": [
            {"src": "rule", "dst": "soybeans", "relation": "适用", "confidence": 0.8},
        ],
    },
    "1ad927484fa080f7": {
        "entities": [
            {"name": "tumbleweed", "type": "物品", "aliases": ["tumbleweed"]},
            {"name": "flowers", "type": "物品", "aliases": ["flowers"]},
            {"name": "rocks", "type": "物品", "aliases": ["rocks"]},
            {"name": "holes", "type": "物品", "aliases": ["holes"]},
        ],
        "relations": [
            {"src": "rocks", "dst": "holes", "relation": "有", "confidence": 0.8},
        ],
    },
    "0f7e4c51ec44402c": {
        "entities": [
            {"name": "Chenwei Divination", "type": "概念", "aliases": ["Chenwei Divination"]},
            {"name": "Yenisei", "type": "角色", "aliases": ["Yenisei"]},
            {"name": "Mr.Yuri", "type": "角色", "aliases": ["Mr.Yuri"]},
            {"name": "supplies", "type": "物品", "aliases": ["supplies"]},
            {"name": "questions", "type": "概念", "aliases": ["questions"]},
        ],
        "relations": [
            {"src": "supplies", "dst": "questions", "relation": "交换", "confidence": 0.75},
        ],
    },
    "b3fc2609a4995ede": {
        "entities": [
            {"name": "fire kangaroos", "type": "角色", "aliases": ["fire kangaroos"]},
            {"name": "housing stress", "type": "概念", "aliases": ["housing stress"]},
            {"name": "Uluru games", "type": "事件", "aliases": ["Uluru games"]},
        ],
        "relations": [
            {"src": "fire kangaroos", "dst": "housing stress", "relation": "共致伤痛", "confidence": 0.7},
        ],
    },
    "3544fa889581323f": {
        "entities": [
            {"name": "song", "type": "物品", "aliases": ["song"]},
            {"name": "handkerchief", "type": "物品", "aliases": ["handkerchief"]},
        ],
        "relations": [
            {"src": "song", "dst": "handkerchief", "relation": "同为馈赠", "confidence": 0.7},
        ],
    },
    "09fd487fb5a23fbf": {
        "entities": [
            {"name": "Wicked", "type": "角色", "aliases": ["Wicked"]},
            {"name": "car", "type": "物品", "aliases": ["car"]},
            {"name": "Timekeeper", "type": "角色", "aliases": ["Timekeeper"]},
            {"name": "woods", "type": "地点", "aliases": ["woods"]},
            {"name": "gods' will", "type": "概念", "aliases": ["gods' will"]},
            {"name": "children", "type": "角色", "aliases": ["children"]},
            {"name": "demons", "type": "角色", "aliases": ["demons"]},
            {"name": "dilated pupils", "type": "现象", "aliases": ["dilated pupils"]},
        ],
        "relations": [
            {"src": "gods' will", "dst": "children", "relation": "指引", "confidence": 0.75},
            {"src": "demons", "dst": "children", "relation": "威胁", "confidence": 0.7},
        ],
    },
    "ac5966b9e2b13c28": {
        "entities": [
            {"name": "Sharperdantes", "type": "组织", "aliases": ["Sharperdantes"]},
            {"name": "Foundation", "type": "组织", "aliases": ["Foundation"]},
            {"name": "Barrel-Bow", "type": "角色", "aliases": ["Barrel-Bow"]},
            {"name": "Nisha", "type": "角色", "aliases": ["Nisha"]},
            {"name": "weapon", "type": "物品", "aliases": ["weapon"]},
            {"name": "battlefield", "type": "地点", "aliases": ["battlefield"]},
        ],
        "relations": [
            {"src": "Barrel-Bow", "dst": "Nisha", "relation": "共育", "confidence": 0.85},
        ],
    },
    "a244fa44b9aa00ec": {
        "entities": [
            {"name": "Mr.Bernard", "type": "角色", "aliases": ["Mr.Bernard"]},
            {"name": "office", "type": "地点", "aliases": ["office"]},
            {"name": "mall", "type": "地点", "aliases": ["mall"]},
            {"name": "rumors", "type": "概念", "aliases": ["rumors"]},
        ],
        "relations": [
            {"src": "Mr.Bernard", "dst": "office", "relation": "于", "confidence": 0.75},
            {"src": "rumors", "dst": "office", "relation": "流传", "confidence": 0.7},
        ],
    },
    "d8733c73e2f9ed55": {
        "entities": [
            {"name": "office", "type": "地点", "aliases": ["office"]},
            {"name": "mannequin", "type": "物品", "aliases": ["mannequin"]},
            {"name": "Foundation", "type": "组织", "aliases": ["Foundation"]},
            {"name": "visitors' advisory", "type": "概念", "aliases": ["visitors' advisory"]},
            {"name": "Jay", "type": "角色", "aliases": ["Jay"]},
            {"name": "Polina", "type": "角色", "aliases": ["Polina"]},
            {"name": "Saint", "type": "地点", "aliases": ["Saint"]},
        ],
        "relations": [
            {"src": "Jay", "dst": "Foundation", "relation": "隶属", "confidence": 0.7},
            {"src": "mannequin", "dst": "Foundation", "relation": "送回", "confidence": 0.75},
        ],
    },
    "ab0c2b4242c1aaef": {
        "entities": [
            {"name": "key", "type": "物品", "aliases": ["key"]},
            {"name": "green chair", "type": "物品", "aliases": ["green chair"]},
            {"name": "Roger", "type": "角色", "aliases": ["Roger"]},
            {"name": "siblings", "type": "角色", "aliases": ["siblings"]},
            {"name": "ceremony for the sufferer", "type": "事件", "aliases": ["ceremony for the sufferer"]},
            {"name": "secret", "type": "概念", "aliases": ["secret"]},
        ],
        "relations": [
            {"src": "Roger", "dst": "siblings", "relation": "是", "confidence": 0.85},
            {"src": "key", "dst": "secret", "relation": "藏有", "confidence": 0.7},
        ],
    },
    "babffbefd24da161": {
        "entities": [
            {"name": "年幼的治疗师", "type": "角色", "aliases": ["年幼的治疗师"]},
            {"name": "康复中心", "type": "地点", "aliases": ["康复中心"]},
            {"name": "乔治橡树", "type": "地点", "aliases": ["乔治橡树"]},
            {"name": "那首歌", "type": "概念", "aliases": ["那首歌"]},
            {"name": "红松鼠", "type": "角色", "aliases": ["红松鼠"]},
            {"name": "啄木鸟", "type": "角色", "aliases": ["啄木鸟"]},
        ],
        "relations": [
            {"src": "年幼的治疗师", "dst": "康复中心", "relation": "隶属", "confidence": 0.8},
            {"src": "红松鼠", "dst": "那首歌", "relation": "倾听", "confidence": 0.8},
            {"src": "啄木鸟", "dst": "那首歌", "relation": "倾听", "confidence": 0.8},
            {"src": "红松鼠", "dst": "乔治橡树", "relation": "栖于", "confidence": 0.8},
            {"src": "啄木鸟", "dst": "乔治橡树", "relation": "栖于", "confidence": 0.8},
        ],
    },
    "5a30c69a1aae3b5d": {
        "entities": [
            {"name": "APPLe先生", "type": "角色", "aliases": []},
            {"name": "观测者", "type": "角色", "aliases": ["观测者"]},
            {"name": "苏芙比小姐", "type": "角色", "aliases": ["苏芙比小姐"]},
            {"name": "药剂", "type": "物品", "aliases": ["药剂"]},
            {"name": "观测", "type": "概念", "aliases": ["观测"]},
        ],
        "relations": [
            {"src": "APPLe先生", "dst": "药剂", "relation": "需备", "confidence": 0.7},
            {"src": "观测者", "dst": "观测", "relation": "进行", "confidence": 0.8},
            {"src": "苏芙比小姐", "dst": "APPLe先生", "relation": "唤醒", "confidence": 0.8},
        ],
    },
    "0f1035d92def6edf": {
        "entities": [
            {"name": "dead mouse", "type": "物品", "aliases": ["dead mouse"]},
            {"name": "apples", "type": "物品", "aliases": ["apples"]},
            {"name": "eggs", "type": "物品", "aliases": ["eggs"]},
            {"name": "codger", "type": "角色", "aliases": ["codger"]},
            {"name": "porridge", "type": "物品", "aliases": ["porridge"]},
            {"name": "arcane skills", "type": "概念", "aliases": ["arcane skills"]},
            {"name": "machine lubricant", "type": "物品", "aliases": ["machine lubricant"]},
        ],
        "relations": [
            {"src": "codger", "dst": "apples", "relation": "提供", "confidence": 0.7},
            {"src": "codger", "dst": "eggs", "relation": "提供", "confidence": 0.7},
            {"src": "codger", "dst": "porridge", "relation": "厌恶", "confidence": 0.8},
        ],
    },
    "183425bf2d8e29ff": {
        "entities": [
            {"name": "Knee of Sound", "type": "地点", "aliases": ["Knee of Sound"]},
            {"name": "old fossils", "type": "角色", "aliases": ["old fossils"]},
        ],
        "relations": [],
    },
    "1cdd27681ed78dbd": {
        "entities": [
            {"name": "papers", "type": "物品", "aliases": ["papers"]},
            {"name": "photography", "type": "概念", "aliases": ["photography"]},
            {"name": "Mr.Kahl", "type": "角色", "aliases": ["Mr.Kahl"]},
            {"name": "secession building", "type": "地点", "aliases": ["secession building"]},
            {"name": "new art", "type": "概念", "aliases": ["new art"]},
            {"name": "manners", "type": "概念", "aliases": ["manners"]},
            {"name": "rituals", "type": "概念", "aliases": ["rituals"]},
            {"name": "Mr.Thomas", "type": "角色", "aliases": ["Mr.Thomas"]},
            {"name": "Expressionism", "type": "概念", "aliases": ["Expressionism"]},
        ],
        "relations": [
            {"src": "Mr.Thomas", "dst": "Expressionism", "relation": "谈论", "confidence": 0.8},
            {"src": "secession building", "dst": "new art", "relation": "展出", "confidence": 0.8},
        ],
    },
    "200823940fbad93a": {
        "entities": [
            {"name": "art", "type": "概念", "aliases": ["art"]},
            {"name": "schmool", "type": "角色", "aliases": ["schmool"]},
            {"name": "Zilla", "type": "角色", "aliases": ["Zilla"]},
            {"name": "Wolf", "type": "角色", "aliases": ["Wolf"]},
            {"name": "show", "type": "事件", "aliases": ["show"]},
            {"name": "Crowd", "type": "角色", "aliases": ["Crowd"]},
            {"name": "terrorists", "type": "角色", "aliases": ["terrorists"]},
        ],
        "relations": [
            {"src": "Crowd", "dst": "terrorists", "relation": "被指为", "confidence": 0.7},
        ],
    },
    "9c28ec066420d2d0": {
        "entities": [
            {"name": "bed", "type": "物品", "aliases": ["bed"]},
            {"name": "black snot", "type": "物品", "aliases": ["black snot"]},
            {"name": "lashes", "type": "物品", "aliases": ["lashes"]},
        ],
        "relations": [
            {"src": "black snot", "dst": "lashes", "relation": "附着", "confidence": 0.8},
        ],
    },
    "07092faefb4b9172": {
        "entities": [
            {"name": "poem", "type": "物品", "aliases": ["poem"]},
            {"name": "doomsday", "type": "事件", "aliases": ["doomsday"]},
            {"name": "Silenus", "type": "角色", "aliases": ["Silenus"]},
            {"name": "forest", "type": "地点", "aliases": ["forest"]},
            {"name": "ring of life", "type": "概念", "aliases": ["ring of life"]},
            {"name": "judgment", "type": "事件", "aliases": ["judgment"]},
        ],
        "relations": [
            {"src": "Silenus", "dst": "forest", "relation": "于", "confidence": 0.8},
            {"src": "poem", "dst": "doomsday", "relation": "提及", "confidence": 0.85},
        ],
    },
    "a5bd078dc3d44096": {
        "entities": [
            {"name": "ballgame", "type": "事件", "aliases": ["ballgame"]},
            {"name": "scoring rules", "type": "概念", "aliases": ["scoring rules"]},
            {"name": "foul points", "type": "概念", "aliases": ["foul points"]},
        ],
        "relations": [
            {"src": "ballgame", "dst": "scoring rules", "relation": "有", "confidence": 0.8},
            {"src": "ballgame", "dst": "foul points", "relation": "有", "confidence": 0.8},
        ],
    },
    "35c6f81bfc69df85": {
        "entities": [
            {"name": "security company", "type": "组织", "aliases": ["security company"]},
            {"name": "Security Control Type 1", "type": "物品", "aliases": ["Security Control Type 1"]},
            {"name": "tear gas", "type": "物品", "aliases": ["tear gas"]},
            {"name": "worm powder", "type": "物品", "aliases": ["worm powder"]},
            {"name": "magnetic interference unit", "type": "物品", "aliases": ["magnetic interference unit"]},
        ],
        "relations": [
            {"src": "security company", "dst": "Security Control Type 1", "relation": "推出", "confidence": 0.85},
            {"src": "Security Control Type 1", "dst": "tear gas", "relation": "含", "confidence": 0.85},
            {"src": "Security Control Type 1", "dst": "worm powder", "relation": "含", "confidence": 0.85},
            {"src": "Security Control Type 1", "dst": "magnetic interference unit", "relation": "含", "confidence": 0.85},
        ],
    },
    "ad9883ccaf2a7763": {
        "entities": [
            {"name": "Iverson", "type": "角色", "aliases": ["Iverson"]},
            {"name": "fire of art", "type": "概念", "aliases": ["fire of art"]},
            {"name": "utopia", "type": "概念", "aliases": ["utopia"]},
        ],
        "relations": [
            {"src": "Iverson", "dst": "utopia", "relation": "向往", "confidence": 0.7},
        ],
    },
    "7f8dfa8db3fa818d": {
        "entities": [
            {"name": "ventilation system", "type": "物品", "aliases": ["ventilation system"]},
            {"name": "exhibition hall", "type": "地点", "aliases": ["exhibition hall"]},
            {"name": "core device", "type": "物品", "aliases": ["core device"]},
            {"name": "sour flame wine", "type": "物品", "aliases": ["sour flame wine"]},
            {"name": "ambush", "type": "事件", "aliases": ["ambush"]},
        ],
        "relations": [
            {"src": "core device", "dst": "ventilation system", "relation": "属于", "confidence": 0.85},
            {"src": "core device", "dst": "exhibition hall", "relation": "位于", "confidence": 0.8},
            {"src": "ambush", "dst": "exhibition hall", "relation": "位于", "confidence": 0.75},
        ],
    },
    "0deb0b1b51d45ff0": {
        "entities": [
            {"name": "Guidance on Security", "type": "概念", "aliases": ["Guidance on Security"]},
            {"name": "security companies", "type": "组织", "aliases": ["security companies"]},
            {"name": "dog", "type": "角色", "aliases": ["dog"]},
        ],
        "relations": [
            {"src": "security companies", "dst": "Guidance on Security", "relation": "依", "confidence": 0.85},
            {"src": "security companies", "dst": "dog", "relation": "征收", "confidence": 0.8},
        ],
    },
    "d988f64c8533e1f5": {
        "entities": [
            {"name": "Miss Acie", "type": "角色", "aliases": ["Miss A.C."]},
            {"name": "replace fuse", "type": "物品", "aliases": ["replace fuse"]},
            {"name": "safety commitment statement", "type": "概念", "aliases": ["safety commitment statement"]},
            {"name": "violators", "type": "角色", "aliases": ["violators"]},
            {"name": "hidden place", "type": "地点", "aliases": ["hidden place"]},
        ],
        "relations": [
            {"src": "Miss Acie", "dst": "safety commitment statement", "relation": "援引", "confidence": 0.8},
            {"src": "Miss Acie", "dst": "violators", "relation": "逮捕", "confidence": 0.8},
            {"src": "Miss Acie", "dst": "hidden place", "relation": "带往", "confidence": 0.75},
        ],
    },
    "1454d89121567b8e": {
        "entities": [
            {"name": "number", "type": "概念", "aliases": ["number"]},
            {"name": "songs", "type": "概念", "aliases": ["songs"]},
            {"name": "steps", "type": "概念", "aliases": ["steps"]},
        ],
        "relations": [
            {"src": "number", "dst": "steps", "relation": "对应", "confidence": 0.75},
        ],
    },
    "810316ffb9cf3060": {
        "entities": [
            {"name": "Stock prices", "type": "概念", "aliases": ["Stock prices"]},
            {"name": "cash", "type": "物品", "aliases": ["cash"]},
            {"name": "Arcanum", "type": "概念", "aliases": ["Arcanum"]},
            {"name": "stock exchange", "type": "概念", "aliases": ["stock exchange"]},
            {"name": "urban agglomerations", "type": "概念", "aliases": ["urban agglomerations"]},
            {"name": "loans", "type": "概念", "aliases": ["loans"]},
            {"name": "stock market", "type": "概念", "aliases": ["stock market"]},
        ],
        "relations": [
            {"src": "Arcanum", "dst": "stock exchange", "relation": "促进", "confidence": 0.8},
            {"src": "stock market", "dst": "Stock prices", "relation": "含", "confidence": 0.7},
        ],
    },
    "8131db0db74fff97": {
        "entities": [
            {"name": "G.C.", "type": "地点", "aliases": ["G.C."]},
            {"name": "ministry", "type": "组织", "aliases": ["ministry"]},
            {"name": "Zhuyep", "type": "角色", "aliases": ["Zhuyep"]},
            {"name": "arcane creatures", "type": "角色", "aliases": ["arcane creatures"]},
            {"name": "liquor smell", "type": "现象", "aliases": ["liquor smell"]},
            {"name": "livestock", "type": "角色", "aliases": ["livestock"]},
            {"name": "fence", "type": "物品", "aliases": ["fence"]},
        ],
        "relations": [
            {"src": "Zhuyep", "dst": "ministry", "relation": "隶属", "confidence": 0.8},
            {"src": "livestock", "dst": "fence", "relation": "逃出", "confidence": 0.8},
        ],
    },
    "de6bf1395cd0a691": {
        "entities": [
            {"name": "Ring des Lebens", "type": "概念", "aliases": ["Ring des Lebens"]},
            {"name": "Ring aller Leben", "type": "概念", "aliases": ["Ring aller Leben"]},
            {"name": "Urteil", "type": "事件", "aliases": ["Urteil"]},
            {"name": "youngest day", "type": "时间", "aliases": ["youngest day"]},
            {"name": "twilight", "type": "时间", "aliases": ["twilight"]},
        ],
        "relations": [
            {"src": "Ring des Lebens", "dst": "Ring aller Leben", "relation": "即", "confidence": 0.8},
        ],
    },
    "f6e8385ec6a1da47": {
        "entities": [
            {"name": "soldiers", "type": "角色", "aliases": ["soldiers"]},
            {"name": "tyranny", "type": "概念", "aliases": ["tyranny"]},
            {"name": "Comrades", "type": "角色", "aliases": ["Comrades"]},
        ],
        "relations": [],
    },
    "a0f7e07f642a115a": {
        "entities": [
            {"name": "Rusalka", "type": "角色", "aliases": ["Rusalka"]},
            {"name": "leyline researcher", "type": "角色", "aliases": ["leyline researcher"]},
            {"name": "editor", "type": "角色", "aliases": ["editor"]},
            {"name": "environmental research", "type": "概念", "aliases": ["environmental research"]},
            {"name": "report", "type": "物品", "aliases": ["report"]},
            {"name": "ley lines", "type": "概念", "aliases": ["ley lines"]},
        ],
        "relations": [
            {"src": "editor", "dst": "environmental research", "relation": "隶属", "confidence": 0.8},
            {"src": "editor", "dst": "report", "relation": "刊发", "confidence": 0.85},
            {"src": "leyline researcher", "dst": "ley lines", "relation": "研究", "confidence": 0.8},
        ],
    },
    "9c8b52daff2260a2": {
        "entities": [
            {"name": "creatures", "type": "角色", "aliases": ["creatures"]},
            {"name": "children", "type": "角色", "aliases": ["children"]},
            {"name": "town", "type": "地点", "aliases": ["town"]},
            {"name": "workers", "type": "角色", "aliases": ["workers"]},
            {"name": "factories", "type": "地点", "aliases": ["factories"]},
            {"name": "ore", "type": "物品", "aliases": ["ore"]},
            {"name": "debris", "type": "物品", "aliases": ["debris"]},
            {"name": "production lines", "type": "概念", "aliases": ["production lines"]},
            {"name": "surrounding cities", "type": "地点", "aliases": ["surrounding cities"]},
        ],
        "relations": [
            {"src": "workers", "dst": "factories", "relation": "改造", "confidence": 0.85},
            {"src": "workers", "dst": "ore", "relation": "清理", "confidence": 0.8},
            {"src": "workers", "dst": "debris", "relation": "清理", "confidence": 0.8},
            {"src": "factories", "dst": "production lines", "relation": "将启", "confidence": 0.8},
            {"src": "town", "dst": "surrounding cities", "relation": "联合", "confidence": 0.75},
        ],
    },
    "cee01bfb05d4ca06": {
        "entities": [
            {"name": "leader", "type": "角色", "aliases": ["leader"]},
            {"name": "humans", "type": "角色", "aliases": ["humans"]},
            {"name": "cleansing", "type": "概念", "aliases": ["cleansing"]},
            {"name": "envoy", "type": "角色", "aliases": ["envoy"]},
            {"name": "mother", "type": "角色", "aliases": ["mother"]},
            {"name": "mask", "type": "物品", "aliases": ["mask"]},
        ],
        "relations": [
            {"src": "humans", "dst": "envoy", "relation": "属", "confidence": 0.7},
            {"src": "envoy", "dst": "mother", "relation": "献首", "confidence": 0.75},
        ],
    },
    "d73867785ba11996": {
        "entities": [
            {"name": "door", "type": "物品", "aliases": ["door"]},
            {"name": "Ms.Bonish", "type": "角色", "aliases": ["Ms.Bonish"]},
            {"name": "luggage", "type": "物品", "aliases": ["luggage"]},
            {"name": "ceremony", "type": "事件", "aliases": ["ceremony"]},
            {"name": "wackos", "type": "角色", "aliases": ["wackos"]},
        ],
        "relations": [
            {"src": "wackos", "dst": "ceremony", "relation": "举办", "confidence": 0.85},
        ],
    },
    "167e99c52a6f9de3": {
        "entities": [
            {"name": "horses", "type": "角色", "aliases": ["horses"]},
            {"name": "driver", "type": "角色", "aliases": ["driver"]},
            {"name": "car", "type": "物品", "aliases": ["car"]},
            {"name": "luggage", "type": "物品", "aliases": ["luggage"]},
            {"name": "travel documents", "type": "物品", "aliases": ["travel documents"]},
            {"name": "trunk", "type": "物品", "aliases": ["trunk"]},
            {"name": "cash", "type": "物品", "aliases": ["cash"]},
            {"name": "fog", "type": "现象", "aliases": ["fog"]},
        ],
        "relations": [
            {"src": "driver", "dst": "car", "relation": "于", "confidence": 0.85},
            {"src": "luggage", "dst": "trunk", "relation": "于", "confidence": 0.85},
            {"src": "travel documents", "dst": "trunk", "relation": "于", "confidence": 0.85},
            {"src": "cash", "dst": "trunk", "relation": "于", "confidence": 0.8},
        ],
    },
    "8ac434b19fea0e9f": {
        "entities": [
            {"name": "arcane skill", "type": "概念", "aliases": ["arcane skill"]},
            {"name": "traces", "type": "概念", "aliases": ["traces"]},
            {"name": "guest", "type": "角色", "aliases": ["guest"]},
            {"name": "room", "type": "地点", "aliases": ["room"]},
            {"name": "wooden box", "type": "物品", "aliases": ["wooden box"]},
            {"name": "buddy", "type": "角色", "aliases": ["buddy"]},
        ],
        "relations": [
            {"src": "arcane skill", "dst": "traces", "relation": "察见", "confidence": 0.85},
            {"src": "guest", "dst": "room", "relation": "滞留", "confidence": 0.8},
            {"src": "guest", "dst": "traces", "relation": "遗留", "confidence": 0.8},
        ],
    },
}


# 规范化：剔除与正名相同的别名（规则7：别名不可与正名相同）
for _d in RESULTS.values():
    for _e in _d.get("entities") or []:
        _e["aliases"] = [a for a in (_e.get("aliases") or []) if a and a != _e.get("name")]


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
    print(f"[validate] 块 {len(RESULTS)}，悬空 {v}，未落地 {m}")
    print(f"[stats] 实体 {total_e}，关系 {total_r}")
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
    print(f"[apply-missing-p37] 写入 {len(RESULTS)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
