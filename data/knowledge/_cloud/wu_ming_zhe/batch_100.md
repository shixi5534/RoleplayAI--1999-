# 剧情图谱抽取 · batch 100

- 角色：`wu_ming_zhe`
- 批次：**100**（未缓存补漏批 1/8，每批 95 块）｜本批块数：**95**
- 筛选：仅未缓存块｜offset -
- 规范版本：cloud-extract-v1
- 输出：`wu_ming_zhe/batch_100.jsonl`

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

### [0] hash=`8bca4c3dcaba4a3f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
La cabaña con el techo azul estaba silenciosa como siempre.En un sueño fugaz, la investigadora de paracausalidad descubrió la verdad detrás del dado de Babilonia.Examinó cuidadosamente los patrones ocultos.Como un astuto astrólogo rastrea los movimientos de las estrellas.Lo que pueda parecer errores o accidentes no niega las verdades del destino.Por el contrario, afirma en su existencia.Solo pregúntale el gran Heráclito.
```

### [1] hash=`5df933ef259ca415`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
En un universo no observado, el dado de Babilonia gira perpetuamente, dictando el destino de todosen un tiempo que es tanto infinitamente largo como infinitamente corto.Mira, cerró los ojos.Respetaba la aleatoriedad de los números y el destino.Respetaba el juicio del dado, de lo contrario, se habría perdido sumisamente en los huecosdel tiempo y bajaría para siempre como un fantasma en el olvido.Permítanme hacer una cosa clara.
```

### [2] hash=`bc5b99a63bcaf756`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Yo no tenía nada que ver con lo que sucedió a los Idealistas ayer.Lo prometí en mi carrera como escritor.Como todos saben, los Idealistas y yo somos los representantes de las dos faccionesde la Sociedad de Poetas de las Américas.Como también sabéis, hemos estado en paz desde que el acuerdo de acuerdos de las letras de los dormidos fue asignado hace unos meses.A pesar de nuestras ideas diferentes, hemos existido a este día bajo el mirante mirante de la torre central.
```

### [3] hash=`85b7fecdfcd8008a`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Restad asegurados de que trabajaremos indignadamente para localizar al idealista perdido.No pongas tantas presiones en ti mismo, Miss Octavia.Su muerte no fue tu culpa.Después de todo, él fue el que trajo el primer cagón verbal.No te respeto, morons.Perdón mi latidimension, hazlo, estoy listo para moderar.Miss Verde, he analizado la incarceración y los recordes de visitantes de los últimos seis meses.
```

### [4] hash=`bff12276f6297297`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
No había ninguna mención de nadie llamado Doris.Entonces parece que solo el médico sabe los whereabouts de Dr.Dores.Miss Jayla, tenemos que reunirnos con el médico.Es importante.Escucha, realmente no deberías tomar los rumblings de los inmigrantes tan seriosamente.Pero, si es tan crítico como dices, haré otro pedido más tarde.Por lo tanto, me temo que la reunión no suceda por menos un par de días.
```

### [5] hash=`f6c963b6c177ce04`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Entendido.Por ahora, por favor, nos juntemos para hoy, Congress.¡Fectacular!¿Tienen salones literarios como este todos los días?Este lugar es prácticamente un paradiso de escritores.¿Entonces, eres la hosta de este salón, Octavia?Digo que nos separamos de nuestras diferencias y tengamos una discusión literaria titulada.Ninguno de ellos.Este Congreso es sobre la randomidad del destino,Misra Coleta.
```

### [6] hash=`b1963e1bace3d224`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Randomidad del destino?Queridos visitantes de la Fundación,Permítanme presentar el Congreso de Komala.Lo que sucedió ayer fue solo una breve anomalía.En el Panopticon,el orden espontáneo entre los inmigrantes es la norma.Y el Congreso de Komala serve como reflexión truer.¿Oda espontánea?¡Sí!A través del Congreso, los inmigrantes asignan y distribuyen medicamentos,bebidas comunales y periodos de ropa.
```

### [7] hash=`c7c14d3f9101d979`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Están completamente autoreguladas.He anunciado el comienzo del 7º Congreso de Komala.Una caja de cartas y...¿Es eso un papel de papel?Hmm...Tiene 20 signos.¿Huh?Echamos prontos patternes escondidos.Mucho como un astrólogo astrónico trae los movimientos de las estrellas.¿No es esto solo como el Día de Babylon?¿El Macguffin que viva por todo el plano?¿El infinito simbio del destino?¿Y el símbolo que compresa el tiempo en un círculo deslizado?
```

### [8] hash=`67280550fc8657aa`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Lo que puede parecer errores o accidentes no nega las veridades del destino.En el contrario, afirman su propia existencia.Pueden preguntar al gran Heráclito.En un universo sin observación, el Dice se vuelve en perpetuación.Dictando el destino de todo el tiempo, que es tanto infinitamente largo como infinitamente corto.Mira, he cerrado mis ojos.Respeto la randomidad de números y destino.Respeto el Dice Judicial.
```

### [9] hash=`ec508074496e371c`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Otherwise, we will acquiesce and lose ourselves in the gaps of time and wander forever as ghosts in oblivion.I...I don't understand what's going on.Oh, but the irony that I probably have more idea what's going on than anyone here.Miss Racalata, this is all in your novel, isn't it?I'm afraid so.The recitations, the references to an astrologer and Heraclitus...Inmate Jose, por favor venga adelante.Ustedes son los primeros en la orden de iniciativa.
```

### [10] hash=`31d5f48b34bc4497`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Por lo tanto, el juicio del destino va a caer en usted antes de todo el resto.¿Me?¿Ok?¡Ah!¡Qué maravilloso número!¡17!¡Como una oasis en un desierto infinito!El resultado es 17.Y la combinación de los puntos es 6 más 4 más 4 más 3.Según la regla de la Día, él recibirá 60 tabletas de Resperadón, 40 tabletas de Closapin y 40 tabletas de Diasepam.Además, él asume el rol de manager cultural del Congreso de la Comala.
```

### [11] hash=`da3629848c9f47e6`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Antes de ir a la oficina, el inmigrante José debe limpiar el primer vestuario durante los siguientes 7 días.Maravilloso, lo limpio.Tengo la broma aquí, el detergente y el tubo de la taula.He estado esperando esta oportunidad.Como manager cultural, hablaré con todos los inmenes y completar la memoria de Comala.Finalmente capturando los momentos cuando las espaldas de la literaria se ignitan y explotan.
```

### [12] hash=`77e37442f37e4446`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Siguiente es Inmate Eduardo.Por favor, venga adelante.No recuerdo la regla de la muerte.No recuerdo nada.Joder.Lo siento, señora Octavia.Pero no creo que pueda hacer esto.No he tenido ninguna medicina en el último Congreso.He tenido múltiples episodios.Es como...Como si mi cerebro estuviera jodido o algo.Está bien, Inmate Eduardo.Es fácil.No necesitas saber las reglas para robar la llave.Dime tu mano, te ayudaré.
```

### [13] hash=`c747f1e9625765a4`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Mis sinceras disculpas, Aduardo.La llave dicta que debes voluntariamente descender a los cochesy escribir el teclado temáticoque actualmente te causa la mayor ansiedad en las paredes.Muchas gracias, Miss Octavia.Ah, creo que mi cabeza está en la mitad.Necesito un momento para descansarNinguna autoridad ni violencia está involucrada en este proceso.Esto es lo que pone a Komala a salvo de todas las otras facilidades custodiales.
```

### [14] hash=`51a5601ab5e01d28`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
¿Es eso todo?¿Te abdicas toda la agencia para el papel de un papel que muere y lo llamas el randomismo del destino?¿Qué tipo de broma es esto?Por favor, calma, Recoleta.Esto es el método que las imágenes han decidido colectivamente reconocer.Están preparadas para enfrentar los posibles sacrificios que brinda.Esto no es sobre ti o yo.No es nuestro lugar para interferir con un procedimiento que ha sido demostrado,
```

### [15] hash=`1d908e92939767da`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
tanto pragmático como efectivo.Mi obligación es asistir a los inmigrantes en mantenimiento de ordena través de los métodos que han establecido.Y tuyo es verificar su self-governance,no la juzgar.Si todo sucede como lo hace en mi novela,entonces cada rol ya está predeterminada.Vertín, ¿te recuerdas la historia que te dije la noche anterior?Bueno, eso es donde los historiadores vienen.Con un pequeño edificio creativo de los libros históricos,
```

### [16] hash=`639e6542a473db7e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
incluso los roles randomes de un muerto pueden de repente hacer sentido.Lo que antes eran tragedias evocables,son rebrandadas como incidencias reasonable,o incluso resultados desirables.Estás empezando a sonar como un gambler.Pero incluso gambladores,después de golpear un balcón o perder un espelgo,comienzan a convencerse de que han descubierto el gran patrón detrás de los juegos de chance.No son solo gambladores ni siquiera.
```

### [17] hash=`e7db277711abc51b`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p10`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（10费洛蒙漩涡）

```text
Juegas trataron de influenciar el destino a través de rituales y charmas.Los antiguos matemáticos calcularon probabilidades en papel.Algunas incluso escribieron libros sobre la teoría de los juegos.Mientras tanto, otras supuestan que hay cheaters entre ellos.Las muertes se cazan, pero a pesar de que número se ha roto, es hora de cruzar el río.
```

### [18] hash=`762202c1b09a2778`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
Eduardo, what's wrong?Are you taking the medicine right now?There's no need to rush.There's plenty of it.You can have it allPoor Dios Eduardo.How could you squander fate's gifts like this?Kind señorita, please keep me the medication.I need it more than anyone elseI'm the one who needs the mostGive me the medicationIf you disrupt the status quo, the entire system of the Panopticon will collapse beyond repair.
```

### [19] hash=`c41e02bc87197b92`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
It is only by respecting the arbitrariness of fate and adhering to the rules of the Die of Babylon that we have kept this place functioning all this time.The Die of Babylon?Tell me, how did you know this name?Are you the one orchestrating this whole thing?It could be.It is Aleph.Just as Verden suspected.including the role results of the absolutely random Dai.That's right.The Dai of Babylon isn't random at all.
```

### [20] hash=`38bf38e23e680203`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
It's nothing but a supercilious fraud veiled under the guise of fateand an actor of the inescapable loop of history.And...and not one of you is paying attention to me whatsoever.To hell with this era of ignoring unknown writers.Ms.Fracoletta, please make your prediction for the next inmate's Dai role.This way, you can prove to Ms.Jailer the irrefutable connection between Kamala and your novel, The Rise and Fall of Samity.
```

### [21] hash=`054ce73b98d2f793`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
You remembered its name!Oh, what sweet balm to my spirit!Ms.Octavia, please continue the Congress and let the next inmate perform their role.Then Ms.Recoleta's statement will be proven true.I appreciate the reminder.No matter the interruption, the Komala Congress must go on, though not for Ms.Recoleta's sake, of course.Next, inmate, please.Hello, inmate Garcia.You know what to do.Of course.La Sexta Cara.
```

### [22] hash=`8950b6d0b83f2a3e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
Un pila roto.El flujo de la fortuna y la calamidad.So the result of the next roll will be a six.As fate reveals, the number is six.Just as Ms.Recoleta predicted.That could still be a coincidence.Do it again.And the disturbing stillness revealed cruelly that it was a mirage.The sixth face, another pillar broken with teeth identical to the last one,confirmed the hypothesis of the parachute investigator.
```

### [23] hash=`2b9738b8c39bd87d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
This place used to be a circular building.But it's unfathomable.I'll take you to the physician.Not because of your earlier request, but because the situation has escalated beyond my means.The overseer of the panopticon will decide how to handle your situation.To be honest, Ms.Recoleta, I wasn't sure you'd be able to correctly predict everything.But why would Ms.Octavia bring this to us?What's in it for her?
```

### [24] hash=`80349545104f2328`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p11`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（11先知、宇宙、造就）

```text
It worked, didn't it?Come with me.Dr.Merlin's office is in the central tower.Please join a society, Miss Torres.Miss Octavia, while I truly appreciate your kind offer,I'm afraid my conversation with the physician must remain private.
```

### [25] hash=`c7494eef79aae18a`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
Wait here a moment.I'll report the situation in your request to Dr.Merlin.However, since he's always busy, I can't guarantee he'll agree to meet you.But I'll do my best to persuade him.Now's our chance, Sinetto.Our chance?What do you mean, Timekeeper?It's unlikely that the Jailer will let us search the Central Tower, even in this situation.We should take the initiative and look for clues while she's away.
```

### [26] hash=`d933af4c83f125af`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
I'm sure many people have praised the special talent of yours.Are you alright?You don't seem as excited as when we first entered Kamala.The all-seeing sentinel of the Panopticon veiled within the central tower.If it truly is Aleph, I...I don't know how to face such a terrifying and increasingly plausible reality.Sorry to interrupt, but...Timekeeper, I think you'll want to see these.Signed art?Are you truly the supreme ruler of the Panopticon of Kamala?
```

### [27] hash=`88b51dfbfc81f59c`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
Dear Erd, I do indeed have answers for every question, including yours.I'm afraid every one of your speculations is off the mark.I am merely an inmate who chose to imprison himself here.And allow me to point out that your identity isn't as ordinary as you claim.and our territory and hierarchy awareness.Our primitive ancestors, like reptiles and birds,followed such instincts to survive.Through millions of years of evolution,
```

### [28] hash=`c07a325589c921a0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
we developed the limbic system.This process is emotions and forms memories.It allows us to feel fear, sadness, anger, joy.Our behaviors are given meaning.Now it's the neocortex that makes up more than two-thirds of our total brain volume.Language, perception, logical reasoning, abstract thought.This is what forms the complexity of human nature.We read, create, perceive.We try to understand both the world and ourselves.
```

### [29] hash=`03b4e168d5137d0d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
We are forever setting goals, one after another.And all this, these multitude, happens within the confines of the skull, in the tight folds of the crowded cerebral cortex.Is he...performing surgery?Such a delicate and elaborate organ.Were it unable to forget, what would come of it?Can this space, no larger than the palm of my hand, truly accommodate dozens of people at once?It looks like he's dying!
```

### [30] hash=`1ec37b3cbe2b0550`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
Fracassola's surgery?Nonsense.The surgery was a tremendous success.I have erased his debilitating hysteria and restored order to the panopticon.What are you trying to achieve by barging in here?Forget it.The next operation requires my attention.Jailer, show them out.Bring me the next patient in 15 minutes.I'm sorry, Ms.Burton.I'm afraid you have to leave now.Just let us speak with you.It'll only take a moment.
```

### [31] hash=`b043728f918dad63`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
I have something very important I need to ask.Important?Nothing is of greater importance than my experiments in the Panopticon, outsiders.To ensure they continue, the stability of time and schedule is absolutely paramount.Experiments in the Panopticon?So you really are the controller of the prison, then?Controller?What an outdated notion.Superficial, really?The panopticon has no need for such power, regardless of who occupies the central tower, or even if no one's there at all.
```

### [32] hash=`9864f3b13b1b394d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
Every inmate is both the observer and the observed, both wielders and subjects of power.Achieving such a state requires no physical or violent measures.The structure of the panopticon itself is the mechanism which sustains it.Komala is simply a manifestation of this model.The end of this era is imminent, is it not?You know about the storm.That's what you call it, is it?A storm that washes everything away?
```

### [33] hash=`9e4a9ea5a3ff5a6b`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
You employees of the Saint Pavlov Foundation should know better than I.Soon this era and everything in it will cease to exist.I must prove the feasibility of the Panopticon model before this place is turned to ruins.Or something even more unrecognizable.The storm that washes everything away?Burton, what on earth are you two talking about?Hmm...No one can predict the era to which we will be reversed.
```

### [34] hash=`a6b30a0769cb592a`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
I have seen the era as change, time and time again.The transformation of this place, over and over.But no matter which era each of these nine storms, as you call them, has taken us back to,Cor the Ysrael continues to plague this land.Dependency, theorus, martyrs, revolutionists.I've seen them all.You, young writer, are no different from those intellectualswho were swept away in the rain.There is no romance in this era.
```

### [35] hash=`fdb9be5360c444c6`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
Only the repeated cycles of madness and brutality.An endless, meaningless struggle.Only in this forgotten corner can we momentarily escapethe plundering of the Marauders and the chaos they unleash, although it won't be long beforethis place is looted by those oily-headed lunatics, just as it has countless timesbefore on this land as rich as silver.But there is still hope.Even in a wasteland, we may still be saved.
```

### [36] hash=`8f52c259ca1eebb2`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
As long as I uncover the path to transcendentality, I will find the ultimate answer.Ugh, I've already wasted far too much time on you.Leave.Now.You heard him.Please don't press things any further.Alright, Signora.I get it.Obviously you don't want to discuss my novel with me anymore.So I won't insist upon it.All the letters we wrote to one another, all those inspiring revisions and suggestions...I guess they meant nothing to you, but there's still something I must tell you.
```

### [37] hash=`b88197c807b22379`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p12`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（12台前，幕后）

```text
Jailer, could you please allow us a private conversation with the facet?No, with Aleph.Leave us, Jailer.I'll spare these outsiders five minutes.
```

### [38] hash=`8e23bc6505c63f83`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
here escapes my notice.That said, it isn't easy to work a miracle as we all know.I shallpersonally verify it all myself.What's happening?Visitors from another era,you have come here with plagued ideologies in an attempt to break the subtle balance of theoptical, but did you not notice the tiles beneath your feet, the cracks and water stains on the walls,constantly changing right before your eyes?This room, the previous room,
```

### [39] hash=`4fb47050c6ece565`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
every room, you have blindly wandered through them, seeing them as nothing more than thebuilding blocks of a monotonous lab room.But this place was not born from the chaoticof a madman.No, every inch has been crafted through the meticulous harnessing of orderand power.Every wisp of spider silk drifting in the wind.Every speck of rust on the galleryrail.Every detail of the Panopticon has been built by my own hand.
```

### [40] hash=`0ca5833e910a6fc0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
With this ever-shiftingConcepts may be transformed into reality, and ideals into substance.I observe the movement of every entity, the passage of every second,the moment you entered this realm.You too became subjects of my experiment.We shall complete it.Move carefully.Admit it.This is all getting out of hand.Impossible!All is under the die's control.I have not failed, as long as I keep the prison running.
```

### [41] hash=`f36ee5d84127d4f0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
It isn't your power model running the prison, it's the Dai.It's simply a form of magic, unrelated to the micro-physics of power you seek.It provides no aid in your experimentation with power.It's a false hope.A castle in the sky given to you by the military junta and Manus Vindicte.Manus Vindicte?Are working with them?What exactly do you intend to do?I...Then I've also failed.I've ended up a pathetic fool, lost in the chaos of reality.
```

### [42] hash=`c52a2548a25d7f5f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
Just like the idealist, chasing visceral realities.Paracelsus seeking the Fountain of Youth.And Zaheer obsessing over the one-sided coin.When did it all start falling apart, Aleph?When the door knob loosened?When the prisoner's wounds started to fester?Or when the daily disinfectant concentration reached 28 mg?Or the crack in the second-grade brick on the wall expanded to 6 mm?Or was it when Warden Tartuffe left Ushuaia
```

### [43] hash=`992ed5e2a0b9a307`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
with news of the Foucault Association's dissolution?This place should have been the ideal ground for psychoanalytic practice.Why did they halt all research?All discussion?We've been abandoned, haven't we?By eras old and new.You designed and have maintained everything in Kumana,right down to the smallest detail.But it is these details that trap you.And as the bars close around you,You are losing your name, Mylan, and you are becoming a physician, a man forever imprisoned
```

### [44] hash=`3b2314659cade1f5`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
within these walls.I don't understand.All these false ears are like a dreadful novel with no conclusion.Trying to find answers within such things is, in itself, a mistake.Much like them, you are destined never to attain transcendentality.Tell me, Olive.Does the ultimate answer even exist?And you?And this recoleta?Are you okay?This recoleta?You're...The word utopia derives from Greek.It means no place.
```

### [45] hash=`a185ba464025b05a`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p13`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（13迷宫的主人）

```text
People cannot understand the structure of the labyrinth, yet they continue to follow its paths.They cannot comprehend the mechanics of fate, yet they believe in its jurisdiction.As if, by doing so, everything will naturally fall into place, and now, the Pole of Nightapproaches.How good it is to see you, Henpal.
```

### [46] hash=`29ebe44148944baa`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
Are you the one controlling Panopticon with the dye?The one hiding Mr.S's whereabouts?What curious inquiries, quite different from the last 2,666 questions I've received.My guests, you may call me Aleph, or by any other name, be it a symbol of God'soneness or a farcical epithet, I am merely one of the many prisoners who voluntarilyreside here.delusions of verses.The idealist lost his own name, Elin II, imprisoned himself within
```

### [47] hash=`f8591e127c9c9614`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
the system of the Panopticon.I'm sure their desperate pursuits caused you some trouble.Please forgive them.After all, your fleeting encounters led to the demise of them both.I think I understand now.The idealist and the physician are both parts of you.Or,To put it another way, they're your alter egos.The physician mentioned Manus Vindicpe.What's the relationship between this prison and the Manus?Visitors from the Foundation.
```

### [48] hash=`9a254f5e470a8aa9`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
We all witnessed those eras perish.In 1977, not long before the fourth storm, I arrived in Ushuaia.Shortly after, some members of the National Foucault Studies Association reached out to me.But it wasn't just them.An Arcanist organization called Manus Vindictae also approached me.Each of them wanted answers.They named me their advisor.You acted as an advisor to the Manus?The two parties presented me with a concept and a parable, respectively.
```

### [49] hash=`5f0c215704a441b8`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
Concept and a parable?The Foucault Association sought to explore the feasibility of the Panopticon concepthere.While Manus Vindicte showed me a parable of the past and future, day and night I wanderedthrough endless texts, endless realities, as I searched for answers.And thus, Merlin was born.He was both an experiment and a price I paid, a new concept, a new direction.Pursuing such things always leaves me confined by the limitations of human knowledge.
```

### [50] hash=`d05aa1ea11d19af3`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
Merlin spent his entire life exploring Foucault's theories in pursuit of that singular, yet infiniteanswer.What about the Manus, Mr.Aleph?You didn't explain why you helped them.Explain why?Because they asked me to, just as you have.I simply worked to answer their questions.So you're saying that, to you, we are no different from Manus Findictae?And if we ask, you'll answer us without holding anything back?
```

### [51] hash=`e82b2cfbb08caf26`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
Is that not precisely what is happening this very moment?Hmm.This is what the Manus gave Merlin, a magical die named the Tear of Komala.It was once a gemstone that belonged to a god.At the beginning of the century, explorers plucked it from an ancient gate they discoveredIn Antarctica, to the explorers' amazement, the gemstone could turn human desires intoreality.So, they cut it into a die, a symbol of fate, and used it to build a sanatorium, which
```

### [52] hash=`b37941ba022050f5`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p14`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（14镜子的面具）

```text
was later transformed into the Panopticon you are standing in right now.You really are the mastermind behind the Panopticon?Marlin used the Panopticon to seek his answer.tell me what is it you really want it's not about what I want it's about whatyou want the third line of your first letter you said you wanted to give therise and fall of sanity an ending
```

### [53] hash=`a8ddc848cfaef45e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Los registros históricos del dado de Babilonia aún se pueden encontrar en la biblioteca de laUniversidad Santa Teresa.No, no, no.Una apertura como esta haría la historia demasiado ambigua.En 1975, en el pueblo de Amalfitano, Sonora, México, ocurrió algo terrible y escalofrianteEl empleado del banco también entró al bar trayendo la noticia de que una cooperaciónmultinacional iba a construir una fábrica de jabón de galletas en Amalfitano.
```

### [54] hash=`68ef47cdca96f865`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Espera, ¿empleado del banco?No sabía que había bancos en Amalfitano, pero sí, tiene sentido.Los bancos comerciales son, sin duda, un sello del capitalismo.¡Gracias, amigo por correspondencia!Antes de convertirse en empleado del banco, era un defensor de las antiguas costumbres del pueblo.Era un pescador de dunas.Después de aceptar el destino otorgado por el dado de Babylonia,Se eligió dejar todo atrás, el triste y aterrador pueblo y los ciclos ocultos dentro, de la
```

### [55] hash=`9910621ccc9b361f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
infinita a la torredad.Oh, qué irónico, pero también es realista.Ahora solo necesitamos un personaje contrastante.Un creyente en el destino, una anciana tejedora, se sentó en su antigua taller, girandoincansablemente su rueca.Un regalo precioso, otorgado por el dado de Babilonia.La tejedora ciega relató suavemente todo lo que había vivido.¡Qué idea brillante, Aleph!Una tejedora ciega no podría haber presenciado el asesinato.
```

### [56] hash=`23acd481747f7567`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
¡Fantástico!En este caso agregaré a un conductor de burros que es asesinado en estecapítulo.Con cada una de tus sugerencias, la historia da un paso adelante.¡Gracias, Aleph!Pero todavía no veo ninguna señal del final.Es como si no importara cuántospersonajes nuevos agreguemos.Todavía falta algo en el pueblo desértico, lefalta una figura clave.Aleph, ¿qué debo hacer?¿Cómo le doy un final a estaMe describiste cómo tus palabras se habían transformado en un rompecabezas desmesurado
```

### [57] hash=`ea6f56bb838b50d0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
infinito, un lenguaje irreconocible, una colección de información ambigua, y unaparábola que había perdido todo su significado, la ausencia de un final aún terroir, atrapándotepara siempre en ese abrazador pueblo desértico.Todo lo que estoy haciendo es intentar encontrarlo para ti.¿Estás diciendo que has estado manipulando los acontecimientosen el panoptico desde que intercambiamos cartas porprimera vez septiembre pasado?
```

### [58] hash=`082dbe2cd8691708`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Sí.Cada vez que revisabas la novela,se hacían ajustes correspondientes en el panoptico.Reflejar fielmente las complejidades de cada detalle era clave para asegurar que la Historia avanzara sin problemas.Estos ajustes los manejaba principalmente Merlin, a veces el idealista, y antes de ellos, Zahir y Pereselso.¿Cada vez?Seis versiones de la historia de Omalfitano ya se han desarrollado en el plenoptico.
```

### [59] hash=`42ee7d776a4ae820`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Eso significa la rana aplastada en el parro, la vaca muriendo de vieja, el lirón cayendo al mar,el fantasma asesinado en el duelo, y los cambios repentinos al dado de Babilonia.Todas las revisiones que sugeriste, todas las muertes, el caos y la locura, ¿realmente sucedieron aquí mismo?Incluso la eternidad tiene sus límites recoletas.En la 6ª revisión, añadimos el Blind Weaver, una figura extraordinaria.
```

### [60] hash=`04d8347bcc0b5db1`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Justo como el investigador de paracausalidad que trae un suéter que te presentaste en tu 7ª letra.El investigador de paracausalidad que trae un...suéter...Miss Recoleta, ¿es este personaje realmente basado en el Tempo Keeper?¿Qué?Por supuesto que no.El investigador de paracausalidad es un personaje totalmente diferente.Estabas buscando su fin, pero cómo pudiste encontrarlo cuando ya no estás más dentro de la historia.
```

### [61] hash=`0259a09883d0838e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Pienso que esta vez, verás el gran final con tus dos ojos.No más tristeza, no más soledad.La respuesta a la que esperabas, está en la final ronda inevitable de la muerte.El Juegler es el Juegler del Banco, y D'Urde es el Juegler blindado.Pero, ¿qué pasa con Roberta, García y Octavia?Ellos no tenían roles asignados.Ellos solo...jugaban cosas, sin ayuda, en la cara de su destino.¿Qué derecho tienen tú o yo para decidir lo que suceda a ellos?
```

### [62] hash=`6cff53728f0c5eed`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Para dictar sus ganas y pertenencias.Pero ellos no podían poder entender algo así, ¿verdad?A ti solo es una historia, pero a ellos es una manifestación de destino dulce.¿Crees que escondiendo detrás de la mirada de la ficción te absolve de la realidad de que has convertido el Panopticon en un cielo vivo?Sí, eres la única que realmente entiende el rostro y el fallo de sanidad.Dios sabe cuántos manuscritos he enviado, pero nunca he recibido una respuesta.
```

### [63] hash=`922f946d240cc128`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Estaba tan agradecida a ti, por tus respuestas, por comprender mi novela, esas cosas eran más preciosas para mi que cualquier descanso sobre el Andes.Si lo sabía, pero tu feedback fue creado de tal manera, y a tal costo, me gustaría no recibirlo en todo.¿No lo entiendes?Incluso si no entienden mi novela, las personas con las que conocí, aun son mis amigos.No importa si tomamos un largo viaje juntos, o simplemente hablamos por pocas horas.
```

### [64] hash=`ee85d156ff9f3612`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Formamos una bondad inesperable, maravillosa.Ellas son parte de mí.¿Cómo podrías tratarlas como personajes ficcionarios?Es disrespetable a mi trabajo, y a la vida en sí misma.Pero, tú crees la pregunta a ti mismo.¿Por qué te resistes a recibir su respuesta?Siempre son así, ¿verdad?Le piden una pregunta a ti solo para abandonarlo con el desvanecimiento de la ira.Esta estornura no va a juzgar a nadie.
```

### [65] hash=`e0bf40fd931dccf9`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Lo has conocido todo el tiempo, Alan.Solo el inocente Panopticon puede mantener control.La torre de todo el mundo.El perfecto sistema de gestión.¡Qué chistoso estupendo eres, Mérida!¿No has oído lo que dicen?No hay necesidad de construir un laberintocuando todo el mundo ya es uno.Tus preguntas sin significadoserán desnudadas por los tiempos de tiempo,solo para resurfecer en los ríos de nuestras mentiras una vez más.
```

### [66] hash=`7cc6968cf3bf9d90`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Lo hemos visto suceder,sobre y sobre de nuevo.Seguramente lo has realizado por ahora,pero el único verdadero significadopuede ser encontrado en la literatura.Por más de un siglo, la literatura ha quedado la última respuesta singular.Este solo caballero, simplemente sentado perdido de amor.¡Vámonos, vosotros!¡Estáis perdiendo nuestro tiempo!¡Encantado!Nuestro izquierdo parece estar en un estado terrible.
```

### [67] hash=`acbe4234943d36e2`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Tenemos que ser cuidadosos.Algo no está bien con esa escena.No hay esenciales para escribir la poesía.Tú, yo y tu poesía.Jajajaja, venga, mantenga la historia.Lleguéla por hasta que finalmente sientamos la hermosa gratitud del final.Tus esfuerzos son asustados por fallar.Hay solo madridas en literatura y arte, no trascendentidad.¿Puedo hacer algo?Si escuchas, ¿cuál es la fantasía que tengo que hacer esto?
```

### [68] hash=`7120636e3cd13ec0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Por favor, no te desmanes.Andy, ¿puedes?Andy.Estas exploraciones, estas fracciones, son fallecidas, ¿no es así?En esta expansión infinita, siento nada más que tristeza infinita.Mister Aleph, ¿estás humana?Por la muerte pacíficamente.Mister Aleph, por favor, no te resistas.Es futil.Futil, sí, todo es futil.La cárcel de las reglas, los ideales de la literatura,ambos son futiles.Mieras ilusiones congelan un largo camino a la trascendentidad.
```

### [69] hash=`4ac872cbf6c8a6f7`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p15`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（15阿莱夫）

```text
Todos se sienten que son nada más que fantasmas en el sueño de alguien más.La realidad va a devorar todo, incluyendo su propia existencia.Es por eso que se desplazan más, más lejos de la transcendentalidad.No se podían romper libre de ese sueño falso.Ninguno de ellos lo podía.Tanto el médico como el idealista caminaron hacia su propia destrucción,como lo esperaba.Pero tu novela todavía tiene esperanza, Recoleta.

Su fin no ha sido escrito todavía.
```

### [70] hash=`f95f6257b7ad8441`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
I'm afraid we can't publish your novel in its current state, Recoleta.We look forward to seeing more refined work from you in the future.Ah, Senor Cruz!What a pleasure to see you here.I'm an editor from the Naranja Dulce Publishing House.Could you spare a moment to discuss the copyright for The Bluebird?We're huge fans of your children's literature.Hey, relax, Recoleta.Look at all the books around you.
```

### [71] hash=`e2243bf4075b659b`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
This place is heaven.You can't get down on yourself.Not here.So, maybe what I need is to find someone to share my manuscript with.But who?Radeo Amazuns.Aleph Averroes.It's you, senor.Don't worry.I promise I'll catch up on the rent next month.Although I must say, this apartment's hardly worth the price.The cracks on the walls must date back to the last century.Oh, you don't even want to know about the terrible things that happened in that factory.
```

### [72] hash=`a2286637c42ede55`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
All I did was lend the oppressed workers a hand.Bah, you're just like those college kids, full of hot air.Anyway, I am not here about the rent.Didn't you tell me to watch out for your letters a while back?Wouldn't you just return from abroad?Well, here it is, a letter for you.Someone actually wrote back to me!Incredible!I found an actual real-life writer!What's the big deal?I wrote plenty of poems in middle school.
```

### [73] hash=`503962039a2b924f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
I have a feeling we're about to embark on an incredible adventure together.Are you interested in joining the Visceral Realism Movement?What?I've never heard of it, but it sounds like fun!Fabuloso!We have no time to waste!Once I finish this letter, you two must join me on a journey to Ushuaia!Ushuaia?The end of the world?Why the heck would we go to that icebox?Oh, don't be such a downer, Pancho.Just think of the fun we'll have, the breathtaking scenery we'll see, and the incredible stories we'll hear.
```

### [74] hash=`58c82cfe94aa4fd8`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
Fine, Maria.I'll deal with the cold if you really want to go so badly.By the way, could you tell us about your novel?Of course.I'll tell you all about it on the way.Hmm.Now where to begin?Alright, let's start with the cottage with the blue roof and a malcitano.It's been six months since we first exchanged letters.Since then, I've been traveling.First from Chile to Mexico, then from Mexico to Argentina.
```

### [75] hash=`a18aeb0c60aefb2b`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
And I've never stopped writing.I'm not really sure what the purpose of my novel is.I just keep writing and writing.I can't stop.You are a ghost, wandering this forsaken land, still striving to create a miracle.You are a wandering poet, born in a Malfi tunnel, the foolishly brave protagonist of the story,and the embodiment of the author herself.A reflection, yes.The author, no.You are simply a figment of her imagination, a manifestation of her dream to wander
```

### [76] hash=`73400f7c2a24cca2`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
Have you not realized it?The literary pursuits and romantic adventures youdescribed, they are merely faded memories from 1975.The poets who joined thevisceral realism movement with you left Latin America long ago.Faded memories?As for the novel, it's yours now.A story you're writing.has ever understood the story of that town, let alone offered any revisions.Following your advice, I added the bank clerk, the dune piscator, the blind weaver, and
```

### [77] hash=`50e49f86d5e7803c`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
the murdered donkey driver.Amalfitano was no longer an empty town with a single blue of cottage.The new ghostly residence had begun to fill the skies over it.The story was finally reaching completion.But even if I am a ghost, as you say, an incarnation of someone else, a fictional being, so what?My resolve will not waver, even if my existence is bound to fade away.Because this isn't what literature is supposed to be.
```

### [78] hash=`cd05462dd3fb2e2e`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p16`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（16虚构的界限）

```text
You once told me there isn't an ounce of reality in fiction, only voids and glorifiedlies.Let me tell you this, whether real or fictional, corporeal or intangible, I have accepted myexistence.Now, let's put a stop to this, Aleph.The inmates aren't characters in my novel.They're people trapped in a prison, just as you are.By simulating my story here, you have made me into some kind of god, a guilty false

Creator a dictator of fate.I never wanted any of thisI never imagined that the spinning wheel would spin again...
```

### [79] hash=`46b12b580cd36e99`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Qué sueño, no es extraño, el sabor de la realidad, tan amargo y triste, pero llenode pensamiento dialéctico, tal vez la gente del panoptico reflejaba mis pensamientosinternos, entonces realmente soy un personaje en la novela, la misteriosa cabaña conel techo azul fue mi hogar todo el tiempo, entonces los rumores que los fantasmas propagaron¿Eran realmente eso?Rumores.Bienvenida de nuevo a Amalfitano, querida escritora.
```

### [80] hash=`3e65fd7f610f4605`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Gracias, querido ícono del capitalismo.¿Pero no desgarré esta novela en pedazos?Verás, Amalfitano es una dimensión más allá de la vida y la muerte.Este pueblo es un reflejo de tus pensamientos internos.Es incorpóreo.No puedes desgarrar algo, incorporo en pedazos.La literatura es infinita y atemporal,como un río que fluye a través de la vida y la muerte.No me extraña que seas mi personaje favorito.
```

### [81] hash=`c140388fbd7ecd1d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Nunca dejas de iluminarme.Desafortunadamente, la literatura es una vocación peligrosa e inútil.Nadie entiende realmente.Ni siquiera recuerda tu trabajo.¿Recuerdas el dicho?Los únicos, verdaderamente muertos, son aquellos que han sido olvidados.Recoleta, desaparecerás para siempre si dejas a Malfitano otra vez.Será como si nunca hubieras existido.Siempre he admirado tu pensamiento crítico, señor.Engaja perfectamente con tu rol.
```

### [82] hash=`efd0c794805c9cee`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Todo estará bien, Recoleta.Lo que sea que haya pasado, ahora has regresado.Eso es lo que importa.El dado de Babilonia rodará de nuevo.Y cada uno de nosotros obtendrá nuestros finales.¡Así es!Resuelve el asesinato en el bar y pon mi alma en paz.Libera el pueblo de la locura infligida por el antiguo espíritu.Arregla la aleatoriedad del dado de Babilonia y aplana la frecuencia catastrófica.¡Lanza la obra de la mesa!
```

### [83] hash=`b48497a3813fa27f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Entonces, ¿el final que he estado buscando es el que el otro yo no pudo darme?El yo que se lanzó de cabeza a la lucha contra un poder invencible.El yo que finalmente dejó esta tierra.Después de todo este tiempo, finalmente he encontrado mi final.Solo un lanzamiento más, y todo habrá terminado.Mi historia, mi pueblo, todo finalmente llegará a su fin, pero el sueño sobre el panoptico también terminará, ¿verdad?
```

### [84] hash=`3a071365a831e191`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Oh cariño, es solo un sueño.No me digas que estás abandonando tu búsqueda de toda la vida por un miserable sueño.Ese sueño es cruel.Nadie entiende esta gran novela y ni este pueblo asombroso.Pero aquí, eres una verdadera escritora.Este es tu hogar, Recoleta.Pero ya extraño a mis amigos en ese sueño.Existe, así como este lugar existe.Pero nosotros también somos tus amigos, Recoleta.Podrías desaparecer si dejas a Malfitano.
```

### [85] hash=`f8dfab93b0984bf1`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
¿Estás segura de que quieres irte?Sabéis como soy, queridos amigos.He pasado mi vida emprendiendo aventuras tontas y no recompensadas.Así soy yo, ¿verdad?Amalfitano es, en efecto, un lugar ideal.Un lugar para vagar, para un viaje corto y para perderse un rato.Y tiene ustedes, mis amigos ficticios, a quienes quiero tanto.Pero debo regresar a mi sueño y ver a mis amigos ahí.Ellos son igual de importantes para mí.
```

### [86] hash=`067ae98625eb8fa8`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Sí, tienes razón Recoleta.No se puede negar que eres un alma noble y apasionada.Cada uno de nosotros lo sabe.También eres nuestra querida amiga.¿Por qué te tendremos de hacer lo que realmente deseas?Te deseamos lo mejor, Recoleta.Buenas noches, querida.Que tu sueño sea dulce esta vez.Gracias a todos, mis amigos.Nunca los olvidaré.Maria, Pancho.Ustedes son los mejores amigos de viaje que he tenido.
```

### [87] hash=`b3c2b33656e77af7`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Nuestros pasos pueden diverger en el futuro, pero los alejados recuerdos de nuestra viajación a través de las tierras,los bosques, y los desartes juntos, permanecerán para siempre.Es genial estar con vosotros.Ustedes son totalmente un tipo.Estaremos esperando por vosotros en mi vinagre.Un pequeño sol después de un duro día de trabajo te hará bien.Hay ambición en su escripción.Es pasionante, poética, fracción y caótica.
```

### [88] hash=`7f09708619fe7441`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Pero cuando se ve como todo, su trabajo se siente como......un poco más que una ilusión superficial.No es suficiente la profundidad para tocar la alma.Me refiero a dar más comentarios......hasta que se deje de romantizar sus aventuras infantiles.Para ponerlo en blanco, su frasología se siente muy deliberada, al punto de distorsión.Su verbiage es como una colección de bocas sentimentales vagas.Lo veo, Aleph.
```

### [89] hash=`a1c557199ccb1a2c`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Entonces esto es lo que realmente sientes sobre mi novela?Un millón de reyes interpretarán una historia de miles de diferentes maneras.Algunos creen que el texto mismo está muerto.Y es el rey quien le da vida.La verdad no puede ser completamente convocada por palabras sola.Eso dicho, creo que el rise y fallo de la sanidad es una buena historia.El paradiso eterno es una biblioteca de tipo.Como siempre lo imaginé.
```

### [90] hash=`a26869602f5f5ae0`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
¿Es esto solo una reflexión de mis pensamientos?Me gusta aquí.Es bueno estar rodeado de literatura.Es hora de volver a la realidad.Estas bien sobre la literatura, Dorsite Bagger.Es una llamada peligrosa y futile.Pero el Amalfitano nunca logrará su fin.Usted ha nullificado su existencia, rendiendo todo esto sin significado.Lo siento, no pude responder a tu pregunta.He falto nuevamente.El Amalfitano y el Panopticon eran dos partes de una habitación.
```

### [91] hash=`92d0863d442e86b7`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Con el Amalfitano desaparecido, Komala no tiene ningún motivo para existir.Lo siento, Aleph.Ustedes, que saben todas las misterios del mundo, que buscan respuestas a cada pregunta,se han perdido en el proceso, puedes responder las preguntas de todos los demás, pero nunca tu propia.¿Quién es la persona detrás de ese mascarilla?¿Es él real?¿Sigue existiendo?Tengan vigilancia, todos.Esto es como cuando el idealista y el físico tuvieron su deslizamiento.
```

### [92] hash=`c1d1a2328a76e84f`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Solo esta vez.Parece que incluso fue.Creo que...Aleph está tratando de derrotar el Panopticon.¡Frieza!Están donde estés.Todos ustedes.Tienes un profundo respirado, soldado.La fiesta se acelera ahora.Esta historia, esta batalla,pronto se terminará.Drawing strength from her wanderings and rebellious exploits,she attempted to change society,wielding the sword of literature as a revolutionary intellectual and a leader of thought.
```

### [93] hash=`57e2871c9855c992`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p17`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（17往昔的幽灵）

```text
Some would hail her as a battle angel of Latin America,with words as piercing as bullets and poems as powerful as tactical bombers.Many share your doubt, myself included.Como para la literatura, bueno, probablemente es mejor no comprar demasiado en el boom latinoamericano.Olvidate del reporte de estatus de antes.Eso dicho, al menos hay una cosa que es cierta.Los libros pueden romperse y se van a dejar escarras.
```

### [94] hash=`1038fafbb543053d`

- lang：`en`｜version：`2.6`｜arc：`疯癫与文明`
- doc：`BV113PpeBENj_p18`
- title：《重返未来：1999》2.6版本主线「疯癫与文明」全剧情 - Reverse: 1999｜4K（18愚人颂）

```text
I was just setting up my exhibit.When everything started shaking, then I realized it wasn't just my imagination.So I followed the cracks in the wall and found my way here.I didn't mean to interrupt.Something's happening to the Panopticon, isn't it?Are you the physician?Or is it whoever you are?Please, please restore the Panopticon to the way it was.I'm begging you.You can do that, right?Why aren't you doing anything, dammit?
```

