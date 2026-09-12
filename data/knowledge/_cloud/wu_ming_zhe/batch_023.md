# 剧情图谱抽取 · batch 023

- 角色：`wu_ming_zhe`
- 批次：**23** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.9」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_023.jsonl`

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

### [0] hash=`2234d55f1adee298`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Without you, there would be no Umbrella, and everyone would have died from the side effects!But many did perish because of me.I had underestimated the danger of the ritual, and it ended up spreading uncontrollably.Did you not once have the same opinion, researcher Adler Hoffman?I...It is surprising to see you change your mind so quickly.But that is just what Laplace needs.The spirit of rationality and self-evolution.
```

### [1] hash=`a0838e7e16b10b60`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I can imagine how they came to this decision.They must have considered the backgrounds of all the employees, including their socialstatus and race.After eight years, we finally created an umbrella to withstand the storm.However,our methods for achieving such progress and breakthroughs were too much for some to handle.People needed an outlet for their frustrations, so someone had to be held responsible for the
```

### [2] hash=`0749db9100374218`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
accidents and casualties.Numerous complaints have been filed against me, accusing me ofbeing a cold, heartless opponent of humanity.Within the Foundation, Xeno, and even here, some are starting to question the idea ofhaving an awakened piston as a leader of Laplace.They argued about my arcane abilities, unsure if I had them under control or if they werebecoming unstable and affecting my ability to make rational decisions.
```

### [3] hash=`16de4d9293e68be8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I did give the nod to Ms.Kikanya in violation of the confidentiality agreement, but ultimately,it helped people survive, and that is all that matters.So they're questioning your standing because you're an awakened, an arcanist?They're doubting the rationality of a machine that values technology and progress aboveall else?Could anything be more absurd?Even I, a human, was on the verge of giving up.
```

### [4] hash=`ef9bbdc080b0dc90`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
It was you who convinced me to save our species.My question is, why are you so upset?This does not affect you.In fact, you may be promoted.Laplace is setting up a new department, and you and Ulrich should have been invitedto head it.Maybe you should take up that offer.At least you will get a promotion as a just reward.By the way, Ulrich ended up receiving a medal, but like you, he was not exactly thrilled
```

### [5] hash=`31d93d282e3d00ab`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
either.He is outside the committee building, refusing to eat in protest, but everyone knows howresilient the awakened can be.It is going poorly.I will suggest that one of you take this position.No one knows this research better than the two of you.Not a chance!The research must progress, and you also need to ensure that the results will notbe abused.Your Highness.The punishment does not bother me, Researcher Hoffman.
```

### [6] hash=`c7457bbf2acabdf8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Power exists only in your dictionary, not mine.From the moment of my awakening, I have been unable to comprehend you creatures.And even now, that remains unchanged.We operate in different ways, just like how our fuelsdiffer.But the bright side is, our paths align.Whether we are creatures or machines,humans or arcanists.Most of us strive for a better life.It is this primal desire that drivesprogress.
```

### [7] hash=`534cfc653d814f7b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
That is why I put on the mask of a human and work on improving my appearanceand speech, all for the sake of better communication with you.Unfortunately,my efforts do not always pay off.Some say that the more human-like I appear,The more different I seem, but I am who I am, and my motivation is not to gain recognitionfrom others.Our aligned path leads us to progress, and that is all there is to it.
```

### [8] hash=`bb2ec4c0c8dd92af`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Thanks to the invention of the umbrella, Laplace can now resume its research unhindered.And, if there is someone better qualified to lead, I am more than willing to remaina humble cog in their machine.Besides, Miss C introduced me to a beautiful resort.The lake there is rich with arcane power, perfect for an awakened arcanist like me.Not only is it a resort, but also an independent team with a good amount of freedom.
```

### [9] hash=`a9fd1d1952ab05f6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
My only concern is if they have adequate power supply.Oh, rust might be a problem.Perhaps I should ask Researcher X about his Titanium-D Rust machine.Time to go, Simone.Madam Lucy, please take a look at this before you go.This is the report you compiled during the storm countdown, detailing 126 side effectsand how the scroll alleviates them.I have some questions about the data for Type 34.Yes, I can see a few errors in here.
```

### [10] hash=`20a56c905c52a166`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Unfortunately, I have to complete all of the handover procedurestoday.Perhaps you can ask Mr.Ulrich about it later.The side effects left a mark on you, didn't they?There are 162 side effects, not 126.There was also an obvious typo in the data for Type 34.We noticed it long agoand corrected it.Took only five seconds.You sacrificed so much for this report,yet you could not see such glaring mistakes.
```

### [11] hash=`efa91137ef6b5df2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
You called me Researcher Hoffman earlier,a name you haven't used since you took over Laplace eight years ago.To avoid confusion with my sister, you and our colleagues started calling me Adler instead.How much data did you lose to impair your research abilities like this?Is this why you have to leave Laplace now?The progress you've made has helped so many, but at what cost to your own well-being?We should go, Madame Lucie.
```

### [12] hash=`4eae0ba12e0e56d6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Goodbye, Researcher Adler.Thank you for correcting my mistake.Fine!I'll take up that hole and do what you've been nagging me to do!I'll take care of those pesky committees!But just so you know, I'm not doing this for the higher-ups who look down on us!but for the people who look up to us from below.Perilousy!Attention!Salute!Why are they throwing papers at me?Are they rejecting me and banishing me?

On the contrary, madam, they are showing their reverence.I see.Let us go, Simone.I miss the Laplace Chargers already.There is a 230-foot bath at the resort, right?
```

### [13] hash=`bbe04bddf775efd2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p10`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（10.泥泞路.1/13 00:30）

```text
What is going on?Warning warningHey Dawkins forget the outside come look at thisSome guys cracked it.They found the correct pronunciationFor real they better be serious if this is some kind of prankla unaso closedamn it damn itUlrichDawkins Victor Likert.Are you in there?Listen!If you receive the pronunciation of the incantation, do not recite it!Do not write it down!Do not pass it on!I know we've had our differences, but you have to trust me!
```

### [14] hash=`ef189e1449f4f071`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p10`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（10.泥泞路.1/13 00:30）

```text
I'm trying to save you!Warning!All personnel stay away from their communication terminals.Do not recite any messages on the screen.Repeat, do not recite the incantation.Do not recite the incantation.Do not recite...Richard?D-Richard!Don't speak.We're going to the Recap Center.No, you go to Dawkins?Dawkins?No, no, no!Researcher Adler, please evacuate immediately.We will take over from here.I thought the worst case would be that the ritual is useless since no one here can wield it.
```

### [15] hash=`bb693568a9d6e663`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p10`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（10.泥泞路.1/13 00:30）

```text
I was wrong.So terribly wrong.All of these catastrophic events, and only three words were uttered, three.What are we dealing with, Madame Lucy?Which deity are we provoking and stealing from?Get some rest, Mr.Adler.Your mission is complete.Other researchers will take it from here.You what?Are you not going to call it off?After all that's happened?The research must go on.The authenticity of the incantation and the fact that any Arcanus can recite it were revealed to us through this unexpected mishap.
```

### [16] hash=`7b2716ef2697f513`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p10`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（10.泥泞路.1/13 00:30）

```text
Now, a new question arises.How can we eliminate the side effects?From now on, we no longer require the help of human researchers.Only Arcanum can lift a curse of Arcanum.Thirty-seven!I'll get you out!Is this Six's scroll?Positive one, negative one, positive two, negative three, three, negative three, positive two, negative one, positive one.I see.I understand now.What did you say?37, are you feeling better now?
```

### [17] hash=`f72c52f11f86720a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p10`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（10.泥泞路.1/13 00:30）

```text
Spartan, Six's scroll reconciled the gap between the supreme existence and me.I can now hear and understand.The answer to my question, the solution to free us from the emanation, the responsePierron promised me, is a string of numbers!
```

### [18] hash=`29c039dcb10d47b3`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
Key to the Gate of Truth, Thorns sent me.This is the final solution.We must leave here at once.We have to tell everyone.I am so proud of you, Thirty-Seven.We will save everyone.But there's one thing I don't understand.And that is?Six, his scroll saved your life.Maybe he foresaw the dangers and protected you from it, so you can leave there almost unharmed.But what was he trying to tell you when he warned you about the collapse of your world as you know it?
```

### [19] hash=`24122488a3e2c4cf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
Mind your step everyone.We are passing the wall of truthThe wall will come crashing down if false words are spokenSilence is advised here unless circumstances dictate otherwise888Forgive me, but this seems to be the right momentFor some long-neglected questions to be answered.Perhaps, but hardly appropriate or righteous.We will talk of righteousness after you've shared what you know, Six.You've been silent for too long.
```

### [20] hash=`c0ee5dc6fdc58ab0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
Four years have passed since you became Six,and for four years you have been hiding things from us.The long-neglected questions have created a cloud of doubt between us,And now the boulder of fate is falling on us, and we are teetering on the brink of destruction.It's time to be honest and true to your people, while you still have them.We are the seekers of truth.It is unjust to keep us from it.Let the wall of truth bear witness.
```

### [21] hash=`eed69d70bd3002b7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
I want nothing but an answer from you.I am not here to provoke untimely conflicts.Answer her, Six.You should be glad that I am not the interrogator here, because the wall would have collapsed immediately.You may lie, but the wall will fall.You may stay silent, then I will lie to break the silence and the wall.Or maybe you could outwit the wall with the liar's paradox.Only sadly, I have tested it for you.
```

### [22] hash=`c7deeee48724f1e5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
One cannot deceive it by stating, I'm lying.After all, it's a test of morality, not logic.It needs your honesty, not your wit, or anything else.What do you wish to know?What else?The most important question of course, the question about the essence.Why has our research stagnated for the past four years?Why did we fail to predict the emanation in 1929 and again in this time?Have we misunderstood the premise?
```

### [23] hash=`67a1410cf821b67b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
What if the emanation is not a manifestation of the Transcendental Law at all?Worship as worship, thinkers think, governors govern, and researchers research.Your questions are not mine to answer, 210.A six has no expertise on the study of the emanation.I'm not qualified to answer about its essence.Your question is to abstract, 210.Don't dance around the subject, six.The wisdom has been passed on to you as it has to every other six.
```

### [24] hash=`1e8d1471fc09a260`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
I watched her, and the previous six bored the ship in search of answers in the phenomenalworld.The ship didn't come back in time.The emanation caught them, and that was only the beginning of our misfortunes.The model failed.Our whereabouts were revealed.Hysteria now poisons the minds of our people, and the empirical knowledge accumulated overyears suddenly no longer applies to the current situation.
```

### [25] hash=`17e7e5dc34fe811c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
Why?What did she find out?Couldit be that something's happened to the transcendental law above?Has the truth we believed in changed?Hipparsis discovered the secrets of Route 2 and toppled Pythagoras' school of thought.The controversy surrounding Newton and infinitesimals presented a challenge to the groundworkof calculus.Russell's self-referential paradox sparked the third mathematical crisis.Though said theory was eventually perfected, the lessons on self-referentiality remained.
```

### [26] hash=`ecdd946bfa6da0ea`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
In the end, Gödel's incompleteness theorems showed that proving or disproving everythingis impossible.Therefore, absolute knowledge is unattainable.The boulder of fate will tumble down its peak whether 37 is the one pushing it or notHowever hard Oedipus tried to defy destiny his path to tragedy remained unchangedYou're talking in riddles again.I should thank you for bringing the question here888 so I may finally speak the truth
```

### [27] hash=`f449a34eb630752d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
77 did ask about the essence of the emanationshe asked what happened to the supreme existence what plunged the world intomadness the answer was disorder and chaos blasted you knew this all alongfrom the first day of your revelation when you became six you knew that theemanation was not a manifestation of the transcendental law and patternsabove but rather a symptom of its utter disorder and chaos and you knew
```

### [28] hash=`0cfb5a69bea9cebf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
that the transcendental realm of numbers was no more,and that the essence of Numa,the one true form we believed in,had become an ever-changing existencelike the irrational numbers?Four years.You kept this to yourself for four years.Why?Was it for a false sense of peace?To keep the island stable,did you deceive us to prevent the realizationthat our research would be in vain?It's time to halt the bickering.
```

### [29] hash=`c2e4b9da5c5102db`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
Get everyone out of here now!Pray to the gods for what you are about to do, and pray that all goes well.Once familiar with this practice, you will understand the constitution of both eternal gods and mortal men.Huh?What happened?Did they not carry out the cleansing ceremony?You will know the extent of all things, the boundaries of their entirety, and what connects them together.Oh, what's going on?
```

### [30] hash=`3444978d95abe2d0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
No, this is the large-scale ritual on this island undoing itself?You will see, as you should, that the nature of the universe flows in all things alike.Thus, you will not hope for what is beyond your reach, and you will not be deceived.Pray, my friends.Pray for yourselves, and pray for everyone.Pray for all the suffering and misery around you.Reach into the unseeable darkness and pray to the unknowable Supreme.
```

### [31] hash=`71aebcc65fc3ac7b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
Speak your hopes, for you are a finite creature yearning to transcend its own existence.The determination that once helped us overcome our insignificance and touch the light of Numa should guide us once more.Where are you going?To the cave.The trial is not over.The final cleansing is yet to come.There are still duties to fulfill.Here is a well-known question you must have heard.What goes on four legs in the morning, two in the afternoon, and three in the evening?
```

### [32] hash=`5b04ad7e960bc4a2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p11`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（11.巨石滚落之刻.1/13 00:30）

```text
It's so well known that no one finds it novel anymore.But please, do me a favor and answeryourself.Correct!This is the same answer Oedipus gave to defeat Sphinx, thusbecoming a hero, but also starting him on his ill-fated destiny.Raise a question,give an answer.This is the most fundamental ritual.Through this we getnearer to God.Yes, a ritual.Whether it is by pouring out wine, slaughtering a
```

### [33] hash=`08bb6ace127b586e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
I was in the cave with 37, but the timer broken.Vertin, here you are.Yeah, people are waiting.The feast is going to start.Today's the big day.We're celebrating because we kickedManus Vindicte off the island,found the key to storm immunity,and saved the numbers people from great disaster.Come on Vertin, you'll miss outon the delicious honey roasted rabbit.Regulus, you've just kicked over something.
```

### [34] hash=`97288e90178a9861`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
What is it?Something for the cattle?Whoever left this here nearly tripped this great captain.Forget it!Come, Vertin!What are you still doing there?Nice wine.Did you make it yourself?Careful, Miss Lillia.Too much wine can corrupt one's body and will.Besides, you are already halfway through our stock for the year.Hmm?But this drink you brought is pleasant to the note.Coffee, you said.I have heard many things about it.
```

### [35] hash=`4701bffc5cb3308f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Oh.Bitter.Ha!Poor guy!I was expecting more from a man of your size.For God's sake, Regulus, keep an eye on your first mate here.Wow!He's so out of it right now.Thank you for helping us, Furtin.We wouldn't have made it without you.And I look forward to our continued collaboration with the Foundation.No, none of this makes any sense.Enough business!People are having a party here!Well, what do you say to this lovely captain who just picked up some food for you?
```

### [36] hash=`b71e43f4ca92b9da`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
My apologies, Regulus.I was too focused on linear regression formulas.I have to admit, she has a good number.Number 100 times better than me, and 210 put together.Calculating, 37 plus 6 plus 210 times 100 equals 2.Oh no, she is not 25,300.I doubt anyone could live with themselves with a number that long.You haven't met before.This is Amu, my white rooster.Amu, this is Vertun.White rooster?Something's not right.
```

### [37] hash=`1d1c28550da3968d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
None of this is right.What's happened on the island?I must still be in the cave.I have to get out of here.Critters eating beans and a white rooster.These are supposed to be taboos on the island.Is this an illusion brought on by the fog?Or a new trial?No.Something's not right.The flow of arcane skills on the island has changed.I need to get rid of them first.My surroundings changed.Is all this still an illusion?
```

### [38] hash=`24dd6ebdd585134b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Looks like the way we came, but it's a little different.These signs, are they trying to take me somewhere?The way out, perhaps?I made some coffee for those clever eggheads.Enough to mend their broken souls after turning their backs on it for half their lives.Fancy a cuppa as well?Here you go.Regulus, it's a violation of their scripture.using examples and analogies, or reduced to its most basic symbols and generalizations.
```

### [39] hash=`3329871778b21585`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Eventually, once they've gotten used to the formulas and outlines,they may just see below the surface and find the deeper essence waiting there.What about you?What do you think is your essence?Are you any more significant than a pile of coffee beans?Do people decide to put milk and sugar in their coffee for the taste?Or is it bitterness?That sharp sense on the tongue that tells them it must be sweetened?
```

### [40] hash=`dc764873ec830f3c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Do they even like coffee?Or is it a memory of needing it to make it through the day?Each decision we make coming from a tug on our hidden strings, strings we cannot beginHow can we lead our lives according to these strict rules?Rules that are always changing definitions.It's too much for this old brain of mine.Why not simplify our definitions?To learn about the world like we were kids once more.Let's begin with math.
```

### [41] hash=`69529cc4ae3caf97`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Could it be as mutable as left and right?Could there be a hidden integer between 3 and 4?Is 1 always 1?Or is it just our frame of reference?But where is it then, this everlasting truth?Have you ever seen it?Have you basked in its radiance before?Maybe the shadows on the cave wall are our true reality.Maybe the sun is just another prop in our shadow theater.What if the people who chose to stay in the cave were the ones who were truly wise?
```

### [42] hash=`2dcf62a269175299`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Be careful what you hold to be true, darling.Two ten.I know thirty seven isn't a fanStill I would be honored to have an integer like that as my number.Let's try it one more timeI have a feeling that together we can find the right number for me.Who am I anoldQuestion it can't be as simple as your name a name after all is only worth what meaning we give itbewildered by their own existenceMan turns to the ultimate truth for answers.
```

### [43] hash=`97aa922502664a39`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
But soon enough, they come to see the truth is also beyond their ability to comprehend.That is when the fear catches up with them.So they put aside their search for truth and look for something more straightforward.A simple answer.Enough to satisfy a frightened child.Caught between a comforting lie and something more frightening than the truth.And if that is so, how can we know who we are, really?
```

### [44] hash=`0bc89d31a385d0a6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
Very good.Perhaps the truth lies hidden in the question.Hold tight to that answer, darling.A bit of elderly advice, there is no greater treasure.One day you might be amused by this idea, when you see yourself from someone else's eyes.This is the second is the squareParty seven, is that you?The triangle on the triangle and the rectangle on the rectanglePerfect things should bethe emanationDisorder and chaos this copy.
```

### [45] hash=`07db236bb67c9728`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p12`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（12.豆子派对.1/13 01:00）

```text
This isn't rightUgly how inelegant?How could this be the revelation from the patterns of the Transcendental Law above?How could such a terrible answer fall on my ears?I can't tell the others about this.There must be a mistake.I need proof.I have to go out there.Merton, my child.Are you here to partake in sand play as well?Leave that I woke up in time and you as well.Let's go vertin.We need to tell everyone their numbers

Do you hear that?So many people out there must be Sophia here to pick me up.I told her she can wait for me outsideWait 37
```

### [46] hash=`ba71eed9ffe4563c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
When will they give us the order to attack?What's taking so long?The island is just across the bay.We have men, weapons, supplies, everything.Just give us order and we will take to shore.Check out these bad boys.Anti-Arcanum weapons courtesy of the American from that Walden place.That creep just doesn't sit right with me.He's got that Arcanus stink about him.But his technology is solid and we needed it.
```

### [47] hash=`9481cfb3883a6af0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
We've got to get ahead of the Serbs and the Greeks!Relax, Georgi.Leave the decisions to the big shots.I'm sure they'll just hug out their differences in the meeting room or something.Besides, you saw the monsters on that island.Can't speak for everyone here, but I don't want to die.Screw the negotiations!Screw the committee!Like it or not, we were the first ones to find the island.Not the Austrians or the Germans.
```

### [48] hash=`beadbfff246f5b4c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
Those arcanists have gone into hiding again.I swear I could see it from here yesterday.Are those bird-like creatures?Living in droves?George and Braza, leave them be.Come, play with us.George?What a good opportunity this is.It's too good to pass up.We've got to act now.We will claim what is ours.This island belongs to us.It's in our territory, and we were the first to find it.Why shouldn't it be ours?
```

### [49] hash=`35816106f7b099b3`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
The Austro-Hungarian Empire has officially declared war on Serbia.Russia is mobilizing in support of Serbia.Germany demands Russia to stop mobilizing at once.Germany is mobilizing.France is mobilizing.Open the door!It's important!You have to listen to me!Albert?I have to go.I have to find Johnson, Raymond, and Herbert.That little rascal pushed Ilsa into the fountain.We have a score to settle.Take care, Clara.
```

### [50] hash=`1caab452f5dd108f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
The syndrome is spreading, Doctor!Stay any longer, you'll be infected too!Leave with me!Just met her at the coffee house last week.We were talking about her wedding.This way, Doctor.Get out of here!This way, Doctor.We have to go back to your clinic.The Special Operations Squad will meet us there.I have just one question.Why hasn't the project stopped yet?Adler Hoffman, you have been removed from the team.
```

### [51] hash=`66d31132fdabc85b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
You're not authorized to be here.You have violated...The LSCC safety management regulations?I brought them with me.You're welcome.If you cared about the regulations as much as you claim,you'd know that none of what's happening aligns with its guidelines.Even the heads of Laplace have no authority to continue the experiment under these circumstances.Yes, she makes the ultimate sacrifice, hoping that it would lead to a breakthrough.
```

### [52] hash=`d3b959bf14b42a1f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
But instead, death continues to rise.How can you let this go on?I demand to know why the experiment is still going!Don't we have enough crazies around here?Madelucy has important things to do.She has no time for you.Go cry to your therapist, human.Important?What could be possibly more important than this right now?What happened to the humanitarian ideals of the Foundation?Are we now under the tyranny of machines?
```

### [53] hash=`4703728a02d78834`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
What's this important thing she's got to do?Leading the paper, sipping on oil, and charging up in a 230-volt bath?Is that you, Adler?Welcome.Look at this mirror, dear.There's a sizeable stain on it.Yes, it is.Hmm.Maybe its owner meant to break it so that the stain would be thoroughly removed.Now the stain is gone.And the owner has a collection of little mirrors.She must have accidentally left this one behind.
```

### [54] hash=`fe2156798a7ae962`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p13`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（13.艺术浪潮.1/13 01:00）

```text
A lady with great ambitions and an unconscious charm.A lady who wishes to make the rest of the world accept who she isAh, as I said, despite their differences in approach, the brother and sister are mirror images of one another.But now the mirror is broken.I hope she can make it through the seven years of bad luck, or a thing.There's no way around it.
```

### [55] hash=`10ef4baf734aa48f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
I am not in a suitable form to receive a guest.Simone, can you put me back in my body?I feel much better, thank you.Oh, you have even put on a face for me.How sweet of you.I have noticed your icy gaze, researcher Adler.You are yearning to correct the logic of this place.Well, I only said that to Simone out of courtesy.In reality, whichever body I am put intomakes no difference to me.The experiment, ma'am.
```

### [56] hash=`9c129395e6c37931`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
Why hasn't it stopped?Are you going to pretend that nothing's happened?That no one died?Could it be that you and Ulrich, the awakened, being the tin cans youare, have no regard for actual lives?Adler Hoffman, I will not warn you again!Relax Adler.You are led by a biased opinion because you lack critical information.to a more rational perspective once you receive sufficient information on the subject.
```

### [57] hash=`149777bada0f6fbb`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
A more rational perspective?We are humans, not machines.We are not expendable parts.I have plenty of reasons to question your decisions.Your excessive insistence on this experiment could be a sign of uncontrollable behavior,a trait commonly seen in arcanists.The experiment has been cancelled everywhere.Except for this very room.As you and Researcher Medicine Pocket have said, the ritual is beyond the limits of almost everyone
```

### [58] hash=`6db9b1ad518b9f7b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
here.The side effects will kill them before the ritual can even take effect.The first wave wasinevitable.Dora had pressed send before she disintegrated.We only managed to halt thesubsequent transmissions and evacuate the unaffiliated staff.We kept only a fewArcanists on the team, and each has signed the consent form.Your insistence will only bring calamity upon calamity on our people, for nothing!
```

### [59] hash=`74905a784469a087`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
You might be right, but how is being right going to help us?Huh?You spoke of the limit, and I am surprised that it is you who brought it up.The physical appearance of humans has remained relatively unchanged since the Neolithic era,but their thoughts and civilization continued to evolve and underwent significant transformations.The achievements that humanity enjoys today were not given to the species by any one person
```

### [60] hash=`4e80c698f63e0753`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
with godlike powers, but were the result of the collective efforts of all human beings.Limits and boundaries must be pushed, or there would never have been room for development.There is no reason to believe that the limit cannot be challenged, especially whenwe already have the tools to do so.We must make progress happen.Gandio's lies.Lies?We have no choice but to go beyond that limit.If we do not break away from the storm, there is no future for us, let alone progress.
```

### [61] hash=`1bd16787fdecf8b2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
We need to first determine all the side effects as a priority.This important step will help us compile data and eliminate the effects so our colleagues can use the ritual safely.And who will try it this time, Madam Lucy?Explain.Please wait, Adler.We have yet to reach an agreement.What?Are you experimenting?Here?She's reciting it?She's read the reports, right?She was there when Dora broke into pieces!
```

### [62] hash=`f700d6bcbb9d4716`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p14`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（14.干沙粒.1/13 02:30）

```text
Don't just stand there!Stop her!Now!Who's going to lead us if she also turns into a pile of scabs?Stay where you are, Enigma!You insisted on being here!You demanded to see this!Don't bring your pathetic, narrow-minded humanitarian values in here and tell us what to do.What do you know about us?You can do it, madam.This is just part of the established procedures.Just a few more syllables, madam, and it will be over.

Established procedures.Simone, good.
```

### [63] hash=`7805efe5373e0d95`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
you wanted to show me that's always bought to die in vain you just let ithappen calm down calm down she's dead right there youmurder we have already repeated this experiment many times many times you'vesent people to their deaths over and over again look at you Adler peeingyour pants over a curse the human boy is so scared that he forgot to ask thethe warmth of a miraculous blessing on my head.Soft, light as a feather.
```

### [64] hash=`f5907ed41df9da31`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
I told Madam Lucy right away,but as soon as she left the room,the curse hit me and I began to liquefy.There was no one else in the room.My liquid form had become too insubstantialto push the help button.A long darkness followed.After that, I woke up again in my original, primitive form, the way I first came into this world.Original, primitive form?Unlike humans, the Awakens have neither flesh nor nerves.
```

### [65] hash=`36b52e5461b8f581`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
We are pieces of consciousness, echoes of a primordial melody that just happened to reside in material objects by chance.With a mind and a body combined, we could talk, learn, think like you do, and performthe experiment and endure the side effects.And this curse, for some reason, cannot affect the primal consciousness that caused ourawakening in the first place.While human minds dissipate when their tangible bodies are destroyed, our minds reawaken
```

### [66] hash=`ad30e9d330183c28`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
regardless of the changes and destruction of our external bodies.Of course, this was an assumption based on idealized circumstances, and I needed anotherawakened being who could awaken in different bodies to confirm my theory.That is why I sought out Madame Lucy for cross-verification.The results?Yes, it was an assumption!You said it yourself!You came back to life this time, but what about the next?
```

### [67] hash=`a44ae508ca299240`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
Nothing is for sure in Arcanum.What if she never wakes up again?What if she dies for good?We know what we are doing, human.Stay out of this.Only the awakened can carry out the experiment.So we must proceed.This has nothing to do with race.It is a sense of duty that every researcher should have possessed when they chose this path.We have to go beyond the limit.Not out of madness, but out of rationality.
```

### [68] hash=`1f7f7875f50ccd7e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
We seem to have replicated effect number two.And 117 of the Coleman lab's protective rituals were proven ineffective.Write it down, Simone.This is the fourth time we have seen it.Also, number 45 and 69 are related to it.We need to speed up.This is too slow.Adler, what are you doing here?I am glad to see you out of your room and working with us again.No, he's not on the team, mom.He forced his way in here.
```

### [69] hash=`cfcd97c816a1b4c6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
Oh?My apologies.I seem to lose a small amount of data when I reawaken.I am glad that you are showing initiative, Adler.Were we supposed to talk?No.We have nothing more to discuss, ma'am.Ulrich has filled me in on everything.But I still worry whether the experiment's risks were properly assessed.Assessments will only be assessments.Much is beyond measure when it comes to Arcanum.Perhaps faith plays a more important role here.
```

### [70] hash=`64cfc1166cbb23fe`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
I'm surprised it is you talking about faith, ma'am.It seems we both have the ability to surprise each other.You are right.Assessments could indeed be useful to us.It allows us to know the probabilities of success and failure based on established factspast experience.But when we find ourselves in uncharted darkness, withno information or past experience to guide us, how are assessments going tohelp us?
```

### [71] hash=`9188d4b1aa20cd36`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
The only thing we have in such darkness is the unwavering faith tomove forward.When the first steam engine whistled, I awoke into this world.At the beginning of this new life, my circuits were charged with a singular primal desireto progress.In the midst of that never-ending whistle, I have watched man build the towers of scienceand knowledge, and I have watched them unleash chaos and destruction.
```

### [72] hash=`7b292613bcbd9a4f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
You too have been lost and deterred, but your engines of progress have never stoppedchurning.Always move forward, no matter the destination you told yourselves.Until the storm brought everything to a standstill.But this is just a small setback.We are only back to the beginning where we stumble blindly.And this time, I happen to have a cane.No need to worry about me.I will not shut down as long as there is still hope for progress.
```

### [73] hash=`9e1d513e7184265c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
We have wasted a bit of time on data recovery.Come, Simone.Let us begin the next experiment.I hope to dissolve into Pace this time, sowe can easily handle it with the Coleman's Ritual of Transformation.Seen enough?We know what we are doing and you are of no help here.It's been the sameold story in this place for the past eight years.When your faith crumbled during thestorm, it was us who took over the place and cleaned up after you.
```

### [74] hash=`78b3ac346e3f4135`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p15`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（15.前行者.1/13 03:00）

```text
It was us whogot things back up and running, put poles in the hearth, and blazed a trail whenMy colleagues.Each of them deserve to live more than me.But they're all gone now.There'sonly me talking to you.Alive.Useless.Am I going to see your names on that list too,Ulrich?Spare me the feelings, human.Though I will take back my sarcastic jabs at you, it isnot something a leader should do.Madam Lucy talked to me about the importance of teamwork.

Um, yes, and by regulations we are not to leave, but, um, they said their new theoryhad to be verified in the storm.
```

### [75] hash=`c3c0a70ec3e42a10`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
Fresh air, green grass, the dew, the mud, this is what I'm talking about, a better world!Researcher Medicine Pocket, I must remind you that we are at the edge of the immunity zone to the storm.Once we cross the line, we will not only catch the storm syndrome, but also be taken by the storm at the end of the countdown.I know that, how stupid do you think I am?Hey, isn't that Rudolph, the poor guy sent to Tunguska?
```

### [76] hash=`6f36caf04492ba10`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
Hey man, how is Siberia?Welcome back.Did you bring me any new research materials?Oh, you don't recognize me?You're breaking my heart!It's me, your best friend that you just met.Medicine Pocket.Researcher, I must make clear that you only applied for 15 minutes outside for research purposes.Your countdown starts from the moment when you cross this line.Okay, safety first, I know!Get off me, you're hurting my arms!
```

### [77] hash=`4d141b349200cc27`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
All bounce as soon as the storm syndrome hits.Even if I catch it, look at the syndromes of this era.Distorted faces, murderous intentions, obsession with war, rampage.What's got you so worried?They aren't that bad.Well, the melting faces part is kind of gross.I really wanted to test this in Vienna.Oh well, better than nothing.Alright now, I'm gonna walk a little further from the immunity zone so the samples are
```

### [78] hash=`921e385b9038f1b7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
easier to gather.The ideal distance is 1,500 kilometers, but don't worry, not gonna do that.Even I can't run that fast.Now behold, the important moment.When I prove the dorks in Laplace wrong about asymmetrical nuclide are.Now hypothetically, if the storm research were to succeed, two things should have been done.And to find out the safe way to use it, we have to...This is what Lucy was thinking.The awakened met the casting requirements of the incantation, and Ulrich succeeded.
```

### [79] hash=`87169cddab3f961e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
While the other Arcanist did not feel the same miraculous blessing like he did.So as long as we eliminate the side effects, they'll be able to inscribe the incantationand mass produce it for the humans.One problem is, only the awakened can carry out the experiments, and there's not manyof them around.It'll take too long, there's no way to do this in 24 hours, heck it could takemonths or even years!
```

### [80] hash=`6fbabbdc05539364`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
there must be something else we can do but you are not an Arcanist why shouldyou play by their rules yes that's right let's try a different approach what if Istart with the desired outcome and work backwards to the question thequickest and most efficient way to save everyone is to make them qualifiedcasters of the ritual they won't even need protective equipment if we can doThe challenge is how do we qualify the casting requirements?
```

### [81] hash=`ed6a118dced3ccbd`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
Medicine Pocket's theory is correct, and there's enough data and supplementary experimentsto back it up.The power of Arcanists is directly tied to the purity of their bloodline, which isassociated with the special cells in their bodies.Using arcane skills reduces the activity of the cells, but the Picasma extract canreactivate them for extended casting.However, the extract only provides endurance, not power.
```

### [82] hash=`b53406b82379b3b6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
It is physiologically impossible for a low-ranked Arcanist to cast a high-ranked skill.That's the reality of it.If we were to compare the power of Arcanists to household appliances, let's say theirnormal voltage is 230 volts, and if the Storm Immunity Ritual were a high-voltagesource of a thousand volts, no, millions of volts, like lightning, the household appliancessamples of the storm.They deduced it also exists in the air before the storm
```

### [83] hash=`64c6ff88692d3f36`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
occurs, like the water droplets in the atmosphere before rain.So now, we canextract it directly from the air, without waiting for the timekeeper tobring the raindrops to us.This will help us a lot in the mass productionof the protective gear.No way.The emanation.AsymmetricalCanis can use it, and the solution was right in front of us!I didn't need to boost the cast's abilities.With the right setup and materials,
```

### [84] hash=`5cc77a3314d1f934`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p16`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（16.水流的引线.1/13 03:15）

```text
the world before the storm is already an enormous stagefor performing the ritual.It's like a charged pylon just needing a cable.Mr.Adler?Thank you, Ms.Whoever,and thanks for letting me know, Dawkins and Victor.It's me, Ulrich.Let me in.I need to see Madame Lucy.Tell her I found a way to transcend the limit.
```

### [85] hash=`07fa2fd4cc3d92fc`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
We don't have time.I'll spare you the technicalities and explain it straight.Our biggest problem is the limit of the bloodline.Low-rank arcaneists can't command high-rank arcane rituals,similar to how household appliances can't withstand what's beyond their designated voltage.In most cases, the caster can only use their own arcane circuits that run through their inherited bloodline.But what if the caster were in a special electric field?
```

### [86] hash=`49537ae7163a867d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
What if we used existing circuits on the outside and put the caster into a greater circuit?What if we factored in the entire planet and used the atmosphere to split the current flowing through us by adding more appliances to the circuit?Don't be ridiculous, Adler.We are not household appliances.Hold on.Let me finish.24 hours before the storm, the entire world is charged with abundant arcane energy.
```

### [87] hash=`ba28566d22fb351d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
It becomes a space emanating Numa, a cloud ready to discharge, a special electric field.Look at asymmetrical Nuclide A.The key to the storm immunity was inside the storm allalong.And look at how the Mantragora is the antidote to its own poison.The solution can be hidden in the question itself.The arcane energy Acaster inherently lacks can be borrowed from the surroundings duringthe storm.We just need a way to induct that energy.
```

### [88] hash=`1f6367044f015ee5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
And Laplace happens to have all the data for the calculations.The observation systems we've built over the past eight years have not been in vain.First, we derive a formula to determine the NUMA needed from the storm based on theArcanus lineage.Then, we'll design a converter to transform the external NUMA into what they can use.They will no longer be bound by their limits!It's still a form of energy, yes?
```

### [89] hash=`aedd0b4e1f896220`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
No one here knows what the storm is, but we do know that it's a massive arcane energy field.We can harness it, much like Arcanists use arrays to amplify their incantations.I see what Researcher Adler is trying to say.A creative solution indeed.But ma'am...Do not worry Ulrich.I also have noticed that humans could be smart and stupid at the same time.Perhaps that is why they need to have their work peer-reviewed.
```

### [90] hash=`edd2e3841dde9c00`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
There is a type of electrophotography invented by Simeon Curleon and his wife Valentina Curleonin 1939 that depicts the energy field surrounding an object or body.It was later used by Laplace as a method of measuring arcane power, notably for the stormobservation systems.Through it, we are able to capture and measure the arcane light, or aura, that is invisibleto the naked eye.The plan of researcher Adler is feasible.
```

### [91] hash=`53a5f0fc603763e1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
Laplace also has the technology to support it.We have the storm observation stations, the capable casters, and the best mathematicians.Ulrich, please ask Miss Tider to lead the calculations, then experiment outside the safe zone and record the Pneuma constantneeded for casting the incantation.And do not give the incantation to anyone.I doubt they can resist trying it.Simone, please contact researcher X.
```

### [92] hash=`3670763fd9f000ed`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
His balancing helmet could be the prototype for our converter.That helmet balances the energy field in and out of our bodies, and was once usedto protect researchers working with dangerous arcane skills.We could boost its powerand use it as a substitute for Adler's converter.But we should postpone their testing request until we have completed our experimentson the side effects.We only have 16 hours and 30 minutes until the storm.
```

### [93] hash=`d59df1aa78dbd732`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p17`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（17.雨幕演说.1/13 04:30）

```text
There's not enough time to...The feasible part of your plan is in motion, and all of Laplace will provide the help we need.We will make it work.As for yourself, perfect your plan so we can save everyone,including the humans.And we only have 16 hours and 30 minutes to find a solution.Understood.I will think of something.You're right about this one.
```

### [94] hash=`0b0e8cab2c339240`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p18`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（18.万物皆数.1/13 04:30）

```text
Slow down and breathe.Stability is an essential virtue to becoming an integer.Okay, let's clean up the place first.The incandation didn't work?Did they fail to perform the cleansing ceremony?Or did you?Survives the oblivion.His hysteria is acting up again.I should help.will eventually lead us to the Kingdom of Truth.What's in front of us now?You seem astray, child.Pains you so?Has the truth not graced thee with its miracles?
```

