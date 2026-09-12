# 剧情图谱抽取 · batch 080

- 角色：`wu_ming_zhe`
- 批次：**80** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.5」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_080.jsonl`

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

### [0] hash=`70168d6663a0ac2c`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
get out and find more!Some big and breaking newslike that revival squad of Aluru Gamesin City Hall with Buddy Girl!It's you.Good timing.The Aluru Gameson the edge of total disruption.The revival squadturn against each other.I knew it.A group of monkeys.This is fun.The chief editor and that chickboth enjoy this.
```

### [1] hash=`ae41ddd12f9dae16`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
That's how you get muddy shoes when you're out hereHere take my handMiss desert flannelWhat is this place?What are we doing here?Something that needs to be done and something that needs to be said big bloke.Don't waitthis isThe warm-up of the rugby game.It's not a formal game, but the audience's enthusiasm is burningI mean, it's hard to get a ticket, but I'm desert final and I know people on the streets
```

### [2] hash=`cb049ada494b775e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
Even when we're outside Melbourne.Sorry, I've never watched any games, and I don't know the rules of rugby.I...I don't think I will understand any of this.Do you mind?No, I'm cool with that.Because the game is not what we're after.You see that guy over there?That's Tom, a shining new star in the NRL.The best fullback they've ever had.He's from the Melbourne Sail Car Club.They have a seagull as their club's mascot with a fish and a chip in its mouth.
```

### [3] hash=`510136de8bc7e0ff`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
Yes, okay.And that bloke over there, that's Kip Carl of the Hobart Blue Lake.He's the kind of player who knows how to really tackle.They call him the Unbreakable King.And lastly, I want you to look at that smaller guy.That's Russell.Doesn't look tough, does he?But he is the slippery jaboa because man he is fast when he gets the ballBut what is this to do with us?I still don't understandEzraGuess how many of them are arcaneists?
```

### [4] hash=`7bc53ca2aa49bdb4`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
Nice one.Nice oneRussell laid it againExcellent interceptionThe key score now the jaboa is slippery as butter run run for russellVictory is yoursMankind is known for their physical resilience and endurance.That is to say,Pormin Kipkala humans,or Russell,whose skills and unpredictability are his strengths,is an Arcanist.Hmm...A reasonable deduction.Physical resilience and varied skills are indeed the respective features of mankind and Arcanists.
```

### [5] hash=`4a19f22e46d95a83`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
However, things are not as simple as they appear.In fact, all of them are arcanists.Shit, give me that thing.Here, be careful.Don't overdose.Painkillers are addictive, you know.And the newspaper's gonna interview you, champions, so don't get high in front ofthe camera.Hey, listen.Sporting is great fun but it can also be dangerous especially for sports likerugby, MMA or boxing which involve a lot of intense physical contact and the
```

### [6] hash=`1f6d3a0d68e7a4ae`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
arcaneists who are good at healing will naturally become the best athletes ofall.15 minutes that's all they take.Most of the arcane treatments takeonly 15 minutes to heal the patient and before that happens the athletescould just take painkillers to help themselvesget through the game.And after the 15 minutes, they are refreshed and healthy,like those athlete dolls you find in the souvenir store.They can slide, impact like a maniac,
```

### [7] hash=`24dc391882073235`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
and don't have to worry about missingany important sporting sessions if injured.This is an advantage?That's right, an unbelievable advantage.But, are they really as good as they look?Their glory comes with a price.Ligament damage and the irreversible tears keep recurring.But there is still an elephant in the room.It paces around, making noises which are unfit for the place.Like this conversation we're having in the locker room.
```

### [8] hash=`913574fd2db0a12a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
But on the sports field, where blood boils,power and strength are the only things that matter.Nobody has the time to stop and ask what we're doing here,Just like they don't have the time to notice the elephant.Ten years ago, Margaret of Broken Hill was invincible on the court.In August last year, she died on the last day of winter.Did she die of recurrent injuries?It's very likely that arcaneist athletes who repeatedly get injured and heal themselves
```

### [9] hash=`e53bb86f21f17dea`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
would get hurt on the same body part in the future.The body will become fragile.They might even twist their ankle from walking, sometimes even break a bone or two.No, she died from an overdose.She needed a horrific amount of painkillers to ease her pain, so much that her bodywas overwhelmed.This, this is cruel.We have to report this to the Foundation and solve it once and for all.The athletes could have played in a safer way if given help.
```

### [10] hash=`ca8e179b5a37d9d5`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
But what if I tell you the Arcanists also don't have a choice?For humans who have the talent for sports, they can win medals with their physical strength.So, Arcanists have to make the most of their advantages to keep oppressed with theircompetitors?I had no idea.I'm sorry.Truly, I didn't mean to make you feel guilty, nor did I deliberately put you inpain.But Ezra, I was once one of them.I used to live on the prize money.
```

### [11] hash=`509c9913c150f447`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
I'm only telling the truth.It is happening every day, every moment and every second.Drug addiction, premature senility and irreversible physical damage.This is almost a destined end for every Arcanist athlete.And nobody is held accountable for this.Not the clubs, or the hosts of the games.Drug abuse is a personal behaviour.That's it.Those people who are passionate about sports and don't want to lead a life without them.
```

### [12] hash=`ae133107b705010f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
I have no idea how they would make a living or handle a quiet life.So I know they don't have much of a choice.The sport industry of humans is generous.They offer equal chances to human and arcanist athletes.But it's also cruel.And the athletes are like the girls in Cinderella's story, who wish their feet would fit the glass slippers.They have no choice but to cut off part of their heels to earn the glory.
```

### [13] hash=`0d2ce47cdfc3e1b9`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
This...this isn't fair.These sports and rules are not appropriate for Arcanists.They...they have been treated unjustly.They aren't taken seriously and respected as athletes.Is Spathedia one of them?That's why she was so furious.So the rumor that they are turning against each other is true.Kamara, this way.This is the human representative of the event.You are that paparazzi?This is not how a polite kid would address others, Mr.
```

### [14] hash=`0194f8d7d287a5d6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p11`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P11【玻璃鞋】）

```text
Ezra.I am just a concerned journalist who ran into you while reporting a rugby game.Watch your mouth, mister.This is harassment.Be a cornered.Then we will break his camera and let him know the price of being a long-tongued liar.
```

### [15] hash=`9f6e3b3bfb5f3899`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Spathedia, it's not all your fault.No, you don't have to be nice.I'm not capable of the job.I should have known when I couldn't even fill in some forms correctly.I don't know how to supervise the construction team.They all left and my schedule's in a mess now.I'm hasty and careless.I actually lost my temper with the people who tried to help me.I also did that to Ezra.I know he has no ill intention, and he's not a bad guy.
```

### [16] hash=`acd2c8c8183cbea4`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Maybe some humans mistreated us, but that has nothing to do with him or the others.I should've got out of his face right away.I screwed up the Uluru games.What I did was not out of friendship or sportsmanship at all.I'm just a nuisance.I'm not qualified for the priestess.Listen.Come here and listen to me.Everyone makes mistakes.That's what your mom told you when I was still asleep, remember?everyone makes mistakes especially young people we were of the same age in the
```

### [17] hash=`2eca0c3c086985ac`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
past it feels awkward to talk like an elder to you but now I have to addressyou as child you are 14 now remember what I was like at your age I appearedout of the campfire so young and naive my flame was beautiful yet lethal asThe point is, you must know your mistake and apologize to the friends you've hurt.You still have room for improvement and the opportunity to avoid the lasting regret.Regret?What's worse than what I'm dealing with?
```

### [18] hash=`919d3d56c30c956f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
I can't think of anything.Ooh, it's rude.Maybe Flammie is a better choice for you than Spathedia.My name has changed, and I can no longer be your best partner.Neither can I be Verdant's good partner, nor Ezra's, nor Desert Flannels.This is my second life, but I still feel like an idiot.What was I like in the previous life?Did I grow up?Did I hurt my friend?Did I have fights with you?Remember our fight, Flammy?
```

### [19] hash=`a183dc4918f032ee`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Yes.We were arguing who contributed the most to the first games.What a trifle.That's right.We had a huge fight over this trifle.We never meant to win the fight.All we wanted was recognition and love.But in the end, we didn't talk anymore.This lasted for several days.Then I tried to find you to make it up.Make it up.I- I don't remember that at allBecause I didn't make itYou were in the distance when I found you
```

### [20] hash=`d99b3e7de14ef384`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
The next second you were attacked by a toxic red snake ambushing from the bushIts venom made you pass out within secondsThe witch doctor stayed by your bed for three days before they sent you to the graveDidn't even have the chance to apologizeYou never grew up, my friend.I'm already an old flame after such a long time,while you are still a teenage girl.So, I'm really happy to see you again,and really sorry that we once grew apart.
```

### [21] hash=`4578d87801465e1a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Thank you for telling me, Ulu.My heart, dear friend, we once burned together as a whole.No one knows my heartbeat better than you do.I will grow up as you wish.I will find Ezra and make it up to him.Invinient!Here we are!Desert Funnel?Ezra?What's the hurry?That was...hell, those guys were chasing us like crazy.Anyway, that's why we are out of breath.A paparazzi was following us and as we were running in the desert we ran into a bunch of thorny devils.
```

### [22] hash=`b3fc2609a4995ede`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
I see.We'll deal with this problem before we talk.Give me 5 minutes.They will no longer be a problem for us.No, you drive them away.Two weeks ago, you were in the column whose heart is hurt by fire kangaroos and housing stress.Would you care to make a statement?Just an accident, not a misconduct.Fire goes out of control very easily, as it's fire after all.Young people.These days, the reopening of the Uluru games has attracted much focus, and speculations have reached such a pitch that we have to respond.
```

### [23] hash=`089aad6dce0bdedd`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Here I will answer your questions about the Uluru games, starting from you, the ardent Mr.Makoa.Of course, it's my pleasure.Made my day.I feel happy, contented, overjoyed.Now that we have the Foundation's people on our side, he can bugger off for good!You know him well.He's our enemy, Verdant.He's your enemy?We are not enemies!I don't even know him!You don't even know him?And he's not your enemy.I don't quite get your relationship.
```

### [24] hash=`7a0e04799646f249`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Things can be complicated between men and women nowadays.Too young to understand it.Don't worry.You will get it at my age.So it's a kind of experience one must grow old enough to learn.The current life expectancy is 50 to 75 years.I don't think I will ever reach your age.Put it like that!You're confusing the kids!I, as one of the parties involved in this story, will explain it to you very clearly.
```

### [25] hash=`47870df733ade7de`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p12`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P12【千年独行】）

```text
Cezra!He's not here!He just went back to his room!He didn't come out when we left!Anecdote!I won't tell the story again!It's way too embarrassing to tell twice!Listen to your story first, and then I'll go talk to him right away.
```

### [26] hash=`a1f4a613de2aa8be`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
the entrance, support structure for the ceiling, camera parrot for broadcasting the games,fluffy so, bear torch for the Uluru flame, obstacles for staple chase, tenacity of thebranches and temperature of the red cloth.Alright, check what item to get before theflame lighting ceremony this midnight.Piers, did I make you sad again?Nothing, I just have sand in my eyes.That is common here, it gets into your eyes very
```

### [27] hash=`35ac88042657077e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
We did make up, that's for sure, but we never really talked about the fight.It's like you break your knee and just cover the wound up with trousers, as if it had never been there.You may feel fine when you jump and run, but it hurts whenever you sit down for a break.I wonder if Ezra and Verdun are going well with the patrol.Relax, Flammie.It will be the opening ceremony tomorrow.Our checklist is even more intricately designed than a road made with pine needles.
```

### [28] hash=`13a450e2960436fd`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
Besides, the bunyips haven't turned up in quite a while.Everything is working like an unsinkable ship at sea.There isn't anything that may cause it to sink.But the last ship that claimed to be unsinkable...What was it called?Got it!Emergency!Tannic!I've bought tickets, let me in!I came all the way here just for the Uluru Games because you said that it is open to all for the first time.Everyone, please be patient.
```

### [29] hash=`511fa8d9ce8fe731`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
We are now standing at the entrance to the Uluru Stadium.And this is where the rumored reincarnation will come with flames and bring about the rain.The rain will comfort the thirsty travelers and soothe their dry heels.I guarantee you, as the ambassador of the games, that no matter what your lineage is,you are welcome here as long as you have a ticket.All you need to do is wait patiently and with sincerity.
```

### [30] hash=`19ac439f008d5837`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
Sincerity?We followed the guide and circled around the desert for a whole day.We need water and food.Some kids have become dehydrated.yes we need water we need to get into the Uluru Stadium you've promised us weneed water we need to get into the Uluru Stadium we need water we need to get inthe Uluru Stadium that's right yes that's rightrevival squad I'm sure you will enjoy this gift from me we need water we
```

### [31] hash=`ca867c846630a2fa`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
We need to get to the Allura Stadium, we need water, we need to get to the Allura Stadium!It's him, that guy.Shameless.We never sold a single ticket or invited so many outsiders to the game.How can they tell such a lie?He's whipping up public opinion.Just his greatest strength.I took a glance at the crowd.There were at least 3,500 of them out there.Not a number of Makawa can incite alone.Some of them must be his accomplices.
```

### [32] hash=`a41e8aa83bd3cf40`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
I'm sure they are good at mobilizing, swindling, blackmailing and stuff.It's the Eucalyptus Brotherhood!The leader is one of them!I know his face!Darn it!Seems like they're not going to make this easy for me since I took their tickets.And there's Makawa!How convenient for them!We can't just leave them here.Outside the stadium they have no food or shelter.Ezra, Verdun, please contact the Foundation for help.
```

### [33] hash=`068120f209bb75e6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
Desert Flannel, I need you to prepare to guide the crowd and maintain order.But the dear, you're not planning to...Let's go all out, mates.I am going.Your attention!That is the daughter of Uluru Stadium!Behind her!She's the girl in the newspaper!What?That girl?Is the reincarnator?Oh dear, there she is!And look at that flame!Isn't that the Uluru flame in the newspaper?Open the gate for us, priestess!
```

### [34] hash=`25f5acaea7ff3904`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
Show us the Uluru Stadium!Open the gate for us!We have tickets!Open the gate for us!We have tickets!Look at those girls, my friends.That is Miss Lithodia and Miss Uluru.The newspapers have been praising them for facilitating the union of mankind and theArkanists, bringing back the true spirit of sporting events and calling them the pioneerpeacemakers.You're a liar!Of course, of course!You are not lying, you never lie.
```

### [35] hash=`045fa5e4212cb7a1`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
No lies have been spoken, every word was true.A junior student from Melbourne, an old soul, a reincarnator, what's her attitudeAm you how could you be so despicable all the constructions are built by Laplace.These are all human contributionsI'm out of here.It's not the Uluru games.Not the one I heard from my grandma at allWe should believe that she's an honest girl.She would never have liedMiss Spathedia, did you really say that?
```

### [36] hash=`d8a9372f172ba481`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
front it light it upConquer it and make it burn.I willI know what my duty is.Sisters of the Uluru Games, and my friend, the Uluru Flame, both of us stand right here.We will not tell a lie or evade any questions.That's right, we stand right here.It's time we put an end to all these slanders, Mr.Makawa.There are reports of your arson.You set fire to a hospital and thousands of human patients in there were almost killed.
```

### [37] hash=`569609ab67f43f24`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
This is supposed to be an unforgivable felony, yet you are still standing here.Did you bribe the officers to get away, Miss Spapadia?Please be careful of your wording, Mr.Makua.That was not arson.It was an accident caused by the instability of my arcane skill.It was awakening at the time, and things like this happen to most arcanists.Second, we didn't cause any injuries or burn the hospital.Only a clinic was slightly burnt in the accident.
```

### [38] hash=`3ba01fcd39dffd7f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
We have paid for the damage already.Besides, the revival squad has promised they will do volunteer work for the hospital every Saturday afternoon as an apology.Good for you.The bunyip is weakened.Now go for it, Fanny.Everyone here is exhausted from the journey to the desert.We're suffering from the heat and the thirst.So why don't you open this gate for us?Is your Golden Gate too good for the tickets we paid for?
```

### [39] hash=`35882a4627af8996`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
Are you shutting us out?You paid for?Are you sure that Uluru Games has ever sold any tickets?Guys, please check your tickets and compare them to each others.I believe they have different sizes, textures and printing methods, which indicate they come from different producers.That's right.If you know the local gangs well,Now you should realize the staff who brought you here and those marshalling the crowds include some familiar faces
```

### [40] hash=`1e94d2b56d046a7d`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
They are Tommy, Jackson and CameronGangsters from the Eucalyptus Brotherhood who made their first pot of gold by selling fake tickets andYou Mr.Makkawa speak for themNo wayWell, yeah, you've got a silver tongue.Your words are indeed clearlogical and reasonable.But how are you going to deny what you said in the photos?You wanted no humans in the stadium and you held a grudge and a prejudice against them.
```

### [41] hash=`e71cb56f6a66cf05`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
There is no doubt that those words came out of your mouth.Your eloquence won't change the fact.Yes, the fact.The fact that is 100% true.You can't deny it.You are right, Mr.Makora.I did say that.I take responsibility for every word heard indoctors, and my first human friend, my good friend.I saw humans as the other kind.I thought they were unreasonable, cruel peoplewho deceive others with bureaucratic jargon.
```

### [42] hash=`53f2201a2ca3d741`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
But now, when I think of humans,I am reminded of my friend, my gentle, brave, smart,selfless, clumsy human friend.Are you going to...Confront it.Light it up.Conquer it.And make it burn for you.Everyone here loves sports as much as I do.I must apologize for being an idiotwith such a narrow view.I'm sorry.I hope everyone can enjoy pure sportsand have you who have tickets.Those of you with no tickets,
```

### [43] hash=`f239158164fcb455`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p13`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P13【永不沉没】）

```text
you can buy one from this desertflannel for just one dollar.I hereby declare opening of the Euler-Damn it!The source has confirmed the rift between them!Run!If I'm fast enough, there's still a chance!Or maybe you don't deserve that chance at all.We've got a helping hand.More than one hand.This is what we call the hammer of justice.Take that, you shitty little long-tongued pig!I will pull your tongue out through one of your eye sockets!

You should have known better than to mess with me!
```

### [44] hash=`2830e15e89657eac`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p14`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P14【跑者史诗】）

```text
The audience are all seated.No stampede or jostle, not to mention injury.All the human athletes have registered and their mixed sporting events with theArcanist athletes have been properly planned and are ready to start in three days.I'm done.I can't even move a finger right now.Come on, Flammy.It's our turn.We walk on this glorious path together, Uwe.Run.Get yourself a running child.This is just the way you've waited a million days and nights for it.
```

### [45] hash=`94a0d1688517b814`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p14`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P14【跑者史诗】）

```text
I want you to be proud.I want you to be happyMy friend my dear friend.You are already my FlammieBut you are actually nothing that you are also my spathetiamy little girlYou have grown up as I am dreamt of countless timesThe snakes who didn't lay a single tooth on you.Both your body and mind are intact.Hey, what's that?The flame is dropping water!The event is important to you, and so to us now.This is who are here with us to join the event through radio, TV or internet.
```

### [46] hash=`12095bad39f06dd5`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p14`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P14【跑者史诗】）

```text
To witness the blazing of the Uluru torch.Spirit of peace petition.In the past thousand years, Holy Fire has been to the highest mountainand touched the rocks in the deepest sea.In the peace and all of the noble qualitiesto every corner of this world.It was also brought out of this world into spaceby rockets and traveled among the stars.From ships to spaceships, from one hand to another.It has journeyed far.
```

### [47] hash=`3700a41caedae664`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p14`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P14【跑者史诗】）

```text
It has come to the plane.Patriots, we shall write in the name of Fordmanship.We shall walk in the original form of man.We shall compete against each other, not for victory, but for participation!
```

### [48] hash=`72f8d10a49e76ecf`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
So, did Ms.Desertflannel go to the hospital to visit Mr.Makawa?Yeah, she bought all the magazines with that photo and brought them to...Oh, wait.I guess you don't know the story between Desertflannel and Makawa.No idea.I was in my room, pondering what happened that day.Don't look at me like that!I've told you I'll never repeat that story again!Okay.I guess it doesn't matter if I never had the chance of hearing it.
```

### [49] hash=`42ee61a6e2abc6e6`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
It's just a story.Oh, I will tell it to you.Come over here kid.You were so kindYou must all know that I have many jobsThese part-time jobs eat away most of my timeBut the clients who gave me these jobs never let me go home empty-handedIf you were me, you'd know that if you are willing enough to take as many jobs as possible, you'd meet some strange clientslike going to a school day pretending to be someone's mom or
```

### [50] hash=`a2f6fc150c28a883`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
for example, braiding the hair of a punk hound in 302 pigtails for a blind man, or waitingfor a rare bird at midnight carrying a camera which was expensive enough to pay for my apartment.I know, sometimes my colleagues in the class would also hire others to help collect informationthey need, but if we have the time, most of us would prefer to take a walk in theforest and try our luck.Yes, that's exactly what my client said.
```

### [51] hash=`74221c336a9ad218`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
He paid me well for the job, so generous that I stared at the dark and waited forthat pink torch hummingbird to show up despite my bloodshot eyes.One day, twodays, and three days passed.I didn't even see anything like it, but I saw awonder beast just as extraordinary as the hummingbird.Glittering platypus,It's pink, and it's glittering, and who knows whether Pink Torch Hummingbird is a strangenickname for that platypus.
```

### [52] hash=`13b4423bb11f1d40`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
Of course I have to take a picture of it.But you know, a bird lover won't need a picture of a platypus.So I sold it to Kidding Fun, a children's magazine.What happened next should be very evident to you, if you read enough bad novels.Is...is that...?Yes, that's right.That platypus was Makua who took the transformation potion.Ah, why would he do that?Perhaps he was looking for some fun or maybe it was an accident?
```

### [53] hash=`e38d6b76a9369278`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
Anyway, according to him, someone pulled out a prank on him and it was definitely not his own choosing.He quit his job the moment that picture was published.He left his friends and family and became a revenger, striving to put me into a miserablesituation just like what he has gone through.So this time, after I made this fortune, I bought the apartment and every copy of thatissue of the magazine.Were you planning to sell them all to Mr.
```

### [54] hash=`18f900df91fa8320`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
McAware?No.Of course not.Who do you think I am?I picked him up at the hospital, took him somewhere quiet and burnt all the magazinesin front of him.He was, oh my gosh, crying so loud.That was pleasant to hear.Now, Miss Babadeer and Mr.Ezra, the interview is ready to start.Please follow me to the stage.Ah yes, in a minute.Did you get the ending of the story?No, not really.Something neither arcanists nor humans can understand.
```

### [55] hash=`5a7cf69c536e9179`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
Perhaps we can ask Vertin later.She's a bit older than us, but she's not here today.I think she went to the stadium with Ms.Ulu.Old swallowing crowd, the apocalyptic hedonism, and the adventure on the island of numbers.So this is what the world has become when I was in slumber for all these years.I have experienced countless rains, and have even seen the rainbow above Uluru, butI've never seen anything like the storm.
```

### [56] hash=`9d1fd55c50927d6e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
I can't believe it just changed everything so easily.But the Alluru Stadium is still here.I know there are spots with mysterious power in this world.They can provide a slim chance of survival in the storm.And the stadium is exactly one of them.Such a place will be desired by different forces one day.It's just a matter of time.Like the menace vindicti you talked about.To them, the Illiru Stadium is like a piece of meat to a hungry wolf.
```

### [57] hash=`07cf88960597d313`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
That's right.The Foundation has already launched the Illiru Guarding Project.It will be a long-term mission and involves a heavy workload,and the Australia branch doesn't have enough manpower for it.Fortunately, a lot of people went to the visitor window of the branch.They are worried about the stadium?Yes, a lot.They volunteered to station here to protect it, even at the cost of their own time and effort.
```

### [58] hash=`edad6664a57e3c80`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
They have built the Uluru Guardians, which consist of 31 Arcanists and 29 Humans.They're reductors, writers, taxi drivers, new stand owners, and so on.And they are all among the audience of the games.You made it, child.This is indeed a brand new beginning.That's why I want to keep it here.We shall run in the name of sportsmanship.We shall walk in the original form of men.We shall compete against each other, not for victory but for participation, by both human
```

### [59] hash=`d3c7a86af13ce3ef`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p15`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P15【红岩护卫队】）

```text
and arcanist.No matter how many times the storm reshapes the world from top to bottom, no matterhow the times or the lifestyle change, no matter how ignorant people become.Wheneverthey open the gate to the Alluru Stadium again, they will remember the spirit and faithit has been conveying.Things will change in the unstoppable river of time, yet theAlluru Stadium shall remain forever.
```

### [60] hash=`ae0a743d9275941f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
It's one of the Arcanus lineages.A rare kind, Miss Bathodea.Based on the past cases, you will eventually become yourself again.The old self.What you saw in your mind were not illusions,but memories from your past self.Under the starry sky, rotting sand, countless Arcanus ran like a herd of beasts.I don't think any Arcanus would say no to witnessing the revival of the onceA junior student from Melbourne, an old soul reincarnated, what's her attitude and what will she do?
```

### [61] hash=`97a9ab76469fa04a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
Find out with me!Come on Flammie, let's light up the allure torch.You've reached desert flannel.I'm not home right now or I don't have time for calls.Please leave a message after the beep.It's before the game starts.Where are you?It's here now unless you're dead!Look, I know you're not into these games, but you can really use the money, right?Otherwise, you wouldn't have come to me.Pick me up again, we're both...
```

### [62] hash=`7945ebc4842acd6f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
Just leave it to Thursday.The game on Thursday is crucial.I will get expelled if I mess it up.I'm begging you.Tim, over, now!Thursday?Wait!We missed the right junction.The roads are different from the map Mr.Slouch Hat gave us.It's too outdated to provide any useful information.Terrific.We've gone wrong again.Again, this is like, yeah, the fourth time.Since my short life is supposed to be spentin creating huge value for all the living things
```

### [63] hash=`afd9e3f3ffe8982f`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
in this world, Foundation should have sent meanother bodyguard, a more reliable one,and the contact here should have offered usa more reliable map.I am the one and only reliable bodyguardwho can keep you safe among all the othersin the Foundation.You are of great significance to Laplace.They don't want you to...take any risks.We can go back to the last junction or keep going forward.There is a trail about 300 meters ahead, and it leads all the way to the Rolling Crock Bookstore.
```

### [64] hash=`134069ca4456e67a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
You want to check them out?When things don't work out one way, a researcher will find another.See?There comes another way.Hey, wait!Miss Spa...Spathadia, right?Till I know you?We arrived in Australia not long ago.We've been lost for way too long, so long that the human society has begun to suffereconomic losses because I've been loafing around.Now you are given an opportunity to help the whole of humanity, and it only takes
```

### [65] hash=`9a83ee2150c29500`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
a few minutes, well, maybe hours of your meaningless life.Take us to the rolling croc.The rolling croc?Exercise!Go straight ahead, turn right into the lane after passing by a cafe with an orangeReally break some part of myself?I said I passed out, but...It doesn't feel like that to me.My vest is dusty, but I don't feel any pain at all.Maybe I need more ice water.No...Maybe it's hot tea that I need.
```

### [66] hash=`a72a705d40bf2774`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
I should've gone to that lab lettuce place with those wacky people and had a physical examination.Let me see...Their card is in...Wait, no!I've turned them down!If I go back to them, that'll be super embarrassing.Besides, I bumped my head on the ground, but it's my stomach that's feeling sick now.I'm sure this is just a coincidence.I seldom have junk food and never miss the training at school.I know my body well.
```

### [67] hash=`de67a49a47d4e5e4`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
It's healthy and tough.I already took the medicine for stomach pain.Now, just take a break, and distract myself from it.The smell of soil, mineral, burning coal, and the golden pender, that already makes mefeel much better.What about my collection?Mom gave it to me for my fifth birthday.In 1884, Brantford was very popular amongst arcanists.The Uluru Games that year had more trees than that in any of the years.
```

### [68] hash=`fc571e49cb7cbf23`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
And then in 1900, St.Pavlov Foundation took over the Uluru Games.Out of security concerns, they abolished one third of the events that involved dangerousactions, and imposed a lot of regulations on the rest.Jones got first place in the game that year.The games in 1938, it was the most successful one ever since the Foundation took over.It was so successful, almost everyone thought the games would be revived and brought back
```

### [69] hash=`71e050f05d980ffc`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
the public, until I wish I could see the Ubiru Stadium with my own eyes again, even for justa minute.Like, like how I used to host opening ceremonies in there, sit on the highest platform, ignitinga flame from the wood saturated by ointment, and then, flew on a rosewood branch, followinga canoe in water and gently pushing it forward, but the flame had a fight withme.He trembled with anger because she was such an unreasonable blockhead.
```

### [70] hash=`3e3e0e104eac27d8`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p1`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P1）

```text
Then my sight was filled with darkness.My sight?Just say something?What are these things doing in my head?Are they illusions?When did I go to the desert?Since when did I-My stomach is much better now, but-My throat is burning!
```

### [71] hash=`d6871fd7228e0136`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
Let's summarize what happened.You fell into a coma for 16 minutes and 30 seconds yesterday due to external impactThen you woke up and found yourself fine.That's right on that nightYou felt an unusual burn coming up to your throat from your stomach at the same time.You had weird illusions andAt last you vomited a ball of fireYes, that's right.Exactlyfor one last timeAre you sure?No one in your family is related to the red dragon?
```

### [72] hash=`b2adfdbf74c34500`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
100% positive!I checked all the family photos and medical records,and even rang Mum and Dad!Do any of it!The symptom is really rare to see.So, don't walk away on me.Are you really buying that?I don't doubt it.Then you're a fucking donut.Would have lost all your clothes to any rauderthat comes up to you if you wandered long enough on the streets.And you!Mourning you!Take your little claws off me!Let me go, now!
```

### [73] hash=`f40a9964ce7c1228`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
Hey, you were the one who burst out of nowhere and knocked me over!Now my brain's not working right and you're responsible for it!Yeah?You mean this smidge of zombie fire?You reckon this is the first time an arcanist sees it?Can get you 20 of these in two days in any workshop.You gotta try harder if you wanna fool me.Oh, whoa!Fire!I saw that ball of fire come out of my mouth!You frauds never stop coming up with new scams.
```

### [74] hash=`67c67ababd3b8fa4`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
No cheat, no eat.Heard that before?Go home with your fake fire.If you continue doing this, be careful of the bunyips.They will crawl into your house through the sewage and take your tonguebecause lies are their favourite food.But there is no evidence to prove that she is telling a lie.Evidence?I have more than enough evidence to prove she's not some innocent lamb.She climbed up the tree outside my window and was shouting and screaming there in the middle of the night.
```

### [75] hash=`97d1caaeb729e205`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
The moment I went outside, she took me here like she was carrying a bag of groceries.One main fur that she was shocked by the fire-voluntary in the bus displayed abnormal behaviors.My god, don't you have adults at home to put some senses in your head?Haven't they taught you not to trust the strangers' words?Especially if they show up at late hours?The stranger?I know something's wrong with my head, and I'm not even sure who I really am anymore.
```

### [76] hash=`5aefcf7f196223aa`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
But you shouldn't have forgotten me.Neighbours, desert flannel.Our street's away.I even said hello to you.Three streets away?How does it make us neighbours?And I don't think our litter-covered street is part of your fancy community,where people sit by the white fountains and walk in the street gardens.The last time I checked, I was not from some rich immigrant family.No matter what you're looking for, for money or for fun, I couldn't care less about it.
```

### [77] hash=`fc23e432c7f3af8a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
The only thing I care about is that my landlord will kick me out if I fail to pay rent this month.So let me go!Don't leave!I think I just nicked you in the teeth.Eve!At least, not before I figure out what happened to me.Things are flashing in my mind now.Sometimes the past, sometimes the present.I remember I can sing, but soon I forget how to do that.Remember the crowd who worshipped me on their knees?
```

### [78] hash=`4a0ce002a0f75bc8`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p2`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P2【邻人友爱】）

```text
They're running somewhere like the Uluru Stadium!They're hot.A hot bonfire?Is that a bonfire?Anyway, no matter what it is,I'm just an ordinary person like anyone else living at the end of the century.This thing shouldn't be in my mind!Must be something wrong with me.With my head or other parts?I can't just go nuts now.My training plan?I have a game to play at the end of the year.The symptoms may not last.

Looks like they pay their employees well.
```

### [79] hash=`9bfd3096a18503ae`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Here is Ms.Spathadia's physical examination.How sweet.They even got you the Salvia Zopaclone Patches.If the illusions get too real and you can't sleep, use them.Okay.Thanks.But I need to ask my coach if I can use it.Don't worry.It's been approved by the Therapeutic Goods Administration of Campbell.The ingredients include Salvia, Mint, and a Hallucination Potion.They can neutralize a side effect perfectly.
```

### [80] hash=`7705396c36c8d443`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
All right, I think that's the last thing I'd like to hear from a doctorWould you just let go of my hand Sheila?Well the good doctor here will have to cut this hand off later because of necrosisCan I hold it for another five minutes, please?I'm sort of nervousThat's right.Breathe inBreathe out then unbend the fingersI'm also human.I feel pain too, sweetheart.I can't believe how lucky I am.We haven't seen a living case for decades.
```

### [81] hash=`cda9b36982579e36`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
This is exciting.Thank you for letting me know about this medicine pocket.Not at all, Ezra, my dear friend.See, I always keep you and your weird little mushrooms at the back of my mind.So, it'd be best if you could give them to me without leaving any records in Laplace's system next time.Anyway, we can talk about that later.Now, go check out the girl.She might be very useful for your paper on Arcanum.
```

### [82] hash=`0c966bcee79a7699`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Of course, I'll tend to her in a moment.I just want to tell you how much I appreciate your thoughtfulness.I've been waiting for this for too long.What?Miss Spathedia, I came for you.I've been briefed on your case and had a basic understanding of the inner flame temperature and the fuel through the laboratory report.Here's a list summarizing all the conditions.It's still a draft, but please take a look.
```

### [83] hash=`8da182fe34b7ac9e`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Since your condition has stabilized, and as a teenager, you're still in a developmentalstage, I'd recommend you to run a test which is more friendly and pleasant to yournose.Now, please blink three times at this dowsing rod, and blow on it as lightly as possible.Wha...What's this?No, not like that.Just be gentle with it.Lower your voice so that you don't blow away the spores on the filter.Okay.Blink three times, and blow.
```

### [84] hash=`37e7d7d759724318`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Then we're going to roll it up and fix it on the dowsing rod.Now time will do its magic.Doctor, is there a cure for my head?Wait, is that the smell of mushroom?It is related to mushrooms, and I'm not a doctor.Please forgive me, Ms.Spathadia.I was so overjoyed I forgot to introduce myself.Hello, I'm Ezra.I'm a human researcher at the Laplace Australia branch.My research is mostly on the diversity of local mushrooms and fungi.
```

### [85] hash=`473e99657bb0a338`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
I'm very thrilled to meet you.You're not a doctor?Just a researcher...and a human...and you're working on...mushrooms?That's right.It's a shame that I didn't become a member of the arcane study team,but I'm equally interested in mushrooms.I enjoy this job.Treat me?Which means I'm not a descendant of the dragon, but that of mushrooms?I'm a fire-breathing mushroom girl?No.I'm not here to diagnose your abnormality, Ms.
```

### [86] hash=`8e8a48037abb3d88`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Spathedia.You're perfectly healthy.Your brain CT result looks normal, and I can see you're in good shape.In a stricter medical sense, you're almost one of the healthiest people I've ever seen.Finally, someone has a sharp eye!So the truth has been unravelled.There has never been any illusions, nor is anybody putting on some strange, absurd, fire spitting show and-But she did not lie!Please, take a look at this.
```

### [87] hash=`cb8c15e87bd68163`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
According to the analysis, the core of a fire consists of an obsidian gravel that has 22 evenly distributed layers.This is no modern thing.It's old.Dead in back thousands of years.What?What do you mean?Whose side are you on?Um, have I made it difficult for you to understand?Well, you'll know when you see it.Please bear with me for five minutes.Have you heard of the Reincarnators?It's one of the Arcanus lineages, a rare kind.
```

### [88] hash=`37746687e4fc2df0`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Since this power can only be randomly triggered,and its manifestation could happen anywhere,any time and in any fashion, it is hard to identify them when there is one.Themost well-known case must be Dorothy of London.She fell down the stairs in herown house and lost every vital sign.But she woke again and became the ancientEgyptian Bantrashid.You...you're not saying that she's...Miss Spathedia is a reincarnator.
```

### [89] hash=`f0bfba34b101f323`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
Those so-called illusions are not aof any brain damage.They were once real.It's her past.Based on the past cases, she'll go througha period of mental turmoil that could be short or longer than anyone could expect.But eventuallyshe will become herself again.The old self.But how is that possible?Everybody knows thatthe reincarnators are just some lousy made up tabloid stories.That's right.Sensationalism,
```

### [90] hash=`07c68cce1be0bb70`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
That's the mainstream opinion about the reincarnators.In Dorothy's case, her experience of learning Egyptian and her career as an archaeologistalso caused controversies over her true lineage, which is understandable since people haven't seena reincarnator in years.But at the beginning of the 20th century, when Dorothy fell down thestairs which decided her fate, Laplace's Scientific Computing Centre established its
```

### [91] hash=`db386ca697461f42`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
branch, carrying out studies of local fungi.The fungi study is a brand newdirection and it has been secretly developing next to the public since.Likethe Australian honey fungus, growing without getting anyone's attention.The facts will speak for themselves.Please allow me to prove it to you.Medicine Pocket, could you please turn off the lights for us?Cheers.When wetalk about reincarnation, the real question behind it is whether the
```

### [92] hash=`96a769be509b4a35`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
exists because the soul is commonly considered to be the essence of whatmakes a person who he or she is.If a person dies his or her soul will returnto the ever circulating network.What network?A theory developed from Riemenson the hypotheses which underlie geometry described the world as aneternal vast invisible yet ubiquitous knit.And as the news story describedA reincarnator is a miracle where a soul disappears from point A and shows up at point B without
```

### [93] hash=`253cde8fc28412e0`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
any clear reasons.Exactly, Ms.Verdin.I'm amazed that you know so much about the reincarnators.That report described the reincarnators is incomprehensible and spontaneous, butthe truth is we've never gotten close enough to observe and study them.That work I read in the textbook!Look, you have a sharp sense.Your arcaneus never cease to amaze me.The latest studies have shown that the working mechanism of mushroom flora may be similar
```

### [94] hash=`68af93e375040204`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p3`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P3【金格！金格！】）

```text
to the brains, and we have made some progress from that.This is why the study of mushrooms is important.It enriches our understanding of the reincarnators, for they are hard to find.Things floating in the air?Mushrooms?The Australian honey fungus.The mushrooms living beneath the ground.It's a pathogenic gem that causes roots to rot.It was first discovered in a eucalyptus plantation in southeastern Australia.
```

