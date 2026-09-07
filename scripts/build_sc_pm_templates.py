# -*- coding: utf-8 -*-
"""06_SC午後_用語別_解答テンプレート.md から音読用の1ページHTMLを生成する。

入力:  06_SC午後_用語別_解答テンプレート.md（正本）
出力:  html/sc_pm_templates.html（単一ファイル。CSS/JSは埋め込み、外部依存なし）

md の見出し・箇条書き・表・引用をそのまま構造化して出力する。要約はしない。
「…。」で終わる鉤括弧はそのまま使える解答テンプレ文として印を付け、
「テンプレ文だけ」表示や検索の対象にする。

使い方:  py -3 scripts/build_sc_pm_templates.py
"""

from __future__ import annotations

import datetime as dt
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "06_SC午後_用語別_解答テンプレート.md"
OUTPUT = ROOT / "html" / "sc_pm_templates.html"
JST = dt.timezone(dt.timedelta(hours=9))

LIST_RE = re.compile(r"^(\s*)(-|\*|\d+\.)\s+(.*)$")
CHAPTER_RE = re.compile(r"^(\d+)\.\s*(.*?)(?:（([^（）]*)）)?$")
TERM_RE = re.compile(r"^(.*?)（(.*)）$")
CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
TEMPLATE_RE = re.compile(r"「[^」]*。」")
PAIR_HINT_RE = re.compile(r"（([^（）]*)）")


# --- markdown（この文書で使われている記法だけ）を読む -----------------------


def parse_table(rows: list[str]) -> tuple[list[str], list[list[str]]]:
    cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in rows]
    return cells[0], cells[2:]


def parse_list(lines: list[str], index: int) -> tuple[list[dict], int]:
    root: list[dict] = []
    stack: list[tuple[int, list[dict]]] = [(-1, root)]
    last: dict | None = None
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            following = lines[index + 1] if index + 1 < len(lines) else ""
            if not LIST_RE.match(following):
                break
            index += 1
            continue
        match = LIST_RE.match(line)
        if match:
            indent = len(match.group(1))
            item = {"text": match.group(3).strip(), "children": [], "ordered": match.group(2) not in ("-", "*")}
            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()
            stack[-1][1].append(item)
            stack.append((indent, item["children"]))
            last = item
            index += 1
            continue
        if line.startswith(" ") and last is not None:  # 折り返された項目の続き
            last["text"] += line.strip()
            index += 1
            continue
        break
    return root, index


def parse(text: str) -> dict:
    lines = text.splitlines()
    doc: dict = {"title": "", "intro": [], "chapters": [], "outro": []}
    chapter: dict | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped == "---":
            index += 1
            continue
        if stripped.startswith("# "):
            doc["title"] = stripped[2:].strip()
            index += 1
            continue
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            match = CHAPTER_RE.match(heading)
            chapter = {
                "number": match.group(1) if match else str(len(doc["chapters"]) + 1),
                "title": (match.group(2) if match else heading).strip(),
                "tag": (match.group(3) or "").strip() if match else "",
                "blocks": [],
            }
            doc["chapters"].append(chapter)
            index += 1
            continue
        if stripped.startswith("### "):
            chapter["blocks"].append(("term", stripped[4:].strip()))
            index += 1
            continue
        if stripped.startswith(">"):
            quote: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip().lstrip(">").strip())
                index += 1
            if chapter is None:
                doc["intro"] = quote
            else:
                chapter["blocks"].append(("quote", quote))
            continue
        if stripped.startswith("|"):
            rows: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            chapter["blocks"].append(("table", parse_table(rows)))
            continue
        if LIST_RE.match(line):
            items, index = parse_list(lines, index)
            chapter["blocks"].append(("list", items))
            continue
        chapter["blocks"].append(("p", stripped))
        index += 1
    if doc["chapters"] and doc["chapters"][-1]["blocks"] and doc["chapters"][-1]["blocks"][-1][0] == "quote":
        doc["outro"] = doc["chapters"][-1]["blocks"].pop()[1]  # 文末の注記は章ではなくフッタへ
    return doc


# --- HTML を組み立てる ------------------------------------------------------


def inline(text: str) -> str:
    out = html.escape(text)
    out = CODE_RE.sub(lambda m: "<code>" + m.group(1) + "</code>", out)
    out = BOLD_RE.sub(lambda m: "<strong>" + m.group(1) + "</strong>", out)
    return TEMPLATE_RE.sub(lambda m: '<span class="tmpl">' + m.group(0) + "</span>", out)


def has_template(text: str) -> bool:
    return bool(TEMPLATE_RE.search(text))


def render_items(items: list[dict], depth: int = 0) -> str:
    if not items:
        return ""
    tag = "ol" if items[0]["ordered"] else "ul"
    out = ["<" + tag + ('' if depth else ' class="items"') + ">"]
    for item in items:
        text = item["text"] + "".join(child["text"] for child in item["children"])
        head = "<li>"
        if depth == 0:  # 「テンプレ文だけ」表示は最上位の項目単位で絞り込む
            head = '<li class="top"' + (' data-t="1"' if has_template(text) else "") + ">"
        out.append(head + inline(item["text"]))
        out.append(render_items(item["children"], depth + 1))
        out.append("</li>")
    out.append("</" + tag + ">")
    return "".join(out)


def render_table(header: list[str], rows: list[list[str]]) -> str:
    head = "".join("<th>" + inline(cell) + "</th>" for cell in header)
    body = "".join("<tr>" + "".join("<td>" + inline(cell) + "</td>" for cell in row) + "</tr>" for row in rows)
    return '<div class="table-wrap"><table><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table></div>"


def unit(kind: str, body: str) -> str:
    """テンプレ文を含む固まりに印を付ける（「テンプレ文だけ」表示と検索の単位）。"""
    return '<div class="' + kind + ' unit"' + (' data-t="1"' if 'class="tmpl"' in body else "") + ">" + body + "</div>"


def render_blocks(blocks: list[tuple]) -> str:
    out: list[str] = []
    term: dict | None = None

    def close() -> None:
        nonlocal term
        if term:
            out.append(unit("term", term["head"] + "".join(term["body"])))
            term = None

    for kind, payload in blocks:
        if kind == "term":
            close()
            match = TERM_RE.match(payload)
            name = match.group(1) if match else payload
            gloss = match.group(2) if match else ""
            head = "<h3>" + inline(name) + (' <span class="gloss">（' + inline(gloss) + "）</span>" if gloss else "") + "</h3>"
            term = {"head": head, "body": []}
            continue
        piece = ""
        if kind == "list":
            piece = render_items(payload)
        elif kind == "table":
            piece = render_table(*payload)
        elif kind == "quote":
            piece = '<blockquote class="note">' + "<br>".join(inline(line) for line in payload) + "</blockquote>"
        elif kind == "p":
            piece = "<p>" + inline(payload) + "</p>"
        if term:
            term["body"].append(piece)
        else:
            out.append(unit("block", piece))
    close()
    return "".join(out)


def render_pairs(blocks: list[tuple]) -> str:
    items = next((payload for kind, payload in blocks if kind == "list"), [])
    cards = []
    for item in items:
        sides = [side.strip() for side in item["text"].split("↔")]
        chips = []
        for index, side in enumerate(sides):
            label = PAIR_HINT_RE.sub(lambda m: '<span class="hint">（' + html.escape(m.group(1)) + "）</span>", html.escape(side))
            # 「↔」は後ろの語と一緒に折り返す（行末に演算子だけ残さない）
            chips.append('<span class="grp">' + ('<span class="vs">↔</span>' if index else "") + '<span class="side">' + label + "</span></span>")
        cards.append('<button type="button" class="pair unit">' + "".join(chips) + "</button>")
    return '<div class="pairs" id="pairs">' + "".join(cards) + "</div>"


def render_nav(chapters: list[dict]) -> str:
    out = []
    for chapter in chapters:
        out.append(
            '<a class="nav-item" href="#ch' + chapter["number"] + '" data-nav="' + chapter["number"] + '">'
            '<span class="n">' + chapter["number"].zfill(2) + "</span>"
            "<span>" + html.escape(chapter["title"]) + "</span>"
            '<span class="tick" aria-hidden="true">✓</span></a>'
        )
    return "".join(out)


def render_chapters(chapters: list[dict]) -> str:
    out = []
    for chapter in chapters:
        number = chapter["number"]
        body = render_pairs(chapter["blocks"]) if number == "12" else render_blocks(chapter["blocks"])
        extra = ""
        if number == "12":
            extra = ('<p class="sub">カードをクリックすると、そのカードだけヒントを表示する。'
                     '<button type="button" class="mini" id="hint-toggle">ヒントを隠す</button></p>')
        out.append(
            '<section class="ch panel" id="ch' + number + '" data-ch="' + number + '">'
            '<h2><span class="num">' + number.zfill(2) + "</span>"
            "<span>" + html.escape(chapter["title"]) + "</span>"
            + ('<span class="tag">' + html.escape(chapter["tag"]) + "</span>" if chapter["tag"] else "")
            + '<label class="done"><input type="checkbox" class="check" data-ch="' + number + '"><span>読了</span></label>'
            "</h2>" + extra + body + "</section>"
        )
    return "".join(out)


TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>06 用語別・解答テンプレート</title>
<!-- 自前のライト／ダーク配色を持つため、Pages の dark.css 自動注入は不要: data-sc-dark-theme -->
<style>
:root{
  --ink:#17231f;--muted:#66716c;--paper:#f5f2e9;--card:#fffdf7;
  --green:#176b55;--green2:#d9eee5;--amber:#bd6b23;--amber2:#f8e5cd;
  --blue:#315c89;--blue2:#dce8f3;--line:#d9d8ce;--shadow:#243c3210;--control:#fff;
  color-scheme:light dark;
}
@media (prefers-color-scheme:dark){
  :root{
    --ink:#e7efe9;--muted:#b7c4bc;--paper:#101713;--card:#19231e;
    --green:#77d4af;--green2:#1d493a;--amber:#ffba70;--amber2:#53371c;
    --blue:#9bcaff;--blue2:#1c3c57;--line:#394a41;--shadow:#00000042;--control:#101713;
  }
  header{background:linear-gradient(135deg,#0d3027,#14543f 58%,#1d6a53)}
  .check{border-color:#92a49a}
}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:96px}
body{margin:0;background:var(--paper);color:var(--ink);line-height:1.75;
  font-family:"Yu Gothic UI","Yu Gothic",Meiryo,sans-serif}
.wrap{width:min(980px,calc(100% - 32px));margin:auto}
header{padding:34px 0 26px;background:linear-gradient(135deg,#123f35,#176b55 58%,#2b7f68);color:#fff}
.eyebrow{font-size:.76rem;letter-spacing:.16em;font-weight:700;opacity:.82}
h1{font-size:clamp(1.6rem,4vw,2.6rem);line-height:1.2;margin:8px 0 10px}
.lead{margin:0;color:#e5f3ed;font-size:.95rem;max-width:70ch}
.lead b{color:#fff}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.chip{border:1px solid #ffffff55;border-radius:999px;padding:5px 12px;font-size:.8rem;background:#ffffff12}

.bar{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--line);padding:10px 0}
.bar-in{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
input[type=search]{flex:1 1 220px;min-width:0;padding:9px 12px;border:1px solid var(--line);border-radius:10px;
  background:var(--control);color:var(--ink);font:inherit;font-size:.94rem}
button.toggle,button.mini{border:1px solid var(--line);border-radius:10px;background:var(--control);color:var(--ink);
  font:inherit;font-size:.86rem;padding:9px 12px;cursor:pointer}
button.mini{padding:3px 10px;font-size:.8rem;margin-left:6px}
button.toggle[aria-pressed=true]{background:var(--green);border-color:var(--green);color:#fff;font-weight:700}
.count{color:var(--muted);font-size:.82rem;margin-left:auto}

main{padding:18px 0 60px}
nav.toc{display:grid;grid-template-columns:repeat(auto-fill,minmax(224px,1fr));gap:8px;margin:0 0 22px}
.nav-item{display:flex;gap:8px;align-items:center;text-decoration:none;color:var(--ink);background:var(--card);
  border:1px solid var(--line);border-radius:12px;padding:8px 11px;font-size:.88rem}
.nav-item:hover{border-color:var(--green)}
.nav-item .n{font-weight:800;color:var(--green);font-variant-numeric:tabular-nums}
.nav-item .tick{margin-left:auto;color:var(--green);opacity:0;font-weight:800}
.nav-item.read .tick{opacity:1}
.nav-item.read{background:var(--green2)}

.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px;box-shadow:0 8px 28px var(--shadow);margin:0 0 16px}
.ch h2{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:1.18rem;margin:0 0 12px;
  padding-bottom:10px;border-bottom:1px solid var(--line)}
.ch h2 .num{font-size:.82rem;font-weight:800;color:#fff;background:var(--green);border-radius:8px;padding:3px 8px}
.tag{font-size:.72rem;color:var(--blue);background:var(--blue2);border-radius:999px;padding:2px 9px;font-weight:700}
.done{margin-left:auto;display:flex;align-items:center;gap:6px;font-size:.8rem;color:var(--muted);cursor:pointer;font-weight:400}
.check{appearance:none;width:19px;height:19px;border:2px solid #a5aaa6;border-radius:6px;background:var(--control);cursor:pointer}
.check:checked{background:var(--green);border-color:var(--green);box-shadow:inset 0 0 0 4px var(--card)}
.term{margin:0 0 14px}
.term h3{margin:0 0 6px;font-size:1rem;color:var(--green)}
.gloss{font-size:.82rem;font-weight:400;color:var(--muted)}
.block{margin:0 0 12px}
.term>ul,.term>ol,.block>ul,.block>ol{margin:4px 0 0;padding-left:1.3em}
li{margin:3px 0}
li ul,li ol{margin:3px 0 4px;padding-left:1.25em}
code{background:var(--green2);color:var(--ink);border-radius:5px;padding:1px 5px;font-size:.88em}
.tmpl{background:var(--amber2);border-radius:5px;padding:1px 3px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.note{margin:8px 0 0;padding:9px 13px;border-left:4px solid var(--amber);background:var(--amber2);border-radius:0 10px 10px 0;font-size:.9rem}
.sub{color:var(--muted);font-size:.84rem;margin:0 0 10px}
.table-wrap{overflow-x:auto;margin:6px 0 0}
table{width:100%;border-collapse:collapse;font-size:.9rem;min-width:min(560px,100%)}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-size:.82rem;white-space:nowrap}

.pairs{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.pair{display:flex;flex-wrap:wrap;align-items:center;gap:6px;text-align:left;font:inherit;font-size:.9rem;
  background:var(--card);border:1px solid var(--line);border-radius:12px;padding:11px 13px;cursor:pointer;color:var(--ink)}
.pair:hover{border-color:var(--green)}
.grp{display:inline-flex;align-items:baseline;gap:6px;min-width:0}
.side{font-weight:700;min-width:0}
.hint{font-weight:400;color:var(--muted);transition:opacity .12s}
.vs{color:var(--green);font-weight:800}
.pairs.hide-hints .pair:not(.reveal) .hint{opacity:0}

body.reading main{font-size:1.14rem}
body.reading .term h3{font-size:1.1rem}
body.reading li{margin:8px 0}
body.reading .panel{line-height:2}
body.templates-only li.top:not([data-t]){display:none}
body.templates-only .table-wrap,body.templates-only .note{display:none}
.hidden{display:none!important}
footer{color:var(--muted);font-size:.8rem;padding:24px 0 40px;border-top:1px solid var(--line)}
footer a{color:var(--green)}
@media(max-width:560px){
  .ch h2{font-size:1.05rem}.panel{padding:15px}.done{margin-left:0;width:100%}
  nav.toc{grid-template-columns:1fr 1fr}.nav-item span:not(.n):not(.tick){font-size:.8rem}
}
@media print{
  body{background:#fff;color:#111}header{background:#fff;color:#111;padding:0 0 10px}
  .lead{color:#333}.bar,nav.toc,.done,.chips,.mini{display:none}
  .panel{box-shadow:none;border-color:#ccc;break-inside:avoid;background:#fff}
  .pairs.hide-hints .hint{opacity:1}
}
</style>
</head>
<body>
<header><div class="wrap">
  <div class="eyebrow">SC 午後 · 音読用テンプレート集</div>
  <h1>06 用語別・解答テンプレート</h1>
  <p class="lead">__LEAD__</p>
  <div class="chips">__CHIPS__</div>
</div></header>

<div class="bar"><div class="wrap bar-in">
  <input type="search" id="q" placeholder="検索（例：DKIM、CSRFトークン、KEV）　/ キーで移動" aria-label="本文を検索">
  <button type="button" class="toggle" id="t-tmpl" aria-pressed="false">テンプレ文だけ</button>
  <button type="button" class="toggle" id="t-read" aria-pressed="false">音読モード</button>
  <span class="count" id="count"></span>
</div></div>

<main class="wrap">
  <nav class="toc" id="toc">__NAV__</nav>
  __CHAPTERS__
  <p class="sub" id="empty" hidden>一致する項目がありません。</p>
</main>

<footer><div class="wrap">
  <p>__OUTRO__</p>
  <p><a href="./index.html">SC午後対策ダッシュボード（01〜06）</a>　/　<a href="./2026_SC_roadmap.html">SC合格ロードマップ 2026</a>　/　<a href="./sc_pm_grader.html">午後記述式セルフ採点</a></p>
  <p>正本は <code>06_SC午後_用語別_解答テンプレート.md</code>。このページは <code>scripts/build_sc_pm_templates.py</code> で生成（__GENERATED__）。読了チェックはこの端末にだけ保存されます。<button type="button" class="mini" id="reset">読了チェックを消す</button></p>
</div></footer>

<script>
(function(){
  'use strict';
  var KEY='sc-pm-templates-read-v1', PREFIX=KEY+':';
  var $=function(id){return document.getElementById(id);};
  var checks=[].slice.call(document.querySelectorAll('.check'));
  var units=[].slice.call(document.querySelectorAll('.unit'));
  var sections=[].slice.call(document.querySelectorAll('.ch'));

  function read(){
    var raw='';
    try{raw=localStorage.getItem(KEY)||'';}catch(e){}
    if(!raw&&window.name.indexOf(PREFIX)===0)raw=window.name.slice(PREFIX.length);
    try{var parsed=JSON.parse(raw||'{}');return parsed&&typeof parsed==='object'&&!Array.isArray(parsed)?parsed:{};}
    catch(e){return {};}
  }
  function write(state){
    var text=JSON.stringify(state);
    try{localStorage.setItem(KEY,text);}catch(e){window.name=PREFIX+text;}
  }
  var state=read();
  function paint(){
    var done=0;
    checks.forEach(function(box){
      var on=state[box.dataset.ch]===true;
      box.checked=on;
      var nav=document.querySelector('[data-nav="'+box.dataset.ch+'"]');
      if(nav)nav.classList.toggle('read',on);
      if(on)done++;
    });
    $('count').textContent='読了 '+done+' / '+checks.length+'章';
  }
  checks.forEach(function(box){
    box.addEventListener('change',function(){state[box.dataset.ch]=box.checked;write(state);paint();});
  });
  $('reset').addEventListener('click',function(){state={};write(state);paint();});
  paint();

  var box=$('q');
  function apply(){
    var query=box.value.trim().toLowerCase();
    var only=document.body.classList.contains('templates-only');
    var hits=0;
    units.forEach(function(item){
      var show=(!query||item.textContent.toLowerCase().indexOf(query)>=0)&&(!only||item.hasAttribute('data-t'));
      item.classList.toggle('hidden',!show);
      if(show)hits++;
    });
    sections.forEach(function(section){
      section.classList.toggle('hidden',!section.querySelector('.unit:not(.hidden)'));
    });
    $('toc').classList.toggle('hidden',!!query||only);
    $('empty').hidden=hits>0||(!query&&!only);
    if(query)$('count').textContent=hits+'件';
    else if(only)$('count').textContent='テンプレ '+hits+'件';
    else paint();
  }
  function toggle(button,cls){
    button.addEventListener('click',function(){
      var on=button.getAttribute('aria-pressed')!=='true';
      button.setAttribute('aria-pressed',String(on));
      document.body.classList.toggle(cls,on);
      apply();
    });
  }
  toggle($('t-tmpl'),'templates-only');
  toggle($('t-read'),'reading');

  var hints=$('hint-toggle'), pairs=$('pairs');
  if(hints&&pairs){
    hints.addEventListener('click',function(){
      var on=!pairs.classList.contains('hide-hints');
      pairs.classList.toggle('hide-hints',on);
      if(on)[].forEach.call(pairs.querySelectorAll('.reveal'),function(card){card.classList.remove('reveal');});
      hints.textContent=on?'ヒントを表示':'ヒントを隠す';
    });
    [].forEach.call(pairs.querySelectorAll('.pair'),function(card){
      card.addEventListener('click',function(){card.classList.toggle('reveal');});
    });
  }

  box.addEventListener('input',apply);
  document.addEventListener('keydown',function(event){
    if(event.key==='/'&&document.activeElement!==box){event.preventDefault();box.focus();}
    if(event.key==='Escape'&&document.activeElement===box){box.value='';box.blur();apply();}
  });
})();
</script>
</body>
</html>
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    doc = parse(SOURCE.read_text(encoding="utf-8"))
    lead = "<br>".join(inline(re.sub(r"^\*\*(.+?)\*\*：", r"**\1**：", line)) for line in doc["intro"])
    chips = "".join(
        '<span class="chip">' + label + "</span>"
        for label in (
            str(len(doc["chapters"])) + "章",
            "テンプレ文 " + str(len(TEMPLATE_RE.findall(SOURCE.read_text(encoding="utf-8")))) + "本",
            "月曜 22:00 の音読30分",
            "§12 は試験直前に音読",
        )
    )
    page = (
        TEMPLATE.replace("__LEAD__", lead)
        .replace("__CHIPS__", chips)
        .replace("__NAV__", render_nav(doc["chapters"]))
        .replace("__CHAPTERS__", render_chapters(doc["chapters"]))
        .replace("__OUTRO__", "<br>".join(inline(line) for line in doc["outro"]))
        .replace("__GENERATED__", dt.datetime.now(JST).strftime("%Y-%m-%d %H:%M"))
    )
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"[info] {OUTPUT.relative_to(ROOT)} を生成しました（{len(doc['chapters'])}章・{len(page):,} bytes）")


if __name__ == "__main__":
    main()
