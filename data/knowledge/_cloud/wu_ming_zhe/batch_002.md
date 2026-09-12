# 剧情图谱抽取 · batch 002

- 角色：`wu_ming_zhe`
- 批次：**2** / 共 8 批（每批 40 块）｜本批块数：**40**
- 筛选：标题含「77号往事」
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_002.jsonl`

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

### [0] hash=`384f8a92faa3e59b`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Toy?You know, it ain't my style to point a gun at an unarmed person.But sometimes you gotta do what you gotta do.Especially when they're speaking with a forked tongue.Five.How hungry, how high I envy the likes of you, you can store your food in so many ways, you have enough bread and water in your barns to last an entire winter, your pastures are full of meats and dairy products, but my food,I promise all I'm trying to do is get back what I lost.
```

### [1] hash=`024ce4f81d577045`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
There's no need to be afraid, we won't hurt you, as long as you tell me the name of your partner.If I tell you her name, will you let me go?That depends on your sincerity.She's called Miss Grace.What's your purpose here?I don't know.People in Black told me to follow Miss Grace's orders, but she hasn't asked me to do anything since we got here.She must be hiding something from me.Careless!I want to eat!
```

### [2] hash=`04faa5d7addc1dbf`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
You annoying little brats can catch me in your dreams!She's casting a teleport ritual.Argus!Your assistants!We can't let her get away!She disappeared fast.At least now we can draw some conclusions.Manus Vindictae has set their eyes on this motel.Under the name of the Order of Enlightenment, they used this place as a baseand conducted some failed ritual experiments before they left.Manus Vindictae.
```

### [3] hash=`4789eb431ba661af`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
I've heard of them.That infamous group of Arcanists.Oh, but how annoying that these moths keep fluttering around.Cut the crap, lady.Where's Vertan?Take me to her.I rarely turn on this light.My baby never gets lost, you see.But a young, spirited child such as yourselfalways needs a light to lead the way.Am I right?To the weary traveler,as light as a shelter,They've scribbled all over the place and made a mess of the rooms.
```

### [4] hash=`cea4bc8fc0b0f3ab`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
They hurt my baby.Oh, my poor baby.Don't be scared.Everything's alright now.Are they still here?Of course.They made an offer that I couldn't refuse.After all...How much did they pay you?You are naive, my sweet child.There are countless things in this world that money can't buy.A traveler can't buy the sudden appearance of a hotel at just the right time.A crying child can't buy the comforting embrace of their mother.
```

### [5] hash=`d89c497a67972086`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
And I can't buy that thrilling satisfaction brought by sweet darkness.Enough of your endless rambling.I can't waste any more time talking to you.I can't.Sleep does leave everything to the adults.Yes.What a good child you are.
```

### [6] hash=`568cbec3ceb009df`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Found his medication prescription, and oh, is this his notebook?Huh, just as expected boss.This motel ain't what it seems to be.Ain't no way that letter was written by Stefan.Take a look.The writing in this letter is delicate and slender, while the writing in this notebook is total chicken scratch.Even a blind person could tell they're written by two different people.Stefan didn't write the letter, so it's very likely that the person who sent it wasn't Stefan either.
```

### [7] hash=`4b9d6c0c3af3d868`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
And this?I hate numbers.I'll leave this one to you, boss.It appears to be Mr.Stefan's records of his daily expenses, along with some notes, cigarettes, alcohol, and a significant amount of psychiatric medication.It says, he was tormented by his hallucinations day after day, so he had to increase his dosage.And it says he saw room numbered 707 here.The motel only has two floors, there can't be a room starting with seven, did he describe
```

### [8] hash=`64dafc4c7c9b0b01`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
it at all?He said, the room had a bright red door that seemed completely out of place.Maybe it was just one of his hallucinations.No, it's not that.He also saw all kinds of things, a pair of twins in the hallway, long hair hanging fromthe ceiling and…he saw Barbara, but assumed she was another hallucination.This proves that Barbara's been to the motel, which means…I'm sorry to say that I've never met an Arcanist with the head of a sheep.
```

### [9] hash=`e838243cbe2975de`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
I can help you ask around if you…Why did she lie to me?So did you find anything useful from the expense record?This distorted reflection in the mirror is probably a result of the excessive arcanum in this motel.A ritual similar to Bloody Mary used to be quite popular among the kids in this town.If you look into a mirror at exactly midnight, the spirit within will morph into the shape of the person you desire most.
```

### [10] hash=`434b751b2ec95f53`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
But if you respond to the spirit's call, it will drain your soul from your body.I always thought those were just myths.So did I.But after all the strange things I've seen, I've become less surprised.These spirits feed on the energy of our souls.That's why you should never trust a word they say.The people who are tricked by them fall into a kind of trance, and some, like Mr.Stefan, go crazy.I wonder what he saw in the mirror.
```

### [11] hash=`1b548f660b3d31ea`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Anyway, I won't repeat his mistake.For mercs like me, the deepest despair ain't external danger, it's internal hesitation.If some pale imitation makes me hesitate so easily, then how can I claim to be ableto protect others?You've got to be able to stand your ground.A cunning criminal would use every excuse to defend themselves in court, and a schemingby would wear all kinds of disguises to gather information on the enemy.
```

### [12] hash=`2da2226f82152ea5`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
That's why we'vegot to stay sharp.When it comes down to it, we only have our own two legs to stand on.Mercs ain't philosophers.Once a merc starts pondering morals, justice, and ethics, they'redigging their own grave.For a merc, the mission objective is the only thing thatmatters.Overthinking don't bring nothing but disaster and destruction.That's why she,no, it, won't fool me.The folks on the ranch adored little Kayla.
```

### [13] hash=`636bfbc6436d2f04`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
She was the apple of all their eyes.Howdare this ugly imitation.So, here's my response.Let this serve as a reminder to remain vigilant.If there were a deceitful spiritof the year award, I'm sure that would win.Stefan Garcia, a Xeno captain, 36 years old.For unknown reasons, likely connected to Manus Vindicte,he moved into this motel.He attempted to make contact with Xeno several times,all of which failed.
```

### [14] hash=`0ccb69d5b1f8c83f`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
During his stay, he was torturedby increasingly intense hallucinations,delusion and fear.And as a result...As a result, he committed suicide.And that's everything the evidence shows.No.We must have overlooked something.A military officer killing himself.A phone call asking for help in Morse code.Not to mention Manus Vindicte.Where's this going, boss?We've encountered a series of bizarre events.One after another, ever since we arrived at this motel.
```

### [15] hash=`5bb5a29508f82e15`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
The rituals in the rooms.The officer that went mad.the spirit in the mirror, and Manus Vendicti.Only one person remains uninvolved.Are you trying to say that she's the mastermind behind all this?She should know more about all this than anyone.Yet she feigns ignorance at every turn,which is suspicious in its own right.But what's there for a motel housekeeper to gain from all this?It's not like these spooky scandals would attract more guests.
```

### [16] hash=`788243086af8f273`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Unless someone else is pulling the strings.But that don't make much sense either, does it?When all these unusual things happened, she was happy to stand by and watch.But by whose orders?Some larger, more mysterious organization?Gimme a break.What if she doesn't desire money or power?So what you're saying is that you need to ask Little Miss Maid a couple morequestions.Precisely.That spirit morphed into Kayla, so it must have seen her face at some point, which means
```

### [17] hash=`0a895790825e7c85`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
that at one time, Kayla was in this room.And you're right, Tuesday's definitely not a run-of-the-mill motel maid.It wouldn't be wise to approach her rashly.Let me finish up here first, then we can go question her together.Alright.I got nothing.Let's go find that maid.eerie rumours centered around the motel these past few months.Yes, we've encountered some bizarre events here, like real life urban legends.
```

### [18] hash=`cf8202356e321c40`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Second, I'm now trapped in a red room.This room isn't the same motel as yours.What's different is that it blocks all forms of communication.I couldn't get the room to open, and my voice didn't reach through the phone.That was until a gunshot broke this intangible restraint.This small room contracted violently, and now I can communicate with the outside world.I thought it was an earthquake, but the contracted space soon returned to normal.
```

### [19] hash=`b8577226189268bd`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Can't do that.Can they?Before this happened, were you using spiders to communicate with the world outside?As luck would have it, there are many spiders here.Thanks to the prevalence of spiders in urban legends, I assume.There's some paranoia about spiders living in hair.It originated in a sermon from 13th century England.A woman was always late to mass because she spent too much time styling her hair.
```

### [20] hash=`f3ef3150dd98ec25`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Eventually, a devil attached itself to her hair in the form of a spider.Yes, they delivered messages for me in their own peculiar way.Being completely isolated from the outside world greatly unsettled me.It reminded me of that terrible phenomenon.Fortunately, that wasn't the case.But you're still trapped in that room, right?Yes, the door's gone.I can't get out from the inside.How did you get in there in the first place?
```

### [21] hash=`8e1eed821e0bdc58`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Or rather, who brought you into that room?Well, who else could it be?Tuesday.Just as I expected.Wait...You're the driver who left me on the road, right?Yeah, it's me.I actually changed my mind and turned back to get you but you weregone by the time I arrived.I guess that's when you came to thismotel, right?Tuesday saw me and invited me here.Oh.Did you want to ask mesomething?Have you seen a girl of about five foot three here in a white
```

### [22] hash=`4cee867da1e2332b`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Heh, that'd be a memorable way to go.Alright, enough kidding around.The little miss May tried so very hard to hide Barbara from us, but I guess the lamb'sout of the bag now.Yes, it's all crystal clear now.Let's go.Hold up a sec, boss.Do you have any candies?I'm running on fumes here, and I ain't got no way to replenish my stash.Us and Barbara will be out of here soon, and you'll find some candy and Kyler in town.
```

### [23] hash=`1d907fe946930450`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Are you not satisfied with my services?No matter what, you shouldn't have cut the phone off, nor should you have isolated mefrom the outside world, because you should know better than anyone what that means.Why should I?All I know is that a poor, helpless child like you shouldn't be alone on the roadside.But my father found it unacceptable to think his eldest son would read those softies magazines
```

### [24] hash=`f023f8b8ffa1c0e1`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
instead of working on the farm.Fashion, trends, disco, these aren't things a Texan man should pursue, at least accordingto my father.In the end, my father destroyed all my brother's disco records, along with his plane ticketto Los Angeles.Perhaps that's for the best.He avoided the riots.Huh?Nothing.So, what do you think?Me?Why should I have any opinion?Let me rephrase that.What impact has this had on you?
```

### [25] hash=`b2064035a1dc75c2`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
What happened between them has nothing to do with me, does it?These were the choices they made.When I first arrived, a local resident told me not to stay at Tuesday's Motel.He said his aunt went mad soon after she stayed here.Remember that lady?Her head was so large.It reminded me of those stories of people with deformities.So I had her watch a freak show at midnight.Sadly, she didn't seem to enjoy it.
```

### [26] hash=`f5ed2e813392c26e`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
At this time of year, the farmers run their combine harvesters on the fields non-stop.The harvest is a joyful time of year,But the accompanying noise always frightens the children.Have you heard the stories of how naughty children get too close to harvesters and getcaught in them, losing a hand or even a head, fields, machinery, children with severedlimbs?These stories are exactly what my motel's missing.
```

### [27] hash=`080da2d86363da7e`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
My baby's calling, please excuse me.I don't want another temper tantrum on my hands.Apologies, my fluffy little child.I look forward to our next conversation.Talking to you always brings me inspiration.But the motel's been too busy lately.It's starting to get on my nerves.See, this is what I mean.How could I bear to send you out on your own?You'll stay right here in this cozy little room until you're fully recovered.
```

### [28] hash=`5d99146d77c0693f`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
I don't need this special treatment of yours, staying here won't cure my illness.Just get some sleep, you'll come to your senses after a good rest.I'll see you soon, many times have I told you not to eat things off the floor my sweetheart.Is this the spot?Sure is shootin'.Look, these footprints, they're less than 10 minutes old.But where's the door to room 707?I can sense some energy fluctuations nearby, but they're definitely not from arcane skills.
```

### [29] hash=`cf634d53d2b3e75b`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Elves could produce such intense energy.Oh, can I help you with something?Ms.Tuesday, I've got a question for you.Do you know how to get to room 707?707?yep what I've been looking for might just be in that room hmm I'm usuallymore than happy to satisfy the requests of my guests as long as it's within mypower but this one crosses the line shame looks like negotiations are overand thence we came forth to see again the stars use an arcane skill so
```

### [30] hash=`442278767af649b9`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
You rely far too much on Picarasma Candy.It can't solve all your problems.They usually work wonders for me.Just one candy restores 50% of my vision.But in my line of work, 50% is never enough.That's why I take two.I need my vision to be at least 100%.That'll do the job most of the time, but sometimes I've got an extremely challenging task.that's when I eat a third candy at that point it's getting extremely dangerous I
```

### [31] hash=`1b27c89f672422d1`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
should be able to see now should I take more absolutely not the large amount ofcandy you've eaten is exactly why your eyes have failed you and in such acrucial moment no less excess leads to destruction this is true for all thingsYou do well to learn your limits.What?Also had to be careful not to frighten those children too much.You've always put your faith in these candies, haven't you?One candy, fifty percent recovery.
```

### [32] hash=`933ab5e26e2a260d`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Two candies, one hundred percent.Three candies.And you can tackle even the most insurmountable problem.Oh, how dependable they are.Just like the venerable Argus, who succeeds in any job she takes on.It's precisely your excessive confidence in these candies that has led to your marvelousdestruction.Just as the people's trust in you as a mercenary has led you to this bottomless abyss.Oh, you poor thing.
```

### [33] hash=`19bf49f59db0274f`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
And of course, they'd never have imagined this.Argus.The mercenary named after the hundred-eyed, all-seeing giant is, in fact, a blind fool.How are you?There you go.The way you can miss.But do you have the guts to pull the trigger?The decision's yours to make.But once I'm dead, you'll never find room 707.Barbara.Kayla.Everything you're looking for is all in that room, isn't it?Don't you dare say her name with that filthy mouth!
```

### [34] hash=`1db8929a7fca0c8e`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
But why?Miss Kayla's such a lovely guest.I very much enjoyed her company.Enough.You and I need to have a serious talk.Oh, there's no need for that.Actually, my baby's eager to meet you.Your...baby?Yes.In fact, the baby is the master of this motel.I think the two of you ought to meet each other first.Here, hold it.This is...There's no deal in this place.Not while I draw breath.August!Don't you interrupt them.
```

### [35] hash=`98606436174bac01`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
There's no need to worry, Miss Burton.I've done this countless times.Allow me to peer into your dreams.That rain?I can catch anything with a toss!Burton, that's why you gathered us here right?You shouldn't be here.You understandwhat we desire most, right Burton?Burton, we made it right?Why is it stillraining?Don't be such a baby Isabella, haven't you seen the rain before?No!Are you afraid of children?
```

### [36] hash=`5ac5703294085a4b`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
No, I'm not afraid of them.Rain is common, it'sSo I wasn't wrong at all.Why waste your time with that mercenary?She may look tough, but she's hollow inside.Have you ever eaten a macadamia nut?Crack the hard shell, and you'll find the delicious centerwho could resist the soft texture and rich flavor of fear.Miss Tuesday, this has to end.You were the one pulling the strings here, aren't you?Oh, what an astounding accusation, but oh do I feel so, I've never felt so satiated
```

### [37] hash=`2c6ea15f240e1e19`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
in my entire life.You're the only one who's ever seen through me, how exhilarating.However, your accusation missed the mark.You see, my hands, they're immaculate.Never once tainted by a single drop of blood.I take great pride in it.You see, I barely do anything to make people's fears arise.I would never injure anyone.Fear created through physical harm is its crudest and most base form.What I crave is the fear that lingers in their hearts.
```

### [38] hash=`21cf1e82a31a953b`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
The kind of fear that, even years later,When they recount their experiences here to their friends and families, a seed of fearis planted in the listener's hearts.I'm still fearing my guests, and they become my beloved children.Where is she?Where's August?Well, I suppose she's experiencing her own fears right now.Under that hard mercenary exterior.She's tormented by them.Can you imagine that?Sorry, Miss Tuesday.
```

### [39] hash=`229b603ed1a80802`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
But I'm not interested in this vile obsession of yours.This is...Howdy, Argus.Long time no see.We thought you'd never come back.Mr.Dennis?Why are you here?Oh, boy.You listening to yourself?Why wouldn't I be here?It's my daughter's wedding day.Huh?Oh, well, congratulations.But you really shouldn't be here.Don't you remember?Three years ago, your daughter ran away from home.She left a letter and then went with Mr.
```

