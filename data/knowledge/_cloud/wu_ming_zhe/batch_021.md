# 剧情图谱抽取 · batch 021

- 角色：`wu_ming_zhe`
- 批次：**21** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.9」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_021.jsonl`

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

### [0] hash=`85ccef922e693ec8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Four years have passed since you became Six, and for four years you have been hidingthings from us.The long-neglected questions have created a cloud of doubt between us, and now theThe shoulder of fate is falling on us, and we are teetering on the brink of destruction.It's time to be honest and true to your people, while you still have them.We are the seekers of truth.It is unjust to keep us from it.
```

### [1] hash=`1f49f2e5950c1324`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Let the wall of truth bear witness.I want nothing but an answer from you.I am not here to provoke untimely conflicts.Answer her, Six.You should be glad that I am not the interrogator here, because the wall would have collapsed immediately.You may lie, but the wall will fall.You may stay silent, then I will lie to break the silence and the wall.Or maybe you could outwit the wall with the liar's paradox.
```

### [2] hash=`ad09434d1c5e2aa1`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Only sadly I have tested it for you.One cannot deceive it by stating, I'm lying.After all, it's a test of morality, not logic.It needs your honesty, not your wit, or anything else.What do you wish to know?What else?The most important question, of course.The question about the essence.Why has our research stagnated for the past four years?Why did we fail to predict the emanation in 1929 and again in this time?
```

### [3] hash=`f29d5b0b7d6288ac`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Have we misunderstood the premise?What if the emanation is not a manifestation of the Transcendental Law at all?Worship as worship, thinkers think, governors govern, and researchers research.Your questions are not mine to answer, 210.A six has no expertise on the study of the emanation.I'm not qualified to answer about its essence.Your question is to abstract, 210.Don't dance around the subject, six.
```

### [4] hash=`7b57a3d1e3c0cd0e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
I watched her walk into the cave and come out unharmed.I watched her.And the previous six, bored the ship in search of answers in the phenomenal world.The ship didn't come back in time.The emanation caught them.And that was only the beginning of our misfortunes.The model failed.Our whereabouts were revealed.Hysteria now poisons the minds of our people, and the empirical knowledge accumulated overthe years suddenly no longer applies to the current situation.
```

### [5] hash=`b1018dc3b8b3f384`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Why?What did she find out?Could it be that something's happened to the transcendental law above?Has the truth we believed in changed?Hypassus discovered the secrets of Route 2 and toppled Pythagoras' School of Thought.The controversy surrounding Newton and infinitesimals presented a challenge to the groundwork of calculus.Russell's self-referential paradox sparked the third mathematical crisis.Though said theory was eventually perfected, the lessons on self-referentiality remained.
```

### [6] hash=`e27068c5a0975677`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
In the end, Gödel's incompleteness theorems showed that proving or disproving everything is impossible.Therefore, absolute knowledge is unattainable.The boulder of fate will tumble down its peak whether 37 is the one pushing it or notHowever hard Oedipus tried to defy destiny his path to tragedy remained unchangedYou're talking in riddles again.I should thank you for bringing the question here888 so I may finally speak the truth
```

### [7] hash=`f449a34eb630752d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
77 did ask about the essence of the emanationshe asked what happened to the supreme existence what plunged the world intomadness the answer was disorder and chaos blasted you knew this all alongfrom the first day of your revelation when you became six you knew that theemanation was not a manifestation of the transcendental law and patternsabove but rather a symptom of its utter disorder and chaos and you knew
```

### [8] hash=`0cfb5a69bea9cebf`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
that the transcendental realm of numbers was no more,and that the essence of Numa,the one true form we believed in,had become an ever-changing existencelike the irrational numbers?Four years.You kept this to yourself for four years.Why?Was it for a false sense of peace?To keep the island stable,did you deceive us to prevent the realizationthat our research would be in vain?It's time to halt the bickering.
```

### [9] hash=`c2e4b9da5c5102db`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Get everyone out of here now!Pray to the gods for what you are about to do, and pray that all goes well.Once familiar with this practice, you will understand the constitution of both eternal gods and mortal men.Huh?What happened?Did they not carry out the cleansing ceremony?You will know the extent of all things, the boundaries of their entirety, and what connects them together.Oh, what's going on?
```

### [10] hash=`3444978d95abe2d0`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
No, this is the large-scale ritual on this island undoing itself?You will see, as you should, that the nature of the universe flows in all things alike.Thus, you will not hope for what is beyond your reach, and you will not be deceived.Pray, my friends.Pray for yourselves, and pray for everyone.Pray for all the suffering and misery around you.Reach into the unseeable darkness and pray to the unknowable Supreme.
```

### [11] hash=`71aebcc65fc3ac7b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Speak your hopes, for you are a finite creature yearning to transcend its own existence.The determination that once helped us overcome our insignificance and touch the light of Numa should guide us once more.Where are you going?To the cave.The trial is not over.The final cleansing is yet to come.There are still duties to fulfill.Here is a well-known question you must have heard.What goes on four legs in the morning, two in the afternoon, and three in the evening?
```

### [12] hash=`93e2bc3c067b7c58`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
It's so well known that no one finds it novel anymore.But please, do me a favor and answeryourself.Correct!This is the same answer Oedipus gave to defeat Sphinx.Thusbecoming a hero, but also starting him on his ill-fated destiny.Raise a question,give an answer.This is the most fundamental ritual.Through this we getnearer to God.Yes, a ritual.Whether it is by pouring out wine, slaughtering amore from a man of your size.
```

### [13] hash=`94647e929aec4e0b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
For God's sake, Regulus, keep an eye on your first mate here.Wow, he's so out of it right now.It appears that thisapple's abstinence from the bottle will have to begin anew.Vertin, we have a big announcement to make.Neo's just completed her proof.Care to wager on that?I'd say she's a multiple of three.Then I'd say she is a multiple of 139.I have to admit, she has a good number.Number 100 times better than me, and 210 put together.
```

### [14] hash=`6f2d4124474e7d81`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Calculating, 37 plus 6 plus 210 times 100 equals 2.Oh no, she is not 25,300.I doubt anyone could live with themselves with a number that long.You haven't bed before.This is Amu, my white rooster.Amu, this is Burton.White rooster?Something's not right.None of this is right.Something's happened on the island.I must still be in the cave.Out of here.Critters eating beans and a white rooster.These are supposed to be taboos on the island.
```

### [15] hash=`49f163f368a489ce`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Is this an illusion brought on by the fog?Something like this could never hold up to skepticism.Mankind is slow in learning new ideas.They need new information to be explained in simple terms, using examples and analogies,or reduced to its most basic symbols and generalizations.Eventually, once they've gotten used to the formulas and outlines,collection of our pastsBut is who we are a measure of our decisions or have our decisions been decided for us long before the moment happens?
```

### [16] hash=`b8fd725b3ef9945d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
We are led by our senses as they in turn are led by our experiences like puppets on a stringOn my two people decide to put milk and sugar in their coffee for the tasteOr is it bitterness?That sharp sense on the tongue that tells them it must be sweetened.Do they even like coffee?Or is it a memory of kneading it to make it through the day?Each decision we make coming from a tug on our hidden strings.
```

### [17] hash=`d6035408355a6ac7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Strings we cannot begin to grasp for ourselves.Only by taking out these saccharine sweeteners can we know what we really drink.Kneading!You'll have to leave from the left.Why not simplify our definitions?To learn about the world like we were kids once more.Let's begin with math.Could it be as mutable as left and right?Could there be a hidden integer between 3 and 4?Is 1 always 1?Or is it just our frame of reference?
```

### [18] hash=`fbb5070bd8357d36`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
But where is it, then, this everlasting truth?Have you ever seen it?Have you basked in its radiance before?Maybe the shadows on the cave wall are our true reality.Maybe the sun is just another prop in our shadow theater.What if the people who chose to stay in the cave were the ones who were truly wise?Be careful what you hold to be true, darling.Timekeeper, are you leaving the banquet?Perhaps we might go somewhere quiet.
```

### [19] hash=`1dda7c9f62813b77`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
I wanted to speak with you about linear regression.Terribly sorry, Senato.I really must be leaving.and peace will not return until one side concedes, even if they are blameless.Doesn't that seem unfair?There's no other way.How decisive young people can be.You don't stop to ask who ought to take the blame,or if it is right that the innocent concede to the guilty.You only want peace and damned be the costs.
```

### [20] hash=`a3ae7683bffa22e1`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
We can only hope that your snap judgments will always choose the right side, darling.You're still here, Vertin.I thought you had disappeared completely.I was hoping I might talk to you about my number.So sorry, but I really do have to leave now.Please, I think you may be the only one that can help.It won't take you long.Six.A perfect number.But it isn't my number.Let's try again.reset the calculation for me back to zero put an asterisk and zero and we can
```

### [21] hash=`5241c5f8a77b6b03`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
continue no that can't be my number either it's far too brilliant for meplease reset the calculation back to zero 210 I know 37 isn't a fan still Iwould be honored to have an integer like that as my number let's try itone more time I have a feeling that together we can find the right numberPerhaps the truth lies hidden in the question.Hold tight to that answer, darling.A bit of elderly advice?There is no greater treasure.
```

### [22] hash=`02e9bdccf87df0ad`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
One day you might be amused by this idea,when you see yourself from someone else's eyes.This is the second is the square.Party seven?Is that you?Put the triangle on the triangleAnd the rectangle, on the rectangle, perfect as things should be.The emanation?Disorder and chaos?Copy!This isn't right!Ugly!Inelegant!How could this be the revelation from the patterns of the Transcendental Law above?How could such a terrible answer fall on my-
```

### [23] hash=`a8c547acae32aed7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
I can't tell the others about this!There must be a mistake!I need proof.I have to go out there.Vertin, my child, are you here to partake in sand play as well?No matter how oft we arrange them, the sight of them never grows stale.Alas, I shall destroy it.I had a terrible dream.What did you dream?I named Six's throne and declared this the rock and roll empire of irrational numbers.She took out a jar of coffee beans and stuffed one into my mouth.
```

### [24] hash=`594ffffe6fbe44df`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
I believed that I woke up in time, and you as well.Let's go, Vertin.We need to tell everyone the numbers.Do you hear that?So many people out there.Must be Sophia here to pick me up.I told her she can wait for me outside.Wait, 37.When will they give us the order to attack?What's taking so long?The island is just across the bay.We have men, weapons, supplies, everything.Just give us order and we will take to shore.
```

### [25] hash=`1ca7bfc0ec928892`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Check out these bad boys.Anti-Arcanum weapons courtesy of the American from that Walden place.That creep just doesn't sit right with me.He's got that Arcanus stink about him.But his technology is solid and we needed it.We've got to get ahead of the Serbs and the Greeks.Relax, Georgi.Leave the decisions to the big shots.I'm sure they'll just hug out their differences in the meeting room or something.
```

### [26] hash=`58d7ee230f492b58`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Besides, you saw the monsters on that island.Can't speak for everyone here, but I don't want to die.Screw the negotiations!Screw the committee!Like it or not, we were the first ones to find the island.Not the Austrians or the Germans.Those arcanists have gone into hiding again.I swear I could see it from here yesterday are those bird-like creaturesleaving in droves George Ibraza leave them be come play with us George what a
```

### [27] hash=`f1345ed3ff057a78`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
good opportunity this is it's too good to pass up we've got to act now wewill claim what is ours this island belongs to us it's in ourterritory and we were the first to find it why shouldn't it be ours theThe Austro-Hungarian Empire has officially declared war on Serbia.Russia is mobilizing in support of Serbia.Germany demands Russia to stop mobilizing at once.Germany is mobilizing.France is mobilizing.
```

### [28] hash=`52440c4121e3c0a9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
But listen to me!It's odd to see you so flustered.What's the matter?I'm headed to the business school.We'll talk when I get back.Business school?to never go back.Ever since your human classmate shot your arm in a tool.What happened to your arm?Oh, Ethan.Yes, he wounded me.He had to prove his standing to the Brotherhood.There was no otherway.But that's in the past.He gave me his arm, so now we're even.
```

### [29] hash=`f63c4c9bbe9b753c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
I have to go.I haveto find Johnson, Raymond, and Herbert.That little rascal pushed Ilsa into the fountain.We have a score to settle.Take care, Clara.If you are not part of this project, please leave immediately.We only have eighteen hours until the storm.This is it.The first time we've made such a breakthrough in all nine storms.Your sister gave up her life to take us this far.I hope you don't need me to remind you that.
```

### [30] hash=`1634867bc9b5c56d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Yes.She may see ultimate sacrifice, hoping that it would lead to a breakthrough.But instead, death continues to rise.How can you let this go on?I demand to know why the experiment is still going!Ugh, don't we have enough crazies around here?Madalusi has important things to do, she has no time for you.Go cry to your therapist, human.Important?What could be possibly more important than this right now?
```

### [31] hash=`be38f508a3721624`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
What happened to the humanitarian ideals of the Foundation?Are we now under the tyranny of machines?What's this important thing she's got to do?Reading the paper, sipping on oil, and charging up in a 230-volt bath?Is that you, Adler?Welcome.Look at this mirror, dear.There's a sizeable stain on it.Yes, it is.Hmm, maybe its owner meant to break it so that the stain would be thoroughly removed.Now the stain is gone, and the owner has a collection of little mirrors.
```

### [32] hash=`d7ebbca6e81ae94b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
The experiment, ma'am.Why hasn't it stopped?Are you going to pretend that nothing's happened?That no one died?Could it be that you and Ulrich, the awakened, being the tin cans youare, have no regard for actual lives?Adler Hoffman!I will not warn you again!Relax, Adler.You are led by a biased opinion because you lack critical information.A common defect in all cognitive processes.The experiment has been cancelled everywhere, except for this very room.
```

### [33] hash=`f409b6f4666599f8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
What?As you and Researcher Medicine Pocket have said, the ritual is beyond the limits of almost everyone here.The side effects will kill them before the ritual can even take effect.The first wave was inevitable.Dora had pressed send before she disintegrated.We only managed to halt the subsequent transmissions and evacuate the unaffiliated staff.We kept only a few Arcanists on the team, and each has signed the consent form.
```

### [34] hash=`1580140e82d910b2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Forgive me, ma'am, but I have to use your argument against you.You too are guided by a biased opinion, an overly optimistic one.Because you have failed to properly assess the risks involved,we have suffered enough misfortunes just by uttering a few syllables of the Incantation.We've talked about the limit of things before.You should know better and ask the rest of the team to quit the experiment.Your insistence will only bring calamity upon calamity on our people for nothing!
```

### [35] hash=`a655475e2378934c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
You might be right, but how is being right going to help us?Huh?You spoke of the limit, and I am surprised that it is you who brought it up.The physical appearance of humans has remained relatively unchanged since the Neolithic era,But their thoughts and civilization continued to evolve and underwent significant transformations.The achievements that humanity enjoys today were not given to the species by any one person
```

### [36] hash=`a5d4c664cb3b40ea`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
with godlike powers, but were the result of the collective efforts of all human beings.Limits and boundaries must be pushed, or there would never have been room for development.There is no reason to believe that the limit cannot be challenged, especially whenwe already have the tools to do so.We must make progress happen.Gandios lies.Lies?We have no choice but to go beyond that limit.If we do not break away from the storm,
```

### [37] hash=`219ee3d6b5e3afdb`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
there is no future for us, let alone progress.We need to first determineall the side effects as a priority.This important step will help us compile dataand eliminate the effectsso our colleagues can use the ritual safely.And who will try it this time, Madam Lucy?You're not going to test the side effects as the cost of lives, are you?No.Thanks to Ulric, we stumbled upon a breakthrough.You are right.
```

### [38] hash=`46652812ba124677`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
It is time to send the other Arcanists home.Only the Awakened are needed here.The Awakened?The power is back, Mom.We are ready to resume.It will take time to properly explain.Please wait, Adler.We have yet to reach an agreementWhat are you experimenting?Here she's reciting it.She's read the reports, right?She was there when Dora broke into piecesDon't just stand there stop her now.I was going to lead us if she also turns into a pile of cops
```

### [39] hash=`1b9a6065442f3b84`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Stay where you are enigma.You insisted on being here.You demanded to see thisDon't bring your pathetic narrow-minded humanitarian values in here and tell us what to doWhat do you know about us?You can do it, madam.This is just part of the established procedures.Just a few more, madam, and it will be over.Established procedures.Simone, good.That's always bought die in vain, and you just let it happen?
```

### [40] hash=`87c9f773809340c0`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
Calm down.Calm down?She's dead right there.You murderer!We have already repeated this experiment many times.Many times?You've sent people to their deaths over and over again?Look at you, Adler, peeing your pants over a curse.The human boy is so scared thathe forgot to ask the crucial question.Did the ritual work?But what do you mean?The curse?The side effect killed her?The experiment failed?Is that not what happened?
```

### [41] hash=`c7c8456d53e90f75`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
No, triggering the curse and failure are two separate things.I was the first one to recite the incantation, way before Dora.When I read it aloud, it worked.I felt the warmth of a miraculous blessing on my head, soft, light as a feather.I told Madame Lucy right away, but as soon as she left the room, the curse hit me,and I began to liquefy.There was no one else in the room.My liquid form had become too insubstantial to push the help button.
```

### [42] hash=`45911caf46e92e99`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
A long darkness followed.After that, I woke up again in my original, primitive form.The way I first came into this world.Original, primitive form?Unlike humans, the Awakened have neither flesh nor nerves.We are pieces of consciousness, echoes of a primordial melody that just happened to residein material objects by chance.With a mind and a body combined, we could talk, learn, think like you do, and perform
```

### [43] hash=`d4c7124d1713a3de`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
the experiment and endure the side effects.And this curse, for some reason, cannot affect the primal consciousness that causedour awakening in the first place.While human minds dissipate when their tangible bodies are destroyed, our minds reawakenregardless of the changes and destruction of our external bodies.Of course, this wasan assumption based on idealized circumstances, and I needed another awakened being who could
```

### [44] hash=`b5cc4747897d4eaf`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
awaken in different bodies to confirm my theory.That is why I sought out Madame Lucyfor cross-verification.The results?Yes, it was an assumption!You said it yourself!You came back to life this time!But what about the next?Nothing is for sure in our Canem!What if she neverwakes up again.What if she dies for good?We know what we are doing, human.Stay out of this.Only the awakened can carry out theexperiment.
```

### [45] hash=`2bac11aeb732fd7c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
So we must proceed.This has nothing to do with race.It is a sense ofduty that every researcher should have possessed when they chose this path.We have to gobeyond the limit.Not out of madness, but out of rationality.We seem to have replicated effect number 2, and 117 of the Coleman lab's protective rituals were proven ineffective.Write it down, Simone.This is the fourth time we have seen it.Also, number 45 and 69 are related to it.
```

### [46] hash=`2403d8f8219d8bfa`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
We need to speed up.This is too slow.Adler, what are you doing here?I am glad to see you out of your room and working with us again.No, he's not on the team, Mom.He forced his way in here.My apologies.I seem to lose a small amount of data when I reawaken.Still, I am glad that you are showing initiative, Adler.Were we supposed to talk?No.We have nothing more to discuss, ma'am.Ulrich has filled me in on everything.
```

### [47] hash=`287433e071891ca4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
ButI still worry whether the experiment's risks were properly assessed.Assessments will only be assessments.Much is beyond measure when it comes to Arcanum.Perhaps faith plays a more important role here.I'm surprised it is you talking about faith, ma'am.It seems we both have the ability to surprise each other.You are right.Assessments could indeed be useful to us.It allows us to know the probabilities of success and failure based on established facts
```

### [48] hash=`42c5a1a92cce863a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
and past experience.But, when we find ourselves in uncharted darkness, with no information or past experienceto guide us, how are assessments going to help us?The only thing we have in such darkness is the unwavering faith to move forward.When the first steam engine whistled, I awoke into this world.At the beginning of this new life, my circuits were charged with a singular primal desireto progress.
```

### [49] hash=`6834c28b24dd65e9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
In the midst of that never-ending whistle, I have watched man build the towers of scienceand knowledge, and I have watched them unleash chaos and destruction.You too have been lost and deterred, but your engines of progress have never stopped churning.Always move forward, no matter the destination you told yourselves, until the storm broughteverything to a standstill.But this is just a small setback.
```

### [50] hash=`32b7afb29da040a2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
We are only back to the beginning where we stumble blindly, and this time, I happento have a cane.No need to worry about me.I will not shut down as long as there is still hope for progress.We have wasted a bit of time on data recovery.Come, Simone, let us begin the next experiment.I hope to dissolve into PACE this time,so we can easily handle it with the Coleman's Ritual of Transformation.Seen enough?
```

### [51] hash=`ff932d5e8767f6a3`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
We know what we are doing and you are of no help here.It's been the same old story in this place for the past eight years.Adler Hovman from the cryptography team.Is Medicine Pocket in?I heard that theywrote a paper on the linear correlation between the purity of an arcane isbloodline and their power.Can I get some more details on the research?The paper is here.Help yourself.Sorry about the stains on it.
```

### [52] hash=`6604836e633d4124`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p60`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 11~15）

```text
I just took it out ofthe trash.If you're looking for Medicine Pocket, I'm afraid they justLeft?To where?They left the building?Hasn't the countdown already begun?Um, yes, and by regulations we are not to leave.But, um, they said their new theory had to be verified in the storm.
```

### [53] hash=`c3c0a70ec3e42a10`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Fresh air, green grass, the dew, the mud, this is what I'm talking about, a better world!Researcher Medicine Pocket, I must remind you that we are at the edge of the immunity zone to the storm.Once we cross the line, we will not only catch the storm syndrome, but also be taken by the storm at the end of the countdown.I know that, how stupid do you think I am?Hey, isn't that Rudolph, the poor guy sent to Tunguska?
```

### [54] hash=`fb412d7569def8c5`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Hey man, how is Siberia?Welcome back.Did you bring me any new research materials?Oh, you don't recognize me?You're breaking my heart.It's me, your best friend that you just met.Medicine Pocket.Researcher, I must make clear that you only applied for 15 minutes outside for research purposes.Your countdown starts from the moment when you cross this line.Okay, safety first, I know!Get off me, you're hurting my arms!
```

### [55] hash=`4d141b349200cc27`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
All bounce as soon as the storm syndrome hits.Even if I catch it, look at the syndromes of this era.Distorted faces, murderous intentions, obsession with war, rampage.What's got you so worried?They aren't that bad.Well, the melting faces part is kind of gross.I really wanted to test this in Vienna.Oh well, better than nothing.Alright now, I'm gonna walk a little further from the immunity zone so the samples are
```

### [56] hash=`921e385b9038f1b7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
easier to gather.The ideal distance is 1,500 kilometers, but don't worry, not gonna do that.Even I can't run that fast.Now behold, the important moment.When I prove the dorks in Laplace wrong about asymmetrical nuclide are.Now hypothetically, if the storm research were to succeed, two things should have been done.And to find out the safe way to use it, we have to...This is what Lucy was thinking.The awakened met the casting requirements of the incantation, and Ulrich succeeded.
```

### [57] hash=`4dfd801fafd8e97b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
while the other Arcanists did not feel the same miraculous blessing like he did.So as long as we eliminate the side effects, they'll be able to inscribe the Incantationand mass-produce it for the humans.One problem is, only the awakened can carry out the experiments, and there's not manyof them around.It'll take too long, there's no way to do this in 24 hours, heck it could takemonths or even years!
```

### [58] hash=`1c6f2b53a0bdf86d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
there must be something else we can do but you are not an Arcanist why shouldyou play by their rules yes that's right let's try a different approach what if Istart with the desired outcome and work backwards to the question thequickest and most efficient way to save everyone is to make them qualifiedcasters of the ritual they won't even need protective equipment if we can doThe challenge is, how do we qualify the casting requirements?
```

### [59] hash=`05fab2311dce7fca`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Medicine Pocket's theory is correct, and there's enough data and supplementary experimentsto back it up.The power of Arcanists is directly tied to the purity of their bloodline, which is associatedwith the special cells in their bodies.Using arcane skills reduces the activity of the cells, but the Picasma extract canreactivate them for extended casting.However, the extract only provides endurance, not power.
```

### [60] hash=`f437661d103fa31f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
It is physiologically impossible for a low-ranked Arcanist to cast a high-ranked skill.That's the reality of it.If we were to compare the power of Arcanists to household appliances, let's say theirnormal voltage is 230 volts, and if the Storm Immunity Ritual were a high-voltagesource of a thousand volts, no, millions of volts, like lightning, the household appliancesThose islanders call the storm the emanation.
```

### [61] hash=`33b998ed8da80804`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Why?The emanation.Emanation.Just what is emanating out?Dawkins, I hope you know this is not the time to catch up!That is if you're able to talk at all!No!Let go!I've just come up with an idea!Leave me alone!Somebody!You're not really here for revenge.And it wasn't you who pushed away the books and opened the door.The invisible ghost.Victor, did you do that?What happened?Any progress?Yes.Researcher Medicine Pocket has proved their theory right.
```

### [62] hash=`506bcedc99cf403a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
They have successfully found the asymmetrical nuclide R in the air before the storm, evenif only a trace.What did you say?They came up with the idea because the nuclide was initially found in the raindropsamples of the storm.They deduced it also exists in the air before the storm occurs, like the waterOur biggest problem is the limit of the bloodline.Low-rank Arcanists can't command high-rank Arcane rituals, similar to how household appliances
```

### [63] hash=`4b50337037a234f0`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
can't withstand what's beyond their designated voltage.In most cases, the caster can only use their own Arcane circuits that run through theirinherited bloodline.But what if the caster were in a special electric field?What if we used existing circuits on the outside and put the caster into a greater circuit?What if we factored in the entire planet and used the atmosphere to split the current flowing through us by adding more appliances to the circuit?
```

### [64] hash=`0971eafcb02f3843`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Don't be ridiculous, Adler.We are not household appliances.Hold on, let me finish.24 hours before the storm, the entire world is charged with abundant arcane energy.It becomes a space emanating Numa, a cloud ready to discharge, a special electric field.Look at asymmetrical Nuclide A.The key to the storm immunity was inside the storm allalong.And look at how the Mantragora is the antidote to its own poison.
```

### [65] hash=`09c426ace188bafe`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
The solution can be hidden in the question itself.The arcane energy a caster inherently lacks can be borrowed from the surroundings duringthe storm.We just need a way to induct that energy.And Laplace happens to have all the data for the calculations.The observation systems we've built over the past eight years have not been in vain.First, we derive a formula to determine the NUMA needed from the storm based on the
```

### [66] hash=`cf7f2de1558965a9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Arcanus lineage.Then, we'll design a converter to transform the external NUMA into what they can use.They will no longer be bound by their limits!It's still a form of energy, yes?No one here knows what the storm is, but we do know that it's a massive arcane energy field.We can harness it, much like Arcanus use arrays to amplify their incantations.I see what Researcher Adler is trying to say.A creative solution indeed.
```

### [67] hash=`5bb0610091070797`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
But ma'am...Do not worry Ulrich.I also have noticed that humans could be smart and stupid at the same time.Perhaps that is why they need to have their work peer-reviewed.There is a type of electrophotography invented by Simeon Curleon and his wife Valentina Curleonin 1939 that depicts the energy field surrounding an object or body.It was later used by Laplace as a method of measuring arcane power, notably for the
```

### [68] hash=`5ae30d6765a99c43`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
storm observation systems.Through it, we are able to capture and measure the arcane light or aura thatis invisible to the naked eye.The plan of researcher Adler is feasible.Laplace also has the technology to support it.We have the storm observation stations, the capable casters, and the best mathematicians.Ulrich, please ask Miss Tider to lead the calculations, then experiment outside the safe zone and record the Pneuma constant
```

### [69] hash=`55219d8bd3630052`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
needed for casting the incantation.And do not give the incantation to anyone.I doubt they can resist trying it.Simone, please contact researcher X.His balancing helmet could be the prototype for our converter.That helmet balances the energy field in and out of our bodies, and was once used to protectresearchers working with dangerous arcane skills.We could boost its power and use it as a substitute for Adler's converter.
```

### [70] hash=`67d3f6dac00c1cd5`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
But we should postpone their testing request until we have completed our experimentson the side effects.What about me, ma'am?Should I go with the calculations team or help with the converter?Right.I wanted to talk about that.You have proven to us the value of human thoughts and perspectives.I am glad that your struggles with the bottle did not damage your brain, Adler.I am confident that your discoveries will save many lives in the storm once implemented.
```

### [71] hash=`12d12086b7585f19`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
The bottle?But it's been seven years.But you overlooked one thing in your plan.What about your people?The humans, who can never cast incantations.They were not included in the plan.I just came up with something that took the least steps to reach the desired outcome.To save humans, they'll have to rely on equipment.Only when we have better control over the ritual, can we store it on arcane devicesfor mass production.
```

### [72] hash=`918f814bc07e1c8c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Then you should go perfect it.We only have 16 hours and 30 minutes until the storm, there's not enough time to...The feasible part of your plan is in motion, and all of Laplace will provide the help we need.We will make it work.As for yourself, perfect your plan so we can save everyone,including the humans.And we only have 16 hours and 30 minutes to find a solution.Understood.I will think of something.
```

### [73] hash=`d23b078af9d6f96e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
You're right about this one.There was no way he overlooked his own race.Okay, let's clean up the place first.One, two, three, four, five.It's being organized when our God is with me.The incandation didn't work?Did they fail to perform the cleansing ceremony?Where's the Oblivion?His hysteria is acting up again.I can do this.He is just...He is divided into two numbers.Six and seven.37 you have seen a pair on right you asked the question didn't you the answer the answer that will save us from the emanation
```

### [74] hash=`5a2ad4ef4f1271b3`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
once and for allIs that it the one true answer from a pair on is a string ofNumbers because the transcendental truth is beyond the limit of our mortal fleshIt cannot be described by words seen by eyesinterpreted by logic or perceived by the senses, it is passed to us in a form we can understandnumbers this is the key to the truth give me some time and i can decode it what i've ever dealtwith in my life we will be freed from all these problems and if we don't know it's distant won't
```

### [75] hash=`f4b8742ae30d68b7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
change what's in front of us now a stray child owns you so has the truth not graced thee withWhat question did you seek its knowledge?What answer did it give you?Aren't you going to perform the cleansing serpents of fear?Please come up to me, Miss Vertan.I wish to have a word with you50 strides from here on the semicircle squareYou will find your friends and the rest of our people.I have done as much cleansing as I could
```

### [76] hash=`2059a9f3b5b81b1a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
If nothing goes wrong, they will regain consciousness soonMay I know what happened during the cleansing ceremony?Thirty-seven and I each had a bizarre dream after the earthquake.Did everyone on the island fall asleep too?The island's order is forged by our faith, and now that faith has been broken, thatis all there is to it.What did you say?Upon our arrival, I sensed a large-scale ritual surrounding the island.
```

### [77] hash=`e9feb2af080b0420`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Is that the circle you kept talking about?Was it...broken during the ceremony?In the midst of such overwhelming destruction, where has their vaunted wisdom gone?And what good does it bring in this final hour?I can hear thy weeping and bellowing within, Miss Sophia.Many a time you have knelt at the Temple of Truth, devoted yourself, prayed for your people,and withstood the tribulations set upon you, all for the betterment of others.
```

### [78] hash=`b3a2680ca65ff33f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Chaos is also a form of truth, is it not?Just like how irrational numbers are numbers.Despite our dislike of them, they still exist and cannot be denied.How did this become the destruction of our people's faith?You will hear no answer from me, 37.For that is not the question worthy of your attention.Do you still remember what you answered to me in the cave?That would be enough then.Don't waste your time on the collapse of the faith.
```

### [79] hash=`e8d035ade5f3d454`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Don't question yourself because others think differently.Walk on, onto the path you have chosen.You have done nothing wrong.Ms.Vertin, I'm afraid I must trouble you for a favor.As you can see, I can hardly take part in this matter for any longer.Should the situation turn for the worse,Please take 37 to safety and assist her in decoding the numbers.You have my word.We are born facing a choice.Either we restrain ourselves and strive for harmony and discipline,
```

### [80] hash=`a5cfbd466098023a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
or succumb to destruction fueled by passion and madness.Though the former may be challenging, the latter will only plunge us into eternal darkness.From one to ten, each number has its moral purpose and mission.Among them, only six was chosen to be the leader.Because six stands for balance?Yes.We must pay heed to the balance between passion and reason, so as to stay on theright path and not be led astray by the calling of our blood.
```

### [81] hash=`77b511b67960006c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
For generations, we committed ourselves to the scripture and stayed true to what we pledged.We left the trivialities and troubles of the phenomenal world behind, and served the supremeexistence with the fruits of our knowledge.This kind of faith was how the island prospered, and it was the source of our salvation.Through diligent practice and contemplation, we managed to remain secluded and independent
```

### [82] hash=`1cc2e47dbd48ce7b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
from the rest of the world.The irrational numbersthat your people rarely appreciate.Are they faced with a different path?A path of passion and madness?We have been long isolatedfrom the outside worldby one emanation after another.Four years agowe tried to seek proofin the outside world, but failed.We regrettably lostsome of our best scholarsand friends in the process.However, it was not the failed attempt that led to this upsetting situation,
```

### [83] hash=`f0c1c618c77f5e95`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
but a crisis from within.Now with our ship capsized and our scale fallen,I am no longer able to reconcile the tilt of people's hearts and souls.We will be divided.The fanatics from the foreign lands can finally spread their hatred amongst theof our shattered beliefs.I will stop Manus Vindicti.Forget not your promise,Miss Vertin.Six, we came tobid you farewell.Everything happened here proves you to be an
```

### [84] hash=`cee01bfb05d4ca06`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
incapable leader.Your preachings of moderation and reconciliationwere nothing but excuses for cowardice.Where were you whenthe humans dropped bombs on us?What did your cleansing do to help us?If those virtues are meant to be theIt is clear they have taken the side of the humans!Kill the envoy!Cut off her head and bring it to our mother!What?You?The mask has robbed them of reason.There's no point in talking further.
```

### [85] hash=`3607171d2ade9798`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Take 6 to safety 37.I'm the one we are after.Point 2!I will meet with Senetta at the square.Miss Bradyo is with them and we will contact our people from there.You found it!That's good.I always wanted to tell you.It is a great number.The number of a herald, prophet and pioneer.When it was first discovered, mathematics was nearly destroyed.But luckily, it also spurred advancements in the field.Are we still friends, Sophia?
```

### [86] hash=`2fc7eccebb1e1cdb`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
Yes, 37.We still are.But there are more important matters I must tend to.This is our way to start the earth is beat up toAnd you look I must leave now 37 lady arcana has shown me another path is itbecause our circle has been broken but I found the truth I have the finalsolution just give me a little more time and everything will be fine againI promise.You and I are different, 37.Not all of us have the privilege
```

### [87] hash=`c865b07f5b4aaa8e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p61`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 16~20）

```text
to look on from the sidelines.Sophia, you...I will join Manus Findic Dei,take others with me, and leave.I will renounce the scriptureand seek vengeance in the phenomenal world.Make your move, 37.If you really are the genius who can overcome anything,She is still on this island.We still have a chance to stop her before it's truly too late.We should go now, Sinetto.We have 15 more hours until the storm.
```

### [88] hash=`53e0639b280ab7a7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
We've got signal Zeno has restored communications with team timekeeperVery well, we will leave you to itJust to confirm before we go the operation Zeno is currently undertaking has been approved by the pack security council, right?I am most pleased to see youHad you a pleasant stay on this island miss verton are they not an intriguing flock of people?Their wise ones draw a circle at their feetIf you came here to incite hatred and recruit the pure-blood arcanists on this island, you
```

### [89] hash=`e2d04ff317cb05ae`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
may now walk away with satisfaction.If you wanted to take the island as one of your bases, you could have done so afterthe cleansing ceremony failed.But you did nothing.You just stood there.Why?Do you struggle to comprehend, sweet Burton?I was waiting for you.Don't worry, Regulus.We have foreseen this.When we first arrived, I was bewildered bythe rules on this island.But as I learned more about their scriptures, things began
```

### [90] hash=`96e5dba274f30b72`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
to make sense.Language is an unreliable means of communication.Information can becomemuddled and vague wording can lead to mistakes and contradictions.That's why the islandvalues math as a more precise and truthful language.They mock language for its ambiguity,An adorable attempt.Are you truly prepared to gamble the life of thy sworn companion, little pup of the foundation?I will not make the same mistake again, Miss Arcana.
```

### [91] hash=`0ec94de3eee9bdb0`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
I know perfectly well what I'm doing.Your provocations will not work on me.For the peace of this world, I will stop you.She's...waiting for something.Everyone, it's almost time.Xeno will start any minute.We need to complete our preparations as planned and force Arcana to show up.Easy.If we finish off all her minions, there's no way she'll just stand by and watch.The big guy up there is mine, you deal with the rest.
```

### [92] hash=`56ee91d2c665da31`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Trying to gain air supremacy?Not under my watch.I'll send that outdated hunk of scrap metal crashing to the bottom of the ocean.Airspace cleared.Preparing now.Just like the battle simulations.I will not allow the tragedy in Chicago to happen again.Timekeeper, it's time I showed you what my training's been for.Start running!Timekeeper, I've defeated the enemy.Beginning preparations now.Be careful, Captain.
```

### [93] hash=`0893060cecc37602`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
It appears that some Abraxas are being affected by the storm.Huh, a mimic strategy.Clever.But we can also use it to our advantage.Everyone!Rotate your arcane skills!Make sure we always have the stronger afflatus.Let's teach it a lesson in improvisation.Get it over quick!Till the torch is lit.Enemy's ritual has altered the environment.Please be careful.Take cover.I'll send it back into outer space.
```

### [94] hash=`3e2f3c0d6e83287a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Time comes to speak of truth.The moment of utterance.The scale of your soul has tilted.The balance needs to be restored.The creature is defeated and Arcana has emerged once again.Timekeeper, stage two is complete.Cool!Now, we just have to activate it!No, things are going too well.Like this has been rehearsed.What on earth is she trying to do?There's no time, Fartzen!You're right.We've put too much time and effort into this plan to not carry it out now.
```

