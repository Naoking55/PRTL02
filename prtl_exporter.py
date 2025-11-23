#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Premiere Pro Legacy Title PRTL Exporter
.prprojファイルから埋め込まれたレガシータイトルを抽出してPRTLファイルとして保存
"""

import gzip
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import re


class PRTLExporter:
    def __init__(self, gui_mode=True):
        self.gui_mode = gui_mode
        self.titles = []
        self.current_prproj_path = None

        if gui_mode:
            # GUIモードの時だけtkinterをインポート
            import tkinter as tk
            from tkinter import ttk, messagebox, filedialog

            self.tk = tk
            self.ttk = ttk
            self.messagebox = messagebox
            self.filedialog = filedialog

            self.root = tk.Tk()
            self.root.title("Legacy Title PRTL Exporter")
            self.root.geometry("600x500")
            self.root.configure(bg="#2b2b2b")

            self.setup_ui()

    def setup_ui(self):
        """UIのセットアップ"""
        # スタイル設定
        style = self.ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#2b2b2b", foreground="#ffffff")
        style.configure('TButton', background="#4080ff", foreground="#ffffff")
        style.configure('TFrame', background="#2b2b2b")

        # メインフレーム
        main_frame = self.ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=self.tk.BOTH, expand=True)

        # タイトル
        title_label = self.ttk.Label(
            main_frame,
            text="Legacy Title PRTL Exporter",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # ファイル選択ボタン
        select_button = self.tk.Button(
            main_frame,
            text=".prprojファイルを選択",
            bg="#4080ff",
            fg="#ffffff",
            font=("Arial", 12),
            command=self.select_file,
            padx=20,
            pady=10
        )
        select_button.pack(pady=10)

        # ステータスエリア
        status_frame = self.ttk.Frame(main_frame)
        status_frame.pack(fill=self.tk.BOTH, expand=True, pady=10)

        status_label = self.ttk.Label(status_frame, text="ステータス:", font=("Arial", 10, "bold"))
        status_label.pack(anchor=self.tk.W)

        self.status_text = self.tk.Text(
            status_frame,
            height=12,
            bg="#505050",
            fg="#c0c0c0",
            font=("Courier", 9),
            wrap=self.tk.WORD
        )
        self.status_text.pack(fill=self.tk.BOTH, expand=True)

        # スクロールバー
        scrollbar = self.tk.Scrollbar(self.status_text)
        scrollbar.pack(side=self.tk.RIGHT, fill=self.tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)

        # ボタンフレーム
        button_frame = self.ttk.Frame(main_frame)
        button_frame.pack(fill=self.tk.X, pady=(10, 0))

        self.export_button = self.tk.Button(
            button_frame,
            text="すべてのタイトルをエクスポート",
            bg="#4080ff",
            fg="#ffffff",
            font=("Arial", 11),
            state=self.tk.DISABLED,
            command=self.export_all_titles
        )
        self.export_button.pack(fill=self.tk.X)

        self.log("準備完了。ファイルを選択してください。")

    def select_file(self):
        """ファイル選択ダイアログを開く"""
        file_path = self.filedialog.askopenfilename(
            title=".prprojファイルを選択",
            filetypes=[("Premiere Pro Project", "*.prproj"), ("All Files", "*.*")]
        )

        if file_path:
            self.log(f"読み込み中: {os.path.basename(file_path)}")
            self.current_prproj_path = file_path
            self.process_prproj(file_path)

    def log(self, message):
        """ステータスログを追加"""
        if self.gui_mode:
            self.status_text.insert(self.tk.END, f"{message}\n")
            self.status_text.see(self.tk.END)
            self.root.update()
        else:
            print(message)

    def process_prproj(self, file_path):
        """prprojファイルを処理"""
        try:
            # GZIP解凍してXMLを取得
            self.log("ファイルを解凍中...")
            xml_content = self.decompress_prproj(file_path)

            if not xml_content:
                self.log("エラー: ファイルの解凍に失敗しました")
                return

            # XMLをパース
            self.log("XMLを解析中...")
            root = ET.fromstring(xml_content)

            # レガシータイトルを抽出
            self.log("レガシータイトルを検索中...")
            self.titles = self.extract_legacy_titles(root)

            if not self.titles:
                self.log("⚠ レガシータイトルが見つかりませんでした")
                if self.gui_mode:
                    self.messagebox.showwarning("結果", "レガシータイトルが見つかりませんでした")
                    self.export_button.config(state=self.tk.DISABLED)
            else:
                self.log(f"✓ {len(self.titles)}個のレガシータイトルを検出しました")
                for i, title in enumerate(self.titles, 1):
                    name = title.get('name', f'Title_{i}')
                    self.log(f"  {i}. {name}")
                if self.gui_mode:
                    self.export_button.config(state=self.tk.NORMAL)

        except Exception as e:
            self.log(f"エラー: {str(e)}")
            if self.gui_mode:
                self.messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{str(e)}")

    def decompress_prproj(self, file_path):
        """prprojファイル（GZIP圧縮）を解凍"""
        try:
            with gzip.open(file_path, 'rb') as f:
                return f.read().decode('utf-8')
        except Exception as e:
            self.log(f"解凍エラー: {str(e)}")
            return None

    def extract_legacy_titles(self, root):
        """XMLからレガシータイトルを抽出"""
        titles = []

        # PremiereDataのバージョンを確認
        version = root.get('Version', 'Unknown')
        self.log(f"PremiereData Version: {version}")

        # レガシータイトルのClassID
        LEGACY_TITLE_CLASS_ID = "fb11c33a-b0a9-4465-aa94-b6d5db2628cf"

        # すべてのMasterClipを探索
        for master_clip in root.iter('MasterClip'):
            class_id = master_clip.get('ClassID', '')

            # レガシータイトルのClassIDと一致するか確認
            if class_id == LEGACY_TITLE_CLASS_ID:
                self.log(f"レガシータイトルのMasterClipを発見: ClassID={class_id}")

                # 名前を取得
                name_elem = master_clip.find('.//Name')
                title_name = name_elem.text if name_elem is not None and name_elem.text else "Untitled"

                # Clip要素からVideoClipを探す
                # MasterClip/Clips/Clip[@ObjectRef] → VideoClip[@ObjectID]
                clip_ref_elem = master_clip.find('.//Clip[@ObjectRef]')
                if clip_ref_elem is not None:
                    clip_ref = clip_ref_elem.get('ObjectRef')
                    self.log(f"  Clip ObjectRef: {clip_ref}")

                    # VideoClipを探す
                    video_clip = self.find_videoclip_by_id(root, clip_ref)
                    if video_clip is not None:
                        self.log(f"  VideoClipを発見")

                        # VideoClip/Clip/Source[@ObjectRef] → VideoMediaSource[@ObjectID]
                        source_elem = video_clip.find('.//Source[@ObjectRef]')
                        if source_elem is not None:
                            media_source_ref = source_elem.get('ObjectRef')
                            self.log(f"  Source ObjectRef: {media_source_ref}")

                            # Media要素を探す
                            media = self.find_media_by_source_ref(root, media_source_ref)
                            if media:
                                self.log(f"  Media要素を発見")
                                # ImporterPrefsからPRTLデータを取得
                                prtl_data = self.extract_prtl_from_media(media)
                                if prtl_data:
                                    titles.append({
                                        'name': self.sanitize_filename(title_name),
                                        'object_id': master_clip.get('ObjectUID'),
                                        'prtl_content': prtl_data
                                    })
                                    self.log(f"  ✓ PRTLデータを抽出: {title_name}")
                                else:
                                    self.log(f"  ✗ PRTLデータが空です: {title_name}")
                            else:
                                self.log(f"  ✗ Media要素が見つかりません")
                        else:
                            self.log(f"  ✗ Source要素が見つかりません")
                    else:
                        self.log(f"  ✗ VideoClipが見つかりません (ObjectID={clip_ref})")
                else:
                    self.log(f"  ✗ Clip要素が見つかりません")

        return titles

    def find_videoclip_by_id(self, root, object_id):
        """ObjectIDでVideoClipを探す"""
        for videoclip in root.iter('VideoClip'):
            if videoclip.get('ObjectID') == object_id:
                return videoclip
        return None

    def find_media_by_source_ref(self, root, object_ref):
        """ObjectRefからMedia要素を探す"""
        # VideoMediaSource要素を探す
        for video_media_source in root.iter('VideoMediaSource'):
            if video_media_source.get('ObjectID') == object_ref:
                # MediaSource内のMedia参照を取得
                media_elem = video_media_source.find('.//Media')
                if media_elem is not None:
                    media_uid = media_elem.get('ObjectURef')
                    if media_uid:
                        # UIDでMedia要素を探す
                        for media in root.iter('Media'):
                            if media.get('ObjectUID') == media_uid:
                                return media
        return None

    def extract_prtl_from_media(self, media):
        """Media要素からImporterPrefsのPRTLデータを抽出"""
        import base64
        import zlib

        try:
            # ImporterPrefs要素を探す
            importer_prefs = media.find('.//ImporterPrefs')
            if importer_prefs is None:
                return None

            # Encoding属性を確認
            encoding = importer_prefs.get('Encoding', '')
            if encoding != 'base64':
                self.log(f"  警告: 予期しないEncoding: {encoding}")
                return None

            # Base64データを取得
            base64_data = importer_prefs.text
            if not base64_data or not base64_data.strip():
                return None

            # Base64デコード
            try:
                binary_data = base64.b64decode(base64_data.strip())
            except Exception as e:
                self.log(f"  Base64デコードエラー: {str(e)}")
                return None

            # "CompressedTitle"ヘッダーをチェック
            if b'CompressedTitle' in binary_data[:100]:
                self.log(f"  CompressedTitleヘッダーを検出")

                # データからPRTL部分を抽出
                # ヘッダーをスキップして圧縮データを探す
                # zlib圧縮データは 0x78 0x9c または 0x78 0xda で始まることが多い
                zlib_start = -1
                for i in range(len(binary_data) - 1):
                    if binary_data[i] == 0x78 and binary_data[i+1] in [0x9c, 0xda, 0x01]:
                        zlib_start = i
                        break

                if zlib_start >= 0:
                    try:
                        # zlib解凍
                        decompressed = zlib.decompress(binary_data[zlib_start:])
                        self.log(f"  解凍成功: {len(decompressed)} bytes")

                        # UTF-16でデコード (Premiere Proのタイトルデータは通常UTF-16)
                        try:
                            prtl_text = decompressed.decode('utf-16', errors='ignore')
                            self.log(f"  UTF-16デコード成功: {len(prtl_text)} chars")
                            return prtl_text
                        except:
                            # UTF-16が失敗したらUTF-8を試す
                            prtl_text = decompressed.decode('utf-8', errors='ignore')
                            self.log(f"  UTF-8デコード成功: {len(prtl_text)} chars")
                            return prtl_text
                    except Exception as e:
                        self.log(f"  zlib解凍エラー: {str(e)}")
                        return None

            # 圧縮されていない場合は、そのまま返す
            try:
                return binary_data.decode('utf-16', errors='ignore')
            except:
                try:
                    return binary_data.decode('utf-8', errors='ignore')
                except:
                    return None

        except Exception as e:
            self.log(f"  PRTL抽出エラー: {str(e)}")
            return None

    def sanitize_filename(self, name):
        """ファイル名として使用できるように文字列をサニタイズ"""
        # 使用できない文字を削除
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # スペースをアンダースコアに
        name = re.sub(r'\s+', '_', name)
        # 長すぎる場合は切り詰め
        if len(name) > 50:
            name = name[:50]
        return name

    def get_downloads_prtl_folder(self):
        """ダウンロード/prtlフォルダのパスを取得"""
        # ダウンロードフォルダを取得（クロスプラットフォーム対応）
        if sys.platform == 'win32':
            downloads = Path.home() / 'Downloads'
        elif sys.platform == 'darwin':  # macOS
            downloads = Path.home() / 'Downloads'
        else:  # Linux
            downloads = Path.home() / 'Downloads'

        # Downloadsフォルダが存在しない場合は作成
        downloads.mkdir(exist_ok=True)

        # prtlサブフォルダを作成
        prtl_folder = downloads / 'prtl'
        prtl_folder.mkdir(exist_ok=True)

        return prtl_folder

    def export_all_titles(self):
        """すべてのタイトルをエクスポート"""
        if not self.titles:
            msg = "エクスポートするタイトルがありません"
            if self.gui_mode:
                self.messagebox.showwarning("警告", msg)
            else:
                self.log(f"警告: {msg}")
            return

        try:
            output_dir = self.get_downloads_prtl_folder()
            self.log(f"\n保存先: {output_dir}")

            success_count = 0
            for i, title in enumerate(self.titles, 1):
                name = title['name']
                prtl_content = title.get('prtl_content', '')

                if not prtl_content:
                    self.log(f"⚠ スキップ（データなし）: {name}")
                    continue

                # ファイル名を生成
                filename = f"{name}.prtl"
                filepath = output_dir / filename

                # ファイルが既に存在する場合は番号を付ける
                counter = 1
                while filepath.exists():
                    filename = f"{name}_{counter}.prtl"
                    filepath = output_dir / filename
                    counter += 1

                # ファイルに書き込み
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(prtl_content)

                self.log(f"✓ 保存: {filename}")
                success_count += 1

            self.log(f"\n完了: {success_count}個のタイトルをエクスポートしました")
            if self.gui_mode:
                self.messagebox.showinfo(
                    "完了",
                    f"{success_count}個のタイトルをエクスポートしました\n\n保存先:\n{output_dir}"
                )

        except Exception as e:
            self.log(f"エラー: {str(e)}")
            if self.gui_mode:
                self.messagebox.showerror("エラー", f"エクスポート中にエラーが発生しました:\n{str(e)}")

    def create_prtl_content(self, xml_content, title_name):
        """PRTLファイルのコンテンツを生成"""
        # PremiereDataのラッパーで囲む
        prtl = f'''<?xml version="1.0" encoding="UTF-8"?>
<PremiereData Version="3">
{xml_content}
</PremiereData>
'''
        return prtl

    def run(self):
        """アプリケーションを実行"""
        if self.gui_mode:
            self.root.mainloop()

    def process_file_cli(self, file_path):
        """コマンドラインモードでファイルを処理"""
        self.titles = []
        self.log(f"読み込み中: {os.path.basename(file_path)}")
        self.process_prproj(file_path)

        if self.titles:
            self.export_all_titles()
        else:
            self.log("レガシータイトルが見つかりませんでした")
            return 1
        return 0


def show_help():
    """ヘルプメッセージを表示"""
    print("""
Legacy Title PRTL Exporter
Premiere Proプロジェクトファイルからレガシータイトルを抽出

使い方:
    python prtl_exporter.py [OPTIONS] [FILE]

オプション:
    -h, --help          このヘルプを表示
    -v, --version       バージョン情報を表示

引数:
    FILE                .prprojファイルのパス（省略時はGUIモード）

例:
    # GUIモードで起動
    python prtl_exporter.py

    # CLIモードで起動
    python prtl_exporter.py project.prproj

出力先:
    ダウンロードフォルダ/prtl/
    """)


def main():
    """メイン関数"""
    try:
        # ヘルプオプションをチェック
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
            show_help()
            sys.exit(0)

        # バージョンオプションをチェック
        if len(sys.argv) > 1 and sys.argv[1] in ['-v', '--version']:
            print("Legacy Title PRTL Exporter v1.0.0")
            sys.exit(0)

        # コマンドライン引数をチェック
        if len(sys.argv) > 1:
            # CLIモード
            file_path = sys.argv[1]
            if not os.path.exists(file_path):
                print(f"エラー: ファイルが見つかりません: {file_path}", file=sys.stderr)
                sys.exit(1)

            if not file_path.lower().endswith('.prproj'):
                print("エラー: .prprojファイルを指定してください", file=sys.stderr)
                sys.exit(1)

            app = PRTLExporter(gui_mode=False)
            sys.exit(app.process_file_cli(file_path))
        else:
            # GUIモード
            app = PRTLExporter(gui_mode=True)
            app.run()

    except KeyboardInterrupt:
        print("\n中断されました", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
