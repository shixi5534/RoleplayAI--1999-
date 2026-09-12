# 剧情图谱抽取 · batch 003

- 角色：`wu_ming_zhe`
- 批次：**3** / 共 8 批（每批 40 块）｜本批块数：**40**
- 筛选：标题含「77号往事」
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_003.jsonl`

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

### [0] hash=`d6eb093fb7f13375`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Schaefer to a city in the northeast.Detroit, I think?I don't quite remember.Come on, quit fooling around.Oh my sweet child.Argus, Argus, got a message to send?Go get Argus, your trusted friend.Argus, got a cheap bus ticket?Go get Argus, she's got your back.Who's there?It's me, Kayla.You haven't forgotten me, have you?Kayla.It's getting dark.We should take them back.Ain't no way they'll make it through the night out here with their mama hurt, and you
```

### [1] hash=`8f0d4f49e0093bd5`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
can't see a thing at night.Yeah, we need to go back now.Can't delay any longer.What?Hold on a moment.What are you doing?Isn't it better to die a quick death and end up in the belly of a wolf?You've got no right to make that decision.No living thing is born to simply die.It could have stood up.It's not like you give a damn about other people's lives.The only reason you can't bring yourself to kill them is because you enjoy how they
```

### [2] hash=`fd35390b839c5adb`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
always praise you and depend on you.You ain't Kayla.Seriously?Are you saying I'm a fraud just because I don't meet your expectations of what I'msupposed to be?Fine, if you think I'm not Kayla, then why don't you kill me now?Just shoot me in the chest, and these people will treat you like a hero.They'll gather in the fields, holding torches, and chant your name.Argus, Argus, she's spineless.The dearest Mars, it's not possible.
```

### [3] hash=`543fd2a3b244f884`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
The fervor of deceitful spirit of an eternal abomination.We only have our own two legs to stand on.Vargas!Our great hero!The heels of your heroic deeds will be passed down through generations!She ain't Kayla.Now, now, you're lying to yourself again.Of course she's Kayla.It's not possible.Do I need to show you the bullet through her heart for you to believe it, Bonehead?Damn it!She's gonna kill us all!
```

### [4] hash=`427fdfeb55c973fc`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p69`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 12~17）

```text
Mary, come on!Let's show these good-for-nothing mercenary not to mess with us!Don't pull the trigger!Virgin?Calm down, Argus.Remember, what you see isn't real.You're still inside the motel.At least for now.Oh!Here comes another little lady.Excellent timing!Come join the party!I'm here to get you out.Well, that wasn't Kayla.Couldn't ask for better news than that, really.No, it wasn't.Let's get out of here.

Okay.She ain't Kayla.
```

### [5] hash=`763dd2c718c587fa`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Did you see it?It?My baby, of course.Oh, so it didn't show up then?What a shy little pumpkin.What is it, exactly?A supernatural being, an amalgam of urban legends, an ever-pounding heart, this shylittle baby.All under one roof, but seeing how you got out of there in one piece, I'm certain you'vealready earned its approval.I'll show you the sweetest little room in the motel.Don't be afraid, sweetheart.
```

### [6] hash=`9740f730afc1d5d8`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Go ahead, open the door.Think of that.Your eyes haven't recovered yet, have they?Such poor aim.Let me lend you a hand.Listen to mama.I told you long ago about the consequences of disobedience.Oh, it's out of bullets.Could you help me reload?My sweet child, can you see it?This is the beauty of fear.Watch out!Please, come in my dear guest.You'll find what you seek inside.Activate it.What the hell is this thing?
```

### [7] hash=`a4ccead66f16f1bf`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Miss Fertin, please follow my instructions.I need to call my sweet baby.The monkeys in the cages chose the mother covered in cloth.All children needto form attachments.It's a vital part of how they learn about the world.Now, goahead and make contact using whatever method you see fit.Don't worry, I'llkeep the situation under control.This is the only way it'll obey.You want me to touch it?How about I let my bullets do the job?
```

### [8] hash=`44f1903c0a04f0f2`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Agony is indeed a form of attachment.You'll make a good mother, Miss Argus.You make me sick.Apologies.Go wrap my baby in your warm embrace and put it out of its agony,and inflict intoxicating pain upon it.That's why I became its mother.If you hadn't explained this earlier,I might have mistaken this for some kind of monster training show.Baby, you deserve a reward.It fell asleep.You may proceed now.
```

### [9] hash=`b1ff24e02e1c1263`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
It was still called sweet home.It was all alone.Abandoned in the wilderness.A poor little thing.So you took it in?Some unknown, growing arcane consciousness that takes the form of a motel, yet somehow also exists as a baby?That guest who came with you.Shortly after her arrival, she hurried off to that armament factory.She's such an impatient child.Luckily, she made her way back here.Her name's Lilia, right?
```

### [10] hash=`91034343c15d05a4`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
What did you do to her?Relax, she's fine.She's sleeping soundly as we speak, with or without nightmares.Follow me.I'm sure she's eager to see you.This is the room.Open it.Vertin!There you are!Listen, those Manu scum have already wormed their way into the town.We can't go there.You look terrible.I couldn't sleep at all in that haunted room.Every time I closed my eyes, I saw all kinds of creepy stuff.
```

### [11] hash=`d5a36a84e81ba606`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Can you come down here, Kapitan?Talking like this hurts my neck.Okay.What's going on?Are you okay, Captain?I'm fine.I have good news and bad news.Don't bother with the order.Just lay it on me.The good news is, we've found Barbara.The bad news is we've got a new problem.This motel is the manifestation of a living consciousness that constantly generates urban legends and spreads fear.It might turn into a supernatural arcane list in the future.
```

### [12] hash=`a673bac224944b25`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
That's why you came looking for me, right?I'll ask the wind for you.It's the least I can do.Did she doze off?Listening...Oh, I heard it!The answer!A distant wind told me that Ms.Erd's latest submission came from the Sao Paulo Veterans Residence.The article she submitted was an excellent piece.But Otsu doesn't know anything beyond that.Okay.I suppose we'll all have restful sleep and sweet dreams tonight.
```

### [13] hash=`599240fff42a7fc2`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
I've collected the material I needed for the upcoming feature interview.I bet the readers will enjoy it.I'll be sure to include your name on the byline, Miss Tuesday.Me?I don't think I contributed anything.Quite the contrary.You played a significant role.If it weren't for you, I wouldn't have realized my inner fear of losing communication with the world.first-hand experiences like this are invaluable to an editor with the way you
```

### [14] hash=`6d956d34021dbb67`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
put it I almost regret letting you go I won't be returning the interviews overif all goes well you'll be able to read about it in the next issue of our twoI'll take my leave now goodbye good I can't wait to leave this place wecan't leave yet I just contacted the Texas branch theirWhat kind of parent would name their child after a 100-eyed giant?You must have mistaken me for someone else.Hale is a common name, after all, like Emma, Anna, or Catherine.
```

### [15] hash=`83d0b54f69a893b0`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
More importantly, miss, you look, although I've never met you before, you seem familiar.I hope you have a wonderful day.Thank you.Are you a guest at this motel?What happened here the st.Pavlov foundation has taken over ISuggest you find alternative accommodation given the dangerous incidents that have occurred here.What should I do?All my things are still insideThe foundation staff will take care of it for you later.
```

### [16] hash=`a73aeade5a35a2d5`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
You can trust themCan I just go and get my things now?I would advise you to wait until the foundation staff arriveOh, I can look after myselfNo need to worry about me missThat girl...What about her?Never mind.It's probably nothing.Apologies for our delayed arrival, Ms.Furtin.We'd been unable to locate the motel until about 10 minutes ago.It's as if something was deliberately interfering with our sense of direction.
```

### [17] hash=`021147aa0020cd57`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Once again, it insisted on eating garbage off the floor.Is every child this stubborn?Stefan, a Xeno officer.Hmm, Stefan.Sounds familiar.The records show he was a high-ranking Xeno officer who went missing after the vacuum bomb footage leaked.Xeno issued a staggering bounty on him.I guess whatever he did really angered Admiral Igor.Who would have thought he'd be hiding in this little motel in the middle of nowhere?
```

### [18] hash=`fb404ec91e33d343`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Obviously luck wasn't on his side.Alright, Miss Burton.We'll take over from here.After the branch completes its procedures, you'll be sent to the headquarters for a more thorough assessment.Will you return my baby to me?It's too early to discuss that.Let's go, Lillia.We must report back to Madam Z about her.Oh dear, it seems a lot transpired while I was away.Kimberly, care to tell me what happened in this motel?
```

### [19] hash=`4e1b58d77518d493`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
There's blood and brains splattered in the hallway.Who died and how?I managed to destroy the ritual sigils under his head, and I couldn't find them.Now that our base of operations has been exposed, we'll have to take away everything related to the ritual and leave.The Foundation's rats will thoroughly search this place soon.The last thing I need right now is more about this certain Toan she confronted me earlier.
```

### [20] hash=`5871af466d08ce90`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Good as her memory.Fret not, Kimberly.People rarely pay attention to things that don't directly involve them.But I do look forward to seeing her again.We're just here to have a conversation, Ms.Tuesday.Relax.I found it in the wilderness.You mean the motel with arcane powers?Just to confirm, the base form of this arcane consciousness is a heart-shaped fetus, correct?yes it's about as intelligent as a one-year-old human and it lacks the
```

### [21] hash=`a1d1b71e82d99fe2`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
ability to deliberately plan or cause the incidents in the motel meanwhile itsees you as its mother displaying remarkable trust and dependence on youtherefore we believe you were a major contributor to these incidents orrather the one who pulled the strings you may not have acted with evilintent but your actions have caused many residents and she's those toI see.The Timekeeper just reported another crucial piece of information to the Foundation.
```

### [22] hash=`c6821d4262bb1422`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
Were there any activities going on in the motel undertaken by the self-proclaimed followersof the Order of Enlightenment?There indeed were.They left not long ago.I still remember their faces.What did they do at the motel?Her face crippled on the floor and made strange noises.I remember now, whatever it was they were trying to do, it was a total failure.One poor girl became trapped inside their mirror.
```

### [23] hash=`43bf4331b6b48b45`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p70`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 18~20）

```text
She never stopped trying to escape.The mirror would make banging noises all night long.We didn't find anyone trapped in a mirror during our search.Well...If you knew they were from a dangerous Arcanist organization, why didn't you report them to the Foundation?Why would I?Fear doesn't frighten me.No, but the contrary.It excites me.I would embrace fear any day of the week.
```

### [24] hash=`ee5ce94249dde247`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
This is the life a warm beautiful night a cold drink and no one but me and the stars in the skyMaybe I'll just lay here till morning a good night with good drinks.OhI wish every day could be like thisHey, buddy, you're blocking my view.Are you stargazing?Has anyone ever told you that you sound awfully like lieutenant Lillia the writer of red 38Heard of her?No one can fly like her!Of course.Oh my...
```

### [25] hash=`8591b5f5804645a1`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
you even look like her!Keep playing dumb, and I'll show you what it's like to have her kick your ass!Lieutenant Lillia!Airman First Class Andreas at your service!Are you the warehouse guard?Yes, ma'am!On your feet, soldier.My Red 38 is in your warehouse for maintenance,and I need you to remove the gravity ritual from it.gravity ritual if you don't understand what I'm saying go get someone who does
```

### [26] hash=`15852044dce4fbd4`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
I need it today right the gravity ritual yes yes I know please come with me I'lltake you to the warehouse are you certain you can undo the ritual yes ma'amthey made sure I got the hang of it before they took off leave it to melead the way soldier open it oh I remember this package I thought it wasSome kind of joke, or someone with the same name as you sent the package.Who would have thought that you'd come to Texas yourself?
```

### [27] hash=`7dcca37d5c6d4c01`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
Hurry it up, soldier.Open the crate.Now.Ma'am, I know you want to do this quick, but...I haven't been authorized to undo this incantation.If you can't do it, find me someone who can.I won't say it a third time.Truth be told, there's no one else to turn to.I'm the only one left.I was made an Airman First Class to do this job.I was still in training before this you see the others were other transferred back to headquarters or just left
```

### [28] hash=`c15749b6def66988`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
I don't know where they are nowBut since they entrusted me with such an important task, I'm sure I have a bright future ahead of meYou just said you aren't authorized not that you don't have the ability right?I have two options for you oneRemove the ritual now or two.I beat your ass and then you remove the ritual wellWell...Choose!No more gibbering!I pick the second one.Huh?Ha ha!You see, I'm happy to get rid of the ritual for you, but I can't do it on my own initiative.
```

### [29] hash=`e2e651829b826227`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
I'm only an Airman First Class.I can't make decisions about this stuff.So, you have to beat me up to avoid future inquiries.One day, after I'm promoted, I'll be able to better assist you, ma'am.I mean, you're the best pilot I've ever seen!I even made a scrapbook of the reports on your flights.All right, no screaming, soldier.Let's do this.Stop, stop!This is plenty to prove my innocence.I'll undo the ritual now.
```

### [30] hash=`c27fd78c92b85b6f`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
Oof.You almost blinded me there.Thanks, soldier.There's one more thing.Yes, ma'am.Do you know why Zeno pulled out of here so suddenly?Hmm.They said it was an order from the top.The top?And that's all I was told.But word is, it was because Admiral Igor got real mad about the video leak of the vacuumbomb.But that's just a rumor.Ever since the evacuation, strange things have started to happen.Such as?
```

### [31] hash=`84f42a529bb90091`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
We started getting visitors from this group called the Order of Enlightenment, and nowthe farmers have stopped tending their fields.The cattle and sheep have been abandoned in the wilderness.All the townsfolk do now is go to these gatherings,hoping that the sufferer will bring them eternal joy.I don't know who this sufferer is, but he ain't doing any good here.Where do those people stay?In the town?
```

### [32] hash=`43793112491e363e`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
It's a ways away, I think.A place called Tuesday's Motel.Belin!Vertin!I have to go back!Let's get out of here, girl!Safe travels, ma'am!Choose this motel.Can you give me a ride?I can't help you.Ask someone else.Can you give me a ride?I said I can't help you!You want some chocolate?Give me some chocolate.I've never tasted anything so...silly.The hell?Stay away from me!Can I?Can I have the candy?Asking me for candy?
```

### [33] hash=`ae09f67cc0b38ebc`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p10`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（10嘿，万圣节！）

```text
This isn't Halloween, idiot!Look at my back!Wanna watch the aerial stunts?Right wind!It's you.Are you alright?You shouldn't sneak up on people like that.I could've hurt you.Apologies.But you're safe now that you're at the motel.No need to be frightened.
```

### [34] hash=`fe70198a8b5ab92a`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
Is that the sound of a sheep?You noticed it too, huh?Ain't no way that's a human on the other end.It's gotta be some kind of animal.Animal?Based on those sounds and the tracks and the dust,I figure it's something small like a...One sec, boss.It's my candy.Using your arcane skill so frequently must be tiring.You should take a break.The job ain't done yet.Far too early to rest.Someone's eavesdropping on us.
```

### [35] hash=`8b5294dd14a06c4d`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
Care to explain why you're here, Ms.Kimberly?Just how obsessed are you with Mr.Stefan, huh?Even now, after his death?It's not what you think.I was just looking for my toy and it just so happens.Toy?You know, it ain't my style to point a gun at an unarmed person.But sometimes you gotta do what you gotta do.Nothing wrong, told me to.Who's your partner?All the time.I'm hungry.I envy the likes of you.
```

### [36] hash=`67d5e076f85baee7`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
You can store your food in so many ways.You have enough bread and water in your barns to last an entire winter.Your pastures are full of meat and dairy products.But my food?I promise all I'm trying to do is get back what I lost.There's no need to be afraid.We won't hurt you.As long as you tell me the name of your partner.If I tell you her name, will you let me go?That depends on your sincerity.She's called Miss Grace.
```

### [37] hash=`32c9ae3a31790f31`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
What's your purpose here?I don't know.People in Black told me to follow Miss Grace's orders, but she hasn't asked me to do anything since we got here.She must be hiding something from me.I don't care less.I want to eat.You annoying little brats can catch me in your dreams.She's casting a teleport ritual.Argus, your assistance.We can't let her get away.She disappeared fast.At least now we can draw some conclusions.
```

### [38] hash=`a44ffbbf1c6925fb`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
Manus Vindicte has set their eyes on this motel.Under the name of the Order of Enlightenment,they used this place as a baseand conducted some failed ritual experiments before they left.I was worried you wouldn't be able to make your way back, so I lit the porch light for you.Oh, but how annoying that these moths keep fluttering around.Cut the crap, lady.Where's Vertan?Take me to her.I rarely turn on this light.
```

### [39] hash=`76118c81f528b716`

- lang：`en`｜version：`2.1`｜arc：`77号往事`
- doc：`BV1Kf421B7KH_p11`
- title：《重返未来：1999》2.1版本「77号往事」全剧情 - Reverse: 1999｜4K（11“请勿打扰”）

```text
My baby never gets lost, you see.But a young, spirited child such as yourself always needs a light to lead the way.Am I right?To the weary traveller, this light is a shelter, to a child, it's a mother, and to you, what does this light mean to you?No matter who they are, people need a light to shine through the darkness, to chase away their fears.Don't you agree?Are you a member of the Order of Enlightenment?
```

