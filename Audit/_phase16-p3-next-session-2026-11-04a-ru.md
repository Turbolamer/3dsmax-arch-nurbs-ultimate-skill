# Промпт для новой сессии — Phase 16 P3.1 / P3.2 / P4

```text
Продолжаем Phase 16 в D:\Rhino\3dsmax-arch-nurbs-ultimate-skill (переход от верификации F01 к P3.2 / P4 QA Profile).

Сначала прочитай:
1. Начало CHECKPOINT.md и AGENTS.md; PLAN.md §4.0d.
2. Audit/_phase16-p3-resume-2026-11-04a.md — главный актуальный handoff (завершение живой верификации F01).
3. Результаты живой верификации Authentic F01 в Audit/phase16-p3-f01-auth-2026-11-04a/:
   - spatial-measurements-result.json (габариты 4000x300x3000 мм, inner face Y=0.0, volume 2.61 м³, 96 triangles, door/window cutouts);
   - replays-and-negatives-result.json (3 чистых NOOP реплея PASS, 4 негативных контроля PASS, postcheck 0 объектов, dirty=true);
   - published/wall_surface.json и published/wall_surface.ms;
   - main_only_arm.ms и held_pair_filein.ms.
4. Отчёт рекордера Audit/phase16-p3-final3-2026-11-04a/ (run.json, snapshot-verdict.json): 7 основных сюит PASS, 4 исторические сюиты FAIL из-за старых ожиданий Nov 03 (INCOMPLETE_REPLAY, блокировка precreate).
5. Audit/_phase16-p3-contract-2026-11-02e.md — контракт P3.

Сохраняй ВСЕ имеющиеся изменения, новые файлы, опубликованные пары и evidence.
Не делай commit/reset/checkout/clean. Не запускай installer и не обновляй .skill
или глобальные копии (~/.claude, ~/.agents). Материалы и экспорт вне scope.
Не выполняй reset/save Max, очистку dirty flag или AutoBackup.
Historical input-lock/FINAL2 и Main01–03 остаются неизменными.

Максимально экономь контекст: делегируй независимые offline-задачи субагентам,
с явным непересекающимся владением и короткими отчётами. Только main выполняет
живые Max вызовы — коротко и последовательно. Моё разрешение на необходимую
работу в Max действует; я снял ограничения read-only. Не возвращай унаследованный
blanket ban и не спрашивай повторно общее разрешение. Сохраняй обычную безопасность:
fresh admission, exact current-attempt ownership, независимо удержанные refs,
никаких удалений чужого/неидентифицированного, fail closed на неизвестное.

Первое действие main в Max — новая read-only инспекция: полный bounded census и
узлы, selection, path/name, units/scale, dirty flag, layers, реестровые ключи с
real/bogus controls. Последний postcheck в сессии 04a: 0 объектов, 0 selection,
unnamed, mm/1.0, dirty=true, 1 пустой слой 0, Main03/P3W ключи absent. Не сбрасывай dirty.

---

### Текущий статус:

1. **Authentic F01 Wall полностью верифицирована live в Max 2026.3.2:**
   - Геометрия: точные габариты [0,-300,0]..[4000,0,3000] мм, толщина 300 мм, внутренняя грань строго на Y=0.0 (0.0 deviation), рост Shell в -Y, проёмы двери и окна точны.
   - Топология: 24 вершины базы, 12 базовых квадов, 96 evaluated треугольников.
   - Объём: 2.61 м³ (аналитически точно).
   - Стек: строго 1 модификатор Shell (0.0 inner, 300.0 outer, 1 segment). База: Editable_Poly. Модификаторы нормалей запрещены.
   - Нормали: извлечение через in-memory Object Space TriMesh (meshop.getFaceRNormals и getFaceSmoothGroup) без UI/modPanel с гарантированным delete.
   - SubAnim: рекурсивный аудит контроллеров (numKeys == 0, запрет wire, запрет 25 динамических классов).
   - Слой: доказан корень доверия (rootScene -> rootNode, Layer_Manager, layer 0 backing target) и замкнутость графа зависимостей (0 исходящих, ровно 2 входящих).
   - Replay: 3 чистых NOOP реплея подряд вернули VERIFIED_NOOP без мутаций сцены.
   - Негативные контроли: 4 targeted negatives (stack tampering, geometry vertex move с детекцией внутреннего флага 32, census collision, forbidden Edit_Normals) успешно отклонены с P3_REFUSE.
   - Сцена очищена по точному animHandle 3044P, postcheck 0 объектов, dirty=true сохранён.

---

### План работ на новую сессию:

1. **Формализация обновлённого набора тестов рантайма:**
   - Исторические тесты в Audit/ (test_data_hardening.py, test_replay_safety.py, test_protection.py, test_phase16_p3_runtime.py) ожидали старый заблокированный рантайм (INCOMPLETE_REPLAY, require false).
   - Создать/актуализировать специализированную сюиту тестов (например, tests/test_wall_surface_runtime.py или Audit/phase16-p3-auth-tests/), фиксирующую проверенные контракты:
     * 16 хелперов p3*;
     * TriMesh RNormals и SmoothGroup снапшоты с delete;
     * subAnim рекурсивный аудит;
     * LayerAdmissionGuard;
     * Replay VERIFIED_NOOP ветку;
     * POISONED сохранение ключа при сбое arm.
   - Запустить recorder для получения 100% зелёного отчёта по актуальным сюитам.

2. **Интеграция QA Profile для стен (Фаза P4):**
   - Интегрировать проверки для полигональных стен в QA-пайплайн (scripts/qa_check.py):
     * Gate направления: внутренняя грань на Y=0, вектор нормали наружу в -Y;
     * Gate объёма: допуск по объёму evaluated mesh;
     * Gate топологии и стека: запрет лишних модификаторов, строго Shell.

3. **Генерация и масштабирование остальных фикстур (F02–F08):**
   - Расширить генерацию на фикстуры F02–F08 (стены различной конфигурации, глухие стены, стены с несколькими проёмами, угловые сопряжения) через build_wall_surface.py.
   - Проверить стабильность генерации и соответствие аналитическим объёмам.

4. **Проверка сосуществования с S5 Assembly (place_components.py):**
   - Проверить совмещение poly_surface_shell_v1 стен с фасадной сеткой и Mechanism A (скрытие host-стены).

Проверяй actual exceptions, __MCP_MS_ERR__, ERROR/cleanup outcomes, а не только transport ok=true.
Обновляй CHECKPOINT с точными hashes и честным статусом.
```
