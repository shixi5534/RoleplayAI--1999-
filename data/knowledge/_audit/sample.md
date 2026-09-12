# 剧情图谱抽取质量审计 · 抽样样本

- 角色：wu_ming_zhe ｜ 样本 15 块（contrib 10 / empty 3 / cloud18 2）
- `本地结果` 是当前缓存里 **qwen2.5:7b** 的抽取；请对照正文用云端模型重新抽取并判定。

## #1 `a8ab700510c4f71e`　[contrib] en 3.5 「周围有人在走动」
- 出处：【重返未来：1999】3.5版本「绿松石蛇俱乐部」全剧情 - Reverse: 1999｜4K（10「周围有人在走动」）

### 正文

No, I kinda know what's going on, but...Don't you worry yourself over us, señora.Oh, don't get me wrong.I mean, no offense.Actually, this is my first time, too.Not so brushed up on the rules myself, let alone the Argos.Then what brings a lady like you here?I have visited every arcane doctor in the city, and not one of them has a clue.They take it as a horrible and unbreakable curse.My dear Camilla, there's not much time left for her.

### 本地 7B 抽取结果

```json
{"entities": [{"name": "señora", "type": "角色", "aliases": ["Madam Lucy", "露西"]}, {"name": "Camilla", "type": "角色", "aliases": ["卡米拉"]}], "relations": [{"src": "señora", "dst": "Camilla", "relation": "拥有", "confidence": 0.9}]}
```

## #2 `97afe71e19da3021`　[contrib] en 3.6 《苦涩之眼》欢迎来到生活的背面。
- 出处：【重返未来：1999】3.6版本「人们向何处去」全剧情流程（10.《苦涩之眼》欢迎来到生活的背面。）

### 正文

We're all quite used to the language disorder by now, so that isn't much of a problem.And there isn't much need for him to communicate with anyone.But what does concern me is that moving tower, a brand new variable.What was it again?There was an expression I heard when I was trying to research Keeperina's and namethese arcane skills.Oh, that's the one!People can only borrow language, they cannot reach the reality behind it.

### 本地 7B 抽取结果

```json
{"entities": [{"name": "moving tower", "type": "事件", "aliases": ["移动的塔"]}, {"name": "Keeperina", "type": "角色", "aliases": ["凯瑞娜"]}, {"name": "arcane skills", "type": "概念", "aliases": ["神秘技能"]}], "relations": []}
```

## #3 `f38d5241a9d8a1a1`　[contrib] en 3.8 记忆看见我
- 出处：【重返未来：1999】3.8版本「世纪末尺度」全剧情流程 - Reverse: 1999｜4K（10.记忆看见我）

### 正文

She's got a heart of stone, you know.It was me, told him to steal from you.This is the thief, this little deer.And she did it all right under my nose.I must admit, I'm impressed.Not just her, she has an accomplice.This noisy little ragamuffin I caught.I'll catch you for this.That voice, the same puppet from before.Miss Ever Echo, is there a reason why you're obstructing our work?Like what you're doing.

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Miss Ever Echo", "type": "角色", "aliases": ["Echo"]}, {"name": "她", "type": "角色", "aliases": ["she", "她"]}, {"name": "他", "type": "角色", "aliases": ["he", "他"]}, {"name": "你", "type": "角色", "aliases": ["you", "你"]}], "relations": [{"src": "Miss Ever Echo", "dst": "她", "relation": "阻碍", "confidence": 0.9}, {"src": "她", "dst": "他", "relation": "指示", "confidence": 0.9}, {"src": "她", "dst": "你", "relation": "偷窃", "confidence": 0.9}, {"src": "Miss Ever Echo", "dst": "她", "relation": "同伙", "confidence": 0.9}]}
```

## #4 `10d030e16320ee62`　[contrib] en 3.2 城市的癔症｜药方是一剂幻觉般的夏日午后
- 出处：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（10.城市的癔症｜药方是一剂幻觉般的夏日午后）

### 正文

Madame Poinish, as much as I appreciate your humor, now really isn't the time for it.Where did she go?I'm quite used to her attitude, but stealing that necklace crosses a line.Adele, Elysianne was never here.Perhaps it fell out of your pocket.Allow me to aid you in its return.I believe it is best you not act alone in your current state.Ah, I've got it now.She didn't come to your parlour today, so she must have gone somewhere else.

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Madame Poinish", "type": "角色", "aliases": ["Poinish", "卢西"]}, {"name": "Adele", "type": "角色", "aliases": ["阿黛尔"]}, {"name": "Elysianne", "type": "角色", "aliases": ["伊莉丝安妮"]}, {"name": "necklace", "type": "物品", "aliases": ["项链"]}], "relations": [{"src": "Madame Poinish", "dst": "Elysianne", "relation": "杀死", "confidence": 0.6}, {"src": "Madame Poinish", "dst": "Adele", "relation": "前往", "confidence": 0.8}, {"src": "necklace", "dst": "Elysianne", "relation": "持有", "confidence": 0.9}, {"src": "necklace", "dst": "Adele", "relation": "象征", "confidence": 0.8}]}
```

## #5 `a42b0264ebd1a747`　[contrib] en 3.7 TH.10【应急策略】须有以万变应不变的智慧。
- 出处：【重返未来：1999】3.7版本主线「他者的悲哀」全剧情 - Reverse: 1999｜4K（13.TH.10【应急策略】须有以万变应不变

### 正文

Mr.Kreis, what evidence do you have that this assault is beyond what is already accountedfor in our emergency procedures?Indeed.You're a form of vigil, Kreis.You should be well aware that there is simply no teleportation array with the capacityto move such a force into our security parameter undetected.Have you already forgotten our investigation into Hill 299?They hollowed it out and transferred 10,000 soldiers inside without being

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Mr.Kreis", "type": "角色", "aliases": ["克雷士"]}, {"name": "Hill 299", "type": "地点", "aliases": ["希尔299"]}], "relations": [{"src": "Mr.Kreis", "dst": "Hill 299", "relation": "前往", "confidence": 0.9}]}
```

## #6 `7d19a4629b9120f6`　[contrib] en 2.6 开幕
- 出处：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（01开幕）

### 正文

Hear this!For us!For poetry!For us!For free will!For literature!Our haven!The Panopticon!No us but here!Doris, that blind writer?Three days ago, she asked me for directions to Komala Prison.Prison?This is an experimental facility.Soon you'll see just what that means.Jailer, who is the ruler of this prison?According to the agreement,the idealist and I represent the two factions of La Sociedad.In light of his possible assassination,

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Doris", "type": "角色", "aliases": ["多丽丝"]}, {"name": "Komala Prison", "type": "地点", "aliases": ["科马拉监狱"]}, {"name": "La Sociedad", "type": "组织", "aliases": ["拉·社会"]}, {"name": "Jailer", "type": "角色", "aliases": ["狱卒"]}, {"name": "Panopticon", "type": "地点", "aliases": ["全景监狱"]}, {"name": "idealist", "type": "角色", "aliases": ["理想主义者"]}], "relations": [{"src": "Doris", "dst": "Komala Prison", "relation": "前往", "confidence": 0.7}, {"src": "idealist", "dst": "La Sociedad", "relation": "代表", "confidence": 0.7}, {"src": "Jailer", "dst": "Panopticon", "relation": "位于", "confidence": 0.7}]}
```

## #7 `d16a9868d5cbee73`　[contrib] en  复古技术
- 出处：【重返未来:1999×原子之心】联动版本 全剧情流程「聚合浪潮」- Reverse:1999｜4K（11.复古技术）

### 正文

Atropine, Benactizine, Pralidoxime...We've almost tried everything.Maybe Obadoxime?We'd have to be extremely careful with the dose.It worked!And it don't work!Just miss!God, finally!Don't celebrate yet.It could be terminal lucidity.We'll need to observe him a little longer, but...We can start preparing his antidote for the others.No more random injections.Got it?That's asking a lot for a Laplace researcher, don't you think?

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Atropine", "type": "物品", "aliases": []}, {"name": "Benactizine", "type": "物品", "aliases": []}, {"name": "Pralidoxime", "type": "物品", "aliases": []}, {"name": "Obadoxime", "type": "物品", "aliases": []}, {"name": "terminal lucidity", "type": "概念", "aliases": []}], "relations": [{"src": "Atropine", "dst": "Pralidoxime", "relation": "尝试", "confidence": 0.7}, {"src": "Benactizine", "dst": "Pralidoxime", "relation": "尝试", "confidence": 0.7}, {"src": "Obadoxime", "dst": "Pralidoxime", "relation": "考虑", "confidence": 0.7}]}
```

## #8 `13dbe6f8e93a9c07`　[contrib] en 3.0 血污与伤痕｜12.破碎的尖拱｜13.和平的价码
- 出处：《重返未来：1999》3.0版本主线「行于漫漫长路上」全剧情 - Reverse: 1999｜4K（11.血污与伤痕｜12.破碎的尖拱｜13

### 正文

It's because of the chauvinism of the telekinesis!Retreat, you monster!Shit.This heart ignites.Calm yourself, Marianne.Steady your breathing.You need not panic.This will not be the end of you.Target locked down.This is now.A sharp hit.The enemy is at peace.You shall be stamped out.I say to you, build a hidden.A sharp hit.Don't waste your time.Now is the time for a sharp hit.We fought over an apple tree

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Marianne", "type": "角色", "aliases": ["玛莉安"]}, {"name": "the chauvinism of the telekinesis", "type": "概念", "aliases": []}, {"name": "monster", "type": "概念", "aliases": []}, {"name": "heart", "type": "概念", "aliases": []}], "relations": [{"src": "Marianne", "dst": "heart", "relation": "点燃", "confidence": 0.9}, {"src": "monster", "dst": "Marianne", "relation": "针对", "confidence": 0.9}, {"src": "Marianne", "dst": "Marianne", "relation": "冷静", "confidence": 0.9}, {"src": "Marianne", "dst": "Marianne", "relation": "无需恐慌", "confidence": 0.9}]}
```

## #9 `b7a3b16729c31fa5`　[contrib] en 3.9 非正式冠军
- 出处：【重返未来：1999】3.9版本「重燃！流金之海」全剧情流程（10非正式冠军）

### 正文

My dear, is it true that you come to us from the cosmos?In the dim memories of my former life, I recall meeting with the polis' elders as they gatheredin a symposium to muse beneath the starry skies.I had just completed an escort for our merchant fleets and had returned to tellthem of my discovery.you don't understand take it it's little bother I need to free my handscitizens honored guests interlopers would you care to join me in a game a

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Madam Lucy", "type": "角色", "aliases": ["Lucy", "Lucy(Madam Lucy)"]}, {"name": "polis' elders", "type": "组织", "aliases": ["polis' elders"]}, {"name": "merchant fleets", "type": "物品", "aliases": ["merchant fleets"]}], "relations": [{"src": "Madam Lucy", "dst": "polis' elders", "relation": "前往", "confidence": 0.9}, {"src": "Madam Lucy", "dst": "merchant fleets", "relation": "完成 escort", "confidence": 0.9}]}
```

## #10 `fec6a2eacc8f4433`　[contrib] zh 3.4 「乐土」
- 出处：【重返未来：1999】3.4版本「不老春」全剧情 - Reverse: 1999｜4K 中配（10.「乐土」）

### 正文

你先获得厂商,你先获得厂商让人不学习,真是蠢好神气派好柔软的床,被子也很暖和我做了个好奇怪的梦但是睡得又特别足神劲清爽入囚以后一直都没什么精神可今天我就觉得自己可以可以差一亩低的样说不定那个跟我差不多高的大花瓶也举得起来慧姑,你醒了你…你是…露丝姐?刚才我与露丝姐在门外谈些事情听到房间内有响动便想应该是你终于醒了你现在身处梅花教内想必一定有很多疑问无妨我们慢慢来我是梅花教的掌门大家都称我人仙子你也这么跟着叫便好人仙子?你就是那个血人地血人是我长生之法又是一个初见而不知贞貌的小家伙你要找的人就在此处可并不是我当年我也是成了他的恩才习得这长生之法的可以不用这个词称呼我吗听了只觉得身上有蚂蚁在爬这到底是怎么回事你还记得昨晚的事吗昨晚在戏台上是了昨晚路思建在戏台上为你引荐釜顶做了一事之后你就睡得十分之香甜你现在感觉如何?倒是觉得神情其爽也有力气了不少我已然长生了你只是跨进了长生的门槛露丝剑初步扭转了你体内的气润

### 本地 7B 抽取结果

```json
{"entities": [{"name": "露丝姐", "type": "角色", "aliases": ["露丝"]}, {"name": "人仙子", "type": "角色", "aliases": []}, {"name": "梅花教", "type": "组织", "aliases": []}, {"name": "路思建", "type": "角色", "aliases": []}, {"name": "釜顶", "type": "角色", "aliases": []}, {"name": "血人", "type": "角色", "aliases": []}, {"name": "长生", "type": "概念", "aliases": []}], "relations": [{"src": "露丝姐", "dst": "人仙子", "relation": "是", "confidence": 0.7}, {"src": "人仙子", "dst": "梅花教", "relation": "掌门", "confidence": 0.7}, {"src": "血人", "dst": "长生", "relation": "方法", "confidence": 0.7}, {"src": "露丝姐", "dst": "路思建", "relation": "引荐", "confidence": 0.7}, {"src": "露丝姐", "dst": "釜顶", "relation": "引荐", "confidence": 0.7}]}
```

## #11 `a430623ba9ca7aaf`　[empty] en 2.6 开幕
- 出处：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（01开幕）

### 正文

It wasn't a big deal, actually.As a sign of gratitude,he explained this strange story to me.One that happened in a village in the Sonora desertcalled Amalfitano in 1975.The people there followed a very unorthodox beliefthat revolved around the Tado of Babylon.One day, a researcher with a suitcase came to the village.She came to study her local customs,A surprising reason for a rude intellectual to appear in a remote settlement in the desert.

### 本地 7B 抽取结果

```json
{"entities": [], "relations": []}
```

## #12 `233a290412cea2df`　[empty] en 3.3 赫克托尔宣言
- 出处：【重返未来：1999】3.3版本主线「远征记」全剧情 - Reverse: 1999｜4K（11赫克托尔宣言）

### 正文

frozen heart.No less clowns for their taste in uniforms, falling off their high horsesagain and again, brought down by their own arrogance.Who would have thoughtthe whole universe turned into one circus starring two troops of fools?Why didn't that blind woman just let the world burn back then?It wouldn'tbeen worse than these chaotic times.And who asked her to play the martyr anyway?If you'relucky enough to find her, take her home and make sure she stays there, quietly, for everyone's sake.

### 本地 7B 抽取结果

```json
{"entities": [], "relations": []}
```

## #13 `f56f4aeac5cfc968`　[empty] en 2.7 ~5
- 出处：《重返未来：1999》2.7版本「1987宇宙组曲」全剧情 - Reverse: 1999｜4K（1~5）

### 正文

carrying with it humanity's spirit of exploration.It is likely to persist longer than life on Earth.In our short lives, we come up with a lot of questions about the world.And we have to find the answers for ourselves.We get to choose what meaning we give to our lives.How beautiful the stars are.Take a deep breath.And relax.This is my debut.I can't fail.Not now.I have to do this for Mr.and Mrs.Kozlov and everyone in the circus.

### 本地 7B 抽取结果

```json
{"entities": [], "relations": []}
```

## #14 `58e2b8696ba87295`　[cloud18] en 3.3 时代遗物
- 出处：【重返未来：1999】3.3版本主线「远征记」全剧情 - Reverse: 1999｜4K（10时代遗物）

### 正文

Shady perhaps, but not too harmful.That project still caused harm to tourists at the Green Lake campsite and the surrounding residents.This is nothing compared to what the Ember Room did.After I joined the project, my orders were to station on the outskirts of Berogradand build a military zone to protect the underground site.At the same time, the Foundation asked for a thorough review of all soldiers

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Green Lake campsite", "type": "地点", "aliases": ["绿湖营地", "Green Lake"]}, {"name": "Ember Room", "type": "组织", "aliases": ["火光之室"]}, {"name": "Berograd", "type": "地点", "aliases": ["贝罗格", "伯格拉德"]}, {"name": "圣洛夫基金会", "type": "组织", "aliases": ["Foundation", "基金会"]}, {"name": "project", "type": "事件", "aliases": ["该项目"]}, {"name": "underground site", "type": "地点", "aliases": ["地下遗址"]}, {"name": "military zone", "type": "地点", "aliases": ["军事区"]}, {"name": "soldiers", "type": "角色", "aliases": ["士兵"]}, {"name": "tourists", "type": "角色", "aliases": ["游客", "度假者"]}], "relations": [{"src": "project", "dst": "tourists", "relation": "造成伤害", "confidence": 0.8}, {"src": "tourists", "dst": "Green Lake campsite", "relation": "位于", "confidence": 0.7}, {"src": "Ember Room", "dst": "Green Lake campsite", "relation": "破坏", "confidence": 0.6}, {"src": "soldiers", "dst": "Berograd", "relation": "驻扎", "confidence": 0.75}, {"src": "military zone", "dst": "Berograd", "relation": "位于", "confidence": 0.8}, {"src": "military zone", "dst": "underground site", "relation": "保护", "confidence": 0.8}, {"src": "圣洛夫基金会", "dst": "soldiers", "relation": "审查", "confidence": 0.8}]}
```

## #15 `3642207c78778d8b`　[cloud18] en 3.2 法兰西特快｜确保任何预言都在保质期内被及时说出。
- 出处：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（01.法兰西特快｜确保任何预言都在保质期内被及时

### 正文

Par le feu, le feu est purifié.What have you done to my crystal?Please, allow me to explain.My name is Adele Tavernier.Have you heard of us before?Les Taverniers, famed jewel hunters?The arcane skill I just used has been performed by my family for generations.We've recovered and examined all manner of treasures,including the Bourbon's own French Blue.Fire holds a certain power to reveal the true nature of what it touches.

### 本地 7B 抽取结果

```json
{"entities": [{"name": "Adele", "type": "角色", "aliases": ["阿黛尔", "Adèle Tavernier", "阿黛尔·塔文尼埃"]}, {"name": "Les Taverniers", "type": "组织", "aliases": ["塔文尼埃家族", "Tavernier family", "Tavernier"]}, {"name": "French blue", "type": "物品", "aliases": ["法兰西之蓝", "法国蓝", "French Blue"]}, {"name": "Bourbon", "type": "组织", "aliases": ["波旁家族"]}, {"name": "arcane skill", "type": "概念", "aliases": ["神秘术", "秘技"]}, {"name": "crystal", "type": "物品", "aliases": ["水晶"]}, {"name": "fire", "type": "概念", "aliases": ["火焰"]}], "relations": [{"src": "Adele", "dst": "Les Taverniers", "relation": "隶属", "confidence": 0.9}, {"src": "Adele", "dst": "arcane skill", "relation": "使用", "confidence": 0.85}, {"src": "Les Taverniers", "dst": "French blue", "relation": "寻回", "confidence": 0.85}, {"src": "Bourbon", "dst": "French blue", "relation": "持有", "confidence": 0.85}, {"src": "Adele", "dst": "crystal", "relation": "施术", "confidence": 0.7}, {"src": "fire", "dst": "crystal", "relation": "揭示本质", "confidence": 0.7}]}
```

