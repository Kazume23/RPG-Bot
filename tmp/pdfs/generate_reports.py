from __future__ import annotations

import math
from pathlib import Path
from statistics import mean

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "tmp" / "pdfs" / "assets"
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#102A43")
TEAL = colors.HexColor("#168C91")
TEAL_LIGHT = colors.HexColor("#E8F5F5")
ICE = colors.HexColor("#F4F8FA")
INK = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#52616B")
GRID = colors.HexColor("#C8D4DA")
RED = colors.HexColor("#A82C3B")
RED_LIGHT = colors.HexColor("#FCECEF")
WHITE = colors.white


pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", r"C:\Windows\Fonts\ariali.ttf"))


BASE = getSampleStyleSheet()
STYLES = {
    "body": ParagraphStyle(
        "BodyPL",
        parent=BASE["BodyText"],
        fontName="Arial",
        fontSize=9.2,
        leading=13.2,
        textColor=INK,
        alignment=TA_JUSTIFY,
        spaceAfter=3.5 * mm,
    ),
    "small": ParagraphStyle(
        "SmallPL",
        parent=BASE["BodyText"],
        fontName="Arial",
        fontSize=7.7,
        leading=10.2,
        textColor=MUTED,
        alignment=TA_LEFT,
    ),
    "caption": ParagraphStyle(
        "CaptionPL",
        parent=BASE["BodyText"],
        fontName="Arial-Italic",
        fontSize=7.4,
        leading=9.5,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=1.5 * mm,
        spaceAfter=4 * mm,
    ),
    "h1": ParagraphStyle(
        "Heading1PL",
        parent=BASE["Heading1"],
        fontName="Arial-Bold",
        fontSize=18,
        leading=22,
        textColor=NAVY,
        spaceBefore=2 * mm,
        spaceAfter=4 * mm,
    ),
    "h2": ParagraphStyle(
        "Heading2PL",
        parent=BASE["Heading2"],
        fontName="Arial-Bold",
        fontSize=12.5,
        leading=15,
        textColor=NAVY,
        spaceBefore=3 * mm,
        spaceAfter=2.5 * mm,
    ),
    "h3": ParagraphStyle(
        "Heading3PL",
        parent=BASE["Heading3"],
        fontName="Arial-Bold",
        fontSize=10,
        leading=12.5,
        textColor=TEAL,
        spaceBefore=2 * mm,
        spaceAfter=2 * mm,
    ),
    "cover_kicker": ParagraphStyle(
        "CoverKicker",
        parent=BASE["BodyText"],
        fontName="Arial-Bold",
        fontSize=9,
        leading=11,
        textColor=TEAL,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    ),
    "cover_title": ParagraphStyle(
        "CoverTitle",
        parent=BASE["Title"],
        fontName="Arial-Bold",
        fontSize=23,
        leading=28,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    ),
    "cover_subtitle": ParagraphStyle(
        "CoverSubtitle",
        parent=BASE["BodyText"],
        fontName="Arial",
        fontSize=11,
        leading=15,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    ),
    "formula": ParagraphStyle(
        "FormulaPL",
        parent=BASE["BodyText"],
        fontName="Arial",
        fontSize=9,
        leading=13,
        textColor=INK,
        leftIndent=5 * mm,
        rightIndent=5 * mm,
        spaceAfter=2 * mm,
    ),
}


def pl(value: float, digits: int) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def stats(values: list[float], k: float = 2.2622) -> dict[str, float]:
    n = len(values)
    avg = mean(values)
    ss = sum((value - avg) ** 2 for value in values)
    u_a = math.sqrt(ss / (n * (n - 1)))
    expanded = k * u_a
    return {
        "n": n,
        "mean": avg,
        "ss": ss,
        "u": u_a,
        "U": expanded,
        "lo": avg - expanded,
        "hi": avg + expanded,
    }


def paragraph(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def section(title: str, number: str | None = None) -> list:
    label = f"{number}. {title}" if number else title
    return [Paragraph(label, STYLES["h2"]), HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=3 * mm)]


def callout(title: str, text: str, warning: bool = False) -> Table:
    bg = RED_LIGHT if warning else TEAL_LIGHT
    accent = RED if warning else TEAL
    content = Paragraph(
        f'<font name="Arial-Bold" color="{accent.hexval()}">{title}</font><br/>{text}',
        ParagraphStyle(
            "Callout",
            parent=STYLES["body"],
            fontSize=8.5,
            leading=11.5,
            alignment=TA_LEFT,
            spaceAfter=0,
        ),
    )
    table = Table([[content]], colWidths=[174 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.8, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5 * mm),
            ]
        )
    )
    return table


def fitted_image(path: Path, max_width_mm: float, max_height_mm: float) -> Image:
    with PILImage.open(path) as source:
        width, height = source.size
    scale = min((max_width_mm * mm) / width, (max_height_mm * mm) / height)
    return Image(str(path), width=width * scale, height=height * scale)


def figure(path: Path, caption: str, max_width_mm: float = 125, max_height_mm: float = 72) -> list:
    img = fitted_image(path, max_width_mm, max_height_mm)
    img.hAlign = "CENTER"
    return [img, paragraph(caption, "caption")]


def cover_story(report: dict) -> list:
    banner = fitted_image(report["banner"], 166, 58)
    banner.hAlign = "CENTER"
    details = Table(
        [
            [paragraph("AUTOR", "small"), paragraph("Wiktor Złotnik", "small")],
            [paragraph("PRZEDMIOT", "small"), paragraph("Metrologia i systemy pomiarowe", "small")],
            [paragraph("CHARAKTER DANYCH", "small"), paragraph("Symulacja dydaktyczna - przykład obliczeniowy", "small")],
            [paragraph("OPRACOWANIE", "small"), paragraph("Nowa redakcja i układ graficzny, wrzesień 2026", "small")],
        ],
        colWidths=[43 * mm, 123 * mm],
    )
    details.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), NAVY),
                ("TEXTCOLOR", (0, 0), (0, -1), WHITE),
                ("BACKGROUND", (1, 0), (1, -1), ICE),
                ("GRID", (0, 0), (-1, -1), 0.5, GRID),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3.5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    return [
        Spacer(1, 5 * mm),
        banner,
        Spacer(1, 14 * mm),
        paragraph("SPRAWOZDANIE Z ĆWICZENIA LABORATORYJNEGO", "cover_kicker"),
        paragraph(report["title"], "cover_title"),
        paragraph(report["subtitle"], "cover_subtitle"),
        callout(
            "WERSJA SYMULACYJNA",
            "Wartości w tabelach zostały przygotowane wyłącznie jako spójny przykład obliczeniowy. Nie są zapisem rzeczywiście przeprowadzonej serii pomiarowej i nie powinny być tak przedstawiane.",
            warning=True,
        ),
        Spacer(1, 10 * mm),
        details,
        PageBreak(),
    ]


def raw_table(columns: dict[str, list[float]], digits: int, first_col: str = "Lp.") -> Table:
    labels = list(columns)
    rows = [[first_col] + labels]
    n = len(next(iter(columns.values())))
    for idx in range(n):
        rows.append([str(idx + 1)] + [pl(columns[label][idx], digits) for label in labels])
    widths = [10 * mm] + [(164 / len(labels)) * mm for _ in labels]
    table = Table(rows, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.1 if len(labels) <= 8 else 6.4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2 * mm),
    ]
    for row in range(1, len(rows)):
        if row % 2 == 0:
            style.append(("BACKGROUND", (0, row), (-1, row), ICE))
    table.setStyle(TableStyle(style))
    return table


def summary_table(columns: dict[str, list[float]], mean_digits: int, uncertainty_digits: int = 5) -> Table:
    rows = [["Wymiar", "n", "Średnia [mm]", "uA [mm]", "U95 [mm]", "Przedział 95% [mm]"]]
    for label, values in columns.items():
        result = stats(values)
        rows.append(
            [
                label,
                str(result["n"]),
                pl(result["mean"], mean_digits),
                pl(result["u"], uncertainty_digits),
                pl(result["U"], uncertainty_digits),
                f'{pl(result["lo"], uncertainty_digits)} - {pl(result["hi"], uncertainty_digits)}',
            ]
        )
    table = Table(rows, colWidths=[16 * mm, 11 * mm, 27 * mm, 25 * mm, 25 * mm, 66 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.2),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.45, GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ICE]),
                ("TOPPADDING", (0, 0), (-1, -1), 2.3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3 * mm),
            ]
        )
    )
    return table


def formula_block(values: list[float], label: str, value_digits: int, title: str | None = None) -> list:
    result = stats(values)
    summed = " + ".join(pl(value, value_digits) for value in values)
    shown_title = title or f"Przykład obliczeń - seria {label}"
    return [
        paragraph(shown_title, "h3"),
        paragraph(
            f'<b>1. Średnia:</b> x̄ = ({summed}) / {result["n"]} = <b>{pl(result["mean"], value_digits + 2)} mm</b>',
            "formula",
        ),
        paragraph(
            f'<b>2. Suma kwadratów odchyleń:</b> Σ(x<sub>i</sub> - x̄)<super>2</super> = {pl(result["ss"], 7)} mm<super>2</super>',
            "formula",
        ),
        paragraph(
            f'<b>3. Niepewność standardowa średniej:</b> u<sub>A</sub> = √[{pl(result["ss"], 7)} / ({result["n"]} · {result["n"] - 1})] = <b>{pl(result["u"], 6)} mm</b>',
            "formula",
        ),
        paragraph(
            f'<b>4. Niepewność rozszerzona:</b> U<sub>95</sub> = 2,2622 · {pl(result["u"], 6)} = <b>{pl(result["U"], 6)} mm</b>',
            "formula",
        ),
        paragraph(
            f'<b>5. Zapis wyniku:</b> N = ({pl(result["mean"], value_digits + 2)} ± {pl(result["U"], 6)}) mm; przedział: {pl(result["lo"], 6)} mm &lt; N &lt; {pl(result["hi"], 6)} mm.',
            "formula",
        ),
    ]


def methods_intro(include_callout: bool = True) -> list:
    items = [
        paragraph("Model statystyczny", "h3"),
        paragraph(
            "Dla każdej serii przyjęto n = 10 odczytów. Wartość średnią wyznaczono jako x̄ = Σx<sub>i</sub>/n. Statystyczną niepewność standardową średniej obliczono ze wzoru u<sub>A</sub> = √[Σ(x<sub>i</sub> - x̄)<super>2</super>/(n(n - 1))]. Dla poziomu ufności 95% i dziewięciu stopni swobody zastosowano współczynnik t-Studenta k = 2,2622, a następnie U<sub>95</sub> = k · u<sub>A</sub>.",
        ),
    ]
    if include_callout:
        items += [
            callout(
                "Zakres interpretacji",
                "Obliczenia opisują wyłącznie rozrzut symulowanej serii (typ A). Pełna ocena wyniku rzeczywistego powinna dodatkowo uwzględniać rozdzielczość, wzorcowanie i inne składniki niepewności typu B.",
            ),
            Spacer(1, 3 * mm),
        ]
    return items


def bullet_items(items: list[str]) -> list:
    result = []
    for idx, item in enumerate(items, 1):
        result.append(
            Paragraph(
                f'<font name="Arial-Bold" color="{TEAL.hexval()}">{idx:02d}</font>&nbsp;&nbsp;{item}',
                ParagraphStyle(
                    f"Bullet{idx}",
                    parent=STYLES["body"],
                    leftIndent=3 * mm,
                    firstLineIndent=0,
                    spaceAfter=2.5 * mm,
                    alignment=TA_LEFT,
                ),
            )
        )
    return result


def literature(items: list[str]) -> list:
    result = []
    for idx, item in enumerate(items, 1):
        result.append(paragraph(f"{idx}. {item}", "small"))
        result.append(Spacer(1, 1.2 * mm))
    return result


def page_callbacks(short_title: str):
    width, height = A4

    def first_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 15 * mm, width, 15 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, 0, width, 8 * mm, fill=1, stroke=0)
        canvas.restoreState()

    def later_pages(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 14 * mm, width, 14 * mm, fill=1, stroke=0)
        canvas.setFont("Arial-Bold", 8)
        canvas.setFillColor(WHITE)
        canvas.drawString(18 * mm, height - 9 * mm, short_title)
        canvas.setFillColor(RED)
        canvas.roundRect(width - 65 * mm, height - 11 * mm, 47 * mm, 6 * mm, 2 * mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Arial-Bold", 6.8)
        canvas.drawCentredString(width - 41.5 * mm, height - 8.9 * mm, "DANE SYMULOWANE")
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont("Arial", 6.8)
        canvas.drawString(18 * mm, 8.5 * mm, "Przykład dydaktyczny - wartości nie są zapisem rzeczywistych pomiarów")
        canvas.drawRightString(width - 18 * mm, 8.5 * mm, f"strona {doc.page}")
        canvas.restoreState()

    return first_page, later_pages


def build_pdf(path: Path, report: dict, story: list) -> None:
    first, later = page_callbacks(report["short"])
    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=21 * mm,
        bottomMargin=18 * mm,
        title=report["title"],
        author="Wiktor Złotnik",
        subject="Przeredagowane sprawozdanie z oznaczonymi danymi symulowanymi",
    )
    document.build(cover_story(report) + story, onFirstPage=first, onLaterPages=later)


DIAL_DATA = {
    "A": [70.43, 70.44, 70.42, 70.40, 70.43, 70.41, 70.40, 70.42, 70.41, 70.44],
    "B": [51.10, 51.12, 51.11, 51.09, 51.11, 51.10, 51.10, 51.12, 51.11, 51.13],
}

MIC_DATA = {
    "A": [16.15, 16.16, 16.15, 16.14, 16.17, 16.15, 16.14, 16.15, 16.16, 16.15],
    "B": [23.26, 23.25, 23.27, 23.26, 23.26, 23.24, 23.27, 23.26, 23.25, 23.26],
    "C": [37.30, 37.31, 37.29, 37.30, 37.32, 37.30, 37.29, 37.30, 37.31, 37.30],
    "D": [28.40, 28.41, 28.40, 28.39, 28.40, 28.42, 28.39, 28.40, 28.41, 28.40],
    "E": [12.00, 12.01, 11.99, 12.00, 12.01, 12.00, 11.98, 12.01, 12.00, 11.99],
    "F": [106.63, 106.64, 106.62, 106.63, 106.64, 106.63, 106.61, 106.63, 106.64, 106.63],
    "G": [45.13, 45.14, 45.12, 45.13, 45.15, 45.13, 45.12, 45.13, 45.14, 45.13],
    "H": [45.35, 45.36, 45.35, 45.34, 45.35, 45.37, 45.34, 45.35, 45.36, 45.35],
}

CALIPER_01 = {
    "A": [20.0, 19.9, 20.1, 20.0, 20.1, 19.9, 20.1, 20.0, 20.0, 20.1],
    "B": [39.9, 40.0, 40.0, 39.9, 40.1, 40.0, 39.9, 40.1, 39.9, 40.0],
    "C": [54.9, 55.1, 55.0, 55.0, 55.1, 54.9, 55.0, 54.9, 55.1, 55.0],
    "D": [80.0, 80.0, 80.1, 80.1, 79.9, 80.1, 79.9, 80.1, 79.9, 80.0],
    "E": [100.0, 100.0, 99.9, 99.9, 100.1, 99.9, 100.1, 99.9, 100.1, 100.0],
    "F": [15.1, 14.9, 15.1, 15.1, 14.9, 15.1, 15.0, 14.9, 15.0, 15.1],
    "G": [17.9, 18.1, 17.9, 18.1, 18.0, 18.0, 17.9, 18.1, 18.0, 18.1],
    "H": [25.1, 24.9, 25.1, 24.9, 25.1, 25.0, 25.1, 24.9, 25.1, 25.0],
    "I": [32.9, 33.1, 32.9, 33.1, 32.9, 32.9, 33.0, 33.1, 32.9, 33.1],
    "J": [45.1, 44.9, 45.1, 44.9, 45.1, 45.0, 44.9, 45.1, 45.0, 44.9],
    "K": [53.9, 54.1, 53.9, 53.9, 54.1, 53.9, 54.1, 54.1, 53.9, 54.0],
}

CALIPER_005 = {
    "A": [20.00, 20.00, 20.05, 19.95, 20.05, 20.05, 20.00, 20.05, 19.95, 20.00],
    "B": [40.00, 40.00, 40.05, 40.05, 40.00, 39.95, 40.00, 40.00, 40.05, 40.00],
    "C": [55.00, 55.05, 55.00, 55.05, 55.00, 55.00, 54.95, 55.00, 55.05, 55.00],
    "D": [80.00, 80.05, 80.00, 80.05, 80.05, 80.00, 80.05, 80.00, 80.05, 80.00],
    "E": [100.00, 100.00, 100.00, 100.05, 100.05, 100.05, 100.00, 100.00, 100.05, 100.00],
    "F": [15.05, 15.00, 15.05, 15.00, 15.00, 15.05, 15.00, 15.00, 15.05, 15.00],
    "G": [18.00, 18.05, 18.00, 18.00, 18.00, 18.05, 18.00, 18.05, 18.00, 18.00],
    "H": [25.00, 25.00, 25.05, 25.00, 25.05, 25.00, 25.00, 25.00, 25.00, 25.05],
    "I": [33.05, 33.05, 33.00, 33.05, 33.00, 33.05, 33.00, 33.00, 33.00, 33.00],
    "J": [45.00, 45.05, 45.00, 45.05, 45.00, 45.00, 45.00, 45.05, 45.00, 45.00],
    "K": [54.00, 54.05, 54.05, 54.00, 54.00, 54.05, 54.00, 54.05, 54.00, 54.00],
}

CALIPER_002 = {
    "A": [20.02, 19.98, 20.04, 19.98, 20.02, 20.02, 20.00, 20.04, 19.98, 20.02],
    "B": [39.98, 40.02, 40.02, 40.04, 39.98, 39.96, 39.98, 40.02, 40.04, 39.98],
    "C": [55.02, 55.04, 54.98, 55.02, 55.02, 54.98, 54.96, 54.98, 55.04, 54.98],
    "D": [79.98, 80.06, 80.02, 80.04, 80.06, 80.02, 80.06, 79.98, 80.04, 80.02],
    "E": [100.02, 99.98, 99.98, 100.04, 100.02, 100.04, 99.98, 100.02, 100.04, 99.98],
    "F": [15.02, 15.02, 15.04, 15.02, 14.98, 15.04, 15.02, 15.02, 15.04, 15.02],
    "G": [18.02, 18.04, 17.98, 18.02, 18.02, 18.06, 17.98, 18.04, 17.98, 18.02],
    "H": [24.98, 24.98, 25.04, 24.98, 25.00, 25.02, 25.02, 25.04, 25.02, 24.98],
    "I": [33.06, 33.04, 32.98, 33.04, 32.98, 33.04, 33.02, 33.02, 32.98, 33.02],
    "J": [44.98, 45.04, 45.02, 45.04, 44.98, 45.02, 45.02, 45.04, 45.02, 44.98],
    "K": [54.02, 54.08, 54.04, 53.98, 54.02, 54.06, 53.98, 54.04, 53.98, 54.02],
}


def dial_report() -> tuple[dict, list]:
    report = {
        "title": "Pomiary długości czujnikiem zegarowym",
        "subtitle": "Metoda porównawcza, opracowanie statystyczne i przykład wyznaczania przedziału ufności",
        "short": "Czujnik zegarowy - sprawozdanie",
        "banner": ASSETS / "doc1_p1_img1.png",
    }
    story = []
    story += section("Cel i zakres ćwiczenia", "1")
    story += [
        paragraph(
            "Ćwiczenie służy poznaniu konstrukcji czujnika zegarowego, zasad jego mocowania oraz sposobu prowadzenia pomiarów porównawczych. Zakres obejmuje przygotowanie stanowiska, wyzerowanie wskazania względem elementu odniesienia, odczyt niewielkich różnic wymiaru oraz statystyczne opracowanie serii wyników.",
        ),
        paragraph(
            "Pomiar jest porównaniem badanej wielkości z przyjętą jednostką lub wzorcem. Sam odczyt nie opisuje w pełni rezultatu - należy również określić jego rozrzut i zakres, w którym z przyjętym prawdopodobieństwem znajduje się wartość oczekiwana. W tym opracowaniu wykorzystano średnią z serii, niepewność standardową średniej i przedział ufności oparty na rozkładzie t-Studenta.",
        ),
    ]
    story += section("Budowa i zasada działania", "2")
    story += [
        paragraph(
            "Ruch trzpienia pomiarowego jest przenoszony przez przekładnię zębatą na wskazówkę obracającą się nad tarczą. W typowym przyrządzie jedna działka odpowiada 0,01 mm, a dodatkowy licznik rejestruje pełne obroty wskazówki. Czujnik nie wyznacza zwykle całego wymiaru bezpośrednio; pokazuje różnicę pomiędzy położeniem ustawionym przy zerowaniu a położeniem badanej powierzchni.",
        ),
    ]
    story += figure(ASSETS / "doc1_p3_img1.png", "Rys. 1. Podstawowe elementy analogowego czujnika zegarowego - grafika zachowana z materiału źródłowego.", 105, 84)
    story += [
        paragraph(
            "Wiarygodny odczyt wymaga sztywnego statywu, prostopadłego ustawienia trzpienia i niewielkiego nacisku wstępnego. Powierzchnie styku powinny być czyste, a stanowisko odizolowane od drgań. Wskazanie odczytuje się przy niezmienionym kierunku najazdu, co ogranicza wpływ luzów mechanizmu.",
        )
    ]
    story += section("Przebieg pomiaru", "3")
    story += bullet_items(
        [
            "Oczyszczono płytę, element odniesienia, badany detal oraz końcówkę trzpienia.",
            "Czujnik zamocowano w statywie i ustawiono trzpień prostopadle do mierzonej powierzchni.",
            "Po nadaniu nacisku wstępnego obrócono pierścień tarczy do położenia zerowego.",
            "Dla wymiarów A i B wykonano po dziesięć odczytów, za każdym razem powtarzając dojście do punktu pomiarowego.",
            "Serie opracowano statystycznie zgodnie z modelem przedstawionym w dalszej części.",
        ]
    )
    story += figure(ASSETS / "doc1_p5_img1.png", "Rys. 2. Schemat badanego elementu i oznaczenie wymiarów A oraz B - grafika zachowana z materiału źródłowego.", 138, 65)
    story += section("Dane symulowane", "4")
    story += [
        callout(
            "WAŻNE",
            "Poniższa tabela stanowi wariant dydaktyczny. Wartości zmieniono o pojedyncze działki elementarne, zachowując rozdzielczość 0,01 mm i zbliżony poziom rozrzutu.",
            warning=True,
        ),
        Spacer(1, 4 * mm),
        raw_table(DIAL_DATA, 2),
        Spacer(1, 5 * mm),
    ]
    story += methods_intro()
    story += formula_block(DIAL_DATA["A"], "A", 2)
    story += [
        Spacer(1, 3 * mm),
        KeepTogether([paragraph("Zestawienie wyników", "h3"), summary_table(DIAL_DATA, 3)]),
    ]
    story += section("Wnioski", "5")
    story += [
        paragraph(
            "Symulowane serie A i B charakteryzują się niewielkim rozrzutem, odpowiadającym pojedynczym działkom czujnika. Otrzymane przedziały ufności są wąskie względem mierzonych wymiarów, co ilustruje dużą czułość metody porównawczej. Nie oznacza to jednak, że rzeczywisty pomiar ma taką samą dokładność - należy jeszcze uwzględnić wzorcowanie, rozdzielczość, błąd ustawienia oraz stabilność stanowiska.",
        ),
        paragraph(
            "Największe znaczenie praktyczne mają: prostopadłość osi trzpienia do powierzchni, stały kierunek dojścia, prawidłowe zerowanie oraz czystość stykających się elementów. Nawet bardzo precyzyjny czujnik nie skompensuje błędów wynikających z niestabilnego mocowania lub niewłaściwej techniki operatora.",
        ),
    ]
    story += section("Literatura i materiały", "6")
    story += literature(
        [
            "PN-71/N-02050, Metrologia - nazwy i określenia.",
            "Do czego służy czujnik zegarowy i jak go odczytać, dowarsztatu.com, dostęp 25.06.2026.",
            "Instrukcja użytkowania czujników zegarowych, e-darmet.pl, dostęp 25.06.2026.",
            "Budowa czujnika zegarowego, blog-cnc.pl - źródło grafiki przyrządu.",
            "Autorskie notatki z ćwiczenia laboratoryjnego.",
        ]
    )
    return report, story


def micrometer_report() -> tuple[dict, list]:
    report = {
        "title": "Pomiary mikrometrem zewnętrznym",
        "subtitle": "Śruba mikrometryczna, technika odczytu oraz statystyczna analiza serii wyników",
        "short": "Mikrometr zewnętrzny - sprawozdanie",
        "banner": ASSETS / "doc3_p1_img1.png",
    }
    story = []
    story += section("Cel ćwiczenia", "1")
    story += [
        paragraph(
            "Celem ćwiczenia jest opanowanie prawidłowej obsługi mikrometru zewnętrznego oraz wykonanie powtarzalnych pomiarów długości z rozdzielczością 0,01 mm. Opracowanie obejmuje identyfikację elementów przyrządu, kontrolę położenia zerowego, poprawne użycie sprzęgiełka i analizę niepewności wyznaczonej z serii odczytów.",
        )
    ]
    story += section("Podstawy działania przyrządu", "2")
    story += [
        paragraph(
            "Mikrometr wykorzystuje precyzyjną parę śrubową. Obrót bębna powoduje osiowe przesunięcie wrzeciona, a wartość wymiaru odczytuje się jako sumę wskazania na tulei i części wynikającej z położenia podziałki bębna. Dla typowego skoku śruby 0,5 mm i pięćdziesięciu działek jeden odstęp podziałki odpowiada 0,01 mm.",
        ),
    ]
    story += figure(ASSETS / "doc3_p3_img1.png", "Rys. 1. Mikrometr zewnętrzny - fotografia zachowana z materiału źródłowego.", 135, 70)
    story += [
        paragraph(
            "Sprzęgiełko ogranicza siłę docisku, dlatego końcowe zbliżanie powierzchni pomiarowych powinno odbywać się wyłącznie z jego użyciem. Nadmierny nacisk może odkształcić kabłąk lub detal. Na wynik wpływają również zabrudzenia, temperatura przyrządu i przedmiotu, nieosiowe ustawienie oraz błąd odczytu skali.",
        )
    ]
    story += section("Przygotowanie i przebieg", "3")
    story += bullet_items(
        [
            "Skontrolowano czystość kowadełka i wrzeciona oraz sprawdzono wskazanie zerowe.",
            "Mierzony detal ustawiono pomiędzy powierzchniami pomiarowymi bez przekoszenia.",
            "Wrzeciono dosuwano sprzęgiełkiem do uzyskania powtarzalnego, lekkiego docisku.",
            "Dla ośmiu wymiarów A-H wykonano po dziesięć odczytów.",
            "Po każdej serii obliczono średnią, niepewność standardową średniej i przedział ufności 95%.",
        ]
    )
    story += figure(ASSETS / "doc3_p4_img1.png", "Rys. 2. Schemat badanego detalu i oznaczenia wymiarów A-H - grafika zachowana z materiału źródłowego.", 112, 68)
    story += section("Dane symulowane", "4")
    story += [
        callout(
            "WAŻNE",
            "Tabela jest przykładem dydaktycznym. Odczyty zmodyfikowano o niewielkie wartości rzędu 0,01 mm, a każdą serię zachowano w zakresie typowym dla przyjętej rozdzielczości.",
            warning=True,
        ),
        Spacer(1, 4 * mm),
        raw_table(MIC_DATA, 2),
        Spacer(1, 5 * mm),
    ]
    story += methods_intro(include_callout=False)
    story.append(KeepTogether(formula_block(MIC_DATA["A"], "A", 2)))
    story += section("Zestawienie obliczeń", "5")
    story += [
        paragraph(
            "Dla wszystkich wymiarów zastosowano identyczny tok obliczeń. Tabela podaje wartości średnie, niepewności standardowe średniej, niepewności rozszerzone oraz granice przedziałów ufności.",
        ),
        summary_table(MIC_DATA, 3),
    ]
    story += section("Wnioski", "6")
    story += [
        paragraph(
            "Przykładowe serie pokazują wysoką powtarzalność pomiarów mikrometrem: zmiany mieszczą się na ogół w zakresie kilku setnych milimetra, a przedziały ufności średnich pozostają wąskie. Jest to zgodne z charakterem przyrządu przeznaczonego do precyzyjnego wyznaczania wymiarów zewnętrznych.",
        ),
        paragraph(
            "Ostateczna jakość rzeczywistego wyniku zależy jednak od warunków termicznych, stanu powierzchni pomiarowych, kontroli zera, ustawienia detalu i sposobu użycia sprzęgiełka. Pełny budżet niepewności powinien łączyć analizę rozrzutu z informacją o rozdzielczości i wzorcowaniu przyrządu.",
        ),
    ]
    story += section("Literatura i materiały", "7")
    story += literature(
        [
            "PN-71/N-02050, Metrologia - nazwy i określenia.",
            "Materiały dydaktyczne Uniwersytetu Jagiellońskiego i Politechniki Warszawskiej dotyczące śruby mikrometrycznej oraz narzędzi pomiarowych.",
            "Katalog przyrządów LIMIT - źródło fotografii wykorzystanej w materiale bazowym; autorskie notatki z laboratorium.",
        ]
    )
    return report, story


def caliper_report() -> tuple[dict, list]:
    report = {
        "title": "Pomiary suwmiarką analogową",
        "subtitle": "Porównanie serii wykonanych przy rozdzielczości 0,10 mm, 0,05 mm i 0,02 mm",
        "short": "Suwmiarka analogowa - sprawozdanie",
        "banner": ASSETS / "doc2_p1_img1.png",
    }
    story = []
    story += section("Cel i zakres ćwiczenia", "1")
    story += [
        paragraph(
            "Ćwiczenie obejmuje posługiwanie się suwmiarką analogową podczas pomiaru wymiarów zewnętrznych, wewnętrznych i głębokości. Celem jest również porównanie wyników uzyskiwanych przy trzech rozdzielczościach noniusza oraz prześledzenie wpływu rozdzielczości i powtarzalności odczytu na statystyczną niepewność średniej.",
        )
    ]
    story += section("Budowa i sposób odczytu", "2")
    story += [
        paragraph(
            "Suwmiarka składa się z prowadnicy ze skalą główną, suwaka z noniuszem, szczęk pomiarowych i głębokościomierza. Pełne milimetry odczytuje się na skali głównej przed zerem noniusza. Część ułamkową wyznacza kreska noniusza pokrywająca się z kreską skali głównej. Rozdzielczość wynika z konstrukcji podziałek i w badanym wariancie wynosi 0,10 mm, 0,05 mm albo 0,02 mm.",
        ),
        paragraph(
            "Podczas pomiaru szczęki powinny przylegać do powierzchni bez nadmiernego nacisku. Przy pomiarze wymiaru zewnętrznego należy zachować prostopadłość do osi detalu, a przy pomiarze wewnętrznym prawidłowo ustawić szczęki w największym przekroju. Odczyt prowadzi się prostopadle do skali, aby ograniczyć paralaksę.",
        ),
    ]
    story += figure(ASSETS / "doc2_p3_img1.png", "Rys. 1. Badany element schodkowy i oznaczenia wymiarów A-K - grafika zachowana z materiału źródłowego.", 150, 72)
    story += section("Przebieg pomiaru", "3")
    story += bullet_items(
        [
            "Oczyszczono powierzchnie detalu, szczęki oraz prowadnicę przyrządu.",
            "Sprawdzono zbieżność kresek zerowych przy zamkniętych szczękach.",
            "Dla wymiarów A-K wykonano po dziesięć odczytów trzema suwmiarkami.",
            "Wartości zapisywano zgodnie z działką elementarną danego noniusza.",
            "Dla każdej kolumny wyznaczono średnią i statystyczny przedział ufności 95%.",
        ]
    )
    story.append(PageBreak())
    story += section("Serie symulowane - suwmiarka 0,10 mm", "4")
    story += [
        callout(
            "DANE SYMULOWANE",
            "Odczyty są przykładem obliczeniowym. Zachowano krok 0,10 mm i nominalne wymiary detalu.",
            warning=True,
        ),
        Spacer(1, 4 * mm),
        raw_table(CALIPER_01, 1),
        Spacer(1, 5 * mm),
        summary_table(CALIPER_01, 3),
    ]
    story.append(PageBreak())
    story += section("Serie symulowane - suwmiarka 0,05 mm", "5")
    story += [
        callout(
            "DANE SYMULOWANE",
            "Wartości zapisano z krokiem 0,05 mm. Rozrzut został zmniejszony względem serii dla 0,10 mm.",
            warning=True,
        ),
        Spacer(1, 4 * mm),
        raw_table(CALIPER_005, 2),
        Spacer(1, 5 * mm),
        summary_table(CALIPER_005, 3),
    ]
    story.append(PageBreak())
    story += section("Serie symulowane - suwmiarka 0,02 mm", "6")
    story += [
        callout(
            "DANE SYMULOWANE",
            "Każdy odczyt jest zgodny z działką 0,02 mm. Dane zachowują niewielki, realistyczny rozrzut wokół wymiarów nominalnych.",
            warning=True,
        ),
        Spacer(1, 4 * mm),
        raw_table(CALIPER_002, 2),
        Spacer(1, 5 * mm),
        summary_table(CALIPER_002, 3),
    ]
    story.append(PageBreak())
    story += section("Model obliczeń i przykład", "7")
    story += methods_intro()
    story += formula_block(
        CALIPER_002["A"],
        "A",
        2,
        title="Pełny przykład - wymiar A, suwmiarka 0,02 mm",
    )
    comparison_rows = [["Rozdzielczość", "Średnie U95 dla A-K [mm]", "Największe U95 [mm]"]]
    for label, dataset in [("0,10 mm", CALIPER_01), ("0,05 mm", CALIPER_005), ("0,02 mm", CALIPER_002)]:
        uncertainties = [stats(values)["U"] for values in dataset.values()]
        comparison_rows.append([label, pl(mean(uncertainties), 5), pl(max(uncertainties), 5)])
    comparison = Table(comparison_rows, colWidths=[45 * mm, 67 * mm, 58 * mm])
    comparison.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ICE]),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )
    story += [Spacer(1, 4 * mm), paragraph("Porównanie wariantów", "h3"), comparison]
    story += section("Wnioski", "8")
    story += [
        paragraph(
            "W symulacji zmniejszenie działki elementarnej wiąże się ze spadkiem przeciętnej niepewności wyznaczonej z rozrzutu serii. Najbardziej skupione wyniki uzyskano dla wariantu 0,02 mm, natomiast suwmiarka 0,10 mm daje najszersze przedziały. Jest to efekt przyjętego modelu danych i nie stanowi porównania konkretnych egzemplarzy przyrządów.",
        ),
        paragraph(
            "W praktyce rozdzielczość jest tylko jednym ze składników jakości pomiaru. Równie ważne pozostają stan szczęk, błąd zera, kierunek docisku, ustawienie detalu, paralaksa i doświadczenie operatora. Zerowy lub bardzo mały rozrzut serii nie dowodzi idealnej dokładności, ponieważ nie obejmuje niepewności typu B.",
        ),
    ]
    story += section("Literatura i materiały", "9")
    story += literature(
        [
            "PN-71/N-02050, Metrologia - nazwy i określenia.",
            "Materiały dydaktyczne do ćwiczeń z pomiarów suwmiarką analogową.",
            "Materiały własne: schemat badanego elementu i notatki z laboratorium.",
        ]
    )
    return report, story


def main() -> None:
    jobs = [
        (OUTPUT / "czujnik_zegarowy_wersja_symulacyjna.pdf", dial_report()),
        (OUTPUT / "suwmiarka_wersja_symulacyjna.pdf", caliper_report()),
        (OUTPUT / "sruba_mikrometryczna_wersja_symulacyjna.pdf", micrometer_report()),
    ]
    for path, (report, story) in jobs:
        build_pdf(path, report, story)
        print(path)


if __name__ == "__main__":
    main()
