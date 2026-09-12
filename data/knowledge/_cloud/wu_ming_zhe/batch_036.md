# 剧情图谱抽取 · batch 036

- 角色：`wu_ming_zhe`
- 批次：**36** / 共 1 批（每批 25 块）｜本批块数：**23**
- 筛选：标题含「1.4」｜offset 475
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_036.jsonl`

## 硬约束（违反即被 `--apply` 丢弃，且**不报错**——产出即静默消失）

1. `type` 只能是以下 7 类之一：角色 / 组织 / 地点 / 概念 / 物品 / 事件 / 时间。
   越界一律回落 `概念`。
2. `relation` 必须命中下方受控词表（77 条）。
   否定的、含拉丁字母的、超过 8 个字的谓语一律丢弃。
3. `src` / `dst` 必须是**本块内某个实体的 name 或 alias**，
   不能引用块外实体，不能用代词泛指。
4. 禁止自环：`src` 与 `dst` 不能是同一个实体，**同一实体的正名与别名之间、别名与别名之间也算自环**。
   例：若本块实体是「无名者」（别名含 凯拉 / Ms. Stranger），则 `凯拉 → Ms. Stranger` 会被建图判为自环静默丢弃。
5. 禁止把 you / she / he / we / they / 她 / 他 / 我们 等代词当实体正名。
6. 只抽取**文本里明确说了**的关系，不要脑补、不要补背景知识。
   拿不准就留空 relations，宁缺毋滥。
7. 机器转写有识别错误：同一角色的不同拼写（ASR 变体）请收进 `aliases`，
   不要新建重复实体。

## 受控词表（77 条）

是、别名、称呼、隶属、担任、象征、转变、包含、位于、前往、离开、返回、来自、居住、连接、持有、使用、获得、给予、制造、摧毁、修复、封印、亲属、同伴、指导、保护、帮助、信任、怀疑、感谢、背叛、对立、对抗、攻击、杀死、击败、威胁、阻止、追踪、隐藏、知晓、发现、寻找、研究、学习、告知、提及、记载、询问、对话、请求、指挥、命令、派遣、服从、依据、许可、发动、参与、关联、导致、遇见、经历、发生于、约定、计划、预言、影响、控制、需要、免疫、希望、等待、关注、警告、指责

## 输出格式

写一个 `batch_<N>.jsonl`，**每行一个 JSON 对象**，顺序与下方 chunk 一致，
并且**必须原样带回每个 chunk 的 hash**（写错 hash 会导致结果写进错误的缓存槽）。

```json
{"hash":"<16位hash>","entities":[{"name":"规范称呼","type":"角色","aliases":["曾用名/代称/昵称"]}],"relations":[{"src":"A","dst":"B","relation":"隶属","confidence":0.9}]}
```

`confidence` 取值 0.0–1.0，只在你**确信**文本明确表达了该关系时给到 0.8 以上。
低于 0.55 的边建图时会被 `min_confidence` 直接拒收。

## chunks

### [0] hash=`42423b073ca86ae3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
This is also true between those who have enough food to eat and those who are starving.Alright, that's it.I've talked enough.Now get up, darling, and brush the sand off yourself.Trust me, you will find your own answer to this error.
```

### [1] hash=`fd19167f2a622643`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Yes, all is well.Those dolphins sent us to the other side of the currents.And one more thing, Captain, and I'm asking this with no ill intention.Uh, may I know your lineage?Thank you.I wish your next mission would be trouble-free too.The members of the Razor Squad are all humans.It's clear then.Real numbers refer to Arcanists, and imaginary numbers mean humans.Then what is the rest of this nonsense?
```

### [2] hash=`69f0cb952612d12d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Seneto, Vertin and this apple are integers.While Miss Lillia and I are fractions.Don't bother asking, I'm pure blood.This apple is also made of pure apple juice.I only consume 1.5 volt DC.So it's not determined by our lineage, or Regulus would have been an integer too.Am I the irrational number?Might as well play us some rock music.Seems the residents on this island venerate integer numbers.And irrational numbers, or the non-terminating, non-repeating decimals, cannot be represented
```

### [3] hash=`bfb051a16a27a593`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
as the ratio of two integers, hence they are discriminated.No, no, no!Who are they to judge and decide me to be the irrational number?I was the only person who didn't cause any damage to the Foundation in the previousprotest!Why do I get to have the worst of both worlds?I've requested information from Ms.Moson about a Pyrron, but it will take some timefor the files to come in.The captain of the Razor Special Operations Squad told me this might be a settlement
```

### [4] hash=`d3adc80ab3a7c968`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
of a group of Arcanus who have been long cut off from the world.Unlike other unregistered Arcanus, these people chose not to live alongside thehumans.They still lead an ancient Arcanus way of life and follow the old customs.The travel notes in 1999, Manus Vindicte showing up in a Littial's base, the storm, or emanation,they must be somehow connected.And we'll find our answer here, I think.Very energetic, Captain.
```

### [5] hash=`456b95158ab48375`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
By the way, how come nobody is here to welcome us?They wouldn't suddenly decide to detain us all just because we have an irrational number here, right?I'm with you all the time.The biggest, worst, and ugliest crime.People eating beans will never transmigrate.They deserve nothing but eternal punishment.Serious?This rule only for soybeans?What about broad beans?Snow peas?Chickpeas?And what does it say about other bean-based products?
```

### [6] hash=`61b9ab9e71d3c67a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Beans are beans.You're funny.This doesn't even make sense.By this logic, aren't the coffee drinkers going to rot in hell?I happen to have a box of coffee beans in my bag.If I put one coffee bean in my mouth, will the vulture get me right away?No way!Whoa, easy mate!Do you want to get physical?This pirate is not scared of you!The critters are coming to your aid!This is not good.We need to separate them.
```

### [7] hash=`1ebecf40a743312a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Martin!Sunetto!Lily!What is going on here?37, let go of the guest's head.Now sorry that I'm late.I'm Sophia the corrector of a p-run.I will take over from here.OhFinally we have an ordinary person herePlease let's talk on the way to the outside
```

### [8] hash=`788ec6e67459a9c6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
We believe everything can be translated into numbers.Things are made up of numbers, and mathematics is the key to opening the gate of truth.It is like the fire that lifts us from the darkness.This world may decay in time, but numbers will transcend the limit placed for all otherthings in existence.And if one can take up the challenges, and improve oneself with practice, they mayPlease repeat all the taboos on the island.
```

### [9] hash=`a68731391da7a9c9`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
It was too dark in there.I didn't take them all downWorry not mr.Netto.I have them all recordedoneabstain from beanstoDo not pick up what has fallenthreetouch not a white roosterforDo not poke the fire with swordsfiveDo not jump over a crossbarlike you.You are a very typical irrational number.Irrational numbers aredisobedient, sometimes unreasonable, and they hardly play by any rules.Just likethe non-terminating random numbers following its decimal.
```

### [10] hash=`4debe80f7cbeaa75`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
These numbers arethe floating points, or the noises.People of this type are the random oneswhose actions show no pattern whatsoever.Disobedient, unreasonable, neverOh, it's you again!I won't be bettered in a fight this time!Thirty-seven?Shouldn't you be off preparing for the doctrinal meeting?Vix asks me to take care of our guests.But I'm usually the one who receives the guests.Engaging with strangers might be a little difficult for you.
```

### [11] hash=`3751a905bdcb3a88`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
There's no cause or link in these two events.People always bother you with trifles only because you're fine with it.Do not sleep on a grave, and do not cut wood on a main road.Idleness is the cause of the breakage of one's flesh and soul in the long journey of perfecting oneself.Those who have not yet found their numbers have even fewer excuses to be indolent.Besides, why would you place the head of a ghast in your mouth?
```

### [12] hash=`1255b38d797dce14`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
She said she's going to eat beans.That does not justify your action.Conspiring to my face to throw me in the sea.Mind you, this pirate's tolerance has limits!Right in the bull's eye.What's that look on your face is?An eye for an eye, a tooth for a tooth.I didn't start this.Regulus, did you just pick up the grape that 37 threw at you earlier from the ground?Did you just...violate the rule of not to pick up what has fallen?
```

### [13] hash=`3c3d3d710c3f44a8`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
What?A Braxxus incoming!It will take the offenders with it!A chicken's head and two snakes as a feat!What?What on earth is that?This is not good.They seem dangerous.Regulus, come to my side!Who dare you?Regulus!Captain!I can't leave her alone.This apple shall follow her.A toast to Regulus, to her ever-fighting spirit of breaking away from jails, no matter howmany times she has been put behind bars.
```

### [14] hash=`d48861f2d77f4a02`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
Luckily she didn't have any beans.May her soul be cleansed in the dungeon.What a mess.Ena eftagramot mima, simatizate otan enosume dio semia.The arcane skills cast by the congregation on this island are very different from
```

### [15] hash=`82396138054ead51`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
Before you enter the Great Hall, please place your right palm on the stone and swear toit solemnly.I wish to be baptized in the water of Gnosis and be rid of the long darkness of ignorance.I ask my tongue to be taken, for it has spoken mindless words and I shall stay silentfor the truth.I choose to leave the fragments of matters behind me and enter the Great Hall ofas clean as a newborn.I swear to let matters stay in the world of matter and
```

### [16] hash=`10f11d343ed1476e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
a form in the world of forms.I swear to reveal no secrets or my heart shall betaken by the vulture, my body consumed in flames, my soul trapped in the endlesswheel of birth.Now knock three times on the stone, put on these ceremonialVertin, are we really going to do this?That oath we have to make to enter the hall sounds vicious.To stay quiet and keep the secrets.It's similar to the training we once received.
```

### [17] hash=`f3b0e4b21097dc9c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
I can go inside on behalf of Timekeeper.No, I'll come with you Seneto.I can't sense any sign of arcane skill on this stone.The oath is more of a formality than a curse.The warning is lifted then?But when Sophia repaired the floor in front of us with her arcane skill, there's no fluctuationof arcane power either.I can't even sense the slightest signs.It's either a kind of arcane skills we're not able to detect.
```

### [18] hash=`ffc58945e7651c62`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
The moment we stepped onto this island, we've been trapped in a tremendous ritual.That's to say, any Arcanum used on this island is only a part of this giant flow.We don't know where this flow is leading us.We know nothing about it.It's too perilous, Timekeeper.I know, Zanetto.But as long as we obey their rules,we won't get into other trouble.The doctrine of the Aperon is to live in solitudeand seek nothing but the truth.
```

### [19] hash=`6f549f2af1a655ee`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
In fact, they've never beenaggressive towards us.I think of this differently.Think.The pure-blood Arcanist community,the unknown Arcanum power,and the obsessionwith certain knowledge or identity sound familiar yet we haven't spotted anytraces of the manners here Maynus vindicte is like the rat living in thegutter I don't think they will let go such a favorable chance which means weneed to find out the truth I believe in timekeeper I have zero interest in
```

### [20] hash=`4bd057ae0bf26561`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
this meeting I'll stay outside to keep a lookout take care I wish to beLast was the loss of the grand unification of different lineages.The truth was buried, and history was rewritten.But the emanation is not a crisis.Instead, it's our last salvation.The supreme existence has once again shown itself to us.The door to the everlasting, transcendent world of forms has opened once again.As Numa pours down, things are rewound to the World of Light.
```

### [21] hash=`d3f728f5011b353e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
Everything in the World of Matter breaks into pieces, for they are as delicate as a petal before it.We, who have the honor to witness the emanation of Numa, have the privilege to survive the turning of the Wheel of Birth.Because we know the truth, our survival is destined.It is the beginning of a mission to bring the unseen truth into this world.Thank you.The next orator is 37.Our smallest irregular prime and the brightest star of Hermes.
```

### [22] hash=`01283d3bcb306122`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
The emanation in 1929 only lasted for two days.All methods to calculate the Numa emanation failed.We found no pattern in the occurrence of time reversal.All our efforts in the past four years have gone completely wasted.That's the end of my speech.Reña sereno, intenso e infinito.Who did that?Who broke the silence?Sorry, Timekeeper.I just...Get ready to run, Snetto.The Abrepsises are coming.You want to offer your seat to the senior?

How dare you?Right wind.
```

