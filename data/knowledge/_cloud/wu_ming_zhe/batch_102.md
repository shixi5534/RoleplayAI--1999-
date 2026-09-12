# 剧情图谱抽取 · batch 102

- 角色：`wu_ming_zhe`
- 批次：**102**（未缓存补漏批 3/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_102.jsonl`

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

### [0] hash=`fbbcd565b07d040d`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p16`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（16.意大利之歌(船桨是在这儿打磨的，浪花是从这儿扑腾的。并不是每阵风儿都追寻永存。)）

```text
Could be someplace ten years ago or even a hundred years.You mean we're traveling through time?I...I don't know.I've got to admit, Senorina, this all sounds a bit too wild to be believed.But as sure as the compass points north, I will trust you mean every word you say.Thank you, Giovanni.So you're saying if we don't do something, then none of us will ever see home again?It's decided then.We'll fight by your side, Miss Barcarola.
```

### [1] hash=`90130e22562ccad1`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p16`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（16.意大利之歌(船桨是在这儿打磨的，浪花是从这儿扑腾的。并不是每阵风儿都追寻永存。)）

```text
Because none of us wants to find ourselves in a random land back when the dinosaurs roamed.You got that right.I won't let them ruin my retirement.We'll sell ourselves home if we've got to.One thing's for certain, I don't want to be stuck here for the rest of my life.Alright, gentlemen, enough with the words.It's time to take action.Miss Barcarola, is there anything we can do?Yes, of course.
```

### [2] hash=`54319a719fa682fc`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p17`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（17.不和谐音(一股震颤灵魂的噪音，连摇滚歌迷也倾倒。)）

```text
I just checked out the wiring.All the signal transmitters have been sabotaged.No wonder there's been no sight nor sound of those oily freaks.Relit in, fish tank.You're not conducting the artificial storm experiments right here, are you?Why not?We have a supernatural phenomenon, a vast water supply, sufficient asymmetrical nuclide R,and the required sound wave frequency ready in the transmission system here.

more than worth a bit of storm syndrome no matter how nasty at least now you'llhave an extra equilibrium umbrella Ulrich I refuse to be a part of this
```

### [3] hash=`09513aa961644f29`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p18`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（18.二十七岁俱乐部(摇滚不死。)）

```text
What did you say?Pardon me, you daft lightbulb.I will not be your undertaker.Regulus, you still haven't grasped the significance of this project, have you?We've figured out the principles of the storm,and even developed the means to create its simulacra.Yes, there's still much room for improvement,but we've already made a huge leap.And now, we finally have the opportunity to put our theories into application.
```

### [4] hash=`748e5efab791b8f9`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p18`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（18.二十七岁俱乐部(摇滚不死。)）

```text
Rock never dies!Huh?Whether you're a rock legend or not, you shine with the radiance of humanity.Regulus, I salute both your experimental spirit and your rock and roll spirit.There's only one thing left to do.Project, experiment some material immutability via artificial storm.Locale, radio room of the Free Breeze crew ship.Experimenters, Ulrich and Regulus, our experiment will now commence.
```

### [5] hash=`e58f9a1f96ba567a`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
Ms.Vertin, it seems all the passengers are gathered in the lobby.We've lost too much time.A lot of people have put on masks while we were locked up.We'll need to round up the ones that are still conscious.Sure.More contenders?Like we don't have enough people wrestling for a mask.Give me that mask, asshole!I'm joining Manus Vindicte.I will take the trial.I believe you may be too weak to endure the trial.
```

### [6] hash=`45ac411a2c8665e4`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
You should leave this valuable opportunity to someoneWho will be more useful to Captain Grace?Please put the mask down, everyone.This isn't the way to survive.Give it to me.That mask belongs to me.Miss Grace smiled at me once.She must like me.She'll want me to join her.I just don't want to be killed by the storm thing.Get back to your senses, people.If I were you, I'd have thrown these creepy masks
```

### [7] hash=`bfded4f9b8bda2c0`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
into the sea the moment I saw them.Salone, you must put on the mask, please!For our people.It's not scary, I promise.Would you rather be captured by those outsiders?Go to the captain's room, Toa.You passed your trial.I'm sure the captain and ourpeople there need you more than I do.I must stay here to look after Kitiono, LittlePita, and our friends who still seem to be lost.Haven't you heard their cries?
```

### [8] hash=`90df619bdb211a41`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
You need to think of the future, Saloni.The new beautiful homeland we're going to recover.We could live peacefully once more.We could-Stop, Toa.I'm sorry.When I see how tainted and twisted your spirit shell has become, I can't.I won't.That's Ms.Saloni.Timekeeper, I think they need assistance.Zanetto!Watch out!Zanetto!Get ready to use those sedatogens.Recaro, me tu cuesta con gole.Pardon me for this, please.
```

### [9] hash=`0d428d7ccea50394`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
What are you doing to my people?I won't let you hurt them.Atootoo.I'm so glad to see you unharmed, Atootoo.But our friends...I know what happened, Salon.Parker Rola told me everything when she got me out.I've made up my mind now.We can't wear their masks, Salon.We never should have agreed to their so-called revenge plan.What's this happening?Take than ever before!Timekeeper!At increasing the dosage of sedatogens!
```

### [10] hash=`4bda8d669ccb3814`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
The mask's influence has wormed its way deep into their brains.I'm afraid sedatogens won't be able to awaken their consciousness any longer.They need something that reaches into their song.Dude!Just toy of yours and pay attention to the class, Baccarola.Music is a language that moves us on to a deeper level than any other.Transcending both culture, place and time.Wherever you are and wherever you go, it will always stir the depths of your soul.
```

### [11] hash=`4d37e695e00e2624`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p19`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（19.我们称作乡愁之物(风中忽闪的罗盘草，河岸的水车发出咕噜声，人们所熟稔的。生活。)）

```text
We're not so different deep down, are we?Huh?What's that sound?Violins, piano, cello, double bass, and flutes.What?Violins?She hates violins!Hey, I want to go home!Sorry for tutu.I didn't expect my song to put your people in the state.Only wanted to help you did you're the greatest musician I've ever seenBut your friend they've they've gone homeBut look at the shining pristine spirit shells around their necks.

That is a signIt tells us that their souls are at peace.That our friends lived a full and honest life.You too!
```

### [12] hash=`da6aed663ca17105`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
Seriously?You're doing the artificial storm experiment?Here?Ha!You're not about to go swimming with my most treasured record, are you?You must understand.This record is a vital element of the experiment.And you need to understand that it's a one-of-a-kind relic of rock and roll!Oh, don't fret.I've taken that concern into account.What?!The closest potential location for the experiment appears to be directly on the route of this cruise ship, the Freepleys.
```

### [13] hash=`84978d96aa9e3806`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
Wow!My calculations show that we're veering off course.We're accelerating on a southward trajectory.These people are fortunate, born into cold wealth and privilege.Miss Grace, please, show us a new way!May coincident to have a similar device myself199920052007There is a pioneer who has crossed the stormThere's a language that transcends all barriersPlease everyone hold on to each other and follow music
```

### [14] hash=`f818d0ab6053d021`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
And you're going to do the experiment aloneThat's the planAnd if I fail, at least you'll have one more umbrella for the others.When the first proverb appears on the shell, we reach the shores of elsewhere.The island, the upturned palm of Mother Sea.The once drifting boat now beds itself in the golden sand.When the second proverb appears on the shell, we kindle the fire,Remember when the waves came and took away Malaga?
```

### [15] hash=`a939f3bcdf0afe69`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
Hailani cried for days over that little pebble castle.And then that strange oil polluted the water all around ITT, the only place where the wateris calm enough to hold a pow-pow race.We haven't held a race since.Then Métis and Vaipuna.But we've made it through, because that's what we do in the face of difficulties,right?What if I told you that the sinking of Malaga and Baipuna wasn't entirely caused by the tsunami, but there were other factors at play?
```

### [16] hash=`9f46cb28bb538e0c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
It is true that the tsunami sent them into the sea, but long before it struck, foreign military forces had been eyeing the islands for their strategic value.Those rumbling sounds, they weren't thunder?They were torpedoes launched by humans, and I have some unfortunate news regarding them.The area is now under martial law.Any development plans for the region should be revised accordingly.These coordinates, they cover Nuku Teow.
```

### [17] hash=`122eab15a9f73e63`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
After a brief investigation, they concluded that your home is an unoccupied area suitablefor their weapon testing.With all due respect, Miss Grace, not even the Nukutai can predict the movements of the ocean that far in advance.On what basis are you making this forecast?It's not a forecast, Mr.Kamuta.Call it the wisdom of hindsight.Or perhaps, I should put it more clearly, have you heard of the storm?
```

### [18] hash=`afe66469df8fa5c7`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
It's the tsunami.It's happening.What's going on, Chuchu?Kamuta?No time for questions, Toa.We must bring these baskets to safety.There's food and clothes in there.Here, I'll give you a hand.What are you doing?Leave them.There's no time.We must get to the ship.Now!Our people still have to live after the flood's over.If we don't bring something, what are we going to eat or wear?These things won't fall into our laps, you know.
```

### [19] hash=`57f281f31619021d`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
Listen, it's different this time.You...Juju!Watch out!What are all these splinter cats doing here?These aren't just splinter cats.Are those Stormation sea snails?And Krabs with ghost faces?I've never seen them all come out together before.What kind of storm is this?They can sense the coming tsunami.Come!We need more hands to drive them off.Understood.Attack.Everyone get to the quickspear!tsunami it's the worst I've ever seen is it true it's this the end of Mellie
```

### [20] hash=`eea1ae05d73e0bca`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
don't you don't just stand there get over hereflesh date to punt Vala miss grace seems I'm right on time you're missgrace you should be more careful out here dear people of new Katao are youThey are the living gold of the ocean, but to the people who live near their regular habitatsThey are an ill womanWherever they appearFloods are sure to followThis tsunami is only the beginningAnimals migrate and leave their homes behind when conditions become
```

### [21] hash=`f79299cb1140dec7`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
Unfavorable you should do the same look around youThink about your peopleTutu, it's okay.We know you have your reasons.Do we really have to leave?The outside world is indeed full of dangers.But there is less to fear than you think.I'll help you through it.Or ship.These headlines.A new naval testing site has been established in an unoccupied area of the eastern Pacific Oceanto facilitate future armament research and development.
```

### [22] hash=`a4eab9aca4d16b72`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p1`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（01.船讯(生活是独立的，可生存不是)）

```text
South America is facing a significant economic crisis marked by stagnation, inflation and rising unemployment.The poverty rate in several regions has reached new highs in the last decade.The Ocean Conservation Association is calling for greater attention to be paid to the oil spill near the archipelagos,claiming that the relevant organizations have yet to launch a full investigation into the cause of the incident.
```

### [23] hash=`cd9aac2bb5e1a73d`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
What are you doing?How could you side with our enemies?Against your own people?Against the ones who would rebuild our home?You've brought shame on our people.You've disappointed me.Stop all this now and come with me.We will beg Ms.Grace to cleanse her soul.Joining Manus Findictae was a mistake, Kamutsa.Their masks blinded our people.They tricked us with their lies and empty promises.There is nothing in this so-called new era that Miss Grace promised us that is worth
```

### [24] hash=`eccc2006e6138b72`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
becoming monsters and corrupting our spirit shells.Our pride must be in ourselves and who we are, the shells around our necks, the wordswe speak to one another, the way we treat others with kindness, not hatred.That is what defines us.We are more than just how the outsiders can use us, more than our sea mother's eye.We are the wisdom of our elders and the traditions we keep sacred.And if our islands all sink beneath the waves, we will remember them in our craft and in
```

### [25] hash=`ff032773e6840a36`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
our stories.We will remember the story of the brave Nukatai girl fighting off the series.We will remember them in the songs of Nuka Teow.No matter whether it's an island or a ship we stand on, as long as we're together, NukaTeow, our home, lies beneath our feet.Didn't you say you would always have faith in me, Kamutsa?You believed I could lead our people to a better future.Now, I believe in myself too.
```

### [26] hash=`c3665a49cb7dc2ad`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
You'll be a better leader than I ever was for Tutu.I'm fine, Tutu.I'll be alright.You're right, dear sister.The words you spoke have opened my eyes.It's the Mask's punishment.Manus Vindicte used their masks to sift out their most loyal followers.Those who passed the trial can retain their personality and memories.However, if they should show any signs of faltering in their faith,The mask will punish them.
```

### [27] hash=`e2dafd6cd25ea9ad`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
Their consciousness will be devoured by the fathomless depths of ArcanumUntil they become nothing but a walking corpsecaught in eternal agonyWell, well, I am stunned by the breadth of your knowledge of our operations miss FurtinBut I must remind youGossip like that is terribly bad manners.Is it any wonder why our guests look so terrified?Though it does pique my curiosityI wonder, even with all you said, do they fear us more than they fear death?
```

### [28] hash=`6671701782607b5c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
What a pity, Mr.Kamuda.I had high hopes for you.It seems our friendship has come to an untimely end.The people here know the truth about your masks.There's no sense trying to deceive them any longer.Oh, is that so?Pinekeeper, what do we have here?How adorable.The ever-loyal deputy leaps into action, but we're on a tight schedule, and I don't have time to play games.There's no power in your shiny little badge here, Mr.
```

### [29] hash=`be83acc96f503624`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
Kamura.Manus Vindicte will forever remember your contribution.Farewell.Fatutu!Watch out!Miss Grace deliberately led us here to the deck, but why?Timekeeper, the cocoon is affecting the mass guests somehow.We're riding in pain.We have to act fast.Finish this before more civilians become victims.Understood.So far to you.Why do you insist on taking their lives too?Betrayal bears a hefty price, Ms.Fututu.
```

### [30] hash=`436d007699207f03`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
The lies of the Foundation have twisted your minds.You're confused, disoriented.I'm sorry I couldn't save you from them.Fight to us.I've done nothing of the sort.I will guide you to a brighter futureTo a home untouched by the tsunamiJust as I promised what a pity hurry along my dear guestSay your farewells to our beloved free breeze while you still have the chanceTake on some atoms.This is our chance
```

### [31] hash=`9d8ae92e9518f4ec`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p20`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（20.向别处(我们哪儿也不去。)）

```text
Time to destroy this thing, and save the Free Free!I will pray for you.Sorry.What is it now, Ms.Barcarola?I'm sure you've already guessed this, but you've been relieved of your duties here.Maining the support of the Nuketai was never your purpose.Am I right?Enlighten your cleverness.If it wasn't so damnably frustrating.A pity.But there's no turning back.
```

### [32] hash=`623f5579e9ae3184`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p21`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（21.最后一次告别(亲爱的，自由的代价是什么？)）

```text
You never cease to amaze me, do you?Manus Vindictae have failed.It would appear that way to you, wouldn't it, Miss Furtin?How shall I congratulate you?And as they say, be seeing you,and sooner than you think,before I go, consider this a parting giftfrom your captain, for all time's sake.Goodbye, my dear guest, from the bottom of my heart.Thank you all for this unforgettable journey.That came from the engine room.
```

### [33] hash=`0401339cea923af0`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p21`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（21.最后一次告别(亲爱的，自由的代价是什么？)）

```text
Those team-headed bastards, they must have done something to it.Go see what you can from the deck, Charlie.Damn it all!It blew the hole straight to the starboard hole!Gentlemen, you can't possibly be saying that the free breeze is going to sink!What's worse, that explosion came from over by the lifeboats!These bastards are hell-bent on making sure we all end up at the bottom of the sea!Bus, Miss Barcarola.
```

### [34] hash=`e2b517743e5b9df0`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p21`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（21.最后一次告别(亲爱的，自由的代价是什么？)）

```text
You promised to keep us safe.And you, Miss, aren't you from the Foundation or whatever?You said you'd protect us.Please line up, everyone.My suitcase should be able to temporarily shelter some passengers.Miss Barcarola, do you know how many passengers are aboard?About 1,600 in total, but I think many of them will be injured.I don't know how well they can move.Ms.Barcarola, could you point me towards the radio room?
```

### [35] hash=`85eca52a5f6c9f30`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p21`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（21.最后一次告别(亲爱的，自由的代价是什么？)）

```text
I believe our friends may be in need of help.Of course, Grace wasn't the captain for long.It's possible she didn't know about the ship's backup lifeboats.They might still be intact.Good thinking, Ms.Barcarola.You're a natural born captain.Everyone, follow me!
```

### [36] hash=`3ccc4e6eb70f0422`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p22`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（22.我不曾遗憾(一种有限的美丽，正在水中消逝。)）

```text
I don't want to die like this.There's still so many things I want to do.I want to go home.Even if the storm changes everything, I just want to go home.We have talked about it, and the Nukatai are willing to give up their spots if there aren't enough boats for everyone.We want to make amends for what happened earlier.Patutu, this wasn't your people's fault.The Free Breeze will not abandon any of its passengers.
```

### [37] hash=`e47cc933afd6e9b8`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p22`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（22.我不曾遗憾(一种有限的美丽，正在水中消逝。)）

```text
You have my word as the official musical director, and I suppose the acting captain.What have you done to your crackling box?Sinfonia Chiusa, di vedete vi con grazia.I don't remember you telling us how hard you worked to find this.I haven't been one of those since my time in Galicia.You're playing on a football?You're in Barcelona?You're not in the green season?You're flying so good!
```

### [38] hash=`cdad12720495884f`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p23`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（23.海中升起的她(她从很远的地方来，她有许多名字，她从未离开过你。)）

```text
Mama said, little pumpkin's violin should have a rich and bright, but not too sharp orunbalanced, just to light her.Let's ask Mr.Bellin for some top notch spruce or maple wood, the best that Cremona canoffer.We'll need some glue for the neck joint and plenty of varnish.Of course, this is a Cremona violin we're talking about.Most important of all, it will be a violin for our little Baccarona.As much as I try to deny it, I suppose my heart is still there with them.
```

### [39] hash=`0dd3431258f80914`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p23`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（23.海中升起的她(她从很远的地方来，她有许多名字，她从未离开过你。)）

```text
Mama, Cremona, we did it.Congratulations, Timekeeper.I should be the one congratulating you, don't you think, Mr.Fishtank?It's an odd twist of fate, isn't it?Indeed.I've just reported our findings to Laplace.With this our research on the storm can finally advance to a new stageI've even managed to develop a taste for rock and rollNever doubted you timekeeper.There was no storm not this time.Anyway
```

### [40] hash=`e669824e4cbbbf43`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p23`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（23.海中升起的她(她从很远的地方来，她有许多名字，她从未离开过你。)）

```text
Thank you for your continued trust the matter is sure to be the most fabulous boat party ever heldI would have missed it for the worldOh, man des choumEs es in bolin foorunUn taten zingen, die lieder klingen im eigen gundO kre de la lune, ni voa kampeOn shesha la blume, on shesha du feOld melancholy, things of the seaThey arrive with the silence of the morningAnd when he goes out to see her, he flies to her house

I feel the chill of the wavesProsperous the wind
```

### [41] hash=`c6d104a1fda99615`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
Uh, Captain, we seem to have deviated from our route to Laplace.Great pirate, Mr Apple, doesn't simply rely on her compass.She must listen to her heart too.Ah, this Apple thought you were trying to slip away to make the most of your final day off.Well, that too.Rat whiskers all the way from Brazil.Nothing for brewing a chill wind, Alexa.Only a hundred and eighty-five sharp-a-donties.We've got some seriously groovy art on the streets
```

### [42] hash=`b5d633e115b7c472`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
Pop art?That's a bit dated, don't you think?I beg your pardon!Did you hear that?We'd better go over there and check it out, Mr.AppleWhat is it?Could it be...Manus Vindicte?Miss Burton did caution us against the Manus followers we might encounter in AustraliaNo, it's something much more important than thatAustralia, for those of you who haven't signed up for the tripThink again.This is the ultimate sailing experience.
```

### [43] hash=`5872e9f3891e9fea`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
Relaxation, food, drink and music.Don't miss out.The Free Breeze is about to set sail.No need to worry about currency exchange,whether it's Australian dollars,sharp odonties, arcane materials or a rare collectible item.All are welcome in exchange for a ticket of equal value.A small price to pay for an unforgettable journeywith the talented, multi-instrumentalist, Parcarola,and her fantastic crackling box.
```

### [44] hash=`4010c9fec0147d0a`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
We've also prepared a little giftfor our most enthusiastic guest, a free cruise ticket.That's what I'm talking about?Oh, this apple should have known better.Ladies and gentlemen, the party starts now.Put your hands together for the enchantingMiss Parcarola and her captivating melodies.You're much too kind, Mr.Hamish.saying all these wonderful things about me, but I'm only a cruise musician.It's thanks to the collective efforts of the whole crew that the Free Breeze has been so successful.
```

### [45] hash=`abd16775897296ed`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
I just feel privileged to be a part of it.I know you want to stay humble, Miss Barcarola, but there's no reason to be so modest.Many of our guests come aboard just to hear you play, and I'm sure there will only be more in the future.So what's the harm with hyping the crowd up with a little round of applause?Well, if it's for the ship, I suppose I can handle a little publicityOf course you can and you deserve it, too.
```

### [46] hash=`bfc275b53b19f82f`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
By the way, do you know the guest over there?She's veryEnthusiastic I've been drumming up the crowd sold us a load more tickets.We've never sold out so quicklyEveryone listen up.I've got some exciting news to sharePiece of paper in my hand could be your ticket to an incredible seafaring adventure.Just think about the cold breeze, the spruced up cruise ship and the awesome music.What more could you ask for?
```

### [47] hash=`596e17d02dc22c62`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p2`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（02.“自由海风”(啊，海风。啊，自由。啊，最后一日假期。)）

```text
This is a once in a lifetime chance for a trip you'll never forget.Buzzing!Throw your hands in the air and your coins out of your pockets and let your dreams come to life.Let's hear those coins jingle and fill your spirit soul!Is she a local?Australians are known for their sunny disposition.No one knows her, miss.But to be honest, I'd love to invite her to join the crew.If only the captain weren't so picky with the new recruits.

I know what you mean.Her enthusiasm is infectious.Maybe her energy would wake up our stuffy new captain.we can see each other again, preferably soon.What?
```

### [48] hash=`65cf118b619c7179`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
They gave you this flyer at the sail away party?Not just that one, there's a whole stack of them!Alright, Researcher Regulus, I think I've got everything down.Let's run through it again.Researcher Regulus suffered horrendous mistreatment during the pre-sail event of the Free Breeze,which has had a significant psychological impact on her.In order to recover from this traumatic event, she formally requests...
```

### [49] hash=`b905c803808e6545`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
A one-year advance on her salary and fifteen days of leave, the funds are to be used solely to book passage on a cruise trip, with the goal of replacing her negative experience from the pre-sale event with a more positive one.Ling, the truth!I can see that bottle of artificial tears in your hand, Regulus.Please put it away.There's no need for dramatics.Thank you, Ulrich.Knew there was a soft spot underneath all that metal.
```

### [50] hash=`3f570fd20f606384`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
So, you can't get the benefits of a full-time employee.And to top it all off, you didn't even show up to register at the first Storm Research Group meeting.I...Please, save me the excuses.There's still a chance for you to turn things around.You can take another assessment.We'll use the results to make up for the assessments you've missed.It'll be crucial for your performance review and, consequently, your employee benefits.
```

### [51] hash=`4253ae203d34ea75`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
Bring it on!You can use the computer to help you, and you might find some useful books and papers in the second drawer on your left.The instructions for the computer and a guide on how it works are all in there.Given its difficulty, there is no time limit for this test.Best of luck, Researcher Regulus.You better keep your word, Ulrich, or you'll be no different than those sailors.At least they didn't torture me with maths.
```

### [52] hash=`d4c04fde1c71740b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
Are you scared?Captain!Follow me, Regulus.Best of luck, Researcher Regulus.Where am I?Am I?What's happening to me?Is this some kind of cruel joke from that apparel mod?Glad to see you're still in high spirits, Researcher Regulus.But this doesn't add up.I gave you an encrypted code, not a Sudoku puzzle.What do you mean?Come on, get yourself together.The ninth storm has passed, Researcher Regulus.You've had plenty of time to brush up on your math.
```

### [53] hash=`d43a9a7708cdb7f4`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
Alright, let me explain.All you have to do is a basic decode and transcription of the result using the Laplace encryptionkey.See how the fourth from last digits have changed?There are no numbers greater than 24 within the 17th interval, and those in the 18thinterval don't exceed 59.So, if we make a bold assumption here, these numbers have probably been coded usingLaplace's nomenclature, where the codes of time are always placed between the
```

### [54] hash=`66db007f013eed5c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
12th and 18th intervals.You'll see this a lot here.We use them for ships,satellites, manpower arrangements, and such.Finally, we input the result intothe Laplace astronomy database to see if we find any matches and, there, aset of photos taken from space.Blin me, I spent the whole day doing this just to find a few photos!These aren't just any photos, researcher Regulus.Take a closer look.The first picture was taken on December 2nd, 1995, the day the Solar and Heliospheric Observatory was launched.
```

### [55] hash=`540ed3a7c21fe878`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
The second picture was taken on June 25th, 1997, during a period of sunspot activity.The third one is from November 21st, 1998.It's an image of the first satellite ever deployed from a space station.Before all our struggles to study and control the effects of the stormThis pioneer crossed the storm unscathed and sent us these imagesWhy are you telling me all this?Did everyone else's assessments turn into some kind of top-secret briefing?
```

### [56] hash=`48efda1d2a6fb73d`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p3`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（03.密码学入门(我们伟大的船长所经历的无数小小挫折之一。)）

```text
All I wanted was an advance on my salaryFor once could you see the bigger picture here?We've been presented with an amazing opportunityAnd all you can think about is your salary
```

### [57] hash=`efac8e08d320d99c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p4`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（04.时代之声(“陨石坑”音乐节里合唱着“一夜狂欢”，人们摇摆肢体。朋友，瞧我接着了什么！)）

```text
very, very important files.The hunt is on.Let's start with what's on this table.La la la la la la la la da da da da da da do do do do.Almost forgot, can't go treasurehunting without some music to rock out to.Dammit, I forgot to tell her to keep quiet.What's happening?Is this an earthquake?This is the note I wrote last time I wasof the Laplace staff.We're not working together for a couple of research papers.
```

### [58] hash=`c2f4ca9890a2b3ab`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p4`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（04.时代之声(“陨石坑”音乐节里合唱着“一夜狂欢”，人们摇摆肢体。朋友，瞧我接着了什么！)）

```text
This is about the survival of everything on Earth.We need all the help we can get, including yours.In fact, the Laplace even held a meetingwith the Foundation to discuss borrowing your record.The Foundation suggested we applyfor an item transfer orderunder the artificial storm projectand let the timekeeper take over the matter.Some of my colleagues told menor happiness, nor harmony, nor fame, nor pride, nor strength, nor skill in arms or arts.
```

### [59] hash=`210e230f6948af9f`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p4`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（04.时代之声(“陨石坑”音乐节里合唱着“一夜狂欢”，人们摇摆肢体。朋友，瞧我接着了什么！)）

```text
Before a cruel whip, man who man would be, must rule the empire of himself, in it must be supreme,establishing his throne, on vanquished will, quelling the challenges of hopes and fears, being himself alone.Is everything all right, Timekeeper?Sinetto, change of plan.We need to contact the Foundation, now.
```

### [60] hash=`3e3fc31c8c31c949`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
Good afternoon, Mr.President.May the peace be with us.May the peace be with us, my friend.Zeno has been restored to its usual state.Aside from Igor's ardent supporters,the rest of the Zeno soldiers and officerswere unaware of his betrayal, just as we expected.Admiral Igor's funeral has been held as planned,one that befits his rank and status.All relevant personnel remained in South Americafor the ceremony as per Zeno's funeral regulations.
```

### [61] hash=`1350a1a0486d078c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
We're in the process of selecting a new admiral.I'll provide you with a candidate list shortly.Additionally, we've dispatched an investigative teamto Tiero del Fuego to search for Igor.Very well.What about the girl?The girl?Are you referring to Lopera?Her emotions have stabilized, so we'vedecided to leave her in South America for the moment.Of course, she'll be put through the necessary investigations as circumstances dictate.
```

### [62] hash=`e80e8dee5719e9ff`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
Keep a close eye on her.And that little singing bird?Zeno is quite upset about our decision regarding Miss Kimberly.They're insisting she undergoes a more thorough investigation.I feared that if we gave too much pushback, they would take a more extreme stance in response.So I agreed.Those soldiers never budge.Of course, Zeno agreed that the investigation would be done under the supervision of the Foundation.
```

### [63] hash=`916befb910f0cc71`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
If nothing else comes up, she will be put into the Timekeeper's team and granted the same rights as the other members.Good.Don't keep Vertan waiting too long.There's more.Madam Z has received word from the Timekeeper.The Timekeeper suspects Manus Vindicte is active again in Sydney Harbor.They're likely on board a cruise ship named Free Breeze.You mean to send them on that cruise?We can't keep her under our wing forever.
```

### [64] hash=`ec475dfe199dcf12`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
Understood.What brings you all the way over here, old friend?La Blas has requested the Foundation's assistance with the artificial storm project?Yes.Ulrich is overseeing the project and has requested as much asymmetrical nuclide are as we can spare.He's also requested our help in determining the most suitable location for the experiment.But Moth's status still remains unclear.If we proceed too hastily, we might jeopardize the situation.
```

### [65] hash=`ef96a74e560034af`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
I thought you'd have foreseen something like this.A few pieces must be sacrificed.If you're to win the game, you know that better than anyone.Is this also the Pax House's decision?You have my word on it.I see.I'll inform the Timekeeper and Ulric of their missions.To their meeting.Oh, no, no, no.Please don't trouble yourself.Sorry, don't get me wrong.I'd appreciate your help where the circumstance is different.
```

### [66] hash=`9026d36c43bdcef0`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p5`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（05.离港日(所有的河流都奔向大海。)）

```text
But the experiment is still confidential.Please don't mention it to anyone.I'd like to avoid any unnecessary risks or interference.On the cruise ship, we are but strangers.I see.Don't you worry.I have a little disguise for myself, too.
```

### [67] hash=`2c90ead7b7a0eec5`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
Baccarola, at last you've graced us with your presence.Henry and I were just having a little vageron whether we'd see our musical staroutside the spotlight.Looks like he'll be buying methe next round of whiskey, eh?Signore, tell me to pour you the first glass.How do you like your whiskey?On the rocks, perhaps?Thank you, my dear.Miss Baccarola!Last time I saw her,she performed an entire symphony all by herself.
```

### [68] hash=`b67425c1f51b98fb`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
She was the whole orchestra.I've never seen anything like it.You again, my little friend.Miss Baccarola, what a pleasure.I've heard so much about you.My child hasn't stopped talking about you since you spoke to him about the didgeridoo at Sydney Harbour.He was so excited by it that he begged us to bring one on board.Lovely.The didgeridoo truly is an enchanting instrument.It's so resonant, don't you think?
```

### [69] hash=`fcebfd8c70700a8b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
And its people hold a special kind of shell at the center of their beliefs.They've rarely made contact with the outside world.It's often been described as a peaceful paradise.I also read that the Nukutai almost never leave their homeland.Why are they here?The Nukutai will never abandon our homeland!Just wait!We'll find our way back when the new era comes!The new era?Toa, that's enough.Tutu told us not to talk with outsiders.
```

### [70] hash=`1fa04e01464a6f00`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
Someone had to tell them the truth.I apologize.I didn't mean to accuse you of anything.I was just curious.Well, next time, keep your mouth shut.What could you possibly know about the Nukutai?Everyone, no fighting.I'm Barcarola, the musical director.Is there anything I can help you with?I'll do all I can to ensureeveryone has a pleasant experience.Going on, what do you want?Tootoo!It's alone!Toa, stay back!
```

### [71] hash=`000a93ea3598a305`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
These outsiders can be dangerous!Dangerous?Have you never heard of me before?Whoever you are, ask that you leave us in peace.I...you...Tootoo, think the tides you came...I wasn't sure what to do.So are we going to take Miss Grace's offer or not?She promised it would bring our islands back.Enough, Toa!These outsiders don't need to know why we're here.And stop mentioning Ms.Grace, could draw unwanted attention.
```

### [72] hash=`0b7610e0fdfc286d`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
But what's there to hide?There's no shame in wanting our home back.If we don't stand with Ms.Grace, we'll lose Nukoteao forever.I want to go home, too.Probably more than anyone.I already miss Mellie's red coral reefs, blue sea, and canoe races.We'll get through this, Toa.I promise we'll be neighbors again.baking breadfruit and coconut flowers together?But before we accept Miss Grace's offer,there's a few things that need to be made clear.
```

### [73] hash=`67881516cb641412`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
And remember, none of these passengers are to blamefor what happened to our home.Okay, but Miss Grace has offered us a way home.We'll have our islands back,just as they were our promised land.We will go home, Sloane.Trust me, I just need to figure out a few things first, starting with this wonderfulnew era she keeps talking about.You seem a little on edge, Chief Komoda.Miss Grace, how much longer do we have to wait for this new era to come?
```

### [74] hash=`e938fa24633418dc`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
Many of our people have never left Nukateao before.We're struggling to adjust.Some have even fallen sick.We can't stay adrift on the sea like this much longer.Please, show us another way.Help us like you did when you foresaw the destruction of Mellie.I beg of you.I've already shown you a way, haven't I?You mean...joining the Manus?But the Nukutai haven't had a conflict with anyone for centuries.That's why we hid ourselves away from the world.
```

### [75] hash=`0b31312d95509065`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p6`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（06.群岛已远(在海的另一头，有溢满的安宁与全部的期待。)）

```text
Difficult to persuade my people to do this.All we want is for our people to return to familiar soil.War is inevitable, whether you want it or not, Nukatai.But if you join us, you will have an invaluable ally.Time, the window is closing.The sifting is about to begin.Has it really come to this?To revenge?
```

### [76] hash=`195b0d424e8eca06`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
Regulus, as I'm sure you understand, there's a great deal of effort involved in creating a concertofrom the initial spark of inspiration to the careful arrangement of the musicto the skill required to play it.The fact that any concerto has ever beenperformed at all is nothing short of a miracle.As musical director it is my duty to select theperfect repertoire to bring delight to every listener.Then the esteemed passengers of the
```

### [77] hash=`4595f75006db691e`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
breeze can enjoy their dessert and wine with the finest musical accompaniment oh you can't beserious where's the fun in just sitting there and listening i promise you this lot have hadmore than enough lazy jazz and swooning piano to last a lifetime we need to shake things upmake this voyage the greatest of the century thousand 60s rock and wouldn't you know itThis visionary former captain has a record player right here with her.
```

### [78] hash=`82daa66e7f89d75d`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
Right people, let me hear you cheer.Music is free.It should stir the soul anytime, anywhere.Regulus, I'm the music chaser here, not you.These outsiders seem so full of life.They're nothing like what Miss Grace described.Full of hatred and hostility.This is my performance.Oof.Are you calling me stupid?What did I say?Of course you have no idea what this is.We form palm bark into lampshades about the size of a coconut, then type that to encompass grass inside.
```

### [79] hash=`18143848d631de3b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
We call it Seamothers Eye.Every Nukatai knows how to make one.They're way better than those noisy, buzzing light bulbs.Wait, why are we even telling her this?We need to lower their guard.Huh?So that we can earn their trust if we don't understand our enemiesHow can we help miss grace with her mission and we build our home?Oh?Besides we can't just leave them to shout and run around it'll disturb our people's rest
```

### [80] hash=`ec833de63b630c01`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
Trust me that girl will thank us for this laterAnd then we can get all the information we need from herThen we should make more see mother's eyes and hand them out to the outsiders now you've got itBy the waves, Tutu.You really are clever.No wonder the elders always listen to you.I...Is this really the right thing to do?What peculiar little things.Reminds me of my days on the fishing boat.I always loved spotting the lighthouse on our way back.
```

### [81] hash=`205d52ae39e34a88`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
These look just like...Craftsmanship is remarkable.You'd be hard pressed to find something of this standard in a factory these days.They remind me of the things my grandma and I used to make when I was little.She could even cut up a whistle out of a pot of sniff.They're sharing food and stories, just like we do on bonfire nights.More and more confused by Miss Grace's words.Baccarola?I want to go home.
```

### [82] hash=`b825430888ee77e7`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p7`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（07.音乐或闪光(你愿意用何者填满屋子？)）

```text
Is this one of the changes I must make to truly embrace music?Tatt of the series, we're expecting an increase in turbulence and noise as we work toward the Moffs.Appreciate your understanding.See?What did I tell you?Music works wonders.Anytime, anywhere.You were right, Signora Regulus.You owe me one now.So, how about a little reciprocity?Say, letting me have a rock session on the ship?Do you promise you won't cause any trouble?

Oh, uh, what do we do now?Tutu never said they'd be so friendly.Tutu?Where did she go?
```

### [83] hash=`0287b59523d22476`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p8`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（08.老调子(夹杂着礁石与一小撮海盐的，粗粝的歌。)）

```text
I've learned so much about the outside worldsince I boarded this ship.So, why do I feel even more confused?Hmm, I trust my people.They're good and kind, and they've never lied to me.You just have to look at their spirit shells to see it.The songs and dances of Mellie nourish the shells,and the purity of my people's soulscolor their surface in the most beautiful patterns.Don't worry, it's almost too easy.
```

### [84] hash=`218b8807829698ac`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p8`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（08.老调子(夹杂着礁石与一小撮海盐的，粗粝的歌。)）

```text
Cities are afraid of loud noises.And the Free Breeze has plenty of speakers on board.The sea is with us today.Of course it is.For how long we've sailed its waves?Why wouldn't it be?Get ready folks, port the helm!270, port starboard.Slow down to 5 knots, watch the bow wave.Turn on the speakers.Time to chase off some sea monsters!You ever play the melodica, signorina?No.Don't worry.Anything you play, we'll do.
```

### [85] hash=`6e15ac8a262465a1`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p8`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（08.老调子(夹杂着礁石与一小撮海盐的，粗粝的歌。)）

```text
Can't be worse than what Essam has to offer.I can hear you, you know.I grieve to leave my native home.I grieve to leave my comrades home.Join in!A simple sailor just like meMust be taught and turned in the deep dark seaFarewell to Nova Scotia, the sea-bound coastLet your mountains dark and dreary beFor when I'm far away on the briny ocean toastNever heave a sigh or a wish for meThe world is indeed full of dangers
```

### [86] hash=`1cb002bc5bf62135`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p8`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（08.老调子(夹杂着礁石与一小撮海盐的，粗粝的歌。)）

```text
There is less to fear than you think I'll help you through it.I have to goUnderstand why are they so nice?This is nothing like the storiesCome in timekeeper.I hope you didn't have too much difficulty during the power outageNot at all sonnetto.It actually gave me the opportunity to try out X's latest invention the bouncing bulbIt's very interestingGood day, Timekeeper, Researcher Regulus, Miss Senero.
```

### [87] hash=`c4e27e9eafacc2ea`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p8`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（08.老调子(夹杂着礁石与一小撮海盐的，粗粝的歌。)）

```text
This really the disguise you went with?Wait a minute, Tim, did you know he'd be here?Listen, there's no way I'm paying for even half an extra ticket.In fact, he should be paying for me!Well, this might take a while to explain.
```

### [88] hash=`b25196f5f6f428fe`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
Did you wake up with a glitch this morning Ulrich?The storm has already taken so many lives, and now you're planning to intentionally bring another one upon us?Quit your worrying, Jonathan.The artificial storm will be under strict control, and you're not even on the research team.Besides, there are some issues we still need to fix, so we've come to a bit of a standstill for now.I promise you won't wake up to find the building engulfed by the storm.
```

### [89] hash=`a65c8b5030bac28b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
Sorry, are you saying that you've already started all right?I have to warn you ever since you found that satellite you've been pushing past the limits of Laplace's regulationsYou've accessed materials from other branches used valuable resources for your own purposes and runexperiments without proper clearanceWhat baseless claims Penelope?I'll have you know that everything I've done has been approved by the HQ director
```

### [90] hash=`0c263e03a9869aee`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
Find someone brave and send them into space.He's right.Why don't we just build another satellite and see how it handles the storm?Wow, what an amazing idea!Truly a stroke of genius.So, we're talking about a controlled experiment, right?That means we'll send not just one, but dozens of satellites, all carrying different items.What's the problem with that?Oh, nothing.the budget team will be thrilled at the idea here's a better one we sit tight
```

### [91] hash=`8a281d42a8151138`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
and wait till the storm sends us back to 1995 and bingo surprise there's oursatellite orbiting around the earth once again medicine pocket please mind yourtone in the meeting room oh sure just as soon as they stop trying to wasteall our research funds.I'm with Researcher Medicine Pocket here.There's noneed to launch more satellites.We should be focusing on the artificialstorm project.The project has made substantial progress.
```

### [92] hash=`99f2bc0158c3f98c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
I have collectedevery item that was once on the Regulus satellite, including the spaceseeds from Plesetsk.You have no idea how difficult that was, let me tellyou.It was easier to get Regulus' record.Still, you probably didn'tto steal it Ulrich.You say that but I've heard that it isn't going all that smoothly.Acceleratingthe reaction of asymmetrical nuclide r with fixed frequency sound waves so as to stimulate the
```

### [93] hash=`9a3454a2560b06d2`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
storm.It sounds impressive but what's the payoff?Have you found the key material thatprovides immunity from the storm?Good point Lucas.I never claimed the experiment was perfect.In fact, I'll be the first to admit that it has some serious procedural flaws.Huh?Through 26 micro-scale artificial storms, I tested seven different space seeds, an astronomicalspectrometer, a high-speed photometer, some obsidian crystals, and a Lycopis lucidus
```

### [94] hash=`0bfc1f6426f3e42b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
talisman.None of them endured the trials.Then what do we do now?Just give up?No!But I have used all the asymmetrical nuclide-R that we had in the warehouse.What?!Sit down, medicine pocket!Jonathan, go get some stress ball!No!I can shout all I want, okay, substitute director?The asymmetrical nuclide-R!It's all gone?!I had to use it.It's just standard consumption, like in any other experiment.And I got results.
```

