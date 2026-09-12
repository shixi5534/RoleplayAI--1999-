# 剧情图谱抽取 · batch 104

- 角色：`wu_ming_zhe`
- 批次：**104**（未缓存补漏批 5/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_104.jsonl`

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

### [0] hash=`1db8ae6ce9ace83f`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
And we are going to leave with ease now.Unnoticed.Hmm?What's coming?Our kind of creature.I can't believe someone has found me.This?The pigment to make you invisible in a second.No one will see you, including yourpuppy friends.Or this?Breeze Glider.When you open your arms, or, um, your front legs,all it takes is a little breeze and the flying membrane will get you anywhere.Or say, are you going to give everyone a surprise too?
```

### [1] hash=`7d3513b8d02760f4`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Sharp Along.It will wake up all the sleepyheads, keeping everyone wide awake.Um, it's often used to deal with those heavy-headed security guards.Where is that puppy?A dog retreats to the cup!Mind-blowing news!He will be the star!It sounds weird.You have to make your choice, my puppy.The owner of this hero puppy?Not exactly.I'm his friend.Best friend.Would you mind telling us how you raised such a brilliant dog?
```

### [2] hash=`a03bf519e68d8479`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
I guess people will care about the puppy's daily life after the article's published.Well, I often enjoy the symphony with him.Sometimes we'll discuss profound philosophicalissues together.Yes, we have quite an extensive collection of books at home.For example, Meditacionesde Prima Filosofia, The Republic, Rhetoric to Alexander.That's an informative first-hand material.Thanks for your cooperation, Mr.
```

### [3] hash=`06b8e1ac03dbf40d`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Owner.It's been a pleasure to be interviewed by you.Pickles too.That's beautiful.We may have further and more detailed interviews that need your cooperation.Constant streams of interviews, film shoots, and friendly matches with the England national football team will follow.I'm sure the team would also like to thank the hero who guarded the cup in person.The puppy's heroic act may even be highly appealing to film investors.
```

### [4] hash=`36200cba8156ea8f`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Really?Wandering is my destiny.After an unprecedented and unexpected soap bubble surprise party,None of them left anything improvised about Utopia.Not even one of them mentioning my contribution.All the people ignored a pioneer who created a new era.A monumental event was shamefully compared to a puppy.Is dead.That's one of the stories I've come across, readers of R2.It's dramatic, full of misunderstandings, lovely animals and terrifying intrigues,
```

### [5] hash=`10d1f0323d5ef9b1`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
again providing us with a ludicrous ending.I'm glad to have the great honor to share this withyou.Wherever you are, whatever you've been, I hope this story will bring you a moment of joy.And I am also sincerely looking forward to your stories.
```

### [6] hash=`543ee159ad7ba605`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p16`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-角色】以盗制盗1-都灵圆盘、缅因齿儿｜梅兰妮个人剧情）

```text
Do you remember this?Failed.Unsense.I know.Just a student.Uncle Fiennes.Curity?Melania.Should I bite him?For sure.I think.Miss Acie.Pelicanetic arcane skill?Fantastic.My apologies.Be nervous.Uncle Fiennes.However...Uncle Fiennes.I'm just a business man.Melania.It will be another long night.I have no idea.I can never think as father did.I...there's nothing I can do.
```

### [7] hash=`1f97d08889c27713`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p17`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-角色】以盗制盗2-水晶头骨、足球比赛｜梅兰妮个人剧情）

```text
Yes, however, Miss Acie.This is a key.Miss Acie, this is Father's sandbox?Yes, however.No.Look at these files, Miss Acie.However.Melania failed.You, you are right.Has been going well.Please put down the things in your hand, Miss.Wait a minute.Melania.I swear on the honor of Ramirez,I will make up for my mistake and in this stupid company I do know so is thatrevenge unlike your father possible admit Melania would you like to be a

thief so no mr.finds I'm just a student wait a minute I just want to seethe legend of Ramirez continue miss AC could you help me think you would sayAce!I bet he would.
```

### [8] hash=`dc2845d5ef05f6dd`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p18`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-角色】小狗与流浪汉1~4｜皮克勒斯个狗剧情）

```text
Yes, I'm terribly sorry.What sugar it feels uneasyThe puppy is asking for your opinion.He will travel farBut it feels uneasyAccepted your suggestionBut puppy hey my friend to chase its dreams to seek the source of everything
```

### [9] hash=`34f10f135540f89c`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p19`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-角色】小狗与流浪汉5~8｜皮克勒斯个狗剧情）

```text
the puppy is surprised the puppy is not familiar with this puppy can't be ofhelp pickles puppy considers you as unwise heyit's confused no chance at all no way wants to leave the party to youwatching to try everyone's having dinner now sit with you together
```

### [10] hash=`142c9fd6a5158810`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
Let me sort things outMiss Lockerhead you said you could record and save your memories using a special type of film developed by the plusWhich means that even if you don't recall taking anything from the Arcanum containment departmentYour film should show whether you did or notBut the fact is the films are gone.Isn't that right?Yeah, I usually carry my most important memories with me and leave the others in my room
```

### [11] hash=`f2113b8e83cf3369`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
The Foundation staff checked the visitor log after the stuff was stolen.Turns out, I was the only one who visited the office that day.So they sent people to my room and checked all my film.But they didn't find anything.Then they said they already had other evidence.So...So they just declared Loggerhead guilty.But that doesn't make any sense to me.Something must be wrong.So, when you found Ms.Latham,
```

### [12] hash=`8d5d2562456602f8`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
You bought her a train ticket instead of putting her under arrest.I know I've gone against orders, but I'm sure Loggerhead didn't do this.She's my friend.I can't just arrest her and have the Foundation lock her up.I'm sorry for keeping all this from you, but you're a vigil.I had to be careful.So, if it's not crossing the line,Miss Liang, Miss Poitier, can I ask you to keep this between us?You can report it after we find out who's really done this.
```

### [13] hash=`6e7a6c93f20cbc85`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
Walk of Fame?Okay, now I just need to turn left.Wait, which way is left again?It changes every time I turn, right?Gosh, how the heck do people read maps?Are you alright?It seems you could use some help.Laura stopped to help me.She was really interested in my head, so we had a little chat.And I found out she was a director!She offered to take me to the Walk of Fame.We talked a lot about movies on her way there, then I told her I was traveling alone
```

### [14] hash=`112063241d9d445a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
So she invited me to join her movie shoot in ChinatownHow can I say no?I mean she's a famous director.There's no way I'd miss a chance like thatInteresting that was the same day that odd things started happening in ChinatownWell, I'm not sure about thatDid anything strange happen that day didn't find a strange film reel when I was unpacking that nightstrange film reelWait, could that be?Film reel I've gotten into the habit of labeling my films like check every day or check from time to time
```

### [15] hash=`4ef1ef7c38d9fff4`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
So that I know what to watch to keep important things in my mindI was gonna do a review that nightBut when I looked through my film there was a role without a label on itI didn't lose it.Check my film if you want to prove it.It got into thin air.But your film only records what you saw.Someone might have taken it when you weren't looking.Does anyone else know about this film reel?Did you have any visitors or notice anything suspicious after you played it?
```

### [16] hash=`26cb46b3071e18cf`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
Suspicious?I don't think so.At least I didn't see anything.The only person who visited me afterwards was Scott.She came to tell me I was wanted by the Foundation.Oh, but actually, I wasn't alone when I played it.Noir was with me.She said she was interested in my memories, so she came and...What's wrong?So, it was Noir who took the film?What are you doing?I'm sorry, director.I'll do it again.You don't have the skill of martial arts.
```

### [17] hash=`bcb979ba1ebb0471`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
It's easy to hit your head when you're down.It's too dangerous for you to do that.Go get some rest.This is the last person, Director.This place is not like Hong Kong.There aren't many dragon and tiger dancersavailable to choose from.Mr.Liu and his discipleswill be here in a few days.Why don't we wait a little bit for this scene?Kez is not here yet.Let me think.Is there any other way?Is it him?That's...
```

### [18] hash=`b67f476479c83f2a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
the famous little donkey in the daytime.What are you doing here again?Listen.I don't know what you, the police chief and the director, are doing this for.But can you stop bothering us with the shooting?We are not allowed to allow outsiders to visit.If you don't have a search warrant, please leave.Guys, relax.Li Ying isn't as mean as she seems.I didn't expect to see you again so soon, Miss Officer.
```

### [19] hash=`6ff1f3b5e1bf3145`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p10`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（10【抽丝剥茧论】）

```text
Do you have any other questions?I think I've made myself very clear during the day.I know nothing about the case you are investigating.I don't know anything about it.You're mistaken, director Filinto.This time I'm here to help.Help?I heard from Miss Laysome thatyou're worried about the missing actor.If you don't mind,I might be able to help you.I didn't expect that.
```

### [20] hash=`8b306e1d493afe83`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p11`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（11【喂，跑龙套！】）

```text
说我的演员,你吗?多谢您的好意,警官小姐不,看您的制服我想也许我该称呼您为职业人小姐您的提案令我受宠若惊若是能有夜巡特遣管理局的人参与这部电影的拍摄想必我们也能够吸引到更多的观众进入影院但也许您对拍摄电影有些误解它并不是一件容易的事您的好意我心领了我对电影《略知一二》也十分喜欢和熟悉您的作品我看了刚才您手下其他人的表现无意冒犯对于那些武戏的部分也许我可以试一试做更好的电影雷森姆小姐告诉我这就是您所追求的东西不是吗什么她在说些什么口气倒是不小这话倒是没错你就这么确定你就是能够让我的电影变得更好的那几条微料是的嗯 有趣既然你都说到这个分上了那么就让我们试试吧捷人小姐切勿打草惊蛇 勿为你真的做到了你所声称的事这一条的确更好堪称完美您过奖了 芬琳士多导演喝这个吧 没打开过的没想到你表现得还挺不错的那个动作那么危险真亏你敢做看着我都害怕不过我得提醒你如果你觉得每次都只是不要命就能获得菲林什多导演的认可
```

### [21] hash=`27196391132e736d`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p11`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（11【喂，跑龙套！】）

```text
那就大错特错了文戏才是考验一个演员的最重要的级标你的外形不错看你刚才拍戏也很认真黑不黑真的对这一行有兴趣如果戏的话年轻人我劝你最好更虚心一些这样才能有机会真的让更多人看到您说得对我很抱歉不过我的本质并不是演员未来也没有在这一行发展的打算电影只是我的爱好那可是太可惜了你的牵引我感受到了她非常诚恳我很满意但如果李月愿意提供更多我会更高兴的如果只是短时间的话我愿意尽我所能提供帮助这是我今天听过的最好的消息了跟我来差不多到晚饭时间了正好带你看看剧本顺便改改剧本相信我我们的观众一定会期待听到至少一句里的台词的台词是吗就这些吧怎么样记住了吗是的我都背下来了这不止一句台词吧投资人要是知道了可不一定会同意他们之前不就说过咱们在香港来一套不能造版不可以边拍边改剧本吗放心吧我都改了多少了她都不看剧本不会知道的而且这样角色塑造才完整一句话虽然也可以但这样的效果更好有不多只有三句而已吗我会在开拍之前将它们练习好的
```

### [22] hash=`24b44bd9d9af0401`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p11`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（11【喂，跑龙套！】）

```text
我期待着你的表现说起来我刚才在片场见到了一些神偶和神教我记得应当马上到渡舍节了剧组的人也要参加《射火游行》吗那是拍戏用的这次电影里的结局会是一场在《射火游行》中的戏我和这边的组织者们打了招呼直接让剧组参与进去借景拍摄在《射火游行》里的戏我记得《C07》的最后一部的结局也是在《射火游行》中视力不错嘛看来你说你熟悉我的片子并不是在吹牛你说你的妖精朋友能够证明一切与恶劣有关,对吗?所以是否和指导员有什么错误?但这并不代表她从来不会做这些!我不会怎么做。对不起,我...我不喜欢纷纷的事情。我们可以直接问她吗?如果每个犯人都会把自己干的所有坏事全部老实交代,这个世界上就不需要我们这个职业了。除了向您表示歉意之外,实际上我这一次来找您还有一些其他的目的是什么嘞是关于最近唐人街发生的那些怪事等等警官小姐难道你刻意接近菲林士多导演实际上还是为了之前那件事请原谅这是我的工作正如我此前所说唐人街一带发生了许多怪事
```

### [23] hash=`9303502bfbf5c78d`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p11`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（11【喂，跑龙套！】）

```text
而这与数年前在菲林士多导演身边发生过的印象事件极其相似当年的调查显示引发事件的罪魁祸首是菲林士多导演的好友编剧何日君生前拍摄的一部暂定名为《三宴归巢》的电影片花而在数日前您应该和雷森小姐一起在她的房间观看过一部影片您对当时放映的那部胶片的去向有什么头绪吗你是说当时的赖盘胶片您不知道我不知道那天晚上我们观看的影片就算用最委婉的说法也绝称不上是一副有趣的偏花甚至连故事都称不上那就是特里斯拍摄的东西绝不可能也许是她原本的内容遭到了污染基金会的档案中记载神秘血管理品三艳归巢拥有放映与重设两种能力放映能力让她能够将胶片中的内容用类似电影印象般的形式在现实世界中再现我猜测这正是受害者们提到的幻觉、鬼影的真身在放映生效的范围内受害者会被重设现象捕获损失一部分神志和记忆档案中虽然没有明确记载但我猜测正是那部分被重设进入胶片的精神能量干扰了胶片中的原有内容不管到底是谁或是什么东西导致了这一切再猛呆死等等你在说什么
```

### [24] hash=`e9078530def10202`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p11`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（11【喂，跑龙套！】）

```text
解释一下简单的,拜托菲林士多导演并不知道那盘胶片很可能就是三眼归巢他也并没有将它拿走我想,他说的是真的真的吗?好消息对,我还没收到,所以这不是好消息但是,艾特洛罗娃和我之间有什么关系,对吗?这肯定是好消息我们还是在互相帮助Li-Ang说这部电影可能会给你造成一些问题让我帮你找到找到那个妃子然后把电影带回ACD那你会安全我会清理然后在中国城市的问题会被解决那是三个鸟儿一块石头真聪明对吧你知道吗雷什么小姐这就是我最喜欢你的一点言语人际真的事总是很复杂既然他们足够有趣总能够为我提供源源不断的素材和灵感令我着迷但有的时候我也会想也许简单些更好你觉得呢职业人小姐我也有同感我还能再问您一个问题吗关于C07的那些传闻他们哪些是真的哪些是假的我并不认为这些陈连旧事是破获了你手头的案件所必须的不仅仅是为了调查案件也因为我想要知道我之前说我很熟悉您的作品也很喜欢它们那并不是在说谎作为一个曾经的观众这些事情的真伪

对我而言很重要原来是这样那么我想你还是不知道为好我很感谢你对我们的电影的喜爱也许过于接近萤幕后的人并不是一个好主意只享受故事才不至于消磨了乐趣不过作为补偿也许我可以提供另一条你应当会感兴趣的消息
```

### [25] hash=`fffbb03591def173`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p12`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（12【捕鼠器】）

```text
and again it's Poitier have you seriously already forgotten my name it's only beenthree hours what's your status couldn't find anything useful sorry I alreadyasked the investigators who came with me to track down the other missingitems you know to cover up for loggerhead but so far they haven'tfound anything as for the person who stole the item I haven't a clue wellWell, at least there haven't been any reports of arcane explosions or earthquakes.
```

### [26] hash=`7b5dc24d4b930ebe`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p12`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（12【捕鼠器】）

```text
No news is good news, right?What about you?Any leads?Miss Noah didn't take the film, but she refused to tell us anything about its curseor the former owner, He Rijin.Looks like I'm the only one who has good news.You do?What about?The illegal trade of arcane items.And hey, feel free to call me again.Seeing as you're a good customer of mine, here's a bit of advice.Watch your back on the way out of here.
```

### [27] hash=`9321adfbeaa2d657`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p12`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（12【捕鼠器】）

```text
What do you mean?Sorry to interrupt, but neither one of you will be making your own way home.Miss Noah, put dog.I'm afraid you'll be coming to the arcane affairs office with me.Fucking cop!You won't get away!Easy, easy!Then stay down!Ms.Noah, could you show me what he gave you?Go ahead.Super 8 millimeters.This must be it.Reunion of the Three Swallows.He Ruijun's final work.The culprit behind the strange happenings in Chinatown.
```

### [28] hash=`57894634f6fdee36`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p12`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（12【捕鼠器】）

```text
Well, that was easier than expected.Half a day and we've already tracked it down.Now all we gotta do is stop it from doing its arcanemy thing.But how?Smash it?I don't think that's a good idea.I have to admit, Ms.Noah's right.Our king items need to be handled with the utmost care.No one knows what will happen once it's broken.We could make things worse.Fine, let's take these two back to the office first.
```

### [29] hash=`548e4b8fe1f45fd3`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p12`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（12【捕鼠器】）

```text
On your feet, tough guy.We gotta go.How'd you find me?Some asshole sell me out?Wait...You!It was you!You fucking traitor!I should have known you were working with the cops!Huh?Talking about?Wait, let me explain.This is just a misunderstanding.Don't worry, Ms.Scott.You're right.There has been a misunderstanding between you and him.Allow me to explain.You never had the attention of betraying him, nor were you working with us.

You simply gave him the item you wanted to sell.That's it.
```

### [30] hash=`cbb8d8f8173ba3b7`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p13`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（13【A计划外】）

```text
What do you mean the truth was always there hidden beneath the lies and distractionsAll you have to do is whittle them down one by onethe probable cause of the events in Chinatown is the reunion of the three swallows film real andApparently miss Noah has history with it, but miss Noah doesn't have anything to do with the foundationThere's no way she could sneak into the ACD and steal the filmThe same goes for this gentleman or any other outsider.
```

### [31] hash=`9630d58f8faa0e00`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p13`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（13【A计划外】）

```text
So, the thief who wants Ms.Latham to take the fall must work for the Foundation.In fact, since they stole the item without being noticed, they probably work for the ACD.And they must be close to Ms.Latham to know enough about her amnesia to be able to take advantage of it.But lots of people at the ACD know about my condition!You can't pin it on Scott just from that!Too harsh right Scott?How long have you known?
```

### [32] hash=`5dadfa40b2dc6f2d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p13`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（13【A计划外】）

```text
Since miss Latham said you were good friendsWith all due respectYour plan was far from perfect.I knew it.You brought me along so this guy would call me outYou're right.I messed up.My plan was far from perfect because wellI couldn't stick to the so-called plan since the very beginning.I didn't know the foundation was alreadyinvestigating the theft until after I had hidden the items in Loggerhead's room.
```

### [33] hash=`d53dfde9e8f06529`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p13`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（13【A计划外】）

```text
Then I had no choice but to use this idiot as the scapegoat.I never thoughtshe'd accidentally bring the film to LA or that I'd be ordered to investigatethe case.I got in touch with this guy a long time ago and the trade sitehappened to be in LA too, so my plan was to get the film back and sell itAll I remember is that an office lady talked to me in the corridoran office ladyWhen what did you talk about?
```

### [34] hash=`e5ed2c732a16ea3d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p13`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（13【A计划外】）

```text
sheShe showed me something.It was a bit dazzling but very beautifulIt was ohOh, right.It was aStill intact.You've got no idea how long I've been looking for thisYou areHey there kidWe meet againNo fucking way.Is she dead?Not yet, but I doubt she can hold on much longer.I'll call an ambulance, and we're gonna need backup.Why are you doing this?Tell me.I need a reason.It's my old friend that you should be asking.
```

### [35] hash=`667ab1f2cc684694`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p13`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（13【A计划外】）

```text
Long time no see, Noor.Yeah, it's been a while.The last time we saw each other was in front of her grave if memory serves.We really should keep in touch more often.but you've gone too far this time my friend this isn't part of our storythis isn't a set director it's not your car that's the spirit this should be funwith you here little vigil let's all play our roles shall we
```

### [36] hash=`29a58e89cf7e7d8b`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p14`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（14【荧屏正发光】）

```text
Andy SueThe Last Marshmonger强粮寄出网友不为掌门不像样和你讲了多少次要沉肩坠轴心静体松怕就要撑不住了你就太向老师告密了术与练功三心二用你看看你带多了多少以这样的体魄强粮又如何能扶走你继续站我等一会过来检查扎不稳马不今天晚上就不要吃饭了走吧走吧没意思,他又要沾一天了哎,要不要去录像厅?好呀,去接晓那家吧今天他们家放神秘警探C07我也想去录像厅我想起来了那个时候我很讨厌强良什么十二镇子之后,强良之主什么成奸除恶,驱除诡异光宗耀祖,履行使命这些对一个孩子来说都太过遥远了没有孩子喜欢告密者和总是板着脸的小班长当他们成群结队的嬉戏玩闹时我只能一个人在一旁看着假装自己并不在意但其实我也想要跟他们一样两脚那天我没有理会父亲的要求独自拿着积蓄找到了那些孩子说的街角的录像厅那就是我第一次看神秘警探C07她的确很有意思,在观看的过程中,我也的确很开心,但我也知道,电影里演的都是假的,一部电影无法改变任何事,等电影结束后,
```

### [37] hash=`aa1dbe3a1dbe4a27`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p14`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（14【荧屏正发光】）

```text
我还是得回到那个院子里去,我不想回去。所以,直到片中字幕开始滚动,我也没有离开,当那些字幕滚动完后,录像带仍在播放,屏幕重新亮了起来,那是电影的花絮。作为主演的奇星,正接受记者的采访。李星小姐,有很多小朋友喜欢你的作品,将你视为他们的英雄。但另一方面,不少成年观众觉得你所饰演的《警探C07》,每一次都可以击败华人的结局,太过理想化,缺乏真实感。对于这方面你有什么看法呢?你觉得这点是不是《警探C07》系列的遗憾?现实世界已经够残酷,所以我们才会在电影世界里面寻求一个圆满的结局。一个善有善报,恶有恶报的理想世界。如果连在大银幕上,我们都不可以相信正义和公理,那我们还可以相信什么?C07是正义的代言人,是坐强扶弱,康复正义的英雄,无论面对怎样的危机或险境,他都可以带给大家期望的圆满结局。我希望我们的电影和C07这个角色,可以带给银幕前的观众,力量和勇气。或者不是每个人都可以在现实世界成为一个真正坐墙附约的战士
```

### [38] hash=`681f1332baab2c5c`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p14`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（14【荧屏正发光】）

```text
毕竟这条路很难走但我希望可以通过我们的电影和C07这个角色至少令大家成为在生活中为自己身边的人带来圆满结局的英雄那是个夹杂在片中字幕中的很短一段采访但当时齐星说的每一个字我都记忆犹新身为强良之主因驱使显刀兽强良,成奸除恶,驱除诡异,守护世间安宁。父亲无数次的耳提面命中所描绘的,那个没有面孔的形象终于清晰了起来。我意识到,我不仅仅可以成为那个给身边人带去圆满结局的英雄,而且可以成为和电影里的C07一样,给所有人带去圆满结局的英雄。别人也许不行但是我可以因为我是梁家之后强梁之主那份令我不堪重负的诅咒在那一天成为了一份祝福那么是哪里出了错呢?什么?抱歉开玩笑的,Boo,你不要装蒜好,把电视播放在我身上我太无聊了,等着你醒来
```

### [39] hash=`6a4b92a51e73b28c`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
Are you up?I got you guys Chinese food.You must be hungry.Almost 20 suspects in the holding cell were injured.Most were found unconscious at the scene and are now in critical condition at the hospital.The victims include arcane black market dealer Castor and Chicago gang leader Jason the Coyote,both of whom have since been acquitted of their crimes.Cameras out of the way!Out of the way!The ambulance needs to come through!
```

### [40] hash=`7645a60b44e2610d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
We need banana bags stacked!At least people could go into shock!Ah, my skin!It burns!Help!NC!I'll tear you apart, you asshole!Fire is speculated to have been started by a victim of a Nightpiercer attackwho displayed signs of mental instability.At the same time, similar incidents have occurred at the Lieber Street Detention Centerand the Chinatown Police Station.The situations at both sites are similarly concerning.
```

### [41] hash=`2d338595b7b23e42`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
It has been reported that the Division of Arcane Affairsis considering the potential connections between these incidents.The mysterious figure behind the unresolved Nightpiercer attacksremains their top suspect.As with the previous attacks attributed to the Nightpiercer,the victims of these incidents are once again notorious criminals with extensive records.However, in light of the Nightpiercer's escalating criminal activities,
```

### [42] hash=`e049bbfa893a162e`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
support for the figure is dwindling as concerns for safety rise.In response to ongoing skepticism regarding the lack of resolution of the Knight-Piercer case,Deputy Chief Eldon of the Division of Arcane Affairs stated during the press conference that...Fuck, I pass out for half a day and Chi-Shing's already turned the city into her personal playground?Grab your stuff, rookie.We're hitting the road.
```

### [43] hash=`78747816dc12d172`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
Gotta find this bitch before she kills someone.What?Your feet stuck to the floor or something?Deputy Chief Eldon took us off the case.Possibly a result of a mental imbalance caused by the setbacks in her career.She thinks she's the real-life CO7.The hero who fights evil and cares for the weak.In short, we have a vigilante on our hands.Thanks to a minor mistake from the Foundation's Arcanum Containment Department,
```

### [44] hash=`bcc2c421edf06b63`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
we also have a dangerous arcane item.A cursed film reel called Reunion of the Three Swallows,somewhere in the city.Liang has confirmed that Constance Scott, the staff member who was assaulted by Qixing yesterday,is the perpetrator of the theft.As you're all aware, there's been an explosion in mental disorders in Chinatown.We now know that the source is the cursed film reel.It's currently in Qixing's possession, which makes her even more dangerous.
```

### [45] hash=`47d30b4cac9f43cc`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
According to your report and the witness's statements, you failed to summon your legendarybeast when you confronted the suspect.As a result, not only did the suspect get away, but your partner sustained an avoidableinjury.I need my best, most reliable officers on this case.Sorry, Liang, but you don't make the cut.The two of you will be excluded from the operation.Bullshit!He can't cut us out!This is our case!
```

### [46] hash=`f9b19920612e75bb`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
No!We're doing this!Calm down, Ms P-Pudding!Even if you feel fine, the doctor said you had to stay in bed for at least a few days.The name's Poitier!And I'm fine, okay?Stop trying to-Damnit.So what went wrong?How come your friend...Teng Leng, was it?Didn't show up?Qiang Liao must have sensed my hesitation and refused my summon.You see, if its master can overcome their selfish desires with an unwavering heart,
```

### [47] hash=`3ef2359907a24512`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
it can turn on them.Father used to warn me about it, but that won't happen again, I promise.If you say so, what are you gonna do now?I'll continue with the investigation.I need to find Qi Xin.What?But that angry grandpa already pulled you off the case.There's nothing wrong with doing our job.If Eldon bitches about it, just tell him you bumped into the crook when you were strolling around the city.
```

### [48] hash=`f1f5a17a8621206f`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
Seriously?Yeah.Nothing wrong with that, is there?So what's the game plan, huh?What are you gonna do?Again?They must have done a dozen takes already, right?Yeah.I'm no movie expert, but even I can tell the actor's nervous as hell.Of course he is.Anyone would be nervous if they knew a wanted criminal could show up at any time and mess you up with Arcanum.Hilden tried to keep the details of the case a secret, but that director from Hong Kong told her crew about it as soon as she came back.
```

### [49] hash=`ce838526702249d8`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
I mean, I guess they have the right to know.And to run.Half of the extras got the hell out as fast as they could.And look at the other half.They're too nervous to work.I know.Hey, that's the Vigil's cadet, isn't it?What's she doing here?The officers said you're here to help, is that right?Excellent.We could really use a hand right now.Come, let's get you in costume.I'm more than happy to help.But first, I have something important to ask you.
```

### [50] hash=`7162901ba31dde22`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
Right to the point this time.I see.I don't think there's any need to tiptoe around each other anymore.Could you answer me directly this time?What happened between you, Qi Xin, and He Rijun, the creator of Reunion of the Three Swallows?How did she die?Why do you and Ms.Qi Xin both want that film?And why is she doing this?What do you plan to do with my answers?To Qi Xin, I'm probably just another fan.
```

### [51] hash=`6761f803c3c9f564`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
But to me, she and her character mean something.I need to know why.I have to arrest her and find out the truth.Maybe I can still fix things, but Miss Noah,I need your help if I'm going to do it.You mean...you want to know more about her?To peek behind the scenes?Learn what really happened behind all the movie magic?I told you it's not a good idea.We create works not just to express ourselves, but to entertain.
```

### [52] hash=`acbbd0d130be4ce0`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p15`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（15【紧急播报】）

```text
Relationship as fan and actress and treat you simply as individualsSaying I want to know more about you sounds rather beautiful.It's touching reallyI'll answer your questions miss LiangFollow me
```

### [53] hash=`7b19629c3f574d90`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
我们的故事开始在11年前,生命是困难的,就像所有年轻艺人一样。但是,就像很多故事的开始,里面有种美丽的感觉。又一身浪潮导演处女作良相,糊涂虽然抵止极佳,但由于大胆创新过度,导致内容诡异颠覆。即使业内有赚,但大众实在难以欣赏最终票房惨淡收场,实属糊涂那我还有什么好说?没有品味就是没有品味OK,要叫好又叫座有时是要妥协的但问题是我一向最不擅长也最不喜欢妥协Nora?是Nora吗?没想到会这么巧在这里见到你好耐冇见,见返你真系好开心呀你系?Theresa,你点解喺度嘅?你几时返香港㗎?Theresa,or as you know her by何日君was a dear friend of minethe script writer of Detective CO7and the creator of the cursed film Reunion of the Three SwallowsThis is a pretty good script, interesting
```

### [54] hash=`b932095bb173428a`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
我和Theresa在外国学习时在电影学院学习的时候我们在同一系列的写作课堂上我们最初不谈话她总是在自己的角落里我只知道她当我们的教授在课堂上作品的一个例子作者的名字Theresa她的故事能够在细节和大画面之间They were engaging, light-hearted, warm.So in that moment, when we met again at the restaurant,I realized she was the one I'd been looking for.At that time, she was an editor at a small press.I invited her to join my studio,and three months later,she put the first edition of Detective CO7 on my table.
```

### [55] hash=`b0ab366dff05b19c`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
所以你觉得怎样?你觉得哪里不够好的话,我都可以改的。我在想,主角要选谁?噢,你的剧本写得很好,比我想像中重要好。我们就用你的剧本。所以我们有了剧本。但我们无法决定谁会演英雄。We held endless auditions, even considered some famous actresses.But none of them fit.Until that night.头先个几个你觉得点呀?我觉得最后个个好似都OK。唔得,佢唔够sharp。你都睇得出㗎。既然睇得出,就唔好局住自己拣。我唔想将就。但是,万一现实生活里面根本不存在这个完全符合我们想像的完美人选呢?万一他只是我们想出来的,那怎么办?那我就会一直找,直到在现实世界找到位置你…你动手动脚干什么?我就是动手动脚,怎么样?死咸猪手,这里不欢迎你们,还不快点?你…你小心点,我不会放过你的哎呀,这次糟糕了那两个古惑仔附近都出了名他们肯定会回来报仇的
```

### [56] hash=`52da2b14043504d8`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
我知道你看不惯他们对个美女咸猪手但是,人家都不出声了你生什么气?你这样搞之后我怎么做生意啊?唉,这次真是让你累死了,阿星行了,老板,我走了他们再来,就叫他们来找我拿,店铺锁匙你记得早点离开门不然那些熟客等得慌纠纠阿声,你……看来你刚刚失业谁呀?关你什么事呀?我有份工作介绍给你你对演戏有兴趣吗?阿声惊讶当我做了提供她说她需要思考所以Teresa给了她一份笔记下一个天,她打开我们的门,并取得了提供。后来,我们学会了阿升是一个很差的家庭。她的父亲在牢笼里,她母亲也有心理问题。她从小就为家庭成为了生意。她父亲的名字常常会把她带进困难,所以她通常都会在工作或战斗中。你所见的C-07她的脸上总是有着自信的笑容但实际上阿升一开始就几乎没笑过一位演员应该学会向摄影机前面的那一刻并回到现实之后但阿升没这样她没回到现实她从那时开始从没停下C-07的角色24小时一天7天一星期她开始笑得像C-07一样她从脏脏脉脉的
```

### [57] hash=`2a4f74af0881d3fe`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
到蠢蠢脉脉的就像C-07一样总裁和BAU做错了一个错误阿升并没有把自己与她的角色误解在这些年来在电影计划中我见过很多演员被他们的角色的蠢蠢蠢脉脉脉的但阿升是不一样的她甚至比自己更值得称呼CO7甚至到最终她自己的意识被反射了梁小姐你问我CO7和我们三个人是否真实现在我可以给你一个答案他们都是真实的我们在CO7的推出后很注重了很多东西把任何人的眼睛都放大你都会找到不完美我们绝对不是其他人阿升和我一样固执和不可思议的当我们不同意的话这会变成了一个很大的争议我们也不会给予其他人可惜Theresa总是被中招我太年轻了太固执了以致这可能会导致的影响我向前走了一条路常常在我身边的那些人都忍不住Theresa, on the other hand, was kind-hearted, perhaps too much so.She never got angry, no matter what people said.
```

### [58] hash=`8c57d10716317f6e`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
She just bottled it up inside and let it eat away at her.She didn't like taking photos.She was self-conscious about her appearance.So we only have a few together.This one was taken when we were shooting CO7-2.We were so close back then.当然,我们终于知道我们必须抛弃但我们并没有对此感到担忧当时,我们的短暂开始伤害我们的关系但当我们发现了,伤害已被处理这个结局太离谱了C07不会这样做的当我们在制造CO7-3时OurSingh在结局上担心了In the sequence, CO7 tracks a criminal through a sure-whore parade, hoping to finish him off herself.
```

### [59] hash=`cbdf7d539a7c2175`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
But when she finds him sitting at home with his family, she changes her mind.Ah Sing didn't like it.She said that CO7 would punish the villain for what he's done, that she would never change her mind.We had countless arguments over this ending.And of course, we never reached a conclusion.行了,到此为止,我们这样吵下去也没意义。我有个提议。并且一起选择了最好的一位她答应了但她没有保留你的奖项她发布了一部电影跟原创的结局相似虽然这部电影很受欢迎但我认为是一场骗局在第一季她宣布她将会离开新的艺术公司是我们三个组成的
```

### [60] hash=`c116f7c9c70fa14d`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
我并没有阻止她Theresa尝试以我们的关系为主就像她一直一样我写了个新剧本不是C07续作,是全新的故事如果你们觉得有意思的话我们下一部电影可以拍它我自己拍了一部片花虽然很简单,可能拍也不太好但是,可以的话,我们一起看这就是她的概念证据在《三个河流》中的合作我知道Teresa总是想把C07系列结束并写下一些她非常热爱的书她可能以为一部新的故事会帮助阿升离开CO7并重新变成自己可惜当她来展示了剧本阿升和我正在争斗中不用了我不会再跟你们拍戏阿升一直对Theresa很友善但当天她把她推出门口并暴露出现while I...well, as I said, I was a jerk.I flipped through her script and a flurry of harsh words left my mouth.点解仲系上次𠮶个类型㗎?我咪讲咗啰。呢种故事唔啱你写呀。In the end, neither are Seng nor I cared enough to watch Teresa's sizzle reel,
```

### [61] hash=`3a6f31bc50a05df7`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p16`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（16【小人物纪录】）

```text
even though she tried so hard to present it to us.That was the last time we saw Teresa.原来的那是Teresa给我们送来的那些年前的这是社会派对的贴纸吗快要是复活节了这几天一切都快忘了了等等是否小姐会你的猜测比我的好
```

### [62] hash=`e7e3c55dea3f8716`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
Wow, look at all these people.Oh, we should have come earlier.I can hardly see a thing from hereAnd whose part is that?You are the one who took ages to get readyAnyway, at least we haven't missed muchLooks like it just started.I heard there's a new event this year.I wonder what it isNot an event.A film crew is shooting a scene during the paradeApparently, they already talked to Mr.Shao and said they wouldn't cause any trouble.
```

### [63] hash=`3c33a2a37950813a`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
Let's go check it out!Maybe we can get into one of the shots!the meaning behind all this but what I do understand is that this is one of themost important events of the year for the people of Chinatown the target couldstrike at any time so we need to be prepared no one wants to see acelebration turn into a nightmare why didn't you see that to your man theyare the ones who've ignored the Chinatown all this time what a
```

### [64] hash=`5cf0304b1239c6dd`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
Oh, Chris.Aiyo, Uncle Chow.Today's our big day.That sour face of yours is gonna scare this guy straight off.Leave the past in the past, la.They are doing this for the right reasons.What we've got to lose.Besides, we could really use a hand right now.They can make up for our manpower shortage.Now, give me a big smile, la.Before your long face scares off our good fortune.the residents to cooperate with us.
```

### [65] hash=`812656b31bd88310`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
You are welcome, sir.Even though I only came here a few months ago,I've already gotten pretty close to the residents.So, it was pretty easy to convince everyone.Don't worry about it.Besides, the Sun Ho Parade is for everyone,whether they're here to watch or dance.We are always happy to have more peoplejoin the celebration.Yeah, but, it'd be weird to stay in my room alone when everyone's out here, don't you think?
```

### [66] hash=`e577896e0cee7477`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
Anyway, I'm waiting for Scott to wake up from her coma.I want to ask her why she stole from the Foundation and pinned it on me.I need to know what she thinks about me and our friendship.If I let you guys do all the work while I just wait in my room,I won't be able to question her without feeling insecure.I know I might not be all that helpful, but I'll do everything I can!Miss Latham's being modest.
```

### [67] hash=`f8eff277fe14edfb`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
As a staff member of the Arcanum Containment Department, she knows how to deal with that film reel better than any of us.She may forget things, but she still has a wealth of knowledge.Her experience might just make the difference between failure and success.Alright, you've got a point.Let's slay them.Thanks for lending us your expertise.Just leave it to me.I can deal with the film.I've rewatched all my related memories so I remember every detail, even down to the scratches on its surface.
```

### [68] hash=`c582a0e29ef7ed01`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
There you are.Everyone was gone when I left the changing room.I thought something was...what's wrong?The costume fits you well!Fancy!It doesn't even look like a costume!Much fancier than that!You are like the best parade dancer I've ever seen!There's no way the Night Piercer would spot you!Look at her!Uncle Zhao!So cool!Is that the Leon's family retro dress?Let me see.Good.You are wearing right.Nice to know that at least some kids remember their traditions.
```

### [69] hash=`7596f33e070cac2d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p17`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（17【夜游者】）

```text
You better not dishonor your family wearing this, kid.My thoughts exactly.Everything's in place.You sure you can perform this time, Vigil?I don't want a repeat of last time.The alley outback's empty.Show us what you got.Yes, sir.I'll prove myself to you.They'll check on me move carefullyLooks like I've got nothing to worry about you're ready kidBraid starting soon.I'll go get dressedthe rest of you I

Need to talk to miss Liang.Could you give us a moment?Don't be late.Why me miss Noah?
```

### [70] hash=`34b5312868668831`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
of her expression, she'd take as many shots as were necessary to get the scene right.As you know, I was a perfectionist, always taking it too far.Many of my crew quit halfwaythrough my projects.Even Theresa struggled sometimes.She told me more than once thatshe couldn't do it anymore.Only Arsene could keep up with my pace.In fact, she'dsystem should be almost unbreakable.So how is it that Miss Scott, a regular staff member
```

### [71] hash=`b15607310b340eeb`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
with no special skills, managed to break through it?And why was she selected to goafter Miss Latham?What was she about to say before that needle pierced her neck?Using's actions don't make sense either.After all these years, why has she decidedAll I know is that, if Ah Sen continues down this path, there will be no happy ending for her.I understand that she's trying to reach something she's always strived for,
```

### [72] hash=`53944a1b145ac8d4`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
but whoever's orchestrating this won't let her get it.I've done that to her before, and it was a huge mistake.I won't let that happen again.What are you going to do?Since coming to Hollywood, there's one thing I found difficult to accept.The producers always stick to the script.They're obsessed with it.Changes are incredibly rare.But that's not how we do it in Hong Kong.The script's finished, and so what?
```

### [73] hash=`abe4fa6535f148eb`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
Things will always come up during shooting.You have to be flexible if you want to make truly great art.If a moment of inspiration were to strike meand I weren't allowed to add it to the movie,then you may as well just kill me there.You want to change the script?Precisely.But we have a small issue.As you can see, I'm not exactly readyto jump to my feet and into the action.I'm better at working behind the camera
```

### [74] hash=`7b1bffdb423c5438`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
than I am in front of it.So, I need a protagonist,one who's as eager as I am to change the scriptand find that perfect ending.Are you interested?It would be an honor.Xing appears.Close in and arrest her as soon as possible.Alright, Noir.The time has come.This will be our final scene.That light's so bright!Whoa!I'm feeling kinda dizzy.Mommy, I'm scared!That arcane fluctuation, it's from reunion of the three swallows!
```

### [75] hash=`03c166ff1cb60e2d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
How does she-Move carefully.Please stay behind me.Happening!That thing's nothing like the critter you're used to dealing with.What were you thinking rushing like that?You're totally out of your league.I was about to attack.What else was I supposed to do?Tch.They look like ghosts, but there is something different about them.So, little ghost hunter, can that machine of yours tell us what they are?One second, Uncle Zhao.
```

### [76] hash=`239ad6d738bc792b`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
Li Li's working on it.I was a leaving man, so?It's got confirmation that this thing is covering the whole of the footers of the beyond.One of our king creations, but it's breaking apart for a while, but then they're back together.Sorry, not my type.Everyone keep calm!Groups A and C, protecting the public is your top priority.These things seem to follow anything that moves.Lure them away!Mr.Lee, Mr.
```

### [77] hash=`0b35a4514fa34443`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
Joe!Gather as many civilians as you can and guide them to a safe place.I'm sure that should help.We won't let you down.B, hold your positions.Target's probably trying to distract us with these monsters.What's your status?Report immediately.This is Fortier.Same thing's happening at the rear of the parade.Roar is signed though.Keep it that way.The rest of you keep your eyes peeled.The target could appear at any time.
```

### [78] hash=`23c0f858994dffce`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
Camerahead, any idea what's going on?Chinatown's been sealed inside an arcane barrier created by the film.Nothing in the records about this, but these arcane fluctuations are definitely from the film.What about those ghost things?I don't remember the file saying it could spawn spirits in a thin air.Well, I don't know.Reunion of the Three Swallows can play and record, that's for sure.Even if its power has been enhanced somehow, it probably wouldn't develop a completely unrelated ability.
```

### [79] hash=`4add4c1fecfaa0b5`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
You are right, because it's not unrelated.Remember the fiend's victims?Part of them was taken away by its record ability.What they lost was part of their spiritual energy and memory.Their Samuan Te Pa, or Three Souls and Seven Spirits,were the Samuan Te Pa of the victims.They're the victims' spiritual energy?But how did the film do that?I'm not sure.Lili's never wrong.We'll never get there, so...Essentially, she's holding everyone in Chinatown hostage.
```

### [80] hash=`18dac710ca6df649`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p18`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（18【因果定律】）

```text
We certainly weren't expecting that.I didn't want it to come to this.This was between me and Noir.But you just couldn't leave it alone, could you?So here we are.Sounds like you already know what this film reel is capable of.Good.Saves me the trouble of explaining it.Now, bring me Noir.
```

### [81] hash=`7a7d0a5c4edcd4e3`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
Target spotted I repeat target spotted what's going on?Who are they?impressive night piercerThis is a whole new level even for youTell me what did you pull to take control of that film reel?I didn't pull anything officer it chose to fulfill my wishThat's all never wanted to get innocent people involved as I said beforeThis is between me and warPoitier?What are you doing?I told you to hold position.
```

### [82] hash=`450c4e2abd320b79`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
Please don't blame Officer Poitier, sir.I forced her to bring me here.What the hell are you thinking?It's time I put an end to all of this.No need to worry, officer.Our reliable vigil will keep me safe, isn't that right?Yes, of course.I will ensure Ms.Noah's safety, Chief.Leave it to me.Keep the target in check, Liang.James and the others are working on how to break this barrier we're in.And that ghost hunter helping them.
```

### [83] hash=`c96fea7144ebabae`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
Stay calm.We want to resolve this peacefully if possible.Haven't forgotten what you learned in negotiation class, have you?Of course not, sir.I got straight ace.Guard up, rookie.And straighten your back.I get why you want to wear this outfit,but you can get things done with or without it.Isn't that right, partner?Right man, I won't fail.Okay, director, our last scene is about to start.Did you see that?
```

### [84] hash=`892520b1044c5bf4`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
So many failures.This is what we have done.This is what the film looks like now.Those dirty, disgusting, and evil thingshave polluted the last piece of his life.These filth is our evidence.So what do you want to do?But until now, Teresa is no longer here.In reality, you are only a representative of justice.Punishing those evildoers in your eyes,will this make you feel better?Now you plan to kill me.
```

### [85] hash=`3d2bec0aed9d4e2d`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
And then?This is your way of getting used to it?If this is the case, then I'll be honest.This is too biased and too childish.Not getting used to it?It's not like that.You are right.The one who treated me with no fear,who cared about me more than his own mother,is dead.I pushed him away in my pain,and let him die in loneliness and pain.Now, what's the point of atoning for my sins?I'm waiting for a dead person to be moved,
```

### [86] hash=`3b28e2e01a24abb1`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
and then say,I forgive you.It's just self-satisfaction.Since you understand these principles,Why can't you let it go?C-07 is a hero who brings a perfect ending to the people around him.But Miss Magic Star, what you're looking for now is not a perfect ending.A perfect ending?It's what I said in the second ending sequence.Chen Lanwei, you still remember.For me, there is no more perfect ending.Maybe you also know that after He Rijun's death
```

### [87] hash=`de0774bbb8c90fb2`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
After I left New Art, I went to other companiesand worked with other directors to make a few movies.But none of them were successful.It wasn't the ticket office problem,but I wasn't satisfied with myself.I couldn't find the feeling I had when I was shooting C07.Those shots, those pictures, those spotlightmade me see a kind of physiological smoke.I wanted to puke, I wanted to scream,I wanted to run away.
```

### [88] hash=`e22efef5b2ad5526`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
So I said goodbye to the screen.But the feeling of being left behindwas always with me.No matter where I went,my soul was still with me.So I started to thinkwhy would it be like this?Why would the plot end up like this?Why would I end up like this?I thought about this questionand thought about itI realized that everything is a mistake.So he must be corrected.Director Felicity, please step back.All our countless choices have led up to this moment.
```

### [89] hash=`83f631cabaf1fb05`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
But not all of those choices were made, willingly.No, some of us had no choice but to fight over scraps in the dark corners of society.This time though, it is my choice, my own will.But I'm fortunate to have you playing opposite me.I can see it in your eyes.You're not playing the role of a hero or an officer.You're yourself.What about you?It's playing the role of a murderous villain.Really what you want?
```

### [90] hash=`b8b02dd6a092fac1`

- lang：`en`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
The answer to that is yours to find out now, Vizsar.Filch are complete.Move carefully.Please stay behind me.Loading.You won't get away.My responsibility.Aim and shoot.Faraday's miracle.Don't leave your friend stranded.Her lives are in your hands.What I'm good at!Damage.Another addition to my collection.Soon, you'll all be tucked awayin my filming.Stay behind me.Relax, no worries.Looks like there's no stopping you.
```

### [91] hash=`a460ff1d859555ba`

- lang：`other`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
In that case, I'll make you stop.the power charging light that illuminates the target target confirmedloading for you loving your power child of scienceexistence and face reality no matter how hard you try you can't change the past oh little vigilthis isn't my curtain call not yet watch outWe're running low, sir.Must be gaining power from this area we're in.都根本没有意义!怎么会没有意义呢?所有的故事都必须有个结局现在的我无法感知当下也无法前往未来
```

### [92] hash=`4765a7727dac04aa`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p19`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（19.【恶与善的挽歌】）

```text
过去囚禁了我所以我必须给我的过去画上一个中指腹圆满结局道数强良?你还没有炼送那个咒语?这一次我不会再犹豫你不会再动摇I used to dream of you, and I used to save you and C07.Because of that, I will stop you.Strong and strong, netizens protect, kill and rescue, eliminate and destroy.
```

### [93] hash=`25402a68f52c262b`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p1`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（01.【新警局故事】）

```text
相传商周时期,天地间痴媚亡两横行,有恶兽围获人间,令神州萧条生灵涂炭。幸有大贤方香氏受天子之托,向十二摄提神请愿得巫武之礼。降伏恶兽收为己用,名为显道兽。显道兽得社体神赶照,化为驱逐世间诡异,护一方安宁的神兽,得万民敬奋。然之,唐末时战乱平起,回首显道兽之传承延续,最后的方向是在先去之前将其分别托付给十二镇子。其中,显道兽强良,壮虎贤蛇,凶悍无凭。得强粮之人后以兽为名改姓为梁世代相承时至今日虽说世间已不再有妖魔肆虐梁家也已不像过去那样风光但家族上下都始终牢记祖训手里刻记秉公持正将为世间承奸除恶视为己任翻开家谱每一个名字后面必定都是一个行得端坐得正响当当的梁家子弟然而显道寿强良却已有近百年未曾显身了直到你我最引以为傲的女儿直到你再一次唤醒了强良你可知子气肩负着何种重望我知道的爸爸你就相信我吧请您相信我我一定会完成强良之主的使命绝不会辜负家族的期望准备好了,Ding,因为我接下来要告诉你的事情
```

### [94] hash=`8439d3076cbbb0e8`

- lang：`zh`｜version：`2.5`｜arc：`唐人街影话`
- doc：`BV1imwueSEQm_p1`
- title：《重返未来：1999》2.5版本「唐人街影话」全剧情 - Reverse: 1999｜4K（01.【新警局故事】）

```text
将会让你失望给我一杯咖啡我先去找我们的判刑抱歉吗?我还在这里我只是一名财政官我付了你的薪水,所以你不要吵吵闹闹去做你的工作真是双流不正下流灭又是他?他在这次的事上在抱怨什么?呃,在我们在中国城里搜寻一只狗的时候我失踪了我送他去看狗狗警察我知道,这不是我们的工作然后他就对我们说话很吵闹然后我回头就跟他说了这件事你记得那小伙伴看见那小伙伴吵架就吵架吗结果就像是一种传统的中国按摩当他们把案件弄清楚了那小伙伴的父母就吵架了但就像是,来吧这简直是小伙伴的错误他道歉了,然后他们原谅他你以为这会是问题解决,对吧?但这家伙却不让他走他根本不关心仍然如此,我猜他嘴里留下了坏味道我只是不明白他为何在我们身上抱怨我们找不到失去的狗,我们找到狗狗至少,大部分人都很友善对啊,我只是想要好消息那怎么说有什么好消息抱歉,我没有那种特殊的味道正是相反的我猜猜Vigilante再次遇上了Vigilante的Nightpiercer
```

