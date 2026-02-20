from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4, landscape  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "api-reference.md"
OUTPUT = ROOT / "docs" / "api-reference-table.pdf"

ENDPOINT_HEADER_RE = re.compile(r"^###\s+(GET|POST|PUT|DELETE|PATCH)\s+`([^`]+)`")
PATH_PARAM_RE = re.compile(r"\{([^}]+)\}")

DEFAULT_BASE_URL = "http://192.168.10.9:8000"
DEFAULT_AUTH_TOKEN = "launch-smoke:admin,ops"
DEFAULT_IDEMPOTENCY_KEY = "demo-key-12345678"


def _clean_inline_code(value: str) -> str:
    return value.replace("`", "").strip()


def _collect_bullet_block(lines: list[str], start: int) -> tuple[list[str], int]:
    items: list[str] = []
    idx = start
    while idx < len(lines):
        current = lines[idx].rstrip()
        if not current:
            idx += 1
            continue
        if current.startswith("### "):
            break
        if current.startswith("## "):
            break
        if current.startswith("- "):
            break
        if current.startswith("  - "):
            items.append(_clean_inline_code(current[4:]))
            idx += 1
            continue
        break
    return items, idx


def _command_endpoint(endpoint: str) -> str:
    normalized = PATH_PARAM_RE.sub(lambda m: f"<{m.group(1)}>", endpoint)
    normalized = normalized.replace("...", "<value>")
    return normalized


def _build_curl_syntax(
    method: str,
    endpoint: str,
    auth: str,
    inputs: str,
) -> str:
    url = f"{DEFAULT_BASE_URL}{_command_endpoint(endpoint)}"
    parts: list[str] = ["curl"]

    if method != "GET":
        parts.extend(["-X", method])

    auth_required = auth.lower().startswith("required")
    if auth_required:
        parts.extend(["-H", f'"Authorization: Bearer {DEFAULT_AUTH_TOKEN}"'])

    if "Idempotency-Key" in inputs:
        parts.extend(["-H", f'"Idempotency-Key: {DEFAULT_IDEMPOTENCY_KEY}"'])

    if method in {"POST", "PUT", "PATCH"}:
        parts.extend(["-H", '"Content-Type: application/json"'])
        parts.extend(["-d", '"<JSON_BODY>"'])

    parts.append(f'"{url}"')
    return " ".join(parts)


def parse_api_reference(markdown: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    rows: list[dict[str, str]] = []
    idx = 0
    while idx < len(lines):
        header = lines[idx].strip()
        match = ENDPOINT_HEADER_RE.match(header)
        if not match:
            idx += 1
            continue

        method = match.group(1)
        endpoint = match.group(2)
        row = {
            "method": method,
            "endpoint": endpoint,
            "auth": "-",
            "purpose": "-",
            "inputs": "-",
            "response_rules": "-",
            "syntax": "-",
        }
        idx += 1

        inputs: list[str] = []
        response_rules: list[str] = []
        while idx < len(lines):
            line = lines[idx].rstrip()
            stripped = line.strip()
            if stripped.startswith("### "):
                break
            if stripped.startswith("## "):
                break

            if stripped.startswith("- What it does:"):
                row["purpose"] = _clean_inline_code(stripped.replace("- What it does:", "", 1))
                idx += 1
                continue
            if stripped.startswith("- Auth:"):
                row["auth"] = _clean_inline_code(stripped.replace("- Auth:", "", 1))
                idx += 1
                continue
            if stripped.startswith("- Input:"):
                headline = _clean_inline_code(stripped.replace("- Input:", "", 1))
                if headline:
                    inputs.append(headline)
                block, idx = _collect_bullet_block(lines, idx + 1)
                inputs.extend(block)
                continue
            if stripped.startswith("- Required header:"):
                inputs.append(_clean_inline_code(stripped.replace("- Required header:", "", 1)))
                idx += 1
                continue
            if stripped.startswith("- Response:"):
                response_rules.append(_clean_inline_code(stripped.replace("- Response:", "", 1)))
                idx += 1
                continue
            if stripped.startswith("- Important behavior:"):
                block, idx = _collect_bullet_block(lines, idx + 1)
                response_rules.extend(block)
                continue
            if stripped.startswith("- Errors:"):
                response_rules.append(_clean_inline_code(stripped.replace("- Errors:", "", 1)))
                idx += 1
                continue

            idx += 1

        if inputs:
            row["inputs"] = "; ".join(inputs)
        if response_rules:
            row["response_rules"] = "; ".join(response_rules)

        row["syntax"] = _build_curl_syntax(
            method=row["method"],
            endpoint=row["endpoint"],
            auth=row["auth"],
            inputs=row["inputs"],
        )
        rows.append(row)

    return rows


def build_pdf(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        leftMargin=16,
        rightMargin=16,
        topMargin=16,
        bottomMargin=16,
        title="MT-Facturation API Reference Table",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#0C2D48"),
        spaceAfter=8,
    )
    cell_style = ParagraphStyle(
        "Cell",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=6.4,
        leading=8,
        textColor=colors.HexColor("#1C2E3E"),
    )
    header_style = ParagraphStyle(
        "HeaderCell",
        parent=cell_style,
        fontName="Helvetica-Bold",
        fontSize=7,
        textColor=colors.white,
    )

    elements = [
        Paragraph("MT-Facturation API Reference (Table + Command Syntax)", title_style),
        Paragraph(f"Source: {SOURCE.name}", cell_style),
        Paragraph(f"Base URL used in syntax column: {DEFAULT_BASE_URL}", cell_style),
        Paragraph(f"Default bearer token used in syntax column: {DEFAULT_AUTH_TOKEN}", cell_style),
        Spacer(1, 8),
    ]

    table_data = [
        [
            Paragraph("Method", header_style),
            Paragraph("Endpoint", header_style),
            Paragraph("Auth", header_style),
            Paragraph("Cmd Syntax (curl)", header_style),
            Paragraph("Purpose", header_style),
            Paragraph("Inputs", header_style),
            Paragraph("Response / Rules", header_style),
        ]
    ]

    for row in rows:
        table_data.append(
            [
                Paragraph(row["method"], cell_style),
                Paragraph(row["endpoint"], cell_style),
                Paragraph(row["auth"], cell_style),
                Paragraph(row["syntax"], cell_style),
                Paragraph(row["purpose"], cell_style),
                Paragraph(row["inputs"], cell_style),
                Paragraph(row["response_rules"], cell_style),
            ],
        )

    # Fits A4 landscape content width (842 - 32 margins = 810 points).
    col_widths = [40, 160, 52, 250, 120, 90, 98]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D5C63")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AFC4D1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F8FA")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ],
        ),
    )

    elements.append(table)
    doc.build(elements)


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    rows = parse_api_reference(markdown)
    if not rows:
        raise RuntimeError("No endpoint rows parsed from api-reference.md")
    build_pdf(rows, OUTPUT)
    print(f"Wrote {OUTPUT}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
