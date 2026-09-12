# 剧情图谱抽取 · batch 092

- 角色：`wu_ming_zhe`
- 批次：**92** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.3」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_092.jsonl`

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

### [0] hash=`2d0a61ff5fad9dca`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Why can't it be...a swan?A black swan?Here?Really?That'swhy you ought to go out more often.Else you'll miss these precious moments.A chanceto see something special, like a black swan.Look at it.Some creatures are born withthese smooth, pitch-black feathers.But it's only under the sunlight that you cantheir iridescent shine.That's when all the other animals can only look on and feel themselvesinferior.
```

### [1] hash=`ba611bae915a0292`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
They can never stand out from the crowd in the same way.Your silence is an answer.I know it.Just as I know every time you lash out and curse,you're cursing your own failure.What closer, Charlotte?Why don't we take a better lookit.Look at its gracefully long neck, those magnificent wings, and how it glides acrossthe water.All swans are beautiful, but only the black feathers make it truly stand out.
```

### [2] hash=`7bd6f63a44cded43`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
It brings back some memories, don't it?The feeling of being one with the swans,and the flow of each step of our dance.We were so close to perfection.All we needed was for you to spread your wings and fly.Fly to Paris, Cairo, Istanbul,and eventually to the Uluru Rock.And it comes to me, and I can hold it in my arms,lift it above my head.This perfect, shining, golden medal, standing on the Uluru Rock.
```

### [3] hash=`ddf93fb2bcf81e97`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Look, what you doing out here?For you?Ignore the noise.Eyes on the swan.It's only a tacky, white swan, covered in soot.How ridiculous it looks now, wearing that false disguise.The poor thing, it must have been covered accidentally.You ought to thank the Black Fog for lifting your illusion.Now you can see it rightly.You're not some special black swan that was born to greatness.You're nothing but...
```

### [4] hash=`67a4897fddd58db0`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Willow, what's wrong with your leg?But a cripple.Come back for the punk.Why didn't you tell me about your...You're much stronger than I thought, Miss Willow.If you allow me to address you as sledge.Leave me be.I'm going home.I'll walk you home.I got you.Miss Tooth Fairy and I was just chasing after the Black Fog.But, but I can walk you home, Fer.I just want to go home.I'll go with you.Flutterpage.
```

### [5] hash=`e91add5f87becd07`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
I'm going with me.Miss Willow.I want to go home.I don't want you to follow me.The Floor Ritual is one of the most popular events of the Uluru Games.It has a bewitching style that generates a resonance between the dancer and audience.Scarlet was a genius.She was born for it, and God has sent her a coach covered in dark feathers and skilledin ancient Celtic runes.Coach Raven taught her the Primal Witch Dance that ignited a fire within her.
```

### [6] hash=`c90fd5775b2733ce`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
At least, until that tragedy ten years ago, which took her leg.Coach Raven had given her a pocket of flower seeds as a reward for all her diligent practicing.It said they were from the druids in the forests of Blastonbury.I guess she planted them around her house and got this garden.Now all these bizarre plants share the same strange air with their owner.Who even invited you here?It's time you leave.
```

### [7] hash=`81f73ee0581796f9`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
I'm here representing our mutual friend, Flutterpage.What for?And that usually the only one welcome inside is Flutterpage.But I'm here to apologize on her behalf.Apologize?What's this?An apology gift.She ran off a little before sunrise to collect these for you.She collects these arcane creatures you use to make the lubricants for your prosthesis, right?But she's afraid that you'll get angry at her again, so she asked me to give it to you.
```

### [8] hash=`cb081384653edc17`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Oh, I see.Now I'm the hateful, angry, wicked witch.You're not.The things that these people say about you, they aren't true.As I mentioned, Flutter Page wanted to apologize because, quote,she didn't want to break your heart.Miss Bartley has told her many things about you.She never knew you're such an outstanding competitor.Caroline?Do you accept her gift?Nosy little brat.Where is she now?In the temporary hospital?
```

### [9] hash=`081534567a40a5ab`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
You want to see her?Don't push me!All right, it's my own fault!Enough.I've had too much of this for one day.Would you mind if I politely asked you to leave?You do have a black fog to chase after all, don't you?Just so you know, it truly has nothing to do with me.Miss O'Hagan?Call me Willow, child.What else do you want to say?Would you let the food stay in your tummy for a bit longer?Eat a little more.
```

### [10] hash=`e7c45f7cddfa2d64`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
I don't want you to be so skinny.all right now leave me be please she's seen too much of this embarrassing sideof me I dreamt of eating a marshmallow last night but it tasted like rubber andthe next day my wife asked me why I ate the cotton she had in her nose I saidit's because the air was so dirty that I wanted to block up my throat and shelaughed of course she says it might be better now that I can't shout and
```

### [11] hash=`dd26f81bfe40ca20`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
whenever someone scores.Highest level of professional arcanists.Their abilitieslie far beyond the limits of our bodies, our perception, and everything else.Arthur, mate, do you know what you're doing?Go on then, be a little louder.May as well let everyone know a trusted servant of His Majesty's governmentand his talking hat are hiding out in a pile of litter.Oh that's what you'reworrying about?I guarantee you, no person in their right mind will think
```

### [12] hash=`9e4d989bb0ed2e9b`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
that a brilliant mind such as yourself would decide to hide in a rubbish bra, pretendingto be a potato.Haha, since when did you become a comedian?I learned from the best, mate.Once and back in Oz, I hoped to be awarded the titleof Duke of Sydney Slapper.Not that anyone gives a toss about titles of nobility backhome.We've got more important things to worry about in the Redlands Down Under.You know, Brimley, old chap, you don't have to be a duke to be above people.
```

### [13] hash=`f8e1b516b2d6cda3`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
All you need is someone tall enough to wear you on his head.Bloody oath, mate.Like I'd let anyone pop me on their head.I'm an intelligent being, not a bloody accessory.Look at that sailor over there.See the ropes in his hand?That right there is presently the most valuable material in all of London to me.Right.A bit of rope.And what about it, mate?It's essential that I have it for my invention.We'll just wait for him to throw the ropes into the pile here, and then we'll be off.
```

### [14] hash=`7dcd9f9890522410`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Just as simple as that.Come closer, closer.Ready now.He's nearly here.It's no longer useful to you, son.Just throw it down.Mate, there's a lot of good that's come of being awakened.I treasure all the adventures we've shared.But I'll tell you right now, I wouldn't have awakened if I knew I'd end up in a rubbish bin covered in fish guts.Just a little mistake.What are all these four exactly?These are my collections so far.
```

### [15] hash=`54231d56b9bc9f53`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
A klaxon, a watering can, a fish bowl, and...A chamber pot?You go on full bonkers, mate.You're the Fogwalker.Aren't you ashamed of hiding in rubbish, stealing old junk?It's not junk, old chap.Every piece here will be invaluable to our work.Each one is a necessary component for my invention.Your invention?For...Ahoy, sailor!You over there, please wait!Would you mind terribly leaving us those old ropes you've got there?
```

### [16] hash=`809445ec0bcc9072`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Good lord, he's bound for the sanitarium at this rate.Move along, move along.No pushing.Everyone will have their chance to vote for their favourite competitor.Oi Sweeney, you only pushed me out of the queue.Good bloody job mate.I'm voting for number 007, Molson.Molson?The first-timer?Not all your life mate.I'm down for 005 Barley, she's the top seed.Three days to the qualifiers, vote while you still can.
```

### [17] hash=`431cbb846e260c1a`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Oi, you over there with the block rolling.Come on over and vote for the winner.Oi, mister, stop your pushing.Oh, I'm terribly sorry.I...Sorry, mate, we're on patrol.Sir, we had a situation over there.Let's follow them.Now introducing the competitors for the Uluru London Qualifiers.Bartley Bartley Bartley boy who pushed me might just step will ya me was youthat pushed me weren't it you should be the one minding your own feet Arthur I
```

### [18] hash=`c58de710c48485a9`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
think we're only making things worse trying to move through this crowdlooks like we found our troublemakers what do we do keep up with them andDon't get me involved.I think I'm feeling sick.But he gave us the rope after all.Stop right there!Seems you two rough sleepers are wanted in connection with a fight breaking out on Cross Street.I'll ask you to come quietly and cooperate.Maid, say something.
```

### [19] hash=`6bb523ecee50ad29`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Wonderful.Now I have everything I need for my experiment.The properties of this sea-worn rope should be able to conduct the large particlesInto the purification vesselsMate shut your god for a minute and listen, but how to measure and screen the size of the particlesWe will need more sophisticated equipmentHuh?Why am I being handcuffed?Because you're being placed under arrest sirwait a secondMr..Fogg is that you?
```

### [20] hash=`de4d94cacfaa3e78`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Bloody hell are you seriously telling me you recognize fog before me?How many talking hats do you know?Terribly sorry gentlemen.I might not have recognized you for all this fogWere it not for that iconic umbrella of yours?OhNaturally just as I've somehow failed to recognize the twoIgnoramuses that tried to handcuff a hat.We're sorry again.Mr.Fog Walker andMr.BrimleyBut, we do need to ask you some questions.
```

### [21] hash=`a3498fbd95f1df08`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
What, with you running around, disturbing the peace, and nicking all these strange things you've got there?Oh, I didn't steal anything.This is all just rubbish, and it's for official business.I'm going to lift the fog from London.I see, I see.All just a terrible misunderstanding, then.Naturally, a bit of old rope, a car horn, unmistakably the latest in technology.Anyways, mates.Best we let you go, you've got a city to save.
```

### [22] hash=`64a32e07aa411120`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
We'll be off now.Glad that's over.I'm no fan of handcuffs, even if I don't have any hands.A little quiet, old chap.I'm just in the middle of a thought.How might I assemble it?I'm sorry, mister, but I just heard what happened.Huh?Did you say lifting the fog, mister?Are you really going to get rid of the big scary fog monster?Will that mean you can cure my mummy?And bring back the blue sky?And then we can still have the Uluru games, right?
```

### [23] hash=`279d5658ac437f26`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Mummy said if the fog keeps sticking around making people sick, then the games won'tcome.Mate, this really isn't the time or place.The klaxon, a probe, a spoon, and a spool of weathered rope.Assembled like so, perhaps using a large pot, or a baby's bathtub, it will still need atouch of the miraculous.Breathing!Yes!The Uluru Qualifiers will not just be fog-free, my little friend.They will be sunny.
```

### [24] hash=`4f6806816c9a2391`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
But I'll need some help.Would you and your friends join me in this project, young lady?Yeah, I'll ask my grandpa, my mommy, and Auntie Martha to help too.The more the merrier.We are going to build the largest fog purification machine on Earth.The London Air Pollution Auto-Detect Cleaner.That just looks like a great honking big vacuum to me, mate.Sulis, Sulis, all life's offerings I bring as sacrifice to you from the growing spring.
```

### [25] hash=`811b936b5d9b344d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
The light will sprout within the world's egg-lay.Your endless quest brings parents joyful day.Parents joyful day?What are you, a parrot?Fine, keep on then.Annoy an old woman to death if you like.Looks like you haven't had a proper guest in ages.Have you forgotten how to make a cup of tea?You like to presume, don't you?So why are you here then?Just to enjoy the sound of a door slamming in your face?
```

### [26] hash=`a044be2f742f6c82`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
Oh, how terrible of me for wanting to visit an old friend.So then, Ms.Bartley, you came all the way down from Yorkshire just to gawk at an old rival?I should feel lucky, should I?Or haven't any sort of tea you'd like you have changed haven't you Charlotte?What the blazes are you doing what just said you don't have any tea I likeBut I think this one is just to my taste.Wow.Miss Willow that ribbon is amazing
```

### [27] hash=`35700644f168485c`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
It can go from long to short in a secondYou're no longer the model of perfection, you're just a shooting star that shined toobriefly but eventually fell away.I am the rising sun.My name will be eternal in this sport, long after yours is forgotten.So be it.Go on, be the glorious sun, and leave this fading star alone.Lisa, you're back!We were just talking about you.About me?What's about me?about your dream and your favorite competitor oh you mean Charlotte O'Hagan
```

### [28] hash=`a2d4a26f9c4c8925`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
yes we that's great but mr.fog needs us for a project he says we can still havethe games if we all work together and maybe everyone will be able to attendthe qualifiers maybe even Charlotte O'Hagan a project what sort of projectGive me a break!What are they planning to do this time?Another useless build that won't pass the House of Lords?Sorry for interrupting.Did I hear you mention Mr.Fogg?Mr.Fogg!
```

### [29] hash=`69b481c1bc89191c`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p77`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 6~9）

```text
He said he's making something that will lift all the fog from London!It's his great invention!With everyone's help, we can build a huge machine!But, he says we'll need lots and lots of things, such as, um, pistons for the mechanic lung, and...I'll take it over from here.Thank you, Lisa.Mr.Fogg!Mr.Fogg?
```

### [30] hash=`c3d01b4a05780ce5`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Miss Willow, I think the water's been shut off.I opened it all the way, but nothing's coming out.Go to the water resource office and ask the staff what's going on.If they're not there, they're probably at the gin barrel.I know you want me to leave, but how are you going to track the time and score without me?With a heart that's pure and a body lean,to the hunt I go through forest green.And when the water's just shut off too.
```

### [31] hash=`51860a688061d3ae`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
I did ask Buzzy to visit the water resource officeHopefully it didn't slip her mind if she even knows how to use itNever mind.I can clean it off without waterDamn it's off you stubbornlittle thingEveryone loathes youAvoids you like the plagueYou're just a patheticStop thinking about it, stop hoping, don't look back, look ahead, just look at the cauldron.See how clean it is now?Stop cleaning the places where you don't belong.
```

### [32] hash=`b18ca7b8280c7825`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
The world is perfect without you.Latterbead, is that you?I can hardly open my eyes in all this wind.Where are you?I'm right here.You've been looking for me, have you?How did you find me?Liberty Grove, on behalf of Charlotte O'Hagan, hereby challenge Caroline Bartley to see who will become the champion of the Floor Ritual in the Uluru Games.No matter if you're a seeded player, a champion, or the son you say you are, Charlotte O'Hagan, the only Floor Ritualist to master the two and a half turn with free leg backwards and upwards, one throw and catch, will defeat you and
```

### [33] hash=`74b53736fcaaffb5`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
win first place in the London Qualifiers.Yes, that's exactly what I mean your attention, pleaseThis glass stopper is one of the core components of this machineWhich can harness the power of the Sun to purify the air of course.This is only one component of menAre you done talking?We've given you everything you need.Where's our purification machine?Quite right.We need to see the purification machine
```

### [34] hash=`d29664dffafef9c4`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
No need to worry folksBelieve me, there is no one who wants this purification machine to work more than I.So, I've been doing some experiments.Arthur, wait!Forgive me for not helping move it.I'm afraid I'm handless and horseless.I can't do a thing.What the bloody hell is that?Some kind of mechanical freak?Not to worry, Brimley.Now folks, take a look at this.Thanks for your generous donations, my experiments on smog removal have finally come to fruition.
```

### [35] hash=`68451c71a559bd28`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Introducing the London Air Pollution Autodetecting Purifier Mk2, a high-power, multi-functionalair-cleaning machine.The current model can only operate for three hours at a time, but I'll continue to improveits performance before the qualifiers begin.It's estimated to last a whole day by then.Wonderful!Simply wonderful!No more smog standing in our way!Goodness, I can't remember the last time I saw the sun and breathed fresh air.
```

### [36] hash=`bec5f0aa9535ad5d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
I feel as though I've been rotting!It's an honour to see that sweet smile of yours, doll.I think I'm inspired somehow.I've always felt like a bit of an outsider in London.But this festive atmosphere makes me feel a sense of belonging.I totally understand.Though I awakened in London, my true home is a land down under, thousands of milesfrom here.In some ways, I'm an immigrant.This sense of belonging is a treasure.
```

### [37] hash=`dfb135cc81005baa`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
An East London resident my chest swelled with pride when I learned that theUluru qualifiers will be held here.I didn't wait to see what would happen.That's your ninth sneeze since we got here.Don't blame me, I didn't even want to come.The Uluru committee ignored my application to stay at the Australian headquarters.They couldn't find anyone willing to come to London with all this smog in the air.They didn't have much choice either, mate.
```

### [38] hash=`4973ba474f992152`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
The Foundation's been preparing for the qualifiers in London for ages.We'll suffer huge financial losses if it's cancelled.Someone has to make the trip to decide whether we should cut our losses or continueto throw money at it.evidence that proves the environment isn't suitable for holding thequalifiers and the profiles of all the participating athletes then we can gohome.Let's see what the local community has done to prepare for the
```

### [39] hash=`5d27a2dbcf44a245`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
upcoming event.White and fluffy!Yes, so fresh.I've never felt anything like it.Hey, I can even see Keaton's store 50 yards from here.Hello!It's waving back!The first week is for planning, the second for execution, and the last for delivery and paperwork.Looks like you've completed the tasks as Judge Want.Are you relieved?Miss Tooth Fairy, the sun is so golden and warm.Don't mind him.He's all over the place after working non-stop for the last few weeks.
```

### [40] hash=`cb21def7d03ff748`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
He's just trying to say he's happy.That's all.What about you?How do you feel?Me?The ranger's soul inside me has always wanted to gallop beneath the blazing sun!Yahoo!A critter?No.Is that...the black fog?What's it doing here?The black fog was a result of the increased density of regular smog in the air,but it seems I was wrong.Mr.Fog's machine has cleaned up the smog around us,But the black fog's still here, and it's getting thicker.
```

### [41] hash=`2a684f4b945395ee`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
How curious.At least now, without the smog covering its trail,I can sense its movements more clearly.I did hear that these little things tend to gatherin the quiet alleys of Cross Street.Perhaps they like a visit from the Tooth Fairies.Slipped away at the first opportunity.I knew it, but what exactly was it?What would make the world a better place?Art?Or a heart of gold?Neither!The little mocker-up of Flutterpage will.
```

### [42] hash=`0806b4a1b00f9151`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Where's Miss Willow?She should be warming up by now.Where's she gone?Miss Willow?Miss Willow!Knock, knock!Don't jump to conclusions.Mr.Wind will tell you the truth.Knock, knock!I'll open all the windows and doors, and all the treasure chests too!Miss Willow?come give it a try first put your hand on it like this okay then what I'll teachyou how to play it imagine the note you want to play and tell it to the didgeridoo
```

### [43] hash=`6159ae43c51e0144`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
wood hmm okay no use your arcane skill not to use your words but toUm, Flutterpage, maybe it's time to give up.Give up?What do you mean, give up?Don't understand.It's the Olaroo games we've been talking about for ages.Think of all the effort you've made.You didn't jump up and down in the garden over and over again to dust it, did you?You're an athlete, not a feather duster.You finished that move!The, um...
```

### [44] hash=`c61385d9967a69dd`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
and that it took all her effort just to keep you in her sight, let alone catch up with you.Because you're different, the one true master of the art.If there were only one gold medal in the history of the Floor Ritual,it'd be meant for you.Those were her exact words.I only chose to become a Floor Ritualist because I had a talent for it.I wanted to win, so I practiced and practiced, paying little attention to anything else.
```

### [45] hash=`a7d3d8dd329d502b`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
My family, my friends, my life, none of it mattered more than victory.To me, there was no reward more alluring than the euphoria of winning.But whenever I looked back at my past glories, I felt no happiness or excitement.Instead, I'd replay every moment in my mind.Every lost point, every imperfect movement, and think about how close I was to failure.So I pursued the next victory even more fervently.
```

### [46] hash=`8c64abb7950d96b8`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
I thought, next time, I won't lose a single point.Next time, I'll be perfect, was what was running through my mind when I was crownedand chocolate drizzled on top.I can still remember the taste.Sweet and tart, with a light bitterness.So what really makes you happy is the cheesecakeafter the game.Right, then let's get you registered for the qualifiersso you can have that post-game celebration cheesecake again.
```

### [47] hash=`e72e215245b93ed4`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Let's go talk to Mr.Fogg.I'm sure he can find a way to get you into thequalifiers.And if your legs cause a new trouble or anything,it ain't happening pardon I said it ain't happeningthe ceremony the foundation officers canceled the qualifiersmr.fog so-called biggest air purifier everdoesn't work please enter in an orderly manner everyonethe ceremony will begin shortly readycan you see mr.fog I can't see a thing past all these people
```

### [48] hash=`9babe8b73d4ed1de`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
you brought the telescope didn't you dad maybe I can see if I look through itGood idea.Here, take the telescope and get on my shoulders.Hold on tight, you hear?This crowd's rabid.All this pushing and shoving just to take a look at a machine.Then again, the most exciting thing we've had around here as of late is the rats fightingin the underground.See Mr.Fogg?What's he doing?Blimey.He's smacking the machine.
```

### [49] hash=`be6f90fc98e79f80`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
It's really strange looking.About half the height of Mr.Fog and connected to a very long tube and a massive funnel.Right there inside the machine.There's a huge mechanical organ or something.Like a lung.Oh, sod it.Hold tight, Freddy.Dad's going to squeeze his way to the front.Alright, I can see them now.I don't recognize those two in uniform.Look, Dad, Mr.Fogg's about to give a demonstration of his purifier to the officers.
```

### [50] hash=`f65f66df7df53e61`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
I heard that it can filter out the smog within ten yards of itself, and it only takes one night to process the waste.The qualifiers will only last two weeks, so it should manage splendidly.It's working!Blimey, it's powerful!It's gulping down the smog faster than a builder down to pint in the pub!I wonder how it works.It's a miracle that a mechanical lung of this sizecan purify so much air without letting out any waste.
```

### [51] hash=`4d88fcc037f214b9`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
The smog's getting thinner.I can see more clearly now.Look, it's even purifying the smog all the way out there.I dare say the ivy on my balconywill be enjoying fresh air within the hour.Mr.Fogg's smiling, Dad.It is.We ain't seen him smile for ages.Looks happy too.They're dancing!Is he doing that Australian ranger dance again?Look at the expression on those Foundation officers' faces.They don't look happy or mad.
```

### [52] hash=`f1d35ec6f629264d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Is something wrong?Whoa!What's going on?The machine's shaking like hell!What's that sound?Some kind of alarm?Ugh!Christ!Cover your ears, Freddy!That howlin' will make you deaf!What in the bloody hell is going on?Freddy are you alright?I'm fine.It blew up.What?First the pipe blew open, thenits glass belly shattered and the mechanical lung rolled out from inside.It's vomiting up black blood.There's no way.
```

### [53] hash=`c357f433e1dcaf6c`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
And...and Mr.Fogg.What happenedto him?He's coughing and coughing.Three and a half minutes.I guess neither one of us wonthat bet.It didn't even last half as long as I predicted.Don't be cruel Gregory.We didn't come all this way just to laugh at these poorpeople.But they did do even worse than predicted.That's a fact, isn't it?Andit proves that the London Climate Management Agency is nothing but a joke.
```

### [54] hash=`7c0a6e66a742bd43`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Listen Gregory, I know you must be exhausted from the long journey andyou're constant sneezing but you can't say that to their faces.Let's just dojob and give them the news.What news?We have to tell them.Mr.Fogg?Mr.Fogg?Please moveaside.I need to use the microphone.Oi!Miss!What are you?Ladies and gentlemen, thank you all for coming to the ceremony today.We greatly appreciateyour hospitality and it heartens us to see you thriving despite the difficulties caused
```

### [55] hash=`0b9c03e69b6c59af`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
by the smog.However, it is clear to us that the London Air Pollution Auto-Detecting PurifierMark 3 is not able to fulfil its duty.Barring an effective solution, the smog-shroudingLondon will do irreversible damage to both the athletes and the general populace if theystay outdoors for too long.In light of this and after much consideration, the Uluruinternational committee has decided to cancel the London qualifiers for the
```

### [56] hash=`c81707c48a7f92f7`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Uluru Games.We will announce arrangements for the affected playersonce internal discussions are over.Thank you all for your hard work.The London qualifiers have been cancelled?I'm afraid so.It wasn't therebut Mr.Brimley told me what happened in the stadium.Mr.Fogg hasA ball of black fog, weaker than the one I met in the alley.Its existence is unstable.Its form changes daily.It doesn't appear to have any self-consciousness, but that critter in the alley was definitely
```

### [57] hash=`0e2ab6fe035eb944`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
intelligent.Huh, this thing.It looks like the illustration in the old book I read to me son.I can't quite remember the title, but it does mention a creature like this.A creature like this?Oi!Miss Tooth Fairy!It's an emergency, doll!The little tack is in danger!Please, Mr.Hat, keep your voice down in the hospital.The patients need to rest.Sorry about that, but this can't wait.Miss Tooth Fairy, they said a girl's climbed at the top of the old bell tower,
```

### [58] hash=`80473960457353dd`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
and she's planning to jump off.A girl?You mean...Yeah!Flutter Page!No normal girl could climb all the way up there!Oi, girl!Get down!Jump off the bell tower.Oh, like I might fall.Don't worry.I'll be fine as long as the winds blowin'.I'll ride it all the way to, um...Australia?Australia.They must be preparing for the finals there.Come here, Miss Tooth Fairy.Have a seat.Come along, Liberty!Quickly!It's dangerous up there!
```

### [59] hash=`66efb162e445ac03`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
Don't let Betty!Oh, you!What's your word?She might jump right off the bloody thing!Why?Why what?First, they told me to get down.And then they told me not to.Why'd they change their minds so quickly?Not just them.It's like, all of a sudden,everything's changed.People said they wanted the qualifiers,but then they cancelled them.They said they'd find a solution,I can cut my own hair, cook my own meals, and do my own laundry.
```

### [60] hash=`b4d6cff39ddaf242`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
No one taught me, I just figured it out myself.I used to think the world was like the fish tank I had at home.No matter how many questions I had, the answers were all inside, just like the fishswimming in there.I was patient too.I'd take the fish one by one and carefully look them over.And, I wouldn't stop until I checked every scale.Yep, every single one.Well, unless mom and dad scolded me.Actually, sometimes I couldn't figure out why they hit me.
```

### [61] hash=`faf54427eea45d6c`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
I just had a lot of questions, and I wanted to know the answers.Anyway, now I've learned the truth about the world.It's different from what I imagined.I thought it was a round tank, but it was actually square.I thought there were goldfish swimming inside, but actually they were pinching crabs andchomping sharks, sometimes even just pieces of rubbish.The round tank only existed in my mind and all the answers I found were nothing, just
```

### [62] hash=`be65dfbd9f10f49d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
my imagination.And what's worse is that I hurt others with my imaginary answers.Miss O'Hagan?I let her down.I spent my entire youth learning how to get along with others.And you know what I realized?People will change as long as the result benefits them.Once things are going well, whether expected or not,people often forget the goals they set before they reach that point.What I'm trying to say is,
```

### [63] hash=`d71fdb956934aa4f`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p78`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 10~14）

```text
We need to remember who we really are and what we really want.Miss Willow must have known what she really wanted.Otherwise she wouldn't have become the youngest floor ritual record holder of the century.I'm sure she understands that it wasn't your fault.You didn't hurt her.In fact, you didn't hurt anyone.You just need to look at the fish tank in a new way.It hurts.What's wrong?I suppose I'll keep this then.
```

### [64] hash=`716c34528f80ef74`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Let's listen again to the interviewShe had all those years ago as the youngest floor ritual record holder of the centuryYou're just one step away from becoming the world championWhat else do you wish to achieve in your career?My ultimate goal is to win the finals of the Uluru GamesBut I'll also register for as many events as possible.I have a lotI want to achieve, but I'm patient, and I'm sure I can do it all eventually.
```

### [65] hash=`3e868d5d8d2be62c`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
No, old friend.It's just you and me, isn't it?Careful with the scaffolding, fellas.You wouldn't want it to fall on your feet.You'll be hobbling about for months.Here's the reimbursement application form.Just fill in the numbers and give me the receipts for the materials.I'll contact the Uluru Committee for your compensation.Is there really no hope, Mr Fogg?We didn't build all this just to tear it all down.
```

### [66] hash=`9af0bcdd649f22fb`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
I'm sorry.To be honest, we'd rather not do this, even if we're getting paid for it.We were over the moon when we got this job.I mean, just look at this place.Huge billboards and that lovely stage background.How could we not be?It's been yonk since we last had an event like this.And who knows when we'll have another.Ah, why don't you stay for a few more days?Well, I don't think there's much point.In fact, I'm the number one seed this year.
```

### [67] hash=`9b08de0806e66d4d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
So I don't even have to participate in the qualifiers to advance in the finals.It's a new system they introduced to get a step closer to the standardization of human sporting events.I only joined because I couldn't pass up the opportunity to compete in my hometown.Don't be too hard on yourself, Mr.Falk.The fact that you made something that worked at all, in just a matter of weeks, is an achievement
```

### [68] hash=`7532c50e122f0c4d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
in itself.I appreciate it, Ms.Tooth Fairy.I know it doesn't make any sense to keep it around after it failed so spectacularly.But I just...I can't bear to break it down.At least not for now.I enchanted it with my arcane skill.So we're linked together.It used to breathe as I did.And now I cough and splutter just like it does.You should go to the hospital as soon as possible.See?How many times have I told you that and you never listened?
```

### [69] hash=`9845ee2fb686561d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Even the doctor's saying so.Anyway, what was it that you wanted to talk about, Ms.Tooth Fairy?The experiments I've been doing these days.Here's a sample of the black fog.I collected it from the alley after it attacked me.As for the tuberculosis, I analyzed the black fog's composition and found some componentsvery similar to those in the patient's saliva.I've concluded that this fog critter is the root cause of the disease.
```

### [70] hash=`4ac0fbd180231c95`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
This critter is fog soluble, can change its form, and is indestructible.It feeds on smog and most interestingly, sensitive emotions, which it seems to absorb to nourish itself.In conclusion, the answer to our problems lies in capturing and containing these critters.Also, in one of my experiments, I cultured two samples under the same conditions and put one of them in the sun, like this.See?Even in today's dim sunlight, it shrinks very quickly.
```

### [71] hash=`4eabde05d6911169`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Just wait a moment, and you'll see.It's true being.Sunlight is their weakness.That's why you never see them in areas with clear skies.As you can see, London provides the perfect conditions for it to survive and multiply.Heavy smoke, and the anxiety and depression caused by the cancellation of the qualifiers.I do believe you're right.But it won't be easy to capture these things.No, definitely not.I'm still trying to figure that one out.
```

### [72] hash=`aae82925aa7a8a88`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
We may be able to lure them intoa trap, but we need to make a specific plan so that the process is controllable and theresults predictable.A specific plan?The only plan I can think of is to pray to God.Some people may seek answers from the divine, but whether that works or not is anothermatter.Oi!Is that Flutter Page's voice?Sure is.Over there, mate.Outside the window.Mr Tooth Fairy, Mr Fog, Mr Brimley, would you like to join us?
```

### [73] hash=`874b6715136a7de2`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
What?The residents of Cross Street have got together to petition for the reopening of the qualifiers.Oi folks, how about this iron?It's a family heirloom.But it'll be perfect as a floating shot sling.And I'll be the stopwatch.I'm an excellent timekeeper.I can keep time down to the millisecond.We all could be the fair good, right?Then I'll put myself forward.Everyone on Cross Street knows I'm an excellent mediator.
```

### [74] hash=`802cb62cf6f41f45`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Everyone's brought things from their homes.Ladders, hanging rods, clotheslines.Anything that might be useful.We're going to rebuild the stadium together.So, will you join us?What?Are you serious?Scrooge, I don't know what to say.This is unbelievable.Since the qualifiers have been cancelled, we'll just have to hold our own games.Ms.Tooth Fairy, I've found the right way to look at the fish tank.So, you're going to join them?
```

### [75] hash=`3c402492b3584b0d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
I...you know me.I'll always jump rim-first into the unknown.But the Foundation's already pulled their funding.The workers are already awaiting their reimbursement.And some players have already left.How could we possibly hold a...Mate, listen up.Those officers from the headquarters didn't give a damn whether the qualifiers were held or not.You could see it all over their faces.All they wanted was to minimise their trouble.
```

### [76] hash=`3cd57575e05d9965`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Did you see how quickly they applied for the cancellation and reimbursement?How hastily they made promises to pacify the people.I've never seen anyone more ready to get things over with.Their job was done as soon as they got the player list.They'd probably already moved their attention to the qualifiers in other regions.After all, our qualifiers are no different from the others to them.But it means something to us, doesn't it?
```

### [77] hash=`9138706908349e34`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
At least for me, this could be my chance to go to Australia.My very nature wants me to run free on the red land, to haul around and forget all mytroubles.I think that's what we all want.In the heat of competition, people are at their best, their most pure.Think about it, mate.You're not the only one who's put a lot of effort into this machine.It hurts me to see it rotting the office too.If you're really going to give up because of a few words from an authority, then as
```

### [78] hash=`86af8a0d9d4c3a13`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Well these people stopped sending me petitions.I've been absolutely inundated with them.Fine.Someone has to keep everyone healthy.I'll do everything I can to minimize thedamage from the smog.Don't worry.I'll talk to the relief center to sort outall of the paperwork for the event.Here you are!This is yours.Come herefor a copy of the emergency guidebook if you don't have one.Make sure you read itWhat can it hurt to own a little sport?
```

### [79] hash=`ebf69239509584ca`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Agreed.We asked for the exhibition ourselves.So we'll pay the price if anything happens.Here's the confirmation of your application.Your contingency plan has been approved by the Relief Center.My colleagues and I will do everything we can to keep you all safe.As for the London Air Pollution Autodetecting Purifier, Mark 3,I'll do my best to fix it.Next, we'll gather the athletes who have yet to leave the city and hold a small exhibition
```

### [80] hash=`3b66b3657ccd901f`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
event.Of course, it won't be an official event, but at least it'll give an opportunity forthe athletes to demonstrate their hard work to a group of spectators.I'm sure they'll be a great source of inspiration for the people of London as they cheeron their favourite athletes.Oi, Mr Fogg, I brought you this.It's Mrs Brown's leek and potato soup with bread and butter.Oh, Mrs Brown.Uh, please give her my thanks.
```

### [81] hash=`d9cb0c210fe4d331`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Has everyone eaten?Yeah.Mrs.Brown, Mrs.Jones, Ben's son and I have been cooking since four in the morning toget food out to everyone.But it still ain't enough.Almost everyone in the neighborhood's coming.Alright, I have to go make more soup.See you later.Hey, what's that you got from the knocker upper?An enchanted sheet, apparently.Mr.Fogg, we can still hold the exhibition even if we can't do it.The exhibition?
```

### [82] hash=`2411c786bc3b422a`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
All right.Introducing the London Uluru Exhibition Games.Twenty-eight players have registered for the six-day event, which will host one sport per day.All right!Everyone, let's push together!Three!Two!One!The residents of Cross Street have taken it upon themselves to rebuild the stadium.Hey, your painting's totally off-theme.Look, mine's a marking bird with a gold medal.It just won first place in the singing competition.
```

### [83] hash=`7eb2307a9b68cad8`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
The Uluru Games ain't got a singing competition.You should have drawn something more athletic, like my sailfish.It's the fastest swimmer in the world.How exciting, your very own Uluru Games,without any interference from the Foundation.It's too fairy.I've made a list of all the athletes who signed up for the qualifiers.A lot of them have left, but some would like to stay for our exhibition.Good, and I've made a list of the daily attendees based on the tickets they bought for the qualifiers.
```

### [84] hash=`1da74495b90755d6`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Mr.Fogg and Mr.Brinley are discussing the possible security issues of the event with the relief center staff and the police.Athletes will go head-to-head, spectators will cheer,and the stadium will be lit up by the energy they release together.It's imperfect, yes, but it's inclusive and unstoppable,and that's what makes it special.Leave it to me, doll.Testing, testing.Ladies and gentlemen, your attention please.
```

### [85] hash=`7f85cfaa29e58f8f`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
Today marks the beginning of the London Uluru Exhibition Games.As you can see the weather isn't looking great.The smoke still sits heavy in thesky.There's no wind, no sunshine, no warmth and even my brim is soggy fromthe damp.It's truly miserable out here.On top of that the stadium is shabby andwe only have a limited number of athletes.To many these games would beseen as disappointing.However even without the support of the foundation
```

### [86] hash=`36480249b661afb1`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
We've managed to rebuild this stadium with nothing but our own hands and determination.I've confirmed that our stadium meets all the standards required by the government,and there's no doubt that it matches the foundations too.As for the operation of our games, we've built a reliable teamconsisting of various Uluru professionals and supporters.They are currently in every corner of the stadium,working their hardest to prepare for the upcoming event.
```

### [87] hash=`34ecc91b68505df4`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
They will be our backbone, supporting the entire Games to ensure that everything runs smoothly.As we all come together, I believe the passion of our Games will burn as hot as the sacred fire of Uluru itself.So, without further ado, I hereby declare that the London Uluru Exhibition Games have begun!area um excuse me i i lost my name tag can i get anyone certainly go straight ahead and take thefirst left ticket to the player office there's a girl called flutter page in there show her your
```

### [88] hash=`fbc71c9e5b286895`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
id and she'll give you a new tag i'll take you there follow me friend sure thanks oi hold on aHas he been sitting all this time under that banner with his machine?Yeah, he's using it to show everyone what can happen if they breathe in too much smog.I don't know if I should call him wavering in his principles or completely stubborn in them.Arthur's always been a righteous official.He truly cares about the people.
```

### [89] hash=`2f8b90549ca9de7d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
He's tough, tenacious, and has a powerful ability to influence others.You sound more like an official than he does.Go for it!No!Not even the smog can stop the people's enthusiasm for sports.No matter the obstacle, they will always find a way to enjoy it.I suppose Mr.Fogg is still refusing to take one of Fludder Page's sheets?Of course he is.Arthur said he'd never run away from the smog.As Fogwalker, he has to confront it.
```

### [90] hash=`46e9c82317cb20ca`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
He's stubborn, just as you said.Competitor number 2401, please enter the floor.Competitors 2402 and 2403, please wait in the locker room.Good luck.What about Charlotte?Charlotte, you're here.And me, you wouldn't be able to stay away?You haven't changed a bit.Hm?What do you want from me?What do I want?Have you forgotten about the challenge?What's your number?But you are the Charlotte I used to know.
```

### [91] hash=`c72bcd320fbf4c4e`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
You're still that black swan I've always chased after.When I saw your performance, the grace, the beauty of it,it inspired me to become a floor ritualist.But you just disappeared after you became champion.Well, as long as you're back.What's so funny?See you on the floor.Player number 2406, Caroline Bartley.please enter the floor time for me to head in too excuse mein number 2405 caroline bardley whenever you're ready
```

### [92] hash=`c249ef1b1fd67682`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
what's this miss raven a seed that will settle in your heartand soon grow to be your closest friend its roots will stretch all theway from australia to the soles of your feetand together you will make the music to your floor ritualNow, my dear, listen closely.Listen to what it has to say.Listen.Let it know who you are.It isn't just a piece of wood, but a mouthpiece passed down through the ages.It allows us to understand what our God hears during the ritual.
```

### [93] hash=`83a5eaa62a45ca9d`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
yes speak to it politely and it'll respond with politeness the path ofpilgrimage is full of thorns it offers no shortcuts you must make your way inchby inch otherwise you'll never reach the sanctuary of glory the place whereAll the lights gather, and you'll dry a-nobody.Aene, if I keep training.Shush.Press your head against your shin,just as the divine sun did.Closer.I want that head tight against your shin.
```

### [94] hash=`f7022bab9d82dd33`

- lang：`en`｜version：`2.3`｜arc：`—`
- doc：`BV1eo4y1u7aW_p79`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.3-活动】 15~20）

```text
The tighter, the better.Yes.Confusion.Sadness.I can see it all over you.My classmates were making fun of me.They said I was using the training to avoid my duties.They said I never do anything with them.I've skipped classes, sports days, and the summer outing.They said that all I do is train to be a clown in a show.Hm?Miss Raven, can I take a break?Just for today?I want to spend time with my classmates.
```

