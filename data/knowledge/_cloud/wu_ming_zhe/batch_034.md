# 剧情图谱抽取 · batch 034

- 角色：`wu_ming_zhe`
- 批次：**34** / 共 1 批（每批 25 块）｜本批块数：**25**
- 筛选：标题含「1.4」｜offset 380
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_034.jsonl`

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

### [0] hash=`6a4ac33d3282c7b7`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
for her inactions was an oath she had made before some stone?Therefore I believed her words were only the nonsense of a lunatic.When we first met, I thought she was different from all those psychos who mistook themalfunction of their prefrontal cortex as the will of God, for they turned out tobe the same.In the name of human sense, I swore everything she said was absurd and ridiculous to me, until...
```

### [1] hash=`a7c1f032155947d0`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
Madame Z said the Arcanists on that island are all named after numbers,because they have a strong belief that numbers are the essence of their souls.The investigator wouldn't write down her name.Is it because of the conflict between their beliefs?Submitting such an unfinished report would only cause problems for the reviewers and evaluators,but this investigator didn't even write down their name.Don't worry, Ms.
```

### [2] hash=`825111ace586159f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p24`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.通天之塔）

```text
Burnish.I'm familiar with this situation.Every time, after the brave Typhon defeats Jupiter, he returns to the auto-island.But each time we twist the ear of Mr.Glassbox, Typhon will show up again and again.We must prepare Lunafixer.Don't forget their favorite jigging magical beans.I don't have those materials with me right now, but I can write to them.It only takes a month.Use the task from me when you found this valuable report.

Well done, Assistant Sotheby.Now it's time for the great Matilda to show a little bit of her greatness.
```

### [3] hash=`b8df8c44765db2be`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Judging from the omen, it's at the northwest, the beginning and the ending of the ring,where the wall reflects repeatedly.West of SPTM, this one is straightforward.The beginning and the ending of the ring is not a problem either.The icon of the computing center is exactly the Ouroboros, a serpent eating its own tail.Here we are.But where the wall reflects repeatedly, does that mean a closed room with mirrors?
```

### [4] hash=`a1ffaa4b9c1fef98`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
The mirror in the display center is a huge kinescope in the wall,and the one in the airtight laboratory is a crystal clear observation window.The one in the rehab center?No, no, no.The mirrors in the operation room have been replaced with curved electronic screens of steel structure after that xenopilot made a scene.So, where is the answer?Didn't you apologize?Where did you come from, dork?Wasting my time?
```

### [5] hash=`3446e30085ba5d9e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Rude!That gentleman doesn't look well.He's covering his face.Nose is running with purple liquid.Don't go to the weekend party night.Absolutely not.The researchers here are too busy to do that.The computing center is working on the most urgent and vital project.The research on the immunity to the storm.We should not disturb them unless it's an emergency.So please stop calling the office and put down the telephone, Ms.
```

### [6] hash=`5590fb688c930d74`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Sotheby.This is not the ear of a tea-kettler and it won't take you twenty twist balls.Les débutantes, mais quand même, c'est trop bizarre.New members with caution and patience trigger the reflux at the right time.Aww, I have to admit that Vertena has won a victory.I just read the map on the counter.You mentioned where the wall reflects repeatedly.Refer to the racquetball center here.You see, its icon is a bouncing ball.
```

### [7] hash=`8c1f25c397a3eeea`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Let me take a look.It is the right direction.Empty boxes, glasswares and copper pieces.Hmm, looks like our destination has piles of metal.Good job, Assistant Sotheby.I have to say, I might have gone a bit too hard on you.You are more capable than I thought.Thanks to your prompt reminder, we have saved quite some time.Sotheby is glad to help.Uniche, since you're such a talented diviner,Why don't you just divine the reason for the storm with your inherited arcane immobility?
```

### [8] hash=`a1e914228c78eb8b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
According to Ms.Moisson, the reason still remains a mystery.If the Crystal Orb can reveal its truth, everything will be much easier for Versin and her team.Find the reason for the storm?Possible for sure!It's a typical mistake of laymans to believe one can see everything's for divination.You are an expert on potions and arcane creatures, but you have little knowledge on other subjects.Haven't you received any systematic education on Arcanum?
```

### [9] hash=`e99241ba5b168b8c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Education on Arcanum?I'm of course well educated in Arcanum, with Ms.Masuo as my tutor,and my arcane friends such as Typhon from the auto island, Jupiter and...Alright alright, now I've understood the fact that the education you have received is not......systematical.Or say, incomplete, imperfect, inelegant.But don't worry, because you are talking to the kind-hearted Matilda.She will spend her valuable time to make it up for you.
```

### [10] hash=`1e0f4f3a88527500`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Some of our quantum knowledge is not completely separated from that of human science.For example, the modern pharmacy and chemistry actually originated from the experiments ofthan alchemy in the ancient times.They developed into two different systemsbecause arcanists focused more on the knowledge ignoredby scientists, which is gnosis.The knowledge we learn from divinationis exactly under this category.
```

### [11] hash=`7a88f5005892df65`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Let me fill you in with more details.If two human researchers test Nell's lawat two different places at the same timewithout making any mistakes, they will alwaysreach the same conclusion.Or, if two potionists use the same ingredients and follow the same formula to make the cough-cough stop-stop potion separately,their products will also have similar effects.However, if two diviners respectively perform divination on the same thing, they will probably see totally different visions.
```

### [12] hash=`fef5ea93327c7e25`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Because what the divination shows is merely omens.The interpretation of these omens is in fact a kind of subjective deduction based on the reality,And there is no such thing as a standard answer.If the two diviners draw the same conclusion,it is more of a coincidence than a result that implies generalizability.So diviners never check the accuracy of their divination through the review of Pierce.And this is an example of Gnosis.
```

### [13] hash=`298fed6a63fcc94a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Unlike human sense, it is unique and possesses no universality.In other words, even if someone finds out a reason for the storm through divination,they can't have other diviners verify it,because a hundred different diviners will give out a hundred different conclusions.The scene will be even busier than a concert at Musique Verain.Being said, the more possible result we get from the divination is nothing.
```

### [14] hash=`a2c5531cf5994691`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Divination cannot bring knowledge which the diviners have never learned.The divination of such world-class knowledge,as complicated as the reason for the storm,can only be performed by world-class diviners.We may find one or two definers like that if time continues to be reversed, like Nostradamus.Hmm, but he lived in the 16th century.Besides, if Nostradamus is not always right...But most boonish is!
```

### [15] hash=`1c992274ba37769d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Thanks to your divination, we're getting closer and closer to that report, right?You, you, you are right!Finding items, interpreting dreams and making simple prophecies.All these things are just a breeze for the bright and clever Matilda!But inquiring about the storm is beyond my ability and it will only bring misfortune.Hmph!I will never make such a stupid mistake.In fact, this half of the report and the handwriting of the author are perfect divination media.
```

### [16] hash=`1438303592e0e0dc`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Besides, our target is not far away from us, and I'm familiar with the surroundings, which have made things much easier than usual.It is true diviners can improve the accuracy and controllability of their gnosis by practicingrepeatedly, holding the rituals properly and making targeted preparations.But that still doesn't mean the result will be absolutely accurate.The report says a person who mentioned the school of numbers claimed she was enlightened
```

### [17] hash=`b6f929ea4de5fb23`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
about the year of the next storm, also by divination.I am not sure what kind of arcane skills they used, but numbers are indeed a kindclaiming to be prophets who can predict the doomsday and thus requesting unemployment benefits.Unemployment benefits?Oh my!The outside world is far more wonderful than I thought!Fascinating!This boonish is even greater than I expected!You bet!What's the greatest, Miss Nociby?
```

### [18] hash=`6ea0ad25119c7f57`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Now, it's the moment to verify the results of my divination.If you look at the ground after the rain,You can often see a wet long trail like this one at the end of the trailThere may be a snail slowly crawling forwardYesForward the snail marks the direction for us.But what if we don't see any snails at either end?How are we going to distinguish the direction to the future from that to the past?You just figured out how those researchers handled matters
```

### [19] hash=`417de852c7dc80b4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
Face the ignorance and do everything they could to find the answers.When the rain rose, they struggled to collect every component left, hoping to preservethe castle built by science.Unfortunately, the effort was in vain.Another wave washed away the castle and restored it to quicksand.Even so, they still worked hard in that house like canned sardines to record whatwas happening because they believe at least the can holding them was a safe
```

### [20] hash=`2ed5aa9dbc30fe8b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
place.Yet in the end they found that the can was only another sandcastle on thebeach.Everything they were familiar with disappeared when the first drop ofrain rose.The chaos didn't last.If it really was the rain that swept awaythe snail and messed up time, then we should look at the silver lining.Doesmean we will find out the truth of time once the secret of the rain is revealed?There has never been a shortcut like this one, since time is only an intangible concept.
```

### [21] hash=`8c768d8d10aafb31`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
So then, observation stations were built all over the globe.The staff learned how to collect andkeep the valuable samples efficiently in no time.The little boxes they used to store theraindrops are still being upgraded even now.Order and silence were brought back to the labs.every piece of gear was placed back on the right track.It was a grand feat andno one could have accomplished it inside this huge cumbersome machine except
```

### [22] hash=`eb4190ef60c80101`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p25`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.白日航船）

```text
another machine.She took no sides and sought only predictable results.That'swhy she made a decision as soon as she read that report and its attachmenton her desk.The former was about a delicate component which flapped like ain that huge machine and the latter was a piece of paper full of circles anddots.Then she stored the information on her hard disk and destroyed the reportand the paper which claimed to have recorded the locations where the storm

might happen, yes the one with the butterfly like drawings, was retainedfor data comparison.It seems she's satisfied with the result.
```

### [23] hash=`94331b100b68177a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
Are we in front of the rocket ball center?The ship showed copper pieces.We need to find something that seems to be locked, but is actually not.Nothing can stop the genius Matilda.The trip to Egypt didn't go smoothly.The ship was hit by a common storm at sea.We were lost in the fog after that, completely off course.Then something merged from the water.Since the first storm, the Foundation has received frequent sightings of arcane creatures
```

### [24] hash=`9eed4cad2294d554`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
which should have been extinct in history.I had no idea what I was shooting at even after I emptied the clip,and I didn't know what to do, so the arcaneists brought us back on course.She named the precise longitude and latitude of our location,even without using the sextant in the spare cabin.I wonder how she did that.Perhaps the world did look different in her eyes, then when I was about to step on a random
```

