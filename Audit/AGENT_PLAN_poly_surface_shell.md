# SUPERSEDED — прежний план `poly_surface_shell_v1`

**2026-11-04:** этот документ больше не задаёт активный маршрут разработки стен.
Single-wall этапы и их прежние статусы не являются приёмкой замкнутой оболочки этажа.

- **Активный план v4:** [`../PLAN.md`](../PLAN.md).
- **Целевая архитектура `closed_inner_contour_shell_v2` и гейты миграции:**
  [`../experiments/closed-contour-shell-v2/MIGRATION_PLAN.md`](../experiments/closed-contour-shell-v2/MIGRATION_PLAN.md).
- **Полная неизменённая прежняя версия этого документа:**
  [`../experiments/closed-contour-shell-v2/prior-wall-route-plan.md`](../experiments/closed-contour-shell-v2/prior-wall-route-plan.md).
- **Фактические результаты прототипа и ограничения:**
  [`../experiments/closed-contour-shell-v2/README.md`](../experiments/closed-contour-shell-v2/README.md).
- **Источник принятых статусов:** [`../CHECKPOINT.md`](../CHECKPOINT.md).

Прототип v2 имеет **6/6 live PASS ограниченных проверок**; пользователь визуально принял
прямоугольный образец 2026-11-04,
production-интеграция ещё не принята. `legacy_cells_v1` остаётся явной совместимостью;
молчаливого fallback нет. Старые lease/witness/nonce/`POISONED` и аудит rootScene/controller
graph не являются обязательствами v2. Исторические доказательства сохраняются, не удаляются.
