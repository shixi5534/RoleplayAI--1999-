# 剧情图谱抽取 · batch 020

- 角色：`wu_ming_zhe`
- 批次：**20** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.9」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_020.jsonl`

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

### [0] hash=`f047c818fb386ffb`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
If you're here to check on the progress, there is none.I'm afraid you'll leave disappointed, Madam Lucy.Send this to everyone.This is la unua.We must share this with everyone.La unua diaglo.Stop the transmission!The ritual is on!Question.Why don't people like the irrational numbers?Do you feel the same about them, 37?Be a little mama.count to 3, and to 17, but I can never count to something like 0.01 001 0001 00001
```

### [1] hash=`70e83ea764e653f5`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
let alone use it in calculations, and this non-repeating decimals would make a mess of the resultsand I can't keep the equations as simple and elegant as I wantBut your favorite, the circle.The ratio of its circumference to diameter is also an irrational number.Is it not?It's special.I know how it was found and what it represents, so I trusted to use it in my calculations.The same with E, logarithm 2, and root 2.
```

### [2] hash=`0ca0046d8c7b90ee`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
But not many irrational numbers are this convenient to work with.Some have no patterns, no simplest forms, and no end.I can't work out their digits, write them out, or calculate them.Not only are they impossible to pinpoint on the number axis,but there's an infinite amount of these irrational numbers.What's so funny, Mama?You're a clever silly goose, my dear.You don't dislike them, you just don't understand them enough.
```

### [3] hash=`1ca4a1861ec8f38c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Take our old friend root 2, for instance.The irrationality of this number can be proven through basic arithmetic, as it cannot be expressedas an irreducible fraction of integers a over b.Proof-by-contradiction is enough, with no knowledge of irrational numbers required.The presence of root 2 is prevalent in nature, and it is particularly noticeable alongdiagonals of a square.This means the system built solely on the ratio of integers was flawed.
```

### [4] hash=`fbf36c21ddfed164`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Yes, root 2 is simple, elegant, and one of the greatest discoveries in mathematics.It showed the existence of infinite incommensurable numbers, with root 2 being themost obvious one to find.This was how the tower of old ideas crumbled, paving the wayrevolutionary breakthroughs that catapulted mathematical analysis into uncharted frontiers.We discovered a kingdom beyond our traditional methods, one that's immeasurable, incommensurable,
```

### [5] hash=`0ad587a8b7953dc2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
and inexhaustible.Key to its gates is hidden in plain sight, in the diagonal of a square.If we get to know the irrational numbers better, we can be friends with them too!But, you haven't told me why people on the island hate them.Thirty-seven.You're awake.Sophia?How long was I out?You've been in a coma for a week.We...I have to find Six!I have to tell them now!Our circle...has been broken.Now we've learned some manners in Apeiron, haven't we?
```

### [6] hash=`c659b70273bdbc5f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Namely, to abstain from beans,never parcel off a loaf, and stay away from the white roosters on the road.It's beenso long since we last talked about these things.How time does fly.This rusty grainof mine is struggling to keep up.We should have waited until dawn to light the candles.The sun would have mistakenthe day for night and delayed its appearance in the morning.That way we would have hadmore time to talk.
```

### [7] hash=`95204ae77f40f70d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Indeed.You possess a far greater understanding of the laws of nature than your ancestors.It's only natural that you wouldn't relate candlelight to sunrise.But for the peopleof earlier times, there was a commonly understood connection between the two.Did the treesnot bear fruit after the Horn of Plenty was filled at the harvest festival?DidThe field not wave with grain?Does the lighting of a match not illuminate the moon?
```

### [8] hash=`4924e0756cea508f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
It's human nature to try to understand the world.Of course, at that time, mistakes were madeand some phenomena were attributed to the wrong causes.Some theories were developed from false facts.It was a time of symbols, you see.The flower represented blessings and harvest.The Ouroboros, the eternal cycle.The hawk, wit and astuteness, and the soil, safety and protection.Aside from nature, the circle symbolized protection, the triangle, stability, and the triple helix,
```

### [9] hash=`b0903fce72a0af6e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
ascendance, change, and the unity of mind, body, and soul.As time went on, things became associated with one another, and more and more symbolswere created.Ah, you can see the cause and effect with your own eyes, dear.It's clear when something is related, and when it isn't.If the outcome isn't what we expect, these symbols must be incorrect.But it's not their physical form that's wrong.Physical objects never lie.
```

### [10] hash=`4ead90ffa0bdabaa`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
It's the meaning and concept given to them that are wrong, you see.Objects are just objects.A match is just a match, not the illuminator of the moon.An animal is just an animal, the circle and triangle are only shapes, and you are justyou.Nothing's happening.Miss Virgin, your attention please.This is a public inquiry, and your answer determines the fate of you and your friends.There will be a vote on your punishment, considering the leak of the island's coordinates
```

### [11] hash=`b59bee7da20d8006`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
and the damages caused by you and Manus Vindicte.Yet, in the past two hours,you've looked at your watch ten times.Forgive me for being blunt.What could possibly bother you more than your sentence?My apologies.Let her look, 888.Doesn't it occur to you that time is also in the form of numbers?Perhaps she's waiting for her lucky number to come.Besides, what conclusions have the good people here made?
```

### [12] hash=`f09628db5677b60d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
We were brought together in this great hall today, for misfortunes have struck us in the past week.Manus followers were found dead in our sacred place, the Gorgon current was cut off, and a human army has invaded our land.There are also the territorial disputes, the threats from external powers, and the conflicts between our guests.As you can see, our guests have brought us quite the unexpected gifts.
```

### [13] hash=`da66147dc6ecc12a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
They will give us their explanations.But whose words should we trust?Those of the Foundation or Manus Vindicte?I swear on the Stone of Truth that I have no knowledge of the leak.We never gave any information to the humans.As we speak, the Saint Pavlov Foundation is taking measuresto mediate the territorial disputes from outside the island.But you did report everything here to the Foundation,and you don't know what they did with the information, do you?
```

### [14] hash=`99169274b525e786`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Right.A questionable defense, a doubtful explanation.Why should we trust her?We all know that the Foundation is closely associated with the humans.They are the false friends of the Arcanists,with their crocodile tears and broken vows,While many may have changed over time, their nefarious human taint lingers.Besides, why should we seek collaboration and assistance from an organizationthat's seven years behind us on the study of the emanation?
```

### [15] hash=`e5882a0544e304b7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
But rush not, brothers and sisters.The moment of decision has not yet arrived.Let's give our old friend Manus Vindicte a fair and equal hearing before casting our pebbles into the pot.Indeed, the Foundation's understanding of the emanation is seven years behind ours.However, our Manus friends here are unable to speak at all, let alone understand complexmathematical principles.Please enlighten us, Miss Arcana.
```

### [16] hash=`3bb3b006da742c4a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Why were swaths of your followers found dead at the door of our sacred place?Did our math lessons drive them to madness, causing them to bash their heads againstthe gates of truth like martyrs.So it would seem.What?Must confess that our followers were ill-preparedto take on the wisdom of the island.But we didst come seek mutual development with sincerity.I trust you are aware of the assistancewe have provided over the years in this world of matters
```

### [17] hash=`0174e018dbf41c4b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
which you, though reluctantly, relied upon.As to this debate, I was once told a storythat now seems fitting to recount.Share with us.Thank you kindly.Tis the story of the circle.A young artist told it to mebefore I arrived on this island.In the ancient past,amid a world of primitive instincts and ignorance,the first intelligent mind awakened,overwhelmed by the enormity of natureand dismayed by its own insignificance, the creature was shaken to its core.
```

### [18] hash=`c409253425ba88b6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
In an act of defiance, it drew a magic circle, shielding its powerless self from the formidable world beyond.This was the first magic, when the primitive man mastered the Numa withinand wielded it against the relentless forces of nature.In that process, man hath gained a deeper understanding of the boundaries and limitations of its power.This is the tale of the First Circle.The Circle shielded us, and its protection benefits thee to this day.
```

### [19] hash=`c3fb18561ea9ebdf`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
What I find intriguing in this story,man hath established its existence recognized its boundaries and learnedthe purpose of life all by relying upon this very circle 37 what's wrong 37 hasfallen ill what's going on is this a hailstorm no I don't think so those areAbraxas is falling from the sky.It's the storm.The storm of this era is here.Ms.Verdin, did you just say the emanation has happened?Just now?
```

### [20] hash=`de40af9945fc80cf`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
More precisely, its 24-hour countdown has begun.There's always a buffer period before the storm,during which the storm syndrome gradually spreads from the critical point across the globe.The symptoms are different every time,And we have yet to discern a pattern.With the help of Laplace Scientific Computing Center, the best we can do now is to senda 24-hour warning prior to the storm.Another minute has passed.
```

### [21] hash=`3078741013992d2b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Please remain seated, everyone.We are still in the middle of a vote.The emanation holds no influence on this island.The discussion must continue until a satisfactory conclusion is reached.No other subjects shall be brought up until then.Come here, Thirty-Seven.Can someone please bring her a blanket?Forty-Two, go with Sophia and check on those Abraxas's.Ah, good news.Good news indeed.We are freed from the pain of choosing whom to blame,
```

### [22] hash=`2842b6dbfd09b341`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
are we not?What?The emanation is coming.The tides of Numa will pour from above and wash away all trivialities.By then, human intruders and the international powers of this era,Along with the turmoil they brought, we'll all be dissolved and poured into the ditcheslike gunk.And we will regain our shores and return to the study of essence and forms.Numa has fallen ill.It's getting bloated, stagnant, and sluggish, drifting into the world of matters where ignorance
```

### [23] hash=`d63117d7be403264`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
reigns.Soon, the tides of Numa will wash over us, sweeping away the fragments of theYou brought outsiders to the sacred place.You betrayed the scripture's teachingsand angered a Puron.Of course, I may have jumped to this accusationas Manus Vendictae also intruded our sacred placewithout permission.People, as of now, there's no proofthat the emanation will influence the island.37's account is lacking.
```

### [24] hash=`e96fc615e19d2963`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
And we are still plagued by suspicions, accusations,and the damage is done to our home.We are to proceed with the hearing and reach a final verdicton both the Foundation and Manus Vindicti.I'm sorry.Please forgive me.I shouldn't have intruded the Hall of Truth, but...Sophia, weren't you and Forty-Two checking on the Abraxas?What is the matter?The Abraxas don't look right.Their beaks, no, their entire heads are melting into oil paints.
```

### [25] hash=`ad957712e82deda4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
and 42 we were on the beach suddenly he now I see it finally all makes sensethere never was the truth nor the transcendental everything is a lienothing but shadows on walls flickers of fire and fragments of reality no onewill survive the oblivion the island will be destroyed amid its conflict theStorm Syndrome.What'd he do to your face?888, stop conversing with him.We must subdue him.Now, Storm Syndrome.
```

### [26] hash=`9380e18187e7ca88`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Please, listen everyone.37 is right.Something's changed on this island.Your immunity to the emanation has been weakened.That's never happened in the last eight times.A feeble induction, my friend.Just because you've never seen a purple cowdoesn't mean it doesn't exist must we talk of logic now 42 has literally been emanatedfirst the army then the emanation everything's been falling apart since the outsiders arrived
```

### [27] hash=`bd279cea59137624`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
on this island the foundation and man is vindictive one of them must answer for thisthen you should also ask 37 and number zero what they've done in the sacred place tothat it isn't, in fact, the work of your arcane skills.As we went through your belongings, Miss Vertin,we found a golden sampling device.Enlighten us.What exactly is the Foundation looking for here?That's...Good, Vertin, good.Let the confrontations be louder
```

### [28] hash=`6d05b50d431a7b9e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
and the struggles be harder.I wonder what shall come of this.Silence.The debate will end now.Since we were unable to come to an agreement, furtherdiscussion is pointless.There are more pressing matters to attend to.This willbe the end of the Assembly and my decision will be the final ruling.demand that both parties leave this island at once.I respectfully acceptyour verdict.My choice much is that of Vertern's.
```

### [29] hash=`35bf2320ce9fa8fb`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
But may I ask for oneHe purged the storm syndrome with an arcane skill.I never thought it would be possibleThe light of intelligence has cleansed 42 of confusion.It is also what the island needsThe incident will be properly handled and my ruling stays unchanged.I expect your words to be matched by actionsMiss AkanaCertainly, it was a fair and just decisionIf only one could depart amidst such unfavorable weather
```

### [30] hash=`70e374beac4fb5e5`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
The first of man were intimidated by the enormity of nature and constantly tried to defy and escape it.Our ancestors, however, had the opposite reaction.They found solace in nature, which welcomed them with a nourishing embrace, sharing its vastness and sublimity without reservation.It was the perfect harmony, the moment the circle ceased to represent confrontation and avoidance.As we bathed in Apollo's illumination and wandered the tranquil shores, our souls resonated
```

### [31] hash=`4a0a7e16b6800959`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
and we were lifted to a higher wisdom.This was how we conquered our fears, emerged from ignorance and allowed ourselves to indulgeon the essence and forms.This was the rise of the classic man.May you all be blessed with the courage for reconciliation, the determination forPeace, and the devotion to nature, qualities no less noble than caution and defiance.You may all leave now.Exile Circle!888 was right.
```

### [32] hash=`52a486193d298728`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
I have enraged Eperon.I am responsible.We'll go back to the Sacred Place, test it, and ask it to share the Divine Light of Gnosisso we can learn the truth about the Essence.What I've done I promise it has been 300 years since the last challenger had their success in the cave37 are you aware that we have other means to cleanse the island even if you don't bring the matter to a pair onYes, then are you aware of the price you will pay should you fail its test?
```

### [33] hash=`1ab5265b4e3b6d90`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Then you shall have my blessing the headquarters has issued a noticeThe critical point of the storm is in Vienna.This type of storm syndrome involves a bodily transformation into oil paintings,primarily affecting the face, but sometimes spreading to the torso.It is often accompanied by delirium and an intense obsession with war.Like the storm of 1929, it was accelerated by social upheavalsresulting from the constant tensions Manus Mendicte created between nations.
```

### [34] hash=`3ec0779ae0dad82d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
This era...the effect.We're still safe around the Hall of Aperon.But there is no guarantee that we'll be safe here forever, right?Reminds me of Zeno's survival test.Seneta and I talked about this.We think the island is protected by a large-scalearcane ritual.The sudden decay of the island's storm immunity might be the resultof its changes, though I'm unsure of the specifics.Those people are doing something about it, right?
```

### [35] hash=`9f725d8644d16ca3`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
That leader with the rockstar hair, shouldn't he be taking action by now?Six has gathered all integers after the assembly.They're going to perform a mass cleansing ceremony.Thirty-seven also mentioned a test.I think they have more than one way to deal with the changes.To the best of this apple's knowledge,secluded pure-blood arcanist groups often have rituals that they keep to themselves.These islanders impart truths based on intellect and rationality.
```

### [36] hash=`66d3dd060c842a02`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Yet their doctrines are highly religious.Perhaps their arcane skills are passed down in a religious manner.Oh, very mysterious.Very arcane.I hope they're not all huddled together doing a mass at a time like this.And I'm more worried about us, Captain.Arcana asked for more time for both sides to withdraw, didn't she?Yes.Six gave us two hours to leave.That is to say, we must set out when the storm countdown reaches twenty hundred.
```

### [37] hash=`a8c4260a44722804`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
And before that, the stone bangle on your wrist still works, right?Yes, I can feel it.It would scold me whenever I thought about going to war with them.Huh, I see.So we only have two hours for the plan.Are you sneaking away from all this?That mask has made him crazy!Any progress?Not much.We've called all the experts here, but so far it's been a waste of time.Not even a bodily reaction when reciting the text.
```

### [38] hash=`b7c260a58251c36e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
It doesn't belong to any known language, nor follow any linguistic rules.Many are starting to doubt the accuracy of the incantation.After all, it was copied down by a novice investigator with her arcane skill, not her supervisor.Miss Marcus, can you confirm that the incantation you dictated was correct?Do you deem the reflection of Ms.Kakanya's arcane mirror to be accurate, factual, andwithout misinterpretation?
```

### [39] hash=`84e27dacd95e9d4e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Can you confirm that your arcane skill, Reed, was performed correctly and provided an unbiased,objective, and flawless interpretation?Please calm down.We are only verifying the details.The Foundation has dispatched a special operation squad to you in Vienna.Please make sure the two other Arcanists involved will return to the Foundation with you.This?Is this it?An ancient miracle.A circle of salvation.
```

### [40] hash=`941a18918f544783`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Auna Seiko.A tuna psycho?An inexplicable incantation transcribed by an Arcanist based on what she saw in the memory of another Arcanist recreated by yet another Arcanist.That's as convoluted as a dream within a dream within a dream to think they wanted an objective restoration.I mean, if Gnosis is so reliable and can really cross-check not only once, but four times, it should have long replaced science by now.
```

### [41] hash=`765b1cf9af37b76d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
With this level of uncertainty, we might have better luck asking typewriter monkeys to randomly give us the answer to the storm immunity.Adler?Why are you here?I requested his participation on the cryptography team.He is a human, but he excels in the field of cryptography.But, and why can't I be here?Is it because Greta Hoffman's my sister?And this, is this what a respectable and honorable member of the Foundation gave her life to retrieve?
```

### [42] hash=`6ff1920342a45f98`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Is this the ritual she died for?Oh right, it wasn't even her who retrieved the ritual.It was a student.You are not currently on the official roster.You can leave at any time.Leave?Why should I leave?Return to your stations, please.Voices!Those voices!The inaudible murmurs, the frightening whispers, they worm into my ears!I told you before!I wrote about this before!But you dismissed them as manic episodes!
```

### [43] hash=`87b6567ae046a0f7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Did you put on the mask?How else would I know that I was right?And now I know!I never ever heard them so clearly, they are screaming inside my head!their temptations, their promises.I just have to let go of my brain.Can you hearit?The benevolent mother is speaking!Now I can write the ultimate paper!Who is this mother?No!I can't say anymore!They've seen it!They've come for me!Suspend all research on the madness mask at once.
```

### [44] hash=`2e7fc42302c9c6e7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p58`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 1~5）

```text
Its dangers far outweigh thepotential benefits.Seal away all equipment and share only a controlledaccount of the incident with others.We cannot afford to have another researcher try on themask again.Now, clean this up.Yes, ma'am.Another dead end.Faraday's miracle.
```

### [45] hash=`7ba56ba7d7a3808a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
What is the status of the sampling, Simone?Any updates from the timekeeper?For the moment, no.The people on the island are still suspicious of the Foundation's motives,so she hasn't had a second chance to collect any samples.But she has called in an hour ago.We were informed that she will return to the cave shortly.She also warned us that the immunity zone on the island appears to be shrinking.The safe zone is not stable.
```

### [46] hash=`872bc3c516438fb3`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Hmm.Do you notice something?They are unrelated, Simone.The mask and the incantation are indeed related toManus Vindicte, but they are unrelated to each other.If the account of the Viennainvestigator is correct, one cannot help but question, why would Arcana notsimply give the masks to his old and her brother?Investigator Marx'sreport was highly lacking, making it challenging for us to infer what truly
```

### [47] hash=`81cba58b5c8487d6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
happened.I suppose we can be skeptical that the report is incomplete, but itIt is all we have for now.She did a good job, I could not have asked for more.We all heard it, an ancient miracle, a circle of salvation.The leader of Manus Vindicte promised a miracle, but the mask is far from it.The mask is a tool of control, designed to identify and enslave the believers.Matthew has demonstrated its effects for us, but this ritual is different.
```

### [48] hash=`7950847682c503e2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Do you mean the ritual is more sophisticated than the mask?Perhaps, but it is not entirely definitive.The investigators in Vienna completed their mission spectacularly,and now Matthew has proven that the mask is useless for our purposes.Its immunity was only a cover for its other functions.And the mask has powerful and irreversible side effects.Even if we find out how it protects the wearer from the storm,
```

### [49] hash=`b0632a8b0883b0b9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
We cannot use it on our colleagues.If this incantation is verified to be true,it will be our Promethean fire.This ritual is useless to us.Save yourself as Hubble.We're not getting anywhere with this.What?Explain yourself, Adler.What do you mean the ritual is useless?You barely sat down.My coffee's still hot.I don't need to waste any more time.It's simple logic.The current information is insufficient for cryptographic decryption.
```

### [50] hash=`7943f905b81a03ba`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
We're attempting an exhaustive brute force comparing every ancient text and recordto find the language or corresponding text.It's like looking for a needle in a colossal haystack.Even if we stumble onto a match, none of us can validate such a thing.A breakthrough in this regard is simply not possible.You can't be serious.And what is the basis of your reasoning?Have you figured out the mechanics behind the ritual?
```

### [51] hash=`82edfbcc94be8e8a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
I didn't need to understand the intricacies of Arcanum to deduce this.It was simple lo-So you never even tried to understand it?With your supposedly superior human reasoning,you dismissed all of our dedication and hard work just like that.Who the f- do you think you are?Matthew was right!You arrogant, clueless morons!Get out of my face, you humanocentric narcissist!Go to hell!was this really necessary I was just sharing my conclusion he worked in the
```

### [52] hash=`f053532cdac565cd`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
same lab as Matthew and he must have been exposed to the mask but hisphysical exam seemed fine is there an incubation period does he seem fine toyou now huh Williams put that down that's the only Conway automaton 5left after the storm security security we've got a code red aim and shoot the light that illuminatesso what are the implications for the decryption there were no unintended consequences we were
```

### [53] hash=`bf7a1c3d3cf8769b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
able to control williams in time and the conway automaton 5 he destroyed wasn't useful to ourwork anyway i am glad you kept the damages to a minimum since you are still here mr ulrichI take it as a sign that you have more to report?Williams was merely an accident, Pam, but Adler is a loose cannon on the team.We need to talk about this.With all due respect, I still don't understand why you put him on the team.
```

### [54] hash=`1d3adaa47c001e25`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
He may have made his contributions to Laplace, but that was eight years ago.Now he's just an irritating defeatist and a staunch supporter of humanocentrism.He never understood the Arcanum, or tried.His lack of knowledge on Arcanum is exactly why we need him.His human perspective will offer valuable insights on arcane rituals.The results of this study will not only be used to save Arcanus,but also humans who share the same world with us.
```

### [55] hash=`37f5d433920f7696`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
We are racing against the clock, Mister, and your report on personal disputes and racialconflicts has wasted 2 minutes and 37 seconds of our time.If he refuses to cooperate, you have every right to remove him from the team.That is your responsibility.Oh, I'm relieved that you survived your altercation.What would you like to report?I'm fed up with wasting time, ma'am.The setback with the mask has already driven too many people insane.
```

### [56] hash=`a62373724419e875`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
That's why you should take a look at this.I can logically deduce that our current direction is another dead end.The Incantation isn't long enough for cryptographic decryption.We will have to turn to ancient records.Perhaps we'll find something in age-old manuscripts, in tablet inscriptions, or in the memoriesof powerful Arcanists.But even if we find it, we can't validate it because none of us can cast a skill.
```

### [57] hash=`1fb92ef059dea846`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Low-ranking Arcanists can't cast high-ranking skills, even if they know the exact pronunciationand meaning of the Incantation.Gnosis is beyond reason like that and cannot be debated.It stems from raw intuition rather than logic and intellect, is shaped by personal experienceand natural abilities, and cannot be intentionally replicated, and is the most determining factor.It relies on the Arcanist's purity of blood.
```

### [58] hash=`586d37a3648f3333`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
The miracle ritual you hold such hopes for belongs to the leader of Manus Vendictae,a pure-blooded Arcanist whose power is beyond our imagination.It's like asking a toddler to solve Goldbach's conjecture.It's completely beyond the boundaries of our limits."But you are not an Arcanist.Why should you play by their rules?You are right.Arcanists differ due to the purity of blood.Researcher Medicine Pocket has already reported the linear correlation between the bloodline
```

### [59] hash=`cbd6729815dab765`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
of an Arcanist and their abilities, and has drawn a conclusion ten times more extreme.Then you should listen, that's their area of expertise.We know that our cryptographers do not have the power to validate the ritual, and we donot expect you to do that.All I ask of you is to come up with a feasible plan and to do it as a team.Your deduction is logical, but not practical or actionable, so I should return this to
```

### [60] hash=`afdcad15213dff90`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
you.What?Your logic is impressive Adler, but do not let it limit your thinking.You spoke of the boundaries of arcane power, but logic has its limits too, no?Knowledge can be obtained through various means, such as intuition, logical reasoning,empirical observations, and teachings from others.Your team is not the only one cracking the ritual through their own means.If you fail, we will turn to the others, and if that approach is wrong, we will
```

### [61] hash=`272730abdc28ab58`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
try another.If no solution is found before the storm, we will simply wait for the next one.What matters is we keep moving forward, no matter the cost.We must keep to the path, or we will be swept away like dust in the rain.If one team fails, you can still turn to the others.Warum dann?Warum muss es kreiter sein?What?Forget it.Just a bitter rational thought.The doves of the White Stone House are here.
```

### [62] hash=`d2646d9e1f454373`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Good.Someone closer to the limit has given us aid.Be ever so careful, dear.The fiery thirst for knowledge is blazing bright within you.Be careful not to put it out.Once, many Fire Thieves sat here, sipping coffee,as they tried to decipher the best angle to hold up their reedsto jam the burning wheel of Helios and steal his flame.The gods are selfish.They're stingy with their might.That's easy to say when the power's not yours to give.
```

### [63] hash=`24dfcd5097d098dd`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Knowing how to share is a rare virtue.Knowing how to share knowledge is a rarer virtue still.How can we transfer our wisdom into mortal minds?The gods pondered.Can inspiration be duplicated from one brain to another?It comes and goes like a gust of wind, so what can be done?Not yet, darling.We've only finished the prologue.However, there is a but waiting down the road.A sudden rain dampened people's enthusiasm for the future.
```

### [64] hash=`13e0c97ecefb355e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
The floppy disks and many clever minds perished in it.Some of the Fire Thieves grieved at the loss.They screamed and swore to retrieve what was lost.What about the rest of them?They returned to primitive chaos.Like coelacanths crawling back into the ocean after thousands of years of evolution.Once again, they became the proteges of Arcanum.Perhaps they made the right choice by leaving that useless science behind.
```

### [65] hash=`d2c7390e69ad5a69`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Who knows?The story of the Fire Thieves has only gone this far, Garf.At this point, no one knows what will happen to PrometheusOr what's inside Pandora's box?Any news from Zeno?They are moving as planned.The deployment will be complete within two hours.What about Arcana?She's found herself a good spot, overlooking all of us from up there.The center of the island where the number of people are heading,
```

### [66] hash=`09a9fe31c1a5beb4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
the entrance to the cave where Vertin and 37 are going,and the beaches in the storm.Nothing escapes her sight.Ha!Impressive!Maybe she's planning her escape.Is she also going to swim?Huh, it seems like we're in for a swimming competition.Speaking of which, it would be nice if those tortoise slowpokes could swim a little faster.Sinetto, I understand your plan now.But I still can't shake off a bad feeling about all this.
```

### [67] hash=`f4a08081142bd59c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Don't worry, Regulus.We have gone over this many times.The margin of error should be below 0.00025%.I'm confident that it will work.I know, I know.Spare me with the numbers.I know I can rely on you.Still worried about Vertin.Will she make it back in two hours?If she doesn't come back in time, who's going to take charge and guide us?We'll have to steer our own course, won't we?Yes, Laplace is gathering every piece of information they can find on the storm.
```

### [68] hash=`1bc20af1ffe7b714`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
The discovery of the asymmetrical nuclide R was already a remarkable breakthrough.It would help the immunity research a lot if the timekeeper could find something usefulin that cave.I don't think she's going to have a lovely time there, judging by what happened tome last time.Is it just me, or do you also find this a bit fishy?The dangers aside, using an answer as a reward?What?Is this deity some sort of answering machine?
```

### [69] hash=`6fb885d648e0ac81`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
In fact, a Pyrron is a philosophical concept introduced by the ancient Greek philosopherAnaximander, which means the origin of everything.It is the physical manifestation of the boundless, the indeterminate, and the infinite.Everything arises from it and returns to it.But it appears to serve a more practical purpose for the believers on this island.Ms.Marta told me about this.There are limits to the knowledge one can acquire even when using numbers,
```

### [70] hash=`b506a3403c588fa2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
which are considered closest to the essence,but appear on as a boundless limitless existence.If we wish to seek knowledge beyond our own limitations,we must turn to it for help.To the best of this apple's recollection, the more ancient, abstract and intangiblean entity is, the more likely it possesses arcane powers beyond our fathom.By communing with the supreme existences through sympathetic magic, worshippers could
```

### [71] hash=`be344fb3a172a0d6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
gain the guidance of their transcendental gnosis.They would, of course, exact a price from the worshippers as well.Could you be more specific on that, Mr.Apple?What's the price?Start with the number that has the largest absolute value, 33.Another giant could be killing that.Not that big of a deal.I thought the next question would be the Ford Circle, the Monster Group, or Hilbert's Infinite Grand Hotel.
```

### [72] hash=`ee3d31e770991367`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Thought it would be 6.Hello 6, are you the real thing?Yes, I'm the real 6.He's so sureWhen it comes to the essence, we are all shadows cast on a wall by a flickering fireHow do you know you're the real six?Did you just smile?Now I very much doubt that you're real.I didn't and I am the true sixThis gate has always been guarded by a six.I have a bad feeling about thisI think the question we're about to answer will be very simple
```

### [73] hash=`b2aeec1d0043b017`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
It's just a formality, isn't it?You'll ask a question and let us through.I've seen you do that on other tests before.Formality is also important.Only the essence is important.Only the forms are important.This is a question about the essence and forms, 37.Please pay heed to it.As for Miss Vertin, we only expect you to lend a patient here.Very well.Thirty-seven.If your pursuit of truth were to lead to the destruction of your faith and beliefs, would you still keep going?
```

### [74] hash=`2a48adea75715a1c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
The question is that, if my pursuit of truth will be the destruction of my beliefs, I came for the truth, and my faith is the truth.Why would the truth be destroyed by the truth?If it's because I did the calculation wrong, I'll go back and do it again, and next time I will do better.What if the essence of truth is there is no truth?Also a form of the truth, its non-existence is an answer in itself, is it not?
```

### [75] hash=`6b17565d2e6f088b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
You're speaking like 210.Are you really 6?If what's behind the gate is really the truth, why would I give up the truth for falsehood?I see.You've passed.As a reward, I will bestow upon you this sacred ritual.It will bridge the gap between you and the supreme existence during communion.Was that it?You didn't even ask a question that posed a real challenge.See, Furtin, I knew this was just a formality.
```

### [76] hash=`5d976c32b8556dd2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Furtin?No, 37.I think this question...37, there are some words I'd like to share with you.Not as six, but myself, who used to live under the name Atticus.We know the story of Socrates' life, how truth and politics are at odds with each other.Either be wise, uninvolved and look on, or be practical, involved and suffer.I hope you will remember your answer when the defining moment comes for you.We should go, Vertin.
```

### [77] hash=`ff1f8511953a1d04`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
There's a long way ahead.I hope the next question will be more fun.Three!A good number!It's the 8th twin prime, the 8th lucky prime, and the same combination as 37!But sadly, you're the 21st prime number, which makes you lost them perfect.Fertin!Are you turning back like Regulus?But you're a Zero!You're not an Irrational!No, I won't go far.I will wait for you here.This is your gate to open.It is your question, your answer.
```

### [78] hash=`8e66774a8a1170d6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
I will stay here and watch over you.If you encounter any danger in there, I will come to your aid at once.But don't you also have a question to ask Aperon?Aren't your doubts unresolved?See you soon, Thirty-seven.Will this really be the collapse of her world as she knew it?Like Six said, if that happens, I'll be here to hold the umbrella for her.Do you think Thirty-seven is going to make it?Who knows?
```

### [79] hash=`288cf4ea40093123`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Six should be the easiest one to pass.The math puzzles in the labyrinth shouldn't be a problem for our little star either.The only tricky question is from a paron, and no one knows what it will be.It is a fair game, answer a Peron's question and it will answer yours, but if you givethe wrong answer, oops, it'll hardly be a graceful end.You're gross.We know little about the test.The last person to pass the test was 300 years ago.
```

### [80] hash=`0f7787cb1151e3f6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
The price of failure was high.For the longest time, the Sixers forbade people from risking their lives for it.Well, Six lied.Someone passed the test four years ago.The two of them are so much alike.Their talents.Their mindsets.Even their first thoughts when facing an impossible challenge.It is an irresistible temptation indeed.With a path to all truths right in front of you.Just within reach.Who wouldn't want to give it a try?
```

### [81] hash=`b8901facceff6903`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
I'm not who you think I am, child.I am but a shadow, a flicker of fire, a projection before you.The finite cannot comprehend the infinite.Your limited senses cannot imagine what you've never seen, nor fathom what you've neverheard.I am the answer to your desperate prayers.I am the blindfold before you see daylight.I am the reflection of your confused, hollow faces in the water.I am the lingering echo of the last visitor
```

### [82] hash=`6e595c3916be1d1c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
But you look just like mama last obstacle of the test truth is just ahead right and here you areIn front of me they reach the transcendental realm my conjecture with the transcendental realmYou speak adorable nonsense my dear daughter.Did you really believe what I say?silly little gooseHave you not doubted?not matter, child.The rules of the game have changed.The Chaos Makers, the Fear Mongers andthe Rule Shapers, they have already outpaced us.
```

### [83] hash=`2a32223141148697`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
We were not wrong.We simply fell behind.We were blinded by the dream of the Transcendental Realm and could not see through reality.But worry not, my daughter.You have made it here and that is all that matters.We will do the calculations together.This time, the results will be more accurate than ever.Mama!This world is an enormous wasteland, 37.Look at the creations in it.The congested, silent herds that scurry to and fro in their meaningless lives.
```

### [84] hash=`3d5a160f0c45c753`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Never have they looked at the stars above, nor bent to smell the flowers.The melodies of the patterns above go unheard by them, their souls unresonant to their wisdom.They are the prisoners of their bodies, complacent in their dulled senses and conceited overtheir success of ruling the planet through violence and bloodshed.They mocked us, shunned us and slaughtered us.They discriminated against us throughout the ages, branded us as lunatics and spat
```

### [85] hash=`070805aec99c6a83`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
I will share with you the infinite secrets of this world the essence of all things and the truthThat transcends everythingThat's what you came forYes, but mama in 37 not infinityWhy would I want an infinite number of secrets?groundShaking did she give the wrong answer?I don't know infinite secretswhose supreme existences cannot even fathom!I am here for a full question!Is it cause the answer to my question?
```

### [86] hash=`4970990035fed979`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
The transcendental truth is outside of all limits too.Mikwe!Madam Lucy, we have the right pronunciation.The script you gave me was correct.This is the arcane language of the Incantation.Where did you get it?Very well.Give it to me.Inform all research teams that we are moving on to the next phase of the project.If you're here to check on the progress, there is none.I'm afraid you'll leave disappointed, Madame Lucie.
```

### [87] hash=`84c1b2140062d388`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Send this to everyone.It has been verified.This is the correct pronunciation of the immunity ritual.This is...La Unua.We must share this with everyone!La Unua Circlo.What was that?Stop the transmission!The ritual is wrong!No.The incantation is indeed correct.What is going on?Warning!Hey Dawkins!Forget the outside!Come look at this!Some guys cracked it!They've found the correct pronunciation!For real?
```

### [88] hash=`a7eb65abd3adaddf`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
They better be serious if this is some kind of prank.Le Una...Circle?Dammit!Ulrich!Dawkins!Victor!Richard!Are you in there?Listen!If you receive the pronunciation of the incantation, do not recite it!Do not write it down!Do not pass it on!I know we've had our differences, but you have to trust me!I'm trying to save you!Warning!All personnel stay away from their communication terminals.Do not recite any messages on the screen.
```

### [89] hash=`f7fe223d9628370a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Repeat.Do not recite the incantation.D-Richard!Don't speak.We're going to the Recap Center.No.You go to Dawkins.Dawkins?No, no, no!Researcher Adler, please evacuate immediately.We will take over from here.No!He taught the worst case would be that the ritual is useless since no one here can wield it.I was wrong.So terribly wrong.The reality is a million times worse.We have invited a disaster.It is a curse, even more unpredictable, unstable and uncontrollable than the mask.
```

### [90] hash=`8c2c2b07a45b87c4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Dora crumbled to dust.Richard cracked like dry land and Dawkins turned into a statue of mud.And Victor, he vanished.We've tried everything, but he's nowhere to be found, yet he's here, typing, sendingemails, getting the door for me.All of these catastrophic events, and only three words were uttered.Three.What are we dealing with, Madame Lucy?Which deity are we provoking and stealing from?Get some rest, Mr.
```

### [91] hash=`88b5c31b1974ee16`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Adler.Your mission is complete.Other researchers will take it from here.You what?Are you not going to call it off after all that's happened?The research must go on.The authenticity of the incantation and the fact that any Arcanus can recite it were revealedto us through this unexpected mishap.Now, a new question arises.How can we eliminate the side effects?From now on, we no longer require the help of human researchers.
```

### [92] hash=`8a93f127edf22292`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p59`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 6~10）

```text
Only Arcanum can lift a curse of Arcanum.Thirty-seven!I'll get you out!Is this Six's scroll?Positive one, negative one, positive two, negative three, three, negative three, positive two, negative one, positive one.I see.I understand now.What did you say?Thirty-seven, are you feeling better now?BuzzFurten, Six's scroll reconciled the gap between the supreme existence and me.I can now hear and understand.

The answer to my question, the solution to free us from the emanation,the response appear on promised me, is a string of numbers.
```

### [93] hash=`f481306036743ea2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Key to the gate of truth, Thornsed me.This is the final solution.We must leave here at once.We have to tell everyone.I am so proud of you, Thirty-Seven.We will save everyone.But there's one thing I don't understand.And that is?Six.His scroll saved your life.Maybe he foresaw the dangers and protected you from it, so you can leave there almost unharmed.But what was he trying to tell you when he warned you about the collapse of your world as you know it?
```

### [94] hash=`2c83735f26d809b4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Mind your step everyone.We are passing the wall of truthThe wall will come crashing down if false words are spokenSilence is advised here unless circumstances dictate otherwise888Forgive me, but this seems to be the right momentFor some long neglected questions to be answeredPerhaps, but hardly appropriate or righteous.We will talk of righteousness after you've shared what you know, Six.You've been silent for too long.
```

