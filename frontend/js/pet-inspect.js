/*
 * pet-inspect.js —— Spine 动画巡检页逻辑（P0-T1 临时调试工具）
 *
 * 用途：实播 s_room.skel 全部动画，人工确认语义槽位，导出 animation_map.json。
 * 依赖：spine-player.js（window.spine.SpinePlayer，素材包自带 4.2 运行时）。
 * 记录存 localStorage（roleplay_spine_inspect），刷新不丢。
 */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  let player = null;          // SpinePlayer 实例
  let animations = [];        // [{name, duration}]
  let records = {};           // name -> {slot, note, duration}
  let current = null;         // 当前选中动画名
  let currentSlot = "unknown";

  const LS_KEY = "roleplay_spine_inspect";
  function loadRecords() {
    try { records = JSON.parse(localStorage.getItem(LS_KEY) || "{}"); } catch (_) { records = {}; }
  }
  function saveRecords() {
    try { localStorage.setItem(LS_KEY, JSON.stringify(records)); } catch (_) {}
  }
  loadRecords();

  function log(msg) { $("log").textContent = "[" + new Date().toLocaleTimeString() + "] " + msg; }

  function renderStats() {
    const total = animations.length;
    const done = Object.keys(records).filter((k) => records[k] && records[k].slot !== "unknown").length;
    $("count").textContent = total + " 动画";
    $("done-count").textContent = "已标注 " + done;
    $("done-count").className = "badge" + (done > 0 ? " warn" : "");
  }
  function renderList() {
    const sel = $("sel");
    sel.innerHTML = "";
    animations.forEach((a) => {
      const opt = document.createElement("option");
      opt.value = a.name;
      const r = records[a.name];
      const tagged = r && r.slot !== "unknown";
      opt.textContent = (tagged ? "✓ " : "· ") + a.name + (a.duration != null ? "  (" + a.duration.toFixed(1) + "s)" : "");
      opt.style.color = tagged ? "var(--ok)" : "var(--fg)";
      sel.appendChild(opt);
    });
    if (current) sel.value = current;
    renderRecords();
    renderStats();
  }
  function renderRecords() {
    const body = $("rec-body");
    body.innerHTML = "";
    Object.keys(records).forEach((name) => {
      const r = records[name];
      const tr = document.createElement("tr");
      const td1 = document.createElement("td");
      td1.textContent = name;
      td1.style.cursor = "pointer";
      td1.title = "点击跳到该动画";
      td1.onclick = () => { current = name; renderList(); play(name, true); };
      const td2 = document.createElement("td");
      td2.textContent = r.slot || "unknown";
      td2.className = r.slot && r.slot !== "unknown" ? "tag-mapped" : "tag-unknown";
      const td3 = document.createElement("td");
      td3.textContent = r.note || "";
      tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3);
      body.appendChild(tr);
    });
  }

  function play(name, loop) {
    if (!player || !player.animationState) return;
    player.animationState.setAnimation(0, name, loop !== false);
    player.speed = Number($("btn-normal").classList.contains("playing") ? 1 : player.speed);
    if (player.paused) player.paused = false;
    current = name;
    $("sel").value = name;
    log("播放: " + name);
  }

  function applyFlip() {
    if (player && player.skeleton) player.skeleton.scaleX = $("chk-flip").checked ? -1 : 1;
  }
  function setSpeed(mult, btn) {
    if (player) player.speed = mult;
    ["btn-slow", "btn-normal", "btn-fast"].forEach((id) => $(id).classList.remove("playing"));
    btn.classList.add("playing");
    log("速度 " + mult + "×");
  }

  function init() {
    const stage = $("stage");
    try {
      player = new window.spine.SpinePlayer(stage, {
        binaryUrl: "./assets/spine/314701_wmz_s_room.skel",
        atlasUrl: "./assets/spine/314701_wmz_s.atlas",
        alpha: true,
        backgroundColor: "00000000",
        showControls: false,
        showLoading: false,
        premultipliedAlpha: true,
        defaultMix: 0.15,
        success: (p) => {
          // 枚举全部动画（skeleton.data.animations）
          animations = (p.skeleton.data.animations || []).map((a) => ({ name: a.name, duration: a.duration }));
          animations.sort((a, b) => a.name.localeCompare(b.name, "zh"));
          renderList();
          if (animations.length) play(animations[0].name, true);
          log("加载完成，共 " + animations.length + " 个动画。逐个播放并标注语义。");
        },
      });
    } catch (e) {
      log("加载失败: " + (e && e.message ? e.message : e));
    }
  }

  // ── 事件绑定 ──
  $("sel").addEventListener("change", (e) => play(e.target.value, $("chk-loop").checked));
  $("btn-play").addEventListener("click", () => { if (player) player.paused = false; });
  $("btn-pause").addEventListener("click", () => { if (player) player.paused = true; });
  $("chk-loop").addEventListener("change", (e) => { if (current) play(current, e.target.checked); });
  $("chk-flip").addEventListener("change", applyFlip);
  $("btn-slow").addEventListener("click", (e) => setSpeed(0.5, e.target));
  $("btn-normal").addEventListener("click", (e) => setSpeed(1, e.target));
  $("btn-fast").addEventListener("click", (e) => setSpeed(2, e.target));
  $("slot").addEventListener("change", (e) => { currentSlot = e.target.value; });

  $("btn-record").addEventListener("click", () => {
    if (!current) { log("先选择一个动画"); return; }
    const anim = animations.find((a) => a.name === current);
    records[current] = {
      slot: currentSlot,
      note: $("note").value.trim() || "",
      duration: anim ? anim.duration : null,
    };
    saveRecords();
    renderList();
    log("已记录: " + current + " → " + currentSlot);
  });

  $("btn-export").addEventListener("click", () => {
    const map = {};
    Object.keys(records).forEach((k) => { map[k] = records[k]; });
    const blob = new Blob([JSON.stringify(map, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "animation_map.json";
    a.click();
    URL.revokeObjectURL(a.href);
    log("已导出 animation_map.json（覆盖到 frontend/assets/spine/ 即可）");
  });
  $("btn-copy").addEventListener("click", () => {
    const map = {};
    Object.keys(records).forEach((k) => { map[k] = records[k]; });
    navigator.clipboard.writeText(JSON.stringify(map, null, 2))
      .then(() => log("已复制 JSON 到剪贴板"))
      .catch(() => log("复制失败，请用导出按钮"));
  });
  $("btn-clear").addEventListener("click", () => {
    if (!window.confirm("清空全部标注记录？")) return;
    records = {};
    saveRecords();
    renderList();
    log("已清空标注");
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      // 输入/选择控件内不劫持方向键（备注输入框移动光标、下拉展开等）
      if (e.target && e.target.matches && e.target.matches("input, select, textarea")) return;
      e.preventDefault();
      const idx = animations.findIndex((a) => a.name === current);
      const next = e.key === "ArrowDown" ? idx + 1 : idx - 1;
      if (next >= 0 && next < animations.length) play(animations[next].name, $("chk-loop").checked);
    }
    if (e.key === "Enter" && !e.target.tagName.match(/INPUT|SELECT/)) {
      $("btn-record").click();
    }
  });

  window.addEventListener("DOMContentLoaded", init);
})();
