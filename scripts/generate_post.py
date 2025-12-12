import json
import os
import re
import urllib.parse
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
    hero = hero_image_url(title)
    body = f"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{safe_title}</title>
  <style>
    :root{{
      --bg:#0f172a;
      --panel:#0b1224;
      --text:#e6ecff;
      --muted:#9fb4ff;
      --accent:#7dd3fc;
      --accent-2:#a78bfa;
    }}
    *{{box-sizing:border-box}}
    body{{
      margin:0;
      min-height:100vh;
      font-family:"Inter","Pretendard","Noto Sans KR",system-ui;
      background:radial-gradient(120% 120% at 20% 20%, #1e293b, #0b1224 60%, #050914);
      color:var(--text);
      padding:32px 18px 72px;
      display:flex;
      justify-content:center;
    }}
    .shell{{
      width:100%;
      max-width:960px;
      background:rgba(11,18,36,0.7);
      border:1px solid rgba(255,255,255,0.08);
      border-radius:20px;
      backdrop-filter:blur(6px);
      padding:26px;
      box-shadow:0 20px 60px rgba(0,0,0,0.45);
      line-height:1.68;
    }}
    a{{color:var(--accent);text-decoration:none;font-weight:600;}}
    a:hover{{text-decoration:underline}}
    .muted{{color:var(--muted);font-size:14px;}}
    h1{{margin:6px 0 10px;font-size:30px;letter-spacing:-0.02em;}}
    h3{{margin-top:20px;margin-bottom:10px;}}
    ul{{padding-left:20px;}}
    code,pre{{background:rgba(255,255,255,0.04);padding:2px 6px;border-radius:6px;}}
    hr{{border:none;border-top:1px solid rgba(255,255,255,0.08);margin:26px 0}}
    .nav{{margin-bottom:12px;}}
    .badge{{display:inline-flex;align-items:center;gap:6px;padding:8px 12px;border-radius:999px;background:rgba(125,211,252,0.15);color:var(--accent);font-size:13px;letter-spacing:0.01em;}}
    .hero{{margin:16px 0 18px;}}
    .hero img{{width:100%;border-radius:16px;border:1px solid rgba(255,255,255,0.08);box-shadow:0 12px 30px rgba(0,0,0,0.35);display:block;}}
  </style>
</head>
<body>
  <main class="shell">
    <div class="nav"><a href="../">← 홈</a> | <a href="./">목록</a></div>
    <div class="badge">Daily Auto Post</div>
    <h1>{safe_title}</h1>
    <p class="muted">{date_str}</p>
    <figure class="hero">
      <img src="{hero}" alt="{safe_title}" loading="lazy" />
    </figure>
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
  </main>
</body>
</html>
"""
    return body


def hero_image_url(title: str) -> str:
    query = urllib.parse.quote(title or "news")
    # 무료, 키 없이 사용 가능한 Unsplash Source
    return f"https://source.unsplash.com/1200x630/?{query}"


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
