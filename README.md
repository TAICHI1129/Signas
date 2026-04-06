# Signas
安全なファイルデジタル署名 & 整合性検証ツールSignas は、Python で動作する軽量な電子署名ツールです。

RSA (2048-bit) 非対称暗号方式を採用しており、ファイルの「改ざん検知」だけでなく、「署名者の真正性」を確実に保証します。

## 主な特徴
RSA デジタル署名: 署名ファイル（.signas）自体の偽造を防止します。

強力な改ざん検知: SHA-256 とストリーミング読み込みにより、数GBの巨大なファイルも低メモリで検証可能。

身元証明: 署名者の名前と、任意で GitHub プロフィールを紐付け可能。

監査ログ (Audit Log): すべての署名・検証の履歴を audit.log に自動記録。

パスワード保護: 秘密鍵をパスフレーズで暗号化し、盗難時の不正署名を防ぎます。

## インストール
```
pip install signas
```
(注意: RSA機能のために cryptography ライブラリが必要です)

## 使い方 (CLI コマンド)
1. 鍵の生成署名を始める前に、あなた専用の鍵ペアを作成します。
```
signas genkey
```

private_key.pem: あなたの秘密鍵です（絶対に他人に渡さないでください！）。

public_key.pem: あなたの公開鍵です（検証者に渡してください）。

2. ファイルに署名するファイルが「本物」であることを証明する署名ファイルを作成します。
```
signas sign <file> <signer_name> [github_url]
```
例: signas sign data.zip TAICHI1129 https://github.com3. 

ファイルを検証するファイルが改ざんされていないか、署名が正しいかを確認します。
```
signas verify <file>
```
※実行には対象のファイル、<file>.signas、および署名者の public_key.pem が必要です。

## .signas ファイルの仕様
.signas は以下のデータを含む JSON 形式です：

info: ファイルの SHA-256 ハッシュ値、署名者名、GitHub リンク。

signature: メタデータに対して作成された Base64 エンコード済みの RSA-PSS 署名。

例:
```
{
  "info": {
    "hash": "5a51be41913d0...",
    "signer": "TAICHI1129",
    "github": "https://github.com"
  },
  "signature": "MIIBIjANBgkqh..."
}
```

セキュリティ上の注意秘密鍵の管理: private_key.pem やそのパスワードを紛失すると、二度と署名ができなくなります。

公開鍵の配布: 検証者は、信頼できるルートから入手した公開鍵を使用してください。

## 実行コード例

1. 準備：鍵ペアの生成署名活動を始める前に、一度だけ実行します。
```
signas genkey
```
入力内容: 秘密鍵を保護するためのパスワード（4文字以上）。

生成物: private_key.pem（署名用）、public_key.pem（配布用）。

----

2. 署名：ファイルに電子署名を付与ファイルが「自分のものであること」と「改ざんされていないこと」を証明します。
  
例A：名前のみで署名する場合
```
signas sign report.pdf "Taro Yamada"
```

例B：GitHubリンクを含めて署名する場合
```
signas sign software.zip "TAICHI1129" "https://github.com"
```

入力内容: genkey で設定したパスワード。

生成物: report.pdf.signas または software.zip.signas。

----

3. 検証：ファイルの真正性をチェック受け取ったファイルが本物かどうかを確認します。
   
同じフォルダに 対象ファイル、.signasファイル、public_key.pem がある状態で実行します。

```
signas verify software.zip
```
成功時: ✅ Verification Successful と表示され、署名者名とGitHubリンクが表示されます。

失敗時（改ざんあり）: ❌ Verification Failed: File content has been tampered with! と表示されます。

失敗時（署名の偽造）: ❌ Verification Failed: Invalid or forged signature. と表示されます。

----

4. 履歴の確認（ログ）いつ、どのファイルに対して操作を行ったかを確認します。
```
#Windows
type audit.log

# Mac / Linux
cat audit.log
```
表示例: [2024-05-20 12:00:00] ACTION: SIGN | FILE: software.zip | STATUS: SUCCESS | Signed by TAICHI1129

----

5. ハッシュ値のみの確認署名を作らずに、単純にファイルのSHA-256値だけを見たい場合です。
```
signas hash sample.txt
```

----

## For the Windows Users
If `signas` command does not work:

Use:
python -m signas.cli
