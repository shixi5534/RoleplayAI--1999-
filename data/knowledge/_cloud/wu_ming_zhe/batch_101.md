# 剧情图谱抽取 · batch 101

- 角色：`wu_ming_zhe`
- 批次：**101**（未缓存补漏批 2/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_101.jsonl`

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

### [0] hash=`53d47a272a63c762`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p18`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（18愚人颂）

```text
Why is this happening?The dye.Don't tell me that I'll do it myself.Garcia.Please.It's happening to me.I was so close, so close to completing the exhibition.Can't you see, Garcia?There is no one controlling this place now.You're free.It isn't the dye that's trapped you, nor is it the walls of this prison.Your words are always at odds with your thoughts.You carry an ocean of questions, yet never reveal even a single drop of them.
```

### [1] hash=`a596843ca2ac8664`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p18`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（18愚人颂）

```text
Why have you never shared your doubts?Why do you stay silent in the face of everything and everyone around you?In my duty.As for you, peri-causality researcher, you're different from any other seeker of answers.Even on a desperate, near-hopeless journey, your heart holds little doubt.Perhaps not every question needs an answer, Mr.Aleph.Is that so?It's thinking.This is float on the planks, and the fleeing prisoners are swimming toward the shore.
```

### [2] hash=`5bccd90cd228db10`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p18`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（18愚人颂）

```text
Time to abandon ship.One that was exiled to a desolate corner of the ocean by the resplendent civilizedworld.Madness is a side effect of the sedative that is knowledge.As long as those on land continue to consume it, this ship will never be short on recruits.This is a war between madness and civilization.Both sides have leveled accusations, spilled blood, and pummeled each other.He's in his home base.

He holds no hope for forgiveness from his enemies, not in the slightest.He's a one-man army, fighting only for himself, alone.Now, do a 360 and look again.He's been utterly defeated.
```

### [3] hash=`6fa6436bfae6d09e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p19`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（19科马拉诸相）

```text
Dear Erda, why are you so interested in the panopticon of Kamala?Dear Mr.Aleph, whether as a doctor or a writer, I simply cannot turn a blind eye to the frictionaround me, especially the discord and injustice I have witnessed here in Kamala.So, I would ask of you a question.Is there any way to resolve the endless conflicts in this place?To put an end to this, a true ending is required.Your arrival has made it possible for this simulation to have an ending, or rather, a victory.
```

### [4] hash=`81b5cc973066bffd`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p19`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（19科马拉诸相）

```text
What do you mean by victory?I'd appreciate it if you could clarify in simple terms.If this victory comes at the cost of any inmate's life, I'm afraid I cannot accept it.I also have another question for you.If I leave, will the stories and conflicts here come to an end?Miscrase of Manus Vindictae will grant you passage, but in any case, the cycle of historywill continue to repeat itself in this prison, and in the entire world.
```

### [5] hash=`beeec06310db3bfa`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p19`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（19科马拉诸相）

```text
The sins of humankind will not cease until veins turn to wires, flesh and bone togeometric shapes, and the world around us twists in the colors of an oil painting.she go?Southward, there on the no-man's continent, Manus Vindictae is preparing to recreate theparable of the past and future.A glorious past and a glimmering future belonging to Arcanus.Dr.Dores is deeply connected to this particular parable.
```

### [6] hash=`1aeef624a7625bf1`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p19`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（19科马拉诸相）

```text
What exactly are the Manus planningto do in Antarctica?And why would Dr.Dores go there voluntarily?Mr.Aleph,When did Dr.Doris depart?It was a day when both the clouds and sun were visible.A day when both the clouds and sun were visible?Could you be more specific?Specific?You mean, the time of day?When both clouds and the sun were visible...Hey, Vertin!I think I know!It was three days ago!Then, Dr.
```

### [7] hash=`4a113d03ad3b2f02`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p19`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（19科马拉诸相）

```text
Doris wasn't going to Komala on the day I met her!She was leaving!She was headed to Antarctica.It was cloudy that afternoon, with a brief spell of sunshine, just like Aleph described.Then it hasn't been long since she left.Excellent news.Three days.If we set off immediately, we might still catch up to her.But, based on the intel we gathered in Ushuaia, Manas Vindicte bombed the entire port three days ago.
```

### [8] hash=`a8eab98e0f7dcf21`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p19`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（19科马拉诸相）

```text
Mr.Aleph, members of the Foundation branch will arrive soon to evaluate your condition.I hope you'll answer their questions with the same patience you showed us.Thank you.Sinetto, let's go.Yes, Timekeeper.Thank you for your assistance too, Rekeleta.Perhaps you'll consider joining the...It came from the Panopticon!
```

### [9] hash=`f2e01b5c43e30279`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p20`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（20灰烬安放地）

```text
When this is all over, I'll write to you, my dear friend.During this journey together, our teamwork has been impeccable.So, you can trust me to do this.I'm not doing it just to help you or the organization we represent.I'm doing it because the inmates are my friends.Okay, I trust you.Take care of yourself, Rekeleta.But, the storm chill and said...Of course.Listen, I believe literature is like an endless, timeless river.
```

### [10] hash=`0cd489691f96a552`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p20`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（20灰烬安放地）

```text
So we'll meet again someday.Somewhere.Probably in someone else's story.Who knows?Adios, mis queridos amigos.You're Dr.Maryland, right?I finally found you.What on earth happened in the central tower?Right after I left, the whole panopticon started collapsing.The tower's in ruin.I've been looking for you everywhere.Please sir come with me.It isn't safeThat won't be necessaryThe snow is still falling yet everything in the labyrinth has already gone up in flames
```

### [11] hash=`ddede4d7ef12a619`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p20`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（20灰烬安放地）

```text
fortunefateKarma, they're nothing but a ridiculous jokeIt's over Jaguar.You have lost your memoriesyour identityYour name and now your titleYou are no longer a jailer trapped in the Panopticon.I don't get it, Dr.Merlin, what are you talking about?I'm going back to Komala, order must be maintained, the prisoners mustn't be allowed to escape.Please take care, Dr.Merlin.Hey, you!Run off like that, it's dangerous!
```

### [12] hash=`25e2c8e9a8d834f7`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p20`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（20灰烬安放地）

```text
In deserts!In the stars!We dream!On 10th of July!Are you blind?The Panopticon is falling apart!It's you!Roberta.moments.It was all meaningless from the beginning.I want to leave this place, go to Spain or France,anywhere but here.I want to go back to my family.Let me seeHow does literature make you feel?As though I'm a kid looking through a kaleidoscope for the first time.Well, maybe that's not the best way to put it.

Perhaps something a little more subtle.A ship, sailing to an unfamiliar land.A parable of the past and future.An era that once existed and is yet to come.
```

### [13] hash=`c40f81c911d51321`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
This is a serious violation of the rules.I'll have to report this to the physician and all of your treatments will need to be reassessedUntil a new treatment plan is in place all members of La Sociedad are confined to their cells without any of their usual privilegesThis is not what we agreed to wordFairs within La Sociedad were not to be disturbed.Please don't do thisPlease he doesn't deserve this.
```

### [14] hash=`b2d433274d3d70a1`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
No one does we don't want to lose our friendsMy duty is to keep order here.What happens beyond these walls is not my concern.Perhaps they've recovered from the physician's treatment and will return to society.Within these walls, the only truth we know is this.No one returns from the clinic of the physician of Kamala.Are you certain this treatment they received is really a cure?Pablo is harmless.He's just a writer who has a talent for finding words and poems.
```

### [15] hash=`81eeb88020bf0487`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
That's all.Please, let him stay.We'll look after him.He can have our share of the medicine.We'll keep him in check.But this doesn't conform to our regulations.Steal as Eric and as ever, idealist.One day, you'll get us all killed.Oh, it's you.I'm glad to see you here.Who is that?That's Octavia, one of our model inmates.She's been a great help in the past.If you're interested in prison literature, I'd suggest talking to her instead of the idealist.
```

### [16] hash=`1ea36436257e6539`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
So, she's a writer too?Who would have thought?This place has got writers coming out of the woodwork.I thought it would be easy to find my writer friend in a prison.But what are the odds that I'd break into a place absolutely lousy with them?He used to be in their gatherings, until she got tired of their nonsense and started here on faction.What are you doing here, Octavia?Haven't you heard?The era of chieftains, ghosts and plantation stories is over.
```

### [17] hash=`f8cea8442b21bca0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
Visceral realism is the future.And has this brilliant visceral realism helped you finish any of these poems?What a waste of time.I'm not interested in your movement or arguing with you.I just walked by and happened to witness another episode of your brutal arrogance.And I'm not about to just stand aside and watch you repeat your mistakes.I'm taking Pablo to the physician.Care to lend a hand, Miss Jailer?
```

### [18] hash=`4b62a894ff410caf`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
We agreed to mind our own business.Are you breaking our agreement?No one, no one will be allowed to erase a word from our poems.Haven't you let your ego cause enough trouble, idealist?Better that than siding with the devil like you.Enough!This pointless arguing ends now.My responsibility lies with you, but you won't get away.Stand down, both of you!You've never listened.I pity your followers, to be led by such a reckless megalomaniac.
```

### [19] hash=`f15cd46de18ef09a`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
Do you even think about the consequences of your actions?We've fought hard to earn the freedom to discuss literature under their watch.Your impulsive ego threatens to destroy everything we've built here.Spare me the lecture, Octavia.We don't need permission to do as we please.You're just another puppet of power, kneeling to the eyes behind those glass walls.They've trained you to believe it was your own decision, to be good and conform.
```

### [20] hash=`23305b0b9468fbcc`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
Who could have done a better job?When I look at you, all I see is a sheep.Docile and obedient, just the way the Tower wants.What kind of work could someone like you create?Literature isn't defended by those lounging in cozy rooms, scribbling to soothing music.Have you looked in a mirror, idealist?You've become a pathetic windmill-tilting fool, a monster tearing down everything around you.A beast of prey, you mean?
```

### [21] hash=`1406c3cc0b837842`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
Naturally, a sheep would be appalled by the mere thought of such a creature.A fearful sheep caught in a vine, confusing the blade that would set it free with the jaws of a lion.Such a master of metaphor!But I beg you, learn to distinguish right from wrong, fantasy from reality.Only then can you truly lead our people toward what's right.Distinguish right from wrong?Don't make me laugh.Is that the limit of your vision?
```

### [22] hash=`1f80bfe7f54dd67a`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
You...Ranios!Friends!Listen to me!There is no truer home to literature than a prison!Who did this?Hands behind your head and drop to your knees, all of you, now!This is your last warning!Idealist...You...You're bleeding...It's in your chest...You must...Yes...Idealist?Was he shot?Where did the blit come from?Miss Jailer, and you ladies over there!Come, give me a hand!We need to get into the physician!
```

### [23] hash=`99df45aec84e8ab8`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
Did you do this, Octavia?You couldn't face the burning truth of his words,so you pierced his very heart instead!Just as he was blazing with the fire of justice!Or was it you, Jailer?Did you intend to crush the voice of poetry beneath your wheel of power?It has to be one of you!Devils in disguise!Beasts and human skin!Can't you see?I had nothing to do with this.I'm as innocent as any of you.I've been trying to keep order here, to protect everyone.
```

### [24] hash=`7c38aab1cd7d18ca`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
And now you blame me?Don't listen to her!The idealist made it very clear!She's trying to get us punished for her own gain!You're a murderer, Octavia!This is mad.You're accusing me without proof.It wasn't me.Just as I thought.You had it all along.Standing around for?Can't you see Julio is hurting himself?It's Mr.Julio.He's hurt.Bleeding.Sounds like he's having an epileptic seizure.Perhaps I could offer some help.
```

### [25] hash=`334b81e8a2b2557d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p7`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（07激情与谵妄）

```text
Please, Miss Octavia, help me so I can help him.Flashing lights could worsen an epileptic seizure.Seem experienced.Was it a major part of your responsibility since San Paolo?You're well prepared for your vision and ambition, for modesty is such an essentialpart of writing, and you've just demonstrated a skillful use of introspection.Thank you for your kind words.Foolish to think that ideas alone could ease people's pain.

Why?Puzzles on top of puzzles.Questions after questions.My head can't do this anymore.
```

### [26] hash=`6e338599ec71b0ad`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
Ladies I must apologize for what happened back thereWe were caught off guard.There has never been a commotion of that scale before I must report this to the physicianDon't worry.Miss Jailer.We made it out in one pieceThank you for your understandingOrdinarily, I put a wrench to score you to a safer locationBut I'm afraid at this hour you'll have missed the last train and the roads are icy at night
```

### [27] hash=`53abcb4a4b2f7ff8`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
Brennan, we can't leave like this.We appreciate your kind consideration, Miss Jayla.But we still have some unfinished business here.I see.I'll arrange a clean room in a safer section for you.We'll do our best to ensure your safety tonight.Julie found us a spare room.Bleak, quiet, and somber.It's a cell like all the others.Don't worry.This isn't the first time we've ended up on the wrong side of the bars.
```

### [28] hash=`cae8d845aac8390d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
But we're still in an Arcanus prison.A place where conflicts and violence can erupt at any moment.Let's not forget that.Ms.Jailer warned us from the start.These prisoners are mentally unstable and potentially dangerous.Ms.Recoleta, with all due respect, we can't afford to see this place through rose-colored glasses.We'd be overlooking the risks, as we did earlier.El auge y la caída de la cordura.We're no strangers to wild guesses, and sometimes they're closer to the truth than you'd think.
```

### [29] hash=`8decd2c28375603e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
So this...the rise and fall of sanity.Sorry.What exactly is your story about?Nunca pensé que te interesaría.It starts...sorry, it's been a while since I told it from the beginning.A few...a few years ago, I worked...worked as a forest ranger.It happened in a desert town called Amalfitano, in Sonora, back in 1975.You know what?Most people say the beginning is a bit hard to get into, except for Aleph.
```

### [30] hash=`629ba8546f587d94`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
I'm thinking of rewriting it, but if you like the sound of it so far, maybe I couldread you the latest part I just finished?Please.Todo empezó con los datos de frecuencia de las cintas.El patrón general parecía haber cambiado.Al principio, la investigadora de paracausalidad lo atribuyó a un error estadístico.Un fallo, tal vez.Oh, sorry.But after a few days and long nights of meticulous calculations,
```

### [31] hash=`76e8d141a1097b6e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
that explanation only became less and less plausible.The odds of success and failure kept shifting.Then the morning light dimmed and died.That was the last time I saw the sun.My own hands were the threats I worked with.The second time I heard the die roll, I was told the oxen in the fields sank to theirknees and never stood again.By the third roll, the fields were crawling with frogs.Plows ran over them, and some still riot, squeezing themselves deeper into the cracks
```

### [32] hash=`714205ea6ff40d05`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
in the earth.The fourth time the die rolled, ten dormice plunged into the sea in a strange sleepwalk,and ten bears feasted for the last time before winter arrived.The final roll of the die was cast in a cage during a duel, before a crowd of eager eyes.The winner left with ten pounds of gold, and the loser left with ten flies, which fell on him to feast.Sorry.Still, it's a beautiful story.Sad, but beautiful.
```

### [33] hash=`091b7fa4a4a1a0ba`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
The story is still too obscure, isn't it?Aleph warned me about this.In her last correspondence,he suggested adding the blind weaver to shed light on the hidden theme.It helped at first,but even with a sage advice, no matter how hard I tried, the plot just didn't seem to move forward.Déjà vu is a single moment, a specific situation, but here it's…everything.La sociedad, the rules, the idealist, even the incidents in the gallery.
```

### [34] hash=`769dd14ad1ef3d2c`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
Each one unfolds in a similar pattern, like the grooves on a record, telling a storyI feel I've listened to before.Amalfitano and Comala.They're two sides of that same record, playing out the same tune.Whatever happens in my story seems to be happening here too.I had that feeling when I met you as well, Miss Burton.At first I thought it was only an interesting coincidence.You're much like the first character in my story.
```

### [35] hash=`fe28d9a42121a5f6`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
A traveler with a suitcase.Then I realized, the doctor, your Doris.She's like the blind weaver who lost her sight to the dye despite having always been faithful to it.And the jailer, she's the bank clerk who assisted the corporation in taking over the town in order to escape her past.And the idealist, he's the murdered donkey driver, and the die of Babylon.No, mis queridos amigos ficticios, que rayos les está pasando?
```

### [36] hash=`8da3d1be64c32797`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
Wait, are you saying that everyone we've met here matches a character from your story?Like, some kind of archetype?Why?Why would he do this?I don't see any reason why he'd be connected.He's an intelligent, cultured, and profound person, not a common killer.No, none of this adds up.Remember, Dr.Doris was brought to Ushuaia by the Xeno Rebels, and we know they're connectedto Manus Vindicte.If this Aleph really is hiding Doris from us, he may be working with them.
```

### [37] hash=`5300b461e608c306`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p8`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（08蛛丝网）

```text
Soneto, I didn't know you had such a flair for stories.Maybe you should join us and become a visceral realist too.I think you're only imagining things.Perhaps you were inspired by this strange prison?Ha ha, perhaps we all need to start writing our own stories.Come out now.Whoever's out there, speak up.How can we help you?My responsibility.
```

### [38] hash=`0437f0fc2132904e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
I come here out of goodwill, believe me, I didn't want any bloodshed either.I understand you just arrived today, there's something you need to know about the inmateshere.We are outcasts, rejected by society and literature, and our privileges are limitedwithin these walls.But before I started my own literature group, I struck a deal with the Panopticon authorities.And what has it changed?Garcia, you're the latest inmate here.
```

### [39] hash=`e6cc3b460efc0079`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
Tell us.Three months ago, before they arrested you and took you here,what has the visceral realism movement accomplished out there?First, it was revolutionary.Young poets joined in droves.We held gatherings.And the literary world seemed alive again.I was just a kid when the leading poets left the city.everyone thought it was only temporary but they didn't come back and nothinghas happened since no one says it but we all know bestural realism died in 1977
```

### [40] hash=`b8dc2ecb84596c5d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
no not for me it's not dead as long as people still believe in it I believe init belief faith what is this obsession with the true self why does your typealways insist on there being a true self hiding beneath our roles in society our disciplines lookat the idealist he never once stopped fighting for what he believed in even long after he was putbehind these bars idealist what a name he gave himself who will he be when he finally breaks
```

### [41] hash=`8aba0c6285bd917f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
free from the eyes of the central tower when he's left without his willful audience and nobodyThe physician told me the horrifying truth about the Panopticon of Kamala and the power behind it.Manasvindicte.By becoming the Panopticon's sole patron, they seized control of the resources and the allocation system,turning this place into a living hell.I suspect that the physician, the current highest authority here, is responsible for this situation.
```

### [42] hash=`f5a1ce903ac3496e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
I discovered that the inmates were put through brutal training,Even when they were too sick to carry out their tasks, they also forced pure-blood Arcanist inmates to wear their masks, effectively turning them into murmuring puppets.Just as we suspected, Manus Vendictae is orchestrating everything.No wonder we didn't find them in the city, they've been hiding here all along.No one would have thought to come looking for them here.
```

### [43] hash=`434321dcb0964ea2`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
Why would Miss Octavia bring this to us?What's in it for her?No, Aleph is like a mirror.He reflects both light and shadow.But Octavia, maybe she hasn't looked at the shadow within for a long time.I know that look on her face.It's the look of a writer.I've seen so many like her during my trip.The faces of a lost, struggling generation.Dr.Merlin, I'm here to report on today's events.Come in.There was a commotion in the gallery today, sir.
```

### [44] hash=`7fc6f74ce9cda79e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
An inmate known as the Idealist was severely injured.The inmates nearby said he lost consciousness from blood loss.However, after we put everyone back in their cell, the Idealist was gone.I made a sweep of the grounds, but there was no trace of him.It's possible that he regained consciousness and went into hiding.I'll perform a full search tomorrow.No need.There is another thing.Two guests from the Foundation came through today.
```

### [45] hash=`a7791fbbccc0d1e1`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
They said theywere looking for someone named Doris.They've shown a willingness to cooperate, thoughthey were involved with the incident in Corridor Zero.Sir, there is one more thing.I told Ms.Octavia we're sure on rations, and she'sadjusted the inmates' portions accordingly, but that won't last long.Manus Ventikte stopped providing supplies back in March, and Sino has collected all the prisoners they had previously placed in our custody.
```

### [46] hash=`7264f85daa7f8271`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
I just wonder why they have so suddenly withdrawn from Ushuaia and brought all the prisoners with them.I also noticed that we haven't received any orders from the government since Warden Tartuffe was transferred.In fact, we haven't had any communication with them at all.Sir, in frank terms, we're facing down a serious shortage of medicine, food, and basic supplies.At this rate, the Panopticon will soon be unable to operate.
```

### [47] hash=`ea00a688147c0cdc`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
Where will our inmates go then?Can we ask the Foundation for help?They've sent their people here, maybe they're interested in the Panopticon?I could arrange a meeting if you like.You're unusually talkative today.Pardon, sir?That's fascinating, you know.You're too soft on him, Aleph.Look at the mess he has us in now.Calm down.He's a rabble-rousing thief, a self-destructive maniac, a snake in the grass.
```

### [48] hash=`3281644004dc8338`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p9`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（09全景中央）

```text
He even stole the teardrop of Kamala from me.He's nearly ruined everything we've worked for.It's only a die, Merlin.It does nothing more than a die can do.You were there today.You saw what he did.He managed to change the Panopticon with this die, even if only for a second.that we have found the path to the ultimate answer.
```

### [49] hash=`057e9c24f243bca1`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p10`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（10.一面又一面(噢，这对于唱片的坏影响远甚于磁带)）

```text
Ms.Simone, did you just say something about the Foundation?Are we not moving off topic?We were discussing our efforts to identify substances immune to the storm.What is all this about the Foundation?No idea, but it's sure to be the most cheerful, positive, wonderful news.That'll teach you to run Madame Buckethead out of town.Now it's going to be those Foundation dimwits calling the shots.Ha!I won't stand for the Foundation ordering Laplace around.
```

### [50] hash=`d03c8b6dbcf003d7`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p10`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（10.一面又一面(噢，这对于唱片的坏影响远甚于磁带)）

```text
I'll set things straight with them later.You have my word.In fact, Miss Simone, you may relay my message now.I understand your concerns, Mr.Enigma, but given our present circumstances, theFoundation's involvement may have a bright side.The resolution the Foundation relayed to me was principally concerned with your artificialstorm project, Mr.Ulrich.Did you switch gears on us, Ulric?For Flux's sake!
```

### [51] hash=`bc31507a58853c8c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p10`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（10.一面又一面(噢，这对于唱片的坏影响远甚于磁带)）

```text
All I did was ask for a little support.Speaking of, the Foundation also sent through their approval for your other requests.Mostly anyway.They agreed to supply the majority of your requested materials, including replenishing a portion of our asymmetrical nuclide R,and they've dispatched field investigators to assist us.Additionally, they've done preliminary screenings on the locations you mentioned, and confirmed
```

### [52] hash=`be699e33a8507c1b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p10`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（10.一面又一面(噢，这对于唱片的坏影响远甚于磁带)）

```text
they meet the specifications of our experiments.The Foundation has never been this generous with us before.Don't go popping the champagne just yet Ulrich!Our new bosses aren't going to come anywhere close to replacing all the asymmetricalNuclide R you've wasted!Still it's all too easy.What's the catch?Drastic times call for drastic measures.I hope you'll find it in your heart to forgive us, Regulus.
```

### [53] hash=`ac73d176de6662ee`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
But instead, after interacting with the people here...Atootoo, my dear.There's no shame in having second thoughts.How could you not?This was but your first glimpse of a world so much wider than you knew.But you'll soon realize that it is nothing more than a dying corpse, its lungs still clinging on to its last breath.The face rots first, you know.It's a nasty scene, I assure you.Those shrinking, putrefying eyeballs are always a headache for taxidermists.
```

### [54] hash=`12d863328bcf92a3`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Next, the chest cavity.It rots out from the inside,bloating with noxious gasses produced by its decomposing flesh,until it's ready to pop like a party balloon.Even at this stage, if you were to hold your breath and look only to the limbs,you might marvel at the artisanship.Such a perfect creation.Yet it dies all the same.So it goes.Do you see the world any clearer now?Take your time, think it through.
```

### [55] hash=`13f121b782078006`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Hmm, outsiders are different from what I expected.Ms.Grace, are you sure they're truly evil?I've even been known to engage in eavesdropping.Ms.Grace?You, Barcarola?Barcarola, what a pleasure to see you.All over the ship for you to thank you for the lamps you made.This is a funny way of saying you're welcome.You're rude astunating criminals!Someone for saying thanks!Ramona?Really not what matters here.
```

### [56] hash=`fc1c1079e5debace`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Please ladies, this was only a small misunderstanding, wasn't it?As both your captain and your friend, I hope that you might be able to resolve this.I do believe I could see you two becoming fast friends.But Tutu here is eager to learn about the outside world.And I'm sure you must have many stories to share, don't you?Consider it a favor.in exchange for those Seamothers' eyes.Um, why don't you take a seat, Miss Barcarola?
```

### [57] hash=`9ead90aae317dfa5`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
You're quick to gloss over your hometown.Cremona, wasn't it?Cremona, the City of Islands, as they say.See, I was born in that awful, dreary old place.But I don't like to talk about it, Miss Grace.Hmm, but it sounds like you still miss your home.So why speak of it that way?Is there something wrong with it?In Nikitaiao, when we find something rotted in our village,we wrap it up in stinky grass and throw it in the ocean.
```

### [58] hash=`05d157515168a565`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Do you outsiders not do this as well?Well, it's not completely rotted exactly.It's just...Ramona, everything is bound up with the violin.How it's made, how it's played, even the science of it.It fills the air in every conversation.You can't walk to the Trattoria without tripping over a Vergioso.They come from Rome, Berlin, London, New York, Nairobi, Tokyo, Uppsala, people from far andwide all crammed into one town.
```

### [59] hash=`a1e44db6bcd1cf45`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Not a day goes by without a concert, a symphony, or a festival musicale.Am I misunderstanding you?Because to the Nukatai, the idea of a place with music and festivals every dayIt sounds very...fun.That's where you're wrong, signora.It's no fun at all.At least, for me.To be Cremonese is to take pride in its music,its history,and above all, its violins.And you must learn to love the violin,the viola, the violoncello,
```

### [60] hash=`8077223248ad4140`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
and the bass.Because there is nothing else.Every quartet is a string quartet.Every concerto is Vivaldi.Strings, strings, strings.The monotony is unbearable.The world has so very many instruments as diverse and as varied as the people that fill it.Even the shell around your neck could sing if you knew just where to tap it.But not in Cremona.That's why I speak of it that way for Tutu.Because, if I had stayed there, I would never have seen the music of the world and its instruments,
```

### [61] hash=`5406d4bf40dddfac`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
and my crackling box would never have been able to know their sounds.The Nukatai don't have many instruments, not so many as you anyway, but we were never bored with what we had.I'm certain that your island holds great beauty beyond its music.If ever we grow tired of singing and dancing, we'd go searching for shells or swimming in the reefs.How could it not be?You are the very star of the free breeze.
```

### [62] hash=`bdf1f2fb05620e44`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Uh-huh.What about you, Miss Grace?You've never told us about your home.It's a place of little interest to anyone.Not even worthy of naming.They say a musician must be free of attachments to be truly creative.Perhaps this is true of captains as well.No, that can't be right!The New Gutai believe that to stray from our home is the death of the spirit.If we travel too far and too long, our spirit shells develop cracks that no amount of Nuka
```

### [63] hash=`9b1bc9b1ff0cbc75`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p11`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（11.我可恨的乡土啊(永远！永远——)）

```text
Glue can mend.And from these cracks come an intense sadness.The elders call it homesick.Homesickness?See, we have this word as well.The sailors aboard often ask me to play the songs of their youth when they'remissing their homes.So many different melodies.Mama Mia the concert you're a regular so rock-and-roll concert, but I haven't even asked her what instruments she needsThank you for talking with us miss grace

Don't mention it.I only hope that it was helpful for you.I have one last question.I was wonderingHow do you stay so?determined
```

### [64] hash=`19b072d11cb2aa2b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p12`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（12.三个音乐家(歌剧院，电台，以及······锯木厂。)）

```text
I haven't even found the power socket yet timekeeper those sounds are familiar aren't they?metallic percussion soundssprinkled with screams of painIt's manas vindictee this time.Don't worry signora regulus.I won't let them disturb your rock partyYou oh fish barnacles are ruining the atmosphere and scaring our gasI very much doubt you're doing this with the approval of Captain GraceAnd as such, as our musical director, I have some authority over them.
```

### [65] hash=`981b4d6b7cab0aff`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p12`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（12.三个音乐家(歌剧院，电台，以及······锯木厂。)）

```text
Moreover, it is my duty to ensure all our guests have a safe and enjoyable stay.Now I see how the manas kept themselves hidden.That barcarola?What's she doing over there?If you've come to be entertained or perhaps for some music lessons,I would be more than happy to assist you in the crew quarters later.However, your musical talents will not be needed at this time, as we already have a scheduled performance.
```

### [66] hash=`ab5c39090dfb9ea5`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p12`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（12.三个音乐家(歌剧院，电台，以及······锯木厂。)）

```text
Do you have any requests?My next performance?First thing!Well, what's happening?Why are they acting crazy?As the musical director of The Free Breeze, can't allow you to harm our guests.Enough of your nonsense, foolish outsider.What are you doing, Fududu?That is an outsider.Have you forgotten your duty to your people?No, but this is not defending our home, and it doesn't feel like avenging it either

What we suffered was not these people's fault.There has to be a better solution to all thisIsn't our way it isn't right for tutu.We have no choice
```

### [67] hash=`d8fcdad005d5b17f`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
We should raise a toast, one and all.For we're in luck's good graces to be aboard this ship.A ship?Hmm...Perhaps one ought to think of it more as an art.Just what are you getting at?Oh, I get it.Is this some kind of surprise theme party, like a murder mystery?Is that right, Miss Barcarola?No.I didn't plan for any of this.You aren't entirely wrong, though, Mr.Matthews.For this is certainly a surprise, if not so much a party as a ceremony.
```

### [68] hash=`df0cedcc1407fea1`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
Allow me to congratulate you, our honored guests.Each of you with your unique talents, resources, and powerful connectionshave earned a chance to join Manus Vindictae.If this is some kind of joke, Captain, I don't find it funny.So how about you knock it off?There's no joke at all, unless you plan on throwing away your precious opportunity to join us in the new era.What the hell is that supposed to mean?
```

### [69] hash=`d155ab0aa12e6008`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
Have you gone insane?How dare you blaspheme our savior?Toa, ever since you put on that mask, you've been acting strangely, like a different person.You're wrong, Salone.I was lost after we left Mellie, but now I've never felt so certain of myself.You must ready yourself for the mask trial, too.We must all be willing to sacrifice to bring our people into the new era.As for these ignorant outsiders,they will never understand the depths of the crimes they've committed
```

### [70] hash=`d7d86db9f968fc43`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
or the punishment they deserve.Calm down, Toa.Don't bother with these outsiders.They only care about themselves.Only the storm can bring the change we need.The Free Breeze is equipped with a double hull and the most advanced communication systemsavailable, capable of contacting rescue and support under any circumstances.Yeah, and something about its stabilizing system.Why should we be worried about some heavy weather?
```

### [71] hash=`605b9b38306ae674`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
Or were you lying to us?Oh, the specifications of the ship are all very much true.No natural weather of non-non could endanger us here.However, the storm I speak of is not a mere matter of churning wind and thunder, and no double hull, nor stabilizing system, could stand against it.So, what the hell is this storm?It is a cleansing.A deluge that will come to eradicate all the sickness of this world.
```

### [72] hash=`2ae03e0de1908a70`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
And an opportunity.A chance to reverse our course.All that is asked of you is an insignificant price.Reverse?Price?What are you talking about?In the 90s, veins turned into wires.In the 80s, skulls turned into geometric shapes.Oh, in the 60s.What fun we had then.The entire world became a pop art spectacle.And Manus Vindicte have seen us through each one.For all these many years.So, you're saying that the world is going to be transformed?
```

### [73] hash=`588f57fb41617713`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
Something weird will happen to our bodies too?You are exactly right.And the Manus were behind all of this?Why?Don't be so harsh on us.We've made heroic efforts to cleanse this world of its sickness.But each generation keeps making the same mistakes.Economic collapse.Environmental crisis.Endless wars and bloodshed.We had no choice.The wounds of this world must be cleansed.One deluge at a time.Now we are welcoming the new storm.
```

### [74] hash=`107eeffedbcef227`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
One that will reverse us to an even more distant past.You're a lunatic, Captain!You need your head examined!Lady, you need a psychiatrist!These things you're showing us, they really happened?Take my word for it, you will all bear witness to it soon.It's coming!We are from the St.Pavlov Foundation,an organization dedicated to the protection and rights of humans and arcanists.Oh, thank goodness!As the timekeeper of the Saint Pavlov Foundation, I can assure you,
```

### [75] hash=`c808a5ba529ee51e`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
what she showed you won't happen here.Manus Vindicte are just trying to manipulate you into buying into their deception and hatred.Don't give in to this false fear.Please, everyone, remain calm.Protect us?You?Don't make me laugh!Oh, wait!She seems trustworthy.Be careful timekeeper.They're coming for usAim and shootNo, this isn't right.I think you need some rest sisterI'm sorry for tutu this needs to be done a fine speech miss Burton such
```

### [76] hash=`47b5f67de82e70df`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p13`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（13.太阳之死(一座漆黑的城市，包裹在风暴、雨水与仇恨中。)）

```text
delectable righteous indignationSurrender miss grace your lies will not succeed hereWhy, of course.To tell a lie brings the harshest of consequences.Even a kindergartner knows that.Everyone, whenever there's an imminent storm, my watch here starts a countdown.But there have been no signs of...A coincidence, Miss Burton.I so happen to have a similar device myself.Three.Possible.As you said, lies will not succeed here.

The question is, who here is the liar?Ladies and gentlemen, I invite you to relish the sight before you.Here we are, just evening on Earth.
```

### [77] hash=`43e1332ec73f951a`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
Who's calling?Regulus?Calling to check on the artificial storm project, are you?I still have a way to go.I'll call you when I need a hand or two.Topside, you fabulous fish tank!There's a gang of Manus thugs here!The Manus?Ah, they're sure to be a considerable amount of nuclide within their masks.Perhaps I don't need this unreliable scrap of metal after all.Send me your location straight away, Regulus!
```

### [78] hash=`e4f77fc874d01792`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
Where are these Manus thugs?Does Laplace possess any technology that could detect an imminent storm?We made several attempts to do so in the aftermath of the second storm, but none of them proved effective.Since that time, we've become reliant on the storm alerts from the Foundation, or more specifically, from you, Timekeeper.Miss Grace claimed that the storm was coming, and she managed to accurately predict the occurrence of the anomaly outside.
```

### [79] hash=`587547a08aa9dd30`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
precursors to the storm everyone listen we have to stay calm ask you to put yourfaith in me and in the free breeze I should have never come to this party toget these people's attention some public services on the free breeze willbe temporarily suspended we apologize for any now entering an area oftreacherous reef during this time there may be some sharp shifts inIn order that we might reach the new era as soon as possible, the Free Breeze will forge ahead at full speed.
```

### [80] hash=`9b0d539e7c35c564`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
Please stay indoors and in case of emergency, hold on to the handrails.I repeat, please stay indoors and hold on to the handrails.Ingrace, why in the world is the Free Breeze going full speed through these reefs?To embrace the future.What if we strike any of these reefs?The damage could be catastrophic.not as catastrophic as missing our chance to embrace the storm I won't standfor this you're just trying to scare us into joining your cult I'll bet there's
```

### [81] hash=`8d9c1b87dde5ba9c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
no reef no storm at all this is trickery and I intend to prove it do asyou wish sir please watch your footing the wind is howling outsideMy arm is a bolt!Miss Grace, you murdered that man.What an utterly baffling accusation.Have I shot him, stabbed him?No, the choice was always in his own hands, wasn't it?Captain, you said you'd save usif we joined Manus Vindictae, right?Not as simple as that, I'm afraid, but relax.
```

### [82] hash=`465e9e0a093cf64f`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
There is only a small trial to pass.Then the new era awaits.You may feel a little disoriented, but your body will be in no danger.So, if we all put on these masks, then this nightmare will be over?Get any firsts than they are now, Kenzie!Give me the mask!Oh, this will be the bravest leap you've ever taken.Please everyone, for you salvation, but slavery!Don't give up your free will!Listen to her!We've got to be free to choose for ourselves!
```

### [83] hash=`6ced826ed1a03b95`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
Oh guys, do you really want to plaster one of those things on your face?You'll never be able to eat again or listen to music.Blimey!What kind of life would that be?Don't waste your breath on these lap dogs.They're all bark and they'll fight!Each moment, now night.Civilians have calmed down, Timekeeper.Take a moment.I'll deal with the rest.No, Senato.This crisis is far from over.Good grief.How many passengers are on this bloody thing?
```

### [84] hash=`c0cbea0b86f60df1`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
I will pray for you.Sorry.Put on the mask!Thank you, Miss Grace!It hurts!It hurts so much!Let more of these people give in to their fears.These stubborn outsiders must be silenced.Take them away!Let our revenge begin with them!We're Nuka Teow!Thelonica, take my troubled sister back to her room.The softness of her heart has clouded her judgment, just as her shell shows.It's waiting for you at home.
```

### [85] hash=`548f8eb52b332c4a`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
We'll be there soon.Just put this on.We'll be there soon.I don't believe your job description permits you to interrupt our guests, does it, Ms.Barcarilla?I don't understand, Captain Grace.Why are you letting this happen?Why are you doing this?Cheer up, dear girl.Hold that chin up high.Now that's the spirit.The brightest star of the Free Breeze forever and always.Just take a look.Your loyal fans are waiting for your next show.
```

### [86] hash=`0264db1d97844569`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
Won't you play some of those beautiful melodies for them again?But Miss Grace, what do you mean by the storm, and diseases of the world, and this new era?Oh, it's all so much simpler than you think, Miss Barcarola.All that you hated in this time will vanish.As if it had never been there at all.The city of violins you swore you'd never return to will soon be forgotten.Washed away in the coming storm.
```

### [87] hash=`183425bf2d8e29ff`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p14`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（14.紧急通讯(一个好消息，与许多个坏消息。)）

```text
Your wish will come true.You'll never need to return to it.You couldn't, even if you tried.Again?Is it you said about the Knee of Sound?The disappointment of those old fossils and their little worlds?Is that right?Yes.I said I never, never wanted to go back.Now, keep your hands steady this time, my dear.You must be certain.
```

### [88] hash=`f9811d16d46ae153`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p15`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（15.海风儿在翻阅(是的，好孩子，那儿从不曾令你辗转反侧，牵肠挂肚。)）

```text
I don't know, Toa.I trust in Kamutsu's leadership, but still...Just like always, you're waiting for everyone else to test the water before you jump.I...I just feel that there's something wrong.You say you're not afraid, Toa, but I hear your chains clinking.You're shaking too.Shut up.That's only because we're in a freezer.are ours to deal with so don't get any ideas.What?Baccarola!Don't tell me you're siding
```

### [89] hash=`3845ddde3bbf4fc9`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p15`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（15.海风儿在翻阅(是的，好孩子，那儿从不曾令你辗转反侧，牵肠挂肚。)）

```text
with these tone-deaf goons!I'm just confused.It seems like there's only one way forwardbut the captain said that only those who put on the mask have a chance to survivethe storm, and that everyone else, the unbelievers, the forsaken, will vanish.Ms.Furtin, tell me the truth, please.What will happen if I put it on?If I reach thisbeautiful new era Ms.Grace speaks of, what will happen to Cremona, the streets,
```

### [90] hash=`6109f740c3c3196b`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p15`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（15.海风儿在翻阅(是的，好孩子，那儿从不曾令你辗转反侧，牵肠挂肚。)）

```text
To follow their divine guidance, we must be willing to renounce both body and mind.See the despair in their eyes when they fall flat on their toes lost in our latest failure.Yes, the awakened ferrofluid sample named Ulric, one of the major contributors to the creation of the Equilibrium Umbrella.The ritual materials are nearly assembled, and we are accelerating our recruitment.
```

### [91] hash=`aed85886a90a3271`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p16`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（16.意大利之歌(船桨是在这儿打磨的，浪花是从这儿扑腾的。并不是每阵风儿都追寻永存。)）

```text
I've been recording the Free Breeze's heading since it left Sydney, thoughunfortunately something has been jamming our signal.Yet we can stillextrapolate from my earlier readings that this ship is not heading to itsadvertised destination.It's heading steadily southward.It appears so.Forecast of the storm, the sudden eclipse, the mask trials, and theat which the free breeze is now heading.If all they wanted was to recruit more followers,
```

### [92] hash=`f12f0c60253c860c`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p16`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（16.意大利之歌(船桨是在这儿打磨的，浪花是从这儿扑腾的。并不是每阵风儿都追寻永存。)）

```text
they would allow for more time to convince the others.However, if the storm is indeed coming,then why would we be racing forward through these reefs?Their actions don't seem to be aimed atrecruiting, nor at passing through the storm.Rather, they seem to be aimed at intimidation.This would add weight to the possibility that the storm they're promising is only a trick to inspire more fear.That said, we must consider the chance of the storm occurring, no matter how slim it may seem.
```

### [93] hash=`514fe9a392945523`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p16`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（16.意大利之歌(船桨是在这儿打磨的，浪花是从这儿扑腾的。并不是每阵风儿都追寻永存。)）

```text
Until the truth is ultimately revealed, all we can rely on are the instruments in our hands and the readings before our eyes.Then we are agreed, Mr.Ulrich.Whether the storm is coming or not, we need to be well prepared.Irrespective of your concerns, thanks to those oily heads and their quirky masks, I have acquired more than enough asymmetrical nuclite R to perform the immutability experiments.But have you considered the side effects, Mr.
```

### [94] hash=`bc897e9341c06afb`

- lang：`en`｜version：`2.4`｜arc：`地球上最后的夜晚`
- doc：`BV19Mq8YzExh_p16`
- title：《重返未来：1999》2.4版本「地球上最后的夜晚」全剧情 - Reverse: 1999｜4K（16.意大利之歌(船桨是在这儿打磨的，浪花是从这儿扑腾的。并不是每阵风儿都追寻永存。)）

```text
Ulrich?It's true.There is the risk of unavoidable side effects the experiments pose.And I admit that, if I were in the lab, we would use much more time and caution.And only those who put on a Manus Bendicte mask and pass its trial can reach the new era with her.I'm sorry, what?That you just turned your old friend Charlie's brain into a knot.Where are we going then?There's no telling where or even when we'll end up.
```

