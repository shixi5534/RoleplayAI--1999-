# 剧情图谱抽取 · batch 010

- 角色：`wu_ming_zhe`
- 批次：**10** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「忧郁的热带」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_010.jsonl`

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

### [0] hash=`04d06e5b1b0c878e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Kill her kill Hurtin noobey your master kill herFollow your instincts follow my ordersobey kill her nowHey, I saidNo, pave the path for usThe Apostles Brotherhood will become their followers undertake their trials and embrace their graceWe all need the miracle Saber's Shell.We will be immortal.What reason could you have to kill your own men?They mutinied and killed their superior officer.The Apostles brotherhood may have infiltrated our base.
```

### [1] hash=`7672239d6980e7ad`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
The Apostles brotherhood?Notorious game from the streets of Sao Paulo.Our intel suggests Manus vindictus presence too.Sao Paulo.There isn't anything for me there.No dancers, no beasts, nothing.In this city, arcanists and humans live side by side.Both are equally passionate, albeit touchy.Violence is far from the means to end here.It's a tool, and one all too readily used.Wait!Apologies.It seems I've killed the wrong people.
```

### [2] hash=`4f9f20f798847b8c`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Mutineers!Traitors!You've made your choices!Now you'll learn the consequences.Zeno never forgives.Attention!Aim!A shame you had to see all that.Our second Lieutenant Lopera is a crack shot.I trained her to be nothing less.Yet no soldier of Zeno would take pride in an execution.The burden falls on me.This was my fault.My negligence.She hunted down these traitors herself.Lieutenant Moldier is investigating still.
```

### [3] hash=`6874a10898444cfd`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
We will find out who else was involved.The Apostles Brotherhood is back.We suspect they may have even infiltrated our base.We've also received intel indicating Manus Vindicta's presence in Sao Paulo.Manus Vindicta?I'm not entirely surprised.Intelligence suggests they are closely associated with the Apostles Brotherhood.What I hadn't expected is that they would drop their Order of Enlightenment guys so soon.
```

### [4] hash=`230fff27d3f3cb43`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Arcane is dead.There is no room for doubt, no one.Nothing could survive a vacuum bomb.It will become used to the tropical sun in San Paolo.I've been through a lot worse.Snowy mountains, deserts and soaring eagles.I do find myself thinking back to those times.Remember our rules, and keep to within the guarded areas.There may be a person of interest to us nearby, a writer for the A2 magazine, said to be
```

### [5] hash=`9ce012f211dfd7ea`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
a blind woman named Irt.Her work seemed to be published after every era the storm has affected.It could be this is only an alias, a pen name used by a new person each time, or...Or could she really have crossed the storm eight times, and somehow the storm has neveraffected her?Miss Barbara provided us with some information.She said the latest piece was sent from a veteran's residence in Sao Paulo.
```

### [6] hash=`0bc2b35eb3602c39`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
I understand they have a doctor working there, a blind woman.If so, she would match our intelligence on this mysterious atuv rider.You should seek her out.You are fortunate to have come now, timekeeper.Carlos, the late commander here, was something of a pain to work with.An idiot.Maybe thisis why his own men rose up and killed him, with already dispensed with most of them.Those men you just had executed?
```

### [7] hash=`d1f8268862a4d054`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Yes.La Pera raided one of their locations.Manu's vindicti will not be so happy toI see that you have one of ours with you, Lieutenant Lillia.I ask that she serve us for the duration of your mission here.She is a fine instructor, and Xena is in need of help training our latest recruits.I'll speak with her and see what she thinks.Thank you.I should return to my work.Your comrades should be waiting for you in the meeting room with Lieutenant Maldir.
```

### [8] hash=`048514823a953f4d`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
What are you doing out here alone?Molly!That is, soldier.You've really been building some strength, haven't you?And you are sprouting up like a weed.And you?Looks like they've been feeding you well.Stop it!How long will you be staying this time?Not long.Father plans to leave soon.He was furious when he heard about the defections.He ordered that he be brought here immediately.Perhaps you might leave with us when you see our lives.
```

### [9] hash=`d5d5ad37ceb6876d`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
And a strange little sheep in the bottle.They have a Neobank Acus there.1986.Rio de Janeiro.Mmm, Rio.Oh, you have friends in Rio?Simply must be Carson.He dissolved.Mr.Carson?What, you mean this old geezer in the photo?What are you talking about?Must be Mr.Carson.Who two men in the world that could look so alike?Could it be a doppelganger?Or an evil twin?But then, surely, Mr.Carson would have mentioned a twin brother?
```

### [10] hash=`755f7054523103b8`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Even an evil one?Nose?And his eyes?Though he's not wearing his glasses.But I know those wrinkles!I must be mistaken.But he's so very like the Carson I remember!Still be-Where is Lieutenant Muldier?Sir, timekeeper.I guess Sotheby saw someone familiar in one of these veterans photos.You know this Carson guy?Look!He does bear a striking resemblance to Mr.Carson, if my memory serves me right.86.Well, as many good soldiers to the Amazon that year.
```

### [11] hash=`12835b1dc11a77aa`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
But some battle through survived.This man is one of the lotto.You're saying that you've met this man before?He looks remarkably similar to a friend of ours who we lost in the storm in 1929.In fact, Admiral, they appear to be nearly identical.It's almost unthinkable.You say Mr Carson would never dress like that, but I'm certain this is him.That is fascinating.Do you know if this man is still alive?
```

### [12] hash=`2b3b344c99653ef8`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
I couldn't say.Dalfour, he would be in our service anymore.But you may find him at the veterans' residence in San Paolo.Thank you for your page, and sir...Lieutenant Moldier, about time.What was it?Did you stop for a picnic?Admiral, I...Save your excuses.Yes, sir.It was my fault, Admiral.I ran into her on our way here.It's been a while since we last saw each other.Your performance on the training ground earlier was most impressive, Ms.
```

### [13] hash=`4900ba9c10466c0d`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Lopera.Allow me to introduce my team.This is Ms.Sotheby, and this is Lieutenant Lillia.How's it going?I was previously assigned to HQ.It seems your assignment here has done little for your discipline, Lopera.You have new orders.I'm assigning you to accompany the Timekeeper and her team to Sao Paulo for the duration of their mission.Me and Lopera?That's a whole lot of firepower.What are we expecting during this mission?
```

### [14] hash=`8ac6d9c2ae67d512`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Oh, sorry, Lillia.I haven't had the chance to speak with you privately.The Admiral asked if you could stay on site to help with training their new recruits.What do you think?You can do as you wish.Training up some new blood, eh?Well, as long as you think you can handle things without me, I can stick around to lend a hand.It will be just like the good old days back at the Academy.Thank you, Lieutenant.
```

### [15] hash=`168b929f3b1c09ca`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
As for you, Lopera, please show our guests to their rooms andtry not to overexert yourself.Lieutenant Lillia, stay for a moment.Lieutenant Moldier will bring some documents shortly.They should proveuseful for your assignment.Now, I have other business to attend to, if you'llexcuse me.Let's go.I'll show you around, but stay close.This space cana bit of a labyrinth.It's only missing a bloodthirsty minotaur lurking its halls.
```

### [16] hash=`27891f1a2d37e68b`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Well, I haven't seen him yet anyways.The base here has been understaffed for some time.Whole sections are deserted.It can't be dangerous.We don't usually allow guests tomove about freely.Well, who am I kidding?We don't have any guests in the first place.Who'd come here for a visit?Scenic views of dead gardens and overgrown brush?In the spring we have vine-tripping competitions, and in the summer you can be part of our complimentary
```

### [17] hash=`ed8772183520102b`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
bug buffet.Even the farmers back home had it better than these.Before Zeno moved in, this was the fort of some Lisbon aristocrat.There's only one place fully off-limits here.That tower.What's in there?Love for super-soldiers!Imbued with the strength of an ox, the width of a man, and the wings and fiery breathof a dragon!Senora, this is a Xenobase, not some chimeras' nest.Besides, if there were any monsters in there, I would have heard them by now.
```

### [18] hash=`c767ca3a02feddee`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Were those the Admiral's exact words?That nobody is allowed inside the tower.Yeah, that was what he said.Under no circumstances is anyone to be allowed inside.King, what I'm thinking...Let me say this again.There are no monsters in that tower.And I am under orders to escort you directly to your rooms.But if we were to say a walk a bit too close and accidentally provoke some nearby creatures...They gave me quite thankfully.
```

### [19] hash=`bd42bbfc3b52c0a4`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
They were easy to handle.We can't let them run off.Who knows what damage they could do.Now where could they have gone?It may well be possible they fled into the tower.Is this the entrance?Lepera, you get lost on your way to the guest rooms, Pera.You know better than to be here.Your ship will be leaving early tomorrow morning.Please return to your rooms and get some rest.This is a military base, not an amusement park.
```

### [20] hash=`3ce4ca8390aa6009`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Please, do not wander about, especially near restricted areas.My apologies, Lieutenant.Perhaps you could point us in the right direction.Here, put this on, Pera.It will allow me to track you should anything happen.You'll remember to bring father a souvenir this time, yes?And promise me you will be careful.I do not wish for our para to buy the farm just yet.Don't worry about me, Molly.Worry about them.
```

### [21] hash=`d04761147061e064`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
I'll kill them all if I have to.Every last one.All right, all right.Enough blabbering.Do you two always share this little heart-to-heart whenever you leave?I've got nothing to say except bye.Or is the tortoise suddenly not so worried about its speed?Sotheby, do we have everything?Always ready to travel.The ship is boarding now.After it departs, I will spend some time gathering intel on Mr.Duncan.Thank you.
```

### [22] hash=`9b75e8bfdc3a1ae8`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
We should be able to find them in the flesh once we get to town.Duncan and I go way back.And I'll introduce you to another friend.She lives in a bottle.I'd be delighted to meet your friends.We should be going now.Lilia, I've told Admiral Eagle that he can rely on you for further assistance as necessary.Is that all right with you?Yeah, I'll do whatever he is doing.Have a good trip!Admiral, a prisoner has gone missing from the tower.
```

### [23] hash=`fe74912362be9b28`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
We'll make sure it's kept under wraps.The seal was broken and we are still investigating who might have been involved.I did encounter the Timekeeper, Mesotoby and Lopera near the tower yesterday.Still, I see no reason to suspect them.The timekeeper doesn't have any incentive.And Lopera?No, she wouldn't be involved.Find the prisoner, but don't attempt to capture her.Let's see who she's been in touch with.
```

### [24] hash=`631e6b6c35257937`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Understood.Lieutenant, this was a failure that must not be repeated.Look at those strange cowboys!What are they doing with those hooks?Never mind the talk of gangs, cartels, and greedy multinational corporations.Pierslander!Thank you for the warning, and the map.Let's hope I won't find any occasion to use it.I hope so too.Well, we have a long cruise ahead.I'll leave you to your business.At the mice.
```

### [25] hash=`cad17cf694ab7b56`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
So the kitchen even prepares food for them?Mind cutting?You boy, back to your place!You up, or there will be no dinner for you tonight!Hey!Out of my way!Miss Vertin, did you notice that boy?Wasn't he awfully strange?You're right.Come on, let's go see what he's up to.It's you!Do you think you're...I was about to ask you the very same question.Is this a new friend, Vertin?Pleasure to meet you.Please, take this.
```

### [26] hash=`4e4e3c6cf33fd064`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Thank you.Have you found what you lost since we last met?Perhaps I could help?Farewell and pleasant journeys, I'm indebted to you for your kindness, and your friend here.Aren't you just a sweetheart?Oh, I could just gobble you up the tea.Madame, please, he isn't proper or ladylike.He treats to buy their worship, and they call it kindness.How undignified, to be reduced to begging for scraps like a dog.
```

### [27] hash=`b95e11f932a23b9e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Dignity doesn't count for much in the face of hunger.Yet no man can live by bread alone.And yet none can live without it.You're aclever girl senora, but I hear from your accent you are no local.So what bringsyou to San Paolo?Business, ne?I have some business myself in the favelas.Colombia, senora.And no, only a visit to the San Paolo veterans residence.It's a safe place.If you find yourself in trouble you should seek it
```

### [28] hash=`00c587cb920ae315`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Oh, is it now?Thank you.You're very kind to offer.Care for a game of dice, señorita?What's the bet?Well, let us bet against the goodness in one another.Let us say that the loser will cover the cost of all the food given to all the little vendedores today.In the winner's name, of course.That's no small wager, señor.Still, I appreciate the good game.Hi, Loven.Who goes first?Ladies first.Lo.Let's make it more interesting.
```

### [29] hash=`6992cdf4db5caed5`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Six.If it rolls anything else, you win.Do you mind?I lost, just as was meant to be.So then, I am to be the vehicle of grace today.Might I have your name, senora?So that all may know the name which is to be sung in paradise today.Carlota Lopez Rivera.But it is Lopera, should you ask after me.That's an interesting die you have there.It was only luck.What's going on?Do as I say, all of you!Look, Fertin, there are some more river cowboys over there.
```

### [30] hash=`2b19f84434d5f388`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
I'm afraid they seem more like river pirates.Stay back, Sotheby.What do you want?Where's the captain?We're changing destinations.The ship will be docking in the favela now, or we'll blow it all to bits!Out of the way!Hold your fire, Lepera.There are oil drums on board.Slimy rats.Either we go to the favela or to the bottom of the river, claro?Make your call!The favela?Are you with the Apostles Brotherhood?
```

### [31] hash=`c3b308d3c11e102c`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p71`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 1~5）

```text
Huh?They forced you into doing this, didn't they?Hijack the ship and bring it to us.Is that right?Guess you'll have to ask her later.Listen, I'm not here to run your errands or play your messenger boy.So ask nicely.There's nothing more I need to tell you.For now.
```

### [32] hash=`dda0eb82a623ff43`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
The Brotherhood just took a beating from Zeno.If they're caught up with their own trouble,then we might have a golden opportunity to turn the people against them.We can't lose anyone else to their lies.What do you say?Wanna talk about plans?Here, drink up.Thanks.Listen, as much as I enjoy being out here all day,we've got to take action now.The sooner the better, don't you think?Hold your horses, young Elemo.
```

### [33] hash=`148d4dbf44dc5edb`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Let me explain.Say I throw a punch at you now, really hit you good.What next?Maybe you'll storm off at first, then you round up your cousins.Maybe grab that tommy gun you borrowed from Colonel Tiago, and you'll find me all aloneBut if we don't play this smart, it'll only cause them to lash out more.Still, we do have to consider one thing.Those who chose to follow them never come back.No, they don't.
```

### [34] hash=`989d45ebb805c91d`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
So, let's seize the day.Grab opportunity by the horns, and maybe we stop losing more of our friends to those bastards.Right now, seems to me that Xeno is our best bet.That just might work, old man.With the brotherhood falling apart,Xeno will certainly look pretty good to folks here.But not so fast, kid.We need a little patience.Let the line out a little first.If you fail to prepare, you're prepared to fail.
```

### [35] hash=`f40402dac1a4805c`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Excellent!Don't think you can get away from me!Duncan Duncan look she's got an anaconda chasing after her I saw it don't youworry hang in there lopera come this way we'll get you here take it thankgoodness you were here to grab me but what are you doing all the way outhere I was wondering the same thing about you girl seems like a strangeplace for a swim I suppose you wouldn't know anything about the girl
```

### [36] hash=`81ecacb1d2a3c975`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Sorry, I didn't expect you to suddenly pull my arm.Pardon me, little lady.We tend to be very straightforward here in the favela.It's quite all right.You look exactly like Mr.Carson.How could you be anyone else?Except for your attire and those shoes.Oh, pardon me, little miss.Are you not comfortable with us drinking?Galeno, put the cup away for me, please.Before I go rambling on again, let's head back to the city.
```

### [37] hash=`bb3575f578ad73bd`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Come on now.Trust good old Duncan.Sorry, I mean Carson.Trust Carson to lead the way.I've never wanted to put San Paolo through this chaos.Order, peace, unity, those are my purposes.And there's something more.A new doctor down at the veteran's residence.Some blind woman.I would not bother you with it, Lord Santos.Except that she's been helping people in the favela.And it is swaying them, poor Zeno.
```

### [38] hash=`3abd7392b7026945`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Then this doctor is with Zeno.She must be.She's always at the veteran's residence.Spends most of the day with those old war dogs.Better do it twice, and align the red and black, slowly.Unbelievable!It's science, kids.Nothing unbelievable about it.I don't know how to thank you, Duncan.Admiral, Lopera just called in.Put her through.Lopera, it's me.What happened?Our ship was sunk.Miss Sotheby and I watched ashore near the favelas.
```

### [39] hash=`34524f1936e43bd9`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
As for the timekeeper, she went overboard.We lost sight of her in the commotion.Her current status is unknown.We'll send people to find her and escort her to the veterans' residence.Additionally, Lieutenant, I have some fresh recruits eager to enroll with Zeno,but they will need the Admiral's assurances that their families will be under our protection.They have it.What's their ETA?They'll leave at once.
```

### [40] hash=`e29d2f91f91d7d50`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Tara!That little hothead.Sir, your orders.are over this sufferer will walk among us once more and we will bask in their divine gracethe day of triumph draws near soon our wagers will pay off all will reap what we have sownyou only need stand with us and take their blessings in return for thisThey ask only for your unwavering allegiance.My brothers and sisters, speak!What do you seek?Señor, please, we only want to see our family again.
```

### [41] hash=`7d8419a117a732ae`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Since they've joined the Brotherhood, we've had no word.We haven't seen or heard from them at all.Ah, but you will see them again soon.I tell you that they are even now faithfully serving our kind, in a new land of prosperity.There in Ushuaia, in Antarctica, in all places where the past and the future converge.There will be no more poverty, no more hatred, no more chaos.We shall reclaim what's rightfully ours.
```

### [42] hash=`19ccc0155ff89eda`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Remember this, humans are vile and sinful creatures.They tortured our men and women, leaving our children to cry in hunger and desperation.But they've already played their hand.All their reason, their science, and their despicable organizations.They raise these rotten edifices to weaken us and leech off of our misfortunes.to blind us from our true purpose.But no longer.Soon their games will be over.
```

### [43] hash=`31449b194ae07612`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
And every injustice and oppression they've held over our peoplewill be returned tenfold.All that they've built will crumble down over their heads.Tell me, my fellow brothers and sisters,What is evil?Evil is the absence of good, and to find what is good is to followour path.The High One has promised us strength and glory.Come with me!Nasmask.Sorrow will weaken you and fear may seize your hearts.Instead let
```

### [44] hash=`5c34ce021d8c33e2`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
May your faith be your guide.Those who take that leap shall find themselves lifted up on the Apostles' wings, while thosewho hesitate will be scorched by the fires at their feet.I have said all that must be said.We'll meet again here in three days' time.And just who are you?Marcando.As students of the truth, we have been granted a much stronger weapon than violence.Lopera, follow my lead.Sir, please forgive her.
```

### [45] hash=`27da61e7fa6c7082`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
She has mistaken you for those pirates on the Tieté river.So just a misunderstanding then?I'm no lunatic after all.Yes, your reverence.She came across a terrible raid on her way here, you see.The poor girl was left terrified.Well, I'll need more than a few words to convince my friends we have not been insulted.I'm an old man with nothing to give you but the truth.Believe me, sir, I came all this way just for you.
```

### [46] hash=`b9edce60bbe9f11b`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
I want to join the Brotherhood.She didn't mean to offend any of the gentlemen here.Please, sir, she's only a kid.Of course.I try never to take offense at a sweet young lady.Don't touch meLet's go.I admire your courageBut bravery alone won't protect you from harmTell me son is what he said the truth of it nowYou'll give me the names of Zeno's new recruitsWho are they?I'm not gonna harm you kid and if ever I do
```

### [47] hash=`f8afccce8b3817d0`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Remember that old Duncan must have his reasons, and he'd never harm a friend intentionally.This young man has one day to think it through.He will give us his names,or he will give us his eyes and tongue as offerings.Mr.Duncan, let this task be set onyou.Prove yourself worthy of our trust.It will be my honor, your reverence.sit atop their piles of corpses and rubble and feast, dining off golden plates with
```

### [48] hash=`8e1830c36720e9df`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
silver spoons, turning their noses up from the dogs at their feet.But that gold haslost its shine, and their silver spoons have tarnished.Everyone can see them for whatthey really are.So, what now?Either the people save themselves, or turn their fateMaybe he had a point, I don't know.Maybe there's truly something greater out there, or maybe it's just what we mortals need to believe.These men from the Apostles' Brotherhood used to be regular churchgoers just like anybody else.
```

### [49] hash=`263e6dddd507ee45`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
But faced with an opportunity to rise above their own cruel realities, they all too readily turned away.They left all their altars and took communion with a new god.It is a tool, and one all too readily used.I must note, however, with some relief that segregation so commonly observed in otherregions is absent here.The arcanists of Sao Paulo live alongside humans, with the latter often displaying traits
```

### [50] hash=`9e10ea6e558cd6b2`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
more common to their arcanist neighbors.Passionate, if a bit touchy.Life here is incomparable to the comfort, security, and freedom of New England.Hardship, violence, and oppression are the fundamentals of life.As constant as the sun, and as heavy as the rain, this country is renowned for its coffee and sugar.It is a land of beauty and bounty, treasures too often extorted,Whether by the princes of Europe and their donatarios, or now by the bankers and corporations.
```

### [51] hash=`6b091971ad1eb5b5`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Despite all the centuries of treasures extracted from the land, desperation remains everywhereyou look.It is a place where insurmountable wealth and the deepest deprivations are neighbors.Sometimes they lie only a street across from one another.The multinationals have cut open the country's throat and now they drink it dry, leavingthe people struggling with poverty and chaos.It is a bleak existence.
```

### [52] hash=`f28a6eba02fa69fa`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
Dear readers, I share this with you so the story of these people might be heard.Shippy, do you know, has life always been like this here?If you ask me, Doc, San Paolo in 1990 isn't much different from Nassau's 1681.It's a shame.Between the sunshine and warm sands, there is a good life to be lived here, if only they were free enough to live it.I used to dream of traveling to all sorts of fascinating places, a foggy city by the Thames, and a little town blanketed in snow and sunflowers.
```

### [53] hash=`3ded2067de1f4149`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
I met so many different people, though I find I can no longer recall their voices.I have only their words left, only my records of them.Have you heard of a weed down at the bottom of Lake Ilopango?The people there turn it into a polenta with cornmeal.Supposedly, if you have it, you'd recall every last thing that's ever happenedto you.Every bit of it.Oh, a weed card!They call it la hierba del tonto, Spanish for the fool's weed.
```

### [54] hash=`03657a5148b65acd`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
You see lad, only a fool would want to remember everything.Sometimes a little forgetfulness is a blessing in disguise.I beg to differ, Shippee.To forget the past, its lessons in pain and joy alike.That isn't a blessing.It's oblivion.But let's not argue over some mythical weed.For all the claims no one has ever seen it, just another myth like the succubus or the minotaur.Aye, aye, let's talk about succubi instead.
```

### [55] hash=`890499f36d94fdb4`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
That's sure to get the lads pricking up their ears.Back in 88, I mean 1688 of course, our chief mate Mr Morgan had an encounter with a succubus after he found her seal while carousing in Portobello.Don't be shy.I let the little ones play on my deck all the time,climbing here and there, like a bunch of cheerful little monkeys.And not just them,I ferry the good doctor from here to the veterans residence too.
```

### [56] hash=`e0adb6c35a5efcc0`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
You'll have to wait till we reach the sea to see me at my full size.Once the water opens up, that's when I'm really free.I ask again.Where are we going mate?Can't just let the wind decide our course.Well, I would sooner believe in a map to El Dorado before I'd swallow the idea of a succubuswith a heart of gold.So, was that girl your master?Did she have your seal?If that were true, then heart of gold or coal wouldn't matter for none.
```

### [57] hash=`bee6641298fa50f9`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
You'd be as thick as old tar.What, are you wondering what gave you away?Your gloves don't do much to hide those claws.Aye, well, mortal flesh doesn't last long.I've ferried many a passenger in my days,and none yet have escaped when Davy Jonescame calling their name.As I recall, the first that went was William Halfleg.He lost the other half in a fightat the port of Southampton,hanged on the governor's orders.
```

### [58] hash=`85afc1a10a85049f`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
And Edward the Red Hand,a nasty piece of work from the Low Countries,loved a bit of throat-cutting,Until he got his own throat slit by some fool in a ramshackle pub on Tortuga.Ha ha ha ha ha ha.Sounds as though they got what they deserved.That they did, lass.They all got what they deserved.Some hanged, some drowned.Some we marooned on a desert isle with naught but a pistol and a flagon of rum.I've been to Plymouth, Nassau, Port Royal.
```

### [59] hash=`9306370cb5ec67ef`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p72`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 6~9）

```text
I once even slipped into Seville disguised as a merchantmanWe're with the brotherhood, Gorota!You apologize, now we might just let you go.Oh, don't you know that Lord Santos is back?We can make this rougher for you if you like.Careful, me lads.I wouldn't pull those knives.Things may go rougher than you bargained for.Not so tough now, are you boys?Try this again, and I'll make a mince out of what's left of you.
```

### [60] hash=`ba23174d84eefd98`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Listen up.We're the Apostles' Brotherhood, not some worthless favela gang.So we start off nice and easy.And if the talk doesn't play along, well, then we make her play along.Claro?Hola.How can I help you, gentlemen?Hey, is she really blind?I'm afraid, yes.But please don't worry.I'm more than able to treat all my patients.Sounds like some kind of explosion near the clinic.Should we go back?It could be an accident, but she's got away with her equipment.
```

### [61] hash=`ab6099142ee4145f`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Doubtful she's the cause of this.Steady on then.Let's hurry back and see for ourselves.Ah, ah.That's not how you treat a doctor, lads.What are you doing to her?Lord Santos would like to have a word with the doctor.That's all.You're not taking her anywhere.See, she's taking care of this girl.Yeah, I'm not asking for permission, sweetheart.Gratis, doctor.Ice the rest of them.Enough.I won't have you fighting in my clinic.
```

### [62] hash=`0f01c2e5b71f0900`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
But they've got the girl, doctor.This lady definitely isn't from the favela.So what's she doing here?She's ill.She needs my help.That is all I ever ask.When you hear me playing this flute, you'll know it's time to strike.Wine's here!Courtesy of an old friend from Mexico!Take a glass, everyone!Here's to his reverence's good health.To his reverence's health?To Marcando!To the invincible brotherhood!
```

### [63] hash=`399dcc17cf438bd7`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
To Marcando!Thank you.That's your flute.Give it over.This is a fine flute.Duncan, did you...you said that you got a friend in Mexico?You know that old Mexican song, La Irona?That I do!I learned it from the best!In the cactus back in Tulum, from a fine young lady with silky hair and gentle eyesas dark as coffin.claro so how fine was this chica don't let me start spinning that yarn it'll beno fun for you to watch an old man bursting into tears I'll only say I was
```

### [64] hash=`186ac6d27bd7cb99`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
heartbroken by the time I left that love of mine anyway enough about thePinchy traidor!Time to cash you out!You'll be the begging for Lord Santos' mercy!Be reasonable, kid!The Brotherhood is finished!Your time's up!Don't let them slip away!Let me!Think you can handle this?Yeah.For the favela, the Brotherhood must die!Sorry to put you through all that, kid.When you reach my age, and just waking up each day is a blessing, you'll eat whatever
```

### [65] hash=`8e777bbca01a4075`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
you want, too.Mamai Mariana, could I have a word with you, please?I have some questions about Mr.Duncan.Oh, Duncan, what kind of trouble has he stirred up now?Alright then, why don't we head inside and give those two some space?Well, my biological father, not Igor.He said, no, that's not the sound of gunfire outside.The workers are setting off fireworks.They're celebrating.But they weren't fireworks.
```

### [66] hash=`8f87eaee2c91278f`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
He betrayed his workers, his compatriots.It wasn't a celebration.It was a massacre.After that, I ran away from home.One day, the Admiral and Molly found me.That's how I joined Zeno.Betrayal's as common as dirt here.Comrades, friends, family, anyone could sell you out.And for cheap too.I hope you can find your boat soon.You know, a place where people have your back.I'll drink this.Of course, don't force yourself.
```

### [67] hash=`c3a5f255bb2b19e5`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
I know the taste isn't for everyone.Carlota Lopez Rivera.That's my full name.Bit of a mouthful, huh?I wanted to erase it from my profile, from everywhere to be honest, but Mevia Hodesaapproved.Molly agreed with him.She said, you mustn't forget your past, Bera.So I let it go, but Lopera sounds so much nicer.So I preferred to go by that.And you, Kimberly?What's your real name?Malahari.The residents of Heartfelt Home called me, and JoNala.
```

### [68] hash=`6ca2df7fc5cee5e1`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
How long ago did Mr.Duncan move here?Do you remember?It must have been five, maybe six years ago.I'm not entirely sure.Do you have any photos of him?We do have one, but he's been gathering dust for years.Let me see.Here.This is him.I know a gentleman who looked just like him.His name was Carson.Did Mr.Duncan ever go by that name?No, not that any of us are aware of anyway.And I've known him since I was a medic in the army.
```

### [69] hash=`5ff301be95505014`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Back then, people called him Duncan the Don'tless, or the all-powerful Duncan.I never once heard Carson or anything of the like.Sorry I couldn't be of more help, miña querida.A crow?Oh dear, this looks like bad news.Santos.Dr.Doras is being held captive in the Colonel's manor.He's given us threedays.He says that if Zeno doesn't return the deserters they detained, he'll executethe doctor.Mamai Mariana, please contact Admiral Igor.
```

### [70] hash=`a4096b1d632d6d0e`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
We need Zeno's help.Igor, how are things in San Paolo?Officer Carlos was shot in the head by one of his own men in this very office.I need soldiers I can trust.So the fearless Igor is afraid of death?An officer was killed by his own soldiers at his own base.This is an immense stain on Zeno's honor.Everything goes according to plan.You'll see your unit shortly.Now it's just a matter of time.There was an ostrich that was chasing a dove, and a god of the sun that was tightly pulling its golden chain.
```

### [71] hash=`858124d3d6323aff`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
I watched as the wooden horse was greeted on our lands, and as the blood of the birds flowed from the sacred fountain.the blood of the birds, but a man with a decisive mind and pride will know that his city will stand.His walls will be strong and he will be unwavering, like the core of the earth.A sin is a sin.The white savannah will cover him, and he will be wrapped in darkness.This is all for the bright future.
```

### [72] hash=`db234dfb4f75ff4a`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
The future is for everyone.Yesterday, we received words from the Time Keeper.The Dr.Torres has been abducted by the Apostles Brotherhood.She should be coordinating with Lopera to set up a rescue operation as we speak.Also, that girl who escaped, Kimberly, is with the Time Keeper.She claims that she was released.Just play along with your lie.There is no need to tell Lopera the truth.The Brotherhood has demanded that we exchange the detained deserters for the Doctor.
```

### [73] hash=`d534d9b868043f5d`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Forgive me for issuing instructions without your consent, but if we refuse or ignore them,I'm afraid they'll...They'll execute the Doctor.What arrangements did you make?I told the Timekeeper that Xeno reinforcements would meet her at the Veterans' residence.Since Lopera is familiar with the place, I also asked her to scout out the rendezvouslocation.And yes.I played along with Kimberly's lie.I assumed you would have done the same, father.
```

### [74] hash=`f7ed6db16c1324e7`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Very good.Your squad will soon arrive.Take them to La Pera at the rendezvous point and bring the doctor back.A squad?I have spoken with headquarters.All going well.Telly, me and the unit will arrive soon.I see.I can hardly remember the last time we were all together.Your father died in Abadan.In a war he had no obligation to fight in.It's far more glorious to die in the throes of battle than to wither away on a sick bed.
```

### [75] hash=`9c9d1a86de7c9cd6`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
He made an honorable sacrifice.How shameful that we would tarnish his honor.Let's begin with that young pilot, Lilia.Tell me, what do you think of her?She is well-trained, experienced, a straight shooter, similar to Lopera in many ways.She is a true Slav, just like my brothers and sisters back home.I suppose she is luckier than Lopera, not destined to become a traitor like her.Lopera is still a child, really.
```

### [76] hash=`945b82d1dcc4cf31`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
So many lives have been lost, in wars, in the storm.What do you think Lopera will do?She's your child, just like me.I think she will stand with us.You think?Do you?She's not important.Here, take a look at this.Not wear it.Nor will you.I promise you, not one of us will wear this thing.The preacher has given us a gift and shared with us an oracle.Again, no one.Erkanist, abuses alcohol and loves to fight.
```

### [77] hash=`6dcd9c37ff3990d0`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Messenger, call Lieutenant Lillia.Tell her to meet me at the training ground.How does it compare to the drink back home?The stuff stops your energy, makes you feel sleepy.Just like this land,this place is always submerged in a half-dead stupor.Poverty.Chaos.To them, the future feels farther away than the sun beating down from above.Tell me, Lieutenant, what do you think of the Foundation?Is this some kind of test?
```

### [78] hash=`f5e6dc4e878a72c3`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Just the curiosity of an old man.I often wonder how the younger generation views the organization.Well, unlike those Manus Maniacs, the people at the Foundation are at least open to reason.Don't get me wrong, they are stubborn, but overall, I think they're good people.The Time Keepers red-headed sidekick, for example.She's a stickler for the rules, but it's so boring to follow all the regulations.
```

### [79] hash=`1943e5e4beb9a1cd`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
That being said, it would probably be even worse without them.Total chaos, actually.Anyway, at the end of the day, someone has to do the thankless jobs, and the people atthe Foundation are the only ones willing to do them.As the Foundation's most loyal partner, Xena has always been committed to creatinga brighter future for both Arcanists and humans, that includes fighting Manus Vindicta, asas any other conflicts and chaos in the world.
```

### [80] hash=`b2e64c656d2e5eba`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Uh-huh, it's a mindless gun.The Foundation points, and Xeno shoots.Precisely.Countless soldiers have perished in the storm,and they've all been deemed necessary sacrifices.I have to tell you, I don't like Xeno's role in all this.Neither do I.But in orders in order,Even if it sends your soldiers to die meaningless deaths against an enemy they couldn't possibly defeat.Still, we march on without hesitation, pushing our weary bodies deeper into the storm.
```

### [81] hash=`34c3e85bacb2b1c8`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
But how much longer can Xena keep going, Lieutenant?How long until our knees buckle and we fall to the ground?I don't know and I don't care.Percana isn't dead.We detected life signs after the explosion of the vacuum bomb.That's impossible.Yes, it is impossible.It would take a miracle for her to survive.Do you believe in miracles, Lieutenant?I'd sooner believe the ramblings of a drunkard.That may be the case, but when a miracle worker appears, there will always be people who follow
```

### [82] hash=`b1e0175e72c21c89`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
them, like sheep follow a shepherd.So when the desertion incident occurred, I wasn't surprised.I was infuriated, however, not because they abandoned Zina, but because they murderedtheir own officer.Dumb traitors.Back before the first storm,human and Arkanius troopsgot along well.We set aside our originsand united under a common banner.Our bloodlines meant nothingnext to our bond as comrades in arms.
```

### [83] hash=`1ceed764933f437f`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
But the storm changed everything.As a soldier, I must obey my superiors, I send my men as ordered, no question asked.But does it really make no difference if the place they die a mortal's death isn't a battlefield like war?These things are never simply a matter of black and white.Lieutenant, what do you think of the Time Keeper?I trust her completely.Sounds like you'd gladly sacrifice yourself for her.
```

### [84] hash=`b074851725f7c4a6`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
We need more leaders like the Time Keeper.Manus Vindicta, the Foundation.They're just two sides of the same coin, aren't they?The Foundation, the PEC Security Council.Manus Vindicta, which path do you think the Time Keeper will eventually take, Lieutenant?I trust in Verzin's decision.Hmm.I understand.Are you sure that Zina is not testing me?No.This has nothing to do with Zina.I'm talking to you now as Igor, not Admiral.
```

### [85] hash=`520cf5870af680ba`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
What's going on?Lieutenant Lilia, you are under arrest for the assault on Admiral Igor.Assault?Oh, I get it.Stand down and surrender, Lieutenant.Even the boots here taste lame.Come on then, you're not taking me down without a fight.Soldiers, fire!Bring it on, show me what you got.You traitorous rats!I never intended things to turn out this way.Surrender now, Lieutenant, or I'll be forced to hurt you.
```

### [86] hash=`9746ddd439e9af83`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
Surrender to you?You'll be the one who's surrendering.If I even give you the chance.Come on, soldiers.Do your worst.What a shame.Fire at will.There is no use resisting, Lieutenant.Tell me, what's Igor planning?Father will lead us to a future where meaningless sacrifices are no more.The die has been cast.I hope you know that this is nothing personal.I'm just following orders.Take Lieutenant Lillia to the holding cell.
```

### [87] hash=`c105fb750c4759f1`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p73`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 10~15）

```text
No one is to harm her without orders from the Admiral or me.What?We are traitors to Zeno now, Lieutenant.I am loyal only to my father.It's a pity, really.I would have liked to work with you in the future.How long has he been planning this?Ever since the preacher gave father a giftand a path to a brighter future.Being killed by your enemy is bad.Being killed by your ally is worse.It was an honorless way to go.

I'm done reading reports anyway.I look forward to your wise decisions.We need some good news for a change.
```

### [88] hash=`c6b92bfab1c614f3`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
Father, Talimei and the unit have arrived.So here they are.The army of justice ready to eradicate the Manus and the deserters in one fell swoop.During the last storm, the Foundation created this thing.And with the help of Laplace and their pair of Narcanists,they stole the Fire of the Gods, just like Prometheus.Which side would you choose?I wouldn't.I would follow.Follow you wherever you lead.Send someone to bring Stefan's belongings here.
```

### [89] hash=`3891c336246dce7f`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
The traitor found something important at Tuesday's motel.Ptelimei will find it useful.That's all for now.Understood.Moldir, long time no see.What do you say?Do we give those humans a chance to surrender?Manus vindicti don't accept humans.But I doubt Father would blame you if you men allowed them to escape the base.Escape the base?Moldir, are you having second thoughts?Either follow this path to the very end,
```

### [90] hash=`650b2f7b5fcd9ad1`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
or show mercy and give Father and the two of us executed.So what then?You want to have a mass execution like Lopera did?On what charges?For refusing to join the rebellion?No one in history has ever been able to do that.Lady Arcana is invincible.I don't care about Arcana.What worries me is that the soldiers who are unwilling to follow us won't just surrender.Then we shoot them.I don't think that's...
```

### [91] hash=`d2dd4bac0ec896d1`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
Father!Where are the others?They went to rally the soldiers.We've been waiting for this day for ages.For ages?How long have you known about this?I told your siblings some time ago.And Lopera...She's not part of the plan.Her only responsibility is to bring back Doris.Doris?Who's that?None of your concern.You have other things to worry about.Go issue your orders to your soldiers.Maldir, prepare the aircraft.
```

### [92] hash=`50d5267f70d3e215`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
We're going to Tierra del Fuego.No.You will bring Kimberly back from the veterans' residence.This is Kimberly's seal.As long as it's in your possession.She cannot disobey you.Bring her back peacefully, if possible.Of course, father.I will do as you wish.Right then, Mordyr.Let's get started.What's going on out there?Is the base under attack?By whom?The Manus has no reason to launch a frontal assault?
```

### [93] hash=`770d7ddc080125fc`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
The Apostles' brotherhood?No, that's even less likely.Take, comrade!Are we under attack?Take your stuff and go!More enemies over here!Comrade!Lieutenant Moldeer asked me to help you.Take care.Kill them all!No.Recall your troops and assemble.Land!Assemble!The bloodshed stops here.Moldeer!Admiral Igor has sent reinforcements.We were instructed to await their arrival at this location.Do you know him?
```

### [94] hash=`140d83464a1bb4dd`

- lang：`en`｜version：`2.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p74`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.2-主线】忧郁的热带 | 16~19）

```text
No, I don't!And I don't want to know him either!I want nothing to do with those senile madmen!Stay away from them, Burton!Trust me, they...Greetings, Timekeeper of Saint Pavlov Foundation.I'm Ptolemy, the commander of Igor's sentinel unit.Are we setting off now, Commander Ptolemy?And please, don't make me resort to violence.Let's just get along, shall we?This isn't an arrest, Miss Kimberly.It's an...
```

