# 剧情图谱抽取 · batch 033

- 角色：`wu_ming_zhe`
- 批次：**33** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.4」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_033.jsonl`

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

### [0] hash=`13a97ffa06363094`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p13`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（13.轴心的点｜1/3 21:00）

```text
Being exposed in full view of the crowd, yet you know nothing about it.37 was acting on impulse.Yet she opened Pandora's box.She leisurely reveals your fate.That carefree behaviour makes no difference to picking up a shell on a beach.How could I not pity you?Ms.Vertin, 37's proof has passed the review.Your friend will now be exempt from the punishment for violating the rules.However, she has to take some catch-up lessons on the scripture.

Please, meet me at the hall tomorrow at noon.I would have words with you.
```

### [1] hash=`8433b78065fbf578`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
Before this negotiation begins, I wish to tell an allegory to the two of you.A group of people were imprisoned in a cave.Behind them, there was a fire.Before them, was a tall solid wall.Their legs and necks were chained and fixed, so they were constrained to look nowherebut to gaze at the wall in front of them.When they dropped their eyes, they saw their own body.When they looked up, the flickering light of the fire fell over them, and they only
```

### [2] hash=`7583639a26854c2e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
saw the shadows of what was passing behind them.No one had lived one day outside the cave.The shadows cast on the wall, all there was to be perceived as reality.They had no knowledge of the real world.One day, one of them escaped from the cave, walked into the light, and saw thetrue world with his own eyes for the first time.Everything he saw or felt in the cave was nothing more than a mere shadow of
```

### [3] hash=`165f58c3131b1487`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
the object's true form.Our world is a poor one, Miss Verton.The phenomenal worldis the cave in this allegory, where we are surrounded by shadows or some humblefractions of the truth.It is ugly, frivolous, filthy, perishable, subject todecay, and filled with hollow desires and meaningless struggles.Only the wise can walk out of that cave and see the world as it truly is.In that eternal, transcendent world, everything is in its most perfect form.
```

### [4] hash=`62edbdfa9b525f52`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
I pray that you, Miss Vertin, the representative of Saint Pavlov Foundation, and you, MissHarkana, her counterpart of Manus Vindictae, would pay heed to my words.Everything you've been fighting each other for means no more than some fragments of phenomena to us.There's only one thing worth doing.That is, to seek higher wisdom, develop one's virtue, and achieve greatness in life.We have never set foot on the soil dampened by the storm,
```

### [5] hash=`6330590507a54c58`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
nor have we ever been involved in the disputes brought by the torrents of time.I beg you, do not take your conflict in the Phenomenal World into the Realm of Truth.For certain.It was never my intention to sully the Sanctuary of Truth.Then, to prevent a situation like this from happening again,I would like to ask you two to carve your names on these two stone banglesand drip a drop of your blood on each of them.
```

### [6] hash=`2715307554db8a8c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
Once the bracelet is put on, no one will be able to remove it.From now on, as long as you're on this island, none of your people will draw blood from one another.Or the bangle shall draw all the blood from you.The peace agreement is so decided.I appreciate that.I'll sign it.Peace agreement.Lady Vertin, we meet again.I wish the best to thy friend.I hope thee findeth the answer satisfactory.It's burning.
```

### [7] hash=`af8533bea814d82c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
Is that Miss Arcana?Miss Arcana, please!Don't go!Save us!You always show up at the right time and right place.Whatever it ta-Not you.Climbing out of the cave in the allegory, all dusty and dirty like a little savage.They must have tried to fill your little brain with long preachment.That which is real is reasonable.They showed you a broad avenue in their teachings where you could enjoy a sense of security
```

### [8] hash=`6ad7059d1aea6c71`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
with all the solid ground, convenient automobiles, and warm sunshine.And at the end of the avenue even lies an inspiring missionto which you are expected to devote your whole life.There is a distinction between good and bad here,and it's as clear as our innate sense of right and wrong,like a floor of black and white tiles.Any stains on it will be noticed immediately, but in fact, there exists another path in the woods.
```

### [9] hash=`a0b8a7c98de70c83`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
It's much less traveled, leading to the unknown darkness which cannot be seen with eyes or proved false.You may even experience indescribable chaos and madness there.This path, however, has an excellent view and it's one of a kind.They never turned back, never picked up what was not theirs, never set foot on the ForbiddenLands and never looked straight at the Sacred Greatness.They showed frugality, patience, and wisdom in the face of hunger and danger.
```

### [10] hash=`7769a49763be2895`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
So the beasts continued to lurk in the shadow, and the ones with the belief passedthrough the woods safely until the path disappeared along with the direction sign.How can anyone, how can you, ignore your love for those thriving plants and blooming flowers?How are you supposed to deal with the unstoppable feeling that overflows like a melody when it is stirred up by the beauty of the scenery?Of course, you will cry the loudest cry, dance the wildest dance, drink the strongest drink, and vomit all the filth inside you.
```

### [11] hash=`6aff012f3b1a9a16`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p14`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（14.和平的枷锁｜1/4 12:00）

```text
Is that what you want?Don't worry.We have plenty of time.You may come back at any time and pick another way.
```

### [12] hash=`9e803080c9bae1c0`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
Congratulations, Miss Sinetto.You are the fastest learner of our doctrine among all the visitors in the past half century.On behalf of all our writers, I award you this laurel wreath.No, no.I wouldn't have achieved this without your guidance.Those mathematic statements are really inspiring.I've learned a lot.But there's still something confusing me, such as Pythagoras in his golden thigh,His memory of the previous lifetimes as the son of Hermes and the transmigration for every 216 years
```

### [13] hash=`8523466caa6c53db`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
Could you please tell me more about these?Why would people fail to see the charm of the matrices?This is not right.I need to spend more time on teachingAnyone anyone say what?Thus my journey of art is doomed to fail.Yeah, I really don't want to study maths anymoreI've signed a peace agreement with O'Karna, and the price of breaking it is...What?So Manus Vendictae is also restrained by the Stone Bangle like we are?
```

### [14] hash=`7b3750e47ceeedca`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
Yes.She put it on without hesitation, but I don't think her purpose would be as simple ashearkening the ancient wisdom.I attacked Manus' followers earlier as Thirty-Seven asked me to, but I received no punishmentfrom the Bangle.Perhaps this island makes its own judgement on what to be classified as hostility, likeit has a mind of its own.Senato, do not report this to the headquarters before we figure out how the bangle works.
```

### [15] hash=`749ff14d6e4229a4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
After all, there are many other things to investigate on this island other than theManas Findicte.I see.I will contact Ms.Juvis and Ms.Muzzle first and keep an eye on Arcana.Not a bad innovation for a simple clap on the forehead.If only you didn't miscalculate the location of the explosion.This apple is grateful that it didn't get blasted into a puddle of apple jam.Warning!Shell cleaning required.
```

### [16] hash=`aff20fdcdcfe3a4b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
Warning!I don't know why, but when I was in that cave, ideas kept flooding into my head.Though, judging by the outcome, they weren't all good ideas.you study with the rest of the students here, abstain from eating meat, bathe in cold water,rise with the Apollo Star, study our doctrine, read the scripture aloud on the beach, soas to remove your floating points and purify your soul.What?I won't do any of that.
```

### [17] hash=`6f1fcafe7765a579`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
But taking your peculiar character into consideration, I decided that some compulsorylabour would be the better option.A great pirate would not remember trivial matters as such.So, where were we?Which part of the beach needs to be taken care of by the great captain?My laboratory.Whoa!Where did you pop up from?37.Aren't you supposed to preach to the visitors?I've seen their numbers.A group of negative repeating infinite decimals.
```

### [18] hash=`7b21bc8ad694590f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
They will achieve nothing but to repeatedly step in the river of mistakes.I gave up on them.Fine.Those of you who are complicit in breaking into the cave will also be sent to labor.Seneto and Lillia will come with me to patrol.Regulus, you can go clean the lab.As for Vertan, you will assist 37 with her study of the emanation.Don't waste more time on the trivial matters of the Phenomenal Worlds, Integers.
```

### [19] hash=`726e43bb0646483b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p15`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（15.群聚的鸟｜1/4 15:04）

```text
That was the sole reason you were on this island, was it not?Don't let down your guard.The Arcanists on this island are not as easy to deal with as you imagined.Down in the cave, I heard some pretty alluring and intriguing anecdotes.Miss Lilia, this way.You will cover this area.Stay on the radio.Don't worry, Timekeeper.Lilia and I will keep an eye on Manus Vindictae.We are counting on you, Senato.

I have a feeling we are coming closer to a big secret.
```

### [20] hash=`36accfc9093030b6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p16`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（16.雨日钟声｜1/4 17:23）

```text
What what am I looking at so your so-called sacred project is this gigantic IDM computerI was curious about them during my stay in LaplaceThose later versions of the model are so much better than the 66 onesBut this one doesn't seem that far advanced to thoseThis is not a junk piece.The man has sold you is itItems of a phenomenal world are all a wasteThis one is long brokenCome on, mate.You people just leave it in a cave.
```

### [21] hash=`9206c067d05caa03`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p16`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（16.雨日钟声｜1/4 17:23）

```text
It's like sending an infant to the kitchen and waiting for it to bring you dinner.Never mind, you'll see what I mean after I fix it.Can you fix an IDM, Regulus?No, but I've seen the La Paz people do it.Shouldn't be too difficult, I assume.Oh, the dust!When was the last time you sent people down here to clean?Oh, some critters are nesting here.Oh, did I break into your party?In the initial four years, the emanation has a pattern.
```

### [22] hash=`aac2dc57c6ae9139`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p16`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（16.雨日钟声｜1/4 17:23）

```text
First, it brought us back to the 90s, then the 80s, and then the 70s.After that, it suddenly leaped to the 30s.In the subsequent three years, it took place twice.Every record here can perfectly match what is in the foundation's files.Wait, these are the records before 2003, you say.But this one refers to the storm in 1966.
```

### [23] hash=`1e1c5d11960c34bf`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p17`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（17.无归的船｜1/4 19:58）

```text
Now we are listening to the New Year collection.The world famous painting Mona Lisa was found and returned to Musée de Louvre in the afternoon of December 13th.The U.S.Congress passed the Federal Reserve Act on December 23rd, formally establishing the Federal Reserve System.The conflict between Austria-Hungary and Serbia has escalated.Bulgaria challenged the Bucharest Peace Treaty.Tension is building up over the Balkan Peninsula.
```

### [24] hash=`a3eabc4fb88477cd`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p17`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（17.无归的船｜1/4 19:58）

```text
So was 37's mother, who was also on that ship.Why are you crying, Sophia?I was wrong.We calculated it wrong, 37.We miscalculated the impacted area of the emanation.We thought the ships would be safe at the Gorgon current,but the safe area is in fact five degrees away.When the emanation happened,the bow of their ship had just entered the safe area.But it was too late.My dad is gone.So is your mom.I know.
```

### [25] hash=`ecb8cb0b1c2d2c38`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p17`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（17.无归的船｜1/4 19:58）

```text
But why are you crying?My mom and your dad have come back to us, right?Have come back?Do you call this coming back?Like this?In the form of geometric bodies, cold and silent, being pushed to the shore?Arrows always exist.The floating points after the decimal can be reduced, but not destroyed.The perfect circle only exists in the abstract, transcendental world.Of course, anyone in the world can find out the value of pi through the most primitive method.
```

### [26] hash=`d3cac9f9caeacb6b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p17`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（17.无归的船｜1/4 19:58）

```text
Egyptians, Greeks, Chinese, and Babylonians.They have all tried.They made circles with twine, painted on the ground with tweaks,or measured the land with cubit boards.But none of them actually drew a perfect circle.However different their practices were,they found out the sole truth,the approximate value of pi.Because the essence of the circleis hiding in the imperfect manifestation of it,is the truth.

It is eternal, unchanged, pure, and transcendent.Anyone can reach out to it at any time,
```

### [27] hash=`8c89fe510a597c22`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
I just saw it.The numbers of everything and every being would just emerge in front of me.I see it, and I speak it out loud.That's it.210 told me numbers imply our fate.Don't believe him, Vertan.Numbers are just numbers.I know nothing about fate.Hmm, fine.I don't think I like 210.And the feeling goes both ways for us.I'm the ignorant prisoner who sits, and she's the wise one who returns.I will be crushed into dust by the truth, while she will be the star shining above it.
```

### [28] hash=`b25257e40a92bcb4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
The truth is like the stars in the night sky, beautiful, but cold.It has been there long before my existence, and will stay that way long after I'm gone.I mean it.This is a keelene, and even the most traditional, delicate, and expensive kind.It has applied fiery red as the dominant color, and the stitches are perfectly neat in the sea.Just like you, darling.It arrived with a Mearsham pipe, a glass jar, a pack of sugar cubes, and a child in panic.
```

### [29] hash=`3ae1cfd686c060d9`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
The correctors.An ancient profession.Their duty is to remove the loose threadsand iron out the wrinkles on the carpets.In the language of this island, that isto check the calculations on the papyri and even the holes on the punch tapes.No one is capable of doing this job except the altruists, because it issimilar to unraveling a ball of wool.Besides finding the end of theI've left countless scratches on that little forehead.
```

### [30] hash=`655a12c107428de7`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
Poor girl.See, that's the problem every corrector has to deal with.Their job is to correct errors.But what if their own existence is also part of the errors?Hmm?Oh, it's no big deal.There is more than one Lume in this world.She left the complicated patterns behindand came to this simple kingdom featuring numbers only.There she made the first contact with a spinning loom named geometry.She had never seen anything like that before, and it was almost impossible for her to comprehend
```

### [31] hash=`a47c8083a6449e69`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
how it worked.She could hardly convert the numbers on the books into an actual diagram in her brain.Without a whole picture of what she was working on, she resorted to her hard workand more hard work.Then a long time passed, leaving one wound after another on her fingers.Later the wounds even became calluses.In the end her hands were no longertender but tough enough to resist the damage from the loom.
```

### [32] hash=`b1326a8c92e19ac9`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
Yes, she has won aplace on this island for herself.Yes, she's a quick learner.She learned evenfaster than some of the locals.That was not enough because she has beenoutmatched by her playmate, the leading one in the field of mathematics onisland that girl is like a perfect piece of satin born by nature it is decoratedby the beauty of mathematics and geometry no manual work involved inorder to reach the showcase where that perfect piece lies and to stay on the
```

### [33] hash=`daa8b236e3f7c035`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p18`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（18.洞穴之外｜1/4 20:20）

```text
right track and fit into the school she has done everything she could butsomething he shouldn't have.Cut not wood on a public road,open not an unwanted bottle.I don't know what to say next.I guess the best line for this circumstance is,see you later.
```

### [34] hash=`a698d57b0f0245f2`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
Wait a second, just a second!Isn't this still the dungeon?Are you setting us up?All caves are interconnected.This is the way to our sacred place.37, wait.I remember Sophia once told us that trespassing on the sacred place is a serious crime.No worries.The restrictions were to help us not be distracted by theunimportant details in life.It would not stop us from seeking the truth.Excellent.I will tell it to the Abraxas when it shows up.
```

### [35] hash=`0708d9ee224bac6e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
Hey, 37.Are you sure this is the right way?My heart just sank as if I took a bite of those overnight potato chips.Are you scared?Oh, you wish.But when I was exploring underground with Lillia earlier,we ran into some fog like this one.It doesn't bring you any wanted guests, mind you.Maybe you were their target because you are an irrational number.Oh, is that so?You integers will be fine then.Don't beg this pirate for help later.
```

### [36] hash=`ec68c9f76475e233`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
Hold that.Something is coming out.Roosterhead with two snakes as its feet.That's weird.Why are they here?They're coming for us.They say, don't be-Regulus, prepare for battle.Okay, I know.I was just teasing her.Prime Bangle is activated.But they're just a braxis.Regulus, wait for their attack.Do not kill them.What kind of request is this?Listen to me, Regulus.That's of prime importance.Huh?You bet!
```

### [37] hash=`a72e3ad6b968201f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
This is the first guest room we were put in when we first entered the island.No, Captain.This apple has the same strange feeling.We saw the rise of Ceres in the same kind of fog, and before that...That's the same fog as in the Illitial space.That is to say, this fog is the cause of our illusion to see the Ceres and the Abraxas' attack.Don't rush to conclusions.Follow 37 first.And what's that Ceres you were talking about?
```

### [38] hash=`17b235ad7e34b805`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
just picked up a piece of paper.Like this, just bent over and reached to the ground.Probably just some math problems leftfrom the critters' breakfast.You never know.Wait, the Compound of Alchemy,the 12 gates leading to the discoveryof the Philosopher's Stone.This is that alchemy handbook givento Edward IV by George Ripley.Why is it here?Look at this, Captain.Of the Great Stone of the Ancients by Basil Valentine, the one hundred and twelve books
```

### [39] hash=`5a3cdd09043f03ab`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
by Giba, Emerald's Tablet in Latin, seems like there are more ancient texts about alchemyhidden inside the hole, but they are all incomplete.Ugh, so maybe I need to crack some more crossword puzzles to find out about this.I might as well just admit that your cave indeed has the power to give people insights.If I follow its lead, perhaps I'll finally work out the answer about that little thingI've been carrying with me.
```

### [40] hash=`99c29f9f7ed06acf`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p19`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（19.逆行的舟｜1/4 20:44）

```text
Never thought that I'd find the answer here.Easy as picking up a shell on a beach.You don't want to get closer to the truth.Of course I do.And that's precisely why I don't want to get to it so easily.I don't want it to be fed into my brain.The ultimate truth that we're talking about.Critters, monsters, creatures with strange heads, do you worse?This pirate is not afraid of you.
```

### [41] hash=`a55785903489f9af`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p1`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（1.小心行船｜1/3 08:13）

```text
You use a maths model to forecast the storm, and its results perfectly match what the foundation recorded.We just worked out the patterns in the number sequences.Close your eyes, Fertin.Truth reveal itself to you.Truth.Who broke the silence?Saneta is in detention.They're planning to sentence her to death.Those of you who agree to the death sentence may remain seated.Who wish to commute Ms.Senetho's punishment?
```

### [42] hash=`f4d6092fe3f73a45`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p1`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（1.小心行船｜1/3 08:13）

```text
Put your pebble into the pots in the middle of the hall.The pure-blood Arcanist community.The unknown Arcanum power.And the obsession with certain knowledge or identity.Sound familiar?I take not thought for needless disputes.There is nothing we can do!We have another ten minute stopsbefore this ship sinks like a stone!Hmm, that sounds like the turbine just cracked.Great, so only two minutes left.Her true captain will never abandon her ship.
```

### [43] hash=`63b2443a45f963f6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p1`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（1.小心行船｜1/3 08:13）

```text
I've sworn to live and die with Rockin' Apple, the second of its name.Then why is it the second?Sotheby just bought us this ship.I rack my brains to think of all the assurances I could give to get that governess off my back.I think it's better for us to embrace the fact that all things would come to an end, Captain.I have a question for you, Zanetta.Please, standkeeper.Hmm.In the field mission evacuation instructions, apart from the part about asking the timekeeper for help,
```

### [44] hash=`1ad46fe4dd06478d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p1`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（1.小心行船｜1/3 08:13）

```text
is there anyone else we can reach out to for rescue?Er, seriously, Vertian.What's going on now?This is a trap!And you are behind all this!It is you who played that nonsense travel note from 1999,and then blew us into this random sea in order to torture us, afflict us, and now feed usto the f-Go ahead!Give us the wicked villain laugh, you Manus mole!Quit playing innocent here!I don't know!I mean, no harm-
```

### [45] hash=`d495b0f2415715aa`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p1`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（1.小心行船｜1/3 08:13）

```text
Nice try!See what else you got to say when this pirate opens your battery cover and findsMaiden Manus there!Please, do not shake me!how about this program lesson 101 the express route to heaven one shouldn'tmiss I think it would serve you better stand this anymore my records my Dr.Peppers my pirate radio my rockin Apple the second if I done to deserve thiswell she did try her best to pick music though no one is in the mood I

think this piece is not bad as to regular says question we need toslightly twiddle this knob to 1913.
```

### [46] hash=`24a3fd7b867353cc`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
Up here on, the boundless, the beginning of all things, everything originates from itand returns to it.Infinity has no start and no end, but nothing would come into existence if there's onlyinfinity.Look up there, Verdin.Now they are presenting in their true forms, in their purest, newest forms.The essences of numbers exist inside all beings, and the patterns of all numbers exist in all matters.The length of a butterfly's wings and its body are a golden ratio, and the plant leaves grow on their stems in the pattern of the Fibonacci spiral.
```

### [47] hash=`313fac290ba2c0db`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
This is the most primitive rhythm of Arcanum, and it is also the beginning of our extraordinary study.This is the essence.And how do I submit my proof?Close your eyes, Vertin.Only when your eyes are closed, mind open up.Stay fully concentrated and recall the question you want to verify.Only in the absolute contemplation can truth reveal itself to you.The storm.The emanation.The storm syndrome.Where are they from?
```

### [48] hash=`6e2c8f1feb1338d0`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
Foundation, Manus Vindicte, Aperon.What roles do they play?Why does the storm fall when history trembles?Why doesn't the storm fall into the misty land?What is the ingredient of asymmetrical nuclide are?The world is a dark underground labyrinth, but Pneuma can guide us to go beyond all things and reach the exit.Ferdin, can you see it?Why?It's burning!What's going on?Is somebody fighting with a malice now?
```

### [49] hash=`0dd797071b3d23a4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
What's happening outside the cave?Are you straying?If the meditation goes beyond control, you will be thrown out of here!This would be a foolish mistake!No man shall bravest the storm and live, including thee.T7!All those illusions.If it weren't for the heat of the stone bangle that wakes me up.Would I go as crazy as they did?Stone reminds me of the spinning wheel.The collector of asymmetric nuclei R.
```

### [50] hash=`9491372bab5e844d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
If the reagent turns gold after reacting with the fog here,that means the fog contains elements that can be immune to the storm.The colour changed faster than I thought.The concentration of R is hundreds of times...No, thousands of times higher than in the Manas' masks.In other words, whoever owns this cave can produce the protective equipment of the stormin big numbers.Is that the reason why Arcana is here?
```

### [51] hash=`52ce6781a21b27d4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
Mother of Mordor, how does it feel, how does it feel?I need to take 37 out of here.So the Abraxas were people from the Manas.The fog here can affect people's minds, like those around the lake in my suitcase.The Manus found a way to launch attacks without being punished by the Bangal.Or don't they care about the price they will be paying anymore?I hope Regulus didn't throw my words to the wind.I have to get rid of them fast and go out to join the others.
```

### [52] hash=`fb24423e6e81ad3a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
The peace agreement no longer works.Is it safe as long as the contracting parties have no intention to fight?The conditions are not clear.A reckless attack may lead to the punishment of the Bangal.I have to be careful with the method and timing of attacking.Typhon won't give up his friends.Will Stubbe be?The body is melting.It turns into a seed.So this is how the manors fight against the restrictions.
```

### [53] hash=`a61fd9e62835dcea`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p20`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（20.探寻者｜1/4 20:52）

```text
They sacrifice one man to feed another.Typhon won't give up his friends.Will Stubbe be?The sacrificed follower has been absorbed by the seed.Is this some kind of ritual?Here, a cave of everything.Thirty-seven?Can you hear me?M-M-Mana...Don't blink!The dead followers turned into geometric symbols.Is it because of the cave?So the seed is the form of Mana's Vindicte.The forms transcend all matter.Mana's words...

You eaters!...form of Mana's Vindicte.It's more distorted than I thought, it's all over.
```

### [54] hash=`b72b0556276ac840`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p21`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（21.驶来的黑｜1/4 22:30）

```text
Vertin!Finally!The Manus suddenly emerged everywhere like ants.Lillia and I couldn't take them all down.I would have acted sooner if you hadn't told me not to pick fights.All they want is to attack, even if their blood will be sucked out.Insane!Back when we were spying on them, I told Sanetto to screw the peace agreement through the radio.I knew those geometry psychos and the Manus would go mad sooner or later.
```

### [55] hash=`d4582d9eb3610f04`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p21`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（21.驶来的黑｜1/4 22:30）

```text
They were not that crazy when they were solving the math problems.Damn it!What the hell happened down there?The cave is the key to be immune to the storm.There is a cave on this island which has the same effect as my suitcase.That's what the menace are after.What?But...But hasn't she also put on the stone bangle?Even if she can break free from that bangle,There is no way she'd let her followers keep carrying out suicide attacks.
```

### [56] hash=`a5c2d51d13bf5a94`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p21`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（21.驶来的黑｜1/4 22:30）

```text
And if she has signed that peace agreement, how will she take the cave from a Piran?Fertin?I'm afraid you have overstayed your welcome, Ms.Arcana.I have to regrettably remind you not to overstep the boundaries, despite the greathelp you've given to us.However, has this been unto thee, that who led us to the exile in this cave?Not appear on this island.37, no!Bring the human's army here.
```

### [57] hash=`39efad9200e8ccfc`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
Look at you, draped into a ball, meant for a sketch.I saw you the moment I came into the library.The Foundation hold balls too?Excuse me, I need to check something.Z told me you wanted to look up the materials on the mysterious school that believes in numbers here.Masa told me she will thoroughly check the documents in the Foundation archive.So I'll go through the books in the SPDM library.If we can find anything about that school, we can be of more help to Versin and her team
```

### [58] hash=`39ec0aa08a0da29c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
I'm sorry miss Sotheby, but I'm afraid the situation is going to disappoint youWhile you spent the last hour looking for T.Kettler's ear, the kind-hearted monitor assistant already gained a valuable access to the libraryBut I haven't found any record regarding the mysterious school that believes in numbers yetMoissol said there are so many books here that they can cover the entire back of a stronzei beast!
```

### [59] hash=`3c23ee60e1ea29b6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
A bit exaggerated, but she's right.Nevertheless, the librarian was transferred to a more important position years ago due to the storm.Many old books are not yet sorted.Some even went missing in the chaos.The only relevant materials I could find are the stories of Pythagoras and some books on mathematical theorems.But I don't think they have anything to do with Vertine's issue.I don't do anything to help.
```

### [60] hash=`797979b2ef4b1f3a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
Being emotional, it doesn't work on this professional member of the foundation.With investigation permission, I can't take you out to collect information.But in fact, there is still another reference room only known to the most outstanding monitor assistant.It's a violation to make noises in the library!Please follow me, Miss Sotheby.Thank you so much, Miss Boulaniche.But, of course, it's only out of her sense of responsibility, not for some personal reasons.
```

### [61] hash=`dfcc545614da5de6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
The reference room storing unnecessary information.It's a place ignored by most staff.Even so, this careful, reliable monitor assistant will not let go of any details.I hereby officially appoint you as the Chief Assistant of Monitor Assistant of SPDM.I will take my responsibility and teach you how to become a devoted foundation member.What is your first task?Read through these unsorted old files.All of them.
```

### [62] hash=`814d3da4888f0cfb`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
All the archived ones.These are the last parts.Some are discarded administrative documents,low priority materials,and substandard reports written byrookie investigators.By the way, you should knowI didn't sort any of them outfor you.And they don't necessarilyhave what you want.It's alright.Leave them to me.I love reading better doHere's the key.Keep it safe.You can sit on the cushion there when you sort out the files
```

### [63] hash=`963624f45e4b3951`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
I I don't want your dress to stay in the stone bench.I'll go see if I missed any filesYou on your familiarity with these fires when she's backDated looks like I didn't miss any relevant files quite a long dayI doubt if that spoiled lady can finish all the materialsShe must have been bored and fallen asleep, waiting for her tea kettle in the dream.It takes much more than dancing at balls to be a foundation investigator.
```

### [64] hash=`40812a5a71d744db`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
I'll send her back to that teacher when she wakes up.And it will be the kind-hearted Matilda who finishes the task for her.Being a great monitor assistant comes with great responsibility.You didn't fall asleep?Did you sort out these files?It looks like you meet the basic requirement for being a rookie investigator.You are more or less qualified to be my assistant as a chief.On this interesting report, it tells a lot about the storm and the numbers.
```

### [65] hash=`bf8cbf107863c0e1`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
Show it to me.To say, it is undoubtedly a violation to submit such a report.But it will be a travesty of the truth and human sense if I cover it up.Sense?Justice?They have always been the creeds in my heart.and are now the reason why I've decided to write down the whole thing.A long time has passed since the first attack of the most severe crisis in our time,but we are still wondering, what on earth does it mean?
```

### [66] hash=`1455c855279f918d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
That was the eve of the millennium, of which no one had any memories, illogically.The next day time was already reversed to 1996, the moment we opened our eyes.We walked out of the building made of grey and white marble as usual,Hardly aware that the sun we based in was from another time.Our survival was unexpected and almost unbelievable in such a calamity which swept the globe.Why did the headquarters of the Foundation survive the reverse?
```

### [67] hash=`c4343c00b9e29ba4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p22`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（【特别篇-星】1.友好会晤）

```text
Why couldn't we find our younger selves in the outside world?Did any other region survive it as we did?What was the cause behind this calamity?I didn't know, nor did anyone else.Things remained unclear until time was reversed again.This time, we all witnessed that rain in the 80s.It became the time-
```

### [68] hash=`26a3c6a48cdf62aa`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
Before she became the Time Keeper, the Vertim wasn't born a Time Keeper.Didn't tell you that?Wait, no one is born a Time Keeper.It's not an inherited title.Anyway, this report includes the secret chronology only accessible to the coremembers of the Foundation.You can only check it under the supervision of the Monitor Assistantbefore you become a qualified investigator.No matter what the reason is, it shouldn't
```

### [69] hash=`93cd754754d504a4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
have been shoved in this dusty room like rubbish.To evaluate its authenticity and risk,the genius Matilda Bwanish will fulfill her dutyas the monitor assistantand carry out a thorough inspection of this report.If you agree to this resolution,please nod, Assistant Sotheby.That was 1985, a gloomy, miserable nightcompared to that peaceful morning in 1996when we were only bothered by confusion.We didn't expect time to be reversed again,
```

### [70] hash=`f6cf733b03f775aa`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
nor did we understand the consequence.Even now, I still remember Paulina's desperate cry.One of her hands was already inside the safe areawhen she fell at the entrance to the headquarters,and that was the only part of her left was the next second.The only legacies we found were an engagement ring on that handand her favorite blue polka dot scarf,which we used to wrap her remains in zen.Be honest, I admired those who still remained calm
```

### [71] hash=`6453d56650f13cd3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
and sympathized with the Arcanistson the edge of mental breakdown.It had nothing to do with the one quarterArcanist blood in my body.It was only the kind of empathywhich all mankind would shareout of instinct in the face of a hopeless calamity.We lost many, too many colleagues.In the materials they sent back,we even saw all the horrifying phenomenasuch as one's veins turning into electric wires.Since then, the storm, a word simply taken from visual observation,
```

### [72] hash=`b1086f95332ba962`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
has been used to refer to the calamity.Of course we can have a word for the calamity itself,but what words should we use to conclude all the absurdity and panic?Before the storm we were all familiar with time.It was supposed to be a straight line connecting the past and the future.We followed the line to move forward.We broke free from ignorance.We built civilizations.We developed technologies.We promoted the well-being of mankind.
```

### [73] hash=`8e99c1cb691c4308`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
And we improved our living conditions step by step.We were so sure that we were making progress on the right path.But then, the path was taken away all of a sudden.Our closest old friend, where are you taking us?To the two most painful war times in the 20th century?The era when no one had ever heard the hiss of steam engines, or the century when mankindwas yet to be enlightened.So far, mankind has achieved a lot in history.
```

### [74] hash=`455d6ee2b836c207`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
Dynamos, automobiles, flyovers, railways, hospitals, poor houses.But if it goes on like this, what is the point of all the efforts we have made?Now we are like a shipwreck left on the island of time, witnessing the fall of themodern world in the unstoppable tsunami.Even though the foundation has lost a lot of staffmembers they are still doing fine compared to Laplace.My younger brother was a good example.
```

### [75] hash=`1ac22b8da08a62e3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
He was the most sensible person I have ever known.On the first day of the second reversehe told me in a calm manner.At least we have reaffirmed that Newton was right.There was never an arrow of time in classical mechanics.Neither in relativity nor quantumMechanics that means this is absolutely normalWhether the time goes backwards or forwards even if it starts spinning around like a tabletop football player
```

### [76] hash=`17cbeced384aeec5`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
They're not against the law of physicsWe can go back in time and keep my guy a medal of great pop itNext day he almost fell off the sixth floor due to excessive drinkingAll the perceptions of time and space developed to this day were overthrownWe couldn't find any series to explain the storm in any existing researchersThere could only be two reasons for this situation.Either we've been completely wrong all the time, or we've come to a brand new world.
```

### [77] hash=`e1c280c7a5e1efd6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
And this new world can never make sense in the way of science, or that of physics.It cannot be verified by an independent third party, and it is impossible to be comprehendedthrough reasoning.Is it true that we have been going the wrong way?Is it true that those once proven wrong by history, those arcanists who claimedpossessed gnosis are actually on the right path?In fact, the one who put an end to the chaos was
```

### [78] hash=`7eb6861dcbff590e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
indeed not a human.This thing, I had no idea what it was.It claimed to be a machine whichnever stops working.It left the limitations of our brains and the metaphysical mistakes we makeceaselessly.But it did solve the most urgent issue.A system was built to tacklestorm relevant emergencies after it took charge of Laplace.The first measure itadopted was contacting all the existing branches of the foundations at the time
```

### [79] hash=`7abdfada8b6ceaad`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
to confirm the scale of available manpower.Then it built observationstations all over the globe to find if there were any other regions immune tothe storm.After that, numerous offices responsible for deducing the cause ofthe storm were established.Even though there were countless disagreementsduring the research, at least we had taken the first step.I handed in the application to take part in this mission,
```

### [80] hash=`463e3361b161008d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
determined to get rid of the fog in my mind.In 1986, I was assigned to the office in Egypt.All my friends came to the dock to see me offbecause we knew it could be the final goodbye.Even though we were equippedwith the emergency communication devicesissued by Laplace, we were still not clearwhen the storm would assault usor where we could hide nearby.What really scared me was not the threat to my life, but the possibility of dying ignorant.
```

### [81] hash=`2302fda9eed2d606`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
Then I boarded the ship to Alexandria from Athens, and that was when I met.Now when I recall it, it was almost impossible to ignore that group of arcanists on theship.There were about a dozen of them, all in eccentric stitched robes.They were followers of a strange school which mixes arcanum and mathematics.I talked to them.No matter how much that conversation bewilters me now, I was more excited than confused at the time.
```

### [82] hash=`684c026a9430608a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p23`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.湿透的科学）

```text
They also survived the storm in 1996, and they noticed the unusual changes taking place in the world as well.That means, they actually met another group of survivors.From the millennium.There was no one who survived the storm?
```

### [83] hash=`d3d224deffccb79b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
A mixture of Arcanum and Mathematics!The ship on the Mediterranean!Unbelievable!Our investigator actually met this group of Arcanus to believe in numbers, and even left such a precious record down on paper.Does it mean we are close to being helpful to Virgin?Certainly!It's what we deserve for all the efforts today!But why did they leave such an important report in the reference room storing unnecessary information?
```

### [84] hash=`57c86754105580cd`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
Did they misput it here after the chaos of the storm?Among them, the most easy-going one was Hugh.He was an engineer as well as an Arcanist.We shared the same preference for human technology, and that became our common topic.Hugh was in his thirties, red-haired, cheek sunken, and deeply depressed due to some kind of eye disease.He was a decent man, with a prudent attitude, working at a desk most of the time.
```

### [85] hash=`7a3a1f4a1e274c7b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
He reminded me of the imperial miniature painting artists in the Sultan's palace.Most of them ended up blind after toiling for their life.He showed me the picture of his daughter.I don't have children, but I could feel his happiness as a father.Although I got along well with you, he seemed quite out of place among that group, whichwas actually led by...her.I don't know what words to use to describe her.
```

### [86] hash=`304e32ecc2f18bfc`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
She was like...a meteor shower, a tempest, or...an unreasonable catastrophe itself.Her existence was just like her name, it was simple, yet implied a lot.Please forgive me for my cowardice.Even now I don't have the courage to write down her name, if one would call that a name.In fact, she was quite a kind of warm-hearted person.Among all the unregistered arcanists I've met, she was one of the nicest ones towards the foundation.
```

### [87] hash=`6debc3c6cfdc38f5`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
She looked young, even though I heard she had a daughter too.Besides, she still possessed the innocence of a child, and that kind of excitement exclusive for genius.That's right, it seemed the whole world was like a sparkling toy to her.Our communication was heart-stirring at the beginning.Both of us were eager to find out what was happening, like two shipwrecked victims grapplingat each other on the sea.
```

### [88] hash=`65ecdb03c7e5686c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
But I didn't have the slightest idea what she was talking about, actually.The problem was not the typical communication issues between humans and arcanists.I was sure the language we used didn't pose any obstacles, but still I couldn'tWhich has never been real or true, and that's why the chaos in this world is not worth any attentionand we should focus on what happened to thesupreme existenceWhat an utter disaster combining modern maths with the ancient superstition
```

### [89] hash=`209f0eafbbe105eb`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
I saw another hubristic arcanist pretending to be the prophet by reliving PlatonismI don't even bother to mention the Balderdash on soul numbersEven the New Age movement could use some of her absurdity, but that was not yet the end.She even claimed to be aware of the exact year when the next reverse would happen.But when I asked her about it seriously, she said,My apologies.I've made an oath.I shall and only shall reveal the demonstration to people who have their own soul numbers.
```

### [90] hash=`72304e715f89e937`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
I'm not sure whether she was making fun of me or being serious,But I had this feeling that she was eager to tell me how she was granted the secret througha moment of aflatus.It seemed she just saw through the loss behind all things instead of finding them throughlogical deduction.Can't you see it?It is right in front of you.After I expressed my inability to comprehend her words 30 times, she finally gave up
```

### [91] hash=`4e17ae2025a8c88c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
and proffered regrets.I'd rather take it as a new kind of humiliation.What really irritated me about her, however, was her contempt towards science and all thescientific research methods.As far as I am concerned, the value of a theory lies in its reliability, universality, andgeneralizability.Our pursuit of the truth has laid the foundation of modern science, allowing us to changethe world.Yet, in her eyes, the value of a theory lies in its beauty.
```

### [92] hash=`f9e47cd3ea0b5ddf`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
I talked to her on the current situation, and I told her how we would save lives andpreserve the hard-earned technology of mankind if we could find the pattern of the storm.It was of course not an easy thing to do and would take enormous manpower, so I askedher sincerely to join the Foundation.Yet again she responded with contempt.She believed they would only become another military squad of the Foundations.
```

### [93] hash=`4eb171cd3f347dee`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
Darling, maths are beautiful for their uselessness, that's why it remains noble and graceful inthis sordid world despite you humans' reckless action of using it to calculate ballistic.She turned down my invitation and left an unfairly negative comment on our storm observationproject.The observation stations you built are destined to be toppled because their basis is thefragile world that follows the laws of physics.
```

### [94] hash=`398f77cf74208874`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
The efforts you've made are like nails on a sand beach, which will only be carried awayby the next tidal wave.But I said, perhaps our efforts are in vain, but someone has to do it.We will try every corner of the beach before making the conclusions that the world weare living in is already a hopeless ruin.What a pragmatic, rigorous and rational speech.But dear, the world is a hopeless ruin.She had never given any proofs or details that showed rigorous logic, and the reason
```

