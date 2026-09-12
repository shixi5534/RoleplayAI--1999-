# 剧情图谱抽取 · batch 054

- 角色：`wu_ming_zhe`
- 批次：**54** / 共 1 批（每批 95 块）｜本批块数：**94**
- 筛选：标题含「1.0」｜offset 380
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_054.jsonl`

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

### [0] hash=`35065fb9ebb8079d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
I didn't realize until I put all these together and found that the underground air raid tunnel connects the northwest and southeast watchtowers.And the two first floors of these towers are the only two exits towards the outside world,aside from the gate.A temporary tunnel!How clever!You see, it is impossible to sneak out from the front gate under their surveillance fromthe watchtowers.In such an open view, they will never see us coming out from underneath!
```

### [1] hash=`ad6ffd859295108e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
A blind spot attack!Then which one of the two towers are we going to?Have you planned out the route?The safest plan is to go to the clinic through the girl's dormitory.There is only a door between the southeast watchtower and the clinic.Taking the Shamirs with us, then we don't have to worry about the keys.The map only shows the blocks outside the southeast watchtower.I noticed that there are many options for transportation in the neighborhood.
```

### [2] hash=`57d3c17ca1962e69`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Easy for escape.This is a nice map.Where did you get it?I got it dropped by one of the ol' lady house.You have to be quick and stealthy in collecting them.Hey, that's my things for the number of a lit y'all has recently increasedairdropping packages with various stuffMapsNewspapers headlining foundation cover-ups survival guides.They even dropped some field Russians recentlyBy coincidence or not, I think this man has been jinkies helping us all the time
```

### [3] hash=`6be8a711d721ff1a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
That'd be great then think them dearly after we get out.Yes, we should I also have news about our timing to moveThe headquarter will visit our school in five days.Before then at Eiffel, the school will keep tabs on us.That's why we should leave on the next dayafter those big guns have left.I know how it's gonna be,that all the instructors and secuitieswill be as lax as the crumbs from a Pandoro.Nothing will keep them getting together.
```

### [4] hash=`a49446cf3ef5220e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Good, then this is it.Prepare food and clothes.The breakaway action starts a week later from now.No crying.Matilda, you look like you're crying.I can't be a part of this breakaway action.This is what you planned to do.Like you and the others, it was my own wish to be transferred here.One time I saw the school ceremony by the campus fence and she here.No, never mind that.To put it in brief, I can't keep messing about with you people anymore.
```

### [5] hash=`e0ee1b39adf6ff6c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
No matter how they have disciplined us, how awful they sometimes could be,I never thought about leaving here.And become the top student in schoolMatilda we won't force you to do anything you don't want to after all we are here becauseWe are longing for freedom.We once fought side by side.That would be enough.OhBy the way, could you tell our plan to mess with junior for me?She is one of us, tooI don't want to leave her behind.
```

### [6] hash=`3ef23548fd8c437c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Tell her about this.Take it to the doorYou've done an excellent job, Mesmer Junior.Taking care of all those patients who suffered from the storm must have been quite harsh, right?I'm sorry you had to go through all this at such a young age.The Mesmers and we have a long history working together.I believe you, as the heir, will be strong enough to know the truth of the storm.We are mad people.They were once ordinary people just like us.
```

### [7] hash=`2ceec52cff620d76`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
It was not their fault.They were just not ready to take the truth.Not everyone can be as strong as you are, Mesmer Jr.Here, we have many other patients waiting for your help.I will try my best.There's one more thing we found in your locker.Do you mind if we keep it for you?It looks like a new plan from a friend of yours.They're too.They'll be in danger.That's what I'm here for.Go have some rest now.
```

### [8] hash=`33856477441e6d00`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Maybe there will be new patients coming in the next few days.Thank you for telling me, Elvis.He spoke.We have the time of the night storm.They predicted that it will take place in the 27th evening this month.You see, I was right on this.Threats would never have persuaded a man as vindictae to speak to us, but interest and love would.Thanks to our scout squad, we have not only found the post commanding the
```

### [9] hash=`ced414624efea329`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Alidia house, but also captured a prisoner.And now the problem with Verton hasalso been taken care of.The breakaway action starts on YIC.Do you have anything in mind?We don't know which of the students have beeninvolved in this plan, but we can send people to the Watchtower and rescuethose last lamps on that day.I want the inspection date to be put off to the 26thand have everyone stay on their posts before then.
```

### [10] hash=`eb28825d3f9dead9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
We will remove one of the guardsfrom each of the watchtowers after the 26th.In the meantime, get rid of the doorin the air raid tunnel from the girl's dorm to the clinic.Install a new door made of lead compounds.Also, transfer some of the patientsin the foundation to the school clinic.I've been looking forward to her transformation since 1999,and I need her to learn the price of rebellion.Do you have any other questions?
```

### [11] hash=`66bc76f2f4f31bb5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
If not, you may go on with your task now.Great with this plan.That's just because you don't understand the game of politics.I don't.Too bad.I'm just a scientist.Change of plan.Emergency.Change of plan.Years after, when I think of that escape, still feels like I was in a chess game, playingagainst an invisible enemy.Back then, I knew nothing about chess, nor resigning, let alone the fact I was in the
```

### [12] hash=`2c3c59a99833e1fa`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Zugswang.It's impossible to go to the clinic through the girl's dorm.The clinic is now crowded with people and we must give up the road to the SelfiesWatchtower.We have another option, to go to the classroom first, then enter the airway tunnelfrom the library.That is to say, we are heading to the North West Tower?Exactly.Once we get down to the tunnel, we will be much safer.Have you left the window open at the first floor?
```

### [13] hash=`0b1607d66e54bb2d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Yes, don't worry.I didn't lock it.Or I can take you in from the library's front door, if the window would be locked by the caretaker.The most dangerous part is from the dorms to the library.Not only will we pass the classroom, but also be exposed under surveillance of the central watchtower.Leave that with me.I will cut the fuse in the central watchtower and that should give you a five minute blackout.
```

### [14] hash=`1831ddca9acbc282`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
And you gotta watch out for the patrol team.I will drive them away from you.Okay, now split up.Once the central watchtower's lights is out, we move.I will see you under the A12 window of the library.And these crystal earrings are gifts from Matilda before I left.Wear these and we can hear each other within a certain distance.That's all.Be careful, I will see you soon.Sitting en route to the central tower.
```

### [15] hash=`c8be34cba735929d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
No visible personnel.All clear.Copy.Be careful.Keep in touch.The thing ahead is...Teaming!It's all teaming!People in the classroom, distract them.Roger that.It'll be curfew soon.What are you doing here?I had an upset stomach and was trying to walk it off.Sorry sir, I'm heading back to the dorm now.Stop.Show me your ID.Beta Alpha Four, cut off the power for the central watch tower for five minutes.
```

### [16] hash=`d6b1fc32944db725`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Fusebox tricked?Now is the time, go!Sir, sir!The light is out in the central tower!Please, come take a look!Is it gonna be problematic?What?We're going back!Everyone, go to the library now!It's difficult to sneak out of the dormant this time.Isabella, if we get stopped by the supervisor, be prepared for conflict.Double Beta 3 are the flower bouquets for the dorm supervisor in position.There are also quite a number of gifts in them.
```

### [17] hash=`fd2b1be79c5cbe63`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Heads down, stay low.Don't get caught.How come there are so many visitors at the supervisor's office?They won't see us getting by!Great!Go!How long until you get here?I'm already at the back of the library!Is the window still open at 812?The caretakers didn't notice it, did they?Yeah, but window 812 is a small one only little girls like you could get inWho come I chose it for it's hidden in the corner
```

### [18] hash=`e1b9b0799cdaf693`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
This is awful.It's okay.Don't worryI'm in a 11 is not locked either.You can get in through a 11 toHassling the windows were all left opened just in case the caretaker would of course be careless at workGiven the inspection was just over.What's your move then Burton to boldly push forward or?Start to feel skepticalAmazing everything's going so well today.You keep watching.We'll be right thereBlackout watchtower
```

### [19] hash=`abe402d3d97ca3bd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Curtained up classroom windowsblind patrol teamsHuh.What a well-planned malpractice show.No wonder.But giving me this fine vodka is just a trade for my dizzy head and half-shut eyes.Look who's after those children.Hopefully I'm not too drunk to get it wrong.Is that a good student?Interesting.You're flying ace reporting for duty.Out of the library.Keep going everyone.What is that noise?It's scary.We should be onto the sports field now.
```

### [20] hash=`3b5fab111b4d1fe7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Probably some big shot is having some fun with his levitating cod.No, it's thunder.It's about to rain.Everything goes so well today.too well maybe making me uneasy don't think like that look we areentering the northwest tower after this crossing who knows we'll be therewaiting for us let's what's wrong person section finally my patience isrunning out you are apples from Zeno what are you doing here being
```

### [21] hash=`bcc21ee63339c605`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
dedicated to duty and catch you guys.You really think escaping can be so easy?She's a soldier with field experience.If we can't take advantage within the first few rounds,you guys retreat immediately and I'll cover for you.As long as one of us can get out of school,our plan succeeds.Oh, I can hear you.In that case, I have to be extra carefulin case any of you lab rats runs away.Please be mindful of your language, Lilia.
```

### [22] hash=`79db0e3c474f66cd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Your duty is to eliminate the Illitiaus in the campus,not attacking the students.Donato, why are you here?Seriously?Is more practice a compulsory course in your foundation?Then try me.Let me see the best you got.Swallow my exhaust!Now temporarily paralyzed.Thank you for your assistance.You're going to do something very dangerous, aren't you?Yes.It will cost you everything you've had here.You will not be regretful.
```

### [23] hash=`6376cb312024fc73`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Right?We've prepared for everything that could happen.No regrets.My notebook anymore.We chose a different future.But future has no right or wrong, Zanetto.Get yourself out of these things.It's a pleasure to be your dustmaid, Ferdinand.Did you hear it?Get in outside!The tower!Don't let Daniel guard.Let me see.How are the Shamiers with the lock?Get excited now.We haven't gone out yet.One after another, keep it quiet.
```

### [24] hash=`e27acd4b68ebab1b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Don't touch anything.The garbage should be on the second floor.Let's move.Relax, Farkton.The best is yet to come.Till we take a breath of the real air.Till we stuffed ourselves with delicious food.Till we get back to our country.There's so much more for us to be shivering at,what an excitement you're right let's open it together two one don't be with us do you want to be
```

### [25] hash=`d1d0f44bcf547768`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Burden, I saw burden by the stormNoIt's just a nightmare a nightmare overly realIs it because I haven't seen them for so long was the first to leave?She said she was going to talk to Madame Z about which department we would belong to I haven't heard from her since thenYesHere are their background reports I wrote for your perusalthenSotheby.Her boredom was swept away by the invitation.She departed in such a haste that her beloved doll was left behind on the carpet.
```

### [26] hash=`fd40fd26e461d8c9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
This is Sotheby, a well-educated lady born in a traditional Orcanist family.She comes from an extremely privileged background.Her family had a special influence around the world.Besides, she has limited social skills and scientific knowledge.It will be difficult to assimilate her.Compared to Sotheby, Mr.Apple was apparently not very happy to be invited.When he left, he turned a little green.Mr.Apple, under his modest and gentle appearance, lies a sharp perception by nature.
```

### [27] hash=`7fa8aeb47bbb2b22`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Being so erudite, he always has his own views of our historical intelligence.As far as I know, he remains upset about Captain Regulus's involuntary affiliations with the Foundation.While Regulus had never been truly accepted by the Foundation, she's missed out all the education and training a member of the Foundation should have received.The influence left by the outside world on her is like a banner among the ordinary staff in the Foundation.
```

### [28] hash=`5683e8e14af0a838`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
A banner way too salient.Once the banner was held up, new arguments were raised, and thus exacerbated the factional conflict inside the Foundation.Factional conflict?There ought to be no factions in the Foundation.All of us share one common goal.You should know that well.But the conflict has been there all the time.And it only grows.The group that believes in mankind supremacy is splitting the foundation's belief apart.
```

### [29] hash=`367efb7792bd15c2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
So, time isn't the only thing we've been observing this year.The conflicts cannot be covered by regulations anymore, Madam Z.The storm has been here for eight years.None of the people who were left behind can shake off the influence it brought.Human technologies are being reversed, while Arcanum is blooming.The unexpected first storm brought more than half of the Foundation's elite members away from us.
```

### [30] hash=`770d1b3c522e0999`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
The number of staff of the House of Integratus and the committee cannot compare with that of their heyday.Even now, in order to contend against Manus Vindictae, we have kept absorbing Arcanus from the outside world.However, the dissenting voices have only grown louder.Loud enough to be heard, and have become a faction that couldn't be shaken, the Mankind Caucus.Beyond their control, these new Arcanists only brought fear.
```

### [31] hash=`355a6abd115420fa`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
They demand an unchallengeable power to make decisions, and a harsher control of Arcanists.Madam Z, I don't want my friends or me to be the sacrifice of this conflict, as we were four years ago.That's why you're handed in the background reports of those Arcanists as the evidence for your proposition in the negotiation.Verdun, what do you want?A neutral, safe, and legitimate place for us.What if I'm also on the side of Mankind Caucus?
```

### [32] hash=`87483fa1a8f9ccb7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
I don't know whose side you're on, but I believe the future you pursue doesn't end up with a foundation being split apart by factional conflict.That's what I learned from that stormy night.Your eyes told me, you didn't belong to that chess game.You may leave the reports any sometime, no matter what your decision is.Please put me through Delegate Mark.Hey Burton.Hello.Your friend is waiting for you in the rehab center.
```

### [33] hash=`19b8769070928359`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Mesmer Junior, remember?Let us take you there, so you guys can catch up.Miss Druvas, we are waiting for your response.Now I am the last to be invited.Is there anything else that concerns you,Miss Druvis?When will my friends come back?They are waiting for you outsidethe suitcase, just as we are.All we want is an opportunity to talk to you faceto face.Please wait a moment.May I ask where we are?The library.
```

### [34] hash=`342e4741be719dfd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
A placewhere people let down their guards.Trust always facilitates cooperation, don't you think?But I don't even know your name.The name is Constantine.I'm the vice president of the joint committeeof the Foundation.Please allow me to extend a welcomeon behalf of the Foundation.We have sent this document into that suitcase days ago.I should assume that you have read it.What's your conclusion then, Ms.
```

### [35] hash=`8e02541990cf00ba`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Weyerhaeuser?Are you referring to inviting Sotheby, Mr.Apple and me to join the Foundation?We need to discuss this with Vertan before we give you a proper response.We don't know much about the Foundation.As far as I'm concerned, I do not yet intend to join any organization.That is to say, you are inclined to turn down my proposal.My apologies.Verton has not only been of great help to us, but also saved us from the storm.
```

### [36] hash=`f5ef7e2d5ddd6622`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
I cannot accept the invitation without her opinion.Neither can I make decisions for others.Fair enough.You, who accidentally and rather luckily escaped from the storm in 1929,and now seek refuge from the Foundation.Weyerhauser, Sotheby, and Apple, you are the spire of the tower.Between you and the Foundation, the stories in the middle are our investigators who go out to rescue the wandering Arcanists and humans.
```

### [37] hash=`c7ac771ebe77cf8e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Vertan is one of them.Merely a drop in the ocean.Vertan, indeed, is the key to connect you and the Foundation.But let's not forget, only an entity as massive and powerful as the Foundation can provideyou with long-lasting protection.Without the Foundation's supplies, manpower, and technology, even Burton can barely sailagainst the great tides of history, let alone the ordinary people, whose fate is doomed
```

### [38] hash=`3205f6bfc3c8c7f2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
to struggle in the endless hazards of time.Open your eyes and take a look, we are the unshakable fortress you should rely on.Do you still wish to talk to Vertin first?She's receiving a treatment from us, which means she won't make it back by your side before any decision is made.Her suitcase will also be retrieved for research purposes after the meeting.As compensation for your displacement, we will arrange you a more decent room.
```

### [39] hash=`d677f5bfb0ae71dd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Ms.C will show you around the headquarters tomorrow.Go walk around and meet some people.Perhaps it will help you see what the most beneficial choice to all of us would be.I will wait for your answer.But don't keep me waiting for too long.Yes, I've received the report on the Chicago office.Well done.Good timing.Did I startle you?Considering what we've been through together, I didn't expect you to be as surprised as Ms.
```

### [40] hash=`41b406793c8fa47c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Weyerhaeuser was.Sharon didn't tell me you're here.There's no need to tense up.I told her not to say anything.I have talked to Ms.Weyerhaeuser.Everything is going well.She's gotten quite a shock.That little pale face.Like a stressed cat.She's in dire need of comfort from a friend.What do you want me to do?To do what a good tamer would do.Reach her with a sincere, friendly gesture.Ease their pains, answer their questions, and lead them on to the right path.
```

### [41] hash=`994e347caee1df24`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Of course, most importantly, make them be of use to us.To serve the course of the peace of mankind.I see.None of them has signed the agreement.But this recruitment is essential for us.For the short term and for the long run.Can you see what I am doing?And there's one more thing.Don't address her as Miss Weyerhaeuser.She doesn't like it.I'll take note on that.Five and two-thirds portions of silver wine, 20 drops of toad oil, and some crumbles
```

### [42] hash=`7af0d1a5aac6e9e5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
of pure gold from Ukiyale.Last ingredient, the burning acid salt.Sotheby's incredible shapeshifting potion will be done at any minute.Can work as a decent vessel here.Different from expected, but it doesn't matter.Three.Me, but I have to open the door.Miss Sotheby?Miss Sotheby, you are not allowed to leave the room without permission.Please forgive me for being violent.Great potion alchemist that easily.
```

### [43] hash=`82c85ec5cc8d2442`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Your dress is a mess.This room smells terrible.Good to see you here.We must apply for more guards for this room.I'm here!Here you are.We'll give you this, and ask you to help us to, um...To evaluate the mock exam of Xena's enrollment procedure.I can't find you anywhere.I'm center, so I came here.Please, possible.Turns out, the moment I saw you, the thing just slipped my mind.You're excited?Alright, I got it.
```

### [44] hash=`7498b348e43fe275`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Go for it, me.Do I look like a stajor to her?Nivashn.Let me check.Elevation, 2,500 feet.Mountainous terrain, dense forest area, good atmospheric visibility.Enemies, groups of ground-based food critters and airborne aletius species O4.If we were to engage the enemy in this dense forest and fight in close range,our mobility will be largely reduced and we can't borrow roll to dodge attacks from the ground.
```

### [45] hash=`01bb99a68d61a6f0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
But if we pull up and deal with the air force firstClose enoughReady to fight.That's it.Scooch, Nate.What kind of new recruits they will let in by giving out such a simple examAre you evaluating the battlefield mock exam for this year?I heard Zeno has updated their question bandJust killing time.I smelled bison grassHuh?In your canteenOh, right.Authentic Zubrovka.One of the few pastimes I have here.
```

### [46] hash=`57db71d2fd76b97c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Wanna have a sip?No, thank you.It smells fresh, tender, like thyme and lavender in spring.I believe it is precious.You can smell things?Fresh indeed.Made in 1929.I'll say it's already about...Forget it.I don't do maths.So, you're here for Vertin too?I'm showing her around the foundation and decided to drop by the rehab center.Does she dream?Sometimes.Let me show you somewhere else.You have a good taste, Belle Weather.
```

### [47] hash=`d57e359bb7129a8c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Never tried the vodka from 1929 before.Good for you to get this in the US when both alcohol and kumarin were banned.The thing you said about, take care of them for me when necessary.I'll consider it.Raise a glass, padruga.To your health, your soon recovery.To our better lives.To this unknown date.To this messed up time.Za zdorovie!You have a basic idea of this place now.I'll walk you to your room.
```

### [48] hash=`8d7b2f53b38b6a9c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Is there anything else you want to know?What do I have to do so you will release Burton?It depends on what you hope to achieve.Depends on us?Is that what you said?Vertan, the person we rely on is being hypnotized in the rehab center.That suitcase, the world we inhabit, has been taken away for research purposes.It's as if the whole thing was manipulated to leave us high and dry and isolated,so that you would have something on us.
```

### [49] hash=`bf9e4c1f76b1ca87`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
We do not have a choice, Madame Z.However, if we change the condition, that something they have can turn the negotiation around and in your favor.I do not understand what you mean.Before she went to the rehab center, Virgin asked me about which department you would be in.And we have worked out a feasible proposal.Better catalyst is what we need at prison.The quiet, mild and tranquil status quo makes the change seem unnecessary.
```

### [50] hash=`33b4eaf5a7d36261`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
A proper gust of wind will vitalize the wave of change and push it to the cusp of evolution.You mean, but it is risky.That's true.I cannot give you any promises.But a fixed pattern of management will only impede the development of everyone.I hold the same idea as Verdict in this case.Or there is another path in front of you.Sign your name and become an official member of the Foundation.A path that many arcaneists who cannot support themselves yarn for.
```

### [51] hash=`ad453b62d40e43d7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
So, you are not inducing me to join the Foundation?I'm here to show you around.My senior asked me to make sure that you had a comforting tour.I hope this tour is helpful for you.We're on it!I can't even get them out with the gravity vacuum cleaner.It's like they're rooted.They weren't here until a few days ago.I heard some of these scenes were also found in the rehab center.But the staff there got rid of them in no time.
```

### [52] hash=`9b613d4740cd58dc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Bloody hell.Looks like we have to dig them out one by one with our fingers.Got to get it done before the inspector's here.Seed?What seed?Ward?I really have to sign the agreement to get out.Anyone yet?Always thinks it through and reaches an agreement with the adults before she signs any document.The cast has said that hundreds of times.It must be vital.Ohbut it's a drop in the bucket.Fine, I'll go apply for a few more, just wait for me there.
```

### [53] hash=`a51530f24deb530b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p8`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜1~5）

```text
Eggerton, go help them out.On your next!A forest is growing out of Ms.Virgin's suitcase!This is great arcane skill!I wish I could see that disaster in myself!Did you get out?
```

### [54] hash=`afa9492251baa603`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
All right, here are 30 cans of Dr.Pepper, 20 bags of Happy Wedges, 11 bags of BigfootGummy, and a bottle of insect repellent for plants.Oh, good timing.There may be a bit of ash on them, but the flavor and texture should still be fine.That's way more than a bit!I can't just carry them with me in broad daylight.Do you know how many procedures I've gone through just to pay you a visit?I've shown you the storm records these years.
```

### [55] hash=`344fec51ae72bbda`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
So did you find anything call it a record?But it's so brief that it only has start time and duration.I can't tell any pattern from thatHmm this Apple believes that the storm which happens randomly does not conform to the self-adjusting nature of the universeSelf-adjusting you mentioned before something like there should be someone who?intervenes or improves the system in order to reduce the growth of the instability of
```

### [56] hash=`c0f847a741e75013`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
the universe?For example, if the universe is a mooring rope, no, a bunch of ropes,there has to be a sailor who pulls the ropes to keep them in order or something.Sounds like the cosmology from centuries ago.But your metaphor reminds me of Madamethe chief of the vice president's staff to a formal member of the committee.I guess she willspend even less time in the lab.The whole building shakes.Did something hit it?
```

### [57] hash=`aed3ed1e376165c5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Let me see.Druvis and Sotheby.What's this?Guys, I am not going to be dragged into a ride at this point.Is that Druvis?What happened to her?Her new hairstyle is sort of cool.This building is the furthest one from the center of the Foundation.On the first and second floors are material rooms and research offices.Few staff stay here.The room next to yours is the projection lab.It was used to control the slides projected in the lobby.
```

### [58] hash=`fac1707870ff43f2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
That screen is gone now, but the transfer devices and circuits are still there.You know what?If you're going to protest, make it loud.It's been a long time since the Foundation had something this much fun.Yes, we have a disagreement with the Foundation, Ms.Sotheby.Burton is seeking a limited freedom for us.Her aspiration is to restore the peaceful life before the storm.For the authorities, however, her aspiration and ambition are labeled as deviation and rebellion.
```

### [59] hash=`63eaacc61ec17255`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
We are thus tempted, alienated, and arrested unjustly.That's why we've been grounded all these days.So we're helping Verta now.Is that right, Ms.Juveth?Think for her.Like what I'm doing right now.Wave on the tree.Right.On the tree.We need to move forward.To move one step further.When we meet up with Regulus and Apple,our voices will be stronger,and more and more people will offer their help.I believe that when the day comes,
```

### [60] hash=`7179a53ee4da503f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
We will be able to shake up the balance in the foundation and tilt it to our side.My goal is to make more potions so that trees can grow larger and larger.Make them so-This is going to be a protracted war of resistance.After we rescue Regulus, please maintain our territory of the woods with the rest of your potions, Ms.Sotheby.Sure, I will economize on them.Look, out of the room.He left.It seems he has made his choice.
```

### [61] hash=`269cd2f583618fa5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Not helping us or them.Well, at least no one is getting hurt from the boiling pot this time.What's at the door now?It seems everyone's there.Perhaps they have guessed our next move.Regulus.Let's go.It's time to meet up with our companions.Just as I was!Do we have the candidate's name list?Show it to me.Please wait a minute.It'll be prepared right away.Why is the light on?Listen up.We have taken over the Foundation.
```

### [62] hash=`b764beac4a6daf4e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Our demands are...Release us!Set Burton free!You have three days.After that, we are...Madam, I...I didn't.I...What's the matter?Something wrong with the printer?No, no.Oh, right.The candidate name list.Here you are.Bloody hell, how dare they cut off the power!This pirate has so much left to declare!Wimps, cowards, hypocrites!I can't agree more!It is very rude to hang up before others finish their words!
```

### [63] hash=`a86e07672c16b146`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
This is not telephone, Miss Sotheby.But of course that's not the point.No matter what, we've communicated to them the most crucial requirements for negotiation.I'm sure they will respond to us properly.I just want to take the chance to show our attitude.Taking over the radio station at the headquarters of the Foundation,it's a gas in the late hundreds of years.It would have been perfect if we could have another
```

### [64] hash=`e77046e5aa6134e3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
You Can't Win to close it out.We could look around here to see if there's other broadcasting equipment.However, this Apple does not recommend frequent provocation.Right now, it's more important to patrol the surroundingsin case we are ambushed by the guards.Miss Druvis is forming Abbottice alone downstairs.Perhaps she needs our help.Fine, you have a point.This pirate has decided to put off the plan to liberate the Foundation.
```

### [65] hash=`42caad977d3baa60`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Besides forming Abbottice, what else do we need to do?There's much to be done, Captain.Find water sources, transfer essential equipment, reserve enough food,set up multiple defences in the woods,and arrange a duty schedule.Make sure someone is garrisoned outside the suitcase,while others are resting inside.The tomato and potato seeds from Las Druvas.You must plant them in the suitcase to guarantee food supply.
```

### [66] hash=`b35ef5690fd7c5b4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Um, tomato and potato?All vegetables, no meat?They're meant for the piggies that grow my bacon.When I was wandering the seas,at least I could have a grilled sea bass every day.I wonder what Vertin eats in rehab.Will she be hungry?Almost forgot about the goodies X sent.We'll definitely hang in there for a few more days with them.Sotheby, Mr.Apple, you go downstairs first.I'll meet up with you once I bring the box down there.
```

### [67] hash=`f6c50c74aff9faa6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Meet you at the entrance.There is no need to hold an emergency meeting for this.Such declaration of war without tactic or plan B is typical example of Arkinist's behavior.The area they control has no value at all, no matter in terms of the size or the influence.Well, the administration department has not taken official actions yet.I heard the plan was to dispatch a team to escort them to the School of Discipline.
```

### [68] hash=`5422ade8d2e8c01f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Problem solved then.Next time, if Vertin brings back more unregistered Arcanists, will the same thing happen again?I don't understand.It's not a shame to join the Foundation, is it?By signing the agreement, Arcanists will enjoy the right to use arcane skills in human society and be bestowed great honor.The Human Resource Department could have used the whole floor to hold the applications a dozen years ago.
```

### [69] hash=`7cf63213c3543b10`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Not even the New Age movement could challenge the Foundation's authority in the international community.At these short-sighted exceptions, they aren't even worth being made a topic for the meeting.Yet, they're not here for the Sympatho Foundation.They're here for Vertin.They choose to follow her out of their own will,because of their admiration for her.That is the essential difference between them and our former recruits.
```

### [70] hash=`17cb02af275ed6bf`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
You mean, it's not important at all for them to join the Foundation?I'm afraid so.But we can't expel them.We both know that the Foundation now requires new members to form a stronger force.What are you trying to say, Miss Z?Skip to the point.Today, the House of Integritas has resubmitted a revised draft of Storm Reformation,Manpower and Discipline.I think it's time to decide if this draft can be adopted and then start the debate.
```

### [71] hash=`07a230a9e6ada6bc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
You are asking for troubles, Madame.Please turn to page 21, section 3.External personnel recruited by the Timekeeper should be placed within the Timekeeper's department.The Time Keeper has the duties of education and discipline to them and should be responsiblefor their follow-up behaviors.Personnel within the Time Keeper's department, subject to the Foundation staff code, willtake orders from the Time Keeper and are not required to take direct orders from
```

### [72] hash=`891cfce8eef06517`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
the Foundation.This section allows those unregistered Arcanists to have more autonomy and develop a strongersense of identity as a part of the Foundation.Meanwhile, by giving orders to the Time Keeper, the Foundation still has the military rightto deploy them.It can't solve the current problem.Which means we will be working with some uncontrollable mercenaries.I'll say it's the reserve service for wartime.
```

### [73] hash=`5132643690f7497a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
It's not going to work.What happened when the Arkanists were not under control?Massacres, tyranny, endless revenge.History is nothing but a sword where they vent their excessive energy and deceive those in power with a speech of ignorance.The reality has proven that.Exactly.What's more, there has never been a reform as such in the history of the Foundation.During the unexpected storm, reforming in a rush will only increase the...
```

### [74] hash=`eac2917c03b4a355`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Sorry for being late.Quite a heated discussion.I can see you all have a great interest in this draft proposal.Hope I didn't miss too much.We are on page 21, section 3. Ms.Z insists on adopting this draft.Ms.Z, please walk Madame Constantine through this section.No need for that.I have read the stenographer's report.In fact, this is the second time I'm addressing this proposal.Considering the Integratus has been very determined to its submission,
```

### [75] hash=`dcee91fe7c0c6aed`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
I believe many delegates must have a burning interest in the case.At least it's worth some discussions.Pedra, why do you oppose it?The rise of Manus Pindicta has caused the Arcanic World to gradually break free from the Foundation.Therefore, we need to monitor what our Arcanists think and control what they do in a stricter manner,in case they go too far.Manes Vindicte has a subversive slogan.Their influence has been getting bigger since the first storm,
```

### [76] hash=`d8873b9c14624f86`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
so has the scale of their infiltration.In the Walden Incident of 1929, we were given away in advance.It probably had something to do with the infiltration.Very well.A point worth discussion.But it is not relevant to our subject here and now.Stenographer, please take down the point Mr.Rosa just made.That will be the subject of our meeting in the third week.Katz, what do you think?The expectations of our constituencies are on our shoulders.
```

### [77] hash=`7504da054e70fb58`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Fear of the Arkanists has grown due to the attacks by Manus Vindictae in many regions.It's not ideal for us to implement the peace policy and promote the arcane technology.To maintain the Foundation's reputation, we have to start with the registered Arkanists,Strengthen the regulations and show the public that Arcanists are reasonable and trustworthy.That is why I am opposed to the draft.Inspiring.
```

### [78] hash=`6e781244fbb55782`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
However, what a shame.None of you have realized the key factor in this subject.What is the key element that decides whether this proposal will be approved or not?Manus Vindictae?The constituents?No.It's far simpler than those.It's Verton.According to the proposal, Verton will become the only tie between these unregistered Arcanists and the Foundation.As the number of Verton's field missions increases, she will inevitably get in touch with more and more unregistered Arcanists.
```

### [79] hash=`84018385679d4d81`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
That is to say, outside the Foundation's jurisdiction, a group of people is getting stronger each day.And armed.Her attitude towards the Foundation will be the key to all the issues.Virgin received her education as PDM from an early age.She has a clear tendency.Yes, that's what I think.That's also why I have asked someone who can provide a valid argument on the issue to join us.You may come in, Saneto.
```

### [80] hash=`a44f0bd116cb447d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Good day, Madam Vice President.Greetings to all committee members.May the peace be with us.The Timekeeper is still in treatment.Before she is restored to health, I appoint you to take care of all the relevant matters on her path.Copy that.Now, ask you some questions.Please answer them truthfully.Clear.Based on your observation, do you or do you not think the Timekeeper has been loyal to the Foundation?
```

### [81] hash=`4548e516a0146d3b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
All the students of the School of Primary Defense of Mankind are devoted to the peace of mankind.We have pledged life-long allegiance to the Foundation that leads the cause.That's not what I'm asking.Let's put it differently.Why do you think Verten would provoke other students to rebel when she was in school?I do not know.I'm sorry.After the incident of the storm, why would Verten show reluctance to invite the unregistered Arcanist to join the Foundation?
```

### [82] hash=`6b420279145276b6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Because, um...At one point in her negotiation with the Manusmen Dictae, Verdin has agreed to join them.What do you think her true intention was?That'll be enough.I believe we all have our answers by now.Madam Vice President, according to our investigation of the event in 1929 and Timekeeper's report,it is highly possible that Arcana of Manusmen Dictae has the arcane power to influence the sanity and consciousness of others from a certain distance.
```

### [83] hash=`8e9ef00c8af34f46`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
She is able to exert an irresistible psychic influence on others through short conversations.Timekeeper...Timekeeper was under huge threats at that time.I think all of her responses were out of her survival instinct.This is also one of the survival strategies that have been taught in Chapter 1, Book 3 of Introduction to Strategy edited by the School of Primary Defense of Mankind.I see.You may leave the room now.
```

### [84] hash=`86eb3d823486ff71`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
We appreciate the information you just added.You've always been an excellent student.We are very proud of you.Now, it's time to leave and rest.Copy that.What a controversial issue.What's your view on this, Ms.Z?In my point of view, Virgin does have doubts about our current system.But doubts doesn't mean disloyalty.In fact, if we want to further expand the staff to contain against the maintenance of Vendictae,
```

### [85] hash=`e48dbd17f2b50639`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
we need flexible management.Apply customized standards to Arcanists with different backgrounds and different training objectives.Through this, not only can we remove the Dock of Verdun,but also ease the tension between the Foundation and other unregistered Arcanists.You have been very thoughtful.Carry it out, then.I'm looking forward to the upcoming debate.The divination requires all of my concentration and my energy.
```

### [86] hash=`307ac99257d80d49`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
The high tide driven by the moon will be here soon.Let's see.It should start around 20h45.There are three minutes left.I must purify the sphere of occultation when the tide starts to rise.If I want the divination to be exact.If the moment is key, whoever it is, I must not be distracted.Concentration!Eyes closed, well concentrated, imagine my body going up and down at the rhythm of the tide, blessed by the moon.
```

### [87] hash=`bdbe1ebbd8016ab4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
It is on the other side of the sea, waiting for me to find it.This is the moment to burn incense.Appear in the occult sphere!Matilda, are you there?I'm sorry, but I think I heard your voice.I need to ask you a favor.Could you please read the future for me?It's in the silver pot with them on mine.Okay, now sit opposite me and gaze into the orb.Okay.Are you here to confess, to interpret a dream, or to seek the prophecy of the crystal?
```

### [88] hash=`85ce15f3568b1a27`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
I am here to confess, and to seek the prophecy.Tell me about the vision in your heart.The vision?I see myself falling.There are two broken decks.They were originally one piece.Every time I get closer to one deck,the other one sinks.People on it will fall with it.I can feel the coldness of the deep waterand the pains when they struggle.Are you sad about it?I feel fear.I see.Which deck would you like to approach intuitively?
```

### [89] hash=`f21f63201c12dc91`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Can you recognize the people on deck?I...there is something bright on that deck.Just like Timekeeper and Druvus.It is warm there.You are attracted to it subconsciously.It guides the way of your heart.What about the other?The other deck makes me feel comfortable, as if I have spent a long time there.I can trace back every step I take.Perhaps that symbolizes your senses.Soneto, are you having trouble making the choice?
```

### [90] hash=`fa25d3decb16c03b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
I can see the conflict between your instinct and senses.Then did the committee's meeting today?Anything happened?I said something wrong.I was not properly prepared.I was unable to help timekeeper and drew thisInstead I created a deeper misunderstandingWhat choice should I make?to resolve their conflictstalemate like thatReally scares me the bright deckCloser and larger.Have you ever thought about following your heart?
```

### [91] hash=`455a89c4a92b901e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Sonneto, maybe you can try following your instinct for once.Maybe something unexpected will happen.I tried.Four years ago, I let them go.That was the worst decision I have ever made.I am ready.Please tell me the right choice.Okay.The reality has shown itself.Take the path you have already taken.Walk the way you have already walked.You shall benefit from listening to the voice in your mind, as it is not yet time to talk.
```

### [92] hash=`0f7e3888017721ba`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
Listen to the voice in my mind.I should not have hesitated.Thank you, Matilda.Your divination is very helpful.My mind is very clear now.But then Matilda buonished much earlier.For your information, those seeking my help must make an appointment at least 15 days before the divination, otherwise, they won't even get to see me!You were very serious during the divination.Even your tone was different from usual.
```

### [93] hash=`9e3709e3ebdcb012`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p9`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜6~10）

```text
However, I am more familiar with the way you talk now.It reminds me of our time at school.Thank you for making time for me, Matilda.If you need my help next time, please let me know good night
```

