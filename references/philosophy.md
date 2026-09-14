# Research Project OS の思想

## 目的

Research Project OSは、研究を「コードを置く場所」ではなく、問いから結論までの証拠鎖として管理するための運用モデルである。

```text
問い
  -> 仮説・計画
  -> Task / 実験 / 解析
  -> expected / observed
  -> evidence
  -> decision
  -> current state
  -> 次の行動
```

目標は、数週間後・数か月後に、別の人間またはAIが「何を、なぜ、どの条件で、どこまで確認したか」を再構成できることにある。

## 中核原則

1. **Gitを意味記録の正本にする** — Markdown/YAML/コード/設定をレビュー可能な履歴として残し、検索indexやContext Packは再生成可能な派生物とする。
2. **証拠を主張に結び付ける** — 作業完了ではなく、claim、入力、方法、expected、observed、validation stage、制限事項で完了を判定する。
3. **不確実性を隠さない** — `UNBOUND`、`PROVISIONAL`、`BLOCKED`を有効な状態として扱い、推測を確認済み事実へ昇格させない。
4. **時間を経た記録を消さない** — 誤りや方針変更は上書きではなく、訂正・反証・`supersedes`として追跡する。
5. **計画と実行を分離する** — WPは目的と依存関係、Taskは一つの実行単位、Gateは進行可否、Evidenceは完了根拠を表す。
6. **AIは提案者であり、正本の所有者ではない** — AIは調査・実装・要約を行えるが、正式決定、外部送信、公開、hardware操作は承認境界に置く。
7. **実行環境を明示する** — 同じprojectを複数サーバで扱う場合、node、role、capability、restriction、commit、tool versionを記録する。
8. **最小限の文脈だけを渡す** — AIには目的に必要なContext Packだけを渡し、秘密、生データ、無関係なproject情報を含めない。
9. **失敗を成果として保存する** — FAIL、PARTIAL、INCONCLUSIVE、NOT_RUNを消さず、停止条件と次の切り分けを残す。
10. **人間の判断を効率化するが、置き換えない** — OSは判断材料を整えるためのもので、研究上の価値判断や責任を自動化しない。

## 境界

Project OSは一つの研究プロジェクトを扱う。複数projectの優先順位、予算、研究ポートフォリオ全体の判断は将来のPortfolio OSの責務とし、現行scopeには含めない。

## 設計上の帰結

- 各projectにstableな`project_id`、Task ID、Evidence ID、Artifact IDを持たせる。
- project repositoryは一つの正本とし、ChatGPT/Codex/他agentは作業セッションとして扱う。
- リモートサーバはprojectの複製ではなく、役割と能力を持つexecution nodeとして記録する。
- raw data、credentials、生成build directoryはGit外に置き、locator、hash、version、access policyだけをGitに保存する。
