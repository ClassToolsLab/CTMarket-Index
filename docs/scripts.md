# 脚本说明

`scripts/` 下有两个 Python 脚本，均只依赖标准库。它们最终都会生成同一种
`index.json`（格式见 [index-format.md](index-format.md)）。

## build_market.py

用于 GitHub Actions 的正式构建脚本：按 topic 拉取仓库并写出索引。

```bash
python scripts/build_market.py --out build/index.json
```

| 参数           | 默认值                    | 说明                                   |
| -------------- | ------------------------- | -------------------------------------- |
| `--out`        | 必填                      | 输出的 `index.json` 路径               |
| `--topic`      | `$MARKET_TOPIC`，缺省 `class-toolkit` | 要聚合的 GitHub topic       |
| `--limit`      | `$MARKET_LIMIT`，缺省 `200` | 最多保留的仓库数量                  |
| `--token`      | `$GITHUB_TOKEN`           | GitHub Token，建议提供以避免限流       |
| `--allow-empty`| 关闭                      | 没有结果时也写出空索引，而不是报错退出 |

行为要点：

- 调用 GitHub Search API，按星数降序，每页最多 100 条
- 翻页之间间隔 1 秒；遇到限流或网络错误会自动退避重试
- 默认上限 200 条，适合定时任务
- 没有匹配结果时默认以非 0 退出，避免用空索引覆盖线上数据

## fetch_local.py

本地调试脚本，复用 `build_market.py` 的请求与构建逻辑，但支持一次拉取更多仓库。

```bash
python scripts/fetch_local.py --limit 1000 --out build/index.json
```

| 参数           | 默认值                    | 说明                                     |
| -------------- | ------------------------- | ---------------------------------------- |
| `--out`        | `build/index.json`        | 输出路径                                 |
| `--topic`      | `$MARKET_TOPIC`，缺省 `class-toolkit` | 要聚合的 GitHub topic         |
| `--limit`      | `0`（即 1000）            | 最多保留数量；超过 1000 会被截断         |
| `--token`      | `$GITHUB_TOKEN`           | GitHub Token，建议提供                   |
| `--allow-empty`| 关闭                      | 没有结果时也写出空索引                   |

行为要点：

- 按 100 条/页翻页，可突破正式脚本的 200 条限制
- GitHub Search API 单次查询最多返回 1000 条，因此上限为 1000
- 未设置 `GITHUB_TOKEN` 时搜索接口约 10 次/分钟限流，脚本会自动等待重试
- 成功后打印总数与前 5 个仓库，便于快速确认结果

## 选择建议

- 日常更新、CI：用 `build_market.py`，控制在 200 条内，速度快、限流风险低
- 本地核对或需要更大范围：用 `fetch_local.py`
- 生成的索引可以直接在插件「仓库源 → 本地文件」中加载预览
