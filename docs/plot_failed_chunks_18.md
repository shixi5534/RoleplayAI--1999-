# 剧情图谱 18 个顽固失败块（供 WorkBuddy 云端模型重抽）

> **状态：已补齐（2026-09-07 23:0x）** — 云端模型逐块抽取结果已固化在
> `scripts/apply_failed_chunks_18.py`（`RESULTS` 字典），执行后缓存 2477/2477 全覆盖，
> 重建后图谱实体 4396→4429、边 4102→4202，`failed=0`。旧图谱备份：
> `data/knowledge/plot_graph_wu_ming_zhe.json.bak_18`。本文剩余部分仅作留档。

- 生成时间：2026-09-07T22:20:00
- 角色：wu_ming_zhe ｜ 总块数 2477 ｜ 已成功 2459 ｜ 本文件 18 块
- 失败原因：7B 本地模型（qwen2.5:7b）对这 18 块产出确定性畸形 JSON（重试无效）。
- 目标：用更强的模型逐块抽取实体/关系，写成缓存文件后回放重建。

## 缓存文件格式（每个 hash 一个文件）

```json
{"entities":[{"name":"<canonical 称呼>","type":"角色|物品|地点|组织|概念|事件","aliases":["<同指别名>"]}],"relations":[{"src":"<实体名>","dst":"<实体名>","relation":"<简短中文谓语>","confidence":0.0到1.0}]}
```

## 重建命令（写完 18 个缓存后执行）

```bash
# 项目根目录
.venv/Scripts/python.exe -c "import os;os.remove('data/knowledge/plot_graph_wu_ming_zhe.json')"
.venv/Scripts/python.exe scripts/build_plot_graph.py --character wu_ming_zhe --build-graph
```

---

## 块 1 / 18 — hash `cd2a0d92e5ec8eb9`

- 语种：**zh** ｜ 文档：`BV196ReBxEq9` ｜ 版本： ｜ 章节：
- 标题：万字解析！一口气带你串联重返未来1999全主线！ 【重返未来1999剧情解析】
- 上传者：薯条小叔叔 ｜ 发布：2026-05-05 ｜ 时长：28:06 ｜ 转写方式：whisper语音转写
- 字符数：400

**正文：**

```text
维尔汀,这从侧面印证了这个至于冠体实验的真实目的是不是找回那个人的能力拉普拉斯未来会不会加入冠体实验还需要剧情的进一步铺垫OK 快速休息一下然后开始第三条进行中的剧情线基金会的派系斗争或者说是鸽子屋的目的到底是什么这是从3.0时期开始提到名面上的一条线老虎的金黄中当时委员会的争执还仅限于基金会内部如何管控新增的编外神秘学家以佩德拉为代表的保守派认为重塑之首的崛起使得神秘学界逐渐脱离了基金会的控制所以需要把控神秘学家的思想与行为这也符合上面提到的第一防线学校存在消除记忆与统一认知的设定而以张芝芝为代表的改革派倾向于与外部神秘学家灵活合作第四章中X暗示过张芝芝来自拉普拉斯后续剧情也给出了肯定的答案那为什么来自拉普拉斯就会让张芝芝支持灵活管控神秘学家呢3.5和3.6版本的剧情就是很好的答案拉普拉斯内部有许多神秘学家他们是与后推进科技进步的关键比如续章中使用的传送软盘在1987宇宙族曲中得到了补全
```

---

## 块 2 / 18 — hash `4be44edf99ecf1ae`

- 语种：**en** ｜ 文档：`BV19KDpB5E9A_p3` ｜ 版本：3.6 ｜ 章节：《答案在盒底》别轻易接受准备好的说辞。
- 标题：【重返未来：1999】3.6版本「人们向何处去」全剧情流程（03.《答案在盒底》别轻易接受准备好的说辞。）
- 上传者：缺德的德鲁伊 ｜ 发布：2026-04-09 ｜ 时长：10:41 ｜ 转写方式：whisper语音转写
- 字符数：410

**正文：**

```text
attitude as an excuse to attack Laplace.We need to use the toy boxessimulations to create a reliable emergency protocol.Okay, I get you.Wejust need to submit something that'll shut them up.So why don't you roundup everyone who's been wasting research materials, hand them all therents ID badges, and turn them over?I did hear the foundation has beenThe vast majority of our past data has been rendered useless.
```

---

## 块 3 / 18 — hash `9f1502e7a8b945b4`

- 语种：**en** ｜ 文档：`BV19KDpB5E9A_p8` ｜ 版本：3.6 ｜ 章节：《夜间攀登者》在峰顶等待日出时分。
- 标题：【重返未来：1999】3.6版本「人们向何处去」全剧情流程（08.《夜间攀登者》在峰顶等待日出时分。）
- 上传者：缺德的德鲁伊 ｜ 发布：2026-04-09 ｜ 时长：10:38 ｜ 转写方式：whisper语音转写
- 字符数：426

**正文：**

```text
have no leads to speak of even the most skilled cryptographer can't reverseengineer a key out of thin air seems like an easy fix to me I say we takethe toy box.Ludwig and the core are both in there, right?So take it apart.Let all its elementsreset to their original states individually, then it'll be a breeze to analyze.That's tooreckless, researcher medicine pocket.Dismantling the toy box might cause significant data loss,
```

---

## 块 4 / 18 — hash `ce4f4ec5c6f6fc43`

- 语种：**en** ｜ 文档：`BV1CS9hBZETX_p24` ｜ 版本：3.7 ｜ 章节：
- 标题：【重返未来：1999】3.7版本主线「他者的悲哀」全剧情 - Reverse: 1999｜4K（13.TH.24【报偿】从谎言堆砌的迷宫中走出，寻得一份轻若无物的珍宝。）
- 上传者：缺德的德鲁伊 ｜ 发布：2026-04-30 ｜ 时长：11:37 ｜ 转写方式：whisper语音转写
- 字符数：401

**正文：**

```text
when you have time.Madam Z, is there any news about my application?Yes, the Vice President and I have spoken.Considering the sensitivity of your role in the Foundation,if you leave your post,your record here must be entirely erased.All your past achievements and contributionswill be expunged from our records,including the sacrifice you madein closing the one-way portal.That all means nothing to me.
```

---

## 块 5 / 18 — hash `ae21a0e1cacae302`

- 语种：**en** ｜ 文档：`BV1E3gD6PEck_p1` ｜ 版本： ｜ 章节：1
- 标题：【重返未来:1999×原子之心】联动版本 全剧情流程「聚合浪潮」- Reverse:1999｜4K（01）
- 上传者：缺德的德鲁伊 ｜ 发布：2026-07-23 ｜ 时长：22:43 ｜ 转写方式：whisper语音转写
- 字符数：412

**正文：**

```text
aspects of farm work.Now these farmers can use their time researching new scientific advancements, which feeds backThat much is clear.Where should I start?Oh, of course, let's start with collective.All the robots you see are controlled by the collective neural network, whichensures their labor is never wasted.Who would have thought that robots wouldbecome our closest companions?Honest, stable, graceful, calm?
```

---

## 块 6 / 18 — hash `6761b931d082cc4e`

- 语种：**en** ｜ 文档：`BV1HvWgzkE8b_p11` ｜ 版本：3.1 ｜ 章节：
- 标题：【重返未来：1999】3.1版本「长夜鸣笛」全剧情 - Reverse: 1999｜4K（11.十三号车厢(一节两节三节车，数到十三别回头。)）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-09-19 ｜ 时长：11:47 ｜ 转写方式：whisper语音转写
- 字符数：405

**正文：**

```text
I can see what you're all thinking, but it's not her.I thought perhaps it could be hiding in this carriage,but it appears I was wrong.Oh.So the stories are true.Good thing we came prepared.That vampire, it won't find us, will it?I'm willing to help you.But only if you give me some information about yourselves.After all, trust is a two-way street, right?I understand.We're refugees.We come from all over.
```

---

## 块 7 / 18 — hash `2f0402a9ed09feb7`

- 语种：**zh** ｜ 文档：`BV1iT421D7S8` ｜ 版本： ｜ 章节：
- 标题：剧情入坑必看！一年来，重返未来1999讲了一个怎样的故事？【重讲未来#0】
- 上传者：银发三千雪满头 ｜ 发布：2024-05-17 ｜ 时长：8:48 ｜ 转写方式：whisper语音转写
- 字符数：406

**正文：**

```text
两方面压力的共同作用再加上基金会上级鸽子屋的指示让基金会的保守派不得不让步维尔廷终于从人工末路中解放名声言顺地带领小队踏上抵抗暴雨的征途但要对抗暴雨这个农场猪维尔廷也只是钢铜鸡饲料进化成鸡而已仍然认真拿捏所幸,对暴雨的研究很快有了新进展事先回溯到1913年底维尔廷在对废弃的奥利陀融基地进行搜查时在一个写着维尔廷的箱子中缴获了一副重塑面具与神秘学家无限恋小姐重塑面具中发现了能抵抗暴雨的元素非对称核塑2基金会就此有了与重塑一般抵抗暴雨的希望同时,无限恋小姐争的信息暗示了一个居住在爱琴海小岛上的神秘学家组织阿派朗学派尽管发来信息的人还是一个谜但为了抵抗暴雨维尔丁小队也在一番波折后抵达了阿派朗学派唯一的代价就是新替的船又沉了只在岛上生活的阿派朗学派遵循着万物接触的神秘纪律甚至头面人物的名字都起成了数字的模样看似封闭保守却能计算与观测暴雨的发生规律还能够防护暴雨这道暴雨影响背后的现实时间 已经推进到了2007年
```

---

## 块 8 / 18 — hash `25ee52e8898f2ead`

- 语种：**en** ｜ 文档：`BV1nfmNBNELN_p10` ｜ 版本：3.3 ｜ 章节：时代遗物
- 标题：【重返未来：1999】3.3版本主线「远征记」全剧情 - Reverse: 1999｜4K（10时代遗物）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-12-11 ｜ 时长：19:49 ｜ 转写方式：whisper语音转写
- 字符数：440

**正文：**

```text
What are they so scared of?The Cavalry is here to protect them.After all the chaos, letters from the front soaring, praises, bandits.Paragrad is one thing, even afraid of its own shadow.Just like the people of Tomarovka.You didn't keep the Cavalry's orders confidential?Word always gets out.Then the citizens must know that you will soon withdraw from the Dawn.People don't understand what they cannot see with their own eyes and you cannot
```

---

## 块 9 / 18 — hash `58e2b8696ba87295`

- 语种：**en** ｜ 文档：`BV1nfmNBNELN_p10` ｜ 版本：3.3 ｜ 章节：时代遗物
- 标题：【重返未来：1999】3.3版本主线「远征记」全剧情 - Reverse: 1999｜4K（10时代遗物）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-12-11 ｜ 时长：19:49 ｜ 转写方式：whisper语音转写
- 字符数：403

**正文：**

```text
Shady perhaps, but not too harmful.That project still caused harm to tourists at the Green Lake campsite and the surrounding residents.This is nothing compared to what the Ember Room did.After I joined the project, my orders were to station on the outskirts of Berogradand build a military zone to protect the underground site.At the same time, the Foundation asked for a thorough review of all soldiers
```

---

## 块 10 / 18 — hash `d6cf5f40c8bee74e`

- 语种：**en** ｜ 文档：`BV1nfmNBNELN_p1` ｜ 版本：3.3 ｜ 章节：河岸静悄悄
- 标题：【重返未来：1999】3.3版本主线「远征记」全剧情 - Reverse: 1999｜4K（01河岸静悄悄）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-12-11 ｜ 时长：15:21 ｜ 转写方式：whisper语音转写
- 字符数：414

**正文：**

```text
Sun's beating down and we need to get the horses watered.We've gone quite a way farther than the assigned watch point.Even if we can push on, the horses can't.Never exhaust your horse.Remember.Fine.Take a break, team.And Sergei, if you shine the light of that telescope into my eyes one more time,the last thing you'll see is a missile to the face.Understood?Understood, Lieutenant.Hey, soldier.You want some more?
```

---

## 块 11 / 18 — hash `839d82e10238842c`

- 语种：**en** ｜ 文档：`BV1nfmNBNELN_p4` ｜ 版本：3.3 ｜ 章节：寂静所笼罩的
- 标题：【重返未来：1999】3.3版本主线「远征记」全剧情 - Reverse: 1999｜4K（04寂静所笼罩的）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-12-11 ｜ 时长：16:32 ｜ 转写方式：whisper语音转写
- 字符数：427

**正文：**

```text
Trust me, what she will do to you is one thing you do not want to foresee.Manus vindicti.Ah, so you can see some specifics.Well, what is your decision?No.Neither your enemy nor your ally.There's nothing I can do for you but bury the dead.Difference of opinion.Why am I surprised?You're just like the rest of them.One bad decision after another.And I am left to write their own.It seems only I can.I gave you your chance, freak.
```

---

## 块 12 / 18 — hash `a8c48a1bc81d3885`

- 语种：**zh** ｜ 文档：`BV1uekVBdETR_p21` ｜ 版本：3.4 ｜ 章节：「致此离离」
- 标题：【重返未来：1999】3.4版本「不老春」全剧情 - Reverse: 1999｜4K 中配（21.「致此离离」）
- 上传者：缺德的德鲁伊 ｜ 发布：2026-01-20 ｜ 时长：14:04 ｜ 转写方式：whisper语音转写
- 字符数：407

**正文：**

```text
百年后见面怪他会让我解开所有细节难怪城里会有疯王扰动这些细节是当年被长生剑凝制的疯就是长生之法的真相难道他从此之后就一直被封在此地他可不是你的食物终于见面了小小草因为镇法组阁的缘故让你辛苦了很高兴你看起来过得还不错你说你自会找我没想到是以这种形式见面如果我没猜错那些风还有给我指明方向的纸页应该都是你做的多亏了忘记的小把戏你应该见过很多次那场大战之后我就一直被封在这梅花树中无法与外界沟通直到几年前人们来这里拉了一些奇怪的线这些黑色的线里有走着一股股特殊的气我的神秘术可以预示他们所以才能在论坛上和你联系你是说电流和信号你的神秘术可以让你通过这些光缆连接互联网或许吧我不确定不过毕竟是受困于此这些气有时候会忽然消失这些时候我就没法看到你也没法和你交流好吧虽然我很想采访你但那估计是另一篇报道了抱歉我的时间真的很紧迫鲁思姐按照我们说好的我解开了所有风解该轮到你履行承诺给我答案了你亲口说过长生剑折断长生之法也随之断绝
```

---

## 块 13 / 18 — hash `ef77d6639051ad99`

- 语种：**zh** ｜ 文档：`BV1uekVBdETR_p21` ｜ 版本：3.4 ｜ 章节：「致此离离」
- 标题：【重返未来：1999】3.4版本「不老春」全剧情 - Reverse: 1999｜4K 中配（21.「致此离离」）
- 上传者：缺德的德鲁伊 ｜ 发布：2026-01-20 ｜ 时长：14:04 ｜ 转写方式：whisper语音转写
- 字符数：400

**正文：**

```text
小小草,在知晓了这一切后,你还会继续追寻长生吗?尽管我们的时间不过一个四季,但生命都予以了我和我的族群尽情去追求它的权力。我们乐于这样做,也勇于这样做。无论长生是真正存在,或只是一个骗局,我都不会因为未知的结果和恐惧就放弃这份追寻本身我想要活下去我想见更多未曾见过的景象写出更好的报道想成为众多炉草集中取得成功的那一个这是只属于我的生命旅程我当然也希望能延长它哪怕只是多一小时一分钟即使寻求的事物一致即使走上同一条路我的经历 我的思想我写下的报道也永远不会与谁全然相同世上有许多遗藏而我也只是我所以我仍会继续追寻长生直到抵达旅途的终点无论结局为何我都不会后悔这世上沾钱过后举棋不定的佣类太多了已经很少见你这样有志气的精官你能不昧本心这很好我没有看错人跟我念天地无极任我才亮天地无极任我才亮等到了这一天仙子不错你倒是与他们不同尚且讲几分情意还识得允诺你传法的恩人你骗我在论坛上一直联系我的人并不是陆思姐
```

---

## 块 14 / 18 — hash `28a719d8d9ef1687`

- 语种：**en** ｜ 文档：`BV1VSybBmEv3_p10` ｜ 版本：3.2 ｜ 章节：城市的癔症｜药方是一剂幻觉般的夏日午后
- 标题：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（10.城市的癔症｜药方是一剂幻觉般的夏日午后）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-10-30 ｜ 时长：14:58 ｜ 转写方式：whisper语音转写
- 字符数：449

**正文：**

```text
Did it get you?Bon sang.This is no dream.How did they get here?Is that what you meant earlier?Maybe you do have a point.At least about the Beast of Gevaudan.Here, take this.It should help with the bleeding.I can't just leave you like this.You'll have to come with me, madame.But I'm afraid I can't take you home.I must find my friends before anything happens to them.I can't just leave them wandering the city while these monsters prowl the streets.
```

---

## 块 15 / 18 — hash `e56cec89bfc0e8d2`

- 语种：**en** ｜ 文档：`BV1VSybBmEv3_p16` ｜ 版本：3.2 ｜ 章节：应许的时刻｜众生所望的国如是降临。
- 标题：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（16.应许的时刻｜众生所望的国如是降临。）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-10-30 ｜ 时长：12:23 ｜ 转写方式：whisper语音转写
- 字符数：428

**正文：**

```text
The Palace of Optics, the Eiffel Tower, the Arc de Triomphe, Notre-Dame, the Luxor Obelisk,the Lutetia Arena, the Medieval Quarters, each piece woven together in perfect harmony.As I've said, thought shapes reality.This pari, born from collective imagination, is buried at its most true and most real.Only when it fully descends shall we finally possess a real world, a life worth living.Must you hang over me like this, Roseau?
```

---

## 块 16 / 18 — hash `3642207c78778d8b`

- 语种：**en** ｜ 文档：`BV1VSybBmEv3_p1` ｜ 版本：3.2 ｜ 章节：法兰西特快｜确保任何预言都在保质期内被及时说出。
- 标题：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（01.法兰西特快｜确保任何预言都在保质期内被及时说出。）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-10-30 ｜ 时长：20:46 ｜ 转写方式：whisper语音转写
- 字符数：425

**正文：**

```text
Par le feu, le feu est purifié.What have you done to my crystal?Please, allow me to explain.My name is Adele Tavernier.Have you heard of us before?Les Taverniers, famed jewel hunters?The arcane skill I just used has been performed by my family for generations.We've recovered and examined all manner of treasures,including the Bourbon's own French Blue.Fire holds a certain power to reveal the true nature of what it touches.
```

---

## 块 17 / 18 — hash `cbd85d3c306f0f3a`

- 语种：**en** ｜ 文档：`BV1VSybBmEv3_p1` ｜ 版本：3.2 ｜ 章节：法兰西特快｜确保任何预言都在保质期内被及时说出。
- 标题：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（01.法兰西特快｜确保任何预言都在保质期内被及时说出。）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-10-30 ｜ 时长：20:46 ｜ 转写方式：whisper语音转写
- 字符数：411

**正文：**

```text
Things might have gone quite differently, no?My arcane skill would have spoken volumes about your integrity.This is close enough, close enough for me to clearly see the shadow upon you.Pardon?A tavernier girl, the youngest and brightest, brimming with vitality.The fated one has stepped onto her path.Twice will she collide with destiny.Once risen, once descended, for a fate left vacant now shall be fulfilled.
```

---

## 块 18 / 18 — hash `3ff8f4686693eda9`

- 语种：**en** ｜ 文档：`BV1VSybBmEv3_p8` ｜ 版本：3.2 ｜ 章节：法兰西之蓝｜有言称，历史是无尽的回环。
- 标题：【重返未来：1999】3.2版本「迁流的盛宴」全剧情 - Reverse: 1999｜4K（08.法兰西之蓝｜有言称，历史是无尽的回环。）
- 上传者：缺德的德鲁伊 ｜ 发布：2025-10-30 ｜ 时长：11:11 ｜ 转写方式：whisper语音转写
- 字符数：406

**正文：**

```text
on its descent through four primary spiritual worlds.Everything we see is a mere manifestation of its true form.If destroyed in this world, it will yet persist in the spiritual world.So long as the idea of it remains, it may return to the world of matter through an emanation of Numa.Perhaps this diamond in your hand is the idea of it, manifested for a second time.But how?All I did was see it in a dream.
```

---
