import json
import os
import re
from datetime import datetime, timezone

try:
    import feedparser
except ImportError:
    raise SystemExit("feedparser가 필요합니다. 로컬에서는: pip install feedparser")

POSTS_DIR = "posts"
POSTS_JSON = os.path.join(POSTS_DIR, "posts.json")

RSS_LIST = [
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://hnrss.org/frontpage",
]

AFFILIATE_NOTE = """
<hr>
<p><b>추천/구매 링크</b><br>
아직 제휴 링크가 없으면, 나중에 쿠팡파트너스/아마존/알리 제휴 링크로 교체하면 됩니다.<br>
예시: <a href="https://www.coupang.com/">쿠팡에서 비슷한 상품 보기</a></p>
"""


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9가-힣\\s-]", "", s)
    s = re.sub(r"\\s+", "-", s).strip("-")
    if not s:
        s = "post"
    return s[:80]


def load_posts_index():
    if os.path.exists(POSTS_JSON):
        with open(POSTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posts_index(items):
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def pick_topic():
    for url in RSS_LIST:
        feed = feedparser.parse(url)
        if getattr(feed, "entries", None):
            e = feed.entries[0]
            title = getattr(e, "title", "오늘의 이슈")
            link = getattr(e, "link", "")
            summary = getattr(e, "summary", "") or getattr(e, "description", "")
            return title, link, re.sub("<[^<]+?>", "", summary)[:600]
    return "오늘의 추천 아이템", "", "오늘은 실무에서 바로 쓰는 추천 리스트를 정리합니다."


def build_post_html(title, source_link, source_summary, dt):
    date_str = dt.strftime("%Y-%m-%d")
    safe_title = title.replace("<", "&lt;").replace(">", "&gt;")
    src = f'<p><small>출처: <a href="{source_link}">{source_link}</a></small></p>' if source_link else ""
    body = f"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{safe_title}</title>
  <style>
    body{{max-width:900px;margin:40px auto;padding:0 12px;font-family:system-ui;line-height:1.65}}
    a{{color:#0b63ce;text-decoration:none}} a:hover{{text-decoration:underline}}
    .muted{{opacity:.7}}
    code,pre{{background:#f6f6f6;padding:2px 6px;border-radius:6px}}
    hr{{border:none;border-top:1px solid #e5e5e5;margin:24px 0}}
  </style>
</head>
<body>
  <p><a href="../">← 홈</a> | <a href="./">목록</a></p>
  <h1>{safe_title}</h1>
  <p class="muted">{date_str}</p>
  {src}
  <h3>핵심 요약</h3>
  <p>{source_summary}</p>

  <h3>바로 쓰는 체크리스트</h3>
  <ul>
    <li>이 이슈/제품이 실제로 필요한 사람은 누구인지 한 줄로 정의하기</li>
    <li>가격/대체재/구매 포인트 3개만 정리하기</li>
    <li>관련 상품/서비스 링크(제휴 링크)로 연결하기</li>
  </ul>

  <h3>결론</h3>
  <p>오늘 포인트는 “구매/행동으로 이어지는 정보”만 남기는 겁니다. 내일도 자동으로 올라옵니다.</p>

  {AFFILIATE_NOTE}
</body>
</html>
"""
    return body


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)

    now = datetime.now(timezone.utc).astimezone()
    title, link, summary = pick_topic()

    date_str = now.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.html"
    filepath = os.path.join(POSTS_DIR, filename)

    i = 2
    while os.path.exists(filepath):
        filename = f"{date_str}-{slug}-{i}.html"
        filepath = os.path.join(POSTS_DIR, filename)
        i += 1

    html = build_post_html(title, link, summary, now)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    index = load_posts_index()
    index.append({"title": title, "date": date_str, "file": filename})
    save_posts_index(index)

    print(f"Generated: {filepath}")


if __name__ == "__main__":
    main()
