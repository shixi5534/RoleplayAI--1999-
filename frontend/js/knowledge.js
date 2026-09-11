/*
 * knowledge.js —— 知识库管理弹层（顶栏「知识库」按钮驱动）。
 * 能力：命名空间切换 / 文档列表(按 doc_id 聚合) / 删除 / 块预览 / 拖拽上传(进度条) / 检索测试(评分+高亮)。
 *
 * 与后端约定（src/roleplay/api/knowledge.py）：
 *   GET    /api/knowledge/stats             → {counts: {ns: n}}
 *   GET    /api/knowledge/documents?ns=     → {namespace, documents:[{doc_id,title,chunk_count,size,created_at,format}]}
 *   DELETE /api/knowledge/documents/{doc_id}?ns=
 *   GET    /api/knowledge/chunks?ns=&doc_id= → {doc_id,namespace,title,chunks:[{text,meta,ts}]}
 *   POST   /api/knowledge/upload             multipart: file + ns + character_id → {doc_id,title,format,stored,namespace}
 *   GET    /api/knowledge/search?q=&ns=&top_k=&hybrid= → {query,results:[{text,score,namespace,meta}]}
 *
 * 设计约束：CSP script-src 'self' → 本文件为外置 JS；样式内嵌于 index.html <style>。
 * 全部符号挂在 window.KnowledgePanel，避免与 chat.js / live2d.js 冲突。
 */
(function () {
  "use strict";

  const API_BASE = ""; // 同源；与 chat.js 保持一致
  const KB_API = API_BASE + "/api/knowledge";
  const ACCEPT_EXT = [".md", ".markdown", ".txt", ".html", ".htm", ".json", ".csv", ".pdf", ".docx"];
  const EXT_BADGE = {
    md: "MD", markdown: "MD", txt: "TXT", html: "HTML", htm: "HTML",
    json: "JSON", csv: "CSV", pdf: "PDF", docx: "DOCX",
  };
  const NS_PRETTY = {
    docs: "通用资料",
    persona: "人设",
    events: "长期记忆",
    web: "联网",
    episodic: "情节片段",
  };

  // ── DOM ──
  let els = {};
  const state = { ns: "docs", uploading: false };
  // 异步请求顺序令牌（F7）：快速切换命名空间/连点检索时，慢请求晚到不得覆盖新结果
  let reqSeq = 0;
  // 弹层关闭 200ms 延迟隐藏的定时器（F9）：重开时须先取消，防止旧定时器藏掉新弹层
  let panelCloseTimer = null;
  let chunksCloseTimer = null;

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    const div = document.createElement("div");
    div.textContent = s == null ? "" : String(s);
    return div.innerHTML;
  }

  function fmtSize(n) {
    if (!n) return "0 B";
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    return (n / 1024 / 1024).toFixed(2) + " MB";
  }

  function fmtTime(ts) {
    if (!ts) return "—";
    const d = new Date(ts * 1000);
    const p = (x) => String(x).padStart(2, "0");
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }

  function toast(icon, label, value) {
    const t = document.createElement("div");
    t.className = "toast";
    const i = document.createElement("span");
    i.className = "t-icon";
    i.textContent = icon;
    const l = document.createElement("span");
    l.textContent = label;
    t.appendChild(i);
    t.appendChild(l);
    if (value != null) {
      const v = document.createElement("span");
      v.className = "t-val";
      v.textContent = value;
      t.appendChild(v);
    }
    const wrap = $("toasts");
    if (wrap) {
      wrap.appendChild(t);
      setTimeout(() => t.remove(), 1900);
    }
  }

  async function apiJSON(url, opts) {
    const resp = await fetch(url, opts);
    if (!resp.ok) {
      let detail = "HTTP " + resp.status;
      try {
        const j = await resp.json();
        if (j && j.detail) detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
      } catch (_) { /* ignore */ }
      throw new Error(detail);
    }
    return resp.json();
  }

  // ── 弹窗开关（复刻 chat.js 的 modal-backdrop 模式）──
  function openPanel() {
    if (panelCloseTimer) { clearTimeout(panelCloseTimer); panelCloseTimer = null; }
    els.backdrop.hidden = false;
    void els.backdrop.offsetWidth;
    els.backdrop.classList.add("open");
    refreshAll();
  }
  function closePanel() {
    els.backdrop.classList.remove("open");
    if (panelCloseTimer) clearTimeout(panelCloseTimer);
    panelCloseTimer = setTimeout(() => { panelCloseTimer = null; els.backdrop.hidden = true; }, 200);
  }
  function togglePanel() {
    if (els.backdrop.classList.contains("open")) closePanel();
    else openPanel();
  }
  function openChunksPanel(doc) {
    if (chunksCloseTimer) { clearTimeout(chunksCloseTimer); chunksCloseTimer = null; }
    els.chunksTitle.textContent = doc ? doc.title : "知识块预览";
    // textContent 天然防注入，无需 esc()（esc 会把 & 等显示成 &amp; 字面实体）
    els.chunksSub.textContent = doc ? `${doc.doc_id} · ${doc.chunk_count} 块` : "";
    els.chunksList.innerHTML = "";
    els.chunksBackdrop.hidden = false;
    void els.chunksBackdrop.offsetWidth;
    els.chunksBackdrop.classList.add("open");
  }
  function closeChunksPanel() {
    els.chunksBackdrop.classList.remove("open");
    if (chunksCloseTimer) clearTimeout(chunksCloseTimer);
    chunksCloseTimer = setTimeout(() => { chunksCloseTimer = null; els.chunksBackdrop.hidden = true; }, 200);
  }

  // ── 命名空间 ──
  async function loadNamespaces() {
    try {
      const data = await apiJSON(KB_API + "/stats");
      const counts = data.counts || {};
      const sel = els.nsSel;
      const prev = state.ns;
      sel.innerHTML = "";
      const namespaces = Object.keys(counts);
      if (!namespaces.length) namespaces.push("docs");
      namespaces.sort();
      namespaces.forEach((ns) => {
        const opt = document.createElement("option");
        opt.value = ns;
        opt.textContent = (NS_PRETTY[ns] ? NS_PRETTY[ns] + " · " : "") + ns + "（" + counts[ns] + "）";
        sel.appendChild(opt);
      });
      // 恢复上次选择（若存在）
      state.ns = namespaces.indexOf(prev) >= 0 ? prev : "docs";
      sel.value = state.ns;
    } catch (e) {
      els.count.textContent = "";
      toast("⚠️", "命名空间加载失败", e.message);
    }
  }

  // ── 文档列表 ──
  async function loadDocuments() {
    const mySeq = ++reqSeq;
    try {
      const data = await apiJSON(KB_API + "/documents?ns=" + encodeURIComponent(state.ns));
      if (mySeq !== reqSeq) return; // 期间已发起更新的请求，丢弃本次结果
      renderDocList(data.documents || []);
    } catch (e) {
      if (mySeq !== reqSeq) return;
      renderDocList([]);
      els.count.textContent = "";
      toast("⚠️", "文档列表加载失败", e.message);
    }
  }

  function renderDocList(docs) {
    const list = els.docList;
    list.innerHTML = "";
    els.count.textContent = `共 ${docs.length} 篇`;
    if (!docs.length) {
      const empty = document.createElement("div");
      empty.className = "kb-doc-empty";
      empty.textContent = "暂无文档。拖拽文件到上方区域，或点击上传。";
      list.appendChild(empty);
      return;
    }
    docs.forEach((doc) => {
      const row = document.createElement("div");
      row.className = "kb-doc-row";
      const badge = EXT_BADGE[(doc.format || "").toLowerCase()] || "DOC";
      const name = document.createElement("span");
      name.className = "kb-doc-name";
      name.textContent = doc.title || doc.doc_id;
      const meta = document.createElement("span");
      meta.className = "kb-doc-meta";
      meta.textContent = `${badge} · ${doc.chunk_count} 块 · ${fmtSize(doc.size)} · ${fmtTime(doc.created_at)}`;
      const actions = document.createElement("span");
      actions.className = "kb-doc-actions";

      const btnPreview = document.createElement("button");
      btnPreview.type = "button";
      btnPreview.textContent = "块预览";
      btnPreview.addEventListener("click", () => openChunksForDoc(doc));
      const btnDel = document.createElement("button");
      btnDel.type = "button";
      btnDel.className = "kb-del-btn";
      btnDel.textContent = "删除";
      btnDel.addEventListener("click", () => deleteDoc(doc));

      actions.appendChild(btnPreview);
      actions.appendChild(btnDel);
      row.appendChild(name);
      row.appendChild(meta);
      row.appendChild(actions);
      list.appendChild(row);
    });
  }

  async function openChunksForDoc(doc) {
    openChunksPanel(doc);
    const mySeq = ++reqSeq;
    try {
      const data = await apiJSON(
        KB_API + "/chunks?ns=" + encodeURIComponent(state.ns) + "&doc_id=" + encodeURIComponent(doc.doc_id)
      );
      if (mySeq !== reqSeq) return;
      renderChunks(data.chunks || []);
    } catch (e) {
      if (mySeq !== reqSeq) return;
      els.chunksList.innerHTML = "";
      const empty = document.createElement("div");
      empty.className = "kb-doc-empty";
      empty.textContent = "块加载失败：" + e.message;
      els.chunksList.appendChild(empty);
    }
  }

  function renderChunks(chunks) {
    const list = els.chunksList;
    list.innerHTML = "";
    if (!chunks.length) {
      const empty = document.createElement("div");
      empty.className = "kb-doc-empty";
      empty.textContent = "该文档没有可预览的知识块。";
      list.appendChild(empty);
      return;
    }
    chunks.forEach((c, i) => {
      const card = document.createElement("div");
      card.className = "kb-chunk-card";
      const text = document.createElement("div");
      text.className = "kb-chunk-text";
      text.textContent = c.text || "";
      const meta = document.createElement("div");
      meta.className = "kb-chunk-meta";
      const m = c.meta || {};
      const pairs = [
        ["#", String(i + 1)],
        ["section", m.section],
        ["format", m.format],
        ["source", m.source],
        ["id", m.id],
      ];
      pairs.forEach(([k, v]) => {
        if (v == null || v === "") return;
        const span = document.createElement("span");
        span.textContent = `${k}: ${v}`;
        meta.appendChild(span);
      });
      card.appendChild(text);
      card.appendChild(meta);
      list.appendChild(card);
    });
  }

  async function deleteDoc(doc) {
    const title = doc.doc_id === "legacy" ? "历史数据（无 doc_id 的存量条目）" : doc.title;
    if (!window.confirm(`确定删除「${title}」吗？将移除 ${doc.chunk_count} 个知识块，不可恢复。`)) return;
    try {
      const r = await apiJSON(
        KB_API + "/documents/" + encodeURIComponent(doc.doc_id) + "?ns=" + encodeURIComponent(state.ns),
        { method: "DELETE" }
      );
      toast("🗑️", "已删除", `${r.removed} 块`);
      loadDocuments();
      loadNamespaces();
    } catch (e) {
      toast("⚠️", "删除失败", e.message);
    }
  }

  // ── 拖拽上传 ──
  function setUploadMsg(text, kind) {
    const el = els.uploadMsg;
    el.textContent = text || "";
    el.className = "kb-upload-msg" + (kind ? " " + kind : "");
  }

  function validExt(name) {
    const dot = name.lastIndexOf(".");
    if (dot < 0) return false;
    return ACCEPT_EXT.indexOf(name.slice(dot).toLowerCase()) >= 0;
  }

  async function uploadFile(file) {
    state.uploading = true;
    els.uploadProgress.hidden = false;
    els.uploadName.textContent = file.name + "（" + fmtSize(file.size) + "）";
    els.uploadFill.style.width = "0%";
    setUploadMsg("", "");

    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("ns", state.ns);
      const stored = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", KB_API + "/upload");
        xhr.upload.onprogress = (ev) => {
          if (ev.lengthComputable) {
            els.uploadFill.style.width = Math.round((ev.loaded / ev.total) * 100) + "%";
          }
        };
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              resolve(JSON.parse(xhr.responseText));
            } catch (_) {
              reject(new Error("响应解析失败"));
            }
          } else {
            let detail = "HTTP " + xhr.status;
            try {
              const j = JSON.parse(xhr.responseText);
              if (j && j.detail) detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
            } catch (_) { /* ignore */ }
            reject(new Error(detail));
          }
        };
        xhr.onerror = () => reject(new Error("网络错误"));
        xhr.send(fd);
      });
      els.uploadFill.style.width = "100%";
      setUploadMsg(`「${file.name}」导入完成：${stored.stored} 块`, "ok");
      loadDocuments();
      loadNamespaces();
    } catch (e) {
      els.uploadFill.style.width = "0%";
      setUploadMsg("导入失败：" + e.message, "err");
    } finally {
      state.uploading = false;
    }
  }

  /**
   * 多文件上传（F5）：串行队列逐个 await。
   * 旧实现 `list.forEach(uploadFile)` 是同步发起，第一个文件的
   * `state.uploading=true` 会让其余文件在锁处静默 return——界面宣称支持多选，
   * 实际只传第一个且无任何提示。
   */
  async function handleFiles(files) {
    const list = Array.prototype.slice.call(files || []);
    if (!list.length) return;
    const bad = list.filter((f) => !validExt(f.name));
    if (bad.length) {
      setUploadMsg("不支持的文件类型：" + bad.map((f) => f.name).join("、"), "err");
      return;
    }
    // 串行上传；每个文件完成后短暂展示进度，便于多文件时看到逐文件结果
    for (let i = 0; i < list.length; i++) {
      await uploadFile(list[i]);
    }
    if (list.length > 1) setUploadMsg(`已导入 ${list.length} 个文件`, "ok");
  }

  // ── 检索测试 ──
  function scoreClass(s) {
    if (s >= 0.3) return "";
    if (s >= 0.15) return "mid";
    return "low";
  }

  function highlight(text, query) {
    if (!query) return esc(text);
    const q = query.trim();
    if (!q) return esc(text);
    const parts = q.split(/\s+/).filter(Boolean);
    let re;
    try {
      re = new RegExp("(" + parts.map((p) => p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")", "gi");
    } catch (_) {
      return esc(text);
    }
    return esc(text).replace(re, "<mark>$1</mark>");
  }

  async function doSearch() {
    const q = els.searchQ.value.trim();
    if (!q) {
      els.searchResults.innerHTML = "";
      return;
    }
    const topK = els.searchK.value || "3";
    const mySeq = ++reqSeq;
    try {
      const data = await apiJSON(
        KB_API + "/search?q=" + encodeURIComponent(q) +
        "&ns=" + encodeURIComponent(state.ns) +
        "&top_k=" + topK + "&hybrid=true"
      );
      if (mySeq !== reqSeq) return; // 快速连续检索：只渲染最后一次
      renderSearchResults(data.results || [], q);
    } catch (e) {
      if (mySeq !== reqSeq) return;
      els.searchResults.innerHTML = "";
      const card = document.createElement("div");
      card.className = "kb-sr-card";
      card.textContent = "检索失败：" + e.message;
      els.searchResults.appendChild(card);
    }
  }

  function renderSearchResults(results, q) {
    const wrap = els.searchResults;
    wrap.innerHTML = "";
    if (!results.length) {
      const card = document.createElement("div");
      card.className = "kb-sr-card";
      card.textContent = "未命中任何知识块。";
      wrap.appendChild(card);
      return;
    }
    results.forEach((r) => {
      const card = document.createElement("div");
      card.className = "kb-sr-card";
      const head = document.createElement("div");
      head.className = "kb-sr-head";
      const score = document.createElement("span");
      score.className = "kb-sr-score " + scoreClass(r.score || 0);
      score.textContent = (r.score || 0).toFixed(4);
      const ns = document.createElement("span");
      ns.className = "kb-sr-ns";
      ns.textContent = r.namespace || "";
      const m = r.meta || {};
      const src = document.createElement("span");
      src.textContent = m.title || m.section || "";
      head.appendChild(score);
      head.appendChild(src);
      head.appendChild(ns);
      const text = document.createElement("div");
      text.className = "kb-sr-text";
      text.innerHTML = highlight(r.text || "", q);
      card.appendChild(head);
      card.appendChild(text);
      wrap.appendChild(card);
    });
  }

  // ── 事件绑定 ──
  function bindEvents() {
    const btn = $("btn-knowledge");
    if (btn) btn.addEventListener("click", togglePanel);

    els.close.addEventListener("click", closePanel);
    els.backdrop.addEventListener("click", (e) => {
      if (e.target === els.backdrop) closePanel();
    });
    els.chunksClose.addEventListener("click", closeChunksPanel);
    els.chunksBackdrop.addEventListener("click", (e) => {
      if (e.target === els.chunksBackdrop) closeChunksPanel();
    });

    els.refresh.addEventListener("click", refreshAll);
    els.nsSel.addEventListener("change", () => {
      state.ns = els.nsSel.value;
      els.searchResults.innerHTML = "";
      loadDocuments();
    });

    // 拖拽上传
    const drop = els.uploadDrop;
    ["dragenter", "dragover"].forEach((ev) => {
      drop.addEventListener(ev, (e) => {
        e.preventDefault();
        drop.classList.add("dragover");
      });
    });
    ["dragleave", "drop"].forEach((ev) => {
      drop.addEventListener(ev, (e) => {
        e.preventDefault();
        drop.classList.remove("dragover");
      });
    });
    drop.addEventListener("drop", (e) => {
      handleFiles(e.dataTransfer && e.dataTransfer.files);
    });
    drop.addEventListener("click", () => els.fileInput.click());
    els.fileInput.addEventListener("change", () => {
      handleFiles(els.fileInput.files);
      els.fileInput.value = "";
    });

    // 检索
    els.searchBtn.addEventListener("click", doSearch);
    els.searchQ.addEventListener("keydown", (e) => {
      if (e.key === "Enter") doSearch();
    });
  }

  function refreshAll() {
    loadNamespaces().then(loadDocuments);
  }

  function init() {
    els = {
      backdrop: $("kb-backdrop"),
      close: $("kb-close"),
      nsSel: $("kb-ns"),
      count: $("kb-count"),
      refresh: $("kb-refresh"),
      uploadDrop: $("kb-upload-drop"),
      fileInput: $("kb-file-input"),
      uploadProgress: $("kb-upload-progress"),
      uploadName: $("kb-upload-name"),
      uploadFill: $("kb-upload-fill"),
      uploadMsg: $("kb-upload-msg"),
      docList: $("kb-doc-list"),
      searchQ: $("kb-search-q"),
      searchK: $("kb-search-k"),
      searchBtn: $("kb-search-btn"),
      searchResults: $("kb-search-results"),
      chunksBackdrop: $("kb-chunks-backdrop"),
      chunksClose: $("kb-chunks-close"),
      chunksTitle: $("kb-chunks-title"),
      chunksSub: $("kb-chunks-sub"),
      chunksList: $("kb-chunks-list"),
    };
    if (!els.backdrop) return; // 元素缺失时静默降级
    bindEvents();

    // Esc：知识库弹窗优先于 chat.js 的 Esc 处理（捕获阶段先于冒泡阶段）
    document.addEventListener(
      "keydown",
      (e) => {
        if (e.key !== "Escape") return;
        if (els.chunksBackdrop.classList.contains("open")) {
          closeChunksPanel();
          e.stopPropagation();
          return;
        }
        if (els.backdrop.classList.contains("open")) {
          closePanel();
          e.stopPropagation();
        }
      },
      true // capture
    );
  }

  // 暴露到 window，供调试 / 其他模块复用
  window.KnowledgePanel = {
    open: openPanel,
    close: closePanel,
    toggle: togglePanel,
    refresh: refreshAll,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
