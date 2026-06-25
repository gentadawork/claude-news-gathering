# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## リポジトリの概要

Claude Code CLIでスケジュール稼働するニュース収集エージェントのワークスペース。基本的にコードは存在せず、スキル定義ファイル（プロンプト）のみで構成される。

例外として `scripts/` 配下のみコードを含む（`run_weekly_podcast.ps1`, `upload_to_drive.py`, `google_drive_auth_setup.py`）。これはAivisSpeechによる音声合成がユーザーのローカルPC上のエンジンに依存するため、クラウドの `/schedule` ルーチンではなく、OS（Windowsタスクスケジューラ）からローカルでヘッドレスのClaude Codeを起動する必要があり、また生成した音声ファイルをClaudeのコンテキストを経由させずにGoogle Driveへ直接アップロードする必要があるため。詳細は README.md の「週次ポッドキャスト自動化」を参照。

## スキル定義

`skills/` ディレクトリに地域別のニュース収集スキルが格納されている。

| ファイル | 対象地域 | ニュースソース |
|---|---|---|
| `news-gathering-jp.md` | 日本 | Yahoo! Japan ニュース |
| `news-gathering-us.md` | アメリカ | CNN |
| `news-gathering-me.md` | 中東 | Al Jazeera |
| `weekly-podcast.md` | 日本/アメリカ/中東（週次） | news reports DB内の既存ページ（再編集） |

## スキルの実行方法

各スキルファイルの内容を `/skill` として登録して呼び出す、またはファイルの内容をそのままプロンプトとして使用する。

## スキルの共通フロー

1. 指定ニュースソース（WebFetch/WebSearch）からジャンル別ニュースを取得
2. 重要度を10点満点で評価し、8点以上を抽出
3. 概要と**記事固有のURL**をまとめる（セクション一覧URLは不可）
4. NotionのDB「news reports」にページとして追加（Notion MCP使用）

## Notionへの出力形式

- 日本: `🇯🇵 日本ニュースレポート YYYY-MM-DD`
- アメリカ: `🇺🇸 アメリカニュースレポート YYYY-MM-DD`
- 中東: `🌍 中東ニュースレポート YYYY-MM-DD`

各ニュースに重要度スコア（例: `9/10`）を付記する。

## 情報源URLの扱い（重要）

記事固有のURLが不明な場合は、WebSearchでニュースタイトルを検索して正確なURLを取得してから記載すること。セクション一覧ページのURLは絶対に使用しない。
