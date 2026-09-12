# 剧情图谱抽取 · batch 085

- 角色：`wu_ming_zhe`
- 批次：**85** / 共 1 批（每批 95 块）｜本批块数：**89**
- 筛选：标题含「1.7」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_085.jsonl`

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

### [0] hash=`5b2145838f1cc2a9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Hippocratic Oath, I will keep things between you and me.Everything will be a secret.Oursecret.Our secret.Klingt wunderbar.Ich erinnere mich an dieses Zimmer.Das Zimmer war übermäßig hell.Ich konnte mich nie an Glühbinnen gewöhnen.Und bevorzugte das sanftere Licht von Kerzen.Meine Mutter hatte immer eine weiße Kerzebrennen.Wenn sie mich beim Zubecken sah.Was ist mit dieser Kerze passiert?Jemand hat sie umgeworfen.
```

### [1] hash=`77cf0947ce8b6d3b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Ha!Das frische Balk.to give himself a ball.I will not make him famous.Only a debut leaves an impression.The following shows are boring repetitions.He laughed.Indeed, too many have made fun of him.Only through passionate fire would the world remember him.I said goodbye to himand went downstairsto talk to the ladies.Blood soaked the wooden floorand dripped into my cup.I went upstairs and found Teofil lying in a blood vessel.
```

### [2] hash=`7c1a5cf35679b676`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
A revolver was lying in his hand,as his cylinder clicked like music.I put on my dress so that the fire could roll down like water.I leaned over the hole in his left boot and said,Teofil, where is your fire?Teofil got up and said,Isolde, where is your weapon?My weapon?Take me now!I held the weapon the whole time!The Ophelion stood in the working room, the flames in the hut in the beams, the ceiling, everything!
```

### [3] hash=`71a81760d082ac50`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
He ran towards me, screaming in pain.He burned, the heat dried my eyes out.He stood in flames and ran towards me.Doctor, run towards me!Take a deep breath.Breathe out slowly.Everything's alright, Isolde.I'm here with you.You're safe.I heard a shot.I can't remember pulling the trigger.After the shot, it slipped out of my hand.I don't have the right to take part in the funeral or to hold a memorial service.
```

### [4] hash=`9953931c39b3c8c8`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
I don't deserve sympathy and kindness.I should have tied him up in the fire.I should have died.Everything is fine.I'm not a judge or a police officer, Isolde.I'm just your doctor.I will stay loyal to you, no matter what you think you are.Your life was in danger.Everyone would have done the same.It wasn't your fault, Isolde.You were just scared.Flipping out the unique talents of Arcanists and their artistic contributions would be like setting fire to the cultural tapestry of Viennese society.
```

### [5] hash=`e028aadc723cc6fe`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Oh, sorry, a flood.A flood is better.They consider it a desecration of the stage.When a singer is channeling, she's essentially asking a spirit to possess her and speak directly through her.Thus, she becomes the character in the opera.People will question the authenticity of the voice.Look at this city, this most enlightened, tolerant city.Under the sweet surface of the Sachertorte lies powder and poisonous vine.
```

### [6] hash=`fceb9e3255432508`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p50`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜8~11）

```text
Arcanists are recognized for their artistic abilities, nothing more.We hold no parliamentary seats, no professional titles, and no professional credentials.We are exiled and marginalized.From hysterical lunatics, street peddlers, and con artists, we need a new dream, a new saga.We need to reinvent ourselves and become a new people.No more repression, only the full embrace of our primal desires.That's why your work has not been in vain.

From Talefield's art exhibition to the promotion of new art...Do not doubt yourself.You're helping a great cause.
```

### [7] hash=`9939acaec1637505`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Reporter of New Free Press, editor-in-chief of the PAN, the founder of Die Fakl.Oh, that's Aegon Erwin Kish, the reporter who uncovered the scandals surrounding ColonelAlfred Riedel.I had investigated this before.Adolf Loos, the architect.He designed theSteiner House, as I recall.That's Major Maximilian Hohne and his wife.Who knewcelebrities like them would visit this exhibition.They look different from the pictures in the
```

### [8] hash=`594fbbf3fe60f7d5`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
papers.They were younger and less chubby.Has my memory failed me?Or is it becausephotography is also an art of beautification?Mr.Kahl was right.People are flockingto the secession building to get a glimpse of the new art.I can't appreciate these things at all.I've informed the field agent squad.AsSoon as Heinrich shows up, we'll get him under control.Ideally, we will take him away for a legal use of arcane skills.
```

### [9] hash=`abe285dbbb248f0a`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
It is the best reason and the least risk.It also complies with the laws of this time.If Menace Vindicte is behind all this, they will show themselves for sure.The squad will assist us with the perimeter by then.Marcus, your mission is to watch everything closely.Heinrich could be disguised and hiding in the crowd.Also, keep an eye on the manners and the rituals.That's what we were originally here for.
```

### [10] hash=`567ffc976ff33554`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Leave it to me.I won't be sitting.Mr.Thomas, the representative, is talking to the ladies about Expressionism.His parents did not foresee the success of Impressionism,the works that made no sense but became priceless on the market.That's why his generation overcorrects their aesthetic standardand pays compliments to any art they don't understand.The reporter for the New Free Press and that major are discussing the frequent suicides
```

### [11] hash=`b657381972cdf13e`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
in Vienna.They've written articles about it and many of them attribute it to the publication ofThe Sorrows of Young Weather.Tanya is describing the founding idea of this circle.This is the first magic circle drawn by the primitive men.Hmm, quite the strong woman.The military exercise in Bosnia and Herzegovina this spring.General Conrad Toulouse Power?A low-pressure trough on the Atlantic Ocean?Ivory-colored paper for official use only?
```

### [12] hash=`8ad405fbd38205a2`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
The General?Wife of a cabinet member?Court sand?Is Arcanum a bacterial infection?Is psychoanalysis a new type of mental illness?Mr.Heinrich is not here.Nothing useful on this page.Gold again.She's the host of the exhibition.She seems healthier than the last time we met.I don't know why, but I'm happy for her.She's about to make a speech.It is my honor to host this exhibition.Before we begin, I'd like to express my gratitude for Mr.
```

### [13] hash=`a05e6ef766be4204`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Heinrich,who is Theophilus' friend and the curator of this exhibition.Heinrich still hasn't shown up.Did he notice something?And also, a friend of mine, the founder of the Circle, Ms.Clara.Without her tireless worth behind the scenes, we wouldn't be here today.Born into a rising arcane family of the middle class, Ms.Clara is a devoted doctor and an art connoisseur with impeccable taste.Dr.Kakanya is standing up, greeting the guests.
```

### [14] hash=`8b88cc5446efa6d1`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Is this so?This is above my clearance.It seems like everyone in Vienna has their own interpretation of the island.Ladies and gentlemen, your attention please.We are forming a committee to petition the Empire to cease its attacks on the island.Please do not ignore what Miss Datta's Dwarf is saying.This is a proving ground for a world-ending experiment.A catastrophe is coming.The clouds of war are filling up the sky.
```

### [15] hash=`aba21f4970f91301`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Open your eyes and look at all we have now.The music, the art, the ambitions of progress.Man's gunfire will destroy them all.What are you all talking about?Not to worry, Doctor.You simply don't know yet.Follow me and I'll show you everything.Where your dream has taken a root.This is ridiculous.An independent kingdom?It is treason.We are Viennese.Why would we want to leave our own country?Are these golems worth about two?
```

### [16] hash=`99db1a25c42ebfe4`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
They look expensive.I'd like one in my collection.Open the door and let us go.This travesty is a disgrace.Are these golems immune to Arcanum?We can't get to Heinrich, but I'm Hoffman.I read them object enchantment strokes the same onesWe found at a foundation branch any signs of the man's ritualsNo, nothing yet Golems can only be broken from withinMarcus tell everyone the method Ola evacuate everyone and use the mute spell don't let more people hear about the error
```

### [17] hash=`747a209711417de9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Heinrich escape with his oldThere's an opening behind the painting after them nothing unexpectedIf the Emanation arrives, everything will be washed away, wars, disputes.Their number one priority is how to find salvation, once and for all.The fact is, we're going astray!The Emanation in 1999 had taken away almost all our outside contacts.Ever since the incident four years ago, we've been cut off from the outside world
```

### [18] hash=`b3ec2b94929b02fb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
and have become an isolated island in the emanation.And during these four years, no research on the emanation progressed.In the end, the theoretical study of its patterns was proven completely wrong.How long should we sit idly by?Until the humans take over our island?No matter who revealed our coordinates, be it the Foundation or Manus Vindicti,Someone should be held responsible.Thirty-seven is the one in charge of studying the emanation.
```

### [19] hash=`d982487535f57051`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Save your questions until after she wakes up.Six is treating her now.Also, talking about the decisions made four years ago is meaningless now.What's more, the Foundation is not hostile.They helped us minimize the damage from the reveal.Manus Vindicte has also given us constant material support since that difficult time four years ago.Ha!Thirty-seven.She's just a child, can't even handle her own business.
```

### [20] hash=`9f3e3efb7ec63710`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Ever since she brought outsiders to the Sacred Place, everything has changed.You know you're judging a child in a coma?Even if Thirty-seven did something wrong, she's certainly paying for it.Don't get angry.What 42 is trying to say is simple.Even if the emanation will take away the human army, when is it coming?Now that our model has failed, how can we be informed of the next emanation and actaccordingly?
```

### [21] hash=`e7880884eb4ac3ec`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
If pure theoretical research is doomed to failure, and if we must look outward, howcan we restore communication with the outside world?Do we stand with the Foundation, or with Manus Vindicte?210.Your words are provocation.Are you saying that we should stop being neutral and get involved in the endless faction disputes?This is against what Epiron stands for!I can't agree either.The truth is supposed to keep us off the Wheel of Birth, not on it.
```

### [22] hash=`263ee032790333ab`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
I was just interpreting what 42 had in mind.Moreover, we're already caught in the wheel of birth.Human weapons were undeniably dropped on our island before.The tragedies it caused and the thirst for justice will only keep us trapped in this cycle.But what caused this cycle to begin with?Brothers and sisters, you are blinded by the shrapnels of that conflict,and you're missing the essence.Listen to me and I will tell you.
```

### [23] hash=`eba36fff17434216`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Cut to the chase, 210.It seems you're the one blinded by your own rhetorics.Who can get me the stone clock on Six's seat?I'll clobber him myself.The original cause is the failure of our research on emanation.Our excellence comes from our beliefs.Once the truth fails us, the foundation that sets us apart from the world will also fail us.However, my people of great wisdom, forgive me for imagining a worst case for you.
```

### [24] hash=`7ace1473b7b8275c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
We believe the book of nature was written in the language of mathematics, and everynumber is a transcendental existence living in the kingdom of eternity.Math is the path to truth.The calculation of math patterns has led us to pursue the fundamental knowledge ofworld.The origin of Pneuma.But what if the supreme existence has no pattern at all?Whatif the air been tied of Pneuma is chaotic and irrational?
```

### [25] hash=`a334d6cb0ca2c90e`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
110, are you denying our beliefs?Are you saying the results we've achieved are justcoincidences?The fundamental theorems of ancient mathematics?The applications andimprovements from modern mathematics?The mathematical laws in atomic clocks?And leafAvoid sedition from a city, purge sickness from the body.They don't look like seagulls.Or am I mistaken?Are these all from the outside world?What's happening out there?
```

### [26] hash=`97e58c7cc8c39d54`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
A lovely day to rest at an outdoor cafe, isn't it, darling?Everyone working here is a capable server and knows how to address you properly with my lady.I'm here for one simple thing.Its culture and art held as their highest ideals.Its institutions believed they held the keys to paradise.They once believed that they were the lucky few.Blessed with the wisdom of a Golden Age,that's why they still linger here even after the smoke of war faded the glimmers of gold away.
```

### [27] hash=`a74bed64dc00815b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
It's not surprising to see Our Lady with them.See, she has to seek these well-hidden things and chirp along with the most overlooked voices.But I feel sorry for her, because she herself overlooks some of these teeny tiny thingssaid at her own expense.Words taken as jokes, ignored because her wishes and anticipation outweigh their sting.But while songs are floating in the wind, the clock keeps ticking.
```

### [28] hash=`dfce6edbb3dd3a43`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
People in the cafe talk about the secessionists and the newest plays in the same breath.No one cares about the rumors trafficked in the newspapers.They're only concerned with what is in front of their eyes.Still, the good doctor comes to share the pain of that melancholy lady,and then next to the cafe, to encourage the lower class to persevere.She says that every man is entitled to the same rights.
```

### [29] hash=`5603662d3be44227`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
She'll draw a circle around them all like the ring road,or the round mirrors in her clinic.The good times will come again, so say the coffee sippers.But you know, in the end, they'll be like the undissolved sugar at the bottom of the cup.My dear, your coffee is getting cold.Looking for a salt fountain to stop.I'm looking for a salt fountain to stop.You sure this will work?No time to complain, Doctor.
```

### [30] hash=`9f6cde1d313b788e`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
You should be very grateful that I'm helping you.This is an invisibility cloak from Bohemia.I did exactly what you told me to do, Doctor.Me?It was you who told me not to suppress myself any longer.It was you who told me that our society needs an operationand that we, Agnestins, need a new lifestyle.Isn't that also your dream?I just want to give you the truth of the world.Ich möchte dir nur deinen Traum zurückgeben.
```

### [31] hash=`d8e6604e720913f7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Burn these letters, Marcus.Destroy them in accordance with the Field Mission Manual Article 341,so that no one else can read them.Okay, Madame Hoffman.But shouldn't we reply to these messages from the Field Squad?Don't bother.The secret letters are sent to all active investigators above rank 4.The Squad is like the watchers of the critical points.They collect and record every event different to the ones in history and report to the foundation.
```

### [32] hash=`2cc4bc56b07ed682`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
These incidents will be the index for evaluating the stability of the current era.In other words, the more reports they send, the more unstable the era is.This keeps every field investigator up to date on the situation so they can plan theirnext move.In the past, we have seen too many tragedies caused by a lack of information.But now, our own task is more urgent.The Circle publicly committed treason.
```

### [33] hash=`0a9cc57afaea6d2c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Isolde and Heinrich disappeared.Kakanya became wanted.The Leopoldstadt riots and the march of the lower-class arcanists may be directly related to them.Heinrich and Isolde's speech is like the spark that ignited the powder cake that is Vienna.The riots have been going on for days.But why was Miss Kakanya wanted?She didn't act out of line in the exhibition and seemed totally unaware of the speech.All she had was the book which didn't belong to this era.
```

### [34] hash=`8e0ad1b686f1668e`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Clearly Heinrich didn't tell her a thing.It is because she is the known founder of the Circle, and a middle class with no background.This is good news for us, Markus.We can start with K'Kanya.They didn't protect her from being wanted, which means she has not been fully assimilated into this elite group of nobles.How typical of menace, Vindicte.We need to find her, fast.Luckily, the spider tail you put on her is reacting.
```

### [35] hash=`fbbfefc3d90ad224`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
You dirty, disgusting officials!For a kingdom of freedom!For a kingdom of freedom?Shoot, they're attacking the Foundation branch?Focus on what's important, Marcus.Someone's summoned a bunch of clitters on Keplerstraße.They're coming this way!Nothing unexp...Oh no.Wanna watch the aerial stockpile?We made this here!Don't blink!Something's wrong with this mist.Maybe the evaporation of the arcane potion.
```

### [36] hash=`c44ab2ede016b8a3`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Devil's shoestring charging by the smell for better diffusivity.Marcus, cover your mouth and nose, but enter the foundation's branch when it clears up.Marcus, are you okay?Did the mist get you?No.Madam Hoffman, the terrorists and the people in the march, what they shouted, for a kingdom of freedom.That's what Miss Dittestorf said in the exhibit, and she quoted that from Dr.Kakanya.And it was me.I told that to Dr.
```

### [37] hash=`226bebd3b911054c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Kakanya.I told her about the island.I told her it's a place of freedom for Arcanists.So, so, I'm the one who caused this turmoil, I told them the secret of the Golden Isleand caused the chain reaction.I didn't listen to you, I'm too reckless, I lack rational thinking I'm unstable andout of control and the one thing I can control.My arcane skill didn't help at all.You vouched for me and appointed me to the field mission from the headquarters
```

### [38] hash=`5f99991b422f88a4`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Maybe it is like what you said.Maybe you did play a role in this era, causing a butterfly effect in history, but tryingto be responsible for everything beyond one's capability is a symbol of irrational hubris.First of all, creating chaos in this chaotic time is more than easy.Just look at all the frequent ethnic conflicts, assassinations and espionage.Humans are more rational and arcanists are more emotional.
```

### [39] hash=`0a468b73dfd3092c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
They are sensitive to the darkness in the world so they can easily become absorbed in their own emotions and ignore reality.If we put a human child in the position of an arcanist who always takes on the world because of his uniqueness,who is never understood for his talents, maybe he too will become impulsive, sensitive, immature and unstable.And that's why it sometimes dawns on me that if we put an arcanist child in the position
```

### [40] hash=`8adcbe835171c81b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
of a human being who receives enough love, education, and positive feedback, these instabilitiesmight be controllable, at least enough to keep them from hurting themselves or others.Madam Hoffman?I took you away from the storm in 1912.Rational.But I've been doing my best to be rational as well.Even though I keep readingand practicing information analysis, I can't make a choice.What if I make a wrong choice?
```

### [41] hash=`b24ad0699c5583f7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
What if there's no right answer?What if I never told Kakanya about...Enough.You're getting carried away.There is nothing mysterious about rationality.It simply guides us out of confusion and straight to the essence of things.The essence?The reason why we're doing a job here is simple, Marcus.Our canists keep going to the menace.It's because they can promise a salvation while we can't.Therefore, decoding their immunity ritual against the storm is top priority.
```

### [42] hash=`4f4bf0f4545bdde5`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
If we can't, being isolated on a small piece of land,we're bound to meet our end in this temporal catastrophe.We're not the only investigators sent by the headquarters.Next, let's turn to where the train departed to find the source of everything.Rewind the clock to before the whistle blew, before the furnace ignited, and then, child,look somewhere far from here.In the Schönbrunn Palace, where the fine gentlemen of Austria-Hungary eagerly planned
```

### [43] hash=`eaf04c0671255bfb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
the extension of their national borders.But those war-starters, those who doodled their ambitions on maps while supping theirdessert would lose nothing in their gamble.The dew-fed river would still flow, and the facades of their great palaces would neverbe chipped or rocked by the guns they set off.Nothing stains their hands, save the cream from their cakes.Look at this painting, how chaotic it is.
```

### [44] hash=`e0a574911e7d0d3b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Look at the repression in the darkness.Look at the beasts in the people's heartsand the maggots under the golden surface.I listen to them as they listen to me.The shadowy echoes inside the skulls,the cacophonies of chaotic colours,the smudges on the canvas of rationalityand the filth in front of magnificent boulevards.They were excised, suppressed.The top paint scraped off and replaced with an empty, monotonous white.
```

### [45] hash=`994bdfb7e09ffa9c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Yet, in the end, they will be released to the fullest, to everything.Downstairs is such an explosion.You...Les left.He shone like a star in the end, just as he wished.But the rest of them, with their rocks and shattered windows, are still left to struggle.If only I could help them, just like how I helped Teofil.What do you mean you helped Teofil?You were not there!He ran at me, stuttering my name.
```

### [46] hash=`c18b70f9e4cb5fc6`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Every inch of his skin was ravaged by flame.So much pain, so much spectacle.Fighting you just like how you invited meLet's heal the world and save it togetherIs that miss Kikanya?Relax people miss Kikanya is on our side.She's helped us a lotWhat are you doing?A gentleman from America said we could do something big here.So I gathered everyoneWe will march down the Kertnerstrasse to the Vienna branch of the foundation
```

### [47] hash=`bcba0993a6f3f8fb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
Our slogan will be equal rights and freedom for our canists.How American is that?He seems to be quite a big shot with wads of cash in his pocket and reliable connections in the government.He said we no longer have to worry about the residence permit and the Arcanum license after this job.Aren't you coming with us, miss?This kind of activity is your favorite, isn't it?Hey, where are you going?Kakanya, you should be tried and punished.
```

### [48] hash=`60cbe71014473404`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
You gave your friends hope, prescribed them treatment, and vowed to stand by their side.But if it's realized in this way, it's the first nightmare imaginable for everyone.I said I would start the secession of the Arcanists, but what is the essence of thismovement?A rebirth?Or a complete betrayal?I'm just like my father, mother, and brother, who tried to shed the label of Arcanistsselling small wares as soon as they climbed up the social ladder.
```

### [49] hash=`b0f0f4d37ea87304`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p51`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜12~16）

```text
I am lost, so please, tell me.What should I do?You already know, don't you?I've been trying so hard to find you.I have something important to tell you.A catastrophe is about to sweep across the globe.But there are still things we can do.If it goes smoothly, perhaps we can save plenty of lives.
```

### [50] hash=`e07dd0a4394e36b8`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
The field agent squad cannot make it this time.They have a more urgent mission.But the Vienna branch already requested support from the army,even though we haven't told them what is happening.They are irritated by the blatant attack.We better use the power of the ERA now.Only one question remains.Is the source of this intel reliable, Markus?Are Isolde and Heinrich really playing in the premiere of Tosca?
```

### [51] hash=`97d9e493f7a81ebf`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
Yes, it may sound a bit absurd.Cavaradossi has been arrested for helping the fugitive Cesare Angelotti, former consul to the Roman Republic.To save her lover, Tosca turns to Scarpia, the chief of police.Scarpia has coveted Tosca for a long time, so he proposes that Cavaradossi will be freed if Tosca gives herself to him.Tosca submits to him, but when he tries to embrace her, Tosca stabs him in the heart with a dagger.
```

### [52] hash=`240cf68d1d163ded`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
For heaven's sake, how did you make that sound so balling?Will pretend to submit and request safe conducts for her and cover a dosy when scarpia signs the paperLa più breve che vita vecchia almost there almost thereHe's not acting that's real blood coming on the mr.Kahl's body the assassination in this story has become reality.Why is the show still on white?Why isn't the audience reacting?What the French stuff going on?
```

### [53] hash=`b8f2b1fe59de1310`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
It really is.Karl, no one...Are you all mad?A man has been killed, don't you see?You escaped from jail, didn't you?Jail only because you were too kind-hearted.I've been trying to clear your name.Harpia proposed an unfair deal.He wanted me as his mistress, but now he's dead, at last.The whole of Rome was overshadowed by his power.What are you talking about, Isolde?Not what the story is like.Have a road, Ossi.
```

### [54] hash=`b5dda584d90e6e1f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
I have the safer conduct.Go to the sacred kingdom of happiness and freedom,where no one knows us.Hardies of Potulac poisoned to death,Plasnyk shot dead,and Hurtnov assassinated,King of Greece assassinated,Archduke France assassinated,All these assassinations, at the same time, distorting, like those paintings, is also some kind of mass hysteria, or...They've grown on my eyes.Don't mind me.Vesto e il bacio de tosca!
```

### [55] hash=`208fe4959298cf3f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
Come, friends, Keith and Keen, take your daggers and get up there!We will all kill our own scarpia!Those so-called upper-class people don't deserve the best seats.I feel the blood splashing on my face.There's no doubt this is art.The way that reality plays a fantasy.I've never seen a show like this before.Zilla!Wolf!What happened?Have you got blood on your face or two?Is this part of the show, or...
```

### [56] hash=`a6dbb67248807ad1`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
They're killing each other in a frenzy!Is no one noticing this?An emergency here!I...No!I can't hear anything!Let me leave!I need to make way myself!Quiet!Be quiet!Go to hell, you terrorists!I need to...I need to disperse them!At least open up the exit!Marcus, what are you doing?I said evacuate!But people are dying!It is our duty to I just got a message from the headquartersThe timekeeper has issued a 24-hour storm warning
```

### [57] hash=`50b2eb3cd08a5e6c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
The man is has carried out several assassinations on the same day the instability of this error has reached the critical pointWhich means the storm is coming.It was me.It was meIt was me who started the chain reaction.It was me who leaked out the detail of the island.It was meGet a hold of yourself MarcusYou are my only friend and the one I cherish most in the whole world.What have I done wrong?You forgive me!
```

### [58] hash=`abe2c3b3284c03eb`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
Because I'm too stupid.Stand your words.Because I'm also sick.The incurable tumor.If that's the case, please help me.Hold my hands.Touch my face.Hug me.Let me hug to hug like you used to.Doctor...I saw myself in this dream of yours,like I was looking in a mirror.It was poor when we had this conversation.It was the first time in my lifethat I saw the sun.Your dream filled my empty life with meaning.
```

### [59] hash=`da7ce733bc23bca2`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
You saved me from it.Just a curse to be trapped.That was a wonderful dream.So beautifulthat I forgothow ugly I amI never thought she would commit a crime over my words.Crime?You mean what I'm doing right now?You don't like it.The Foundation knows all the truths.Yet they won't tell us anything.That's why we have to release everything they repress.The noose, the barrier, the riots, the chaos?That's what Manus Vindictae told me.
```

### [60] hash=`256f03a69a6e398f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
Is this not like your dream?Did I misunderstand?What in the world did they tell you?They told me the method of salvation, Doctor.They gave me the opportunity to save your loved ones.The world, and your dream.Welcome, Angelotti, and unknown lady from the Foundation.You have such a kind heart, Doctor.Yet you don't know the truth.How are you going to bear the pain when you do?Theophilus set himself on fire.
```

### [61] hash=`f9441a83190239fe`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
Ben hung himself to death.Emmanuel laid himself on the railroad tracks.Are these the suicide cases in Vienna?They all came into contact with Samanus?Hear them!There will be bullets, helmets, scores.You haven't kind of told me.How I wish it were a farce.A farce that claimed the lives of more than 10 million people.A farce that dozens of leaders decided to take part in.Ben, a dear friend of mine.He played the best Fantasia in A minor ever.
```

### [62] hash=`a3f650700ae4beb9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p52`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜17~20）

```text
But came back from the battlefield, missing an arm and a leg.And Emmanuel.His hands were born to write poetry, but he was sent to the front and dug trenches until he died of disease.Our hands are meant to hold paintbrushes, play pianos, and write stories.But they end up in gunfire because you narrow-minded hypocrites keep inciting them to violence.We've already suffered for our gifts.Now we have to watch our talented friends sacrifice themselves for man's childish tantrums.

Ladies, you know all of this.Yet you call us terrorists?Real terrorists are you, humans.Sie haben diesen Krieg begonnen!
```

### [63] hash=`d32af6f036fada0f`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Fortunately, the Guiding One has heard our cries and promised us salvation.The storm will put a stop to this frenetic melody before all of the good,artistic, heartfelt things in life are destroyed before our eyes.It will wash away the unwanted, the unimportant.The creators of this chaos will be severely punished.It's still a little early for what Mr.Forget-Me-Not has planned,but the actors and actresses are in place.
```

### [64] hash=`6d224297f23cde30`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Sadly, you won't be fine for long.Mr.Forget-Me-Not is one of the best potion makers.The formula is carefully designed to prolong your suffering, until sweet death finallyspreads its wings over you.But resent not, your pain is fleeting compared to what my people were made to endure.As for you, Miss Angelotti, a choice lies before you.You have been lied to.Humans have whispered lies through their petty, made-up history.
```

### [65] hash=`d6d675aadcd030fa`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
There has been genocide, the lengthy, vicious kind, under the banner of high-minded reason.They tried to split the world in two, so that the progressives cannot be stopped by the non-progressives,so that the irrational cannot speak against the rational.When they do, death and destruction follow.You're one of us.Right Marcus, this is the missing part of history that they didn't let you go throughHoffman kept everything from you.
```

### [66] hash=`c3c5dabdf3ff22c1`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Didn't she?She's a liarYou're here because you want to find the truth.You don't have to work for a human institutionPick it up drive it into your mentors heartShow us your resolve an opportunity has arisenTake it a chance to learn who you really arewhere you came from and why you were abandoned.Very good Angelotti, before the High One of Midnight sheds merciful tears and washesaway the sins of man, pass the test and join us, and we will take you through the storm
```

### [67] hash=`7663e7209674336e`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
back to our era.My era has already come, 1914, the year you once wiped out with this storm is myera.Huh?I waited in the abandoned lighthouse of that island.I waited in the marble house of the Foundation, watching the time go back to 1966, to 1929, and finally, back here.You say this is salvation, but you're just replacing one annihilation with another.The Foundation wants to stop the destruction, but you're speeding it up.
```

### [68] hash=`e53000d2681018ee`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
You don't care about this era, nor the people living in it.You abandoned them, who hide in your empty kingdom, in your garden that doesn't yet exist with your, with your art, your poems and your pianos.And me, I just wanted to go home.Why would you take away even that?Marcus, don't lose control of yourself.Here!Here with me, Doctor.Let the rain wash away the old world, so we can build your dream in a new one.
```

### [69] hash=`40eec318a0f90cb7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
I thought we were on the same side of liberating our oppression, giving freedom to the Arcanists.I never thought that you would take people's lives, Isolde.Is this why you hesitate?Because I killed a person who shouldn't be killed?A person from the Foundation?After you befriended the young lady?I will take Heinrich's life, for that would make it fair.Please, come with me and witness my commitment, Doctor.
```

### [70] hash=`ad97b875789a02f7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Did you say you're going to kill who?Miss Angelotti, if you still don't see the big picture after returning to your true self, you are not one of us.Enjoy the sifting before the storm.Ah, Isolde, you're just in time.Kanya's decision is the key to victory.I can't let the clues end here.This is the Vyce's decision.Is Heinrich still alive?Should have been faster.Protect you from his old.She won't side with Manus from what I see.
```

### [71] hash=`b72676055072740b`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Give him my place in the storm shelter.Her arcane powers will be useful to us.So the both of you can evacuate safely.I know what I'm doing.I've taken back my senses before I die.The pain never ceases.To die with my sanity and rationality still intact, it has been an honor.Can you give her first aid and take her to the station?You'll meet the Foundation there, they'll have better equipment, they'll know what to do.
```

### [72] hash=`d0c72692e78b5d9c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Henrik is dead, but there must still be clues on him.This isn't over yet, I have to finish the mission.Marcus takes us.The number of that orphanage in Romania, I've had it with me for a while now.Please save your strength, madam.This isn't what we need to worry about.We don't have anything else to worry about.The mission is over.Silly child.Bring home before the storm comes.The future is yours.There must be something I can do.
```

### [73] hash=`1ad85ec2240c1b6c`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Everything is a book.Everything can be read.The most immediate threat to her life is that potion.Devil's shoestring, Belladonna, Narcissus, Nezetta roots, and the fruits and roots ofthe Picrasma tree.It's the formula made by Forget-Me-Not.The Picrasma extract makes up more than 50% of the potion.This is very different from Laplace's formula.Arcanist potions seem to be a concoction of instincts and information.
```

### [74] hash=`5e520b99d51f8604`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
And there's nothing else I can do?The Picresma Extract is not a poison in itself, just that humans cannot...There must be a way, madam!Please!Jason...Don't give up.Keep reading.I will find a way.Marcus.No.Every book has an end, Marcus.There's nothing more on a finished page.No matter how reluctant you are to flip that page and get to the end,you will move on to a new chapter.No, no, no!For all the pain I had to put on you.
```

### [75] hash=`25d0d5922870b44d`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
I hate you!An incredible woman, her suffering ends here.Doctor, have you decided?I must leave, but I will wait for your answer.Huffman was calm till the end.Why?Was she not afraid?No, I just read her fear through her trembling fingers,but she would not show it.She knew it would have frightened meRepeat this is the 24-hour countdown to the storm all personnel must return to the headquartersRepeat this is the 24-hour countdown to the storm.
```

### [76] hash=`a509e6b4f398d0ef`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
This is Semmelweis.You must leave now.Last callYou know, we won't wait if you miss it.The storm is coming doctorCome with me to the headquartersYou can take Madame Hoffman's place in the shelterIt's a shame, so if we won't get to be colleagues.Der Suche nach Silenus.Did Theophil write the poem in the same misery and despair?Then why did he call the painting The Salvation?He set fire to every piece of his work, but he didn't leave this one out.
```

### [77] hash=`b644d4898f09f8af`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
And this strange way of drawing.Rick said he showed the path to salvation and brought you all to the guiding wall.Salvation.Dutpi, if I succeed, I can prevent the death of someone who holds the clues.Even if I die, I'll still turn Kakanya completely against Isolde.This was your plan, madam?What really scared me was not the threat to my life,but the possibility of dying ignorant.I know what to do now.
```

### [78] hash=`d3e1355fa8a69564`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
There might be another way.Don't fall into darkness.Don't let madness or despair take over, Doctor.This is not the end.My mission is not over.There's still another way to end this.But it can only be done by you and me.The Guiding One is merciful in bringing this era to an end before the summer of 1914.Here, the nationalists, the internationalists, the arcanists, the rationalists, the progressives,
```

### [79] hash=`e2c15be7befaf4b1`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
the conservatives, the fanatics, the bystanders.They indulge in passion, insisting that it is their ideals that make up the world.Who would have thought that such a progressive and sensible era would end in a barbaricI want to look at this city one last time.Whatever you want.I've thought about this and made up my mind, Isolde.You were right.I will join you.I have been waiting to hear this for so, so long.
```

### [80] hash=`93da9c4686d31863`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
I know this is what you want.Now I can finally make your dream come true.I...Before we leave, I would like to take von Lastfork in this world.Would you like to join me and walk to my clinic?And the other one wanted to scratch off the color from above,reveal its true colors and re-form them.That's you, Isolde.You tried to scratch off despair and re-form the world with your compassionate, compassionate hands.
```

### [81] hash=`c7c3c9830ee41098`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
He created the art, and you completed it.You and your brother have been the co-painters of this painting,as compassion for this world.Look at this painting!Look at this mirror, Isolde!What did the leader of Manus Vindicte show you?What is the way to salvation?Is it a spell?A ritual?You're the only one who knows!Watch the mirrors, Miss Marcus.I'll guide this old to the memory.If only this would undo my mistakes.
```

### [82] hash=`110353bb179980be`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
You can do this, Miss Kakanya.I can't see you.Where are you?Don't leave me, Doctor!Close your eyes.Tell me what you think of the rescue.She's talking to her sister who died young.Where are you now, Isolde?Somewhere special.An ordinary party.A seance.Wunderer, Schmeichler, immer da, bei jedem Treffen, diese naive kleine Tosca, sie vertrauteihren süßen Worten, sie erzählte ihnen eine andere Geschichte, Vorhänge im Wind, das
```

### [83] hash=`d976d7be94937f92`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
warme Wartnir-Sonne.Was passierte als nächstes?Schließ es!Another side?The buttons.The moment of silence.Face.The present.Benefit from reading.Till the torch is lit.Here.Fine.Benefit from reading.Right with me.Speak of truth.Wanna watch the aerial stunts?In the moment of silence, the scale of your soul has tilted.The balance needs to be restored.Hit from reading.Wanna watch the Ariel's dance?Do you know this part?
```

### [84] hash=`98631798d6fbd878`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
I thought so.Kakanya!I'm fine.Go on, Isolde.From one point, the brush drew a circle.The portrait began with this stupid circle.It drew eyes and a mouth.And then the circle became the circle.Unheil, Gebar Unheil.Kunst.Eine faszinierende Krankheit.Verlangen, Unterdrückung und Wahnsinn.Alles wird durch Kunst ausgelebt.Es ist die Rettung!Wir kommen näher!Nein, nein!Er malt es falsch!Du malt es falsch!
```

### [85] hash=`24aae25ba92b3eb7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
Til the torch is lit.Wanna watch the aerial stunts?The maid's flicker.The moment of silence.Don't blink.Benefit from reading.Sister Narka's yet.For Adosie.He's too good on her.The victory's here.I should excuse myself.Stop using the mirror.You will both collapse if you continue to force her.I'm running out of options.I have to hypnotize her.You, Miss Clara.The doctor who resents hypnosisand had even thought to do it to stop it.
```

### [86] hash=`3226593a910f05d7`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
You are going to use it on me?Why?Because I'm a hysterical, irrational woman?The wicked witch, the cursed, inconsolable arcanist?Why?Why are you like this to me?Please calm yourself, Isolde,and fix your eyes on this watch.Did I do something wrong again?Am I hopelessly incurable?Why, why couldn't you cure me?Save me from despair one more time.Sleep, Isolde.Go to the place of peace.To the home of the night.
```

### [87] hash=`95d0bfcd2c5d4ca9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
The most cruel of all.If you have already made a decisionand you think that I am guilty,why do you treat me like sand?If this is the solution that you brought, I will take it with pleasure.The sky is black and the stars are more beautiful.Isolde, what do you think of when you look at this painting?I am intrigued by the name of your little group, The Circle.Yes.Unlike other animals, there's a power in every one of us.
```

### [88] hash=`765d7672efd73ba9`

- lang：`en`｜version：`1.7`｜arc：`—`
- doc：`BV1eo4y1u7aW_p53`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.7-主线】第六章.今夜星光灿烂｜21~24）

```text
It's the source of ourinstinct.Following it, man survives the cruelty of nature.In awe of thisextraordinary power, the first of man will do a magical circle on the ground,symbolizing a higher power and declaring that man would no longer be at thepromised land heard it i read the storm immunity ritual we did it finally news from the front linethey have sent home the storm immunity ritual get to work people

in the 22 hours before the storm arrives the whole world is our proving ground
```

