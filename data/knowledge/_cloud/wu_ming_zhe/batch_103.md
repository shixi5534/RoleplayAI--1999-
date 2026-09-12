# 剧情图谱抽取 · batch 103

- 角色：`wu_ming_zhe`
- 批次：**103**（未缓存补漏批 4/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_103.jsonl`

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

### [0] hash=`ce2b663726dc5952`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
with that amount of resources of course you'd find something dumbass even abroken clock's right twice a day he batted if you want you're gonna smashthat dead end head-on I don't see why you're commenting on my work we're noteven in the same department you use my materials that was most of thenuclide are from both the class and the foundation you have to be kiddingYou get all you want while I'm here like some chump filling out endless forms just to get a few drops!
```

### [1] hash=`ad59e233f10c2728`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
Next time, just give me the funds and Nuclide,and I'll be more than happy to run a few laps in the storm with that crap from the satellite and see what happens!We would never endanger the life of a researcher like that.That's why we should launch another satellite!No need to risk anyone's life, especially since we got plenty of colleagues with aeronautics experience.Those sneaky researchers at Institutum Lawrence are going to get ahead of us
```

### [2] hash=`bf55bc697da968b7`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p9`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（09.战争与和平(关于如何理解每一位拉普拉斯人。)）

```text
Lawrence is that strange secret society?Let's see what kind of ball they're spouting this timeNo medicine pocket.Just toss the letter into the shredderLadies and gentlemen, my apologies for interrupting your debate.The st.Pavlov Foundation has passed a new resolution
```

### [3] hash=`f4cdf07da6cd741b`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Hey, is that gal really coming?You really think she'd announce a plan stealing to every living person before she acts?And she even made a security plan for us?Well, I'll say, she's either a maniac or a freaking crime genius.It is mine now.Are you satisfied with the answer, Miss A.C.?One last to go, Melania.The Remit Cup.Now does anyone not want to visit the Rimmick Cup?Raise your paw, please.Alright, it's unanimous!
```

### [4] hash=`b877fabbdbfb3acf`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
New Humans is a robotics company doing the right calls.They have never failed any mission as a security.I'm sorry, Mr.Iverson.Actually, I didn't know my entrance would be so straightforward.Catch them!I can't believe someone has found me.Am I exposed?The puppy is asking for your help.All right, puppy.Let's make a deal.Humans Company announced they'd offer another reward for the 13th International Jewelry Show.
```

### [5] hash=`6a7ef9b3412e564e`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
The company claimed that the person who filches the heart of London can collect a £1 million reward at Number 15 Bond Street.Tribal news sources reveal that several people have failed and been arrested, including bignames like Greedy Jack, Crime Duo, Pain and Drizzt, oh, excuse me, hello, in the newsof today, grab a copy.Are you talking to me?You've turned around, that's to say, you're, sorry, my, my bad, I didn't notice
```

### [6] hash=`43b6ea734909eda3`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
your uniqueness.No need to apologise, warm-hearted child.Could you please read me the news of the day?I will pay appropriately.Sure, my generous lady.Please, sit right here to get away from the crowds.Hope you don't mind my raspy voice.London faces severe public security issues.Approval rating might drop.Cafe prepares for motorcycle road racing.Government failed to halt.Rock pirate hijacks radio frequency, claiming fun is about to begin.
```

### [7] hash=`fbf1ee1effedd6e0`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Artistic recon street.Police warning over colourful bubbles.That will be a fantastic plot to start the story.We are here with full sincerity, Sergeant William.Certainly.You made all our headlines.Londoners know what you've done.However, your proposal for security companies in maintaining the security of London doesn'tconform to the principles of law enforcement.What's more, the public is still alert to security companies.
```

### [8] hash=`9db9087017fc06ae`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
You know, after the Ramirez incident, people no longer trust security companies.Ramirez?Oh Jesus, why do you compare us with an arcanist company?They never make any security plans, nor do they resort to weapons or force.The only thing they have is the stupid brainwave which definitely brings all kinds of trouble.They even claim possessing the imagination that goes beyond all thieves.Good heavens, do you believe that?
```

### [9] hash=`35c6f81bfc69df85`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Why would a security company think as a thief?Well, hard to believe though.They did create many miracles.formulated guidance on security.This is our latest product, Security Control Type 1.It carries abundant security measures, including tear gas,end-dive worm powder, magnetic interference unit,and can detect any threat within a radius of five meters.Most importantly, it is fully under controland reacts to emergencies with 173 in-built programs.
```

### [10] hash=`10d1f3f9e162c472`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
I think it is a reliable helping hand of our police officers.Just like now.If we switch on its sensor...Suspicious invader detected.Location right under the first office desk.The second, the third, the target is moving quickly.Is it going wrong?It never goes wrong.Hey, hey, gentlemen, and this very sensitive robot friend.Hello?You, again?Where's...Thompson, get in here and kick him out right now!Wait, wait, I just want to talk to you about the watering car, look.
```

### [11] hash=`1ed7cfa6affc44ed`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
I've told you a hundred times, nobody ever cares about those god knows what pop elements.Pop, yes, pop!You just spoke it out!Currently, Pop is still too avant-garde, so I'm very glad to meet someone with the same taste.That's because you've tediously repeated it for ages!So you can understand our philosophy, and I believe others will...I get it.This is a malicious rule-breaker.Such kind of violation can be tackled with by the security plan installed in our robot.
```

### [12] hash=`0df0cc82b321fd85`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Sergeant William, here is another reason why London needs our robot.Puppies are friendly, lovely, and they can read your mind.Oh, such a lame idea.Some people don't like those plushy quadrupeds.It's so difficult to get their hair off our nose and clothes.Oh, and their smell stinks.Sergeant, now I will present you Security Control Type 1, Moralization.It has an all-round precaution plan installed for all citizens.
```

### [13] hash=`df1e721985edd456`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
And, of course, it knows how to cope with you hooligans.It doesn't rely on some impalpable imagination.Totally controllable?For sure.Hey!Malfunctioning, you iron monster!Keep away from me!What's in your hand?Put it down!That's rude!We want peace, not war!As you've seen, Sergeant William, our robot excelled.According to our research data, new humans is winning the public.People trust robots.They are looking forward to a safer and more peaceful London.
```

### [14] hash=`16e36bc0a7dd89e3`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Wow, the talent Mr.Robot just presented is stunning.Please don't believe the nonsense he just said.London needs imaginative art parties.It needs street fairs for everyone to get their voice heard.London is utopian.I will throw a feast for more people to have fun.By then, our philosophy will hit the headlines of all newspapers and become a new tidal trend.Everyone will get to know and fall in love.
```

### [15] hash=`75b76f3044d492c3`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Really?But we only receive countless complaints.About you particularly.Uh, uh, people just need some time to digest.London has been in chaos for too long.We need to thoroughly and completely root out all dangers and threats.I'm in total agreement, Mr.Iverson.I think New Scotland Yard will further consider the importance of security robots in London.Disapprove!This is a violation of civil rights and a defiance to liberty!
```

### [16] hash=`4e6f10861155f843`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
The heart of London is gone!It's beautiful.This is what Father used to protect.But, it is mine now.The robots can't tell real fire from fake.Just a few sheets of nitrate flash paper, they'd turn on all the fire sprinklers loyally.Then, a steady stream mixed with slug essence from the fire water reservoir gushed outof the sprinkler heads.Miss Acie, did you see how the robots were glued to the floor, unable to move?
```

### [17] hash=`9b56a074fa45acd9`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
If they had emotions, they would have cursed me to death.Are you satisfied with the answer, Miss Acie?one last to go Melania what a strict mentor no worries I will get back to thehotel as planned right on the dot the next stop is from 1132 insomnia 90 hotelget to Regent Street take a rest on the bench at the fifth flowerbed for threeminutes and 25 seconds then turn into the lane next to honey candy house miss
```

### [18] hash=`9da6e908bdadfa8f`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
AC on your right fire engine bubbles is this the latest way toextinguish fire but why is it here oh the bubbles not good leave only threeminutes left I must go now don't stand in the way hey that's not theThat's a ski resort on the snowy mountain.Best place for vacation.Elders and youngsters, friends who are passionate or reserved.Welcome to the bang bang frisbee rock and roll party.It's an improvised and liberated event of art that everybody can join.
```

### [19] hash=`23717b6e45e2f40d`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Utopia, where you can totally voyage far, even with myopia.This is our world in the future.Yeah, who's this a knob head causing traffic jams on my wayThere's no timeTake it easy.Just fix these balls.There must be something that worksdisguising capssteeples hiding cupsThe smart detergent gunTwenty-three detergent bottles at one shot.In a flash, it will make this place shiny as new.Perfect answer.Give me back my empty streets.
```

### [20] hash=`745b792cb7edc283`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Don't.It's super absorbent.Oh, my adorable bubbles.Look how you embrace each other enthusiastically.Take it away.It is the summon of uterbi.The revelation of terpsichore.You've sorted out a roadmap of all the blocks in London, you need a new plan, a bold new plan.What is going?Your magazines, your handbags, everything!Celebrate!Hey!That's my magazine, what are you doing?What are you going to do with Miss Acie?
```

### [21] hash=`51084627b47d0633`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Back to me!Watch out, he's mad!Plan A.Plan B.The show's on, Howard.A conventional choice.A nice party.Time waits for no one.Even for a great people.Jeez!I can't tell his strength just from his appearance!Well, um, Miss Melania, thank you for your, uh, bewildering variety of gadgets.I would have been in trouble otherwise.If there's anything I can do for you, please let me know.You really want to thank me?
```

### [22] hash=`0f68bba7890dece6`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Uh, R-Rest In?Maybe you could take your chances there.A better choice would be Insomnia Nighty Hotel,but apparently the way there is blockedby the stupid fire engines.Rest In is around the third corner,down the lane from here.By the way, stay away from those nutters dancingin bubbles and keep an eye on your handbagso you don't end up like me.I managed to grab it from the news agentsand this is what happened.
```

### [23] hash=`70cc5497e16fe1c2`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Oh, my Rimmet Cup legend.I bought it for my collection precisely because of the column topic in this issue.The Rimmet Cup?Yes, you know it too.The same trophy that was won by Brazil four years ago.It's suddenly missing during the exhibitionand was replaced with a counterfeit by a thief where nobody knew.The security company failed to do anythingand thus paid out a huge compensation.The genuine thing was only found in the trash months later.
```

### [24] hash=`b817df629f09f15c`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
That legendary trophy has now arrived in London.It will be the most wonderful award given to the winner.Whoa, have I seen things?This is actually a celebration party for England,and it's the biggest ever!Pickles, Pickles, come on!Mr.Charlton, are you alright?It's March.Still quite a long way to go before the World Cup final.Is it?Thank you for reminding me.I need to tell Pickles in case he goes there for nothing.
```

### [25] hash=`2a8d634315d08d2d`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Pickles!My little Pickles!He shouldn't have let his guard down.The bubbles from the fire engine must have been turned into a sort of life form by some specific incantations.Poor Mr.Charlton.I suggest you try some of this, Stinky Mud Freshener.It cleans the air nearby with its brutal destructive power, only with a slight side effect.Oh, I feel so much better now, I almost couldn't breathe.Thank you Miss Melania, God bless you and have a safe journey.
```

### [26] hash=`f65f9898c18e7944`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
You're welcome Mr.Charlton.I think the Stinky Mud Freshener would suit you better.God bless you to find your little pickle soon.The Port of Aze Cafe faces the North Circular Road.It is around 4.803 miles from the destination.Captain Regulus drives at 65 miles an hour.Given the rules of the racing, she will arrive earlier.There is a lovely puppy!Hello Mr.Puppy.Look a bit nervous Mr.Puppy.Are you hungry?
```

### [27] hash=`3d8f87af22ba73a5`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Perhaps it is not a good time to fall.Please don't show me your tongue at random.Makes this apple feel stressed out.Captain, help.Your eyes seem to light up when I mention my captain.If Captain Regulus finishes the racing trouble free, I might introduce you to her.But now, let's stay away from each other, puppy.It seems you are quite interested in Captain Regulus.Wandering across high seas, she is a great pirate who never gets caught by all the Orwellian and the Conservatives.
```

### [28] hash=`9f333a5e6379ed04`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Is my explanation precise enough?Hope my wording meets Captain's requirement.I think you will like her.Most of the time we are wandering in London.Captain is fond of anything novel and funny.I am sorry little puppy, I have to go.Captain Regulus seems to be in trouble.I really enjoyed our conversation.Hope I can fully understand what you say next time.Or maybe I can invent a tool to help us communicate.
```

### [29] hash=`366558aca20a35e6`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
See you, puppy.Bark bark.Freeze!Routine check.Your fire engine driving licence please.Hello, Mr Officer.Again?Within a month you visited the police station 13 times.Stirring the pointersa Big Ben, dawdling at 10 Downing Street, dying Tower Bridge with waterproof paints.This time you threw a messy street party, didn't you?It was not a mess, police officer.You're suspected of breaking traffic laws.It's reasonable for us to arrest you right now.
```

### [30] hash=`c8f65766f659b22b`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Wait, police officer, what?What I did is legitimate.I've applied for the use of fire engine to the sergeant and got approved.Please, feel free to check, Mr.Officer.Can't believe the sergeant would approve such a ridiculous application.That's what he approved.But how are you going to justify those weird bubbles?Which one are you referring to?The laser bubble that reflects people's dreams?It caused all the people at the square to fall into a deep sleep for two whole days.
```

### [31] hash=`1470d3e6f5317ac8`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
They experienced the most unexpected but best holiday ever.Honestly, I really envy them.Or you mean the classic work of mine, the Reverie Bubble?If it's convenient to you, could you please disclose the feedback of other officers?I need some inspiration to revise my formulas.What did those officers see when they enjoyed my bubbles?Surrendered criminals or......remotion announcement?Enough!This time we will absolutely find out the odd ingredients in the bubbles.
```

### [32] hash=`7dee35c3c93f1ffc`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
You can't deceive all of us.Only if you guys can open the water tank.At least up to now.You don't have enough evidence......Mr.Officer.Fine.I now ask you to cooperate with our investigation as the witness.Ugh.Alright.Cops shouldn't be wearing such ragged clothes.What?This is a demonstration against the materialistic life, the Code of Freedom!Ahem.Though you didn't mistaken me with those stupid cops, I still suggest you better distinguish us.
```

### [33] hash=`9078b49316de30d9`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
You were a suggestion!There are some slight scratches on the codes.The transmission system functions well.The braking system is not very well.It's an apple!Your vehicle looks fine.Captain, are you alright?I'm not!I could have won this, but it all went to pot!The Ragged Lad ruined my game, my chance to be a podium winner!He ruined a rising racing star!Ahem.I need to warn you again that any defamation might cause a lawsuit.
```

### [34] hash=`c778d9a86a7ba360`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
Hmph!For fault?You broke into the trap, Ragged Lad!Sir, the lawsuits you were talking about, are you referring to those who are approaching?What?Bloody hell!They found me!Carnaby Street, call for backup.According to the latest update from Sergeant William, his seal has been stolen.The suspect Diggers is suspected of committing a series of crimes,including illegally using fire engines, forging police ID, attacking police officer.
```

### [35] hash=`8eb1310001e5d715`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p13`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜1~4）

```text
We also found someone illegally held an MRR competition on the street, and the suspect is likely Regulus, the rock pirate on the wanted list.You two!Freeze!Co-operate with our investigation!Alright.Maybe.If all his statements are to be believed.Do you remember what he said at the end?He told us to read tomorrow's newspaper.The headline.
```

### [36] hash=`201e34c9dc3ee048`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Finally, I'm back.25 minutes and 38 seconds?I can't believe I'm 15 minutes late.Blame it all on that bloody fire engine.Still need to work on your flexibility.I'm trying, Miss A.C.Now, the final step.Yes, the final step.Take a photo of the reunion.Although there was a little challenge at the end, I was able to complete the answer sheet successfully.What if I enjoyed the photo shooting?Twitching eyebrows, stiff smile.
```

### [37] hash=`3c6342dd4ffef6c1`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
You'll like him.No, I'll be better, Miss Acie.Unpredictable imagination won't be enough.A better plan with more details is also required.I won't let go one single minuteuntil I accomplish the ultimate goal.I became a thief late in life.So I'm not yet good at dealing with emergenciesbeyond the plan.At least so far,I've given the correct answer to every question Father left.These are what Father used to protect.
```

### [38] hash=`f0d5b8074b9dc999`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
You've done a great job.Thank you, Miss Hasee.There's only one question left.The key question.The Remick Cup.If I recapture Father's memories and glories,is it enough to make up for his regrets?Father, will he understand me?Maybe you should meet him.It has been some time.When the company went bankrupt, we couldn't even afford a decent cemetery.I wouldn't be surprised if a few wild animals jump out of nowhere in this desolation.
```

### [39] hash=`844c2021a7c5d7dc`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Excellent judgement.Critters!It seems they've made this place their playground.Three, this is not the shiny crappy vault.It's on an important mission.Be careful.Two, one, down.It's a rather wise decision to carry around Ziz popping nuts.Father, I brought the Heart of London for you.Do you remember it?That dim thief got sidetracked by the surprising slug spray and broke into the security roomwith it.
```

### [40] hash=`28e671673af55612`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
After that, he turned over a new leaf.And things unattended have never come to his mind.But what I'm going to face is completely different from a poor little thief.That new security company had carefully arranged robots.They took action by the book and were heavily guarded.But there's no creativity in their defense.All actions were exactly as they were in the guidance on security.Not even as surprising as a fire engine.
```

### [41] hash=`906cdb570d91c2f2`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
It should be the best of times for thieves.I can't leave it to you.It needs to be sent to Sergeant Williams' office tomorrow evening on time.As evidence, it's quite important.But I have some interesting news.the world seems to have changed a lot.Today we have Mr.Iverson from the New Humans Company,which provides security servicesfor the soon arriving Rimmick Cup.As an experienced head of the company,
```

### [42] hash=`ec0133ef6ed5cac1`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
he would love to share the storiesof the Rimmick Cup with us.Years ago, the Rimmick Cup was under the protectionof the most well-known security company, Ramirez,but magically disappeared overnight.It only took one day for Ramirez to retrieve the cup.This flourishing company received waves of compliments, and people were celebrating the story of a false alarm.Everyone, including us, thought Ramirez defended their reputation.
```

### [43] hash=`9014f843babc5fd7`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
But, unfortunately, evidence from the verification agency showed that the rimmed cup they brought back was a counterfeit.They were confronted with the pressure of forgery suspect and the disappointment from all the peers.The imagination of Ramirez caused catastrophic havoc to the Hill Society.We then have to put aside the security theory held by Ramirezand return to the more science-based and reliable guidance on security.
```

### [44] hash=`dc1fbc385c9254b7`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
As it turns out, any security theories without regulations are castles in the air.It's a pure joke.What a sharp comment.Security measures require pre-built plan, advanced equipment, and reliable personnel.Ridiculous imagination is the last thing.The ideal answer to all of these can be taken from the new human security robots.Father, when you were assigned the mission to protect the Rimmet Cup,did you ever imagine such a day would come?
```

### [45] hash=`7b72fc931efe253b`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
If we had conducted a quality check on that Rimmet Cup after receiving it?If we had investigated the transaction records of the client company if we had verified the list of patrol officersPerhaps I would not be talking to your silent tomb today father.I will prove it allEven if it'll lead me to a path different from yoursReal protection is more than defenseIt's about attackMr.Iverson needs to learn a harsher lesson.
```

### [46] hash=`a1c14e0f37449a57`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Hey long time no seeyou here?I bet you the day before.You show up so often these days.Did you get rid of those scouts?They don't have time for me right now.Yesterday Captain Regulus encountered a weirdo.Right, ragged lad claimed to have left us his last words in the newspaper.Uh Captain, I'm afraid what he said was a surprising note.Never mind, it doesn't matter.Tommy, what's on the front page today?
```

### [47] hash=`1ff02f25636e5812`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Here, say for yourself.The Ribbit Cup exhibition starts today.Carnival for fans.New humans has announced to undertake the Ribbit Cup exhibition.More security robots will be put into use to replace human jobs.If all goes well, the security systems will be introduced to the police after the exhibition.London will embrace real peace.Far more reliable than humans.meticulous enforcers, an all-round urban security landscape.
```

### [48] hash=`a9ee2aa80a993c6e`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
It seems London will tighten the regulations.The government plans to launch security robots.Urban tin monsters!Yes, according to the description on newspapers,those robots can block out mobile signals and change the regional magnetic field.I'm afraid our broadcast will be affected.Can we still borrow others' radio waves?Of course we can't.What surprising note is this?If the robots take over London, my plans for a pirate's gig will go down the drain!
```

### [49] hash=`ad0b61a020621983`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
New humans.I get it.Ragged lad is part of the robots team.Or maybe even a badass boss trying to take control of London.No wonder he seems to have a problem with the cops.Blimey!This one is huge!Are you going to provide your first hand to the press?They must be interested.Never mind, he saved us once after all.A friend will persuade him to abandon his evil plan.Captain Regulus will never forget friendship for profit.
```

### [50] hash=`5ebfacf7bab569a1`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Damn shame.That's a heap of dosh.You can even get your cycles and fancy equipment.Huh?Tell me first, how much do they pay?Captain.I was just curious.Just kidding.I have to go and do something more important now.Cheers Tommy!Bye, I'm here if you change your mind!Breaking.Gemini 8 conducted first manual docking in space.Fifth fluffy sports meeting is coming.Interested candidates, please sign up with your pet.
```

### [51] hash=`324b124529a80133`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Police notice.A man controlled a watering car with special means and deliberately violated public transit.He will be detained for three days as a punishment.How come?Party theme, the key points of my speech, post, future trend of art, none arementioned.A brand new world was born yesterday, but most people don't have a chance to celebrate.Gloomy clouds haunt the sky of my utopia.Shame on London, shame on the world.
```

### [52] hash=`9ce7d17df70f9b08`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
We needto change, radical change.We won't be corrupted by entertainment.The bell ofwill break the shackles of stubbornness.London has been trapped in long and dreadful night.What it needs is the sun, not the dull stars.The deserted street won't attract many people.They're used to following the crowd.They can only spot the noticeable objects.We must throw a grand party of artto topple the mainstream, to blow more people's minds.
```

### [53] hash=`2b67ce6c8405a2ef`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
And it shouldn't be contained only to streets.I get it.The eye-catching exhibition hall of the Rimmet Cuff will become the unprecedented, the craziest, and the perfect stage!Wendy, I've told you so many times, no picking up litter on the road.What have you brought back this time?Open your mouth.Ahhh.Luckily there's nothing dirty on it.Gosh, it really messed with my head yesterday.I almost forgot something very important.
```

### [54] hash=`fb1b6c7d02abf67f`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Kids look!Look at what good news our little Wendy has brought home.The RimmickCup exhibition starts today!Now I have a better idea.How about visiting theRimmick Cup exhibition this afternoon?I heard that they will be doing alottery at the exhibition.The luckiest guy gets full tickets to all theWorld Cup rounds.Our little Pickles is definitely a lucky pup just likeother draw before.Are you not excited?
```

### [55] hash=`5d38a1cf7e77e2c7`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
There's a chance to get an out-of-printsigned football there, then we'll have a new toy for our ball game.Calm down Wendy, we will have a democratic voting session.Now doesanyone not want to visit the Rimmick Cup?Raise your paw please.Right, it'sunanimous!Dear, you promised me you won't make a scene when we're outsideand no yelling at strange things.All right, Mom.Ah, security screening passed.The warrior of the new era successfully arrives
```

### [56] hash=`cd2bf913d5e959b7`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
at the final battlefield with his magnificent bubble device.They are waiting for a gale.This is going to be the critical transition of our time.Can't cut in.A world without airflow is like a pond of dead water.The soap bubbles of a new world can't blow in.But a real artist never loses the guts and grit if everything goes on smoothlyI can blow enough soap bubbles to create an ocean of reveries within half an hour
```

### [57] hash=`52345d6741de0f2d`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
I just need to cover myself.How would someone blow bubbles indoors?What a funny smell I'm exposed in just a minute.OhI need to hurry up.These bubbles are far from enoughSeriously, you should respect and treat an artist fairlyThere you are again, annoying hooligan.I don't think I can understand what you're thinking.Are Arcanus also stupid that you always overestimate yourselves?I am not defeated, Mr.
```

### [58] hash=`ad9883ccaf2a7763`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Iverson.The fire of art will never be extinguished.Just like our craving for utopia never ceases.Annoying blabber.Though I don't know what stupid idea is lingering in your brain,Obviously you just failed again.Utopia is not stupid, sir.Without a goal, life would be stuck in the mess of corrupting materials and entertainment.I'm sure, soon enough, people will have the courage to speak up and sing for peace and love.
```

### [59] hash=`e3c415380ea92140`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
I've met a lot of young people like you who chase unrealistic fantasies.Ignorant and hilarious.cage I see my reverie bubble solution shoot it's in my eyes it's itchy blessme Talia put the efficacy takes effect a bit slower the fuses were changedrecently I'm guessing that of security here is a pretty tough nut to crack butunfortunately too much attention to the guidance on security will probablylead to carelessness in other areas transferring all the human security
```

### [60] hash=`15c8760f1207e76a`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
from relying solely on the patrol and precaution of robots.The consequence is a 30-second blind spotin the monitored areas every four hours,13 minutes, and two seconds.That gives you the chance to change the fuse here.That's right, Ms.Sacy.I will prove the ineffectivenessof the guidance on security in personand start the show at just the right moment.Then our next plan is to meet upwith all the security robots.
```

### [61] hash=`29c54cd67027015a`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
suspicious invader detected locating the last one you seem a bit smarter thanthe other robots locating failed initiate program to push pin blue gun nonoise I have to be quick watch out for its detectives look out it's nottear gas or electrode bug spray these robots are actually using realmilitary ammunition this violates the guidance on security that has beenhyperbole and believes it to be true.We need to hurry.
```

### [62] hash=`7f8dfa8db3fa818d`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Turn 45 degrees left and move 13 steps farther.The core device of the ventilation system is located in the third room on the leftside of the exhibition hall.There's no necessary living conditions and lighting.Normally no one will be there.I will have plenty of time to adjust the airflow.Strange.Like the sour flame wine that's over fermented.Oh, there you are.You are?What's going on?There's actually an ambush here.
```

### [63] hash=`f207dd97f2b6dcc4`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
It hurts all over.But is this my reverie?Or really heaven?Could it be a form of art created by the subtle sense of danger I'm feeling right now?And the dirty air?Come to me.You are my muse.Did I just bump into a human security staff who got fired and went crazy?Alright, I'll just think of it as an unexpected additional exam question.Try this.The ground-grappling that father used to teach me.Wow!Inspiration.
```

### [64] hash=`4d8126d25ab40a8a`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
My inspiration.Never lasts long.I've never experienced such vivid pain from the reverie.Still holding on?One more time.It's all settled.This...this is not reverie.This is a terrorist attack.Crying action.Shameful violence.You said an ambush here?You crazy addict of imprisonment and war.I must blow your cover.Huh?Are you not one of them?Of course not!Sorry.Stay, stay away from me!You must be the demon that Iverson summoned.
```

### [65] hash=`038204011a58a4e6`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
You're more horrific than those robots.If I say it's all a misunderstanding, could...would you understand?What do you think?A little reckless.Miss Acie, I know.I'm too nervous.In no way is there any possibility for him to be a security staff.It sounds like a joke.I must claim that violence is the antonym of art.It should resort to a more sensible means to fight.In five minutes, I have to change the terminal valve in the room first, adjust the position
```

### [66] hash=`9a14eca2f508d35c`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
of the deflector in the duct, and change the airflow from the spiral fan.Abundant magnetic glue will be blown out of the ventilation ducts by the spiral fan,and adhere to the robots.The fine glue will paralyze them.Completely.After that, you could just waltz away.Sounds like a big project.Do you need my help?Absolutely.Stay as far away as possible from the regulator valve behind you.Ugh.Captain, isn't our destination supposed to be the exhibition hall of the Rimmet Cup?
```

### [67] hash=`b727b1c950435b70`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Of course.I think we just missed the front gate at the junction we passed just now.Where we are now looks like a deserted back door.And there is a no entry sign.It's not important.It's not good for the fan-favourite disc jockey to appear in the crowded areas.I don't want to make a noise.Oh, I see.I thought it was because Captain didn't have enough budget.Complete misunderstanding!Our aim is to convince the ragged lad to expose the evil plans of those tin monsters.
```

### [68] hash=`97fc760f67edeca1`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Of course, we can't just walk in.Mr Apple, do you remember Tommy's offer of a generous reward?He hopes we can divulge a sensational secret.Captain, it seems you really want that bonus.Of course not!The righteous street pirate has a warm heart.We should do Tommy a favour.And we should accept a friend's quality thanks.I get it, Captain.The great rock pirate saves the day.The cocky ragged lad is no longer stray.
```

### [69] hash=`d4bd88b7f4627879`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
The big hero who saves London takes a series of exclusive interviews.Endless bonus!Captain.Captain, watch out!You guys from the government?I've done nothing bad!At least not yet.The skin hardness, the voice and the liquid released from the wound have nothing to do with humans.I am afraid they are...Oh, I get it!They're the security robots in the newspaper!Well, it might be.Is there a new way to keep order in London?
```

### [70] hash=`f2a39246ae381c3c`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Those fuddy-duddies don't have their beards in their heads, do they?We'll have to change the plan.London must not be taken over by these ugly tin monsters.We need to expose the security robots to the public for what they really are.They're violent, rude and extremely dangerous.This Apple will fight by your side till the very end.No, you have a more important mission, Mr.Apple.Captain Regulus asks you to take over the nearest radio station.
```

### [71] hash=`98251ef847b7fb60`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
Roger that.It says clearly on the leaflet, we welcome everyone who loves football.Yes, Mister.Then you should let us in.Me, Wendy, Alice, Nelson and Little Pickles.We all love football.I'm sorry but no pets are allowed in here.We provide pet keeping services with professional police dog guarding.Uh...Go ahead, Wendy.Looks like we'll all have a good place to go.Have a great time in the puppy land.Lovely to see you again, puppy with blue eyes.
```

### [72] hash=`b62739e411752f0a`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
This apple has accepted a commission from Captain to investigate the venue.Oh, right.Since last time we met, this apple has been contemplating how to communicate with you.So, here it is.A simple translator.Doggy.It's still under testing, so the functions are not complete.Sometimes it just stops working.Also, it might somehow misunderstand dog language.The puppy expresses his gratitude.It's my pleasure.
```

### [73] hash=`efff3dc35a917dce`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p14`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜5~10）

```text
It's a pity that this apple doesn't have adequate time to test it.You'd better leave as soon as possible.Those violent security robots may show up at any time.The puppy expresses his denial.There is something very important for the puppy inside.Oh I see, fair enough.Let's head forward.In the face of danger, this apple will do his utmost to assist.
```

### [74] hash=`ac7be07af6c50b62`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
How do you find this place at a glance?Have you been here?The puppy expresses his modesty.The mission assigned by Captain progresses smoothly.We have a whole set of broadcasting equipment here,then we only need to installa corresponding frequency interference device.Captain Regulus can fully control all radio channelswithin the radius of five kilometers.Bloody hell!Who let this plushy monster in?Now this whole place is contaminated by disgusting fur.
```

### [75] hash=`6a4faa9373bec676`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Robots!Where are my robots?Drive it out!Command received.Unknown energy detected.What's wrong?You broke down?Risk rating.Request support.Terrible plushy monster!It must be a terrorist!We must put it down right now!All of you!Drive it out!No, no, no!Put it down!DEFCON 3!What are you doing?Get away from my pickles!It's you who brought it in.I now warn you, your dog is a bloody hazardous uncertainty and we must put it down.
```

### [76] hash=`0deb0b1b51d45ff0`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
What a humbug!He's not hazardous at all.Every one of our neighbors loves him.Let's go!Achoo!You don't have a voice here.You can't leave either.According to item 5, article 172 of the Guidance on Security, security companies have the right to directly deal with any dangerous items when on duty.I command you to hand me your dog.As compensation, we will buy you a more purebred and more friendly dog for helping us wipe out risks.
```

### [77] hash=`b1ec9ba0b9b1cc44`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Don't use your mind to a pet dog.My friend, crazy bastard, would you ever leave your friend alone?Fine, maybe you would, a cold blooded trap, dead from the neck up.Put onto the World Cup audience blacklist, I kindly request you to stop what you are doing.Very well done.But I'll tell you what, you can't threaten me.I'm definitely not leaving Pickles alone.Go fuck your World Cup.What a fool.Catch them!
```

### [78] hash=`5afb8eec0728d1ad`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Finally.Turn the ventilation system to the highest mode.I don't want any dog fur here.Other robots, go catch that dog!Man confirmed.What have you done?Not me!The ventilation system suddenly started to work!This is the perfect plan you told me!We're going to be blown out!Slow down!Too late!Crash warning!Hi, Austin Vader.I'm sorry, Mr.Iverson.Actually, I didn't know my entrance would be so straightforward.
```

### [79] hash=`461f01e5de06eaaa`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
I think she knows the situation better than...Huh?Where is she?It seems you are the abandoned poor worm.What else are you going to show me?Any jokes of the never will happen utopia?It may be unrealistic, but it is possible.Lots of bubbles!Is this the special event of the exhibition?These soap bubbles are...I see!The ventilation system is switched on!The soap bubble device I threw inside is now functioning!
```

### [80] hash=`bde795cf79f820e4`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Excuse me, may I borrow your broken robots?Stop!What the hell did you do?What are these damn bubbles?Actually, it is a reformation of art.Get down from there, you bastard!Is he provoking the robots?He did sign a safety commitment statement, right?My friends, have you been fed up with the dull and dreary reality?Do you want to get rid of this place of cliché and red tape?You once yearned for a better world, a peaceful world with music.
```

### [81] hash=`2fa6dfd351ba7752`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Open your eyes and look at the soap bubbles in front of you.Now!And salute to all the transient beauties.Get out of here!Don't you want to try some of these bubbles, Mr.Iverson?We can find a peaceful way to coexist.Boring little trick.Aren't you curious at all?Take a look at it and you'll activate every cell of art.Even iron nerds can sparkle their imagination.Tony, your imagination level is null.
```

### [82] hash=`01d63f81c9cc6c96`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Joking time over.Your utopia has always been a joke.Only hegemony, hatred, and force can push history forward.Vain revolt is like helpless barking.Perhaps I will be expelled from this impromptu party,away from its artistic beauty,and forced to bid farewell to my new friends.Yes.It's better to say that the show hasn't yet begun.Let's turn up the light,turn down the air conditioning, and crank up the usage of the radio.
```

### [83] hash=`d988f64c8533e1f5`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Let's see,when will the replace fuse blow?Miss Acie, we don't have much time left.Comeon, let me bring you to a hidden place.Please don't mind swallowing aslightly bulky thing.What tricks did you come up with?This is going to beThe most crucial part.Please help me, Miss A.C.Actually, according to item 18 in the safety commitmentstatement, we need to arrest the violators whointerrupt others' visit.
```

### [84] hash=`43c236f283f7bcd0`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Tie him up and inject Mew Mew Mewtube potion.I don't want to hear his stupid ideas anymore.Command received.Mew Mew Mew.Activate the spraying system.Clean all those damn bubbles.The farce is over.All our guests, please enjoy your visit.Unfortunately, those who were bewitched and violated the safety commitment statement,you will be further investigated after the exhibition.My microphone back!My bread!
```

### [85] hash=`18abdb27f98c470f`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
I only took a bite!What's going on?Who let them in?Sorry, Mr.Ives, there are too many of them.In time, pirate captain has arrived at the grandest stage.It's 25 degrees east.You are listening to the Rock and Apple, the most distinctive ship to date.Salute to all my discerning audience, my loving followers.You get it right.This pirate has hijacked all the radio frequency pins.You're able to pick up Radio Apple clearly from anywhere in London.
```

### [86] hash=`e04225a1911b3570`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Whether you're cheering for the moment or wish to change the channel,whether you love rock and roll or hate all music,Do not switch, if you don't want to miss the moment to unveil a conspiracy.A huge conspiracy about the London authorities and the compelling security robots.My friends, we are in the middle of a huge hoax.The London authorities have deceived everyone.It is impossible to have such obedient, flawless, safe and reliable security robots in this world.
```

### [87] hash=`7688577e960cef77`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
On the contrary, they use violence, harm citizens and show no kindness.What?To cover the back sides and block the news, the man in charge, he keeps out the people who want to have fun to visit the Rimmick Cup.Captain Regulus clashed with the robot army at the back entrance of the hall.The brave captain managed to escape and to retreat.But there's no doubt that this is an infringement of our freedom.
```

### [88] hash=`8877d88179afaae6`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Competent London authorities attempt to work with security companies and use their awful robots to govern.They want to take our lives away and render us helpless so they can manipulate us.You have my respect, poor ragged lad.What that pirate said, is that true?I am very sure you are deceived.But you did imprison the poor citizen.If that's what you think, I can now prove to you the reliability of new humans' security.
```

### [89] hash=`688c94a6e75a6703`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Mr.Madbot, you and your evil plan have been overcome by the Justice Captain Regulus.It then belongs to us, belongs to freedom!You're right.In such case, security guards are more flexible.You...you mean...Do something!These people are breaking the rules!Are you just going to stand and watch?copy that what are you doing Apple here put the tape away this pirate's instinctsand never wrong my assistant mr.
```

### [90] hash=`477691e8f26116b5`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Apple has firsthand evidence of everything itwill be the most sensational news every news agency will invest millions on itthe next song for the exasperated poor authorities mm-hmm all is ready go turnthe emergency light and go check the circuit copy that what are you doingthis is not the emergency light no no that wasn't me the cup the cup ismissing flawless protection is just a disguise while threatening is the
```

### [91] hash=`b56f68f81221e9ad`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
essence in such a dull and dreadful exhibition hall does anyone stillremember those stories full of imagination and miracles she hopes theWho are you?You were repelled by Ramirez's novelty, and hated their surprising imagination and miracle stories one after another.Apparently, it is better to follow the rules, even if we fail.We'll have nothing to be blamed.To bury that shining star, the peers jointly forged a Remit Cup, and carefully schemed a security commission that was doomed to fail.
```

### [92] hash=`95236fed6424f369`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Bullets!You are a thief!You're not going to defame us!Or my real name, of course, Melania Ramirez.Mr.Iverson, what shall we do?Don't listen to her.Are you going to believe a thief?But there's no article on guidance that we could follow to deal with a situation like this.Fathead!Put her down, then everything will be fine.Gun ready, field bullets.Looks like you guys made the worst choice.Well, it's not surprising, but to tell you that some of the equipment carried by the robots have violated the guidance on security.
```

### [93] hash=`69a63ddb4dbbba65`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
So, I replaced them with safer firework bullets.Sorry, but it's better to destroy the remote control that will place our security at risk as early as possible, okay?Look at that dog!No, not that one!Look at the water collie!He found us the Rimmick Cup!What?That puppy ran away!What's he gonna do?Feeling sick.Disgusting.Almost crying.Sorry, Miss A.C.It was me who asked you to swallow too much weird stuff.
```

### [94] hash=`769f6a8d6f97c6bd`

- lang：`en`｜version：`1.1`｜arc：`—`
- doc：`BV1eo4y1u7aW_p15`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.1-活动】雷米特杯失窃案｜11~16）

```text
Even including me.I swear, when it's all over, I will take you to a professional leather care store for proper treatment.But now, we have to get out of here as soon as possible.Are you finished?Of course.Iverson looks as if he's just swallowed a whole slug slime.Eventually, he's lost to the Arcanist imagination.Those journalists who are not in the plan would definitely not miss the big news.It's all a mess here.
```

