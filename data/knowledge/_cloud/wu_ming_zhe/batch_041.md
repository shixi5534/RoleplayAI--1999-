# 剧情图谱抽取 · batch 041

- 角色：`wu_ming_zhe`
- 批次：**41** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.8」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_041.jsonl`

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

### [0] hash=`cb59dea8706c8ebe`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p17`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（17【雪与雪之外的】）

```text
I am sure it will be of more help in the future.You're not only doing this for yourself or for me,but for those who sacrificed for all of us.Must be the new resource!Call!It is call!We did it!This is our call!Comrade, we will use it to cook our meal tonight!And it will be the best meal I've ever had!Is that so, comrade Nikita?You got a problem with my food, huh?I made a rough estimate.The research here should last hundreds of years.
```

### [1] hash=`7f7c4134dd425afe`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p17`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（17【雪与雪之外的】）

```text
For the first time in history, the theory of ley lines has been verified.There is no doubt your work deserves a fair assessment now.Thank you for your help, Ms.Vila.We achieved this together, didn't we?Of course, the glory goes to every one of us.I'm very glad to see you again, Ms.Vinson.Are you?You don't look glad at all.I admit, I underestimated the people here.Especially you, Ms.Vinson.The great heroine who found coal deep beneath the town, huh?
```

### [2] hash=`1394501ab4afb295`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p17`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（17【雪与雪之外的】）

```text
So, did I manage to ruin Zeno's little plans?We have nothing left to do here.Zeno will leave soon.I know we disagree on many things, our future included.Still, Zeno looks forward to working with you again, hopefully in a more friendly way.I hope so too.You don't want to be embarrassed by another lowly researcher again, do you?Goodbye, Miss Vinsong.Wait.I have one last question.Please.I'm at your service.
```

### [3] hash=`223f5dc634bc03cf`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p17`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（17【雪与雪之外的】）

```text
Zeno confirmed the existence of Hoitooks in Rayashki months ago, but you just took care of them without letting anyone know.You already knew there would be a large reserve of coal here, didn't you?
```

### [4] hash=`633c0dfb8733be89`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p18`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（18【你好，来亚什基】）

```text
After thorough discussion, the people of Rayashki have made their final decision.I stand here to declare the future direction of Rayashki.As of today, Rayashki will be no longer affiliated with any organizationsand all factories dedicated to processing of rhenium ore will be shut down.What are we going to do for the work, Sam?I don't want to sit around at home living on benefits.There will be many things to do, comrade Valeriya.
```

### [5] hash=`1e95cf73ef327f3d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p18`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（18【你好，来亚什基】）

```text
As the elites above us struggle for power, we, ordinary people, suffer in darkness.But now there will be a new source of power, one built to lift up the people, not to take from them.And it will run on Rayashki coal.We will start new factories in Rayashki and explore the possibilities of working with other coal producers nearby.We will mine with our own hands and feed ourselves.Maybe we can even build a dock and sell our products far away.
```

### [6] hash=`7dc9ad530c365dda`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p18`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（18【你好，来亚什基】）

```text
We will raise a new banner above Ryashka.One welcoming all ordinary peopleto come to a livable place with abundant powerand job opportunities for their future.What about your plan, comrade Winsong?I think I'm going to stay for a while.You need to know that for now we must tighten our belts.Everyone's rations must be cut for some time until rayashki gets back on its feet.At least for now, the study of ley lines belongs here, not in the fancy halls and symposiums
```

### [7] hash=`e42c4625487c890c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p18`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（18【你好，来亚什基】）

```text
of human academia.This place still holds many possible research avenues, monitoring the changes in the environment,further detailing the local lei energy map,maybe even studying the mutation of the Kikituks.I must finish them to further develop the study,before it is ready for academia again.Then it sounds like you may be with us for a long time yet.Good.And don't forget, you were expected to cut the ribbon at the ceremony.
```

### [8] hash=`c84a0e0129ed1fae`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p18`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（18【你好，来亚什基】）

```text
I want to apologize for being rude to you during class.I'll bring you some friendship cheese next time.to apologize i promise you will always be our camera hats off to you i think we performedvery well at the ceremony will you come teach us again do you want to learn more too same hereThe sunflowers we planted are blooming, we protected the town.We begin the next chapter of Ryashki today.I'm so glad we will build it together.

Privet Ryashki.
```

### [9] hash=`f5701b7270688a0d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
Thank goodness!I was hoping you'd be here.Oh, um, is this a bad time?No, it's alright.Have a seat.I'm not a pure Rusalka.As you can see, I must get in touch with water every once in a while to replenish my power from the ocean.Hello, comrade Vila.It's been a while, comrade Winsome.They say you're working hard on the mine, and the study of ley lines is getting popular among the workers.They have helped a lot.
```

### [10] hash=`249b015b8d71568f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
My research on the environment wouldn't have gone nearly so smoothly without them.It's given a second life to my studies, and it is growing so well.It has even gained some recognition beyond Rayashki.I am truly happy that I came here.I never thought the comrade Winsong would be so bashful over her accomplishments.I thought you were more stubborn and confident than that.I'm only teasing, comrade.It's a matter of fact that you're not as fearless as you pretend to be, isn't it?
```

### [11] hash=`35a9870cfd88475a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
That's why we must all stick together to make up for each other's weaknesses and makeRyashki proud.Sorry, speeches have become an occupational habit.Fine, you got me.But it's not a big deal.Just as you are not quite the gentle and demure schoolteacher that you appear tobe.Are you comrade?We're even.Actually,I've come to say goodbye.Laplace has invited me to givea lecture for their European branch.
```

### [12] hash=`2002294d3c26466e`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
They want me to give a lectureon how I combined environmental analysiswith the Arkanum based onwhat we've done here in the Ryashki.Sounds like a very promising new beginningfor your studies.How are things going in the town?We are getting more visitors now.It seems people are eager to see something different.I'm sure they will.We've also begun cooperating with many governments and agencies near us, including the Foundation.
```

### [13] hash=`c47d6fa6256fd093`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
They hope to carry out some short-term training on the Arcanum for the children.What's this?Open it.It's from the Foundation.Mr.Nameday invites me to visit the Foundation and discuss further cooperation.The children are also waiting for me there.It seems they mentioned you all the time during their training.Did we miss the ley line exam?The foundation has all sorts of incredible things.Like biting coins, noisy corbels, a glass pen with rainbows inside.
```

### [14] hash=`e58234b9ab13010f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
So much fun!I've mastered a lot of incantations.I missed the town and everyone.Yeah, we missed comrade Alyonka, comrade Blinchik, and comrade Pirozhki.They say we will be able to go home in a few months.I must master the most powerful arching skills by then, so I can use them to protect the town.We'll transform into sea swallows!Then we'll be able to fly and fly to far, far away!Because Linska University Hospital received their rare case today,
```

### [15] hash=`c6480a090739f2fc`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
The patient's veins irreversibly transformed into electric wires.As of 1800, all arterial, venous, and capillary tissues throughout the patient's body have undergone necrosis.The directors said they would invite more professionals to the consultation to decide on further research direction.Global Variety News has claimed the case may become one of the greatest unsolved mysteries of the era.They started a new column to analyze possible compatibilities
```

### [16] hash=`24950f47c9cee0d8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
between the patient's new wired veins and different appliances.Please stay tuned for more details.The Flying Carpet Travel Agency is starting a tour around Northern Europewhere you will be able to see the breathtaking aurora borealis,pet fluffy keykerns, and even enjoy a flying carpet race.The destination of our tour is Ryashki,A mysterious town, the warmest place in the Arctic Circle, sitting atop many rich veins of coal.
```

### [17] hash=`4aa661c850b94253`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
When you get there, we suggest that you abide by the town's wishes and work to earn what you need instead of buying it.Though this is not an obligation, of course.But why not have a try when you're given the opportunity to experience a new and better lifestyle?Trust me, you won't be disappointed.Where should I start, dear readers?Ryashki is like a sparkling gem embedded into the permafrost, and above lies an eye-catching
```

### [18] hash=`278c5dbabc979f3c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p19`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（19【致后代】）

```text
banner.Perhaps it will draw even more attention in the future.Through the past decades, the citizens there have been trying to achieve something differentfor themselves, a great cause which may take the work of generations to achieve.But now, they are no longer a nameless town in the far north, nor is their dream a passingfad bound to be forgotten.I sincerely hope all of us will be able to witness its history and its future.

That's why I knew I must write down this story, in the hopes that their dream willremain in your heart forever.
```

### [19] hash=`7f11759827a43650`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
That navy blue color.It's a mutant.So that's why they've sent me here.Something is wrong with this town.Rayashki is a town on an island near the North Pole.Peaceful and free from strife.Decades has prospered from mining ore.But the ore has now run dry.Without the ore, Zeno will no longer support us.From Zeeland to the Balkan Peninsula, my journey went on and on.But above all other places, I kept finding my thoughts returning to that little town,
```

### [20] hash=`3a5ddd9b5a4e50f6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
to its incandescent lights glowing in the long dark of the Polar Night, to the shareddream of the people there.I got this picture book from Ryashki.It is a children's book, a thin one at that, but story inside has the power to warm a frigidheart.Once opened, wells of bright primary colors run into one another and flow up onto mypalm.I found myself returning to it during stormy days when I was stuck at home.
```

### [21] hash=`2073e1230d8f8fc8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
This is a story about honest and ordinary people.The swans are dancing in a circle.Their arms go back and forth.Vila and the swans have done this dance almost 20 times last week.She taught the swans all their beautiful moves.Swan lift is the best ballet ever.I remember Mr.Afghani once said so.He also said the tortoises would come to watch the show.Why would tortoises want to watch one lake?Says she doesn't like the tortoises.
```

### [22] hash=`7df5ccbaf5f098b7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
She likes knowledge.I don't know much about knowledge.But I think Ms.Vila is always right.Only between you and me?Vila smells like seaweed and coral.Those are happy smells to me.I think she must be the princess of the ocean, but she tells us she is not special, and thateveryone here is equal, who matter if they are a princess or a swan, that we all havetwo feet and ten fingers, and if we all work together, we can build the peak into
```

### [23] hash=`235b693f9f2d7480`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
the future.I hope in the future we still get to sing and dance.When we are not building beacons.Inna's favorite food is called Alonka.It's a chocolate bar.She used to cry a lot whenever she made a mistake with her dancing.But then Vila talked to her.And now she doesn't cry so much.One time she danced very, very perfectly.So Vila gave her a piece of an Alonka bar.I believe she will be a great dancer.
```

### [24] hash=`32d063b406b8c89b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
If she doesn't get too nervous on stage, then she could have even more chocolate.I wish I was like her.I want chocolate too, but I'm not a swan like her.And now, there's never any Elionka on the canteen's cupboard.Now, Nina is the swan princess, the most prettiest of all swans.Bassano is the swan prince.He is a nice one and he has many many swan friends.And Piotr is the evil sorcerer, a black swan.
```

### [25] hash=`4157f06f15567803`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
Nobody wanted to be the bad guy, but Piotr doesn't mind.He is very serious and always bossy to everyone, so he doesn't have many swan friends.Peter just wants to do his job as perfectly as he can, cause he loves our town.Now of course he's not a swan, but he also loves his town.Then there is a little mouse, who moves as quickly as the blowing wind.Will it be our new visitor?What was it that Vila said about new visitors?
```

### [26] hash=`2b27a5b4766474f5`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
I don't remember now.Reporting to you, comrade Vila.I have a very important question.Well then go ahead, little comrade Avgust.Do we receive the new visitors coming to town?Maybe we can welcome them with Salienka?Or friendship?Or maybe something else?We will welcome them with white snow, with smiles on our faces, and with welcoming arms we use to achieve our dreams, as we do for everyone who comes here, little comrade.
```

### [27] hash=`fd57f6eb90bb5e0e`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
It's always good to ask questions, but don't forget your task today, alright?My drawings are important, but Vila says entertaining our new friends is also important.If one comes first, though the swans have flown away, Evgeny will go up to the stage.Evgeny is not an evil sorcerer, but he knows a secret magic that makes everyone's tongues hide in their mouths.He is not so much a bad person, I think.
```

### [28] hash=`ca947119c88e25d9`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
Evgeny's shadow is very long, but no one, not even my sunflower, can explain why.Evgeny walks heavily onto the stage.His appearance comes without any applause.We have received a telegraph.Zeno's investigators will arrive here in Ryashki tomorrow afternoon.And we will be hosting a welcome ceremony.I understand your concerns.I know you don't want Zeno to interfere with your lives.Nor do you want their troops stationed here.
```

### [29] hash=`280f84a660367a2d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
And I would remind you that they have honored their side of the deal for decades now.We give them Runium ore and they supply us in return.It should be as simple as that.Always it has been this way.Since my grandfather's time.Times have changed, Comrade Knut.In the old days, Zeno used to pay us generously for mining the Cerunium,because our ore was necessary for the Arcane Combat Vehicles.But now, we have nearly exhausted all our mines.
```

### [30] hash=`fd312004bae31c34`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
You know this better than I do.But isn't there some other work we can do?Already we build our own houses, and now we even grow our own crops.he's right why must we work with Zeno if we could feed ourselves comrades calmyourselves Evgeny is doing this for everybody's sake have you forgottenabout those little monsters is there anyone left on our defense team thathasn't been injured fighting them it is as comrade Nikita said the
```

### [31] hash=`4c076854f8c3b9fb`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
critters are running rampant these days not only have they occupied mostour minds.Some have even found their way into the town.Do you really think we can protect ourpeople with our small defense team?Don't you care about your neighbor's safety?Do you wantto keep Ryashki an isolated town just to let it die?Ryashki is more than an isolated town,Evgeny.And we all know that.But this is the reality we almost face now.
```

### [32] hash=`d9ae95665a6120b2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
It was your idea toto these you know big guys for help but you never even asked what we think did you so you can'tblame us for disagreeing now i'm doing this for your good we can take care of ourselves everyonewatch out defense team on it i salute your sense of smell comrade vila we could have sufferedmuch more severe consequences without your forewarning think nothing of it it's just areflex reaction when there's danger nearby.
```

### [33] hash=`5970f189a7bbad6d`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
But this incursion has proved my point.We need Xeno's help.The other townspeople are not gifted with your set of talents.We are all vulnerable to the growing dangers.Wouldn't you agree?I only ask you to put yourself in their shoes.Your criticism is valid and well accepted, Comrade Evgeny.Perhaps I could agree with your plan.provided Zeno's presence is a temporary one, we just don't want them to change things for us here.
```

### [34] hash=`3c9e57f5058930a4`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
I'm glad that you have finally come to realize what is best for us.Zeno is known for their rigorous methods and rational decision-making,and they are committed to maintaining peace around the world.I'm sure they will make the right decision.They trusted us to supply their ore, and we have faithfully played our part in supporting them.Thanks to our help, Zeno has successfully tackled many international issues.
```

### [35] hash=`ba21e509e8df8417`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
It has always been them and us together, fighting for a better world.When you put it that way, he is right.We should be proud of our cooperation.Therefore, we will show our appreciation to Zeno for the contributions they've made to the world with our help.Now let's continue our rehearsals.Have you seen Avgust?I can't find him.Where did he go?Hmm, looking for any Alenka left in the cupboards I bet.
```

### [36] hash=`0d197fb69eecba8f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p1`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（01）

```text
He's always breaking the rules, doing whatever he wants.We shouldn't talk badly about our classmate, Dota.He's one of us.Yes, you're right.I just wanted everyone to do their best.Even him.Don't worry kids, we will find him.A child is missing, comrade Evgeny.I suggest a temporary suspension of our rehearsals.It must be that strange kid again.He is always sneaking away like this.He's only trying to understand the world in his own way.
```

### [37] hash=`423ab3e293db6726`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
Vila once said that sunflowers mean warmth, and that makes them everyone's friends.They would warmly welcome every guest that comes to town.Just like my best friend here, right?Ah, friends.Everyone should have a best friend.Now here are big friends, so that our new guests won't feel so lonely when they come.Amazing.I've never seen such a highly mutated Ejidak before.I would have missed these precious research opportunities if there weren't a gathering in the town.
```

### [38] hash=`793fe29b83821231`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
Winsong, seems like life has been good to you and your theory.The disorder and lay energy here has not only caused the exhaustion of the Runian mines,but has also mutated local critters to varying degrees.Hmm, then Zeno was right.No wonder they have sent so many researchers here to look for abnormalities.Even the crank ones like me.It's obvious that this town has more to it than a handful of overly active critters.
```

### [39] hash=`f7a1393227d49730`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
But they don't seem especially interested in the mutant ones either.Zeno, what were you looking for here?My leg!Strange.You're not a fox, and you're not a sable.Hey, kid, what are you doing?Oh, shoot.Ajarax are usually known for their good temper.It seems to not apply to their mutant kin.Are you building blocks here?Lucky for us, it seems to still be afraid of the dark like the rest of its kind.It's finally over.
```

### [40] hash=`744e86758a6eb481`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
My materials!Well, you are the most most.We drove away all the bad creatures and protected everyone.Swans on the stage, the pig burning furnaces in the factory, and even the uncles sleeping in the mine with Papa.I think they will all give you a big thumbs up.Huh?Tell me, Winsong?Just to be clear, I'm not a spy, kid.I'm just a traveler staying in town for the moment.But I have never seen you before.
```

### [41] hash=`fb6f864f0f74ac80`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
Do you also like the rest in the water?Like Vila?Do you also have a beautiful blue tail?I have no idea what you're talking about, but I'm certain that I'm not what you think I am, little fellow.Researcher!We often stay in quiet corners when we work on a project, so you won't see us often.Understand?For researchers, like those people on TV, I saw them stand on a tall, tall stage with flowers in their arms,
```

### [42] hash=`8bcaa269cb05e2bd`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
spoke a lot, and cried.And they were given a shiny medal.Viola said the medals were to praise them very cleverly.I see your medal.Um, Stellon, you look stunning.It looks purer than those in the minecarts.Papa gave it to me.It is precious, but also very dangerous.A crystal like this is almost as volatile as undiluted runium ore.They use this stuff for war machines.Kid, listen to me.Put that away.Go home now and don't let anyone see it.
```

### [43] hash=`bf1a9b3bee876785`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
Understand?It could stimulate the critter's appetite.A very, very tall wall?When I can protect the whole town?Like what you did with the blocks?I'm sorry, little fellow.That was just a trick.It won't last long.Everyone should learn from you.Could I make the doors and stones listen to me like you did one day?Will I be great?Like you?A strange kid like you should live in the age of Aquarius and be a part of the New Age
```

### [44] hash=`e72a28e26d7c4f10`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
Movements or become some kind of yogi doing meditation.And do it anywhere but here.The New Move.What is that?Where are you from?It's not a place.It's a spirit of a time, full of interesting things like crystals, new schools of thought,many crazy and creative ideas.Will the sun close its eyes?Will the dark clouds spit on people?Will our ships blow bubbles under the water?Of course!They even believe that the world is a giant piece of blank paper,
```

### [45] hash=`92224ac03ba3ec2c`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
and they are the artists drawing on it.And not only that, they are obsessed with bizarre ideas.Where did the Stonehenge on the Salisbury Plain come from?Where are the ships and planes which traveled past the Sargasso Sea now?I like them.They called themselves Ley Hunters, the apprentices of a once renowned school of thought.However, few people in academic circles accepted the idea of Ley Lines as an answer to their questions.
```

### [46] hash=`f665ddae7270b827`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
So, for these Ley Hunters, it has been a long walk through a dark night.Then they can come today.Here the sun never set.Half the year anyways.Then I can be their friend!And when I grow up?I'm afraid it's a bit too late, little fellow.Most have already given up.They lost interest in solving the mysteries and lost their faith in finding the curves and the lines.So the study of ley lines has been all but abandoned.
```

### [47] hash=`9006f5f4c3eef34b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p2`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（02【大发现！】）

```text
There's only one fool left that hasn't given it up.And you, I suppose, are this only one fool, yes?Please, ma'am.Believe me, I am not a child abductor.Well, this isn't a good place to receive our guests.We have much more appropriate arrangements for new friends.But if our guest has any ill intentions, we will retaliate.Um...
```

### [48] hash=`edc6a86d900a8d6b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
Thank you for taking care of little comrade Avgust, miss.You mean I'm not here to be questioned?Or arrested?Of course not.Perhaps we're a little too optimistic, but when we meet a stranger,we prefer to welcome them.I'm Winsong.That's a very unique name.And what is it you come from?From the east side of the Dniester River.No offense, miss, but you have a complicated and unfamiliar scent about youThe smell of hard rocks, a lighthouse by the sea, rainwater in a humid summer, nothing
```

### [49] hash=`0e6768dc0f9302b2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
hostile though.I think most ruthless travelers like me smell like that.Welcome to Ryashki, Miss Wensong.Thank you.I understand your caution, but...You have nothing to worry about.It's not a disease.Anyway, let's talk about you.I heard that you are a researcher.Not long ago, many of your peers visited here.They wandered around and looked under every rock and floorboard in the town, like you do.I thought perhaps they were attracted here by the town itself.
```

### [50] hash=`60133143327dc970`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
But regrettably, not long after, they left one after another in disappointment.I was disappointed too.Will you be like them?Those people are famous scholars.Of course they won't spend too much time on a project with unclear prospects.But I...I'm used to those.I salute you for your courage and spirit of exploration.I thought you...I thought you might be more hostile to me.Shouting things like,Who do you think you are to prowl about on our private property?
```

### [51] hash=`3670ecd5d690efb9`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
Many see the study of ley lines likefinding a needle in the grass of a Siberian field.Wasted effort with negligible results.There is no such thing as meaningless work.It doesn't matter who you are, where you from or what you do.You will find your purpose here.Is that so?No wonder how you have such anUnusual student like August.All that childhood wonderInnocence somehow you've preserved it in him, haven't you?
```

### [52] hash=`79f0df2b65756e58`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
The show finished?He cancelled our rehearsal AugustMr.Evgeny just left red-facedYes, and he cancelled the friendship cheese on the food menu.All thanks for you.But I was welcoming our new friend.And we have lost our cheese because of you.This is all your fault.You're the most bothersome kid in the Ryashki.I know that word.Most means the best.So thank you, Peter.Avgus, we don't see anyone new here.
```

### [53] hash=`4486c2a90acf6219`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
You're not lying again, are you?She's with Vila.They greet each other, share footprints, and even sing together.Windsong is also the best.She can draw many lines on the snow, and even on a seagull.We're not having another freaking town, right?Drawing on the blackboard, like Miss Vila did?She made the earth turn into a tall, tall wall and she blew her breath at it and made a building appear.If we had enough ley hunters like her working together, we would be able to send sunflowers high into the sky.
```

### [54] hash=`d418c80890c7f6f7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
Ah, that's not so tough.All the men in town know how to build stuff like that.When we grow up, we will work like them with hosing shovels.But that will take ages.If we can learn how to build like the Lake Hunters, then we can help the adults right now!Don't listen to Ofgus!Greetings, Miss Windsong.Is it true?Can you really shape the earth into different things and build things from it?Not exactly.
```

### [55] hash=`6ec1f91bd31ac235`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
The things I build with my arcane skill have only a momentary effect.I can't use it that way.I learned it as part of my research, while studying ley lines.Ms.Windsong, Havkos told us.Are they true?The sun that closes its eyes, the dark clouds that spit on people, and the lines that can reveal everything.Ms.Windsong, will you be our teacher?Like Ms.Vila?Can you prove anything?Kids, one question at a time.
```

### [56] hash=`c633e2d9d12d62cc`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
Sorry, Ms.Vila.I should explain it to them.Mine is not a formal discipline.Many peoplebelieve that it relies too much on the observations of arcanists, and the conclusions aren'tuseful for the public.So it is best that you kids do not study it.A pursuit of passionfit for only a very stubborn fool like me.I see.Then you must show us all about it.Should the she gets.I'm sure Miss Wonsong would be very happy to give us a special lesson about her studies.
```

### [57] hash=`f5a29d322f6a0da4`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
Uh-huh.Miss Vela, I thought I made myself clear.You have worked hard in this pursuit of passion, haven't you?Regardless, the study of ley lines is, well, it's useless.Useless?These kids should learn something like geography.It's a much more thorough and important field.As far as the general public and academic institutions are concerned,the study of ley lines is just a niche aspect of geography.Worse still, one that is solely accessible to arcanists.
```

### [58] hash=`c64f96ff542056b5`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
To devote any real time to its investigation would take up valuable research funds andequally valuable researchers.At least that was how they felt about it.Who can say for certain?What about you?Do you also think that the study of ley lines is a waste of funds and manpower?I...of course I don't.Through ley lines we can detect arcanum-related events in the area, learn about localand find the secrets hidden both above and below the Earth's surface.
```

### [59] hash=`415dac48adab96f6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
But I can't yet prove this to people.You don't have to prove it alone.It doesn't matter what others think of your work.The only important thing is finding its uses.At first, Rayashki was just a remote village far north in the Arctic Circle.People came here to share a dream of a better future.It was only by luck that we found the runway.Then Zeno approached us and became our business partner.For over 60 years, people here have worked together to make it what it is now.
```

### [60] hash=`bc126da5ccef8963`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p3`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（03【羽茅地】）

```text
We built the school, the swimming pool, and the cinema for everyone.Rayashki embraces and takes in every newcomer.You and your studies are no exception.This is where our paths meet.I'm not just doing this for you.I'm doing this for a better future.A well-rounded education is vital in bringing up the next generation of scientists and workers.Our children should learn more about this world,even from those perspectives and types of knowledge that aren't widely accepted.

Thank you, Miss Vila.
```

### [61] hash=`d00e4345d5436a14`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
The study of ley lines sees the world as a clear map.The cities look like squares to us,while natural landscapes appear to be curves overlapping one another.Many bizarre places in the world, such as the location of the Tunguska explosionor the mysterious 30th parallel north,can't be drawn in squares and curves like cities in ordinary landscapes.We need to find a way to indicate themin a clear, precise way.
```

### [62] hash=`14c27bd7430700e2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
It's a maze.Well, it is the ley line map of a city,but you are right, it does look like a maze.To begin with, I should introduce the most crucial conceptin the study of ley lines.That of ley energy.It is a special energy which we can easily detectthroughout the town.See how it comes out from underneath the groundgoes into the local biosphere, circulating around like a system.If wethink of the town's ley lines as a food web, then ley energy lies at its foundation.
```

### [63] hash=`ae80eff13c8561a6`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
Like how big fish eat small fish, and small fish eat even smaller fish.Exactly!They are the smallest fish eaten by the big fish.If we catch thebig fish and study what they eat, we will know where to find the other bigand the lay energy I mean when the big fish die and break down the small fishwill go back to where they first came from the circulation goes on and on you'veput it very well miss Winston like the rain water that comes from the ocean to
```

### [64] hash=`94e6c2c5f225059b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
the rivers and returns back to the ocean you're a quick learner but it isexactly like water.The concentration of light energy is far more noticeable thanthat of a lake or a school of fish.Once we find its densest spot, we'll be ableto trace it back to its source.And what are these bright spots?These are theenergy-rich locations.In a way, they indicate the energy flow.So men, theylook like stars in the sky.
```

### [65] hash=`beed2080d71ccc0b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
Yes, and finding these locations can be very costlyin terms of time and manpower.And what do we do if they're finding them?They can tell us many things.The lay hunters will follow their courses,analyze the components in them,and match those components to each resource.Some of the components don't matchwith any of the known resources,Which means, there might be a new resource waiting to be discovered.
```

### [66] hash=`3ac09beb2f7b6858`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
Of course from the late energy we can also learn about the local critters.You talk about strange things, almost like Avgust does.These are just lions.Dancing earthworms.There you go.They are having fun.Jumping on the waves.Then into the little boxes.And back into the little bowls.Great!We have two of them now.Interesting, but we don't really understand.Cheer up, kids!It's not finished yet.Leyline cartography is complicated.
```

### [67] hash=`92896bcf81d582d7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
It takes the efforts of many ley hunters working together,investigating the area, even braving dangerous and forbidden places.To this day, we've never been able to finish a completed lei energy map.This is the swimming pool.That little square is our square.These little balls are our homes.I live here, the third ball on the left of yours.You're very bright, Avguz.This is the lei energy map of Rayashki.
```

### [68] hash=`c9eac47f644782b7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
Rinsong, why are you mapping the energy of our town?Have you found any secrets that we don't know?Children, right now you can only see what's above the ground,but there is even more lay energy beneath the ground.Will the sun always be in the sky?Will the glaciers ever melt away?What lies in the darkness beneath us?Are there other critters around here that you've never seen?How should we deal with them?
```

### [69] hash=`977043dae6b9d26b`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
I heard once that there were many strange footprints next to the school windows.Uncle Patrick saw it, a monster with six legs, and each one has spikes.That must be a cichirn, a small-sized canaday critter, mostly seen in cold areas.But the lay energy might have affected the weather of their habitat, or they wouldn'tbe here in Rajaski in summer.The deep blue line here shows that particular one's movement.
```

### [70] hash=`90de45702e69ecae`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
Maybe Uncle Patrick could have drawn too much.The lay energy accumulated in them suggest that they mostly feed on moss and worms underthe snow and stay near town.We can infer that this is a docile herbivorous kind of critter that is merely curious abouthuman behavior.I think feeding them will be much more useful than driving them away.Since these critters begin to overrun the area, the defense team has encountered many
```

### [71] hash=`9e4a8d447c94145e`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
new creatures.I can feel there is something strange about them, but I can't yet understand the differences.You provided a different angle on the situation, Ms.Winsong.I believe it would help the defense team greatly.Tires in the furnace are out, the bees and kites dance around the pond, white mosses on the wall,all whole from the sky.They changed things, Avgust.The defense team will keep the critters out of town and protect everyone.
```

### [72] hash=`15cd6029a4a93709`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
And there will not be any stones falling from the sky.Is everything alright, Piotr?Yuck!You're lying!Ryashki is safe!It will be your home forever!I hate to tell you this, kid, but what Avgus just said could be right.I have the same feeling that the good weather here won't last too long.Look at those thick gray lines.Those are the traces of cloud movements and moisture.Now they're mingled together.
```

### [73] hash=`456fada6d02e08a5`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
But the sun will still be shining.Ms.Vila said that the polar day will last for a very, very long time.Ms.Vila was right, and past statistics don't lie.According to the data, the weather here should continue for the next few months.Yet the ley lines say otherwise.They say the weather will be extremely unpredictable.You are making things up.The forecaster on TV said the weather in the Ashki will be comforted in the coming months.
```

### [74] hash=`9dd73de033d2f4c8`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
And the weather forecaster was right, according to his analysis.But life is full of surprises.I know why you're concerned, Ms.Wensong.I feel the glaciers are melting slightly faster than usual.There is going to be a warm front forming from the melting water.Will there really be stones falling from the sky?I can't say anything for certain just yet, kid.All I have is this incomplete map.And as you can see, many sources of the marks and traces haven't been located,
```

### [75] hash=`989d1d16fff13880`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
which means we can't come up with a precise calculation.But there's no question that Ryashki will soon face many challenges.The weather could become much worse.The environment might change.Maybe some unknown critters might turn up.Ryashki's at home, so it can be dangerous.You can't fly if your feathers get wet.They will need some time to take in all this new knowledge.Don't you agree?I thought I could handle all their questions.
```

### [76] hash=`2c2bf39e7a36986a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
I think I made things worse.Sorry.Have faith in them.They will come around.Are you here to laugh at me?All these stories of monsters and falling stones,they aren't good at all.I overheard Mr.Afdini talking.He said the town has so many problems,And soon, what some people think will decide our future.If people believe in those terrible stories, maybe they will be scared and they won't come back to Ryashki.
```

### [77] hash=`ac70877dbd98e9b2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p4`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（04【园丁对花儿说】）

```text
Hong will be forgotten.I wasn't lying.Hello, Pikiru.What?What are you doing?I will draw its attention.You go find a defense team for help.Seiji, it feels warm, doesn't it?Miss Winsong said they can be our friends.That they will bring seeds to every corner of the town.Like a gardener?Yeah!Plant more sunflowers, Kikirin!So, Ms.Winsong was not a liar.
```

### [78] hash=`69766b0118e238ac`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
Do you really think it's a good idea to turn to Zemo for help?We have drawn almost every man and woman from the mining facilities to get rid of the critters nesting around the port.Most of the defense team were injured.Some lightly, but others got much worse.It will be weeks before they can return to duty.If an attack like the one at the rehearsal happens again, I'm not sure we will be able to protect ourselves.
```

### [79] hash=`b00e419bfcdbf6b5`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
I know most of our people are frustrated with Xeno's arrival, but I expected better from you, Vila.People trust you, and they will follow you, but that doesn't make you right.Maybe you're still too young to see the dangers.I might be wrong, but history is a long lesson in learning what is right through being unafraid to be wrong.Sadly, we don't have time for a trial and error.And this is your excuse for making decisions for us against our will?
```

### [80] hash=`521c25ee5c3b09de`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
I will hold myself responsible for my decisions.In that, you have my word.Today is the day of our welcome ceremony.Vila said when the bell rings, the important people from the Tortoise Academy will arrive.Everyone looks excited.Nina has put on her best dress.I know she'll be great on stage, but Sona will do all with Piotr.It's his duty to protect the princess.As for me, I got a new job from Mr.Afghani.
```

### [81] hash=`20600c551f30e039`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
Salute!Shake hands and give them the warmest welcome.What this?They're bubbles in the water.Again, Kikirin, are you planting sunflowers under the water?Have you brought your friends?Your friends also have six legs!Look, they're wearing needle grass and flat files on their legs.Are you also here for the ceremony?Come, Kikirin and friends, come to the prettiest town in all of the Yarte, the Yashki.Please, enjoy yourself.
```

### [82] hash=`a66f6955eed79ad7`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
Comrade Avgust, what are you doing?Whoa!I'm welcoming the Kikirn.Get out of there!They're dangerous!Defense team, drive them away!Wait!These are Kikirn!They're not aggressive, they're just curious about us!The kids seem to like them!Get rid of them!As you command, comrade!The Kikirns are all gone.I think they don't like us anymore.Comrade Yevgeniy.Take the kids back to where they were, comrade Vila.
```

### [83] hash=`7e01d4d4a8fdf89e`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
It was your duty to protect them.Maybe if we make the town a better place more friends will come back.Then they will also come back.Makes sense.The family of Kikirin includes dozens of subspecies.But none of them are so greatly adapted to water as this.That is to say, they might also be affected by the lay energy under Ryashki.Pity that they were driven away.There was much we could have learned from them.
```

### [84] hash=`5b19550ccef8a228`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
The temperature here is rising much faster than expected, and much earlier in theseason.I imagine if you asked the weather bureau, they would say this is just an odd occurrenceof unseasonable weather outside of expected ranges.It's time.The Xeno investigators should be here any minute.I must stress again how important this ceremony could be for our future.Our town's economy is facing a cliff, and I am sure each one of you has noticed the
```

### [85] hash=`7064a243997dea3a`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
increased rationing.If we wish to take care of our people in the future and protect our friends and familyfrom these frequent creature attacks, we need Xeno's support.So we will work with Xeno, because we must.The future of Ryashki is in our hands.So is the future of every comrade here.And we need the cooperation of every man and woman here.Zeno's ships are very fast.So as soon as they appear on the horizon, our ceremony will begin.
```

### [86] hash=`4edaca61a297c1ab`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
Understood.Zeno is late.So late that Ms.Volova said they were absent.Do you think something bad happened to them?What are they doing there?Oh, like a polar bear's head.Poor bear, losing all his hair.Can there be snow in summer?Is this related to the strange thing Avgust said earlier?If so, I'm happy that these aren't stones or a dark cloud spit.Can't believe it!You were never right before!Oh, it's chilly.
```

### [87] hash=`498598ea258216c2`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
The snow is biting against my skin.I'm sorry, Avgust.I shouldn't call you a liar.But will Ryashki really get into trouble?We are there.We will not be defeated.Not by clouds or bears.This is walking very slowly.But no one has left their position.Ryashki, those ones must go back to their...Go as fast as you can.We will.Don't forget your own job.So, this milky white line is this snowstorm.The average temperature in Rajaski has reached its highest point in the last five years,
```

### [88] hash=`eda8d1cee42d7051`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
which together with the abnormally rich air moisture have produced an unseasonal and odd kind of snow.The weather forecast was wrong.Lay lines were right.Everyone listen.Our ceremony will begin.As you command, comrade.Music, please!It's a pleasure to speak to you all, our valued friends in Ryashki.On behalf of Zeno Arms Academy, I am here to announce the details of the Zeno-Ryashki Cooperation Agreement.
```

### [89] hash=`90610dc3094ca126`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p5`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（05【手风琴】）

```text
As many of you have expected, a squad of armed troops will soon be sent to aid you with thecritter problem.However, having given it careful consideration, we have decided that the town of Ryashkiis no longer viable for our continued support and must be abandoned.We advise that all residents prepare to be transferred to a new post immediately.Thank you for your cooperation.What?
```

### [90] hash=`7b7a15bd998c4200`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
I don't see the point of your reluctance.The letter conveyed Zeno's decision clearly.I suggest we warm ourselves up with a few drinks before we go.Do you have any stowage in town?Better than sitting here dwelling on the things that cannot be changed.Please, tell me you have something like cocoa here?This is not what we agreed on earlier, Mr.Bertolt.Call yourself Villa.You must be mistaken, my very passionate friend.
```

### [91] hash=`49d0ccbf3f78ae31`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
Sino sent a warning months ago.The estimated value Ryashki can add to Sino'sprogram is less than satisfactory.Further support is no longer recommended.Should any new valuable resources be found in the region, please reply to thisletter as soon as possible for further assessment.Then we heard back from Ryashki.In fact, the sender was...you, Evgeny?Yes, it was.And it was you yourself that argued the most compelling point, I have to say.
```

### [92] hash=`a566625b18600413`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
One that has drawn the higher-ups' attention, and the reason why I was sent here.I believe you wrote,I have total faith in the quality of the people of Ryashki.Their solidarity, dedication, and motivation have proven invaluable to us.I am certain they would carry those same strengths of character and skill to any post no matterwhere they were assigned.Xeno accepted my application.Of course, I asked around before making my submission and Xeno seemed to have a good
```

### [93] hash=`96896d31bb1147ec`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
reputation.It was a golden opportunity to join them.It is, but do not get us wrong.Our entrance requirements can be most difficult to meet.Zeno only takes in the best of the best.You want some of us to work for Zeno?You never told us anything like that!Evgeny!Be reasonable, Vila.Some of us deserve this opportunity.All the others!The elders and children!Some of our comrades have been injured and even died in the mine!
```

### [94] hash=`52c53b5b11d6844f`

- lang：`en`｜version：`1.8`｜arc：`再见，来亚什基`
- doc：`BV1bM4m1Q7Zj_p6`
- title：《重返未来：1999》1.8版本「再见，来亚什基」全剧情 - Reverse: 1999｜4K（06【好日子，坏日子】）

```text
Are we to forget their sacrifices?Relax, my friend.That's why we sent our very best biological control squad.We will escort you to the nearest shelter.Face reality, Vila.I know how much effort we have put into building this town.And I understand you have this dream to fulfill.But we must prepare for the worst.We may have to give up on our rayashki.Read this.Field investigation has confirmed that the remaining runium reserves in Rayashke are around
```

