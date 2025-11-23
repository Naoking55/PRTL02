# Legacy Title PRTL Exporter

Premiere Proのレガシータイトルを.prprojファイルから抽出し、PRTLファイルとして保存するツール。

## 概要

Premiere Pro 2022以降ではレガシータイトル機能が削除されましたが、プロジェクトファイル(.prproj)内に埋め込まれているレガシータイトルデータを抽出してPRTLファイルとして保存することで、バックアップや移行が可能になります。

## 主な機能

### Pythonツール（推奨）
- .prprojファイルから直接レガシータイトルを抽出
- GUIとCLIの両モードに対応
- 標準ライブラリのみで動作（外部依存なし）
- ダウンロードフォルダの`prtl`サブフォルダに自動保存

### CEPエクステンション（開発版）
- タイムライン上のレガシータイトルを自動検出
- 選択したタイトルまたは全タイトルをPRTL形式でエクスポート
- Premiere Pro 2021 (v15.x)対応

## Pythonツールの使い方

### 必要要件

- Python 3.6以上
- 標準ライブラリのみ（外部パッケージ不要）

### GUIモード

1. スクリプトをダブルクリックで実行、または：
   ```bash
   python prtl_exporter.py
   ```

2. 「.prprojファイルを選択」ボタンをクリック

3. レガシータイトルを含むPremiere Proプロジェクトファイルを選択

4. 検出されたタイトルがリストに表示されます

5. 「すべてのタイトルをエクスポート」ボタンをクリック

6. PRTLファイルが以下の場所に保存されます：
   - **Windows**: `C:\Users\[ユーザー名]\Downloads\prtl\`
   - **macOS**: `/Users/[ユーザー名]/Downloads/prtl/`
   - **Linux**: `/home/[ユーザー名]/Downloads/prtl/`

### CLIモード

コマンドライン引数で.prprojファイルを指定して実行：

```bash
python prtl_exporter.py /path/to/project.prproj
```

自動的にレガシータイトルを検出して、ダウンロードフォルダの`prtl`サブフォルダにエクスポートします。

---

## CEPエクステンションの使い方（開発版）

### インストール方法

<details>
<summary>インストール手順を表示（クリックして展開）</summary>

#### 1. エクステンションフォルダを配置

エクステンションを以下のフォルダにコピーします：

**Windows:**
```
C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\PRTL02
```

**macOS:**
```
/Library/Application Support/Adobe/CEP/extensions/PRTL02
```

#### 2. CSInterface.jsをダウンロード

`client`フォルダに`CSInterface.js`を配置する必要があります。

以下のURLからダウンロードしてください：
```
https://raw.githubusercontent.com/Adobe-CEP/CEP-Resources/master/CEP_10.x/CSInterface.js
```

ダウンロード後、`client/CSInterface.js`として保存してください。

#### 3. デバッグモードを有効化

CEPエクステンションを開発・使用するには、デバッグモードを有効にする必要があります。

**Windows:**

1. レジストリエディタ（regedit）を開く
2. 以下のキーに移動：
   ```
   HKEY_CURRENT_USER\Software\Adobe\CSXS.10
   ```
3. キーが存在しない場合は作成
4. 文字列値 `PlayerDebugMode` を作成し、値を `1` に設定

**macOS:**

ターミナルで以下のコマンドを実行：
```bash
defaults write com.adobe.CSXS.10 PlayerDebugMode 1
```

#### 4. Premiere Proを再起動

Premiere Proを再起動すると、メニューに表示されます：
```
ウィンドウ > エクステンション > Legacy Title PRTL Exporter
```

</details>

### 使い方

1. Premiere Proでプロジェクトを開き、シーケンスをアクティブにします
2. エクステンションパネルで「タイムラインをスキャン」ボタンをクリック
3. レガシータイトルが検出されてリストに表示されます
4. 「すべてのタイトルをエクスポート」ボタンをクリック

エクスポートされたPRTLファイルはデスクトップに保存されます。

---

## ファイル構造

```
PRTL02/
├── prtl_exporter.py        # Pythonツール（推奨）
├── .debug                  # デバッグ設定
├── CSXS/
│   └── manifest.xml        # CEPエクステンション設定
├── client/
│   ├── index.html          # UIパネル
│   ├── index.js            # クライアント側JavaScript
│   └── CSInterface.js      # Adobe CEPライブラリ（要ダウンロード）
├── host/
│   └── index.jsx           # ExtendScript（Premiere Pro側）
└── README.md               # このファイル
```

## PRTLファイル形式

エクスポートされるPRTLファイルはXML形式で、以下の情報を含みます：

- タイトル名
- 継続時間
- コンポーネントとプロパティ
- エクスポート日時
- メタデータ

## トラブルシューティング

### Pythonツール

#### タイトルが検出されない

1. .prprojファイルに本当にレガシータイトルが含まれているか確認してください
2. プロジェクトファイルが破損していないか確認してください
3. Premiere Proでプロジェクトを開いて、プロジェクトウィンドウでレガシータイトルが表示されているか確認してください

#### エラー: ファイルの解凍に失敗

1. .prprojファイルが正しいPremiere Proプロジェクトファイルか確認してください
2. ファイルが破損していないか確認してください
3. 古いバージョンのPremiereで作成されたファイル（CS6以前）の場合、GZIP圧縮されていない可能性があります

#### GUIが表示されない

1. Python 3.6以上がインストールされているか確認してください：
   ```bash
   python --version
   ```
2. tkinterがインストールされているか確認してください（通常、Pythonに同梱されています）

### CEPエクステンション

#### エクステンションが表示されない

1. デバッグモードが有効になっているか確認
2. エクステンションフォルダのパスが正しいか確認
3. Premiere Proを再起動
4. CSInterface.jsが正しく配置されているか確認

#### タイトルが検出されない

1. アクティブなシーケンスがあるか確認
2. タイムラインにレガシータイトルが配置されているか確認
3. タイトルがビデオトラック上にあるか確認

#### エクスポートが失敗する

1. デスクトップへの書き込み権限があるか確認
2. ディスクに十分な空き容量があるか確認
3. ファイル名に使用できない文字が含まれていないか確認

## 開発情報

### デバッグ

Chromeでデバッグするには：

1. Premiere Proでエクステンションを開く
2. ブラウザで以下にアクセス：
   ```
   http://localhost:8088
   ```
3. DevToolsでデバッグ可能

### カスタマイズ

- `client/index.html` - UIのカスタマイズ
- `client/index.js` - クライアント側のロジック
- `host/index.jsx` - Premiere Pro連携とエクスポートロジック
- `CSXS/manifest.xml` - エクステンション設定

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

- このエクステンションはPremiere Pro 2021専用です
- Premiere Pro 2022以降ではレガシータイトル機能が削除されているため使用できません
- エクスポートされたPRTLファイルの互換性は保証されません
- 本番環境での使用前に必ずテストしてください

## サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。
