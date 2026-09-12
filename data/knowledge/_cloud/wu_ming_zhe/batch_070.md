# 剧情图谱抽取 · batch 070

- 角色：`wu_ming_zhe`
- 批次：**70** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.2」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_070.jsonl`

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

### [0] hash=`4cb626279fc141c6`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
That was a night in 1971.A night with pouring rain.In that rain, the communication center of Zeno lost contact with the Green Lake campsite.Wasn't it a story?I am kind of attracted indeed.It is really not a wise choice for you.It's our rights to stay here.You can't just expel us.Someone is passing messages to us through these notes.We have been with a butcher whose identity is unknown to all of us.
```

### [1] hash=`893cb45cd2b21453`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Like the story of Zeno Youth Force.We are in real danger now.The creatures are multiplying.Things are getting worse.It seems this is the entrance.Green Lake can't say!We are now at the...Green Lake!Michael, a self-explanatory fool.He leads the life of a clown in front of his popular peers,like a companion animal to them.He has turned himself into one of thosechattering, gong-holding monkeys.clowning around with a head filled with junk food, alcohol, and psychedelic potions.
```

### [2] hash=`f0bcb73fa85ae17d`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Green Lake Campsite.I hope we can find a clean and vast lake here to swim, with or without a swimsuit.See my muscles?The young ladies will all crazily scream for these puppies.Ho, ho, ho!Ugh.Freddy, an athlete, captain of the school's rugby team, an ostentatious, self-centered, and annoying narcissist.He is in the prime of his life, a period which will be recalled repeatedly and eagerly decades later, like a drunk man obsessively licking the salt off the snacks.
```

### [3] hash=`560306f6b1caab60`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Damn, Freddie.For one second in your life, could you please stop thinking about taking your pants off?Jason, the young scholar, he is the teacher's favorite student, straight A's, clever, reliable, and logical.He pays more respect to girls than most of the idiotic men do.His interest is reading those encyclopedias or looking into some strange science stuff.You can wipe your face with this, Michael.
```

### [4] hash=`9d50c25d530595d8`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
We will get to the camp soon.Anne, the Virgin.There is a non-aggressive, harmless amount of gentleness and beauty in her that youdon't get to see much of in this crazy time.She was born and raised in a faithful Christian family, along with other sisters.She attends the reading session held in her community every weekend.Ugh, lower your voices.Enough shouting.Ugh, I'm still hungover so don't mess with me and everybody will stay happy.
```

### [5] hash=`0054dc6693fb6d46`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Understand?Blondie.Reckless and dumb.A typical blondie.Always indulging herself in alcohol, beautiful clothes, and other vain pleasures.To me.You can choose from the rest.Michael will be glad to help you, sweetie.Take Anne with you.A girl would know to attend to details.One day she will pay for her doings.One day.They were all...Their heads were hung at the treetop.It was until a week later were they found by other campers.
```

### [6] hash=`310d38a9c32752ed`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Murderer?No, there was no murderer.At least nobody has ever seen one.Some said it was done by a person who has long lost his humanity.That he was possessed by some demonic spirits and therefore immortal.Michael, you fool!Stop telling such a dumb story!Come maintain the bonfire, idiot!I finished the store on my way!Hey, do you guys smell anything?Something quite gross, like, uh, putrid?Holy motherfucking God!
```

### [7] hash=`ebbe4827cb331e15`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Oh, oh gosh, I just saw it!It's Viscera?!Gah!WRAAAH!Please, F you!Don't throw up on me, Michael, you damn jerk!Ugh!Step back.This is a badger.Judging from the degree of putrification, it has died at least a week ago.Blonnie, did your uncle mention any beasts living in the woods?Blonnie?Blon- Oh my goodness.They sneaked away again!In this very moment!Well, I think so.She left with Freddy when Michael started puking.
```

### [8] hash=`c3e788fb6d6ebb55`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Naughty!Stop that!Haha, yeah.I can push this further.You see, I will.Timekeeper, now that we have given the report, Madam Z said we won't have any other assignments for a while.It may be a little abrupt to ask, but I was wondering if you would like to take a heritagetrain ride with me?Please, trust me.This journey will be the best ever.Let's start off immediately and come back furtively so nobody will know.
```

### [9] hash=`d323767720c8df1a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
No, thank you.I'm not interested.Okay, fine.Wait, Angie, do you want to travel?Let's start off immediately and come back furtively so nobody will know.I'm flattered, you ask, but I'm leaving for assignment soon, so I'm not goingDeducting by the logic, we might be drowning in the latter one.We just made a joke.I don't find it funny, but considering I have an odd sense of humor, I can politely laugh at your joke.
```

### [10] hash=`309c5ae390f4107e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Like this!This is super awkward.Don't worry, Timekeeper.Although his manner is debatable, he is not a bad person.He was the one who received the Outstanding Contribution Award in the latest annual appraisal.Allow me to introduce...No, wait!Don't use that name.Here with Timekeeper, just call me Horipedia, which I prefer.Okay, Mr.Horipedia.I've never heard of this nickname of yours.It's a long story.
```

### [11] hash=`497bdf163a311771`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I can share with you at another time.Now, let's get down to business.Have you guys heard of the myth of the Green Campsite?Yeah, it was me.Given that you didn't know me, I sent it anonymously.I don't see how these are correlated.Well, of course they are.An anonymous envelope better triggers curiosity.And you are the most inquisitive person I know.Didn't you worry that I might throw it away?Honestly, I did.
```

### [12] hash=`9cfc92e23d6cb7f1`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
So I wrote to another 13 people.Now I have six maps.Don't be upset.Yours is the most intact one, so I selected it.Thank you for your approval.A mystery solved.No wonder I found the handwriting on the envelope familiar.I did some research on Green Lake Campsite after piecing together the map.It was the map of one of the training bases of Xeno.They used to train their youth force there in the early 60s,
```

### [13] hash=`e5cca4eafabc37ee`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
and deserted that base in the early 70s.It had been underused even before it was abandoned.It was more of a Boy Scout camping site than a military training base.Exactly, Ms.Saneto, but this is the outdated version of the story now.This is not your fault.You haven't been in the headquarters for a long time, so you must have missed out onsome first-hand information.Now, about the Green Lake campsite, we have some updates.
```

### [14] hash=`2f78c460f84312bb`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
That was a night in 1971, a night with pouring rain.Heavily and hastily, sheets of rain formed a barrier, isolating the woods from theworld.In that rain, the communication center of Zeno lost contact with theGreen Lake campsite.Was it normal rain?It was.Drops of water with dust fallingfrom above.It didn't cause any illusions or unusual symptoms, but tookaway all the youth force stationed at the campsite.
```

### [15] hash=`82361e6b84e60a65`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
In the cabin they lived.People found clothes, blankets, even books left open on the table.What doesmove or breathe stayed there as usual.But their owners, those living youngsters,disappeared from the woods like drops of dew under the sun.Since then, nobody hasever seen those youth force again.Xeno has not, nor Laplace, nor us.Green Lakecampsite has then become a ghastly and deserted land.Ms.Sinetto, please put down your hands.
```

### [16] hash=`c549ffd2aa4a13f7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
They're hindering your ears fromNo one knew which rainforest they referred to the personality of all those kids have changedThe outgoing Bruno became speechless the gentle Anna Queenie starts picking quarrels with othersThey were not who they were but no one could pin down the differenceDay after day the smell of fungi and moist soil never disappeared.It lingered for one weektwo weeksthree weeksTill one night, grade one student Drea suddenly woke up from his dream.
```

### [17] hash=`a8459ec1e7aa8f12`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
A muddy tentacle stretching out beneath his bed closed around his ankle and pulled himonto the floor!There, a face awaited him, a hideous face of a human-like creature with a BLOODY MOUTH!Senato?Senato, easy.You were going to break your wand.I was just a bit caught off guard.It has never come to my mind that such a bizarre event would take place withinwere less combat experience and capability compared to those graduates.
```

### [18] hash=`a7ca1010c84a0447`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Still, they have received years of training as reserve soldiers.As we all know, Xeno would arm their youth force and the trainers with drill weapons for outings.It was nearly impossible to wipe out a youth force in the territory of Xeno without being noticed by the academy.It's not true, just a made-up story.Tooth Fairy, did you come back from the trip?I've rerouted my journey to a new destination.
```

### [19] hash=`6f8d97fda146ace8`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
My companions suggested us to meet at the foundation first, so I came back earlier.Anything wrong with the original destination?It's fine and safe, but now I have a better place to go.It's a place of myths and danger.There once lived many adolescents.With any luck,I will embrace a harvest of baby tea.No way.The place you're heading is...It's Green Lake campsite.Wasn't it a story?A story made up by Mr.
```

### [20] hash=`c922dfe820b89ba5`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Horipedia?He made a part of it, such as the bloody hands underneath the bed and the midnight screaming.Except for those, the rest is exactly the same as I know.As you just said, in their own training base, impossible for the youth force to be...It proves that Green Lake Campsite is out of this world, a place worth visiting.You're three minutes and fifteen seconds late, Miss Tooth Fairy.No worries, I didn't waste my time waiting.
```

### [21] hash=`528117905a9baff2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
We need more people to join us.Angie and Adolf have turned me down, but Verdin and Saneto haven't walked away yet.I am trying to win them over.I think I'm almost there.Now, they are really attracted by the Green Lake, so we are starting off soon.Attracted?Pardon me, J- Mr.Horipedia.We did not plan to go there, and we certainly do not feel any strong attraction to that place.Oh, really?But Verdin seems to be very attracted.
```

### [22] hash=`5e5cf9de9aa352aa`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Or am I mistaken about the look on her face?Timekeeper!I am kind of attracted indeed.See that?I am right.I'm glad to see you in an adventurous spirit, Miss Burton.Great!Take your suitcase, pack your clothes, don't forget to bring two novels to kill time.Now let's take the hands of our two new partners.Journey on!Thank you for the letter, Emily.Now we are bringing our driver friends the latest weather forecast.
```

### [23] hash=`e0c193670bb7bdbb`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Ohio is having a sunny week, with a comfortable level of humidity, and zero chance of rain.Sorry, I forgot to switch off the in-built radio.Sit tight and put on your safe belt, hold the hands of people sitting next to you.If necessary, close your mouth, then clench your teeth.You can do as I said, or not.I was mainly talking to them.Yes, madam?Yes, Ms.Tooth Fairy.Are those little winged elves still nagging you?
```

### [24] hash=`7359290a7f53affc`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I remember you were troubled by them as early as I was in school.They are still there.They have never left there.The good thing is that they can't distinguish lies.They spend every second of their life overhearing me and totally believe what I say.As long as they hear me say,cover your mouth and clench your teeth.They will never attack you.We all owe Mr.Campbell a big thank you for this.All of his teeth were stolen when he was with Miss Tooth Fairy.
```

### [25] hash=`f3172b045123f14c`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
That's when humans finally realized how vindictive and vengeful those little things are.They stepped across the world for the cure.Eventually, they found a solution.Mr.Campbell?Who is this person?And what happened to him?He is my brother.I am also a Campbell.Miss Campbell.While he is a mister.We shared a roof when we were little.I was cursed for eating a tooth fairy.It and its fellows swore to steal all my teeth.
```

### [26] hash=`9dc1fdebbad40917`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
At first, they did it.I ate nine fairies and lost eleven baby teeth.My parents soon found out.They ordered a special toothpaste for me, in case I lose all my baby teeth and becomea horrific old lady.In their second attack, those tooth fairies failed to steal the teeth from Miss Campbell,so they rushed to Mr.Campbell.His teeth disappeared in a flash, and he never had one since then.People said it was the curse of the Tooth Fairy.
```

### [27] hash=`b4c2f1461f98dcfa`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Just like in books, the flying human-like critters are bigoted.Once gained, they will keep the love and hatred at heart forever.I'm so sorry, Ms.Tooth Fairy.I shouldn't have asked.Don't worry, sweetie.My brother now has his own teeth.He lives a stable life.The past is in the past.And I don't really think he was cursed.I've never heard the tooth fairy swore at him, neither have I found any mark on him
```

### [28] hash=`53251045e73865b6`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
that can be detected by Arcanum.Instead of being cursed, what he suffered is more likely to be a congenitally missingtooth, a term defined in human medical science.I know that case, I just never thought Mr.Campbell lost his because of this.None of my classmates or instructors ever doubted the authenticity of such a curse when they gossip of such things.SPDM is a community of a bunch of young arcaneists and several instructors.
```

### [29] hash=`f4b38e39a24ff034`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
For those kids, a curse is more common than a disease diagnosed by human medical science.As a result, they neglected what they can't comprehend and only learned the story from a one-sided perspective.Soon enough, rumors started to spread.But that was a curse, a trouble that you can't easily shake off once you were put under.People could hardly forget that.If Toothpherys could curse his sister, they could also curse him.
```

### [30] hash=`9e25c1934d0ed09a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Everything came naturally, that was it.Kids were ignorant for lack of knowledge, yet adults were ignorant for their cognitiveinertia.In a story where truth and falsity are mingled together, it is hard to tell whichI heard it!I've...I've heard the God's will!Oh, God...I will guide your children...I will guide them...Guide them away from the demons...From the land of demons!Dilated pupils, disordered speech, and a body temperature of 3 degrees higher than the normal level.
```

### [31] hash=`d956e1cc3f80afd9`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Iron buckets, felling axes, picnic mats.Here we are in a campsite.It is only normal to expect these tools to be here.What is this?Anything?Have you found anything, Senedo?Something is buried in the ground.Right here.A box made of iron or aluminum.It looks like...like a candy box.Tushing from the rust, it has been buried here for four to five years.A kid's candy box?If this is from a brutal crime, there might be some evidence inside.
```

### [32] hash=`3cd010ae6da3e670`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
We are all ears, Ms.Ferdin.This is not a candy box.It is a pill box.Correction.It is an empty pill box.You're back, Ms.Tooth Fairy.What did you find when you explored the campsite?Roughly the same as here.Near the woods, there's a place for firewood cutting.More traces left by critters can be found near the woods than here.I also found the teeth and claw marks of giant critter as well as some excretion.
```

### [33] hash=`be38b34332655450`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
That is to say...one gigantic critter inhabits here?If not more?Yes, that's why I came back here.Watch out for the critters.We may have stepped in their territory.I understand.I'll tell them to be careful, yes.Thank you for your advice.Bye.Angie, come in.This is the file that the timekeeper submitted.It's about the storm.Please hand it to the research department.Affirmative.I will bring it to them.
```

### [34] hash=`ffce482c5b32ee1b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Next month, your squad will be dispatched to North America to join Zeno for a joint mission.The tactical unit under the timekeeper will be replaced by the third squad.Please complete the handover procedure before you leave.By the way, your application for the outing permission has been permitted.The document will be posted to your door mailbox by 7pm tomorrow.I'm very grateful for your help, Madam Z.
```

### [35] hash=`e5453bd89b255e32`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
You're welcome.Get some good rest.Don't forget to remind your team members that actions outside areas mentioned in the application will not be allowed.They need to return back to the headquarters by the specified time and check in once they're back.I will, Madam Z.I will look after them.Off you go.He did have some past records of violation, such as being late, absent from duty, and taking actions without permission.
```

### [36] hash=`01839be602a90d9b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
His past records means that his outing application will not be permitted.He must be well aware of it.That's why he wasn't even bothered to apply for one.My, no wonder he always said, let's start off immediately and come back furtively so nobody will know!Don't be nervous.Our priority now is to get them back and minimize the possible consequences.Angie, do you know where they're going?Hello?Is it the liaison department of Xeno Armaments Academy?
```

### [37] hash=`d5707a32373533b2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I am Zee.Please put me through Lieutenant Baya.Did someone scream?My god, Jason.We have to check it out.I know they like to fool around, but we are here now.Michael, stay here and take a rest.Shhh.Don't make any noise.Alright.They will all be fine, huh?Hope so.Seek this is not funnyWaitLook over there.How was that?Those stories are all true all trueHow is that possible?It is not in compliance with the laws of?
```

### [38] hash=`1199d3f8b4481eb0`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Nature no more crying and stand up run.I will look out for you runJason the blood is all over the placeDon't think too much.Don't look back run speed upThe bushes right over there!Follow me!Let's speed up!Apologies, I didn't mean to intrude.What happened here?A crazy murderer?Student campers?This is much more interesting than I expected!Protect the victims!Get ready to fight!Who are you?And the bushes?
```

### [39] hash=`41240d30c1a5c353`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Why did you come out of the bushes?Worry not, miss.Please get behind.You're safe with us.Oh, that's my friend!And they aren't- I understand.They deserve a decent funeral.After I take care of this demonic creature, may the peace be with us.Seneta, calm down.What a d-This taste of cherry syrup is killing me!You?You're still alive?Of course.What kind of question is that?You were vomiting blood, and that gentleman over there doesn't even have a head attached to his body.
```

### [40] hash=`04b278055450db26`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
That's a prop.It looks like a real one.Nicely done.You add bloody paste substituteinto the cherry syrup, which makes it smell like the real blood.Be prudent about thedosage because it's slightly addictive.You've used too much.What on earth is happening?This is a theater, or a filming site.These young people are busy with their businesswhile we just interrupted them.I'm Anne.Are you two the actress Jennifer recruited?
```

### [41] hash=`0e8c27d50d23155e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I'm afraid I don't know this Jennifer you're referring to.My bad.She sometimes goes by the name Blonnie.It was just me who always calls her Jennifer.Fucking damn it, you idiot!There's no way we can use this take!Here she comes.Sorry, excuse me.Fartin.No, not asking!Huh?Are you asking me?I am Horipedia.And you are, hmm, the big one, the athlete, the smaller one, the fool, and the slim one, the scholar, and the only girl who's standing here, the virgin.
```

### [42] hash=`533a807ce5847255`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
It seems like the first girl who lay down.I'm talking about you, uh, ahem, right, a blondie.Who the hell you are, why you are here, and what do you break into my film site for?Film?We were in the middle of shooting a movie.A horror movie.Jennifer is our dir- dir- dir- director?And playwright.Is that the word?Horror movie?Here?Where is your gear?What's the story?What's your business here?What?Are- aren't you confident enough?
```

### [43] hash=`f7f6bf0781bd319a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
The gear is right here!In the script too!Take a good look at it, smartass!Recorder CCD TR-57, the latest version, a pretty one.It costs quite a lot and has many features.Optical camouflage outer shell, long standby time for operating independently,and hand gesture triggered flashlights and lighting adjustments.Wow, it's the first time to see a real one, other than those advertisements printed on magazines.
```

### [44] hash=`384f533da6dc22f7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
What a coincidence.How do you use the flash?With a snap, a wave, or adjusting your glasses?Or an applause!Ha ha ha ha!It's the applause!Now it's easier!Unbelievable!What the hell do you think you're doing?Piss off!5 minutes 31 seconds.The sticky bulletshould have been four times more powerful than this,but still within my estimation.Hey Blondie!Clap your hands!Damn it, for freak's sake!Look what you brought here!
```

### [45] hash=`b2037e763393f118`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Good!Now it's time!It escaped, taking myprecious collection away.Nah, there's no way to follow it.The trees that pushed down have blocked the path.Thiswould take us some time.That was definitely not your usual critter.Miss Twoferi, whatkind of traces did you find earlier?Most of them are left by medium in small critters.Claw marks of giant critters areclear but few.There's probably one critter of such a mince size.
```

### [46] hash=`7285230dd0c4be9e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Besides, we needto offer an explanation to that lady.Of course.Why are you all staring at me?Do I have something on my face or my clothes?There, there, Jennifer.I can try piecing it together and fix it for you.Would it help you to feel better?It's no use!Everything in it is gone every take I took!Yeah, like what Anne said, don't be sad.Thanks to your generosity, none of us were injured.You just say!
```

### [47] hash=`9bd466e6184a0de9`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I'm trying to comfort you.Don't glare at me.Actually, I think this is unnecessary, but they made me...behind me.The girl with the hat and the girl in the white, huh?Necessary?You think it's unnecessary?Do you have even the slightest idea of what you have destroyed?Make your four eyes useful and look at these.What do you think they are?Alright, calm down.Let's be reasonable.If you were mad because of your movie I am really sorry, but at that very moment
```

### [48] hash=`41958ad781099d96`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I thought our safety matter the most.Also, I have good news for you.Thisrecorder is meant for taking daily family videos.The clips taken by itaren't nearly enough to be called a movie.So, to some extent, I justprevented you from shooting a disastrous movie.If you are lookingfor any financial compensation, please talk to the girl with the hat.I'm not reaching over some movies.I don't care about this stupid shit at all.
```

### [49] hash=`46bd29ca6f72e576`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
You think money can get you out of trouble?It doesn't even come close!Collaboration products of Recorder and Lugas.You can only find three of these all over the world, only three!It's more valuable than any jewelry or luxury handbags!Suede decoration on it alone can buy 200 of your stupid head, dumbass!My makeup!You stinking therefore!Go clean the broken trunks and bridges off the path!We have to get back to the cabin as soon as possible.
```

### [50] hash=`191794bbbbe258c2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I have no desire to catch a cold in the rain.This is not a safe place for you.Get back to the town, find a hotel, and take a hot shower.My students and I will escort you to the main roadat the edge of the woods and arrange a car for you.If any of you have symptoms like an itchy throator rising temperature, please buy some Ropitussinor a similar drug at the nearest pharmacy.As long as you take care of that big monster,
```

### [51] hash=`20dcee8b78fca6c9`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I can continue with my projectto get that stupid shit movie done.We don't have the camera...camera...Camera, you dumb girl!You have no idea what we are doing here,so don't tell me what to do if the best you could do is handcraft some props.Staying here is really not a wise choice for you.It is very dangerous, and you can't protect yourselves.Right to stay here?You can't just expe...You are, of course, entitled the right to stay, Miss Blonnie.
```

### [52] hash=`8ea1cc1ea42cd13e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
But I hope you could keep in mind that you and your friends are in grave danger.The Green Lake campsite is not a place for fun.You should stay with us, for the sake of your safety.The rain is getting heavier, we might catch a cold.Let's clean up the road and head for the shelter.All this gibberish to scare us off.Come here, Freddie!Go into the campsite and see if you can find some axes for us.We will never do harm to any human.
```

### [53] hash=`c3555a7ba2e42f93`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
It's strictly stipulated.Save your bureaucratic rhetoric, little girl!I've read those books.I know you've done some dirty things.Tell me!Shut your face, Michael!I've recruited you to play the fool, not asking you to really be one.Don't bring disgrace on us for going to Vine State College with you.You're all students from Vine State College?Yes, faculty of soul-making.This fool here is a chemistry student.
```

### [54] hash=`310d17ddc5b46c0e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
The big guyover there is an art student on English literature and poetry.It's one of myassignments to make a movie during the semester break.So I hired everyuseless meathead available and traveled all the way to this shithole just toshoot a stupid horror movie.Stupid horror movie?I thought you loved horrormovies.Ew, don't disgust me.Who would possibly have interest in thefilled with characters in sweat and dust and presenting zero romance or any nice costumes.
```

### [55] hash=`ec67e7f2b77a9849`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
You mean you are not interested in horror movies but determined to film one here?You tell me.They are cliched, meaningless, but easy to make.They are the easiest option for this assignment.That's it.I've never liked any of them.Oh, I see.That's why you selected this awful script, all these beautiful but useless props,and such an untrained cast.What did you say?Well, I've read your script.It is illogical and dull.
```

### [56] hash=`fbd2f91a7108ea89`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
The conflicts are not strong enough.Or we can call it a classic, butin another word, it's stale.I really wonder, how did you getadmitted to the filmmaking faculty?The admission criteria for Vine State Collegeshould be quite difficult to meet.You!You're no one but aspawn of the foundation like those bodyguardsmy daddy has!Come on, relax Blonnie.If your dad didn't sponsor the two library buildings,you would not be here studying filmmaking.
```

### [57] hash=`5a7af7299db965dd`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
And you look exactly like an Arcanist when you get mad.Don't.It's not a good look.And again?Pick a punch from me?I'm not in a good mood today.I just lost a camera so you can keep on pissing me off if life is being too good for you!Whoa, whoa, whoa.Normally you wouldn't be so mad over a little joke like this.Are you making a fuss now because your arcanist friends got your back?Jason, Jennifer is trying to finish a project.
```

### [58] hash=`1b8c7bc3d2c2602a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
You shouldn't be mean to her.And Jennifer, please don't get into a fight with him.Isn't he your friend?You know friends won't say hurtful words to each other.I don't understand.Is this the way people make friends in the outside world?I'll knock off every tooth in your mouth and give them away to that crazy teeth collector!This way can your empty head remember how much I hate being called an arcanist!
```

### [59] hash=`b0edd648cc31bc71`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
But you are always an arcanist.Although you've tried every means to be a human, it won't change your identity.However much you despise us, many brilliant playwrights are arcanists.Mr.Horipedia, please stop making this worse!Quiet.If you don't shut up now, I will shut you all up forever.Miss Anne has a point.This is not how friends get along.Ladies and gentlemen, we are not here to fight.We need to cooperate.
```

### [60] hash=`f4b709cd3c83c550`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
I don't expect you to love each other, but no more fights.I don't care whether you are arcanist or human.Now sit back on the sofa, everyone.I'm sorry, Ms.Tooth Fairy.I'm sorry, too.I should have stopped them.I'm also recruited as an actress.She's not as restless, energetic as your classmates.Isn't he another actor you hired?Together with Anne in the town near the woods?No.I've never looked for any other actors.
```

### [61] hash=`3f19d5bd828957be`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
The only new actor I hired is Anne, because she looks almost like a twin to Anna, and Anna is absent because of her stomach flu.Oh, wait.Right.Anna is in hospital because of her stomach flu.Which was a result of that toad bark stew she had with Rod.So Rod was not in the car with us when we left.Holy Mother of God.That is, we've been with a butcher whose identity is unknown to all of us.Checked you!
```

### [62] hash=`df3a5f7edf2ea53b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Please get so dark!What time is it now?Okay, okay.Afternoon.1pm.Nope.That butcher is going to slaughter us.He is truly a cold-blooded murderer.Don't freak out, Freddy.A murderer is not someone you frequently meet.You're not shooting a horror movie.Actually, you are.A giant monster?A fake friend of yours?A sudden nightfall?Anything you're not like a horror movie?Damn it, aren't you being paranoid enough?
```

### [63] hash=`8b52f473b109be44`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Do you want the situation to get messier?You, sit down.I will go check the electrical panel and fix it.It will bring back the light and restore your sanity.Negative from me.Those who remain alone in a horror movie never end up safe and sound.If the butcher is really lingering outside the door, you will be his first blood.Although you are rude, impolite, and suspected to ancestry discrimination,I suggest you to take someone with you for the sake of your safety.
```

### [64] hash=`e034bbff53f2fb2a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p20`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜1~6）

```text
Oh, back off, you troll!He really didn't do that on purpose, did he?What's on purpose?He said and did all the things you shouldn't be doing.We are in a horror movie.His actions are like taking some sleeping pills,biting the noose around his neck and shooting himself in the head.
```

### [65] hash=`83c02c3ee8bd3781`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
It has been seven minutes and twenty-five seconds since our bro the Bray took the one-man mission.I've never fixed a panel before.Can anyone tell me if it's normal to take this long?From my experience in human society, it is not too long.If the device has been drastically destroyed or the maintenance man is not familiar with that model,it will take longer time to fix.This is not unusual.We need to go outside to find him.
```

### [66] hash=`5b9be701fa388d75`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
We are not in the human society.Aside from the butcher, he might confront some other troubles.Sinetta, you stay here with Ms.Tooth Fairy.I will go find Jason with Horrorpedia.No matter if we find him or not, we'll come back in five minutes.What if you don't?Then it means we are not in the kind of horror moviewhere Ms.Fortune only happens to lone wolves.If we don't come back,please evacuate the whole campsite and contact rescue.
```

### [67] hash=`daec307279418b4f`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Jason?Relax, man.Firstly, lone wolf disappears.Next, it will be the people who failed to escape.Now we must stick together.At least the rain was the origin of all these weird things.You shouldn't have walked into it.I remember the weather forecast said there won't be any rain in this area today.Like the story of Zeno Youth Force.We are in real danger now.Zeno?Zeno Armaments, Engineering and Technology Academy?
```

### [68] hash=`2c10e689ff154770`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
You know it?Are there anecdotes about Zeno and the town as well?Live here.This cabin.Away from those weirdos!We're leaving!Well, we should listen to our friends and stay-If- if rot can be fake, this whole campsite can also be an entire illusion!You guys look normal, just like- like any ordinary people whom we would possibly run into in a place like this!But then, you will infiltrate!Please calm down.
```

### [69] hash=`045daf6fbd72c8eb`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
We've only been trying to help.Won't be deceived anymore.I will shoot you stay away from meJason is rightArcanists are all insaneLet you get into my carYou guys stay here and wait for the butcher to get you.I'll let them leave like this hurry upGood.It's too dark out here hardly visibleMichael must have driven out of here, but how did Lonnie disappear in the blink of an eye?To the south.The skid marks and footprints all point to the south.
```

### [70] hash=`e2d63aa952243d67`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Here are the claw marks of the critter.They might be in danger.We need to hurry up.Over here!I found her!Stay still!We're coming for you!Ms.Twoferian Horipedia, please follow them.Senetta and I will handle this.Be careful.This critter is very malicious.Use this if needed.The rain has healed its wounds.It's getting stronger and harder to deal with.May the peace be with us.This should be fine, right?
```

### [71] hash=`d147e2886b87d8ce`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
It seems to be mixed up.I think it is.Watch out.The spikes from the forest.Oh, bad version.They're holding to pieces.You're awake!I have just given you first aid for the wounds.For now, we will have to wait for Ms.Tooth Fairy to administrate a thorough treatment when she comes back.Don't worry.We didn't find her in the woods, wasn't she in Michael's car?No, she wasn't.She jumped off, she saw me being attacked by the critter and jumped out from the side window.
```

### [72] hash=`6a565e33bbf42896`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Oh no, the butcher, he must have taken in, must be with him, I saw him too.He was walking towards her.Just like what would happen in a horror movie.I'm terribly sorry for what you're going through, but this is not the typical kind of treatment that we used to receive from herBut then she wouldShe would ask us to take the tooth fairies.That is those golden elves in the glass jarThey're effective in treating toothache and other oral diseases, but also
```

### [73] hash=`8cd3361387957b29`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Can be used to reduce inflammationStimulates wound healing and relieve headachesI will just put it in my mouth and swallow it with my eyes closed!This is not about you.It is my own rule of treatment.I have specific treatments for humans and Arcanists correspondingly.Through our contact so far, I got to know that you don't consider yourself as an Arcanist,and that's why I will not treat you as one.
```

### [74] hash=`9c6dca4447c97166`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Are you upset about what I said?I owe you an apology.I shouldn't have been rude to Arcanists in front of you.I know it hurt your feelings.I was not myself.I chose to live amongst humans, chose to be their friends, to be a different Arcanist.I thought in this way I would be taken in as one of them.But as you see, when things come to a critical moment, they run away without me.It was my car that they drove to escape, and yet they called me a freak and left me here to die.
```

### [75] hash=`28a88af1ca5c1827`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Funny, isn't it?I've applied Carbuncle Growth Promoter.It will paralyze, sedate, and accelerate your cell regeneration.Your wounds will close up in 30 minutes.Isn't that a medicine for our canists?It is a prescription approved by the medicine examination supervised by Campbell.In this case, it doesn't violate my rule.I could have applied this earlier and spared me the pain.I don't rely on painkillers.
```

### [76] hash=`b8ccd7a5aa81d078`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
I am an excellent doctor.Minimizing patients pain is of course my forte.When kids can't suppress their pain,I normally sing for them to ease their pain.You didn't sing for me!Was itbecause you didn't want to?Maybe.I confess what you didn't say at firstwas really annoying.Alkanists and humans almost act as if they were ofone merged entity, but we all know how lines have been drawn between theirpeople and the others.
```

### [77] hash=`af097cce9e5d274e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
You grew up among humans and you learn to look away fromthe truth as they did.But you do react better to the medicine for Arcanists.Their blood is bringing you a good outcome.In another half an hour, yourwounds will be fully recovered.By then, you will be able to jump and runfreely as if you were never hurt.However you feel about your ancestry, itShe pretended that she got a stomachache, lying in bed for half a class.
```

### [78] hash=`5e26361dbe6ff8e1`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
She took many toffees when she left.The caretaker faked her illness?And that also explains her toffees.You didn't know that?It seems I need to apologize to Vertin for letting out her secret.But thank goodness you are on her side now.Our negligence didn't cause much damage.The last girl normally has two categories.Anna is the exemplar of the first kind, pure, innocent, and mild like a virgin.The second kind is those cool girls, more condescending, erudite, and sophisticated.
```

### [79] hash=`f89d2186137ae4b9`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
This category can easily tackle any difficulties and make sensible choices like our mist-toothfairy.They are all good girls, approved by society, therefore people reward them with the privilegeto survive.The critter's claw and the butcher's cleaver will never hurt them or kill them.so what do you mean I mean please don't worry it'll be fine she is safe she isparticularly safe before we die but if we lose her the probability of our
```

### [80] hash=`95cc58fda021e5e2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
death will go up up up up up and up very comforting wait the carcass of thegiant critter is missing maybe it's not totally dead and has crawled back toThis is the smell of the key.The moss here is definitely special.We need to take some samples back from this tooth fairy.A curtain?It's Anne's voice.She must be here.Anne, can you hear me?Below.The pit is deliberately dug.The soil here is dry and granular.
```

### [81] hash=`1621b103cca4a846`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
This was originally a cave.She is hidden inside.I see you.Stay strong and take my hands.I will pull you out.Thank you.I thought I would die in there.Where are the others?Aren't they alright?Did someone go rescue them as well?We saved Blonnie, but didn't find any of the boys.Don't worry, we will do our utmost to find them.This is good news.Jennifer is safe now.The butcher threw me into that pit and left.
```

### [82] hash=`ae73bcba566e8083`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
I don't know when he'd be back.Perhaps anytime now.Ferdin, we have to get out of here now.Just as the classic plot goes, this is the right timing.Step back.He can't kill you, but he might hurt you.I will fight along this time.I can't be a burden to you now.Run!Run away from him!Don't let him catch you!You can let go of Mian.It's over.He disappeared.Right.I know.Yeah, you defeated him.Like a marvelous miracle.
```

### [83] hash=`24ae30ad96a4a37e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
A miracle, a brave heart, and the miserable death of the crazy criminal killed by his own weapon.This is The Last Girl.Filled with bizarre little items.Puppets, a Ouija board, audio tapes, a diary and a ring box.To my forever love, Victoria, here lies my lifelong secret.In the summer of 1973, I took the life of a young lady.Oh, sounds like an intriguing story.Those kids will love it.The pity is, I find no teeth here.
```

### [84] hash=`dcd5324397d5daa9`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
That'd make another trap.The cabin is more safely secured now.Now, take these boards to the east side of the house.We need to have that direction covered as well.It was pure luck.No, you are awesome.You stroke away a knife at the branch and took the murderer's life with his own weapon.I can't be wrong with your part to play here.You are the last girl.I should have noticed this earlier.You are gentle, simple, and kind-hearted enough to put yourself in danger to save others.
```

### [85] hash=`781b5c30cc66e2d3`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
No one is more suitable for this role than you.This is your part.Good, good.From now on, I will stay right next to youWe haven't found any trace of human activities.This is a potion.Like most moss-made potions, it paralyzes the central neural system of humans.The subject will become impulsive, confused, and mad.They permeated the whole campsite with the rain,taking away the sanity from Jason, Freddie, and Michael,
```

### [86] hash=`41c557aeda89ad38`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
like what would happen in a horror movie.No surprise.Ordinary people would never behave as foolish as the main characters in a horror movie.It's said that a similar smell was also found on the Xeno Youth Force.Were they controlled by the moss here?Yes.The changes of personality can be one of the effects of the moss.So the moss not only affects humans, it also works on Arcanists.What about us?Why haven't we been affected?
```

### [87] hash=`efca7b1895153bd0`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Time.It takes time.Humans perceive the world through the use of reason.They are the creature of logic and senses.However, they soon lose their sanity when they meet insanity.Our canists are not the same.We were born with chaotic, mixed emotions.Our innate sensitivity to feelings and potion resistance are stronger.The Xenal Youth Force stayed here for an adequately long period to be contaminated.It will also affect us when the time comes.
```

### [88] hash=`ed146403c5d46fa8`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Perhaps we have lost our minds without realizing it.What are these?They look appealing!Why hasn't anyone told me about them?In the attic these tiny and exquisite items have a lot to dig intoPity I still haven't found a toothThey're trying to solve the problem yet.We can do nothing but fiddle aroundMaybe I should have worked harder in college so that I can at least understand a thing or two from the conversations
```

### [89] hash=`79dfa6c726bba515`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Don't worry Jennifer.I don't understand any of what they said either.You are not alone.I'm here with youI'm not like you.You literally don't know anything.I remember when we first met, you asked of everything I had on me.You grew up here, in a small town, in the middle of nowhere.It's only normal that you don't know anything about the outside world.But I'm different.I've been to big cities.I've gone to college.
```

### [90] hash=`2632b165de659b54`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
I've read books.I pretended to be well adapted to this lifestyle.But in fact, I'm still ignorant, knowing nothing but empty pleasures.My hair color gives away who I am.I'm a silly blondie.Don't speak of yourself like this, Jennifer.I'm not silly.You're smart.You make your own movie with the script you wrote by yourself.You're pretty and kind and you're the best person I've ever known.Please don't hate yourself.
```

### [91] hash=`0d67d13992753164`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Fine, I get it.But can you let go of my hand first?You're hurting me a bit.Sorry.Are you going to be okay?Shall I get you some ointment before these red areas on your hand?You're funny.I'm not some glass doll that breaks for being held too tightly.You're a great fun.You're smiling.Did I make you happy?This is good.Don't you find me weird?My attitude changes so rapidly.I've been mean to you for a long time, and all of a sudden I start to follow you around
```

### [92] hash=`3023a942811bad63`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
and try to use you to survive from this.Weird?What's so bad about that?Even if you're weird, it's a good kind of weird.I like you staying by my side.Even if I'm a benefit-driven fence-sitterwho immediately embrace Arcanistafter being ditched by my human friends?Jason and Michael shouldn't hate youif they knew you better.You seem to really like me.You would jump off the car to rescue me.You protect me, praise me, you would even be happy because I was happy.
```

### [93] hash=`dba0f5f26eb7cbc7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Because I've never seen anyone as pretty as you are.You're special.You're different to the rest of us.Oh, stop.I won't be embarrassed for these nice things you said about me.I've heard enough of them throughout my entire life.Listen, I'm very sorry for mistreating you, and I'm grateful that you came to save me.I will reward you with a secret.My secret.Do you want to hear it?Absolutely!I'd love to!
```

### [94] hash=`c6dac81e18554e5c`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
In fact, I don't hate horror movies.This is the diary I found in the attic.There were many other things, like a full warehouse.Actually liked them a lot when I was a kid.I spent most of my time here, in Green Lake campsite, writing my own horror moviescripts on paper.The handwriting is pretty childish.So the writer might be around 8 to 13 years oldSome of the narratives are straightforward, but the story itself is very creative
```

