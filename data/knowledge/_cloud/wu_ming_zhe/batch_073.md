# 剧情图谱抽取 · batch 073

- 角色：`wu_ming_zhe`
- 批次：**73** / 共 1 批（每批 95 块）｜本批块数：**33**
- 筛选：标题含「1.2」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_073.jsonl`

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

### [0] hash=`d01673df155f426c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
Unexpected.For now.Watch out.Nine, eight, ten, D.Cross through the honor of the forest.Two, one, down.What I'm thinking is...Strange.I remember I left it here.Where's the camera?Are you looking for something?So I can help.No one asks for your help.Go away.If you have nothing better to do, I need a place to rest.Yes, sure.You must be tired.Don't worry.I'll take care of it.Let me give you a hand, Anne.
```

### [1] hash=`f3604dbc0f2b1c19`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
That'd be great!The tools are in the closet.This won't take us long.So, you guys are really the investigators from the St.Pavlov Foundation?What is St.Pavlov Foundation?No way!You've never heard about St.Pavlov Foundation?St.Pavlov Foundation is an official institution that takes in and organizes arcanists, Anne.My friends and I work for them.We will try our best to keep everyone here safe.I've never met a real one
```

### [2] hash=`5e1fa091f9654c1a`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
What do you guys normally do taking humans for subject research?Roaming around to snoop on the political parties.Are those stories true?human subjectresearchpolitical partiesPardon me.I don't follow youWe will never do harm to any human.It's strictly stipulatedSave your bureaucratic rhetoric little girlI've read those books.I know you've done some dirty things.Tell me!Shut your face, Michael!I recruited you to play the fool,
```

### [3] hash=`a1a87ef131888faa`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
not asking you to really be one.Don't bring disgrace on us for going to VineState College with you.You're all students from Vine State College?Yes.Faculty of Soul Making.This fool here is a chemistry student.The big guy over there is an art student on English literature and poetry.It's one of my assignments to make a movie during the semester break.So I hired every useless meathead available and travelled all the way to this shithole
```

### [4] hash=`fccfa2c190312e91`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
just to shoot a stupid horror movie.Stupid horror movie?I thought you loved horror movies.Ew!Don't disgust me!Who would possibly have interest in the movies filled with characters in sweatand dust and presenting zero romance or any nice costumes?You mean, you are not interested in horror movies but determined to film one here?You tell me.They are cliched, meaningless, but easy to make.They are the easiest option for this assignment.
```

### [5] hash=`deedfb8b139db830`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
That's it.I've never liked any of them.Oh, I see.That's why you selected this awful script, all these beautiful but useless props, and such an untrained cast.What did you say?Well, I've read your script.It is illogical and dull.The conflicts are not strong enough.Or, we can call it a classic, but in another word, it's stale.I really wonder, how did you get admitted to the filmmaking faculty?The admission criteria for Vine State College should be quite difficult to meet.
```

### [6] hash=`54753de4224624fa`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
Hmm.You!Do you know about your no one but a spawn of the foundation like those bodyguardsmy daddy has?Come on, relax Blonnie.If your dad didn't sponsor the two library buildings, you would not be here studyingfilmmaking.You shouldn't be mean to her.And Jennifer, please don't get into a fight with him.Isn't he your friend?You know friends won't say hurtful words to each other.I don't understand.Is this the way people make friends in the outside world?
```

### [7] hash=`3291f4e2bc6dd0a0`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
I'll knock off every tooth in your mouthand give them away to that crazy teeth collector.This way can your empty head remember how much I hate being called an arcanist.But you are always an arcanist.Although you've tried every means to be a human, it won't change your identity.However much you despise us, many brilliant playwrights are our gainists.Mr.Horipedia, don't make this worse!Quiet.If you don't shut up now, I will shut you all up forever.
```

### [8] hash=`7912e001d460afe5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
Miss Anne has a point.This is not how friends get along.Ladies and gentlemen, we are not here to fight.We need to cooperate.We met by the edge of the woods, as well as Rod, the one that plays the butcher.That's everyone in my crew.Now, if your curiosity has been well satisfied, leave.I need a break.Sorry to interrupt you when you're not in a good mood.Actually, Rod didn't come here.He's hospitalized.
```

### [9] hash=`0ac5bac32fbccd02`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
Do you remember?He's not here?Then who played the butcher?Isn't he another actor you hired?Together with Anne in the town near the woods?No.I've never looked for any other actors.The only new actor I hired is Anne, because she looks almost like a twin to Anna, and Anna is absent because of her stomach flu.Oh, wait.Right.Anna is in hospital because of her stomach flu.Which was a result of that toad bark stew she had with Rod.
```

### [10] hash=`c1fab77153c7f882`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
So Rod was not in the car with us when we left.Holy Mother of God.That is, we've been with a butcher whose identity is unknown to all of us.Checked you!Please get so dark!Okay, okay.Afternoon.1pm.Is that re- nope.That butcher is going to slaughter us.He is truly a cold-blooded murderer.Don't freak out, Freddy.A murderer is not someone you frequently meet.You're not shooting a horror movie.Actually, you are.
```

### [11] hash=`8ca88638b2d88275`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
A giant monster?A fake friend of yours?A sudden nightfall?Anything you're not like a horror movie?Damn it, aren't you being paranoid enough?Do you want the situation to get messier?You, sit down.I will go check the electrical panel and fix it.It will bring back the light and restore your sanity.Negative from me.Those who remain alone in a horror movie never end up safe and sound.If the butcher is really lingering outside the door, you will be his first blood.
```

### [12] hash=`1e9a5dd2def10e7b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
Although you are rude, impolite, and suspected to ancestry discrimination,I suggest you to take someone with you for the sake of your safety.Oh, back off, you troll!He really didn't do that on purpose, did he?What's on purpose?He said and did all the things you shouldn't be doing.We are in a horror movie.His actions are like taking some sleeping pills,putting the noose around his neck and shooting himself in the head.
```

### [13] hash=`eb26a9c42d0456f9`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p7`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（07勇敢者游戏）

```text
It has been seven minutes and 25 seconds since our bro, the Bray, took the one-man mission.I've never fixed a panel before.Can anyone tell me if it's normal to take this long?From my experience in human society, it is not too long.If the device has been drastically destroyed or the maintenance man is not familiar with that model,it will take longer time to fix.This is not unusual.We need to go outside to find him.
```

### [14] hash=`cdb556071b2b278b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p7`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（07勇敢者游戏）

```text
We are not in the human society.Aside from the Bookture, he might confront some other troubles.Sinetta, you stay here with Ms.Tooth Fairy.I will go find Jason with Horrorpedia.No matter if we find him or not, we'll come back in five minutes.What if you don't?Then it means we are not in the kind of horror movie where Miss Fortune only happens to lone wolves.If we don't come back, please evacuate the whole campsite and contact rescue.
```

### [15] hash=`d007de6c724b7c89`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p7`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（07勇敢者游戏）

```text
Jason?Relax, man.Firstly, Lone Wolf disappears.Next, it will be the people who failed to escape.Now we must stick together.At least the rain was the origin of all these weird things.You shouldn't have walked into it.I remember the weather forecast said there won't be any rain in this area today.Like the story of Zeno Youth Force.We are in real danger now.Zeno?Zeno Armaments Engineering and Technology Academy?
```

### [16] hash=`b4185f6d8350ec22`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p7`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（07勇敢者游戏）

```text
You know it?Are there anecdotes about Zeno and the town as well?Live here.This cabin.We're from those weirdos.We're leavingRod can be fake this whole campsite can also be an entire illusionYou guys look normal just like like any ordinary people whom we would possibly run into a place like thisBut then you will infiltratePlease calm down.We've only been trying to help won't be deceived anymore.I will shoot you
```

### [17] hash=`fcf18e4cd2ca7d9c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p7`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（07勇敢者游戏）

```text
Here are the claw marks of the critter.They might be in danger.We need to hurry up.Over here!I found her!Stay still!We're coming for you!Ms.Twoferian Horipedia, please follow them.Senetta and I will handle this.Be careful.This critter is very malicious.Use this if needed.The rain has healed its wounds.It's getting stronger and harder to deal with.May the peace be with us.Oh, it seems to be mi- It should be fine, right?

Oh, it seems to be mixed up.I think it is.Watch out.Oh, bad notion.
```

### [18] hash=`56dfe6f820d2e887`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
Oh, man, did I get pulled into pieces?P-Pieces...Lani!You're awake!I have just given you first aid for the wounds.For now, we will have to wait for Ms.Tooth Fairy to administrate a thorough treatment when she comes back.Don't worry, she's very professional and skillful.You won't feel any pain in the process.Am I in the cabin?Then I'm not dead!She saw me being attacked by the critter and jumped out from the side window.
```

### [19] hash=`7a734aeea7f6e599`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
The butcher, he must have taken in, must be with him.I'm looking towards her.Just like what would happen in a horror movie.It's okay.Here, take my hand.We know where she is now.This is good.We will get her back safe and sound.Okay, I...I understand.New Fairy, you're back.Here is Michael.Then she got lost.According to Blonnie, the last thing she saw was the approaching butcher from the woods.She is in great danger.
```

### [20] hash=`3cdf7c4126b62a24`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
We must act swiftly to save her.Also, we need to turn this cabin into a security base for the upcoming battles.Horipedia and I will rescue Anne.He's a horror movie expert and it will be of great help.In the meantime, you and Seneto stay here to take care of Blonnie and to securethis room.I will take good care of her.Please bear with me for a minute.The wounds caused by critters are prone to tetanus.
```

### [21] hash=`0af0edaf4d01eaa2`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
I need to thoroughly sterilize them.How about some painkillers?Me some!I'm very sorry.I don't have any with me.I'm very sorry for what you're going through, but this is not the typical kind of treatment that we used to receive from her.She would...she would ask us to take the tooth fairies.That is, those golden elves in the glass jar.They're effective in treating toothache and other oral diseases, but also can be used
```

### [22] hash=`edce931ea5d48c85`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
to reduce inflammation, stimulates wound healing, and relieve headaches.Take...you mean...to eat...this?Uh, yes.And it actually tastes pretty nice.Like mint and flavored dried plum.It's...it just looks a bit unconventional.Far as to eat this sh-Please, stretch your legs.I need to sterilize the inner thighs.I'll fling!Sorry, Blunny.You can't eat tooth fairies as a treatment.I can't I?Of course I can!
```

### [23] hash=`cf1ccb56efc96abe`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
I will just put it in my mouth and swallow it with my eyes closed!This is not about you.It is my own rule of treatment.I have specific treatments for humans and arcanists, correspondingly.Through our contact so far, I got to know that you don't consider yourself as an arcanist,and that's why I will not treat you as one.Are you upset about what I said?I owe you an apology.I shouldn't have been rude to Arcanists in front of you.
```

### [24] hash=`bd58dcb5737a2777`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
I know it hurt your feelings.I was not myself.I chose to live amongst humans, chose to be their friends,to be a different Arcanist.I thought in this way I would be taken in as one of them.But as you see, when things come to a critical moment,It is a prescription approved by the medicine examination supervised by Campbell.In this case, it doesn't violate my rule.I could have applied this earlier and spared me the pain.
```

### [25] hash=`607b686c80e85610`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
I don't rely on painkillers.I am an excellent doctor.Minimizing patients' pain is of course my forte.When kids can't suppress their pain, I normally sing for them to ease their pain.You didn't sing for me!Was it because you didn't want to?Maybe.I confess, what you didn't say at first was really annoying.Arcanists and humans almost act as if they were of one merged entity, but we all knowhow lines have been drawn between their own people and the others.
```

### [26] hash=`49c13ad37db15941`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
You grew up among humans, and you learned to look away from the truth as they did.But you do react better to the medicine for arcanists.Their blood is bringing you a good outcome.In another half an hour, your wounds will be fully recovered.You will be able to jump and run freely, as if you were never hurt.However you feel about your ancestry, it is helping you out.My wounds...a good outcome.Tooth Fairy, please wait.
```

### [27] hash=`12c98168364c031e`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p8`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（08太妃糖罐中）

```text
If what Mr.Horopedia has said is true, it's dangerous for us to split up.The three of us should stay together.It will take another 25 minutes for her legs to fully recover.If the situation were to develop based on the rules of horror movies, at this stage,I am safe.Don't worry about me.I see.Have you also done a lot of research about this genre?Not a lot.I just browsed the secret notebook left by Horopedia in the infirmary.

I covered him from the instructors to keep his notebook.Since then, we became friends.But thank goodness you are on her side now, our negligence didn't cause much damage.
```

### [28] hash=`1f110f1f23ff37ea`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p9`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（09最后的女孩）

```text
Hmm.The last girl normally has two categories.Anna is the exemplar of the first kind.Pure, innocent, and mild like a virgin.The second kind is those cool girls.More condescending, erudite, and sophisticated.This category can easily tackle any difficulties and make sensible choices like our mistooth fairy.They are all good girls, approved by society.Therefore, people reward them with the privilege to survive.
```

### [29] hash=`3cce7ec8884c5fce`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p9`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（09最后的女孩）

```text
The critter's claw and the butcher's cleaver will never hurt them or kill them.So what do you mean?I mean, please don't worry.It'll be fine.She is safe.She is particularly safe before we die.But if we lose her, the probability of our death will go up, up, up, up, up, and up.Very comforting.Wait, the carcass of the giant critter is missing.maybe it's not totally dead and has crawled back to its den hmm it was dead
```

### [30] hash=`21cddf6a41fb674c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p9`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（09最后的女孩）

```text
I've checked and there was no way it could survive here in the mud it's thefur oh also what's this a note that's weird hey look it's the butchersfootprints let's follow it hmm the footprints disappear the soil here isless moisturized than the outside so the footprints are barely left theMel, I think I've smelled this before.The key.This is the smell of the key.The moss here is definitely special.We need to take some samples back from this tooth fairy.
```

### [31] hash=`631fc52e8949ecf9`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p9`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（09最后的女孩）

```text
Curtain?It's Anne's voice.She must be here.Anne, can you hear me?Below.The pit is deliberately dug.The soil here is dry and granular.This was originally a cave.She is hidden inside.I see you.Stay strong and take my hands.Burton, we have to get out of here, now!Just as the classic plot goes, this is the right timing.Step back.He can't kill you, but he might hurt you.I will fight along this time.I can't be a burden to you now.
```

### [32] hash=`dc426259ea4015bf`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p9`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（09最后的女孩）

```text
Run!Run away from him!Don't let him catch you!No!You can let go of me, Anne.It's over.He disappeared.Right.I know.Yeah, you defeated him.Like a marvelous miracle.A miracle?The Braveheart?And the miserable death of the crazy criminal killed by his own weapon?This is The Last Girl.
```

