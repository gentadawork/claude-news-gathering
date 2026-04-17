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
