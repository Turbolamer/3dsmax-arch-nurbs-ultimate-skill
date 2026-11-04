# Промпт для новой сессии — Phase 16 P3.1 / 2026-11-03f

Продолжаем Phase 16 P3.1 в `D:\Rhino\3dsmax-arch-nurbs-ultimate-skill`.

Сначала прочитай:
1. Начало CHECKPOINT.md и AGENTS.md; PLAN.md §4.0d.
2. `Audit/_phase16-p3-resume-2026-11-03f.md` — новый основной handoff.
3. `Audit/_phase16-p3-contract-2026-11-02e.md`.
4. `Audit/phase16-p3-main-probes-2026-11-03f/controller-graph-v2-residue.json`.
5. `Audit/phase16-p3-controller-incident-2026-11-03f/report.md`.
6. `Audit/phase16-p3-runtime-hardening-2026-11-03f/PRECREATE-GATE-REPORT.md`.
7. `Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md`.
8. `Audit/_phase16-p3-post-publication-2026-11-03f.json`, если уже опубликован;
   его отсутствие не заменять выдуманным evidence — сверить handoff с файлами.

Сохрани ВСЕ изменения, новые файлы, old pairs и evidence. Не делай
commit/reset/checkout/clean, installer/.skill/global-copy update, reset/save,
dirty-flag clearing или AutoBackup. Материалы и экспорт вне scope.
Максимально делегируй независимую offline-работу с явным непересекающимся
владением и короткими отчётами. Только main выполняет live Max, коротко и
последовательно. Разрешение пользователя на необходимую работу в Max действует:
не возвращай старый blanket ban и не спрашивай повторно то же разрешение.

**КРИТИЧНО: последняя сцена НЕ пустая.** Отдельный controller probe main
вернул actual ERROR `Mesh operation on non-mesh: Box`, cleanup refused
`lost exact Shell`. Read-only наблюдал один возможный временный остаток:
`Box001`, node handle `2024P`, Shell handle `2044P`, selection0, unnamed mm/1,
dirty=false, слой0. Прежние fileIn-local node/Shell refs не сохранены независимо
между вызовами. Имя, census и recovered handle не являются authority на удаление.
Не удаляй/подхватывай/ретрай автоматически; нужен ручной осмотр пользователем и,
если он сам уверенно идентифицирует временный остаток, ручное удаление. Если
есть сомнение — оставить. Это ownership stop, не отмена общего разрешения Max.

Первое Max-действие — НОВАЯ read-only инспекция: все nodes/census, selection,
path/name, units/scale, dirty, layers, exact old Main03 key. Даже если пользователь
сказал, что очистил временный остаток, перепроверь, не предполагай ноль.
Не опирайся на старые нулевые postchecks, выполненные до controller incident.

Статус:
- P0/P1 и ограниченная offline-приёмка P2 действуют. **P3.1 NOT ACCEPTED.**
- Исторический FINAL2 7/7 suites, 250 методов, 307 stable entries сохранён.
  Это старый snapshot, НЕ результаты текущих изменённых исходников.
- Main03 раньше реально failed на LayerProperties->MaxObject, cleaned0,
  POISONED и безопасный refused repeat. При новом входе процесс Max уже был
  последующим (PID9012, start2026-11-03T17:27:21.875Z), key отсутствовал.
  Не заявляй непрерывность прежнего witness, не rearm/recreate Main03.
- Из четырёх P3 sources изменён runtime, current SHA-256:
  `3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf`.
  Старые bytes и intermediate hardening сохранены отдельно; не откатывать.
- Runtime сохраняет `INCOMPLETE_REPLAY` и временный executable
  `INCOMPLETE_PRECREATE` до BUILDING/создания. Это не полноценное исправление;
  не снимать guards для PASS. Safe-case cleanup пока не реализован полностью.
- Main повторил protective21 OK; unchanged runtime42 с **1 FAIL** на требовании
  старого handle recovery/delete; independent layer/replay14 с **7 failed
  subtests**; lease-model19 OK; measurement-diagnostics13 OK. Не скрывать failures,
  не возвращать опасный fallback ради теста. Полного нового frozen run ещё нет.
- Bounded layer probes реально показали backing `layerAsRefTarg` identity,
  distinct/repeat, lock/GI/name edits и node reassignment; guarded cleanup тогда
  прошёл. Данные в `Audit/phase16-p3-main-probes-2026-11-03f/`.
  Интерфейс33/backing34(`degrade`)/GI18 — ничего не опускать. Не production
  baseline и не универсальная полнота metadata.
- VData11 live control прошёл в узком объёме. EData3 actual ERROR/INCOMPLETE,
  точная операция не локализована. Новые EData candidates НЕ выполнены.
- Controller candidate failed; полного F01 и трёх clean NOOP нет. Новая genuine
  pair не публиковалась и не запускалась.

Следующая работа после разрешения ownership stop:
1. Изучить bounded layer reader candidate/handoff под
   `Audit/phase16-p3-layer-reader-2026-11-03f/`, если создан; не считать его
   Max-verified или внедрённым только по отчёту.
2. Завершить доказуемые native/specified-normal, controller descendants,
   разрешённые dependency graph и safe exact cleanup, cheap guards ДО evaluation.
   Не опускать поля, не считать unknown/read error равенством.
3. Откалибровать независимый persistent witness protocol; candidate в
   `Audit/phase16-p3-lease-next-2026-11-03f/` disabled/unexecuted, не root-of-trust.
   Новые probes должны сохранять точные refs/handles в independently retained
   witness сразу после constructor/attach и до следующего рискованного вызова.
   Не повторять ошибку локальных refs после `fileIn`; stage markers на каждый API.
4. После реальных исправлений остановить всех авторов, заморозить closure,
   выполнить полный recorder в новом каталоге, разобрать raw FAIL/skip/errors/drift.
   Затем НОВАЯ authentic emitted pair и explicit checked lease с новым actual key;
   Main01–03 не трогать. Новая папка/nonce сами по себе key не меняют.
5. Выполнить именно новый emitted .ms, реально измерить F01 direction/inner face/
   openings-through-void/area/volume/topology/bounds/thickness/census/stack;
   actual predelete-grid/native polygon gaps не заменять predictions/triangle
   groups. Потом три настоящих NOOP и edit/collision/cleanup negatives.

Original 21 P2 skips не закрыты; F02–F08, integration/poly-QA — отдельные гейты.
Исторический input-lock с прежним contract hash не переписывать. Все старые
immutable manifests, published pairs и failure evidence оставить как есть.
Проверяй transport errors, `__MCP_MS_ERR__`, actual ERROR и cleanup outcomes,
а не только `ok=true`. Обновляй CHECKPOINT честно с exact hashes и различением
PASS / FAIL / INCOMPLETE. Не запускать installer и не объявлять этап завершённым.
