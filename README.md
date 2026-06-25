# claude-news-gathering

Claude Code (CLI) でスケジュール稼働するニュース収集エージェント。

## 使い方

```shell
claude
```

でエージェントを開始し、

```shell
/schedule create news-gathering-me.md を使った中東ニュース収集エージェント。毎朝3:00 (JST) 実行。プロンプトにスキルの内容を埋め込む。
```

等のようにしてスケジュールタスクを作成する。
公開レポジトリとしてskillを公開していれば「プロンプトにスキルの内容を埋め込む。」ではなく「{{url}} のリポジトリにあるskill `` を参照。」とすることができる（らしい）。

## 週次ポッドキャスト自動化

`skills/weekly-podcast.md` は、毎週土曜12:00に1週間分（月・水・金）の国別ニュースレポートをポッドキャスト原稿に再編集し、[TextToSpeech](../TextToSpeech) リポジトリの `aivis-tts` CLI（AivisSpeech）で音声化し、Google Driveにアップロードしたうえで、音声リンク付きの原稿ページをNotionの「news reports」DBに追加するスキルです。

AivisSpeechエンジンはユーザーのローカルPC（`http://localhost:10101`）でしか動作しないため、このルーチンだけは他のスキル（クラウドの `/schedule`）と異なり、**ローカルPC上で常駐起動するWindowsタスクスケジューラ**から実行します。

### 構成

- `skills/weekly-podcast.md`: ヘッドレスClaude Codeに渡すプロンプト本文（Notion抽出・原稿再編集・音声合成・mp3変換・Driveアップロード・Notionページ作成の手順）
- `scripts/run_weekly_podcast.ps1`: タスクスケジューラから呼ばれるラッパー。AivisSpeechエンジンの起動確認後、`claude -p` を実行する
- `scripts/upload_to_drive.py`: 生成した音声ファイルをGoogle Drive APIで直接アップロードするスクリプト。`.secrets/token.json` のOAuthトークンを使い、Claudeのコンテキストやツール呼び出しにファイル内容を一切通さない（数MBのbase64データをMCP経由でやり取りするのは非現実的なため）
- `scripts/google_drive_auth_setup.py`: 上記トークンを発行する、初回だけ実行する対話的セットアップスクリプト
- `transcripts/` `outputs/` `logs/`: 生成される原稿・音声・実行ログ（gitignore対象）
- `.claude/settings.local.json`: このリポジトリの無人実行が使うツールだけを許可するリスト。グローバルの権限バイパスモードはこのマシンでは無効化されているため、ここに許可リストを登録することで `claude -p` を承認待ちなしで実行できるようにしている
- `.secrets/`: Google OAuthクライアント情報・トークン（gitignore対象、絶対にコミットしない）

### 事前準備

1. AivisSpeech Engineを起動しておく（スクリプトは自動起動しません。未起動時はログにエラーを残して終了します）
2. ローカルで `claude` CLIにログイン済みであること
3. Notion MCPが連携済みであること
4. [TextToSpeech](../TextToSpeech) リポジトリの `aivis-tts` コマンドが利用可能であること（`run_weekly_podcast.ps1` がvenvの `Scripts` ディレクトリを実行時にPATHへ追加する）
5. `ffmpeg` がPATHから実行できること（wav→mp3変換に使用）
6. Google Driveアップロード用のOAuthトークンを発行しておくこと（初回のみ）:
   1. https://console.cloud.google.com/ でプロジェクトを作成し、「Google Drive API」を有効化する
   2. 「APIとサービス」→「認証情報」で OAuth クライアント ID（アプリケーションの種類: デスクトップアプリ）を作成する
   3. ダウンロードしたJSONを `E:\workspace\claude-news-gathering\.secrets\client_secret.json` として保存する
   4. `python scripts/google_drive_auth_setup.py` を実行し、ブラウザでGoogleアカウントにログインしてアクセスを許可する（`.secrets/token.json` が作成される）
   5. 以降は `scripts/upload_to_drive.py` が自動でトークンを更新しながら無人アップロードする

### タスクスケジューラへの登録

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"E:\workspace\claude-news-gathering\scripts\run_weekly_podcast.ps1`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 12:00pm
Register-ScheduledTask -TaskName "WeeklyNewsPodcast" -Action $action -Trigger $trigger -RunLevel Limited
```

登録後、即時実行して動作確認する場合は `Start-ScheduledTask -TaskName "WeeklyNewsPodcast"` を使います。
