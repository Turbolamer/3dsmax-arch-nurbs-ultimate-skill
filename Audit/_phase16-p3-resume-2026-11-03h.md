# Phase 16 P3.1 — handoff 2026-11-03h

## 1. Статус и границы

**P3.1 NOT ACCEPTED (IN PROGRESS).** P0/P1 и ограниченная offline-приёмка P2 остаются в силе.
Пользователь разрешил необходимую работу в 3ds Max (read-only ограничения сняты).
Обычные правила безопасности действуют строго:
- Fresh scene admission перед каждым действием;
- Exact current-attempt ownership;
- Независимо удержанные direct references и handles;
- Fail-closed при любой неопределённости;
- Никаких удалений неидентифицированных или чужих объектов;
- Не делать commit/reset/checkout/clean;
- Не запускать installer и не обновлять `.skill` или глобальные копии;
- Материалы и экспорт вне scope;
- Не выполнять reset/save Max, не очищать dirty flag и не обращаться к AutoBackup;
- Сохранять все существующие файлы, evidence и historical input-lock/FINAL2/Main01–03.

## 2. Scene: свежая входная инспекция и текущее состояние

1. **Входная инспекция сессии** (`Audit/_phase16-p3-live-entry-2026-11-03h.json`):
   - `objects.count = 0`, `selection.count = 0`
   - `maxFilePath = ""`, `maxFileName = ""` (unnamed)
   - `units = millimeters`, `scale = 1.0`
   - `dirty = true` (наблюдаемый флаг сохранён, не сбрасывался)
   - `LayerManager.count = 1`, слой `"0"` пуст (`getNumNodes = 0`, `memberCount = 0`, `backingHandle = 48P`)
   - Исторический Main03 key `#__P3W_2a27162292203d7e9f982ae655c3a5b20af18a9044b039a105222a09bdf7eff7` подтверждён как отсутствующий (`globalVars.isGlobal = false`, runtime error на `get`), с позитивными контролями (`rootNode = true`, `units = true`) и негативным контролем (`bogus = false`).
2. **Postcheck после живых калибровок:**
   - 0 объектов, 0 выделения, unnamed, mm/1.0, dirty=true, 1 слой, слой 0 пуст, backing handle 48P, ключ отсутствует. Сцена не изменена.

## 3. Независимый Source Review рантайма

Независимый аудит проведён и зафиксирован в `Audit/phase16-p3-runtime-review-2026-11-03h/REPORT.md`:
- SHA-256 `scripts/wall_surface_runtime.py`: `ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2` (60 948 bytes, byte-identical).
- Pre-edit baseline SHA-256: `3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf`.
- Diff: 79 строк точечного hardening в `freeze(dataOnly:true)` (Integer, Integer64, Float, Double) и строгая валидация типов для `nv`, `ne`, `deadV`, `deadE`, `vn`, `en`, `BooleanClass` support и `BooleanClass` dead flags.
- Тесты:
  - `python -B Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py` -> **15/15 OK**
  - `python -B Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py` -> **21/21 OK**
  - `python -B Audit/test_phase16_p3_runtime.py` -> **41 OK, 1 FAIL** (ожидаемый FAIL в `test_cleanup_exact_current_attempt_refs_only` из-за отказа от небезопасного handle-reacquisition/delete в пользу residual-регистрации).
- Предохранители: `INCOMPLETE_PRECREATE` (строка 893) и `INCOMPLETE_REPLAY` (строка 879) подтверждены как активные и безусловные (`require false`). Конструкторы и replay недостижимы.

## 4. Разрешение проблемы идентичности слоя (Live Discovery)

Устранён главный блокер архитектуры слоёв (`Audit/phase16-p3-main-probes-2026-11-03h/layer-manager-anchor-result.json`):
1. Установлен независимый корневой якорь для менеджера слоёв:
   - `rootScene` (Scene, handle 36P) — стандартный глобальный ReferenceMaker.
   - `refs.getReference rootScene 11` даёт **точный `Layer_Manager` ReferenceTarget** (handle 46P).
   - `refs.getReference rootScene 4` даёт **точный `rootNode`** (`MAXRootNode`, handle 39P).
2. Установлена связь менеджера со слоем:
   - `refs.getReference (refs.getReference rootScene 11) 1` даёт **точный backing target слоя 0** (`Base_LayerBase_Layer`, handle 48P), совпадающий по ссылочному равенству с `(LayerManager.getLayer 0).layerAsRefTarg`.
3. Установлена замкнутость графа зависимостей:
   - `refs.getNumRefs backing = 0` (нет исходящих ссылок).
   - `refs.dependents backing` содержит ровно 2 объекта: `rootScene` и `Layer_Manager`. Чужих зависимостей: **0**.

## 5. Bounded Layer Reader Live Pass

Выполнен и зафиксирован верифицированный ридер слоёв:
- Скрипт: `Audit/phase16-p3-main-probes-2026-11-03h/layer-reader-verified.ms` (SHA `e51669c2aac257391ee6222d98e8e49325bb5663617f4f4ab6e05428d75b7ec7`).
- Результат: `Audit/phase16-p3-main-probes-2026-11-03h/layer-reader-verified-result.json`.
- Прочитано и верифицировано:
  - 33 interface свойства (повторяемость доказана).
  - 34 backing свойства, включая `#degrade` (повторяемость доказана).
  - 18 nested GI свойств (повторяемость доказана).
- Негативные контроли успешно сработали:
  - Мутация отсоединённого массива GI обнаружена (`detachedGIMutationDetected = true`).
  - Мутация отсоединённого массива degrade обнаружена (`detachedDegradeMutationDetected = true`).
  - Неверный backing witness отклонён (`wrongBackingRefused = true`).
  - Фиктивное свойство отклонено (`bogusPropRefused = true`).
  - Undefined скаляр отклонён (`undefinedScalarRefused = true`).
- Итог: `outcome = BOUNDED_LAYER_READER_PASS_INCOMPLETE_REPLAY`.

## 6. Оставшиеся открытые вопросы до публикации новой Authentic Pair

1. **Specified Normals Base Metadata:**
   - `polyop` в 3ds Max не экспортирует API для specified normals. В Editable_Poly базовой геометрии нормали вычисляются динамически по smoothing groups, если нет модификатора `Edit_Normals`.
   - Требуется строгий предикат отсутствия модификатора `Edit_Normals` и отсутствия кастомных нормалей до evaluated шага.
2. **SubAnim & Controller Descendants:**
   - Рекурсивный аудит дерева `subAnim` на объекте и модификаторах (Shell): проверка `numKeys == 0`, запрет wire (`paramWire`), script-контроллеров и constraints.
3. **Lease Lifecycle & Arm Catch:**
   - Исключить вызов `globalVars.remove registryKey` из catch-блока скрипта arm (сохранять `POISONED` статус при сбое для forensic проверки).
   - Синхронизировать состояния lease между обёрткой и рантаймом.
4. **Authentic emitted wall pair F01:**
   - Только после интеграции проверенных решений остановить авторов, заморозить closure, запустить полный recorder в новом каталоге, создать genuine pair с новым registry key и external lease witness, и выполнить честные измерения (direction, openings, topology, volume, bounds, census, stack, 3 clean NOOPs).
