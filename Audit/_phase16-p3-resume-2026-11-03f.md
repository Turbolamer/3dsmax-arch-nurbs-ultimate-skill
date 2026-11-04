# Phase 16 P3.1 — остановка / handoff 2026-11-03f

## Решение и причина остановки

**P3.1 NOT ACCEPTED.** P0/P1 и ограниченная offline-приёмка P2 остаются в силе.
Пользователь попросил дождаться субагентов и остановиться из-за заполненного
контекста, продолжить в новой сессии. Новые Max-пробы, эмиссия, изменение
production-кода и финальный полный прогон после этого запроса не выполнялись.
Разрешение пользователя на необходимую работу в Max остаётся действующим;
повторно спрашивать то же разрешение или возвращать прежний blanket ban нельзя.
Но текущий ownership/cleanup stop ниже обязателен и не является таким запретом.

## Сначала — реальный live-блокер, не старый нулевой census

**Последнее наблюдение в Max: ОДИН объект, не ноль.** Main выполнил отдельную
маленькую controller/graph калибровку, а не настоящий emitted F01. Первая
кандидатура `controller-graph.ms` не распарсилась; отдельно сохранённый v2
затем создал Box/попытался Shell и вернул:

```text
P3_CONTROLLER_GRAPH|ERROR=-- Runtime error: Mesh operation on non-mesh: Box
|CLEANUP_ERROR=-- Runtime error: lost exact Shell
|outcome=INCOMPLETE_RESIDUE_OR_IDENTITY|cleanup=false|objects=1|selection=0
|dirtyBefore=false|dirtyAfter=false
```

Полная отдельная запись:
`Audit/phase16-p3-main-probes-2026-11-03f/controller-graph-v2-residue.json`.
Read-only запрос `c3d6ad0b476c43349f78a51050433319` наблюдал:

* `Box001`, node handle `2024P`, class `Editable_mesh`, base `Box`;
* один Shell, handle `2044P`; parent undefined, children0;
* selection0, unnamed path/name, millimeters/1.0, dirty=false, слой0;
* Main03 key отсутствует.

Независимый snapshot `f360e6317bba4489b8f295960da2870d` подтвердил
objectCount1/rootCount1, один Shell. **Это наблюдения на тот момент, не гарантия
текущего состояния.** Прежние локальные node/Shell ссылки не были независимо
сохранены между вызовами. Имя, восстановленные handles, один объект и логическая
хронология не являются удаляющей authority. Не удалять/подхватывать автоматически,
не reset/save, не очищать dirty flag, не retry и не «чинить» registry.

Нужен ручной осмотр пользователем и, только если пользователь сам уверенно
идентифицирует временный остаток, его ручное удаление в Max. Если идентичность
остаётся сомнительной — оставить. Затем main получает новую read-only инспекцию.
Не просить ещё раз общее разрешение на Max: блокер — владение, а не разрешение.
Независимый разбор:
`Audit/phase16-p3-controller-incident-2026-11-03f/report.md`.
Точная выбросившая операция **не доказана**; `update n` лишь гипотеза.
Cleanup guard означает, что Shell ref **или** handle был undefined.

Хеши сохранённых failed candidates:

```text
85ff2e65de58b79b525fc9af19d2a30eb68a46c2e0e07ee9791553b7df51d372 controller-graph.ms
4d5b064c7d98bc531644ed9990629d4a3621989fcae0546c2150b1b6e8f50aa7 controller-graph-v2.ms
```

## Другая Max-сессия при входе

Свежий вход был read-only и **до** всех проб:
`Audit/_phase16-p3-resume-live-entry-2026-11-03f.json`.
PID9012 стартовал 2026-11-03T17:27:21.875Z, позже FINAL2. Тогда были нулевые
objects/selection, unnamed mm/1, dirty=false и отсутствующий Main03 global.
Real/bogus global-контроли и direct get различили отсутствие. Это последующий
процесс, не продолжение прежнего точного POISONED witness. Причины всех
промежуточных пользовательских/внешних действий не устанавливались.

Main03 не перевооружали, не восстанавливали, не удаляли и не перезаписывали.
Его историческое POISONED evidence неизменно; отсутствие в новом процессе не
делает прежний failed run clean NOOP и не разрешает повтор той же пары.

## Что реально продвинулось live — только узкие калибровки

Все файлы ниже находятся в `Audit/phase16-p3-main-probes-2026-11-03f/`.
Только main выполнял Max, коротко и последовательно.

| Контроль | Реальное наблюдение | Граница |
|---|---|---|
| `layer-owned.ms` / `layer-owned-result.json` | Отличающийся backing `layerAsRefTarg`, повторные snapshots совпадают; owned lock, GI `isGISpecular` и rename изменяют detached snapshot, restore совпадает; exact-verified empty layer cleanup | Не production reader, не все поля/скрытые данные, не lifecycle или same-name replacement |
| `layer-membership.ms` / `layer-membership-result.json` | Exact owned Box moved между backing layers и обратно, membership arrays подтверждены; guarded Box+layer cleanup, default48P сохранён | Не полный dependency/cleanup контракт |
| `vdata11.ms` / `vdata11-result.json` | Канал добавлен, repeat0.375, edit0.625, выбранные geometry controls неизменны; real/bogus/wrong-type различаются, exact cleanup | Не production comparator и не вся VData/EData/native metadata |
| `edata3.ms` / `edata3-result.json` | **ERROR/INCOMPLETE:** vertex data support not enabled channel3; точная операция ещё неизвестна; exact cleanup/zero postcheck | Не отсутствие API и не равенство |
| Controller candidates | Parse failure, затем runtime failure/residue | **FAIL/INCOMPLETE, live stop** |

Read-only исследование слоя:
`Audit/_phase16-p3-layer-readonly-2026-11-03f.json` и
`Audit/_phase16-p3-layer-calibration-brief-2026-11-03f.md`.
Интерфейс слоя имеет 33 перечисляемых свойства; backing RefTarget — 34, включая
дополнительный `degrade`; nested GI имеет 18. Interface-only enumeration неполон
даже среди наблюдаемых свойств. Сам MixinInterface нельзя передавать MaxObject
anim APIs; backing target здесь прошёл handle roundtrip. Скрытое состояние и
полнота этим не доказаны. Не исключать неудобные поля.

## Текущие production bytes и незавершённый hardening

```text
a2b0534835352d740710e6136a64fdeb9b9b1cd42c307cb15776511462903878 scripts/build_wall_surface.py
5c1e3134756396ff34fbc869d72f89e2f616c2ae8a29aead196d5f5689d28f12 scripts/wall_surface_inputs.py
3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf scripts/wall_surface_runtime.py
7868798b426f0f0c53560a9c36a65bfba4342930543ac0b041e369217d66b76b scripts/wall_surface_publish.py
```

Из четырёх P3-модулей изменён только runtime. Его старые точные bytes и
intermediate revision сохранены отдельно в
`Audit/phase16-p3-runtime-hardening-2026-11-03f/`:

* `wall_surface_runtime.pre-edit.py.bin` SHA
  `bd582b4590265e8c7850114f2ba57434835baf467dd77884ab66da231660ce15`;
* `wall_surface_runtime.pre-precreate-gate.py.bin` SHA
  `d9f470754639a78b3fe5478fde91e5c513d7834c9ba8ffecbcff990225b9b08a`.

Убрано handle-only deletion; непонятные refs/candidates/cleanup/disposal теперь
сохраняются и явно докладываются. Required missing fields больше не становятся
`absent==absent`, строки копируются; added dirty-arm/context/attempt diagnostics.
**Это не реализует весь safe-case cleanup контракт.** Промежуточный STOP-комментарий
не блокировал construction, поэтому теперь добавлен настоящий unconditional
`INCOMPLETE_PRECREATE` до BUILDING/создания; `INCOMPLETE_REPLAY` сохранён до
любого replay evaluation. Его нельзя снимать ради зелёного теста или F01.

Отчёты:
`Audit/phase16-p3-runtime-hardening-2026-11-03f/PRECREATE-GATE-REPORT.md`,
`Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md`,
`Audit/phase16-p3-runtime-review-2026-11-03/review.md`.
Open: независимый persistent witness, classified dependency closure, controllers/
subAnims/Shell до evaluation, native/specified normals, safe exact cleanup,
malformed prior lease diagnostics и неоднозначная семантика COMMITTED.

## Offline: не подменять прежний FINAL2 новыми утверждениями

Исторический FINAL2 по прежним bytes: 7/7 suites, 250 методов, 307 entries,
все OK. Его manifests не изменялись и не включают последующую работу.
В этой сессии **полный новый settled recorder не выполнялся**, новая genuine
pair не публиковалась и не запускалась.

Main независимо повторил на текущем runtime:

* `test_protection.py`: **21/21 OK**, source/model tests, не Max;
* unchanged `Audit/test_phase16_p3_runtime.py`: **42 run, 1 FAIL**, тест
  `test_cleanup_exact_current_attempt_refs_only` требует удалённые
  `getAnimByHandle createdHandles[i]` и `delete exactNode`;
* `Audit/phase16-p3-replay-tests-2026-11-03f/test_replay_safety.py`:
  **14 methods / 7 failed subtests**, отсутствующий production layer/GI reader,
  input hashes до/после совпали;
* `Audit/phase16-p3-lease-next-2026-11-03f/test_witness_model.py`: **19/19 OK**,
  только модель и source-shape; disabled Max templates не запускались;
* `Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py`:
  **13/13 OK**, диагностика не выдаёт derived triangle groups за native polys.

Старые тесты не ослаблялись. Не восстанавливать опасную ветку ради старой
лексической проверки; но и не выдавать unconditional retain за готовый cleanup.
Все author preliminary/intermediate failures сохранены в собственных каталогах.

## Новые offline handoffs

* `Audit/phase16-p3-layer-design-2026-11-03/REPORT.md`: design и disabled/
  unexecuted candidates; длинный mutation scaffold не запускать как есть.
* `Audit/phase16-p3-metadata-design-2026-11-03/REPORT.md`: exhaustive gap review,
  native normals/controllers/dependencies; historical current-lease wording
  superseded новым read-only входом.
* `Audit/phase16-p3-edata-design-2026-11-03f/DESIGN.md`: новое пооперационное
  диагностирование и alternate reader candidates, **НЕ выполнены в Max**.
* `Audit/phase16-p3-lease-next-2026-11-03f/README.md`: two-holder witness candidate,
  disabled/unexecuted. Не immutable root-of-trust, не arbitrary concurrent safety.
* `Audit/phase16-p3-grid-observer-design-2026-11-03f/README.md`: proposed independent
  same-attempt predelete-grid observer, не implementation; текущий post-fileIn
  reader не восстанавливает прежний grid. `grid_raw.issues`/timing admission gap
  требует отдельной проверки, не эха predictions.
* `Audit/phase16-p3-measurement-next-2026-11-03/README.md`: triangle-group candidate
  не native polygon evidence; его запуск/синтаксис не проверены Max.
* `Audit/phase16-p3-recorder-next-2026-11-03f/README.md`: новый no-clobber recorder,
  selftests только на явно fake isolated fixture; НЕ новый P3 финальный прогон.
* `Audit/phase16-p3-layer-reader-2026-11-03f/`: отдельный offline bounded-reader
  candidate. `REPORT.md`/`REPORT_p31_offline.md` и `README_p31_offline.md` говорят:
  exact backing/GI profiles 33/34/18, conservative dependency/membership gates,
  all statuses remain INCOMPLETE; `test_candidate.py`/`test_p31_offline.py` report
  14 structural/model tests OK. MAXScript not parsed/fileIn-ed/timed; no runtime
  integration, no production comparator, no replay. Exact helper SHA:
  `0dc718d9ae30751d8c32220e10e1d5d05141cf498b0092c3e89da9f252ea3ca7`.
  A first delegation attempt for this reader errored before this later successful
  offline artifact; the first error is not a verification result.

## Следующая работа после разрешения ownership stop

1. Прочесть этот handoff, начало CHECKPOINT/AGENTS, PLAN §4.0d, прежний contract,
   actual residue и independent incident reports. Свежая read-only scene/state
   инспекция всегда первое Max-действие: census/exact nodes, selection, path/name,
   units/scale, dirty, current layers и Main03 key. Не предполагать 0 nodes.
2. Не трогать candidate residue автоматически. Пользовательский ручной осмотр/
   разрешение ситуации не доказывает полноту модели; только после нового census
   планировать очень короткие новые probes с заранее retained witness и
   пооперационными markers до каждого рискованного API.
3. Доказать/внедрить bounded layer reader, не опуская backing/nested поля,
   завершить прочие обязательные native/controller/dependency readers и cleanup.
   Unknowns остаются INCOMPLETE. Только main выполняет live, subagents offline.
4. Отдельно откалибровать persistent independent lease/witness протокол; не
   reacquire из registry и не называть это independent. Новый namespace/identity
   должен давать реально новый key; новая папка/nonce сами по себе не меняют key.
5. Когда действительно исправлено — остановить всех авторов, заморозить всю
   closure, повторить полный offline recorder в НОВОМ каталоге, разобрать raw
   FAIL/SKIP/xfail/errors/drift. Не менять старые manifests и input-lock.
6. Только затем новая authentic published pair, explicit independently checked
   lease и выполнение **именно emitted .ms**, independent actual F01 measurements,
   три настоящих clean NOOP и targeted edit/collision/cleanup controls.

Original 21 P2 skips не закрыты. F02–F08, integration и независимый poly-QA
остаются отдельными гейтами. P7/materials и P9/export вне scope.

## Preservation / publication

Все старые изменения и новые файлы сохранять. Main01–03, accepted P2 bytes,
49 legacy fixtures, historical FINAL2/input-lock, package и HEAD не менять.
Не commit/reset/checkout/clean, installer/global-copy/.skill update, reset/save,
AutoBackup или dirty-flag clearing. Первичная независимая сверка 827 прежних
entries: 826 match, 0 missing, sole drift `graphify-out/cache/last_query_stamp`;
точный writer не установлен (read-only git commands вызывали hook output).
Это не исключает поздние новые файлы/текущие разрешённые runtime/doc edits.
Separate post-publication manifest нового handoff будет записан main после
завершения всех авторов; он не заменяет FINAL2 или фактическую live QA.
