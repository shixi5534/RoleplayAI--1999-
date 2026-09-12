# 剧情图谱抽取 · batch 030

- 角色：`wu_ming_zhe`
- 批次：**30** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.4」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_030.jsonl`

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

### [0] hash=`a55785903489f9af`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
You use a maths model to forecast the storm, and its results perfectly match what the foundation recorded.We just worked out the patterns in the number sequences.Close your eyes, Fertin.Truth reveal itself to you.Truth.Who broke the silence?Saneta is in detention.They're planning to sentence her to death.Those of you who agree to the death sentence may remain seated.Who wish to commute Ms.Senetho's punishment?
```

### [1] hash=`f4d6092fe3f73a45`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Put your pebble into the pots in the middle of the hall.The pure-blood Arcanist community.The unknown Arcanum power.And the obsession with certain knowledge or identity.Sound familiar?I take not thought for needless disputes.There is nothing we can do!We have another ten minute stopsbefore this ship sinks like a stone!Hmm, that sounds like the turbine just cracked.Great, so only two minutes left.Her true captain will never abandon her ship.
```

### [2] hash=`63b2443a45f963f6`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
I've sworn to live and die with Rockin' Apple, the second of its name.Then why is it the second?Sotheby just bought us this ship.I rack my brains to think of all the assurances I could give to get that governess off my back.I think it's better for us to embrace the fact that all things would come to an end, Captain.I have a question for you, Zanetta.Please, standkeeper.Hmm.In the field mission evacuation instructions, apart from the part about asking the timekeeper for help,
```

### [3] hash=`1ad46fe4dd06478d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
is there anyone else we can reach out to for rescue?Er, seriously, Vertian.What's going on now?This is a trap!And you are behind all this!It is you who played that nonsense travel note from 1999,and then blew us into this random sea in order to torture us, afflict us, and now feed usto the f-Go ahead!Give us the wicked villain laugh, you Manus mole!Quit playing innocent here!I don't know!I mean, no harm-
```

### [4] hash=`c82c54ec22828be4`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Nice try!See what else you got to say when this pirate opens your battery cover and findsMaiden Manus there!Please, do not shake me!how about this program lesson 101 the express route to heaven one shouldn'tmiss I think it would serve you better stand this anymore my records my Dr.Peppers my pirate radio my rockin Apple the second if I done to deserve thiswell she did try her best to pick music though no one is in the mood I
```

### [5] hash=`c32c1fd3e9b570b2`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
think this piece is not bad as to regular says question we need toslightly twiddle this knob to 1913.This is the official letter of appointmentfrom the foundation.Congratulations, Burton.After the long evaluation period and the re-examination,the Storm Reformation manpower and disciplinehas been officially approved by the Pax Security Council.Team Timekeeper is now a legitimateindependent department.
```

### [6] hash=`c32f5458a3633c4f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
You are now granted a more flexible autonomydiscipline unregistered Arcanists.The Arcanists who have been and will be assigned to Timekeeper'steam will be put through a risk assessment procedure carried out by the Foundation.Those who are in lower risk categories only need to receive primary artificial sub-nemulismtraining while the high-risk ones will go to the School of Discipline.But I willmake sure they will be registered as members of Team Timekeeper when they enrol.
```

### [7] hash=`e26c9feea0983485`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
I see.I have only one question.Are you still our point of contact for the Foundation, Madam Z?Yes, of course.Then I have no further questions.Meanwhile, Team Timekeeper can apply for secondment from the Foundation, Laplace, and Zeno if necessary.You can check this file for more details.It stays the same.Keep investigating the storm and Manus Van Dikte.I'll arrange for some people to meet you at the base.
```

### [8] hash=`640f6d20523b3357`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
I think you'll have a great time together.The fog is thick here.It used to be the nest of a leety house, a kind of creature resting in valleys withabundant water resources.What's more, it's winter now.I have to be the errand girl.The Foundation wasn't even planning to give me a ship.Miss Tinetto is going through the procedures in the headquarters to transfer herselfto Team Timekeeper.Mastruvus and Sotheby are on a break, for they have spent much time and energy clearing the woods and repairing the foundation's square.
```

### [9] hash=`51a271b3d53e4f50`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Miss Lilia has been given an administrative penalty because she broke into the rehabilitation centre not long ago.This leads us to the current situation, where only the captain and this apple are able to act freely.So in the end was I, the renowned rocking pirate, the only one who didn't cause any damage to the foundation buildings?I have never felt so humiliated in my life!You're not planning on destroying this place now, are you, Regulus?
```

### [10] hash=`f178d7d06629d5ee`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
No, no.Huh?Who's here?Lillia and a stranger?What took you so long?Fell into a gutter?Hello, Timekeeper.My name is Moisson.My employee ID is SF27602191908238X.I believe Madame Z has told you about me.I am now an official member of your team.Miss Morzan, welcome to the team.Madame Z said you're an excellent tutor in Arcanum.She's too kind to say so.In fact, I have a lot to learn from you.Also, thank you for taking good care of Miss Sotheby.
```

### [11] hash=`b377e37562855380`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Hold on, you know Sotheby?According to Madame Z, Miss Morzan used to be Sotheby's private teacher.It is a long story.Let Miss Lillia give us an introduction to the base first.As the field operator, she knows this place better.Huh, after I got promoted and transferred to the headquarters, those exciting outboundmissions have been removed from my schedule.In short, although it's called the base, the only place unaffected by the storm is
```

### [12] hash=`ee539cda783410df`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
a narrow 20-metre-long corridor no larger than a hunter's lodge.My former fellows had already searched this place from top to bottom.Those Laplace dudes had even sent in their lab dogs to search here inch by inch.Found nothing but some excrement of the Aletius and the dog's own poop.There might be some clues that are invisible.Regulus is a specialist in optical arcane skills.Maybe she can find something.
```

### [13] hash=`3b6042c0a39fa7cf`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
A specialist?Well, I'll take that as a compliment, but for the record, compared to searching,hiding treasures is more of a pirate's lot.So, if it were up to me to hide treasuresin this place...Please hold on for a second, Captain Regulus.The fog seems abnormally thick.Lucky you, they hit the jackpot right away.Hmm, there shouldn't be any ambush in this place.Easy, Ms.Regulus.Please carefully retreat to my side.
```

### [14] hash=`2f61330449c093f2`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Ms.Timekeeper, please cover us.You want to offer your seat to the senior?A little trick.Hold on, hold on.It was a misunderstanding, Timekeeper.We attacked to defend ourselves.We are not the enemy.We are the investigators from the Foundation.These are our IDs.The base has been deserted long ago, right?What's the purpose of the investigation now?The outside world has been reversed to 1913.We are here to collect the lost scientific devices from the 1970s.
```

### [15] hash=`50a601d0bec40a14`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Science and technologies are regressing rapidly due to the storm.Those old devices which used to be outdated have become valuable to us.I see.Do you mind us investigating this place?It won't be long.Sure.We are glad to give you a hand if you need it, Timekeeper.Good.I have some questions about the base and I wonder if you may help.So it was just a mistake.Back to treasure hunting now.Let's see what Zeno and Laplace have left here.
```

### [16] hash=`9ccc9008e4fa1bb1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Infrared shotgun.Oh, a maglev auto-feeder.Kato calibrator.Oh my god!And a full box of Laplace's military chocolate!Martin!Come check it out!It's all good stuff!MREs!Ahem.This pirate with a heart of gold wouldn't mind tasting it for you.I don't mean to rain on your parade, but even dogs won't eat those things.It makes Aletia's excrement smell better in comparison.That being said, to the best of this apple's knowledge,
```

### [17] hash=`9056b1c4a0b54960`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Canine animals shouldn't have consumed any food which contains theobromine anyhow.Then can I have it or not?There is nothing to be worried about since the captain is not an animal of the Canidae family.As befits the first mate of mine.Wait a second, Regulus.Show me the thing in your arms.Why?What do you want?Feel like my chocolate now?No, the supply box.It has my name on it.True are there any other vertin in the foundation as far as I know
```

### [18] hash=`9e7d679aac7f3891`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
No one is called by that name, but meLooks like an ordinary wooden boxBut these ordinary boxes are always the most dangerousSo turns out we did find something useful in this treasure huntIt even has vertin's name on it like a celebrity autograph a treasure indeedNo one can stop a pirate from opening her fresh trophy!News of the day.The Outcasts held the 11,231st Pup Rally in the Mammoth Cave, Kentucky.
```

### [19] hash=`7e84aa2457a39749`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
They eventually unanimously passed the principle of dozing in spring, relaxing in summer,slacking off in autumn, and hibernating in winter.Practical modern incantations has now been reissued for the 77th time.We are now at the end of the 20th century.This book still remains the number one book on the list of Most Regretful Purchase onClassic Score by the New Yorker.Biographer Erd has recently published her latest travel notes, Roaming in a Peron,
```

### [20] hash=`deeddf653c2490c2`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
which has started a new round of craze for traveling in the Aegean Sea region.The chief editor of The Voice of the Millennium strongly recommends this book, praisingit to be the literary reproduction of the romantic, elegant, and classical dreams,A glimpse of the golden era.Among them, criticisms abound.The Babylonian review issued a warning that the author's observation of the Apollo Starwas fatally inaccurate.
```

### [21] hash=`73adbbbb4d7c1786`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Self-driving tourists can easily get lost in the Gorgon current backwash if they donot correct their direction by 3.14 degrees on the forward sextant Model T.Time for late night news.What?End of the 20th century?Voice of the Millennium?Is this radio broadcasting news in 1999?Just as I suspected.Since Timekeeper hasn't reported the time of this era to the Foundation,you two, as the Foundation's investigators, shouldn't have known what year this is.
```

### [22] hash=`6b08e16d82a012e1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
In such pouring rain, time is the best proof of identity.Ha!I get it.Not a bad plot.Ms.Morzon!Watch your six!Let us help you!I didn't expect them to be clever enough to disguise themselves as a Foundation's investigators.They sure have learnt a thing or two.The era of 1929 only lasted for two days.The frequent change of time muddles work and responsibilities in the Foundation,which in turn caused some chaos within it.
```

### [23] hash=`d98436770874fd06`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Luckily, Ms.Morzon noticed the signs of it at the beginning.Timekeeper, please take a look at this box.I'm afraid this is what they came here for.This is...the Manus mask they used to stay immune to the storm.I will explain all of these as briefly as possible.Good news.The analysis report on the mask you submitted to the Scientific Computing Center is now available, Timekeeper.We've found the same component in it as the raindrop from the storm.
```

### [24] hash=`a3e41671fe507d1c`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
This is a component named Asymmetrical Nuclide R by the Scientific Computing Center.Its name comes from the bifurcation structure it presents under the Arcanum Imaging.The Scientific Computing Center has also run some tests on the samples of the raindropsyou previously submitted.After removing all water, mud, human hair, and dandruff within, the remaining unanalyzablecomponent is what we called asymmetrical nuclide R.
```

### [25] hash=`8797972f40d9aff3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
What a familiar name.Disappeared right away and we only have a photo of it.Fortunately we extracted the staple form of it from the Manus mask.It might bethe key to staying immune to the storm.Does that mean it'll be possible for thescientific computing center to develop protective gears which are immune to thestorm?Like the Manus does.Seems to be so.A credit to you.The whole center iscrazy about it and I'm responsible for passing along the good news on
```

### [26] hash=`ae9bf008f48e6fa1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
behalf of my fatigued colleagues.They stayed up all night and suffered fromManisfin Dictate always has more information on the storm and how to be immune to it.We've been trying our best to keep up with their progress.Fortunately, now we have another direction.Oh, and these are the files you asked me to search for.Luckily, the SPDM Library has every single issue of global arcane geography since the 1960s.
```

### [27] hash=`5ec710e5d7ab5a73`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Also, Ms.Sotheby accepted your request.Thank you, Sinetto.With these files, and the help of Regulus, that should be enough.What else do you get except for playing dumb, you cunning flower-headed tin box?Speak!Tell us what you know!Like, what were you doing in the Illitial's base?In what way are you associated with Manus Vindicte?And who put you in that box which has Vertin's name on it?No idea.And those ridiculous radio programs, end of the 20th century,
```

### [28] hash=`d1fc479cd33d4d27`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
Voice of the millennium and roaming in a pyrén.Don't waste our time, otherwise we have no choice but bathe you with this bottle of vodka.Geez, do you really mean that?Anything less cruel?Formalin, of course!I never waste my drinks.Yeah, that's more like it.But I...I really don't know anything.The Apollo star we just heard about means the sun.The Ford sextant Model T is an arcane device produced in the early 19th century.
```

### [29] hash=`c0b14358465b10cf`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
The Scientific Computing Center has one of those as a part of their collection.The Gorgon current is mostly created in the Aegean Sea, near the Balkan Peninsula.I remembered an Arcanum magazine in the 1970s, had a detailed article about this,and introduced the circulating current.I read it in the periodical room in SPDM.The current will be flowing backwards every time the Earth is at Ophelian and Perihelion.
```

### [30] hash=`6fe2f8d710735917`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
This is also known as the current reversal, which is on the third day of January andJuly this year, and the time in the outside world is January the 1st, 1914.Are you saying that all those broadcasts are leading us to an actual place?I thought we'd have a nice break after this.Regulus, you're going for a ship, haven't you?I tell you that I've got you one.Now hold on a second.Come to think of it, it wasn't the flower-headed radio thingy who tricked me into the Aegean Sea.
```

### [31] hash=`71732e3d9fa14757`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p32`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜1~4）

```text
It was...Verdin!Watch out!The big wave!Blyat!This is enough!S-U-0-1-V-E!Wait, Lillia!Are you sure about taking off in such stormy weather?this isn't a normal storm something is attacking us from the ocean I need topull it out you guys go study that whatever instruction right now ha ha Ifinally got you damn bastard my turnVDV, how many wins?
```

### [32] hash=`6f52510d99103bd5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Field Mission Evacuation Instructions, Article 21.Whenever there is an emergency, the fieldofficer may send an SOS code with their wands through any transmission device with roundbuttons on it.Any Foundation member nearby will provide immediate humanitarian aid.To send the code, please turn the knob one time to the right, half to the left, andno witness report of the Gorgons since the 12th century.
```

### [33] hash=`95bd86c7572ff578`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
I thought the current was simplynamed after the mythology.Well it's my privilege to have the chance to fight against it, huh?William, Todd, let'ssee who gets it down first!Entities should not be multiplied unnecessarily.Captain, I hope you still remember our foundingmotto.Want to compete with me in speed?Have a try, if you dare.oh you have guts and I appreciate it bring it on speed up my friends we need
```

### [34] hash=`41825633aef8f08b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
to rush back to the Balkan Peninsula for another mission everyone please wait aminute the size of the sea monster it's shrinking what's happening now it'sgone out of sight oh I have a bad feeling about this not good it'scrawling into the cabin it plans to tear the ship apart from the insideEveryone watch out!Your watch was wrong.Pardon me?Your watch was wrong.Are you talking about my pocket watch?
```

### [35] hash=`65231221204dc8eb`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Your watch was losing time so I fixed it for you.I...I don't understand.Do you mean this is the right time?Yeah.This is the year 2007, is it not?You're saying we're in 2007?In fact, 1999 is nothing special compared to 1991 and 1993, however, 999 is a brilliantnumber.It is a Capricorn number, a palindromic number, and the largest three-digit natural number.Sorry to interrupt, but I only meant to ask about Erd the Biographer.
```

### [36] hash=`7afd1b659971f668`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
She'd been here on this island and written a travel note called Roaming in Aperon.Does the name of the book ring about?I am sorry.I have no idea about the fragments of matters you're talking aboutfragments ofmattersCaptain you should go this Apple's arm hasStay with me for a little longerShush you wicked dolphins.Mr.Apple is not your breakfast nor are my recordsIsn't that Vertin?Vertin!Are you done with the standing and staring?
```

### [37] hash=`8341e20a0ece3205`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Come give us a hand!Thank god you are here, Vertin.Mr Apple and I were this close to being made a stargazee pie by these clever bastards and served to the dinner table.You've also been incredibly helpful, Regulus.Is that so?Like how?You rebuild my confidence in communicating with people.Have you seen Sinetta and the others?Please grant us entry to this island so that we can share them.Timekeeper?I'll explain to you later.
```

### [38] hash=`198aefe6883569fd`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Trust me.Please, Seneto.Come this way.We will talk.However, only integers and fractions are welcomed here.No irrational number is allowed on this island.Throw her into the sea!Deadpool!You still look confused.I know, darling.You haven't even vomited up the mouthfuls of seawater you ingested deep into your stomach.Just relax and lie where you are.You don't have to get back on your feet right away.Usually, yes.
```

### [39] hash=`49e622f26ec12bf1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Usually, when those drunkards and patients wake up from a coma, just like you do right now,they only have two questions.The first one will help you find out the name of the land you are lying on,We gotta let the past be the past, like how we deal with old newspapers, because all Ispeak is one simple fact after another.Anyways, we will keep each other company for quite a while.Finally a question about yourself.
```

### [40] hash=`30f4109b3450a32a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
In front of you is a boundless sea.All you can see, besides the beach you are lying on, is water, water, and water.Not even you can avoid asking this question.But a kind-hearted soul already told you that time is moving forward as it used to be.Step by step.So the time is...The year 2007!Yes!Time is back on the right track, going where it's supposed to be.Raindrops literally drop again, and no one goes back to the past anymore.
```

### [41] hash=`1424fbfe7ee5bcb6`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
new money buys one art piece after another to show off their good tastethey don't even mind turning their homes into museumsa cafe named San Marco officially opensgathering the most outstanding intellectuals and writers of the timethey talk and laugh there as if nothing could stand in their waythen the cafe receives a neurologist whose briefcase carries theinterpretation of dreamsAnd celluloid film and projectors become a new means of expression for artists.
```

### [42] hash=`9a1e800ec5b191e3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
At this point, helmets remain intact in the warehouse.Gauze only works in hospitals.Bullets only fly in the firing range.And the flame that swallows lives is not even lit.But soon, soon enough, the young people who swore to retrieve their homelandwill take up daggers and guns to fulfill their oath.Buildings will shake like a leaf and rocks will fall off and hit the walls.Screams will try to break free from people's throats.
```

### [43] hash=`cefa183a8bf95b17`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
And at that moment, a clip will be loaded secretly in the name of supreme honor.The golden age is about to end.A vortex of blood is already swirling in the river of time,waiting to devour everything that passes by.When that actually happens, all the beautiful curves derived from nature, the B-shaped brooches,the punch, the eiderdown duvets, everything will be destroyed, leaving only an insurancecontract behind.
```

### [44] hash=`9c88b3ee2c1a8071`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
And it doesn't even work.Even this cafe will be smashed into concrete pieces.See?We have combed the hair now.Everything I just talked about is the time you want.You wouldn't buy the nonsense about the fairness of time when you reach my age.It actually feels different between those who keep their eyes shut and those who keep theirs open.Likewise, those who kill never share the same feeling with those who are killed.
```

### [45] hash=`69dbf06d4dddc334`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
This is also true between those who have enough food to eat and those who are starving.Alright, that's it.I've talked enough.It's clear then.Real numbers refer to arcanists, and imaginary numbers mean humans.Then what is the rest of this nonsense?Seneto, Vertin and this apple are integers.While Miss Lillia and I are fractions.Don't bother asking, I'm pure blood.This apple is also made of pure apple juice.
```

### [46] hash=`db37d427779afc7c`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
I only consume 1.5 volt DC.We are prisoners in the world, and our body is the cage of the soul.Oh, cut me a break.Might as well play us some rock music.Seems the residents on this island venerate integer numbers.And irrational numbers, or the non-terminating, non-repeating decimals,cannot be represented as the ratio of two integers, hence they are discriminated.Oh no no!Who are they to judge and decide me to be the irrational number?
```

### [47] hash=`d396fd008672a43b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
I was the only person who didn't cause any damage to the Foundation in the previous protest!Why do I get to have the worst of both worlds?I've requested information from Ms.Moson about Epiron, but it will take some time for the files to come in.The captain of the Razor Special Operations Squad told meThis might be a settlement of a group of Arcanists who have been long cut off from the world.Unlike other unregistered Arcanists, these people chose not to live alongside the humans.
```

### [48] hash=`f3a4725ff6963d7f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
They still lead an ancient Arcanist way of life and follow the old customs.We must be meticulous when getting in touch with them.But they used modern mathematical terms.And that girl talked about Caprica.He was an Indian mathematician active in the first half of the 20th century.I think they are not living in complete isolation.They are still in contact with the outside world.This place wouldn't be affected by the storm, just like the Illitial base,
```

### [49] hash=`1abd24861ae76147`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Foundation headquarters and my suitcase.The travel notes in 1999, Manasvindipte showing up in Illitial's base.The storm, or emanation, they must be somehow connected.And we'll find our answer here, I think.Very energetic, Kapitan.By the way, how come nobody is here to welcome us?They wouldn't suddenly decide to detain us all just because we have an irrational number here, right?I'm with you all the time.
```

### [50] hash=`ac2f869e90ec32d7`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Six asked me to welcome you.Scared me again.What were you doing hiding in the corner?Because it seemed you were in the middle of proving a conjecture.According to the scripture, disturbing others when they are giving proof of their arguments is as sinful as eating beans.snow peas, chickpeas, and what does it say about other bean-based products?Beans are beans.You're funny.This doesn't even make sense.
```

### [51] hash=`c19fe80f6d661094`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
By this logic, aren't the coffee drinkersgoing to rot in hell?I happen to have a box of coffee beans in my bag.If I put one coffee bean in my mouth, will the vulture get me right away?No way!Whoa, easy mate.Do you want to get physical?This pirate is not scared of you.The creatures are coming to your aid this is not good.We need to separate themWhat is going on here37 let go of the guests head nowSorry that I'm late.
```

### [52] hash=`ecc0dbd6dce0e44f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
I'm Sophia the corrector of a p-run.I will take over from here.OhFinally we have an ordinary person herePlease let's talk on the way to the outsideWe believe everything can be translated into numbers.Things are made up of numbers, and mathematics is the key to opening the gate of truth.It is like the fire that lifts us from the darkness.This world may decay in time, but numbers will transcend the limit placed for all
```

### [53] hash=`cb396cf4a86cc7a4`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
other things in existence.And if one can take up the challenges and improve oneself with practice, they mayIrration numbers are disobedient, sometimes unreasonable, and they hardly play by any rules.Just like the non-terminating random numbers following its decimal.These numbers are the floating points, or the noises.People of this type are the random ones whose actions show no pattern whatsoever.
```

### [54] hash=`4859c69ef1809fcb`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Disobedient, unreasonable, never played by the rules.Do not sleep on a grave, and do not cut wood on a main road.Idleness is the cause of the breakage of one's flesh and soul in the long journey of perfectingoneself.Those who have not yet found their numbers have even fewer excuses to be indolent.Besides, why would you place the head of a ghast in your mouth?She said she's going to eat beans.That does not justify your action.
```

### [55] hash=`551350b089081dbd`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
Come to think of it, is she safe to bite if she had consumed the beans?Wouldn't that make you the bean eater as well?The right way to deal with this is to throw the offenders into the sea, let the gorgoncurrent take them and confine them in the ever-repeating circular motion.This is the most optimal solution.How come you didn't think of it?This is one of the most basic set problems.Uh, hello?Are we done with the chit-chatting?
```

### [56] hash=`89a562323d332ad4`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
conspiring to my face to throw me in the sea.Mind you, this pirate's tolerance haslimits!Right in the bullseye.What's that look on your face is?An eye for an eye,a tooth for a tooth.I didn't start this.Regulus, did you just pick up thegrape that 37 threw at you earlier from the ground?Did you just violatethe rule of not to pick up what has fallen?What?Axis incoming!It will take the offenders with it!
```

### [57] hash=`516d435e5cb51892`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
A chicken's head and two snakes as a feat!What?What on earth is that?This is not good.They seem dangerous.Regulus, come to my side!How dare you!Captain!I can't leave her alone.This apple shall follow her.A toast to Regulus.To her ever fighting spirit of breaking away from jailsNo matter how many times she has been put behind bars.Luckily she didn't have any beans.May her soul be cleansed in the dungeon.
```

### [58] hash=`aad43514dee9ecbf`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p33`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜5~8）

```text
What a mess.In the F.T.Gromot Mima,se matizete o tan eno sume Dio semia.Did you see that?The arcane skills cast by the congregation on this islandare very different from those we have seen.Mr.Apple is with Regulus.She won't be in danger for now.Let's follow Sophia.We have wasted too much time on unnecessary matters.Ms.Fertin, this is the place you've journeyed to visit,the Hall of Epiron.This is where we share our knowledge of Numa,

which is also the storm you've been referring to.
```

### [59] hash=`98a9ceb28815e8c4`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Before you enter the Great Hall, please place your right palm on the stone and swear toit solemnly.I wish to be baptized in the water of Gnosis and be rid of the long darkness of ignorance.I ask my tongue to be taken for it has spoken mindless words and I shall stay silent forthe truth.I choose to leave the fragments of matters behind me and enter the Great Hall of Formsclean as a newborn.I swear to let matters stay in the world of matter, and a form in
```

### [60] hash=`c12ed357e58e8537`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
the world of forms.I swear to reveal no secrets, or my heart shall be taken by the vulture,my body consumed in flames, my soul trapped in the endless wheel of birth.Now knock three times on the stone.Put on these ceremonial dresses.That'll be all.Remember to enter the hall from the right and leave from left.You are thehumblest audience here, hence not allowed to speak.Please stay quiet and keep the
```

### [61] hash=`d62de5c5cd151141`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
secrets you heard at heart.I will arrange your meeting with six after this.No problem.Miss Sophia, could you give us some privacy?Please enjoy.I havenothing more to say.Verzin, are we really going to do this?That oath weto make to enter the hall sounds vicious.To stay quiet and keep the secrets, it's similarto the training we once received.I can go inside on behalf of Timekeeper.No, I'll come with you
```

### [62] hash=`d5ef8e0bd3165275`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Seneto.I can't sense any sign of arcane skill on this stone.The oath is more of a formalitythan a curse.The warning is lifted then?But when Sophia repaired the floor in front of usWe know nothing about it.It's too perilous, Timekeeper.I know, Zanetto.But as long as we obey their rules,we won't get into other trouble.The doctrine of the Aperon is to live in solitudeand seek nothing but the truth.In fact, they've never been
```

### [63] hash=`db8e2076129b80bc`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
aggressive towards us.I think of this differently.Think.The pure-blood Arcanist community,the unknown Arcanum power,and the obsessionwith certain knowledge or identity sound familiar yet we haven't spotted anytraces of the manners here Maynus vindicte is like the rat living in thegutter I don't think they will let go such a favorable chance which means weneed to find out the truth I believe in timekeeper I have zero interest in
```

### [64] hash=`962a6a3a55339cee`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
this meeting I'll stay outside to keep a lookout take care I wish to beAll my heart shall be taken by the vulture, my body consumed in flames, my soul trappedin the endless wheel of birth.Fellow brothers, sisters, our quest for Gnosis had suffered three unprecedented crises.First was the discovery of irrational numbers, and then the creation of imaginary numbers.Last was the loss of the grand unification of different lineages.
```

### [65] hash=`db3cf03c11131bc8`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
The truth was buried, and history was rewritten.But the emanation is not a crisis.Instead, it's our last salvation.The supreme existence has once again shown itself to us.The door to the everlasting, transcendent world of forms has opened once again.As Numa pours down, things are rewound to the world of light.Everything in the world of matter breaks into pieces, for they are as delicate as a petal before it.
```

### [66] hash=`37002beabba16507`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
We, who have the honor to witness the emanation of Numa, have the privilege to survive the turning of the Wheel of Birth.Because we know the truth, our survival is destined.It is the beginning of a mission to bring the Unseen Truth into this world.Thank you.The next orator is 37, our smallest irregular prime, and the brightest star of Hermes.The emanation in 1929 only lasted for two days.All methods to calculate the Numa emanation failed.
```

### [67] hash=`a2ac7fd142819f39`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
We found no pattern in the occurrence of time reversal.All our efforts in the past four years have gone completely wasted.That's the end of my speech.Reña sereno, intenso, e infinito.Who did that?Who broke the silence?Sorry Timekeeper, I just...Get ready to run, Snetto.The Abraxas are coming.Do you want to offer your seat to the senior?How dare you?I win.Can somebody tell mewhy I constantly get locked up ever since I've known Vertin?
```

### [68] hash=`969b39bd9f0ead44`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
First locked up in a suitcase, then a foundation cell, now this!What else could it be if Vertin weren't the jinx?You got the wrong person!She is the most irrational number here!I'm knocked.What does it say here?Freedom will be granted once the proof is completed.That's to say, I have to prove myself not an irrational number to get out of here.Which is exactly what I've been trying to do, isn't it?
```

### [69] hash=`680c49a95611e2e0`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Rat!Captain, maybe you're in the wrong direction.This apple presumes that thefollowers on this island have a close connection with Pythagoreanism.Pythagoras?That ancient Greek mathematician?The guy who saidsomething about the opposite side of a right triangle?Isn't he the guy wholives in some time BC?Maths is only a part of the Pythagorean'sachievements but from a more universal perspective they are a mysterious group
```

### [70] hash=`27d06c48c3fe61cf`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
of scholars.Believing things are made up of numbers, venerating integer numbers, abstainingfrom beans, and the religious collective lifestyle.These are all pointing to Pythagoreanism.The earliest Pythagorean school perished because of the discovery of irrational numbers,which explains their odium of it.At that time, a deviant student named Hipposusdiscovered root 2, and the theories based on the ratio of integers they hold dear were
```

### [71] hash=`9003045e35047501`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
up-ended.Hipposus himself was drowned in the sea.This apple assumes they see the integers as the standard of virtue, and people canincrease the number they rank through study and self-improvement.Besides, they are convinced that a numerical code is hidden in everything and everyone.Whoever can solve the code can obtain the truth of the world.Now I know what's going on.This pirate has had enough of this moral standard, which is obviously prudish, backward and lacks
```

### [72] hash=`cd7d43e36ec27cd5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
humanitarian spirit.I'm going to tackle the root cause of this misfortune.Why am I not surprised?The captain quickly gives the sufficient and prerequisite condition to prove herselfan irrational number.This apple may be able to offer some help.An earthquake?All Abraxas are flying in the same direction.Is this their habits, or?Sofa!This place has made the London Juvenile Detention Centre a heaven on earth!
```

### [73] hash=`89bd7c41bbd7ca8f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Is there a piece of paper?Did one of the Abraxas' drop this?Strange.The unsolvable puzzle.Is this a math problem?0.4, 0.7, 1, 1.6, 2.8, 5.2, 10 and 19.6, 8 numbers in total are listed in this order.There are 8 symbols below, respectively representing the Sun, Mercury, Venus, Earth, Mars, Jupiter,Saturn and Uranus.Maybe it is a hint that we should fill the symbols in the blank box after the numbers.
```

### [74] hash=`5fa5da48718cb039`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
That sign says to complete the proof.Does it mean to solve this puzzle?How unsolvable can it be?Clearly each of these eight numbers should represent one planet.We can easily find the missing planet by trying them one by one.And our Mr.Apple here is the king of the times crossword, yes?I think there is a difference between this and a crossword.In this apple's humble opinion, the ratio of certain numbers should match this number sequence, such as the radius, volume or rotation period.
```

### [75] hash=`ee8792b9eef16e2b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Wouldn't the Sun be absurdly large if these numbers stand for their sizes?The underground critters are back!Don't touch my notes, it's not your food!Hold on please, Captain.Seems like the critters are trying to tell us something.They are pointing at the sign of the Sun.Is that so?Even the critters on this island know math.The sun?What if the sun is just here to serve as a reference point?I read an IAU's report in The Times two years ago.
```

### [76] hash=`110e4716e7567e0f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
You know, the International Astronomical Union.Earth's average distance to the sun is approximately 93 million miles.As for Mercury, the average distance is 36 million and Venus 67 billion miles.Let's say if we take the distance between Earth and the Sun as one astronomical unit,then the distance between the Sun and Mercury would be approximately 0.4 units, and Venus0.7 units.There you go.These numbers are the ratio of the average distance to the Sun to the Earth-Sun distance.
```

### [77] hash=`04cdf08b7ba55515`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
The average distance from Mars to the Sun is about 142 million miles, Jupiterabout 484 million miles, Saturn 886 million miles, and Uranus 1.786 billion miles.By rough calculation, and if we round the results to one decimal place, Mars wouldbe 1.6 unit, Jupiter 5.2 unit, Saturn 10 unit, and Uranus 19.6 unit.That's weird.All these numbers one can hardly remember have become so clear in my mind.But if these numbers stand for the ratio of distance, what's the planet for 2.8?
```

### [78] hash=`8daf9cc6c7ed3186`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
There's no planet between Mars and Jupiter.If the sun is the reference, we will have one planet missing here.Is it really a puzzle unsolvable?Nothing is unsolvable.You are looking at the solution!There must be one planet out there, unknown to us as of yet, located between MarsIs the universe truly arranged according to this sequence?The ultimate key of everything!Regulus!What are you doing?Got food poisoning after accidentally eating one of those critters?
```

### [79] hash=`d2b40f8c11f77c22`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Odd.My head hurts.What was that?I'll make it short.Stanetta is in detention.They're planning to sentence her to death by giving her the poisoned wine.Hey, what?As you can see, this school on the island lives in a box made by the truth.Even if they have a donut in their hands when they are hungry, they still see a topologicalspace.Like the cute ring attached to an initiation toy.It's not food anyways.
```

### [80] hash=`cf5758ec0a1f1be7`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
But if you give them a puzzle, they will enjoy it like the best Kaiserschmarrn.Oh, my apologies.found the answer to the stars for us the young man firmly believed that themovement of the stars and the Sun follow certain laws just like how the delicateyears in a watch work together and his point was even proven correct by Zeushis grandfather when another gentleman observed the sky through thereflecting telescope he took great pains to make a celestial body was
```

### [81] hash=`5b9fd9de9634010e`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
I forgot that you are one of the boring people from the modern times.You need to understand that we are talking about a forgotten masterpiece from the 18thcentury.Back then, everyone still believed that the imaginary creatures living on the starsgot to witness the birth of God's creations, and the ever-lasting temperature changesup there were set to punish the exiles.Oh, how romantic.It was a beautiful dream, but it was still ended, eventually, by another discovery.
```

### [82] hash=`d924e070bc3b65a8`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
The eighth planet.Not the Ceres, nor the Uranus, but a new planet.People found it through more precise astronomical data and calculation, proving that the numbersequence found by the merchant's son was only a myth.Now we are clear of what we've been talking about.It's an unsolvable puzzle.It makes no sense from the very beginning.We found the Ceres because it happened to be there.It is real, and no one can deny its existence.
```

### [83] hash=`4ad7feb1939c9875`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
In other words, we can perfectly prove the rationality of mathematics because we invented it.It's been a good dream, I suppose.now imagine that you are walking alone in the darkest valley ever trying todrag your fragile body upward as much as possible before it is worn out horsecries squeeze their way out of your mouth to ask for a response from thegods suddenly an afflatus dawns on you the next moment a miracle happens you
```

### [84] hash=`d31ee8c0c2d495b1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
You are already at the top of the mountain, witnessing the rise of a huge celestial bodyfrom the skyline.Even if it's only in your imagination, you have just witnessed the dawn of the creation,and the shock is real.An old admonition is engraved here.Let no one ignorant of geometry or the irrational numbers enter.you're right 37 but people always tend to believe that virtuous people areintegers that is what we call belief correct but not entirely correct
```

### [85] hash=`17863c75b7347741`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
everyone can make mistakes numbers are just numbers they are not associatedwith virtues unlike me you're always right 37 I don't know what differs usOf course, I don't want to miss the chance.What chance?The chance to see your numbers.There's no greater knowledge than the knowledge of oneself.And there's no more exciting truth than the truth of oneself.I can quickly tell which types of numbers you are, but it requires proof to know
```

### [86] hash=`4ab6b658ab90d0ac`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
the exact number of your soul.I want to know the answer before you see your own numbers.So it's 37 who proves it, not Vertin.I'd be glad to give this chance to you.That's boring.Let's go, Vertin.The assembly's about to start.Don't worry, Timekeeper.I'll defend myself.Back in the Foundation, I once won a public debate of a similar nature.This is my duty.I won't let it get in the way of the team's investigation.
```

### [87] hash=`449021f1ecaa4ac6`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Sonneto.By our tradition, Ms.Sonneto will be given the poisoned wine.so she will be muted and stay that way forever.However, Sophia raised her objection against the decision.After giving the matter some discrete thought,I have decided it is necessary to hold an assembly and take care of it democratically.Those of you who agree to the death sentence may remain seated.Those of you who wish to commute Miss Sanetto's punishment,
```

### [88] hash=`7baee1e3c24496dd`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
please put your pebble into the pot in the middle of the hall.Now, Ms.Senetto, Ms.Vertin, you may defend yourselves until the sand in this hourglassfalls to the bottom.I am Senetto from St.Pavlov Foundation.I wish all the honorable audiences here would lend me their ears to hear my defenseas a humanitarian gesture.What number are you?Defendant of Court requires an answer.What is your number?What?Me?
```

### [89] hash=`87b5957ef02ab6d4`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
No, I don't have a number.Don't waste our time.People without a number cannot stand in the hall of truth.All her words are void.Sentence her to death now.Forty-two's argument is valid.Defenders, what do you wish to contend?What?It's valid?Objection!According to the record, the last time we inflicted severe punishment was in 1980to a visitor who ate beans.He ate a carbuncle that feeds on beans.Then he was sentenced to death according to the said theory.
```

### [90] hash=`e3d9af108d3aef5d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
In our scripture, eating beans is the most evil sin,which undoubtedly fits the most severe punishment.If we are now executing people for breaking the silence at the assembly,how would it reflect our attitude towards the consumption of beans?Has the latter become less sinful?I suggest Seneto's punishment to be commuted.A good argument.37's argument is deemed valid.The debate will continue.Objection.
```

### [91] hash=`082cf9f0f534edfb`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
The punishment for eating beans is to throw the offenders into the Gorgon Current,while the punishment for the Silence Breaker is to drink poisoned wine.Among all the punishments we have, there's no other punishment more dreadful than being thrown into the Gorgon Current.Because eternity and infinity are the two things we have the least knowledge of,which makes them the most ghastly punishments among all.
```

### [92] hash=`4ae295ef48535694`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Giving her the poisoned wine doesn't make the consumption of beans less sinful.Her argument is invalid.Objection!The crimes would fall into the same categoryif we are taking the punishment as a frame of reference, which is...Objection!The two crimes in question are not commensurable,Which makes your comparison invalid.What's this?Lost in this additional debate?I...I see.So that's how it works.Timekeeper?
```

### [93] hash=`fe9757cfb67e090d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
I will help you.Look at my back.I'd like to start by quoting 42's first argument.People without a number cannot stand in the Hall of Truth.In that case, it's not possible for Sanetto to commit a crime in the Hall of Truth.Because she can't even be in the Hall.What?Oink, Vertin.This is our chance to out-argue them.These are merely clumsy sophisms.We've all seen her break the maxim.Objection!What you see cannot be submitted to the court as a transcendental fact.
```

### [94] hash=`1650cf4ea71b1bf5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
It's nothing but the fragments of the phenomenal world which can't be used in your argument.Objection sustained.Please, ladies and gentlemen, keep the debate logically consistent.Since Senato has no number and a person without a number does not exist beforethe truth, Senato thus didn't offend your truth.She didn't break any rules.Rejection!The rule breaker has a number.We can all tell that she is very
```

