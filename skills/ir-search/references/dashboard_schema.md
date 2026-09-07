# 대시보드 데이터 형식 (dashboard.json)

`build_dashboard.py`가 읽어 `templates/dashboard.html`에 끼워 넣는 JSON 한 파일의 형식.
지원사업(수혜)과 수주(입찰·용역) 공고를 **같은 형식**으로 담고 `kind` 칸으로 구분한다.
대시보드 상단 토글(전체 / 수주 / 지원사업)이 이 칸을 본다.

공고 본문에 없는 값은 추정하지 않고 `null`(화면에는 '불명')로 둔다.

## 최상위

| 키 | 타입 | 설명 |
|---|---|---|
| `meta` | object | 헤더·KPI 재료 |
| `open` | array | Ⅰ 지금 지원 가능한 공고 (카드) — 접수중 + 자격 충족(A그룹) 또는 수주 참가 가능 |
| `roadmap` | array | Ⅱ 요건 충족 시 / 연례 반복 (표) — B그룹, 이번 회차 마감된 반복 사업 |
| `reframe` | array | Ⅲ 변형하면 가능 (표) — C그룹 |
| `excluded` | array | Ⅳ 검토 후 제외 (표) |
| `conclusion` | string(HTML) | Ⅴ 탐색 결론 — `<b class="h">` 소제목 + `<ul>` 구조 권장 |
| `notes` | array of string | 데이터 신뢰도 안내 항목 (커버리지·부분수집·불명 표기 등) |

## meta

| 키 | 타입 | 예 |
|---|---|---|
| `target` | string | 프로필의 `대상` 이름 → 헤더 제목 "○○ 사업 탐색 대시보드" |
| `date` | `YYYY-MM-DD` | 기준일 (D-day 계산 기준) |
| `eyebrow` | string | 헤더 위 작은 영문/한글 라벨. 비우면 "Business Opportunity Scan" |
| `profile_summary` | string | 헤더 부제. 프로필 요약 한 문장 |
| `regions` | array of string | 지역 한정 칩 라벨들 (예: ["제주","경기"] → "제주 한정만"·"경기 한정만" 버튼). 비우면 칩 없음 |
| `channels` | array of string | 수집 채널 표시 (예: ["K-Startup", "기업마당", "나라장터"]) |
| `counts` | object | `{ "open": n, "roadmap": n, "reframe": n, "excluded": n }` — 비우면 배열 길이로 계산 |
| `scope_fingerprint` | string \| null | scope_plan.json의 fingerprint (재조사 대조용, 푸터 표시) |
| `report_path` | string \| null | 마크다운 보고서 경로 (푸터 표시) |

## open[] — 카드 한 장

| 키 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `kind` | `"grant"` \| `"bid"` | ✓ | grant=지원사업, bid=수주(입찰·용역) |
| `id` | string | ✓ | 출처 내 고유 ID (K-Startup `pbancSn`, 나라장터 입찰공고번호 등) |
| `source` | string | ✓ | 출처 코드 (`kstartup`, `bizinfo`, `nipa`, `kocca`, `smtech`, `g2b`) |
| `n` | string | ✓ | 공고명 |
| `org` | string | ✓ | 기관 (없으면 "불명") |
| `cat` | string | ✓ | 유형 칩. 지원사업: 자금·공간·R&D·멘토링·글로벌·인프라·경진대회 등 / 수주: 교육운영·행사대행·콘텐츠개발 등. 미분류는 원 출처의 분류를 그대로 |
| `due` | `YYYY-MM-DD` \| null | ✓ | 마감일. null이면 "마감 불명" |
| `dueT` | `HH:MM` \| null | | 마감 시각 |
| `budget` | number \| null | | 사업비(원). 지원사업은 지원 한도, 수주는 추정가격·기초금액 |
| `bl` | string \| null | | 사업비 라벨 ("추정가격", "기초금액", "지원 한도" …). null이면 "사업비" |
| `method` | string \| null | | 수주: 계약방식 / 지원사업: 지원 형태("사업화 자금 + 입주공간") |
| `region` | string \| null | | 지역 제한 공고면 지역 이름 ("경기"). `meta.regions`의 값과 같아야 칩 필터에 걸림 |
| `sum` | string | ✓ | 공고 요약 1~2문장 (개조식 ~함/~임). 상세 미검증이면 제목 기반 한 줄 |
| `fit` | string(HTML) \| null | | 적합 이유. `<b class='kw'>(키워드)</b> 설명` 반복. null이면 "검증 전" 표시 |
| `warn` | string \| null | | 확인 필요 사항 |
| `score` | integer 0~100 \| null | | 적합도. null이면 "미평가" (필터·정렬에서 최하위) |
| `eligibility` | string \| null | | 지원사업 전용: 자격 검증 결과 요약 ("예비창업자 ✓ · 만 39세 이하 ✓ · 전국 ✓") |
| `url` | string | ✓ | 원문 링크 |

## roadmap[] — Ⅱ 표

| 키 | 설명 |
|---|---|
| `kind` | grant / bid |
| `n`, `org` | 사업명, 기관 |
| `when` | 다음 공고 예상 시기 또는 트리거 ("비수도권 법인 설립 후", "2027. 2.~3.") |
| `size` | 규모 텍스트 (HTML 허용, `<span class="dim">` 부연) |
| `score` | 적합 (정수 또는 null) |
| `point` | 준비 포인트 / 연쇄 경로 |
| `url` | 원문 (선택) |

## reframe[] — Ⅲ 표

| 키 | 설명 |
|---|---|
| `kind`, `n`, `org` | |
| `angle` | 프레이밍 각도 ("AI 음성 기술 → 오디오 콘텐츠 제작 파이프라인으로 재서술") |
| `risk` | 리스크 ("결과물이 콘텐츠여야 함") |
| `due` | 마감일 (선택) |
| `url` | 원문 (선택) |

## excluded[] — Ⅳ 표

| 키 | 설명 |
|---|---|
| `kind`, `n`, `org` | |
| `size` | 규모 텍스트 |
| `reason` | 제외 사유 (HTML 허용) |

## 채우는 주체

| 칸 | 채우는 쪽 |
|---|---|
| `id, source, n, org, due, url`, 지원사업 `cat`(원 분류), 수주 `budget/bl/method/dueT` | 크롤러 → `build_dashboard.py --from-jsonl` 부트스트랩 |
| `sum, fit, warn, score, eligibility, region`, 섹션 배정(open/roadmap/reframe/excluded), `conclusion` | Claude — SKILL.md 2~3단계(전수 검토·상세 검증) 결과를 기록 |
| `meta.*` | 프로필(`ir-search-profile.md`) + 실행 매니페스트 |

## 부트스트랩 규칙 (`--from-jsonl`)

크롤 jsonl(K-Startup 형식: `pbancSn, category, title, org, start, deadline, url`)을 읽어
`open[]`에 `kind="grant"`, `score=null`, `fit=null`, `sum=제목`으로 넣는다. 판정 전 상태이므로
화면에는 "미평가 / 검증 전"으로 표시된다. Claude가 판정을 채운 뒤 다시 빌드한다.
