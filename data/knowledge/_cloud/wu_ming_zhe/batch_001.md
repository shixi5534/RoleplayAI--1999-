# 剧情图谱抽取 · batch 001

- 角色：`wu_ming_zhe`
- 批次：**1** / 共 8 批（每批 40 块）｜本批块数：**40**
- 筛选：标题含「77号往事」
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_001.jsonl`

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

### [0] hash=`595d8916cde06eb9`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p67`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 1~6）

```text
That's probably where you'll find him.Kim, what does he look like?Like every other Xeno soldier.They all look the same to me.You'll know him when you see him.But I have to tell you, the Bard doesn't like outsiders.Have you heard of the Order of Enlightenment?It's an occult society.Very active these days.They were preaching in this town just a few days ago.Today is their day of prayer.And what does that have to do with me?
```

### [1] hash=`42ad6b4f2ee62b57`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p67`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 1~6）

```text
The bar you're going to is where they gather to pray.That's all I know.If you're going up there, please be careful.Huh, thanks.Watch over you, great sufferer.By your decree, the glory of former days shall grace our present power.Great sufferer, by your decree, the glory of former days shall grace our present path.We dedicate our souls and minds to you.We seek the well-being of our people in your name.
```

### [2] hash=`788d5c3fd64d7b64`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p67`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 1~6）

```text
May the sufferer watch over you.Under their grace, may our cups overflow.To the sufferer!Time for a stranger to come.No crushing the party, am I?Have to learn to take what we can get, eh?You ain't getting that either.Seriously?You don't have any whiskey?I'm starting to understand why Zeno evacuated.What's the point of living in a town where there's no real liquor?Especially for those drunkards.What's a Zeno lieutenant doing here anyway?
```

### [3] hash=`20a06dbd32937e34`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p67`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 1~6）

```text
No alcohol, fuel in that warehouse of yours?Huh, you sure have some interesting drinking habits down here.But I'm curious, why did the sufferer promise you to make you all change your face?I mean, that's quite an achievement, especially here in Texas.Oh, so we're doing this now?Are we?Look, I don't care what you're doing here.Just tell me where that Xeno soldier went.What Xeno soldier?Don't play dumb with me.
```

### [4] hash=`adcc684509259a39`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p67`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 1~6）

```text
That soldier?He's a complete idiot, that one.It's obvious that Xeno has abandoned him, but he insists that they left him here becausethey believe that only he could keep the warehouse safe.Why are you looking for him now if you decided to ditch him in the first place?Listen, I can tell you guys aren't the biggest fans of Xeno, but that has nothingto do with me.I'm just here to get my stuff back.If you insist on finding him try your luck on the outskirts of town.

You might be drinking thereThanks
```

### [5] hash=`4f2c132ba2bdd1b2`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
We can't say for sure if this ritual was created by the last guest.Fact is, you can find all kinds of unusual markings in this motel,most of them less than a month old, very recent indeed.The maids said that there aren't many tourists these days,so my guess is that a group of skilled arcanists have left their work in every room.Based on the markings I've seen so far,There were about three to five people in this group.
```

### [6] hash=`527f57505628ac16`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
And was there a sheep headed Arcanist among them?Well that, I don't know.What I can say though, is that there was a sheep living in here.I saw some hoof prints on the hallway floor, it looked like someone had stayed in thismotel with a sheep.Sounds pretty odd, but I suppose it ain't too strange given the local farmland.But I'm sure this will catch your attention.What?We all know that sheep walk on four hooves, but the hoof prints I saw were different.
```

### [7] hash=`b9240a0a4dc81f47`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
They were small and delicate, and most importantly, followed the movement pattern of a human.Judging by the trail, the owner of the hoof prints was about the size of a slender kid, maybe five feet tall.That's it?What I'm looking for?Don't all know it.They can question my morals, but nobody can question my competence.Can you discern the owner's identity?Hmph.I ain't all knowin'.I can't identify people by their blood.
```

### [8] hash=`74c9030cb4a69851`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
No, I'll need more than just blood to find out who was here.Hm?We are at the beginning and the original source of metals.Through us, the highest tincture of art is brewed.There is neither a spring nor water like mine.I heal and help both the rich and the poor.Yet I am full of hurtful poison.What the hell does that mean?It's a quote from a text on alchemy.All challenges will be resolved with the provision of sufficient and high-quality materials
```

### [9] hash=`352fc998e1f0e1af`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
and the precise execution of the array.But where do we find these materials?What was once Sundered shall reunite.I've seen this handwriting before.In here.My phone number.Yep.This is definitely the same.That sound.It's a Flying Arrow M1903 pistol.Kimberly?What's wrong with her now?I better go check it out, boss.Something don't seem right.You coming?That Kimberly must've run into something.Just when I thought you couldn't get any dumber.
```

### [10] hash=`e233119fcdb67e53`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Is this a suicide?Pulled out the gun and shot himself in the head!His brain splattered on the walls and flew down to the floor!Hmm.There's gunshot residue and powder burns near the wound.Gunpowder particles on his fingers.There's no doubt.He died from a gunshot wound.The bullet was fired from the pistol in his right hand and went straight through his skull.But this ain't just any pistol.It's a Xenopistol.
```

### [11] hash=`ab4e0230c02d3c4a`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
You've got yourself in some serious trouble, Missy.Just an innocent, sad, terrified girl who just happened to pass by.Well, Miss Innocent, Sad, and Terrified.If you want to prove your innocence, start by telling us what happened here.And mind you, I will call you out if you lie.The evidence here will tell me what's true and what ain't.If you're so clever, then why are you asking me?Figure it out yourself.
```

### [12] hash=`359f0d70ec474434`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Right, I'll tell you.This madman has been harassing me.Ever since I moved into this place, I'd often seen him pacing around in the hallway.Day and night, he'd stomp around out here.He didn't care if anyone else was trying to sleep.I thought he must have had a lot on his mind, like he was troubled or something.so I asked him what happened deep sunken eyes were bloodshot every fiber of hisbeing screamed that something was wrong with him sir if you have any problems
```

### [13] hash=`3d296169f2e2db10`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
there are many ways to solve them but pacing in the hallway isn't one of themplus it disrupts everyone's sleep I swear I didn't say anything too harshBut he was just downright rude.Get the hell away!Get out of my face!Excuse me!That's pretty rude, you know.I had no desire to argue with the madman.Thankfully, the maid intervened when she heard what was going on.I have no idea what she said to him, but eventually they came to terms.
```

### [14] hash=`bc9bd71c9bf74744`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
He stopped pacing the hallway from then on.That was a relief.It's not my place to ask.The situation is a little concerning.Mr.Stefan in at your door, dope against it.I just want to confirm that everything's alright between you two.Haven't!Calm down, miss.It's all over now.Do you still have that letter with you?Don't hold onto that.I threw it out right away.It's somewhere in that bin.I need someone to make my bed, and prepare my clothes, and, most importantly, I need to eat!
```

### [15] hash=`07d67ffde2acb395`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
I wouldn't even be here if I weren't looking for...I want to apologize for my behavior earlier in the hallway.Hmm.Looks like a perfectly normal letter to me.No hints that this is from a man on the verge of a mental breakdown.If you won't take my word for it, go ahead and ask the maid.She was there!She can vouch for me!Please, we weren't accusing you of anything.Though griffology has been criticized a lot these days, I gotta say, this looks more like
```

### [16] hash=`3407d9bcce72ab3b`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
a woman's handwriting to me.Then was a woman?You still with us, Missy?What I'm suggesting is that Mr.Stefan didn't write this letter, but a woman did.But that's just speculation.Chances are Mr.Stefan's handwriting was just a little feminine.I'll keep this letter for now.Back to my questions.If the story you told is true, then why are you at the scene of his death?Did you go looking for him, even after all the weird things he'd done?
```

### [17] hash=`ccbb98413747d87c`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Hungry?If I remember correctly, the motel offers room service.And you get one free meal a day, so even if you ain't got no money, you have enoughfood to get by.Eating one of those ham sandwiches.You came to me and made me drop my guard so that one day you could turn me in for abounty.But why me?Why are you doing this to me?It wasn't me who made the plan.It wasn't me who executed it.It wasn't me who pressed that damn button.
```

### [18] hash=`9a15afb28410b8a0`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
All I did was expose their crime to the rest of the world.Tell me, why else would they want my head so desperately if they didn't believe theywere guilty?he pressed the pistol against his temple and pulled the trigger you know the restwhat's going on in here this man killed himself oh dear there's blood everywhereit'll be a lot of work to clean it all up and with the weather being so hotthe room will soon start to smell all the carpets have to go
```

### [19] hash=`8e9ff658da2f76d1`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Have you seen any before?Masks shaped like hands.I've never had a guest who wore a hand shaped mask.Never seen anyone in blue and black either.But if an organization was going to do something in secret,I don't think they'd be too public about it.Hey lady, take me to his room.It shouldn't be too hard for you to find the room yourself, right Miss Argus?After all, that's how you make a living, but I can just tell it to you, it's 214.
```

### [20] hash=`ff7aba1d248d3621`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
You must be curious about that room, I'm surprised.You've been in almost every room in the motel, and you've been here for two days.You're like a child in your curiosity.This place would be much safer if you were the sheriff here.Anyway, I hope you can find that girl soon.Why do you want to go to Stefan's room exactly?Is it related to our investigation?Why of course, boss.I'm here looking for Kayla.
```

### [21] hash=`6773534582dc4dab`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Just as you're looking for that sheep-headed...What is it?That Arcanist you're looking for.Is her name Barbara?You know her?Yep.We met.On Route 77.I just got done asking two men about Kayla's whereabouts, and saw that it was getting dark.My sight ain't so good at night, and the nights are long these days, so I was in abit of a hurry, hoping to get somewhere with proper lights as fast as I could.That's when I saw her, Barbara, all alone by the road.
```

### [22] hash=`526e9dcdaa75790f`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Some jerk of a driver dumped her there, and she asked me for a ride.I turned her down.Heck, I could hardly see.She'd have been better off waiting for the next driver than riding with a blind bat like me, you know?But as I drove away, I changed my mind.She was too young to be left out there all by herself.So I turned back to get her.But when I arrived, she was already gone.There was nothing but a trail of hoof prints in the dirt.
```

### [23] hash=`f2916d3074c24eba`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
When I got to the motel, I saw those hoof prints again.I gotta say, I was kind of relieved to see them.At least she made it here safely.And is she still here?Well, I've never seen any hoof prints leave in the motel.But that don't mean she's still here.You gotta be mindful of what your mind picks up and what might slip you by.It's easy to ignore other evidence when what you've seen already fits your hypothesis.
```

### [24] hash=`e851e2ec5b6b00d8`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
That being said, it's still likely that she's somewhere in the motel.All right, then let's look for her.It seems we're in agreement.To room 214.202, 203, hmm?I've checked those two.Ain't much in them.Argus, did you see a red door just now?A red door?Nothing.Must have been my imagination.Are you all right?Can you still see?Don't worry about it.Ain't the first time this has happened.Second, whether Manus Vindicke has been here, or anyone from that Order of Enlightenment.
```

### [25] hash=`15bb77f3c5338c90`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
And last, about Mr.Stefan.The pistol he used was a Xeno military weapon, and he seemed to know about my relation tothe vacuum bomb operation.It's likely that he once held a high rank within the Xeno military.I want to know why he came to this motel, and what happened to make him lose his mindhere.Lose his mind here?What makes you think he wasn't crazy already?Xeno pays much more attention to its soldiers' mental well-being than any conventional military organization.
```

### [26] hash=`dd25cd9285f91010`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
It's because quite a few of them are arcanists.They're both Xeno's strength and weakness.So I'm inclined to think Mr.Stefan developed these mental health issues after entering the motel.Huh.Is that so?I gotta say, I don't know much about all this military institution stuff.So, here's the plan.First, locate Barbara.Second, look for any signs of Manus Vendictae or the Order of Enlightenment.And third, find out how poor old Stefan lost his marbles.
```

### [27] hash=`17faa1be7982fa25`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
And of course, I've got my own business to deal with.Tracking down Kayla.transformation array but it's not in its full form.They were trying something.Check it out.This is hair from the mane of a howler line and there are some other materials around it too.Not exactly sure what they are though.They're too finely ground but one thing's for sure.Someone held a ceremony here and for some reason it didn't work out for them.
```

### [28] hash=`a7fd4d6bb028a807`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
This is important.The Foundation needs to know about this.Argus?This is Kayla's hair.She was here.In this room.Or at least someone who came into contact with her.This is the life.A warm, beautiful night.A cold drink and no one but me and the stars in the sky.Maybe I'll just lay here till morning.A good night with good drinks!I wish every day could be like this.Hey buddy, you're blocking my view.Huh?
```

### [29] hash=`4202cb9317c6fded`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Are you stargazing?Has anyone ever told you that you sound awfully like Lieutenant Lillia?The rider of Red 38?Heard of her?No one can fly like her.Of course.Oh my!You even look like her!Keep playing dumb, and I'll show you what it's like to have her kick your ass.Lieutenant Lillia, Airman First Class Andreas at your service.Are you the warehouse guard?Yes, ma'am.On your feet, soldier.My Red 38 is in your warehouse for maintenance and I need you to remove the gravity ritual from it.
```

### [30] hash=`279fe8bb560c6681`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Gravity ritual?If you don't understand what I'm saying, go get someone who does.I need it today.Right, the gravity ritual.yes yes I know please come with me I'll take you to the warehouse are youcertain you can undo the ritual yes ma'am they made sure I got the hang of itbefore they took off leave it to me lead the way soldier open it oh Iremember this package I thought it was some kind of joke or someone with the
```

### [31] hash=`7b68417509b15a5c`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
same name as you sent the package who would have thought that you'd come toyourself hurry it up soldier open the crate now ma'am I know you want to dothis quick but I haven't been authorized to undo this incantation if you can'tdo it find me someone who can I won't say the third time truth be told there'sno one else to turn to I'm the only one left I was made an airman firstclass to do this job I was still in training before this you see the
```

### [32] hash=`0af1b6c27024eb99`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
The others were either transferred back to headquarters or just left.I don't know where they are now.But since they entrusted me with such an important task, I'm sure I have a bright future aheadof me.You just said you aren't authorized, not that you don't have the ability, right?I have two options for you.One, remove the ritual now.Or two, I beat your ass and then you remove the ritual.Well...Choose!
```

### [33] hash=`f66bb55f6966178d`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
No more jibbering!I picked the second one.Huh?You see, I'm happy to get rid of the ritual for you.But I can't do it on my own initiative.I'm only an Airman First Class.I can't make decisions about this stuff.So, you have to beat me up to avoid future inquiries.One day, after I'm promoted, I'll be able to better assist you, ma'am.I mean, you're the best pilot I've ever seen.I even made a scrapbook of the reports on your flights.
```

### [34] hash=`221917bd7f720dc8`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
Alright, no screaming, soldier.Let's do this.Stop, stop!This is plenty to prove my innocence.I'll undo the ritual now.Oof, you almost blinded me there.Thanks, soldier.There's one more thing.Yes, ma'am?Do you know why Zeno pulled out of here so suddenly?Hmm, they said it was an order from the top.The top?That's all I was told.But word is, it was because Admiral Igor got real mad about the video leak of the vacuum
```

### [35] hash=`a43c64d4ae972c88`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
bomb.But that's just a rumor.Ever since the evacuation, strange things have started to happen.Such as?We started getting visitors from this group called the Order of Enlightenment, and nowthe farmers have stopped tending their fields.The cattle and sheep have been abandoned in the wilderness.All the town's folk do now is go to these gatherings, hoping that thesufferer will bring them eternal joy.I don't know who this sufferer is, but he
```

### [36] hash=`0e601582d9bd9166`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
ain't doing any good here.Where do those people stay?In the town?It'sa ways away, I think.A place called Tuesday's Motel.Belin, Vertin!I have to go back!Let's get out of here, girl!Safe travels, ma'am!Choose this motel.Can you give me a ride?I can't help you.Ask someone else.Can you give me a ride?I said I can't help you.I want some chocolate.I had a kind man who gave me some chocolate.I've never tasted anything so silly.
```

### [37] hash=`9c5bbd6de804ba9d`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
The hell?Stay away from me!Can I?Can I have that candy?Asking me for candy?This isn't Halloween, idiot!Look at my back!Wanna watch the aerial stunts?Right, Wind?It's you.Are you alright?Pale.You shouldn't sneak up on people like that.I could have hurt you.Apologies.But you're safe now that you're at the motel.No need to be frightened.Is that the sound of a sheep?You noticed it too, huh?Ain't no way that's a human on the other end.
```

### [38] hash=`4aed6ba33cf353e6`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
What are its side effects?Boss, you expect a merc to reveal her weakness?We ain't that close yet.One thing I can tell you though is that I suffer the side effects as long as my eyes are open.Luckily, I've got cutting edge technology at my disposal.They're safe, efficient, and most importantly, satisfy my sweet tooth.They may be called candy, but they're actually medicineand ought to be used following medical instructions you should know that
```

### [39] hash=`9a3483211d3cd59d`

- lang：`en`｜version：`2.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p68`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.1-活动】77号往事 | 7~11）

```text
give me a break pops what do doctors know about my life i use these candies whenever i need themain't that the whole point but did you hear that hear what heartbeat right outside the doorsomeone's eavesdropping on us care to explain why you're here miss kimberlyJust how obsessed are you with Mr.Stefan, huh?Even now, after his death?It's not what you think.I was just looking for my toy and it just so happens.
```

