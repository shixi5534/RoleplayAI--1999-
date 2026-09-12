# 剧情图谱抽取 · batch 079

- 角色：`wu_ming_zhe`
- 批次：**79** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.5」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_079.jsonl`

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

### [0] hash=`6cda634a8c75ab05`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
There is no doubt that it tastes better than gilded carrots and look at this army of royal guardsThey must be here to greet the great Dali clatterRoyal guard what is he saying?Ah, no kidding.Is that giant creature covered with spikes his royal guard?Thorny devils.The enormous creatures born in the burning sand of the stadium.They used to be mounts for the players, but it looks like they have forgotten their master after all these years of slumber.
```

### [1] hash=`000ee5364abaffc9`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
Enough talk.Let's put them back to dust and ashes.Be careful young man, an apple a day keeps the doctor away.I dedicate this win to Ms.Spa people, those of you who are not afraid of fire and wishto walk among the flair, register here.Having a good time here, they are sweaty but also delighted.I've never seen anything like this in the class.As Ms.Hulu said, this excitement comes from the stadium itself.
```

### [2] hash=`39c7540bfb98f30d`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
Is this a recovery arcane skill that works on arcanists?Or a kind of cheering potion?No, I don't think so.It just smells familiar.Yes, right.Totally agree with you.It smells like the weird cave on that island.Ugh, hmm?I smell beef with tomato and Nick's grilling sauce.Rounder and weaker, and the victory goes to Ms.Desert Town!Her temperature is a bit lower than just now, but her condition is quite stable.
```

### [3] hash=`c8e97fb25278a256`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
I guess it's more to reincarnate a reaction, but something else.Is she alright?She feels hot, but not as hot as the horse you made of pure gold.I'm positive that she was once a lot hotter than your little hooves are right now.She was a walking fire that burned fiercely, the forest destroying kind.Please don't panic.I have not observed any signs of a flame in her eyes or mouth.She's not a blaze again.
```

### [4] hash=`a529cd9fcfa5b735`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
Ms.Desertflannel, did she have any abnormalities before she passed out?Abnormalities?Some, I think.She waddled as if she was pierced and talked so loudly that anyone could tell she wasn't in a clear mind.Trunk.Clouding of consciousness.No!Regulus!You look like an apple coloured giant rock Mr.Apple, you're so big and our ship isso small, it means your change of size changes your voice as well.But, since you get this huge we can strike those oafogies in London like a meteor.
```

### [5] hash=`9683cb1cf940e345`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
On top of the world there will be our flag of rock and roll.I require the big ex-That's Miss Hulu.She's out of control.Is this also a result of the stadium's power?I'm so tired.Let me take a nap.Oh dear.Don't pass on you out of here.Just a sec-Another one has passed out.If we let it go on like this, every Arcanist here would-Miss Burton, we have to leave at once!That's out too!Bunny Bunny, take everyone back to the suitcase.
```

### [6] hash=`9b938c75ca2d1a4a`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p43`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜1~8）

```text
Don't let anyone out before I open it again.Alright, got it!Huh?A ramble!Sippin' in the grass!Darling, he's on it!They're out for now.The good news is, we are already a skilled fire brigade.Careful, young man.Down.
```

### [7] hash=`4cc79c34a0a42555`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Desert Flannel's dizziness is in remission.She's already well enough to deal with her business on the fax machine.Will it do harm to her physical condition?Ms.Desert Flannel is only experiencing a very mild reaction.She can move around freely and it is recommended for her to do so.Ms.Spathedia, on the contrary...She's not even awake.No, but her body temperature and her Arcanum level are getting stable now.
```

### [8] hash=`e5c442c90837ec3c`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
She should wake up any minute.Miss Ulu is different to the other unconscious Arcanists.She was weakened by the long sleep, while the other Arcanists lost consciousness becauseof external factors.Look, this is their physiological data in the last three hours.Many Arcanists have told us that their physical abilities were improved as they enteredthe stadium.They felt they were in a refreshed state, like they had a good sleep or rested properly.
```

### [9] hash=`7d1d752cdf5db772`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
But after they competed in four to six different games, or the average sportingtime exceeded 3.5 hours, they would feel dizzy as if they had consumed too much alcohol.And these symptoms were relieved soon after they left the stadium.You mean people are in oblivion because of that stadium?That place is so dangerous, is it possible to hold the games again?I think this is why in the past, athletes were only allowed to compete in three different
```

### [10] hash=`206c5ebe4808fb6e`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
sports.As long as we stick with the same rule, the safety of our athletes shouldn't be problematic.I got it!So this place is just as safe as the club I work in!As long as we ain't breaking the rules, nothing will happen!Like how the bodyguards and I take care of our club,the rule and special medicine made by Miss Ezra will protect the Uluru Stadium!Miss?Oh?What's wrong, Miss Ezra?Miss Bunny, but you see, I'm not a miss.
```

### [11] hash=`af65510b1301929d`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Huh?You are funny, Miss Ezra.Please stop teasing me.What else can you be except a lady?A gentleman?Ezra is indeed a he.Father dear, you're awake.Here, take this water and the nutrition supplement capsule.To a boy?To a boy!And Missy Ezra here is holding her for it and looks......overwhelmed?Uh, he is not a Missy.He's a buddy!A buddy, Ezra?So what?Boy or girl, is that such a big deal?Nothing is more important than this.
```

### [12] hash=`81b678cfa4594270`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Dear Miss Verdin, I am glad to hear from you.No, no, not that one.That's for Verdin.From some guy called Slouch Hat.Oh, thank you.He's my contact in Australia.We've been writing letters these days.So, what am I supposed to look at then?This one?Large-scale event application form.Alice Springs Government.We just need to go to the city hall, fill in the form, and submit it!Then we're ready to have our Uluru game!
```

### [13] hash=`b4f938cdaa699b2a`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Before then, let's hit the-No, Ms.Spathedia!You haven't fully recovered, you need to rest!Your side.Come on!Our summer games are about to start!Bath O'Dea is surely a good runner.Even faster than the potion-drunk Ms.Sotheby!Okay, since the doctor and the patient are both happy, I, the event assistant producer, am also hitting the road.Wait for our good news!What are these?Look, I know English, but I don't understand any of the things written here.
```

### [14] hash=`02c3cb07cd356372`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
What is Northern Territory Event Security Law?Oh, and what is type 3 field safety certification?Ugh, I think I'll just go with C here for event types.That's what looks closest to the Uluru game since they have both two-word phrases.Maybe let's just go with that one.I always go with C when I have no idea what I'm reading.Mass event application, fire escape plan...You are on your own.City Government Service Center, District B, Window 13 at your service.
```

### [15] hash=`3fb87a9646dde1ff`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Thanks for your waiting.Your form will be examined.Oh, great.She stopped.What happened?I've seen that look on Miss Judy's face.She's my math teacher.Whenever she puts on that face...Yes?It means none of your answers are correct.Uh huh.I told you we can't feel who knows in the form.Who knows you can't write that?This one!Yes, Ms.Desert...I'm sorry, and you are...Spathedia!Director of the event!Instead of what, Desert Flannel!
```

### [16] hash=`b94b842ea5e91141`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Talk to you!Sick!The form!Instead!I will prepare a stool for you.Please stop jumping.Now to jump up again and again!Here's the form we revised!Let's check it!Alright.You've submitted the Arcanus Gathering Registration Form.The mass events application form and the desert areas gathering application formYour application will be in the approval process very soonI'd go crazy if I had to fill them in again.
```

### [17] hash=`8851fa783968176d`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I've never experienced such pain.We cried on each other's shoulders several timesSame for me.I'm sorryIt's nothingBut please take a look here at the second half of the sports game process and events application formMost of the events of your application have been confirmed, not approved.If you want to add them to the Illuru Games, an independent application for each event's security permissions is required.
```

### [18] hash=`a659cffd264b8022`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
How can I get the permission then?You need to fill in these forms and take live photos for the events you want to apply for.I'll take care of them!Miss, I'll stay in bed for the next three days.I'll take the medicine in time.No hesitation!No worries, Spathedia.They made me fanatic and crazy.How amazing, my young friend.I'm just like the present me when I talk to you.What do you mean, the present me?
```

### [19] hash=`5cb608d69ca19e10`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
An old flame that has been burning for over a thousand years.You are smart, and your ideas are fun.I've been paying attention to you when I was still a small flame.Looks like you have a lot of expectations for the Uluru Games.Sometimes it feels like you care about the games even more than Flammie does.I do have hopes for it.My wish to revive the games is stronger than Ezra's.And my expectations for it are higher than Spathadia's.
```

### [20] hash=`d22c33c785ea7c54`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
After all, we're in a different age now, which means we can achieve much more than a sports game.But to be honest, I'm impressed by Ms.Spathadia's energy and passion for all these.wait I think I just heard something I heard it too it's bunny hips and thosethorny devils they must have snuck out from the stadiumdarn those tabloids we're at the center of the storm now these things justwon't let us go like some cockroaches attracted to an open draw of jam
```

### [21] hash=`771636e36508e09c`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
scraps of paper sticking to the corner of their mouths is that the newspaperMayhem.Revival squad of Alluro games in City Hall with Bunny Girl?Mental breakdown of Receptionistexclusive on Australian knacker?Children?What have you done out there?Look at my back.This has forwarded the Alluro Games application to the Foundation, and it has been movingsmoothly in the system in the last two weeks.I heard that from Mr.
```

### [22] hash=`304c1fe0df9a27be`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Sloutchat on thephone this morning.They believe it will be a good opportunity to build a positiveimage for Arcanists, and it will strengthen the communication between them and humans.The Foundation is happy to see that happen.Then when will we have the result of the application?The procedure is long and complicated.Besides, the safety reports were only submitted a few days ago, so it will take at least
```

### [23] hash=`db9e2f6e4cae775c`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
20 days.The construction after that will never make it on the-Jania said the construction will take at least a month and a half!They even made our arcane skills accessible to them!They modified arcane gadgets, and added some science stuff,and the arcane tricks I know suddenly become something new.Some invention exclusive for humans' use.They're even taking away the Uluru Stadium with metal bars!It was me who found this stadium, and I'm not giving it to anyone!
```

### [24] hash=`7c5044304fe23090`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Taking away?We...No, I have never thought of taking anything away from you, Ms.Spathedia.I was just trying to help.Like most of the Laplace researchers, we spend most of our time in the lab, we read, we studyday and night.We weren't doing it to make humans noble, not for Arcanists.Those products and achievements, they are the fruit of the combination of Arcanumand science.They were made to make everyone's life better.
```

### [25] hash=`b1ac448cd10a27d1`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
You think I never saw the ad of Laplace?I had Arcanum with science, tame the orderless power with sense.That's what you tell the people!Sense will guide sentiments, so as to prevent the latter from destroying itself in the flames.You have to tend to the flames carefully, to understand them, protect them from danger.This is what I've been taught, and this is also the principle I've always acted upon.
```

### [26] hash=`23164252b2050f79`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
The very suitcase that we are staying in is also placed at the entrance made by humans.You shouldn't think so ill of them when you're standing on it.We were only trying to help.That's all.You can't just argue with a rude human who has no respect for a c-Sorry.I will go back to my room now.It's a nice map.It shouldn't be left in halves.What do you think?I don't like the idea of giving up.And I have never messed up a job once I took it.
```

### [27] hash=`f6d7bdf7b8ff9d34`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I'll take care of this, and you look after that.What do you say?Ulu, are you alright?I'm fine.I just feel a bit dizzy.What the heck did you say?What do you mean no other progress?Progress of the Alluru Stadium renovation?Who the heck will buy our newspaper for this piece of shit?Sorry, sir.We haven't been able to find anything new about the Revival Squad for a long time.They didn't even step out of that suitcase in the last two weeks after we got their names in the papers.
```

### [28] hash=`5d28a18f8329e4cf`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Neither did we hear anything from the sources.I'm not hiring a notorious journalist like you for this boring news.Get out and find more.Some big and breaking news, like that revival squad of Aluru Games in City Hall with BuddyGirl.It's you.Good timing.The Aluru Games on the edge of total disruption.The revival squads turn against each other.Are they...not in the room, I knew it.Showing Ezra what the world is like.
```

### [29] hash=`df9fe88fb559a42d`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Be right back, Desert Flannel.Watch your feet and your head.The people here never look down.That's how you get muddy shoes when you're out here.Here, take my hand.Miss Desert Flannel?What is this place?What are we doing here?Something that needs to be done, and something that needs to be said.Big bloke!Don't worry!of the rugby game it's not a formal game but the audience's enthusiasm is burningi mean it's hard to get a ticket but i'm desert final and i know people on the streets
```

### [30] hash=`06019b852d23b25f`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
even when we're outside melbourne sorry i've never watched any games and i don't know therules of rugby i i don't think i will understand any of this do you mind no i'm cool with thatbecause the game is not what we're after.You see that guy over there?That's Tom, a shining new star in the NRL.The best fullback they've ever had.He's from the Melbourne Sail Car Club.They have a seagull as their club's mascot
```

### [31] hash=`0e16c9ef12014f64`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
with a fish and a chip in its mouth.Yes, okay.And that bloke over there,that's Kip Carl of the Hobart Blue Lake.He's the kind of player who knows how to really tackle.They call him the unbreakable king and lastly, I want you to look at that smaller guy.That's RussellDoesn't look tough does he but he is the slippery jaboah because man he is fast when he gets the ballWell, what is this to do with us?
```

### [32] hash=`53bc2a6e31864030`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I still don't understandEzraGuess how many of them are our canists?Nice one.Nice oneRussell made it againExcellent interception the key school now as well as slippery as butter run run for RussellMankind is known for their physical resilience and endurance that is to sayPorn and kip-kala humans or Russell whose skills and unpredictability are his strengths is an archaenistHmm a reasonable deduction
```

### [33] hash=`e483937c7821e179`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Physical resilience and varied skills are indeed the respective features of mankind and archaenistsHowever, things are not as simple as they appear.In fact, all of them are arcanists.Shit, give me that thing.Here, be careful.Don't overdose.Painkillers are addictive, you know.And the newspaper's gonna interview you champions,so don't get high in front of the camera.Hey, listen!Sporting is great fun, but it can also be dangerous.
```

### [34] hash=`b5d696ef23f6053b`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
especially for sports like rugby, MMA, or boxing,which involve a lot of intense physical contact.And the arcaneists who are good at healingwill naturally become the best athletes of all.15 minutes, that's all they take.Most of the arcane treatments take only 15 minutesto heal the patient.And before that happens,the athletes would just take painkillersto help themselves get through the game.And after the 15 minutes,
```

### [35] hash=`2ab092d691601fd0`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
They are refreshed and healthy like those athlete dolls you find in the souvenir storeThey can slide, impact like a maniac and don't have to worry about missing any important sporting sessions of InjunThis is an advantage?That's right, an unbelievable advantageBut are they really as good as they look?Their glory comes with a priceLigament damage and the irreversible tears keep recurringBut there is still an elephant in the room.
```

### [36] hash=`14e021d7dad923da`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
It paces around, making noises which are unfit for the place, like this conversation we'rehaving in the locker room.But on the sports field, where blood boils, power and strength are the only things thatmatter.Nobody has the time to stop and ask what we're doing here, just like they don'thave the time to notice the elephant.Ten years ago, Margaret of Broken Hill was invincible on the court.In August last year, she died on the last day of winter.
```

### [37] hash=`42b20c15b835dc75`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Did she die of recurrent injuries?It's very likely that arcaneist athletes who repeatedly get injured and heal themselveswould get hurt on the same body part in the future.The body will become fragile, they might even twist their ankle from walking, sometimeseven break a bone or two.No, she died from an overdose.She needed a horrificamount of painkillers to ease her pain.So much that her body was overwhelmed.
```

### [38] hash=`d297fc5b89eedfb0`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
This is cruel!We have to report this to the foundation and solve it once andfor all.The athletes could have played in a safer way if given help.But whatif I tell you the Arcanists also don't have a choice?For humans who havetalent for sports.They can win medals with their physical strength.So, arcaneists have to makethe most of their advantages to keep oppressed with their competitors?I had no idea.
```

### [39] hash=`fa26ce0394672127`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I'm sorry,truly.I didn't mean to make you feel guilty.Nor did I deliberately put you in pain.But Ezra, I was once one of them.I used to live on the prize money.I'm only tellingthe truth.It is happening every day, every moment and every second.Drugaddiction, premature senility and irreversible physical damage.This isalmost a destined end for every arcanist athlete and nobody is heldaccountable for this.
```

### [40] hash=`9b89bfc3b35ad5d6`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Not the clubs or the hosts of the games.Drug abuse isa personal behavior.That's it.Those people who are passionate aboutand don't want to lead a life without them.I have no idea how they would make a living or handle a quiet life.So I know they don't have much of a choice.The sport industry of humans is generous.They offer equal chances to human and arcanist athletes.But it's also cruel.And the athletes are like the girls in Cinderella's story
```

### [41] hash=`ce749d5085187795`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
who wish their feet would fit the glass slippers.They have no choice but to cut off part of their heels to earn the glory.This isn't fair.These sports and rules are not appropriate for Arcanists.They have been treated unjustly.They aren't taken seriously and respected as athletes.Is Spathedia one of them?That's why she was so furious.So the rumor that they are turning against each other is true.Kamara, this way.
```

### [42] hash=`491ea2209f3680fa`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
This is the human representative of the event.You with that paparazzi?This is not how a polite kid would address others, Mr.EzraI am just a concerned journalist who ran into you while reporting a rugby gameWatch your mouth, mister.This is harassment.Be a cornered.Then we will break his camera and let him know the price of being a long-tongued liarSpathedia, it's not all your fault.You don't have to be nice.
```

### [43] hash=`83ec7d5182ebb8af`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I'm not capable of the jobI should have known when I couldn't even fill in some forms correctly.I don't know how to supervise the construction team.They all left and my schedule's in a mess now.I'm hasty and careless.I actually lost my temper with the people who tried to help me.I also did that to Ezra.I know he has no ill intention and he's not a bad guy.Maybe some humans mistreated us, but that has nothing to do with him.
```

### [44] hash=`f31e00923caa67ec`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
But all the others...I should have got out of his face right away.I screwed up the Uluru games.What I did was not out of friendship, or sportsmanship at all.It's a new sense.I'm not qualified for the priestess.Listen.Come here and listen to me.Everyone makes mistakes.That's what your mom told you when I was still asleep, remember?Everyone makes mistakes.Especially young people.We were of the same age in the past.
```

### [45] hash=`01c9e4e54504efce`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
It feels awkward to talk like an elder to you.But now, I have to address you as child.You are 14 now.Remember what I was like at your age?I appeared out of the campfire, so young and naive.My flame was beautiful, yet lethal as well.I couldn't control myself, not to mention understand others.My situation is different.I said something really bad, and I already...It's impossible that you make no mistake or do everything perfectly.
```

### [46] hash=`f955bedae5f37210`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
You just need to face them and learn from them.You stepped into the muddy river, that's fine.Just keep going towards the clean stream.The point is, you must know your mistake and apologize to the friends you've hurt.You still have room for improvement, and the opportunity to avoid the lasting regret.Regret?What's worse than what I'm dealing with?I can't think of anything.Eww, it's rude.Flammie is a better choice for you than Spathedia.
```

### [47] hash=`228efeb767122502`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
My name has changed, and I can no longer be your best partner.Neither can I be Verdant's good partner, nor Ezra's, nor Desert Flannels.This is my second life, but I still feel like an idiot.What was I like in the previous life?Did I grow up?Did I hurt my friend?Did I have fights with you?Remember our fight, Flammie?Yes.We were arguing who contributed the most to the first games.What a trifle.That's right.
```

### [48] hash=`4ceff947e0aa5c3b`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
We had a huge fight over this trifle.We never meant to win the fight.All we wanted was recognition and love, but in the end, we didn't talk anymore.This lasted for several days.Then I tried to find you to make it up.Make it up?I...I don't remember that at all.Because I didn't make it.You were in the distance when I found you.The next second, you were attacked by a toxic red snake ambushing from the bush.
```

### [49] hash=`fb81e64d5ed115ab`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
It's venom made you pass out within seconds.The witch doctors stayed by your bed for three days before they sent you to the grave.Didn't even have the chance to apologize.You never grew up, my friend.I'm already an old flame, after such a long time, while you are still a teenage girl.So, I'm really happy to see you again.I'm really sorry that we once grew apart.I see.Thank you for telling me, Ulu.
```

### [50] hash=`824e693e122f199b`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
My heart, dear friend, we once burned together as a whole.No one knows my heart beat better than you do.I will grow up as you wish.I will find Ezra and make it up to him.Be an ender!There's a funnel!Ezra, what's the hurry?Those guys were chasing us like crazy.Anyway, that's why we are out of breath.A paparazzi was following us, and as we were running in the desert, we ran into a bunch of thorny devils.
```

### [51] hash=`5cf7913267571f73`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I see.We'll deal with this problem before we talk.Give me five minutes.They will no longer be a problem for us.We finally drove them away.Two weeks ago, you were in the column whose heart is hurt by fire kangaroos and housing stress.Would you care to make a statement?It's just an accident, not a misconduct.Fire goes out of control very easily, as it's fire after all.Young people.Besides, you and your fellow team members were seen chasing after a metal UFO on the back of a wooden horse.
```

### [52] hash=`0add201a1d457107`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
He's a hat, as well as a helping hand.And greetings to everyone, I'm Slouch Hat.Go!Unlike them, I'm sure most of you in the media industry know, or at least have heardof me.I'm a member of the Northern Australia Rangers, also the spokesman of the Saint Pavlov FoundationAustralia branch.These days, the reopening of the Uluru Games has attracted much focus, and speculationshave reached such a pitch that we have to respond.
```

### [53] hash=`b6e15f6d9797008f`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Here, I will answer your questions about the Uluru Games,starting from you, the ardent Mr.Makoa.Of course, it's my pleasure.Made my day.I feel happy, contented, overjoyed.Now that we have the Foundation's people on our side,he can bugger off for good.You know him well.He's our enemy, Verdant.He's your enemy?We are not enemies.I don't even know him.You don't even know him, and he's not your enemyI don't quite get your relationship.
```

### [54] hash=`954fa14dd00259e2`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
This can be complicated between men and women nowadaysYou're still too young to understand it.Don't worry.You will get it at my ageSo it's a kind of experience one must grow old enough to learnThe current life expectancy is 50 to 75 years.I don't think I will ever reach your agePut it like that.You're confusing the kids.I as one of the parties involved in this storyWill explain it to you very clearly
```

### [55] hash=`96618561d40fb84c`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Ezra go back to his room.He didn't come out when we leftFirst of all, you stay for my little anecdote.I won't tell the story again.It's way too embarrassing to tell twiceI'll listen to your story first and then I'll go talk to him right awayFor the entrance support structure for the ceiling come repair it for broadcasting the gamesFluffy, so?Bear torch for the Uluru FlamePopsicles for Steeplechase
```

### [56] hash=`8a3a2791980963e8`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Tenacity of the branches and temperature of the red clothAlright, checking what item to go before the flame lighting ceremony this midnightYou sad again?I just have sand in my eyesThat is common here, it gets into your eyes very easilyJust like when my granny saw me walking for the first timeYoung lady, you should have preserved the dignity of this old flameYou burned me!Blue burning hot and energetic, safety factor of the field, really did us a huge favour.
```

### [57] hash=`0ffaae8a4e74133a`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Shame I haven't had the time to talk to Ezra since we had that fight, we were both busy and sad it was.I haven't talked about it, but I didn't feel anything wrong between you two.We did make up, that's for sure, but we never really talked about the fight.It's like you break your knee and just cover the wound up with trousers, as if it had never been there.You may feel fine when you jump and run, but it hurts whenever you sit down for a break.
```

### [58] hash=`510da37e6b14ed84`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I wonder if Ezra and Vernon are going about with the patrol.Relax, Flammie.It will be the opening ceremony tomorrow.Our checklist is even more intricately designed than a road made with pine needles.Besides, the bunyips haven't turned up in quite a while.Everything is working like an unsinkable ship at sea.There isn't anything that may cause it to sink.But the last ship that claimed to be unsinkable...
```

### [59] hash=`e9bd5411e39d6408`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
What was it called?Got it!Agency!The Titanic!I've bought tickets, let me in!I came all the way here just for the Uluru Games because you said that it is open to all for the first time!Everyone, please be patient.We are now standing at the entrance to the Uluru Stadium.And this is where the rumored reincarnation will come, with flames and bring about the rain.The rain will comfort the thirsty travelers and soothe their dry feels.
```

### [60] hash=`0b8318f129c81324`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I guarantee you, as the ambassador of the games, that no matter what your lineage is,you are welcome here as long as you have a ticket.All you need to do is wait patiently and with sincerity.Sincerity?We followed the guide and circled around the desert for a whole day.We need water and food.Some kids have become dehydrated.Yes, we need water.We need to get into the Uluru Stadium.You've promised us.
```

### [61] hash=`695252a9ecb566d0`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
We need water.We need to get into the Uluru Stadium.we need water we need to get in the Uluru stadium that's right yes that'sright revival squad I'm sure you will enjoy this gift from mewe need to get to the Uluru stadium we need water we need to get to the Uluru stadiumit's him that guy shameless we never sold a single ticket or invited soThat is the daughter of Uluru Stadium, behind her, she's the girl in the newspaper!
```

### [62] hash=`7aff05d06686b2c8`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
That girl?Is the reincarnator?Oh dear, there she is, and look that flame, isn't that the Uluru flame in the newspaper?Open the gate for us Priestess, show us the Uluru Stadium!Open the gate for us, we have tickets!We have tickets!Open the gate for us!We have tickets!Look at those girls, my friends.That is Miss Lithodia and Miss Oolou.The newspapers have been praising them for facilitating the union of mankind and the Arcanists,
```

### [63] hash=`136f519a7c8d045b`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
bringing back the true spirit of sporting events and calling them the pioneer peacemakers.You're a liar.I'm out of here.It's not the Uluru Games.Not the one I heard from my grandma at all.We should believe that.She's an honest girl.She would never have lied.Miss Spathedia, did you really say that?Confront it.Light it up.Conquer it.And make it burn.I will.I know what my duty is.This is the Uluru Games.
```

### [64] hash=`11d8ec549eef6527`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
And my friend, the Uluru Flame.Both of us stand right here.We will not kill alive or evade any questions.That's right, we stand right here.It's time we put an end to all these slanders, Mr.Makawa.There are reports of your arson.You set fire to a hospital,and thousands of human patients in therewere almost killed.This is supposed to be an unforgivable felony,yet you are still standing here.Did you bribe the officers to get away, Miss Spapadilla?
```

### [65] hash=`666980c2a4b9e44c`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Please be careful of your wording, Mr.Makkala.That was not arson.It was an accident caused by the instability of my arcane skill.It was awakening at the time, and things like this happen to most arcanists.Second, we didn't cause any injuries or burn the hospital.Only a clinic was slightly burnt in the accident.We have paid for the damage already.Besides, the revival squad has promised they will do volunteer work for the hospital every Saturday afternoon as an apology.
```

### [66] hash=`d6ce1c28e23195fe`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Good for you.Damn, that bunny up is weakened.Now go for it, Sammy.Everyone here is exhausted from the journey to the desert.We're suffering from the heat and the thirst, so why don't you open this gate for us?Is your Golden Gate too good for the tickets we paid for?Are you shutting us out?Tickets you paid for?Are you sure that Uluru Games has ever sold any tickets?Lies!Please check your tickets and compare them to each other's.
```

### [67] hash=`5f140b4a256ab0b0`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
I believe they have different sizes, textures and printing methods,which indicate they come from different producers.That's right.If you know the local gangs well,now you should realize the staff who brought you hereand those marshalling the crowds include some familiar faces.They are Tommy, Jackson, and Cameron, gangsters from the Eucalyptus Brotherhood who made theirfirst pot of gold by selling fake tickets.
```

### [68] hash=`79a537c70b75dc92`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
And you, Mr.Makkawa, speak for them.Three, two, one, down.No way.Well, yeah, you've got a silver tongue.Your words are indeed clear, logical, and reasonable.But how are you going to deny what you said in the photos?You wanted no humans in the stadium, and you held a grudge and a prejudice against them.There is no doubt that those words came out of your mouth.Your eloquence won't change the fact.Yes, the fact.
```

### [69] hash=`151d408700bc8f31`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
The fact that is 100% true.You can't deny it.You were right, Mr.Makora.I did say that.I take responsibility for every word heard in that photo.But people, listen to me!In the past, I saw humans as the other kind.I thought they were unreasonable, cruel people who deceive others with bureaucratic jargon.But now, when I think of humans, I am reminded of...of my friend.My gentle, brave, smart, selfless, clumsy human friend.
```

### [70] hash=`677eea6d411ec202`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Are you going to...Confront it, light it up, conquer it, and make it burn for you.Everyone here loves sports as much as I do.I must apologize for being an idiot with such a narrow view.I'm sorry.Now, I hope everyone can enjoy pure sports and have fun wedding.Those of you who have tickets.Those of you with no tickets, you can buy one from this desert flannel for just one dollar.I hereby declare the opening of the Oola Rig!
```

### [71] hash=`b8b53013e85bdce2`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
The source has confirmed the rift between them!Run!If I'm fast enough, there's still a chance!Or maybe you don't deserve that chance at all.You've got a helping hand.More than one hand.Aha!This is what we call the hammer of justice.You shitty little long-tongued pig, I will pull your tongue out through one of youreye sockets!You should have known better than to mess with me!The audience are all seated, no stampede or jostle, not to mention injury.
```

### [72] hash=`f2767e0c4f5fc65b`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
All the human athletes have registered, and their mixed sporting events with the Arcanistathletes have been properly planned and are ready to start in three days.I'm done, I can't even move a finger right now.Come on Flammy, it's our turn.May you walk on this glorious path together, Uru.Run.Get yourself a running child.Light up the Uluru torch as you were promised.I have promised.I am running, even though the day I last ran here was a thousand years ago.
```

### [73] hash=`457c94225ef96b5e`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Feels just like yesterday to me.I went across the long track, stepping on the burning red soil.I am sweating like a sparkling star.I am going to the top of the stadium, to light up the torch.Have I grown up as you wish?Am I new and different now?Have you waited a million days and nights for it?I want you to be proud.I want you to be happy.My friend, my dear friend.You are already my Flammie.But you are actually more than that.
```

### [74] hash=`8ae2af1632d37372`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
You are also my Spathedia.My little girl.You have grown up as I have dreamt of countless times.The snakes who didn't lay a single tooth on you.Both your body and mind are intact.Their flame is dropping water!I want it to be a successful event.It's important to you.And so to us now.This is who are here with us,or following the event through radio, TV or internet.I invite you to witness the blazing of the Uluru torch.
```

### [75] hash=`c6d7c4e61d14d09e`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
spirit of peace, competition.In the past thousands of years,Holy Fire has been to the highest mountainand touched the rocks in the deepest sea,taking the peace and all of the noble qualitiesto every corner of this world.It was also brought out of this worldinto space by rockets and traveled among the stars,from ships to spaceships, from one hand to another.It has journeyed far.We shall forget hatred, conflict, turbulence, and chaos of the past, we shall write in the name of Fordsmanship, we shall walk in the original form of man, we shall compete against each other, not for victory, but for participation.
```

### [76] hash=`8738906f2db95e39`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
Did Miss Desert Funnel go to the hospital to visit Mr.McAvoy?Yeah, she bought all the magazines with that photo and brought them to-Oh wait, I guess you don't know the story between Desert Flannel and Makoa.No idea.I was in my room, pondering what happened that day.Don't look at me like that!I've told you I'll never repeat that story again!Okay, I guess it doesn't matter if I never had the chance of hearing it.
```

### [77] hash=`c1579904bcac03af`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
It's just a story.We'll tell it to you.Come over here, kid.You were so kind!You must all know that I have many jobs.These part-time jobs eat away most of my time, but the clients who gave me these jobs neverlet me go home empty-handed.If you were me, you'd know that if you were willing enough to take as many jobsas possible, you'd meet some strange clients.Like going to a school day pretending to be someone's mom, or braiding the hair
```

### [78] hash=`7b46946d753f86e1`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
of a punk hound in 302 pigtails for a blind man, or waiting for a rare bird at midnightcarrying a camera which was expensive enough to pay for my apartment.I know, sometimes my colleagues in the class would also hire others to help collect informationthey need, but if we have the time, most of us would prefer to take a walk in theforest and try our luck.Yes, that's exactly what my client said.He paid me well for the job, so generous that I stared at the dark and waited for that pink
```

### [79] hash=`a6cc90f7ab57d8d5`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
torch hummingbird to show up despite my bloodshot eyes.One day, two days and three days passed.I didn't even see anything like it, but I saw a wonder beast just as extraordinaryas the hummingbird glittering platypus pink glittering platypus it's pink it's glitteringand who knows whether pink torch hummingbird is a strange nickname for that platypusof course i have to take a picture of it but you know a bird lover won't need a picture of a
```

### [80] hash=`73c3178998002d17`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
platypus so i sold it to kidding fun a children's magazine what happened next should be veryevident to you if you read enough bad novels is is that yes that's right thatplatypus was Makoa who took the transformation potion ah but why wouldhe do that perhaps he was looking for some fun or maybe it was an accidentanyway according to him someone pulled out a prank on him and it wasdefinitely not his own choosing he quit his job the moment that picture
```

### [81] hash=`119bb5e578fdb15c`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
was published he left his friends and family and became a revenger striving toput me into a miserable situation just like what he has gone through so thistime after I made this fortune I bought the apartment and every copy of thatissue of the magazine are you planning to sell them all to mr.McAvoy no ofcourse not I think I am there I picked him up at the hospital took himsomewhere quiet and burnt all the magazines in front of him.
```

### [82] hash=`a68e7c635df8a767`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
He was, oh my gosh, crying so loud, that was pleasant to hear.Well, Ms.Babadeer and Mr.Ezra, the interview is ready to start.Please follow me to the stage.Ah, yes, in a minute.Did you get the ending of the story?No, not really.There is something neither arcanists nor humans can understand.Perhaps we can ask Vertin later.She's a bit older than us, but she's not here today.I think she went to the stadium with Miss Ulu.
```

### [83] hash=`cba23b061b577c49`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
The old swallowing crowd, the apocalyptic hedonism, and the adventure on the island of Numbers.So this is what the world has become when I was in slumber for all these years.Fortunately, a lot of people went to the visitor window of the branch.They are worried about the stadium?Yes, a lot.They volunteered to station here to protect it, even at the cost of their own time and effort.They have built the Uluru Guardians which consist of 31 Arcanists and 29 Humans.
```

### [84] hash=`397938de82390b61`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
There are doctors, writers, taxi drivers, new stand owners and so on, and they are allamong the audience of the games.Child, this is indeed a brand new beginning.That's why I want to keep it here.We shall run in the name of sportsmanship.We shall walk in the original form of men.We shall compete against each other, not for victory, but for participation, by both human and arcanist.No matter how many times the storm reshapes the world from top to bottom,
```

### [85] hash=`82d4978629e5bb61`

- lang：`en`｜version：`1.5`｜arc：`—`
- doc：`BV1eo4y1u7aW_p44`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.5-活动】复兴！乌卢鲁运动会｜9~15）

```text
no matter how the times or the lifestyle change, no matter how ignorant people become,Whenever they open the gate to the Alluru Stadium again, they will remember the spirit and faith it has been conveying.Things will change in the unstoppable river of time, yet the Alluru Stadium shall remain forever.
```

### [86] hash=`20b204a243345ecf`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
Laplace has forwarded the Alluro Games application to the Foundation,and it has been moving smoothly in the system in the last two weeks.I heard that from Mr.Sloutchat on the phone this morning.They believe it will be a good opportunity to build a positive image for Arcanists,and it will strengthen the communication between them and humans.The Foundation is happy to see that happen.Then when will we have the result of the application?
```

### [87] hash=`89588713d79cf634`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
The procedure is long and complicated.It's okay.We have talked about the construction arrangement.We may start the renovation ourselves and move on to other things when we have more people to help.As I demonstrated here, if we plan it properly, we may be able to finish the construction in a month.By then, we can start the event as Ms.Spathedia first planned.Gosh, I...I already checked the schedule a hundred times!
```

### [88] hash=`8c20734b5367ab33`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
How did you manage to cut down 15 days from nowhere?This is unbelievable!You must be mistaken.We need not repair what's inside the stadium.I added it to the list.I have investigated the site with some workers from the construction team.The stadium is ancient.The walls are badly weathered and can barely hold up anything.It has become more of a natural scenic spot than a stadium for sports.For safety reasons, we might use a support structure made of alloy to...
```

### [89] hash=`2bcfb5b0f38157cb`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
No, definitely no!That's what we're talking about, not some office building on the street!I will not let you in!I wouldn't have let the gate open if you told me your plan earlier!But what about the audience, Miss Spathedia?How are we going to look after their safety?If one of the walls or the ceiling collapses, how can they escape?Nothing like that has happened before.Not even one case in the past hundreds of years.
```

### [90] hash=`aebd961006dfef8a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
Nothing stays the same forever.Ms.Spathedia?You invited me to the games.It's also you who told me that humans, like myself,can enter the Oleroo Stadium if it shows itself.You...I thought you were different.You showed concern about our K-Nest, andyou helped us a lot.You were a kind human.But I'm not special.I'm no greater than any other human.I don't deserve to be treated differently.I'm just one of the majority.
```

### [91] hash=`ca2ec7f9ada84a5a`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
An ordinary human.They modified arcane gadgets, and added some science stuff, and the arcane tricks I know suddenly become something new.Some invention exclusive for humans' use.They're even taking away the Uluru Stadium!It was me who found the stadium, and I'm not giving it to anyone!Taking away?We...No, I have never thought of taking anything away from you, Ms.Spathedia.I was just trying to help.
```

### [92] hash=`b21b63b5da063eae`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
Like most of the Laplace researchers.We spend most of our time in the lab, we read, we study day and night.We weren't doing it to make humans noble, not for Arcanists.Those products and achievements, they are the fruit of the combination of Arcanum andscience.They were made to make everyone's life better.You think I never saw the ad of a class?Tame the orderless power with sense!That's what you tell the people!
```

### [93] hash=`84b0b70fa2531b66`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
Sense will guide sentiments, so as to prevent the latter from destroying itself in theflames.You have to tend to the flames carefully to understand them protect them from dangerThis is what I've been taught and this is also the principleI've always acted upon very suitcase that we are staying in is also placed at the entrance made by humansYou shouldn't think so ill of them when you're standing on it
```

### [94] hash=`f84251a665799909`

- lang：`en`｜version：`1.5`｜arc：`复兴！乌卢鲁运动会`
- doc：`BV1pb4y1M72G_p10`
- title：《重返未来：1999》1.5版本「复兴！乌卢鲁运动会」全剧情 - Reverse: 1999｜4K（P10【过家家】）

```text
We were only trying to helpThat's allProgress of the Alluru Stadium renovation?Who the heck will buy our newspaper for this piece of shit?!Sorry, sir.We haven't been able to find anything new about the Revival Squad for a long time.They didn't even step out of that suitcase in the last two weeks after we got their names in the papers.Neither did we hear anything from the sources-I'm not hiring a notorious journalist like you for this boring news!
```

