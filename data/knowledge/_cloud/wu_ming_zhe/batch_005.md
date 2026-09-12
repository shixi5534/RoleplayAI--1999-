# 剧情图谱抽取 · batch 005

- 角色：`wu_ming_zhe`
- 批次：**5** / 共 1 批（每批 100 块）｜本批块数：**93**
- 筛选：标题含「77号往事」｜offset 200
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_005.jsonl`

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

### [0] hash=`3c6bdccdc1469182`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
Argus!A great hero!Heals of your heroic deeds will be passed down through generations!She ain't Kayla.Now now, you're lying to yourself again.Of course she's Kayla.It's not possible.Do I need to show you the bullet through her heart for you to believe it, Bonehead?Damn it!She's gonna kill us all!Mary, come on!Let's show these good-for-nothing mercenary not to mess with us!Don't pull the trigger!Virgin?
```

### [1] hash=`bb60b1c6197cae40`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p17`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（17小水洼）

```text
Calm down, Argus.Remember, what you see isn't real.You're still inside the motel.At least for now.Oh!Here comes another little lady.Excellent timing!Come join the party!Burden.I'm here to get you out.That wasn't Kayla.Couldn't ask for better news than that really.No, it wasn't.Let's get out of here.Okay.She ain't Kayla.
```

### [2] hash=`b1f5aabd78d7e923`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
Did you see it?It?My baby, of course.Oh, so it didn'tshow up then?What a shy little pumpkin.What is it, exactly?A supernatural being.An amalgam ofurban legends.An ever pounding heartand a shy little baby.All under one roof.But seeing how you gotof there in one piece.I'm certain you've already earned its approval.Come on in.I'll show youthe sweetest little room in the motel.Be afraid, sweetheart.Go ahead.
```

### [3] hash=`df80c39708d644ec`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
Reyes haven't recovered yet,have they?Such poor aim.Let me lend you a hand.Listen to mama.I told you long agothe consequences of disobedience oh it's out of bullets could you help me reloadmy sweet child can you see this is the beauty of fear watch outplease come in my dear guest you'll find what you seek inside activated what thehell is this thing miss Furtin please follow my instructions I need to call
```

### [4] hash=`9c9ecdbc0abb6a37`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
My sweet baby, all the monkeys in the cages chose the mother covered in cloth.All children need to form attachments.It's a vital part of how they learn about the world.Now, go ahead and make contact using whatever method you see fit.Don't worry, I'll keep the situation under control.This is the only way it'll obey.You want me to touch it?How about I let my bullets do the job?Agony is indeed a form of attachment.
```

### [5] hash=`77bc5fc205668014`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
You'll make a good mother, Miss Argus.You make me sick.Apologies, my baby, in your warm embrace.Put it out of its agony and inflict intoxicating pain upon it.Which is precisely why I became its mother.If you hadn't explained this earlier, I might have mistaken this for some kind of monster training show.Baby, you deserve a reward.It fell asleep.You may proceed now.Still called sweet home.It was all alone.
```

### [6] hash=`52c5a8897902e0db`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
Abandoned in wilderness.A poor little thing.So you took it in.Some unknown, growing arcane consciousness that takes the form of a motel.Yet somehow also exists as a baby.Yes.But it seriously impacted the lives of the locals.They chose to come here of their own volition.Argus, I need you to keep Tuesday in check until we make it out of here.You ain't gotta tell me twice.I've gazed at this scenery countless times, but never have I felt as enthralled as today.
```

### [7] hash=`7e9df6c6ad421494`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
Miss Furtin, don't you think you've forgotten something?Forgotten what?That guest who came with you.Shortly after her arrival, she hurried off to that armament factory.She's such an impatient child.Luckily, she made her way back here.Her name's Lilia, right?What did you do to her?She's fine.She's sleeping soundly as we speak, with or without nightmares.Follow me.I'm sure she's eager to see you.This is the room.
```

### [8] hash=`e150d74daa15024b`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p18`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（18不眠夜）

```text
Open it.Vertin!There you are!Listen, those Manu scum have already warmed their way into the town.We can't go there.You look terrible.I couldn't sleep at all in that haunted room.Every time I closed my eyes, I saw all kinds of creepy stuff.Can you come down here, Captain?Talking like this hurts my neck.Okay.
```

### [9] hash=`a9c8b9695961e66c`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p19`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（19飘）

```text
What's going on?Are you okay, Capitan?I'm fine.I have good news and bad news.Don't bother with the order.Just lay it on me.The good news is, we've found Barbara.The bad news is we've got a new problem.This motel is the manifestation of a living consciousnessthat constantly generates urban legends and spreads fear.It might turn into a supernatural arcane list in the future.We can't let it grow here unchecked.
```

### [10] hash=`4b854c6896049fcc`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p19`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（19飘）

```text
We need the help of the Foundation to keep it under control.Boss, my job here is done.I'm heading into town for Kayla.Oh, and I promised a young fella that I'd help him find his mother.I've gotta go now.How do I pay your fee?Fee?We're friends, Verdon.I don't need no payment.Alright, Kapitan.Any progress on finding Erd?That's why you came looking for me, right?I'll ask the wind for you.It's the least I can do.
```

### [11] hash=`34158afae9793a51`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p19`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（19飘）

```text
Did she doze off?Listening...Oh, I heard it!The answer!A distant wind told me that Ms.Erd's latest submission came from the Sao Paulo Veterans Residence.The article she submitted was an excellent piece, but Autu doesn't know anything beyond that.Okay.I suppose we'll all have restful sleep and sweet dreams tonight.I've collected the material I needed for the upcoming feature interview.I bet the readers will enjoy it.
```

### [12] hash=`af1f0463b01b46a9`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p19`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（19飘）

```text
I'll be sure to include your name on the byline, Ms.Tuesday.Me?I don't think I contributed anything.Quite the contrary.You played a significant role.If it weren't for you, I wouldn't have realized my inner fear of losing communication with the world.They have to investigate this supernatural being as soon as possible.And I'll be here soon, I presume.I can feel their energy fluctuations of teleportation rituals.
```

### [13] hash=`4a3709dd712235f6`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p19`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（19飘）

```text
It must be them.Looks like you guessed wrong, Captain.I met her in town.Names Kayla.Kayla?Do you know someone called Argus?The name doesn't ring a bell.How strange.What kind of parent would name their child after a 100-eyed giant?You must have mistaken me for someone else.Hale is a common name, after all.Like Emma, Anna, or Catherine.More importantly, miss, you look...Although I've never met you before, you seem familiar.
```

### [14] hash=`d7b8b7a15dba23a9`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p19`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（19飘）

```text
I hope you have a wonderful day.Thank you.Are you a guest at this motel?What happened here?The St.Pavlov Foundation has taken over.Will you return my baby to me?It's too early to discuss that.Let's go, Lillia.We must report back to Madden Z about her.
```

### [15] hash=`594fe98ecc8ce86f`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
10.6 inches long signs of limping male 20 years old lightweight more sets of footprints hereare you sure this is where the materials for the revered one are there isn't even a single traceof human activity here let alone a market i guess the only possible explanation is we'rehere for these plants right of course not you idiot that's too bad i'm great at harvestingplants I'm a pro see check out these calluses although my mom would probably
```

### [16] hash=`2eed37f0024b46b2`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
disagree you have any idea what these materials look like it must be importantso we'd better handle them with care don't want to risk mistaken them forweeds you know I hope they're easy enough to find with my leg messed uplike this I can hardly handle any delicate work that's him the one witha limp sorry about this man at least you'll see your mom soon up there inlet's try that again a girl about five foot three chestnut hair emerald green
```

### [17] hash=`1e4cb96482203bb3`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
eyes speaks like a Texan have you seen her yes or no no then why is her hairclipped in your pocket I remember there's a girl five foot threechestnut hair she's always carrying a basket her name's Kayla too but hersave us all some time are you with the foundation the foundation yeah they hate the foundation yousee but you saved me i need some help my mom i never heard of no foundation and i don't give
```

### [18] hash=`6a7fa6036aa789e6`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
a you-know-what about what's going on between you and them got my own matters to deal withI'll leave him with youKeep the gun you figure the rest out yourselfNow where's this motel?Listen you saved my life.So I owe you one.I have to warn you that motelSave your breath.We're done hereWaitYou're a mercenary, right?I can tell by your gearI'm I'm worried about my mother.If you see her on the road, please give me a call
```

### [19] hash=`99349ebbdeb95829`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
Here's a photo of her.Got it.And here, my phone number.And listen, be careful.Something he wrote about that motel.Two sheep, three sheep.Is that a sheep?Hmm.Two sheep, three sheep.Funny how we hit the hay every night, just like kids hit the books every day.I'm Barbara.Nice to meet you.You're in my way, ma'am.I tried waving and shouting at the drivers, but none of them stopped for me.Thankfully, pacing around the road seems to have done the trick.
```

### [20] hash=`62baf9ed5517e83f`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
Listen, if you need a ride, here's my answer.Now.My driver left me here, probably because of that scraping sound on the car roof.That scared him half to death.Everything happens for a reason.Destiny's brought me to the right place, I think.Could you give me a ride?I'm on a business trip, so money is no object.It ain't about money.Oh, a disappointing answer.But I understand.One must be vigilant.If you don't mind me asking, miss, what happened to your eyes?
```

### [21] hash=`5c2434c2b6cf8ef6`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p1`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（01迷途的脚印）

```text
They're bloodshot.It's best not to drive with your eyes in such a state.You have a much higher chance of getting into an accident.That ain't none of your concern, Miss Sheep.See ya.This little lamb almost didn't make it out of her mama's belly.That's life.Don't say that.No living thing is born to suffer.Look, it's already standing.What an adorable little thing.It's getting dark.We should take them back.

Ain't no way they'll make it through the night out here with their mama hurt.And you can't see a thing at night.You're right.Let's go.Screw it.I should have minded my own damn business.
```

### [22] hash=`0cc6d03f3279e7c3`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p20`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（20往日不再）

```text
Oh dear, it seems a lot transpired while I was away.Kimberly, care to tell me what happened in this motel?There's blood and brains splattered in the hallway.Who died and how?To destroy the ritual sigils under his head, and I couldn't find them.Now that our base of operations has been exposed,we'll have to take away everything related to the ritual and leave.The Foundation's rats will thoroughly search this place soon.
```

### [23] hash=`eb916cdae04b22cd`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p20`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（20往日不再）

```text
The thing I need right now is more about this Toe and she confronted me earlier.Good as her memory.Fret not, Kimberly.People rarely pay attention to things that don't directly involve them.But I do look forward to seeing her again.We're just here to have a conversation, Ms.Tuesday.Relax.I found it in the wilderness.You mean the motel with arcane powers?Just to confirm, the base form of this arcane consciousness is a heart-shaped fetus, correct?
```

### [24] hash=`58dfbfbdb6bbc9b4`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p20`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（20往日不再）

```text
Yes.It's about as intelligent as a one-year-old human, and it lacks the ability to deliberately plan or cause the incidents in the motel.Meanwhile, it sees you as its mother, displaying remarkable trust and dependence on you.Therefore, we believe, you were a major contributor to these incidents, or rather, the one whopulled the strings.You may not have acted with evil intent, but your actions have caused many residents in
```

### [25] hash=`1aa70d7b14818d85`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p20`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（20往日不再）

```text
Chisos to suffer mental breakdowns.They were seeking some form of relief from their mental anguish, which provided theperfect opportunity for the Manus to entrench themselves so deeply in this town.Isn't that so, Ms.Tuesday?Well, I've never been to that town.And even if it is, as you say, they made their choices, didn't they?I see.The Timekeeper just reported another crucial piece of information to the Foundation.
```

### [26] hash=`e9406a8531a2332d`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p20`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（20往日不再）

```text
Were there any activities going on in the motel undertaken by the self-proclaimed followersof the Order of Enlightenment?There indeed were.They left not long ago.We didn't find anyone trapped in a mirror during our search?Well...If you knew they were from a dangerous Arcanist organization, why didn't you report them to the Foundation?Fear doesn't frighten me.No, at the contrary, it excites me.I would embrace fear any day of the week.
```

### [27] hash=`abf7a0c61b4318d2`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
Before we left, TTT was telling me an urban myth about Texas.Sounds about right.What's the story about?The story starts off in the typical way.A man was driving down a long Texas road when he saw a girl hitchhiking.He offered her a lift and a piece of chocolate.The man dropped the girl off at a cemetery and drove on.It was late at night, so he was hoping to reach his destination quickly.Soon after, he saw a funeral procession going down the road.
```

### [28] hash=`992914221af3bc42`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
Both of the dead seemed familiar.Curiosity came over him, and he followed them to the cemetery.Lo, a piece of chocolate!Give me a moment.I have to take this.It's from the Foundation.Timekeeper, this is an emergency notice.The Zeno base in Texas, USA has conducted a large-scale evacuation.Zeno has not yet responded regarding their actions.Should you encounter any difficulties on your trip there, please contact headquarters immediately.
```

### [29] hash=`b43a2b0c301f95e5`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
Understood.Despite these developments, your mission remains the same.Contact A2 Editor Barbara, who was last seen near Route 77 collecting information.And find Erd's current whereabouts through her.Since A2 Editors use a special communication channel, her current location is still unknown.We'll be in touch as soon as there's any new information.Any questions, timekeeper?No.Thank you.All the best, then.
```

### [30] hash=`024fbaa802953e77`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
What did they say?There was a mass evacuation at the Xeno base in Texas.What's that all about?They called me two days ago saying that Red 38 was still under routine maintenancein their armament factory.But now?All of a sudden they're gone?How am I going to get my Red 38 back now, huh?If they hadn't taken her away for inspection, we wouldn't be travelling in this littlecar, wasting all day on the road.
```

### [31] hash=`0132b9beea3e7057`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
The operator only mentioned an evacuation, it's still possible that some of them havestayed behind to keep the factory running.If you're worried about Red 38, we can take a detour there, it's in Chisos,the town isn't far from here.Hey, mister, can you take us to the cheeses?It's just a little detour.Girls, I don't know why y'all are here, but whether it's just for a bit of adventure or for business,
```

### [32] hash=`8a9a3572b26886c4`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
I gotta tell you, something ain't right in that town.We've all heard the stories.Scratching sounds on car roofs, animal bits stuck to car grills,and those people in black robes running around.It's all too weird for me.Give the ghost stories a rest.Look, if you're trying to negotiate a higher price,at least be a little smart about it,instead of trying to spook us with a few tall tales.You got me all wrong.
```

### [33] hash=`65129b12d62b33f9`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
Who in their right mind would throw away the cash in their handunless they were forced to?Benjamins are good and all, but they ain't worth my life.Ain't no way I'm taking you there,no matter how much cash you throw at me.Why?Were you the driver in that ghost story?no have you seen this things happen yourself come on it's just a littledetour it won't even cost you much fuel sir you see that it's fogging up ain't
```

### [34] hash=`c95dcd3fae5f5873`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
no way this fog is natural we shouldn't go any further I'm stopping right herefine I'll drive swap seats with me no nobody get out of the car why are youAre you kidding me?You haven't heard the stories, have you?Then what the hell are you even doing here?When the fog rolls in on Route 77, you should always stay in the car.All kinds of terrible things hide in the fog.Some folks say they saw giant white crocodiles.
```

### [35] hash=`40dbd5ed6a879ff2`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
Others say they saw dead bodies hanging from trees.Ain't nobody leaving this car.Not until the fog's gone.Is that...is that...Oh, come on!Don't tell me you're scared of this stuff.He's fainted.I see.This looks like the work of a mumus.It's a critter commonly seen in the southern U.S.When they're frightened, they produce a fog-like gas from their respiratory trumpet.So that sound is just some critter scratching along on the roof.
```

### [36] hash=`abc617d1c1dab4a7`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
At this rate, I won't get my Red 38 back for another month.Well, I've always wanted to try this.Help me move this guy, and you'll have to give up your passenger seat, Captain.I know what you're thinking, but do you have a US driver's license or any driver's licenseat all for that matter?What do I need that for?I can fly a broom and even do all those maneuvers.That takes more skill than driving a car, don't you think?
```

### [37] hash=`7f423c8a9004b340`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p2`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（02浓雾天）

```text
Compared to flying, driving a car is child's play.Just look at the number of drivers compared to pilots in the world.Now where do we start?Start both engines.Keep the tachometer at 70%.Here's the nose wheel steering, the position indicator for the joystick, the throttlelever, and these are for the flaps.No, no, that's not right.We're in a car, not a flying machine.Let's just get out, Capitán.Come rub my head around this hunk of metal.

Good decision.If these critters are responsible for this fog, our solution is simple.We drive them away.Let's go!
```

### [38] hash=`c24dded7482bf4f4`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p3`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（03婴儿电台）

```text
What is it, Kapitan?Someone's casting arcane skills nearby.Do you hear that?Sounds like a crying baby.Better go take a look.You know, a Texan soldieronce told me about a notorious banditback in his hometown many years ago.He would record the soundof a crying babyand play it outside the homes of single mothers.Then he'd wait,ready to attack themif any of them opened their door to look for the baby.
```

### [39] hash=`e0ceac98bc98e675`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p3`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（03婴儿电台）

```text
yes but the actions of one man don't negate all other calls for helpof course not it's just a reminder to be ready for anythingwe're close now prepare yourself got itvertsyn over here please are you alright miss finally someone pleasehelp me these critters won't let me leave every time I try they knock meDid you get a good look at them?Those slippery little things look like seals, don't they?They always jump on passing cars and rub their flat hind legs on the roof, making that
```

### [40] hash=`8adcf60732e6f29e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p3`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（03婴儿电台）

```text
coarse scraping sound.Amazing creatures, aren't they?These little fear-mongers.But they are, in fact, easily frightened.The slightest movement could startle them.That's why it's foggy all year round here.Many of my guests have trouble finding their way to the motel.Are you ladies looking to check in at the motel?Motel?Yes, Tuesday's Motel.If you're looking for a comfortable bed for the night, it's the place to go.
```

### [41] hash=`0bbcac9cedb8b410`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p3`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（03婴儿电台）

```text
Anyway, thank you so much for saving us.I owe you one.Excuse me, are you the maid at Tuesday's Motel?I almost forgot to introduce myself.Folks around here call me Tuesday.Hey, Tuesday.Over here.Hey, Tuesday.Breakfast for one, please.Tuesday.Ah, ain't we all like horses?And our names like the rains pullin' at us.Do you need a place to stay, ladies?Thank you for your kindness.But our driver's still in the car.
```

### [42] hash=`558d37f23c950ecc`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p3`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（03婴儿电台）

```text
We can't just leave him there.And our luggage and travel documents are still in the trunk.Don't worry, it ain't far.When night falls and the signs are lit, a weary traveler may find a comfortable place to rest here.Welcome to Tuesday's Motel, ladies.
```

### [43] hash=`ce744a8f425abc1b`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
That'll be $25 altogether.Will that be on card or cash?Cash please.Hey, do you know if there's an armament factory in the town nearby?Armament factory?Yes, there is one.Would you like a map?If you plan on visiting, make sure to return early.It can be a difficult walk in the dark.Doesn't seem far from here.Yes.How's business?Not too great.It's the off-season now.You don't seem too good at small talk.
```

### [44] hash=`b3200b9ce4beceb2`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
Is there anything you'd like to ask?I do have one question.Have you seen a sheep-headed Arcanist around?That's not a face you'd easily forget.And why are you looking for this Arcanist?Please.That makes this request simply too adorable to turn down.Well, I don't know.I'm sorry to say that I've never met an Arcanist with the head of a Sheep.I can help you ask around if you...Sounds like something's going wrong upstairs.
```

### [45] hash=`4c87d25a88d6dd5e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
Sorry about that.Let's head up.Your room's on the second floor too.Then we can take a look at what's happened.Sounds good.Just so you know, the guests upstairs are a little...You can stay behind me if you like.How about it?It's just a simple room swap.I'm sure it won't be no trouble at all for a generous lady such as yourself.That's the guest staying in room 210.She arrived here the night before yesterday.
```

### [46] hash=`67e8015d39403a87`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
She was injured when she came in.Seems it didn't take her long to recover.I don't quite understand why she insists on swapping rooms with the other guests.If she does the same to you, please call the front desk.I'll do my best to help.Why didn't you offer her your help?She needs it more than I do.Oh, things don't work like that here, miss.Everyone has their own secrets.With the variety of guests we get, it's best to keep your mouth shut.
```

### [47] hash=`4a5b17ff6e18b322`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
Or else somebody will shut it for you.Although there are fewer bounty hunters around these days.My advice is to stay quiet if you don't want any trouble.Especially if you're dealing with an armed mercenary.The mirror...Mr.Stefan, are you coming out for some fresh air?Maid, you're just in time.I'd like to swap rooms with this Kimberly lady.If Ms.Kimberly and yourself have come to an agreement, then I see no reason why you can't do so.
```

### [48] hash=`3c03a8f0fb801c7d`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
Uh...Timekeeper?Have we met?Vertan...That's me.Do I know you saw?I'm ever so sorry about all this, Ms.Furtin.You've only just arrived, and you've had to deal with so much trouble already.Oh, it's no trouble.In fact, I'm glad that we came here.That man said he'd seen a sheep-headed monster.Oh, that.He's quite delusional.Surely you won't take the ramblings of a madman for a fact, will you?He's been peculiar since the day he checked in.
```

### [49] hash=`56efef36b1243f88`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
He spasms and twitches, and pays little attention to his surroundings.It's best not to have a face-to-face conversation with him.Who knows what he'll do next?Hey you, maid!Enough chatter.You have a job to do.I accepted the offer this, uh, Miss Argus made.What's next?What should we do?Apologies, Miss Kimberly.I'll be with you in a moment.Could the both of you wait for me at the front desk?The rooms need to tidy up before they can be occupied.
```

### [50] hash=`aa6f7b9b99eb5eca`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p4`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（04红勋章.）

```text
You may take a rest on the couch in the lobby while you wait.Miss Burton, I'm afraid I'll have to leave you here.Do you mind going to your room alone?Not at all.You can just leave the room as it is.If you clean it, it'll interfere with my work.You might want to check on that Kimberly lady.But it ain't wise to mess with the girl packing heat down here in Texas.Later, Miss Kimberly.Hurricane skill.
```

### [51] hash=`f778f530f059d3b7`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
he clearly knows something but he appears to be rather mentally unstable and he'shostile towards me Adam Z cautioned me on this I must be extra careful whendealing with people like him should make sure I have a backup plan in placebefore proceeding still no sign of Lillia yet in trouble hello is thatmiss Tuesday I think I know what this is that's an R E P respond missThank you.I'll ask my friend what she thinks when she comes back.
```

### [52] hash=`fa9f770b315d9078`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
And the kitchen closes at nine.Please take note of that.Can help you with?I'm good for now.Thank you.Spiders?Is that an arcane array?Patterns familiar.I've seen it somewhere before.Yes, I've definitely seen this before.When I was in school.Burton, are you listening?The instructor just said it'd be in the next exam.If you like, you can check my notes.Oh, thank you.My mind was somewhere else.Why have they made it a key point of the exam if we can't even use it?
```

### [53] hash=`8400a8bada36ac04`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
I see.They didn't teach us about arrays so that we could use them.They wanted us to be able to identify them so that we could avoid danger.It's highly likely to cause an explosion or other severe consequences if I act too hastilyLillia still hasn't come back.I must find someone else to help.Hey, we met back in the hallway.Remember?Now it's your turnWhat exactly do you want from me miss?Well, it's simple.
```

### [54] hash=`adf77abcd19bb3ac`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
The person I'm looking for is right here in this motelAnd I'm scouring every corner of it to find herLook missy.I don't want to make things hard for youName your price, and we can talk.If this person's gone to such great lengths to avoid you, perhaps she doesn't want to see you at all.Well, that ain't my concern, is it?A job's a job.Whether it's catching a cheating spouse, tracking someone down, or delivering a letter, it don't make no difference to me.
```

### [55] hash=`e28d23943ba9b927`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
Very well.But you'll have to look elsewhere, I'm afraid.There's no one but me in this room.Huh.Look, I know what I'm doing.How about you turn around and take a good look around the room?So you can knock me out as soon as I turn my back to you?Missy, if that were my plan, I wouldn't have spent all this time talking to you.I much prefer to do my business pleasantly.I don't like to see things get too ugly.
```

### [56] hash=`21dfa678fdad6a8d`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
I see.Fine.If you don't want to turn around, I'll tell you what I see.You've burned your finger there.You should be more careful.This is...Don't look like a fire burn to me.What was it?Some arcane energy?Looks like this room has a couple secrets too.So you touched an arcane array, and its power burned you.How's that for a guess?Pretty close, huh?Before I let you investigate the room, I have one more question.
```

### [57] hash=`d2713db321a23167`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p5`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（05临时通讯.）

```text
You take jobs from people nearby, don't you?Of course.It's obvious, ain't it?You seem more intrigued by my profession than my peculiar request.You're in trouble, ain't ya?Then let me formally introduce myself.The name's Argus.I'm 26, and I have extensive experience as a mercenary.Let's make a deal.
```

### [58] hash=`0a9ad88e5ea23a86`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
I'm Caleb, by the way.I heard some rattling here and thought some of those kids might have come back to steal weapons again.These things aren't cheap, and the kids know it.Kids stealing from the military?Huh, that's a new one.Where are the guards here?Oh, didn't they tell you, Lieutenant?The army stationed here started evacuating a month ago.There aren't many of them around these days.Evacuating?Then where can I find the soldiers that are still here?
```

### [59] hash=`90ca0eed2ed86ea5`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
You're new in town, right?Did you see a bar on your way here?That's where the Xeno soldiers spend their nights drinking.You might want to check there first.That's probably where you'll find him.Him?What does he look like?Like every other Xeno soldier.They all look the same to me.You'll know him when you see him.But I have to tell you, the bar doesn't like outsiders.Have you heard of the Order of Enlightenment?
```

### [60] hash=`3b3e2d98fc0d8f79`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
It's an occult society.Very active these days.They were preaching in this town just a few days ago.Today is their day of prayer.And what does that have to do with me?The bar you're going to is where they gather to pray.That's all I know.If you're going up there, please be careful.Huh, thanks.Sufferer, watch over you.Great sufferer, by your decree, the glory of former days shall grace our present path.
```

### [61] hash=`5427231f2f49e4a8`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
We dedicate our souls and minds to you.We seek the well-being of our people in your name.May the sufferer watch over you.Under their grace may our cups overflow.To the sufferer!You shut up!Time for a stranger to come.No crushing the party, am I?Napa Valley, Californian Red, Kentucky Whisky.Ha, there's a lot of good stuff here.one vodka straight the best you got it ain't business hours lady hey all I did
```

### [62] hash=`9c8c4da38f6b0980`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
was ask for a drink is this how you treat your customers as I said we ain'tserving you why don't you have vodka fine I can settle for whiskey have to learnto take what we can get hey you ain't getting that eitherSeriously?You don't have any whiskey?I'm starting to understand why Zeno evacuated.What's the point of living in a town where there's no real liquor?Especially for those drunkards.What's a Zeno lieutenant doing here anyway?
```

### [63] hash=`85eaae63040bc657`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
No alcohol fuel in that warehouse of yours?Huh.You sure have some interesting drinking habits down here.But I'm curious, why did this sufferer promise you to make you all change your face?I mean, that's quite an achievement, especially here in Texas.Oh, so we're doing this now?Are we?Look, I don't care what you're doing here, just tell me where that Xeno soldier went.What Xeno soldier?Don't play dumb with me.
```

### [64] hash=`982e08a1b11a1afb`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p6`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（06玻璃酒瓶）

```text
That soldier, he's a complete idiot, that one.It's obvious that Xeno has abandoned him, but he insists that they left him here becausethey believe that only he could keep the warehouse safe.Why are you looking for him now if you decided to ditch him in the first place?Listen, I can tell you guys aren't the biggest fans of Xeno, but that has nothingto do with me.I am just here to get my stuff back.

If you insist on finding him try your luck on the outskirts of town.You might be drinking thereThanks
```

### [65] hash=`8235736ad5d20b15`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p7`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（07羊皮纸）

```text
We can't say for sure if this ritual was created by the last guest.Fact is, you can find all kinds of unusual markings in this motel,most of them less than a month old.Very recent indeed.The maids said that there aren't many tourists these days,so my guess is that a group of skilled arcanists have left their work in every room.Based on the markings I've seen so far, there were about three to five people in this group.
```

### [66] hash=`593ae97b79140f7a`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p7`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（07羊皮纸）

```text
And was there a sheep-headed arcanist among them?Well that, I don't know.What I can say though, is that there was a sheep living in here.I saw some hoof prints on the hallway floor.It looked like someone had stayed in this motel with a sheep.Sounds pretty odd, but I suppose it ain't too strange given the local farmland.But I'm sure this will catch your attention.What?We all know that sheep walk on four hooves, but the hoof prints I saw were different.
```

### [67] hash=`6c98660a04e13176`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p7`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（07羊皮纸）

```text
They were small and delicate, and most importantly, followed the movement pattern of a human.Judging by the trail, the owner of the hoof prints was about the size of a slenderkid, maybe five feet tall.That's the one I'm looking for.Don't I know it?They can question my morals, but nobody can question my competence.So, may I enter your room now, Miss Verden?Please.Now, let's start with this little thing.
```

### [68] hash=`bc6b9a9b578762fe`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p7`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（07羊皮纸）

```text
The carvings are new.No sign of woodwormdamage or moisture absorption.These splinters along the edge are extremely sharp.Hmm?Is this...dried blood?I heal and help both the rich and the poor.Yet I am full of hurtful poison.What the hell does that mean?It's a quote from a text on alchemy.All challenges will be resolved with the provision of sufficient and high quality materialsand the precise execution of the array.
```

### [69] hash=`a50fb96cb5e9074e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p7`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（07羊皮纸）

```text
But where do we find these materials?What was once Sundered shall reunite.I've seen this handwriting before.And here, my phone number.Yep, this is definitely the same.That sound.It's a Flying Arrow M1903 pistol.Kimberly?What's wrong with her now?I better go check it out, boss.Something don't seem right.You coming?That Kimberly must have run into something.
```

### [70] hash=`8414484cbcaf7f10`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
Just when I thought you couldn't get any dumber.Is this a suicide without the gun and shot himself in the headHis brain splattered on the walls and blood onto the floorHmm.There's gunshot residue and powder burns near the woundGunpowder particles on his fingersThere's no doubt he died from a gunshot woundThe bullet was fired from the pistol in his right hand and went straight through his skullBut this ain't just any pistol.
```

### [71] hash=`2fe0ba2503bde3cf`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
It's a Xeno pistol.You've got yourself in some serious trouble, Missy.Just an it-sad, terrified girl who just happened to pass by.Well, Miss Innocent, Sad, and Terrified.If you want to prove your innocence, start by telling us what happened here.And mind you, I will call you out if you lie.The evidence here will tell me what's true and what ain't.If you're so clever, then why are you asking me?Figure it out yourself.
```

### [72] hash=`359f0d70ec474434`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
Right, I'll tell you.This madman has been harassing me.Ever since I moved into this place, I'd often seen him pacing around in the hallway.Day and night, he'd stomp around out here.He didn't care if anyone else was trying to sleep.I thought he must have had a lot on his mind, like he was troubled or something.so I asked him what happened deep sunken eyes were bloodshot every fiber of hisbeing screamed that something was wrong with him sir if you have any problems
```

### [73] hash=`c56e5150dd24568f`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
there are many ways to solve them but pacing in the hallway isn't one of themplus it disrupts everyone's sleep so I didn't say anything too harsh but hejust downright rude get the hell away get out of my face excuse me that'spretty rude you know we had no desire to argue with the madman thankfully themaid intervened when she heard what was going on I have no idea what she saidto him but eventually they came to terms he stopped pacing the hallway
```

### [74] hash=`9e9fdee4fca2615e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
from then on.That was a relief.I'm sure the other guests would agree.That maid canvouch for what I've said.Ask her yourselves.Not long after, I found a letter from Stefan on the floor of my room.It had been slidunder my door.In the letter, he apologized for his behavior.Should I make peace withNo.Is there an issue between Mr.Stefan and yourself?She seems hesitant to speak.I know it's not my place to ask, but the situation is a little concerning.
```

### [75] hash=`7d93945586f0740f`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
Mr.Stefan, I'm at your door.I just want to confirm everything's alright between you two.Calm down, miss.It's all over now.Do you still have that letter with you?Don't hold on to that.I threw it out right away.It'ssomewhere in that binDear Ms.KimberlyI've got a question alreadyHow did he know your name?You didn't know each other well enough to have exchanged them.Did you?I'm here.Damn it.You can't interrogate me like this, but if you must know
```

### [76] hash=`b60105e817986223`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
Maybe he heard it when my friend called meYour friend why that a young girl like myself should never travel alone to places like thisit's the one to make my bed and prepare my clothes andmost importantly, I need to eat IWouldn't even be here if I weren't looking for I want to apologize for my behavior earlier in the hallwayHmm looks like a perfectly normal letter to meNo hints that this is from a man on the verge of a mental breakdown
```

### [77] hash=`78ca0cd3c05e0b59`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
If you won't take my word for it, go ahead and ask the maid.She was there!She can vouch for me!Please, we weren't accusing you of anything.Though griffology has been criticized a lot these days, I gotta say, this looks more like a woman's handwriting to me.Stefan was a woman?You still with us, Missy?What I'm suggesting is that Mr.Stefan didn't write this letter, but a woman did.But that's just speculation.
```

### [78] hash=`94d271d7d81cd37a`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
Chances are Mr.Stefan's handwriting was just a little feminine.I'll keep this letter for now.Back to my questions.If the story you told is true, then why are you at the scene of his death?Did you go looking for him, even after all the weird things he'd done?Hungry?If I remember correctly, the motel offers room service.And you get one free meal a day, so even if you ain't got no money, you have enough food to get by.
```

### [79] hash=`a6e0052e9872f0c0`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
Eating one of those ham sandwiches!Alright, so you've got some standards when it comes to food.Let's drop that.You were there when he fired the shot, right?What happened then?Take your time and think it through.There's no rush.Fifteen minutes ago, he rang my doorbell.I thought my friend had returned from town.You came to me and made me drop my guard so that one day you could turn me in for a bounty.
```

### [80] hash=`7615fa1a9135c69c`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
But why me?Why are you doing this to me?It wasn't me who made the plan.It wasn't me who executed it.It wasn't me who pressed that damn button.All I did was expose their crime to the rest of the world.Tell me, why else would they want my head so desperately if they didn't believe they were guilty?But at least I get to decide when I step through that door, right?I had no idea what he was talking about, and he didn't give me much chance to figure it
```

### [81] hash=`46799a69e3eedf92`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
out either.I'm afraid your mission is doomed to fail, young lady.In that moment, a smile of relief came over his face, and without a moment's hesitation,He pressed the pistol against his temple, and pulled the trigger.You know the rest.What's going on in here?This man killed himself.Oh, dear.There's blood everywhere.It'll be a lot of work to clean it all up.And with the weather being so hot, the room will soon start to smell.
```

### [82] hash=`57d208516eef5a47`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p8`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（08纪实文学）

```text
All the carpets have to go.Miss Tuesday, can I ask you a question?that's how you make a living, but I can just tell it to you.It's 214.You must be curiousabout that room.I'm surprised.You've been in almost every room in the motel, andyou've been here for two days.You're like a child in your curiosity.This placewould be much safer if you were the sheriff here.Anyway, I hope you can find thatI'll see you girl soon.
```

### [83] hash=`44c75bd80686694e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
Why do you want to go to Stefan's room exactly?Is it related to our investigation?Well, of course boss.I'm here looking for Kayla just as you're looking for that sheep-headedWhat is it?But our canist you're looking for is her name BarbaraYou know herYep, we met on route 77I just got done asking two men about Kayla's whereabouts and saw that it was getting darkMy sight ain't so good at night, and the nights are long these days, so I was in a bit of a hurry,
```

### [84] hash=`45e422a121205ecf`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
hoping to get somewhere with proper lights as fast as I could.That's when I saw her,Barbara, all alone by the road.Some jerk of a driver dumped her there, and she asked me fora ride.I turned her down.Heck, I could hardly see.She'd have been better offthan waiting for the next driver than riding with a blind bat like me, you know?But as I drove away, I changed my mind.She was too young to be left out there all by herself.
```

### [85] hash=`efc70d1556de17c3`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
So I turned back to get her.But when I arrived,she was already gone.There was nothing but a trail of hoof prints in the dirt.When I got to the motel, I saw those hoof prints again.I gotta say, I was kinda relieved to see them.At least she made it here safely.And is she still here?Well, I've never seen any hoof prints leave in the motel.But that don't mean she's still here.You gotta be mindful of what your mind picks up and what might slip you by.
```

### [86] hash=`e327a024996613b6`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
It's easy to ignore other evidence when what you've seen already fits your hypothesis.That being said, it's still likely that she's somewhere in the motel.All right, then let's look for her.It seems we're in agreement.To room 214.202.203.Hmm?I've checked those two.Ain't much in them.Argus.Did you see a red door just now?A red door?Nothing.Must have been my imagination.Are you alright?Can you still see?
```

### [87] hash=`3fce9da325368b92`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
Don't worry about it.Ain't the first time this has happened.Second, whether Manus Vindicke has been here, or anyone from that Order of Enlightenment.And last, about Mr.Stefan.The pistol he used was a Xeno military weapon, and he seemed to know about my relation tothe vacuum bomb operation.It's likely that he once held a high rank within the Xeno military.I want to know why he came to this motel, and what happened to make him lose his
```

### [88] hash=`072cea8a039cea5a`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
mind here.Lose his mind here?What makes you think he wasn't crazy already?Zeno pays much more attention to its soldiers' mental well-being than any conventional militaryorganization.It's because quite a few of them are arcanists, they're both Zeno's strength and weakness.So I'm inclined to think Mr.Stefan developed these mental health issues after enteringthe motel.Huh, is that so?I gotta say, I don't know much about all this military institution stuff.
```

### [89] hash=`67524970e3672019`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
So here's the plan.First, locate Barbara.Second, look for any signs of Manus Vindictaeor the Order of Enlightenment.And third, find out how poor old Stefan lost his marbles.And of course, I've got my own business to deal with.Tracking down Kayla.Hey boss, I've got something.These footprints are from a spider.Looks like the littlewent back and forth along here quite a few times.I know this might not seem
```

### [90] hash=`c1c25dc37ec79852`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
pertinent to our investigation but it is worth noting.You ever seen a spider makea phone call?I'm afraid I'm not interested in the movements of spidersright now.Come on boss, loosen up a little.You hear that?Sounds likedripping water.I'm sure it's just the motel plumbing.But...Watch out!this place is definitely more than meets the eye i'm with you on that there's just too mucharcanum related weirdness going on here never seen so many arrays in a motel before
```

### [91] hash=`120407c487e682cd`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
but we've only found one in your room yeah but there are a load more one room has them drawnfrom floor to ceiling looked like some kind of transformation array to me i ain't no expert soThis is hair from the mane of a howler line, and there are some other materials around it, tooNot exactly sure what they are though.They're too finely groundBut one thing's for sureSomeone held a ceremony here and for some reason it didn't work out for them
```

### [92] hash=`50bdb9252aa3362e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p9`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（09丝与线）

```text
This is important the foundation needs to know about thisAugust this is Kayla's hairShe was here in this roomOr at least someone who came into contact with her.
```

