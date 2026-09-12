# 剧情图谱抽取 · batch 076

- 角色：`wu_ming_zhe`
- 批次：**76** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.3」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_076.jsonl`

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

### [0] hash=`124565b28bf7d741`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
A tunnel?He told me this, hoping that one day I will take over his responsibility to look after the village.If I remember it correctly, that forest, which is also the exit of this tunnel, is right outside the impact area.That's great.In the tunnel, even if we don't make it to the forest in time, we can still avoid the damage.But, the problem is there's a gate to the tunnel.Now, just for the record, I'm only quoting my old man.
```

### [1] hash=`e33ceb6f98bdd945`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
It is a gate which only opens to the leader who has earned his people's trust.V is going real treasure hunting this time.Oh, well, my father's version was hardly as exciting as open sesame.I didn't believe him even as a child.I tried to open it by force many times.Well, it never worked.My old man was telling the truth.Things would be problematic for us, because I don't think I can get that gate open.
```

### [2] hash=`f61a98608f55320c`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
Firstly, I've never wanted to be a leader.And speaking of the people's trust,how do you think those cursing old men in the yard will feel about me?hmm even so we will open that gate even if we have to smash it with our barefists I'm not sure if you were being sarcastic it's the best way in thecurrent situation watch your stepsShermaine told us it's truly uselesswhat did I say this is never the gate for me to open
```

### [3] hash=`0c3876ebe88067e4`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
I knew that you would kill us all.Stupid boy.If you can't protect your family,then how will you protect others?Oh god, please listen to our prayersand send us a martyr.With the trust of humans,we have...Me a brick?And you?Me?What about me?King don't you now you go dumb can't defend yourself.I just don't understand youand you say why is you afraid can you shut them up in thing story only themost smart and wise people can open it why do you hesitate now little one you
```

### [4] hash=`05c9adca1d3eb89f`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
think I'm the smartest and wisest person no but why ask me it is yourMy answer don't matter.Their answer don't matter too.I said you should shut them up.There will be a gate for me and I will open it my way.I am the one to decide how to open my gate.My spell will be longer and cooler than some open sesame.Not jealous you.Ha ha.Ha ha ha.Interesting.Looks like dad was right.I am not qualified to be a leader.
```

### [5] hash=`5601b9312d7984e4`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
Thanks, kid.Anyway, times have changed.Forget the spell.But this is me, wherever I am.Not that.Screw it.I have no idea what my father once promised you.In fact, I have no interest in what your old heads think.But what is my way of opening the door?And the one standing right here, right now, is me.Not another Sharma.That is to say...Turns out the gate is much more fragile than I thought.I'll smash that door open, even if it takes the other arm of mine.
```

### [6] hash=`f334b347336eda76`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
That's what I'm talking about!So cool!I guess you didn't see that coming.To tell the truth, I had prepared myself to bounce off from that closed gate,like what had happened many times when I was a kid.See how I burst it open?That was cool!So in the end, my dad was just telling nonsense to a kid.Those so-called profound teachings, like one needs adequate strength, or a sense of responsibility.Those were too abstract for a kid to understand.
```

### [7] hash=`bc8f330280ed8299`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
That's indeed his style.But in the end, the door was opened.That's for sure.That's a good ending for a story.At least a million times better than mine.You have a long way to go before reaching the end, but I'd say you're in a much better place now than you were in the beginning.It's good progress, trust me.He who only stays behind a closed door will turn away many things, including a chance to survive.
```

### [8] hash=`0b645262246961db`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
Alright, alright!Rose rabbit ever!Mr.Ja, you have the first bite?A person with no family, yet radiates the warmth of family to others.Only Kumar had the slightest warmth from someone.Maybe such an absurd thing would have never happened.I doubt she's upset about what happened.Maybe she has found herself a good seat to enjoy this dance of Shiva.That's true.She's the kind of person who always finds herself the best seat to watch the show.
```

### [9] hash=`81f32ad12431d19c`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p13`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（13.芝麻开门）

```text
But I'm curious.Tell me, did she...was not a part of a conversation.She just admitted that she was being vindictive.MaybeI was being vindictive out of hatred.Like you said.The realm can never extractevery word I've said.It's theoretically impossible.Where, where did she hear that part?
```

### [10] hash=`3c9654b40f1df186`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p14`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（14.无星之地）

```text
She was in the same room?How could it be?I know that room well.We have searched every inch of it, unless she was hanging on theceiling right above us.But as I said, she always finds herself the best seat.To be someone who can smile knowinglyat the argument made by the lecturer, knowing full well the thinking process behind, whileStaying close to other whispering opinions, like a perfect observatory, from which we
```

### [11] hash=`41f8bac1bd864007`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p14`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（14.无星之地）

```text
witness the events in the universe.Maybe I've been in the wrong direction.She didn't make the star fall as revenge on the village.Mr.Shermain, she was not on the ceiling.Are you taking me seriously?That was just a joke to lighten up the mood.But under the ground.Remember the underground survival guide where we found this photo?She's right under that house.First to the corner.It's crazy.It has gone beyond my imagination.
```

### [12] hash=`a7e7354fdb1381a0`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p14`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（14.无星之地）

```text
Sorry, but you don't have to come with me.If you don't let me see my own sister,I will be dying for answers.Who would dig a basement here?That reminds me.How curious Dee is when it fell.Well, the major reason she did that.It's possible that she was well prepared last time she came back to Morpah.I never thought she foresaw that we would be kicked out from the project.And as you just deduced, she did so to see that star?
```

### [13] hash=`596bf87d169ccd9e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p14`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（14.无星之地）

```text
Almost 100% sure.Without me, she must have asked the Manus to support her with arcane skills.I knew it was extremely mentally unstable when she left me.It wouldn't take any effort if the Manus had the intention to recruit her.Watching the meteor shower and being destroyed by it has been our plan all along.At this point, it is hard to say who's worse, she or we, since we have prepared to diewith her evil plan.
```

### [14] hash=`1f8b4ded34de2af6`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p14`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（14.无星之地）

```text
However reluctant I am to admit this, sometimes Arcanus are indeed strange creatures.It's like a madhouse party.But what did you teach Matilda before we left?That's the only chance to survive in her realm.I came up with it when I was calculating the range of the fallen star damage.As I said, you are the tiger cub, trying to take a bite in the arm, even when the hunterhas had you in her grip.That matter was between Kumar and me.
```

### [15] hash=`1e75080dd87f2229`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p14`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（14.无星之地）

```text
There is another theory according to my calculation.If there are more observers, the realm might collapse.It's the only theory Kumar does know.At the same time, it is not yet strictly verified, but I have faith in that girl.She's indeed a genius.I hope it's not too late to make our last attempt.If you ask me, it's not yet the time to make that attempt.Ha ha!This must be the appetizer she served us!

Great Shiva, I hope your fists feel as light and crispy as pani puri when they landon my body.Look over there.It is...empty down there.
```

### [16] hash=`e187146ee7f67ff2`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p15`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（15.博识者美餐）

```text
The showers estimated to fall at 4 a.m.today by then the comet will alsoThree and a half hours to go.OhAlmost forgot about thisMusic you're right.It's not too high forMe happen to you.OhWell, I didn't expect so many visitors, but since you're here, pleaseTake a seat, I built this place by myself, it's not a big room, and not soundproof.I heard you very clearly under the ground, when you searched the room and went through
```

### [17] hash=`3329346182fbfc98`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p15`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（15.博识者美餐）

```text
my stuff.What's wrong about an astronomer reading, calf-feeding and management?You should have left, the plan has changed.Let it be.What did they call this?Destiny?You know about destiny, right, Calaborna?Watching the stars with me?Good.It's like living the old days again.What better in the realm?What did the Manus do to you?The Manus?Oh, they're fine.Helps me a lot.Impressive arcane skills, experiment apparatus, and food.
```

### [18] hash=`d7b130281bfb1f23`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p15`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（15.博识者美餐）

```text
Lots of food.Seems like she's no longer capable of commanding those wandering madness.The priority is to stop that star.We can deal with the rest.The star?You're going to stop the comet?You are taking it from me?Again?I will never!I will never let anyone sit their hands on it!
```

### [19] hash=`0a1538943ba9fb41`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
I'm going to throw up.It feels strange in here.Was that Master's face?It's hard to get used to it for the first time.I feel a lot better in here.I'm sorry, Calabona.I don't think this body of mine can hold any longerfor more appropriate meeting in the real world.I'm glad you came back for me.What I said was indeed too harsh.Why do you have to?Price is too high.In the first instance, I did have other intentions.
```

### [20] hash=`ff093f0792e6d209`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
I kept imagining how my so-called parents would react when they were about to get crushed to pieces by the star.Little did I know, they have already paid for what they've done.I worked myself to the bone, but who knew I would lose everything, including my purpose.It really sucks, but it's okay.Just a minor setback compared to what I've been through.It's not even worth mentioning.That's why I changed my mind.
```

### [21] hash=`2237b0e893667f20`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
I want to see it.To see it.The star we can't see with our eyes.Seems like I was not very careful about my wording when my mind was clouded.It is a celestial body, Calabona.Not a star.It could even be a moving black hole.I'd rather you did this out of the hatred towards the people who abandoned you, or eventowards me.For I carelessly exposed my identity as an Arcanist, and thus you lost your home.I wish the same.
```

### [22] hash=`179eba4c93943f70`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
I wish so badly that I could just be filled with pure hatred towards someone, but Ican't, kid.You're the lucky one young brother.I was going to kick your butt in our last encounter, but I just couldn't do itKid Banner University can get my names on the SCI listBut the mannus allows me to touch the universeThey are not that different to meSister mother told me about this you physically can't take such a great amount of Arcanum in you
```

### [23] hash=`d84f56401e8c40a8`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
The men should also know this.I appreciate that they remembered this about me.But this is the path I chose.When I look into the sky,I feel myself the freest being in the world.The universe.What a vast, life-embracing place it is.No matter if you're a canist or a human.Even a grain of sand,it encompassed everything.But I was driven away from studying it, abandoned by my own family, for some insignificant, unimportant
```

### [24] hash=`ee26808b80b50b85`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
reasons.I should have understood this earlier.My struggle means nothing on this planet, Calabona.Just want to see that celestial body with my own eyes.That's not how you look at a star.The telescope shouldn't be placed in a basement, and you shouldn't lower your head.How long has it been since the last time you looked up at the night sky, at the other stars?What's more, if the star falls, people in the village, including those kids, none of
```

### [25] hash=`a7f325dae9cfd00d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
them will survive.The madness you summoned here has brought disaster to this place, to the peopleand their families.They are not the sacrifices of your wish.Stop heading down the wrong path, Komar.You know what?I don't care about them.Just like they've never cared about me, haven't they?Sorry.Please indulge me with one last willful act.This is the path I chose.And you can't stop me, Calabona.It's Matilda!
```

### [26] hash=`3ed27e4ca64dd1ff`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
They made it!Quickly!You understand?Yes!That's what Miss Calabona taught me to do!But I can't see anything when my eyes are closed.Don't rely on the eyes.Hold this crystal and take a deep breath.To feel, um, what she said?The change of the universe.Meteor shower is starting earlier.What did you do?That's the matter I'd only once known between you and me, Kumar.The observation method.You told others about the celestial egg?
```

### [27] hash=`87ba7cb6c6214acb`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
So what?I see.You once pitched that research proposal to me.You are indeed my best student, Calabona.I finally understand why you asked me to keep it a secret.Even if we named it Egg, it's actually a projection of the universe which has the samefeature.The universe is infinite.As long as we observe it self-consciously,Think each of ourselves as one of the centers of the universe.The egg will then collapse because of multiple centers, until it puts a quietus in everything,
```

### [28] hash=`9e34dcba0f5400c9`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
including that star.A shattered mirror will never be pieced together again if there are enough forces to breakit.Am I right?Then, there was neither existence, nor non-existence.There was neither the realm of space, nor the sky beyond.Who could master these skills?Those old fogies in the village?A genius girl and a bunch of kids who looked up at the stars.I'm sorry, Kumar.I have toNo, we have to stop you this time.
```

### [29] hash=`1e7a7346f530cbba`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
I can't let you destroy more punk or destroy yourselfThe unfortunate is the first, but irreversible.Either do it quickly or hold her off.The realm will collapse once the observation starts.and I believe in it.Don't rush it.She seems to be waiting as well.She's accumulating power.As the nebula collapses,no watching eyes will survive the destruction.But you should remember,it's not ours that our observation belongs to.
```

### [30] hash=`79e049dab8e2a6b9`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p16`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（16.新观星者们.）

```text
To others, our method to see that star.You have really ruined everything this time.How dare you!I didn't take advantage of you.You and I,We are very alike.Why are you treating me this way?I wanted to see that star.Why did you stop me?Why?We wouldn't have to waste time on this, right?I'll still leave the research data behind so that you can make it yours.Wanna watch the aerial stunts?Time.Handle it gently.

Right wind!You can push it a little further.I've lost everything.I, I don't understand.
```

### [31] hash=`95152bc7ef67cb6e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p17`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（17.无昼无夜）

```text
It's about to collapse!Got to go now!Kumar!Jermain, you covered me.I'm fine.Taking that falling star with it,tonight only the meteor shower will sparkle in the sky.Kumar, how about we go back to the institution?To the university?There's no place I can go back to.Yes, there is.You can stay at my place.You can use my lab.we can start oversurereally?you will?let's go thenleave this place firstbut there are some papers
```

### [32] hash=`9f1822005b01a494`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p17`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（17.无昼无夜）

```text
I need to take with melet go of my armMr SharmaKumar says she'll come with usshe just needs to take some papersit won't take longand there was neither deathnor immortalitythere was neither daynor nighteveryone has a place to go back toWhat a nice world to live in.When the universe constructs me for a second time, I will not come to this world again.So this is what Chandigarh look like.It's slay!This way!
```

### [33] hash=`d2a74a0e9ca5f52f`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p17`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（17.无昼无夜）

```text
Come over here!Ah!So you're only an assistant?No wonder they made you go through so many procedures earlier.Just Milky?You be careful, otherwise you will regret your doings when you get to the foundation.I think it's not a good time for her.They will be back after the meteor shower.I wish I can have my stomach full every day when I go to school.Yes, my twin did take tea even though he's a good boy and a fool.

Alright people, don't be greedy.One wish only.
```

### [34] hash=`bffdaf33d715e642`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p18`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（【晃铃响于山谷】1至3）

```text
To the higher place?All the poisoned arrows, deadly traps, and the fierce animals.This face even looks welcoming to me, my friend.Wise to wade this river.Seems like I'm not welcome here either.Just walk it off while you still can.Nothing to complain about.Seems like you've been feasting in the past years.I wonder what your teeth can do to the stones,if they couldn't even break up human bones?Um...
```

### [35] hash=`d8fd1e21df266d0c`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p18`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（【晃铃响于山谷】1至3）

```text
this again, fall for this again.I will stand here and watch you burn to ashes.Kill you dumbass!I have no idea.Don't need you here.We're no longer a shaman.Take your hats off me.Your mother and I, the entire family, have invested years in your education.Yet you have let us down.I can give everything back to you as long as everyone gets out of this placeWhite elephant will look after your soul now.You see me as your sister
```

### [36] hash=`61984be43e7175da`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p18`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（【晃铃响于山谷】1至3）

```text
I remember you were this tall don't look at me like that do this little make a dealGive me a hand friends.I can't do this alone cut your warm belly open before you pierce my neck with those teethAnd suck up my blood
```

### [37] hash=`637bffce6f24616c`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p19`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（【晃铃响于山谷】4至6）

```text
your part dutifully what happened when we first met you nearly blinded one ofmy eyes let me see into the wrong place hey little fella what are you doing herestay there don't move enough now that's enough my friends sit sit a feast hasbeen given to us fuck with you mother nature
```

### [38] hash=`6871ca605215a98a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
oh just in time is this yours yes put it away kid this shine only few touristsare willing to only the locals know they have something to do with thatcomet myth I had about some mythologies are the original translation of therealm that's how we located the star it reaches level five on Torino scaleMeet your shower.So many of them as the news mentioned.This Deepa festival will become a disaster.It's all because of my sister who I've only seen once in my life.
```

### [39] hash=`3f8fc86d44373f9d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
It's also my teacher.M-Miss Shajah?Why?How do you find this place?My dear children, enjoy your Deepa festival.So meet your shower.I'll smash that door open, even if it takes the other arm of mine.When did you last look up at the sky?Not how you look at the stone.You should have lowered your head.Hypotheses have been made regarding the quasars as follows.The darkness below the podium is boiling.The eyes were the questions in inspection.
```

### [40] hash=`b492d9be3d511cc2`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
Some behind glasses are cast out of the darkness.Just like the signals beamed from several light years away and received at the top of the observatory.Based on the data of its redshift, Dr.Schmidt deducted that it is moving away from us at a recessional velocity of 1 sixth of flight speed.Page three.Mmm.Put it in.In most cases, we would consider a stellar black hole as what is left from the gravitational collapse of a star.
```

### [41] hash=`e87645b8e1f7bc66`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
They fight, attract each other, and merge into a supermassive black hole, to which the starsin the nearby galaxies will be eventually pulled by gravity.Page 3, here it is.And there was neither existence, nor non-existence.There was neither the realm of space, nor the sky beyond.Then, there was neither death, nor immortality.There is neither day nor night.Inside the Quasars, there is a violent activity occurring that is close to a supernova.
```

### [42] hash=`87ae0ad9cc2cf39c`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
It devours stars, and the gas cloud turns into stars out of gravitational driving.Thus, a new star is born.It is a graveyard filled with corpses, as well as a cradle for new stars.That was a successful lecture, Calabouna.Thanks for your rare compliment.I can't believe the first thing you do after the long absenceis listening to my embarrassing speech.You see, this is not my thing.I'm still struggling with the word I should use in part three.
```

### [43] hash=`c8da6a14b1b2da73`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
Oh, but you know I won't pass up a good chance to sit in the audience?To be someone who can smile knowingly at the argument made by the lecturer,Knowing full well the thinking process behind, while staying close to other whispering opinions.This is the perfect spot for observations, like a perfect observatory from which we witness the events in the universe.I'd rather not give a comment on your personal taste.
```

### [44] hash=`655830173b239030`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
Kumar, I think we should make some adjustments to the details of the following observation.He's an idea.How about we put away the work for the moment?Forget those things.Just look at the stars.Simply fix your eyes on them.Move over.The grass beneath me feels like pine needles.Donnie from the institution had paid a visit here.Based on his attitude, I may tell he was doubting my identity as a human.
```

### [45] hash=`599e770d3c0bb5a9`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
If it goes on like this, we are likely to be kicked out of our own project.I've destroyed all the observation data of that special celestial body.At least through this we can keep the observation method between you and me.Does seem...have I done anything wrong?No.As a research student, you did an excellent job, though no more than I'd expect froma student of mine.That's just what we've been doing, isn't it?
```

### [46] hash=`b2b7b119055fcfde`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
Hiding in the corners?doing research that completely has nothing to do with others.You know what?I'm a bit tired.Seriously.Tired of the pointless power struggles between these specks of stardust.We all know none of us could avoid the fateof being restored to the basic elements of the universe after we die.Never mind.It's not the first time it's happened.I've never been welcomed on either side.Speaking of which, my parents, yeah I told you about them, they abandoned me
```

### [47] hash=`17e0332c5843bc71`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
because I had little so-called talent for our kingdom and now they are showingremorse for what they have done.There's more, my stupid younger brother knewnothing about what happened to me.He didn't even recognize me, his ownsister.You paid them a visit this time back in your hometown?Visit them?Nosweetheart, I went home to do many things except to hear some old people's apology.I've never cared about those things.
```

### [48] hash=`cc1fc4c5981cefca`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p1`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（01.观星者们.）

```text
I went there to deal with a little business, and it was done smoothly.So smoothly that I've taken care of everything there is to be done.Calabona.If one day we can see that celestial body with our own eyes, or even touch it withown hands.I will definitely.Kamar, what are you talking about?
```

### [49] hash=`3322c1f6d9a4d226`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p20`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（【晃铃响于山谷】7至8）

```text
Give me a hand, friends.I can't do this alone.Think I got the stubbornness from you, father.Footage predicted.
```

### [50] hash=`912db4ee2ff938a5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Comment ce serait bien si je pouvais dormir dans mon lit par un temps aussi frais et agréable,ou alors autant rester à délit avec maman au ventre de cette opase ?Mais congé la prochaine fois !En ce moment, l'énergie céleste semble être parfaitement forte,et la meilleure zone d'observation se trouve être proche de tes lits !Quelle occasion providentielle pour ce génie de la divination !Ce serait de la folle inori à faire !
```

### [51] hash=`b294a35120fd67f9`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Tant voir !Quand j'ai trouvé le bon endroit pour méditer,Je remontrai jusqu'au sommet !Voyons voir de quoi il est question sur cette afficheDIPA FestivalUn mot pancrole de DIPA Festival de Mr.ShankerEvery year to seek the blessings of VandrumOh !Alors c'est en fonction de la pluie de météorite ici !Vandrum...Je crois que j'ai lu ce nom dans un documentJe suis à l'est de Chandigarh en ce moment.Pourrait-il y avoir moins de signes ici ?
```

### [52] hash=`1c0c2c5778c116ad`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Car t'es en anglais de l'autre côté !Très bien.Ce serait encore mieux et plus classe si c'était en français.L'endroit que j'ai trouvé grâce à la divination s'appelle...Mor-Vac.C'est un temple !Je dois me rendre dans sa grotte au nord ?Bon, un temple.Cela peut être un rapport avec le mythe de la comète que j'ai lu avant !C'est pas aussi l'un des endroits où l'on peut voir la prochaine gluie de météorite ?
```

### [53] hash=`66a943f20eef29c5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Super !C'est là que je vais alors !Oui mon stylo !Très bien !Notons-le !Bien joué !Pratiquement la nouvelle ville !Beaucoup mieux que le plafond de la gare de Delhi !Je me demande comment vont Momo et Papa maintenant ?C'est India ?Vous m'avez encore négocié.C'est un petit geste rapide.Très court.C'est marrant.Quelle nid de fille.Friends, vous avez vu ?Cette fille va être très douée.Qui est en train de dormir.
```

### [54] hash=`64d6dca7ef6e5b1a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Je ne vois rien, Boss.Comme vous,les yeux de tout le monde ne sont pas si bons.Oh, merci.Oh, de la merveilleuse jeunesse et de la cartouche.Mais qu'est-ce qui est-ce qui est en train d'être en pleine sommeil?C'est le plan qui est offert à la station de rail.Peut-être quelque chose qui a été fait.Par exemple, le plan du poids.Si tu peux aller plus loin dans les livres,Et puis ?Ne t'en fais pas.Ce sera très difficile pour toi.
```

### [55] hash=`ed171d0fce47b932`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Si tu vas de l'autre côté,prends les papers comme je l'ai appris,et si tu les trouves,dis-moi ce que c'est.Pas de problème.Attention, petit.C'est ton premier pas dans notre travail.Oh, ne dis pas à Mr Chakoque je t'ai appris ce travail.Vas-y, vas-y.N'aie qu'un autre aller le prendre avant toi.Quelques choses qui se balancentCe n'est pas une rencontre amoureuse.Quoi ?J'ai mis ça dans ma poche.Quelqu'un doit travailler sur ses techniques.
```

### [56] hash=`92e9463e41fd88f9`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
C'est vrai, mec.Je veux y aller.C'est inutile.Vas-y.Fais ton propre travail.Malheureusement pour toi.Mon boulot aujourd'huic'est de m'interroger dans le boulot d'autres.Ça semble qu'il y a plus de choses dans la poche de toi.Vas-y, tu sais où on va.C'est mon pédule !Je serai à la maison à 10hWow, il y a tellement de choses à faire !Oh mon dieu !Hey !Dépêchez-vous !Vous allez vous blesser !Pourquoi est-il en courant ?
```

### [57] hash=`63ee48652d8eb90e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Laissez-moi voir...Ah, bien joué !Vous avez planifié cette route avant, n'est-ce pas ?Alors, à gauche !Oh mon dieu !S'il vous plaît, laissez-moi !C'est venu !Maintenant, donnez-moi !Vous visez !Je suis fatiguée !T'es encore là ?Merde !Reste là !Prends l'allée derrière !Wow !T'es sûre que tu sais comment aller, mec ?Mais c'est assez !Donne-le à la fille, d'accord ?D'ailleurs, la police n'est pas aussi mauvaise que tu penses.
```

### [58] hash=`7aa9d8df0db0b1e5`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Non !Je ne vais jamais y aller !Ta terri !Vos logues n'as-t-ils pas reçues ?Tu n'es qu'un petit...Ah !Toi !Mec !Attends !Juste en temps.Est-ce que c'est toi ?Euh, oui !Laisse-le, enfant.Merci.Elle est partie si vite !Bon, j'espère que je ne les ai pas abîmés lors de la poursuite.Une, deux...Il manque deux pages ?Où sont-elles passées ?Je suis sûre que j'ai déjà fait ce que j'avais pensé.Et personne ne brûle plus qu'un oiseau.
```

### [59] hash=`0dc851b09f34ad12`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Prends soin de toi.Réalise-toi.Le pauvre Agathe.Je vais gagner de l'argent avec cette fille.Et avec celle que tu n'as pas réussi.Hmph!C'est un objectif avec des cheveux jaunes.Tu vas voir, Kanjira.Oh!C'est quoi ce que j'ai mis sur le pied?Est-ce qu'elle a trouvé ça?Oui.Mes yeux ne me traîneront pas.C'est vraiment un plan d'un poids.Regarde, il a fait une étoile.C'est comme une photo des livres.Oh, tu es incroyable, Kajira.
```

### [60] hash=`e0b003870b5601cc`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
C'est incroyable.Laisse-moi voir.Oh, je vais devoir lire avec les notes.Qu'est-ce que c'est ?Il a écrit tous les mots de faute.Y'a un petit peu de bimbo et de matra sur les mots...Oi!Ne pense pas à mon déjeuner!En fait, je suis un guide, qui donne toujours le meilleur service.Un guide ?Qui donne toujours le meilleur service ?Un guide de tour, peut-être ?De toute façon, je vous le dis, personne ne connait la sphère mieux que moi.
```

### [61] hash=`bb0e71b930981e44`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Hey, n'arrêtez pas !Tu me stères comme ça?Je me déroulant ici pour une raisonJe ne donne que des services aux gens de l'extérieuret aux gens coolIls ont un bon goûtC'est pourquoi je te trouve à la stationde tous les voyageursGrand customer, jamaisLes gens de l'extérieur et d'impressant, tu disHmmm, au moins tu as des yeux fiersTu vois, le lieu que tu visites est différent de celui de d'autresCet église, il y a seulement quelques touristes qui sont capables de...
```

### [62] hash=`bfb1212c87419ca8`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Ha ha, seulement les locaux le savent.Et maintenant, les gens peuvent entrer dans 3 caves par 4.Mais si vous choisissez moi,je peux vous prendre dans la cave Nord,même si elle n'est pas oublier.Vous allez me prendre.Comment je fais ça?Les connexions locaux, bien sûr!Je ne savais pas qu'il y avait des différences entre les documentset le brochure touristique.Je savais que c'était tout ce que vous riez.
```

### [63] hash=`b8659c6c8b9376cb`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Je sais que c'est juste une snotte.Tu vois, je fais juste une vie ici.Je suis petite et fin.Je ne peux pas compter avec les adultes.Tu es si belle.Tu ne vas pas me laisser,la pauvre fille,être faim pour pas de monnaie.Tu as-tu?Même si tu me regardes avec des yeux fous,je sais que tu es une fille avec un bon goût.Just like a sand cat, brave and smart.Sand cat, it sounds like a smart animal.Anyways, you is lucky to meet me my lady.
```

### [64] hash=`8a86d4eb70896c35`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p2`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（02.黄水晶灵摆.）

```text
Well well, for a great customer like you, I can only suffer some loss.Just 200 rupees and I'll show you the shrine and the whole Moorpunk village.With a special Deepa festival tour on the house.Want me to recommend a hotel?I know good hotels too.Oui ou non, mes chers invités, mes meilleurs invités, s'il vous plaîtJe vous invite à être mon assistante temporaireJe suis déjà très tristeC'est la chute !

Excellent !Avez-vous arrangé un bus de shuttle pour le voyage ?Hum hum, j'ai quelque chose de meilleur que le bus pour vousJe vous promets, vite comme une flèche !
```

### [65] hash=`ac16257e65a380b1`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
Damn it, Sinha, for one last time!Don't borrow that annoying human thing to her!Hold that bottle, my guest!Sorry, you must not be used to this.Use it.If you want yourself dirty, fine.You look very decent after all.Here it is!Fill a full white must and sandals.Calming palo santo and cinnamon.You feel your chakra open?I can also smell a lot of mango.That smells good.Jump over this wall and we're in.
```

### [66] hash=`db882fc283994728`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
At least there is a hidden side door.To see the closed cave, you must pay a price.Connections.Well, that took my guess.No tuk-tuk this village is faster than that.Uncle Sinha is not so nice and lend me if I don't give him my lunch money.My root don't need entrance ticket.Shouldn't you give me credit?How come?Although I think you don't like this rude behavior.Can you hit enough?Not to wipe my nose on your skirt.
```

### [67] hash=`b87b5b969b9ebf77`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
Yet you repay my kindness with good.The wall up this height is really a piece of cake.Do you need a hand getting up here?Weirdo.Now what this?Better not be lying.What's that in your hand?You want a bite?The prayers are so piousSo don't worryThe fruits are tastyLike I expectSo sweetTake it from the offeringBy the wayI hope you are not afraid of snakesI am a special kindCurious about what exactlyyou are referring to
```

### [68] hash=`25d527b4e55f3662`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
Specially rude or specially annoyingWhy so angry?I mean, I'm Arcanist.Hope I don't scare you.Relax.I'm not like others.Are you serious?Can't you tell I'm also an excellent?All those good virtues you can see.You don't look like one.I thought all Arcanists except me are like...Like the villagers.Those old man's yell when they see humans like annoying monkeys or crowing chickens.They even drive humans away.
```

### [69] hash=`9d37e2836647f482`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
Don't care they is here to help.Why you think only the train station is tidy and clean?Humans and other places is all drive away.I'm not like them because...Anyways, I never thought there is more a pianist like me.You read too little and know too little.Why don't you follow my example and adopt the style of Airwheel, a canist.Oh, Manka say there is just a few people outside.So up your head, stay confident and walk out like we paid.
```

### [70] hash=`3dfbb67e8a97ef18`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
Nice, nobody around as usual.But I still suggest you be careful since I understand the damage been digging.Just don't involve me if you must break something.So this is the head of Vindre?Dark and scary, but this is what must go through on the way to treasure.Just like you must say, open sesame, right?I really don't know what to make of this treasure you've been mumbling about.I hope you didn't get the wrong idea.
```

### [71] hash=`8be0aef3c70918ea`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
I see what you mean here.Relax, I will zip my lips and tell no one.I'll just stay here then.Everything good luck!Despite all the strange things you've been talking about along the way,you have successfully taken me here as promised.I guess here is where we part.Thank you!I wish you all the best, my brave guest!Even if a snake or a dragon is waiting for you,you don't need to get a treasure.We'll meet again!
```

### [72] hash=`19233ea3aaff14f3`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
This mural painting seems to be related to this myth.Here!On this document!Let's see...I found it!Before the serpent struck in night sky, the stone house of Azura rose to the north of the head of Vindre.The master of the stone has acted with countless feet, with countless eyes, to trip, to pry, in bringing the blessed house of men to rest.The best moment to train on the heavenly energy is when the comet crosses the sky.
```

### [73] hash=`244b613a43e4cf9c`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p3`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（03.寻宝新骑兵.）

```text
Darkness reaches the men as the serpent's tail refills itself.Some are sent down the great slopes and never return.For desire is the unfallible.Voldifauro, Le Désir, Je devrais méditer avant de m'entraîner, The circle of everything, The tip of the great tail, All...Est-ce que j'ai mal entendu?Ce n'est pas normal!Est-ce que cette statue était dans cette position avant?Il est temps de se replier!Proche d'ici toi!

Pense à ce que tu as appris et pratiqué autrefois!You want to offer your seat to the senior?Handle it gently.
```

### [74] hash=`1180c81278255c70`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
C'est pas bon, j'suis ma Tilda.Arrêtez vos pieds !Bien joué, petit divin.Ramaniyani Ariyani.Mes jambes ?Elles-mêmes.Closez vos yeux.Ne regardez rien.Les illusions vont détruire votre souhait.Mayura Abirudani.Une compétence organique hallucinante.Poire de Lady from the train station.On dirait que nos destinés sont maintenant entrainés ensemble.Kid, qu'est-ce que tu fais ici ?Je ne pense pas que ce lieu est ouvert à des touristes.
```

### [75] hash=`658fa29aebc0894a`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
C'est une illusion ?Ils ne sont pas.S'il vous plait, restez derrière moi.Ce n'est qu'une illusion.Tu as raison.Ce n'est pas une illusion cette fois-là.Mais qu'est-ce que tu fais ici ?Je n'étais qu'ici pour...Le temps d'expliquer.On est à l'exit bientôt.Souvenez-vous, laissez ce village dès que possible après que vous sortez.N'oubliez pas...Faites attention à votre tête !C'est plus dur que je l'ai pensé.
```

### [76] hash=`736ef5a590ef7988`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
Mon père m'a dit que ces statues pouvaient bouger.Encore une fois !C'est dangereux !Ah, désolé !Bien que vous ayez une appearance très impressionnante comme statue,votre attitude et votre manoeuvre sont problématiques.Ils m'ont presque sauvé.Hey, vous allez bien ?Ces trucs sont freaks.Alors, vous savez d'où ils viennent ?Ma tête a presque été éclatée quand j'ai atteint l'entrée.Je ne sais pas si c'est un petit garçon.
```

### [77] hash=`d6a20fd54fe0f269`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
Ou peut-être il y a 12 ans.Je suis accueilli par ces choses dès que je reviens.Quelle surprise !C'est lui ?Attends !N'est-ce pas le petit garçon de la station de train ?J'ai aidé à reprendre ton truc.Tu te souviens de moi ?Oui, c'est moi !C'était une bête merciless.Ha !Quelle coïncidence !Peut-être que ce n'est pas le meilleur endroit pour une réunion,mais la occasion n'est pas pour nous de décider.
```

### [78] hash=`ab89cf7414bc8ee8`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
Oh, je devrais me présenter à cette fois.Mon nom est Chamaine.Désolé, je n'avais pas beaucoup d'aide tout à l'heure,et j'ai laissé cette fille s'arrêter.Mais cette fois, j'ai fait ça à vous.J'ai fait ça à vous, je suppose.Désolée de vous interrompre.Mais je pense que ce lieu est en sécurité seulement pour le moment.C'est une bonne choix d'arriver le plus vite possible.Je veux dire plus que ce cave.
```

### [79] hash=`68325f9f5c97fb98`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
En fait, êtes-vous des touristes ?J'espère que vous pouvez quitter cette ville dans quelques jours.Je sais que ça a l'air bizarre, mais vous devez me croire.C'est moi, Marie-Père-Chan.Wow, wow, wow, easy lady.Take your time.Weird listening.Oh!Here's your ID.Miss...Kala...Bona.Hold it.Thank you.C'est pas possible.How come you have Kumar's stuff on your belt?You know Kumar?Laisse-moi voir.Page 1...Page 2...
```

### [80] hash=`6cabe78992efa211`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p4`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（04.交织线.）

```text
Thank you.Le papier parle d'énergie céleste, il est exactement de celle sur laquelle je veux m'exercer.L'analyse sur l'énergie arcanique est très similaire à celle des documents que j'ai trouvé.Pas complètement, celui-ci semble.
```

### [81] hash=`109d17ccb2bd0e21`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
वाक्याक्मार का खाना थाकुछ होना जाहिए था नाउसे उसे कुई राक्षस तो नहीं खा जाएगाहे भग्वान रक्षा करना उस खमंदी मूर्ख कीजो भाग निकलाओ और मेरे लिए सारा घजाना चोट रहासम्हल केशुप चाबवो तीक हैवो कहराई में क्या करी ही है?वो दोनों कौन है?मुझे नहीं पता था कि यहां इतनी सारी चटाने है!तीक है!चढ़ते रहो!लगभाग पहुछ गए!पथर है क्या?ऐसा लगता है कि यह वहां मौजूद बचुरत मौर्तियों में से एक है!अरे, ये क्या हिल सकती है?वाँ!
```

### [82] hash=`9cea4e41b1c36701`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
ये बिल्कुल वैसा ही है!वैसा ही!खानी की तरहां!हाँ!ये सही है!वो खजाने की रक्वाली करने वाले गोलिम!वो सच है!मैं जानती थी!और वो अज्गर जो महल को खाता है!वो रत्यं जो सुमंदर को तोरता है!खुल जा सिन्सिम्, मिश्शर्जा जूट पोल रही है, वो परी कथाइं नहीं है, इसमें कोई अस्चेरे नहीं, कि उसके दो सहायक है, वो खजाना खोजने वाले है, उन्हों ने रक्षकों को हराया है, चुप कर उनका पीचा करो, और मुझे कम से कम थोड़ा साखजाना मिलजो वो भीचे छोड़ गये हैं, जैसे कासिन ने तराजू से सिक्का निकाला था।
```

### [83] hash=`8eb471437fdf536a`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
कुछ पिष्यानात्रावा कै प्राज़ाका खुद नहीं है।अच्छाइं, आप आप पता श्यक प्रजाने के पर जाएं नहीं।तो आपको आप तुम्राइन का प्रजाने के प्रीज़े है।आपको आपको प्रजाने का इस्ते है。खुमार्, और मेरे परस्ट अभिल में आप लुप जाति to the celestial body and its existence is only known to Kumar and me.इस का लिए आपजिक्त हो यह बना उनवर्साच अपनी प्रस्ट का लिए आप तो एक बुल्द ऍि आपनितान के बाध्यता रखानिंग को आसाहतान विक्रेनी प्रस्ता का का रहाता हैं।
```

### [84] hash=`00ca50a3be67a40d`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
पर उनके ड़ातो बादी होता।अर्कानिम् इस लिए ऍोद्ट्रे वीविवाद स्यमच और रहे जाएंके था।और उनके बारे जाएंगे नहीं पर लिए खार।और इस व्यक्रेमिन चार।उनके लिए लेए लग के लिए नहीं पाथ करते हैं।लिए पराइपकल जाना नहीं रपाना का पौंच च्तिजिवा अच्छाँ।मसाले हमें अच्छाँ को विएका है तो इसर्था।और एक दोना पर विवाला थी ये अबस्वाशण के लिए नहीं पूर्भना है।She saw her leave with the madness, and I found this from what she left behind, compared it to the hole in the wall.
```

### [85] hash=`acb2f1880411e507`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
It does come from this cave, and it has something to do with the arcanum-related materials on that celestial body.But Kumar never makes mistakes.This one is more like a clue she left to me.Judging from the situation, apparently I am not the only one invited.अब ओरी पाया को आप वो पताली देखिए।क्यों रहे हूँ।मेरे आप बहुत प्रश्चाइंगे यह पड़ी हूँ।मेरे अपके लिए प्रश्चाइंगे यह पड़ी हूँ।इस छकानीको अब कया लिए फिश्ट्टल कपी हेब भीजिना के कलोना东खाम का कहता बाला और यपडिल dobrze चाहि क Kindernerm forest
```

### [86] hash=`40f71e2ebab8a661`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
तोस्ते से परू करे कि हिए मृदूबा के इक एक सुच टाइञाना प्निया विश्ट करत कर थाजां, चाहि is the first thing that I found weird in what you said.As far as I know, my sister is even worse than unqualified,if taken as an Arcanist.She is almost like a human.It's nearly impossible for her to use the most basic aquarium skills.And this?This is not something a random person from our world can do.Is she really able to control these things?
```

### [87] hash=`8a13652252d8690a`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
No she can't, but she has a solution.कपारा और कुमार और मानिस के साथ की कापाई �वाट।मुर्पाइन्वाल।में कौडर औट चेजे चारका पर मैं क्षिर।आप पहुग एक पहशाना का कुपा।अपने स्थवाँ को मैं य स्वाइएर का चारका रहा।में कछा चेजे लिए आप याह्टार बर्णा।यंनाे को तामाम हैं ?यह आप तक की खराब, सबसे खराब परीकता है।यहां कोई खजाने नहीं है, और अब तो यहां चडाने भी नीचे गे रही है।मुझे, मुझे वापस चाना है, मुझे दावनी देनी है।मैं थक गई हूं।
```

### [88] hash=`c911d7924a9b6420`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
कंजिरा!मिश शजा!यूंग मिस।स्ट्राइट। तो आप तो लिएए परावा जाएए, वेर आथर्से यह था?वेर दे जाए?वे परावा था, वो कछाओ था नहीं तुम्हां परावा और अपने लिए तो लिए तो अभी देखा!वेर भी पार किसा परावा देखा!ये अगर बत?guessing at what is happening on earth.विल्ड लिए लिए नुज्याना है। Listen to me..और्ट्रहाइं के आप हाँ कि रुप कर कराणा है। And they are caught by a stone hand in the shrine's cave.और सब शिवारभालाशालों के लिए सकाओा। And I see the treasure hunters.
```

### [89] hash=`2111879abc4b2b06`

- lang：`other`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p5`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（05.继承者.）

```text
और यह्सा वत्ते हैं। I hear what they say.में तीयो और स्माश्ट विलेज वेन दीपा फेस्टिवल स्टाट।हाणि, मैं तोल आप आप आपने पारी टेल्स नहीं है।नहीं, यह तुम स्ट्रू!तोस स्टाचुस अच्छाली देखा!नहीं तुम स्ट्रू!तोम स्ट्रू!तुम स्ट्रू!आप इप गष के इप में से हाँ देगा?आप आप आपके लिए खाराव?अपने फिर कुमारा और अपने बी आपको शारी शारी जीड्रा कर था।एक वetts और पीड़े देगा रहा था?यह आप की वालेट इस यह अड़ाग ना to पता रहा था?
```

### [90] hash=`1cfb118d1dc39926`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Thank you so much for your understanding, Mr.Sharma, and Ms.Poonish.Ah, please, madam.I have my admiration for voluntarily taking care of these kids.Besides, technically speaking, this room doesn't belong to me anymore,but to my sister, Kumar.I wish I could leave the house to you for future use.But you heard what the lady said.I don't even know if the house will survive the meteor.This is the latest batch of Darjeeling tea.
```

### [91] hash=`f81f410cb9a836c7`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
Some locals gave it to me when I went across their village.Careful, it's hot.To iron on it, to get it, lying to me, all this-Quiet before Ms.Sharjah.You don't lose anything, my lady, please forgive me, will you?Now pass me cookies, I need to fill my belly and get to work.My apologies, Ms.Sharjah.I know this is totally out of the blue, and the details are yet to be verified,But our valuable time is running out.
```

### [92] hash=`a8c21216b2c32098`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
The last thing we should do is keep on waiting.Allah Baha'um.My!I think I know this name.I've read the paper co-authored by you and Professor Himani.Huh?You've read my paper?Yeah!I'm studying in a public university in Chandigarh.I get to learn a lot of new stuff there.I had a whim to study astronomy before and I remember reading it in a periodical.yes I'm sure it's the same name this part and this part I've read them in
```

### [93] hash=`e301b96253e007be`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
your paper but um this one on the side I don't know anything like it it's okaythat one involves the knowledge of Arcanum anyway this is good news nogreat news so what are you doing in Morpah oh I take care of the kids herein my spare time.Most of them are humans, but there are Arcanists too.I see.So, what are you going to do now?I know the top priority is to evacuate the villages, but we don't have much time,
```

### [94] hash=`d9630824555da43e`

- lang：`en`｜version：`1.3`｜arc：`行至摩卢旁卡`
- doc：`BV1Hz4y1T7Je_p6`
- title：《重返未来：1999》1.3版本「行至摩卢旁卡」全剧情 - Reverse: 1999｜4K（06.菩提树）

```text
since the Deepav festival will start in less than four days.Besides, things are complicated in this village.Most of them, including me, had moved to Chandigarh.And the rest of them?I've heard about that on the way here.Most villagers are reluctant to leave no matter what I say.I tried by starting with those young arcanists, but shame, it didn't work at all.The silver lining is, we have the helping hand of Ms.
```

