# 冰箱管家

[English](README.md) | 简体中文

适配未修改的官方 OctoSense 的独立脚本应用。保留原版界面、首次建档、库存、
本地配餐、食用确认和持久化；不向官方宿主注入额外模型或语音服务。

## 启动

需要 Python 3.11+、Rust，以及官方项目已准备好的 `.sources/`。
在官方仓库根目录运行（已在 Windows 验证，实际结果见 VALIDATION.md）：

```powershell
.\apps\pantry-steward\run.cmd --prepare-local-test
```

`--prepare-local-test` 仅在本人同意生成本地测试密钥后使用。密钥保存在系统本地
应用数据目录的 `OctoSense/pantry-steward-local-test-keys` 下，位于仓库之外。
这些不是正式发布者密钥，不上传，也不向任何远程仓库提交作品。
以后可直接双击本文件夹的 `run.cmd`，或在根目录运行：

```powershell
.\apps\pantry-steward\run.cmd
```

启动器使用官方仓库固定版本的 App Hub CLI 和 `.sources/` 依赖，检查源应用包，
为单独的本地快照签名，通过 App Hub 原有的签名、摘要和权限检查安装，
然后在官方宿主中打开冰箱管家。不修改官方宿主代码。

测试库存和桌面设置隔离在 `.local-state/` 中，不覆盖正常桌面或原项目的库存。
旧数据和 `ai.env` 没有复制进来；请勿在删除测试目录前忘记备份需要的数据。

## AI 与语音

模型在这个测试桌面的 OctoSense AI 提供方设置中配置。应用不读取 `ai.env`，
不接触密钥、不提供密钥输入框。官方 `model.budget` 只表示预算，不表示模型已配置。
无服务或无提供方时给出提示，可以继续用本地规则。真实在线模型调用**未验证**。

麦克风图标保留，但本版本点击只提示“语音识别暂不可用”，不录音、
不申请麦克风权限。原版语音适配代码仍保留在原项目。

## 检查与单独预览

这些检查与预览命令已在 Windows 验证，实际结果见 VALIDATION.md：

```powershell
python -X utf8 apps/pantry-steward/tools/launch.py --check
python -X utf8 apps/pantry-steward/tools/launch.py --standalone
```

单独的官方 card-host 不提供模型服务，本地功能应完整可用。
只有 `bundle/` 是 App Hub 提交候选，不是整个官方仓库、工具或测试目录。
发布者身份、隐私文本确认、正式签名和正式提交仍需作者本人处理。
参赛演示前应固定实际验证过的官方版本，不临时更新。
