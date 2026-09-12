# 剧情图谱抽取 · batch 106

- 角色：`wu_ming_zhe`
- 批次：**106**（未缓存补漏批 7/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_106.jsonl`

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

### [0] hash=`e03288e1a0bed940`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
I don't mean to judge your decision.It may be understandable in some cases.But if this threat is not just a prank, if it's serious, am I sensing disapproval?There has been an increase in patients coming from Chinatown showing signs of mental instability.Their symptoms include confusion, amnesia, drowsiness, and volatile anger.None of the patients seem to have anything in common.No prior history, all without clear cause.
```

### [1] hash=`fb3392cefb68c647`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
Does that sound familiar?Sorry, is this leading somewhere?A case, 8 years ago.He Rijun, the scriptwriter for your first big hit, Detective CO7.She burned to death in her own house.However, the cleaners found a fume rail in the debris,surprising the intact after the fire.Strange, isn't it?Every other item was burnt to ash.Yet this one 8mm reel was as good as new.The cleaners felt the same way.So being curious, they played the reel.
```

### [2] hash=`c9863b6e0dd89bad`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
Three of the five who watched it ended up in an asylum.One jumped from a building, and the last, according to the report, became like an emptyshell of the person.And what's happening here reminds you of that.There are some commonalities between the cases.I can't ignore the possibility that they are related.Two in particular stand out to me.The similar symptoms of those affected.And you, hard to shake the thought that these are not coincidences.
```

### [3] hash=`4626e135ca8846fb`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
What are the police still here for?Are we gonna get back to Finland?Who knows?But it doesn't seem good.We are losing light here.Can these guys wrap it up already?Is that an accusation?No, not at all.I'm just hoping you might be able to shed some light on our case.After our initial investigation, we officially recorded it as a nominous Arcanum incidentand determined that the cause with the 8mm film reel, which contained the film titled
```

### [4] hash=`75c3dfde74a1dde7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
Reunion of the Three Swallows.To this day however, the exact nature of the Arcanum hasn't been conclusively determined.We still aren't sure why it has this strange effect on people's minds, nor why the damageappears to be irreversible.Perhaps more importantly, we still don't know the origin behind the Arcanum on thereal.There are many possible causes that might create such an effect.One of the most common thought is from absorbing powerful emotions from an Arcanist.
```

### [5] hash=`4eda52c344c55a4b`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
The darkest emotions possess the strongest power, anger, hatred, emotions so strong that they can outlast their barest death,like a curse from beyond the grave carrying out their last will as an obsession.And in such cases, these objects are sure to lead to disaster.I believe that this film is, undoubtedly, one such cursed item.If it is the case that this film was involved in these new incidents,then we must find out what obsession is carrying out and find a countermeasure.
```

### [6] hash=`9a6054da6d3bc8b8`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
I assume you're already on the case.Indeed, I am, Ms.Noah.I've been studying the report on the original case,including some of the theories of the original investigator.One of those theories suggests that, despite your collaboration on the CO7 series,There were many points of conflict between you and Ms.He.In fact, the reports mentioned you had a violent quarrel with her on the day of the fire.There was even a question about whether you might have been responsible for her death.
```

### [7] hash=`1458e6ddb1c9eafc`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
So as you can see, I have more than a strong reason to believe you are connected.And if this cursed reel is behind these recent incidents, I'm afraid that yoube the intended target of this curse.
```

### [8] hash=`cd423431a4dfad0d`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p8`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（08【餐后审问室】）

```text
可恶的同僚谁能猜得到那位著名的导演会是她自己的现实剧集跟她聊天后我们还是没什么好聊的我看不懂她的笑容但如果你的小说真的有道理那战争就在危险之中所以为什么不聊她不担心她自己的生活吗是吗原来对面杂货店哪家的女儿也就是了最近都不知道搞什么好多建峰家里都出了事姥姥家还算好嘞她带着女儿去看中医抓了药吃了一段时间就好了不少当时对面街口马仔她阿妈就麻烦了那个阿婆原本就身体不好忽然间又变得疯疯癫癫他们两公婆都担心死了之前都有个良媒来问这件事说什么事情不太对路我说呀就是临近年关那些污浊的东西都出来了您说还有人打听过这件事那是什么人他说自己是什么新科学新科学什么鬼事物所的好像是个神婆刚来到唐人街这一带的他还给了我一张卡片你的怪也不麻了不过不知道被我放到哪里去原来如此多谢你那么有任何进展吗我有些坏消息首先我们期望有更多的犯人第二我们并不是唯一的发现了我们必须赶快如果我们不想让这宗案件吸引更多人的注意那我们怎么不开始
```

### [9] hash=`be66ea87d5bb2b83`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p8`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（08【餐后审问室】）

```text
与指导人合作呢她似乎是我们的最佳指导人我找到了一个人她的案件与这个人有关系就像你刚才说的太多的偶遇不能深入思考那名写作者她是什么人贺 瑞珠莹她是个艺术家 对吧没想到她会把那部电影带来她最后一部分的恨恨我看过很多这样的案件坏东西太奇怪了可能是她把诺瓦追赶到这里但没有证据证明诺瓦和贺之间有合作等一等,你不是在其他视频中写了这份报告吗?可能是发型而已,但那是一件事不仅是那件事,还有这个我自己做了一些探索那天清洁员走过那层楼是那天Nu'ar在车上遇到的那一晚让她的腿受伤变得更神奇根据报告,他们在每个时辰之间发生了发生在建筑物里,是不少于一楼的距离从遇到的场景来的那是什么证据呢?我们DAA的指挥官有个说法当它来到Arcanum的时候就没有什么像是个伪证无论是伪证还是不伪并不是太多了我们需要证据当然我们不能只走到证据上但当它来到Arcanum的时候你必须要跟着你的指挥So keep your nose to the ground.
```

### [10] hash=`e17ebf11fbbf74d3`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p8`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（08【餐后审问室】）

```text
I get you.This isn't just about evidence.You don't want to point the finger at someone you admire.But you've got to pursue this.Even if that means you have to separate the artists from their work.Actually,there is another reason that I'm not entirely convinced thatMiss Noah,the film incident,and the events in Chinatown are connected.In fact,it's quite a substantial reason.如果我们的记录是正确的那些被诛逼的纸巾是被本地公司
```

### [11] hash=`ae8e35326ded340c`

- lang：`other`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p8`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（08【餐后审问室】）

```text
六个月后发生的这意味着除非一件严重的事情发生了那些纸巾应该继续保存在本地公司里对不起 对不起如果我记得对你之前提到你昨天看到本地公司的人显得很奇怪是的September 1990, after the tenth storm, a female Arcanist committed a serious assault and caused a number of casualties.She had appeared at an illegal gathering held by the Order of Enlightenment, a subordinate organization of Manes Vindicte.The timekeeper encountered her and confirmed her identity.Anjo Nala, a Beyond Arcanist.
```

### [12] hash=`66ce67a5cb1dfb5c`

- lang：`other`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p8`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（08【餐后审问室】）

```text
Born sometime in the 19th century, she was sealed inside a wind-up toy in the year 1968.Since then she has become a lethal weapon that must obey whoever possesses her toy.But back in 1985, I mean the real 1985, that toy had been safely stored in an Arcanum containment department as a dangerous item.Until it was stolen.You were involved in that particular inventory check.4个更新的物品已经被淘汰了在最后一波的情况下和那些严重的武器
```

### [13] hash=`ed4e1e73a265c575`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p8`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（08【餐后审问室】）

```text
把整个组织变成了弥漫然而,我们部门最重要的任务却失败了幸运的是我们被弥漫的任务却成功了你和你的伙伴刚才说的在中国城市中有很多奇怪的事发生对吧我的任务是捕捉Lathem,并取得她所抢抢抢的所有蓝色物体,并且为他们造成更多损失。但我估计已经太晚了。那你所说的是……是的,你提到的那些偷偷的物品是被你提到的那些偷偷的物品你也说了你有些信息关于它们的现代存在我被说要用严格的秘密去处理但是在这个时候他们的取消越快越好所以我们一起努力吧她的主角是Latham一个醒来的奥奇利人我没办法相信她会做到的我们是朋友和亲密友我曾经叫她Loggerhead因为我知道她是最遗憾的人但我最初不相信她可以做这种事我还不明白为什么她不是那种很生气的人但警察已经查清楚了警察不是那种会犯错的人你已经在这里几天了对吧你有没有说她在哪里对不起我没有真可惜
```

### [14] hash=`f0e9b794d25f73f9`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
Have a good day!actually heavily protected by Arkin Rituals.According to Ms.Scott, Latham acted alone.But there's nothing in her file that would suggest she's capable of that.Her Arkin skill level is frankly far from remarkable.Even with insider knowledge, I don't believe it's possible she could have bypassedthe security system and escaped on her own.Either Ms.Latham has planned the foundation for fools, or she has more powerful accomplices.
```

### [15] hash=`a2cf70a28049201e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
There were no warnings or notices on her employee records.You mean she's not actually wanted?No, I don't think so.Ms.Scott said that their department wanted to solve this problem in secret.So I thought I might explain the reason Ms.Latham's warrant wasn't on her file.However, when I tried to access more of their records to double-check my findings,I ran into a block on Ms.Scott's records.Access denied.
```

### [16] hash=`6bd65c302db5eee6`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
I've had permission to view this information.If you need access, please contact your supervisor.It could just be because I'm only a cadet.There are some files that I don't have access to yet.I contacted my supervisor, but I haven't heard anything back.I don't mean to distrust her, but I can't hold anyone above suspicion.And what about me?You're putting a lot of trust in me, Liang.Yes, the first day we were on duty together, you said you need to know what makes me tick.
```

### [17] hash=`9662647cef87af2b`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
I did, didn't I?I've reconsidered it, and you're right.During my training as a visual, our instructor emphasized many times that trusting our partner was of vital importance.And you, Miss Boydie, have proven to be capable, decisive, and compassionate.I have developed a deep respect for your work.We shared the same goal, to discover the truth behind the incidents happening in Chinatown.I can't think of any reason why I shouldn't cooperate with you.
```

### [18] hash=`3f3f04e4bbb4ee0c`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
Alright, alright, alright.Enough!I'm flushing already.Damn girl, I didn't expect my meek little mouse to turn into this.This what?Forget it.You've made your point, now stop it.But you kinda missed my point.I'm worrying that the Foundation is going to punish you for leaking classified information.Won't you get in trouble?Though I may be a vigil of the Foundation,before that I am the descendant of the Liang family.
```

### [19] hash=`f8febe02edddc2c7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
I'm obliged to do all that is necessary to fulfill my destiny.And given the circumstances,I think providing all relevant information that might assist usin catching the thief and retrieving the threatening or king objectsLet me see.There it is.I almost went too far again.Now the key card.Where did I put it?Oh, here.Home sweet home.Oh, I'm exhausted.Latham, right?It's been a while.We have some questions for you.
```

### [20] hash=`a989dc731c249440`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p9`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（09【没头脑嘉宾】）

```text
Please try to cooperate.Tell you everything.It was me, okay?They said I stole those arcane objects and sold them for money.Well, maybe I did- Ouch!What do you mean, maybe?because actually I can't remember it I can't find my memory film for that timeso really I just don't know memory film so to summarize what you just saidLatham you're an awakened piece of a movie projector which forms a Lathamloop you were designed to play movies not record them and that's why you

What do you think?
```

### [21] hash=`22d603a2c80fa0c7`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
Go!Turn on the emergency light!And go check the circuit!Copy that!What are you doing?This is not the emergency light!No, that wasn't me!The cup!The cup is missing!Flawless protection is just a disguise, while threatening is the essence.In such a dull and dreadful exhibition hall, does anyone still remember those stories full of imagination and miracles?Who are you you were repelled by Ramirez's novelty and hated their surprising imagination and
```

### [22] hash=`b1b4e16ec9e3b273`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
Miracle stories one after anotherApparently it is better to follow the rules even if we fail we'll have nothing to be blamedto bury that shining star the peers jointly forged a rim it come andCarefully schemed a security commission that was doomed to failBullets you are a thief.You're not going to the famousWell, it's not surprising to tell you that some of the equipment carried by the robots have violated the guidance on security.
```

### [23] hash=`46260a5417134602`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
So, I replaced them with safer firework bullets.Sorry, but it's better to destroy the remote control that will place our security at risk as early as possible, okay?Look at that dog!No, not that one.Look at Walter Collie.He found us the Rimmick Cup.He ran away.What's he gonna do?Of course.Iverson looks as if he's just swallowed a whole slug slime.Eventually, he's lost to the Arcanist imagination.Those journalists who are not in the plan will definitely not miss the big news.
```

### [24] hash=`91103049920bb6b1`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
It's all a mess here.And we are going to leave with ease now.Unnoticed.What's coming?Our kind of creature.I can't believe someone has found me.Am I exposed?no one will see you, including your puppy friends.Or this, Breeze Glider.When you open your arms, or your front legs,all it takes is a little breezeand the flying membrane will get you anywhere.Or say, are you going to give everyone a surprise too?
```

### [25] hash=`0669907b1a319248`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
Shark Alarm, it will wake up all the sleepyheads,keeping everyone wide awake.It's often used to deal withthose heavy-headed security guards.Where is that puppy?Jane this way.You'll retrieve the cup!Mind-blowing news!He will be the star!It sounds weird.You have to make your choice, my puppy.Cheers, pup!I don't know of this hero, puppy.Not exactly.I'm his friend.Best friend.Would you mind telling us how you raised such a brilliant dog?
```

### [26] hash=`ab404545afe6d3c2`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
I guess people will care about the puppy's daily life after the article's published.Well, I often enjoy the symphony with him.Sometimes we'll discuss profound philosophical issues together.Yes, we have quite an extensive collection of books at home.For example, Meditaciones de Prima Filosofia,The Republic, Rhetoric to Alexander.That's an informative first-hand material.Thanks for your cooperation, Mr.
```

### [27] hash=`a4231849ee7e0d1e`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
Owner.It's been a pleasure to be interviewed by you.Pickles, too.That's beautiful.We may have further and more detailed interviews that need your cooperation.constant stream of interviews, film shoots, and friendly matches with the England national football team will follow.I'm sure the team would also like to thank the hero who guarded the cup in person.The puppy's heroic act may even be highly appealing to film investors.
```

### [28] hash=`6ca8d2b141f446bf`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p10`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P10.真相泛滥｜选择题｜皆大欢喜）

```text
Sharing is my destiny.After an unprecedented and unexpected soap bubble surprise party,none of them left anything improvised about Utopia.Not even one of them mentioning my contribution.I'm glad to have the great honor to share this with you, wherever you are, whateveryou've been, I hope this story will bring you a moment of joy, and I am also sincerelylooking forward to your stories.
```

### [29] hash=`1b22a805c12800c3`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p11`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（以盗治盗）

```text
Do you remember this?Sure.I can now prove to you...failed.Nonsense.I know.I'm just a student.
```

### [30] hash=`c91ba42c73bca06d`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p12`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（以盗治盗2-缅因齿儿）

```text
NoFantastic Melania.Should I bite him?Wait a minute for suretelekinetic arcane skillFantastic my apologies be nervousUncle finds howeverUncle finds I'm just a businessmanMelania it will be another long nightNarnia I have no idea.I can never think as father did.I think I can do
```

### [31] hash=`ac7cbd44c161d5f6`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p13`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（以盗治盗3-水晶头骨）

```text
yes however melania say see this is a key got it miss ac father's sandbox yes howeverlook at these files miss ac however melania failed you you are right
```

### [32] hash=`7761f7687927b7ad`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p14`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（以盗治盗4-足球比赛｜尾声）

```text
Everything has been going well.Got it!Please put down the things in your hand, miss.Wait a minute.Melania.I swear on the honor of Ramirez.I will make up for my mistake.For the plan.The one with the plan in this stupid company.But I do know.So is that revenge?Unlike your father.Possible.I admit.Melania, would you like to be a thief?So...so...No Mr.Fiennes.I'm just a student.Wait a minute.I just want to see the legend of Ramirez continue.

Miss Acie.Think he would say ace?I bet he would.
```

### [33] hash=`7b6af500c8819608`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p15`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（小狗与流浪汉1）

```text
Yes, I'm terribly sorry.What sugar it feels uneasyThe puppy is asking for your opinion.He will travel farBut he feels uneasyAccepted your suggestionBut puppy hey my friend to chase its dreams to seek the source of everything
```

### [34] hash=`34f10f135540f89c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p16`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（小狗与流浪汉2）

```text
the puppy is surprised the puppy is not familiar with this puppy can't be ofhelp pickles puppy considers you as unwise heyit's confused no chance at all no way wants to leave the party to youwatching to try everyone's having dinner now sit with you together
```

### [35] hash=`0c130f1379f28869`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p17`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（昨日金杯）

```text
What the puppy wants to get rid of the current situation?Oh, no exactly the moment of excitementI justThe greatness of art.Hey my friend
```

### [36] hash=`4fe7f63d9d685c4e`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
Is that gal really coming?You really think she'd announce a plan stealing to every living person before she acts?And she even made a security plan for us?Well, I'll say, she's either a maniac or a freaking crime genius.It is mine now.Are you satisfied with the answer, Miss A.C.?One last to go, Melania.The Rimmick Cup.Now, does anyone not want to visit the Rimmick Cup?Raise your paw, please.All right, it's unanimous.
```

### [37] hash=`1069c7edaf1d99e9`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
New Humans is a robotics company doing the right course.They have never failed any mission as a security.I'm sorry, Mr.Iverson.Actually, I didn't know my entrancewould be so straightforward.Catch them!I can't believe someone has found me.Am I exposed?The puppy is asking for your help.All right, puppy, let's make a deal.Humans Company announced they'd offer another reward for the 13th International Jewelry Show.
```

### [38] hash=`b6da0eebe26b352a`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
The company claimed that the person who filches the heart of London can collect a £1 million reward at Number 15 Bond Street.Tribal news sources revealed that several people have failed and been arrested,I will pay appropriately.Sure, my generous lady.Please, sit right here to get away from the crowds.Hope you don't mind my raspy voice.London faces severe public security issues.Approval rating might drop.
```

### [39] hash=`aaa8a7036710f126`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
Café prepares for motorcycle road racing.Government failed to halt.Rock Pirate hijacks radio frequency, claiming fun is about to begin.Artistic recon street.Police warning over colourful bubbles.That will be a fantastic plot to start the story.We are here with full sincerity, Sergeant William.Certainly.You made all our headlines.Londoners know what you've done.However, your proposal for security companies in maintaining the security of London doesn't
```

### [40] hash=`73e0bcfe5e4b7677`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
conform to the principles of law enforcement.What's more, the public is still alert to security companies.You know, after the Ramirez incident, people no longer trust security companies.Ramirez?Oh Jesus, why do you compare us with an arcanist company?formulated guidance on security.This is our latest product, Security Control Type 1.It carries abundant security measures, includingtear gas, endive worm powder, magnetic interference unit,
```

### [41] hash=`eabda5e9d5c40cc3`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
and can detect any threat within a radius of five meters.Most importantly, it is fully under controland reacts to emergencies with 173 in-built programs.I think it is a reliable helping hand of our police officers.Just like now.If we switch on its sensor...Suspicious invader detected.Location right under the first office desk.The second, the third, the target is moving quickly.Is it going wrong?It never goes wrong.
```

### [42] hash=`3b0531e45ba7fe28`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
Hey, hey, gentlemen, and this very sensitive robot friend.Hello?You, again?Where's...Thompson, get in here and kick him out right now.Wait, wait, I just want to talk to you about the watering car, look.I've told you a hundred times, nobody ever cares about those god-knows-what-pop elements.Pop, yes, pop, you just spoke it out.Currently, Pop is still too avant-garde, so I'm very glad to meet someone with the same taste.
```

### [43] hash=`c644557311c2c850`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
That's because you've tediously repeated it for ages!So you can understand our philosophy, and I believe others will...I get it.This is a malicious rule-breaker.Such kind of violation can be tackled with by the security plan installed in our robot.Sergeant William, here is another reason why London needs our robot.Puppies are friendly, lovely, and they can read your mind.Oh, such a lame idea.Some people don't like those plushy quadrupeds.
```

### [44] hash=`f1419a22a658aefa`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
It's so difficult to get their hair off our nose and clothes.And their smell stinks.Sergeant, now I will present you Security Control Type 1, Moralization.It has an all-round precaution plan installed for all citizens.and of course it knows how to cope with you, hooligans.it doesn't rely on some impalpable imagination?totally controllable?for sure.hey!malfunctioning, you iron monster?keep away from me!
```

### [45] hash=`e7d9017c70957f67`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
what's in your hand?put- put it down!that's rude!we want peace, not war!as you've seen, sergeant william, our robot excelled.London is utopian.I will throw a feast for more people to have fun.By then, our philosophy will hit the headlines of all newspapers and become a new tidal trend.Everyone will get to know and fall in love.Really?But we only receive countless complaints.About you particularly.
```

### [46] hash=`c6d6ecd30664c127`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p1`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P1.领衔的人们）

```text
But people just need some time to digest.London has been in chaos for too long.We need to thoroughly and completely root out all dangers and threats.I'm in total agreement, Mr.Iverson.I think New Scotland Yard will further consider the importance of security robots in London.Disapprove!This is a violation of civil rights and a defiance to liberty!The heart of London is gone!What?
```

### [47] hash=`6823678d4edadcb3`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
It's beautiful.This is what father used to protect, but it is mine nowThe robots can't tell real fire from fake just a few sheets of nitrate flash paperThey'd turn on all the fire sprinklers loyallyThen a steady stream mixed with slug essence from the fire water reservoir gushed out of the sprinkler headsMiss AC did you see how the robots were glued to the floor unable to move if they had emotions
```

### [48] hash=`36ef3745a6de238f`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
they would have cursed me to death.Are you satisfied with the answer, Miss A.C.?One last to go, Melania.What a strict mentor.No worries, I will get back to the hotel as planned.Right on the dot.The next stop is...Room 1132, Insomnia 90 Hotel.Get to Regent Street,take a rest on the bench at the fifth flower bedfor three minutes and twenty five seconds then turn into the lane next to honey candy house
```

### [49] hash=`8d086cd56ed8178d`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
miss ac on your right fire engine bubbles is this the latest way to extinguish firebut why is it here what's wrong with the bubbles not good leave only three minutes left i mustLet's go now.Don't stand in the way, hey?That's not the direction, boy.That's a ski resort on the snowy mountain.Best place for vacation.Elders and youngsters, friends who are passionateor reserved, welcome to the Bang Bang Frisbee
```

### [50] hash=`68f20694e63c3c66`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
rock and roll party.This is an improvised and liberated event of artthat everybody can join.This is the utopia where you can totally voyage far,And even with myopia, this is our world in the future.Yeah!Who's this?Ugh, a knobhead causing traffic jams on my way?There's no time.Okay, take it easy, take it easy.Just fix these bubbles.There must be something that works.Disguising caps, staples, hiding cups.
```

### [51] hash=`1151c0908f80213c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
The smart detergent gun.23 detergent bowls at one shot.In a flash, it will make thisplace shiny as new.Perfect answer.Give me back my empty streets.Don't.It's super absorbent.My adorable bubbles, look how you embrace each other enthusiastically!Take it away!It is the summon of your terpy, the revelation of terpsichore!Haha!Thank you so much!That avant-garde courageous and innovative girl in the leather cap!
```

### [52] hash=`58c51236778ac4e1`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
These unplanned and inexplicable things...I think I'm also affected by the visions.The traffic is totally congested.No chance to get back to normal in two minutes and 25 seconds.Honey Candy House.Insomnia Nighty Hotel.Calm down, Melania.You've sorted out a roadmap of all the blocks in London.You need a new plan.A bold new plan.Spice is going!Your magazines, your handbags, everything!Celebrate!hey that's my magazine what are you doing what are you going to do with
```

### [53] hash=`e29fc7ea4154b97a`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
miss ace oh chow he's madthe show's on conventional choice a nice time with the note even for a greatcheese I can't tell his strength just from his appearance well um missMelania thank you for your bewildering variety of gadgets I would have beenmore important things to do.I can't get stuck here.Please, show me to the hotel,the one nearest to here and farthest from the police station, if you really want to thank me.
```

### [54] hash=`042f1f82111a9da4`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
Uh, R-Rest Inn?Maybe you could take your chances there.A better choice would be Insomnia90 Hotel, but apparently the way there is blocked by the stupid fire engines.Rest Inn is around the third corner, down the lane from here.By the way, stay away from those nutters dancing in bubbles,and keep an eye on your handbag, so you don't end up like me.I managed to grab it from the newsagents and this is what happened.
```

### [55] hash=`aa383f725f234aa9`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
Oh, my Rimmet Cup legend.I bought it for my collection precisely because of the column topic in this issue.The Rimmet Cup?Yes, you know it too.The same trophy that was won by Brazil four years ago.It's suddenly missing during the exhibition.and was replaced with a counterfeit by a thief where nobody knew.The security company failed to do anything and thus paid out a huge compensation.The genuine thing was only found in the trash months later.
```

### [56] hash=`cd230a0c5ce18ef0`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
That legendary trophy has now arrived in London.It will be the most wonderful award given to the winner.Woah, have I seen things?It's actually a celebration party for England!And it's the biggest ever!Pickles!Pickles, come on!Mr.Charlton, are you alright?It's March.Still quite a long way to go before the World Cup final.Is it?Thank you for reminding me.I need to tell Pickles in case he goes there for nothing.
```

### [57] hash=`90e6294ccf7ffeba`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p2`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P2.临时派对）

```text
Pickles!My little Pickles!He shouldn't have let his guard down.The bubbles from the fire engine must have been turned into a sort of life form by some specific incantationsPoor mr.Charlton.I suggest you try some of this thinking mud freshenerIt cleans the air nearby with its brutal destructive power only with a slight side effect.OhWell, I feel so much better nowThomas can breatheThank you, Miss Melania!

God bless you and have a safe journey!You're welcome, Mr.Charlton.I think the stinky mud freshener would suit you better.God bless you to find your little pickle soon.
```

### [58] hash=`71be0e8b48f9b6f1`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
The Court of A's Cafe faces the North Circular Road.It is around 4.803 miles from the destination.Captain Regulus drives at 65 miles an hour.Given the rules of the racing, she will arrive earlier.There is a lovely puppy.Hello Mr.Puppy.You look a bit nervous Mr.Puppy.Are you hungry?Perhaps it is not a good time to fall.Please don't show me your tongue at random.Makes this apple feel stressed out.Captain, help.
```

### [59] hash=`2f175ac6a3317658`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
Your eyes seem to light up when I mention my captain.If Captain Regulus finishes the racing trouble free, I might introduce you to her.But now, let's stay away from each other, puppy.Oh?It seems you are quite interested in Captain Regulus.Wandering across high seas, she is a great pirate who never gets caught by all the Orwellian and the Conservatives.Is my explanation precise enough?I hope my wording meets Captain's requirement.
```

### [60] hash=`2149786fd890d2f6`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
I think you will like her.Most of the time we are wandering in London.Captain is fond of anything novel and funny.I am sorry little puppy, I have to go.Captain Regulus seems to be in trouble.I really enjoyed our conversation, hope I can fully understand what you say next time.Or maybe I can invent a tool to help us communicate.See you puppy.Bark bark.Freeze!Routine check.Your fire engine driving licence please.
```

### [61] hash=`68cea06d2f674f0b`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
Hello Mr.Officer.Again?Within a month you visited the police station 13 times.Stirring the pointers at Big Ben, doodling at 10 Downing Street, dying Tower Bridge with waterproof paints.This time you threw a messy street party, didn't you?It was not a mess, police officer.You're suspected of breaking traffic laws.It's reasonable for us to arrest you right now.Wait, police officer, what?What I did is legitimate.
```

### [62] hash=`2762efa21418df41`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
I've applied for the use of fire engine to the sergeant and got approved.Please, feel free to check, Mr.Officer.Can't believe the sergeant would approve such a ridiculous application.That's what he approved.But how are you going to justify those weird bubbles?Which one are you referring to?The laser bubble that reflects people's dreams?It caused all the people at the square to fall into a deep sleep for two whole days.
```

### [63] hash=`17dab98f36643bcd`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
They experienced the most unexpected but best holiday ever.Honestly, I really envy them.Or you mean the classic work of mine, the Reverie Bubble?If it's convenient to you, could you please disclose the feedback of other officers?I need some inspiration to revise my formulas.What did those officers see when they enjoyed my bubbles?Surrendered criminals or promotion announcement?Enough!This time we will absolutely find out the odd ingredients in the bubbles.
```

### [64] hash=`89be7f6296d40c41`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
You can't deceive all of us.Only if you guys can open the water tank.At least up to now.You don't have enough evidence, Mr.Officer.Fine.I now ask you to cooperate with our investigation as the witness.Well, you're right.Cops shouldn't be wearing such ragged clothes.What?This is a demonstration against the materialistic life, the Code of Freedom!Ahem.Though you didn't mistaken me with those stupid cops, I still suggest you better distinguish us.
```

### [65] hash=`59acac051133181c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
You were a suggestion!There are some slight scratches on the codes.The transmission system functions well.The braking system is not very well.Are you referring to those who are approaching?What?Bloody hell!They found me!Carnaby Street, call for backup.According to the latest update from Sergeant William, his seal has been stolen.The suspect, Diggers, is suspected of committing a series of crimes,including illegally using fire engines, forging police ID, attacking police officer.
```

### [66] hash=`cbe6a73d2bd8a6a9`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p3`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P3.犬类的哲学｜头条新闻）

```text
We also found someone illegally held an MRR competition on the street,and the suspect is likely Regulus, the Rock Pirate on the wanted list.Ah!You two!Freeze!Cooperate with our investigation!Whoa!Is he all right?Maybe, if all his statements are to be believed.Do you remember what he said at the end?He told us to read tomorrow's newspaper.The headline?Is that an obituary or something?Mr Apple, I'm going to add a special session for Rock Radio tonight.

What?The worst beginning and the best ending.To our forever, Ragged Lad.
```

### [67] hash=`201e34c9dc3ee048`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
Finally, I'm back.25 minutes and 38 seconds?I can't believe I'm 15 minutes late.Blame it all on that bloody fire engine.Still need to work on your flexibility.I'm trying, Miss A.C.Now, the final step.Yes, the final step.Take a photo of the reunion.Although there was a little challenge at the end, I was able to complete the answer sheet successfully.What if I enjoyed the photo shooting?Twitching eyebrows, stiff smile.
```

### [68] hash=`40599fa3c407b2c3`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
You'll like him.No, I'll be better, Miss Acie.Unpredictable imagination won't be enough.A better plan with more details is also required.I won't let go one single minuteuntil I accomplish the ultimate goal.I became a thief late in life.So I'm not yet good at dealing with emergenciesbeyond the plan.At least so far, I've given the correct answerBut to every question Father left, these were Father used to protect.
```

### [69] hash=`dff5590e022f0563`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
You've done a great job.Thank you, Miss Acie.There's only one question left.The key question.The Remit Cup.If I recapture Father's memories and glories, is it enough to make up for his regrets?Father, will he understand me?Maybe you should meet him.It has been some time.When the company went bankrupt, we couldn't even afford a decentcemetery.I wouldn't be surprised if a few wild animals jump out of nowhere in this desolation.
```

### [70] hash=`0906dcc13f157c9b`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
Excellent judgement.Critters!It seems they've made this place their playground.Three, this is not the shiny crappy vault.It's on an important mission.Be careful.Two, one, down.It's a rather wise decision to carry around Zizz Popping Nuts.Father I brought the heart of London for you.Do you remember it?That dim thief got sidetracked by the surprising slug spray and broke into the security room with it
```

### [71] hash=`101084fea5d99019`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
After that he turned over a new leaf and things unattended have never come to his mindBut what I'm going to face is completely different from a poor little thiefThat new security company had carefully arranged robotsThey took action by the book and were heavily guarded.But there's no creativity in their defense.All actions were exactly as they were in the Guidance on Security.Not even as surprising as a fire engine.
```

### [72] hash=`c103be2b2f711b3c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
It should be the best of times for thieves.I can't leave it to you.It needs to be sent to Sergeant Williams' office tomorrow evening on time.As evidence, it's quite important.But I have some interesting news.The world seems to have changed a lot.Today we have Mr.Iverson from the New Humans Company, which provides security services for the soon-arriving Rimmick Cup.As an experienced head of the company, he would love to share the stories of the Rimmick Cup with us.
```

### [73] hash=`4dc68396d5e5662b`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
Years ago, the Rimmick Cup was under the protection of the most well-known security company, Ramirez, but magically disappeared overnight.It only took one day for Ramirez to retrieve the cup.This flourishing company received waves of complimentsand people were celebrating the story of a false alarm.Everyone, including us, thought Ramirez defended their reputation.But, unfortunately, evidence from the verification agency showed
```

### [74] hash=`d1899858c25945ae`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
that the rimmed cup they brought back was a counterfeit.They were confronted with the pressure of forgery suspectand the disappointment from all the peers.The imagination of Ramirez caused catastrophic havoc to the Hell Society.We then have to put aside the security theory held by Ramirezand return to the more science-based and reliable guidance on security.As it turns out, any security theories without regulations are castles in the air.
```

### [75] hash=`54fa1680ec075ec5`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
It's a pure joke.What a sharp comment.Security measures require pre-built plan, advanced equipment, and reliable personnel.Ridiculous imagination is the last thing.The ideal answer to all of these can be taken from the new human security robots.Father, when you were assigned the mission to protect the Remit Cup,did you ever imagine such a day would come?If we had conducted a quality check on that Remit Cup after receiving it?
```

### [76] hash=`a91acc14e10ee80c`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
If we had investigated the transaction records of the client company, if we had verified the list of patrol officers,perhaps I would not be talking to your silent tomb today.Father, I will prove it all.Even if it'll lead me to a path different from yours.Real protection is more than defense.It's about attack.Mr.Iverson needs to learn a harsher lesson.Hey, long time no see!You here?Bet you the day before.
```

### [77] hash=`b72c99b09bccd116`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
You show up so often these days.Did you get rid of those scouts?They don't have time for me right now.Yesterday, Captain Regulus encountered a weirdo.Right.Ragged lad claimed to have left us his last words in the newspaper.Captain, I'm afraid what he said was a surprising note.Never mind, it doesn't matter.Tommy, what's on the front page today?Here, see for yourself.The Ribbit Cup exhibition starts today.
```

### [78] hash=`6087130ebbade880`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
Carnival for fans.New humans has announced to undertake the Ribbit Cup exhibition.More security robots will be put into use to replace human jobs.If all goes well, the security systems will be introduced to the police after the exhibition.London will embrace real peace.Far more reliable than humans.Meticulous enforcers.An all-round urban security landscape.It seems London will tighten the regulations.
```

### [79] hash=`42f4194481a0a6b4`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
The government plans to launch security robots.Urban tin monsters!Yes, according to the description on newspapers, those robots can block out mobile signals and change the regional magnetic field.I'm afraid our broadcast will be affected.Can we still borrow others' radio waves?Of course we can't.Surprising note is this, if the robots take over London, my plans for a pirate's gig will go down the drain.
```

### [80] hash=`dc42876df575eef7`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
New humans?I get it.Ragged lad is part of the robots team, or maybe even a badass boss trying to take control of London.No wonder he seems to have a problem with the cops.Limey!This one is huge!Are you going to provide your first hand to the press?They must be interested.Never mind, he saved us once after all.A friend will persuade him to abandon his evil plan.Captain Regulus will never forget friendship for profit.
```

### [81] hash=`ae8b4909cf44144a`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
Damn shame, that's a heap of dosh.You can even get your cycles and fancy equipment.Huh?Tell me first, how much do they pay?Captain.I was just curious.Just kidding.I have to go and do something more important now.Cheers, Tommy!I'm here to change your mind!Breaking.Gemini 8 conducted first manual docking in space.Fifth fluffy sports meeting is coming.Interested candidates, please sign up with your pet.
```

### [82] hash=`ae0a8d4a171b9b0d`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
Police notice.A man controlled a watering car with special means and deliberately violated public transit.He will be detained for three days as a punishment.How come?Party theme, the key points of my speech, host, future trend of art?None are mentioned.A brand new world was born yesterday, but most people don't have a chance to celebrate.Gloomy clouds haunt the sky of my utopia.Shame on London.Shame on the world.
```

### [83] hash=`4279aabf10bb817b`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
We need to change.Radical change.We won't be corrupted by entertainment.The bell of art will break the shackles of stubbornness.London has been trapped in long and dreadful night.What it needs is the sun, not the dull stars.Decided street won't attract many people.They're used to following the crowd.They can only spot the noticeable objects.We must throw a grand party of artto topple the mainstream, to blow more people's minds.
```

### [84] hash=`5113c7c485bf9817`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p4`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P4.不回头｜航线合流）

```text
And it shouldn't be contained only to streets.I get it.The eye-catching exhibition hall of the Rimmet Cup will become the unprecedented, the craziest, and the perfect stage!
```

### [85] hash=`474e3126c4e5c2fb`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p5`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P5.正中红心）

```text
Wendy, I've told you so many times, no picking up litter on the road.What have you brought back this time?Open your mouth.Ahhh.Luckily, there's nothing dirty on it.Gosh, it really messed with my head yesterday.I almost forgot something very important.Kids, look!Look at what good news our little Wendy has brought home.The Rimmick Cup exhibition starts today!Now I have a better idea.How about visiting the Rimmick Cup exhibition this
```

### [86] hash=`d37e235050db5d72`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p5`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P5.正中红心）

```text
afternoon?I heard that they will be doing a lottery at the exhibition.The luckiest guy gets full tickets to all the World Cup rounds.Our littlepickles is definitely a lucky pup just like every other draw before.Are younot excited?There's a chance to get an out-of-print signed football thereThen we'll have a new toy for our ball game!Calm down, Wendy.We will have a democratic voting session.Now, does anyone not want to visit the Rimmet Cup?
```

### [87] hash=`4a236a0aaa0dff45`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p5`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P5.正中红心）

```text
Raise your paw, please.Right, it's unanimous!That's mine!Dear, you promised me you won't make a scene when we're outside and no yelling at strange things.Alright, Mum.Security screening passed.If everything goes on smoothly, I can blow enough soap bubbles to create an ocean ofreveries within half an hour.I just need to cover myself.Hey, look!How would someone blow bubbles indoors?What a funny smell.
```

### [88] hash=`1e3578a8e8565afe`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p5`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P5.正中红心）

```text
I'm exposed in just a minute?Ugh, I need to hurry up.These bubbles are far from enough.You should respect and treat an artist fairly.There you are again, annoying hooligan.I don't think I can understand what you're thinking.Are Arcanus all so stupid that you'll always overestimate yourselves?I am not defeated, Mr.Iverson.The fire of art will never be extinguished, just like our craving for Utopia never ceases.
```

### [89] hash=`082a3692827959fc`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p5`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P5.正中红心）

```text
Annoying blabber.Though I don't know what stupid idea is lingering in your brain, obviously you just failed again.Utopia is not stupid, sir.Without a goal, life would be stuck in the mess ofcorrupting materials and entertainment.I'm sure, soon enough, people will have thecourage to speak up and sing for peace and love.I've met a lot of youngpeople like you who chase unrealistic fantasies.Ignorant and hilarious.

oh it's itchy bless me Talia hope the efficacy takes effect a bit slower
```

### [90] hash=`9ee8c3ac7002769b`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
All the fuses were changed recently.I'm guessing the head of security hereis a pretty tough nut to crack.But unfortunately, too much attentionto the guidance on security will probablylead to carelessness in other areas,transferring all the human security staffand relying solely on the patroland precaution of robots.The consequence is a 30-second blind spotin the monitored areas every four hours, 13 minutes,
```

### [91] hash=`aeb3e8e69876fb7f`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
and two seconds.That gives you the chance to change the fuse here.That's right, Miss Acie.I will prove the ineffectiveness of the guidance on security in personand start the show at just the right moment.Then our next plan is to meet up with all the security robots.Suspicious invader detected.Locating.The last one.You seem a bit smarter than the other robots.Locating failed.Initiate program two.Push pin blue gun.
```

### [92] hash=`1c57e309842db6d1`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
Oops.No noise.I have to be quick.Watch out for its detectors.Look out.It's not tear gas or electrode bug spray.These robots are actually using real military ammunition.This violates the guidance on security that has been strictly followed all the time.Is Mr.Iverson actually new at security?No, no way.The only possible reason is that he's unscrupulous.For his security announcement.I know their slogan.
```

### [93] hash=`57b359a19551cfda`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
New humans promise, the Rimmet Cup will be absolutely secure.Everyone's happy to accept the hyperbole and believes it to be true.We need to hurry.Turn 45 degrees left and move 13 steps farther.The core device of the ventilation system is located in the third room on the left side of the exhibition hall.There's no necessary living conditions and lighting.Normally no one will be there.I will have plenty of time to adjust the airflow.
```

### [94] hash=`b4b59f5f17e4329f`

- lang：`en`｜version：`1.1`｜arc：`雷米特杯失窃案`
- doc：`BV1P14y1D7To_p6`
- title：《重返未来：1999》1.1版本「雷米特杯失窃案」全剧情 - Reverse: 1999｜4K（P6.非暴力合作）

```text
Strange.Like the sour flame wine that's over fermented.There you are.You are?What's going on?There's actually an ambush here.It hurts all over.But is this my reverie?Or really heaven?Could it be a form of artcreated by the subtle sense of danger I'm feeling right now?And the dirty air?Cometo me.Come to me.You are my muse!Go!Into a human security staff who got fired and went crazy?Alright.I'll just
```

