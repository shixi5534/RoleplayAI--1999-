# 剧情图谱抽取 · batch 025

- 角色：`wu_ming_zhe`
- 批次：**25** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.9」｜offset 475
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_025.jsonl`

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

### [0] hash=`9ba6517579a7b762`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
I apologize, Miss Kakanya.Perhaps the result of our work will notreally help your situation.You said the knot works on both humans andYes.That is more than enough.This is the best news I've heard so far.There's a chance for everyone.I have two more pieces of good news.First, the curse is not inevitable.Our experiments showed a 0.49% likelihood of no side effects occurring at all.Second, the closer the storm gets, the more Pneuma fills the air, leading to a
```

### [1] hash=`e7b097745559e393`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
success rate of the ritual.Yet, even with these factors combined, the rate of success is still extremely low.It's alright.With millions of people trying, there's hope that at least one person will succeed against the odds.Thank you for sharing this with me, madam.I will do everything I can to spread this not in Vienna.To the Arkanists, humans, Magyars, and Germans, they are all my people, regardless of their
```

### [2] hash=`599011d31ca0d864`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
social status, profession, or race.They all deserve the right to survive.Madam Lucy, I can only assume you acted impulsively and overlooked the proper application process.The Knot is new and not ready for widespread testing.Distributing it in Vienna could lead to more casualties or even fall into the hands of our enemies.My brothers and sisters, put down your cups for a moment and lend ear to me.We were born extraordinary, yet estranged from the world around us.
```

### [3] hash=`6cccaea6436d6e9b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Throughout the ages, we wandered the world like a ship lost at sea.Despite the instability and chaos, we persevered, and together we sought after the truth thatwould illuminate us all.Through introspection and contemplation, we cleansed ourselves of hatred, madness anddelusion, and embraced the value of beauty and harmony.Yet now, our shattered faith mingles with the rubble of this phenomenal world, as specks
```

### [4] hash=`bcec6f49072d3e06`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
in an unjust timeline, as remnants of a tide long receded.The dream of the transcendental world is broken, and the order of the transcendental law is no more.Our sanctuary has crumbled, exposing us to live in a world filled with conflict and turmoil,where we will be trapped in the wheel of birth, doomed to repeat the mistakes of history for eternity.But do not despair, for there is another way to the truth.
```

### [5] hash=`944bd979760be31e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
It is a path fueled by unbridled passion, one that was stifled by moderation and restraint.A path that transcends the individual, breaks all boundaries and limitations, and leadsus back to the essence in a fiery blaze of glory.This path is the emanation which we stride into for the ultimate truth of ourjourney.Doctor?Finally, someone I know!Ilich, gather everyone you can and havethem read out these steps in the plaza for all to hear.
```

### [6] hash=`17dee823f5024cbf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
If possible, go to thetelegraph office or use a printing machine to copy flyers.Distribute asmany copies as you can.I'll go to Leopoldstadt and find the GarkusThey know where to find abandoned military hot air balloons.What are you talking about, Doctor?People are too busy trying to escape.I want nothing to do with those crazies.This?A guide for tying knots?Don't you know the world is about to end?
```

### [7] hash=`0d4c5e69506c4247`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
So many warnings.Who'd want to read this?The people who want to survive will read it.I can't guarantee anything.It's a gamble for our lives.But people have a right to try before doomsday arrives.Trust me one more time, please!Fine, Dr.Clara.If this works, your coffee for the rest of your life is on me.I needed a test!I deciphered the code of appearance!Are you joining them, Ms.Marta?I find myself uncertain of which way to go.
```

### [8] hash=`33c47a4c0b8b43ec`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Would you kindly give me some guidance?The guidance I can offer you is limited, Ms.Marta.I think fate knows its own fate better than anyone.Thank you for your advice.I think I understandDear child look at you.You're exhausted.Couldn't be of help then but it's okayThe party is over nowAt least let me brush your hair darling or your hair will get all knotted and it will hurt you when you try toUntangle them.
```

### [9] hash=`07820cb2e3b1345b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
I'm not surprised an old friend of ours notDirtiest knots are tied with rope.Knotts are often found in many stories, signify promises, counting and measuring, an instrumentof salvation, and one of execution.I could go on all day.The influence and power of knots can't be overstated.It is said that it was in the cutting of the Gordian knot that Alexander becamethe great.Just touching the meter's long rope provides blessings to the faithful in
```

### [10] hash=`263fff8eb163c0ae`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
Bellum.And tiny knots on strings can carry the history of an entire people.The ancient Inca called it khipu.The intricate variations of hundreds of fabrics, colors,and lengths of strings were used to record their stories through the ages.And to thinkShakespeare only had twenty-six letters to create his masterpieces.Just look around you.Don't sailors use knots to mark depths and men's sails?Or coachmen tying knots to rein their horses?
```

### [11] hash=`9b3b5b4cf7a4354a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p27`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（27.酒神颂.1/13 20:45）

```text
An anti-respectable lady or gentleman knows the knots they must tie about their necks to stay in fashion.Consider the knot-like helix structure of DNA and the changes in states of matter.Invisible to the naked eye?There you go, I hope you keep this not as a record of the words we shared here
```

### [12] hash=`0c31a2a74508dbdc`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
I...I don't understand.I should be giving them my blessings.They're brave enough to return to the essence.But instead, sadness washes over me.I should feel happy for Sophia, now that she knows her soul number.Yet, I am filled with sorrow.Why did you all leave?Is it because I wasn't fast enough?Is it because I didn't do well enough?Thirty-seven.Leave the island to the world outside.Ms.Vertin, you're clearing a path out of the mires of the Phenomenal World.
```

### [13] hash=`c158d2d9a79dd02a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
I sincerely hope you will steer it away from the horrors of war.It's our duty to do so.Also, the person you were looking for, I am not familiar with a biographer named Erd.However, in my recollections from the previous six, there was a lady with a soul numberjust as unique as yours.Are you saying...Sadly, these vague scraps of information were all that I inherited.I hope they will be useful to you.
```

### [14] hash=`df31e89766c1e8c0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
I'm returning to the cave, 37.There are still people who refuse to be caught in the cycle of hatred or give in to unrestrainedpassion.The entrance to the sacred place may be destroyed, but the people's faith is yet to be extinguished.We will persist in studying the scrolls, copying the scriptures and restoring our halls.We will worship the ancient one in penance and work to rekindle the flame of our broken
```

### [15] hash=`d03217be6e84cc0f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
beliefs.The island is a manifestation of our choices, a haven removed from the phenomenal world,a place of order and harmony, and it is our determination that will sustain its tranquilexistence.No, your choice has already been made, 37.You should not go back.The sorrows anddoubts you have can only be alleviated by experiencing the outside world.Thousands of500 years ago, the first faithful ones fled from the Roman Empire and journeyed to this
```

### [16] hash=`89afcab7efb612d9`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
island, where they founded the school of Eperon.500 years ago, refugees from Arabia found shelter here.They filled the cavern's shelves with copies of their writings and texts.Half a century ago, scholars who had their research exploited for warfare came and expandedour knowledge on modern mathematics.There were many 37s and 6s among them, yet, are we any different from them in essence?Even if we are no longer here, the numbers 37 and 6 will still exist.
```

### [17] hash=`d8a86efd54e7caa3`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
Even if the islands sank, these numbers would reappear elsewhere.The integer sequence is infinite, 37.Rather than clinging to a set of specific numbers, you should go and work out your own calculations and conclusions.So now you're choosing to be wise and look on.But I don't understand.How could one be wise by being uninvolved and looking on from the sidelines?you overestimate wisdom miss verton it can't do everything wisdom can free
```

### [18] hash=`8c4da45a66541bda`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p28`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（28.数轴的两端.8/15 9:42）

```text
people from ignorance but it can also lead them to a nihilistic void yetsomeone will always seek this wisdom even if nihilistic to briefly riseabove their worldly troubles and find some relief and someone will have tostay here and provide a neutral haven for the drifters of the phenomenal
```

### [19] hash=`57d632dc39817ef8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
We are prisoners within these cavern walls.Our gaze is held captive by the shadows thrall, until our hands clasp and our chains rattled.We united to break free from our shackles.The sightless joined forces with the soundless, and the voiceless uplifted the helpless.Together we assembled a sliver of truth, a piece of the world hidden since youth.Have you got something for me, Mesmer?They asked me to give this to you.
```

### [20] hash=`ba483cbf9f6629cf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
The culmination of our research.The crystallization of man and all its wisdom.The protective gear against the storm.An umbrella.Something you personally don't really need.It's called the equilibrium umbrella.This is the first model,consisting of a converter, a harmonizer, and a ritual core.The converter generates a balancing field that can cast rituals in the storm,taking account of the wielder's capabilities.
```

### [21] hash=`f4d4ede152ba8f2f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
The harmonizer's markings are inspired by the scroll of a Peron.Madam Lucy tested it against 162 known side effects and found it to be highly effective.The original scroll has been returned to the island.This is only a simplified and duplicated rendition.The 162 curses aren't all of them, right?Correct.There may be other unknown side-effects, so the umbrella is only a prototype in the testingphase.
```

### [22] hash=`1b5ab8876a0cf89a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
And the ritual core, at first it was called the 37 Lucy Knot in honor of the two maincontributors.However, both of them turned it down.Yes, I still remember what 37 said at the time.She would rather name it after the mathematical properties of the knot, even if it's toomuch of a mouthful.Thirty-seven is not a name, and the truth should not be dressed up with anyone's name.I only found it.I didn't invent it.
```

### [23] hash=`f7fe31d593b89571`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
I don't need something named after me to prove my sense of existence.But I'm not on the island anymore.I can understand that the imaginary numbers need to honor the discovery.You may use another contributor's name for it.I'm willing to accept that.Madam Lucy showed no interest in the naming rights, so it was transferred to the third major contributor, Adler Hoffman.Sadly, researcher Adler also rejected the offer.
```

### [24] hash=`3848d02f5398b439`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
At first, we nearly ended up using the date of that day as the name, but he changed his mind after confirming he could use his family name instead.The Hoffman Nut?You named it after Madam Hoffman?But with this umbrella in hand, I will venture into the new world and marvel at what's tocome.Will the sucker-tort taste the same?And lastly, the asymmetrical nuclide R in the handle of the umbrella is supposed to
```

### [25] hash=`3df5e6efcb857684`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
protect against the storm syndrome, but this still needs to be confirmed through testing.It's okay, this is the one thing we need the most.If you have no further questions about its usage, I'm heading back to the rehab center.The afflicted researchers there are in dire need of my magnet therapy.Don't you think one is not enough for my needs?I think five.No, fifteen might be more helpful.My suitcase can't protect humans from the storm.
```

### [26] hash=`6be535b8d022fd8f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
They'll need the umbrella to survive.In the future missions, I may encounter lots of-Just a reminder, timekeeper.Huh?That's not what I was talking about.I'm talking about the brave and glorious sacrifice of my apple the second.Don't you think the foundation should compensate me with a shiny new ship?Oh.Oh?What do you mean oh?Are you saying you totally forgot about it?Easy, Regulus.Those people are likely buried in paperwork right now.
```

### [27] hash=`5cc0897e350d4752`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p29`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（29.伞与结.8/21 12:15）

```text
Just be patient and wait.Lillia, how's your commendation ceremony?Heh, they rewarded me for escorting the important item during the storm.How is delivering a scroll worthy of a reward?I'll say someone should be grateful I didn't crash into the committee building.Take it.Might be useful for your alchemy.It's made of pure gold!On behalf of the pirate community, I thank you for your remarkable contribution to alchemy!

Huh?Funny you say that, Seneto.Now we have two new ships.
```

### [28] hash=`483df561b79b0870`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
Nothing's happening.Miss Virgin, your attention please.This is a public inquiry, and your answer determines the fate of you and your friends.There will be a vote on your punishment, considering the leak of the island's coordinates and the damages caused by you and Manus Vindicte.Yet, in the past two hours, you've looked at your watch ten times.Forgive me for being blunt.What could possibly bother you more than your sentence?
```

### [29] hash=`4b4650e91d94f805`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
My apologies.Let her look, 888.Doesn't it occur to you that time is also in the form of numbers?Perhaps she's waiting for her lucky number to come.Besides, what conclusions have the good people here made?We were brought together in this great hall today.For misfortunes have struck us in the past week.Manus followers were found dead in our sacred place, the Gorgon current was cut off, anda human army has invaded our land.
```

### [30] hash=`ab21cda849452fcd`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
There are also the territorial disputes, the threats from external powers, and the conflictsbetween our guests.As you can see, our guests have brought us quite the unexpected gifts.They will give us their explanations.But whose words should we trust, those of the Foundation or Manus Vindicte?I swear on the Stone of Truth that I have no knowledge of the leak.We never gave any information to the humans.
```

### [31] hash=`1dbb382c83563926`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
As we speak, the Saint Pavlov Foundation is taking measures to mediate the territorial disputes from outside the island.But you did report everything here to the Foundation, and you don't know what they did with the information, do you?A questionable defense, a doubtful explanation.Why should we trust her?We all know that the Foundation is closely associated with the humans.They are the false friends of the Arcanists, with their crocodile tears and broken vows.
```

### [32] hash=`555b7dd2b84ae614`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
While many may have changed over time, their nefarious human taint lingers.Besides, why should we seek collaboration and assistance from an organization that'sseven years behind us on the study of the emanation?But rush not, brothers and sisters.The moment of decision has not yet arrived.Let's give our old friend Manus Vindicte a fair and equal hearing before castingour pebbles into the pot.Indeed, the Foundation's understanding of the emanation is seven years behind ours.
```

### [33] hash=`f28e49f1f47c4d57`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
However, our Manus friends here are unable to speak at all, let alone understand complexmathematical principles.Please enlighten us, Miss Arcana.Why were swaths of your followers found dead at the door of our sacred place?Did our math lessons drive them to madness, causing them to bash their heads againstgates of truth like martyrs.So it would seem.What?I must confess that ourfollowers were ill-prepared to take on the wisdom of the island, but we did
```

### [34] hash=`b7ecc4202b2514d6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
come seek mutual development with sincerity.I trust you are aware of theassistance we have provided over the years in this world of matters which youthough reluctantly relied upon.As to this debate, I was once told a storythat now seems fitting to recount.Pray, share with us.Thank you kindly.Tis the story of the circle.A young artist told it to mebefore I arrived on this island.In the ancient past,
```

### [35] hash=`f00757cde399de05`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
amid a world of primitive instincts and ignorance,the first intelligent mind awakened,overwhelmed by the enormity of natureand dismayed by its own insignificance, the creature was shaken to its core.In an act of defiance, it drew a magic circle, shielding its powerless self from the formidable world beyond.This was the first magic, when the primitive man mastered the Numa withinand wielded it against the relentless forces of nature.
```

### [36] hash=`c11be23d636464e2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p2`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（02.蓝与灰.1/12 20:30）

```text
In that process, man hath gained a deeper understanding of the boundaries and limitations of its power.This is the tale of the First Circle.The Circle shielded us, and its protection benefits thee to this day.What I find intriguing in this story,Man hath established its existence, recognized its boundaries, and learned the purpose of life, all by relying upon this very circle.37.What's wrong, 37?Has fallen ill.

Ah!What is going on?Is that a hailstorm?No, I don't think so.Those are Abraxas's.Falling from the sky to the storm.The storm of this era is here.
```

### [37] hash=`f302cdf328771a7e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
15 plugs.This should be enough to cover all socket types at our destination.Simone, pass me the experiment log, please.Madame Lucie, is it true?Are you leaving Laplace?Yes.The inquiry is over.This is the decision of all parties involved.You have got to be kidding me!After all the incredible contributions you've made, they're suspending you?This is absolutely ridiculous!Without you, there would be no Umbrella, and everyone would have died from the side effects!
```

### [38] hash=`88f4a3b05c9cdee0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
But many did perish because of me.I had underestimated the danger of the ritual, and it ended up spreading uncontrollably.Did you not once have the same opinion, researcher Adler Hoffman?I...It is surprising to see you change your mind so quickly, but that is just what Laplace needs.The spirit of rationality and self-evolution.I can imagine how they came to this decision.They must have considered the backgrounds of all the employees,
```

### [39] hash=`ea893ffbf7ec203c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
including their social status and race.After eight years, we finally created an umbrella to withstand the storm.However, our methods for achieving such progress and breakthroughs were too much for some to handle.People needed an outlet for their frustrations, so someone had to be held responsible for theaccidents and casualties.Numerous complaints have been filed against me, accusing me ofbeing a cold, heartless opponent of humanity.
```

### [40] hash=`9626363e47e033c8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
Within the Foundation, Zeno and even here,Some are starting to question the idea of having an awakened piston as a leader of LaPlace.They argued about my arcane abilities, unsure if I had them under control or if they werebecoming unstable and affecting my ability to make rational decisions.I did give the nod to Miss Kikanya in violation of the confidentiality agreement,But ultimately, it helped people survive, and that is all that matters.
```

### [41] hash=`74032a30c7b8b646`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
So they're questioning your standing because you're an awakened, an arcanist?They're doubting the rationality of a machine that values technology and progress aboveall else?Could anything be more absurd?Even I, a human, was on the verge of giving up!It was you who convinced me to save our species!My question is, why are you so upset?This does not affect you.In fact, you may be promoted.Laplace is setting up a new department, and you and Ulrich should have been invited to head it.
```

### [42] hash=`fb9628a9816260a2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
Maybe you should take up that offer.At least you will get a promotion as a just reward.By the way, Ulric ended up receiving a medal.But like you, he was not exactly thrilled either.He is outside the committee building, refusing to eat in protest.But everyone knows how resilient the awakened can be.It is going poorly.I will suggest that one of you take this position.No one knows this research better than the two of you.
```

### [43] hash=`e950bdf1eb74e2a6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
Not a chance!The research must progress, and you also need to ensure that the results will notbe abused.Scheisse.Your height.The punishment does not bother me, researcher Hoffman.Power exists only in your dictionary, not mine.From the moment of my awakening, I have been unable to comprehend you creatures.And even now, that remains unchanged.We operate in different ways, just like howour fuels differ.
```

### [44] hash=`abeff2ae6ecbc99f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
But the bright side is, our paths align.Whether we are creatures or machines,humans or arcanists.Most of us strive for a better life.It is this primal desirethat drives progress.That is why I put on the mask of a human and work on improving myappearance and speech, all for the sake of better communication with you.Unfortunately,my efforts do not always pay off.Some say that the more human-like I appear,
```

### [45] hash=`7dca9d6c4f246c6c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
The more different I seem, but I am who I am, and my motivation is not to gain recognitionfrom others.Our Align Path leads us to progress, and that is all there is to it.Thanks to the invention of the Umbrella, Laplace can now resume its research unhindered.And, if there is someone better qualified to lead, I am more than willing to remaina humble cog in their machine.Besides, Miss C introduced me to a beautiful resort.
```

### [46] hash=`e1b507058d7e5f31`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
The lake there is rich with arcane power, perfect for an awakened arcanist like me.Not only is it a resort, but also an independent team with a good amount of freedom.My only concern is if they have adequate power supply.Oh.Rust might be a problem.Perhaps I should ask Researcher X about his Titanium-D Rustmachine.Time to go, Simone.Madam Lucy, please take a look at this before you go.This is the report you compiled during
```

### [47] hash=`9441ee9200e4e1c5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
the storm countdown, detailing 126 side effects and how the scroll alleviates them.I have some questions about the data for Type 34.Yes, I can see a few errors in here.Unfortunately, I have to complete all of the handover procedurestoday.Perhaps you can ask Mr.Ulrich about it later.The side effects left a mark on you, didn't they?There are 162 side effects, not 126.There was also an obvious typo in the data for Type 34.
```

### [48] hash=`a2f98a8a75355372`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
We noticed it long agoand corrected it.Took only five seconds.You sacrificed so much for this report, yet youcould not see such glaring mistakes.You called me Researcher Hoffman earlier,a name you haven't used since you took over Laplace eight years ago.To avoid confusion with my sister, you and our colleagues started calling me Adler instead.How much data did you lose to impair your research abilities like this?
```

### [49] hash=`ce7585dbd4819abf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
Is this why you have to leave Laplace now?The progress you've made has helped so many, but at what cost to your own well-being?We should go, Madame Lucie.Hmm, goodbye, Researcher Adler.Thank you for correcting my mistake.I'll take up that hole and do what you've been nagging me to do!I'll take care of those pesky committees!But just so you know, I'm not doing this for the higher-ups who look down on us!
```

### [50] hash=`a499ab35e18cfba6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p30`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（30.谢幕词.8/21 14:00）

```text
but for the people who look up to us from below.Perilousy!All attention!Salute!Simone, why are they throwing papers at me?Are they rejecting me and banishing me?On the contrary, madame.They are showing their reverence.I see.Let us go, Simone.I miss the Laplace chargers already.There is a 230-volt bath at the resort, right?
```

### [51] hash=`444d87fcb430c6ed`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
Nothing beats a Dr Papa after saving the day.Worrying about other things?We just took down Okana and snagged the storm immunity.Why not kick back for a minute, mate?The best bit about this whole thing is I ended up with two ships in one day.Let's treat ourselves to fizzy drinks and get all puffed up today!To Vertin!Aside from my sinking ship?Not too shabby.Plenty of adventures surprises and treasures the only problem this bloody island
```

### [52] hash=`2553ff139a6a56ab`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
Can't even eat beans without getting a lecture.What's with the Abraxas biting people?Don't they understand that rules are made to be brokenNo way people this obstinate could ever write good lyrics.Can you imagine?spitting rhymesHa!I'm dead!But let's be honest, that last mill was absolutely smashing.They went out with a bang, didn't they?Striding into the storm to prove their beliefs?How cool was that?
```

### [53] hash=`a089f40023b3635a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
I was half tempted to join them, but I reigned it in.Not today.This rockin' pirate will never suffer the same fate of those number crunchers.Because my grand finale will be the one that rocks the world, mate.I'm surprised there's another great mind like mine in the phenomenal worldThey must have a special number.I think we'll meet again soonMm-hmm.Hey vertsen come drink with meOnly kids like regulars drink soda.
```

### [54] hash=`c59ee411ad6e9070`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
You should get used to vodkaI'm underage, tooSheesh, you were never the model student, but now you sound like one if you're not into drinking holy waterAt least chat with me, or the joy of drinking will be lost.Now that's a topic to get the sips flowing.Who isn't up for a little reminiscing while drinking?I became a pilot because I love flying, obviously.Ah, the wind rushing past you,the thrill of acceleration,
```

### [55] hash=`ef66deae8e6a26ac`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
the weightlessness and adrenaline while chasing the enemy.The best part is the screamingwhen you slice apart their plane.Call me disloyal if you want,but to me, Zeno was just a place to get a pilot's license.Ever since I got my papers and an aircraft,I had been looking for a place to fly freely.In Zeno, I needed a mission to fly.At the foundation, my role would have been reduced to a mere instructor,
```

### [56] hash=`d84e917b0dc11031`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
so I looked for a place with endless problemswhere I could have unlimited fun in the air.Can you guess where I ended up?Your suitcase.Bye!Maybe you can join me for another ride sometime.Not like the last time when you were sick, but in an actual air fight.Not like the last time when......part of a gentleman and helped me carry the suitcase.What's in it?The moving pictures of Typhon I chose for my new island friends,
```

### [57] hash=`180469f8baf64c45`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
Including Typhon and the auto island, Typhon and the Pegasus, Typhon and the battle against Jupiter, all are perfect gifts for new friends.I know what you're worrying about, but don't worry.Miss Morsal approved my request, so I asked the Foundation to make copies for everyone.Even though she said something like, no copyright issues in this time and year.If a lady always responds with, I need to think about it, then her answer is no.
```

### [58] hash=`53969a26c9e82add`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
She's not into balls.No more spoonish for long, Vertin.Could you possibly share her interest with me?I knew it, Vertin.You must really enjoy lugging seatcases around.A beautiful morning to you, Verdin.As you described, this is a forest worth looking forward to.Branches of the trees are arranged in a perfect pattern,showing a sense of harmony and unity.I can see the gentle and caring nature of the guardian of the forest.
```

### [59] hash=`5cf6d949f1f5a2f2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
That is high praise.Indeed, all branches follow the same pattern and grow in the same way.The edges of squares give rise to triangles,and the edges of triangles give rise to squares.I may not be familiar with this trimming style,but I can hear the trees humming with joy.That pattern is called the Pythagoras tree.I have heard of this Pythagoras.He was a mathematician.Little did I know that histheorem could be expressed on trees.
```

### [60] hash=`a98d25659260f96e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
My respects to the sagacity of the ancients.I am grateful for your concern, Burden.I am well.The Foundation did not make ithard for me to repair the Square.Instead, they collected data on the potential damagethat the proliferating plants could cause to the Foundation's infrastructure.Theythoroughly examine the growth potions made by Ms.Sotheby.So it seems our nextprotest will need a new strategy.It won't be as easy.
```

### [61] hash=`8b7de34d0cf983b9`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
I would love to talk to thetrees again.They are delightful.Farewell for now.I would love to talk to the tree.Nice to meet you, Timekeeper.I have intended to visit you, but traininginterfered.Forgive me for meeting you like this instead.Yes, training.I was instructed to leave Laplace and go on a vacation.Just as I was wondering where and how I was going to accomplish this task, Madame Z recommended
```

### [62] hash=`e189158e2f156146`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
your suitcase.So I prepared this spare body for easier communication with the members in your suitcase.Considering the presence of underage individuals, I opted for a softer material.Hopefully, they will be comfortable with the temperature of my metal.As for my training, it is to master the art of resting.I would like to inquire, how does one define the concept of resting?Apologies for the interruption, Timekeeper.
```

### [63] hash=`bb2fdd7ad7dfdb53`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
This is a paradox.My work has ordered me to rest.If I were to stop working, then I would have to stop resting too.Please provide an alternative suggestion.See you soon, Timekeeper.Remember, we still need to complete the Resting Plan.See you soon, Timekeeper.It's a seven-letter word.The second letter is A and the third letter, I.Failing, failure, jailing, painful...No, not these.Open your mind.What about Rainbow?
```

### [64] hash=`a0c74ad43703edbe`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
Hmm?Good one.Then the six is O, the start of opportunity.The research team will become its own department and focus on studying the equilibrium umbrella.And Ulrich and I are going to head it.Once he's done with his hunger strike, we'll have to decide who's going to be in chargeof all the boring stuff Madame Lucy couldn't be bothered to deal with.Stuff like politics, getting along with people, and working with other organizations.
```

### [65] hash=`f5781cafb749561e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
I must say that Laplace is being overly technocentric here.They couldn't find anyone else to head the department, except for this unsociable researcherand this awakened thing that can't even show emotions like a normal person.The social scene at Laplace is going to be a disaster.So were you just here for small talk?I was told it would help with my re-socialisation.Thanks.I was told it would help-Back for more, Dr.
```

### [66] hash=`9f440a120a72e522`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
Pappa!The brown bean juice the math geeks hate so much?You think I'd make a fuss again?Coffee would be lovely, but right now Dr.Papa is my jam.So, uh, maybe next time.We already have the equilibrium umbrella saving us from the storm.Just gotta put it into production and distribute it worldwide.Give it a hundred years, it'll be the year 2000 in no time.Alright, maybe that's a bit too long, but we can find a better way for sure.
```

### [67] hash=`b55cb77ea7ca374f`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
And there's no solid proof that the storm only takes us back to the 20th century, isthere?What if, as the Dorky Biter would say, there is such a thing as a white crow?Maybe the next storm will take us to the future.A future where we can sail into space!Oh!I'm gonna be a rockin' space pirate, that's for sure!And we'll pop over to Leo and see if any aliens are up for some rock and roll!Glad you enjoyed that.
```

### [68] hash=`fa18d8a3c7543d72`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
If you ever want more Dr Papa, I'm here for ya.You're early for our reunion.Is your watch telling the wrong time again?This question is unresolved.The outside world is too murky, too distant from the essence.Zeno?It's a party over there.They've been wanting to erase Arkana from existence since 1999.And they finally did.The bomb flattened the entire military base, leaving nothing behind.The authorities have officially confirmed her death.
```

### [69] hash=`d5ffc53bdfefb9f6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
Now everyone in Zeno is celebrating the victory.There was a commendation ceremony.Even the dogs were honored with medals.But accolades mean nothing to me, so here I am, talking to you.Paka!Maybe you can join me for another ride sometime.Not like the last time when you were sick, but in an actual air fight.Inverton, we have assistance to you.Yes, another storm we braved together.Even though there was a tense atmosphere before the storm, everyone was on edge.
```

### [70] hash=`5efa972ade1e3e2a`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
her, one must first understand her intentions.Manus vindicte's purpose is clear, but Arkanasis a mystery.She didn't care about anything based on the time I spent with her.In accordancewith the laws of nature, fruits fall, seeds take root, and trees bear new produce.Thetree can be pruned, its fruit thinned, and even cut down to change its appearance.Yet the inherent law of nature cannot be altered.
```

### [71] hash=`7f665085472e0be4`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
To me, arcana is like an unchangeable law, one without any purpose.It cannot be overcome, just as it cannot be changed.I would love to talk to the trees again.They are delightful.Farewell for now.More advice on resting, timekeeper.I am glad that you and I have come to the same conclusion.Based on my observations, resting is what one does to recharge their physical and mentalsystems through the combination of a balanced diet, suitable exercise, and sufficient sleep.
```

### [72] hash=`96a1cf1a78ed7a66`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
But these measures do not work for the awakened.I require no sleep, my sustenance is electricity, and exercise quickens my deterioration.I suppose the closest definition of resting is the continuous charging of electricity.But from your perspective, can this not be categorized as the sin of gluttony?See you soon, timekeeper.Remember, we still need to complete the resting plan.I am no alcanist.I can only draw conclusions from what I see.
```

### [73] hash=`727413b5039365d5`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
So if you have something to say, say it directly.She dumped a mess on Ulrich and I.The research team will become its own department and focus on studying the equilibrium umbrella.And Ulrich and I are going to head it.Once he's done with his hunger strike, we'll have to decide who's going to be in chargeof all the boring stuff Madame Lucy couldn't be bothered to deal with.Stuff like politics, getting along with people, and working with other organizations.
```

### [74] hash=`388a848feeef3d63`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p31`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界1）

```text
I must say that Laplace is being overly technocentric here.They couldn't find anyone else to head the department, except for this unsociable researcher,and this awakened thing that can't even show emotions like a normal person.The social scene at Laplace is going to be a disaster.So were you just here for small talk?I was told it would help with my re-socialization, thanks.
```

### [75] hash=`b4564c77d9d0045e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
Bring me more straps, I need to hold him down.Farton?Thought I would get some rest.It's been a while since we saw each other outside the foundation, hasn't it?I should probably thank you for the extra work you're causing me.Finally, I have a chance to escape the daily grind and enjoy some fresh air.Even though some of the foundation staff are starting to see me as your go-between.Whatever.It's nice to get away from the screaming patients once in a while.
```

### [76] hash=`571fb0ab259fcbe8`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
Here, the equilibrium umbrellas you requested.To do what?Be your errand girl?Sadly, the number of people losing their minds only increased over the years.I'll never be able to leave this job.You should continue your efforts, Veriton.Find ways to minimize the impact of the storm on people,as you did with the equilibrium umbrella.that'll save me a lot of trouble.It's no big deal, just part of the job.
```

### [77] hash=`c085fced782f0602`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
Now, if youdon't mind, please verify the delivery and confirm receipt of the items yourequested.The faster you count, the sooner I can take a break.Done withthe counting?There's no need to hurry.Get the numbers right, Veriton.They aresaving when they recited the incantation.The survivors were impacted in twodifferent ways.Some looked fine on the outside, but their minds were definitelyunstable.Of those people, some were just tired and having a bad day.
```

### [78] hash=`2e63cb5a43a1da15`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
I put themto sleep.That was easy.There were also people who were severely deformed bythe curse.They had changed so much that they were unrecognizable.Thesepatients quickly adapted to their new appearance and began to enjoy scaringtheir colleagues.Sometimes their pranks would go too far, and the traumatizedvictims would end up coming to me.The sane arcanists are now more troublesomethan the insane.
```

### [79] hash=`3ea533f0666b4a69`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
It just goes to show how unpredictable arcanists can be.It'sno big deal, just part of the job.Now, if you don't mind, please verify thedelivery and confirm receipt of the items you requested.The faster youThe sooner I can take a break.Finally caught you.Can hide from me?Did you really think you could sneak off to the twist ball without the knowledge of the monitor assistant Matilda?Twist ball?You can't fool me.
```

### [80] hash=`62eeb491ad6bacd6`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
The lovely Sotheby has given away the details of your clan.You should feel lucky that I'm soft hearted and generous with other people's mistakes.And be sure to invite me.As the monitor assistant, I am obligated to be there and supervise.Join you?You mean leaving here with you, also with her?And trick me into breaking the rules?I will become a foundation investigator all on my own.And I will outdo you and Sonnetto in this position.
```

### [81] hash=`348709a54cc7b28e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
You're going to join me, not the reverse.Which is...Not another ball without me, I should hope.Clever than this 13.You know you can't fool me.I will be watching something you want to tell meI never said I wanted a partyUnlike you I've been keeping myself occupied as the monitor assistantAnd I already have plans for my next holidayAnd I will be visiting my mother in the one after that want me at your party make sure it is scheduled after my family
```

### [82] hash=`3e5f3a011cafd11b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
time which isAnother ball without me.I should hopeYou're cleverer than this, Fertin.You know you can't fool me.I will be watching.Congratulations, Fertin.The Foundation is pleased with your recent performance.I am here to award you on behalf of the Foundation.I know you're not a fan of these ceremonies, so here's your medal and a brief statement on your achievements.You could say that, but some wasted no time in securing their next step.
```

### [83] hash=`4b3ac8802cedb93e`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
They are already seeking partnership with Laplace on the development of the Equilibriumumbrella.The umbrella will allow the foundation to move freely during the storm.The committee should announce a new bill on field investigation soon.The balance within the foundation will shift once more.The politicians will be busy.Speaking of balance, we should be equipping frontline investigators with equilibrium
```

### [84] hash=`8ccec607f5f8f25c`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
umbrellas as a top priority.No need to rush, Burton.Take your time and rest.Enjoy the company of your friends before you set out again.Don't worry about the reports, I'll handle them.You've been busy ever since becoming the timekeeper.And you deserve a break.Is there anything else, Burton?That was nothing compared to what you and your friends have done.Even though we now have the equilibrium umbrella to shield us from the storm,
```

### [85] hash=`6f4745df52b62a89`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
We still have ways to go before we can truly understand it.We will get there, Vertin.Slowly, but surely.No need to rush, Vertin.Take care.Enjoy the company.Don't worry about the report.Good morning, or evening, my lady.Just as expected, the wine on this highland is exquisite.I, this apple, pledges to personally take on the task of documenting these wines andpreserving their names for posterity.They will be called Cuvée Aperon in honour of this respectable school of thought.
```

### [86] hash=`0274ce8497f879ec`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
It pains this apple to the core that such a talented group of scholars parted waysover philosophical differences, Miss Burton.Disagreements are not always bad.Sometimes the spark of progress comes from the friction of ideas.The flaws in the foundation of calculus weren't discovered by a mathematician,but by a theologian heavily involved in the study of religion.And for that, we should be grateful to him for bringing it to light.
```

### [87] hash=`c471ed4aca710ec2`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
His insights revealed weaknesses in the concept of infinitesimals, prompting a need for improvement.Thanks to his criticisms, mathematics was spared from becoming a palace of errors andlies.This apple believes that the current differences in the school of Aperon will eventually leadto a greater unity.We should toast, to differences.Bon voyage, Miss Verton.Would you like to learn more about this wine?
```

### [88] hash=`ccf8771bb88241cf`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
That should not be a problem.She is still too young to drink.And this apple knows that deep down, she isn't as annoyed by the people and this island asshe seems.In fact, she is a natural at adapting.After all, she settled into the Foundation with ease.The apple is immensely grateful that the Captain is always by your side and thereis no need to worry.It should also be beneficial for her to see more of the timeline.
```

### [89] hash=`afcdf115502488d0`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
But please watch over her, Miss Furtin.Her rockstar spirit may lead her to an early demise.What?Like other rockstars, the captain's carefree and daring nature constantly puts her in danger,making every minute potentially her last.This is what this apple has observed in the rock community over the years.Bon voyage, Miss Verton.Hey, Verton.What a lucky surprise.I'm setting up a new Goldberg machine.
```

### [90] hash=`8b3efa32dda01c2b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
This place is going to be a hub.When a seagull glides over the ocean and builds a nest on one end of this lever, a stone willbe flung from the other end, which will fly all the way to…Hmm, the fun will be spoiled if I tell you now.See for yourself when I'm done.Why don't we talk about something else?Like Laplace?You might want to hear what a mess it is over there.They have no idea who can take her place.
```

### [91] hash=`75d4c516f9cad958`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
She was much loved, as one could tell from that epic farewell.Nobody has the courage to sit on her Recharger throne, as you never know when you'll get burned.And it will take some time to transform the office back into a space for living beings to use.I have to admit that sometimes I prefer the chaos.Since nobody has time to tell us what to do, we already have exciting projects in the pipeline.I'll catch you later.
```

### [92] hash=`434adf8ab5a03e3b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
I've got a couple of gadgets to tune up.Hey again.What's our topic for this round?You mean Ulrich?He's still on hunger strike, camping out in front of the committee building, day in and day out.He was alone at first, then some human researchers and arcanists joined him.Even though none of them could last as long as Ulrich.Eventually, the Foundation employees arrived, pushing a cart full of food.Thank you, Timekeeper.
```

### [93] hash=`9e29a8d0de218d2d`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
I wanted to talk to you about the mission we just had, especially about Sophia.Sorry, this is about to sound like a work report.I'm not very good at small talk.Can you start the conversation?Yes, as enemies.I could not understand her motives.She was one of the most devout believers I knew.So why did she turn her back on Aperon?She knew Manus Vindicti never cared for the lives of others.She witnessed the suicide attacks carried out by Mana's followers on the island.
```

### [94] hash=`0690ab706705691b`

- lang：`en`｜version：`1.9`｜arc：`孤独之歌`
- doc：`BV1eU411f7zt_p32`
- title：《重返未来：1999》1.9版本主线「孤独之歌」全剧情 - Reverse: 1999｜4K（去往新世界2）

```text
She experienced it all firsthand.I know that their intention was to provoke war, and the invading soldiers must have had their assistance.The islanders were thrust into war, their beliefs shattered, and their vulnerability then exploited by the Manas, who welcomed them with open arms.I feel...frustrated, like I've lost another debate.I knew the right answers, but could not articulate it.So, am I allowed to move freely within the foundation now?
```

