# HANDOFF — ir-search (silkomg9 포크)

마지막 갱신: 2026-09-08

## 지금 상태
- 원본 djfksjd/ir-search 를 포크해 **HTML 대시보드 기능**을 얹는 중. 지원사업(수혜) 조사는 원본 그대로 동작하고, 대시보드 생성(SKILL.md 5단계)이 추가됨.
- 설치 명령·플러그인 메타데이터는 silkomg9 로 전환됨 (`claude plugin marketplace add silkomg9/ir-search`).
- 대시보드 관련 파일: `skills/ir-search/templates/dashboard.html`, `skills/ir-search/scripts/build_dashboard.py`, `skills/ir-search/references/dashboard_schema.md`, `tests/test_build_dashboard.py`.
- 프로필은 템플릿 방식: `ir-search-profile.template.md`(git 추적) → 채운 `ir-search-profile.md`(gitignore). 현재 로컬에는 리사 프로필이 채워져 있음(개인 파일, 기기 이동 시 직접 복사).
- 실제 조사 1회 완료: `C:\Users\LISA\Documents\지원사업조사_리사_20260907\` (보고서.md, dashboard.html, 원시 jsonl, 상세 원문, 첨부). 재조사(diff 모드)는 이 폴더를 직전 결과로 씀.
- 로컬 미리보기: `.claude/launch.json`(gitignore) → `output/` 폴더를 8765 포트로 서빙. `output/`도 gitignore.

- **civic-search(새 스킬) 착수**: 개인·모임·비영리·협동조합 대상 교육·공모·지원사업 조사용. 2026-09-07 소스 조사 완료 → `docs/research/civic-sources-2026-09-07.md`(통합 분석) + `docs/research/raw/`(원시 5개). 소스 레지스트리 초안 `skills/civic-search/references/sources.md`(verified 25 / candidate / manual / excluded), 프로필 템플릿 `civic-search-profile.template.md`. SKILL.md·크롤러는 아직 없음.

## civic-search (개인·모임·비영리·협동조합 지원사업 스킬) 진행 상태
- 소스 레지스트리 v0.2: `skills/civic-search/references/sources.md` — 리사 판정(쓸만함/보류/제외) 반영, 목록 URL 전부 실호출 재확인·교정(2026-09-07~08).
- 새로 찾은 핵심 소스: **아트누리(artnuri.or.kr)** — 전국 문화재단·유관기관 예술지원사업 통합 포털(아르코 운영, SSR). 아르코·제주문화예술재단(JS 사이트) 공고를 여기서 대체 수집 가능.
- 점검표 HTML: `output/civic_sources_check.html` (gitignore, 로컬 미리보기 8765). 생성 스크립트는 스크래치패드에만 있음 — 필요하면 sources.md 표를 파싱해 다시 만든다.
- 남은 확인: work24 훈련과정 목록 URL, kakaoimpact·jfac·chest_jeju·jejutp XHR, ggvc 목록 URL, jejusi eminwon 검색 파라미터, seoul.go.kr robots `/news` 허용 여부.
- 다음 단계: civic-search SKILL.md 초안 + 어댑터 구현(gnuboard → wordpress → gg_baseboard → 개별 순).

## 다음 할 일
0. **civic-search 다음 단계**: (a) 레지스트리의 "후속 확인" 항목을 브라우저로 검증(seoulpa.kr, coop.go.kr, chest bbs 매핑, arko/jfac XHR, work24 목록 URL, seoul.go.kr robots `/news`) → (b) 어댑터 `gnuboard`·`wordpress`·`gg_baseboard`·`rss` 4종 먼저 구현(verified 소스 절반 커버) → (c) SKILL.md 작성(ir-search 워크플로 재사용, 프로필 축만 교체). 주의: seoulmaeul.org는 도메인 탈취 상태라 링크 금지.
1. **수주(입찰) 크롤러** `skills/ir-search/scripts/g2b_api.py` — 나라장터 입찰공고 공개 API(data.go.kr 키 재사용, 데이터셋 활용신청 필요). 출력 jsonl에 `kind=bid`, `budget/bl/method/dueT` 채우기 → `build_dashboard.py bootstrap`이 그대로 받음. 키 처리·마스킹은 `kstartup_api.py` 방식 재사용.
2. 사용자가 data.go.kr 키 발급 + 나라장터 API 활용신청 후 `.env`에 `DATA_GO_KR_KEY=` 저장.
3. 재조사 흐름 실검증: 2~4주 뒤 `diff_surveys.py` + `bootstrap --merge`로 직전 판정 보존 확인.
4. (선택) 대학 산학협력단·학교장터(S2B) 공고 누락 여부 확인 후 소스 추가 검토.

## 알아둘 것
- 테스트 중 3개(`test_attach_download.py`의 심볼릭 링크 2건·robots 경로 1건)는 Windows 권한·파이썬 3.14 차이로 실패 — 기능 무관, 원저장소 이슈.
- Windows에서 파이썬으로 파일을 쓰면 CRLF가 되기 쉬움 — 저장소는 LF 고정(`core.autocrlf=false`). 텍스트 파일을 쓸 때 `newline="\n"`.
- 크롤 결과를 URL 목록 파일로 넘길 때 CR(\r)이 붙으면 404가 남 — `tr -d '\r'`.
- 기업마당·NIPA는 기본 `--max-pages 30`이면 부분 수집(partial). 전수는 `--max-pages 120`.
- NIPA 게시판은 2020년부터 전체가 실려 있어 모집중은 마감일로 걸러야 함.
- 노션 기록: 앱개발 > 스킬 > 지원사업리서치 > 작업내용 (https://app.notion.com/p/3d4e952a671f81868882def94b2d9c39)
