# Phase 16 P3.1 — independent OFFLINE source audit of the layer-reader candidate

**Дата:** 2026-11-03

**Вердикт:** кандидат остаётся `INCOMPLETE` / disabled / offline-only. В
production, lease, baseline, construction, cleanup или replay он не интегрирован
и не может считаться accepted P3.1. Я не вызывал 3ds Max, ни один Max MCP
tool, `fileIn`, bridge или live scene API. Исправленный runtime/helper в старые
файлы не вносился; в этом каталоге добавлены только независимые тесты, runner,
логи и этот отчёт.

## 1. Объём и authority

Проверены независимо, только чтением:

* оба MAXScript-кандидата и Python emitter из
  `Audit/phase16-p3-layer-reader-2026-11-03f/`;
* `Audit/_phase16-p3-contract-2026-11-02e.md`, прежде всего §§ public boundary,
  ownership/replay, limits, detached state и fail-closed rules;
* `Audit/_phase16-p3-resume-2026-11-03f.md`;
* `Audit/_phase16-p3-layer-calibration-brief-2026-11-03f.md` и raw
  `Audit/_phase16-p3-layer-readonly-2026-11-03f.json`;
* только соответствующие raw layer probes/results в
  `phase16-p3-main-probes-2026-11-03f/`: `layer-owned.ms`,
  `layer-owned-result.json`, `layer-membership.ms` и
  `layer-membership-result.json`;
* текущий runtime только для проверки отсутствия integration и сохранения
  unconditional refusals.

Live probe evidence используется ниже лишь как **измеренный контекст API**, не
как выполнение этого кандидата. Источник измерения действительно сообщает
interface `33`, backing `34` с дополнительным `degrade` и nested GI `18`
(`_phase16-p3-layer-readonly-2026-11-03f.json:5,9,13,17-21,23-28`). Оно было
получено на одном default layer/одном процессе; полнота metadata этим не
доказывается.

## 2. Что подтверждено source audit

### 2.1 Профили 33 / 34 / 18

Оба кандидата транскрибируют ровно измеренные наборы:

* `layer_reader.ms:4-17` — 33 interface properties;
* `layer_reader.ms:18-31` — 34 backing properties, включая backing-only
  `#degrade` на строке 30;
* `layer_reader.ms:32-40` — 18 nested GI properties;
* `layer_reader_p31_offline.ms:6-18`, `:20-33`, `:34-42` — те же три профиля.

Независимый тест сопоставляет имена и observed MAXScript classes из raw JSON,
а не извлекает ожидаемый профиль из самого кандидата. Отсутствующее,
неизвестное или дублированное имя отклоняется (`layer_reader.ms:80-95`,
`layer_reader_p31_offline.ms:104-120`). Это хорошая conservative policy:
`degrade` не потерян, nested GI не заменён на один hash или name.

### 2.2 Typed detachment и unexpected/unreadable values

`layer_reader.ms:56-79` и `layer_reader_p31_offline.ms:66-102` проверяют Boolean,
Integer, Float, Name, bounded String и Color; Float/цветовые компоненты проходят
finite/range guard, строки копируются, неизвестный scalar type бросает
`INCOMPLETE`. Nested GI читается собственным exact profile
(`layer_reader.ms:97-102`, `layer_reader_p31_offline.ms:122-127`).

Профиль проверяется до getter loop, а getter failure попадает во внешний
`try/catch` observation. В новой Python model проверены missing/unknown,
NaN, infinity и unknown nested value; исходная Python model дополнительно
проверяет wrong type и duplicate-case через dictionary keys. Oversize string
guard присутствует в source, но отдельный тест на превышение в этой работе не
запускался. Это не доказательство поведения Max.

### 2.3 Identity, names, membership и dependency shape

У кандидата есть правильное разделение `LayerProperties` (MixinInterface) и
backing `ReferenceTarget`:

* `layer_reader.ms:47-55` выполняет exact reference/handle round-trip;
* `layer_reader_p31_offline.ms:50-63` сначала отвергает `MixinInterface`, затем
  проверяет retained `(reference, handle)` witness;
* `layer_reader.ms:147-153` и `layer_reader_p31_offline.ms:241-246` требуют
  `node.layer.layerAsRefTarg` == independently supplied backing;
* name не используется как ownership/identity authority (`old:178-179`,
  `p31:137-143`; README `:32-34`).

Membership не принимается по одному имени:

* old candidate дополнительно требует one-node scene/member shape
  (`layer_reader.ms:137-161`);
* P31 принимает только witness-supplied 1–16 members, проверяет exact witness,
  duplicate/foreign/member count и каждый member backing
  (`layer_reader_p31_offline.ms:160-196`).

Dependency check допускает только observed root + manager + optional exact member
shape, zero outgoing refs и bounded dependent array
(`layer_reader.ms:162-175`, `layer_reader_p31_offline.ms:198-231`). Комментарий P31
правильно называет это conservative observed-shape guard, а не доказательством
полноты graph.

### 2.4 Strict `INCOMPLETE`

Оба snapshot path стартуют и заканчивают только `INCOMPLETE`:

* old: `layer_reader.ms:184-198`, comparator `:274-289`;
* P31: `layer_reader_p31_offline.ms:272-288`;
* emitter: `emitter_fragment.py:20-33,47-57` — initial/replay examples
  бросают до construction.

Ни один helper не возвращает `PASS`, `UNCHANGED`, `NOOP` или cleanup authority.
В runtime bytes, наблюдавшихся во время recorded run, эти отказы находились в
`scripts/wall_surface_runtime.py:849` (`INCOMPLETE_REPLAY`) и `:861-864`
(`INCOMPLETE_PRECREATE`). **После run runtime изменился извне:** в повторно
прочитанном snapshot SHA `ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2`
аналогичные unconditional `require false` присутствуют на строках `:879` и
`:893`, до конструктора `:901`. Это source observation новых bytes, не их
прогон и не объяснение причины drift. Ни один runtime edit этим аудитором не
делался. Детали — `post_run_snapshot.json`.

## 3. Findings / blockers

### F-01 — emitter выбирает старый helper, не P31 variant (HIGH, integration)

`emitter_fragment.py:14-15,36-44` жёстко читает
`layer_reader.ms` и pin-ит SHA-256
`0dc718d9ae30751d8c32220e10e1d5d05141cf498b0092c3e89da9f252ea3ca7`.
`layer_reader_p31_offline.ms` с SHA
`5b16d1d648a2cdefd9b98440ad4fb4ae1ca1a1c3dde0ecf47990dfe44a8ad4f2` emitter-ом
не достигается и не проверяется. Это существенно, потому что old helper
сохраняет live reference objects в snapshot (F-02), а P31 возвращает mostly
detached handles/markers.

Следствие: нельзя говорить, что более строгий P31 candidate уже является тем,
что выдаёт fragment. Исправленный emitter не создавался намеренно; интеграция
запрещена до отдельного review/live gate.

### F-02 — `layer_reader.ms` snapshot не полностью detached (HIGH, contract)

В old helper `p3LayerExactRef` возвращает `#(value, h, classOf value)`
(`layer_reader.ms:47-55`), а `p3LayerReadOnce` кладёт `nodeRef`, `rootRef`,
`backingRef`, `managerRef` и member reference в payload
(`:141-161,180-182`). Поэтому `p3LayerTreeEqual`/`p3LayerSame` сравнивают не
только detached scalar state, но и живые Max references
(`:121-131`, `:256-258`, `:282-285`). Это может быть полезной identity check,
но это не detached snapshot в строгом смысле contract.

P31 лучше отделяет state: `p31ReadProperties` записывает
`#("same_exact_backing")`, а результат `p31ReadOnce` содержит handles, не
reference objects (`layer_reader_p31_offline.ms:129-147,249-256`). Однако P31 не
подключён к emitter (F-01) и имеет отдельный comparator gap (F-03).

### F-03 — P31 equality не revalidate-ит witnesses после detached reads (HIGH,
  pre-integration)

`p31ObserveTwice` выполняет `p31ReadOnce` дважды и затем сравнивает только
detached `a`/`b` через `p31DetachedEqual` (`layer_reader_p31_offline.ms:274-286`).
После возврата второго read нет повторного `p31ExactWitness`/handle
round-trip/identity validation и нет validation payload перед
`PARTIAL_STABLE`.

Если reference/lifecycle state станет stale после read (или callback/lifecycle
поведение окажется не тем, что предполагает один main-thread call), равные
detached arrays всё ещё дают `INCOMPLETE/PARTIAL_STABLE`. Статус не становится
PASS, но это не тот fail-closed equality observation, который нужен для
baseline/replay. `README_p31_offline.md:97-101` правильно предупреждает о
non-atomic double read, но этот конкретный post-read witness gap source-ом не
закрыт. До live calibration это остаётся blocker.

### F-04 — manager witness shape проверяется, но actual `LayerManager` identity не
  authenticated (HIGH, contract)

Old reader принимает caller-supplied `expectedManager`, проверяет его handle и
сравнивает его с entries returned by `refs.dependents`, но нигде не требует
`expectedManager == LayerManager` (`layer_reader.ms:141-146,162-175`). P31 делает
то же для `managerWitness` (`layer_reader_p31_offline.ms:201-230`): это exact
witness некоторого reference, не доказанный actual LayerManager reference.

Это совпадает с handoff gap (`README_p31_offline.md:59-60`) и с contract
§3, где требуется независимо удержать и live-проверить настоящий manager
witness. Raw readonly evidence показывает `LayerManager` среди dependents, но
не удерживает его exact reference/handle между вызовами
(`_phase16-p3-layer-calibration-brief-2026-11-03f.md:8-13`). Поэтому dependency shape
не равен dependency identity.

### F-05 — P31 не проверяет scene/layer/context census; old проверяет только часть
  (HIGH, admission boundary)

`p31ReadOnce` начинается с `p31ExactWitness` node/backing и затем читает
`node.layer`, hierarchy, membership, dependencies и properties
(`layer_reader_p31_offline.ms:233-256`), но не проверяет `objects.count`, полный
scene node set, `LayerManager.count`, selection, units, file path/name или dirty
state. Лишний node в другой layer либо лишняя layer может быть не виден этому
reader-у.

Old candidate строже только в двух местах — `LayerManager.count == 1` и exact
one-node `objects` census (`layer_reader.ms:137-140`); он тоже не проверяет
selection/units/path/dirty. Runtime сейчас проверяет часть admission отдельно,
но layer emitter не передаёт такой context snapshot. Contract §3 (identity,
baseline, changed scene census) требует, чтобы caller доказал эти условия; их
отсутствие нельзя принять за reader completeness.

### F-06 — P31 использует `getNumNodes()` без measured positive control (MEDIUM,
  live calibration)

P31 вызывает `layer.getNumNodes()` на строках `176-177` и повторно `194`. В
сохранённом measured membership probe проверялись `layer.nodes &array` и counts
(`phase16-p3-main-probes-2026-11-03f/layer-membership.ms:49-62,95-99`), но
`getNumNodes()` там нет; raw membership result также не содержит этого вызова.
Read-only evidence подтверждает `nodesCall=true`, не `getNumNodes`
(`_phase16-p3-layer-readonly-2026-11-03f.json:20-21`). Если API getter
недоступен/имеет другую семантику, outer catch корректно даёт INCOMPLETE, но
P31 нельзя назвать live-validated до короткой отдельной калибровки.

### F-07 — measured 33/34/18 — observed profile, не complete native state (HIGH,
  acceptance boundary)

Exact `getPropNames` guards — хорошая защита от silent drift, но одновременно
делают candidate refusal-only за пределами одного observed profile. Ни один
вариант не читает native/specified normals, mesh metadata, controllers/subAnims,
Shell/plugin/renderer extensions, custom attributes или полный dependency graph.
Это явно остаётся outside scope в `README_p31_offline.md:73-80,91-100` и
`REPORT.md:72-75`, а contract требует complete state readers до replay.

Особенно важно не превращать `degrade` и 18 GI scalars в доказательство
полноты: raw evidence — один default layer без nodes, parent и children
(`_phase16-p3-layer-calibration-brief-2026-11-03f.md:3-6,14-21`).

### F-08 — lifecycle / same-name / equal-state identity не измерены (HIGH,
  acceptance blocker)

Measured owned-layer probe доказал только узкий positive: distinct backing target,
stable alias, lock/GI/name mutation and restoration, exact in-call cleanup
(`layer-owned-result.json:5-8`). Membership probe доказал move to another backing
and back plus exact in-call cleanup (`layer-membership-result.json:5-8`).

Не доказаны same-name replacement, two distinct layers with equal detached state,
deletion/recreation, handle reuse, populated-layer lifecycle, undo/redo,
save/load/merge/restart и external callbacks. Синтетические `Ref` objects в
`test_candidate.py:66-92,316-335` не могут закрыть эти Max lifecycle gates.
README это перечисляет как open controls (`README_p31_offline.md:77-80`).

### F-09 — operational ceilings применяются после потенциально тяжёлого Max call
  (MEDIUM, documented limitation)

`getPropNames`, `layer.nodes` и `refs.dependents` вызываются до проверки
результатных `.count` (`layer_reader.ms:80-95,157-164`,
`layer_reader_p31_offline.ms:104-118,178-211`). Поэтому `<=34`, `<=16`, `<=64`
и `<=12` ограничивают обработку возвращённого значения, но не allocation/time
внутри самого Max API call. README это честно признаёт в `:94-96`; contract
operational ceilings требуют refusal, но до runtime calibration нельзя
рекламировать resource-safety.

### F-10 — MAXScript validity и actual execution отсутствуют (CRITICAL,
  execution gate)

Оба файла прямо объявляют boundary:

* `layer_reader.ms:1-3` — paste-inside-wrapper, not run in Max;
* `layer_reader_p31_offline.ms:1-4` — text only, not parsed/fileIn-ed/timed;
* `test_candidate.py:1-5` и `test_p31_offline.py:1-5` — Python static/model
  checks, no Max interpreter.

Независимый runner использовал только Python subprocess commands. Его lexical
delimiter smoke test — не MAXScript parser; `ast.parse` применён только к
Python emitter/test. Поэтому не установлены parse/load, local-function scope
inside actual wrapper, getter/exception paths, timing, `getNumNodes`, manager
handle behavior или any fileIn result. Синтаксический риск остаётся именно
risk, а не reported parse failure.

Адресные места для будущей проверки exact bytes: обращения локальных `fn` к
outer-local profiles (`layer_reader.ms:97-105,215-223`, P31 `:122-131`),
рекурсивная функция с keyword parameter `depth:` (`old:121-131`, P31
`:259-270`), вложенные вызовы и индексирование в boolean guard (`old:151,268`),
`if … then … else …` как элемент array (`old:285`). Эти формы не объявляются
неверными: прошлый live `layer-owned.ms:20-29,43-60` уже демонстрирует часть
похожих форм, но не компилирует оба рассматриваемых файла целиком. Реальный
исторический parse failure другого controller candidate — отдельное событие,
не доказательство синтаксической ошибки здесь
(`phase16-p3-controller-incident-2026-11-03f/report.md:14-23`).

### F-11 — old comparator не подтверждает свежесть предоставленного snapshot
  (MEDIUM, API precondition)

`p3LayerSame a b` проверяет форму и live exact-ref roundtrip, затем сравнивает
предоставленные payloads (`layer_reader.ms:250-271,274-289`); он не делает
новый `p3LayerReadOnce` и не привязывает второй snapshot к текущему времени или
вызову. Дважды переданный один старый, но структурно валидный snapshot может
остаться `INCOMPLETE/OBSERVED_MATCH` после изменения layer state при сохранных
references. Это не ложный `PASS`: иллюстративный `REPLAY_OBSERVATION` в
`emitter_fragment.py:28-32` сначала вызывает новый snapshot, а затем всегда
бросает `INCOMPLETE_REPLAY`. Будущий caller обязан сохранить независимое свежее
чтение и сравнение; сам comparator их не гарантирует.

### F-12 — nested GI проверяется как value-profile, не как independently
  retained interface identity (MEDIUM, explicit assumption)

`p3LayerReadGI` и `p31ReadGI` проверяют только `MixinInterface`, exact 18-name
profile и прочитанные значения (`layer_reader.ms:97-102`,
`layer_reader_p31_offline.ms:122-127`). Они не удерживают/не сверяют subtype
или identity GI interface между interface/backing reads. Raw evidence сообщает
repeat-equality GI reads на одном layer (`_phase16-p3-layer-readonly-2026-11-03f.json:23-26`),
но не доказывает подстановку/сохранение GI interface в иных состояниях.
Нельзя вызывать anim handle API на mixin ради «исправления»: эта операция уже
показана проблемной для `LayerProperties`. Если рассматриваемый contract требует
GI identity, нужен отдельно калиброванный safe механизм; иначе явно утверждённый
value-only subset плюс доказанный внешний graph guard. До решения — INCOMPLETE.

## 4. Test-strength audit

### 4.1 Settled offline commands and exact outcomes

Executed from repository root:

```text
python -B Audit/phase16-p3-layer-reader-2026-11-03f/test_candidate.py -v
  exit 0; Ran 14 tests; OK

python -B Audit/phase16-p3-layer-reader-2026-11-03f/test_p31_offline.py -v
  exit 0; Ran 14 tests; OK

python -B Audit/phase16-p3-layer-independent-2026-11-03g/run_offline.py
  exit 0; unchanged=true
  candidate.log:    exit 0; 14 tests; exact OK/no qualifiers
  p31.log:          exit 0; 14 tests; exact OK/no qualifiers
  independent.log:  exit 0; 17 tests; exact OK/no qualifiers
```

`run_offline.py` exclusively created `candidate.log`, `p31.log`,
`independent.log` and `run.json` in this new audit directory. `run.json:6-46`
records before/after SHA-256 for candidate, evidence, runtime and audit-test
inputs; `unchanged: true` **только между двумя наблюдениями этого run**. Позднее
read-only post-run наблюдение зафиксировало drift одного input — runtime
`3a7a…3acf → ab80…efc2` — и отсутствие drift у остальных 18 входов;
`post_run_snapshot.json`. Источник изменения неизвестен. Это отдельная запись,
не изменение старого `run.json` и не повторный тест новых runtime bytes.

### 4.2 What the independent 17 tests actually test

`test_independent.py` checks, offline only:

* independent raw-evidence profile reconstruction and exact 33/34/18 matching;
* candidate/emitter SHA pins and the fact that emitter selects old helper, not
  P31;
* lexical delimiter balance only (explicitly not parsing MAXScript);
* source characterization of witness, membership, dependency and missing
  context/scene-census guards;
* a separate Python fail-closed model for mutate/restore, unknown/missing/
  nonfinite/nested values, replacement handles, foreign members/deps and
  stale handle maps;
* two **in-memory source mutants**: removing the old Float finite guard still
  leaves the original 14-test `test_candidate.py` suite green, and removing the
  P31 Color type guard still leaves the original 14-test `test_p31_offline.py`
  suite green. The on-disk candidate bytes were hash-checked before/after and
  were not changed.

The mutation result is a limitation finding, not a live failure: the existing
tests are textual/model tests and do not execute MAXScript branch behavior. The
independent model is useful negative evidence but is not a Max oracle.

## 5. Hash manifest

The authoritative run manifest is `run.json`; raw stdout/stderr logs have their
own hashes there. Candidate and evidence hashes observed in that run:

```text
0dc718d9ae30751d8c32220e10e1d5d05141cf498b0092c3e89da9f252ea3ca7  layer_reader.ms
5b16d1d648a2cdefd9b98440ad4fb4ae1ca1a1c3dde0ecf47990dfe44a8ad4f2  layer_reader_p31_offline.ms
105cbcba7771175e0291a421dea4f874c66b9f51ddb0db3fd5dba340cb8b16b9  emitter_fragment.py
27bf1a85bf483e232a3367fd1dc2321ebbe6b273d1388c614fc6a593182153b4  test_candidate.py
a6725a4d28ff555bf70db9cc8bc2c32a49a2e4a5b6604e83b58cc207e7e8d69b  test_p31_offline.py
072a46f1a5382b17775dc3cc440996e88814594704eefd4e02244c01dbd2a62e  README_p31_offline.md
fed6e750921065cfa920de8e4c0041578f580fc62c9434874ff312daf0096ee8  REPORT.md (source candidate report at audit start; this independent report is separate)
7c076ce3080101d13fec2a663049cc1d19d5c7cb2423b678ba03cd8cc706dce1  REPORT_p31_offline.md
5527991d2bf68055abb678f8c031cfa63ed675137b139affcf69b3da5fcf5d17  independent test
a2a3d1ef0ab5920babe8917e65eed53c57f58909c29fdd497f81877266e3f818  offline runner

4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f  contract
b3df0d3e27c2ec568197b4adb2f4679c467805ea7d29a992dbb72cacf198846c  main handoff
dcee5901eab5ddf56d0d83ceeff410658c335d9a903ffe6d4b6c06e8b902a1a5  calibration brief
c4a338253d3315d87be74d7f5fdb533867487d5f9271d8b67050568b3107a383  measured readonly JSON
aaca2608e05ba46c83e89a554210d11dfc676ef8b6c7ae1d805591834eebaffc  layer-owned.ms
382b98f6eee156e8ad893c96b37052182c004786bc3348bdba5ce1bcd36676e4  layer-owned-result.json
07fdd1599c5517445eeee89282aa65caded0d1038fe057aada95e4a7f8d56a79  layer-membership.ms
be51b426e9e25f78b7308286d148e1b515d532e585982607df6c586388cad673  layer-membership-result.json
3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf  wall_surface_runtime.py during recorded run
ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2  later read-only runtime snapshot, not tested here
```

The `REPORT.md` hash above is the **pre-existing candidate `REPORT.md`** hash
(`fed6…6ee8`), disambiguated because this file has the same basename in the
independent directory. `run.json` is the byte-accurate authority for every
path/hash and before/after equality **during that run**. The later separate
`post_run_snapshot.json` is the authority for the observed subsequent runtime
drift; neither record is a lock or a guarantee of current bytes.

```text
1c5be3669d7a404cf993b7442ba37939fb7324fc0963c7d0165f253901006ea4  run.json
181b9336c2696d47fa797ddf8b87fc9c0bf920c2d14972dadec23c724b5d69b1  post_run_snapshot.json
961cdc55c1fcc126b8746a904d438783a74309628d6cde29b73ae9a4ef12ef95  candidate.log
31127f888db0f8cd8c18a48c52a89f699ae16bba1880116390f3e61ee4773aef  p31.log
432b2541b6b69f49837b0c8b5a6f126ffd5c5f73d029e96304041af678159a38  independent.log
```

## 6. Disposition / required next gates

1. Keep both helpers and emitter disabled; do not integrate the old helper merely
   because the Python suites are green.
2. Decide whether one reviewed candidate is authoritative; if P31 is selected,
   create a separately reviewed disabled emitter pinned to P31 rather than
   silently using the old helper.
3. Before any integration, close manager identity, scene/context census,
   post-read witness validation, `getNumNodes` calibration, nested/interface
   identity and dependency completeness questions.
4. The handoff's residue/ownership stop remains in force: no mutating work until
   the operator resolves it and main obtains a fresh read-only scene inspection.
   Thereafter run an exact helper in Max only through a fresh coordinator-owned,
   bounded read-only/disposable gate; capture raw transport `ok/error` and actual result,
   not transport success alone. Do not call that future run a replay/acceptance
   pass unless the contract's native/controller/cleanup gates also pass.
5. Preserve unconditional `INCOMPLETE_PRECREATE` and `INCOMPLETE_REPLAY`; no
   offline result here authorizes construction, cleanup, baseline or NOOP.

No corrected disabled candidate was added by this audit. This auditor did not
modify existing files, production runtime, old evidence/tests, package/installer/
global copies, git state or Max scene. The separately observed subsequent
runtime drift is external to this audit; its writer and other concurrent activity
are not attributed here.
