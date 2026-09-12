# 剧情图谱抽取 · batch 024

- 角色：`wu_ming_zhe`
- 批次：**24** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.9」｜offset 380
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_024.jsonl`

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

### [0] hash=`4357fc822abc2d36`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
question did you seek its knowledge and what answer did it give you and you'regoing to perform the clean please come up to me miss verton I wish to have aword with you 50 strides from here on the semicircle square you will find yourfriends and the rest of our people I have done as much cleansing as I couldif nothing goes wrong they will regain consciousness soon I know whatWhere has their vaunted wisdom gone?
```

### [1] hash=`12dd4ed20ae65de4`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
And what good does it bring in this final hour?I can hear thy weeping and bellowing within, Miss Sophia.Many a time you have knelt at the Temple of Truth, devoted yourself, prayed for your people,and withstood the tribulations set upon you, all for the betterment of others.Thy character is without reproach.Yet the truth has never deemed you worthy, has it?No, that's not!You shall be granted a greater opportunity.
```

### [2] hash=`a5bcf920ef7a1046`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
A blessing that befits thy devotion.Violation of the scripture!We shouldn't!The scripture?Yet you were never truly counted as one of them.Do you not agree?As evidenced by the decision that truth hath made.No one escapes their fate, as ever.dislike of them.They still exist and cannot be denied.How did this become thedestruction of our people's faith?You will hear no answer from me, 37, for thatis not the question worthy of your attention.
```

### [3] hash=`f2283c2630c24260`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
Do you still remember whatyou answered to me in the cave?That would be enough then.Don't waste yourtime on the collapse of the faith.Don't question yourself because othersthink differently.Walk on, onto the path you have chosen.You have done nothing wrong.Ms.Vertin, I'm afraid I must trouble you for a favor.As you can see, I can hardly take part inthis matter for any longer.Should the situation turn for the worse, please take 37 to safety
```

### [4] hash=`31c1aac8d327d4e5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
and assist her in decoding the numbers.You have my word.We are born facing a choice.Either we restrain ourselves and strive for harmony and discipline, or succumb to destructionfueled by passion and madness.Though the former may be challenging, the latter will only plunge us into eternal darkness.From one to ten, each number has its moral purpose and mission.Among them, only six was chosen to be the leader.
```

### [5] hash=`b10717a132cf6a3a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
Because six stands for balance.Yes, we must pay heed to the balance between passion and reason, so as to stay on the rightpath and not be led astray by the calling of our blood.For generations, we committed ourselves to the scripture and stayed true to what wepledged.We left the trivialities and troubles of the phenomenal world behind, and servedthe supreme existence with the fruits of our knowledge.
```

### [6] hash=`54be4da5ea5c5cdb`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
This kind of faith was how the island prospered, and it was the source of our salvation.Through diligent practice and contemplation, we managed to remain secluded and independent from the rest of the world.The irrational numbers that your people rarely appreciate, are they faced with a different path?A path of passion and madness?We have been long isolated from the outside world by one emanation after another.
```

### [7] hash=`91b6155206310dbe`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
Four years ago, we tried to seek proof in the outside world, but failed.We regrettably lost some of our best scholars and friends in the process.However, it was not the failed attempt that led to this upsetting situation, but a crisisfrom within.Now, with our ship capsized and our scale fallen, I am no longer able to reconcile the tiltof people's hearts and souls.We will be divided.The fanatics from the foreign lands can finally spread their hatred amongst the ruins of
```

### [8] hash=`f3f5ec5d09e92a2a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
our shattered beliefs.I will stop Manus Vindicti.Forget not your promise, Ms.Vertin.Six, we came to bid you farewell.We must act and reclaim what was taken from ours.That is the true meaning of salvation.It is true that I was absent earlier, but please listen to me.Everything will get better because I already have the truth with me.The truth?What good will it do right now?Will it drive out the humans?
```

### [9] hash=`85bfa1ebdbc41740`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
Will it reclaim our home?Will it bring back our deceased friends?What salvation did your truth bring when steel pierced our chests?Manus Vindicte granted us the power to fight back.What did the Foundation do?Don't waste your time with these integers.The Foundation's envoy is here.It is clear they have taken the side of the humans.Kill the envoy!Cut off her head and bring it to our mother!What?You?
```

### [10] hash=`439934a001ebda3b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p19`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（19.双行道.1/13 05:00）

```text
The mask has robbed them of reason.There's no point in talking further.Take 6 to safety 37.I'm the one we are after.I will meet with Senetta at the square.This radio is with them and we will contact our people from there.Don't worry, we had a plan against the Manus and we can still carry it out.Now, on my mark.
```

### [11] hash=`f047c818fb386ffb`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
If you're here to check on the progress, there is none.I'm afraid you'll leave disappointed, Madam Lucy.Send this to everyone.This is la unua.We must share this with everyone.La unua diaglo.Stop the transmission!The ritual is on!Question.Why don't people like the irrational numbers?Do you feel the same about them, 37?Be a little mama.count to 3, and to 17, but I can never count to something like 0.01 001 0001 00001
```

### [12] hash=`70e83ea764e653f5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
let alone use it in calculations, and this non-repeating decimals would make a mess of the resultsand I can't keep the equations as simple and elegant as I wantBut your favorite, the circle.The ratio of its circumference to diameter is also an irrational number.Is it not?It's special.I know how it was found and what it represents, so I trusted to use it in my calculations.The same with E, logarithm 2, and root 2.
```

### [13] hash=`0ca0046d8c7b90ee`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
But not many irrational numbers are this convenient to work with.Some have no patterns, no simplest forms, and no end.I can't work out their digits, write them out, or calculate them.Not only are they impossible to pinpoint on the number axis,but there's an infinite amount of these irrational numbers.What's so funny, Mama?You're a clever silly goose, my dear.You don't dislike them, you just don't understand them enough.
```

### [14] hash=`1ca4a1861ec8f38c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
Take our old friend root 2, for instance.The irrationality of this number can be proven through basic arithmetic, as it cannot be expressedas an irreducible fraction of integers a over b.Proof-by-contradiction is enough, with no knowledge of irrational numbers required.The presence of root 2 is prevalent in nature, and it is particularly noticeable alongdiagonals of a square.This means the system built solely on the ratio of integers was flawed.
```

### [15] hash=`fbf36c21ddfed164`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
Yes, root 2 is simple, elegant, and one of the greatest discoveries in mathematics.It showed the existence of infinite incommensurable numbers, with root 2 being themost obvious one to find.This was how the tower of old ideas crumbled, paving the wayrevolutionary breakthroughs that catapulted mathematical analysis into uncharted frontiers.We discovered a kingdom beyond our traditional methods, one that's immeasurable, incommensurable,
```

### [16] hash=`b6292c2347b9ca53`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
and inexhaustible.Key to its gates is hidden in plain sight, in the diagonal of a square.If we get to know the irrational numbers better, we can be friends with them too!But...you haven't told me why people on the island hate them.Thirty-seven.You're awake!Sophia?How long was I out?You've been in a coma for a week.We...Have to find Six!I have to tell them now!Our circle...has been broken!Now we've learned some manners in Apeiron, haven't we?
```

### [17] hash=`7afd750a2666e66a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
Namely, to abstain from beans,never parcel off a loaf, and stay away from the white roosters on the road.It's beenso long since we last talked about these things.How time does fly!This rusty grainof mine is struggling to keep up.We should have waited until dawn to light the candles.The sun would have mistaken the day for night and delayed its appearance in the morning.That way we would have had more time to talk.
```

### [18] hash=`0c3ec437ab5ef650`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
Indeed, you possess a far greater understanding of the laws of nature than your ancestors.It's only natural that you wouldn't relate candlelight to sunrise, but for the peopleof earlier times, there was a commonly understood connection between the two.Did the trees not bear fruit after the Horn of Plenty was filled at the harvestfestival?The Ouroboros, the eternal cycle, the hawk, wit and astuteness, and the soil, safety and protection.
```

### [19] hash=`58ec53b790650d18`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
Aside from nature, the circle symbolized protection, the triangle, stability, and the triple helix, ascendance, change, and the unity of mind, body, and soul.As time went on, things became associated with one another, and more and more symbolswere created.You can see the cause and effect with your own eyes, dear.It's clear when something is related and when it isn't.If the outcome isn't what we expect, these symbols must be incorrect.
```

### [20] hash=`263e1ddc57fe10cf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p1`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（01.对角线中.1/12 20:30）

```text
But it's not their physical form that's wrong.Physical objects never lie.It's the meaning and concept given to them that are wrong, you see.Objects are just objects.A match is just a match, not the illuminator of the moon.An animal is just an animal.The circle and triangle are only shapes.And you are just you.
```

### [21] hash=`652199b2e00b9337`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p20`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（20.古希腊悲剧.1/13 05:45）

```text
The key.Lillia has verified Arcana's location.She is still on this island.We still have a chance to stop her before it's truly too late.We should go now, Sinetto.We have 15 more hours until the storm.
```

### [22] hash=`b7d05a9e1d5c72d1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
We've got signal Zeno has restored communications with team timekeeperVery well, we will leave you to itJust to confirm before we go the operation Zeno is currently undertaking has been approved by the pack security council, right?I am most pleased to see youHad you a pleasant stay on this island miss verton are they not an intriguing flock of people?Their wise ones draw a circle at their feetI can't fathom your motives.
```

### [23] hash=`cb2eff422eb35131`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
If you came here to incite hatred and recruit the pure-bloodArcanist on this island, you may now walk away with satisfaction.If you wanted totake the island as one of your bases, you could have done so after the cleansing ceremonyfailed.But you did nothing.You just stood there.Why?Information can become muddled and vague wording can lead to mistakes and contradictions.That's why the island values math as a more precise and truthful language.
```

### [24] hash=`437f58384fc4a034`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
They mock language for its ambiguity, scorn its flaws, and ruthlessly expose its inconsistencies like they did during that debate.The pact on this bangle is of a similar nature.I see.It forbids us from actively attacking, but what is considered an attack?She's still there, looking down at us through that portal.She's...waiting for something.Everyone, it's almost time.Xeno will start any minute.We need to complete our preparations as planned and force Arcana to show up.
```

### [25] hash=`8ac8d8ce5779e299`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
Easy!If we finish off all her minions, there's no way she'll just stand by and watch.The big guy up there is mine, you deal with the rest.Trying to gain air supremacy?Not under my watch.I'll send that outdated hunk of scrap metal crashing to the bottom of the ocean.Airspace cleared.Preparing now.Just like the battle simulations.I will not allow the tragedy in Chicago to happen again.Timekeeper, it's time I showed you what my training's been for.
```

### [26] hash=`12dc612fb91bfb77`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
Start running?Timekeeper, I've defeated the enemy.Beginning preparations now.No time to think.All hands and all the members of the band combined!Timekeeper, there's a gigantic creature emerging from the portal.We must complete Stage 2 as soon as possible.We better finish it off before we start Stage 3.Copy that.This is a critical moment.Everyone stay alert and await my command.You may be-Timekeeper, please allow me to assist you.
```

### [27] hash=`1ae5b0d5944bd303`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
Another giant is newly made this year!Is this creature changing its afflatus to match that of its attacker?Huh a mimic strategy clever, but we can also use it to our advantageEveryone rotate your arcane skills make sure we always have the stronger afflatusLet's teach it a lesson in improvisationGet it over quick!Until the torch is lit.Enemy's ritual has altered the environment.Please be careful.Take cover.
```

### [28] hash=`cc5d24e0c0296349`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
I'll send it back into outer space.The time comes to speak of truth.The moment of utterance.The scale of your soul has tilted.The balance needs to be restored.The creature is defeated.Narcana has emerged once again.Timekeeper, stage 2 is complete.Cool!Now we just have to activate it!No, things are going too well.Like this has been rehearsed.What on earth is she trying to do?There's no time, Fartzen!
```

### [29] hash=`123e2ddcafbf0ec1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
You're right.We've put too much time and effort into this plan to not carry it out now.Senato, Lillia, Regulus, assume your positions.It's time to enact the final stage.Their maturity has been the Foundation's goods.Ms.Sophia, is the guiding one really not coming with us?She...Are you saying...?Fret not, my child.You heard me true.I shall die today.Timekeeper, location Alpha is ready for the ritual.
```

### [30] hash=`0f4e2065916a9c2f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
Location Beta, ready!Mr.Apple and I are ready!Good.Requesting to use the Advanced Arcane Skill, Afaroy Aram, number 000262603100008to teleport a top priority threat to the Parmenida's base.Loosen up and enjoy the ride!Bye!Launch sequence initiated.Starting countdown...30...29...28...The target has not reached the designated location.I repeat the target has 151413 large-scale arcane ritual detected aphoroi around verified life signal detected
```

### [31] hash=`60261587ad5efce7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
Target is in position initiating detonation sixfivefourthreetwo oneVacuum bomb detonatedNo arcane energy detected.No life signal detectedtarget eliminatedAdmiral, we might have a life signal, but there's too much interference.Give me that.It's nothing.There is no sign of life.It was the wind.So that means a triumphant victory.A salute to you, Admiral, and to the Timekeeper.Our efforts for peace have prevailed, and we have emerged victorious.
```

### [32] hash=`38b35020fb985655`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
Let us forever remember this day for its greatness.Glory to all who fought for this!We did it!A bullet is among us, right under this roof.It serves no army, no country, only peace.The heavy rain at the end of the century dissolved and washed away many of its comrades,but it was lucky enough to survive.Few would hesitate to choose a life of freedom over the achievement and satisfaction of a job.Given the short lifespan of a bullet, why would it choose anything else?
```

### [33] hash=`74d93507b5c1ea11`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p21`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（21.手影戏.1/13 06:30）

```text
But its boss, the General, has more to think about.What are they going to do next time?Will this bullet be put to use when the rain comes again?A big shot, dear.
```

### [34] hash=`66599c9a72569da5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
Drink thisIt will help relieve your painWorry notIt's not made from the grapes on my head29 are there any other injured that have not been found yet.I've scouted the islandEvery remaining member should be here.So you have means the members not here have joined manas vindicteIs six still in a coma miss Marta to you or the alone infinite the non-subsistent?The ineffable I call.Grant me inspiration of nature.
```

### [35] hash=`e4026a3cd8f4f685`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
Guide my soul with truth.Give me power of enlightenment.Tear off from the web of ignorance.Redeem me from the evil.Hatred and what throttles me down.Break through the ground of bad.Corruption's chain.The carapace of darkness.The living death.Sensation's corpse, the tomb I carry.Learn the beauty of truth, the balance and limitations of all.Are you still praying?Or are we praying to answer us?For generations, we have searched for purpose and meaning.
```

### [36] hash=`2258406bd0daeb39`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
But now that the truth is lost, what is left for us to live for?The side effects are completely random.Among the current samples, the probability of no sideeffects occurring is 0.52%.And of the 81 recorded side effects, 39 of them will causeirreversible damage to the biological body.24 will permanently alter the composition ofthe castor's body, functioning.And 18 minor effects will cause only minor,
```

### [37] hash=`1efe2c596cc32c78`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
superficial injuries that do not affect daily functioning.Laplace's archives has enough rituals to protect casters from the minor effects, butthe other two categories are highly lethal.After 72 experiments, the diversity of side effects has decreased significantly.It is unclear if this is due to repeated testing on a single subject or due to alimited range of possible side effects.More than 90% of these effects are related to concepts such as dirt and dust.
```

### [38] hash=`71b5e0fb49f451b2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
Is it because of the origins of this ritual's power?The number of recorded side effects is 86, not 81.When did I write these five down?Madame Lucy, Zeno's plan was a success.With the help of Team Timekeeper, the leader of Manus Vindictae was teleported to a desertedmilitary base and targeted with a thermo-barric weapon.It was a direct hit with no signs of life detected.The momentous event was captured on camera in the Observation Room.
```

### [39] hash=`69803986584cc2c7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
A tremendous victory.Please extend my congratulations to the Admiral for this remarkable feat.Also, you have two call requests.One is from the Timekeeper, which Laplace received shortly after the battle withManus Vendictae.She is requesting remote assistance to help the Aperon decode a numerical code relatedto the storm immunity.Put her through immediately.And the other call?It's Cacania, the Viennese Arcanist who helped investigate Marcus in acquiring the ritual.
```

### [40] hash=`aa294065a399dcf7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p22`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（22.致传道者.1/13 12:00）

```text
We have updated her the progress of the study and the potential side effects of the incantation.But she insists on knowing the right pronunciation.
```

### [41] hash=`e1f17c2830432e14`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
No, we are not aware of that.37 and I had just entered the cave when the investigator sent back the ritual.I see.Thank you for the thorough explanation, Madam Lucy.I'll make sure to inform the members of Appirin.If possible.Could you kindly explain this to them again after we set up the communication device?Next thing's the acoustic components.Totally understandable if you don't have any on hand.Regulus, can you help me find some...
```

### [42] hash=`24e8802bb7536fa6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
What are you saying, mate?Of course this great disc jockey would have the acoustic components!I'll have you know, I made friends with the Dolphins as soon as I had the chance,hoping they'd retrieve some of the radio components from Apple II.Chilly Bell!Have a communicator equipped with a speaker.Before, there were too many years for one tiny radio.What?What now?Another attack?Not quite.That's the sound of our colleague, Medicine Pocket.
```

### [43] hash=`9f789a70592e3df1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
How goes it on your end, Burton?The storm is only 8 hours away.Has the immunity zoneon the island stopped shrinking?I think so.No one in the Hall of Appearance affected by the storm syndrome so far.Theimmunity zone seems stable for now.Man has been dictating the humans have left.Thereshould be no further destruction on the island.Hmm, so the decay of the immunity zone is not linear.It seems to be influenced by the islander's mindset toward the truth, and it eventually reaches a stopping point.
```

### [44] hash=`83b1ffa9dfdce33e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
Could it be that the ritual on this island, rooted in the power of faith and belief, serves to amplify only the radius of the storm immunity?Fascinating.That can wait, Research Rex.There's one thing I'd like to confirm, Timekeeper.about the question miss 37 asked in the cave how can we escape the darkness ofthe phenomenal world and be freed from the emanation forever to my understandingthat is almost the same as asking how we can be immune to the storm and 37
```

### [45] hash=`5cb02a6872896155`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
also said the transcendental truth was beyond the limits of her mortal flesha parent answered her with an eerie sound one that could drive anyone madjust by hearing it it was then that the scroll six gave her unfurledand transcribe the sound into a string of numbers,providing us with the code.Yes, that's the key to our problem.We both received a solutionto the same question simultaneously,immunity against the storm.
```

### [46] hash=`ccca0d12521c6720`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
This could be our Rosetta Stone timekeeper.We found our own Rosetta Stone!Rosetta Stone?Allow me to explain.The Rosetta Stone is a stone tabletinscribed with a decree in three different languages,hieroglyphs, demotic, and ancient Greek.Hieroglyphs were the sacred writing for the divine, while Demotic script was known asthe language of the people.Both scripts were ancient Egyptian, lost to time when the tablet was discovered.
```

### [47] hash=`4a28909ec5a3b96d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
However, because scholars were still able to read ancient Greek, and through comparingthe three inscriptions that all said the same thing, they were finally able to understandthe hieroglyphs.And now, we too have our own set of inscriptions to decode.The first is similar to hieroglyphs, as the truth Ms.37 heard in the cave is completelyunintelligible and can drive people insane just by listening to it.
```

### [48] hash=`6c48b1f5cfed8aa3`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
The second is like Demotic Script, a ritual we obtain from Arcana that can place a curseupon those who read it aloud.It cannot be handled by ordinary people.Finally, the numerical code you shared with us is like the readable Ancient Greek,without any divine powers but crucial in deciphering the other two inscriptions.unlock even deeper knowledge that only belongs to the Divine?Exactly.We're looking for the same answer to the same question,
```

### [49] hash=`607de096a207e978`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
like how the same decree is inscribed onto the tablet in different forms.And just like the inscriptions on the tablet, we have three versions of the ritual.If we can delve into the essence of the ritual and master its inner workings,we may eventually transcribe it into a side-effect-free ritualthat can be used by everyone!Yes, it should work, because the nature of the universe flows in all things alike.
```

### [50] hash=`94329f84f642de98`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
I'm glad you think so, Ms.37.Your hypothesis is based on too many assumptions, Ulrich.It requires further refinement and confirmation.We now have valid incantations.We should continue in this direction.You mentioned the word transcribe just like the Timekeeper did.It holds the answer to improving the ritual.You mean?The scroll you mentioned that can bridge the gap between you and the supreme existence
```

### [51] hash=`7a4f7526671f2e3d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
during communion?It is the scroll that transcribed the eerie sound and saved 37 from the lethal side effects.Does this mean it could potentially lessen the negative effects of the immunity incantation?Wait, Madam Lucy, let me take it from here.We would like to borrow this scroll for research.If you lend us this scroll, we will make significant advancements on the research,and we promise to provide every assistance you require in the future.
```

### [52] hash=`c560d4fcbcde4655`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p23`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（23.碑文辞书.1/13 13:00）

```text
Lend you the scroll?Are you asking us to give the legacy of Epiron,our most cherished possession to you?A scientific research organization that serves humans?Why not?We are seekers of truth, are we not?
```

### [53] hash=`44b33b94e660b5f3`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Heed my words, 37.That scroll is a sacred relic passed down from the wise sages of Epiron,safeguarded by the Sixes and entrusted only to believers who brave Epiron's test.It has the power of harmonization and reconciliation.You may keep it until youfully grasped the secrets shared with you by Epiron, but you will not share it with someBefore joining the school of Epiron, my people and I had wandered the world for ages.
```

### [54] hash=`563449c518d77bd8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Our long lives made it difficult for us to truly fit in with the world.Daughter of Truth, I implore you to hear the words of this old soul.Humans have indeed achieved incredible feats, and their enlightenment has even touched my soul.But unfortunately, most humans do not have an inherent respect for knowledge or its boundaries.They only chase after power blindly.I have experienced it first-hand.I tried to guide and persuade them, but ultimately I failed.
```

### [55] hash=`65283b2adc02d15b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
That is why I am here now.What you are deciding to share is not only knowledge, but it is a ritual, a piece of power.A ritual, designed for harmonization, created for the devout believers and created for thesages seeking the truth.Yet, on the other hand, it can also be used for unspeakable horrors,such as silencers on guns, suppressors on rifles, or even on nuclear bombs.It won't.888, I won't let this happen.
```

### [56] hash=`8bb7d2a8d12581ae`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
I promise.You can't promise anything, Miss Furtin.You're too young, too inexperienced to comprehend the dark nature of history.But it's the truth we're talking about.What could possibly outweigh the truth?If all it takes is lending someone a scroll to unlock unspeakable secrets, why not do it?Haven't the failures of the past four years proven that a stagnant mindset does not bringforth the light of truth?
```

### [57] hash=`0fb34712a98cec83`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
As individuals devoted to critical thinking, should the pursuit of truth not be our primarygoal in life?My brothers and sisters, do not let hatred stop you, and don't let the dust of thephenomenal world blind you.Two hundred and ten!And remember, it was thirty-seven who passed the test and earned the scroll.It is her rightful responsibility to handle this situation.Otherwise, what other choice do we have?
```

### [58] hash=`4f9a1d4c68b74466`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
I have made up my mind.I will share this scroll with Laplace.We will decipher the code together.The truth is the truth.It should not be swayed by anything else.Everyone, cost your pebble if you agree with me.Swear here, he too would have called for a vote.Miss Lilia, are you certain about this?Absolutely.See the nice weather today?Much better than the day we landed.No wind, no cloud, the clear sky, and that giant moon.
```

### [59] hash=`87970de11a87d5cd`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Come find a better day to deliver the package.It's just to the headquarters, not even going outside of Europe.Three hours is more than enough.I'm done being stuck on this suffocating island.Nobody can stop me from taking this flight.The headquarters are at least 768 nautical miles away and you have no protection during the long flight.It's dangerous.And we have only 7 hours until the storm.Dangerous?
```

### [60] hash=`3ba17f2012996745`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Maybe.But this is an exhilarating flight in the storm, Saneto.What better chance than now to push Zeno into updating their flying manual?Besides, what's wrong with a bit of oil painting on me?Should be a nice badge of honor.Mate, it's quite a distance.Just be sure not to go toppling into the Mediterranean Sea.Red 38 is no way an apple the second.Uh-oh, Manus Aletius?We didn't kill them all off?I don't have time for you, little stingray rats.
```

### [61] hash=`f1d9f27ef762a1ed`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Still got your speed, huh?I guess the death of your boss didn't faze you much.Oh, a Manus aircraft?Worse a fight!Haha, breathe on!Your downfall will be an explosive orchestra over the waters!Look at my back!Yes, Ms.Tider has derived the formula and my team has finished designing the prototype converter.Now, we just need the big wigs upstairs to approve the experiment application.This is an unprecedented chance to rob this storm of its energy.
```

### [62] hash=`ca749f40d62b5760`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
I wouldn't miss this for anything.The Scroll of Aperon has shown great potential in protecting casters from the ritual.It is expected to outperform the Coleman protection rituals.The sheer variety of side effects is concerning, but we already have a list of 122 cursesand their effects.Once the scroll arrives, we will test and record its reactions to each of the effects.This should speed up our analysis considerably.
```

### [63] hash=`6034914d44411e1b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
An ugly plan it is.There is no grace or beauty in this approach.It is purely driven by practicalityand uses clever tactics to make things fit.How typical of imaginary numbers.What?It sounds pretty cool to me.Taking advantage of the storm?It's about time we plundered it instead.It really looks like we should throw this plan into the sea.You're not trying to comprehend the ritual, Vertin, but scrambling to make use of it before the emanation arrives.
```

### [64] hash=`9f3885a05887ce04`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Isn't making use of it enough for our purposes?No!Theory is incomplete.You will be hindered by impossible obstacles in no time.Mister, could you show me the incantation?I want to see it too.Laplace is looking for a safe method to deliver the incantation.Given the incidents before, some time is required for the application procedure.Once received, please do not read it out by any means.The side effects are extremely deadly.
```

### [65] hash=`3f1a219dbf90ef95`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Apologies.We took some time to test the delivery methods.For your safety, only the text of the incantation will be delivered.The exact pronunciation will be sent to the timekeeper later.Thanks, mate.Since the island has no visual communication, we will send the incantation letter by letterthrough a cladney plate, a technique that converts simple patterns to sound waves.Ah, enough with the mumbo jumbo, there's no time for details.
```

### [66] hash=`04bd7883c11cb4ff`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
Anyway, Timekeeper, we'll need the help of that lady, Ms.Radio, right?Huh?Yes, somebody please find her a metal square plate, fix it on a sturdy base, and poursand on it.Now, a special recording will be sent to you.Please stay by the edge of the plate, embrace the sound, and, um, uh, groovealong.I assume you mean vibrate?No, no, no, no, no.That's just rude.Yes, exactly.If all goes well, the vibrations will move the sand and visualize the text in a pattern.
```

### [67] hash=`bdc0a0d5e8ca5f9d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p24`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（24.历史的回环.1/13 14:00）

```text
We have 12 recordings ready, each representing a letter in the incantation.We'll play the first one when you're ready.Oh, of course.My pleasure.First one's done, Mr.Ulrich.Right, 11 to go.Incantation?Are you reading it in your head?Don't tell me even thinking about it can trigger the curse?No.It's just...I can read this language.37.I think I know what it says.It means...The First Circle.
```

### [68] hash=`d9e38ef9f4f84d2a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
The First Circle.That's what the Incantation says?That's it.The investigator in Vienna reported a similar thing.An ancient miracle.A circle of salvation.Akana even drew a circle in the air while saying it.She did it so nonchalantly, as if it were a meaningless gesture.We didn't think much of it at the time.Once we confirmed that it did not affect the casting of the Incantation,we forgot about it and moved on.
```

### [69] hash=`e7fb058100dbe8e2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
Can't believe I overlooked it!This is not your fault Ulrich.The gesture was overlooked because it did not really help the research.Our focus was on practical application rather than understanding the incantation itself.If the incantation means the first circle, how will this be helpful to the research?Well, Vertin, I don't know why you can read it, but I do know that Gal is thrilled by your interpretation.
```

### [70] hash=`2f04821d16dc3f69`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
because you mentioned her favorite shape the circle the essence of theincantation is a circle what kind of circle is it topology any closed curve ona plane can be classified as a circle told youFertin let's go back to the Rosetta Stone hypothesis based on thehypothesis if the incantation in the numerical code share a common essenceWhich is the key to the storm immunity and we now know the incantation refers to a circle
```

### [71] hash=`53214c969f54c10d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
Then the essence of this numerical code should also be a circleRight.YesBefore this conversation.I had no idea which direction to takeThe numerical code could be a snippet of an incantation or it could be a geometrical ritual arrayI had a lot of theories to go onbut testing them could take weeks or even months.Worse yet, if my line of thinking was completely wrong,we could waste decades of time and effort.
```

### [72] hash=`99b0acd3b5822e06`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
But the Rosetta's Stone Hypothesis is easy to verify.Let us suppose that the Incantation and Numerical Code share a similar essence.We know that the Incantation does work as proven by the Awakened.If the Incantation is a circle,Then the numerical code should also be circular in nature, and has the same effect as the incantation,which is a circle that saves people from the emanation, and can also be experimented with by the awakened.
```

### [73] hash=`12a2cbfaf7d060dd`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
If the experiment works, then the hypothesis is true, and vice versa.I see what you mean here.It really is an easily provable hypothesis.The first circle?Yes, it was the timekeeper who translated the incantation.And according to the investigator in Vienna, Arcana also drew a circle when she cast theritual.But experiments have shown that the gesture has no effect on the ritual.We thought maybe it was a symbolic gesture.
```

### [74] hash=`c8a0993d6bc1e203`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
No, no, no.It is no way just symbolic.Arcanists excel at condensing their experiences into symbolic representations.An unknot could be a variation of a closed curve.A knot!Knots were how the ancients of the Incas and Chinese collected data and kept records.But which knot is it exactly?The Jones polynomial of the trefoil knot is t plus t cubed minus t to the power of 4.The figure-eight knot is t to the power of negative 2 minus t to the power of negative 1
```

### [75] hash=`dbca423cbac48cf6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p25`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（25.最初的圆.1/13 15:31）

```text
t to the power of negative 3, plus 2t to the power of negative 2, minus 3 times t to thepower of negative 1, plus 3, minus 3t, plus 2t squared minus t cubed, plus t to the powerof 4. See, Verten, appear and give us the answer.The key we've been looking for,the most profound secret, the language of the divine.No sound or text is needed,Madam Lucy, is the signal dropping?Madam Lucy, can you hear us?

I can.
```

### [76] hash=`743eb256d9a5db69`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
I never thought it would be the Time Keeper and the Aperon Arcanus who'd solve the problem.But now even humans can cast this ritual.Indeed.The knot is the physical form of the ritual we were looking for.Surprisingly, the numerical code yielded practical results.I thought it was necessary to report this to the Time Keeper's organization.It was her contribution.But it did not go well.Forgive the interruption, what's a knot?
```

### [77] hash=`c59a5a3c159e4f52`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
I will be glad to answer your question.Knot theory is a branch of algebraic topology.In mathematics, a knot refers to a connected closed curve in three-dimensional Euclideanspace that does not intersect itself.They can also be described as shapes in three-dimensional space that are homeomorphicto circles.Knot theory focuses on the entanglement and configurations of closed curves in three-dimensional
```

### [78] hash=`7320bbe64a7d5944`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
space rather than the curves themselves.Since all closed curves are homeomorphic to circles, they can all be topologically categorizedas circles.A knot equivalent to a two-dimensional circle is called an unknot, and...I don't mean to question Laplace's expertise, but this approach may not be the best solutionfor widespread implementation.As it turned out, presenting a technical report was much too premature.
```

### [79] hash=`71d5f16bf96ef490`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
We should have a complete and official report once the immunity gear is produced.Maybe you can change your approach the next time you report as a foundation.I simply gave them honest answers, but this solution is deserving of widespread implementation.All we need is a piece of rope and tie it end to end,and spend three to five minutes to make this knot.This can be done anywhere, at any time, by anyone using any type of cordage.
```

### [80] hash=`6c4e8dcca1a5556e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
The oldest, fastest, and most basic ritual, the key to braving the storm, is a knot.Why didn't you tell the House of Integratus?I'm sure they would have funded us generously.I will make sure to put it in my interdepartmental report, but at this point in time the knotonly functions like an incantation.It is not suitable for widespread use until the research on the side effects and theconverter are complete.
```

### [81] hash=`1d878d3ea9e57d19`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
In any case, I've completed all the tasks you assigned me.My last plea is, please never put Ulrich and I on the same team again.I'm surprised that you're not in the lab.Something bothering you?Wait, don't tell me you're charging here.Excellent job, researcher Adler.You have proven that you are keeping the locations of public outlets in Laplacein mind, which is a positive sign for your re-socialization.
```

### [82] hash=`25faaadbc1206cdf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
But I am powering up to reach my optimal condition, preparing for what is to come.The scroll of Aperon.The final piece of the puzzle.The key to minimizing any negative effects caused by the incantation.Wow!The designers on artificial semnambulism could use some of this inspiration.Look at the clouds, painted with a syndrome of colors and interrupted by a glorioustrick of rainbow.It's truly a masterpiece.
```

### [83] hash=`dcfa6dc835c98245`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
Funny.They're flying towards the headquartersout of instinct.Maybe they can sense immunity zones.These little beasts would make fora good study.But I'm not in the mood to take any prisoners.Fuel and ammunition arerunning out.Maybe I should storm the vice president's office with them.But otherPeople might get hurt there.Never mind.Hmm, dive into the lake?But the splash might wet the scroll.Wait, isn't that...
```

### [84] hash=`835eb528cc8f9b71`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
Ms.Lillia, this way.Ha!Good timing!Enemies intercepted.Ally landed successfully.Ms.Travis, the Illitiaus are all ensnared in vines.The winds of triumph sweep through the woods.An excellent flight, Ms.Lillia.We will take it from here.Come, everyone.We shall vanquish our foes with the aid of the woods.The reddish woods are watching you.I weave the gown with thorns.You shall repay with sacrifice of wounds.
```

### [85] hash=`9aef28c4c7fef403`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
The special operations squad is ready to go.Dr.Kakanya, are you really going to stay here?Don't worry about me, young missy.This won't be goodbye forever.I was born and raised in this city.This is where I came from, where I lived and where I belong.This is my whole world.I despised the maggots under its golden surfaceand fought for the justice and fairness in our society.But I also cherish every detail of this city.
```

### [86] hash=`b984a6723e2b04a6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p26`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（26.银镜与纱幕.1/13 17:45）

```text
From the intricate carvings on the theater columnsto the dirt trodden by dock workers.All of these things make me me.My family, my friends, my people, and my operas and culture are all here.I never once thought about leaving this place.I have never thought about destroying it either.Being washed away with it would be a just punishment for all my sins.I wish I could be as brave as you are.Thank you, Miss Clara.

Hurry, ladies, before any of us turns into one of those exquisite paintings.
```

### [87] hash=`be80eafe67e9772f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Six is awake?Perfect!Like the number ten!He will be happy to hear that I've cracked the code!The truth still shines!With some time, communication, and a flash of inspiration, we can bring it down from the unattainable skies and let its radiance illuminate all!Also proven that the truth is not out of reach or too distant to grasp!If she knows about this, she'll come back to us, right?I'm sure she'll be happy with what you've accomplished, 37.
```

### [88] hash=`dd303be1d46fb3ef`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Did 210 and 888 go to get 6?You don't seem that happy.The Star of Hermes deciphered the code of Eperon.She found a way to cross the emanation.We should all feel happy for her.Yet here you are, so indifferent.It is because you, too, know thatWhat has happened will not change, regardless of whether she figures it out or not.A meagre ritual to save people from the emanation is nothing compared to the disruption of the law above.
```

### [89] hash=`0417b80f92da2c89`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
It also cannot change the fact that our faith is dead.We're talking about how the island has sunk, and we're now sailing in a tsunami.A tiny miracle, a spark of inspiration won't save the ship from the wrath of the tides.To be honest, Mai was surprised that she asked such a practical question.I guess the trivialities of the Phenomenal World did eventually affect her.It's a shame that many others lack her determined will to see beyond the void of our broken reality.
```

### [90] hash=`7af3f5d10ae02a67`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
What's your point?Can't you see?I'm getting a rise out of you.Who would have thought that our great, perfect, honorable leader of the School of Apeiron has been an Eyelist all along?You never revered the truth, did you?That's why you kept us in the dark for four years.You never respected our beliefs for a second in your life.The people who seek the truth are more important than the truth itself.I may not understand that ever-shifting number, but I do understand and respect
```

### [91] hash=`eb2aa789f81d97f7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
the people here.So you know the secret.What now?Now that you know the truth could leadnihilistic void, I wonder if you would abandon our doctrines, our wisdom, and our inheritance,and stepping to the darkness in a fit of rage.When truth fails, sophistry prevails, correct?Ha!We cannot deny that fate, the unspeakable, holds wisdom beyond our understanding.One you told me in the cave?The trial is over.
```

### [92] hash=`ef5bb273c7eacd59`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Why mention it?You should answer my question first.Are they holding the ceremony outside the immunity zone?I told them to go to the meadow near the top of the mountain where they will be completely safe.I've checked my calculations over and over, leaving no room for error.888 must have made a mistake.I need to warn them.37.Either be wise, uninvolved, and look on, or be practical, involved, and suffer.
```

### [93] hash=`ed75d590d65672c4`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Whichone will you end up choosing?Yes.In recognition of your extraordinary contributions, Laplace is honored to present you with thefruits of our labor.This knot is the result of our research.The knot has beenvalidated as a working ritual on both humans and Arcanists.With the help of other Arcanists, we found methods to avoid side effects and conductedsmall-scale experiments with success.So are you saying we can...
```

### [94] hash=`b948f4eb9fa36b9d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
However, since the experiment is still in its early stages, it involves a varietyof materials and complicated rituals that are not yet possible for transmission.nor can we deliver you any experimental equipment as the storm is about to makelandfall.The knot acts as an equivalent to the incantation, but it does notguarantee that we will meet the casting requirements or avoid the likely sideeffects.
```

