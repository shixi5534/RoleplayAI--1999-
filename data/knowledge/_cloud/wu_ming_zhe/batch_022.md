# 剧情图谱抽取 · batch 022

- 角色：`wu_ming_zhe`
- 批次：**22** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.9」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_022.jsonl`

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

### [0] hash=`daf031d46ffbad1d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Sinetto, Lillia, Regulus, assume your positions.It's time to enact the final stage.We are mature enough in the foundations, kids.Miss Sophia?Is the guiding one really not coming with us?She...Are you saying?Fret not, my child.You heard me true.I shall die today.Timekeeper, location Alpha is ready for the ritual.Location Beta, ready.Mr.Apple and I are ready!Good.Requesting to use the Advanced Arcane Skill, Aphoroi Aram,
```

### [1] hash=`75991a072a0759ad`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
number 000262603100008to teleport a top-priority threat to the Parmenida's base.Loosen up and enjoy the ride!Bye!Launch sequence initiated.Starting countdown...30...29...28...The target has not reached the designated location.I repeat, the target has...15...14...13...Large-scale arcane ritual detected.Aphoroi around, verified.Life signal detected.Target is in position.It means a triumphant victory.
```

### [2] hash=`f31f292b05c1d1f3`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
A salute to you, Admiral, and to the timekeeper.Our efforts for peace have prevailed, and we have emerged victorious.Let us forever remember this day for its greatness.Glory to all who fought for this!We did it!Woohoo!Woo!A bullet is among us, right under this roof.It serves no army, no country, only peace.The heavy rain at the end of the century dissolved and washed away many of its comrades, but
```

### [3] hash=`1938da2b78be3839`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
it was lucky enough to survive.Its pointy end still shines silver, ready to drill a hole into its enemy.Sadly, its bulky colleagues stole its thunder in this war.One push of the button, one big explosion.There was no need for the rest of the ammunition.Certainly, who doesn't want a life without theneed to work?Few would hesitate to choose a life of freedom over the achievement andsatisfaction of a job.
```

### [4] hash=`4080f956d7a0336e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Given the short lifespan of a bullet, why would it choose anything else?But its boss, the General, has more to think about.What are they going to do next time?Will this bullet be put to use when the rain comes again?A big shot, dear.A wise man of the most insightful kind.You should talk to him if you have the chance.But he's been in a gloomy mood lately.Be careful not to mention anything related to the conservative battle tactics used in 1999.
```

### [5] hash=`97c1a0b712290291`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
The missile that would have been launched, and especially anything about the bullets lost in that battle.If they hear you say that they won't be needed anymore, you'll end up with quite the ammunitionbill.Alright, let's leave this bullet to itself.Solitude may help alleviate its anxiety about the future.Drink this.It will help relieve your pain.Worry not.It's not made from the grapes on my head.Hang in there, 29.
```

### [6] hash=`f893531b3ffa0fb2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Are there any other injured that have not been found yet?I've scouted the island.Every remaining member should be here.So you have.It means the members not here have joined Manus Vindictae.You stick still in a coma, Miss Marta.To you, O the alone infinite, the non-subsistent, the ineffable, I call.Grant me inspiration of nature, guide my soul with truth.Give me power of enlightenment.Tear off from the web of ignorance.
```

### [7] hash=`a9d795ac429006f1`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Redeem me from the evil, hatred and what throttles me down.Break through the ground of bad, corruption's chain, the carapace of darkness, the living death, sensations corpse, the tomb I carry.Learn the beauty of truth, the balance and limitations of all.are you still praying the truth is gone are we praying to answer us for generations we havesearched for purpose and meaning but now that the truth is lost what is left for us to live for
```

### [8] hash=`1b2652d7b4a8e530`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
no the truth is still there i passed a pair on test and it showed me the answerit will free us from the wheel of birth once and for all i just need some time to decode itWe will do our best to help, but how much time do you need?I have someone in mind that can help us decode faster, but I need your approval before Iask them for help.May I share the truth with the others, 37?The side effects are completely random.
```

### [9] hash=`0131c30658a38449`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Among the current samples, the probability of no side effects occurring is 0.52%.And of the 81 recorded side effects, 39 of them will cause irreversible damagethe biological body, 24 will permanently alter the composition of the castor's body functioning,and 18 minor effects will cause only minor, superficial injuries that do not affect dailyfunctioning.Laplace's archives has enough rituals to protect castors from the minor effects,
```

### [10] hash=`8a0caa1e56ff7f56`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
but the other two categories are highly lethal.After 72 experiments, the diversity of sideeffects has decreased significantly.It is unclear if this is due to repeated testingon a single subject or due to a limited range of possible side effects.More than 90% of these effects are related to concepts such as dirt and dust.Is it because of the origins of this ritual's power?Hmm?The number of recorded side effects is 86, not 81.
```

### [11] hash=`1a0f225254f1d37c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
When did I write these five down?Madam Lucy, Xeno's plan was a success.With the help of Team Timekeeper, the leader of Menace Vindictae was teleporteda deserted military base and targeted with a thermo-barric weapon.It was a direct hit withno signs of life detected.The momentous event was captured on camera in the observation room.A tremendous victory.Please extend my congratulations to the Admiral for this
```

### [12] hash=`47871f21f76498ff`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
remarkable feat.Also, you have two call requests.One is from the timekeeper,which Laplace received shortly after the battle with Manus Vendictae.She is requesting remote assistance to help the Aperon decode a numerical code related to the storm immunity.Put her through immediately.And the other call?It's Cacania, the Viennese Arcanist who helped investigate Marcus in acquiring the ritual.We have updated her the progress of the study and the potential side effects of the incantation.
```

### [13] hash=`4fa41a71e0d0239c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
But she insists on knowing the right pronunciation.We are not aware of that.Thirty-seven and I had just entered the cave when the investigator sent back the ritual.I see.Thank you for the thorough explanation, Madam Lucy.I'll make sure to inform the members of Appurin.If possible, could you kindly explain this to them again after we set up the communication device?Next thing's the acoustic components.
```

### [14] hash=`9334754a65462206`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Totally understandable if you don't have any on hand.Regulus, can you help me find some...What are you saying, mate?Of course, this great disc jockey would have the acoustic components!I'll have you know, I made friends with the dolphins as soon as I had the chance,hoping they'd retrieve some of the radio components from Apple II.Actually, found some!Have a communicator equipped with a speaker.Before, there were too many years for one tiny radio.
```

### [15] hash=`10ec2e285a984ba4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
What?What now?Another attack?Not quite.That's the sound of our colleague, Medicine Pocket.Hard at work.How goes it on your end, Burton?The storm is only eight hours away.Has the immunity zone on the island stopped shrinking?I think so.No one in the Hall of Appearance affected by the storm syndrome so far.The immunity zone seems stable for now.Man has been dictating that humans have left.There should be no further destruction on the island.
```

### [16] hash=`0cced613b2a26098`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Hmm, so the decay of the immunity zone is not linear.It seems to be influenced by the Islander's mindset toward the truth, and it eventuallyreaches a stopping point.Could it be that the ritual on this island, rooted in the power of faith and belief,serves to amplify only the radius of the storm immunity?Fascinating.That can wait, Research Rex.There's one thing I'd like to confirm, Timekeeper.About the question Ms.
```

### [17] hash=`c7ee6a0738713c98`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
37 asked in the cave, how can we escape the darkness ofphenomenal world and be freed from the emanation forever.To my understandingthat is almost the same as asking how we can be immune to the storm.Yes, and 37 also said the transcendental truth was beyond the limits of hermortal flesh.A parent answered her with an eerie sound, one that could driveanyone mad just by hearing it.It was then that the scroll 6 gave her
```

### [18] hash=`6b5c0ac17b646fee`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
unfurled and transcribed the sound into a string of numbers, providingus with the code.Yes, that's the key to our problem.We both received a solution to the same question simultaneously, immunity against the storm.This could be our Rosetta Stone, Timekeeper.We found our own Rosetta Stone!Rosetta Stone?Allow me to explain.The Rosetta Stone is a stone tablet inscribed with a decree in three different languages,
```

### [19] hash=`209722c054ce198d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
hieroglyphs, Demotic, and Ancient Greek.Hieroglyphs were the sacred writing for the divine, while Demotic script was known as thelanguage of the people.Both scripts were ancient Egyptian, lost to time when the tablet was discovered.However, because scholars were still able to read ancient Greek, and through comparingthe three inscriptions that all said the same thing, they were finally able to understand
```

### [20] hash=`b1a7959ede925e4f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
the hieroglyphs.And now, we too have our own set of inscriptions to decode.The first is similar to hieroglyphs, as the truth Ms.37 heard in the cave is completelyunintelligible and can drive people insane just by listening to it.The second is like Demotic Script, a ritual we obtain from Arcana that can place a curseupon those who read it aloud.It cannot be handled by ordinary people.Finally, the numerical code you shared with us is like the readable Ancient Greek,
```

### [21] hash=`c182387b32c52e68`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
without any divine powers but crucial in deciphering the other two inscriptions.unlock even deeper knowledge that only belongs to the Divine?Exactly.We're looking for the same answer to the same question,like how the same decree is inscribed onto the tablet in different forms.And just like the inscriptions on the tablet, we have three versions of the ritual.If we can delve into the essence of the ritual and master its inner workings,
```

### [22] hash=`59e1f7745038b097`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
we may eventually transcribe it into a side-effect-free ritual that can be used by everyone.Yes, it should work, because the nature of the universe flows in all things alike.I'm glad you think so, Ms.37.Your hypothesis is based on too many assumptions, Ulrich.It requires further refinement and confirmation.We now have valid incantations.We should continue in this direction.You mentioned the word transcribe just like the Timekeeper did.
```

### [23] hash=`2f56962820d2e0cb`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
It holds the answer to improving the ritual.You mean?The scroll you mentioned that can bridge the gap between you and the Supreme Existenceduring Communion.It is the scroll that transcribed the eerie sound and saved 37 from the lethal side-effects.Does this mean it could potentially lessen the negative effects of the Immunity Incantation?Wait, Madam Lucy, let me take it from here.We would like to borrow this scroll for research.
```

### [24] hash=`1849f6a4764100e9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
If you lend us the scroll, we will make significant advancements on the research,and we promise to provide every assistance you require in the future.Lend you the scroll?Are you asking us to give the legacy of Epiron,our most cherished possession to you?A scientific research organization that serves humans?We are seekers of truth, are we not?Heed my words, 37.That scroll is a sacred relic passed down from the wise sages of Epiron,
```

### [25] hash=`ed66407e756f20ac`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
safeguarded by the Sixes, and entrusted only to believers who brave Epiron's test.It has the power of harmonization and reconciliation.You may keep it until youfully grasped the secrets shared with you by Epiron, but you will not share it with someBefore the emanation cut us off, we had these types of communications with the outside world.It was fun, unlike what came after.I'm sure by sharing this scroll, the code from Aperon will be deciphered.
```

### [26] hash=`601d1f55cc0f0cf8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
I must prove that the light of truth still glimmers!But how can you be sure the scroll will only be used for researching the ritual?How can you ensure that the humans won't exploit it to create weapons of destruction?Before joining the School of Epiron, my people and I had wandered the world for ages.Our long lives made it difficult for us to truly fit in with the world.Daughter of Truth, I implore you to hear the words of this old soul.
```

### [27] hash=`4bfafe87c8afb2a1`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Humans have indeed achieved incredible feats,And their enlightenment has even touched my soul.But unfortunately, most humans do not have an inherent respect for knowledge or its boundaries.They only chase after power blindly.I have experienced it firsthand.I tried to guide and persuade them, but ultimately I failed.That is why I am here now.What you are deciding to share is not only knowledge, but it is a ritual, a piece of
```

### [28] hash=`4ff9d10bc7de2d97`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
power.A ritual designed for harmonization, created for the devout believers, and created forthe sages seeking the truth.Yet, on the other hand, it can also be used for unspeakable horrors, such as silencerson guns, suppressors on rifles, or even on nuclear bombs.It won't.888, I won't let this happen.I promise.You can't promise anything, Ms.Furtin.You're too young,too inexperienced to comprehend the dark nature of history.
```

### [29] hash=`96a05f52126d0219`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
But it's the truth we're talking about.What could possibly outweigh the truth?If all it takes is lending someone a scroll to unlock unspeakable secrets, why not doit?Haven't the failures of the past four years proven that a stagnant mindset does not bringforth the light of truth?As individuals devoted to critical thinking, should the pursuit of truth not be our primarygoal in life?My brothers and sisters, do not let hatred stop you, and don't let the dust of
```

### [30] hash=`c647e94417885a76`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
phenomenal world blind you 210 and remember it was 37 who passed the testand earned the scroll it is her rightful responsibility to handle this situationotherwise what other choice do we have I have made of my mind I will sharethis role with the plus we will decipher the code together the truth istruth it should not be swayed by anything else everyone cost your pebble if you agree with meif six were here he too would have called for a vote miss lilia are you certain about this
```

### [31] hash=`96322a9a4e24fa31`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
absolutely see the nice weather today much better than the day we landed no wind no cloudthe clear sky and that giant moon come find a better day to deliver the packageIt's just to the headquarters, not even going outside of Europe.Three hours is more than enough.I'm done being stuck on this suffocating island.Nobody can stop me from taking this flight.The headquarters are at least 768 nautical miles away,
```

### [32] hash=`5e3a6d1c550122d8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
and you have no protection during the long flight.It's dangerous.And we have only seven hours until the storm.Dangerous?Maybe.But this is an exhilarating flight in the storm, Sanatole.What better chance than now to push Zeno into updating their flying manual?Besides, what's wrong with a bit of oil painting on me?Should be a nice badge of honor.Mate, that's quite a distance.Just be sure not to go toppling into the Mediterranean Sea.
```

### [33] hash=`4636117d2e1779e7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Red 38 is no way an apple the second.Uh-oh!Manus Aletius?We didn't kill them all off?I don't have time for you, little stingray rats.Still got your speed, huh?I guess the death of your boss didn't faze you much.Oh, a Manus aircraft?Worse a fight!Ha-ha!Bring it on!Your downfall will be an explosive orchestra over the waters!Look at my back!Yes, Ms.Teiter has derived the formula and my team has finished designing the prototype converter.
```

### [34] hash=`8116ad048a2d7385`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Now we just need the big wigs upstairs to approve the experiment application.This is an unprecedented chance to rob this storm of its energy.I wouldn't miss this for anything.The scroll of Eperron has shown great potential in protecting casters from the ritual.It is expected to outperform the Coleman protection rituals.The sheer variety of side effects is concerning, but we already have a list of 122 curses and their effects.
```

### [35] hash=`015a92cd7f23da61`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Once the scroll arrives, we will test and record its reactions to each of the effects.This should speed up our analysis considerably.How can we get humans to make use of this ritual?Ideally, the incantation is made into a tool like the Manus Mask or Laplace's Incantation Softus.What is the plan of the imaginary numbers?You want to use the waves of Numa and the reconciliation of the scroll to allow everyone
```

### [36] hash=`3e3be2c089396015`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
to recite the storm immunity ritual?Yes.What do you think, 37?An ugly plan, it is.There is no grace or beauty in this approach.It is purely driven by practicality and uses clever tactics to make things fit.apologies we took some time to test the delivery methods for your safety onlythe text of the incantation will be delivered the exact pronunciation willbe sent to the timekeeper later thanks mate since the island has no visual
```

### [37] hash=`babdb0fb98020a19`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
communication we will send the incantation letter by letter through aclad knee plate a technique that converts simple patterns to soundwaves enough with a mumbo-jumbo there's no time for details anywaytimekeeper we'll need the help of that lady miss radio right huh yes somePlease find her a metal square plate fix it on a sturdy base and pour sand on it a special recording will be sent to youplease stay by the edge of the plate embrace the sound and
```

### [38] hash=`5dcdfbc0f2c1ff8f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Groove along I assume you mean vibrateNo, no, no, no, no, that's just rudeYes, exactly.If all goes well the vibrations will move the sand and visualize the text in a patternWe have 12 recordings ready each representing a letter in the incantationThat's it!The investigator in Vienna reported a similar thing.An ancientmiracle, a circle of salvation.Akana even drew a circle in the air whilesaying it.
```

### [39] hash=`0ee9d8b65aac95e3`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
She did it so nonchalantly, as if it were a meaningless gesture.Wedidn't think much of it at the time.Once we confirmed that it did notaffect the casting of the incantation, we forgot about it and moved on.Can't believe I overlooked it!This is not your fault Ulrich.The gesturewas overlooked because it did not really help the research.Our focus was on practical applicationrather than understanding the incantation itself.
```

### [40] hash=`10a3eb753edad8fd`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
If the incantation means the first circle,how will this be helpful to the research?Vertin, I don't know why you can read it, but I do know that Gal is thrilled by your interpretation.Because you mentioned her favorite shape, the circle.So if the incantation is a circle, what kind of circle is it?In topology, any closed curve on a plane can be classified as a circle.Told you!Fertin, let's go back to the Rosetta Stone hypothesis.
```

### [41] hash=`b7a04dc4284b2c7b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Based on the hypothesis, if the incantation in the numerical code share a common essence,which is the key to the storm immunity,and we now know the incantation refers to a circle,Then the essence of this numerical code should also be a circle, right?Before this conversation, I had no idea which direction to take.The numerical code could be a snippet of an incantation, or it could be a geometrical ritual array.
```

### [42] hash=`a70d5165d6766b10`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
I had a lot of theories to go on, but testing them could take weeks or even months.Worse yet, if my line of thinking was completely wrong, we could waste decades of time and effort.But the Rosetta Stone hypothesis is easy to verify.Let us suppose that the Incantation and Numerical Code share a similar essence.We know that the Incantation does work as proven by the Awakened.If the Incantation is a circle, then the Numerical Code should also be circular in nature,
```

### [43] hash=`fbee7aba032b651d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Because you're really into circles.Specifically, I simply like it because it's a great shape.I don't understand.Positive 1, negative 1, positive 2, negative 3, 3, negative 3, positive 2, negative 1, positive 1.How do these numbers relate to the circle?The first circle?Yes, it was the timekeeper who translated the incantation.And according to the investigator in Vienna, Arcana also drew a circle when she cast the
```

### [44] hash=`9818ce2adb21a5fc`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
ritual.But experiments have shown that the gesture has no effect on the ritual.We thought maybe it was a symbolic gesture.No, no, no.It is no way just symbolic.Arcanists excel at condensing their experiences into symbolic representations.that could be mass-produced for everyone.Will that form have to be a circle too?Things often hold the deepest meaning, as always.So, the first circle, what could it be?
```

### [45] hash=`893d3e1a191a4069`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
A wheel, a piece of rope, a pendulum.I spent too long on the wheeland not realizing there was something more promising.A circle can also be seen as a knot with no crossings.An unknot.This could be a variation of a closed curve!A knot!Knots were how the ancients of the Incas and Chinese collected data and kept records!But which knot is it exactly?The Jones polynomial of the trefoil knot is t plus t cubed minus t to the power of 4.
```

### [46] hash=`178c3d1bd3891f01`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Right, the second three I heard sounded different from the other threes.That three must be the constant term of the polynomial.Then if we use this three as the origin, like a number axis,the left side is the coefficient for the negative exponents,and the right side is the coefficients for the positive exponents.This string of coefficients is the shorthand of a Jones polynomial.If we assign the eight coefficients to the eight corresponding exponents
```

### [47] hash=`704413b6afdee7b9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
in a Jones polynomial, we get its true form.T to the power of negative fourminus T to the power of negative threeplus two T to the power of negative twominus three times T to the power of negative oneplus three minus three Tplus two T squared minus T cubedplus T to the power of four.Fever 10, a Pyrron did give us the answer.The key we've been looking for,the most profound secret,the language of the divine!
```

### [48] hash=`9021b1602b38fbf5`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
No sound or text is needed, just pure structure,the very form of the essence itself!It is a beautiful shape, a simple knot!A knot?Great.Now there is only one step left.The verification.Did you hear that, Madam Lucy?Can you help us verify the authenticity of this knot?Of course.I have paid close attention to the discussion.This polynomial produces a single unique knot.We can now tie a knot to test it.
```

### [49] hash=`76564bc6aa403613`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Madam Lucy, is the signal dropping?Madam Lucy, can you hear us?I...worked.I never thought it would be the timekeeper and the Aperon Arcanus who'd solve the problem.But now even humans can cast this ritual.Indeed.The knot is the physical form of the ritual we were looking for.Surprisingly, the numerical code yielded practical results.I thought it was necessary to report this to the Time Keepers' Organization.
```

### [50] hash=`0ca730cb7fd678fc`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
It was her contribution, but it did not go well.Forgive the interruption, what's a knot?I will be glad to answer your question.Knot theory is a branch of algebraic topology.In mathematics, a knot refers to a connected closed curve in three-dimensional Euclideanspace that does not intersect itself.They can also be described as shapes in three-dimensionalspace that are homeomorphic to circles.Knot theory focuses on the entanglement and configurations
```

### [51] hash=`5e9d0ab4aa518561`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
of closed curves in three-dimensional space, rather than the curves themselves.Sinceall closed curves are homeomorphic to circles, they can all be topologically categorizedas circles.A knot equivalent to a two-dimensional circle is called an unknot, and...I don't mean to question Laplace's expertise, but this approach may not be the best solutionfor widespread implementation.The concepts are complex even for us, let alone others.
```

### [52] hash=`0a2ec25a0c435c03`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
We can't expect to give an advanced math lesson to every individual under these circumstances.Ah, doing math before the storm!Nobody's got time for that!As it turned out, presenting a technical report was much too premature.We should have a complete and official report once the immunity gear is produced.Maybe you can change your approach the next time your report is a foundation.I simply gave them honest answers.
```

### [53] hash=`877d3b764de6e550`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
But this solution is deserving of widespread implementation.All we need is a piece of rope and tie it end to end.And spend 3-5 minutes to make this knot.This can be done anywhere, at any time, by anyone using any type of cordage.The oldest, fastest, and most basic ritual, the key to braving the storm, is a knot.Why didn't you tell the House of Integratus?I'm sure they would have funded us generously.
```

### [54] hash=`6f91668eb67f9941`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
I will make sure to put it in my interdepartmental report.But at this point in time, the knot only functions like an incantation.It is not suitable for widespread use until the research on the side effects and the converterare complete.In any case, I've completed all the tasks you assigned me.My last plea is, please never put Ulrich and I on the same team again.I'm surprised that you're not in the lab.
```

### [55] hash=`ae39f10694b60096`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Something bothering you?Wait, don't tell me you're charging here.Excellent job, researcher Adler.Here you have proven that you are keeping the locations of public outlets in Laplacein mind, which is a positive sign for your re-socialization.I am powering up to reach my optimal condition, preparing for what is to come.The scroll of a perron.The final piece of the puzzle.The key to minimizing any negative effects caused by the incantation.
```

### [56] hash=`701597499c7f3860`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Wow, the designers on artificial semnambulism could use some of this inspiration.Look at the clouds, painted with a syndrome of colors uninterrupted by a glorious streakof rainbow.It's truly a masterpiece.Funny, they're flying towards the headquarters out of instinct.Maybe they can sense immunity zones.These little beasts would make for a good study.but I'm not in the mood to take any prisoners fuel and ammunition are
```

### [57] hash=`77851ffe7418e6d8`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
running out huh maybe I should storm the vice president's office with them butother people might get hurt there never mind hmm dive into the lake but thesplash might wet the scroll wait isn't that miss Lillia this way huh goodBeing washed away with it would be a just punishment for all my sins.I wish I could be as brave as you are.See you, Miss Clara.Hurry, ladies, before any of us turns into one of those exquisite paintings!
```

### [58] hash=`0a4ef763ef1986f6`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Sorry, but the headquarters is too far for the teleportation disc from here.You'll have to bear with us smelly old grunts for a little longer.Goodbye, Miss Marcus.Sharing this error with you has been an honor.Is your birthday approaching, Doctor?I made this for you, turquoise and topaz, just like you in your eyes.Please accept my blessings, Doctor.May your life be filled with joy and contentment, and may your courage guide you through all
```

### [59] hash=`33c35f429f93ab2c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
that comes your way.You are worthy of all the beauty and goodness this world has to offer, and I will holdyou in my heart and in my prayers, forever.Sweet dreams, Sister D'Astalfe.Madam Lucy, any progress on the research?Rex is awake?It's perfect, like the number 10!He will be happy to hear that I've cracked the code!Vertin, the light of truth still shines!With some time, communication, and a flash of inspiration,
```

### [60] hash=`c979293fc54c5c2c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
we can bring it down from the unattainable skies and let its radiance illuminate all!Also proven that the truth is not out of reach or too distant to graspOnce if knows about this she'll come back to us, right?I'm sure she'll be happy with what you've accomplished 37Did 210 in 888 go to get six?You don't seem that happyThe star of Hermes deciphered the code of a pair on she found a way to cross the emanation
```

### [61] hash=`e80b9dd0b0e4547e`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
We should all feel happy forYet here you are, so indifferent.It is because you, too, know that what hashappened will not change, regardless of whether she figures it out or not.A meager ritual to save people from the emanation is nothing compared to thedisruption of the law above.It also cannot change the fact that our faithis dead.We're talking about how the island has sunk, and we're now sailing
```

### [62] hash=`c58bed72b6ea17ea`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
in a tsunami.A tiny miracle, a spark of inspiration won't save the ship from thewrath of the tides.To be honest, Mai was surprised that she asked such a practicalquestion.I guess the trivialities of the phenomenal world did eventually affect her.It's a shame that many others lack her determined will to see beyond the void of our brokenreality.What's your point?Can't you see?I'm getting a rise out of you.
```

### [63] hash=`fcd326032441df61`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Who wouldthought that our great, perfect, honorable leader of the School of Apeiron has been anAnnihilist all along.You never revered the truth, did you?That's why you kept us inthe dark for four years.You never respected our beliefs for a second in your life.The people who seek the truth are more important than the truth itself.I may not understandthat ever-shifting number, but I do understand and respect the people here.
```

### [64] hash=`22392b2dc8896dbd`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
So you knowsecret.What now?Now that you know the truth could lead to an nihilistic void, Iwonder if you would abandon our doctrines, our wisdom, and our inheritance,and step into the darkness in a fit of rage.When truth fails, sophistryprevails, correct?We cannot deny that fate, the unspeakable, holds wisdom888 must have made a mistake!I need to warn them!37.Either be wise, uninvolved, and look on, or be practical, involved, and suffer.
```

### [65] hash=`1e65ccc088c5fb41`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Which one will you end up choosing?Yes.In recognition of your extraordinary contributions, Laplace is honored to present you with the fruits of our labor.This knot is the result of our research.The knot has been validated as a working ritual on both humans and Arcanists.With the help of other Arcanists, we found methods to avoid side effects, and conductedsmall-scale experiments with success.Are you saying we can...
```

### [66] hash=`b948f4eb9fa36b9d`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
However, since the experiment is still in its early stages, it involves a varietyof materials and complicated rituals that are not yet possible for transmission.nor can we deliver you any experimental equipment as the storm is about to makelandfall.The knot acts as an equivalent to the incantation, but it does notguarantee that we will meet the casting requirements or avoid the likely sideeffects.
```

### [67] hash=`c8e87216b218f733`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
I apologize Miss Kakanya, perhaps the result of our work willnot really help your situation.You said the knot works on both humans andI have two more pieces of good news.First, the curse is not inevitable.Our experiments showed a 0.49% likelihood of no side effects occurring at all.Second, the closer the storm gets, the more Pneuma fills the air, leading to a greatersuccess rate of the ritual.Yet, even with these factors combined, the rate of success is still extremely low.
```

### [68] hash=`2bd9b81e7538d5bd`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
With millions of people trying, there's hope that at least one person will succeedagainst the odds.Thank you for sharing this with me, madam.I will do everything I can to spread this not in Vienna.To the Arkanists, humans, Magyars, and Germans, they are all my people, regardlessof the social status, profession, or race.They all deserve the right to survive.Madame Lucie, I can only assume you acted impulsively and overlooked the proper application
```

### [69] hash=`54324cf3dc0fd9b1`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
process.The Knot is new and not ready for widespread testing.Distributing it in Viennacould lead to more casualties or even fall into the hands of our enemies.I must remind youthat this is a clear violation of the regulations set by Pax Security Council,the Saint Pavlov Foundation, and the Laplace Scientific Research Center.Ah, yes.How careless of me.I did tell her I would share the results of the research.
```

### [70] hash=`21a57fcdc0391818`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
And this is what you call a promise.And the database says,a promise made is a promise kept.My brothers and sisters, put down your cups for a moment and lend ear to me.We were born extraordinary, yet estranged from the world around us.Throughout the ages, we wandered the world like a ship lost at sea.Despite the instability and chaos, we persevered, and together we sought after the truth thatwould illuminate us all.
```

### [71] hash=`0def1ef6188e1f4f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Through introspection and contemplation, we cleansed ourselves of hatred, madness anddelusion, and embraced the value of beauty and harmony.Yet now, our shattered faith mingles with the rubble of this phenomenal world, as specksin an unjust timeline, as remnants of a tide long receded.The dream of the transcendental world is broken, and the order of the transcendental law is no more.Our sanctuary has crumbled, exposing us to live in a world filled with conflict and turmoil,
```

### [72] hash=`2d259f44e99d58dc`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
where we will be trapped in the wheel of birth, doomed to repeat the mistakes of history for eternity.But do not despair, for there is another way to the truth.It is a path fueled by unbridled passion, one that was stifled by moderation and restraint,a path that transcends the individual, breaks all boundaries and limitations, and leadsus back to the essence in a fiery blaze of glory.This path is the emanation, which we stride into for the ultimate truth of our journey.
```

### [73] hash=`41d0c70c4f188fe2`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
Doctor?Ilich, gather everyone you can and have them read out these steps in the plaza for allto hear.If possible, go to the telegraph office or use a printing machine to copy flyers.Distribute as many copies as you can.I'll go to Leopoldstadt and find the Garkus brothers.They know where to find abandoned military hot air balloons.what are you talking about doctor people are too busy trying to escape I want
```

### [74] hash=`60b6442c2573d214`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
nothing to do those crazies this a guide for tying knots don't you know the worldis about to end so many warnings who'd want to read this the people who wantto survive will read it I can't guarantee anything it's agamble for our lives but people have a right to try before doomsdayarrives please trust me one more time please find a car if this works yourcoffee for the rest of your life is on meplease in the test i put the code of appearance i aren't you
```

### [75] hash=`867b79dd779e2e9f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
stop are you joining them as matter i find myself uncertain of which way to gowould you kindly give me some guidance the guidance i can offer you islimited miss marta i think fate knows its ownfate better than anyone.Just touching the meter's long rope provides blessings to the faithful inBellum.And tiny knots on strings can carry the history of an entire people.The ancient Inca called it Khipu.The intricate variations of hundreds of
```

### [76] hash=`0b5a9432a5be28cb`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p62`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 21~27）

```text
fabrics, colors, and lengths of strings were used to record their storiesPass the end through it tighten it up.There you go.Hope you keep this knot as a record of the words we shared here
```

### [77] hash=`132842fb0b588481`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I...I don't understand.I should be giving them my blessings.They're brave enough to return to the essence, but instead...Sadness washes over me.I should feel happy for Sophia, now that she knows her soul number.Yet, I am filled with sorrow.Why did you all leave?Is it because I wasn't fast enough?Is it because I didn't do well enough?Thirty-seven.Leave the island to the world outside.Ms.Vertin, you're clearing a path out of the Myers of the Phenomenal World.
```

### [78] hash=`c158d2d9a79dd02a`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I sincerely hope you will steer it away from the horrors of war.It's our duty to do so.Also, the person you were looking for, I am not familiar with a biographer named Erd.However, in my recollections from the previous six, there was a lady with a soul numberjust as unique as yours.Are you saying...Sadly, these vague scraps of information were all that I inherited.I hope they will be useful to you.
```

### [79] hash=`b62429a62209ead9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I'm returning to the cave, 37.There are still people who refuse to be caught in the cycle of hatred or give in to unrestrainedpassion.The entrance to the sacred place may be destroyed, but the people's faith is yet to be extinguished.We will persist in studying the scrolls, copying the scriptures, and restoring our halls.We will worship the ancient one in penance and work to rekindle the flame of our broken
```

### [80] hash=`76bd5ee552225a95`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
beliefs.The island is a manifestation of our choices, a haven removed from the phenomenal world,a place of order and harmony, and it is our determination that will sustain its tranquil existence.No, your choice has already been made, 37.You should not go back.The sorrows and doubts you have can only be alleviated by experiencing the outside world.Thousands of years ago, the first faithful ones fled from the Roman Empire and
```

### [81] hash=`1eef4b7be4f9b33b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
journeyed to this island, where they founded the school of Aperon.500 years ago, refugees from Arabia found shelter here.They filled the caverns'shelves with copies of their writings and texts.Half a century ago, scholarswho had their research exploited for warfare came and expanded our knowledgeon modern mathematics.There were many 37s and 6s among them.Yet, are we any different from themin essence?
```

### [82] hash=`894a58a1db3d0715`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Even if we are no longer here, the numbers 37 and 6 will still exist.Even if theislands sank, these numbers would reappear elsewhere.The integer sequence is infinite,37.Rather than clinging to a set of specific numbers you should go and workout your own calculations and conclusions.So now you're choosing to be wiseand look on, but I don't understand.How could one be wise by beinguninvolved and looking on from the sidelines?
```

### [83] hash=`3cdc499d5fcf29b9`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
You overestimate wisdom Ms.Burton.It can't do everything.Wisdom can free people from ignorance but itcan also lead them to a nihilistic void.Yet, someone will always seek this wisdom,even if nihilistic,to briefly rise above their worldly troublesand find some relief.And someone will have to stay hereand provide a neutral havenfor the drifters of the phenomenal worldand give the lost souls a harbor to return to.
```

### [84] hash=`00a2a1f28be12f2f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Solutions than ever before,well, to discover all it has to offer.Maybe a little, I will get used to it, because the nature of the universe flows in all thingsalike.We are prisoners within these cavern walls.Our gaze is held captive by the shadows thrall.Until our hands clasp and our chains rattled, we united to break free from our shackles.The sightless joined forces with the soundless, and the voiceless uplifted the helpless.
```

### [85] hash=`4509d4d728a50c6c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Together, we assembled a sliver of truth, a piece of the world hidden since youth.Have you got something for me, Mesma?I asked me to give this to you.The culmination of our research, the crystallization of man and all its wisdom, the protectivegear against the storm, an umbrella, something you personally don't really need.It's called the equilibrium umbrella.This is the first model, consisting of a converter, a harmonizer, and a ritual core.
```

### [86] hash=`885c7941090461f7`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
The converter generates a balancing field that can cast rituals in the storm,taking account of the wielder's capabilities.The harmonizer's markings are inspired by the scroll of a Peron.Madam Lucy tested it against 162 known side effects and found it to be highly effective.The original scroll has been returned to the island.This is only a simplified and duplicated rendition.The 162 curses aren't all of them, right?
```

### [87] hash=`f7aa084a92fe7bec`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Correct.There may be other unknown side effects,so the umbrella is only a prototype in the testing phase.And...the ritual core.At first it was called the 37 Lucy nod in honor of the two main contributors.However, both of them turned it down.Yes.I still remember what 37 said at the time.She would rather name it after the mathematical properties of the knot, even if it's too much of a mouthful.37 is not a name, and the truth should not be dressed up with anyone's name.
```

### [88] hash=`66d2763175f3023f`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I only found it.I didn't invent it.I don't need something named after me to prove my sense of existence.But I'm not on the island anymore.I can understand that the imaginary numbers need to honor the discovery.You may use another contributor's name for it, I'm willing to accept that."Madam Lucy showed no interest in the naming rights, so it was transferred to the thirdmajor contributor, Adler Hoffman.
```

### [89] hash=`d7cf0e2ce3e19bf4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Sadly, researcher Adler also rejected the offer.At first, we nearly ended up using the date of that day as the name, but he changedhis mind after confirming he could use his family name instead.The Hoffman Knot?You named it after Madame Hoffman?Yes.Researcher Adler Hoffman wanted to make sure that Greta Hoffman would never be forgotten for her selfless sacrifice.Level 4 Investigator Marcus, please accept this umbrella.
```

### [90] hash=`90eb8345fbe925f4`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
It is rightfully yours.Given the incredible contributions you have made, you are welcome to apply for a well-deserved and extended vacation.No, I will request for permission to go out.My era has gone, but with this umbrella in hand, I will venture into the new world andmarvel at what's to come.Will the sucker-tort taste the same?And lastly, the asymmetrical nuclide R in the handle of the umbrella is supposed
```

### [91] hash=`5b8bf9a3a30ba415`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
to protect against the storm syndrome, but this still needs to be confirmed throughtesting.It's okay.This is the one thing we need the most.If you have no further questions about its usage, I'm heading back to the rehab center.The afflicted researchers there are in dire need of my magnet therapy.Don't you think one is not enough for my needs?I think five.No, fifteen might be more helpful.My suitcase can't protect humans from the storm.
```

### [92] hash=`9564d20eea83c9e5`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
They'll need the umbrella to survive.Just be patient and wait.Lillia, how's your commendation ceremony?Heh.They rewarded me for escorting the important item during the storm.How is delivering a scroll worthy of a reward?I'll say someone should be grateful I didn't crash into the committee building.Take it.Might be useful for your alchemy.Let me see!It's made of pure gold!On behalf of the pirate community, I thank you for your remarkable contribution to alchemy!
```

### [93] hash=`3b896a6bb031839c`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
I have one too.Please forgive my lack of contribution, Timekeeper.It seems the Awakened Woods have embraced tranquility once more.Perhaps a sign of good things to come.I'm glad to see you back on your feet, Ms.Truvis.In fact, there's a place I'd like to introduce you to.A flourishing island that survived both war and the storm.The Foundation will rebuild Apple II and pay for its maintenance.Funny you say that, Sinetto.
```

### [94] hash=`e74da13ae8d4ba2b`

- lang：`en`｜version：`1.9`｜arc：`—`
- doc：`BV1eo4y1u7aW_p63`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.9-主线】第七章.孤独之歌 | 28~30）

```text
Now we have two new ships.Fifteen plugs.This should be enough to cover all socket types at our destination.Simone, pass me the experiment log, please.Madame Lucy, is it true?Are you leaving Laplace?Yes.The inquiry is over.This is the decision of all parties involved.You have got to be kidding me!After all the incredible contributions you've made, they're suspending you?This is absolutely ridiculous!
```

