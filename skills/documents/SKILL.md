---
name: documents
description: Создание и правка офисных документов: Word (.docx), PDF, PowerPoint (.pptx), Excel (.xlsx). Использовать, когда пользователь просит сделать отчёт, реферат, презентацию, таблицу или что-то прочитать/изменить из этих файлов.
---

# Документы (Word / PDF / PPT / Excel)

Вся работа — в песочнице агента, на Python. Библиотеки ставятся на лету (интернет есть).

## Установка (в начале сессии, при первой надобности)
```bash
pip install -q python-docx pypdf python-pptx openpyxl
```
Все четыре проверены работающими (Python 3.13, 2026-09-22).

## Word (.docx) — отчёты, рефераты
```python
from docx import Document
doc = Document()
doc.add_heading('Отчёт', 0)
doc.add_paragraph('Текст…')
doc.save('otchet.docx')
```
- Чтение: `Document('файл.docx')` → `.paragraphs`, `.tables`.
- Вставка таблиц, списков, заголовков — стандартные методы python-docx.

## PDF
- Чтение текста: `pypdf` → `PdfReader('файл.pdf').pages[i].extract_text()`.
- Слить / разрезать / повернуть: `pypdf` → `PdfWriter`.
- Создание PDF с нуля: сначала .docx (python-docx), конвертация через LibreOffice, если он есть в песочнице (проверить: `which soffice`).
- OCR сканов: `pytesseract` + `pdf2image` (установить при надобности).

## PowerPoint (.pptx)
```python
from pptx import Presentation
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])  # 1 = заголовок + текст
slide.shapes.title.text = 'Заголовок'
slide.placeholders[1].text = 'Текст слайда'
prs.save('prezentaciya.pptx')
```

## Excel (.xlsx)
```python
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws.append(['Предмет', 'Зачётные единицы', 'Статус'])
ws.append(['Математика', 6, 'идёт'])
wb.save('tablica.xlsx')
```

## Правила
- Язык содержания — русский (или как попросит пользователь).
- Имя файла — латиницей, по содержанию: `otchet_fizika_2.docx`.
- Готовый файл обязательно передать пользователю (показать в чате / положить туда, где он его видит).
- Сложная задача (много таблиц, специфические стили, формы) — сначала план, потом работа, результат показать до финала.
- Углублённые случаи: смотреть официальные скиллы upstream (github.com/anthropics/skills) как **референс** — в наш репо их не копировать (proprietary-лицензия), наши скиллы — свои.
