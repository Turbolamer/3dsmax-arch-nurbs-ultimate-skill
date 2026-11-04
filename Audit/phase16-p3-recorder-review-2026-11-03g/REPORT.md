# Независимый offline review следующего P3.1 recorder

## Вердикт и границы

**Не запускать final recorder на текущем дереве.** Авторы ещё пишут: при
последовательных чтениях появился `phase16-p3-lease-review-2026-11-03g/`,
пополнились `phase16-p3-main-probes-2026-11-03g/` и
`phase16-p3-data-hardening-2026-11-03g/`, изменялись runtime и тест; затем
появились `phase16-p3-closeout-2026-11-03g/` и
`phase16-p3-layer-identity-design-2026-11-03g/`. Последняя перечисленная здесь
инвентаризация датирована **2026-11-03 19:39:09 UTC** и не является блокировкой
или обещанием полноты на момент запуска. Остановить всех
авторов и все фоновые записи, снова инвентаризировать, проверить содержимое,
затем скорректировать команду ниже и выбрать новый `--out`.

Проверенные байты: `recorder.py` SHA-256
`92127961d6b9f3a163608f12d029ae7d0da1e4e8f64de2cfa065f67b104a493c`,
`README.md` SHA-256
`e16a4d5f5718bb40279bffc6fc084f6127fc5102e559f042758b1e0f4ce93c8c`.
Проведён source review и изолированные вызовы **только извлечённой через AST
функции `observations`** на синтетических строках. Не запускались ни recorder,
ни его selftest, ни реальные suites, ни Max/MCP/git/installer. Ниже нет заявления
о новом test PASS или принятии P3.1.

## Находки

### 1. Неполное discovery даёт видимость полного прогона

`recorder.py:247-253,268-291` запускает только непосредственные
`Audit/test_phase16_p3*.py`, два заданных пути `OPTIONAL_INDEPENDENT` и явные
`--suite`. `--input DIR` лишь включает файлы в hash snapshot, **не исполняет**
тесты в этом каталоге. Поэтому README-команда `README.md:15` не запускает ни
новые suites `03g`, ни ранее известные `test_protection.py`,
`test_witness_model.py`, `test_candidate.py` и `test_p31_offline.py`. За пределами
семи имён `REQUIRED_SUITES` она не требует присутствия ни одного из новых
тестов. Даже известные replay/measurement помечены optional и незаметно исчезнут
из плана, если отсутствуют, если только их не задать явно. Один нераспознанный
или пропущенный nested suite при благополучных остальных способен оставить
`RECORDED_REQUIRES_REVIEW`/exit 0 — **не полный suite PASS**.

Discovery выполняется повторно, но `suites` для выполнения фиксируется отдельно
после первого snapshot (`:460-469,481-483`). Изменение после freeze этого набора
обычно обнаружит следующий snapshot, но добавление и обратное удаление между
ними не обнаруживается; drift в частях дерева, которые не перечислены для
inventory, не обнаруживается вообще. Динамический подбор новых `.py` также
запускает недоверенный entrypoint без whitelist; тесты не sandboxed. До запуска
сопоставить `run.json`/первый `discovered_suites` с независимым утверждённым
списком, а не считать сам discovery доказательством правильности плана.

У любого дополнительного suite minimum равно **1**, а не известному количеству
его методов (`:496`). Например, 1 вместо обнаруженных статическим анализом 32
cleanup-методов может удовлетворить recorder. На просмотренных байтах AST даёт
32 `test_*` у cleanup, 15 у data hardening, 17 у independent layer; это **только
число синтаксических определений**, не run и не гарантия unittest discovery.
После freeze самостоятельно утвердить ожидаемые имена/количество, сравнить с
raw logs и объяснить изменения. Семь старых minimum — тоже нижние границы, а не
проверка имён или точного набора; новый код с тем же количеством не равен
историческому покрытию.

### 2. `unittest`-parse может дать ложно неотклонённый вывод

`observations` (`:363-404`) требует по одной строке `Ran N test[s] in …` и
`OK`, но не связывает их порядком, потоком, с настоящим `unittest` или с самим
запущенным тестом. Даже обратный порядок `OK\nRan 1 test in 0.001s\n` принят
как `UNQUALIFIED_OUTPUT_REQUIRES_REVIEW`, как и напечатанные вручную строки.
Этот статус — не PASS; однако при exit 0, стабильных зафиксированных входах и
остальных хороших результатах `:523-545` может вернуть общий exit 0.

Изолированная проверка функции на синтетике:

| Добавка к `Ran 1 test in 0.001s\nOK\n` | Результат функции |
|---|---|
| стандартное `OK (skipped=1)` вместо `OK` | `REFUSED` |
| `{"skipped": 1}` | `REFUSED` |
| `{"skip": 1}` | `UNQUALIFIED_OUTPUT_REQUIRES_REVIEW` |
| `{"skipped": true}` | `UNQUALIFIED_OUTPUT_REQUIRES_REVIEW` |
| `[  SKIPPED ]` | `UNQUALIFIED_OUTPUT_REQUIRES_REVIEW` |

Это **нетипичные** сообщения/метаданные, не утверждение, что обычный Python
unittest скрывает свой `OK (skipped=1)`. Regex распознаёт не все формы (`skip`
в единственном числе, boolean и bracket-first), а учёт stdout/stderr не сохраняет
межпоточный порядок; произвольный executable вообще может имитировать вывод.
Прочесть raw stdout/stderr и смысл тестов, а не только `observations.issues`.
Лучший будущий recorder — структурированный `unittest.TestResult` в доверенном
runner с именами и outcomes, подтверждённый контролями skip, xfail, unexpected
success, import/collection errors, пустого набора, нескольких runners и
поддельного/разорванного summary; даже он не превращает тестовую модель в live QA.

Уже виден отдельный **семантический ложный PASS при неверной интерпретации**:
`phase16-p3-layer-independent-2026-11-03g/test_independent.py:381-446` содержит
observational tests, которые специально утверждают, что две прежние батареи
**не убивают** in-memory guard mutants. Зелёный статус такого теста подтверждал
бы обнаруженный пробел, а не защищённость guard. Аналогично synthetic cleanup и
lease models не являются проверкой Max, реального cleanup или replay.

### 3. Сохранность ограничена перечисленной выборкой и моментами наблюдения

* Есть полезные pins для четырёх P2 источников, ровно 49 legacy fixtures,
  package, четырёх Main03 файлов, семи старых run manifests и P2 manifest
  (`:208-222,304-319`); остальные файлы деревьев и `--input` в основном только
  сравниваются **с началом текущего прогона**, а не с ранее зафиксированным
  авторитетным хешем. Если старый, но не отдельно pinned Main01/02 или prior
  log был изменён *до* before-snapshot, recorder этого не обнаружит. `HEAD`
  проверяет указатель commit, не tracked/untracked/ignored worktree bytes.
* Snapshot не покрывает весь рабочий каталог. В частности,
  `Audit/_phase16-p3-post-publication-2026-11-03f.json` содержит
  `all_current_preserved_files` с 2023 путями; recorder включает сам JSON
  через glob, но **не сверяет** все 2023 записи с диском. Поэтому требуется
  отдельное read-only сравнение каждого старого пути с этим manifest
  **до и после** прогона, с повторной проверкой SHA самого manifest, отдельным
  журналом missing/drift/unreadable, unlisted и известной разрешённой смены
  runtime/docs; старые файлы и manifest не переписывать. Новый run directory
  учитывать отдельно, проверка тоже не атомарна. Сам по себе исторический
  `phase16-p3-preservation-entry-2026-11-03g/REPORT.md` — лишь более раннее
  наблюдение, а не новая сверка.
* `tree_files` исключает `__pycache__`, `.pyc/.pyo` (`:174-185`), включая
  явно переданный каталог. `-B`/`PYTHONDONTWRITEBYTECODE=1` предотвращает
  **запись**, но не запрещает чтение существующего валидного bytecode; уже
  найдены `.pyc` в `scripts/__pycache__`, а `wall_surface_inputs.py:30-33`
  импортирует `scene_units`/`validate_specs`. Привязать запуск к заранее
  отсутствующему отдельному `PYTHONPYCACHEPREFIX` под approved temp и проверить
  у дочерних Python-процессов окружение; альтернативно доказать отсутствие
  используемых caches. Не удалять чужие cache-файлы. Это снижение риска, не
  гарантия для запускающих собственные процессы программ.
* Снимки не атомарны, не являются lock, не видят изменение с восстановлением,
  промежуточные события и состояние после exit-snapshot. Tests исполняются с
  правами пользователя и могут писать вне наблюдаемого множества; subprocess
  timeout может оставить descendants (`:407-430,511-514`). `process-exit.json`
  ставится непосредственно перед return, а не после внешнего подтверждения
  завершения; исключение, прерывание или I/O ошибка может оставить неполный
  каталог. Сохранять его и разбирать, не перезаписывать и не объявлять PASS.
* `no_link_ancestors` + последующее открытие и `reserve_output` — отдельные
  операции, а не защита от произвольной конкурентной подмены пути/жёстких ссылок;
  нет эксклюзивного замка всего дерева. Это граница доверенной sequential
  среды, а не утверждение, что подмена происходила. `README.md:84-94` правильно
  оговаривает многие ограничения; формулировку `exit 0 … recorder health only`
  нельзя расширять до полноты или сохранности всего репозитория.

## Предлагаемая команда после stop/freeze

Это **точная команда для наблюдавшихся путей**, а не инструкция запускать её
сейчас. Из корня репозитория, в Bash на Windows; сначала подтвердить, что все
пути существуют, нет reparse points, `%LOCALAPPDATA%/Temp/opencode` доступен,
output **ещё не существует**, а выбранный `PYTHONPYCACHEPREFIX` не существует и
никто его не создаёт. Если путь занят, выбрать другой непересекающийся новый.
Приведённый `recorder.py` сам вызывает `git rev-parse` на каждом snapshot
(`:256-265`): **пока ограничение «никаких git» остаётся в силе, эту команду
исполнять нельзя**. Для no-git режима нужна отдельно согласованная/проверенная
новая реализация recorder; этот review старые файлы не меняет.

```bash
PYTHONPYCACHEPREFIX="C:/Users/Turbolamer/AppData/Local/Temp/opencode/phase16-p3-empty-pycache-2026-11-03g" python -B Audit/phase16-p3-recorder-next-2026-11-03f/recorder.py \
  --out Audit/phase16-p3-next-final-2026-11-03g \
  --suite Audit/phase16-p3-replay-tests-2026-11-03f/test_replay_safety.py \
  --suite Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py \
  --suite Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py \
  --suite Audit/phase16-p3-lease-next-2026-11-03f/test_witness_model.py \
  --suite Audit/phase16-p3-layer-reader-2026-11-03f/test_candidate.py \
  --suite Audit/phase16-p3-layer-reader-2026-11-03f/test_p31_offline.py \
  --suite Audit/phase16-p3-cleanup-model-2026-11-03g/test_cleanup_model.py \
  --suite Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py \
  --suite Audit/phase16-p3-layer-independent-2026-11-03g/test_independent.py \
  --input Audit/phase16-p3-recorder-next-2026-11-03f/README.md \
  --input Audit/phase16-p3-recorder-next-2026-11-03f/selftest.py \
  --input Audit/phase16-p3-replay-tests-2026-11-03f \
  --input Audit/phase16-p3-measurement-next-2026-11-03 \
  --input Audit/phase16-p3-metadata-design-2026-11-03 \
  --input Audit/phase16-p3-layer-design-2026-11-03 \
  --input Audit/phase16-p3-main-probes-2026-11-03f \
  --input Audit/phase16-p3-lease-next-2026-11-03f \
  --input Audit/phase16-p3-runtime-review-2026-11-03 \
  --input Audit/phase16-p3-runtime-hardening-2026-11-03f \
  --input Audit/phase16-p3-layer-reader-2026-11-03f \
  --input Audit/phase16-p3-edata-design-2026-11-03f \
  --input Audit/phase16-p3-grid-observer-design-2026-11-03f \
  --input Audit/phase16-p3-controller-incident-2026-11-03f \
  --input Audit/phase16-p3-hardening-independent-2026-11-03f \
  --input Audit/phase16-p3-preservation-2026-11-03f \
  --input Audit/phase16-p3-closeout-2026-11-03f \
  --input Audit/phase16-p3-cleanup-model-2026-11-03g \
  --input Audit/phase16-p3-closeout-2026-11-03g \
  --input Audit/phase16-p3-data-hardening-2026-11-03g \
  --input Audit/phase16-p3-layer-identity-design-2026-11-03g \
  --input Audit/phase16-p3-layer-independent-2026-11-03g \
  --input Audit/phase16-p3-lease-independent-2026-11-03g \
  --input Audit/phase16-p3-lease-review-2026-11-03g \
  --input Audit/phase16-p3-main-probes-2026-11-03g \
  --input Audit/phase16-p3-metadata-independent-2026-11-03g \
  --input Audit/phase16-p3-preservation-entry-2026-11-03g \
  --input Audit/phase16-p3-recorder-review-2026-11-03g
```

Директории `03g` в команде охватывают известные на момент inventory model и
её dependency `reference_model.py`, pre-edit snapshot, новый independent test и
его runner/logs, выключенный lease review test, новый lease review, probe sources
и results, metadata/disabled layer-identity design, closeout и preservation record.
Наблюдавшиеся прямые JSON/MD-файлы `Audit/_phase16-p3-*2026-11-03g*`
автоматически хешируются glob-ом `:274`.
`run_checks.py`, `run_offline.py`, generators и selftest **не являются** suites
этого прогона: они пишут собственные логи/требуют другие аргументы или не дают
single unittest summary; запускать их вместо явных tests нельзя.

**Исключение, которое необходимо сохранить видимым:**
`Audit/phase16-p3-lease-independent-2026-11-03g/test_review.py.disabled` —
существующий отдельный observational unittest entrypoint, а не разрешённый
`--suite`: `validate_inputs` (`:322-333`) принимает только суффикс `.py`.
Команда выше его **хеширует, но не выполняет**. Нельзя честно назвать её одним
полным прогоном всех релевантных suites. После отдельного решения владельца о
запуске disabled observational test возможна команда:

```bash
python -B Audit/phase16-p3-lease-independent-2026-11-03g/test_review.py.disabled -v
```

Её нужно выполнять только после того же freeze с независимым безопасным
exclusive-capture raw stdout/stderr, exit/status, до/после хешами и проверкой
окружения; результат не попадает в recorder и не является защитным PASS.
Альтернатива — согласованный новый recorder с явной поддержкой этого exact
entrypoint и собственной проверкой; ни переименование оригинала, ни
автоматическое включение `.disabled` недопустимы. После freeze повторить поиск
новых файлов/зависимостей, классифицировать каждый suite и добавить свежие
`--input`/`--suite`; README-команда и эта инвентаризация не предсказывают будущие
файлы.

Наконец, отказ или failure прежних runtime/replay проверок нельзя ослаблять ради
зелёного verdict. Любой результат — лишь ограниченное offline свидетельство;
прежние live blockers и P3.1 NOT ACCEPTED не отменяются exit 0.
