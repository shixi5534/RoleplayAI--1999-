# 剧情图谱抽取 · batch 052

- 角色：`wu_ming_zhe`
- 批次：**52** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.0」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_052.jsonl`

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

### [0] hash=`21f501d69e4a05e7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Casual wear required.The date of the 1929 crash confirmed by primary sources is Thursday, October 24th, and thedecline happened again on the 28th and 29th.Intelligence division indicates that no arcane forces were involved.Hmm.The Manus is changing history, Ranunzie.I'll send you a special team and give you the highest command.Do not make any moves until you figure out the reason why they want to change the history.
```

### [1] hash=`24075257d7c8b551`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Copy that.Sounds like your friend just got into some troubles, Regulus.I'd say, sign these documents and that's all for me, right?And then to the office of the Scientific Computing Center.That's right.Let me show you the way, Regulus.Mm, this is Ax, our mechanical scientist.he will introduce you to some of her research devices.Although you're known for your rock and roll,I've heard that you're also interested in human technology.
```

### [2] hash=`d4c6a364d1240d9b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Oh, I got it.I don't need to introduce myself then.Just call me Captain R.That's not what our names come from.Follow me, friend from afar.I have a lot of interesting new things to show you.The office is the only branch of the Scientific Computing Centeraffiliated with the Foundation,Although you didn't bring the Little Thing with you, I believe it's still necessary for us to know each other.So it seems everyone at the Foundation is an intelligence expert.
```

### [3] hash=`2de8b096b6141905`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
We are not part of the Foundation.Not even part of the Scientific Computing Center.Unlike the Manus rioters who attacked you for your Little Thing.We are only interested in the Arcanus to our curious and inquisitive.Everything else has nothing to do with us.To better understand the storm, Lorenz needs more talented collaborators.Hmm.So does the door in front of us lead to your secret base?For now, yes.
```

### [4] hash=`dbc7fead686d5ca2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Can't see anything inside.Vertin and Senetto, what are they doing now?Freddy, do you make the auto-island move faster?Our Miss Senetto has something really urgent.Miss, you're really going to sell your potion?Now you've got a lot more strength, right?I added the most effective tears of the pure blooded caressand the strongest bile acid of the blue lobster.Definitely makes you forget the fears and be courageous and excited for two whole days
```

### [5] hash=`e0edb3e984611b06`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
without food and drink.Ms.Sotheby, did you feed him a whole bottle of that?It's too dangerous!Oh, the handrail!I've never felt so good in my whole life!Charge, baby!Charge!Charge to high heaven!The wheels on the bus goround and round!Round and round!I know we crashed into theback wall of the Walden,but it looks like...like an underground labyrinth.Crashed into the back wall of the bar?They all act in groups, generally speaking.
```

### [6] hash=`3ae378124c069de0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
If you see one carbuncle, it means...There's a large group of carbuncles around here.We have to beat them before we leave.Okay, alchemy will def-Come in handy.Freddy...Leave him to me.I will carry him.Miss Sotheby, you seem to know the Walden better.Please lead the way.Sure, no problem.It's different from the bar I imagined.I will definitely find the right way outSchneider who's there?I just heard.
```

### [7] hash=`c77705b06c208c42`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Is it my mistake?It's not going out of the wallIt's a mixture of human blood and vomit us.This isSerumWhy are you talking to yourself against a wall if you want to get out soon?Oh, I will be there right awayIt shouldn't be a mistakeThere is a human imprisoned by Arcanum in this speakeasy, we have to report it to the timekeeper as soon as possible.Thanks for coming to assist.To make you ask Madam Z for help, it must be tough here.
```

### [8] hash=`376687627cee06ec`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
I just don't feel good about this.Hopefully it's my misjudgment.Is everyone in position?Yes.Eight of the team got the invitation to the gathering, they have entered separately.Others are standing by at every entrance of the speakeasy.These are the intel we got about the Walden.They're going to hold a live jewel show tonight.Fighters can win stock in the amount of one million dollars, and the betting odds can be from five to one to ten to one.
```

### [9] hash=`be7398fc4bdaf7d9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
They're crazy.Timekeeper, please, take this with you.It's the latest product from the Scientific Computing Center, Heaven Apostle 347.They've added the cell sap of the bombard ball to it, unfold its wing, and it will blast in 15 seconds.The blast is undirectional.Please watch your position when you use it.Got it.Let's head down to the warden now.You follow Apple.Remember to stay low profile.Welcome.
```

### [10] hash=`fbe5d484004db07d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Welcome, everyone.All the new immigrants, arcanists, moralities and immoralities,anti-saloon league and democratic progressives, free thinkers and churchgoers.Welcome to your eternal home, the Walden.How was it?You seemed to be enjoying the last show, the hooch dance girl with the boa constrictor.Well, in that case, next round's python suite is all on me.I assure you every Chicagoan loves the YY Bourbon.
```

### [11] hash=`018386a4f65ddd97`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Forget its charm.Oh, I guess your eyes are fixed on the charts.Don't worry, my friends.Let's focus on the next duel instead.Trust me, and you'll get the return beyond your craziest imagination.Ah, so crowded.This Apple's favorite bow tie almost gets lost.Why is the speakeasy so busy?It doesn't look like an illegal place at all.This is the only speakeasy in the States that has never been given a shakedown.
```

### [12] hash=`fbabf28b8b3939c6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
It's said that, forget me not, owner of the speakeasycan make a potion drink which is not alcoholic until people drink it.From purchasing raw materials, getting a medical store license,distillating, transporting and selling, and ensuring the security together withgangs.We got nothing on them.It welcomes allthe marginals and doles out patronage positions.Through this the Walden has already cemented itself as the one above all
```

### [13] hash=`48e6fb78f7fd6bb0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
other speakeasies in Chicago.Did you find out the relationship betweenDoes Manners-Finn dictate him?No, his document was edited purposely.But we can be sure he is from this era.However, we found that the time he made contact with the politicians was close to the beginning of the unusual boom of the domestic financial market.Since then, you can't talk about arcane stock trading without mentioning the Walden.
```

### [14] hash=`a4d06a7bf13e3939`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Alright, my friends.We're about to have a taste of tonight's appetizer.let's welcome our fighter of the year the defender of the undefeated honor ofknocking out ten consecutive Arcanists and human challengers then which guestwill have the honor to be the challenger of the do a million dollarcoupon you get beat the crap out in lion bed for two months worth itI prefer Betty.Maybe I can get a Hamptons Villa.
```

### [15] hash=`b97d2d778f30c809`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
The fate of this challenger, we let the Spotlight decide.The Spotlight chose you, lady with the top hat.I give you Schneider, the defending champion of last year,and the timekeeper from St.Pavlov Foundation, Miss Vertin.Shit, they got our intel's too?I'm going, don't worry.And now, let the duel begin.Long time no see, Miss Governor.It seems my lord would like to see me kill you myself.He has even created such a chance on purpose.
```

### [16] hash=`5b5056676df150d8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
This is your life, here to enforce justice on the Foundation.The Foundation obviously has no justice.You don't even dare make the storm public.Turn down my families with ridiculous lies.Is that your so-called justice?Orange and Seneso's mission capsule.That's where you can hijack the hostages outside the parking.There's no shelter there for me.Then all I can do is to complete the tasks for my lord.
```

### [17] hash=`e882310be054220d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
He just lost my focus.I won't become serious now.The champion!I bet all my money on you!The downrock is to 381.17!Then I...I add 5,000 more!It's better than I thought.It's in the Foundation.Why did you go to the Foundation?Can't the Manus give you what you want?Because we, the ones sifted out by the storm, want stormy is about to fall.Who cares whether the shelter is the eave or the rubble?What if I say, I can provide you with the shelter?
```

### [18] hash=`f11107641135f235`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
The person who said this to me last time is just sitting behind us watching the game.The trend is falling by 31%.Is it me or?Hmm, it seems we are behind the spotlight.Brats are huge!Why don't I use a corrosive potion to dissolve them so we can move the bricks?Good idea.Let's start from the middle.We should get out of here as soon as possible.Timekeeper, she definitely needs my help.The joy, the joy from the bottom of my heart.
```

### [19] hash=`99060e9ffb5b62d8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Another 19% down?What the hell?What are they doing?Can I get my five thousand back?No?Hey, forget me not!Is there something wrongwith your chart?Today's not April Fool's!Seems no one cares about us anymore,Miss Governor.If that is the case, I'll make your arms bleed, my lord.Will the audience beinterested then?The market's really dropping out of time.To accelerate theEveryone is exiting?The trading volume is more than 12 million shares!
```

### [20] hash=`47e96224ebcf970a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Hey you, my ass!Who has the cash?You tell me!Who has the cash?Let me out!I'm in a hurry!I need to go home!I'm killing people!They gave us a dam!It's too dangerous.Why doesn't Vertin use that blasting bombard ball?No, not yet.We're fighting up close here.Can't let the bomb give us away.fine enough fun for me if I don't kill you I'm afraid we won't be able to leavetonight it would be great if I met you and your rubble first and so we would
```

### [21] hash=`8e57dd65d74526da`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
have not forget it miss governor a deal for breathingI'm fine why are you behind the stage you seem well thank goodness thosewith which the Dow dropping more than 300 is not worth mentioning the world you live inyear 1929 of the roaring 20s is welcoming its finale and now i invite you to wait quietlyfor the finale to come be crazy oh what you're talking don't worry he'll be quiet for a whileHello?
```

### [22] hash=`423b2a76dd5a733b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Oh, the DAO closed at 2.30.07.I see.That's it, my friends.Wall Street has collapsed.And the storm has finally come.At first, it's a drop of rain you can barely see.From the drain, from the bottom of rubber shoes, from the milk about to be dumped,They become an unknown pond, as if trying to get rid of a pernicious habit.A pernicious habit of this era and society.What I said caused uproar in the crowd.
```

### [23] hash=`17257d29a1fc0293`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
And that habit will only grow like a mutation haunting every living body.In the 60s it crashed people into absurd cartoons.In the 90s, it turns our veins into cables.At last, all the absurdities will transform into a stormand eventually cleanse the world.Only the people who weren't sifted outhave the right to reverse with usdetails that couldn't miss Burton already begun.I finally got the answer.That's all for what we know about the storm.
```

### [24] hash=`00eb48693b627b9d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
And what our institutum does is to catch in advance any time, event, or place that maycause the storm.For ourselves, we call it chaotic energy.According to the latest research materials, we infer that the storm that could reversethe world was caused by the original butterfly, flapping its wings in the ancient time.The ancient time, you said?Is that the oldest of the oldest?Yes, because it's in the eye of the storm, in the Walden in Chicago, where your friends
```

### [25] hash=`38520e8c6eadcdce`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
are now.Let us wish her the best of luck.I finally got the answer.You were using the history to expedite the storm.Community conflicts, turbulent history, new technology, all of these may lead to thestorm.Since the last day of 1999, the world started to get reversed by the storm, one afteranother.Which past do you want to return?50 years ago?A century ago?Or...The past with the right order, of course.
```

### [26] hash=`3276102945c9cff5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Well, I didn't expect a human lackey to understand what the right order is.Friends of the Walden, all along, there is not much time for us.Ask yourselves, who will enlighten you of the impending doom but we, Manus Vindicte?You actually detained a human in your secret room.So, your first mission to join us Manos is...These government lackeys who hide the truth of the storm from you.Take them down.Are you really joining this insurgent organization?
```

### [27] hash=`9d47100f13ee4b7c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
He's using your fears!Miss Senero, we are scared, but we are free.You know what I'm talking about.The rioters are here.Be careful, there are so many of them.Ms.Sotheby, we're here.We'll have you surrounded.Please stay inside.Of course, Mr.Carson lied to me.It's time to show the power of our manner.Mr.Nesho, we are here to help.Everyone else, come with me.Let's break out.We've been waiting for this moment.
```

### [28] hash=`58c72b3168e3affc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Let's go!I...I'm going home.Let me out of here.I don't want any gathering.Screw the money!I'm leaving here, you lunatics!The door!Where's the door?The window?Did I go crazy too?It's too dangerous outside.Without our masks, you'll soon get infected with the pernicious habits of the era and be sifted out by the storm.I don't care!I don't give a fuck!I can never repay the debt of my lifetime!Let me go before I go insane!
```

### [29] hash=`5e7c11ba0b34d87c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
government I didn't do anything wrong I'm begging you help us don't be afraidwe will definitely timekeeper they've reconstructed the buildingall the exits are blocked become two civilians hurt already many masscivilians among our enemies the next battle will be harder we can't keepfighting with this we need to find a way out we'll protect everyone on bothWe've made an underground labyrinth in the speakeasy.
```

### [30] hash=`eb78864d037967c2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
The end of the labyrinth.What will that be?Timekeeper, Sotheby and I have explored here for a while.The overall area of this secret chamber is not too big, but many obstacles here can move.It's easy to get lost.I had drawn a map before, and the exit is very close in this direction.As long as it's near the outer wall of the speakeasy, we will be able to break through.right right mr.Nessa is exceptional okay then follow the night do not make
```

### [31] hash=`3c38403e6e8dee7f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
any noise I'll meet you soon I'll go get Marion I think I can find her she mustbe here is Schneider casting an arcane skill she's near us but why can I sensetimekeeper do you any questions about the plan no it's nothing you make thecall there will be many unexpected dangers in the labyrinth we need to movecarefully lots many forks ahead we're getting closer to the outer wall yes Iheard the sounds of the street miss Sotheby did you get hurt we didn't know
```

### [32] hash=`e75cb69fc8e9c30b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
there were so many ambushes no worries you carry Freddy and clean up theMia sorella, it's Schneider.Call my name.Don't you remember me?It's Schneider.I'll get you out right now.Hmm?Back to our citrus orchard in Sicily.Back home soon.You chased us here.Is it you?You are abusing this girl.Stop you!To piss me off.Sparisi.They force you to eat.Vaffanculo.Took the Truth Serum?I have memorized the formula.
```

### [33] hash=`be86102b0900822c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
The feel and smell of the liquid could confirm it.Let her lie on her back, right arm high.I will conduct first aid and get her to vomit up the potion.Be quick.Oh, we got company!We need to get out of here, fast!Stay focused.Don't worry, leave it to me.She will spit it out.Waffles!The new enemies are not something we can deal with.We have to get out of here.Please move out the way.This is very dangerous.
```

### [34] hash=`99e51d7d67d07a84`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Three rounds left, right, with the wing, but on the wheel.Get out of the hole while you can.This wall is about to collapse.Leave the rest to me.I weave the gown with thorns.You shall repay with sacrifice of wounds.Frost you with the armor of the forest.
```

### [35] hash=`71cabfa56d8a282c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Timekeeper...We can't leave Timekeeper inside alone.If we break the wall now, we can still...No, we cannot get in touch with Vertin yet.Without her location, they may get hurt from the blast.Black smoke!Watch out!We need to stay away from the wall.It's too dangerous inside.Some of us are feted by enemies' incantation.Then find the nearest window and get in.We may surround the enemy.Timekeeper must not be caught by the Manus!
```

### [36] hash=`7db0e149bac293f0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Look, bring all your weapons!If we break out together, with them!A group of masked men at the main entrance are rushing over!Oh no, they...We should go.What?When Timekeeper is absent, Chief Assistant Seneta will be the first in command.Going back now is like lambs to the slaughter.It will only ruin the last chance to rescue the Timekeeper.The enemy is after us.We are still in danger.It will only cost us more if we act on impulse.
```

### [37] hash=`c0d3ef0723c65839`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
But...Please trust the Timekeeper.She will do her best not to put herself in danger.And the Manners will also want to know why the Timekeeper is immune to the storm.We need to make a rescue plan as soon as we are safe and get her out.Copy that.Found them!The rioters are here.Miss Sotheby, the car once hit by the Heaven Apostle.Is it still working?I have no idea.It's also my first time taking the auto-island.
```

### [38] hash=`56b499c4e6d38802`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
I used to travel with Hippogriffa Shero.It still works, but the engine needs a moment.Because of you!Everybody, get ready to fight.Come on.We're all counting on you, buddy.Just a little bit.On!Is that the Great Arcanum?Next time, please teach me how to master it.sure no problem miss really he stepped on my scat well I have a lot of potionshidden here if they're broken I'm over thank goodness this apple doesn't take
```

### [39] hash=`fd853d18b298ba95`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
much space they're behind us the rear view mirror is really something let'smove everyone sit tight grab everything in your reach these are the words weSotheby and Miss Zanetta begins.Am I right, Miss Zanetta?Miss Zanetta?Are you crying?Oh.You're back, Miss Druvis.What you brought back is as satisfyingas expected, Miss Druvis.Is that right?What do you mean by right?They are not good people, Miss Druvis.
```

### [40] hash=`4bd1f2df3dad8a26`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
One is a traitor and the other a bureaucrat.You've done it right for all the blinded ones.I don't care whether they're good or not.I just want to know.Is it really the right thing to do?Of course not.Shall we meet Lady Vertina's equals at the conference table?Better treatment she deserves.I have been seeking a chance to talk to you from an equal position.The name is Arcana.Hello.The leader behind Manus Vendictae.
```

### [41] hash=`720f6382232f0ebb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Thou art acquainted with us.Lady Vertin, here is an official offer that you joinest Manus Vendictae.Why, I simply adore thy visage, emotionless in each storm.I adore that which shineth in gold, nestled in thy cranium.Miss Schneider, it is you who betrayed us first.Is that so, Mr.Forget-Me-Not?Seems we have never reached an agreement.After all, your promise was a lie from the very beginning, Miss Schneider.
```

### [42] hash=`c5a102c85623ccb0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
You should have known what was coming for you.So, what are the three questions?And how do you indulge in my suffering?Content thee, my child.The Foundation experiments on the orphans of Arcanists.Is this true?Yes.We are looking for the arcane antibody, immune to the storm.And I'm the only successful subject.And the name of the antibody is?Asymmetric Immune Protein G.People call it a lie.Thou shall not be misled by an abominable worm, Lady Vertin.
```

### [43] hash=`5cf9266348e66e15`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Or her limbs are not my next target.The last question.Only one who bravest the storm easily, the Arcanists thou hast met.I will join you.Very well, are they?Most of them are deserted.In the mental hospital, the correctional institution, the abandoned orphanage and the streets that no one sets foot on.We have been deserted by the principles of this world.As though we were born to be so eccentric and marginalised.
```

### [44] hash=`de130cbe8ba23db0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Thine eyes are not blinded, Lady Vertin, but venom pain them.Stand up, Miss Schneider.Both your right hand and left leg are injured.Lady Vertin, what do you think of her pistol?A great one.Exactly.Which was improved by our finest wand maker, Druvis III.I don't need it.And end her life.I decided to join you!Indeed.It is a mission, a new mission, showing our welcome to thee.Thou hast no right to refuse.
```

### [45] hash=`393ee33f1069ecbf`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Complying is thy only choice.Yet, Lady Vertin liketh not this, and nay it is.Have an orange.Orange?Why are oranges here?Schneider, how did you become so young?The friend that Mia Sorella said helping us pick oranges.Uncle Cannavale is going to transport the oranges to town tonight.Where?Where am I?The orange tree feels so real.The familiar scent.I'm here to pick oranges.Thank you for wiping the mud off my face.
```

### [46] hash=`7ffa44583580cb21`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
To help us pick oranges.Who says I'm not skilled?Observe.Let me pick up that big orange at the top for you.Just climb up here, take a small jump.My lord.You're forgiving Norton's back.It's a huge scar on her back.I think I just saw a critter.Didn't watch my step when driving it away.Well, that didn't take the arc, right?I often find them in the bushes.You often see strange creatures?Are you also an arcanist?
```

### [47] hash=`3a5ba12a1b18e6ce`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
I'm...The critters are making trouble now.Wait a minute.I will deal with them soon.What about the world outside?The future.Will you also come to town, Schneider?I have no idea, the United States many years ago, the blessing we give is hurting.Don't feel like it.I've been wondering, don't you think this orange tastes bitter?Shoot another one!In blood!Accidentally though, our new member is quite the sharpshooter.
```

### [48] hash=`2ff3fd27fdb2fd2a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Where are you going, Miss Druvis?To where I go.This body, thou hast any idea, Miss Druvis?Send her back to where she belongs, so that they know Miss Burton's choice.How long before we get to the manor?Miss Southerby, we've been driving for more than 40 minutes.A corner ahead!What's that shadow?It's moving!Waffle!That's the manor's vindictae's believer.Get around now!Don't let them see us!No!We can't turn around now!
```

### [49] hash=`2cfaf895c4f2d51b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Let's fight.Put an end to all that's happening in this ridiculous forest.We must not let the manors know where we are going.copy let's make it fast there should be no other enemies are you all rightdoes anybody hurt are you okay mr.Apple I got accidentally splashed by theslime it must contain a high concentration of toxins moldy theantidotes made from leeches glasses of blood black fern root and at least two
```

### [50] hash=`4c9f4954342004d7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
It's not a statue, a quiet, raven heart.The sorcerer and heretic...Oh God, forgive me, sweet Mary, mother of Jesus!What has flown over?God bless us!Don't be afraid!In time I have seen so many arcane creatures and plants for real.Now Geister, my father found it near the Blue Ridge Mountains in Braddock Heights.Don't worry, it no longer sucks human blood.It's my good friend now and to welcome you home every time
```

### [51] hash=`6055041835fc8fa4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Never allow this no one else, but us here.What mr.Apple just mentioned is it really mango carrot?I'm so sorry.I did not hear it clearly either need a small cut of his leaf to release venomHopefully the toxin will take effect slowerUncle said fungicide humans apply on plants not in the index starting with MsoCo-co-co-snuffing.How could it be possible?We should have all the potion materials in our warehouse.
```

### [52] hash=`c5994e719b7b1050`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Is that in Latin?What can I do?I promised to cure Mr.Apple!Did I hear something?Someone is here.This floor is a private storage area.Servants are strictly forbidden, and I never met any servant along the way.Around this corner, there's gonna sneak a peek, making no sound.Miss Sotheby, you're back.You!I'm doing the weekly inventory check.I apologize for not welcoming you in time.However, what happened to your outfit, my lady?
```

### [53] hash=`93848b533bbfdb34`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
The dust on your cheek, and where is the bow on your left arm?Why do you look like you just crawled out of the trenches?This is terribly bad manners.I hope that Mr.Forget-Me-Not and the high society you meet today will not think thatthe Sotheby's are a group of savages.The Manners?I don't understand.I assure you the manner has not been disturbed by anyone.However, after dinner, all the servants somehow got acute gastrointestinal inflammation.
```

### [54] hash=`b4a602090cca4275`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Your favorite gardener, Nick, is in hospital now.I was waiting for Master's phone call while they were having dinner.Don't worry, my lady.I have double-checked the food.I assume that it's just because of the inappropriate preservation.Coco CarrotIn the lobby!I see.Please, be at ease, and a decent meal will be prepared for your friends.A banana be stored?Corridor?Did you come out to the devils?Gotcha!
```

### [55] hash=`e67b9106b27b0a14`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Thank you, Alka, Miss Sotheby.Mr.Apple has applied the medicine just now, and Miss Marion found the medicine outside the garden's store room.There are still many Arcanists who are better than me.But why do you look so serious?This is...Come here, Ms.Sotheby.The manas has taken action.There is a large-scale disease outbreak in the city center.The news is on the radio.According to the Public Health Service, by 8 p.m.
```

### [56] hash=`f855e5d909c69a2c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
today,13,469 cases of asphyxiation deaths,2,283 confirmed cases of acute respiratory distress syndrome,and 181,002 confirmed cases related to gastrointestinal inflammationwere reported in 45 regions.Patients with the new disease have had such primary symptomsas swallowing difficulties, shortness of breath,and gastrointestinal inflammation.The disease is likely to spreadin the areas of residence where people were killed.
```

### [57] hash=`179b9f0174a38ce3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
It has not yet been confirmed as highly infectious.PHS Commissioned Corps has intervenedin food supply controland will report its findings as soon as possible.The east side of Michigan Avenue in Loop District,The Gold Coast Block in the near north side and the River North neighborhood are the most affected areas.We have also received reports from Evanston and Oak Park.Until the source of the disease is identified, we ask that general public refrain from eating at restaurants, cafes, bars and public places.
```

### [58] hash=`fb1aefc6d9d03ebc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
If not necessary, please do not visit major public hospitals in urban areas.More than a hundred thousand people are sick.Oh my gosh.You look so angry, Ms.Senetto.Are you okay?I'm fine.The casualties are staggering.How did the manas do that?These are obviously exogenous diseases.Poison?The inbox said that people who are sick would all have stomach pains.Gastrointestinal inflammation, right?But even the hypertoxic ash of Paradiction Tree can't cause such a mass casualty.
```

### [59] hash=`5321fb0b3df4f3f4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
And this apple's symptom doesn't include gastrointestinal inflammation.I have recorded the broadcast and the timekeeper's situation, and will report it to the headquarters now.Whether it is the solution to the storm or the plan to rescue the timekeeper, we all need instructions at a higher level.Apologies for interrupting.Is it time for dinner?Yes.Ladies and gentlemen, dinner is ready.May this wonderful night wash away our distinguished guest's weariness.
```

### [60] hash=`21bf3ac3aec0032a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
These are the appetizers.Or would you like me to introduce them, my lady?The 1919 Boitratai sweet wine Moulis en Médoc from Chateau Chasse-Bline.Creamy orange caramels with toffee pudding.Puffer pod in herring soup.Cream of watercress soup, oysters with mignonette sauce, and dill aromats.What do you say is in the bowl in front of you, Mr.Carson?What is it?Cream of watercress soup, made of wasari, blue cheese, watercress, fresh shellfish.
```

### [61] hash=`2c151c6a4bf38a08`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
If there is anything wrong with the cuisine, please let me know, my lady.What's wrong with you, Mr.Carson?These are not for dinner, not even food at all.Miss Vertin doesn't seem to have any appetite.Or do you too wonder how gold bar steak with wineand boiled silver coin tastes?Storm syndrome.That's how you call these pernicious habitsfrom the old society.Sounds like the foundation are so satisfied
```

### [62] hash=`886b348dc4d87a00`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
with how the old society worksthat you call the current situation a syndrome.The storm syndrome turned money into foodin people's eyes.It's so ridiculous.How did they eat those gold bars?It's not easy to cut them off.Of course not.Gold is no meat or vegetable.But humans, yes, they are impressive.They had somehow worked out a brand new set of tools dealing with the new food.A para that can pare the rough surface of the gold like a potato.
```

### [63] hash=`21ed4afcf8cfa032`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
A spray gun that can melt bullion within seconds.For paying.In the storm, the thing that dominates their lives is still money.How could it be more ridiculous for the time?Why do you blame them?In the storm, there is no life.You look very sad, Miss Burton.I do not understand.This burnt branch should have come from a rowing tree, right?I have seen this tree in Ireland and South West England.It is often called quickbeam, derived from Old German.
```

### [64] hash=`d7a7158c959b386a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
means stay alive.Rowan is full of vitality.Even if it is transplantedfrom Europe to North America,it grows vigorously and stretchesinto a vast forest.In the most dangerous days in the Celtic calendar,people wear garlands and berriesof Rowan to pray for its blessing for vitality.However,an unexpected fire destroyedall of them.Just like the storm,it's there for no reason.I suggest you stop talking.Like this branch, whose life was brutally terminated.
```

### [65] hash=`2c38fa32c534da87`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
They worked out new tools.They tried to eat these soft and gold bars,and sold the food that's no longer valuable.But it's so hard to understand life with their own logic,because they just want to live as much as possible,but not go back in time.Watch your mouth, Furtin.Going back in time?Why isn't it real life?Is this little rowan branch really alive, Ms.Drus?You've used Arcanum to keep us from the moment when it was burned.
```

### [66] hash=`b3dcd18fce61e1d3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Once you dispel the Arcanum, it would not be what it is now.I think you are clear, Ms.Trevis Thun.Every tree lives for tomorrow.Enough!How abominable!This is not where you can give your speeches and such cliches.Since you're still being such a bureaucrat,why not let our believers help you get used to the Manus Mannus?You should not touch others' belongings.Look what you've done.Rowan was often planted next to Welsh cemeteries because it would guide the deceased to the next life.
```

### [67] hash=`920cc0914d330b30`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
So as not to stay in the world and haunt the living.But I was hoping the Arcanum is dispelled like things being touched by others.Take it away.Alright.You've treasured it for a long time.Is it alright to just give that to her?You asked me to stay.Is there anything you would like me to know?Yes.I've received an instruction from the guiding one.Our next plan concerns you.Follow me.It's a nice view here.
```

### [68] hash=`0843af480710cdaa`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
Indeed.Where your woods can just be seen.Are you here to ask about my decision?We had negotiated with the local government.They are very interested in your woods.Because of the storm, the medical supplies cannot meet the needs of the surging number of patients.They need places to house the patients and refugees.Your woods are the best choice for its abundant space and adaptability to cast the healing rituals.
```

### [69] hash=`0b9f4c904d4f9623`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
So, have you made up your mind, Ms.Truvis?Always welcome to join us, Manus.If I join you, will you reject the government because of me?We have a better plan.In the woods, they're going to build the only major relief shelter in the city.Arcanum will be used as the main treatment here, which means food, resource, money.And everything necessary to build Manus Vindicte.We've reached a consensus.Nobody can offer a better assistance in the field of Arcanum than us.
```

### [70] hash=`04a7ceb860f5ea74`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
What about those refugees?Only those who are sifted out by the storm.You will not.You have my word.We hope that on Relief Day you'll show up as the owner of the woods and offer your help.I am no longer the owner of the woods.For as long as you need, I will transfer the ownership to you at any time.Not to mention that the one and only owner of the woods is you to the end.What you once had is what I should have.
```

### [71] hash=`d73a30f663830ddd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
I will look after the woods for you till the moment we start the relief day plan.Thank you for tomorrow.Not enough bullets.Cover me, my lord.Your wound hasn't healed.Can't get hurt anymore.Stay behind me.This is a cage.She wants to catch us.The exit at two is our last chance.Break through!No, my lord.It's too late.It hurts!The slime on the thorns will make your body stiff.Be careful.All retreats are blocked.
```

### [72] hash=`0ecb805ed35f3d5b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
No.We can't be trapped here.Let me try again.Give it up.It bounced back.How?How was the thorn cage so tough?It's over.Dammit, why?You are not pure blood, right?My lord.I'm not sure.You are like me.Crappy guy is not good at Arcanum.Don't you see it?Pure blood Arcanists and we are worlds apart.It drew this.You know it.When you push out the old woman in white, you should have figured it out.No matter how we struggle, it makes no difference.
```

### [73] hash=`88023c0af234f0b6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p4`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜1~7）

```text
We will be sent to Arcana.There must be a way.It just takes time.You are braver than most people I've ever met, my lord.But it's not enough.Far from enough.When it's time, please kill me.What are you talking about?Left of my chest, the Manus will not let us go.Killing each other has always been their favourite.You are much more important than me, my lord.Cherish your value.I don't understand!remember left of my chest it quick it's too risky and if you want to survive no

choice me my lord I cherish my life more than anyone but what you said she sheheard it all her destiny is her choice
```

### [74] hash=`7ca3f969ca0ba7fc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
The second, the first, and underground.Altogether three secret chambers in the speakeasy.The remaining material rooms, study rooms, and corridor on the second floor cross out.The most likely place to park Schneider should be in one of the rooms on the other twofloors.It's a pity that the patrolman could not be confirmed.I'm afraid a battle will be inevitable.Bring the healing potion, other potions, medical equipment, food, masks of the mannus,
```

### [75] hash=`684df1386ca6dd2b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
and the Rowan branch sprouted,the symbol of protection and blessing.I'll take it, go.It's weird, it was a straight path when investigating.Someone's coming, I should hide from them.The Rowan branch seems to be pulling me.Does it want me to choose the path where they are?Okay, then I'll wait for them to go over.I saw my grandma in the entrance of the hospital.She choked on cashAnd was carrying on a stretcher.
```

### [76] hash=`ac708ad790139541`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
She can't even recognize me.It's nothing, Mr.Thomas.My son Robert's dead.I heard it on the radio.They had just sifted out by the storm.Not as lucky as we are.I don't understand.Three hours before, you're still crying.We have to accept all this.Accept that the dream of our new age is broken.and the fact that we have to fight against the government tomorrow.Fight against the government?Yes.Mr.Forget-Me-Not told me so.
```

### [77] hash=`96efbacacf213373`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
We need to deliver tons of goods to the real sanctuary of Manus Vindicte.Our safety is not fully guaranteed, even with the masks.Only in the sanctuary can we hide from the influence of the storm.And then we set sail anew to the new age, to the new life.Just like Ms.Vert-Teen.Oh!What are you talking about, Mr.Robert?Your hand!With the black slime!Smasters!I gotta find somebody!Both his appearance and voice have changed.
```

### [78] hash=`2f49ca71d8cc353b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Just like the believers who can't talk.Is it the mask?Or arcana?No, I can't stay any longer.I need to pass through here and go to the underground before anyone else comes.Mine hands, thine order.I'm Vertin.A follower like you.Please let me pass.He can't be talked into sense.Is he moving just by instinct?I can only stun you first.Sorry, Mr.Robert.Footsteps.At least five or six people.I should go downstairs quickly.
```

### [79] hash=`80b560cfa327c830`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
The underground.Another turn-off.Are you really showing me the way?Then I'll go left.So close.Just avoided another group of guards.I don't have much energy to talk, my lord.I just want to know, who of us is last choice?I didn't have the chance to talk to her alone.But I think, since I can meet you now, maybe...Blooming.Maybe she shares the same dream with us.Schneider, now you need to save your strength.
```

### [80] hash=`0a1e0ca63321bc58`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Don't open your eyes until you meet Sinetto.I'll see you in the relief shelter.To publish the lab results of the 42nd trial of the choo-choo hallucinogen number threeWhat you saw the Madonna?DaggerPortland cement blocksTaste like cement tooTwine and scissorsPineapple cherry tomato pizzaGlen Miller's trombone electionMiddles?Is that here?The body of my dog in the trench?Gosh, really sorry Mr Carson.
```

### [81] hash=`57cda2c6c106e4ec`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Still need to improve, improve!Turns out the storm syndrome can distort all these senses about foods.Working up an appetite with hallucinogen is harder than I thought.Miss Sotheby, we have to hurry up.The longer they can't eat, the weaker they get.Receive the message from the patrol team.Followers are around the manor.We must be doing something bad!Ms.Sinetto, have you heard from the Foundation?Not yet.
```

### [82] hash=`107c36929520c2a4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
If the instructions are delayed, I'm afraid I will implement the backup plan.To rescue the Timekeeper is the primary goal.I'm afraid that reality fails you, ladies.Followers!That black suit.The feathers.Schneider?That's my sister Schneider!What happened?The blood everywhere!What happened?Death, of course.There are many bodies.She's the only one to go home.Just for you to know.It's our Miss Vertin's decision.
```

### [83] hash=`7570fccadf0bd3dd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Let me check.The scar on her chest has no sign of slime.Miss Vertin's already one of us.We share the same blood.That's an incredible gunfight.greater than any of you have seen last night believe it or not check the scarson the body they're like sparkling pearls on the beachunforgivable how can there be someone who spoke such rude words and insultedthe deceased and the timekeeper like this may the peace be with us the
```

### [84] hash=`e19db662743ccf81`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
enemies are cleared good fight old woman avenge me fiercely even my stoneYour heart will be moved.My sister!Jesus and sweet Mary!How did you get these bad injuries?Where is the timekeeper?What happened to you?These are not important in your heart.There has been an irrevocable answer for long.Look at this flower.Look at every word on it.And I can see this.She passed out!Take her inside for emergency medical attention.
```

### [85] hash=`dcff08771706cd73`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Listen, agent number 9 is almost there!Please mind your step and don't forget your manners, my lady.Ms.Sonnetto is at work.Do not disturb her.Yes.Sonnetto received.We are on our way to the relief shelter, close to the woods.Long story short, our agents in Washington reported that all the relief supplies are being delivered to Chicago.What the menace wants are those supplies, so you need to adjust your plan.
```

### [86] hash=`23a524653634f39a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Our first priority is to stop them from grabbing the supplies and to rescue the refugees.There may well be a tough battle today.Just in case, we will send you some fresh crews.What about the timekeeper?She knows what she is doing.You will meet when the mission is completed, Sonnet.Understood.I will do my best.Thank you for what you have done for the well-being of mankind.Looking forward to the good news.
```

### [87] hash=`7316534d4c71ebae`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
The walls are locked.Go back, give her non-transport staff.Of course we are the transport staff, though the direction we're going is different from yours.Now they've arrived, I feel a lot more awake.Everyone, please lend me your strength.Let me see, Mr.Forget-Me-Not, so you and the man who's gonna work with us?Exactly.Show me your physician's license.Are you good at clinical diagnosis?How many patients have you seen?
```

### [88] hash=`7d4f3719d032e440`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Sir, I'm an Arcanist.Oh, aka con artist, right?I was invited.You've already prepared the crucible and the materials I need.Why bother asking me?What are these numbskull chiefs thinking?What can this freak do?Plan house with some rotten roots and toad?Isn't this Mr.Forget-Me-Not?Fabulous.Such a relief that you're here.We haven't had any food for a whole night.We're starving and can't stop thinking about eating.
```

### [89] hash=`104318a545d72604`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
I don't know.They say it's cash.Don't worry.I promise everything will be okay, Mrs.Durant.You will definitely treat people in the white tent zone first, right?For the love of all the great party times we had.We couldn't take any more of these.So, there are other zones here.Then who is living outside the white tent zone?Only God knows.I heard that it's a bunch of tramps and vendors.I've never seen them before
```

### [90] hash=`fd1aec4ba5d7ed93`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
howeverDistinguished lady you look very familiarHave we met somewhere before?I'm afraid you made a mistake madamStop dawdling since you're here to save lives hurry up then thousands of people are waitingKeep silent when I'm making potions, sir.Yeah, pretentious.I'll check 30 minutes later.See what the hell you're up to.You're surprised.He's just another stupid human.Enjoy the peace before the storm.
```

### [91] hash=`85f3564aa44ad070`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
These powders are not poisonous.Also, the potion he's brewing doesn't do any obvious harm.It smells nice.Even like, why?Does he really want to treat the patients?Impossible.Get out of my way!Where did they hide the medicine?Tear it!Tear it apart!What are these boxes?I can't take these!The relief supplies of the service corps!It's the Quilt!Who wants this shit?Relief supplies?So that's it!Lots of reserve food and oil, medical supplies, emergency supplies and temporary
```

### [92] hash=`10b099b782c8c755`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Give me that other people will be attracted here.I need to take him downSorry take a restYou can no longer waste your energy like this.Are you running away?It's true thisNo, I'm picking them upThen you should not pick this way.Are you still as lost as you were at the beginning?It is heavily guarded in the frontThere are more serious crises than just nowEven so, are you still moving forward?Until we see tomorrow, our own eyes.
```

### [93] hash=`9c44146edd432184`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Will you come with me, Drupis?Your friends are on the way.I see huge engines are roaring towards here.What we desire is being removed, what we despise is being rescued.But our enemies are still increasing, north to south, from east to west.The storm is coming.I accept your invitation, but this is a formal farewell.I need to see my woods one last time, and engrave it in my mind.Good.This should be the third transport truck we seized.
```

### [94] hash=`c814ab1140a62d6f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
In order to avoid attention, the manors reduced the number of guards for the supply transport.They must have never expected our attack.Captain, lead the team to escort the three vehicles back to the manor.You and the others, follow me to the relief shelter.Copy that!It is hallucinogen, my lady.If you are confident, you can pour it into my mouth.Thank you for being my experimental subject!Action!You don't want to eat gold bars!
```

