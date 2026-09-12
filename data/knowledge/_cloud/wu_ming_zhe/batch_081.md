# 剧情图谱抽取 · batch 081

- 角色：`wu_ming_zhe`
- 批次：**81** / 共 1 批（每批 95 块）｜本批块数：**92**
- 筛选：标题含「1.5」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_081.jsonl`

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

### [0] hash=`3490233f721ffa4d`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
At the end of the 1970s, Laplace researchers who intervened in the local environment protectionfound that, unlike other fungi which reproduce through the spreading of spores, the honeyfungi spread by the growth of their underground mycelia all over the forest.You think it's like that invisible net?Yes, a net hiding underground, in which you see an object disappear at point A and magicallyemerge again at point B.
```

### [1] hash=`99cb43418d5d4d70`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
The reincarnators are very similar to Australian honey fungusin this aspect, and with her breath, a small amount of her saliva and the dousing rod,we will be able to find her net and map her movements on it.And when her gazeblazes the Amphilardus nidiformis.Amphi...Amphilardus...what?Isn't that a ghost fungus?Yes, the ghost fungus, the mushrooms that glow in the dark.They're called chinga in older times,
```

### [2] hash=`391e761ecc43fc96`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
which means spirit and soul, the sparkle of ideas in human minds.If the mushroom has simulated Spathidae's gnat, then these two light spots are...The one closer to us represents the current Miss Spathodea, and the farther and brighterone is what put her through the changes now.So that's me in the past?We'll gradually turn into...Five minutes.We are right on time.Miss Desertflannel, how do you feel?
```

### [3] hash=`d01c3f34782da034`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Dammit, if she's so badly injured, how much would the compensation be?Is this how my life will be?Being heavily in debt?Ms.Desertfunnel, you're nibbling at your nails.You will get hurt from it.Please stop.I'm fine.You...are you talking to me?You were saying?Yes.I was asking how you were doing.Did you get my drift?I...I think.Well, I know it's highly unlikely that this little girl was hatched from a dragon's egg,
```

### [4] hash=`51f56ec72b7d34f5`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
but is it possible that she's just some kind of uncommon lizard?You know, the really ancient ones?Any anything but a reincarnator, but what you said doesn't make senseIt doesn't make sense that was fire coming out of her mouth family here is a pixel in youDoes it make sense to you?I?Don't follow IKnow this is not your fault.It's just your arcana's nature taking overIt's very normal if you got too carried away by your emotions and became delusional and hysterical
```

### [5] hash=`6ffa822eabefcbeb`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Please, take my hand.I was once trained to help Arcanist calm down.Now breathe with me.And out.You know about Arcanist.You're not even one of us.Everyone.Please, believe me that I meant you no harm, Ms.Balthadir.I was only trying to help.How?By calling us delusional?There's nothing I hate more than humans like you saying that others are over-emotional.People.No.Nothing like that, Miss Spathedia.It is not my intention to criticize anything or anyone.
```

### [6] hash=`4239b52383e5215d`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
It's just biologically,Arcanists tend to be more sensitive and easily affected.I also like Arcanists,almost as much as I'm interested in mushrooms.That's why I studied him.Hmm, do you smell something burning?I tried to warn you.It has grown larger and largeras your lizard hypothesis heated up.I'm sure the guards of Laplace will break in soon.Security of Laplace Research Center Hospital taking over.
```

### [7] hash=`40e8d1838947ca6d`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
All patients and non-staff please follow me to evacuate the room.Evaluating fire level.Level 2.Extinguishing the fire.Source of ignition confirmed.Request for permission to use kangaroo foam fire extinguisher 3.I don't know why but it's important this is for sure.Those bubble kangaroos will kick its butt once they see the flames.I don't want that.I'll protect it for you.Don't worry.There you go.Now you're free from the fuzzy foam.
```

### [8] hash=`b1a5fe5c01d96122`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Thank goodness.Um, I mean, thank you.Though I still smell like a Joey.I'm much better now.In the early stages of Arcane Ability Awakening, the rate of Arcanus losing control can reach 74.3%.But it doesn't mean that you can set a fire in the clinic of the Laplace Research Center Hospital.Or fight the security to protect the flame.Sorry, I didn't mean to do this, and I have no idea why my flame grew so...
```

### [9] hash=`1994f818c4cf26fa`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
so large all of a sudden.That never happened before.I know I should have been responsible and noticed the anomaly earlier.I was completely lost in the argument.The silver lining is, as the fire was still under control, they used the kangaroo foam fire extinguisher and thus it didn't cause any casualties.Please write down your emotional changes and physical reactions that occurred during the incident on this sheet of paper.
```

### [10] hash=`9d8d863d7a6686b5`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
We'll keep tracking your physical health information.The concentration potion is on that table, and there are blankets and Type 2 PMMA safety boxes in the cabinet under the table.Please keep the hazards sealed for safekeeping.Okay, you are still in an unstable state.Please have a rest here and don't move around.If you need anything, please press the call bell on your left and our nursing staff will come to help.
```

### [11] hash=`ae5de04513f9a02f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
In case we burn, the box she mentioned is...Oh, here it is.Oh, freedom matters, little flame.We have no choice.Sorry, buddy.Alright, listen.My teacher said fire needs oxygen to burn.So I'll leave a small window for you to breathe.I...Wait...Wanted...To...You...Are you talking?The cobraTwo Uluru GamesUluru Games?What's going on with the Uluru Games?
```

### [12] hash=`c4f678bb0d253f2b`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Is this the Laplace fashion of dealing with emergencies?I swear if anyone walks past us now, schoolers or deros,I will be instantly killed by their silent judgement.As a matter of fact, when the patient or the subjectbecomes unstable during contact,it is necessary to isolate themfrom the triggering cause immediately.But we just burnt down the isolation room.No wonder Head Nurse Judith was so angry.
```

### [13] hash=`cc844494129e81ee`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Miss Vertin, are you all right?That kangaroo is punching your nose.I'm fine.So is the kangaroo.I'm sure Medicine Pocket will bring usthe concentration potion soon.We look like a bunch of kangaroos,feel like kangaroos, and even smell like kangaroos.We will make tomorrow's headline of the Australian nagaand become the three kangaroos hanging outon a public lawn at midnight.That'd be the end of our social lives as humans and the beginning of a life as kangaroos!
```

### [14] hash=`456a90c0d56e1c82`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Make the headline?Ah!I see.Please, don't worry.Although it's true that Medicine Pocket is a frequent celebrity on the news, the concentrationpotion is not their work.Besides, we didn't use anything new in its development.I'm not worried about that, guy.I was talking about myself.There are paparazzi following me around these days.I didn't know you were famous.I'm not!It's just that someone wants my name spread in a bad way.
```

### [15] hash=`bf4a46bced491306`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Ugh, trust me, you should never piss off the paparazzi.You should turn to the police for help.Yeah, yeah, just shut up and keep your eyes peeled for anything suspicious.I will toss his shoes on the power lines if I find him here.Ms.Desert Flannel!Watch your back!What are those paparazzi-Ah!It burns!Is this...fire?Ms.Desert Flannel, the lake is over there!Get in there!My kangaroo kicked me!I can't see where the lake is!
```

### [16] hash=`80ca138430f0c6bf`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Wait, calm down.You are not in danger.She is.Are you joking?I was getting burned!Huh?There's nothing on my skin.Didn't cause any damage on me.Just burning the foam on my skin.Is that some new method developed to get rid of the potion?But what is Miss Spathedia doing here?The head nurse shouldn't have let an unstable patient walk around freely.Did...did she sneak out?Gosh mate, she's on fire!Does she even remotely look stable to you?
```

### [17] hash=`d24c12caf4daaaca`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Rice like a deal.Stipping on the red soil where vines and woods grow.She's as well heated as a boiling pot!We can't let her go on like this!Her brain is going to be roasted in that little head!your temperature is dangerously high chill out I'm not a lizard and concretenumber two with cream is the best dish in pipe material but the deer issuffering confusion it's probably the flames doing we need to separate them
```

### [18] hash=`c1d3e1037774a41d`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
first okay okay miss Burton please step back this is just some sporesmiss desert flannel worry not they are the tranquilizer that the locals usedpacify animals and was once widely used among our canists in early times for hunting.As long as we calm her down, we can bring her back to...Meet the real games.This is where sportsmanship originates.Young people.Young people!Did I use the wrong mushroom?
```

### [19] hash=`1fb9922d0a390412`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Miss Spathedia has become even more restless.What about Miss Desertfunnel?Is she...?No, you didn't.She's behaving exactly the way you described.Is it, Flannel?Is this the house for me?Does this mean I don't have to pay rent anymore?Looks like this is how she has her mental break.I will bring her back to normal immediately.It won't take more than five minutes.But I think Ms.Spathody is going to attack again.
```

### [20] hash=`ca35c69d0181e191`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
What we need is the reopening of the gate to the Scorching Land.And the retrieval of the rock.Fire is getting stronger!Get down!We are running out of time.Let's deal with the burning issue first.I will.I will try my best.Be careful, young man.Fine.What are you doing here guys?I thought you were driven away.I remember it now.It's about the deer.We must revive.I've heard what's going on.We will check if her organs are injured by the high temperature after returning to Laplace.
```

### [21] hash=`372c04ee3be4ee52`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
You can visit her tomorrow after 11am.Can we visit her?I thought you will send her to the wards on the 13th floor.Go with the flow when you can't fight it.We've now understood what will happen if we separate you and keep her alone someplace else.What's more, Laplace can't lose another clinic.I see.This is great, thank you.Are you sure those mushrooms won't cause any damage to my brain and body?Like lower IQ levels, lung diseases, or skin allergy?
```

### [22] hash=`c985958a1a04f848`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
Um, if you think it's necessary, I will accompany you to Laplace for some follow-up check-ups.Of course, you don't have to pay for the tests.The fee will be deducted from my salary.Please, don't worry about the money.Okay, okay, enough.I trust you.I don't need a kid to pay the doctor for me.Besides, it's embarrassing enough to be put down by mushrooms.Not to mention that I'll be given that guy the story he craved if I was hospitalized.
```

### [23] hash=`3846c5ecaf761847`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
That guy?Oh, you mean the journalist following you?Speak of the devil.yourself!Don't make me force you!Makua, don't you dare involve others.This is between you and me.I've told you long ago that one day I will make you feel the same misery that I did.I have been following you all the time.And this is the moment.The moment of vengeance.Now I have more than enough photos.As for these other people,you didn't strike me as such a kind-hearted person I didn't know you
```

### [24] hash=`e9e82f349a1de0c6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p4`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P4【后手直拳】）

```text
were so shameless let's see what tomorrow's newspaper has to say aboutthis missed photographer photo of us he your enemy maybe arch enemy whathappened between you two if you don't want to be one of the burning kangarooson the headline tomorrow shut up and start running we have to stop him
```

### [25] hash=`55226481f6c41a82`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
G'day.You got the latest Australian naga here?Nice choice.Everyone is talking about it.A strange party held in the city park last night.The witness claimed to see the burning kangaroos,mushroom-intoxicated rolling croc, and the teenage arsonists dancing together.A secret event on the public lawn?The revival of the Uluru Games?It saddens us to admit that the recession and inflation have walloped some young adults.
```

### [26] hash=`37f5aa7c1f6efd41`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
They were crawling in the park at night, groaning and moaning like beasts, dragging themselvesalong and losing consciousness.Wade, your voice, are you...Do you have to talk to me right now?I'm busy hating my life.I don't have time for your little chit chat.No way, desert flannel, it's really you.Everybody is talking about you right now and they can really imagine.Some say you're mad.Some say you're the heroes fighting against aliens.
```

### [27] hash=`fb358a97c57c5ab4`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
Well, the most known story is that event.Is it real that you're going to restart the games?I have nothing to do with it.It was all that Junior's fault.I was just unlucky.It was pure bad luck that I ran into those weirdos, got taken to the hospital andlet Makawa get what he wants.I shouldn't have let him get away.If I see him again, I swear I will pull out his tongue and tie it around his neck.Oh!Look at this gibberish!
```

### [28] hash=`f4becfaa2aa13a6e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
He said we are the dopeheads who eat bunyips from the sewerage, a burning kangaroo, andI am a nutter because I can't find a way to afford rent!Oh, this is great, I might as well be a kangaroo.At least it's true that you're banging your head against the wall for rent.Yeah, mindful that you're talking to a nutter.Whatever.I will soon lose my part-time jobs and be kicked out of the house where my granny lived for decades.
```

### [29] hash=`d428711a16c83eb8`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
I'm heading back.Let me know if you know of any job vacancies.I can do a lot of things.As long as the money is good.Nah.As long as I'm paid.Wait!Desert Flannel!Come and take a look at this.So many people came here this morning asking about the Uluru Games.And one hour before, the Scissors Jerry brought me this.This is a pre-sale ticket to the Uluru Games?I've sold over 50 tickets at a unit price of this much.
```

### [30] hash=`b5490ddb230e4d8c`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
It has been suspended for too long.So long that everyone thinks society has forgotten it.But we remember.Our ancestors told us about those amazing and funny sports.That big, wide, fancy stadium.They all remember it.Even looking forward to it.And even bid up for a fake ticket.Mate, did you get more of these from the other gangs?Two boxes left.These are from the Slicky and Eucalyptus Brotherhood.Eucalyptus and what?
```

### [31] hash=`5eb16dfad9ee05e7`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
Didn't catch that name.Oh, do you have the mints that I bought from you before?The least purchased ones?You always put them at the bottom of your box?Alright, now give me my ticket back and I'll put it away.I don't want any of the gangs to find out.dealing with the other desert flannel that's what i keep telling everyonemoneying the water is what this bad girl doesthat's right desert flannel has taken the fake tickets with her
```

### [32] hash=`13f6efc6a9cefa6d`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
the ones from clippy slicky and the eucalyptus brotherhoodshe's gone no not to the black market siri heard that the bunyips are getting restless again is that trueI'm gonna make a fortune out of it!I will be able to buy that house, get myself a new oven, some new clothes, and that giantwool nest for Pleppy!Those bunyets are out again!Haven't seen them out in the sun for a while now.I must hurry.Wait, are they coming my way?
```

### [33] hash=`dcb23d276cb20732`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
I've got my eyes on them.They are more interested in her than in me.Oh, this makes sense.Since the Uluru Games have made the biggest news of the week, the people are going on and on about it all day.And where else will the rumour-loving bunyeps go at this point?The last time I saw something like this was when that scandal of Mr Pompadour broke.It will be a big story.Almost as certainly as a cut will bleed.
```

### [34] hash=`8961a3b8dbb68462`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
I will pause my other projects and focus on this one.This is very kind of you.I really appreciate it.Nobody, nor any arcane creatures, can stop me from getting rich.Let alone that you haven't eaten enough rumours to grow into a three-floor-high and multi-legged, gigantic monster!Happy, give me a hand with that smell of rumours from the ticket box!Come get it yourself!Told you I'm super healthy!You should let me go now!
```

### [35] hash=`a741f9de51b395b0`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
But you need our care, Ms.Spathedia.It's also our responsibility to make sure that you're safe and stable.When arcanists were first introduced to their power,They would experience a four to twelve week adjustment period, during which they may suffer emotional breakdowns, strong hallucinations, or frequent comas.I have something very important to do right now!I mean it!I'm here!I'm fine!There'll be no more confusion, mental breakdown, hallucination, or coma!
```

### [36] hash=`00a136311b5e568b`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
Something very important?What is it?Iflame talked to me this sleep.I think it's exhausted after her rampage last night.I think that's my memory as a reincarnator.I saw my own body in that window, just like the one I'm looking at here.I saw a lot of flames, wobbling lights and people.My heart has never beaten that fast, yet the fire in my body seemed completely natural,as if it was destined to burn inside me.
```

### [37] hash=`7ee10b68324fde61`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
It whispered just one phrase to me, again and again.Like what you mentioned last night.Survive the Uluru Games!What?What are you going to do?Let's not get to the paperwork of applications, security arrangement and permission from the local government just yet.The location of entrance to the Uluru Games was never fixed.Only few Arcanists could find it, and the games are for Arcanists only.There has never been a human athlete in there, and they have been cancelled for all these years because
```

### [38] hash=`aacb8425a409a8a7`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
You?On the way?Coming too?Of course.We've been through so many things together, am I not part of the team?No, of course not!What can I take you and the revival squad?For our keenest!You read the documents, right?Since the very beginning of history, humans have made countless attempts to find the entrance to the stadium, yet none of them made it.It's just not for humans!You are such a rare opportunity to us, because none of us know when and where the next reincarnator
```

### [39] hash=`ffd1d56b9730f900`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
will be found.If we miss this opportunity, the academic circle may have to wait for another decadeto further their research.The discovery you and I made may shock many.Our names might go down in history, but most importantly, it's going to help alot of people.Have you heard of Cengiz, invented by Dame Parodi?It was inspired by a long-legged shepherd in France, and it has helped many athleteswith disabilities to walk and run again.
```

### [40] hash=`762909f0fb93d475`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
Miss Batherdia, you look miserable in the blanket.Keep going, Ezra.You're very close.Me?Close to what?I don't follow.Well, speaking of close, guess who is close to becoming the most successful businessperson here?Desert Funnel.Where have you been?But I thought, I'm not some monster crawling out of the syringe.You look a mess.What happened?I didn't ask you why you were crouching in bed like an ostrich, did I?
```

### [41] hash=`f75f43794a6ae213`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p5`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P5【漂浮球们】）

```text
So maybe you can return the favour and keep your nose out of my business, yes?And what really matters, is the good stuff here.Know how unbelievably lucky we are, my dear business po- uh, friends?Yeah, no.I don't.Ezreal alone is already too much information for my brain.Fine, you restless and humorless people.We'll bring back-Hey!What kind of reaction is this?Why are you quiet as stones?This is a great idea.

And you're giving me this?Join my revival squad.Handshake?Handshake.Then I-No!Not you!
```

### [42] hash=`160d46deb2a7a7f1`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
We also have the budgerigar coat as an emergency measure.So that's why Ezra took you to the room before we left, to tell you all this.Ezra is worried about you, and so are we.Oh, someone is feeling bad about what she said earlier.If you ask me, that human girl has a good heart.Maybe she can work on her ways of communicating with people,but that altruism in her is almost angel-like.And she has the face of a little angel wouldn't be such a bad idea to put her in some baby care commercials
```

### [43] hash=`ced23b0a52f331e5`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
I heard those things pay you generously.I might as well ask what she thinks, huh?Who's talking again?It sounds the same to me.This is just the sound of fire burning snoring like my late old manWell, maybe you can also try turning off this little thingy's TV.Maybe it will jump up and shout.I'm still watchingI'm not joking it's really talking listen wait its temperature has gone upand it's transforming what is this a rocket no we're waiting everyone mind
```

### [44] hash=`d7d2adf149cdcd86`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
your steps and keep up in the desert I wonder why I'm not as clever andcreative as you are miss Ferdin was she talking to me she always looks overPerhaps she knows that I'm following them, but no, I'm hiding well.They shouldn't know.Having emotional turmoil, acting impulsively, feeling fanatical about the retrieved memories,and the unstoppable urge to return to the homeland all match the description in the research notes.
```

### [45] hash=`6ee38c52944c1aef`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
And now the fire, which is also the key in this case, is burning vigorously.The notes end here.That's all we know about reincarnators.can't adopt more based on the current data, but at the same time the unknown can be dangerousyet exciting.It may bring about catastrophes or miracles, just like arcanists so charming and lively.My job is to help and protect them, so their burning enthusiasm will not be dampened.
```

### [46] hash=`a4c4bf8942fe3c7f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
Like what Mom said, this is our mission as mankind.Annual Jump of Frog Mushroom, the Fairy Ring Powders, and the Butterfly Shaped PortobelloMushroom.Very well, I have them all.This time, I'm prepared for any danger.We're not running away from the journey.The beginning of the journey?No, we set off from Melbourne.We're close to Uluru now, so it's almost so distant.What are these?These are murals.No.
```

### [47] hash=`216fb4b0a0678d76`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
They are reliefs, all the marks are carved out of the wall.These carvings existed long before any murals, and they are rougher.Of course they are, just think, when did our ancestors learn to draw with paints?And when did they start carving with sharp stones?They're beautiful, like star trails, one circle and another, I think I've seen thembefore.These marks have to mean something.Maybe they will lead us to the entrance to the stadium.
```

### [48] hash=`6b8569efbc84d6d7`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
This is a time when Spathadia's opinion matters more than ours.Come, key girl, take a look at this.Spathadia?Where...where did she go?And that fire...they're all gone.What the hell is going on again?She better be pulling a prank on me.I heard her footsteps behind me just now.Relax, Desert Flannel.We've got help.Ezra?How did you get here?Wait, how long have you been following us?From the beginning, when you were at the hospital.
```

### [49] hash=`6dcaa539b8b87b1e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
Sorry, Miss Desert Flannel.Please let me check this first.This smell.I can't be wrong.This is Devil's Thorn.What's that?Does it have anything to do with her missing?A rare kind of mushroom that grows in the desert.Allegedly it's genetically connected to lizards.I've only seen its pictures inbooks.It has wide open pileus with sharp spikes and its roots are as absorbentas a sponge which allows it to absorb and preserve underground water.
```

### [50] hash=`f78ee9af514dc040`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
Theyonly appear around water sources and with this spiral pattern on the wall Ithink, think I might have a way to find her.Please come with me.Flame, throat, it hurts.Do you remember me?I travel through the endless flood, drought, rain, and waterfalls to finally reach you.Do you remember me?I do, but not really.Recall your name or your face to remember.Remember our fight.Intelligence and spirit we are bound to find.
```

### [51] hash=`815c02fb535f3511`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
Help with you, you dumb ball of fire!Neither do I, you scurl!My hands are burning, like they're soaked in fire.That's because you reached into me.We had a fight, attacking each other with nails like two cats.I can feel my knees trembling again.I know this game, a sport which is not popular enough to be included in any commercial or professional games.It's also the sport for which I've been secretly training myself every day after lunch.
```

### [52] hash=`2a65b3c65065664c`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
The lightbulbs picking game, Lingy's Harvest.No, not lightbulbs for the athletes to pick up from the ground, but fire.And I don't have such a burning campfire at home.It can only be found here, beside the flowing spring, under the starry sky, on the scorching sand.I saw the burning campfire and the sparks scattering in all directions.My hands surrounded by blazing flames.I touched the inner cone again and again as I flew by.
```

### [53] hash=`aa1e2e161c010bd0`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
Immersed in great joy, I dove down from the air.At that time, our hands held each other in the flames.Our traces went on, from one torch to another.Yes, I know, remember it now.I once drank the cold water in the springand covered my limbs with colorful stripsuntil a pair of wrinkled hands touched my forehead.Good girl, my good girl.Your hands are dusted, but you win the game and your soul is sparkling.
```

### [54] hash=`c14b1c0b99d48046`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
It's you who find the hottest fire for us.It's you who connect to it and make friends with it.I shall grant you the scepter and lead you to the highest platform.I shall become the next priestess of the Uluru temple.I shall take responsibility for every drop of sweat on the red soil, and I shall eulogizeall the significant fair competitions.I shall store the flame in my mouth, my stomach, my heart, and my ribs.
```

### [55] hash=`d8ba47a80cb34e83`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
I shall protect her, not to let her extinguish, nor to let her go astray or away.I hereby swear, I shall be, with the Uluru Games, until, forever, enters to the stadium!Now I must be, fanned up!I can beat them just rolling around!Goodness, you found me!These critters!They don't look like any kind that I know of!What are they?These critters are the guardians of the stadium!They are...I can explain it later!
```

### [56] hash=`52bc9bc51fa15224`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
We have to deal with them first!No time to hesitate!Protect Spatha Deer and engage!Great!They are down!Everyone, for the sake of prudence, please stay back and do not approach before confirming the danger has been eliminated.No!There's no more danger now!Look!No need to worry or hesitate.Now, it's all clear.Long story short, mates, I've retrieved many memories.At least now I know who I used to be.
```

### [57] hash=`13c064a49199b421`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p6`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P6【涅槃日】）

```text
I was the first priest in the history of the Uluru Games.The flame that drew all the way from the ancient times inside me.I will become the next priestess in the history of the Uluru Games.What I said, Mace?My flame is so clumpy.So good kids never lie.So?
```

### [58] hash=`183fa2a7e7a43aad`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Where did she go?It was like a long slumber, or a view of the garden behind the wall.I finally get to see the sun again.The world out there has completely changed, but you remain the same, Flemmy.My dear friend, you found me and put an end to the long, dark dream.You set me on fire again, bringing me back to what a flame should be like.Welcome to the end of the 20th century, Ulu.For you, this is an interesting era, with many, many new things.
```

### [59] hash=`75ae2b0b4b9e7440`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Well, I think we can learn them together, later, one by one.Well, from my dear, brave friend, to the Uluru, my dear, brave friend, waiting for...The chondrine of the entrance to the Uluru Stadium is sourced from a fantastic arcane ritual.Instead of a summon, it's closer to a sacrifice.The fire element also plays an important part in the sacrifice.In Spathadia's case, Ulu is her flame.Will it have anything to do with the unique condition Miss Spathadia has?
```

### [60] hash=`67d131d6728de1c6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Unlike other reincarnators, she still has a clear memory of this life, despite heryoung age.Or, it's because the two light spots of hers, the older self and the modern self,are not that different, so she's spared going through any drastic changes.And the reason behind it might be…Yes, I'm here.What can I do for you miss about the deer waiting for you?I seeSorry, I was too involved in taking notesI will pack in return to Laplace as soon as possible
```

### [61] hash=`86b832fe305563fb`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
But before that I have to clean up the spores and the mess we made in the battle firstOtherwise, they may change the environment here.Come on you weirdo.You're leaving nowAfter all our effort I can never understand you aren't you waiting for me to leaveIt's not.I'm waiting for you to join us.We'll go into the stadium together.I...come to think about what I've suffered.Coma, hallucination, confusion, burst, misconception that I was almighty.
```

### [62] hash=`305d870eebdca27e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
And then as you can see, I fell into a coma again after my sudden disappearance.I think you're right.I do need a doctor by my side.But mankind cannot enter the stadium.We all know tha-Physically, I don't feel anything special.Maybe because you're human.Wait!Not so fast!Be careful!Miss, you will fall!I won't!This is exactly what her canes should feel.Zulu!Pardon me.May I call you that?Go ahead if you want, child.
```

### [63] hash=`6b09a01e236c86e4`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
But of course, I would appreciate it if you called me madam.Since I'm a few hundred years older than all of you.Besides, I am the most sacred flame of the games.And those benches!Things change, Flammie.Past hundreds of years, when you were absent, countless changes happened to the Uluru Games.Lawns and benches had somehow appeared in the stadium, but none of these changes were made by Arcanists.Those actually made by Arcanus for new events, new rules, and new management.
```

### [64] hash=`cfebb753914c94f7`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
These are the changes that really made the Uluru games different.Never seen ice racewalking in my memories, so there was no stone bearing divinationor a new tridecaphon either.Ice racewalking is not a traditional sport in Australia.It originated in Northern Europe and became popular in cold countries.That's right.Racewalking was introduced to the games in 1926.If my memory serves me well, it was introduced by the Saint Pavlov Foundation.
```

### [65] hash=`8a85ad669cbafd26`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
On one hand, they hope to show the internationality and inclusiveness of the game.On the other...It took the place of fire racewalking.I see.I read it somewhere before.At the beginning of the 20th century, after Saint Pavlov Foundation to go over the Olu RooGames, some challenging and relatively dangerous sports were cancelled.This was also the turning point of the Olu Roo Games.From then on, the games declined in popularity, and fewer and fewer athletes came each year.
```

### [66] hash=`4013ea0d1bdeabce`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
People.No, these idiots!They know nothing about the essence of the alcanist sporting event.On Earth, can you find an alcanist who would burn their own legs in fire racewalking?Everyone knows you'll be fine as long as you believe the fire's harmless.But, in point of fact, fire is dangerous.Think about it.It's unbelievable.Given your short fuse, I can't believe you just let them cancel your favorite event and lo-
```

### [67] hash=`4bbc9c21c9d1d3bc`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Short fuse?Yeah, you heard it right.She's got the hottest temper, burns like a self.Change for me, I have already spent over a thousand years in this world.I am no longer the young, hot-headed flame of your age.Grandmother should call me Grandma now.Grandma?So they can just take away your favorite event just because you're old now?Anyway, Flammy is back.It's time Arcanists took back the Uluru games from the Foundation.
```

### [68] hash=`65a853980d11abd2`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Let's design a new list of events that fit real Arcanists.We'll start from Fire Racewalking.There are woods here.Ula can start some bonfires with them.Will the Foundation agree to this?They seem difficult to deal with.It's hard to take it over from the Foundation.But if we have all the security-related facilities prepared,and apply to host the event through Laplace Scientific Computing Center...Considering Spathedia's identity, we do stand a chance.
```

### [69] hash=`8fe3176ebe31a00a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
But the paperwork we're going to deal with...You're not supposed to talk about paperwork in the sacred Uluru Stadium!Instead of a bunch of weak office workers who would pant from climbing a few stairs,what I need is some real athletes who can help me complete the fire race walking.I don't mind whether they're cute or weird, I only need them to be energetic.This is the only thing we ask of athletes in this sport.
```

### [70] hash=`68ca9fa5a03a9786`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Great idea, but the only inconvenience is that we are in the middle of the desert,a place where only flies visit.and as I checked my contact list I saw only client, client and client.The ordinaryones and the ones I once stood up.Where are we going to find athletes?Well Ihappen to know many Arcanists who meet your need and they happen to be hereright now.What?Come on Kat see them anywhere.Why are you opening the suitcase?
```

### [71] hash=`4003a8f0626dc750`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
Are you going to organize your stuff here?Anyone care to have some fresh air?Mmm, the fresh smell of grass with smoked fragrance.There is no doubt that it tastes better than gilded carrots.And look at this army of royal guards.They must be here to greet the great Dali Clatterth.Royal guard?What is he saying?Ah, no kidding.Is that giant creature covered with spikes his royal guard?Thorny devils.The enormous creatures born in the burning sand of the stadium.
```

### [72] hash=`c3edc50c6c6efe32`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p7`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P7【老火种】）

```text
They used to be mounts for the players, but it looks like they have forgotten their master after all these years of slumber.Enough talk.Let's put them back to dust and ashes.Be careful, young man.An apple a day keeps the doctor away.I dedicate this win to mists that those of you who are not afraid of fire and wish to walk among the flames, register here!
```

### [73] hash=`abaeead53d73e14e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p8`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P8【火警热线】）

```text
Oh, are you saying that a sports game can archetype people too?Hmm, I think Mr.Apple knows it better than me.Let me check where he is.Must be Mr.Apple.He seems rounder and bigger.And the victory goes to...Ms.Desert?Taupe.Her temperature is a bit lower than just now,but her condition is quite stable.I guess it's more to reincarnate a reaction, but something else.Is she alright?She feels hot, but not as hot as the horse you made of pure gold.
```

### [74] hash=`a66683f25b4449d7`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p8`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P8【火警热线】）

```text
I'm positive that she was once a lot hotter than your little hooves are right now.She was a walking fire that burned fiercely, the forest destroying kind.Please don't panic.I have not observed any signs of a flame in her eyes or mouth.She's not a blaze again.Miss Desertflannel, did she have any abnormalities before she passed out?Abnormalities?Some, I think.She waddled as if she was pierced and talked so loudly that anyone could tell she wasn't in a clear mind.
```

### [75] hash=`f79b03c0e1e92b32`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p8`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P8【火警热线】）

```text
Trunk.Clouding of consciousness.No, Regulus!You look like an apple-colored giant rock, Mr.Apple.You're so big, and our ship is so small.Seems your change of size changes your voice as wellBut since you get this huge we can strike thoseOphogies in London like a meteor onThere will be a flag of rock-a-rollThis is quite the big-Regulus!Your limit!Your sweat is the best eulogy for the Red Le-That's Miss Ulu!
```

### [76] hash=`0137ead2f9346c2f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p8`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P8【火警热线】）

```text
She's out of control!Is this also a result of the stadium's power?Oh, I'm so tired.Let me take a nap.Regulus?Oh dear.Don't pass on you out of here.Just a sec!Another one has passed out.If we let it go on like this, every Arcanist here would-Miss Verton?We have to leave at once!So do bunny bunny take everyone back to the suitcase.Don't let anyone out before I open it againAll right, got it.Huh?Have to put her out for now the good news is we are already a skilled fire brigade

Careful young man careful young man
```

### [77] hash=`8ca78cc6b9f9cac6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
Desert Flannel's dizziness is in remission.She's already well enough to deal with her business on the fax machine.Will it do harm to her physical condition?Ms.Desert Flannel is only experiencing a very mild reaction.She can move around freely and it is recommended for her to do so.Ms.Spathedia, on the contrary...She's not even awake.No.But her body temperature and her Arcanum level are getting stable now.
```

### [78] hash=`ac813f3b8e273853`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
She should wake up any minute.Miss Ulu is different to the other unconscious Arcanists.She was weakened by the long sleep, while the other Arcanists lost consciousness becauseof external factors.Look, this is their physiological data in the last three hours.Many Arcanists have told us that their physical abilities were improved as theyentered the stadium.They felt they were in a refreshed state, like they had a good sleep or rested properly.
```

### [79] hash=`92a80146a2cf9b61`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
But after they competed in four to six different games, or the average sportingtime exceeded 3.5 hours, they would feel dizzy, as if they had consumed too much alcohol.And these symptoms were relieved, soon after they left the stadium.You mean, people are in oblivion because of that...stadium?That place is so dangerous, is it possible to hold the games again?I think this is why in the past, athletes were only allowed to compete in three different
```

### [80] hash=`f559006453d39237`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
sports.As long as we stick with the same rule, the safety of our athletes shouldn't be problematic.I got it!So this place is just as safe as the club I work in!As long as we ain't breaking the rules, nothing will happen!Like how the bodyguards and I take care of our club,the rule and special medicine made by Ms.Ezra will protect the Uluru Stadium!Miss?Oh?What's wrong, Ms.Ezra?Miss Bunny, but you see, I'm not a miss.
```

### [81] hash=`a5a2e9b5d56fbbfc`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
Huh?You are funny, Miss Ezra.Please stop teasing me.What else can you be except a lady?A gentleman?Ezra is indeed a he.Fathodea, you're awake.Here, take this water and the nutrition supplement capsule.To a boy?And Missy Ezra here is holding her for it and looks......overwhelmed?Uh, he is not a Missy.He's a buddy!A buddy, Ezra?So what?Boy or girl, is that such a big deal?Nothing is more important than this.
```

### [82] hash=`c049c8ff5ddb71e6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
Dear Miss Verdin, I am glad to hear from you.No, no, not that one.That's for Vertin.From some guy called Slouch Hat.Oh, thank you.He's my contact in Australia.We've been writing letters these days.So, what am I supposed to look at then?This one?Large scale event application form.Alice Springs Government.We just need to go to the city hall, fill in the form, and submit it!Then we're ready to have our Uluru game!
```

### [83] hash=`4e9ed4f982fc47ed`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
Before then, let's hit the-No, Ms.Spathedia!You haven't fully recovered, you need to rest!I'm not feeling that bad.Actually, I'm feeling really good.That's right!Really good!The pool's not like a no man's land.We're just going there to fill in some forms.They've all hurt me.Okay?No!This time is different.This is not like what happened before, Ms.Spathedia.I'm your doctor,and I'm responsible for your health.
```

### [84] hash=`355baf8758d134b0`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
I can't let you leave my side.Your side?Your side.Come on!Our summer games are about to start!Bath O'Dea is surely a good runner.Even faster than the potion-drunk Ms.Sotheby.Okay, since the doctor and the patient are both happy, I, the event assistant producer, am also hitting the road.Wait for our good news!What are these?Look, I know English, but I don't understand any of the things written here.
```

### [85] hash=`c58f7f0c00f0bd8a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
What is Northern Territory Event Security Law?Oh, and what is type 3 field safety certification?Ugh, I think I'll just go with C here for event types.That's what looks closest to the Uluru game since they have both two-word phrases.Maybe let's just go with that one.I always go with C when I have no idea what I'm reading.Mass event application, fire escape plan...City Government Service Centre, District B, Window 13 at your service.
```

### [86] hash=`280c27c3d800c83c`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
Thanks for your waiting.Your form will be examined...Oh great, she stopped.What happened?I've seen that look on Miss Judy's face.She's my maths teacher.Whenever she puts on that face...Yes?It means none of your answers are correct.Uh huh...I told you we can't feel who knows in the form.Who knows you can't write that?this one yes miss desert I'm sorry and you arebut the dear the event little what does it flannel up to you sick the form instead
```

### [87] hash=`97e541ba8dfb145a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
I will prepare a stool for you please stop jumping now to jump up again andagain here's the form we revised check it all right you've submitted theArcanus Gathering Registration Form, the Mass Events Application Form, and the Desert AreasGathering Application Form.Your application will be in the approval process very soon.I'd go crazy if I had to fill them in again!I've never experienced such pain!
```

### [88] hash=`3d3aa4250ac29a5a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
We cried on each other's shoulders several times!Same for me.I'm sorry?It's nothing.But please, take a look here at the second half of the sports game process and events application form.Most of the events of your application have been confirmed, not approved.If you want to add them to the Illuru Games, an independent application for each event's security permissions is required.How can I get the permission then?
```

### [89] hash=`2b8b23aa7f9acb83`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
You need to fill in these forms and take live photos for the events you want to apply for.You are smart and your ideas are fun.I've been paying attention to you when I was still a small flame.Looks like you have a lot of expectations for the Uluru games.Sometimes it feels like you care about the games even more than Flammie does.I do have hopes for it.My wish to revive the games is stronger than Ezra's, and my expectations for it are higher than Spathadia's.
```

### [90] hash=`855efaa577502217`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
After all, we're in a different age now, which means we can achieve much more thana sports game.But to be honest, I'm impressed by Ms.Balthadir's energy and passion for all these.She's...huh?Who are those people by her side?From here?Here!We need entrance here!I also need a kiosk, and a fridge with drinks!Okay, our engineer will bring you the suitable sample materials before tomorrow 5pm.These things just won't let us go, like some cockroaches attracted to an open jar of jam.
```

### [91] hash=`3c2adebe38dfadb9`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p9`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P9【万事救星】）

```text
Scraps of paper sticking to the corner of their mouths.Is that...the newspaper?Mayhem.Revival squad of Allure games in City Hall with Bunny Girl?Mental breakdown of receptionist exclusive on Australian knacker?Children?What have you done out there?Look at my back!
```

