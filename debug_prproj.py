#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.prprojファイルのXML構造をデバッグするツール
"""

import gzip
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def analyze_prproj(file_path):
    """prprojファイルを解析してタイトル関連の要素を探す"""

    # GZIP解凍
    print(f"ファイルを解凍中: {file_path}")
    try:
        with gzip.open(file_path, 'rb') as f:
            xml_content = f.read().decode('utf-8')
        print("✓ 解凍成功\n")
    except Exception as e:
        print(f"✗ 解凍エラー: {e}")
        return

    # XMLをパース
    try:
        root = ET.fromstring(xml_content)
        print(f"✓ XMLパース成功")
        print(f"ルート要素: {root.tag}")
        print(f"Version: {root.get('Version', 'N/A')}\n")
    except Exception as e:
        print(f"✗ XMLパースエラー: {e}")
        return

    # すべての要素タグを収集
    all_tags = set()
    for elem in root.iter():
        all_tags.add(elem.tag)

    print(f"=== 検出された要素タグ ({len(all_tags)}個) ===")
    for tag in sorted(all_tags):
        print(f"  - {tag}")
    print()

    # "Title"を含む要素を探す
    print("=== 'Title'を含む要素 ===")
    title_elements = []
    for elem in root.iter():
        if 'title' in elem.tag.lower() or 'title' in str(elem.get('ClassID', '')).lower():
            title_elements.append(elem)
            print(f"タグ: {elem.tag}")
            print(f"  ClassID: {elem.get('ClassID', 'N/A')}")
            print(f"  ObjectID: {elem.get('ObjectID', 'N/A')}")
            if elem.text and elem.text.strip():
                print(f"  テキスト: {elem.text.strip()[:100]}")
            print()

    # ProjectItemを探す
    print("=== ProjectItem要素 ===")
    project_items = root.findall('.//ProjectItem')
    print(f"ProjectItem数: {len(project_items)}\n")

    for i, item in enumerate(project_items[:10], 1):  # 最初の10個のみ
        print(f"ProjectItem {i}:")
        print(f"  ObjectID: {item.get('ObjectID', 'N/A')}")
        print(f"  ClassID: {item.get('ClassID', 'N/A')}")

        # 名前を探す
        name_elem = item.find('.//Name')
        if name_elem is not None and name_elem.text:
            print(f"  Name: {name_elem.text}")

        # MediaSourceを探す
        media_source = item.find('.//MediaSource')
        if media_source is not None:
            print(f"  MediaSource ClassID: {media_source.get('ClassID', 'N/A')}")

        # 子要素を表示
        children = list(item)
        if children:
            print(f"  子要素: {', '.join([c.tag for c in children[:5]])}")
        print()

    # MasterClipを探す
    print("=== MasterClip要素 ===")
    master_clips = root.findall('.//MasterClip')
    print(f"MasterClip数: {len(master_clips)}\n")

    for i, clip in enumerate(master_clips[:10], 1):
        print(f"MasterClip {i}:")
        print(f"  ObjectID: {clip.get('ObjectID', 'N/A')}")
        print(f"  ClassID: {clip.get('ClassID', 'N/A')}")

        name_elem = clip.find('.//Name')
        if name_elem is not None and name_elem.text:
            print(f"  Name: {name_elem.text}")
        print()

    # XMLの一部をファイルに保存
    output_file = Path(file_path).stem + "_structure.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== XML構造サンプル ===\n\n")

        # 最初の1000行を保存
        lines = xml_content.split('\n')
        for i, line in enumerate(lines[:1000], 1):
            f.write(f"{i:4d}: {line}\n")

    print(f"\n✓ 詳細をファイルに保存しました: {output_file}")
    print(f"  このファイルを確認して、タイトルデータがどこにあるか探してください。")

def main():
    if len(sys.argv) < 2:
        print("使い方: python debug_prproj.py <file.prproj>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"エラー: ファイルが見つかりません: {file_path}")
        sys.exit(1)

    analyze_prproj(file_path)

if __name__ == '__main__':
    main()
