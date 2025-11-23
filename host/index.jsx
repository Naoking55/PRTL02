/* global app, Folder, File */

/**
 * Legacy Title PRTL Exporter - ExtendScript
 * Premiere Pro 2021 対応
 */

/**
 * アクティブシーケンス内のレガシータイトルをスキャン
 */
function scanForLegacyTitles() {
    try {
        var project = app.project;
        if (!project) {
            return JSON.stringify({ error: "プロジェクトが開かれていません" });
        }

        var sequence = project.activeSequence;
        if (!sequence) {
            return JSON.stringify({ error: "アクティブなシーケンスがありません" });
        }

        var titles = [];
        var videoTracks = sequence.videoTracks;

        // 全てのビデオトラックをスキャン
        for (var i = 0; i < videoTracks.numTracks; i++) {
            var track = videoTracks[i];
            var clips = track.clips;

            for (var j = 0; j < clips.numItems; j++) {
                var clip = clips[j];

                // レガシータイトルかどうかを判定
                if (isLegacyTitle(clip)) {
                    titles.push({
                        name: clip.name,
                        trackIndex: i,
                        clipIndex: j,
                        start: clip.start.seconds,
                        end: clip.end.seconds,
                        duration: (clip.end.seconds - clip.start.seconds)
                    });
                }
            }
        }

        return JSON.stringify({
            success: true,
            titles: titles,
            count: titles.length
        });

    } catch (e) {
        return JSON.stringify({ error: e.toString() });
    }
}

/**
 * クリップがレガシータイトルかどうかを判定
 */
function isLegacyTitle(clip) {
    try {
        // レガシータイトルの判定方法
        // 1. クリップの種類をチェック
        var projectItem = clip.projectItem;
        if (!projectItem) {
            return false;
        }

        // タイプコードが 4（Title）であることを確認
        if (projectItem.type === 4) {
            return true;
        }

        // 名前に "Title" が含まれているかチェック（追加の判定）
        var name = clip.name.toLowerCase();
        if (name.indexOf("title") !== -1 || name.indexOf("タイトル") !== -1) {
            // さらにメディアパスをチェック
            var mediaPath = projectItem.getMediaPath();
            if (mediaPath === "" || mediaPath.indexOf(".prtl") !== -1) {
                return true;
            }
        }

        return false;
    } catch (e) {
        return false;
    }
}

/**
 * レガシータイトルをPRTLファイルとしてエクスポート
 */
function exportLegacyTitleToPRTL(params) {
    try {
        var config = JSON.parse(params);
        var project = app.project;
        var sequence = project.activeSequence;

        if (!sequence) {
            return JSON.stringify({ error: "アクティブなシーケンスがありません" });
        }

        var track = sequence.videoTracks[config.trackIndex];
        if (!track) {
            return JSON.stringify({ error: "トラックが見つかりません" });
        }

        var clip = track.clips[config.clipIndex];
        if (!clip) {
            return JSON.stringify({ error: "クリップが見つかりません" });
        }

        // タイトルのプロパティを取得
        var titleData = extractTitleData(clip);

        // PRTLファイルを生成
        var prtlContent = generatePRTLContent(titleData);

        // ファイル名を生成（クリップ名をベースに）
        var safeFileName = sanitizeFileName(clip.name);
        var timestamp = new Date().getTime();
        var fileName = safeFileName + "_" + timestamp + ".prtl";

        // 保存先フォルダを選択（デスクトップをデフォルトに）
        var savePath = getDesktopPath() + fileName;

        // ファイルに書き込み
        var success = writeToFile(savePath, prtlContent);

        if (success) {
            return JSON.stringify({
                success: true,
                filename: fileName,
                path: savePath
            });
        } else {
            return JSON.stringify({ error: "ファイルの書き込みに失敗しました" });
        }

    } catch (e) {
        return JSON.stringify({ error: e.toString() });
    }
}

/**
 * タイトルからデータを抽出
 */
function extractTitleData(clip) {
    var data = {
        name: clip.name,
        start: clip.start.seconds,
        end: clip.end.seconds,
        duration: clip.end.seconds - clip.start.seconds,
        components: []
    };

    try {
        var projectItem = clip.projectItem;

        // クリップのコンポーネントを取得
        if (clip.components && clip.components.numItems > 0) {
            for (var i = 0; i < clip.components.numItems; i++) {
                var component = clip.components[i];
                var componentData = extractComponentData(component);
                if (componentData) {
                    data.components.push(componentData);
                }
            }
        }

        // プロジェクトアイテムからメタデータを取得
        if (projectItem) {
            data.projectItemName = projectItem.name;
            data.mediaPath = projectItem.getMediaPath();
        }

    } catch (e) {
        // エラーが発生しても基本データは返す
        data.extractError = e.toString();
    }

    return data;
}

/**
 * コンポーネントからデータを抽出
 */
function extractComponentData(component) {
    try {
        var data = {
            displayName: component.displayName,
            properties: []
        };

        // プロパティを取得
        if (component.properties && component.properties.numItems > 0) {
            for (var i = 0; i < component.properties.numItems; i++) {
                var prop = component.properties[i];
                data.properties.push({
                    displayName: prop.displayName,
                    value: getPropertyValue(prop)
                });
            }
        }

        return data;
    } catch (e) {
        return null;
    }
}

/**
 * プロパティの値を取得
 */
function getPropertyValue(prop) {
    try {
        // プロパティタイプに応じて値を取得
        if (prop.getValue) {
            var value = prop.getValue();
            if (typeof value !== 'undefined') {
                return value.toString();
            }
        }
        return "";
    } catch (e) {
        return "";
    }
}

/**
 * PRTLファイルのコンテンツを生成
 */
function generatePRTLContent(titleData) {
    var xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<PremiereData Version="3">\n';
    xml += '  <Title>\n';
    xml += '    <Name>' + escapeXML(titleData.name) + '</Name>\n';
    xml += '    <Duration>' + titleData.duration + '</Duration>\n';

    // コンポーネントデータを出力
    if (titleData.components && titleData.components.length > 0) {
        xml += '    <Components>\n';
        for (var i = 0; i < titleData.components.length; i++) {
            var component = titleData.components[i];
            xml += '      <Component>\n';
            xml += '        <DisplayName>' + escapeXML(component.displayName) + '</DisplayName>\n';

            if (component.properties && component.properties.length > 0) {
                xml += '        <Properties>\n';
                for (var j = 0; j < component.properties.length; j++) {
                    var prop = component.properties[j];
                    xml += '          <Property>\n';
                    xml += '            <Name>' + escapeXML(prop.displayName) + '</Name>\n';
                    xml += '            <Value>' + escapeXML(prop.value) + '</Value>\n';
                    xml += '          </Property>\n';
                }
                xml += '        </Properties>\n';
            }

            xml += '      </Component>\n';
        }
        xml += '    </Components>\n';
    }

    // メタデータ
    xml += '    <Metadata>\n';
    xml += '      <ExportDate>' + new Date().toISOString() + '</ExportDate>\n';
    xml += '      <ExportTool>Legacy Title PRTL Exporter</ExportTool>\n';
    xml += '      <SourceName>' + escapeXML(titleData.projectItemName || titleData.name) + '</SourceName>\n';
    if (titleData.mediaPath) {
        xml += '      <MediaPath>' + escapeXML(titleData.mediaPath) + '</MediaPath>\n';
    }
    xml += '    </Metadata>\n';

    xml += '  </Title>\n';
    xml += '</PremiereData>\n';

    return xml;
}

/**
 * XML用の文字列エスケープ
 */
function escapeXML(str) {
    if (!str) return "";
    var s = str.toString();
    s = s.replace(/&/g, "&amp;");
    s = s.replace(/</g, "&lt;");
    s = s.replace(/>/g, "&gt;");
    s = s.replace(/"/g, "&quot;");
    s = s.replace(/'/g, "&apos;");
    return s;
}

/**
 * ファイル名をサニタイズ
 */
function sanitizeFileName(name) {
    var safe = name.replace(/[<>:"\/\\|?*]/g, "_");
    safe = safe.replace(/\s+/g, "_");
    return safe;
}

/**
 * デスクトップパスを取得
 */
function getDesktopPath() {
    var desktop = Folder.desktop;
    var path = desktop.fsName;

    // パスの最後にスラッシュを追加
    if (path.charAt(path.length - 1) !== "/" && path.charAt(path.length - 1) !== "\\") {
        path += "/";
    }

    return path;
}

/**
 * ファイルに書き込み
 */
function writeToFile(filePath, content) {
    try {
        var file = new File(filePath);

        // ファイルを書き込みモードで開く
        if (!file.open("w")) {
            return false;
        }

        // UTF-8で書き込み
        file.encoding = "UTF-8";
        file.write(content);
        file.close();

        return true;
    } catch (e) {
        return false;
    }
}
