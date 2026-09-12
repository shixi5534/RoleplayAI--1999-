# 剧情图谱抽取 · batch 043

- 角色：`wu_ming_zhe`
- 批次：**43** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.8」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_043.jsonl`

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

### [0] hash=`3765b83421c530d3`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
See how it comes out from underneath the ground and goes into the local biosphere, circulatingaround like a system.If we think of the town's ley lines as a food web, then ley energy lies at its foundation.Like how big fish eat small fish, and small fish eat even smaller fish.Exactly!They are the smallest fish eaten by the big fish.If we catch the big fishand study what they eat, we will know where to find the other big fish.
```

### [1] hash=`7f53fba24462ae2f`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
And the lay energy,I mean when the big fish die and break down, the small fish will go back to where theyfirst came from.The circulation goes on and on.You've put it very well, Ms.Wimson.Like the rain water that comes from the ocean to the rivers and returns back to the ocean.You're a quick learner.But it is not exactly like water.The concentration of light energy is far more noticeable than that of a lake or a
```

### [2] hash=`e37a510053814a85`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
school of fish.Once we find its densest spot, we will be able to trace it back to its source.And what are these bright spots?These are the energy-rich locations.In a way, they indicate the energy flow.So many look like stars in the sky.Yes, and finding these locations can be very costly in terms of time and manpower.And what do we do after finding them?They can tell us many things.The Lay Hunters will follow their courses, analyze the components in them, and match
```

### [3] hash=`39fe2d876365611e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
those components to each resource.Some of the components don't matchwith any of the known resources,which means there might be a new resourcewaiting to be discovered.Of course, from the late energy,we can also learn about the local critters.You talk about strange things, almost like Avgus does.These are just lions.Dancing earthworms.Here you go!They're having fun!Jumping on the waves, then into the little boxes, and back into the little balls.
```

### [4] hash=`b922e322264e60ed`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Great!We have two of them now.Interesting, but we don't really understand.Cheer up, kids!It's not finished yet.Leyline cartography is complicated.It takes the efforts of many ley hunters working together,investigating the area, even braving dangerous and forbidden places.To this day, we've never been able to finish a completed Ley Energy map.Here is the swimming pool.That little square is our square.
```

### [5] hash=`c533a8f681226820`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
These little balls are our homes.I live here, the third ball on the left of yours.You're very bright, Avguz.This is the Ley Energy map of Rayashki.Rinsong, why are you mapping the energy of our town?Have you found any secrets that we don't know?Children, right now you can only see what's above the ground.But there is even more lay energy beneath the ground.Will the sun always be in the sky?Will the glaciers ever melt away?
```

### [6] hash=`2d315af3aaaf2f13`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
What lies in the darkness beneath us?Are there other critters around here that you've never seen?How should we deal with them?I heard once that there were many strange footprints next to the school windows.Uncle Patrick saw it.A monster with six legs and each one has spikes.That must be a cichirn, a small-sized canaday critter, mostly seen in cold areas.But the lay energy might have affected the weather of their habitat,
```

### [7] hash=`2bdc2e46307e5da9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
or they wouldn't be here in Ryashki in summer.The deep blue line here shows that particular one's movement.Maybe Uncle Patrick could have drunk too much.The lay energy accumulated in them suggests that they mostly feed on moss and wormsunder the snow and stay near town.We can infer that this is a docile herbivorous kind of critter that is merely curious abouthuman behavior.I think feeding them will be much more useful than driving them away.
```

### [8] hash=`e099cebe97259c91`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Since these creatures began to overrun the area, the defense team has encountered many new creatures.I can feel there is something strange about them.But I can't yet understand the differences.You provided a different angle on the situation, Miss Windsong.I believe it would help the defense team greatly.The tires in the furnaces are out, the pinkites dance around the pond, white moss is on the wall, oh, oh...
```

### [9] hash=`e31224be5652e2f6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
I think they changed things, Avgust.The defense team will keep the critters out of town and protect everyone.And there will not be any stones falling from the sky.Is everything alright, Piotr?You're lying!Ryashki is safe.It will be your home forever.I hate to tell you this, kid, but what Avgus just said could be right.I have the same feeling that the good weather here won't last too long.Look at those thick gray lines.
```

### [10] hash=`82b4d46afaca68b6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Those are the traces of cloud movements and moisture.Now they're mingled together.But the sun will still be shining.Ms.Vila said that the polar day will last for a very, very long time.Ms.Vila was right.And past statistics don't lie.According to the data, the weather here should continue for the next few months.Yet the ley lines say otherwise.They say the weather will be extremely unpredictable.You are making things up.
```

### [11] hash=`63b16a6ae0973d49`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
The forecaster on TV said the weather in the Ashki will be comforted in the coming months.And the weather forecaster was right, according to his analysis, but life is full of surprises.I know why you're concerned, Ms.Wensong.I feel the glaciers are melting slightly faster than usual.There is going to be a warm front forming from the melting water.Will there really be stones falling from the sky?I can't say anything for certain just yet, kid.
```

### [12] hash=`c71a7f81748538a1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
All I have is this incomplete map, and as you can see many sources of the marksand traces haven't been located,which means we can't come up with a precise calculation.But there's no questionthat Ryashki will soon face many challenges.The weather could become much worse.The environment might change.Maybe some unknown critters might turn up.Ryashkis are home, so it can be dangerous.You can't fly if your feathers get wet.
```

### [13] hash=`f1d9601b39b8f0e0`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
They will need some time to take inall this new knowledge.Don't you agree I thought I could handle all their questions.I think I made things worseSorryHave faith in themThey will come around.Are you here to laugh at me all these stories of monsters and falling stonesThey aren't good at all.overheard mr.Evgeny talkingHe said the town has so many problems and soon what some people think will decide our future
```

### [14] hash=`dbcec7fbd7108afe`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
If people believe in those terrible stories, maybe they will be scared and they won't come back to Ryashki.Everything will be forgotten.I wasn't lying.Hello, Pikiru.What?What are you doing?I will draw attention.You go find a defense team for help.It's itchy.It feels warm, doesn't it?Miss Windsong said they can be our friends.That they will bring seeds to every corner of the town.Like a gardener?Plant more sunflowers, Kikirin!

So, Ms.Winsong was not a liar.
```

### [15] hash=`69766b0118e238ac`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Do you really think it's a good idea to turn to Zemo for help?We have drawn almost every man and woman from the mining facilities to get rid of the critters nesting around the port.Most of the defense team were injured.Some lightly, but others got much worse.It will be weeks before they can return to duty.If an attack like the one at the rehearsal happens again, I'm not sure we will be able to protect ourselves.
```

### [16] hash=`b00e419bfcdbf6b5`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
I know most of our people are frustrated with Xeno's arrival, but I expected better from you, Vila.People trust you, and they will follow you, but that doesn't make you right.Maybe you're still too young to see the dangers.I might be wrong, but history is a long lesson in learning what is right through being unafraid to be wrong.Sadly, we don't have time for a trial and error.And this is your excuse for making decisions for us against our will?
```

### [17] hash=`521c25ee5c3b09de`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
I will hold myself responsible for my decisions.In that, you have my word.Today is the day of our welcome ceremony.Vila said when the bell rings, the important people from the Tortoise Academy will arrive.Everyone looks excited.Nina has put on her best dress.I know she'll be great on stage, but Sona will do all with Piotr.It's his duty to protect the princess.As for me, I got a new job from Mr.Afghani.
```

### [18] hash=`70931f4c636b1b5d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Salute!Shake hands and give them warmest welcome.What this?They're bubbles in the water.Again, Kikirin, are you planting sunflowers under the water?Have you brought your friends?Your friends also have six legs!Look, they're wearing needle grass and flat files on their legs.Are you also here for the ceremony?Come, Kikirin and friends, come to the prettiest town in all of the Yarte, the Yashki.Please, enjoy yourself!
```

### [19] hash=`b9159320c6a6116e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Comrade Avgust, what are you doing?Whoa!I'm welcoming the Kikirn!Get out of there!They're dangerous!Defense team, drive them away!Wait!These are Kikirn!They're not aggressive, they're just curious about us!The kids seem to like them!Get rid of them!As you command, comrade!The Kikirns are all gone!I think they don't like us anymore...Comrade Yevgeniy, take the kids back to where they were comrade Vila.
```

### [20] hash=`1bc3a80bbf4b30de`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
It was your duty to protect them.Maybe if we make the town a better place more friends will come back.Then they will also come back.Make sense.The family of Kikirin includes dozens of subspecies, but none of them are so greatly adapted to water as this.That is to say, they might also be affected by the lay energy under Ryashki.Pity that they were driven away.There was much we could have learned from them.
```

### [21] hash=`ef15a9911ccadde3`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
The temperature here is rising much faster than expected, and much earlier in theseason.I imagine if you asked the weather bureau, they would say this is just an odd occurrenceof unseasonable weather outside of expected ranges.It's time.The Xeno investigators should be here any minute.I must stress again how important this ceremony could be for our future.Our town's economy is facing a cliff.And I am sure each one of you has noticed the increased rationing.
```

### [22] hash=`40a27ae70b1f7a43`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
If we wish to take care of our people in the future and protect our friends and familyfrom these frequent creature attacks, we need Xeno's support.So we will work with Xeno, because we must.The future of Ryashki is in our hands.So is the future of every comrade here.And we need the cooperation of every man and woman here.Zeno's ships are very fast.So as soon as they appear on the horizon, our ceremony will begin.
```

### [23] hash=`33da5235f8c2fd33`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Understood!Zeno is late.So late that Ms.Volova said they were absent.Do you think something bad happened to them?What are they doing there?Oh, like a polar bear's head.Poor bear, losing all his hair.Can there be snow in summer?Is this related to the strange thing Avgust said earlier?If so, I'm happy that these aren't stones or a dark cloud spit.Can't believe it!You were never right before.Oh, it's chilly.
```

### [24] hash=`727ba1591ac9a26a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
The snow is biting against my skin.I'm sorry, Avgust.I shouldn't call you a liar.But will Ryashki really get into trouble?We are there.We will not be defeated.Not by clouds or bears.This is walking very slowly.But no one has left their position.Ryashki, those ones must go back to their...Go as fast as you can.We will.Don't forget your own job.August.Say it again, comrade.It's a pleasure to speak to you all, our valued friends in Ryashki.
```

### [25] hash=`913fc3e64592970c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
On behalf of Zino Arms Academy, I am here to announce the details of the Zino-Ryashkicooperation agreement.As many of you have expected, a squad of armed troops will soon be sent to aid you with thecritter problem.However, having given it careful consideration, we have decided that the town of Rajaskiis no longer viable for our continued support and must be abandoned.We advise that all residents prepare to be transferred to a new post immediately.
```

### [26] hash=`2bd03b6c1cd71748`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Mr.Bertholdt.Call him yourself, Villa.You must be mistaken, my very passionate friend.Sino sent a warning months ago.The estimated value Rajaski can add to Sino's programis less than satisfactory.Further support is no longer recommended.Should any new valuable resources be found in the region,please reply to this letter as soon as possiblefor further assessment.Then we heard back from Rajaski.In fact, the sender was...
```

### [27] hash=`fd7042eef3fbff22`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
you, Evgeny.Yes, it was.And it was you yourself that argued the most compelling point, I have to say.One that has drawn the higher-ups' attention, and the reason why I was sent here.I believe you wrote,I have total faith in the quality of the people of Ryashki.Their solidarity, dedication, and motivation have proven invaluable to us.I am certain they would carry those same strengths of character and skill to any post no matter
```

### [28] hash=`735b5830a95f76f3`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
where they were assigned.Xeno accepted my application.Of course, I asked around before making my submission, and Xeno seemed to havereputation.It was a golden opportunity to join them.It is, but do not get uswrong.Our entrance requirements can be mostdifficult to meet.Zeno only takes in the best of the best.You want some of usto work for Zeno?You never told us anything like that!Yevgeny!Bereasonable, Vila.
```

### [29] hash=`32f31298cdc67e42`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Some of us deserve this opportunity.All the others!We haveelders and children some of our comrades have been injured and even died in themine are we to forget their sacrifices relax my friend that's why we sent ourvery best biological control squad we will escort you to the nearest shelterface reality Vila I know how much effort we have put into building thistown and I understand you have this dream to fulfill but we must prepare
```

### [30] hash=`15abc0346e427680`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
for the worst, we may have to give up on our rayashki.Read this.Field investigation has confirmedthat the remaining ronium reserves in rayashkiare around 0.0173 kilotons,which is less than 0.275% of our average annual output.The mine is located high within the Arctic Circle,which has entailed significant transportation costs.The harsh environment is also wholly unsuitable for building any permanent processing facilities.
```

### [31] hash=`51b047d166bb8c39`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
In addition, military spending on the region has recently been elevated 3.61 times dueto increasing animal and critter attacks, and that number is still rising.Clearly, the region is now incapable of self-management.According to the Guide on Global Humanitarian Aid by the Office for Disaster Risk Reductionof Zeno Arms Academy, we propose to send a special squad to the region to evacuateall local citizens and subsequently take care of the remaining biological control issues.
```

### [32] hash=`c33d6c6f0f9839c3`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
And our admission standards will be lowered, at Zeno's discretion, so that you willwork harder than your new positions, no matter what.You shouldn't rush to a decision.We are discussing Ryashki's future here, Yevgeny.For six decades, the people herehave put in great efforts to turn the towninto what it is today.We won't leave just because you tell us so.Our grandparents didn't even have construction equipment
```

### [33] hash=`65131e48db04902e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
at the beginning.They built these houses with their own hands.We shipped over the planting soil.We built walls to keep out the wind and snow.When you came here, you brought books for the children and introduced us to a speciesdifferent than humans.You became one of us.I'm not happy about this either, Comrade Führer.I won't buy that, Comrade Evgeny.This is not just about my dream, but everyone's dream.
```

### [34] hash=`03724d26c09a0a87`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Or have you forgotten what Ryashki was meant to be?A utopia built for and by everyone, the voice of a better future, one which would soundacross the land and seas.I remember every word of it.You have my sympathy, friends.Sino has also suffered huge losses in many regions.We have lost manpower, territory, armament factories, and even some of our affiliatedmilitary schools.Rayashki is but one of these losses.
```

### [35] hash=`af4135eebd3722b7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
We know how you feel right now, but Sino hashis own problems to be faced.And investing in these new industries,purchasing fancy equipment, all these things Rayashki will need.All of thistakes money, and even Sino must be economical.Shouldn't the people inRayashki also benefit from these global benefits Sino has promised?WeWe will get there, my friend.Maybe slowly, but we will get there.Trust me, Xeno has done everything they can for you.
```

### [36] hash=`ec4b47708248a93a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
We need to keep our eyes on our goals and stay on the right courseso that we won't get lost in these turbulent times.Yes?I know how much faith these people have in you,and I believe you can show them a different perspective about these coming changes.Of course, this will also help you during Zeno's assessment.Good luck, my friend.Reserves of Runium running dry.The appearance of new critters.The sudden snowstorm.
```

### [37] hash=`b4b8ebf2f2b6eea1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
I have connected the ley lines of each of these phenomena.The map is nearly complete.But still haven't traced many lines and marks back to their source.Perhaps if I go back to the factories, into the restricted zones.But I can't do that alone.Definitely not when the situation in town is so unstable.I should have given this up long ago.There's no chance that the study of ley lines will ever be accepted again.
```

### [38] hash=`8ccf422f117aada3`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Regretfully, Ms.Wensong, with nothing but these outdated files and materials to backyou up, there's simply no way to justify reinstating the study of ley lines intoour curriculum.We don't have unlimited funds, and we must save our money for projects with greater potential.The study of ley lines is...Of course, we might be able to consider new ideas and projects, but you can't be allowedto do this on your own.
```

### [39] hash=`f94036daedaa6c2c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
You will need endorsements from the Institution of Geographic Studies, the Arcane CreaturesSociety, or other such organizations.Let me think...Xeno seems to be interested in Geographers recently.They just recruited a number of researchers for a new commission.Maybe you should go try your luck with them.Submission date is getting closer each day.But I've made poor progress.Xeno won't endorse me if I can't find a breakthrough.
```

### [40] hash=`6a283d8b2c442f2d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
They have become more and more radical and desperate lately.First they sent those researchers here to conduct their haphazard studies,and now an armed force?And all this effort just to chase the rumor of some source of perpetual energy?That this perpetual energy source must be hidden somewhere beneath the permafrost?If higher-ups call the shots, all they need to do is spread a little honey in the right places.
```

### [41] hash=`18b8aaf1a2be0128`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Then all the little researchers will swarm on it like flies.But could there really be a magical power source like that?Whether there is or not, I still have a map to finish.There's no way that I can map every ley line in the region all by myself.Goodbye research funds, goodbye lectures and seminars, and so long to my dreams of being chair of the Geographical Perspectives Forum.What was that?Finsong, we've been waiting.
```

### [42] hash=`50cfcde88ab7a578`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Finsong, we prepared a special medal ceremony for you in August.Please, come to our ceremony.We just wanted to thank you for teaching us.Miss Villa was right.We shouldn't have been so quick to argue.We should have listened.So you should be given an award for being right.But our ceremony will not be as big as the ones on TV.Miss Winsong, will you accept this medal?I have no cup to put this medal in, so we can't toast with it in celebration.
```

### [43] hash=`c60e98fcda980f47`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
now I know no matter what I won't be returning empty-handed thank you kids doyou mean are you leaving us so much you still need to teach us but I ask himbraces every guest including you miss winston don't you like it here thosethings I heard at the welcome ceremony won't we all be leaving soon and leaveStranger was mean, he wasn't our friend.This is Artan.They can't speak for us.Miss Fela invited the men from Xeno to leave his ship.
```

### [44] hash=`31803a468e392c71`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Then they went into Mr.Afgini's meeting room together.Uncle Knut promised me that Novan will give up this place.They will go to many meetings and find a solution that satisfies both sides.The tortoises move slowly.They need to keep their eyes opened and lookfor a better answer.So, will you stay and teach us?I won't cause you any more trouble.I promise.Hmm?Bad Calculator speaking.Hello, Bad Calculator.
```

### [45] hash=`82cf9f2b28252a9b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Are you giving the Earthworms directions?What's going on here?Oh, my calibrator!The whale-like backbone,the diamond-shaped teeth,two short legs with dim eyesand an extremely sharp nose.That must be a Kikidook.But their closest habitat should be Conkarl's land,hundreds of kilometers away.Their marks on the map appear to be red,sort of reddish brown,and there's a large amount of light energyaccumulated around them.
```

### [46] hash=`2e2a00b050df774e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Clearly they're high on the food chain.Seems like the small fish have attractedmore than one big fish.Kids, get behind me.The Kikirks are giving a performance.There are no scenes.There are four dances.And their belly shakes.But why aren't their ears doing anything?Avgust!What are you doing there?Stay back!Those are not Kikirn!They are left behind.They...they...they can't join the dance.Not get their halyonka.
```

### [47] hash=`22686197903feed6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Ears?Pryroda eti cisla i cierty!So that seems to be their weak spot.Good job, little one.You're even more perceptive than I thought.Next?This was one of the last working instruments I had!Be sad, Miss Winsong.If we plant them in the soil, more will come out when spring comes.Thank you, Avgust.Miss Winsong, can I be a layhunter too?If we were as good as you are, maybe we could have protected your machine.
```

### [48] hash=`a46b62182368e851`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
And maybe we could protect our town.Kids, lay hunting isn't a good profession.If you become a lay hunter, you will have to deal with doubt from all your peers,even hatred and homework that piles up to your roof.People in the Yashkia are taught not to doubt or hate others.They would never hate you or us.Would you let us show you around, Ms.Viansong?We haven't had many other visitors here since the critters started coming near the town.
```

### [49] hash=`5a7fa6fa9dd516b7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Get the blind lady once.She always smiles, and she has a pretty typewriter.Villa said she's a...writer.The writer has been to many towns, and she fills up her papers with so much ink, just like I do.So, I made the drawing for her, too.And she promised us that she will tell more people to come visit Ryashki.Will people from other places like it here?What about your other visitors?I remember they had green and red rectangular paper and some shiny cookies in their hands.
```

### [50] hash=`226884b02a272e23`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
They tried to trade us their silly papers so they could take our cans and things.They never wanted to work with their own hands.And Ryashki doesn't like lazy bones.Vinsong, Richard got all of us together last night and we read for our how to be a good tour guide guide.We can guide you.Miss Vinsong is just a bit strange.She's not lazy.Olagyi, let's not hurry onto our awards, Avgus.We haven't helped Miss Vinsong yet.
```

### [51] hash=`6daaeab9cabc4a51`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Right.Good to see you at our little factory, Miss Vinsong.Hello, sir.The kids have told me that you want to learn more about the history of Ryashki and thestrange things that have happened in the past, yes?I do, but would that be going against any rules?Most certainly not, miss.We are not some stubborn old goats that dismiss people for asking questions.In fact, I'm relieved.It will be much easier to talk to you than that bitter fellow from Xeno.
```

### [52] hash=`df2354d5f5b804e6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
He came to the factory with his armed squad, took a quick look around, and left even without a polite farewell.Like a whiff of cold breeze that went.Outdated machines and hundreds of workers, young and old, each one a mouth to be fed.They are certainly not a pretty sight to the eyes of that gritty hyena.Pathetic number crunching cretin.I am starting to like you, Miss.We would have much to talk about.
```

### [53] hash=`47965bf407ebe3e0`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Perhaps over a drink.If only I didn't have to get done with my work.You can see what's going on here, right?Don't feel sorry for us.Xena might no longer need this ore processing factory, but we can make use of what's left of it.Once we get rid of the critters, we can arrange for other minerals or materials to be shipped to Rajashti for processing.It is a shame we've wasted so much of our good years, never preparing for these bad times.
```

### [54] hash=`931661d8b1f2ce0c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
If those strange little monsters weren't there, we might be able to return to our mines.Then, we'd really be able to turn things around.About these mining sites...Mr.Canute, have you ever found anything there, other than Runium ore?Zeno soon sent out some troops and caught all the monsters.They didn't leave asingle one behind.We never heard about those pebbles again, nor have we foundmore of them in the mines.
```

### [55] hash=`1bbd4087f92b1ff2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Not the rest.Now we've exhausted the runium and moreand more strange looking critters have appeared.So it's not safe to go backthere.We left them completely deserted.Take a look at this Mr.Knute.No noMany of the other workers have seen it.So, the color of Ahoytuk is bright yellow, and that matches with these bright yellow lines I've traced here on the map.They are burrowing animals, often living as deep as 50 meters underground.
```

### [56] hash=`e55a2ab7953ad09e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
So if they were here, that must mean that there must be some undiscovered resource here.Talk of undiscovered resources would be music to our ears, miss.I don't want to get your hopes up.It's still too early to draw any conclusions.we will find a way to drive those critters away and start production once again.We have all our brothers and sisters with us, and these machines still run perfectly.As long as we continue to put in our best effort, there's no reason why things won't get better.
```

### [57] hash=`9ad37b47f0e717ee`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Is this exceptionally positive spirit common with the people here?Well, can't blame us for that.There are very few places in the world like Rayashki.Here, everyone earns their food and their rest through working hard together.Then outside of work, ice hockey, learning courses, even music lessons.Not everyone is as lucky as us.That is why we won't let Ryashki die.With busy hands and open hearts, Ryashki will live on.
```

### [58] hash=`87f5fc7a6d94db03`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
It will grow stronger, glowing as brightly as these furnaces.I have to say, Rajaski is truly a curious place.It has a spirit which I've never found elsewhere.Yes, perhaps that's what was missing from the study of ley lines in the past.Would you like to meet Mr.Patrick?It's time to go to the canteen, boys and girls.Eat well and you'll grow strong.Patrick knows how to feed you well.He's the best cook in town.
```

### [59] hash=`503952d73a41e0d8`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
But I would suggest you be careful with that one, if you don't want to get stuck with his endless chatter all night.I have never been to the canteen.I stayed out of that area in my previous visits to avoid unwanted trouble.Forward to comrade Blinche.Das korev sreci, miss.I look forward to hearing good news from you.This is our canteen.We play hide and seek here when we're hungry.Comrade Stu and Potato Kiroshki are always the easiest to find.
```

### [60] hash=`d6f92945e5e427d6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
They're not very clever, kind.But Comrade Linkshit is very good at the game.He can only be found at dinners on Friday.Like mashed potatoes and boiled potatoes and potato stew.Mr.Patrick said, a good cook can turn even simple ingredients into delicious food.Grown-ups are so kind to us.Sometimes they give us their cheese and salad, so they only have potatoes to eat.When you share your elenco with everyone, when we grow up, it will be our turn to help the grown-ups with their potatoes.
```

### [61] hash=`045a591dc4d43e18`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
We're all so happy, didn't we?When they give us metal, half the food in them.August, it's called the Virgos Festival.We have it every month.Everyone must sit in a circle in the canteen and sing songs.And Miss Villa plays the accordion for us.We each get a can of food in it.Sometimes it's a shanka, sometimes it's salad, sometimes sprouts.After the Teen Hat Festival, we would bury our teen hats in the ground.
```

### [62] hash=`eea4735a8d8ec83b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Yellow ones, red ones, and white ones.Then tiny trees will come out from them next year.I have told you many times, they are not tin seeds, and they don't grow into trees.They are just tin cans.We only bury them so they won't pollute the snow.Tiles of tin cans.Food.Those empty cans you mentioned, did you store them here?I know this place.That's where the adults dug a big hole.They put some things inside, it's covered up with rocks and ice now.
```

### [63] hash=`e2d48471998582aa`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Yes, Basono is right!That's where the grown-ups put all our old metal after they make them into little cubes.Miss Vila said it helps keep our town and the whole region clean.Why?What's wrong with that place?I'm thrilled!There must be lots of big fish left to be found around there.If I can write a report, and provide a practical plan, maybe I can get the- I mean, I couldrequest reinforcements.This is no trip, children.
```

### [64] hash=`c9859368f3589364`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
I'm not going there for a hike.You must stay in town and be good.That goes for every one of you.Understood?Quiet, kids!Attention, please.Tomorrow at 8 in the morning, we will be holding our final hearing.In this meeting, we hope to finalize our next steps and answer any remaining questions.We look forward to seeing you then.What's this?Are you planning on getting a job with Xeno too?It says here you've been staying in this town for months, but it seems you're not on our list for potential recruitment from Ryashki.
```

### [65] hash=`b342476ca997debd`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
I should remind you, for you researchers, what you produce tells much more about you than your efforts.That's precisely why I'm here.Why else would we ask you to investigate here in the first place?Do you have anything else to report?No, but I do need your help.I will need an armed squad to come with me to the mining sites so that I can continuemy investigations into this subject.I'm afraid I don't know how long it will take.
```

### [66] hash=`c873555d2c8efe9f`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
It also depends on the number of soldiers you can spare for the task.You have a terrible sense of humor.I'm not being funny.You want more research on the new resource too, don't you?Miss Vinson, do you really think this is even a remotely reasonable request?Critters are running rampant in the area and you demand help to verify what is, as faras I can see, a highly questionable conclusion.Why should I base Xeno's time and resources on this?
```

### [67] hash=`5e621a2dd79ffc28`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Not to mention putting the lives of our soldiers at risk.If you have doubts, please take a look at these filesAnd let me guess you learned all this from your study of ley linesTo date the theory of ley lines has neither been approved by the arcane study review associationNor accepted by the project assessment of human science and technologyIt has zero academic achievements zero endorsements and aside from the questionable example in front of me
```

### [68] hash=`02ad057b1f3df3c9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
So, then you never planned on controlling the critters here?The squad you brought here was to control the town?A force sufficient to deal with the critters would have attracted and wanted attentionfrom our rivals.It is not in our interests to share this town or its resources.I'm sure you can see that.So even if we do find the resource for you, you won't leave this town or itspeople alone?We are talking about the ultimate energy source of Arcanum.
```

### [69] hash=`1651c631c16df86e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Do you think we will just walk away and leave it to be squandered by a bunch of ignorantpeasants and miners?You should be ashamed of yourself.What we are going to do with Ryashki should be of no concern to you.We have made every arrangement for you.We aren't monsters.Before the final decision is made, we will continue to help the locals as much ascan, including you.You seem surprised.Isn't it what you have always wanted?
```

### [70] hash=`9db865f076c303f2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
With Zeno'sendorsement, you will be able to teach your program in any university.We have preparedthis gesture of our good faith in you.Now, it's your turn to show yours.Forget aboutan armed squad.They have more important things to do.You're on your own, my friend.Once I fill the gaps in my data, I will be able to pitch it to Zeno and all subsequentresearch won't be a problem anymore.The primary food sources for hoi tuc are raw minerals underground.
```

### [71] hash=`d47c4c07d6f74bfe`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
Those processed metals only keep them from starving to death.They wouldn't have gone across any icy ocean just to gnaw on old equipment and trash.All I need to do is find a trace of their activities so that I can learn aboutOf course, I hope the outcome will be different this time.Before all that, I need to clear out this place.Shoot.Now I've done it.Those vestigial-digging teeth, the three-fingers long-tearing teeth, these are not hoi tuc.
```

### [72] hash=`1c0f7b2dbf3e4bc6`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
These scaled wings must be for swimming.Get out!Get out of here!I'll cover you!Thank you, sir.Yevgeny, the kids told me about a canpile.Is it nearby?Canpile?They must be talking about our waste metal.I'm afraid it's gone, Miss Vinson.Maybe animals dug it all out, or maybe those little monsters ate it.Do you know if that happened before or after the Runian mines ran dry?I'm not sure.You shouldn't be here.
```

### [73] hash=`5b8009a82b9e1b54`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
There's nothing of value to find in this place.And you're not supposed to be using this arcane equipment here either.We have a better way to deal with these fierce little monsters.What you're doing will just attract more of them.You can drive away the Kiki Toks?Not anymore.We don't have much left to fight them off with.Zeno didn't bring any equipment for our team, let alone any weapons.You have lived in Rajashki for a long time.
```

### [74] hash=`3042ab7becabfc73`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p55`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 5~9）

```text
You know what commitment means heremuch better than I do.I won't give it up so easily.Just like the people herewon't give away their land like nothing.It's stubbornness.That's all.Theyshould have gone to other places and put their talents to good use ratherthan stay here to fight for nothing.Is that why you gave away the town soIt's my responsibility to protect everyone, to do right by them.I will make them see it tomorrow at the hearing.
```

### [75] hash=`73dbf9e4989fdaa9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
People of Rayashki, my dear friends, good day to you all.Over the past two days, Sino has assessed the potential risks and benefits in the areaand held hearings on what should be done about the future of this town.Our hearings saw very limited attendance.We've taken that to be a gesture of approval.Mr.Evgeny has put in a great effort helping to make these changes happen.We all owe him a great deal.
```

### [76] hash=`dbc4ee3570903964`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Thank you, sir.Please believe that we have made the best decision we could for you.We all know the Runium here has run dry,and the land has been exhausted of all further material wealth,now and into the foreseeable future.As a result, your local processing factory has lost its intended purpose.What's more, Sino has changed our cooperation strategy.Though your town's loyalty will never be forgotten, we must have a sober-minded view of its costs and benefits.
```

### [77] hash=`bfdefd5fdf7ec8d1`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
To sum up, our final decision is that we will be ending operations and all future cooperation between Zeno and Rajasthi.Well, Mr.Bertolt, you have just got here.Perhaps you didn't have enough time to get to know us well enough.Ryashka's value is not just in the Runium.We have many other factories too.Yes, you have a brick factory, a power plant, many forklifts, a smattering of conveyor belts.But all these were all built and suited for only the processing of Runium ore.
```

### [78] hash=`fd240156b7412885`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Without the ore, they simply have no benefit to us.Now that you have full knowledge of the situation and our intentions,We want to assure you that your loyalty has not been forgotten.So we have generously prepared two choices for the future of Rajasthan.Firstly, Sino believes that you have many valuable qualities.The determination and skills you've shown in the past year of our cooperation haveproved that your people can be a great asset to us.
```

### [79] hash=`52b212c9d773766f`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Indeed, many of you already meet the entrance requirements to join Xeno.Therefore, on behalf of Xeno Arms Academy, I wish to extend a heartfelt invitation to you.Leave Ryashki, join us, and work for one of our other branches as members of Xeno.What are you saying?You want us to abandon our home for some promise of a job?Calm down, Mr.Knuth.This is not about abandoning your home.It's about joining us in our efforts
```

### [80] hash=`0bc8c6dd0f8235b7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
to contribute to world peace through a more optimized allocation of manpower.So you're just going to pack us all up and ship us away to work for Zeno?You misunderstand, madam.Every year, Zeno dismisses 4% of our employees becausethey failed to pass our rigorous work reviews.And the number of our colleagues that arehim in the line of duty is even larger still.Working for Sino is a privilege, not a gift.
```

### [81] hash=`2e537894de510972`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
That's why only a small number of you will be allowed to come and work for us.What?Now according to article 58 in the section on protection of Arcanist rights signedat the Event Horizon Convention, we provide basic supplies for any residents who haven'toffered a position with Zeno.They will be transferred immediately to the nearest reliefstation until our social workers contact them for further arrangements.
```

### [82] hash=`359a11250723778f`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
So then you're suggestingyou will send our children and elderly away to some kind of refugee station?And the rest of us must go to work for Zeno without any questions?RIDURAK!This is total rubbish!Sir, please lower your voice.Well, you would be glad to know that your work experience in particular is valuable to CINO, Mr.Knoot.If you're not interested in our first plan, we have another.If the residents in the area prove reluctant to relocate, CINO can offer another alternative.
```

### [83] hash=`52106532de388b4c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
As stated earlier, Rajaski is a remote town that possesses some significant industrial infrastructure.Therefore, it could be considered an ideal location for a new complex of arms factories.There would be a need to substantially upgrade the Rajaski wharf to turn it into one of the seaports Sino plans to build across the globe.Additionally, a radio station will be constructed within the town,Our resources as much as anyone's are limited and they must be put to good use.
```

### [84] hash=`85721a111263055a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
We cannot afford to waste them on strategically useless, costly people and places.If you've found Sino to help you, you should be able to give us something in return.Don't you agree?So Yevgeny, this is the best choice you made for all of us?Ahem, I must speak in Mr.Afghani's defense.He is committed to his duty, and only wishes to do what he can for his compatriots.Shame us!All you've done is sold us out!
```

### [85] hash=`8adc7e27446486ec`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
You tell them, Knut!Do you think it's getting a bit windy lately?Clearly, with all the hot air in Afghani's head, his mind has been blown away!I swear to you, I'm not doing this out of my own interest.Comrades, there are many better places in this world, and you have better purposes tofulfill.You shouldn't waste your time here.Let's all calm down, my friends.It's time to be reasonable.Think carefully.
```

### [86] hash=`1e775dc5b5b776bf`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Sino has been very generous regarding the offers before you.Generous?Now that's ridiculous.We won't let you take away our family and friends, nor are we about to let youour town into a puppet state.We will stay here, no matter what.Comrades, I understand how you feel right now, but we must face the cruel reality ofour situation.And you're willing to send away our own people or give up on all that's built here
```

### [87] hash=`c935134f60220582`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
because of this so-called reality.It is the only way forward.If we continue to stay here without any help, it will be the end of us either way.Do we have to turn to Zeno for this help?The truth is, just as Ryashki's economy has been dependent on Rui, we remain dependenton Zeno.Without them, at the present rate of consumption, we will be out of supplies and materialswithin a year.The situation looks bad.
```

### [88] hash=`1ae08fb2736f8a96`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Zeno is determined to gain control over this place, but if I complete the taskCasino requested, does it mean I will shatter their dream?And what about my dream?Did the people who refuse to acknowledgethe study of ley lines act out of the same self-interest?I've seen this happen so many times before.A simple dream is made to face a cruel realitywhere the clever ones give up and leaveand the stubborn fools remain waiting to be crushed.
```

### [89] hash=`06495406b870da83`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
We have to fight for our misery.But I am, Miss Villa.With all due respect, I can't complete this task alone.As any ordinary researcher, I can relate to them.Please, forgive me for interrupting.I have heard so much about Rajaski these days.They started from nothing, but bit by bit they accomplished the impossible.Their voice should be heard.Pryroda at a chisla i chertei.Mr.Boto, we can't hold them any longer.
```

### [90] hash=`f6e8385ec6a1da47`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Now, will you listen to me?We don't need your help.Your soldiers and your tyranny are no longer welcome here.Comrades, what do you say?Shall we solve the problem with the strength of our own hands and hearts?What else can we do?This is what we've always done when there was a problem.There will be more solutions than problems if we work together.If I must die, I will die here with all of you.Just stop talking nonsense, you idiot.
```

### [91] hash=`d5103f89cb92b62f`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Nobody is going to die.Rayashki belongs to all of us.We will stand with it till its last moment.They might say they're just ordinary people, but they are so brave and noble.Could I really have traded the future of these people away from my ley line studies?Zeno...I was a mule chasing after a carrot on a stick.They lured me here all so I could help ruin everything.You seem to be in a good mood.We taught Zeno a lesson.
```

### [92] hash=`2d2450b68b6011d2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
They were forced to leave with their devil's bargains and tail stuck behind them.We fought back, finally.A nice little trick that was.Thank you, comrade Winsong.We all know who the mysterious hero was that gave us a helping hand.I...I didn't do anything.It's no shame to have helped your friends, not to mention to stand up to Xeno.Have more confidence in yourself, comrade Winsong.But will you really gain anything from this fight?
```

### [93] hash=`8d51b51e7fb6b662`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
Not sure.But we have to do something, right?That's why I'm here.To talk to me?I don't know why, but Ms.Vila, you must have thought too much of me.In fact, I'm only a simple researcher.I'm not powerful enough to change Zeno's decision.You are the one thinking too much, comrade Blenso.Your Ley Line lessons were much more popular than you think.They have had a positive effect on the children.Now they are looking at the bigger picture
```

### [94] hash=`fcdeeae2eb48c794`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p56`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 10~15）

```text
and observing the world in a more detailed way,you'll unleash their curiosity.Is the aurora the bubbles spit out by the stars?They form such a beautiful map.Do they study ley lines too?But it remains the case that the study of ley lines has never been verifiedfor all its ambitions.Only a limited number of people studied it in the past decades,and that number is decreasing even now.What you're looking at is not some skin problem, but my past, my past as a Rusalka.
```

