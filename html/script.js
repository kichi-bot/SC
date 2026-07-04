/* ============================================================
   SC午後対策ダッシュボード  script.js
   検索フィルタ / スクロール連動ナビ / TOPへ戻る /
   チェックリスト保存 / モバイルサイドバー
   すべてローカル完結（外部依存なし）
   ============================================================ */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    setupSearch();
    setupBackToTop();
    setupScrollSpy();
    setupSidebar();
    setupChecklists();
  }

  /* -------------------- 検索フィルタ -------------------- */
  function setupSearch() {
    var input  = document.getElementById('search');
    var clear  = document.getElementById('searchClear');
    var status = document.getElementById('searchStatus');
    if (!input) return;

    // 検索対象ユニット：カード類・テーブル行
    var units = Array.prototype.slice.call(
      document.querySelectorAll('.search-unit')
    );
    var rows  = Array.prototype.slice.call(
      document.querySelectorAll('table.filterable tbody tr')
    );

    function run() {
      var q = input.value.trim().toLowerCase();
      clear.style.display = q ? 'block' : 'none';

      if (!q) { reset(); status.textContent = ''; return; }

      var hits = 0;

      units.forEach(function (u) {
        var match = u.textContent.toLowerCase().indexOf(q) !== -1;
        u.classList.toggle('search-hidden', !match);
        u.classList.toggle('hit', match);
        if (match) hits++;
      });

      rows.forEach(function (r) {
        var match = r.textContent.toLowerCase().indexOf(q) !== -1;
        r.classList.toggle('search-hidden', !match);
        if (match) hits++;
      });

      // 章：可視ユニット/行が無ければ薄く
      document.querySelectorAll('section.chapter').forEach(function (sec) {
        var visible = sec.querySelectorAll('.search-unit:not(.search-hidden), table.filterable tbody tr:not(.search-hidden)').length;
        sec.classList.toggle('dim', visible === 0);
      });

      status.textContent = hits
        ? '「' + input.value.trim() + '」に一致：' + hits + ' 件を表示中（他は非表示）'
        : '「' + input.value.trim() + '」に一致する項目は見つかりませんでした';
    }

    function reset() {
      units.forEach(function (u) { u.classList.remove('search-hidden', 'hit'); });
      rows.forEach(function (r) { r.classList.remove('search-hidden'); });
      document.querySelectorAll('section.chapter').forEach(function (s) { s.classList.remove('dim'); });
    }

    var t;
    input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 120); });
    clear.addEventListener('click', function () { input.value = ''; run(); input.focus(); });
    // Escで解除
    input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { input.value=''; run(); } });
  }

  /* -------------------- TOPへ戻る -------------------- */
  function setupBackToTop() {
    var btn = document.getElementById('toTop');
    if (!btn) return;
    window.addEventListener('scroll', function () {
      btn.classList.toggle('show', window.scrollY > 500);
    }, { passive: true });
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* -------------------- スクロール連動ナビ -------------------- */
  function setupScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.sidebar nav a[href^="#"]'));
    if (!links.length) return;
    var map = {};
    links.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      var el = document.getElementById(id);
      if (el) map[id] = a;
    });

    var targets = Object.keys(map).map(function (id) { return document.getElementById(id); });

    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          links.forEach(function (l) { l.classList.remove('active'); });
          var a = map[en.target.id];
          if (a) a.classList.add('active');
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px', threshold: 0 });

    targets.forEach(function (t) { obs.observe(t); });

    // クリックでモバイルサイドバーを閉じる
    links.forEach(function (a) {
      a.addEventListener('click', function () { closeSidebar(); });
    });
  }

  /* -------------------- モバイルサイドバー -------------------- */
  var _sb, _bd;
  function setupSidebar() {
    _sb = document.querySelector('.sidebar');
    _bd = document.querySelector('.backdrop');
    var burger = document.querySelector('.hamburger');
    if (burger) burger.addEventListener('click', function () {
      _sb.classList.toggle('open');
      if (_bd) _bd.classList.toggle('show', _sb.classList.contains('open'));
    });
    if (_bd) _bd.addEventListener('click', closeSidebar);
  }
  function closeSidebar() {
    if (_sb) _sb.classList.remove('open');
    if (_bd) _bd.classList.remove('show');
  }

  /* -------------------- チェックリスト保存 -------------------- */
  function setupChecklists() {
    var boxes = document.querySelectorAll('.checklist input[type=checkbox][id]');
    var KEY = 'sc-pm-checklist';
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { saved = {}; }

    boxes.forEach(function (b) {
      if (saved[b.id]) b.checked = true;
      b.addEventListener('change', function () {
        saved[b.id] = b.checked;
        try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {}
      });
    });

    var resetBtn = document.getElementById('resetChecks');
    if (resetBtn) resetBtn.addEventListener('click', function () {
      boxes.forEach(function (b) { b.checked = false; });
      saved = {};
      try { localStorage.removeItem(KEY); } catch (e) {}
    });
  }
})();
