# 剧情图谱抽取 · batch 062

- 角色：`wu_ming_zhe`
- 批次：**62** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.6」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_062.jsonl`

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

### [0] hash=`9d8a9e1c7a188996`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
And now you think it's no longer worth the effort to put things back in order?yes you people are no more than passengers in my life drifting past melike those lanterns in the river what's more what is my purpose here if thegods of Shoti they serve don't intend to intervene the lights in the river aregone and they will be no more in the future what is she doing even shallowPut it away, and please give this another thought.
```

### [1] hash=`b5e600fde990d1f1`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
It's so late.Is he still looking for Romance?Is he still looking for the Red Bride and the others?It should be.Let's just let the others wait.It's not appropriate.Is that so?Then let's start first.I'll keep the wine for him.Everyone, the host has a lullaby to sing.Please listen.Everyone knows.I don't know the lyrics.I can't say anything about purple and silver hair.Just say something.Don't interrupt the host.
```

### [2] hash=`265002d22be04c35`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
How can I write the poem by myself?So I had to read a poem from the book.I think it's very nice.It's called君今屈枝 满酌不虚词劝君今屈枝 满酌不虚词It means劝大家喝酒有更多的酒喝不许推辞Is that really what it means?I don't care.Anyway,满酌不词再卷白波慧饮千岁 打通我入城起 乡邻们待我就很好 很亲切厨业设宴是我能为大家做的为数不多的好事情愿大家畅与美酒 厨业平安 朔日心想事成吕征 您要不要再说些什么我这老人家今日只需说一句 厨业平安就够了Good night, Chu Ye!Qu Niang, isn't that a good thing to say?It seems that putting the poem you wrote on the wall
```

### [3] hash=`3106cd09be608ed7`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
on top of each otheris still quite useful.Look at what you said.Our Jin clan has long not believed in sticking poems on the wall.How about we say thatwe should learn from Qu Niang to turn poems into handbags.Anyone who takes them outwill be very curious.Actually, what they wroteBut I still can't understand it, but the words are all very beautiful.Then who taught you these words that you said so fluently today?
```

### [4] hash=`92b7b9abfd36efba`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
It was taught by the former manager.It was the manager of the return home.He taught me.Speaking of which, is he still coming back?I don't know.But at this time, he should have already eaten dinner in his hometown.Qu Niang got his letter.If you don't come back and you really become the manager, what about the restaurant?What can we do?The owner of the restaurant has been coming and going every day.
```

### [5] hash=`3da2221c84e2f641`

- lang：`other`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
If you hadn't come, it would have been a complete mess.Qu Niang is a righteous person.She knows the big picture.She has a kind heart.Such a kind heart, whether she is the owner of the restaurant or the manager,she can handle it.The evaluation is so high.It's not biased, but there is something strange.Of course there is something strange.A few hours ago,她在直辞的一番话,仍使我记忆犹新。学无止尽,大抵如此。没有,没有你说的那样好啊,李政。什么话?
```

### [6] hash=`d65237e6bc2eb1e1`

- lang：`other`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
什么,绝记忆,无形地难,道语之貌,天语之行, 无以耗物内伤其身,守道年来的引诱。真有这事啊?Of course, even if she didn't know the words, she was still trying to learn them.She had her own understanding of the famous Chinese opera.If there was a student beside her, she would definitely be moved by her words.She couldn't choose the wrong words.Unfortunately, she was facing a demon, not a human.Facing a demon in a straight line?Qu Niang was in a confrontation with that woman?
```

### [7] hash=`691f399494c39638`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
She thought that woman was Xiang Rui, so she asked some questions.You dare to ask her?Aren't you afraid that she will turn you into a strange horse?I couldn't think of that much back then.It was the first time I saw Xingmeng with such a beautiful waist.So I...Qu Niang!Where is Qu Niang?What?This is...Where is Qu Niang?What's going on?Those two Hu people had colluded with Ge Tian a long time ago.They help Getian escape and now use the mysterious spell to hide in the outskirts.
```

### [8] hash=`13ca6081d5ef3a5f`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
If it's going to rain soon and the rivers are in danger,if they don't stay outside for a long time, they will definitely come to find you.Because you are the target of those people.Qu Niang, you...you have to leave here.You can't stay in the cellar.The cellar?The cellar is my cellar.Why do I have to leave here?You are now in danger.In order to ensure your safety, you have to go to the government with the guards.
```

### [9] hash=`657e993089eb9614`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Since Getian can get out of prison,it's unreliable.We only have one choice left.He's not Xiangrui, nor is he a demon.That's true.Because what you need to be afraid ofis the woman who made the wine.Line up!I knew you would come to her.Where are your friends?They asked you to be the vanguard.Qu Niang,you still have a chance to change.Don't turn people into rats.There are too many missing people.People turned into moths?
```

### [10] hash=`3d329cae9d35ed29`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Didn't the statistics say thatthe missing people turned into half-naked monsters?What is he talking about?You don't understand moths at all.Besides,what does missing people have to do with me?Qu Niang,are you still talking nonsense?Right?No need to talk to him.Let's catch him first.Surrender.And dispel your arcane skill.Turn the victims back to who they were.We will put an end to it before the Shuozhi.
```

### [11] hash=`0d5432173ea31060`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
But I don't possess the power to transform people from one shape to another, and thus cannot turn them back.You're asking the wrong one.You have to blame this on me.I've never met those missing people, and I have no idea what you're talking about.Is this because...did you have a grudge against me or something?Nothing of that sort.I'm here only to prevent an unwanted escalation.I could have just walked away, and there's nothing you can do.
```

### [12] hash=`3b10731fea1e1fbc`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I could have gone to other mountains, and life would have continued as it has always been.But for those who have been turned into half luchus, no one can get them out of this trouble.been turned into half Lushus?Are you saying that the animals in my backyard and those in the Jitsi?Are they all the missing people?But I thought they were just Lushus.The first time I saw them, it was clear that we were alike.
```

### [13] hash=`3739af19bf4f57dd`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
We're just some halfdivinebeasts.We must not be humans.I've done nothing totransform them?I'm just taking good care of them so that they can tell me wherethey're from and if they can take me home.The New Young Mountain shelters thebeasts.The beasts have white heads, red tails, the bodies of horses, and themarkings of tigers.When they neigh, the sound becomes music.The name isI understand you were trying to help, and that was enough.
```

### [14] hash=`d0510ef9f7743a64`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I don't understand.The Daoist said the one who can protect and benefit the people shall be a Xiangrui.If you can, but you don't, that would be wrong.I've done a terrible job.I'm not that majestic, nor do I look like any Xiangruis in the book.I can't even turn into a real Lu Shu.How is that enough?Jiu Niangzi, I think you need to tell us everything.Have you ever transformed people into loose shoes?
```

### [15] hash=`d408b25235836381`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Answer us!I was trying to help.Everyone get what they want, just like the former Julie.She wanted to go back to her hometown, so I offered her a drink and sent her back.Jiu Niangzi, do you understand what you are saying?Every word I say!Jin Yangzhi, what have you done?You should have asked this a lot earlier.What did you do to the Jiali?She came to my tavern and complained that you didn't understand her at all,
```

### [16] hash=`630a9ea01699a6fd`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
and that she was considering going back to her hometown.But it seemed far away from Pei City.She looked sad and tired, and didn't know what to do.So...so you...I must grant her wish.Mustn't I?The Daoist said a Lushu can easily go a thousand miles within a day.If they start running, go faster, that will be over ten thousand miles.If that's how I can help her, I should definitely do that!You...Just like, like now!
```

### [17] hash=`2d8433da98bdce8b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
If the Peiling River dries out, you have nowhere to go.Just turn into Lushus, and then you won't suffer.Those who can go anywhere they want to the north to the south wherever they want.I can grant your wish differentlyEven if I can't recover the river from drought.I was thinking going away freely might be a good choiceBut in the endWhat I'm doing is wrongShe'll numbs you not by doing thisWhat else can I do?
```

### [18] hash=`b76133fc3b1008dd`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Junangzi, remember what you said to me last night?Liquor has many different names, but they are still liquor.You can put on many different clothes, but you will still be the same Junangzi.Likewise, whether you turn me into a horse, a donkey or a lushu, I will still be the same Yenisei.You don't have to force yourself to become the people's strong ray.It's only an unreachable symbol.What matters is that the Jumang Si I know, but do whatever she could to help others.
```

### [19] hash=`263f581faa45bc49`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
That's just what the genre does, as far as I know.Even though some results turn down to be not so satisfying,your sincerity is as valuable as the genre itself.So now you just need to turn us all back.Yes.So turn back, where no path lies before you.I will think carefully, think of what I did before.I can do it, I can do it without them.My head is about to turn yellow.I'm so scared.Grandma!Ah!And we have no time left.
```

### [20] hash=`ba77f7ccb4d40601`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
South to south, east to south.In time to change of direction.One fire won't kill another.The church can extend.Follow me.This is...Be careful, Ping'er.There's an excrement under our feet.Our room is narrow.I can't see clearly.What are you doing?This is dangerous.Qu Niang, if you're still awake.We need to stop the Limu people.Who's stopping?Don't smoke.There's an Milky Way.The law has already been broken.
```

### [21] hash=`7ef67b5ab2aa3b0c`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
But Qu Ming, you should wake up.He said it's true.You can't do it.I just want everything to be back to normal.Is that too much?There should have been ways to undo it.But now, even I am confounded.Where pain is real, then...You said you can't do it.Not that you don't want to.Right?The arcane skill with conditions cannot be taken back once it is cast.Just like the irretrievable curses and vows in Siberian shamanism.
```

### [22] hash=`6ef3f661e861a272`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I can see some markings on this girl's skull.Like an unknown seal.I've been speculating about what caused limitation of her power.This may be the reason why she's in pain.A seal powerful enough to change one's marking on the bones is not to be easily broken.Skull?What you're talking about.I can't.I can turn them into lushu's, but not the opposite way.Maybe...maybe I can't be a Xiangrui at all.Qualified.
```

### [23] hash=`2294f39c7a578310`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
As one more question that seems to be overlooked by us all.How many people have drunk Jin Neng Su's liquor in the Merry Festival spirit?Tell me the truth, my mother is the ninth deer in the world, seems to be very great, but also far away.After all, except for the moment when she left, I don't really remember her.Your mother is Xiangrui who protects one side.What is Xiangrui?生儿有灵,选择造福一方,保护一方之名的大妖,就像你的母亲。
```

### [24] hash=`15c28fcd6fafb4cb`

- lang：`other`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
但祥瑞不应有私情,因这私情,他为你而陨落,你须得记住。又是什么?他不应有的东西,你也不需要了解。但,他没能走下去的路,你却应当继续走。What road?Is it a dirt road like this?Or is it like the road outside those houses?Neither.Staying in the city, becoming their protector, becoming Xiangrui, one day you will know.She took me away, but left me.Xiangrui's mother was also like that.So I thought separation was a price to pay in the mortal world.So...so I started to make up a mother, a Xiaorui, from those scattered words, from the different pictures, from the unreachable legend,
```

### [25] hash=`8de9b7121f6bfc05`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
and then learned to become her, learned to replace her, but also to see her again.I want to ask her, what does she think?If he knew that I, Xiangrui, did such a good thing, would he have any regrets at all?Regrets of leaving me, regrets of leaving me alone.Now it seems that I have never truly understood him, nor have I truly understood Xiangrui.Qu Niang, are you really going to...I know, no one has ever really jumped over it.
```

### [26] hash=`14cfa6da4706e5ab`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
In order to warn me, Li Zheng also told me many stories.Some stories that are not suitable to tell children.But I have to go.Because this is the only way.There is only a question mark.And saying that Japan should have a question mark.Thank you for letting me go.Even took clothes for me.Although Chi Li is not here,I don't know how to wear it.But it doesn't matter.New clothes are always new clothes.
```

### [27] hash=`7bb22c9388d3806b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I won't change my taste just because I'm not wearing well.Thank you so much.Then I'll go now.Maybe we'll find another way.You don't have to...Mr.Getian, we...We are left with only one option,which is to stand here and pray for her.Correct?Pray that the ask and acquire,or the divination,will answer us and give us what we want in a flash.But is it really possible?I think not.We should go.I heard today is a special day for the locals,
```

### [28] hash=`fb0d6479a90977a9`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
known as Sui Zhao Chuan.Mr.Getian, what is Sui Zhao Chuan?It comes from an ancient proverb,百载难逢,遂照春。It's the first day of a new year,and the first day of spring.Lichun, the beginning of spring, corresponds to the lower trigram of 坎 in the direction of 根, it is the season of life, a time when the weather is clear and yang fills the air.They are pleasing to the ears, but I don't know what to make of it when all these are put together.
```

### [29] hash=`5a764a19cb7d8024`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
立春 is one of the 24 solar terms.It signifies the beginning of spring.遂朝春 is how people would call it when the first day of the Du Shuo festival and the first day of spring happen to be the same day.It is a once-in-a-century good sign.Indeed.It's also the first day of a new year.I like the coincidence.Do you still find it equally pleasing if your teammates are not coming back?That was before the flood.
```

### [30] hash=`973bee4ad41744c8`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
The aftermath of that disaster lasted longer than I thought.I was so wrong to think it was over.It all began with the unstoppable flood.At first, it was just a few unusual tides that no one noticed.Then the flood came, followed by the destruction of the bridge.The temple on the mountain thus lost its connection to its pilgrims.The prayers were no longer answered.I do not understand what caused all these things.
```

### [31] hash=`9d6a4e3d2aac7fe7`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
My people left the mountain to help with the situation, but they never came back.And now, even this river beneath us is gone, just like the Yuan Temple, forever lost inthe fog.It's useless.The god won't hear us, nor will it see us.Please know that I don't mean to offend you with this question.Please.Can't you take those people to the other end of the bridge,if the condition of the divination is to go across the broken bridge?
```

### [32] hash=`7f9ae9c14f8d313c`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Though we're both outsiders in this place,you are more naive than I am.One can only meet the condition by going over the bridge oneself,even if the price is their life.You might think it's cruel,But what good would it do if people were easily given what they asked for without paying aprice?Wouldn't it make others' suffering a joke?You don't believe me.I'm trying to understand.It's all the same.I can take you to the other side of the bridge, but you must not be disappointed
```

### [33] hash=`18ce8cb8ec0ce6f9`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
if it ends up fruitless.Pardon?I can take you there.Why?Oh, I'm also an Arcanist.My instinct told me that I should flee to the end of the world the moment I saw you.You did run away, along with my poor teammates, who were turned into looshes.I could not have imagined being around someone with unreadable blood.Turns out, it wasn't as strange as I thought it would be.Not much difference, you mean?It was just some futile effort I made when I realized this was a dead end.
```

### [34] hash=`42c70cdc60f18c27`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
But I have no idea how it got to this point.Where are you going?I have questions to ask.Even if there are no answers?Yes, I think.It is the same for all these people.They keep asking.Even though they hear no answers.I know what you're going to say.How are you going to do it?We don't have any wood and chips like that.I will use my finger, mouth and water on the ground.You can ask too, whatever means you use.
```

### [35] hash=`c685417df1e12fa8`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
What I want to know.What's your question?Say it if you like.I think I will write it down.I'm going to carry out the fortune walk,putting wooden chips in their mouths.They're all here, right?Yes, with the wooden chips.They are here for the divination.but the chips are empty they will have to ask in their minds what would you likeme to do you can you can be their mouths hands and eyes you can also do
```

### [36] hash=`af88ca78fd10f664`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
nothing just like the good sir waiting behind us I see if they're here for thedivination I will help madam after we go back you're wrong it can hear usWho is that?It was her.The noise I heard.It was Chen Neng-se, right?It was an unusual disturbance when she jumped over the bridge.It was Jiu Niang-ze?Mr.Liu, did you see that?Yes, that's her.That's really her.High heaven, she did it.She jumped over!
```

### [37] hash=`9f8bca2fa9066f11`

- lang：`other`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
This, it's Jiu Neng-se!The river!The river is rising!The power of the divination?端的是百年南玉,云中却狂雨乱坠,异乡贫生,即使那崖岸上是至人晕眩之武器,崖下是去不可凡之深渊。I, Lu Shu, have fulfilled everyone's expectations and have decided to cross the bridge that no one can cross.For the sake of him, I will seek a way to get back to Gui Jia.You're wrong!It's Mutian, not Gui Jia!This...this...We've heard this story several times.You're really confused about making this mistake.
```

### [38] hash=`3a91719df74a7cc5`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Say the story!There is always a way to change something.Those of you who haven't heard about it,take it as you haven't heard about it at all,or forget about it.Hey, how is the story starting again?I remember that he said he wouldn't say it again.And he won the last ticket for it.Original fairy?How do you sleep in this quality?Who is our original fairy?A year before?唐后兰衣公子之问,我可全数听说了。I've heard all the questions about Lanyi Childe, the Queen of Tang Dynasty.
```

### [39] hash=`c687014cd91d5750`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
这,这,这,耳朵这么好使。This, this, this, ear is so good.我这回来,就像你,可是这鹿鼠传奇的一部分。This time, just like you, I'm a part of this legendary deer.我?什么意思啊?Me?What do you mean?鹿鼠月桥唤醒鸳鸟复生河流,黑林川恢复往日冲营。The deer, Yueqiao, awakens the abyss and rejuvenates the river.Heilinchuan rejuvenates the past.Ha ha ha, as for you,the变为他类 原是你自己卖酒食 缺金少两 坏了名声却怪师姐收成不良 赢生不易这陆鼠 可算是解了你的困境替你经营酒坊 还令你好好睡上一觉请来呀 坐享其成便是你想睡一觉起来 就有人帮我写了策论At a young age, you should learn to write your own stories.
```

### [40] hash=`855aa54f0f63a7f3`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
You're so young and promising!But you should go back and rest early.Tomorrow, you have to write some stories.But you can't write your own stories.Right?I have so many things to write about this time.Enough for me to write a travel note.What should I call it?Travel in the East?Journey to Pei City?Neither of them sounds good.There are already too many travels and journeys.I think you are different from those authors, Madam.
```

### [41] hash=`6bf9ac507a9ed51b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
So...Unlike others, the two of you have experienced it in its entirety.What do you mean?There was a beginning, and now here is an end.Forget not where you came from at the end.This is the entirety.The hexagram of water and fire.I'd assume this belongs to an elderly person.What about yours?This is Xu, the hexagram of waiting.Though I don't know what could be derived from it.The interpretation is simple.
```

### [42] hash=`290b9cfe8152b939`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Above is water.The Stranding Dragon, advising patience.Below is uprightness,which means you will smooth away the obstacles.Thank you, Mr.Gatien.No need.And what about you?Have you learned your answer?It taught me to let things be.Since I have left the mountain,I should follow what's inside my mind.I remember that at the end of the Peiling River,where the lanterns float,stands a great building.It might be real or illusion.
```

### [43] hash=`bf415805e1867345`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I have seen it many times,Yet I have never thought of going there.There's nothing there.We'll go anyway.What about Junansi?She jumped over the bridge.Is she never coming back?Perhaps we will meet againone dayLet's make camp after we get out of the forestWhat do you say?I'm fine with it.How are you feeling Mr.Durian?I'm fine with thatYes, that's the title.The title is actually not a good choice for a book on geographical discoveries.
```

### [44] hash=`042195727dbd14d1`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
On one hand, there is no doubt that schwa zhi is a difficult word for the target readersof this book.On the other hand, the word notes, in most cases, is used to describe the collectionsof informal essays.They usually record the daily talks of professional writers, and thus include a variety of ideasand inspirations.As a geographer, however, I don't possess enough knowledge of literature to write the
```

### [45] hash=`6529ebdd57c6f364`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
real notes, nor does the assistant who takes dictations from me, unfortunately.Even so, we have decided to use these words for the title, Postscript.The title has also been included in the first draft we sent to the editors of MotherlandDocumentary and the Department of Publication Review.The next page is missing.Let me see.Oh, found it.June 4.Sunny.I never knew the journey back to Omsk would take so long.
```

### [46] hash=`9a041ddd054f2b76`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
My assistant and I set off from Yekaterinburg last year, and we didn't arrive untilnow.In Omsk, we met the governor again.I left him some drafts of this book, in return for the help from the local scientific researchassociation.Those drafts have recorded the steppe ecosystem around the Om river in detail.For example, before we arrived in Omsk, we followed a herd of sheep across the river.The wool on their tails was apparently matted.
```

### [47] hash=`8d596e488794385e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I recorded this detail because the way they crossed the water was almost a miracle.It is known to all that sheep can be easily drowned because their thick wool holds themback in water.Yet, things seemed different for those sheep.They had been trained by the local Hurtis and were able to cross the river swiftly,as if they were only several balls of cotton floating on the water.When they came to the shore, I noticed that their hooves were in the shape of
```

### [48] hash=`2fd82fa1ab172d44`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
a round cake.With one slice missing, they climbed out of the water with their little cake hooves, shookthemselves dry, and continued on to the next pasture, never hesitant to go forward, neverlooking back.Seeing all these, I hope I would be as determined as these sheep in my future journey.Today's article was an extract from a geographic manuscript from St Pavlov FoundationIt's okay.I had a weird dream.
```

### [49] hash=`48b77a30b9221442`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
What's going on?This is a letter from the Foundation.A colleague from the Russian branch was transferred to the headquarters today.She has shown a strong willingness to perform long-term field missions.The headquarters intends to transfer her to the Timekeeper squad.Would you have a meeting with her?It is said that she is experienced in geographical exploration and survival in the wilderness.
```

### [50] hash=`b2d27ce69a640c88`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p10`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中英配）

```text
你们能听懂我说的话吗可不可以告诉我你们是从哪里来的怎么了娘子面生我们从前见过吗我不认为我们刚刚来这里真的吗天哪欢迎你们来陪成玩刚才也在街上吗真不好意思一来就让你们看见这种混乱的情况我保证这只是一场意外我可以想象你快速地反应并救了我们更多的麻烦没有 没有都是我应该做的而且大家也帮了很多忙你们找我是有什么事情吗如果有什么能帮上忙的请尽管告诉我这里有个案子人们叫你朱南斯你工作在朱斯对吗嗯 是的黎晓莹帮了我们找你我们听到你在街上的谈话那天天鸣鸣来这里吗羽人你说城外那位祥瑞我听说他以前好像来过今天就不知道了宵夜里的动物有什么新的吗我也不清楚今天我到池子点毛的时候围栏里就已经有很多年级动物了真奇怪啊为什么越来越多了呢它们都长得差不多我不知道哪些是今天送到的经常忘记自己刚才数到哪里了如果我识字就好了能写下来就不会算错我们来这里是为了帮助其实我们是商人的队伍当我们到城市的外面时我们的队伍被转移到马上并被带走一只巨大鸟
```

### [51] hash=`ba4694720972b7a7`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p10`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中英配）

```text
李正说那只鸟应该是他们在找的鸟人他曾经在鸟市里遇见过所以我们来这里要求帮助他们...他们应该不是马但是怎么可能呢你们的意思好像是说女人能把人变成...变成马明白难道因为她是祥瑞就会有这样的能力吗我们也听过故事中的传说者似乎是一种地区守卫什么神我只知道涉提神我只知道涉提神有十二还是十三位的样子但那些名字很多我都不认识我知道今年是社体神直徐的生辰年我们会请很多的年节动物去断桥供奉他走集合月桥是最有趣的我们会带着年节动物去到悬崖上的断桥前一起数着步数摆动身子像跳舞一样最后再尝试跳过去跳过了一座崩塌的桥上的山洋?这听起来很危险,而且还蛮有趣的。步步跳不过去的。还没听说有谁能跳过去呢。连最厉害的山羊都跳不过去,更别说人了。我们还会提前用神秘术进行保护,防止真的有人或者动物掉下去。山谷很深,掉下去就再也回不来了。我只是新来的,在上任职词回乡后,暂时兼任这个工作而已。他们跟我说,我只需要这几天把职词照看好就可以了。
```

### [52] hash=`67bb42822888d795`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p10`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中英配）

```text
所以,简单来说,你就是门守?我不是,我不站在门口呀。我也有其他事要做的比如我还要安抚那些被爆肝声音吓到的人有一种被神秘术加强过的爆肝声音很大的比刚才茶馆外面的动静都还要大很多请原谅她她没有意义伤害你的感受我们在东北说话不严谨没关系没关系我能感觉到她只是有点着急但现在着急也没用呀就像野猪上树也不是说会就会的哦 或者你们能从这些码里面认出来哪些是你们的同伴吗我看看这里有一 二 三三只半温码来 你们也瞧瞧我不能我没有时间去记录分别除了即使他们是我的队友他们两个人还是不在你们的同伴比三个还多三加二我们等著瞧瞧李仲找到的事吧对的,孩子李仲没有给我们写了一封信吗?对的,我差点忘记了请读这封信,朱耐姆斯它可能有关杂志的资料加高为蓝,早些放班,回酒坊跟什么呀?这些都跟与人有什么关系?别担心这几天我会帮你们多多留意新来的马的一旦有什么好消息李正一定会转告你们哦 这样啊你们可以住在我的酒坊里刚才忘了和你们介绍了

我正在经营一家酒坊而且 生意还挺不错的酒坊就在离直辞两方距离的金市中李政会知道的我还可以顺路把这些家伙都送回植瓷你们也去看一看其他的年节动物吧好主意这会很棒能帮助我们在街上睡觉的麻烦是啊不过等晚些入夜了街市上会更好看杜硕节有金灯和庭寮照得天上和地上都亮堂堂在晚上感觉什么都是特别亮的
```

### [53] hash=`9d3708bb03223e73`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p11`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中英配）

```text
你对Junang Si的说话有什么想法?你能否在舞台上问一问?跳过一座破坏的桥是像跳过一座山洞或爬过一座山这是一个不能遇到的情况就像那些商人说的不可能的价钱吗?你们是在说城外的断桥吗?不好意思大堂里的座椅都还没擦洗也委屈你们先坐在这里不要担心谢谢你们让我们留在这里这就是我们所说的破坏桥你可不可以告诉我更多?断桥吗?反正在我到城里的时候就已经断掉很久了在它下面是高高的悬崖对面是一个叫渊庙的地方但被雾崎遮盖了所以我也不知道那个庙是不是真的存在The Yuen Temple据说在渊庙里你能和直徐对话有什么问题你虔诚的问他他就会回答他们管这叫什么来着,好像是问补?而且据说那里的雾气有些奇异,不能久留,否则会让人昏迷,或者变得过于兴奋,我是没有见过的。就算会这样,以前的人们都还是会去月庙,就说明问补确实有效呀。在桥被洪水冲断之后,可就再也没有这样的好事了。看起来很奇怪,那里已经有一个桥了,为何人们不会在这些年代重建呢?
```

### [54] hash=`853161470c011770`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p11`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中英配）

```text
这个我知道,是因为水变少了,人们不能游过去到对岸,也没办法跳过去因为山河山之间的悬崖很高很危险,人跳不过去不过,如果能成为新的祥瑞,或许就能跳过去了他们是很厉害的,八面威风,还能守护一方,为众人排忧解难我去打晚上水缸那边没有点灯还要过一条小溪我怕你找不着地方圆圆的,我瞧你们不见,还以为都歇去了呢Oh, sorry, madame bismuth is tired, so thank you for helping us这些话就不必说了,呢,这是你要的水怎么了?It looks expensive哦,这是别人给我的我不知道它贵不贵,但它很漂亮,是吧?Yes, it is delicate上面画的是鹿鼠,一种翔蕊它好雄伟的,尾鬃就像傍晚的云霞一样呵呵,我很喜欢它,也希望你会喜欢太好了,而且它看起来有点像那些驾驶马它们两只都很像驾驶马但大家还是觉得它们是马,不是吗?当然是,我觉得这类型它们是来自贝斯城的
```

### [55] hash=`311e382526efbaa3`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p11`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中英配）

```text
是个很有趣的发现,会帮助我们提升旅游记录你的饮品好闻这是一种睡眠药吗?听起来这里有很多种不同的药I thought liquor was just liquor.At least there aren't so many types in my hometown.好吧,其实我也不明白,为什么酒有这么多不同的名字,却都还是酒。如果是因为它们颜色不同,那我换了一件颜色不一样的衣服,我就不叫曲娘了吗?没错,如果你的同伴变成了马,或者别的什么颜色的动物,那就不是你的同伴了吗?他们是,当然,我其实在担心也许不只是担心,我不知道你看起来,真的很想念你的同伴想念她们我不会用这句话来描述我的感受我只想的是她们变成了动物因为我给了她们一个错误的方向如果…如果她们无法变回正确的自己呢?我觉得不会这样的事情一定不会变得更糟糕我觉得一定会有办法的就像天空出现彩色的云朵池水变得如春酒般甘美一样天地之间还有许多吉祥的征兆没有显现

你想想,也许月庙是真的呢也许,也许会有别的办法让你能认出你的同伴而且,就算羽人不是祥瑞,这城里却还有别的祥瑞总之谢谢,小姐不,朱南瑟我明白你的意思我真的明白谢谢这有什么,我一定会帮你们的我口袋里还有一些甘酸枣仁你快把水喝掉,我去给你泡三枣水,也有助眠效果
```

### [56] hash=`f0ca80cb8e672fbb`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
the yard go downstairs and through the main hall.What's that sound?Where does it come from?Who is it?Someone's singing?Horses glowing?What?What on earthhappening?Give me to drink?Junangzi, where are you?Is she?Lead them away!Stop here!I must go further.Keep going.You're so weak.Who is it?Only you.The man who stole our horses.You have to come with me.Jing Sheng, it's dangerous here.Say no more.What's going on?
```

### [57] hash=`b9d2231e50ee1bd9`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
We're not here for you to demolish.Who are you inviting?The two people who came yesterday are still sleeping upstairs.What kind of person are they?You mean Yu Ren?He's been here before.Why is he here?He's not Xiang Rui.I didn't do anything good, you're not allowed to treat her to a drink.If you want me to see her, I'll definitely...Wait, what?Who was taken away by her?Tea color and sauce color?What color?
```

### [58] hash=`18aa77b874f1e29d`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
Why am I getting more and more confused?Next time, I'll definitely make more for you.Look, what are they talking about?Please be careful.Here, let me help you.Thank you, thank you so much.Where's Yennece?Did you see her upstairs or in the yard?Is she your friend?I didn't see her.Did she go out first?No, not very likely.She would have told me if she was going out.Or at least asked someone to pass on the message.
```

### [59] hash=`7296269555a7d341`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
Did you really not see her today?No.I really didn't see her this morning.The missing persons cases.Is this how they happened?I...I don't know.Li Zheng never told me about it.If, I'm only saying, if this is another missing case, there must be a clue or two telling us what happened.Could you please look around and see if she left anything in the yard?She must have been taken from there, or I would have definitely heard the noises.
```

### [60] hash=`751414b1c0ce5ee6`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
Don't worry, we can go find Li Zheng.Wait...What's wrong?I sense an arcane energy.Someone cast a skill in the yard.Follow me.Where are you going?You can't see it.Tell me.I'll take you there.No.Please follow me.If you go any further, you'll reach the water tank.I had a water bath here last night.It's somewhere close to the water jar.I sense it clearly.This is...That makes sense.Li Zheng told us that the feather man uses a bone wand.
```

### [61] hash=`80ca4e793465242b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
Yenisei also saw something similar in that giant bird's hand when we faced him outside the city.I knew it.Now we have evidence.We can...No, it's not enough.And Yenisei is missing.Why?I think that's enough.Yuren's share has fallen here.That means she's been here.And your partner is missing.Doesn't that mean she did it?But only Yenisei knows what the giant bird looks like.She also drew the picture of that bird.
```

### [62] hash=`8c56574039abd30f`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p12`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中英配）

```text
Without her, we cannot confirm that the feather man and the giant bird are the same creature.Exactly.I don't think this is right.I just feel like we should do something, because you're sad.You have a point.Then, we...Let's stop here for now.Today, Li Zheng will also be there.He wants to tell me something about Du Shuojie.We can just tell him.Li Zheng will have a way.Sure.
```

### [63] hash=`5c8196a31aa1557e`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p13`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（13【葛生】.）

```text
本草姬与月桥所用年节动物皆不超过三只,一牛一羊一驴,未有例外。收成玉刹,城内少有可用的青壮成驴,以至于用马代替。可现今即使庆贺只需生辰,池子之内的年节动物也过多了,其中还有为人所变,断不可一视同仁。若要取消月桥之疑,岁除后便是朔日,须得尽早决断,必要。人生是在这年节关头,烦扰从来都借种而至。你便是掌事之人,可上次我所见的明明是另一人。我有要事相告,若是再不阻止,万事修矣。我乃葛天,此行事为告知,那九方娘子以术法使人变为露树形貌,须得尽快阻止,以免遗憾更广。她骨相过轻,形状尚在生长,也因此作为不定,恐为祸患。你指的难道是曲娘?正是。古相,难道,你是可视古相的黎山母,但你的身形分明不似黎山老母?我自然并非黎山母。那这些言辞从你口中说来,岂不无人相信?你还不若声称自己是黎山母?而且,黎山母啊,且看看周围吧。你说的是这些门间,人面,鸟声,红尾,你们画这些,我并非祥瑞,此类筹措或祈祷毫无必要。这些并非向祥瑞祈愿的门间,而是你的通缉令。
```

### [64] hash=`c83d53faaca6bf37`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p13`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（13【葛生】.）

```text
无论如何,现在捉拿曲娘最为要紧,正是她造成了城中的这些失踪案件。我还猜想,你是前来自首或交涉,如今看来,却是我想多了,主动前来攀摇娶娘,你是全然不知,自己才是头号一贩呐。这与我何干?我们数次收到人口失踪上报,次次与你现身于城内,挟动我来到执辞的十日关联。这是污蔑,当时那位执理应知晓我的来意。当我们赶往之辞时,你早已只身离去,不见踪影。无人为他作证,他自是被法曹视为胡言乱语,现已回乡聚宴。若非此事突然,我本就不会来到城中,自然没有久留的道理。况且,咽下神秘术随性示威的苦果,本应是值辞之责。你伶牙俐齿昨日正有两位胡商来到佩城向我们提供了一些线索而这些线索都指向你正是那两位胡人你认罪了?这是我此行要告知你的另一件事那两人其中之一线下就在此处他可以向你解释你说他是谁?稍待请看着茶水泼过的地方到你坐下再向你奉茶不是为何你立行仙前那样是说神秘术啊还是说须得干净的水才行河水不结应当没有这样的限制你之前究竟是怎样做到的
```

### [65] hash=`5adbfacd0257b758`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p13`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（13【葛生】.）

```text
将它拿下你这是何意疑犯因此我所知已倾书相告你们不去捉拿曲娘反而在这里纠缠于我找干净的水来我再证明给你不守旧情即可我不会同意你动手你抓不得我保护那红尾的马那可能是受害者你的力气总会耗尽的何须走到这一步仅仅找来清水于我我就能向你证明取娘的过错我又如何知道你的证明不是你用神秘术伪造的结果呢说到底我们了解你指认的罪魁取娘却对你一无所知甚至于在城内有人失踪前,你都未曾入过沛城。我们又要从何处判断你的话语真实与否。更何况,你说自己并非祥瑞。的确,我并非祥瑞。此前也从未来到城中,因为我本就不愿下山。你却还是做了这样的事。为何我一定要来到人世当中呢?你这话是什么意思?我的那些同族都已下过山了。为了你们,放弃性命,放弃族人,放弃性命,放弃,放弃一切,成为一个符号,一个图腾,变得谁也不是。语人,你究竟在说什么?我告知过可以怎样称呼我。语人并非我的名字。眼前语人或许非我族类。并无以名相称之必须,看来儿等却乎忘矣,

忘了过去那些下山的葛田氏,亦曾是建城之人,柱桥之人,抵御洪水之人,只记得一个久不存在,从未回应的社提神,所以我不愿,不愿下山,不愿相处之后,却又这样被猜忌或忘却。你究竟是谁?现今看来,桥段,乃是必然,已如在我之后,再无可填。桥段?你与段桥又有何关联?语人,你说清楚!就这样吧,你们尽可以来请住我了。Mr.Ning sir, please wait!不要过来!
```

### [66] hash=`38dc0195ea9a2d64`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p14`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】）

```text
他把女士拿走了,发生什么事了?现在我们又失去了一名证人,难道这也在你的计划之中?我的书账昨日便已遗落在她的酒房,你一问便知。娶娘是这样吗?在院子里是发现了一根骨头,搬那东西现在正在被掳走的胡人娘子身上。先把她捆起来,你还有什么要说的?该说的我都已说了,若再不制止,便是真的祥瑞来了也无力回天。你究竟为何执着于指认曲娘为凶手?凶手?我是什么凶手?曲娘,无妨,我们都知道你与失踪案无关。而且他还说什么什么真祥瑞也没办法,看他才是假的。曲娘,不必激动,现下只能暂且将他关押在植瓷。我自去告知法曹现在要紧的是派人去追回马和那位胡人娘子须得找到她的书章才可溯源把她也带下去吧其他人都散了徐娘你随我来我有事与你商议羽然你到底想做什么徐娘你明明看上去就像祥瑞为什么要说这样的话而且就算你不是祥瑞,你难道,难道不怕,不怕真的祥瑞降责于你吗?许致他早前未与我们有所接触,的确并非此地祥瑞,城中也已是庇护久矣。可是,山上的羽人就是祥瑞,但那是他的样貌,就能让旁的人觉得他是祥瑞。
```

### [67] hash=`b385b04d11b0bf74`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p14`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】）

```text
池里离开前跟我说过,羽人长得像钩芒,就像画册里走出来的一样。好像这能解释一切,可是画在书上的祥瑞啊。曲娘。但她当然不是祥瑞了。不像钩芒,或者灭萌鸟。她连绝技艺,无形地难的道理都不明白。绝技艺,无形地难。哎,道理确实如此,只要做错了事必然会留下痕迹。即使他试图嫁祸于你,我们在尚未找到数账和证人之前,也不能轻易假定他为凶手。我们还没有找到足够确证的痕迹,曲娘。羽仁,什么叫做真的祥瑞,你知道他在哪里,你又为什么要带走别人的同伴,却来这里指认我?这样的形貌是天道赋予的,就不应该因为自身的好物得失而偏离了这形貌应有的本性。明明可以变得像叔叔先生说的,像画册上画的那样好,那样受人们喜爱,就像大家所期望的那样。你把湖人小娘子和他的同伴带走的时候都没有考虑过人们的心情不是他们想要分离的时刻你令人伤心了这不是祥瑞该做的事好了许娘就到这里吧你们先把她带下去她也什么都没有告诉我大家都是一样的虽然我知晓你一直以来都对祥瑞十分着迷
```

### [68] hash=`59d720b5f566bec6`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p14`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】）

```text
但羽人今日来到之辞,言语中已经透露了他实则并非祥瑞的事实,甚至我以为他的态度更像是说他自身并非祥瑞,也从未想过要成为祥瑞。我不明白,他怎么能不想呢?并非人人都对祥瑞的传说如此趋之若鹜,黑城的确曾在祥瑞的庇护下有过不错的时光。但此去今年,那段旧日只能在神话典籍中查阅,甚至我也不敢论断,真正的祥瑞是否还存在。曲娘,您应该知道,现在我们也已不需要祥瑞了。不需要吗?现在没有祥瑞,甚至也没有了行之有效的问卜。但你看,我们失去了与渊妙的沟通,城中依然秩序井然杜说节也依然热闹非凡可见祥瑞并不是一成立足之必须这样吗今日看来原来你是识字的你知道我不会写字的 李政绝技易 无形地难不是的我只是听道士说过太多次所以记住了哪位道士是城中的道人吗?是我来到城里之前曾经与一个道士同行过一段时日他会重复一些话我总是听不明白但心里牢牢地记着听起来你曾有一位闲师毕竟你入城以后一向与人为善走上了一条与葛天不同的道路原来他叫葛天?
```

### [69] hash=`744759ddbb9a82f8`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p14`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】）

```text
是啊葛天但你刚才还是同她说的太多了她并不是你一直在寻找心中所向往的祥瑞真正的祥瑞不会毫无理由做出这样冒犯的事她或许只是一个久居山上的大妖究竟为什么要指认我呢?我不明白是我做错了什么吗?可以想见因为你是直理天人之理,已因她之故回乡去了,她见此法奏效,或是想要顾己重施,况且今日她闯入植瓷时,见我似乎相当惊讶,由此不难推断一二。还有那被掳走的胡人娘子,她……放下心吧,已派人出去搜寻了,我们现在也该去商定一下明早走击与月桥的事项。月桥?是的,还有这件事,要是断桥能够修复就好了,就不用粘结动物,也不用跳桥了。刚才我问葛天,可是他什么都不回答的时候,我就在想,如果我能直接问直徐呢?去冤庙?如果是真正的问博,那我想了解的事情,也一定会有答案吧。是啊,事情就是这样。葛天线下暂时收押在植瓷地牢,曲娘也还在那边。两个时辰前,我与直离曲娘商议后,决定保留走脊与月桥的仪式。只是那些生有异色的动物确实不便再用,规模相较以往直徐直年有所缩减。
```

### [70] hash=`a959035822cedb01`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p14`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】）

```text
此为人员名录与各类筹措明细,我令人摩洗了几份,已经送到各方去了。您辛苦。应当的。还有葛天一事,按照法规,须得杜硕节后再升堂会审。我还有一问,证据追回来了没有?尚未追回。越走胡人娘子的红尾马居大抵还是受了葛天的控制。等我们的人追到郊外,已经在雨中消失得无影无踪。城市郊外急雨,行路困难,可以理解。只能等此次雨停后再行搜索了。不过,一马驹斜一盲眼女子,应当走不出太远。待到雨停,我会亲自带队前去。劳烦法曹,分内侍罢了。指理呢?诶?法曹是问娶娘还是先前的那位?回乡的那位。大概须得等到杜硕节后才有消息我尚未收到她的回信曲娘毕竟年轻在回销那位直李传来消息之前还须得您多多看着直慈先她足够良善也正因此我才会向直慈贸然举荐若曲娘行事出了差池自然也是我的责任话虽如此年节事项繁多难免有所疏漏也不必太过苛责。正是,若你寻回了证据和那两位胡商,也劳烦派人知会一声。稍待,还有一事,是今夜岁除宴,法曹若是愿意,可携亲眷来娶娘的九方度过。

九方?那可是今室街坊都去?是啊,他宴情相邻,理由也不难猜。岁除首夜,反过年去,便是杜硕节的第一天,往年酒坊也是设宴的。末日,是啊,新的一年又是植须生辰,希望供奉著植须的渊庙,亦能传来好消息。
```

### [71] hash=`82011b3f489031f6`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p15`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（15【空心眼】）

```text
Is it you, Yannisay?Where are you?Please, not let them catch us.I'm good.How did you...I am walking to you through the water.Please, hurry up and get back on me.Turn into a striped horse too?Or is this your arcane skill?I am not a striped horse, madam.I'm a Lushu.Both of them are arcane creatures, but not the same kind.And yes, that's my arcane skill.Show images and a few sounds through water.Why are you different from the animals turned from Mr.
```

### [72] hash=`4454d392ec044011`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p15`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（15【空心眼】）

```text
Druryan and the others?You told me they only have stripes on them, right?Yes, I have an assumption about that, but I can't verify it now.What is it?Remember the river Arthin found?Perhaps that was the lower course of the main river, and it included Julans's arcanepower because the stream across her yard is near one of its branches.The running water might have diluted the arcane power in there.Usually, a stream of running water is like an independent settlement.
```

### [73] hash=`2413edd61fe8d9dc`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p15`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（15【空心眼】）

```text
It rejects outsiders by nature.Even I have been rejected more than once.The striped horses our teammates turned into could be an accident caused by an incomplete arcane skill.Those other striped horses in the Jitsu?Are they too...Perhaps Jumangzi had no idea at all that she somehow leaked her arcane skill into the river.As for the water I had, she must have made it on purpose.How did Ge Tian get involved in all this?
```

### [74] hash=`db07c53c3828dbfc`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p15`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（15【空心眼】）

```text
Last night, after he saved me from the wooden dolls, he has stopped.We need to find shelter, madam.Oh child, I don't see why he had to take you away.What if I was there with you?Ge Tian, Li Zhong, and Jian Ningzi, they all seem strange.Please trust me, madam.I used to think this way too.Maybe he's fooling us with a fake rescue.But he's not.He even showed me his arcane skill to win my trust.Yes, he read my bones.

Can you imagine that?He gained information by reading my bones.And then he actually told me something I didn't even know about myself.
```

### [75] hash=`b69d298d75db6096`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
If I let go, you will fall, and death will be your end.Hold your life dear, you are a lot more vulnerable than you can imagine.Threatening me?It's a river down there!Yes, but you don't know how shallow it is.Even a lantern can't float on it.It's dying, unlike the other branches you saw outside the city.So what?Does that explain why you captured me?The river is dying.I'm held by a birdman in midair.
```

### [76] hash=`8b7472af0e22c584`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
I'll fall and die if I struggle.There's nothing I can do.Yes.It's a rare wisdom for a girl of your age to know her limits.I'm not a birdman.I'm a Yao.My name is Ge Tian.You can use arcane skills.You're an arcanist.If you say so, then it is so.We have gone for miles.I'll leave you here.Beyond the fort, you will see the step.You don't understand.What on earth is your purpose?Why did you turn humans into horses?
```

### [77] hash=`e1c80b1f82955781`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
I believe you can commit much worse crimes if you want to.Are you doing it for fun?The more you ask, the more mistakes you make.There is no such thing as a wrong question.I will answer one of the questions.Regarding why I turned people into horses.The answer is I didn't do it.Neither did I have that intention.Interesting.Who did it then?The lady owner of the tavern.Junangzi?Precisely.If that's the case, why did you leave Madame Bismelster alone?
```

### [78] hash=`f25b82bc8077bfe9`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
Do you really think I would buy your nonsense after I saw you take my teammates away?You saw the horse in the yard with the red tail and red mane, did you not?Yes, I saw them.It's not a horse, it's a lushu, or at least it looks like one.Lushu?I have never heard of it before.It sounds like an arcane creature native to the east.It is a lushu, and also Jiu Nianzi herself.What?That thing is Junang Si?
```

### [79] hash=`e3f6ae40a29b071b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
What you saw tonight was not real Lushu.Those horses merely resembled half of them.I speak of the fact that Jiu Niangzi might be a Lushu, a kind of Yao, or as you would put it, an arcane creature.Your words sound even more complicated than those in the city.Is it because you are also an arcane creature, like the Lushu, or you have a thing only the pure blooded can understand?We're nothing alike.Lushus are Xiangrui's,
```

### [80] hash=`40a435a45505d301`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
born with red manes and white faces,covered with tiger's markings.In the books, Lushus are capable of casting arcane skillnamed the Shape of Well.It could be the same skill that Jiuniangzi usesto turn others into Lushus.Do you understand?Yes, I'll try.The Shape of Well is a dangerous and secret skill.As written in the books, the Lushus use it to transform blood into fire and stone into gold.So, it's like alchemy.
```

### [81] hash=`641701edaf87eeed`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
I'm unfamiliar with what you said, but Zhou Nianzi's power seems to be restricted.She cannot fully transform into a Lushu like a Yao could, nor does she possess great power.She is closer to a half Yao.Unlike other Lushus, she requires a certain medium to cast her skill, the shape of will.This is also why people did not recognize her.She is harder to identify.Xun Neng Si.Xa Fiao.Is that another name for the mixed blood?
```

### [82] hash=`845819044d0298fa`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
Anyway, even if you are telling the truth, how did you know that?It is within my bloodline.Like you find your direction through the water.I read people through their bones.How did you know my...Wait, you mean you can read people through their bones?That makes no sense.What can one's physical condition tell you?Many.Many stories.Many sounds.Even if I was never there with them.Such as you.The markings on your bones resemble an open net.
```

### [83] hash=`64da74ffc930fd00`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
Yet it captures nothing.You are away from the waterless landwhere you once lived,and to this day you are still wandering.What?You will travel far many times in lifeand turn homeward,like the migratory birds,until you find your lake.What on earth are you talking about?Have I mistaken anything?I should hope not.Forgive me,I have long since stopped reading other's bonesand put them into words.Perhaps I did not tell it in the most precise way, but it should be generally accurate.
```

### [84] hash=`95ea6b522ef6e2b0`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
Alright, stop.I need...I need some time to digest your words.Careful.Things again!They already attacked me once in the street!These stupid birds!This one is shining bright out of my way!Have you drunk the liquor?Offered by Jiu Niangzi?No, but I had the water from her.Why?The scent of liquor stands is not strong enough to attract them here.It would have taken a proper consumption of liquor for them to notice.
```

### [85] hash=`1c943e709be87d67`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
I worry that liquor is the medium for her transformation skill, but that is only myspeculation.If the water you drink also exerts the same effect on you, you'll also...What's the result?Someone has been here.A woman with a high-pitched footstep and a horse.It's not a horse, it's a horse.The footprints are even thinner and smaller.Look carefully.Where are these footprints?There's a shallow pool ahead.
```

### [86] hash=`8dd48cff0fc06c28`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
There's no trace of them after counting to ten from here.There's no trace of them leaving.It shouldn't be.If the footprints disappear,there's a chance of a flood.这里不应当还有其他痕迹。例如此处,藤的边缘,琴类脚印,梦琴,相当有力的执照大小,和加进的峰瑞程度。更早的时候,曾在此落脚。真的,这附近还有两组脚印。浅而窄,是年轻女子的脚印。此处,此低矮,靠近河面的中空树藤,昂不是普通琴类的理想落脚点。The young woman who came heremet such a huge and fierce Qin Xia Lubut there is no blood around her.Maybe the truth of the missing Hu Shang
```

### [87] hash=`a1299279edb71909`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
is still different from what people say.We need to go back to Zhici.Too late.So it seems her tea can also transform people.I must report this to the authorities.Stay here.Can speak through the water.You know what my arcane skill can do,but I can't maintain it for long.I spent too much energy fighting the Zhuyi's.I must take leave.She must be in great danger now.I have thought about it, given that my wand was also left in that tavern.
```

### [88] hash=`06f0ebb57081130f`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
But should I return, Zhonyang's might be alerted.I sense kindness in that girl.She hasn't done anything evil except for turning people into luchus.Your friend should be safe with her for the moment.The more urgent matter is to spread the wordBefore she further repeats her mistake, I must go find someone to handle this properly.In a person's case now, you'll be turning yourself in if you go alone.The world outside the mountains is indeed not meant for me to step into.
```

### [89] hash=`46002440057d92d3`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p16`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（16【见我所见】）

```text
But you are already involved.Besides, we gave Li Zhen a drawing of you when I was not clear of the truth.No matter.I will reason with him.Even so, you will need me there.Look at my arcane skill.It will be the best proof, right?So they will know that June 9th Sea is the real culprit who turned the people into horses, I mean blue shoes.If they really need it.You need to know that you are a suspect.Even though I know you are innocent, you need something absolutely persuasive to prove it.

All in all, you must take me with you.My arcane skill will vindicate you.
```

### [90] hash=`27fdfe88080e4f78`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
It looks so different than it does in the daytime.It's so quiet and empty, as if it's waiting for us.It's night time now.They have lit the braziers.There is cloth of different colors around them.Remember our New Year's?We put up the Harberos and made festive fights.There were also decorations on the houses.Yes, I remember that.Perhaps people here also stay with their families at this time of year,
```

### [91] hash=`ebdcde5c6fb3bc6b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
Like we do on New Year's Eve.A heartwarming custom.Yeah.The guards here are more reliable than ours in the Empire.At least they don't get drunk on New Year's Eve.Madam, we are close to the Jussi.We didn't prepare anything other than these bottles.Don't cast any skills for now.You need to rest.We don't know what's ahead of us.Hold on.Baggering footsteps.Almost limping.Sounds like this person just tripped and fell, or drunk.
```

### [92] hash=`28189014f991b8f5`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
Chunangzi?What is she doing here?Where did she go?I don't know if she's going to the tavern, but she has left the port.That's for sure.We should go find out what she drunk.It is...a wooden chip.Rough surface and some carvings on it.Is this an inscribed text?Maybe.Please hold it.I'll check the other side.Starting from the round end, there is a person, I guess, at the top.Then there is another person holding a bowl in the middle.
```

### [93] hash=`242dcfbd7f05ed52`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
A person holding a bowl in the middle, and then?Then there is a striped horse at the bottom.What does it mean?A striped horse?Goetian once said that a lu-shu has a red mane in the markings of a tiger.But we're not done with Jun Neng Tzu yet.Yenisei and the others are still in the shape of Lu Xiu.She was turned into a Lu Xiu in front of you.Are you going to just let her be?She has told you everything.
```

### [94] hash=`33e3cad1ab3b62e3`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
Yes, she did.Now you're the only one who can persuade others to go after Jun Neng Tzu.We are foreigners here.Listen to us.Today at the Zhici, none of us would have gotten away if I hadn't surrendered.They will always see me as a greater threat.You...I knew it.You two are in it together.The merchant identity was only an excuse you made up to enter the city.Isn't that so?No, please listen to me.The stories you told Li Zheng made no sense at all!
```

