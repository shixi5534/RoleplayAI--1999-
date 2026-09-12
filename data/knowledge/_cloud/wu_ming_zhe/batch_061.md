# 剧情图谱抽取 · batch 061

- 角色：`wu_ming_zhe`
- 批次：**61** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.6」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_061.jsonl`

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

### [0] hash=`a4a1bbdad6331282`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p45`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜1~6）

```text
什么?当你找到阿克林技术时的方向时查看如果水是真实的如果不是的话呢?在这种情况下,小孩我们没有选择只要把水放在你的瓶子里好,我会做到我会找到方向的通过误解如果水在流动,检查是否有任何错误我会前往这条河流一切会如我所说南东轻松一点用你的时间这个标志已经出现了我请了河流向我展示最强的能量然后它在南东之间包括所有其他方向这应该是我们所寻找的方向是的,这条河是真实的在流水中,它正在流向着生命好吧,也许我错了不可能考虑所有的可能性,女士请等一等我会把方向记录下来,并向所有人报告你为我们找到流水的方法,已经证明了自己是对的所以这次,我不会判断你的我听到,他们在附近绕圈吗?你确定吗?这不是他们的适当季节来绕圈和种植我应该是没看见东西但我不知道他们为什么在这里还有那些花有什么错你,你在哪里?你没看到我们周围的石头吗?它的颜色是不正常的我从来没有看过这种东西甚至不在书中而且看看石头的洞洞它们被水淹没了这不是在这个环境下发生的事
```

### [1] hash=`650f72ded5864fc3`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p45`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜1~6）

```text
冷静点,先生可能我们已经到达其他奇迹的记录了但这就这样了这怎么回事你怎么能解释呢又是你这个笨蛋的艺术技巧吗这是什么解释什么我不知道它是什么种子它看起来像是一朵小花,但是...站住有什么不对的同意,我们现在有个情况我们应该回到我们仍然能做的那样美女,我必须说这是我的想像之外只是一朵花,是吗?为什么你们都这么害怕?我看不懂,但是...这里的一切错误了雷霆不应该在这里出现雷霆不应该在这里出现植物在一瞬间发生我不想这么说但这个地方似乎被禁止相对而言,我记得很清楚我还告诉过你我的疑问这可能是和自然之间的交流当然不是你看你身上,这些奇怪的现象你知道我没有把事情搞清楚你决定去追求那些云屏但我们却结束了我不知道你下一项计划是什么但是算我的不,我的生命这不是我的意愿丹巴斯梅尔兹从来不会做这件事重点是这个地盘不合适你会被我带回来的没有疑问 这是你的计划对不起杰里安先生已经告诉了我们你的秘密 亚练的技术这是我们在这次航空上的最后希望
```

### [2] hash=`37630ca8c5093135`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p45`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜1~6）

```text
我们信任他这就正是这样你必须来陪我们我来到了丹巴斯梅尔兹我不会离开她我绝对不会让你离开我们队伍的队伍不 燕妮 你要跟他们一起去他们在把你放在后面看来你的助手已经做了自己的决定抱歉 但我从来没想过会这样话够了 我的抱歉 女士们什么?你在做什么?我不明白怎么回事?不可能什么声音?除此之外,我没有感觉到有什么浮动力量的浮动力量对不起,女士,我没有办法我认为,如果这不是因为我们肯定是有人在周围留在我身边它在这里,小心这是什么?它很快,根据它的翅膀的响声我们必须向前走,保护Mr.Jorian和其他人他们可能是它们的目标噢,是的,是蜂蜜!把蜂蜜拿出来,把蜂蜜拔走,把蜂蜜拔走不,等等,我没想到那是一只蜂但这只蜂蜜是人类的!而且它并没有靠近?你在说什么?我听不到!这只蜂蜜是人类的脸?这只蜂蜜的音乐也来自这只蜂蜜吗?这只蜂蜜在人类的脸上玩的音乐好,我明白你的意思我先走了请你好好听听我的步骤尽快找到我们归去此处并无尔等所寻之物
```

### [3] hash=`0c3246bbd43c0d11`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p45`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜1~6）

```text
什么?既如此,不如归去这声音是什么?听起来像一个年轻人怎么会这样?至少,这肯定不是一个计划呃...也许是在说话,但声音很奇怪我从来没有听过这样的语言若执着于此便是光阴蹉跎前程枉然勿要上前了我只能为你做出一切让我们去吧别担心信仰的指引已决定我认识你的语言但如果你会吃它你应该再试试牛肉有一个很丑的味道女士,小心你意思是食物,还是什么?让我们...停下来,这里没有其他东西给你我需要什么我所要的,甚至是我的自我掌握等等!我说错了什么吗?不要生气,女士他似乎是不可预测的那种人你还要跟这个家伙走吗?我们要赶快去追他我们要上去吗?如果要上去我看到了一片大野,一些植物,和一座黄色的森林森林的架子看起来像鸟鸣人们在楼下看起来很不一样楼上和人们,对吗?只有城市有楼下我也听到那些声音这不是幻想不,你不明白那些黄色的楼上和门口看起来很不一样最后一件事我能记得的是这个巨大的鸳鸯的探索在南方消失了你面前的城市楼也在南方

对吧女士你又在做什么你从来没听过我孩子我们站在正确的地方在这些楼上我们的队友可能在受苦因为我的评论门开了我可以看到城市的人但是警察在巡逻他们在拿着一些像武器一样的武器而前面那些看起来跟我们很不一样我不觉得他们懂得我们的语言就算我们要他们让我们进去记得那些巡逻吗几乎是不可能和他们沟通的没有一个翻译者希望我们的旅行证据能把我们通过那扇门
```

### [4] hash=`284d25ab83f80b4e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Please show me your pass.You have all our documents.This is not a pass.Sir, you have the documents.Please, take a closer look at them.I'm not a sir.Please show me the right pass,which shows where you come from and where you're going.Been here if I knew the answers.No pass, no entry.I think it has been clearly stated on our documents.The documents were issued by the Association.Our teammates were transformed into horses and taken away by a winged man.
```

### [5] hash=`d94c4d6803e4e654`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
We think they might have been brought here, so we need to get into the city to find them.This is urgent.I hope you can understand.I've been on duty for over six hours.There was no such thing as a winged man.You can't fool me with your stupid story.I've seen too many of these little tricks.The rule is, no pass, no entry.Fine.This man understands our language, but he won't buy it.Yenny?Then I will see if we can make it in without this pass.
```

### [6] hash=`a4bbc5423e296a95`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Trying to break in?You're overestimating yourself.Just trying.Because we are not given any choices, sir.Wait, Yenise!Do this!Closing the gate is bad.We...we have to get in.Or how are we going to get them back?We can't just leave them hereNeither can I just turn away from the clues to the Dushua festival and the mysterious Eastern arcane power, sirI beg of youDon't get any closer.Are you all right?
```

### [7] hash=`e780f12fafee81c8`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
They wish you just give up madamI'm even thinking of all these things we've been through are just illusionsThe unusual terrains the teammates turned into striped horses and now this nonsenseIt won't let you go in there and risk your life on the contraryChild, the unknown people, the uncharted city.We are very close to what we've been chasing.We were born to run after these exciting and amazing things.
```

### [8] hash=`d418d8371be422a4`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
You're also looking for an answer from Ask and Acquire, right?We have no idea how Mr.Druyan and the others are doing.There is more to consider other than our own safety.Well said.Speaking of which, the city is much safer than the wild.Besides, it's holiday time.They could be here for the celebration.Don't be so harsh on them.Understood.If I am correct, you have lost your pass, right?We do have a pass, but it seems it doesn't work here.
```

### [9] hash=`b99ece44aeb9e208`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Well, just an understandable mistake for people from afar.I should apologize for my mistake.What's more, this lady by your side has red hair, green eyes, and fair complexion.The features match the records in history books.History books?Mr.Li Zheng, in your history books?Do you have...Like I said, you may just call me Li Zhong.Book says, Wu Sun, one of the tribes in the western regions, has the most unusual appearance.
```

### [10] hash=`7e902aecc9296448`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
The present foreigners are their descendants with features of green eyes, red hair, and the looks of macaque monkeys.Monkeys?Maybe we can't believe every word in the book.No matter.Where were we just now?Are you not?It's interesting you ask.According to the records of the hub, most of the foreign merchants with fluent Hanis have lived a long time in the Central Plains.While you're obviously not one of them, neither have you paid frequent visits here.
```

### [11] hash=`cf2658351b01ae32`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Otherwise, you wouldn't have forgotten a proper pass.You're a man of sharp wit, I have to say.Back where we are from, merchants come and go, including those who speak your tongue.We've dealt with them a lot throughout the years.If it weren't for their advice, we wouldn't have made it this far on our first journey as a new caravan.I see.Foreign merchants are well informed and welcomed by the citizens in Pei City.
```

### [12] hash=`d8159c595148c595`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Oh, there are other foreign merchants in the hub.You are reliable as always, child.Thank you.I will take a look.Hold on a second.Looks like it's written in Turkic.Is it Turkic?No, it...Yes, a variation of it.This is the written language in the North.Yeni?This is the written language in your hometown.Also known as Yeniseik.Isn't it?Yes, that's right.My apologies.On our way here, they were transformed into horses and taken away by a giant bird.
```

### [13] hash=`fddbf9789b58ff8e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Transformed into horses?Then how come you didn't get transformed?We have no idea.Perhaps because Madame Bismaritz and I are arcanists, while the others are humans.What do you mean?Does the giant bird only attack humans?Then how does he identify them?Huh?The lines it draws are really heavy.And do we only have the black ink?There are different colors.May I have the red one?Please, hold on.I will get it for you.
```

### [14] hash=`e79d6273c1a19925`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
This is great!With your drawing, we can issue wanted posters to find the Featherman.You stay silent.Any questions or concerns?You mentioned a former employee of the G.C.Or should I call her the Zhili?If the Featherman has been there, you can take over the animals he brought to her.Even if he hasn't, you can still proceed with the letter.Since Gionansi is a very warm-hearted, she should be in the Jitsu right now.
```

### [15] hash=`56354a2ece405821`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
You can find her there.Thank you.We should go, Yenny.Even if we have to follow the crowd.Madam, do you think we can take the gaps between the houses?Or find a shortcut?That'd be even better.Careful.What's wrong?Sorry, we were in a hurry.Are you alright?No problem.Don't worry about the bumping.Oh, aren't you the foreigners?I've never seen any red hair in the city.It's pretty.It's holiday time.It's fine to stumble into people.
```

### [16] hash=`8131db0db74fff97`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
But what's with the rush?Where are you going?We're going to the G.C.Oh, but the weather is crowded with visitors.Do you know who they're running about?What happened?They have a local animal named Zhuyep of the ministry.Maybe they're arcane creatures?I don't know.I've never seen one in books.The liquor smell probably comes from them.And I think a herd of livestockrushed out of the fence over there.
```

### [17] hash=`1706b3827372b155`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
But I can't see it clearly.Sorry, madam.We are not supposed to stop here.How do you have enough trouble with the Zhuyep?Who does help these festive animals now?Wait, Jiu Niangzi?Jiu Niangzi, aren't you supposed to be in the Zhici,the work hours?You, isn't it?Do this without you?Making so much trouble on the first day of work?Who were you, Jiu Niangzi?I didn't see you in the tavern.Me?I was in the Zhici.
```

### [18] hash=`c89a274c52d38923`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
What were you doing there?Mr.Liu, did you forget again?The former Zhili went back to her hometown.Jiu Niangzi is the new Zhili now.That's not it.I'm justCovering for her.I was counting the festive animals and then I heard the noise outsideYou must have been distracted by the storyteller, huh?He was telling the end of the story today so you would never miss itWell, yeah, I thought he might tell the story of young ray.
```

### [19] hash=`654cac348be6ff50`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
So I hurried out and forgot to lock the fenceWe need to follow the crowd and see if we will have a chance to talk to herLet's put aside the juyan for nowHuh and talk about Emperor Yao.He had seen strange beasts like this many timesIt was the seventh year of his reignYao granted an audience to an envoy offering a treasure from the Zhejiang kingdomThe envoy had a strange face and a bulgy chestHe claimed to have come from somewhere millions of miles away from the Yumen Pass.
```

### [20] hash=`4bcaed550c8a029b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
This bird is born with the talent for human languages and the phoenix's voice.Our people see it as a Shang Ray, and I am here to offer it to you, your majesty.Then Yao and his people saw a real giant bird.It was as huge as a mountain and as dazzling as a phoenix.It had an azure body and red tail feathers.Was it really a phoenix?No, the bird was called Miemon.It was said to be able to read one's bones,
```

### [21] hash=`d0fdf8ff5deed46f`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
change their fate, and even remove misfortune.Yao was pleased with the giftand kept the bird in Duxua Mountain.Naturally, that very bird was the ancestor of all the Miamongs nowadays.Be patient and listen.Miamongs tend to inhabit silent and clean environments.So since the ancient times, the people have always cleaned their yards carefully fromtime to time, hoping the Shang Rays will gather and stay beside them.
```

### [22] hash=`af1391f9b607dd3c`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
It may not work immediately, but it makes things possible in the long term.Ah, so that's why we have the tradition of cleaning the yard on shore, too.Exactly.Some even make Miamang statues with jewelry and use them to decorate their homes,hoping the Miamangs will bless the family.Remember the chicken statues on your roof?Actually, they are not chickens, but Miamangs.So are those birds you see in the paper cutouts on the doors.
```

### [23] hash=`4fbe935e70db03c7`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Look, everyone, this is the Mayamon.It's like a normal chicken.More like a capercaillie to me.And like the bird I just threw, isn't it?The way he is speaking is interesting, rhythmic, like singing.It would be great if there was some music to accompany him.Something is missing in his story without the music.He could...Among the five elements, Miamong belongs to the fire.That's why people set fire in spring to drive away misfortunes.
```

### [24] hash=`0cb90d564284e1e8`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Speaking of...What is this noise?Cracker!Shoot!I almost forgot!Excuse me!Please let me go out!You won't listen to the rest?It's still early.Oh, are you going back to the tavern to make our drinks?Here is the case.The people call you Zhunangzi, and you work in the Zhixi, right?Yes, Lijun told us to find you, and we happened to hear your conversation on the street.So did the Featherman come here today?
```

### [25] hash=`dc3329c3f10fe424`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Featherman?You mean the Xiao Rui out of the city?I heard that he had been here.As for today, I have no idea.Li Zheng said that bird was probably the feather man they've been looking for and he appeared around the Zhese once.That's why we are here to ask for help.They're not horses, I suppose.Possible.Are you saying that the feather man can turn people into...into horses?Stan, how did he get this power?
```

### [26] hash=`a13019ec3ccf901e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
The use of arcane skills seems common here.Perhaps there are also many arcanists around, but could you please tell us more about thegods of Shirti?There are 12 or 13 of them, I guess?That's all I know.I can't read most of their names, but I know this year is the Year of Zhixu!We will bring lots of festive animals to the Broken Bridge to worship it!But not me.I'm new here, filling in for the former Jilly after she went back to our hometown.
```

### [27] hash=`3f9c77648c875519`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
They told me to take care of Jitsi for a couple of days.That's good enough for me.So, simply put, you're a doorkeeper?Not just keeping the door safe.I do stuff too.Like, um, take good care of those startle by the firecrackers.There is a kind of firecracker enhanced by arcane skill.It can make a huge sound much more louder than what you heard in the tea housePlease forgive her.She didn't mean to hurt your feelings.
```

### [28] hash=`56c76cc18d137952`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
We speak bluntly in the north.Oh, it's all rightI can tell she's a bit anxiousGetting us anywhere likePigs can't learn how to climb in a dayLet's think another way.He recognized your teammates from these horsesI'll pay close attention to the new horses for you.If there's any good news, I'll ask Li Zheng to tell you.You're so kind.But we just got here and haven't decided where to stay for the night.
```

### [29] hash=`a89ce9cb68d0e45b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
How are we going to keep Li Zheng informed once we find a place to rest?I see.I forgot to tell you that I'm the owner of a tavern.And I'm doing it well.It is located in a merchant's hub, two streets away from the Zhici.Everything seems brighter at night.Madam, what do you think about Junang's words?Could that be asking the choir?Jumping over a broken bridge is like...Jumping over a canyon or climbing over a mountain.
```

### [30] hash=`c0ceab2ddad05324`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
It's a condition that cannot be met.Like those merchants said.An inevitable price?Are you talking about the broken bridge outside the city?I'm so sorry, the chairs in the lobby have not been cleaned yet.So, I'm not sure if there really is a temple there or not.The Yuan Temple.They said you can talk to Zhi Xu in the Yuan Temple.Be faithful and ask it.It will answer you.What did they call this?The Divination, I think?
```

### [31] hash=`2a997898c7fdda09`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
They also said that the fog was strange.You can't stay there for long, or you'll pass out and get overexcited.Well, I haven't seen such things so far, but even so, people of that time still rushed there and prayed.Doesn't it mean that the divination is for real?After the bridge was broken, no one's wish was ever granted.Seems odd.There was already a bridge in the first place.Why wouldn't people rebuild it in all these years?
```

### [32] hash=`211e5bffbdf2038f`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
I can answer this one!The river dried out, people couldn't swim across,and the cliffs between the mountains were too dangerous to jump over.But, if one can be the new Xiangrui, the problem will be solved.The Xiangruis are awesome!They protect the city, help the people.There's nothing they can't do.Never mind.We'll check the striped horses in the Zhixi again tomorrow.Alright, I'll go with you.It's time to rest now.
```

### [33] hash=`1a4747a001dcdf8b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
I got the rooms cleaned for you upstairs.Okay, I'll take you to the room.I didn't see you from there.I thought you went to sleep.Oh, sorry.Madame Bismerth is tired, so...Thank you for helping us.Don't bother.Here's the water.What's wrong?It looks expensive.It's a gift I received.I don't know how much it costs, but it's delicate, isn't it?Yes, it is delicate.The pattern is a lushu, also a kind of xiangrui.
```

### [34] hash=`71c7150d1a2f7f0b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
See?It's majestic!The tail is like the sunset clouds.I really like it.I hope you do too.Majestic indeed.And it looks a bit like those striped horses in the Zhese.Both of them are similar to horses.But people still think they're horses, don't they?Sure they do.I think this species is native to Pei City.It's an interesting discovery and will help enrich our travel notes.She's in bed now.I can only drink it for her.
```

### [35] hash=`f2403d1e898cf4d6`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Your drink smells good.Is this the liquor that helps one sleep tight?Not exactly.It's just unfiltered liquor.Sounds like you have a lot of different kinds of liquor here.Sure we do.There are a lot of different liquors.The unfiltered ones, the clear ones, the ones made of herbs, the fine ones, and on and on.Bedtime liquors made of herbs with spined date seeds.I thought liquor was just liquor.At least there aren't so many types in my hometown.
```

### [36] hash=`55d22bcc689befe9`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Well, to be honest, I too have no idea why they are still liquor, though they have different names.If the color is the standard to classify them, then what am I when I'm wearing differentcolor clothes?Am I not 九娘子 anymore?That is to say, if your teammates are turned into horses or other animals in differentcolors, are they not your teammates anymore?They are, of course.I'm worried actually.Well, maybe not just worried.
```

### [37] hash=`4d69c8c237750cfe`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
I don't know.Looks like...you really miss your teammates.Miss them?I won't use this word to describe my feeling.All I'm thinking is, they were turned into animals because I gave them the wrong direction.What if...what if they can't turn back to who they really are?I think that will happen.Things won't get any worse.There must be a way, I promise.Like, the clouds turn colorful, pool water gets sweet like liquor, there are many signs
```

### [38] hash=`f29db49f36baf4ab`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
of auspiciousness, they just need time.Think about it, what if the story about the Yuan Temple is real?Maybe, maybe there will be another way for you to recognize your teammates.Even if the Featherman is not the Xiangrui, there are other Xiangruis in the city.All in all.Thank you, miss.No, Junang-sue.I see what you mean.I really do.Thank you.It's nothing.I will definitely help you.Here's some other spinedate seeds.
```

### [39] hash=`8872a1b5430acf56`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Drink the water, and I'll go make you a cup of tea with the seeds.It also helps you sleep.The yard...Go downstairs, and through the main hall.What's that sound?Where does it come from?Who is it?Someone's...singing?Tried horses...glowing?What...is happening?Asking me to drink?Chulangzi...Where are you?Is she...the Moe?Stop here.I must go further.They're going.Be off, feebly.Who is it?It's you.You!The other man who stole our horses!
```

### [40] hash=`e4015844d803e109`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
but I think you're overthinking I I mean whether enough or not it's not up to usright I know nothing about the law it it just doesn't feel right I'm justthinking we should do something because you are sad you have a pointthen we let's go to the kitchen now Lee Jung will be there today you'reHe was supposed to tell me something about the Doshua Festival.Let's tell him what happened today.He will know what to do.
```

### [41] hash=`b503beb67e18c147`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Sure.In past years, the festive animals used in the Fortune Walk and the Bridge Leap were less than three.A goat, and without exception.The poorer the harvest, the less food for the animals and less well-fed donkeys.So people had to use horses instead.However, aren't there too many festive animals this time?Even if it is for celebrating the birth of Zhixi, not to mention some of them are transformed
```

### [42] hash=`5f453117bbbcf11e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
from humans, we shall act rudently.If we have to cancel the ceremony, we must make the decision before New Year's Eve.A giant bird, a feather man, there's always trouble around New Year's.Are you responsible for this place?There was someone else when I last visited.No matter, I have an urgent matter to discuss, or it will be too late.I'm Ge Tian, and I'm here to advise caution.The lady owner of the tavern can turn people into lushu.
```

### [43] hash=`5702afd332fc57a1`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
She needs to be stopped, or more people will suffer.She has extremely light bones, which means she's still in the stage of development.She might be unstable, hence a danger to keep in the city.You are referring to Jiu Nanzi?Precisely.The goddess of Li Mountain that can read one's bones?But you don't look like her at all.No goddess of Li Mountain.Then your words have no weight at all.You should have claimed to be her.
```

### [44] hash=`4bb1f628959c942b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Besides, goddess of Li Mountain.Take a look around you.These paper cutouts, a man's face burned with a red tail.You are drawing me, not a Xiangrui.These paper cuts won't send me your prayers and wishes.They are not paper cutouts for worshipping the Xiangrui,but wanted posters, and you are wanted.The most important thing is to find Jiu Niangzi.She's the culprit of the missing person's case in the city.
```

### [45] hash=`01afa4858b3f1c74`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
I thought you came here to confess or make peace,But it seems not.You come to defame Jiunangzi while being ignorant of the fact that you are the top suspect.How am I related to this?Every time a disappearance was reported, you were witness bringing animals to the Jizhi.No.The nature of my visit has been taken wrongly.The Zhili there knew what I came for.When we arrived at the Jizhi, you had already fled without a trace.
```

### [46] hash=`6dede7997ccd2bc9`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
No one could testify in front of the Faxiao for her.So her words were considered nonsense.Now she has returned to her hometown.I wouldn't have shown up in the city if not for the urgent matters.What's the purpose of lingering around when my business is done here?Besides, the Zhi Ci allowed arcane scales to be cast without restrictions in the city.So it is your responsibility to bear the consequences of such negligence.
```

### [47] hash=`80a24618e2ea2c9d`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
You are very articulate.But how can you explain the testimony provided by the two foreign merchants?All roads are leading to you.Yes, the two foreigners.Confess?They are the other reason why I'm here.One of the two is here with us.She can explain to you.Wait, you mean she is...Ask your patience.Please, look at the water on the floor.What is this for?Is this a demonstration of your discontent?Because I didn't treat you as a guest, offer you a seat, or give you a cup of tea?
```

### [48] hash=`aee649892818cbee`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Can't escape work this time.Must it be clean water to reflect it?The water in the river was no cleaner.How did you do it earlier?What is the meaning of this?You are suspect.That's right.I know, I told you truthfully, why are you troubling me, instead of going after Jiu Niang Zi?Find some clean water, I'll prove it to you.That's enough.I'll fight you, but neither will you have me.Be careful not to hurt that horse, he might be one of the victims.
```

### [49] hash=`6b71247ef4007835`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
How dare you?Your strength will eventually run out.Is this necessary?Find me the clean water and I will show you what Jiu Niang Zi has done.How will I know if you're using your arcane skill to fake the result?The truth is, we know the girl very well, but nothing about you.No one had gone missing in Pace City before you showed up.So how can we trust you or your proof?And you have denied that you are a Shangrei.
```

### [50] hash=`0e3869f6d740a20f`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
It is true that I'm not a Shangrei, nor have I ever visited here.I never wanted to leave the mountain.You still left.You really shouldn't have come to the human world.What do you mean?My people have left a mountain and come to help you.They renounced their names, families, and even lives for you.They gave up everything so that you would have gods to worship.They became symbols, totems, except themselves.
```

### [51] hash=`f218a16007849da4`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
What are you talking about, feather man?I told you my name.I'm not a feather man.This feather man is not one of us.No need to call him by name.Seems like my people have been long forgotten.You forgot the Ge Tian who left the mountains,the city builders,the bridge masters,the flood fighters.They all faded into oblivion.You only remember the gods of She Ti,will never answer to your prayers.That's why I'm discouraged.
```

### [52] hash=`117046945b64fc60`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
By the idea of leaving the mountain like my people,I don't want to face such suspicion and disbeliefafter giving you all the help.Who are you?Now that I see it,the destruction of the bridge was inevitable.It was bound to happenlike I was bound to be left in the mountainand be the last of us.The bridge?Did you have something to do with the broken bridge?Featherman, tell us!Question no more.You can have me, if that's what you want.
```

### [53] hash=`79ec1b1b8b0d2396`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Mr.Ning Sir, please wait!Come no further!Huh?Ning took away the lady!What's going on?Now we lost another witness.Is this also part of your plan?中我的数账昨日便已遗落在他的酒房你一问便知取娘是这样吗在院子里是发现了一根骨头帮他东西现在正在被掳走的胡人娘子身上先把他捆起来你还有什么要说的该说的我都一说了若再不制止便是真的祥瑞来了也无力回天你究竟为何执着于指认取娘为凶手The murderer!What murderer am I?Qu Niang, it doesn't matter.We all know that you have nothing to do with the missing case.And what did he say?There's nothing we can do about the truth.
```

### [54] hash=`b3a436906a9bdf82`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
He's the fake one!Qu Niang, don't get agitated.For now, we can only lock him up in the pool.I'll go tell Fa Cao myself.The most important thing nowis to send someone to get Ma and that woman.We need to find her account first,then we can get to the bottom of this.Take her with you.Everyone else is gone.Xu Niang, come with me.I have something to discuss with you.Yuren, what on earth do you want to do?
```

### [55] hash=`938bd0f6f05a68fd`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Xu Niang?You look like Xiang Rui.Why would you say that?And even if you're not Xiang Rui,aren't you...Aren't you afraid...Aren't you afraid that Xiang Rui will do this to you?Xu Zhi, he didn't have any contact with us before.Indeed, this is not Xiangrui, and the city has been hidden for a long time.The mermaid on the mountain is Xiangrui, but that is her appearance, which can make others think that she is Xiangrui.
```

### [56] hash=`cba103cd40681eeb`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Before leaving the pond, Chi Li told me that mermaids look like hookers, just like walking out of the drawing book.It seems that this can explain everything, but Xiangrui is drawn on the book.Qu NiangBut of course, he is not Xiangrui, not like Goumao, or Mianmengniang.He doesn't even understand the principle of learning the art of art, and never doing anything.Learning the art of art, never doing anything?
```

### [57] hash=`83e9248fae1a03f8`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Hey, that's the truth.As long as you do something wrong, it will leave a mark.Even if he tries to frame you,before we find the books and witnesses,we can't just assume that he is the murderer.We still haven't found enough evidence to prove that Qu Niang is the murderer.Yu Ren, what is the real Xiang Rui?You know where he is.Why did you take someone else's accomplice and come here to point the finger at me?
```

### [58] hash=`8af847543dfbf1b9`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Such a person is blessed by the heavens.He shouldn't have deviated from the true nature of this person because of his lack of talent.He could have become like what Mr.Shu Shu said.He could have been as good as the painting.It's like being loved by people.Just like what everyone is hoping for.When you took Hu Ren's wifeand her companions away,you didn't think about their feelings.That's not the time for them to separate.
```

### [59] hash=`9a9bb8f2c4df0e45`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
You make me sad.This is not what Xiang Rui should do.Alright.Xu Niang,let's stop here.Take her away first.She didn't tell me anything.Everyone is the same.Although I know that you have always been very obsessed with Xiangrui,Yu Ren's words today have already revealed that she is actually not Xiangrui.I even thought that her attitude was more like saying that she is not Xiangrui,and that she never thought of becoming Xiangrui.
```

### [60] hash=`bfa795b9cf9afacd`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
I don't understand.How can she not think?Not everyone is so familiar with the legend of Xiangrui.Black City indeed had a good time under the protection of Xiangrui.But this year, the old days can only be checked in the mythical books.I don't even dare to judge whether the real Xiangrui still exists.But Qu Niang, you should know that now we don't need Xiangrui anymore.Don't we need it?Now we don't have Xiangrui,
```

### [61] hash=`fa2a1ac34406481a`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
and we don't even have an effective question mark.But look, we lost our communication with Yuan Temple,and the city is still in order.Du Shuojie is still very lively,which shows that Xiangrui is not a must-have.Is that so?Today, it seems that you are a poet.You know that I don't know how to write, Li Zheng.Unparalleled, indescribable?No, I just heard the Taoist say it too many times, so I remembered.
```

### [62] hash=`016123f2db8aaaa1`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Which Taoist?Is it a Taoist in the city?Before I came to the city, I traveled with a Taoist for a period of time.He would repeat some words.I always don't understand, but I remember it in my heart.It sounds like you once had a master.After all, you've always been kind to people after you entered the city.You walked on a path that's different from Ge Tian.So his name is Ge Tian.Yes, Ge Tian.But you still said too much to him just now.
```

### [63] hash=`ef930f868d2f824a`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
He's not the Xiangrui you've been looking for all this time.The real Xiangrui wouldn't do something like this for no reason.He might just be a demon who lives in the mountains for a long time.Why does he only recognize me?I don't understand.Did I do something wrong?You can think of it.It's because you are a paper gift.The paper gift has been returned to his hometown because of him.He sees this method as a joke.
```

### [64] hash=`e5a6646b49748a5c`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
Or he wants to do it again.Besides, when he broke into the paper temple today,I seemed to be quite surprised.So it's not hard to deduce one or two things.And that woman who was kidnapped...She...Relax.I've already sent someone out to search.We should now discusswhat will happen to Yueqiao tomorrow morning.Yueqiao?Yes.And this thing...If only the bridge could be repaired.No need to connect the animals.
```

### [65] hash=`8b9dc49fdbd642ea`

- lang：`zh`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p46`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜7~14）

```text
No need to jump the bridge.When I asked Getian just now,but he didn't answer anything,尚未追回,越走胡人娘子的红尾马居,大抵还是受了葛天的控制,等我们的人追到郊外,已经在雨中消失的无影无踪。城市郊外急雨,行路困难,可以理解。只能等此次雨停后再行搜索了。不过,一马居,协议盲眼女子,应当走不出太远。待到雨停,我会亲自带队前去。劳烦法操,分内侍罢了。稍待,还有一事,是今夜岁厨宴,法曹若是愿意,可携亲眷来娶娘的酒坊度过。酒坊?那可是今室街坊都去?是啊,他宴请乡邻,理由也不难猜。岁厨守夜,反过年去便是杜硕节的第一天,往年酒坊也是设宴的。
```

### [66] hash=`e3a3446009d51dc0`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Is it you, Yannisay?Where are you?Please, not let them catch us!I'm good.How did you...?I am walking to you through the water.Please hurry up and get back on me!Turn into a striped horse too?Or is this your arcane skill?I am not a striped horse, madam.I'm a Lushu.Both of them are arcane creatures, but not the same kind.And yes, that's my arcane skill!They were small and would melt when they touched liquor.
```

### [67] hash=`5c18590d3be5ec0f`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
And there were horses in the yard, also coming in on me.They had red manes and red tails, just like what I look like now.Didn't know they were Lushu's until now.Their stripes glowed under the moon.But didn't you have a closer look at the Lushu wall last night?I had no time to see it clearly, to be honest.Anyway, that chat I had with Junansi was...quite good.and it included Julan's arcane power because the stream across her yard is near one of its branches.
```

### [68] hash=`a12134274bb6e33b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
The running water might have diluted the arcane power in there.Usually, a stream of running water is like an independent settlement.It rejects outsiders by nature.Even I have been rejected more than once.The striped horses our teammates turned into could be an accident caused by an incomplete arcane skill.Oh child, I don't see why he had to take you away.What if I was there with you?All I know is he was there to take us out of the danger.
```

### [69] hash=`34ca16d4f9f05262`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
And he's injured now.When we confronted the people at the JC, he didn't fight back at all.I think he didn't hurt them for a reason.If he really meant to help us, we must go save him.Child, all of a sudden you seem to trust this creature entirely.Did he do anything else for you?Based on what we know, Ge Tian, Li Zheng, and Jian Nengze, they all seem strange.Please trust me, madam.I used to think this way, too.
```

### [70] hash=`54ea37c91eae54ea`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Maybe he's fooling us with a fake rescue.But he's not.He even showed me his arcane skill to win my trust.Yes, he read my bones.Can you imagine that?He gained information by reading my bones.And then he actually told me something I didn't even know about myselfIf I let go you will fall and death will be your endHold your life dearYou are a lot more vulnerable than you can imagineName me.It's a river down there
```

### [71] hash=`bc18ce1227e81419`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Yes, but you don't know how shallow it isEven a lantern can float on it.It's dying.I like the other branches you saw outside the citySo what does that explain why you captured me?The river is dying.I'm held by a bird man in midair.I'll fall and die if I struggle.There's nothing I can doYesIt's a rare wisdom for a girl of your age to know her limits.I'm not a bird man.I'm a yawMy name is good yet and use arcane skills
```

### [72] hash=`f49b0b68cffb2b26`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
You're an arcanist if you say so and it is soWe have gone for miles.I'll leave you here.Beyond the fort, you will see the step.I don't understand.What on earth is your purpose?Why did you turn humans into horses?I believe you can commit much worse crimes if you want to.Are you doing it for fun?The more you ask, the more mistakes you make.There is no such thing as a wrong question.We'll answer one of the questions regarding why I turned people into horses
```

### [73] hash=`0371ff4d3c66784c`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
The answer is I didn't do it neither.Did I have that intention?Interesting who did it then the lady owner of the town?junangziPrecisely if that's the case.Why did you leave madam besmelster alone?Do you really think I would buy your nonsense after I saw you take my teammates away?You saw the horse in the yard with the red tail and red mane, did you not?Yes, I saw them.It's not a horse, it's a lushu, or at least it looks like one.
```

### [74] hash=`e005a92a88ef412a`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Lushu?I have never heard of it before.It sounds like an arcane creature native to the East.It is a lushu, and also Jiu Niangzi herself.What?That thing is Junang Si?What you saw tonight was not real lushu.Those horses merely resembled half of them.I speak of the fact that Jiu Niangzi might be a lushu, a kind of yao,or as you would put it, an arcane creature.Your words sound even more complicated than those in the city.
```

### [75] hash=`1d13d02ff2635e07`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Is it because you are also an arcane creature, like the lushu?Or you have a thing only the pure blooded can understand?We're nothing alike.Lushu's are Xiang Rays,born with red manes and white faces,covered with tiger's markings.In the books, Lushu's are capable of casting an arcane skillnamed the Shape of Well.It could be the same skill that Jiuniangzi usesto turn others into Lushu's.Do you understand?
```

### [76] hash=`0683bc0608922211`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Yes, I'll try.The Shape of Well is a dangerous and secret skill.As written in the books, the Lushu's use it to transform blood into fire and stone into gold.So...it's like alchemy.I'm unfamiliar with what you said, but...Zhou Nianzi's power seems to be restricted.She cannot fully transform into a Lushu like a Yao could, nor does she possess great power.She's closer to a half Yao.Unlike other Lushus, she requires a certain medium to cast her skill, the shape of a whale.
```

### [77] hash=`b06fc0680a058394`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
This is also why people did not recognize her.She is harder to identify.Xun Neng Si, half-yau.Is that another name for the mixed blood?Anyway, even if you are telling the truth, how did you know that?It is within my bloodline.Like you find your direction through the water.You are away from the waterless land where you once lived, and to this day you are still wandering.What?You will travel far many times in life and turn homeward, like the migratory birds, until you find your lake.
```

### [78] hash=`09fc467981104642`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
What on earth are you talking about?Have I mistaken anything?I should hope not.Forgive me, I have long since stopped reading others' bones and put them into words.Perhaps I did not tell it in the most precise way, but it should be generally accurate.Alright, stop.I need...I need some time to digest your words.Careful.Things again!They already attacked me once in the street!These stupid birds!This one is shining bright!
```

### [79] hash=`7197eb75fc96c399`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Have you drunk the liquor?Offered by Jiuniangzi?No, but I had the water from her.Why?The scent of liquor stands is not strong enough to attract them here.It would have taken a proper consumption of liquor for them to notice.I worry that liquor is the medium for her transformation skill.But that is only my speculation.If the water you drink also exerts the same effect on you, you'll also...What's the result?
```

### [80] hash=`74758248fe366693`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Someone has been here.A woman with a high footstep and a horse.It's not a horse.It's a horse.The footprints are even thinner and smaller.Look carefully.Where are these footprints?There's a shallow pool ahead.There's no trace of them after counting to ten from here.There's no way to cover the direction they left.It shouldn't be.If the footprints disappear,there's a chance of a flood.There's a chance of a flood.
```

### [81] hash=`d0abe7543e40836e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
No, there shouldn't be any other traces here.For example, here.The edge of the cave.The sound of the zither.The size of the zither is quite powerful.And the degree of sharpness.It was here earlier.Really?There are two footprints nearby.It's shallow.It's the footprints of a young woman.This place is so low.is not an ideal place for ordinary people.The young woman who came heremet such a huge and fierce Qin.
```

### [82] hash=`cce53cbc84be8c8f`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
But there is no blood around.Maybe the truth of the missing Huis still different from what people say.We need to go back.Too late.So it seems RT can also transform peopleand must report this to the authorities.Stay here.can speak through the water.You know what my arcane skill can do,but I can't maintain it for long.I spent too much energy fighting the Jouillets.I must take leave.She can't see, and she's still in the heaven.
```

### [83] hash=`d47031d651c0aa77`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
She must be in great danger now.I have thought about it,given that my wand was also left in that tavern.But should I return,Zhou Niang's might be alerted.I sense kindness in that girl.She hasn't done anything evilexcept for turning people into luchus.Your friend should be safe with her for the moment.The more urgent matter is to spread the wordbefore she further repeats her mistake.I must go find someone to handle this properly.
```

### [84] hash=`1c62414a13cf2582`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
It's a person's case now.You'll be turning yourself in if you go alone.But outside the mountainsis indeed not meant for me to step into.But you are already involved.Besides, we gave Li Zhen a drawing of youwhen I was not clear of the truth.No matter.I will reason with him.Even so, you will need me there.Look at my arcane skill.It will be the best proof, right?So they will know that Junang Si is the real culprit who turned the people into, I mean, Lushu's.
```

### [85] hash=`72b6d7e095e36851`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
If they really need it.You need to know that you are a suspect.Even though I know you are innocent, you need something absolutely persuasive to prove it.All in all, you must take me with you.My arcane skill will vindicate you.Perhaps people here also stay with their families at this time of year, like we do on New Year's Eve.A heartwarming custom.Yeah, the guards here are more reliable than ours in the Empire.
```

### [86] hash=`e4a315e021fa4cb1`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
At least they don't get drunk on New Year's Eve.Madam, we are close to the Juicy.We didn't prepare anything other than these bottles.Don't cast any skills for now.You need to rest.We don't know what's ahead of us.Yenisei and the others are still in the shape of Lushu.She was turned into a Lushu in front of you.Are you going to just let her be?She has told you everything.Yes, she did.Now you're the only one who can persuade others to go after Zhen Neng Zhe.
```

### [87] hash=`66d99fe033cc0163`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
We are foreigners here.Don't listen to us.Today at the Zhici, none of us would have gotten away if I hadn't surrendered.They will only see me as a greater threat if I insist on raising doubts about her.They have known her for a long time, but know nothing about me.My words have no greater effect than yours, for I'm also a foreigner here.Still, you're going to just give it all up before exhausting every possible way to end this?
```

### [88] hash=`07b1dd45d73a0c92`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
You need not break my pride.Ge Tian and Mian Meng are never meant to get involved in this.There are people coming.You...I knew it.You two are in it together.The merchant identity was only an excuse you made up to enter the city.Isn't that so?No, please listen to me.The stories you told Li Jiang made no sense at all.How dare you come back like you did nothing, and break into the jail?You go first.Mr.
```

### [89] hash=`276b13d6bb40764e`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Kichin!Lushu is our free-footed creatures.Get on her back and leave.I'll join you shortly.Go!Don't you run!Catch them!Is he?Have faith in him, child.He is able to defend himself,since he managed to escape without others' help.I believe...I believe he is not aggressive.He left his wand behind when he tried to save you.You're here.You seem fine.Do you still intend to leave?Or have you changed your mind?
```

### [90] hash=`f95cea162a9a1f10`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I'm here for one last thing.When I was imprisoned in Zhici, I heard that Jiu Niangzi would hold a banquet at the tavern tonight.And the Fa Cao was also invited.I'll take the opportunity and get those half-lushus out of there.Please wait a second, sir.Yes?We're not going anywhere.We must release them from the arcane scale and bring them back.If you don't flee tonight, I'm afraid there will be no better chance for you to leave.
```

### [91] hash=`3d5e99a49e8671e5`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Though her true intention is beyond my speculation, I fear the consequences of her action will be severe.You know full well the consequences.Certainly.But you won't help us stop her.That is not my problem to address.I have done my part.Then why did you help us get rid of the soldiers and offer to help again?It doesn't suggest my further involvement in this matter.You are contradicting your own words, sir.
```

### [92] hash=`6766c72cd96d4c55`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
I'll put it differently.Look at the street.It is empty tonight.There was a time when people sent lanterns down the river on New Year's Eve.Even the simplest lantern would glow like the moon on the water.Those lanterns, carrying people's wishes, floated down the river.The further they went, the more wishes were granted.Some would cast arcane scales on their lanterns to keep them from getting wet, but most of
```

### [93] hash=`cf673e525a8e7a6b`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
the lanterns still disappeared in the depths of the mountains or at the waterfalls.I used to look down at the city from the mountaintop, watching those lanterns floatdown the streams and merge into a light belt in the dark.They were more brilliant and vibrant than the bonfires that were lit up all night in this city.I'm sorry.I don't understand what you mean.Time is against us.Now the river has dried up, and the water no longer has vitality.
```

### [94] hash=`86593bcdac7524e4`

- lang：`en`｜version：`1.6`｜arc：`—`
- doc：`BV1eo4y1u7aW_p47`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.6-活动】朔日手记｜15~23）

```text
Rainfall is getting scarce, accelerating the dying process.What was lost does not compensate for what was given,So people no longer show up by the river and send their wishes at night.And I have lost my opportunity to watch the light belt.Even so, to this day I haven't fully understood why I was impelled to leave the mountain.I once thought I couldn't bear the sight of those humans being turned into other creatures.
```

