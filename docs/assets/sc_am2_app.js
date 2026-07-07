/* SC午前Ⅱ ダッシュボード（外部ライブラリ不使用） */
(function () {
  "use strict";
  var TOPICS = window.SC_AM2_TOPICS || [];
  var QS = window.SC_AM2_QUESTIONS || [];
  var LS = {
    get: function (k, d) { try { return JSON.parse(localStorage.getItem(k)) || d; } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  var PRI_NAME = { A: "最優先", B: "重要", C: "余力", D: "低頻度" };
  var PM_NAME = { high: "午後関連:高", middle: "午後関連:中", low: "午後関連:低" };

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ---------- 優先順位マップ ---------- */
  function topicCard(t) {
    var c = el("div", "card topic-card p" + t.pri);
    c.innerHTML =
      '<h3>' + esc(t.cat) + ' <span class="badge pri-' + t.pri + '">' + t.pri + '・' + PRI_NAME[t.pri] + '</span> ' +
      '<span class="badge pm-' + t.pm + '">' + PM_NAME[t.pm] + '</span></h3>' +
      '<div class="nums">出題 ' + t.count + '問(全33回) / 直近重みスコア ' + t.score + '</div>' +
      '<div class="action">' + esc(t.action) + '</div>';
    return c;
  }
  function renderTopics() {
    var ab = document.getElementById("topics-ab");
    var cd = document.getElementById("topics-cd");
    if (!ab) return;
    var sorted = TOPICS.slice().sort(function (a, b) {
      if (a.pri !== b.pri) return a.pri < b.pri ? -1 : 1;
      return b.score - a.score;
    });
    sorted.forEach(function (t) {
      (t.pri === "A" || t.pri === "B" ? ab : cd).appendChild(topicCard(t));
    });
  }

  /* ---------- タブ（戦略） ---------- */
  function initTabs() {
    document.querySelectorAll(".tabs").forEach(function (tabs) {
      var btns = tabs.querySelectorAll("button");
      btns.forEach(function (b) {
        b.addEventListener("click", function () {
          btns.forEach(function (x) { x.classList.remove("active"); });
          b.classList.add("active");
          var root = tabs.parentElement;
          root.querySelectorAll(".tab-panel").forEach(function (p) {
            p.classList.toggle("active", p.id === b.dataset.panel);
          });
        });
      });
    });
  }

  /* ---------- チェックリスト（localStorage保存） ---------- */
  function initChecklist() {
    var saved = LS.get("sc_am2_check", {});
    document.querySelectorAll(".checklist input[type=checkbox]").forEach(function (cb, i) {
      var key = cb.dataset.key || String(i);
      cb.checked = !!saved[key];
      cb.addEventListener("change", function () {
        saved[key] = cb.checked;
        LS.set("sc_am2_check", saved);
      });
    });
  }

  /* ---------- 暗記カード：検索・カテゴリ絞り込み・覚えた ---------- */
  function initFlashcards() {
    var box = document.getElementById("fcard-list");
    if (!box) return;
    var cards = Array.prototype.slice.call(box.querySelectorAll("details"));
    var search = document.getElementById("fcard-search");
    var catSel = document.getElementById("fcard-cat");
    var hideLearned = document.getElementById("fcard-hide-learned");
    var counter = document.getElementById("fcard-count");
    var learned = LS.get("sc_am2_learned", {});

    // カテゴリの選択肢を生成
    var cats = [];
    cards.forEach(function (c) {
      if (cats.indexOf(c.dataset.cat) < 0) cats.push(c.dataset.cat);
    });
    cats.forEach(function (c) {
      var o = document.createElement("option");
      o.value = c; o.textContent = c;
      catSel.appendChild(o);
    });

    // 覚えたボタン
    cards.forEach(function (c) {
      var term = c.dataset.term;
      var btn = el("button", "learned-toggle", "覚えた");
      btn.type = "button";
      if (learned[term]) c.classList.add("learned");
      btn.addEventListener("click", function (ev) {
        ev.preventDefault(); ev.stopPropagation();
        var on = c.classList.toggle("learned");
        learned[term] = on;
        LS.set("sc_am2_learned", learned);
        apply();
      });
      c.querySelector("summary").appendChild(btn);
    });

    function apply() {
      var q = (search.value || "").toLowerCase();
      var cat = catSel.value;
      var shown = 0;
      cards.forEach(function (c) {
        var hit = (!cat || c.dataset.cat === cat) &&
          (!q || (c.textContent || "").toLowerCase().indexOf(q) >= 0) &&
          !(hideLearned.checked && c.classList.contains("learned"));
        c.style.display = hit ? "" : "none";
        if (hit) shown++;
      });
      counter.textContent = shown + " / " + cards.length + " 枚を表示";
    }
    search.addEventListener("input", apply);
    catSel.addEventListener("change", apply);
    hideLearned.addEventListener("change", apply);
    apply();
  }

  /* ---------- 問題一覧 ---------- */
  var qShown = 0, qFiltered = [], STEP = 100;
  function qMatch(r, q, cat, pri) {
    if (cat !== "" && r[4] !== +cat) return false;
    if (pri && r[7] !== pri) return false;
    if (q) {
      var hay = (r[0] + r[1] + "問" + r[2] + r[5] + r[6] + TOPICS[r[4]].cat).toLowerCase();
      if (hay.indexOf(q) < 0) return false;
    }
    return true;
  }
  function qItem(r) {
    var t = TOPICS[r[4]];
    var pmFull = { h: "high", m: "middle", l: "low" }[r[8]];
    var d = el("div", "q-item");
    d.innerHTML =
      '<div class="meta">' +
      '<b>' + r[0] + '年' + r[1] + ' 問' + r[2] + '</b>' +
      '<span>正解:' + esc(r[3] || "-") + '</span>' +
      '<span class="badge pri-' + r[7] + '">' + r[7] + '</span>' +
      '<span class="badge pm-' + pmFull + '">' + PM_NAME[pmFull] + '</span>' +
      '<span>' + esc(t.cat) + '</span>' +
      '</div>' +
      '<p class="theme">' + esc(r[6]) + '…</p>' +
      '<span class="sub">小分類/キーワード:' + esc(r[5]) + '</span>' +
      (t.trap ? '<div class="muted">ひっかけ傾向:' + esc(t.trap) + '</div>' : '');
    return d;
  }
  function renderQuestions(reset) {
    var list = document.getElementById("q-list");
    var note = document.getElementById("q-count");
    var more = document.getElementById("q-more");
    if (reset) { list.innerHTML = ""; qShown = 0; }
    var frag = document.createDocumentFragment();
    var end = Math.min(qShown + STEP, qFiltered.length);
    for (var i = qShown; i < end; i++) frag.appendChild(qItem(qFiltered[i]));
    qShown = end;
    list.appendChild(frag);
    note.textContent = "該当 " + qFiltered.length + " 問中 " + qShown + " 問を表示(全" + QS.length + "問・新しい回から)";
    more.style.display = qShown < qFiltered.length ? "block" : "none";
  }
  function initQuestions() {
    var list = document.getElementById("q-list");
    if (!list) return;
    var search = document.getElementById("q-search");
    var catSel = document.getElementById("q-cat");
    var priSel = document.getElementById("q-pri");
    TOPICS.forEach(function (t, i) {
      var o = document.createElement("option");
      o.value = i; o.textContent = t.cat;
      catSel.appendChild(o);
    });
    function apply() {
      var q = (search.value || "").toLowerCase();
      qFiltered = QS.filter(function (r) { return qMatch(r, q, catSel.value, priSel.value); });
      renderQuestions(true);
    }
    search.addEventListener("input", apply);
    catSel.addEventListener("change", apply);
    priSel.addEventListener("change", apply);
    document.getElementById("q-more").addEventListener("click", function () { renderQuestions(false); });
    apply();
  }

  /* ---------- ナビ・トップへ戻る・最後のセクション ---------- */
  function initNav() {
    var links = document.querySelectorAll(".nav a");
    links.forEach(function (a) {
      a.addEventListener("click", function () {
        LS.set("sc_am2_last_section", a.getAttribute("href"));
      });
    });
    var toTop = document.getElementById("toTop");
    window.addEventListener("scroll", function () {
      toTop.classList.toggle("show", window.scrollY > 600);
      // 現在地ハイライト
      var cur = null;
      document.querySelectorAll("section[id]").forEach(function (s) {
        if (s.getBoundingClientRect().top < 80) cur = "#" + s.id;
      });
      links.forEach(function (a) {
        a.classList.toggle("active", a.getAttribute("href") === cur);
      });
    }, { passive: true });
    toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

    // 前回開いていたセクションへのショートカット表示
    var last = LS.get("sc_am2_last_section", null);
    var lastBox = document.getElementById("last-section");
    if (last && lastBox && document.querySelector(last)) {
      var name = document.querySelector('.nav a[href="' + last + '"]');
      lastBox.innerHTML = '前回の続き:<a href="' + last + '">' + (name ? esc(name.textContent) : last) + ' へ移動</a>';
      lastBox.style.display = "block";
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderTopics();
    initTabs();
    initChecklist();
    initFlashcards();
    initQuestions();
    initNav();
    var d = document.getElementById("updated");
    if (d && !d.textContent) d.textContent = "2026-07-06";
  });
})();
