# 剧情图谱抽取 · batch 088

- 角色：`wu_ming_zhe`
- 批次：**88** / 共 1 批（每批 95 块）｜本批块数：**95**
- 筛选：标题含「2.0」｜offset 190
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_088.jsonl`

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

### [0] hash=`0b390a285be01429`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Give me the application form.I'll arrange it for you.Oh, wait.Someone told me to give this to you.Nowhere like damn it.My baby's gonna be stuck here foreverFair distance from the safety houseMiss but paid me andHere's a tip too.I hope it can make up for your lossextentDinguished and generous passengers such as me must be a rarityI will walk the rest of the way.If you stay here and wait for me, I will show you my generosity again when I return!
```

### [1] hash=`e0c1a7aa6cd7b729`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
Sure, miss!The location of the security house is classified.I must be very careful.Okay, now I won't leave any footprints behind me.If only I had an assistant with me, then I wouldn't have to carry this suitcase alone.It would be even better if it was honest.Mom would be happy to meet her.I don't feel mom's incantation at all.I guess it makes sense.The staff at the place swore that this place was so hidden
```

### [2] hash=`c51ea7a581a7adf5`

- lang：`en`｜version：`2.0`｜arc：`—`
- doc：`BV1eo4y1u7aW_p66`
- title：《重返未来：1999》公测 全剧情【4K英配/电影画幅】（【2.0-活动】飞驰！明日之城 | 15~22）

```text
that a glaucus could not find it.I hope she's doing well.Those stupid Manus' followers could never find her.She's one of the best, I would guess, crystal healers.She must have foreseen all the possible circumstances to prepare for it.But she will certainly be surprised to see that this visitor is her own daughter.The SPDM canteen knows nothing about French cuisine.I can't wait to eat a new mom's dish.

The most important thing is that I have to ask mom to choose a new orbicular for me.Even the best crystal craftsman couldn't do anything to repair the cracks in mine.I want to see who's the-
```

### [3] hash=`790af044aa6e27b0`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Hmm...La pièce derrière le restaurant ?La Mercuria est partie avec cet homme !Elle nous a...trahis !Je dois prévenir Jay !La cérémonie approche, elle va dévoiler notre plan !Ont-ils vraiment laissé ici toute seule ?Oh, oh !J'ai apporté un cadeau, Jay.Yes, là-bas !Il y a un trou dans la porte !Ils sont tous là !En tant que pardon pour la pauvreté de mes enfants, j'aimerais que tu prennes en charge de cette négociation.
```

### [4] hash=`1a5fd55750a0efa4`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Merci grand-père.Mais nous savons que nous n'avons pas de fête ici.Et pourquoi ne t'as pas ton garçon G.O.qui vient là-bas et s'excuser lui-même ?Je vais te donner un petit conseil, Jay.Ne sortez pas de leurs propriétés, n'ayez pas l'intention de vos propres hommes.Voici comment vous jouez.Je vous donne une condition.Si vous acceptez, je vous enlèverai un bulletin.Quand toutes les chambres sont vides, vous gagnez.
```

### [5] hash=`9d248796dee5dc36`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Si vous prenez vos chances et vous rejettez la condition,je vous enlèverai.Ne vous inquiétez pas, je vous enlèverai un bulletin dans votre poingue.Je respecte totalement votre liberté de choix.Vous êtes encore bienvenu à essayer votre chance avec tous les 4 bulletins, si vous le souhaitez.Je...Je peux voir les bulletins dans la chambre quand il roule un cylindre.D'accord, je vais compter sur le boss.
```

### [6] hash=`2773a09b7de5400f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Il faut lui aider à survivre au prix le plus bas.Voici ton verre, boss.Merci, Weizen.Je pouvais utiliser un verre.J'ai de beaux yeux !Je pouvais faire beaucoup de choses.Comparer des coins, des voitures, trouver des droits d'eau.Je suis capable de spotter des cheats et des dealers froid.D'accord.Faisons ça, grand-père.On dirait que tu as un bosse pour un bosse, les gars.8, 10, 10 fois.La prochaine chambre est bloquée.
```

### [7] hash=`99447bc57231d756`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Merci, Weizen.Condition 2.Arrêtez vos gens de là.Maintenant.Nous avons besoin de silence.Vos amis sont déchirant notre conversation.Vous l'avez entendu, les gars.Arrêtez de là.Weizen, prenez soin de votre bosse.Jay, qu'est-ce que tu fais ?J'aimerais plutôt prendre ce putain de putain avec moi.Quand es-tu devenu un putain d'héreux ?Non, les gars.Vous n'êtes pas à m'aider à rester ici.Juste sortez.C'est un plaisir de faire du boulot avec toi, Jay.
```

### [8] hash=`1a9d00d7282fa9c8`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Tu es un homme pratique.Que la souffreur vous bénisse.Il n'y a pas de déni que tu aies un coeur merveilleux.18 fois.Les deux prochaines shots sont en sécurité.J'ai eu à vendre le boss.Fais-le jusqu'à la fin, putain.Ne t'inquiètes pas.Je te conseille si Jay ne le fait pas.Oui, sir.Maintenant...Condition 3.Vous avez déjà perdu le jeu, Legers.Oh, donc vous voulez prendre vos chances, hein ?J'ai pensé que 50-50 était assez proche.
```

### [9] hash=`1eadb426b1a1a553`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Mais tu sais, petit ami, je n'ai jamais dit que je tirerais seulement une fois.Essaye, vieux homme.Fais-le.Tu as de la chance, petit ami.Maintenant, essayons ça de nouveau.Mets de l'eau, toi le malade !Jay !Veux-tu voir ce qui se passe quand tu m'amuses avec moi ?Le jeu est fini, grand-père.Oh, mais on préfère continuer.Les enfants, arrêtez sa face.Si c'est comme ça qu'il doit être,Faisons ça, vieux homme.
```

### [10] hash=`085ae6ba058f4745`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Mais cette fois,Nous avons la main en haut.Maintenant, donne-moi ce que tu as pris.Et je vais te laisser et tes petits lackeys partir.Put down the knife, kiddo.That was just a warning.To let you know the game isn't over yet.Now, I got one last condition.Let us leave in peace.So, what do you say?Help me out!Pollock needs this place to live!I can turn all of Height Street to ashes, if you want me to.
```

### [11] hash=`5616f771d71f21b9`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
Good boy.By the way, get yourself a better knife.J'ai des couteaux de beurre plus fort que ça, mais warning pour essayer de prendre mes hommes.Qu'est ce qu'il s'est passé à toi, Jay?Tu étais inquiétant quand Holik et moi avons rencontré toi.Nous étions comme un paquet de morts, rommageant dans les cannes de poils et dormant dans la rue.Tout ce qu'on avait était des vêtements sur nos couches, mais nous l'avons encore fait jusqu'ici.
```

### [12] hash=`8bded44a80bb42ec`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p10`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（10再见，鼠辈）

```text
J'aurais préféré que j'arrête mes poings et que je fasse ma dernière droppe de sang que de prier pour Mercie.Donc, s'arrêtez !Désolé, Mister J.Tout ce que j'ai voulu c'était un endroit sûr pour dormir.Pas tout ça.Je ne veux pas être tué.Boss, je vais les retenir.On va tout retenir.Hey !
```

### [13] hash=`0a6fa1802e983c5f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
Be honest, I thought I'd never use this thing again.I remember that dayDad was in the living room with his friends boasting about this awesome.Treasury found on his tripHadn't seen a smile like that since mom died his friends all sucked up to him thought he dug up some good stuffI was just a whiny little kid back thenNo one liked meAfter his friends left dad put me in a suit and tie like I was some kind of stage performer and took me to the
```

### [14] hash=`80f1368d6df0ed81`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
velvet restaurantWhen we got there, he brought this little girl to me and said,Hey son, I got you a little sister.That was the first time I met Paulina and her mom.I realized that he wasn't lying about the treasure.The days after were sweet, like eating dessert on cloud nine every day.But it didn't last long.My dad was nothing but a broke insurance agent after he ran away from the Whelanfamily.He had big dreams, but he was too weak to realize them.
```

### [15] hash=`625caa0a28ebccb7`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
The Wayland family, compiled by the SPDF, they've been arcane blacksmiths famous for their sword-makingfor generations.But the book says the family perished in the war.No matter what generation, Frenchy, weak people cower in dark holes, learn to hidetheir power, and only use it when they really need it.Being reckless can kill you.I've learned that better than anyone since my old man died, and you know what?
```

### [16] hash=`47472f29f206147f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
His friends were right.He followed Solomon's manuscript, a document left behind by his family, and dug up somethingfrom under the ruins, a worthless piece of black iron.Document holds top-secret information only available to certain members of the Foundation.How did he get it, and what have you done with the iron?most of it became this thing strapped to my back and the rest well you'relooking at it girl I didn't get why dad said it was good
```

### [17] hash=`b05ad8b5a1dd64a3`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
stuff until now you know those witches who can tell at a glance whether kidwill be a warrior or a priest when I looked at the scrap of metal I had thesame feeling it was destined to be a killer knife and now it's gonna makearrive either.Miss J, there's no reason to risk your life.The reinforcements will arrive in no time.Then we can finish this with minimum casualties.Take this lesson from the experienced investigator,
```

### [18] hash=`707b28f71d4799eb`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
Matilda Bwanish.Preparation is the key to success.I guess you're right.When I was a scrawny little street kid,I looked to a savior,like a cop or a boss.Anything to avoid a beating.We all got the smarts to stay out of trouble.We just gotta look both ways before we make our move.This wallet is all I have, please.There's nothing in it.Just a photo of my wife and daughter.Oh, bogey!Take it back if you got the guts!
```

### [19] hash=`4b0d8d3cdd3be96f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
Ha ha ha!Brent!Catch!Over here, old man!Hey!Get out of the way, you stupid bastard!Help me, Brian!I'm sorry.I'm sorry, friend.We show tolerance and modesty.Tell me, did your brain slip out of your skull?Don't you know how expensive this cleaner is?Spray it on this piece of crap one more time and you ain't getting a cent next month.But sir, the customer paid us to use this cleaner.And I pay you to work for me, you idiot.
```

### [20] hash=`2dbaf6b7969f0292`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
Either listen to me or go back to daydreaming in that burnt down garage of yours.We know our limits.Do what we can, and give up when we have to.Ten.Seven.Hey, hey.Just stay down, you idiot.You'll get paid after the game, I promise.Ah, come on.You think you're a tough man?Just stay down and we'll make a fortune.But if you've ever tried the Tempura Sword, you know that hesitation ruins the work.You gotta be brave, decisive.
```

### [21] hash=`707cee6cb928eb7f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
That's how you make a great sword.That's how you live a great life.You don't gotta be too careful about what you say and do.Don't gotta be prepared for everything.Because a brave and decisive fist, well that's unstoppable.I won't just stand back and wait like a coward.Never.You understand?You're right.This would be a serious violation.You'll be going against the direct orders of the Foundation.Therefore, as your supervisor, I will keep an eye on you wherever you go, just in case you do something stupid.
```

### [22] hash=`250c488f706baf37`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p11`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（11炉火与铁站）

```text
Fine by me, Commander.Hey, where are the badges?They were here just now.Mr.Pioneer!Mr.Pioneer!
```

### [23] hash=`04e5fd64ef6a041e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
Sorry I've never seen a case like this before.I can't quite believe what I'm looking at to be honest.I'm afraid there's nothing human medicine can do.This is well beyond my means.What do you think you're doing Pops?No one told me you took the new kids to Hate Street.Those crazy dogs could have hurt you, you know that?Hurt me?I appreciate your concern kiddo.I heard that you found your dagger.shoot yourself in the head then return home a loser you promised we'd settle
```

### [24] hash=`16fb55604f74fd6d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
down here make it our second home we were cast out by the humans but wetrusted you we all understood that hating humans wouldn't put food on atable that's why we respected you why we still respect you Jerry Littlefingerdied in the tub his mama still thinks he's working for us on the seaShort Ken, who spent his whole life waiting tables, was shot to pieces just a couple of days after his daughter was born.
```

### [25] hash=`fb39bd10ec24b77a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
And my wife, Savina, was burned to death by some piece of shit Austinist!Even now the cops won't tell me who did it!But even through all the pain and all the hardship, we had principles.Principles that have earned us respect and made us more money than our fathers did in their entire lives.But now you've been corrupted by those lunatics from the Order of Enlightenment.Now the clinics refuse to treat us.
```

### [26] hash=`41dcd282b24dd698`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
They know we don't go by our principles anymore.That every cent we have is taken from those poor people who are as hungry as we used to be.What do we stand for now?Beating down on the poor and murdering children?No one trusts us anymore!You're pushing everyone further and further away!When are you gonna stop, huh?How many more have to suffer?Geo, my boy.You haven't seen the bigger picture.And even now, with that girl messing with your mind.
```

### [27] hash=`94f529b28b3d9e02`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
You have no intention of killing me.You're loyal.I'll give you that, kid.I've been wondering who that witch is.The girl who's making my boy feel mercy and guilt.You're not thinking straight anymore.Can't even hold a gun.It's shameful.Geo's hesitating because he is thinking straight, Legers.Let's don't bring peace.Geo's risking his life to make you see the truth.I believe you understand that better than anyone, but if you insist on taking his
```

### [28] hash=`466e4f1006aaad86`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
I've come here to help you, just like that doctor, I see.I've seen it countless times, how people gather energy to themselves.They put their own lives, their own desires, above all else.They take from others, even exploiting them to satisfy their greed.But Geo's not one of them, nor are you.I can see the aura around you, your soul, your wishes, your energy.None of them are focused on yourself.They're all focused on someone else, someone hidden in this place.
```

### [29] hash=`37e07e589d20e20b`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
He's right here, beneath these floorboards.And you've kept him secret all this time, haven't you?So he's the reason for everything you've done.Death has almost taken him, yet you still cling onto him.You won't let him go.He's suffering.So the rumors were true.The wailing that people heard, it came from this poor man, and you, a human of fleshand blood, unprotected by any arcane skills, were shot in the head, yet continue to walk
```

### [30] hash=`c9b91dcddedda479`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
and talk.Those bullets never penetrated your head, did they?Because you are not Legers.He is.The Order of Enlightenment has allowed him to survive, albeit in a dying body.But there is a price for this.His consciousness.The most I can do is recover his consciousness for a short while.But I can't save him from death.You tried so many treatments, brother.Sometimes, it felt like torture.He bred.You're back!
```

### [31] hash=`16380500d1cfd53e`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
Legers, you're back!Listen, I've found a way to cure your condition.I swear you won't die, I swear!Are you a professor now, Salvatore?This outfit isn't your usual style.Just like you always wanted.Listen, this isn't what I wanted.You're supposed to be working at a law firm.Taking money out of the hands of rich, tight women.Not spilling blood.You gotta get out of this dump.I dirtied my hands so that yours would be clean.
```

### [32] hash=`aaa3ad12e83cd5f6`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
So that you could live the life you wanted.I never wanted you to follow in my footsteps.How are the others doing?Ken and Jerry.They're both honest, hard-working guys.I never should have brought them into this world.They've gone home, Legers.They've...Sleeping for too long, Salvatore.My brain isn't working.And even opened my eyes anymore.It feels like they're glu-Shut.Describe it to me.Tell me where I am.
```

### [33] hash=`a1c50b21bb607972`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
Is that...The sun?Am I an evil thing for us from the kitchen?Did she find out we stole the rum again?Ahem.Le Gers?Yes, the sun is rising.I can feel it's warm.You...You're at home.Isn't that right, Legers?Yeah.We're in Sicily.We're in your old bedroom, remember?Dad just beat the hell out of us.He's smoking in the doorway right now.He said he'd tie us up to stop us from getting ourselves killed on the streets of America.
```

### [34] hash=`75fc725fe89a676b`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p12`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（12空棺柩）

```text
Told us to settle down here, in Sicily.I'm sorry, brother.I couldn't get us tickets to the States.Mama told us to take our stuff out of the suitcases and put it away.We packed a ton.You must be exhausted from unpacking it all.We didn't go to him too fast, but happy to hear that.I was totally clueless.I gotta go to bed.Don't wake me up, Salvatore.Remember to keep breathing.You gotta have one member of the family who uses his brain for a living.

Promise me.I will, brother.I promise.See you tomorrow.He's gone.I won't blame Geo.And I see now why you all made your choice.
```

### [35] hash=`a36ca471a5632931`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
We thought she was a grandma, you know, like one of those little old ladies who uses a walkerWell boy was I wrong.She ran faster than a jackrabbit.So there she went the goods still in her armsShut up Ross and quit trying to get rich.I gotta take a leakKuko you trying to piss up a lake or something?Hurry upShoot, I don't come over here.My zipper's stuck.Give me a sec KukoPioneer, I'm sorry, man.I should have come earlier.
```

### [36] hash=`b3e46e8ebc5345f6`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
Enough faffing around.Go get my arm, and don't make me repeat myself.Hey, hey, hey, don't kick my butt.Damn.What's wrong with you, man?I've never swum in my entire life.You almost killed me.Well, when new boys join us in the future, I'll tell them, you know that famous Jay?He was drowned in a kiddie pool.May the rubber duck be with him.Miss Mesh, the door is right where you're standing.There's nothing here, Miss Bowenish.
```

### [37] hash=`c75f58e96f3e13e9`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
No keyhole, no door frame.Is it buried underground?Perhaps we need to dig it up?No.Since the very beginning, there's never been a specific door that leads to their lair.In other words, any door could take us there.The key is a shortcut.It will take us directly to them.I saw them go into the woods with dozens of believers.They went inside a tent.I was worried about my friend,so I searched for any secret tunnels or cellars that they might have used.
```

### [38] hash=`d47f9c17401dbb0c`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
I thought I could follow the traces left by their arcane skills,but I found nothing.At the same time, I heard that a door had been salvaged from the sunken Lady Elgin.The archaeologists found that the door didn't leave anywhere.It was useless.Back on the ship, it was installed in front of a wall.I've read about these meaningless doors before in my brief study of archaeology.When installed inside tombs, they serve as a decoration and a distraction against
```

### [39] hash=`412132c4a00d284d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
tomb raiders.So, it dawned on me that perhaps it is not the door that matters.It is the key that matters, just a medium through which spaces are connected.It is the key that opens the way.En conclusion, this key can make any door a shortcut to their lair.Even without a door, there is still a path we can take.There is always a direct route that connects two points on the map of GnosisWe can take that path by touching the key and reciting the incantation
```

### [40] hash=`17aa8259826e8b60`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
All we need to do is draw an entrancesoSend the coordinates to the foundation when the reinforcements arrive they can come with usBefore we enter you must know I only master the art of opening the door the art of closing the door howeverWell, only the Manus know how to do that.Are you all aware of the risk?We may get locked in there and never come backAll right.All right enough talk.We've come this far
```

### [41] hash=`7851b7ee66e58477`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p13`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（13小窍门）

```text
Nothing's gonna scare me off.We're here gentlemen boss boss.What are you doing?I can help too.Just ask mr.PioneerYou're smarter than most kids.I know WyzenThat's why I got an even more important job for youAh, it appears we're already in the middle of their lair, Miss Bowanish.Welcome, distinguished guests.
```

### [42] hash=`a0266c43a9f64113`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p14`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（14赞颂诗）

```text
Pity, I thought you gentlemen would recognize me.Have we met before?Wait, I know.Give me a sec.Damn, when did I mess with this girl?She's gonna eat us aliveif she finds out I don't remember her.My apologies, ma'am.We simply didn't expect to see you.We're new here,and the sight of this place took us aback.I see.Allow me to thank you againfor your alms.I can forgive your surprise.You're certainly not the first to react in such a way.
```

### [43] hash=`776e366359fec125`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p14`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（14赞颂诗）

```text
You don't look like merchants or believers, and even the way you were invited is unique.You must be the special guest of the ceremony.That's exactly who we are.We got lost.That's why we look a bit messy.Lovely young people.Now, may I see your invitation from the Order of Enlightenment?Look at you!There are no invitations.It was just a joke, sweetheart.Relax.I have no interest in those outdated rules.
```

### [44] hash=`60701ebe11b4382a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p14`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（14赞颂诗）

```text
With our customers, there is business.Everycoin I earn is as glorious as the last, no matter whose pocket it's from.And, amidstyour confusion, I smell a good deal.On the other hand, it is good manners to notify our host of the arrival of new guests.I'm sure they'll provide a satisfying reward in return.You've given me quite the dilemma.What to do?I wonder...Don't look at me!Where's your money?There's no room in my budget for any extra expenses!
```

### [45] hash=`4a434e09b9f10220`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p14`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（14赞颂诗）

```text
In that case, how about another deal?I recognize that thing on your back the moment I saw it, young sir, and those calloused blacksmith hands.Oh look, you've wrapped it so tightly for fear of it being recognized.That thing can't be hidden.Since you've lugged it all the way here, why not show it to me?Uh, no.It's totally worthless.It makes a payment.This crystal ribbon.Would you look at that?This is Barrow Bow and Nisha's money.
```

### [46] hash=`5aba6a61bd09a387`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p14`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（14赞颂诗）

```text
And you, little lady, must be her daughter.This will be quite a show.What are you talking about?Anyway, I showed you my sincerity.Now it's your turn.Hey!Where do you think you're going?We haven't asked you anything yet.No need, sweetheart.I already know what you're going to ask.A good merchantalways knows what a customer needs.Your friend has been waiting for a longtime.Oh, and here's some free advice.
```

### [47] hash=`1487df30621698f7`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p14`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（14赞颂诗）

```text
Don't get too close to the altar.Hey, what's that?Jay?Madam Gloria, isn't it?I thought she went home afterWhy are you intruding on his joy?Can you not see that he is enjoying the grace granted by the sufferer?Desecrator!Leave that evil believer alone!Paulina?Are you Paulina?
```

### [48] hash=`a7d9205628dedcea`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p15`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（15眼中之物）

```text
According to the Foundation's assessment, this is a priority level A operation,which means it'll be as dangerous as the Walden operation.I hope you're fully aware of the risk.We don't have enough men or supplies, Captain.We don't stand a chance.They've refused to send us any support since the last mission.We can't do this without...Enough, soldiers.An order is an order.Remember, the goal is not to fight a war.
```

### [49] hash=`2e08cbeccfc766a2`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p15`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（15眼中之物）

```text
The Manus leaders are scattered all over the place.Our mission is to find them and finish them.The assassination of the Manus leaders is our top priority.The backup from the Foundation will not arrive until we've completed this mission.In other words, if we fail, we're on our own, right?Let's hope it doesn't come to that.Time to move, soldiers.We've almost arrived at Investigator Bo'anish's coordinates.
```

### [50] hash=`ac988baba4264a32`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p15`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（15眼中之物）

```text
We're walking from here on out.Quit standing in the middle of the road.Hey, are you blind or something?Focus on the operation, Todd.Let's go.Just close your eyes, and it all becomes real.Close your eyes.Stop thinking.Then you will be in paradise.Illusion is also part of reality, is it not?And for me, you should have come sooner.I'm sorry.That's the illusion confused you, Jay!You must break away!I know you're only an illusion.
```

### [51] hash=`64299b6521fdfd3c`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p15`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（15眼中之物）

```text
A thought in my mind that I just can't shake.But even so, I want to stay.There's something I've always wanted to know.Tell me, Paulina, do you want to go back to Haight Street?We'll stay in the restaurant like we used to,but there'll be no drunks looking for trouble this time.Hop on my bike and go for a ride around San Francisco.But then the outsiders arrived, they massacred us, yet our beliefs availed us nothing.
```

### [52] hash=`a18f0917af0b0512`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p15`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（15眼中之物）

```text
Bombs were detonated, and my friends were blown to pieces.The entire isle was shrouded in the darkness of death, but that will never happen again.We have found the eternal paradise.We praise.We rejoice.We punish.We cleanse.We awaken.We are one.We punish.We cleanse.We awaken.We are one.
```

### [53] hash=`89a073b72dd1b4f2`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p16`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（16走吧羔羊）

```text
We've lost contact with investigator Bowen each, please reconfirm the coordinates what captain they're just normal arcanists and humansInvestigator Bowen each said that she left a door at the coordinates that will take us to the ceremony site, butAccording to the plan she was supposed to meet us here.I will leave these uninvited guests to you.They jazzWhat a hypocrite look who's the domesticated dog now, huh?
```

### [54] hash=`477db20f3c1db067`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p16`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（16走吧羔羊）

```text
You enjoy looking the boots of your ownernow let us enjoy their grace we plead let not our joy dissipate let our pain andsorrow fade let our souls what the party what happened got it boss thanks formaking me one of the dead for a while Cheers sorry Matilda I lied to you IAnd we thought that your authentic reaction would be more convincing.Geo reached an agreement with Jay before we left.That punch felt pretty personal, though.
```

### [55] hash=`4d0481a5ac4edcda`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p16`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（16走吧羔羊）

```text
You almost beat the crap out of me, Geo.I couldn't help myself.Jay, you want me to beat him up?No, Hollic.He's an ally now.We got to look out for our friends, right?Yeah, we're friends, huh?Still, if these sons of bitches don't pay up to fix the garage,I'll beat the shit out of them.So be it.I have already prepared a surprise for you blasphemers.Legers, I have exhausted my pity for you.It appears your loyalty is even more worthless than I expected.
```

### [56] hash=`b63589fb133cfd94`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p16`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（16走吧羔羊）

```text
Very well.The door to Elysium shall be shut tight.There will be no cracks for you rats to crawl through.Chosen believers, prove your loyalty!This wasn't part of the plan, Jay.Not even the most bewitching voice can drown out the songs of the birds.Those who dance, those who are blinded, breathe in the fragrance of the medic, and come withme.
```

### [57] hash=`46d63d0f9d25c6bf`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
Everything, everything is ruined.I never should have trusted any of you.Thanks for the show.Your failure was magnificent.Your arrogance, your regret, and that look on your face when everything was ruined.They were all just perfect.you into the depths of the Gorgon Current.I will crack your skull and make you bearthe price of my pain."You'd almost forgotten about your Mediterranean roots.I must say, I didn't expect such
```

### [58] hash=`ac5966b9e2b13c28`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
courage from a coward who fled a battlefield.Your pitiful Sharperdantes are far fromsufficient payment.No one would be stupid enough to go against the Foundation forso little profit.Besides, this was never part of the deal.Do you have any idea who you're dealing with?That's Barrel-Bow and Nisha's daughter, and the weapon that boy carries.But listen, if you don't help me escape, I'll never pay you the other half.
```

### [59] hash=`b9a91019c405c7dd`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
It's true that the people at the Foundation are all misers.They're still more generous than you.I can give you anything.Rare wands, alchemic materials, and jewelry.Lots and lots of jewelry.I got them from the believersThere's more.I keep them in a cellar that only I have the key toYou're a dishonest customer ApostleYou're lucky that your pockets aren't emptyPack your stuff.Let'sHey there little lady.
```

### [60] hash=`451a3cfbc0b40a6f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
Nice to see you againI have no interest in the maness.I just have some business to finishYou know, I'll work with anyone if the deal is sweet enoughI'm a businesswoman.I always keep my word.I'm sure you understand that.You're right.I will not let you escape.You have to take the two of you to the foundation.You can plead your case there.Anyone offer your seat to the senior?I'm from the foundation's logistics department.
```

### [61] hash=`24bede37ccaf7d98`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
Je suis perdue?How does she know my-Everything's here.I swear.You have to make sure I get out of here safely.If you keep your word, I'll tell the preacher about you, and we can do more business together!Come out, Believer.There's been a change of plan.Follow me.Eternity will get us out of here.What a huge collection of valuables!And people just handed them over to you.Looks like religion is a profitable business.
```

### [62] hash=`bc7a77ab120590ff`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
All right, now escort me out of here!I never promised any escort, Apostle.Did you ever hear me utter such a word, but I did say I'd get you out of here safely.Let me see.If memory serves, that tricky little thing is...Here it is.There you go, it's from the St.Pavlov Foundation, one of a kind.This gadget was stored in their headquarters.No one could lay a finger on it, but when chaos broke out, it fell into the hands
```

### [63] hash=`074b37b3f46d7e37`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
of an employee looking to make a profit.What's this?Some kind of wind-up toy?How's this going to help me?Do I look like a completeidiot to you?Of course not, my dear customer.Just wind it when you need to use it.That's all,apostle.What's it going to do?Turn me into some kind of beast?A three-headed dog or acrazed bigfoot?Listen to yourself.Why would I do that to a customer?You won't turn into a monster, I promise.
```

### [64] hash=`145e6bbeb69143f1`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p17`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（17离别赠礼）

```text
There's still plenty of business to be done between the two of us.Time to say goodbye.It's been a pleasure working with you.Wait, wait!Great Inculcator of Arcanum, please bless this child on his knees before you.I am willing to sacrifice every drop of blood in my body so that you may be revived.
```

### [65] hash=`334a967513eb3cff`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p18`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（18别无所依）

```text
This will be useful.Thank you for your help.Now, then.Since Ms.Mercury's density will be unconscious within a minute!Jay!Are you okay?I'm fine.It's nothing.Good thing is the pain's kept me awake, and I can still move my arms.Looks like an exciting show.I wish I could sit down and watch.Enjoy it, miss.Fine.We'll use what I have.Ugh.This sucks, Dad.My forging's not even close to your level.In that moment, your father was...
```

### [66] hash=`e8481877c52d8443`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p18`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（18别无所依）

```text
well, his arms were charred.There was nothing we could do.He was dying, but he wouldn't let the sword go.What I didn't know was that it wasn't he who was holding onto the sword.But the sword that was holding onto him...The sword was gone, holding it in your arms, fast asleep in your bed.Away from it, kid.You may not have chosen it.Sorry, Mr.Tang.Long time no see, buddy.Have a little dream with me, cutie pies?
```

### [67] hash=`eb0e89052acd6967`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p18`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（18别无所依）

```text
What the hell is this monster?Is this thing the girl that was just here?Hell of a transformation.Pretty much not right, it must be from her arcane skill!This seems to be affecting us somehow!Get back!Stay away from me!This sword's got a mind of its own, and it ain't happy!Boss?She, uh, she's moving!Watch yourselves!Melt it down, forge it up.What'd you think about this?Just...half to deaf.Still breathing.
```

### [68] hash=`1b6d154b8dd9a964`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p18`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（18别无所依）

```text
I'm not going down like this, french fry.Nah, gotta check on Holik.No!Boss, stay back!We didn't have to keep playing this little game.You just won't be satisfied until it's over, will you?Let go!Just stay where you are!Hide yourself!Just listen to him, will you?This is starting to become bothersome.no no no I have to do this Jay tell Beckett that I didn't I didn't run awayor cause any trouble this time I'm more useful than he thinks right boss he'll

never make fun of me againDammit!Fire!Only way, someone's gotta see this smoke.
```

### [69] hash=`f650fc33393b9987`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
Jay, really don't give a crap about what you learned on the streets.I don't want to hear it.I'd rather take my chances and die out there than stay here and never live at all.You really think you're going to build connections with the government?Rub shoulders with the upper class?You think they'll take you seriously?You're no different from any of the cannon fodder at the bottom of their system.You're going to be fighting a battle even tougher than the one on Hate Street.
```

### [70] hash=`cd295a9295577b08`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
Why do you think I kept those government suck-ups from finding you in the first place?Listen, it doesn't matter where you go as long as it's not the St.Pavlov Foundation.You could go to college, join a company, a hospital, you'd have a better life thananyone else!A better life than anyone else, huh?Listen to yourself, that's ridiculous!You finally said what you really think, didn't you Jay?Our righteous boss and kind-hearted neighbor.
```

### [71] hash=`026db89e5ce10f18`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
But you know what?I'm not interested in comparing myself to anyone else.I actually want to do something meaningful with my life.Something beyond you.Beyond myself.Beyond the whole of Hate Street.And there is nothing you can do that is going to stop me from pursuing my dream.But who's gonna help you when you're in danger?Those idiots in white robes?How can you entrust your life to the Foundation, and not your family or friends?
```

### [72] hash=`4b1dd89bb67ca5b5`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
And all because of some dream you're not even sure you can realize?You know, one day, you'll come crawling home and cry about how the world is nothing likeyou imagined.And I'll just laugh and say I told you so.Then laugh, Jay.Some people are willing to deal with pain, even willing to sacrifice themselves if theyhave to.If I die out there, it'll be because I chose to.If that's the price I'll pay to protect everyone, then so be it.
```

### [73] hash=`518539fefb9af086`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
What happened, sis?Since when did we walk such different paths?Ever since you beat up that voodooist who tricked me and laughed because I was a human.That's when.You beat him to a pulp, Joe.You forced him to bake on the street.Everyone here is stuck in a vicious cycle.One person tortures another, then he tortures someone else, and so on and so on.It never ends.Well, I think I found a way to break the cycle, and I'm going to try it even if I
```

### [74] hash=`13dcff40160209a0`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
make mistakes.I know you'd think you can stop anything, bar fights, arguments, but you can't stopme.Bike's broken.I'll take the Greyhound.They're not running today.Then I'll walk.I'll walk until I get there.Alright Blondie, ready for a formal in-bath?Foundation!Duty to protect the people!Tell me Matilda, when you come from the menace, are you certain that you have the courage to come face to face with death?
```

### [75] hash=`48db6480d685633f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
Are you sure you're ready to serve as a field investigator?I will do everything I can to protect everyone.With honor and dignity, I will make the Bwanish family proud.Run, you idiot.I don't need you to protect me.I don't need your sacrifice.I don't care about your duty or whatever the Foundation says.I don't fucking care.You don't get it, do you?If you die like Holic back there, everything you have,
```

### [76] hash=`25bb4317c60cd05f`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
Everything you've been through will be gone for good.Tell your boss that I got in trouble because I didn't follow the confidentiality agreement.Tell her I deserved it.And tell her that stupid big guy over there pecked the wrong side and got himself killed.You've done your job.No one can blame you.No, I decline your offer.I will stand until the reinforcements arrive.Ron, forget about us.Save yourself.
```

### [77] hash=`e15eca31cbbe8c29`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
Some people are willing to deal with pain, even willing to sacrifice themselves if they have to.If I die out there, it'll be because I chose to.If that's the price I'll pay to protect everyone, then so be it.I wish you could have lived a different life.I wish you'd been born into a happy family, that you'd had your own room with a huge bedand lived in a beautiful, fancy house.I wish you'd been a rich girl.
```

### [78] hash=`43da396b9d373f9d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p19`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（19绒丝带）

```text
I wish you'd been cherished by your parentsand that everyone had been proud of you.I wish you'd never known about the poverty, disease, and war in the real world.I wish you could have slept in a room without a broken window,on the fireplace that kept you warm at night.I wish you didn't have to live in that rundown room I set up for you.I wish you could have worn new clothes, but no one had them.I wish you could have been surrounded by kind and loyal friends,

who wish never met.
```

### [79] hash=`883697c4528badf3`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Damn it.Just wait and see Jay.I'll make you payHey Geo right you forgot this if you need help find me in the new age marketLet's play a game for you Paulina don't you see itI'd rather die out there than stay here and never live at all.The game isn't over yet, Jay.The Honorable Apostle and Miss Mercuria have been expecting you.Answer me, Jay.What are you going to do when your friends point their knives at you?
```

### [80] hash=`fc0098b5dcd7881a`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
How do we keep their sacrificial lambs from leaping off the cliff?To my days out junkies, my loud and proud mischief makers, and all my beautiful little heartthrobs.It's your oldest and dearest friend, with the straight shooting of your father and tender loving just like your mama.It's your boy Vincent, aka the old ostrich.Bringing you a balanced dish of good news, then let's soften the blow with the good stuff first.
```

### [81] hash=`23305d03448dd31d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
The New Age market has finally gotten a little re-invigoration after the Harmonic Convergence.Was it a sign from another world, or the harbinger of a Mayan doomsday prophecy?Who knows?But why worry, my lovelies?Keep those heads in the sand and your ears to the ground.Because more visitors means more money.Huge potential for young and old to make some dough.To hit you with the bad news, yesterday's gangland battle stretched from the six all the way to the steps of the People's Palace.
```

### [82] hash=`b82d62927c947b89`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
And it came with a particularly heavy drizzle of bullet casings to rattle you all night long.Last night, Legerza dead and his Arcanus minions booted the Tung Ching champ so hard in the ass that they've been driven right out of our city.If you're brave enough to head out into the streets, might still find a few gold teeth left on the ground.Now, the sweet, naive souls among you might think that means our fair city will finally have a moment of peace.
```

### [83] hash=`9a57928bfb6e7a90`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
But you listen to Papa Ostrich here, kiddies.This is only the beginning.What the Jers wants is nothing less than the whole damn city and I have it amongst an authority where he's headed next.I'm told his aim is to make a deal with Hape Street's very own Joe, aka J.Brown, for a steak and that juicy New Age market pie.Here's hoping that it goes smoothly, but if that fails, at least we'll have some quality entertainment.
```

### [84] hash=`2744292e5c8a754d`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Now it's time for the old ostrich to duck his head again, leaving you with some solid music to groove your body and shake your booty with our next track, The Golden City.Pop ostrich.Give me a break.Anyways, what can I get you, guy?Tequila.And?Straightforward.I like that.So what are you after?The waitress's phone number, ticket to an underground boxing match, or you're after someone specific.You know what I'm after?
```

### [85] hash=`86869e713b5f17b5`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
I'm after you shutting your damn mouth.Cut the smart shit with me and listen, because I'm only going to ask once, where is Jay?Point him out, then get your ass out of my sight.Whoa, hey, hey, easy, man.I'd be happy to.You gotta tip me.That bastard owes me money, so you can go ahead and feed his ass.Don't want a kick from me.You better not be playing with me, because that's a good way to get cut.But hey man, little heads up, Jay was born and raised in Haight Street, and he knows
```

### [86] hash=`fd798040acfe0ecb`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
the place better than anyone, and circled around the cops won't be easy to corner.Plus he's got a lot of friends around, so picking a fight here could go south fast.Never know who's liable to stand beside him, but you know what I say, the good timesThank you, sir.I probably shouldn't pry, but what do you want from Jay?If you want to take him down over Hate Street, you'll be disappointed.This place has got nothing but struggling folks.
```

### [87] hash=`0c015a2b423e2226`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
He couldn't mug someone for enough to catch the bus.What else could it be?A damn new age morning.Don't know what Pops is planning to do with it, but he's got to have it.Not like I'd give a damn otherwise.What kind of schmuck does business in a gutter like this?Pops is stubborn about it.Used to be I'd have a say in private, but he don't listen to anyone now except those freaks from the Order of Enlightenment.
```

### [88] hash=`2b9a9bcec5544fc4`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Not that I'm crying about it, but robbing folks who ain't got no money, kicking them while they're down, it don't sit like that.But order's orders, so maybe I'll turn a blind eye.When I can.You asked too many questions.Trust me, you're the perfect bait.You draw the fishies in like a magnet.This is terribly unbecoming of you, Jay.Do you realize how many times this is?My body may be artificial, but my soul can feel pain too.
```

### [89] hash=`38a9d13f325df979`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
You lying sack of shit.Not so friendly after all, huh?We'll continue our conversation later, Jay.Easier to fight here than at back alleys.Now who's lying, Mr.Geo?You took my shot, but you didn't even break that Jay guy's nose.Still, thanks for the offer.Give my best to Mr.Leger for me.The old man is gonna like you, smartass.We'll have another parlay.You and me.Yeah, yeah.Run on home with your tail between your legs.
```

### [90] hash=`a7496b86f685bfe4`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Pfft.Leger's losers.Looks like he might need a dentist, cause he just got kicked in the teeth.They'll be home crying into their cereal soon enough.The way they're huffing it, they could have outrun my four-cylinder Hummingbird GR8100.They must have missed their calling.They ain't dentists, they're trackstarks.Ha ha ha!Cheers to unbreakable bonds!To unbreakable bonds!Look Jay, I gotta go.The shelter is going to be closing up soon.
```

### [91] hash=`e1d525efb6ef7ad8`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
my partner at the shop you know he doesn't like it when I come in coveredwith blood scares the richy rich types away it's all good bro thanks for comingtoday is anything I can help you know where to go thanks bro but if you'rereally such a good friend how about you spot me a quarter mil or so so Ican buy that sweet new convertible lambarari LM-50 well since we'regood buddies, right?Yeah, sure thing, buddy.
```

### [92] hash=`d93b06d75c200a23`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Right after I give you a knuckle sandwich.See you around, Jay.Would you kindly give me back my damn hands already?Hey, stop kicking me.Justa sec.Hi.My apologies.Where were my manners?Please don't take it personally,But I need to warn you that...Whoa, wait, wait.Someone's missing.Where's Mercuria?Hey, Miss Sputnik.Have you seen her?Oh, Miss Mercuria.She left in a hurry, carrying that dagger those rough type gentlemen dropped.
```

### [93] hash=`2362b02f18448fb4`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
Do we follow her?No, of course not.She's just doing her thing.The old man didn't tell us what kind of mess we were in for here.I'm not paid enough for this.Hey, Gio, right?You're just giving it back?What's this meant to be?Some kind of insult?Yo, your boss runs me off, now you're giving me back my own knife like I'm some pity case?Think I won't hurt you cause you're a woman?Think again, bitch!What is this?
```

### [94] hash=`271c86eb5f374e55`

- lang：`en`｜version：`2.0`｜arc：`飞驰！明日之城`
- doc：`BV1ws421M74J_p1`
- title：《重返未来：1999》2.0版本「飞驰！明日之城」全剧情 - Reverse: 1999｜4K（01）

```text
The color of your energy is as dark as the coal in Chase Forge.No.Worse.Darker than I've ever seen before.I'm afraid, but something else besides that, I see a burning energy, the embers of a homereduced to ashes, a harrowing darkness that's followed you throughout your life, when yourwife and child left you, when your debtors begged on their knees at your feet.What are you talking about?I understand you now Mr.
```

