# Готовый prompt следующей сессии — Phase 16 P3.1, 2026-11-02e

Host date предыдущей сессии — 2026-11-03; имена evidence сохраняют `2026-11-02e`.
Скопируй текст ниже как задание:

---

Продолжай Phase 16 P3.1 в `D:\Rhino\3dsmax-arch-nurbs-ultimate-skill`.
Сначала прочитай `CHECKPOINT.md`, `AGENTS.md`, `PLAN.md` §4.0d,
`Audit/_phase16-p3-resume-2026-11-02e.md` и решённый
`Audit/_phase16-p3-contract-2026-11-02e.md`; итоговая проверка main:
[coordinator verification](_phase16-p3-coordinator-verification-2026-11-02e.md).
Сохрани ВСЕ прежние правки/artifacts/evidence;
никаких commit/reset/checkout/clean, установки, обновления архива/глобальных копий.

**P0/P1 и ограниченная offline-приёмка P2 действуют. P3.1 НЕ ПРИНЯТ.** Четыре новых
CLI/input/runtime/publication-модуля реализованы; точные tested hashes есть в handoff.
Main выполнил `Audit/phase16-p3-final2-2026-11-02e/`: 7/7 suites, 250 методов OK,
без SKIP/xfail, 307 entries стабильны до/после/process exit, HEAD прежний, четыре P2
source/49 legacy fixtures/package неизменны. Это offline, не приёмка геометрии.
Первый recorder с doc-drift — сохранённая история; поздние docs/layer-probe не часть FINAL2.

Я уже разрешил необходимую работу в Max; не возвращай случайно унаследованный запрет.
Максимально делегируй независимые задачи с явным непересекающимся владением; **live Max
выполняет только main**, короткими последовательными вызовами. Не reset/save, не очищать
dirty flag, не трогать AutoBackup; материалы/экспорт и установка незавершённого метода вне scope.

Реальный Main03 emitted fileIn через проверенный hash-held wrapper успешно armed,
но initial baseline упал на `MixinInterface:LayerProperties -> MaxObject`; точная
попытка убрана, objects=0, exact lease/witness сохранён POISONED. Реальный повтор той же
пары отказал без rearm/изменений. Читай
`Audit/_phase16-p3-main03-live-result-2026-11-02e.json` и
`Audit/_phase16-p3-live-final-controls-2026-11-02e.json`. Это НЕ clean NOOP;
принятой стены/полного F01 QA нет. Не auto-rearm/не удалять registry ради повторного запуска.

**Первое действие main — fresh read-only scene/state и осмотр точного POISONED lease**,
не доверие старому нулевому census. Затем разберись со специализированным bounded layer
reader/comparator, полным native/specified-normal metadata, controller/dependency сравнениями.
После FINAL2 main fileIn-нул
`Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-single-node.ms`, который записал
`Audit/phase16-p3-state-probes-2026-11-02e/layer-comparison-evidence.txt`.
Actual response/final snapshot: `Audit/_phase16-p3-post-test-layer-and-scene-2026-11-02e.json`.
В evidence default/self/repeat
equality и detached typed properties стабильны, bogus miss различим; handle/refCount всё
ещё бросают. Это материал для следующей калибровки, НЕ unique layer/edit-detection proof.
Нельзя обходить baseline/опускать поля/считать недоступность равенством.

После доказанного исправления: новые frozen bytes/tests и НОВАЯ artifact pair, reviewed
explicit lease protocol без перезаписи Main01–03, actual emitted fileIn, независимые
F01 direction/area/volume/topology/void/bounds/census/stack measurements. Далее три реальные
clean NOOP и целевые edit/collision/cleanup negatives с сохранением правок. Сохраняй
`INCOMPLETE_REPLAY`, пока полнота не доказана. Оригинальные 21 P2 skips не закрыты;
F02 и последующие integration/poly-QA гейты не выполнены, synthetic echoes не использовать.
Сверяй raw errors/markers, не один transport ok. Итог каждой стадии — честные PASS/FAIL/
INCOMPLETE с exact hashes; после публикации docs отдельные hashes, старые manifest не менять.
