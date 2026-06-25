以下の手順で、今週分のニュースレポートを国別にポッドキャスト原稿へ再編集し、AivisSpeechで音声化したうえでNotionに記録してください。

## 対象国

- 🇯🇵 日本（Notionページタイトルに「日本」を含む）
- 🇺🇸 アメリカ（Notionページタイトルに「アメリカ」を含む）
- 🌍 中東（Notionページタイトルに「中東」を含む）

## 事前準備

起動直後はNotionのMCPツールが「接続中」で使えない場合があります。最初に `ToolSearch` で `"notion"` を検索し、ツールが使用可能になっていることを確認してから手順を開始してください（Google Driveへのアップロードは専用スクリプトを使うため、Google Drive MCPは不要です）。

## 手順（国ごとに繰り返す）

1. NotionのDB「news reports」（データソース: `collection://33c7a18f-094b-806d-9a61-000bec7b42f9`）に対し、`notion-query-data-sources` のSQLモードで以下を抽出してください。
   - `名前` にその国名を含む
   - `作成日時` が直近7日以内（今日を含む。今週の月・水・金に作成されたレポートを想定）
2. 抽出した各ページを `notion-fetch` で全文取得してください。
3. 取得した記事群を、1つの自然なポッドキャスト原稿（日本語、導入→本編→締めの構成）に再編集してください。単なる記事の連結ではなく、聞いて分かりやすい話し言葉に書き直してください。重要度が高いニュースを優先し、重複する話題はまとめてください。
4. 原稿を `E:\workspace\claude-news-gathering\transcripts\<country_en>_weekly_<YYYY-MM-DD>.md` に保存してください（`country_en` は `japan` / `usa` / `middle_east`）。
5. Bashツールで以下を実行し、音声を合成してください（AivisSpeechエンジンが起動していない場合は失敗するので、その場合はこの国をスキップし、エラー内容を出力して次の国に進んでください）。

   ```
   aivis-tts E:\workspace\claude-news-gathering\transcripts\<country_en>_weekly_<YYYY-MM-DD>.md --output E:\workspace\claude-news-gathering\outputs\<country_en>_weekly_<YYYY-MM-DD>.wav --language ja
   ```

6. `.wav` は数十MBになり、base64エンコードしてMCPツール呼び出しのパラメータに渡すのはコンテキスト上現実的でないため、ffmpegで128kbpsのmp3に変換してください。

   ```
   ffmpeg -y -i E:\workspace\claude-news-gathering\outputs\<country_en>_weekly_<YYYY-MM-DD>.wav -codec:a libmp3lame -b:a 128k E:\workspace\claude-news-gathering\outputs\<country_en>_weekly_<YYYY-MM-DD>.mp3
   ```

   続けて、`E:\workspace\claude-news-gathering\scripts` ディレクトリに `cd` してから以下を実行し、Google Driveに直接アップロードしてください（このスクリプトはファイル内容をClaudeのコンテキストに通さず直接アップロードし、`webViewLink` を標準出力に1行だけ出力します）。

   ```
   python upload_to_drive.py E:\workspace\claude-news-gathering\outputs\<country_en>_weekly_<YYYY-MM-DD>.mp3
   ```

   出力された `webViewLink` をそのまま次のステップで使ってください。ffprobe等による追加の検証は不要です。スクリプトの終了コードが0で `webViewLink` が出力されていれば成功として次に進んでください。
7. `notion-create-pages` で「news reports」データソース配下に新規ページを作成してください。
   - 名前: `🎙️ <国旗emoji> <国名>週次ポッドキャスト原稿 <YYYY-MM-DD>`
   - `日付`: 今日の日付
   - タグ: `情報_ニュース`
   - content: **手順4で保存した `transcripts\<country_en>_weekly_<YYYY-MM-DD>.md` の内容を `Read` ツールで読み込み、そのまま使ってください（記憶から再構成したり書き直したりしないこと。他国の原稿の内容を混在させないこと）。** その全文に続けて、末尾に `🔊 音声: [Google Driveで再生](<webViewLink>)` を追記

## 完了報告

3カ国すべて処理したら、各国の成否（成功した場合は生成したNotionページ名とDriveリンク、失敗した場合は理由）を一覧にして出力してください。
