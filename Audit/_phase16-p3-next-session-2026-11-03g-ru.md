# Промпт для новой сессии — Phase 16 P3.1

```text
Продолжаем Phase 16 P3.1 в D:\Rhino\3dsmax-arch-nurbs-ultimate-skill.

Сначала прочитай:
1. Начало CHECKPOINT.md и AGENTS.md; PLAN.md §4.0d.
2. Audit/_phase16-p3-resume-2026-11-03g.md — главный новый handoff.
3. Audit/_phase16-p3-resume-2026-11-03f.md и
   Audit/_phase16-p3-contract-2026-11-02e.md.
4. Все актуальные отчёты и post-publication запись 03g, на которые ссылается
   CHECKPOINT 03g, с точными final hashes после остановки всех авторов.
5. Audit/_phase16-p3-live-post-operator-2026-11-03g.json;
   Audit/_phase16-p3-witness-local-calibration-2026-11-03g.json;
   Audit/phase16-p3-main-probes-2026-11-03g/layer-reference-identity-result.json;
   Audit/phase16-p3-main-probes-2026-11-03g/layer-empty-observer-result.json.
6. Audit/phase16-p3-main-probes-2026-11-03g/DO-NOT-RUN-POPULATED-DRAFT.md;
   metadata, cleanup-model, lease и layer independent reports 03g.

Сохраняй ВСЕ имеющиеся изменения, новые файлы, опубликованные пары и evidence.
Не делай commit/reset/checkout/clean. Не запускай installer и не обновляй .skill
или глобальные копии. Материалы и экспорт вне scope. Не выполняй reset/save Max,
очистку dirty flag или AutoBackup. Historical input-lock/FINAL2 и Main01–03
остаются неизменными.

Максимально экономь контекст: делегируй независимые offline-задачи субагентам,
с явным непересекающимся владением и короткими отчётами. Только main выполняет
живые Max вызовы — коротко и последовательно. Моё разрешение на необходимую
работу в Max действует; я снял ограничения read-only. Не возвращай унаследованный
blanket ban и не спрашивай повторно общее разрешение. Сохраняй обычную безопасность:
fresh admission, exact current-attempt ownership, независимо удержанные refs,
никаких удалений чужого/неидентифицированного, fail closed на неизвестное.

Первое действие main в Max — новая read-only инспекция: полный bounded census и
узлы, selection, path/name, units/scale, dirty flag, layers, точный старый Main03
registry key с real/bogus controls. Последний postcheck в прежней сессии: 0 объектов,
0 selection, unnamed, mm/1.0, dirty=true, один пустой слой 0, Main03 key absent.
Но это лишь прошлое наблюдение, не обещание текущего состояния; не сбрасывай dirty.

Остаток controller probe: ранее наблюдался Box001 с Shell. Я выбрал вариант, что
сам его узнаю и удалю вручную; следующий census оказался пустым. Точное
промежуточное действие main не наблюдал. Прежний локальный witness потерян; имя,
handle и хронология не дают authority для удаления любых возможных новых объектов.
Не восстанавливай/rearm/retry Main01–03 и не заявляй непрерывность прежнего
POISONED witness после смены процесса.

P0/P1 и ограниченная offline-приёмка P2 остаются. P3.1 NOT ACCEPTED. Исторический
FINAL2: 7/7 suites, 250 методов OK, 307 stable entries на ПРЕЖНИХ bytes. Это не
результаты текущего runtime. Main03 действительно failed на LayerProperties ->
MaxObject, cleaned0 и POISONED; безопасный отказ повтора не clean NOOP. Новая
authentic wall pair не публиковалась/не запускалась. Нет принятого F01 и трёх
настоящих clean NOOP. Original 21 P2 skips, F02–F08, integration/poly-QA остаются.

После остановки авторов проверь текущий runtime SHA в CHECKPOINT/03g record и
независимо оцени все его изменения. Последний hash:
ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2;
авторские offline результаты по нему: 15/15 data/model, 21/21 protection,
legacy 42 run / 1 FAIL. Это не полный frozen run, не проверка Max и не
независимая semantic acceptance. Сохраняй executable INCOMPLETE_PRECREATE и
unconditional INCOMPLETE_REPLAY; не снимай их ради F01/тестов. Не возвращай
handle-only deletion/recovery ради старого assertion; unconditional retention
тоже не выдавай за реализованный safe-case cleanup. Unknown/read error никогда не
равен equality. Дешёвые unsupported-state проверки должны предшествовать evaluation.

Новые результаты main:
- локальная одно-вызовная calibration показала alias/fresh equal-payload struct и
  array distinction и detached string copy. Это НЕ persistent cross-call witness;
- empty layer backing: 33 interface / 34 backing включая degrade / 18 nested GI;
  rootScene != rootNode, Scene dependent == rootScene. LayerManager — Interface,
  getHandleByAnim на нём реально throws; Layer_Manager RefTarget иной. Не
  whitelisting по классу/имени/handle и не получай исходный witness из registry;
- p31 offline candidate распарсился внутри wrapper и только частичные helper reads
  исполнялись на существующем пустом слое. Detached GI/degrade edits — только
  локальные данные. p31ReadOnce/ObserveTwice/membership/dependencies, второй
  layer_reader.ms, полный production baseline и replay НЕ проверены;
- Python cleanup model 32/32 использует synthetic closed-world assumptions, не
  доказывает Max graph/disposal/ownership.

Post-publication record Audit/_phase16-p3-post-publication-2026-11-03g.json,
SHA 17b8767b371f76df5cba2d365c3e0f8bf695d0a36f8dc9019d0f7b969bd48a99,
отдельно фиксирует 0 missing/0 unexpected drift при non-atomic сравнении с 03f.
Его запись сделана до финального обновления CHECKPOINT/handoff/этого промпта;
не трактуй ожидаемый post-record documentation drift как порчу данных — проверь
файл заключительной статусной сверки и его точные hashes.

НЕ ЗАПУСКАЙ Audit/phase16-p3-main-probes-2026-11-03g/make-layer-populated-reader.py
или его output — это неисполненный и небезопасный черновик, см. DO-NOT-RUN.
В частности, он находит purported manager по классу в том же dependency list,
подменяет rootNode на rootScene и не доказывает безопасный cleanup. Сохрани файл.

Последовательность работ: сначала независимый source review runtime и текущих
результатов; затем bounded layer reader с exact отдельно удержанными backing/scene/
manager witnesses и всеми 33/34/18 полями; mandatory native/specified-normal
metadata, controller descendants, permitted dependency graph, pre-evaluation
ordering и safe exact cleanup; отдельно persistent independent lease/witness
без reacquire из registry. Для каждого нового live probe сохраняй exact direct
refs и handles до следующего risky API, separately retained witness и stage markers.
При timeout/ошибке/identity ambiguity — INCOMPLETE, никакого автоматического retry.

Только после исправлений остановить всех авторов, freeze полную closure, выполнить
полный recorder в НОВОМ каталоге и разобрать raw FAIL/SKIP/xfail/drift; затем
создать новую genuine pair и actual новый registry key (новый каталог/nonce сами
по себе ключ не меняют), explicit independently checked lease и выполнить именно
новый emitted .ms. Независимо измерить direction, inner face, openings/through-void,
area, volume, topology, bounds, thickness, census и stack; потом 3 настоящих clean
NOOP и targeted edit/collision/cleanup negatives. Actual predelete-grid и native
evaluated polygon gaps не заменять predictions, triangle groups, восстановленным
grid или synthetic output echoes.

Проверяй actual exceptions, __MCP_MS_ERR__, ERROR/cleanup outcomes, а не только
transport ok=true. Обновляй CHECKPOINT с точными hashes и честным PASS / FAIL /
INCOMPLETE. Не объявляй P3.1 завершённым по offline-тестам, безопасному отказу,
одной эмиссии или узкой калибровке.
```
