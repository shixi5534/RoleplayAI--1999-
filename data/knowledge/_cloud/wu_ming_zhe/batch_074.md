# 剧情图谱抽取 · batch 074

- 角色：`wu_ming_zhe`
- 批次：**74** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.3」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_074.jsonl`

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

### [0] hash=`6871ca605215a98a`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
oh just in time is this yours yes put it away kid this shine only few touristsare willing to only the locals know they have something to do with thatcomet myth I had about some mythologies are the original translation of therealm that's how we located the star it reaches level five on Torino scaleMeet your shower.So many of them as the news mentioned.This Deepa festival will become a disaster.It's all because of my sister who I've only seen once in my life.
```

### [1] hash=`f7500aaedf435bf8`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
It's also my teacher.Ms.Shajah?Why?How do you find this place?My dear children, enjoy your Deepa festival.So meet your shower.I'll smash that door open even if it takes the other arm of mine.When did you last look up at the sky?Not how you look at the stone.You should have lowered your head.Hypotheses have been made regarding the quasars as follows.The darkness below the podium is boiling.The eyes were the questions in inspection.
```

### [2] hash=`e76c645df47daaa3`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Some behind glasses are cast out of the darkness.Just like the signals beamed from several light years away and received at the top of the observatory.Based on the data of its redshift, Dr.Schmidt deducted that it is moving away from us ata recessional velocity of one sixth of flight speed.In most cases, we would consider a stellar black hole as what is left from the gravitationalcollapse of a star.
```

### [3] hash=`7d3469fc94d0d5a7`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
They fight, attract each other, and merge into a supermassive black hole to whichthe stars in the nearby galaxies will be eventually pulled by gravity.Page three.Here it is.And there was neither existence nor non-existence.There was neither the realm of space nor the sky beyond.Then there was neither death nor immortality.There was neither day nor night.Inside the quasars, there is a violent activity occurring
```

### [4] hash=`21fdf98db0f9ae0b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
that is close to a supernova.It devours stars,and the gas cloud turns into starsout of gravitational driving.Thus, a new star is born.It is a graveyard filled with corpses,as well as a cradle for new stars.That was a successful lecture, Calaboona.Thanks for your rare compliment.I can't believe the first thing you doafter the long absence is listening to my embarrassing speech.You see, this is not my thing.
```

### [5] hash=`a41fcdc1bc1f6491`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
I'm still struggling with a word I should use in part three.Oh, but you know I won't pass up a good chanceto sit in the audience,to be someone who can smile knowinglyat the argument made by the lecturer,knowing full well the thinking process behindwhile staying close to other whispering opinions.This is the perfect spot for observations, like a perfect observatoryfrom which we witness the events in the universe.
```

### [6] hash=`12a6414ac46709f9`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
I'd rather not give a commenton your personal taste.Kumar, I think we should make someadjustments to the details of the following observation.Here's an idea, howabout we put away the work for the moment?Forget those things, just look atstars.Simply fix your eyes on them.Move over, the grass beneath me feels like pine needles.Donnie from the institution had paid a visit here.Based on his attitude,I may tell he was doubting my identity as a human.
```

### [7] hash=`7e5a1ff2a194fdc0`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
If it goes on like this, we are likely to be kicked out of our own project.I've destroyed all the observation data of that special celestial body.At least through this we can keep the observation method between you and me.You seem...have I done anything wrong?No, as a research student, you did an excellent job, though no more than I'd expect from a student of mine.That's just what we've been doing, isn't it?
```

### [8] hash=`3c8614f6035a0fc9`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Hiding in the corners, doing research that completely has nothing to do with others.You know what?I'm a bit tired.Seriously.Tired of the pointless power struggles between these specks of stardust.We all know none of us could avoid the fate of being restored to the basic elements ofthe universe after we die.Never mind, it's not the first time it's happened.I've never been welcomed on either side.Speaking of which, my parents, yeah, I told you about them.
```

### [9] hash=`604a4b87949df051`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
They abandoned me because I had little so-called talent for Arcanum, and now they are showingremorse for what they have done.There's more.My stupid younger brother knew nothing about what happened to me.He didn't even recognize me, his own sister.You paid them a visit this time back in your hometown?Visit them?No, sweetheart.I went home to…to do many things, except to hear some old people's apology.
```

### [10] hash=`a3096ed2d9a02a3b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
I've never cared about those things.I went there to deal with a little business, and it was done smoothly.So smoothly, that I've taken care of everything there is to be done.Calabona, if one day we can see that celestial body with our own eyes,or even touch it with our own hands,I will definitely.Komar, what are you talking about?Excuse the sake of Marianne Le Normand!Oh, finally!Ouch!This train train really hurt my neck!
```

### [11] hash=`a21a647bb72312c6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
How would it be good if I could sleep in my bed for such a cool and pleasant time, or rather stay in bed with mom in the wind of these topazes?When will they approve my vacations next time?At the moment, Celeste's energy seems to be perfectly strong, and the best zone of observation is near Delhi!What a provident opportunity for this genius of divination!It would be crazy not to do anything!Let's wait and see!
```

### [12] hash=`581358e12cfef2fc`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
When I find the right place to meditate, I will go back to the top!Let's see what the questions are on this poster.DIPA FestivalIt says that DIPA Festival is missing one of the major champions every year to seek the blessings of...So it's because of the rain and the weather here!I think I read the name in the documents.I am in the east of Chandigarh at the moment.Could there be less signs here?This map is in English on the other side.
```

### [13] hash=`fbc5fc823e5f64fa`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Very good.It would be even better and clearer if it was in French.The place I found thanks to the divination is called......Mort.It's a temple!I have to go back to his cave in the north?Well, a temple.This may be related to the myth of the comet that I read before.Isn't it also one of the places where we can see the next rain of meteorites?Great, that's where I'm going then.Yes, my pen.Very well, let's note it.
```

### [14] hash=`e6eb1b3f214ca3d4`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Well played, everything is very nice in the new city.Much better than the ceiling of the Delhi station.I wonder how mom and dad are going to get married now.It's dangerous.It's really fast when you negotiate.Just a quick siesta.Very short.It's amazing.What a beautiful girl.Friends, did you see that?That girl must be very restless.Who is sleeping on the train station.Oh, I can't see anything, boss.
```

### [15] hash=`2eb0dac447ea3d07`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Just like you, everyone's eyes are not as good as yours.Oh!Thank you.Oh!Miracle jewelry and wallet.But even in such a deep sleep, what is it that is so tightly held?This is the map that they give at the railway station for free.Is it something valuable?Like a map of the treasure.If you can get close to it in the books, then?Let it be.It will be very difficult for you.If you go left, take the card the same way I taught you.
```

### [16] hash=`78de47f4ad46ee25`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
And if you get it, tell me by giving me this sign.No problem.Carefully, this will be your first step in our work.Oh, Mr.Jaco, don't ever tell him that I taught you this job.Go!No one else should go and get it before you.Kier Kishore's balance!Is this yours, miss?Angela Mom gave me!Are you?It fell on the floor.I was just picking it up for you.There!Don't lose it again.Nuh-uh.It's yet too early to say thanks, girl.
```

### [17] hash=`9d87951f63f3c022`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Hmm?About three minutes ago, or five minutes ago,this fellow was wandering around you like a sneaky badger.Trust me, this is no friendly encounter.What?I've put it in my pocket.Someone needs to work on his techniques.Right, boy?Let me go!Go!It's a waste!Go!Do your own work!The police station is not as bad as you think.No!I will never ever go there!That daddy!Followed us deep!Watch my hair!You little thief!
```

### [18] hash=`4f87be14dd368e21`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Ah, you!Boy!Wait!Just in time.Is this yours?Uh, yes.Put it away, kid.Thank you.I hope I didn't damage them during the chase.One, two...Hmm?There's no fish.Where did they go?Thank God, I've already made a plan to run away.And no one runs faster than Ajr.Be careful.Run away.Poor Ajr.I'll make a profit from that girl.And in that too, in which you didn't succeed.Hmm.So that golden hair is an easy target.
```

### [19] hash=`7a3ef7f5c011dc8c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
You will see how, Kanjeera.Hey, what did I put my foot on?Was she looking for this thing?Yes, my eyes will not deceive me.This is really a map of a treasure.Look, she has even made a star.Just like a picture of books.You are so lucky, Kanjeera.This is amazing!Let me see.I have to read with the notes.What is this?He has written all the words wrong.Even the dot and the numberon the words.Don't even bother trying!
```

### [20] hash=`7c6f03bf8ed785c6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
It's in French!Hey!Don't even think aboutmy treasure!What are you muttering about with my map?Justpick it up andLook for its owner.Hope I can help.Matilda needs no one's help.Not to mention from a girl who just showed up out of nowhere.Don't touch me!Is this your first time in the village?On your own?What's your plan?Sightseeing?Family visit?Or looking for some?Go first.Why is that any of your business?
```

### [21] hash=`6da40139dc0654d1`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
I mean, perhaps not clear to you, but in fact I'm a guide who always gives best service.A guide?Who always gives the best service?Tour guide maybe?Anyways, I tell you, nobody knows the village better than I.Hey, don't stare at me like this.I'm wandering here for a reason.I only give services to outstanding and cool people.They have good taste.I find you at the station from all travelers.My most great customer ever.
```

### [22] hash=`b8f1097e42cc6ff0`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
The outstanding and impressive people you say, hmm at least you have sharp eyes.See the place you was visiting is different from others.This shrine only few tourists are willing to, only the locals know.And now people can only go into 3 caves out of 4.But if you choose I, I can take you to North Cave, even if it's not open.You're going to take me there.How I do that?Local connections of course!No wonder there were some discrepancies between
```

### [23] hash=`4775bc8945fb4527`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
the documents and the tourist brochure!Because I knew this all along!Who are you laughing at?Oh no my dear guest, it's just sneeze!You see,I just make a living here.I'm short and thin,can't compare with adults!And you is so great!You will not let eye,beak, poor kidGet hungry for no money, will you?Even if you look at me with those puffy eyes.First sight I know, you are the lady with great taste.Just like the Sand Cat, brave and smart.
```

### [24] hash=`ad944c057430879d`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Sand Cat?It sounds like a smart animal.Anyways, you is lucky to meet me my lady.Well well, for a great customer like you, I can only suffer some loss.Just 200 rupees and I'll show you the shrine and the whole Moorpunk villageWith a special Deepa festival tour on the houseWant me to recommend a hotel?I know good hotels tooYes or no my dear guest?My most great guest?Please?I'd love you to be my temporary assistant
```

### [25] hash=`de8d299eb3425426`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Sad alreadyExcellent!Have you arranged a shuttle bus for the travel?I have something gooder than bus for you.I promise you!Quick like flash!It's a jerk again!Damn it's enough for one last time!Don't borrow that annoying human thing to her!Not yet, Vespa!Hold that button!Sorry, you must not be used to this.Here, use it.If you want yourself dirty, fine.You look very decent after all.Here it is.full of pearl, white, must and sanders
```

### [26] hash=`b79ee6b30824c36c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
calming palo santo and cinnamonyou feel your chakra open?I can also smellhmmma lot of mangothat smells goodjump over this wall and we're inthere is at least a hidden side doorto see the closed cave you must pay a pricethese are your local connectionsTuk-tuk, my guest?No tuk-tuk this village is faster than that.Uncle Sinha is not so nice and lend me if I don't give him my lunch money.My root, don't need entrance ticket.
```

### [27] hash=`bc534329e8068314`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Shouldn't you give me credit?Now come!Although I think you don't like this rudebehavior.And considerate enough not to wipe my nose on your skirt.Yet you repay my kindness withDon't climbing over a wall up this height is really a piece of cake.Do you need a hand getting up here?Huh, weirdo.Now what this scum?Better not be lying.What's that in your hand?Want a bite?The prayers are so pious.So don't worry, the fruits is tasty.
```

### [28] hash=`6f6d071e18d60a89`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Mmm, like I expect, so sweet.Did you take it from the oven?By the way, I hope you're not afraid of snakes, I'm a special kind.Tell us about what exactly you're referring to, specially rude or specially annoying.Why so angry?I mean, I'm a genius.Hope I don't scare you.Relax, I'm not like others.Are you serious?All those good virtues you can see in a person doesn't look like one.I thought all our chemists except me are like...
```

### [29] hash=`fd32448c88806f80`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Like what?Like the villagers.Those old mans yell when they see humans like annoying monkeys or crowing chickens.They even drive humans away.Don't care they are here to help.Why you think only the train station is tidy and clean?Humans in other places is all drive away.I am not like them because...Anyways, I never thought there is more a pianist like he.You read too little and know too little.Just you follow my example and adopt the style of every pianist.
```

### [30] hash=`7106d4ac52e1e268`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Mauta say there is just a few people outside.So up your head, stay confident and walk out like we paid.Nice.Nobody around as usual.But I still suggest you be careful sinceI understand the damage been digging.Just don't involve me if you must break something.So this is the head of Fintre?Dark and scary, but this is what must go through on the way to treasure.Just like you must say, open sesame, right?
```

### [31] hash=`8b4ce6218b10cd2e`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
I really don't know what to make of this treasure you've been mumbling about.I hope you didn't get the wrong idea.I see what you mean here, relax, I will zip my lips and tell no one, I'll just stay herethen.Everything good luck.Anyway, despite all the strange things you've been talking about along the way, you havesuccessfully taken me here as promised.I guess here is where we part, thank you.I wish you all the best, my brave guest!
```

### [32] hash=`b2f4049f3944d81f`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Even if a snake or a dragon is waiting for you,you need to get a treasure.We'll meet again!This mural painting seems to have something to do with this myth.Here!On this document!Let's see...I found it!Before the serpent struck in night sky, the stone house of Azura rose to the north of the head of Vindre.The master of the stone has acted with countless feet, with countless eyes, to trip, to pry, and bringing the blessed house of men to rest.
```

### [33] hash=`0c3f21ad680da407`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
C'est peut-être l'origine d'une créature mystérieuse, le coup du serpent, c'est à dire le meilleur moment pour s'entraîner sur l'énergie céleste, et lorsque la comète traverse le ciel, darkness reaches the man as the serpent's tail reveals itself.Some are sent down the great slopes and never return.For desire is the unfallible devourer.Le désir.Je devrais méditer avant de m'enfinir.The circle of everything.
```

### [34] hash=`a6547f4fc08da3a5`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
The tip of the great tail.All.Did I mishear?It's not normal!That this statue was in this position before.It's not good!It's time to turn back!Hurry up!We have to hurry up!Think about what you've learned and practiced before!Do you want to offer your seat to the senior?Handle it gently!Get on your feet!Well done, little diviner.Ramaniyani ariyani...My legs...sit themselves...Close your eyes.Don't look at anything.
```

### [35] hash=`2854897ed745572d`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Illusions will destroy your will.Mayura Abiratani, a woman from the train station, looks like part of our destinies are now tied together.Kid, what are you doing here?I don't think this place is open to tourists.Not your illusion?They're not.Please, stay behind me.They look real.Are you alright?Not illusions this time.How did Kumar do this?I was only here for...But time for explaining.We're at the exit soon.
```

### [36] hash=`2004edc26318acb6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
Remember, leave this village as soon as possible after you're out.Do not...Watch your head!Harder than I thought.Dad hadn't told me those statues could move.Again.Huh.That's dangerous.Ah, sorry.Though you have a very impressive appearance as a statue,your attitude and manner are problematic.Ha!Hey, you guys alright?These things are freaky.So, do you know where they came from?My head almost got smashed when I reached the entrance.
```

### [37] hash=`094b27619163b292`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
I'm welcome by these things as soon as I'm back.What a surprise.Wait, aren't you the little one from the train station?I helped get your stuff back.Remember me?Yeah, that's me.That was one merciless bite.Huh, what a happy coincidence.Well, maybe this is not the best place for a reunion, but the occasion is not for us to decide.Oh, I should introduce myself this time.The name is Shamane.Sorry, I wasn't much of a helping hand earlier and let that kid get away.
```

### [38] hash=`eb5f672094902908`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
But this time I have made it up to you.Huh?You have made it up, I guess.Sorry to interrupt you.But I think this place is safe only for now.It'd be a wise choice to leave as soon as possible.You mean more than this cave.Actually, are you tourists?I'm hoping you can leave this village in a couple of days.Hmm?I know this sounds weird, but you need to trust me.That's how you recognize me.Easy lady.Take your time.
```

### [39] hash=`9c63b111430af383`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p26`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜1~4）

```text
We're listening.Oh, here's your ID.Miss KalaBona hold it.Thank you.My Galap nahi ho saktaHow come you have Kumar stuff on your belt?You you you know KumarLet me see.Page one, page two, page five.These papers speak of celestial energyAnd exactly the kind of energy I want to exerciseThe analysis on the arcane energy is very similar to that of the documents I found.Not completely.This one, it seems.
```

### [40] hash=`54a425252c41366f`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
वाक्या कमार का खाना थाकुछ होना जाहिये था ना?उसे उसे कुई राक्षस तो नहीं खा जायगा?हे भग्वान रक्षा करना उस कमंदी मूर्ख कीजो भाग निकलाओ और मेरे लिए सारा घजाना चोट रहासम्हल केशुप चाबवो तीक हैवो कहराई में क्या करी ही है?वो दोनों कौन है?मुझे नहीं पता था कि यहां इतनी सारी चटाने है!तीक है!चढ़ते रहो!लगभाग पहुछ गए!पत्थर है क्या?ऐसा लगता है कि यह वहां मौजूद बत्सूरत मौर्तियों में से एक है!अरे!ये बिल्कुल वैसा ही है, वैसा ही, थानी की तरहां।
```

### [41] hash=`8f06fee6725b46a0`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
हाँ, ये सही है, वो खजाने की रक्वाली करने वाले गोलिम।वो सच है, मैं जानती थी।और वो अज्गर जो महल को खाता है, वो रत्तन जो सुमंदर को तोरता है।खुड़ जा सिन्सिम्मिश्शर्जा जूट पोल रही हैवो परी कथाइन नहीं हैइसमें कोई अस्छेरे नहींकि उसके दो सहायक हैवो खजाना खोजने वाले हैउन्होंने रक्षकों को हराया हैजुपकर उनका पीचा करोऔर में ज़ियां से थोड़ा सा कजाना मिल जाएगाजो वो भीजे चोड़ गए हैजैसे कासेन निर्तराजू से सिक्का निकाला था
```

### [42] hash=`f30c7412ba919093`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
एंट्यिंग में हिंडी वर्ड में सब चाहिता थाऔर पर आप मुझे बार प्रागा लेता नहीं जासळा पर आप लेताShe's the bad guy associating with the manus !!!But his abnormal growth curves, the fluctuation of celestial energy is a man-made result ?Actually, I'm not 100% sure about their association, but yes, your conclusion about the growth curves is right.The fluctuation was caused by an unnamed celestial body, and its existence is only known to Kumar and me.
```

### [43] hash=`1de7878362cb8dfd`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
इसक्या के वेश्ट्ट्ट हमारे भाना उनिवर्सित्य के लिए रहा है.आप उनकाइइंट पर पीछणाएटि का लिए भी रश्ट्ट्ट्ट।तो अभी गुद्द है तो आप लिए जास्थि तूए राटिकार पर लिए उनकाइइंट्ट्ट्ट।And we were expelled from the university.After that, our disagreement got even worse.In the end, we took different paths.But apparently, neither of us gave up on the research.We could frequently feel the existence of each other from the changes of the celestial body.
```

### [44] hash=`b9484a7bcd983280`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
And one day, I found an abnormality during the observation.The energy never fluctuated in such a fierce and peculiar way.ह declared to contact herbut when I finally found the lab she had worked inThe staff told me she had already leftGreat common friend told me she had seen Kumar by coincidenceShe saw her leaf with her madnessAnd I found this from what she left behindcompared it to the hole in the wall
```

### [45] hash=`92b63ed6aeb929d6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
It does come from this caveand it has something to do with the arcanum-related materials on that celestial bodyजामगते इसका पढ़ाइर पर पढ़ाइर्गा पर्भे है।यह आपच़िएन करता हैं।और यह सिथकवाजा पढ़ाइर्गा पर भालता है सब, और इसे लिए है।यह इश्यपता कुछ की आप करता है!यह सुद।मुला, बशुन कैसिया, कौटापा हूँ के लाएकी भी प्रिस्सार्वाथ काता है।घिसट्रम् पड़ाइना चीवल का की लिए उनकारिंड हा आते आप की प्रिशिया और विश्या नहीं लिए भी नहीं यारा अंदिता।
```

### [46] hash=`597c30a848bcb766`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
हमसे पूछ्ट करणा पार्थ करना देखने कि, आप गुद सब भासकीना था गबारा इसचाए तो अवसान की ऊरणे के लागनीना पती नहीं का गळपता।let alone arcanist as extraordinary as i ammaa sarasati ka vardhan hainhow fortunate the foundation has been to have such an excellent subordinate like i amI hereby apply for assistance to the foundation as a Astronomy Professor and an Arcanistyesi skala bahunarather than find kumara and the manis
```

### [47] hash=`c19485bf5ec90a27`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
we have something more important to do nowsomething more importantWe need the foundation's assistance to evacuate the villagers and turistsMourpunk village soon as possible because the near or it AstroIt's not an asteroid that celestial body we study not able to be observed by human technologyIt's approaching this village at a danger speed which reaches level 5 on turin scale and0.01 on Palermo scale.
```

### [48] hash=`1f764be33e5e8aae`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
What?In brief, the meteor shower that is occurring during Deepa festival willमें और बहुए शिन्ट करें पाई।हमें आज़िगार करने के शुरॉधार अपते एंट्राण रहा हैं।तो उडिiał के च्णडिगर्जा का षुर्षतिक्षा!नहीं, इस्ट्रिक्षिंवीं भसदारित भाल भारता आप था!था में आपकरिब सीवलितभा करें!If the foundation offers its assistance, I will provide any support when needed.This is her real?Yes.In this case, what happened in the caves was probably nothing more than an experiment.
```

### [49] hash=`d9da901f302f7697`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
I am not sure why she is doing this, but I won't allow such an abuse of our hard work.It is our work after all.That's why I must stop the star from falling.Did you guys hear anything?यह अपतकी खराब, सबसे खराब परीकता है!यहाँ कोई खजाने नहीं है, और अप तो यहां चडाने भी निचे गे रही है!मुझे, मुझे वापस चाना है, मुझे दावनी देनी है!मैं थक गई हूं!कंजिरा!मिस्च शर्जा!यूंग मीजा!सबारी तो आप पलनी देखा ने लिए तो ले चारते हैं?
```

### [50] hash=`22fc87400136f3ea`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
आप अपने यादरोज्ञारज्ञार देखा देखा?यह वाादा देखा नेए नहीं थेट्रेन और अच्छाने करें और अच्छाने देखा देखा ने लिएइंटीकू, मैं लिए पास्ताटूटरा रूबा हुआनि तुम्हाय।नहीं!इसे तूम्हाँ लिए ट्रूपत्त के लिए खुर था.आए बिडू। क्या पर लिए आप लगतू आप?मैं व्रूद पहली नहीं बाता है देख्रूँ.तो भीकर्ष़स्यषण भामाच्ट होते है।तो बात की पढ़ा हुआँ जावा खुद कर सकते होंगा।हम अलमच के कुई कवार्ज़ाज से भीतम आपना क्या रहे हैंऔर कि समुझा वह ऋटा नियता रहे है।
```

### [51] hash=`a1fbcfa8392ad0a9`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
इस पर बारी ऩुर का लगता है।पursday let's find my clever evil sister so that our astronomer friend can figure out a way tostop the meteor?Or spread the word and tell everyone to take the earliest train and leave the impactarea.It's hard to be optimistic given the situation, but atleast there is something we can doto reduce the damage.But if we continue to sit around waiting, the situation will only worsen.
```

### [52] hash=`b1951c11ab7441c5`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
Come, let's think.अह, उन्हाразу बेरूलन जस्टनाшиб की नहीं क anticip कर सकता हैं।आपका ब Nina, इस खर्त्रता आवा है।अह, इन्हां्ता उ hullly अर्ड развит के पहर हैं।मेरा क्यू जुस्ते शुश्ट भात के सुभे हैं।चाहिए अरूजा।आप पिड़ाफर्या के लिए गुज़्े?मैं आप एजा मसत्प्रण्रोड़ें की लिएगाब?तो मैं आपने अपने सेयमा यारिवाब हो दिखाए चई?हे!वंधिल्ड!प्राम्वा ख्रीएट्स, शिवा इक्ष्टरमिनात्ट्स, और विश्नु पढ़ लिए बालंज़ विश्नु उन्गे आप रख्णा कर लेता था तरहा।
```

### [53] hash=`dde5131d9453dbe1`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
क्या तो शक्रिपा अपना होता। यह लिए अपना खोशे के लिए ईर बॉरूरा सकता।तो सवा गूआइजंव्ल अपने लिए आउनिम करे।यह बैस कहती खाँभारवा जासन स्विटियाजंगि पर बिडा हो ऐसी चाप चापचा श्गाmb ते चापचाड़।In fact, there is a connection between them and they can support each other.If Arcanists and humans could get along, I suppose the world would have developed faster than it does nowIt's not easy to explain it through, but in short, there is another universe in the shape of an egg affecting reality
```

### [54] hash=`c7171b5b06717987`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
We call it the meditator's realm.Just like our daily dreams, you can enter it once you fall asleepआंचवाविगारोंस हैं आगर ट्र।और हमांस कर रूम्सित लिए जशान।काम भी धॆर खान्iędzy एक गही स्टा इस है metsha definite aawar khanna ladies aawar khanna ladies aawar khanna ladies aawar khannaलिंट्मा लिंereiम लिंट्मा्स्टो außer mealtos are the undenied fears of the dead,वह पयथागुट पाक्या पाते हैं क्योंगळ्य सर्वा है।
```

### [55] hash=`bd2adeb7169c46d8`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
जब टिद्षी मित्टृजी कर रहे हैं टिद्षी कहाँ खी रूसटाइटा है।आथ्टै चीटा कधा मैं घोटाती खेल कर रहें।और वह आथ्टैति कर रहे हैं ज़ाए त्हाँ।अर्केनम् च्टिमान्टीगार्षाहाँ के अनिदा काएए वसी पाइस।आपको तौवान करता है, वो पता है.अपनावा का नदरा पूड़ास्रे का विटहाँ है.अपने विन्ध बाच और उण करता है, वीन्द की कुना है।अच्छर शर्र। यह पर आप आपके निम्मियरा पर ग्रीमं लिए रूप आपको लिए तर्टिशाइचा था।मुझे आपको ये झूमृसे के पार मृई जज यह पक्रेदाए यह भार्भाव्वदा लिए नहीं रिए पार बरावावादे यह प्राव।
```

### [56] hash=`c6e7ba3b126fac23`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
Felt she is a distant relative I don't know of.After all, it's rare to meet someone so clever and open-minded in this villageI even lent this room to herThis was my secret basement, you know.But, only after we parted did my father tell me that she is my sisterthe daughter they sent away for lack of Arcanum TalentI do remember those days roughlyBack then, I couldn't find her in the institutionजाता हुति पाँणुच प्राटिए है.
```

### [57] hash=`e0fd701648d36e9f`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
एक सब एक लिए में नहीं खुडके लिए चटिएना बाला खुडके रहाँ हमारे.किसा एक स्टाना बिक पाँणा लिए पाइए लिए लिए कर सकता है।हाँ लोग अगर प्रप में खीएज र्भात है.तो लग्या से लिए चारूपहता को ज़रून है।तो तोड़े, अपने चार्पपियद ना अभी लिए अंवर्सट्रा कहना थे।आप आप लिए याओगादाना प्रिवाब हुआ पोलिए आप पर लिए पर लिए आप के लिए नुट्रून का लिए।वेनदिकते कुमार के कृंदड्या है प्रीताइज दिंदिटेहमानी कह взять एक तुम ब्राहूल है।
```

### [58] hash=`2245c1af836dd8ee`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
लेत वो पूर्व के पहल बिना की पार्था पूरूत हैवागर अन भी हाँ भी तो चुप रहा हैं।तो जब चिकज़े यहमार्फ का बी तामाना है क्रिभा।अज्धा कि अन्हें समझ इक्षानी भालिक्षाना हैं लिता या तामाना से भालिक्षाना लिए तो परादिता था।भी क्या क �न याबाद पर अर्टसान कर है, क्टि यह was and I,बेटरा क्या ईटेक और क्ये पता कर रहे था?तो आप अपने अच्छाति के लिए था, में साथी लिए देख़ा पहला बुत है.सवलिए बश्रे चाह था, आप फोठोमा और था?
```

### [59] hash=`376517f951d61b9c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
ईक एक लिए भी भाव्ता कह रहे हैं?Parce je DAMShwetja ...It's not I don't want to talk to my father now.You have come to me I dont know so many times.Father has already scolded me several time for letting Gena learn all those unorthodox stuff from youYou know those human booksYou can see even Gena's mother has no help in the kitchen nowI even have to prepare the candles for Deepak festival myselfतुम किस से बात कर रहे हैं। तुम तुम फिर से।
```

### [60] hash=`7b2d51599986353f`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
देखिये, क्रिप्या मेरी बात मानिये, ये आप अथस्तिति है।पूरी बात समझने का वक नहीं है।बस इतना समझा लिजी, कि ये सारा गाउ उल्कापन से तहस नहस हो जाएगा।आप और आपकी परीवार कुछ तरन्त यहां से चले जाना चाहिएं।बस, पहुत होचुकी ये बाते।हम जानगे है तम्हारी योजना।हमें यहां से निकालना चाहते हो, कभी नहीं।नहीं पिताजी, आप जानते हैं कि शर्जा हमेशा।मैं से बात कर रहूं। चले जाओ। वण्ना।आप हिम।तुम कोर हो पागल। अर इन्सानों के डाल में क्या कर रहे हो।
```

### [61] hash=`077d011ac6d1ad2a`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
तंजिना।और किस की सहायता करूं। तुमहारी ऐह्सान परामोष बुध्धे।तुम।किठी बार शर्जाने तुमहारी सहायता करी हैऔर जिना को नाजाने किठी बाते सिकाई हैंतुम लोगों ने सिलप उसके साथ बौरा बरताव किया हैबस बाते करते रहते हो आर्केनिस्त और अंसानों के बारे मेंरहो यहीं अगर रहना हैं तोशर्जात तुम सब को बचाने की कोशिश कर रही है पर कोई सुनना नहीं चाता गिरने दो उल्का पिंट को ताकि तुम सम कुछल जाओ उसके नीचेमुझे माफ कर दो ये तोकंजिरा स्टाप टोंट बॉल मी ये हाथ
```

### [62] hash=`bf916ad8934d9b5f`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
You have made me mean to you and bullying you!Why you must look for trouble?Kanjira!After all the things you do for themhow can they treat you like that?Just leave them alone!Come with me!I still have your spot on my caravan!The time for entering and exiting the trains at the station is the same every day!I remember it felt!There will be a train leaving here soon!There is still time!Kanjira!Take a deep breath and listen to me!
```

### [63] hash=`8cc9b4e2f0b9117e`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
You know you said all those things to them for me!And I appreciate that.But think about it.If I treat them just the same waythey treated me.Just stand by and watch them head to death.Even if I am doing thisout of understandable fury.How would it make me any different to them?Volunteering to help youand in your opinionrisking my life to save them.They are all out of my own will.Hatred doesn't end itself, Kanjira.
```

### [64] hash=`c16f4314fbb86e96`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
It has to beSo meYouand Ajadis the sameKanjiraDon't cry KanjiraSo you'vE been thinkLittle oneYou'Re just like usWe are your familyYou don't understand BisharjaEnough talkMay be I don't understand any of your lecturesBut you can't stay hereSorry KanjiraI have to admit they are unreasonable.But as I said, we should put that aside now.It's a matter of life, Kanjira.I can't.You are not listening to me at all.
```

### [65] hash=`25af674dc2b485e2`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
Be a saviour and go.We live here on our own.Kanjira.But then you submit to me.हा है साब.इतना सनाता क्यो है यहां?बहर को तो बहुत भीर थी.इतना सारा.यहाँ सुरक्षत है। यहाँ जाओ।मेरी तो जान ही नितल गई थी।शुकर है तुम थीख हो। क्या हुआ यहां?पता नहीं कुछ भयानक से लोब अच्छानक आ गए।उन्होंने जहरों पे मखुर्टे लगा रखे थे।वहाँ उस प्लाट्फॉम पर कुछ और लोग है।बता नहीं कहां से आथब के और यात्रियों पर बिरा मद्लब के हम्ला करने लगे।
```

### [66] hash=`ba1411c5e08e1d4e`

- lang：`other`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p27`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜5~7）

```text
शुकर है कि सारी यात्रियों यहां से जा चुके थे।मिश्र जाक की वजह से बच गये।हम पीचे रहे के तुम्हारा इत्तिसार कर रहे थेतुम अकेले आयो, मिश्र जाक कहा हैशान्त वो लोग आरहे हैतुम्हे देखना लेताथ तेनी मेरी चणिकीसही में इन सभ जीजों के तुम्हे इस बक कोई ज़रूरत हैइस प्लेस्रीश नगी एक बाध हो नहीं यहाँ होगा।यह मैं एक प्लेस्रीस नहीं यह विए जाज़े गलभ है।तो लिए पार्ते पर अधिर रहें।इस था दिवाश्त करie��ा।
```

### [67] hash=`18b19282f83eab51`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
I was always, for most of the time, the best student in first aid class.The pain is gone, yeah?Not bad.Dealing!Chai's!Hmm, I didn't expect to see this.What a spacious yard for a house located right next to the train station.Old buddy, I'm surprised that you're still here.We have settled everyone so far.I didn't expect so many men as members here.I've never encountered them before.They can't be communicated with.
```

### [68] hash=`7b15f7bf9b4416fa`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
How horrible.And since we meet them here, it means...I did cooperate with the menace.It's completely out of control.The incantation in the cave.She must be able to detect the fluctuation caused by it, and that gave us away.But what in the world is her purpose?Did she think I would stop her?So she deployed these...things to slaughter the village.Does revenge matter that much to her?I trusted her, I never believed she would do such a thing even if we're no longer on the same path.
```

### [69] hash=`7ba5cc60a7e79ce0`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
But the reality tells me, my trust in her is nothing but a joke.Hatred changes people.It's not a choice, Calabona.You don't have to feel bad for trusting people.You trust someone because they're trustworthy, but you never need a reason to hate.Let your guard down for even one second.The toxic idea will sneak into your mind, and it would be impossible to get rid of it.It will burn your mind and sanity until you become an animal living for revenge.
```

### [70] hash=`bcab67014d753fdd`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Even forget your own name.Oh, don't look at me like that.It's nothing personal.In my mind, she is still my cool and scholarly sister.I was young and easily fooled back then.What I said was based on my real-life experience.I was way more outrageous than her.I mean, we were all young once, right?No matter what, she's already on the move.But we don't even know where she is.Think about it.The-But Sharjah's still out there.
```

### [71] hash=`1752bce2fbb066b4`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
She can't use any arcane skills.If she's fine by the mask monster?SPF-1 portable contact device activated.Abnormal arcane skill fluctuation detected.Conducting analysis.It's itself?Source of abnormal arcane skill fluctuation confirmed.Similar faction, Manus findictae.Margin of error, 0.121%.Emergency support application sent.Adjusted support application priority to high.Does it mean we can ask the Foundation for backup now?
```

### [72] hash=`4011d56aa0950bc6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Yeah, that's good news.But the Manus are still wandering out there.Before the Foundation evacuates them, the village will be destroyed.We can't just sit around and watch.There is another way.What way?If she can do it, I can do it too.Maybe I can find traces of her if I enter the realm, because I also mastered meditationskills.Yes, that's right, I know the path inside.What do I need?yes water enough water to soak me in now hold on please wait if it was so
```

### [73] hash=`219efbcef79c51a8`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
easy and why didn't you look for her in the realm in the first place I it is arisky move am I right how did you know oh just my instincts or experiencesperhaps what fence but when I look at you I see a desperate tiger cub corneredthe Hunters.The situation is not as simple as you think.Since she can invite us to more punk,she can play the same trick and invite you to her realm.This could be a trap.
```

### [74] hash=`dee73833ff42b723`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
A trap to keep youstuck inside the realm.You are right.It is a risky move.With the other two idols as her anchors,she's the true dominator of the realm now.I can't foresee what's ahead of us in there,So I've been avoiding it.We don't have other choices, do we?Now we are talking.You seem ready.But...Whatever you decide to do next, don't.This is the advice from an experienced hunter.Because whatever is in your mind now is going to send you into the hunter's trap.
```

### [75] hash=`3230b088dbd0de63`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
This happens to all kinds of animals.When the animal realizes it is cornered,its mind will be in a muddle.It can't think of anything else, but at the same time,it strangely grows overconfident.It will take the gamble of escaping from its last way out,which is also going to be the entrance of the trap.Trust me, I know how you feel.You thought there's no way out, but a footlogged bridge.The Manus followers are still wandering about, and some villagers haven't been
```

### [76] hash=`2e7a1e91592c78bb`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
to safer locations, but sometimes we must take the risky path to get out of the dreadful situation.Even though it is full of traps, it may not solve all the problems, but it's better than doingnothing.If this really is a trap, that means we will meet again.And I have been waiting fora chance to talk to her face to face for too long.I have been chasing after an imaginarygoal since she left me.I watched that star closely, taking down everything that I could
```

### [77] hash=`51c65db5fb5e3ffb`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
observe.However, despite all the efforts, deep down I know better than anyone else,it's useless.I remember those days, almost half of which were like living in a mist.But now, but now, I can feel it.Her silhouette is right there in front of me.To be honest,This is not the best time to seize this chance.No matter how I look at it, this is too good an opportunity to pass up.Okay, fine.If you insist on doing this, I will not stop you.
```

### [78] hash=`159d3bfb3631067c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
We all have our lessons to learn, and you are right, we don't have any better options.What is it they say?No risk, no feast, huh?But please keep this in mind.No matter what happens, your safety will always be the top priority.We cannot bear to lose someone who is capable of putting this to an end.I will.Are you sure?To use this?What's wrong with it?It has enough water to soak me in.You are much more practical than I thought.
```

### [79] hash=`11d65539004cb9c0`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Before I go...Are you going to take it with you, Miss Kahalabauna?similar to some of the crystal divination theories.So perhaps this will help you in the waterif the crystal can stabilize the magnetic fieldand guide you in there.You need to be surprised.This is how quickly a genius can think.Thank you.Ah, great.So it's only me who can't understandthis meditation in water thing?Well, it takes all sorts of rocks to form a mountain.
```

### [80] hash=`b32c5a6262f1b5d2`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
The pendulum and enough liquid.And all I have to do now isbe the first man to recreate the observatory in the realm.Just an illusion in my mind.You remembered almost every detail of me as a child.Did it hurt that I hit someone as a child?You should not be here!You taught me a few moves to deal with those brats at that age.This feels weird.Did Kumar put you here?To guard this fragment of memoryThis shall be the obstacle in my way
```

### [81] hash=`432ab4028ee4c029`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
To where I want to beAnd to face the illusion from the pastFor your seat to the seniorWhat are you doing here?Go away!I was small and weak in my 12 year old roomBut I never had any problem in hitting the spotBut why?Why you?You want to talk to me?You've grown taller and you have stronger hands, like I've dreamt of.So have you two found the graveyard of stars?How dare you!But look on here.That'd still be me.
```

### [82] hash=`da894121300e6e93`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Which is also you.We're 16 and the bad kids sitting behind us cut our hair.Leave now.Kala Bhavna.The thing you are clinging on to.Facing and chasing.Think what it is.Still asking questions that cannot be answered.Just as you always did.What do you think I should chase after?This time, I won't be deceived, Kumar.Since that day, I have never stopped studying science.20-year-old me was fierce.You'll trail.
```

### [83] hash=`1c02ca84ebf65bfc`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
You came here sooner than I expected, Kala Poonam.Knew you would come.See you again.I miss you dearly too, my child.I hope you've been doing well while I was away.Hope you're happy with the surroundings I set.I always find it enjoyable here.A place full of memories.And perfect for small talks.I'd rather you suffered, miss.Someone is having a worse attitude these days.There's no need to look around, kid.
```

### [84] hash=`c7090689c7fe0681`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
I already had a few years of experience in the field before you started your research.And one of the most basic skills one has to master in the meditator's realm is to coverup the traces of reality.Even so, you didn't even think about creating a starry sky for yourself here.That would be unnecessary.You can see it any time outside this realm if you like.Why did you invite me here?I know you've put in a lot of efforts.
```

### [85] hash=`85d7b48eb61011fc`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
I understand the difficulty within, and sympathize you, Kalapauuna.I always do.Just like what I did with my younger brother.By the way, that letter has been delivered to him safely, I assume?You're smart enough not to bring the fish new statue with you.Did somebody kindly remind you not to do that?Never mind, that's not helpful.I don't understand.Why involve him?Maybe I was being vindictive out of hatred, like you said.
```

### [86] hash=`973e6c41306aba82`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
After all,they precluded me from doing anything even before I give it a try.Although my misfortune was notmy brother's doing, there's no one else left in the family to take my anger.So ask me now.Ask me anything you wish to know.I can tell you everything.What you're curious about,what you're confused about, anything you can't work out in your little brain.I can explain it all.Hasn't the idea that I might locate you bothered you for even a second?
```

### [87] hash=`a5d0e0973d3c267e`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Locate me?You are still as naive as a child, my Kalabauna.You little dummy, Ulu.That is simply impossible.This is the first time you doubt my capability.Why would I do that?Of all the students, you are the only child who is smart enough to follow my steps this far.You just don't have time on your side and need a better mindset in dealing with the unexpected.I've tried to teach it to you.Remember those impromptu speeches I asked you to give?
```

### [88] hash=`7abdb742a5bc84f8`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Those were good practice.Don't have?What do you mean?Perhaps you have put too much stock in the idea that I will rely on Manus Vindicte in this.Instead, I trust myself more than them.And of course, I also trust you.What's more, they were never good enough for me.But luckily, I have never been a real Arcanist or a real human,only pretending to be either of them when necessary.I can easily act like an alcanist to gain their trust, just like I could act like a
```

### [89] hash=`0599286f125ad64f`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
human when I was teaching at Bana.What are you staring at?Take it if you're interested.You thought it is the key to cracking the meditator's realm, like the stone statuesearlier?Though it is too late for hints, there is one thing I have to remind you of.You didn't catch up to the real me, nor did you improve the situation by enteringthe realm.You chased me all the way here.Chased the orb of winning against me.
```

### [90] hash=`1edbb4d28aac5e32`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Butyou only helped me complete my plan.The moment you entered the realm, the last stepof my plan was done.Completed.As you know, exerting influence on reality through the meditator's realm is challenging.after all this realm is like the shadow of its real counterpart a reflection ofreality I went to a lot of trouble even wasted a statue to finally stick out acorner of the shadow over the boundary of the two worlds you mean the statue
```

### [91] hash=`a0bacc91a02be06f`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
in the cave yes what I needed was an outside in force to break the realmwhich is almost unbreakable from the inside.A mirror can reflect objects, but there's nothing it can do to itself.It can only be shattered into pieces by people not from the reflection, but reality.Whenever there is a shooting star streaking across the sky of this realm,An equally beautiful star will fall on the real earth and guess what?
```

### [92] hash=`65fd9130ab1de11b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
You are the force I'm looking forNo, how?So the fluctuation I detected the energy of the celestial body felt by the foundation girlJust false alert.Oh, no, I have to admit that young girl was not part of my planBut, at least you are on the right track about what happened.If anything is to blame, it's your ego.You were trying to win, but not by saving people.The idea of proving yourself to me outwaved their lives.
```

### [93] hash=`4c645148a95c039b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
You must be wondering, how could she lay such a trap with her insignificant arcanepower?She can barely lift a lump of clay.She must have had the Manus Vindicte on her side to help.All that being said, you don't have to feel yourself to be a lesser version of me.You're still my best student, my best colleague, and my strongest rival.Well, with some room to improve.Even this time you didn't lose the game for lack of wits, but for the fact that
```

### [94] hash=`1933f472fa9ba8e5`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
I know you a bit better than you know me.And I simply have more experience hunting a prey.You and the madness have never, never thought that.If I didn't enter the realm to see you...Then things are going to be tricky for me.You would be enjoying a happy deeper festival,while I would be crying in a dark corner nobody knows of.Why would you?Well, time's up.Remember to ask the most important question first next time, chat.
```

