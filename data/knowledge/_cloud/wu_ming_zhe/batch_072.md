# 剧情图谱抽取 · batch 072

- 角色：`wu_ming_zhe`
- 批次：**72** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.2」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_072.jsonl`

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

### [0] hash=`55e824fb97debae5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p14`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（14高塔之上）

```text
A lighthouse, a strange lake, a fishing net in a wooden box.Rub it three times, blow and unveil it.What comes out of it is definitely not a genie offering us three wishes.We have dealt with more curses in the past two hours than many people during their entire life.If it is a curse, then it is a curse prepared for us.
```

### [1] hash=`2908daa36ed1513d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
Today, I'm going to read you the frightening hunter.I wrote it yesterdayThis is the story of a hunter the hunter is tall and muscly and of great frameHe can twist chill rebar with his bare hands and no one can lift his arms up by a hair's thickness and escape from himThe hunter lives in the campsite deep in the woods.He would slaughter every living thing that breaks into his territoryOne day, a group of college students came into the forest.
```

### [2] hash=`e28f640d14466a2c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
They enjoyed their time there, drinking and dancing.When it comes to the night, the strongest of them disappeared.The hunter killed them!He hung the boy's head on the tree and turned to the girl with the blonde hair.She also soon breathed her last breath.The third victim is the clumsy short guy, followed by the nerdy tall guy.The hunter came up to our protagonist the kind naive girlWas the first story she ever told me an intriguing
```

### [3] hash=`bc86c80ea8698b34`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
Interesting story.This is the story of Jessica.Oh nice.You're here againSince you last showed up hereJust like the character we've seen in the moviesShe's a kind introvert virtuous girl the friends of hers took her to a beautiful campsite next to a lovely lakeThis would be the perfect place for a swimsuit partyGet up so I can see better?What they didn't know is that deep in the water, a defeated evil army is in hiding.
```

### [4] hash=`6489c9aaaa73f683`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
You're frowning?Countless demonic war beasts were roaring relentlessly to be unleashed, and an evil plan has been hatched.A massacre was about to take place!Can I do it to make you feel better, Jennifer?Yes, a nightmare indeed.Jessica ran as fast as she could, kept pushing herself to go faster and faster until her ankles could not support one more sprint and she rolled into a muddy pond.The monster with dark fur and a bloody mouth was right behind her.
```

### [5] hash=`faa73859ca879377`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
Then...Are you crying?Jennifer?I gotta go!Where are you?Oh no!It's mom!I'm here!Yes, so you are crying Jennifer aren't you taking the notebook with you bring it into the lakeReally like this, please.I'll probably never come back here again.I gotta go see youJessicaOkay, see youJennifer was the last story she told I didn't understand what she meant by see youFor she has never actually seen meAfter that, I also haven't seen her for a long, long time.
```

### [6] hash=`bfaf75764e76fa77`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
Feels like...for ages.I went through every corner of the campsite and collected every item I could possibly find,making stories out of them, one after another.But who is there to tell?There's no one in the woods anymore.At first, I spent my days with my furry friends.They were my loyal listeners, and I taught them how to act and behave like the monstersin the stories.We played the stories, one after another.
```

### [7] hash=`e164e0ff23a62f9a`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
It was great fun, but the stories got old.No exceptions.This is when those young people came into the woods, like the protagonists in ourstories.They arrived with their friends, and each of them have different relationships withone another.We had a good time, but I would think about Jennifer a lot.When I started to believe that I will never see her again, she's back.She came back with many people who I have never met before, as well as a camera that
```

### [8] hash=`fb236ae9422fdc25`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
I have never seen.She was here to make a movie, which is a word I used to hear a lot from her.I understand it to be kind of a story that could be stored in a box.I'm glad that she's still passionate about horror movies, like what I have been feelingin all these years.They were short of one actress, and I know what that word means.Brilliant idea came to my mind.I joined them.I was like the monster in the stories that hides in the group.
```

### [9] hash=`34804b11f8f84d14`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
She will be so surprised when she finds out what I did.However, an accident happened.There were other people in the forest.Misfortune, what a misfortune.Jennifer was upset.She got into a fight with a strange man.I called upon the rain, bringing these people into my story too.They accomplished a good story.The man who knows a lot about horror movies, and who is always calm.The woman who seems strange, and the woman who smells like a puppy.
```

### [10] hash=`f9046510b243fb62`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p15`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（15绿湖妖谭）

```text
They are all very interesting people.I start to like them.They are different to the people I met before who always cried and fainted very quicklynot long after my story started.Interesting and of great fun.So I want to tell them the truth and make friends with them.I have to let them know about this.That girl name was never Anne.It's Jessica.This is the last surprise I've prepared for you.Now, enjoy!

Critters!
```

### [11] hash=`c24e2c1bf265664a`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p16`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（16怪物设计家）

```text
The lighthouse is sinking.Everyone move and leave now!She was the last girl.She was our only mean to survive in this horror story and we have lost her.No, she was never with us.It's me who created such a girl in Green Lake.A girl who restrained people and treated them like toys.Calm down Lani, calm down.I can't!The late Tooth Fairy, we have lost all the cards.We still have a chance.You don't understand!
```

### [12] hash=`882c39ac914ca708`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p16`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（16怪物设计家）

```text
It was me who created the stories, I created that monster!I brought many monsters in that notebook and with all those stories I told, I created her!I turned our last girl into the biggest villain!What should we do now?How are we gonna-You are right.This is the story created by you.They are all created by you.It's your story, your monsters, your past, your cane skill, and your identity as an Arcanist.
```

### [13] hash=`ad08d7bd669ad3a5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p16`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（16怪物设计家）

```text
They all belong to you.Belong?To me?The monster born in the bottom of the lake, the butcher, and the pathetic bride.They all came from you.It was you who taught Jessica how to make a story, how to create all of this.Using this amazing tool.Good!Hooked onto the rock!You might feel a bit seasick.Please try not to vomit.If you fail, at least don't puke on me.Set sail and hold tight!We are heading towards the River Bay!
```

### [14] hash=`63a64173daa3ff7e`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Honestly, can't we just show her our sincerity and care?To share something from the bottom of our heart?To cure her agony caused by the antagonist's lonely childhood?Oh, there she is!Just like I expected.You made it.Did you enjoy the story?Oh, I didn't give you any background information in advance.But it's okay.You will see a familiar face or two.I believe you haven't forgotten them.Just like I can't forget you, Jennifer.
```

### [15] hash=`9833edc125cc88ab`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
You must have really liked them.So much that you would remember them, as well as me,for such a long time.I will not leave you alone again.I'll come back for you.Every year, no, every six months.I'll have more time after the graduation.If I make a new movie, you will be my first audience,like what we used to do.But I hate living by myself.I don't wanna live like this anymore.I have no one to talk to.
```

### [16] hash=`f74296e4c333ef95`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
The friends I have here can do nothing but roar.I sing with them as the sun comes up and wake up among them as the moon rises.Jennifer, you know, I used to have the same dream over and over again.A forest and a grassland, not in Green Lake, nor any places that I know of.I can hear music that I've never heard before.After we met, there is you in that dream.You'd wake up in that dream with me, giving me a wreath.
```

### [17] hash=`3aef87dc531d310a`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
In that dream, I can truly rest.But when I wake up, I found myself in Green Lake again.Do I belong here?In Green Lake campsite?Or somewhere afar?In the days when no one is here, I always hum the melody in the dream.Quietly.Waiting.until my figure almost blended into the mosses but I waited for too long so longthat you were no longer a girl but a woman now I'm tired of waiting for youI'm tired of living all by myself I was hoping that you may like my story
```

### [18] hash=`20f3e08aeadcbe4a`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
that you are different from all those people who always tried to run awaybut I don't want that to happen again we will live a happy life by green lightsinging under the starry sky, telling stories to each other,and having a sweet dream on the soft moss.Do not make an enemy of the earth.Don't worry, let me show you.What's this?It seems to be mixed up.Fine, right?Advice from the forest.Don't leave me alone.
```

### [19] hash=`5b643b8d84baa5eb`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Oh look, I still have so many stories to tell.We will have a good time together.The stories by the lake,The hunter hiding in the campsite?You'll like them fans!Right...right...Are we using the return of the Monster Plot now?Please...Save me some lousy plot development...No...me...Given that you're holding a knife, I'd better shut up.Pandy...No need to look back...Brought you the armor of the forest...
```

### [20] hash=`75f7854bc1655258`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Plan A...What's this?A mice pot.The story has ended.It was our first story.Why?You don't like it anymore?We will never run out of stories, Jessica.Enough with the fight.It does no good to either of us.Listen.I will come up with more games and stories.We will live a happy life forever and ever.Oh, don't worry.I have prepared it all.Have to care at allOh my god!Be careful, she's still standingJennifer, you are the best
```

### [21] hash=`e332dd659e94cf04`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Technist in the storyThe most beautifulKind hearted girlIn our 13th storyHere comes the little brideBloody and dressed in whiteNow her story startsFollowed by her friends in lineJenniferA pearl as pure and white as a tooth.What a shame.She has decayed to such an extent.Typhon won't give up his friends.Neither would Typhon give up his friends.Look, Sotheby.I know what this is.The Reddison Woods are watching you.
```

### [22] hash=`9e910e25ab951324`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
This is the gift well prepared for you.I weave the gown with thorns.You shall repay with sacrifice of wounds.I will get you anything you want.My little button, the sweet fruits, the moss bed, the dew cup.Fog starts to gather around her.Step back.Cover your mouth and nose.Don't breathe the fog in.Her wounds are healing, and I sense her Arcanum is getting stronger.We need to leave now, Timekeeper.I will get you the best beds, honey, and fruits.
```

### [23] hash=`0f144f1ae8b00f77`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
I will search for foods for you.I will take the responsibility to take care of you.Jessica, we will not stay.Now listen to me carefully.No, I hate living alone.I will get you a beautiful house much better than the one you have here.I will show you around restaurants, shopping malls, and discos.So many places.Also get you a room right in our house.I don't care whether my parents allow this or not.I really want to be with you, but I don't want to leave here.
```

### [24] hash=`7e2565a2a6b05167`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
I have no desire for the outside world.I will quickly reveal this true look of mine, and people will look at me as if I've donesomething wrong.I don't like that.I hate when my power gets weakened.I...I want you to stay...here...with me.If I say I could stay...Eyekeeper!Jessica, if I stay, what will you get me, except for food and shelter?What else will you get me?Will you?If you stay, I will share my critter friends with you, along with my cave, my keys, my
```

### [25] hash=`426b979d3c88e979`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
little buttons, anything you want!Sounds great.We will definitely have great fun.But Jessica, where were the people who once chose to stay here?When they stayed for long enough, after you ran out of all available gains, theywere no longer attractive to you, and no longer adored by you.I can stay longer than them, but with no exception.I will become boring one day.You will be alone again.Every day waking up, falling asleep, roaming in the dream alone.
```

### [26] hash=`617d31fddbc6de27`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
You can lead a different life.You can embrace a diversified and meaningful life.A diversified...meaningful...life?When you were Anne, you asked what my wishes were.Now I know the answer.I know what I want.It's you.Do you want to come with me?I will find you a good place to stay.Where nobody will consider you to be weird.Nor will they keep staring at you.You will see the world with us.The amazing and unique outside world.
```

### [27] hash=`2635e805f64a4ab7`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
This...outside world?What else will it have?There are a lot of people and fantastic things out there.Some people eat gold bars.Some others dance on the crocodile skin.Some people ride a rocket, dashing into the sky, and eventually fall into an unknown zero gene.Even the grassland, and the anonymous music in your dream, they truly exist in the outside world.If you are willing to come with me, you will have them all.
```

### [28] hash=`32b297136823037d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Will you really take me to that place?Of course.Why would I trust you?I promise with everything I can offer.I know that word.It means words that cannot be brokenWe'll make your wish come true.I like you.I hope you can be my friendThis is new.I haven't made a friend like you in a really long timeWhat's this?This is a gift to you.Press it.You will find out.I see the medics are readyPlease leave the injured to us
```

### [29] hash=`23dce7d24c0ca5ae`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Captain!We found the target and are now carrying out the rescue!Over!There are no enemies here.Everyone here is a member of our squad.Please don't attack!Repeat, please don't attack!Oh come on, seriously?First we persuaded her with love and care, then we presented the Deus Ex Machina.Now we're doing this?This is the worst antagonist ever!Everything is so screwed.Commentators won't write anything nice for us.
```

### [30] hash=`8e5fa0f031a9f108`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
Well, if it were them to write the story, characters like me would always fail to live long enough to see the end.So I don't oppose to end this peacefully.But to end it like this...Aren't you happy?They did it, like what you said.Some emotional and comforting plots.Eventually, it shows us that love always wins.Uh, Ms.Tooth Fairy, that was a joke.A joke to show you my sense of humor.Timekeeper, it's great to see that you are fine.
```

### [31] hash=`88c13d891b982ca6`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p17`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（17新出埃及记）

```text
And Mr.Horipedia, Madam Z is waiting for you in the car outside the woods.Please, come with us.What?Madam Z?She's here?Oh!Ah, my wounds!How painful!Medics!Where are the medics?What are these?People from the outside world.Don't worry.They won't hurt you.You might receive some training for a period.It might be a bit boring, but I promise it won't last too long.
```

### [32] hash=`6828377845f4c727`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
Are you suffering from the headache again?Me?No, I'm not.You shouldn't lie to a doctor.Fine.A bit.Just a bit.Some warm water will help.I don't need those...those things.I don't taste like your tooth fairies.It's the texture that creeps me out.I've tried multiple times.You know how it ended.Don't worry.I have some drugs for humans.Wanna try?She needs to receive some education to become adequately socialized.
```

### [33] hash=`980840d1594a14f0`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
Based on her result of the amended Arcanist Risk Evaluation Chart, this little girl is very dangerous.We rescued nine hostages from her cave.Three are from the film crew, the other six are from the student expedition team that went missing six months ago.The validity of that chart is debatable, for it doesn't have a sufficient number of questions to draw a conclusion.Yeah.When we arrive at the Foundation, we will give her a more comprehensive test.
```

### [34] hash=`838e913e35d9088e`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
But that doesn't mean that she'll get a higher grade.We all know that the amended version tends to overestimate the exam needs.Can I visit her while she's in the Foundation?Of course.Chatting with someone familiar is conductive to embracing the community.You don't need to worry too much about her.We'll treat her the right way.The Arcanum shown on her is of a very unique kind, and shall be helpful in many experiments.
```

### [35] hash=`779c66dcf8483c37`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
That's good.But I still have one more question.Go ahead, Doctor.Members from the Xeno also participated in the rescue.Did you call them to come?Yeah.This should have been their responsibilities.To be more precise, all of these problems were their fault.Are you talking about the missing of their youthfuls?What?No.But wait, what missing use force?The myth that Xeno Youth Force disappeared overnight at the Greenlight Campsite.
```

### [36] hash=`5385b752701c2042`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
Haven't you ever heard of that?Never.Where did you hear that?Joshua told me.He's just a young man.Impulsive and can tell a story from a fact.Why would you believe-Never mind.Back to the business.By the end of the 50s, Zeno found a bunch of critters with unique appearance in the woods near the Green Lake campsite.As they continued to investigate, they found a special moss in the woods that can trigger changes in appearance.
```

### [37] hash=`0da82291b4ba7ae5`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
In order to conduct further research, they built a campsite and held some camping activities as a disguise from time to time.The critters mutated and evolved very fast.Meanwhile, the town prospered and the nearby population soared.After several incidents of attacks on local residents by flat creature subjects,Zeno decided to move the campsite out of that area.That dear girl was neglected during the moving.
```

### [38] hash=`39816dc065f9d77d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
She was left at the Brine Lake and kept on secretly living there till now.Other critters that escaped have hybridized with the local breedsand hence created the new critters you've encountered.They more or less carry a lineage of changelings,which are very hard to deal with.But thank God you've brought this girl under control.Jessica has been like the...front, or leader.I think she's more like a leader, or even a master to them.
```

### [39] hash=`6e48d6110158026c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
Zeno conducted military training to the first batch of critters, so they are more obedient than others.Your Jessica is like...their commander.She gives orders to the critters at the bottom of the lake, through a radio hidden in a remote control,so that they act in precise alignment.So you knew the truth of the Green Lake campsite from the beginning?It was Zeno's idea to clean up the mess with the Foundation.
```

### [40] hash=`373ad6f6e7a0f022`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p18`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（18俗套写真）

```text
They contacted me before.If you could have asked me earlier, like,before you depart, we wouldn't have to go through so much trouble.Kids were ignorant for lack of knowledge,yet adults were ignorant for their cognitive inertia.In a story where truth and falsity are mingled together,Hush now.Give me my camera.Water will help.I don't need those...those things.
```

### [41] hash=`9a14d3ce078cd056`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p19`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（旧齿与陈痕.0至4）

```text
I think it is.It's here.Not sure.Just some peculiarities.I'm thinking is.Or song is.Sorry.It's here.Excuse me.Nothing you can do either?What I'm thinking is.
```

### [42] hash=`4cb626279fc141c6`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
That was a night in 1971.A night with pouring rain.In that rain, the communication center of Zeno lost contact with the Green Lake campsite.Wasn't it a story?I am kind of attracted indeed.It is really not a wise choice for you.It's our rights to stay here.You can't just expel us.Someone is passing messages to us through these notes.We have been with a butcher whose identity is unknown to all of us.
```

### [43] hash=`c4d5dbd7d5cbe5ed`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Like the story of Xeno Youth Force, we are in real danger now.The creatures are multiplying.Things are getting worse.It seems this is the entrance.Green Lake can't say!We are now at the...Green Lake!Michael, a self-explanatory fool.He leads the life of a clown in front of his popular peers, like a companion animal to them.He has turned himself into one of those chattering, gong-holding monkeys,Clowning around with a head filled with junk food, alcohol, and psychedelic potions.
```

### [44] hash=`9ea4c048d594669e`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Green Lake campsite.I hope we can find a clean and vast lake here to swim, with or without a swimsuit.See my muscles?The young ladies will all crazily scream for these puppies.Oh, oh, oh!Ugh.Freddy.An athlete.Captain of the school's rugby team.An ostentatious, self-centered, and annoying narcissist.He is in the prime of his life, a period which will be recalled repeatedly andeagerly decades later, like a drunk man obsessively licking the salt off the
```

### [45] hash=`3f2ab29cf5327695`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
snacks.Damn Freddy, for one second in your life could you please stop thinking abouttaking your pants off?Jason, the young scholar, he is the teacher's favorite student, straight A's,clever, reliable, and logical.He pays more respect to girls than most ofidiotic men do.His interest is reading those encyclopedias or looking into somestrange science stuff.You can wipe your face with this, Michael.We will get to
```

### [46] hash=`afb4741ed0374e10`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
the camp soon.And the Virgin.There is a non-aggressive, harmless amount ofgentleness and beauty in her that you don't get to see much of in thiscrazy time.She was born and raised in a faithful Christian family, alongwith other sisters.She attends the reading session held in her communityevery weekend.Lower your voices.Enough shouting.I'm still hungover so don't mess with me andeverybody will stay happy.
```

### [47] hash=`b57c4af8fdd71009`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Understand?Blondie.Reckless and dumb.A typical blondie.Alwaysindulging herself in alcohol, beautiful clothes, and other vain pleasures.She was luckily bornMichael will be glad to help you sweetie take in with you a girl would know toattend to details one day she will pay for her doings one day they were alltheir heads were hung at the treetop it was until a week later where theyfound by other campers murder there was no murderer at least nobody has
```

### [48] hash=`c285f3a577a5d29c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
seen one some said it was done by a person who has long lost his humanitythat he was possessed by some demonic spirits and therefore immortal Michaelyou fool stop telling such a dumb story come maintain the bonfire idiot I'dfinish the store on my way hey do you guys smell anything I don't think quiteRed?Holy motherfuckin' god!Oh gosh, I just saw it!It's Viscera?Please, F you!Don't throw up on me, Michael, you damn jerk!
```

### [49] hash=`73826d02e9fed8dd`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Step back.This is a badger.Judging from the degree of putrification, it has died at least a week ago.Blonnie, did your uncle mention any beasts living in the woods?Blonnie?Blon-Oh my goodness, they sneaked away again, in this very moment.Well, I think so.She left with Freddy when Michael started puking.Naughty, stop that.Yeah, I can push this further.You see, I will.Timekeeper, now that we have given the report, and Madam Z said we won't have any other
```

### [50] hash=`213ba4fe2071186f`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
I'm flattered you asked, but I'm leaving for assignment soon, so I'm not going to make it.Really?That's a sad coincidence.I heard that you've worked so hard and have saved up so many unused leaves.You also have two days of outing permission.Oh, hey guys.Yes, you guys.Our great Miss Timekeeper and her excellent assistant, Seneto.Am I right?There might be two explanations.One, I got the wrong person.
```

### [51] hash=`1890cfba85ee3434`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Two, this is your sense of humor.Such a puzzle.Deducting by the logic, we might be drowning in the latter one.We just made a joke.I don't find it funny.But considering I have an odd sense of humor,I can politely laugh at your joke.Like this.Hahahaha!This is super awkward.Don't worry, Timekeeper.Although his manner is debatable,he's not a bad person.He was the one who received the Outstanding Contribution Award
```

### [52] hash=`201b639cb29a7a2d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
in the latest annual appraisal.Allow me to introduce...But no, wait!Don't use that name.Here with Timekeeper,just call me Horapedia, which I prefer.Okay, Mr.Horapedia.I've never heard of this nickname of yours.It's a long story.I can share with you at another time.Now, let's get down to business.have you guys heard of the myth of the campsite yeah it was me given that youdidn't know me I sent it anonymously I don't see how these are correlated well
```

### [53] hash=`f077c2abf2241cb8`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
of course they are an anonymous envelope better triggers curiosity and you arethe most inquisitive person I know didn't you worry this I might throw itaway honestly I did so I wrote to another 13 people now I have six mapsDon't be upset.Yours is the most intact one, so I selected it.Thank you for your approval.A mystery solved.No wonder I found the handwriting on the envelope familiar.I did some research on Green Lake Campsite after piecing together the map.
```

### [54] hash=`0d0e3602ac3c394f`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
It was the map of one of the training bases of Xeno.They used to train their youth force there in the early 60s and deserted that base in the early 70s.It had been underused even before it was abandoned.It was more of a boy scout camping site than a military training baseExactly miss Seneto, but this is the outdated version of the story nowThis is not your fault.You haven't been in the headquarters for a long time
```

### [55] hash=`cd36536ab7560372`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
So you must have missed out on some first-hand informationNow about the Green Lake campsite.We have some updatesThat was a night in 1971 a night with pouring rainHeavily and hastily, sheets of rain formed a barrier, isolating the woods from the outside world.In that rain, the communication center of Zeno lost contact with the Green Lake campsite.Was it normal rain?It was, drops of water with dust falling from above.
```

### [56] hash=`997c807b9b7d8951`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
It didn't cause any illusions or unusual symptoms,but took away all the youth force stationed at the campsite.In the cabin they lived.People found clothes, blankets, even books left open on the table.What does not move or breathe stayed there as usual, but their owners, those living youngsters,disappeared from the woods like drops of dew under the sun.Since then, nobody has ever seen those youth force again.
```

### [57] hash=`af660443fbf53bdb`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Zeno has not, nor Laplace, nor us.Green Lake Campsite has then become a ghastly and deserted land.Ms.Sinetto, please put down your hands.They're hindering your ears from receiving information.You might then miss the climax.Thank you for the kind reminder.It was an unforgettable night.Three months later, all the missing members of the Youth Force came back to Xeno.They carried the smell of fungi in moist air, stepping into their dorm without making any noise.
```

### [58] hash=`c51f3a80bd67fea0`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
They claim that they just came back from a tough mission in the rainforest.No one knew what the mission was.No one knew which rainforest they referred to.The personality of all those kids have changed.The outgoing Bruno became speechless.The gentle Anna Queenie starts picking quarrels with others.They were not who they were, but no one could pin down the difference.Day after day, the smell of fungi and moist soil never disappeared.
```

### [59] hash=`155e14f229d60094`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
It lingered for one week, two weeks, three weeks, till one night, grade one student Dreasuddenly woke up from his dream.A muddy tentacle stretching out beneath his bed, closed around his ankle, and pulledhim onto the floor!There, a face awaited him, a hideous face of a human-like creature with a BLOODYMOUTH!Huh?Xeno Armaments Academy, the best military talents training base at present.The members of Youth Force were relatively younger,
```

### [60] hash=`187de4bc836fdd20`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
with less combat experience and capability compared to those graduates.Still, they have received years of training as reserve soldiers.As we all know, Xeno would arm their Youth Force and the trainers with drill weapons for outings.It was nearly impossible to wipe out a youth force in the territory of Xeno without being noticed by the Academy.It's not true, just a made-up story.Tooth Fairy, did you come back from the trip?
```

### [61] hash=`12abe5c13a1f448c`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
I've rerouted my journey to a new destination.My companions suggested us to meet at the Foundation first, so I came back earlier.Anything wrong with the original destination?It's fine and safe, but now I have a better place to go.It's a place of myths and danger.There once lived many adolescents.With any luck, I will embrace a harvest of baby tea.No way.The place you're heading is...It's Green Lake Campsite.
```

### [62] hash=`5ea0635d0ba7b780`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Wasn't it a story?A story made up by Mr.Horipedia?He made up part of it, such as the bloody hands underneath the bed and the midnight screaming.Except for those, the rest is exactly the same as I know.As you just said, in their own training base, it's impossible for the Youth Force to be...It proves that Green Lake Campsite is out of this world, a place worth visiting.You're three minutes and fifteen seconds late, Ms.
```

### [63] hash=`ca3506c57a673d35`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Tooth's Fairy.No worries, I didn't waste my time waiting.We need more people to join us.Angie and Adolf have turned me down, but Verdun and Sanato haven't walked away yet.I am trying to win them over.I think I'm almost there.Now, they are really attracted by the Green Lake, so we are starting off soon.Attracted?Pardon me, J- Mr.Horopedia, we did not plan to go there, and we certainly do not feel any strong attraction to that place.
```

### [64] hash=`f2fbc938403ffb0d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p1`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（01）

```text
Oh, really?But Verdun seems to be very attracted.Or am I mistaken about the look on her face?Timekeeper!I am kind of attracted indeed.See that?I am right!I'm glad to see you in an adventurous spirit, Ms.Burton.Great!Take your suitcase, pack your clothes, don't forget to bring two novels to kill time.Now, let's take the hands of our two new partners.Journey on!
```

### [65] hash=`da5339ed1ac01caa`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p20`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（旧齿与陈痕.5至8）

```text
thank you it's a beautiful day glad to hear that my girl that's greatexactly my girl exactly welcome to adulthood may i join you how did thishappen these formulas wonders out of my wayit does work wonders i'm sorry i've been coming to the marketyou should i show a gentle and patient young womanHuh, are you asking me to take care of a bunch of kids take it any time you wish
```

### [66] hash=`04b318cf32440b94`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
Thank you for the letter EmilyNow we are bringing our driver friends the latest weather forecastOhio is having a sunny week with a comfortable level of the humidity and zero chance of rainSorry, I forgot to switch off the inbuilt radioSit tight and put on your safe belt all the hands of people sitting next to you if necessaryClose your mouth then clench your teeth.You can do as I said or not.I was mainly talking to them
```

### [67] hash=`90dce0dc43af77e4`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
Yes, madamYes, Ms.Tooth Fairy.Are those little winged elves still nagging you?I remember you were troubled by them as early as I was in school.They are still there.They have never left there.The good thing is that they can't distinguish lies.They spend every second of their life overhearing me and totally believe what I say.As long as they hear me say,cover your mouth and clench your teeth, they will never attack you.
```

### [68] hash=`d73a9ff5339d8729`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
We all owe Mr.Campbell a big thank you for this.All of his teeth were stolen when he was with Ms.Tooth Fairy.That's when humans finally realized how vindictive and vengeful those little things are.They stepped across the world for the cure.Eventually, they found a solution.Mr.Campbell?Who is this person, and what happened to him?He is my brother.I am also a Campbell, Ms.Campbell, while he is a mister.
```

### [69] hash=`83927a6f7f2e9488`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
We shared a roof when we were little.I was cursed for eating a tooth fairy.It and its fellows swore to steal all my teeth.At first they did it.I ate nine fairies and lost eleven baby teeth.My parents soon found out.They ordered a special tooth brace for me in case I lose all my baby teeth and becomea horrific old lady.In their second attack, those tooth fairies failed to steal the teeth from Miss Campbell
```

### [70] hash=`8947c978bb6bb838`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
so they rushed to Mr.Campbell.His teeth disappeared in a flash,and he never had one since then.People said it was the curse of the Tooth Fairy.Just like in books, the flying human-like critters are bigoted.Once gained, they will keep the love and hatred at heart forever.I'm so sorry, Ms.Tooth Fairy.I shouldn't have asked.Don't worry, sweetie.My brother now has his own teeth.He lives a stable life.
```

### [71] hash=`a7f109a8d94081b0`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
The past is in the past.And I don't really think he was cursed.I've never heard the tooth fairy swore at him.Neither have I found any mark on him that can be detected by Arcanum.Instead of being cursed, what he suffered is more likely to be a congenitally missing tooth,a term defined in human medical science.I know that case.I just never thought Mr.Campbell lost his because of this.None of my classmates or instructors ever doubted the authenticity of such a curse when they gossip of such things.
```

### [72] hash=`3830f8f615f99806`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
SPDM is a community of a bunch of young arcaneists and several instructors.For those kids, a curse is more common than a disease diagnosed by human medical science.As a result, they neglected what they can't comprehend and only learned the story from a one-sided perspective.Soon enough, rumors started to spread.But that was a curse, a trouble that you can't easily shake off once you were put under.
```

### [73] hash=`9dd4238ed77285a4`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
People could hardly forget that.If Toothpherys could curse his sister, they could also curse him.Everything came naturally.That was it.Kids were ignorant for lack of knowledge, yet adults were ignorant for their cognitiveinertia.In a story where truth and falsity are mingled together, it is hard to tell which is which.After all, life is not a show.You won't have a narrator to warn you of the dangers ahead.
```

### [74] hash=`09fd487fb5a23fbf`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p2`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（02乳齿儿）

```text
Leave here!Careful!Wicked, don't worry.Cover your mouth and nose.Get out of the car.Is everyone okay?Did somebody get hurt?Timekeeper, you-Go away!Go!Go away!Get out of my woods!I heard it.I heard it!I've...I've heard the gods' will!Oh, god...I will guide your children.I will guide them...Guide them away from the demons!Oh, from the land of demons!Dilated pupils, disordered speech, and a body temperature of three degrees higher than the normal level.
```

### [75] hash=`26d636586e5bbdd9`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p3`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（03空铁皮）

```text
This...this must be the camp.Ah, I sniff conspiracy in the air.What will happen here?Murder?Sacrifice?Spy attack?Or evocation?Let me see, let me see, let me see.What do we have here?Things have been left here catching dust, and I see no footprints or any signs of activity.Seems like it has been deserted for a long time.Iron buckets, felling axes, picnic mats.You mean we are in a campsite?It is only normal to expect these tools to be here.
```

### [76] hash=`d585b34050ed2b96`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p3`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（03空铁皮）

```text
What is this?Anything?Have you found anything, Seneto?Something is buried in the ground.Right here.A box?Made of iron or aluminum?It looks like...like a candy box.Touching from the rust, it has been buried here for four to five years.A kid's candy box?I also found the teeth and claw mugs of giant critter as well as some excretion.That is to say...one gigantic critter inhabits here?If not more?Yes, that's why I came back here.
```

### [77] hash=`8356fc9d9974e8f3`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p3`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（03空铁皮）

```text
Watch out for the critters.We may have stepped in their territory.I understand.I'll tell them to be careful, yes.Thank you for your advice.Bye.Angie, come in.This is the file that the Timekeeper submitted.It's about the Storm.Please hand it to the research department.Affirmative.I will bring it to them.Next month, your squad will be dispatched to North America to join Xeno for a joint mission.The tactical unit under the Timekeeper will be replaced by the third squad.
```

### [78] hash=`91715e40d136a9ce`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p3`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（03空铁皮）

```text
Please complete the handover procedure before you leave.By the way, your application for the outing permission has been permitted.The document will be posted to your door mailbox by 7pm tomorrow.I'm very grateful for your help, Madam Z.You're welcome.Get some good rest.Don't forget to remind your team members that actions outside areas mentioned in the application will now be allowed.They need to return back to the headquarters by the specified time and check in once they're back.
```

### [79] hash=`a52c119b5e3b91b4`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p3`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（03空铁皮）

```text
I will, Madam Z.I will look after them.Off you go.He did have some past records of violation, such as being late, absent from duty, and taking actions without permission.His past records means that his outing application will not be permitted.He must be well aware of it.That's why he wasn't even bothered to apply for one.My!No wonder he always said, let's start off immediately and come back furtively so nobody will know!
```

### [80] hash=`525aa706d47d160b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p3`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（03空铁皮）

```text
Don't be nervous.Our priority now is to get them back and minimize the possible consequences.Hello?Is it the liaison department of Zeno Armaments Academy?I am Z.Please put me through Lieutenant Baya.
```

### [81] hash=`b3a850c0b5568bf2`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p4`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（04廉价糖浆）

```text
what was that did someone scream my god jason we have to check it out i know they like to foolaround but we are here now michael stay here and take a rest don't make any noiseall right they will all be fine huh hope so this is not funny wait look over thereWhat the hell was that?Those stories are all true.All true.How is that possible?It is not in compliance with the laws of nature.No more crying, Anna.
```

### [82] hash=`1cee1faa31d63797`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p4`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（04廉价糖浆）

```text
Stand up.Run!I will look out for you.Run!Jason, the flood of blades!Don't think too much.Don't look back.Run!Speed up!No, no, that's my friend, and they aren't.Understand, they deserve a decent funeral.After I take care of this demonic creature, may the peace be with us.Seneto, calm down.The taste of cherry syrup is killing me!You're still alive?Of course.What kind of question is that?You were vomiting blood, and that gentleman over there doesn't even have a head attached to his body.
```

### [83] hash=`316eb06588488eea`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p4`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（04廉价糖浆）

```text
That's a prop.It looks like a real one.Nicely done.You add bloody-taste substitute into the cherry syrup, which makes it smell like the real blood.Be prudent about the dosage, because it's slightly addictive.You've used too much.What on earth is happening?This is a theater, or a filming site.These young people are busy with their business while we just interrupted them.I'm Anne.Are you two the actress Jennifer recruited?
```

### [84] hash=`44a359998ebf52a4`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p4`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（04廉价糖浆）

```text
I'm afraid I don't know this Jennifer you're referring to.My bad.She sometimes goes by the name Blonnie.It was just me who always calls her Jennifer.Fucking dammit!There's no way we can use this take!Here she comes!Sorry, excuse me.Fartin.No!Asking!Huh?Are you asking me?I am Horapedia, and you are, hmm, the big one, the athlete, the smaller one, the fool,and the slim one, the scholar, and the only girl who's standing here, the virgin.
```

### [85] hash=`14ead847d38a295d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p4`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（04廉价糖浆）

```text
It seems like the first girl who laid down.I'm talking about you, uh, ahem, right, a blondie.Who the hell you are, why you were here, and what do you break into my film site for?Film?We were in the middle of shooting a movie.A horror movie.Jennifer is our dir...dir...director?Playwright.Is that the word?Horror movie?Here?Where is your gear?What's the story?What's your business here?What?Aren't you confident enough?
```

### [86] hash=`c4e6ee884ba5f26b`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p4`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（04廉价糖浆）

```text
The gear is right here!In the script too!Take a good look at it, smartass!Recorder CCD TR57?The latest version!A pretty one.It costs quite a lot and hasmany features.Optical camouflage outer shell, long standby time for operatingindependently, and hand gesture triggered flashlights and lightingadjustments.Wow!It's the first time to see a real one other than thoseadvertisements printed on magazines.

What a coincidence!How do you use the
```

### [87] hash=`185cdda46cd588eb`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
Besides, we need to offer an explanation to that lady.Of course.Why are you all staring at me?Do I have something on my face or my clothes?Roll films are ruined, too!There, there, Jennifer.I can try piecing it together and fix it for you.Would it help you to feel better?It's no use!Everything in it is gone, every take I took!Yeah, like what Anne said, don't be sad.Thanks to your generosity.None of us were injured
```

### [88] hash=`2d3b6da6c9afb8b8`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
Did you just say I'm trying to comfort you don't clear at meActually, I think this is unnecessary, but they made me behind me the girl with a hat and the girl in the whiteNecessary you think it's unnecessaryDo you have even the slightest idea of what you have destroyed make your four eyes useful and look at theseWhat do you think they are?Alright, calm down.Let's be reasonable.If you were mad because of your movie, I am really sorry.
```

### [89] hash=`c7d0d42a83c76b2d`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
But at that very moment, I thought our safety mattered the most.Also, I have good news for you.This recorder is meant for taking daily family videos.The clips taken by it aren't nearly enough to be called a movie.So, to some extent, I just prevented you from shooting a disastrous movie.If you are looking for any financial compensation, please talk to the girl with the hat.Reaching over some movies?
```

### [90] hash=`0cc32cbe4ad8cdb8`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
I don't care about this stupid shit at all!You think money can get you out of trouble?It doesn't even come close!Collaboration products of Recorder and Lugas!You can only find three of these all over the world, only three!It's more valuable than any jewelry or luxury handbags!Way decoration on it alone can buy 200 of your stupid head, dumbass!Make up you stinking there for go clean the broken trunks and bridges off the path
```

### [91] hash=`d0cf43d45644e50f`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
We have to get back to the cabin as soon as possible.I've no desire to catch a cold in the rainThis is not a safe place for you get back to the town find a hotel and take a hot showerMy students and I will escort you to the main road at the edge of the woods and arrange a car for youIf any of you have symptoms like an itchy throat or rising temperaturePlease buy some Ropitussin or a similar drug at the nearest pharmacy as long as you take care of that big monster
```

### [92] hash=`c8590b721146a048`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
I can continue with my project to get that stupid shit movie done.We don't have the cameracameraCamera you dumb girlYou have no idea what we are doing here.So don't tell me what to do with the bestYou could do is handcraft some prop staying here is really not a wise choice for youIt is very dangerous, and you can't protect yourselves.You have the right to stay here!You can't just expec-You are, of course, entitled the right to stay, Miss Blonnie.
```

### [93] hash=`3885eb72eb218985`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p5`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（05嘶吼明星）

```text
But I hope you could keep in mind that you and your friends are in grave danger.The Green Lake campsite is not a place for fun.You should stay with us, for the sake of your safety.The rain is getting heavier.We might catch a cold.Let's clean up the road and head for the shelter.all this gibberish to scare us off come here Freddie go into the camp site andsee if you can find some access for us kids if you find any teeth please pick

them up and hand them to me Freddie I'm freezing
```

### [94] hash=`ac6d7be3984992cd`

- lang：`en`｜version：`1.2`｜arc：`绿湖噩梦`
- doc：`BV1Vp4y15759_p6`
- title：《重返未来：1999》1.2版本「绿湖噩梦」全剧情 - Reverse: 1999｜4K（06林中小屋）

```text
The lock has been broken.Those are bite marks from small critters.They might have nested inside.This damn place has power supply?Who'll pay for the bill?Maybe it has underground cables, or it's powered by some generation sets left by Xeno.Wait.Stop here.To your right, by the corner of the stairway, there are three...No, at least three of them.They're getting closer!Blondie, take your friends away!
```

