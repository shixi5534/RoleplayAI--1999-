# 剧情图谱抽取 · batch 004

- 角色：`wu_ming_zhe`
- 批次：**4** / 共 8 批（每批 40 块）｜本批块数：**40**
- 筛选：标题含「77号往事」
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_004.jsonl`

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

### [0] hash=`42ec2edf5a595cc6`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
Order of enlightenment?You mean those troublesome guests?Guests?I don't likethem one bit.They've scribbled all over the place and made a mess of the rooms.They hurt my baby.Oh my poor baby.Don't be scared.Everything's all right now.Are they still here?Oh of course.They made an offer that I couldn'trefuse.After all, how much did they pay you?Oh, you are naive, my sweet child.There arecountless things in this world that money can't buy.
```

### [1] hash=`f89f0d9d1f63314b`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
A traveler can't buy the suddenappearance of a hotel at just the right time.A crying child can't buy the comfortingembrace of their mother.And I can't buy that thrilling satisfaction brought by sweetDarkness enough of your endless rambling.I can't waste any more time talking to you.I can'tsleep to sleepEverything to the adults.YesWhat a good child you are
```

### [2] hash=`c57caf62765ec155`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
Found his medication prescription and ohIs this his notebook?Just as expected boss this motel ain't what it seems to beAin't no way that letter was written by StefanTake a look the writing in this letter is delicate and slender while the writing in this notebook is total chicken scratchEven a blind person could tell they're written by two different peopleStephen didn't write the letter, so it's very likely that the person who sent it wasn't
```

### [3] hash=`67fd3818f7b0cbda`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
Stephen either.And this?Ugh, I hate numbers.I'll leave this one to you, boss.It appears to be Mr.Stephen's records of his daily expenses, along with some notes,cigarettes, alcohol, and a significant amount of psychiatric medication.It says, he was tormented by his hallucinations day after day, so he had to increase his dosage.And it says he saw room numbered 707 here.The motel only has two floors, there can't be a room starting with seven.
```

### [4] hash=`cc29bd5f8fa58bfc`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
Did he describe it at all?He said, the room had a bright red door that seemed completely out of place.Maybe it was just one of his hallucinations.No, it's not that.He also saw all kinds of things, a pair of twins in the hallway, long hair hanging fromthe ceiling, and he saw Barbara, but assumed she was another hallucination.This proves that Barbara's been to the motel, which means...I'm sorry to say that I've never met an Arcanist with the head of a sheep.
```

### [5] hash=`787211017143b823`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
I can help you ask round, if you...Why did she lie to me?So did you find anything useful from the expense record?This distorted reflection in the mirror is probably a result of the excessive arcanum in this motel.A ritual similar to Bloody Mary used to be quite popular among the kids in this town.If you look into a mirror at exactly midnight, the spirit within will morph into the shape of the person you desire most.
```

### [6] hash=`e1a1594f86750dae`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
But if you respond to the spirit's call, it will drain your soul from your body.I always thought those were just myths.So did I.But after all the strange things I've seen, I've become less surprised.These spirits feed on the energy of our souls.That's why you should never trust a word they say.The people who are tricked by them fall into a kind of trance and some, like Mr.Stefan, go crazy.I wonder what he saw in the mirror.
```

### [7] hash=`d124e2031cb54e63`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
Anyway, I won't repeat his mistake.For mercs like me, the deepest despair ain't external danger, it's internal hesitation.If some pale imitation makes me hesitate so easily, then how can I claim to be ableto protect others?You've got to be able to stand your ground.A cunning criminal would use every excuse to defend themselves in court, and a schemingspy would wear all kinds of disguises to gather information on the enemy.
```

### [8] hash=`2e7d47a872ab8da8`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
That's why we'vegot to stay sharp.When it comes down to it, we only have our own two legs to stand on.Mercs ain't philosophers.Once a merc starts pondering morals, justice, and ethics,they're digging their own grave.For a merc, the mission objective is the only thingmatters.Overthinking don't bring nothing but disaster and destruction.That's whyshe...no...it...won't fool me.The folks on the ranch adored little Kayla.
```

### [9] hash=`8e9fd9f1e0f6aad3`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p12`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（12猎犬与姑娘）

```text
She wasthe apple of all their eyes.How dare this ugly imitation.So here's myresponse.Let this serve as a reminder to remain vigilant.If there were aSeatful Spirit of the Year Award.I'm sure that would win.
```

### [10] hash=`820b93833f267831`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p13`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（13反刍的胃袋）

```text
Stefan Garcia, a Zeno captain, 36 years old.For unknown reasons, likely connected to ManusVindicte, he moved into this motel.He attempted to make contact with Zeno several times,all of which failed.During his stay, he was tortured by increasingly intense hallucinations,delusion and fear.And as a result...As a result, he committed suicide.And that's everything the evidence shows.But that don't make much sense either, does it?
```

### [11] hash=`baf415066d9926f8`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p13`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（13反刍的胃袋）

```text
When all these unusual things happened, she was happy to stand by and watch.But by whose orders?Some larger, more mysterious organization?Gimme a break.What if she doesn't desire money or power?So what you're saying is that you need to ask Little Miss Maid a couple morequestions.Precisely.That spirit morphed into Kayla, so it must have seen her face at some point.Which means that at one time, Kayla was in this room.
```

### [12] hash=`ca9e951f1102ebb1`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p13`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（13反刍的胃袋）

```text
And you're right, Tuesday's definitely not a run-of-the-mill motel maid.It wouldn't be wise to approach her rashly.Let me finish up here first, then we can go question her together.Alright.I got nothing.Let's go find that maid.I have a few questions for her myself.Where'd the body go?Ain't no signs of dragon neither.Who?How?The phone again.What do you think?Should we answer it?I bet it's another one of those prank calls.

Those weren't prank calls.Someone was sending a distress signal in Morse code.Here it is now.Who's this?
```

### [13] hash=`b23d07e67147eed1`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
Second, I'm now trapped in a red room.This room isn't the same motel as yours.What'sdifferent is that it blocks all forms of communication.I couldn't get the room to open, and my voicedidn't reach through the phone.That was until a gunshot broke this intangible restraint.This small room contracted violently, and now I can communicate with the outside world.First, thought it was an earthquake, the contracted space soon returned to normal, can't do that, can they?
```

### [14] hash=`c6c467c79a4da041`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
Before this happened, were you using spiders to communicate with the world outside?As luck would have it, there are many spiders here, thanks to the prevalence of spiders in urban legends, I assume.There's some paranoia about spiders living in hair.It originated in a sermon from 13th century England.A woman was always late to mass because she spent too much time styling her hair.Eventually, a devil attached itself to her hair in the form of a spider.
```

### [15] hash=`1e5a5d9bfcc3feff`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
Yes, they delivered messages for me in their own peculiar way.Being completely isolated from the outside world greatly unsettled me.It reminded me of that terrible phenomenon.Fortunately, that wasn't the case.But you're still trapped in that room, right?Yes, the door's gone.I can't get out from the inside.How did you get in there in the first place?Or rather, who brought you into that room?Well, who else could it be?
```

### [16] hash=`55b020e622b5c2ec`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
Tuesday.Just as I expected.Wait.You're the driver who left me on the road, right?Yeah, it's me.I actually changed my mind and turned back to get you, but you weregone by the time I arrived.I guess that's when you came to this motel, right?Tuesday saw me and invited me here.Oh.Did you want to ask me something?Have you seen a girl of about five foot three here, in a white dress, curly chestnutcolored hair, green eyes, small hands?
```

### [17] hash=`4f7b597757f6a15e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
We have seen her first arrived.I saw a girl who matched your description coming down the hallwayHe was carrying an empty basketPresumes that she'd been shopping in the town nearby if I recall correctly she didn't check outThank you.How can we find this room in the hallway number 707 look for door covered in redLooks like the phone got disconnectedSo Barbara's in that room that Stefan saw, number 707.
```

### [18] hash=`b2656b49db6c0fc2`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
I'm going to find it.What about you?Heading into town for Kayla.I did notice a weird spot in the hallway earlier.The maid's footprints were going back and forth like there was an entrance there,but I didn't see no signs of a door.I wouldn't be surprised if you died by your own gun one day.Heh, that'd be a memorable way to go.Enough kidding around.Our little miss May tried so very hard to hide Barbara from us,
```

### [19] hash=`007e2d0a1c1b209d`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p14`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（14保佑她）

```text
but I guess the lamb's out of the bag now.Yes, it's all crystal clear now.Let's go.Hold up a sec, boss.Do you have any candies?I'm running on fumes here and I ain't got no way to replenish my stash.Us and Barbara will be out of here soon, and you'll find some candy in Kyla in town.
```

### [20] hash=`ee81ff297718bc7e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p15`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（15服务热线）

```text
Are you not satisfied with my services?No matter what, you shouldn't have cut the phone off.Nor should you have isolated me from the outside world.Because you should know better than anyone what that means.Why should I?All I know is that a poor, helpless child like youshouldn't be alone on the roadside.Where's your mother?Didn't she tell you to be careful?Hmph, that's exactly what a child would say.
```

### [21] hash=`b1c6b37dff60edde`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p15`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（15服务热线）

```text
I've always felt a familiarity with you, like I've known you for a long time.Can you tell me about it?Why were you out here on Route 77 all alone?Maybe I can help you.Have you heard of Atu?Oh, it's a magazine about fashion, trends, and the avant-garde.My brother loved that magazine.but my father found it unacceptable to think his eldest son would read thosesofties magazines instead of working on the farm.
```

### [22] hash=`5616388a85926958`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p15`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（15服务热线）

```text
Fashion, trends, disco.Thesearen't things a Texan man should pursue, at least according to my father.In theend, my father destroyed all my brother's disco records along with hisarrived a local resident told me not to stay at Tuesday's motel he said his auntwent mad soon after she stayed here I remember that lady her head was solarge it reminds me of those stories of people with deformities so I had her
```

### [23] hash=`f8c35118d3652402`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p15`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（15服务热线）

```text
watch a freak show at midnight sadly she didn't seem to enjoy it at thistime of year the farmers run their combine harvesters on the fieldsThe harvest is a joyful time of year, but the accompanying noise always frightens thechildren.Have you heard the stories of how naughty children get too close to harvesters and getcaught in them?Losing a hand or even a head, fields, machinery, children with severed limbs, these stories
```

### [24] hash=`6bfcfc4f79b5b1af`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p15`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（15服务热线）

```text
are exactly what my motel's missing.My baby's calling.Please excuse me.I don't want another temper tantrum on my hands.Apologies, my fluffy little child.I look forward to our next conversation.Talking to you always brings me inspiration.But the motel's been too busy lately.It's starting to get on my nerves.See, this is what I mean.How could I bear to send you out on your own?You'll stay right here in this cozy little room until you're fully recovered.
```

### [25] hash=`284b3d552ccf8539`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p15`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（15服务热线）

```text
I don't need this special treatment of yours.Staying here won't cure my illness.Just get some sleep.You'll come to your senses after a good rest.I'll see you soon.Many times have I told you not to eat things off the floor.Are there, my sweetheart?
```

### [26] hash=`f2200571321ebd76`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p16`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（16苦目糖）

```text
is this the spot sure is shooting look these footprints they're less than 10minutes old but where's the door to room 707 I cansense some energy fluctuations nearby but they're definitely not from arcaneskills what else could produce such intense energy oh can I help you withsomething miss Tuesday I've got a question for you do you know how toan extremely challenging task.That's when I eat a third candy.
```

### [27] hash=`f2180d0487ddb0d1`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p16`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（16苦目糖）

```text
At that point, it's gettingextremely dangerous.I should be able to see now.Should I take more?Absolutely not.The largeamount of candy you've eaten is exactly why your eyes have failed you, and in such a crucialmoment no less.Excess leads to destruction.This is true for all things.You do well toyour limits, also had to be careful not to frighten those children too much.You've always put yourfaith in these candies, haven't you?
```

### [28] hash=`3223534d4684c503`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p16`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（16苦目糖）

```text
One candy, fifty percent recovery, two candies, one hundredpercent, three candies, and you can tackle even the most insurmountable problem.Oh, how dependablethey are.Just like the venerable Argus, who succeeds in any job she takes on.It's preciselyyour excessive confidence in these candies that has led to your marvelous destruction.Just as the people's trust in you as a mercenary has led you to this bottomless abyss.
```

### [29] hash=`0f03e20515a525a7`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p16`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（16苦目糖）

```text
Oh,you poor thing.And of course, they'd never have imagined this.Argus, the mercenarynamed after the hundred-eyed, all-seeing giant.It's, in fact, blind fool.How are you?There you go.Now there's no way you can miss.But do you have the guts to pull the trigger?The decision's yours to make.But once I'm dead, you'll never find Room 707.Barbara, Kayla, everything you're looking foris all in that room, isn't it?
```

### [30] hash=`efd2dd41e1f9c405`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p16`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（16苦目糖）

```text
Don't you dare say her name with that filthy mouth!But why?Miss Kayla's such a lovely guest.I very much enjoyed her company.Enough.You and I need to have a serious talk.Oh, there's no need for that.Actually, my baby's eager to meet you.Your baby?Yes.In fact, the baby is the master of this motel.I think the two of you ought to meet each other first.Here, hold it.This is...No deal in this way.Not while I draw breath.

August!Don't you interrupt them.There's no need to worry, Miss Burton.I've done this countless times.Allow me to peer into your dreams.
```

### [31] hash=`8b312c7d6c7ecda5`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
Where am I?Is that rain?I can catch anything with a toss.Burton, that's why you gathered us here, right?You shouldn't be here.You understand what we desire most, right, Burton?Burton, we made it, right?Don't be such a baby, Isabella.Haven't you seen rain before?No!Were you afraid of children?But it can't stop us anymore, because the umbrella's here.At least now, when the storm comes, I can hold up the umbrella and protect my companions.
```

### [32] hash=`687029126ee7c87b`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
And although this ability has come too late for some, we still have a future to protect.Why are you so obsessed with people's fears?Your hands have been trembling with excitement this whole time.So I wasn't wrong at all.Why waste your time with that mercenary?She may look tough, but she's hollow inside.Have you ever eaten a macadamia nut?Crack the hard shell, and you'll find the delicious center who could resist the soft
```

### [33] hash=`045e20efb47cc69c`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
texture and rich flavor of fear.Miss Tuesday, this has to end.You were the one pulling the strings here, aren't you?Oh, what an astounding accusation.But oh, do I feel so, I've never felt so satiated in my entire life.You're the only one who's ever seen through me, how exhilarating.However, your accusation missed the mark.You see, my hands, they're immaculate.Never once tainted by a single drop of blood, I take great pride in it.
```

### [34] hash=`aba0de1f41a30eb4`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
You see, I barely do anything to make people's fears arise.I would never injure anyone.Fear created through physical harm is its crudest and most base form.What I crave is the fear that lingers in their hearts forever.The kind of fear that, even years later,when they recount their experiences here to their friends and families,Sorry, Miss Tuesday.But I'm not interested in this vile obsession of yours.
```

### [35] hash=`bf33282706992113`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
This is...Howdy, Argus.Long time no see.We thought you'd never come back.Mr.Dennis, why are you here?Oh boy, you listening to yourself?Why wouldn't I be here?It's my daughter's wedding day.Huh?Well, congratulations, but you really shouldn't be here, don't you remember?Three years ago, your daughter ran away from home.She left a letter and then went with Mr.Schaefer to a city in the northeast.Detroit, I think?
```

### [36] hash=`eaaf684365ca7b5f`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
I don't quite remember.Come on, quit fooling around.What is it?Did you lose some livestock, or...?Come to Alice's wedding.We've prepared plenty of food and beer, and we've got the chapel choir together.Don't miss out, missy.Sorry.I won't be there.Why?I need to deliver a letter to...to Mrs.Mary's husband.She can't go herself because of her bad legs, you see.Hey, August.I didn't ask you to deliver any letters.
```

### [37] hash=`556ed9bca00b4ebe`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
Oh my sweet child.Argus, Argus, got a message to send?Go get Argus, your trusted friend.Argus, got a cheap bus ticket?Go get Argus, she's got your back.Argus, Argus...Who's there?It's me, Kayla.You haven't forgotten me, have you?Kayla...It's getting dark.We should take them back.Ain't no way they'll make it through the night out here with their mama hurt.And you can't see a thing at night.Yeah, we need to go back now.
```

### [38] hash=`ddc037afe54980d5`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
Can't delay any longer.What?Hold on a moment.What are you doing?Isn't it better to die a quick death than end up in the belly of a wolf?You've got no right to make that decision.You hunt the targets of your missions.I'm sure you know that better than I do.Why should I kill them?Do you need a reason?Just do as we've always done.I say.And you do.No need to think about it.Isn't that what you pride yourself on?
```

### [39] hash=`2c7b282daf20654d`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
A mindless tool that blindly follows orders.That's all a mercenary needs to be.Isn't that the so-called value of a mercenarysupposed to be if you think I'm not Kayla then why don't you kill me now justshoot me in the chest and these people will treat you like a hero they'llgather in the fields holding torches and chant your nameArgus Argus she's spineless Argus Argus she'sThe deepest despairing external danger, our deceitful spirit of eternal delusion, we only have our own two legs to stand on.
```

