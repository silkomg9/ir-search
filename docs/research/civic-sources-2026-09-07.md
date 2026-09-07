# 개인·모임·비영리·협동조합 지원사업 소스 조사 (2026-09-07)

> 목적: "개인·모임(비법인)·비영리단체·협동조합이 지원할 수 있는 교육·공모·지원사업"을 찾는
> 새 스킬의 소스 레지스트리 초안. 기존 ir-search(기업·창업 대상) 소스와 겹치지 않는 것만 다룸.
> 검증 방법: 웹검색 + WebFetch + curl 실호출(브라우저 UA). "미확인"은 정직하게 남김.
> 원시 조사 파일 5개(전국 비영리 / 개인 / 서울 / 경기 / 제주)를 통합·재검증한 결과.

## 1. 한 줄 결론

- **바로 자동 수집 가능(1순위) 소스 25곳**이 확인됨. 대부분 서버렌더링 + 단순 페이지 파라미터.
- **핵심인데 기술 장벽이 있는 소스**: 사회적기업진흥원(robots 전면 차단), 제주도청(JS + robots), 서울시공익활동지원센터(JS 리다이렉트), 제주문화예술재단(JS).
- **큐레이션 허브형 소스**(타기관 공고를 사람이 모아 재게시)가 지역 커버리지에 가장 효율적: 제주청년센터·제주소통협력센터·제주콘텐츠진흥원, 더나은미래(RSS), 온통청년(오픈API).
- **지자체 본청 고시공고**는 노이즈가 커서 키워드 필터 필수. 시·군·구 통합 창구는 서울·경기 모두 **없음**.
- **제외 확정**: 알리오(경영공시), 1365 기부포털(기부처 조회), 서울혁신파크(폐쇄), LG상록재단(공모 없음), 서울시마을공동체종합지원센터(**도메인 탈취됨**).

## 2. 대상별 우선 소스 매트릭스

| 신분 | 전국 | 서울 | 경기 | 제주 |
|---|---|---|---|---|
| 개인(청년) | 온통청년 API, 위비티, 링커리어, 씽굿 | 청년몽땅정보통 | 경기청년포털 | 제주청년센터 |
| 개인(예술·창작) | 아르코, 예술경영지원센터, 예술인복지재단 | 서울문화재단 | 경기문화재단, 경기콘텐츠진흥원 | 제주문화예술재단(기술 미확인), 제주콘텐츠진흥원 |
| 개인(교육·훈련) | 고용24(진입점 미확정), 늘배움, K-MOOC | 서울시평생학습포털 | 경기도평생교육진흥원 | 제주평생교육다모아 |
| 모임(비법인) | 행안부 마을공동체 공모, 아름다운재단 | (마을센터 체계 붕괴, 자치구 개별) | 경기도마을공동체지원센터 | 제주마을만들기센터, 제주소통협력센터 |
| 비영리단체 | 사회복지공동모금회, 아름다운재단, 한국여성재단, 더나은미래 | 서울시공익활동지원센터(기술 미확인), 서울시복지재단 | 경기도공익활동지원센터, 경기복지재단 | 제주공익활동지원센터(robots), 공동모금회 제주지회(미확인) |
| 협동조합·사회적기업 | 사회적기업진흥원(robots 차단), coop.go.kr(URL 재확인) | 서울시사회적경제지원센터 | 경기도사회적경제원 | 제주사회적경제지원센터 |

## 3. 1순위: 자동 수집 가능 (검증됨)

| # | 소스 | 목록 URL | 대상 | 유형 | 기술 메모 |
|---|---|---|---|---|---|
| 1 | 온통청년 | youthcenter.go.kr/youthPolicy/ythPlcyTotalSearch | 청년 개인 | 정책·지원사업 | SSR 확인(480KB). **오픈API 있음**(인증키 필요, XML). 스킬에서는 API 우선 |
| 2 | 위비티 | wevity.com/?c=find&s=1&gub=1&gp={N} | 개인 | 공모전·지원사업·장학 | SSR, robots 전면 허용, `gp` 페이지 |
| 3 | 링커리어 | linkareer.com/list/activity | 개인 | 대외활동·교육·공모전 | robots 허용, 목록 텍스트 추출 정상 |
| 4 | 씽굿 | thinkcontest.com | 개인 | 공모전·교육 | robots 허용. 목록 URL 구조 미확인 |
| 5 | 더나은미래 | futurechosun.com/feed | 비영리·소셜벤처 | 큐레이션(보도) | **RSS 확인됨**. 가장 쉬운 소스 |
| 6 | 예술경영지원센터 | gokams.or.kr/02_apply/introduction_nt.aspx | 예술 개인·단체 | 지원사업 | ASP.NET, `page=` 파라미터. 기업마당에도 동시 게재 |
| 7 | 서울시사회적경제지원센터 | sehub.net/archives/category/alarm/opencat , /camevent | 사회적경제·개인 | 지정공고·교육 | SSR, 당일 게시 확인. 폐지설은 사실 아님 |
| 8 | 서울문화재단 | sfac.or.kr/participation/participation/artspace_project.do | 예술 개인·단체 | 공모 | SSR, 페이지 1~10. 마감일은 상세에서 |
| 9 | 청년몽땅정보통 | youth.seoul.go.kr/bbs/list.do?key=2303300002 | 청년 개인 | 모집공고 | SSR |
| 10 | 경기도사회적경제원 | gsic.or.kr/home/kor/M232113179/business/apply/index.do | 협동조합·사회적기업 | 교육·지원사업 | 카드형 SSR. 구 gsec.or.kr과 관계 미확인 |
| 11 | 경기도마을공동체지원센터 | ggmaeul.or.kr/base/board/list?boardManagementNo=51&menuLevel=2&menuNo=78 | 마을모임·청년공동체 | 공모 | SSR, `page=`. 시·군 지원사업 게시판(No=52) 별도 |
| 12 | 경기청년포털 | youth.gg.go.kr/gg/intro/notice.do | 청년 개인 | 공고·모집 | SSR, `article.offset=N`(10단위) |
| 13 | 경기복지재단 | ggwf.gg.go.kr/archives/category/gfnews/gfnotice | 복지 종사자·시설 | 교육·공모 | 워드프레스 계열, 152페이지, RSS 가능성 |
| 14 | 경기도일자리재단 | gjf.or.kr/main/pst/list.do?pst_id=notice_ap | 개인 | 교육·모집 | SSR, 17페이지 |
| 15 | 경기콘텐츠진흥원 | gcon.or.kr/gcon/business/gconNotice/list.do?menuNo=200061 | 개인 창작자·팀 | 공모 | SSR이나 페이지 이동이 JS 함수. GET 파라미터 재확인 |
| 16 | 경기도공익활동지원센터 | gggongik.or.kr/page/centernews/centernotice.html | 공익단체 | 공모·모집 | curl 200(43KB, 목록 마커 128) → SSR로 판단 |
| 17 | 경기문화재단 | ggcf.kr/boards/businessNotices/articles | 예술 개인·단체 | 공모 | curl 200(79KB) → 첫 페이지 SSR. "더보기" 추가 로딩은 XHR 확인 필요 |
| 18 | 제주사회적경제지원센터 | jejuhub.org/user/news/support | 사회적경제·협동조합 | 공모·교육 | SSR, 페이지 1~5 |
| 19 | 제주청년센터 | jejuyouth.com/bbs/board.php?bo_table=1_2_2_1&page={N} | 청년 + **타기관 큐레이션** | 공모·지원·교육 | 그누보드 SSR, 거의 매일 갱신. 제주 허브 소스 |
| 20 | 제주소통협력센터 | jejusotong.kr/bbs/board.php?bo_table=4_4_1_1 | 개인·소셜벤처·마을 | 공모·모집(큐레이션) | 그누보드 SSR, 진행상태 배지 |
| 21 | 제주콘텐츠진흥원 | ofjeju.kr/communication/notifications.htm | 창작자·교육단체 | 기관/교육/타기관공고 | SSR, 분류 컬럼 있음 |
| 22 | 제주경제통상진흥원 | jba.or.kr/bbs/board.php?bo_table=2_1_1_1 | 창업자·소상공인·협동조합 | 사업공고·교육 | 그누보드 SSR, 51페이지 |
| 23 | 제주여성가족연구원 | jewfri.kr/index.php/contents/notice/jewnotice/notice?page={N} | 도민 개인 | 연구과제 공모 | SSR. 정책연구 용역 성격이라 필터 필요 |
| 24 | 제주마을만들기종합지원센터 | jejumaeul.or.kr | 마을·활동가 | 공모·교육 | WebFetch는 403이나 **브라우저 UA curl은 200(795KB)** → UA 지정하면 수집 가능. 게시판 URL 미확인 |
| 25 | 서울시복지재단 | welfare.seoul.kr/web/contents/communication1-1.do?schBdcode=_swf_news03 | 복지시설·단체 | 공모·채용 | SSR 추정, 카테고리 코드로 구분 |

공모전 포털은 위비티·씽굿·링커리어 셋이면 충분. 올콘·콘테스트코리아는 중복, 캠퍼스픽은 403, 대티즌은 noindex.

## 4. 2순위: 내용은 핵심이나 기술 장벽 있음

| 소스 | 문제 | 대응안 |
|---|---|---|
| 한국사회적기업진흥원 socialenterprise.or.kr | **robots.txt `User-agent: * Disallow: /`** (검색봇도 루트만 허용). 조사된 게시판 URL은 404 | 자동 수집 금지. 사용자 수동 확인 안내 + 기업마당·경기사회적경제원·sehub 등의 재게시분으로 보완 |
| 협동조합 포털 coop.go.kr | 조사된 게시판 URL(menu_no=2038)이 "게시판 정보 없음"으로 리다이렉트 | 브라우저로 실제 메뉴 URL 재확인. 교육 공지 위주라 우선순위 중 |
| 사회복지공동모금회 chest.or.kr | 메인 정상, `/bbs/{1000~1013}/initPostList.do` 게시판 다수 확인. 1004는 500 오류 | 각 bbs 번호가 어떤 게시판인지 브라우저로 매핑. 배분신청은 proposal.chest.or.kr 별도 |
| 아르코 arko.or.kr | `/content/5520`은 SSR(82KB). `/board/list/*`는 빈 껍데기(JS) | 공모 목록의 실제 XHR 엔드포인트 확인. 신청은 ncas.or.kr |
| 서울시공익활동지원센터 seoulpa.kr | `/` → `/welcome.do` meta refresh. 구 snpo.kr은 아직 살아 있음(32KB) | 브라우저로 게시판 URL 확인. NPO 대상 큐레이션이라 확인 가치 높음 |
| 제주도청 고시공고 jeju.go.kr/news/news/law.htm | curl 200(165KB)이나 목록 항목이 정적 HTML에 없음(JS 로드). **robots.txt가 `/news/` 불허** | robots 존중 → 자동 수집 제외. 제주청년센터·소통협력센터 큐레이션으로 대체 |
| 제주공익활동지원센터 jeju.go.kr/jejunpo | 같은 도메인 robots 불허 | 위와 동일 대체 |
| 제주문화예술재단 jfac.kr | curl 200이나 975바이트(JS 앱) | XHR 엔드포인트 확인 또는 수동 |
| 제주테크노파크 jejutp.or.kr | SPA(템플릿 변수만 반환) | XHR 확인 또는 제외(기업 위주) |
| 경기도자원봉사센터 ggvc.or.kr | JS 네비게이션, 목록 미로드 | XHR 확인. 단체공모(최대 600만원) 있어 가치 있음 |
| 고용24(HRD-Net 통합) work24.go.kr | 훈련과정 목록 진입 URL 미확정 | 브라우저 확인. 개인 교육에서 가장 큰 소스 |
| 보조금24 → 혜택알리미 plus.gov.kr/portal/benefitV2 | robots는 이 경로 허용. 로그인 기반 개인 매칭 | 크롤링보다 "사용자 직접 확인" 안내용 |
| 서울시 고시공고 seoul.go.kr/news/news_notice.do | SSR(88KB), `curPage=N&bbsNo=277`. robots는 `Disallow: /` 후 Allow 목록. `/news` 허용 여부 재확인 | 허용이면 키워드 필터(모집·공모·지원·교육)로 수집 |
| 경기도 고시공고 gg.go.kr/bbs/board.do?bsIdx=469 | SSR. robots는 `/site/ /common/` 등만 불허 → `/bbs/` 허용으로 보임 | 키워드 필터로 수집 |

## 5. 3순위: 참고·보조

- 아름다운재단(beautifulfund.org/tag/지원사업/ 워드프레스, RSS 가능성), 한국여성재단(womenfund.or.kr, 단체 운영비 지원 있음), 브라이언임팩트, 카카오임팩트(JS 가능성), 다음세대재단. 민간재단은 공고 수가 적어 **RSS 또는 월 1회 점검**으로 충분.
- 행안부 mois.go.kr 게시판(청년마을·마을공동체 연례 공모). 전자정부 게시판, 연 1~2회.
- 한국장학재단 민간장학금 게시판, K-MOOC, 늘배움(all.go.kr), GSEEK. 교육 콘텐츠라 "지원사업" 성격 약함.
- 서울50플러스재단, 서울시가족센터, 경기도여성가족재단(gwff.kr, SSR), 경기도평생교육진흥원(gill.or.kr, SSR). 특정 신분에만 유용.
- 제주의소리 "제주시" 코너. 지자체 협찬 콘텐츠라 출처 표기 시 원문 재확인 필요.
- 자치구·시군: 서울 성북구(sb.go.kr/www/selectEminwonList.do, eminwon 계열 SSR), 마포구(mapo.go.kr/site/main/nPortal/list), 제주시(eminwon.jejusi.go.kr), 경기 시군은 새올 계열(`saeol/gosi/view.do`) 다수. **eminwon/새올 어댑터 하나로 여러 지자체를 덮을 가능성**. 단, 서귀포시 robots는 일반 크롤러 차단.
- 공공데이터포털 data.go.kr: 부처별 "공모사업 현황" 파일데이터가 흩어져 있음. 통합 API는 없음.
- 서울 열린데이터광장 고시공고 API(OA-2482)는 종료예정. 은평구 고시공고 데이터셋(OA-22373)은 존재.
- 경기데이터드림: 고시공고 데이터셋 검색 0건.

## 6. 반드시 알아둘 위험

1. **seoulmaeul.org(서울시마을공동체종합지원센터) 도메인이 탈취됨.** curl 결과 제목이 도박 사이트 광고. 어떤 문서에도 링크하지 말 것. 자치구 마을센터 25곳 중 16곳 폐쇄 보도.
2. socialenterprise.or.kr, jeju.go.kr, seogwipo.go.kr은 robots.txt가 일반 크롤러를 막음 → 기존 스킬 원칙대로 "수동 확인" 처리.
3. 공모전 포털(위비티 등)은 민간 상업 사이트. 약관 확인 후 요청 간격 넉넉히.
4. 지자체 협찬 언론 콘텐츠, 운영주체 불명 민간 통합 사이트(seoulalarm.com)는 1차 출처로 쓰지 않음.

## 7. 새 스킬 설계에 주는 시사점

- **프로필 축**이 기존 ir-search와 다름: 신분(개인 / 모임 / 비영리법인 / 협동조합·사회적기업) × 지역(서울·경기·제주) × 분야(문화예술·청년·복지·마을·사회적경제·교육) × 원하는 것(교육 / 사업비 / 공간·활동비 / 상금).
- **어댑터 재사용**: 그누보드(`bbs/board.php?bo_table=X&page=N`) 3곳(제주청년센터·소통협력센터·경제통상진흥원), 워드프레스 archives 계열 3곳, eminwon/새올 계열 지자체, 경기 산하기관 공통 `base/board/list?boardManagementNo=` 2곳(마을센터·여성가족재단). 어댑터 5~6종이면 1순위 25곳 대부분을 덮음.
- **허브형 소스 우선**: 제주는 청년센터+소통협력센터+콘텐츠진흥원 3곳이 도내 타기관 공고를 큐레이션하므로 이 3곳으로 시작하면 도청 robots 문제를 우회하지 않고도 커버리지 확보.
- **API·RSS 먼저**: 온통청년 API, 더나은미래 RSS, 워드프레스 계열 `/feed`.
- 기존 `scope_plan.py`의 소스 상태(verified / candidate / manual) 체계를 그대로 쓰면 됨.

## 8. 후속 확인 목록 (브라우저 필요)

- [ ] 서울시공익활동지원센터 seoulpa.kr 게시판 URL·렌더링
- [ ] coop.go.kr 실제 공지·교육 게시판 URL
- [ ] chest.or.kr `/bbs/{번호}` 게시판 이름 매핑, proposal.chest.or.kr 공고 목록
- [ ] 아르코 공모 목록 XHR, jfac.kr XHR
- [ ] 고용24 훈련과정 목록 URL
- [ ] seoul.go.kr robots의 `/news` 허용 여부
- [ ] 경기콘텐츠진흥원 `pageIndex` GET 동작, 경기문화재단 "더보기" XHR
- [ ] jejumaeul.or.kr 게시판 URL(UA 지정 후)
- [ ] 은평구 고시공고 URL, 경기 시군 새올 어댑터 샘플 3곳

---
원시 조사 파일(에이전트 5개 산출물)은 `docs/research/raw/` 에 함께 보관.
