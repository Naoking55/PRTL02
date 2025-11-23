#!/bin/bash

# CSInterface.jsをダウンロードするスクリプト

echo "CSInterface.jsをダウンロードしています..."

curl -o client/CSInterface.js https://raw.githubusercontent.com/Adobe-CEP/CEP-Resources/master/CEP_10.x/CSInterface.js

if [ $? -eq 0 ]; then
    echo "✓ CSInterface.jsのダウンロードが完了しました"
else
    echo "✗ ダウンロードに失敗しました"
    exit 1
fi
