/* SC午前Ⅱ ダッシュボード（外部ライブラリ不使用） */
(function () {
  "use strict";
  var TOPICS = window.SC_AM2_TOPICS || [];
  var QS = window.SC_AM2_QUESTIONS || [];
  var PROGRESS = window.SC_AM2_PROGRESS || null;
  var FOCUS_PROGRESS = window.SC_FOCUS_TODO_PROGRESS || null;
  var PM_PROGRESS = window.SC_PM_PROGRESS || null;
  var ANKI_PROGRESS = window.SC_ANKI_PROGRESS || null;
  var MAP_MANUAL_KEY = "sc_am2_exam_map_manual";
  var FALLBACK_STORAGE_KEY = "sc_am2_window_storage";
  var PROGRESS_DB_NAME = "sc-study-progress";
  var PROGRESS_DB_STORE = "progress";
  function readFallbackStorage() {
    try {
      var value = JSON.parse(window.name || "{}");
      return value && typeof value === "object" ? value : {};
    } catch (e) {
      return {};
    }
  }
  function writeFallbackStorage(k, v) {
    try {
      var storage = readFallbackStorage();
      storage[FALLBACK_STORAGE_KEY] = storage[FALLBACK_STORAGE_KEY] || {};
      storage[FALLBACK_STORAGE_KEY][k] = v;
      window.name = JSON.stringify(storage);
      return true;
    } catch (e) {
      return false;
    }
  }
  var LS = {
    get: function (k, d) {
      try {
        var raw = localStorage.getItem(k);
        if (raw !== null) return JSON.parse(raw) || d;
      } catch (e) {}
      var fallback = readFallbackStorage()[FALLBACK_STORAGE_KEY];
      return fallback && Object.prototype.hasOwnProperty.call(fallback, k) ? fallback[k] : d;
    },
    set: function (k, v) {
      var serialized = JSON.stringify(v);
      try {
        localStorage.setItem(k, serialized);
        if (localStorage.getItem(k) === serialized) return;
      } catch (e) {}
      writeFallbackStorage(k, v);
    }
  };

  function openProgressDb() {
    return new Promise(function (resolve, reject) {
      if (!window.indexedDB) {
        reject(new Error("IndexedDBを利用できません"));
        return;
      }
      var request = window.indexedDB.open(PROGRESS_DB_NAME, 1);
      request.onupgradeneeded = function () {
        if (!request.result.objectStoreNames.contains(PROGRESS_DB_STORE)) {
          request.result.createObjectStore(PROGRESS_DB_STORE);
        }
      };
      request.onsuccess = function () { resolve(request.result); };
      request.onerror = function () { reject(request.error || new Error("保存領域を開けません")); };
    });
  }

  function writeProgressDb(key, value) {
    return openProgressDb().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(PROGRESS_DB_STORE, "readwrite");
        tx.objectStore(PROGRESS_DB_STORE).put(value, key);
        tx.oncomplete = function () { db.close(); resolve(); };
        tx.onerror = function () { db.close(); reject(tx.error || new Error("保存できません")); };
      });
    });
  }

  function readProgressDb(key) {
    return openProgressDb().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(PROGRESS_DB_STORE, "readonly");
        var request = tx.objectStore(PROGRESS_DB_STORE).get(key);
        request.onsuccess = function () { resolve(request.result); };
        request.onerror = function () { reject(request.error || new Error("読込できません")); };
        tx.oncomplete = function () { db.close(); };
      });
    });
  }

  function sanitizeManualMap(value) {
    var result = {};
    if (!value || typeof value !== "object" || Array.isArray(value)) return result;
    Object.keys(value).forEach(function (key) {
      if (/^(am2|pm):/.test(key) && typeof value[key] === "boolean") result[key] = value[key];
    });
    return result;
  }

  function publishedManualMap() {
    return sanitizeManualMap(PM_PROGRESS && PM_PROGRESS.manualMap);
  }

  function currentManualMap() {
    var combined = publishedManualMap();
    var local = sanitizeManualMap(LS.get(MAP_MANUAL_KEY, {}));
    Object.keys(local).forEach(function (key) { combined[key] = local[key]; });
    return combined;
  }

  function persistManualMap(value) {
    var clean = sanitizeManualMap(value);
    LS.set(MAP_MANUAL_KEY, clean);
    setMapSaveStatus("ブラウザに保存しました");
    writeProgressDb(MAP_MANUAL_KEY, clean).then(function () {
      setMapSaveStatus("ブラウザに二重保存しました");
    }).catch(function () {
      setMapSaveStatus("ブラウザ保存済み。念のためJSONも保存してください");
    });
  }
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

  /* ---------- 過去問道場の進捗 ---------- */
  function progressMetric(label, value, note) {
    var card = el("div", "card");
    var labelNode = el("div", "label");
    labelNode.textContent = label;
    var valueNode = el("div", "big");
    valueNode.textContent = value;
    var noteNode = el("p", "muted");
    noteNode.textContent = note;
    card.appendChild(labelNode);
    card.appendChild(valueNode);
    card.appendChild(noteNode);
    return card;
  }

  function formatMinutes(minutes) {
    var value = Math.max(0, Number(minutes) || 0);
    var hours = Math.floor(value / 60);
    var rest = value % 60;
    if (!hours) return rest + "分";
    return hours + "時間" + (rest ? rest + "分" : "");
  }

  function formatPoints(value) {
    var number = Number(value);
    return Number.isFinite(number) && Number.isInteger(number) ? String(number) : String(value);
  }

  function renderFocusProgress() {
    var summary = document.getElementById("focus-progress-summary");
    var updated = document.getElementById("focus-progress-updated");
    var taskList = document.getElementById("focus-progress-tasks");
    if (!summary || !updated || !taskList) return;
    if (!FOCUS_PROGRESS) {
      updated.textContent = "Focus To-Doの勉強時間データはまだありません。";
      return;
    }

    updated.textContent = FOCUS_PROGRESS.project + " / データ取得: " +
      String(FOCUS_PROGRESS.capturedAt).replace("T", " ").replace(/\+.*$/, "");
    summary.appendChild(progressMetric("累計", formatMinutes(FOCUS_PROGRESS.totalMinutes), "Focus To-Doの実行済み時間"));
    summary.appendChild(progressMetric("今月", formatMinutes(FOCUS_PROGRESS.monthMinutes), "当月の作業時間"));
    summary.appendChild(progressMetric("今日", formatMinutes(FOCUS_PROGRESS.todayMinutes), "本日の作業時間"));
    summary.appendChild(progressMetric("未完了タスク", FOCUS_PROGRESS.unfinishedTasks + "件", "完了 " + FOCUS_PROGRESS.completedTasks + "件"));

    (FOCUS_PROGRESS.tasks || []).forEach(function (item) {
      var li = document.createElement("li");
      var head = el("div", "progress-item-head");
      var label = document.createElement("span");
      var value = document.createElement("strong");
      label.textContent = item.name;
      value.textContent = formatMinutes(item.minutes) + "（" + item.pomodoros + "回）";
      head.appendChild(label);
      head.appendChild(value);

      var meter = el("div", "progress-meter focus-progress-meter");
      var fill = document.createElement("span");
      var ratio = FOCUS_PROGRESS.totalMinutes ? item.minutes / FOCUS_PROGRESS.totalMinutes * 100 : 0;
      fill.style.width = Math.max(0, Math.min(100, ratio)) + "%";
      meter.appendChild(fill);
      li.appendChild(head);
      li.appendChild(meter);
      taskList.appendChild(li);
    });
  }

  function pmProgressListItem(item) {
    var li = document.createElement("li");
    var head = el("div", "progress-item-head");
    var label = document.createElement("span");
    var value = document.createElement("strong");
    label.textContent = item.label;
    value.textContent = item.questions + "問 / " + formatPoints(item.score) + "点（" + item.accuracy + "%）";
    head.appendChild(label);
    head.appendChild(value);
    var meter = el("div", "progress-meter");
    meter.setAttribute("role", "progressbar");
    meter.setAttribute("aria-label", item.label + "の得点率");
    meter.setAttribute("aria-valuemin", "0");
    meter.setAttribute("aria-valuemax", "100");
    meter.setAttribute("aria-valuenow", String(item.accuracy));
    var fill = document.createElement("span");
    fill.style.width = Math.max(0, Math.min(100, item.accuracy)) + "%";
    meter.appendChild(fill);
    li.appendChild(head);
    li.appendChild(meter);
    return li;
  }

  function pmQuestionListItem(item) {
    var li = document.createElement("li");
    var head = el("div", "progress-item-head");
    var label = document.createElement("span");
    var value = document.createElement("strong");
    label.textContent = item.exam + " " + item.question + "（" + item.attempt + "回目・" + String(item.gradedAt).slice(0, 10) + "）";
    value.textContent = formatPoints(item.score) + " / " + formatPoints(item.max) + "点（" + item.accuracy + "%）";
    head.appendChild(label);
    head.appendChild(value);
    var meter = el("div", "progress-meter");
    meter.setAttribute("role", "progressbar");
    meter.setAttribute("aria-label", item.exam + " " + item.question + " " + item.attempt + "回目の得点率");
    meter.setAttribute("aria-valuemin", "0");
    meter.setAttribute("aria-valuemax", "100");
    meter.setAttribute("aria-valuenow", String(item.accuracy));
    var fill = document.createElement("span");
    fill.style.width = Math.max(0, Math.min(100, item.accuracy)) + "%";
    meter.appendChild(fill);
    li.appendChild(head);
    li.appendChild(meter);
    return li;
  }

  function renderPmProgress() {
    var summary = document.getElementById("pm-progress-summary");
    var updated = document.getElementById("pm-progress-updated");
    var dayList = document.getElementById("pm-progress-days");
    var examList = document.getElementById("pm-progress-exams");
    var questionList = document.getElementById("pm-progress-questions");
    if (!summary || !updated || !dayList || !examList) return;
    if (!PM_PROGRESS) {
      updated.textContent = "午後採点サイトの公開用集計はまだ同期されていません。";
      return;
    }
    updated.textContent = "最終採点日: " + PM_PROGRESS.lastStudyDate + " / データ取得: " +
      String(PM_PROGRESS.exportedAt).replace("T", " ").replace(/\+.*$/, "");
    summary.appendChild(progressMetric("採点済み問題", PM_PROGRESS.questions + "問", "午後問題のセルフ採点"));
    summary.appendChild(progressMetric("合計点", formatPoints(PM_PROGRESS.score) + " / " + formatPoints(PM_PROGRESS.max) + "点", "採点済み問題の配点合計"));
    summary.appendChild(progressMetric("得点率", PM_PROGRESS.accuracy + "%", "目標 70%以上"));
    (PM_PROGRESS.days || []).slice(0, 14).forEach(function (item) { dayList.appendChild(pmProgressListItem(item)); });
    (PM_PROGRESS.exams || []).forEach(function (item) { examList.appendChild(pmProgressListItem(item)); });
    if (questionList) {
      var results = PM_PROGRESS.questionResults || [];
      if (!results.length) {
        var empty = document.createElement("li");
        empty.className = "muted";
        empty.textContent = "問ごとの点数はまだ同期されていません。";
        questionList.appendChild(empty);
      }
      results.forEach(function (item) { questionList.appendChild(pmQuestionListItem(item)); });
    }
  }

  function mapGroups(map, kind) {
    var completed = new Set((map.completed || []).map(String));
    if (kind === "am2") {
      return [[1, 25]].map(function (range) {
        var values = [];
        for (var i = range[0]; i <= range[1]; i += 1) values.push(String(i));
        return { key: range[0] + "-" + range[1], label: range[0] + "–" + range[1] + "問", total: values.length, done: values.filter(function (value) { return completed.has(value); }).length };
      });
    }
    return (map.items || Array.from({ length: map.total }, function (_, index) {
      return { key: "問" + (index + 1), label: "問" + (index + 1) };
    })).map(function (item) {
      return { key: item.key, label: item.label, total: 1, done: completed.has(item.key) ? 1 : 0 };
    });
  }

  function renderExamMap(target, maps, kind) {
    if (!target) return;
    target.textContent = "";
    var manual = currentManualMap();
    if (!maps || !maps.length) {
      target.appendChild(el("p", "exam-map-empty", "まだ解いた問題が同期されていません。"));
      return;
    }
    maps.forEach(function (map) {
      var row = el("div", "exam-map-row");
      var head = el("div", "exam-map-head");
      var name = document.createElement("strong");
      var status = document.createElement("span");
      name.textContent = map.label;
      status.textContent = (map.completed || []).length + " / " + map.total + "問 自動記録";
      head.appendChild(name);
      head.appendChild(status);
      var grid = el("div", "exam-map-grid");
      mapGroups(map, kind).forEach(function (group) {
        var storageKey = kind + ":" + (map.id || map.label) + ":" + group.key;
        var automatic = group.done === group.total;
        var checked = automatic || Boolean(manual[storageKey]);
        var label = el("label", "exam-map-check" + (checked ? " done" : ""));
        var input = document.createElement("input");
        input.type = "checkbox";
        input.checked = checked;
        input.disabled = automatic;
        input.setAttribute("aria-label", map.label + " " + group.label + "を解いたとして記録");
        input.addEventListener("change", function () {
          var next = sanitizeManualMap(LS.get(MAP_MANUAL_KEY, {}));
          next[storageKey] = input.checked;
          persistManualMap(next);
          renderPastExamMaps();
        });
        var text = document.createElement("span");
        text.textContent = checked ? "✓ " + group.label : group.label + "（" + group.done + "/" + group.total + "）";
        label.appendChild(input);
        label.appendChild(text);
        grid.appendChild(label);
      });
      row.appendChild(head);
      row.appendChild(grid);
      target.appendChild(row);
    });
  }

  function renderPastExamMaps() {
    renderExamMap(document.getElementById("am2-exam-map"), PROGRESS && PROGRESS.examMaps, "am2");
    renderExamMap(document.getElementById("pm-exam-map"), PM_PROGRESS && PM_PROGRESS.questionMaps, "pm");
  }

  function setMapSaveStatus(message) {
    var status = document.getElementById("map-save-status");
    if (status) status.textContent = message;
  }

  function saveManualMap() {
    var manualMap = currentManualMap();
    persistManualMap(manualMap);
    var payload = {
      schemaVersion: 2,
      savedAt: new Date().toISOString(),
      source: "SC午前Ⅱ 傾向と対策",
      manualMap: manualMap
    };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "sc_am2_manual_progress.json";
    link.click();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    setMapSaveStatus("保存しました。JSONファイルを保管してください。");
  }

  function loadManualMap(file) {
    if (!file) return;
    file.text().then(function (text) {
      var payload = JSON.parse(text);
      if (!payload || (payload.schemaVersion !== 1 && payload.schemaVersion !== 2) || !payload.manualMap || typeof payload.manualMap !== "object") {
        throw new Error("形式が違います");
      }
      var manualMap = sanitizeManualMap(payload.manualMap);
      persistManualMap(manualMap);
      renderPastExamMaps();
      setMapSaveStatus("保存データを読み込みました。");
    }).catch(function () {
      setMapSaveStatus("読み込みに失敗しました。保存したJSONを選んでください。");
    });
  }

  function initMapStorageControls() {
    var save = document.getElementById("map-save");
    var load = document.getElementById("map-load");
    var file = document.getElementById("map-load-file");
    if (!save || !load || !file) return;
    save.addEventListener("click", saveManualMap);
    load.addEventListener("click", function () { file.click(); });
    file.addEventListener("change", function () {
      loadManualMap(file.files && file.files[0]);
      file.value = "";
    });

    readProgressDb(MAP_MANUAL_KEY).then(function (stored) {
      var restored = sanitizeManualMap(stored);
      if (!Object.keys(restored).length) return;
      var local = sanitizeManualMap(LS.get(MAP_MANUAL_KEY, {}));
      Object.keys(local).forEach(function (key) { restored[key] = local[key]; });
      LS.set(MAP_MANUAL_KEY, restored);
      renderPastExamMaps();
      setMapSaveStatus("保存済みの午後進捗を復元しました");
    }).catch(function () {});
  }

  function renderAnkiProgress() {
    var updated = document.getElementById("anki-progress-updated");
    var summary = document.getElementById("anki-summary");
    var history = document.getElementById("anki-history");
    if (!updated || !summary || !history) return;
    if (!ANKI_PROGRESS) {
      updated.textContent = "Ankiアプリの学習記録はまだ同期されていません。";
      return;
    }

    var captured = String(ANKI_PROGRESS.capturedAt || "").replace("T", " ").replace(/\+.*$/, "");
    updated.textContent = "最終学習日: " + (ANKI_PROGRESS.lastStudyDate || "記録なし") +
      " / Ankiから取得: " + captured + (ANKI_PROGRESS.readMode === "snapshot" ? "（アプリ起動中）" : "");
    summary.appendChild(progressMetric("学習日数", ANKI_PROGRESS.studyDays + "日", "Ankiの復習履歴がある日"));
    summary.appendChild(progressMetric("復習回数", ANKI_PROGRESS.reviews + "回", "学習済み " + ANKI_PROGRESS.reviewedCards + " / " + ANKI_PROGRESS.totalCards + "枚"));
    summary.appendChild(progressMetric("学習時間", formatMinutes(ANKI_PROGRESS.minutes), "Ankiが記録した回答時間の合計"));
    (ANKI_PROGRESS.days || []).slice(0, 14).forEach(function (item) {
      var line = document.createElement("li");
      var dayTime = item.minutes ? formatMinutes(item.minutes) : "1分未満";
      line.textContent = item.label + "　" + item.reviews + "回（" + item.cards + "枚） / " + dayTime;
      history.appendChild(line);
    });
  }

  function progressListItem(item) {
    var li = document.createElement("li");
    var head = el("div", "progress-item-head");
    var label = document.createElement("span");
    label.textContent = item.label;
    var value = document.createElement("strong");
    value.textContent = item.correct + "/" + item.total + "問（" + item.accuracy + "%）";
    head.appendChild(label);
    head.appendChild(value);

    var meter = el("div", "progress-meter");
    meter.setAttribute("role", "progressbar");
    meter.setAttribute("aria-label", item.label + "の正答率");
    meter.setAttribute("aria-valuemin", "0");
    meter.setAttribute("aria-valuemax", "100");
    meter.setAttribute("aria-valuenow", String(item.accuracy));
    var fill = document.createElement("span");
    fill.style.width = Math.max(0, Math.min(100, item.accuracy)) + "%";
    meter.appendChild(fill);
    li.appendChild(head);
    li.appendChild(meter);
    return li;
  }

  function renderProgress() {
    var summary = document.getElementById("progress-summary");
    var updated = document.getElementById("progress-updated");
    if (!summary || !updated) return;
    if (!PROGRESS) {
      updated.textContent = "進捗データはまだありません。";
      return;
    }

    updated.textContent = "最終学習日: " + PROGRESS.lastStudyDate + " / データ取得: " +
      String(PROGRESS.downloadedAt).replace("T", " ").replace(/\+.*$/, "");
    summary.appendChild(progressMetric("総演習", PROGRESS.total + "問", "過去問道場の全学習履歴"));
    summary.appendChild(progressMetric("正解", PROGRESS.correct + "問", "不正解 " + PROGRESS.wrong + "問"));
    summary.appendChild(progressMetric("正答率", PROGRESS.accuracy + "%", "目標 60%以上"));
    summary.appendChild(progressMetric("学習日数", PROGRESS.days.length + "日", "継続して記録された日数"));
    summary.appendChild(progressMetric("挑戦した問題", PROGRESS.uniqueQuestions + "問", "重複を除いた問題数"));

    var dayList = document.getElementById("progress-days");
    PROGRESS.days.slice(0, 14).forEach(function (item) {
      dayList.appendChild(progressListItem(item));
    });
    var categoryList = document.getElementById("progress-categories");
    PROGRESS.categories.forEach(function (item) {
      categoryList.appendChild(progressListItem(item));
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
    renderFocusProgress();
    renderAnkiProgress();
    renderPmProgress();
    renderProgress();
    renderPastExamMaps();
    initMapStorageControls();
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
