# 剧情图谱抽取 · batch 042

- 角色：`wu_ming_zhe`
- 批次：**42** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.8」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_042.jsonl`

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

### [0] hash=`163154a87d53f68c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
0.0173 kilotons, which is less than 0.275% of our average annual output.The mine is located high within the Arctic Circle, which has entailed significant transportationcosts.The harsh environment is also wholly unsuitable for building any permanent processing facilities.In addition, military spending on the region has recently been elevated 3.61 times dueto increasing animal and critter attacks, and that number is still rising.
```

### [1] hash=`cb298af8ae8f4cca`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
Clearly, the region is now incapable of self-management.According to the Guide on Global Humanitarian Aid by the Office for Disaster Risk Reductionof Zeno Arms Academy, we propose to send a special squad to the region to evacuateall local citizens and subsequently take care of the remaining biological control issues.And our admission standards will be lowered at Zeno's discretion, so that you will
```

### [2] hash=`982667d4ab932ac6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
all find work with us somewhere.I'm sorry, but this is reality.From the start, this ore was the only thing they wanted from us.The environment here has always been harsh for mining.But we overcame it and sent our shipments to wherever Zeno had need of them.And I salute each one of you for your work, my friends.But now, our mission is over.I believe all of you will continue to work hard in your new positions, no matter what...
```

### [3] hash=`9cc86bbaa5438cda`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
You shouldn't rush to a decision.We are discussing Ryashki's future here, Yevgeny.For six decades the people here have put in great efforts to turn the town into what it is today.We won't leave just because you tell us so.Our grandparents didn't even have construction equipment at the beginning.They built these houses with their own hands.We shipped over the planting soil.We built walls to keep out the wind and snow.
```

### [4] hash=`0a072ea2c376a504`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
When you came here, you brought books for the childrenand introduced us to a species different than humans.You became one of us.I'm not happy about this either, Comrade Vilar.I won't buy that, Comrade Evgeny.This is not just about my dream, but everyone's dream.Or have you forgotten what Ryashki was meant to be?A utopia built for and by everyone.The voice of a better future.One which would sound across the land and seas.
```

### [5] hash=`7728abd948f99625`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
I remember every word of it.You have my sympathy, friends.Sino has also suffered huge losses in many regions.We have lost manpower, territory, armament factories, and even some of our affiliated military schools.Rayashki is but one of these losses.We know how you feel right now.But Sino has his own problems to be faced.And investing in these new industries, purchasing fancy equipment, all these things Rayashki will need.
```

### [6] hash=`122b9777b8c12ca7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
All of this takes money, and even Zeno must be economical.Shouldn't the people in Rayashki also benefit from these global benefits Zeno has promised?We will get there, my friend.Maybe slowly, but we will get there.Trust me, Zeno has done everything they can for you.We need to keep our eyes on our goals and stay on the right course, so that we won'tget lost in these turbulent times, yes?I know how much faith these people have in you, and I believe you can show them a different

perspective about these coming changes.Of course, this will also help you during Zeno's assessment.Good luck, my friend.
```

### [7] hash=`5480d5c6b1429d54`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
The reserves of Runium running dry, the appearance of new critters, the sudden snowstorm.I have connected the ley lines of each of these phenomena.The map is nearly complete, but still haven't traced many lines and marks back to theirsource.Perhaps if I go back to the factories, into the restricted zones, but I can't dothat alone.Definitely not when the situation in town is so unstable.Well, I should have given this up long ago.
```

### [8] hash=`a653176c030c1736`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
There's no chance that the study of ley lines will ever be accepted again.Regretfully, Miss Wensong, with nothing but these outdated files and materials to backyou up, there's simply no way to justify reinstating the study of ley lines into ourcurriculum.We don't have unlimited funds, and we must save our money for projects with greaterpotential.The study of ley lines is, of course, we might be able to consider new ideas and projects.
```

### [9] hash=`549238976a370aa6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
You can't be allowed to do this on your own.You will need endorsements from the Institution of Geographic Studies, the Arcane CreaturesSociety, or other such organizations.Let me think, Xeno seems to be interested in geographers recently.They just recruited a number of researchers for a new commission.Maybe you should go try your luck with them.Submission date is getting closer each day, but I've made poor progress.
```

### [10] hash=`95f6702b3d8c1653`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
See, no one endures me if I can't find a breakthrough.They have become more and more radical and desperate lately.First they sent those researchers here to conduct their haphazard studies,and now an armed force?And all this effort just to chase the rumor of some source of perpetual energy?That this perpetual energy source must be hidden somewhere beneath the permafrost?If higher-ups call the shots, all they need to do is spread a little honey in the right places.
```

### [11] hash=`6814d92162d8a2a6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
Then all the little researchers will swarm on it like flies.But could there really be a magical power source like that?Whether there is or not, I still have a map to finish.There's no way that I can map every ley line in the region all by myself.goodbye research funds goodbye lectures and seminars and so long to my dreams ofbeing chair of the geographical perspectives forum what was that songwe've been waiting for song we prepared a special medal ceremony for you in
```

### [12] hash=`22428013bb669314`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
August please come to our ceremony we just wanted to thank you for teachingus miss Villa was right he shouldn't have been so quick to argue weof listen so you should be given an award for being right but our ceremony will not be as bigas the ones on tv miss one song will you accept this medal i have no cup to put this medal inso we can't toast with it in celebration now i know no matter what i won't be returning empty
```

### [13] hash=`2243954a72022ca6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
Thank you, kids.Do you mean, are you leaving us?So much you still need to teach us!But Ayashki embraces every guest, including you, Miss Vinson.Don't you like it here?Those things I heard at the welcome ceremony.Won't we all be leaving soon?Then leave it.Stranger was mean.He wasn't our friend.This is Artan.They can't speak for us.This fella invited the men from Xeno to leave his ship.Then they went into Mr.
```

### [14] hash=`2c4d5af7c23db26f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
Afgini's meeting room together.Uncle Knut promised me that Novan will give up this place.They will go to many meetings and find a solution that satisfies both sides.The tortoises move slowly.They need to keep their eyes open and look for a better answer.So, will you stay and teach us?I won't cause you any more trouble, I promise!Bad Calculator is speaking!Hello, Bad Calculator!Are you giving the Earthworms directions?
```

### [15] hash=`0c6ae7cc6f658223`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
What's going on here?Oh, my calibrator!The whale-like backbone, the diamond-shaped teeth, two short legs with dim eyes and an extremely sharp nose...That must be a Kikidook!But their closest habitat should be Concarl's Land, hundreds of kilometers away.Their marks on the map appear to be red, sort of reddish brown, and there's a large amountof light energy accumulated around them.Clearly they're high on the food chain.
```

### [16] hash=`a04589373f1e370c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
Seems like the small fish have attracted more than one big fish.Kids, get behind me.The Kit Kats are giving a performance.There are no sins, there are four dances, and there are belly shakes.But why aren't their ears doing anything?Avgust, what are you doing there?Stay back, those are not Kikirin.They are left behind.They can't join the dance.Not get their aviunka.Ears?Priroda eti čisla i čerty.So that seems to be their weak spot.
```

### [17] hash=`e4b03dca146a8eff`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
Good job, little one.You're even more perceptive than I thought.Next?This was one of the last working instruments I had!Be sad, Miss Winsong.If we plant them in the soil, the moral will come out when spring comes.Thank you, Avgust.Miss Winsong, can I be a layhunter too?If we were as good as you are, maybe we could have protected your machine.And maybe we could protect our town.Kids, lay hunting isn't a good profession.
```

### [18] hash=`332ce8b5e1265eaf`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p7`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（07【纸奖章】）

```text
If you become a lay hunter, you will have to deal with doubt from all your peers,even hatred and homework that piles up to your roof.People in the Yashkia are taught not to doubt or hate others.They would never hit you, or us!
```

### [19] hash=`a5666fb93d840b43`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
We're happy that you let us show you around, Ms.Viensong.We haven't had many other visitors here since the critters started coming near the town.Bet the blind lady wants.She always smiles, and she has a pretty typewriter.Villa said she's a...writer.The writer has been to many towns, and she fills up her papers with so much ink.Just like I do.So, I made a drawing for her, too.And she promised us that she will tell more people to come visit Ryashki.
```

### [20] hash=`0ee32f7aa1bde455`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Will people from other places like it here?What about your other visitors?I remember they had green and red rectangular paper and some shiny cookies in their hands.They tried to trade us their silly papers so they could take our cans and things.They never wanted to work with their own hands.And Ryashki doesn't like lazy bones.Vinsong, picture got all of us together last night, and we read for our how to be a good tour guide guide.
```

### [21] hash=`21ac6dac69339b14`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
So, we can guide you.Miss Vinsong is just a bit strange.She's not lazy.Hey, Olagie.Let's not hurry on to our awards, Avgus.We haven't helped Miss Vinsong yet.Night.Good to see you at our little factory, Miss Vinsong.Hello, sir.The kids have told me that you want to learn more about the history of Ryashki and thestrange things that have happened in the past, yes?I do, but would that be going against any rules?
```

### [22] hash=`8f26e10387d4b46f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Most certainly not, miss.We're not some stubborn old goats that dismiss people for asking questions.In fact, I'm relieved.It will be much easier to talk to you than that bitter fellow from Xeno.He came to the factory with his armed squad, took a quick look around, and left even without a polite farewell.Like a whiff of cold breeze, that one.These old, outdated machines, and hundreds of workers, young and old, each one amount to be fed.
```

### [23] hash=`0edb783de01bde35`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
They are certainly not a pretty sight to the eyes of that gritty hyena.Crunching cretin.I am starting to like you, miss.We would have much to talk about.perhaps over a drink.If only I didn't have to get done with my work.You can see what's going on here, right?Don't feel sorry for us.Xena might no longer need this ore processing factory,but we can make use of what's left of it.Once we get rid of the critters,
```

### [24] hash=`292e7a6301d4b162`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
we can arrange for other minerals or materials to be shipped to Ryashki forprocessing.It is a shame we've wasted so muchof our good years, never preparing for these bad times.If those strange little monsters weren't there, we might be able to return to our mines.Then we'd really be able to turn things around.About these mining sites...Mr.Canute, have you ever found anything there, other than Runium ore?
```

### [25] hash=`0357af769f19d672`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Never.I know those sites like the back of my own hand.I've never seen any other minerals of any worth there.But give it some time, miss.Well, give me some time.Just a few months ago, back when Xeno was still into work with us and not just shipus away, I remembered I found some strange little pebbles.Dark pebbles that were stuck in the clothes of those little monsters.Xeno soon sent out some troops and caught all the monsters.
```

### [26] hash=`3b715f9ad8ef2bb9`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
They didn't leave a single one behind.The color of ahoy took is bright yellow and that matches with these bright yellow lines.I've traced here on the mapThey are burrowing animals often living as deep as 50 meters underground.So if they were here that must meanThat there must be some undiscovered resource here talk of undiscovered resources would be music to our ears missUm, I don't want to get your hopes up.
```

### [27] hash=`67e7a95691e762d1`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
It's still too early to draw any conclusionsHahaha, yet the corner of your mouth is suggesting the opposite.I must be cautious before confirming there really is a new resource.Nonetheless, it's a silver lining.Thank you, Mr.Knute.Think nothing of it, miss.Maybe one day you and your research will return the favor.If I can, I hope your work here can be resumed shortly.Don't worry about us.we will find a way to drive those critters away and start production once again.
```

### [28] hash=`38af5b88d5e119a4`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
We have all our brothers and sisters with us, and these machines still run perfectly.As long as we continue to put in our best effort, there's no reason why things won't get better.Is this exceptionally positive spirit common with the people here?Well, can't blame us for that.There are very few places in the world like Rayashki.Here, everyone earns their food and their rest through working hard together.
```

### [29] hash=`b5843ac758753cb3`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Then outside of work, ice hockey, learning courses, even music lessons, not everyoneis as lucky as us.That is why we won't let Ryashki die.With busy hands and open hearts, Ryashki will live on.It will grow stronger, glowing as brightly as these furnaces.I have to say, Rajaski is truly a curious place.It has a spirit which I've never found elsewhere.Yes, perhaps that's what was missing from the study of ley lines in the past.
```

### [30] hash=`925e06b90cb4d116`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Would you like to meet Mr.Patrick?It's time to go to the canteen, boys and girls.Eat well and you'll grow strong.Patrick knows how to feed you well.He's the best cook in town.But I would suggest you be careful with that one.If you don't want to get stuck with his endless chatter all night.I have never been to the canteen.I stayed out of that area in my previous visits to avoid unwanted trouble.Forward to comrade Blinche!
```

### [31] hash=`320b6bba8d4521da`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Das korre fstretche, miss.I look forward to hearing good news from you.This is our canteen.We play hide and seek here when we're hungry.Comrade Stu and Potato Kirovsky are always the easiest to find.They're not very clever, kind of.But Comrade Linkit is very good at the game.He can only be found at dinners on Friday.Like mashed potatoes and boiled potatoes and potatoes stew.Mr.Patrick said a good cook can turn even simple ingredients into delicious food.
```

### [32] hash=`5bb7df2d2429c30e`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Grown-ups are so kind to us.Sometimes they give us their cheese and salad so they only have potatoes to eat.When we show you a link with everyone, when we grow up, it will be our turn to help the grown-ups with their potatoes.We're all so happy then, when they give us metal-happy food in them.It's called the Vorkus Festival.We have it every month.Everyone must sit in a circle in the canteen and sing songs.
```

### [33] hash=`ea472a942d2440ca`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
And Miss Villa plays the accordion for us.We each get a can of food in it.Sometimes it's a shanka, sometimes a salad, sometimes sprouts.After the Teen Hat Festival, we would bury our teen hats in the ground.Yellow ones, red ones, and white ones.Then tiny trees will come out from them next year.I have told you many times, they are not tin seeds and they don't grow into trees.They are just tin cans.
```

### [34] hash=`a809d54be47d8a33`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
We only bury them so they won't pollute the snow.Tons of tin cans.Food.Those empty cans you mentioned, did you store them here?I know this place.That's where the adults dug a big hole.They put some things inside.It's covered up with rocks and ice now.This is no trip, children.I'm not going there for a hike.You must stay in town and be good.That goes for every one of you.Understood?Quiet, kids!Attention, please.
```

### [35] hash=`e41111b6619c517f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p8`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（08【工厂颂】）

```text
Tomorrow at 8 in the morning, we will be holding our final hearing.In this meeting, we hope to finalize our next steps and answer any remaining questions.We look forward to seeing you there.
```

### [36] hash=`47f53431a07dff63`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
What's this?Are you planning on getting a job with Xeno too?It says here you've been staying in this town for months, but it seems you're not on our list for potential recruitment from Ryashki.I should remind you, for you researchers, what you produce tells much more about you than your efforts.That's precisely why I'm here.Go on.Based on the recent investigations, I'm confident that there is a new energy source in the area that has yet to be discovered.
```

### [37] hash=`14a194a1bdef8e27`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
And that's it?We already believed there was something here when we sent you out in the first place.You were sent here to find it.Instead, all you do is confirm what we already knew.But you said that perpetual energy was just a myth, didn't you?Of course it wasn't just a myth, lady.Why else would we ask you to investigate here in the first place?Do you have anything else to report?No, but I do need your help.
```

### [38] hash=`7084d2e1bface8ec`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
I will need an armed squad to come with me to the mining sitesso that I can continue my investigations into this subject.I'm afraid I don't know how long it will take.It also depends on the number of soldiers you can spare for the task.You have a terrible sense of humor.I'm not being funny.You want more research on the new resource too, don't you?Ms.Vinson, do you really think this is even a remotely reasonable request?
```

### [39] hash=`7b88229d185daf66`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Critters are running rampant in the area and you demand help to verify what is, as faras I can see, a highly questionable conclusion.Why should I base Xeno's time and resources on this?Not to mention putting the lives of our soldiers at risk.If you have doubts, please take a look at these files.And let me guess, you learned all this from your study of ley lines?I...To date, the theory of ley lines has neither been approved by the Arcane Study Review Association,
```

### [40] hash=`f0edb5d49139ecc0`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
nor accepted by the Project Assessment of Human Science and Technology.It has zero academic achievements, zero endorsements,So then you never planned on controlling the critters here?The squad you brought here was to control the town?A force sufficient to deal with the critters would have attracted and wanted attentionfrom our rivals.It is not in our interests to share this town or its resources.I'm sure you can see that.
```

### [41] hash=`88f07e57b3896b0b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
So even if we do find the resource for you, you won't leave this town or its peoplealone?We are talking about the ultimate energy source of Arcanum.Do you think we will just walk away and leave it to be squandered by a bunch of ignorantpeasants and miners?You should be ashamed of yourself.What we are going to do with Ryashki should be of no concern to you.We have made every arrangement for you.We aren't monsters.
```

### [42] hash=`59a1a66dccfc9b26`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Before the final decision is made, we will continue to help the locals as muchwe can, including you.You seem surprised.Isn't it what you have always wanted?Vezino's endorsement.You will be able to teach your program in any university.We have prepared this gesture of our good faith in you.Now, it's your turn to show yours.Forget about an armed squad.They have more important things to do.You're on your own, my friend.
```

### [43] hash=`ecc8054fb9bc8bde`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
But prove to us that you can do this job and bring us the best answer you can give.And this piece of paper will be yours when you complete your mission.I understand.See that you do.Good luck out there, Miss Windsong.I...out of my mind?He was just trying to get me out of his office.He threw a carrot out of the window and I chased right after it like a blindedmule.Still, maybe this carrot is too good to let go.
```

### [44] hash=`9281b887b4bc1d92`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Once I fill the gaps in my data, I will be able to pitch it to Zeno and all subsequentresearch won't be a problem anymore.The primary food sources for Hoi Tuc are raw minerals underground.Those processed metals only keep them from starving to death.They wouldn't have gone across any icy ocean just to gnaw on old equipment and trash.All I need to do is find a trace of their activities so that I can learn about their current conditions and from there
```

### [45] hash=`8900ec734a9caa2c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Locate their other food sourcesStay calmHoi took our gentle creatures.They rarely attack humans.I just need to be cautiousCity, okayAll right change of direction if I were to look down instead of looking forwardMaybe I should scan the area and follow where the lay energy is leading.Just like I did at Silbury Hill.Of course, I hope the outcome will be different this time.Before all that, I need to clear out this place.
```

### [46] hash=`2056620a41862ac2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Nature is a mosaic of flowers!Now I've done it.Those vestigial-digging teeth, the three-finger long-tearing teeth...These are not hoi tuc!They perceived my approach even though I used my ley line reader as a dampener.Get out!Get out of here!I'll cover you!Thank you, sir.Evgeny, the kids told me about a can pile.Is it nearby?Can pile?They must be talking about our waste metal.I'm afraid it's gone, Ms.
```

### [47] hash=`b45f77579bbe2835`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Winson.Maybe animals dug it all out, or maybe those little monsters ate it.Do you know if that happened before or after the Runian mines ran dry?I'm not sure.You shouldn't be here.There's nothing of value to find in this place.And you're not supposed to be using this arcane equipment here either.We have a better way to deal with these fierce little monsters.What you're doing will just attract more of them.
```

### [48] hash=`513ba8f0faadb584`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
You can drive away the Kiki Toks?Not anymore.We don't have much left to fight them off with.Zeno didn't bring any equipment for our team, let alone any weapons.Go.Leave before it's too late.What if I don't want to just give up?I've seen your residence application.You say you are a researcher.Then you should be clever enough not to go down a fruitless and dangerous path.I admit that what I am doing here is reckless.
```

### [49] hash=`05ba04e38bdf129b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
And maybe I'm just motivated by my own selfish interests.but I can't just walk away from my commitments.You have lived in Ryashki for a long time.You know what commitment means here much better than I do.I won't give it up so easily.Just like the people here won't give away their land like nothing.It's stubbornness.That's all.They should have gone to other places and put their talents to good use.
```

### [50] hash=`9c23905b98fa0b56`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p9`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（09【比知识更重】）

```text
Rather than stay here to fight for nothing.Is that why you gave away the town so easily to Zeno?Do you really even know your neighbors?I have lived and worked together with them for decades.Don't be ridiculous.I just...I agree with Zeno's perspective.I've been to many places and I have encountered many people like you.Stuck up leader types, making decisions on behalf of other people because it's what's

good for them.And they should listen, just as you should now.It's my responsibility to protect everyone, to do right by them.I will make them see it tomorrow at the hearing.
```

### [51] hash=`874bac4a24493958`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
that navy blue color it's a mutant so that's why they've sent me heresomething is wrong with this town Ryashki is a town on an island near theNorth Pole peaceful and free from strife the decades has prospered frommining ore but the ore has now run dry without the ore Zeno will no longer support usI once traveled to a small town called Ryashki.It was located high up within the arctic circle, and it was frigid cold all year long.
```

### [52] hash=`1fa50d494b44e12a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
After my visit there, I traveled to many more places, from Zeeland to the Balkan Peninsula.My journey went on and on, but above all other places, I kept finding my thoughts returningto that little town, to its incandescent lights glowing in the long dark of thePolar Night, to the shared dream of the people there.I got this picture book from Ryashki.It is a children's book, a thin one at that, but story inside has the power to warm a frigid
```

### [53] hash=`5129745995671b79`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
heart.Once opened, wells of bright primary colors run into one another and flow up onto mypalm.I found myself returning to it during stormy days when I was stuck at home.This is a story about honest and ordinary people.The swans are dancing in a circle, their arms go back and forth.Vila and the swans have done this dance almost 20 times last week.She taught the swans all their beautiful moves.Swan lift is the best ballet ever.
```

### [54] hash=`12b8ea573e8a7976`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
I remember Mr.Afghani once said so.He also said the tortoises would come to watch the show.Why would tortoises want to watch one lake?Says she doesn't like the tortoises.She likes knowledge.I don't know much about knowledge.But I think Ms.Vila is always right.Only between you and me?Vila smells like seaweed and coral.Those are happy smells to me.I think she must be the princess of the ocean, but she tells us she is not special
```

### [55] hash=`bf6893a0cc571e55`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
and that everyone here is equal who matter if they are a princess or aswan.That we all have two feet and ten fingers and if we all work together wecan build the peak into the future.I hope in the future we still get toand dance when we are not building beacons.Ina's favorite food is calledAlonka.It's a chocolate bar.She used to cry a lot whenever she made a mistakewith her dancing, but then Vila talked to her and now she doesn't cry so much.
```

### [56] hash=`b9ff9fc548a8d239`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
One time she danced very very perfectly, so Vila gave her a piece of anAlonka bar.I believe she will be a great dancer if she doesn't get tooon stage then she could have even more chocolate.I wish I was like her.I wantchocolate too, but I'm not a swan like her.And now there's never any Elionka onthe canteen's cupboard.Now Nina is the swan princess, the mostthe gittiest of all swans.Bassano is the swan prince.
```

### [57] hash=`5dff7cda84d7f5b3`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
He is a nice one, and he has many many swan friends, and Piotr is the evilsorcerer, a black swan.Nobody wanted to be the bad guy,but Piotr doesn't mind.He is very serious and always bossy to everyone,so he doesn't have many swan friends.Peter just wants to do his job as perfectly as he can, cause he loves our town.Now, of course, he's not a swan, but he also loves his town.Then there is a little mouse, who moves as quickly as the blowing wind.
```

### [58] hash=`f8aa6c24c4be8065`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Will it be our new visitor?What was it that Vila said about new visitors?I don't remember now.Reporting to you, comrade Vila.I have a very important question.Well then go ahead, little comrade Avgust.Do we receive the new visitors coming to town?Maybe we can welcome them with Salienka?Or friendship?Or maybe something else?We will welcome them with white snow, with smiles on our faces, and with welcoming arms we use to achieve our dreams, as we do for everyone who comes here, little comrade.
```

### [59] hash=`724a5f7a1621150b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
It's always good to ask questions, but don't forget your task today, alright?My drawings are important, but Vila says entertaining our new friends is also important.One comes first.After the swans have flown away,Evgeny will go up to the stage.Evgeny is not an evil sorcerer,but he knows a secret magicthat makes everyone's tongues hide in their mouths.He is not so much a bad person, I think.Evgeny's shadow is very long,
```

### [60] hash=`2063a30e552ec412`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
but no one,Not even my sunflower can explain why.Afghani walks heavily onto the stage.His appearance comes without any applause.We have received a telegraph.Zeno's investigators will arrive here in Ryashki tomorrow afternoon.And we will be hosting a welcome ceremony.I understand your concerns.I know you don't want Zeno to interfere with your lives, nor do you want their troops stationedhere.And I would remind you that they have honored their side of the deal for decades now.
```

### [61] hash=`24050ae7b1a4e66b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
We give them runium ore and they supply us in return.It should be as simple as that.Always it has been this way since my grandfather's time.Times have changed, comrade Knut.In the old days, Zeno used to pay us generously for mining the Cerunium, because our ore wasnecessary for the Arcane Combat Vehicles.But now, we have nearly exhausted all our mines.You know this better than I do.But isn't there some other work we can do?
```

### [62] hash=`08ba459a42655066`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Already we build our own houses, and now we even grow our own crops.He's right.Why must we work with Zeno if we could feed ourselves?Comrades, calm yourselves!Evgeny is doing this for everybody's sake.Have you forgotten about those little monsters?Is there anyone left on our defense team that hasn't been injured fighting them?It is as comrade Nikita said.The critters are running rampant these days.
```

### [63] hash=`13d4f965bc2dd157`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Not only have they occupied most of our mines,some have even found their way into the town.Do you really think we can protect our people with our small defense team?Don't you care about your neighbor's safety?Do you want to keep Rayashki, an isolated town, just to let it die?Rayashki is more than an isolated town, Evgeny.And we all know that.But this is the reality we all must face now.It was your idea to turn to these, you know, big guys for help.
```

### [64] hash=`a8a34fb8a3ea02c7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
But you never even asked what we think, did you?So you can't blame us for disagreeing now?I'm doing this for your good.We can take care of ourselves.Everyone, watch out!Defense team, on it!I salute your sense of smell, comrade Vila.We could have suffered much more severe consequences without your forewarning.Think nothing of it.It's just a reflex reaction when there's danger nearby.But this incursion has proved my point.
```

### [65] hash=`5404c9ff85fb33ab`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
We need Zeno's help.The other townspeople are not gifted with your set of talents.We are all vulnerable to the growing dangers.Wouldn't you agree?I only ask you to put yourself in their shoes.Your criticism is valid and well accepted, comrade Evgeny.Perhaps I could agree with your plan.Provided Zeno's presence is a temporary one,we just don't want them to change things for us here.I'm glad that you have finally come to realize what is best for us.
```

### [66] hash=`e613dc5a051a9f48`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Zeno is known for their rigorous methods and rational decision-making,and they are committed to maintaining peace around the world.I'm sure they will make the right decision.They trusted us to supply their ore,and we have faithfully played our part in supporting them.Thanks to our help, Zeno has successfully tackled many international issues.It has always been them and us together, fighting for a better world.
```

### [67] hash=`7fa7a9afe3b30ce2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
When he puts it that way, he is right.We should be proud of our cooperation.Therefore, we will show our appreciation to Zeno for the contributions they've made to the world with our help.Now let's continue our rehearsals.Have you seen Avgust?I can't find him.Where did he go?Hmm, looking for any Alenka left in the cupboards, I bet.He's always breaking the rules, doing whatever he wants.We shouldn't talk badly about our classmate, Pilter.
```

### [68] hash=`3ce3a43ac49e8554`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
He's one of us.Yes, you're right.I just wanted everyone to do their best.Even him.Don't worry, kids.We will find him.A child is missing, comrade Evgeny.I suggest a temporary suspension of our rehearsals.Ah, it must be that strange kid again.He's always sneaking away like this.He's only trying to understand the world in his own way.Villa once said that sunflowers mean warmth, and that makes them everyone's friends.
```

### [69] hash=`2dda1b5242e4b97d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
They would warmly welcome every guest that comes to town, just like my best friend here, right?Ah, friends.Everyone should have a best friend.Now here are big, small friends, many, many friends.So that our new guests won't feel so lonely when they come.Amazing.I've never seen such a highly mutated Ejirak before.I would have missed these precious research opportunities if there weren't a gathering in the town.
```

### [70] hash=`c8006d60993b0298`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
The wind song seems like life has been good to you and your theory.The disorder and lay energy here has not only caused the exhaustion of the Runian mines,but has also mutated local critters to varying degrees.Hmm.Then Xeno was right.No wonder they have sent so many researchers here to look for abnormalities.Even the crank ones like me.It's obvious that this town has more to it than a handful of overly active critters.
```

### [71] hash=`b24ca3bab807b3b4`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
But they don't seem especially interested in the mutant ones either.Dino, what were you looking for here?Let go of my leg!You're not a fox, and you're not a sable.Hey, kid, what are you doing?Oh, shoot.Ejerax are usually known for their good temper.It seems to not apply to their mutant kin.Fine.Priroda et a chisla e cherti.Are you building blocks here?Lucky for us, it seems to still be afraid of the dark like the rest of its kind.
```

### [72] hash=`5e66cb78223096b2`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
It's finally over.My materials!Well, you are the most most.You drove away all the bad creatures and protected everyone.Swans on the stage, the pig burning furnaces in the factory,and even the uncles sleeping in the mine with Papa.I think they would all give you a big thumbs up.Huh?Just to be clear, I'm not a spy, kid.I'm just a traveler staying in town for the moment.But I have never seen you before.
```

### [73] hash=`86ab3da5fc63631b`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Do you also like the rest in the water?Like Villa?Do you also have a beautiful blue tail?I have no idea what you're talking about,But I'm certain that I'm not what you think I am, little fellow.Research her.We often stay in quiet corners when we work on a project, so you won't see us often.Understand?Researchers?Like those people on TV?I saw them stand on a tall, tall stage, with flowers in their arms.
```

### [74] hash=`1bf3044863b51518`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
spoke a lot and cried, and they were given a shining bella said the medals were to praise themfor being very clever.May I see your medal?Um, crystal on you looks stunning.It looks purer than those in the mine carts.Of course.Papa gave it to me.It is precious,but also very dangerous.A crystal like this is almost as volatile as undiluted runium ore.They use this stuff for war machines.Kid, listen to me.
```

### [75] hash=`460c220e2599ee5c`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Put that away.Go home now and don't let anyone see it.Understand?It could stimulate the critter's appetite.You build a very, very tall wall?When I can protect the whole town?Like what you did with the blocks?I'm sorry, little fellow.That was just a trick.It won't last long.Everyone should learn from you.Make the dirt and stones listen to me like you did one day.Will I be great?Like you?A strange kid like you should live in the age of Aquarius
```

### [76] hash=`6a9848776aec49ce`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
and be a part of the New Age movementsor become some kind of yogi doing meditationand do it anywhere but hereThey know what is that?Where are you from?It's not a placeIt's a spirit of a timefull of interesting things like crystalsnew schools of thoughtmany crazy and creative ideasWe have the sun close its eyes?We have the dark clouds spit on people?Will our ships blow bubbles under the water?Of course.
```

### [77] hash=`ded16cc5fad77cd4`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
They even believe that the world is a giant piece of blank paper.And they are the artists drawing on it.And not only that, they are obsessed with bizarre ideas.Where did the Stonehenge on the Salisbury Plain come from?Where are the ships and planes which traveled past the Sargasso Sea now?I like them.They called themselves Ley Hunters, the apprentices of a once renowned school of thought.However, few people in academic circles accepted the idea of Ley Lines as an answer to their
```

### [78] hash=`1f802f292aa14526`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
questions.For these Ley Hunters, it has been a long walk through a dark night.And they can come through the- Here the sun never sets.Half-dead anyways.And I can be their friend.And when I grow up, I will be a Ley- I'm afraid it's a bit too late, littlefellow.Most have already given up.They lost interest in solving the mysteries and losttheir faith in finding the curves and the lines.So, the study of ley lines has been
```

### [79] hash=`d08a679d15de9ad8`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
all but abandoned.There's only one fool left that hasn't given it up.And you, I suppose, are this only one fool, yes?Ah, please, ma'am.Believe me, I am not a child abductor.Well, I think this isn't a good place to receive our guest.We have much more appropriate arrangements for new friends.But, if our guest has any ill intentions, we will retaliate.Um...Thank you for taking care of little comrade Avgust Smith.
```

### [80] hash=`d802d0a6e2097fbc`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
You mean I'm not here to be questioned or arrested?Of course not.Perhaps we're a little too optimistic, but when we meet a stranger, we prefer to welcomethem.Well, I'm Wenzong.That's a very unique name.And where is it you come from?From the east side of the Dniester River.No offense, miss, but you have a complicated and unfamiliar scent about you.The smell of hard rocks, a lighthouse by the sea, rainwater in a humid summer, nothing
```

### [81] hash=`d7ce5abc07e9e3a7`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
how seldom.I think most ruthless travelers like me smell like that.Welcome to Ryashki, Miss Winsome.Thank you.I understand your caution, but…You have nothing to worry about.It's not a disease.Anyway, let's talk about you.I heard that you are a researcher.Not long ago, many of your peers visited here.They wandered around and looked under every rock and floorboard in the town, like youI thought perhaps they were attracted here by the town itself, but regrettably not long
```

### [82] hash=`7f7849c351cfaa19`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
after they left one after another in disappointment.I was disappointed too.Will you be like them?Those people are famous scholars.Of course they won't spend too much time on a projectwith unclear prospects.But I...I'm used to those.I salute you for your courage and spirit of exploration.I thought you...I thought you might be more hostile to me.Shouting things like, who do you think you are to prowl about on our private property?
```

### [83] hash=`7943dd06f4498e2d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Many see the study of ley lines like finding a needle in the grass of a Siberian field.Wasted effort with negligible results.There is no such thing as meaningless work.It doesn't matter who you are, where you're from or what you do.You will find your purpose here.Is that so?No wonder how you have such anUnusual student like August.All that childhood wonderinnocenceSomehow you've preserved it in him.
```

### [84] hash=`54ec364f0852c690`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Haven't you?He canceled our rehearsal, August.Mr.Evgeny just left red-facedYes, and he canceled the friendship cheese on the food menu.All thanks for youBut I was welcoming our new friendand we have lost our cheese because of you this is all your fault you're the most bothersome kidin the riyashki i know that word most means the best so thank you peter we don't see anyone newhere you're not lying again are you he's with villa they greet each other share footprints
```

### [85] hash=`70ed7be535daa164`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
and even sing together.Wind song is also the best.She can draw many lines on the snowand even on a seagull.We're not having another freaking town, right?Drawing on the blackboardlike Miss Vila did?She made the earth turn into a tall, tall walland she blew her breath at itand made a building appear.If we had enough ley hunters like her working together, we would be able to send sunflowers high into the sky.
```

### [86] hash=`b9ec6c59131d39fa`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Ah, that's not so tough.All the men in town know how to build stuff like that.When we grow up, we will work like them, with hosing shovels.But that will take ages.If we can learn how to build like the ley hunters, then we can help the adults right now.I want to listen to Ofgus!Greetings, Miss Windsong.Is it true?Can you really shape the earth into different things and build things from it?Not exactly.
```

### [87] hash=`cff0e1e759da9ded`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
The things I build with my arcane skill have only a momentary effect.I can't use it that way.I learned it as part of my research, while setting ley lines.Those things Ofgus told us.Are they true?The sun that closes its eyes, the dark clouds that spit on people, and the lines that can reveal everything.Ms.Windsong, will you be our teacher?Like Ms.Vila?Can you prove anything?Kids, one question at a time.
```

### [88] hash=`7eba85461a2d72d9`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Sorry, Ms.Vila.I should explain it to them.Mine is not a formal discipline, many people believe that it relies too much on the observations of arcaneists, and the conclusions aren't useful for the public.So it is best that you kids do not study it.A pursuit of passion fit for only a very stubborn fool like me.I see.Then you must show us all about it.Shouldn't she, kids?I'm sure Ms.Winsong would be very happy to give us a special lesson about her studies.
```

### [89] hash=`91abf9b23d45918d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Uh-huh.Ms.Vila, I thought I made myself clear.You have worked hard in this pursuit of passion, haven't you?Regardless, the study of ley lines is, well, it's useless.These kids should learn something like geography.It's a much more thorough and important field.As far as the general public and academic institutions are concerned, the study of ley lines is just a niche aspect of geography.Worse still, one that is solely accessible to arcanists.
```

### [90] hash=`2d53d45e0148e53d`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
To devote any real time to its investigation would take up valuable research funds and equally valuable researchers.At least that was how they felt about it.Who can say for certain?What about you?Do you also think that the study of ley lines is a waste of funds and manpower?I...of course I don't.Through ley lines we can detect arcanum-related events in the area,learn about local arcane creatures,and find the secrets hidden both above and below the Earth's surface.
```

### [91] hash=`4b30285b47aeb402`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
But I can't yet prove this to people.Well, you don't have to prove it alone.It doesn't matter what others think of your work, the only important thing is finding its uses.At first, Rayashki was just a remote village far north in the Arctic Circle.People came here to share a dream of a better future.It was only by luck that we found the room here.Then Zeno approached us and became our business partner.
```

### [92] hash=`0ac09129f309986a`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
For over 60 years, people here have worked together to make it what it is now.We built the school, the swimming pool, and the cinema for everyone.Rayashki embraces and takes in every newcomer.You and your studies are no exception.This is where our paths meet.Please know that I am not just doing this for you.I am doing this for a better future.A grounded education is vital in bringing up the next generation of scientists and workers.
```

### [93] hash=`d9a12c576b023879`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
Our children should learn more about this world, even from those perspectives and typesof knowledge that aren't widely accepted.Thank you, Miss Vila.The study of Ley Line sees the world as a clear map.The cities look like squares to us, while natural landscapes appear to be curves overlappingone another.Many bizarre places in the world, such as the location of the Tunguska explosionor the mysterious 30th parallel north
```

### [94] hash=`4851ab1efe9f0a1e`

- lang：`en`｜version：`1.8`｜arc：`—`
- doc：`BV1eo4y1u7aW_p54`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.8-活动】再见，来亚什基 | 1~4）

```text
can't be drawn in squares and curveslike cities in ordinary landscapes.We need to find a way to indicate themin a clear, precise way.It's a maze.Well, it is the ley line map of a city,but you are right.It does look like a maze.To begin with, I should introduce the most crucial conceptin the study of ley lines.That of ley energy.It is a special energy which we can easily detect throughout the town.
```

