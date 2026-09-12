# 剧情图谱抽取 · batch 032

- 角色：`wu_ming_zhe`
- 批次：**32** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.4」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_032.jsonl`

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

### [0] hash=`36d0964b4c01ceba`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
She believedthey would only become another military squad of the Foundations.Darling, maths are beautiful for their uselessness.That's why it remains noble and gracefulin this sordid world, despite you humans' reckless action of using it to calculate ballistic.She turned down my invitation and left an unfairly negative comment on our storm observationproject.The observation stations you built are destined to be toppled because their basis is the
```

### [1] hash=`33c5f1b415809685`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
fragile world that follows the laws of physics.The efforts you've made are like nails on a sand beach, which will only be carriedaway by the next tidal wave.But I said, perhaps our efforts are in vain, but someone has to do it.We will try every corner of the beach before making the conclusions that the world we areliving in is already a hopeless ruin.What a pragmatic, rigorous, and rational speech.
```

### [2] hash=`f14b80b2ee013702`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
But dear, the world is a hopeless ruin.The conversation ended in disagreement.I don't know why Arcanists hate the world so much.Perhaps the reason is they have never been truly accepted.To this day I still remember her venomous conclusion.The world built on past experiences has ended.In your words, which you used to mock us,why not embrace the reality?Yet about the Gnosis which she deeply believed in
```

### [3] hash=`d612f715b5b75bb3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
and the so-called prophecies she made through numbers,she had never given any proofs or details that showed rigorous logic.And the reason for her inactions was...was an oath she had made before some stone?Therefore I believed her words were only the nonsense of a lunatic.When we first met I thought she was different from all those psychos,who mistook the malfunction of their prefrontal cortex as the will of God.
```

### [4] hash=`263476a6f6faecae`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
But they turned out to be the same.In the name of human sense, I swore everything she said was absurd and ridiculous to me, until...Don't worry, Ms.Bourniche, I'm familiar with this situation.Every time, after the brave Typhon defeats Jupiter, he returns to the auto-island.But each time we twist the ear of Mr.Glassbox, Typhon will show up again and again.Ms.Moisson told me the ear is the key to bringing back our hope.
```

### [5] hash=`1b48c25f47f1a509`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Wait, don't tell me you are talking about the shows on the mechanical television?Now it's time for the great Matilda to show a little bit of her greatness.Judging from the omen, it's at the northwest, the beginning and the ending of the ring,where the wall reflects repeatedly.Northwest of SPTM, this one is straightforward.The beginning and the ending of the ring is not a problem either.The icon of the computing center is exactly the Ouroboros,
```

### [6] hash=`cf4a1d0a0d4be0c1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
A serpent eating its own tail.Here we are.But where the wall reflects repeatedly, does that mean a closed room with mirrors?The mirror in the display center is a huge kinescope in the wall.And the one in the airtight laboratory is a crystal clear observation window.The one in the rehab center?No, no, no.The mirrors in the operation room have been replaced with birthed electronic screens of steel structure after that xenopilot made a scene.
```

### [7] hash=`ca0b730003d60c3e`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
So, where is the answer?Didn't you apologize?Where did you come from, dork?Wasting my time?That gentleman doesn't look well.He's covering his face.Nose is running with purple liquid.What a beginner, but still, it was too weird!The members with caution and patience triggered Arathlattus at the right time.Covertina won a victory, not Boratio!He just read the map on the canter.You mentioned where the wall reflects repeatedly.
```

### [8] hash=`cc3bd1999eefda55`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Refer to the racquetball center here.You see, its icon is a bouncing ball.We take a look.Found it!Please, a right direction.Next, boxes, glasswares and copper pieces.Looks like our destination has piles of metal.Good job, Assistant Sotheby.To say I might have gone a bit too hard on you.You are more capable than I thought.Thanks to your prompt reminder, we have saved quite some time.Sotheby is glad to help.
```

### [9] hash=`8b2f2513e7709ad7`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Uniche, since you're such a talented diviner,Why don't you just divine the reason for the storm with your inherited arcane immobility?According to Ms.Moissan, the reason still remains a mystery.If the Crystal Orb can reveal its truths, everything will be much easier for Vertinand her team.And the reason for the storm?Possible for sure!It's a typical mistake of laymen to believe one can see everything's for divination.
```

### [10] hash=`6424768d168b2615`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
You are an expert on potions and arcane creatures, but you have little knowledge on other subjects.Haven't you received any systematic education on Arcanum?Education on Arcanum?I'm of course well educated in Arcanum, with Ms.Moissot as my tutor,and my arcane friends such as Typhon from the auto island, Jupiter and...You've understood the fact that the education you have received is not......systematical.
```

### [11] hash=`dd65d421ff527ed7`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Or say, incomplete, imperfect, inelegant.But don't worry, because you are talking to the kind-hearted Mathilda.She will spend her valuable time to make it up for you.Some of our quantum knowledge is not completely separated from that of human science.For example, the modern pharmacy and chemistry actually originated from the experiments of portions and alchemy in the ancient times.They developed into two different systems because arcanists focused more on the knowledge
```

### [12] hash=`82b57eaae2aca62b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
ignored by scientists, which is Gnossis.The knowledge we learn from divination is exactly under this category.Let me fill you in with more details.If two human researchers test Snell's Law at two different places at the same timewithout making any mistakes, they will always reach the same conclusion.Or if two potionists use the same ingredients and follow the same formula to make the cough-cough stop-stop potion separately, their products will also have similar effects.
```

### [13] hash=`c5c893c19e1d1412`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
However, if two diviners respectively perform divination on the same thing, they will probably see totally different visions.Because what the divination shows is merely omens.The interpretation of these omens is in fact a kind of subjective deduction based on the reality.And there is no such thing as a standard answer.If the two diviners draw the same conclusion,it is more of a coincidence than a result that implies generalizability.
```

### [14] hash=`e4728f19542668f6`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
So, diviners never check the accuracy of their divination through the review of peers.And this is an example of Gnosis.Unlike human sense, it is unique and possesses no universality.In other words, even if someone finds out a reason for the storm through divination,they can't have other diviners verify it, because a hundred different diviners will give out a hundred different conclusions.The scene will be even busier than a concert at Musique Verraille.
```

### [15] hash=`3ed87bbc12eafda1`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Being said, the more possible result we get from the divination is nothing.Divination cannot bring knowledge which the diviners have never learned.The divination of such world-class knowledge, as complicated as the reason for the storm, can only be performed by world-class diviners.We may find one or two diviners like that if time continues to be reversed, like Nostradamus.Hmm, but he lived in the 16th century.
```

### [16] hash=`99fe18357101404d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Besides, if Nostradamus is not always right, then most boonish is.Thanks to your divination, we're getting closer and closer to that report, right?You, you, you are right!Finding items, interpreting dreams and making simple prophecies.All these things are just a breeze for the bright and clever Matilda!But inquiring about the storm is beyond my ability and it will only bring misfortune.I will never make such a stupid mistake.
```

### [17] hash=`ce58cddc20098883`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
In fact, staff of the report and the handwriting of the author are perfect divination media.Besides, our target is not far away from us, and I'm familiar with the surroundings,which have made things much easier than usual.It is true diviners can improve the accuracy and controllability of their gnosisby practicing repeatedly, walking the rituals properly, and making targeted preparations.But that still doesn't mean the result will be absolutely accurate!
```

### [18] hash=`9ca2030198e02022`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Person who mentioned the School of Numbers claimed she was enlightened about the year of the next storm.So by deflation?I'm not sure what kind of arcane skills they used, but numbers are indeed a kind of omen too.I am not talking about the specific knowledge of mathematics, but the numbers themselves,because they are even more abstract than images and languages as kind of symbol.Even so, there is no way for us to verify this prophet, unless it really comes true.
```

### [19] hash=`d67f82d912122aaa`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
That is also why it takes almost nothing to spread a prophecy.My mother taught me many people in the outside world write to the foundation every day,claiming to be prophets who can predict the doomsday and thus requesting unemployment benefits.to stay.Employment benefits?Oh my!The outside world is far more wonderful than I thought!Fascinating!This boulaniche is even greater than I expected!You bet, Miss Fluffyby!
```

### [20] hash=`bccbcb363a781b84`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Now, it's the moment to verify the results of my delineation.If you look at the ground after the rain, you can often see a wet, long trail.Like this one.At the end of the trail, there may be a snail slowly crawling forward.Yes, forward.The snail marks the direction for us.But what if we don't see any snails at either end?How are we going to distinguish the direction to the future from that to the past?
```

### [21] hash=`489a0a945133e039`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
You just figured out how those researchers handled matters.Face the ignorance and do everything they could to find the answers.When the rain rose they struggled to collect every component left hoping topreserve the castle built by science.Unfortunately the effort was in vain.Another wave washed away the castle and restored it to quicksand.Even so theystill worked hard in that house like canned sardines to record what was
```

### [22] hash=`7d656dba6de754ea`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
happening because they believed at least the can holding them was a safeIt was a grand feat and no one could have accomplished it inside this huge cumbersome machine except another machine.She took no sides and sought only predictable results.That's why she made a decision as soon as she read that report and its attachment on her desk.The former was about a delicate component which flapped like a butterfly in that huge machine.
```

### [23] hash=`48dab493b29a286f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
And the latter was a piece of paper full of circles and dots.Then she stored the information on her hard disk and destroyed the report.And the paper which claimed to have recorded the locations where the storm might happen,yes, the one with the butterfly-like drawings, was retained for data comparison.It seems she's satisfied with the result.Are we in front of the rocket ball center?The orb showed copper pieces.
```

### [24] hash=`1ee1e43431a18a48`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
We need to find something that seems to be locked, but is actually not.Nothing can stop the devious Matilda.The trip to Egypt didn't go smoothly.The ship was hit by a common storm at sea.We were lost in the fog after that, completely off course.Then something merged from the water.Since the first storm, the Foundation has received frequent sightings of arcane creatureswhich should have been extinct in history.
```

### [25] hash=`abe3d62c599c383b`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
I had no idea what I was shooting at, even after I emptied the clip.And I didn't know what to do, so the arcanists brought us back on course.She named the precise longitude and latitude of our location,even without using the sextant in the spare cabin.I wonder how she did that?Anyway, she saved my life, but that was not enough to settle the differences between us.She remained rejective to working with the Foundation, and I finally gave up on the
```

### [26] hash=`9bf459e1a3f75e82`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
attempt to persuade them.My mission on that trip was not to make contact with them.Besides, what we needed was builders of the Storm Observation System, not some liarswho would only make things worse.As for the shelter they took from the Storm, she wouldn't say a word as if shedealing with a spy who prided to find out the deepest secrets of the Arkanists.In the end, he mediated between us.He gave me an address in Istanbul to which I could send
```

### [27] hash=`1d55290805feab62`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
the letters to contact them.After that, I spent more than half a year in the Egypt office.Things were even worse there than I expected.Some have gone missing after the storm.The people who were supposed to be in the Egypt office, according to the member liststored in the headquarters in 1985,but not there when I arrived.The situation could be caused by the limitationsof the transmission of paver-based materials,
```

### [28] hash=`7e9f66196fafa529`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
because the computer was not yet popularizedto every corner of the globe at the time.One minor mistake of a copyistcould develop into a huge difference.Besides that, the chaos inside Laplacewas an even worse issue.I learned that someone published the paperSamplings of global and regional chaotic energy route changes.In the name of Butterfly of Lorenz, apparently they secretly used our sampling sites,
```

### [29] hash=`7026d668632b8bf3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
yet their research direction and conclusion were radically different from Laplace's.The research is equally divided into two schools.One sticking to the human technology they have focused on,and one changing their direction to Arkanum.At the time, it was still too early to decide which direction was right, without sufficientexperimental data.But many already believed that if time continued to be reversed, human technology would only
```

### [30] hash=`4a69035be5d022b3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
keep falling into decline, while Arcanum, which relies on personal ability, would riseagain.It's true that gnosis cannot be copied, verified by an independent third party, orcomprehended through reasoning.Its nature decides that it cannot lay the foundation of science or be popularized toevery ordinary person.It takes solid marble to build a castle, not slippery sand.Even so, what harm will it do to rely on arcanum when the underlying logic of all
```

### [31] hash=`355abddf6c4f9ca9`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
things has become unreasonable?Before the disagreement was settled, the storm in 1987 was predicted.We were ordered to return to the headquarters 24 hours before its arrival, but the predictionwas not accomplished by Laplace.A captive from Manus Vindicte namesthe precise date of that storm.Our enemies, those lunatic xenophobes,valuing only pure blood, made it further than we did.Yes, we built observation stations,
```

### [32] hash=`3e7e4ed9b57899f5`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
we made countless deductions,we developed multiple simulation models.We made efforts, we sacrificed life,we did whatever we could.Yet the result was that we didn't findany other regions immune to the stormexcept the headquarters and another one in North America.In the end, 95% of the branch members were reversed,87.9% of the equipment was destroyed,and 100% of our predictions failed.In conclusion, our endeavor brought no achievements.
```

### [33] hash=`4ff4bc36f62280ee`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
As for the captive from Manus Bendicte,the delirium patient who claimsthat oracles flowed under his parietal bone,when we asked him how he learnsthe precise date of the storm,He burst into laughter.Can't you hear it?Has God left you behind when he spread his grace?Then he smashed his own skull with a handcuff.Yes, there was no doubt.He was an incurable lunatic.But his insane nonsense was exactly the reason we survived the storm again.
```

### [34] hash=`47e48b82220c889d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
No matter how unreasonable or illogical it was, or how much a lie it sounded like.So we'd better believe we shouldn't go out in black today because the fish is swimming in the water.We'd better believe in the existence of the non-physical, everlasting, transcendent world where everyone's soul is a number.We'd better believe in the supreme existence which caused the disorder of time by merely casting its shadow.
```

### [35] hash=`4c1519b7735ec630`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
That means the life of individuals means nothing more than rubbish and the world is but an imperfect ruinfor only the chosen ones will pass the trial and the rest will be eliminated by the rain.How am I supposed to do that?Finally, I made up my mind to write to her.I didn't expect her to answer my questions.All I wanted was to confirm if she had survived that storm.For the sake of our peaceful talk about the rhombus.
```

### [36] hash=`8d00858d8d2f009f`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Yet what I heard from them was a simple announcement of her death.With only two words.After we had suffered from the collapse of all the existing orders and the failure of all the great lawsIf this is what she called the glimpse of the supreme existenceThe moment of a phlatus.Do you have to present it in such a cruel way?The last two digits in the number of the year after that storm were exactly her name and her number
```

### [37] hash=`bd21e48c85d1a547`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
77I can tell from your uniform, you are a student of SBDM, or...This is Laplace.Do you have your guardian's approval to leave the school, Miss Underage Student?Wufal!She promoted Monitor Assistant of SBDM!Is my ID!To ignore a formal administrator of the Foundation?This Monitor Assistant will report every misbehavior of yours!Every little bit of them!We found that report here!How is a report filled with meaningless words of any concern to you, Madame Z?
```

### [38] hash=`edc9563d38965e35`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
It provides information about Arcanus Group Fertin is now dealing with.If possible, please give it to me.Of course.How can I turn down a request from Constantine's Chief of Staff?Take it away.I hope you don't mind the mold on it.To the computing center, Mr.Rude!Ms.Bwanish?Ms.Sotheby?You've done a great job.I'm sure what you have found would be of great help to Timekeeper.And I will report your active performance in this mission to SPDM as soon as possible, Ms.
```

### [39] hash=`56376448adc2adc2`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Bwanish.We need to further analyze the files you've found.The first on the scene could provide more detailed information.Let's get out of here.I didn't accomplish it alone!And Sotheby also played a significant role!Just to say, Miss Boonish, we can start preparing the balloons and flowers for the Twist Ball!Speaking of which, this monitor assistant still needs to think about it.By the way, just call me Matilda.
```

### [40] hash=`f765b4193b3cf085`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
There will be no advance in human technology.You think so?Even thee, Madame Zee, has given up on the study of theoretical physics and become a politician.No, I've never thought of that.I am astonished by the fact that you are interacting with others.they broke in if it was a complaint that you were making you know it iswithin your rights to submit an interdepartmental complaint within sevendays after the incident don't bother that file means nothing to me I didn't
```

### [41] hash=`1c4035584e840b9a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
file it because it is a report against the rules why bother to submit such alog full of personal feelings and emotional behaviors to our greatrigorous foundation is that so I am gratified to find that you still haveYou repeat the process like a roaring locomotive that pulls the research center out of this chaotic disaster.You question not what is ahead of you, nor whether the path you've taken will be regular or easy.
```

### [42] hash=`04db25562b6532ec`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
The only idea you planted into your little brain is to move forward to improve.Thank you for your compliment.Credit goes to everyone.But I beg of you, leave me alone.The work of analyzing the masks of Manus Vindicti did not go well.A side effect occurs in the researchers and it is getting worse.The isolation wards on the basement level are overwhelmed.What a scene.Have you aborted the experiment?Not yet.
```

### [43] hash=`7c761cdefb95275c`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
We have conducted the Arcanum Imaging experiment on the masks and found a component whichalso exists in the raindrops of the storm.But knowing what it is composed ofdoes not help explain how it works.What we're looking for is the original ritualthat the menace cast on them.You're trying to figure out one's career planningfrom one's physical examination report.I wonder why it is not working.Even if somehow you manage to find the original ritual,
```

### [44] hash=`dbafa39a6ff82732`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
you still need a proper environment to test it,Which is the outside world with a coming storm.That's why we can't tell if we're getting results.Even if we had the right ritual, proper permission from the Foundation to travel,and strong-minded volunteer subjects,experiments performed in the Ivory Tower won't succeed because...An experiment about the storm can only be done in a storm.Glad to see your brain is not rusty yet.
```

### [45] hash=`c286aefcae3ffc7d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
It only took you three sentences to draw the conclusion which took the seminar a week to reach.That proves you are capable of the project.The history maintenance team has forecast different critical points of this storm.Foundation investigators are on their way.If Manus Vindicte still plans to accelerate the storm, like what they have done in 1929,there will be a high possibility that their people will show up at the transformation point of history and society.
```

### [46] hash=`29fdbaa1e1339d0a`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Also known as the critical point of time, the center of the storm.Your sister, Greta Hoffman, is also one of the investigators.I have no interest in any Hoffmans other than myself.We have different perspectives.It is okay.I am just here to inform you that,if any of the investigators successfully send the information of the ritual back,the research about the immunity of the storm will be conducted immediately.
```

### [47] hash=`684c6eaee8849f7d`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p37`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-主线】第五章-特别篇-星｜1~6）

```text
Take your time and be mentally prepared, but once the storm alert is issued, we onlyhave 24 hours to verify the feasibility of the ritual.I wish you will be fully prepared by then.One thing is for sure now.The age of humans has come to an end.
```

### [48] hash=`90237bc33d323475`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p38`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】37.沙粒的记忆.角色剧情）

```text
Thirty-seven.Certainly.One, two, three.Does all this have any symbolic meaning?What?Thirty-seven.I just think...Close your eyes.As the scripture says,do not shy away from anything beautiful.Uh...I understand.Actually...In addition, I shall leave this with you.Thank you.Actually...Please wait.This is...I understand.potentially number maybe that's not right what do you need they are beautifulsubtract one subtract one like I said it's really good this is question is let
```

### [49] hash=`8b5f08ddba542ccc`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p38`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】37.沙粒的记忆.角色剧情）

```text
me think tension please this is fact not right fun 37 number well that'sin fact actually course to have fun 37 of course well that's outstanding but youour star of Hermes are the gold hidden in the sand on the never-ending beachsince this fragments that's outstanding instance of course that's outstanding orattention please or in fact Sophia like I said that's true of course to have fun37 thanks a lot thanks a lot in fact this is what people call genius like
```

### [50] hash=`a7aca1ce7ae99af3`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p38`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】37.沙粒的记忆.角色剧情）

```text
this I understand it's really good it's all right I think in fact it's notThere's nothing wrong with letting the stars shine where they should, and those who lookup will continue to look up.This is...actually is everything, all of it just about this number.Will it explain everything?That's outstanding.In fact, this is what people call genius.But you, our star of Hermes, are the gold, hidden in the sand, on the never-ending beach.
```

### [51] hash=`1454d89121567b8e`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p38`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】37.沙粒的记忆.角色剧情）

```text
Actually, it's alright.They are beautiful.It's everything.All of it just about this number.Will it explain everything?Sure!Thank you.No much about songs.That's outstanding.Two hundred and eighty-four steps.Thank you.
```

### [52] hash=`2c52eec42a4a6823`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p40`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】6.漫漫之夜行迹.角色剧情）

```text
A voice came from above and spoke to the man.An important thing will happen to you.D7.My friend.I think otherwise.But...An answer to your question.I think otherwise.In addition, if this gift is from the above,do we really have no choice but to kneel before destiny,begging for its love and mercy?Thank you for the long talk, Sophia.It is no surprise.Given that it's the proof you have to give a voice from the above spoke to a
```

### [53] hash=`cc0324a280a8be69`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p40`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】6.漫漫之夜行迹.角色剧情）

```text
man well that's outstanding otherwise it's why we stagnate in seeking thetruth like them from science poor child we walk in long from science benefitfrom reading learn from science we walk in long nights from science learn fromuntil the torch is lit.Thank you for the long talk, Sophia.A voice from the above spoke to a man.The scale of your soul has tilted.The balance needs to be restored.Therefore, beg your pardon.
```

### [54] hash=`0522c24bf1ba6f63`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p40`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-角色】6.漫漫之夜行迹.角色剧情）

```text
We walk in long nights.The scale of your soul has tilted.The balance needs to be restored.I see.The voice from the above spoke to a man.An important thing will happen to you.What will it be?Man asked.You will gain wealth.You will gain fame.You will walk in the garden of wisdom and happiness.The voice answered.It is just as simple as it is.
```

### [55] hash=`314f57877e7c9bcf`

- lang：`en`｜version：`1.4`｜arc：`—`
- doc：`BV1eo4y1u7aW_p41`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.4-剧情】雾行者·奥利弗的故事.轶事）

```text
that's what happened what happened all right forgive someone for asking never has just takeit as a trip to london forgive someone for asking one is reminded of some things in the pasti'll get it sorted soon someone is reminded of some things in the pastThou hath someone's admiration.Huh.Never hesitate.The sword is drawn.Thou hath someone's admiration.The enemies don't seem to be in the habit of wearing gas masks.

Fight for the unarmed.Thou hath someone's admiration.His trumpet's sound.The judgment day has come.I'll get it sorted soon.
```

### [56] hash=`49271cfb69dc4eca`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Can somebody tell me why I constantly get locked up ever since I've known vertin?First locked up in a suitcase then a foundation cell now thisWhat else could it be if vertin weren't the jinx you got the wrong person?She is the most irrational number here.I'm knockedWhat does it say here?Freedom will be granted once the proof is completed.That's to say, I have to prove myself not an irrational number to get out of here.
```

### [57] hash=`72500d0b7375e52a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Which is exactly what I've been trying to do, isn't it?Rat!Captain, maybe you're in the wrong direction.This apple presumes that the followers on this island have a close connection with Pythagoreanism.Pythagoras?That ancient Greek mathematician?The guy who said something about the opposite side of a right triangle, isn't he the guywho lives in sometime BC?Maths is only a part of the Pythagoreans' achievement, but from a more universal perspective
```

### [58] hash=`d2c8d7945b7ec10e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
they are a mysterious group of scholars.Believing things are made up of numbers, venerating integer numbers, abstaining frombeans and the religious collective lifestyle, these are all pointing to Pythagoreanism.The earliest Pythagorean school perished because of the discovery of irrational numbers, whichexplains their odium of it.At that time, a deviant student named Hipposus discovered root 2, and the theories based
```

### [59] hash=`581d3b47f8759a2b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
on the ratio of integers they hold dear were upended.Hipposus himself was drowned in the sea.This apple assumes they see the integers as the standard of virtue, and peoplecan increase the number they rankthrough study and self-improvement.Besides, they are convinced that a numerical codeis hidden in everything and everyone.Whoever can solve the codecan obtain the truth of the world.Oh, I know what's going on.
```

### [60] hash=`f29d324a0b38021b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
This pirate has had enough of this moral standardwhich is obviously prudish, backward,and lacks humanitarian spirit.I'm going to tackle the root cause of this misfortune.Why am I not surprised?The captain quickly gives the sufficient and prerequisite condition to prove herself anirrational number.This apple may be able to offer some help.An earthquake?All Abraxas's are flying in the same direction.
```

### [61] hash=`26c798ac970b974a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Is this their habit or?To collapse.So far this place has made the London Juvenile Detention Centre a heaven on earth.Is there a piece of paper?Did one of the Abraxas's drop this?Strange.The unsolvable puzzle.Is this a math problem?0.4, 0.7, 1, 1.6, 2.8, 5.2, 10 and 19.6.8 numbers in total are listed in this order.There are 8 symbols below, respectively representing the Sun, Mercury, Venus, Earth, Mars, Jupiter, Saturn and Uranus.
```

### [62] hash=`be58c9c2a5e0e02b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Maybe it is a hint that we should fill the symbols in the blank box after the numbers.That sign says to complete the proof.Does it mean to solve this puzzle?How unsolvable can it be?Clearly each of these eight numbers should represent one planet.We can easily find the missing planet by trying them one by one.And our Mr Apple here is the king of the times crossword.Yes?I think there is a difference between this and a crossword.
```

### [63] hash=`77cad5c20c0697a2`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
In this apple's humble opinion, the ratio of certain numbers should match this numbersequence such as the radius, volume or rotation period.Wouldn't the sun be absurdly large if these numbers stand for their sizes?The underground critters are back!Don't touch my notes!It's not your food!Hold on please, Captain.Seems like the critters are trying to tell us something.They are pointing at the sign of the sun.
```

### [64] hash=`591be142e5acb66f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Is that so?Even the critters on this island know math.The sun?What if the sun is just here to serve as a reference point?I read an IAU's report in The Times two years ago.You know, the International Astronomical Union.Earth's average distance to the sun is approximately 93 million miles.As for Mercury, the average distance is 36 million and Venus 67 billion miles.Let's say if we take the distance between Earth and the Sun as one astronomical unit,
```

### [65] hash=`e45e6b23a7a2bbad`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
then the distance between the Sun and Mercury would be approximately 0.4 units, and Venus0.7 units.There you go.These numbers are the ratio of the average distance to the Sun to the Earth-Sun distance.The average distance from Mars to the Sun is about 142 million miles, Jupiterabout 484 million miles, Saturn 886 million miles, and Uranus 1.786 billion miles.By rough calculation, and if we round the results to one decimal place, Mars would be
```

### [66] hash=`22448ba4f42cd9bb`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
1.6 unit, Jupiter 5.2 unit, Saturn 10 unit, and Uranus 19.6 unit.That's weird.All these numbers one can hardly remember have become so clear in my mind.But if these numbers stand for the ratio of distance, what's the planet for 2.8?There's no planet between Mars and Jupiter.If the sun is the reference, we will have one planet missing here.Is it really a puzzle unsolvable?Nothing is unsolvable.You are looking at the solution.
```

### [67] hash=`2457b5b28b13a2b8`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
There must be one planet out there, unknown to us as of yet, located between Mars andThe ultimate key of everything!Regulus!What are you doing?Got food poisoning after accidentally eating one of those critters?Odd.My head hurts.What was that?I'll make it short.Stanetta is in detention.They're planning to sentence her to death by giving her the poisoned wine.As you can see, this school on the island lives in a box made by the truth.
```

### [68] hash=`0c97b3751c3c5770`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Even if they have a doughnut in their hands when they are hungry, they still see a topological space.Like the cute ring attached to an initiation toy.It's not food anyways.But if you give them a puzzle, they will enjoy it like the best Kaiserschmarrn.Oh, my apologies.I was not talking about the one you are holding.No.With all due respect, that thing in your hand is pretty old.The mold on it seems to come from the 18th century, judging from the smell.
```

### [69] hash=`4406b11b205887c4`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
I'm sure you know what will make you sick if eaten.But we have to admit, it is not just ordinary mold.It reminds us of the story in which, once, a merchant's son looked up at the night sky,found the answer to the stars for us.The young man firmly believed that the movement of the stars and the sun follows certain laws.Just like how the delicate gears in a watch work together.And his point was even proven correct by Zeus' grandfather.
```

### [70] hash=`840da29dd1308fff`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
When another gentleman observed the sky through the reflecting telescope he took great pains to make,a celestial body was exactly there.What was it called?19.6, the 8th number in the sequence, the 7th planet in the solar system, and the legendaryGod of the sky.If the world was not created by God, are there any theories we can use to explainsuch a beautiful law?Yes, the one that says it never actually exists.
```

### [71] hash=`bdc7689af96e7e10`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Anyone can see the breach in this number sequence.that is the planet which is supposed to be the fifth number in the sequence Imean how come we have never seen it before if it does exist either God iswrong or we've been blind all this time what do you think oh darling Iforgot that you are one of the boring people from the modern times you needto understand that we are talking about a forgotten masterpiece from the
```

### [72] hash=`f711c7802a7bd67e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
But it was still ended, eventually, by another discovery, the eighth planet.Not the Ceres nor the Uranus, but a new planet.People found it through more precise astronomical data and calculation, proving that the numbersequence found by the merchant's son was only a myth.Now we are clear of what we've been talking about.It's an unsolvable puzzle.It makes no sense from the very beginning.We found the Ceres because it happened to be there.
```

### [73] hash=`7812f312d7479869`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
It is real, and no one can deny its existence.In other words, we can perfectly prove the rationality of mathematics because we invented it.It's been a good dream, I suppose.Now, imagine that you are walking alone in the darkest valley ever.trying to drag your fragile body upward as much as possible before it is worn out.Horse cries squeeze their way out of your mouth to ask for a response from the gods.
```

### [74] hash=`ae64a5a70519b9e0`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p10`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（10.海盗的数学｜1/3 14:21）

```text
Suddenly, an aflatus dawns on you.The next moment, a miracle happens.You are already at the top of the mountain,witnessing the rise of a huge celestial body from the skyline.Even if it's only in your imagination,you have just witnessed the dawn of the creation.And the shock is real.
```

### [75] hash=`eaad27bef254ce99`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p11`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（11.尺的援助｜1/3 19:00）

```text
An old admonition is engraved here.Let no one ignorant of geometry or the irrational numbers enter.Thirty-seven told me you are the integers.She's the genius kissed by the god of truth.She can see our numbers and has never made a mistake.I don't understand.Why would you break the silence at the meeting?I apologize, Miss Sophia.I won't defend our behavior.You're right, 37.But people always tend to believe that virtuous people are integers.
```

### [76] hash=`0d30cc0beab12be1`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p11`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（11.尺的援助｜1/3 19:00）

```text
That is what we call belief.Correct.But not entirely correct.Everyone can make mistakes.Numbers are just numbers.They are not associated with virtues.Unlike me.You're always right, 37.I don't know what differs us.That's boring.Let's go, Vertin.The assembly's about to start.
```

### [77] hash=`e6d5512d53785012`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
Timekeeper, I'll defend myself.Back in the Foundation, I once won a public debate of a similar nature.This is my duty.I won't let it get in the way of the team's investigation.Sonneto.By our tradition, Ms.Sonneto will be given the poisoned wine, so she will be muted and stay that way forever.However, Sophia raised her objection against the decision.After giving the matter some discreet thought, I have decided it is necessary to hold an assembly and take care of it democratically.
```

### [78] hash=`d8976e5bc0928d57`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
Those of you who agree to the death sentence may remain seated.Those of you who wish to commute Miss Sanetto's punishment, please put your pebble into the pot in the middle of the hall.Now, Miss Sanetto, Miss Vertin, you may defend yourselves until the sand in this hourglass falls to the bottom.I am Sonneto from St.Pavlov Foundation.I wish all the honorable audiences here would lend me their ears to hear my defense as a humanitarian gesture.
```

### [79] hash=`76eaa7ccebdb9af8`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
What number are you?Defendant, the court requires an answer.What is your number?What?Me?No, I don't have a number.Don't waste our time.People without a number cannot stand in the Hall of Truth.All her words are void!Sentence her to death now!Forty-two's argument is valid.Defenders, what do you wish to contend?What?It's valid?Objection!According to the record, the last time we inflicted severe punishment was in 1980, to a visitor who ate beans.
```

### [80] hash=`4cff678895d27886`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
He ate a carbuncle that feeds on beans.Then he was sentenced to death according to the said theory.In our scripture, eating beans is the most evil sin, which undoubtedly fits the most severe punishment.If we are now executing people for breaking the silence at the assembly, how would it reflect our attitude towards the consumption of beans?Has the latter become less sinful?I suggest Senato's punishment to be commuted.
```

### [81] hash=`e1495658e8469c50`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
A good argument.Thirty-seven's argument is deemed valid.The debate will continue.Objection.The punishment for eating beans is to throw the offenders into the GorgonCurrent, while the punishment for the Silence Breaker is to drink poisoned wine.Among allthe punishments we have, there's no other punishment more dreadful than being throwninto the Gorgon Current, because eternity and infinity are the two things we have
```

### [82] hash=`13336cf6751b0174`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
the least knowledge of, which makes them the most ghastly punishments among all.Giving her the poisoned wine doesn't make the consumption of beans less sinful.Her argument is invalid.Objection!The crimes would fall into the C category if we are taking the punishment as a frame of reference, which is...Objection!The two crimes in question are not commensurable, which makes your comparison invalid.Blast in this irrational debate, I...
```

### [83] hash=`d29b8d53be6d4096`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
I see.So that's how it works.Timekeeper?I will help you.look at my back i'd like to start by quoting 42's first argument people without a number cannotstand in the hall of truth in that case it's not possible for senato to commit a crime in the hallof truth because she can't even be in the hall what point virgin this is our chance to outargue them these are merely clumsy sophisms we've all seen her break the maxim objection what you
```

### [84] hash=`04d4d1cb5cb645cd`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
cannot be submitted to the court as a transcendental fact.It's nothing but the fragments of thephenomenal world which can't be used in your argument.Objection sustained.Please ladiesand gentlemen, keep the debate logically consistent.Since Senato has no number, and a personwithout a number does not exist before the truth, Senato thus didn't offend your truth.She didn't break any rules.Objection!The rule breaker has a number.
```

### [85] hash=`8c9e4ce5c6cc95e7`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
We can all tell that she is very likely an integer.Therefore, she should be identified as an unknown number, not void.Your sophism has failed.42's argument is held valid.Is there anything else you'd like to add, defendant?The secret, Fertin?We would call criminals negative numbers.I got it!It is easy to prove Senato's innocence.According to the law of the excluded middle, Senato either committed a sin or committed
```

### [86] hash=`c4c2762bd2101c83`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
no sin.The two statements cannot be both false at the same time.Since we consider a criminal as a negative number and a non-criminal as a positivenumber, Senato at present is considered an unknown number.That means she doesn't belong to the criminal set or the non-criminal set.She did not commit a sin, and did not commit no sin.It's a paradox.I hereby demand to modify the criminal sentence that has been given to Sinetto.
```

### [87] hash=`094ae74b4ca12878`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
The law of excluded middle, a good sophism.Good for you to create a paradox from one sentence of my argument.But pitifully, you've made a fatal mistake.You've taken my argument as the basis of your defense.I said people without a number should be expelled from the Hall of Truth.You don't have a number either, Miss Outsider.Based on my argument, which has also been approved by you,I argue that all your arguments are invalid.
```

### [88] hash=`4387309473b0d873`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
There's no time left.Thirteen has a number.I saw it.Thirty-seven.Do you know what you're saying?Yeah.I read her number.Just now.That's really a pain in the neck for that logical pragmatic assistant of yours, isn't it?People always tend to mark what they can't figure out as arcanists' doings,as if things would make sense once they do so.But it won't change the fact that The Debate is only a game involving sophistry,
```

### [89] hash=`39db5c5c376de089`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
improvisation, and strawman fallacy.So what makes it superior to Beans, if the form is what they are really after?Anyways, whoever fools the others first will win the game.No Arcanum at all.And that argument of hers is the best attraction for the audience.Hmm.A special number.A zero.That's ambitious, darling, and I love it.But you need to know that infinity is the most unfamiliar thing for the people,
```

### [90] hash=`f16c0cea15dec21f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p12`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（12.雀鸟的行径｜1/3 20:00）

```text
and that's why it triggers the most curiosity.Whoever tries to eat up this elephant with one bite will get all bloated and pinned by their own weight, waiting to die like a turtle upside down.By then, I guess you would be eager to throw up the elephant and turn back into the adorable, easy-going Zero we all like.Just like you, people are always on the way to finding something that can satisfy them undoubtedly, as if what they already have was disappointing.

She never says no.She just lets the hopes pile up on her shoulder because shesimply doesn't care at all.What a good, good child.
```

### [91] hash=`4bbc2ff2dfc8ebb3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p13`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（13.轴心的点｜1/3 21:00）

```text
Thirty-seven.You just said Vertin's number is zero.Do you know what it means?Very clearly.Would you be able to submit proof to a Peron?No problem.Half of you in this hall have put in the pebbles.If Thirty-seven's argument is found to be true, every argument Vertin has spoken in Sonnetto's defense will be deemed valid.Sonnetto will be exempt from the punishment.and a flying arrow is forever motionless this debate is nothing but meaningless wordplay
```

### [92] hash=`64b0821c7c149ba5`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p13`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（13.轴心的点｜1/3 21:00）

```text
that pacifist lets you off this time six a perfect number indeed for he knows the benefit ofreconciliation who wants to have blood on their hands and be devoured by the cycle of hatredyet it's a torture for any intelligent mind to hear such an immature debatecan you feel the suffering of our leader now i'm sorryNo apology needed, Miss Outsider.I also feel sorry for your pain, given that 37 has revealed your number.
```

### [93] hash=`632f8a98c94937b1`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p13`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（13.轴心的点｜1/3 21:00）

```text
What do you mean?37.Our evil little genius.The most cunning star of Hermes.She's been having fun revealing others' numbers for a long time.Our numbers are our essence, and it's also the most important proof we get once in our lifetime.The number of our souls suggests our fate.It might be changed through algorithms, temporarily, swirling, shifting, or transforming alongsideother changes occurring on the coordinate axis, but in the end, we can only be ourselves.
```

### [94] hash=`6348affe66fa77b0`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p13`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（13.轴心的点｜1/3 21:00）

```text
One is thought, two is opinion, three is wisdom, four is strength, five enthusiasm,6 Harmony, 7 Order, 8 Philanthropy, 9 is Restraint, while 10 is Completion.Zero, however, is in the middle of the axis, the origin of the frame of reference.It's neither positive nor negative, neither prime nor composite.Things are ever-changing, but you stay the same.Your loneliness also lasts forever.This is your fate.
```

