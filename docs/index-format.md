# index.json 格式

市场索引是一份 UTF-8 编码的 JSON 文件，插件据此渲染「工具市场」列表。`schema` 只在
发生不兼容变更时递增。

## 示例

```json
{
    "schema": 1,
    "generated_at": "2026-11-14T04:00:00Z",
    "topic": "class-toolkit",
    "count": 2,
    "tools": [
        {
            "full_name": "owner/repo",
            "owner": "owner",
            "name": "repo",
            "description": "一个课堂工具",
            "html_url": "https://github.com/owner/repo",
            "homepage": "",
            "stars": 12,
            "forks": 3,
            "open_issues": 1,
            "watchers": 12,
            "license": "MIT",
            "language": "C++",
            "topics": ["class-toolkit"],
            "created_at": "2026-01-02T07:07:40Z",
            "updated_at": "2026-11-10T08:00:00Z",
            "pushed_at": "2026-11-13T14:11:26Z",
            "default_branch": "main",
            "archived": false,
            "size": 422,
            "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4"
        }
    ]
}
```

## 顶层字段

| 字段           | 类型     | 说明                                 |
| -------------- | -------- | ------------------------------------ |
| `schema`       | integer  | 格式版本，当前为 `1`                 |
| `generated_at` | string   | 生成时间，UTC 的 ISO-8601 时间       |
| `topic`        | string   | 索引对应的 GitHub topic              |
| `count`        | integer  | `tools` 中的条目数量                 |
| `tools`        | array    | 工具列表，按星数降序排列             |

## tools[] 字段

| 字段             | 类型     | 说明                                 |
| ---------------- | -------- | ------------------------------------ |
| `full_name`      | string   | `owner/repo`                         |
| `owner`          | string   | 仓库所属用户或组织                   |
| `name`           | string   | 仓库名                               |
| `description`    | string   | 仓库描述，可能为空                   |
| `html_url`       | string   | 仓库主页地址                         |
| `homepage`       | string   | 项目主页，可能为空                   |
| `stars`          | integer  | GitHub 星数                          |
| `forks`          | integer  | Fork 数量                            |
| `open_issues`    | integer  | 未关闭的 issue 数量                  |
| `watchers`       | integer  | watcher 数量                         |
| `license`        | string   | SPDX 标识或许可证名称，可能为空       |
| `language`       | string   | 主要语言，可能为空                   |
| `topics`         | string[] | 仓库的 topic 列表                    |
| `created_at`     | string   | 创建时间，UTC 的 ISO-8601 时间        |
| `updated_at`     | string   | 最近更新时间，UTC 的 ISO-8601 时间   |
| `pushed_at`      | string   | 最近推送时间，UTC 的 ISO-8601 时间   |
| `default_branch` | string   | 默认分支名，可能为空，缺省视为 `main` |
| `archived`       | boolean  | 仓库是否已归档                       |
| `size`           | integer  | 仓库体积（KB，GitHub 口径）          |
| `avatar_url`     | string   | 仓库所有者的头像地址                 |

## 使用建议

- 只依赖需要的字段，忽略未知字段
- `full_name` 与 `html_url` 是稳定标识
- 列表展示前可按 `stars` 或 `updated_at` 自行排序
