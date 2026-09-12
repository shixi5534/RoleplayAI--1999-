# 剧情图谱抽取 · batch 093

- 角色：`wu_ming_zhe`
- 批次：**93** / 共 1 批（每批 95 块）｜本批块数：**17**
- 筛选：标题含「2.3」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_093.jsonl`

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

### [0] hash=`a370ff2cf4111e9d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
So, you do remember it.Every word, our God can only hear the most faithful prayers.Yes, only the most faithful.You must offer everything you have to Him.Your heart, your flesh, from here to here.If you can't do that, you'll be surpassed and never win the attention of our God.By not enough, I mean it's imperfect.Unfaithful!Our God won't hear you!Are you unwilling to try a better element, or simply unable to?
```

### [1] hash=`2006b034a90ebed4`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Oh, please.I can do any element without even trying.Then show it to our God!I've got it.Stop nagging me.Hmph.I suppose I got carried away.This applause isn't for me, but it should be.Must have been that graceful element that Caroline finished perfectly.She had it down to the smallest detail.In that way, we were like, sticklers for detail.That's why...Thank you.Thank you, everyone.I'm feeling so...
```

### [2] hash=`baef04b7d9766da8`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
restless.Player number 2407, Anna Smith, please enter the field.What did you think, Charlotte?Well, you certainly haven't skimped on your training these past years.That's it?You're better than when you were nine.I'll give you that.But are you sure you saw my performance clearly?His smog's rather heavy.Flutter page.Miss Tooth Fairy!Mr Brimley!Good timing!Just in time, eh?Well, we wouldn't want to miss Miss Willow's performance now, would we?
```

### [3] hash=`b9f0bbab289e6c99`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
The lady doing her routine right now is called Anna.It should be Miss Willow next.I can hardly see a thingTrue.The smog's too heavyHopefully it'll clear before Miss Willow comes outWhat's wrong?Whoa, she's stooped.I think she's requesting a timeout aTimeout is she her?Silence, please an announcement from the floor ritual judges due toboth measurePlayer number 2407, Anna Smith, requested suspension after discussion.
```

### [4] hash=`fd241e7cd01c0927`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
The judges have decided to suspend the game.Willow, will she not get to compete?Suspended?We gave everything to hold these games.How could she just back out like this?I heard that a winged key archery player got injured.Maybe that's why.What, so we're supposed to just leave?The games have hardly begun.Ms.Toothberry, what should we do?Ms.Willow is next.It'll be such a shame if she can't play.Did you hear that?
```

### [5] hash=`71d738164a6e5a98`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
The games have been suspended.Yes.I suppose we should head home and wait for the notice.Maybe the games will continue once the smog clears.What?Go home and spit in the faces of everyone who worked so hard to make this happen?Huh?No.Halest yellow turns to godly light.The sun births shadows.The moon shines bright.Luch, reborn from dark's embrace.I walk your path in sacred space.Life's end is death, but bones to life ascend.
```

### [6] hash=`c1d73c23b4a50670`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Luch, before me, from underworld I wend.Luch, gaze on me, I rise from shadows dark.Luch, heed me, your power impart, as you are me and I your counterpart.The smoke is clearing!Everyone, come back!The games are on again!There's something there.Fear in the smoke!Activated.Looks like it's in pain, like an earthworm squirming and writhing before it dies.It certainly had a violent reaction to Miss Willow.
```

### [7] hash=`55acf2f877880d3d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Could it be that her ritual holds some power that suppresses the Black Fog?Told you that Miss Willow was the best match of them all!This is no time for chit chat.We need to stop the damn thing.Otherwise it'll destroy this place, just like it did the hospital.Arthur, get the crowd out of here!Damage.No, damage.Who won?It's generating a new body.Copy my bow, ain't it?I don't think so, little tacker.
```

### [8] hash=`d7f33284c5861cd1`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
They're just heads of coal.Don't give up, Willow!Why are there still civilians here?They want to help.Come on, everyone, let's dance with Willow.Follow her lead.Flowers bear fruit, and beasts give offsprings way.With eyes of fire, hit through the Cloudy Maze!Hit through the Cloudy Maze!Alright you filthy little thing, it's time you learnt a lesson.You are under arrest for the pollution of the sky as well as 15 crimes in violation of the Public Health Act.
```

### [9] hash=`69512cd421668773`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Take a good look around, because before long, you'll be rotting behind bars.It may be broken, but it's still an air purifier.That's all from me.Thank you for watching.Come in.Madam Z, here's the report from my mission.It seems you've been busy too.Even though we've confirmed connection between societal turbulence and the storm,there is no time to catch a breath.Once chaos breaks, it will be the end of another era.
```

### [10] hash=`ea8dbb1a27bbab5e`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
But we can't resist the inevitable.All we can do is maintain order,to postpone it as long as possible.So, any findings in London?A Volpergus's tooth from the Black Fog, and the last baby tooth of a child.Very rare, even for my collection.Right, that's good to know.I heard the London branch is still trying to replicate the ritual that was carriedout at the exhibition games.Well, what's that?It was a coincidence, actually.
```

### [11] hash=`cd8e3be4b4d7a062`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
After analyzing the live sample provided by Mr.Fog, the London branch concludedthat the Volpergus is a mutant of the Kaharith, a critter species that's been extinct forcenturies.Ms.Willow lent one of her heirlooms to the London branch after the games, a book thatdetails an ancient ritual meant to worship the God of the Sun.This is the ritual she performed on the floor, but when Ms.Willow performed the
```

### [12] hash=`cd4b779d3d1db0d8`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
ritual again in front of the Volpergus, nothing happened.My guess is that, since the Kaharith disappeared, the ritual fell out of use and became fragmentedover the years.Her version of it is probably incomplete.The conditions must have happened to align at that moment to allow the ritual to work.It could have been any combination of things.Miss Willow's dancing, the music from the didgeridoo wood, the fire from the torch,
```

### [13] hash=`65ccf8f7a9080ebe`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
the magnetic fields around the stadium, or perhaps it was all of them.The ritual also happened to have the power to capture the Volpergas, which put an endto the heavy smog in London.It makes sense, really, that a ritual used to worship the god of the sun would capturea monster that covers the sky and plunges everyone into darkness.In conclusion, the ritual's success was a near-unrepeatable coincidence.
```

### [14] hash=`f5e465d5b4cb96d6`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
An endangered critter and a long forgotten ritual.I guess that's why humans are always sifting through their past.There's always wisdom to be found in history.It's gone bitter.I should've finished it earlier.By the way, I've approved your vacation request.No one should disturb you this time.Thank you.Have a good day.Milk candy makes me miss the rabbit candy back home.Well, at least it goes with the tea.
```

### [15] hash=`a9b0e52af98aa2be`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Hmph.I suppose your flying does come in handy after all.Pedal with you!No, this is proof enough.Pedals for the winner of the qualifiers!Oh please, they're just qualifiers.Who's that, I wonder?What happened to the garden?It's beautiful!Ms Willows put a lot of care into it ever since she won first place in the qualifiers.Ah, Charlotte.Ever predictable.What are you doing here?We want to invite you to join us.
```

### [16] hash=`6543289b0c7f00e7`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Let's go to Australia together.With Caroline too?For your information, Charlotte, the top three athletes all qualify for the finals.And besides, I might have beaten you if you weren't so lucky as to capture that Volpergus.By the way, the ship we're taking is owned by the Bartley family.What?So, Ms.Bartley said she'd arrange a presidential suite for us.For presidents?It seems we'll be spending quite some time together in the coming weeks.

Which one of us is a president?Spie, shut your mouth.Don't scare me anymore.
```

