# 剧情图谱抽取 · batch 107

- 角色：`wu_ming_zhe`
- 批次：**107**（未缓存补漏批 8/8，每批 95 块）｜本批块数：**30**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_107.jsonl`

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

### [0] hash=`00c4cfe94bdcc147`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
Trying action?Shameful violence?You set an ambush here?You crazy addict of imprisonmentand war.I must blow your cover.Are you not one of them?Of course not.Sorry.Stayaway from me.You must be the demon that Iverson summoned.You're more horrific thanthose robots.If I say it's all a misunderstanding, could, would you understand?What do youIt's the biggest difference between Iverson's company and ours.
```

### [1] hash=`21ce9a6ce4a4286f`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
Really?I still feel pain in my neck.It's just an accident.As compensation, I will get you out.Fine.Apology accepted.When will we start off?In five minutes.I have to change the terminal valve in the room first, adjust the position of the deflector in the duct, and change the airflow from the spiral fan.abundant magnetic glue will be blown out of the ventilation ducts by the spiralfan and adhere to the robots the fine glue will paralyze them completely
```

### [2] hash=`faf3da1e618b10e8`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
after that you could just walk away sounds like a big project do you needmy help absolutely stay as far away as possible from the regulator valvebehind you
```

### [3] hash=`6bfeef9178453b9b`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
Captain, isn't our destination supposed to be the exhibition hall of the Rimmet Cup?Of course.I think we just missed the front gate at the junction we passed just now.Where we are now looks like a deserted back door.And there is a no entry sign.It's not important.It's not good for the fan-favourite distrokey to appear in the crowded areas.I don't want to make a noise.Oh, I see.I thought it was because Captain didn't have enough budget.
```

### [4] hash=`93d8c401939ccf55`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
A complete misunderstanding.Our aim is to convince the ragged lad to expose the evil plans of those tin monsters.Of course we can't just walk in.Mr Apple, do you remember Tommy's offer of a generous reward?He hopes we can divulge a sensational secret.Captain, it seems you really want that bonus.Of course not.The righteous street pirate has a warm heart.We should do Tommy a favour.And we should accept a friend's quality thanks.
```

### [5] hash=`320a4fff6abe0078`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
I get it, Captain.The Great Rock Pirate saves the day.The cocky ragged lad is no longer stray.The big hero who saves London takes a series of exclusive interviews.Endless bonus!Captain.Captain, watch out!Are you guys from the government?I've done nothing bad.At least not yet.The skin hardness, the voice and the liquid released from the wound have nothing to do with humans.I am afraid they are...Oh, I get it!
```

### [6] hash=`144931e1ca06bb0d`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
They're the security robots in the newspaper!Well, it might be.A new way to keep order in London?Those fuddy-duddies don't have their bids in their heads, do they?We'll have to change the plan.London must not be taken over by these ugly tin monsters.We need to expose the security robots to the public for what they really are.They're violent, rude and extremely dangerous.This Apple will fight by your side till the very end.
```

### [7] hash=`9917480ffb06beed`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
No, you have a more important mission, Mr Apple.Captain Regulus asks you to take over the nearest radio station.Roger that.It says clearly on the leaflet, we welcome everyone who loves football.Yes, Mister.then you should let us in.Me, Wendy, Alice, Nelson, and Little Pickles, we all love football.I'm sorry but no pets are allowed in here.We provide pet keeping services with professionalpolice dog guarding.
```

### [8] hash=`8fa5182913cd6e60`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
ErrrrrrrrrrrrrrGo ahead Wendy.Looks like we'll all have a good place to go.Have a great time inthe puppy land.Lovely to see you again, puppy with blue eyes.This apple has acceptedcommission from captain to investigate the venue.Alright, since last time we met, this apple hasbeen contemplating how to communicate with you.So here it is.A simple translator.Doggy.It'sstill under testing so the functions are not complete.
```

### [9] hash=`14c0eba5889d3f81`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p7`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P7.天才调音师｜小礼物）

```text
Sometimes it just stops working.Alsoit might somehow misunderstand dog language.The puppy expresses his gratitude.It's myThis apple doesn't have adequate time to test it.You'd better leave as soon as possible.Those violent security robots may show up at any time.The puppy expresses his denial.There is something very important for the puppy inside.Oh, I see.Fair enough.Let's head forward.In the face of danger, this apple will do his utmost to assist.
```

### [10] hash=`13d26a575b1a564c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p8`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P8.空降嘉宾）

```text
How do you find this place at a glance?Have you been here?The puppy expresses his modesty.The mission assigned by Captain progresses smoothly.We have a whole set of broadcasting equipment here.Then we only need to installa corresponding frequency interference device.Captain Regulus can fully control all radio channelswithin the radius of five kilometers.Bloody hell!Who let this plushy monster in?So now this whole place is contaminated by disgusting fur.
```

### [11] hash=`6a4faa9373bec676`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p8`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P8.空降嘉宾）

```text
Robots!Where are my robots?Drive it out!Command received.Unknown energy detected.What's wrong?You broke down?Risk rating.Request support.Terrible plushy monster!It must be a terrorist!We must put it down right now!All of you!Drive it out!No, no, no!Put it down!DEFCON 3!What are you doing?Get away from my pickles!It's you who brought it in.I now warn you, your dog is a bloody hazardous uncertainty and we must put it down.
```

### [12] hash=`a861f1377a4baf8a`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p8`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P8.空降嘉宾）

```text
What a humbug.He's not hazardous at all.Every one of our neighbors loves him.Let's go!You don't have a voice here.You can't leave either.According to Item 5, Article 172 of the Guidance on Security, security companies have the right to directly deal with any dangerous items when on duty.I command you to hand me your dog.As compensation, we will buy you a more purebred and more friendly dog for helping us wipe out risks.
```

### [13] hash=`bce4c6058f6c22d2`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p8`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P8.空降嘉宾）

```text
Don't lose your mind to a pet dog.My friend, crazy bastard, would you ever leave your friend alone?Fine, maybe you would.Cold-blooded crap, dead from the neck up.Put onto the World Cup audience blacklist, I kindly request you to stop what you are doing.Very well done.But I'll tell you what, you can't threaten me!I'm definitely not leaving Pickles alone.Go fuck your World Cup!What a fool.Catch them!
```

### [14] hash=`eae03d2879e3f036`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p8`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P8.空降嘉宾）

```text
Turn the ventilation system to the highest mode.I don't want any dog fur here.Other robots, go catch that dog!Man confirmed.What's going on here?What have you done?not me the ventilation system suddenly started to work this is the perfect planyou told me we're going to be blown out slow down too late crash warning hi
```

### [15] hash=`f17abe219491046e`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Nasty invader.I'm sorry, Mr.Iverson.Actually, I didn't know my entrance would be so straightforward.I think she knows the situation better than...Huh?Where is she?It seems you are the abandoned poor worm.What else are you going to show me?Any jokes of the never-will-happen utopia?It may be unrealistic, but it is possible.Lots of bubbles.Is this the special event of the exhibition?These soap bubbles are...
```

### [16] hash=`e9d734fec8a79f33`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
I see.The ventilation system is switched on.The soap bubble device I threw inside is now functioning.Excuse me, may I borrow your broken robots?Stop!What the hell did you do?What are these damn bubbles?Actually, it is a reformation of art.Get down from there, you bastard!Provoking the robots?He did sign a safety commitment statement, right?My friends, have you been fed up with the dull and dreary reality?
```

### [17] hash=`aba0e0bfbfddeaaf`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Do you want to get rid of this place of cliché and red tape?You once yearned for a better world, a peaceful world, with music.Open your eyes and look at the soap bubbles in front of you.Now!And salute to all the transient beauties.Predative fray ready to deploy.Don't you want to try some of these bubbles, Mr.Iverson?We can find a peaceful way to coexist.Boring little trick.Aren't you curious at all?
```

### [18] hash=`3c48dad45dd9282c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Take a look at it and you'll activate every cell of art.Even iron nerds can sparkle their imagination.Tony, your imagination level is null.Joking time over.Your utopia has always been a joke.Only hegemony, hatred, and force can push history forward.Vein revolt is like helpless barking.Perhaps I will be expelled from this impromptu party, away from its artistic beauty and forcedto bid farewell to my new friends.
```

### [19] hash=`af4023aef2df90d7`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Perhaps people as insensible, cold, and numb as you will become mainstream in the end.But it is not now.Brilliant.Although there were some unexpected hiccups, everything went well.The fuse has been changed.Bullets replaced.Magnets installed.Please don't mind swallowing a slightly bulky thing.What tricks did you come up with?This is going to be the most crucial part.Please help me, Miss A.C.Actually, according to item 18 in the safety commitment statement,
```

### [20] hash=`609895122a3af170`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
we need to arrest the violators who interrupt others' visit.Tie him up and inject Mew Mew Mewtube Potion.I don't want to hear his stupid ideas anymore.Command received.Activate the spraying system.Clean all those damn bubbles.The farce is over.All our guests, please enjoy your visit.Unfortunately, those who were bewitched and violated the safety commitment statement, you will be further investigated after the exhibition.
```

### [21] hash=`a5b99bed6b8eaf10`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Give my microphone back!My bread!I only took a bite!What's going on?Who let them in?Sorry, Mr.Ives.There are too many of them.In time, the sharp pirate captain has arrived at the grandest stage.It's 25 degrees east.You are listening to the Rockin' Apple, the most distinctive ship to date.Salute to all my discerning audience, my loving followers.You get it right.This pirate has hijacked all the radio frequencies here.
```

### [22] hash=`05b291ac2f796c88`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
You're able to pick up Radio Apple clearly from anywhere in London.Whether you're cheering for the moment or wish to change the channel, whether you love rock and roll or hate all music, do not switch.If you don't want to miss the moment to unveil a conspiracy, a huge conspiracy about the London authorities and the compelling security robots.My friends, we are in the middle of a huge hoax.The London authorities have deceived everyone.
```

### [23] hash=`dee7dec14efb4df7`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
It is impossible to have such obedient, flawless, safe and reliable security robots in this world.On the contrary, they use violence, harm citizens and show no kindness.What?To cover the back sides and block the news, the man in charge, he keeps out the people who want to have fun to visit the Rimmick Cup.Captain Regulus clashed with the robot army at the back entrance of the hall.The brave captain managed to escape, to retreat, but there's no doubt that this is an infringement of our freedom.
```

### [24] hash=`8877d88179afaae6`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Competent London authorities attempt to work with security companies and use their awful robots to govern.They want to take our lives away and render us helpless so they can manipulate us.You have my respect, poor ragged lad.What that pirate said, is that true?I am very sure you are deceived.But you did imprison the poor citizen.If that's what you think, I can now prove to you the reliability of new humans' security.
```

### [25] hash=`7df505836c6de6af`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p9`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P9.泡泡无可破灭｜自由的频段）

```text
Mr Madbotch, you and your evil plan have been overcome by the Justice Captain Regulus.London belongs to us, belongs to freedom!You're right.In such case, security guards are more flexible.you you mean do something these people are breaking the rules are you justgoing to stand and watch copy that what are you doing Apple here put the tapeaway this pirate's instincts are never wrong my assistant mr.

Apple hasfirsthand evidence of everything it'll be the most sensational news every newsagency will invest millions on it.The next song for the exasperated poorauthorities.Mm-hmm all is ready
```

### [26] hash=`bbb8eca0ce3041f0`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
We're used to it.Fighting for every street.It's not worth it.But your friends!Maybe you ought to stop nosing around where you don't belong.I'm sorry.We should get going.My Isha's got things to do.You shouldn't be so hard on her.I do not think I can make this decision for you.I get your concern, but she's my friendI don't want to put her on a dangerous pathSo there's three guys in that tent.I knew the boss was here
```

### [27] hash=`6782c6459eb3353d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
But who's the third dude Pollock?I heard he was in the market collecting informationWhat where are you here?You're that big guy.Let's use luckySo Mrs.Mercuria will be here soon too.According to the investigator's manual,wait for the most reliable support and action.But if the situation continues to worsen,another civilian could be involved.Maybe I should let Mrs.Mercuria join us, shouldn't I?Where is this old man?
```

### [28] hash=`c50bf9df6ab3dc5f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
He didn't come back once all night.This man has no sense.Madame Mercuria will be on stage soon.I have to decide before she goes.Like me, she provides another option, but in the end, we can only make decisions forourselves.Her dance offers to break them away from the reality of time and the weight of decision,even for just one song.Thank you, Monsieur Pioneer.Don't go to the living room.I have to catch her.
```

### [29] hash=`6135b354b6cf6faa`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
It's...it's Mr.Gio inside his tent?I knew that my memory wasn't wrong!She's hiding something from us, and this Gio seems to be special to her!But...if she's from Manus...No!Stop, Matilda!You can't make such an active guess!Mercury can't be...
```

