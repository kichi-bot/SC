# sc-siken.com 情報処理安全確保支援士 過去問 スクレイパー
# 出力: C:\SC\sc_kakomon.json

import sys, io, time, json, re
import requests, urllib3
from bs4 import BeautifulSoup
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
urllib3.disable_warnings()

BASE = "https://www.sc-siken.com"
OUT  = Path(r"C:\SC\sc_kakomon.json")

PERIODS = [
    ("令和7年秋期",   "/kakomon/07_aki/"),
    ("令和7年春期",   "/kakomon/07_haru/"),
    ("令和6年秋期",   "/kakomon/06_aki/"),
    ("令和6年春期",   "/kakomon/06_haru/"),
    ("令和5年秋期",   "/kakomon/05_aki/"),
    ("令和5年春期",   "/kakomon/05_haru/"),
    ("令和4年秋期",   "/kakomon/04_aki/"),
    ("令和4年春期",   "/kakomon/04_haru/"),
    ("令和3年秋期",   "/kakomon/03_aki/"),
    ("令和3年春期",   "/kakomon/03_haru/"),
    ("令和2年秋期",   "/kakomon/02_aki/"),
    ("令和元年秋期",  "/kakomon/01_aki/"),
    ("平成31年春期",  "/kakomon/31_haru/"),
    ("平成30年秋期",  "/kakomon/30_aki/"),
    ("平成30年春期",  "/kakomon/30_haru/"),
    ("平成29年秋期",  "/kakomon/29_aki/"),
    ("平成29年春期",  "/kakomon/29_haru/"),
    ("平成28年秋期",  "/kakomon/28_aki/"),
    ("平成28年春期",  "/kakomon/28_haru/"),
    ("平成27年秋期",  "/kakomon/27_aki/"),
    ("平成27年春期",  "/kakomon/27_haru/"),
    ("平成26年秋期",  "/kakomon/26_aki/"),
    ("平成26年春期",  "/kakomon/26_haru/"),
    ("平成25年秋期",  "/kakomon/25_aki/"),
    ("平成25年春期",  "/kakomon/25_haru/"),
    ("平成24年秋期",  "/kakomon/24_aki/"),
    ("平成24年春期",  "/kakomon/24_haru/"),
    ("平成23年秋期",  "/kakomon/23_aki/"),
    ("平成23年特別",  "/kakomon/23_toku/"),
    ("平成22年秋期",  "/kakomon/22_aki/"),
    ("平成22年春期",  "/kakomon/22_haru/"),
    ("平成21年秋期",  "/kakomon/21_aki/"),
    ("平成21年春期",  "/kakomon/21_haru/"),
]

SECTIONS = [
    ("午前Ⅰ", "am1", 30),
    ("午前Ⅱ", "am2", 25),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
LABELS  = ["ア", "イ", "ウ", "エ", "オ"]


def fetch(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            if r.status_code == 404:
                return None
            r.encoding = "utf-8"
            return r.text
        except Exception as e:
            if i < retries - 1:
                time.sleep(2)
            else:
                print(f"  ERROR {url}: {e}")
                return None


def parse_question(html, period_name, section_name, num):
    soup = BeautifulSoup(html, "html.parser")

    mondai = soup.find("div", id="mondai")
    if not mondai:
        return None
    question_text = mondai.get_text(strip=True)

    sel_list = soup.find("ul", class_="selectList")
    choices = {}
    if sel_list:
        for li in sel_list.find_all("li"):
            text = li.get_text(strip=True)
            for label in LABELS:
                if text.startswith(label):
                    choices[label] = text[len(label):]
                    break

    ans_box = soup.find("div", class_="answerBox")
    answer = ""
    if ans_box:
        raw = ans_box.get_text(strip=True)
        m = re.search(r"([アイウエオ])$", raw)
        if m:
            answer = m.group(1)

    ansbgs = soup.find_all("div", class_="ansbg")
    explanation = ""
    if len(ansbgs) >= 2:
        explanation = ansbgs[1].get_text(separator="\n", strip=True)

    return {
        "period":      period_name,
        "section":     section_name,
        "number":      num,
        "question":    question_text,
        "choices":     choices,
        "answer":      answer,
        "explanation": explanation,
    }


def main():
    results = []
    total_ok   = 0
    total_skip = 0

    for period_name, period_path in PERIODS:
        for section_name, section_key, max_q in SECTIONS:
            print(f"\n[{period_name} {section_name}]", flush=True)
            for num in range(1, max_q + 1):
                url = f"{BASE}{period_path}{section_key}_{num}.html"
                html = fetch(url)
                time.sleep(0.3)

                if html is None:
                    print(f"  skip:{num}", end=" ", flush=True)
                    total_skip += 1
                    continue

                item = parse_question(html, period_name, section_name, num)
                if item:
                    results.append(item)
                    print(f"  {num}:OK", end=" ", flush=True)
                    total_ok += 1
                else:
                    print(f"  {num}:ERR", end=" ", flush=True)
                    total_skip += 1

            print()

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n==== 完了 ====")
    print(f"取得: {total_ok}問  スキップ: {total_skip}問")
    print(f"保存: {OUT}")


if __name__ == "__main__":
    main()
