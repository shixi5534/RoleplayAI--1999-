# 剧情图谱抽取 · batch 083

- 角色：`wu_ming_zhe`
- 批次：**83** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.7」｜offset 95
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_083.jsonl`

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

### [0] hash=`5b7ffebc4a2b3d01`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
I can't let the clues end here!This is a wise decision.Is Heinrich still alive?I should have been faster.I can protect you from his old.She won't side with Manners from what I see.Give him my place in the storm shelter.Her arcane powers will be useful to usso the both of you can evacuate safely.I know what I'm doing.I've taken back my sensesbefore I die.I'm glad the pain never ceases.To die with my sanity and
```

### [1] hash=`0be571b82e627846`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
Rationality still intact it has been an honorCan you give her first aid and take her to the station?You'll meet the foundation there?They'll have better equipment.They'll know what to doHenrik is dead, but there must still be clues on him.This isn't over yet.I have to finish the missionMarcus the number of that orphanage in Romania.I've had it with me for a while nowBut please save your strength madam.
```

### [2] hash=`36c70aeb3df9d12f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
This isn't what we need to worry aboutWe don't have anything else to worry about.The mission is over.Silly child.Bring home.Before the storm comes,the future is yours.There must be something I can do.Everything is a book.Everything can be read.The most immediate threat to her lifeis that potion.Devil's dew string.Belladonna.Narcissus.Is that the roots, and the fruits and roots of the Picrasma tree?
```

### [3] hash=`556cdf45f41199d0`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
It's the formula made by Forget-Me-Not.The Picrasma extract makes up more than 50% of the potion.This is very different from Laplace's formula.Our Canis potion seemed to be a concoction of instincts and information.And there's nothing else I can do?The Picrasma extract is not a poison in itself, just that humans cannot...There must be a way, madam!Please!Don't give up.Keep reading.I will find a way.
```

### [4] hash=`c2986e173e7152d6`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p22`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（22.空白页.1/12 22:45）

```text
Marcus.No.Every book has an end, Marcus.There's nothing more on a finished page.No matter how reluctant you are to flip that page and get to the end.You will move on to a new chapter.Forgive me.No, no, no, no!For all the pain I had to put on you.An incredible woman.Her suffering ends here.Doctor, have you decided?I must leave, but I will wait for your answer.
```

### [5] hash=`2d939b6dad4db277`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p23`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（23.汉赛尔与格蕾特.1/12 22:55）

```text
Madame Hoffman was calm till the end.Why?Was she not afraid?I just read herfear through her trembling fingers, but she would not show it.She knew it wouldhave frightened me.Repeat, this is the 24-hour countdown to the storm.Allpersonnel must return to the headquarters.Repeat, this is the 24-hourcountdown to the storm.This is similar life.You must leave now.Last call.You know we won't wait if you miss it.
```

### [6] hash=`6850b4bcd2e561fa`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p23`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（23.汉赛尔与格蕾特.1/12 22:55）

```text
The storm is coming, Doctor.Come with me to the headquarters.You can take Madame Hoffman's place in the shelter.King Midas hunted in the woods in search of Sylannus, the wisest satyr, the companionof the wine god.What is the best and most enticing thing for a man?the king asked.Strange way of drawing.Rick said he showed the path to salvation and brought you all to the guiding wall.Salvation.Did be.
```

### [7] hash=`ef2e362b43fde47f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p23`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（23.汉赛尔与格蕾特.1/12 22:55）

```text
If I succeed, I can prevent the death of someone who holds the clues.Even if I die, I'll still turn Kakanya completely against Isolde.This was your plan, madam?What really scared me was not the threat to my life, but the possibility of dying ignorant.I know what to do now.There might be another way.Don't fall into darkness.Don't let madness or despair take over, Doctor.This is not the end.My mission is not over.
```

### [8] hash=`a6ca0dbd11010d1e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p23`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（23.汉赛尔与格蕾特.1/12 22:55）

```text
There's still another way to end this.But it can only be done by you and me.The Guiding One is merciful in bringing this era to an end before the summer of 1914.Here, the nationalists, the internationalists, the arcanists, the rationalists, the progressives,the conservatives, the fanatics, the bystanders.They indulge in passion, insisting that it is their ideals that make up the world.Who would have thought that such a progressive and sensible era would end in a barbaric war?
```

### [9] hash=`84a842cc10fb4747`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p23`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（23.汉赛尔与格蕾特.1/12 22:55）

```text
Yet in the end, like dust, they'll be swept away and forgotten by time.Only the true believers will survive the end, but I must regretfully remind you, killingone of our own, despite your merits, is a violation of the rules.I will report this to the guiding one.May I have a moment alone?Mister, forget me not.I want to look at this city one last time.Whatever you want.I've thought about this and made up my mind, Isolde.
```

### [10] hash=`8eb45e72ba48c906`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p23`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（23.汉赛尔与格蕾特.1/12 22:55）

```text
You were right.I will join you.I've been waiting to hear this for so, so long.I know this is what you want.Now I can finally make your dream come true.Before we leave I would like to take one last walk in this worldWould you like to join me and walk to my clinic?
```

### [11] hash=`500eda98ce5b60d4`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
Du hast alles gut durchdacht.Der Spiegel macht mehr Angst nach dem was passiert ist.Er spiegelt wahrheitsgetreu mein hässliches Gesicht wieder.Meine abstoßende Seele.Doktor, du bist nicht abstoßend.Wie kann jemand, der abstoßend ist, so edelig hohe Ideale haben wie du?Hm, vielleicht, vielleicht haben sie recht.Es ist Zeit das Tuch zu lüften.Das Licht tut weh.Hast du die Vorhänge geöffnet?Ich kann nichts sehen.
```

### [12] hash=`2cc84ff068af1d5b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
Schauen Sie sich dieses Gemälde an, Isolde.Erinnert es Sie an etwas?Ich kann es nicht deutlich sehen, Doktor.Ist zu hell hier.Könntest du die Vorhänge etwas zuziehen?Das ist das Gemälde Ihres verstorbenen Bruders.Die Rettung.Wir haben eine einfache Tatsache übersehen, Isolde.Bis Heinrichs letzte Worte uns alle daran erinnerten.Theophil schrieb seine Notiz in Verzweiflung.Ich kann nicht sehen.Könntest du bitte das Licht im Raum dimmen?
```

### [13] hash=`4892fcc186b70672`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
Betrachte dieses Gemälde!Schau dir diese Spiegel an, Isolde!Was hat dir der Anführer von Manus Windig dir gezeigt?Was ist der Weg zur Rettung?Ist das ein Zauber?Ein Ritual?Du bist die Einzige, die es weiß!Schau die Haare an, Frau Marcus.Ich werde die Erinnerung bewegen.Nur dann kann ich meinen Fehler nicht machen.Du kannst das machen, Ms.Kakanya.Halt meine Beine!Wunderer, Schmeichler, immer da, bei jedem Treffen.
```

### [14] hash=`dc12a9fd63d4026c`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
Diese naive kleine Tosca, sie vertraute ihren süßen Worten.Sie erzählte ihnen eine andere Geschichte.Vorhänge im Wind, das Warme war der Sonne.Was passierte als nächstes?Schließes!Ein weiterer Teil?Nein.Die Zeit der Silenz.benefit from reading till the torch is litbenefit from readingso ich sauer auf mich, ich weiß, eine Schauspielerin sollte perfekt seinRedetorske sollte den feinsten Traum darstellen
```

### [15] hash=`40ae18ca8c55a7b7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
sehen sie!Und Pracht preist!ist der Vogel noch da?Eröffnete und trinkte umWonderwalls areal stuntIm Moment der Silenz.Die Skala deines Seels hat geblüht.Die Balance muss gerettet werden.Sie haben die Balance gemacht.Willst du den Aerial Stunt sehen?Kunst, eine faszinierende Krankheit.Verlangen, Unterdrückung und Wahnsinn.Alles wird durch Kunst ausgelebt.Es ist die Rettung!Wir kommen näher!Er meint es falsch!
```

### [16] hash=`cf5cf22bbc386800`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
To Phil!Du meinst es falsch!Möchtest du den Aerial Stunst schauen?Die Macht fliegt!Der Moment der Silenz.Don't blink!Die Benefiz von Reading.Was passiert als nette Rassistin nach passiert?Havrodossi, bist du gegangen?Victory is killed.I should excuse myself.Stop using the mirror!You will both collapse if you continue to force her!I'm running out of options.I have to hypnotize her.Hypnotize me?Du, Miss Clara, der Doktor, der die Pneumatisierung auslässt und sogar die Tatsache hat, es zu stoppen.
```

### [17] hash=`b7281b3acc8c420f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
Du wirst es an mich benutzen.Warum?Weil ich eine hysterische, irrationale Frau bin?Die wütende Witch.Die verletzte, unbekannte Arkanistin.Warum?Warum bist du so wie mir?Please calm yourself, Isolde, and fix your eyes on this watch.Why?Did I do something wrong again?Am I hopelessly incurable?Why, why couldn't you cure me?Can't you save me from despair one more time?Schlaf, Isolde.Gehe zum Ort des Friedens, zum Heim der Nacht.
```

### [18] hash=`da496b80a984fd5a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p24`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（24.今夜星光灿烂.1/12 23:00）

```text
Wenn du bereits eine Entscheidung getroffen hast und denkst, dass ich schuldig bin,warum behandelst du mich dann zu Sand?Wenn das Tierlösung ist, die du gebracht hast, werde ich sie mit Freude annehmen.Wir haben es geschafft!Finally!News from the frontline.They have sent home the storm immunity ritual.Get to work, people.In the 22 hours before the storm arrives, the whole world is our proving ground.
```

### [19] hash=`9c28ec066420d2d0`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Move!Ugh!Move!Shoot, are you blind, or did you hit me on purpose?I don't control this thing!It only drifts on my bed at night!I can sit back for a week!Just remove your brain.Problem solved.Oh, thanks!Oh, I didn't think of that.Thank you for your advice.You are so sweet.Oh, you're so welcome, pal.I'd wet my eyes more often if I were you.Just do something to get that black snot off those lashes.The good news is, the persons in charge of this place are all dead.
```

### [20] hash=`91976d81c369ec66`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
The bad news, the one in charge right now, is not a person!Hello, Researcher Medicine Pocket.Your meal allowance is being deducted to pay for door repair.I don't care, Buckethead!Do your worst!A few pennies don't bother me.You could have called me from your lab terminal.The technology department has equipped every researcher with the latest communication device,and I have the energy to communicate with everyone.
```

### [21] hash=`16e7abd6dc019637`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Then how am I supposed to know whether my report is lying in your trash or not?Oh please, you know we gotta talk face to face to solve our issues when things get ugly.Congrats on the one and only achievement you got from the Manus Mask.We're now fully aware of its side effects,and this great achievement is filling the halls with oil and insanity.You should thank the hatted Cuckoo for her report.No one's turned into a crazy monster yet, or the Manus would be attacking the headquarters from the Plas right now!
```

### [22] hash=`fdf68804966dd370`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Damn it!What are you doing?Are you even listening to me?My apologies.You said we needed to talk face-to-face.If I understand it correctly, this is your number one request.You always carry a face in your pocket?That's just...great!You are welcome.It is our duty to learn and meet the needs of every researcher.This will help them reach their full potential while respecting the nature of their being.I received some letters of complaint.
```

### [23] hash=`73bbf3ad4f92a37a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
They asked me to develop a better sense of humor.They said it would help me understand the researcher's sarcasm, so I am studyingit.75% of the complaints mentioned they did not want to see a face on my head.Some even use strong words like never let me see that face of yours again.I am glad that you are one of the other 25% researcher medicine pocket.You know what?I don't mind if you keep that face on.
```

### [24] hash=`e2464338c44e556e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
As long as you let me kick it around a bit.Regarding your second request, I have read your report.I fully understand the side effects of the mask as well as the feasibility of the decryption.Then what's the point?It's like trying to get the syrup formula out of a Coke can.Ugh!Again, we are all screwed without the original ritual from the Manus.It is too early to conclude that the mask does not contain important clues.
```

### [25] hash=`e0c8b42475bddf73`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
The attempts we are making are very necessary.Besides, the situation in Laplace is not as bad as you say.The side effects are completely under control.The subjects are only suffering from dehydration and mania.Fortunately, the rehabilitation center has extensive experience in dealing with manic patients.And some researchers, like yourself, are already manic without putting on the mask.So the side effects will not affect them much.
```

### [26] hash=`d637d7458cae651b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Ball pens!Ball pens love brains!Extensive experience, huh?That is right.I am glad you have noticed our efforts.We have prepared a large amount of polymer materials in case of minor vandalism by the patients.Haha, amusing.So this is the logic of a machine, huh?Humans are as expendable in the lab as glass.You should be glad that your head is harder than my teeth, alright?Your opinion surprises me, Researcher Medicine Pocket.
```

### [27] hash=`d909c4d10e864c23`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
There is a big difference between the human body and glass.As for the original ritual, you are not the first researcher to make this suggestion.We are fully aware of its importance.We have dispatched investigators and members of the Field Agent Administration to investigatevarious regions.Here are the images they sent back.Field what?Field Agent Administration.If you have not heard of the name before, most prefer to call them the History Guards,
```

### [28] hash=`18b799b934d04064`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
given their function.right that team of cannon fodder the thought of people being thrown aroundlike garbage makes me feel lucky that I'm just a piece of glass looks likeface-to-face conversation does solve problems finally we're gettingsomewhere aside from the insane colleagues running a mock let me guessthe blue dots are good news huh correct they represent the safe areas immuneto the storm.Ah, North America.
```

### [29] hash=`0634c97a26185cd0`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
I should have gone there for a walk in the park.I don't deserve to suffer in this stupid gray prison.I have to say, Researcher Medicine Pocket,even though I approved your request for a sports field,which you claimed was a humanitarian need,I think it is more of a canine need.I suggest you install an indicator on your humor moduleso we know when to laugh.See?Like this blinking red dot.Is that Vienna?
```

### [30] hash=`6b2bc6526fb071f7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Yes.Alright, alright!Not privy to the information, huh?I know of your tricks.One day I will find the logical fallacies in your words, I swear!And this here...Yellow.Better than the worst, worse than the best.That's the Aegean Sea.What's all the fuss about?Don't tell me there's a 500 meter long blue crab.No, no sightings of large marine organisms other than the Gorgon.This is where Timekeeper and her team are right now.
```

### [31] hash=`c2d2de4b8dbc3df6`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
By the way, it seems you can distinguish between colors precisely, so the canine elements inyou are more of a personal choice than an innate trait.I see your efforts on improving your sense of humor, I do, but that's enough now.Turn off the module, okay?Who the heck put these complaints in the box?I'm gonna kick their teeth out back to business timekeeper and her team are ina bit of a situation the details are classified and I am not privy to them
```

### [32] hash=`8e5714735a8d88ae`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
either huh classified I know what's going on in this place classified meansthey're in big trouble Marcus Marcus I'm sorry madam Hoffman I was reading theConsidering they will probably do the same thing they did in 1929, you know,escalate the international conflicts to accelerate the reverse, this mission isprobably quite risky.It's okay, Madame Hoffman.I am fully prepared.I've been waiting for my first field mission since I joined the Foundation.
```

### [33] hash=`90dafcbd6f7aef7e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Thank you for approving my application, or it's still be talking to rustyfiling cabinets and diamond patterns on the wall.No need to thank me, Investigator Marcus.It's in the news.Unknown island appears on the Aegean Sea.Forces attacked by arcane creatures.Ownership over island causing conflicts between Bulgaria, Serbia and Greece.Austro-Hungarian Empire and Russian Empire to establish a negotiating committee.
```

### [34] hash=`d26e3b08c24e9fad`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p2`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（02.进行曲.1/7 9:30）

```text
Madam Hoffman, the increased turmoil could cause the storm to arrive earlier, right?That is not our problem.The headquarters will send someone to intervene since it is caused by the Arcanum.Now, just focus on our destination, Vienna.Time to get out.Grab your luggage.
```

### [35] hash=`84e2b7bed52eebe7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
Here it is!The national treasure of Austria!The creamy chocolate cake, the buttery ganache and the delicious apricot jamCreated by the ingenious apprentice Franz Sacher in 1832Renowned throughout the worldThe dessert of ViennaSacher ToadMy first time seeing a real oneHow should I cut it?If I cut straight, the cake will get mushyIf I cut sideways, I'll miss out on the apricot filling.What if I eat it in one bite?
```

### [36] hash=`300808a5977f5996`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
No, no, how unrefined.The director would scold me for that.I have to think carefully.There must be some other way.Remember all your training, Investigator Marcus.This is the most important moment of your life.Don't get too excited or you'll ruin it.Thank you for deciding for me.What's with the tears, Marcus?Because the cake is way too sweet.According to the plan, the head of the Vienna branch would pick us up and guide us through the necessary procedures of this era.
```

### [37] hash=`7f36a178be1d1803`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
But our train was two hours late.That being the case, our Mr.Carl should have been waiting for two hours, but so far there is no sign of any gentleman in the Foundation's uniform.So Mr.Carl is also more than two hours late.A clever deduction.I'd say it's never been discovered before, like the Celtic Otherworld, you know, the heavenly land beyond the sea in Bran's legend.The Arcanum has declined after the Enlightenment.
```

### [38] hash=`645d6263a63f3185`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
It is an honor for all of us in this era to find such a paradise from the past.You're not fit to be human if you don't understand what that island means to us, my friend.Secret base.Otherworld.Fascinating.I need to write this down.Miss, could you show me your papers, please?Ah, right.I'm sorry.My friend has it.Could you hold on a minute?I am an Arcanist sent from the headquarters of the Saint Pavlov Foundation.
```

### [39] hash=`d90a24156eab7587`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
I have a letter of introduction from the head of the Vienna branch.Arcanist?Then you come with us, Miss.Hands up and be quiet.bring over the golems we have an unregistered arcanist huh don't let herget away what is happening at ease James allow me to explain this respectablelady is most definitely not a Russian spy this Hoffman so this lady was thebig case is your assistant no spy would be stupid enough to carry an
```

### [40] hash=`62bbf695e56244e1`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
Relax, this was just a minor incident.You'll never find another place astolerant as Vienna.It's the very same principles the Foundation strives for.All registered Arcanists can come and go as they please in this beautiful city.We even offer artists and musicians perks that cover every aspect of theirlives because Vienna loves art and music.Speaking of registeredThere must be some mistake.All Arcanists entering Europe must possess an Arcanum license,
```

### [41] hash=`0c44b97bac42fb92`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
issued by the local government.Austria enacted this policy in 1756.They abolished it in 1868, but were in the time of great tension.So, you know...Perhaps this lady knows something.Ms.Marcus?Yes?You are an Arcanist, even though you're sent by the headquarters, correct?Is everything okay, Mr.Carl?Is it not acceptable?Oh, yes, it's a perfectly good license.I can even smell the ink from the government office.
```

### [42] hash=`119555d9ba159de7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
Welcome to Vienna, Miss Arcanist from Romania.You should have shown it to me sooner.It would have saved us a lot of trouble.Um, I'm so sorry to have wasted your time.Speaking of which, no offense, but you are two hours and fifteen minutes late, Mr.Carl.My apologies.The Minister of Finance and I had a little too much at lunch.Well, your train was late too, wasn't it?You were having lunch when you were supposed to be here.
```

### [43] hash=`b500e561c1c4f096`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
We agreed.Relax, lady from the headquarters.You're just not used to the space around here.Look at this industrialization and so-called modern designs.They have turned our beloved city and our carefree life into a cold, impersonal machine.Please forgive the train staff, the sewer workers, and the plumbers.It is their right to be a little unpunctual, and enforcing this right is a symbol of ourfree will.
```

### [44] hash=`82706d2e9d4fd114`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
In the end, you didn't wait too long, and I got to enjoy my lunch.It all worked out, right?So, vie for the train late.No, no, no, that's okay.It's just a group of lunatics banished to an island.They're arcane criminals from a small country and people will forget about them in less than a month.Only a few would believe that it has any real influence on Vienna.You know, the young artists who think highly of themselves, the schemers with evil plans,
```

### [45] hash=`4ae18ace579e34f2`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p3`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（03.叉子与蛋糕.1/7 10:00）

```text
and the conspiracy theorists suffering from neurasthenia.Put away your license.We need to catch up with Carl.Remember my words, Marcus.Never trust anyone.Even if they're a branch member of the Foundation.
```

### [46] hash=`313038a8b5bd54cf`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
So this is the Vienna branch?Blended!Look at the walls, simple yet elegant.It's like a temple of modern art.I can read the contrast between different shapes and textures.This Mr.Ulrich must have put so much effort into the design.It must be a very pleasant place to work at, Mr.Kahl.Oh, no.This is a secession building.Another meeting place for the young artists to show off, other than the cafes.They said they wanted to break away from traditional art.
```

### [47] hash=`7b388768edbaad31`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
Well, it's more like they're breaking away from human life.There's nothing to like here.Only inexplicable paintings and neurostinic lunatics.But people keep coming back.There are even secession groups to the secession.Like cells dividing through mucosis.The entrance to our venerable branch is on the left.Please follow me.Notice the guard?It's the most loyal and reliable knight of Vienna.Powered entirely by arcane ritual.
```

### [48] hash=`89377ab2cbde3712`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
The greatest achievement since the revival of Arcanum in Europe.In 1662, a royal magician from London offered it to the emperor at the time.Since then, it's guarded the Empire for centuries.Ah, sir!Greetings, dear Suscarpia.How is your son Tamino?I hear he's not getting along well with his fiancé.He's a strange one.What's he doing standing in the corner like that?My apologies, Miss Hoffman.Please hold on.
```

### [49] hash=`4dda70e854a027be`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
Terrific, Heinrich!Just as terrific as your pathetic art career!That's great!Best wishes to you, Suscarpia.That's why he sees everyone as a character in an opera.Operas and music, they do harm to your eyes and fill your ears with useless sounds.Is every artist like this?Scarpia, Angelotti, they are indeed characters from the opera Tosca.Oops, I am getting off topic.Don't worry, we've modified its original ritual to meet the needs here.
```

### [50] hash=`e5e7d9eb8588220b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
Lots of people come in and out after all.when they did the maintenance or repair?Let's hope so.Now take a look at this before Mr.Karl comes out.Several days ago, a member of the field agent squadfound a painting that was reported in this magazine,The Pan.It belonged to Teufel von Dittarsdorf,a deceased artist from Vienna who committed suicide.Its name is The Salvation,and it was found along with a poem.
```

### [51] hash=`07092faefb4b9172`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
The poem mentions the doomsday,On the search for Silenus in the forest, I asked him what is the best and most wonderful thing for a human being.How is it that a human being has never been born, he said.I looked at him.The ring of life.The ring of all life.Your hands form the ring.And the judgment is pronounced.Wem wird das ewige Glück gewährt, die Gnade von oben, und diese Lehre, das Aufhören derExistenz?
```

### [52] hash=`3566ee6b3a8bfee2`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
For so moving, this Sieglind.Poor Siegmund, my best friend has returned to the void.Thank you all for coming today to shed tears for our departed hero.He was a righteous and noble man who cared for his people.He was still trying to save the Arcanists on the Golden Isle before he died.He left us so many beautiful poems and paintings.Shame that the fire burnt everything to ashes.The only thing that survived was the salvation.
```

### [53] hash=`7b0d805874f385f7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
We were in a golden age of progressive ideas.We believed the Enlightenment would make ignorance historyand lead us to paradise where everyone would be saved.The barrier between Arcanists and humans would be removed.In Vienna, that tolerant city, we would stand together hand-in-hand, back-to-back, relivingthe intimacy we once shared when we first came into this world.Oh, world, its head bites its feet, its knees touch its nose.
```

### [54] hash=`abe1e68873e1b570`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
But the reality is, the survival space of our canists is shrinking.We try to speak up in our own language, but that only makes us strangers in ourown land.That's why we have decided to exhibit Sigmund's last work.Not only in memory of the deceased, but in memory of his noble spirit, his sincere concernfor his people, and his scrutiny of this tragic world.There is no need to be sad, my friends.He has left us with Rheingold.
```

### [55] hash=`ebd962d0505ddebf`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p4`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（04.分离派之家.1/7 10:15）

```text
We will found a committee with the funds raised by the exhibition to improve theThe evidence collection permit.They've provided us with all the official documents we need in this era asWell as a list of all the Arcanists in Vienna in 1914But we're not going to cooperate with them any furtherBecause of the requirements to confidentialityWe'll only need manpower from them in the following operations

In case you spend a whole day on the A section Marcus.We're looking for TeofilStarts with a T.How did you know I was starting from line A?
```

### [56] hash=`54664b528e6f296e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p5`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（05.游灵派对.1/7 10:15）

```text
Isolde?Isolde!She passed out again!She must have smelling salts on her.Find them!What's going on?Make way!Let me see.Kakania!People!Make way for the doctor!Isolde, can you hear me?Oh no, it's a seizure.She's going to bite herself.Get a stick!Heinrich, do you have any props she can bite?I bet she can't wait.Isolde, open your mouth.They'll throw their wallets at you as if they'll be left behind by the times.
```

### [57] hash=`e32c272f1e8db7ef`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p5`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（05.游灵派对.1/7 10:15）

```text
They're all blinded by the shining glamour of progressivism,and they even scoff at psychoanalysis,the real meaningful discovery of the era.Isolde?A real Isolde.Now let go of me first.Oh no, it's a seance.Miss Tosco only does it before a performance.Of course it turned out this way.She's lost control.She summoned evil spirits this time, not the good ones.She's afraid of the paintings.Oh, poor girl.
```

### [58] hash=`39b7e68837a65998`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p5`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（05.游灵派对.1/7 10:15）

```text
It's her brother's paintings.Skakania!Watch out!Heinrich, give me a hand!Draw the ghosts away by whatever means!These souls are no longer bound to their bodies.They're a nuisance to deal with.Over there!Leave the doctor alone!I brought this bullet with my savings.Who took it out of my body?It was enough of your ugly fuss.What family are you from, miss?How much property do you owe?Stop working!You'll have to try harder, Mr.
```

### [59] hash=`b972cb3d4889e733`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p5`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（05.游灵派对.1/7 10:15）

```text
Heinrich.Deeper beat, gentlemen.Are my stars?He took half my body!No!Father will scold me!You don't wanna miss it!I'm nobody!Back with the stink of a monkey!How dare you!filthy fingers upon mewhenevertime waits for no oneeven for a great thingtake care of Isoldeoh catching a ghost with myhandsyeah it's so soft andstickyin fact youare now safe Isoldefeel the pressure of my handsthe pressure willremind you of some things
```

### [60] hash=`6178a10b7c29df99`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p5`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（05.游灵派对.1/7 10:15）

```text
You will slowly and steadily reach your head, and you will not be harmed.That's it.When I release the pressure, you will slowly open your eyes.These things will gently fall to the ground, like feathers.Now you will carefully catch them.Tell me.What did you see?What happened?Dr.Schwartz told me that humans are rational,and we should be able to control ourselves completely.The opera I can't bear.Heinrich, please take Miss Diddersdorf to get some rest.
```

### [61] hash=`be915a8bd6ddafab`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p5`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（05.游灵派对.1/7 10:15）

```text
I will.What about you, Doctor?Where are you going?I'm going to get that damn Schwarz!Kakanya?Hmm?You are from the Foundation?And...Angelotti?And...the unknown lady?
```

### [62] hash=`a61180b5e43c6b5d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Remember, Marcus.The working staff of the Foundation branch will take care of the dispute in their fashion.We just need to follow him in.The members of the Circle are top priority, but before any of them can be convicted,as said before, all we have to do is silently observe and respect their lives.Understood.I almost bumped into her.That lady in green seemed to be in a bad mood.Shall I ask the gentleman from the branch who she is?
```

### [63] hash=`53a5a5410c38d24e`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Oh, he seems busy at the moment.But that gentleman is a person of this era.If I interrupt him, am I also interrupting his original course of action?My, my, Mr.Regalato.Your hair has grown so fast.To what do we owe this pleasure?Are you also here for the exquisite art?Can you just be normal for once, Henry?And stop calling me by those opera names.Someone reported an arcane disturbance here.I see candles.
```

### [64] hash=`386650587e5c63ff`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Are you holding a seance?I must remind you that arcane rituals are not allowed unless you have a separate permit.Excuse me?That's not fair.The first permit already costed us a...Please calm yourself, sir.Be mindful of what you implied.The Viennese government has ensured you the greatest possible freedom through working with us.Who do you think cleaned up after you people?After those fires, passionate murders and deadless tempeits?
```

### [65] hash=`55845d6b568cc165`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
We can't bear the consequences of your moments of epiphany forever.Not to mention the seance is one of the most dangerous acts.We've had two colleagues injured still being treated for mental illness in the Vienna General Hospital.You will find no other plays as tolerant and open-minded as this one.In return, you should do your part and cooperate with the government.Seance?What seance?Nothing of the sort, Mr.
```

### [66] hash=`3ac00c5b851ca0dd`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Rigoletto.This is just a rehearsal of the play.The candles, the settings, and of course these paintings once bathe in fire.Yes, this is an art exhibit, a youth rally, or, as we prefer to call it, a visualizationof the future.I demand a rational conversation.Now, I must question the sanity of this gathering.Is there no one here who is of sound mind?If not, I'll have to...I'm terribly sorry, Mr.Strauss.
```

### [67] hash=`c87bae78276ce596`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Sorry to have kept you waiting.These burnt pictures, they're the work of Theophil von Dittestop.They're the perfect subjects for reading.Only a third of the picture can be read.But I can see it clearly.An ingenious composition that balances the different elements of the picture.Sadly, the creator focused too much on the form and overlooked the content.The frame is made of...not important.Next page.
```

### [68] hash=`e9616519557d69bb`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
This one is luckier.Half of it survived the fire, so we can see the lower half of the lady in the picture,but uh...Teofil certainly had a way with women.She was not his first prey, and this one only a frame remains.The rest of his works are too damaged, but I do remember an intact one somewhere...But aside from this, I don't see anything else.Next page.People can be read, too.That person, Missy's old.
```

### [69] hash=`18197488b0a181e8`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Unlike other ladies pursuing the latest fashions in Paris, she still wears the corset, withonly some Art Nouveau jewelry by her waist.She's as delicate as a butterfly.She is a renowned medium.The Ditista family is well known for their mediumship.Nowadays, they use that power mostly for art.That is, they summon a spirit to possess their body so they can sing, write, and paint like no other.They also suffered for this power.
```

### [70] hash=`bd61f6f0b6b51848`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Wrecked by neurosis and hysteria, the family has had very few members despite its long history.Wait a minute, the picture behind her is still intact, and it is enormous.Salvation?Strange, this painting is.You have a keen eye for art, Miss.This painting is the work of my dearest friend, Sigmund.The Salvation.The only piece he left behind that survived the consuming flames.These enchanting, magical circles, one next to another.
```

### [71] hash=`95193949dd196057`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Oh, I was only reciting Miss Cacania.We're both passionate about the subject.How regrettable.She would have given you a much better explanation if she were here.Let's start our conversation with a simple exercise first, please repeat after meDitters DorfAfter all the days you've spent in Vienna, you should be familiar with the nameTell me how do you feel about it?You're making light of it againBut fair enough you're new here not as familiar with this name as those who live here murmuring it in their dreams
```

### [72] hash=`ac8e12fc8070aad5`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p6`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（06.是，首相！.1/7 10:30）

```text
Most of the time it swirls invisibly through the conversations on the streetWell then, high time to tell you about them.Vienna, at present, is a splendid, crumbling house.Whenever the waltz starts playing, the roof trembles along with the music,while the dancing crowd, and funny that it is a crowd,none of them dare look up at it.The people here live in identical pretty little houses,And it is in this act of fighting against her madness that she proves herself proper among the noble ladies.

She knows better than anyone why a piece of art is valuable and how to make it worth even more.
```

### [73] hash=`301bea7e48616ed7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
Good day.Uh, I would like to check the date of a novel.Yes, it is Der Mann ohne Eigenschaften by Robert Musel.I see, I see.What did they say?Just as I remembered it.The novel was completed in 1930.The word Cacania was also created by Robert Musel.Cacania should not be a nickname for anyone in 1914.It doesn't belong to this era.She could be with men as vindictae, or at least associated with their people.
```

### [74] hash=`4a18a9b6c175b4f2`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
What's more, when we were at the secession building, I read that painting, The Salvation.It seemed out of place compared to the other paintings.Teofil, we have applied a new technique on The Salvation, a more daring kind, audacious even.But these are only subtleties, I can't be too certain.I was interrupted by that strangely speaking gentleman, so I didn't get everything.Another thing, its content reminds me of the symbol of...
```

### [75] hash=`979e442f95806c7a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
the circle.Pristine circle resembles the circles in The Salvation.Heinrich called them magical circles, one next to another.They must be more than just circles, I think.Was he demonstrating the madness of passion?But the lines are clean.Perhaps the purity of eternity?No, the circles are too twisted for that.Was he just representing a primitive state of being?I don't understand any of it.So this must be art.
```

### [76] hash=`d2c678e769de21b7`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
You're funny sometimes.I wasn't joking.Based on what we know, we can't be sure if this group of young arcanists and the Manus are connected.But we all know that the latter is eager to win over the cynicalrevolutionary youth.You did well, Marcus.The important figures of the circle,Isolde, Heinrich, and even the late Teofil.We have made contact with them all.Only this Kakanya.What does the intel say about her?
```

### [77] hash=`f02e02027a01d892`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
Kakanya, also known as Miss Clara, inherited her arcane skills from herfamily.She's able to reflect people's thoughts in a mirror.She was once amedical student but dropped out halfway through.These days, she shows up atvarious social events as a psychiatrist, which the Foundation tries to prohibit because shedoesn't have a license.And she is also...an activist.An activist?According to Mr.Heinrich, she is meeting with a doctor named...
```

### [78] hash=`2c0908a54138cc3d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
Schwarz today.Schwarz, the family Dr.Carl mentioned.Let's try our luck there.Now then, Ms.Clara, Mr.Schwartz, only three weapons are allowed in the duel.The army knife, the sword, and the pistol.I believe the choice to Dr.Schwartz, for he has more experience in these duels than I do.It's an honor to fight you, and I look forward to ending your winning streak.Not so much an honorable thing for me.Please!
```

### [79] hash=`20879ec60f34518b`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
Pardon me, what is happening?A duel, ma'am.Just as Dr.Schwartz was demonstrating his therapy,Mrs.Clara barged right in.They were arguing, and this is how they decided to end it.To ensure fairness of the duel, the combat must happen within 48 hours of the challenge, but...I've never seen one take place on the spot.Well, I hope they know what they're doing.I don't want to get caught as collateral damage.
```

### [80] hash=`ceb1770d34ee703f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
That green dress...So she is Kakania.What do we do?If she gets injured, our mission will...Don't worry about people in that time.It is their life to live.Never intervene if you don't know the exact consequences of your actions.The course of history is more important than our investigation.This is investigator Greta Hoffman.What?Hold on.I'll be right back.Where are you going?The field agent squad needs to speak to me.
```

### [81] hash=`552cb93b23dc07f4`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
This won't take long.I will leave this to you.Remember what I said, Marcus.Dr.Shorts, three times he has been involved in duels and three times he has won.Impressive.This time he's still going for the pistol.But Miss Kakanya does not have an assistant and she has only one witness in this duel.This is not right.Why did she agree to this?She's being reckless.Even an Arcanist should have at least one assistant in a duel.
```

### [82] hash=`4e5e9d09495d97e2`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
I can only admit that you're right if you have to call a different academic perspective slander.A different academic perspective?Do you really think Freud and his petty tricks are academic?One could hardly find a vast insult to science than this!Is that so?Do you really mean that?Rumor has it that you taught the military the method of hypnosis for a price.Do you wish to clear things up here?Huh?This is defamation.
```

### [83] hash=`90a6b1fd8e0db5b3`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p7`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（07.公正的决斗.1/7 14:12）

```text
I have never been...Who is dueling here?Ah, it's a here.Come back yet?Miss Foundation employee.This is a quiet road.We're going to jump, Miss Foundation.Three, two, one, there we go!Start running.Seal off that exit!Don't let them get away!Got to sneak away before I miss Foundation.They won't leave you behind.I'll help you as you helped me.Kikanya, this way!
```

### [84] hash=`0557688c6c335e47`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
Kikonya!This way!Over here!Elige!Thanks a lot!The prop show came in handy!Finally!Why do I keep having things stick to my lips?Ha!Be careful with that!It is no ordinary beard!Every single strand was soaked in a bohemian potion, mixed with blood root, toad's heart, and yavingal.Why were the guards after you?Communication is not that hard.You've done this through before.You can do it.My my, Kikanya.
```

### [85] hash=`ae317545ea1bd0ff`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
Are you friends with government officials now?Times have changed indeed.I've been here for a whole year.But I've never seen an official without a beard.Where are you from?Croatia, Moravia, Belize?I grew up in Romania.Oh, I'm from Bosnia and Herzegovina.That makes us friends, since we're both from somewhere near.It's not an Austrian problem, nor a Hungarian problem.The central government sits in the middle, and no official has any idea of what's what.
```

### [86] hash=`170a70a77797a1bf`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
Should this be the Kaiser's concern?Or the Koenig's?Or both?You'd be the biggest fool to listen and follow these broken rules.Stuck in the system, nowhere to go, unless you work the magic of Crohn's.What happens if we don't have an Arcanum license?Oh, you'll love this!Who knows?You could get 3 days in detention or maybe 10 years in prison.Even if you are sentenced to prison, they might forget to bring you in.
```

### [87] hash=`c59b768308c21cc2`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
Or if you're an outstanding citizen who can shed your arcanum during your human re-education,you might get to have a nice life.Without a license, that is.Our justice system is much more unpredictable than the arcanists.We still have a fair chance of getting away.Very informative, Iriich.Oh well then, Ms.Petsa Kikanya and Ms.Foundation forgets I said anything.They are some alcanist kids on the streets.
```

### [88] hash=`7ee70c61316df03d`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
I'm surprised you know nothing about them.The country has changed, lady, and not everything in Vienna is as decent and sumptuous as thebuildings on Ringstrasse and Hengasse.Thankful for your help, Ms.Foundation, but so far I have returned to favor.You don't want to God's ease, do you?Fair even.So, can you tell me why you're here?My fees are reasonable, no one's ever complained.No, um, Ms.Kakanya, this is really coincidental.
```

### [89] hash=`f339fb0208af6078`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
I just happen to know that you are a psychiatrist.So?A psychiatrist considered doctors now?I think there's been a misunderstanding.Wait, I'm not here to check your credentials.Then what?So you call yourself Kakanya, but I know your first name is Clara.Surely there's no bureaucracy, no discrimination, no poverty here.This is a city of humanism and freedom.Oh, yes.Karkania.Kaiserlich Königlich.Or Kaiserlich Unköniglich.
```

### [90] hash=`b024f9acb6519f1a`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
And Karkania.The shit land.There's no better name for this country.So then...You did get that book.From a friend.Now's my chance.I still have one spider-tail Madame Hoffman left me, if I can find a chance to leave the spider-tail on her, or in her place.I'm intrigued by the book.Can I see it?By Samuel Weiss of the Field Agent Administration.Please confirm, Madame Hoffman.Yes.Report received.And I envy your light-heartedness and optimism.
```

### [91] hash=`a622265b0dd16200`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
They got you out of Vienna on such short notice, I can only imagine that must have been difficult for you as well.According to your intel, the Empire's had too many assassinations in a short period of time.This is not good for the critical point, Semmelweis.I'm in a good mood?Greta, I have more to tell you.I've pulled out to Vienna overnight, and I didn't have time to brief the new squad there.You know it takes ages to get through the briefing process, I might as well just tell you now, personally.
```

### [92] hash=`2cf349d9e0be8afc`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
There could be an Arcanist who has crossed the storm, and is now in Vienna.This is not her ritual.Something's happened.I'm surprised, Miss Marcus.You know so much about Tessera.My Salta Foundation was nothing but bureaucrats and book firms.Have you been to the secession building?Did you like it?Shame that book isn't there.Please, come in.Forgive the mess.I must say that it is at least more orderly than the administration of the Empire.
```

### [93] hash=`b68b55e5219d165f`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
Thank you.These are state props.Heinrich left them here.He certainly learned some useful things in Berlin.Make yourself comfortable.I'll get you some tea and look for the book.Please don't bother, Miss Kakanya.I won't stay long.I have to go back to the branch soon.I just need to confirm that you have that book with you at...Kakanya's arcane skill?Oh, Miss Foundation, it's okay.Just a little trick I use to ensure my personal safety.
```

### [94] hash=`30b74cb1cea798c9`

- lang：`en`｜version：`1.7`｜arc：`今夜星光灿烂`
- doc：`BV1Ar421s7wF_p8`
- title：《重返未来：1999》1.7版本主线「今夜星光灿烂」全剧情 - Reverse: 1999｜4K（08.镜面与提灯.1/7 15:07）

```text
I usually even charge for this.Look into the mirror, which reflects your inner world.This trick has been used by Arcanus for thousands of years.When it was first used, the Roman Emperor still ruled this land.Speaking of which, Miss Foundation.How did you know that the pistol was tempered with?Your arcane skill.The mirror.I am curious.No need to be alarmed.I'll treat you gently.Start running.Deep breath, Miss.
```

