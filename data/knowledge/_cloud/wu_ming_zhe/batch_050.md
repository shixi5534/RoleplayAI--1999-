# 剧情图谱抽取 · batch 050

- 角色：`wu_ming_zhe`
- 批次：**50** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.0」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_050.jsonl`

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

### [0] hash=`f3e96e6b14732ba0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Richard tends to opposeGloria tends to supportBlack Agate tends to opposeUso neutralThe situation doesn't look goodDo you have any news, Mark?Someone is spreading the minutes of your last meetingI didn't get any direct evidence, but apparently every voter has read the anonymous minutesThe topic about Vertin, it has become a great disadvantage to us.Double embellishment, a four four point double low approach.
```

### [1] hash=`cb2b8b4d6952857b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
No wonder that the draft goes through so easily.To reject the draft during the committee meeting does not actually address the real problem.The House of Integrators can still resubmit the draft during the next legislative session.So she is planning for the long term.To bring down the voting stage and make it a plan that is totally abandoned.I'm afraid so.A draft that has failed to win votes can hardly win the trust of the House's reviewers again.
```

### [2] hash=`b593e21b98de527d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
And of course, it won't be submitted to the committee.Did anyone make any actual move yet?Not yet.The minutes only changed their preferences.But the number of those who have taken a stand still remains the same.Just as I expected.This draft is not about Burton, but a promise to the future, about how to balance the benefitsbetween different interest groups.To reach that, we need to meet the expectations of those groups who have a need for flexible
```

### [3] hash=`9455675ecb8c3b13`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
management, and also appease conservatives and not shake their confidence in controllingthe overall situation.Actually, I have an opportunity to change the game now.Opportunity.I hereby challenge Delegate Mark Hall to a public debate on the revised draft of Storm Reformation, Manpower and Discipline.This draft of his will bring unpredictable risks to the Foundation, yet Mark himself seems completely unaware of it.
```

### [4] hash=`66eaa92f04e97dd3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
I believe it is necessary to make such risks public in a legal way.See, I knew they were going to escalate Burton's issue.You want to accept this challenge?All the internal media are reporting the news.If I step back, they will definitely humiliate me and take advantage of the public opinion to undermine the draft.Mark, that's a menacing move.It is calming for us.No matter fight or flight, they have comprehensive preparation for this.
```

### [5] hash=`cca01942d03b6ee7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
I would suggest taking the long view and not jumping to conclusions.But defense without attack will never bring us victory, Madam Z.I've always wanted an opportunity to defend the draft in public.Concerning the questions they implied about Vertin, I've collected more than enough cases to refute them.Myth-leading questions twist people's opinions.It's time to tell them the truth.You have accepted it.
```

### [6] hash=`62fabc46f4abb43f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Was it in front of the media?I was there when Pedro challenged me.So were the media.Don't think it's going to be a complete mistake.It is a crucial debate.Do your best.You don't have to come along with me.I'm here to repel the pests in the woodsIt's part of my daily routineThank you for your kindness, Mr.ThisIt is fun to stay in Ms.Burton's suitcaseReally feel like seeing by the way the penchantWhat are they?
```

### [7] hash=`7108bd3b78e9f89c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
I've heard of a kind of giant worm called the Tapsal worm.They live in cavesI'll be long and their heads are like cats.Be very careful if you see one.Both its skin and breath are toxic.I have never heard of such a terrible worm.Hopefully we will not encounter any.Too disinfesting this time.Oak processionary moths.Perhaps a few gray squirrel cubs.It's not enough to only rely on potions and arcanum to keep the woods in peace.
```

### [8] hash=`fda8ebbc1e34ca7f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Oak trees reside here.And everything will change with it.Animals that live in symbiosis.Fungi that depend on each other.All of them live in diversity by the day.Oak processionary moths.They are preying on something.This apple is deeply grateful for what you've done.I almost thought I was caught in a nightmare.This apple has never seen so many moths.This apple is going to have PTSD from insects.They are very sensitive to the scent of sap.
```

### [9] hash=`7ddd9bcbd4ee161b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
With all due respect, even among all the plants, Mr.Apple is quite attractive to insects.The scent that attracted under Mr.Apple's invisibility didn't work.Mr.Apple, did you find out anything?Yes, Ms.Druvis.I brought something insignificant.As we planned earlier, I disguised myself and reached the office building next to us.There is a device to detect arcane power at the entrance.However, this apple pried out what we needed from the guards.
```

### [10] hash=`3dc04ca98af5b33b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Did Ms.Vertin win on that voting list?Sadly, not yet.It's not time for a formal vote.Everyone is cautious and remains neutral.Apart from that, there are some rumours in the Foundation.They are not very favourable to Vertin.It sounds as though the situation that Madam Z handles is more complicated and volatile than I thought.However, the votes have not been lopsided under such bad circumstances.Perhaps that means the Arcanists who share our aspirations are not in the minority.
```

### [11] hash=`e4d26226b07e811c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
That said, I'm afraid we are starting a protracted war, Miss Druvis.Yes, I know.I've taken inventory of the supplies.We can still hang in there for four weeks and a half.Although they have cut off the water and electricity supplies in the building, westill live on the resources in the suitcase for a while.There are fewer guards destroying the woods,probably because the abidus works.What worries this apple is that if the procedure to finalize
```

### [12] hash=`6527c1ba0bfd8cb0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
the draft takes more than four weeks and a half, we would...We would then survive by graduallyshrinking our territory until Madame Z's draft is officially approved.We have chosen the thornytrail.And so we are destined to burn our boats and never look back.Burton, she isworth fighting for.For this point, Captain and this apple have absolutely no disagreement.Then this applewill keep scouting around for updates so that we could respond in time.
```

### [13] hash=`6f8412c13c921dca`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Hmm?What are you looking at, Miss Sotheby?Let's go back to the deep woods.Isn't that scarf a bit too high profile?The other debater of the day is the delegate of the House of Integrality, Mark Hall.Over the past ten years, he has served the Foundation by drafting countless acts and conventions.The topic of the debate today, Storm Reclamation.Manpower and discipline is exactly a work of art.Alright, both sides are seated.
```

### [14] hash=`91b91a5aaa9fba46`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Before we start the debate officially,I suggest we give Mark, the draft writer, an opportunity to introduce the draft.Would you please, Mark?With pleasure.Storm Reformation and its advocates believe in such a goal.In this ever-changing environment, smitten by the Storm,this draft will help the Foundation win the trust of a considerable number of Arcanistswho have different backgrounds and abilities in a more efficient and stable way.
```

### [15] hash=`c9190b4670dbda4d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
That is exactly where I must raise an objection.The draft has a huge risk which Mark Hall has not realized at all.No sir, I totally understand what you're trying to say.You have put forward several questionable arguments to prove Verton's suspicion of disloyalty.In response to that, please allow me to invoke the following cases to prove Verton'scompetence for leading the unregistered Arkanists.Please turn to page 373 of Burton's personnel file.
```

### [16] hash=`0f630053063b9ccc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
As you can see, since Burton became the timekeeper, the number of unregistered Arcanists she hasrescued so far is 63.That is a number unmatched by that of anyone present.If that's not enough to prove her loyalty, let's continue.I have to say, Mark, you have completely misunderstood my point of view.I don't care what Burton has done.but the feasibility of the draft.According to the existing regulations,
```

### [17] hash=`bcaa83f71ee95380`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
the duties of educating and disciplining unregistered arcaneistsare taken by the School of Discipline.While you suggested in the draftthat Timekeeper's personal teaching would replace the current collective training,have you ever thought about the budget that we could possibly spend on it?The Foundation spends an alarming sum of money on education every year,and there is no way we pay extra for personal training.
```

### [18] hash=`36c8cb1bea258dd0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Oh, what budget?I don't see why we're talking about budget all of a sudden.Did you really read the draft?I didn't mention a word about budget.Of course you didn't, which exactly proves you have never realized the risk I just mentioned.Oh, it seems the real topic of the debate has just surfaced.I believe everyone in the hall is looking forward to where it goes.So, Mark, in terms of this point, we would like to know your real thoughts.
```

### [19] hash=`711beb92d43b0be8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
The Blackstone is left there alone.The last move is also a defense in panic.If I were the player, what is it?Senato asked me to give it to you personally.Dear Madame Z, With this letter, I send you my best regards.I have been instructed to manage affairs on behalf of Timekeeper during her treatment.Please let me know if there are any missions to alleviate the situation.I will do my best to meet your expectations.
```

### [20] hash=`954634132392e2e7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Sincerely, Saneto.Good news.Oh, you're also here?Yes.I am taking combat drills with the artificial somnambulism training system.Six hours?I'm not the only one goofing around.No, I'm not.I am not goofing around.I am waiting for orders.Well, much luckier than me.I have so many things to bitch about.Bitch baklusha.Have you heard it?Literally me.I should have turned downthe offer when they promoted me to the Foundation headquarters.
```

### [21] hash=`ffc289da08dde96a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
They don't haveany field missions for a flying witch.Is it because of the provisions oftalent protection?Only God knows.House arrest may be a better name.Look,since we're both bored to death, do you want to have a try at somedifficult things what is it this have you tried the artificial somnambulismjoint training put on the helmet together and switch to multiplayer mode twooperators can take on the harder training mode more insane enemies like
```

### [22] hash=`7637c16863e64ef0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
playing in the arcade okay shall I turn this red knob what is an arcade niceController, but I shot I'm entering the zone now.It's been a long time.Why not have some fun?You better get it togetherDon't fail mechokingCenturies die.Sorry.I cannot do math nowMy mind goes blank who would expect these an Eto would have a brain fateHave you heard the result of the debate?I heard that.The number of people opposing the draft significantly increased after the debate.
```

### [23] hash=`2dba96e65a2540a3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
It's not going well.Soon will be the voting session.The opposition has taken the lead.I hope Ms.Druvis can hold out.You visited them?I submitted a request to enter that building.The system arranged guards to accompany me to ensure my safety.The moment they entered the building, they started sawing the trees, saying that they need to carve out the path.Since then, I have not been there.Four and a half weeks.
```

### [24] hash=`7b827261da448511`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
After that, they can't hold on for any longer.Really?In that case, the vote result has to come out before that.Hi.May the peace be with us.Do you mind giving us some privacy?Do whatever you like.based on the severity of the circumstances.Fines will be imposed and the offender's salary shall be deducted accordingly in minor cases,while detention or expulsion shall be imposed in major cases.The penalty also depends on what is damaged.
```

### [25] hash=`8c4c21d975cf8183`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
For example, production tools, household goods, buildings, equipment and facilities, etc.These are the properties that involve less cost and limited influence if damaged.If the number of people involved in a brawl is equal to or less than 8, and there are no major casualties, the penalty will be minor.May I ask what happened?Why are you asking this all of a sudden?Nothing.As I said, bored to death.
```

### [26] hash=`82a006c606136842`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
So bored that I have been paying attention to the Foundation's regulations.Even the flying manuals failed to win this much of my attention.So long, Sonneto.Hopefully there's good news for us next time I see you.We are falling behind even further.A vote or two won't help us turn this around.I know.The move to deny was indeed useless.The Arcanists that were on our side have defected.We misjudged the situation in the debate.
```

### [27] hash=`f69267c64ece875a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
We're going to seize the opportunity and the initiative.To seize the initiative may bring us the chance.That is to say, don't pull back, don't jump, even when they're attacking, but to focuson the bigger picture, to win strong positions, the black tsuke, then the white hane, andthe black counter hane here, the white stand, through these moves, I see, the move to dayeleven can save us more than ten moco stones, we can still win within ten moves.
```

### [28] hash=`559f3874a999e631`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Yes?Are there any other things we can do?We need an influencer.A leader who can win us more than 10 votes.Give me the file of the uncommitted leaders.Including those who were neutral about this issue in the beginning.Okay.No.Too young to be convincing.Noni, head of the Natural Resource Committee?There are only three of them in the group.Center Bernard, leader of the mankind caucus.Yes, he can be your man.
```

### [29] hash=`df5c1b47bacbad33`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
He is eloquent and leads a group of 11.All of the 11 are his loyal followers.Why is he uncommitted?I thought he would be the first to vote.Perhaps they believe it's a sure bet.Find out what he's been up to.But, Madam Z, are you sure you want to cooperate with him?This doesn't make any sense.We don't even serve the same group.Mark, we're all serving for the Foundation's future.I just want to know what he needs now.
```

### [30] hash=`d419a36981d8011f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
The office in Chicago, US.He is trying to cover that region with his influence.Bernard believes the employees there are guilty of serious dereliction of duty.They discriminate against humans of different classes,and are suspected of committing electoral fraud in collusion with the local capitals.The Supreme Court's investigators have already intervened,But they cannot go out due to the storm right now, so the case is pending investigation.
```

### [31] hash=`1761b72fbc0b903d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Chicago office.I see.Great.Exactly what we can help with.Through what?Through Sonnetto.I have a meeting with her on Friday.This may lead us to a win-win situation.This is for the upcoming victory.It will be the final vote soon.It's a stunning victory for us.Cheers!A staff of mine is willing to testify as a witness.Her report can prove your pork.Strong enough to prove their negligence?It depends on the special prosecutor.
```

### [32] hash=`b8093c01cb5142d9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
But the evidence is strong enough to prove that you're innocent from setting up others out of your personal interest.Looks like you've got your own little work.They don't serve humans or arcanists.They're just puppets manipulated by money.I wanna bring order back to that place.But you're asking for too much.Eleven votes.We're on the opposite side.I can never persuade all of them to vote for you.Besides, the court session of the Chicago case starts later than the final vote.
```

### [33] hash=`5b1074e04fbf7aee`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Don't tell me you want the service before you pay for it.Don't worry.You can vote after testifying.How are you gonna do that?I will do what I can, in my power.The vote won't start so soon.I can drive for nine votes, or ten,for the appreciation of your political resourcefulness.Good luck making a better Chicago office, Bernard.It's Pedro.Come in.I'm here to report the situation so far.Some neutral parties have tilted in favor of the draft.
```

### [34] hash=`5210c97d4c77d49d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
How many?Not a lot of them, but enough to make the votes even.They've always pursued revolution in the foundation.Looks like Mark has finally persuaded them.I heard Ms.Z has been working hard on canvassing too, but the number of non-conservatives remainsthe same.We don't have to worry about that.I believe we will still prevail in the final vote days later.What about the other groups?Still functioning as usual.
```

### [35] hash=`5fddd259ee8c4694`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
Nothing special.By the way, Bernard and his men paid a visit to SPDM.I didn't get to talk to them.Thank you for the report.She's never been so persistent.Do you know why she's been so different this time, Pedro?I didn't realize you had time to invite me to play table tennis.Or are you actually here to lobby, Madam Z?I'll say both, Katz.Back then when I was a student,I'd often invite my classmates to play ping pong after we left the laboratory.
```

### [36] hash=`dfbd74da6377625b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
A cold shower after getting soaked in sweat is a piece of memory I can't forget.You remind me of the old days in the table tennis varsity.You're the only one I can practice with here.Serve it, Madame Z.Let's compete.Backhand chop.Great, great.Again.Ready to go.Nice shot.We're planning to revise some articles in the draft.Which articles?The article is about strengthening the control of registered Arcanists.
```

### [37] hash=`1dabb087c22e1509`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
You're right.We do need to improve the credibility of the Foundation in the outside world.Tell me more.The Timekeeper's power to discipline should be transferred back to the School of Disciplineand the Foundation.The Foundation will conduct a unified risk assessment on Arcanists to ensure thisteam is always under control.But in fact, it still belongs to the Timekeeper, right?That is our minimum requirement.
```

### [38] hash=`9b607899aef96d19`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
And you will not change.I didn't expect you to compromise.It's not a compromise.It's a reasonable amendment to the draft.Transferring the power of education and discipline to the foundationwill help lower the budget and reduce the pressure on virtually.And you would even lobby an opponent, me, for this amendment.A reasonable appeal shouldn't be rejectedjust because it is raised by a different faction.
```

### [39] hash=`9936b6c9ae171521`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p10`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜11~16）

```text
The foundation needs solidarity, not contradiction.If the draft is meant to pass,I will do whatever I can to make it meet most expectations.Just like this ping-pong.Friendship first, competition second.Legislation shall serve the people.You have my vote, Madame Z.A vote is not the only thing I need, Katz.
```

### [40] hash=`7f53065179157957`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Constantine, has the voting started?You see, here is the number of votes I haveestimated.The pro-drafts will lose by five votes to their opponent.Don'tforget our bet.The one who loses will pay for the new stamps.The final voteis not today, I'm afraid.Z's speech is still ongoing.She's just started thepart on Article 3, Section 5 of the Rules of Procedure, but the speech haswill only have two outcomes.
```

### [41] hash=`cc96f63f434d9c05`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
It is either one of the parties wins over two thirdsof support and gains victory,or both parties get stuck in a tug of war.If this tug of war doesn't end with a clear outcome,the Storm Reformation will end up completely deadand forbidden to be discussed within five years.Are the stakes getting too high?Madam Vice President,Mr.President came back from the Pax House.I will go see him now.He's waiting for you in the office
```

### [42] hash=`0e98e7ad67d26576`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Good day to you sir.May the peace be with usMay the peace be with us.Are you feeling better these days?I can still hang in for a few yearsThank you.Are they doing all right?Just as usual nothing to worry aboutI'll stay in the foundation these months.The agenda is well arrangedThere is something more important that I must tell you in personThis is their judgment?I have no objection to it.Hold tight, my friend.
```

### [43] hash=`cdfa329b9cbdc942`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Excuse me.I have to admit, I was surprised.Thank you for telling me this.As a witness?Yes.Your report means a lot to him.I can provide the report, but I have no experience in court hearings.If I say something wrong, will it affect the special prosecutor's decision?Sonnetto, testifying is not taking exams.The court doesn't need a skillful witness.Just honestly tell them what you saw.Focus on the point, and don't distort the facts.
```

### [44] hash=`7986998581443bd5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Supreme Court, they value the sense of justice of the youth.Sense of justice?A noble quality you have.I will do my best, Madam Z.I was one of the parties involved in the 1929 storm incident, I submitted a detailed report of that.He searched the database and found the report, so he made a request for access to my supervisor, Madam Zee.Madam Zee asked if I would be willing to provide the report and attend court as witness.
```

### [45] hash=`25f05002693b0491`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Could you tell me the reason why you agreed to testify?I, my immediate supervisor, is having a long-term treatment, and there are more time slots available on my schedule.I am happy to be able to make a difference during the time, and defend the established facts.More importantly, I personally believe that there is still much room for improvement for the Foundation's office in Chicago in the United States.
```

### [46] hash=`d012218dedaf86eb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
What is this, Miss Sinatto?This is a record of all my travels from the time I received the promotion order in theresearch center to go to the office in Chicago in the United States, to the time I went backto the headquarters of the Foundation when the storm came.This is the field report and diary I wrote about the storm in 1929.What point do you make?I would like to prove that the Foundation's office in Chicago in the United States
```

### [47] hash=`0ba70cb341e784a9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
violated the declaration, fight for the peace and order of mankind, and the rightsof some humans and arcanists.Tarnishing her reputation!I request a debate duel.I won't allow her to distort the truth like this.Mrs.F, I haven't checked these files yet.Silence, please.Your Honor, you can examine the files one by onewhile we're having the debate duel.I can't bear to see the long history of our office
```

### [48] hash=`a8e08393c80f0c56`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
slandered in this way by a newcomer.I demand a duel with her.Senato is an investigator with rich combat experience.There is no good dueling with her.Do you accept the debate duel?I have no objection, madam.Please to the stage, duelists.The debate during your duel will be faithfully recorded.Three defeats in the debate of one side will end the duel.You have the floor now.I have decades of historical materials of the office and know it better than anyone else.
```

### [49] hash=`fc8cae35fd958c92`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Well, you were in office for just...three days?What makes you think your testimony is more valuable than my materials?Whether the history is long or short, it does not affect the validity of the facts.Article 78 of the International Law of Procedure states,Any individual who has knowledge of the case and has an independent will is obligedto testify as witness.Hereon, I shall prove the value of my testimony.
```

### [50] hash=`76d644b41db8095f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
February 14th, 1929, after the storm.Half of the staff in the office were absent from work.I learned that this was permitted by the director.They were required to sell alcohol and speakeasies at night to make a profit for the office.The malpractice at daytime was therefore tacitly approved.This can be found in photo appendix number 3-12-8.Slander!It's individual behavior of the employees who do not comply with the rules.
```

### [51] hash=`4b119f17aee77402`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
That morning, an hour and a half before my encounter with Timekeeper,a procession appeared in the square in front of the office.They were mostly humans, with a few arcanists.They were protesting against the high registration fee charged by the office for registering their identity information.To be honest, you can find similar problems in any large institution in the world.As long as we manage the office in a different way or change the staff, it would be improved.
```

### [52] hash=`a433be57f77b2521`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
But you claimed that we violated the Declaration of Peace.This is pure slander and gross defamation!I am not slandering the office.Schneider...You refuse to offer a human...No, an entire family, the shelter of the Foundation.Schneider, a friend we met in Chicago.She once chose to join the Foundation under the pressure of both the Storm and Manus Pidicte.But instead of offering any solution or help, you just gave her a rejection letter.
```

### [53] hash=`9576e45b03871c72`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
I found this letter in her suit pocket.It had a small line written on it.Poppers, fuck off.I had completely no idea what this was about, not to mention the fact that no one in the office had ever heard of the storm.What help could they offer?This particular case, you should have reported to the headquarters or to the investigators out there, instead of doing nothing but leaving an insult.I do not understand why there was such wording on it.
```

### [54] hash=`23435d499e902b95`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Was it because she did not pay enough shelter fee to qualify for sheltering?Or was it because the wand she used was transformed by Arcanum, which made you think she was an Arcanist?Does not the Declaration of Peace say, everyone strong or weak, rich or poor of any race deserves a helping hand so that the existing peace and order should be maintained?Humans, if only they had made it to the headquarters sooner...
```

### [55] hash=`8420ee0b04196ae3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
In the particular circumstance at present, it's impossible for the headquarters to takein humans from all over the world.But you bring out a possibility.A possibility better than anything that happened.Thank you very much for your testimony, Ms.Senato.And also for the debate, Mr.Seth.I seem to be too emotional just now.Ms.Senato, you brought us a great debate.They have remained uncommitted to Storm Reformation so far.
```

### [56] hash=`f7847788bd8978d3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
I thought they wouldn't bother to attend.The opposition side doesn't need a dozen more votes to win after all.But the advocates of the draft do.There will be a new draft given to you in two hours.I brought together a revision group last night with some hired experts.We have adjusted some of the articles in the previous draft.of the Timekeeper's special team in Section 1, on page 40.Every Arcanist assigned to the Timekeeper's department
```

### [57] hash=`70332a8b3ec67b8a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
will be put through the Foundation's risk assessmentand graded accordingly.Ordinary Arcanists only need to receiveprimary artificial somnambulism training.The more extraordinary ones will be sentto the School of Discipline for re-education.Delegate Mark also submitted another edition,which was quite similar to this one.Remember, we have to make everyone aware of these changes before the voting starts.
```

### [58] hash=`50155afb39bf289f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
We have to make sure this version of the proposal is the one that gets the final approval in the end.Understood.Can't believe this is happening.First revolution targeting our canists in the past decades.Don't forget my stamps for this quarter, Constantine.Two more hours.Okay, kebab.Some of the potatoes we planted have turned yellowStruvis said this is the harvest time.Let's dig them out and make shepherd potato
```

### [59] hash=`00d869b073075d1c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Vegetable don't want them anymoreI've been eating healthy salads for a monthI want rich juicy meaty sinewy savory sizzling meat wait goodWhere's that smell coming from?Krita is a type of meat roast it over fire and a square meal is hereIt smells so good!What can I do?What's going on, Miss Sotheby?Why are you here walking around alone?Um, where is Captain?Good to see you here.Regular said she smelt meat for the forest to catch critters.
```

### [60] hash=`226fc987089fe547`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Waffle.It has been too long since we last had Dr Pepper.Does Captain finally start to have a senior moment?Let's hurry over and take a look.The smell of food is unusual.It's verdant over there.There may well be other dangers lurking somewhere.This is weird.Where on earth does the smell come from?That's the lair of carbuncles.They've been stirred up.A bumper harvest of critters?Hold on, Captain.We're coming.
```

### [61] hash=`cf18f2a946a64dc9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Edible!I did smell the sizzling meat.It's somewhere around here.Right around...Oh.Hi.Where are you?Lillia, what are you doing here?I got you something good.It tastes so good.So good.I barely know what Greece is supposed to taste like.Great god of rock for his blessings.This pirate finally gets some meat.Huh?It is me you should thank.The goddess of victory who soon brings you freedom.Bring us freedom soon?
```

### [62] hash=`9ec9bcb3f5a10a19`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
may I ask how should I interpret your words you want some thank you so muchfor coming alone and providing us with supplies Lillia however please tell uswhy you were here did madam Z sent you already been four and a half weeksright this is not the first time I visit you guys here the one hiding inthe shadow last time it's you I wonder how much longer you can hold onfor verting you see saying is one thing fighting is another I've seen many
```

### [63] hash=`ce47775946e033ec`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
deserters way too many crying out loud peeing their pants drooling all over ontheir rabbit food but you guys are different you actually did it youconquered places in the foundation defended your own places and putpressure on those in white till this day, the last day in these four weeks and a half.That's the Stal'naya Volya I appreciate.If I didn't come today, would you eat yourboots tomorrow?Of course not!
```

### [64] hash=`16ec9a65347a9d82`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
We still have potatoes, almost ripe!Thank you for your kindness, Miss Lillia.May I take it that you are coming to bringus the good news?Is there a final result for Madame Z's draft?So far as I know, Madame Z hasn't given up yet.Just like you, when she gets serious, she looks like a fierce doe.But I already lost my patience.Tons of processes need to be done before it can be performed.Even if the draft is passed at the final vote, as long as Vertin is still on that
```

### [65] hash=`6869913e75ea0e2d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
bed in the ward, you're just an isolated island.Everyone can step on you.Take care of them for me when necessary.That's what Vertin said when she gave me the vodka.It's time to deliver on my promise.Are you going to do something dangerous?I think that is worth the risk.I've been waiting for this moment for so long.Someone needs to wake up from the dream.Final round of the vote.Voters, please hurry up.
```

### [66] hash=`8a7b6a0e60d38a8b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
One minute to go.Please be responsible to your votes in every round.Vote as soon as possible.The draft advocates have more votes now, but they still need more than that to meet thesuper majoritarian requirements.Please vote now.30 seconds to go.Final countdown.This will be your last chance to vote.Please, hurry up.Reformation, discipline.Wake up, verzen.What's that sound?What's going on?That was a quick reaction.
```

### [67] hash=`72c7f1752b1d8bdf`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
1, 2, 3.Well, relax.I'll keep the acceptable damage under eightWhat is this?Everyone get your gear formation one capture the intruder bring it onLet me have my dear long lost real fightrightLet me have my dear long lost real fight Eden each momentFrom one five to five calling for backup.Hey, no backup.I need to strictly follow the damage control standardWell, Lillia?Finally awake?Nice!Time for us to leave.
```

### [68] hash=`87188b3ab30a0117`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Come here and sit on the broom.That's behind me.Grab tight!Don't say I didn't warn you if you fall down and die.I'm whining for Constantine.Oh, good weather.How do you feel?Getting used to the light?Feels so good.This is just an appetizer.I'll be gentle since you're just discharged.They were right.Good as new.They stayed up all night just to save you.I guess you're the only one who has slept tight.
```

### [69] hash=`793b04ca18fb1a83`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Madame Zia, Druvis, Saneto...From the bill and the protesting to countless debates, planning and...Everyone is holding their umbrellas for you, Burton.The storm, it will pass one day.Thank you.Thank you all.Yes, everything is going to be alright.Enough flying, time to head back.What are we doing next?No idea, meet your friends first?Fight with your comrade in arms.You're no danger ahead.Up tight, I'm going to speed up.
```

### [70] hash=`138fa97c791a92cf`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
How are you feeling?Better now?Killing me.Here's water.Captain, sip please.Don't put too much pressure on your esophagus.This apple told you not to swallow leather in haste.I'm alive!I thought I wouldn't be able to see the sun tomorrow or see Vertin discharged.Because Lillia...Wait, whose voice was that?Is it...Vertin!You silly git!Now you come back!Vertin?Vertin!Are you feeling okay?There was a lot of equipment connected to you.
```

### [71] hash=`f3e96cde8e82a2fe`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Do you feel any discomfort?Do you need any nutritional supplements, Miss Burton?We have a lot of healthy fresh salads here.Why did you come back for?What are all these white pigeons doing up game?Wait!Just wait!I'm fine.It was a fiddle.Just a bit of a headache.Nothing else.It's good to see you again.Thank you for being here.We're waiting for you.You're the only friend we have in this world.Welcome back, Burton.
```

### [72] hash=`522fc10519db1d8a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
We have good news to share.This is good.This is great.May I ask what good news?The passage of the Bill, Storm Reformation, Manpower and Discipline.Once it's approved by the PAC Security Council, it will become law.Your friends and you will enjoy more autonomy and a life with even fewer restrictions.You will also have a more respectable status in the Foundation.Ms.Z will fill you in with more details.
```

### [73] hash=`dbf8ee2fc477d765`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Thank you for telling me this.What about the treatment?Treatment?Didn't it finish just now?This treatment has an investigative purpose,and the timekeeper has passed the examination as a safe, low-risk individual.As Ms.Zee has said, Ms.Burton is strong enough to be the timekeeper.However, you will receive punishments for the damage to public property.I suggest you heed it as a warning.We should say our goodbye.
```

### [74] hash=`b6ba248219f774f1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p11`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第四章.老虎的金黄｜17~23）

```text
Please rest well.Seems like the dove of the White Marble House is paying you a visit.What do you mean?Nothing peculiar.It just means you have come to their notice.Yes, that's right.I got it.I'll reply you tomorrow.Please wait, Madame Zee.Madame Constantine asked me to give this to you.Did she say why?no she didn't explain it wait I think she mentioned it's September 11 in theChinese calendar today I see please send my thanks to her I'm glad to witness

your progress
```

### [75] hash=`8b5f58e8322f1ac7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Little rascals fell asleep.You notice that old gum sticking to their shoes like crushed leeches.Who does?I'm very glad that we are on the same page on this.Describing an abandoned carbohydrate gum won't make anyone come.So let's skip to the next line.Have you noticed the gravel mixed into the gum base?The off-white sand.the synthetic waxed elastic fiber.In the South Bank, there is only one placewhere such a politically symbolic floor is laid.
```

### [76] hash=`9dcc70287b0c59d3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
St.Pavlov Foundation.Just like every day in the past,it's very lively here in the square.Speculators who advocate mankind supremacytry to get the attention of the foundationthrough demonstrations.They are on the same side.However, the Foundation won't give themwhat they want.They even sent a little girl to go through the motions.Yes, yes, no one will everignore them.They are honey-colored.They are the morning sun in California.
```

### [77] hash=`c052b20439ce56d3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
They are thedazzling spot on the dough that you'll never catch.For those hypocrites, the littleThe best place for her, a position that is too marginal to be marginal.That's the best portrayal of the second generation immigrants in the 20th century.She is the good girl you already know, orange hair.When she's deep in thought, she turns her pen like a nimbleball in a magician's hand.She is puzzled at the guys shouting around her, but there's light in her eyes as if
```

### [78] hash=`69e07a013b63231b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
the air smells like tropical corals and wild oranges.That is not what's supposed to happenthis winter, but it's been in her mind, lingering, dancing, reminding her to keep on living.She used to be desperate.Defeat after defeat, her vigorous vitality won't fade away, though.At least, not now.Why did you pick up that cold, opaque, opalescent glass wine bottle from the ground at thismost critical moment?
```

### [79] hash=`71b4110307428005`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
The scream outside the parking lot, the friction between the brake pads and the wheel drumsor the story unfolding like Jalo films.Obviously, none of them are as impressive as this bottle.I can tell that you've got good taste.Even so, do you still want to give it a try?Every carbuncle you've ever met will appreciate your courage.Now, some cold liquid runs through your throat.It trickles slowly, most likely because it's thick, but the taste is much smoother than
```

### [80] hash=`fa315e4e8da12868`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
you think.Then, faint scent of absinthe greets your nostril, and maltose, and lemon thyme,and coconut sugar.It's as delicious as a present from the arcanist from New Zealand.And at the same time, your heart swells and you feel a scorching energy fill your windpipe.Your vision begins to blur.You kind of see the rough letter on the bottom, the Walden Potion Bar.Of course it's not alcohol.Alcohol is a mysterious taboo, but it will empower you to face the next damn reality.
```

### [81] hash=`ac663d62a71b4af2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
There are enough people in black outside.Enough to prevent any eavesdropping or violent conflict.Mrs.Greco glanced blandly over the 1, 2, 3, 4, 9, 10, 11 children in front of her.This is a big family, and it has grown bigger and bigger over the past few years, becauseof Schneider.She's Schneider's biological mother.You see her furrowed face like a hard stone wall, while inside the wall is all about a
```

### [82] hash=`00d3ccac29d08732`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
pious farmer's life.The Grecos are not good at dealing with gang affairs.They can't even figure out when their daughter became to be the backbone of the whole family.When Schneider took out $500 from her pocket and put them on the table, they were completelyshocked for the first time.Schneider, Schneider, the youngest daughter they seldom cared about.It's impossible to keep every child well fed.Schneider could not even get a piece of bread in the Eucharist.
```

### [83] hash=`2b50eb6781295370`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
But a good daughter will not let anyone worry.She sat on the bench outside the church and hummed.She found a way out for herself.She walked to the underground market, fascinated.she announced her new identity one day.The bread provided in some sacredreligious ceremonies.According to different teachings, it's sometimes matzah,sometimes fermented bread, or sometimes any kind of bread.Now, Mrs.Greco said,
```

### [84] hash=`5169f0ff89b5365c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
we live or we die.If Schneider comes back safely tonight, we will leave whenrises.The doors in front of us are closing one after another, but thebenevolent Maria will give us the ultimate shelter.My children, remembertoday forever.Her words speak for her status, but Mrs.Greco's eyes nevermoved away from that small Madonna on the table.Her clothes were soaked.4 p.m.A family is determined to start a new journey.
```

### [85] hash=`f53c589d82a38b16`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Be it's telepathy, maybeMaybe your soul is out of your body.Maybe you're back here.In the dark woods, the huge oak trees crack in front of you.Dry and pungent fumes billow out, swallow a lot of things, a lot of money, a lot oflives, family laughers, and a pair of eyes that once looked to the future.Dead skin, dead fish, upturning fishy scales, desperate, the wailing whales of aquatic animalsbeing boiled in the sea, your palm, those upside-down, towering barks like frightened
```

### [86] hash=`c53b4a88b7a63e68`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
cats trying to save their last bits of dignity before death, your touch makes them fall,No muss, no fuss, they've planned for this.They don't like fire, and they don't like staying on the cross for a long time.You still have so many questions you haven't asked her.But before you could, the war had begun.IQ being positive.Your optimism will help you achieve your goals.Oh, it's a surname buried in dust.
```

### [87] hash=`0ed567e98488e703`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
It has been shot by history.Even the living Cavendish Jr., who once sat in front of you, has taken off this crown.Get me not.That stupid name is so damn humorous.That young master with a pale face died.His insidious expressions grew day after day.He passed through countless hunger and suicide and the only thing left was decadenceThat woman gave him a promiseShe said a few words to forget me not and then traveled north and disappeared in the fog
```

### [88] hash=`5b67138bde294630`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
The Windy City was an unwanted sarcoma which she left behindOnly when the gun is pointed at his throat can he see exactly what's in his brainTherefore, he grants himself the freedom to revenge, revenge, revenge and to die.Now the sarcoma belongs to him.He swears to build a magnificent stage there.He is patiently waiting to put his meanness, craziness and quivers under the sun.Let's rewind the time to a few years ago.
```

### [89] hash=`46c635923588e462`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Trust me, you won't regret reading this story, you will never be offended by your humor.Okay, the past is waiting for us to look back.It's winter in the early 20th century.The gloomy rain never stops.The square on West Jackson Avenue is alive with people.There is an Italian Renaissance-style basilica.You rarely see so many people get together without making a sound.This is a black requiem mass.The priest is chanting the requiem, and the people mark a cross on their chests.
```

### [90] hash=`c841113c9f9db685`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
He was a father.He dedicated to a sinner of, or it shall give him eternal peace.A woman in a black robe turns to you and whispers.She turns back.Explaining this makes her unpleased.More and more people are queuing for the funeral.The square is alive with chants here and there.The Grecos are among them.They're covered by the dark cloud of long-handled umbrellas.Soon, their voices are replaced by whimpers.
```

### [91] hash=`69b7801e9c7e38ba`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
You can hardly tell whether their expressions are pleased or sorrowful.But you can't snide her.in the direction of Mr.Greco's broken left palm.Yes, it's wrapped with a bandage.3,390 feet away from the crowd,in the shadow of the church,stands the girl you want to see.She is pale and thin,as if she has just recovered from a serious long illness.Clenches, and a fire lifts in her eyes,fighting against the ubiquitous chance.
```

### [92] hash=`356c2088edf8b055`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
You don't know why she looks so, so furious.Is she, what, eleven years old?The mass is about to usher in the ultimate climax.It rains heavier.The priest opens his arms to embrace the sky.The Lord be with you, and also with you.Schneider responds in a voice that could hardly be heard.She puts her hand on her heart.This is the first time she responds to the Lord, and it will be the last.Nervous.All know something's gonna happen.
```

### [93] hash=`0fc81ff7477915e3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
With your, that, the brains full of weird ideas, somehow you can feel it.It's your special talent.The talent comes together with your sensitive nerves and rich emotions.Things are getting messy.New friends and old friends come one after another.And here you are.Fog rises.It separates the black and the white,just like separating two groups of bulldogs.They're turning around and around,revealing their fangs as if they're trying to tear their own tails apart.
```

### [94] hash=`484dbe2d9e38f075`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Interesting choice.It fits you very well, little freak.It works the same as fog, for example blocking eyesight, hiding secrets and slowing down thosewho want to get in and out.It also works differently, like hallucinating, intoxicating, and getting people lost foreverin a foggy, never-marked-on-a-map road.Sidious.But smart guys are everywhere, especially now and here.What we have to do is wait.Wait.
```

