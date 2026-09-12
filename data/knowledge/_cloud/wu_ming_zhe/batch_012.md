# 剧情图谱抽取 · batch 012

- 角色：`wu_ming_zhe`
- 批次：**12** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「忧郁的热带」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_012.jsonl`

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

### [0] hash=`6be8feef2d3b0106`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p19`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（19.【赌局】）

```text
I'm afraid you're playing the wrong game now.Oh, yeah?So what does the winner get this time, Dr.Doris?No.There are no prizes.Who and I are nothing but specks of dust in the wind.It was you, wasn't it?You came to this sacred place and attacked my people.Yeah, and I'm ready for round two.And this time, you won't be living with your life.Fate has brought us together this day.Just as it brought you victory in that bed.
```

### [1] hash=`01340c37f9f275ed`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p19`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（19.【赌局】）

```text
The puppy wishes to come along.I've got some trouble, bro.Give me the face.The puppy agreed with your decision.What's that?Blood can only be paid in blood.From the crucible.He agreed with your decision.And it is blood and gold that stain this land.In this game of prayers.And I've had quite enough of you, little gumbler.Looks like I win again.Yes, you won, Ysra.Won't be a table left to play the next.

So long, little time, you paid a little more attention to your friend.We can talk after we get out of here.
```

### [2] hash=`bf3544fab2036e49`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
Kill her kill Hurtin noobey your master kill herFollow your instincts follow my ordersobeynowHey, ISaid no pave the path for usThe Apostles Brotherhood will become their followers undertake their trials and embrace their graceWe all need the miracle they bestow.We will be immortal.What reason could you have to kill your own men?They mutinied and killed their superior officer.The Apostles' Brotherhood may have infiltrated our base.
```

### [3] hash=`c8a0d40ab389a892`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
The Apostles' Brotherhood?Notorious gang from the streets of Sao Paulo.Our intel suggests Manus Vindictus' presence too.Sao Paulo.There isn't anything for me there.No dancers, no beasts, nothing.In this city, arcanists and humans live side by side.Both are equally passionate, albeit touchy.Violence is far from the means to end here.It's a tool, and one all too readily used.Wait!Apologies.It seems I've killed the wrong people.
```

### [4] hash=`4f9f20f798847b8c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
Mutineers!Traitors!You've made your choices!Now you'll learn the consequences.Zeno never forgives.Attention!Aim!A shame you had to see all that.Our second Lieutenant Lopera is a crack shot.I trained her to be nothing less.Yet no soldier of Zeno would take pride in an execution.The burden falls on me.This was my fault.My negligence.She hunted down these traitors herself.Lieutenant Moldier is investigating still.
```

### [5] hash=`6874a10898444cfd`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
We will find out who else was involved.The Apostles Brotherhood is back.We suspect they may have even infiltrated our base.We've also received intel indicating Manus Vindicta's presence in Sao Paulo.Manus Vindicta?I'm not entirely surprised.Intelligence suggests they are closely associated with the Apostles Brotherhood.What I hadn't expected is that they would drop their Order of Enlightenment guys so soon.
```

### [6] hash=`12fa7b39c567e29c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
Arcane is dead.There is no room for doubt, no one.Nothing could survive a vacuum bomb.You will become used to the tropical sun in San Paolo.I've been through a lot worse.Snowy mountains, deserts and soaring eagles.I do find myself thinking back to those times.And kept within the guarded areas there may be a person of interest to us nearby awriter for their two magazineSaid to be a blind woman named Earth
```

### [7] hash=`1226aa154a2216b3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
Her work seemed to be published after every era the storm has affected it could be this is only an alias apen name used by a new person each time oror could she really have crossed the storm eight times andSomehow, the storm has never affected her.Ms.Barbara provided us with some information.She said the latest piece was sent from a veteran's residence in Sao Paulo.I understand they have a doctor working there, a blind woman.
```

### [8] hash=`9036fbdc0ab2744c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p1`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（01.【此即正义】）

```text
If so, she would match our intelligence on this mysterious atuv rider.You should seek her out.You're fortunate to have come now, timekeeper.I see that you have one of ours with you, Lieutenant Lillia.I ask that she serve us for the duration of your mission here.She is a fine instructor, and Xena is in need of help training our latest recruits.I'll speak with her and see what she thinks.Thank you.I should return to my work.

Your comrades should be waiting for you in the meeting room with Lieutenant Maldir.
```

### [9] hash=`c2b11053b2b21b67`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
Eliminate all hostiles.Find Lopera and Dr.Doris.Brotherhood Guard's gone.Molly!Pera!Thank goodness this tracker button still works.What happened in the chapel?I had to fight with Santos, but he got away.Weren't you supposed to go to the veterans' residence?Rescuing the doctor is our top priority now.I am so glad to see you safe, Doctor.Great job, Pera.Let's head back to the base with Dr.Doris.What about the timekeeper?
```

### [10] hash=`8eae421f3947aaa6`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
She's on a new mission assigned by the Foundation.It's got nothing to do with us.Father wants me to bring you and the doctor back to the base as soon as possible.What do you mean?Why this sudden change of plan?What's going on here?Just come already.We're evacuating Sao Paulo.Evacuating?To where?Just follow your orders, Lupera.The Admiral sent me to pick you up.Then why didn't he tell me any of this?
```

### [11] hash=`0e8a5f8a3ee85a08`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
I don't know.I'm sure he has his reasons.We're heading south.To Tierra del Fuego.They've made preparations for us.Come on, Pera.Come with us.You, me, father, telling me, everyone will all be there.Everyone?Why didn't anyone tell me about this?Because, Pera, you can ask questions later.We don't have much time.No.Why are we going to Tierra del Fuego?And why are we running out of time?What are you planning to do?
```

### [12] hash=`a111bc5be46189e8`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
Waiting for you in Tierra del Fuego?Who's behind all this?That jerk, Pálemi?No.Father gave these orders.Come on, Lobera.Lower your gun.Father needs the doctor.We need her.Bring her back to the base and come with us to Tierra del Fuego.Why?What are you going to do in Tierra del Fuego?Seize the future.A future for all Arcanists.Father has embraced the preacher's promise.None has been dictated.No.My family are not traitors.
```

### [13] hash=`662ef68f94cdd67f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
Look, you don't have to do anything for them if you don't want to.Just come with us.Come home.Forgive me, Pera.Tell me what you've got.What's going on?What's Pa planning to do?What about you?Are you going to kill Father and me?Like you did those traitors?I...I got some trouble for you.Get this...hey!Drop your weapon, Pera.It's time to come home.Why didn't Pa tell me his plan?He doesn't trust me, does he?
```

### [14] hash=`ff17ea097920e1c1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
Did you come here to take me home?Yes.You're lying, Mommy.Never be.Most of the time, anyway.Enough is enough, Pera.You're wasting our time.You mean the time for your scheme?Making the Doctor back is more important than me, right?No!Pera, I want you to come home with me.You call that a home?With a traitor for a father and a sister who doesn't even trust me?Cristobal, why is he doing this?For the good of us all, Pera.
```

### [15] hash=`27f6dbcb677e03c1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
Consider your mission complete.I'll take over from here.Thank you for your service, comrade Lupera.What's going on?I'll handle this.Take the blind lady and retreat.Make sure she is safe.I am sorry it has to end this way.Farewell, Pera.Has something gone wrong?Wait a minute.What's going on here?Xeno soldiers?What are they doing here?That's the doctor, isn't it?Why isn't Lupera with them?tranquilizer bullet oh I see it's shattered oh no have you been planning
```

### [16] hash=`af9414fbceda5ab3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p20`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（20.【亲爱的你】）

```text
this am I really the only one who knew nothing about it was I ever actuallyaccepted into this family timekeeper yet that why did yourThen leave you here all alone.Hurry back to the residence.It's Igor.
```

### [17] hash=`ae791e969a1e3fe5`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
I guess you haven't had an easy time either.I have bad news.Igor's just started a rebellion.He's got an army.What's the situation at their base?Not good.There was fighting and bloodshed.Lots of it.The rebels must have won.Those traitorous bastards.What about Lepera?Did she defect too?All I know is that she was sent to the Colonel's manor earlier.But why would Igor...if Lepera's also joined the rebellion?
```

### [18] hash=`14f2d98041d8976e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
Igor still wants you.We'll come back for you later.What now then, Kapitan?There are no foundation branches nearby.If we request reinforcements, they'll be too slow to arrive.Then we go ourselves.Count me in.I have to talk to Igor.He owes me an answer.White Rum, could you take us to the Xeno base?Anything to save the Dock?Anchors away, mateys!You screwed up.It's just a minor setbackBazaar isn't happy
```

### [19] hash=`8debbc48ee9c9944`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
Look, I'll deal with her.Okaynext time I'llThere won't be a next time.We can't just waltz into the foundation and take herAnyway, are the aircraft ready?YeahFather and the doctor will be boarding soonWho is she anyway?I don't knowLooks like father hasn't told you everything eitherYou should never entrust all the pieces of a puzzle to a single hand.All this time with Fathers made you quite enigmatic.
```

### [20] hash=`3b645d585202ee69`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
There's a charm in mystery, you know.Are you not coming with us on a helicopter?Someone has to stay behind and organize the repeat.You go ahead with Father.I'll join you later.Sometimes I just don't understand you, Moldeer.Oftentimes I don't understand myself either.Perhaps.That's why father always keeps me close.Just get going.I'll take up the rear.We're under attack!Don't get entangled with the enemy!
```

### [21] hash=`80138126a025b898`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
Focus on the evacuation!How many hostiles are there?Three!And a sailboat!A sailboat?What is this?The age of exploration or something?One of them is flying some kind of aircraft.Oh, she's fast!Two squads are currently engaged with her in courtyard A2!So, you're just going to leave me here in San Paolo, huh?Where's Igor?You've grown taller since we last met, dear little sister.Whoa, whoa!Don't look at me like that.
```

### [22] hash=`4d42bcc978e49a3c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
I don't care what you do.Come home or stay with the Timekeeper.I won't stop you.Get out of my face.Molly?Miss Moldea, it's unfortunate that we have to meet again under these circumstances.we've simply chosen different paths timekeeper I suppose the next time I seeyou will be in Antarctica then me go join father I can handle this Molly whyforgive me I can't let you pass soldiers take aim what on earth is eagle
```

### [23] hash=`f82938a7f2788c87`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p21`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（21.【原爆点】）

```text
trying to do we are soldiers it's our duty to follow orders not questionI don't ever want to see you again.We couldn't halt Eagle's escape.More rebels came at us following the gunfire, and we were forced to flee the base.We failed.
```

### [24] hash=`f79b944183bb14d9`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p22`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（22.【西风咆哮】）

```text
You made the right choice.We simply followed their guidance, preacher.Unfortunately, we failed to bring the Succubus.But I did bring you this and Miss Earth as well.No, Admiral.Not you.Us.We all need the miracle they bestow.My men will not wear the masks, nor will they take the trials.We need no trials to test the loyalty of my children, preacher.And for now, Miss Earth will stay under my protection.
```

### [25] hash=`57720a5a5e0fe15f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p22`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（22.【西风咆哮】）

```text
As you wish.Until next time, Admiral.Father, I shot at Lopera.I have to be honest, father.I don't fully agree with your decision.At least not on a personal level.You are entitled to your opinion, Lieutenant.Atmanus Vindicke.I thought you'd make the same choice she did.No.I will always follow you, father.Just let her be.Now, bring me Doctor Doros.Father, I don't know you, sir.You must have mistaken me for someone else.
```

### [26] hash=`84d40c9c1107755c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p22`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（22.【西风咆哮】）

```text
No, I couldn't possibly mistake you, old friend.In the last days before the Millennium,We fought side by side, in hindsight, that battle may have been a mistake.The storm swept across the world, leaving behind an era of chaos, and we lost our future.But now, another path lies before us, one that we once fought desperately against.A path paved by Arcana.A path leading to a world free of conflict.My old friend, that marble chair the Foundation gave you, was the secret behind it?
```

### [27] hash=`440ac149c2ec741e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p22`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（22.【西风咆哮】）

```text
What happened to you after you pressed that button?Nothing.Do you remember what happened after you walked into that White House?I'm sorry.I don't know anything about that.My dear Miss Earth, your name continues to show up between the occurrences of the storm.I don't know what you've encountered, what you've experienced in all this time,but your very existence is about to change the fate of us all.
```

### [28] hash=`80e65e20e6c935bb`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p22`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（22.【西风咆哮】）

```text
We have some news you'll be happy to hear.Trust me, you'll wish you had more than a minute for this.Now, this kind-hearted doctor has become a crucial part of another wicked scheme, ofwhich our dear Admiral is well aware.An orchestra without a conductor can barely play a symphony.Recognizing that missing, vital piece, the Admiral seized the opportunity without hesitation.Experience gives a veteran his scars, yes, but also a scrap of wisdom.
```

### [29] hash=`f1f194daf01888dc`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p22`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（22.【西风咆哮】）

```text
He knew he should gain the upper hand in this one-sided gamble.Your minutes up.Time certainly does fly, doesn't it?I'll be back when there's a new development.Stay alive if you can.I'd like to keep reading reports for you.
```

### [30] hash=`7089cad879e66f30`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
But at some point, we have to move on.Thank you for the advice.It's just...Pardon me.My apologies for interrupting.Miss Sotheby, I heard about what happened in the favela.Thanks to your efforts, Zeno has been able to recruit a new group of spirited youths.Mr.Duncan, we need to record your information and cross-reference it with that of Mr.Carson, who was lost during the storm of 1929.It's bewildering, isn't it?
```

### [31] hash=`4bdd2301afb0affb`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
How could that be another Mr.Carson?1929?Please come with me, Mr.Duncan.It won't take long.After that, you'll need to initiate the procedures for your reenlistment in the Zeno Arms Academy.While the said procedures are underway, the rehab center will take care of the injuries you sustained in Sao Paulo.Welcome back to our cause.There have been many cases like yours.Politicians, singers, the list goes on.
```

### [32] hash=`7bd93b4a21d97f75`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
The foundation compared them to photos from the 90s.While their appearances had changed,they were undoubtedly the same person.Hey, isn't that Lieutenant Lillia?This is an alcohol-free zone, Lieutenant Lillia.Please try to follow the regulations.Oh, did I just wander into another dry zone?Great.So many rules and regulations.Oh, how boring.Has Lopera arrived?She's in her room right now.Burton managed to secure her some rest time before her interrogation.
```

### [33] hash=`dc1cfe63658bf77c`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
Poor girl.Honestly, no one deserves to go through what she has.It's even worse than being cooped up and buried in paperwork.Clerical work is essential too.Well, good luck, comrade Duncan.Don't forget to stretch your hand between signing papers.You also need to write a report, Lieutenant Lillia.Our executives are quite curious to know how you managed to escape the rebels' custody.Moldeer, the woman in charge of the base, had one of her guards release me.
```

### [34] hash=`59394f67e18387f2`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
You mean to say that Moldeer, the lieutenant who's joined the rebellion, set you free?I think so.At least that's what the guard told me.Lieutenant Moldeer asked me to help you.Take care of-I'll be sure to make note of that.And, of course, please specify this in your written report as well.This is very important, Lieutenant.If she's having doubts, then we may still have a chance to win back Igor's rebels.
```

### [35] hash=`d73bf067d26bc099`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
Or at least some of them.Igor fooled us all with his rebellion.It's been confirmed that the Dr.Doraz he took is none other than Ms.Byrd.The motives behind his actions, however, are still unclear.While only a small number of the Xeno soldiers chose to join his rebellion, I believe itis necessary to urge the Xeno Arms Academy to strengthen the discipline of their members.No need to worry about that.
```

### [36] hash=`77d3f82d468a02a4`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
Xeno will handle it themselves.If that's your judgment, then I have no objections.On a separate note, Moth, our mole planted within Manus Vendictae, has sent us somenew information.The Manus are sending supplies, personnel and weapons in huge numbers to the south.It appears our suspicions were correct.Manus Vindicte is preparing a ritual to draw forth another storm.The location of Jerry Wilson provided by Miss Lucy confirms that the Manus are moving toward Antarctica.
```

### [37] hash=`097d3a2adbdd9437`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
Additionally, it's now clear that some of the arcanist organizations, including the Apostles Brotherhood,have been assisting the Manus through criminal activities such as smuggling and human trafficking.All very valuable information.How's the Timekeeper doing?She's stable.It's worth noting, however, that she brought back a succubus from the Manus.She requested that we revoke the arrest warrant for the succubus
```

### [38] hash=`634bde93400f3517`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
and grant her all the rights enjoyed by Team Timekeeperin accordance with the Storm Reformation Manpower and Discipline Act.I've consented to a request.Excellent.She's the ideal person to keep watch over the succubus.Very good, sir.About Igor.The late Admiral Igor of the Zeno Arms Academy will be duly honored in the headquarters Hall of Merit.His great achievements and remarkable service deserve to be remembered.
```

### [39] hash=`c6772aae1a076a25`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p23`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（23.【谢幕演出】）

```text
That's all for now.London, Lima, Aswaiya.A report from Columbia.The mugshots of Pablo Emilio Escobar Gaviriado not match those archived.Similar anomalies have appeared for other notable figures.Why did Igor abduct Miss Erd?And why does he want Kimberly?And where are Igor andhis army going?Why did they defect?Mr Carson, who was reversed by the storm of 1929,has somehow reappeared in 1990, or maybe there's more to it.

Could it be that thestorm doesn't kill people, at least not physically?
```

### [40] hash=`0c20fbefad1608dc`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p24`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（24.【独角戏】）

```text
one two three shots on target one two three two fivebetrayal you planned to kick me out right from the very beginning didn't youor did you never even trust me in the first place this awesome kind of game toyou Molly
```

### [41] hash=`40eea4e3e1d8ced1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p2`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（02.【框中旧影】）

```text
What are you doing out here alone?That is, soldier.You've really been building some strength, haven't you?And you are sprouting up like a weed.And you?Looks like they've been feeding you well.Stop it!How long will you be staying this time?Not long.Father plans to leave soon.He was furious when he heard about the defections.He ordered that he be brought here immediately.Perhaps he might leave with us when the missile arrives.
```

### [42] hash=`66a4e128d0c26902`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p2`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（02.【框中旧影】）

```text
No, I came to w-weep.The grounds have gotten so messy since the shutdown.You're lying.Those ears of yours are scarlet red.Alright, no more joking.We should get to the meeting room.Our Foundation guests are waiting.I would like to get back before they realize I've slipped away.Alright, but while we go, let me tell you about the prisoner we captured during our raid.And a strange little sheep in a bottle.
```

### [43] hash=`6568efb9f38bde28`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p2`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（02.【框中旧影】）

```text
I wonder if they have any Abang Akus there?1986.Rio de Janeiro.Mmm, Rio.Oh, you have friends in Rio?That simply must be Carson.I saw him.He dissolved.Mr.Carson?What, you mean this old geezer in the photo?What are you talking about?This must be Mr.Carson.Two men in the world that could look so alike.Could it be a doppelganger?Or an evil twin?But then, surely, Mr.Carson would have mentioned a twin brother.
```

### [44] hash=`8582f8f2e2eb6829`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p2`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（02.【框中旧影】）

```text
Even an evil one.Nose, and his eyes.Though he's not wearing his glasses, but I know those wrinkles.Look closer.I must be mistaken.But he's so very like the Carson I remember.Where is Lieutenant Muldir?Sir, timekeeper.I guess Sotheby saw someone familiar in one of these veterans photos.You know this Carson guy?Look, look!He does bear a striking resemblance to Mr.Carson, if my memory serves me right.
```

### [45] hash=`c01e1038393dc843`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p2`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（02.【框中旧影】）

```text
86.We lost many good soldiers to the Amazon that year.But some battle through survived.This man is one of the lotto.You're saying, that you've met this man before?He looks remarkably similar to a friend of ours who we lost in the storm in 1929.In fact, Admiral, they appear to be nearly identical.It's almost unthinkable.You're saying Mr Carson would never dress-I'm certain this is him!That is...fascinating.

Do you know if this man is still alive?I couldn't say.Dalfour, he would be in our service anymore.But you may find him at the veteran's residence in St.Paul.Thank you for your patience, sir.
```

### [46] hash=`43b100e249142c52`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
Lieutenant Moldier, about time.What was it?Did you stop for a picnic?Admiral, I...Save your excuses.Yes, sir.It was my fault, Admiral.I ran into her on our way here.It's been a while since we last saw each other.Your performance on the training ground earlier was most impressive, Miss Lepera.Allow me to introduce my team.This is Miss Sotheby, and this is Lieutenant Lillia.How's it going?I was previously assigned to HQ.
```

### [47] hash=`43e4e3930cd38af6`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
It seems your assignment here has done little for your discipline, Lupera.You have new orders.I'm assigning you to accompany the Timekeeper and her team to Sao Paulo for the duration of their mission.Me and Lupera?That's a whole lot of firepower.What are we expecting during this mission?Oh, sorry Lillia.I haven't had the chance to speak with you privately.The Admiral asked if you could stay on site to help with training their new recruits.
```

### [48] hash=`81f87988e2317aa0`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
What do you think?You can do as you wish.Training up some new blood, eh?Well, as long as you think you can handle things without me, I can stick around to lend a hand.It will be just like the good old days back at the Academy.Thank you, Lieutenant.As for you, Lopera, please show our guests to their rooms, and try not to overexert yourself.Lieutenant Lillia, stay for a moment.Lieutenant Moldier will bring some documents shortly.
```

### [49] hash=`21cc0ce786f5fb9f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
They should prove useful for your assignment.Now, I have other business to attend to.If you'll excuse me.Let's go.I'll show you around.But stay close.This base can be a bit of a labyrinth.It's only missing a bloodthirsty Minotaur lurking its halls.Well, I haven't seen him yet anyways.The base here has been understaffed for some time.Whole sections are deserted.It can't be dangerous.We don't usually allow guests to move about freely.
```

### [50] hash=`6d78eb300658019b`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
Well, who am I kidding?We don't have any guests in the first place.Who'd come here for a visit?Scenic views of dead gardens and overgrown brush?In the spring we have vine tripping competitions.And in the summer you can be part of our complimentary bug buffet.Besides, if there were any monsters in there, I would have heard them by now.Were those the Admiral's exact words?That nobody is allowed inside the tower?
```

### [51] hash=`9dd0bd38143e9248`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
Yeah, that was what he said.Under no circumstances is anyone to be allowed inside.So I'm thinking…Let me say this again, there are no monsters in that tower, and I am under orders toescort you directly to your rooms.But if we were to say walk a bit too close, and accidentally provoke some nearby creatures...They gave me quite a start!Thankfully, they were easy to handle.We can't let them run off.Who knows what damage they could do?
```

### [52] hash=`078da38b6a8e93b2`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
Now where could they have gone?It may well be possible they fled into the tower.Is this the entrance?Gamekeeper!Mi viejo, the Admiral.He won't be happy with this.Is there something hidden inside?There's an arcane array on the door.Is it to stop us from entering?Or to keep what's inside from coming out?I have no idea.We're soldiers.We follow orders, no questions.As Mi Viejo would say.With all the flooding we've had,
```

### [53] hash=`176e0b71bb6d61d2`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p3`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（03.【牛头人身怪】）

```text
they probably shoved everything they wanted to keep safe and dry in there.La Pera.You get lost on your way to the guest rooms, Pera.You know better than to be here.Your ship will be leaving early tomorrow morning.Please return to your rooms and get some rest.This is a military base, not an amusement park.Please do not wander about, especially near restricted areas.My apologies, Lieutenant.Perhaps you could point us in the right direction.

See ya!
```

### [54] hash=`da2579246a3a7bb8`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
Here, put this on para.It will allow me to track you should anything happen.You'll remember to bring father a souvenir this time, yes?And promise me you will be careful.I do not wish for our para to buy the farm just yet.Don't worry about me, Molly.Worry about them.I'll kill them all if I have to.Every last one.All right, all right.Enough blabbering.Do you two always share these little heart-to-hearts whenever you leave?
```

### [55] hash=`0caffb9fe58f65f8`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
I've got nothing to say except bye.Or is the tortoise suddenly not so worried about its speed?Sotheby, do we have everything?Always ready to travel.The ship is boarding now.After it departs, I will spend some time gathering intel on Mr.Duncan.Thank you.We should be able to find them in the flesh once we get to town.Duncan and I go way back.And I'll introduce you to another friend.She lives in a bottle.
```

### [56] hash=`5e071c3647028d8f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
I'd be delighted to meet your friends.We should be going now.Lilia, I've told Admiral Eagle that he can rely on you for further assistance as necessary.Is that all right with you?Yeah, I'll do whatever he is doing.Have a good trip!Admiral, a prisoner has gone missing from the tower.We'll make sure it's kept under wraps.The seal was broken and we are still investigating who might have been involved.
```

### [57] hash=`60f749e6dd1d6fac`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
I did encounter the Time Keeper, Mesotoby and Lopera near the tower yesterday.Still, I see no reason to suspect them.The Time Keeper doesn't have any incentive.And Lopera?No, she wouldn't be involved.Find the prisoner, but don't attempt her capture.Let's see who she's been in touch with.Understood.Lieutenant, this was a failure that must not be repeated.Look at those strange cowboys!What's they doing with those hooks?
```

### [58] hash=`f0d224ebc636999f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
Are they trying to hitch a ride?Yes.They will use those hooks to grab onto the side of the ship and moor their boats to ours.Take this, timekeeper.What's this?Just a map, in case we get separated.These will show you the way from the harbor to the veterans' residence.Though, it can't show you the safest way.For that, you'll need me.But what am I saying?San Paolo is perfectly safe.That's what the politicians say anyways.
```

### [59] hash=`e9ce4c0e512ea877`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
Never mind the talk of gangs, cartels, and greedy multinational corporations.Pure slander!Thank you for the warning, and the map.Let's hope I won't find any occasion to use it.I hope so too.Well, we have a long cruise ahead.I'll leave you to your business.At the mice.So the kitchen even prepares food for them?My darling, you boy, back to your place!You walk or there will be no dinner for you tonight!
```

### [60] hash=`983274efdd4ef3d6`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
Hey, out of my way!Miss Burton, did you notice that boy?Wasn't he awfully strange?You're right.Come on, let's go see what he's up to.It's you!What are you doing here?I was about to ask you the very same question.Burton, pleasure to meet you.Please, take this.Thank you.Have you found what you lost since we last met?Perhaps I could help.Thank you, but I would prefer to do this on my own.I was the one who lost it, and I will be the one to get it back.
```

### [61] hash=`388d529d1f9ffc7e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p4`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（04.【离岸流】）

```text
This ship is headed to São Paulo.Is that why you're heading as well?Would you like to accompany us?I don't.There isn't anything for me there.Only a bit of misery and pain.No feasts or banquets.Nope.No.I would rather we simply part ways here, Miss Virgin.Farewell and pleasant journeys.I'm indebted to you for your kindness.And your friend here.Aren't you just a sweetheart?Oh, I could just gobble you up the tea.

Madam!Please!He isn't proper or ladylike!
```

### [62] hash=`1bfa08fa6bace730`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p5`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（05.【地狱之船】）

```text
a few treats to buy their worship and they call it kindness how undignifiedto be reduced to begging for scraps like a dog dignity doesn't count for much in the face of hungeryet no man can live by bread alone and yet none can live without it you're a clever girlsenora but i hear from your accent you are no local so what brings you to san pauloBusiness, ne?I have some business myself in the favelas.
```

### [63] hash=`2e8b0c352ddaae01`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p5`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（05.【地狱之船】）

```text
Colombia, senor.And now, only a visit.To the Sant Paulo Veterans Residence.It's a safe place.If you find yourself in trouble, you should seek it out.Oh, is it now?Thank you.You're very kind to offer.Care for a game of dice, senorita?What's the bet?Well, let us bet against the goodness in one another.Let us say that the loser will cover the cost of all the food given to all the little vendedorestoday.
```

### [64] hash=`5124f6d2dbd4340e`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p5`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（05.【地狱之船】）

```text
In the winner's name, of course.That's no small wager, senor.Still, I appreciate the good game.High low, then.Who goes first?Ladies first.Low.Let's make it more interesting.Six.If it rolls anything else, you win.Do you mind?I lost, just as was meant to be.So then, I am to be the vehicle of grace today.Might I have your name, senora?So that all may know the name which is to be sung in paradise today.
```

### [65] hash=`abf3e06ce8e1bcbc`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p5`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（05.【地狱之船】）

```text
Carlota Lopez Rivera.But it is Lopera, should you ask after me.That's an interesting die you have there.It was only luck.What's going on?Do as I say, all of you!Look, Furtin, there are some more river cowboys over there.I'm afraid they seem more like river pirates.Stay back, Sotheby.What do you want?Where's the captain?We're changing destinations.The ship will be docking in the favela now.Or we'll blow it all to bits!
```

### [66] hash=`9317a61639b31b40`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p5`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（05.【地狱之船】）

```text
Get out of the way!Hold your fire, Lepera.There are oil drums on board.Slimy rats.Either we go to the favela or to the bottom of the river, claro?Make your call!The favela?Are you with the apostles, brotherhood?They forced you into doing this, didn't they?Hijack the ship and bring it to us.Is that right?Too bad for you.These ships won't be making any unplanned detours today.Stupidos!Get down!Blazebusters?
```

### [67] hash=`282a0fddffcd0b67`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p5`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（05.【地狱之船】）

```text
Lifeboats!Get to the lifeboats now!Sotheby, you need to jump now!Join LePera!Situations...Things went sideways.That's what happens when you put guns in the hands of amateurs.But you handled the water better this time.You controlled your breathing, kept your airways clear.And this time, you remembered to lie back and float.Does it matter?I'm all you've got.Listen, I'm not here to run your errands or play your messenger boy, so ask nicely.

There's nothing more I need to tell you...for now.
```

### [68] hash=`b7eeca7f1fb5d794`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p6`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（06.【杰出演员】）

```text
The Brotherhood just took a beating from Zeno.If they're caught up with their own trouble,then we might have a golden opportunity to turn the people against them.We can't lose anyone else to their lies.What do you say?Want to talk about plans?Here, drink up.Thanks.Listen, as much as I enjoy being out here all day,we've got to take action now.The sooner the better, don't you think?Hold your horses, young Elemo.
```

### [69] hash=`70a5ea952008dc34`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p6`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（06.【杰出演员】）

```text
Let me explain.Say I throw a punch at you now.Really hit you good.What next?Maybe you'll storm off at first.Then you round up your cousins.Maybe grab that tommy gun you borrowed from Colonel Tiago.And you'll find me all alone and say, you're done, you old fart!It'll only cause them to lash out more.Still, we do have to consider one thing.Those who chose to follow them never come back.No, they don't.
```

### [70] hash=`059ee555910a14d1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p6`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（06.【杰出演员】）

```text
So, let's seize the day.Grab opportunity by the horns,and maybe we stop losing more of our friends to those bastards.Right now, seems to me that Xeno is our best bet.That just might work on that.With the brotherhood falling apart, Zeno will certainly look pretty good to folks here.But not so fast, kid.We need a little patience.Let the line out a little first.If you fail to prepare, you're prepared to fail.
```

### [71] hash=`19a80d1e3b6556da`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p6`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（06.【杰出演员】）

```text
Excellent!Don't think you can get away from me!You like to wrestle, huh?Alright, let's see who gets the upper hand!Easy now, Lopera.We just cut her out of that fish's belly.You're a veritable Jonah, aren't you?Dreamt of a very, very big fish.I was in its belly.It was as wide as the sky.I couldn't breathe.Please, strange dream, Mr.Carson.She's awake!Carson?There's a little dirt on me.Here, and on the collar, too.
```

### [72] hash=`ba6fe8d078f3fbf6`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p6`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（06.【杰出演员】）

```text
Oh, goodness.Why am I here?I- Will it be you, Mr.Carson?You must be mistaken, little lady.My name is Duncan.I'm a friend of Lopera.That's right.So to be, this is Duncan from the veteran's residence.We've known each other for a long time.You must be confusing him with someone else.Now, up on your feet, little lady.Sorry, I didn't expect you to suddenly pull my arm.Pardon me, little lady.We tend to be very straightforward here in the favela.
```

### [73] hash=`58475a6cd2d4d4fd`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p6`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（06.【杰出演员】）

```text
It's quite all right.You look exactly like Mr.Carson.How could you be anyone else?Except for your attire and those shoes.Oh, pardon me, little miss.Are you not comfortable with us drinking?Galeno, put the cup away for me, please.
```

### [74] hash=`428c5c973eedffc0`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
I've never wanted to put Sao Paulo to this chaos.Order, peace, unity.Those are my purposes.Much has been wagered here, Marcando.Much.Now it has been lost.Your reverence, it was Zeno.Those animals will make them pay for what they did.Is that why you've decided to grace us with your presence,your reverence?There is a lot to do if we're going to recover the ground we I've lost your reverence.And there's something more, a new doctor down at the Vedran's residence.
```

### [75] hash=`b8ee597b50514bed`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
Some blind woman.I would not bother you with it, Lord Santos, except that she's been helping people inthe favela, and it is swaying them, poor Zeno.Then this doctor is with Zeno.She must be.She's always at the veteran's residence, spends most of the day with those old war dogs.A doctor gaining the trust of the people in the favela.She'd make quite the prize, wouldn't you say, Marcando?A much more valuable bargaining chip to Zeno than a few deserters.
```

### [76] hash=`c6fbea22d8a62604`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
You will see this task through, Marcando.But before that, to pay a visit to the favela, I've brought us some new blood.See?Just like this.Wrap the wire around it.Better do it twice, and align the red and black, slowly.Unbelievable!It's science, kids.Nothing unbelievable about it.I don't know how to thank you, Duncan.Admiral, Lopera just called in.Put her through.Lopera, it's me.What happened?Our ship was sunk.
```

### [77] hash=`9a85e3a5c8d6cad3`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
Ms.Sotheby and I washed ashore near the favelas.As for the Timekeeper, she went overboard.We lost sight of her in the commotion.Her current status is unknown.We'll send people to find her and escort her to the Veterans residence.Additionally, Lieutenant, I have some fresh recruits eager to enroll with Zeno, but they will need the Admiral's assurances that their families will be under our protection.
```

### [78] hash=`ced8bcb42d03a446`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
They have it.What's their ETA?They'll leave at once.Tara!That little hothead.Sir, your orders.Leave the matter to me, Moldier.I will send someone to take care of this.What did the Admiral say?He agreed.Did you hear that?Xena will protect us!I have no doubt.They were working for the Brotherhood.The Apostles' Brotherhood?They've bounced back quicker than I'd hoped.Still, we need to be cautious.Figure out just what they're after.
```

### [79] hash=`81ecaa394bd2fe5a`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
Our days of anguish and deprivation are over.This sufferer will walk among us once more,and we will bask in their divine grace.The day of triumph draws near.Soon our wagers will pay off.All will reap what we have sown.You only need stand with usand take their blessings.In return for this, they ask only for your unwavering allegiance.My brothers and sisters, speak!What do you seek?Señor, please, we only want to see our family again.
```

### [80] hash=`ab730812eab116ef`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
Since they've joined the Brotherhood, we've had no word.We haven't seen or heard from them at all.Ah, but you will see them again soon.I tell you that they are even now faithfully serving our kind in a new land of prosperity.They're in Ushuaia, in Antarctica, in all places where the past and the future converge.There will be no more poverty, no more hatred, no more chaos.we shall reclaim what's rightfully ours remember this humans are vile and
```

### [81] hash=`1e318f510ea3f4b6`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
sinful creatures they tortured our men and women leaving our children to cry inhunger and desperation but they've already played their hand all theirreason their science and their despicable organizations they raisethese rotten edifices to weaken us and leech off of our misfortunes, to blind us from ourtrue purpose.But no longer!Soon their games will be over, and every injustice and oppressionthey've held over our people will be returned tenfold.
```

### [82] hash=`c769a4f01949dca1`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
All that they've built will crumbledown over their heads.Tell me, my fellow brothers and sisters, what is evil?Evilis the absence of good, and to find what is good is to follow our path.The High Onehas promised us strength and glory.Come with me.Samanas, Mosque...Sorrow will weaken you, and fear may seize your hearts.Instead, let faith be your guide.Those who take that leap shall find themselves lifted up on the Apostles' wings,
```

### [83] hash=`cd63eb0be91d9347`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
while those who hesitate will be scorched by the fires at their feet.I have said all that must be said.Is what he said the truth of it nowYou'll give me the names of Zeno's new recruitsWho are they?I'm not gonna harm you kid and if ever I doRemember that old Duncan must have his reasons and he'd never harm a friend intentionallyThis young man has one day to think it throughHe will give us his names, or he will give us his eyes and tongue as offerings.
```

### [84] hash=`46912103eff238a2`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
Mr.Duncan, let this task be set on you.Prove yourself worthy of our trust.It will be my honor, your reverence.Marcando, you'll stay with them.Don't forget what I told you earlier.This place was once known for its inexhaustible mines, the riches of its rainforests.But that gold has lost its shine, and their silver spoons have tarnished.Everyone can see them for what they really are.So what now?Either the people save themselves, or turn their fate over to the hands of the so-called
```

### [85] hash=`cb4a01573aa7df7f`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p7`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（07.【无端指控】）

```text
savior.What would you do if it were you?Who's asking the questions here?Me or you?Learn the dates when the dealers bring their medicine into port and figure out which water tanks hide the key to the local gang's safe houseDon't look at me for answers.It's none of my business
```

### [86] hash=`c01ccf5399b7317d`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p8`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（08.【河上的生与死】）

```text
In the narrow streets, violence is so often more than just a means to ending conflicts.It is a tool, and one all too readily used.I must note, however, with some relief thatsegregation so commonly observed in other regions is absent here.The Arcanists ofSão Paulo live alongside humans, with the latter often displaying traits more common toarcanist neighbors.Passionate, if a bit touchy.Life here is incomparable to the comfort,
```

### [87] hash=`f3136a768f4a8457`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p8`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（08.【河上的生与死】）

```text
security, and freedom of New England.Hardship, violence, and oppression are the fundamentals oflife.As constant as the sun and as heavy as the rain, this country is renowned for its coffeeand sugar, it is a land of beauty and bounty,treasures too often extorted,whether by the princes of Europe and their donatarios,or now by the bankers and corporations.Despite all the centuries of treasuresextracted from the land,
```

### [88] hash=`2d8221b82ab5b5c7`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p8`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（08.【河上的生与死】）

```text
desperation remains everywhere you look.It is a place where insurmountable wealthand the deepest deprivations are neighbors.Sometimes they lie only a street across from one another.The multinationals have cut open the country's throat and now they drink it dry,leaving the people struggling with poverty and chaos.It is a bleak existence.Dear readers, I share this with you so the story of these people might be heard.
```

### [89] hash=`2af455ff5b05b189`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p8`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（08.【河上的生与死】）

```text
Shippy, do you know, has life always been like this here?If you ask me, Doc, San Paolo in 1990 isn't much different from Nassau's 1681.It's a shame.Between the sunshine and warm sands, there is a good life to be lived here, if only they were free enough to live it.I used to dream of traveling to all sorts of fascinating places.a foggy city by the Thames, and a little townblanketed in snow and sunflowers.
```

### [90] hash=`7eba6bc6632fda10`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p8`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（08.【河上的生与死】）

```text
I met so many different people, though I find I can no longer recall their voices.I have only their words left, only my records of them.Have you heard of a weed down at the bottom of Lake Ilopango?The people there turn it into a polenta with cornmeal.supposedly if you have it you'd recall every last thing that's ever happened toyou every bit of it oh so we called they call it la hierba del tonto Spanish for
```

### [91] hash=`b5b0755103a043c8`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p8`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（08.【河上的生与死】）

```text
the fools weed you see lad only a fool would want to remember everythingsometimes a little forgetfulness is a blessing in disguise I beg to differpain and joy alike.That isn't a blessing.It's oblivion.But let's not argue oversome mythical weed.For all the claims no one has ever seen it.Just another myth.Like the succubus, or the minotaur.Aye, aye.Let's talk about succubi instead.That's sure to get the lads pricking up

their ears.Back in 88, I mean 1688 of course, our chief mate, Mr Morgan, had an encounter
```

### [92] hash=`9c4708da0df6dab9`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p9`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（09.【惊情三百年】）

```text
So you weren't even traveling together.And still you brought her all the way here.You have a good heart, Miss Kimberly.You flatter me, Doctor.It was only that the current pushed her to my side when we all fell into the water.And I just couldn't forgive myself if I would let her drown.In fact, she and I had met briefly before, in Texas.We didn't part on the best terms.Some hanged, some drowned, some we marooned on a desert isle with naught but a pistol and a flagon of rum.
```

### [93] hash=`26cfc0ac2ce5e161`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p9`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（09.【惊情三百年】）

```text
I've been to Plymouth, Nassau, Port Royal.I once even slipped into Seville disguised as a merchantman to smuggle pepper and cinnamon.Wherever the captain wanted to go, we sailed.But one by one, Davy took them all.Is he sick?I hadn't thought your kind capable of it.Neither, no!Karamba, I like this girl, she's feisty.You're with the brother of Gorota.You apologize, now we might just let you go.Or don't you know that Lord Santos is back?
```

### [94] hash=`2cec6870671daef7`

- lang：`en`｜version：`2.2`｜arc：`忧郁的热带`
- doc：`BV1QutpeVEHo_p9`
- title：《重返未来：1999》2.2版本主线「忧郁的热带」全剧情 - Reverse: 1999｜4K（09.【惊情三百年】）

```text
We can make this rougher for you if you like.Careful me lads, I wouldn't pull those knives.Things may go rougher than you bargained for.If there had been any doubt of what you are, Lass, that fight sure cleared it up.
```

