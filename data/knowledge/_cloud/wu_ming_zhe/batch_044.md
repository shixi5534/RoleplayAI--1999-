# 剧情图谱抽取 · batch 044

- 角色：`wu_ming_zhe`
- 批次：**44** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.8」｜offset 380
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_044.jsonl`

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

### [0] hash=`a543e989801e49e9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Rusalka?You mean the mermaid from folklore?My people used to live in a far-secluded place in the North, away from the humans.For hundreds of years, there was only hostility, plunder and slaughter between us and them.We only started to learn more about each other in the last few decades.And then, I was born.It's been a hard life growing up within human society,but I've become used to it.Still, some things never got easier.
```

### [1] hash=`665411a1121fed81`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Most humans still thought I was a freak.They welcomed me with mocking, sarcasm and contempt for my people, my heritage.As for the Rusalki, they too found a half-blooded mermaid unacceptable.They didn't approve of my living among the humans,forcing me to live as a fugitive in Moscow and Saint Petersburg.They tried to catch me by every means possible so they could wash away the stain they sawin me.That sounds very difficult.
```

### [2] hash=`14631c77ccfe4332`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Humans have stigmatized and hunted the Rusalki for centuries, while Rusalki still havethe instinct to attack and plunder human ships even now.How are they supposed to make peace in such little time?That was what I thought years ago.Then I came to this town.A wonderful world where humans and Rusalka could live in peace.I was finally convinced.In Ryashkiv, everyone can make contributions with their skills.
```

### [3] hash=`a0f7e07f642a115a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Whether you are a human, a Rusalka, or a leyline researcher.I don't mean to give you more stress or push you.You will always be our friend.Whatever your choice is.But this is not an unreachable dream.It's real.The editor of the environmental research agreed to publish our report, finally!But he only gave us 5,000 words on the last few pages.Undoubtedly, it's still a good start.Our first step to reviving the study of ley lines.
```

### [4] hash=`afed11b1e58222c9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
That's it.I give up.Maybe I'll study something else, like urban planning or landscape design.At least I can make a living that way.The study of ley lines is outdated.Everyone agrees now that it can't be verified by science.This whole study was a dead end.Ley lines are only...a baseless theory of Arcanum.I tried talking about our study of ley lines with other Arcanists, but almost no onehas ever heard of it.
```

### [5] hash=`288bfe3a0d29672d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
They are more interested in Laplace's breakthroughs.Or anecdotes in their own fields.like the chaotic energy sampling mentioned in the paper written by the Butterfly of Lorenz.So, maybe it is an unreachable dream?Do wish I could help, but it would take a lot of resources to verify the theory behind ley lines.There may be even danger, and sacrifice.Even Zeno has paid little attention to my research.
```

### [6] hash=`0da405df283d0bf4`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
They only see it as a means to an end.Researchers in other fields can stand on the shoulders of giants.While I...I don't even have a school to return to.I doubt that the study of ley lines will help you much.I see.Well, thank you for your honesty, comrade Winsong.I'm sorry.До скорой встречи.До встречи, Вила.Winsong, don't forget your next lesson.The children are still waiting.But the town is...Life must continue, comrade.
```

### [7] hash=`ac70d741a7d0e1c1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
We can't let our worries stop us.K is over.Thank goodness I still remembered the basic premises of ley lines in biology.Feel free to ask me any questions.Cheer up, little ones.There won't be any exams for this subject.Um...Miss Winsong, are you going to take up those potatoes alone again?...to help you, or to beat the critters out there.that we will find their weakness as long as we finish the map with you.
```

### [8] hash=`3c3d28edd8e14098`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Just like how you taught us to.Kikirin are not dangerous at all.They are plant-eating critters and pose little threat to humans.I have ropes, flowers, and white gloves.We'll dig up a lot of potatoes together.Byoker is strong.He can lift any rocks that are in our way.Nina can prepare a kettle of warm water for everyone.I'm sorry little ones.I wish I could verify all the theories.We've been working on but
```

### [9] hash=`2985814e451da8ea`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
As you can see a critical part is missing it might take months to finish itBesides there may be even more dangerous critters in that areaQuietchildrenWipe your tears and cheer up.Our Ayashki will stand strong.Rimi, but what are you going to do?Vila, I hope you aren't seriously considering Zenos.Of course not.They might try, but we will never give in.No matter what, for now we must find a way to protect our town.
```

### [10] hash=`9c8b52daff2260a2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
We will need a shelter from these creatures.All decided to stay.Look outside, children.Each and every one of us is doing what we can to hold our town together.Spitting out puffy bubbles?The workers are going to transform the abandoned factories into something useful.They're cleaning the ore and debris there.Not an easy job.After that, we will start new production lines and cooperate with the surrounding cities.
```

### [11] hash=`314678888e3fbe9a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
We will grow potatoes, breed fish and make canned food.We will bind our strength together.Are we putting makeup on the factories?We can paint their faces and put beautiful garlands on them.So what is Mr.Patrick doing?Everyone's waiting in line.I'm sorry, Avgust.I think we will have to live without our teen hats and comrade Blinchik for a long time.They are signing on to a reform of our rationing.To transform our factories, we need to cut down the budget for the canteen.
```

### [12] hash=`1ff5cb158734ee01`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Oh, thank you for your sacrifice, comrade Pinchik.You deserve a medal and some chocolate.Look, the bulldozers are tearing down those houses.Yes, we all agreed to exchange some of our living space for more land to grow food.Price is much higher than it first seemed.Is it worth it?Of course!You cannot find what we have here in Zino's barracks or in a relief camp.You can't find it anywhere in the world.
```

### [13] hash=`75a10e45d46107a9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Think about the old comrades and the babies.They are the past and the future of Rayashki.How could we leave them behind or subject them to Zino's whims?She'll never be abandoned in Rayashki.I think people out there would be envious if they saw what you are doing here.We really aren't doing anything so special.We're only doing our job, our duty to one another.There are lots of conflicts out there.Conflicts like the one between humans and Rusalki.
```

### [14] hash=`fd9abf52587a5a98`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Like the ones that mocked the study of ley lines and dissolved our school.They did so simply because it might take from their funds or steal their glory.Everyone forever building walls just to keep separated from each other.Hoarding whatever they could get their hands on.Then they blame the aftermath, the harm they do to others on cruel realities.Reality beat everyone's mortal enemy, the cause of all suffering, war, greed, the perfect
```

### [15] hash=`e44cd281f7b92409`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
excuse to never care.But things are different in Ryashki.They took me in unconditionally when I came here, and they stayed friendly fora week, a month, a year, and even now.So naturally, it became my dream, too.Everyone here shares a beautiful dream.A dream that we can work and enjoy life together.That someday there will be no more conflicts between people or worries about tomorrow.That everyone will be able to work to achieve their passions whatever field they wish to pursue.
```

### [16] hash=`e0f957ff9d2bd8d7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
A utopia.It's not just a way of life for now, but the future we're always trying to reach.I've spread the study of ley lines in Ryashki, along with its potential.They showed great interest.The study tells us about the secrets that could lie beneath the earth after all.Perhaps it will bring hope to Ryashki.But I'm not one of you.You taught the children something new, and you helped us explore our town's potential, didn't you?
```

### [17] hash=`e782deed07a6c54a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Everyone here is more than happy to help you.You know, comrade Knuth has been boasting about the assistance he was able to provide for your studies.And many others are envious.They want to help you too.More importantly, you already have a group of curious students here willing to study your theory.Now, allow me to ask you again, comrade Wensong.Would you hold a lecture on ley lines for all the citizens of Ryashki?
```

### [18] hash=`1b8c125e3c272ddf`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Even though my research doesn't have any endorsements or achievements?Of course, perhaps we can be the first to endorse it, after your lecture.You're being far too obvious in your recruitment tactics.The world is not a beautiful place, poverty, privilege, egoism, exclusivism, so many problems.But that doesn't mean it can't get better in the future.Perhaps the experiment we're doing in Rajaski now will become the symbol of a better
```

### [19] hash=`cd14d42cba516479`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
future.A new world where all races and ideas can coexist.Well, of course it may fail and end up a ruin,but at least we've tried.We love our home and we're ready to devote our lives to it.I can't shake the feeling you're inviting me aboard a leaky boatthat could sink at any moment.Maybe, comrade Wensong.But should we think, remember, your friend is a Rusalka, and we do well underwater.What an honor.
```

### [20] hash=`c7ce887a5e12291e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Today, I am going to introduce the study of ley lines.And the progress of my research, Andrayashki, thanks to your help, I have finished thedrafts of the town's ley energy map.And I have confirmed the presence of many precious resources.Through these colorful lines?These lines and spots show us the state of local energy.Each color represents a different concentration of creatures or minerals.Simply put, this area covered in frozen earth and frost contains many rich resource veins.
```

### [21] hash=`e0de11c3be211740`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
These gray marks symbolize them.They are located in most of the corners of the map, all of them outside of town.Oh, maybe that's why grandpa said we couldn't grow anything here in the beginning.They eventually solved that problem by importing rich black topsoil for our fields.As for the ronium you've mined to make a living, look at the dark gray marks.According to the map, they are becoming increasingly scattered and faint, so it can be hard
```

### [22] hash=`65e78e443e76a909`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
to see them.Besides resources, we can also find concentrations of different creatures using the map.The navy blue marks represent the Kikirn, while the aqua green ones represent the mutant Kikirn from the wharf.They feed on plants, and you can find their traces in many corners of the town.The red-brown marks are the Kikituks, an aggressive species.They're vicious by nature and prey on just about anything arcane they can find.
```

### [23] hash=`30f7906cf104ad8e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Even other creatures.I feel as though my head is going to explode from all this new information.Can you explain a little simpler for this old workhorse, comrade Winsong?Of course.This sample comes from a kiki-tuk in the mine.I took it with Mr.Yevgeny's help.Seems like just a normal piece of fluff, no matter how I look at it.Yes, and in most people's eyes, it's nothing more than that.But in a lay hunter's eyes, it reveals a great deal of information.
```

### [24] hash=`790432995bdbc50b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Uh, the navy blue marks and the red-brown ones seem to mix together,and there are also dark gray ones popping out among them.So it looks like our Mr.Kiki-Tuc ate well.Perhaps he had a Kikian soup with Arunium-flavored kefir.Looks like these critters have realized their dream long before we could.But what about those black marks?If my memory serves me right,The map you just showed us had those black marks too.
```

### [25] hash=`f2554a0ab7e13115`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Yes, but they don't match any creature or resource we know.I believe it represents a new kind of resource.Oh, well where is it then?We can only find the answer in this area here.You mean in the depths of the mine?The lay energy is emanating from there.Afterwards it flows throughout the food chain,passing through all kinds of creatures and materials before eventually returning to its source.Then our new resource is probably somewhere there.
```

### [26] hash=`1ca75c00cc036fb7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
So we need to find it.Then we won't have to put up with Xeno anymore.But...do you have any other proof?Of course.Remember the critter you found in the mine, Mr.Knute?Yes.You said it was called, um...Hoi...Hoitu...Hoituk, a subspecies of Kikituk.They live underground and feed on minerals.That was around the time we had begun to run out of roonium.Is that so?But they were still there, perhaps even more
```

### [27] hash=`2ca26c148888fb45`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
active than usual.That could only mean they were attractedby some other mineral or energy source, right?And even though I didn't find any further hoituksduring my research, I did find the Olga mutants,One of their close relatives.Since they are social creatures, my discovery must prove the presence of some of these hoitoks.Even if we cannot find them yet.But in the end, this is all just conjecture.
```

### [28] hash=`8db3a35674b07020`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Are we really going to waste all our time and money on your assumptions?Or can you prove it's something more than conjecture?I would call it...a preliminary conclusion.But could it be endorsed by any authorities or proven theories?So far, no.So then it is little more than a fairy tale, am I right?I admit.It's a gamble.It's never easy to dig, you know, and Xeno has already withdrawn all their own equipment.
```

### [29] hash=`a17cee0d7c4c5622`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
All we have left in Ryashki are some outdated machines.Besides, Ms.Wensong mentioned the critters.Maybe their presence there is some kind of proof, but they are themselves a danger.It is obvious that there will be many more critters there than near the town.And you would have us waste time, perhaps even sacrifice our comrades,to pursue what could just be a fairy tale?There is no doubt.The cost is simply too high.
```

### [30] hash=`81091f43ebb22aa8`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Who would be foolish enough to dig some holes in the wildJust to see if there are critter bones in there.The answer is very clear.We don't need new kind of geography meets with our king.Let's save everybody some trouble.Conclusion, the application for Project Ley Line should be rejected.Agreed.I...Even cranks can apply for research funds nowadays.Keep moving comrade Winsong.Keep moving.The people of Rayashki don't back down in the face of their problems.
```

### [31] hash=`cb25512c28be878c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Whatever it is, we can fix it together, right?I approve of comrade Winsong's proposal.That's right.This is not a gamble or a fairy tale.Here's a ley line simulator.It can simulate the creatures on the ley energy map so we can do further analysis.Is it able to simulate the creatures too?Certainly.Simulating critters is lesson one in the ley line textbook.We can use this simulation to carry out targeted training against the critters.
```

### [32] hash=`aa78cc7d8cbf62af`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Looks like the study of ley lines is more organized than I thought.Congratulations, comrade Winsong.You will have the manpower you need.Come on, comrade.We can't wait.It's like digging the mine all over again.That was the biggest achievement of my life.Let's do this, comrades.Digging like this is no easy work.That was one powerful blow.I think we can draw our conclusions now.Everyone, we have to admit, this is going to be a risky operation.
```

### [33] hash=`cc63e37a4fa6ba08`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
But it's also our last chance to protect our land and our people.We must explore the mines.There will be danger.Yes, some of us may get hurt.But we may also find this new resource and save our Ayashki.For you, for me, for everyone!We can already expect that creatures have occupied the mine.We'll just have to work together to drive them away.We dug this mine with our own machines once.And we'll do it again.
```

### [34] hash=`6c9f0563bf93d46a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
It's how we've made it so far.However old they are now, they will always be our children.Right?You're good at the assembly, huh?Nikita, you're gonna be busy with the engines.Valeria, we need you for the screws.Miss Vila, they've been doing strange things.Father took out a lot of old books, and he spends most of his time looking over his blueprints now.He said they will be the key to saving the town.
```

### [35] hash=`ffbb00b82dc1b422`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Shame I can't read those books or help with anything.My dad was acting strange too.He started fiddling with the bottles from under his bed again.But mom didn't scold him this time, she even took out some of her treasures from the cabinet.Ranger horn, noisy birch sap, golden teeth seal whiskers.Dad said his potions would keep everyone energetic for a whole day.Even Mr.Miser took out his ones from the safe box.
```

### [36] hash=`92e08a73b9b5b8be`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Move kids.Good luck comrade Bila.Doing strange things too?To use and maintain model A050, operation manual of model SAKA1562.These dusty books, they look older than me.These old friends are our textbooks.Do adults take exams too?We're doing something far more important than exams, kids.We haven't used these old fellas since Zeno brought the new ones.Most of our comrades don't know how to operate them.
```

### [37] hash=`4a1bfa527b906612`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Now is the time to put them back into use.Comrade Knut has been teaching us how to use these outdated technologies.That's right.All the adults have been divided into many groups.Knut is the leader of the engineering group,and Pasono's uncle is in the investigation group,while Nina's father has joined the potion group.All of them take part in the CREATOR COMBAT training at DAS every dayand we share our combat experience with each other.
```

### [38] hash=`8d871c9e1f703c50`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
And everyone is working hard to explore the mine.We will be able to live on our own without Zeno!I want to be proud of me too!Is there anything that we can do?I have lots of metal toy trains!Can we make components out of them?They can spin and whistle like a minecart!That's a great idea!I'm sure it will inspire everyone!Come down children, I know you want to do your bitBut our future needs youNow your job is to study hard so Ryashki can rely on you in the future
```

### [39] hash=`cac23b5b25871207`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Understand what about of course we can't find him.He'll be so sad if he doesn't get to have a job, tooDon't worry.He's helping the town in his own wayWhiskers?It's only been a few months.Can't believe the monsters have already occupied the whole place.Well, not a problem as long as we got our mischievous little comrade.He always knows exactly where they will come out.Things wouldn't have gone nearly as smoothly without him.
```

### [40] hash=`42c6547739f47465`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
I would never have believed he could do this if comrade Windsong hadn't endorsed him.Never underestimate any of our comrades, big or small.Do I need to repeat that again?Well done, Avgust.You protected everyone.Protected?I was just teaching our monster friends how to dance right.They are slow learners.Yes, that's what we want you to do.A performance with the Kiki Tuks.Your job is to tell which critter, I mean, which friend is dancing wrong.
```

### [41] hash=`4d5291118756110e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
That's your talent, isn't it?Just like you showed us before.Oh, what if they dance like?Um, then they deserve some alenka chocolate, don't they?Comrade Sergei, our new friend is right beside your boots.I think he is hoping to kiss them.Will you dance with him?What?Watch out!Any more critters than we can deal with here.Many of us are injured.We must retreat.Decision to come here together, comrade Evgeny.
```

### [42] hash=`33feb2b0b317131e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
We are so close to the depths.We must not give up now.I know everyone's wounded, but look how far we've gone.It's been worth it, don't you think?This is all my fault.I'm sorry.Winston, you've given us a workable plan and helped us recognize our little comrade's potential.No?He's only a child.He's one of us, comrade Evgeny.I will keep him safe.We aren't just digging a mine now.If we manage to find this resource, no one will have to leave.
```

### [43] hash=`76259065acd22e67`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
And we can continue to live together, right?There's nothing compared to the glory of our future.Again, I think this is a foolish idea.You!I want to talk.I was just about to look for you, comrade Evgeny.I've found more details.Here.Trust me, they will ease your mind.More or less.Let's skip to the point.I want you to stop your research.What?Our exploration has only just started, yet many of our people have already been hurt.
```

### [44] hash=`c723eada5bbb238c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Can you promise there won't be further injuries or...worse, before we've found this fairytale treasure?Your so-called new resource is still unconfirmed, yet the price we've paid looking for it is already mounting.We had other options, safer options for all of us.We just need to be better prepared.We will arm ourselves with more knowledge for next time.I know what you're after here.The study of ley lines, right?
```

### [45] hash=`1336098f0e777490`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
The people here may be enthusiastic, but they are only laymen.I've spoken with someone who can help you far more.It is good to see you, Ms.Vinsonk, our proud scholar of a budding, if still informalschool.And you, the big shot from Zeno.Should I feel flattered you stopped by?I read your files, as Mr.Evgeny suggested.You know already that Xeno has investigated many Arkane cases and been deployed to many
```

### [46] hash=`6ffc7e060c7f2b1b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
places related to Arkenum.But we have never met anyone quite as obsessive in their study as you are.What now?Have the Big Shots decided they are going to trust my studies?While I might admire your perseverance myself, no, they're not convinced.We just wonder what you and your school have gained from this long journey.Enough with the crap.As you wish.First, I believe you owe Comrade Evgeny some thanks.
```

### [47] hash=`871e4a43bf760ec0`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Huh?The less than satisfactory results from your study may not have earned this letter fromAll we have to do is wait for Xeno's grace to be bestowed on us.We should be moved to tears by your mercy, no?Putting aside your sarcasm, I would suggest you consider the danger of throwing away thisopportunity.You are wasting time, effort, maybe even lives on some foolish vile goose chase.We can offer the people here a much safer and more feasible way forward.
```

### [48] hash=`63b5ac2576531ec1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Don't you see?Ahem.I'm afraid you're mistaken, Ms.Winsong.As far as Sino is concerned, the value ofthis land is exhausted, fairytale resources notwithstanding.Once we've transferred theArkanists away, Rajaski will be abandoned.We are aware of the danger that staying hereposes to these people, and it is our responsibility to save them, whether they wish to resistor not.That's the only reason for our decision.
```

### [49] hash=`53828e3275cbb5b2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Understand?Let's be practical.Has many outstanding young people.A strong academic atmosphere.A better future.You will get the opportunity to revive your school of ley lines.If you pass the exam, there will be a better choice for all of you.Mr.Big Shot, could you use your rusted brain to think of a more noble reason than consumerism and elitism?Do you really think our desire for a better life is the only reason why we refuse to leave?
```

### [50] hash=`b8c222b2c115d485`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
You used ordinary people as a stepping stone to power and privilege, and even now you takeour sacrifices for granted.Reality is cruel.Not you, not Rajaski, and not even Simon can save everyone.You will have to deal with that.You should take what is to come as an inevitable optimization of our society's development.I know.Life may still get harder even if we find this new resource.So what?Your brand of elitism may have invaded every corner of the world, but not this town.
```

### [51] hash=`381cf4a86750fee5`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Not yet.I see.Most scholars like you hold the same naivety.They refuse to leave any of their comrades behind, even if the price is their own future.What we would sacrifice ourselves for is not the study of ley lines or any otherpersonal goals, but our dream to thrive together, to live in a bright future weall can share.As for this, I don't need it.A leper never changes its spots.Mr.Swinson, for years, I believed that our mission was to change the world.
```

### [52] hash=`0bea8759c9d14675`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
But when I looked up, the gate to the new world was already closed.Little Ryashki just coasted along.And I tried to keep everything the way it was.But I failed.Ryashki is done.All our efforts, our will, our dreams.Nothing can change the creeping reality.We attempted to achieve something meaningful.Something that could make history.But the spirit of the times stands against what we are building, not just Zeno, but the whole world.
```

### [53] hash=`ff00841996d4b110`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
That's what reality is like.Boring.Disappointing.You are too pessimistic, Comrade Evgeny.Zeno has tried to recruit me several times.Do you know what I've learned from all their efforts?They don't want us to explore that mine.They belittled our efforts, offered pity for Ryashki, and then planned out a promisingfuture for us.Yet they didn't give us a hand.Even when our people were injured or died, do you really think they are so eager to
```

### [54] hash=`b1fb98b59fd2304b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
stop us just because they don't want any more sacrifices?Of course not, my friend.A lesson I learned from living in their society.Never do what your enemies want you to do.Xeno is afraid of us.They are afraid that we may discover a new kindling to relight our fire.That we may burn so brightly that we grow out from their control to create our own future.But they can't have it their way.Rayashki belongs to us, as does the future.

I...I will give it some thought, Miss Wynne.Homer, Winslow.
```

### [55] hash=`5be50043b66cef14`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I haven't done any field investigation of ley energy since our school fell apart.Don't worry, comrade Winsong.Look, these stones are still the same stones we've always known.And don't be afraid to fail.My father told me that failure is just success and progress.Even if we cannot find this new resource or save Arayashki, we've come back hereWe gather and work for our common goal.We have nothing to complain about.
```

### [56] hash=`1e0e69db819fa376`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Alright.Whatever the result, we thank you for your efforts.Now leave the rest to us.Comrade Yuri, check the connection status.Don't forget to check the drill, Comrade Elena.Relax, it's much easier than opening a can with only your fingers.Knut had grown a slender arm, one that each place as no one could, and picked up stonesthere.They are not like the soft, transparent stones from the sky.These are hard, as chocolate.
```

### [57] hash=`9599f610dfd95502`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I think they are good stuff, too.Vilas said we could make them into guns and houses to help the town, but maybeMaybe we will irritate the owner of the stones?Am I right that this sample is from a hundred meters underground?Yes, usually we don't need to reach that deep to find runium ore.Relax comrades, at least it proves there is something new on the Rajasthi.Hmm, I have been a miner for 40 years and one thing I know for sure is this.
```

### [58] hash=`3717ef02d5b489e6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
This is not bedrock.It's a Kikituks hair.The black marks are the new resource we're looking for.The red-brown ones are the Kikitooks.And the bright yellow ones are their mineral-eating relatives, the Hoitooks.The machine will show us the stability of the lei energy in a minute.We are at the source of the lei energy now, so the lines should have been pure.If my eyes serve me right, I think I see bad news.
```

### [59] hash=`e2651f717778d3ad`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
You're right.This source is like an estuary polluted beyond recovery.It is carrying too many traces, both from creatures and non-creatures.Besides, the black ore down there seems to have attracted a large number of critters,which has only worsened the pollution.A senior of mine said in his notes that in this case,it will take a push for the core to activate its self-purification system.We got a big one!
```

### [60] hash=`c86753c574d91fde`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Look at that!We should have prepared swimming floats, but the waves won't reach us if we ride this lake.If the lake energy materializes, put in a 7.62 centimeter sea serpent bone, three drops of common vervein sap, and 20 milligrams of snail sawfish embryo.Are you crazy?Wow!It has a beautiful stone on its neck too.Think your father also fell asleep in the mine?This is our Ryashki's future we're fighting for.
```

### [61] hash=`299ca04ffe9f0c56`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
We've been waiting for this, haven't we?That's right!Dear comrades, this is the critical moment for our town.No good weapons, no external support.But we have our friends, our family, and each other who will never leave anyone behind.Yes, there's nothing to be afraid of.We can always figure it out, so long as, so long as we still have hope.Damn it!This thing is huge!No way!Where are all these little monsters hiding?
```

### [62] hash=`b9865e9c8c49d82a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
The lay energy here is like a feast set out for the nearby critters.None of them can resist the temptation.The Kikeherns are dancing, the Igiraks are singing,and the Kikitooks are drawing with their breath.Is this their tin hat festival?There is nothing to be afraid of.We've got our comrades, our weapons and our spirit.Victory will be ours comrades.It's an honor to meet you.The moment of silence, until the torch is lit.
```

### [63] hash=`d63543573b57f77a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
We have our turns.We walk in long legs.We made it?Well done comrades, I knew we could make it no something's wrongDo you feel it to come back once?The lay energy has sensed danger.It's become even more activeTo deal with the pollution of other threats.The system will choose critters with potential and make them into its underlingsCan be still defeated this timeComrade Vazotsky do not worry look around you.
```

### [64] hash=`142ed7958742eaa6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
We have got your backCalm down calm downThink hard.There must be a weakness to this creature.I...I can do this.No, you're wrong, Comrade Winsong.We can do this.Kai Ka Zhe Shou.What a tragedy.The moment of silence.Kai Sa...The silver torch is lit.Medic, get the wounded to the back.No!It's not that bad.I can...Don't push yourself too hard.All of our comrades are willing to fightso we don't have to leave anyone behind.
```

### [65] hash=`27cb042d1447ac13`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
trust me alright all wounded fall back team three take their position lay downsuppressive fire comrade really is right we won't leave any of our comrades onthe battlefield it'd be a shame if we didn't get to see you cry at thevictory celebration got it the scale of your soul has tilted thebalance needs to be restored we made it good jobComrades, they will be talking about this day for decadesI didn't expect that energy from you comrade Yuri
```

### [66] hash=`f411dec4311017f0`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
See, I don't only build houses.I also build this rock-solid barMake a head count of the wounded and check our remaining suppliesWe will need to work in groups of three in case the creatures come backThank You comrades all of you the glory goes to every one of usVictory is secure.I should excuse myself.We...make it.After we drove the critters away, the self-purification system began to run slower.Ha ha!
```

### [67] hash=`459ab24bf253d4ec`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Time to go, all out!Let's go, comrades!Brighter future!Comrades here!Its energy has not run out yet.What on earth?It's the ore!Damn it, don't tell me it's still powering this thing!I see.So we just break that stone, and it's over, right?Yes.Theoretically.Leave it to me.I'm the marksman here.Just need to get a little closer.Little closer.Comrade Adrian, comrade Daniel, and I will go with you.There may be something we can do.
```

### [68] hash=`fc9d4c979a4a0d87`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Okay.Believe.Our attacks cannot break this stone at all.The cycle of lay energy is long.It may take months, years, or even longer than that to return to its source.As long as that ore remains on its neck, the lay energy will continue with the purification until it wipes out everything around.So all we can do is wait?For our own safety, we'd better stay out of this area until it completely returns to the source.
```

### [69] hash=`206e435e5a45ba36`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I should have seen this coming.I'm so sorry.Comrade Patrick, Comrade Ikita, you're not down yet, right?Anyone else?We still got the digger, the crane, and our own strength.Let's try harder.It's nothing more than a stupid stone.We can do this.That's our last chance.Stop this senseless sacrifice, Comrade Knut.It's pointless to keep going.But to save Ryashka is also your dream, no?Our little one from afar swore she would unite all of us, no matter who we are or where we're from.
```

### [70] hash=`5309d527b97e6a5c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
We must keep all that in our minds.How can we give up now?I'm so happy I came here and made friends with all of you, comrades.You each have a kind heart and a strong will.Before I met you, my dream was only a joke to the others out here.But you've shown me it isn't unreachable.Now it feels so real and heartwarming.Sometimes I almost forget that you see the fins and scales on my body.That's why I don't want you to sacrifice yourself for nothing.
```

### [71] hash=`2785fc8f2d15161a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I don't want to lose him.What we want is to stay together.That's why we're fighting to save Ryashki.Right?Damn it!Wands have lost their feathers.Are you still able to reach the sky?I must thank you, Robert Winslow.You've rekindled something in me, in us.I will tell you that I read some papers on your lay lights after midnight.It holds some great ideas, I admit.You and Ryazhkin deserve a better future.
```

### [72] hash=`7474a6d753cda7d5`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I want you to know, I recommended you to Zeno only because I was worried for your future.I did not want you to be stuck in a dying town.And it gives me pain to see how brave and determined you all have been.I won't let any of you die here.Yevgeny, what are you doing?The sad thing is, I took a very different path long ago.But what does it matter now?Ryashki is proud of you.I am proud of you.You will continue to build the new world of your dreams.
```

### [73] hash=`9d7a0818672cf15c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Our dream.No matter where or when.I will always be there with you.Seize the opportunity.Vila, wind zone, my comrades!Comrade Evgeny...This is not fair!Just because he was the only pilot here doesn't mean he could make that decision alone!We should have had a vote!We fixed that fighter together!That asshole left us behind!But he will always be our comrade, right?Evgeny, salute!Here's the sea swallow!
```

### [74] hash=`874f4d02ea5dff05`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
He flew into the future, child.The future will all reach one day.Comrade Evgeniy.Everything he did was for Ryashki.We shared the same dream, didn't we?To do all we can for the good of the people.Reporting.Drilling reclear.Ready for new exploration.That's the spirit.We must keep going.All the period.Yuri, start the machines.On it!You'll be glad to have another best friend.I don't like you!It's a promise!
```

### [75] hash=`7a3c58daad21f1f1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Are your feathers wet, Piotr?Face, Ms.Winson.Can kids still cry after they grow up?I should have known.The abnormal fluctuation of the ley energyand how much of an attraction it is to the critters.I should have noticed they were different from my theory.At least this experience will be valuable for the study of ley lines, won't it?Take it in and make something of it.I am sure it will be of more help in the future.
```

### [76] hash=`e8d7a9c4c073e8c1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
You're not only doing this for yourself or for me,but for those who sacrificed for all of us.Resource!Coal!It is coal!We did it!This is our coal!Comrades, we will use it to cook our meal tonight.And it will be the best meal I've ever had!Is that so, comrade Nikita?You got a problem with my food, huh?I made a rough estimate.The resource here should last hundreds of years.For the first time in history, the theory of ley lines has been verified.
```

### [77] hash=`ba0daa3690307a33`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
There is no doubt your work deserves a fair assessment now.Thank you for your help, Ms.Vila.We achieved this together, didn't we?Of course, the glory goes to every one of us.I'm very glad to see you again, Ms.Vinson.Are you?You don't look glad at all.I admit, I underestimated the people here.Especially you, Ms.Vinson.The great heroine who found coal deep beneath the town, huh?So, did I manage to ruin Zeno's little plans?
```

### [78] hash=`d5f980d5b86ac44b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
We have nothing left to do here.Sino will leave soon.I know we disagree on many things.Our future included.Still, Sino looks forward to working with you again, hopefully in a more friendly way.I hope so too.You don't want to be embarrassed by another lowly researcher again, do you?Goodbye, Ms.Vinsong.Wait!I have one last question.Please, I'm at your service.Zeno confirmed the existence of Hoytuks in Rayashki months ago,
```

### [79] hash=`5ec02eb2ea494201`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
but you just took care of them without letting anyone know.You already knew there would be a large reserve of coal here, didn't you?For thorough discussion, the people of Rayashki have made their final decision.I stand here to declare the future direction of Rayashki.As of today, Rajashki will be no longer affiliated with any organizationsand all factories dedicated to processing of Runium Orb will be shut down.
```

### [80] hash=`9a4ee012fb7b78bf`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
What are we going to do for work, Sam?I don't want to sit around at home living on benefits.There will be many things to do, comrade Valeria.As the elites above us struggle for power, we ordinary people suffer in darkness.But now there will be a new source of power, one built to lift up the people, not to take from them.And it will run on Rayashki coal.We will start new factories in Rayashki and explore the possibilities of working with other coal producers nearby.
```

### [81] hash=`6dea6c1e859a4685`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
We will mine with our own hands and feed ourselves.Maybe we can even build a dock and sell our products far away.We will raise a new banner above Rayashki.One welcoming all ordinary peopleto come to a livable place with abundant powerand job opportunities for their future.What about your plan, comrade Winsong?I think I'm going to stay for a while.You need to know that for now we must tighten our belts.
```

### [82] hash=`67995f207b898be6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Everyone's rations must be cut for some timeuntil Rayashki gets back on its feet.At least for now, the study of lei lines belongs here, not in the fancy halls and symposiumsof human academia.This place still holds many possible research avenues, monitoring the changes in the environment,further detailing the local lei energy map, maybe even studying the mutation of the Kikituks.I must finish them to further develop the study, before it is ready for academia again.
```

### [83] hash=`a5ccb81c2259b794`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Then it sounds like you may be with us for a long time yet.Good.And don't forget, you were expected to cut the ribbon at the ceremony.I want to apologize for being rude to you during class.I'll bring you some friendship cheese next time.To apologize, I promise.You will always be our comrade.Hats off to you.You performed very well at the ceremony.Will you come teach us again?We want to learn more too!
```

### [84] hash=`1832d2ac8c45413c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Right here!Miss Winsong!The sunflowers we planted are blooming!We protected the town!We begin the next chapter of Ryashki today.I'm so glad we will build it together.Oh, thank goodness!I was hoping you'd be here.Oh, um, is this a bad time?No, it's alright.Have a seat.I'm not a pure Rusalka.As you can see, I must get in touch with water every once in a while to replenish my power from the ocean.Hello, comrade Vila.
```

### [85] hash=`8bccd76dd5fcc831`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
It's been a while, comrade Vinson.They say you're working hard in the mine, and the study of ley lines is getting popular among the workers.They have helped a lot.My research on the environment wouldn't have gone nearly so smoothly without them.It's given a second life to my studies, and it is growing so well that it has even gained some recognition beyond Rayashki.I am truly happy that I came here.
```

### [86] hash=`9a18fa51f3a20a99`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I never thought the comrade Winsong would be so bashful over her accomplishments.I thought you were more stubborn and confident than that.Only teasing, comrade.It's a matter of fact that you're not as fearless as you pretend to be, isn't it?That's why we must all stick together to make up for each other's weaknesses and make Ryashki proud.Sorry.Speeches have become an occupational habit.Fine, you got me.
```

### [87] hash=`2adbde7b2ef573cc`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
But it's not a big deal.Just as you are not quite the gentle and demure schoolteacher that you appear to be.Are you, comrade?We're even.Actually, I've come to say goodbye.Laplace has invited me to give a lecture for their European branch.They want me to give a lecture on how I combined environmental analysis with the arcanum,based on what we've done here in the Ryashki.Sounds like a very promising new beginning for your studies.
```

### [88] hash=`c95f9079a97c2b04`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
How are things going in the town?We are getting more visitors now.It seems people are eager to see something different.I'm sure they will.We've also begun cooperating with many governments and agencies near us, including the Foundation.They hope to carry out some short-term training on the Arcanum for the children.What's this?Open it.It's from the Foundation.Mr.Nameday invites me to visit the Foundation and discuss further cooperation.
```

### [89] hash=`fee430228c207578`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
The children are also waiting for me there.It seems they mentioned you all the time during their training.Did we miss the ley line exam?The foundation has all sorts of incredible things.Like biting coins, noisy corbels, a glass pen with rainbows inside.So much fun!I've mastered a lot of incantations!I missed the town and everyone.We miss comrade Alyonka, comrade Blinchik, and comrade Pirozhki.They say we will be able to go home in a few months.
```

### [90] hash=`749b6dc5297c1ed9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
I must master the most powerful arching skills by then so I can use them to protect the town.We'll transform into sea swallows.Then we'll be able to fly and fly to far, far away.Because Linska University Hospital received their rare case today,The patient's veins irreversibly transformed into electric wires.As of 1800, all arterial, venous, and capillary tissuesthroughout the patient's body have undergone necrosis.
```

### [91] hash=`ab7bf4bcc4bf2e09`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
The directors said they would invite more professionals to the consultationto decide on further research direction.Global Variety News has claimed the case may becomeone of the greatest unsolved mysteries of the era.They started a new column to analyze possible compatibilitiesbetween the patient's new wired veinsand different appliances.Please stay tuned for more details.The Flying Carpet Travel Agency
```

### [92] hash=`13ae6af136782c12`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
is starting a tour around Northern Europewhere you will be able to seethe breathtaking aurora borealis,pet fluffy key cairns,and even enjoy a flying carpet race.The destination of our tour is Ryashki,a mysterious town,the warmest place in the Arctic Circle,sitting atop many rich veins of coal.When you get there, we suggest that you abide by the town's wishesand work to earn what you need instead of buying it.
```

### [93] hash=`9acb44e8aa0429c2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
Though this is not an obligation, of course.But why not have a try when you're given the opportunityto experience a new and better lifestyle?Trust me, you won't be disappointed.Where should I start, dear readers?Ryashki is like a sparkling gem embedded into the permafrost, and above flies an eye-catchingbanner, perhaps it will draw even more attention in the future.Through the past decades, the citizens there have been trying to achieve something different
```

### [94] hash=`649f9d268e94728f`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p57`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 16~19）

```text
for themselves, a great cause which may take the work of generations to achieve.But now, they are no longer a nameless town in the far north, nor is their dreama passing fad bound to be forgotten.I sincerely hope all of us will be able to witness itshistory and its future.That's why I knew I must write down this story, in the hopesthat their dream will remain in your heart forever.
```

