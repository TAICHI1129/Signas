# Signas
File digital signature

Signas は Python で動作する軽量電子署名サービスです。
ファイル改ざん検知と署名者確認が可能。リネームされてもハッシュ値で検出できます。

## 特徴

* ファイル改ざん検知
* 署名者の確認
* CMD / ターミナルで動作
* 依存ライブラリなし（標準 Python のみ）
* .signas ファイルに署名者名（必須）と GitHub リンク（任意）を記録

## インストール

pip install . を実行してインストールします。

## CLI コマンド

署名する場合は、`signas sign <file> <name>` と入力します。
GitHub リンクも追加する場合は、`signas sign <file> <name> [github]` とします。

ファイルの SHA-256 ハッシュを確認する場合は、`signas hash <file>` と入力します。

署名の検証（リネームされたファイルでも確認可能）を行う場合は、`signas verify <file> <signas_file>` と入力します。

## .signas ファイル仕様

.signas ファイルは JSON 形式で保存されます。必須項目は "hash"（SHA-256 ハッシュ値）と "signer"（署名者名）です。
任意項目として "github"（GitHub リンク）を追加できます。さらに元のファイル名は "original_filename" として記録されます。

例として、次のような内容になります：
```
hash: 5a51be41913d0de774d527c684ee849205b10672b65dcfdf6023dca04cc10217
signer: TAICHI1129
original_filename: example.txt
github: [https://github.com/TAICHI1129](https://github.com/TAICHI1129)
```

## 使用例

* 名前のみで署名する場合
```
signas sign example.txt TAICHI1129
```

* 名前と GitHub リンクを付けて署名する場合
```
signas sign example.txt TAICHI1129 [https://github.com/TAICHI1129](https://github.com/TAICHI1129)
```

* ファイルのハッシュを確認する場合
```
signas hash example.txt
```

* ファイル名を変更しても署名を確認する場合
```
signas verify renamed_example.txt example.signas
```
