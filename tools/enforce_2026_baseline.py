#!/usr/bin/env python3
"""将网页内嵌数据校正到 2026 版考核大纲和复习指南口径。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TRANSPORT_NOTE = (
    "熟悉五种运输形式及对应规则：包装危险货物——《国际海上人命安全公约》第VII章A部分、"
    "《国际防止船舶造成污染公约》附则III、《国际海运危险货物规则》；固体散装货物——《国际海上人命"
    "安全公约》第VI章A、B部分和第VII章A-1部分、《国际海运固体散装货物规则》、GB 40558《海运固体散装货物"
    "安全技术要求》；散装油类——《国际防止船舶造成污染公约》附则I；散装液体化学品——《国际海上人命安全"
    "公约》第VII章B部分、《国际防止船舶造成污染公约》附则II、《国际散装危险化学品船舶构造和设备规则》；"
    "散装液化气体——《国际海上人命安全公约》第VII章C部分、《国际散装液化气体船舶构造和设备规则》。"
)


def rewrite_embedded_json(
    path: Path,
    prefix: str,
    suffix: str,
    mutate,
) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index(prefix) + len(prefix)
    end = text.index(suffix, start)
    data = json.loads(text[start:end])
    mutate(data)
    encoded = json.dumps(data, ensure_ascii=False)
    path.write_text(text[:start] + encoded + text[end:], encoding="utf-8")


def update_study_map(data: dict) -> None:
    data["subtitle"] = "2026版《考核大纲》+《考核复习指南》—固体散装方向"
    item = next(item for item in data["items"] if item["id"] == "i41")
    item["note"] = TRANSPORT_NOTE
    assert data["total"] == 103


def merge_false_cross_reference(
    articles: list[str],
    false_prefix: str,
    plain_reference: str,
) -> None:
    for index in range(len(articles) - 1, 0, -1):
        if articles[index].startswith(false_prefix):
            continuation = articles[index].replace(
                false_prefix,
                plain_reference,
                1,
            )
            articles[index - 1] = articles[index - 1].rstrip() + continuation
            del articles[index]


def update_law_reader(data: list[dict]) -> None:
    reg = next(item for item in data if item["id"] == "reg3")

    # PDF 转文本时，条文内的“第五条”和“第十八条”交叉引用被误切成新条文。
    merge_false_cross_reference(
        reg["chapters"][0]["articles"],
        "**第五条** 规定的能力要求",
        "第五条规定的能力要求",
    )
    merge_false_cross_reference(
        reg["chapters"][3]["articles"],
        "**第十八条**",
        "第十八条",
    )

    counts = [len(chapter["articles"]) for chapter in reg["chapters"]]
    assert counts == [7, 7, 3, 4, 9, 2], counts
    reg["chapter_count"] = 6
    reg["article_count"] = sum(counts)
    assert reg["article_count"] == 32


def main() -> None:
    rewrite_embedded_json(
        ROOT / "学习导图.html",
        "const DATA = ",
        ";\nconst LEVEL",
        update_study_map,
    )
    rewrite_embedded_json(
        ROOT / "法规阅读.html",
        "const DATA = ",
        ";\nconst STORAGE_NOTES",
        update_law_reader,
    )


if __name__ == "__main__":
    main()
