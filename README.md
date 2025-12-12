AutoBlog (0원 자동 발행)
========================

GitHub Pages + GitHub Actions로 매일 자동으로 글을 생성·커밋·배포합니다. API 키/유료 모델 없이 RSS 기반으로 생성합니다.

빠른 사용법 (Windows PowerShell)
--------------------------------
```powershell
cd C:\홈페이지\autoblog
pip install feedparser
python .\scripts\generate_post.py   # 로컬 테스트
```

GitHub 연동
-----------
1) 새 저장소 생성 후 원격 추가:
```powershell
git init
git branch -M main
git remote add origin https://github.com/<USER>/autoblog.git
git add .
git commit -m "init autoblog"
git push -u origin main
```

2) GitHub Pages: Settings → Pages → Deploy from a branch → Branch `main`, folder `/` 설정.

3) Actions 워크플로: `.github/workflows/autopost.yml`는 매일 UTC 00:10(한국 09:10) 실행 → 글 생성 → 커밋/푸시. 필요하면 cron을 복수로 추가.

파일 구조
---------
- `index.html` : 홈
- `posts/index.html` : 글 목록(자동 생성된 `posts.json`을 읽음)
- `scripts/generate_post.py` : RSS 기반 글 생성기
- `.github/workflows/autopost.yml` : 일정 실행/커밋
- `posts/` : 생성된 글 및 `posts.json`

수익화 포인트
-------------
- `scripts/generate_post.py`의 `AFFILIATE_NOTE`에 제휴 링크 교체.
- `RSS_LIST`를 구매 의도가 높은 피드(IT 기기/생활용품 리뷰 등)로 교체.
- 발행 빈도 증가는 cron 라인 추가: 예) `"10 0 * * *"` + `"10 9 * * *"` (KST 09:10, 18:10).
