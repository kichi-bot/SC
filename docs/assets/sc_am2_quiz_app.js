/* SC午前Ⅱ 演習モード（外部ライブラリ不使用） */
(function () {
  "use strict";

  var QUESTIONS = window.SC_AM2_QUIZ_QUESTIONS || [];
  var READY_QUESTIONS = QUESTIONS.filter(function (question) { return question.available; });
  var QUESTION_STATS_KEY = "sc_am2_quiz_stats_v1";
  var CARD_STATS_KEY = "sc_am2_card_review_v1";
  var LETTER_KEYS = { "1": "ア", "2": "イ", "3": "ウ", "4": "エ", "5": "オ" };
  var root;
  var cards = [];
  var quizState = null;
  var cardState = null;

  var LS = {
    get: function (key, fallback) {
      try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch (error) { return fallback; }
    },
    set: function (key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch (error) {}
    }
  };

  function byId(id) { return document.getElementById(id); }

  function empty(node) {
    while (node && node.firstChild) node.removeChild(node.firstChild);
  }

  function node(tag, className, text) {
    var element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function addOption(select, value, text) {
    var option = document.createElement("option");
    option.value = value;
    option.textContent = text;
    select.appendChild(option);
  }

  function shuffle(items) {
    var copied = items.slice();
    for (var index = copied.length - 1; index > 0; index--) {
      var other = Math.floor(Math.random() * (index + 1));
      var saved = copied[index];
      copied[index] = copied[other];
      copied[other] = saved;
    }
    return copied;
  }

  function totalQuestionStats() {
    var saved = LS.get(QUESTION_STATS_KEY, {});
    var total = 0;
    var correct = 0;
    Object.keys(saved).forEach(function (id) {
      total += saved[id].total || 0;
      correct += saved[id].correct || 0;
    });
    return {
      total: total,
      correct: correct,
      wrong: total - correct,
      answered: Object.keys(saved).filter(function (id) { return (saved[id].total || 0) > 0; }).length
    };
  }

  function totalCardStats() {
    var saved = LS.get(CARD_STATS_KEY, {});
    var total = 0;
    var known = 0;
    Object.keys(saved).forEach(function (id) {
      total += saved[id].total || 0;
      known += saved[id].known || 0;
    });
    return {
      total: total,
      known: known,
      reviewed: Object.keys(saved).filter(function (id) { return (saved[id].total || 0) > 0; }).length
    };
  }

  function choiceText(question, answer) {
    for (var index = 0; index < question.choices.length; index++) {
      if (question.choices[index][0] === answer) return question.choices[index][1];
    }
    return "";
  }

  function isWrongQuestion(question, saved) {
    var result = saved[question.id];
    return result && (result.wrong || 0) > 0;
  }

  function questionCandidates() {
    var mode = byId("quiz-mode").value;
    var period = byId("quiz-period").value;
    var category = byId("quiz-category").value;
    var saved = LS.get(QUESTION_STATS_KEY, {});

    return READY_QUESTIONS.filter(function (question) {
      if (period && question.period !== period) return false;
      if (category && question.category !== category) return false;
      if (mode === "new" && saved[question.id]) return false;
      if (mode === "wrong" && !isWrongQuestion(question, saved)) return false;
      return true;
    });
  }

  function updatePoolNote() {
    var candidates = questionCandidates();
    var count = +byId("quiz-count").value;
    var note = byId("quiz-pool-note");
    note.textContent = candidates.length
      ? "この条件から " + Math.min(count, candidates.length) + " 問を出題します（候補 " + candidates.length + " 問）。"
      : "この条件に一致する問題はありません。出題条件を変えてください。";
  }

  function renderQuizStats() {
    var holder = byId("quiz-stats");
    var stats = totalQuestionStats();
    var accuracy = stats.total ? Math.round(stats.correct / stats.total * 100) : 0;
    var values = [
      ["総演習", stats.total + "問"],
      ["正答率", stats.total ? accuracy + "%" : "—"],
      ["間違い", stats.wrong + "問"],
      ["回答済み", stats.answered + " / " + READY_QUESTIONS.length + "問"]
    ];
    empty(holder);
    values.forEach(function (item) {
      var card = node("div", "practice-stat");
      card.appendChild(node("span", "practice-stat-label", item[0]));
      card.appendChild(node("strong", "practice-stat-value", item[1]));
      holder.appendChild(card);
    });
  }

  function renderCardStats() {
    var holder = byId("card-stats");
    var stats = totalCardStats();
    var values = [
      ["カード復習", stats.total + "回"],
      ["覚えた", stats.known + "回"],
      ["復習済み", stats.reviewed + " / " + cards.length + "枚"]
    ];
    empty(holder);
    values.forEach(function (item) {
      var card = node("div", "practice-stat");
      card.appendChild(node("span", "practice-stat-label", item[0]));
      card.appendChild(node("strong", "practice-stat-value", item[1]));
      holder.appendChild(card);
    });
  }

  function showQuizHome() {
    quizState = null;
    byId("quiz-home").hidden = false;
    byId("quiz-player").hidden = true;
    byId("quiz-result").hidden = true;
    renderQuizStats();
    updatePoolNote();
  }

  function recordQuestionAnswer(question, correct) {
    var saved = LS.get(QUESTION_STATS_KEY, {});
    var result = saved[question.id] || { total: 0, correct: 0, wrong: 0 };
    result.total += 1;
    if (correct) result.correct += 1;
    else result.wrong += 1;
    result.lastAnsweredAt = new Date().toISOString();
    saved[question.id] = result;
    LS.set(QUESTION_STATS_KEY, saved);
  }

  function startQuiz(queue) {
    var candidates = queue || questionCandidates();
    var requested = +byId("quiz-count").value;
    if (!candidates.length) {
      updatePoolNote();
      return;
    }

    quizState = {
      queue: queue || shuffle(candidates).slice(0, Math.min(requested, candidates.length)),
      index: 0,
      correct: 0,
      missed: [],
      answered: false
    };
    byId("quiz-home").hidden = true;
    byId("quiz-result").hidden = true;
    byId("quiz-player").hidden = false;
    renderQuestion();
  }

  function renderQuestion() {
    var question = quizState.queue[quizState.index];
    var questionBox = byId("quiz-question");
    var choicesBox = byId("quiz-choices");
    var progress = byId("quiz-progress");
    var feedback = byId("quiz-feedback");
    var next = byId("quiz-next");
    var number = quizState.index + 1;

    quizState.answered = false;
    empty(questionBox);
    empty(choicesBox);
    empty(feedback);
    feedback.hidden = true;
    next.hidden = true;
    progress.textContent = number + " / " + quizState.queue.length + " 問";
    byId("quiz-progress-bar").style.width = (number - 1) / quizState.queue.length * 100 + "%";

    var meta = node("div", "quiz-meta");
    meta.appendChild(node("span", "quiz-period", question.period + " 問" + question.number));
    meta.appendChild(node("span", "badge pri-" + question.priority, question.priority));
    meta.appendChild(node("span", "quiz-category", question.category));
    questionBox.appendChild(meta);
    questionBox.appendChild(node("div", "quiz-question-text", question.question));

    if (question.sourceUrl) {
      var source = node("a", "quiz-source", "図表の確認・出典ページを開く");
      source.href = question.sourceUrl;
      source.target = "_blank";
      source.rel = "noreferrer";
      questionBox.appendChild(source);
    }

    question.choices.forEach(function (choice, index) {
      var button = node("button", "quiz-choice");
      button.type = "button";
      button.dataset.answer = choice[0];
      button.setAttribute("aria-label", choice[0] + "。" + choice[1]);
      var label = node("span", "quiz-choice-label", choice[0]);
      var text = node("span", "quiz-choice-text", choice[1]);
      button.appendChild(label);
      button.appendChild(text);
      button.addEventListener("click", function () { answerQuestion(question, choice[0]); });
      choicesBox.appendChild(button);
      button.dataset.key = String(index + 1);
    });
  }

  function answerQuestion(question, selected) {
    if (!quizState || quizState.answered) return;
    quizState.answered = true;
    var correct = selected === question.answer;
    var buttons = byId("quiz-choices").querySelectorAll("button");
    var feedback = byId("quiz-feedback");
    var next = byId("quiz-next");
    var answerText = choiceText(question, question.answer);

    buttons.forEach(function (button) {
      button.disabled = true;
      if (button.dataset.answer === question.answer) button.classList.add("is-correct");
      else if (button.dataset.answer === selected) button.classList.add("is-wrong");
    });

    recordQuestionAnswer(question, correct);
    if (correct) quizState.correct += 1;
    else quizState.missed.push(question);

    empty(feedback);
    feedback.className = "quiz-feedback " + (correct ? "correct" : "wrong");
    feedback.appendChild(node("h3", "quiz-feedback-title", correct ? "正解！" : "不正解"));
    feedback.appendChild(node("p", "quiz-answer", "正解：" + question.answer + "　" + answerText));
    if (question.explanation) {
      feedback.appendChild(node("h4", "quiz-explanation-title", "解説"));
      feedback.appendChild(node("div", "quiz-explanation", question.explanation));
    }
    feedback.hidden = false;
    next.textContent = quizState.index === quizState.queue.length - 1 ? "結果を見る" : "次の問題へ";
    next.hidden = false;
    byId("quiz-progress-bar").style.width = (quizState.index + 1) / quizState.queue.length * 100 + "%";
    renderQuizStats();
  }

  function nextQuestion() {
    if (!quizState || !quizState.answered) return;
    if (quizState.index >= quizState.queue.length - 1) {
      showQuizResult();
      return;
    }
    quizState.index += 1;
    renderQuestion();
    byId("quiz-player").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function showQuizResult() {
    var result = byId("quiz-result");
    var percent = Math.round(quizState.correct / quizState.queue.length * 100);
    var missed = quizState.missed.slice();
    empty(result);
    result.appendChild(node("h3", "quiz-result-title", "演習結果"));
    result.appendChild(node("p", "quiz-result-score", quizState.correct + " / " + quizState.queue.length + " 問正解（" + percent + "%）"));

    if (missed.length) {
      result.appendChild(node("p", "muted", "間違えた問題は、今のうちにもう一度解くと定着しやすいです。"));
      var list = node("ul", "quiz-missed-list");
      missed.forEach(function (question) {
        list.appendChild(node("li", "", question.period + " 問" + question.number + " — " + question.subcategory));
      });
      result.appendChild(list);
      var retry = node("button", "primary-btn", "間違えた問題だけ解き直す");
      retry.type = "button";
      retry.addEventListener("click", function () { startQuiz(shuffle(missed)); });
      result.appendChild(retry);
    }

    var back = node("button", "secondary-btn", "出題設定に戻る");
    back.type = "button";
    back.addEventListener("click", showQuizHome);
    result.appendChild(back);
    byId("quiz-player").hidden = true;
    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function collectCards() {
    return Array.prototype.slice.call(document.querySelectorAll("#fcard-list details[data-term]")).map(function (card, index) {
      var body = card.querySelector(".body");
      return {
        id: "card-" + index + "-" + card.dataset.term,
        term: card.dataset.term,
        category: card.dataset.cat,
        answer: body ? body.textContent.trim() : ""
      };
    });
  }

  function cardCandidates() {
    var mode = byId("card-mode").value;
    var category = byId("card-category").value;
    var saved = LS.get(CARD_STATS_KEY, {});
    return cards.filter(function (card) {
      var stats = saved[card.id];
      if (category && card.category !== category) return false;
      if (mode === "new" && stats) return false;
      if (mode === "weak" && !(stats && (stats.lastRating === "uncertain" || stats.lastRating === "forgot"))) return false;
      return true;
    });
  }

  function updateCardPoolNote() {
    var candidates = cardCandidates();
    var count = +byId("card-count").value;
    byId("card-pool-note").textContent = candidates.length
      ? "この条件から " + Math.min(count, candidates.length) + " 枚を出題します（候補 " + candidates.length + " 枚）。"
      : "この条件に一致するカードはありません。";
  }

  function showCardHome() {
    cardState = null;
    byId("card-home").hidden = false;
    byId("card-player").hidden = true;
    byId("card-result").hidden = true;
    renderCardStats();
    updateCardPoolNote();
  }

  function startCards() {
    var candidates = cardCandidates();
    var requested = +byId("card-count").value;
    if (!candidates.length) {
      updateCardPoolNote();
      return;
    }
    cardState = { queue: shuffle(candidates).slice(0, Math.min(requested, candidates.length)), index: 0, rated: 0 };
    byId("card-home").hidden = true;
    byId("card-result").hidden = true;
    byId("card-player").hidden = false;
    renderCard();
  }

  function renderCard() {
    var card = cardState.queue[cardState.index];
    var answer = byId("card-answer");
    byId("card-progress").textContent = (cardState.index + 1) + " / " + cardState.queue.length + " 枚";
    byId("card-progress-bar").style.width = cardState.index / cardState.queue.length * 100 + "%";
    byId("card-category-label").textContent = card.category;
    byId("card-term").textContent = card.term;
    empty(answer);
    answer.hidden = true;
    byId("card-reveal").hidden = false;
    byId("card-ratings").hidden = true;
  }

  function revealCard() {
    if (!cardState) return;
    var card = cardState.queue[cardState.index];
    var answer = byId("card-answer");
    answer.textContent = card.answer;
    answer.hidden = false;
    byId("card-reveal").hidden = true;
    byId("card-ratings").hidden = false;
  }

  function rateCard(rating) {
    if (!cardState || byId("card-ratings").hidden) return;
    var card = cardState.queue[cardState.index];
    var saved = LS.get(CARD_STATS_KEY, {});
    var stats = saved[card.id] || { total: 0, known: 0, uncertain: 0, forgot: 0 };
    stats.total += 1;
    stats[rating] += 1;
    stats.lastRating = rating;
    stats.lastRatedAt = new Date().toISOString();
    saved[card.id] = stats;
    LS.set(CARD_STATS_KEY, saved);
    cardState.rated += 1;
    renderCardStats();

    if (cardState.index >= cardState.queue.length - 1) {
      showCardResult();
      return;
    }
    cardState.index += 1;
    renderCard();
  }

  function showCardResult() {
    var result = byId("card-result");
    empty(result);
    result.appendChild(node("h3", "quiz-result-title", "カード復習を完了しました"));
    result.appendChild(node("p", "quiz-result-score", cardState.rated + " 枚を復習しました。"));
    var again = node("button", "primary-btn", "もう一度カードを選ぶ");
    again.type = "button";
    again.addEventListener("click", showCardHome);
    result.appendChild(again);
    byId("card-player").hidden = true;
    result.hidden = false;
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function showView(name) {
    var isQuiz = name === "quiz";
    byId("quiz-view").hidden = !isQuiz;
    byId("card-view").hidden = isQuiz;
    document.querySelectorAll("[data-practice-view]").forEach(function (button) {
      var active = button.dataset.practiceView === name;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });
  }

  function setupQuestionOptions() {
    var periods = [];
    var categories = [];
    READY_QUESTIONS.forEach(function (question) {
      if (periods.indexOf(question.period) < 0) periods.push(question.period);
      if (categories.indexOf(question.category) < 0) categories.push(question.category);
    });
    periods.forEach(function (period) { addOption(byId("quiz-period"), period, period); });
    categories.sort().forEach(function (category) { addOption(byId("quiz-category"), category, category); });
  }

  function setupCardOptions() {
    var categories = [];
    cards.forEach(function (card) {
      if (categories.indexOf(card.category) < 0) categories.push(card.category);
    });
    categories.sort().forEach(function (category) { addOption(byId("card-category"), category, category); });
  }

  function renderApp() {
    root.innerHTML =
      '<div class="practice-shell">' +
        '<div class="practice-tabs" role="tablist" aria-label="演習メニュー">' +
          '<button type="button" class="active" role="tab" aria-selected="true" data-practice-view="quiz">問題を解く</button>' +
          '<button type="button" role="tab" aria-selected="false" data-practice-view="cards">カードを復習</button>' +
        '</div>' +
        '<div id="quiz-view" class="practice-view">' +
          '<div id="quiz-stats" class="practice-stats"></div>' +
          '<div id="quiz-home" class="practice-home card">' +
            '<h3>問題演習を始める</h3>' +
            '<div class="practice-config">' +
              '<label>出題方法<select id="quiz-mode"><option value="all">ランダム</option><option value="new">未回答のみ</option><option value="wrong">間違えた問題のみ</option></select></label>' +
              '<label>年度<select id="quiz-period"><option value="">すべての年度</option></select></label>' +
              '<label>分野<select id="quiz-category"><option value="">すべての分野</option></select></label>' +
              '<label>問題数<select id="quiz-count"><option value="5">5問</option><option value="10" selected>10問</option><option value="25">25問</option></select></label>' +
            '</div>' +
            '<p id="quiz-pool-note" class="count-note"></p>' +
            '<p class="quiz-data-note">全825問中、選択肢本文がそろった ' + READY_QUESTIONS.length + ' 問を演習できます。図表中心で選択肢が欠ける問題は、出典ページで確認してください。</p>' +
            '<button id="quiz-start" type="button" class="primary-btn">この条件で始める</button>' +
          '</div>' +
          '<div id="quiz-player" class="quiz-player card" hidden>' +
            '<div class="quiz-progress-row"><span id="quiz-progress"></span><button id="quiz-end" type="button" class="text-btn">中断して戻る</button></div>' +
            '<div class="progress-track"><div id="quiz-progress-bar" class="progress-bar"></div></div>' +
            '<div id="quiz-question"></div><div id="quiz-choices" class="quiz-choices" role="group" aria-label="解答を選択"></div>' +
            '<div id="quiz-feedback" class="quiz-feedback" aria-live="polite" hidden></div>' +
            '<button id="quiz-next" type="button" class="primary-btn" hidden>次の問題へ</button>' +
          '</div>' +
          '<div id="quiz-result" class="quiz-result card" hidden></div>' +
        '</div>' +
        '<div id="card-view" class="practice-view" hidden>' +
          '<div id="card-stats" class="practice-stats"></div>' +
          '<div id="card-home" class="practice-home card">' +
            '<h3>カードを復習する</h3>' +
            '<div class="practice-config">' +
              '<label>出題方法<select id="card-mode"><option value="all">ランダム</option><option value="new">未復習のみ</option><option value="weak">あやしい・忘れたカード</option></select></label>' +
              '<label>カテゴリ<select id="card-category"><option value="">すべてのカテゴリ</option></select></label>' +
              '<label>カード数<select id="card-count"><option value="5">5枚</option><option value="10" selected>10枚</option><option value="20">20枚</option></select></label>' +
            '</div>' +
            '<p id="card-pool-note" class="count-note"></p><button id="card-start" type="button" class="primary-btn">カードを始める</button>' +
          '</div>' +
          '<div id="card-player" class="card-player card" hidden>' +
            '<div class="quiz-progress-row"><span id="card-progress"></span><button id="card-end" type="button" class="text-btn">中断して戻る</button></div>' +
            '<div class="progress-track"><div id="card-progress-bar" class="progress-bar"></div></div>' +
            '<span id="card-category-label" class="card-category-label"></span><h3 id="card-term" class="card-term"></h3>' +
            '<p class="muted">意味や使いどころを思い出してから、答えを表示してください。</p>' +
            '<button id="card-reveal" type="button" class="secondary-btn">答えを見る</button>' +
            '<div id="card-answer" class="card-answer" hidden></div>' +
            '<div id="card-ratings" class="card-ratings" hidden><p>思い出せましたか？</p><button type="button" data-card-rating="known">覚えた</button><button type="button" data-card-rating="uncertain">あやしい</button><button type="button" data-card-rating="forgot">忘れた</button></div>' +
          '</div>' +
          '<div id="card-result" class="quiz-result card" hidden></div>' +
        '</div>' +
      '</div>';
  }

  function bindEvents() {
    document.querySelectorAll("[data-practice-view]").forEach(function (button) {
      button.addEventListener("click", function () { showView(button.dataset.practiceView); });
    });
    ["quiz-mode", "quiz-period", "quiz-category", "quiz-count"].forEach(function (id) {
      byId(id).addEventListener("change", updatePoolNote);
    });
    ["card-mode", "card-category", "card-count"].forEach(function (id) {
      byId(id).addEventListener("change", updateCardPoolNote);
    });
    byId("quiz-start").addEventListener("click", function () { startQuiz(); });
    byId("quiz-next").addEventListener("click", nextQuestion);
    byId("quiz-end").addEventListener("click", showQuizHome);
    byId("card-start").addEventListener("click", startCards);
    byId("card-reveal").addEventListener("click", revealCard);
    byId("card-end").addEventListener("click", showCardHome);
    document.querySelectorAll("[data-card-rating]").forEach(function (button) {
      button.addEventListener("click", function () { rateCard(button.dataset.cardRating); });
    });
    document.addEventListener("keydown", function (event) {
      if (!quizState || quizState.answered || byId("quiz-player").hidden) return;
      var answer = LETTER_KEYS[event.key] || event.key;
      var valid = quizState.queue[quizState.index].choices.some(function (choice) { return choice[0] === answer; });
      if (valid) {
        event.preventDefault();
        answerQuestion(quizState.queue[quizState.index], answer);
      }
    });
  }

  function initialize() {
    root = byId("practice-app");
    if (!root || !QUESTIONS.length) return;
    cards = collectCards();
    renderApp();
    setupQuestionOptions();
    setupCardOptions();
    bindEvents();
    showQuizHome();
    showCardHome();
  }

  document.addEventListener("DOMContentLoaded", initialize);
})();
