# 剧情图谱抽取 · batch 086

- 角色：`wu_ming_zhe`
- 批次：**86** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.0」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_086.jsonl`

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

### [0] hash=`2d177a686db373b6`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Damn it.Just wait and see Jay.I'll make you payHey Geo, right you forgot this if you need help find me in the new age marketLet's play a game for you Paulina, don't you see it?Stop!I'd rather die out there than stay here and never live at all!Alicia!The game isn't over yet, Jay.The Honorable Apostle and Miss Mercuria have been expecting you.Answer me, Jay.What are you going to do when your friends point their knives at you?
```

### [1] hash=`fc0098b5dcd7881a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
How do we keep their sacrificial lambs from leaping off the cliff?To my days out junkies, my loud and proud mischief makers, and all my beautiful little heartthrobs.It's your oldest and dearest friend, with the straight shooting of your father and tender loving just like your mama.It's your boy Vincent, aka the old ostrich.Bringing you a balanced dish of good news, then let's soften the blow with the good stuff first.
```

### [2] hash=`efe75ae69ea3f17b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
The New Age market has finally gotten a little re-invigoration after the Harmonic Convergence.Was it a sign from another world, or the harbinger of a Mayan doomsday prophecy?Who knows, but why worry my lovelies?Keep those heads in the sand and your ears to the ground.Because more visitors means more money.Huge potential for young and old to make some dough.To hit you with the bad news, yesterday's gangland battles stretched from the six all the way to the steps of the People's Palace.
```

### [3] hash=`986447e300446043`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
And it came with a particularly heavy drizzle of bullet casings to rattle you all night long.Last night, Legerza dead and his Arcanus minions booted the Tung Ching champ so hard in the ass that they've been driven right out of our city.If you're brave enough to head out into the streets, might still find a few gold teeth left on the ground.Now the sweet, naive souls among you might think that means our fair city will finally have a moment of peace.
```

### [4] hash=`b7e4a32cfd5f9c8e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
But you listen to Papa Ostrich here, kiddies.This is only the beginning.What the Jairs wants is nothing less than the whole damn city and I have it under the authority where he's headed next.I'm told his aim is to make a deal with Hape Street's very own Joe, aka J.Brown, for a steak and that juicy New Age market pie.Here's hoping that it goes smoothly, but if that fails, at least we'll have some quality entertainment.
```

### [5] hash=`f1cbb99b811a5c93`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Now it's time for the old ostrich to duck his head again, leaving you with some solid music to groove your body and shake your booty with our next track, The Golden City!Pop ostrich.Give me a break.Anyways, what can I get you, guy?Tequila.And?Straightforward.I like that.So what are you after?The waitress' phone number?Ticket to an underground boxing match?Or are you after someone specific?You know what I'm after?
```

### [6] hash=`f4b6d575801c9d31`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I'm after you shutting your damn mouth.Cut the smart shit with me and listen, because I'm only going to ask once.Where is Jay?Point him out, and get your ass out of my son.Well, hey, hey, easy, man.I'd be happy to.You gotta tip me.That bastard owes me money, so he can go ahead and beat his ass.Don't want afor me you better not be playing with me because that's a good way to get cut buthey now little heads up Jay was born and raised in Haight Street and he knows the
```

### [7] hash=`7cacc568a6aa0577`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
place better than anyone and circles around the cops won't be easy to cornerplus he's got a lot of friends around so picking a fight here could go southfast never know who's liable to stand beside him but you know what I say theThe good times are over, so Jay and all his crew can bite the big one for all I care.Hey, and uh, just so you know, you're the first one with enough guts to mess with him.So, whether you're here to break his nose or...
```

### [8] hash=`77685f3eaaf36c14`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Well, this shot's on me, bro.To you, and your boss.Y'all smartass.We need more people like you.Young guys these days.Jammed by arcades and slots, you know?These adult children living in their mother's basements.They ought to be out here begging for a job.What's your name, pal?It's Vern, sir.Put it there, Vern.Call me Geo.Alright, now you point me to this J-Bastard, and afterwards, if you're looking to do some hustling, meet me at Rue Street.
```

### [9] hash=`9caf705e8bd278c8`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I'll take you to the boss.But, uh, mind yourself around here, will ya?The old man's been unpredictable lately.Quick to fly off the handle, you know?Thank you, sir.I probably shouldn't pry, but what do you want from Jay?If you want to take him down over Hate Street, you'll be disappointed.This place has got nothing but struggling folks.He couldn't mug someone for enough to catch the bus.What else could it be?
```

### [10] hash=`92305453f06f8662`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
A damn new age morning.Don't know what Pops is planning to do with it, but he's gotta have it.Not like I'd give a damn otherwise.What kind of schmuck does business in a gutter like this?Pops is stubborn about it.Used to be I'd have a say in private, but he don't listento anyone now except those freaks from the Order of Enlightenment.Not that I'm cryingabout it, but robbing folks who ain't got no money, kicking them while they're down,
```

### [11] hash=`bfb328048ea6c05b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
it don't sit like that.But order's orders, so maybe I'll turn a blind eye.When I can,you ask too many questions.no worries man you were looking for Jay right that guy in the suit with thedance floor see him later Jay three two one gentlemen what is happening here tieup his hands but careful you don't break them for now sure thing mr.Geo whatthe hell what's going on with huh that hurts you got rocks in your jaw
```

### [12] hash=`b043849198017054`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Trust me, you're the perfect bait.You draw the fishies in like a magnet.This is terribly unbecoming of you, Jay.Do you realize how many times this is?My body may be artificial, but my soul can feel pain too.You lion sack of shit.Not so friendly after all, huh?We'll continue our conversation later, Jay.Easier to fight here than a back alley.Now who's lying, Mr.Geo?You took my shot, but you didn't even break that J-guy's nose.
```

### [13] hash=`709d07a4d89512ec`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Still, thanks for the offer.Give my best to Mr.Leger for me.The old man is gonna like you, smartass.We'll have another parlay.You and me.Yeah, yeah.Run on home with your tail between your legs.Pfft.Leger's losers.Looks like he might need a dentist, cause he just got kicked in the teeth.They'll be home crying into their cereal soon enough.The way they're hoofing it, they could have outrun my four-cylinder Hummingbird GR8100.
```

### [14] hash=`d86eb31f2661af50`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
They must have missed their calling.They ain't dentists, they're track stars.Hahaha!Cheers!To unbreakable bonds!Look Jay, I gotta go.The shelter is going to be closing up soon.And my partner at the shop, you know, he doesn't like it when I come in covered with blood.Scares the richy rich types away.It's all good, bro.Thanks for coming today.If there's anything I can help, you know where to go.Thanks bro.
```

### [15] hash=`f3e491f6b5bf52d7`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
But if you're really such a good friend, how about you spot me a quarter mil or soso I can buy that sweet new convertible Lamborari LM50.well since we're such good buddies right yeah sure thing buddy but after I giveyou a knuckle sandwich see you around Jay would you kindly give me back mydamn hands already hey stop kicking me just a sec my apologies where were mymanners please don't take it personally but I need to warn you that
```

### [16] hash=`592879892c126d1c`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Whoa, wait, wait.Someone's missing.Where's Mercuria?Hey, Miss Sputnik.Have you seen her?Oh, Miss Mercuria.She left in a hurry, carrying that dagger those rough type gentlemen dropped.Do we follow her?No, of course not.She's just doing her thing.The old man didn't tell us what kind of mess we were in for here.I'm not paid enough for this.Hey, Gio, right?You're just giving it back?What's this meant to be?
```

### [17] hash=`8bb44004a6286876`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Some kind of insult?Hey, yo, your boss runs me off, now you're giving me back my own knife like I'm somepity case?Think I won't hurt you because you're a woman?Think again, bitch!What is this?The color of your energy is as dark as the coal in Jay's Forge.No.Worse.Darker than I've ever seen beforeAfraid but something else besides thatI see a burning energyThe embers of a home reduced to ashesa harrowing darkness
```

### [18] hash=`a097ce1ece64a712`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
That's followed you throughout your lifeWhen your wife and child left youWhen your debtors begged on their knees at your feetWhat are you talking about?I understand you now Mr.Gio.Forced to live with this darkness inside you.I'm sorry ifI scared you, but I'm only here to return this.You're a boy trembling inside this brawnyshell of a man.You're too far down a path that you never wanted to set foot on.
```

### [19] hash=`8d3c2a5518f1775e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Mr.Gio, if you need help, find me in the New Age Market.So as I take off the tire, I notice the gal.Some rich lady from the market's got a crazy look of worry on her face.So I tell her, break my jaw if I'm telling a lie.We're good folks here.Don't believe me?Just ask around about Jay and his friends on Hate Street.Please, take care Mr.Holick.You have been drinking way too much.Come on, Hollic.You don't got the balls.
```

### [20] hash=`b22f76b412e5f6dc`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I saw this guy get a nosebleed yesterday and he cried like a little baby.Back me up, Jay.Hey, Jay?What?Did they bust your head or something?You're off daydreaming or we're talking about some rich bimbo.Sorry, Mr.Beckett.I believe Jay's present concerns may be revolving around, you know, Le Gere's the dead.Nah.We off stuff shirt.take a look bombshell news uncovered video shows fae used as new execution
```

### [21] hash=`4df9eb468f5f0473`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
method for the minds of those Hollywood producers think of next oh I thinkI've seen images from this video from spam mail and newspapers we're stilltrying to identify this woman to confirm the authenticity of the videoIf you have any information, please call us at 429-7234-X7.Up next, homebound or hoodwinked, the mystery of the so-called long-lost son.We turn to the story of Sergeant Howard Eden, a retired Army veteran and the stranger claiming
```

### [22] hash=`d4ae31c3fe18b332`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
to be his long-lost son.But, is this a heartwarming reunion, or a sinister story of senior exploitation?Let's...Oh, too bad.You know, it's good fun watching all her nonsense and sensationalism.Hey, show some respect.Sure, that whole, how woodchucks could control the world peace she did was a little iffy,but who knows what those woodchucks could chuck at us.Alright, that ledger's thing is really bothering me, okay?
```

### [23] hash=`435bdff20f0d45a1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
What's his story?I've heard it, not gonna lie, kinda sick.Cops hate him, but the street punks love him.They say back in Hunters Point, a bunch of guys was swatering him, had him tied uplike a pig, and when they got tired, they put a gun in his mouth and made him eatit.The bullet went straight through his throat out the back of his headBut when the cops came they found nothing but a few bloody teeth.
```

### [24] hash=`d307e58a2aa057ee`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
He was goneHmm scary, right?But here's the thing.YeahLegers is a pure humanSo what happened?Where did he go?Mr.Halleck, I think you've been watching too many of those horrible Romero moviesPeople returning from the dead.That's hokey cinema not realityI can only assume this leger is the dead and made up this rumor himselfPerhaps so he might attract more powerful arcanists to his sidepotion addictsSmugglers card sharks getting them all under his thumb until he can cobble up the whole of San Francisco
```

### [25] hash=`362174ff85c8ab00`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
And yeah, it's been working but not anymorebecause we ain't gonna sit and watch afraid you're overestimating ourstrength mr.hollick their enterprise is much more dangerous than all ourprevious rivals no less so if they're aiming on partnering up with thelunatics in the new age market gotta agree with that assessment pioneer it'sbeen days since my last session with a paying customer seems like everyone
```

### [26] hash=`432a87f634611efe`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
is joining up with them and their energy is disturbing to say the least.They'vebeen poking around my shop looking for some rare sort of books and materials,kinds I never even heard of before.I would advise avoiding directconfrontation, Jane.I hear you.Avoid confrontation.That's the right move forsure, but it's not gonna be possible.They aren't giving us a choice.Theshops abandoned Hate Street a long time ago.
```

### [27] hash=`e175ddcfb406294e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Ain't nobody that cares about these streetsbut us now.Remember?That was when all those artist trailers were burnt down.After that,the rest of the diviners and such were ran off quick.It's only those loonies thathave stuck around, misguiding our canists, making everything worse.We were smart.Wewould have left then and there.Closed up shop.Took the first bus out of theI know what you're saying, but I don't know, man.
```

### [28] hash=`1196efa806124234`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
That kind of talk is for cowards.We don't have to get them involved in this.You have to admit that they care about our canists, despite all their bureaucracy.Turning to the Foundation would not be a bad choice for us, Jay.Yes, Mr.Jay, I think Mr.Pioneer might be right.I don't want to lose my job because of these bandits.I'll be glad to bring you to the foundation.Your assistance would be more than welcome, Miss Disco Ball.
```

### [29] hash=`0b5cacfd2106d0b1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
It couldn't possibly hurt to reach out to Paulina.Maybe she could help us with the red tape.She's your sister after all.No.I'm only going to say this once, and it's for real.This is our own business, nobody else's, and especially not hers.Paulina made her choice.She could have talked with me.She could have approached us if that's what she wanted.She had the chance.She's had years.Not a word.She has her own life.
```

### [30] hash=`2e5765b40146a94b`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
And she made it out of these streets.She ain't coming back.She ain't even looking back.She's not that little girl tagging around us anymore.She's got fancy marble floors now.Got all that decency and good taste that she never had here.She doesn't need us.She's not that little girl tagging around us anymore.She's got fancy marble floors now.Got all that decency and good taste that she never had here.
```

### [31] hash=`19b60f3db6f75fe5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
She doesn't need us.You think I'm gonna scrape down on my knees for her?Heh, I'd rather stick my foot in hot slag.At least that way I'd have one leg to stand on.Jay, please just give it some thought.This may be the only way for all of us to survive this.Ugh, I need a drink.something just hit me and my shoot run mr.J all the money in the bar is um howis it you're saying gone cat catch that kid the puppy wishes to come along boss
```

### [32] hash=`3366995c6db9ac23`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
this kid's like a rat he's scurrying in between those boxes we can't catch himLooks like we do this the hard way, Jay.Don't blame us for breaking nothing.Come out, you little rat.I got my eyes on you.Haven't you eaten?Knew it.Cat Eye Weizen, owner of the most infamous sticky fingers from here to the market and back.Little dude, I know you're dattering off with those guys from the Order of Enlightenment.
```

### [33] hash=`53037354f90df8b9`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
But why didn't you go to the shelter?You trying to get yourself hurt out here?Let me go, you big jerk!Sooner or later, someone is going to teach you a lesson or two.Don't think that arcaneist mom of yours wants you using your cat eye to steal things.I know things seem tough right now, kid, but acting like the world owes you something,it's going to bring you nothing but trouble.When I got my finger chewed up by that machine, I lost everything.
```

### [34] hash=`6e4c703a17c1b228`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I could have went around sticking up places.I didn't.Think you got it worse than me?Hey, we're going to let him go just like that?Your friends are waiting out there, but mr.It's fine.It's about NickLet him go these kids lost their homes to the New Age market their parents deserted themThey've got nowhere to goBeckett look at them.You can't compare it doesn't work like thatEach suffering has its own energy
```

### [35] hash=`4f57a3019582c180`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Man, consider my second thought thought over.But get this straight.If I see her fold her armsand give me any of that snooty attitude,we're gone.Out the door, no discussion.Those men in white sets,there won't be any more bad people around the school.And nobody will be hungry, just like before.Like with mom and dad.They'll give us candy and soup and meat every week.And a big comfy house.Cover up a little more, Polly.
```

### [36] hash=`48ea23b6e9e61e0f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
You're gonna catch a cold.You can't trust anything adults tell you like that.If they give us candy or soup or even meat,it's because they want something from you.Nothing you get in this world is just given away,at least of all from people like them.But they did give me a fun job.See, now I can make store doors and sell them for money.That's because they need you.Our little Paulina is one of the most cleverest kids in all of Hate Street.
```

### [37] hash=`a544e42f65c5c023`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I'll say bad guys.Bet on it.Only good adult I ever met is Mr.Tang.Okay.But Joe, what if they're not lying?And you don't have to wash dishes, or take off tires, or any of that stuff.Don't overthink it, okay kiddo?I'm right here with you.Always will be.Okay, but if you do leave, you have to tell me first, because we'll always stick together,deal?Deal!Sleep tight, Bollie.This place is ritzed up like a palace.
```

### [38] hash=`6c80005414fabdb9`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Who do they think they are?Who needs a floor that shines like a mirror, where they hire a dog to lick it clean everyday?Philistine as ever, Jay.It's evident the people here must possess exceptional aesthetic taste.I'm at my limits of you sucking up to them.This place is built like a fortress, a bomb shelter.Makes me feel like I've got a target on my back.Can't imagine why anyone would feel safer here.
```

### [39] hash=`f6188f6abc62f8b7`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
You ask any artist, they'll say,Clean kills the soul.Might look clean and tidy on the outside, but inside...Bit oaf that does not know how to watch where he is going!Hey, mind your manners, shortstuff.Excuse me?Just call me Short Stuff?I apologize for my frankness.He ought to mind his own manners.Then you two look as though you have just wandered in like, how do you say, lost puppies?I'll let it go, just this once.
```

### [40] hash=`3ad7f12c63be4f48`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Are you here to register as Arcanus?Sorry, we're just in the middle of a shift change.Please wait a moment.Isn't it Fiona's shift?She should be able to handle this on her own.There is work to be done, people!Quickly!Retweet!Got it.Welcome to the Saint Pavlov Foundation Reception Center.How can I help you?Hello!We're here to visit a member of your staff for, um, some private matters.If possible, we'd like to have a conversation with her in person.
```

### [41] hash=`a6c58f18422a4d00`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Sure.Please read the visitor's advisory here and fill out these forms.I'm so sorry, sir.Just let me pick these up.Relax, miss.It's nothing.Just a short visit to my sister.She's like a clerk here, or something.Nothing important.Her name's Paulina Lassage.Just tell her that it's her brother.Just pop him by for a visit.Paulina Lassage?Could you tell me your name again?It's Joe.Joe Brown.You can call me Jay.
```

### [42] hash=`5ca0858a6f1571d0`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Follow me, please.Miss Paulina was one of the first people I met when I joined the Foundation.she was so talented so incredible it was no wonder they gave her all the bigassignments I could always tell she was very proud but not in an arrogant wayshe never turned her back on people I always knew I could turn to her foradvice it's the first time that we swept Manus that badly they even forgotthe rest of their supplies in the basement what are they gonna do without
```

### [43] hash=`3b64da308f8202a1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
those now that we have some spare manpower to chase after them I heard theRazor has started searching for the Foundation's lost assets.After all this time, we're finallyback on the trail.I don't know, man.Good as it seems to be, I'm worried the news is getting out of control.Now rumors are spreading everywhere.It could get dangerous.Otherwise, why would we havebeen assigned here with Mr.Bernard to get to the bottom of this?
```

### [44] hash=`19f9ee1518221354`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Zip it.What, you guys having a party or something?Never seen an office so...smiley.Feels like a sales day at the mall.All those eager girls and boys running past the window.A mood like this usually comes with good news.Please don't pay them any mind.They're just chitchatting.Doesn't really mean anything.It might mislead you even.Gentlemen, come in please.Despite all the smiles, it hasn't been easy for us recently.
```

### [45] hash=`7bf49cd328264614`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Our time and resources have been stretched thin.We've suffered a lot of losses.It still feels a little unreal that we're still standing.A lot of good people sacrificed everything they had to get us where we are.Excuse me?I suppose that's also just idle chit chat.Maybe I don't know any more than they do.I only just wanted to say, since you're family, that Ms.Paulina was one of thebest people I've ever met.
```

### [46] hash=`c28485de32465186`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
an asset to everyone here at the foundation this is where the remains ofall those that died in the service of the st.Pavlov foundation are kept inmemorial I'm so sorry that I have to be the one to tell you but Paulina ishere too you better know what you're saying miss I'm sorry Fiona dear wouldyou mind giving us a moment of privacy I'll be waiting outside J areAre you going to be alright?To me, Jay.
```

### [47] hash=`6885b5a43a1c5834`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Is there anything I can do for you?Maybe we can take a look, just to be sure.No, don't, don't do anything.But don't you fucking do a damn thing.How can all that someone is, was, be in a box like this?It's so small.This is some kind of sick joke!Jay!Easy, Jay, easy.Do you have her photo?But I don't understand, why would the editor of the show go to such a lonely place?What could it mean on URD?Okay, at least I can go and see mom.
```

### [48] hash=`4d1575ea6791c7eb`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
It would certainly be a surprise, what their Matilda has accomplished will make the whole family proud!My Matilda, special enquirer for the Saint-Pavlov Foundation!Now the little Matilda has thrown another star at the Boinich family's line!Miss Boniche, a moment of your time.Unfortunately, it seems our mission has been cancelled.Cancelled?You may have heard what Fiona did.Well, I'd heard the chatter about it, certainly, but she only just started as a receptionist.
```

### [49] hash=`4d944e117cbb13c7`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
It is no matter if she is a little unfamiliar with the processes and, uh...Her regulation since the first storm.Families of the deceased employees are no longer informed of their deaths.But she made a mistake, or forgot, and the two arcanus she received earlier got awayfrom her near the memorial hall.They didn't even fill out the proper forms.Oh, that could indeed represent a serious intelligence leak!
```

### [50] hash=`43797646ea8abf72`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
And Mr.Bernard asks that we get ahead of the narrative before it gets to the press,given how fast the news spreads in this day and age.New orders are for us to find these two visitors and prevent the information fromfurther spreading.Yes, tracking down the editor of O2 will be reassigned to some other team.Correct, ma'am.Tracking down these two Arcanists was given top priority.And those two were the same ones you ran into earlier today.
```

### [51] hash=`e529199c456661c0`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
My friends, after the Harmonic Convergence,we discovered the failure of prophecy and eschatologyAnd the new possibilities of coexistence between the faith in Pneuma and science.They claim there is one God.And God is dead.But is that so?Friends, it's time to abandon the disputes of religions and to know that we are one.God is you.God, it's me.The information that our escaped visitors have gone into hiding with an energy healer
```

### [52] hash=`299e3556e24374da`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
called Mercuria is crowded here.I'd rather not attract attention to ourselves, so keep your heads down.Some kind of temporary tent and a sign lying on the ground.Something's not right.I barely sense any arcane fluctuations here.Could it be a trap?This market is filled with unregistered arcanists, not to mention the human tourists.There are sure to be dangerous ones among them.I shouldn't have come.
```

### [53] hash=`f26b5ad7ee8a7424`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
They're going to slice me up and feed me to the pigs.Pigs will eat everything.All the bones, your head, not a hair left.That's how they treat traitors.Pops won't save me then.He won't stand at my side.No.But here you are, Mr.Geo, shivering like a new leaf, because you're ready for an answer.The answer to yourself.You brought a strange smell with you, and a weak faltering energy, like that of someone
```

### [54] hash=`41db64ed8d56e602`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
gravely ill.Have you been to any hospitals?Just follow the ledges.Nowadays only visits we have are the living and the dead ones, not much in between.We don't deal with addicts, or sick dogs.Wait.Shut it.Before you start, I'm not buying any of your goddamn spices or candles.I'm just here for an answer.How did you know the fire that took my family?How?Are you some kind of psychic?Or a prophet?Tell me.
```

### [55] hash=`4d99aa5cd7a61eb1`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Tell me!No.I shouldn't have come here.Unless, maybe I'd chop off your pretty little head and give it to them.That'd be my excuse.What have you got?What do you see in your hand?Is it a knife for my throat?Or a diamond covered key?Shut up!You're just a witch who survived her burning!A liar!Breathe.Slow and true.Look at it again.This is a dagger forged in your own dark flame.Everything has a shell of meaning.
```

### [56] hash=`5f72c7ed81ff3a8e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
But hold your gaze on it and it all strips away, until those words become strokes ofblack and that dagger becomes a cold sheet of metal.Is a cage, cast off its shackles and nature reveals itself to us.Don't be afraid, hold that feeling, now close your eyes with me, do you see it?A door surrounded by darkness.Yes.The door is...shaking.Like something's behind it.No, it's scared.Don't try to picture it.
```

### [57] hash=`cc0276546b812c4d`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Take away the shell.Just tell me by the impression.Where does it lead you?It goes...home?Fire!The door's on fire!No.I don't want to go there.Not there.Someone's screaming.Savina!My baby!No!Help them!Help them, please!That's over now.Look around.Who is with you?Pops and others.They're standing.With torches and chains.Who are the others?I don't know.I don't know!Their eyes are covered by hands!No, not hands!
```

### [58] hash=`4eb07b8b6591c186`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Those are hand-shaped masks!Hey, who's this girl?Didn't your mom teach you not to spy on people?Miss Boniche!Damn it!You're the girl from the Foundation!Ain't that just my luck?Candy.Mr.Brown, we have need of your cooperation.We do not want to hurt you or your friends.But should you continue to resist, we'll be forced to take necessary action.Unbelievable!So rude!Even as an Arcanist, all he does is this vulgar hand-to-hand combat.
```

### [59] hash=`1d3927cb87a57e67`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
That long stick he carries most certainly isn't a toy.If you would be willing to come quietly and play nice,I will consider lowering your risk rating in our report.I gotta say, sometimes I wish I could take a knee in surrender.but sadly even after all those hard knock lessons I never learned once howto raise the white flag put it down Jay your fight is over this this is thesmoke of burning mandrake cover your nose in your mouth hold your breath stay
```

### [60] hash=`630dfff436dec02f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
away from the should know that kidnapping a foundation investigator andinterfering with an official investigation is a serious crimeEspecially when you've kidnapped the one and only Matyza Bwanish, a pivotal figure in the St.Pavlov Foundation we're talking about!Pivotal, eh?Huh.A whiny little pup happens to stay standing from a little smoke.Yeah, I don't see anything worth being proud of.Tell me, did Polina send you to ask us to sign this bogus confidentiality agreement?
```

### [61] hash=`ed74d8ac4bce5e2e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
Let me guess, she's probably still hiding in the Foundation office, right?Too scared to see your own flesh and blood?What are you talking about?We're here to bring you and that mannequin back to the Foundation.This is a serious violation of the visitor's advisory.Jay, I think we should ask this another way.Miss Bwanish, what proof do you have that Paulina Lassage is dead, as your receptionist claimed?
```

### [62] hash=`c669bb196debaa23`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
The photo on the box isn't hers, just some lookalike or airbrush job.So how can we believe anything else you say?Isn't the same as the one in this photo?How can I explain this to you?Please, be assured that we have no reason to lie to you at this juncture.Actually, you shouldn't have found out about any of this in the first place.Maybe I'm not familiar with your Polina,but I do know that there was a woman at Saint Pavlov's named Polina Lesage,
```

### [63] hash=`1dbfd1252e8b5a09`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
and I know that she died.As far as the claims of different photos, mementos, it's complicated.There is a little I can say freely, but headquarters is working on it, and many other similar cases.I don't have the kind of clearance to know what's really going on, and even if I did, I couldn't tell you.For everyone's safety.Huh.So a little prize investigator's also in the dark.something she once owned or often used.
```

### [64] hash=`b59696aa2b96cd8a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I will then begin my scrying using this object to the fog in my crystal orband reveal to us her current existence.But if we find nothing beneath the fog,I am quite sure you understand what this means.And then I will be needing you to return with me.And as I have heard that energy healers are able to detect the flow of Nema,Alright, Frenchie.This is hers.Take it.Then let us commence.Binds all.Show me the trace of the one to whom this belongs.
```

### [65] hash=`1ad9b815a398c27a`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p64`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 1~5）

```text
I bid you to respond.Lift the fog.Reveal what existence lies hidden from us.Give us your vision.Sight beyond sight!What?All that and you just stop?This thing busted or something?Nothing happened.Jay, the divination is over.The energy is gone.Just like she said.You come all this way for what?Just another foundation trick?So what is it this time?Did you mess around with the orb?Some kind of protection skill?

You don't have time for these games.Jay!It means she's really gone.Sorry, Jay.Are you still with us?Yeah.I'm fine.So I guess it's legit.
```

### [66] hash=`7d319802effaeade`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I feel like a bastard!How is it that I still need to learn not to trust anything that comes out of that...That stupid lying jerk's mouth!Mail today, sis.Nah, no visitors yet, Polly.Haven't heard a word.Another pack of lies.And I bought them!Hey Polly, open the door!What are you even doing in there?Lone Joe!Who the hell do you think you are to decide my choice?My future, my fate!Don't talk to me.Don't ever talk to me again.
```

### [67] hash=`d1f98ef666d1bbf2`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I'm leaving today.Whatever!Why are you even this obsessed with this mission of theirs?They're fooling you, sis.Don't you see it?Only two kinds of people that buy the Peace Be With Us kind of bullshit they're selling.The first kind are those like you, Polly, stupid kids that don't know nothing about anything except what they've read in books.And the others are the ones fleecing you taking all you got and spitting you out.
```

### [68] hash=`d609f1cc999d1662`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Also, they can have more money more controlPaul, I'm sorry.All right, I flew off the handle.I made a mistakeBut these guys PaulinaDo you think they care about you?about anyoneYou're just another penny in their pocket a coal for their furnace.They'll burn you up and replace you easy as thatYou think you're going out there, do something big, because you don't even know what lifeis yet.You just read about it in your books, telling you some shit about a foundation member paying
```

### [69] hash=`5d3a8f519f42822f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
the ultimate sacrifice for others.I think that makes them some kind of hero.You don't know what that kind of sacrifice means, sis.Do they say how those brave foundation goons really felt facing death?They aren't going to tell you they were afraid, that they hated everyone who put them there,that they probably shit themselves before they bit it, just wishing they could go home.They don't put that in books, do they?
```

### [70] hash=`a116187a8d0efc4d`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
You read what they want you to think.It ain't the truth, Polly.Maybe I'm not smart like you, sis.I can't read the things you read, can't learn like you.Why learn the hard way?Clap about what you learned on the street.Don't want to hear itI'd rather take my chances and die out there than stay here and never live at allShe was on this other levelcommandeerBarter de mauvaise nouvelleMe oh my man, no, he's so proud co-operate.
```

### [71] hash=`77f2fa518888eb2f`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
NoSeleman, es qu'ils ne se sont pas encore éveillésWe really have to report our information on the Vindicti Manus to the Foundation.After the death of Arkana, the remains of the Vindicti Manus were all scattered in the air,carried away by the wind, untraceable.They even abandoned all their hideouts and resources just to hide in this air.And it seems that they succeeded.There has been no trace of them so far.
```

### [72] hash=`c39a3fd078efb317`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Well, not yet.But I think that with this news, the special investigator, Mathilde Abouaniche, will be the one who will find the key.I am very sure that my ability of exemplary analysis will be rewarded by our leaders.Oh, maybe they will even place Mademoiselle Sonnetto in my team.And yourself please, I have had quite enough of these bumping accidents today.THE ENLIGHTENMENT!SOON COMES THE SUFFERERS' ENLIGHTENMENT!
```

### [73] hash=`b0fa4a9206e95f53`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
ENLIGHTENMENT!IT'S THE ENLIGHTENMENT!Yeah, yeah, chant louder, you stupid jerks.The higher you lift those arms, the easier it is to reach into those pockets.Let's do the most important thing now!And now, together we are their children.Only we possess the truth of salvation.Police, governments, communities, and nations are only the deceitful constructs of history.Our salvation lies solely in the return of the sufferer.
```

### [74] hash=`4633ff1d30392242`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
But now we must stand shoulder to shoulder as we anticipate our coming celebration ofthe sufferer.We await.We rejoice.We await.We rejoice.The sufferer has heard us.Know this, children.Now take heart, for we have another lost lamb who has cast aside the world to joinus.All, it is time.Follow the bell ringer.The gate to Elysium shall soon be opened.I have to return to inform the Foundation.I have to get out now.
```

### [75] hash=`431598a0afc24ea7`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Move!No, it can't be.Where is the key to the gate?Apostle Matthews, please wait a moment.Be vigilant, all.There are deceivers among us.Behold, the deceivers among us!Dang it, dang it, dang it!Where did you come from?Didn't anybody tell you whose turf this is?We are in so much trouble.They'll catch you!Damn it, they get to see again!Son of a gun, kid!What did I tell you about making a mess?These freaks are mad!
```

### [76] hash=`8f2f5c28636d00d5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Sit back.We're ever sitting in the road.Ha ha ha ha!So long, suckers.What brings you out here, short stuff?Starting to wonder why we keep running into each other.You've got a funny way of saying thanks french fry if I listen to you back there you'd have been stuck here and hung outTo drive.I need your help.I can't take care of these cookie cultists all by myselfAs you wish my ladyNight shining chrome at your service say the word
```

### [77] hash=`672af283ea8ad0a6`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
to protect civilians!Get on, Frenchie.Really didn't want to get involved,but you were starting to look like a lost puppy,so I'll forgive you.You know, Short Fry,if you're trying to protect someone,you should learn when to accept their help.No one gets anywhere in this world alone,not even at your Big Shot Foundation.I said, take the helm!I said, take!Hold on to your socks!Water ahead!Jay, where did you get this chick?
```

### [78] hash=`1543e556c44e51f9`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
I hope you aren't looking for a babysitter.Hey Jay, you say hi to Pioneer for me.Those heels he recommended helped me land a big role.Hey, um, Mr.G, right?It's me, Brian.I've been looking for you.All thanks to you and that badge you got me.They finally gave me a room down at the shelter.They even offered me some dishwashing work tomorrow.No more sleeping in tents or under the overpass.bless you mr.
```

### [79] hash=`9c0880bf5cd3f246`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
G I owe you my life oh come on bro Brian weren't you the onethat helped me get that girl's number you help me I help you that's the dealif it isn't my favorite customer Jay I got the latest edition of motor babeyou interested I swear they're not pirated see you guysIsn't that man calling you?What are you saying?Sorry, this kitten here purrs pretty loud.This thing you have behind your back?Is it not that troublesome?
```

### [80] hash=`4967aed6751d69b2`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Why do you take it with you?Oh, my dad gave it to me.Carried it around for years.Is it?Hold on tight.We're almost there.Here's everything that was in that bell ringer guy's pockets.Think I got everything.Except anything that he was wearing under that getup.But there ain't enough money in the world to get me to wrestle through some shit state called the Sundies.Holic, what was that for?Sorry, kiddo.
```

### [81] hash=`00f9d82f9d555426`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Jay said I gotta knock you on the head any time you cuss.Exactly, Holic.We gotta teach this potty mouth some manners.Especially when there's a lady present.Well, seems I have you to thank, Miss Booneesh.Years of wasted effort trying to cultivate gentlemen out of these CADs, and you manage it in hours!SPFI portable contact device activated.Welcome.Verification success.Registered user, Matilda Bwanish.
```

### [82] hash=`519cdb37c84f4291`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Access level B.It worked!I have a higher- I won't be making the same mistake twice!Emergency support.Apologies, as there have been no abnormal arcane fluctuations detected.The emergency support team is currently occupied.Please provide further details so that we can evaluate the necessity of emergency assistance.Message sent.Support will be arranged in order of priority.I should have applied for an expansion to our team.
```

### [83] hash=`9cc298b45576ee85`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
They will be of no help at allI will have to send my entire team back just to deliver my report to the foundationSo we must count on them to bring support back.Oh, yeah supportYou want to be a part of this french fry you finally taking an interest in all of thisMission the foundation would deal with this without letting naughty civilians like you get involved if you must insist on helping usI suggest you provide what information you know, and then I, Special Investigator Matilda
```

### [84] hash=`591f0ed84e598f2e`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Buhanish, will solve the problem and save the day!Yeah, not going to do that.There isn't one of us here on Hate Street that would stand aside while someone elsesaves us.You want to get a clue about this place?Then the first thing you gotta know is that we deal with our own problems.Irregulations?I would need to file for a special approval?Well, you can have the key, little investigator of Bowen each, since you're so dedicated
```

### [85] hash=`886050f37a5c5aac`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
to your job.Whether you get your special approval or not, we're going to be the ones to take down thosebastards.It's not about vengeance, it's that the people here, they'll never trust someoneto do this for us.We have to do it ourselves.Judges, police, your foundation.Yeah, this will be the key to wherever their hideout is.A place of dark revelry, they've kept it a close secret, but I've seen those that have
```

### [86] hash=`f74de44fc77274c4`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
come back from that place.They're transformed into something unnatural.Their flesh and their spirit, it wasn't their own anymore.Big shot businessmen groveling and sobbing at the feet of their apostle.And the most loving mother I know.She abandoned her kid by a dumpster.Friends we've lost.It's like they're gone.They aren't them anymore.They're possessed.Until one day, they just vanish.Never to be seen again.
```

### [87] hash=`6a69ef8b9c4b72fd`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Open this gate, and flush out their nest of vipers before they can open it oncemore.Otherwise, our mission here and your chance to avenge your friends will fail!Gets even better from there, french fry.That ceremony of theirs is set for the day after tomorrow.They're planning something big.Bigger than anything they've thrown at us before.Yeah, I heard that big guy mumbling stuff like, the last revelation or something.
```

### [88] hash=`d101e65b10118833`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Kinda weird seeing a big dude crying like that.Hahaha!The last revelation?Perhaps then this is the last time Madness plan on opening the door to their LSEM?They will be gone, perhaps for good.Jay, you got a lot of friends there still.What'll you do when they point their knives at you?How do we keep their sacrificial lambs from leaping off the cliff?Not my business to save someone who doesn't want to be saved.
```

### [89] hash=`d3b1e5482d3cea82`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Never even really thought of saving everyone.Not a long while.It's not worth the pain.I cannot disagree this time.Still, we have time to make preparations in advance.Support is on the way, so until then we must stay below their attention.I'm thinking that maybe we may try collecting more information by infiltrating their followers.Perhaps then we will have a better chance to find this gate of theirs.
```

### [90] hash=`a62ffd7cd9f340eb`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Sure, Tilly.Tomorrow I'll show you around the New Age Market.You can meet some of my friends, figure out how to fit in, but maybe a change of outfit first.Who knows who might recognize you?And the Saint Pavlov Foundation is not the most welcome organization around here.Thank you very much, Miss Mercuria.Oh, and I remember you know that Gio, we might collect some further information from him.Gio?I don't know who you mean.
```

### [91] hash=`76ec8ee326aa0634`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
not remember it was just as I arrived you had a visitor and you called himGio I haven't had any visitors all day okay you saw him yes only thing Iremember is some weirdo investigator poking her head into this town bloodmust be shed and our blasphemous eliminated you have proven yourYesterday, two intruders broke the ritual of revelation and stole from us the key tothe gates of Elysium.The precious gift of Elysium granted by the sufferer before their agonizing sacrifice has
```

### [92] hash=`7d86d0d1a0d1ce73`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
been blocked from us.You should have kept the secret of the key.Let me use my green chair to grill this shameful rat.I bet she'll be knocked out, am I right?She ate your hospitality, madam, but I have a very important mission.A shopping mission.So much shopping to do.So, nice to meet you, Miss Cooper.Let go of the poor girl, Cooper.It's time I show her some real treasures.I'm sure they're much more suited to her than your old trash.
```

### [93] hash=`430b627c54102a97`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
Oh, and I ought to tell you, the merchant of eternity says she'll soon come to the New Age Market.And she's bringing her stock of treasures.It's gonna draw in the crowds.Ah, give it up, Marge.There's no way Eternity will like that old junk.Will you two ever just fess up and admit you're friends?Fine, fine, Mercuria.You don't have to poke fun.Just let us know how we can help you.A door.We're looking for a door or a gate.
```

### [94] hash=`d73867785ba11996`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p65`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 6~14）

```text
The one you mentioned before.A door?Sorry, I need time to recall it.Hey, why don't you show Ms.Bonish around and I'll stay here to gather my memories.I'm not going anywhere.I'm still trying to rack my brain and this old thing can only manage one thing at a time.Is this your luggage?You're packing up?Yeah.We're leaving this place.Before the wackos hold their ceremony if we're lucky.When we came here, it was to find some safe place away from these people and their conflicts.
```

