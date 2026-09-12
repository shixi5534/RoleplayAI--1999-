# 剧情图谱抽取 · batch 063

- 角色：`wu_ming_zhe`
- 批次：**63** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.6」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_063.jsonl`

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

### [0] hash=`b00243e5006dbed2`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
How dare you come back like you did nothing, and break into the jail!You go first.Mr.Keqin!Luxu is our free-footed creatures.Get her back and leave.I'll join you shortly.Go!Don't you run!Catch them!Wait a while.Is he...?Have faith in him, child.He is able to defend himself, since he managed to escape without others' help.I believe...I believe he is not aggressive.He left his wand behind when he tried to save you.
```

### [1] hash=`49c275a220c459fb`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
You're here.You seem fine.Do you still intend to leave?Or have you changed your mind?I'm here for one last thing.When I was imprisoned in Zhici,I heard that Jiu Niangzi would hold a banquet at the tavern tonight.And the Fa Cao was also invited.I'll take the opportunity and get those half Lushus out of there.Please wait a second, sir.Yes?We're not going anywhere.We must release them from the arcane scale and bring them back.
```

### [2] hash=`02de13c15b77548a`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
If you don't flee tonight,I'm afraid there will be no better chance for you to leave.Though her true intention is beyond my speculation, I fear the consequences of her action will be severe.You know full well the consequences.Certainly.But you won't help us stop her.That is not my problem to address.I have done my part.Then why did you help us get rid of the soldiers and offer to help again?It doesn't suggest my further involvement in this matter.
```

### [3] hash=`30cbc5a232f29e21`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
You are contradicting your own words, sir.I'll put it differently.Look at the street.It is empty tonight.There was a time when people sent lanterns down the river on New Year's Eve.Even the simplest lantern would glow like the moon on the water.Those lanterns, carrying people's wishes, floated down the river.The further they went, the more wishes were granted.Some would cast arcane scales on their lanterns to keep them from getting wet.
```

### [4] hash=`326f711f505ac0de`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
But most of the lanterns still disappeared in the depths of the mountains or at the waterfalls.I used to look down at the city from the mountain top, watching those lanterns float down the streams and merge into a light belt in the dark.They were more brilliant and vibrant than the bonfires that were lit up all night in this city.I'm sorry.I don't understand what you mean.Time is against us.Now the river has dried up and the water no longer has vitality.
```

### [5] hash=`71f1596b29664512`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
Rainfall is getting scarce, accelerating the dying process.What was lost does not compensate for what was given,so people no longer show up by the river and send their wishes at night.And I have lost my opportunity to watch the light belt.Even so, to this day I haven't fully understoodwhy I was impaled to leave the mountain.I once thought I couldn't bear the sight of those humans being turned into other creatures.
```

### [6] hash=`d07b4c689b8ed1fb`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p17`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（17【舍玉求石】）

```text
And now you think it's no longer worth the effort to put things back in order?Yes.You people are no more than passengers in my life,drifting past me like those lanterns in the river.What's more, what is my purpose here?If the gods of Shoti they serve don't intend to intervene the lights in the river are gone andThey will be no more in the future.What is she doing?Even shallow water could also be dangerous

She trust her.She knows what she's doingWhat is this our river lanterns?Yes, I can't see them, but I can feel the light.Are you appreciating them with your own eyes?
```

### [7] hash=`e5358e16c34ef5b3`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p18`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（18【除夜宴】）

```text
七娘,定年知道要在门口迎了?因为李正说过啊,我怎么了?瞧着红不熟色的这是竹叶花苗想着若是你,定不要别家酿的酒这儿呢,还有我自己绣的结彩两匹不多,对路纹好不好也寻个地方挂起来不比去岁你送的纸马差这太贵重了,我马上去挂起来哪里的话你这就知道站在门口迎客了我还想着偷偷的来 喝酒再同你打招呼呢各两个 三个 四个几个一个 八个 九还没数清楚呢也许是法曹未到他的姬儿早已落座只是尚未得见他本人这么晚了 他还在巡逻吗是不是还在寻找红人娘子他们应当是我们就这样让其他人等著 不大妥当这样那我们先开始吧我会给他留酒的诸位主人家有祝酒词要唱烦请听过大家都知道我不识字也说不出来什么紫丑银毛随便说点吧此下别打断人家说到哪里了祝酒词哪会自己写啊所以只好从执词的书上看了一句我觉得很好听是叫劝君今驱之 满酌不虚词没有念错劝君今驱之 满酌不虚词是说 劝大家喝酒有更多的酒喝 不许推辞真是这个意思吗哎 不管了总之 满酌不词再卷白波 会饮千岁
```

### [8] hash=`6f79fb4bad025cf7`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p18`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（18【除夜宴】）

```text
打通我入城启乡里们待我就很好 很亲切除夜社宴是我能为大家做的为数不多的好事情愿大家畅与美酒除夜平安说日心想事成吕正您要不要再说些什么我这老人家今日只需说一句除夜平安就够了除夜平安菊娘这说得不是挺好吗看来把人家写给你的情诗还是有些耳濡目染的用处瞧你说的我们京市早就不信贴诗在墙上了不如说现今都学曲娘把诗搅成帕子做包但凡带着出门人人都羡慕好奇呢其实他们写的东西我还是看不懂但字都是很好看的那今天这几句说得这么流利谁教你的呀是前任执理教的这样的心性,无论做酒坊主人,还是做执礼,都应付得来。评价这样高,不是偏心,就是却有其事。自然是却有其事。几个时辰前,他在执词的一番话,仍使我记忆犹新。学无止尽,大抵如此。没有,没有你说的那样好啊,李政。什么话?什么绝技艺,无形地难,道语之貌,天语之行,无以耗物内伤其身,守道年来的引诱。哇,真有这事啊?自然,群娘即使不识字,也一直在摸索着修习,对典籍名句亦有自己的理解。
```

### [9] hash=`045b779e87802e2e`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p18`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（18【除夜宴】）

```text
当时若有旁的书生在,也一定会为她的话语所撼动,挑不出错出来。只可惜,当时她面对的是妖,而非人。在直辞面对妖?莫非,许娘与那羽人对峙了?她以为那羽人是祥瑞,所以问了些问题。你竟然还问她话?你就不怕她将你也变成有半分的快马吗?我当时想不了那么多。我第一次见到行貌那么像画上祥瑞的妖,所以就曲娘曲娘在何处怎么了曲娘在何处这是怎么了那两个胡人原来与葛天早有勾结他们驻葛天越狱现已用神秘朔躲进了郊外只要是不久还要落雨河边滩险他们不在外面久留一定会过来找你因为你正是那羽人的目标曲娘你须得离开这里不可留在郊方酒坊酒坊是我的酒坊我为什么要离开这里你现在处于危险之中为了保证你的安全是得随巡防兵移步官府既然葛天能够越狱只此一不可靠我们只剩下官府一个选择他既不是祥瑞也不是什么大妖不用怕他呀的确如此因为你们更需要惧怕的是酿酒的这娘子列队我就知道你会来找他你的同伙呢他们让你来打前锋曲娘你现在悔改仍有机会不要再将人变为鹿鼠了

失踪者已是太多人变成鹿鼠同级列上不是说失踪者变成的是班纹怪马吗他究竟在说什么你在说什么你根本不了解鹿鼠而且失踪者和我有什么关系曲娘她在胡说是不是不必与她多说先捉住她
```

### [10] hash=`8a6936b735de312b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
Surrender and dispel your arcane skill.Turn the victims back to who they were.We will put an end to it before the Shuoju.But I don't possess the power to transform people from one shape to another, and thus cannot turn them back.You're asking the wrong one.This on me?Never met those missing people.I have no idea what you're talking about.Is this because I have a grudge against me or something?Nothing of that sort.
```

### [11] hash=`3023f69898546108`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
I'm here only to prevent an unwanted escalation.I could have just walked away, and there's nothing you can do.I could have gone to other mountains, and life would have continued as it has always been.But for those who have been turned into half luchus, no one can get them out of this trouble.I've been turned into half Lushus.Are you saying that the animals in my backyard and those in the jutsu?Are they all the missing people?
```

### [12] hash=`860f584f22730107`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
But, but I thought they were just Lushus.The first time I saw them, it was clear that we were alike.We're just some halfdivinebeasts, so they must not be humans.I've done nothing to transform them, I'm just taking good care of them so that theycan tell me where they're from and if they can, take me home.The New Yang Mountain shelters the beasts.The beasts have white heads, red tails, the bodies of horses, and the markings of tigers.
```

### [13] hash=`eab2d05bbe73dbcf`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
When they neigh, the sound becomes music.The name is Lushu.The striped horses you keep in the yard are half Lushus.They look like what's told in the tales,and they cry like humming songs in the moonlight.And the wooden dolls infuse your arcane skill,the shape of well into the liquor,which turns people into Lushus or half Lushu.As for the dolls, they were once soaked in the water of Peiling River.Were they not?
```

### [14] hash=`55a1a7cef5c668c9`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
The stream runs through the backyardNo, no wayThey're just for fun or or a bath.They should notWhat who let it in?Catch it.It's you the markings of a tiger and a red maneExactly what the feather man said, but his reflection is a womanFlection is that the foreign lady from the street earlier?You are a Lushu.You're a real Lushu now, is what a Lushu should be.But, why are you still here?Don't see what you mean, Ms.
```

### [15] hash=`d911e0a92f616ee1`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
Chumansi.You're hurt, and you shouldn't be here.It's not right.You're able to recognize your teammates, and had already left here.Wait, what?Oh, my God.I get it!Junanshi, you turned me into a Lushu because you thought that would help me find my teammates, didn't you?Last night, you said you would help me, so this is how you...But I was not asking for help.I was only being emotional, or pouring out my troubles.
```

### [16] hash=`88d7bf1abec93be9`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
Anyway, I was not asking for anything from you.From the thought, I could feel the sincerity from the bottom of your heart.It was too real to be fake.I understand you were trying to help, and that was enough.I don't understand.The Taoist said the one who can protect and benefit the people shall be a Xiangrui.If you can, but you don't, that would be wrong.I've done a terrible job.I'm not that majestic, nor do I look like any Xiangruis in the book.
```

### [17] hash=`b2eb4d9bff3feff4`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
I can't even turn into a real Lu Shu.How is that enough?Jiu Niangzi, I think you need to tell us everything.Have you ever transformed people into loose shoes?Answer us!I was trying to help everyone get what they want, just like the former Jili.She wanted to go back to her hometown, so I offered her a drink and sent her back.Jiu Niangzi, do you understand what you are saying?I understand every word I say.
```

### [18] hash=`bd185f78b41722ec`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
What have you done?You should have asked this a lot earlier.What did you do to the Jiali?She...she came to my tavern and complained that you didn't understand her at all andthat she was considering going back to her hometown, but it seemed far away from PeiCity.She looked sad and tired and didn't know what to do.So...so you...I must grant her wish.Mustn't I?The Daoist said a Lushu can easily go a thousand miles within a day.
```

### [19] hash=`6daafb88bcdd6b92`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
If they start running, go faster, that will be over ten thousand miles.If that's how I can help her, I should definitely do that!You...Just like...like now!If the Peiling River dries out, you have nowhere to go.Just turn into Lushus, and then you won't suffer.Lushus can go anywhere they want.To the north, to the south, wherever they want.I can grant your wish differently.Even if I can't recover the river from drought.
```

### [20] hash=`7f172b22700fe649`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
I was thinking, going away freely might be a good choice.But, in the end...In the end, what I'm doing is...Not by doing this.What else can I do?Junangzi, remember what you said to me last night?Liquor has many different names, but they are still liquor.You can put on many different clothes, but you will still be the same Junangzi.Likewise, whether you turn me into a horse, a donkey or a lushu,I will still be the same Yenisei.
```

### [21] hash=`9e31c79563b8f654`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
You don't have to force yourself to become the people's genre.I think it's only an unreachable symbol.What matters is that the Junangzi I knowwould do whatever she could to help others.That's just what the genre does, as far as I know.Even though some results turned out to be not so satisfying,your sincerity is as valuable as the genre itself.so now you just need to turn us all back yes so turn back where no path lies
```

### [22] hash=`ef12afc201558143`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
before you it's never too late to return all right you can talk now it'sokay what these handicrafts are able to talk how could you be manipulated bythem you know sir no no you're getting it wrong don'tYou must come to the Jutsu with me, Jun Yanzu.We'll see what we can do.I'm sorry.But I must fix it.I can fix it.This is all because of me.I need to...I will think carefully.Think of what I did before.
```

### [23] hash=`d19d3981d2190b8b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
I can do it.I can do it without them.I just came back from the toilet.Mom!This house has some kind of formation under its feet.It's hard for me to see clearly when the space is narrowed.What are you doing?This is dangerous.Qu Niang, if you're still awake, you need to stop Lin Mu Ren.Stop who?My little Mu Ren.I won't come back.This house has a mechanism, formation, and competition.But Qu Niang, you should wake up.
```

### [24] hash=`13aed9fb0912f43b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
He said it's true.He can't do it.I just want everything to be back to normal.Is that too much?There should have been ways to undo it.But now even I am confounded.Your pain is real.Then...You said you can't do it.Not that you don't want to.Right?The arcane skill with conditions cannot be taken back once it is cast.Just like the irretrievable curses and vows in Siberian shamanism.I can see some markings on this girl's skull.
```

### [25] hash=`3a0714786f2d6dec`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p19`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（19【如愿】）

```text
Like an unknown seal.I've been speculating about what caused limitation of her power.This may be the reason why she's in pain.A seal powerful enough to change one's marking on the bones is not to be easily broken.Skull?You're talking about…I can't…I can turn them into Lushu's, but not the opposite way.Maybe…maybe I can't be a Xiangrui at all…qualified?There's one more question that seems to be overlooked by us all.

How many people have drunk Jin Aeng-seo's liquor in the merry festival spirit?
```

### [26] hash=`e19202d193580d36`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
Are we really going in the right direction this place is nothing but grass grass and grassThe Eastern arcane skill you said is just a deception.No one is begging you to stay hereI'm Joe Niazi filling in for the former jellyAre you in trouble?Our teammates were turned into horses and brought away by talking giant birdYou should not be here.The Featherman is related to some disappearances in the city.
```

### [27] hash=`81e265d064a860f9`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
You're a Xiangrui.Why do you have to do that?Stop this now.Or even a real Xiangrui cannot save you from the disaster.They pretended to be merchants to get into the city, but they are actually with the Featherman.Casting the Eastern Arcane Scale we're looking for requires a price, a terrible price.The picture of the wanted is complete.Please have a look.Great!All thanks to that foreign lady.She must be good at...
```

### [28] hash=`471fce84d114619d`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
painting?A newspaper.Their cart has not appeared for a long time.I heard that the price was low and they didn't have enough workers.These merchants are greedy as a pit.Just like those farmers.Smoke, dust, searchers are the last thing this poor city needs.Last time she was on a trip for a whole year.She didn't send a single letter.Now she's going to places where you can only make friends with mosquitoes,
```

### [29] hash=`ea69409780367e27`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
mites and mites.Holy Mary, don't let her get sick.Or should I return home as a detective, like that woman?Oh, you mean the medal awarded for the research?It's bronze.Who knows how much it costs.Not to mention the points she missed.Young cavalrymen came and left, but she didn't even have the opportunity to meet them.and the knife in my pocket oh I need to waterproof the papers linen it's oh hereit is I could bring more new apartment this time why is it already used it's
```

### [30] hash=`53911e258e46a9d2`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
record I wrote from dictation judging from the handwriting I must have doneit in the wilds the edge is ragged so probably it's been stored for over asince it dried.Over a year.Oh, it's the travel diary Madame Miss Merz asked me to write down forher.Maybe I should call it travel notes?Either way, I think I had completed the arrangement and sentthe original to her.There's no way I forgot such an important thing.
```

### [31] hash=`97546db7e87fa0e7`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
So what is it doing here?And it's...it's missing a few days of records.October 10, October 16,October 17, cloudy.We saw the carriage and rented boats from the local farmers to sailalong the Om River before it froze.In this way, we might be able to enter the city of Omsk without passing the North Gate.After all, the travellers from the Far East had said, the city was heavily guardedlike a fortress, and the guards would not overlook the slightest inconsistency between
```

### [32] hash=`7fd07bde33161940`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
people's stories and their documents.We had to go through this trouble because we were in such a rush when we set off thatwe had little time to prepare the documents, they were far from authentic enough to convincethe guards.Before we left, I gave several speeches to raise funds for the travel.I elaborated on my plan in my speech in the park.One of my arguments mentioned the Du Shuo festival in the eastern land.
```

### [33] hash=`37b2278a9691bda5`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
Legend of the Du Shuo festival?I was gratified to see that the audience was drawn to the relations between land worshipand the historical geological features in Asia, and the investigation materials abouta long-lost arcane skill.While the forms of land worship vary from one religion to another, the stories aboutan Eastern arcane skill known to the merchants as Ask and Acquire, almost identical.In those stories, men and women with determined minds overcame the highest mountain and the
```

### [34] hash=`10a5e05682159bf2`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
deepest canyon to seek an answer.They patiently endured the suffering like the ascetics, pleading for the gods of Shirti'smotherly mercy and hoping to be given what they asked.Even to this day, after the seekers are long gone, the god has never shown itself to anyone of us.But we know it was there, for there is no better proof of the ask and acquire thanthis revived land.There is a sureness in people's remarks on ask and acquire.
```

### [35] hash=`00779e6b356e13ea`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
They are certainabout its authenticity, like any geologist would doubt the difference ofsoils in flood plains and mountains.That's right, do we really have to seeit to believe it?None of us have ever touched one sedimentary rock, but weTime we've spent running and waiting.What?Take a good look around.The rain has stopped.Don't act like you just noticed it, miss.How much longer are we going to wait, huh?
```

### [36] hash=`049e1742d412271c`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
Long enough for the vultures to eat the flesh and bones?Mr.Krolich, you're troubled by unnecessary concerns.The vultures are scavengers.They are here only for the animal corpsesbrought by the thunderstorm.They will leave us alone.So they don't pose a threat?Then what's with the waiting?If you're trying to get us back on the road, you have the right to propose it directly.The team discusses to decide the next step.
```

### [37] hash=`87e600223a1bca16`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
That's how things have worked all the way.We are not trying to waste your time.That's what I mean.We should get going now.I see.We will suggest the directions as usual, and everyone will vote to decide.Oh no, you don't get it.There's no need to discuss or voteHmm because we are not going forward, but going back.That's the only direction availableI'm not the only one with this idea in this best man
```

### [38] hash=`1f544f0470785323`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p1`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（01）

```text
Those legends from the East that the show festival is it and the arcane trick you call ask and acquireNone of them matter more than our livesCan anyone promise there won't be another emergency like this?What if we can find shelter next time?We'll be lying dead out there, just like those corpses.I hear you.Given what happened earlier, it is only reasonable that you would wish to return.
```

### [39] hash=`c0f442ed014c2bea`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p20`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（20【别春山】）

```text
道士告诉我,我的母亲是从古至今第九只鹿鼠,似乎很伟大,却也很遥远。毕竟,除了她离开时从人变回妖母样的那瞬间之外,我不太记得她。你母亲是庇护一方的祥瑞。什么是祥瑞?生而有灵,选择造福一方,保护一方之名的大妖,就像你的母亲,但祥瑞不应有私情,因这私情,她为你而陨落,你却得记住。又是什么?她不应有的东西,你也不需要了解,但,她没能走下去的路,你却应当继续走。什么路?是这样的泥土路,还是像那些房子外面的石板路?都不是,有在城里,成为他们的庇护者,成为祥瑞,终有一日你会知晓。倒是带走我,却又离开我,曾是祥瑞的母亲也同样如此,于是我以为,分离,是步入人间必须付出的代价。将我关入佩城前,道士也曾经允诺我,成为祥瑞,便能理解她,触及她。这话很诱人,于是我就留了下来。起初,我日夜不停地咀嚼这句话,却实在不知道应该怎么做,因为道士也从未指点我应该怎么做,可我也没有其他的选择。于是,于是我开始从那些散落的话语,从不同的话策里,从不可触及的传奇中,试着拼凑起一个母亲,一个祥瑞,然后学着称谓她,
```

### [40] hash=`b8ed5f5be2bd5b66`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p20`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（20【别春山】）

```text
学着取代她,却也是为了再次见到她。我想问问他,怎样想的呢?若是知道我这祥瑞做的这样好,会不会有哪怕一点的后悔呢?后悔离开我,后悔将我一人留下。现在看来,我其实从未真正理解过他,也没有真正理解过祥瑞。曲娘,你难道真的要……我知道,从来都没有人真的跳过去了。李政为了告诫我,还讲过许多故事,一些不适合用来告诫孩童的故事,可我一定得去,因为只有这个方法了,只有问卜,而且说日本就应该有问卜。谢谢你愿意放我走,甚至还替我取来了衣服。虽然芷莉不在,我都不知道怎么穿她才对,但没关系,新衣服始终是新衣服,不会因为我穿得不好,就变了味道,真的谢谢你。那我这就……我走了。也许,我们会找到其他法子。你不必……Mr.Getian, we are left with only one option which is to stand here and pray for her, correct?Pray that the ask and acquire or the divination will answer us and give us what we want in a flash?
```

### [41] hash=`ec74163c2df3e708`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p20`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（20【别春山】）

```text
But is it really possible?I think not.We should go.I heard today is a special day for the locals, known as Sui Jiao Chuan.白仔难逢,遂朝春。是新年第一天,春天第一天。丽春。春天的开始,是坎的下半径,是根的方向。是生命的季节,是天气清晰,阳光充满空气。它们很满意我的耳朵但我不懂要做什么当它们全部都放在一起丽春是一种二十四季的宗教它代表春天的开始所以招春是人们会叫它当杜硕节的第一天和春天的第一天都发生在同一天它是一年一世的好日子确实也就是新年第一天我喜欢这种选择你仍然认为这种选择如果你的队友还没回来那么我会把他们带回来看看我能否做到我知道你的沉默是隐藏的但这是现在最好的选择毕竟如你刚才所说祈祷并不足够带他们回来他们可以只要一段时间但这只是在过去发生过的事就像你刚才说的日子可以只在我们记忆中存在吗
```

### [42] hash=`1a989685b6ffd959`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p20`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（20【别春山】）

```text
那是在雨伞之前那灾情的后果比我想像中的久了我太错了以为它已经结束了一切都开始在雨伞上最初只是一群不平常的雨伞没有人意识到之后雨伞就来了被桥头的毁灭山上的寺庙因此,它们的绳索失去连系祈求不再被回答我不明白它们为何会发生这些事我的人人都离开了山上为了帮助这个情况但他们从来没有回头现在这座河在我们身上已经消失了就像元天堂永远都失去在云里无法使用神不会听到我们也不会看见我们请知道我并不打算用这个问题来骚扰你拜托你不能把那些人带到桥上的另一边如果天使的状况是要跨过坏桥虽然我们在这里都是外国人但你比我更难看嗯?一个人只能遇到跨过桥的状况即使是他们的生命你可能会觉得很可怜
```

### [43] hash=`a5e1efbfd1b75786`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p21`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（21【天堑亦通途】）

```text
What is that supposed to mean?Judging from the fact that you have unreadable bones,you are certainly neither a young nor a human.A grom king?No.I'm also an Arcanist.My instinct told me that I should flee to the end of the world the moment I saw you.You did run away, along with my poor teammates, who were turned into looshus.I could not have imagined being around someone with unreadable bones.Turns out, it wasn't as strange as I thought it would be.
```

### [44] hash=`f35f3f9aa1cd5834`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p21`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（21【天堑亦通途】）

```text
Not much difference, you mean?Like the people here believe that there's no difference between humans and arcanists.Which makes me very surprised.Based on the bones I've seen, they are different.It's just that.Doesn't make a difference, right?We are the same when we desire something.I wasn't questioning you or the temple when I asked you about flying to the other side.I wasn't even questioning the strange condition of this arcane skill.
```

### [45] hash=`c3e01c03710e819b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p21`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（21【天堑亦通途】）

```text
What do you mean?Running out of options, I guess.It was just some futile effort I made when I realized this was a dead end.But I have no idea how it got to this point.Where are you going?I have questions to ask.Even if there are no answers?Yes.I think it is the same for all these people.They keep asking, even though they hear no answers.I know what you're going to say.What are you going to do it?We don't have any wooden chips like that.
```

### [46] hash=`e12ed8f3e411e276`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p21`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（21【天堑亦通途】）

```text
I will use my finger, mud and water on the ground.You can ask too, whatever means you use.What I want to know.Child, what's your question?Say it if you like.I think I will write it down.Like to carry out the fortune walk in wooden chips in their mouths.They're all here, right?YesWith the wooden chips.They are here for the divination, but the chips are emptyThey will have to ask in their mindsWhat would you like me to do?
```

### [47] hash=`2c576487610ff33b`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p21`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（21【天堑亦通途】）

```text
You canYou can be their mouths hands and eyesYou can also do nothingJust like the good sir waiting behind usI see.If they're here for the divination, I will help.Madam, after we go back...You're wrong.It can hear us.Who is that?It was her.The noise I heard.It was Chen Neng-se, right?It was an unusual disturbance when she jumped over the bridge.That was Jiu Niangzi?Mr Liu, did you see that?Yes, that's her.
```

### [48] hash=`c34dd80a5f78f254`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p21`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（21【天堑亦通途】）

```text
That's really her.High heaven, she did it!She jumped over!This...That...It's Chumansi!Turn into a lushu!A lushu!The people are back!The river!The Paley River is rising!My body's...What's happening?It's over!Coming form!I'm not sure if I saw it clearly.I think for an instant, turned into a real lushu!The power of the divination?The magic of ask in the choir?Oh wait, the people in the city have come back.

So maybe...What?What's going on?My head hurts.I had this...dangerous dream.Everyone!Indeed a rare occasion.
```

### [49] hash=`3ce360f3c3f4cd53`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p22`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（22【“所求必应”】）

```text
上回说道说道祥瑞路数人间历劫凡人悔恶正是且说那路数贤草且还厨业叩败了先生开解之恩自成中一别独往段桥去去之今岁朔日亦交春端得是百年难遇云中却狂雨乱坠意向贫生即使那崖岸上是致人晕眩之武器崖下是去不可凡之深渊陆属身负了众人期望决意越过这无人可争之断桥为他所避又者寻觅重启龟甲问卜之法你说错了是木天不是龟甲好好好这故事我们都听过好几遍了这也讲错您确实糊涂了说故事总有疏漏或再变劳烦各位听过的就当做是没听过一般全全忘了吧这说输了怎么又开始原先我还记得它说不会再讲了他最后一场的座堂票呢元仙你这一觉睡的元仙是哪个元仙翻过年以前后兰一公子之问我可全数听说了耳朵这么好使我这回来就像你可是这陆属传奇的一部分什么意思陆属月桥唤醒鸳鸟附身河流黑铃川恢复往日冲鸣人们年节走动频繁于是我便重拾就业了至于你那陆鼠收了你的酒馆将你变为咖喱原是你自己卖酒食缺金少粮坏了名声却怪师姐收成不良迎生不易这陆鼠可算是解了你的困境替你经营酒坊
```

### [50] hash=`ecda07e2a9828e5e`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p22`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（22【“所求必应”】）

```text
还令你好好睡上一觉醒来啊坐享其成便是我也想睡一觉起来就有人帮我写了策论小小年纪也习写策论年少有为年少有为啊不过还是早些回去洗洗睡了明日立起来温书要紧听故事可写不来色论是不是两个人都经历了这一切你意思是什么开始就开始现在就结束了最后你从哪里来的这就是一切因此快乐都发现了对不起我还是不明白你的语言没关系抱歉打扰你我们可以走了吗我真的想马上回家那我们走吧你所看到的可能是一张核心图,而不是它的解释,你仍然记得它是什么样的样子吗?它稍微改变了,就像这个样子水和火的核心图,我猜这是属于一个生物的人你的呢?这是虚,等待的核心图,虽然我不知道它是从什么地方来的翻译简单水在上面水灯在水面上要有耐心下方是亮面这意味着你会避免困难这意味着你会找到水你只需要等谢谢你我没有知道在你这一刻你已经在河边决定了
```

### [51] hash=`b79404e9ce5c733e`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
Let's make camp after we get out of the forest.What do you say?I'm fine with itHow are you feeling mr.Durian?I'm fine with that the riverWhat is it?The compass is working greatNothing, let's move the compass is working, which means we can rely on the map again.OhThat's goodAsk for the book.I'm going to writeYes.Have you decided the title?Yes.I will call it...Notes on Schwar...On Schwar...Yes.That's the title.
```

### [52] hash=`9a990ea99849f7d6`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
The title is actually not a good choice for a book on geographical discoveries.On one hand, there is no doubt that Schwarzy is a difficult word for the target readers of this book.On the other hand, the word notes, in most cases, is used to describe the collectionsof informal essays.They usually record the daily talks of professional writers, and thus include a variety of ideasand inspirations.As a geographer, however, I don't possess enough knowledge of literature to write
```

### [53] hash=`a4721ffae6526720`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
the real notes, nor does the assistant who takes dictations from me, unfortunately.Even so, we have decided to use these words for the title, Postscript.The title has also been included in the first draft we sent to the editors of MotherlandDocumentary and the Department of Publication Review.The next page is missing.Let me see.Oh, found it.June 4, Sunny.I never knew the journey back to Omsk would take so long.
```

### [54] hash=`aafef327e1346ab7`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
My assistant and I set off from Yekaterinburg last year, and we didn't arrive until now.In Omsk, we met the governor again.I left him some drafts of this book, in return for the help from the local scientific researchassociation.Those drafts have recorded the steppe ecosystem around the Om river in detail.For example, before we arrived in Omsk, we followed a herd of sheep across the river.The wool on their tails was apparently matted.
```

### [55] hash=`dce2ab5b76a5d8e8`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
I recorded this detail because the way they crossed the water was almost a miracle.It is known to all that sheep can be easily drowned because their thick wool holds themback in water.Yet things seemed different for those sheep.They had been trained by the local Hurtas and were able to cross the river swiftly,as if they were only several balls of cotton floating on the water.When they came to the shore, I noticed that their hooves were in the shape of a round
```

### [56] hash=`4539e9ce853f9563`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
cake with one slice missing.They climbed out of the water with their little cake hooves, shook themselves dry,and continued on to the next pasture, never hesitant to go forward, never looking back.From all these, I hope I would be as determined as these sheep in my future journey.Today's article was an extract from a geographic manuscript from Saint Pavlov Foundation FarEast branch, recorded by Yenisei.
```

### [57] hash=`cbebb94b4b69395e`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
Next is the news broadcast.Hmm?Miss Radio?Yes, I'm here.I...What time is it now?It's 4.15pm.The nap went on a little longer than I thought.Yes.How are you feeling?I think I had a dream.Are you alright?It's okay.I had a weird dream.What's going on?It's a letter from the Foundation.A colleague from the Russian branch was transferred to the headquarters today.She has shown a strong willingness to perform long-term field missions.
```

### [58] hash=`72cdb45390a639b9`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p23`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（23【他日再逢】）

```text
The headquarters intends to transfer her to the Timekeeper squad.Would you have a meeting with her?It is said that she is experienced in geographical exploration and survival in the wilderness.She could be a great helper.Geographical exploration?What's her name?Please hold on.Let me check her file here.And her name is...Yenisei.
```

### [59] hash=`f53f1a5ce09a44f7`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p24`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（07【远来是客】中配）

```text
请出示过所我们所有的通行文书都已经给你了这不是过所先生文书就在您的手上请再看看吧我不是先生凡请出示准确过所上面会写清楚你从哪里来要到哪里去如果我知道这个问题的答案我就不会在这里了没有过所不能进城我认为这张通行证上都写得很清楚了您瞧协会印发的过关文书在北边的周边关爱都使用没有理由在您这里不行他不行我不知道你用这个经过了哪里的关卡况且这上面的记录无论文字还是印章都不合规制我不能放你们进去这是玩忽职守换个人来跟我们说你听不懂我们的话我明白你们在说什么如果你的确能听懂事情实际上是这样的朋友我们的同伴被变成了马一样的动物又被一个长着翅膀的人带走了我们怀疑他们进了城所以才需要进去找到他们这很紧急希望你能理解我今日只守此门已于三个时辰从没见过什么长着翅膀的人编故事是无用的像你们这样想要浑水摸鱼的家伙我见过太多了规矩就是没有过所 不能进城看来这家伙是听得懂但听不进去小燕妮赛我要试试没有你说的这东西究竟能不能进去
```

### [60] hash=`47d8c21dae12a36c`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p24`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（07【远来是客】中配）

```text
你们要强行闯关真是不自量力我只是要试一试因为我们也没有别的办法了先生小燕妮赛正试图强行闯入关城门我们要关门了我们得进去否则再也找不到揪人眼先生他们了不能把他们丢在里面还有那些杜硕杰与东方神秘术的线索我请求你不要上前了我们或许真的该放弃了我甚至怀疑这一切是否只是一场可耻的幻觉那些怪异的地貌那些变成班温玛的队友还有眼前这这些我不能眼睁睁地看着你用自己的安危去冒险恰恰相反对闻所未闻的风度人情距离我们所追寻的东西已经非常接近了那些我们生来便要追寻的新奇而伟大的事物而且,你不也有问题,期望着索求必应,能够给出答案吗?更不必说还有纠若人先生他们不明的去向。与这些想必,我们的安全简直不值一提。说得好,若论安全,城内应比城外安全许多。我可以向两位保证。至于我,我在这城中最大的金氏任李正一职,两位称呼我为李正即可。李正?听起来,一位体面的先生。李正,这两人啊强行冲关入城。我已知悉,情况可控,不必关城门了。这两位似是胡商,正在我职责范围之内。
```

### [61] hash=`54ff27d7726417d2`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p24`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（07【远来是客】中配）

```text
况且正值节日,亦或许只是前来参加庆典的人,不必如此严苛。我瞧两位似乎丢了过锁文书。我没有文书,只是好像不能在这里使用。远道而来难免错漏,不过即使两位来此或为经商或为杜硕杰,这缺了过锁却仍是麻烦。杜硕杰,现在就是杜硕杰期间吗?正是。我还以为你们是清楚这一点才来到沛城。我们知道,但我们从来没有真正参与过,所以不了解,也不确定。我们只是听过这个传说。哦,不朔节,难道在你们的部族当中被当作同窑传唱了?哦,部族?不是那样的,我们来自北方。北人?我还以为两位都是西边巫孙族的后人。我听闻他们早已失落于哲罗曼关外,此前都无人得见。假知你们的服饰也相当奇特,这才贸然猜测了。实在抱歉。况且,您的同伴红发碧眼,帽色白皙,恰好符合史书上的记载。史书?李政先生你们的史书上我说过了称我为李政即可书中有言巫孙与西域朱戎其行罪役今知胡人青眼赤须壮类弥猴者笨其种也猴子吗或许书中所言也不可尽信两位听过便罢至于先前我们说到何处了
```

### [62] hash=`422bd957c01c8013`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p24`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（07【远来是客】中配）

```text
是否杜硕杰我们是为杜硕杰来的正是背成杜硕杰的氛围与一点曾经最鼎盛时每年都能吸引许多不远万里赶来的人想必两位自北而来路途遥远亦是如此辛苦了不过我尚有最后一问你这眼是双目接盟?您说的没错,这会有什么影响吗?对缺少过所文书的旅人来说,身有疾残或许并非坏事。今日当值的长门郎新才到任,或有冒犯之处,还请两位海涵。这便随我来吧,逗留城外并不安全。最近人口失踪案频发,须得四方走动巡查才能确保不会有人因被拦在门外而失踪。失踪案?
```

### [63] hash=`e35ae63fe217047f`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p25`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（08【十万个问答】中配）

```text
都先坐下来吧在这边我没有摸到座椅要怎么似乎是跪坐的方式这里有软垫两位随心坐下即可小娘子面色好些了方才想问什么我想问你们的城墙难道不会塌下来吗为什么这么说因为我看见城墙似乎是黄色的纯土石结构他们应该经不起雨水冲刷和大风侵蚀,更不用说,上面还有用木头架起来的阁楼。你独见其外,不知其中木桩已沉沉嵌入大地,土石竟为衣柄与外壳,无需担忧,即使墙砖剥落,它也存在久矣,与整座城的年岁相仿。整座城的年岁相逢,那这座城存在多久了?据我所知,数百年。县志占据了书库的一整片书架,十载为一本。数百年是一个比实际更轻描淡写的概括。城中多有历史遗迹,或许之后可带令辞前去游赏。贝斯美尔女士不是我的母亲。别女诗,抱歉,我还忘了她的演技。没关系,也许是因为我看上去行动太过自如,人们常常忽略这一点。宽心些,此事亦有好的一面。即使你行动无碍,我们依然会施以援手。我可以问一下这是为什么吗?对于我是盲人这件事,你们似乎很在意。双目失明为赌籍,残疾者受官府庇护,北人没有这样的惯例吗?
```

### [64] hash=`11694696e9a7befa`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p25`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（08【十万个问答】中配）

```text
这问题若令你感到冒犯。不如说,相当好。在北方,我需要付出更多,才能得到和寻常人一样的待遇。竟是如此。北边弱肉强食,我有所耳闻。却不成想,连极残者也得不到应有的庇护。既然今日你们已经来到沛城,就放下心来吧。而且,两位的汉话听起来十分流利,这会令你们在城中方便许多。您指的是,我们现在说的正是汉话吗?小娘子此言倒是当真有趣。在今世计策中,言语流利的胡人多数都在中原生活已久,而你们看上去显然并非如此。并且也没有频繁地出入中原,否则就不会连过所也忘记了。我得说,您猜得没错,我们在家乡时常年与那些会讲汉话的商人打交道。正如您说的那样,他们总是日夜兼程,穿梭于不同的城乡之间。如果不是有他们分享给我们的经验,像我们这样首次出行的商队,恐怕还会遭遇更大的危机胡商见多识广沛城也一向乐于与他们贸易往来对了,今世之中有些胡商,若无落脚处,也可去那边寻个旅店,那么还需此物两位需背起此类过所文书以作身份证明由此,才好在城中
```

### [65] hash=`992a31a8058c5f95`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p25`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（08【十万个问答】中配）

```text
行走,否则仍有可能被驱逐出去好的,那请问我们要怎么……请两位将线下写有的文书与我一关。让我翻翻的东西在哪儿?在我这里。一直都在我这里。女士,可靠的好孩子。我来看看。看起来像突厥文。这是突厥文吗?是的,可以说它是突厥文。我们北方也使用这种文字。孩子,这是你家乡的文字。也叫耶尼塞文,不是吗?哦,是的,没错。抱歉,我们应该考虑到这种文字在中原不那么常见。我了解了,无妨,只是须得两位自己写出来历了。具体行文参见此书。好的,我来写。不好意思,我好像也不认识这上面的字。啊?是我考虑不周。汉化读写的确比听说更困难小童今日不在既如此那便你们说我来写比如此处两位入城所为何事经商商队几人算我们在内七个人原本有七个人原本他们现在何处这也是我们想要知道的再来到这里的路上他们变成了马一样的动物,然后被一只巨鸟带走了。被变成了马?那两位如何幸免于难?嗯,我不知道。也许因为Bethmere女士与我是神秘学家,而他们是人类。
```

### [66] hash=`40f8d870c6de0941`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p25`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（08【十万个问答】中配）

```text
何出此言?难道巨鸟只袭击人类,可它又如何分辨呢?毕竟人类与神秘学家并无太大分别。什么?不大区别先不论神秘学家与人类的区别我认为问题也有可能出在水上穿越草原时我们发现了一条活水河流当时其他人由于长途跋涉的疲累在我们发现异常之前就喝下了那条河中的水是的,那是一条在草原上自西北方延伸出来的河流量不大,但很清楚你们所见的河流,也许是我们的母亲河佩玲川,但近来她已经濒临枯竭,也不会导致这般变化。那巨鸟长什么模样?黑色或棕色的翅膀,红色的尾羽,面目像人。还有,在我的回忆中,那位巨鸟具有青年男子的嗓音。面鸟身,那么便是羽人,他能否奏乐?他使用一种能发出声音的长条形乐器,还能用那乐器奏乐来控制动物随它前进。他是否还带着像骨头的短杖?有相似的东西,但我不确定,当时它与我们的距离实在是太远了。既如此,我大跃知晓这羽人身份了,若真如我所想,即使他本就并非祥瑞,这也实在……听起来,似乎还发生过什么事情。你们所见巨鸟或我们城中所传的羽人,
```

### [67] hash=`7c7f5b17e865e92e`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p25`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（08【十万个问答】中配）

```text
他曾被城中少许居民视为祥瑞,皆因其大致身形与传说中的勾芒相似。祥瑞是一种类似保护神的存在吗?并非如此,祥瑞多为妖类,但常与人为善,施术解难,浮游天地。在你们来报之前,城中亦有人侧面目击过持有股仗的羽人。据传,他曾将动物牵引至植瓷,声称所带动物实则为人所变。这……这和我们同伴的遭遇是一样的?家室却为同一人所为,那便足以怀疑他与城内失踪案有关了。原来之前说的失踪案,是这件事。可惜,我们那位侧面目击者甚至无法凭记忆给出一张画像。此后也无人佐证他的说法,自然被当作是胡言乱语了。为此,法曹甚至以为他中了邪,建议他趁节日回乡歇去。我们还能找到她吗?她是于执策工作的执礼,虽非官府要人,可这年节里也不能出现这样的差错,现下是其他人在执策帮忙。如果……如果我还能给出羽人的画像呢?虽然她当时非在半空,看不清细节,只记得扩形和翅膀的颜色,但我学过素描,而且有画地图的经验,我能画出来。素描,地图,嗯,即使你能画出来,我们也只能暂且发令通缉,捉不得他下狱。

一切还需得等到当庭对峙才行。不过,既然你能画,便试试吧。此处有毛笔与烟台,请。这是刚才您用的那种很长的笔,对吗?是。这上面的就是墨水?可我似乎站不起来莫须得心言后战去我来替你研磨你尽管画这个笔落在纸上笔迹怎么这么粗而且这个墨水只有黑色吗旁的颜色也是有的红色可以吗稍等我去取
```

### [68] hash=`30e442bef4d674df`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p26`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（09【街市狂澜】中配）

```text
如此甚好,有这画像,我们仅可以通缉羽人了,小娘子沉默不语,可是还有其他顾虑。您先前提到执子有一位已经离开的工作人员,或者说执礼。您说那位执礼曾经见到了羽人和他带来的动物,那也许他今天也会来,如果他带着我们同伴变成的那些班纹马。意味着前任执礼目击的羽人与你们所见却为同一人那么或许两位应去一趟执祠我修书一封老两位带去执祠交与现在的执礼曲娘若是真有羽人来过你们也好接手那些被她带来的动物假使没来两位也能将姓转交请新任执礼多多留意曲娘是个热心的孩子此刻约莫正在致辞两位自去寻他便是如果这样一直推挤着彼此前进就太慢了女士我们能不能从房屋与房屋之间穿过去当然如果能问到更快的路径会更好小心抱歉我们急着赶路您还好吗无妨不过刘威科碰罢了两位是胡人吧还从没在城中见过你这头发色似的真是漂亮现在各处都在过节摩擦是常有的不过你们这样着急是要去哪里呢我们是要去止辞原来如此可现在去止辞的路上游人却是太多了或许两位能从别的路过去
```

### [69] hash=`82cb1bbe77616eef`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p26`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（09【街市狂澜】中配）

```text
那是天呐竹叶怎么会白日里出现在大街上竹叶是什么一种魔精吗好香啊我似乎闻到了一股酒香味主爷好大的一股酒味主位这夜白日月市乃喜一照夜不要惊慌他找我们来了别思明女士小心等我歇等生好像不仅没有减瘦反而越发纷扰了被有尘土扬起的呛人气发生什么事了路上突然出现了一只被称为主业的当地神秘学动物我不知道似乎身带酒香更远处似乎是冲进来了一群生畜但我没能看清抱歉女士我们本来不该停在这里的这会儿又是谁家的年纪动物跑出来了不是体能吗应该在植子吗你这是我会在这里等你谢谢你们要不然我可真不知道该怎么办杀人第一天就出这么大的岔子体能打哪来啊早些时候在酒房没瞧见你我就在那边在植瓷里曲娘在植瓷做什么对了你又忘了原先的植礼回乡去了现在呀曲娘已是新的植礼了不不是的我只是代班我刚才清点结清动物的数量时听到了外面的动静是听到了叔叔先生的声音吧今日是他最后一脚你定是不会错过是啊我想着他可能会讲祥瑞的故事才着急出来兴许是没有关好围栏的门
```

### [70] hash=`2ffceb85efe89be0`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p26`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（09【街市狂澜】中配）

```text
总是惦记着祥瑞祥瑞的不晓得的还以为你是要写书呢也看看手掌有无擦伤若是有恙一会儿可随我去医馆取药晚些时候还要请大伙喝酒好的呀那是一定的真是谢谢你们女士请跟我来那位应该就是李正所说的执礼请您留身脚下现在地面上有些乱糟糟的我们得继续跟上去看看或许能与他搭上话先不论竹叶如何且说那地窑亦是多见此类异兽其在位日久即至七年有使者前来献宝此时乃皆凶国人样貌精奇 胸脯尖削自称从御门关外 万万里处来由鸟生来其通人言名落凤相无人引以为祥瑞特此献上人主抵谣诸臣见证皆凶使者所献宝物果真为一巨鸟其貌壮如山鸾由凤凰之姿青森红尾神貌不凡难道真的是凤凰非也非也此鸟换作灭蒙鸟云是能看古相改命貌仍亦在于是地遥甚悦不另辟山头四肢今人所见灭蒙改物硕身十足之后也您有亲眼见过灭蒙鸟吗莫急莫急灭蒙鸟生性极敬浩劫古今之人常将门前扫净盼望祥瑞其鸟停留聚集虽时不定长此一往或可见之我们朔日须得扫门人是这么个道理正是亦有人将金玉珠宝刻成灭蒙模样庄典家宅 以求平安
```

### [71] hash=`263e09f092c10ce0`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p26`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（09【街市狂澜】中配）

```text
试一试诸位仰头望具今日屋头岩上索克石叶其非石叶也其真灭蒙叶家户所在门间 亦已是此鸟即为灭蒙鸟可这个看起来像普通的鸡这看起来像松鸡也像我刚才画的巨鸟她说话的方式和语调很有韵律感像是在唱歌只可惜没有伴奏清唱似乎令这些歌词失去了一些味道如果她能变萌疏火听了燃春此急为遇这是什么声音听了爆肝天呐我差点忘了正式抱歉抱歉请让开一下我得出去这就不继续听了时辰还早着呢急着回去酿酒吗不是酿酒但也还有事呢明天一定请你们喝酒
```

### [72] hash=`1ac25f79a0d6ab2d`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p27`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中配）

```text
你们能听懂我说的话吗可不可以告诉我你们是从哪里来的请问怎么了娘子面生我们从前见过吗应该没有我们才到城里真的吗天哪欢迎你们来陪程玩她也在街上吗真不好意思一来就让你们看见这种混乱的情况我保证这只是一场意外可以想象的意外您的反应很及时避免了一场灾难的发生没有 都是我应该做的而且大家也帮了很多忙你们找我是有什么事情吗如果有什么能帮上忙的请尽管告诉我是这样的我先前听见他们叫你曲娘你是曲娘在执辞工作 是吗嗯 是的我们从李政那里过来之前才好听见了你们在街上的对话我听说他以前好像来过今天就不知道了那植辞有没有今天才先送到的动物我也不清楚今天我到植辞点锚的时候围栏里就已经有很多年节动物了真奇怪啊为什么越来越多了呢你看这几年来他们都长得差不多我不知道哪些是今天送到的清点的时候也很麻烦经常忘记自己刚才数到哪里了如果我识字就好了能写下来就不会算错我们的同伴就变成了这种有班闻的马是这样的我们原本是一支商队走到城外的时候
```

### [73] hash=`1eb8a510b5621493`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p27`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中配）

```text
同伴被变成了马还被一只巨鸟带走了李政告诉我们那只巨鸟很可能就是他们正在追寻的羽人而他曾经在植瓷附近触摸过所以我们想来植瓷寻求帮助那应该不是马但是怎么可能呢你的意思好像是说羽人能把人变成变成马我不明白难道因为他是祥瑞就会有这样的能力吗我们刚刚也在说书先生那儿听到了关于祥瑞的故事祥瑞听起来确实很像具有地狱特征的保护神什么神我只知道摄提神是的摄提神这应该才是你们供奉的东西猜祥瑞应该更类似一种本地的信仰传奇的神秘学家之类的这里神秘术的使用听起来相当常见或许神秘学家也一样不过既然说到这里你能告诉我摄体神究竟是什么吗我只知道摄体神有十二还是十三月的样子但那些名字很多我都不认识我知道今年是摄体神直徐的生辰年我们会请很多的年节动物去断桥供奉他走集合月桥是最有趣的我们会带着年节动物去到悬崖上的断桥前一起数着步数摆动身子像跳舞一样最后再尝试跳过去跳过悬崖上的断桥这听起来不仅危险而且还相当地耳熟步步跳不过去的还没听说有谁能跳过去呢
```

### [74] hash=`16f839d63ca4808e`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p27`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中配）

```text
连最厉害的山羊都跳不过去更别说人了我们还会提前用神秘术进行保护否则真的有人或者动物掉下去山谷很深掉下去就再也回不来了真有意思那些提前的神秘术设置都是由什么人负责的就是植瓷负责的植瓷是负责管理配成神秘术事物的地方啊不过我并不负责那些我只是新来的在上任植瓷回乡后暂时兼任这个工作而已他们跟我说我只需要这几天把侄子照看好就可以了所以简单来说您是开门的我不是我不站在门口呀我也有其他事要做的比如我还要安抚那些被爆肝声音吓到的人有一种被神秘术加强过的爆肝声音很大的比刚才茶馆外面的动静都还要大很多请您原谅他并不是对你有恶意只是我们来自北方说话都会直率一些没关系 没关系我能感觉到他只是有点着急当现在着急也没用呀就像野猪上树也不是说会就会的哦 或者你们能从这些马里面认出来哪些是你们的同伴吗我看看这里有一 二 三三只半温马来 你们也瞧瞧我认不出来当时太匆忙了我不记得样貌的差别而且也许这几只都是也还差了两只你们的同伴比三个还多
```

### [75] hash=`720715cf0d23b2dc`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p27`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（10【异乡人关怀】中配）

```text
三加二这样吧我们先等等李政那边的消息对了小叶尼赛李政不是给了我们一封书信吗我差点忘记了群娘小姐请你看看这个也许里面有关于羽人的线索家高为蓝早些放班回酒坊什么跟什么呀这些都跟羽人有什么关系别担心这几天我会帮你们多多留意新来的马的一旦有什么好消息李政一定会转告你们谢谢您的好意不过我们今日才入城还没有找到住的地方要怎么才能让李政知道我们在哪里呢?哦,这样啊,你们可以住在我的酒坊里。刚才忘了和你们介绍了,我正在经营一家酒坊。而且,生意还挺不错的。酒坊就在离植瓷两方距离的金市中,李政会知道的。我还可以顺路把这些家伙都送回植瓷。你们也去看一看其他的年节动物吧。我三床这太好了也不必在外面摸索到天黑了是啊不过等晚些入夜了街市上会更好看露朔节有金灯和亭梁照得天上和地上都亮堂堂在晚上感觉什么都是特别亮的
```

### [76] hash=`cd7a34198868ca67`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p28`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中配）

```text
女士,您觉得白天娶娘说的有可能是锁桥必应吗?越过断桥就像越过悬崖攀爬高山就像商人们说的那样一个不可能达成的条件一种绝对的代价你们是在说城外的断桥吗?不好意思,大堂里的座椅都还没擦洗也委屈你们先坐在这里没关系,谢谢您的收留关于我们刚才说的那座断桥您知道些什么吗断桥嘛反正在我到城里的时候就已经断掉很久了在它下面是高高的悬崖对面是一个叫冤庙的地方但被雾气遮盖了所以我也不知道那个庙是不是真的存在冤庙是说在冤庙里你能和直徐对话有什么问题你虔诚地问他他就会回答他们管这叫什么来着好像是问补而且据说那里的雾气有些奇异,不能久留,否则会让人昏迷,或者变得过于兴奋,我是没有见过的,就算会这样,以前的人们都还是会去月庙,就说明问卜确实有效呀,在桥被洪水冲断之后,可就再也没有这样的好事了。是有些奇怪按理说如果最开始这座桥能修建起来那就没有道理不能重建这个我知道是因为水变少了人们不能游过去到对岸也没办法跳过去因为山河山之间的悬崖很高很危险
```

### [77] hash=`4a2cd582db016da8`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p28`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中配）

```text
人跳不过去不过如果能成为新的祥瑞或许就能跳过去了他们是很厉害的八面威风还能守护一方为众人排忧解难什么事情都能做到没关系明天明天我们再去执辞看看那些班温嘛我和你们一起去现在就先歇歇吧我在楼上收拾出了房间这里呢还有著名的啄酒能帮你们睡个好觉来些吧抱歉曲娘小姐我不喝酒Besmeyer女士也不喝酒为什么要叫我小姐小姐水的话要等一下水缸在院子另一头,我去打。那我自己去,不用麻烦你。晚上水缸那边没有点灯,还要过一条小溪,我怕你找不着地方。今天在植瓷看到的那些班纹马,花色众多,完全难以分辨。明天还要早起,您喝些水再去休息吧。其实我不渴,只是累了,那我扶您去休息。圆圆的,我瞧你们不见,还以为都歇去了呢抱歉,S.Mill女士太累了,所以,谢谢你帮助我们这些话就不必说了,呢,这是你要的水这个杯子怎么了?它看起来很昂贵哦,这是别人给我的,我不知道它贵不贵,但它很漂亮,是吧?是的,它很漂亮上面画的是鹿鼠,一种祥瑞,它好雄伟的,尾宗就像傍晚的云霞一样,我很喜欢它,也希望你会喜欢。
```

### [78] hash=`d0cb66cf6a4b2f0d`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p28`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中配）

```text
是很威风,仔细看,它和池子里那些斑纹马还有点相近,或许因为都是马一样的动物吧。但大家还是觉得它们是马,不是吗?当然了,我想他们应该是配成特有的物种,这很有意思,对我们的封屋记录很有帮助他去睡了,那这杯就只好归我了你的杯子里很香,这个就是你说的助眠酒吗?这就是普通的酌酒听起来在你们这里,酒有很多的分类当然呀,酒有很多不同的,有浊酒、清酒、药酒、鹿酒哎,好多好多,著名酒就是一种加了三藻人的药酒我还以为酒就只是酒而已,至少在我们那里没有这么多的分别好吧,其实我也不明白,为什么酒有这么多不同的名字,却都还是酒如果是因为它们颜色不同,那我换了一件颜色不一样的衣服,我就不叫曲娘了吗?没错,如果你的同伴变成了马,或者别的什么颜色的动物,那就不是你的同伴了吗?不是那样的,他们当然,其实我很担心,或者说,不仅仅是担忧,我不知道你看起来,真的很想念你的同伴想念?不会这样描述这种心情,我只是认为他们会变成动物都是由于我指错了方向,如果他们再也变不回来了,那我觉得不会这样的,事情一定不会变得
```

### [79] hash=`51620b16942a41a8`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p28`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（11【廊下夜话】中配）

```text
更糟糕,我觉得一定会有办法的。就像天空出现彩色的云朵,池水变得如纯酒般干美一样,天地之间还有许多吉祥的征兆没有显现,你想想,也许月庙是真的呢,也许,也许会有别的办法让你能认出你的同伴,而且,就算雨人不是祥瑞,这城里却还有别的祥瑞,总之,谢谢你,曲娘小姐,曲娘,我明白这有什么,我一定会帮你们的我口袋里还有一些甘酸枣仁你快把水喝掉,我去给你泡三枣水,也有助眠效果
```

### [80] hash=`f46fafd0cd55c0c0`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p29`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中配）

```text
下楼后,穿过主厅娘在哪儿?你如此泪弱你是偷走我们马匹的羽人罢了,也须得与我走怎么回事?静声,此地危险,多说无益他家不是让你们拆家你们要请谁喝?昨天来的两位还在楼上睡着呀他来过了,他来做什么?他都不是祥瑞,也没有再做好事不许你们请他喝酒要让我见到他,我一定……等等,谁被他带走了?他色和酱色?什么颜色?我怎么越听越糊涂了?下次我一定给你们多做一张嘴你看看,这都是在说什么呀?请小心一些来,我扶你谢谢,谢谢你小耶尼赛,她不在楼上,也不在院子里吗?是你红头发的朋友吗?我没看见他,他是不是先出门了?不会的,他如果要出门去,一定会告诉我或者至少通过您告诉我您真的没有见到他吗?没有,早上真的没有呀城里的失踪案,是不是也都是这样的情况?我,我不知道,李政没有和我讲过只是如果,这就是所谓的失踪案那也一定会留下什么蛛丝马迹请您帮忙看一看院子里有没有留下什么东西它不是在二楼被掠走的否则我不会一点声音也没听见你先别急
```

### [81] hash=`d23556b2f76e6cee`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p29`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（12【倾杯舞】中配）

```text
我们可以去找李正等等怎么了神秘术这院子里有使用过神秘术的痕迹跟着我你要去哪你看不见呀你告诉我我带你去请跟着我就好往前走就是水缸了昨晚我来这里打过水就在水缸的附近我能很清晰地感受到这是那就对了李正说羽人也拿着像骨头的树帐而小燕尼塞看见巨鸟也有这样的东西我就知道这下我们有证据了我们可以而且小燕尼塞失踪了为什么我觉得这就够了呀羽人的骨帐都掉在这里了这说明他来过,而且你的同伴不见了,那不就说明是他干的吗?但只有小燕妮赛现将亲眼看见了巨鸟,巨鸟的画像也是他提供的我们依然无法证明巨鸟与羽人就是同一人我听不懂,是说就算我们找到了他的骨头,也不能用这个证明任何东西吗?但是,我觉得不需要想这么多就是,就是这个证据够不够,能不能证明,不是我们说了算的嗯,我也不懂,但感觉这样不对我只是觉得,我们应该做些什么,因为你很难过你说的对我们先去直辞吧,今天李正也会在,他要跟我说些杜硕捷的事我们正好可以告诉他,李正会有办法的
```

### [82] hash=`dff8f820df789e1d`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p2`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（02【柔板】）

```text
So, are we on the same page?I fully understand where you're coming from.And I acknowledge your reasoning.What are you trying to...But we still need a vote to decide.Wait.No problem, of course.It's the civilized way to solve it.But I require we skip the speech.We have no time to waste on your monologue.Madam!Alright, gentlemen.If you agree to go back, please, raise your hand.What about Mr.Urien?He has not voted yet, so the vote is not over.
```

### [83] hash=`ce5470e5a9936654`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p2`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（02【柔板】）

```text
Oh, he's too tired to show up.But I'm sure he shares the same idea with us, because...We are all humans.Of course he's on our side.Say no more, Krolic.Pack your things.Let's head back.Fine.We'll split up from here, then.We'll take all the supplies with us, or we can't make our way back.No discussion.Gentlemen, the team was put together in good faith.Perhaps we should negotiate, not...The compass doesn't work here.
```

### [84] hash=`03c53995878dbf92`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p2`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（02【柔板】）

```text
You need me to find the way back.Leave our supplies, and I'll show you the way.You have to do this the hard way.That, my friends, is not how civilized people solve their problem.Mr.Jurian.Mr.Jurian.Mr.Krolik, I thought you were here to discuss the reallocation of supplies with Madame Bessemer.I didn't expect this.Well...It's true that you didn't choose to be here.You are here because you have an important mission given by the Governor to complete.
```

### [85] hash=`f4c878f42c32956d`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p2`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（02【柔板】）

```text
We have come this far.Do you really want to give up now?As for you gentlemen, Petrov surprised you here too.It's a risk that none of us expected, but it shouldn't have broken your will.I remember you showed a great interest in those ancient strata in the south when wewere at the speech.All we need is safety.There will always be a buffer period after extreme weather.We should seize the chance and head back.
```

### [86] hash=`500daa1693cf61c7`

- lang：`en`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p2`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（02【柔板】）

```text
I believe that refers to the highest mountain and deepest canyon in those stories.I reckon so.But Mr.Jurian, as a human historian studying the arcane skill, believes it's a form of exchange that arcanists make with nature.Mm-hmm.And you think he's wrong?At this stage we can't verify anything, so all these assumptions will have to remain assumptions.
```

### [87] hash=`5c8196a31aa1557e`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p30`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（13【葛生】中配）

```text
本草姬与月桥所用年节动物皆不超过三只,一牛一羊一驴,未有例外。收成玉刹,城内少有可用的青壮成驴,以至于用马代替。可现今即使庆贺只需生辰,池子之内的年节动物也过多了,其中还有为人所变,断不可一视同仁。若要取消月桥之疑,岁除后便是朔日,须得尽早决断,必要。人生是在这年节关头,烦扰从来都借种而至。你便是掌事之人,可上次我所见的明明是另一人。我有要事相告,若是再不阻止,万事修矣。我乃葛天,此行事为告知,那九方娘子以术法使人变为露树形貌,须得尽快阻止,以免遗憾更广。她骨相过轻,形状尚在生长,也因此作为不定,恐为祸患。你指的难道是曲娘?正是。古相,难道,你是可视古相的黎山母,但你的身形分明不似黎山老母?我自然并非黎山母。那这些言辞从你口中说来,岂不无人相信?你还不若声称自己是黎山母?而且,黎山母啊,且看看周围吧。你说的是这些门间,人面,鸟声,红尾,你们画这些,我并非祥瑞,此类筹措或祈祷毫无必要。这些并非向祥瑞祈愿的门间,而是你的通缉令。
```

### [88] hash=`c83d53faaca6bf37`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p30`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（13【葛生】中配）

```text
无论如何,现在捉拿曲娘最为要紧,正是她造成了城中的这些失踪案件。我还猜想,你是前来自首或交涉,如今看来,却是我想多了,主动前来攀摇娶娘,你是全然不知,自己才是头号一贩呐。这与我何干?我们数次收到人口失踪上报,次次与你现身于城内,挟动我来到执辞的十日关联。这是污蔑,当时那位执理应知晓我的来意。当我们赶往之辞时,你早已只身离去,不见踪影。无人为他作证,他自是被法曹视为胡言乱语,现已回乡聚宴。若非此事突然,我本就不会来到城中,自然没有久留的道理。况且,咽下神秘术随性示威的苦果,本应是值辞之责。你伶牙俐齿昨日正有两位胡商来到佩城向我们提供了一些线索而这些线索都指向你正是那两位胡人你认罪了?这是我此行要告知你的另一件事那两人其中之一线下就在此处他可以向你解释你说他是谁?稍待请看着茶水泼过的地方到你坐下再向你奉茶不是为何你立行仙前那样是说神秘术啊还是说须得干净的水才行河水不结应当没有这样的限制你之前究竟是怎样做到的
```

### [89] hash=`3e20a349281f0558`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p30`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（13【葛生】中配）

```text
将它拿下你这是何意疑犯因此我所知已倾书相告你们不去捉拿曲娘反而在这里纠缠于我找干净的水来我再证明给你不守旧情即可我不会同意你动手你抓不得我保护那红尾的马那可能是受害者力气总会耗尽的何须走到这一步仅仅找来青蛇与我我就能向你证明曲娘的过错我又如何知道你的证明不是你用神秘术伪造的结果呢说到底我们了解你指认的罪魁曲娘却对你一无所知甚至于在城内有人失踪前,你都未曾入过沛城。我们又要从何处判断你的话语,真实与否。更何况,你说自己并非祥瑞。的确,我并非祥瑞。此前,也从未来到城中。因为我本就不愿下山。你却还是做了这样的事。为何我一定要来到人世当中呢?你这话是什么意思?我的那些同族都已下过山了。为了你们,放弃性命,放弃族人,放弃性命,放弃一切,成为一个符号,一个图腾,变得谁也不是。羽人,你究竟在说什么?我告知过可以怎样称呼我,羽人并非我的名字。眼前羽人或许非我族类,并无以名相称之必须。原来儿等却乎忘忆,忘了过去那些下山的葛田氏,

异层是建城之人,铸桥之人,抵御洪水之人,只记得一个久不存在,从未回应的社提神。所以我不愿,不愿下山,不愿相处之后,却又这样被猜忌或忘却。你究竟是谁?现今看来,桥段,乃是必然,已如在我之后,再无可填。桥段?你与段桥又有何关联?语人,你说清楚!就这样吧,你们尽可以来请住我了。薛娘小姐!
```

### [90] hash=`e8f095a465b3602a`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p31`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】中配.）

```text
什么?刚才跑出去的是什么?那东西还带走了和我一起来的那位娘子现在我们又失去了一名证人难道这也在你的计划之中?我的数账昨日便已遗落在她的酒房你一问便知娶娘是这样吗?在院子里是发现了一根骨头但那东西现在正在被掳走的胡人娘子身上先把她捆起来你还有什么要说的?该说的,我都已说了。若再不制止,便是真的祥瑞来了,也无力回天。你究竟为何执着于指认曲娘为凶手?凶手?我是什么凶手?曲娘,无妨。我们都知道你与失踪案无关。而且他还说什么,什么真祥瑞也没办法。但他才是假的!曲娘,不必激动。现下只能暂且将她关押在植瓷我自去告知法曹现在要紧的是派人去追回马和那位胡人娘子须得找到她的书章才可溯源把她也带下去吧其他人都散了徐娘你随我来我有事与你商议羽然你到底想做什么徐娘你明明看上去就像祥瑞为什么要说这样的话?而且,就算你不是祥瑞,你难道,难道不怕,不怕真的祥瑞降责于你吗?许娘,许致她早前未与我们有所接触,的确并非此地祥瑞,城中也已是庇护久矣。
```

### [91] hash=`d2d37840eae9b2d8`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p31`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】中配.）

```text
山上的雨人就是祥瑞,但那是她的样貌,就能让旁的人觉得她是祥瑞。池里离开前跟我说过,羽人长得像钩芒,就像画册里走出来的一样。好像这能解释一切,可是画在书上的祥瑞啊。曲娘。但她当然不是祥瑞了,不像钩芒,或者面蒙鸟。她连……绝技艺,无形地难的道理都不明白。绝技艺,无形地难。道理确实如此,只要做错了事,必然会留下痕迹。即使他试图嫁祸于你,我们在尚未找到数账和证人之前,也不能轻易假定他为凶手。我们还没有找到足够确证的痕迹取娘。羽人,什么叫做真的祥瑞?你知道他在哪里,你又为什么要带走别人的同伴,却来这里指认我?这样的形貌,是天道赋予的。就不应该因为自身的好物得失,而偏离了这形貌应有的本性。明明可以变得像叔叔先生说的,像画册上画的那样好,那样受人们喜爱,就像大家所期望的那样。你把胡人小娘子和他的同伴带走的时候,都没有考虑过人们的心情,不是他们想要分离的时刻。你令人伤心了,这不是祥瑞该做的事。好了,曲娘,就到这里吧,你们先把她带下去。
```

### [92] hash=`045332b4e3785e28`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p31`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】中配.）

```text
她也什么都没有告诉我,大家都是一样的。虽然,我知晓你一直以来都对祥瑞十分着迷,但语人今日来到执词,言语中已经透露了他实则并非祥瑞的事实。甚至,我以为他的态度更像是说他自身并非祥瑞,也从未想过要成为祥瑞。我不明,他怎么能不想呢?并非人人都对祥瑞的传说如此趋之若误臣的确曾在祥瑞的庇护下有过不错的时光但此去今年那段旧日只能在神话典籍中查阅甚至我也不敢论断真正的祥瑞是否还存在曲娘你应该知道现在我们也已不需要祥瑞了不需要吗现在没有祥瑞甚至也没有了行之有效的问补但你看我们失去了与渊妙的沟通城中依然秩序井然杜说节也依然热闹非凡可见祥瑞并不是一成立足之必须这样吗今日看来原来你是识字的你知道我不会写字的 李政绝技易 无形地难不是的,我只是听道士说过太多次,所以记住了哪位道士?是城中的道人吗?是我来到城里之前,曾经与一个道士同行过一段时日他会重复一些话,我总是听不明白,但心里牢牢地记着听起来,你曾有一位闲师,毕竟你入城以后,一向与人为善
```

### [93] hash=`a5e7b10e338bbc2c`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p31`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】中配.）

```text
走上了一条与葛天不同的道路原来他叫葛天?是啊,葛天但你刚才还是同他说的太多了他并不是你一直在寻找心中所向往的祥瑞真正的祥瑞不会毫无理由做出这样冒犯的事他或许只是一个九居山上的大妖究竟为什么要指认我呢?我不明白,是我做错了什么吗?可以想见,因为你是直理。人人之理,已因她之故回乡去了。她见此法奏效,或是想要故技重施。况且,今日她闯入执词时,见我似乎相当惊讶。由此不难推断一二。还有那被掳走的胡人娘子,她……放下心吧,你派人出去搜寻了。我们现在也该去商定一下明早走击与月桥的事项月桥?是的,还有这件事要是断桥能够修复就好了就不用年节动物,也不用跳桥了刚才我问葛天,可是他什么都不回答的时候我就在想,如果我能直接问直徐呢?去渊庙?如果是真正的问博那我想了解的事情,也一定会有答案吧?是啊,事情就是这样。葛天线下暂时收押在执祠地牢,曲娘也还在那边。两个时辰前,我与直理曲娘商议后,决定保留走击与月桥的仪式。只是那些生有异色的动物确实不便再用,规模相较以往直徐直年有所缩减。
```

### [94] hash=`afc49ac4246e1ebc`

- lang：`zh`｜version：`1.6`｜arc：`朔日手记`
- doc：`BV1o5411v7Ci_p31`
- title：《重返未来：1999》1.6版本「朔日手记」全剧情 - Reverse: 1999｜4K（14【往日鎏金】中配.）

```text
此为人员名录与各类筹措明细,我令人摸血了几份,已经送到各方去了。您辛苦。应当的,还有葛天一事,按照法规,须得杜硕节后再升堂会审。我还有一问,证据追回来了没有?尚未追回,越走胡人娘子的红尾马居,大抵还是受了葛天的控制。等我们的人追到郊外已经在雨中消失得无影无踪城市郊外急雨 行路困难可以理解只能等此次雨停后再行搜索了不过一马居邪一盲眼女子应当走不出太远待到雨停我会亲自带队前去劳烦法曹分内侍罢了纸礼呢法曹是问娶娘还是先前的那位回乡的那位大概须得等到渡说节后才有消息我尚未收到她的回信曲娘毕竟年轻在回向那位执理传来消息之前还须得您多多看着执辞些她足够良善也正因此我才会向执辞贸然举荐若曲娘形势出了差池自然也是我的责任话虽如此年节事项繁多难免有所疏漏也不必太过苛责。正是,若你寻回了证据和那两位胡商,也劳烦派人知会一声。稍待,还有一事,是今夜岁厨宴。法曹若是愿意,可携亲卷来曲娘的酒坊度过。那可是今室街坊都去?

是啊,他宴请相邻,理由也不难猜。岁厨守夜,反过年去便是杜硕节的第一天。往年酒坊也是奢宴的我日明年是啊,新的一年又是知徐生辰希望供奉著知徐的渊庙,亦能传来好消息
```

