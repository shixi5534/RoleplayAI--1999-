# 剧情图谱抽取 · batch 077

- 角色：`wu_ming_zhe`
- 批次：**77** / 共 1 批（每批 95 块）｜本批块数：**45**
- 筛选：标题含「1.3」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_077.jsonl`

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

### [0] hash=`caf7a7bd11f0affc`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Bhanish.She will try to make contact with the Foundation as soon as possible.But we still need to evacuate every villager we can.We know almost nothing about Khwar's plan now.Not to mention her whereabouts or purpose.For now, we have two solutions to the problem.First, let's find my clever evil sister so that our astronomer friend can figure out a way to stop the meteor.Or, spread the word and tell everyone to take the earliest train and leave the impact area.
```

### [1] hash=`6d5ffa5980734158`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
It's hard to be optimistic given the situation, but at least there is something we can do to reduce the damage.but if we continue to sit around waiting the situation will only worsen comelet's think the f1 portable contact device activated welcome arcane skillverification activated please make sure you are not equipped with any wandsread out the random incantation displayed on the screen clearly make
```

### [2] hash=`0d4c60f5a7853e52`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
sure your tone remains stable verification success registered userMatilda Bwanish, access level D.No abnormal arcane skill fluctuation detected in the area so far.Level D, access only supports quick report.So according to the investigator, we can ask for a reinforcement via this system.So, what's the point of transporting it everywhere?I thought it would be useful for emergencies.Does that mean I'm going to miss the chance to study celestial energy
```

### [3] hash=`e26efe074f465f73`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
in addition to wasting my chance to capture the Manus?The reception here is terrible!I'm in contact with the-or it's going to hurt your throat and ruin your beautiful voice.Kanjira was ecstatic about those cookies.She even took three pieces with her when she left.I hope that kind human girl would get to the train station safely with those kids.Now, let's take a look at you.What are you doing?Is this the stone Kumar left to you?
```

### [4] hash=`76d3df3f2a2bb8d1`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Vishnu?Brahma creates, Shiva exterminates, and Vishnu safeguards the balance of the world, lyingon the ocean of stars, according to the materials.Well, maybe I should explain it with mythologies for non-researchers.They mentioned three idols, but Vishnu's is the only one left, so she must havetaken the other two.Perhaps it's proof that Komar abandoned the path of maintaining the balance in the first place.
```

### [5] hash=`18823d369c6ba71e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
That mural there, she said the mythology on it has been passed down in her family.That's true.I've recited that story at least 20 times.But the part on the mural, to be honest, it feels so out of place to me.It was more like foisted into those well-known myths.Like a pair of ox horns on a horse's head.Unusual metaphor, but actually, it plays a significant part in connecting all the mythologieswe know.
```

### [6] hash=`cf4ea5bff85fd07a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
These mythologies are the primary material of our research.We've been trying to prove human science with basic Arcanum theory.In fact, there is a connection between them, and they can support each other.If Arcanists and humans could get along, I suppose the world would have developedfaster than it does now.It's not easy to explain it through, but in short, there is another universe in theshape of an egg affecting reality.
```

### [7] hash=`9dc95ce5d778eefe`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
We call it the meditator's realm.Just like our daily dreams, you can enter it once you fall asleep.But that's not how we do it.We connect part of our gnosis with the realm through a special kind of meditation.It's not as easy as it sounds.One needs to either master the meditation skills like we do, or use a special medium as an anchor.Our mythologies are the original translation of the realm.An existence that cannot be observed through the methods in this world can be located as long as it is included in mythology.
```

### [8] hash=`77cde1dd90a72af5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
That's how we located that star.Sadly, if we can't prove its existence with data recorded by human technology, our discovery is useless.I am surprised.For all this time, she has never given up on studying the old Arkinumtale of our family.You can even say she's fanatic about it.It's just, indeed we can do a lot of supernaturalthings in the realm.If your mind is calm or your anger strong enough, you can even
```

### [9] hash=`b89acf31307f6564`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
do whatever you want.But it's limited inside there.Remember I said it's likeour daily dreams?Just think of it as a controllable one.Everything in the realm is created basedon reality.In other words, it's nothing but a mirror.And the images in a mirror can neveraffect reality.It's impossible to bring anything into the realm, not to mention takinganything out.But the statues in the cave actually exist in this world.
```

### [10] hash=`4d954162f27f34f5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
They are tangible.That means she's gone much further than I do.She mastered a method I'm not aware of.What bewilders me is her arcane skill.How did she do that if not for the Manus' help?She also knows that cave a lot better than I do, right?We never hung out much.How long did she stay in the village on her last visit?A month maybe?Or two weeks?I'm not sure.I even crushed her glasses by accidentally sitting on them.
```

### [11] hash=`71ceb531ff8d186d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Those are the same glasses you have on your belt.At that time, I thought she was a distant relative I don't know of.After all, it's rare to meet someone so clever and open-minded in this village.I even lent this room to her.This was my secret basement, you know.But only after we parted did my father tell me that she's my sister,the daughter they sent away for lack of Arcanum talent.I do remember those days roughly.
```

### [12] hash=`01a2d202f9a7ee6f`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Back then I couldn't find her in the institution.I was all alone for a long time.What happened to her has inevitably affected me.I grew more and more rebellious against the family rules.It's like a story full of cliches.Giving up the training, refusing to listen to my father, skipping all the practice I could possibly avoid.I didn't want to be the blockhead hedged by the so called family heritage.
```

### [13] hash=`f557a1afd23a4950`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Hatred could be the most likely reason.Actually, we didn't get along well after we left the university.Ever since our identities as Arcanists were we couldn't stay in the institution anymore.That's also the beginning of our disagreement.I was taught that, on the way to proving myself, ourselves,we were each other's only friend and best partner.How could I finish my study in a campus full of humans without her?
```

### [14] hash=`2f8178d426134714`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
But then, my mind was changed.I wouldn't have connected Komar with the Manus Vindictaeif Hamani's words were all I had.But I know that was not the first time they madecontact.Yes, I don't know the reason, but the Manus has contacted her long ago.She gave them the cold shoulder at the time, but I knew something inside her had changed.Soon after that, she left me, taking all the materials with her.I know the only
```

### [15] hash=`78ee43aa1ea1cf1d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
thing I can do to meet her again, is keep walking on the way to study that celestialbody.That will lead me to her one day.As I said, we could frequently feel the existenceof each other from the changes of the celestial body, but she could always find more informationthan I do, because the traces left by Arcanum are more obvious than those left by science.This connection between us conveyed my belief to her that one day we would meet
```

### [16] hash=`a223161db4e24e5f`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
as colleagues.I just didn't expect that this would be the final outcome of myobservation, or that we would end up on the opposite sides.Can there be anylamer stories to tell than these two?For now, we can't find more clues in ourhouse.Maybe we should go to the shrine again?How much do you remember themyth of your family?As I just said, that was the primary material of ourconvenience of Arcanum.If I can foresee any sign about Kumar, our problem will be
```

### [17] hash=`b954d72907a6361a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
ended with the help of the great Mathilda of course.Okay, take a deep breath, giveme your hands, rest them on top of mine.Yes, like that.Now think of Kumar in yourPinstation?Already reached Mokpo?
```

### [18] hash=`5d3d9737cf2a2466`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
have come to me I don't know so many times father has already scolded meseveral times for letting Gina learn all those unorthodox stuff from you youknow those human books you can see even Gina's mother has no help in thekitchen now I even have to prepare the candles for Deepa festival myself nomatter what you say I'm not taking your advice this time you wouldbetter leave before my father comes out you know how mad he gets when he
```

### [19] hash=`d062e35f6d82184e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
She's a human.Rajesh, who are you talking to?You?You again?Listen, please listen to me.This is an emergency.There is no time to understand the whole thing.Just make it clear that this whole village will be destroyed by the earthquake.You and your family should leave immediately.Enough.Enough of this talk.I know your plan.You want to get us out of here?Never!No, father.You know Sharjah is always...
```

### [20] hash=`9bcdf3daa71e2422`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
I'm talking to him.Go away!Or else...Hey!Who are you, you fool?And what are you doing in the middle of nowhere?Tanjira!Who else should I help?Your ungrateful old man?You!How many times Sharjah has helped you, and taught Jinnah a lot of things.You people have only treated her badly.You only talk about arcanists and humans.Stay here if you want to.Sharjah is trying to save you all.But no one wants to listen?
```

### [21] hash=`4ac865accccf7b8a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
Let Ulka Pint fall, so that you all can crush under her.Please forgive me.This is...Kanjira, stop!Don't bully me!It hurts!I'm bullying you!Why you must look for trouble?Kanjira!After all the things you do for them, how can they treat you like that?Just leave them alone!Come with me!I still have your spot on my caravan.The time for entering and exiting the trains at the station is the same every day.
```

### [22] hash=`243a7048b846725e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
I remember it well.There will be a train leaving here soon.There's still time.Kanjira take a deep breath and listen to me.I know you said all those things tothem for me and I appreciate that but think about it if I treat them just thesame way they treated me just stand by and watch them head to death even if I'mdoing this out of understandable fury how would it make me any different tothem volunteering to help you and in your opinion risking my life to save
```

### [23] hash=`1042bcbc298eca4b`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
We are all out of my own will.Hatred doesn't end itself, Kanjira.It has to be ended by someone.I don't understand.Do I?Do we mean nothing to you?How come?What gave you such an idea?You are my most precious children.All of you are my treasures.But the first time you preferred they over we.You always put they first when there's a problem.Kanjira.But I am not a kid now.If I can, I don't want to be an Arcanist too.
```

### [24] hash=`97d6dc6b6d57200d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
So me, you and Achar is the same.Kanjira, don't cry Kanjira.So you've been thinking.Little one, you're just like us.We are your family.You don't understand Visharja.Enough talk.Maybe I don't understand any of your lectures.But you can't stay here.I'm sorry Kanjara.I have to admit they'reUnreasonable, but as I said we should put that aside now.It's a matter of life KanjaraI can't you is not listening to me at all
```

### [25] hash=`5b19e9a9fc03338a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
We are savior and go we live here on our own KanjaraThen you submit the beat.Yes, sirWhy is there so much silence here?There was a lot of crowd in the sea.So much crowd!Oh Boss!Here!It's safe here.Come here.I almost died.Thank God you are fine.What happened here?I don't know.Some scary people suddenly came.They had put masks on their faces.There!There are some other people on that platform.I don't know where they came from.
```

### [26] hash=`7ef969a064ab3dff`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p7`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（07.银手镯.）

```text
and started attacking the pilgrims without any reason.Thank God, all the pilgrims had left from here.They were saved because of Mishra Jaq.We were waiting for you.You have come alone.Where is Mishra Jaq?Shant, they are coming.Don't you see?Oh my God!You don't need these things right now?
```

### [27] hash=`72f31ff48839fc16`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
I was always, for most of the time, the best student in first aid class.The pain is gone, yeah?Not bad.D-Ling!Chai's!Hmm, I didn't expect to see this.What a spacious yard for a house located right next to the train station.Old buddy, I'm surprised that you're still here.We have settled everyone so far.I didn't expect so many men as members here.I've never encountered them before.They can't be communicated with.
```

### [28] hash=`55941ec319c20bae`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
How horrible.And since we meet them here, it means I did cooperate with the menace.It's completely out of control.The incantation in the cave.She must be able to detect the fluctuation caused by it, and that gives us away.But what in the world is her purpose?Did she think I would stop her?So she deployed these things to slaughter the village.Does revenge matter that much to her?I trusted her.I never believed she would do such a thing, even if we're no longer on the same path.
```

### [29] hash=`7ba5cc60a7e79ce0`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
But the reality tells me, my trust in her is nothing but a joke.Hatred changes people.It's not a choice, Calabona.You don't have to feel bad for trusting people.You trust someone because they're trustworthy, but you never need a reason to hate.Let your guard down for even one second.The toxic idea will sneak into your mind, and it would be impossible to get rid of it.It will burn your mind and sanity until you become an animal living for revenge.
```

### [30] hash=`611a928ad40d2293`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
Even forget your own name.Oh, don't look at me like that.It's nothing personal.In my mind, she is still my cool and scholarly sister.I was young and easily fooled back then.What I said was based on my real life experience.I was way more outrageous than her.I mean, we were all young once, right?No matter what, she's already on the move.But we don't even know where she is.Think about it!But Sharjah's still out there.
```

### [31] hash=`1752bce2fbb066b4`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
She can't use any arcane skills.If she's fine by the mask monster?SPF-1 portable contact device activated.Abnormal arcane skill fluctuation detected.Conducting analysis.It's itself?Source of abnormal arcane skill fluctuation confirmed.Similar faction, Manus findictae.Margin of error, 0.121%.Emergency support application sent.Adjusted support application priority to high.Does it mean we can ask the Foundation for backup now?
```

### [32] hash=`c0d9fe0c7cfeb558`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
Yeah, that's good news.But the Manus are still wandering out there.Before the foundation evacuates them, the village will be destroyed.We can't just sit around and watch.There is another way.What way?If she can do it, I can do it too.Maybe I can find traces of her if I enter the realm, because I also mastered meditationskills.Yes, that's right, I know the path inside.What do I need?Yes, water.Enough water to soak me in.
```

### [33] hash=`c17c76e1e7eb4da1`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
Now hold on, please wait.If it was so easy, why didn't you look for her in the realm in the first place?I...It is a risky move, am I right?How did you know?Oh, just my instincts or experiences, perhaps?No offence, but when I look at you, I see a desperate tiger cub cornered by the hunters.The situation is not as simple as you think.Since she can invite us to more punk, she can play the same trick and invite you to
```

### [34] hash=`f18430a8432660e5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
her realm.This could be a trap.A trap to keep you stuck inside the realm.You are right.It is a risky move.With the other two idols as her anchors, she's the true dominator of the realm now.I can't foresee what's ahead of us in there, so I've been avoiding it.We don't have other choices, do we?Now we are talking.You seem ready.But...Whatever you decide to do next, don't.This is the advice from an experienced hunter.
```

### [35] hash=`b3d2a5fe23a135b5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
Because whatever is in your mind now is going to send you into the hunter's trap.This happens to all kinds of animals.When the animal realizes it is cornered, its mind will be in a muddle.It can't think of anything else, but at the same time it strangely grows overconfident.It will take the gamble of escaping from its last way out,which is also going to be the entrance of the trap.Trust me, I know how you feel.
```

### [36] hash=`2b110c7b56059da1`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
You thought there's no way out, but a footlogged bridge?The Manus followers are still wandering about, and some villagers haven't been moved to safer locations.But sometimes, we must take the risky path to get out of the dreadful situation.Even though it is full of traps, it may not solve all the problems.But it's better than doing nothing.If this really is a trap, that means we will meet again.And I have been waiting for a chance to talk to her face to face for too long.
```

### [37] hash=`806ca64d146af211`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
I have been chasing after an imaginary goal since she left me.I watched that star closely, taking down everything that I could observe.However, despite all the efforts, deep down I know better than anyone else, it's useless.I remember those days.Almost half of which were like living in a mist.but now but now I can feel it her silhouette is right there in front of meto be honest this is not the best time to seize this chance no matter how I
```

### [38] hash=`b0a3a76dee1d2a9f`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p8`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（08.泪水壶.）

```text
look at it this is too good an opportunity to pass up okay fine if youinsist on doing this I will not stop you we all have our lessons to learnAnd you are right, we don't have any better options.What is it they say?No risk, no feast, huh?But please keep this in mind.No matter what happens, your safety will always be the top priority.We cannot bear to lose someone who is capable of putting this to an end.

I will.
```

### [39] hash=`17a9f1ab60b7717a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p9`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（09.小守护者.）

```text
Are you sure?To use this?What's wrong with it?It has enough water to soak me in.You are much more practical than I thought.Before I go...Are you going to take it with you, Miss Kahalabauna?No.Shermaine has a point.This is our last chance to win this fight,and it should be kept away from Kumar as far as possible.Miss Kahalabauna?Take this with you, then.This is your...Pendulum.It's one of my collections.
```

### [40] hash=`65d61c4acd1847cb`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p9`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（09.小守护者.）

```text
One of the purest.Even I don't have a lot of them around.I realize that the theory of meditation you've talked about is quite similar to some of the crystal divination theories.So perhaps this will help you in the water if the crystal can stabilize the magnetic field and guide you in there.You...You need to be surprised.This is how quickly a genius can think...Thank you.Ah, great.So it's only me who can't understand this...
```

### [41] hash=`bb88a3895680de08`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p9`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（09.小守护者.）

```text
meditation in water thing?Well, it takes all sorts of rocks to form a mountain.Okay, the pendulum and enough liquid.And all I have to do now is to be more suitable in the place we first met,to recreate the observatory in the realm.Just an illusion in my mind.She remembered almost every detail of me as a child.Did it hurt this much when I hit someone as a child?Give me a few moves to deal with those brats at that age.
```

### [42] hash=`2c38ed9a6a5c7ca1`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p9`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（09.小守护者.）

```text
This feels...weird.Did Kumar put you here?To guard this fragment of memory?This shall be the obstacle in my wayto where I want to beand to face the illusion from the past.I'll offer your seat to the senior.What are you doing here?Go away!I was small and weak in my 12 year old roomOkay, but I never had any hesitation in hitting you, right?But why?Why you?To talk to you?I'm not better in this Samra either.
```

### [43] hash=`ddb51cd37cd05fc2`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p9`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（09.小守护者.）

```text
Then I'll have to do it in a different way.You've grown taller and you have stronger hands.Like I've dreamt of.So have you two found the graveyard of stars?So?What do you mean?Do you mean, Kumar?How dare you!You've become quiet again.Life is a conversation between someone's heart and soul.But I never thought that it would be done so quickly.Who's next?That'd still be me.Which is also you.We're 16 and the bad kids sitting behind us cut our hair.
```

### [44] hash=`32f35024ec9f777d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p9`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（09.小守护者.）

```text
Leave now, Kala Bhavna.The present.The thing we're clinging onto.Facing and chasing.Think what it is.Thinking questions that cannot be answered, just as you always did.What do you think I should chase after?This time, I won't be deceived, Kumar.Ever since that day, I have never stopped studying science.Keep moving.
```

