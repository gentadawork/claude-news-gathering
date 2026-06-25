"""
保存済みのOAuthトークン（.secrets/token.json、google_drive_auth_setup.py で発行）を使い、
指定したローカルファイルをGoogle Driveの専用フォルダにアップロードし、
webViewLink を標準出力に1行だけ出力する。

無人実行（ヘッドレスClaude含む）から呼び出すことを想定しており、
ファイル内容をClaudeのコンテキストやMCPツール呼び出しに通さずに直接アップロードする。

Usage:
    python upload_to_drive.py <file_path>
"""

from __future__ import annotations

import json
import mimetypes
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SECRETS_DIR = REPO_ROOT / ".secrets"
TOKEN_PATH = SECRETS_DIR / "token.json"

TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
DRIVE_FILES_ENDPOINT = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD_ENDPOINT = "https://www.googleapis.com/upload/drive/v3/files"
FOLDER_NAME = "週次ニュースポッドキャスト"
FOLDER_MIME = "application/vnd.google-apps.folder"


def _load_token() -> dict:
    if not TOKEN_PATH.exists():
        raise SystemExit(f"error: {TOKEN_PATH} が見つかりません。先に google_drive_auth_setup.py を実行してください。")
    return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))


def _get_access_token(token_data: dict) -> str:
    body = urllib.parse.urlencode(
        {
            "client_id": token_data["client_id"],
            "client_secret": token_data["client_secret"],
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = urllib.request.Request(TOKEN_ENDPOINT, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]


def _find_or_create_folder(access_token: str) -> str:
    query = urllib.parse.urlencode(
        {
            "q": f"name='{FOLDER_NAME}' and mimeType='{FOLDER_MIME}' and trashed=false",
            "fields": "files(id,name)",
        }
    )
    req = urllib.request.Request(f"{DRIVE_FILES_ENDPOINT}?{query}")
    req.add_header("Authorization", f"Bearer {access_token}")
    with urllib.request.urlopen(req) as resp:
        files = json.loads(resp.read().decode("utf-8")).get("files", [])
    if files:
        return files[0]["id"]

    metadata = json.dumps({"name": FOLDER_NAME, "mimeType": FOLDER_MIME}).encode("utf-8")
    req = urllib.request.Request(DRIVE_FILES_ENDPOINT, data=metadata, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["id"]


def _upload_file(access_token: str, folder_id: str, file_path: Path) -> str:
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    metadata = json.dumps({"name": file_path.name, "parents": [folder_id]}).encode("utf-8")

    init_req = urllib.request.Request(
        f"{DRIVE_UPLOAD_ENDPOINT}?uploadType=resumable&fields=id,webViewLink",
        data=metadata,
        method="POST",
    )
    init_req.add_header("Authorization", f"Bearer {access_token}")
    init_req.add_header("Content-Type", "application/json; charset=UTF-8")
    init_req.add_header("X-Upload-Content-Type", mime_type)
    with urllib.request.urlopen(init_req) as resp:
        session_uri = resp.headers["Location"]

    file_bytes = file_path.read_bytes()
    put_req = urllib.request.Request(session_uri, data=file_bytes, method="PUT")
    put_req.add_header("Content-Type", mime_type)
    put_req.add_header("Content-Length", str(len(file_bytes)))
    with urllib.request.urlopen(put_req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    return result["webViewLink"]


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python upload_to_drive.py <file_path>", file=sys.stderr)
        return 2

    file_path = Path(argv[0])
    if not file_path.exists():
        print(f"error: file not found: {file_path}", file=sys.stderr)
        return 1

    token_data = _load_token()
    access_token = _get_access_token(token_data)
    folder_id = _find_or_create_folder(access_token)
    link = _upload_file(access_token, folder_id, file_path)
    print(link)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
