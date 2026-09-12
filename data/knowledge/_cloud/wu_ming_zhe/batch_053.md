# 剧情图谱抽取 · batch 053

- 角色：`wu_ming_zhe`
- 批次：**53** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「1.0」｜offset 285
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_053.jsonl`

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

### [0] hash=`a9236a3d4bcc31c8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Contribution!I'm going to try it for my family first.Isn't that okay?My lady, it's really hard to understand.After all, I am the woman who escaped from Druvis the Third.Compared to any of you, I know what death tastes like.You mention her a lot.Is it only me he does not know, huh?I have read her investigation report.She's the stepdaughter of a Washington State Forestry tycoon.You mean the Weyerhaeuser?
```

### [1] hash=`dcd2ad4a6e98ddd3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Master once dealt with them.However, the family suffered a great deal of misfortune.Be careful, everyone.We have entered the area of the relief shelter.Has risen in the woods.Myself, Diamond, a little dizzy.Come here.Hold your breath.The white fog should be a protective incantation to hide the relief shelter.It is now 35 minutes to 10.The refugees nearby are not well, and the guards are doubled.From now on, everyone please proceed with caution.
```

### [2] hash=`d5dbedc2a543c4f4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Ensure that you are not disturbed by the fog.Yes.Patients in the structure zone have also taken the potion.They are feeling a bit better.What's that smell?You just gave it out before he sampled them?The press is here in no time.You have to be fully responsible for any accident.The press?Aren't you the ones who want a press conference just to show off what the arcane is doing to relief?Hey, give me some potion.
```

### [3] hash=`e9bc1c22cc91fada`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
These toad freaks.I didn't know there would be press today.Forgive me that I want to hold a banquet before the storm, Miss Druvis.After all, for us, Manus Vindictae, this era is no longer of any value.The potion, and it tastes so familiar.The smell!I knew it!I knew he can't trust these insane people!Insane?More sane.The ridiculous and absurd decrees.The Prohibition has lasted for almost ten years.
```

### [4] hash=`f4e2b035d7d9b7bb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
How could you know its being?Or forget me not.The fall has gone.No need for more blood.What makes you doubt, and everything here should be doomed?It is not destiny.It's themselves after bankruptcy.No, not self-burned.Their daughter who studied dark magic burned them alive.I said if I take a photo of her before I die, move!Let me take one!No, don't do this.I have not studied dark magic.It's said that you always objected to their plans of cutting the trees and selling the woods.
```

### [5] hash=`81c09cd9d79f9ef6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
So they did it at midnight to avoid you.However, you were at the scene of their death.To tell them of the new arcane scale.You hear the sound of trees.I know there is a way to make us all survive.No need to level up trees.No need to file for bankruptcy.we can go back to the life we had the kind of life they expected so you chooseto escape the dead by burning down the woods I will find the arsonist
```

### [6] hash=`74d6294befee1505`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
I will not let the woods grow I will defend everything about them I willyour blessing once brought me fortune and hope now I will give this blessinglive to see that day.So, you left in such a hurry just to get your accomplice, Bumblebee.It's time to clean the garden, my disciples.How can we get in?I've already heard theTime Keeper's voice.She's close to us.She needs help.The Arcane Skill on the Fog is far
```

### [7] hash=`a4b592566260da6b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
more powerful than ours.It's countering us.I can't wait any longer.I don't want it to beLike the last time there must be a way to focus all of our arcanum simultaneouslyAs long as we're more powerful even just for a second as long as there's a breachSometimes things can be fixed without arcanum.It is also a good way to learn from human experienceSo the reinforcements sent by the Foundation are you guys?
```

### [8] hash=`8167d28e6fa3725e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
excellentFinally we catch up.I'm cream crackerNo worries, Sonnetto.We will rush in and meet Vertin.What did you just say, Mr.X?Is there another way?The essence of arcane power lies in the intuitive insight into everything.And our human friends are good at logical deduction based on awareness, which is rejected by the Arcanists.Since we can't beat the Manus in terms of Arcanum, then...Why not try to use a counter-intuitive logic experiment to open the door of this protective incantation?
```

### [9] hash=`4f4caae603954e64`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Anyway, as long as the caster can be interrupted, anything is fine.Are you going to avoid the surveillance of the fog and go directly in to break the incantation?What counter-intuitive experiment will you do?Check it out.The next experiment is, within three minutes, use this copper pipe to boil a pot of water in the distance.Please hold on, Timekeeper.Reinforcements are coming right away.There are so many of us.
```

### [10] hash=`118c25f28bde369d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
How many rounds can you make it through?Your good luck won't last long.Despite the coming storm or the Foundation's reinforcements, there is only one ending to your story.I don't care about the words of a dying man.Miss Druvis, I found the truth for you.The culprit to blame, the arsonist, is right here in the shelter.As long as you keep your promise to stay.It's not important anymore.Not important?
```

### [11] hash=`40f11ce8fca15549`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
He ruined everything with just 20 barrels of gasoline.That's him.A firefighter who lost his job because of the depression.Thought that putting out a fire could win him his job back.Look at those hands!They set the fire, burned your families alive, burned your woods into ashes.How could you?How could you even forget such pain like that through this?Mr.Forget-Me-Not, help in the flames in the past, for your compassion for someone you've never met.
```

### [12] hash=`16f36997526892f5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Today is just the same as before.In the past, I tried everything to protect something.But before I knew it, I already stood on the opposite side of myself in the past.My woods will not perish.They will live with scars, and new shoots in spring.They will look haggard, but at the same time, they will stand upright.They will continue to grow, recording everything about their own history,territory, residents, and an anecdote of a reckless firefighter in the 1920s.
```

### [13] hash=`e9e408d04766b238`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
They will keep going upwards until they cross the millennium.Please allow me to bid you farewell, Mr.Forget-Me-Not.Understand.We belong to the future.Isn't the spring already here?I think I should go back to where I belong.The Forget-Me-Not flower field!I wrote about the place!Rainier!Next time you see a wounded snake, don't save it no more.Smear its tongue with the ashes of the spirit.Well, what is that man going to do?
```

### [14] hash=`25d37126c1d9bbdd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
What a terrible Arcanum fluctuation.If I knew it, I wouldn't have come in.Are you having a quarrel?Looks like it poured at a bad time.Thank you for...Sinetta, Brigulus.You're not hurt.That's great.I'm sorry.You protected me when the fall fell, but I could not save you, even let you confront the madness alone.I'm sorry.Your hands are trembling, Seneta.Calm down.You did nothing wrong.We are together now, aren't we?
```

### [15] hash=`ace742675a454ca3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
There are more challenges for us to take.It's not the time to catch up.You're right.We are late, but not too late.Timekeeper, I'm so glad that you are safe and sound.What comes next is the final battle.This time, please let me protect you.My lady, stand behind me!This is intense.The number of the injured on both sides is still increasing.We have assembled so many combatants.But if that's the Manus' power, I will then need much more training.
```

### [16] hash=`4a383bbd001706e4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
You are all bleeding.Sacrifice thy body.Conduct forth carrying sorrows.Vertin, the saviour that people follow.Blessings be unto you, whose people shall be no more in ours.Least thou be in the sky.The enemy is coming!Everybody protect yourselves!It's raining.Holy shall be.Adieu.Keep the shadows fast.Please everybody, hold on!It's really thrilling.I don't think I'm good for the fieldwork.Those who are not injured, please take charge of the inventory and gather all the refugees.
```

### [17] hash=`22f48d1c7c9fccb1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Whose people shall be no more?Six hours left.In the following time, symptoms will get worse.The influence scope of the storm syndrome will be further expanded.How shall we spend the last hours?And what can I do?Let's hear everyone's wishes.How about that?Schneider?My lord, you're actually lying here defenseless.I've been with you for a long time.My lord?No way.Schneider?How did we get so close to her?
```

### [18] hash=`ee18b837beaae3ae`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Senato.Timekeeper, the supplies have been counted and are being transported to the headquarters.The refugees are also being settled.I just received the news that here is not the main target for the Manus.This morning, Arcana led other members and robbed a large amount of supplies from Washington.What is the next mission for us?The storm, it should be coming soon.Yes, Senato.This time, I want to hear everyone's wishes.
```

### [19] hash=`dff10b332b69dfc2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
How could there be such a big crystal ball?yes if this was the last moment in your life what wish would you want to make myLord are we gonna die we are starving for too long my Lord I want to have dinnerwith my family for us Italians that's the best moment of life have no wishwhat is your wish may I realize it for you a few refugees have already passedMiss Sotheby prepares for everyone tonight.I didn't know you prayed.
```

### [20] hash=`cab41c9de0c338f5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
You're the last one to tell me your wish.Although you won't go, I still want to know.Do you want to hear my wish, my lord?Then my wish is, don't forget me.Well...Instead, how tiring it is to cook.Nearly we delivered the meals to all the refugees,but our soup became cold.Oh?Well, thanks to your hallucinogen, what I see happens to be a parfait.It also tastes the same.I had the souffle.Miss Sotheby, thank you for the meal.
```

### [21] hash=`30a793cb2cc5044b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
Fillet steak?Sorry, I gotta have some more.What is that taste?Tastes like corned beef, dust, and baseball gloves.Someone just wearing it.What you say if you don't believe it from the bottom of your heart even the hallucinogen won't help.Don't be fooled by the storm.What I prepared for you is definitely the best food in the world.Happen to you.Is there anything that doesn't suit your appetite?No.It tastes amazing, my lady.
```

### [22] hash=`c32a62238e47d1e8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p5`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第二章.夜色温柔｜8~15）

```text
What did you eat, Mr Carson?I can have one more Santa Maria, look after us have compassion on usDon't be afraid, take my hand, close your eyes just like when we were bornEverything will be fineGoodbyeMy LordSchneiderI'm sorry, your familyI'm sorry.I'm not a real Arcanist.What do you mean?I don't understand.I always wanted to be lucky, but I think I should say adio now.Adio?You mean the stone will also...

You've never eaten the gold bar in front of us.Are you always tolerating it?Now it's coming, my lord.Don't forget me.Don't forget my heartbeat on the right.
```

### [23] hash=`0312bbb8685cd951`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
What Arcanist regard to be more important is the knowledge from another pathway, which is often known as gnosisCompared with mankind's knowledge gained from reasoning.What are the features of gnosis?Seneto features of gnosis are one it cannot be verified by an independent third party andTwo it is impossible to be comprehended through reasoningExactly.And that's also one of the reasons that the knowledge of the study of arcanum
```

### [24] hash=`3036dad14cb4e098`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
is hard to be accepted by the academic world.The academic research is required to be opento the public and can pass the independent tests.But the unpredictability of arcanumwill lead to the arcane researches to methodological agnosticism.Thus, all the trainings and the scientific stabilizing appliances that the school providedfor you is to overcome the instability of your arcane skill, in order to ensure the
```

### [25] hash=`1599736ce54437ab`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
peace and stability of the human world.It'll ease me...I was almost fast enough to answer this question.How could she be so fast?Next question.After the fall of the Roman Empire, the number of arcanists, along with the relatedliterature, have reduced correspondingly.Who can tell us the history of that time in brief?As the Roman Empire declined, some Arcanists were tempted by the irrational side of their
```

### [26] hash=`905c68d5dfa51df9`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
nature and applied Magia Naturalis in warfare and disputes over interests, which irritatedthe Church and other powers of religion.At that time, people in Europe widely considered Arcanum to be the paganism that collaborateswith the demons, hence the trials against Arcanists.In response, Arcanists struck back fiercely.However, due to their spontaneous character and the unpredictability of their whereabouts,
```

### [27] hash=`eea58339d8e660a8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
their communication was unsuccessful during the fight.Both sides struggled in repeated battles.In the end, mankind, jointly led by both their religious and secular leaders, prevailed.She's wrong!I know, I know the right answer!Alright, give it a try, Matilda.I know!It wasn't Arcanus who started the war.The attack on Constantinople was waged by lordships in western Europe to ransack the capital for resources and the literature of Arcanum.
```

### [28] hash=`64969efdd21f5b28`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
The nursery rhyme my grandpa sang for me tells me all about it.Long ago Arcanus weren't called by this name.They were once gifted philosophers, diviners or doctors until they were put on the labels of pagans, freaks and witches and isolated by their people.They were entirely forgotten.The next time people saw them, they had this new name.Arcanists.Inspiring.Do you remember its name?Never told.How about the melody?
```

### [29] hash=`2f15dd4c60b1e4f4`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Could you present several lines for the class?I think it was like...That's not it.Here, I...I can remember it.But still feel confident enough to answer the question.Shame on you little thingSit down, please MatildaSonnetto is correctMatilda you have just transferred hereIt may take you some time to get used to our curriculum a rhyme can be used in studying folkloreBut it's still different from a formal historical intelligence
```

### [30] hash=`b403ce8f2bcfafb1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
classPlease turn to the last question at the test after the Ottoman Empire sees control overConstantinople, Georgius Gemistos, a member of our Charon commune, also anArcanist and philosopher of the Roman Empire, traveled to Florence.He broughtone classical literature of ancient Thurigy into the city, which sparkeddiscussion and later brought about the annual humanist gathering, the CaldeaConference, where the study of Arcanum was debated over its use for
```

### [31] hash=`9bf70beadcae44f1`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
mankind development.Who knows the name of his work brought by Gamestos?Miss!Verten, do you know the answer to this question?Verten?Verten.She is absent again.We'll just take another route.Seneto, come here.Is my book all still there?She didn't push it down, right?She didn't.She is nice.Unlike the bad potion instructor who turned my books into a puddle of mud.Please, don't bring me these pebbles and frogs anymore.
```

### [32] hash=`08c159d957065622`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
These are...We are born-to-die martyrs.Why?Just because the student handbook says so.That's right.I don't like the handbook.It smells like there's stinky socks in the attic.Sanato, aren't you really curious about what is outside the school?You were also in that parade outside the school before.The pebbles, the frogs, the attic of stinky socks.They're just a teeny-tiny part of the whole world.I once met a girl who came to our school.
```

### [33] hash=`bfa563a0a4a939eb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Please, these are very dangerous things.The student handbook is protecting us.It is protecting us from harm and regrets.As the instructors have told us,to live is to lose things around usuntil the day we lose life itself to death.That's why we should only focus on the supreme missions.Until the day we lose life itself to death.Now it's coming, my lord.What?Don't forget, my heart is...Failed.Her traumatic segment has been reactivated.
```

### [34] hash=`2ae198ba7e6acb5d`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Increase the power, stabilize her Psycube.Try the next dream.The artificial synembilism therapy may not work on her, Mesmer.You're here, mademoiselle.All patients who have the symptoms of stress disorder need to receive treatments in the rehabilitation center.Her trauma level was assessed as a type 2.I needed to take responsibility for her health.Back in the year when she became the timekeeper, she didn't receive any treatment.
```

### [35] hash=`2c6cb937f3970ba5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
I know her well.She has enough power in her to make it through.I'm just following orders, madam.It is the committee's direct order to treat Fertin.If you have anything to say, convince the vice president first.She hasn't had any food for days, gave her a glucose injection.I have a meeting later.So if you would excuse me, I did expect you would have learned your lesson in such a long timeTimekeeper
```

### [36] hash=`d3800b0b28b4e65b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
No, I'm more used to calling you fair 10.I have changedHave you are you still suffering from those?Pointless things.This is an atom the chief assistant of the foundation's timekeeperMy employee number is s f 3 8 0 0 0 0 0 0 0 8 0 1 1 0 2 yCould you please register a visit to Ward 1525 for me?Please present your ID.Hold that crystal with your right hand until the color changes.Oh, okay.What is the shape of the sun?
```

### [37] hash=`c85b33bf28322cc5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
A sphere or a cube?A sphere.Which is edible?Rubber, cabbage, or carbuncle?Cabbage.Does the rain come down from the sky or the other way around?Can be both.You're good to go.Take these materials with you.The visitor guide is between the second and third page.Go in from the left, turn right twice, and take the lift.Keep walking and you will see the ward.Anything else I should know?Just leave the number out next time, will you?
```

### [38] hash=`e68ffd9891758390`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
The nurses seem busy here.The registration is also more rigorous than it was before.I wonder if this is because of the storm.Turn right again?But there's only one way, and it goes left.Did I miss any crossings?Maybe I'm seeing things.So, here is a junction to the right.Plus, I can't get away from them.And I will not bring danger to the timekeeper.I will catch this person.The Rehabilitation Center is established to provide
```

### [39] hash=`306b94f1bc438869`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
affected medical services and trainings to the patientsfor their bodily functions to be restored.This center is managed by Laplace Scientific Computing Center.If you have any special requirements or have encountered any suspicious persons, please move to the ground floor lobby for help.If you are distant from the lobby, please press the yellow button next to the far host cabinets.The security on your floor will come to assist shortly.
```

### [40] hash=`1b762c447776ebab`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
They're here.I don't see any cabinets.That's fine.If no help or assistance has come to you in time, you may take action to defend yourself.A free wake-up procedure will be administered on any unresponsive persons, if any.Just what I need.The sanitary trolley is parked at the next turn.I've left the biggest garbage bag on it.Speak up!Why are you following me?You're not getting away, wherever you are.
```

### [41] hash=`b5017822ed616f09`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Peace be with us.Matilda?It's you?I'm sorry.I thought it was someone suspicious, so...Are you alright?Monitor student in, obliged to stop you from making a scene here and disturbing the patients, my warning!Put this on a tier, pending graduate.I battle with some acute mania patient getting out, waiting for my fancy transcranial magnetic stimulation therapy.On a tier?How would I have anything to do with Matilda Boanish?
```

### [42] hash=`09f7f4c506124a97`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
The top three students in school, the monitor assistant, and the speaker of graceful French.None shall forget my name after making the acquaintance of me.I didn't, but I guess no one will remember the third place.In my way!Matilda, please take...She just ran away like that.There's even garbage dust on her hair.I didn't know she was the one following me.I shouldn't have acted in haste.Alright, get down to business.
```

### [43] hash=`b5701dd23f5e1e7a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Senedo, you are here visiting the Timekeeper, right?Follow me.Okay.A little bird told me you went to visit Furtin.Is that right?Yes.How is she doing?Just like the other patients.Unconscious.Artificial Somnambulism therapy shall be good for her.It's been four years since she became the Timekeeper.She surely needs a break.Yes, and I have no other opinion about this, Madam Vice President.I'm here for another issue.
```

### [44] hash=`904991f743dddf2e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
The proposal of additional manpower submitted by the House of Integratus.I have given it consideration.It's not worth a committee hearing.Are you here to talk about dead plans?Yes, because I have the exact opposite view.Vertan's suitcase will not be affected by the storm,just like the buildings in our headquarters,which means she will soon be able to form a team,indirectly controlled by the Foundation.
```

### [45] hash=`197a491891065d0b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
I suggest putting her in commandof an independent autonomous unit.With enough support,They should soon become another reliable force of the Foundation, and it also facilitatesa relationship with Vertan.The people Vertan brought back with her, who are they?Arcaneists who have stable personalities, good command over their arcane skills, andsome social experiences.If you ask me, they are some pitiful exiles who lost everything in the storm.
```

### [46] hash=`49a5e951a5c09cf0`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
So desperate, horrified, and overwhelmed, longing for something stable to hold onto.Vertan is not here.Only the Foundation can give them what they want.But what can they give us in return?The innate arbitrariness of Arcanists?Or questioning our beliefs of mankind's supremacy because they have nobler blood?Of course the Foundation needs new blood.Especially those who are highly obedient and know the importance of order.
```

### [47] hash=`72fea191f8c83239`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
That's why these poor refugees need no independent unit or autonomy.They need the guidance of disciplines.A teaching more comprehensive than what's been given to those naive children in school.I see.What you want is a group of dumb puppets.I'm always the optimist in the room.And you know that, Miss Z.This won't be so much of a dead plan if one day they can prove they are not some dumb puppets.To think that she's the one responsible for this mess now.
```

### [48] hash=`6b35eaeb3e02e9b5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
But I don't know if I should be mad or sad about it.This mess must be terrible and there's so much I could help for it.But it's been a long time since I've seen it.If I want to push the saints, well...What did I just say?The person who's going to beat the best in the class!care worker?I saw it.I saw it all.Bodies breaking down into pieces and cubes.It'sa pretty octahedron.Can't let your octahedron fall to the ground too.
```

### [49] hash=`2374da719942b887`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Becareful with your ears.I care about myself.It's my orb.Touch it.What's its shape?This?You have wounded a caretaker and took the keys.I'm obliged to take you down.The storm took our friend from us.In fact, we all knew this would have happened.But it took place too soon, caught us all off guard.And there were only clothes left.That's right.I've looked up the directory of Arcanus in the U.S.in 1929.
```

### [50] hash=`ee9b912a72a5bbb7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
None of their family is on it.She was Greco's biological daughter.Schneider was a pseudonym.I haven't worked out the reason behind this, but she was indeedfrom the vice president of the committee, Constantine.The order from on high was given on the premiseof rational thinking and consideration over pros and cons.You are not questioning the reasoning of mankind, are you?I am not.Sharing the same set of values is the reason
```

### [51] hash=`079603109684c140`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
I'd like to share these interesting details with you.Of course, if you were a pure-blood human,I would appreciate you more.Veriton's magnetic field always maintains a nuanced balance.She barely dreams proactively.So I have to deploy different dreams to search for the very first dream which reflects the source of her trauma.How much longer is this therapy going to take, in your view?However long it takes.
```

### [52] hash=`d4ee4e48b3547111`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
As long as I receive a new order.None of these have been applied for the Timekeeper's well-being.Yes.What's wrong with you, Sinetto?I...I don't know.Sorry, I overreacted.I don't feel quite myself today.I can't tell what's wrong.Perhaps I ate something bad for breakfast.Go back and rest if you're feeling unwell.Don't be too hard on yourself.Thank you.Please, take good care of the Timekeeper.I'll be on my way.
```

### [53] hash=`9aab61e398898dcb`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
In 388 BC, standing in the garden paths of Athens, there was an academia of philosophers.Thirty-six human ideologists presented that day were thinking about the ever-present old question.Just as you are.What passes knowledge?What maintains the world's balance?Students, don't forget the exhortation from the philosophers.Rationality.Responsibility.This will be your lifelong pursuit.Let peace be with men.
```

### [54] hash=`2f8081cd0dedb365`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Last year, 45% of our graduates were chosen to work in the St.Pavlov Foundation headquarters.A particular excellent student has even been accepted by the House of Integratus.The rest of the children too have become frontline investigators,staffs of foundation offices in other countries,or professional soldiers dedicating themselves to the magnificent cause of mankind.For thousands of years, we have taken in countless young arcanists from workhouses and boundling
```

### [55] hash=`34ad43954ea74dba`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
hospitals, and have raised them to be outstanding students and morals in every industry.You will also be the backbone in preserving world order.And, James Burton, then why aren't you standing in the line?I'm sorry.I just wanted to see you clearly, since your speech was so wonderful.Burton, you are the youngest child we've ever taken in.You were just a month old when you came to the school,and by now you've spent almost 12 years in him.
```

### [56] hash=`55faac391de03a16`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
I'd like to hear your thoughts since you are the most unique child in the school.Whatever the question or opinion is, I will respond with an answer.Any question?Of course as you would the storm sirYeah, I asked how much further do we have to go what?So we get to the guard houseWe're almost there.Don't worryOkay, as your punishment.No dinner will be served tonight.You will stay here until tomorrowDon't fix you up at noon
```

### [57] hash=`124b38dbed35446a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Okay, I won't ask you how you knew that wordWell, you have to promise that you won't mention it again.I promise.All right, here we are.This is not some friendly place.The arcane skills I taught you before may help.I hope you have paid close attention in that class.Get inside.Think carefully, or next time it won't be just confinement.This is the Shamir one.So cool.It's said that the Shamirs are marvelous creatures.
```

### [58] hash=`ba9da918cb383f94`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Even King Solomon searched for them for years.They're incredible engravers, more skilled than the greatest craftsmen among human.They can engrave on leaves, metal, and gemstones, build a sacred temple, or destroy a giant vessel.But now, they've become tools for punishing naughty kids.There were at least a few hundred Shamirs here, and they're all moving towards me.The instructor did teach two incantations to repel insects, but Shamirs are not any ordinary one.
```

### [59] hash=`0f2d83b2afcd5451`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
They were in fact a kind of advanced critter.The elementary arcane skills won't work on them, let alone there are no signs of my arcaneabilities up till now.I'm not an arcaneist at all.Please don't bite me two times a day.You're right.No.Stop.I have to focus now.There must be a way I can think of.Water keeps dripping down from the side of the ceiling near the window, but ithasn't rained for days.Here is a thin layer of mud on the ground.
```

### [60] hash=`01d02646bf0b97ed`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Judging from its volume, it's not likely to be brought in by other children whowere once in confinement.The dripping water has made the ground uneven.For these tiny worms, these descending areas are like impassable gulfs.Could the ground be lapped like this so as to slow down the worms, and give us the timeto cast incantations?But why would they gather around my feet?This is...These out there routes have been planned already.
```

### [61] hash=`c583243079c39ccc`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Wool?Poe?So that's the case.The legend says that the way to store Shamir worms is to wrap them in wool, and storeI thought we were on the same boat.If I let you out, will you come back?Of course not!Not even for a minute!But if you don't come back, the instructor will give us a harsher punishment.I'm just sneaking out for food.I'll be back.What would you like to have?Fish and chips.Some onion for the grip on the side if they have any.
```

### [62] hash=`d18073ee618fc29e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
No problem.I'll bring some mashed peas too.So you managed to control the Shamirs and got out?Yes.How about you?Any odd things in your room?Nothing peculiar.Just some stinky dots.Didn't even take me long to take care of them.The staff canteen does serve some good fish and chips.What you have in the second canteen is not even close to it.Keep missing the dressings, and sometimes it's not even cod they fried.
```

### [63] hash=`7ff329b253aa5613`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
So, why are you here?I said...What word?I said at the pre-parade assembly.Oh, you mean the S-1?The school assembly?Oh, good for you.That is gonna be so fist.I don't understand.It was him who said that I can ask any questions that I want.Where did you learn that word?I heard it from the janitor of our dormitory.That was the last thing he said.I saw him being escorted outside the school gate and onto a truck.
```

### [64] hash=`4feef372072321f6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
He screamed all along.The storm is coming!Um, I said it again.Shoot.Never mind.Keep going.I asked many people, but none was bothered to answer.Uncle Morris said the janitor left the school at an inappropriate timeand saw some inappropriate things so he needed a treat.So I was right.The school is blocking the news feed.Look at this.I snuck this up from the staff office.The world-changing storm.Truth covered by the foundation.
```

### [65] hash=`375bcb99555f21b8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Yes, it wrote about a phenomenon called the storm, which would bring everybody endangered.Yet, the Foundation has stayed in silence about it.We are not allowed to say that word, and this is the evidence.It doesn't tell us exactly what the word is either.There's a line in bold at the end of the article.Welcome to Manus Vindicti.What's Manus Vindicti?Dunno.Never heard of it.Something has been printed on the back too.
```

### [66] hash=`ea133f309d6a9bd7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Let me see, nor happiness, nor harmony, nor fame, nor pride, nor strength, nor skill inarms or arts, shepherd those herds, whom blindness makes tame.Their eyes see not one light of bright stars, man's past ways are shaded by their shame,peons are but admiration's mirror half.Tides run in blind by their ever-be routine, staining that heaven with obscene calamity.When Follywrecks wit, where do stand we?
```

### [67] hash=`02447a3800361829`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Before a cruel whip, man who man would be, must rule the empire of himself.In it must be supreme, establishing his throne on vanquished will, quelling the challengesof hopes and fears, being himself alone.What's going on?Great!The chips have brought in more rats!Thurton, Hampton!Madam Vice President.Come in.Here is the Mont State Department report.Any news I shouldn't miss?The mainstream media in Europe are on our side,
```

### [68] hash=`f44aa594f5ad7a82`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
and have no extra coverage on the issue.In fact, as long as there is no tangible evidence,They won't act upon this rashly.The storm hasn't come to this area yet.For most of the people, Wumanus Vendicti has said in their pamphlets are totally unfoundedand ludicrous.They have been making quite a scene here and there.As I heard, residents nearby have all received their pamphlets.Even the SPDM has reported some cases.
```

### [69] hash=`a17451a169d08c46`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Affected by the time reversion, our manpower and resources have become much less thanIt will take us a long time to complete a city-wide air defense system.These pamphlets air dropped.Yes, most of them were.Give me a visual of the aerial carriers of Manus Vindicte.These are Illidias.Their sizes are about 4 to 6 feet, covered mostly in black.They have a similar appearance to manta rays and have good maneuverability and explosive power.
```

### [70] hash=`db7ac87a04d457c2`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Olydeo 04.This type of Olydeo has limited operation range and cannot take long haul.They are too dependent on the water.Indeed.According to our report, they usually leave after 3 hour hovering every day.Ms.Z, where do you see fit for this bishop?I think it should go to B5.I thought the same.Adequate for low-altitude aerial reconnaissance surveys.I will forward this to the secretary of the army.Make a copy to the Pax House as well.
```

### [71] hash=`2a4c469999dd256a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Copy that.What about the school's air defense?There have been rumors in school.I'm worried the students might be affected.Sanzeno's Air Force trainees to the school.Affirmative.Our ladyas are crafty creatures.I will pick those who are equipped with field experience.We are leading ourselves into a death trap.We need someone to forecast the storm.Finally got to let my baby SU-01VE out for a ride.It feels right!
```

### [72] hash=`f34d2286cc860eb3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
This is where they train those little lab rats?Oh, five canteens!Way better than that stupid Xeno!Oi!Lillia!We don't have the signal yet!You must not take off!Get down here now!Nobody cares, dude!There will always be a signal!Either you move your ass, or swallow my exhaust!This is outrageous!For once, I forgot my rabbit's foot and I got a science team over here!Shut up and take your brew.See those dark bats there?
```

### [73] hash=`6d2635300387250f`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Let's see who come back with more trophies.Loser, loser!Vodka coaster!For whom?From whom?No idea.Quit asking.Just we didn't pass it down.Waste my time taking notes.I will...Did you write this note?Yes.Are you coming?No, you were going to shine my shoes for the rest of the week.Don't you change thesubject.Not only did you pass notes in class, but also did so to spread suchsuch horrifying information.
```

### [74] hash=`545eb5d628c6639e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
You don't want this to be given to the instructors,do you?So that's what you want.I don't care Joseph.You can deal with it as you want.Come on, shine my shoes for a week or cry in the guardhouse again.I'mI wrote it.That's not what my writing looks like when I use my right handNow you were the one holding the note.I could say it's you who wrote it, right?I'll call the instructor over for youFreak you're just a bastard that can't even cast an incantation
```

### [75] hash=`8a276d0a0be9c7b5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Why you two I want her legs broken todayI need to hide quickly.Do you think they're gonna come?What if in the end?No one shows up.Maybe nobody cares what's outside the school.Maybe everyone's happy with what they've learned in the school.At least there'll be two, I guess.Isabella, when she just got into the school, she was crying all the time and wanted to go home.Maybe she will come.They are here!
```

### [76] hash=`03e378acbb461b30`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
My god!That's...How come there are so many of them?Mesmer Junior, Penny, Matilda, you all here?You gathered us all here.Are you going to hold out against the principal?Absolutely not.I've thought of that.That was a harsh question you asked Mesmer, but thank goodness.I'll be the first one out of here were a rebellion.This peace lever is not up against anyone.What is it you want?I came here in secrecy.
```

### [77] hash=`c3d932c65c440394`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
So many of you, so many of you in school are just like the ring and me, want to know more about the things outside.Those rumors, have you heard?Yet we are prohibited not only to say that word, but also to speak about anything related to the outside world.Our life is all about training, peace and mankind, nothing else.We have different hair colors, speak with different accents and cast different arcane skills.
```

### [78] hash=`7797891e29293b16`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
But the student handbook asks us to forget about all that.It aims at eliminating our differencesand ensuring conformity in the school.We have found some pamphlets with poemsfrom the outside world printed on them.This is something we've never been taught in class.That poem inspired me with so many things.We are the chosen ones.We are meant to be the backboneof the primary defense for mankind.But all of you here today
```

### [79] hash=`06b06ed1367adf8a`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
must still be curious about who you really are and what is in the world outside.We cannot leave here, but we can know the truth through another way.Fellow students, before entering the school, where did you live?What kind of life did you lead?Did people there cast incantations too?Did they like scone just as we do?By piecing together our memories from all over the world,we can rebuild the very world outside.
```

### [80] hash=`5eeabc8c5e434b45`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
How you know the world this is the safest method we can think ofGiven that none of us are leaving schoolI tuck some of these pamphlets in my pocket and stained glass balls an instructor left to me when he resignedI'd say these are a part of that outside worldBefore MatildaI'm the most senior transfer student in this schoolIn fact, I was too senior to be taken in if not for that special approvalThat is to say, I remember the outside world a lot more than you do.
```

### [81] hash=`b870fb880c1a9cb3`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
Hi, I'm Isabella.I was taken here at four, so I don't remember much of the outside world.I can recall Mother Superior used to like wearing floral dresses in pale blue,and we don't have much rain from where I grew up.The cloudless sky stretched out over a head and fell into the horizon.Ecologists for generations in the Arcanum world.Animal magnetism was invented by my grandfather's grandfather's grandfather's grandfather.
```

### [82] hash=`27c521f39bb78f9e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
But I'm not interested in Arcanus.They're all mad people, and we had to treat them after all.They looked scary.Oh, and there was a big football field near my house.Bare spots were on the turf everywhere, and there was also rust on the gold.What's football can't follow beautiful poem sing it the melody of our school songSee each word is well matched to the rhythmnor happiness norMajesty nor faith nor peace nor strength nor skills
```

### [83] hash=`f6d41ffd3a45fc2e`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p6`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜1~10）

```text
My things you go well togetherMakesThe purple is joining the notes so well.Is this a sign I've been by destiny?Are we told to, told to?The singing of the great ceremony!Possible!We will definitely get caught!Doing so, the goddess wears!Be upset, or blame us.Let's give it a try, to then it was before.
```

### [84] hash=`bcde612d73b6f0fd`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
You weren't in the dormitory last night.Were you on duty yesterday?Yes, as I am today.I know you are planning something behind the instructor's backs.Please do not act against any regulations stipulated in the student handbook.Otherwise, I am obliged to report this to the instructor as the monitor student on duty.Okay?Are we ready?Yes.Let's do this!Good luck to us all!Today, I am honored to be accompanied by the young representative of the St.
```

### [85] hash=`01153edd2cdffcb5`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Pavlov FoundationCommittee, Ms.Z, principal of our close partner, Mr.Claude Smith of Zeno Academy, and theoutstanding alumni who graduated last year, to our annual parade ceremony.The parade ceremony, where we show our best image and morale once a year.Each year, the best students would be selected to take a three month intense trainingand become the honor guard of our school and present the fabulous demeanor of our students.
```

### [86] hash=`c10abc4b946de475`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
And now, everyone, the first part of the ceremony, School Song, lives on!Get out them!It slipped in my hand!We've investigated the event in the school.Incited by the maintenance pamphlets, a girl named Merton assembled about 20 students to sing a revised version of the School Song at the parade ceremony.Principal Richard and the safety supervisor failed to dissuade them and thus deployed guards, thumb-beater potion and non-lethal weapons.
```

### [87] hash=`b31b115210281dae`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
During the conflict, Virgin Slap was accidentally shot by a non-lethal weapon.She fell into a coma.With the treatment provided by the Spoo Clinic, she was discharged after making a full recovery.She should be back to Spoo today.What a bad move.Who's move?What was their appeal?They wanted to know the outside world, especially the storm.This Vertan is the one that we know of?The kid who stretched her arms outside the front gate to catch the frog during the storm.
```

### [88] hash=`0d9349938d94279b`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
That Vertan?Yes.If I recall correctly, the report described her arm didn't show any signs of changeafter getting soaked in the storm.They sowed a seed of doubt in those children.What happened this time will have a long-lasting effect, and Manus will not sit tight by it.And I, I need Vertin to grow.When an Illidial gets nervous, it may attack people.Whenever this happens, we need to lower our body as much as we can and act friendly
```

### [89] hash=`553eafb0cb84c7c6`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
to avoid irritating it.I think you may find this helpful.You'll be out next week.They're welcome to borrow my notesThank you for your kindness.I hope they'll have the chance to use themI'm here to return this bookSure, I'm glad to see you reflecting on your actionsThe principal and the instructors would never do harm to their students.Think you understand nowThank You instructor.I'll be on my way.
```

### [90] hash=`639949775df37fd7`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
Hope you have a wonderful dayIsabella, put these back on the shelf.Yes, miss.I have very important things to say to you.I've now obtained the map of the school, including the blocks around it.But now we can't meet in public places, as there are students watching us.George the Oak was auto-zoned to the alert area.We need a new location for gathering.Better meet tonight.It's right beneath this building.
```

### [91] hash=`2ca4d2231c153fb8`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
It was an air raid tunnel under the library.Someone would come down there.We can walk there from the basement level 2 of the girl's dorm.There will be a gate, but it opens at an easy push, but it will be a long way to walk,and we will have to walk through the basement level of the clinic.That's nice, girl's dorm.Right?Don't worry, easy enough for me.I also have some important info to share with you.
```

### [92] hash=`3e5901fec0244a7c`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
See you at 7.I'll bring along the others, so don't you worry.Welcome to Mesmer Junior's dorm and the teaching building to look her up.She's not in any of the places, so I just came on my own.Probably she's studying in secret.Good for her.But she will not get the better of me.What about the others?I can see some people are missing.They no longer speak to me after coming out of the guardhouse.These are all the companions we have now.
```

### [93] hash=`c75bed5798cca492`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
It's alright, Ring.What we're going to do this time is much more dangerous than last time.and we may lose everything we have.We're here because we made up our minds.If not for the ceremony, I wouldn't have thought...That the principal, as well as the instructors,are afraid of us knowing even the slightest thing about the outside world.They're even more afraid that we would become puppets that break away from the threads.
```

### [94] hash=`a5a2e78d14a828ad`

- lang：`en`｜version：`1.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p7`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【1.0-主线】第三章.故事一无所有｜11~16）

```text
I don't want to live like this anymore.Burton, that's why you gathered us here, right?When I vomited in the guardhouse because of extreme hunger, I prayed, but one day...This is the full map of our school, including the aerial view of the schools and the blocks nearby.I found the technical drawings of the air defense renovation in the library, and added the missing underground tunnel part to the map.
```

