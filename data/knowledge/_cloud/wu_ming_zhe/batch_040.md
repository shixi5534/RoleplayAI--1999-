# 剧情图谱抽取 · batch 040

- 角色：`wu_ming_zhe`
- 批次：**40** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.8」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_040.jsonl`

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

### [0] hash=`73dbf9e4989fdaa9`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
People of Rayashki, my dear friends, good day to you all.Over the past two days, Sino has assessed the potential risks and benefits in the areaand held hearings on what should be done about the future of this town.Our hearings saw very limited attendance.We've taken that to be a gesture of approval.Mr.Evgeny has put in a great effort helping to make these changes happen.We all owe him a great deal.
```

### [1] hash=`bd69edfde766bdc8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
Thank you, sir.Please believe that we have made the best decision we could for you.We all know the runeum here has run dry,and the land has been exhausted of all further material wealth,now and into the foreseeable future.As a result, your local processing factory has lost its intended purpose.What's more, Sino has changed our cooperation strategy.Though your town's loyalty will never be forgotten, we must have a sober-minded view of its costs and benefits.
```

### [2] hash=`bfdefd5fdf7ec8d1`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
To sum up, our final decision is that we will be ending operations and all future cooperation between Zeno and Rajasthi.Well, Mr.Bertolt, you have just got here.Perhaps you didn't have enough time to get to know us well enough.Ryashka's value is not just in the Runium.We have many other factories too.Yes, you have a brick factory, a power plant, many forklifts, a smattering of conveyor belts.But all these were all built and suited for only the processing of Runium ore.
```

### [3] hash=`2479f59d6087fa9a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
Without the ore, they simply have no benefit to us.Now that you have full knowledge of the situation and our intentions,We want to assure you that your loyalty has not been forgotten, so we have generouslyprepared two choices for the future of Rajasthan.Firstly, Sino believes that you have many valuable qualities.The determination and skills you've shown in the past year of our cooperation haveproved that your people can be a great asset to us.
```

### [4] hash=`52b212c9d773766f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
Indeed, many of you already meet the entrance requirements to join Xeno.Therefore, on behalf of Xeno Arms Academy, I wish to extend a heartfelt invitation to you.Leave Ryashki, join us, and work for one of our other branches as members of Xeno.What are you saying?You want us to abandon our home for some promise of a job?Calm down, Mr.Knuth.This is not about abandoning your home.It's about joining us in our efforts
```

### [5] hash=`84ab7fe20b4d2127`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
to contribute to world peace, through a more optimized allocation of manpower.So you're just going to pack us all up and ship us away to work for Zeno?You misunderstand, madam.Every year, Zeno dismisses 4% of our employees because theyfailed to pass our rigorous work reviews.And the number of our colleagues that arehim in the line of duty is even larger still.Working for Sino is a privilege, not a gift.
```

### [6] hash=`681d78c185a2be9b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
That's why only a small number of youwill be allowed to come and work for us.What?Now, according to Article 58 in the sectionon protection of Arcanist rightssigned at the Event Horizon Convention,we provide basic supplies for any residentswho haven't been offered a position with Zeno.They will be transferred immediatelyto the nearest relief station until our social workerscontact them for further arrangements.
```

### [7] hash=`908bc3284f07b204`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
So then, you're suggesting you will send our children andelderly away to some kind of refugee station?And the rest of us must go to work for Zeno without any questions?Bredorak!This is total rubbish!Sir, please lower your voice.Well, you would be glad to know that your work experience in particular is valuable to CINO, Mr.Knoot.If you're not interested in our first plan, we have another.If the residents in the area prove reluctant to relocate, CINO can offer another alternative.
```

### [8] hash=`5e5114fe598277d4`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
As stated earlier, Rajaski is a remote town that possesses some significant industrial infrastructure.Therefore, it could be considered an ideal location for a new complex of arms factories.There would be a need to substantially upgrade the Rajaski wharf,to turn it into one of the seaports Sino plans to build across the globe.Additionally, a radio station will be constructed within the town,which will better facilitate our communication throughout the Arctic region
```

### [9] hash=`b34cc4691c64b12c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
so as to stabilize and coordinate with the other powers in the area.They will now be passing out forks listing the options I've presented.Please fill them in with your choice.So your only other option is to turn Rayashki into some kind of military base under Xeno's control?I won't put it so bluntly, but you're not incorrect.Our resources, as much as anyone's, are limited and they must be put to good use.
```

### [10] hash=`0230e66cf0989c2a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
They cannot afford to waste them on strategically useless, costly people and places.If you've found Sino to help you, you should be able to give us something in return.Don't you agree?So Yevgeny, this is the best choice you made for all of us?I must speak in Mr.Evgeny's defense.He is committed to his duty and only wishes to do what he can for his compatriots.Shameless!All you've done is sold us out!
```

### [11] hash=`d689cb5d889cd9c3`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
You tell them, Knut!Do you think it's getting a bit windy lately?Clearly!With all the hot air and if Danny's head, his mind has been blown away!I swear to you, I'm not doing this out of my own interest.Comrades, there are many better places in this world.And you have better purposes to fulfill.You shouldn't waste your time here.Let's all calm down, my friends.It's time to be reasonable.Think carefully.
```

### [12] hash=`41fb2b44ee30fc4b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
Sino has been very generous regarding the offers before you.Generous?Now that's ridiculous.We won't let you take away our family and friends,nor are we about to let you turn our town into a puppet state.We will stay here, no matter what.Comrades, I understand how you feel right now,but we must face the cruel reality of our situation.And you're willing to send away our own people, or give up on all we've built here because of this so-called reality?
```

### [13] hash=`9e565ecf99f49186`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
It is the only way forward.If we continue to stay here without any help, it will be the end of us either way.Do we have to turn to Zeno for this help?The truth is, just as Ryashki's economy has been dependent on Rui, we remain dependent on Zeno.Without them, at the present rate of consumption, we will be out of supplies and materials within a year.The situation looks bad.Xeno is determined to gain control over this place.
```

### [14] hash=`308814df48b5e864`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
But if I complete the task as Xeno requested, does it mean I will shatter their dream?And what about my dream?Did the people who refused to acknowledge the study of ley lines act out of the same self-interest?I've seen this happen so many times before.A simple dream is made to face a cruel reality, where the clever ones give up and leave,and the stubborn fools remain, waiting to be crushed.We are waiting for our misery.
```

### [15] hash=`271d0c42d3f24a5b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
But I am, Miss Vila.With all due respect, I can't complete this task alone.As any ordinary researcher, I can relate to them.Please, forgive me for interrupting.I have heard so much about Ryashki these days.They started from nothing, but bit by bit they accomplished the impossible.Their voice should be heard.природа и течисла и чертыMr.Bottle, we can't hold them any longer.Now, will you listen to me?
```

### [16] hash=`5078d069055abe65`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p10`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（10【仅有的日子】）

```text
We don't need your help.Your soldiers and your tyranny are no longer welcome here.Comrades, what do you say?Shall we solve the problem with the strength of our own hands and hearts?What else can we do?This is what we've always done when there was a problem.There will be more solutions than problems if we work together.If I must die, I will die here with all of you.Stop talking nonsense, you idiot!

Nobody is going to die!Rayashki belongs to all of us.We will stand with it till its last moment.They might say they're just ordinary people, but they are so brave and noble.
```

### [17] hash=`1cf44b90785a7221`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
I traded the future of these people away from my ley line studies.I was a mule chasing after a carrot on a stick.They lured me here all so I could help ruin everything.You seem to be in a good mood.We taught Zino a lesson.They were forced to leave with their devil's bargains and tailstack behind them.We fought back, finally.A nice little trick that was.Thank you, comrade Winsong.We all know who the mysterious hero was that gave us a helping hand.
```

### [18] hash=`bc50e4e5c1e656bc`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
I...I didn't do anything.It's no shame to have helped your friends, not to mention to stand up to Zeno.More confidence in yourself, comrade Linsong.But will you really gain anything from this fight?Not sure.But we have to do something, right?That's why I'm here.To talk to me?I don't know why, but Ms.Vila, you must have thought too much of me.In fact, I'm only a simple researcher.I'm not powerful enough to change Zeno's decision.
```

### [19] hash=`c23f54e0c0186b58`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
You are the one thinking too much, comrade Blenso.Your ley-line lessons were much more popular than you think.They have had a positive effect on the children.Now they are looking at the bigger pictureand observing the world in a more detailed way.You've unleashed their curiosity.Is the aurora the bubbles spit out by the stars?They form such a beautiful map.Do they study ley lines too?But it remains the case that the study of ley lines has never been verified.
```

### [20] hash=`46afe570950442b0`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
For all its ambitions.Only a limited number of people studied it in the past decades.And that number is decreasing even now.What you're looking at is not some skin problem.But my past.My past as a Rusalka.Rusalka?You mean the mermaid from folklore?My people used to live in a far-secluded place in the North, away from the humans.For hundreds of years, there was only hostility, plunder and slaughter between us and them.
```

### [21] hash=`4428e779ae555247`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
We only started to learn more about each other in the last few decades.And then I was born.It's been a hard life growing up within human society, but I've become used to it.Still, some things never got easier.Most humans still thought I was a freak.They welcomed me with mocking, sarcasm and contempt for my people, my heritage.As for the Rusalki, they too found a half-blooded mermaid unacceptable.They didn't approve of my living among the humans, forcing me to live as a fugitive
```

### [22] hash=`23e996dcb33fff92`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
Moscow and Saint Petersburg.They tried to catch me by every means possible, so they could washaway the stain they saw in me.That sounds very difficult.Humans have stigmatized and hunted theRusalki for centuries, while Rusalki still have the instinct to attack and plunder human shipseven now.How are they supposed to make peace in such little time?That was what I thoughtThen I came to this town, a wonderful world where humans and Rusalka could live in peace.
```

### [23] hash=`8968a0cb7fb09869`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
I was finally convinced.In Rajashkina, everyone can make contributions with their skills,whether you are a human, a Rusalka, or a ley-line researcher.I don't mean to give you more stress or push you.You will always be our friend, whatever your choice is.But this is not an unreachable dream.It's real.The editor of the environmental research agreed to publish our report, finally!But he only gave us five thousand words.
```

### [24] hash=`d23d00e0013d9762`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
On the last few pages.Undoubtedly, it's still a good start.Our first step to reviving the study of ley lines.That's it, I give up.Maybe I'll study something else, like urban planning or landscape design.At least I can make a living that way.The study of Leylines is outdated.Everyone agrees now that it can't be verified by science.This whole study was a dead end.Leylines are only...a baseless series of Arcanum.
```

### [25] hash=`84cd358635c42837`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
I tried talking about our study of Leylines with other Arcanists, but almost no one has ever heard of it.They are more interested in Laplace's breakthroughs, or anecdotes in their own fields,like the chaotic energy sampling mentioned in the paper written by the Butterfly of Lorenz.So, maybe it is an unreachable dream?Do wish I could help, but it would take a lot of resources to verify the theory behind ley lines.
```

### [26] hash=`f732d62f574b5be6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p11`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（11【最后一位乡下人】）

```text
There may be even danger, and sacrifice.Even Zeno has paid little attention to my research.They only see it as a means to an end.Researchers in other fields can stand on the shoulders of giants.While I...I don't even have a school to return to.I doubt that the study of ley lines will help you much.I see.Well, thank you for your honesty, comrade Winsong.I'm sorry.До скорой встречи.До встречи, Вила.

But, Winsong, don't forget your next lesson.The children are still waiting.But the town is...Life must continue, comrade.We can't let our worries stop us.Okay...
```

### [27] hash=`d5dd69f0b435e3c7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
is over.Thank goodness I still remembered the basic premises of ley lines in biology.Feel free to ask me any questions.Oh, cheer up little ones.There won't be any examsfor this subject.Um...Miss Winsong, are you going to take up those potatoes aloneagain?We have to beat the critters out there.That we will find their weakness aslong as we finish the map with you.Just like how you taught us to.Kikirin are
```

### [28] hash=`176a62c114d32a8f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
dangerous at all.They're plant-eating critters and pose little threat to humans.I have ropes, flowers, and white gloves to dig up a lot of potatoes together.Piyota is strong.He can lift any rocks that are in our way.Nina can prepare a kettle of warm water for everyone, and...I'm sorry, little ones.I wish I could verify all the theories we've been working on,But, as you can see, a critical part is missing.
```

### [29] hash=`a2ecd89e9361fe5c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
It might take months to finish it.Besides, there may be even more dangerouscritters in that area.We'll become the witch's new castle.Or perhaps an empty castle.Quiet, children.Wipe your tears and cheer up.Our Ayashki will stand strong.Really?But Vila, I hope you aren't seriously considering Zenos.Of course not.They might try, but we will never give in.No matter what, for now, we must find a way to protect our town.
```

### [30] hash=`6556ad0ca989a10f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
We will need a shelter from these creatures.We've all decided to stay.Look outside, children.Each and every one of us is doing what we can to hold our town together.spitting out puffy bubbles?The workers are going to transform the abandoned factories into something useful.They're cleaning the ore and debris there.Not an easy job.After that, we will start new production lines and cooperate with the surrounding cities.
```

### [31] hash=`b8aa68d23a748e51`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
We will grow potatoes, breed fish and make canned food.We will find our strengths together.Are we putting makeup on the factories?We can paint their faces and put beautiful garlands on them.Oh, what is Mr.Patrick doing?Everyone's waiting in line.I'm sorry, Avgust.I think we will have to live without our teen handsome comrade Blinchik for a long time.They are signing on to a reform of our rationing.
```

### [32] hash=`32f8b294940ae55a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
To transform our factories, we need to cut down the budget for the canteen.Oh, thank you for your sacrifice, comrade Blinchik.You deserve a medal!And some chocolate!Look!The bulldozers are tearing down those houses!Yes, we all agreed to exchange some of our living space for more land to grow food.Price is much higher than it first seemed.Is it worth it?Of course!You cannot find what we have here in Zinus' barracks or in a relief camp.
```

### [33] hash=`c78cf34dca345e90`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
You can't find it anywhere in the world.Think about the old comrades and the babies.They're the past and the future of Ryashki.How could we leave them behind or subject them to Zino's whims?She'll never be abandoned in Ryashki.I think people out there would be envious if they saw what you are doing here.We really aren't doing anything so special.We're only doing our job, our duty to one another.There are lots of conflicts out there.
```

### [34] hash=`6960d4144419dbe9`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
Conflicts, like the one between humans and Rusalkia.Like the ones that mocked the study of ley lines and dissolved our school.They did so simply because it might take from their funds or steal their glory.Everyone forever building walls just to keep separated from each other.Hoarding whatever they could get their hands on.Then they blame the aftermath.The harm they do to others on cruel realities.
```

### [35] hash=`5aea73a0714e596c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
reality be everyone's mortal enemy the cause of all suffering war greed theperfect excuse to never care but things are different in a Yashki they took mein unconditionally when I came here and they stayed friendly for a week amonth a year and even now so naturally it became my dream to everyone hereShares a beautiful dream.A dream that we can work and enjoy life together.That someday there will be no more conflicts between people or worries about tomorrow.
```

### [36] hash=`278f8afa64f098df`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
That everyone will be able to work to achieve their passions whatever field they wish to pursue.A utopia.It's not just a way of life for now, but the future we're always trying to reach.I've spread the study of ley lines in Rayashki along with its potential.They showed great interest.The study tells us about the secrets that could lie beneath the earth after all.Perhaps it will bring hope to Rayashki.
```

### [37] hash=`ddf6dbaea9f00168`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
But I'm not one of you.You taught the children something new, and you helped us explore our town's potential,didn't you?Everyone here is more than happy to help you.You know, comrade Knut has been boasting about the assistance he was able to providefor your studies.And many others are envious.They want to help you too.More importantly, you already have a group of curious students here willing to study your theory.
```

### [38] hash=`11e8da5931a8ab14`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
Now, allow me to ask you again, comrade Winsong.Would you hold a lecture on ley lines for all the citizens of Ryashki?Even though my research doesn't have any endorsements or achievements?Of course!Perhaps we can be the first to endorse it, after your lecture.You're being far too obvious in your recruitment tactics.The world is not a beautiful place.Poverty, privilege, egoism, exclusivism, so many problems.
```

### [39] hash=`ffa5b8a69eacd19d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p12`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（12【晚班列车】）

```text
But that doesn't mean it can't get better in the future.Perhaps the experiment we are doing in Rajashki now will become the symbol of a better future.A new world where all races and ideas can coexist.Well, of course it may fail and end up a ruin.But at least, we've tried.We love our home, and we're ready to devote our lives to it.I can't shake the feeling you're inviting me aboard a leaky boat that could sink at

any moment.Maybe, comrade Wensong.But should we sink, remember, your friend is a Rusalka, and we do well underwater.What an honor.
```

### [40] hash=`6aab9393af762eed`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
Today, I am going to introduce the study of ley lines and the progress of my research on the Rayashki.Thanks to your help, I have finished the drafts of the town's ley energy map andI have confirmed the presence of many precious resources.Through these colorful lines?These lines and spots show us the state of local ley energy.Each color represents a different concentration of creatures or minerals.
```

### [41] hash=`c21f66a8fbc674c6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
Simply put, this area covered in frozen earth and frost contains many rich resource veins.These gray marks symbolize them.They are located in most of the corners of the map, all of them outside of town.Oh, maybe that's why grandpa said we couldn't grow anything here in the beginning.They eventually solved that problem by importing rich black topsoil for our fields.As for the runium you've mined to make a living, look at the dark gray marks.
```

### [42] hash=`8806c224e53fef4b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
According to the map, they are becoming increasingly scattered and faint, so it can be hard to see them.Besides resources, we can also find concentrations of different creatures using the map.The navy blue marks represent the kikirn, while the aqua green ones represent the mutant kikirn from the wharf.They feed on plants, and you can find their traces in many corners of the town.The red-brown marks are the Kikituks, an aggressive species.
```

### [43] hash=`40707a570ca50d66`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
They're vicious by nature and prey on just about anything arcane they can find.Even other creatures.I feel as though my head is going to explode from all this new information.Can you explain a little simpler for this old workhorse, comrade Winson?Of course.This sample comes from a Kikituk in the mine.I took it with Mr.Yevgeny's help.Seems like just a normal piece of fluff,no matter how I look at it.
```

### [44] hash=`27304751fc14065c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
Yes, and in most people's eyes, it's nothing more than that.But in a lay hunter's eyes, it revealsa great deal of information.The navy blue marks and the red-brown onesseem to mix together.And there are also dark gray ones popping out among them.So, it looks like our Mr.Kiki-Tuc ate well.Perhaps he had a Kikian soup with Arunian-flavored kefir.Looks like these critters have realized their dream long before we could.
```

### [45] hash=`63e8fdee0b36e83f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
But what about those black marks?If my memory serves me right, the map you just showed us had those black marks too.Yes, but they don't match any creature or resource we know.I believe it represents a new kind of resource.Oh, well where is it then?We can only find the answer in this area here.In the depths of the mine?The lay energy is emanating from there.Afterwards, it flows throughout the food chain, passing through all kinds of creatures and materials before eventually returning to its source.
```

### [46] hash=`f0bfd628d3455262`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
Then our new resource is probably somewhere there.Even if we cannot find them yet.But in the end, this is all just conjecture.Are we really going to waste all our time and money on your assumptions?Or can you prove it's something more than conjecture?I would call it a preliminary conclusion.But could it be endorsed by any authorities or proven theories?So far, no.So then it is little more than a fairy tale.
```

### [47] hash=`bf573cacfe0f1624`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
Am I right?I admit, it's a gamble.It's never easy to dig, you know.And Xeno has already withdrawn all their own equipment.All we have left in Ryashki are some outdated machines.Besides, Ms.Wensong mentioned the critters.Maybe their presence there is some kind of proof, but they are themselves a danger.It is obvious that there will be many more critters there than near the town.And you would have us waste time, perhaps even sacrifice our comrades, to pursue what could just be a fairy tale?
```

### [48] hash=`0a718280d73334b3`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
There is no doubt, the cost is simply too high.Who would be foolish enough to dig some holes in the wild just to see if there are critter bones in there?The answer is very clear.We don't need new kind of geography mixed with arcane.Let's save everybody some trouble.Conclusion, the application for Project Leyline should be rejected.Agreed.I...Even cranks can apply for research funds nowadays.Keep moving, Comrade Winsong.
```

### [49] hash=`65e082483b0664d4`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
Keep moving.The people of Rayashki don't back down in the face of their problems.Whatever it is, we can fix it together, right?I approve of Comrade Winsong's proposal.Me too!That's right.This is not a gamble or a fairy tale.Here's a Ley Line simulator.It can simulate the creatures on the Ley Energy map,so we can do further analysis.Is it able to simulate the creatures too?Certainly.Simulating critters is lesson one in the Ley Line textbook.
```

### [50] hash=`75ab797ddf1bd854`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
We can use the simulation to carry out targeted training against the critters.Looks like the study of Ley Lines is more organized than I thought.Congratulations, comrade Windsong.You will have the manpower you need.Don't, comrade!We can't wait!Ha ha ha!It's like digging the mine all over again!That was the biggest achievement of my life!Let's do this, comrades!Digging like this is no easy war!That was one powerful blow!
```

### [51] hash=`52d950dbc6a94a5a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
I think we can draw our conclusions now.Everyone, we have to admit, this is going to be a risky operation.But it's also our last chance to protect our land and our people.We must explore the mine.There will be danger.Yes, some of us may get hurt.But we may also find this new resource and save our Ryashki.For you, for me, for everyone!We can already expect that critters have occupied the mine.We'll just have to work together to drive them away.
```

### [52] hash=`c6f08354530491ba`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p13`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（13【别了芝诺！】）

```text
We've dug this mine with our own machines once, and we'll do it again.It's how we've made it so far.However old they are now, they will always be our children, right?You're good at the assembly, huh?Nikita, you're going to be busy with the engines.Valeria, we need you for the screws.
```

### [53] hash=`b35a2cc5152fca97`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
It's Vila.They've been doing strange things.Father took out a lot of old books, and he spends most of his time looking over his blueprints now.He said they will be the key to saving the town.Shame I can't read those books or help with anything.My dad was acting strange too.He started fiddling with the bottles from under his bed again.But mom didn't scold him this time.She even took out some of her treasures from the cabinet.
```

### [54] hash=`e7f154571e0acf4d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
Ranger Horn, Noisy Birch Sap, Golden Teeth Seal Whiskers.Dad said his potions would keep everyone energetic for a whole day.Even Mr.Miser took out his ones from the safe box.Move, kids.Good luck, comrade Vila.Strange things too?To use and maintain model A050,operation manual of model SAKA1562.These dusty books, they look older than me.These old friends are our textbooks.Do adult stick exams too?We're doing something far more important than exams, kids.
```

### [55] hash=`9c6e9e58fa6f6ea2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
We haven't used these old fellas since Zeno brought the new ones.Most of our comrades don't know how to operate them.Now is the time to put them back into use.Comrade Knut has been teaching us how to use these outdated technologies.That's right.All the adults have been divided into many groups.Knut is leader of the engineering group,and Pasono's uncle is in the investigation group,while Nina's father has joined the potion group.
```

### [56] hash=`555162f60181be32`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
All of them take part in the creature combat training at dust every day and we share our combat experience with each other andEveryone is working hard to explore the mine.We will be able to live on our own without ZenoMiss Vila, I want the town to be proud of me too.Anything that we can do?I have lots of metal toy trains.Can we make components out of them?They can spin and whistle like a minecartThat's a great idea.
```

### [57] hash=`d925a1b77b211018`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
I'm sure it will inspire everyoneMine first!Calm down, children.I know you want to do your bit.But our future needs you.Now your job is to study hard,so Ryashki can rely on you in the future.Understand?What about Avgust?We can't find him.He'll be so sad if he doesn't get to have a job too.Don't worry, Nina.He is helping the town in his own way.It's only been a few months.Can't believe the monsters have already occupied the whole place.
```

### [58] hash=`fe50a3129f329891`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
Well, not a problem as long as we got our mischievous little comrade.He always knows exactly where they will come out.Things wouldn't have gone nearly as smoothly without him.I would never have believed he could do this if comrade Winsong hadn't endorsed him.Never underestimate any of our comrades, big or small.Do I need to repeat that again?Well done, Avgust.You protected everyone.Protected?But I was just teaching our monster friends how to dance right.
```

### [59] hash=`ececf700e8c2e690`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
They are slow learners.Yes, that's what we want you to do.A performance with the Kiki-Tux.Your job is to tell which critter, I mean, which friend is dancing wrong.That's your talent, isn't it?Just like you showed us before.What if they dance like?Um...Then they deserve some alenka chocolate.Don't they?Comrade Surgir, our new friend is right beside your boots.I think he is hoping to kiss them.Will you dance with him?
```

### [60] hash=`876a449c2cc544ab`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
What?Watch out!Can we do another try?Back off!More critters than we can deal with here.Many of us are injured.We must retreat.We made the decision to come here together, comrade Evgeny.We are so close to the depths.We must not give up now.I know everyone's wounded, but look how far we've gone.It's been worth it, don't you think?This is all my fault.I'm sorry.Brad Winslow, you've given us a workable plan and helped us recognize our little comrade's potential.
```

### [61] hash=`0e75e45416856417`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p14`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（14【从现实到现实】）

```text
No?He's only a child.He's one of us, comrade Evgeny.I will keep him safe.We aren't just digging a mine now.We managed to find this resource.No one will have to leave.And we can continue to live together, right?There's nothing compared to the glory of our future.I think this is a foolish idea.
```

### [62] hash=`0e669bab34d56724`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
It's me ohYou I want to talk.I was just about to look for you comrade.You've gained you I've found more detailsHereTrust me.They will ease your mindmore or lessLet's skip to the point.I want you to stop your researchWhat?Our exploration has only just started yet.Many of our people have already been hurtCan you promise there won't be further injuries orWorse, before we've found this fairytale treasure.
```

### [63] hash=`7d1135c1bf9483b7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
Your so-called new resource is still unconfirmed, yet the price we've paid looking for it isalready mounting.We had other options, safer options for all of us.We just need to be better prepared.We will arm ourselves with more knowledge for next time.I know what you're after here.The study of ley lines, right?The people here may be enthusiastic, but they are only laymen.I've spoken with someone who can help you far more.
```

### [64] hash=`e4b4bbf444474be8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
It is good to see you, Miss Vinsong.Our proud scholar of a budding, if still informal, school.And you, the big shot from Xeno.Should I feel flattered you stopped by?I read your files, as Mr.Evgeny suggested.enough with the crap as you wish first I believe you owe comrade Evgeny somethanks huh the less than satisfactory results from your study may not haveearned this letter from Zeno but comrade Evgeny insisted on us offering
```

### [65] hash=`b93ce8aaf930c3e9`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
it to you once you have a recommendation you will be able tocommunicate with all the renowned scholars in our lab your long wait forOnce we've transferred the Arkanists away, Rajaski will be abandoned.We are aware of the danger that staying here poses to these people, and it is our responsibility to save them,whether they wish to resist us or not.That's the only reason for our decision.Understand?
```

### [66] hash=`f63d1a23c6faf8f8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
Let's be practical.As many outstanding young people, a strong academic atmosphere, a better future,You will get the opportunity to revive your school of ley lines.If you pass the exam, it will be a better choice for all of you.Mr.Big Shot, could you use your rusted brain to think of a more noble reason than consumerism and elitism?Do you really think our desire for a better life is the only reason why we refuse to leave?
```

### [67] hash=`e6b1546df6c62624`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
You used ordinary people as a stepping stone to power and privilege.And even now, you take our sacrifices for granted.Reality is cruel.Not you, not Rajaski, and not even Silo can save everyone.You will have to deal with that.You should take what is to come as an inevitable optimization of our society's development.I know.Life may still get harder even if we find this new resource.So what?Your brand of elitism may have invaded every corner of the world, but not this town.
```

### [68] hash=`da58514b43e56bdc`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
Not yet.I see.Most scholars like you hold the same naivete.They refuse to leave any of their comrades behind, even if the price is their own future.What we would sacrifice ourselves for is not the study of ley lines or any other personal goals,But our dream to thrive together.To live in a bright future we all can share.As for this, I don't need it.A leopard never changes its spots.I envy your innocence, Miss Winsor.
```

### [69] hash=`7ddb313b7c1b1f66`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
For years, I believed that our mission was to change the world.But when I looked up, the gate to the new world was already closed.Little Ryashki just coasted along, and I tried to keep everything the way it was, but I failed.Ryashki is doing all our efforts, our will, our dreams.Nothing can change the creeping reality.We attempted to achieve something meaningful, something that could make history,
```

### [70] hash=`ea9cf3937528eb00`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
but the spirit of the times stands against what we are building here.Not just Zeno, but the whole world.That's what reality is like.Boring.Disappointing.You are too pessimistic, comrade Evgeny.Hm?Zeno has tried to recruit me several times.Do you know what I've learned from all their efforts?They don't want us to explore that mine.They belittled our efforts, offered pity for Ryashki,and then planned out a promising future for us.
```

### [71] hash=`6df6fd25b036cc77`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
Yet, they didn't give us a hand, even when our people were injured or died.Do you really think they are so eager to stop us just because they don't want any more sacrifices?Of course not, my friend.A lesson I learned from living in their society.Never do what your enemies want you to do.Xeno is afraid of us.They are afraid that we may discover a new kindling to relight our fire.That we may burn so brightly, that we grow out from their control to create our own future.
```

### [72] hash=`47e395ab033e50a6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p15`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（15【哦草根，草根】）

```text
But they can't have it their way.Rayashki belongs to us, as does the future.I...I will give it some thought, Miss Wynne.Humbert Winslow.
```

### [73] hash=`cc69eac88624d3a8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
I haven't done any field investigation of lay energy since our school fell apart.Don't worry, comrade Windsong.Look, these stones are still the same stones we've always known.And don't be afraid to fail.My father told me that failure is just success and progress.Even if we cannot find this new resource or save our riyashki, we've come back hereWe gather and work for our common goal.We have nothing to complain about.
```

### [74] hash=`1e0e69db819fa376`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Alright.Whatever the result, we thank you for your efforts.Now leave the rest to us.Comrade Yuri, check the connection status.Don't forget to check the drill, Comrade Elena.Relax, it's much easier than opening a can with only your fingers.Knut had grown a slender arm, one that each place as no one could, and picked up stonesthere.They are not like the soft, transparent stones from the sky.These are hard, as chocolate.
```

### [75] hash=`e47b39a874a92ff6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
I think they are good stuff, too.Vilas said we could make them into cans and houses to help the town, but maybeMaybe we will irritate the owner of these stones?Am I right that this sample is from a hundred meters underground?Yes, usually we don't need to reach that deep to find runium ore.Relax comrades, at least it proves there is something new on the Rajashti.Hmm, I have been a miner for 40 years and one thing I know for sure is this.
```

### [76] hash=`3717ef02d5b489e6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
This is not bedrock.It's a Kikituks hair.The black marks are the new resource we're looking for.The red-brown ones are the Kikitooks.And the bright yellow ones are their mineral-eating relatives, the Hoitooks.The machine will show us the stability of the lei energy in a minute.We are at the source of the lei energy now, so the lines should have been pure.If my eyes serve me right, I think I see bad news.
```

### [77] hash=`e2651f717778d3ad`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
You're right.This source is like an estuary polluted beyond recovery.It is carrying too many traces, both from creatures and non-creatures.Besides, the black ore down there seems to have attracted a large number of critters,which has only worsened the pollution.A senior of mine said in his notes that in this case,it will take a push for the core to activate its self-purification system.We got a big one!
```

### [78] hash=`79b88b14571292e1`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Look at that!We should have prepared swimming floats, but the waves won't reach us if we ride this lake.If the lake energy materializes, put in a 7.62cm sea serpent bone, 3 drops of common vervein sap, and 20mg of snail sawfish embryo.It has a beautiful stone on its neck too.Think your father also fell asleep in the mine?Damn, is that the raw runium ore that Xeno has been looking for?The energy is so pure.
```

### [79] hash=`442471a603b788e2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
No wonder it materialized into such a huge body.Defense formation!Miners, stay behind us and evacuate!Comrades, stand with me if you got a weapon!No matter if it's a rifle, a staff, or a shovel, grip them tight!This is our Ryashki's future we're fighting for.We've been waiting for this, haven't we?That's right!Dear comrades, this is the critical moment for our town.No good weapons, no external support.
```

### [80] hash=`c07caf0b64b6f4c8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
But we have our friends, our family, and each other who will never leave anyone behind.Yes, there's nothing to be afraid of.We can always figure it out, so long as...so long as we still have hope.Damn it!This thing is huge!No way!Where are all these little monsters hiding?The ley energy here is like a feast set out for the nearby critters.None of them can resist the temptation.The kikirans are dancing, the eegilaks are singing, and the kikituks are drawing with their breath.
```

### [81] hash=`c0d8af19c23db7da`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Is this their tin hat festival?There is nothing to be afraid of.We've got our comrades, our weapons and our spirit.Victory will be ours, comrades.It's an honor to meet you.The moment of silence, until the torch is lit.We have our turns.We walk in long legs.We made it?Well done comrades, I knew we could make it no something's wrongDo you feel it to come back once?The lay energy has sensed danger.It's become even more active
```

### [82] hash=`00a4859587c2df31`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
To deal with the pollution of other threats the system will choose critters with potential and make them into its underlingsCan be still defeated this time?Comrade Vazotsky do not worry look around you.We have got your backCalm down calm downThink hard.There must be a weakness to this creature.I...I can do this.No, you're wrong, Comrade Winsong.We can do this.Kai, Kai, you're so...What a tragedy.The moment of silence.
```

### [83] hash=`6a4eb1404670e6db`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Kai, you're so...The silver torch is lit.Medic, get the wounded to the back.No!It's not that bad.I can...Don't push yourself too hard.All of our comrades are willing to fight so we don't have to leave anyone behind.Trust me, all right, all wounded, fall back.Team three, take their position.Lay down suppressive fire.Comrade Willy is right.We won't leave any of our comrades on the battlefield.It'd be a shame if we didn't get to see you cry
```

### [84] hash=`da359d2fce932557`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
at the victory celebration.Got it.Peace of silence.The scale of your soul has tilted.The balance needs to be restored.We made it!Good job, comrades.They will be talking about this day for decadesI didn't expect that energy from you comrade yori.See I don't only build housesI also build this rock-solid but make a head count of the wounded and check our remaining suppliesWe will need to work in groups of three in case the creatures come back
```

### [85] hash=`b2d5a4e063b0c406`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Thank you comrades all of you the glory goes to every one of usVictory is secure.I should excuse myself.We make it.After we drove the critters away, the self-purification system began to run slower.Haha!Time to go all out!Let's go comrades!Brighter future!Comrades here!Its energy has not run out yet.What on earth?It's the ore!Dammit, don't tell me it's still powering this thing!I see.So we just break that stone and it's over, right?
```

### [86] hash=`51f0de685df3c57a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Yes.Theoretically.Leave it to me.I'm the marksman here.Just need to get a little closer.Little closer?Comrade Adrian, comrade Daniel, and I will go with you.There may be something we can do.Okay.Believe.Our attacks cannot break this stone at all.The cycle of Lay energy is long.It may take months, years, or even longer than that to return to its source.As long as that ore remains on its neck, the lay energy will continue with the purification until it wipes out everything around.
```

### [87] hash=`69807ed549681475`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
So all we can do is wait?For our own safety, we'd better stay out of this area until it completely returns to the source.I should have seen this coming.I'm so sorry.Comrade Patrick, comrade Ikita, you're not down yet, right?Anyone else?We still got the digger, the crane, and our own strength.Let's try harder.It's nothing more than a stupid stone.We can do this.That's our last chance.Stop this senseless sacrifice, comrade Knut.
```

### [88] hash=`30e2d429dc04808e`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
It's pointless to keep going.But to save Ryashka is also your dream, no?Our little one from afar swore she would unite all of us, no matter who we are or where we're from.We must keep all that in our minds.How can we give up now?I'm so happy I came here and made friends with all of you, comrades.You each have a kind heart and a strong will.Before I met you, my dream was only a joke to the others out here.
```

### [89] hash=`97f4b47dc9ef698d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
But you've shown me it isn't unreachable.Now it feels so real and heartwarming.Sometimes I almost forget that you see the fins and scales on my body.That's why I don't want you to sacrifice yourself for nothing.I don't want to lose him.What we want is to stay together.That's why we're fighting to save Ryashki.Right?Damn it!Wands have lost their feathers.Are you still able to reach the sky?I must thank you, Robert Winslow.
```

### [90] hash=`0b879060ffde3025`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
You've rekindled something in me, in us.I will tell you that I read some papers on your lay lights after that night.It holds some great ideas, I admit.You and Ryazhkin deserve a better future.I want you to know, I recommended you to Zeno only because I was worried for your future.I did not want you to be stuck in a dying town.And it gives me pain to see how brave and determined you all have been.I won't let any of you die here.
```

### [91] hash=`c7415ca38045af6f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
Yevgeny, what are you doing?The sad thing is I took a very different path long ago.But what does it matter now?Ryashka is proud of you.I am proud of you.You will continue to build the new world of your dreams.Our dream.No matter where or when.I will always be there with you.Seize the opportunity.Vila, wind zone, my comrades!Comrade Evgeny...This is not fair!Just because he was the only pilot here doesn't mean he could make that decision alone!
```

### [92] hash=`e0d5b89f71058bc6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p16`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（16【前进进行曲】）

```text
We should have had a vote!We fixed that fighter together!That asshole left us behind!But he will always be our comrade, right?Evgeny, salute!Here's the sea swallow!He flew into the future, child.The future will all reach one day.Comrade Evgeniy.
```

### [93] hash=`b0430f73315de435`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p17`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（17【雪与雪之外的】）

```text
Take hold, comrades!Everything he did was for Ryashki!We shared the same dream, didn't we?To do all we can for the good of the people.Reporting.Drilling reclear.Ready for new exploration.That's the spirit!We must keep going!Hold it period!Yuri, start the machines!On it!It's my best friend.I think it will be glad to have another best friend.I will become a great hero like you!It's a promise!A man's promise!
```

### [94] hash=`512fca262e5a9cce`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p17`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（17【雪与雪之外的】）

```text
Well, why are your feathers wet, P.O.Dad?You have water on your face, Mr.Winson.Can kids still cry after they grow up?I should have known.The abnormal fluctuation of the light energy and how much of an attraction it is to the critters.I should have noticed they were different from my theory.At least this experience will be valuable for the study of Leylites, won't it?Take it in and make something of it.
```

