# 剧情图谱抽取 · batch 087

- 角色：`wu_ming_zhe`
- 批次：**87** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.0」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_087.jsonl`

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

### [0] hash=`c272399cdd20796e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
But now they've followed us here as well, and we've already lost too many friends.I suggest you follow us out, before whatever is going to happen here happens.Where you made your living?Can you so easily walk away?Everyone on Hate Street would be just as stubborn as Jade.But I think it's a wise choice.Wise?Huh.Don't make me laugh.Hate Street.New Age Market.None of this is ours, really.Even the clothes on our back.
```

### [1] hash=`7dd638b4fa0bbd03`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
All we own are the footprints we leave behind.Until they're washed away by the tides of time.We live our lives on the fringes of a world that is not kind to us.We're used to it.Fighting for every street.It's not worth it.But your friends maybe you ought to stop nosing around or you don't belongI'm sorry.Come on.We should get goingMy issue has got things to do.You shouldn't be so hard on herYou've had a hard enough time convincing yourself of what you have to do
```

### [2] hash=`75966bc06a55f95c`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Let's just focus on what's nextNothing more.That's keeping miss Mercuria.There were only a few unexpected patrons.She should have already returnedIf she knows the information I have, she will risk everything to help her friends.So please, don't tell her this.Don't put her in danger.I do not think I can make this decision for you.I get your concern, but she's my friend.I don't want to put her on a dangerous path, so...
```

### [3] hash=`590b581229157e67`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
There's three guys in that tent.I knew the boss was here, but it was the third dude.Pollock?I heard he was in the market collecting information.What?Where are you here?You're that big guy!Let's use Lucky!So let Mrs.Mercuria join us, right?Oh, where did this old man go?He didn't come back once all night.This man has no sense.Mrs.Mercuria will show up soon on stage.I have to decide before she comes.
```

### [4] hash=`270c4a6df3ce4c47`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Her dance offers to break them away from the reality of time and the weight of decision,even for just one song.No!Stop, Matilda!You can't make such an aggressive guess!Mercuria can't be...The room behind the restaurant?I have to hurry!Mrs.Mercuria left with this man!She betrayed us!I have to warn Jay!The ceremony is approaching.She's going to unveil our plan!Did they really leave it here alone?Oh!
```

### [5] hash=`67c0b63bc0110ebb`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
The contact device!It's still in my suitcase!I brought you a gift, Jay.Yes, over there!There's a hole in the door!They're all here!As an apology for my children's poor behavior,I'd like you to take charge of this negotiation.Thanks, Grandpa.But we both know we're not having a party here.And why doesn't your boy Gio come over and apologize himself?Let me give you a piece of advice, Jay.Don't go tempting dogs away from their owners.
```

### [6] hash=`1745f69fdcd01521`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Pay attention to your own men.Or did I misunderstand?This gift from us, Mr.Holick, he a friend of yours?It's Holick!I...I can see the bullets in the chamber when he rolls the cylinder.Alright, I gotta count for the boss.Gotta help him survive the game at the lowest price.Here's your glass, boss.Thanks, Wyzen.I could use a drink.I got sharp eyes!I can do lots of stuff.Counting coins, cars, finding water drops.
```

### [7] hash=`ea222c1af98d3925`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I'm great at spotting cheats and shady dealers.Alright, let's do this, Grandpa.Weizen, get that tequila from the bar.Need a drink to clear our minds.On it, boss.That's a clever kid you got there.Alright, let's get started, kiddo.Condition one, return what you took from us.Sure.Continue like this, Jay, and this will be the best game I ever played.I thought he'd hesitate at least a little bit.Looks like you got a coward for a boss, boys.
```

### [8] hash=`ea8c212fc78c6d5e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Ten.Ten times.The next chamber's loaded.Thanks, Weizen.Condition two.Get your people out of here.Now.We need quiet.Your friends are disturbing our conversation.You heard him, guys.Get out of here.Take good care of your boss.Jay, what are you doing?I'd rather take this bastard to hell with me!When did you become such a coward?No, guys.You're not helping by staying here.Just go.It's a pleasure doing business with you, Jay.
```

### [9] hash=`20efcbf1d71a032f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
You're a practical man.May the sufferer bless you.There's no denying that you got a merciful heart.Eighteen times.The next two shots are safe.I gotta tell the boss.Fill it up to the top, kiddo.Don't skimp on him.I'll tip you if Jay doesn't.Yes, sir.Now, condition three.You've already lost the game, Legers.Oh, so you want to take your chances, huh?Figured 50-50 was close enough.But you know, kiddo, I never said I would only shoot once.
```

### [10] hash=`21a51297ff714fca`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Try it, old man.Do it.You got lucky, kid.Now let's try that again.Eat lead you lucky bastardJaySee what happens when you mess with me games overGrandpa ohBut we prefer to continueKids rip his face off if that's the way it's got to be let's do this old manBut this time we got the upper handnow give back what you took and I'll let you and your little lackeys go orYou're a smart kid, Jay, but apparently you need a lesson in failure.
```

### [11] hash=`38520d61a23da4e7`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I'll be glad to give it to you.We were actually playing two games just now.Those missed shots, they had a purpose.They may not have hit you, but they did hit our second target.Boss, that's...Hold this garage, and your bike!Put down the knife, kiddo.that was just a warning to let you know the game isn't over yet now i got one last conditionlet us leave in peace so what do you say i can turn all of height street to ashes if
```

### [12] hash=`cfc29ec4ba042b5b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
you want me to good boy by the way get yourself a better knife i got butter knives sharper thanJay what were you thinking are you a coward boss don't blame him Beckettit's my fault please don't go Jay I'll come back to help oh come onHolick you just said that this is your fault so do me a favor and shut up youknow you're the one who got us into this mess right if you'd learned yourDamn lesson, none of this would have happened.
```

### [13] hash=`c27e9c878b6f3720`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
So just shut up.Sorry, Mr.J.All I wanted was a safe place to sleep.Not all this.I don't wanna get killed.Boss.I'll get them to come back.We'll get everything back.Hey, hey!I am awaiting orders at 379 Hate Street now.I have sent two investigators back to the branch.They'll show you the way.Since time is limited,I will go to the target location in advanceLes Gers and those Arkanists have made a total mess of the market.
```

### [14] hash=`bca976fa8d550483`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
The people's safety is our top priority now.Jay's been away since this morning.He has to be here when the reinforcements arrive.Where did he go?Nowhere, Miss Bourniche.He's right there.To be honest, I thought I'd never use this thing again.I remember that day.Dad was in the living room with his friends,boasting about this awesome treasury found on his trip.I hadn't seen him smile like that since mom died.
```

### [15] hash=`afc8823fab59808b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
His friends all sucked up to him, thought he dug up some good stuff.I was just a whiny little kid back then.No one liked me.After his friends left, dad put me in a suit and tie like I was some kind of stageperformer and took me to the velvet restaurant.When we got there, he brought this little girl to me and said,Hey son, I got you a little sister.That was the first time I met Paulina and her mom.
```

### [16] hash=`a64fa6880b4e79e6`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I realized that he wasn't lying about the treasure.The days after were sweet, like eating dessert on cloud nine every day.But it didn't last long.My dad was nothing but a broke insurance agent after he ran away from the Weyland family.He had big dreams, but he was too weak to realize them.The Weyland family?I've read about them compiled by the SPDF.They've been arcane blacksmiths famous for their sword making for generations.
```

### [17] hash=`3c026bf04e607cf5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
But the book says the family perished in the war.No matter what generation, Frenchie, weak people cower in dark holes, learn to hidetheir power, and only use it when they really need it.Being reckless can kill you.I've learned that better than anyone since my old man died.And you know what?His friends were right.He followed Solomon's manuscript, a document left behind by his family, and dug upsomething from under the ruins, a worthless piece of black iron.
```

### [18] hash=`e4d92aceca12c28d`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Document holds top secret information only available to certain members of the foundation.How did he get it?And what have you done with the iron?Most of it became this thing strapped to my back.And the rest?Well, you're looking at it, girl.I didn't get why Dad said it was good stuff until now.You know those witches who can tell at a glance whether a kid will be a warrior or a priest?When I looked at this scrap of metal, I had the same feeling.
```

### [19] hash=`7ae4f8103a98beb8`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
It was destined to be a killer knife.And now, it's gonna make its debut.And I have decoded the spell on the key.You have to wait, Jay.Miss Mercuria, she's joined Manus Fintixte.We have no way of knowing what information she's given them.I don't need their help.I can bring my friends back myself, French fry.Those crazies are holding the ceremony soon.I'm not going to let them destroy my birthplace.
```

### [20] hash=`dfd84f0b746801a4`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I'm not going to wait for your little friends to arrive either.Miss J, there's no reason to risk your life.The reinforcements will arrive in no time.Then we can finish this with minimum casualties.Take this lesson from the experienced investigator, Mathilde Buanish.preparation is the key to success I guess you're right when I was a scrawnylittle street kid I looked to a savior like a cop or a boss anything to avoid a
```

### [21] hash=`22dcf6741f16105b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
beating we all got the smarts to stay out of trouble we just got to look bothways before we make our move this wallet is all I have please there'sThere's nothing in it.Just a photo of my wife and daughter.Bogey!Take it back if you got the guts!Ha ha ha!Breton!Catch!Over here, old man!Hey!Get out of the way, you stupid bastard!Help me, Brian!I'm sorry.I'm sorry, friend.We show tolerance and honesty.
```

### [22] hash=`7447217cefd91e44`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Tell me, did your brain slip out of your skull?Don't you know how expensive this cleaner is?Spray it on this piece of crap one more time and you ain't getting a cent next month.But sir, the customer paid us to use this cleaner.And I pay you to work for me, you idiot.Either listen to me or go back to daydreaming in that burnt down garage of yours.We know our limits.Do what we can and give up when we have to.
```

### [23] hash=`da7c6e899882db0e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Hey, hey!Just stay down, you idiot!You'll get paid after the game, I promise!Ah, come on!You think you're a tough man?Just stay down and we'll make a fortune!But if you've ever tried the Tempura Sword, you know that hesitation ruins the work.You gotta be brave, decisive.That's how you make a great sword.That's how you live a great life.You don't gotta be too careful about what you say and do, don't gotta be prepared for
```

### [24] hash=`94ac22580e26fb6b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
everything.Because a brave and decisive fist, well that's unstoppable.I won't just stand back and wait like a coward.Never.You understand?You're right.This would be a serious violation.You'll be going against the direct orders of the foundation.Therefore, as your supervisor, I will keep an eye on you wherever you go.Just in case you do something stupid.Fine by me, Commander.Hey, where are the badges?
```

### [25] hash=`5d283d5033e357d9`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
They were here just now.Mr.Pioneer!Mr.Pioneer!Sorry, I've never seen a case like this before.I can't quite believe what I'm looking at, to be honest.I'm afraid there's nothing human medicine can do.This is well beyond my means.What do you think you're doing, Pops?No one told me you took the new kids to Hate Street!Oh, and say hello to your mother for me.Listen to yourself, pops.Five years ago, when we moved here from that remote, alcanist village, we were down and
```

### [26] hash=`bebe0cfc5d3537db`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
out.But still, you said you'd rather shoot yourself in the head than return home a loser.You promised we'd settle down here, make it our second home.We were cast out by the humans, but we trusted you.We all understood that hating humans wouldn't put food on a table.That's why we respected you, why we still respect you.Jerry Littlefinger died in the tub.His mama still thinks he's working for us on the sea.
```

### [27] hash=`3e1198c9d5c9b823`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Short Ken, who spent his whole life waiting tables, was shot to pieces just a couple ofdays after his daughter was born.And my wife, Savina, was burned to death by some piece of shit Austinist!Even now the cops won't tell me who did it!But even through all the pain, and all the hardship, we had principles.Principles that have earned us respect and made us more money than our fathers didin their entire lives!
```

### [28] hash=`641fb8e88305610d`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
But now you've been corrupted by those lunatics from the Order of Enlightenment!Now the clinics refuse to treat us!They know we don't go by our principles anymore.That every cent we have is taken from those poor people who are as hungry as we used tobe.What do we stand for now?Beating down on the poor and murdering children?No one trusts us anymore.You're pushing everyone further and further away.
```

### [29] hash=`8c9de0aa2b653e5a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
When are you gonna stop, huh?How many more have to suffer?Geo's hesitating because he is thinking straight, Legers.Let's don't bring peace.Geo's risking his life to make you see the truth.I believe you understand that better than anyone.But if you insist on taking his life, I won't stop you.He made this choice himself.Is that so?I'm sorry, Pops.Get him out of here.I've no need for cowards, no matter how loyal they are.
```

### [30] hash=`2ef83373eca683e5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
You've got me wrong.I didn't come here to help Geo or to witness his sacrifice.I was just following my heart.I was invited here to join you.To be precise, I've come here to help you, just like that doctor.I see.I've seen it countless times, how people gather energy to themselves.They put their own lives, their own desires, above all else.They take from others, even exploiting them to satisfy their greed.
```

### [31] hash=`8ba73d222acc7681`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
But Geo's not one of them, nor are you.I can see the aura around you.Your soul, your wishes, your energy, none of them are focused on yourself.They're all focused on someone else.Someone hidden in this place.He's right here, beneath these floorboards, and you've kept him secret all this time,haven't you?So he's the reason for everything you've done.Death has almost taken him, yet you still cling onto him.
```

### [32] hash=`8e77d39425d873d1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
You won't let him go.He's suffering, so the rumors were true.The wailing that people heard, it came from this poor man, and you, a human of fleshand blood, unprotected by any arcane skills, were shot in the head, yet continued to walkand talk.Those bullets never penetrated your head, did they?Because you are not Leger's.He is.The Order of Enlightenment has allowed him to survive, albeit in a dying body, but there
```

### [33] hash=`ab5408d486554c7c`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
is a price for this.His consciousness.The most I can do is recover his consciousness for a short while, but I can't save himfrom death.You tried so many treatments, brother.Sometimes, it felt like torture.He breathed.You're back!Legers!You're back!Listen, I've found a way to cure your condition!I swear you won't die!I swear!Are you a professor now, Salvatore?This outfit isn't your usual style.You used to wear a pair of gold frame glasses and criticize everything you saw.
```

### [34] hash=`831e78deeee0e080`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
A true intellectual.That's the Salvatore I know.After you were shot, I disguised myself as you.I've been running your kingdom.These kids need you.So I gave up my diploma.We'll share the fame and power when you get back on your feet.Just like you always wanted.Listen, this isn't what I want.You're supposed to be working at a law firm, taking money out of the hands of rich titleones, not pulling trickers, not spilling blood.
```

### [35] hash=`43210ac6f6317ec6`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
You gotta get out of this dump.I dirtied my hands so that yours would be clean, so that you could live the life youwanted.I never wanted you to follow in my footsteps.How are the others doing?Ken and Jerry.They're both honest, hard-working guys.I never should have brought them into this world.They've gone home, Legers.They've...I've been on the streets sleeping for too long, Salvador.My brain isn't working.
```

### [36] hash=`dec3859aa638f105`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I can't even open my eyes anymore, feels like they're glued shut, am I?Describe it to me, tell me where I am, is that the sun?Am I an eagle in think calling for us from the kitchen?Did she find out we stole the rum again?Les Gers?No.Yes, the sun is rising.Oh, I can feel it's warm.You...you're at home.Isn't that right, Legers?Yeah.We're in Sicily.We're in your old bedroom, remember?Dad just beat the hell out of us.
```

### [37] hash=`e4a3070440df8ac1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
He's smoking in the doorway right now.He said he'd tie us up to stop us from getting ourselves killed on the streets of America.I is totally creepy t-I gotta go to bed.Don't wake me up, Salvatore.Remember to keep breathing.Gotta have one member of the family who uses his brain for a living.Promise me.I will, brother.I promise.See you tomorrow.He's gone.I won't blame Gio.And I see now why you all made your choice.
```

### [38] hash=`4df8e2bc119cad91`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
We thought she was a grandma, you know?Like, one of those little old ladies who uses a walker.Well, boy was I wrong.She ran faster than a jackrabbit.So there she went, the good still in her arms.Shut up, Roth.And quit trying to get rich.I gotta take a leak.Hey, Kuko!You trying to piss up a lake or something?Hurry up!Shoot.I don't come over here.My zipper stuck.Give me a sec Kuko.Ah, you need scissors or something
```

### [39] hash=`44bd6fe5a1211215`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Mr.Pioneer nowWhat the hell told you it wouldn't work.It isn't handy at allIntruders over here come quick you idiots.OhI have a feeling this one will be a hard nut to crackDon't worry about them.They're probably just hiding somewhere.We've already taken down most of the guards.They'll realize soonI'm here boss!Help!Mr.Pioneer is...Pioneer!I'm sorry man!I should have come earlier!Enough faffing around!
```

### [40] hash=`af3723646309e3ed`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Go get my arm!And don't make me repeat myself!Hey!Don't kick my butt!Damn!What's wrong with you man?I've never swum in my entire life.You almost killed me.Well, when new boys join us in the future, I'll tell them you know that famous Jay.He was drowned in a kiddie poolMay the rubber duck be with himThe door is right where you're standing, but there's nothing here miss Bowen eachNo keyhole.No door frame.
```

### [41] hash=`08cd44cf1b1d5c1d`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Is it buried underground?It perhaps we need to dig it upNo, since the very beginning, there's never been a specific door that leads to their lair.In other words, any door could take us there.The key is a shortcut.It will take us directly to them.I saw them go into the woods with dozens of believers.They went inside a tent.I was worried about my friend, so I searched for any secret tunnels or cellars that they might have used.
```

### [42] hash=`2b91196dfb0deff8`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I thought I could follow the traces left by their arcane skills, but I found nothing.At the same time, I heard that a door had been salvaged from the sunken Lady Elgin.The archaeologists found that the door didn't lead anywhere.It was useless.Back on the ship, it was installed in front of a wall.I've read about these meaningless doors before in my brief study of archaeology.When installed inside tombs, they serve as a decoration and a distraction against tomb raiders.
```

### [43] hash=`b6f8f0107eb51a6b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
So, it dawned on me that perhaps it is not the door that matters.It is the key that matters.A medium through which spaces are connected.It is the key that opens the way.En conclusion, this key can make any door a shortcut to their lair.Even without a door, there is still a path we can take.There is always a direct route that connects two points on the map of Gnosis.We can take that path by touching the key and reciting the incantation.
```

### [44] hash=`b02fa157e98d126f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
All we need to do is draw an entrance.So...Send the coordinates to the Foundation.When the reinforcements arrive, they can come with us.Before we enter, you must know.I only master the art of opening the door, the art of closing the door, however.Well, only the Manus know how to do that.Are you all aware of the risk?We may get locked in there and never come back.Alright, alright, enough talk.We've come this far.
```

### [45] hash=`a3576d2bc884ffad`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Nothing's gonna scare me off.We're here, gentlemen!Boss, boss, what are you doing?I can help too.Just ask Mr.Pioneer.Now calm down, fellas.It can't possibly be that bad.If people are managed followers, the Foundation's reinforcements will be far from sufficient.Ah, it appears we're already in the middle of their lair, Miss Boaniche.Welcome, distinguished guests.What a pity!I thought you gentlemen would recognize me.
```

### [46] hash=`04e3ac6d0d98bc4b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Have we met before?Wait, I know.Give me a sec.Damn!When did I mess with this girl?She's gonna eat us alive if she finds out I don't remember her.My apologies, ma'am.We simply didn't expect to see you.We're new here, and the sight of this place took us aback.I see.Allow me to thank you again for your alms.I can forgive your surprise.You're certainly not the first to react in such a way.You don't look like merchants or believers.
```

### [47] hash=`09abd18ce915cce5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
And even the way you were invited is unique.You must be the special guest of the ceremony.That's exactly who we are.We got lost.That's why we look a bit messy.What lovely young people.Now, may I see your invitation from the Order of Enlightenment?Look at you!There are no invitations, it was just a joke, sweetheart, relax.I have no interest in those outdated rules, where there are customers, there is business.
```

### [48] hash=`592f99221799653a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Every coin I earn is as glorious as the last, no matter whose pocket it's from.And amidst your confusion, I smell a good deal.On the other hand, it is good manners to notify our host of the arrival of new guests.I'm sure they'll provide a satisfying reward in return.You've given me quite the dilemma.What to do?I wonder...Don't look at me!Where's your money?There's no room in my budget for any extra expenses!
```

### [49] hash=`55b075a01473c850`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
In that case, how about another deal?I recognize that thing on your back the moment I saw it, young sir, and those calloused blacksmith hands.Oh, look, you've wrapped it so tightly for fear of it being recognized.That thing can't be hidden.Since you've lugged it all the way here, why not show it to me?Uh, no.It's totally worthless.I'll make the payment.This crystal ribbon.Would you look at that?This is Barrow Bow and Nisha's money.
```

### [50] hash=`50885c08b6a9fd7c`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Then you, little lady, must be her daughter.This will be quite a show.What are you talking about?Anyway, I showed you my sincerity.Now it's your turn.Hey!Where do you think you're going?We haven't asked you anything yet.No need, sweetheart.I already know what you're going to ask.A good merchantalways knows what a customer needs.Your friend has been waiting for a longtime.Oh, and here's some free advice.
```

### [51] hash=`88c9fbf217cb69e2`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Don't get too close to the altar.Hey, what's that?Jay?Madam Gloria, isn't it?I thought she went home afterJay, what the hell are you doing?Wait, Niko!Why are you intruding on his joy?Can you not see that he is enjoying the grace granted by the sufferer?Yes, equator!Leave that evil believer alone!Paulina?Place your palms upon your eyes.Be Lord.
```

### [52] hash=`a7d9205628dedcea`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
According to the Foundation's assessment, this is a priority level A operation,which means it'll be as dangerous as the Walden operation.I hope you're fully aware of the risk.We don't have enough men or supplies, Captain.We don't stand a chance.They've refused to send us any support since the last mission.We can't do this without...Enough, soldiers.An order is an order.Remember, the goal is not to fight a war.
```

### [53] hash=`1da27d815a7cab3b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
The Manus leaders are scattered all over the place.Our mission is to find them and finish them.The assassination of the Manus leaders is our top priority.The backup from the Foundation will not arrive until we've completed this mission.In other words, if we fail, we're on our own, right?Let's hope it doesn't come to that.Time to move, soldiers.We've almost arrived at Investigator Bo and Nisha's coordinates.
```

### [54] hash=`ac988baba4264a32`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
We're walking from here on out.Quit standing in the middle of the road.Hey, are you blind or something?Focus on the operation, Todd.Let's go.Just close your eyes, and it all becomes real.Close your eyes.Stop thinking.Then you will be in paradise.Illusion is also part of reality, is it not?And for me, you should have come sooner.I'm sorry.That's the illusion confused you, Jay!You must break away!I know you're only an illusion.
```

### [55] hash=`db74dc15ec3cc54b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
A thought in my mind that I just can't shake.But even so, I want to stay.There's something I've always wanted to know.Tell me, Paulina, do you want to go back to Haight Street?We'll stay in the restaurant like we used to,but there'll be no drunks looking for trouble this time.Hop on my bike and go for a ride around San Francisco.scare the heck out of any boys who try to hit on you.If the Saint Pavlov Foundation invites you to join them again,
```

### [56] hash=`096f074b18befe01`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I'll tell them to buzz off.Of course.You're not Paulina.Not even close.You didn't call me a jerk.You didn't have that sarcasm of hers when people looked down on her.Of course I miss my sister.More than anything.She was proud of me.And when she packed her bags and left Hate Street, she was proud of herself.What do you mean, Team Matilda?We should obviously be Team Jay.Oh, please.Neither one of you has good taste.
```

### [57] hash=`6abd37c4be1b662a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I'll tell you one thing.You got good noses, but it'll only bring you misfortune in this game.Good evening, uninvited guests.and repeat after me.We praise.We rejoice.We praise.We rejoice.We praise.We rejoice.We punish.We cleanse.We awaken.We are one.We punish.We cleanse.We awaken.We are one.We've lost contact with Investigator Boanish.Please reconfirm the coordinates.What, Captain?They're just normal Arcanists and humans.
```

### [58] hash=`1026bd47a0d28620`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Investigator Boanish said that she left a door at the coordinates that will take us to the ceremony site.But...According to the plan, she was supposed to meet us here.I will leave these uninvited guests to you, Lejaz.Good job, Wyzen.Thanks, boss.It took hours to get the plan through Becca's thick skull.But we nailed it.Put the key away.Mr.Tang once told me an old Eastern proverb.Wangzong Zhuo Be'er.
```

### [59] hash=`0d3d0ef0bfe81e9a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Impossible!How did they get here?You!How long have you been working with these blasphemers?Ha!Say goodbye to your precious leisure.You're a little behind on the news, aren't you?I am the only Les Jours now, Apostle.Calm down, Miss Bourniche.Time was against us, and we thought that your authentic reaction would be more convincing.Gio reached an agreement with Jay before we left.That punch felt pretty personal, though.
```

### [60] hash=`94a5ee7635d422f3`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
It almost beat the crap out of me, Gio.I couldn't help myself.Jay?You want me to beat him up?No, Holic.He's an ally now.We gotta look out for our friends, right?Yeah, we're friends, huh?Still, if these sons of bitches don't pay up to fix the garage, I'll beat the shit outof them.So be it.I have already prepared a surprise for you blasphemers.Legers, I have exhausted my pity for you.It appears your loyalty is even more worthless than I expected.
```

### [61] hash=`78586ba03351c63a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Very well.The door to Elysium shall be shut tight.ones that you have no control over you're welcome in the depths of thewoods where whips and voices cannot reach who is calling not even the mostbewitching voice can drown out the songs of the birds those who dancethose who are blinded breathe in the fragrance of the meat egg and come withMe.Everything, everything is ruined.I never should have trusted any of you.
```

### [62] hash=`bfea5e5ead82bcaa`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Thanks for the show.Your failure was magnificent.Your arrogance, your regret, and that look on your face when everything was ruined.They were all just perfect.Damn it!Where have you been, Eternity?You defrauded us.Taken every sharp-a-dontie, squeezed us of every drop of sweat and blood!You swore the ceremony would go smoothly, and that you'd pay your highest respects to the inculcator of Arcanum, the Great Sufferer!
```

### [63] hash=`501b966b57dac701`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
You rotten, shameless liar!If I could only throw you into the depths of the Gorgon Current, I will crack your skull and make you bear the price of my pain!I'd almost forgotten about your Mediterranean roots.I must say, I didn't expect such courage from a coward who fled a battlefield.Your pitiful Charperdontes are far from sufficient payment.No one would be stupid enough to go against the Foundation for so little profit.
```

### [64] hash=`80f6bf215abf556e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Besides, this was never part of the deal.Do you have any idea who you're dealing with?That's Barrow Bow and Nisha's daughter.And the weapon that boy carries?But listen, if you don't help me escape, I'll never pay you the other half.It's true that the people at the Foundation are all misers.They're still more generous than you.I can give you anything.Rare wands, alchemic materials, and jewelry.Lots and lots of jewelry.
```

### [65] hash=`5b391828245325a0`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I got them from the believers.If there's more, I keep them in a cellar that only I have the key to.You're a dishonest customer, Apostle.You're lucky that your pockets aren't empty.Pack your stuff.Let's...Hey there, little lady.Nice to see you again.Arthur?I have no interest in the manis.I just have some business to finish.You know I'll work with anyone if the deal is sweet enough.I'm a businesswoman.
```

### [66] hash=`330120ad12f7a851`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I always keep my word.I'm sure you understand that.You're right.Cannot let you escape.I have to take the two of you to the foundation.You can plead your case there!Anyone up for your seat to the senior?I came from the foundation's logistics department!Everything's here!I swear!You have to make sure I get out of here safely.If you keep your word, I'll tell the picture about you and we can do more business together!
```

### [67] hash=`6d8b5e6f96fb1ef0`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Come out, Believer.There's been a change of plan.Follow me.Eternity will get us out of here.What a huge collection of valuables.And people just handed them over to you.Looks like religion is a profitable business.Alright, now escort me out of here.I never promised any escort, apostle.Did you ever hear me utter such a word?But I did say I'd get you out of here safely.Let me see.If memory serves, that tricky little thing is...
```

### [68] hash=`cc7848d11df89ab5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Here it is.There you go, it's from the St.Pavlov Foundation, one of a kind.This gadget was stored in their headquarters, no one could lay a finger on it.But when chaos broke out, it fell into the hands of an employee looking to make a profit.What's this?Some kind of wind up toy?How's this going to help me?Do I look like a complete idiot to you?Of course not, my dear customer.Just wind it when you need to use it.
```

### [69] hash=`40ab71b7174595aa`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
That's all, Apostle.What's it going to do?Turn me into some kind of beast?A three-headed dog or a crazed bigfoot?Listen to yourself.Why would I do that to a customer?You won't turn into a monster, I promise.There's still plenty of business to be done between the two of us.Time to say goodbye.It's been a pleasure working with you.Wait, wait!I'm a merciful hunter.When I penetrate your skull with this needle, you'll die quickly.
```

### [70] hash=`bfed55d277a81cfe`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
You'll hardly suffer.Or would you rather I use a more ancient method?I could extract your spine and store it in a jar of formalin.Jay, she insisted on coming.She wouldn't take no for an answer.Order, what are you still doing here?We have captured all the peddlers and believers in the lair.Everyone's waiting for you.Did you catch the apostle?He's crucial to our investigation!You freaked me out, Frenchie.
```

### [71] hash=`298afe53d67a01fb`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
For a second there, I thought I'd have to rush you to the hospital.Both I can deal with such a simple trick!No.Matilda, Holik, I need you to go and get all the Arcanists who can still fight.I'm just trying to carry out my master's order.Don't waste my time.This will be useful.Thank you for your help.Now then...We'll be unconscious within a minute!Jay!Are you okay?I'm fine.It's nothing.Good thing is, the pain's kept me awake.
```

### [72] hash=`ba087b370b9f401c`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
And I can still move my arms.Looks like an exciting show.I wish I could sit down and watch.Enjoy it, miss.Is that woman to your weapons, boys?Fine.I'll use what I have.Ugh.This sucks, Dad.My forging's not even close to your level.In that moment, your father was, well, his arms were charred.There was nothing we could do.He was dying, but he wouldn't let the sword go.What I didn't know was that it wasn't he who was holding onto the sword, but the sword
```

### [73] hash=`3aa32b53b68b98a3`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
that was holding onto him.The next day, the sword was gone, and I saw you holding it in your arms, fast asleepyour bed.Stay away from it kid.You may not have chosen it.Sorry Mr.Tang.Long timeno see, buddy.Have a little dream with me cutie pies.What the hell is this monster?Is this thing the girl that was just here?Hell of a transformation.Something hereStay away from me!This sword's got a mind of its own, and it ain't happy!
```

### [74] hash=`6ae61637c35d20b1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Boss?She, uh, she's moving!Watch yourselves!Melt it down, forge it up.What'd you think about this?Just half to death.Still breathing.I'm not going down like this, French fry.Nah.Gotta check on Hollic.No!Boss, stay back!We didn't have to keep playing this little game.You just won't be satisfied until it's over, will you?Go!Just stay where you are!Hide yourself!Just listen to him, will you?This is starting to become bothersome.
```

### [75] hash=`ce46b62b28a13ab5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
No, no!I have to do this!Jay, tell Beckett that I didn't...I didn't run away or cause any trouble this time.I'm more useful than he thinks, right boss?He'll never make fun of me again.Damn it!Fire!Someone's gotta see this smoke.Don't give a crap about what you learned on the streets!I don't want to hear it!I'd rather take my chances and die out there than stay here and never live at all.You really think you're going to build connections with the government?
```

### [76] hash=`c1290c4cb97881b7`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Rub shoulders with the upper class?You think they'll take you seriously?You're no different from any of the cannon fodder at the bottom of their system.You're going to be fighting a battle even tougher than the one on Hate Street.Why do you think I kept those government suckups from finding you in the first place?Listen, it doesn't matter where you go, as long as it's not the St.Pavlov Foundation.
```

### [77] hash=`aeb2e04fd2134bfd`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
You could go to college, join a company, a hospital, you'd have a better life thananyone else!A better life than anyone else, huh?Listen to yourself.That's ridiculous!You finally said what you really think, didn't you Jay?Our righteous boss and kind-hearted neighbor, but you know what?I'm not interested in comparing myself to anyone else.I actually want to do something meaningful with my life.Something beyond you.
```

### [78] hash=`5533ffb59aca30db`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Beyond myself.Beyond the whole of Hate Street.And there is nothing you can do that is going to stop me from pursuing my dream.But who's gonna help you when you're in danger?Those idiots in white robes?How can you entrust your life to the Foundation and not your family or friends?And all because of some dream you're not even sure you can realize?You know, one day you'll come crawling home and cry about how the world is nothing like you imagined.
```

### [79] hash=`020f06eadb2b9a71`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
And I'll just laugh and say I told you so.Then laugh, Jay.Some people are willing to deal with pain.Even willing to sacrifice themselves if they have to.If I die out there, it'll be because I chose to.If that's the price I'll pay to protect everyone, then so be it!What happened, sis?Since when did we walk such different paths?Ever since you beat up that voodooist, who tricked me and laughed because I was a human.
```

### [80] hash=`ba1f7a1c8eac6d7b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
That's when.You beat him to a pulp, Joe.You forced him to bake on the street.Everyone here is stuck in a vicious cycle.One person tortures another.I'll walk until I get there all right blondie ready for a formal in bathtell me Matilda when you come from the man are you certain that you have thecourage to come face to face with death are you sure you're ready to serve as afield investigator I will do everything I can to protect everyone with honor
```

### [81] hash=`394c73434cc315ad`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Antignity, I will make the Bwanish family proud.Run, you idiot.I don't need you to protect me.I don't need your sacrifice.I don't care about your duty or whatever the Foundation says.I don't fucking care.You don't get it, do you?If you die like Holic back there,everything you have,everything you've been through,will be gone for good.Tell your bossthat I got in trouble becauseI didn't follow the confidentiality agreement.
```

### [82] hash=`183b6db3fd022eda`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Tell her I deserved it.And tell her that stupid big guy over therepicked the wrong side and got himself killed.You've done your job.No one can blame you.No, I decline your offer.I will stand until the reinforcements arrive.Just run.Forget about us.Save yourself.Some people are willing to deal with pain, even willing to sacrifice themselves if they have to.If I die out there, it'll be because I chose to.
```

### [83] hash=`2fef524115e2b75a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
If that's the price I'll pay to protect everyone, then so be it.I wish you could have lived a different life.I wish you'd been born into a happy family.That you'd had your own room, with a huge bed, and lived in a beautiful, fancy house.I wish you'd been a rich girl.I wish you'd been cherished by your parents, and that everyone had been proud of you.I wish you'd never known about the poverty, disease, and war in the real world.
```

### [84] hash=`05de52b2526de889`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I wish you could have slept in a room without a broken window,on the fireplace that kept you warm at night.I wish you didn't have to live in that rundown room I set up for you.I wish you could've worn your clothes, but you all were not around.I wish you could've been surrounded by kind and loyal friends you'd never met.I don't want to write this letter, but I promised myself that once we could talk as equals,
```

### [85] hash=`5cb7df80c3b7b41d`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I would persuade you to accept my decision.Sure is dusty in here.I gotta clean up.I thought I would have the courage toconfront you then.I thought I could tell you how foolish and selfish you were.thought I could make you proud of me by going to places you've never beenand seeing what you've never seen.But now, when faced with a mission thatcould put my life at risk, I realized that I'm not as brave as I thought.
```

### [86] hash=`882d92fb161d1624`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Mythemselves if they had to.I remembered the scared look on your face when you heard that.I was so proud of myself at the time.I thought, finally, I managed to scare him.But nowI wish I could go back and stop myself.I know that scaring you is nothing to beproud of.I only did it because I knew I was the only one in the world who couldhurt you.And now that I've established myself, I can talk to you as an equal.
```

### [87] hash=`dcc77f6b60ba3a9c`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
But I found myself doubting my decision, when my colleague knocked on my door, urgingme to prepare for our field mission.And he called out my name, Paulina, Paulina!How I wished he were you.How I wished for you to open that door and protect me.That thought only lasted for a moment.Then I understood where my fear came from, and why you were so scared when I talked aboutsacrifice.I realized that even though countless people are suffering out there, even though my colleagues
```

### [88] hash=`a8df653ee297ab5f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
have sacrificed their lives, even though more and more children have become homeless,I'm not as brave as I want to be.All fixed.Finally.You're looking much better now, buddy.Mr.J, are you really selling the restaurant?Don't worry about it.A new, even better guy will take over.But I also understand that someone has to step forward and stop this tragedy.Otherwise, our world will fall apart, leaving nothing but sadness and pain.
```

### [89] hash=`35839eaf3a5ebd44`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
A single drop of water can't form an ocean.A single piece of tile can't build a roof,Nor can a single person put an end to a war.For a long time, humans and arcanists have been on opposite ends of the spectrum.Faced with this catastrophic event, we may all perish unless we stick together.But in the grand scheme of things, I'm just a blip on the radar.Yes, I'm just a weak, cowardly human.But I'm also a member of the Saint Pavlov Foundation.
```

### [90] hash=`03302d978fbfe816`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
We should go, Jay.Boss, what's in it for you to join the Foundation?You know they're all liars.Those holier-than-thou officials never tell us what's really going on.Besides, if Les Gers is taking over the restaurant...Hey, watch your mouth, kid.Your boss would have been hacked to pieces if it weren't for us.Wipe your nose, kid.Les Gers will be a good boss.Promise.He'll clean up the mess on Haight Street, and after that, the poor house staff will
```

### [91] hash=`c3bfb1ff25373086`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
get you into school.And Holick's bike.It's yours now.So, what are you going to do now?Me?I'm going to jump into the sea.And try to swim.What do you mean, boss?I thought you didn't know how to swim.Shut up, you noisy bastards!I'm trying to sleep here!You shut up!Yes, no one can cause a friggin' earthquake!Shut up!Make any more noise and I swear I'll anesthetize you so you sleep for the entire month!
```

### [92] hash=`7e30cd9f7d51ba3b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
I owe you one, Razor.No, you owe Mesh one.If she hadn't led us to the door, we wouldn't have been able to stop that girl in time.As it turns out, your Curia foresaw the whole thing and took action before anyone realized what was going on.She always does this.Once she's fixed on a goal, she never considers her own safety.But despite her courage, she's still a living person who can get hurt.Please, promise me you'll bring her back.
```

### [93] hash=`9ea50b35160b6234`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
It's a shame we couldn't arrest that girl.If only we'd had a little more time to prepare.You're up, man.You saved my life, didn't you?I'll get you pretty far on Hate Street.Aside from the most important one which is now in the hands of Manus Findictae.Luckily, the man in control of the girl is one of their insignificant believers.For the time being, there's a limit to what he can do with her.This, at least, is good news.
```

### [94] hash=`d6aa101bea1b64a9`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
You've caused quite a stir among senior management, Ms.Bohnisch.It seems you're starting to make a name for yourself.Thank you, Monsieur Bernard.By the way, I would like to apply to leave the Foundation during my vacation.I want to visit my mother in her safety house.That merchant, Eternity, and the peddlers in that lair mentioned her name several times.I team it necessary to confirm her safety.No problem.
```

