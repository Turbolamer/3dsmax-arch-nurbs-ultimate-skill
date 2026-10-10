# План исполнения: точная форма, нативные единицы Max и автоматический P8

Дата: 2026-10-09. Репозиторий: `D:/Rhino/3dsmax-arch-nurbs-ultimate-skill`.
Адресат: LLM, выполняющая одну ограниченную микрозадачу за раз.
Статус: **PLAN ONLY — реализация, сборки, установка и новые живые измерения не выполнены**.
Единственное владение автора этого документа: новый `AGENT_PLAN_form_precision.md`.
Будущие разрешения ниже — условия последующей работы, а не разрешение начать её сейчас.

## 1. Результат и порядок авторитетов

Цель: выразить исходную форму числами, получить воспроизводимые точки построения и независимо измерить результат в Max.
Обязательная цепочка: S1 → S2/S3/S4/S5 → S7/P8 → передача модели для ручных материалов.
P8 — восстановленный исторический этап QA; он не зависит от отменённого S6/P7 и не открывает S8/P9.
Номера **фаз 01–16 этого плана** не совпадают с историческими P0–P15 или фазами 0–8 исходного брифа.
Минимальный обязательный эталон: конечный полуэллиптический цилиндрический свод и ссылки на arc/ellipse_arc его сечений.
В полном обязательном результате есть генераторы, адаптивная граница единиц, конфигурация QA, реальный сбор MCP и автоматическая оценка.
Структурная проверка legacy-модели — отдельный результат; она не заменяет проверку аналитической формы.

| Приоритет | Документ/решение | Как использовать |
|---|---|---|
| 1 | Текущее явное решение пользователя и подтверждённые locks, полностью встроенные в §2 | Определяет scope; три основные решения уже закрыты, временный файл не нужен |
| 2 | Этот план; после FREEZE — одобренный shipped English `references/_form-units-qa-design.md` | Английский frozen contract supersedes русский root plan для исполнения; scope меняет только пользователь |
| 3 | Исполненные транскрипты CHECKPOINT/AGENTS с датой и контролями | Основание технических фактов только для измеренного контекста |
| 4 | Текущий исходный код, особенно `main`, загрузчики и проверки | Основание утверждений о существующем CLI/поведении; не доказательство работы API Max |
| 5 | `AGENT_BRIEF_form_precision.md`, действующие playbooks, PLAN/SKILL | Применять в части, не отменённой таблицей ниже; старые противоречия не обходить молча |
| 6 | Необязательные временные decision/audit artifacts | Supporting evidence автора; не prerequisite исполнения и не новая live-сертификация |

| Старое ограничение | Новый действующий смысл | Что сохраняется |
|---|---|---|
| Бриф §1/§7 фаза 6/§10: P8 и qa.json запрещены | P8/S7 восстановлен; qa.json — план, отчёт отдельно | P7/P9 отменены; QA не создаёт материалы, UV, экспорт |
| Бриф §4/§5: только сцена cm/1, числа без пересчёта | Спецификации cm; граница Max учитывает SystemType и SystemScale | Настройки реальной сцены пользователя сохраняются |
| D8 открыт, надо выбирать A/B | **D8=A**: исходные параметры в dimensions.json | Derived-only G-49 для NURBS; B не реализовывать |
| D1 запрещает любые правки build_spec/build_nurbs | Генератор не становится примитивом строителя; правки dimensional sinks необходимы | Только владелец и отдельное разрешение на перечисленные emitter/library файлы |
| Фаза 6 — исключительно ручные probes | Минимальная аналитическая ссылка нужна обязательному QA | Общая intent DSL остаётся design-only |
| P8-a…g в фазе карнизов | Переименовать в MOULD-a…g | Это не этап P8 QA |
| «Все строители защищены от overwrite» | Наблюдаемое расхождение source/docs; защиту спроектировать и проверить | Нельзя полагаться на несуществующую общую защиту |
| Приоритет старого брифа «если расходится, спроси» | Подтверждённые overrides выше не переспрашивать | Новые решения о схеме/допусках/исправлениях требуют gate |

Датированная отмена P8 от 2026-10-05 остаётся историей. Активную маршрутизацию меняют только в авторизованной фазе.
Плановая запись CHECKPOINT в будущей сессии не означает implementation done, VERIFIED или принятие P8.
Будущие shipped references, agents, scripts/comments/help, CHECKPOINT пишутся **по-английски**; этот корневой план — по-русски.

## 2. Decision locks и оставшиеся вопросы

| Lock | Уже принято; не задавать заново |
|---|---|
| L-UNIT | Канонические длины cm и ключи `_cm`; явный ввод mm нормализуется офлайн; Max получает нативные значения |
| L-QA | P8 автоматический; qa.json — locked configuration/check plan; raw evidence и qa-results.json раздельны |
| L-D8 | dimensions.json владеет исходными параметрами; генератор/точки derived; эталон QA независим от точек |
| L-SESSION | Сейчас только этот план; никаких Max calls, builders, git mutation, checkpoint edits, установки |
| L-SCOPE | Фазы исходного брифа 5 и 8 требуют отдельного «да»; 7 только дизайн; общий intent только дизайн |
| L-HISTORY | Существующие examples и старый barrel-vault.json сохраняются byte-identical |
| L-SAFETY | Assembly G-81 без модификаторов; иные стеки ≤5 добавлений/вызов, >10/узел только после вопроса; 20 никогда |

Следующие решения не были одобрены. Будущий агент задаёт их одним коротким пакетом в фазе 02, затем STOP.
Не превращать рекомендацию в факт, не выбирать значение по умолчанию ради старта кода.

| Gate decision | Рекомендация | Что именно пользователь утверждает |
|---|---|---|
| A-VERSION | Явно поддерживать 1.0 и 1.1; новые references/generator/QA config — 1.1 | Минорную версию, смешанные файлы, отказ неизвестным версиям |
| A-TOL | Раздельные arithmetic, form и numerical budgets | `surface_deviation_cm`, способ задания cm³ допуска, граничный comparator |
| A-FIELDS | Контракты §5 как ограниченный v1 | Имена/типы/единицы/joins/происхождение, закрытую форму и target kinds |
| A-CLOSED | Явная политика 360° и shell equality | Разрешён ли closed consumer; exact seam, минимальные distinct points; правило 0.001 cm |
| A-EXAMPLE | Новый coherent fixture под `specs/fixtures/form-precision/`, recipe отдельно | Размещение примера QA по §12 grammar без правок старых examples |
| A-WRITE | Draft-only expansion; transaction/ownership для computed outputs | Правила отказа/замены и журнал незавершённой пары JSON+MS |
| A-OWNERS | Последовательные patch scopes §8–§10 | Узкие правки existing emitters/library/validator/scaffold и будущих документов |
| A-LIVE | Изолированные разрешённые rehearsal scenes | Право на probes, units matrix, replay, именованную очистку; production только read-only QA |
| A-CORRECT | При подтверждении дефекта отдельный stage-owner patch | Dimension-correct G-82 и представление полного wall-host, не исключение из QA |
| A-REGEN | Historical examples отдельно от новых adaptive examples | Регенерировать только owner-driven копию в новом утверждённом расположении |

Необходимые design-only записки по intent/per-level/mouldings не дают разрешения на их реализацию.
Archive rebuild и global installation — разные будущие разрешения, запрашиваются после измеренных ворот.
Создание ветки/коммиты/push не являются частью этого плана; только по отдельной просьбе пользователя.

## 3. Исходная линия: что известно и чего она не доказывает

Источники прочитаны в порядке: decisions → CHECKPOINT → PLAN → оба аудита → исходный бриф.
Аудиты: `C:/Users/TURBOL~1/AppData/Local/Temp/opencode/form-units-audit.md` и `form-qa-audit.md`.
Это история подготовки, не future read order: решения встроены в §2, существенные findings/contracts — в этом плане.
Позднему агенту не нужен доступ к temp decisions/audits; их отсутствие не блокирует работу по repo и frozen English design.
Исторический baseline validator: **138/0/0/15**, не вечный будущий acceptance total и не количество G-правил.
Исторические узлы: massing 27; NURBS 10 дополнительных; вместе 37; massing+assembly 244; full chain 254.
Произвольный проект получает ожидаемый set/count из contracts, а не эти константы.
Исторически живые units: centimeters, scale 1.0; другие типы/масштабы этим не сертифицированы.
MAXScript execution — ground truth; introspection/discovery не заменяют контролируемый probe.
Исторически: commit обязателен для evalPos; domain не всегда [0,1]; parent ID нельзя синтезировать.
Исторически: Box.pos — центр XY и **низ Z**, copy/baseObject сохраняют это; plain copy не instance.
Исторически: point_grid overshoot, cv_grid undershoot; bbox узла не доказывает форму поверхности.
Исторически: getCurrentException, findString и matrix3 работают; старые заявления об отсутствии отозваны.
Новые SystemType enums, wire precision, seed semantics, mesh-volume/open-edge APIs остаются **UNVERIFIED**.
Source-observed: emitter пишет сырые cm; library имеет raw physical defaults; QA CLI ещё нет.
Source-observed: G-82 сравнивает cm³ с linear_cm²; host и WAL cells могут оставаться одновременно видимыми.
Source-observed: shell threshold `>` в library/census расходится с допускающим equality G-47.
Source-observed: `0.5 cm` ошибочно названо half millimetre; это **5 mm**, не 0.5 mm.
Репозиторий не имеет build/test/lint runner; не выдумывать `pytest`, `npm test`, qa/capture/export scripts как существующие.

## 4. CLI: существующее и предлагаемое строго раздельно

### 4.1 Существующее по исходникам main(), не команды этой сессии

Везде обычный `-h/--help`. `<p>` — абсолютный pipeline directory; `--out` builders по умолчанию равен `--in`.

| Script | Точный текущий интерфейс | Вход → выход/ограничение |
|---|---|---|
| env_preflight.py | `[--results FILE] [--transport TEXT] [--json]` | Bare печатает probes; все SKIP и exit 0 не PASS; --json не печатает тела |
| build_spec.py | `--stage TEXT --in DIR [--out DIR] [--json]` | Только massing; locked dimensions → massing.json/massing.ms; иной stage exit 2 |
| build_nurbs.py | `--in DIR [--out DIR] [--json] [--build] [--allow-draft]` | Hand-authored nurbs → normalized nurbs.json/nurbs.ms; --build compatibility flag |
| facade_tables.py | `[--stage grids/components/tables/all] --in DIR [--out DIR] [--json] [--build] [--allow-draft]` | Default all; dimensions+massing и нужные intermediate → JSONs/CSVs; --build compatibility flag |
| place_components.py | `[--stage TEXT] --in DIR [--out DIR] [--json] [--build] [--allow-draft]` | Default/only assembly; здесь --build overrides --allow-draft |
| validate_specs.py | `[--dir DIR] [--file FILE] [--json] [--warnings-as-errors] [--rule TEXT] [--build] [--allow-draft]` | Default specs/pipeline; --file грузит siblings; --rule фильтрует display, не общий exit |
| init_project.py | `--project ID [--dir DIR] [--from DIR] [--force] [--dry-run]` | Default dir=.; fresh 11 specs+manifest; seeded 8 JSON+manifest, без CSV/reserved |
| install_skill.py | `[--target archive/global/all] [--mcp-repo DIR]` | Default all; архив всегда строится; global/all устанавливают в оба home каталога |

Реальные обязательные входы `place_components`: **dimensions.json, massing.json, components_registry.json, world_table.csv**.
`assembly.json` — выход, не вход; старое описание в AGENTS необходимо узко исправить в будущей doc-фазе.
Massing не принимает --build/--allow-draft/--force/units; NURBS не принимает --stage.
Текущие builders преимущественно проверяют major=1; часть writers всегда пишет 1.0.
Текущий validator WARNs на nonzero minor/patch; 1.1 сегодня не проходит warnings-as-errors как known supported.
`curve_gen.py`, `expand_curves.py`, `qa_check.py`, `build_mouldings.py` пока отсутствуют.
`capture_views.py`, `export_max.py`, `lint_script.py`, `check_skill_md.py` не являются текущими executable tools.

### 4.2 Предлагаемые интерфейсы — FREEZE до кода

Рекомендация интерфейса QA ниже — самостоятельный контракт; обращаться к временным audit sketches не требуется.
`curve_gen.py` — import-only библиотека; отдельный CLI не требуется.
`expand_curves.py --project-dir DIR --in FILE --out FILE`: expansion draft nurbs; вход/выход — файлы, не dirs.
`expand_curves.py --project-dir DIR --in FILE --check`: read-only; отказ при несовпадении stored points/provenance/count.
`expand_curves.py --project-dir DIR --in FILE --suggest-count --section-id ID --tol-cm X`: read-only suggestion одной секции.
Во всех режимах DIR обязателен: absolute coherent project root; pipeline = DIR/specs/pipeline, project identity совпадает с input/dependencies.
--in выбирает nurbs draft; штатно его parent равен pipeline. --out — новый авторский draft в том же project, не locked upstream overwrite.
Expansion меняет только выходной draft nurbs; dimensions, assumptions/conflicts ledgers и остальные dependencies читает read-only, включая locked.
Dependency paths относительны project root, разрешаются только внутри проекта; absent/mismatched dependency — refusal, не guessed sibling/default.
Draft --in вне pipeline допускается только через явный approved dependency/identity mechanism, frozen в02; до него — refusal во всех modes.
`--check`, expansion и suggestion взаимно исключены; X finite >0; ambiguous/missing selector — usage/refusal.
Рекомендация: expansion не in-place; differing existing --out refuses; новый draft публикует владелец после сравнения.
Suggestion выдаёт count+method+bound+limits, не обещает допустимый NURBS interpolation error.
`qa_check.py --in DIR --emit RUN_DIR --run-id TOKEN [--json]`: offline emit request/context/batches, **READY/NOT_EVALUATED**.
`qa_check.py --in DIR --request FILE --results FILE --out RUN_DIR [--json]`: offline assess, пишет qa-results.json.
`--emit` несовместим с --request/--results/--out; assess требует все три; отсутствие results не переключает в emit.
Run token supplied агентом, проверяется как безопасная строка; не случайный серверный guard и не credential.
Request deterministic без времени/nonce; context и scripts deterministic при одинаковых request+run-id.
Emit exit 0 означает valid request ready, **не model PASS**; assess 0 только complete PASS; 1 FAIL/ERROR/INCOMPLETE; 2 usage.
У expansion exit 0 означает выполненную операцию/check, 1 refusal/invalid data, 2 usage; stdout не переопределяет exit.
Предлагаемый env_preflight `--require-complete` в captured mode отказывает при mandatory SKIP/missing/malformed.
Validator остаётся static: не добавлять ему --results, Python connection, geometry evidence или несуществующий --stage qa.
Для stage-aware inventory нужен одобренный API/gate context; форма его CLI **обязательный FREEZE**, не угадывать флаг.
CLI/build_mouldings и кольца задаются только в optional design gates; не публиковать фиктивные executable examples.

## 5. Контракты данных: обязательный FREEZE перед реализацией

В этом разделе конкретные рекомендации. До A-FIELDS/A-VERSION/A-TOL они не являются утверждённой схемой.
FREEZE считается полным только при наличии таблицы **каждого leaf**: type, required/default, units, range, consumer, origin.
Если предложение ниже не определило leaf/API/политику, агент пишет вопрос в дизайн и STOP, а не добавляет разумный default.
Шесть шагов grammar §12 выполняются вместе: schema → invariant → implementation → provenance → inventory → example.
Строки API/classes/tools живут в emitters/evidence, не в geometric config или arbitrary source formulas.

### 5.1 Envelope и версии

Первые шесть ключей сохраняются: schema_version, spec, project, units, source, status.
Canonical units: length=cm, angle=deg; area leaf именует m2/cm2, volume leaf cm3, никакого mm под `_cm`.
Source сохраняет текущий source.kind/reference/recorded_at contract; origins используют given/assumed/derived/conflict, не новый ledger.
Рекомендация versions: 1.0 geometry без новых features; 1.1 для references/generator/defined QA config.
Каждый файл проверяется по собственной версии; geometry 1.0 + QA 1.1 допустимы при project/dependency compatibility.
Новый feature в 1.0 — FAIL; known 1.1 не WARN; неизвестный minor/patch в required build/QA — refusal до отдельной поддержки.
Writer сохраняет применимую версию либо делает явную owner migration; не терять metadata через hardcoded SCHEMA_VERSION.
Missing legacy QA на ранних gates/old examples — legacy NOT_EVALUATED/SKIP, не global mandatory FAIL.
P8 требует defined locked QA config независимо от версии upstream; draft/superseded/empty не дают delivery PASS.
Fresh scaffold создаёт **draft plan без verdict**; filled draft lint проверяет структуру; P8 всё равно refuses draft.
Seeded путь явно создаёт нужный draft QA и missing-intent tasks; копирование examples не создаёт analytical authority.
Legacy result-ish QA stub не автоматически переименовывается в config; миграция отдельным authoring step.
Run reports лежат вне pipeline, чтобы discovery/envelope lint не принимали их за design specs.

### 5.2 dimensions.json: узкая исходная аналитическая authority

Working key `form_references[]`; конкретное имя требует A-FIELDS. Таблица не является второй геометрией для строителя.
`id`: unique safe string без units, required, S1 owner; используется joins и evidence sample IDs.
`kind`: closed enum `arc`, `ellipse_arc`, `semi_elliptical_barrel`; required, policy constant; не имя Max class.
Для arc/ellipse: `plane` XY/XZ/YZ; `center_cm` finite [3]; radius_cm>0 **или** semi_axes_cm=[a,b]>0 по kind.
`from_deg`, `to_deg`: finite degree scalars; 0<abs(delta)<=360; oriented finite interval без arbitrary formula text.
Для barrel: `plane`, `center_cm`, `semi_axes_cm`, `from_deg`, `to_deg`, `longitudinal_range_cm=[s0,s1]`, s1>s0.
Рекомендация v1 barrel ограничить upper semiellipse: from/to = 180/0 или 0/180; XZ profile и +Y longitudinal сначала.
Расширение barrel на XY/YZ требует явной frame map на FREEZE; section arcs уже знают все три planes.
Axes v1: XY=(+X,+Y), XZ=(+X,+Z), YZ=(+Y,+Z); normal/longitudinal sign фиксируется таблицей, не cross-product догадкой.
`center_cm` barrel задаёт поперечный центр; координата along longitudinal axis должна иметь объявленное правило offset/range.
Рекомендация range — **world-coordinate endpoints**, longitudinal component center=0; секционные centres берут y=s.
Span=2a, rise=b, springing=center.z для XZ; если хранить aliases, invariant вычисляет их, не три независимых authority values.
Shape values S1 given/assumed/conflict с ledger; фиксированные vocabulary/axes имеют документированное exemption, не fake derived.
`precision_targets[]`: source element ID + reference ID + `role=design_surface` + requirement profile; data join, не node pattern.
Сам required target registry locked S1/QA dependency: удаление reference/target — scope change, не способ снять FAIL.
Для каждой generator section нужен join к reference и station: recommended `form_reference_ref` и `station_cm` вне generator.
Join symbols и origin path syntax **FREEZE**: file-qualified reference resolver не считать существующим legacy origin_inputs.
QA oracle строится из исходного reference; генератор обязан совпадать с ним по frame/axes/radii/angles/station.

### 5.3 sections[].generator и points_cm

Generator остаётся внутри sections[]; points_cm остаются единственным geometric primitive builder.
Exact keys: kind, plane, center_cm, radius_cm/ semi_axes_cm, from_deg, to_deg, count; extraneous kind-specific keys FAIL.
`count`: integer, не bool, 2…500; операционный лимит не сертификат допустимого размера Max-call.
Point i: t=t0+(t1−t0)i/(n−1); P=C+a cos(t)e1+b sin(t)e2; углы вычисления — radians, input — degrees.
Оба endpoints включены; serialization q(x)=round(x,6), −0→0; finite scalars и strict JSON без NaN/Infinity.
Points stored [n][3], cm; points provenance derived from sections[i].generator; generator leaves derived from dimensions refs.
Station/copy arithmetic имеет пересчитывающую формулу; никакого points→kind→points как численной authority.
Recompute tolerance **0.001 cm** — только expansion consistency, не физический surface tolerance.
Reject adjacent rounded duplicates/zero chords; full 360/count=2 недопустим; count=3 closed degeneracy также проверять.
Closed 360 policy FREEZE: рекомендовать ≥3 distinct vertices, явный closed consumer и единственную permitted seam duplicate.
Без одобренного closed consumer нельзя принять full-circle row просто потому, что формула выдаёт точки.
G-42 equal counts относится u_loft/uv_loft/point_grid/cv_grid; независимые sweep sections не обобщать до equal counts.
Chord diagnostic: sampled max — estimate; circle sagitta и conservative bound отдельно именованы.
Для C(t)=(a cos t,b sin t): ||C''||≤max(a,b), ошибка vector linear interpolation ≤a_max·Δt²/8.
Это bound расстояния curve→соответствующая chord: ближайшая точка не дальше линейного interpolant внутри chord.
Для rounded endpoints добавить обоснованный rounding budget; при 3D q(6) endpoint bound ≤sqrt(3)·0.5e−6 cm.
Доказательство предпосылок, segment span и ограничений входит в design; bound не относится NURBS/обратному Hausdorff.
Для circle sagitta на minor chord применять только соответствующий angular range; при больших arcs не расширять формулу молча.
Suggestion count выбирает наименьший допустимый n в 2…500 по доказанному bound; exhausted → no recommendation/refusal.
Chord initial diagnostic не hard NURBS FAIL; severity требует решения; few measured counts не универсальная interpolation bound.

### 5.4 qa.json — только конфигурация

После envelope proposed keys: tolerances, origin_inputs, origins, profile, dependencies, scope, check_plan, sampling, limits, capture_plan.
Никаких measured/error/pass/verdict/determinism-results в конфигурации; legacy checks/captures/verdict не наследовать механически.
`profile`: closed policy ID/version; recommendation `form_precision_v1` или отдельный `legacy_structure_v1`.
Form profile требует ≥1 analytical target и все inferred precision targets; structure profile выводит **FORM NOT SPECIFIED**.
`dependencies[]`: required `{file, spec, schema_version}`; relative safe path внутри project; actual SHA-256 вычисляет emitter.
CSV dependency задаёт producer/spec join и canonical columns; не притворяться, что CSV имеет JSON envelope.
`scope`: source IDs и expanded exact owned names/roles; names выводятся по существующим mapping functions, не wildcard всей сцены.
`check_plan[]`: unique ID, known check kind, source target_ref, optional required reference_ref, tolerance_ref; без disable boolean.
Runtime mandatory families inferred independently (§7); удалённая check row оставляет missing required ID → FAIL.
`sampling`: schedule policy/version, grid_u=5, grid_v=5, landmarks policy; counts exact non-bool positive.
`limits`: max rows/batch, total targets/samples, calls/time budgets; finite positive operational bounds, не tolerances.
Initial 25 evalPos/batch — proposal до time probe; превышение total caps refuses, batching не дропает rows.
`capture_plan`: optional viewport attachments, empty допустимо; camera/renderer создание не часть v1.
`tolerances`: arithmetic references отдельно; surface_deviation_cm>0 или approved zero policy; angle_deg; volume policy cm3.
Numerical serialization/solver budgets отдельно в named policy; не прятать их увеличением geometric tolerance.
`origins`: actual file-qualified derived/assumed entries и ledger для физических thresholds; exemptions только для enumerated policies.
`origin_inputs`: legacy dotted paths сохраняются лишь как compatibility metadata; не используются как hash/dependency authority.
Selected frame: integer/non-bool либо finite tick policy; exact field/units FREEZE; request и каждый batch проверяют его неизменность.

### 5.5 Request, run context, receipts, raw evidence и report

Расположение recommendation: `<project>/runs/form-qa/<run-id>/`, за пределами specs/pipeline; существующие runs не перезаписывать.
`qa-request.json`: protocol_version, project, qa_hash, input_hashes, profile, expected scope/check/batch/sample sets, quantities/methods.
Request includes canonical reference snapshots, tolerance policy, selected frame, required replay references; hash canonical byte payload.
Порядок стабильный; никаких clocks, random, runtime units, live pointers или nonce в deterministic request body.
`qa-run-context.json`: run_id/nonce, request_hash, expected build receipts, approved context; local evidence tag, **не server guard**.
Run-id uniqueness проверяется локально; это защита от случайной stale reuse, не криптографическая аттестация Max.
`build-receipt.json`/stage receipt: project/stage/input+script hashes, library revision/hash, executed owned names, system tuple, c/f.
Receipt дополнительно связывает local run/session/frame; exact live write/capture mechanism обязательно калибровать до использования.
Скрипт не может автоматически знать SHA-256 своих bytes без contract; hash computes emitter/agent, receipt связывает observed invocation.
Если server session identity недоступен, указать local session ID + limitation; не изобретать bridge-provided guard token.
У pre-existing user model без build receipts required spec-build binding отсутствует: **STOP missing binding**, не implicit acceptance.
QA не удаляет/перестраивает модель для получения receipts и не создаёт retrospective executed-build evidence из текущих specs.
Отдельно approved measurement-only `legacy_structure_v1` может оценить наблюдаемую структуру, но явно не claims executed spec build/replay/form PASS.
Library revision guard: expected revision/hash и tested reload/capability check; `MCP_NURBS_Arch != undefined` недостаточно.
`qa-measurements.json`: immutable полный tool envelopes + normalized wire records + request/run/batch/sample IDs + timings/errors.
Каждый batch: START/END, expected/observed row count, unit/frame snapshots, target transform/census fingerprint, explicit status.
Каждая row: observation_id, check_id, target_id, sample_id если нужен, quantity, units-dimension, space, finite raw numeric values/error.
XYZ raw из evalPos: space=`world_scene`, один objectTransform; bbox raw уже scene/world, не повторный transform.
Runtime class/superclass labels допустимы в evidence; static config хранит geometric roles, не API spelling.
Hash каждого raw response и capture artifact; assessor сохраняет provenance до конкретной row; raw не правят для ремонта.
`qa-results.json`: report_schema/protocol, input/request/QA/raw hashes, project/run/session/frame/units, completeness и check results.
Check result: expected/observed/error/tolerance/unit/method/status, IDs evidence, N_expected/N_observed/N_compared, worst sample.
FORM result: max/mean/RMS, solver uncertainty, coverage landmarks, claim=`sampled_conformance`; без global certified wording.
Verdict statuses: PASS, FAIL, ERROR, INCOMPLETE; optional NOT_RUN/SKIP отдельно; required SKIP/ERROR блокирует PASS.
Report сохраняет original geometry tolerance; boundary policy recommendation: error upper ≤ tolerance PASS, lower>tolerance FAIL, иначе INCOMPLETE.
Exact wire escaping, scalar precision, locale, protocol enums, hash inclusion/exclusion и cross-file path grammar — mandatory FREEZE.
Несуществующий serializer/API не становится установленным фактом из-за этого списка; сначала controlled calibration.

## 6. Единицы: ввод пользователя и граница Max

### 6.1 Явный ввод mm → canonical cm в S1

1. Сохранить исходное число, явную единицу, документ/строку/размер на чертеже в source evidence; не переписывать источник.
2. Определить dimension каждого поля **по реестру схемы**, не suffix-guess и не обход всех numeric leaves.
3. Для length mm: cm=value_mm/10; например 1800 mm→180 cm, 0.5 mm→0.05 cm, 20000 mm→2000 cm.
4. Для XYZ mm преобразовать все три length components; unitless direction/weights/count/angle не трогать.
5. Если исходник явно mm²: cm²=/100, m²=/1,000,000; mm³: cm³=/1000; только для declared area/volume leaf.
6. mm input tolerance нормализовать так же, но не заменять утверждённый QA threshold новым числом без владельца.
7. Разрешить смешанные **явно подписанные** source values; единица пропущена/неоднозначна → conflict/assumption gate, не UI guess.
8. Записать canonical value и provenance conversion с raw value/unit/ref; физические исходные shape params принадлежат dimensions.
9. Assumption ledger покрывает использованные inferred units; не ставить given там, где единица угадана агентом.
10. Strict JSON/q(6) применять на canonical output; сохранить unrounded input evidence; проверить round-trip физической величины.
11. Валидатор подтверждает cm/deg envelope и conversion consistency; при уже `_cm` поле не делить второй раз.
12. Fixture: raw 12000 mm span/1800 mm rise/4000 mm springing → 1200/180/400 cm; QA reference остаётся cm.

### 6.2 Runtime conversion и недопустимые обходы

Пусть k — cm на base SystemType unit; s=units.SystemScale; **c=k·s** cm/scene-unit, f=1/c.
Write geometry: L_scene=L_cm/c; point_scene=point_cm/c; readback L_cm=L_scene·c.
Area readback: A_m2=A_scene2·c²/10000; volume V_cm3=V_scene3·c³; powers применяются по quantity type.
Degrees/counts/weights/ratios/normalised schedules/knots/percentages не конвертируются.
Direct units.SystemType/SystemScale reads — historical route; display metadata отдельно, не conversion authority.
k mathematical candidates: mm=.1, cm=1, m=100, km=100000, inch=2.54, foot=30.48, yard=91.44, mile=160934.4.
Exact runtime enum spellings и весь standard enum support — будущие probes; unsupported/custom type refuses clearly.
Finite positive s,c,f обязательны; отсутствующие/zero/NaN/unknown данные никогда не fall back на cm.
Unit preamble **до delete/create/layer/scene mutation**; staged receipt drift check также до mutation.
Смена system tuple между S2/S3/S5/QA или внутри batches инвалидирует build/run; rebuild только owned model после разрешения.
Не менять Units Setup пользователя, не whole-scene rescale, не final node.scale/parent scale workaround.
Не масштабировать num()/весь numeric tree; только explicit length sinks scene_length_expr/scene_point_expr.
Library получает scene-native arguments; caller конвертирует один раз; evaluated derivative vertices уже native.
Physical defaults/cutoffs propagate до first construction: set merge, approximation merge, shell presence, derivative thickness.
render_edge_pct/spacialEdge и curvatureDistance не считать cm по имени; percent/viewDependent semantics probe отдельно.
UV domains и trim seed не blanket-scale: point_grid chord-length domain ≠ universal length contract или angle.
Native mm/m/non-1 fixtures проверяют domain/seed mapping и оба merges; setter echo не достаточно.
Factor serialization не q(6); numerical budget, large-coordinate fixtures и locale проверяются живьём, не auto-loosen tolerance.
Certified minimum: cm/1, mm/1, m/1, mm/10, cm/2; general standard-unit claim только после bounded probes всех enums.
Отдельные authorised rehearsal contexts; display mismatch отдельно с неизменным system tuple; production settings сохраняются.

## 7. Требуемый QA и независимость ожиданий

| Family (runtime, не G-rule) | Откуда ожидание | Что читается и что блокирует PASS |
|---|---|---|
| QA-V1-COVERAGE | Request и inferred mandatory registry | Exact ID sets/counts, hashes/run/batches, frame/units, errors/truncation |
| QA-V1-CENSUS | Source IDs + independently expanded owned names | Actual node names/classes/parents, duplicates, missing/extra owned nodes |
| QA-V1-NURBS-CENSUS | Kind/canonical shell decision/relations | Committed subobjects, class/role, domain, ambiguity, relation readbacks |
| QA-V1-PLACEMENT | dimensions/massing/registry/world-table joins | Bboxes/base-Z, centres/rotation, every baseObject link, actual dimensions |
| QA-V1-WALLS | Host/opening formulas и measured cells | Exact visible occupancy, overlaps/gaps/full host, full thickness, cm³ identity |
| QA-V1-FORM | Locked dimensions analytical reference | Finite nearest distance, finite span, landmarks, maximum sampled deviation |
| QA-V1-STACK | Assembly ownership/G-81 contract | Actual scoped modifiers count; no global modifier ban |
| QA-V1-REPLAY | Separate authorised rehearsal protocol | Three real runs and snapshots; production capture не делает replay сама |

Census считает actual nodes, не counters из build log; scatter declaration не означает scatter scene node.
Design surface resolver: kind+role+expected census+class/relational readbacks; ambiguity ERROR, не first/last universal rule.
Trim historical emitted surface contribution=0; не отправлять projection curve в evalPos как surface.
First/last heuristics для shell/blend лишь исторические подсказки, не общий target selector.
Sample baseline 5×5, fractions {0,.25,.5,.75,1}²; actual U/V endpoints read после commit.
Дополнительные required IDs: springings/crown на first/middle/last longitudinal stations и longitudinal endpoint landmarks.
Exact selection/matching этих landmarks проверяется probe: normalized UV **не** обязана совпадать с ellipse angle/crown.
Если resolver/critical-landmark route не способен получить required coverage, INCOMPLETE и design/probe STOP, не quietly omit.
World point: (evalPos local) * node.objectTransform **один раз**, затем raw scene→cm **один раз** в assessor.
Oracle для finite ellipse arc минимизирует Euclidean distance по ограниченному t interval, включая endpoints.
Не применять implicit ellipse residual как cm, vertical delta или atan2 как exact nearest solution.
Для barrel oracle: transverse arc distance и distance along конечному interval; при ортонормальном frame distance=sqrt(d_arc²+d_span²).
Проверить отдельные station/extent/landmark constraints: точки поверхности могут лежать на правильной части бесконечного цилиндра и быть слишком короткими.
Bounded stdlib solver обязан дать numerical error bound; recommendation interval branch/refinement, не single-start local minimum.
Один вариант: curve Lipschitz a_max даёт lower bound max(0,d(mid)−a_max·half_interval), evaluated d даёт upper; subdivide до бюджета.
Для signed/oriented interval unwrap применять фиксированное правило; comparator controls circle/crown/endpoints/outside span независимы generator_points.
Exhausted solver budget → INCOMPLETE; max gate не компенсируется mean/RMS; sampled PASS не global surface fidelity.
Box bbox-volume допустим только class/transform подтверждают axis-aligned solid assumption; rotated bbox product не volume.
Иначе отдельный calibrated snapshot-mesh signed volume + watertight/orientation route; не общий NURBS bbox product.
Wall check рассматривает **delivered visible active solid geometry**; скрытие лишнего host нельзя предполагать из JSON.
Foreign nodes перечислять отдельно; intersecting visible foreign wall требует owner review, не менять и не обещать глобальный opening PASS.
Volume rule A-TOL: явный cm³ budget или обоснованный dimensional propagation; cm² как threshold недопустим.
Рекомендация для известного Box: endpoint uncertainty e даёт extent uncertainty d=2e; для positive w,h,t взять максимум двух product differences.
Upper=(w+d)(h+d)(t+d)−wht; lower=wht−max(w−d,0)max(h−d,0)max(t−d,0), оба cm³; total budget суммировать только с обоснованием.
Такой bound может скрыть маленькую щель: exact interval occupancy и per-cell checks остаются обязательными, не replaced volume-only gate.
Рекомендация form threshold .5 cm допустима только как **новый явно одобренный** физический выбор; не наследовать arithmetic автоматически.
Counts/topology exact; lengths cm, area m²/cm² явно, volume cm³; zero tolerance не заменять `or default`.
Numerical controls offline; API/instance negatives в rehearsal; production QA не создаёт control nodes, не rebuild/delete.
Все mandatory rows: **N_expected=N_observed=N_compared>0** и exact ID sets; duplicates/extras/missing FAIL.
Исключения: optional NOT_RUN отдельно; absent required evidence никогда не optional SKIP и не 0-vector.
Legacy structure profile не требует invented references; report FORM NOT SPECIFIED без form_precision PASS.
Required form profile не зелёный, если analytical refs удалены, checks отключены или oracle выведен из same emitted points.
Wrong semi-axis 185 вместо180 — известный 5 cm comparator control только на exact crown исходного эталона, не на произвольном UV sample.
Optional viewport evidence: реальные prefixed capture tools, без камер/renderer changes; картинка не quantitative gate.
Optional scatter: count equality только count repeatability; true determinism требует transforms/model assignments/config+seed bindings.
Scatter save/load/clear/rebuild — отдельный mutating approval/probe; не dependency core QA и не автоматически revived cancelled scope.

## 8. Карта будущих файлов и символов

Ниже scopes для будущего координатора. Каждый patch получает собственный точный subset; таблица не массовая лицензия.
Existing names observed в source/audits; новые имена помечены proposed и утверждаются FREEZE.

| Файл | Existing symbols/точка входа | Узкая будущая работа |
|---|---|---|
| scripts/validate_specs.py | RULE_TITLES, CROSS_FILE_RULES, SpecDef/SPEC_INVENTORY, run_checks | Центр ID allocation; dispatch новых static predicates |
| scripts/validate_specs.py | check_envelope/check_inventory, RECHECK_STAGES, G-1/G-3/G-15/G-31 | Explicit versions, contextual QA presence; P8 recheck без P7/P9 |
| scripts/validate_specs.py | check_nurbs_rules, _g42_shape, _g49_provenance | Generator/ref joins; equal counts только lattice; D8 derived сохраняется |
| scripts/validate_specs.py | _g82_wall_tiling_volume, check_assembly_rules | Dimension-correct policy и visible-host declaration при approved correction |
| scripts/init_project.py | INVENTORY, RESERVED_KEYS, SEEDED_FROM_EXAMPLES, envelope, build_plan/build_manifest | Draft QA config fresh+seeded; target canonical vs observed; proposed scaffold_qa |
| scripts/env_preflight.py | SCRIPT_*, CheckSpec/build_checks, ResultsRunner/evaluate/main | Read-only unit capture, strict complete gate; не новый transport |
| scripts/build_spec.py | load_locked_dimensions, Model/build_massing, rect_of, prism_box/element_box | Canonical arithmetic; rect limitation сохраняется до optional mesh phase |
| scripts/build_spec.py | render_ms, verify_script/verify_script_shape, write_bytes | Length sink conversion, preamble/receipt, approved write transaction |
| scripts/build_nurbs.py | load_spec/normalise, section_literal, tessellation_line, dependent_surface_lines | Version/metadata checks; points/merges/thickness conversion без generator math |
| scripts/build_nurbs.py | expected_census, MIN_SHELL_THICKNESS_CM, self_check, render_ms/verify_script | Shell equality in cm, library revision/reload guard, first-call defaults |
| scripts/build_nurbs.py | main, write_bytes, serialize/strict_loads | 09.6: JSON+MS guarded transaction/recovery; input draft сохранён при совпадении read/write пути |
| snippets/nurbs_arch_library.ms | applyArchTessellation, createULoftShell/createUVLoftNetwork, makePointSurfaceGrid/makeCVSurfaceGrid | Scene-native optional arguments и initial propagation; no double conversion |
| snippets/nurbs_arch_library.ms | sampleSurfaceToQuadPoly/createDiagridOnSurface, makePointCurve/makeCVCurve, knots | Native evaluated geometry; dimensional default resolution; knots/weights unchanged |
| scripts/facade_tables.py | read_spec/read_downstream, build_grids/build_registry, render_csv, guard_existing_grids | Consistent envelope compatibility; canonical tables не масштабировать |
| scripts/place_components.py | UPSTREAM_NAMES/main, build_placements/build_opening_cuts/build_wall_cells/build_assembly, prototype_sizes | Реальные four inputs; canonical computations; narrow approved wall contract |
| scripts/place_components.py | render_ms, _check_script_shape, _check_wall_tiling, write_bytes | Boundary lengths, no modifiers, cm³ policy, receipt/write safety |
| scripts/scene_units.py (new) | proposed unit_factor, scene_length_expr, scene_point_expr, emit_unit_preamble | Shared Python emission text, dimensional classification; никакого live connection |
| scripts/curve_gen.py (new) | proposed generator_points, validate_generator, chord_bound, suggest_count | Stdlib pure math и documented bound; sampled diagnostic отдельно |
| scripts/expand_curves.py (new) | proposed main/read_draft/expand/check/suggest | Authoring CLI; provenance; guarded draft output |
| scripts/qa_check.py (new) | proposed main/emit_request/parse_capture/assess/resolve_reference/distance_to_arc | Два offline modes, strict denominator, independent oracle, reports |
| references/_form-units-qa-design.md (new) | Approved contract/decision register | Полный FREEZE fields/API ownership и G IDs |
| references/_form-generators-evidence.md (new) | Future executed transcripts | Shape/units/serialization/domain/receipt certification; можно разделить при необходимости |
| agents/max-qa.md (new) | S7 contract | Emit → sequential MCP collect → assess; read-only delivery |
| specs/recipes/nurbs/barrel-vault-generated.json (new) | Draft template | Filename/spec match; instantiate coherent project before build |
| specs/fixtures/form-precision/ (proposed new) | Coherent defined QA example | §12 example; placement approved; без runtime reports в shipped specs |

Не создавать десятки пустых helper modules. Shared QA helper допустим только после изменения ownership/design map.
Last registered invariant сейчас G-83; proposed G-84…G-90 reserve **центрально, последовательно**, не параллельными авторами.
Recommendation allocation: 84 generator schema, 85 expansion, 86 reference/join, 87 QA config, 88 coverage joins, 89 tolerances/schedule, 90 dependencies/provenance.
G-42/G-49/G-3/G-15/G-31 расширять по смыслу, а не дублировать; optional rings/mouldings получают IDs после approved block.
Runtime QA-V1 registry отдельный; static validator не наблюдает Max и не присваивает live PASS.

Dimensional sink checklist для patch review (audit source locations; actual symbols перечитать перед правкой):
- build_spec.render_ms: Box width/length/height и pos; grouping.parent_pivot_cm; Dummy physical size только при approved explicit contract.
- build_nurbs.section_literal: каждый point3; dependent_surface_lines: set.merge и rail/trim points через общий boundary.
- build_nurbs.render_ms: u_loft thickness, grid merge, post-commit merge, space_frame thickness; tessellation_line: merge_tol_cm.
- createULoftShell/createUVLoftNetwork: initial set.merge и initial applyArchTessellation settings, не только позднее применение.
- makePointSurfaceGrid/makeCVSurfaceGrid: nested approximation получает explicit merge; createDiagridOnSurface thickness physical.
- place_components.render_ms: PROTO Box sizes, PLC position после canonical base-Z arithmetic, WAL Box sizes/base positions.
- Derivative evaluated points, knot fractions, p_vec direction, seed domain coordinates, tension, rotations, SCATTER_DENSITY не length sinks.
- q/_round_tree/num/prototype_sizes/CSV builders/self_check остаются canonical; no recursive conversion или unrelated defaults cleanup.

## 9. Протокол микрозадачи и dependency DAG

DAG core: 01→02→03→04→05→06→07→08→09→10→11→12→13; optional 14/15/16 имеют собственные approval branches.
03 probes делают specification API facts возможными; 04–06 не утверждают новую форму до live gate 12.
11 correction branch возвращается к owner 08/09 и новым 10–12 evidence; отказ пользователя оставляет delivery BLOCKED.
14 rings не prerequisite core; 15 широкий intent/per-level design не prerequisite core; 16 mouldings только при отдельном approval.
Фазу можно разбить мельче, но нельзя объединить scopes/gates ради экономии сообщений.

Каждая строка patch ниже — **один coherent patch, потом STOP/gate**; командные/live операции отдельная микрозадача без code patch.
Перед patch: прочитать только нужные symbols/context; проверить actual names; записать input/output и разрешённые файлы.
После patch: проверить diff, выполнить назначенный gate, записать real output/exit/IDs/числа в future evidence.
Gate status: READY, RUNNING, PASS, BLOCKED, FAIL; SKIP mandatory gate не PASS; нет evidence → NOT_RUN.
Координатор ведёт future gate register в design/evidence; автор этого плана его сейчас не создаёт.
Handoff микрозадачи ≤12 строк: scope, changed symbols, gate evidence, next ID, unresolved STOP; листинги — в artifacts.
Только координатор делает live probes и final acceptance; subagents возможны при explicit ownership и доступном tool.
Нет delegation tool → исполнить один scope последовательно; не выдумывать spawn/client commands.
Max никогда не параллелить; readonly collection тоже последовательная ради consistent snapshot.
В patch нельзя менять чужие пользовательские файлы/неизвестный git diff; rollback только своих staged artifacts.

Локальные gates обязательны **после каждой микрозадачи**, не только в конце фазы; ID evidence равен ID микрозадачи.
Multi-file patch строка делится на .a/.b по файлу, кроме необходимого согласованного schema/consumer pair; каждый suffix получает gate.
После implementation patch syntax-check затронутого Python; полный `python -m py_compile scripts/*.py` — на phase gate.
Нет runnable prerequisite для промежуточного patch → import/static review и pending integration explicit; phase PASS пока запрещён.

| Microtask IDs | Минимальный локальный gate перед следующей задачей |
|---|---|
| 01.1–02.4 | Exact ownership/authority/leaf diff; unanswered decisions отмечены; 02.4 требует явный approval record |
| 03.1–03.8 | Known working и bogus control различаются, exact outputs/timing/cleanup; каждый API вопрос закрыт отдельно |
| 04.1 | Old/new/mixed version good cases; unsupported feature/version bad cases, QA-less earlier stage stays valid |
| 04.2–04.4 | Grammar fields↔registry bijection; derived reference join и raw-mm known answers; два invalid origin/reference cases |
| 05.1–05.2 | Endpoint/crown/plane known answers; degeneration controls; mathematical bound prerequisites проверены |
| 05.3–05.4 | Two-run bytes; draft success/locked refusal/existing-output refusal; check/suggest read-only и actual exits |
| 06.1–06.4 | Exact G84/85/86 messages, valid unequal sweep; recipe vs coherent-project validation и hashes старых examples |
| 07.1–07.3 | Certified factors, bad scales, no mutation before guard; emit-only не complete preflight PASS |
| 08.1–08.3 | Sink inventory covered; unchanged canonical output, deterministic MS; smoke fileIn/readback на owned fixture |
| 08.4 | Differing output и interrupted publication; prior complete artifact/input intact; incomplete pair refused |
| 09.1–09.5 | First-call forwarding, zero/below/equal/above shell, revision/metadata check; native geometry не double-scaled |
| 09.6 | NURBS differing output/interrupted pair refusal и recovery; same-path input draft сохранён; M34 proof |
| 10.1–10.2 | ≥2 negatives на G87–90, config без results; fresh/seeded parity; P8 recheck success/P7/P9 refusal |
| 10.3–10.4 | Deterministic request/batches, full ID set; M21–25 parser refusals; no fabricated transport/import |
| 10.5–10.7 | Independent circle/arc/span controls, max gate и bounded solver; good/bad synthetic evidence, config locked |
| 11.1–11.5 | Host/volume evidence; owner approval before correction; correct opening PASS/active-host FAIL |
| 12.1–12.9 | Actual identity sets/raw responses/unit/frame consistency per leg; no skipped batch; each negative fails |
| 13.1–13.6 | Active routing/CLI verified, history preserved; actual handoff evidence; separate archive consent |

Future baseline workdir: `D:/Rhino/3dsmax-arch-nurbs-ultimate-skill`; <tmp> — absolute authorised temporary root.
Scaffold: `python scripts/init_project.py --project rehearsal-form --dir <tmp> --from D:/Rhino/3dsmax-arch-nurbs-ultimate-skill/examples`.
Во всех baseline builder/validator commands <p> = absolute `<tmp>/rehearsal-form/specs/pipeline`; не relative examples и не project root.
Перед rebuild убрать только четыре computed seeded JSON в owned rehearsal: massing/facade_grids/components_registry/assembly; nurbs сохранить.
Проверки: `python scripts/validate_specs.py --dir <p> --build` и та же с `--warnings-as-errors`; не filtered --rule report.
Preflight: bare emit → sequential MCP+bridge/plugins captures → `python scripts/env_preflight.py --results <absolute-json>`.
Каждый вызов начинается `python scripts/<script>.py` и содержит required --in/--stage по §4.1; strict flag только после реализации.

## 10. Последовательные обязательные фазы

### Фаза 01 — разрешение на исполнение и source baseline

01.1 READ ONLY: принять этот план; пользователь разрешает следующий scope и будущие gates, не всю optional программу.
01.2 READ ONLY: status/diff, symbols/CLI, example hashes, registered max G-ID; фиксировать user work, не требовать clean git через удаление.
01.3 PATCH только `_form-units-qa-design.md`: authority overrides, locks, decision list, source-observed vs historical vs unverified.
Gate 01: scopes известны, historical files защищены, текущие commands отделены от proposed; unanswered designs остаются blocked.

### Фаза 02 — FREEZE без реализации

02.1 PATCH design: утвердить A-VERSION/A-FIELDS/A-TOL, schemas §5, exact leaf inventory и per-kind reference joins.
02.2 PATCH design: closed 360, shell equality, finite solver/bound, sampling landmark selection, reports/wire/receipt safety.
02.3 PATCH design: explicit future CLI §4.2, contextual inventory API, atomic/ownership policy и example/regeneration location.
02.4 QUESTION/STOP: пользователь утверждает ещё не одобренные decisions одним пакетом; locks L-UNIT/L-QA/L-D8 не спрашивать.
Gate 02: signed/frozen table содержит все unresolved leaves/choices; нет pending field, из которого следующий patch вынужден угадывать.
До PASS 02 код не писать; calibration procedures могут иметь placeholders в design, но не в executable contracts.

### Фаза 03 — bounded live calibration после A-LIVE

03.1 OFFLINE baseline в owned temp project: current compile/validator и canonical chain; exact outputs/hashes, не old PASS totals.
03.2 LIVE historical cm/1 только отдельная разрешённая сцена; если недоступна, не выполнять raw-cm scripts в native mm.
03.3 LIVE units enums/scale/display controls: bounded known physical box, direct fields, working и bogus control в каждом API batch.
03.4 LIVE serializer/locale precision: fractions/negative/large coordinates/counts, malformed control, START/END output completeness.
03.5 LIVE commit/domain/world transform/seed controls: translated/rotated/parented/nonuniform measurement fixture; local vs world ошибка обнаруживается.
03.6 LIVE merges/shell cutoff/approximation semantics: initial values против геометрии; reject setter-only proof; capture ordinary shell sign.
03.7 LIVE library revision/reload и stage receipt mechanism; stale revision, mixed unit tuple и namespace collisions detect до mutation.
03.8 LIVE box/mesh volume route если нужен; open/inverted controls для новых APIs; новые names не объявлять verified по introspection.
Gate 03: exact transcripts и interpretation; unsupported case named; timings small (<~2s, stop growth около 1s); owned cleanup.
Если intended mechanism не работает, вернуть design 02 с фактами; не объявлять API отсутствующим из all-throws batch.

### Фаза 04 — schema compatibility и canonical reference authority

04.1 PATCH `validate_specs.py` version/envelope/inventory symbols: explicit known versions и stage-aware QA presence; G-1/G-3 tests.
04.2 PATCH grammar sections 2/3/4/11/12: только frozen version/migration/canonical-runtime distinction; будущие docs English.
04.3 PATCH validator reference schema/joins registry: reserve G-86 centrally; file-qualified resolver, dimensions required targets.
04.4 PATCH input rules/max-input и approved fixture dimensions: raw mm procedure, D8=A origins/ledger, no guessed defaults.
Gate 04: mixed 1.0 model+1.1 QA policies valid; legacy lint не требует QA; new feature under1.0 fails; refs without origins fail.
Два independent bad cases на новый predicate; real messages/exits; earlier S1 gate не требует будущих raw results.

### Фаза 05 — чистая curve library и авторский expansion

05.1 PATCH только `curve_gen.py`: frozen generator validation/points/q, exact plane mapping, finite/duplicate/360 checks.
05.2 PATCH только `curve_gen.py`: chord diagnostic и proven bound/suggestion; no Max interpolation promise, independent known answers.
05.3 PATCH только `expand_curves.py`: draft expansion, --project-dir dependency binding/read-only upstream, origins, guarded out/rollback.
05.4 PATCH тот же CLI: readonly check/suggestion, selector/exit rules; read stored bytes повторно, не только in-memory model.
Gate 05: deterministic repeated bytes; count/plane/axes negatives; cm/mm normalized fixture; failed write оставляет input unchanged.
Old 28-point recipe residual отдельно пересчитать against a=600,b=180; результат не freshness/live claim.

### Фаза 06 — static generator/ref checks и coherent example

06.1 PATCH validator G-84/G-85 и existing G-42 joins; missing generator gives named compatibility SKIP, не required form SKIP.
06.2 PATCH grammar §8.2/§9.7 + max-nurbs authoring contract: points primitive, draft authoring/lock, correct lattice/sweep scope.
06.3 PATCH new generated recipe only: template spec=filename stem; no placeholder points in executable fixture.
06.4 PATCH approved coherent fixture: instantiated nurbs.json/spec=nurbs, dimensions refs/ledgers/project identity; lock через владельца.
Gate 06: old examples hashes unchanged; recipe lint отдельно; actual project --build/warnings-as-errors проходит без fake SKIP acceptance.
Changed generator+points with fixed dimensions intent FAILs G-86; changed points only FAILs G-85.

### Фаза 07 — unit helper и strict preflight

07.1 PATCH `scene_units.py`: certified enums/factors, dimensional expression helpers, inline preamble/receipt fragment.
07.2 PATCH env_preflight: unit capture/scoring и required-complete; missing plugin fields не inherit false-as-absent для QA.
07.3 PATCH unit docs: mathematical examples отдельно от executed unit certificate; display units metadata only.
Gate 07: finite positive scale/type gates; preamble before mutation; bare emit NOT_EVALUATED; captured incomplete fails strict mode.
Literal unchanged angles/weights/percent/counts и converted lengths проверить по exact dimensional sink inventory.

### Фаза 08 — massing/facade/assembly граница единиц

08.1 PATCH build_spec render_ms+verify_script: all Box dimensions/pos и group pivots; JSON arithmetic unchanged.
08.2 PATCH facade_tables consumed envelopes: cm/deg/version/project gate; CSV headers/values unchanged, no geometry conversion here.
08.3 PATCH place_components render_ms+shape checks: prototype dimensions, z−h/2 then convert pos, WAL cells, rotation unchanged.
08.4 PATCH approved computed-output write policy в этих owners: validate all bytes прежде публикации; no unimplemented overwrite promise.
Gate 08: canonical JSON/CSV compare in two temp dirs; adaptive MS deterministic; invalid units/receipt fail before deletes.
Live smoke physical Box/base-Z/rotated panels/native mm и non-1 scale; scoped identities, zero assembly modifiers.
Если multi-file atomicity не guaranteed, transaction manifest+detect/refuse incomplete pair обязателен; partial output не ready build.

### Фаза 09 — NURBS boundary/library first-call propagation

09.1 PATCH library optional scene-native args: merge/tessellation initial forwarding; explicit physical defaults safe for manual calls.
09.2 PATCH library shell decision: approved canonical threshold policy forwarded явно; raw native 0.001 не решает физическое наличие shell.
09.3 PATCH build_nurbs section_literal/dependent/settings/tessellation/render: points, thickness, merge, diagrid; no double derivative scale.
09.4 PATCH expected_census/self_check/verify_script: equality везде одинаково; revision guard/reload и receipt before mutation.
09.5 PATCH load/normalise/version: generator metadata validated but formula never geometry primitive; known schema preserved.
09.6 PATCH build_nurbs.main/write_bytes: validate обоих payloads до publication, ownership/refusal и JSON+MS transaction/recovery по A-WRITE.
При input/output nurbs.json по одному пути сохранить исходные bytes/hash (включая draft) до записи; failure/interruption не уничтожает авторский input.
Controlled owner replacement допустим только по frozen policy; rollback восстанавливает previous complete pair/input, incomplete pair не build-ready.
Gate 09: old normalized canonical data consistent; emits under mm/cm/m/scales measured same physical shape/merges/shells.
Gate 09 также требует M34 для NURBS: differing destination refusal, fault между JSON/MS publication и same-path draft recovery.
Threshold tests ниже/equal/выше .001 cm + zero; percentages/seed mapped только по calibrated semantics.

### Фаза 10 — определённый QA plan, emit и assessor

10.1 PATCH grammar + validator inventory/QA dispatch: G-87…G-90, frozen configuration shape, no result fields; P8 recheck only.
10.2 PATCH init_project: scaffold_qa draft и fresh/seeded parity; empty plan не verdict; no forced conversion legacy stubs.
10.3 PATCH qa_check offline emit: dependencies/hashes/expected IDs/requests/run-context/read-only batches; no Python pipe/TCP import.
10.4 PATCH qa_check parser: exact wire/errors/START/END, bool/nonfinite rejection, quantity dimensions, no zero defaults/zip truncation.
10.5 PATCH qa_check oracle: finite arc/span bounded solver, independent controls, numerical interval acceptance; form vs structural report.
10.6 PATCH qa_check assess/aggregation: exact >0 denominator, required coverage/hash drift, immutable evidence refs, external results.
10.7 PATCH max-qa + coherent fixture QA plan: inference activation и documented collect leg; frozen plan before measurement.
Gate 10: full offline mutation matrix §11; good synthetic evidence оценён, bad evidence refuses, NOT_EVALUATED never PASS.
Synthetic fixtures доказывают evaluator, **не live model QA**; реальные Max results ещё требуют фазу 12.

### Фаза 11 — обязательный correctness branch: объёмы и видимый wall-host

11.1 READ/ASSESS: source и live scoped evidence независимо проверяют dimensional G-82 и visible full host filling opening.
11.2 DESIGN/QUESTION: при дефекте stage owner утверждает narrow correction; recommendation keep host as explicit hidden/reference/non-rendering carrier, cells — delivered solids.
Роль/видимость/renderer flag/scope/resume semantics должны быть точными; не считать hidden выключенным для всех volume APIs автоматически.
11.3 PATCH volume owners: `_check_wall_tiling`, `_g82_wall_tiling_volume`, grammar/current contract и QA используют одобренный cm³ policy.
11.4 PATCH wall owners: утверждённое host representation в assembly+massing integration; preflight ownership/rollback protects foreign nodes.
11.5 REBUILD/MEASURE только rehearsal: one wall opening, deliberate active host negative, no-gap/no-overlap control, original counts scoped.
Gate 11: нет cm³-vs-cm² comparison в новом required gate; intended visible solids имеют openings; QA обнаруживает восстановленный full host.
Старые exact-zero P6 measurements остаются historical evidence; они не доказывают этот visibility fix.
**Нельзя закончить «реализация QA завершена» с заведомо непроходимой правильной wall gate.** Исправление prerequisite delivery.
Нет одобрения/не работает correction → статус BLOCKED, численная причина и owner question; не exclusions/auto-repair/tolerance widening.
Если narrow verification disproves дефект в actual scope, приложить discriminating evidence; branch correction не нужен, gate всё равно доказан.

### Фаза 12 — live acceptance: emit → MCP collect → assess

12.1 AUTHORISED REHEARSAL: coherent generated vault + canonical chain; expectations frozen before fileIn, offsets/roles известны.
12.2 REPLAY: три реальные загрузки каждого applicable stage, receipt/name sets/counts/dimensions по каждому pass; не production rebuild.
12.3 COLLECT: агент последовательно выполняет bounded generated MS через `3dsmax-mcp_execute_maxscript`; absolute forward-slash paths.
Tool envelope/result проверяется на errors/timeouts/`__MCP_MS_ERR__`; full raw responses сохраняются immutable файловыми tools.
12.4 ASSESS offline: current locked specs+request+captures; exact sets и >0 comparisons; не Max PASS text и не build counters.
12.5 MATRIX: cm/1, mm/1, m/1, mm/10, cm/2; каждый supported standard enum отдельным bounded case до general-support claim.
12.6 FORM: counts 7/13/25/41 + original recipe + cv_grid/straight controls; max/mean/RMS/sample IDs, wrong-axis/crown/span cases.
12.7 NEGATIVES в rehearsal: moved/missing panel, plain copy, wrong surface role, shifted form, active full host, wrong scale/double derivative.
12.8 CLEANUP rehearsal: collect names then delete by names, два passes; исходная сцена/foreign nodes intact; delivered model retain.
12.9 PRODUCTION QA: read-only collect/assess при unchanged units/frame/receipts; missing receipts → STOP missing binding (§5.5), не auto-fix.
Gate 12: все required checks PASS с exact coverage, valid controls, max sampled within approved threshold и bounded solver budget.
Если desired form не проходит, вернуть owner authoring/count/model-kind вопрос; новый kind отдельно утверждается, tolerance не меняется.
Если Max workload превышает budget, batching/design revise; не escalated freeze probe и не dropped samples.

### Фаза 13 — active docs, handoff, regeneration и archive gate

13.1 PATCH active AGENTS/PLAN/SKILL/orchestrator/01 workflow: S5 last geometry builder, S7 gate, no cancelled-QA directives в current routing.
13.2 PATCH max-input/massing/nurbs/facade/components/assembly и 07/08/09/11/14 unit/QA notes только identified contradictions.
Stale Sweep attach/tension=1/current bug directives исправить по source+executed facts; history `_p6-contract`/incidents не search-replace.
13.3 PATCH CHECKPOINT future queue/status/evidence: planned/offline/live различать; current reopening отдельно от dated cancellation.
13.4 REGEN decision: old examples byte-identical; generated adaptive artifacts делаются owner builders в approved **новой fixture copy**.
Old examples/*.ms могут остаться historical cm/1-only; обозначить это в active docs. Не требовать их equality с новым emitter output.
Если нужно shipping current adaptive example scripts, owner regenerates новую curated copy, validates/fileIn/measures её и публикует только после gate.
Нельзя hand-edit generated .ms или молча заменить historical examples; изменение их статуса/места — отдельное явное решение.
13.5 HANDOFF: locked model specs+QA plan, raw/results/receipts paths/hashes, units certificate, scope/counts, numerical worst errors/limitations.
13.6 ASK archive permission: только после PASS; current `python scripts/install_skill.py --target archive`; global installation отдельно.
Archive inspect collect_files/extracted bytes; timestamps ZIP означают archive bytes не necessarily deterministic; raw runs не packaged.
Gate 13: active docs match runnable CLI, required modules shipped, examples history intact, measured QA exercised, no unclosed delivery blockers.

## 11. Fault injection: обязательная матрица отказов

Мутации только owned temporary copies/evidence fixtures; каждая имеет known-good control и exact observed message/exit/check ID.
На **каждый новый G predicate минимум две независимые плохие мутации**; runtime family тоже проверяет success и failure, не только parser.

| ID | Мутация/случай | Обязательный результат/owner gate |
|---|---|---|
| M01 | Missing/unknown SystemType; scale 0/NaN/negative | Refusal до mutation; 07/08 |
| M02 | mm correct + ignored SystemScale; wrong c/f | Physical measurement failure; 12 |
| M03 | Same system tuple, changed display labels | Geometry unchanged; metadata alone не меняет verdict; 03/12 |
| M04 | Changed units between stages/batches; stale receipt | INVALID/INCOMPLETE run; no partial PASS; 07/10 |
| M05 | cm² threshold для cm³; area power used for volume | Dimensional policy reject; 10/11 |
| M06 | tolerance 0 then hidden `or .5`; arithmetic reused as form | Reject illegal fallback/policy; A-TOL fixtures; 04/10 |
| M07 | shell 0, below/equal/above .001 cm in native m/mm | Census/geometry consistent with frozen rule; 09/12 |
| M08 | Missing initial merge/default forward; only late setter | Seam/approximation negative detects physical effect; 09 |
| M09 | count 1, count true, wrong plane, radius≤0 | G-84 fails, exact reason; 05/06 |
| M10 | angle delta 0/>360; wrong kind-specific radius keys | G-84 fails; 05/06 |
| M11 | full360 count2/3; rounded adjacent duplicate/zero chord | Degeneracy refusal, no divide by zero; 05 |
| M12 | Point shifted 1 cm; stored count mismatch | G-85 failure; 06 |
| M13 | Generator+points changed, dimensions reference fixed | G-86 reference-join failure; 06 |
| M14 | Unequal lattice counts; independent valid sweep counts | First fails G-42; second remains valid; 06 |
| M15 | New feature in1.0; unsupported future version | Version/feature refusal; known1.1 no WARN; 04 |
| M16 | Missing/mismatched origin/ref; circular authority | G-86/G-90 failure; 04/10 |
| M17 | Required check removed/disabled, no analytic targets | G-88/profile failure, not structure masquerading as form; 10 |
| M18 | Legacy result fields in config; wrong key/container | G-87 failure; empty scaffold not PASS; 10 |
| M19 | Bad physical tolerance/sample bounds; bad dependency | G-89/G-90 failures; 10 |
| M20 | P8 recheck vs P7/P9 rechecks | P8 accepted; P7/P9 rejected; 10 |
| M21 | Zero observations/compares; missing/extra/duplicate sample | Exact ID denominator failure, no zip truncation; 10 |
| M22 | Same counts but substituted IDs; duplicate node name | Identity/coverage ERROR, no nearest-name join; 10/12 |
| M23 | success=true plus sentinel/error; timeout/missing END | Batch ERROR/INCOMPLETE; 10/12 |
| M24 | Undefined evalPos/nonfinite/bool numeric/default-zero | Explicit error, no zero vector; 10 |
| M25 | Wrong project/hash/request/run/frame/session | Binding failure; 10 |
| M26 | Double world transform/normalization/derivative scaling | Wrong-space/physical measurement failure; 09/12 |
| M27 | Pick offset instead of design base; domain [0,1] assumed | Role/domain failure and observed form error; 12 |
| M28 | Wrong half ellipse/infinite span/oracle from same points | Finite reference/span/control failure; 10/12 |
| M29 | One sample max>tol, low mean; solver exhausted | FAIL/INCOMPLETE, never mean-based PASS; 10 |
| M30 | Missing/moved/rotated panel or ordinary copy | Actual census/placement/baseObject failure; 12 |
| M31 | WAL gaps+overlap cancel volume; insufficient thickness | Occupancy/full-thickness FAIL even with equal total; 11/12 |
| M32 | Full visible host fills opening while cell table correct | Required WALLS FAIL; approved host correction then PASS; 11 |
| M33 | Foreign node/name collision; arbitrary cleanup | Safe refusal/foreign report; fixture node survives; 03/12 |
| M34 | Differing output/interrupted JSON+MS, включая NURBS same-path draft input | Refusal/recovery; input и prior complete pair intact; 05/08/09.6 |
| M35 | Stale library definition loaded; unsupported capability | Tested revision guard refuses/reloads approved route; 09 |
| M36 | Fake replay/scatter PASS from single count snapshot | Required replay incomplete; optional scatter no determinism claim; 10/12 |
| M37 | Optional moulding open/inverted mesh/invalid corner | MOULD topology/volume failure if phase16 enabled; not core before approval |

Не цитировать выдуманный refusal text заранее. Заполнять real transcript после выполнения; policy expected здесь, observed позже.

## 12. Опциональные фазы из полного исходного брифа

### Фаза 14 — генераторы колец (исходная фаза 5), отдельное approval

14.1 DESIGN patch `_form-rings-design.md`: profile_gen circle/ellipse/rounded_rect, explicit sampling/counts, simple CCW/no holes.
Freeze input owner/provenance по D8=A и compatibility map kinds; `profile_cm` остаётся derived straight ring, элемент Z-prism.
Current rect_of/Box-only не строит эти rings; **нужен настоящий новый polygon-prism polyop emitter**, не generator-only patch.
14.2 PROBE в authorised rehearsal: convertTo Editable_Poly/createVert/createPolygon route, winding/caps/triangulation/volume/topology APIs.
14.3 IMPLEMENT только approved mesh owner: rectangle fast path отдельно, concave simple ring и no-hole validity, zero modifiers.
14.4 STATIC: new IDs centrally after core; exact distinct/winding/degenerate/self-intersection guards, ≥2 mutations/rule.
14.5 LIVE: three builds; exact name sets/topology, bbox lengths cm и volume cm³; native mm/m/non-1 coverage.
Rounded_rect ideal area = w·d−(4−π)r²; circle/ellipse ideal formulas; polygon-exact area отдельно, не путать с ideal intent.
Volume error budget выводится из chord/area loss и height; не threshold «на глаз» и не oracle из emitted mesh vertices.
Gate 14: independent analytic vs discretization accounting и closed mesh; optional module/docs/example published только после gate.

### Фаза 15 — широкий intent и per-level footprints (исходные 6/7), design-only

15.1 PATCH `_form-intent-probes.md`: расширения beyond narrow required reference, probe vocabulary, limitations, no formula-source DSL.
Минимум для QA уже core; general intent/continuity/global fidelity не внедрять в этот design-only scope.
15.2 PATCH `_form-per-level-footprint.md`: разные floor_plates outlines, setbacks/rotation/taper, correspondence rings/loft possibility.
Impact map обязателен: G-29, area formulas, site footprint consumers, core containment, grid columns, facades/runs/walls/components.
Не считать same vertex count достаточным для валидного loft или automatic nonprismatic assembly.
Freeze будущие source authority/per-level areas/levels/mapping/constraints и migration до любого отдельного implementation proposal.
Gate 15: только записки и owner questions/estimate; **кода нет**, старое единое footprint поведение сохраняет historical статус.

### Фаза 16 — профильные полосы одним mesh (исходная 8), approval отдельно

16.1 READ ONLY если доступна сцена исходного теста: class/count existing strips; нет сцены → explicit NOT_RUN, не blocker design.
16.2 DESIGN `_form-mouldings-design.md`: отдельный mouldings.json, profiles/bands, immutable seven massing kinds; не Z-prism kind.
Profile local `(out_cm,z_cm)` simple closed без undercuts: по высоте один interval [d_in,d_out]; source params dimensions/ledger.
Contour refs simple CCW; band profile_ref/ring_ref, z_cm **или** level_index+offset_cm, repetitions, layer, instance policy.
Miter formula P+d(n1+n2)/(1+n1·n2); denominator около 0/collinear/backtracking, sign/outer normals явно определяются.
Miter limit **FREEZE units**: recommendation dimensionless ratio displacement/abs(d) с special d=0 rule; alternative max_miter_cm отдельный key.
Не сравнивать ratio с cm; default пользовательский/ledger, не произвольная константа.
Offset validity для signed inward/outward extrema **и критических событий/всего нужного диапазона**, не только одного max|d| ring.
16.3 STOP/QUESTION: schema location/name, profile parameter ownership, instance default, topology algorithm и limits; только после «да» probes/code.
MOULD-a rectangle+concave ring watertight mesh; known open edge control калибрует prospective polyop.getOpenEdges.
MOULD-b winding/normals и signed volume; known closed/inverted box controls, not bbox volume.
MOULD-c bounded mesh-size ladder 100/500/2000/5000 vertices только при предыдущем <~1s; stop before freeze.
MOULD-d 10 instances via copy/baseObject; plain-copy negative реально false; prototype counted отдельно.
MOULD-e face material-ID write/read calibration только IDs, без материалов; invalid ID semantics не предполагают throw.
MOULD-f optional Sweep/add_modifier/collapse control после отдельного approval; не main emitter, measured attach/collapse ещё нужны.
MOULD-g optional closed rail sweep sharp-corner probe; known working rail control; не replacing mandated one-band mesh design.
16.4 IMPLEMENT proposed build_mouldings/max-mouldings/grammar/validator/inventory/scaffold/example после measured routes.
Topology algorithm FREEZE до counts: triangulation/caps/seam indexing дают exact predicted vertex/face counts, не универсальная догадка n·m.
Identical contour/profile: один prototype+instances с declared hidden prototype role; changing contours — отдельные meshes, не per-level implementation без phase15 approval.
Mesh vertices/level translations converted once; indices/normals/unitless ratios не масштабируются; one watertight mesh per band.
Independent volume ∫[A(d_out(z))−A(d_in(z))]dz; Simpson exact для quadratic segments только при неизменной offset topology/validity.
Critical topology changes/invalid offsets reject/subdivide по approved math, не universal Simpson exact claim для collapsed/concave events.
16.5 LIVE gate: three builds, exact counts, bbox cm, no open edges, volume cm³ within independent error budget, instance control.
Material handoff: material не propagates с prototype по историческому P15; face IDs data допустимы, P7/UV всё ещё out of scope.
Gate 16: measured negative topology/corner controls и cleanup; core QA включает moulding checks лишь после approved feature presence.

## 13. Риски, остановки и rollback

| Риск/сигнал | Немедленное действие | Возобновление/rollback |
|---|---|---|
| Неодобренная схема/leaf/threshold/API assumption | STOP design, точный вопрос и рекомендация | Вернуться к02, не кодировать default |
| Max dialog/timeout | Не повторять mutating call; cheap bridge status при разрешённом live scope | User closes dialog; read-only reconcile scene, fresh session если нужен |
| Недоказанная API absence | Сохранить exact exception, known hit/miss/bogus calibration | Исправить probe, не переписывать guide по подозрению |
| Units/library/frame/receipt drift | Invalidate affected run/build, сохранить raw | Новый owned replay после разрешения; foreign geometry не rescale |
| Numerical error сравним с tolerance | INCOMPLETE и precision report | Improve capture/solver/coordinates с owner; tolerance не widen |
| Partial file transaction | Не считать ready output, refuse build | Restore own previous complete pair или новая temp generation; preserve journal |
| Visible host/volume defect confirmed | QA FAIL, открыть narrow stage-owner branch11 | Approved source correction, regeneration и свежие measurements |
| Shape fails under approved count/budget | Показать intent vs measured max/worst sample | Owner changes draft construction/count; new kind или scope approval отдельно |
| User work/foreign node collision | Refuse destructive build, record collision | Новое owned namespace/scene approved; не delete unrelated |

Rollback code: сохранить исходный patch/diff, откатить только собственный coherent patch после проверки user edits; no git reset/clean.
Rollback artifacts: prior complete bytes retained; immutable raw report не overwrite, новый run ID; failed reports остаются evidence.
Rollback scene: fixture cleanup по known-owned names, collected before deletion, два passes; user production модель QA не меняет.
Не использовать `formattedPrint` никогда; не synthetic parent*ID literal; не 20-modifier ladder; не отсутствующие plugin/Rhino tools.
Top-level .ms local требует fileIn-safe function wrapper; bare fn through execute bridge не route для новых long helpers.
One script/call under ~2s; result `success:true` без проверки sentinel/END/coverage не успешное исполнение.
After Max restart follow bridge/client reconnect protocol; не трактовать .NET FileStream failure как proof dead pipe.

## 14. Определение готовности и prompts

Core DONE только после всех обязательных 01–13 gates; optional 14–16 отмечаются отдельно, не скрываются как implementation done.
- Approved contract/версии/тolerances/ownership; канонические cm и explicit-mm normalization действуют и покрыты fixtures.
- Form source authority dimensions → generator → points; changed construction не изменяет independent intent без owner.
- Все physical sinks/defaults/cutoffs converted once; units/precision/domain/seed/reload/receipt semantics measured в supported matrix.
- Legacy examples byte-identical, new adaptive artifacts owner-generated и measured; no hand-edited MS, policy regeneration documented.
- Static rules выделены и mutated; old baseline totals historical; new stage/recipe/project gates различаются.
- Defined qa.json locked plan; raw outside pipeline immutable; qa-results отдельный report; fresh/seeded draft не fake PASS.
- Real automatic emit → sequential MCP collection → offline assess exercised; Python не имеет выдуманного self-connection.
- Exact identity sets и N_expected=N_observed=N_compared>0; все required check families/landmarks/comparator controls выполнены.
- Form precision PASS отдельно от legacy structural result; sampled conformance честно обозначено; max gates, не mean.
- Visible wall host и dimensional volume correction закрыты при необходимости; отказ approval означает BLOCKED, не DONE.
- Replay отдельный authorised rehearsal; production QA read-only, retain deliverable; foreign nodes/settings не повреждены.
- Active English docs отражают текущую реализацию; историческая отмена/measurements сохранены; executed label только фактическим probes.
- Handoff содержит scope, units certificate, hashes/paths, exact counts/errors, limitations и optional statuses; archive/installation permissions раздельны.

### Start prompt следующей сессии

> Прочитай AGENT_PLAN_form_precision.md и CHECKPOINT/AGENTS. Начни только 01.1–01.2 READ ONLY.
> Locks: canonical cm/native Max conversion, restored P8 config/results split, D8=A уже приняты; не спрашивай их снова.
> До кода предъяви unresolved A-* approvals и точное владение следующего одного patch. Max/build/install/git mutation пока запрещены.
> Выполни одну микрозадачу с gate, сообщи ≤12 строк и остановись. Не интерпретируй этот prompt как approval optional14–16.

### Resume prompt после пройденного gate

> Last PASS: [ID], evidence: [absolute path/hash, actual output], next: [ID]. Approved scope: [exact files/symbols].
> Прочитай frozen design и только relevant source context; проверь user diff и входные hashes/locked status.
> Выполни ровно next ID, затем его gate. Если prerequisite/evidence/approval отсутствует, STOP с конкретной причиной.
> Не меняй tolerances, intent, required coverage, examples history или production model для получения PASS.
> Верни ≤12 строк: files/symbols, actual checks, coverage/errors, status, next ID, user decision если blocked.

### Prompt исправления обязательного blocker

> Blocker: [WALL/VOLUME/FORM/API], observed vs expected: [numbers/IDs], immutable evidence: [path/hash].
> Запроси narrow owner approval branch11 либо authoring branch; QA не auto-repair и не сокращает denominator.
> После approved source patch regenerated owned artifacts и fresh request/run обязательны; старый FAIL не переписывать.
> Gate completion требует measured pass правильной модели и measured fail deliberate negative, иначе BLOCKED.
