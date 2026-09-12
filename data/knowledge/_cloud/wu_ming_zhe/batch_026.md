# 剧情图谱抽取 · batch 026

- 角色：`wu_ming_zhe`
- 批次：**26** / 共 1 批（每批 73 块）｜本批块数：**73**
- 筛选：标题含「1.9」｜offset 570
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_026.jsonl`

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

### [0] hash=`a358f480fdd2bc1a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
I could use a little cleaning, polishing, and perhaps a coat of wax, if I can find someoneto do it.In that case, why don't we enjoy a little pampering time together?We could slather ourselves in machine oil, bask in the sun, and let the rays zap ourimpurities away.Did you find something, Ms.Furtin?Certainly.Which DJ do you have in mind, or are we looking for updates on a particularpolitician?In that case, why don't we enjoy a little pep we could slather ourselves in?

Overflowing.Cold.Just like a flowing wine.Wait, where am I?
```

### [1] hash=`bb5f81593631409b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Ms.Ferdin, did you just say the emanation has happened?Just now?More precisely, its 24 hour countdown has begun.There's always a buffer period before the storm,during which the storm syndrome gradually spreads from the critical point across the globe.The symptoms are different every time, and we have yet to discern a pattern.With the help of Laplace Scientific Computing Center,The best we can do now is to send a 24-hour warning prior to the storm.
```

### [2] hash=`54b5be1c350c28dc`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Another minute has passed.Please remain seated, everyone.We are still in the middle of a vote.The emanation holds no influence on this island.The discussion must continue until a satisfactory conclusion is reached.No other subjects shall be brought up until then.Come here, 37.Can someone please bring her a blanket?into the ditches like gunk, and we will regain our shores and return to the study of essence
```

### [3] hash=`5ba1be81024426c5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
and forms.The world has fallen ill.It's getting bloated, stagnant, and sluggish, drifting into the world of matters whereignorance reigns.Soon, the tides of Numa will wash over us, sweeping away the fragments of thephenomenal world.What did you say?In other words, we will all be taken by the emanation?This?This is unthinkable!Thirty-seven, you just woke up from a coma.You're not well.Why don't you take another rest?
```

### [4] hash=`7bf9d755e84c6cd9`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Time for that.I'm here to warn you.A Pyrron is gone.I can no longer sense it.This has never happened before!Why are you so surprised, Thirty-seven?You should know the reason of its alienation.You brought outsiders to the sacred place.You betrayed the scriptures teachingsand angered a Puron.Of course I may have jumped to this accusation as ManusVendicta also intruded our sacred place without permission.
```

### [5] hash=`95417ce70baea414`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
People, as of nowthere's no proof that the emanation will influence the island.37'sand the damage is done to our home.We are to proceed with the hearingand reach a final verdicton both the Foundation and Manus Vindicti.I'm sorry, please forgive me.I shouldn't have intruded the Hall of Truth, but...Sophia, weren't you and Forty-Twochecking on the Abraxas's?What is the matter?The Abraxas's don't look right.
```

### [6] hash=`82fef0e9112f4364`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Their beaks, no, their entire headsare melting into oil paints.and 42 we were on the beach suddenly he now I see it finally all makes sensethere never was the truth nor the transcendental everything is a lienothing but shadows on walls flickers of fire and fragments of reality no onewill survive the oblivion the island will be destroyed amid its conflict thedoesn't mean it doesn't exist must we talk of logic now 42 has literally been emanated
```

### [7] hash=`061f3170a619e748`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
first the army then the emanation everything's been falling apart since the outsiders arrivedon this island the foundation and man is vindictive one of them must answer for thisthen you should also ask 37 and number zero what they've done in the sacred place to angerthe work of your arcane skills.As we went through your belongings, Miss Vertin,we found a golden sampling device.Enlighten us.What exactly is the
```

### [8] hash=`618ac98fa29a3f58`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
foundation looking for here?Nuts.Good, Vertin, good.Let the confrontations belouder and the struggles be harder.I wonder what shall come of this.Silence!The debate will end now.Since we were unable to come to an agreement,further discussion is pointless.There are more pressing matters to attend to.This will be the end of the assembly, and my decision will be the final ruling.I demand that both parties leave this island at once.
```

### [9] hash=`4a0883e15d1778d1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
I respectfully accept your verdict.Certainly.It was a fair and just decision.If only one could depart amidst such unfavorableweather.I presume Miss Vertin will also appreciate more time to prepare for the journey.What sayest thou?The hourglass empties in two hours.Please leave before that.Thank you for your thoughtful consideration.Lastly, I would like to share a story.To conclude today's meeting and respond to Miss Arcana's tale.
```

### [10] hash=`17516b6f6c0d964d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Most honored.I too have heard the story of the First Circle, but in my version, more followed.The First of Man were intimidated by the enormity of nature and constantly tried todefy and escape it.Our ancestors, however, had the opposite reaction.They found solace in nature, which welcomed them with a nourishing embrace, sharing itsvastness and sublimity without reservation.It was the perfect harmony, the moment the circles ceased to represent confrontation
```

### [11] hash=`880e76d5ea267623`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
and avoidance.As we bathed in Apollo's illumination and wandered the tranquil shores, our soulsresonated and we were lifted to a higher wisdom.This was how we conquered our fears, emerged from ignorance, and allowed ourselves to indulge on the essence and forms.This was the rise of the Classic Man.May you all be blessed with the courage for reconciliation, the determination for peace, and the devotion to nature.
```

### [12] hash=`ab16d76937c240cd`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Qualities no less noble than caution and defiance.You may all leave now.XR circle!888 was right.I have enraged a Peron.I am responsible.Back to the sacred place,pass its test,and ask it to share the divine light of Gnosisso we can learn the truthabout the essence.I will make up for what I've done.I promise.It has been 300 yearssince the last challenger had their successin the cave.37.Are you aware that we have other means to cleanse the island, even if you don't bring the matter to a payroll?
```

### [13] hash=`8b462033ec9df355`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p3`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（03.石钟之下.1/12 21:00）

```text
Yes.Then are you aware of the price you will pay should you fail its test?Then you shall have my blessing.
```

### [14] hash=`e6dc39a29f6f757a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p4`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（04.证明的开端.1/12 23:00）

```text
headquarters has issued a notice.The critical point of the storm is in Vienna.This type ofstorm syndrome involves a bodily transformation into oil paintings, primarily affecting the face,but sometimes spreading to the torso.It is often accompanied by delirium and an intenseobsession with war.Like the storm of 1929, it was accelerated by social upheavals resultingfrom the constant tensions Manus Mindigte created between nations.
```

### [15] hash=`6cdf515f280b9451`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p4`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（04.证明的开端.1/12 23:00）

```text
This era......is absurd.We went through all that trouble,sweated our guts out,and finally got to a place where the storm can be kept out,but now you're telling me that immunity is going to disappear like a fart in the wind?I was planning to stay here for a while.There might be alchemic materials and pieces of books the Abraxasists left behind from their mills.That is frustrating, mate!Such is the nature of Arcanum.
```

### [16] hash=`43d1aff6dff9dd0b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p4`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（04.证明的开端.1/12 23:00）

```text
The immunity hasn't disappeared.It's just waning.For now, only the beach has lost the effect.We're still safe around the Hall of Appurin.But there's no guarantee that we'll be safe here forever, right?Huh.Reminds me of Zeno's survival test.Senetta and I talked about this.We think the island is protected by a large-scale arcane ritual.To the best of this apple's knowledge, secluded pure-blood arcanist groups often have rituals that they keep to themselves.
```

### [17] hash=`dd8e05a888e3df39`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p4`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（04.证明的开端.1/12 23:00）

```text
These islanders impart truths based on intellect and rationality, yet their doctrines are highly religious.Perhaps their arcane skills are passed down in a religious manner.Oh, very mysterious, very arcane.I hope they're not all huddled together doing a mass at a time like this.Huh, I see.So we only have two hours for the plan.Plan?We're sneaking away from all this!Sorry, Regulus.Your...accommodation was a long way from ours.
```

### [18] hash=`f27fb5399ecfaa07`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p4`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（04.证明的开端.1/12 23:00）

```text
So we haven't given you the latest updates.To put it simply, 37, we...We're discussing how to leave this place, 37.Precisely.I was just about to say, your chief wants us gone in a jiffy.But you'll have to wait till Vertin and I return.Me?Where are we going?Kind of question is that.The only place worth going.You're the one and only Zero.We'll go see a pair on together.Aren't you going to look for 37?

You took such good care of her while she was in a coma.I...don't know.I don't know what I should do, Madame Mata.
```

### [19] hash=`64b6fd0b6c86aa74`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Damn you narcissistic, fat-headed, humanocentrist freaks!You are the crazy ones, and I will prove myself right!Seriously!Can someone please bring Matthew back to the rehab center?That mask has made him crazy!Any progress?Not much.We've called all the experts here, but so far it's been a waste of time.Not even a bodily reaction when reciting the text.He doesn't belong to any known language, nor follow any linguistic rules.
```

### [20] hash=`859f916aa6f93dda`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Many are starting to doubt the accuracy of the incantation.After all, it wascopied down by a novice investigator with her arcane skill, not her supervisor.Ms.Marcus, can you confirm that the incantation you dictated was correct?Wealso learned that you witnessed a visual recording of Arcana performingher arcane skill depicted through images recreated by a pure-bloodedReed, was performed correctly and provided an unbiased, objective, and flawless interpretation?
```

### [21] hash=`86489d72d18571f3`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Eyes, hear the detenting.Down phonetically.Please calm down.We are only verifying the details.The Foundation has dispatched a special operation squad to you in Vienna.Please make sure the two other Arcanists involved will return to the Foundation with you.This?Is this it?An ancient miracle?A circle of salvation?A tuna psycho?An inexplicableincantation transcribed by an Arcanist based on what she saw in the memory of another
```

### [22] hash=`02889a594cce7bc7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Arcanist recreated by yet another Arcanist?That's as convoluted as a dream within awithin a dream to think they wanted an objective restoration.I mean, if Gnosis is so reliableand can really cross-check not only once, but four times, it should have long replaced scienceby now.With this level of uncertainty, we might have better luck asking typewriter monkeysto randomly give us the answer to the storm immunity.
```

### [23] hash=`b27706876b7feb3d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Adler?Why are you here?I requested his participation on the cryptography team.He is a human, but he excels in the field of cryptography.But, and why can't I be here?Is it because Greta Hoffman's my sister?And this, is this what a respectable and honorable member of the Foundation gaveher life to retrieve?Is this the ritual she died for?Oh right, it wasn't even her who retrieved the ritual.It was a student.
```

### [24] hash=`b0945e71044dbcb1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
You are not currently on the official roster.You can leave at any time.Leave?Why should I leave?Return to your stations, please.Let us not dismiss its credibility until we have exhausted every possibility.Also, add Adler Hoffman into the cryptography team roster.Storm Observation and Research Center.Noted.I will make sure Ms.Lucy is aware of that.What is the matter?It's a call from the rehab center about the previous study on the Manus mask.
```

### [25] hash=`d6f92221dae43dfe`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Ma'am, I think you should go see this in person.Very good, Matthew.Now tell us.What did you hear?Voices!Those voices!The inaudible murmurs, the frightening whispers, they worm into my ears!I told you before!I wrote about this before!But you dismissed them as manic episodes!Did you put on the mask?How else would I know that I was right?And now I know!I never ever heard them so clearly, they are screaming inside my head!
```

### [26] hash=`7a13eb0b279fa0ca`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p5`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（05.四次方程.1/12 23:10）

```text
Their temptations!Their promises!I just have to let go of my brain!Can you hear it?The benevolent mother is speaking!How?I can write the ultimate paper!Who is this mother?I can't say anymore!They've seen him!They've come for me!Suspend all research on the madness mask at once.Its dangers far outweigh the potential benefits.Seal away all equipment and share only a controlled account of the incident with others.

We cannot afford to have another researcher try on the mask again.Now, clean this up.Yes ma'am.Another dead end.Barrage.Faraday's miracle.
```

### [27] hash=`cf79764bf12225f0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
What is the status of the sampling, Simone?Any updates from the timekeeper?For the moment, no.The people on the island are still suspicious of the Foundation's motives, so she hasn't had a second chance to collect any samples.But she has called in an hour ago.We were informed that she will return to the cave shortly.She also warned us that the immunity zone on the island appears to be shrinking.The safe zone is not stable.
```

### [28] hash=`462eef583dececc4`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
Hmm...Have you noticed something?They are unrelated, Simone.The mask and the incantation are indeed related toManus Vindicte, but they are unrelated to each other.If the account of the Viennainvestigator is correct, one cannot help but question, why would Arcana notsimply give the masks to his old and her brother?Investigator Marx'sreport was highly lacking, making it challenging for us to infer what truly
```

### [29] hash=`81cba58b5c8487d6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
happened.I suppose we can be skeptical that the report is incomplete, but itIt is all we have for now.She did a good job, I could not have asked for more.We all heard it, an ancient miracle, a circle of salvation.The leader of Manus Vindicte promised a miracle, but the mask is far from it.The mask is a tool of control, designed to identify and enslave the believers.Matthew has demonstrated its effects for us, but this ritual is different.
```

### [30] hash=`7950847682c503e2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
Do you mean the ritual is more sophisticated than the mask?Perhaps, but it is not entirely definitive.The investigators in Vienna completed their mission spectacularly,and now Matthew has proven that the mask is useless for our purposes.Its immunity was only a cover for its other functions.And the mask has powerful and irreversible side effects.Even if we find out how it protects the wearer from the storm,
```

### [31] hash=`b0632a8b0883b0b9`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
We cannot use it on our colleagues.If this incantation is verified to be true,it will be our Promethean fire.This ritual is useless to us.Save yourself as Hubble.We're not getting anywhere with this.What?Explain yourself, Adler.What do you mean the ritual is useless?You barely sat down.My coffee's still hot.I don't need to waste any more time.It's simple logic.The current information is insufficient for cryptographic decryption.
```

### [32] hash=`7943f905b81a03ba`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
We're attempting an exhaustive brute force comparing every ancient text and recordto find the language or corresponding text.It's like looking for a needle in a colossal haystack.Even if we stumble onto a match, none of us can validate such a thing.A breakthrough in this regard is simply not possible.You can't be serious.And what is the basis of your reasoning?Have you figured out the mechanics behind the ritual?
```

### [33] hash=`5bd6948d52b844ca`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
I didn't need to understand the intricacies of Arcanum to deduce this.It was simple lo-So you never even tried to understand it.With your supposedly superior human reasoning,you dismissed all of our dedication and hard work just like that.Who the f- do you think you are?Matthew was right!You arrogant, clueless morons!Get out of my face, you humanocentric narcissist!Go to hell!was this really necessary I was just sharing my conclusion he worked in the
```

### [34] hash=`c4fe80b797038831`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
same lab as Matthew and he must have been exposed to the mask but hisphysical exam seemed fine is there an incubation period does he seem fine toyou now huh Williams put that down that's the onlyConway automaton 5 left after the storm security security we've got ared aim and shoot the light that illuminates all so what are the implications for the decryptionthere were no unintended consequences we were able to control williams in time and the conway
```

### [35] hash=`b4d51c9c7cd5372b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
automaton 5 he destroyed wasn't useful to our work anyway i am glad you kept the damages toa minimum since you are still here mr ulrich i take it as a sign that you have more to reportWilliams was merely an accident, Pam, but Adler is a loose cannon on the team.We need to talk about this.With all due respect, I still don't understand why you put him on theteam.He may have made his contributions to Laplace, but that was eight years ago.
```

### [36] hash=`da164551450440fd`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
Now he's just an irritating defeatist and a staunch supporter of humanocentrism.He never understood the Arcanum, or tried.He's still stuck in the time before the firstHis human perspective will offer valuable insights on arcane rituals.The results of this study will not only be used to save Arcanus,but also humans who share the same world with us.We are racing against the clock, Mister,and your report on personal disputes and racial conflicts has wasted 2 minutes and 37 seconds of our time.
```

### [37] hash=`a4f8c96d59efa33e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
If he refuses to cooperate, you have every right to remove him from the team.That is your responsibility.Oh, I'm relieved that you survived your altercation.What would you like to report?I'm fed up with wasting time, ma'am.The setback with the mask has already driven too many people insane.That's why you should take a look at this.I can logically deduce that our current direction is another dead end.
```

### [38] hash=`7bc9a3a824767a0b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
The incantation isn't long enough for cryptographic decryption.We will have to turn to ancient records.Perhaps, we'll find something in age-old manuscripts, in tablet inscriptions, or in the memoriesof powerful Arcanists.But even if we find it, we can't validate it because none of us can cast a skill.Low-ranking Arcanists can't cast high-ranking skills, even if they know the exact pronunciationand meaning of the Incantation.
```

### [39] hash=`72b3668da35d01b1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
Gnosis is beyond reason like that and cannot be debated.It stems from raw intuition rather than logic and intellect, is shaped by personal experienceand natural abilities, and cannot be intentionally replicated.And the most determining factor, it relies on the Arcanist's purity of blood.The miracle ritual you hold such hopes for belongs to the leader of Manus Vendictae,a pure-blooded Arcanist whose power is beyond our imagination.
```

### [40] hash=`550a8e74ff0eefc1`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
It's like asking a toddler to solve Goldbach's conjecture.It's completely beyond the boundaries of our limits."But you are not an Arcanist.Why should you play by their rules?You are right.Arcanists differ due to the purity of blood.Researcher Medicine Pocket has already reported the linear correlation between the bloodlineof an Arcanist and their abilities, and has drawn a conclusion ten times more extreme.
```

### [41] hash=`cebfa9690ee456be`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
Then you should listen.That's their area of expertise.We know that our cryptographers do not have the power to validate the ritual, and we donot expect you to do that.All I ask of you is to come up with a feasible plan and todo it as a team.Your deduction is logical, but not practical or actionable.So I shouldreturn this to you.What?Your logic is impressive Adler, but do not let it limit your thinking.
```

### [42] hash=`be40f47d4d57eb37`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
You spokethe boundaries of arcane power.But logic has its limits too, no?Knowledge can be obtained throughvarious means, such as intuition, logical reasoning, empirical observations, and teachings from others.Your team is not the only one cracking the ritual through their own means.If you fail, we will turn to the others.And if that approach is wrong, we will try another.If no solution is found before the storm, we will simply wait for the next one.
```

### [43] hash=`7504cab9ac15941a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
What matters is we keep moving forward, no matter the cost.We must keep to the path, or we will be swept away like dust in the rain.If one team fails, you can still turn to the others.What?Forget it.Just a bitter rational thought.This marks the end of my efforts.Hopefully, the others will bring you the needed breakthroughs.You've been waiting here for a while.Are you expecting someone?You aren't the type to waste time listening to us whine.
```

### [44] hash=`b7b013bcffae5382`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
So there must be something here worthy of your attention.Is someone close to a breakthrough?Nothing of the sort.I am recharging.We have a public power outlet here, but I am indeed waiting.The doves of the White Stone House are here.Good.Someone closer to the limit has given us aid.Be ever so careful, dear.The fiery thirst for knowledge is blazing bright within you.Be careful not to put it out.Once, many fire thieves sat here, sipping coffee, as they tried to decipher the best angle to hold up their reeds to jam the burning wheel of Helios and steal his flame.
```

### [45] hash=`df4c38437f230b77`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
The gods are selfish.They're stingy with their might.That's easy to say when the power is not yours to give.Knowing how to share is a rare virtue.Knowing how to share knowledge is a rarer virtue still.How can we transfer our wisdom into mortal minds?The gods pondered.Can inspiration be duplicated from one brain to another?It comes and goes like a gust of wind.So what can be done?Not yet, darling.years of evolution.
```

### [46] hash=`4860c6d2805571f5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p6`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（06.傲慢与偏见.1/12 23:33）

```text
Once again, they became the proteges of Arcanum.Perhaps they made the rightchoice by leaving that useless science behind.Who knows?The story of the Fire Thieves has onlygone this far, though.At this point, no one knows what will happen to Prometheus, or what'sinside Pandora's box.
```

### [47] hash=`b47e53f559bc84eb`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
Any news from Zeno?They are moving as planned.The deployment will be complete within two hours.What about Arcana?As if she's a part of a force in the wind.She found herself a good spot, overlooking all of us from up there.The center of the island where the number of people are heading.The entrance to the cave where Vertin and 37 are going.And the beaches in the storm.Nothing escapes her sight.Oh, impressive!
```

### [48] hash=`457d71893d605f60`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
The margin of error should be below 0.00025%.I'm confident that it will work.I know, I know.Spare me with the numbers.I know I can rely on you.Still worried about Vertin.Will she make it back in two hours?If she doesn't come back in time,who's going to take charge and guide us?We'll have to steer our own course, won't we?Yes.Laplace is gathering every piece of informationthey can find on the storm.
```

### [49] hash=`8be8294a4dc5e783`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
The discovery of the asymmetrical nuclide R was already a remarkable breakthrough.It would help the immunity research a lot if the timekeeper could find something useful in that cave.I don't think she's going to have a lovely time there, judging by what happened to me last time.Is it just me, or do you also find this a bit fishy?The dangers aside, using an answer as a reward?What?Is this deity some sort of answering machine?
```

### [50] hash=`66db72f2fa03d741`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
In fact, a Pyrron is a philosophical concept introduced by the ancient Greek philosopherAnaximander, which means the origin of everything.It is the physical manifestation of the boundless,the indeterminate and the infinite.Everything arises from it and returns to it.But itto serve a more practical purpose for the believers on this island.Ms.Marta told me about this.There are limits to the knowledge one can acquire
```

### [51] hash=`bf24bec8e6475f80`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
even when using numbers, which are considered closest to the essence,but appear on as a boundless limitless existence.If we wish to seek knowledgebeyond our own limitations, we must turn to it for help.To the best of this apple's recollection, the more ancient,Abstract and intangible an entity is, the more likely it possesses arcane powers beyond our fathom.By communing with the supreme existences through sympathetic magic,
```

### [52] hash=`5e4a7f08e7d1fdfb`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
worshippers could gain the guidance of their transcendental gnosis.They would, of course, exact a price from the worshippers as well.Could you be more specific on that, Mr.Apple?What's the price?Lives or something else?Good!Now you are on number one and you should jump to seven.This is a four by four magic squareYou just need to make sure every four steps you take adds up to 34I don't understand 37.
```

### [53] hash=`7b1bdd1d0ed78842`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
This place was different the last time we were hereIt has changed because the test has begunThe path to new knowledge is always harder than verifying a known resultDon't worry.This is like a labyrinth with a minotaurThirty-three!I could be given that!But what does it mean to us?Like I said, it's not that big of a deal.I thought the next question would be the Ford Circle, the Monster Group, or Hilbert's Infinite Grand Hotel.
```

### [54] hash=`c921b06f1b78dc85`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
Thought it would be Six.Hello, Six.Are you the real thing?Yes.I'm the real Six.Be so sure.When it comes to the essence, we are all shadows cast on a wall by a flickering fire.How do you know you're the real Six?Did you just smile?Now I very much doubt that you're real.I didn't.And I am the true Six.This gate has always been guarded by a Six.I have a bad feeling about this.I think the question we're about to answer will be very simple.
```

### [55] hash=`6c66f578081a95f8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p7`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（07.米诺陶迷宫.1/12 23:33）

```text
It's just a formality, isn't it?You'll ask a question and let us through.I've seen you do that on other tests before.Formality is also important.The essence is important.Only the forms are important.This is a question about the essence and forms, 37.Please pay heed to it.As for Miss Vertin, we only expect you to lend a patient here.Very well.Thirty-seven.If your pursuit of truth were to lead to the destruction of your faith and beliefs, would you still keep going?

What kind of question is that?
```

### [56] hash=`93a05a45128e1c44`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
If my pursuit of truth will be the destruction of my beliefs,I came for the truth, and my faith is the truth.Why would the truth be destroyed by the truth?If it's because I did the calculation wrong,I'll go back and do it again.And next time, I will do better.What if the essence of truth is there is no truth?Isn't that also a form of the truth?Its non-existence is an answer in itself, is it not?You're speaking like 210.
```

### [57] hash=`eb1e9683424a9f6d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
Are you really six?I should be more specific.You may see it as another allegory.A gate stands before you.Open it, and you will find the truth you seek.But at the same time, the world as you know it will crumble.Will you still open it?Yes.If my world changes because the truth is revealed, doesn't that mean my previousunderstanding was wrong and should be corrected?If what's behind the gate is really the
```

### [58] hash=`0664b74d9a195eff`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
truth, why would I give up the truth for falsehood?I see.You've passed.As a reward, I will bestow upon you this sacred ritual.Itwill bridge the gap between you and the supreme existence during communion.Was that it?You didn't even ask a question that posed a real challenge.See, Furtin?I knew this was just a formality.Furtin?No, 37.I think this question...37, there are some words I'd like to share with you.
```

### [59] hash=`a8dcae93f3d077a4`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
Not as six, but myself, who used to live under the name Atticus.We know the story of Socrates' life, how truth and politics are at odds with each other.Either be wise, uninvolved, and look on, or be practical, involved, and suffer.I hope you will remember your answer when the defining moment comes for you.We should go, Vertin.There's a long way ahead.I hope the next question will be more fun.Good number!
```

### [60] hash=`13fd0287b4de5a01`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
It's the 8th Twin Prime, the 8th Mucky Prime, and the same combination as 37!But sadly, you're the 21st Prime number, which makes you less than perfect.Fertin, let's start with...With 73, because it has the largest absolute value.Nice choice, Fertin!You are a quick learner!There they are!I haven't expected so far just like what mom told me they're just games likeskipping rocks catabos and hopscotch I've always been good at games there's the
```

### [61] hash=`3a82cf3d35775ff9`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
gate Fertin we're almost at the end what's the matter Fertin you've beenquiet since we met six but your number zero not six you have no common factorNone of the precepts forbids one from doing so.People like her may fall behind or get distracted along the way,learning at a slower pace.But in the end, we will all converge.It doesn't matter if some arrive sooner than others.So, are you going to ask something else?
```

### [62] hash=`c6d2717f4adeffc8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
Yes, I have come up with a better question.A question that will solve all our problems once and for all.If you encounter any danger in there, I will come to your aid at once.But don't you also have a question to ask Aperon?Aren't your doubts unresolved?No, I don't need to ask anymore.The question you're going to ask, the one that will free us all from the emanation,is exactly the question I want to ask, 37.
```

### [63] hash=`b7c9ad91446e90d8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p8`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（08.德尔斐神谕.1/12 23:49）

```text
I see, so you're choosing to be the one who looks on, like the third kind of men in the Olympic Games.A choice of insight, most appropriate for the number zero.In that case, I will see you later then, Verten.See you soon, 37.Will this really be the collapse of her world as she knew it?Like Six said, if that happens, I'll be here to hold the umbrella for her.
```

### [64] hash=`b1fbf81c5c8737f8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
Do you think 37 is going to make it?Who knows?Six should be the easiest one to pass.The math puzzles in the labyrinth shouldn't be a problem for our little star either.The only tricky question is from Aperon, and no one knows what it will be.It is a fair game.Answer Aperon's question and it will answer yours.But if you give the wrong answer, oops, it'll hardly be a graceful end.You are gross.We know little about the test.
```

### [65] hash=`4f66bf145b1bb425`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
The last person to pass the test was three hundred years ago.The price of failure was high.For the longest time, the Sixers forbade people from riskingtheir lives for it.Well, Six lied.Someone passed the test four years ago.The two of them are so much alike.Their talents, their mindsets, even their first thoughts when facing an impossible challenge.It is an irresistible temptation, indeed, with a path to all truths right in front of you, just within reach.
```

### [66] hash=`1bfc622cade67a95`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
Who wouldn't want to give it a try?I'm not who you think I am, child.I'm but a shadow, a flicker of fire, a projection before you.The finite cannot comprehend the infinite.Your limited senses cannot imagine what you've never seen, nor fathom what you've never heard.I am the answer to your desperate prayers.I am the blindfold before you see daylight.I am the reflection of your confused, hollow faces in the water.
```

### [67] hash=`2421b255c518eaca`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
I am the lingering echo of the last visitor.But you look just like Mama.The truth is just ahead, right?And here you are.See in front of me that you finally reach the Transcendental Realm?The Transcendental Realm?Speak adorable nonsense, my dear daughter.Did you really believe what I said?You silly little goose!Have you not doubted, even for a moment?You did.You wavered when you strolled the shores at night,
```

### [68] hash=`876d26f6fdd5b365`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
when you inevitably gazed at the geometric bodies.If they really are manifestations of the Transcendental World,Why can't I find Mama's number in the broken pieces?You thought.Why can't I hear her voice?Why can't I see their patterns?The darkness blinds me.I miss you, Mama.My poor, sweet daughter.You are too young and naive.Too attached to what is familiar and too trusting of your teachings.The congested, silent herds that scurry to and fro in their meaningless lives.
```

### [69] hash=`9df2e648fca31009`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
Never have they looked at the stars above, nor bent to smell the flowers.The melodies of the patterns above go unheard by them, their souls unresonant to theirwisdom.They are the prisoners of their bodies, complacent in their dulled senses and conceitedover their success of ruling the planet through violence and bloodshed.They mocked us, shunned us, and slaughtered us.They discriminated against us throughout the ages,
```

### [70] hash=`2f460d7ccad0347f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
branded us as lunatics, and spat on what we held dear.But we never gave up once.We were never truly defeated.One day,they will be proven wrong, and they will be forced to admit it.But mama, I'm 37, not infinity.Why would I want an infinite number of secrets?The ground is shaking.Did she give the wrong answer?I don't long for the infinite secrets, for it is not within the scope of my number.I know who I am.
```

### [71] hash=`e87571e236729db7`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
I am only 37, a finite number, a pebble in the sand.The tides could wash over me, engulf me, and crush me at any moment.Even so, I am glad to be 37, for I know my limits, I know my boundaries.A concept whose supreme existences cannot even fathom.Question, and be free!Is it be answer to my question?The Transcendental Truth is outside of all limits, too.Make way!Madam Lucy, we have the right pronunciation.
```

### [72] hash=`f612ab79b8e687fb`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p9`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（09.不可超越之物.1/13 00:10）

```text
The script you gave me was correct.This is the arcane language of the Incantation.Where did you get it?Very well.Give it to me.Inform all research teams that we are moving on to the next phase of the project.If you're here to check on the progress, there is none.I'm afraid you'll leave disappointed, Madam Lucy.Send this to everyone.It has been verified this is the correctpronunciation of the immunity ritual.

This is La Unua.We must share this witheveryone.La Unua Circlo.What was that?Stop the transmission!The ritual iswrong!No.The incantation is indeed correct.
```

