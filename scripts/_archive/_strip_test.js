// MarkerStripper 流式原型 v2：token 流 → 净化文本流 + 标记事件，含对抗样本。
const VALID = new Set(['e_idle','e_weixiao','e_nanguo','e_yansu','e_yihuo','e_mianju',
  'b_diantou','b_liaofa','b_shanzi','b_taishou','b_yaotou','b_zhelian','b_idle',
  't_idle','t_bizui','t_weixiao_bizui','t_nanguo_bizui','t_yansu_bizui']);
const TAG_SHAPE = /^[ebt]_[a-z0-9_]+$/;   // 只有"像词表"的才可能被吞
const MAX_TAG_LEN = 32;

function createStripper() {
  let hold = '';
  let out = '', actions = [];
  function step() {
    while (hold) {
      if (hold[0] !== '[') {
        const next = hold.indexOf('[');
        if (next === -1) { out += hold; hold = ''; return; }
        out += hold.slice(0, next); hold = hold.slice(next); continue;
      }
      const close = hold.indexOf(']');
      if (close < 0) {
        if (hold.length > MAX_TAG_LEN + 2 || /\n/.test(hold)) { out += hold[0]; hold = hold.slice(1); continue; }
        return; // 未闭合且仍可能是标记 → 暂扣（stall），等后续 token
      }
      const inner = hold.slice(1, close);
      if (TAG_SHAPE.test(inner)) {
        if (VALID.has(inner)) actions.push(inner); // 合法→发事件；幻觉词→静默吞
        hold = hold.slice(close + 1); continue;
      }
      out += hold[0]; hold = hold.slice(1); continue; // 形状不像→放掉'['
    }
    return;
  }
  return {
    feed(tok) { hold += tok; step(); },
    flush() { out += hold; hold = ''; },
    text: () => out,
    actions: () => actions,
  };
}

const CASES = [
  { name: '正常标记句', toks: ['[e_weixiao]你', '好呀 ', '[b_diantou]', '欢迎回来'],
    a: ['e_weixiao','b_diantou'], t: '你好呀 欢迎回来' },
  { name: '标记被token腰斩', toks: ['[e_', 'weixiao', ']今天', '天气不错'],
    a: ['e_weixiao'], t: '今天天气不错' },
  { name: '流尾半截标记必须放行', toks: ['好，', '[b_sha'],
    a: [], t: '好，[b_sha' },
  { name: '非词表形态方括号放行', toks: ['引用 ', '[不确定]', '这里'],
    a: [], t: '引用 [不确定]这里' },
  { name: '引用序号[1]放行', toks: ['见文献[1]。'],
    a: [], t: '见文献[1]。' },
  { name: '前缀形似但幻觉→吞不发', toks: ['嗯[e_bogus]哦'],
    a: [], t: '嗯哦' },
  { name: '嵌套方括号', toks: ['[a[b]c]正文'],
    a: [], t: '[a[b]c]正文' },
  { name: '超长伪标记不卡流', toks: ['[' + 'x'.repeat(40), ']尾'],
    a: [], t: '[' + 'x'.repeat(40) + ']尾' },
  { name: '纯文本无标记', toks: ['就', '是聊天', '而已'],
    a: [], t: '就是聊天而已' },
  { name: '换行+标记混排', toks: ['[e_yihuo]嗯？\n\n[b_yaotou]没有', '办法'],
    a: ['e_yihuo','b_yaotou'], t: '嗯？\n\n没有办法' },
  { name: '标记内含换行→放行', toks: ['[e_weix', 'iao\nx]后'],
    a: [], t: '[e_weixiao\nx]后' },
];

let pass = 0, fail = 0;
for (const c of CASES) {
  const s = createStripper();
  for (const t of c.toks) s.feed(t);
  s.flush();
  const okA = JSON.stringify(s.actions()) === JSON.stringify(c.a);
  const okT = s.text() === c.t;
  const ok = okA && okT;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${c.name}`);
  if (!ok) {
    if (!okA) console.log(`   actions got=${JSON.stringify(s.actions())} want=${JSON.stringify(c.a)}`);
    if (!okT) console.log(`   text got=${JSON.stringify(s.text())} want=${JSON.stringify(c.t)}`);
  }
  ok ? pass++ : fail++;
}
console.log(`\n${pass} pass / ${fail} fail`);
