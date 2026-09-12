# 剧情图谱抽取 · batch 035

- 角色：`wu_ming_zhe`
- 批次：**35** / 共 1 批（每批 95 块）｜本批块数：**93**
- 筛选：标题含「1.4」｜offset 405
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_035.jsonl`

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

### [0] hash=`00abaad9b57e0465`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
plank on the ship, she suddenly dragged me back.I thought it was only an inappropriate joke, but the next second, the plank broke.I was stunned, and asked her how she saw that coming.She just answered me as if we were talking about the weather.Because that plank is deformed like a rhombus.I was confused, there is the rhombus.Anyway, she saved my life, but that was not enough to settle the differences between us.
```

### [1] hash=`74c8c3f91daabc39`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
She remained rejective to working with the Foundation, and I finally gave up on the attemptto persuade them.My mission on that trip was not to make contact with them.Besides, what we needed was builders of the Storm Observation System, not some liarswho would only make things worse.As for the shelter they took from the Storm, she wouldn't say a word as if shedealing with a spy who tried to find out the deepest secrets of the Arkanists.
```

### [2] hash=`2a7202199bc1defe`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
In the end, he mediated between us.He gave me an address in Istanbul to which I couldsend the letters to contact them.After that, I spent more than half a year in the Egypt office.Things were even worse there than I expected.Some have gone missing after the storm.The people who were supposed to be in the Egypt office, according to the member liststored in the headquarters in 1985,but not there when I arrived.
```

### [3] hash=`5e493ff3e0d8d88a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
The situation could be caused by the limitationsof the transmission of paper-based materials,because the computer was not yet popularizedto every corner of the globe at the time.One minor mistake of a copyistcould develop into a huge difference.Besides that, the chaos inside Laplacewas an even worse issue.I learned that someone published the paperSamplings of global and regional chaotic energy route changes
```

### [4] hash=`b2303775ac15ff06`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
in the name of Butterfly of Lorenz.Apparently they secretly used our sampling sites,yet their research direction and conclusion were radically different from Laplace's.The research is equally divided into two schools.One sticking to the human technology they have focused onand one changing their direction to Arkanum.At the time, it was still too early to decide which direction was right, without sufficient experimental data.
```

### [5] hash=`41dd74e3c644f35a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
But many already believed that if time continued to be reversed, human technology would only keep falling into decline,while arcanum, which relies on personal ability, would rise again.It's true that gnosis cannot be copied, verified by an independent third party, or comprehended through reasoning.Its nature decides that it cannot lay the foundation of science or be popularized toevery ordinary person.
```

### [6] hash=`b7fc6a34bd649112`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
It takes solid marble to build a castle, not slippery sand.Even so, what harm will it do to rely on Arcanum, when the underlying logic of allthings has become unreasonable?Before the disagreement was settled, the storm in 1987 was predicted.We were ordered to return to the headquarters 24 hours before its arrival, but the predictionwas not accomplished by Laplace.A captive from Mennes Vindicte names
```

### [7] hash=`b0a9eff6f857e654`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
the precise date of that storm.Our enemies, those lunatic xenophobes,valuing only pure blood, made it further than we did.Yes, we built observation stations.We made countless deductions.We developed multiple simulation models.We made efforts.We sacrificed life.We did whatever we could.Yet the result was that we didn't find any other regionsimmune to the storm except the headquarters and another one in North
```

### [8] hash=`1b116a74037743f3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
America.In the end, 95% of the branch members werereversed.87.9% of the equipment was destroyedand 100% of our predictions failed.In conclusion, our endeavor brought noachievements.As for the captive from Manus Bendicte,the delirium patient who claims that oracles flowed under his parietal bone,When we asked him how he learns the precise date of the storm, he burst into laughter.Can't you hear it?
```

### [9] hash=`7de78316d9e19b99`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
Has God left you behind when he spread his grace?Then he smashed his own skull with a handcuff.Yes, there was no doubt.He was an incurable lunatic.But his insane nonsense was exactly the reason we survived the storm again.No matter how unreasonable or illogical it was, or how much a lie it sounded like.So we'd better believe we shouldn't go out in black today because the fish is swimming in the water.
```

### [10] hash=`da6e30a71691208f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
We'd better believe in the existence of the non-physical, everlasting, transcendent world where everyone's soul is a number.We'd better believe in the supreme existence which caused the disorder of time by merely casting its shadow.That means the life of individuals means nothing, more than rubbish, and the world is but animperfect ruin, for only the chosen ones will pass the trial, but the rest will be
```

### [11] hash=`c6c7fc26add0752e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
eliminated by the rain.How am I supposed to do that?Finally, I made up my mind to write to her.I didn't expect her to answer my questions.All I wanted was to confirm if she had survived that storm, for the sake of ourpeaceful talk about the Rhombus.Yet what I heard from them was a simple announcement of her death with only two wordsShe died then it burned and turned to ashes in a second on the same day
```

### [12] hash=`ddad3b966b631f2f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
The first and only timekeeper who just took officethe 12 year old childReturned alone from the stormShe told us the time in the outside world at that point and that was how I knew she was rightIt is right in front of you.If there is a god, why are you playing such a crank on us after we had suffered fromthe collapse of all the existing orders and the failure of all the great laws?If this is what she calls a glimpse of the supreme existence, the moment of a phlatus,
```

### [13] hash=`9be55f157b3ed501`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
do you have to present it in such a cruel way?The last two digits in the number of the year after that storm were exactlyher name, and her number.77.Incredible!It's true!Someone really made this prophecy!To know what we found!Ms.Sotheby, you performed as well as a formal investigator!We need to submit this report to your instructor immediately!What are you doing in other people's rooms?This is my personal item.
```

### [14] hash=`a2e94a3a14e7a3e8`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
You have no rights to take it.Please leave immediately.A personal item?This is a precious record that should have been submitted to the Foundation.According to Administration and Regulations for Dispatch Personnel, St.Pablo Foundation Decreed No.259,every member of the Foundation, when acting as a field investigator, is required to create a comprehensive investigation report of all directions and promptly submit it.
```

### [15] hash=`b2ca4716bd7f005c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
And they are obliged to ensure the authenticity, objectivity, and impartiality of the report.No personal bias is allowed in the content.If you have read this report, miss, you should know that it's not even qualified to be filed.I can tell from your uniform you are a student of SPDM or...This is Laplace.Do you have your guardian's approval to leave the school, miss underage student?Promoted monitor assistant of SPDM!
```

### [16] hash=`21f6140c7c42a675`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
My ID!They know a formal administrator of the foundation this monitor assistant will report every misbehavior of yoursEvery little bit of them our report hereThe great must boo and ish and I discovered some important informationI came to you and madam Z immediately after we read itAnish I didn't expect to see the second half of that report here in your room AdlerDon't call me that friend.Why not?Just call me enigma just like everyone else
```

### [17] hash=`56825db37c2a983f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
Relax, I know nicknames mean no harm, but I don't understand.How is a report filled with meaningless words of any concern to you, Madame Z?It provides information about the Arcanist Group Fertin is now dealing with.If possible, please give it to me.Of course.How can I turn down a request from Constantine's Chief of Staff?Take it away.I hope you don't mind the mold on it.I didn't accomplish it alone.
```

### [18] hash=`48375e9103d57007`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p26`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.缄默的悼词）

```text
Sotheby also played a significant role.Just to say, Ms.Boonish, you can start preparing the balloons and flowers for the twist ball-Speaking of which, this monitor assistant still needs to think about it.By the way, just call me Matilda.There will be no advance in human technology.You think so?Even thee, Madame Z, has given up on the study of theoretical physics and become a politician.No.I've never thought of that.
```

### [19] hash=`485b92534ecef2b3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
I am astonished by the fact that you were interacting with others.They broke in.If it was a complaint that you were making.You know it is within your rights to submit an interdepartmental complaint within seven days after the incident.Don't bother.That file means nothing to me.I didn't file it because it is a report against the rules.Why bother to submit such a log full of personal feelings and emotional behaviors to our great, rigorous foundation?
```

### [20] hash=`60241d938e3d2433`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
Is that so?I am gratified to find that you still have some sense.I too am gratified that you still have no idea that I was being sarcastic.Oh, that was sarcasm.Never mind.What do you want from me, Madam Lucy?You went all the way to this dusty rundown place so hurriedly that you even forgot to put on that pathetic mask.This is not because of some old files, I assume.Certainly.I hope you can be the cryptographer of the Manus Vindictae's ritual.
```

### [21] hash=`79f27aa90017f338`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
You are still the best.You are asking me, a human, to decode the ritual of a pure-blood arcanist group?I don't see how I'll be helpful to this project.You cannot evaluate your own level of being of value, Adler.Well, you evaluate our value.Test us in experiments you set.Prove the hypotheses by exhaustion,make mistakes, and start all over again.You repeat the process like a roaring locomotivethat pulls the research center out of this chaotic disaster.
```

### [22] hash=`2a26aa62a0ae5999`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
You question not what isahead of you, nor whether the path you've taken will be regular or easy.The onlyThe idea you planted into your little brain is to move forward, to improve.Thank you for your compliment.Credit goes to everyone.That was not even a...Miss Miragara.Guess you agree, a life without creativity is not worth living.And that's the life that I wake up to every day.I'm no longer the person you thought you came here for.
```

### [23] hash=`e4bee82e2c088375`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
I'll never be able to combine human technology and Arganum, and I'll never comprehend eventhe slightest part of it.I am useless to you.I don't expect someone made of tin to understand a human mind.But I beg of you, leave me alone.The work of analyzing the masks of Manus Pindicti did not go well.A side effect occurs in the researchers and it is getting worse.The isolation wards on the basement level are overwhelmed.
```

### [24] hash=`42924d004b089654`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
What a scene.Have you aborted the experiment?Not yet.We have conducted the arcanum imaging experiment on the masksand found a component which also exists in the raindrops of the storm.But knowing what it is composed of does not help explain how it works.What we're looking for is the original ritual that the menace cast on them.You are trying to figure out one's career planning from one's physical examination
```

### [25] hash=`0509dd43f2216956`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
report.I wonder why it is not working.Even if somehow you manage to find the original ritual, you still need a proper environmentto test it, which is the outside world with a coming storm.That's why we can't tell if we're getting results.Even if we had the right ritual, proper permission from the Foundation to traveland strong-minded volunteer subjects.Experiments performed in the ivory tower won't succeed
```

### [26] hash=`6a3f24438d6f7558`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
because...An experiment about the storm can only be done in a storm.Glad to see your brain is not rusty yet.It only took you three sentences to draw the conclusionwhich took the seminar a week to reach.That proves you are capable of the project.The history maintenance teamhas forecast different critical points of this storm.Foundation investigators are on their way.If Manus Vindicte still plans to accelerate the storm, like what they have done in 1929,
```

### [27] hash=`4d71587c0e667d27`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
there will be a high possibility that their people will show up at the transformation point of history and society,also known as the critical point of time, the center of the storm.Your sister, Greta Hoffman, is also one of the investigators.I have no interest in any Hoffmans other than myself.we have different perspectives it is okay I am just here to inform you that ifany of the investigators successfully send the information of the ritual back
```

### [28] hash=`480d17a6dbff4713`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p27`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.新航向）

```text
the research about the immunity of the storm will be conducted immediately takeyour time and be mentally prepared but once the storm alert is issued weonly have 24 hours to verify the feasibility of the ritual I wish youwill be fully prepared by then.One thing is for sure now,the age of humans has come to an end.
```

### [29] hash=`4ab5564a69c56387`

- lang：`zh`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p28`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（十四行诗的电话）

```text
司辰,是您吗?我是十四航师,请放心,这里一切如常,此次通讯并非紧急联络只是,无线剑小姐似乎接收到了您的信号,您需要我做些什么吗?抱歉,我,我听不清您的声音,我知道,您正在进行暴雨相关的研究,希望我没有打扰到您根据红弩剑小姐收集到的消息重塑之手似乎又在谋划着什么我担心他们的目的或许与您的暴雨研究有关我应该陪伴在您身边的在您回来之前我们会继续注意重塑之手的行踪也请您务必小心保重自己如果有任何需要请您一定与我联系我随时都在我得继续执行巡查岛屿的任务了之后见谢谢
```

### [30] hash=`949179956ae44b8c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
This is the official letter of appointment from the Foundation.Congratulations, Verton.After the long evaluation period and the re-examination,the Storm Reformation, Manpower and Discipline has been officially approved by the Pax Security Council.Team Timekeeper is now a legitimate, independent department.You are now granted a more flexible autonomy and independent budget.What was that?Budget?The Foundation will buy a sign, me a new ship.
```

### [31] hash=`1c79b8a528ceb021`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
Unfortunately, independent means doesn't rely on others.I can apply for a ship for you, but it's not guaranteed.Misers.Fine, not that I wanted an obsolete ship painted in grayish shepherd check.However, the price of passing that bill is to let the Foundation keep its authority to discipline unregistered Arcanists.The Arcanists who have been and will be assigned to the Time Keeper's team will be put through
```

### [32] hash=`bf22c0142370d056`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
a risk assessment procedure carried out by the Foundation.Those who are in lower risk categories only need to receive primary artificial sub-nemulismtraining while the high-risk ones will go to the School of Discipline.But I will make sure they will be registered as members of Team Time Keeper when theyenrol.I see.I have only one question.Are you still our point of contact for the Foundation, Madam Z?
```

### [33] hash=`aeb2069705ea4421`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
Yes, of course.Then I have no further questions.Meanwhile, Team Timekeeper can apply for secondment from the Foundation, Laplace, and Zeno, if necessary.You can check this file for more details.It stays the same.Keep investigating the storm and Manus Vendicti.You can make your own plans of action.The Foundation only needs a monthly report on the result.Oh, the fog is thick here.It used to be the nest of a Lete house, a kind of creature resting in valleys with abundant
```

### [34] hash=`36a6fd505f93fba8`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
water resources.What's more, it's winter now.I have to be the Erin girl.The Foundation wasn't even planning to give me a ship.Miss Sinetto is going through the procedures in the headquarters to transfer herselfto Team Timekeeper.Miss Druvis and Sotheby are on a break, for they have spent much time and energyclearing the woods and repairing the foundation square.Miss Lilia has been given an administrative penalty
```

### [35] hash=`584dbfd36dbac70d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
because she broke into the rehabilitation centre not long ago.This leads us to the current situation,where only the captain and this apple are able to act freely.So in the end was I, the renowned rocking pirate,the only one who didn't cause any damage to the foundation buildings?I have never felt so humiliated in my life!You're not planning on destroying this place now, are you, Regulus?No, no.Huh?
```

### [36] hash=`b7b74a9373e9f48f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
Who's here?Lillia and...a stranger?What took you so long?Fell into a gutter?Hello, Timekeeper.My name is Moisson.My employee ID is SF27602191908238X.I believe Madame Z has told you about me.I am now an official member of your team.As the field operator, she knows this place better.After I got promoted and transferred to the headquarters,those exciting outbound missions have been removed from my schedule.
```

### [37] hash=`8b2b3aee5c0c72a9`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
In short, although it's called the base,the only place unaffected by the storm is a narrow 20-meter long corridorno larger than a hunter's lodge.My former fellows had already searched this place from top to bottom.Those Laplace dudes had even sent in their lab dogs to search here inch by inch.Found nothing but some excrement of the aletios and the dog's own poop.There might be some clues that are invisible.
```

### [38] hash=`f8526c8dfd26cbde`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p2`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（2.藏宝地｜12/24 10:17）

```text
Regulus is a specialist in optical arcane skills.Maybe she can find something.A specialist?Well, I'll take that as a compliment.but for the record compared to searching hiding treasures is more of a pirate'slot so if it were up to me to hide treasures in this place please hold onfor a second captain Regulus the fog seems abnormally thicklucky you they hit the jackpot right away hmm there shouldn't be any ambush

Easy, Ms.Regulus.Please carefully retreat to my side.Ms.Timekeeper, please cover us.Will I offer your seat to the senior?A little trick.
```

### [39] hash=`0f0eed7295b44743`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
Hold on, hold on.It was a misunderstanding, Timekeeper.We attacked to defend ourselves.We are not the enemy.We are the investigators from the Foundation.These are our IDs.The base has been deserted long ago, right?What's the purpose of the investigation now?The outside world has been reversed to 1913.We are here to collect the lost scientific devices from the 1970s.Science and technologies are regressing rapidly due to the storm.
```

### [40] hash=`6710a872db621c66`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
Those old devices which used to be outdated have become valuable to us.I see.Do you mind us investigating this place?It won't be long.Sure.We are glad to give you a hand if you need a timekeeper.Good.I have some questions about the base and I wonder if you may help.So it was just a mistake.Back to treasure hunting now?Let's see what Zeno and Laplace have left here.infrared shotgun, a Magalev auto-feeder, Kato calibrator, my god, and a full box of Laplace's
```

### [41] hash=`8fb9f2394e5e945b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
military chocolate!Vertin, come check it out!Awkward stuff!MREs!Ahem, this pirate with aheart of gold wouldn't mind tasting it for you!I don't mean to rain on your parade, but evendogs won't eat those things.It makes Aletia's excrement smell better in comparison.That being said, to the best of this apple's knowledge, canine animals shouldn't have consumedany food which contains theobromine anyhow.
```

### [42] hash=`a1a3c1f0da08215f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
Then can I have it, or not?There is nothing to be worried about, since the captain is not an animal of theCanidae family.Well said, as befits the first mate of mine.Wait a second, Regulus.Show me the thing in your arms.why what do you want feel like my chocolate now no the supply box has myname on it true are there any other vertin in the foundation as far as I knowno one is caught by that name but me looks like an ordinary wooden box but
```

### [43] hash=`4dd5263543131077`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
these ordinary boxes are always the most dangerous so turns out we did findslacking off in autumn, and hibernating in winter.Practical Modern Incantations has now been reissued for the 77th time.We are now at the end of the 20th century.This book still remains the number one book on the list ofMost Regretful Purchase on Classic Score by the New Yorker.Biographer Erd has recently published her latest travel notes,
```

### [44] hash=`561be3da7c4c847b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
Roaming in a Peron, which has started a new round of crazefor traveling in the Aegean Sea region.The chief editor of The Voice of the Millennium strongly recommends this book, praising itto be the literary reproduction of the romantic, elegant and classical dreams, a glimpse ofthe golden era.Among them, criticisms abound.The Babylonian Review issued a warning that the author's observation of the Apollo
```

### [45] hash=`c8ce79bb19ee76b5`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
star was fatally inaccurate.Self-driving tourists can easily get lost in the Gorgon current backwash if theycorrect their direction by 3.14 degrees on the forward sextant Model T.Time for late night news.What?End of the 20th century?Voice of the Millennium?Is this radio broadcasting news in 1999?Just as I suspected.Since Timekeeper hasn't reported the time of this era to the Foundation,you two, as the Foundation's investigators, shouldn't have known what year this is.
```

### [46] hash=`f16e10c4a9d02d60`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p3`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（3.压箱底｜12/25 17:32）

```text
In such pouring rain, time is the best proof of identity.Huh, I get it.Not a bad plot.Miss Morzon, watch your six!Let us help you!Didn't expect them to be clever enough to disguise themselves as the Foundation's investigators.They sure have learnt a thing or two.The era of 1929 only lasted for two days.The frequent change of time muddles work and responsibilities in the Foundation,
```

### [47] hash=`2ad3e02792940510`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
I will explain all of these as briefly as possible.Good news.The analysis report on the mask you submitted to the Scientific Computing Center is nowavailable, timekeeper.We've found the same component in it as the raindrop from the storm.This is a component named asymmetrical nuclide R by the Scientific Computing Center.Its name comes from the bifurcation structure it presents under the Arcanum imaging.
```

### [48] hash=`c62cf94ce213985a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
The Scientific Computing Center has also run some tests on the samples of the raindropsyou previously submitted.After removing all water, mud, human hair, and dandruff within, the remaining unanalyzablecomponent is what we called asymmetrical nuclide R.What a familiar name.But it disappeared right away and we only have a photo of it.Fortunately, we extracted the staple form of it from the mannus mask.
```

### [49] hash=`64713c2dbdf5d87f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
It might be the key to staying immune to the storm.Does that mean it'll be possible for the Scientific Computing Center to develop protectivegears which are immune to the storm?Like the Manistas?Seems to be so.A credit to you.The whole center is crazy about it.And I'm responsible for passing along the good news on behalf of my fatigued colleagueswho stayed up all night and suffered from neurasthenia.
```

### [50] hash=`86b3a074ae0b9fd7`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
We need more samples.Fortunately, now we have another direction.Oh, and these are the files you asked me to search for.Luckily, the SPDM library has every single issue of global arcane geography since the1960s.Also, Ms.Sotheby accepted your request.Thank you, Senetto.With these files, and the help of Regulus, that should be enough.What else do you get except for playing dumb, you cunning flower-headed tin box?
```

### [51] hash=`198f8f58570a2932`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
Speak!Tell us what you know!Like, what were you doing in the Illitial's base?In what way are you associated with Manus Vindicte?And who put you in that box which has Vertin's name on it?No idea.And those ridiculous radio programs, end of the 20th century,voice of the millennium and roaming in a pyrene...Don't waste our time.Otherwise we have no choice but bathe you with this bottle of vodka.Geez, do you really mean that?
```

### [52] hash=`9176443f790a29db`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
Anything less cruel?Formalin, of course.I never waste my drinks.Yeah, that's more like it.But I...I really don't know anything.I'm just the receiver of signals.Please believe me, when I woke up I was already in that box.This interrogation won't get us anywhere.Sotheby and Juvus are still on leave.They will not take part in this action.While Miss Morzom will stay put in the Foundation's headquarters as our contact.
```

### [53] hash=`09f286588563f613`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
Wait, a field mission?Didn't we just come back from that Illitial base?Besides, where is this field?The Apollo Star we just heard about means the sun.The Ford Sextant Model T is an arcane device produced in the early 19th century.The Scientific Computing Center has one of those as a part of their collection.The Gorgon Current is mostly created in the Aegean Sea, near the Balkan Peninsula.I remembered an Arcanum magazine in the 1970s, had a detailed article about this, and introduced
```

### [54] hash=`3f9630776f5a6c9f`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
the Circulating Current.I read it in the periodical room in SPDM.The current will be flowing backwards every time the Earth is at Ophelion and Perihelion.This is also known as the Current Reversal, which is, on the third day of JanuaryJuly this year and the time in the outside world is January the 1st 1914.Are you saying that all those broadcasts are leading us to an actual place?I thought we'd have a nice break after this.
```

### [55] hash=`69b0a550dace603c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p4`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（4.出航日｜1/1 09:50）

```text
Regulus, you're going for a ship, haven't you?I tell you that I've got you one.Now hold on a second.Come to think of it,It wasn't the flower-headed radio thingy who tricked me into the Aegean Sea.It was......Virgin!Watch out!The big wave!Blyat!This is enough!S-U-N-O-L-A-D-I-N-W-E!Wait, Lilia!Are you sure about taking off in such stormy weather?This isn't a normal storm.Something is attacking us from the ocean!

I need to pull it out!You guys go study that whatever instruction right now.Ha ha!I finally got you, damn bastard!It's my turn!WDW!How many wins?Swallow my exhaust!
```

### [56] hash=`48cc98d0a734548b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p5`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.坏钟表｜1/3 08:45）

```text
Field Mission Evacuation Instructions, Article 21.Whenever there is an emergency, the fieldofficer may send them SOS code with their wands through any transmission device withround buttons on it.Any Foundation member nearby will provide immediate humanitarianaid.To send the code, please turn the knob one time to the right, half to the left,oh you have guts and I appreciate it bring it on speed up my friends we need
```

### [57] hash=`df3633915b01a16a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p5`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（5.坏钟表｜1/3 08:45）

```text
to rush back to the Balkan Peninsula for another mission everyone please wait aminute the size of the sea monster it's shrinking what's happening now it'sgone out of sight oh I have a bad feeling about this not good it'scrawling into the cabin it plans to tear the ship apart from me insideEveryone watch out!Oh no!Your watch was wrong.Pardon me?Your watch was wrong.Are you talking about my pocket watch?

Your watch was losing time so I fixed it for you.I...I don't understand.Do you mean this is the right time?Yeah.This is the year 2007, is it not?
```

### [58] hash=`3cd582c5e2546832`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
You're saying we're in 2007.Do you know the storm is that how you call it?We call it the emanationThe tide of Numa is pouring down from above and convergingIt would raise as a tsunami and break the world of matters where darkness abounds.I don't understandThis shouldn't be hard for you to understandYou are also a real number.I am 37In fact, 1999 is nothing special compared to 1991 and 1993, however, 999 is a brilliant
```

### [59] hash=`efddd81d8d9617cc`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
number.It is a Capricorn number, a palindromic number, and the largest three-digit natural number.Sorry to interrupt, but I only meant to ask about Erd the biographer.She'd been here on this island and written a travel note called Roaming in Aperon.Does the name of the book ring a bell?I am sorry.I have no idea about the fragments of matters you are talking about.Fragments of...matters?Captain, you should go.
```

### [60] hash=`878c09e8c78d11de`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
This apple's arm has...Mr.Apple, stay with me for a little longer!Shush, you wicked dolphin!Mr.Apple is not your breakfast, nor are my records!Isn't that Vertin?Fertin!Are you done with the standing and staring?Come give us a hand!Thank god you were here, Fertin.Mr Apple and I were this close to being made a stargazy pie by these clever bastards and served to the dinner table.You've also been incredibly helpful, Regulus.
```

### [61] hash=`837f0758d6574589`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
Is that so?Like how?You rebuild my confidence in communicating with people.Have you seen Sinetta and the others?Now, we only need to find the captain and his team members.Sonneto...These people are...They are the Apuron believers.They lent us a helping hand after the ship went down.Not at all.An integer is under an obligation to help his kind.Miss Sonneto, have you found your friends?Yes.Only the members of the Razor Squad are still missing.
```

### [62] hash=`cd737a356a942198`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
They also belong to the St.Pavlov Foundation like we do.The Emanation.Please grant us entry to this island so that we can share them.Timekeeper?I'll explain to you later.Trust me.Please, Seneto.Come this way.We will talk.However, only integers and fractions are welcomed here.No irrational number is allowed on this island.Throw her into the sea!Deadpool!We gotta let the past be the past, like how we deal with old newspapers.
```

### [63] hash=`f1acb38e68595742`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
Because all I speak is one simple fact after another.Anyways, we will keep each other company for quite a while.Finally a question about yourself.In front of you is a boundless sea.All you can see, besides the beach you are lying on, is water, water, and water.Not even you can avoid asking this questionBut a kind-hearted soul already told you that time is moving forward as it used to bestep by step
```

### [64] hash=`45e61026cc28c541`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
So the time isThe year 2007YesTime is back on the right track going where it's supposed to beRaindrops literally drop again and no one goes back to the past anymoreSome miss the good old days, though.Oh, you still doubt it, don't you?I can see it in your eyes.Don't get me wrong, I'm on your side.After all the hard times I've experienced,if anyone told me that my life was just a boring dream,one neither good nor bad, I would throw a shoe at them.
```

### [65] hash=`132284e1fca183ce`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
I can tell you are being burned by anxiety,but to find the time you want,We need to comb through the situation like how you do with your hairTime is like a soccer tort and now it has been divided into many pieces on the largest pieceStands the white chocolate cardYes, the last good days of the 20th centuryThe gentlemen are still growing handlebar mustaches and the ladies have not yet flattened the curves on their bodies
```

### [66] hash=`d09f45c9610c6d84`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
New money buys one art piece after another to show off their good taste.They don't even mind turning their homes into museums.A cafe named San Marco officially opens,gathering the most outstanding intellectuals and writers of the time.They talk and laugh there, as if nothing could stand in their way.Then, the cafe receives a neurologist,whose briefcase carries the interpretation of dreams,And celluloid film and projectors become a new means of expression for artists.
```

### [67] hash=`7694f87f526ed67b`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
At this point, helmets remain intact in the warehouse.Gauze only works in hospitals.Bullets only fly in the firing range.And the flame that swallows lives is not even lit.But soon, soon enough, the young people who swore to retrieve their homelandwill take up daggers and guns to fulfill their oath.Buildings will shake like a leaf, and rocks will fall off and hit the walls.Screams will try to break free from people's throats.
```

### [68] hash=`cefa183a8bf95b17`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
And at that moment, a clip will be loaded secretly in the name of supreme honor.The golden age is about to end.A vortex of blood is already swirling in the river of time,waiting to devour everything that passes by.When that actually happens, all the beautiful curves derived from nature, the B-shaped brooches,the punch, the eiderdown duvets, everything will be destroyed, leaving only an insurancecontract behind.
```

### [69] hash=`9c88b3ee2c1a8071`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
And it doesn't even work.Even this cafe will be smashed into concrete pieces.See?We have combed the hair now.Everything I just talked about is the time you want.You wouldn't buy the nonsense about the fairness of time when you reach my age.It actually feels different between those who keep their eyes shut and those who keep theirs open.Likewise, those who kill never share the same feeling with those who are killed.
```

### [70] hash=`42423b073ca86ae3`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p6`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（6.数字王国｜1/3 10:00）

```text
This is also true between those who have enough food to eat and those who are starving.Alright, that's it.I've talked enough.Now get up, darling, and brush the sand off yourself.Trust me, you will find your own answer to this error.
```

### [71] hash=`fd19167f2a622643`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Yes, all is well.Those dolphins sent us to the other side of the currents.And one more thing, Captain, and I'm asking this with no ill intention.Uh, may I know your lineage?Thank you.I wish your next mission would be trouble-free too.The members of the Razor Squad are all humans.It's clear then.Real numbers refer to Arcanists, and imaginary numbers mean humans.Then what is the rest of this nonsense?
```

### [72] hash=`69f0cb952612d12d`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Seneto, Vertin and this apple are integers.While Miss Lillia and I are fractions.Don't bother asking, I'm pure blood.This apple is also made of pure apple juice.I only consume 1.5 volt DC.So it's not determined by our lineage, or Regulus would have been an integer too.Am I the irrational number?Might as well play us some rock music.Seems the residents on this island venerate integer numbers.And irrational numbers, or the non-terminating, non-repeating decimals, cannot be represented
```

### [73] hash=`bfb051a16a27a593`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
as the ratio of two integers, hence they are discriminated.No, no, no!Who are they to judge and decide me to be the irrational number?I was the only person who didn't cause any damage to the Foundation in the previousprotest!Why do I get to have the worst of both worlds?I've requested information from Ms.Moson about a Pyrron, but it will take some timefor the files to come in.The captain of the Razor Special Operations Squad told me this might be a settlement
```

### [74] hash=`d3adc80ab3a7c968`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
of a group of Arcanus who have been long cut off from the world.Unlike other unregistered Arcanus, these people chose not to live alongside thehumans.They still lead an ancient Arcanus way of life and follow the old customs.The travel notes in 1999, Manus Vindicte showing up in a Littial's base, the storm, or emanation,they must be somehow connected.And we'll find our answer here, I think.Very energetic, Captain.
```

### [75] hash=`456b95158ab48375`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
By the way, how come nobody is here to welcome us?They wouldn't suddenly decide to detain us all just because we have an irrational number here, right?I'm with you all the time.The biggest, worst, and ugliest crime.People eating beans will never transmigrate.They deserve nothing but eternal punishment.Serious?This rule only for soybeans?What about broad beans?Snow peas?Chickpeas?And what does it say about other bean-based products?
```

### [76] hash=`61b9ab9e71d3c67a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Beans are beans.You're funny.This doesn't even make sense.By this logic, aren't the coffee drinkers going to rot in hell?I happen to have a box of coffee beans in my bag.If I put one coffee bean in my mouth, will the vulture get me right away?No way!Whoa, easy mate!Do you want to get physical?This pirate is not scared of you!The critters are coming to your aid!This is not good.We need to separate them.
```

### [77] hash=`1ebecf40a743312a`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p7`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（7.豆子罐头｜1/3 12:10）

```text
Martin!Sunetto!Lily!What is going on here?37, let go of the guest's head.Now sorry that I'm late.I'm Sophia the corrector of a p-run.I will take over from here.OhFinally we have an ordinary person herePlease let's talk on the way to the outside
```

### [78] hash=`788ec6e67459a9c6`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
We believe everything can be translated into numbers.Things are made up of numbers, and mathematics is the key to opening the gate of truth.It is like the fire that lifts us from the darkness.This world may decay in time, but numbers will transcend the limit placed for all otherthings in existence.And if one can take up the challenges, and improve oneself with practice, they mayPlease repeat all the taboos on the island.
```

### [79] hash=`a68731391da7a9c9`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
It was too dark in there.I didn't take them all downWorry not mr.Netto.I have them all recordedoneabstain from beanstoDo not pick up what has fallenthreetouch not a white roosterforDo not poke the fire with swordsfiveDo not jump over a crossbarlike you.You are a very typical irrational number.Irrational numbers aredisobedient, sometimes unreasonable, and they hardly play by any rules.Just likethe non-terminating random numbers following its decimal.
```

### [80] hash=`4debe80f7cbeaa75`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
These numbers arethe floating points, or the noises.People of this type are the random oneswhose actions show no pattern whatsoever.Disobedient, unreasonable, neverOh, it's you again!I won't be bettered in a fight this time!Thirty-seven?Shouldn't you be off preparing for the doctrinal meeting?Vix asks me to take care of our guests.But I'm usually the one who receives the guests.Engaging with strangers might be a little difficult for you.
```

### [81] hash=`3751a905bdcb3a88`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
There's no cause or link in these two events.People always bother you with trifles only because you're fine with it.Do not sleep on a grave, and do not cut wood on a main road.Idleness is the cause of the breakage of one's flesh and soul in the long journey of perfecting oneself.Those who have not yet found their numbers have even fewer excuses to be indolent.Besides, why would you place the head of a ghast in your mouth?
```

### [82] hash=`1255b38d797dce14`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
She said she's going to eat beans.That does not justify your action.Conspiring to my face to throw me in the sea.Mind you, this pirate's tolerance has limits!Right in the bull's eye.What's that look on your face is?An eye for an eye, a tooth for a tooth.I didn't start this.Regulus, did you just pick up the grape that 37 threw at you earlier from the ground?Did you just...violate the rule of not to pick up what has fallen?
```

### [83] hash=`3c3d3d710c3f44a8`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
What?A Braxxus incoming!It will take the offenders with it!A chicken's head and two snakes as a feat!What?What on earth is that?This is not good.They seem dangerous.Regulus, come to my side!Who dare you?Regulus!Captain!I can't leave her alone.This apple shall follow her.A toast to Regulus, to her ever-fighting spirit of breaking away from jails, no matter howmany times she has been put behind bars.
```

### [84] hash=`d48861f2d77f4a02`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p8`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（8.旧诫言｜1/3 12:42）

```text
Luckily she didn't have any beans.May her soul be cleansed in the dungeon.What a mess.Ena eftagramot mima, simatizate otan enosume dio semia.The arcane skills cast by the congregation on this island are very different from
```

### [85] hash=`82396138054ead51`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
Before you enter the Great Hall, please place your right palm on the stone and swear toit solemnly.I wish to be baptized in the water of Gnosis and be rid of the long darkness of ignorance.I ask my tongue to be taken, for it has spoken mindless words and I shall stay silentfor the truth.I choose to leave the fragments of matters behind me and enter the Great Hall ofas clean as a newborn.I swear to let matters stay in the world of matter and
```

### [86] hash=`10f11d343ed1476e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
a form in the world of forms.I swear to reveal no secrets or my heart shall betaken by the vulture, my body consumed in flames, my soul trapped in the endlesswheel of birth.Now knock three times on the stone, put on these ceremonialVertin, are we really going to do this?That oath we have to make to enter the hall sounds vicious.To stay quiet and keep the secrets.It's similar to the training we once received.
```

### [87] hash=`f3b0e4b21097dc9c`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
I can go inside on behalf of Timekeeper.No, I'll come with you Seneto.I can't sense any sign of arcane skill on this stone.The oath is more of a formality than a curse.The warning is lifted then?But when Sophia repaired the floor in front of us with her arcane skill, there's no fluctuationof arcane power either.I can't even sense the slightest signs.It's either a kind of arcane skills we're not able to detect.
```

### [88] hash=`ffc58945e7651c62`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
The moment we stepped onto this island, we've been trapped in a tremendous ritual.That's to say, any Arcanum used on this island is only a part of this giant flow.We don't know where this flow is leading us.We know nothing about it.It's too perilous, Timekeeper.I know, Zanetto.But as long as we obey their rules,we won't get into other trouble.The doctrine of the Aperon is to live in solitudeand seek nothing but the truth.
```

### [89] hash=`6f549f2af1a655ee`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
In fact, they've never beenaggressive towards us.I think of this differently.Think.The pure-blood Arcanist community,the unknown Arcanum power,and the obsessionwith certain knowledge or identity sound familiar yet we haven't spotted anytraces of the manners here Maynus vindicte is like the rat living in thegutter I don't think they will let go such a favorable chance which means weneed to find out the truth I believe in timekeeper I have zero interest in
```

### [90] hash=`4bd057ae0bf26561`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
this meeting I'll stay outside to keep a lookout take care I wish to beLast was the loss of the grand unification of different lineages.The truth was buried, and history was rewritten.But the emanation is not a crisis.Instead, it's our last salvation.The supreme existence has once again shown itself to us.The door to the everlasting, transcendent world of forms has opened once again.As Numa pours down, things are rewound to the World of Light.
```

### [91] hash=`d3f728f5011b353e`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
Everything in the World of Matter breaks into pieces, for they are as delicate as a petal before it.We, who have the honor to witness the emanation of Numa, have the privilege to survive the turning of the Wheel of Birth.Because we know the truth, our survival is destined.It is the beginning of a mission to bring the unseen truth into this world.Thank you.The next orator is 37.Our smallest irregular prime and the brightest star of Hermes.
```

### [92] hash=`01283d3bcb306122`

- lang：`en`｜version：`1.4`｜arc：`洞穴的囚徒`
- doc：`BV1kN411s7xt_p9`
- title：《重返未来：1999》1.4版本主线「洞穴的囚徒」全剧情 - Reverse: 1999｜4K（9.噤声之席｜1/3 14:00）

```text
The emanation in 1929 only lasted for two days.All methods to calculate the Numa emanation failed.We found no pattern in the occurrence of time reversal.All our efforts in the past four years have gone completely wasted.That's the end of my speech.Reña sereno, intenso e infinito.Who did that?Who broke the silence?Sorry, Timekeeper.I just...Get ready to run, Snetto.The Abrepsises are coming.You want to offer your seat to the senior?

How dare you?Right wind.
```

