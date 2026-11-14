# CTMarket-Index

ClassSuite「工具市场」的公共索引仓库。它把 GitHub 上带[`class-toolkit`](https://github.com/topics/class-toolkit) topic 的仓库整理成一份[`index.json`](docs/index-format.md)，供 ClassSuite 的「工具市场」页面浏览。

## 收录规则

- 仓库公开可见，并添加 topic `class-toolkit`
- 索引按星数从高到低排列
- 索引每日自动更新

## 如何让你的项目出现在市场里

1. 打开仓库首页，进入右侧 **About → Topics**
2. 添加 `class-toolkit`
3. 等待下一次索引更新即可

## 插件如何读取

插件默认从以下地址获取索引：

```
https://raw.githubusercontent.com/ClassToolsLab/CTMarket-Index/CTMarket-Index/index.json
```

GitHub 无法访问时会自动回退到 jsDelivr：

```
https://cdn.jsdelivr.net/gh/ClassToolsLab/CTMarket-Index@CTMarket-Index/index.json
```

## 索引格式

字段说明与示例见 [index-format.md](docs/index-format.md)。

## 脚本

`scripts/` 下提供索引构建与本地抓取脚本，用法与参数说明见 [scripts.md](docs/scripts.md)。

## 相关项目

- [ClassToolsLab/ClassroomTools-Market](https://github.com/ClassToolsLab/ClassroomTools-Market)：工具市场插件
- [ClassToolsLab/ClassSuite](https://github.com/ClassToolsLab/ClassSuite)：班级软件集合

## 许可证

- 代码（`scripts/`、`.github/`）：[MIT 许可证](LICENSE)
- 索引数据（`index.json`）：[CC0-1.0 许可证](LICENSE-DATA)
