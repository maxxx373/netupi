# База учебных заведений

Одна запись — один вуз или колледж, отдельным JSON-файлом:

```
data/
  schema.json              схема записи (JSON Schema)
  institutions/ru/*.json   российские вузы и колледжи
  institutions/abroad/*.json  зарубежные
  photos/<id>/…            фото со свободной лицензией
```

Имя файла совпадает с `id`: `data/institutions/ru/hse.json`.

## Правила

1. **Только проверяемые данные.** У каждой записи есть `sources` со ссылкой и датой. Не нашли — поле не заполняем, а пишем в `todo`. Ничего не выдумываем.
2. **Главный источник — официальный сайт вуза.** Агрегаторы только для сверки, их тексты не копируем.
3. **Фото только со свободной лицензией** (Wikimedia Commons и т.п.) или с разрешения вуза. Автор и лицензия записываются в `photos`.
4. **Цифры привязаны к году** (`data_year`, `passing_score.year`). Проходные баллы, цены и сроки меняются каждый год.
5. **`summary` пишем своими словами**, по-русски, 2–4 предложения.
6. **`confidence`** — честная оценка: `high`, если всё с официального сайта и свежее.

## Связь с анкетой

| Вопрос анкеты | Поле |
|---|---|
| Вуз или колледж | `type`, `levels` |
| Кем хочешь стать | `fields`, `programs[].field` |
| Баллы ЕГЭ / ОГЭ, аттестат | `programs[].passing_score`, `requirements.gpa_min` |
| Предметы ЕГЭ | `programs[].ege_subjects` |
| Олимпиады | `requirements.olympiad_benefits` |
| Активити | `requirements.activities_matter` |
| Портфолио | `requirements.portfolio` |
| Языки, уровень английского | `languages_of_instruction`, `requirements.language_level` |
| Международные экзамены | `requirements.intl_exams` |
| Россия / за границу, страна, город | `country`, `city` |
| Какой город комфортен | `city_size` |
| Грант обязателен, бюджет | `funding`, `cost` |
| Общежитие | `dorm` |
| Формат учёбы | `study_formats` |
| Что важно в вузе | `perks`, `rankings` |

## Проверка

```bash
python3 scripts/validate.py
```
