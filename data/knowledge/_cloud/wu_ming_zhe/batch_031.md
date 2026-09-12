# 剧情图谱抽取 · batch 031

- 角色：`wu_ming_zhe`
- 批次：**31** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.4」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_031.jsonl`

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

### [0] hash=`09700f28399a27d1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
likely an integer.Therefore she should be identified as an unknown number, notYour sophism has failed.42's argument is held valid.Is there anything else you'd like to add, defendant?Are you a secret, 13?We would call criminals negative numbers.I got it!It is easy to prove Senato's innocence.According to the law of the excluded middle,Senato either committed a sin or committed no sin.The two statements cannot be both false at the same time.
```

### [1] hash=`b33d837bfa5f27d8`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Since we consider a criminal as a negative number, and a non-criminal as a positive number,Senetto at present is considered an unknown number.That means she doesn't belong to the criminal sect, or the non-criminal sect.She did not commit a sin, and did not commit no sin.The paradox.I hereby demand to modify the criminal sentence that has been given to Senetto.The law of excluded middle.A good sophism.
```

### [2] hash=`f33750cc901de255`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
Good for you to create a paradox from one sentence of my argument.But pitifully, you've made a fatal mistake.You've taken my argument as the basis of your defense.I said people without a number should be expelled from the Hall of Truth.You don't have a number either, Miss Outsider.including that hat you don't want those good ears to hear this privateconversation that pad of paper from the miss yes the one wielding the ruler is
```

### [3] hash=`82a2f86518db9e32`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
quite valuable I can tell it is of a certain age and records quite a lot ofanecdotes one visitor to the island took out abouquet from his luggage to share it with others he made an attempt toparcel it off another visitor fell to the ground and happened to sit on athat the debate is only a game involving sophistry, improvisation, and strawmanfallacy.So what makes it superior to beans?If the form is what they are
```

### [4] hash=`2d5011f42bd76cb9`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
really after.Anyways, whoever fools the others first will win the game.Noarcanum at all.And that argument of hers is the best attraction for theBy then, I guess you would be eager to throw up the elephant and turn back into the adorable,easy-going Zero we all like.See, just like you, people are always on the way to finding something that can satisfythem undoubtedly, if what they already have was disappointing.
```

### [5] hash=`141c983f21f0576c`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p34`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜9~12）

```text
They stare at the flame of the matches, read the tea leaves in the cup, and bustlearound the instruments with star patterns.A nice, unique prime number which equals the word genius.At least everyone prefers to think this way.Why not deify the one that is able to reach the truth when you have the chance?It's much easier to pin your hopes on others than to blame yourself.I guess you also did that, right darling?

It's okay.She never says no.She just lets the hopes pile up on her shoulderbecause she simply doesn't care at all.What a good, good child.
```

### [6] hash=`cd0ed73eed123c98`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Thirty-seven.You just said Vertin's number is zero.Do you know what it means?Very clearly.Would you be able to submit proof to a Peron?No problem.Half of you in this hall have put in the pebbles.If Thirty-seven's argument is found to be true, every argument Vertin has spoken in Sonnetto's defense will be deemed valid.Sonnetto will be exempt from the punishment.Alas, poor little Vertin.You still don't understand.
```

### [7] hash=`b389394d32348a49`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
The number of our souls suggestsour fate.It might be changed through algorithms temporarily, swirling, shifting, or transformingalongside other changes occurring on the coordinate axis.But in the end, we can only be ourselves.One is thought, two is opinion, three is wisdom, four is strength, five enthusiasm, six harmony,seven order, eight philanthropy, nine is restraint, while ten is completion.Zero, however, is in the middle of the axis, the origin of the frame of reference.
```

### [8] hash=`379399a4a0d0ae72`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
It's neither positive nor negative, neither prime nor composite.Things are ever changing, but you stay the same.Your loneliness also lasts forever.This is your fate, being exposed in full view of the crowd, yet you know nothing aboutit.Thirty-seven was acting on impulse, yet she opened Pandora's box.She leisurely reveals your fate.That carefree behaviour makes no difference to picking up a shell on a beach.
```

### [9] hash=`7ce4e8fb16d9f8b5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
How could I not pity you?Ms.Vertin, 37's proof has passed the review.Your friend will now be exempt from the punishment for violating the rules.However, she has to take some catch-up lessons on the scripture.Please, meet me at the hall tomorrow at noon.I would have words with you.Before this negotiation begins, I wish to tell an allegory to the two of you.A group of people were imprisoned in a cave.
```

### [10] hash=`7c4518ca05bebfb9`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Behind them, there was a fire.Before them, was a tall solid wall.Their legs and necks were chained and fixed,so they were constrained to look nowhere but to gaze at the wall in front of them.When they dropped their eyes, they saw their own body.When they looked up, the flickering light of the fire fell over them, and they only sawthe shadows of what was passing behind them.No one had lived one day outside the cave.
```

### [11] hash=`33df5aa47960bfeb`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
The shadows cast on the wall all there was to be perceived as reality.They had no knowledge of the real world.One day, one of them escaped from the cave, walked into the light, and saw thetrue world with his own eyes for the first time.everything he saw or felt in the cave was nothing more than a mere shadow ofthe object's true form.Our world is a poor one, Miss Verten.The phenomenal worldis the cave in this allegory, but we are surrounded by shadows or some
```

### [12] hash=`46cb959e9996bb5a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
humble fractions of the truth.It is ugly, frivolous, filthy, perishable,subject to decay, and filled with hollow desires and meaningless struggles.Only the wise can walk out of that cave and see the world as it truly is.In that eternal, transcendent world, everything is in its most perfect form.I pray that you, Miss Vertin, the representative of Saint Pavlov Foundation, and you, MissArkana, her counterpart of Manus Vindicte, would pay heed to my words.
```

### [13] hash=`b3a08153dbdd9e32`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Everything you've been fighting each other for means no more than some fragments ofWhenever my intention to sully the sanctuary of truth.Then to prevent a situation like this from happening again, I would like to ask you twoto carve your names on these two stone bangles and drip a drop of your blood on each ofthem.Once the bracelet is put on, no one will be able to remove it.From now on, as long as you're on this island, none of your people will draw blood
```

### [14] hash=`d2f8956990331e94`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
verton emotionless in the storm alas no man shall bravest the stormand live including thee a wooden gox in theality house base has my name on it was that your doing sadly it wasn'ti hope thee findeth the answer satisfactoryis that miss arcana miss arcana please don't save us but the right time andBut they have nothing to complain about.You know what they say, what is reasonable is real, that which is real is reasonable.
```

### [15] hash=`efe59287f6613225`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
They showed you a broad avenue in their teachings where you could enjoy a sense of securitywith all the solid ground, convenient automobiles and warm sunshine.And at the end of the avenue even lies an inspiring mission to which you are expectedto devote your whole life.There is a distinction between good and bad here, and it's as clear as our innate senseof right and wrong, like a floor of black and white tiles.
```

### [16] hash=`f0a1865af1fadb89`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Any stains on it will be noticed immediately, but in fact, there exists another path inthe woods.It's much less traveled, leading to the unknown darkness which cannot be seen witheyes or proved false.You may even experience indescribable chaos and madness there.This path, however, has an excellent view, and it's one of a kind.The plants are thriving with bursting energy, and the flowers are blooming in a delightful
```

### [17] hash=`b2a563a2b231ca8a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
atmosphere.So, which will you take?That's not an easy choice to make.This grandma must give you a round of applause.I would have even pinned a boutonniere to your suit if I had one.But I have to remind you, those things in there are not easy to deal with.It would be a good choice if you want to enjoy the scenery without getting lost in the darknessI'm sure you know that myth you shall take the soul of your love out of the underworld
```

### [18] hash=`d1b113a0e474332f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Yet you shall not look back.That's rightYou shall pass by the sleeping sirens yet.You shall not make a soundThe ones with the belief set off they entered the dark woods barefooted yet moved soSmoothly as if they were walking on the AvenueThey kept their mouths shut and eyes forward.They never turned back, never picked up what was not theirs, never set foot on the ForbiddenLands, and never looked straight at the Sacred Greatness.
```

### [19] hash=`84671d06ec0212e1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
They showed frugality, patience, and wisdom in the face of hunger and danger.So the beasts continued to lurk in the shadow, and the ones with the belief passedthrough the woods safely until the path disappeared along with the direction sign then the first oneto look back gave an exclamation before being exiled think about what i just said that whichis real is reasonable never look back in the woods darling if you don't want to be turned
```

### [20] hash=`e4ce74a197bbddd3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
into a pillar of salt which can do nothing but wail then never ever look back yes we'd betterstay awake, stay calm, stay cautious all the time.But then there comes the problem.How can anyone, how can you ignore your lovefor those thriving plants and blooming flowers?How are you supposed to deal with the unstoppable feelingthat overflows like a melody when it is stirred upby the beauty of the scenery?
```

### [21] hash=`dbeef48f71159021`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Of course, you will cry the loudest cry,Dance the wildest dance, drink the strongest drink, and vomit all the filth inside you.After all, there is no need to enter the woods if the soul-stirring scenery is not what you are after, right?No, you better let it slip your mind, darling.Just let it go and hurry forward.Remember to keep your eyes shut and hold your breath.When you do so, the scenery will no longer mean anything to you, nor will the fragrance
```

### [22] hash=`fa7724112a7d5471`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
of the flowers.You will get out of the woods and reach where the truth lies.Is that what you want?Don't worry, we have plenty of time.You may come back at any time and pick another way.Congratulations, Miss Sinetto.You are the fastest learner of our doctrine among all the visitors in the past halfcentury.On behalf of all our writers, I award you this laurel wreath.No, no.I wouldn't have achieved this without your guidance.
```

### [23] hash=`08b70d2e3ba2cf0c`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Those mathematic statements are really inspiring.I've learned a lot.But there's still something confusing me,such as Pythagoras and his golden thigh,his memory of the previous lifetimes as the son of Hermes,and the transmigration for every 216 years.Could you please tell me more about these?Why would people fail to see the charm of the matrices?This is not right.I need to spend more time on teaching.
```

### [24] hash=`40b3d86cb8b79937`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Anyone!Anyone save us!Thus my journey of art is doomed to fail.I really don't want to study maths anymore.Help.Timekeeper, you are here.I heard that you completed all the lessons on the scripture.This laurel wreath suits you well.She put it on without hesitation, but I don't think her purpose would be as simple as harkening the ancient wisdom.I attacked Manus' followers earlier as 37 asked me to, but I received no punishment from the bangle.
```

### [25] hash=`b8b6afc445af54e6`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Perhaps this island makes its own judgement on what to be classified as hostility, like it has a mind of its own.Senato, do not report this to the headquarters before we figure out how the bangle works.Apologies, Vertin.I was going to rescue Sinetto through a very creative underground tunnel.But things didn't quite go as planned.Not a bad innovation, but a simple clap on the forehead.If only you didn't miscalculate the location of the explosion.
```

### [26] hash=`91c6a9f65ad767db`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
This apple is grateful that it didn't get blasted into a puddle of apple jam.Warning!Shell cleaning required.Warning!Since you have too many floating points, words of discipline would not work on you.We would have suggested you study with the rest of the students here.Abstain from eating meat, bathe in cold water, rise with the Apollo star, study our doctrine,read the scripture aloud on the beach, so as to remove your floating points and purify your soul.
```

### [27] hash=`0af3b376f6c04f79`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
What?I won't do any of that.But taking your peculiar character into consideration, I decided that some compulsory labour would be the better option.Oh, that's the best news of the day!I'd rather clean up the rubbish on the beach than be surrounded by people giving sermons all the time!At least the rubbish doesn't talk gibberish!I'd be dead if you didn't change your mind!Regulus, studying the scripture is not that scary.
```

### [28] hash=`3eaf22094a477263`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
They will teach you and guide you until you take full command.Just like taking lessons at school.Is that what schools are like?Haven't you been to a school, Regulus?A great pirate would not remember trivial matters as such.So, where were we?Which part of the beach needs to be taken care of by the great captain?My laboratory.Where did you pop up from?As for Vertan, you will assist 37 with her study of the emanation.
```

### [29] hash=`d5cab57c572293bc`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Don't waste more time on the trivial matters of the Phenomenal World, Integers.That was the sole reason you were on this island, was it not?Don't let down your guard.The Arcanists on this island are not as easy to deal with as you imagined.Down in the cave, I heard some pretty alluring and intriguing anecdotes.Miss Lillia, this way.You will cover this area.Stay on the radio.Don't worry, Timekeeper.
```

### [30] hash=`a881d7774f486c05`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p35`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜13~16）

```text
Lillia and I will keep an eye on Manus Vendictae.We're counting on you, Senato.I have a feeling we're coming closer to a big secret.What am I looking at?So your so-called sacred project is this gigantic IDM computer?I was curious about them during my stay in Laplace.The form, or the essence, is what's left of you after all the fakeness has been peeled off.
```

### [31] hash=`078578c316910854`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Now we are listening to the New Year collection.The world-famous painting Mona Lisa was found and returned to Musée de Louvre in the afternoon of December 13th.The U.S.Congress passed the Federal Reserve Act on December 23rd, formally establishing the Federal Reserve System.The conflict between Austria-Hungary and Serbia has escalated.Bulgaria challenged the Bucharest Peace Treaty.Tension is building up over the Balkan Peninsula.
```

### [32] hash=`a3eabc4fb88477cd`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
So was 37's mother, who was also on that ship.Why are you crying, Sophia?I was wrong.We calculated it wrong, 37.We miscalculated the impacted area of the emanation.We thought the ships would be safe at the Gorgon current,but the safe area is in fact five degrees away.When the emanation happened,the bow of their ship had just entered the safe area.But it was too late.My dad is gone.So is your mom.I know.
```

### [33] hash=`968b144ebbb9820b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
But why are you crying?My mom and your dad have come back to us, right?Have come back?Do you call this coming back?Like this?In the form of geometric bodies, cold and silent, being pushed to the shore?No matter how much time you spend on it or how sophisticated your device is, it is impossibleto draw a perfect circle in the phenomenal world.Arrows always exist.The floating points after the decimal can be reduced, but not destroyed.
```

### [34] hash=`df283d57b7a16b3f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
The perfect circle only exists in the abstract, transcendental world.Of course, anyone in the world can find out the value of pi through the most primitivemethod.Egyptians, Greeks, Chinese, and Babylonians, theyhave all tried.They made circles with twine, painted onthe ground with twigs, or measured the land withcubit boards.But none of them actually drew a perfectcircle.However different their practices were, they found out
```

### [35] hash=`d775be11f2dedb37`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
the sole truth, the approximate value of pi.Because theessence of the circle is hiding in the imperfectGive them your proof, just like how we submit the proof of our soul number.Place your hand on it.Feel the texture.The craft is one of a kind.Not some cheapie you can get from the flea market.I mean it.Helene.And even the most traditional, delicate, and expensive kind.It has applied fiery red as the dominant color, and the stitches are perfectly neat from the
```

### [36] hash=`967fcd4c56f8fce1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
sea, just like you, darling.It arrived with a Meersham pipe, a glass jar, a pack of sugar cubes, and a child in panic.Both she and the Keeling were born on the land where the craft originated.Their appearances apply the same dominant color, and the patterns in them share similarcomplexity.Oh, your curiosity is aroused.But we are not done with the carpets yet.You've always got to get a souvenir or two
```

### [37] hash=`0f5a344b9ba8496a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
every time you reach a new place.So you will have something to showwhen you tell the stories one day, right?Look at these handmade fabrics, how splendid!Those incredible patterns were the only thingon the craft women's minds when they made the carpets.It's safe to say they have spent their whole lifeimproving their skills at using the vertical loom.And that's how we get these carpet knotsarranged in beautiful lines.
```

### [38] hash=`9a0ef6370c28b418`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
But they are just people like us.What if they get distracted?What if the carpet knots go off the right trackand get tied to the wrong threads?Hmm?Then you will be in trouble, big trouble.All the problems in the universe will come at youand the situation will be even worsethan the bureaucratic system of a millennial empire.Calm down.Many swear like you do when there is nothing they can do.They always step into the same river named Mistake
```

### [39] hash=`3c24a8ccfa241414`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
again and again.That's why we need them.Those crossing the river with their rulers,spanners, toolboxes, and dusty faces.The correctors, an ancient profession.Their duty is to remove the loose threadsand iron out the wrinkles on the carpets.In the language of this island, that is to check the calculations on the papyri and even the holes on the punch tapes.No one is capable of doing this job except the altruists, because it is similar to unraveling a ball of wool.
```

### [40] hash=`405bcd6559ee4537`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Besides finding the end of the threads, you must always pay attention to the cats.Yes, the cats.They may jump on the ball and make things even worse.And she, the red-haired little girl with the carpet in her arms, was overwhelmed at the beginning.Not yet familiar with the ruler, she tried her best to find the end of the threads.So the cats took the opportunity to jump on her together and left countless scratches on that little forehead.
```

### [41] hash=`6e7808e91bead09d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Poor girl.See, that's the problem every corrector has to deal with.Their job is to correct errors.But what if their own existence is also part of the errors?Oh, it's no big deal.There is more than one loom in this world.She left the complicated patterns behindand came to this simple kingdom featuring numbers only.There she made the first contact with a spinning loom named Geometry.She had never seen anything like that before,
```

### [42] hash=`110704e63586e377`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
And it was almost impossible for her to comprehend how it worked.She could hardly convert the numbers on the books into an actual diagram in her brain.Without a whole picture of what she was working on, she resorted to her hard workand more hard work.Then a long time passed, leaving one wound after another on her fingers.Later, the wounds even became calluses.In the end, her hands were no longer tender, but tough enough to resist the damage from the loom.
```

### [43] hash=`8973da984a6d0cab`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Yes, she has won a place on this island for herself.Yes, she's a quick learner.She learned even faster than some of the locals.That was not enough, because she has been outmatched by her playmate,the leading one in the field of mathematics on the island.That girl is like a perfect piece of satin, born by nature.It is decorated by the beauty of mathematics and geometry.No manual work involved.In order to reach the showcase where that perfect piece lies,
```

### [44] hash=`597a2bcd89c9d7d8`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
and to stay on the right track and fit into the school,she has done everything she could.She is still the most distinctive carpet there.Anyone can tell that as long as they spend some time on the island.Of course not.It's only a bit different from others.So she will continue to weave on the loom until one day the spindle pierces her callus,and the fire burns everything to the ground.You know that mathematician who was thrown into the sea?
```

### [45] hash=`23367d965cd8d08d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
He died because he said something he shouldn't have.Cut not wood on a public road, open not an unwanted bottle.Oh, is that so?You integers will be fine then.Good luck.Don't beg this pirate for help later.Hold that.Something is coming out.Who stood ahead with two snakes as its feet?Braxxus?That's weird.Why are they here?They're coming for us.What did I say?Don't beg-Regulus, prepare for battle.Okay, I know.
```

### [46] hash=`2cc945ae8ce86ee8`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
I was just teasing her.Grim Bangle is activated, but there's just a Braxxus.The Twelve Gates lead into the discovery of the Philosopher's Stone.This is that alchemy handbook given to Edward IV by George Ripley.Why is it here?Look at this, Captain.Of the Great Stone of the Ancients by Basil Valentine,the one hundred and twelve books by Giba,Emerald's Tablet in Latin,Seems like there are more ancient texts about alchemy hidden inside the hole, but they are all incomplete.
```

### [47] hash=`9f33b37d78aaee9a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
So maybe I need to crack some more crossword puzzles to find out about this.Caves endow people with wisdom.Our secret knowledge is hidden in the silent boulder walls.The knowledge in those books is just a drop in the ocean.Follow me, Regulus.Vertin, you lot go ahead.Go with 37, I will meet you outside.Infinity has no start and no end, but nothing would come into existence if there's only infinity.
```

### [48] hash=`c0d549021e07cce2`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Look up there, Vertin.Now they are presenting in their true forms, in their purest and newestforms, cutting all what we call mathematics.The essences of numbers exist inside all beingsand the patterns of all numbers exist in all matters.The length of a butterfly's wings andThe plant's body are a golden ratio, and the plant leaves grow on their stems in the pattern of the Fibonacci spiral.This is the most primitive rhythm of Arcanum, and it is also the beginning of our extraordinary study.
```

### [49] hash=`97672a80aec30018`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
This is the essence.And how do I submit my proof?Close your eyes, Vertin.Only when your eyes are closed will your mind remain fully concentrated, and recall the question you want to verify.Only in the absolute contemplation can truth reveal itself to you.The Storm.The Emanation.The Storm Syndrome.Where are they from?Foundation, Manus Vindicte, Aperon.What roles do they play?Why does the storm fall when history trembles?
```

### [50] hash=`32bd2dd708e323c0`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Why doesn't the storm fall into the misty land?What is the ingredient of asymmetrical nuclide are?The world is a dark underground labyrinth, but Numa can guide us to go beyond all things and reach the exit.Fertin, can you see it?Why?It's burning!What's going on?Is somebody fighting with a malice now?What's happening outside the cave?Are you straying?The meditation goes beyond control, you will be thrown out of here!
```

### [51] hash=`f75c40c5544f000f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
This would be a foolish mistake!Your pair on this is us!No man shall bravest the storm and live, including thee.G7!All those illusions.If it weren't for the heat of the stone mangle that wakes me up, would I go as crazy asthey did?This stone reminds me of the spinning wheel.The collector of asymmetric nuclei are.If the reagent turns gold after reacting with the fog here, that means the fogcontains elements that can be immune to the storm.
```

### [52] hash=`acb2ae6b4efc6c1a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
The color changed faster than I thought.The concentration of R is hundreds of times...No,thousands of times higher than in the Manus' masks.In other words,whoever owns this cave can produce the protective equipment of the storm in big numbers.Is that the reason why Arcana is here?Mother, how do I feel?How do I feel?I need to take 37 out of here.So the Abraxas were people from the manors.The fog here can affect people's minds like those around the lake in my suitcase
```

### [53] hash=`919e176c39bf9860`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
The manors found a way to launch attacks without being punished by the bangleWell, don't they care about the price they will be paying anymore.I hope Regulus didn't throw my words to the windI have to get rid of them first and go out to join the othersThe peace agreement no longer works.Is it safe as long as the contracting parties have no intention to fight?The conditions are not clearA reckless attack may lead to the punishment of the bangle.
```

### [54] hash=`1f361f6df6fcbc7f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
I have to be careful with the method and timing of attacking.Typhon won't give up his friends, neither will Stotherby.The body is melting.It turns into a seed.So this is how the manors fight against the restrictions.They sacrifice one man to feed another.Typhon won't give up his friends, neither will Stotherby.everywhere the sacrificed follower has been absorbed by the seed this is somekind of ritual okay of everything 37 can you hear me
```

### [55] hash=`b80518158b186c8f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
don't blink the dead followers turned into geometric symbols is it because ofthe cave so the seed is the form of Manus whenBack when we were spying on them, I told Saneto to screw the peace agreement through the radio.I knew those geometry psychos and the Manus would go mad sooner or later.They were not that crazy when they were solving the math problems.Damn it!What the hell happened down there?The cave is the key to be immune to the storm.
```

### [56] hash=`c98c372422d4e39a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
There is a cave on this island which has the same effect as my suitcase.That's what the Manus are after.What?But...But hasn't she also put on the stone bungalow?Even if she can break free from that bungalow,there is no way she'd let her followers keep carrying out suicide attacks.And if she has signed that peace agreement, how will she take the cave from a pyron?Fertin?What's that?I'm afraid you have overstayed your welcome, Ms.
```

### [57] hash=`f1d31333aa7d5594`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p36`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-洞穴的囚徒｜17~21）

```text
Arcana.I have to regrettably remind you not to overstep the boundaries.I find pleasure in this allegory of the cave.However, has this been unto thee?That too led us to the exile in this cave.
```

### [58] hash=`a3cef291b160418b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Look at you, draped into a ball, meant for a sketch.I saw you the moment I came into the library.The foundation holds balls too?Excuse me, I need to go to the park.She told me you wanted to look up the materials on the mysterious school that believes in numbers here.Masa told me she will thoroughly check the documents in the foundation archive.So I'll go through the books in the SPDM library.If we can find anything about that school, we can be of more help to Versin and her team
```

### [59] hash=`2372ccf6c27d9307`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
I'm sorry Miss Sotheby, but I'm afraid the situation is going to disappoint youWhile you spent the last hour looking for T.Kettler's ear, the kind-hearted monitor assistant already gained valuable access to the libraryBut I haven't found any record regarding the mysterious school that believes in numbers yetWussle said there are so many books here that they can cover the entire back of a strontate beast!
```

### [60] hash=`2d6c24c3c0c48250`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
A bit exaggerated, but, ahem, she's right.Nevertheless, the librarian was transferred to a more important position years ago due to the storm.Many old books are not yet sorted, some even went missing in the chaos.The only relevant materials I could find are the stories of Pythagoras and some books on mathematical theorems.But I don't think they have anything to do with Vertine's issue.I don't do anything to help.
```

### [61] hash=`016f18274e5baf31`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Being emotional, it doesn't work on this professional member of the foundation.With investigation permission, I can't take you out to collect information.But in fact, there is still another reference room only known to the most outstanding monitor assistant.It's a violation to make noises in the library!Please follow me, Miss Sotheby.Thank you so much, Ms.Bwanish.You mentioned ball.I haven't heard that word for a very long time.
```

### [62] hash=`c84605c52fbcf603`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
I remember what Mr.Carson, my butler, had taught me.He said,Express your gratitude to fair ladies by holding a grand ball.I'll write to my father and ask for a brand new unsinkable and maneuverable rock and roll park.I'm sure he will gladly say yes.Manoeuvrable rock'n'roll park?Yes!We can hold a twist ball on it when Bertin and her team are back.Allow me to say no.The monitor assistant of SPDM will never participate in such an inelegant activity.
```

### [63] hash=`efeebb2b902b2748`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Wait, did you just say Bertin and her team?Talk about the ball later.The kind-hearted Matilda Buhanish will try her best to help you with the task.But, of course, it's only out of her sense of responsibility.Not for some personal reasons.The reference room storing unnecessary information.It's a place ignored by most staff.Even so, this careful, reliable monitor assistant will not let go of any details.
```

### [64] hash=`0abe80cb4505f078`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
I hereby officially appoint you as the Chief Assistant of Monitor Assistant of SPDM.I will take my responsibility and teach you how to become a devoted foundation member.What is your first task?Ha!Read through these unsorted old files.All of them.All the archived ones.These are the last parts.Some are discarded administrative documents, low priority materials,and substandard reports written by rookie investigators.
```

### [65] hash=`d4404f4f09e351d1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
By the way, you should know I didn't sort any of them out for you.And they don't necessarily have what you want.It's alright.Leave them to me.I love reading.Better do.Here's the key.Keep it safe.You can sit on the cushion there when you sort out the files.I don't want your dress to stain the stone bench.I'll go see if I missed any files.Listen, this monitor tests you on your familiarity with these files when she's back.
```

### [66] hash=`a9a73b9bcf91ec99`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Cleated.Looks like I didn't miss any relevant files.Quite a long day.I doubt if that spoiled lady can finish all the materials.She must have been bored and fallen asleep, waiting for her tea kettle in the dream.It takes much more than dancing at balls to be a foundation investigator.I'll send her back to that teacher when she wakes up.And it will be the kind-hearted Matilda who finishes the task for her.
```

### [67] hash=`950f15f6dbf11198`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Being a great monitor assistant comes with great responsibility.You didn't fall asleep.Did you sort out these files?and are now the reason why I've decided to write down the whole thing.A long time has passed since the first attack of the most severe crisis in our time,but we are still wondering, what on earth does it mean?That was the eve of the millennium, of which no one had any memories, illogically.
```

### [68] hash=`2d5f24bfd2b04709`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
The next day time was already reversed to 1996, the moment we opened our eyes.We walked out of the building made of grey and white marble as usual,Hardly aware that the sun we based in was from another time.Our survival was unexpected and almost unbelievable in such a calamity which swept the globe.Why did the headquarters of the Foundation survive the reverse?Why couldn't we find our younger selves in the outside world?
```

### [69] hash=`5873c85c351b992c`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Did any other region survive it as we did?What was the cause behind this calamity?I didn't know, nor did anyone else.Things remained unclear until time was reversed again.This time, we all witnessed that rain in the 80s.It became the time-Or she became the timekeeper?So Vertim wasn't born a timekeeper.Didn't tell you that?Wait, no one is born a timekeeper!It's not an inherited title!Anyway, this report includes the secret chronology only accessible to the core members of the Foundation.
```

### [70] hash=`740e22f731aeb09a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
You can only check it under the supervision of the monitor assistant before you become a qualified investigatorNo matter what the reason is, it shouldn't have been shoved in this dusty room like rubbishBut with its authenticity and risk, the genius Matilda Bwanish will fulfill her duty as the monitor assistant and carry out a thorough inspection of this reportIf you agree to this resolution, please nod, Assistant Sotheby
```

### [71] hash=`13f416f5437c42e6`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
That was 1985.A gloomy, miserable night compared to that peaceful morning in 1996 when we wereonly bothered by confusion.We didn't expect time to be reversed again, nor did we understandthe consequence.Even now, I still remember Paulina's desperate cry.One of her henswas already inside the safe area when she fell at the entrance to the headquarters,And that was the only part of her left was the next second.
```

### [72] hash=`c2af5fd5b7b05731`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
The only legacies we found were an engagement ring on that hand, and her favourite bluepolka dot scarf, which we used to wrap her remains in the end.To be honest, I admired those who still remained calm and sympathised with the Arcanistson the edge of mental breakdown.It had nothing to do with the one-quarter Arcanist blood in my body.It was only the kind of empathy which all mankind would share out of instinct in
```

### [73] hash=`1809d9c58a25443b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
face of a hopeless calamity.We lost many, too many colleagues.In the materials theysent back, we even saw all the horrifying phenomena, such as one's veins turning intoelectric wires.Since then, a storm, a word simply taken from visual observation, hasbeen used to refer to the calamity.Of course, we can have a word for the calamityBut what words should we use to conclude all the absurdity and panic?
```

### [74] hash=`775d14339eee1940`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Before the storm we were all familiar with time.It was supposed to be a straight line connecting the past and the future.We followed the line to move forward.We broke free from ignorance, we built civilizations, we developed technologies, we promoted thewell-being of mankind, and we improved our living conditions step by step.We were so sure that we were making progress on the right path.But then, the path was taken away all of a sudden.
```

### [75] hash=`12bd45ac62800617`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Our closest old friend, where are you taking us?To the two most painful war times in the 20th century?The era when no one had ever heard the hiss of steam engines?Or the century when mankind was yet to be enlightened?So far, mankind has achieved a lot in history.Minimos, automobiles, flyovers, railways, hospitals, poor houses.But if it goes on like this, what is the point of all the efforts we have made?
```

### [76] hash=`bf3fd20078dca96d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Now we are like a shipwreck left on the island of time,witnessing the fall of the whole modern world in the unstoppable tsunami.Even though the Foundation has lost a lot of staff members,they are still doing fine compared to Laplace.My younger brother was a good example.He was the most sensible person I have ever known.On the first day of the second reverse, he told me, in a calm manner.At least we have reaffirmed that Newton was right.
```

### [77] hash=`e38721da4b2d8b6a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
There was never an arrow of time in classical mechanics.Neither in relativity nor quantum mechanics.That means this is absolutely normal.Whether the time goes backwards or forwards,even if it starts spinning around like a tabletop football player,they're not against the law of physics.We can go back in time and kick one guy in the middle of gate poppin!The next day he almost fell off the sixth floor due to excessive drinking.
```

### [78] hash=`cf16cef60ae833a4`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
All the perceptions of time and space developed to this day were overthrown.We couldn't find any series to explain the storm in any existing researches.There could only be two reasons for this situation.Either we've been completely wrong all the time,or we've come to a brand new world.And this new world can never make sense in the way of science, or that of physics.It cannot be verified by an independent third party, and it is impossible to be comprehended
```

### [79] hash=`1afea3fdbe13b1df`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
through reasoning.Is it true that we have been going the wrong way?Is it true that those once proven wrong by history, those arcanists who claimedto possess gnosis, are actually on the right path?In fact, the one who put an end to the chaos was indeed not a human.This thing, I had no idea what it was.It claimed to be a machine which never stops working.It laughed the limitations of our brains and the metaphysical mistakes we make ceaselessly.
```

### [80] hash=`737350b83fdece93`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
But it did solve the most urgent issue.A system was built to tackle storm-relevant emergencies after it took charge of Laplace.The first measure it adopted was contacting all the existing branches of the foundationsat the time to confirm the scale of available manpower.Then it built observation stations all over the globe to find if there were any otherregions immune to the storm.After that, numerous offices responsible for deducing the cause of the storm were established.
```

### [81] hash=`d5b94277d24f8077`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Even though there were countless disagreements during the research, at least we had takenthe first step.I handed in the application to take part in this mission, determined to get ridof the fog in my mind.In 1986, I was assigned to the office in Egypt.All my friends came to the dock to see me off, because we knew it could be the final goodbye.Even though we were equipped with the emergency communication devices issued by Laplace,
```

### [82] hash=`92b285f24d343c8f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
we were still not clear when the storm would assault us, or where we could hide nearby.What really scared me was not the threat to my life, but the possibility of dying ignorant.Then I boarded the ship to Alexandria from Athens, and that was when I met.Now when I recall it, it was almost impossible to ignore that group of arcanists on the ship.There were about a dozen of them, all in eccentric stitched robes.
```

### [83] hash=`bcb0eb33a4642bd5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
They were followers of a strange school which mixes arcanum and mathematics.I talked to them.No matter how much that conversation bewilters me now,I was more excited than confused at the time.They also survived the storm in 1996,and they noticed the unusual changes taking place in the world as well.That means I actually met another group of survivors from the Millennium.A mixture of Arkanes who survived the storm?
```

### [84] hash=`1f1b6b9000fad86a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
A mixture of Arkanes and mathematics?The ship on the Mediterranean?Unbelievable!Our investigator actually met this group of Arkanes who believed in numbersand even left such a precious record down on paper.Does it mean we are close to being helpful to Vashin?Certainly.It's what we deserve for all the efforts today.But why did they leave such an important report in the Reference Room storing unnecessary information?
```

### [85] hash=`67d574ab175a07b9`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Did they misput it here after the chaos of the storm?Among them, the most easy-going one was Hugh.He was an engineer, as well as an Arcanist.We shared the same preference for human technology, and that became our common topic.Hugh was in his thirties, red haired, cheeks sunken, and deeply depressed due to some kindof eye disease.He was a decent man, with a prudent attitude, working at a desk most of the time.
```

### [86] hash=`87c8f93721b525c1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
He reminded me of the imperial miniature painting artists in the Sultan's palace.Most of them ended up blind after toiling for their life.He showed me the picture of his daughter.I don't have children, but I could feel his happiness as a father.Although I got along well with you, he seemed quite out of place among that group, whichwas actually led by her.I don't know what words to use to describe her.
```

### [87] hash=`5c6f9297489a44b3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
She was like a meteor shower, a tempest, or an unreasonable catastrophe itself.Her existence was just like her name.It was simple, yet implied a lot.Please forgive me for my cowardice.Even now I don't have the courage to write down her name, if one would call that a name.In fact, she was quite a kind of warm-hearted person.Among all the unregistered arcanists I've met, she was one of the nicest ones towards
```

### [88] hash=`bee1afbc9d11aa11`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
the foundation.She looked young, even though I heard she had a daughter too.Besides, she still possessed the innocence of a child, and that kind of excitement exclusivefor genius.That's right, it seemed the whole world was like a sparkling toy to her.Our communication was heart-stirring at the beginning.Both of us were eager to find out what was happening, like two shipwrecked victimsgrappling at each other on the sea.
```

### [89] hash=`646b5b00c629aaa5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
But I didn't have the slightest idea what she was talking about, actually.The problem was not the typical communication issues between humans and arcanists.I was sure the language we used didn't pose any obstacles, but still I couldn't understandany words of hers.I would believe that one is highly intelligent if one can name all the factors of 11,567without thinking.What this one said was illogical nonsense which no one could ever imagine.
```

### [90] hash=`a0cfa4ad8af0c4ea`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
She claimed that there is a world of numbers, above all else, where the non-physical essencesof all things exist in the form of timeless, absolute, unchangeable ideas, and that thephysical world where the time flows is nothing but an appendage which has never been realor true.And that's why the chaos in this world is not worth any attention, and we shouldfocus on what happened to the supreme existence, an utter disaster combining modern maths with
```

### [91] hash=`5671bf8b72645709`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
ancient superstition.I saw another hubaristic arcanist pretending to be the prophet byreliving Platonism.I don't even bother to mention the Balderdash on soul numbers.Even the New Age movement could use some of her absurdity.But that was not yet theend.She even claimed to be aware of the exact year when the next reverse would happen.But when I asked her about it seriously, she said,My apologies, I've made an oath.
```

### [92] hash=`df58ae21283419c5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
I shall and only shall reveal the demonstration to people who have their own soul numbers.I'm not sure whether she was making fun of me or being serious,but I had this feeling that she was eager to tell me how she was granted the secret through a moment of aflatus.It seemed she just saw through the loss behind all things, instead of finding them throughlogical deduction.Can't you see it?It is right in front of you.
```

### [93] hash=`d2004df746f19d76`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
After I expressed my inability to comprehend her words 30 times, she finally gave upand proffered regrets.I'd rather take it as a new kind of humiliation.What really irritated me about her, however, was her contempt towards science and allthe scientific research methods.As far as I am concerned, the value of a theory lies in its reliability, universality andgeneralizability.Our pursuit of the truth has laid the foundation of modern science, allowing us to change
```

### [94] hash=`6ed9a4e210eec646`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
the world.Yet, in her eyes, the value of a theory lies in its beauty.I talked to her on the current situation, and I told her how we would save lives anddeserve the hard-earned technology of mankind if we could find the pattern of the storm.It was of course not an easy thing to do and would take enormous manpower.So I askedher sincerely to join the Foundation.Yet again she responded with contempt.
```

