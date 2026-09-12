# 剧情图谱抽取 · batch 091

- 角色：`wu_ming_zhe`
- 批次：**91** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.3」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_091.jsonl`

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

### [0] hash=`8fed555256dfb66a`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p20`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（20伦敦今日晴）

```text
For presidents?Seems we'll be spending quite some time together in the coming weeks.Which one of us is a president?It ain't it!It-Shut your mouth.Don't scare me anymore.
```

### [1] hash=`957a36c2dfdab595`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p2`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（02烟囱中的雨燕）

```text
Stay right there, miss.I'll be back soon as I finish.Don't go getting off your sauce while I'm goneHmm.This is an Arcanist fair booth application formYou need only fill this and get proper approval from the city government then no one can bother youApproval a what's the point?The games will be over by the time they've even looked at my applicationAre we entirely certain we even want to hold the fair in these conditions don't you think?
```

### [2] hash=`fee81e47436100c7`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p2`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（02烟囱中的雨燕）

```text
The weather now isn't appropriate for that kind of strenuous physical activity.What else can we do?We need to earn our bread, or perhaps you could clean the air for us, eh, Mr.Fogwalker?I'm doing all that I can.Which means you can't do nothing at all, don't it?Yeah, we're a coffin.But what we make in a day at the fair here is more than an entire week anywhere else.Not like we have royal allowances to rely on, unlike you.
```

### [3] hash=`3e0b5a735dde2009`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p2`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（02烟囱中的雨燕）

```text
what's to come next I wonder sometimes despite being an arcanist myself it'shard to understand my own people but that's what they think around here mycolleague is presently out investigating this curse they mentionedbut to say nothing of his intrepid skills as a Ranger I doubt he'llproduce any evidence of this so-called hag in fact heArthur, a little help, mate.We've got trouble.So, here it is.What's that after you now, old hat?
```

### [4] hash=`004e2f17fe52c7cf`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p2`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（02烟囱中的雨燕）

```text
It's the Black Fog.Seems I've startled it.And now it's sent our critters into the streets.Steady on.Let's charge like soldiers of the Great Emu War.It's the hag.The hag's cast is coming for us.Those nasty critters are coming from her garden.Run!Oh, damn it.May I say it was an honor to serve as your bodyguard, miss.I'm Brimley the ranger colleague of my mate here Arthur fog.I wasn't hurtThanks to you
```

### [5] hash=`59838b183b276ccd`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p2`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（02烟囱中的雨燕）

```text
Thank you miss tooth fairyFor telling us what happened at the hospital.We ought to make a summary of our investigation so farWe've encountered three oddities thus far todaythis mysterious black fog the unusual burning chest symptom andThis so-calledfog hagSwitchdoctor, you done talking to Mr.Fog and Mr.Hat?Flutterpage, where have you been?Hmm?Wasn't you listening?I was off catching snails.With a bit of help from the canaries.
```

### [6] hash=`37de7fcc43cc0585`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p2`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（02烟囱中的雨燕）

```text
Good on you, little tacker.That's quite the harvest.Shall we then, Miss Switchdoctor?Where are you taking me?Thought I'd show you around Cross Street.Figuring since I'm the best guide here.Are you?Then do you happen to know about the house at the south end of the street?Sure do!Actually, these snails are for her.You can tag along with me to see her if you like.
```

### [7] hash=`cc63e927b48705e8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p3`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（03雾中鬼婆）

```text
This right here, miss, is the Fog Lady's house.As you can tell, it is a very big, big house.Not like mine.Mine is small, but very high up.Steep, tilted roofs, sash windows.It's very Victorian.Hmm?Oh no.Her name ain't Victoria, miss.At least, I don't think so.But you visit her often?She likes when I bring her snails.You think she eats them?All I know is I gave her her snails.And then she asked me to stay around her house for a while.
```

### [8] hash=`9e32d18d67ec96ca`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p3`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（03雾中鬼婆）

```text
When she's not in a sour mood, she even teaches me some words.For arcane skills.But if she is sour, then all she does is hand me some books.And I can't even read most of them.Don't go asking her too many whys.So I can't come in at all you promised you'd help me practice my arcane skillThen you better not let me catch you saying all over ever again left me a bookCarbuncle on it come here flutter page.
```

### [9] hash=`8825667dfde7e97c`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p3`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（03雾中鬼婆）

```text
Are you all right?I thought I could play at her house todayWould you like to do something else?like whatLike see your new friend.Mr.HatMr..HatUh, uh, uh, Ms.Flutterpage, I'll ask you to not wear me on your head.I know I can fly, but that doesn't mean you can treat me like a kite.Besides, I'm due to begin my patrol.I need to...That gives us some time for business.First of all, allow me to express my respect for your adventurous spirit.
```

### [10] hash=`ecea6526fcb2c942`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p3`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（03雾中鬼婆）

```text
A haunted hag mansion whose owner feeds on snails.To visit her so quickly on your own initiativein London and the presence of an unidentified arcane-related tuberculosis outbreak, we regretfullyhave decided that the Uluru London Qualifiers will be cancelled until further notice toprotect the health of competitors and spectators.Competitors still wishing to participate are encouraged to register for the qualifiers
```

### [11] hash=`7861bc151d5cde12`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p3`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（03雾中鬼婆）

```text
in Paris or other cities.I received this shortly after submitting my report concerning the events on CrossStreet.This great city will be the laughing stock of Europe, if not the entire world.Unless, unless there's a way to clean the air in London.Perhaps then I might convince the Foundation to reconsider.Mr.Fogg, there's only three weeks left before the qualifiers.It's a serious effort just to address the smog over London,
```

### [12] hash=`bec1e1eaba14daa6`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p3`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（03雾中鬼婆）

```text
let alone this new black fog and the disease that has come with it.After that black fog rolled through, patients with this tuberculosis variant seem to be multiplyingas fast as hairs in the Great Artesian Basin.
```

### [13] hash=`28380767a1cfeeb8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p4`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（04久远的辉煌）

```text
Through misty woods, on paths concealed by haze.He thrice died, and thrice was born in ancient days.Guide me rightly, that I may not stray.Flowers bear fruit, and beasts give offsprings way.With eyes of fire, pierce through the cloudy maze.A letter from Saint Pavlov's foundation.Due to what?Deterion air quality?And arcane tubal keeled kiss?Um, they said the Uluru qualifiers are cancelled.Do you understand at all what you're saying?
```

### [14] hash=`29b256b1beb78ae7`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p4`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（04久远的辉煌）

```text
No, but-Go away!I said get out!You know what I don't want to hear, Aelas?Your voice and your infernal knockingDon't you never take another step into my house never just a wee bit leftsnailsLet them think what they will.I don't care the fog hag a toad monsterFailed work of an ancient alchemistYes, it's of courseCharlotte O'Hagan, you're nothing but an ugly, evil, terrifying, fog hag living in a haunted house.
```

### [15] hash=`c79e01af48bb5141`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p4`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（04久远的辉煌）

```text
You deserve every bit of it.What an age.At last, witches no longer need worry about beingcaptured in their sleep, pissed on a stake, or burnt alive.The ancient rituals are differentnow.We dance, communicating with spirits like a joyful game, or a graceful competition.The desirable.I left the pot on.Pit for the rubbish now.
```

### [16] hash=`1afe6dfabe078ea1`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
Good morning!It's this here's your wake-up call.Rise and shine, wakey time!Enough!I said enough with the gal!I'm already awake, ain't I?So stop buzzing around!Mrs Wilson, you awake?You can't be late again or old Mr Pig Eyes will be on you with his belt.What happened?You hear me?Shut up already, Liberty.Didn't you know Mrs Wilson was sick?She's sick?She's a toad, a toad what can't get out of her house to see sunlight, and decided to curse us all just because she didn't like the fair.
```

### [17] hash=`d1f56f5a92b2ac12`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
Have you gone off your rocker, Freddy?Just leave me alone.I got work to do.That's work, eh?You call knocking on people's window work?I climb up in the steam turbines to tighten up the screws, and I clean them chimneys from the inside.Think you can do that, eh?But I don't want to tighten screws or climb up chimneys.I don't like the smells.Oh, so you like the smell of this black fog, do you?All thanks to your wicked hag friend.
```

### [18] hash=`19a5752fe2c939da`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
Go away, the fog lady taught me this.Lady, you mean that hag?I should have guessed you'd bethat ugly toad witch's apprentice.Not my friend anymore.Not snail delivery day,but after she threw me out of the house last time,Maybe I'll go apologize, maybe then I can learn some more tricks from her, or at least read her books.Now why didn't you let Miss Tooth Fairy in last time?She's not a bad person, she even gave me some flying medicine, it was sweet and sour.
```

### [19] hash=`feaabd5bae5ccbc8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
You think Miss Willow's lonely?She needs new friends, and maybe some flying medicine too, this time it won't go through the window.Not that I get why she was so mad.Was it that I stopped her from eating breakfast, maybe?Well, time to figure it out.I bet if I walk in from the front door, she won't be so angry.Miss Flutterpage?What in the blazes are you doing here?Good Lord, I hope you didn't get hurt.
```

### [20] hash=`fba0d1dd65529fca`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
Miss Bartley, I'd advise you to please stay a safe distance back.No.Just look at the state of this garden.well you're right there mate it's not your typical hospital Arthur's calling itthe London Emergency Relief Center for special tuberculosis patientskind of a hospital ain't it one lady she's not from Cross Street how didyou know miss book lady swan I suppose you mean miss Caroline Bartley we're
```

### [21] hash=`916f638275a6c8fa`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
We're hoping she'll be our lifesaver.Lifesaver?Exactly so.See, my hat friend, we civil servants can actually accomplish a thing or two.We found Miss Botley, a shining star of Uluru, a talented competitor, and above all, she'san insider.She arrived in London days ago, looking for our fog lady.She claimed to be an old acquaintance.Some luck, isn't it?If she can figure out the connection between her, the Black Fog, and this fiery TB...
```

### [22] hash=`affb6b5381aaa303`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
Oh, speaking of which, that Miss Willow truly has a special name.Heh heh.Heh heh?What are you laughing at?How long have you been up, mate?Sleep?Who needs to sleep at a time like this?I'm more than energetic.I'm a veritable locomotive.Better than ever.Arthur you need to get some shut-eye mate.Is that what you think?That I'll just goback home for a little rest now?Now of all times?Dead wrong mate.We've got
```

### [23] hash=`93756e547f905b4a`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
rounds to make at the London Emergency Relief Center for special tuberculosispatients.Come with me my chapeau chap.We've got a city to save.Oh all rightMiss Flutterpage go find Miss Tooth Fairy would you?She said your arcane skillOnly when it's blowing something around, like dust or old paper, but I ain't got nothing like that with me now.I used all of it when Freddy tried to catch me.Is there anything else I can use?
```

### [24] hash=`c51b76a3c3a4b685`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p5`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（05小叫醒工）

```text
What with this wind, eh?Where's it coming from?Oi!My hat!Please, is there any good Samaritan who can spare a blanket?Oh, God bless you.Fairy!Flutterpeach, there you are.What's wrong?I've got to find a way to clear up the sky.
```

### [25] hash=`0f1035d92def6edf`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
It's been near a week.This is how the world I should have known.I'm always too naive.A dead mouse.Classic.Sure to disgust me.Rots and apples and eggs from that boring old codger.I suppose he's down to his last teeth now.Soon enough the only thing he'll be eating is porridge.Bit of comfort in knowing he hates porridge.No.I don't need to cast my arcane skills.Stand up.You loser, you.A machine lubricant.
```

### [26] hash=`ca9d26f4348d8884`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
I suppose I need to buy some.I can do this.I will do this.All by myself.Let's go.Closed due to illness.While the owner has gone to Ms.Tooth Fairy for treatment.Please leave your name, order, and address on the list below, and we will deliver itto your home as soon as the owner recovers.Tooth Fairy, alright, then I can find the owner if I go to this Tooth Fairy.Is she some kind of doctor then?Not that she could treat what ails me anyway, eh?
```

### [27] hash=`f5c68cc2ac135daa`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
What other shops might sell canary saliva and lanolin snail slime?A bit of old rope, or an old boot.Why can't it be...a swan?A black swan?Here?Really?That's why you ought to go out more often.Else you'll miss these precious moments.A chance to see something special, like a black swan.Look at it.Some creatures are born with these smooth, pitch-black feathers.But it's only under the sunlight that you can see their iridescent shine.
```

### [28] hash=`9c8a4f8ab358a135`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
That's when all the other animals can only look on and feel themselves inferior.They can never stand out from the crowd in the same way.Your silence is an answer.I know it.Just as I know every time you lash out and curse, you're cursing your own failure.What closer, Charlotte?Why don't we take a better look at it?Look at its gracefully long neck, those magnificent wings,and how it glides across the water.
```

### [29] hash=`80e55754f4bb1b6f`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
All swans are beautiful, but only the black feathers make ittruly stand out.It brings back some memories, don't it?The feeling of being one with theand the flow of each step of our dance.We were so close to perfection.All we needed was for you to spread your wings and fly.Fly to Paris, Cairo, Istanbul, and eventually to the Ullaru Rock.And it comes to me, and I can hold it in my arms,lift it above my head.
```

### [30] hash=`102f117336f2ff0a`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
Why are you looking at that swan?It's dead.Of course it's dead and gone.That's right.What kind of swan would want to be with something so ugly and stained?Of course it's ended up alone.Died alone.What else were you expecting?You didn't really believe that spread-your-wings-and-fly bollocks, did you?You ought to thank the black fog for lifting your illusion.now you can see it rightly you're not some special black swan that was born to
```

### [31] hash=`240932a62fe0bd97`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p6`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（06黑天鹅）

```text
greatness you're nothing but hello but a cripple come back why why didn't youtell me about your you're much stronger than I thought miss Willow if youallow me to address you miss Latch leave me be I'm going home I'll walkhome.I got you.Miss Tooth Fairy and I was just chasing after the Black Fog, but, but I can walkyou home first.I just want to go home.I'll go with you.Flutter page.With me?On to go?

I don't want you to follow me.
```

### [32] hash=`70ecf95336136de8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p7`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（07早午餐）

```text
The Floor Ritual is one of the most popular events of the Uluru Games.It has a bewitching style that generates a resonance between the dancer and audience.Scarlet was a genius.She was born for it.And God has sent her a coach covered in dark feathers and skilled in ancient Celticrunes.Coach Raven taught her the Primal Witch Dance that ignited a fire within her.At least, until that tragedy ten years ago, which took her leg.
```

### [33] hash=`1898a5a7549b0bef`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p7`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（07早午餐）

```text
Coach Raven had given her a pocket of flower seeds as a reward for all her diligent practicing.It said they were from the druids in the forests of Glastonbury.I guess she planted them around her house and got this garden.Now all these bizarre plants share the same strange air with their owner.Whatever you say, Miss Witch Doctor.The door isn't locked.Let's get inside.Sorry to interrupt.Diets high in sugar and fatty oils may well lead to stomach illness, Miss O'Hagan.
```

### [34] hash=`1eec1bc288059d9c`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p7`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（07早午餐）

```text
I choose the name Tooth Fairy instead of my real name, Campbell.But did you choose to let people call you Willow?Or do you prefer the name Charlotte O'Hagan?That is the name of...an excellent Uluru Floral Ritualist.Tooth Fairy.Some kind of doctor, right?I think your prescription is a little fuzzy.I'm no athlete.I've only got one leg.This Charlotte has nothing to do with Willow.Just like I have nothing to do with the Uluru Games.
```

### [35] hash=`3ed092b03c92f4ea`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p7`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（07早午餐）

```text
So far as I know, the Uluru Games do not exclude people with disabilities from full participation.Who even invited you here?It's time you leave.I'm here representing our mutual friend, Flutterpage.What for?I understand that usually the only one welcome inside is Flutterpage, but I'm here to apologize on her behalf.Apologize?What's this?An apology gift.She ran off a little before sunrise to collect these for you.
```

### [36] hash=`e3cabf627e6fb544`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p7`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（07早午餐）

```text
She collects these arcane creatures you use to make the lubricants for your prosthesis, right?But she's afraid that you'll get angry at her again, so she asked me to give it to you.Oh, I see.Now I'm the hateful, angry, wicked witch.No, you're not.The things that these people say about you, they aren't true.As I mentioned, Flutterpage wanted to apologize because, quote,she didn't want to break your heart.
```

### [37] hash=`2652f1ab0aeb0a85`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p7`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（07早午餐）

```text
Miss Bartley has told her many things about you.She never knew you're such an outstanding competitor.Caroline?Will you accept her gift?Nosy little brat.Where is she now?In the temporary hospital?You want to see her?Don't push me!Now would you stop that crying at least not here in myOi no more only come in when you let me anything you ask say anything you need me to say missSo could I still come around again sometime?

Stop your crying first lassOkay, I'll stop crying what can I help you?EnoughAlright, now leave me be, please.She's seen too much of this embarrassing side of me.
```

### [38] hash=`2980a6344f0d2c67`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
I dreamt of eating a marshmallow last night, but it tasted like rubber.And the next day, my wife asked me why I ate the cotton she had in her nose.I said it's because the air was so dirty that I wanted to block up my throat.And she laughed.Of course, she says it might be better now that I can't shout and holler whenever someone scores.These are the highest level of professional arcanists.their abilities lie far beyond the limits of our bodies, our perception, and everything else.
```

### [39] hash=`ed2b6d85adbd04ec`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
Arthur, mate, do you know what you're doing?Go on, then.Be a little louder.May as well let everyone knowa trusted servant of His Majesty's government and his talking hat are hiding out in a pile of litter.Oh, that's what you're worrying about?I guarantee you, no person in their rightmind will think that a brilliant mind such as yourself would decide to hide in a rubbishbra pretending to be a potato ha ha since when did you become a comedian I learned from
```

### [40] hash=`170fff8d53f1567b`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
the best mate once I'm back in Oz I hope to be awarded the title of Duke of Sydneyslapper not that anyone gives a toss about titles of nobility back home we've got moreimportant things to worry about in the redlands down under you know Brimley old chap youYou don't have to be a duke to be above people.All you need is someone tall enough to wear you on his head.Bloody oath, mate.Like I'd let anyone pop me on their head.
```

### [41] hash=`17992dd72e8a308c`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
I'm an intelligent being, not a bloody accessory.Look at that sailor over there.See the ropes in his hand?That right there is presently the most valuable material in all of London to me.Right.A bit of rope.But I'll tell you right now, I wouldn't have awakenedif I knew I'd end up in a rubbish bin covered in fish guts.Just a little mistake, just a little mistake.What are all these for, exactly?These are my collections so far.
```

### [42] hash=`dff93936f05c3ac6`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
A klaxon, a watering can, a fish bowl, and...A chamber pot?You've gone full bonkers, mate.You're the Fogwalker.Aren't you ashamed of hiding in rubbish,stealing old junk?It's not a junk or chap.Every piece here will be invaluable to our work.Each one is a necessary component for my invention.Your invention?For- Ahoy, sailor!You over there, please wait!Would you mind terribly leaving us those old ropes you've got there?
```

### [43] hash=`86a0da254747cea9`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
Good lord, it's down to the sanitarium at this rate.Move along, move along.No pushing.Everyone will have their chance to vote for their favourite competitor.Oi Sweeney, you only pushed me out of the queue.Good bloody job mate.I'm voting for number 007, Molson.Molson?The first-timer?Not all your life mate.I'm down for 005 Bartley, she's the top seed.Three days to the qualifiers.Vote while you still can.
```

### [44] hash=`0b3ad5a48367bfcb`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
Oi!You over there with the block rolling!Come on over and vote for the winner!Oy!Mister, stop your pushing!Oh, I'm terribly sorry.I...Sorry mate, we're on patrol.Sir, we have a situation over there.Let's follow them.Now introducing the competitors for the Uluru London Qualifiers.Bartley!Oy!Who pushed me?Majesty will ya me was you that pushed me weren't it you should be the one minding your own feet
```

### [45] hash=`53212886ec8dce07`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
Arthur I think we're only making things worse trying to move through this crowdLooks like we found our troublemakers.What do we do?Keep up with them and bring him inYes, sirArthur next timeDon't get me involved.I think I'm feeling sickbut he gave us the rope after all stop right there seems you two rough sleepers are wanted inconnection with a fight breaking out on cross street i'll ask you to come quietly and cooperate
```

### [46] hash=`d7d6135c31bfc874`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
mate say something wonderful now i have everything i need for my experiment the properties of thissea-worn rope should be able to conduct the large particles into the purification vesselsMate, shut your gob for a minute and listen.But how to measure and screen the size of the particles?We will need more sophisticated equipment.Why am I being handcuffed?Because you're being placed under arrest, sir.
```

### [47] hash=`be2c31b995777158`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
Wait a second.Mr.Fogg?Is that you?Bloody hell!Are you seriously telling me you recognise Fogg before me?How many talking hats do you know?Terribly sorry, gentlemen.I might not have recognized you for all this fog, were it not for that iconic umbrella of yours.Oh, naturally.Just as I've somehow failed to recognize the two ignoramuses that tried to handcuff a hat.We're sorry again, Mr.Fogwalker and Mr.
```

### [48] hash=`4f64d23580e360e8`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
Brimley.Anyways, mates.Best we let you go, you've got a city to save.We'll be off now.Glad that's over.I'm no fan of handcuffs, even if I don't have any hands.A little quiet, old chap.I'm just in the middle of a thought.How might I assemble it?I'm sorry, mister, but I just heard what happened.Huh?Did you say lifting the fog, mister?Are you really going to get rid of the big, scary fog monster?Will that mean you can cure my mummy?
```

### [49] hash=`19d0ac766b42d111`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
And bring back the blue sky?And then we can still have the Uluru games, right?Mummy said if the fog keeps sticking around, making people sick, then the games won'tcome.Mate, this really isn't the time or place.But I'll need some help.Would you and your friends join me in this project, young lady?Yeah, I'll ask my grandpa, my mummy, and Auntie Martha to help too.The more the merrier.We are going to build the largest fog purification machine on Earth.
```

### [50] hash=`b7ca809c6a19b131`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p8`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（08小巷落难记）

```text
The London Air Pollution Auto-Detect Cleaner.That just looks like a great honking big vacuum to me, mate.Another bad mood a miss Willow this one's your worst this week.I counted it up every 32 hoursSteady as a clock you start scolding me scolding the plants the antseven flowers IThought we'd agreed no more peeking around my house without permissionYeah, but you didn't kick me outDid you and you gave me some rye bread and lemon jam?

Don't quite know why you keep trying to act the big meanie, Miss Willow.I know you're as softy now.Deep down.Ouch!The qualifiers.Hello again, Miss Swan.
```

### [51] hash=`e05f85c9d76818fc`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p9`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（09天平与角逐）

```text
May I ask who she is?She happens to be this patient's favorite competitor of all time.She collected all of her posters and clippings, she even keeps a few photos of her as a bookmarkand in her purse.Her favorite ritualist.Looks like you haven't had a proper guest in ages.Have you forgotten how to make a cup of tea?You like to presume, don't you?Most people think she's too old to compete now, that she's, uh, retired to God knows
```

### [52] hash=`78a8197b0fec0e51`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p9`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（09天平与角逐）

```text
where.Others say she's become an addict, wasting her life away.I guess I heard in the gossip rags that some people think she's keeled over anddied.Too bad for this young lady, but I doubt we'll ever see her in the games again.Wherever she is, she's like us not to lose, even if she did compete.You just want to announce to the world you've beat me, eh?Think that'll be a fair challenge, do ya?Perhaps you ought to find someone a little more your speed.
```

### [53] hash=`3635a108dc91470c`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p9`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（09天平与角逐）

```text
Someone who's still in one piece.Again, Miss Bartley.Please turn around.I haven't any sort of tea you'd like.You have changed, haven't you, Charlotte?What the blazes are you doing?You just said you don't have any tea I'd like.The rules and scoring systems are entirely different and higher in every wayThe limits you once broke through are now considered standard for beginnersBut indeed I learned it all from you
```

### [54] hash=`42ca565392e5c2af`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p9`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（09天平与角逐）

```text
Face it.You've been left behind.You're no longer the model of perfectionYou're just a shooting star that shined too briefly, but eventually fell awayI am the rising sun.My name will be eternal in this sport, long after yours is forgotten.So be it.Go on.Be the glorious sun.And leave this fading star alone.Lisa, you're back.We were just talking about you.About me?What about me?About your dream and your favorite competitor.
```

### [55] hash=`43f05249e7bfd53d`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p9`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（09天平与角逐）

```text
Oh, you mean Charlotte O'Hagan?yes we that's great but mr.fog needs us for a project he says we can still havethe games if we all work together and maybe everyone will be able to attendthe qualifiers maybe even Charlotte O'Hagan a project what sort of projectgive me a break what are they planning to do this time another useless buildsthat won't pass the House of Lords.Sorry for interrupting.Did I hear you mention Mr.
```

### [56] hash=`a96e2e6d19a58e9a`

- lang：`en`｜version：`2.3`｜arc：`圣火纪行：东区黎明`
- doc：`BV13USLYFEZH_p9`
- title：《重返未来：1999》2.3版本「圣火纪行：东区黎明」全剧情 - Reverse: 1999｜4K（09天平与角逐）

```text
Fogg?He said he's making somethingthat will lift all the fog from London.It's his great invention.With everyone's help, we can build a huge machine,but he says we'll need lots and lots of things,such as, um, pistons for the mechanic lung and...I'll take it over from here.Thank you, Lisa.Mr.Fogg?Mr.Fog?
```

### [57] hash=`6a27907ed0190ebb`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
I'm ready to go.Please fasten your seat belt, miss.We're setting off now.You ever been to London, miss?Yes, a long time ago.Long, eh?Five years?Ten years?Longer than that.Come on, Finn.How long?You don't look 100 years old.The hospital is two streets away.Oh, by the way,it's been arranged for you to meet Mr.Fogg first,The tube?You won't like it, miss.Not the kind of place for a decent young lady.I'll wait here for you, love.
```

### [58] hash=`7ecd5423c6ffcbc6`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
I'll do my best not to crack into my flask of whiskey while I wait.Thank you.I'll be back soon.How are things at SPTM, Tooth Fairy?I'm hearing rave reviews about their school physician.I'm glad to hear it.Young children are particularly easy to soothe.a few candies and they behave just fine, a little toffee or a nibble of a fruity sweetand they've forgotten all about the tooth fairy's taste.A proper dose of sweets serves to calm the
```

### [59] hash=`044b16e640256c71`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
nervous system and that doesn't just apply to kids.Your work here is undoubtedly busier thanmine at SPDM.Besides, you're directly responsible for our timekeeper, the littletroublemaker.But I am sure you didn't summon me here all for a little chit chat.The foundation has now confirmed the correlation between social turmoil and the emergenceof the storm.Our branches around the world are now making efforts to collect information
```

### [60] hash=`78b15cd5ea1eae47`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
on these key social movements.As you may know, there was a strike thathas only just ended in London.And there is something I'd like to show you, besidesthe strike itself.Tobacolosis.Indeed, there appears to be abnormalities concerning air pollution and the reported casesof TB.Compared to our records before the storm, TB mobility rates are extraordinarily high,approaching levels that shouldn't be seen until the Great Smog of 1952.
```

### [61] hash=`e1cb913fdce988da`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Our Mr.Fogg, the Fogg Walker, has also reported that there is something unusual aboutGood luck then.Mr.Fogg will contact you when you arrive.He is our liaison between the Foundation and the British Government.He'll take you to the hospital, handling many of these respiratory patients.You will be given full trust to resolve this problem.There is something else.The Uluru Qualifier will soon be held in London.
```

### [62] hash=`06859556407cf911`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
It may factor into your investigation.Qualifier?Uluru London Qualifier coming soon.Arcanist Fair in Cross Street.Support your favorite competitors.Winners will represent Great Britain in the Australian Finals.Australia?They shipped my uncle off to Australia back in the day.I always figured he got done in by a kangaroo.But if the smokey gets any worse, I think I might chance it.Maybe I'll find him in the outback there.
```

### [63] hash=`34e3467e690848c0`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Or at least avenge him.That smoke seems to have severely damaged that hospital.But you don't seem concerned.We've seen worse, miss.You wouldn't believe how many houses we lose a year of gas line explosions.Nothing much can shock us Londoners.It's a city where you commit arcanists from all over the world.Arabians, North Africans, Indians and Japanese.Who knows what kind of arcane skill they can cast.
```

### [64] hash=`6096b3c92b3fc64d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Let's follow the path of this dark soot on the street.Maybe we can find it, or its owner.As you like, miss.Seems it's leading us to the East End.Only thing that comes out of the East End are drunks, tramps, and Jack the Ripper.Bloody!Miss, I swear to I, Evan, that I have not had a drop of drink today.This is the East End for you.Either you it's someone, or someone it's you.please miss take a look for me tell me if I hit anything I can take it it
```

### [65] hash=`65d4ea6fdc323d54`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
appears there's no one in front of the car no one I'm up here hmm look up theremiss can you catch me she's being lifted up on the wind is this her arcane skillif so she's amazing for her age you ain't going to qualify for nothingI'd like to make amends if I hurt him, especially if he can't work.He doesn't work, but you still need to apologize.Come on out, Sudokiki.This bug here wants to apologize to you.
```

### [66] hash=`4894459024d17e35`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Baffin doesn't even have a waist, and he's as big as a kangaroo!The waist is right there.Can't you see?A frightened critter is dangerous.Please stay back, child.Sir, I suggest you cover your mouth and nose.There's something off about this smog.Christ, so the rumours are true.I never should have gone into an alley like this on such a smoggy day.He's looking at the end of the alley.He must want to go that way.
```

### [67] hash=`bd8de970a754d0e4`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
The smog's not as thick there.I think he wants to escape.Maybe the smog's harmful to him too.Get over already, you stupid car!Hmm, it's a bit sour, like a mouldy raspberry, but still sweet.Why aren't other pills as sweet as yours?I see, so you're a witch doctor, aren't you?I can tell from your metal mask, teeth necklace, and the golden fairies in your jar.That is a reasonable assumption.So you're here for the olive root fair then?
```

### [68] hash=`a3fb4906532ad931`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
You've even got the flyer with you.I'm here as a doctor to investigate a tuberculosis outbreak, but the strange black fog damagedthe hospital I was heading to.I followed the trace it left behind to this area.Black fog?There ain't no black fog.Around here the smog is yellow, and sometimes I've seen black smoke puffing up fromthe factory chimneys.But never in Cross Street.I'd like to be an arcane skill miss, lots of us are canists here.
```

### [69] hash=`72fe5c7f15dc02fa`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
That's why we're all chuffed up for the Uluru Qualifiers.There's harbalists, sidekicks, diviners, magicians...Thank you, Flutterpage.I think I've got the idea.Then I'll show you around.You'll like it here.Stop littering, you grimy little bunk!Uluru Fair!The trace of the Black Fog seems to have disappeared into a large gathering of volcanoes.But I was called away to deal with matters here on Cross Street.
```

### [70] hash=`3f07f72fb5a8096b`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
It's a happy coincidence that you popped by.It will save us both some time.The matter?You mean the air pollution?Not precisely, no.Though one could say the problem is related.In fact, it seems just about every one of our problems comes down to these sticky contradictions.For example, contrary to good wisdom,The people of Cross Street have opted to continue their fare despite the obvious dangers of the fog.
```

### [71] hash=`dcb2f2c89a4f2718`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
That's just unreasonable.You're the unreasonable one here, mate.Stop the Uluru Fair on account of a bit of fog.Fog in London.Should we cancel if there's water in the Thames next?Citizens should be made aware of the harm caused by fog and reduce unnecessary outdoor activities.Pardon me, you lot government officials.next I wonder sometimes despite being an arcanist myself it's hard to understandmy own people but that's what they think around here my colleague is
```

### [72] hash=`71f55f685747c6df`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
presently out investigating this curse they mention but to say nothing of hisintrepid skills as a Ranger I doubt he'll produce any evidence of this soHag.In fact, he-After a little help, mate, we've got trouble!So, here it is.What's that after you now, old hat?It's the Black Fog.Seems I've startled it.And now it's sent our critters into the streets!Steady on!Let's charge like soldiers of the Great Emu War!
```

### [73] hash=`4aaffbed8caf7130`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
It's the Hag!The Hag's cast is coming for us!Those nasty critters are coming from her garden!Run!Oh, dammit.All I know is I gave her snails, and then she asked me to stay around her house for a while.When she's not in a sour mood, she even teaches me some words for arcane skills.But if she is sour, then all she does is hand me some books, and I can't even read most of them.Don't go asking her too many whys.
```

### [74] hash=`ffe828ddc6a46bdc`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
If you do, she says, get out!And you've got to go.You left me a book.It's got a carbuncle on it.Come here, Flutterpage.Are you alright?I thought I could play at her house today.Would you like to do something else?Like what?Like see your new friend, Mr.Hat.Mr.Hat?Uh, ah, Miss Flutterpage.I'll ask you to not wear me on your head.I know I can fly, but that doesn't mean you can treat me like a kite.Besides, I'm due to begin my patrol.
```

### [75] hash=`9e1a1b599b3ea5f0`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
I need to...That gives us some time for business.First of all, allow me to express my respect for your adventurous spirit.A haunted hide mansion whose owner feeds on snails.To visit her so quickly on your own initiative was a bold move, Miss Tooth Fairy.Here's your tea.No sugar, just as you asked.The connection between this lady and the Black Fog will require further confirmation.However, judging from our encounter, she doesn't seem to have much concern for the world outside
```

### [76] hash=`8a1bf8018c19e13d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
her home.I also noted that the word Uluru seemed to irritate her.Uluru?As in the Uluru games?Not a fan, I take it.It's certainly odd for an arcaneist to have a negative impression of the games.though not unprecedented which reminds me of this letter I suspect our fog ladymight be glad to hear it letter from the st.Pavlov foundationUluru games organizing committee to the Uluru London qualifiers organizing
```

### [77] hash=`f1a70d8f5663de59`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
committee copied to the office of the London atmospheric cleanup committee dueto the rapid deterioration of air quality in London and the presence ofunidentified arcane related tuberculosis outbreak.We regretfully have decided thatthe Uluru London qualifiers will be cancelled until further notice toprotect the health of competitors and spectators.Competitors still wishing toparticipate are encouraged to register for the qualifiers in Paris or other
```

### [78] hash=`8d17d58912f50193`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
cities.I received this shortly after submitting my report concerning thethe laughing stock of Europe, if not the entire world, unless, unless there's a way to cleanthe air in London.Perhaps then I might convince the Foundation to reconsider.Mr.Fogg, there's only three weeks left before the qualifiers.It's a serious effort just toaddress the smog over London, let alone this new black fog and the disease that has come with it.
```

### [79] hash=`9e7ce7f514cf984f`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Three weeks, one for making plans, one for enacting said plans, and still one more for the final procedures.What are you doing now, Mr.Fogg?Thinking, Ms.Tooth Fairy, is how I make the plans.Forgive me for interrupting, Arthur, but I had to call off my patrol earlier than expected.I'm afraid I need a favor of you, Ms.Tooth Fairy.Hmm?Would you mind helping us with some of the sick?After that black fog rolled through, patients with this tuberculosis variant seem to be
```

### [80] hash=`bb3ec3eb2f038406`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
multiplying as fast as hairs in the Great Artesian Basin.Through misty woods on paths concealed by haze, he thrice died and thrice was born inancient days.Guide me rightly that I may not stray.We wanted to show you the arcane skill.You taught me on a bad mood.Aren't you?What happened?I promise I didn't call you miss Willow in front of othersYou said I can call you miss Willow when it's just you and me right and you actually listened
```

### [81] hash=`7c31215e0b750f5f`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
First time for everything a but it's not about what you call meThen what is it?Let me help you up.I don't need itDue to what?Deterion air quality?And arcane tubal keeled kiss?Um, they said the Uluru qualifiers are cancelled.Stop!Do you understand at all what you're saying?No, but-Go away!I said get out!You know what I don't want to hear?Alas!Your voice!And your infernal knocking!Don't you never take another step into my house.
```

### [82] hash=`cda961aced914eb9`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Never!Just a wee bit left.Snails?Let them think what they will.I don't care.A fog hag.A toad monster.A failed work of an ancient alchemist.Yes, yes of course, Charlotte O'Hagan.You're nothing but an ugly, evil, terrifying fog hag living in a haunted house.you deserve every bit of it what an age at last which is no longer need worryabout being captured in their sleep pissed on a steak or burnt alive the
```

### [83] hash=`de795d60210a61c3`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
ancient rituals are different now we dance communicating the spirits like ajoyful game or a graceful competition the desirable I left the pot on brotherShe's a toad, a toad what can't get out of her house to see sunlight and decided to curse us all just because she didn't like the fair.Have you gone off your rocker, Freddy?Just leave me alone.I got work to do.That's work, eh?You call knocking on people's window work?
```

### [84] hash=`eab8d53d34043a6b`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
I climb up in the steam turbines to tighten up the screws and I clean them chimneys from the inside.Think you can do that, eh?But I don't want to tighten screws or climb up chimneys.I don't like the smells.Oh, you like the smell of this black fog, do you?All thanks to your wicked hag friend.Go away.Huh?The fog lady taught me this.Lady?You mean that hag?I should have guessed you'd bethat ugly toad witch's apprentice.
```

### [85] hash=`1e50d27a44307fd3`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
You're not my friend anymore.Not snail delivery day,But after she threw me out of the house last time, maybe I'll go apologizeMaybe then I can learn some more tricks from her or at least read her booksHello.Now, why didn't you let Miss Tooth Fairy in last time?She's not a bad personShe even gave me some flying medicine.It was sweet and sourYou think Miss Willow's lonely?A ranger?Are you really a ranger?
```

### [86] hash=`c1b4aad0f3a1b2b7`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Can you be a ranger without a real horse?Will I get a hat like you if I get to be a ranger?Are you here for the lady living here?Miss, you look a lot like Miss Willow, the Fog Lady.So straight and proper like a swan.Miss Willow?You said?Miss Willow?Did she say you weren't allowed to call her that too, miss?Allowed?What kind of nutter has she become?Hmm.Thank you for taking me here, Mr.Brimley.I can handle the rest myself.
```

### [87] hash=`9d46ccc984e573a3`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
You're welcome.Let's go, shall we, eh, little tacker?It's not safe to leave you here.I'll escort you to the hospital.Ms.Tooth Fairy needs your help.All right.The hospital was a big, big building.This is more like a fair.Only with sick people.Well, you're right there, mate.It's not your typical hospital.Arthur's calling it the London Emergency Relief Center for Special Tuberculosis Patients.Still kind of a hospital, ain't it?
```

### [88] hash=`eb106fc1718c241d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
Swan Lady.She's not from Cross Street.How did she know Miss Sw...Fog Lady?ago, looking for our Fog Lady.She claimed to be an old acquaintance.Some luck, isn'tit?If she can figure out the connection between her, the Black Fog, and this fiery T.B.Oh,speaking of which, that Miss Willow truly has a special name, he-heh.He-heh?What are you laughing at?How long have you been up, mate?Sleep?Who needs to sleep at a time like this?
```

### [89] hash=`8a91320dfba9b15a`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
I'm more than energetic.I'm a veritable locomotive, better than ever.Arthur, you need to get some shut-eye, mate.Is that what you think?That I'll just go back home for a little rest now?Now of all times?Dead wrong, mate.We've got rounds to make at the London Emergency Relief Centre for special tuberculosis patients.Come with me, my chappo chap.We've got a city to save.Oh, alright.Miss Flutterpage, go find Miss Tooth Fairy, would ya?
```

### [90] hash=`5d9b5c87bfeb8fd1`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
She said your arcane skill might be of some help.Arcane skill?Help?How can I help a witch doctor?Maybe Miss Tooth Fairy will tell me.But where is she?So many people here.I can hardly tell them from one another.Oh but she has got those golden fairies with her.Maybe I can see them.Like how Miss Willow taught me.To control the wind you need to learn to see it first.Can you see the wind, Lass?When it's blowing something around, like dust or old paper.
```

### [91] hash=`00dd00358345b98f`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p76`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 1~5）

```text
But I ain't got nothing like that with me now.I used all of it when Freddy tried to catch me.Is there anything else I can use?I see it!What with this wind, eh?Where's it coming from?Oi!My hat!Please, is there any good Samaritan who can spare a blanket?Oh, God bless you.Fairy!Flutterpeach, there you are.What's wrong?Got to find a way to clear up the sky!
```

### [92] hash=`91af9ad66172d0c4`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
It's been near a week.This is how the world works.I should have known.I'm always too naive.A dead mouse.Classic.Sure to disgust me.Rops and apples and eggs from that boring old codger.I suppose he's down to his last teeth now.Soon enough the only thing he'll be eating is porridge.Bit of comfort in knowing he hates porridge.Bound by steam, to curse, bumping into ghosts during the Samhain.Curse, lost everything betting on the ponies.
```

### [93] hash=`0dad7cc27c8a3e55`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Each and every misfortune must surely be Willow's curse.Superstitious fools.Scheisters.Now these are new, aren't they?Bloodstained rags.Wonderful.Sooner or later they'll all cough their lungs out.I don't need to cast.My arcane skills.Stand up.You loser, you.Machine lubricant.I suppose I need to buy some.I can do this.I will do this.All by myself.Nothing to it.Let's go.Closed due to illness.While the owner has gone to Ms.
```

### [94] hash=`252eecb64a549bd3`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Tooth Fairy for treatment.Please leave your name, order, and address on the list below, and we will deliver itto your home as soon as the owner recovers.Tooth Fairy, all right.Then I can find the owner if I go to this Tooth Fairy.Is she some kind of doctor, then?Not that she could treat what ails me, anyway, eh?What other shops might sell canary saliva and lanolin snail slime?old rope?Or an old boot?
```

