# 剧情图谱抽取 · batch 089

- 角色：`wu_ming_zhe`
- 批次：**89** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.0」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_089.jsonl`

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

### [0] hash=`a621854e212dcd90`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Geo, forced to live with this darkness inside you.I'm sorry if I scared you, but I'm only here to return this.You're a boy trembling inside this brawny shell of a man.You're too far down a path that you never wanted to set foot on.Mr.Geo, if you need help, find me in the New Age Market.
```

### [1] hash=`446f5505ce1e68e8`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
I don't want to write this letter, but I promised myself that once we could talk as equals,I would persuade you to accept my decision.Sure is dusty in here.I gotta clean up.I thought I would have the courage to confront you then.I thought I could tell you how foolish and selfish you were.I thought I could make you proud of me by going to places you've never been and seeing what you've never seen.But now, when faced with a mission that could put my life at risk, I realize that I'm not
```

### [2] hash=`6a10b5dfbbdd3e56`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
as brave as I thought.My hands are trembling.My body wants to run.I don't want to lose everything I have.I don't want to die, nameless.Especially now that I'm so close to the light I've always wanted.When did you get this hole?Oh.Sorry, buddy.I shouldn't have kicked you.I keep thinking about what I told you that day.About how some people would sacrifice themselves if they had to.I remembered the scared look on your face when you heard that.
```

### [3] hash=`831200d35810dfa0`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
I was so proud of myself at the time.I thought, finally, I managed to scare him, but now I wish I could go back and stopmyself.I know that scaring you is nothing to be proud of.I only did it because I knew I was the only one in the world who could hurt you.And now that I've established myself, I can talk to you as an equal.But I found myself doubting my decision, and my colleague knocked on my door, urging
```

### [4] hash=`3762911928dfd9cc`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
me to prepare for our field mission, and he called out my name, Paulina, Paulina!How I wished he were you, how I wished for you to open that door and protect me.That thought only lasted for a moment.Then I understood where my fear came from, and why you were so scared when I talkedabout sacrifice.I realized that even though countless people are suffering out there, even though my colleaguessacrificed their lives.
```

### [5] hash=`49a064005e9d8820`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
Even though more and more children have become homeless,I'm not as brave as I want to be.All fixed, finally.You're looking much better now, buddy.Mr.J, are you really selling the restaurant?Don't worry about it.A new, even better guywill take over.But I also understand that someone has to step forward and stop this tragedy.Otherwise, our world will fall apart, leaving nothing but sadness and pain.
```

### [6] hash=`6e6628af88360718`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
A single drop of water can't form an ocean.A single piece of tile can't build a roof, nor can a single person put an end to awar.For a long time, humans and arcanists have been on opposite ends of the spectrum.Faced with this catastrophic event, we may all perish unless we stick together.But in the grand scheme of things, I'm just a blip on the radar.Yes, I'm just a weak, cowardly human.But I'm also a member of the Saint Pavlov Foundation.
```

### [7] hash=`07dc114082c538aa`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p20`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（20信鸽）

```text
I can finally, truly say those words with conviction.Some people are willing to deal with pain, even willing to sacrifice themselves if theyhave to.This is a good spot.piece by piece we'll build a shelter and one day the rain will stop we can'tsave those we've lost but I believe that one day we'll reach a new era weshould go Jay
```

### [8] hash=`6ab0385187560f70`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
Boss, what's in it for you to join the Foundation?You know they're all liars!Those holier-than-thou officials never tell us what's really going on.Besides, if Les Gers is taking over the restaurant...Hey, watch your mouth, kid!Your boss would have been hacked to pieces if it weren't for us.Wipe your nose, kid.Les Gers will be a good boss.Promise.They'll clean up the mess on Haight Street, and after that, the Poorhouse staff will get you into school.
```

### [9] hash=`0c87468a7bb4e6f2`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
and holic spike it's yours now so what are you gonna do now me I'm gonna jumpinto the sea and try to swim what do you mean boss I thought you didn't know toswim shut up you noisy bastards I'm trying to sleep here you shut up yesno one can cause a friggin earthquake shut up make any more noise and IBut despite her courage, she's still a living person who can get hurt.Please, promise me you'll bring her back.
```

### [10] hash=`acdc0e53202b570e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
It's a shame we couldn't arrest that girl.If only we'd had a little more time to prepare.You're a man.You saved my life, didn't you?I'll get you pretty far on Haight Street.By the way, where's Matilda?She's supposed to take me to the Foundation today.She's been summoned to report on the operation.I guess.It's gonna be rough.There were a lot of civilians involved, and she didn't follow her commands.
```

### [11] hash=`243470b450583013`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
She might even have her position revoked.What?But we wouldn't have gotten anywhere without her.Jerry, that's how things work over there.If you're really planning on joining them, you'll have to learn to follow their rules.Where's she now?We're not authorized to request that information.What's wrong with my nose?This isn't even allergy season yet!Miss Bowenish, are you alright?Continue.I read your report last night.
```

### [12] hash=`9046c59d15958499`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
I must say that your judgement has given us some very important information.According to your report, the missing assets are in the possession of Eternity, aside from the most important one which is now in the hands of Manus Findictae.Luckily, the man in control of the girl is one of their insignificant believers.For the time being, there's a limit to what he can do with her.This, at least, is good news.
```

### [13] hash=`a5c9f21fc5000f0c`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
You've caused quite a stir among senior management, Ms.Boenisch.It seems you're starting to make a name for yourself.By the way, I would like to apply to leave the Foundation during my vacation.I want to visit my mother in her safety house.That merchant, Eternity, and the peddlers in that lair mentioned her name several times.I deemed it necessary to confirm her safety.No problem.Give me the application form.
```

### [14] hash=`d53094d763ea98c6`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p21`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（21旱鸭子）

```text
I'll arrange it for you.Oh, wait.Someone told me to give this to you.He said you left it in San Francisco.Odd.I don't remember leaving anything.He said that it's proof of your promotion.Shall we?B!Let's go where you want to go.
```

### [15] hash=`786296845ae7a158`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p22`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（22门前足音）

```text
When it was complete, they were ecstatic.They kissed the earth in their jubilation.Yet in the end, they found nothing.I'm not sure what you're talking about.Never mind.I know what you're going to say.The preacher has ordered us to return.She has received a new oracle.Let's go.From nowhere!Damn it!My baby's gonna be stuck here forever!And all for a bit of cash!AAAAAAAAFair distance from the safety house.
```

### [16] hash=`4500eae589a01cfa`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p22`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（22门前足音）

```text
Tilda must count us again!Wait, Miss!Hate me!And here's a tip too.I hope it can make up for your loss.To some extent,Dinguished and generous passengers such as memust be a rarity.I will walk the rest of the way.If you stay here and wait for me,I will show you my generosity again when I return.Sure, Miss!The location of the house of securityclassified.I must be very careful.Okay, now I won't leave any
```

### [17] hash=`062978067a7c724e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p22`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（22门前足音）

```text
footprints behind me.If only I had an assistant with me, then I wouldn't haveto carry this suitcase alone.It would be even better if it washonest.Mom would be happy to meet her.I don't feel theincantation of mom at all.I guess it makes sense.The staff of theI hope she's doing well.And there you have it!Manu's fans would never be able to find her.She's one of the best guessers,the healer of...She must have foreseen all the possible circumstances
```

### [18] hash=`aa7a84abeaebd79a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p22`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（22门前足音）

```text
and prepared herself.And she will certainly be surprisedto see that she's visiting her own daughter.The SPDM canteendoesn't know anything about French cuisine.I can't wait to eat a newMom's dish!The most important thing is that IAsk my mom to choose a new orbicular for me.The best crystal craftsman couldn't do anything to fix the cracks in mine.Tamboanie, I came to see who is the-
```

### [19] hash=`c3c8396415e705c2`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
So, as I take off the tire, I notice the gal.Some rich lady from the market's got a crazy look of worry on her face.So I tell her, break my jaw if I'm telling a lie.We're good folks here.Don't believe me?Just ask around about Jay and his friends on Hate Street.Please, take care, Mr.Holick.You have been drinking way too much.Ha ha ha!Come on, Hollick.You don't got the balls.I saw this guy get a nosebleed yesterday, and he cried like a little baby.
```

### [20] hash=`cdba38f16c00ab16`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
Back me up, Jay.Hey, Jay?What?Did they bust your head or something?You're off daydreaming or we're talking about some rich bimbo.Sorry, Mr.Beckett.I believe Jay's present concerns may be revolving around, you know, Le Gere's the Dead.Nah, way off stuff shirt.Take a look.Bombshell News.Uncovered video shows F.A.E.used as new execution method.Hmm.What will the minds of those Hollywood producers think of next?
```

### [21] hash=`d95a0204e8950463`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
Oh, I think I've seen images from this video.From spam mail and newspapers.We're still trying to identify this woman to confirm the authenticity of the video.If you have any information, please call us at 429-7234-X7.Up next, homebound or hoodwinked, the mystery of the so-called long-lost son.We turn to the story of Sergeant Howard Eden, a retired Army veteran and the stranger claimingto be his long-lost son.
```

### [22] hash=`ebccd987744a467d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
But, is this a heartwarming reunion, or a sinister story of senior exploitation?Let's...Awww.Bad.You know, it's good fun watching all her nonsense and sensationalism.Hey, show some respect.Sure, that whole how woodchucks could control the world peace she did was a little iffy,but who knows what those woodchucks could chuck at us.Alright, that Ledger's thing is really bothering me, okay?What's his story?
```

### [23] hash=`fc77c057585034bc`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
I've heard it, not gonna lie, kinda sick.Cops hate him, but the street punks love him.They say, back in Hunters Point, a bunch of guys was swatering him, had him tied uplike a pig, and when they got tired, they put a gun in his mouth and made him eatit.The bullet went straight through his throat out the back of his headBut when the cops came they found nothing, but a few bloody teeth.He was goneHmm scary, right?
```

### [24] hash=`cfb0a999b90e82ec`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
But here's the thing.YeahLegers is a pure humanSo what happened?Where did he go?Mr.Halleck, I think you've been watching too many of those horrible Romero moviesPeople returning from the dead, that's pokey cinema, not reality.I can only assume this legers the dead and made up this rumor himself.Perhaps so he might attract more powerful arcanists to his side.Potion addicts, smugglers, card sharks, getting them all under his thumb until he
```

### [25] hash=`91bd14f6cedb3e96`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
can gobble up the whole of San Francisco.And yeah, it's been working, but not anymore.Cuz we ain't gonna sit and watchAfraid you're overestimating our strength mrHalleck their enterprise is much more dangerous than all our previous rivalsNo less so if they're aiming on partnering up with the lunatics in the new age marketGotta agree with that assessment pioneer.It's been days since my last session with a paying customer
```

### [26] hash=`6079fa4336213939`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
seems like everyone is joining up with them and their energy isdisturbing to say the least they've been poking around my shop looking for somerare sort of books and materials kinds I never even heard of before I wouldadvise avoiding direct confrontation Jay I hear you avoid confrontation that'sthe right move for sure but it's not gonna be possible they aren't giving usa choice the cops abandoned Haight Street a long time ago ain't nobody
```

### [27] hash=`e4497f400cbb9223`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
that cares about these streets but us now.Remember?That was when all thoseartist trailers were burned down.After that the rest of the diviners and suchwere ran off quick.It's only those loonies that have stuck around,misguiding our canists making everything worse.We were smart.We would haveleft then and there, closed up shop, took the first bus out of the city, ranfor her miserable pathetic lives.
```

### [28] hash=`3abe793c4fe1c994`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
But then, we ain't that kind of smart, areinvolved in this you have to admit that they care about our canists despite alltheir bureaucracy turning to the foundation would not be a bad choice forus Jay yes mr.J I think mr.pioneer might be right I don't want to lose myjob because of these bandits I'll be glad to bring you to the foundationyour assistance would be more than welcomeMiss Disco Ball, it couldn't possibly hurt to reach out to Paulina.
```

### [29] hash=`16d964c92adec695`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
Maybe she could help us with the red tape.She's your sister after all.No, no, no.I'm only going to say this once and it's for real.This is our own business, nobody else's, and especially not hers.Paulina made her choice.She could have talked with me.She could have approached us if that's what she wanted.She had the chance.She's had years.Not a word.She has her own life.And she madeit out of these streets.
```

### [30] hash=`1b96dc0a12980fb6`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
She ain't coming back.She ain't even looking back.She'snot that little girl tagging around us anymore.She's got fancy marble floorsnow.Cut all that decency and good taste that she never had here.Shedoesn't need us.She's not that little girl tagging around us anymore.She'sfancy marble floors now.Got all that decency and good taste that she never had here.She doesn'tneed us.You think I'm gonna scrape down on my knees for her?
```

### [31] hash=`b8322ade6df98144`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
I'd rather stick my foot in hotslag.At least that way I'd have one leg to stand on.Jay, please just give it some thought.This may be the only way for all of us to survive this.Ugh, I need a drink.Somethingjust hit me and my shoot run mr.J all the money in the bar is um how is ityou're saying gone cat catch that kid the puppy wishes to come along boss thiskid's like a rat he's scurrying in between those boxes we can't catch him
```

### [32] hash=`07b3ad2baed50c18`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
looks like we do this the hard way J don't blame us for breaking nothingCome out, you little rat!I got my eyes on you!Haven't you eaten?Knew it.Cat Eye Weizen.Owner of the most infamous sticky fingers from here to the market and back.Little dude, I know you're dattering off with those guys from the Order of Enlightenment.But why didn't you go to the shelter?You trying to get yourself hurt out here?
```

### [33] hash=`e013d2f492d7f9aa`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
Let me go, you big jerk!Sooner or later, someone is going to teach you a lesson or two.Don't think that arcaneist mom of yours wants you using your cat eye to steal things.I know things seem tough right now kid, but acting like the world owes you something, it'sgonna bring you nothing but trouble.When I got my finger chewed up by that machine, I lost everything.I could have went around sticking up places.
```

### [34] hash=`9af921c0950aac73`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
I didn't.Think you got it worse than me?Hey, we gonna let him go just like that?Your friends are waiting out there.But, Mr.J?It's fine, Spotnick.Let him go.These kids lost their homes to the New Age market.Their parents deserted them.They've got nowhere to go.Beckett, look at them.You can't compare.It doesn't work like that.Each suffering has its own energy.Hey kid, you and your friends looking for some almost honest cash?
```

### [35] hash=`db73fc230ba39ef3`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p2`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（02娱乐不至死）

```text
You mean...Thanks, Jay.I got sharp eyes.I can do lots of stuff.Counting coins, cars, finding water drops.I'm great at spotting cheats and shady dealers.Easy, kid.Dill your belly first.Ms.Sputnik, please get these kids some burritos.Dang kid, those arms are like chopsticks.Hey, Ms.Sputnik, let's make those extra meat.Alright, man.Consider my second thought thought over.But get this straight, if I see her fold her arms and give me any of that snooty attitude,

we're gone.Out the door, no discussion.
```

### [36] hash=`e651a2906b5470a7`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
Those men in white sets, there won't be any more bad people around the school, only we'll be hungry, like before, like with mom and dad.They'll give us candy, and soup, and real meat every week, and a big comfy house.Cover up a little more, Polly.You're gonna catch a cold.You can't trust anything adults tell you like that.If they give us candy, or soup, or even meat, it's because they want something from you.
```

### [37] hash=`58089b7b8c6b4070`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
Nothing you get in this world is just given away.Least of all from people like them, but they did give me a fun jobSee now I can make store doors and sell them for moneyThat's cuz they need you our little Paulina is one of the most cleverest kids in all of hate StreetSo I'll say bad guysBad on it only good adult.I ever met is mr.TangOkay, but you but if they're not lying you don't have to wash dishes or take off tires or any of that stuff
```

### [38] hash=`826b27700ca22566`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
Two thousand beers for guests!Get the move out!Don't overthink it, okay kiddo?I'm right here with you.Always will be.Okay, but if you do leave, you have to tell me first.Cause we'll always stick together.Deal?Deal!Sleep tight, Polly.This place is ritzed up like a palace.Who do they think they are?Who needs a floor that shines like a mirror?What, they hire a dog to lick it clean every day?Just what this place needs!
```

### [39] hash=`a64f4a77978541a0`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
Another stupid oaf that does not know how to watch where he is going!Hey, mind your manners, short stuff.Excuse me?Shorts?I apologize for my frankness.He ought to mind his own manners.Daring you to look as though you have just wandered in like, how do you say, lost puppies?I'll let it go, just this once.Are you here to register as Arcanus?Sorry, we're just in the middle of a shift change.Please wait a moment.
```

### [40] hash=`a3104f874e0d186d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
Isn't it Fiona's shift?She should be able to handle this on her own.There is work to be done, people!Quickly, vite, vite!Got it.Welcome to St.Pavlov Foundation Reception Center.How can I help you?Hello.We're here to visit a member of your staff for, um, some private matters.If possible, we'd like to have a conversation with her in person.Now that we have some spare manpower to chase after them, I heard that Team Razor has started searching for the Foundation's lost assets.
```

### [41] hash=`a244fa44b9aa00ec`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
After all this time, we're finally back on the trail.I don't know, man.Good as it seems to be, I'm worried the news is getting out of control.Now rumors are spreading everywhere.It could get dangerous.Otherwise, why would we have been assigned here with Mr.Bernard to get to the bottom of this?Zip it.What, you guys having a party or something?Never seen an office so...smiley.Feels like a sales day at the mall.
```

### [42] hash=`ad937888ce53f09d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
All those eager girls and boys running past the window.A mood like this usually comes with good news.Please don't pay them any mind.They're just chit chatting.Doesn't really mean anything.It might mislead you even.Come in please.Despite all the smiles, it hasn't been easy for us recently.Our time and resources have been stretched thin.We've suffered a lot of losses.It still feels a little unreal that we're still standing.
```

### [43] hash=`13867e795794571e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
A lot of good people sacrificed everything they had to get us where we are.Excuse me?I suppose that's also just idle chit chat.Maybe I don't know any more than they do.I only just wanted to say, since you're family, that Ms.Paulina was one of thean asset to everyone here at the Foundation.This is where the remains of all those that died in the service of the St.Pavlov Foundation are kept in memorial.
```

### [44] hash=`6345d0a191e1e8df`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
I'm so sorry that I have to be the one to tell you, but Halina is here too.You better know what you're saying, Miss.I'm sorry, Fiona dear.Would you mind giving us a moment of privacy?I'll be waiting outside.J, are you going to be alright?To me, J, is there anything I can do for you?Maybe we can take a look, just to be sure.No, don't, don't do anything.But don't you fucking do a damn thing.How can all that someone is, was, be in a box like this?
```

### [45] hash=`4ef657954a4b0de9`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
It's so small.This is some kind of sick joke.I knew then she'd never look back.This was stupid.Never should've let you talk me into coming here.I know that sometimesbrothers and sisters don't get along.But I thought that only meant little fights,squirrels over toys.This is something much worse.We're leaving.Now.I can't stand the idea that she's justlooking at me through a monitor, maybe even laughing.
```

### [46] hash=`14fcfc7824f29bd9`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
That herpathetic loser brother.get me out of here before I turn this place upside down I apologize I'm surethis loss must feel hmm such heart-wrenching news I'm crying my eyesout oh there's nothing we can do now sorry for bothering you we'll be onour way out now let's go Jay please wait gentlemen you need to fill theThey're usually within the foundationThen I could ask my superiors.Maybe they'd let you take these home here.
```

### [47] hash=`137e72d0a589dd5c`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p3`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（03小匣子）

```text
I'll just need your name and addressWhat that's just sick miss you're really asking me to sign some papers for what?So you can hand me off some old junk and pretend this never happenedYou think that's enough to get me to stop asking questions.Where is she?Not this bullshit Fiona, can you tell me what happened here?
```

### [48] hash=`974211c9d7c53941`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Mais je ne comprends pas !Quoi est-ce que l'éditeur du OCU irait visiter un endroit cité Sodeley ?Qu'est-ce que ça pourrait dire sur URD ?D'accord, au moins je peux passer voir maman.Ça serait certainement une surprise !Ce que leur Mathilda a accompli va rendre toute la famille fière !Ma Mathilda, enquêterie spéciale pour la Fondation Saint-Pavlov !Maintenant, la petite Mathilda ajoute une autre étoile à la lignée de la famille Boinich !
```

### [49] hash=`9523bd75c9b956d2`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Heu, heu, heu, heu !ou l'ont oublié, et les deux arcanes qu'elle a reçues auparavant s'éloignent d'elle près du hall de l'hôpital.Ils n'ont même pas encore rempli les formes propres.C'est pas bon, ça pourrait vraiment représenter une démonstration de l'intelligence sérieuse !Et Mr.Bernard demande que nous fassions l'avenir de la narrative, avant qu'elle arrive à la presse,selon la vitesse de la nouvelle épreuve dans ce jour et l'âge.
```

### [50] hash=`1190da5b07e7db95`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Les nouvelles ordres sont pour que nous trouvions ces deux visiteurs,et pour éviter que l'information ne se fasse plus.Bien sûr !Donc, notre tâche de traiter les éditeurs de O2 sera réassigné à d'autres équipes ?C'est correct, Mme.Traiter ces deux Arcanistes a été donné de la priorité.Et ces deux étaient les mêmes qu'il y a eu avant aujourd'hui.Mes amis, après la conversion harmonique,nous avons découvert le faillir de la prophétie et de l'eschatologie
```

### [51] hash=`9839b7b7a1c8c759`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
et les nouvelles possibilités de co-existence entre la foi en Pneuma et la science.Ils croient qu'il y a un Dieu.Et Dieu est mort.Mais est-ce que c'est le cas, amis?C'est l'heure d'abandonner les disputes des religionset de savoir que nous sommes un.Dieu est toi.Dieu, c'est moi!C'est l'information que nos visiteurs qui s'escapentsont en train de s'enfuir avec un healer d'énergieappelé Mercuria.Ici, j'aurais préféré ne pas attraper l'attention à nous-mêmes.
```

### [52] hash=`14da1eb82360bb4e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Alors, mettez vos cheveux en bas!Quelque chose d'un tent temporaire,et un signe en bas.Quelque chose n'est pas bon.Je ne ressens presque aucune fluctuation arcane ici.Est-ce que ça pourrait être une trappe?Ce marché est rempli d'arcanistes inregistrés.Pas à mentionner les touristes humains.Il y a sûrement des gens dangereux entre eux.Je ne devrais pas y arriver.Ils vont me placer et me tuer à des oiseaux.
```

### [53] hash=`b8e5cdbf5f1dc260`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Les oiseaux mangent tout.Tous les os, votre tête.Pas un hair left.C'est comme ça qu'ils traitent les traiteurs.Les Pops ne m'aident pas.Il ne m'aidera pas.Non.Mais ici vous êtes, Mr.Geo.Enchirant comme une nouvelle bouche, parce que tu es prêt à une réponse.L'answer à toi-même.Tu as apporté une odeur étrange avec toi.Et une énergie fauteuse.Comme celle d'une personne gravement malade.As-tu été à un hôpital ?
```

### [54] hash=`37c32f975ce75ce7`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Non !Juste à suivre les lèches !Aujourd'hui, les vies que nous avons sont les vies de ceux qui sont mortes.Pas beaucoup entre eux.On ne tient pas à des attaques ou à des sables d'oeufs.Attends, arrête ça.Avant de commencer, je ne achète pas n'importe quel d'un de vos cendres.Je suis juste là pour une réponse.Comment sais-tu que le feu m'a pris ma famille ?Comment ?Es-tu quelque sorte de psychique ?
```

### [55] hash=`aba293304946b678`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Ou un profiteur ?Dis-moi !Non, je ne devrais pas venir ici.Unless, maybe, I'd chop off your pretty little head and give it to you!That'd be my excuse!What have you got?What do you see in your hand?Is it a knife from my throat?Or a diamond-covered key?Shut up!Stop babbling!You're just a witch who survived her burning!A liar!Breathe, slow and true.Look at it again.This is a dagger forged in your own dark flame.
```

### [56] hash=`06e4abf99adcdf00`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Everything has a shell of meaning.But hold your gaze on it and it all strips away.Until those words become strokes of black and that dagger becomes a cold sheet of metal.Is a cage.Cast off its shackles and nature reveals itself to us.Don't be afraid.Prends ce sentiment.Maintenant, ferme tes yeux avec moi.Veux-tu le voir ?Une porte entourée par la douleur.Oui.La porte s'éteint.Comme si quelque chose était derrière.
```

### [57] hash=`b3fbb0e9359d0d61`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p4`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（04新客人）

```text
Non, c'est...C'est affreux.Ne t'essayes pas de l'imaginer.Prends l'épaule.Juste raconte-moi par l'impression.Où est-elle ?Qui sont les autres ?Je ne sais pas, je ne sais pas !Leurs yeux sont couvés par...Les mains !Non, pas les mains !Ce sont des masques en forme de mains !Hey, qui est cette fille ?N'est-ce pas que ta maman vous a appris à ne pas espionner sur les gens ?Mlle Boniche !Merde, tu es la fille de la fondation !

C'est pas juste ma chance !
```

### [58] hash=`b383a85506eb7999`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
You're a normalist, but you must have lots of candy.Mr.Brown, we have need of your cooperation.We do not want to hurt you or your friends.But should you continue to resist,we'll be forced to take necessary action.Unbelievable!So rude!Even as an arcanist,all he does is this vulgar hand-to-hand comedy.That long-sticky charisma certainly isn't a toy.Ahem.If you would be willing to come quietly and play nice,
```

### [59] hash=`97147ef92383e52f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
I will consider lowering your risk rating in our report.I gotta say, sometimes I wish I could take a knee and surrender.But, sadly, even after all those hard knock lessons,I never learned once how to raise the white flag.Put it down, Jay.Your fight is over.This...this is the smoke of burning Mandrake.Cover your nose and your mouth.Miss Wanish, hold your breath.Stay away from the...He knows that kidnapping a Foundation investigator and interfering with an official investigation is a serious crime.
```

### [60] hash=`9615890f9c4b8bb7`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
Especially when you've kidnapped the one and only Matizah Bwanish, a pivotal figure in the Saint Pavlov Foundation we're talking about.Pivotal, eh?Huh.A whiny little pup happens to stay standing from a little smoke.Yeah, I don't see anything worth being proud of.Tell me, did Paulina send you to ask us to sign this bogus confidentiality agreement?Let me guess, she's probably still hiding in the Foundation office, right?
```

### [61] hash=`d8733c73e2f9ed55`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
Too scared to see your own flesh and blood?Talking about hiding in our office, we're here to bring you and that mannequin backto the Foundation.This is a serious violation of the visitors' advisory.Jay, I think we should ask this another way.Actually, you shouldn't have found out about any of this in the first place.Maybe I'm not familiar with your Polina, but I do know that there was a woman at Saint
```

### [62] hash=`01b973d323aca473`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
Pavlov's named Polina Lesage, and I know that she died.As far as the claims of different photos, mementos, it's complicated, and there isa little I can say freely, but headquarters is working on it and many other similarcases.I don't have the kind of clearance to know what's really going on, and even if I did,I couldn't tell you, for everyone's safety.Huh.So our little prize investigator's also in the dark.
```

### [63] hash=`ee4e73af8f8eb6bc`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
Maybe we can just go ahead and jot all these questions down and send them backto the Foundation.Or maybe we set up shop here!Just let any old passerby take a good look at them!Prove this Polina of yours is in fact deceased with us to the proper paperwork, yes?Then we can be getting out of your hair for good.The burden of proof lies with you, special investigator.Alright, but I will hold you to your word, mannequin.
```

### [64] hash=`e424e49677dfb44e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
Before we begin, I should say I don't do this lightly.But if you need to know, don't say I didn't warn you.I am a diviner, one that uses crystals.I suspect that sort of practice may already be familiar to you.I'll need an object that symbolizes Miss Le Sa...Polina.Or something related to her.It must have a deep connection to her.Something she once owned or often used.I will then begin my scrying using this object to the fog in my crystal orb
```

### [65] hash=`64f9c74f3053e814`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
and reveal to us her current...existence.But if we find nothing beneath the fog...I am quite sure you understand what this means.And then, I will be needing you to return with me.And as I have heard that energy healers are able to detect the flow of nema, the madamhere will be able to prove the authenticity of my divination, no?I'll see it.Yeah.Look, I saw the arcane energy flowing from your little friend's hand to their wand
```

### [66] hash=`ba108f6a47890aa1`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
just now.Jay, what do you think about this?My sister's little minion back at the Foundation already exposed the lie.Still, seems only fair I get to spy on her back.We'll see who's laughing now, sis.Alright Frenchie, this is hers.Take it.Then let us commence.Finds all.Show me the trace of the one to whom this belongs.I bid you to respond.Lift the fog, reveal what existence lies hidden from us, give us your vision, sight beyond
```

### [67] hash=`0d27503d7d91b77b`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p5`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（05审讯节目）

```text
sight!What?All that and you just stop?This thing busted or something?Nothing happened.Jay, the divination is over, the energy is gone, just like she said.You come all this way for what, just another foundation trick?So, what is it this time?Did you mess around with the orb?Some kind of protection skill?I don't have time for these games.Jay!It means she's really gone.Sorry, Jay.Are you still with us?

Yeah, I'm fine.So I guess it's legit.
```

### [68] hash=`7d319802effaeade`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
I feel like a bastard!How is it that I still need to learn not to trust anything that comes out of that...That stupid lying jerk's mouth!Mail today, sis.Nah, no visitors yet, Polly.Haven't heard a word.Another pack of lies.And I bought them!Hey Polly, open the door!What are you even doing in there?Lone Joe!Who the hell do you think you are to decide my choice?My future, my fate!Don't talk to me.Don't ever talk to me again.
```

### [69] hash=`3a2f854749939005`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
I'm leaving today.Whatever!Why are you even this obsessed with this mission of theirs?They're fooling you, sis.Don't you see it?Only two kinds of people that buy the Peace Be With Us kind of bullshit they're selling.The first kinds are those like you, Polly.Stupid kids that don't know nothing about anything except what they've read in books.And the others are the ones fleecing you, taking all you got and spitting you out,
```

### [70] hash=`685fb553481b5d2d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
all so they can have more money, more control.Paul, I'm sorry, alright?I flew off the handle.I made a mistake.But these guys, Paulina, do you think they care about you?About anyone?You're just another penny in their pocket, a coal for their furnace.They'll burn you up and replace you, easy as that.You think you're going out there, do something big, because you don't even know what lifeis yet.You just read about it in your books, telling you some shit about a foundation member paying
```

### [71] hash=`0facff5558dade3b`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
the ultimate sacrifice for others.I think that makes them some kind of hero.You don't know what that kind of sacrifice means, sis.Do they say how those brave foundation goons really felt facing death?They aren't going to tell you they were afraid, that they hated everyone who put them there,that they probably shit themselves before they bit it just wishing they could go home.They don't put that in books, do they?
```

### [72] hash=`0af1f55a778af54e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
You read what they want you to think.It ain't the truth, Polly.Maybe I'm not smart like you, sis.I can't read the things you read, can't learn like you.Why learn the hard way?Clap about what you learned on the street.Don't want to hear itI'd rather take my chances and die out there than stay here and never live at allShe was on this othercommandeerBarter de mauvaise nouvelleMe oh my mother no, he's so proud co-operate.
```

### [73] hash=`33376271e4210f82`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
NoSeleman, is he not so so pass on co-reveilleBut I think that with this news, the special investigator, Matilda Boanich, will be the one who will find the key.I am very sure that my ability of exemplary analysis will be rewarded by our leaders.Oh, maybe they will even place Mademoiselle Sonnetto in my team.Mind yourself, please!I've had quite enough of these bumping accidents today!The Enlightenment!
```

### [74] hash=`7cfd3d55b2e6a6e9`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
Soon comes the sufferer's Enlightenment!Enlightenment!It's the Enlightenment!Yeah, yeah, chant louder, you stupid jerks.The higher you lift those arms, the easier it is to reach into those pockets.Not very convenient, but I suppose that morality is far from being the most important thing now.Shoulder to shoulder as we anticipate our coming celebration of the suffererWe awaitWe rejoiceWe await we rejoice
```

### [75] hash=`f576c3785b43377c`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
The sufferer has heard us know this children now take heart for we have another lost lambWho has cast aside the world to join us?All.It is time.Follow the bell ringer.The gate to Elysium shall soon be opened.I must return to inform the Foundation.I must leave now.Move!No, it can't be.Where is the key to the gate?Apostle Matthews, please wait a moment.Be vigilant, all.There are deceivers among us.Behold!
```

### [76] hash=`91b4cbe01e57affa`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
The deceivers among us!Dang it, dang it, dang it.Where did you come from?Didn't anybody tell you whose turf this is?We are in so much trouble.They'll catch you!Damn it, they get to see us again!Son of a gun, kid!What did I tell you about making a mess?These freaks are mad!Sit back.We're ever sitting in the road.Ha ha ha ha!So long, suckers.What brings you out here, short stuff?Starting to wonder why we keep running into each other.
```

### [77] hash=`2d65d111165e35e8`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
You've got a funny way of saying thanks French fry.If I listen to you back there, you'd have been stuck here and hung out to drive.I need your help.I can take care of these kooky cultists all by myself.As you wish, m'lady.It's the glauakis!Glauakis?No, they don't have such an acute sense of smell.It must be a kind of mutant they tamed.Night and shining chrome at your service.Say the word.Now after, you must set up a foundation, and it is my duty to protect civilians!
```

### [78] hash=`b490b1248cce303d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p6`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（06乐园在即）

```text
Get on, Frenchy.Really didn't want to get involved, but you were starting to look like a lost puppy, so I'll forgive you.You know, Short Fry, if you're trying to protect someone, you should learn when to accept their help.No one gets anywhere in this world alone, not even at your Big Shot Foundation.I said, take the helm!I said, take...Hold on to your socks!Water ahead!
```

### [79] hash=`d34d0e1961abe86d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
Jay!Where did you get this chick?I hope you aren't looking for a babysitter.Hey Jay!You say hi to Pioneer for me.Those heels he recommended helped me land a big role.Hey, um, Mr.G, right?It's me, Brian.I've been looking for you.All thanks to you and that badge you got me.They finally gave me a room down at the shelter.They even offered me some dishwashing work tomorrow.No more sleeping in tents or under
```

### [80] hash=`dbd153acac086b3a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
the overpass.Bless you Mr.G.I owe you my life.Oh come on, Bruh, Bruh, Bruh, Bruh,Brian.Weren't you the one that helped me get that girl's number?You help me, I helpyou.That's the deal.If it isn't my favorite customer Jay, I got the latest edition ofMotor Babe.You interested?I swear they're not pirated.See ya guys.Talking to youEmergency support.Apologies, as there have been no abnormal arcane fluctuations detected.
```

### [81] hash=`c336363db6fecfb3`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
The emergency support team is currently occupied.Please provide further details so that we can evaluate the necessity of emergency assistance.Message sent.Support will be arranged in order of priority.You know I should have applied for an expansion to our team?and then I, Special Investigator Matilda Bowenich,will solve the problem and save the day.Yeah, not going to do that.There isn't one of us here on Haight Street
```

### [82] hash=`91b60961aca6e142`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
that would stand aside while someone else saves us.You want to get a clue about this place?Then the first thing you gotta knowis that we deal with our own problems.Irregulations?I would need to file for a special approval?Well, you can have the key,little investigator Bowen Ich, since you're so dedicated to your job.Whether you get your special approval or not, we're going to be the ones to take down those
```

### [83] hash=`205817512c56ebac`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
bastards.It's not about vengeance, it's that the people here, they'll never trust someone to dothis for us.We have to do it ourselves.Judges, police, your foundation, one rat's nestafter another, promised to bring us change, and then left us to the wolves.Nah.Worsethan rats.At least they know how life here really works.At least they see us.At leastrats don't claim to be our saviors.We can only trust someone who's been through the
```

### [84] hash=`ff2858a316bc6000`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
trenches with us.Thank you, Jay.This must be the key to Mendes' Elysium.Mercuria, would you?Yeah.This will be the key to wherever their hideout is.A place of dark revelry.They've kept it a close secret.But I've seen those that have come back from that place.They're transformed into something unnatural.Their flesh and their spirit.It wasn't their own anymore.Big shot businessmen groveling and sobbing at the feet of their apostle.
```

### [85] hash=`396c7f74eb925b3a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
And the most loving mother I know, she abandoned her kid by a dumpster, the friends we'velost.It's like they're gone, they aren't them anymore, they're possessed.Until one day, they just vanish, never to be seen again.So, we must find this gate and flush out their nest of vipers before they can openit once more.Otherwise, our mission here and your chance to avenge your friends will fail!Gets even better from there, french fry.
```

### [86] hash=`39ae518316a1618b`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
That ceremony of theirs is set for the day after tomorrow.They're planning something big.Bigger than anything they've thrown at us before.Yeah, I heard that big guy mumbling stuff like, the last revelation or something.Kinda weird seeing a big dude crying like that.Hahaha!The last revelation?Perhaps then this is the last time Manusplan on opening the door to their Elysium?Then they will be gone.Perhaps for good.
```

### [87] hash=`21df5df41f682950`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
Jay, you got a lot of friends there still.What'll you do when they point their knives at you?How do we keep their sacrificial lambs from leaping off the cliff?Not my business to save someone who doesn't want to be saved.never even really thought of saving everyone not a long while it's not worththe pain I see you fortunately I cannot disagree this time still we have time tomake preparations in advance support is on the way so until then we must stay
```

### [88] hash=`dabf162e3e73538e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
below their attention I'm thinking that maybe we may try collecting moreinformation by infiltrating the followers perhaps then we will have aSure, Tildy.Tomorrow I'll show you around the New Age Market.You can meet some of my friends, figure out how to fit in, but maybe a change of outfit first.Who knows who might recognize you?And the Saint Pavlov Foundation is not the most welcome organization around here.
```

### [89] hash=`27d07d03d1841bd3`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p7`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（07好哥们，好主顾）

```text
Thank you very much, Miss Mercuria.Oh, and I remember you know that Gio, we might collect some further information from him.Geo?I don't know who you mean.You do not remember?It was just as I arrived, you had a visitor, and you called him Geo.I haven't had any visitors all day.Jay, you saw him, yes?Only thing I remember is some weirdo investigator poking her head into this tent.
```

### [90] hash=`5f7b70142f8ceb10`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p8`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（08晚祷的叮嘱）

```text
Blood must be shed, and our blasphemers eliminated.You have proven your unwavering devotion.Roger, the Green Chair,Mya, the Petty Plague,and our human brother, Léger's the Dead.Welcome to the Hall of the Suffra.Shush, child.It is rude to disturb our precious feast.Yesterday, two intruders broke the ritual of revelation and stole from us the key to thegates of Elysium.The precious gift of Elysium granted by the sufferer before their agonizing sacrifice has
```

### [91] hash=`ab0c2b4242c1aaef`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p8`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（08晚祷的叮嘱）

```text
been blocked from us.You should have kept the secret of the key.Let me use my green chair to grill this shameful rat.I'll make him talk, spill the secrets he hid, and present his flesh to you as an offering!Well well, Roger.Such a caring brother.Your offering is appreciated, yet our siblings have already torn his chest apart, and stillno secrets.Just another careless fallen brother.This is our final warning.

The ceremony for the sufferer draws near.
```

### [92] hash=`413b453463147488`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
So this lovely young lady is family all the way from France for Curia?Well, let me be her guide to the wonders of America.Look at her pretty outfit.Add some crystal earring and a stylish wand.I bet she'll be knockout, am I right?She's your hospitality, madame, but I have a very important mission.A shopping mission.So much shopping to do.So, nice to meet you, Miss Cooper.Now let go of the poor girl, Cooper.
```

### [93] hash=`2d977a512f524f0b`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
I'm still trying to rack my brain, and this old thing can't only manage one thing at a time.Is this your luggage?You're packing up?Yeah.We're leaving this place.Before the wackos hold their ceremony if we're lucky.When we came here, it was to find some safe place away from these people and their conflicts.But now they've followed us here as well, and we've already lost too many friends.I suggest you follow us out, before whatever is going to happen here, happens.
```

### [94] hash=`39bbf1ae9c66bd4a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p9`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（09离巢的蛇）

```text
Where you made your living?Can you so easily walk away?I thought everyone on Haight Street would be just as stubborn as Jay.I think it's a wise choice.Wise?Huh.Don't make me laugh.Haight Street.New Age market.None of this is ours, really.Even the clothes on our back.All we own are the footprints we leave behind, until they're washed away by the tides of time.We live our lives on the fringes of a world that is not kind to us.
```

