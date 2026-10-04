from __future__ import annotations

import importlib.util
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "tmp" / "pdfs" / "assets"
OUTPUT = ROOT / "output" / "docx"
OUTPUT.mkdir(parents=True, exist_ok=True)

DATA_SPEC = importlib.util.spec_from_file_location(
    "report_data", ROOT / "tmp" / "pdfs" / "generate_reports.py"
)
DATA = importlib.util.module_from_spec(DATA_SPEC)
assert DATA_SPEC.loader is not None
DATA_SPEC.loader.exec_module(DATA)


NAVY = "17365D"
TEAL = "0F7C83"
PALE = "F2F7FA"
LIGHT_GRAY = "D9D9D9"
MID_GRAY = "666666"
RED = "A62B3C"
BLACK = RGBColor(0, 0, 0)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=90, bottom=90, end=90) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color: str = LIGHT_GRAY, size: str = "6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_fixed_layout(table) -> None:
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.first_child_found_in("w:tblLayout")
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def set_run_font(run, name: str = "Arial", size: float | None = None, bold=None, color=None) -> None:
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def style_paragraph_runs(paragraph, size=None, bold=None, color=None) -> None:
    for run in paragraph.runs:
        set_run_font(run, size=size, bold=bold, color=color)


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = BLACK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    title = doc.styles["Title"]
    title.font.name = "Arial"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    title.font.size = Pt(24)
    title.font.bold = True
    title.font.color.rgb = BLACK
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(8)
    title_ppr = title._element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)

    for style_name, size in (("Heading 1", 15), ("Heading 2", 12)):
        style = doc.styles[style_name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = BLACK
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True

    if "Subtitle" in doc.styles:
        subtitle = doc.styles["Subtitle"]
        subtitle.font.name = "Arial"
        subtitle._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        subtitle._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        subtitle.font.size = Pt(11.5)
        subtitle.font.color.rgb = BLACK
        subtitle.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle.paragraph_format.space_after = Pt(18)

    caption = doc.styles["Caption"]
    caption.font.name = "Arial"
    caption._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    caption._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    caption.font.size = Pt(8)
    caption.font.italic = True
    caption.font.color.rgb = RGBColor(90, 90, 90)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_after = Pt(8)


def configure_section(section) -> None:
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(18)
    section.bottom_margin = Mm(17)
    section.left_margin = Mm(16)
    section.right_margin = Mm(16)
    section.header_distance = Mm(7)
    section.footer_distance = Mm(7)
    section.different_first_page_header_footer = True


def add_page_number(paragraph) -> None:
    paragraph.add_run("Strona ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)


def configure_header_footer(section, short_title: str) -> None:
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(2)
    content_width = section.page_width - section.left_margin - section.right_margin
    p.paragraph_format.tab_stops.add_tab_stop(content_width - Mm(2), WD_TAB_ALIGNMENT.RIGHT)
    left = p.add_run(short_title)
    set_run_font(left, size=8, bold=True, color=RGBColor(30, 30, 30))
    right = p.add_run("\tDANE SYMULOWANE")
    set_run_font(right, size=8, bold=True, color=RGBColor(166, 43, 60))

    first_header = section.first_page_header
    first_header.paragraphs[0].text = ""

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = Pt(2)
    run = fp.add_run("Przykład dydaktyczny   |   ")
    set_run_font(run, size=7.5, color=RGBColor(100, 100, 100))
    add_page_number(fp)
    style_paragraph_runs(fp, size=7.5, color=RGBColor(100, 100, 100))

    first_footer = section.first_page_footer
    first_footer.paragraphs[0].text = ""


def add_branding(doc: Document) -> None:
    table = doc.add_table(rows=2, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [Cm(2.2), Cm(11.8), Cm(2.8)]
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = widths[idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, 80, 80, 80, 80)
    table.cell(0, 0).merge(table.cell(1, 0))
    table.cell(0, 2).merge(table.cell(1, 2))
    set_cell_shading(table.cell(0, 0), "52A9E2")
    p = table.cell(0, 0).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("INT")
    set_run_font(run, size=16, bold=True, color=RGBColor(255, 255, 255))
    p = table.cell(0, 1).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("INSTYTUT NAUK TECHNICZNYCH")
    set_run_font(run, size=11, bold=True, color=BLACK)
    p = table.cell(1, 1).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("UNIWERSYTET KOMISJI EDUKACJI NARODOWEJ W KRAKOWIE")
    set_run_font(run, size=7.3, color=RGBColor(60, 60, 60))
    p = table.cell(0, 2).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("UKEN")
    set_run_font(run, size=15, bold=True, color=RGBColor(20, 55, 105))
    set_table_borders(table)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)


def add_cover(doc: Document, title: str, subtitle: str) -> None:
    add_branding(doc)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(26)

    kicker = doc.add_paragraph()
    kicker.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = kicker.add_run("SPRAWOZDANIE Z ĆWICZENIA LABORATORYJNEGO")
    set_run_font(run, size=9, bold=True, color=RGBColor(15, 124, 131))
    kicker.paragraph_format.space_after = Pt(8)

    p = doc.add_paragraph(title, style="Title")
    ppr = p._p.get_or_add_pPr()
    border = ppr.find(qn("w:pBdr"))
    if border is not None:
        ppr.remove(border)
    p.paragraph_format.keep_with_next = True
    p = doc.add_paragraph(subtitle, style="Subtitle")
    p.paragraph_format.keep_with_next = True

    notice = doc.add_paragraph()
    notice.alignment = WD_ALIGN_PARAGRAPH.CENTER
    notice.paragraph_format.space_before = Pt(10)
    notice.paragraph_format.space_after = Pt(4)
    run = notice.add_run("WERSJA SYMULACYJNA")
    set_run_font(run, size=10.5, bold=True, color=RGBColor(166, 43, 60))
    description = doc.add_paragraph(
        "Dane w tabelach są przykładem obliczeniowym i nie stanowią zapisu rzeczywiście przeprowadzonej serii pomiarowej."
    )
    description.alignment = WD_ALIGN_PARAGRAPH.CENTER
    description.paragraph_format.space_after = Pt(18)

    details = doc.add_table(rows=4, cols=2)
    details.alignment = WD_TABLE_ALIGNMENT.CENTER
    details.autofit = False
    labels = ["Autor", "Przedmiot", "Charakter danych", "Opracowanie"]
    values = [
        "Wiktor Złotnik",
        "Metrologia i systemy pomiarowe",
        "Symulacja dydaktyczna i przykład obliczeniowy",
        "Nowa redakcja i układ graficzny wrzesień 2026",
    ]
    for idx, row in enumerate(details.rows):
        row.cells[0].width = Cm(4.3)
        row.cells[1].width = Cm(12.1)
        set_cell_shading(row.cells[0], NAVY)
        if idx % 2 == 1:
            set_cell_shading(row.cells[1], PALE)
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, 110, 140, 110, 140)
        p = row.cells[0].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(labels[idx].upper())
        set_run_font(run, size=8, bold=True, color=RGBColor(255, 255, 255))
        p = row.cells[1].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(values[idx])
        set_run_font(run, size=8.5, color=RGBColor(45, 45, 45))
    set_table_borders(details)
    set_fixed_layout(details)
    doc.add_page_break()


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True


def add_body(doc: Document, text: str) -> None:
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.widow_control = True


def add_numbered_steps(doc: Document, items: list[str]) -> None:
    for idx, item in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Mm(5)
        p.paragraph_format.first_line_indent = Mm(-5)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(f"{idx:02d}  ")
        set_run_font(run, size=9.5, bold=True, color=RGBColor(15, 124, 131))
        run = p.add_run(item)
        set_run_font(run, size=10.2, color=BLACK)


def add_figure(doc: Document, path: Path, caption: str, width_cm: float) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    cap = doc.add_paragraph(caption, style="Caption")
    cap.paragraph_format.keep_with_next = False


def set_table_font(table, size: float, header_size: float | None = None) -> None:
    for r_idx, row in enumerate(table.rows):
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    set_run_font(
                        run,
                        size=header_size if r_idx == 0 and header_size is not None else size,
                        bold=True if r_idx == 0 else False,
                        color=RGBColor(255, 255, 255) if r_idx == 0 else BLACK,
                    )


def add_raw_table(doc: Document, columns: dict[str, list[float]], digits: int) -> None:
    labels = list(columns)
    rows = len(next(iter(columns.values()))) + 1
    table = doc.add_table(rows=rows, cols=len(labels) + 1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_fixed_layout(table)
    header = ["Lp"] + labels
    for c_idx, text in enumerate(header):
        cell = table.cell(0, c_idx)
        cell.text = text
        set_cell_shading(cell, NAVY)
    for r_idx in range(1, rows):
        table.cell(r_idx, 0).text = str(r_idx)
        for c_idx, label in enumerate(labels, 1):
            table.cell(r_idx, c_idx).text = DATA.pl(columns[label][r_idx - 1], digits)
        if r_idx % 2 == 0:
            for cell in table.rows[r_idx].cells:
                set_cell_shading(cell, PALE)

    total_width_cm = 17.4
    first_width = 0.75
    other_width = (total_width_cm - first_width) / len(labels)
    for row in table.rows:
        prevent_row_split(row)
        for c_idx, cell in enumerate(row.cells):
            cell.width = Cm(first_width if c_idx == 0 else other_width)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, 70, 55, 70, 55)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
    set_repeat_table_header(table.rows[0])
    set_table_borders(table)
    set_table_font(table, 7.6 if len(labels) <= 8 else 6.5, 7.4 if len(labels) <= 8 else 6.8)
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(3)


def add_summary_table(doc: Document, columns: dict[str, list[float]], mean_digits: int) -> None:
    headers = ["Wymiar", "n", "Średnia mm", "uA mm", "U95 mm", "Przedział 95 procent mm"]
    table = doc.add_table(rows=len(columns) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_fixed_layout(table)
    for c_idx, header in enumerate(headers):
        table.cell(0, c_idx).text = header
        set_cell_shading(table.cell(0, c_idx), TEAL)
    for r_idx, (label, values) in enumerate(columns.items(), 1):
        result = DATA.stats(values)
        cells = [
            label,
            str(result["n"]),
            DATA.pl(result["mean"], mean_digits),
            DATA.pl(result["u"], 5),
            DATA.pl(result["U"], 5),
            f'{DATA.pl(result["lo"], 5)} do {DATA.pl(result["hi"], 5)}',
        ]
        for c_idx, value in enumerate(cells):
            table.cell(r_idx, c_idx).text = value
        if r_idx % 2 == 0:
            for cell in table.rows[r_idx].cells:
                set_cell_shading(cell, PALE)
    widths = [Cm(1.5), Cm(1.0), Cm(2.5), Cm(2.1), Cm(2.1), Cm(8.0)]
    for row in table.rows:
        prevent_row_split(row)
        for c_idx, cell in enumerate(row.cells):
            cell.width = widths[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, 75, 80, 75, 80)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
    set_repeat_table_header(table.rows[0])
    set_table_borders(table)
    set_table_font(table, 7.2, 7.0)
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(3)


def m_run(text: str):
    run = OxmlElement("m:r")
    run_pr = OxmlElement("m:rPr")
    normal = OxmlElement("m:nor")
    run_pr.append(normal)
    run.append(run_pr)
    node = OxmlElement("m:t")
    node.text = text
    run.append(node)
    return run


def m_sub(base, sub):
    node = OxmlElement("m:sSub")
    base_el = OxmlElement("m:e")
    base_el.append(base)
    sub_el = OxmlElement("m:sub")
    sub_el.append(sub)
    node.extend([base_el, sub_el])
    return node


def m_sup(base, sup):
    node = OxmlElement("m:sSup")
    base_el = OxmlElement("m:e")
    base_el.append(base)
    sup_el = OxmlElement("m:sup")
    sup_el.append(sup)
    node.extend([base_el, sup_el])
    return node


def m_frac(numerator: list, denominator: list):
    node = OxmlElement("m:f")
    num = OxmlElement("m:num")
    den = OxmlElement("m:den")
    for part in numerator:
        num.append(part)
    for part in denominator:
        den.append(part)
    node.extend([num, den])
    return node


def m_rad(parts: list):
    node = OxmlElement("m:rad")
    rad_pr = OxmlElement("m:radPr")
    deg_hide = OxmlElement("m:degHide")
    deg_hide.set(qn("m:val"), "1")
    rad_pr.append(deg_hide)
    degree = OxmlElement("m:deg")
    expression = OxmlElement("m:e")
    for part in parts:
        expression.append(part)
    node.extend([rad_pr, degree, expression])
    return node


def m_bar_x():
    node = OxmlElement("m:acc")
    props = OxmlElement("m:accPr")
    char = OxmlElement("m:chr")
    char.set(qn("m:val"), "¯")
    props.append(char)
    expr = OxmlElement("m:e")
    expr.append(m_run("x"))
    node.extend([props, expr])
    return node


def add_equation(doc: Document, parts: list, keep_with_next: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = keep_with_next
    math_para = OxmlElement("m:oMathPara")
    math_pr = OxmlElement("m:oMathParaPr")
    justification = OxmlElement("m:jc")
    justification.set(qn("m:val"), "center")
    math_pr.append(justification)
    math_para.append(math_pr)
    math = OxmlElement("m:oMath")
    for part in parts:
        math.append(part)
    math_para.append(math)
    p._p.append(math_para)


def add_model_equations(doc: Document) -> None:
    add_heading(doc, "Model statystyczny", 2)
    add_body(
        doc,
        "Dla każdej serii przyjęto dziesięć odczytów. Statystyczną niepewność średniej wyznaczono na podstawie rozrzutu serii. Dla poziomu ufności 95 procent i dziewięciu stopni swobody zastosowano współczynnik t Studenta równy 2,2622.",
    )
    add_equation(
        doc,
        [m_bar_x(), m_run(" = "), m_frac([m_run("Σ"), m_sub(m_run("x"), m_run("i"))], [m_run("n")])],
        keep_with_next=True,
    )
    add_equation(
        doc,
        [
            m_sub(m_run("u"), m_run("A")),
            m_run(" = "),
            m_rad(
                [
                    m_frac(
                        [m_run("Σ("), m_sub(m_run("x"), m_run("i")), m_run(" - "), m_bar_x(), m_sup(m_run(")"), m_run("2"))],
                        [m_run("n(n - 1)")],
                    )
                ]
            ),
        ],
        keep_with_next=True,
    )
    add_equation(
        doc,
        [m_sub(m_run("U"), m_run("95")), m_run(" = k · "), m_sub(m_run("u"), m_run("A"))],
    )


def add_example_calculation(doc: Document, values: list[float], label: str, digits: int) -> None:
    result = DATA.stats(values)
    add_heading(doc, f"Przykład obliczeń seria {label}", 2)
    numerator = " + ".join(DATA.pl(value, digits) for value in values)
    add_equation(
        doc,
        [
            m_bar_x(),
            m_run(" = "),
            m_frac([m_run(numerator)], [m_run(str(result["n"]))]),
            m_run(f' = {DATA.pl(result["mean"], digits + 2)} mm'),
        ],
        keep_with_next=True,
    )
    add_equation(
        doc,
        [
            m_sub(m_run("u"), m_run("A")),
            m_run(" = "),
            m_rad(
                [
                    m_frac(
                        [m_run(DATA.pl(result["ss"], 7))],
                        [m_run(f'{result["n"]} · {result["n"] - 1}')],
                    )
                ]
            ),
            m_run(f' = {DATA.pl(result["u"], 6)} mm'),
        ],
        keep_with_next=True,
    )
    add_equation(
        doc,
        [
            m_sub(m_run("U"), m_run("95")),
            m_run(f' = 2,2622 · {DATA.pl(result["u"], 6)} = {DATA.pl(result["U"], 6)} mm'),
        ],
        keep_with_next=True,
    )
    add_equation(
        doc,
        [
            m_run("N = (") ,
            m_run(DATA.pl(result["mean"], digits + 2)),
            m_run(" ± "),
            m_run(DATA.pl(result["U"], 6)),
            m_run(") mm"),
        ],
    )


def add_simulation_note(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run("Dane symulowane  ")
    set_run_font(run, size=10, bold=True, color=RGBColor(166, 43, 60))
    run = p.add_run(text)
    set_run_font(run, size=10, color=BLACK)


def add_literature(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(item)
        set_run_font(run, size=9, color=BLACK)


def new_document(title: str, short_title: str, subtitle: str) -> Document:
    doc = Document()
    configure_styles(doc)
    configure_section(doc.sections[0])
    configure_header_footer(doc.sections[0], short_title)
    doc.core_properties.title = title
    doc.core_properties.author = "Wiktor Złotnik"
    doc.core_properties.subject = "Edytowalne sprawozdanie z oznaczonymi danymi symulowanymi"
    add_cover(doc, title, subtitle)
    return doc


def build_dial() -> Path:
    title = "Pomiary długości czujnikiem zegarowym"
    doc = new_document(
        title,
        "Czujnik zegarowy",
        "Metoda porównawcza oraz statystyczne opracowanie wyników",
    )
    add_heading(doc, "1 Cel i zakres ćwiczenia")
    add_body(
        doc,
        "Ćwiczenie służy poznaniu konstrukcji czujnika zegarowego, zasad jego mocowania oraz sposobu prowadzenia pomiarów porównawczych. Zakres obejmuje przygotowanie stanowiska, wyzerowanie wskazania względem elementu odniesienia, odczyt niewielkich różnic wymiaru oraz statystyczne opracowanie serii wyników.",
    )
    add_body(
        doc,
        "Pomiar jest porównaniem badanej wielkości z przyjętą jednostką lub wzorcem. Wynik powinien zawierać informację o rozrzucie i zakresie, w którym z przyjętym prawdopodobieństwem znajduje się wartość oczekiwana. W opracowaniu wykorzystano średnią z serii, niepewność standardową średniej i przedział ufności oparty na rozkładzie t Studenta.",
    )
    add_heading(doc, "2 Budowa i zasada działania")
    add_body(
        doc,
        "Ruch trzpienia pomiarowego jest przenoszony przez przekładnię zębatą na wskazówkę obracającą się nad tarczą. W typowym przyrządzie jedna działka odpowiada 0,01 mm, a dodatkowy licznik rejestruje pełne obroty wskazówki. Czujnik pokazuje różnicę pomiędzy położeniem ustawionym przy zerowaniu a położeniem badanej powierzchni.",
    )
    add_figure(doc, ASSETS / "doc1_p3_img1.png", "Rysunek 1  Podstawowe elementy analogowego czujnika zegarowego", 8.5)
    add_heading(doc, "3 Przebieg pomiaru")
    add_numbered_steps(
        doc,
        [
            "Oczyszczono płytę, element odniesienia, badany detal oraz końcówkę trzpienia.",
            "Czujnik zamocowano w statywie i ustawiono trzpień prostopadle do mierzonej powierzchni.",
            "Po nadaniu nacisku wstępnego ustawiono tarczę w położeniu zerowym.",
            "Dla wymiarów A i B wykonano po dziesięć odczytów.",
            "Serie opracowano statystycznie zgodnie z przedstawionym modelem.",
        ],
    )
    add_figure(doc, ASSETS / "doc1_p5_img1.png", "Rysunek 2  Schemat badanego elementu i oznaczenia wymiarów A oraz B", 13.6)

    add_heading(doc, "4 Dane symulowane")
    add_simulation_note(doc, "Wartości zmieniono o pojedyncze działki elementarne, zachowując rozdzielczość 0,01 mm i zbliżony poziom rozrzutu.")
    add_raw_table(doc, DATA.DIAL_DATA, 2)
    add_model_equations(doc)
    add_example_calculation(doc, DATA.DIAL_DATA["A"], "A", 2)
    add_heading(doc, "5 Zestawienie wyników")
    add_summary_table(doc, DATA.DIAL_DATA, 3)
    add_heading(doc, "6 Wnioski")
    add_body(
        doc,
        "Symulowane serie A i B mają niewielki rozrzut odpowiadający pojedynczym działkom czujnika. Wąskie przedziały ufności ilustrują czułość metody porównawczej, lecz nie określają pełnej dokładności rzeczywistego pomiaru. Pełna ocena powinna uwzględniać wzorcowanie, rozdzielczość, błąd ustawienia i stabilność stanowiska.",
    )
    add_body(
        doc,
        "Największy wpływ na wynik mają prostopadłość osi trzpienia do powierzchni, stały kierunek dojścia, prawidłowe zerowanie i czystość elementów stykowych. Precyzyjny czujnik nie kompensuje błędów wynikających z niestabilnego mocowania lub niewłaściwej techniki operatora.",
    )
    add_heading(doc, "7 Literatura i materiały")
    add_literature(
        doc,
        [
            "PN 71 N 02050 Metrologia nazwy i określenia",
            "Instrukcja użytkowania czujników zegarowych e darmet",
            "Budowa czujnika zegarowego blog cnc",
            "Autorskie notatki z ćwiczenia laboratoryjnego",
        ],
    )
    path = OUTPUT / "czujnik_zegarowy_wersja_edytowalna.docx"
    doc.save(path)
    return path


def build_micrometer() -> Path:
    title = "Pomiary mikrometrem zewnętrznym"
    doc = new_document(
        title,
        "Mikrometr zewnętrzny",
        "Śruba mikrometryczna technika odczytu i analiza wyników",
    )
    add_heading(doc, "1 Cel ćwiczenia")
    add_body(
        doc,
        "Celem ćwiczenia jest opanowanie prawidłowej obsługi mikrometru zewnętrznego oraz wykonanie powtarzalnych pomiarów długości z rozdzielczością 0,01 mm. Opracowanie obejmuje kontrolę położenia zerowego, poprawne użycie sprzęgiełka i analizę niepewności wyznaczonej z serii odczytów.",
    )
    add_heading(doc, "2 Podstawy działania przyrządu")
    add_body(
        doc,
        "Mikrometr wykorzystuje precyzyjną parę śrubową. Obrót bębna powoduje osiowe przesunięcie wrzeciona, a wartość wymiaru odczytuje się jako sumę wskazania na tulei i części wynikającej z położenia podziałki bębna. Dla typowego skoku śruby 0,5 mm i pięćdziesięciu działek jeden odstęp podziałki odpowiada 0,01 mm.",
    )
    add_figure(doc, ASSETS / "doc3_p3_img1.png", "Rysunek 1  Mikrometr zewnętrzny", 12.8)
    add_body(
        doc,
        "Sprzęgiełko ogranicza siłę docisku, dlatego końcowe zbliżanie powierzchni pomiarowych powinno odbywać się z jego użyciem. Na wynik wpływają zabrudzenia, temperatura przyrządu i przedmiotu, nieosiowe ustawienie oraz błąd odczytu skali.",
    )
    add_heading(doc, "3 Przygotowanie i przebieg")
    add_numbered_steps(
        doc,
        [
            "Skontrolowano czystość kowadełka i wrzeciona oraz sprawdzono wskazanie zerowe.",
            "Mierzony detal ustawiono pomiędzy powierzchniami pomiarowymi bez przekoszenia.",
            "Wrzeciono dosuwano sprzęgiełkiem do uzyskania lekkiego i powtarzalnego docisku.",
            "Dla ośmiu wymiarów A do H wykonano po dziesięć odczytów.",
            "Po każdej serii obliczono średnią i przedział ufności 95 procent.",
        ],
    )
    add_figure(doc, ASSETS / "doc3_p4_img1.png", "Rysunek 2  Schemat badanego detalu i oznaczenia wymiarów A do H", 9.8)

    add_heading(doc, "4 Dane symulowane")
    add_simulation_note(doc, "Odczyty zmodyfikowano o niewielkie wartości rzędu 0,01 mm i zachowano rozrzut typowy dla przyjętej rozdzielczości.")
    add_raw_table(doc, DATA.MIC_DATA, 2)
    add_model_equations(doc)
    add_example_calculation(doc, DATA.MIC_DATA["A"], "A", 2)
    add_heading(doc, "5 Zestawienie obliczeń")
    add_summary_table(doc, DATA.MIC_DATA, 3)
    add_heading(doc, "6 Wnioski")
    add_body(
        doc,
        "Przykładowe serie pokazują wysoką powtarzalność pomiarów mikrometrem. Zmiany mieszczą się w zakresie kilku setnych milimetra, a przedziały ufności średnich są wąskie. Ostateczna jakość rzeczywistego wyniku zależy jednak od warunków termicznych, stanu powierzchni pomiarowych, kontroli zera, ustawienia detalu i sposobu użycia sprzęgiełka.",
    )
    add_heading(doc, "7 Literatura i materiały")
    add_literature(
        doc,
        [
            "PN 71 N 02050 Metrologia nazwy i określenia",
            "Materiały dydaktyczne Uniwersytetu Jagiellońskiego i Politechniki Warszawskiej dotyczące śruby mikrometrycznej",
            "Katalog przyrządów LIMIT oraz autorskie notatki z laboratorium",
        ],
    )
    path = OUTPUT / "sruba_mikrometryczna_wersja_edytowalna.docx"
    doc.save(path)
    return path


def add_comparison_table(doc: Document) -> None:
    datasets = [
        ("0,10 mm", DATA.CALIPER_01),
        ("0,05 mm", DATA.CALIPER_005),
        ("0,02 mm", DATA.CALIPER_002),
    ]
    table = doc.add_table(rows=4, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    headers = ["Rozdzielczość", "Średnie U95 dla A do K mm", "Największe U95 mm"]
    for c_idx, header in enumerate(headers):
        table.cell(0, c_idx).text = header
        set_cell_shading(table.cell(0, c_idx), NAVY)
    for r_idx, (label, dataset) in enumerate(datasets, 1):
        uncertainties = [DATA.stats(values)["U"] for values in dataset.values()]
        values = [label, DATA.pl(sum(uncertainties) / len(uncertainties), 5), DATA.pl(max(uncertainties), 5)]
        for c_idx, value in enumerate(values):
            table.cell(r_idx, c_idx).text = value
        if r_idx % 2 == 0:
            for cell in table.rows[r_idx].cells:
                set_cell_shading(cell, PALE)
    widths = [Cm(4.3), Cm(7.0), Cm(5.6)]
    for row in table.rows:
        for c_idx, cell in enumerate(row.cells):
            cell.width = widths[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, 100, 100, 100, 100)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
    set_repeat_table_header(table.rows[0])
    set_table_borders(table)
    set_fixed_layout(table)
    set_table_font(table, 8.2, 8.0)


def build_caliper() -> Path:
    title = "Pomiary suwmiarką analogową"
    doc = new_document(
        title,
        "Suwmiarka analogowa",
        "Porównanie serii dla trzech rozdzielczości noniusza",
    )
    add_heading(doc, "1 Cel i zakres ćwiczenia")
    add_body(
        doc,
        "Ćwiczenie obejmuje pomiary wymiarów zewnętrznych, wewnętrznych i głębokości za pomocą suwmiarki analogowej. Celem jest również porównanie wyników uzyskiwanych przy trzech rozdzielczościach noniusza oraz ocena wpływu rozdzielczości i powtarzalności odczytu na statystyczną niepewność średniej.",
    )
    add_heading(doc, "2 Budowa i sposób odczytu")
    add_body(
        doc,
        "Suwmiarka składa się z prowadnicy ze skalą główną, suwaka z noniuszem, szczęk pomiarowych i głębokościomierza. Pełne milimetry odczytuje się na skali głównej przed zerem noniusza. Część ułamkową wyznacza kreska noniusza pokrywająca się z kreską skali głównej.",
    )
    add_body(
        doc,
        "Szczęki powinny przylegać do powierzchni bez nadmiernego nacisku. Przy pomiarze wymiaru zewnętrznego należy zachować prostopadłość do osi detalu, a odczyt prowadzić prostopadle do skali, aby ograniczyć błąd paralaksy.",
    )
    add_figure(doc, ASSETS / "doc2_p3_img1.png", "Rysunek 1  Badany element schodkowy i oznaczenia wymiarów A do K", 14.5)
    add_heading(doc, "3 Przebieg pomiaru")
    add_numbered_steps(
        doc,
        [
            "Oczyszczono powierzchnie detalu, szczęki i prowadnicę przyrządu.",
            "Sprawdzono zbieżność kresek zerowych przy zamkniętych szczękach.",
            "Dla wymiarów A do K wykonano po dziesięć odczytów trzema suwmiarkami.",
            "Wartości zapisywano zgodnie z działką elementarną danego noniusza.",
            "Dla każdej kolumny wyznaczono średnią i statystyczny przedział ufności 95 procent.",
        ],
    )

    doc.add_page_break()
    add_heading(doc, "4 Serie symulowane suwmiarka o rozdzielczości jednej dziesiątej milimetra")
    add_simulation_note(doc, "Zachowano krok 0,10 mm i nominalne wymiary detalu.")
    add_raw_table(doc, DATA.CALIPER_01, 1)
    add_summary_table(doc, DATA.CALIPER_01, 3)

    doc.add_page_break()
    add_heading(doc, "5 Serie symulowane suwmiarka o rozdzielczości pięciu setnych milimetra")
    add_simulation_note(doc, "Wartości zapisano z krokiem 0,05 mm i zmniejszono rozrzut względem pierwszej serii.")
    add_raw_table(doc, DATA.CALIPER_005, 2)
    add_summary_table(doc, DATA.CALIPER_005, 3)

    doc.add_page_break()
    add_heading(doc, "6 Serie symulowane suwmiarka o rozdzielczości dwóch setnych milimetra")
    add_simulation_note(doc, "Każdy odczyt jest zgodny z działką 0,02 mm i zachowuje niewielki rozrzut wokół wymiaru nominalnego.")
    add_raw_table(doc, DATA.CALIPER_002, 2)
    add_summary_table(doc, DATA.CALIPER_002, 3)

    doc.add_page_break()
    add_heading(doc, "7 Model obliczeń")
    add_model_equations(doc)
    add_example_calculation(doc, DATA.CALIPER_002["A"], "A", 2)
    add_heading(doc, "8 Porównanie wariantów")
    add_comparison_table(doc)
    add_heading(doc, "9 Wnioski")
    add_body(
        doc,
        "W symulacji zmniejszenie działki elementarnej wiąże się ze spadkiem przeciętnej niepewności wyznaczonej z rozrzutu serii. Najbardziej skupione wyniki uzyskano dla wariantu 0,02 mm, a suwmiarka 0,10 mm daje najszersze przedziały. Jest to efekt przyjętego modelu danych, a nie porównanie konkretnych egzemplarzy przyrządów.",
    )
    add_body(
        doc,
        "W praktyce rozdzielczość jest tylko jednym ze składników jakości pomiaru. Znaczenie mają również stan szczęk, błąd zera, kierunek docisku, ustawienie detalu, paralaksa i doświadczenie operatora. Mały rozrzut serii nie dowodzi idealnej dokładności, ponieważ nie obejmuje składników niepewności typu B.",
    )
    add_heading(doc, "10 Literatura i materiały")
    add_literature(
        doc,
        [
            "PN 71 N 02050 Metrologia nazwy i określenia",
            "Materiały dydaktyczne do ćwiczeń z pomiarów suwmiarką analogową",
            "Materiały własne schemat badanego elementu i notatki z laboratorium",
        ],
    )
    path = OUTPUT / "suwmiarka_wersja_edytowalna.docx"
    doc.save(path)
    return path


def main() -> None:
    for output in (build_dial(), build_caliper(), build_micrometer()):
        print(output)


if __name__ == "__main__":
    main()
