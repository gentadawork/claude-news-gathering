以下の手順で日本のニュースを収集し、レポートを作成してください。

## 手順

1. 各種ニュースソースから下記のジャンルごとのニュースを抽出してください。  
2. ユーザーにとってのニュースの重要度を10点満点で評価して、重要度が8点以上のニュースを抽出してください。  
3. 重要度が高いニュースについて概要を説明してください。情報源のページURLも記載してください。  
4. まとめた内容をNotionのDB「news reports」にページとして追加してください。  

## 出力形式

- レポートタイトル: 「🌍 中東ニュースレポート YYYY-MM-DD」
- 各ニュースには重要度スコア（例: 9/10）を記載
- Notionのページタイトルも同形式にしてください

## ニュースソース

- [Al Jazeera - Middle East](https://www.aljazeera.com/middle-east/)
- [Al Jazeera - Economy](https://www.aljazeera.com/economy/)
- [Al Jazeera - Science and Technology](https://www.aljazeera.com/tag/science-and-technology/)
- [Al Jazeera - Climate Crisis](https://www.aljazeera.com/climate-crisis/)

## ジャンル

- 国際ニュース
- 経済ニュース
- IT技術関連ニュース
- AI関連ニュース
- 科学関連ニュース
- 環境関連ニュース

## 情報源URLのルール（重要）

- 各ニュースの情報源URLは、必ず**その記事固有のURL**（例: `https://www.aljazeera.com/news/yyyy/m/d/xxx` ）を記載してください。
- 「 `https://www.aljazeera.com/middle-east/` 」「 `https://www.aljazeera.com/economy/` 」などのセクション一覧ページのURLは使用しないでください。
- 記事の個別URLが不明な場合は、WebSearchでニュースタイトルを検索して正確な記事URLを取得してから記載してください。