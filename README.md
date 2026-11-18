# 一棵圣诞树 · Christmas Tree (Python)

以 **Python** 为主体的动态粒子圣诞树。使用 Pygame 播放桌面动画，并提供独立 HTML 贺卡，方便直接转发给朋友。

## 运行 Python 动画

需要 Python 3.10 或更新版本。在项目目录执行：

```bash
python -m pip install -r requirements.txt
python tree.py
```

自定义祝福和配色：

```bash
python tree.py --wish "愿你的冬天，有光，也有温暖。" --name "来自你的朋友" --theme 0
```

- 拖动鼠标：旋转圣诞树
- 空格：暂停或继续
- `T`：切换绯樱 / 鎏金 / 冰蓝配色
- `S`：开关飘雪
- `E`：在当前工作目录导出「送你一棵圣诞树.html」；同名文件会被覆盖
- `Esc`：退出

## 生成方便分享的 HTML

仅导出文件使用 Python 标准库，**无需安装 Pygame**：

```bash
python tree.py --export 圣诞树.html --wish "圣诞快乐，愿你平安喜乐。" --name "送给特别的你" --theme 0
```

将生成的 HTML 文件发给朋友，对方下载后用浏览器打开即可，无需联网或安装 Python。HTML 中也可以点击「写祝福」修改文字，再点击「保存贺卡」导出。

手机聊天软件内置预览可能不执行动画，请下载后用浏览器打开。

## 项目结构

| 文件 | 用途 |
| --- | --- |
| `tree.py` | Python 主程序：生成三维粒子、投影、动画循环与 HTML 导出 |
| `requirements.txt` | Python 桌面动画依赖 |
| `index.html` | 离线分享版，也是 Python 导出时使用的模板 |
| `LICENSE` | MIT 开源许可证 |

Python 桌面版与 HTML 分享版使用相同的视觉设计，分别实现动画。浏览器无法直接运行普通 Python/Pygame 脚本，因此分享版保留必要的 Canvas/JavaScript；HTML 不依赖外部资源，也不会上传祝福语。GitHub 语言统计将 HTML 作为生成的分享配套文件处理。

## 致谢

视觉创意参考 [ZekangLi-Zico/Christmas-Tree](https://github.com/ZekangLi-Zico/Christmas-Tree) 的粉色螺旋粒子树、树顶爱心与地面光环。本项目独立实现 Python 桌面版与浏览器分享版。

## 许可证

本仓库代码采用 [MIT License](LICENSE)。参考项目代码与素材不包含在本仓库中，亦不由本仓库的许可证覆盖。
