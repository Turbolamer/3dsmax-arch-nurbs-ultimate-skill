# Phase 16 P3.1 — handoff 2026-11-03g

## Статус и границы

**P3.1 NOT ACCEPTED.** P0/P1 и ограниченная offline-приёмка P2 остаются в силе.
Пользователь попросил дождаться субагентов, зафиксировать результаты и остановиться
из-за заполненного контекста. После этого запроса main не выполняет новых Max-вызовов,
не запускает пробы/финальный recorder и не продолжает реализацию. Новая сессия
должна самостоятельно заново проверить актуальные состояние и хеши.

Пользователь повторно сказал: «делай в 3d max все что нужно, ограничения read only
сняты». Не восстанавливать унаследованный blanket ban и не спрашивать повторно то же
общее разрешение. Это не отменяет проверку ownership, свежий scene admission,
маленькие последовательные main-only вызовы и отказ при неизвестной идентичности.
Материалы и экспорт вне scope. Не делать commit/reset/checkout/clean, не запускать
installer, не обновлять `.skill` и глобальные копии. Не reset/save Max, не очищать
dirty flag и не обращаться к AutoBackup. Сохранять все существующие файлы,
незакоммиченные/новые данные, опубликованные пары и immutable evidence.

## Scene: historical residue и последнее наблюдение

Первая read-only инспекция в этой сессии увидела **1 выбранный Box001** с одним
Shell, в отличие от нулевого selection при завершении предыдущей сессии. Запись:
`Audit/_phase16-p3-live-entry-2026-11-03g.json`. Имя и handles не считались
доказательством происхождения или authority для удаления. В основном предыдущем
инциденте точная выбросившая операция не доказана: `update n` — гипотеза;
cleanup guard обнаружил отсутствие Shell ref **или** handle, не определив что
именно. Сохранять `Audit/phase16-p3-controller-incident-2026-11-03f/report.md`.

Пользователь выбрал вариант, что он распознаёт временный объект и удалит его
вручную. Последующее read-only наблюдение main:
`Audit/_phase16-p3-live-post-operator-2026-11-03g.json` — **0 объектов,
0 выделенных, unnamed path/name, millimeters/1.0, dirty=true, один пустой слой 0,
Main03 key отсутствует**. Само промежуточное ручное действие main не наблюдал.
Dirty flag не очищался и не доказывает чистую историю. Переход пользователя
разрешил прежний ownership stop для этой видимой ситуации, но не дал автоматической
authority для любых иных объектов. Следующий сеанс начинает с нового bounded
read-only census и scene/state/selection/units/dirty/layers/старого Main03 key;
результат этого сеанса не гарантия состояния после перерыва.

Последний полный отдельный Max postcheck после всех live-калибровок:
`Audit/phase16-p3-main-probes-2026-11-03g/layer-empty-observer-result.json` —
0 объектов/selection, unnamed mm/1, dirty=true, слой 0 пуст и backing 48P,
Main03 key absent. В текущей сессии main не создавал/не удалял сценовые объекты,
не менял слои, registry или selection, не сохранял/reset Max, не очищал dirty.
Локальные переменные/structs/массивы probe изменялись только в его локальном scope.
Не заявлять, что прежний Main03 POISONED witness пережил смену процесса; не
воссоздавать/rearm/retry Main01–03 и не считать их безопасным NOOP.

## Новые live-калибровки — только частичные результаты

1. `Audit/_phase16-p3-witness-local-calibration-2026-11-03g.json`: main вызвал
   `Audit/phase16-p3-lease-next-2026-11-03f/01-local-calibration.ms`, SHA
   `4146bfd9bde17cdb8096f0e968092288c0f2e41663fa628f8a1586626fc9f39b`.
   В одном local вызове alias и отдельно созданные equal-payload struct/array
   различались; перестановка values определялась; copy строки пережила изменение
   исходной строки. Никаких новых global/node. **Это не cross-call persistent
   witness**, не доказательство независимого lease, не F01/NOOP. Хеш перед
   fileIn снимался вне Max, read-hold не применялся.
2. `Audit/phase16-p3-main-probes-2026-11-03g/layer-zero-readonly-result.json`:
   existing default backing exact ref/handle roundtrip; counts interface 33,
   backing 34 (`degrade` только backing), nested GI 18. Empty backing dependencies
   содержали `Layer_Manager` и `Scene`; ни один не был `rootNode`. Это не полная
   graph-классификация и не доказательство populated layer.
3. `Audit/phase16-p3-main-probes-2026-11-03g/layer-reference-identity-result.json`:
   `rootNode` (`MAXRootNode`) != `rootScene` (`Scene`); второй exact равен Scene
   dependent. Сам `LayerManager` имеет класс `Interface`, не равен обоим
   dependents и при `getHandleByAnim` вернул **реальную ошибку** `Unable to
   convert: <Interface:LayerManager> to type: MaxObject`. `Layer_Manager`
   ReferenceTarget отдельно round-tripped handle, но независимый источник его
   identity/роль и lifecycle не доказаны. Не превращать класс/имя/handle или
   повторно прочитанный dependency список в authority. Оба layer-кандидата
   ожидают `rootNode` в deps; на empty evidence это предположение не выполняется;
   полный candidate на populated layer ещё не вызывался.
   Independent disabled design:
   `Audit/phase16-p3-layer-identity-design-2026-11-03g/REPORT.md`. На основании
   имеющихся свидетельств отдельный независимый источник и активный anchor для
   manager target не найдены; `.ms.disabled` — псевдокод, не запускать как probe.
4. `Audit/phase16-p3-main-probes-2026-11-03g/layer-empty-observer-result.json`:
   один candidate `layer_reader_p31_offline.ms`, SHA
   `5b16d1d648a2cdefd9b98440ad4fb4ae1ca1a1c3dde0ecf47990dfe44a8ad4f2`,
   распарсился как часть нового wrapper SHA
   `2dcd5550d5c2b4f2bdf9d0779ea09a70ac614f3445390703ba4b10745c8386bd`.
   Только частичные profile/property/GI/typed-detach функции на existing empty
   layer отработали: repeated 33/34/18; неправильный backing, bogus profile и
   undefined Float отказали. GI/degrade mutations были на **отсоединённых
   массивах**, не на реальном слое. `p31ReadOnce`, `p31ObserveTwice`, membership
   и dependency helpers не вызваны. Второй `layer_reader.ms` с SHA `0dc718…`
   не выполнялся. Нет production integration/comparator, baseline или replay.
   Автономный wrapper запускался без file-hold; внешние hashes до/после совпали.

Independent source audit `Audit/phase16-p3-layer-independent-2026-11-03g/REPORT.md`
сохраняет выводы своего более раннего по материалам обзора: автор сообщает
14/14 + 14/14 исходных tests и 17/17 независимых offline checks, а также
mutation controls, не пойманные исходными suites. **Позднее/параллельно main**
получил перечисленную выше узкую live калибровку частичных функций P31 (не
полный reader). Поэтому отсутствие любого parse/fileIn в §§F-06/F-10 аудита
больше нельзя читать как актуальное для точно указанного wrapper: он реально
парсился и часть функций выполнялась, empty и single-observed-member
`getNumNodes()` ранее по `03g` записям вернул 0 и 1. Это не проверка поведения
`getNumNodes()` при controlled изменении membership, не полноценный candidate
test, не member/dependency graph calibration и не production PASS. Другие
finding-и — отсутствие независимого manager identity, отсутствие post-read
witness revalidation, source/manager/ref/resource gaps — остаются открытыми.

## Запрещённый незаконченный черновик main

`Audit/phase16-p3-main-probes-2026-11-03g/make-layer-populated-reader.py` SHA
`304b32e2873cdb2b597bed3861526aefba3c00bfd55b873bfe41425d7d97fdb7` начал
писаться до пользовательской остановки. **Не запускать генератор и не запускать
его возможный output:** его нельзя считать безопасной пробой. Отдельное предупреждение
`Audit/phase16-p3-main-probes-2026-11-03g/DO-NOT-RUN-POPULATED-DRAFT.md`:
получает manager из того же deps по классу, неверно передаёт rootScene вместо
rootNode, содержит недостаточно защищённый exact cleanup и не держит независимый
original witness. На момент остановки генератор не запускался,
`layer-populated-reader.ms` отсутствовал. Сохранить черновик как evidence; его
docstring описывает намерение, а не доказанную безопасность.
Независимая проверка `Audit/phase16-p3-draft-unsafe-review-2026-11-03g/REPORT.md`
добавляет риск повторения формы прежней parse error, неполную stage-aware очистку,
отсутствие pre-delete dependency/context guards и ограничения диагностики; это
source risks, не новый Max-инцидент.

## Offline / acceptance границы

После завершения всех авторов main считал runtime и исходный diff, проверил
сырые summaries и SHA логов из `Audit/phase16-p3-data-hardening-2026-11-03g/`:

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12 scripts/wall_surface_inputs.py
ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2 scripts/wall_surface_runtime.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
```

Изменён только runtime: narrow VData/EData source hardening с strict count,
support и scalar/finite guards, tagged detached values и zero-loop guards.
До правки snapshot SHA `3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf`
сохранён в `Audit/phase16-p3-data-hardening-2026-11-03g/wall_surface_runtime.pre-edit.py`.
На новых bytes автор зарегистрировал 15/15 offline model/source tests и 21/21
protective tests; unchanged legacy suite — 42 run, **1 FAIL**, тот же старый
cleanup assertion. Raw logs и `v3-results.json` сохраняют всё, recorder этого
ограниченного прогона вышел 1. MAXScript этого runtime не парсился и не
выполнялся; полная независимая semantic review hardening и полный frozen recorder
по-прежнему нужны. `INCOMPLETE_PRECREATE` / `INCOMPLETE_REPLAY` остались, не
делать из тестов clean replay/cleanup и не возвращать опасную handle ветку.

Historical immutable FINAL2 — прежние bytes: 7/7 suites, 250 методов OK,
307 stable entries; это не тест текущего runtime. Main03 фактически failed на
`LayerProperties -> MaxObject`, был очищен и POISONED; безопасный отказ повтора
не clean NOOP. Новая authentic emitted wall pair не создавалась и не запускалась;
нет принятого F01 и трёх настоящих clean NOOP. Original 21 P2 skips не закрыты;
F02–F08, integration и независимый poly-QA остаются отдельными гейтами. Не
переписывать historical input-lock, manifests, Main01–03 или старый evidence.

До этой сессии main независимо видел protective suite 21/21 OK на старом
`3a7a38…` runtime, прежний runtime suite 42 run/1 FAIL из-за старого требования
handle-reacquisition/delete, layer/replay suite 14 methods/7 failed subtests,
lease model 19/19 и measurement diagnostics 13/13. После текущего runtime
hardening эти исторические результаты нельзя выдавать за тесты новых bytes.
Новый полный frozen recorder в этой сессии не запускался; новые offline и live
результаты не превращать в F01 acceptance.

Дополнительный independent metadata source audit:
`Audit/phase16-p3-metadata-independent-2026-11-03g/REPORT.md`.
Specified-normal/other native metadata, полнота controller descendants, полный
Shell state, классифицированный permitted node/non-node graph, до-evaluation
ordering и safe exact cleanup остаются незавершёнными. EData3 ошибка не
локализована; VData11 — узкая отдельная калибровка.

Offline cleanup model `Audit/phase16-p3-cleanup-model-2026-11-03g/REPORT.md`:
автор выполнил 32 теста OK над **synthetic** closed-world graph/disposal oracle;
ни Python `is`, ни выдуманная полнота graph/disposal не доказывают Max semantics
или production cleanup. Новые данные авторов и окончательные runtime hashes см.
в итоговом CHECKPOINT и post-publication записи этой сессии.

`Audit/phase16-p3-lease-review-2026-11-03g/REPORT.md`: independent OFFLINE review,
model 19/19, 02/03/04 templates disabled/unexecuted, arm catch и candidate
retention policy несовместимы, post-state не состыкован с COMMITTED, mutable
двух-holder protocol не immutable root of trust; runtime изменялся параллельно,
поэтому это не frozen review. Его фраза о ещё не выполненной local calibration
отражает состояние автора и superseded для узкого *одновызовного* наблюдения
пунктом 1 выше, не для cross-call proof. Другой неуспешно прерванный agent успел
создать `Audit/phase16-p3-lease-independent-2026-11-03g/test_review.py.disabled`;
его результаты не заявлены и файл не удалять.

`Audit/phase16-p3-recorder-review-2026-11-03g/REPORT.md` фиксирует, что `--input`
хеширует, но **не запускает** вложенные тесты, а extra suites требуют явного
`--suite` и отдельной сверки names/counts и raw logs. Source-level parser
контроли показывают, что некоторые нестандартные skip metadata или fake summaries
могут не быть отфильтрованы; его exit 0 сам по себе не доказывает покрытие.
Описанные inventory и команда привязаны к моменту аудита, требуют переоценки
после freeze. Автор консервативно отметил «никаких git»; фактическое указание
пользователя запрещает `commit/reset/checkout/clean`, а не все read-only git
операции. Тем не менее `git rev-parse` может запустить наблюдаемый hook; это
побочный эффект, который нужно учитывать отдельно, не менять старый recorder
молча и не запускать его в этой остановленной сессии.

## Дальше — последовательность, не разрешение на обход guards

1. Прочитать начало CHECKPOINT/AGENTS, PLAN §4.0d, handoff 03f и этот handoff,
   post-publication записи 03f/03g и новые независимые reports. Первый Max-вызов
   — свежая bounded read-only инспекция, без предположения о пустой сцене.
2. Независимо проверить все новые source changes и hashes, сохранить
   `INCOMPLETE_PRECREATE` и `INCOMPLETE_REPLAY`; не возвращать handle-only delete
   и не заменять safe exact cleanup безусловным retain.
3. Развивать layer reader с exact независимо retained witness и всеми 33/34/18
   полями; calibrate настоящий manager/scene ref без идентификации по классу,
   имени или handle. Разобрать прочие native metadata, controllers, graph,
   pre-evaluation controls и cleanup согласно contract; неизвестное => INCOMPLETE.
4. Откалибровать реально независимый persistent lease/witness в пределах честной
   trusted sequential threat model; не reacquire из registry. Новые live probes:
   direct constructor ref и witness/handle до следующего risky API, stage markers,
   отдельный safe cleanup и independently retained witness; без автоповтора при
   таймауте/ошибке/потере identity.
5. Только после исправлений остановить всех авторов, заморозить closure и выполнить
   полный recorder в **новый** каталог с разбором raw failures/skips/drift, затем
   новую authentic emitted pair, новый actual registry key, независимые реальные
   F01 measurements, три настоящих clean NOOP и targeted negatives. Не подменять
   actual predelete-grid и native evaluated polys predictions, triangle groups,
   восстановленным grid или synthetic echoes.

Сверка сохранности в начале сессии `Audit/phase16-p3-preservation-entry-2026-11-03g/`
нашла 2023/2023 matching 03f manifest entries, 0 missing/drift, package и 41/41
Main01–03 / 50/50 FINAL2 match на момент неатомарного сканирования; это не test
PASS и не гарантия последующих авторских правок. После остановки авторов main
записал `Audit/_phase16-p3-post-publication-2026-11-03g.json`, SHA
`17b8767b371f76df5cba2d365c3e0f8bf695d0a36f8dc9019d0f7b969bd48a99`:
2097 файлов, в 2023 прежних entries 0 missing / 0 unexpected drift; разрешённые
изменения — только CHECKPOINT и runtime, package/HEAD сохранены. Неатомарная
запись не новый тестовый PASS/lock. Она сделана **до** финального обновления
этого handoff и CHECKPOINT; их итоговые hashes отдельно приведены в файле
заключительной статусной сверки, старые записи не переписывались.
