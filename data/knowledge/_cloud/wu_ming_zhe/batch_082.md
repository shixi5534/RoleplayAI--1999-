# 剧情图谱抽取 · batch 082

- 角色：`wu_ming_zhe`
- 批次：**82** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.7」｜offset 0
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_082.jsonl`

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

### [0] hash=`9559050374431058`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p10`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（10.内窥镜.1/7 16:15）

```text
You know what happened, but under the Foundation's regulations, I must reiterate that the primarysubject of this investigation has been changed to Heinrich.These two invitations are very useful.I'll tell the field agent squad to act tomorrow night.Once Heinrich's identity is verified,we will detain him in the exhibit.But I must remind you, Marcus, what you did today wasa serious violation of the field mission manual, and I have to report this to the headquarters.
```

### [1] hash=`bd64b9db30e5ff33`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p10`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（10.内窥镜.1/7 16:15）

```text
In principle, everyone on this list is useful.On the other hand, the branch has its own connections, too.More importantly, takes more than a conversation over teato get the people on the same side of a conflict.I am worried you are not ready for this, Marcus.There is too much wickedness out there dressed in the skin of kindness.The most horrible atrocities are always committed for the most seemingly justified reasons.
```

### [2] hash=`f7ef4583da661c0b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p10`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（10.内窥镜.1/7 16:15）

```text
Even at the headquarters,The rules are there for a reason.Nothing in the manual was written out of imagination.Every one of them came from a mistake of the past.We are only here to observe.This is Vienna in 1914, the birthplace of an enduring war and chaos, the criticalpoint.It is a powder keg and the slightest spark will set it off.Any action we take could have unfathomable consequences.That is why we advise extreme caution.
```

### [3] hash=`6402bb3d17ed655f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p10`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（10.内窥镜.1/7 16:15）

```text
This is our responsibility to this era.I understand completely, Madame Hoffman.I won't make the same mistake again.Isolde, you look sad and pale.What happened?Did something happen in the troop?Or did those dreadful officials come back?No, I'm just a bit worried.You...you entered a duel for my sake.Hello last time in the secession building now, I understand have to get her to stop relying so much on her arcane power
```

### [4] hash=`43ff4b42e2740ecc`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p10`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（10.内窥镜.1/7 16:15）

```text
Luckily not completing my education is why I know a little bit of everything.What are you doing?Doctor?Is the session over?Was it because I did something wrong?Did I mess up?Nonsense you for doing great.I just have to clean the room of itGo away mirrors are useless to ghosts.Leave my patient alone and never come backStart running.Are you talking to me?These ghosts are confusing her.I have to calm her before she hurts herself
```

### [5] hash=`766abea4ecc9c049`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p10`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（10.内窥镜.1/7 16:15）

```text
I'll take care of you miss DitterstorfTell me who is here.I'll behave miss KikanyaLook at me, pleaseWho she's a little girlhear that someone's crying fire color should be used for a burning cage did youhear something crack fall and split apart snap crackle the fire is yellingsomething's burning in the fire it's okay I'm here you'll be all right
```

### [6] hash=`a19c3817a7ccd14d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p11`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（11.独幕剧.1/7 18:45）

```text
Feeling better now?Is anything still haunting you?Talking to you?Do you remember who you are, Isolde?Oh, Doctor.I see it now.That fire.The fire that devoured everything.How could I ever forget?The raging fire consumed everything, including Teofil.He was screaming.His mind was already gone before he lighted it all.How could he ignore everything with such disregard?Who allowed him to forget with such disregard?
```

### [7] hash=`3e2e5e6a7cdfc6a7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p11`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（11.独幕剧.1/7 18:45）

```text
Well, I remember.I remember it all.I am from a noble family.I need to be a qualified Dittistorff.An outstanding arcanist.A first-rate opera singer.A good sister.And a good daughter.Never forget my manners.Never forget the family.But he...I remember now!I held the gun all the time!Theophilus stood in the study room, the flames in the hut, the beams, the ceiling, everything!He ran towards me, screaming in pain.
```

### [8] hash=`7b8094956bdcb78e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p11`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（11.独幕剧.1/7 18:45）

```text
He burned, the heat dried my eyes out.He stood in flames and ran towards me.Doctor, run towards me!Breathe deeply, Sam, out.Everything is alright, Isolde.It requires courage and is not easy to do.Most people can't do it.But you did very well.Did I do a good job?Yes, a great job.If they're so intent on the presentation of the true self, the mares in my clinic wouldlike a word with them.It is an actor's job to become another person.
```

### [9] hash=`7ed8b95c0dfdd461`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p11`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（11.独幕剧.1/7 18:45）

```text
On stage, in a fictional world, they briefly trick our eyes into thinking it's real.And to achieve that, we rehearse rigorously, through sweat and pain.They take care of the music, the costumes, the settings, the lights.Your gift helps you do this better than others, that's all.Then we needed residence permits, and now, permission to cast arcane skills.And we can do nothing but tolerate, stay polite and dignified, be a good arcanist, show no
```

### [10] hash=`478321d4f4e46f9c`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p11`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（11.独幕剧.1/7 18:45）

```text
signs of instability, because we're supposed to stay rational, otherwise, we're animals.But people are complicated, they can't stay rational forever.As Dr.Freud said, they're just seeing the tip of the iceberg.post us.
```

### [11] hash=`2cd447d185b0622c`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
Reporter of New Free Press, editor-in-chief of The Pan, the founder of Die Fakl.Oh, that's Egon Ervin Kish, the reporter who uncovered the scandals surrounding ColonelAlfred Rädl.I had investigated this before.Adolf Loos, the architect.He designed theSteinerhaus, as I recall.That's Major Maximilian Hohne and his wife.Who knewcelebrities like them would visit this exhibition.They looked different from the pictures in the
```

### [12] hash=`1cdd27681ed78dbd`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
papers.They were younger and less chubby.Has my memory failed me?Or is it because photography isalso an art of beautification?Mr.Kahl was right.People are flocking to the secessionbuilding to get a glimpse of the new art.I can't appreciate these things at all.I'veAlso keep an eye on the manners and the rituals.That's what we were originally here for.Leave it to me.I won't be sitting.Mr.Thomas, the representative, is talking to the ladies about Expressionism.
```

### [13] hash=`c8a7402e8e16d14d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
His parents did not foresee the success of Impressionism,the works that made no sense but became priceless on the market.That's why his generation overcorrects their aesthetic standardand pays compliments to any art they don't understand.The reporter for the New Free Press and that major are discussing the frequent suicidein Vienna.They've written articles about it and many of them attribute it to the publication of
```

### [14] hash=`0a5ea2774580006e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
The Sorrows of Young Weather.Tanya is describing the founding idea of this circle.This is the first magic circle drawn by the primitive men.Hmm, quite a strong woman.The military exercise in Bosnia and Herzegovina this spring.General Conrad Toulouse Power?A low-pressure trough on the Atlantic Ocean?Ivory-colored paper for official use only?The General?Wife of a cabinet member?Court sand?Is Arcanum a bacterial infection?
```

### [15] hash=`ef84844d4e804860`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
Is psychoanalysis a new type of mental illness?Mr.Heinrich is not here.Nothing useful on this page.Gold again.She's the host of the exhibition.She seems healthier than the last time we met.I don't know why, but I'm happy for her.She's about to make a speech.It is my honor to host this exhibition.Before we begin, I'd like to express my gratitude for Mr.Heinrich,who is Theophilus' friend and the curator of this exhibition.
```

### [16] hash=`93c55cece0ab9cc0`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
Heinrich still hasn't shown up.Did he notice something?And also, a friend of mine, the founder of the Circle, Ms.Clara.Without her tireless worth behind the scenes, we wouldn't be here today.Born into a rising arcane family of the middle class, Ms.Clara is a devoted doctor and an art connoisseur with impeccable taste.Dr.Kakanya is standing up, greeting the guests.Is this so?This is above my clearance.
```

### [17] hash=`09b45b244666564e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
It seems like everyone in Vienna has their own interpretation of the island.Ladies and gentlemen, your attention please.We are forming a committee to petition the Empire to cease its attacks on the island.The Arcanists there are not lunatics.They are simply living free.Their existence is a revelation to us.To help them is to help ourselves.Our society is sick.Treating the individual is only treating a symptom.
```

### [18] hash=`d0d065f5dfa95751`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
It needs a radical surgery.A revolution that would let us rediscover our oppressed nature and reinvent ourselvesin this world.Something's wrong.Her speech is...I wish for the Arcanists to unite, and establish an independent kingdom of freedom, free from repression and oppression!It's an emergency.Seal the exits.Add is all to our targets.Marcus, now!What?Am I hearing things, or did Ms.Tittlesdorf really say that?
```

### [19] hash=`2b002944fdd2f7b4`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
Forgive her.Perhaps Ms.Tittlesdorf hasn't fully recovered from her illness.I think so too.How?I did not tell her to-Ladies and gentlemen dear friends calm downDo not panic for I have found salvation for youHenry what is that behind you?Open the target showed up the golems are attacking us.I see it tooThe arcane skill of object enchantmentMarcus give it a readPlease do not ignore what miss status dwarf is saying.
```

### [20] hash=`ad3ec8b396259417`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
This is a proving ground for a world-ending experiment aA catastrophe is coming!The clouds of war are filling up the sky!Open your eyes and look at all we have now!The music, the art, the ambitions of progress!Man's gunfire will destroy them all!What are you all talking about?Not to worry, Doctor.You simply don't know yet.Follow me and I'll show you everything where your dream has taken root.This is ridiculous!
```

### [21] hash=`b30b2ad2b078f495`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p12`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（12.艺术沙龙.1/8 10:00）

```text
Any signs of the man's rituals?No, nothing yet.Golems can only be broken from within.Marcus, tell everyone the method.Ola, evacuate everyone and use the mute spell.Don't let more people hear about the error.Heinrich escaped with his old.There's an opening behind the painting.After them.Nothing unexpected.Vanna, are you alright?I'm fine.They have escaped the tunnel.Stop the chase.Let's not cause any more disturbances.

What is it, Marcus?It's too...in a branch...of the foundation?That one's loose.Exactly.
```

### [22] hash=`60655e95cff4a2c3`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Thank you for your mediation within the committee.I think you're right.Sending more people to the island will only exacerbate the trust issue.They don't trust us, and that's what Arcana wants.Things have just got better, and we can't let anything else upset this delicate balance.I think if we somehow can't come to an agreement with the Aperon,we should at least prevent them from allying with the Manus in turn.
```

### [23] hash=`dd7d49db4bc5ee6e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
The fact is, we're going astray.The emanation in 1999 had taken away almost all our outside contacts.Ever since the incident four years ago, we've been cut off from the outside world andhave become an isolated island in the emanation.And during these four years, no research on the emanation progressed.In the end, the theoretical study of its patterns was proven completely wrong.How long should we sit idly by?
```

### [24] hash=`e323cd9ed13e53b0`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Until the humans take over our island?No matter who revealed our coordinates, be it the Foundation or Manus Vindictae, someone should be held responsible.Thirty-seven is the one in charge of studying the emanation.Save your questions until after she wakes up.Six is treating her now.Also, talking about the decisions made four years ago is meaningless now.What's more, the Foundation is not hostile.They helped us minimize the damage from the reveal.
```

### [25] hash=`c195677bba3fc77b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Manus Vindicte has also given us constant material supportsince that difficult time four years ago.Ha!Thirty-seven.She is just a child, can't even handle her own business.Ever since she brought outsiders to the Sacred Place, everything has changed.You know you're judging a child in a coma?Even if 37 did something wrong, she's certainly paying for it.Don't get angry.What 42 is trying to say is simple.
```

### [26] hash=`a1efddfea31f7021`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Even if the emanation will take away the human army, when is it coming?Now that our model has failed, how can we be informed of the next emanation and act accordingly?If pure theoretical research is doomed to failure and if we must look outward, how canwe restore communication with the outside world?Do we stand with the Foundation, or with Manus Vendicti?210, your words are provocation.Are you saying that we should stop being neutral and get involved in the endless
```

### [27] hash=`161e58d86d1e8035`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Suspicion disputes?This is against what Epiron stands for.I can't agree either.The truth is supposed to keep us off the Wheel of Birth, not on it.I was just interpreting what Forty-Two had in mind.Moreover, we're already caught in the Wheel of Birth.Human weapons were undeniably dropped on our island before.The tragedies it caused and the thirst for justice will only keep us trapped in this cycle.
```

### [28] hash=`97359c236e524277`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
But what caused this cycle to begin with?Brothers and sisters, you are blinded by the shrapnels of that conflict,and you're missing the essence.Listen to me and I will tell you.Cut to the chase, 210.It seems you're the one blinded by your own rhetoric.Who can get me the stone clock on Six's seat?I'll clobber him myself.The original cause is the failure of our research on emanation.Our excellence comes from our beliefs.
```

### [29] hash=`9967a9c07e2fab35`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Once the truth fails us, the foundation that sets us apart from the world will also fail us.However, my people of great wisdom, forgive me for imagining a worst case for you.We believe the book of nature was written in the language of mathematics,and every number is a transcendental existence living in the kingdom of eternity.Math is the path to truth.The calculation of math patterns has led us to pursue the fundamental knowledge of the world, the origin of Numa.
```

### [30] hash=`73757a280da644eb`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
But what if the supreme existence has no pattern at all?What if the air been tied of Numa is chaotic and irrational?110, are you denying our beliefs?Are you saying the results we've achieved are just coincidences?The fundamental theorems of ancient mathematics, the applications and improvements from modernmathematics, the mathematical laws in atomic clocks, and leaf-benation, and every prophecyof emanation that were proven correct, were they all just a collective dream of ours?
```

### [31] hash=`4b72ff6a5ba79e86`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Well, like I said, I was just imagining a worst-case scenario.Exhaustion is also a common method of proof.Please help us, oh Epirron.Correct the errors of our souls.Bring us back on the right path.Harmonize our spirit with the flesh.Our will with life.Avoid sedition from a city.Purge sickness from the body.They don't look like seagulls.Or am I mistaken?Are these all from the outside world?What's happening out there?
```

### [32] hash=`512ca969b2565da5`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
A lovely day to rest at an outdoor cafe, isn't it, darling?Everyone working here is a capable server and knows how to address you properly withmy lady.I'm here for one simple thing.Information.With a careful ear to the goings-on, a shrewd businesswoman can gather all the latestnews.There she comes, that girl in green with the bouncing feathers in her hat.Don't worry.things said at her own expense.
```

### [33] hash=`b285e0293b011c75`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p13`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（13.岛.1/11 9:00）

```text
Words taken as jokes ignored because herwishes and anticipation outweigh their sting.But while songs are floating inthe wind, the clock keeps ticking.People in the cafe talk about thesecessionists and the newest plays in the same breath.No one cares about therumors trafficked in the newspapers.They're only concerned with what is inIn the end, they'll be like the undissolved sugar at the bottom of the cup.

My dear, your coffee is getting cold.
```

### [34] hash=`f1a0cbe41a7c40f1`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p14`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（14.费切尔怪鸟.1/11 17:00）

```text
I'm looking for a salt fountain to stop.You sure this will work?No time to complain, Doctor.You should be very grateful that I'm helping you.This is an invisibility cloak from Bohemia.It took the hair of two witches to make one.No one will see you even if you are right under their noses.Where did the feathers come from?Holy...the feathers!I should have known these arcane devices were unreliable.It was you who told me not to suppress myself any longer.
```

### [35] hash=`809a77bc6162f22b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p14`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（14.费切尔怪鸟.1/11 17:00）

```text
It was you who told me that our society needs an operationand that we, Agnestins, need a new lifestyle.Isn't that your dream too?I just want to give you the truth of the world.I just want to give you your dream back.
```

### [36] hash=`6b12313fab271ade`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
These incidents will be the index for evaluating the stability of the current error.In other words, the more reports they send, the more unstable the error is.This keeps every field investigator up to date on the situation so they can plan their next move.In the past, we have seen too many tragedies caused by a lack of information.But now, our own task is more urgent.The circle publicly committed treason.
```

### [37] hash=`bb3ef698b86bb145`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
Isolde and Heinrich disappeared, Kakanya became wanted.The Leopoldstadt riots and the march of the lower-class arcanists may be directly relatedto them.Heinrich and Isolde's speech is like the spark that ignited the powder cake thatis Vienna.The riots have been going on for days.But why was Miss Kakanya wanted?How typical of menace, Vindicte.We need to find her fast.Luckily, the spider tail you put on her is reacting.
```

### [38] hash=`47e2e58dcb25292e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
You dirty, disgusting officials!For a kingdom of freedom!For a kingdom of freedom?Shoot, they're attacking the Foundation branch?Focus on what's important, Marcus.Someone's summoned a bunch of clitters on Kertmesstraße.They're coming this way!Nothing unexpected.What they shouted?For a kingdom of freedom?That's what Miss Dittestorf said in the exhibit, and she quoted that from Dr.Kakanya.And it was me.
```

### [39] hash=`8a26ac73988f339a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
I told that to Dr.Kakanya.I told her about the island.I told her it's a place of freedom for Arcanists.So I'm the one who caused this turmoil.I told them the secret of the Golden Isle and caused the chain reaction.But trying to be responsible for everything beyond one's capability is a symbol of irrationalhubris.First of all, creating chaos in this chaotic time is more than easy.Just look at all the frequent ethnic conflicts, assassinations and espionage.
```

### [40] hash=`54632490e2dfcbcd`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
If not the circle in his old, the menace will find themselves a different flashpoint.You never know how the leaked information will simmer.Its subsequent spread is uncontrollable, and remorse would be useless.The thing is, everyone has their own ideas about that island.Your words just deepened their expectations.As for your self-assessment, we have all heard it.Humans are more rational and arcanists are more emotional.
```

### [41] hash=`55228d40dcf881a2`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
They are sensitive to the darkness in the world so they can easily become absorbedin their own emotions and ignore reality.But if we put a human child in the position of an Arcanist, who always takes on the worldbecause of his uniqueness, who is never understood for his talents, maybe he too will becomeimpulsive, sensitive, immature and unstable.And that's why it sometimes dawns on me that if we put an Arcanist child in the
```

### [42] hash=`2fd0914b5d4cf429`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
position of a human being who receives enough love, education and positive feedback,These instabilities might be controllable, at least enough to keep them from hurtingthemselves or others.Madam Hoffman?I took you away from the storm in 1912.It has been a long time after that, so I know how precious it must be for you toreturn to 1914, and your urge to complete the mission and go back to Romania.You are not an impulsive person, Marcus.
```

### [43] hash=`19164a9a2020c53d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
What if there's no right answer?What if I never told Kakanya about...Enough.You're getting carried away.There is nothing mysterious about rationality.It simply guides us out of confusion and straight to the essence of things.The essence?The reason why we're doing a job here is simple, Marcus.Arcanists keep going to the menace.It's because they can promise a salvation while we can't.Madam Hoffman, besides finding Miss Kakanya, there may be another way.
```

### [44] hash=`0f85077901ea4009`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
That painting, the last work of Teofil, The Salvation.Something's off with it.When I read it in the exhibition, I felt a familiar afflatus.It was concealed in a clever way, but I noticed the traces of concealment.Manus's arcane skill.But I couldn't read anything more from it.Now, we need to find Kakanya.Did you hear that?The sound of a match scraping against the box, igniting in a dark, silent alley?
```

### [45] hash=`1b93f2cfe7e2ab4d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
And then, war, like an unstoppable train, hurtles down the track with its passengersvanishing in the thick, black smoke.In the train, the elderly tremble in the corner and the infants babble dreaming.Next, let's turn to where the train departed, to find the source of everything.Rewind the clock to before the whistle blew, before the furnace ignited, and then, child,look somewhere far from here.In the Schönbrunn Palace, where the fine gentlemen of Austria-Hungary eagerly plan
```

### [46] hash=`94ffcd4de7fc5398`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
the extension of their national borders.A yearning furnace at last had its reason to burn, to steam toward its final destination.My dear, it's not a story of hatred or anger.The footprints were laid down before you ever stepped forward into them.Fresh-faced boys traded books and toys for rifles, and poets were buried in trenches,musicians deafened by explosions and the howls of death.But those war starters, those who doodled their ambitions on maps while supping their
```

### [47] hash=`448d00b4f08e5dd6`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p15`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（15.重燃灯火时.1/11 17:07）

```text
dessert would lose nothing in their gamble.The dew-fed river would still flow, and the facades of their great palaces would neverbe chipped or rocked by the guns they set off.Nothing stains their hands, save the cream from their cakes.Perhaps we wait.Wait for a pouring rain to douse the fires.A flood that might sweep the armies, wagered like betting chips from their maps.Then, perhaps, that car will turn and the fated dead will come back to life.

But you know that will not be how the story ends.
```

### [48] hash=`125f3c50afb42ce4`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p16`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（16.林间旅途.1/11 17:09）

```text
I care about them.Tumor said it should be removed.Look at this painting.How chaotic it is.Look at the repression in the darkness.Look at the beasts in the people's hearts.And the maggots under the golden surface.I listen to them as they listen to me.The shadowy echoes inside the skulls.The cacophonies of chaotic colours.The smudges on the canvas of rationality and the filth in front of magnificent boulevards
```

### [49] hash=`4512b7a495a6fb02`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p16`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（16.林间旅途.1/11 17:09）

```text
They were excised suppressed the top paint scraped off and replaced with an empty monotonous whiteYet in the endThey will be released to the fullestTo everything downstairs is such an explosionYou feel has leftHe shone like a star in the end, just as he wished.But the rest of them, with their rocks and shattered windows, are still left to struggle.If only I could help them, just like how I helped Teofil.
```

### [50] hash=`32abe3a22bedf9d1`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p16`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（16.林间旅途.1/11 17:09）

```text
What do you mean you helped Teofil?You were not there!He ran at me, stuttering my name.Every inch of his skin was ravaged by flame.So much pain.So much spectacle.I need to get water!But he was already on fire.And the only water I found was in his skull and veins.Miss Detestov, I sold you.You shot Teofil on purpose.So this is the truth you had repressed?You...You were right, Doctor.Lifting a repression is the first step to liberation.
```

### [51] hash=`fb05138f3325f6da`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p16`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（16.林间旅途.1/11 17:09）

```text
I am fully cured.look at me did I do a good job with me doctor I am inviting you just like howyou invited me let's heal the world and save it togetherdoctor is that miss Kikanya relax people miss Kikanya is on our side she'shelped us a lot but are you doing a gentleman from America said we coulddo something big here so I gathered everyone we will march down theKertnerstrasse to the Vienna branch of the foundation our slogan will be
```

### [52] hash=`07a4a29dbe7ea70a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p16`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（16.林间旅途.1/11 17:09）

```text
Equal rights and freedom for Arcanists.How American is that?He seems to be quite a big shot with wads of cash in his pocket and reliable connections in the government.He said we no longer have to worry about the residence permit and the Arcanum license after this job.Aren't you coming with us, miss?This kind of activity is your favorite, isn't it?Hey, where are you going?Kakanya, you should be tried and punished.
```

### [53] hash=`30e726dad42dad80`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p16`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（16.林间旅途.1/11 17:09）

```text
Why?I have something important to tell you.A catastrophe is about to sweep across the globe, but there are still things we can do.If it goes smoothly, perhaps we can save plenty of lives.
```

### [54] hash=`1349886334ec3945`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p17`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（17.艺术至上.1/12 19:25）

```text
I collected information about this opera.Rome, 1800s.Painter Mario Cavaradossi and singer Tosca are two lovers.Cavaradossi has been arrested for helping the fugitive Cesare Angelotti, former consul to the Roman Republic.To save her lover, Tosca turns to Scarpia, the chief of police.Scarpia has coveted Tosca for a long time, so he proposes that Cavaradossi will be freed if Tosca gives herself to him.
```

### [55] hash=`9ab6b329e032d099`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p18`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（18.唯有喝彩之声.1/12 20:55）

```text
Think smoothly.Isolde is going to finish the show.No one saw her backstage.Quick passage.Like at the exhibition.Marcus, keep an eye on Isolde.I'll go find Heinrich.The branch staff will take action as soon as she comes off the stage.I'll talk to you on the intercom.And request safe conduct for her and cover a dossier.Once Carpia signs the paper...Alvia se liete!O breve, ci vedo vecchia?Almost there.
```

### [56] hash=`80219379644311e6`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p18`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（18.唯有喝彩之声.1/12 20:55）

```text
Definitely, Miss Kakanya.He's not acting.That's real blood.You know, the Mr.Carl's body...The assassination in the story had come reality.Why is the show still on?Why isn't the audience reacting?What about the branch stuff?What is going on?It really is.Mr.Carl.Oh, Matt.Don't you see?Stopped from jail?You were put into jail only because you were too kind-hearted.I've been trying to clear your name.
```

### [57] hash=`46c732581f8b2840`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p18`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（18.唯有喝彩之声.1/12 20:55）

```text
There'd be a proposed and unfair deal.He wanted me as his mistress.But now he's dead, at last.The whole of Rome was overshadowed by his power.What are you talking about, Isolde?That's not what the story is like.Stay with me, Cavaradossi.I have the safer conduct.We'll go to the sacred kingdom of happiness and freedom, where no one knows us.Hardies, Potilag poisoned to death, Plasnik shot dead, and Hurtnov assassinated,

King of Greece assassinated, Archduke Franz assassinated,all these assassinations at the same time?
```

### [58] hash=`aadb20b0c8febeed`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p19`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（19.浪潮的重逢.1/12 21:00）

```text
Their faces are distorting like those paintings.Is this also some kind ofMasisteria or anyone seen my glasses?Could you pass them to me?Oh, they've grown on my eyes.Don't mind meThis to a you but you did OscarCome friends Keith and keen take your daggers and get up there.We will all kill our ownscarpiaThose so-called upper-class people don't deserve the best seats!I can almost feel the blood splashing on my face!
```

### [59] hash=`200823940fbad93a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p19`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（19.浪潮的重逢.1/12 21:00）

```text
There's no doubt this is art!The way in which reality plays a fanatic!I've never seen a schmool like this before!Zilla!Wolf!What happened?Have you got blood on your face or two?Is this part of the show or?Only each other in the frenzy is not noticing this an emergency here.Know I can't hear anythingCrowd won't let me leave.I need to make way myselfI had be quietGo to hell you terrorists.I need to I need to disperse them.
```

### [60] hash=`08f494d33e4bfba9`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p19`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（19.浪潮的重逢.1/12 21:00）

```text
So open up the exitMarcus, what are you doing?I said evacuate but people are dyingHe once told me what really scared you was not a threat to your life, but the possibility of dying ignorant.I think I understand what you mean now.I don't want that either.I don't want to go back to the headquarters without doing anything at all.Well said, Marcus.Let's go.Find Heinrich and Isolde.They might know the ritual or have the clues we need.
```

### [61] hash=`ad98cb05434a0a64`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p19`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（19.浪潮的重逢.1/12 21:00）

```text
We can still catch the last train if everything goes smoothly.Kakanya is not with you?Ms.Kakanya ran up to the stage.She and Isolde...Heinrich has enchanted all the props.There must be a hidden entrance to the secret chamber.I am sure Ms.Kakanya and Isolde are still in this theater.Come here!There are traps under the floor.
```

### [62] hash=`afc3fe500f98b2e5`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
a painting based on the mysterious island the host is is old the opera singer oh poor thingevery member of that family met a tragic end and now her brother teofil has left usbehold my late brother's final painting inspired by the golden aisle the salvationMiss Dittistoff, I know your brother's death has affected you deeplyDoctor you need to release your oppressions the rain the Golden IsleThe island of the painting is that where the timekeeper is at now
```

### [63] hash=`d11a658d6b9923b4`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
How did Teofil know about the storm and the island?He belonged to anOrganization called the circle.It's the symbol of the circle.Are they really just a group of artists?what do you see in the mirror I see golden circles teofil in the fire heburned all his paintings and then heard a shot all these assassinations at thesame time will our people be able to defend themselves on that island toTo help them is to help ourselves.
```

### [64] hash=`0a2d64773ef88fc3`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
I can see how you burned with passion.Welcome to the Circle, Miss Marcus.We share the same dream as you.I am intrigued by the name of your little group,the Circle.Even if the world ends tomorrow,we still have a show to watch.Please, enjoy.Hey, you.Steps into a building of gray and white diamond patterns,and the curtain falls forever.The smile on her face seems too serene.She is still dreaming.Her madness keeps them on alert,
```

### [65] hash=`6a044c0637e44fd3`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
but in the court she seems so meek and mentally steady,like a docked boat on calm waters.Naughty elegantly to every gentleman she meets,her world has become the performance a show that never ends I'd say she's agreat actress isn't she my dear you are indeed a great connoisseur only one actof a play can't tell a good story by itself oh forgive my ramblings thegolden curtain has risen fix your collar darling and keep moving forward
```

### [66] hash=`bf9ad90b48b28221`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
On behalf of the General Medical Association of Vienna, I would like to thank you all forattending this demonstration conference.It is a great honor.As we can see, dear friends, the era of science has arrived.The era of man has arrived.Today we will share the honor of witnessing the advancement of technology.its contributions to medical science and even the world.Now please allow me to introduce the patient again,
```

### [67] hash=`5961d51312c98854`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Miss Isolde van Dittersdorf.This lady has selflessly volunteered for the experimentand in return will receive a healthy mind in no time.She's been living a miserable life due to hysteria.How terrible it is for a young woman like her.As we all know, mental illness is taking an increasing toll on our country.Even suicide has become more rampant.The tragedies are piling up, and our dear lady is in excruciating pain as we speak.
```

### [68] hash=`4931a957ec20fcfa`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Thanks to the development of medical science, we can again be rescued from the abyss ofpain.As I said before, the electroshock therapy uses the most advanced technology available.The medical use of electricity dates back to the 18th century.Isolde, the youngest daughter of the Dietersdorfs?Oh no wonder she volunteered.The treatment should do wonders for her.You know there's something wrong with that family.
```

### [69] hash=`97c5d82d7c1e772a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Well, the artist did what an artist would do.He wrote a sad poem and then set fire to his paintings together with himself.You know what?My uncle works for the police.He showed me the autopsy report.The truth is, T.F.L.shot himself.He was killed by a bullet.Good thing he didn't have to suffer all that pain before he died.Poor boy.He was so talented and handsome.Oh, she's less fortunate.Fainted at her only brother's funeral.
```

### [70] hash=`50d43d1662f29ef4`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Didn't even get to see him one last time.I hope the latest treatment will alleviate her suffering.Lunatics.The whole family is a bunch of lunatics.Manor, sir.This is Vienna where we record these poor people.Arcanists.I sincerely hope that Isolde can put an end to her miserable nightmare.After all, she is one of the most talented opera singers in Vienna.Just like her mother.You know what they say?Talent and hysteria go hand in hand.
```

### [71] hash=`51271acb76e9bd1e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Think about it.They both come from the mind.Bye, please.The treatment will now begin.Are you ready, Miss Tietersdorf?Yes, I'm ready.because it's not like the underlying principles are the same as that frog experiment, huh?My treatment is supported by systemic series and reliable references, and it is approvedand sponsored by the General Medical Association, which means it's reasonable and legitimate.
```

### [72] hash=`a49add0afe243dfc`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Well, you are, correct me if I'm wrong, a social activist known for her little arcane tricks,Miss Kakanya or should I say miss Clara as far as I know you don't even have a medical degreeBesides your so-called art movement this secession is it it confuses me reallyAnyway in order to have a more professional conversation.I suggest we talk laterYou know after you get a medical licenseNo, dr.Schwartz this conversation has nothing to do with my personal identity or experience
```

### [73] hash=`e02974f633145e6f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
I'm only asking you as a citizen of Vienna, and as a human being, with empathy.How can you not see that she's suffering?Have you been thoroughly brainwashed by the supposed authority of medical science?Or have you two been blinded and deafened by hysteria?Oh, you rude little...Please allow me to reiterate, the EST is an advanced and reliable treatment.Besides, Mr.Tostoff has signed an agreement before we start it.
```

### [74] hash=`15bd45500ba5e094`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
The experiment is conducted under mutual consent.Your objection is of no use, and it is even harmful to the patient's interests.Be always welcome to bait.Since you question my methods, please be my guest and indulge us with your thoughts on her condition.As I understand it, Mr.Sigmund Freud published his studies on hysteria in 1895.He believes that hysteria was a psychological disorder caused by problems in the nervous system.
```

### [75] hash=`a08c8adb5a8c034c`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
It was not a simple organ disease.His trauma theory explains that the patient's personal life experiences were the real cause of the disorder, affecting the patient in subtle ways.It makes much more sense to analyze the patient's traumas than to harm their body.As to whether his theory is advanced enough, you can read the Totem and Taboo, which he published last year.What?Freud.The man who told people to marry their mothers and kill their fathers.
```

### [76] hash=`3eede5009ff29006`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
The one who couldn't get a verdict when his patients spewed insanity.It took him 17 years to become a professor, for God's sake.Miss Clara, I've tolerated your immature antics, and I always welcome advice and opinion,as long as rational and reasonable.See, we seldom remember our dreams, and even what we don't forget can be hard to understand.And that's why we need a dream interpreter.A doctor that values Shakespeare above his patients and cigars above his own career.
```

### [77] hash=`af12da589b330943`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
A doctor like Sigmund Freud lures out forgotten memories from your past through a techniquecalled free association.Otherwise, how could we prove the effectiveness of his treatments?And he has.You can read them in journals, in the textbooks, and hear them in the chattering of medicalstudents.Your name will be blacked out on the pages by then, but your dreams will become thelatest gossip on everyone's lips.
```

### [78] hash=`857b9ee199e8ddba`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p1`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（01.绿匕首.1/6 10:00）

```text
Oh, my dear, all medicine has side effects.The best medicine is bitter to the taste.Hm, perhaps you're right.It's not the only way.Do you hear that?That shrill, piercingsound of metal on the skull?Blood-curdling screams?Even the strongest soul would quakein fear.But this is the other way.However, funny enough, some people prefer the pain.It ends faster than a hard talk with the doctor.
```

### [79] hash=`87df5a2d257302dc`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
Even though they pretended to be fine, yet the source of the sickness lay not in ourselves, but in the twisted era we lived in.Radical surgery is the only way to remove this ugly tumor.And it was also you who told me to stop repressing and to embrace my desires.We should restore the world to what it was like.A kingdom of freedom where everyone will be happy.Are these not your words?Or have I misunderstood them?
```

### [80] hash=`fe37d57ed252a67a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
Why won't you look at me?Have I made such a big mistake that you don't want to see me again?No, no, no.Please, answer me.I'm begging you.You are my only friend and the one I cherish most in the whole world.What have I done wrong?Why won't you forgive me?I'm too stupid to stand your words.Because I'm also sick.The incurable tumor.If that's the case, please help me.Hold my hands.Touch my face.Hug me.
```

### [81] hash=`e855c9dd896458cf`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
Be heart to heart like you used to.Doctor.I saw myself in this dream of yours.Like I was looking in a mirror.It was evening when we had this conversation.It was the first time in my life that I saw the sun.Your dream filled my empty life with meaning.I never thought she would commit a crime over my words.Crime?Tell me, of all the books you have read, and all the documents you have worked with, did
```

### [82] hash=`e6f7dce2d42c5c80`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
any of them mention the catastrophe that suddenly broke out in the summer of 1914?The scourge of the 20th century?The real history?You have such a kind heart, Doctor, yet you don't know the truth.How are you going to bear the pain when you do?Teofil set himself on fire.Ben hung himself to death.Emmanuel laid himself on the railroad tracks.Are these the suicide cases in Vienna?They all came into contact with the menace?
```

### [83] hash=`fa80203afd266300`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
Hear them.The ghosts of future history haunting the city from above.Heads full of holes, covered in shrapnel, empty stomachs.Even the ghosts of little children.I can see them all.Cities bombed to the ground.And trains full of people headed straight for death.It is coming.Coming!By then, the guts hanging from trees will be more vibrant than spring flowers.There will be bullets, helmets, ghosts.They haven't cancelled.
```

### [84] hash=`80284a4e25be3165`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
How I wish it were a farce.A force that claimed the lives of more than ten million people.A force that dozens of leaders decided to take part in.Ben, a dear friend of mine, he played the best Fantasia in A minor ever, but came backfrom the battlefield missing an arm and a leg.And Emmanuel, his hands were born to write poetry, but he was sent to the front anddug trenches until he died of disease.Our hands are meant to hold paintbrushes, play pianos, and write stories.
```

### [85] hash=`f4a7e94ebd5b2d88`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p20`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（20.战争和和平.1/12 21:25）

```text
But they end up in gunfire because you narrow-minded hypocrites keep inciting them to violence.We've already suffered for our gifts.Now we have to watch our talented friends sacrifice themselves for man's childishtantrums.Ladies, you know all of this.Yet you call us terrorists?Real terrorists are you, humans.Sie haben diesen Krieg begonnen.
```

### [86] hash=`4396d03d9c30de1b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
Fortunately, the guiding one has heard our cries and promised us salvation.The storm will put a stop to this frenetic melody before all of the good,artistic, heartfelt things in life are destroyed before our eyes.It will wash away the unwanted, the unimportant.The creators of this chaos will be severely punished.It's still a little early for what Mr.Forget-Me-Not has planned,but the actors and actresses are in place.
```

### [87] hash=`39aa87c406395f82`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
As for you, Miss Angelotti, a choice lies before you.You have been lied to.Humans have whispered lies through their petty, made-up history.There has been genocide, the lengthy, vicious kind, under the banner of high-minded reason.They tried to split the world in two, so that the progressives cannot be stoppedby the non-progressives, so that the irrational cannot speak against the rational.When they do, death and destruction follow.
```

### [88] hash=`d79bf17daa19d8ac`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
You're one of us, an Arcanist child abandoned at an orphanage.You must have heard your heart pounding like a knock on the door.It's the sound of a long-lost soul coming home.It calls to you to rid your shackles of reason, to expose the lies of history, to embraceyour primal passions and unleash the powers of your gift.You should be one of us, as you always should have been.Right, Marcus?This is the missing part of history that they didn't let you go through.
```

### [89] hash=`3703cf4fb048049a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
Hoffman kept everything from you, didn't she?She's a liar!You're here because you want to find the truth.You don't have to work for a human institution!Pick it up, drive it into your mentor's heart, show us your resolve.An opportunity has arisen.Take it!A chance to learn who you really are, where you came from, and why you were abandoned.Very good, Angelotti!Before the High One of Midnight sheds merciful tears and washes away the sins
```

### [90] hash=`113f0d6214c6ef0a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
of man, pass the test, and join us!But you're just replacing one annihilation with another.The Foundation wants to stop the destruction, but you're speeding it up.You don't care about this era, nor the people living in it.You abandon them.You hide in your empty kingdom, in your garden that doesn't yet exist with yourart, your poems, and your pianos, and me.I just wanted to go home.Why would you take away even that?
```

### [91] hash=`9cecc85bf943cf73`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
Marcus, don't lose control of yourself.No, it's not.It's here!There it is.Let's get it over quick!He's calling me.If you're with me, Doctor, let the rain wash away the old world so we can build your dream in a new one.I thought we were on the same side of liberating our oppression, giving freedom to the Arcanists.I never thought that you would take people's lives, Isolde.I killed a man of the Foundation, thus you thought I was imposing Manus Vindicti's
```

### [92] hash=`ad71f1ee61614d6f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p21`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（21.回旋镖.1/12 21:45）

```text
cause over yours.It displeased you, am I right?Then I shall prove myself to you.I will take Heinrich's life, for that would make it fair.Please, come with meand witness my commitment, Doctor.What did you say?You're going to kill who?Miss Angelotti, if you still don't see the big picture after returning to your true self,you are not one of us.Enjoy the sifting before the storm.Ah, Isolde, you're just in time.

These two are hopeless.Hi, Millie.
```

### [93] hash=`a02a796bfe9be584`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
You're turning your dagger at meMe the one who showed you the way to salvationMe the one who brought you all to the guiding one.I even pleaded with forget-me-not to keep a spot for Kaka.NiaFor your sake.Could you do this to me?Are you trying to stop me?You still think of me as a doctor?I can't let you do any more killingMiss Marcus, can you get on your feet or slows him down get madam Hoffman to safety?
```

### [94] hash=`6669e307fdc7e00f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
You seem to be in painIt's all right.Soon you will be freed from the pain.You are out of your mind, Hoffman.Don't.There must be a better way.But how long do we have to wait for another opportunity like this?You think you can still make it back to the headquarters?You think there will be a second chance for you?Even if we fail, Marcus will be safe.The situation has changed.Kanya's decision is the key to victory.
```

