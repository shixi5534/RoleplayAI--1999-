# 剧情图谱抽取 · batch 075

- 角色：`wu_ming_zhe`
- 批次：**75** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.3」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_075.jsonl`

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

### [0] hash=`55f59cfa5aea6a7d`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Don't thank me for that suggestion, and don't think too much of my kindness.I didn't explain all these things for your sake.I told you everything because only by doing so can I enjoy the victory to its fullest.Your desperation is a good prize for me.You know I have a bad taste for entertainment.Go back to the deeper festival.At least there's one good thing left for you.You will get to see that beautiful shooting star with your own eyes.
```

### [1] hash=`73cda7848327c585`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Just like I will.Alfida.It hurts no more.She's been in Seher for four minutes, 26 seconds.Is this the reasonable length of time?I remember I once learned about the ideal time length for meditation in one of theelective classes.What's more, she's holding her breath underwater.When there is only one way to the destination, you have no choice but to take it.You have to force yourself to take that painful step and then blame yourself for being such
```

### [2] hash=`2e8c6091bf09870d`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
a desperate fool to move and lose balance.But the silver lining is, it's just a stagger on the solid ground, and you willeventually regain your footing.Leave here.Now.And get everyone.I'm such a fool.I've known that I'm not a match for Komar.I keep telling myself I did all these things to save the people.To save the village.Turns out it was me fighting against a dummy she set up.I messed up everything.
```

### [3] hash=`4d144bcdb10f274b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
For everyone.I should have listened to you.You were more sensible than just left this path.This stupid damn trap.Nothing would have turned out this way.Oh, is that how you see it?I assume you think it is this way because you have failed in the mission and thus feeldepressed and indulged yourself in some negative thinking, which is totally understandable.Blaming it all on yourself, telling yourself you will be the only one to suffer the consequence
```

### [4] hash=`e5edd1dcf0a09ce5`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
so as to alleviate the guilt, or you didn't understand what I said to you earlier atall.What?You have to stop it, Calabona.Remember what I said?You don't have to feel bad for trusting people.And here's another piece, don't blame yourself for being brave.What did she tell you?You were a fool and you ruined everything.Both of us know this is not the case.Brave or reckless, prudent or cowardly.Comments like these could be predictions, but most of the time are hindsight.
```

### [5] hash=`4d5b81428faf127a`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
The good news is we still have time to change that.You know what kind of bears the hunters feared the most?The ones which were once trapped but eventually got away.Nobody can remain a predator forever.We don't know what will happen in a next encounter.What's more, life is a long fight where we outsmart one opponent and get outsmartedby the other.That's the wisdom of nature.Bears eat salmon, wolves eat rabbit, but eventually, bears or wolves, their skin will
```

### [6] hash=`bba03289f772b6c3`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
become our blankets.A tiger might have strength, yet a rat also has its wits.You don't needto defeat her to validate your victory.You can win this war another way, a way to youradvantage.When will the wrestling between a fisherman and a fish begin?When the fish bites thebait.So if you still have some strength left in you to get back on your feet andthink straight, that'd be most helpful.After all, I don't think we have the time for another round
```

### [7] hash=`79f55983239401a7`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
of meditation.I was wrestling with- She broke the boundary between the meditator's realm andreality through me.I'm afraid the falling star will arrive early.No other way to stop her then?There might be a way to stop her by locating her in person, but I didn't spot any clue in theand now we are in a dangerous situation almost as urgent as the time when Ramawas facing the arrow knocked to a full bow instead of getting caught up in
```

### [8] hash=`93924bd8c6157f69`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
nostalgia we should take action and protect what can be savedthe arrival time of the foundation backup is 6 a.m.it'll be too late if themeteor really falls early we need a shelter that can withstand the impactalso we have to gather all the villagers and in the field training theRaktor also told us to go with you.I'll go with you.I know the way better.Besides, Shadjah is not back yet.If anything happens to she, I will not forgive myself
```

### [9] hash=`7cfac175e5b5ad96`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
I say those words.I'm staying.If I can calculate the range of damage of the comet,we may retreat to a safe location.Every rat has its day.And this rat is doing her best.Don't put on a face like that.You are not some rat.I can tell.You are the tiger cub.In the meantime, let's not forget, the real rat is still out there looking smug.Watch out for the things I knock off.I didn't do it on purpose.Give me a hand, friends.
```

### [10] hash=`608428d8e0b96f41`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
I can't do this alone.We are safe as long as they can't find us.Mr.Jinn, I'm scared.Relax, Cheena.Remember what Pati and Dada said?Just wait here and they will be back soon.Your brother is also helping them out.Those monsters are terrifying.Even Mata.Um, Mata just passed out.Don't worry.She will-You scumbags!You devils!Don't be so coward Raj!Don't be so coward!I can't believe that we need a woman's support
```

### [11] hash=`63d6939ffc5aba50`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Lala Jahan!Father!Be careful!Behind you!Oh boy!That was close!Miss Shurja, I admire you for your courage!for your courage, but this is getting a bit too nerve-wracking.Kanjana!Wait, how did you find this place?Sorry, Mr.Chacha, I should not be this mad at you.That scares me so.Sorry, couldn't control myself when my body just...Huh?Stop, kid!This hand, you, you, you are Mr.Chalma's son!Hey!You are Tikaal Chacha, aren't you?
```

### [12] hash=`dd7bb54412efcb7a`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
It's been a long time since I've met you.How come you're here?Hello, uncle.There must be a lot of talk.But not right now.There's going to be an earthquake here.The impact of the earthquake is going to make a huge hole.And that earthquake is going to be here before the foundation's help arrives.But you guys are luckier than anyone else.because we were able to find you all first.Let's go, Uncle Takal.
```

### [13] hash=`003cc8c1a1daabd6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Let's go to my house and talk.You remember the way to our house, don't you?What?That burnt-out old house?I've never been here before.Then you'll have to forgive me.You'll go with us.Even if I have to lock you up and drag you away.No!Alright, I'm glad to see that you're fine, Ms.Shurja.We are in dire need of a helping hand.Ms.Shurja, I remembered you know this place well.Yes, I do.We need to transfer everyone here, humans and Arcanus, to a safe place.
```

### [14] hash=`c7bd799837e50439`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
And you're the best person to do that.I...alright, I'll do whatever I can as long as it helps.I wish my father could see this.Isn't she a lot more reliable than I am?I've told the old man a million times that humans make more decent work partners than Arcanus.I hear you!Sharjah, please briefly tell us what the neighborhood is like.We need to pick up everyone in the town as soon as possible.We need to find the quickest way to do it and avoid all the enemies on the way.
```

### [15] hash=`a8b08122ff7b9eb1`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Hey, relax.We can't run away from them.We will just run over them.Look at my back!The Balahs live near the village entrance.The fastest way there.Oh an auntie star.She lives atHey people that rumbling noise sounds like giant rocks rolling downhill those guys are catching upWanna watch the aerial stunts?No need to look back fine wanna watch timeDon't blinkThis is the fastest route the last house is right there, but
```

### [16] hash=`efaf8cc47efc4b71`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p28`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜8~12）

```text
Woohoo!Living my wildest childhood dream!Can I just run over them?Not cause any damage to these arcane monsters!Seems like we have to fight.I hope this is the last trouble we have to deal with.We are running out of time.One, two, three...Okay, all are here.We got everyone.The gas pedal is more heavy.Oh!I'm going to the car!There are a lot of animals there, huh?I can only see your face from here.I have a feeling that you will have to do this right now.

In fact, this was your first time.This will be over soon.Because we have such an excellent driver.The journey can be over.But it won't take long.
```

### [17] hash=`55c13739e0604dff`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
How is everything now?Well, it's going smooth.The young people and tourists left as soon as I persuaded them.Only the old and the children are left here.It's not that easy for them to move, and...You promised to give me half of it.Now what?The boss cannot keep her own promise?Hmm, I do most messenger work.More food for more work.These kids were abandoned and driven away by humans.I'm glad to see Kanjra get along with them.
```

### [18] hash=`28322aeb3ad06107`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
If she could enjoy life like this, nothing.You just reminded me of my mother, Sharjah.Perhaps people like you are the key to saving all of us.I just observed it again.The figures are showing a grim picture.Luckily, I've worked out the specific range of damage.As long as we can get out of this radius, there will be no casualties.As for other losses, they are beyond my ability to cover.The airship of the Foundation is on the way.
```

### [19] hash=`615ad58046800ea2`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
At least our water supply is secured for now.But the problem is, such a distance!The distance.Even if we follow the straight line, it is impossible for us, for the elders and the children, to get out of it within hours.We are getting so close to success!We could go underground!Underground?Wait!I remember my old man told me about an emergency tunnel leading to the forest on the mountain.Its entrance is right here, beneath the floor of this very room.
```

### [20] hash=`770a7af21b82bc2a`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
A tunnel?He told me this, hoping that one day I will take over his responsibility to look after the village.If I remember it correctly, that forest, which is also the exit of this tunnel, is right outside the impact area.That's great.In the tunnel, even if we don't make it to the forest in time, we can still avoid the damage.But, the problem is, there's a gate to the tunnel.Now, just for the record, I'm only quoting my old man.
```

### [21] hash=`0f53fa168d9653e3`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
It is a gate which only opens to the leader who has earned his people's trust.V is going real treasure hunting this time.Oh, well, my father's version was hardly as exciting as open sesame.I didn't believe him even as a child.I tried to open it by force many times.Well, it never worked.My old man was telling the truth.Things would be problematic for us.Because I don't think I can get that gate open.
```

### [22] hash=`c39838233d2f661c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Firstly, I've never wanted to be a leader.And speaking of the people's trust,How do you think those cursing old men in the yard will feel about me?Hmm, even so, we will open that gate.Even if we have to smash it with our bare fists.I'm not sure if you are being sarcastic.It's the best way in the current situation.Watch your steps.Especially since this is truly useless.What did I say?This is never the gate for me to open.
```

### [23] hash=`6b48e12177dae250`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
I knew that you will kill us all.You scoundrel.You can't protect your family.So how will you protect others?Oh god, please listen to our prayers and send a martyr for us.With the trust of humans, we have...Me a brick?And you?Me?What about me?King don't you now you go dumb can't defend yourself.I just don't understand youand you say why is you afraid can you shut them out in thing story only themost smart and wise people can open it why do you hesitate now little one you
```

### [24] hash=`d105b9142c9ca9ac`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
think I'm the smartest and wisest person no but why ask me it is yourMy answer don't matter.Their answer don't matter too.Said you should shut them up.There will be a gate for me and I will open it my way.I am the one to decide how to open my gate.My spell will be longer and cooler than some open sesame.Not jealous you.Interesting.Looks like dad was right.I am not qualified to be a leader.Thanks kid.
```

### [25] hash=`2c435ddf4ecbb515`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Anyway, times have changed.Forget the spell.But this is me, wherever I am.Not that.Screw it.I have no idea what my father once promised you.In fact, I have no interest in what your old heads think.But what is my way to open the door?And the one standing right here, right now, is me.Not another Sharma.That is to say...Turns out the gate is much more fragile than I thought.I'll smash that door open, even if it takes the other arm of mine.
```

### [26] hash=`41b343f7284fe5ef`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
That's what I'm talking about!So cool!I guess you didn't see that coming.To tell the truth, I had prepared myself to bounce off from that closed gate,like what had happened many times when I was a kid.See how I burst it open?That was cool!Ho!Ha!Though in the end, my dad was just telling nonsense to a kid.Those so-called profound teachings, like one needs adequate strength or a sense of responsibility.
```

### [27] hash=`e7d5de4356493639`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Those were too abstract for a kid to understand.That's indeed his style.But in the end, the door was opened, that's for sure.That's a good ending for a story.At least a million times better than mine.You have a long way to go before reaching the end, but I'd say you're in a much better place now than you were in the beginning.It's good progress, trust me.He who only stays behind a closed door will turn away many things, including a chance to survive.
```

### [28] hash=`0b645262246961db`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Alright, alright!Rose rabbit ever!Mr.Ja, you have the first bite?A person with no family, yet radiates the warmth of family to others.Only Kumar had the slightest warmth from someone.Maybe such an absurd thing would have never happened.I doubt she's upset about what happened.Maybe she has found herself a good seat to enjoy this dance of Shiva.That's true.She's the kind of person who always finds herself the best seat to watch the show.
```

### [29] hash=`d103f96790d44ff7`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
But I'm curious.Tell me, did she…It was not a part of a conversation.She just admitted that she was being vindictive.Maybe I was being vindictive out of hatred, like you said.Like you said.The realm can never extract every word I've said.It's theoretically impossible.Where, where did she hear that part?She was in the same room.How could it be?I know that room well.We have searched every inch of it, unless she was hanging on the ceiling right above us.
```

### [30] hash=`4e609d8f44e45ae3`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
As I said, she always finds herself the best seat.To be someone who can smile knowingly at the argument made by the lecturer,knowing full well the thinking process behind, while staying close to other whispering opinions,Like a perfect observatory, from which we witness the events in the universe.Maybe I've been in the wrong direction.She didn't make the star fall as revenge on the village.This guy was the shaman.
```

### [31] hash=`c0c8309cfa30334c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
She was not on the ceiling.Are you taking me seriously?That was just a joke to lighten up the mood.Under the ground.Remember the underground survival guide where we found this photo?she's right under that house first to the corner crazy it has gone beyond myimagination sorry but you don't have to come with me if you don't let me see myown sister I will be dying for answers who would dig a basement here that
```

### [32] hash=`b5592aad5ffc372f`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
reminds me how curiosity is one of them well the major reason she did it'spossible that she was well prepared last time she came back to more pumpI never thought she foresaw that we would be kicked out from the project.And as you just deduced, she did so to see that star?Almost 100% sure.Without me, she must have asked the Manus to support her with arcane skills.This way, I knew I was extremely mentally unstable when she left me.
```

### [33] hash=`322b08099093bd41`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
It wouldn't take any effort if the Manus had the intention to recruit her.Watching the meteor shower and being destroyed by it has been our plan all along.At this point, it is hard to say who's worse, she or we, since we have prepared to diewith our evil plan.However reluctant I am to admit this, sometimes Arcanus are indeed strange creatures.It's like a madhouse party.But what did you teach Matilda before we left?
```

### [34] hash=`8b9738fe81ca30e1`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
That's our only chance to survive in her realm.I came up with it when I was calculating the range of the fallen star damage.Hmm, as I said, you are the tiger cub, trying to take a bite in the arm, even when thehunter has had you in her grip.That matter was between Kumar and me.There is another theory according to my calculation.If there are more observers, the realm might collapse.It's the only theory Kumar does know.
```

### [35] hash=`ddfb50ff21fb9cb3`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
At the same time, it is not yet strictly verified, but I have faith in that girl.She's indeed a genius.I hope it's not too late to make our last attempt.If you ask me, it's not yet the time to make that attempt.Haha!This must be the appetizer she served us!Great Shiva, I hope your fists feel as light and crispy as pani puri when theyland on my body.Look over there.It is empty down thereThe showers estimated to fall at 4 a.m.
```

### [36] hash=`5a5ad6cd2e677d58`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Today by then the comet will alsothree and a half hours to go OhAlmost forgot about thisMusic you're right.It's not too high forMe happen to you.OhWell, I didn't expect so many visitorsSince you're herePlease take a seat.I built this place by myself.It's not a big room, and not soundproof.I heard you very clearly under the ground when you searched the room and went through my stuff.What's wrong about an astronomer reading, calf-feeding and management?
```

### [37] hash=`3c94d555d90677c6`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
You should have left.My plan has changed.Let it be, let it be, didn't they call this destiny?You know about destiny, right, Caliborna?Marching the stars with me, good, it's like living the old days again.Sister, you're in the realm, what did the Manus do to you?The Manus?Oh, they're fine, helped me a lot.Impressive arcane skills, experiment apparatus, and food.Lots of food.These...Seems like she's no longer capable of commanding those wandering madness.
```

### [38] hash=`c5b03d9f627662fd`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Priority is to stop that star.We can deal with the rest.You're going to stop the comet.You are taking it from me.Again?I will never...I will never let anyone sit their hands on it!I am gonna throw up.It feels strange in here.Was that...Master's face?I can keep.It's hard to get used to it for the first time.I feel a lot better in here.I'm sorry, Calabona.I don't think this body of mine can hold any longer
```

### [39] hash=`13c551fb4dcdfe99`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
for a more appropriate meeting in the real world.I'm glad you came back for me.What I said wasindeed too harsh.Why do you have to?Look at you.The price is too high.In the first instanceI did have other intentions.I kept imagining how my so-calledparents would reactwhen they were about to get crushed to piecesby the store.Little did I know,They have already paid for what they've done.I worked myself to the bone, but who knew I would lose everything, including my purpose.
```

### [40] hash=`e23e5d0649f5b166`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
It really sucks.But it's okay, just a minor setback compared to what I've been through.It's not even worth mentioning.That's why I changed my mind.To see it, the star we can't see with our eyes.Seems like I was not very careful about my wording when my mind was clouded.It is a celestial body, Calabona, not a star.It could even be a moving black hole.I'd rather you did this out of the hatred towards the people who abandoned you,
```

### [41] hash=`567d01b7149322d3`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
or even towards me.For I carelessly exposed my identity as an Arcanist, and thus you lost your home.I wish the same.I wish so badly that I could just be filled with pure hatred towards someone.But I can't, kid.You're the lucky one, young brother.I was going to kick your butt in our last encounter, but I just couldn't do it.But the Manus has made you.Kid, Banner University can get my names on the SCI list,
```

### [42] hash=`b82e8a6e3c675f01`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
while the Manus allows me to touch the universe.They are not that different to me.Sister, mother told me about this.You physically can't take such a great amount of Arcanum in you.The menace should also know this.I appreciate that they remembered this about me, but this is the path I chose.When I look into the sky, I feel myself the freest being in the world, the universe.What a vast, life-embracing place it is, no matter if you're a canist or a human.
```

### [43] hash=`a2d7d76fd38d7f48`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Even a grain of sand, it encompassed everything, but I was driven away from studying it, abandonedby my own family, for some insignificant, unimportant reasons.I should have understood this earlier, that my struggle means nothing on this planet.Kalapana, I just want to see that celestial body with my own eyes.Now you look at the star, the telescope shouldn't be placed in a basement, and you shouldn't
```

### [44] hash=`4a1fe037f64cee0b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
lower your head.How long has it been since the last time you looked up at the night sky, at theother stars?What's more?If the star falls, people in the village, including those kids, none of them will survive.The madness you summoned here has brought disaster to this place.To the people and their families.They are not the sacrifices of your wish.Stop heading down the wrong path, Kumar.You know what?
```

### [45] hash=`05c729bf97088b69`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
I don't care about them.Just like they've never cared about me, haven't they?Sorry.Please indulge me with one last willful act.This is the path I chose, and you can't stop me, Calabauna.Matilda!They made it!Quickly!Do you understand?Yes!That's what Miss Calabauna taught me to do.But I can't see anything when my eyes are closed.Don't rely on the eyes.Hold this crystal and take a deep breath.To feel, um, what she said?
```

### [46] hash=`fe7f484e6909fc68`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
The change of the universe.Meteor shower is starting earlier!What did you do?That's the method only once known between you and me, Komar.The observation method?You told others about the celestial egg?So what?I see.You once pitched that research proposal to me.You are indeed my best student, Kalabona.I really understand why you asked me to keep it a secret.Even if we named it Egg, it's actually a projection of the universe which has the same feature.
```

### [47] hash=`10b7446a624ab296`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
The universe is infinite.As long as we observe it self-consciously,think each of ourselves as one of the centers of the universe.The Egg will then collapse because of multiple centers, until it puts a quietus in everything,including that star.A shattered mirror will never be pieced together againIf there are enough forces to break it, am I right?Then there was neither existence nor non-existence.There was neither the realm of space nor the sky beyond.
```

### [48] hash=`5e4322fd09ec408b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Who could master these skills?Those old fogies in the village?A genius girl and a bunch of kids who looked up at the stars.I'm sorry, Kumar.I have to.No, we have to stop you this time.I can't let you destroy more, punk.Or destroy yourself.Even the unfortunate may reverse what's irreversible.Either do it quickly, or hold her off.The realm will collapse once the observation starts.And I believe in it.
```

### [49] hash=`8eb659d7e37769a7`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Don't rush it.She seems to be waiting as well.She's accumulating power.As the nebula collapses, no watching eyes will survive the destruction.But you should remember, it's not eyes that our observation belongs on.To others, our method to see that star.You have really ruined everything this time.How dare you!I didn't take advantage of you.You and I, we are very alike.Why are you treating me this way?
```

### [50] hash=`332ae58ba4d5735c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
I wanted to see that star.Why did you stop me?Why?How dare you!We humans?We wouldn't have to waste time on this, right?You Eden!causing us to leave the research data behind, so that you can make it yours.Wanna watch the aerial stunts?Time.Handle it gently.Bright wind.Pacific version!If I can push it a little further, I've lost everything.I don't understand.It's about to collapse!Gotta go now!Kamar!
```

### [51] hash=`572a2fb580108f0c`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Mr.Shermain, you covered me.I'm fine.Pretty.taking that falling star with it tonight only the meteor shower will sparkle inthe sky come on I'm still here how about we go back to the institution to theuniversity there's no place I can go back to yes there is you can see myplace you can use my lab we can start over sure really you will let's goI will not come to this world again.So this is what Chandigarh look like.
```

### [52] hash=`65413e5467e3c811`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
It's sleigh!What's this?Candy?This way!Come over here!Ah!So you're only an assistant.No wonder they made you go through so many procedures earlier.You is just spooky!You better be careful!Otherwise you will regret your doings when you get to the foundation!Make a face for me!Ms.Scherja and Mr.Sharma, thank you so much for helping our staff.Um, you flatter me.I just did what I could.No, madam.We've ascertained your achievement.
```

### [53] hash=`c401b5192bcfdacd`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p29`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-活动】行至摩卢旁卡｜13~17）

```text
Before this incident, you volunteered to help over 10 arcanists and human children.And this time, you rescued more than 30 arcanists.That's remarkable, madam.What's this?Oh, I think it's not a good time for her.They will be back after the meteor shower.Son, I wish I can have my stomach full every day when I go to school.It's my dream to take tea even though I'm still a good boy.Alright people, don't be greedy.

One wish only.
```

### [54] hash=`bffdaf33d715e642`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p30`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】晃铃响于山谷.鬃毛砂砾）

```text
To the higher place?All the poisoned arrows, deadly traps, and the fierce animals.This face even looks welcoming to me, my friend.Wise to wade this river.Seems like I'm not welcome here either.Just walk it off while you still can.Nothing to complain about.Seems like you've been feasting in the past years.I wonder what your teeth can do to the stones,if they couldn't even break up human bones?Um...
```

### [55] hash=`295fcb238d4eb32f`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p30`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】晃铃响于山谷.鬃毛砂砾）

```text
And this again.Fall for this again.I will stand here and watch you burn to ashes.I'll kill you, dumbass!I have no idea.Don't need you here.We're no longer a shaman.Take your hats off me.Your mother and I, the entire family,have invested years in your education.Yet you have let us down.I can give everything back to youAs long as everyone gets out of this place!White elephant will look after your soul.
```

### [56] hash=`73b02ca61ded691b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p30`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】晃铃响于山谷.鬃毛砂砾）

```text
Now you see me as your sister.I remember you were this tall.Don't look at me like that.Little one, shall we make a deal?Give me a hand, friends.I can't do this alone.Cut your warm belly open before you pierce my neck with those teeth and suck up my blood.Run your part dutifully.And when we first met, you nearly blinded one of my eyesInto the wrong place.Hey little fella.What are you doing here?Stay there.
```

### [57] hash=`bbfd5c68f3978fd0`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p30`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】晃铃响于山谷.鬃毛砂砾）

```text
Don't move enoughNow that's enough my friends.Sit sit a feast has been given to usMother Nature wish me luck.Now it's like give me a hand friends.I can't do this aloneI think I got the stubbornness from you fatherprotection
```

### [58] hash=`386c3015e76a61f2`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
For us?It was supposed to be a quick nap.She did that again?Need to be my last project here.That's right, I should have done this earlier.Much better than I thought.Lucky.And we're walking in an institution, not a pet store.Remember to tie it to the door.We have never seen it with our own eyes though.Yes, miss.So, Sirius, Betelgeuse.They look so close to each other in the eyes of mankind.but they are actually over 600 light years apart.
```

### [59] hash=`70a3821cb527f451`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
Relaxing is important for...Deadline.Because of the bad weather, they have to come here another day.You should go with them.The admin here.I love this big girl.She's beautiful.Nice taste.But I'm not the admin.Researchers should treat their observation data like their own child.Will you leave your child to the homeless on the street?Sorry, no offense, Garaf.Kumar, I've already been away from home for two whole days just to fill in the observation
```

### [60] hash=`446370887bb22b4d`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
data.Don't harm me, Kumar.I won't come back.On life.The report given here concerns the work the supernova under the binary star systemof White Dwarf FYDL 82A.Thank you for listening.You're an Arcanist, right?Of course, everyone is welcome to study astronomy.We astronomers have an open mind.That's what's been written here.I will never approve a report written by an arcanist.Astrolabe, spice and hourglass.
```

### [61] hash=`3ea2e49ad184ac3a`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
It's not a game with my stupid little daughter.If you do the research in a human way, I'll say nothing but welcome.However, you acquired all those data through absurd methods.Apologies.You made a valid point, but I don't have the evidence of something I did not do.I have no further questionsIn conclusion, a supernova that is closer to Earth than any other ones in history will take placeYour conclusion shocked us
```

### [62] hash=`1cde34498f7e8e5e`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
YesI will take responsibility for the public opinions it may causeIt's a price I have to payCan't be certain that it will go the way I expectI'd say this report is a doom-mongering workA smart answerBut time will tell if you're a sly arcanistAt least better than Kumara's bedroom.So the past data of the secondary star is...These data!The movement of the secondary star was even more extreme than it is now.
```

### [63] hash=`4b1f9ee8145d9066`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
It was even closer to the white dwarf in the past, until it reaches the extremumand deflects away.Prediction is, something must be wrong with these data.Either the observer, or my mistake.Try again.What's this?So none of you know what it is?It's ridiculous that the emission would let you students with no common sense get into my classroom.Please come see me after the class.How long have you been here?
```

### [64] hash=`e55f160c55ebcd6e`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
You would like to see it, right?The accurate and precise data to us means the same as the stunning night sky to them.The switch.Normal data too?Is it possible that the changes of the orbit follow a certain pattern?No way.Origin of the star Faust.A star in the system which is yet to be found.Try this.It's an effect.Happening.I negated my own theory and rebuilt it again and again.Every time I found this spark of hope in the darkness, the truth just put it out against
```

### [65] hash=`9a3d82689579572b`

- lang：`en`｜version：`1.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p31`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.3-角色】尘埃与星的边界.伽菈波那）

```text
my will.I think I'm ready.I still have this broken shirt.Stars don't die.They don't need to eat.No one can occupy them by spending money.They are so beautiful.My daddy is in Maulino.The stars are the only one thing we can watch together when we're on the phone.The sink full of greasy dishes.Endless housework.I want to run away from them.Even though life was filled with unstoppable snores and cries,

I knew I was living for myself as long as I still saw the stars.They are just there.
```

### [66] hash=`84b9d76927c7b09b`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
year old me was fierce, ill trail.You came here sooner than I expected, Kalapuna.Knewyou would come.See you again.I miss you dearly too, my child.I hope you've beendoing well while I was away.Hope you're happy with the surroundings I set.I alwaysfind it enjoyable here, a place full of memories, and perfect for small talks.A draw thatsuffered, miss.Someone is having a worse attitude these days.There's no need to look around, kid.
```

### [67] hash=`a53bc4cef0047053`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
I already had a few years of experience in the field before you started your research, and oneof the most basic skills one has to master in the meditator's realm is to cover up thetraces of reality.Even so, you didn't even think about creating a starry sky for yourselfhere.That would be unnecessary.You can see it any time outside this realm if you like.Why did you invite me here?I know you've put in a lot of efforts.
```

### [68] hash=`78f3b16a64c3beca`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
I understand the difficulty within, and sympathize you, Lapona.I always do.Just like what I did with my younger brother.By the way, that letter has been delivered tohim safely, I assume?You're smart enough not to bring the fish new statue with you.Did somebody kindly remind you not to do that?Never mind, that's not helpful.I don't understand.Why involve him?Maybe I was being vindictive out of hatred, like you said.
```

### [69] hash=`a2bae0c841f18f36`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
After all, they precluded me from doing anything even before I give it a try.Although my misfortune was not my brother's doing, there's no one else left in the family to take my anger.So ask me now, ask me anything you wish to know.I can tell you everything.What you're curious about, what you're confused about,anything you can't work out in your little brain.I can explain it all.Hasn't the idea that I might locate you bothered you for even a second?
```

### [70] hash=`ca030f4edab734f6`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
Locate me?You are still as naïve as a child, my Kala Pauna, you little dummy ulu.That is simply impossible.This is the first time you doubt my capability.Why would I do that?Of all the students, you are the only child who is smart enough to follow my steps thisfar.You just don't have time on your side and need a better mindset in dealing withunexpected.I've tried to teach it to you.Remember those impromptu speeches I asked you to give?
```

### [71] hash=`63425b1cab6154be`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
Those were good practice.Don't have?What do you mean?Perhaps you have put too much stockin the idea that I will rely on Manus Vindicte in this.Instead, I trust myself more than them,and of course I also trust you.What's more, they were never good enough for me.But luckily, I have never been a real Arcanist or a real human, only pretending to be either of them when necessary.I can easily act like an Arcanist to gain their trust, just like I could act like a human when I was teaching at Venner.
```

### [72] hash=`11c77e39f7b29f32`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
What are you staring at?Take it if you're interested.You thought it is the key to cracking the meditator's realm like the stone statues earlier?Though it is too late for hints, there is one thing I have to remind you of.You didn't catch up to the real me, nor did you improve the situation by entering therealm.You chased me all the way here, chased the hope of winning against me, but you onlyhelped me complete my plan.
```

### [73] hash=`63c36ccc48334589`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
The moment you entered the realm, the last step of my plan was done.Completed what as you know exerting influence on reality through the meditators realm is challengingafter all this realm is like the shadow of its real counterpart aReflection of reality I went to a lot of trouble even wasted a statueTo finally stick out a corner of the shadow over the boundary of the two worldsYou mean the statue in the cave?
```

### [74] hash=`a0b8f87a16be3569`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
YesWhat I needed was an outside in-force to break the realm, which is almost unbreakable from the inside.A mirror can reflect objects, but there's nothing it could do to itself.It can only be shattered into pieces by people not from the reflection, but reality.Whenever there is a shooting star streaking across the sky of this realm,Whenever there is a shooting star streaking across the sky of this realm, an equally beautiful
```

### [75] hash=`25547baccddba4db`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
star will fall on the real earth.And guess what?You are the force I'm looking for.No.How?So the fluctuation I detected, the energy of the celestial body felt by the FoundationGirl, are just false alert?Oh no.I have to admit, that young girl was not part of my plan, but at least you are on the right track about what happened.If anything is to blame, it's your ego.You were trying to win, but not by saving people.
```

### [76] hash=`0b8a1fcbb207f77a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
The idea of proving yourself to me outwaved their lives.You must be wondering, how could she lay such a trap with her insignificant arcane power?She can barely lift a lump of clay.She must have had the Manus Vindicte on her side to help.All that being said, you don't have to fuel yourself to be a lesser version of me.You're still my best student, my best colleague, and my strongest rival.Well, with some room to improve.
```

### [77] hash=`0b8e4822e2b10848`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
Even this time you didn't lose the game for lack of wits, but for the fact thatI know you a bit better than you know me.And I simply have more experience hunting a prey.You and the madness have never, never thought thatif I didn't enter the realm to see you.Then things are going to be tricky for me.You would be enjoying a happy deeper festivalwhile I would be crying in a dark cornernobody knows of.
```

### [78] hash=`9c01806b7cb182a5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p10`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（10.篱笆墙之外.）

```text
Why would you?Well, time's up.Remember to ask the most important question first next time, chat.Don't thank me for that suggestion, and don't think too much of my kindness.I didn't explain all these things for your sake.I told you everything because only by doing so can I enjoy the victory to its fullest.Your desperation is a good prize for me.You know I have a bad taste for entertainment.Go back to the deeper festival.

At least there's one good thing left for you.You will get to see that beautiful shooting star with your own eyes.Just like I will.Alfeeda.
```

### [79] hash=`7603b39cfe871111`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
My ankle hurts no more.She's been in the hair for 4 minutes, 26 seconds.Is this the reasonable length of time?I remember I once learned about the ideal time length for meditation in one of theelective classes.What's more, she's holding her breath underwater.When there is only one way to the destination, you have no choice but to take it.You have to force yourself to take that painful step and then blame yourself for being such a desperate fool
```

### [80] hash=`7797e81cd4c8cc48`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
To move and lose balanceBut the silver lining is it's just a stagger on the solid ground and you will eventually regain your footingLeave herenowAnd get everyone want to blame.I'm such a fool.I know that I'm not a match for KumarKeep telling myself I did all these things to save the people to save the villageTurns out it was me fighting against a dummy.She set up.I messed up everything for everyone
```

### [81] hash=`e61343f2cea6e1f3`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
I should have listened to you more sensible than just left this path this stupid damn trapNothing would have turned out this wayIs that how you see it?I assume you think it is this way because you have failed in the mission and thus feel depressed and indulge yourself in someNegative thinking, which is totally understandable.Blaming it all on yourself,telling yourself you will be the only oneto suffer the consequence so as to alleviate the guilt.
```

### [82] hash=`79d97dcead8ddf33`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
Or you didn't understand what I said to you earlier at all.What?You have to stop it, Calabona.Remember what I said?You don't have to feel bad for trusting people.And here's another piece.Don't blame yourself for being brave.What did she tell you?You were a fool and you ruined everything both of us know this is not the casebrave or recklessprudent or cowardlyComments like these could be predictions, but most of the time our hindsight's the good news is we still have time to change that
```

### [83] hash=`4cf9fb055eea9cfe`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
You know what kind of bears the hunters fear the most the ones which were once trapped, but eventually got awayNobody can remain a predator foreverWe don't know what will happen in the next encounter.What's more, life is a long fight where we outsmart one opponent and get outsmartedby the other.That's the wisdom of nature.Bears eat salmon, wolves eat rabbit, but eventually, bears or wolves, their skin will
```

### [84] hash=`200ac51c1bc0be52`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
become our blankets.A tiger might have strength, yet a rat also has its wits.You don't need to defeat her to validate your victory.You can win this war another way, a way to your advantage.When will the wrestling between a fisherman and a fish begin?When the fish bites the bait.So, if you still have some strength left in you to get back on your feet and think straight,that'd be most helpful.After all, I don't think we have the time for another round of meditation.
```

### [85] hash=`aec83b3636e324f7`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
I was wrestling with...She broke the boundary between the meditator's realm and reality through me.I'm afraid the falling star will arrive early.No other ways to stop her then?There might be a way to stop her.By locating her in person.But I didn't spot any clue in the realm.And now...We're in a dangerous situation.Almost as urgent as the time when Rama was facing the arrow knocked to a full bow.Instead of getting caught up in nostalgia, we should take action and protect what can be saved.
```

### [86] hash=`339f140615f4348a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
The estimated arrival time of the Foundation backup is 6am.It will be too late if the meteor really falls early.We need a shelter that can withstand the impact.Also, we have to gather all the villagers.And, in the field training, the instructor also told us to...Go with you!I know the way better!Besides, Shadjah is not back yet.If anything happens to she, I will not forgive myself I say those words.
```

### [87] hash=`7b41e6e6e8b2391a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p11`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（11.硕鼠的智慧.）

```text
I'm staying.If I can calculate the range of damage of the comet,We may retreat to a safe location.Every rat has its day.And this rat is doing her best.Don't put on a face like that.You're not some rat.I can tell.You are the tiger cub.In the meantime, let's not forget,the real rat is still out there looking smug.Watch out for the things I knock off.I didn't do it on purpose.Give me a hand, friends.

I can't do this alone
```

### [88] hash=`1b1bfafa7cad237d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p12`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（12.以卵击石.）

```text
We are safe as long as they can't find us.Sujan, I'm scared.Relax, Jeev.Remember what Pati and Dada said?Just wait here and they will be back soon.Your brother is also helping them out.I'm fine.Even Matta.Matta just passed out.Don't worry.She will...Sali, you meanie rakshas.Gaye dekhi re.Pitaaji, humi vim bhot saare hain.इतने पुछ्दिल मद बनो राज, मद बनो, इकिन नहीं होता है कि हमें एक इंसान नर्की के सहारी की सरूरत पर रही है, ला लजा हम पे पिटाजी कहां से, एक पीचे,
```

### [89] hash=`660fc4a31013e36a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p12`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（12.以卵击石.）

```text
Oh boy, that was close.Ms.Shurja, I admire you for your courage, but this is getting a bit too nerve-wracking.तर्जा!गंजरा!Wait!How did you find this place?Sorry, Ms.Sharjah!I should not be this mad at you.That scares me so.Sorry!Couldn't control myself when my body just...Huh?रुको बच्छे!यहाँ बच्छे तुम तुम तुम तुम तुम चर्वाजी के बिच्छे हो!अरे!आप तो तिकाल चाचा है ना?कित्ने अर्से होगे आप से मिले होएते तू तू कैसे?
```

### [90] hash=`1450eeeba05cfc04`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p12`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（12.以卵击石.）

```text
तकाल चाचाहोत पाते हुँगीपर इस वक नहींइस जगा एक उल्कपिंद गेरगाइसके प्रभाव से एक विशाल गड़ा बान जाएगाऔर तो और वो उनकपिन यहां पर फाउंडेशण के कोई सहाइता पहुछने से पहले आगिरिगा।बार आप लोग सब से ज्यादा कुश किस्मित हैं योंके हुम सब से पहले आप लोगो को डुनद पाई हैं।चल्ये तकाल चाचा, मेरे गर्ब चल्गे बतक करते हैं, आपको हमारे गर्कर रस्ता याद हैं न?क्या, वो जिला हुए प्राना गेर, स्वाली नी उत्ता, कभी यही?फिर तो आपको मुझे माव करना परेगा।
```

### [91] hash=`f0ee184ce1850a67`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p12`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（12.以卵击石.）

```text
चाजा, आप हमारे साथी जाएंगे।भले मुझे आपको बंदकर किंज के लेजाना परेग।बाज़े लेज़े!आप ग्राइट!आप आप आप प्रजा तो आप रहा हैं।आप आप आप पारीजा नहीं हैं।टांबलेंग!इस का फास्तिस हर्ट!अच्टनी स्फार्प है...अच्टनी स्पामत!उन्हाक एट्राना रच्छान्हूद्ट द्रीम!नौजी!क्या आप इसा रिना और धे पामारे में ळब वारा गाए रहे हैं?और हम तकला एसा ताखों करें।और अभी नहीं ज़ियें हमाद तकला की किनते हैं!आप पाथ पीर हैं!नहीं आपके पगरी दे्ख sean कहों!

मुझे दरहे है की आपको अबी इस इसे नहों ताना होगा!उसे आप पाथ पिर हैं!
```

### [92] hash=`f35e98b38358ee7d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
How is everything now?Well, it's going smooth.The young people and tourists left as soon as I persuaded them.Only the old and the children are left here.It's not that easy for them to move, and...You promised to give me half of it.Now what?The boss cannot keep her own promise?Hmm.I do most messenger work.More food for more work.These kids were abandoned and driven away by humans.I'm glad to see Kanjra get along with them.
```

### [93] hash=`b52ae08d240ec1ec`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
If she could enjoy life like this, you just reminded me of my mother.Sharjah, perhaps people like you are the key to saving all of us.I just observed it again.The figures are showing a grim picture.Luckily, I've worked out the specific range of damage.As long as we can get out of this radius, there will be no casualties.As for other losses, they are beyond my ability to cover.The airship of the Foundation is on the way.
```

### [94] hash=`36e0b6514e8412e3`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
At least our water supply is secured for now.But the problem is, such a distance.The distance.Even if we follow the straight line, it is impossible for us, for the elders and the children, to get out of it within hours.We are getting so close to success!We could go underground!Underground?Wait!I remember my old man told me about an emergency tunnel leading to the forest on the mountain.Its entrance is right here, beneath the floor of this very room.
```

