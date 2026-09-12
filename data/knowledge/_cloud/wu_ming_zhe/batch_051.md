# 剧情图谱抽取 · batch 051

- 角色：`wu_ming_zhe`
- 批次：**51** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.0」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_051.jsonl`

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

### [0] hash=`b10660d6e0b7d67a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Sticky, swampy, and dark, welcome to the Nihility, you nasty, curious Pandora.You might be in an ocean, a well, the base of a ring finger, whatever.After the frantic invitation, you are rewarded some mold-like bruises on your legs.The paramecia think this gift will freak you out.But for you, the invisible wounds are much more severe.Don't worry, they are not gentle at all.Neither are you benign.Group of people in gowns.
```

### [1] hash=`39a2f51a3cc148e8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Their gowns are made of white polyester and are over knee-length.There are seven, namely number one to number seven.Probably only those odd-number guys are here.Or maybe number four, or sixes, with them, dammit I don't care.What matters is that your classmate is among them.No, not the gentle and loyal one who always stands by your side.It is the other one.The one with a clean cut and indifferent edge that feels like a refined machine.
```

### [2] hash=`d90fb2d963fa20c8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Never mind her given name, just take a glance at her glorious family name.Like sherry cask whiskies to the alcoholic.Upman cedar-aged robusto Cameroons to smokers.And the Mesmers to the arcanists.Dumbass.Love your humor.Yeah, you're right.Boo!Long ago.Long, long ago.You might have had the chance to experience such a period.When humans chose to live without prayers.then Laplace started to cooperate with them.
```

### [3] hash=`d0ddcf939f7e505a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Oh, as they call themselves.Theysuffocate the flame of awareness.They help your free-falling to the bottom ofthe abyss.Like this.It's really hard finding an Arcanist who can freelymaster such skill.As you know, scarcity causes tragedy.That was the start ofThe Mesmers are merciful and professional.They welcome every patient to treat their disorder.By then, you should realize the wrapping paper was never protecting the sandwich.
```

### [4] hash=`73bac7300eb15842`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
But the hand, the mustard from an unknown bottle, the squeezed meatloaf, and rustylettuce leaf, all were crushed and fell out from between the bread.Void, foul and raspy screaming, this filth contaminated the little girl's hands and corruptedthe white polyester.It is indeed a good time for silence.Now you've noticed those exposed wounds on the machine, those marks from repeatedwashing and adjustments.
```

### [5] hash=`2bedd05d1ce740eb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Well, the Traumata from childhood is usually hard to forget.Take your suitcase.Now it's time.Get lost.The light sheds in and fills half of the room.Amazing.Now you fall in love with the guardhouse.Let me take another can of beer.Congratulations.You are mad or artistic.Either of them deserves celebration.You are really a master.I'm sure you can't wait to explainwhy Donald Judd didn't name his boxes.
```

### [6] hash=`bc2475cd69394efd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
All of these were the doings of therational brain of humans.Philosophy intertwines with aesthetics, and togetherthey stagger ahead till today.Till the past, complexity replaced simplicity.Civilization vanished another civilization.Suddenly, one day, when theySuch behavior is as gentle as your new stepmother.Within years, continuous subtraction will finally cover the whole planet with trees again.Monkeys will then eat the fruits to a brand new future.
```

### [7] hash=`3b4c69a7280d3e53`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
You dumbass.Discolored grotto with burnt and brittle edges.Such meticulous preservation still failed to prevent its fate from being eroded by time.your memory.The two pigtail braids fall on the side of her cheek.The eyes behind that pair ofblack framed glasses are as deep posed as a deer's.A memoration for international students atImperial College London.Nineteen something to nineteen something.A line of elegant writing
```

### [8] hash=`eebf7015064de409`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
with a hint of bronzing.All the critical information is here.I mean, this is good news.Nowadays, the year is no longer important.The East, a vast land to the west coast of the Pacific.The ferry she took once crossed the Strait of Gibraltar and the Suez Canal.Watch your word, you little badass.This is not a bedtime story and I am not your sweet grandfather.You know her, but you're not a close acquaintance of hers.
```

### [9] hash=`c52fc0344851bb15`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Neither am I.There is someone else who knows her well.She has cut her hair short now, like a drop of dew on the lily petal, shaking underneaththe calyx.Here, technically speaking, her initial destination was not here, not this gray and white building,nor under the umbrella, nor the calyx.She is an expert at theoretical physics and studies string theory.a soccer bet or the day after tomorrow lose it all back into the crowd understand i can feel the
```

### [10] hash=`f49457fc6eb88dbb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
desire and depression burning deep inside your brain you are longing to be a part of an absurdbroken bizarre arcanum story which is beyond your imagination and past experienceBut sorry, I can't help but laugh.You got into some trouble and have to run around blindly among those in white robes like a panic ant.Come on, close your eyes.Imagine inside a TV with static noise.A red-nosed bad guy opens his arms to you and says,
```

### [11] hash=`02775a0412a3210d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Welcome to the human world.I know, dude.Just as confusing as the big shots at a podium.They stand there with a mic in their hands.Their uvula would tremble before they speak.Hello, hello.Testing, testing.Three, two, one.Comma, comma, comma.Everyone has to wait for what will happen with a full bladder empty stomach.Listen, this is not just a world of Arcanists.Arcanists, Arcanum creatures, and even Arcanum itself are but insignificant existence hidden beneath all else.
```

### [12] hash=`09fd0b948632e0f5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
You must learn about those who are in power at the present moment.They live on the other side of the earth, setting rules on the thrones in the scarcely populated wilderness.On the contrary, it's a boring documentary about those in power standing between thesky and the earth, seeking the real meaning of fairness and ideals.There's still plenty of time, go ahead, keep moving, but don't jump to any conclusion.
```

### [13] hash=`715c289e0f8e4822`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Just make sure you're always on the way, so you will learn more about humans.More and more.In this lonely, whirling, dark universe, I'm the only one who was willing to tell you all these stories on the cold bench in the park.You haven't met him yet.Actually, only few have, as the opportunities are always fleeting like the falling stars.But it's okay.The Foundation still works well without him.Our responsible Constantine, working without any complaint like an unbreakable lily, is
```

### [14] hash=`6c7bc2007c5158b1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
trying hard to change the Foundation's direction to what she believes to be correct.Come on, let's look at the bigger picture.The brilliant folds in the human brains tell them they need the powers to separate andcontrol each other, and bang, there come the committee, the House of the Integratus,and many other administration departments.The House of the Integratus and the Committee are in charge of lawmaking.
```

### [15] hash=`bcfcf959b8744398`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Not just in the Foundation, but in countries and even in the global society.Those eyes behind the thick fancy reading glasses review whatever has something todo with the relationship between humans and arcanists.The Committee has the right to approve or reject the proposals from delegates.Well, of course, some of the delegates are very stubborn.They will keep submitting their proposals again and again, no matter how many times it has been rejected.
```

### [16] hash=`75ece770ca8c1830`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Just like a Shrike trying to protect the fledglings until it's beat dead.When it comes to the formal debate, you will get to watch a dogfight full of the essence of modern civilization.Everyone, including the President, the delegates, the parties, and the expert groups becomes a maniac in the arena of power.After this stage, the final result depends on the White Marble House.They seldom express their opinions, but they will, sometimes.
```

### [17] hash=`fe53b8bbfe476db6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Oh yes, yes.Look how polite you are when you ask that question.Like I'm some high school student working part-time in a mall selling local socks to you.And I'd be very nice and tell you, of course, we must not ignore the other administration departments of the foundation.As well as the headquarters poor branches located in different countries.And the humanitarian school of primary defense of mankind.
```

### [18] hash=`045b90e899a19c16`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
easily like telling the difference between cake layers is a mess listen upit drifts along the chaotic swirl between order and disorder enticingcountless idealists and realists to come over storm exacerbates the chaosthose are canists who were snorkeling are now surfacing you see miss Z is auntil you break a huge entity into small groups, as small as possible.That's when they are able to clean the vomit on the living room floor effectively and emotionlessly.
```

### [19] hash=`bec383f66691e43d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Yes, an imitation show.A ball imitation show, little thing.You're imitating the Messiah, while I'm imitating an orange ball made of plastic,being pushed back and forth by two rackets.I have nowhere else to go.Once they apply a force on me, I can't help bouncing to the sky.You can see how the air flows across my dry, wrinkled skin.Oh, what a coincidence.Aren't you in the same situation as mine now?
```

### [20] hash=`a5bd078dc3d44096`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Look at your frowning face.Your face wrinkles from the eyebrows to the nose tip.Hahaha!Yes, sure.Complicated and enchanting.Use your silly and smart head to think about this ballgame carefully.The complex scoring rules, the harsh requirements for reactive agility, the countless possible foul points.Your fingers, your wrists and arms, a correct way of using them will lead to victory.Human like, a standard human.
```

### [21] hash=`dc6ecb2dda50e34c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
Grave looking, rational thinking, efficient acting.She was digging in the files, and the only touch of bright color on her was across her neck.A blue polka dot scarf, tied in the French way.The scarf was there to cover up a nevus on her skin.A lonely dark spot that lacks a symmetric counterpart on the other side of the neck.Thirteen Arcanist high school students attacked the crowd during the nighttime celebration.
```

### [22] hash=`a0140f20ce557bec`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
They claimed the oracle had uttered to them, from the inside of a gigantic Cordia Elianoides,that they had to shoulder the responsibility to protect the people.So they took their wands and knives, carried bottles of potion of concocted picric acidand Nitrosylose, and walked into the festival market like any regular happy young people.Their attack led to 17 deaths, 6 were injured, among which 4 were disabled for life.
```

### [23] hash=`39dcc20c6afa58b0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
One young girl among the attackers couldn't physiologically stop her hysterical laughter.Even when she was under arrest, she quivered convulsively, with her hands twitching tightlyHysteria, madness, paranoia, hearing voices or seeing things, these abnormalities are the sparks flying in the air, and our canists are like dry cotton.The encounter of the two will cause a fire.Paulina complained quietly.
```

### [24] hash=`30abe065ccd42ca2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
She accused the danger of fire the risk of heat.One can hardly hold no grudges against the flame.Racist thoughts crept silently into her blonde-haired beautiful head, like a cunning centipede.Fortunately, this is not yet the end of the story.Paulina still had her chances to change.Change, yes.An alteration.Everybody has to change.You can improve your living standards, pay for prettier white clothes,
```

### [25] hash=`3988c574674eee18`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
You pick it hard, just to locate and take out the hardest, largest booger that irritatesyour nasal membranes to stop the endless sneezing.The change of Paulina started from a question.A senior staff of the Foundation walked to her, flipping through the pages of thesame folder and asked,But Paulina, how are you going to deal with the fire?On the next page, the survivors started a new life under the supportive measures, and
```

### [26] hash=`dc2932d4a64376ed`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
the crazy children have left their poor family, leaving the violence and harassment behindand moved into a sanatorium with white walls.The record of the follow-up visits showed that they have stayed mentally stable since.They learned to calm themselves and overcame drug addiction and alcohol abuse.Some of them were even married.Between the last two pages, there lies a thank you letter.The name signed at the end of the letter went on for two lines, and the last name ends
```

### [27] hash=`b902c506ea81d87e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
with a cheerful strike going up, like a smiley face.The fire is always there, Paulina.We need to find a way to live with it, not to extinguish it.Keep them somewhere safe, like a high shelf, and away from the fuel.Watch over the temperature.Maybe teach them to burn in a manner that no one, including themselves, would be hurt.Division and confrontation have never taken this world to a better place, have they?
```

### [28] hash=`74a81f0c6cbd38c6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
They went on talking for a bit more.About the responsibilities of this job.About personal liabilities.About hatred.Their name won't be listed in the cast at the end of the movie, not even a poor St.PavlovSquad Leader A.They're a bunch of people.A bunch of people just like you, though there are still differences between you and them.Open their bellies and you can find everything that should be there.
```

### [29] hash=`f9c330838d1430a9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
The liver, the stomach, the spleen, the lungs, and the heart.Their faces are clear to be seen.Look at them carefully.Carefully.You might have met one or two of them.They come from the same institution as yours.The Saint Pavlov Foundation.From the France branch.La from the Egypt branch.And the Matryoshka from the Russia branch.Your ugly trauma, a mixture of your mental issues and miserable past, would burst out
```

### [30] hash=`5a7e722286700a5d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
in the next second, making everyone's heart twitch.But think otherwise.If the truth were known to all, today's not real and there's no tomorrow.I'm going to eat my shoes and an asteroid is falling, then all of them would go crazy.And then, you may start contemplating.Should they all go aboard the Ark?Can this Ark carry this many people?Try to raise the question as peacefully and slowly as you can.
```

### [31] hash=`fa78cea9f6f6a9e9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p12`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】主线小径补充剧情）

```text
And their enthusiasm will be dampened.And let out a sound like what you hear when you pour water into a heated pan.Their feelings.They.You mean Eve, Law and the Matryoshka.garbage there is under the stage.There may be liquid seeping out of rotten pastry and dairy products, intrusions of Americancockroach, with sleek abdomen crawling everywhere.Who can say it's not a blessing to know nothing about the truth?

Especially when you can't leave this shitty place.Ha ha ha ha ha ha ha ha!
```

### [32] hash=`3e3379996f143830`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
It's raining, no it is not, it's the storm, the storm is coming.Are you feeling seasick?Open your eyes followers, it's 12 at noon and The Rockin' Apple is welcoming the most unwelcome visitors.On hold of you, a public hearing, you stalkers, stalking me, the pirate for days,can be shocked away by the rock and rolling coasters night and day.Now, listen to Radio Apple.Come with me.Let's count down to ecstasy.
```

### [33] hash=`994dacea8182f51c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Three, two, one.Say your names, you British government stooges.Say your names, you Manus vindictae robbers.You banned music.You robbed traders.Our lips are sealed and we wandered, but nothing gonna change our love for freedom ever!There is a huge black ship behind us.We are under attack.Please be ready to abandon the ship, my captain.I'll hand you over, but please don't break my ship!My records and my treasures!
```

### [34] hash=`f30ad1fa681d2d4a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
No violence!Say something if you can hear me!Hey!We don't know them.We've tried to tell you.We're the investigators from the Foundation.You've got the wrong people.Regulus' ship was sunk.Landed.Good.They landed safely.The Riders are still after them.If it goes on like this...My apologies, timekeeper.Are you feeling better now?This is Battersea Park.Chelsea is across the river.I sent the backup request without authorization, and you were teleported here.
```

### [35] hash=`150bf28299e24285`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
It was too rushed.The ritual was not ready, and you fell into a coma.But it's an emergency.Please allow me to report and ask for backup.Go ahead, please.The day before yesterday, we were resisted when registering Regulus in.Our teammates were also taken by her.The bad news is that Manus Vindicte is onto her now.We must rescue our teammates, complete the mission before the storm, and return to the research center.
```

### [36] hash=`3f20532cf469320c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
I'm not like you, and you know that well.I haven't been trained systematically for the Battle of Arcanum, my classmate.Don't have to fight, Ms.Furtin.Please just guide me by my side.You are the most perceptive person I have ever seen in terms of Arcanum.And what's more, I heard that.Within 24 hours before the storm, we could ask you for help if we have any problems.Is that right, Timekeeper?This is what it says in the field mission evacuation instructions.
```

### [37] hash=`9a16ecf791b82429`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
You are a careful reader.I'll help you out, don't worry.Fifty minutes left.Come on, let's movePlease use this it will send us directly to the other sidethis is aPortable floppy disk for the arcane skill teleport.I use it just now to send youIt's still under experiment.So it is not stable.Madam Z only gave me threeBut if everything goes well, it will save us much timeThink of the destination name it in the vision then the ritual of teleport will start
```

### [38] hash=`8737ec8b139bcb0b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
There are too many of them.I can't hang on anymore.What's your status?The way is blocked.I'm still trying to break it through.Can we go back?Before the storm?Sugar sugar!I saved money for five years, my beloved apple!And the tape scan driver I just bought yesterday!All thanks to the bottom!If I weren't protecting the records, I would have been able to beat you all!Don't be smug!My pink windmill, my John Thunderfinger's live show!
```

### [39] hash=`6d87fbc09ca35a74`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
I'm gonna kill you!Captain, what's your six?Enemy at your one, now.Who's there?The Incantation, is it?It's the captain!Yes, our captain's here!Captain, how did you do that?You stopped the enemy just in time!Nothing special.All thanks to Timekeeper's help.Predict enemies' move while teleporting.Timekeeper, you seem to be more perceptive than before.You are...our Timekeeper?To meet you, which means the storm is coming soon.
```

### [40] hash=`4e810ee9679b5bc9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Indeed.You still have 45 minutes.I'll do my best to help before the storm.Now, everyone, get ready to break through.Regulus, you're doing this too.Huh?Since you saved the pirate, I'll do this.Sonnetto, assist me, please.The breach is behind us.The alley towards King's Road.Ryan City.Left hands up!We broke out of the enemy's encirclement.Thank you for your decisiveness, timekeeper.We are distanced from them for now.
```

### [41] hash=`3ec13549da5bacd3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Captain, are there any teleport floppy disks left?We have to go now.This is the last one.Let's take Regulus back.Huh?Where are we going?Please do not get me wrong.We will not do anything against you.We are investigators from Sympath Love Foundation.As far as I know, you have not registered for the Arcanum license.Unauthorized use of Arcanum is a violation of the public security law.Please cooperate with our investigation and registration.
```

### [42] hash=`8f5201b2457b7aae`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Just come back with us to the research center, and as quickly as possible.Am I...recruited?Fine, it's okay to go with you, but could you show me the floppy disk first?Sure, no problem.Wow, so the incantation can really be recorded and read.A floppy disk to store advanced arcane skills.So cool!You were very serious.If you really want to thank me, just take a copy of the times.See, it's all good news on the first two pages.
```

### [43] hash=`343a5c23ac2dc0e8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Only comes along every once in a thousand years, eh?Please give me a copy.Do you like the world outside, Sonnetto?No, I'm just, I'm just curious.I will throw it away when I finish it.Please don't take it to heart.That voice!Timekeeper, look at that table!Yummy!Mmm, so yummy!More El Grey with brown sugar, please!The optical arcane's killed to be invisible.Now I understand.It blew into the building.
```

### [44] hash=`823a26c6d40164b1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
What?Regulus, will you cooperate or not?Please answer me.Your foundation is just an authority working with governments.If I register in my location will be exposed anywhere any time.I'm not doing itMay the peace be with usSo you sabotage my arcane skills who cares I'll just go invisible againNo weakness will give me away this time.Catch me if you canWell time to change my strategy, please guide me
```

### [45] hash=`305d733260d3c05e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
If that's what you got, this pirate will not be caught.You better listen up.Time to rock your world.Are you ready to shake?Do not worry, Timekeeper.I now have enough moxie.I can see further and hear better.I can now summon a stronger ritual capable of unveiling the useless facades.Turn your eyes on me and listen to my incantation.Witness my ultimate.Detect the world I have never seen before.this seems pretty dangerous do not worry timekeeper i will keep things in check each moment now night
```

### [46] hash=`b1fe613eefef6dbb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
i have not taken my best shot please stand up and continue to fight with meshe doesn't look right she's pale i'll go check what are you doing it's the misty bubblegumyou know how to use it right i need your help before that i'll help you out i'll see you inbookstore on Oxford Street.Now push me.Timekeeper!Close your eyes.It's my mistake, but it shouldbe fine.The time of Misty Bubble Ball is limited, so she must still be in this block.
```

### [47] hash=`4c036085e7edcd78`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Seneta, are you still searching?The storm is coming.If you don't go back now, it'llbe too late.Let me search these stores again.Whoa, you freaked me out!Did weSay the Bookstore?Exactly.Isn't it the Bookstore?The unimproved Misty Bubble Ball has a special scent.Sonnettowill be here any minute.So, so what do you want from me?Poor me!Relax.I'm not going to take you to the Foundation.I ask you to go somewhere safe
```

### [48] hash=`02eec1e10dcac8a5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
with me.Regulus.I need you to...brave the storm with me.Brave the storm?She's here.on your end I'm sorry you shook your head that means my mission faileddon't begin I have to go back thank you very much for your support timekeeperdoes if nothing happened are my eyes pecks on me your own eyes the end of anera and you survived you've braved the storm my experiment succeeded thanks forThis is Marion Smith, a single mother.
```

### [49] hash=`3ca01bc8becdb0e4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
She was worried if she could afford their lunch for the weekend,but still couldn't give up her dream of being a writer.I met her in a snack bar at 2am.Her one act play about the Transantartica Expedition was a real masterpiece.This is Julie, who once invited me to her house.Her bedroom wall was full of Rivaldo posters.The FIFA World Player of the Year, who then became the mass idol.backwards so the people in the photo people like me where are they now are
```

### [50] hash=`d6e5aac297c3ef5d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
they all reversed in a storm us now maybe I never met them again before youI've done so many experiments in an accident I realized that my suitcaseseemed to be able to cut the storm out it can preserve the traces of thelast era like these photos so I tried to put newspapers mushroomsmy polusies into the case.They all succeeded.However, when it comes to the friends I made inthe last era, I failed.It doesn't work on ordinary people.
```

### [51] hash=`0cd87dbf242635c3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
Maybe I should just record the time andspend no feelings on what I see, as the Foundation asked me to do.But why are we?Because we couldsee the mutation of the world, the weird things before the storm had left deep impressions onApple.I think so.When you were sailing out at sea on the radio, Regulus hadcried out, shout it to the full moon.It was the beginning of the month so it'simpossible to have a full moon in the sky.
```

### [52] hash=`4c032eddd950d905`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p1`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】序章.此即明日）

```text
The real moon was to the west ofyou.There were two moons that night.There is someone that can see what Isee in this world.So I decided to try it again for the last time.Is that anMr.Apple, could you please give Vertin a hand?I need to really think about it.The things you said.
```

### [53] hash=`5de4b57d1ea64ef6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
She knows dark magic!Run!This is my suitcase.Please give it back to me.Touch me!I'm going to give it to the officer.Damn basilisk losers!When a pirate meets robbers,robbing is not a good behaviour that you kids should learn.Sero, Rob!Oh!Looks like the generation we met is not quite friendly.If they shake the suitcase like this,Regulus will probably fall apart.Mr.Apple, I need your help.My pleasure.
```

### [54] hash=`63b7088dcb319612`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
This apple will shed some light on justice for them.Well, it won't violate the Declaration of the Rights of the Child.Hide it in the tree hole this time.It shouldn't be that easy to be found.The situation of the Arcanists forty years ago looked much worse than ours.At least we can still talk to the human.The subculture movement has indeed changed the social status of some Arcanists.While in the 1920s, there are still many injustices.
```

### [55] hash=`5bf7e9583ca14c0d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Mr Apple, how long will it take for the suitcase to be completely invisible?30 minutes.This Apple is still waiting for the right solar altitude.You can meet with Regulus first.This Apple is afraid that in order to have some fun, she might...In order to relieve the boredom, she might make you troubles.Regulus!Limekeeper?I'm thinking about how to find you.May I ask where is this place?Use the advanced arcane skill, Aferoi around number 000262603100008 to send me over?
```

### [56] hash=`8ec522a52040acc0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
No, it should not be this.Senetto?Why a- is it because I touched that line?Regulus?Adam Z is right, she said Regulus was with you.What?Regulus...she...you sleep...I'm also...a bit like...Why did you all black out?What happened?I don't seem to be affected.I should come back and check again later.Miss Vertin, they all wake up.However, Seneto found Regulus immediately.They're at a standoff in the lobby.
```

### [57] hash=`58038a5d83450bc7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
I'm coming.You are awake.How do you feel?Any discomfort?timekeeper you made it I heard that you caught no you gained the trust ofregulus when I returned to the research center the committee informed me thatregulus would join the foundation as our colleague I am here to convey thecommittee's commendation and your next mission I did not expect that youwould just summon me in the future if possible I hope you could show me the
```

### [58] hash=`9bf9175cd2c14dc1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
incantation I would also like to learn it regulus we're very glad toHowever, you need to go to the Foundation and the Scientific Computing Center first to complete the registration process.As an Arcanist Talent rated S, we will provide you with the best equipment for scientific research.Congratulations for what?Wasn't the deal we made?Institution, Vertin told me, is a place where the storm can be avoided.
```

### [59] hash=`5ccf60ba520b09d0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Free use of arcane skills is guaranteed, and Dr.Pepper is even free for 365 days.Exactly.If it is a place full of serious old men, Regulus must not be interested in it.Sorry for this Apple's interruption.The Foundation is definitely not a place for serious old men.That's where Vertan and I grew up.And there are many other people like us.People who stand there.You, Miss Sinetto, could be so panicked.
```

### [60] hash=`38c11034e58c39da`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Well, at least the Foundation is not that horrible as all.I should have more training.Let me explain.Regulus, Apple, what I invited you to join before is the St.Pavlov Foundation.As for Dr.Pepper, I think Sanetto will find a way.I will definitely make an application to the administration.For the sake of 365 days of free drink, I'll join you.It shouldn't take too long to go through the procedures, right?
```

### [61] hash=`631370aa2fa7f7ab`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
I've got a bunch of belongings to pack up.Bertin?You?I'm sorry.Turns out the Foundation doesn't fully trust you, just like you don't trust them.You acted privately without their knowledge, but they were still able to foresee the outcome.If you don't mind, please tell us the stories from the past.After all, that's where our captain is leaving for.The Foundation is currently the charity that can provide the best treatment for Arcanists.
```

### [62] hash=`8394a8b7484dfc86`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
There is no doubt about it.Every few years, the Foundation selects talented Arcanists from children around the world.They go to orphanages and admonition centres and even fish out unique ones from the prisons and detention centres.I was also one of them.Since I can remember, I know it very well that I am alone.Until 1999, when the first storm came, I seemed to see my mother.So you have a mother?I was not sure.
```

### [63] hash=`7e44fd77e0d985c0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
All of us.Our memories of 1999 are blurred.I know what you said to Sonnetto just now is expedient.I can still help you get out of here.Never mind.Think about it.If they can detect the whereabouts of the first one, then of course they can find the second and third.In that case, it never ends, does it?You can't send all your partners away.So you mean?Hmph.I won't lose anything to go with you.Just don't forget the great kindness of the pirate.
```

### [64] hash=`b9a6b85e1c044714`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Anyway, I've considered carefully.In this world, the storm never stops.How could realfreedom exist?Since I would be inevitably reversed wherever I go, get to the Foundationand investigate.By the way, you've got the best research devices.Wow.It's gonna beso much fun.I have a lot of little things to study.I see.In that case, this apple respects the captain's decision.In the currentvolatile situation, it is also more beneficial for us to join the official
```

### [65] hash=`8fb937d07b8bf84a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
institution.The Foundation and we, after all, are not on the opposite sides inthe first place.Since you told me about the storm, I'm more or less excited.Then come back as soon as you finish the registration.The Foundation isnew arcane-ness for the foundation as much as possible.I see.The forces of the Manus expand dramatically year by year.To stop the trend, we do need additional manpower.Seneto, did you have oranges just now?
```

### [66] hash=`8dd2cc6ab7b8e266`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
There is a scent of orange on the capsule.I did not, and I will definitely wash my hands after eating.Maybe that's my mistake.If there is no question, we are ready to go.What it isRegulus's voiceWhy is her voice coming from above?whoaMiss verton senatoSeems like our suitcase has disturbed some imps captain went out to check but got trappedHang in there even the tree hole is not safe enoughWe should go.
```

### [67] hash=`a1833e68c0463056`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
I will carry it with me along the waybutRegulusHmm.What's that worried look?Come on, Sinetto gave me a floppy disk.I'll reach the quarter 100% safe.Well, that's a fight.I gotta split then.This is a free trip.I'll definitely enjoy myself.Let's get ready to move.The mission is in the underground parking at 2122 Lincoln Park Street, two blocks away from us.We still have plenty of time.Could we go there by bus?
```

### [68] hash=`b27aa2405a7d58a8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
It's so cold here.This apple is getting frosty.Really?I seem to feel nothing.It's actually kind of warm compared to our routine training at low temperatures.According to the intelligence, now it's still one hour before the incident.Hmm...So this is the distance from the entrance to the wall, and here should also be marked...What you're depicting in the air, is that the reconstruction of the victim's position?
```

### [69] hash=`1fa822874735bf39`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Yes, I reconstructed to actual scale.In this way, I can calculate the position that can provide cover without hindering us from joining the battle in time.For anything that may cost others' lives, I want to be as cautious as possible.What if...No, nevermind.I'm not worried about my own life.I'm just...It's fine.I won't know.Someone's here.Two human drunks.Don't let them wander around.It's too dangerous here.
```

### [70] hash=`b0589bcef69ef3bb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
The gang fight will definitely hurt them.How's it going?Skin damage.Less than or equal to 5mm.No visceral damage or Psycube fluctuation found for the movement.Conclusion.The injuries meet the requirements of Emergency Defense Code of St.Pavlov Foundation.It will probably take some time for them to wake up.Hide them under the car first.We don't have much time.Let's hurry up to the hidden position.Mr.
```

### [71] hash=`29ec764903806caa`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Apple, why are you a little upset?"This apple found a pack of sharp odontists in their pocket, and a child's finger,which are the currencies that are only used by arcaneists.It's just...It's 1929, a year full of racial discrimination.This is also the reason why we need to stop the next tragedy.For the peace of all mankind.There's still 30 minutes.Who's coming early?Gunshots?But the Arcanists haven't got here.
```

### [72] hash=`7e28ee63d72c7f11`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Damn it.Let's go.This is very-Killing them!Can the Arcanists?Aren't you also here for these, Miss Governors?Who know history very well.So, next on the lead is...Adam here.Why can't I shoot her?!Why?!Timekeeper!Be careful with her gun.Seems it is not our bodies that she is aiming at.Got you.Please stand behind us.I will escort you to somewhere safe.You guys are also arcanists!Ha ha ha ha ha ha!Dry shite!
```

### [73] hash=`4a336640a2b999cb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Carotid archery ruptures.We lost him.What a pity, because the Arcanist's blood is so dirty that he would rather die than go with you.Life is precious.I do not want anyone to waste it.Those unconscious Arcanists behind you are the original victims, right?You were bringing them back to Manus Vindicte?I'm much more interesting than the stubborn old woman next to you.You're also gorgeous.OhYour hair color is quite similar to the feather.
```

### [74] hash=`443de3c3b5ad75f6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
I likeOnes my questionSargeWe are just on to the same people before the stormEveryone wants more useful guysIn that way your destiny and mineAre they now tightly connected?They're alive!You hate humans that you could kill them like that!Then tell me, this massacre in history, who should be killed, human or arcanist?Difference in talent is never and never will be the reason to deprive people of life.
```

### [75] hash=`4a2c5ee9ea278341`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Bingo, Miss Governor!Canist or mortal, I, um...Don't really think it matters.As long as we survive, it's all good.What's in the shadow?She's holding a ritual!Stop her!She's going to take those arcaneists away!I like you very much.I still have to finish my task.Is there a word for killing Adam for me?Don't forget me!That's it?She's gone?What are these?Stock gift agreement.Don't worry, I will deal with them right now.
```

### [76] hash=`74c0edc42bd95be7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p2`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜1~6）

```text
Wait, that's an address on the seal.Holly Potion Bar.The Walden.Seneto, update the result to the headquarters.Roger that.And we...Let's move on to the next destination.The Walden.It may have the answer to all the questions.
```

### [77] hash=`033df517df006104`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
It'll be our honor to have the young lady's presence at the Walden.Thanks to your kindness last time, we were able to invent the new potion before the National Prohibition Act was enacted.Of course, I will deliver what you had purposed on time.Yes, everything is fine.No, you don't have to worry too much about Congress.You need to trust them.humans they talk the talk and don't walk the walk but they're more likely to vote
```

### [78] hash=`382f3f36590bff51`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
for the side that seems more ethical please be rest assured we'll make theyoung ladies day a pleasant one it's good weather and ideal for animpressive stormon February the 5th, Duke Ellington's Jazz Orchestra will perform at the walkjust what a jazz fun should beThere you go, Miss Southerly.There's no need to deliberately read that aloud.Master in England has given you the permission to go out.Also, I've spoken to the owner of the warden on the phone.
```

### [79] hash=`bb4e4518a8b1c900`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Hooray!That's not what a young lady should say.You also have the great mission of saving people.Fine, fine.Just don't go hawking your new nutrient potions.Miss Moussin would be worried if she saw you come back disappointed.Wrong way, my lady.The car is at the front door.Bodyguard?You promised I could go out alone this time.Mind your manners, my lady.There isn't a bodyguard there for you this time.
```

### [80] hash=`df862768ad41090d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Put near the bar is quite dangerous.We must pick you up in person for peace of mind.In brief, after entering the bar, staff will lead you to your seat.Remember, watching only.No alcoholic or incited potion drinks.Do not talk to strangers.Black Bottom or Santonguero are not allowed.Hm?My lady?The woods.Don't call me.All the plants are dead.There's no evidence of life at all.Even the bark on the branches are charred.
```

### [81] hash=`705a211daa1a0c22`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Looks like it has been through a huge fire.Well, if it were not the path we must take,I really don't want to enter these woods.Speaking of which, Sinetto,have you ever heard of a ghost story about fire?No, never.Oh, so it is said that in the early 20th century,there was a devastating forest fire in Washington.Uh, Mr.Apple?Lots of unknown creatures!Senato, stay behind me!No, too many of them.We can only take one round at most, not for long.
```

### [82] hash=`0ca4cd038203e3d8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Critters keep coming from the roots.Are they living here?Coming again!Careful!I'm Keeper.Did you see my mark on the map?Yes.According to my calculation, that's the closest position to the edge of the woods.In one minute, I'll cover you to move in the opposite direction.Remember, there's a slope two miles away that can slow down the critters.Ms.Sinetto, aren't you coming with us?Surprised by such an overwhelming number, we can't get out.
```

### [83] hash=`fa49038d5584f71d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Don't worry, the action strategy would be more flexible if there's only me.As long as the enemies are not ghosts.No, even if they are ghosts, I will survive.Please trust me, just like how we used to be.Let's go, Mr.Apple.May the peace be with us.They're all coming for us.It's a good thing.Maybe we covered Seneto.As long as one of us can leave the woods,there is hope for the rest.Too late to climb up the slope.
```

### [84] hash=`7e8636ef808f8d4c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
Get ready to fight!Mr.Apple, how much longer can you hold on?Though it may not sound like what an apple should say,this apple will fight with youto the last moment.Vertin, look out!No offence.Would you please pass me my heel?It seems to have fallen into your arms.This is my promised land.I am Druvis the Third.It's my pleasure to meet you.The hills?Here you are.Then I will come down and clean up the mess.
```

### [85] hash=`623a7a1ce054a4b9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
It's fine to land there first.Tell him I don't like touching them directly, these invaders.She beats hundreds of them with one single move.Is it the power of her wand?No, the arcane circle she casted is pretty archaic.She must have a European arcane in background.It's been a long time since I saw the Arcanist visitors.Thank you for helping me expel the critters.Then, as for the ones left, just as the woods prophecy and whisper,
```

### [86] hash=`091f236bc00ac807`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
invaders, you shall offer your sacrifice for the peace.Please allow us to assist you.Finally, we are safe now.Thank you very much for your help, Miss Druvis.You ran a long way into the woods.Are you looking for the girl with orange hair?Yes.I see her get rid of the critters and take a dark green Bentley to the northwest.The woods know where the visitors go, leading them astray or to the light.And your friend, she has good fortune.
```

### [87] hash=`3a10b2ffae7442c8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
The exit on the North West?It's quite close to the Walden on the map.The Walden?Now I see.You are also here for the Storm Gathering tonight.What is the Storm Gathering?It is a gathering of elite Arcanists from all states.Besides, celebrities and frequenters familiar with the Barkeeper are also invited.I think there will be the regular jewel performances, a banquet that is too noisy, and the announcement
```

### [88] hash=`53d5d5c74b005964`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
of good news.Do you know what exactly the good news is, Miss Dreavers?My apologies, I am not interested in that, but if you want to know the good news, youmight as well take my invitation and take a look.This is a secret gathering in a speakeasy.It's by invitation only, and a stock coupon of at least $50,000 is needed.Why does it always have something to do with financial securities?We had a subscription agreement before, but it was burned by our friend.
```

### [89] hash=`810316ffb9cf3060`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
That's alright, but you can actually get here with nothing.Stock prices have reached what looks like a permanently high plateau.Have you heard about this?Today's cash is not used for transactions.The application of Arcanum has made stock exchange surprisingly convenient.The urban agglomerations expand rapidly in the new era.And even the critters have lost their home.Only loans and the infinitely soaring stock market could satisfy such a huge desire.
```

### [90] hash=`987584264783f5c4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
It is similar to the history this apple knows, but sounds a little different.This is the gift agreement for a 50,000 US dollar coupon.If you're still going to the gathering, take it with you.You're not going?Thank you for asking, but I do not want to leave the woods for now.Hello, I am your personal stockbroker.Your grantee application has been received.Application approved.Account updated.Thank you for your support to Blue Chip Stock.
```

### [91] hash=`c0603c4d3cfd5945`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
The real estate market is on fire today.Now we have customized recommendations for you.We're good, thank you.The exit of the woods is at the end of the road.Next to the Three Cypresses.I will leave you here then.May the woods bless you with fortune.And if you see the barkeeper, please send him my best regards.Lord, forget me not.You have a good day.The men I need.Have you brought them back?Seven Arcanists not even missing a single cutie finger.
```

### [92] hash=`3500872afa825791`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
They are all very interested in the doctrine of the Manus.Soon they will become your devout desperados.I did my job so perfectly.What rewards will there be for me?I heard you didn't take care of the redundancies.Our instructions to kill civilians say you, the Arcanists who are not pure-blooded, arejust worthless.And if we are from the Southern Mafia, we don't care about brotherhood.We can't be as ruthless as this storm.
```

### [93] hash=`a2508e773369e7ca`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
For the special ones, of course, we Manus will make exceptions.just like now we're still searching for your missing sister Schneider thank youfor being considerate your step-sister Marion must be extremely touched if sheknows how much you value her you were adopted by the Grecos after all it'snot like you're related to those humans by blood matter what we are familiesand I've lived together for more than 10 years thank you for caring so
```

### [94] hash=`4019ab040bf0f4bd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p3`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第一章.在我们的时代｜7~16）

```text
about Marianne, which sister is missing.Let's leave tonight.Hello, please get me Madame Zee of the Saint Pavlov Foundation committee.It's you.What's wrong?I request access to the historical intelligence on the US financial market in 1929, specificallythe date of the Wall Street stock market crash and how much Arkanin was involvedin the methods of stock exchange.Anything else?Also, I request sending backup to reinforce us for the storm gathering tonight.
```

