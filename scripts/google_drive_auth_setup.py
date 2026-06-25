"""
Google Drive アップロード用OAuthトークンを取得する、一度だけ実行する対話的セットアップスクリプト。

事前準備（ユーザーが行う）:
1. https://console.cloud.google.com/ でプロジェクトを作成（既存のものでも可）
2. 「APIとサービス」→「ライブラリ」で Google Drive API を有効化
3. 「APIとサービス」→「認証情報」→「OAuth クライアント ID を作成」
   - アプリケーションの種類: デスクトップアプリ
   - 作成後、JSONをダウンロードし、このリポジトリの
     .secrets/client_secret.json として保存する
4. このスクリプトを実行する:
     python scripts/google_drive_auth_setup.py
   ブラウザが開くのでGoogleアカウントでログインし、アクセスを許可する。
   成功すると .secrets/token.json にリフレッシュトークンが保存され、
   以降は scripts/upload_to_drive.py が無人で使えるようになる。

スコープは drive.file（このアプリが作成したファイルのみにアクセス）に限定している。
"""

from __future__ import annotations

import http.server
import json
import sys
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SECRETS_DIR = REPO_ROOT / ".secrets"
CLIENT_SECRET_PATH = SECRETS_DIR / "client_secret.json"
TOKEN_PATH = SECRETS_DIR / "token.json"

REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/"
SCOPE = "https://www.googleapis.com/auth/drive.file"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    code: str | None = None

    def do_GET(self) -> None:  # noqa: N802 (http.server API name)
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.code = params.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<html><body>認証が完了しました。このタブは閉じてください。</body></html>".encode("utf-8"))

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass


def main() -> int:
    if not CLIENT_SECRET_PATH.exists():
        print(f"error: {CLIENT_SECRET_PATH} が見つかりません。READMEの手順でOAuthクライアントを作成し配置してください。", file=sys.stderr)
        return 1

    client_secret_data = json.loads(CLIENT_SECRET_PATH.read_text(encoding="utf-8"))
    installed = client_secret_data.get("installed") or client_secret_data.get("web")
    if not installed:
        print("error: client_secret.json の形式が想定と異なります（'installed' キーが必要）。", file=sys.stderr)
        return 1

    client_id = installed["client_id"]
    client_secret = installed["client_secret"]

    auth_url = AUTH_ENDPOINT + "?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
        }
    )

    print("ブラウザを開きます。Googleアカウントでログインし、アクセスを許可してください。")
    print(auth_url)
    webbrowser.open(auth_url)

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), _CallbackHandler)
    server.handle_request()

    code = _CallbackHandler.code
    if not code:
        print("error: 認証コードを取得できませんでした。", file=sys.stderr)
        return 1

    token_request = urllib.parse.urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    req = urllib.request.Request(TOKEN_ENDPOINT, data=token_request, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        token_response = json.loads(resp.read().decode("utf-8"))

    refresh_token = token_response.get("refresh_token")
    if not refresh_token:
        print("error: refresh_token が返されませんでした。一度Googleアカウントのアプリ連携を解除してから再実行してください。", file=sys.stderr)
        return 1

    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(
        json.dumps(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"成功: {TOKEN_PATH} を保存しました。今後は upload_to_drive.py が無人で使えます。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
