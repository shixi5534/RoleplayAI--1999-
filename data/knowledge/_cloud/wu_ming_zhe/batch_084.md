# 剧情图谱抽取 · batch 084

- 角色：`wu_ming_zhe`
- 批次：**84** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.7」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_084.jsonl`

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

### [0] hash=`792527608e4b2c32`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
Look at the mirror.This is a private session.Your secrets are safe with me.Now, what do you see?I can see Akane's arcane skill, the maze of mirrors.Look at them directly, miss.They'll reveal your deepest secrets and desires.Illusions, Marcus.Just break her arcane skill and get out.Do the only thing I can do.Great.I see her.Behind these illusions, but which one is real?Candy, you see through the illusions, or was it pure luck?
```

### [1] hash=`8fc024df9ab87416`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
She can move through any luck.I need to be sure.I'd be disappointed for it to fluke.Wanna watch the aerial stunts?Candy, everything a book.Everything can be read.These reflections are merely distractions.Candy, the page of truth.Oh, it's true.You saw through the illusions, as you saw through the pistol.Alright, enough of my tricks.What a pleasant surprise!How does your skill work?Let me see.No!Out of here!

Uh-oh!That went smooth.Exactly.
```

### [2] hash=`391e9a81a7b75317`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p9`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（09.门与门之间.1/7 15:46）

```text
The reflections she created were real enough, but not perfect.The reflections had neither shadows nor breath.Most importantly, they didn't have her passion and subtle movements.I read the truth from these details.She meant me no harm.Maybe it was just a little trick she was playing.But I...This is...That was...I knew it.Your arcane scale is incredibly unique.It's a new academic field is opening its doors to you.
```

### [3] hash=`50f9cdc78f8691c6`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p9`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（09.门与门之间.1/7 15:46）

```text
Let's go inside.Oh dear, I forgot your tea.Gosh, she's bubbling like a parrot.It's Madam Hoffman.Ma'am?The spider tail has shown me your direction.How did you get that far?What is that place?An arcane fluctuation?Went to target Miss Kakania in her clinic.I'm safe.Investigations going well, ma'am.Stay where you are.I'm on my way.and to keep the world safe and orderlytill this day we continue to strive for this goal.
```

### [4] hash=`4b6ee17f6efc0d6c`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p9`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（09.门与门之间.1/7 15:46）

```text
My sympathies for all that is happening.We could have been very good friendsif you weren't working for the Foundation.I know you meant every word you said.I can see how you burned with passion.The Circle was founded for the same reason,but I will not change my view on certain things.But on second thought,Welcome to the circle!Chico!Thank you, Miss Kakanya.Exactly.
```

### [5] hash=`4b3fc4d4422183ec`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
A painting?Based on the mysterious island?The hostess Isolde?The opera singer?Oh, poor thing.Every member of that family met a tragic end.And now her brother, Teofil, has left us.Behold, my late brother's final painting.Inspired by the Golden Isle.The salvation.Miss Dittestorf, I know your brother's death has affected you deeply.Doctor...You need to release your oppressions.The rain.The Golden Isle.
```

### [6] hash=`c343edf7323be73d`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
The island of the painting.Is that where the timekeeper is at now?How did Tailfil know about the storm and the island?He belonged to an organization called The Circle.It's the symbol of The Circle.Are they really just a group of artists?What do you see, Inzimir?Welcome to the Circle, Miss Marcus.We share the same dream as you.I am intrigued by the name of your little group, the Circle.Even if the world ends tomorrow, we still have a show to watch.
```

### [7] hash=`3486e436954e2ef7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Please, enjoy.Hey you!Yes, you, my hurried child.You rush through the street like a cyclone.It is a great honor.As we can see, dear friends,the era of science has arrived.The era of man has arrived.Today, we will share the honor of witnessingthe advancement of technology,its contributions to medical science,and even Seville.Now please allow me to introduce the patient again,Miss Isolde von Dittelsdorf, this lady has selflessly volunteered for the experiment and in return will receive a healthy mind in no time.
```

### [8] hash=`66072a23a8d02947`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
She's been living a miserable life due to hysteria.How terrible it is for a young woman like her.As we all know, mental illness is taking an increasing toll on our country.Even suicide has become more rampant.The tragedies are piling up and our dearlady is in excruciating pain as we speak.Thanks to the development of medicalscience we can again be rescued from the abyss of pain.As I said before the
```

### [9] hash=`c59c95347a73fa95`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
electroshock therapy uses the most advanced technology available.TheYou know what?My uncle works for the police.He showed me the autopsy report.The truth is, TFL shot himself.He was killed by a bullet.Good thing he didn't have to suffer all that pain before he died.Poor boy, he was so talented and handsome.Oh, she's less fortunate.Fainted at her only brother's funeral, didn't even get to see him one last time.
```

### [10] hash=`c411c0a2fc85eed9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
I hope the latest treatment will alleviate her suffering.Lunatics!The whole family is a bunch of lunatics!Manner, sir!This is Vienna where we call these poor people arcaneists.I sincerely hope that Isolde can put an end to her miserable nightmare.After all, she is one of the most talented opera singers in Vienna.Just like her mother.principles are the same as that frog experiment, huh?My treatment is supported by systemic series and reliable references, and it is approved
```

### [11] hash=`1f56b1cda842f729`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
and sponsored by the General Medical Association, which means it's reasonable and legitimate.Well, you are, correct me if I'm wrong, a social activist known for her little arcanetricks, Miss Kakania.Or should I say, Miss Clara?As far as I know, you don't even have a medical degree, besides your so-called art movement.This secession, is it?It confuses me, really.Anyway, in order to have a more professional conversation, I suggest we talk later.
```

### [12] hash=`5b338d1cca312547`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
You know, after you get a medical license.No, Dr.Schwartz, this conversation has nothing to do with my personal identity orexperience.The experiment is conducted under mutual consent.Your objection is of no use, and it is even harmful to the patient's interests.Be always welcome to bait.Since you question my methods, please be my guest and indulge us with your thoughts on her condition.As I understand it, Mr.
```

### [13] hash=`79f77181747568ac`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Sigmund Freud published his studies on hysteria in 1895.He believes that hysteria was a psychological disorder caused by problems in the nervous system.It was not a simple organ disease.His trauma theory explains that the patient's personal life experiences were the real cause of the disorder,affecting the patient in subtle ways.It makes much more sense to analyze the patient's traumas than to harm their body.
```

### [14] hash=`4221da69700b83d7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
As to whether his theory is advanced enough, you can read the Totem and Taboo, which he published last year.What?Freud.The man who told people to marry their mothers and kill their fathers.The one who couldn't get a verdict when his patients spewed insanity.It took him 17 years to become a professor, for God's sake.Miss Clara, I've tolerated your immature antics, and I always welcome advice andopinion, as long as rational and reasonable.
```

### [15] hash=`5b91fad03f50fcc1`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
However, funny enough, some people prefer the pain.It ends faster than a hard talk with the doctor.Move!Shoot, are you blind or did you hit me on purpose?I don't control this thing.It always drifts on my bed at night.I just sit back for a week.Just remove your brain.Problem solved.Oh, I didn't think of that.Thank you for your advice.You are so sweet.Oh, you're so welcome, pal.I'd wet my eyes more often if I were you, just do something to get that black snot off those lashes.
```

### [16] hash=`53284ead8fbb12bb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
The good news is, the persons in charge of this place are all dead.The bad news, the one in charge right now, is not a person!Hello, Researcher Medicine Pocket.Your meal allowance is being deducted to pay for door repair.I don't care, Buckethead.Do your worst.A few pennies don't bother me.You could have called me from your lab terminal.The technology department has equipped every researcher with the latest communication device,
```

### [17] hash=`0de16f8ef23d3e23`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
and I have the energy to communicate with everyone.Then how am I supposed to know whether my report is lying in your trash or not?Oh please, you know we gotta talk face to face to solve our issues when things get ugly.PUNGRATS on the one and only achievement you got from the Manus Mask!We're now fully aware of its side effects, and this great achievement is filling the halls with oil and insanity!
```

### [18] hash=`998a7cb17a678286`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
You should thank the hatted cuckoo for her report.No one's turned into a crazy monster yet, or the Manus would be attacking the headquarters from Laplace right now!Dammit!What are you doing?Are you even listening to me?My apologies.You said we needed to talk face-to-face.If I understand it correctly, this is your number one request.You always carry a face in your pocket?That's just...great!You are welcome.
```

### [19] hash=`2470d4266836a30a`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
It is our duty to learn and meet the needs of every researcher.This will help them reach their full potential while respecting the nature of their being.I received some letters of complaint.They asked me to develop a better sense of humor.They said it would help me understand the researcher's sarcasm, so I am studying it.75% of the complaints mention they did not want to see a face on my head.Some even use strong words like,
```

### [20] hash=`1d1c96f3b94f5316`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Never let me see that face of yours again.I am glad that you are one of the other 25% Researcher Medicine Pocket.You know what?I don't mind if you keep that face on.As long as you let me kick it around a bit.Regarding your second request,I have read your report.I fully understand the side effects of the mask as well as the feasibility of the decryption.Then what's the point?It's like trying to get the syrup formula out of a Coke can.
```

### [21] hash=`88b264a2d399dcd9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Ugh!Again, we are all screwed without the original ritual from the Manus!It is too early to conclude that the mask does not contain important clues.The attempts we are making are very necessary.Besides, the situation in Laplace is not as bad as you say.The side effects are completely under control.The subjects are only suffering from dehydration and mania.Fortunately, the rehabilitation center has extensive experience in dealing with manic
```

### [22] hash=`1c4f086b22ce2b3d`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
patients, and some researchers, like yourself, are already manic without putting on the mask.So the side effects will not affect them much.S!Ball pens!Ball pens love brains!Extensive experience, huh?That is right.I am glad you have noticed our efforts.We have prepared a large amount of polymer materials in case of minor vandalism by the patients.Ha ha!Amusing.So this is the logic of a machine, huh?
```

### [23] hash=`d563f9b700b113f4`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Humans are as expendable in the lab as glass.You should be glad that your head is harder than my teeth, alright?Your opinion surprises me, researcher medicine pocket.There is a big difference between the human body and glass.As for the original ritual, you are not the first researcher to make this suggestion.We are fully aware of its importance.We have dispatched investigators and members of the field agent administration to investigate
```

### [24] hash=`850afbf4ff061a95`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
various regions.Here are the images they sent back.Field...what?Field Agent Administration.If you have not heard of the name before, most prefer to call them the History Guards,given their function.Right.That team of cannon fodder.The thought of people being thrown around like garbage makes me feel lucky that I'mjust a piece of glass.Looks like face-to-face conversation does solve problems.Finally, we're getting somewhere, aside from the insane colleagues running amok.
```

### [25] hash=`97c639c6a3134bdb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Let me guess, the blue dots are good news, huh?Correct.They represent the safe areas immune to the storm.Ah, North America, I should have gone there for a walk in the park.I don't deserve to suffer in this stupid gray prison.I have to say, Researcher Medicine Pocket, even though I approved your request forsports field, which you claimed was a humanitarian need.I think it is more of a canine need.I suggest you install an indicator on your humor module so we know when to laugh.
```

### [26] hash=`a5be39ba8dc13b5b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
See?Like this blinking red dot.Is that Vienna?Yes.Alright, alright!Not privy to the information, huh?I know of your tricks.One day I will findlogical fallacies in your words I swear.And this here, yellow, better than theworst, worse than the best.That's the Aegean Sea.What's all the fuss about?Don't tell me there's a 500 meter long blue crab.No, no sightings of largemarine organisms other than the Gorgon.
```

### [27] hash=`b2309927b1dfecd4`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
This is where Timekeeper and herteam are right now.By the way, it seems you can distinguish betweencolors precisely, so the canine elements in you are more of a personal choice than aninnate trait.I see your efforts on improving your sense of humor, I do, but that's enough now.Turn off the module, okay?Who the heck put these complaints in the box?I'm gonna kick their teeth out!Back to business.Timekeeper and her team are in a bit of a situation.
```

### [28] hash=`0a5e2db20734cf06`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
The details are classified and I am not privy to them either.Huh.Classified.I know what's going on.In this place, classified means they're in big trouble.Marcus?I'm sorry, Madam Hoffman.I was reading the newspaper.I know I told you to practice your arcane skills more, but you don't have to do it all the time.I just told you the oath to secrecy for this mission.Level 2 investigator Marcus, repeat it to me.
```

### [29] hash=`da2ce84d4fb88777`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Remember the field mission manual.Never disclose any information about the storm or the era to irrelevant people.Never build unnecessary connections with the current era.Never disclose any real information about the headquarters to members of the branch.Never discuss confidential matters in unrelated settings.Austro-Hungarian Empire and Russian Empire to establish a negotiating committee.Madame Hoffman, the increased turmoil could cause the storm to arrive earlier, right?
```

### [30] hash=`7d87f4978329ce63`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
That is not our problem.The headquarters will send someone to intervene since it is caused by the Arkenum.Just focus on our destination.Vienna.Time to get out.Grab your luggage.The national treasure of Austria.The creamy chocolate cake, the buttery ganache and the delicious apricot jam.Created by the ingenious apprentice, Franz Sacher in 1832, renowned throughout the world.The dessert of Vienna.Sacher tot.
```

### [31] hash=`552e95bb917930c7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
My first time seeing a real one.How should I cut it?That straight?The cake will get mushy.If I cut sideways, I'll miss out on the apricot filling.What if I eat it in one bite?No, how unrefined.The director would scold me for that.I have to be careful.to think carefully.There must be some other way.Remember all your training,Investigator Marcus.This is the most important moment of your life.Don't get
```

### [32] hash=`0f7005126ed4393b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
too excited or you'll ruin it.But...Nothing.Thank you for deciding for me.What was it here, Marcus?Because the cake is way too sweet.According to theplans, the head of the Vienna branch would pick us up and guide us throughThis lady with the big case is your...assistant?No spy would be stupid enough to carry an entire case of papers in public.So will we all, gentlemen!The gentlemen in Vienna have become exceedingly sensitive after the infamous espionage cases of 1913.
```

### [33] hash=`ef51d3ef7be10cad`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
And their pride was almost destroyed by the Rettel case.I have to remind you, Miss Hoffman, that theoretically we have to go through an entire approval process before I authorize the dispelling of the Mute spell.Whatever.Who cares?They shouldn't have treated a young lady like that, for whatever reason.Relax.This was just a minor incident.You'll never find another place as tolerant as Vienna.It's the very same principles the Foundation strives for.
```

### [34] hash=`c844720515c48b77`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Welcome to Viera, Miss Arcanist from Brumania.You should have shown it to me sooner.It would have saved us a lot of trouble.I'm so sorry to have wasted your time.Speaking of which, no offence, but you are two hours and fifteen minutes late, Mr.Cobb.My apologies.The Minister of Finance and I had a little too much at lunch.Well, your train was late too, wasn't it?You were having lunch when you were supposed to be here.
```

### [35] hash=`58dad2b276050836`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
We agreed.Relax, lady from the headquarters.You're just not used to this place around here.Look at this industrialization and so-called modern designs.They have turned our beloved city and our carefree life into a cold, impersonal machine.Please forgive the train staff, the sewer workers and the plumbers.So rumors about the golden aisle had kept the branch busy.There was no one else but me to pick you up
```

### [36] hash=`3f3e2d6da37f989e`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
It wouldn't have been so embarrassing if headquarters had sent us manpower instead of taking it from usI am also on the job.Mr.Carl.Should I include your complaints in the report?That's okayIt's just a group of lunatics banished to an islandThey're arcane criminals from a small country, and people will forget about them in less than a month.Only a few would believe that it has any real influence on Vienna.
```

### [37] hash=`ae2a5c933b5dfe0b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
You know, the young artists who think highly of themselves,the schemers with evil plans,and the conspiracy theorists suffering from neurasthenia.The Maghavs and the Bohemians are already giving us a headache.Austria abolished that policy in 1868, but Romania did not until 1913.I carried it with me out of habit.Thank goodness I did.This is indeed the era I'm from.That time has returned.Never disclose any information about the storm or the era to irrelevant people.
```

### [38] hash=`a77b0390b61ec4eb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p48`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜1~3）

```text
Put away your license.We need to catch up with Karl.Remember my words, Marcus.Never trust anyone, even if they're a branch member of the Foundation.
```

### [39] hash=`313038a8b5bd54cf`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
So this is the Vienna branch?Blended!Look at the walls, simple yet elegant.It's like a temple of modern art.I can read the contrast between different shapes and textures.This Mr.Ulrich must have put so much effort into the design.It must be a very pleasant place to work at, Mr.Kahl.Oh, no.This is a secession building.Another meeting place for the young artists to show off, other than the cafes.They said they wanted to break away from traditional art.
```

### [40] hash=`48226fc760044ebc`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Well, it's more like they're breaking away from human life.There's nothing to like here.Only inexplicable paintings and neurostenic lunatics.But people keep coming back.There are even secession groups to the secession.Like cells dividing through mucous.The entrance to our venerable branch is on the left.Please follow me.Notice the guard?It's the most loyal and reliable knight of Vienna,powered entirely by arcane ritual,
```

### [41] hash=`8cdc286791422dc0`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
the greatest achievement since the revival of Arcanum in Europe.In 1662, a royal magician from London offered it to the emperor at the time.Since then, it's guarded the Empire for centuries.Ah, sir!Greetings, dear Suscarpia.How is your son Tamino?I hear he's not getting along well with his fiance.He's a strange one.What's he doing standing in the corner like that?My apologies, Miss Hoffman.Please hold on.
```

### [42] hash=`4dda70e854a027be`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Terrific, Heinrich!Just as terrific as your pathetic art career!That's great!Best wishes to you, Suscarpia.That's why he sees everyone as a character in an opera.Operas and music, they do harm to your eyes and fill your ears with useless sounds.Is every artist like this?Scarpia, Angelotti, they are indeed characters from the opera Tosca.Oops, I am getting off topic.Don't worry, we've modified its original ritual to meet the needs here.
```

### [43] hash=`dc1a408c0cb81196`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Lots of people come in and out after all.I will.Who's Mr.Eckhart?The contact between the Foundation and the Vienna branch in 1914.A phantom of history.At that time, people still believed the Golden Age that had begun with the last generation would continue as it should.And that their positions in government would be as unshakable as the long-standing empire.It won't let me in.You're not joking, are you, Mr.
```

### [44] hash=`ed378daa73a4c1b9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Karl?I am not!Oh no, this isn't broken!Oh, no, it's stuck!Oh, my belly!I had this suit custom-made in Paris!What on earth is going on?Why is the defense system activated?Marcus, can you read its internal rituals?Tethering its sluggishness?Yes, I think so.Good.It's a good chance for you to get some experience.Just stay safe.Oh, no!Miss Hoffman!These golems represent the spirit of the Vienna branch!
```

### [45] hash=`15ba2598365e0ed6`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Nine!Procedures are not the problem, darn it!You're not German, are you?So, what's wrong with the Golem?As Mr.Carl said, its structure is simple and yet incredible.The malfunction comes from one of the components.There's an extra stroke on the enchantment.These strokes look new.I guess the staff made a mistake when they did the maintenance or repair.Let's hope so.Now take a look at this before Mr.
```

### [46] hash=`272d8b89cf2cbac1`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Carl comes out.Several days ago, a member of the field agent squad found a painting that was reported in this magazine, The Pan.It belonged to Teufel von Dittarsdorf, a deceased artist from Vienna who committed suicide.Its name is The Salvation, and it was found along with a poem.The poem mentions the doomsday, the reversal of time, and the rain.salvation and rain sounds so yes and given the sightings of menace leaders in
```

### [47] hash=`71bc0a64e2a61668`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Vienna we believe Teofil came into contact with menace leaders before hedied and probably learned the truth of the storm and the method of salvationthis was how menace bin dictae recruited arcanists in 1929 if he knewthe method of salvation why did he still kill himself after so hey notSilenus in Valde fragte ich ihn, was ist das beste und wunderbarste für den Mensch,wie wäre, wo der Mensch nie geboren wurde, sagte er.
```

### [48] hash=`de6bf1395cd0a691`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Ich betrachtete ihn, den Ring des Lebens, den Ring aller Leben.Deine Hände formen den Ring, und das Urteil wird ausgesprochen.On the youngest day, in the twilight, when the story blows away.Oh world, his head bites his feet, his knees touch his nose.Oh man, they inhabit the earth and wait for the sky to fall.Yesterday becomes tomorrow, tomorrow turns into yesterday again.Who will disappear in the rain?
```

### [49] hash=`e2f776f6cbf6872d`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Wem wird das ewige Glück gewährt, die Gnade von oben, und diese Lehre, das Aufhören derExistenz?For so moving, this Sieglind.Poor Siegmund, my best friend has returned to the void.Thank you all for coming today to shed tears for our departed hero.He was a righteous and noble man who cared for his people.He was still trying to save the Arcanists on the Golden Isle before he died.He left us so many beautiful poems and paintings.
```

### [50] hash=`ee610ba3280b5dc0`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Shame that the fire burnt everything to ashes.The only thing that survived was the salvation.We were in a golden age of progressive ideas.We believed the Enlightenment would make ignorance historyand lead us to paradise where everyone would be saved.The barrier between Arcanists and humans would be removed.In Vienna, that tolerant city, we would stand together hand in hand, back to back, relivingthe intimacy we once shared when we first came into this world.
```

### [51] hash=`6c212cd2f2128966`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Oh, world, its head bites its feet, its knees touch its nose.But the reality is, the survival space of our canists is shrinking.We try to speak up in our own language, but that only makes us strangers in ourown land.That's why we have decided to exhibit Sigmund's last work.Not only in memory of the deceased, but in memory of his noble spirit, his sincere concernfor his people, and his scrutiny of this tragic world.
```

### [52] hash=`6c878627c8dfc1d6`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
There is no need to be sad, my friends.He has left us with Rheingold.We will found a committee with the funds raised by the exhibition to improve theHow did you know I was starting from Line A?It says Teofil belonged to a group of artists called The Circle.They often gathered in a secession building.Madam Hoffman, I think we can make contact with them one by one.What's happening?I sense strong arcane fluctuations over there!
```

### [53] hash=`2fd0b0cd01dc539c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
I think it's...it's a...ghost?Dissolve?Dissolve!My god!She passed out again!They're all blinded by the shining glamour of progressivism, and they even scoff at psychoanalysis,the real meaningful discovery of the era.I'll give you the ring, Theophil.It's so beautiful.I'll make it better.I can do it.I can still sing.I-Isolde?Look at me, Doctor!Help me!I will, Isolde.Now let go of me first.Oh no.It's a seance.
```

### [54] hash=`38a3463034d7e261`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Miss Tosca only does it before a performance.Of course it turned out this way.She's lost control.She summoned evil spirits this time.Not the good ones.She's afraid of the paintings.Oh, poor girl.It's her brother's paintings.Miss Kikania!Watch out!Heinrich, give me a hand!Draw the ghosts away by whatever means!Is that a body?These souls are no longer bound to their bodies.They're a nuisance to deal with.
```

### [55] hash=`7dca350acacc074f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Hey!Over there!Leave the doctor alone!I brought this bullet with my savings.Who took it out of my body?It was you!YOU!Enough of your ugly fuss.What family are you from, miss?How much property do you own?Stop working!You'll have to try harder, Mr.Heinrich.Deep heart beat, gentlemen.Are my spasms?She took half my body!No, father will scold me!You don't wanna miss it!I'm nobody!Backed with the stink of a monkey!
```

### [56] hash=`78f158a46c07649c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
How dare you label filthy fingers upon me!The show's over.Time waits for no one.Even for a great people.Roll on my exhaust!I'll take care of his old!Take this!Oh, catching a ghost with my pants.Yeah, it's so soft and sticky.It's back you!That one's...You're safe now, Isolde.Now feel the pressure in my hands.The pressure will remind you of some things.You will slowly and steadily reach your head and not hurt yourself.
```

### [57] hash=`360e147e1d860a64`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
That's it.When I release the pressure, you will slowly open your eyes.Those things will gently fall to the ground, like feathers.My, my, Mr.Igalato.Your hair has grown so fast.To what do we owe this pleasure?Are you also here for the exquisite art?Can you just be normal for once, Henry?And stop calling me by those opera names.Someone reported an arcane disturbance here.I see candles.Are you holding a seance?
```

### [58] hash=`58507b3e20d0d4b5`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
I must remind you that arcane rituals are not allowed unless you have a separate permit.Excuse me?That's not fair.The first permit already costed us a...Please calm yourself, sir.And be mindful of what you implied.The Viennese government has ensured you the greatest possible freedom through working with us.Who do you think cleaned up after you people, after those fires, passionate murders and deadless tempeits?
```

### [59] hash=`49dfbbc56c34dfd9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
We can't bear the consequences of your moments of epiphany forever.Not to mention the Seance is one of the most dangerous acts.We've had two colleagues injured, still being treated for a mental illness in the ViennaGeneral Hospital.You will find no other place as tolerant and open-minded as this one.In return, you should do your part and cooperate with the government.Seance?What Seance?Nothing of the sort, Mr.
```

### [60] hash=`6f3dde27fd1c0b18`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Rigoletto.This is just a rehearsal of the play.The candles, the settings, and, of course, these paintings once bathe in fire.Yes, this is an art exhibit, a youth rally, or, as we prefer to call it, a visualization of the future.I demand a rational conversation.Now, I must question the sanity of this gathering.Sadly, the creator focused too much on the form and overlooked the content.The frame is made of- not important.
```

### [61] hash=`cac13111814e551c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Next page.This one is luckier.Half of it survived the fire, so we can see the lower half of the lady in the picture,but uh, Teofil certainly had a way with women.She was not his first prey, and this one only a frame remains.She is a renowned medium.The Dittistoff family is well known for their mediumship.Nowadays, they use that power mostly for art.That is, they summon a spirit to possess their body, so they can sing, write, and
```

### [62] hash=`0862d609ab8c242a`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
paint like no other.They also suffered for this power.Wrecked by neurosis and hysteria, the family has had very few members despite itslong history.Joseph?Yes, Director.Don't be so hard on them.Joseph of Wonderful Stage Effects.Heinrich is an expert at this, yes?What better demonstrates our free wills than respecting the artists in their work?None of us would mind an episode of excitement every once in a while.
```

### [63] hash=`f3c79cc888ea254f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Even the gentlemen from the headquarters would agree with me, don't you think?Yes, you are right.Kakania should not be a nickname for anyone in 1914.It doesn't belong to this era.She could be with men as vindicti, or at least associated with their people.What's more, when we were at the secession building, I read that painting, The Salvation.It seemed out of place compared to the other paintings.Teofil may have applied a new technique on the salvation, a more daring kind, audacious
```

### [64] hash=`0aaaee2d3b1b9bd3`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
even.But these are only subtleties, I can't be too certain.I was interrupted by that strangely speaking gentleman, so I didn't get everything.Another thing, its content reminds me of the symbol of the circle.Twisting circle resembles the circles in the salvation.Ma'am, you're funny sometimes.I wasn't joking.Based on what we know, we can't be sure if this group of young Arcanists and the Manus are connected.
```

### [65] hash=`7ba371a158caff2c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
But we all know that the latter is eager to win over the cynical, revolutionary youth.You did well, Marcus.The important figures of the Circle.Isolde, Heinrich, and even the late Tyophil.We have made contact with them all.Only this Kakanya.What does the intel say about her?Anya, also known as Miss Clara, inherited her arcane skills from her family.She's able to reflect people's thoughts in a mirror.
```

### [66] hash=`5f54a0553ee0a32a`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
She was once a medical student, but dropped out halfway through.These days, she shows up at various social events as a psychiatrist, which the Foundationtries to prohibit because she doesn't have a license.And she is also...an activist.An activist?according to mr.Heinrich she is meeting with a doctor named Schwartz todaySchwartz the family dr.Karl mentioned let's try our luck therenow then mr.Schwartz only three weapons are allowed in the duel the
```

### [67] hash=`74b848f69eaba052`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
army knife the sword and the pistol I believe the choice to dr.Schwartz forhe has more experience in these tools than I do it's an honor to fight youAnd I look forward to ending your winning streak.Not so much an honorable thing for me.Pardon me, what is happening?A duel, ma'am.Just as Dr.Schwartz was demonstrating his therapy,Mrs.Clara barged right in.They were arguing, and this is how they decided to end it.
```

### [68] hash=`6296c82b1d2fb214`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
To ensure fairness of the duel,the combat must happen within 48 hours of the challenge,but I've never seen one take place on the spot.Well, I hope they know what they're doing.I don't want to get caught as collateral damage that green dressSo she is KakaniaWhat do we do if she gets injured our mission will don't worry about people in that time.It is their life to liveNever intervene if you don't know the exact consequences of your actions
```

### [69] hash=`81fc54cee907e1b8`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
The course of history is more important than our investigationThis is investigate a crater Hoffman, but hold on.I'll be right back.Where are you going?The field agent squad needs to speak to me.This won't take long.I will leave this to you.Remember what I said, Marcus.Yes, madam.Leaving this to me.To me.Pre-aid, Marcus.There's nothing to be nervous about.You can't be an assistant forever.There will come a day when you're all on your own.
```

### [70] hash=`8b50c5cb12ee09d8`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Just like at the secession building, I only have to watch her.If I end up talking to Ms.Kakanya, I'll just pretend to be an ordinary employee of the Foundation.Easy.You used to do well on your own, when you were reading in the lighthouse and the forest.Dr.Shorts, three times he has been involved in duels, and three times he has won.Impressive.This time he's still going for the pistol.But Miss Kakanya does not have an assistant, and she has only one witness in this duel.
```

### [71] hash=`c2e54689b054c75b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
This is not right.Why did she agree to this?She's being reckless.Even an Arcanist should have at least one assistant in a duel.Dr.Schwarz's assistant brought them a pair of pistols.FN Model 1910.Is that a right weapon for a duel?I'm back yet.Foundation employee.This is a quiet float.We're going to jump, Miss Foundation.Three, two, one, here we go!Start running.Seal off that exit!Don't let them get away!
```

### [72] hash=`c559ed4e1cc0b968`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p49`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜4~7）

```text
Got to sneak away.Don't worry, Miss Foundation.They won't leave you behind.I'll help you as you helped me.Kikanya!This way!Elige!I thought you were out selling bears on the street.The magic mustache!You clever boy!Quick, ning your price.Are you sure you can afford that, Kakanda?Triple the price can accept.You know my limits, old friend.Put it on this foundation.Take it off.You'll be exposed.It smells, but bear with it.

Keep quiet and follow me.I'll get you to safety.Lead us if you want your pay, Ilich.Got it.Follow me.Fine.
```

### [73] hash=`68fb9ed2aaa62933`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Kikonya!This way!Over here!Elige!Thanks a lot!The prop show came in handy!Finally!Why do I keep having things stick to my lips?Be careful with that!It is no ordinary beard.Every single strand was soaked in a bohemian potion, mixed with blood root, toad's heart, and yavin gal.Why were the guards after you?That's a long story.My my Kikanya, are you friends with government officials now times have changed indeed
```

### [74] hash=`a8fb788539adf1ba`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
I've been here for a whole yearBut I've never seen an official without a beardWhere are you from?Croatia Moravia, Belize.I grew up in Romania.Oh, I'm from Bosnia and HerzegovinaThat makes us friends since we're both from somewhere nearBe careful on the streets these days each you could be in trouble to if the guards catch you after allAnd no official has any idea of what's what should this be the Kaiser's concern or the Koenigs or both
```

### [75] hash=`b1fb43c47f27fedc`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
You'd be the biggest fool to listen and follow these broken rulesStuck in the system nowhere to go unless you work the magic of Crohn'sWhat happens if we don't have an Arcanum license?Oh, you'll love thisWho knows?You could get three days in detention or maybe ten years in prisonEven if you are sentenced to prison, they might forget to bring you inOr, if you're an outstanding citizen who can shed your arcanum during your human re-education,
```

### [76] hash=`463a148cbdbb5808`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
you might get to have a nice life.Without a license, that is.Our justice system is much more unpredictable than the arcanists.We still have a fair chance of getting away.Very informative, Iriich.Oh well then.Ms.Peta Kikanya and Ms.Foundation, forget I said anything.They are some arcanist kids on the streets.Yet, if you stop looking, it's everywhere.Look at this country, my friend.The sumptuous buildings rise so high
```

### [77] hash=`e8f8c77fef72aae9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
that the people in power never have to lay eyes on the rye farmers of Bohemia,the immigrants from the east coast of the Antarctic Sea,or on the arcanists.How could there possibly be smog choking the industrial area?How could there possibly be cold houses in the winter?The cafe house is definitely filled with people who love to danceand not with those who can't afford the heat.Oh, no.Surely there's no bureaucracy, no discrimination, no poverty here.
```

### [78] hash=`00171f2735598a95`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
This is a city of humanism and freedom.Oh, yes.Cacania, Kaiserlich Königlich.Or Kaiserlich Unköniglich.And Cacania, the shit land.There's no better name for this country.So then, you did get that book from a friend.Now's my chance.I still have one spider-tail Madame Hoffman left me.If I can find a chance to leave the spider-tail on herOr in her place.I'm intrigued by the book.Can I see it?By some advice of the field agents and administration.
```

### [79] hash=`0ad3789ec782d134`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Please confirm Madame Hoffman.Yes, report received and I envy your light-heartedness and optimism.They got you out of Vienna on such short notice.I can only imagine that must have been difficult for you as well.According to your intel, the Empire's had too many assassinations in a short period of time.This is not good for the critical point, Semmelweis.In a good mood?Greta, I have more to tell you.
```

### [80] hash=`50d2bb75810171e5`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
I've pulled out of Vienna overnight, and I didn't have time to brief the new squad there.You know it takes ages to get through the briefing process, I might as well just tell you now, personally.There could be an Arcanist who has crossed the storm, and is now in Vienna.Heinrich left them here.He certainly learned some useful things in Berlin.Make yourself comfortable.I'll get you some tea and look for the book.
```

### [81] hash=`ec823e792ab4a3eb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Please don't bother, Miss Kakanya.I won't stay long.I have to go back to the branch soon.I just need to confirm that you havethat book with you at...Kakanya's arcane skill?Miss Foundation, it's okay.Just a little trick I use to ensure my personal safety.I usually even charge for this.Look into the mirror, which reflects your inner world.This trick has been used by Arcanus for thousands of years.When it was first used, the Roman Emperor still ruled this land.
```

### [82] hash=`ddec33f6e7a3bbdd`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Speaking of which, Miss Foundation.How did you know that the pistol was tempered with?Your arcane skill?The mirror.I am curious.No need to be alarmed.I'll treat you gently.Start running.Deep breath, Miss.Look at the mirror.This is a private session.Your secrets are safe with me.Now, what do you see?I can see Akane's arcane skill, the maze of mirrors.Look at them directly, miss.They'll reveal your deepest secrets and desires.
```

### [83] hash=`56c914245409ac09`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Illusions, Marcus.Just break her arcane skill and get out.Do the only thing I can do.Great.I see her.Behind these illusions, but which one is real?Candy, you see through the illusions.Or was it pure luck?She can move through me.Be luck?I need to be sure.I'd be disappointed for it to fluke.Wanna watch the aerial stunts?Candy, everything a book.Everything can be read.These reflections are merely distractions.
```

### [84] hash=`cbe1f0e72db4ba76`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Candy, the page of truth.Oh, it's true.You saw through the illusions as you saw through the pistol.all right enough of my tricks what a pleasant surprise how does your skillwork let me see no out of here reflections she created were real enoughbut not perfect their reflections had neither shadows nor breath mostimportantly they didn't have her passion and subtle movements I read thetruth from these details she meant me no harm maybe it was just a little
```

### [85] hash=`ea5c842a21e5c01a`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
And that's the masterpiece which would be hard to miss.That was day of his final piece of work.The Golden Isle being its subject.Big news at the time.The island hidden from all people in the Aegean Sea.The ancient Arcanus settlement.The strange current and magnetic field around it.The animals only heard in storiesand a shadow of modern society cast upon it.Well, those are just hearsay.Every one of them came from a mistake of the past.
```

### [86] hash=`6eaa44c7a42e0155`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
We are only here to observe.This is Vienna in 1914, the birthplace of an enduring war and chaos, the critical point.It is a powder keg and the slightest spark will set it off.Any action we take could have unfathomable consequences.That is why we advise extreme caution.This is our responsibility to this era.I understand completely, Madam Hoffman.I won't make the same mistake again.Isolde?You look sad and pale.
```

### [87] hash=`bc3c614e4fd4753f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
What happened?Did something happen in the troop?Or did those dreadful officials come back?No.I'm just...a bit worried.You...you entered a duel for my sake.Dear Lord, the thought of you getting hurt breaks my heart.I never overcharge my treatment, nor sell unnecessary things to the patient,and I will never experiment on my patients.Hehehe, your smile.So you agree with what I said about those psychiatrists and doctors?
```

### [88] hash=`06185f5a060a0fb9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Okay, then let's get to it.Dr.Sigmund Freud wrote that repression of desires is one of the primary causes of hysteria.You need to release these desires.I'll guide your memory to find the deeply hidden thoughts.Trust me, and tell me everything during the session.You'll suffer less from the repression and your physical ailments.Fainting and convulsions will become less severe.Cast off your shackles and trust in me.
```

### [89] hash=`2c9f470d4f74f670`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
This first step is crucial.I know tragedies in your family have affected you deeply,but I'm here to help you now.If you have trouble putting thoughts into words, use this mirror.It reflects your inner thoughts, like a mind's endoscope.Why am I not here?Is your mirror not working?It's not showing my reflection.Oh, no, this isn't right.I promised to do my best.It must have been.I have to remember it.
```

### [90] hash=`4b46f2c41bfc2417`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
You prepared all of this for my sake.I mustn't disappoint you.Oh no, she's stuck in her obsessive thoughts.Isolde, please sit down and listen to my voice.Who is me?I am who?Greetings.Hello.The last time in the secession building, now I understand.I have to get her to stop relying so much on her arcane power.Luckily not completing my education is why I know a little bit of everything.What are you doing, Doctor?
```

### [91] hash=`1d449011f1fc3497`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Is the session over?Was it because I did something wrong?Did I mess up?Nonsense.You've been doing great.I just have to clean the room a bit.Go away!Mirrors are useless to ghosts!Leave my patient alone and never come back!start running are you talking to me these ghosts are confusing her i have to calm her before shehurts itself i'll take care of you miss ditterstorff shh tell me who is here i'll behave miss kikanya
```

### [92] hash=`9de0afb87e3c21f9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
look at me please who she's a little girlWho are you?Why are you in my bed?Why'd you call my father father?My mother mother?And my brother brother?Hello?I saw you beg and crumble.The father took you awayThe second child remembered that she was really the third child.A seizure.A memory related to the electroshock therapy.At least my treatment's working.She's exploring her robust memories.Shush.Hear that?
```

### [93] hash=`cc79dc9cd07ce022`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Someone's crying fire.Color should be used for a burning cage.Did you hear something crack, fall, and split apart?Snap.Crackle.The raging fire consumed everything, including Teofil.He was screaming.His mind was already gone before he lighted it all.How could he ignore everything with such disregard?Who allowed him to forget with such disregard?What I remember, I remember it all.I am from a noble family.
```

### [94] hash=`0424931d66e2c1d7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
I need to be a qualified Titustov.An outstanding arcanist, a first-rate opera singer, a good sister, and a good daughter.Never forget my manners, never forget the family.But he, he got away with it.If Telfield was truly a man of courage, he should have joined the army or foughta duel with someone.That would have made his death more honorable.Don't be afraid.You can talk to me about anything.In the name of my family and the
```

