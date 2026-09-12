# 剧情图谱抽取 · batch 105

- 角色：`wu_ming_zhe`
- 批次：**105**（未缓存补漏批 6/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_105.jsonl`

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

### [0] hash=`7d7980dc85fa18b3`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p1`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（01.【新警局故事】）

```text
对L.A.S.T.R.E.A.S.T.I.E.S.太荣耀了这次是谁受伤的有些富贵男孩他们在新闻上发生了一些严重的事件把一位同事放进ICU但你知道是怎么回事鞋带被拔掉所有的责任都被拔掉了但是 知道吗他们今天早上有些族裔从Vigils的办公室我猜他们决定我们不够努力或是其中一件事Vigils从基金上的?他们不是只负责恶行罪行的罪行而是造成严重的影响吗?我看不见这位Nightpiercer是他们的麻烦除了Vigils怎么会帮助我们呢?他们不认识这个城市就像我们一样甚至不算是一名官员只是一名族裔等等你不是说族裔吗?你听到我吗?看来他们决定这件事是一件事派驾驶队去帮助和测试他们的钥匙所以我们现在不只是狗狗,我们也是小孩这是个笑话吗?你的说话?我的嘴巴?长官说这是一个机会让我们人类之间发展出更好的关系我认为鸭子只是想和圣帕维罗的基金合作对,这样就能解释了Alden的脸所以,大家知道这艘飞行艇在做什么吗?
```

### [1] hash=`bb300f37288a09b0`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p1`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（01.【新警局故事】）

```text
还是有什么好用的?我听说有个中国女孩从一个有名的艇群的家庭她有一个非常有名的家庭这就是为什么这艘飞行艇聚集了她真的吗?只为她有名吗?这不可能是唯一的原因她至少会在测试中成功吗?看来她甚至没有接受测试她还在训练当中被选择没有任何经验所以你说这女孩是个完全的伪女?有些损失的富豪女孩在找机会去刷她的签证?不太像我所说的我是圣帕勒基地两月的Vigil圣帕勒基地两月的Vigil在报告工作的办公室里请你请教我去见代理长Alton嗯,他在办公室里我知道了,谢谢这是我们的公主我看到了街头的狗狗好,我支持你糟糕,我猜我的日子不是越来越容易了
```

### [2] hash=`a93b1c52a8da4b9c`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p20`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（20.【直至消逝的光】）

```text
我知道,那个是强梁简模一说,真的很像是险道兽强梁啊哎,你瞧,那尾巴,那老虎头和手上画的一模一样啊难道是强梁神兽显灵,还救我们了全部说来,那个女孩就是这一代的镇子怎么越说越玄乎了什么险道兽十二镇子那都几百年没见过了老周不是都说了,这是拍戏啊对,我不是和你们说了,这都是拍戏吗?你们这些家伙,居然还不相信我?这还不是因为你这老头子,评理总是不着调吗?现在我信了,我信还不行吗?这都是假的?老天,刚才那些像是鬼魂一样的演员出来的时候,真是吓死我了。我还以为真的出了什么事啊。真是逼着啊,这次真是来对了。没想到唐人街的社会游行这么棒,我得多拍些照片。这是显道兽强梁?哇,有影哦早听说夜群特遣晚礼局去年来了一个十二阵子的后人但还是第一次亲眼见到传说中的强梁大霸沈威那两个警长先生他们制服了那位演员小姐了这下就没有问题了只要拿到了那盘被诅咒的胶片我想我们应该就可以解除结界释放她夺取的那些受害者的神志让大家都恢复原状了
```

### [3] hash=`9a26af67485916e0`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p20`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（20.【直至消逝的光】）

```text
卖卖这是刚才的发生了什么不是已经解决了吗拍放它它好像不太对劲看起来就像是像是胶片损坏了的影像一样难道说这个有胶片构固的结界正在它正在崩溃这下糟了离开边缘区域把人们都往内侧带不要靠近那些看起来出问题了的东西知道了不过这到底是怎么回事我自己已经解决了吗我们正在调查雷瑟姆小姐您能否做些什么警长请借给我一些人手我能够施展神秘学藏品管理部交给我们的限制术士但我无法坚持太久问题还是输在那盘胶片身上我们会尽快从根源上解决这一切的好了 奇心小姐你也赢到任情现状了无论你在做什么立刻停下这是被诅咒的胶片三眼归巢它发生了什么?这股气息是…不会错,这是邪朔!而且这个数量根本匪夷所思!丽小姐,果然您也这么认为吗?我们之前遇到过类似的情况那位在行政大厅中发狂的洪先生被三眼归巢影响失去了部分的精神能量所以才被那些游荡的魂灵承煦而入所以我一直怀疑…我想漏了!居然没有提前计视到这一点!那些伤了他身的东西既然会被丢了香蚊蹭炮的驱敌吸引
```

### [4] hash=`a022e5f437de290c`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p20`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（20.【直至消逝的光】）

```text
那就更会被那些离开驱敌的圣魂吸引呢对他们来说那可是最好喂的饵料这里不知道有多少被胶片吸来的圣魂当然会引无数孤蚊野鬼过来了这可不是这张小小的胶片能够承受得住的奇奇小姐你的手是啊这张胶片被诅咒的胶片从一开始就失控了我看你如何解体一开始了雷瑟姆小姐意外播放了胶片她便在唐人街一带不断地制造受害者但仔细想想这件事本身就很奇怪八年前在香港的事件中仅有五名受害者但这一次在唐人街时她却始终没有停下直到胶片落入奇星小姐你的手上随即发生的印象事件停止了取而代之的是特定的目标遭到袭击我们当时以为是你借用胶片的力量实现原定的袭击计划你只是在尽力控制胶片将它制造的受害者限定在那些恶人而非无辜者的身上是这样吗职业人小姐太抬举我了我只是不希望好友留下的遗物就这样成为作恶多端的邪物而已所以你才做了这一切在射火游行上将所有人都卷进来是因为你已经逐渐开始无法控制胶片了可是你不是想要杀死菲林士多女士吗难道那也是谎言如果说利用胶片是临时起义
```

### [5] hash=`bd26a4e4d68ff986`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p20`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（20.【直至消逝的光】）

```text
那么你原本的计划到底是奇星小姐对神秘警探菲林七最后一步的结局耿耿于怀那就是她心中的执念那个结局有两个最重要的元素射火游行以及一个应当得到惩罚的恶人恐怕在齐心小姐眼中菲律师多女士就是那个人这个人不是菲律师多导演是吗?为了完成你想要的那个新的结局你打算在社会游行中杀死的那个恶人大家期望的结局是穷凶劫恶之辈得到应有的惩罚这回除了我之外还有谁配得上这个名号我不明白你为什么要这么做Kway我必须这么做就像一滴墨汁落在白纸上无论用多少的清水去晕开用颜料去覆盖我无激于事她都永远无法恢复到纯洁无瑕的模样了神也是一样人们总说浪子回头惊不欢但并不是所有的错误不能够被原谅你是说何日君小姐的事但调查明明显示,他的死是一场意外,你没有必要为他的死如此苛责自己,你只是…只是沉溺在自己的偏执之中,一次又一次推开了真心关切自己的友人,对他的感受与想法视而不见。这样自私的人怎么能够配得上C07的称号呢?又怎么能够再站在摄像机的面前
```

### [6] hash=`2431e9e1a289dd01`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p20`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（20.【直至消逝的光】）

```text
折磨那些同样令人作呕的渣子的确能够带来些许释放感与解脱感但那也只是暂时的那种令人作呕的感觉始终如影随形我四处寻找能够自愈自己的方法一直没有意识到那个最应该得到惩罚的渣子就是我自己再简单不过的答案我居然花了那么久的时间才注意到这种地狱般的日子总算能够结束了没有必要这样的你这样对自己太严苛了我相信何日君小姐一定没有责怪你收起你的拉桃花树吧职业人小姐她没有责怪我你已经看到了这张胶片如今的模样还能够这样说吗当然能你刚才的话根本是对Teresa的轻视Teresa的确是那种会积极在家偷偷摸眼泪的人但每一次掉过眼泪之后她都会重新振作起来对我说我优秀改了一些你看看这一版明明这些你都也知道但你却觉得Teresa被说了两句之后就放弃了她的梦想放弃了她所热爱的生活我可不会选择那样的胆小鬼做搭档所以你怎么说这就是我想要的结局这次我可不会听你的话了不要犹豫了职业人小姐警长先生我已经没有了力气则也无需劳烦你们动手这么多年过去
```

### [7] hash=`1fe2d4e039f8a613`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p20`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（20.【直至消逝的光】）

```text
我还是学了一些真东西的只要杀死我一切都会结束了那些不速之客会和我一同被消灭一切都会恢复原状一个圆满的结局所有人都会满意还等什么了是有这个方法了吗等等 教官没有任何证据能够保证我们按照奇心小姐所说杀了她 事情就会解决请让我试试吧毕竟驱除诡异 吞噬邪祟这可是我和强良的专程李要做什么你在做什么我能够感受得到她的确吸收了太多不好的东西说实话,恐怕我和强良从没有挑战过这样的对手。但让我试试看,这不是因为家族的使命,也不是为了模仿电影中C0G的所作所为,而是因为我想要这么做,所有的故事都必须有个结局。而我,也有我想要的结局。抱歉,这次我说不出什么义正慈严的大道理,只能给出这样任性的理由,但如果你愿意的话,请回忆我吧,强良。有大贤方乡世人受天子之祸向十二摄提神请愿得巫武之礼降伏恶兽收为己用然而贤道兽一时能庇护的范围终究有限于是人间仍有诸多邪祟诡异四面非人力所能敌但那时的百姓们却从未放弃过抵抗因为他们知道

只要心怀希望与斗志到最后一刻贤道手必将现身逐出恶鬼还人间一片太平
```

### [8] hash=`3973b8c7a698ff9e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
Last night, the Chinatown Shuho Parade drew hundreds, as tourists and locals gathered for the Eastern Spectacle.These photos, shared by an enthusiastic tourist, show the enormous holographic images that were created on-site,using arcane skills to present a stunning performance of the Chinese folk tale, Zhang Liang's exorcism.The event has been deemed a well-organized success, with many promising to attend again next year.
```

### [9] hash=`99893b2f1c5a52b3`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
Locals have expressed their thanks.One spokesperson said it's been wonderful to share our culture with people from all around the worldChinatown is always ready to welcome new friends from both near and farIn other news the arcane vigilante night piercer who has perpetrated dozens of attacks across the city has been apprehended by the DAANight piercer was revealed to be Chi-sheng a former Hong Kong movie star
```

### [10] hash=`f90862e12f2097b7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
Some members of the public have expressed continued support for the vigilanteDue to the questionable backgrounds of our victims, Deputy Chief Elden of the Division of Arcane Affairs gave his response.Visual anti-justice is incredibly dangerous to our society.No individual has the right to bypass the law and enact their judgement on others.Taking the law into your own hands will only lead to chaos, violence and potential harm to innocent people.
```

### [11] hash=`ee10f7ce8a56c83a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
We urge the citizens of Los Angeles to place their trust in usas we continue to dedicate ourselves to maintaining a safer society for everyone.If you share our passion for justice, we encourage all citizens to direct their assistanceand feedback to the Division of Arcane Affairs.The LAPD has just announced a plan to add anumber of positions for Arcane Affairs officers in the coming year to address the DAA staffing
```

### [12] hash=`b3a309241bdf1484`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
shortage.The St.Pavlov Foundation's Vigils Bureau training program is alsoset to begin in the coming months.To apply, please dial the hearing I canaffairs officers.Hasn't it always been your dream to don the uniform?Lookslike they accept all the applicants too.Why don't you give it a shot whenyou are better?Knock it off.I've been a greengrocer for 20 years.With a little training, I'm sure you'll become an outstanding officer.
```

### [13] hash=`63b09143d9c1f8ac`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
There's a lot that goes into being an officer, but I believe what matters most is the heart to pursue justice and the courage to protect others.The doctor said you can be discharged soon.You should seriously consider applying for the position.Well, in that case, I'll think about it.Thank you so much, young lady.I heard you were the one who got rid of the curse and saved everyone.You are our hero!You're too kind, madam.
```

### [14] hash=`a19a01b5d170d215`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
I was only doing my job.And I didn't do it alone.It was a combined effort.Well, that's that.No more curse film crazies.Almost all the victims have recovered.Most of them have already been discharged too.Just a few poor saps who got hit hard are still around.But they should be out of here before long.Same goes for the victims in the parade.They've all regained their Sam...or...what's it called again?
```

### [15] hash=`6e3615f50e764080`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
It's Sam Wan Chut Pak, ma'am.Just call it spiritual energy or something like that.I heard that those crooks who were taught by a thing or two by Kee Singhas also recovered.Well, mentally, they are pretty physically messed up, so they will have to stay here for a while, I think.So many victims and not a single death.That's a blessing.Xi Xing pulled her punches apparently.I guess deep down she wasn't the deliverer of justice she claimed she was.
```

### [16] hash=`16b2cbb9eb07dd35`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
Well, no use wondering about it.Years on this job will quickly show you that the madness in Arcanus' blood always comes out in Arcanus' criminals.Trying to understand them is a waste of time.That may be the case, but I think that if we look at each other as individuals, we cancome to understand one another eventually, if we all try our best.Still nothing from Shang Lian?Well, what did you expect?That huge spooky spookter was a nasty opponent on its own.
```

### [17] hash=`91cdf354767f6e39`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
Not to mention all the ghosts that were attracted by that film reel.It was creepy, la.All those ghosts in one place.It was more crowded than the Dai Pai Dong.I mean, the Chinatown food stall on Saturday night.What's worse, those specters drowned the San Wan Chut Park of innocent people.If that hadn't happened, then Qiang Liang wouldn't have had to sa-Qianliang was lost because of my incompetence.I don't know how I'll be able to face my family now.
```

### [18] hash=`84b5e72dc758c545`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
There's something else that's bothering me.When Qianliang pulled in the evil spirits, I thought I was going to die with it.But it looked at me and pushed me aside.It bore everything, all alone.Why did it go to such lengths to help me?Because I'm its Zhenzi.The way it looked at me, I think it wanted to tell me something, but I didn't understandwhat.Qiang Liao had been by my side since I was six, but I always saw it as a heavy burden
```

### [19] hash=`7b53a13d1826d97b`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
or a double-edged sword.I never saw it as an independent individual or as a friend.I never tried to truly understand it, and now I've probably lost the opportunityto ever understand it.Come on, enough with the long face.Maybe Qiang Liang will respond to you one day, you never know.And I'm here if you ever need my professional ghost busting service.Exclusive discount just for you.Agreed.Isn't it a literal legendary beast that's existed for ages?
```

### [20] hash=`664bcc011264c7a6`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
No way it bit the dust just like that.I bet it's recharging in its lair or something.Then it'll come back when it's full of juice again.We're crying out loud.The DAA is in a movie theater.Where do all these people come from?My apologies, sir.I invited them.This may be the only chance for Teresa's last work to be shown to the public.I want as many people to see it as possible.Every filmmaker wants their work to be shown to the world.
```

### [21] hash=`c871c8a39867496a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
I appreciate your understanding.Oh now sir, it's no big deal.Everyone here knows what really happened.We just want to know what the theme's about.Yeah, didn't you see something on TV about...Assistance and feedback?You'd be going back on your word if you ignored us now.Hey, don't you go talking circles around me again.No need to worry, Deputy G.Velden.After Thor examination, we've determined that the film reel no longer possesses the ability to twist reality
```

### [22] hash=`29ea44782bf00ef1`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
It was our negligence that allowed the film to be taken in the first placeSo as mr.Joe said the people deserve to know the truthBesides every viewer is required to sign this confidentiality agreement before entering the screening roomAll right, everyone.Please hurry the movie starts in 15 minutesYou have my thanks, Vigil.If it weren't for you, I doubt Ah Sing and I would have had this chance to watch our good friends one song.
```

### [23] hash=`2111f8ec21c99eb5`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
I also have to thank you for helping me stop Ah Sing and for helping me keep my promise.Your promise?Yes, I swore on these two legs.In the past, all I cared about was making the best film.I saw everyone, even my actors and writers, as tools to reach that goal.But I was wrong.There's no such thing as a best film, only a better film.And to make a better film, I need a team around me.What matters most is the people who make the film, not the film itself.
```

### [24] hash=`5805a6978092ea7d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
But as long as we're living, there's still a future.Maybe I should hire a good lawyer for our scene.They can probably secure a shorter sentence.When she's free again, both physically and mentally,perhaps we can make a movie together, just like old times.Are you sure?With all due respect, Ms.Noah, that will probably be a very long time from now.So even if we're old ladies by then, as long as we can still move,
```

### [25] hash=`a96b574e2bbf61be`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p21`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（21重映日）

```text
I'm certain we can make moviesSpeaking of which you'd make an excellent addition to my crew miss LiangDon't hesitate to contact me if you reconsider your career choiceYou're very generous miss Noah, but I think I'll stick to being a fan for the time beingI look forward to seeing what you do nextYou won't be disappointedBy the way, have you seen miss Latham lately?The visuals will put a stop to it.

I suppose we'll have to wait and seeHey, you two get your asses in the screening room.We're all waiting for youNothing's more important than a movie that's about to startLet's go vigil
```

### [26] hash=`791146c98f868787`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
Scott's Ward.Did I take a wrong turn?Excuse me, Doctor.Could you tell me where Constance Scott's Ward is?I'm kind of lost.You're in the wrong area.You need to go straight forward this way,take a left at a corner, and a right at the next.Forward, left, then right, okay.I'll remember it now.Thanks for the help.Sure.That's odd.Why do I feel like I talked to that doctor a few days ago?Must just be my bad memory.
```

### [27] hash=`30d78b45a57d1f2e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
A lady last time was more friendly.Wait, which way did she say again?Sorry, doctor.It isn't time for the routine checkup yet.You're right.But yesterday's medical report showed some concerning fluctuations in the patient's data.It was my honor to serve you madam, and I must say you have incredible foresightThe vigils caught me, but they couldn't get any useful information because I can't remember any
```

### [28] hash=`8c71cb0850c99057`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
But you needn't worry I can handle this myself.I met Matilda not long agoShe was worried about you.Have you not contacted her?That is not necessary.Were she more perceptive, she would have already discovered me herself.She will find me when she's ready.What was I doing again?You are far more distant than you think.They run fast, that's for sure.Looks like this fish is bigger than we thought.Have you figured out what happened to the two officers?
```

### [29] hash=`84d5040b5e724b92`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
Truly genius.And I still don't get why you're keeping all this from Liang.She's your cadet and right here in the city.We should have had her join the investigation.I can't wait to see her face when she finds out what's been going on.And I'm not defending you this time either.Defending me?There's nothing to defend.If we told her about our plan, she would have started acting differently and spooked our fish.
```

### [30] hash=`437f43f450fb3ee0`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
There are five in total, including the cursed film reel and the wind-up toy that the timekeeper shattered.Tell me Bob, does our fish need all five arcane items?It's Alan, not Bob.How many times do I have to tell you?And to answer your question, no, I don't think so.The wind-up toy has already been destroyed and the film reel has been recovered by a fellow cadet.These items did cause a few problems, but I don't see any common thread between the incidents they caused.
```

### [31] hash=`03273f11abef794b`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
Correct, Brian.Those two items were probably just decoys to divert our attention.Again, it's Alan.Fu ca mu yu lin, ren jie shi er bu jian.Of the five objects, they probably only need one.Take a guess, Buck.Which one do they need?Manus Vindictae obviously considered the succubus a valuable asset before she got away, right?So if our fish was a die-hard loyalist, they would have delivered the wind-up toy to their
```

### [32] hash=`3bf23e60aaace44e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p22`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（22无署名访客）

```text
master straightway, rather than letting it be passed around all over the place.While our fish is in collusion with Manus Vindictae, they are swimming in murky waters.They may be pursuing their own agenda.Things are starting to get interesting, aren't they?Like I said earlier, not bad at all.
```

### [33] hash=`edc7593b12e156a1`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
Here we are.Get out.First case of the day.Anytime regular beat cops find a case related to Arcanum, they'll call it in to dispatch, and then we get to come mop it up.This is what we call a basic Arcanum incident.The bread and butter of our work, kid.It's not often that we get anything urgent, but you've got to stay on your toes.But to be honest, I hope we don't get anything big today.Last thing I want is to take a rookie like you into a real emergency.
```

### [34] hash=`e14a67e2fafa8e40`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
Are you just that much of a pushover or is this all an act pardon?I don't quite understandNothing, just keep close never know what can happen with these casesDo you know how long I've been waiting those monsters are at it againUm, please remain calm ma'am.We're here now and we won't let them hurt youAm I correct that you reported there are critters that have broken into your houseCould you describe them for us?
```

### [35] hash=`70ba308d680aa7ac`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
Do you have an idea how many?Ugh, I don't know.Like a ton, a bunch?Two and a half buttloads?I didn't stick around to count them.So, there are many of them.In that case, I suggest we split up, ma'am.You could stay here and keep the ladies safe, and send me to take the critters down.Given we're in the city, I suspect them to be tamed, and it's possible that someone may be controlling them.Once we've established their type, we may be able to deduce the incantation that's controlling them.
```

### [36] hash=`20a3d04411bbc6c0`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
Some incantations can be easily traced, such as the manipulation incantation, or the shadow incantation.Tell me, ma'am, where are...They?Is this...This appears to be a Montreal.A new breed of critter from the Miss New Bible Critter Rehabilitation Center.Endorsed by the LSCC.They are medium to large in size and classed as non-aggressive.The Montullo consumes base Arkin materials and extracts the energy from them.
```

### [37] hash=`324f416a3921cda7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
They are intended to assist in the Arkin production industry.They've been slated for worldwide distribution.Why are they here?What are you looking for?They killed them?Oh man, please don't worry, they will not attack people, and it's against our proceduresto kill non-aggressive critters without authorization.There's in my lawn!And they almost bit my sweetest tail!Your sweetie?Um, I see, ma'am.I will do my best to get them up.
```

### [38] hash=`882a0b56b1cbfb52`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
Don't you dare lay a finger on my precious munchies!What?Can I help you, sir?I knew it!This jerk is my next-door neighbor?He keeps all kinds of these ridiculous smelly critters around.I order you to throw him and all his disgusting little pets in jail!Are you out of your mind?They're just some adorable monchalos!What kind of sicko would want to hurt them?What did I tell you, huh?The copy agreed with your decision.
```

### [39] hash=`0863e59c49ec9d03`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
Finally, lunchtime.I'll grab the cheeseburger and an Americano.Large.So, some fluffy trespassers, an alchemy incident,a noise complaint for a werewolf infected,Are all the restaurants here so expensive?This is the first time I've been to LA and it seems things cost more than I expected.What?You broke?You're telling me the foundation, THE foundation, can't afford to pay you a decent wage?Oh no, no, it's...
```

### [40] hash=`d53b0a91dfcfc8a9`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
My subsidy should be enough for daily necessities.It's only the...I was hoping to save some money, but it seems the prices here won't allow me to.Sorry, please forget it.I'll have a chicken sandwich.Thank you.Okay.Alright, question time, rookie.Because I think I've got the wrong impression.What I heard was that you were some pampered rich kid from a crazy old legendary family.It's true.The Liang family have a long history and many legendary ancestors.
```

### [41] hash=`bb0066183faf1103`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
But that was a long time ago.Nowadays, we're not so different from any other ordinary family.Mm-hmm, sure.Ordinary.With all due respect, the Qiang Liang is a secret bean.It is deserving of great respect.It has a divine mission to expel diseases and evil beings, and has guarded the worldthrough the ages.Maybe that just sounds like old legends, but it's the truth.We've recorded every battle we've fought in our family chronicles, and we're only
```

### [42] hash=`74f1b11d0926e6a9`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
allowed to borrow its power when we're in the greatest of danger.This morning might have been a cakewalk, but this job can blindside you just like that.Never underestimate anything.Hey, you in there, princess?I apologize, but in our family, we have a rule.It means we believe you shouldn't talk when eating or sleeping.What?You're kidding.You're trying to say I'm being rude?Or wait, you're serious, aren't you?
```

### [43] hash=`0fcac85868be2b42`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
What kind of stupid rule is that?Besides, why would anyone be talking while they're asleep?What, like you can't sleep talk?How do you even control that?Sorry, maybe I didn't translate it right.It means, keep quiet before sleep.The heck?So many rules.Damn princess, you must have had a miserable childhood.Let me guess.Every day it was courses and training, stuck inside, no books, no movies.Did they even let you watch Saturday morning cartoons?
```

### [44] hash=`6c446e2981af13cc`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
I've heard of kids like youSounds worse than jail to me a childhood like that is rough kid.It's bad for your head bad for the job, tooI don't understand why you're upset miss Poitier.How is it bad for the job?Did you check the list of incidents before we set off?There's a case we're going to after lunch a director that received some kind of threatShe's shooting a film in Chinatown.Anyways, this director is an Arcanist, and her movie is all about Arcanum.
```

### [45] hash=`63f7dbc41650d44a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
So it's in our department.The point is, knowing's half the battle in this job.It'd be easier if you were a cinephile, or at least familiar with films.Maybe then you'd know a thing or two about her.She's famous for those detective C.O.7 films.The first movies to really put a focus on Arcanum and Arcanists.Something about it, though.The detective in those films used a skill a lot like this Nightpiercer crook.
```

### [46] hash=`1226d4456e697082`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p2`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（02【最高危机】）

```text
What's her name again?Something with an N?News?Yeah, that's it.Wait, so you...Yes.I've watched her movies, too.I'll be damned!So was it a special reward for getting straight A's, or......are requesting immediate arcana support.City hall we're close by aren't we pack up lunchtime's over
```

### [47] hash=`ac2416380925a408`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
Let go of the hostage, sir!This won't do you any good!Away!That was close.Where's our backup?DAA, at your service.What's the situation?See for yourself.Don't come any closer!Stay back!Please!Don't kill me!I'm sorry!I really am!Please let me go!Shut up!It's too late now.Say another word and you are dead!Stay back!Hey!Trust me, pal.You really don't want to do this.Who's that?Doesn't look like one of ours.
```

### [48] hash=`eaf2ba11aaacb6d7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
Just some civvy.She was talking with a suspect before we got here.That woman...What, you know her?Look familiar or something?No, just a thought.It's nothing.People make mistakes.But some mistakes can't be undone.Don't put that blood on your hands or it'll never wash off.Is hurting this guy worth all that pain and guilt?Sooner or later, you'll get what's coming to him for what he's done.I promise you that.
```

### [49] hash=`1491aab1a20a77f6`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
I must!He's distracted.Rookie.Time for us to take him down.Please stand down, sir.Suspect under control?I repeat, suspect under control.No further backup needed.Nice moves.I was kinda hoping we'd get to see that familiar of yours, though.A simple threat like this isn't worthy of Qiang Liang.I have to reserve its assistance, unless absolutely necessary.So is this just another one of those rules?Or do you mean its help comes with a price tag?
```

### [50] hash=`ed1b31da9fcb4929`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
That it?What do you mean?I mean, so far, every time you talk about the job or your family rules,it's just the surface level stuff.How do you actually feel about any of this?How I feel?I don't understand why it would be necessary to mention that.Cause we're partners, kid.We've got to trust each other.How am I gonna let you watch my six if I don't even know how you tick?I see.You're my partner and instructor during my assignment with the LAPD Division of Arcane Affairs.
```

### [51] hash=`69c1d2f5453a7931`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
So, I'll do my best to learn from you and complete my work as assigned.I won't slow you down.That's not what I'm...Forget it.Oh, thank god you took down that lunatic.I'm really grateful, miss.But ain't you a bit young to be an arcane affairs officer?I think I've seen that uniform somewhere else before.You're a vigil, right?Yes, sir.Wait.I know you.The arcaneist scammer Johnny Three Times has been apprehended.
```

### [52] hash=`f225b973c8da8596`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
Using his arcane skew, ominous obeisance, he manipulated his victims to do anythinghe asked, specifically transferring all their money to him.You're that scammer Johnny Three Times?That's when this loony attacked the police escort took him hostageHey easy officer.You've already got me.Don't need to be so rough with the cuffsClam it JohnnyWe should have just let that guy ice him.May I ask officer?Do we know if the men trying to kill him was?
```

### [53] hash=`f2057644afcd2a26`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
Yeah, he's the son of a victim.This bastard took his mom for all she was worth and when she found outboomheart attack like mother like son he was just as dumb as his daughtering old mom worse evenbecause he didn't even catch wise to it it's a concrete jungle baby and it follows jungle rulessurvival of the fittest crap for brains here never had a chance if it wasn't me it would havebeen someone else what a joke imagine killing over just because you lost a bit of cash
```

### [54] hash=`59a52f96fc96f535`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p3`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（03【秩序与失衡】）

```text
Then we've got this dumbass coming at me with even less of a brain.Think about it.If he killed me, how's he gonna get his money back?What the fuck up, asshole?Poitier, what are you doing?What?I'm teaching this douchebag a lesson.But we can't do that.It's against the rules.Well, I guess the visuals are cut above the trash when it comes to the DAA.Am I right?Let's get this straight, rookie.You don't tell me what to do.

I should have known.You're just the worst kind of cop.Everything by the book, sticking to your high and mighty principles like you know what's best.Stop him!
```

### [55] hash=`3d501a7c2b80bc8d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Help me!Get away!Out of my way.I will kill you.I will kill you all!Damn it!Is this dude high or something?No.No, I don't think this is drugs.It's an arching skill.I sense some kind of evil spirit.I think I can stop him, ma'am.Whatever it is, whatever you think you can do,do it.I will.This is my duty.Kill!I must kill this bastard!Who are you?Please stay calm, sir.I have no weapon.I'm just here to make a phone call.
```

### [56] hash=`966f36f111ef90ce`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
What?A phone call?Yes.And you are going to make it.Who are you dialing?You'll soon find out.Should we...cuff him?But I believe we should bring him to the hospital to be checked over immediately.Think you can handle him?We got this con man to take care of.God, what a loser.You know what I'm about to say, right?Okay, I'm sorry.Is that what you want?For me to say it?Sorry.I felt bad for that guy, but there was nothing we could do for him while he was possessed.
```

### [57] hash=`963e95585f94c45a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
If it weren't for you, we might have shot him.Well done, Visual Liang.And please just forget what I said.I was out of line.Say something.Right.It's okay.I didn't take it to heart.Good.Who's there?Sorry.I shouldn't eavesdrop.It's a bad habit.It's just...You remind me of my friends back in the old days.You're the lady that tried to help us soothe him.Thank you for the help.It could have turned out much worse if you hadn't been there.
```

### [58] hash=`ff60e57a9f115771`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Thank you again.That's too kind of you, young vigil.I just did what anyone should.Really, it was you and your partner that were the real heroes.You're too modest, ma'am.Actually, forgive me for asking.Haven't I seen your face before?Good to know that someone still remembers those old flicks, even after all these years.Yes, from the movies!That's right, you...you are...You got me, I'm casing or were you hoping I'd say detective co7 a
```

### [59] hash=`28347423d72d0656`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Full report will take some time.You'll need to wait for nowThank you, doctorOur perp had his idea with him that saves us a lot of diggingEric Wong 43 runs a grocery store in ChinatownLet's see the only family member.We've got is his wife a Lillian Lao who immigrated to the states10 years ago.Both have no criminal record, totally clean.He's an arcanist apparently,and a powerful one at that.But no reports of any prior misuse of arcana.
```

### [60] hash=`59a483a0bedac3e0`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Hmm, his car wasfound near the crime scene, all filled up with potatoes and carrots from the wholesalers.Either this was just a spur of the moment whack-o-move, or some bizarre attempt ata tuber-based alibi.Anyway, we've contacted his wife, and she should be here soon.Maybe we'll get some more clues from her.Yo, Liang.You listening?You're right.Earth calling Liang!Officer Podia, we're in a hospital.
```

### [61] hash=`f865aaa6447c6414`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
We should keep quiet.I would have.But that didn't seem likely to bring you back to Earth, space cadet.So what's got you lost in space now?I'm just thinking.About what?About Miss Qi Xin.Right.I guess you're really into those movies, huh?It's all good, Boo.I get the picture now, our little CO7 fan sneaking into the cinema behind her parents' back.You know, you're beginning to almost seem human, Princess.
```

### [62] hash=`10f41714c11d78bc`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
At first, I thought you might be an android,like those Laplace bots that got riding parking tickets for us.I, in fact, I do like Ms.Qixing's CO7 movies very much.Her character means a lot to me.Oh, is that the reason why you decided to be a V.I.S.H.I.A.L.?Specifically, yes.It's the reason I decided my destiny was to be in the police.But back to the topic.I was thinking about Ms.Qi Xin,but it wasn't because I like her or anything like that.
```

### [63] hash=`e8baf0340318cd58`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
It's just that her being here made me think about Knight Piercer.Ms.Qi Xin has a similar arcane skill to the one he appears to use.She called it Silver Needle.She even performed it in her movies.Could that really just be a coincidence?Huh?What she said felt meaningful in some way.It's a great pleasure to meet you, Ms.Qi Xin.I grew up watching your films.But what are you doing here in L.A.?I mean, if it's okay to ask?
```

### [64] hash=`9a450e96ac8eeac7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Sure.Not a problem at all.I'm here to see an old friend.Is it miss Noah?I heard she's planning a new film.OhSo you heard the news?It's been a long time since I last saw her.You're right though kid.I've got somethingI need to talk to her aboutUm, of course, that's great.Oh and the do show festival is coming soonI hope you'll go to the show for parade in Chinatown.It'd be so much fun to see you there
```

### [65] hash=`232f4b818ce3f1bf`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Huh showIs it really that time of year again?You don't like the parade?Of course I do.I like every bit of it.Watching people eat, perform, and come together to celebrate the end of the year,and to pray for peace and good luck in the next.I like the pure and simple wish that the Shohour Parade carries.But it always reminds me of the ending.What ending?You mean, the ending of the last film in the CO7 series?
```

### [66] hash=`88b345735d0115db`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
Yes.I know lots of people like that ending.A reflection of reality, they say.Tragedy leaves people with a deeper impression than comedy.But as for me, I hated it.The good guys failed and the bad guys won?What kind of an ending is that?Maybe we don't get a say in how things work in reality.But in stories, we can.We should.Reality itself is tragic enough already.Why should a movie remind us of how absurd things really are?
```

### [67] hash=`6e6427c9b5ed4dd1`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
What goes around comes around.That's what people want to see in the movies.I…I agree with you.When I was little, I also didn't like how it ended.Maybe it's true that reality can't guarantee us true justice, but I still want to see justice being served.At least in fiction.I feel the same way.Pardon me for asking.That beast you summoned was something else.It reminded me of a certain creature.A legendary beast from the north of China.
```

### [68] hash=`c9fc6466f36feff8`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p4`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（04【降邪】）

```text
That must make you a descendant of the Liang family, right?Yes.I'm Liang Yue.from the Liang family of the Twelve Jinz.Liang Yue.It's a good name, little vigil.I'll keep it in mind.
```

### [69] hash=`9fec8ed0f49c5631`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p5`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（05【局外人】）

```text
我写了一篇文章关于其心先生和其他两位制作人在CO7系列之间的冲突以前我以为只是谎言但现在想起了她所说的如果是真的我会说什么这太可笑了那停下吧,小姐我们还有工作要做你想想有多少人在洛杉矶有相似的技巧来吧,这是个完全的偏见你不认为他们是同一个人,对吗?这太疯狂了我们在谈谈的就是这位警察C-07虽然她已经退役了一段时间但她真的超级有名如果她真的就像个C-07一样为什么要等到这一段时间呢?这次是她最后一部电影的过程我们现在只能和这位创作家谈判我完全没事,只是小一点的伤痕我自己可以解决你称为破坏了手臂的伤痕就要马上让我们去治疗这里发生什么事?你是一位警察吗?你能帮我把这女孩停下来吗?她正在努力离开,用破坏了手臂她并非出了意外但从她醒来之后她已经不再让我们去检查任何东西她可能不是我们一般的病人但我们是医生我们不能让某人离开当他们需要立即的医疗注意一张照片吗快点吧我去…还有另一班但你只有一个朋友你应该去看医生
```

### [70] hash=`3138a80e4132fdf9`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p5`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（05【局外人】）

```text
坐下来等待等你确定要离开请向我们展示你的ID让医生可以给你治疗他在驾驶电梯一只狗…什么小心王先生的家人刚到场明白Mr.Wong在做什么?不漂亮他怎么了?他今天早上看起来很正常请放松,Mr.Wong我们要等著看医生说什么又是你对,对你属于邻居的私人眼睛,不是吗?你被犯罪了吗?什么?在外面,我好像是个傻瓜我其实是需要帮助的人我不会负责我的邻居抱歉Liang老师解决了他身体状况他的身体状况很稳定但我担心他心里可能会有长期影响他似乎在思考和记忆疾病中受苦最好是让他睡觉医生,他会不会醒来?我可以跟他说话吗?现在,我们建议对他这可能会让他更加紧张,因为我们担心他可能会失去记忆我现在该怎么办?他的母亲枪,我无法再用它了女士所以,谁是中国小孩的主人?DAA给你做你的工作吗?忘了啦听着如果你不尽力去帮助这群人那你就该离开我的路吧当他们第一次把他带进来他身上有血液流出的痕迹他可能已经离开了很久证明他已经无法控制自己
```

### [71] hash=`c166dce37ed2e554`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p5`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（05【局外人】）

```text
但我猜任何决定的东西都已经消失了医生无法独自解决因为,最糟糕的情况下,他们可能不相信我们,然后把这个可怜的家伙推到蠢蠢的农场去女士,拜托,你必须为你丈夫坚持他们已经派了一些最好的医生来自Laplace医疗中心如果有任何人可以帮助他,那会是他们他说他正在买农产品来自洛西拉斯不可以让他来然后警察就打电话给我我丈夫是个好男人大家都知道他绝对不会做这种事请你帮助我们你可以靠我们了我们会找出真相我保证谢谢非常感谢你你是我们唯一的希望拜托不要做错误的错误,小姐你永远不能做出你无法决定的一件事抱歉,小姐但我只能说保持住我没有说我们不会做到最好谢谢你,小姐不是很快我们还需要一些坚实的证据如果我们要破坏这个案件但是,从哪里开始看起来我们没有明确的证据不像我们所见的样子王先生没有敌人而且他对他的社群很深爱如果这件事是真的那也不能是一个简单的目标但还是有些事情我仍然想起当我问过任何最近的活动或发生王先生并没有回答
```

### [72] hash=`99cdc049abc44770`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p5`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（05【局外人】）

```text
而是…Jo我们的私人眼睛和他手上的尺子对抗DAA是的他提到他表示,最近有很奇怪的事情发生在L.A.的中国城市中据我所知他指出,那里突然之间的孩子变得很遥远并不回应年轻人开始显示记忆失误还有一个很健康的年轻人很快地发展了疾病的症状失去心智失去家人和朋友的记忆失误这也很熟悉Mr.Wong的状况但没有人认为会把事情带到警察那里我还和医生谈过他们说他们也发现了中国城的患者在乱七八糟的情况下和记忆失踪的增长我猜 再一次没有人认为我们的关注力你认为什么 护士这些情况是否相关如果它是你做的当中的传播我们可能会被冲到我们的头上即使如此,我认为我们无法把这件事看作是一种可能性我们的精神力量,直接影响到心脏,是很少见的但它们仍然存在我读过一些相似的案例,在《Virgil's Archive》中我记忆中,有一个案例和我们所见的相似症状然而,若有这些症状的犯罪意识那会是什么?或是会是一场偶遇?可能是一个小孩有强烈的艺术能力

无法控制它或是一些无法控制和危险的艺术物我们无法作出任何结论没有更多的证据艺术物不就有一个基础部分保存和记录危险的艺术物吗是的在基础部分的首领处它的官方名字是艺术部分啊!我相信我到了嗯!比我没想到的灵魂和空间更亮丽
```

### [73] hash=`943c960c763ffa62`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Des armoires, des armoires et encore des armoires.Qui est responsable ici ?J'avais l'impression que c'était un département important, non ?Où est la sécurité ?Le département contient tous les objets connusqui ont produit des phénomènes dangereux au Mister Yuli et à l'Arkane.Certains disent même qu'il contientchaque mystère Arkane résolu et non résolu, jamais enregistré.Et bien sûr, le plus grand mystère de tous les temps,
```

### [74] hash=`17c425efa619bf34`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
La tempête !Les défis toujours !Comme c'est le cas pour nous tous, ils sentent que chaque département sont désormais tournés vers l'étude de la tempête,il y a peu de temps pour ces énigmes plus triviales.Je me demande comment va maman.Madame Zia a dit qu'elle la surveillerait mais toujours pas de nouvelles.Moi Mathilde Abouaniche, c'est ta maman, la plus grande mère de tous les temps !Qu'est-ce qui pourrait bien avoir mal tourné ?
```

### [75] hash=`778357cb0f0bc1cf`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Maintenant, sa fille la plus remarquable est en train d'accomplir une mission importante pour la Fondation.Contrairement à certains autres qui ont consacré leur temps précieux à des vacances en nom de réveiller les jeux delurus.On espère tout de même qu'ils réussiront à rendre ces jeux aussi grandioses et sublimes qu'ils disent qu'ils étaient dans le passé lointain ou sinon...un sample d'eau de la rivière Peilin, numéro 003.
```

### [76] hash=`41661acddd3c6334`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Il y a des milliers de samples, collections et records ici.Mais peu importe qui vous en demande,celui-ci va toujours faire leur liste.Collecté dans une ville remote en Chine,quand les investigateurs arrivent,ils ont trouvé qu'il avait été isolé dans le temps.Tous ses habitants s'étendaient et vivaientcomme s'ils étaient de la dynastie de Tang.Ils n'étaient pas compétents de l'état du monde au-delà de leurs terres,
```

### [77] hash=`1af638cab876c6a5`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
comme s'ils étaient entrainés dans un capteur de temps du passé oublié.Oh, est-ce que c'est possible ?N'a-t-on jamais laissé la ville, pas même pour voyager ou faire du boulot ?Tu es une bonne personne, Miss.Oui, il semble que les investigateurs étaient confusés aussi.Au final, ils réalisent que l'art de l'Arcane est affecté sur la rivière de Palin.Oui, bien sûr !Qui n'a pas entendu de la bohénitie et de leur fille d'investigatrice ?
```

### [78] hash=`a11573275a3ab9d9`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
N'est-ce pas que tu sais que tout le monde t'a dit depuis que tu as rejoint la fondation ?En fait, ma mère et moi avons visité toi.Oh, mais je ne m'y ai pas présenté.Constance Scott.Je suis un étudiant de la SPDM.Bien sûr, maintenant, je suis juste un récordeur ici.J'ai été en train de vous chercher aussi, Mlle Scott.Le commissaire Pedra m'a demandé de te le donner.Une lettre ?Qu'est-ce qu'il s'agit de ?
```

### [79] hash=`6d29b316afe9fb2d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Et tous les efforts doivent être faits pour récupérer cet objet arcane avant de causer de plus en plus de problèmes.Vous devez partir immédiatement.Son dernier recrutement a été à Chinatown, Los Angeles.C'est un gâteau !Viens voir !Viens choisir !Désolé, pouvez-vous dire ça encore une fois ?Ji Ma Wu ?Et ça signifie......Paper Horse Dance ?D'accord, j'ai compris !Hey, boss !Vous avez encore de la brûlure ?
```

### [80] hash=`4f6b3ae75af54968`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
C'est tout ?Je vais faire un char si tu veux un peu plus de poivreIl y a un dragon sur la plage !C'est super cool !Bienvenue dans la ville de Chinatown, comment est-ce que tu aimes ?Oui, ça me donne un certain sentiment de nostalgieTu viens ici souvent Mlle Boidier ?Oui, je pense que ouiJe veux dire, à l'extérieur du travail, ça fait longtemps3 ans ou plusSeulement une fois dans 3 ans ?Je ne pense pas que tu peux le considérer souvent
```

### [81] hash=`3a1aa390671b4c2f`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Oui, c'est un endroit amusant pour un jour, bien sûr.Mais les choses sont différentes quand tu le mets sur ton uniforme.Tu te souviens de ton œil privé à l'hôpital, Joe ?Tu peux avoir une impression de comment les gens voient la police autour de lui.Tu veux dire que les résidents ici ne coopèrent pas avec la division de l'affaires arcane ?C'est compliqué.Il y a beaucoup de langage et de barrières culturelles.
```

### [82] hash=`03090a3af9267310`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Les gens ici ne tournent pas à la police pour résoudre leurs problèmes.Même quand ils le font, on a l'impression qu'on n'a pas d'idée d'où commencer.Ce qui m'a surprise la plus, c'est comment les Arcanistes de tous les types et les humains vivent si proche ensemble ici.Je pense que c'est la même chose en Chine, n'est-ce pas ?Je me souviens d'une fois, on a eu une calle à partir d'une séance.Quand on est arrivé là, il s'est dit que le shopkeeper était un grand oiseau blanc aussi haut que moi.
```

### [83] hash=`86e9bacdb1526050`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Et l'autre fois, on a chassé un pote perdu pour un poteur chelou.En tout cas, j'ai demandé à une vieille dame si elle avait vu un pote à côté.Tu sais ce qu'elle a dit ?Bien, je ne sais pas ce qu'elle a dit, mais elle a commencé à se moquer de moi d'être un laowai.Maintenant, donne-moi un peu de crédit.Je ne parlerai pas chinois, mais je sais que laowai signifie étranger.Donc excuse-moi ?Comme je suis américaine, bébé !
```

### [84] hash=`56820f91a6c37e83`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Peut-être juste un peu.Je suis curieuse de la pensée du directeur derrière de belles films.Mais ce n'est qu'un sujet de police.Donc je vais activer avec une souci professionnelle.En fait, j'ai fait une demande avec la branchée de l'intelligence de Virgilpour un dossier sur le directeur Noah et d'autres événements.On devrait le recevoir bientôt.Tu as déjà un dossier sur elle ?Ça me semble que tu vas un peu trop à bord, rookie.
```

### [85] hash=`65e169df591841c0`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Ce n'était pas en fait le directeur qui nous a appelé.Son assistante l'a appelé.Après, Noir nous a contacté et a dit que la « menace » était juste une misunderstanding.Normalement, on laisse ça comme ça.Il y a trop de crimes réels là-bas pour s'inquiéter avec un cas où la victime ne pense pas que tout s'est passé.Mais encore, selon Dispatch, l'assistante était vraiment trompée.L'opérateur a l'impression qu'on devrait lui donner un second look,
```

### [86] hash=`b8b08037e8f72d3b`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
donc ils ont la file ouverte.Mais regarde, c'est juste un follow-up et une excuse pour venir ici.Donc, gardez votre esprit sur la mission réelle.D'accord, madame.Elle a été réassignée au precinct local.Qu'est-ce qu'il s'est passé ?Qu'est-ce que ça veut dire ?Rien, fille.C'est juste que la plupart des forces n'ont pas été appris à affronter les crimes arcains.Ne me trompe pas.Ils sont bons policiers capables, mais je suis inquiète.
```

### [87] hash=`e84d8a198fd1b3ee`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
Si c'était un autre cas, je serais fermée.Just not break him, am I right?Not too often.Actually, I think we're obliged to take Ms.Noah's case seriously,even if it wouldn't help us with the other case.Please wait a minute, it's my communication device.SBF-1 portable contact device activated.You've received a new message.Downloading attachment.Download complete.Please check your mailbox.Message?What's it about?
```

### [88] hash=`0cd49b8fbef47b0e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p6`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（06【秘密通缉令】）

```text
C'est de l'Intelligence Department.Ils ont trouvé ses records.Miss Noir est enregistrée avec une fondation.Il y a peut-être quelque chose dans ses files qui peut nous offrir des bouts.Attends, c'est ça ?
```

### [89] hash=`4e47b55178c90ee5`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
Whose is this?It's blocking the camera's sightlines!Get it out of the way!When are we coming in?We've been waiting forever!I wish I brought a chair.What's going on?Are they filming another movie?Do you see anyone famous?Oh, is that today's lunch?Mind if I take a look?Not now!Alright, fine.That odd person I saw at the hospital, she works for the Foundation.Who?You mean Camera Head over there?What do you mean by odd?
```

### [90] hash=`e7fa07746a245292`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
You think she could be a fake?No, she's a real Foundation member.I checked her information as well when I inquired about Ms.Noah's file.Her name is Latham, an Awakened Arcanist currently working in the Arcanum Containment Department.I wasn't given any access to her details, but based on our encounter, we should have no problem with her.But...We did it!Abby, you're here!No, I'm afraid we'll have to roll that again.
```

### [91] hash=`8f4c2af0eb21ffc0`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
I'm sorry, Director.Not at all.I just want more emotion this time.She's your true love, but you have been apart for a long time.Things are different now.She is, you are.Your reunion must be more complex.It isn't simply happiness you feel.You must mix that emotion with worry and guilt.She doesn't know anything about what happened to you.You can't help but worry that she will never be able to understand you.
```

### [92] hash=`3e8598bfe8a5be0e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
You wonder if she has got herself into any troubles.I know this is a short scene, but the audience must see your full range of emotions.You are capable of more, so be more.I know you attended drama school, so let's see that training shine.I received so many letters, most of them friendly, some of them not so much friendly.I've made a name in this industry, and a few enemies too.If I paid any attention to the negativity, it only dragged me down.
```

### [93] hash=`b8411caf32b9bd78`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
I tend not to keep the bad ones around.While I'm sure you would do a fine job keeping me safe, officers,I can't let myself worry over it.Besides, what are they going to do, break my kneecaps?Frankly, the only thing I am worried about is that your presence is another distraction for my crew.So, it's very much appreciated that you went out of your way to check in on me, but I have a movie to make.I can't disappoint my fans.
```

### [94] hash=`2a74b0653f071e4f`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p7`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（07【参演须知】）

```text
Now, if you'll excuse me, we're burning daylight and I still have four more scenes to film.These Hollywood producers may have opened doors for me, but they also give me so many problems lately.Is this really just because of a movie?Pardon me?You seem to be refusing our assistance because you've decided this threat is only a harmless prank.You've decided that it's worth the risk to focus on your film.
```

