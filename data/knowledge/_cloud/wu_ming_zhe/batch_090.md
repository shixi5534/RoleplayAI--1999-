# 剧情图谱抽取 · batch 090

- 角色：`wu_ming_zhe`
- 批次：**90** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.3」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_090.jsonl`

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

### [0] hash=`fcf4672d36aa05aa`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p10`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（10明珠蒙尘）

```text
Willow, I think the water's been shut off.I opened it all the way, but nothing's coming outGo to the water resource office and ask the staff what's going on if they're not there.They're probably at the gin barrelI know you want me to leave but how are you going to track the time and score without me?With a heart that's pure and a body lean to the hunt I go through forests greenI have a whole sink of dishes that haven't been washed.
```

### [1] hash=`87c345406f80cca6`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p10`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（10明珠蒙尘）

```text
And here I am, fighting a little stain on a cauldron.And when the water's just shut off too.I did ask Buzzy to visit the water resource office.Hopefully it didn't slip her mind.If she even knows how to use it.Never mind.I can clean it off without water.Dammit, it's off.You stubborn little thing.Everyone loathes you.Everything will be alright.Just give up.Stop thinking about it.Stop hoping.Don't look back.
```

### [2] hash=`4cb4b78c8afe40a2`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p10`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（10明珠蒙尘）

```text
Just look at the cauldron.See how clean it is now?Stop clinging to places where you don't belong.The world is perfect.Without you.Latterbeige, is that you?I can hardly open my eyes in all this wind.Where are you?I'm right here.here.A letter of challenge?Liberty Grove on behalf of Charlotte O'Hagan herebychallenge Caroline Bartley to see who will become the champion of the floorritual in the Uluru Games.
```

### [3] hash=`82737b1874084ba1`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p10`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（10明珠蒙尘）

```text
No matter if you're a seeded player, a champion, or theson you say you are, Charlotte O'Hagan, the only floor ritualist to master thetwo-and-a-half turn with free leg backwards and upwards, one throw andWe'll defeat you and win first place in the London Qualifiers!What?You mean...
```

### [4] hash=`89ab1fbb6c44a3d0`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
Out of the way!I found the perfect component for Mr.Fogg's machine!This allows us to analyze the composition of the atmosphere.If the color of the filter paper meets that of the pollution stem,it will determine that the air is polluted and start working automatically.Let me show you.I found a blast stopper!It's the one you were looking for, right?Oh, you found it.Yes, that's exactly what I need.No need to worry folks.
```

### [5] hash=`b5e85d0b952bb23e`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
Believe me, there is no one who wants this purification machine to work more than I.So, I've been doing some experiments.Arthur!Lane!Here!Forgive me for not helping move it.I'm afraid I'm handless and horseless.I can't do a thing.What the bloody hell is that?Some kind of mechanical freak?Not to worry, Brimley.Now, folks, take a look at this.Thanks to your generous donations, my experiments on smog removal have finally come to fruition.
```

### [6] hash=`e859fb1c1eeab4a4`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
Introducing the London Air Pollution Autodetecting Purifier Mark II, a high-power, multifunctional air-cleaning machine.The current model can only operate for three hours at a time.But I'll continue to improve its performance before the qualifiers begin.It's estimated to last a whole day by then.Wonderful!Simply wonderful!No more smogs standing in our way!Goodness, I can't remember the last time I saw the sun and breathed fresh air.
```

### [7] hash=`3a8144f075f8b9ab`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
I feel as though I've been rotting!It's an honor to see that sweet smile of yours, doll.I think I'm inspired somehow.I've always felt like a bit of an outsider in London, but this festive atmosphere makesme feel a sense of belonging.I totally understand.Though I awakened in London, my true home is a land down under, thousands of milesfrom here.In some ways, I'm an immigrant.This sense of belonging is a treasure.
```

### [8] hash=`7302c0e6cc027ad9`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
The East London resident in my chest cried when I learned that the Uluru Qualifierswill be held here.Wait to see what would happen.That's your ninth sneeze since we got here.Don't blame me.I didn't even want to come.The Uluru Committee ignored my application to stay at the Australian headquarters.They couldn't find anyone willing to come to London with all this smog in the air.They didn't have much choice either, mate.
```

### [9] hash=`631459ac0e69208b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
The Foundation's been preparing for the qualifiers in London for ages.We'll suffer huge financial losses if it's cancelled.Someone has to make the trip to decide whether we should cut our losses or continue to throw money at it.You must have done something to be the lucky one who has to do the job.I do apologize.These little monsters are all over the streets these days.He sounds so calm.You'd think he was just talking about stray cats.
```

### [10] hash=`71e64afa53159663`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
You have to admire the stoicism of the Brits, especially in the face of all this.Honestly, this environment's totally unsuitable for any kind of outdoor activity.Hmm.Hey, what are you doing?Making note of the crash that almost happened?These records will be used to decide if the qualifiers should be cancelled.Someone has to be the doer since we already have a whiner on the team, eh?Look at all the decorations and posters.
```

### [11] hash=`29e3f6eba8eb1ed9`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
So much preparation for an event that won't even be held.I'm surprised they even want to hold the qualifiers, given the situation.Anyway, let's make it quick and get this job over with.Let me see...We need two things.Evidence that proves the environment isn't suitable for holding the qualifiersand the profiles of all the participating athletes.Then we can go home.Changes made to Cross Street.Let's see what the local community has done to prepare for the upcoming event.
```

### [12] hash=`fdee090f4f237a43`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
White and fluff!Yeah, so fresh.I've never felt anything like it.Hey, I can even see Keaton's store 50 yards from here.Hello!Keaton's waving back!The first week is for planning, the second for execution, and the last for delivery and paperwork.Looks like you've completed the tasks as Judge Want.Are you relieved?Miss Tooth Fairy, the sun is so golden and warm.Don't mind him.He's all over the place after working non-stop for the last few weeks.
```

### [13] hash=`78396f99d7bb73ab`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
He's just trying to say he's happy, that's all.What about you?How do you feel?Me?The ranger's soul inside me has always wanted to gallop beneath the blazing sun!Yahoo!A critter?No.Is that...the black fog?What's it doing here?It was a result of the increased density of regular smog in the air,but it seems I was wrong.Mr.Fog's machine has cleaned up the smog around us,but the black fog's still here and it's getting thicker.
```

### [14] hash=`8611b22c90cf0286`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p11`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（11叮叮当当！）

```text
How curious.At least now, without the smog covering its trail, I can sense its movements more clearly.I did hear that these little things tend to gather in the quiet alleys of Cross Street.Perhaps they like a visit from the Tooth Fairies.Slipped away at the first opportunity.I knew it.But what exactly was it?
```

### [15] hash=`1d7d8ccc072c880d`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p12`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（12老木头）

```text
Which would make the world a better place?Art?Or a heart of gold?Neither!The little mocker up of Flutterpage will.Miss Willow, she should be warming up by now.Where's she gone?Miss Willow?Miss Willow!Knock, knock!Don't jump to conclusions.Mr.Wind will tell you the truth.Knock, knock!I'll open all the windows and doors,and all the treasure chests too!Miss Willow?and that it took all her effort just to keep you in her sight, let alone catch up with you.
```

### [16] hash=`02baf665b8e1c635`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p12`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（12老木头）

```text
Because you're different, the one true master of the art.If there were only one gold medal in the history of the floor ritual,it'd be meant for you.Those were her exact words.I only chose to become a floor ritualist because I had a talent for it.I wanted to win, so I practiced and practiced, paying little attention to anything else.My family, my friends, my life, none of it mattered more than victory.
```

### [17] hash=`144c4d39bbf9ba0d`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p12`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（12老木头）

```text
To me, there was no reward more alluring than the euphoria of winning.But whenever I looked back at my past glories, I felt no happiness or excitement.Instead, I'd replay every moment in my mind.Every lost point, every imperfect movement, and think about how close I was to failure.So I pursued the next victory even more fervently.I thought, next time, I won't lose a single point.Next time I'll be was what was running through my mind when I was crowned champion
```

### [18] hash=`3c33f51ad48237cb`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p12`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（12老木头）

```text
of the Beltane.But there was no next time.Happy?I love being a knockerupper.Every morning, I get to see all kinds of sleep in positions.Some people cuddle, others curl up in a ball, and some ain't even in bed at all.I like watching them wake up too, like newborn kittens learning to crawl.And finally, when they completely open their eyes and stand on their feet, I feel a gustof fresh wind rushing out the window.
```

### [19] hash=`25f18f30f2c0362b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p12`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（12老木头）

```text
for his machine in a stadium.Why ain't you going there?It ain't happening.Pardon?I said it ain't happening.The ceremony.The foundation officers cancelled the qualifiers.Mr.Fogg's so-called biggest air purifier everdoesn't work.
```

### [20] hash=`6ebea87ee6ca0286`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
Blues enter in an orderly manner.Everyone, the ceremony will begin shortly.Freddy, can you see Mr.Fogg?I can't see a thing past all these people.You brought the telescope, didn't you, Dad?Maybe I can see if I look through it.Good idea.Take the telescope and get on my shoulders.Hold on tight, you hear?This crowd's rabid.All this pushing and shoving just to take a look at a machine.Then again, the most exciting thing we've had around here as of late is the rats fighting
```

### [21] hash=`abff30aeade5de84`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
in the underground.What's he doing?Blimey!He's smacking the machine.It's really strange looking.About half the height of Mr.Fog and connected to a very long tube and a massive funnel.They're inside the machine!There's a huge mechanical organ or something, like a lung!Oh sod it!Hold tight, Freddy!Dad's going to squeeze his way to the front!Alright, I can see them now.I don't recognize those two in uniform.
```

### [22] hash=`b6a589eeed39de1e`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
Are they the officers sent from the Foundation headquarters in Australia?That's what I heard.The Uluru committee sent them here to supervise the qualifiers and they'll report the results back to their headquarters, too.Ah, so it's down to them whether our athletes make it to the finals in Australia or not.I'm counting on them.Oh, please, Will.It's the players that you should count, not the judges.
```

### [23] hash=`bcaa0e6847018f7c`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
Well, I hope they like Caroline as much as I do.Look, Dad, Mr.Fogg's about to give a demonstration of his purifier to the officers.I heard that it can filter out the smog within ten yards of itself and it only takes onenight to process the waste.The qualifiers will only last two weeks so it should manage splendidly.It's working!Blimey!It's powerful!It's coping down the smog faster than a builder down to pint in the pub!
```

### [24] hash=`60cff4c3c8aa7c5e`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
I wonder how it works?It's a miracle that a mechanical lung of this size can purify so much air withoutletting out any waste.The smog's getting thinner.I can see more clearly now.Look, it's even purifying the smog all the way out there.I dare say the ivy on my balconywill be enjoying fresh air within the hour.Mr.Fogg's smiling, Dad.Ain't that great?It is.We ain't seen him smile for ages.Looks happy too.
```

### [25] hash=`dc40a618489856c5`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
Is he doing that Australian ranger dance again?Look at the expression on those Foundation officers' faces.They don't look happy or mad.Is something wrong?Whoa!What's going on?The machine's shaking like hell.What's that sound?Some kind of alarm?Ugh!Christ!Cover your ears, Freddy!That howlin' will make you deaf!What in the bloody hell is going on?Freddy, are you alright?I'm fine.what first the pipe blew open then it's glass belly shattered and the
```

### [26] hash=`1be7379f34098b63`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
mechanical lung rolled out from inside it's vomiting up black blood there's noway and and mr.fog what happened to him three and a half minutes I guessneither one of us won that bet it didn't even last half as long as IDon't be cruel, Gregory.We didn't come all this way just to laugh at these poor people.But they did do even worse than predicted.That's a fact, isn't it?And it proves thatthe London Climate Management Agency is nothing but a joke.
```

### [27] hash=`12b293d043dc4655`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
Listen, Gregory, I know you must be exhausted from the long journey and your constantsneezing, but you can't say that to their faces.Let's just do our job and givethem the news.What news?We have to tell them.Mr.Fogg?Mr.Fogg?Please move aside.I need to use the microphone.Oi!Miss!What are you-Ahem.Ladies and gentlemen, thank you all for coming to the ceremony today.We greatly appreciate your hospitality, and it heartens us to see you thriving despite the difficulties caused by the smog.
```

### [28] hash=`3db64edaedebbb1d`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
However, it is clear to us that the London Air Pollution Autodetecting Purifier Mark3 is not able to fulfil its duty.Barring an effective solution, the smog-shrouding London will do irreversible damage to boththe athletes and the general populace if they stay outdoors for too long.In light of this, and after much consideration, the Uluru International Committee has decidedto cancel the London Qualifiers for the Uluru Games.
```

### [29] hash=`6d8868dd3440ad62`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p13`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（13剪彩仪式）

```text
We will announce arrangements for the affected playersonce internal discussions are over.Thank you all for your hard work.You mean that the London Qualifiers have been cancelled?I'm afraid so.It wasn't there,but Mr.Brimley told me what happened in the stadium.Mr.Fogg has locked himself in his office.He's refusing to speak to anyone.It seems there's nothing we can do about it.Miss Willow, where are you going?
```

### [30] hash=`1d478bded90d9235`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p14`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（14一粒灰尘）

```text
The black fog seems terrifying.If I'd been there, I'd have buried myself in the garden or jumped in the sewer before it reached me.Thankfully all the patients and nurses were fine.Only Leonard's daughter got a few bruises.But what a shame it is that the building was ruined.It was 300 years old, you know.The stained glass alone was a masterwork.Its existence is unstable, its form changes daily.It doesn't appear to have any self-consciousness, but that critter in the alley was definitely
```

### [31] hash=`34929c2e3f8fe063`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p14`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（14一粒灰尘）

```text
intelligent.Huh, this thing.It looks like the illustration in the old book I read to me son.I can't quite remember the title, but it does mention a creature like this.A creature like this?Oi!Miss Tooth Fairy!It's an emergency, Darl!The little tack is in danger!Please, Mr.Hat, keep your voice down in the hospital.The patients need to rest.Sorry about that, but this can't wait.Miss Tooth Fairy, they said a girl's climbed at the top of the old bell tower, and she's planning to jump off.
```

### [32] hash=`6f3cc9baede39ea2`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p14`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（14一粒灰尘）

```text
A girl?You mean...Flutter Page!No normal girl could climb all the way up there!Oi, girl!Get down!It's dangerous up there!Don't worry, I'll be fine as long as the wind's blowin'.I'll ride it all the way to, um...Australia?Australia!They must be preparin' for the finals there.Come here, Miss Tooth Fairy.Have a seat.Come along, Liberty!Quickly!It's dangerous up there!Liberty!Oh, you!What's your word?
```

### [33] hash=`2b5312f28f28ac44`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p14`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（14一粒灰尘）

```text
She might jump right off the bloody thing!Why?Why what?I used to think the world was like the fish tank I had at home.No matter how many questions I had, the answers were all inside, just like the fish swimmingin there.I was patient, too.I'd take the fish one by one and carefully look them over.And I wouldn't stop until I checked every scale.Yep, every single one.Well, unless Mom and Dad scolded me.
```

### [34] hash=`871ae7f29b9959f8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p14`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（14一粒灰尘）

```text
Actually, sometimes I couldn't figure out why they hit me.I just had a lot of questions, and I wanted to know the answers.Anyway, now I've learned the truth about the world.It's different from what I imagined.I thought it was a round tank, but it was actually square.I thought there were goldfish swimming inside,but actually they were pinching crabs and chomping sharks.And you know what I realized?
```

### [35] hash=`6c1cfe247be2cb15`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p14`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（14一粒灰尘）

```text
People will change as long as the result benefits them.Once things are going well, whether expected or not, people often forget the goals theyset before they reach that point.What I'm trying to say is, we need to remember who we really are and what we really want.So I must have known what she really wanted.Otherwise, she wouldn't have become the youngest floor ritual record holder of thecentury.it won't hurt it's out I thought I didn't have any baby teeth left well you

don't anymore this was the last one yeah it stinks it does I suppose I'llkeep this then
```

### [36] hash=`5d16596358c87595`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
Let's listen again to the interview she had all those years ago.As the youngest floor ritual record holder of the century,you're just one step away from becoming the world champion.What else do you wish to achieve in your career?My ultimate goal is to win the finals of the Uluru Games,but I'll also register for as many events as possible.I have a lot I want to achieve, but I'm patientand I'm sure I can do it all eventually.
```

### [37] hash=`d0d9131d454324a5`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
Now, old friend, it's just you and me, isn't it?Ooh, careful with the scaffolding, fellas.You wouldn't want it to fall on your feet.You'll be hobbling about for months.Here's the reimbursement application form.Just fill in the numbers and give me the receipts for the materials.I'll contact the Uluru Committee for your compensation.Is there really no hope, Mr.Fogg?We didn't build all this just to tear it all down.
```

### [38] hash=`07e2e8c466df0df5`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
I'm sorry.To be honest, we'd rather not do this, even if we're getting paid for it.We were over the moon when we got this job.I mean, just look at this place.Huge billboards and that lovely stage background.How could we not be?It's been yonk since we last had an event like this.And who knows when we'll have another.The fact that you made something that worked at all, in just a matter of weeks, is an achievement
```

### [39] hash=`3ea18375e49cb323`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
in itself.I appreciate it, Ms.Tooth Fairy.I know it doesn't make any sense to keep it around after it failed so spectacularly,but I just...I can't bear to break it down.At least not for now.I enchanted it with my arcane skill, so we're linked together.As for the tuberculosis, I analyzed the black fog's composition and found some componentsvery similar to those in the patient's saliva.I've concluded that this fog critter is the root cause of the disease.
```

### [40] hash=`3917fe57d7393bc0`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
This critter is fog soluble, can change its form, and is indestructible.It feeds on smog and most interestingly, sensitive emotions, which it seems to absorbto nourish itself.In conclusion, the answer to our problems lies in capturing and containing these critters.Also, in one of my experiments, I cultured two samples under the same conditions and putone of them in the sun, like this.See, even in today's dim sunlight, it shrinks very quickly.
```

### [41] hash=`d3637466c91a64a1`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
Just wait a moment, and you'll see.It's true being.Sunlight is their weakness.That's why you never see them in areas with clear skies.As you can see, London provides the perfect conditions for it to survive and multiply,heavy smoke, and the anxiety and depression caused by the cancellation of the qualifiers.I do believe you're right, but it won't be easy to capture these things.No, definitely not.
```

### [42] hash=`38bca1e733ded8fb`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
I'm still trying to figure that one out.We may be able to lure them into a trap, but we need to make a specific plan so that the process is controllable and the results predictable.A specific plan?The only plan I can think of is to pray to God.Some people may seek answers from the divine, but whether that works or not is another matter.Oi!Hmm?Is that Flutterpage's voice?Sure is.Over there, mate.Outside the window.
```

### [43] hash=`88c379421cca3b2b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
Miss Tooth Fairy, Mr.Fogg, Mr.Brimley, would you like to join us?What?The residents of Cross Street have got together to petition for the reopening of the qualifiers.Hi folks, how about this iron?It's a family heirloom, but it will be perfect for the floating stockpile.And I'll be the stockpile.I'm an excellent timekeeper.I can keep time down to the millisecond.This could be the fair good, right?Then I'll put myself forward.
```

### [44] hash=`65ff6d20c0af2fb9`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p15`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（15触底反弹）

```text
Everyone on Cross Street knows I'm an excellent mediator.Everyone's brought things from their homes.Ladders, hanging rods, clotheslines.Anything that might be useful.We're going to rebuild the stadium together.So, will you join us?Are you serious?Scrooge, I don't know what to say.This is unbelievable.All fires have been cancelled.We'll just have to hold our own games.Ms Tooth Fairy, I've found the right way to look at the fish tank.
```

### [45] hash=`ae36df4e3306758f`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
So you're going to join them IYou know me I'll always jump rim first into the unknownBut the foundations already pulled their fundingThe workers are already awaiting their reimbursement and some players have already leftHow could we possibly hold it mate listen up those officers from the headquarters?Didn't give a damn whether the qualifiers were held or not you could see it all over their facesAll they wanted was to minimize their trouble.
```

### [46] hash=`3cd57575e05d9965`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
Did you see how quickly they applied for the cancellation and reimbursement?How hastily they made promises to pacify the people.I've never seen anyone more ready to get things over with.Their job was done as soon as they got the player list.They'd probably already moved their attention to the qualifiers in other regions.After all, our qualifiers are no different from the others to them.But it means something to us, doesn't it?
```

### [47] hash=`04616bcfdbb2dee1`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
At least for me, this could be my chance to go to Australia.My very nature wants me to run free on the red land,to haul around and forget all my troubles.I think that's what we all want.In the heat of competition, people are at their best, their most pure.Think about it, mate.You're not the only one who's put a lot of effort into this machine.It hurts me to see it rotting the office, too.If you're really going to give up because of a few words from an authority, then as
```

### [48] hash=`c1e918b2d506f23d`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
your partner, I have to tell you, don't ever let anyone deny your achievements, includingyourself.Alright, calm down old chap.Mr.Fogg, the people want the qualifiers because they're for everyone.They provide each and every person with an equal opportunity to shine, and thatincludes you and me although for us it'll be more like a battle to fight honestly will these peoplestop sending me petitions i've been absolutely inundated with them someone has to keep everyone
```

### [49] hash=`3f560d2678ebb24f`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
healthy i'll do everything i can to minimize the damage from the smog don't worry i'll talk tothe relief center to sort out all of the paperwork for the event here you are this isif you don't have one.Make sure you read it carefully.We don't want anyone hurtif there's an emergency.And here, take this special sheet I enchanted to protect youfrom the smog.I came up with the idea a couple days ago.It can drive away the
```

### [50] hash=`94be1d2ac6515c1d`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
smog around you by controlling the wind.Not very effective, but it's betterthan nothing.Blimey!You did all this yourself?Cheers, little knocker-upper, but you don't need to worry about us.We'vein the smog for generations.What can it hurt to own a little smog?Agreed.We asked for the exhibition ourselves, so we'll pay the price if anything happens.Here's the confirmation of your application.Your contingency plan has been approved by the
```

### [51] hash=`85008eab9a28cea9`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
Relief Centre.My colleagues and I will do everything we can to keep you all safe.As for the London Air Pollution Auto-Detecting Purifier Mark 3, I'll do my best to fix it.Next, we'll gather the athletes who have yet to leave the city and hold a small exhibition year.Of course, it won't be an official event, but at least it'll give an opportunity for the athletes to demonstrate their hard work to a group of spectators.
```

### [52] hash=`b9d1f63b4728ad50`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
I'm sure they'll be a great source of inspiration for the people of London as they cheer on their favourite athletes.Oi, Mr Fogg, I brought you this.It's Mrs Brown's leek and potato soup with bread and butter.Oh, Mrs.Brown, please give her my thanks.Has everyone eaten?Yeah, Mrs.Brown, Mrs.Jones, Ben's son and I have been cooking since four in the morning to get food out to everyone.But it still ain't enough.
```

### [53] hash=`66b7af2e721227a8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
Almost everyone in the neighborhood's coming.Alright, I have to go make more soup.See you later.Hey, what's that you got from the knocker upper?And it charted sheet apparently.She told me to blow it when I need to use it.Would you look at that?It conjured a gust of wind.We can use this while we're working.Yeah, it blows the smog away.Alright, well, sort of.Mr.Fogg!Mr.Fogg!I'm here to help!Oh, you.
```

### [54] hash=`e9638076841c0b6b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
You're the girl from the market, aren't you?Yes, that's me!Let's try our best to fix the machine together.But there's no need to worry.Mr.Fogg, we can still hold the exhibition even if we can't do it.The exhibition?All right.Introducing the London Uluru Exhibition Games.28 players have registered for the six-day event, which will host one sport per day.All right!Everyone, let's push together!Three!
```

### [55] hash=`ead7573cc515c3b2`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
Two!One!The residents of Cross Street have taken it upon themselves to rebuild the stadium.Hey, your painting's totally off-theme.Look, mine's a marking bird with a gold medal.It just won first place in the singing competition.The Unuru Games ain't got a singing competition.You should have drawn something more athletic.Like my sailfish.It's the fastest swimmer in the world.How exciting!Our very own Uru Games, without any interference from the...
```

### [56] hash=`949664246a495e82`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
It's too fairy.I've made a list of all the athletes who signed up for the qualifiers.A lot of them have left, but some would like to stay for our exhibition.Good.And I've made a list of the daily attendees based on the tickets they bought for the qualifiers.Mr.Fogg and Mr.Brimley are discussing the possible security issues of the event withthe Relief Center staff and the police.We may actually start the games on the day the qualifiers were originally scheduled,
```

### [57] hash=`c4a02b5a7c2a09a0`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
but since this is all improvised, we'll probably encounter some unexpected problemsas the games continue.We need to be prepared.Yeah, I know!Thank you, Flutterpage.all right you've got yourself a new outfit it looks great on you oh I likeyour coat too thank you my grandmother had one just like it she died two yearsago had a proper sweet tooth too we'd have got along well how did you know Iwas here oh I didn't until my tooth fairies found you so you have a whole
```

### [58] hash=`6186bcd2c839dbdc`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p16`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（16我们的乌卢鲁）

```text
It's totally amateur, but it's built on enthusiasm and sportsmanship.Athletes will go head-to-head, spectators will cheer,and the stadium will be lit up by the energy they release together.It's imperfect, yes, but it's inclusive and unstoppable.And that's what makes it special.
```

### [59] hash=`9260688375a47fac`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
Leave it to me, darl.Testing, testing.Ladies and gentlemen, your attention, please.Today marks the beginning of the London Uluru exhibition games.As you can see, the weather isn't looking great.The smoke still sits heavy in the sky.There's no wind, no sunshine, no warmth, and even my brim is soggy from the damp.It's truly miserable out here.On top of that, the stadium's shabby and we only have a limited number of athletes.
```

### [60] hash=`4547d9c7eac48f65`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
To many, these games would be seen as disappointing.However, even without the support of the Foundation, we've managed to rebuild this stadiumwith nothing but our own hands and determination.I've confirmed that our stadium meets all the standards required by the governmentand there's no doubt that it matches the Foundation's too.As for the operation of our games, we've built a reliable team consisting of various Uluru professionals and supporters.
```

### [61] hash=`5c4faf342bcaed49`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
They are currently in every corner of the stadium, working their hardest to prepare for the upcoming event.They will be our backbone, supporting the entire games to ensure that everything runs smoothly.As we all come together, I believe the passion of our games will burn as hot as the sacred fire of Uluru itself.So, without further ado, I hereby declare that the London Uluru Exhibition Games havebegun!
```

### [62] hash=`26a565d9fae5dd69`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
Ms Toothbury, we don't have enough judges for the winged key archery, but Franz hasbeen put on to umpire two events at the same time, so he left to do the other one.Two events at the same time?The other event starts tomorrow.He must have mixed up the schedule.Get him to come back.All athletes participating in the 1500 meter weighted run, please report to the third preparation area.I repeat, please report to the third preparation area.
```

### [63] hash=`a287e637fa021ff4`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
Um, excuse me.I lost my nametag.Can I get a new one?Certainly.Go straight ahead and take the first left to get to the player office.There's a girl called Flutterpage in there.Show her your ID and she'll give you a new tag.I'll take you there.Follow me, friend.sure thanks boy hold on a minute friend why haven't I seen you before this ideais fake security I'm just a big fan please don't kick me out I just too
```

### [64] hash=`6461024a20099503`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
furry my doll what is it head of security I've been told that a maid of ourswould like to post some flyers in the stadium we already have a sponsor I'mI'm afraid you'll have to turn him down.By mate, I mean Arthur.Has he been sitting all this timeunder that banner with his machine?Yeah, he's using it to show everyone what can happenif they breathe in too much smog.I don't know if I should call him wavering
```

### [65] hash=`d526e6e322359102`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
in his principles or completely stubborn in them.Arthur's always been a righteous official.He truly cares about the people.He's tough, tenacious,and has a powerful ability to influence others.Just as you said.Floor Ritual competitors, please report to the 5th Preparation Area.I repeat, please report to the 5th Preparation Area.Oh, that's Ms.O'Hagan's event.Yeah.Do you think she'll show up?I'm sorry, Mr.
```

### [66] hash=`98a5440335319150`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
Brimley.Did you hear that?The Floor Ritual's about to start.But where's Ms.Willow?Go check the Floor Ritual venue, Flutterpage.What for?Is Ms.Willow there?Isn't she?competitor number two four oh one please enter the floor competitors two four ohtwo and two four oh three please wait in the locker room good luck what aboutCharlotte Charlotte you're here and me you wouldn't be able to stay away theyhaven't changed a bit what do you want from me what do I want have you
```

### [67] hash=`1f474aa3adeb2a05`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p17`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（17开幕式）

```text
to know stop trying to bond with me but you are the charlotte i used to knowyou're still that black swan i've always chased afterwhen i saw your performance the grace the beauty of itit inspired me to become a floor ritualistbut you just disappeared after you became championwell as long as you're back what's so funnySee you on the floor.Player number 2406, Caroline Bartley, please enter the floor.

Time for me to head in too.Excuse me.Player number 2405, Caroline Bartley, whenever you're ready.
```

### [68] hash=`ce2c75f4a3d0d0de`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p18`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（18灰黄的对话）

```text
What's this miss Raven a seed that will settle in your heart and soon grow to be yourclosest friendIts roots will stretch all the way from Australia to the soles of your feet and togetherYou will make the music to your floor ritualNow my dearListen closelyListen to what it has to sayListen, let it know who you are.It isn't just a piece of wood, but a mouthpiecepassed down through the ages.It allows us to understand what our God hears
```

### [69] hash=`0dcc80747c114b2f`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p18`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（18灰黄的对话）

```text
during the ritual.It doesn't look all that special to me.Ha ha silly girl, if youyes speak to it politely and it'll respond with politeness the path ofpilgrimage is full of thorns it offers no shortcuts you must make your way inchby inch otherwise you'll never reach the sanctuary of glory the place whereAll the lights gather, and you'll dry a nobody.Will I be free clean if I keep training?Shush.Press your head against your shin, just as the divine sun did.
```

### [70] hash=`2acab0ee277f0cba`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p18`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（18灰黄的对话）

```text
Closer.I want that head tight against your shin.Tighter the better.Yes.Confusion, sadness.I can see it all over you.Yes, only the most faithful.You must offer everything you have to him.Your heart, your flesh, from here to here.If you can't do that, you'll be surpassedand never win the attention of our God.If that happens, you'll be completely forgotten,like you never existed.Is that what you want?
```

### [71] hash=`3ae049aab330cd8c`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p18`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（18灰黄的对话）

```text
She had it down to the smallest detail.In that way, we were like, sticklers for detail.That's why.Thank you.Thank you, everyone.I'm feeling so restless.Player number 2407, Anna Smith.Please enter the field.What did you think, Charlotte?Well, you certainly haven't skimped on your training these past years.That's it?You're better than when you were nine.I'll give you that.But are you sure you saw my performance clearly?
```

### [72] hash=`c7f340a01b67db14`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p18`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（18灰黄的对话）

```text
His smog's rather heavy.Flutter page.Ms.Tooth Fairy!Mr.Brimley!Good timing!Just in time, eh?Well, we wouldn't want to miss Ms.Willow's performance now, would we?The lady doing her routine right now is called Anna.It should be Ms.Willow next, but I can hardly see a thing.True.The smog's too heavy.Hopefully, it'll clear before Miss Willow comes out.What's wrong?Woah, she's stuck!I think she's requesting a time-out.
```

### [73] hash=`3c1edb4dec9a46ae`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p18`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（18灰黄的对话）

```text
A time-out?Is she her?Silence, please!An announcement from the floor of Ritual Judges.Due to force majeure, player number 2407, Anna Smith, requested suspension after discussion.The judges have decided to suspend the game.Suspended?Willow, will she not get to compete?Suspended?We gave everything to hold these games.How could she just back out like this?I heard that a winged key archery player got injured.

Maybe that's why.What, so we're supposed to just leave?The games have hardly begun.Ms.Tooth Fairy, what should we do?Ms.Willa was next.It'll be such a shame if she can't play.
```

### [74] hash=`2f0b166d5e0d55a6`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p19`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（19雾中独舞）

```text
Did you hear that?The games have been suspended.Yes.I suppose we should head home and wait for the notice.Maybe the games will continue once the smog clears.What?Go home and spit in the faces of everyone who worked so hard to make this happen?No.What do you mean, no?I won't wait any longer.Charlotte.Damn this bloody smog.Life's end is death, but bones to life ascend.Luch, before me, from underworld I wend.
```

### [75] hash=`db2c816c963a67d6`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p19`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（19雾中独舞）

```text
Luch, gaze on me, I rise from shadows dark.Luch, heed me, your power impart, as you are me and I your counterpart.The smoke is clearing!Everyone, come back!The games are on again!There's something there.Fear in the smoke!Activated.Looks like it's in pain.Like an earthworm squirming in writhing before it dies.It certainly had a violent reaction to Ms.Willow.Could it be that her ritual holds some power that suppresses the black fog?
```

### [76] hash=`132f810a002b2219`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p19`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（19雾中独舞）

```text
Told you that Ms.Willow was the best witch of them all!This is no time for chit chat.We need to stop the damn thing.Otherwise it'll destroy this place, just like it did the hospital.Arthur, get the crowd out of here!Damage.Who won?It's generating a new body.It's a copy of my bow, ain't it?I don't think so, little tacker.They're just heads of coal.Don't give up, Willow!Why are there still civilians here?
```

### [77] hash=`565e04472c5e90ab`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p19`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（19雾中独舞）

```text
They want to help.Come on, everyone.Let's dance with Willow.Follow her lead.Flowers bear fruit, and beasts give off springs way.With eyes of fire, get through the Cloudy Maze!Paired it all.Alright, you filthy little thing.It's time you learnt a lesson.You are under arrest for the pollution of the sky,as well as 15 crimes in violation of the Public Health Act.Take a good look around,because before long, you'll be rotting behind bars.

It may be broken, but it's still an air purifier.That's all from me.Thank you for watching.
```

### [78] hash=`f7a6e223fbc4bc19`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
I'm ready to go.Please fasten your seatbelt, miss.We're setting off now.You ever been to London, miss?Yes, a long time ago.Long, eh?Five years?Ten years?Longer than that.Come on, fan.How long?You don't look a hundred years old.The hospital is two streets away.Oh, by the way,it's been arranged for you to meet Mr.Fogg first,The tube?You won't like it, miss.Not the kind of place for a decent young lady.
```

### [79] hash=`2127dbcca1e57fac`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
I'll wait here for you, love.I'll do my best not to crack into my flask of whiskey while I wait.Thank you.I'll be back soon.How are things at SPTM, Tooth Fairy?I'm hearing rave reviews about their school physician.I'm glad to hear it.Young children are particularly easy to soothe.a few candies and they behave just fine.A little toffee or a nibble of a fruity sweetand they've forgotten all about the tooth fairy's taste.
```

### [80] hash=`28fc1fec9b781575`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
A proper dose of sweets serves to calm the nervous system and that doesn't just apply tokids.Your work here is undoubtedly busier than mine at SPDM.Besides, you're directlyI'm responsible for our timekeeper, the little troublemaker.But I am sure you didn't summon me here all for a little chit-chat.The Foundation has now confirmed the correlation between social turmoil and the emergenceof the storm.
```

### [81] hash=`b3df9ed5acbf2b56`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
Our branches around the world are now making efforts to collect information on these keysocial movements.As you may know, there was a strike that has only just ended in London.And there is something I'd like to show you, besides the strike itself.Tobacolosis.Indeed, there appears to be abnormalities concerning air pollution and the reported cases of TB.Compared to our records before the storm, TB morbidity rates are extraordinarily high,
```

### [82] hash=`3b2b0981f04f2fa1`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
approaching levels that shouldn't be seen until the Great Smog of 1952.Our Mr.Fogg, the Fogg Walker, has also reported that there is something unusual about the composition of the fog.So we need an insider with knowledge of the storm to visit London, ideally one with a medical background.I see.I know, your winter vacation just started.But I'm sure you understand the dire situation we find ourselves in.
```

### [83] hash=`4013fb227ef178f5`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
I'll apply for a special allowance for this field mission.What do you say?I'd be happy to go.Perhaps I'll collect some rare teeth from this era.Good luck then.Mr.Fogg will contact you when you arrive.He is our liaison between the Foundation and the British Government.He'll take you to the hospital,handling many of these respiratory patients.You will be given full trust to resolve this problem.There is something else.
```

### [84] hash=`56aab2051aa9b4dc`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
The Woolaroo Cool Fire will soon be held in London.He may factor into your investigation.Qualifier.Uluru landing qualifier coming soon.Alcanist Fair in Cross Street.Support your favorite competitors.Winners will represent Great Britain in the Australian finals.Australia?They shipped my uncle off to Australia back in the day.I always figured he got done in by a kangaroo.But if the smokey gets any worse, I think I might chance it.
```

### [85] hash=`bf2d9dba18701c44`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
I suspect Mr.Fogg will have known before we did.Let's follow the path of this dark soot on the street.Maybe we can find it, or its owner.As you like, Miss.Seems it's leading us to the East End.Only thing that comes out of the East End are drunks, tramps and Jack the Ripper.Miss, I swear to I, Evan, that I have not had a drop of drink today.This is the East End for you.either you it's someone or someone it's you please miss take a look for me tell
```

### [86] hash=`d5515e507df3a549`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
me if I hit anything I can take it it appears there's no one in front of thecar no one hmm look up there miss can you catch me huh she's being lifted upon the wind is this her arcane skill if so she's amazing for her age youMr.Driver run away like the suit to Kiki.He was worried for his car.If it got damaged, it could cost him his job.Lose his job?Oh, got it.I don't want to lose my job neither.He has a car, so I wager he makes more than six pence a week.
```

### [87] hash=`3d3481bba5c8756b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
How did he get that job?Can I do it too?I suppose you could.Once you grow up.Here, open your mouth.Hmm, it's a bit sour, like a moldy raspberry, but still sweet.Why aren't other pills as sweet as yours?I see, so you're a witch doctor, aren't ya?I can tell from your metal mask, teeth necklace, and the golden fairies in your jar.That is a reasonable assumption.You've even got the flyer with you!Actually, I'm here as a doctor to investigate a tuberculosis outbreak.
```

### [88] hash=`e3044b4ad7c7412b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p1`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（01伦敦第一日）

```text
But the strange black fog damaged the hospital I was heading to.I followed the trace it left behind to this area.Black fog?There ain't no black fog.Around here the smog is yellow.And sometimes I've seen black smoke puffing up from the factory chimneys.But never in Cross Street.I'd like to be an arcane skill, miss.Lots of us are canists here.That's why I roll chuffed up for the Uluru Qualifiers.There's harbalists, psychics, diviners, magicians...

Thank you, Flutterpage.I think I've got the idea.Then I'll show you around.You'll like it here.
```

### [89] hash=`98c351c6a19d8672`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
Come inMadam C.Here's the report from my mission.It seems you've been busy, tooEven though we've confirmed connection between societal turbulence and the stormThere is no time to catch a breathOnce chaos breaks, it will be the end of another eraBut we can't resist the inevitable.All we can do is maintain orderTo postpone it as long as possibleSo, any findings in London?A Vol Pergus's tooth from the Black Fog and the last baby tooth of a child.
```

### [90] hash=`f352c246440d58e0`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
Very rare, even for my collection.That's good to know.I heard the London branch is still trying to replicate the ritual that was carried out at the exhibition games.What was that?It was a coincidence, actually.After analyzing the live sample provided by Mr.Fogg, the London branch concluded thatthe Volpergus is a mutant of the Kaharai, a critter species that's been extinct forcenturies.Miss Willow lent one of her heirlooms to the London branch after the games, a book
```

### [91] hash=`d07c8e04d1c4e566`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
that details an ancient ritual meant to worship the god of the sun.This is the ritual she performed on the floor.But when Miss Willow performed the ritual again in front of the Volpergas, nothing happened.My guess is that, since the Kaharith disappeared, the ritual fell out of use and became fragmentedover the years.Her version of it is probably incomplete.The conditions must have happened to align at that moment to allow the ritual to
```

### [92] hash=`4745f554604e7672`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
work.It could have been any combination of things – Miss Willow's dancing, the musicthe didgeridoo wood, the fire from the torch, the magnetic fields around the stadium.Or perhapsit was all of them.The ritual also happened to have the power to capture the Volpergas,which put an end to the heavy smog in London.It makes sense, really, that a ritual used toworship the god of the sun would capture a monster that covers the sky and plunges everyone
```

### [93] hash=`88f1d4ee4a506d71`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
into darkness.In conclusion, the ritual's success was a near unrepeatable coincidence.An endangered critter and a long forgotten ritual.I guess that's why humans are always siftingthrough their past.There's always wisdom to be found in history.It's gone bitter.I should'vefinished it earlier.By the way, I've approved your vacation request.No one should disturb youshe won first place in the qualifiers.
```

### [94] hash=`525b4ef579ca0fa4`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
Charlotte, ever predictable.What are you doing here?We want to invite you to join us.Let's go to Australia together.With Caroline too?For your information, Charlotte, the top three athletes all qualify for the finals.And besides, I might have beaten you if you weren't so lucky as to capture that Volpergus.By the way, this ship we're taking is owned by the Bartley family.So Ms.Bartley said she'd arrange a presidential suite for us.
```

