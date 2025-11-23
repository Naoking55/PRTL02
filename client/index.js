/* global CSInterface */

let csInterface;
let legacyTitles = [];
let selectedTitleIndex = -1;

function init() {
    csInterface = new CSInterface();

    document.getElementById('scanBtn').addEventListener('click', scanTimeline);
    document.getElementById('exportBtn').addEventListener('click', exportSelected);
    document.getElementById('exportAllBtn').addEventListener('click', exportAll);

    updateStatus('準備完了');
}

function updateStatus(message, type = 'info') {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = type;
}

function scanTimeline() {
    updateStatus('タイムラインをスキャン中...', 'info');
    document.getElementById('scanBtn').disabled = true;

    csInterface.evalScript('scanForLegacyTitles()', function(result) {
        document.getElementById('scanBtn').disabled = false;

        if (result === 'EvalScript error.') {
            updateStatus('エラー: ExtendScriptの実行に失敗しました', 'error');
            return;
        }

        try {
            const response = JSON.parse(result);

            if (response.error) {
                updateStatus('エラー: ' + response.error, 'error');
                return;
            }

            legacyTitles = response.titles || [];

            if (legacyTitles.length === 0) {
                updateStatus('レガシータイトルが見つかりませんでした', 'warning');
                document.getElementById('exportBtn').disabled = true;
                document.getElementById('exportAllBtn').disabled = true;
                document.getElementById('titleList').innerHTML = '<div style="color: #a0a0a0;">タイトルなし</div>';
            } else {
                updateStatus(`${legacyTitles.length}個のレガシータイトルを検出しました`, 'success');
                document.getElementById('exportAllBtn').disabled = false;
                displayTitles();
            }
        } catch (e) {
            updateStatus('エラー: 結果の解析に失敗しました - ' + e.message, 'error');
        }
    });
}

function displayTitles() {
    const titleList = document.getElementById('titleList');
    titleList.innerHTML = '';

    legacyTitles.forEach(function(title, index) {
        const titleDiv = document.createElement('div');
        titleDiv.className = 'title-item';
        titleDiv.textContent = `${index + 1}. ${title.name} (Track ${title.trackIndex + 1})`;
        titleDiv.onclick = function() {
            selectTitle(index);
        };
        titleList.appendChild(titleDiv);
    });
}

function selectTitle(index) {
    selectedTitleIndex = index;

    const items = document.querySelectorAll('.title-item');
    items.forEach(function(item, i) {
        if (i === index) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });

    document.getElementById('exportBtn').disabled = false;
    updateStatus(`選択: ${legacyTitles[index].name}`, 'info');
}

function exportSelected() {
    if (selectedTitleIndex < 0 || selectedTitleIndex >= legacyTitles.length) {
        updateStatus('エラー: タイトルが選択されていません', 'error');
        return;
    }

    const title = legacyTitles[selectedTitleIndex];
    exportTitle(title, selectedTitleIndex);
}

function exportAll() {
    updateStatus(`${legacyTitles.length}個のタイトルをエクスポート中...`, 'info');
    document.getElementById('exportAllBtn').disabled = true;

    let exportCount = 0;
    let errorCount = 0;

    function exportNext(index) {
        if (index >= legacyTitles.length) {
            document.getElementById('exportAllBtn').disabled = false;
            if (errorCount === 0) {
                updateStatus(`完了: ${exportCount}個のタイトルをエクスポートしました`, 'success');
            } else {
                updateStatus(`完了: ${exportCount}個成功、${errorCount}個失敗`, 'warning');
            }
            return;
        }

        const title = legacyTitles[index];
        const params = JSON.stringify({
            trackIndex: title.trackIndex,
            clipIndex: title.clipIndex,
            index: index
        });

        csInterface.evalScript(`exportLegacyTitleToPRTL(${params})`, function(result) {
            try {
                const response = JSON.parse(result);
                if (response.success) {
                    exportCount++;
                } else {
                    errorCount++;
                }
            } catch (e) {
                errorCount++;
            }

            updateStatus(`エクスポート中... (${index + 1}/${legacyTitles.length})`, 'info');
            exportNext(index + 1);
        });
    }

    exportNext(0);
}

function exportTitle(title, index) {
    updateStatus(`エクスポート中: ${title.name}`, 'info');
    document.getElementById('exportBtn').disabled = true;

    const params = JSON.stringify({
        trackIndex: title.trackIndex,
        clipIndex: title.clipIndex,
        index: index
    });

    csInterface.evalScript(`exportLegacyTitleToPRTL(${params})`, function(result) {
        document.getElementById('exportBtn').disabled = false;

        if (result === 'EvalScript error.') {
            updateStatus('エラー: ExtendScriptの実行に失敗しました', 'error');
            return;
        }

        try {
            const response = JSON.parse(result);

            if (response.success) {
                updateStatus(`成功: ${response.filename} を保存しました\n保存先: ${response.path}`, 'success');
            } else {
                updateStatus('エラー: ' + (response.error || '不明なエラー'), 'error');
            }
        } catch (e) {
            updateStatus('エラー: 結果の解析に失敗しました - ' + e.message, 'error');
        }
    });
}

document.addEventListener('DOMContentLoaded', init);
