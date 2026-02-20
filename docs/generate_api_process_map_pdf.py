from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]
from reportlab.lib.units import mm  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "api-process-map.md"
OUTPUT = ROOT / "docs" / "api-process-map.pdf"

DEFAULT_BASE_URL = "http://192.168.10.9:8000"
DEFAULT_AUTH_TOKEN = "launch-smoke:admin,ops"
DEFAULT_IDEMPOTENCY_KEY = "demo-key-12345678"

METHOD_ENDPOINT_RE = re.compile(r"(GET|POST|PUT|DELETE|PATCH)\s+(/api/v1/[A-Za-z0-9_./{}?=&-]+)")
PATH_PARAM_RE = re.compile(r"\{([^}]+)\}")
IDEMPOTENT_PATHS = {
    "/api/v1/landing/submit/new",
    "/api/v1/landing/submit/plan-change",
    "/api/v1/billing/runs",
    "/api/v1/collections/payments",
    "/api/v1/collections/invoices/{invoice_id}/approve-paid",
}


def extract_endpoint(text: str) -> tuple[str, str] | None:
    normalized = text.replace("`", "")
    match = METHOD_ENDPOINT_RE.search(normalized)
    if not match:
        return None
    method = match.group(1)
    endpoint = match.group(2).rstrip(").,;")
    return method, endpoint


def endpoint_to_command_path(endpoint: str) -> str:
    normalized = PATH_PARAM_RE.sub(lambda m: f"<{m.group(1)}>", endpoint)
    return normalized.replace("...", "<value>")


def is_public_endpoint(endpoint: str) -> bool:
    return endpoint == "/api/v1/health" or endpoint.startswith("/api/v1/landing/")


def needs_idempotency(endpoint: str) -> bool:
    return endpoint.split("?", 1)[0] in IDEMPOTENT_PATHS


def build_curl_command(method: str, endpoint: str) -> str:
    command_parts: list[str] = ["curl"]
    if method != "GET":
        command_parts.extend(["-X", method])
    if not is_public_endpoint(endpoint):
        command_parts.extend(["-H", f'"Authorization: Bearer {DEFAULT_AUTH_TOKEN}"'])
    if needs_idempotency(endpoint):
        command_parts.extend(["-H", f'"Idempotency-Key: {DEFAULT_IDEMPOTENCY_KEY}"'])
    if method in {"POST", "PUT", "PATCH"}:
        command_parts.extend(["-H", '"Content-Type: application/json"', "-d", '"<JSON_BODY>"'])
    command_parts.append(f'"{DEFAULT_BASE_URL}{endpoint_to_command_path(endpoint)}"')
    return " ".join(command_parts)


def as_html(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def markdown_to_flowables(markdown: str) -> list[object]:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#0D2D4A"),
        spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=colors.HexColor("#0E5F67"),
        spaceBefore=8,
        spaceAfter=5,
    )
    h3_style = ParagraphStyle(
        "H3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#20415F"),
        spaceBefore=6,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#1F2E3A"),
        spaceAfter=2,
    )
    code_style = ParagraphStyle(
        "Code",
        parent=body_style,
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        backColor=colors.HexColor("#F3F7FA"),
        borderColor=colors.HexColor("#D3E0E8"),
        borderWidth=0.3,
        borderPadding=4,
    )
    cmd_style = ParagraphStyle(
        "Cmd",
        parent=code_style,
        fontSize=8,
        leading=10,
        spaceAfter=0,
    )

    flowables: list[object] = []
    lines = markdown.splitlines()
    idx = 0
    in_code_block = False
    code_lines: list[str] = []
    bullet_items: list[str] = []

    def flush_bullets() -> None:
        nonlocal bullet_items
        if not bullet_items:
            return
        items: list[ListItem] = []
        for item in bullet_items:
            endpoint = extract_endpoint(item)
            if endpoint:
                method, path = endpoint
                command = build_curl_command(method, path)
                items.append(
                    ListItem(
                        [Paragraph(item, body_style), Paragraph(as_html(command), cmd_style)],
                        leftIndent=4,
                    ),
                )
            else:
                items.append(ListItem(Paragraph(item, body_style), leftIndent=4))
        flowables.append(
            ListFlowable(
                items,
                bulletType="bullet",
                start="circle",
                bulletFontName="Helvetica",
                bulletFontSize=8,
                leftIndent=12,
            ),
        )
        bullet_items = []

    while idx < len(lines):
        raw = lines[idx]
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                flowables.append(Paragraph("<br/>".join(code_lines), code_style))
                flowables.append(Spacer(1, 4))
                code_lines = []
                in_code_block = False
            else:
                flush_bullets()
                in_code_block = True
            idx += 1
            continue

        if in_code_block:
            code_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            idx += 1
            continue

        if not stripped:
            flush_bullets()
            flowables.append(Spacer(1, 2))
            idx += 1
            continue

        if stripped == "---":
            flush_bullets()
            flowables.append(Spacer(1, 4))
            idx += 1
            continue

        if stripped.startswith("- "):
            bullet_items.append(stripped[2:].replace("`", ""))
            idx += 1
            continue

        flush_bullets()

        if stripped.startswith("# "):
            flowables.append(Paragraph(stripped[2:], title_style))
        elif stripped.startswith("## "):
            flowables.append(Paragraph(stripped[3:], h2_style))
        elif stripped.startswith("### "):
            flowables.append(Paragraph(stripped[4:], h3_style))
        else:
            line = stripped.replace("`", "")
            flowables.append(Paragraph(line, body_style))
            endpoint = extract_endpoint(line)
            if endpoint:
                method, path = endpoint
                command = build_curl_command(method, path)
                flowables.append(Paragraph(as_html(command), cmd_style))
        idx += 1

    flush_bullets()
    return flowables


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    flowables = markdown_to_flowables(markdown)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=14 * mm,
        title="MT-Facturation API Process Map",
    )
    document.build(flowables)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
