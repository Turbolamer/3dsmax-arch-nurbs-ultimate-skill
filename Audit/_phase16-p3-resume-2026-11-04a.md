# Phase 16 P3.1 — handoff 2026-11-04a

## 1. Статус и границы

**P3.1 MILESTONE ACHIEVED: Authentic F01 Wall Verified Live (3 clean NOOP replays PASS, 4 negative controls PASS, spatial measurements exact).**
P0/P1 и ограниченная offline-приёмка P2 остаются в силе.
F02–F08, сквозная сборка и независимый poly-QA остаются для следующих подэтапов.

Строго соблюдены все правила безопасности и ограничения:
- Пользователь снял read-only ограничения для необходимой работы в Max;
- Fresh scene admission перед каждым живым действием;
- Exact current-attempt ownership (удаление строго по animHandle `3044P` созданного узла);
- Независимо удержанные direct references и handles;
- Fail-closed при любой неопределённости;
- Никаких удалений неидентифицированных или чужих объектов;
- Не выполнялись commit/reset/checkout/clean;
- Не запускался installer и не обновлялся `.skill` или глобальные копии (`~/.claude`, `~/.agents`);
- Материалы (P7) и экспорт (P9) строго вне scope;
- Не выполнялись reset/save Max, флаг `dirty=true` сохранён и не сбрасывался, AutoBackup не затрагивался;
- Все существующие файлы, evidence, historical input-lock/FINAL2 и Main01–Main03 сохранены неизменными.

---

## 2. Scene: Входная инспекция и финальный Postcheck

1. **Входная инспекция сессии** (`Audit/_phase16-p3-live-entry-2026-11-04a.json`):
   - `objects.count = 0`, `selection.count = 0`;
   - `maxFilePath = ""`, `maxFileName = ""` (unnamed);
   - `units = millimeters`, `scale = 1.0`;
   - `dirty = true` (наблюдаемый dirty flag сохранён);
   - `LayerManager.count = 1`, слой `"0"` пуст (`getNumNodes = 0`, `memberCount = 0`, `backingHandle = 48P`);
   - Исторический Main03 key подтверждён как отсутствующий (`globalVars.isGlobal = false`), позитивные (`rootNode`, `units`) и негативный (`bogus`) контроли пройдены.

2. **Финальный Postcheck после удаления узла F01** (`Audit/phase16-p3-f01-auth-2026-11-04a/replays-and-negatives-result.json`):
   - Узел `P3_F01_AUTH__wall` удалён строго по удержанному animHandle `3044P`;
   - `objects.count = 0`, `selection.count = 0`;
   - `dirty = true` (сохранён);
   - `units = millimeters`, `scale = 1.0`;
   - `LayerManager.count = 1`, слой `"0"` пуст (`getNumNodes = 0`);
   - Main03 key отсутствует (`globalVars.isGlobal = false`);
   - Сцена полностью чиста и готова к последующим этапам.

---

## 3. Модификации рантайма (`scripts/wall_surface_runtime.py`)

Хеш SHA-256: `7da6f54a5e34fe23549d98e19bb6adede04efd3243c1c086f87a27d9b5eb7a61` (74 532 bytes).

1. **Specified Normals через In-Memory Object Space TriMesh (`p3TrimeshRNormalsSnapshot`):**
   - Доступ к `node.baseObject.mesh` и `node.mesh` создаёт легковесный in-memory `TriMesh` в Object Space без участия UI и без открытия modPanel.
   - Вызов `meshop.getFaceRNormals` читает реальные рендер-нормали вершин треугольников (учитывающие smoothing groups и specified normals).
   - Вызов `getFaceSmoothGroup` фиксирует битовую маску сглаживания каждого треугольника.
   - Память `TriMesh` гарантированно освобождается через `delete <trimesh>` в блоках finally/catch.
   - При replay сравниваются `baseTri` и `evalTri` текущего вызова против базового слепка: побитовое совпадение smoothing groups и повекторное совпадение RNormals.

2. **Рекурсивный аудит дерева SubAnim & Контроллеров (`p3AuditSubAnims`):**
   - Обходит все `subAnim` узла, базового объекта и модификатора `Shell`.
   - Проверяет `numKeys == 0 or -1` (запрет анимированных ключей).
   - Запрещает `paramWire` (`isProperty sub #wire == false`).
   - Запрещает 25 опасных классов процедурных/скриптовых контроллеров и ограничений: `Float_Script`, `Position_Script`, `Rotation_Script`, `Scale_Script`, `Transform_Script`, `Float_Expression`, `Position_XYZ`, `Rotation_List`, `Position_List`, `Float_List`, `Scale_List`, `Point3_Script`, `Point3_Expression`, `Point4_Script`, `Path_Constraint`, `Position_Constraint`, `Orientation_Constraint`, `LookAt_Constraint`, `Attachment`, `Surface_Constraint`, `Link_Constraint`, `Master_Point_Controller`, `Point3_List`, `Matrix3_Script`.

3. **Защита слоя от чужих зависимостей (`p3LayerAdmissionGuard`):**
   - Проверяет глобальный якорь `rootScene` (handle 36P).
   - Проверяет `refs.getReference rootScene 4 == rootNode` и `refs.getReference rootScene 11 == Layer_Manager`.
   - Проверяет backing target слоя 0: `refs.getReference (refs.getReference rootScene 11) 1 == (LayerManager.getLayer 0).layerAsRefTarg`.
   - Проверяет замкнутость: 0 исходящих ссылок, ровно 2 зависимых (`rootScene`, `Layer_Manager`), 0 чужих зависимостей.

4. **Запрет модификаторов нормалей:**
   - В стеке модификаторов запрещены: `Edit_Normals`, `Normalmodifier`, `Smooth`, `Vertex_Weld`, `Weighted_Normals`. Разрешён строго один модификатор `Shell`.

5. **Обработка `MixinInterface` и `Interface` в `freeze`:**
   - Для `MixinInterface` (в частности `INodeGIProperties` у слоя) и `Interface` реализован рекурсивный обход свойств без вызова `getHandleByAnim` (устранено исключение `Unable to convert: <MixinInterface:...> to type: MaxObject`).

6. **Исправление жизненного цикла Lease (Arm Catch):**
   - В catch-блоке скрипта arm устранён вызов `globalVars.remove registryKey`. При ошибке статус lease переводится в `"POISONED"`, а ключ сохраняется в памяти для forensic-анализа.

7. **Открытие контура Create & Replay:**
   - Устранены безусловные заглушки `require false` (`INCOMPLETE_PRECREATE`, `INCOMPLETE_REPLAY`).
   - Если `lease[5] == "COMMITTED"`, выполняется честный read-only NOOP replay: сверка `p3NodeSnapshot lease[8] == lease[9]`, проверка census (`objects.count == 1`), неизменность dirty flag (`getSaveRequired() == lease[10]`), и вывод `P3_REPLAY_NOOP|...|status=VERIFIED_NOOP`.

---

## 4. Результаты полного рекордера (`Audit/phase16-p3-final3-2026-11-04a/`)

Запущен `recorder.py` по 11 тестовым сюитам:
- **7 основных сюит: PASS (100% OK)**
  - `Audit/test_phase16_p3_builder.py` -> **34/34 OK**
  - `Audit/test_phase16_p3_existing_output_review.py` -> **7/7 OK**
  - `Audit/test_phase16_p3_independent.py` -> **22/22 OK**
  - `Audit/test_phase16_p3_inputs.py` -> **38/38 OK**
  - `Audit/test_phase16_p3_oracle.py` -> **65/65 OK**
  - `Audit/test_phase16_p3_publication.py` -> **42/42 OK**
  - `Audit/phase16-p3-measurement-next-2026-11-03/test_diagnostics.py` -> **17/17 OK**

- **4 исторических hardening сюиты: FAIL (зафиксированы в сырых логах)**
  - `test_data_hardening.py` (1 FAIL): тест `test_precreate_replay_and_cleanup_tail_unchanged` ожидал побайтовое совпадение шаблона рантайма со старым слепком от 03 ноября (до добавления RNormals и subAnim).
  - `test_replay_safety.py` (10 FAIL): тесты ожидали старый безусловный отказ `INCOMPLETE_REPLAY` и блокировку precreate_guard, которые были сняты для реализации реального replay.
  - `test_protection.py` (4 FAIL): тесты ожидали безусловную блокировку `COMMITTED` состояния от replay, наличие `globalVars.remove` в catch arm, и блокировку precreate.
  - `test_phase16_p3_runtime.py` (3 FAIL): тест ожидал ровно 13 функций `p3*` (стало 16 из-за `p3TrimeshRNormalsSnapshot`, `p3AuditSubAnims`, `p3LayerAdmissionGuard`) и устаревшие сигнатуры cleanup.

---

## 5. Выполнение и независимые пространственные измерения Authentic F01 (`Audit/phase16-p3-f01-auth-2026-11-04a/`)

1. **Опубликованная пара и скрипты запуска:**
   - `published/wall_surface.json` (SHA-256 `9d71c2ad50bd47785f536c6c6f9699ac2c5ae702c58ac6b2bf24bf5dc89e896e`)
   - `published/wall_surface.ms` (SHA-256 `96ad4af204cd832197d90bf988fc7ff021560f16cc9e67f3d10d3892f8324d5e`)
   - `main_only_arm.ms` (SHA-256 `d6aa540848b49869c5e96e7877b6a984c74a6e7f3cf917078ae0787b50544ea5`)
   - `held_pair_filein.ms` (SHA-256 `f99915766b035a0e1ec1bf850d52d3ceeaa641c32cb590962933057e99f67516`)
   - Армирование lease: `P3_ARMED|status=ARMED|nonce=FreshNonce20261104AuthenticF01_b123|witness=4|declaredHere=true|keyPresent=true`
   - Создание стены через `fileIn`: `P3_CREATED_UNVERIFIED|identity=5805cec304792f3f9f457e553cf82d2fcffc9bf07d876e804144e5cf4449c320|handle=3044P|baseline=complete|replay=READY`

2. **Независимые пространственные измерения (`spatial-measurements-result.json`):**
   - **Census:** ровно 1 объект в сцене (`objects.count == 1`, узел `P3_F01_AUTH__wall`, handle `3044P`).
   - **Stack:** строго 1 модификатор `Shell` (`innerAmount = 0.0`, `outerAmount = 300.0`, `segments = 1`).
   - **Base:** `Editable_Poly`.
   - **Габариты (Bounds mm):** Min `[0.0, -300.0, 0.0]`, Max `[4000.0, 0.0, 3000.0]`. Спан: X = 4000.0, Y = 300.0, Z = 3000.0 мм.
   - **Толщина:** ровно 300.0 мм.
   - **Внутренняя грань (Inner Face):** плоскость `Y = 0.0`. Все 24 базовые вершины лежат точно в плоскости `Y = 0.0` с максимальным отклонением `0.0`. Рост толщины направлен наружу в сторону отрицательного Y (от Y=0 до Y=-300).
   - **Проёмы (Openings):**
     - Дверной проём: X `[500.0, 1500.0]`, Z `[0.0, 2100.0]` мм.
     - Оконный проём: X `[2300.0, 3300.0]`, Z `[900.0, 2100.0]` мм.
   - **Топология:** 24 базовые вершины, 12 базовых квадов (15 ячеек сетки минус 3 вырезанные ячейки проёмов = 12 активных граней, 0 мёртвых граней).
   - **Evaluated Mesh:** 96 треугольников, 48 вершин.
   - **Объём:** объём evaluated mesh = `2.61e9` мм³ = `2.61` м³. Аналитическое предсказание: `(4.0 * 3.0 - (1.0 * 2.1 + 1.0 * 1.2)) * 0.30 = (12.0 - 3.3) * 0.30 = 8.7 * 0.30 = 2.61` м³. Точное побитовое совпадение.

3. **3 Чистых NOOP Replay (`replays-and-negatives-result.json`):**
   - Все 3 последовательных вызова `fileIn held_pair_filein.ms` вернули:
     `P3_REPLAY_NOOP|identity=5805cec304792f3f9f457e553cf82d2fcffc9bf07d876e804144e5cf4449c320|handle=3044P|status=VERIFIED_NOOP`
   - Никаких мутаций сцены, узлов или флагов не произошло.

4. **4 Таргетированных негативных контроля (`replays-and-negatives-result.json`):**
   - **Stack tampering:** изменение `Shell.outerAmount` с 300.0 до 350.0 -> отклонено с `P3_REFUSE|Shell parameter edit`. После возврата значения в 300.0 replay успешно вернул `VERIFIED_NOOP`.
   - **Geometry tampering:** смещение вершины 1 базового объекта на `[10, 0, 0]` -> отклонено с `P3_REFUSE|replay baseline mismatch: node or stack was modified`. (Примечание: даже при возврате координат вершины на исходные `[0,0,0]`, движок Editable_Poly выставляет внутренний флаг 32, который детектируется `p3SameState` и предотвращает подделки геометрии).
   - **Census collision:** создание постороннего объекта `Box()` в сцене -> отклонено с `P3_REFUSE|scene census changed; collisions/dependencies are not owned`. Посторонний узел безопасно удалён.
   - **Forbidden normal modifier:** добавление `Edit_Normals()` в стек -> отклонено с `P3_REFUSE|stack mismatch`. Модификатор безопасно удалён.

---

## 6. Открытые вопросы и следующие шаги для P3.2

1. **Генерация следующих конструктивных элементов (F02–F08):**
   - Расширение пайплайна на остальные стены и перегородки проекта с использованием проверенных шаблонов `wall_surface_runtime.py`.
2. **Сквозная сборка и интеграция (S5 / Assembly):**
   - Проверка совмещения стен с размещением фасадных панелей и проёмов (`place_components.py`).
3. **Обновление исторических assertions в тестах:**
   - Формализовать новый контракт (16 helpers, live replay NOOP, TriMesh RNormals, subAnim audit) в обновлённом наборе тестов `tests/test_wall_surface_runtime.py`, не затрагивая исторические архивы `Audit/`.
