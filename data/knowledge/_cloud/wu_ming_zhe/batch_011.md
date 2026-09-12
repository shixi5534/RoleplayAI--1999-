# 剧情图谱抽取 · batch 011

- 角色：`wu_ming_zhe`
- 批次：**11** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「忧郁的热带」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_011.jsonl`

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

### [0] hash=`799c80ad9bf150b6`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
invitation.A succubus should follow her instincts.Come on, obey your master.You know, you were close, Kimberly.You almost found it.It was hidden at Tuesday's motel, just like you thought.Stefan thought it was just a wind-up toy what a fool yes that's the spirit comewith me and I don't he's not going to give it back to you oh so you'd ratherstay with the timekeeper I guess you need a little reminder of who your
```

### [1] hash=`b97b74d8ad099cbb`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
real master is soldiers prepare to fire pick it up timekeeper I hold noWant me to kill...Ten?Come on.My patience has its limits.You will obey me.Do it, demon.Your freedom for the life of a stranger.Yes!Kill her!Prove your loyalty!Then I'll give you back your toy.I promise.Raise your gun, Timekeeper.Aim at her and pull the trigger.this monster is going to kill you you'll have to shoot her if you want to live
```

### [2] hash=`375986c01b722c91`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
obey your master yes give in just like that look Kimberly she picked up the gunshouldn't you kill her before she kills you she obviously values her ownlife over yours and she won't hesitate to fire a bullet through your heart toYou're just a horrifying beast, I mean look at you, you're a succubus, a demon born tobe bound to a master, born to be controlled.If that's what you want, then kill her, break her neck.
```

### [3] hash=`21fc013a5d5412fe`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
Now heed my order, and kill Verten, end your suffering with her death, don't think,just obey.How dare youLooks like negotiations off the table timekeeper.I suppose I'll have to turn to violenceSoldiers kill them allSpare no one but KimberlyShe's the only one the admiral needs.I'll kill one of you.What kind of monster is she?Maintain formation and fall back keep firingRetreat everything will be fine Kimberly.
```

### [4] hash=`d7c8dea8ce8e0b24`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
I'm here.It's okayYou're going to be alright.You're no longer bound by anyone.No contract, no seal.The wind-up toy's been destroyed.It's been shattered into pieces.You're free, Kimberly.You don't have to take orders from anyone anymore.Kimberly doesn't have to take orders?Nala doesn't have to take orders?Come.If you've got nowhere else to go,You can come to the Foundation with me if you like.I'll let them know you risk your life to protect me from the Xeno Rebels.
```

### [5] hash=`ce6d6d05e98fed0c`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
Anyway, the choice is yours.And choose?Yes, whatever you want.No one can control you anymore.You belong to no master, only yourself.To myself?Like when my sister died?The first time I left home?Like when I fled to Sao Paulo during the war?and, in return, receive mine.After all, this city and its false era will be washed away by this storm before long.Those poor unbelievers.We were all once like them, yet to realize that we are children bathed in the light
```

### [6] hash=`4faa6568aaf31dbb`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
of the divine.One day, they will turn from darkness to light.Just like our Xeno friends did not long ago the apostates howeverThey who have abandoned our faithThey must dieI'm still curious, you knowAbout who attacked the manor who disturbed the meeting between the Apostles Brotherhood and the messenger of the great manners vindicteWho came here?At least Manus Vindicte promises these soldiers a future, a future worth looking forward to.
```

### [7] hash=`d36985140485b91a`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
The sufferer will be reborn, and the Apostles Brotherhood will sail south with me.We will become followers of this sufferer, undertake their trials, and their grace willbe bestowed upon us.The world is reversed.We will seven maybe eight guards.No way to get throughWait, Mary.I finally found you.I bet you didn't expect to see me here.Did you?Duncan, how did you know I was here?Keep it down nowOur friends at the veterans residence told me everything
```

### [8] hash=`6740822a6ed48746`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
The timekeeper said you were going to the manor aloneWould you look at the beautiful coronary?i'll head that way you stay hidden in the woods and make your way to the other side lead them towardthe river let's make this a little more exciting shall we boys nice shot ah it appears someone hascome to your rescue dear lady i'm not surprised i should have put a bullet in your skull back onthat sheep i'm afraid you're playing the wrong game now oh yeah so what does the winner get
```

### [9] hash=`8b9bbfaea00187ed`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
Just as it brought you victory in that bet.The puppy wishes to come along.Rubble broom, kiss the face.The puppy agreed with your decision.Blood can only be paid in blood.Crucible.He agreed with your decision.And it is blood and gold that stain this land.I'm tired of playing this game of prayers.And I've had quite enough of you, little gumbler.Looks like I win again.Yes, Anitra.I'm afraid there won't be a table left to play the next.

So long, it took time.You paid a little more attention to your friend.We can talk after we get out of here.
```

### [10] hash=`20eaf4490be43d08`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Eliminate all hostiles.Find Lopera and Dr.Doris.Brotherhood Guard's gone.Molly!Pera!Thank goodness this tracker button still works.What happened in the chapel?I had a fight with Santos, but he got away.Weren't you supposed to go to the veterans' residence?Rescuing the doctor is our top priority now.I am so glad to see you safe, Doctor.Great job, Pera.Let's head back to the base with Dr.Doris.What about the timekeeper?
```

### [11] hash=`8eae421f3947aaa6`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
She's on a new mission assigned by the Foundation.It's got nothing to do with us.Father wants me to bring you and the doctor back to the base as soon as possible.What do you mean?Why this sudden change of plan?What's going on here?Just come already.We're evacuating Sao Paulo.Evacuating?To where?Just follow your orders, Lupera.The Admiral sent me to pick you up.Then why didn't he tell me any of this?
```

### [12] hash=`77c5d5757d97daf6`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
I don't know.I'm sure he has his reasons.We're heading south.To Tierra del Fuego.They've made preparations for us.Come on, Pera.Come with us.You, me, father, telling me...Everyone will all be there.Everyone?Why didn't anyone tell me about this?Because...Pera, you can ask questions later.We don't have much time.No.Why are we going to Tierra del Fuego?And why are we running out of time?What are you planning to do?
```

### [13] hash=`06747d15f211c0ca`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Waiting for you in Tierra del Fuego?Who's behind all this?That jerk, Pálemi?No.Father gave these orders.Come on, Lobera.Lower your gun.Father needs the doctor.We need her.Bring her back to the base and come with us to Tierra del Fuego.Why?What are you going to do in Tierra del Fuego?Seize the future.A future for all Arquinas.Father has embraced the preacher's promise.None has been dictated.No.My family are not traitors.
```

### [14] hash=`ad10c8734c5ea066`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Look, you don't have to do anything for them if you don't want to.Just come with us.Come home.Forgive me, Pera.Tell me what you've got.What's going on?It's Pa planning to do.What about you?Are you going to kill Father and me?Like you did those traitors?I...I got some trouble for you.Get me some tape!Drop your weapon, Pera.It's time to come home.Why didn't Pa tell me his plan?He doesn't trust me, does he?
```

### [15] hash=`59210e313ff2e16e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Did you come here to take me home?Yes.You're lying, Mommy.We never meet.Most of the time, anyway.Enough is enough, Pera.You're wasting our time.You mean the time for your scheme?Making the Doctor back is more important than me, right?No!Pera, I want you to come home with me.You call that a home?With a traitor for a father and a sister who doesn't even trust me?Cristobal, why is he doing this?For the good of us all, Pera.
```

### [16] hash=`73100c599e4d542c`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Consider your mission complete.I'll take over from here.Thank you for your service, comrade Lupera.What's going on?I'll handle this.Take the blind lady and retreat.Make sure she is safe.I am sorry it has to end this way.Farewell, Pera.Has something gone wrong?Wait a minute.What's going on here?Xeno soldiers?What are they doing here?That's the doctor, isn't it?Why isn't Lupera with them?tranquilizer bullet oh I see it's shattered oh long have you been planning
```

### [17] hash=`84915974499dccb5`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
this am I really the only one who knew nothing about it was I ever actuallyaccepted into this family timekeeper yeah why did your men leave you hereAnyway, are the aircraft ready?Yeah.Father and the Doctor will be boarding soon.Who is she anyway?I don't know.Looks like Father hasn't told you everything either.You should never entrust all the pieces of a puzzle to a single hand.All this time with Father's made you quite enigmatic.
```

### [18] hash=`0d7fec7bb6677b2f`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
There's a charm in mystery, you know.Are you not coming with us on the helicopter?Someone has to stay behind and organize the retreat.You go ahead with Fazer.I'll join you later.Sometimes I just don't understand you, Moldeer.Oftentimes I don't understand myself either.Perhaps that's why father always keeps me close.Just get going.I'll take up the rear.We're under attack!Don't get entangled with the enemy.
```

### [19] hash=`b472e249c7166d4e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Focus on the evacuation.How many hostiles are there?Three!And a sailboat!A sailboat?What is this?The Age of Exploration or something?One of them is flying some kind of aircraft.Oh, she's fast!Two squads are currently engaged with her in courtyard A2!So, you're just going to leave me here in San Paulo, huh?Where's Igor?You've grown taller since we last met, dear little sister.Whoa, whoa!Don't look at me like that.
```

### [20] hash=`aef3031c19d4ccd5`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
I don't care what you do.Come home or stay with the Time Keeper.I won't stop you.Get out of my face.Molly?Miss Maldia.It's unfortunate that we have to meet again under these circumstances.We've simply chosen different paths, Time Keeper.I suppose the next time I see you, we'll be in Antarctica.The enemy go join father I can handle this Molly why forgive me I can't letyou pass soldiers take aim what on earth is Eagle trying to do we are soldiers
```

### [21] hash=`63d0333e9ffb7429`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
it's our duty to follow orders not question them Molly hold the entranceat all costs they must not reach the Admiral target confirmed ever want to seeand Miss Eart as well.No, Admiral.Not you.Us.We all need the miraclethey bestow.My men will not wear the masks.Nor will they take thetrials.We needno trials to test the loyalty ofmy children, Preacher.And for now, MissEart will stay under my protection.
```

### [22] hash=`3e22599d6cf82b85`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
As you wish.Until next time, Admiral.Father, I shot at Lupera.I have to be honest, Father.I don't fully agree with your decision.At least not on a personal level.You are entitled to your opinion, Lieutenant.But I don't need your approval.I understand.You only need my opinions.Precisely.Had you anticipated that Lupera wouldn't come with us?Now, bring me Dr.Doros.Father, I don't know you, sir.You must have mistaken me for someone else.
```

### [23] hash=`ef9348a75b125798`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
No, I couldn't possibly mistake you, old friend.In the last days before the Millennium, we fought side by side.In hindsight, that battle may have been a mistake.The storm swept across the world.Leaving behind an era of chaos, and we lost our future.But now, another path lies before us.One that we once fought desperately against.A path paved by Arcana, a path leading to a world free of conflict, my old friend.
```

### [24] hash=`1840eb0b8bf48d6e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
That marble chair the Foundation gave you, was the secret behind it?What happened to you after you pressed that button?Nothing.Do you remember what happened after you walked into that White House?I'm sorry.I don't know anything about that.My dear Miss Earth, your name continues to show up between the occurrences of thestorm.I don't know what you've encountered, what you've experienced in all this time.
```

### [25] hash=`7c51fb2339b47b1d`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
But your very existence is about to change the fate of us all.You have some news you'll be happy to hear.Trust me, you'll wish you had more than a minute for this.It involves a mutual friend of ours, a long-lost acquaintance you've been searching for.crucial part of another wicked scheme of which our dear admiral is well aware an orchestra withouta conductor can barely play a symphony recognizing that missing vital piece the admiral seized the
```

### [26] hash=`0dfc0dda4918f2ca`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
opportunity without hesitation experience gives a veteran his scars yes but also a scrap ofMiss Sotheby, I heard about what happened in the favela.Thanks to your efforts, Zeno has been able to recruit a new group of spirited youths.Mr.Duncan, we need to record your information and cross-reference it with that of Mr.Carson, who was lost during the storm of 1929.It's bewildering, isn't it?How could that be another Mr.
```

### [27] hash=`4aa0479b6fd6569b`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Carson?1929?Please come with me, Mr.Duncan.It won't take long.After that, you'll need to initiate the procedures for your re-enlistment in the Xeno Arms Academy.While the said procedures are underway, the rehab center will take care of the injuriesyou sustained in Sao Paulo.Welcome back to our cause.There have been many cases like yours.Politicians, singers, the list goes on.The Foundation compared them to photos from the 90s.
```

### [28] hash=`9f8714485bad3c24`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
While their appearances had changed, they were undoubtedly the same person.Hey, isn't that Lieutenant Lillia?This is an alcohol-free zone, Lieutenant Lillia.Please try to follow the regulations.Oh, did I just wander into another dry zone?Great.So many rules and regulations.Oh, how boring.Has Lopera arrived?She's in her room right now.Burton managed to secure her some rest time before her interrogation.
```

### [29] hash=`e55f0242a512e316`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Poor girl.Honestly, no one deserves to go through what she has.It's even worse than being cooped up and buried in paperwork.Clerical work is essential, too.Well, good luck, Comrade Duncan.Don't forget to stretch your hand between signing papers.You also need to write a report, Lieutenant Lillia.Our executives are quite curious to know how you managed to escape the rebel's custody.Moldeer, the woman in charge of the base, had one of her guards release me.
```

### [30] hash=`62c2aa845acafec1`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
You mean to say that Moldeer, the lieutenant who's joined the rebellion, set you free?I think so.At least that's what the guard told me.Lieutenant Moldeer asked me to help you.Take care.I'll be sure to make note of that.And of course, please specify this in your written report as well.This is very important, Lieutenant.If she's having doubts, then we may still have a chance to win back Igor's rebels.
```

### [31] hash=`a2ed1f2af9189a82`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
Or at least some of them.Igor fooled us all with his rebellion.It's been confirmed that the Dr.Doraz he took is none other than Ms.Erd.The motives behind his actions, however, are still unclear.While only a small number of the Xeno soldiers chose to join his rebellion,I believe it is necessary to urge the Xeno Arms Academy to strengthen the discipline of their members.No need to worry about that.Xeno will handle it themselves.
```

### [32] hash=`62eda431a7406e1e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
If that's your judgment, then I have no objections.On a separate note, Moth, our mole planted within Manus Vindictae, has sent us somenew information.The Manus are sending supplies, personnel and weapons in huge numbers to the south.It appears our suspicions were correct.Manus Vindictae is preparing a ritual to draw forth another storm.The location of Jerry Wilson provided by Miss Lucy confirms that the Manus are moving
```

### [33] hash=`8e55301f1c3b41be`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
toward Antarctica.Additionally, it's now clear that some of the arcanistorganizations, including the Apostles' Brotherhood,have been assisting the Manus through criminal activities,such as smuggling and human trafficking.All very valuable information.How is the Timekeeper doing?She's stable.It's worth noting, however, that she brought backa succubus from the Manus.She requested that we revoke the arrest warrant
```

### [34] hash=`70e8ab569c18d481`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
for the succubus and grant her all the rights enjoyedby Team Timekeeper.In accordance with the Storm Reformation Manpower and Discipline Act,I've consented to her request.Excellent.She's the ideal person to keep watch over the succubus.Very good, sir.About Igor.The late Admiral Igor of the Zeno Arms Academywill be duly honored in the Headquarters Hall of Merit.His great achievements and remarkable
```

### [35] hash=`061904bfcbfb5ebf`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
service, deserve to be remembered.That's all for now.London, Lima, Aswaiya.A report from Columbia.The mugshots of Pablo Emilio Escobar Gaviriado not match those archived.Similar anomalies have appeared for other notable figures.Why did Igor abduct Ms.Erd?And why does he want Kimberly?And where are Igor andgoing why did they defect mr.Carson who was reversed by the storm of 1929 hassomehow reappeared in 1990 or maybe there's more to it could it be that the
```

### [36] hash=`b2a7dcd8e3da59a3`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p75`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 20~24）

```text
storm doesn't kill people at least not physically one two three shots onTarget.Two.Three.One.Two.Five.Betrayal.You planned to kick me out right from the very beginning, didn't you?Or did you never even trust me in the first place?This awesome kind of game to you?Molly?
```

### [37] hash=`ba23174d84eefd98`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p10`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（10.【白色航船】）

```text
Listen up.We're the Apostles' Brotherhood, not some worthless favela gang.So we start off nice and easy.And if the talk doesn't play along, well, then we make her play along.Claro?Hola.How can I help you, gentlemen?Hey, is she really blind?I'm afraid, yes.But please don't worry.I'm more than able to treat all my patients.Sounds like some kind of explosion near the clinic.Should we go back?It could be an accident, but she's got away with her equipment.
```

### [38] hash=`61f7d800d1479df5`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p10`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（10.【白色航船】）

```text
Doubtful she's the cause of this.Steady on, then.Let's hurry back and see for ourselves.Ah, ah.That's not how you treat a doctor, lads.What are you doing to her?Lord Santos would like to have a word with the doctor.That's all.You're not taking her anywhere.See, she's taking care of this girl.Yeah, I'm not asking for permission, sweetheart.Gratis, doctor.Iced the rest of them.Enough.I won't have you fighting in my clinic.

But they've got the girl, doctor.This lady definitely isn't from the favela.So what's she doing here?She's ill.She needs my help.That is all I ever ask.
```

### [39] hash=`5fe9e2a06cfd907f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
You're a clever one viejo.I like working with your typeMuch appreciated.I've tried to pick up a thing or two over the yearsYou've had plenty of time to learn a man of your ageBy the way, what about that girl?Where does she go?Don't know maybe got scared away.You know how little rich girls areI'm certain she's found her way back to her daddy's bodyguards.She'll be no cause for concernEnough snoring syrup in the wine now to put them all in a dreamy deep deep sleep
```

### [40] hash=`5fc3b69c3711dbd5`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
Stronger effect if I had included a dash of slumber bella donna in the recipeThis will be more than enough little lady.We only need to get them to drink the wineThen drink this just a dropIt will stay on your tongue and prickle around in your mouth.That way you won't drift off like the othersI've uncorked it much tastier potions before, but this one...It'll do just fine.Thank you, little lady.Pass me the wine and wait for my signal.
```

### [41] hash=`f79f3efa40c3e2f0`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
When you hear me playing this flute, you'll know it's time to strike.The wine's here!Courtesy of an old friend from Mexico!Take a glass, everyone!Here's to his reverence's good health.To his reverence's health?To Marcando!To the invincible brotherhood!To Marcando!Duncan, that's your flute.Give it over.This is a fine flute.Duncan, did you...you said that you got a friend in Mexico?You know that old Mexican song, La Llorona?
```

### [42] hash=`b13110f47ef485f9`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
That I do!I learned it from the best, in the cactus back in Tulum, from a fine young lady with silky hair and gentle eyes as dark as coffin.Claro.So, uh, how fine was this chica, huh?Don't let me start spinning that yarn.It'll be no fun for you to watch an old man bursting into tears.I'll only say I was heartbroken by the time I left.That love of mine.Anyway, enough about the old flames of yesterday.
```

### [43] hash=`4dca2d367979d8d3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
Let's raise a glass to a better tomorrow.To poor old Duncan.Good.Good music.Huh?Who?Who are you?Lopera!Galeno!Come on!Give me a hand!Pinchy traidor!Time to cash you out!You'll be...be begging...for Lord Santos' mercy!Be reasonable, kid!The Brotherhood is finished!Your time's up!Don't let them slip away!Let me...Think you can handle this?Yeah.For the favela...The Brotherhood must go-Sorry to put you through all that, kid.
```

### [44] hash=`488b8ee359c027ed`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
Don't mention it.If this means we can get rid of them for good, it'll all be worth it.So what's next?Next?Zeno will come around to pick you up.But first, we've got to get back to the veterans' residence.No, señor.One of you has to stay.The people need to see you, or they'll worry that you've deserted us.Ms.Sotheby is never afraid!It's decided then.Lopera, head for the veterans' residence.Tell them what happened and contact Admiral Igor from there.
```

### [45] hash=`91ac281d7f39a9e7`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p11`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（11.【圣保罗舞曲】）

```text
Galeno, you've done us proud, kid.If I were king, I'd have made you a knight.Who knows?Maybe the little lady could do that for us.But first, young Galeno, we'll seek another deed worthy of knighthood.It's time we fight for our people
```

### [46] hash=`fe1cf748458af824`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p12`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（12.【“平安夜”】）

```text
You ever been to a veteran's residence?Not many young faces there.Besides Lopera.As far as the doc goes, doubtful anyone knows her real age.And even the saltiest sailor knows better than to ask a lady her age.Oh, I see that joke missed the bow, so to speak.No, no.It wasn't a bad joke at all.Really.Aye.Thanks for the kind words, lass.Hopefully, we'll see them soon.You know, I knew a girl who looked just like her, a caregiver here way back in the 60s.
```

### [47] hash=`e36681f022a184c2`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p12`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（12.【“平安夜”】）

```text
Back when this place was called Heartfelt Home.But it can't be her now, can it?Besides, I'm old now and my memory is a bit fuzzier than it used to.May I see Dr.Doris' room?She wouldn't mind, but please be careful not to move anything.Is that one over there, dear?She never locks the door.Back here, you fluffy rapskin!Do be careful, Miss Kimberley.How did that happen?Why have you been standing there?
```

### [48] hash=`4665acef5e81fbc8`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p12`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（12.【“平安夜”】）

```text
Just a little while.Funny, I've never thought to open a door like that before.Come along, let's take a peek inside.This red button on the chair?This typewriter seems like it's seen a lot of use.Do you see any drafts?Any samples?I can't say.I'm not very familiar with these things.There's something here.I thought her name was...Doris.
```

### [49] hash=`6e3870ec17a31364`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
Sink me, Lepera!I thought you'd been sent to Davy Jones' locker!Why did you think that?I'm tougher than the stubble on the chins of the old geezers here.I'm like you, a ship that'll never sink.Timekeeper, who's that over there?Kimberly?Did me viejo let you go?Oh, Timekeeper, let me explain.When we were routing out the deserters, we found Kimberly hanging out with the Manus thugs.You don't have a boat!
```

### [50] hash=`e2d3e81a87eb2d95`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
No, I mean, I'm not in any boat with anyone!Only I found my...Listen, I don't know who it is you're looking for, but it's not me.I've already told you everything I know.Not welcome here.Get out of your way.Take me back to the place.I don't want to see that thing.Alright girls, if you want to have a chat, at least take a seat first.It simply won't do to have you all standing around the entrance like this.
```

### [51] hash=`d114376fff123301`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
I think candy is bad for your teeth, vovo.Oh, I'm much too old to worry about that.When you reach my age and just waking up each day is a blessing, you'll eat whatever you want too.Mama and Mariana, could I have a word with you please?I have some questions about Mr.Duncan.Oh Duncan, what kind of trouble has he stirred up now?Alright then, why don't we head inside and give those two some space?And Lopera, apologize to that poor girl properly, you hear?
```

### [52] hash=`1c99f5aa06999dee`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
Mi viejo released you, which means you can be trusted.And you saved Vertan's life too.I guess I shouldn't have been so hostile toward you.Have a drink.As a token of my apology, Salvador and coffee.Greats if you need to pull anall-nighter.Yep, bitter like the old days.Back in Colombia, my father did horrible thingsto his plantation workers.Well, my biological father.Not Igor.He said, no, that'snot the sound of gunfire outside.
```

### [53] hash=`bc6a4998a3708075`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
The workers are setting off fireworks.They're celebrating.You know, a place where people have your back.I'll drink this.Of course, don't force yourself.I know the taste isn't for everyone.Carlota Lopez Rivera.That's my full name.Beat of a mouthful, huh?I wanted to erase it from my profile.From everywhere, to be honest.But me via Hodes approved.Molly agreed with him.She said,You mustn't forget your past, Vera.
```

### [54] hash=`0307f7a7689ee56f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
So I let it go, but Lopera sounds so much nicer, so I preferred to go by that.And you, Kimberley?What's your real name?Nahari.The residents of Heartfelt Home called me.And Joanala.How long ago did Mr.Duncan move here?Do you remember?It must have been...five?Maybe six years ago?I'm not entirely sure.Do you have any photos of him?We do have one, but he's been tethering dust for years.Let me see, here, this is him.
```

### [55] hash=`7618134fc4b3ebb8`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
I know a gentleman who looked just like him.His name was Carson.Did Mr.Duncan ever go by that name?No, not that any of us are aware of anyway, and I've known him since I was a medicin the army.Back then, people called him Donken the Don'tless, or the All Powerful Donken.I never once heard Carson or anything of the like.Sorry I couldn't be of more help, miña querida.A crow?Oh dear, this looks like bad news.
```

### [56] hash=`e04ba18556bc9b22`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p13`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（13.【粉红海豚】）

```text
Santos.Dr.Doras is being held captive in the Colonel's manor.He's given us three days.He says that if Zeno doesn't return the deserters they detained, he'll execute the doctor.Mamai Mariana, please contact Admiral Eagle.We need Zeno's help.
```

### [57] hash=`3730940036111eb1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
We simply don't have the men to spare.It doesn't need to be large.Just dispatch my sentinel unit from Buenos Aires to Sao Paulo.At the very least, send three men.Dolemi?One of your orphan children?That seems like a feasible solution.Yes.His parents died fighting for a Xeno.All my children are loyal to a fault.Officer Carlos was shot in the head by one of his own men in this very office.I need soldiers I can trust.
```

### [58] hash=`e7ca479db014364a`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
Ah, so the fearless Igor is afraid of death after all.An officer was killed by his own soldiers at his own base.This is an immense stain on Zeno's honor.Indeed, everything goes according to plan.You'll see your unit shortly.Now it's just a matter of timeYesterday we received word from the Time Keeper that the city will stand up and will be as strong as the core of the earth.What a sin!The fire is burning.
```

### [59] hash=`ca9581cff451cd4e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
The white sauna will cover it and it will be covered with darkness.This is all for the bright future.The best future for everyone.Yesterday, we received word from the Time Keeper.The Dr.Torres has been abducted by the Apostles Brotherhood.She should be coordinating with Lopera to set up a rescue operation as we speak.Also that girl who escaped, Kimberly, is with the Time Keeper.She claims that she was released.
```

### [60] hash=`0063c81b17415a3e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
Just play along with your lie.There is no need to tell Lopera the truth.The Brotherhood has demanded that we exchange the detained deserters for the Doctor.Forgive me for issuing instructions without your consent, but if we refuse or ignore them,I'm afraid they'll...They'll execute the doctor.What arrangements did you make?I told the timekeeper that Xeno reinforcements would meet her at the veteran's residence.
```

### [61] hash=`b023dd953a1453b3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
Since Lopera is familiar with the place, I also asked her to scout out the rendezvouslocation.And, yes, I played along with Kimberly's lie.I...I assumed you would have done the same, Father.Very good.Your squad will soon arrive.Take them to La Pera at the rendezvous point and bring the Doctor back.A squad?I've spoken with headquarters.All going well.Telly, me and the unit will arrive soon.I see.I can hardly remember the last time we were all together.
```

### [62] hash=`6e9797f41c3a7171`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
Your father died in the Badan.In a war, he had no obligation to fighting.It's far more glorious to die in the throes of battle than to wither away on a sick bed.He made an honorable sacrifice.How shameful that we would tarnish his honor.Let's begin with that young pilot, Lilia.Tell me, what do you think of her?She is well-trained, experienced, a straight shooter, similar to Lopera in many ways.She's a true Slav, just like my brothers and sisters back home.
```

### [63] hash=`71cf71bc94f6667e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
I suppose she's luckier than Lopera, not destined to become a traitor like her.Lopera is still a child, really.So many lives have been lost, in wars, in the storm.What do you think Lopera will do?She's your child, just like me.I think she will stand with us.You think, do you?Anyway, she's not important.Here, take a look at this.Not wear it, nor will you.I promise you, not one of us will wear this thing.
```

### [64] hash=`6f6ee4e53b333cdb`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
The preacher has given us a gift and shared with us an oracle.We will bring her something in return.Fire and brimstone rained down from heaven, yet among the ruins were covered the remnantsof a miracle, a miracle that is living, breathing and growing.I can sense their life force, I can hear their whispers from within these ashes, Maldir.They are invincibleRather than endlessly throwing young soldiers lives to the white stone house.
```

### [65] hash=`54e792acc2017ff9`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
Choose to stand with the true future.I will always stand with you fatherThe gambling games been set up in a place unfamiliar to you soonYou'll be invited to join the table as wellYou seem to have grown quite assertiveBut remember thisAs a newcomer to the table, you have no privilege to make demands or probe for information unless you're looking to be targeted and isolated.You have to lose a few rounds.
```

### [66] hash=`6f219cc566241d05`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p14`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（14.【无眠之人】）

```text
Pay your entry fee.Only then can you start to learn the secrets of those at the table.The player's backgrounds, the dealer's habits, and the truth behind the highest stakes gambler.It's baffling to me.while the black robes plot to overturn the table.Clever?More like cretinous and atrocious.Once the tables flipped, there'll be nothing but chaos.Who would bother to set it right again?No one.
```

### [67] hash=`4515957a55516196`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Arcanist.Abuses alcohol and loves to fight.Messenger.Call Lieutenant Lillia.Tell her to meet me at the training ground.How does it compare to the drink back home?The stuff subs your energy.Makes you feel sleepy.Just like this land.This place is always submerged in a half-dead stupor.Poverty.Chaos.To them, the future feels farther away than the sun beating down from above.Tell me, Lieutenant, what do you think of the Foundation?
```

### [68] hash=`71e989d5e86b6c32`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Is this some kind of test?No, no.Just the curiosity of an old man.I often wonder how the younger generation views the organization.Well, unlike those Manus Maniacs, the people at the Foundation are at least open to reason.Don't get me wrong, they are stubborn, but overall, I think they're good people.The Time Keepers red-headed sidekick, for example.She's a stickler for the rules, but it's so boring to follow all the regulations.
```

### [69] hash=`1943e5e4beb9a1cd`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
That being said, it would probably be even worse without them.Total chaos, actually.Anyway, at the end of the day, someone has to do the thankless jobs, and the people atthe Foundation are the only ones willing to do them.As the Foundation's most loyal partner, Xena has always been committed to creatinga brighter future for both Arcanists and humans, that includes fighting Manus Vindicta, asas any other conflicts and chaos in the world.
```

### [70] hash=`4df10de5ef1bc102`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Uh-huh, it's a mindless gun.The Foundation points, and Xeno shoots.Precisely.Countless soldiers have perished in this storm,and they've all been deemed necessary sacrifices.I have to tell you, I don't like Xeno's role in all this.Neither do I.But in orders in order,Even if it sends your soldiers to die meaningless deaths against an enemy they couldn't possibly defeat.Still, we march on without hesitation, pushing our weary bodies deeper into the storm.
```

### [71] hash=`102be1df68af11ec`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
But how much longer can Xena keep going, Lieutenant?How long until our knees buckle and we fall to the ground?I don't know, and I don't care.Arkana isn't dead.We detected life signs after the explosion of the vacuum bomb.That's impossible.Yes, it is impossible.It would take a miracle for her to survive.Do you believe in miracles, Lieutenant?I'd sooner believe the ramblings of a drunkard.That may be the case.
```

### [72] hash=`e4f3dedf6a07e2d1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
But when a miracle worker appears, there will always be people who follow them, like sheep follow a shepherd.So, when the desertion incident occurred, I wasn't surprised.I was infuriated, however, not because they abandoned Zina, but because they murdered their own officer.Damned traitors!Back before the first storm, human and Arkanius troops got along well.We set aside our origins and united under a common banner.
```

### [73] hash=`6a4c14028a91fb0e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Our bloodlines meant nothing next to our bond as comrades in arms.But the storm changed everything.As a soldier, I must obey my superiors, I send my men as ordered, no question asked.But does it really make no difference if the place they die a mortal's death isn't a battlefield?Like war, these things are never simply a matter of black and white.Lieutenant, what do you think of the Time Keeper?I trust her completely.
```

### [74] hash=`5adea6058731163d`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Sounds like you'd gladly sacrifice yourself for her.We need more leaders like the Time Keeper.Manus Vindicta, the Foundation.They are just two sides of the same coin, aren't they?The Foundation, the PEC Security Council.Manus Vindicta, which path do you think the Time Keeper will eventually take, Lieutenant?I trust in Verzin's decision.I understand.Are you sure that Zina is not testing me?No.This has nothing to do with Zina.
```

### [75] hash=`0a1b67fd0e8ce720`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
I am talking to you now as Igor, not Admiral.What's going on?Lieutenant Lilia, you are under arrest for the assault on Admiral Igor.Assault?Oh, I get it.Stand down and surrender, lieutenant.Even the boots here taste lame.Come on then.You're not taking me down without a fight.Soldiers, fire!Bring it on.Show me what you got.You traitorous rats!I never intended things to turn out this way.Surrender now, lieutenant.
```

### [76] hash=`91cd81f47092996d`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Or I'll be forced to hurt you.Surrender to you?You'll be the one who is surrendering if I even give you the chance come on soldiers do your worstWhat a shame?Fire at will there is no use resisting lieutenant.Tell me what's eager planning?Father will lead us to a future where meaningless sacrifices are no moreThe die has been cast.I hope you know that this is nothing personal.I'm just following orders
```

### [77] hash=`06a1d35363b0a3b6`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p15`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（15.【北地骏鹰】）

```text
Take Lieutenant Lillia to the holding cell.No one is to harm her without orders from the Admiral or me.What?We are traitors to Zeno now, Lieutenant.I am loyal only to my father.It's a pity, really.I would have liked to work with you in the future.How long has he been planning this?Ever since the preacher gave father a gift and a path to a brighter future.Live or die, Lieutenant.I will never betray my family.

it was an honor this way to go I'm done reading reports anywayI look forward to your wise decisionswe need some good news for a change
```

### [78] hash=`c6b92bfab1c614f3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p16`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（16.【重逢日】）

```text
Father, Talimei and the unit have arrived.So here they are.The army of justice ready to eradicate the Manus and the deserters in one fell swoop.During the last storm, the Foundation created this thing.And with the help of Laplace and their pair of Narcanists,they stole the Fire of the Gods, just like Prometheus.Which side would you choose?I wouldn't.I would follow.Follow you wherever you lead.Send someone to bring Stefan's belongings here.
```

### [79] hash=`24af1774c5ec1de3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p16`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（16.【重逢日】）

```text
The traitor found something important at Tuesday's motel.Ptelime will find it useful.That's all for now.Understood.Moldir, long time no see.What do you say?Do we give those humans a chance to surrender?Manus vindicti don't accept humans.But I doubt Father would blame you if you men allowed them to escape the base.Escape the base?Moldir, are you having second thoughts?Either follow this path to the very end,
```

### [80] hash=`78a4d7cf97e75186`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p16`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（16.【重逢日】）

```text
or show mercy and give Father and the two of us executed.So what then?You want to have a mass execution like Lopera did?On what charges?For refusing to join the rebellion?They went to rally the soldiers.We've been waiting for this day for ages.For ages?How long have you known about this?I told your siblings some time ago.She's not part of the plan.Her only responsibility is to bring back Doris.Doris?
```

### [81] hash=`70576d23cf961db1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p16`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（16.【重逢日】）

```text
Who's that?None of your concern.You have other things to worry about.Go issue your orders to your soldiers.Of course, Father.I will do as you wish.Right then, Moldir.Let's get started.What's going on out there?Is the base under attack?By whom?The Manus has no reason to launch a frontal assault?The Apostles' Brotherhood?No, that's even less likely.Take a comrade!Are we under attack?Take your stuff and go!
```

### [82] hash=`ee91ce7dd5e64020`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p16`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（16.【重逢日】）

```text
More enemies over here!Comrade!Lieutenant Moldeer asked me to help you, take care of them, kill them all!No, recall your troops and assemble.Hands, assemble!The bloodshed stops here.Moldeer, time to head to Sao Paulo.Forgive me for asking, Pazar, but what if Lupera refuses to come back?Oh, Moldeer, if it's too much for you to bear, I'd be happy to go and see our dear little sister for you.No need.

This is my mission.I will get her to come back.There will be no alteration of the mission.Tell me.Retrieve Kimberly.
```

### [83] hash=`675aed1a85cc254a`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p17`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（17.【离群的黑羊】）

```text
No, no.It's Lopera's mission to take care of the doctor.My mission?Well, it concerns the young lady behind you.I wasn't informed of this.What does she have to do with Zeno?As far as I'm aware, the Zeno officer at Tuesday's motel committed suicide.Kimberly had nothing to do with it.Oh, Stefan?I couldn't care less about him.I'm not stupid, you know.Miss Kimberly somehow escapes the base.Let's just get along, shall we?
```

### [84] hash=`fbeb5cb6b915390c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p17`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（17.【离群的黑羊】）

```text
This isn't an arrest, Ms.Kimberly.It's an invitation.A succubus should follow her instincts.Obey your master.You know, you were close, Kimberly.You almost found it.It was hidden at Tuesday's motel, just like you thought.Stefan thought it was just a wind-up toy.What a fool.Yes, that's the spirit.Come with me, and I'll...Don't.He's not going to give it back to you.Oh, so you'd rather stay with the Timekeeper.
```

### [85] hash=`0984e69cf2ed7779`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p17`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（17.【离群的黑羊】）

```text
I guess you need a little reminder of who your real master is.Soldiers!Prepare to fire!Pick it up, Timekeeper.I hold no grudge against you, and I'm not going to shoot an unarmed civilian.Make your choice.Take the weapon and continue to fight, or surrender.If you do surrender, I'll guarantee your freedom.But Kimberly has to come with us.I see.So you've chosen to fight, on your feet.Now then, Kimberly, kill her.
```

### [86] hash=`9b2d643848deb7e4`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p17`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（17.【离群的黑羊】）

```text
Want me to kill...Batten?Come on.My patience has its limits.You will obey me.Your freedom for the life of a stranger.Yes!Kill her!Prove your loyalty!Then I'll give you back your toy.I promise.Raise your gun, Timekeeper.Aim at her and pull the trigger.this monster is going to kill you you'll have to shoot her if you want to liveobey your master yes give in just like that look Kimberly she picked up the gun
```

### [87] hash=`a0ad83babed79c83`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p17`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（17.【离群的黑羊】）

```text
shouldn't you kill her before she kills you she obviously values her own lifeover yours and she won't hesitate to fire a bullet through your heart toher?You're just a horrifying beast.I mean, look at you.You're a succubus.A demon bornto be bound to a master.Born to be controlled.If that's what you want, then kill her.Breakher neck.Now, heed my order and kill Vertin.End your suffering with her death.

Just obey.
```

### [88] hash=`4463bf826ea8ca6c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p18`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（18.【台风眼】）

```text
Britten...How dare you!Looks like negotiations off the table, Timekeeper.I suppose I'll have to turn to violence.Soldiers, kill them all.Spare no one but Kimberly.She's the only one the Admiral needs.I'll kill every one of you!What kind of monster is she?Maintain formation and fall back.Keep firing!Lane!Retreat!Everything will be fine, Kimberly.I'm here.It's okay.You're going to be alright.You're no longer bound by anyone.
```

### [89] hash=`daab90e2c0dcd8ec`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p18`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（18.【台风眼】）

```text
No contract, no seal.The wind-up toy's been destroyed.It's been shattered intopieces.You're free, Kimberly.You don't have to take orders from anyone anymore.Kimberly doesn't have to take orders?Nala doesn't have to take orders?Come.If you've got nowhere else to go, you can come to the Foundation with me if you like.I'll let them know you risk your life to protect me from the Xeno Rebels.Anyway, the choice is yours.
```

### [90] hash=`757ea41bd73926bd`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p18`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（18.【台风眼】）

```text
Can choose?Yes, whatever you want.No one can control you anymore.You belong to no master, only yourself.belong to myself.Like when my sister died.The first time I left home.Like when I fled to Sao Paulo during the war.The old days.No longer rely on or under the control of anyone.Just think about who you are.What you want.And enjoy your new life, Nala.Starting today.
```

### [91] hash=`eebc2cfbadc949e1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p19`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（19.【赌局】）

```text
All this time, waiting for Xeno, I really want nothing more than to clear up this little misunderstanding of ours.There's no benefit to me hurting you.I hope only to peacefully return you to your friends, and in return, receive mine.After all, this city and its false era will be washed away by this storm before long.Those poor unbelievers.We were all once like them, yet to realize that we are children bathed in the light of the divine.
```

### [92] hash=`eac2965c34036efa`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p19`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（19.【赌局】）

```text
One day, they will turn from darkness to light, just like our Xeno friends did not long ago.The apostates, however, they who have abandoned our faith, they must die.People like him are...useful.Tools to be used to our benefit until they're lost to this storm.Isn't that also how Zeno uses their soldiers, Doctor?As currency to be spent and lost?At least Manus Vindictae promises these soldiers a future.
```

### [93] hash=`5ca76b09649963a5`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p19`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（19.【赌局】）

```text
A future worth looking forward to.The sufferer will be reborn, and the Apostles' Brotherhood will sail south with me.We will become followers of this sufferer, undertake their trials, and their grace willbe bestowed upon us.The world is reversed.Eight guards?No way to get through.Wait, Mary!I finally found you!I bet you didn't expect to see me here, did you?just watch I can handle this myself unless you dare to join me old timer
```

### [94] hash=`ee06d0005569ff8a`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p19`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（19.【赌局】）

```text
give me a few dots okay here's the plan you lure the guards away and I'll checkinside the chapel when I take my shot I'll head that way you stay hidden in thewoods and make your way to the other side lead them toward the river let'sLet's make this a little more exciting, shall we, boys?Nice shot.Ah, it appears someone has come to your rescue, dear lady.I'm not surprised.I should have put a bullet in your skull back on that sheep.
```

