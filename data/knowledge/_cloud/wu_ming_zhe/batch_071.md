# 剧情图谱抽取 · batch 071

- 角色：`wu_ming_zhe`
- 批次：**71** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.2」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_071.jsonl`

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

### [0] hash=`8b8da902f81e754e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
But later we moved to another townMy parents are in great success in business and we moved into a high-profile community where only humans are allowedWe were also given privileges that or canis cannot enjoyIt was then, I realized, nobody wants me to be an Arcanist.It was since that day, the diary stopped updating.It might be forgotten, or taken away.The story ended there.That's why I decided to break off my connections with Arcanists, and stop showing interest
```

### [1] hash=`1ca1cdae2913c82d`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
in emotive things like horror movies in order to hide the Arcanist side of me.I took out my energy on other things, which may ease my mind, like soap operas, new clothes,fashions.People liked me this way.They said this is what I'm supposed to do.They believed I'm a dumb bimbo, believed that I hate books.I led a life they want me to have, till I graduated from high school.I don't like these people.
```

### [2] hash=`6be40412b1d9522a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
You shouldn't have been put through this.You are the smartest person I've ever known.If one day I run into them, I will pull their noses and mouths off, like this!A wonderful idea.I wish I was as creative as you are.So, in the end, I attacked one of the jerks who didn't watch his mouth at the prom.I slapped him in the face and smashed four sandwiches and a salad on his head.Then, feeling resentful for what had happened, I applied for a degree in filmmaking, a
```

### [3] hash=`595234515966ac1b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
But I have lost control over my power since I threw it into the l-Huh?Aren't you guys cold?It's so chilly!That ring...wasn't it on my finger a minute ago?Watch out.Something is approaching.I failed.I took her down!Around again!Do I do?Buddy, if you want to survive, leave that ring alone!Get down from the ground!What they need is a song.What on earth is that?I was a talented driver.Once we get out of here, I'm going to get myself a driver's license.
```

### [4] hash=`ec99e5d054ed3e88`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Within 30 seconds you crashed over every critter in our site.I don't think you were qualified to be a driver.No, no, that's not the point.Where did you fit the car?Pink lines.This is drawn with an oil paint pen.This is her arcane skill.Your arcane skill restored pretty fast.For making progress in life, and for your courage to embrace who you truly are.Hey, this is my handkerchief.Take it, wipe your face.
```

### [5] hash=`80ac52c733b46266`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Did you just get a bit woozy from putting up a big scene to the rescue?I didn't!Okay, uh huh, yeah, mhm.What are you doing?I know the rules of social courtesy.You just saved my life, so I won't embarrass you by telling others you just overestimated your ability.If you are willing to take advice from me, I would say don't overburden yourself.There's a note hidden inside, just like the one found in the butcher's corpse.
```

### [6] hash=`25e564a0663898ee`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Someone is passing messages to us through these notes.If we defeat more monsters, we will get a clearer picture of what's happened at Green Lake campsite.This is the all-time favorite trick of the plotter.He takes the whole situation under control, playfully teases the innocent participants like us,through which she gains a special sense of fulfillment, but we have our means to cope with it.The ring brought us a putrefied ghost bride.
```

### [7] hash=`5266982a98b4b4d2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Then we got the book, the pill box, the weird samples.Every item from the attic comes from a monster we just confronted.Touching the Forbidden and the Misfortune will befall you.We can find stories of this kind in many civilizations, but what if we used to fight back?It's always better to take action before our enemy does.Horipedia, how lucky is it for you to get their weaknesses right?Almost a hundred percent.
```

### [8] hash=`4508093b5da06a89`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
If one Horipedia's not enough,we have one more creative Miss Horipedia here as backup.Can't be talking about me.Of course you.You are erudite and experienced in horror movies.Relax, you deserve the title of Horipedia.Does he always vex people like this?Or is he just being annoying here?Mr.Horopedia is not a bad person.He's just a bit...unconventional.There's no doubt this is the craziest carnival ever!
```

### [9] hash=`70fbfed21cd1576c`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
The delirious fog, the attic filled with curses, the rainy night and the countless monsters...I praise you, my beloved cabin in the woods!So many things seen!I venture this sneezing critter specimen has been standing here for over a hundred years.who lived between a world of humans and alkanists.These things happen.I can imagine that.Anyway, at least I got to point out that his teeth were chattering and that made him cry.
```

### [10] hash=`405dd9ed7bfe850a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
That was fun.Totally worth the scolding from my father.Think of it that way.It's not that bad to be a freak.Who knows?Maybe.I'm glad you say so.Watch out, they're coming.Put that aside.Tell us the story you wrote about that specimen.Arrested life is even more dangerous.Thanks for noticing, Ms.Tooth Fairy.If this thing has something to do with the butcher,we may predict his weakness through it.You're getting better and better at this, Burton.
```

### [11] hash=`207f5c951f89f5cb`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
A simple logical deduction, plus a movie knowledge.Bang!Oh, my dear GS-003 Silver Bullet, I will give you a kiss.By the way, did I mention that it actually doesn't include any silver?I barely had any chance to test it, you know, you know field missions, let alone a real spiritual body to be my lab rat.I could only analyze their information, predict their action patterns, and ask for a little help from Laplace.
```

### [12] hash=`5c353ab682e6400d`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
Look how my bullets penetrate those ghost critters' heads just now!You do know that nobody gives a rat's ass about your bang bang ghost shooting lecture, right?After watching a film, haven't you had that what if I'm the heroine fantasy?The words written on this love letter are smudged by rain.I wish I could read them.It's more of an arcane gadget symbolizing a tragic love story.The only purpose is to hold a curse ritual.
```

### [13] hash=`6cddb15a8791fab1`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
To fake an event record is simple, but to create a poem.I assume the one behind all these is not able to do that.I agree, Ms.Tooth Fairy.Please take this note, Timekeeper.I'm looking forward to your deduction.good this should be the last note Fertin these are all the notes we can find inthe backyard I just checked on Jennifer and Sunetto they're still looking formore but this shouldn't take them much longer thank you for your update except
```

### [14] hash=`ddb7c4af1d309908`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p21`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜7~13）

```text
that Fertin can I ask you a question sure please do you have any wishes bigWith information we can, we can start cross-examining them any minute.I get it.Let's go back.Have you noticed?Noticed what?The rain has stopped.
```

### [15] hash=`850f2e49c862431c`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
That's right.This is where all the stories are leading to.Huh.Jack the Drowner, the monster crying under the water, and the bride sinking into a glistening mirror.Here must be the center of all that happened.This is where the ghost stories we encountered at the campsite were created, and now they have led us here.What we need to do next is find the clues hidden here and let the clues build our story.
```

### [16] hash=`5534f4a3baddf00b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Hm?What's wrong, Blonnie?when we arrived here was there was there a lighthouse huh hmm I think it justshowed up out of nowhere like a ghostly figure appearing behind you a lighthousein the lake lighthouse is the lighthouse in the lake also a classicelement in horror stories well not quite but it can be a good place forit makes no difference whether we are on the shore or in the boat.We're just cakes and different plates to it, if it does exist.
```

### [17] hash=`095480323de8d160`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
If I were the lake monster, between the cake running away from meand the cake which willingly comes to me, I would give the latter one a better ending.Alright, if I have to be eaten like a cake, I prefer to be the cake that has more control over its death.Get into the boat then.Let's head to the lighthouse.Huh, a normal lighthouse.Not even a bloody handprint is found here.Well, I'll be damned.The reality is not as sensational as the stories.
```

### [18] hash=`ddbbc22a3e0e1493`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Just like the permanent teeth loss can't rival the latest and most frightening curse for excitement.This is not just an ordinary place to me.I've never seen this before.I used to come here every day, reading novels by the lake, but I've never seen a lighthouse here.It just shows up like a ghostFollowed by a series of mysterious horrific events come and take a look at thisThis is the man behind the scene is much simpler than I thought
```

### [19] hash=`ded8dc8a27a82dc1`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Maybe he really is a childLike those evil kids in the movies despite their evil nature.They can only perform the evil deeds through simple meansWe're really going to open itWe'll have to open it according to the noteI am saying this is obviously a curse, a lighthouse, a strange lake, a fishing net in a wooden box.Rub it three times, blow and unveil it.What comes out of it is definitely not a genie offering us three wishes.
```

### [20] hash=`fee1ce49a5d48c38`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
We have dealt with more curses in the past two hours than many people during their entire life.If it is a curse, then it is a curse prepared for us.Today, I'm going to read you The Frightening Hunter.I wrote it yesterday.This is the story of a hunter.The hunter is talland muscly and of great frame.He can twist, he'll rebarwith his bare handsand no one can lift his arms up by a hair'sthickness and escape from him.
```

### [21] hash=`dc7b18bb035075fc`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
The hunter lives in the campsitedeep in the woods.He would slaughter every living thing that breaksinto his territory.One day, a group of college studentscame into the forest.They enjoyed their time there, drinking and dancing.When it comes to the night, the strongest of them disappeared.The hunter killed them!He hung the boy's head on the tree and turned to the girl with the blonde hair.Oh!She also soon breathed her last breath.
```

### [22] hash=`0e9aff5623184196`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
The third victim is the clumsy short guy, followed by the nerdy tall guy.The hunter came up to our protagonist, the kind, naive girl.It was the first story she ever told me.An intriguing, interesting story.This is the story of Jessica.How nice, you're here again.Um, since you last showed up here.Just like the character we've seen in the movies,she's a kind, introvert, virtuous girl.The friends of hers took her to a beautiful campsite next to a lovely lake.
```

### [23] hash=`83a6888e676d4be2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
This would be the perfect place for a swimsuit party.You've grown taller.Get up so I can see better.What they didn't know is that deep in the water, a defeated evil army is in hiding.You're frowning.Countless demonic war beasts were roaring relentlessly to be unleashed, and an evilplan has been hatched.A massacre was about to take place.Can I do it to make you feel better, Jennifer?Yes.A nightmare indeed.
```

### [24] hash=`e9af2f823f76a489`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Jessica ran as fast as she could, kept pushing herself to go faster and faster until herankles could not support one more sprint and she rolled into a muddy pond.The monster with dark fur and a bloody mouth was right behind her.Then...Are you crying?Jennifer?We gotta go!Where are you?Oh no!It's Mom!I'm here!Yes, so you are crying, Jennifer.Aren't you taking the notebook with you?Throwing it into the lake?
```

### [25] hash=`8829ec7b2d455818`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Really like this place.Probably never come back here again.I gotta go.Jessica.See you, Jennifer, was the last story she told.I didn't understand what she meant by see you, for she has never actually seen me.After that, I also haven't seen her for a long, long time.feels like, for ages.I went through every corner of the campsiteand collected every item I could possibly find,making stories out of them, one after another.
```

### [26] hash=`5aea21155f078ce2`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
But who was there to tell?There's no one in the woods anymore.At first, I spent my days with my furry friends.They were my loyal listeners,and I taught them how to act and behavelike the monsters in the stories.We played the stories one after another.It was great fun, but the stories got old, no exceptions.This is when those young people came into the woods, like the protagonist in our stories.They arrived with their friends, and each of them have different relationships with
```

### [27] hash=`ac30dae420bc65bb`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
one another.We had a good time, but I would think about Jennifer a lot when I started to believethat I will never see her again, she's back.She came back with many people who I have never met before,as well as a camera that I have never seen.She was here to make a movie,which is a word I used to hear a lot from her.I understand it to be kind of a storythat could be stored in a box.I'm glad that she's still passionate about horror movies,
```

### [28] hash=`3ae31ab1699bc118`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Like what I have been feeling in all these years.They were short of one actress.And I know what that word means.A brilliant idea came to my mind.I joined them.I was like the monster in the stories that hides in the group.She will be so surprised when she finds out what I did.However, an accident happened.There were other people in the forest.Misfortune.What a misfortune.Jennifer was upset.She got into a fight with a strange man.
```

### [29] hash=`3ea683c9bd0ebab7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
I called upon the rain, bringing these people into my story to...They accomplished a good story!The man who knows a lot about horror movies?The man who is always calm?The woman who seems strange?And the woman who smells like a puppy?They are all very interesting people.I think I start to like themThey are different to the people I met before who always cried and fainted very quickly not long after my story started
```

### [30] hash=`37b0f742dabfcaf7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Interesting and of great funSo I want to tell them the truth and make friends with them.I have to let them know about thisThat her name was never AnneJessica this is the last surprise I prepared for you now enjoyYou don't understand!It was me who created the stories, I created that monster!I caught many monsters in that notebook and with all those stories I told, I created her!I turned our last girl into the biggest villain!
```

### [31] hash=`46bd6500f6f904b7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
What should we do now?How are we gonna-You are right.This is the story created by you.We are all created by you.It's your story, your monsters, your past,your cane skill, and your identity as an Arcanist.They all belong to you.Belong?To me?The monster born in the bottom of the lake,the butcher, and the pathetic bride.They all came from you.It was you who taught Jessica how to make a story,how to create all of this.
```

### [32] hash=`8c5c4fdb2dbd272e`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
She created them all, but you endowed her with such ability.Do I shouldn't be so ostentatious?There's no way that I can have control over such a fake bow!If I keep doing this for any longer, I would die of headache before making it to Aunt Jessica!I've warned you so, haven't I?But don't worry, the reliable horapedia will save your neck!Using this amazing tool!Good!Hooked onto the rock!You might feel a bit seasick, please try not to vomit.
```

### [33] hash=`0e42150f1d2e1e4f`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
If you fail, at least don't puke on me!Said so, and hold tight!We are heading towards the riveting!Honestly, can't we just show her our sincerity and care?To share something from the bottom of our heart?To cure her agony caused by the antagonist's lonely childhood?Oh, there she is!Just like I expected.You made it.Did you enjoy the story?Oh, didn't give you any background information in advance.But it's okay.
```

### [34] hash=`65a3fe2f28bbf71f`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
You will see a familiar face or two.I believe you haven't forgotten them.Just like I can't forget you, Jennifer.Come with me.I've prepared you a new home.A home where you may sleep on beds made of soft moss and drink clear, cold spring water.I will get you toffees, coffee, and so many teeth in beautiful shapes.You can even have mine if you like.You will stay here with me happily ever after.Till...
```

### [35] hash=`3be693c56e71a990`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
till...a time even, I don't know, well...Jessica, let us talk.You've been thinking of me, haven't you?Of course I have.You were fond of me, as well as the stories I made, aren't you?Yes, I'm fond of you, Jennifer.Do you want to make me happy?I think so.I have made you happy once.Would you let me do it again?Do you like my story?Let us go then.Including Jason, Freddie and Michael.Let all of us go.Why?
```

### [36] hash=`8a56faf8324a36c1`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
You have made a mistake.You hurt people and that is unacceptable.This is not funny.I was to blame for misleading you.I can't let you keep on doing this.I...Don't you like my story?Yes.I like it very much.It resembles a lot of the stories I wrote when I was a kid.I have no one to talk to.The friends I have here can do nothing but roar.I sing with them as the sun comes up and wake up among them as the moon rises.
```

### [37] hash=`0d6d3b3f6c50164a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Jennifer, you know, I used to have the same dream over and over again.A forest and a grassland, not in Green Lake, nor any places that I know of.I can hear music that I've never heard before.After we met, there is you in that dream.You'd wake up in that dream with me, giving me a wreath.In that dream, I can truly rest.But when I wake up, I found myself in Green Lake again.Do I belong here?In Green Lake campsite?
```

### [38] hash=`e108fe06a3551e4a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Or somewhere afar?In the days when no one is here, I always hum the melody in the dream.Quietly, waiting, until my figure almost blended into the mosses.But I waited for too long, so long that you were no longer a girl, but a woman now.I'm tired of waiting for you, I'm tired of living all by myself, I was hoping thatyou may like my story, that you were different from all those people who always tried
```

### [39] hash=`3cafa053f5a19506`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
to run away.But I don't want that to happen again.We will live a happy life by Greenlight.Singing under the starry sky.Telling stories to each other.And having a sweet dream on the soft loss.Do not make an enemy of the Earth.Don't worry.Let me show you.Ah, it seems to be mixed up.Fine, right?Advice from the forest.Don't leave me alone.Oh look, I still have so many stories to tell.We'll have a good time together.
```

### [40] hash=`0bc7b7899ae94e83`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
The stories by the lake, the hunter hiding in the campsite, you'll like them fast.Monster plot, right?Jennifer?Are we using the return of the monster plot now?Please, save me some lousy plot development.Lousy me?Given that you're holding a knife, I'd better shut up.Handy.No need to look back.Brought you with the armor of the forest.Plan A.What's this?A Mice Pass.The story has ended.It was our first story.
```

### [41] hash=`6782f73dafca1179`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Why?You don't like it anymore?We will never run out of stories, Jessica.Enough with the fight.It does no good to either of us.Listen, ohI will come up with more games and stories.We will live a happy life forever and everDon't worry.I have prepared it allBe careful she's still standingJenniferTechnist in the story the most beautifulkind-hearted girl in our 13th storyHere comes the little bride, bloody and dressed in white.
```

### [42] hash=`2a6bf2c4250a6b78`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Now her story starts, followed by her friends in line.Shenifer, Shenifer!A pearl as pure and white as a tooth.What a shame, she has decayed to such an extent.Typhon won't give up his friends.What Typhon won't give up his friends?No other be it.I know what this is.The Reddison Woods are watching you.This is the gift.Well prepared for you.I weave the gown with thorns.You shall repay with sacrifice of wounds.
```

### [43] hash=`62814e69b2f3a47b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
I will get you.Anything you want.My little button.The sweet fruits.The moss bed.The dew cup.The fog starts to gather around her.Step back.Cover your mouth and nose.Don't breathe the fog in.Her wounds are healing and I sense her arcanum is getting stronger.We need to leave now, Timekeeper.I will search for foods for you.I will take the responsibility to take care of you.Jessica, we will not stay.Now listen to me carefully.
```

### [44] hash=`3abc4339946d18b0`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
No, I hate living alone.I will get you a beautiful house much better than the one you have here.I will show you around restaurants, shopping malls, and discos.And so many places.I will get you a room right in our house.I don't care whether my parents allow this or not.Really want to be with you, but I don't want to leave here.I have no desire for the outside worldI will quickly reveal this true love of mine and people will look at me as if I've done something wrong.
```

### [45] hash=`41f5845558407ad6`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Don't like that.I hate my power gets weakened.Want you to stay?Here with me if I say I could stay I keep herJessica if I stayWhat will you get me?Except for food and shelter.What else will you get me?Will you?If you stay, I will share my critter friends with you.Along with my cave, my keys, my little buttons, anything you want.Sounds great.We will definitely have great fun.But Jessica, where were the people who once chose to stay here?
```

### [46] hash=`b2d790f9588dda63`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
When they stayed for long enough, after you ran out of all available gains,They were no longer attractive to you, and no longer adored by you.I can stay longer than them, but with no exception.I will become boring one day.You will be alone again.Every day waking up, falling asleep, roaming in the dream alone.You can lead a different life.You can embrace a diversified and meaningful life.A diversified...meaningful...life?
```

### [47] hash=`489063ae957f756b`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
When you were Anne, you asked what my wishes were, now I know the answer, I know what Iwant.It's you.Do you want to come with me?I will find you a good place to stay, where nobody will consider you to be weird, norwill they keep staring at you.You will see the world with us, the amazing and unique outside world.This outside world, what else will it have?There are a lot of people and fantastic things out there.
```

### [48] hash=`6112093a87f71707`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Some people eat gold bars, some others dance on the crocodile skin.Some people ride a rocket, dashing into the sky, and eventually fall into an unknown zerogene.Even the grassland and the anonymous music in your dream, they truly exist in theoutside world.If you are willing to come with me, you will have them all.Will you really take me to that place?Of course.Why would I trust you?I promise.With everything I can offer.
```

### [49] hash=`2c4efa508868d967`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
I know that word.It means words that cannot be broken.It will make your wish come true.I like you.I hope you can be my friend.This is new.I haven't made a friend like you in a really long time.What's this?This is a gift to you.Press it.You will find out.I see.The medics are ready.Please leave the injured to us.Captain!We found the target and are now carrying out the rescue!Over!There are no enemies here.
```

### [50] hash=`8a334cd0ee1fc786`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Everyone here is a member of our squad.Please don't attack!Repeat, please don't attack!Oh come on, seriously?First we persuaded her with love and care,then we presented the Deus Ex Machina, now we're doing this?What?Madam Z?She's here?Oh, my wounds!How painful!Medics!Where are the medics?What are these?People from the outside world.Don't worry, they won't hurt you.You might receive some training for a period.
```

### [51] hash=`9aefa60761cfed55`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
It might be a bit boring.I promise it won't last too long.Are you suffering from the headache again?Me?No, I'm not.Based on her result of the amended Arcanist Risk Evaluation Chart, this little girl is very dangerous.We rescued nine hostages from her cave.Three are from the film crew, the other six are from the student expedition team that went missing six months ago.The validity of that chart is debatable, for it doesn't have a sufficient number of questions to draw a conclusion.
```

### [52] hash=`351a6d78283489f4`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Yeah, when we arrive at the Foundation, we will give her a more comprehensive test.But that doesn't mean that she'll get a higher grade.We all know that the amended version tends to overestimate the exam needs.Can I visit her while she's in the Foundation?Of course.Chatting with someone familiar is conductive to embracing the community.You don't need to worry too much about her.We'll treat her the right way.
```

### [53] hash=`77c684186ba3ea28`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
The Arcanum shown on her is of a very unique kind and shall be helpful in many experiments.That's good.But I still have one more question.Never!Where did you hear that?Joshua told me.He is just a young man, impulsive and can tell a story from a fact.Why would you believe...Never mind.Back to the business.By the end of the 50s, Zeno found a bunch of critters with unique appearance in the woods near the Green Lake campsite.
```

### [54] hash=`c447a5ebe8d1f1c4`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
As they continued to investigate, they found a special moss in the woods that can trigger changes in appearance.In order to conduct further research, they built a campsite and held some camping activitiesas a disguise from time to time.The critters mutated and evolved very fast.Meanwhile, the town prospered and the nearby population soared.After several incidents of attacks on local residents by flat creature subjects, Zeno
```

### [55] hash=`ddf9795d8631d815`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
decided to move the campsite out of that area.That dear girl was neglected during the moving.She was left at the Brine Lake and kept on secretly living there till now.Other critters that escaped have hybridized with the local breedsand hence created a new critters you've encountered.They more or less carry a lineage of changelings which are very hard to deal with.But thank god you've brought this girl under control.
```

### [56] hash=`306946c8c15064a6`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Jessica has been like a friend or leader.I think she's more like a leader or even a master to them.Zeno conducted military training to the first batch of critters so they are more obedient than others.Your Jessica is like their commander.She gives orders to the critters at the bottom of the lake through a radio hidden in a remote control so that they act in precise alignment.So you knew the truth of the Greenlight campsite from the beginning?
```

### [57] hash=`f4a3ccda5cd99066`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
It was Zeno's idea to clean up the mess with the Foundation.They contacted me before.If you could have asked me earlier, like before you depart,we wouldn't have to go through so much trouble.Kids were ignorant for lack of knowledge,yet adults were ignorant for their cognitive inertia.In a story where truth and falsity are mingled together,it is hard to tell which is which.What did you say?Nothing, nothing important.
```

### [58] hash=`8048f776e949c8c7`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p22`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-活动】绿湖噩梦｜14~18）

```text
Have you heard of what happened to my brother?Your brother?What happened to him?Do you know how his teeth disappear?I don't want to offend anyone, but wasn't it because of the curse of the Tooth Berries?What?What are you laughing at?Nah, nothing.As for my brother, I will tell you more later.Hush now, give me my camera.I don't need those...those things.
```

### [59] hash=`2f70b58f34ad7434`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p23`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-角色】旧齿与陈痕-0~8.牙仙角色剧情）

```text
I think it is.It's here.Not sure.Just some peculiarities.I'm thinking it is.Our song is.Sorry.It's here.Excuse me.Nothing you can do either?What I'm thinking is.Thank you.It's a beautiful day.Glad to hear that.My girl.That's great.Exactly.My girl.Exactly.My girl.Welcome to adulthood, Campbell.May I join you?Just a second.How did this happen?It does work wonders.What of my way?It does work wonders.

It works.I'm sorry.Should I?Sure.A gentle and patient young woman.Huh.Are you asking me to take care of a bunch of kids?Take it any time you wish.
```

### [60] hash=`23fdd2e37c6b443a`

- lang：`en`｜version：`1.2`｜arc：`—`
- doc：`BV1eo4y1u7aW_p24`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.2-角色】飞跃旧屋之墙.洁西卡角色剧情（更新中））

```text
Jessica.2146, Jessica.Fine.46, Jessica.092146.No.Thank you.What?No.What's wrong?Sorry for that.The situation is not good.Jessica?That's right.No.This is...tastic.The top three students in school, the monitor assistant, and graceful French.Graceful, Miss Boigniche.Forgive me.I will try to make the process less ti-Exactly.So glad that I didn't let you down.I see.Love its sound.Thank you.That's awesome.
```

### [61] hash=`8dbb445059c113c2`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p10`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（10收集癖）

```text
A warehouse filled with bizarre little items.Puppets, a Ouija board, audio tapes, a diary, and a ring box.To my forever love, Victoria, here lies my lifelong secret.In the summer of 1973, I took the life of a young lady.Oh, sounds like an intriguing story.Those kids will love it.Senato!Activate the trap!Prepare to engage!
```

### [62] hash=`bf708f0deaba15a6`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p11`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（11白苔藓）

```text
Any signs of artificial cultivation?I'm not sure.This place has been deserted for so long.We haven't found any trace of human activities.This is a potion.Like most moss-made potions, it paralyzes the central neural system of humans.The subject will become impulsive, confused, and mad.They permeated the whole campsite with the rain,taking away the sanity from Jason, Freddie, and Michael,like what would happen in a horror movie.
```

### [63] hash=`edbdcfb06b3cd6c5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p11`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（11白苔藓）

```text
No surprise.Ordinary people would never behave as foolish as the main characters in a horror movie.It's said that a similar smell was also found on the Xeno Youth Force.Were they controlled by the Moss here?Yes.The changes of personality can be one of the effects of the Moss.So the Moss not only affects humans, it also works on Arcanists.What about us?Why haven't we been affected?Time.It takes time.
```

### [64] hash=`ca6eb0bf8fc583ff`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p11`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（11白苔藓）

```text
Humans perceive the world through the use of reason.They are the creature of logic and senses.However, they soon lose their sanity when they meet insanity.Arcanists are not the same.We were born with chaotic, mixed emotions.Our innate sensitivity to feelings and potion resistance are stronger.The Xenal Youth Force stayed here for an adequately long period to be contaminated.It will also affect us when the time comes.
```

### [65] hash=`8b39b97db4704170`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p11`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（11白苔藓）

```text
Perhaps we have lost our minds without realizing it.Turkeys!They look appealing!Why hasn't anyone told me about them?I found them in the attic.These tiny and exquisite items have a lot to dig into.Pity.I still haven't found a tooth.
```

### [66] hash=`c90c2bdddfe8a8a1`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
Look, they're trying to solve the problem, yet we can do nothing but fiddle around.Maybe I should have worked harder in college, so that I can at least understand a thingor two from the conversations.Don't worry, Jennifer.I don't understand any of what they said either.You are not alone.I'm here with you.Not like you.You literally don't know anything.I remember when we first met, you asked of everything I had on me.
```

### [67] hash=`c14bfbeb80a50ab2`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
You grew up here, in a small town, in the middle of nowhere.It's only normal that you don't know anything about the outside world.But I'm different.I've been to big cities.I've gone to college.I've read books.I pretended to be well adapted to this lifestyle.But in fact, I'm still ignorant, knowing nothing but empty pleasures.My hair color gives away who I am.I'm a silly blondie.Don't speak of yourself like this, Jennifer.
```

### [68] hash=`c7a5a13ef5612d87`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
I'm not silly.You're smart.You make your own movie with the script you wrote by yourself!You're pretty, and kind, and you're the best person I've ever known!Please don't hate yourself!Fine, I get it, but can you let go of my hand first?You're hurting me a bit.Sorry!Are you going to be okay?Shall I get you some ointment before these red areas on your hand?You're funny!I'm not some glass doll that breaks for being held too tightly!
```

### [69] hash=`0fb5d3cd3146badb`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
You were great fun!You're smiling.Did I make you happy?This is good.Don't you find me weird?My attitude changes so rapidly.I've been mean to you for a long time and all of a sudden I start to follow you around and try to use you to survive from this.Weird?What's so bad about that?Even if you're weird, it's a good kind of weird.I like you, staying by my side.Even if I'm a benefit-driven fence-sitter who immediately embraces Arcanist after being
```

### [70] hash=`3a1452d685d72180`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
ditched by my human friends.Jason and Michael shouldn't hate you, if they knew you better.You seemed to really like me.You would jump off the car to rescue me, you protect me, praise me, you would evenbe happy because I was happy.Because I've never seen anyone as pretty as you are.You're special.You're different to the rest of us.Oh, stop.I'll not be embarrassed for these nice things you said about me.
```

### [71] hash=`461c9510a5e179b5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
I've heard enough of them throughout my entire life.Listen, I'm very sorry for mistreating you, and I'm grateful that you came to save me.I will reward you with a secret.My secret.Do you want to hear it?Absolutely!I'd love to!In fact, I don't hate horror movies.This is the diary I found in the attic.There were many other things, like a full warehouse.I actually liked them a lot when I was a kid.I spent most of my time here, in Green Lake campsite,
```

### [72] hash=`9978886c06ffdbe5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
writing my own horror movie scripts on paper.The handwriting is pretty childish,so the writer might be around 8 to 13 years old.Some of the narratives are straightforward, but the story itself is very creative.But later, we moved to another town.My parents are in great success in business, and we moved into a high-profile communitywhere only humans are allowed.We were also given privileges that orcanists cannot enjoy.
```

### [73] hash=`b90f9e94ac6101ba`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
It was then I realized, nobody wants me to be an orcanist.It was since that day, the diary stopped updating.It might be forgotten, or taken away.The story ended there.That's why I decided to break off my connections with Arcanists, and stop showing interestin emotive things like horror movies in order to hide the Arcanist side of me.I took out my energy on other things which may ease my mind, like soap operas, new
```

### [74] hash=`f20c325c884f3987`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
clothes, fashions.People like me this way.They said this is what I'm supposed to do.They believedI'm a dumb bimbo.Believed that I hate books.I let a life they want me to have,till I graduated from high school.I don't like these people.You shouldn'thave been put through this.You are the smartest person I've ever known.Ifone day I run into them, I will pull their noses and mouths off.Like this!wonderful idea.
```

### [75] hash=`a3a1e4ffbc8bac04`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
I wish I was as creative as you are.So in the end I attacked oneof the jerks who didn't watch his mouth at the prom.I slapped him in the faceand smashed four sandwiches and a salad on his head.Then feeling resentful forwhat had happened, I applied for a degree in filmmaking.A course which wasconsidered to be ill-fitted to me.And next I start shooting horror moviesThat's itWell, we are all here paying attention to your voices
```

### [76] hash=`a68d6aedf337d071`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
We heard everything you just said think this is yours now.I should hand it back to you.Where did you find it?I haven't seen this for a really long timeI used to do some Arcanus tricks with itBut I have lost control over my power since I threw it into the look huh, huh, aren't you guys cold?How come it's so chilly?That ring, wasn't it on my finger a minute ago?Watch out, something is approaching.Can't fail.
```

### [77] hash=`438ae7c6bc7196f2`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
Do I do?If you want to survive, leave that ring alone!Ground!What they need is a song.There's two for singing.I'm sorry.What on earth is that?Know I was a talented driver?Once we get out of here,I'm gonna get myself a driver's license.Within 30 seconds,making me a bit hype.A good try.Please keep up with the feeling.That's all I need to say.Can I take it as a gift?You mean?Well, you still owe me a song.
```

### [78] hash=`3544fa889581323f`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p12`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（12急速激情）

```text
Please, I want a song from you.Sure, take it as a gift.For making progress in life,and for your courage to embrace who you truly are.Hey, this is my handkerchief.Take it, wipe your face.Did you just get a bit woozy from putting up a big scene to the rescue?I didn't!Okay, uh-huh, yeah, mm-hmm.What are you doing?I know the rules of social courtesy.You just saved my life, so I won't embarrass you by telling others you just overestimated

your ability.If you are willing to take advice from me, I would say don't overburden yourself.
```

### [79] hash=`9758744a7f43f08b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
There's a note hidden inside, just like the one found in the butcher's corpse.Someone is passing messages to us through these notes.If we defeat more monsters, we will get a clearer picture of what's happened at GreenLake Campsite.This is the all-time favourite trick of the plotter.He takes the whole situation under control, playfully teases the innocent participantslike us, through which he gains a special sense of fulfilment.
```

### [80] hash=`ec8b1aba3f2675fc`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
But we have our means to cope with it.The ring brought us a putrefied ghost bride.Then we got the book, the pill box, the weird samples.Every item from the attic comes from a monster we just confronted.Touching the Forbidden and the Misfortune will befall you.We can find stories of this kind in many civilizations.But what if we used the fight back?Not to wait for the monsters, but summon them to us.
```

### [81] hash=`dde03229fb4d28ab`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
Exactly.If you want, we can select which ones to summon first.If you carefully look into each of these, you will find that these items have a lot to tell us.If we plan their arrivals and predict their weaknesses in advance, victory will absolutely be ours!Good strategy, but equally beneficial.However we decide to do this, it's always better to take action before our enemy does.Horipedia, how lucky is it for you to get their weaknesses right?
```

### [82] hash=`bdbcb2ec0e8aec9b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
Almost a hundred percent!If one Horipedia's not enough, we have one more creative Miss Horipedia here as backup.You can't be talking about me!Of course you!You are erudite and experienced in horror movies.Relax, you deserve the title of Horipedia.Does he always vex people like this?Or is he just being annoying here?Mr.Horropedia is not a bad person.He's just a bit...unconventional.There's no doubt this is the craziest carnival ever!
```

### [83] hash=`c76179c9e06289af`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
The delirious fog, the attic filled with curses, the rainy night and the countless monsters...I praise you, my beloved cabin in the woods!I bet you this sneezing critter specimen has been standing here for over a hundred years.Ew!It's just like...like what?Oh, never mind.My dad had a business partner.An old money, you know?Who had a real wonder room in his mansion.I was seven back then.His son wanted to show me his so-called masculinity and took me to see his great-grandpa's collection.
```

### [84] hash=`e002df5ffa018c40`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
He thought I would be screaming when I saw the freaky tube-headed snake specimen, but he didn't know that I was a freak myself.Put that aside.Tell us the story you wrote about that specimen.You must have written one about it, right?I would like to hear it too.I'm sure it will be interesting.Seriously?It's written by a seven-year-old girl!Maybe someday I'll make it a film.Those users who want to brag about their masculinity in front of girls will wet their pants in the theater!
```

### [85] hash=`0b13278fbbcd9aae`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
Before that, someone get that note out of those...things.For the record, I won't lay a single finger on it.Watch your fingers, Ms.Burton.A rusted knife is even more dangerous.Thanks for noticing, Ms.Tooth Fairy.If this thing has something to do with the butcher, we may predict his weakness through it.You're getting better and better at this, Burton.A simple logical deduction, plus some movie knowledge.
```

### [86] hash=`13cedf6ec243b6bd`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
Bang!Oh, my dear GS-003 silver bullet, I will give you a kiss.By the way, did I mention that it actually doesn't include any silver?I barely had any chances to test it.You know, field missions, let alone a real spiritual body to be my lab rat.I could only analyze their information, predict their action patterns, and ask for a little help from Laplace.Look how my bullets penetrate those ghost critters' heads just now!
```

### [87] hash=`b2138856310e001b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
You do know that nobody gives a rat's ass about your bang-bang ghost shooting lecture, right?After watching a film, haven't you had that what if I'm the hero in fantasy?The words written on this love letter are smudged by rain.I wish I could read them.It's more of an arcane gadget symbolizing a tragic love story.The only purpose is to hold a curse ritual.To fake an event record is simple, but to create a poem.
```

### [88] hash=`42309e0c197d0ad1`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
I assume the one behind all these is not able to do that.I agree, Ms.Tooth Fairy.Please take this note, Timekeeper.I'm looking forward to your deduction.good this should be the last note Fertin these are all the notes we can find inthe backyard I just checked on Jennifer and Sandero they're still looking formore but this shouldn't take them much longer thank you for your update exceptthat Fertin can I ask you a question sure please do you have any wishes big
```

### [89] hash=`d6e2655c5118cacf`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
Mr.Horropedia wants a cup of coffee or a gum, Ms.Tooth Fairy wants a collection ofcritter teeth, and Sonnetto.Yeah?Who wants a toffee?She said she wants to taste it properly this time, for she has never really paid attentionto the flavor.Once we get out of here, their wishes will soon come true.How about you, Anne?What do you wish to get?It is a secret.I can't tell you now, but I will get you some presents.
```

### [90] hash=`a5484e45105102e9`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p13`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（13幸运曲奇）

```text
I don't have many friends, and I really like you.Timekeeper, an ease of information we can.We can start cross-examining them any minute.I get it.Let's go back.Have you noticed?Noticed what?The rain has stopped.
```

### [91] hash=`850f2e49c862431c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p14`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（14高塔之上）

```text
That's right.This is where all the stories are leading to.Huh.Jack the Drowner, the monster crying under the water, and the bride sinking into a glistening mirror.Here must be the center of all that happened.This is where the ghost stories we encountered at the campsite were created, and now they have led us here.What we need to do next is find the clues hidden here and let the clues build our story.
```

### [92] hash=`e9701a5d3ed917be`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p14`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（14高塔之上）

```text
Hm?What's wrong, Blonnie?when we arrived here was there was there a lighthouse huh I think it just showedup out of nowhere like a ghostly figure appearing behind you a lighthouse inthe lake lighthouse is the lighthouse in the lake also a classic element inhorror stories well not quite but it can be a good place for horror stories inmiddle of a huge gloomy lake a lighthouse stands there like the fang
```

### [93] hash=`47adf54bc48df6b0`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p14`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（14高塔之上）

```text
and a monster's mouth you can't find any place better than this to hide ahorrifying secret and there's even a boat here you should know that acampsite horror movie couldn't exist without a little boat huh you're justnot afraid of being killed are you turns over what if there's a lakemonster we might be putting ourselves into its mouth like serving in aof dessert.To be fair, it makes no difference whether we are on the shore
```

### [94] hash=`190c8b66e8a5e23d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p14`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（14高塔之上）

```text
or in the boat.We're just cakes and different plates to it, if it does exist.If I were the lake monster, between the cake running away from me and the cakewhich willingly comes to me, I would give the latter one a better ending.Alright, if I have to be eaten like a cake, I prefer to be the cake that hasmore control over its death.Get into the boat then.Let's head to theI am saying this is obviously a curse.
```

