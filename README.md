# Legacy Title PRTL Exporter

Premiere Pro 2021向けのCEPエクステンション。レガシータイトルをPRTL形式でエクスポートします。

## 概要

Premiere Pro 2022以降ではレガシータイトル機能が削除されましたが、2021以前のバージョンで作成したレガシータイトルをPRTLファイルとして保存することで、バックアップや移行が可能になります。

## 機能

- タイムライン上のレガシータイトルを自動検出
- 選択したタイトルまたは全タイトルをPRTL形式でエクスポート
- タイトルのプロパティとメタデータを保持
- デスクトップに自動保存

## 対応バージョン

- Adobe Premiere Pro 2021 (v15.x)

## インストール方法

### 1. エクステンションフォルダを配置

エクステンションを以下のフォルダにコピーします：

**Windows:**
```
C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\PRTL02
```

**macOS:**
```
/Library/Application Support/Adobe/CEP/extensions/PRTL02
```

### 2. CSInterface.jsをダウンロード

`client`フォルダに`CSInterface.js`を配置する必要があります。

以下のURLからダウンロードしてください：
```
https://raw.githubusercontent.com/Adobe-CEP/CEP-Resources/master/CEP_10.x/CSInterface.js
```

ダウンロード後、`client/CSInterface.js`として保存してください。

### 3. デバッグモードを有効化

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

### 4. Premiere Proを再起動

Premiere Proを再起動すると、メニューに表示されます：
```
ウィンドウ > エクステンション > Legacy Title PRTL Exporter
```

## 使い方

### 1. タイムラインをスキャン

1. Premiere Proでプロジェクトを開き、シーケンスをアクティブにします
2. エクステンションパネルで「タイムラインをスキャン」ボタンをクリック
3. レガシータイトルが検出されてリストに表示されます

### 2. エクスポート

**個別エクスポート:**
1. リストからタイトルを選択
2. 「選択したタイトルをエクスポート」ボタンをクリック

**一括エクスポート:**
1. 「すべてのタイトルをエクスポート」ボタンをクリック

エクスポートされたPRTLファイルはデスクトップに保存されます。

## ファイル構造

```
PRTL02/
├── .debug                  # デバッグ設定
├── CSXS/
│   └── manifest.xml       # エクステンション設定
├── client/
│   ├── index.html         # UIパネル
│   ├── index.js           # クライアント側JavaScript
│   └── CSInterface.js     # Adobe CEPライブラリ（要ダウンロード）
├── host/
│   └── index.jsx          # ExtendScript（Premiere Pro側）
└── README.md              # このファイル
```

## PRTLファイル形式

エクスポートされるPRTLファイルはXML形式で、以下の情報を含みます：

- タイトル名
- 継続時間
- コンポーネントとプロパティ
- エクスポート日時
- メタデータ

## トラブルシューティング

### エクステンションが表示されない

1. デバッグモードが有効になっているか確認
2. エクステンションフォルダのパスが正しいか確認
3. Premiere Proを再起動
4. CSInterface.jsが正しく配置されているか確認

### タイトルが検出されない

1. アクティブなシーケンスがあるか確認
2. タイムラインにレガシータイトルが配置されているか確認
3. タイトルがビデオトラック上にあるか確認

### エクスポートが失敗する

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
