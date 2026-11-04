# Phase 16 P3.1 — независимый OFFLINE audit metadata и safety design

**Вердикт: BLOCKED / INCOMPLETE; P3.1 NOT ACCEPTED.** Это анализ исходников и
сохранённых свидетельств, а не реализация, компиляция MAXScript или live-проверка.
На проверенном снимке runtime есть исполняемые запреты `INCOMPLETE_PRECREATE` и
`INCOMPLETE_REPLAY`. Их необходимо сохранять; они не доказывают безопасность
скрытого за ними construction/replay path и не распространяются задним числом на
ранее выпущенные `.ms` (`scripts/wall_surface_runtime.py:821-864`,
`Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md:40-60`).

**Граница работ:** только чтение production, тестов и прежнего evidence. Новых Max
или MCP вызовов нет. Offline тесты не запускались; настоящий отчёт — source/design
review, не результат тестирования и не утверждение о текущем состоянии Max. Ранее
зафиксированный controller incident оставил кандидата residue; до решения
оператором не выполняются автоматическое удаление, reset, save, re-arm или новый
mutating probe. Для любой будущей операции нужна новая независимая оценка состояния
(`Audit/phase16-p3-controller-incident-2026-11-03f/report.md:113-130`).

## 1. Версии, границы и основной вывод

Контракт требует сравнивать фактическое состояние или fail closed, запрещает
подмену/удаление wall при replay и требует cleanup лишь точных новых ссылок с
проверкой удаления (`Audit/_phase16-p3-contract-2026-11-02e.md:28-33,39-48`).
Предыдущий metadata review рассматривал **другой** runtime SHA `bd582b…`
(`Audit/phase16-p3-metadata-design-2026-11-03/README.md:10-25`). В текущих
проверенных bytes SHA `3a7a38…` изменились важные детали:

* `graphSnapshot` теперь расположен **перед** `evaluatedSnapshot` в
  `nodeSnapshot` (`scripts/wall_surface_runtime.py:774-798`), в отличие от
  старого вывода о порядке. Но сам обход/сбор значений не доказывает
  допустимость графа или отсутствие прежней неявной оценки. Более того, в
  предложенном повторном сравнении правая сторона `nodeSnapshot` сначала вся
  вычисляется, включая `snapshotAsMesh`, а `same baseline …` запускается лишь
  после возврата (`:930-932`).
* Отсутствующее явно запрошенное node property теперь вызывает `require`, а
  `getUserPropBuffer` копируется (`:783-790`); старые замечания про `absent`
  sentinel и некопированный buffer нельзя автоматически переносить на этот SHA.
  Семантика типа, конечности и detached-состояния остальных данных остаётся
  непроверенной.
* Текущий cleanup **не удаляет** ни один `createdRefs`/`conversionRefs`, а
  сохраняет их как residual (`:979-1023`). Это безопаснее попытки удаления по
  повторно найденному handle при неизвестной идентичности, но не реализует
  договорный cleanup доказуемо безопасного случая. Replay и строительство сейчас
  останавливаются раньше этого кода.

Матрица ниже разделяет **вывод по тексту source** и предположения о Max API.
Не показано, что непроверенное свойство обязательно существует, что ошибочная
ветка реально исполнилась в Max, или что имел место вредоносный побочный эффект.

## 2. Приоритетные source findings

### A. Mandatory native / specified-normal metadata — BLOCKER

`polySnapshot` записывает часть V/E/F, face loops, flags, smoothing, mat IDs,
maps, VData/EData и selection (`scripts/wall_surface_runtime.py:644-695`). Он
**не содержит отдельного чтения base specified-normal table**: per-face-corner
specified flag, corner → normal ID, explicit flag и компоненты вектора,
идентичность/разделение или sharing. `evaluatedSnapshot` читает `getNormal` один
раз на evaluated vertex (`:704-714`), а не указанные base corner records. Поэтому
равные computed vertex normals, bbox, topology или triangles не являются
свидетельством равенства этих обязательных метаданных. Перестановка/разделение
ID может требовать отдельной проверки даже при совпавших векторах.

Требуемая граница: либо полный **read-only**, detached, типизированный base reader
для всех поддержанных face/corner/normal записей, включая доказанные связи и
границы диапазонов, либо независимый доказанный predicate отсутствия
соответствующего состояния **с отрицательным контролем добавления каждого вида**.
Если различение отсутствия/нечитаемости или мутация base недоступны — INCOMPLETE;
не называть category optional, если она обязательна контракту. Для dead entries
нужен доказанный запрет/инвариант либо собственный reader; сейчас ставится только
`#("dead")` (`:651-660,670-675,683-692`).

`Edit_Normals` и `meshop.getFaceRNormals` в раннем design — кандидаты для
отдельных контролей, а не доказанный read-only доступ к base; добавление modifier,
collapse или topology repair к replay wall не допустимы как способ чтения
(`Audit/phase16-p3-metadata-design-2026-11-03/README.md:137-160`). Проверять нужно
отдельно: изменение одной specified/explicit flag, вектора и same-vector
split/merge или ID association, с независимым подтверждением мутации; затем
продемонстрировать отличие/отказ именно production reader **до** оценки. Иной
выбор/эквивалентность ID требуется сначала обосновать измеренной семантикой, а
не угадывать.

Помимо normals, остаются неустановленными face-edge/edge-face incidence,
внутренние diagonals/triangulation, полная доменная граница map/hidden channels,
native/custom компонентные данные и адекватность dead sentinel. Существующие
читатели полезны, но полнота не следует из перечисленных имён API
(`scripts/wall_surface_runtime.py:654-695`;
`Audit/phase16-p3-metadata-design-2026-11-03/README.md:27-40`).

### B. Descendants/subAnims и Shell — BLOCKER

`graphSnapshot` следует по `refs.getReference`, для посещённого controller
проверяет whitelist класса и допускает `numKeys == 0 or -1`, затем считывает
generic properties (`scripts/wall_surface_runtime.py:608-643`). В нём нет
отдельного полного обхода `numSubs` / `getSubAnim`, доказательства эквивалентности
subAnim и reference graphs или проверки каждого descendant и его роли. Значение
`-1` на композитном controller не свидетельствует об отсутствии ключей, wire,
constraint или script в его детях. Класс сам по себе также не доказывает
статичность, а значения в текущий момент не исключают off-time key.

До разрешения оценки требуется ограниченно, с проверкой каждого шага и полноты,
разобрать допустимые transform/position/rotation/scale и visibility контроллеры,
их все достижимые subAnim descendants, а также Shell, param blocks и все
анимируемые поля. Для каждого controller path нужны exact identity, поддержанный
ролью класс, evidence статичности и отсутствие скрытой/wired/scripted/constraint
зависимости; неизвестный дочерний узел, неоднозначный результат, ошибка,
unavailable handle, неполный path или превышение лимита => INCOMPLETE, не
`same`. Проверка лишь `getPropNames`, отснятого текущего значения или родительского
`numKeys` не заменяет это условие. Все реально редактируемые Shell fields и три
enable flags подлежат сравнению со **заранее одобренным** набором; три параметра
`innerAmount`, `outerAmount`, `segments` недостаточны (`:763-771`).

Нужны раздельные позитив и независимо подтверждённые отрицательные контроли:
обычный статичный составной controller; ключ на потомке при неизменном текущем
времени и значении; замена leaf; wire/script/constraint; дополнительный/
заменённый modifier; изменённое другое Shell поле, включая увеличение вычисления.
Отказ проверяется до первой потенциальной оценки. Если интерфейс не может
доказать полноту или безопасное чтение — профиль остаётся неподдержанным.

Controller incident не подтверждает controller graph. Исходник `controller-graph-v2.ms:67-76`
создаёт Box/Shell, делает `addModifier`, `update`, потом получает Shell handle и
печатает setup marker. В `controller-graph-v2-residue.json:5-8` marker отсутствует,
есть фактическое `Mesh operation on non-mesh: Box`, `cleanup=false` и более
позднее наблюдение одного узла с Shell. Совместный cleanup guard
`controller-graph-v2.ms:134-143` доказывает только `shellMod == undefined` **или**
`shellHandle == undefined` при том чтении; `update` — гипотеза, а не доказанное
место исключения (`Audit/phase16-p3-controller-incident-2026-11-03f/report.md:42-85`).
Даже успешный запуск этого кандидата не проверил бы все descendants: его
source показывает только отдельные свойства и первый уровень node subAnims,
без рекурсивного сравнения путей (`controller-graph-v2.ms:77-114`).

### C. Permitted dependency graph — BLOCKER, не baseline произвольного состояния

Текущий код фиксирует outgoing refs, список `refs.dependents` и прямое base sharing
между scene nodes (`scripts/wall_surface_runtime.py:601-607,623-640,772-776`).
Он **не классифицирует** каждый incoming/outgoing edge, не запрещает foreign
non-node dependent и не доказывает полноту traversal. Отсняв в baseline уже
подключённый foreign target, нельзя считать этот target автоматически разрешённым.
Проверка `objects.count == 1` и `instanceUsers` не заменяет проверки не-node
references, Shell, его параметров и инфраструктурных объектов.

Предлагаемый ограниченный контракт: до вычисления определить конкретный
stage-specific ориентированный graph ролей для exact node, base, Shell, derived
object/param blocks, controllers, approved root/layer и доказанно допустимых
infrastructure targets; для каждого edge учитывать направление, кратность,
роль, exact identity и сопоставление его обратной стороны там, где API это
поддерживает. Любой ранее не классифицированный edge, target, alias, цикл,
unresolved `undefined` или неполное перечисление => INCOMPLETE. Реальные
`NodeRefMgr`, `ObRefModApp`, `ModApp`, `DerivedObject` из наблюдения incident
(`controller-graph-v2-residue.json:7`) — лишь кандидаты ролей; их имена классов
сами по себе не являются безопасным глобальным whitelist. Не делать универсального
утверждения о Max graph по этой неудачной попытке.

Нужны calibrated independent controls для same-object положительного случая,
замены равным по значениям объектом, plain copy vs instance/shared base,
foreign node, иностранного non-node dependent на node/base/Shell/controller,
hierarchy и пропавшей/нечитаемой ссылки. Сохранить exact identities соседей.
`refs.dependents` материализуется **до** проверки его `items.count <= 128`
(`:601-605,639`), а `pending` накапливается до проверки числа посещённых targets
(`:610-630`): итоговый лимит сам по себе не ограничивает затраты на создание
коллекции и очередь. Если API не предоставляет предварительного дешёвого лимита,
это остаётся незакрытым ресурсным риском, а не O(128) гарантией.

### D. Pre-evaluation ordering — BLOCKER, даже после перестановки graphSnapshot

До `graphSnapshot` source уже читает `node.parent`, `material`, stack/base и
Shell-параметры (`:757-771`); сам `graphSnapshot` делает `custAttributes.count`,
reference enumeration и `getProperty` каждого посещённого target (`:585-599,618-640`).
Не доказано, что каждый такой read безопасен и не вызывает evaluation до
классификации controller/dependency. Более того, сохранённый construction path
вызывает `update node` после операций с сеткой и после attachment Shell
(`:898,912,917,923-925`); является ли конкретный `update` причиной или вызывает
оценку в этом контексте — **не доказано**. `snapshotAsMesh` явно выполняется в
`:704`, а cap `getNumFaces` проверяется только **после** его создания (`:707-710`).
Само наличие конечного результата не ограничивает стоимость его построения.

Требуемая последовательность при будущем самостоятельном design/repair:

1. Без writes и без неклассифицированных оценивающих getters удостоверить
   независимо удержанный lease/context, exact node/base/Shell identities,
   census, stack тип/порядок и приемлемые лимиты; все участвующие операции
   должны быть отдельно признаны безопасными для данного Max build/profile.
2. Не оценивая потенциально опасные значения, доказать полный поддержанный
   controller/subAnim/parameter/dependency graph, включая отсутствие custom,
   scripted, wired, keyed или чужих зависимостей. Выбрать полный фиксированный
   набор разрешённых полей и прочитать только безопасные typed values; проверить
   их и все параметры, влияющие на сложность, против заранее допустимого
   construction recipe или сохранённого detached replay baseline.
3. Для replay закончить **все** pre-evaluation сравнения до любого
   `snapshotAsMesh`, `update`, repair или иного вычисляющего вызова. Для первого
   создания проверять ожидаемые значения recipe, а не принимать только что
   полученные произвольные значения как разрешённые. Учесть все более ранние
   construction calls: разрешить лишь отдельно оценённые и доказанно bounded для
   конкретной стадии. Если невозможно убедительно разграничить безопасные reads
   и возможное выполнение пользовательского кода — сохранять отказ.
4. Лишь затем вызывать bounded evaluated snapshot и проверять фактический лимит,
   сохраняя независимый контроль disposal. Контроль post-evaluation triangle
   count — дополнительный результат, не замена pre-evaluation complexity gate.

Тестовый замысел: зафиксировать специальный evaluation counter/sentinel и
независимо подтвердить ввод каждого unsupported состояния; требовать, чтобы
counter не изменился при отказе. Отдельно контролировать keyed leaf вне current
time, wire/script, unknown ref, добавленный modifier, изменение Shell поля,
недоступный reader и превышение размера. Наличие `graphSnapshot` раньше по
тексту не является доказательством этой схемы.

### E. VData/EData: отсутствие, ошибка и unknown — разные состояния

В `scripts/wall_surface_runtime.py:678-694` **есть** loops по `getNumVDataChannels`
и `getNumEDataChannels`, support и значениям живых элементов. Брошенное
исключение не перехватывается там как `false`: оно выходит наружу. Однако source
не требует, чтобы count был `Integer`, support был строго `BooleanClass`, а
значение поддержанного элемента — разрешённым конечным скаляром; значения
вставляются без `freeze`/проверки. Если getter **вернёт**, а не бросит,
`undefined` для поддержанного канала/элемента, одинаковые такие записи могут
сравниваться как одинаковые через `same` (`:531-540`), вместо явного UNKNOWN.
Это источник возможной ambiguity, а не утверждение, что реальный API именно так
возвращает значения. Поведение неверного типа/`undefined` в `if support` здесь
не установлено; исключение тоже должно остаться INCOMPLETE.

Рекомендуемая typed tri-state схема:

* `KNOWN_SUPPORTED(value)` только при достоверном в диапазоне channel index,
  `BooleanClass true`, успешно считанном разрешённом типе и конечном значении
  каждого релевантного живого элемента; сохранять независимые скалярные копии.
* `KNOWN_NOT_ALLOCATED` для индекса за подтверждённой границей allocation,
  только если документированная и на данном build калиброванная семантика count
  действительно доказывает этот случай. Не делать заведомо out-of-range вызов
  support getter; `count == 0` требует явной проверки нулевой итерации и не
  позволяет придумывать значения для несуществующих элементов.
* `KNOWN_UNSUPPORTED` только при валидном count/domain и строго boolean `false`
  от проверенного support reader для **запрошенного в диапазоне** канала.
  Число каналов, наличие allocation и support — разные факты. Проверить отдельно
  count-zero и границы включительно: нельзя угадывать семантику циклов и индексов.
* `UNKNOWN/INCOMPLETE`: throw, `undefined`/неверный тип любого обязательного
  результата, NaN/infinite, непрочитанный элемент, неподтверждённое отсутствие,
  dead-element uncertainty или недостоверный/вне допустимого диапазона count.
  Два UNKNOWN никогда не образуют equality/NOOP. То же относится к maps и
  компонентам Point/Quat/Color в `freeze` (`:558-582`), где конечность каждого
  компонента также пока не проверяется.

В прочитанном существующем design приведена документационная граница EData 0–10
и VData 0–100, EData 1–2 и VData 1–10 описаны как reserved
(`Audit/phase16-p3-edata-design-2026-11-03f/DESIGN.md:61-74`). Runtime сейчас
применяет одинаковый верхний предел `100` к `vn` и `en` (`:680-682`). Границы
и смысл counts необходимо заново согласовать с версией и контролями; не
выдавать документированное ожидание за измеренное поведение Max и не переходить
в неопределённый индекс ради проверки. Независимо подтвердить поддержку,
добавление/удаление и same-count value edit, а также отсутствие изменений
контрольных данных. Зарезервированные каналы не менять на production wall.

Исторический EData3: `edata3.ms:44-61` объединяет операции и пишет detail только
после них; `edata3-result.json:5-8` показывает `ok=true` транспорта при реальном
`Vertex data support not enabled … channel: 3`. Конкретный setter/getter не
локализован, support/readback не доказаны, это не отсутствие API и не ошибка,
зафиксированная в production runtime. Отдельная VData11 попытка подтверждает
только наблюдённые 0.375/repeat/0.625 на owned quad (`vdata11-result.json:5-8`).

Новые `probe.ms` и `alternate-control.ms` — неисполненные designs, не измерение.
`probe.ms:180-247` локализует caught errors по стадиям, но добавляет VData11 и
не повторяет исходный опыт буквально; `C04/C05` читают данные, записанные
target setter. `alternate-control.ms:158-212` предлагает другой selected-edge
writer/reader, но эквивалентность channel index и независимость storage не
установлены. Они накапливают log локально и возвращают его в конце: при timeout
или process interruption последняя сохранённая стадия не гарантирована. Их
cleanup имеет намеренно строгие guards, включая неизменность dirty-флага и
непроверенную политику зависимостей (`probe.ms:264-314`;
`alternate-control.ms:215-251`); это может корректно оставить residue и не
доказывает пригодность запуска. Ничто в данном review не разрешает их запуск.

### F. Layer, witness и сравнение значений — сопряжённые blockers

`freeze` generic reference использует `exactRef`, включая для `#layer`
(`scripts/wall_surface_runtime.py:541-557,580-583,777-791`); предыдущий Main03
фактически не смог преобразовать `LayerProperties` к anim handle, как описано в
`CHECKPOINT.md:155-165`. Позднее наблюдение backing target и bounded owned-layer
контроли — не интегрированный runtime reader или полный replay baseline
(`CHECKPOINT.md:77-94`). Нужны отдельные точная layer/backing identity, состояние
и вложенный GI, membership, отрицательные controls и unknown refusal. Класс или
имя слоя не достаточно.

Вызов стены читает `registryWitness` из самого глобала и лишь сравнивает его с
тем же локальным чтением (`scripts/wall_surface_runtime.py:826-835,853-860`).
Отдельный main-owned witness исходного точного lease и detached ожидаемые nonce,
контекст и state transitions обязательны при каждом допущенном вызове; nonce
правильной длины не доказывает continuity. Timeout, потеря/замена witness,
открытие/merge/restart или сомнительная операция => inspect-only, без re-arm.
Предлагаемая гарантия — trusted sequential controlled session, не защита от
произвольного вредоносного кода (`Audit/_phase16-p3-runtime-design-2026-11-02e.md:79-83,103-120`).

`COMMITTED` после двух ограниченных snapshots помечен в source как
construction-only (`scripts/wall_surface_runtime.py:930-940`), но прежний
design резервировал COMMITTED до полного baseline
(`Audit/_phase16-p3-runtime-design-2026-11-02e.md:200-217`).
Согласовать это явным решением coordinator либо использовать отдельный
provisional state; ни тот, ни `P3_CREATED_UNVERIFIED` не означает replay или
geometry acceptance. Никакой отказ/ошибка диагностики не должен объявляться
доказанной чистой историей lease
(`Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md:96-156`).

## 3. Точные условия будущего cleanup: design, не реализованный алгоритм

Контракт требует попытаться выполнить безопасный случай; он **не** разрешает
удаление на основании только имени, tag, найденного handle или пустого census.
Ниже — необходимый минимум для будущего решения; до калибровки и обзора это
не означает, что совокупность условий уже достаточна для любого Max plugin.

| Состояние | Допустимое решение при проверенном contract/profile |
|---|---|
| До любой попытки конструктора | Не удалять ничего. Отдельно проверить admitted context/полный survivor set; неисправный reader — INCOMPLETE. |
| Конструктор вызван, но exact return не удержан/не независимо засвидетельствован | Исход неизвестен, включая частичный эффект до throw/timeout. Не искать и не adopt по имени, handle, одиночному объекту или census; сохранить диагностику, inspect-only. |
| Возврат node удержан и доказан | Только непрерывная исходная живая exact ссылка текущей попытки, отдельно удержанный оригинальный witness/ledger и совпадающий handle-roundtrip, корректные stage/context/units, exact survivor census, отсутствие чужих parent/children, shared base и **классифицированное отсутствие чужих node и non-node dependents** на всех освобождаемых ролях могут открыть путь к удалению. Не чинить зависимости/selection/units, чтобы пройти guard. |
| `convertTo` начат/вернулся | Записать точный возвращённый candidate до потенциально бросающего read; не повышать его до authority без доказанной непрерывности с исходной ссылкой, двустороннего witness/handle cross-check и целостного окружения. Неизвестный или другой candidate и неизвестная invalidation => retain/INCOMPLETE. |
| Shell ещё не конструировался | Не требовать заведомо несуществующий Shell witness для отдельно доказанного безопасного node cleanup. Это не снимает остальные проверки. |
| Shell constructor/attach начат | Сохранить оригинальный exact Shell ref до handle/attachment/update, проверять стадию и фактическую привязку. Если исход конструктора или attachment неизвестен, либо Shell ref/значимая зависимость потеряны, retain и INCOMPLETE. Отдельно описать безопасную жизнь сконструированного, но unattached non-node Shell: не вызывать для него node `delete` и не заявлять disposal без доказательства. Не detach чужие/неизвестные объекты для разрешения cleanup. |
| Удаление exact node разрешено и выполнено | Проверить, что именно исходная ссылка больше не валидна/отсутствует, и сравнить **полный exact survivor set** с предоперационным; отдельно записать failure исходной операции, все cleanup/readback ошибки и статус lease. Одного нулевого числа недостаточно. |
| Delete/readback/disposal бросил, прерван или таймаут | Результат неизвестен; не повторять delete/disposal по новой найденной ссылке. Не считать отсутствием residue, сохранить все доступные свидетельства, обратиться к оператору. Отдельно учитывать non-scene mesh snapshot и его точное disposal (`scripts/wall_surface_runtime.py:696-753,1023`). |

Условия для необходимого контроля: native API-граф должен быть калиброван для
каждой стадии и содержать допустимые внутренние связи — ни `refs.dependents`,
ни класс target, ни `dirty=false` в отдельности не доказывают отсутствие callback,
чужого права или чистоты undo history. Источник истины — independently retained
точные ссылки и approved profile в пределах доверенной последовательной сессии.
Dirty flag — наблюдение, а не доказательство отсутствия изменений; требование
его равенства исходному может консервативно блокировать cleanup после обычного
создания. Нельзя очистить dirty flag, сохранить/reset сцену или удалять другие
объекты ради успешного postcheck. Contract-safe dirty transition нужно отдельно
определить и проверить, без обещаний восстановления истории.

Текущий catch собирает census и diagnostic refs, затем best-effort помечает lease
POISONED (`scripts/wall_surface_runtime.py:943-1046`); до гарантированного
сохранения ссылок или при interrupted catch гарантировать этот результат нельзя.
Нужны controls на границах constructor return → публикация exact ref → handle →
conversion return → Shell return → attachment → любой evaluating operation →
baseline → lease transition, а также на ошибках каждой проверки, самой диагностики,
delete и post-read. Для каждого unsafe случая требовать **no delete**, сохранения
исходных exact соседей и INCOMPLETE. Для действительно допустимого случая
дополнительно нужен positive exact cleanup/survivor control; иначе выполнение
contract `:33` не показано. Только offline модели не доказывают Max semantics.

## 4. Ограниченный план верификации; всё пока NOT RUN

1. Сохранить оба исполняемых отказа; стабилизировать/хэшировать полный исходник и
   независимый witness/cleanup design. Явно разрешить COMMITTED/provisional
   semantics до любой отмены барьера. Ранее выпущенные файлы учитывать отдельно.
2. На **offline** уровне подготовить независимые source/state-machine controls с
   positive и negative моделями, неизвестными типами/support/значениями,
   недостающими и заменёнными refs, циклом/foreign non-node, несколькими стадиями
   и error injection; зафиксировать порядок gate < evaluation и отсутствие cleanup
   при unknown. Эти controls не считать синтаксической/поведенческой проверкой Max.
3. Только после разрешения текущего residue оператором и нового read-only входа
   main может отдельно рассмотреть короткие, sequential, exact-owned калибровки;
   зафиксировать независимо мутацию каждого поля и успешность/ошибки исходного и
   cleanup paths. Не считать старый VData11 доказательством EData или текущего
   comparator. Любой неуспех/таймаут/непрочитанная категория сохраняет блокировку.
4. Лишь после полного reviewed pre-evaluation graph, native metadata и безопасного
   cleanup/witness профиля, на стабильных bytes повторить соответствующие offline
   suites и отдельно оценить genuine emitted F01, независимые geometry/direction
   результаты, три реальные same-lease NOOP и отдельные target-specific отрицательные
   controls по контракту. Эти пункты за рамками данного review и не выполнены.

## 5. SHA-256 исходных bytes, прочитанных для аудита

Хэши — независимые локальные чтения bytes, не блокировка файлов и не гарантия
отсутствия параллельного изменения. Исторические отчёты связываются со своими
версиями, а не пересчитываются как доказательства текущего runtime.

```text
3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf  scripts/wall_surface_runtime.py
4e53b474fc65db7ce1fc2fc78bc3e5358b59e85690d66bb600475474d878bf0f  Audit/_phase16-p3-contract-2026-11-02e.md
f5dacae9fc573819626001d861692da5f0ff2706003044d1a915c7ba9e71ac1a  Audit/_phase16-p3-runtime-design-2026-11-02e.md
d847371370088471613982ae8f08fdef56341ba8903dfbac97d06bf1f0aacdd8  Audit/phase16-p3-metadata-design-2026-11-03/README.md
ac4cdbaa4097ece2fabdd7038aa6a920409839ad265f471767342524ab880e8f  Audit/phase16-p3-metadata-design-2026-11-03/REPORT.md
714b09f66c57f2513ee7ed3c65b8273066571358ef7fac241eb8763cc68026b9  Audit/phase16-p3-metadata-design-2026-11-03/vdata-channel-control.ms
0b64fd7015c4d35070ad518876703294ee45207ce2a532c495fe65bbd15246b3  Audit/phase16-p3-metadata-design-2026-11-03/layer-ref-target-readonly.ms
1cd3438da2d649f337b0e30fe286f130a83fc3a7fefa2edf6d4b6534692d117f  Audit/phase16-p3-edata-design-2026-11-03f/DESIGN.md
aaf7dbc498768df046f638501a6505dc6d0d94ccd2219d843a97b7d6e3c2b575  Audit/phase16-p3-edata-design-2026-11-03f/probe.ms
45365a8ae162c752c41912608f4d73bce28367210d3fe6a3eb7645287b6aa990  Audit/phase16-p3-edata-design-2026-11-03f/alternate-control.ms
3c848df6dfca5f201ce0c358aab95d55ad5596a9cbd0f744725afc0441b055a3  Audit/phase16-p3-controller-incident-2026-11-03f/report.md
4d5b064c7d98bc531644ed9990629d4a3621989fcae0546c2150b1b6e8f50aa7  Audit/phase16-p3-main-probes-2026-11-03f/controller-graph-v2.ms
b95b20a7c6a0d793bbcae0c2d93c702baa73eca13c1c1f9037ed79d4e03b2867  Audit/phase16-p3-main-probes-2026-11-03f/controller-graph-v2-residue.json
ae7ddb26e911259d873737f80c7a24988e3fe45b9d6a5931d6d745b55e25ff50  Audit/phase16-p3-main-probes-2026-11-03f/edata3.ms
5e86604ad6af4d55e239ec1054e775288ca077d28980f57d1a3b2815c92ad1a1  Audit/phase16-p3-main-probes-2026-11-03f/edata3-result.json
1551988805e2011ae860e8f7f5c3e31a70edf64885c9cadcb66ce71f5ed38416  Audit/phase16-p3-main-probes-2026-11-03f/vdata11.ms
50a0faebf7311cd0511f92cec1af00a809dc6646a798ca2b50b347af459c6ee8  Audit/phase16-p3-main-probes-2026-11-03f/vdata11-result.json
144c7b04b31a169cf4f896848a8a5f627d65c2672ab2836c78b091e2bf3e2966  Audit/phase16-p3-hardening-independent-2026-11-03f/REPORT.md
88baf03fd899d006b14652b9dfcdeb2481c470270448e1d91c9f0bbdcc600272  Audit/phase16-p3-runtime-review-2026-11-03/review.md
ad5fff9108227b1b32fcd87e479dabbcd03edcbb880151a1611d593bc9ac8d35  Audit/phase16-p3-runtime-hardening-2026-11-03f/PRECREATE-GATE-REPORT.md
```

`graphify-out/graph.json` осмотрен только чтением: в нём не найдено узлов для
`wall_surface_runtime`, `phase16-p3` или specified normals; graph не использован
как доказательство отсутствия исходников или актуального состояния. Результаты
соответствуют указанному snapshot и должны быть перепроверены при drift.
