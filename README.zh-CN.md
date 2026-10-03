# 冰箱管家 · Pantry Steward

简体中文 | [English](README.en.md)

**把冰箱里快到期的食材，变成今晚可以执行的一顿饭。**

这是参加 [GOSIM Agentic App 黑客松 2026](https://create.gosim.org/agenticapp26/) 的开源应用，选择 OctoSense + AppCard 场景方向。参赛应用位于 [`apps/pantry-steward/`](apps/pantry-steward/)，当前版本为 **0.4.1**，采用独立 OctoScript 脚本应用包，在未修改的官方 OctoSense 桌面中安装、运行。

用户确认库存和饮食偏好后，管家生成菜单候选、检查到期与用量、提醒临期食材，并在用户确认实际食用量后更新库存。当前重点是 Windows 桌面的完整任务闭环；在线模型接入已实现，真实提供方请求尚未验证。

## 界面预览

下图来自官方 OctoSense 桌面的真实运行截图。

![冰箱管家首页](apps/pantry-steward/bundle/screenshots/01-main.png)

更多截图：[菜单方案](apps/pantry-steward/bundle/screenshots/02-plan.png) · [用量确认](apps/pantry-steward/bundle/screenshots/03-confirm.png) · [库存更新后](apps/pantry-steward/bundle/screenshots/04-updated.png)。

## 要解决的问题

买了食材之后，人们经常忘记库存、到期时间和剩余数量；决定今晚吃什么时，还要重新梳理这些信息。冰箱管家让同一份已确认库存贯穿后续规划和用餐记录，减少重复说明与食材浪费。

完整流程为：

```text
建立饮食档案 → 确认食材入库 → 输入本餐目标 → 生成菜单候选
       ↑                                       ↓
 更新档案与库存 ← 核对实际用量并确认扣减 ← 接受今晚方案
       └──────── 临期检查与下一餐再规划 ──────────┘
```

菜单生成与库存执行分开：候选生成不代表用户已经接受，接受菜单也不代表已经吃完。库存只在确认实际用量后扣减。

## 已实现的功能

| 功能 | 当前行为 |
| --- | --- |
| 首次建档 | 选择饮食场景，填写基础资料、饮食偏好与忌口，再录入第一批食材 |
| 库存管理 | 按批次保存名称、克数和剩余天数；添加、修改与移除均有确认流程 |
| 菜单规划 | 根据真实库存生成候选，展示来源、推荐原因、预计时长、食材用量与做法 |
| 在线模型 | 通过官方宿主 `model.complete` 请求结构化菜单；提供方与密钥由宿主管理 |
| 本地规则 | 不调用模型，按食材到期顺序安排简单家常搭配；复杂目标理解依赖在线模型 |
| 临期提醒 | 应用运行期间周期检查临期库存，创建新候选，保留原正式方案供用户比较 |
| 食用确认 | 核对并修改实际克数；拒绝超量、陈旧方案和重复扣减；确认后再规划 |
| 本地持久化 | 保存饮食档案、库存、方案、选项和执行记录，重开后恢复 |
| 用户控制 | 暂停管家、切换规划方式、开关提醒、稍后提醒、重新设置档案 |
| 比赛演示 | 经确认载入样例、推进演示时间、观察临期重排，并恢复演示前的数据 |

导航包含 **首页 / 冰箱 / 方案 / 档案 / 设置**。界面采用自然光背景、半透明玻璃分区和深绿色主操作。

## 下载与运行

### 环境准备

当前已有 Windows 运行记录。需要 Git、Python **3.11+**、Rust stable，以及 Windows C++ 编译工具和 Windows SDK。首次准备和构建需要联网与可用磁盘空间；这是源码项目，首次双击会编译，不是现成安装包。

项目仓库：[woshuoduijiushidui/OctoSense-AppCard](https://github.com/woshuoduijiushidui/OctoSense-AppCard)。

以下为新机器的安装步骤；完整冷启动下载流程尚未在本次文档整理中重新验证。已有环境的检查、构建与启动记录见 [VALIDATION.md](apps/pantry-steward/VALIDATION.md)。

```powershell
git clone https://github.com/woshuoduijiushidui/OctoSense-AppCard.git
cd OctoSense-AppCard
python -X utf8 tools/setup.py
```

若本机已经有框架依赖仓库，使用官方 setup 的 `--hub` 参数指向已有依赖目录，复用仓库，具体见 [官方环境说明](https://github.com/OctoSense-org/OctoSense)。

### 第一次打开

从仓库根目录执行：

```powershell
.\apps\pantry-steward\run.cmd --prepare-local-test
```

**执行这个参数表示你同意生成本地测试密钥。** 启动器用它们创建本机测试目录，让应用通过官方 App Hub 的签名、摘要和权限检查安装进桌面。密钥位于系统本地应用数据目录的 `OctoSense/pantry-steward-local-test-keys` 下，位于仓库之外；它们不作为正式发布者身份，也不会提交到远程商店。

首次构建需要等待，请保留命令窗口。启动后会出现官方 OctoSense 桌面，并打开冰箱管家。

### 之后打开

直接双击 `apps/pantry-steward/run.cmd`，或者在仓库根目录执行：

```powershell
.\apps\pantry-steward\run.cmd
```

不要通过删除 `.local-state/` 解决启动问题，这个目录同时保存了本机测试桌面和应用数据。启动失败时保留窗口中的错误信息。

## 普通用户怎么用

1. **建立档案。** 选择饮食场景，填写基础资料、偏好与忌口，确认后进入食材录入。
2. **录入真实库存。** 输入食材名称、数量（克）和剩余天数，点击预览，核对后确认入库；至少添加一批食材才能完成建档。
3. **生成这一餐。** 在首页输入目标，例如“优先处理豆腐，做一顿清淡的晚饭”，点击“生成这一餐”。不配置模型时可在设置中切换本地规则。
4. **查看并接受候选。** 在方案页复核做法和用量，点击“就吃这套 · 设为今晚方案”。
5. **确认实际食用量。** 做完后点击“我吃完了 · 核对实际用量”，填写真实克数，再确认扣减。取消不会改变库存。
6. **继续更新冰箱。** 新购买、剩余数量或到期日期变化时更新对应批次，管家将按最新库存重新校验、规划。

## 在线 AI 怎么配置

**这个版本使用官方 OctoSense 宿主的 AI 提供方设置，不读取旧版本的 `ai.env`。** 在启动器打开的测试桌面中，通过 OctoSense 的 AI providers 设置配置老师提供的接口信息与 Token。配置入口和实际支持的提供方以当前宿主界面为准。

请求路径是：

```text
main.splash → 官方 model.complete 服务 → 宿主管理的模型提供方
            ← 结构化结果与预算信息 ←
应用复核库存、到期日期和累计用量 → 创建待确认候选
```

规划会发送本餐目标、饮食档案、可用食材的名称/克数/剩余天数、原菜单标题和触发原因。应用不读取 Token，不在脚本中收集密钥；请不要将 Token 放进 GitHub 或 bundle。

`model.budget` 查询成功只代表预算服务可响应，**不代表模型已经配置或请求已经成功**。以实际生成结果及候选的“在线 AI”来源为准。超时、无服务、无提供方或结果不合规时会显示提示；需要时手动切换本地规则。

此迁移版已接入官方接口，但真实在线模型请求、无提供方错误的完整链路尚未验证。独立 `--standalone` 预览使用官方 `card-host`，它不提供模型服务，应使用本地规则。

## 给评委的 3 分钟演示路径

1. 完成首次建档，在设置中切换到本地规则，确认载入演示数据。演示前状态会备份。
2. 回首页查看已有原菜单，再到设置点击“时间 +12 小时”。这只推进演示时钟。
3. 查看豆腐临期触发的新候选，比较原菜单与新方案；原方案在用户接受前仍保留。
4. 接受新方案，核对实际用量，先取消一次，展示库存不变；再次确认，展示真实扣减与下一餐候选。
5. 重开应用，检查库存、方案和选项恢复。

这条路径展示可复现的本地闭环。在线演示需提前在同一宿主配置提供方，并完成真实调用验证；本地规则演示不作为在线 AI 成功的证据。

## 参赛与提交说明

参赛方向为 **OctoSense + AppCard 场景应用**，实际交付形态为官方宿主中运行的非系统 OctoScript 应用。场景重点是：确认真实状态、规划行动、用户审批、执行与结果复核。

按 [比赛页面](https://create.gosim.org/agenticapp26/) 当前说明，初赛提交需包含场景、可运行原型、源码、截图与演示，截止时间为 **2026 年 10 月 4 日 23:59（UTC+8）**；作品需以 Apache-2.0 开源。具体提交入口、成员信息和补充材料以主办方通知为准。README 不代表资格审核或获奖承诺。

比赛提交与 App Hub 上架分别准备。公开仓库提供应用源码、启动工具和验证材料；App Hub 应用包候选是：

```text
apps/pantry-steward/bundle/
```

只有 bundle 是应用分发内容。发布者身份和隐私文本仍待本人确认，正式签名和商店提交尚未完成；本机测试镜像不等于上架。[官方发布流程](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)。

## 代码与数据位置

| 路径 | 用途 |
| --- | --- |
| `apps/pantry-steward/bundle/main.splash` | 应用界面、库存、规划、提醒、确认与持久化逻辑 |
| `apps/pantry-steward/bundle/manifest.json` | 应用 ID、版本、storage/model 权限和额度 |
| `apps/pantry-steward/bundle/listing.json` | 商店介绍、图标、截图和发布者字段 |
| `apps/pantry-steward/bundle/assets/` | 图标与背景资源 |
| `apps/pantry-steward/bundle/screenshots/` | 真实官方桌面运行截图 |
| `apps/pantry-steward/tools/launch.py` | 官方 CLI 构建、本机测试镜像安装与启动 |
| `apps/pantry-steward/.local-state/` | 隔离测试桌面、应用安装与库存数据，不提交 Git |
| `apps/pantry-steward/VALIDATION.md` | 实际验证记录与未验证项 |
| `apps/pantry-steward/PRIVACY.md` | 待作者确认的隐私说明 |
| `apps/pantry-steward/REVIEW-ANSWERS.md` | App Hub 七项审核问题的草稿回答 |

默认库存位于 `.local-state/apps/pantry-steward/` 下的运行沙箱内，包括 `pantry.json`、`pantry.backup.json` 和 `before-demo.json`。使用 `--app-data` 时数据位于指定测试目录。迁移版不复制原项目库存和 AI 配置。

## 验证与当前边界

以下是 [2026-10-02 验证记录](apps/pantry-steward/VALIDATION.md)中的结果，本次 README 整理未重新执行程序：

- 官方 OctoSense 验证基线：[`b221f7b4`](https://github.com/OctoSense-org/OctoSense/commit/b221f7b4c877dd823d04e4ee510cc74880de5535)；App Hub 固定版本：[`58c3c8ae`](https://github.com/OctoSense-org/OctoSense-App-Hub/commit/58c3c8aed8fc811a16d67c5f784a8a44214ff876)。
- `pantry-steward 0.4.1 — PASSED`：源 bundle 准入检查通过，只有未签名警告，授予 storage/model；本机签名快照也通过检查。
- **18 项官方宿主界面与数据检查通过**，覆盖建档、入库、临期重排、方案接受、取消、超量拒绝、扣减和重启持久化。
- **6 项启动器检查通过**；Windows 批处理入口启动成功。
- 已检查运行日志与四张真实截图。正式发布签名、App Hub 提交及其他平台未验证。

语音图标目前只提示识别不可用，不录音。拍照识别、OCR、买菜下单、Android 真机与 APK 尚未交付。运行期间的临期检查不等于宿主关闭后的系统后台服务。

热量、营养和偏好展示属于原型估算或简单规则，不能当作专业营养测量、长期学习模型或医疗建议。到期天数由用户输入，不保证食品安全；忌口仍需用户复核。

## 开发与复核

在仓库根目录执行以下已记录的检查与独立预览命令：

```powershell
python -X utf8 apps/pantry-steward/tools/launch.py --check
python -X utf8 -m unittest discover -s apps/pantry-steward/tools -p 'test_*.py'
python -X utf8 apps/pantry-steward/tools/launch.py --standalone
```

官方宿主 UI 回归需要先启动独立的隐藏测试桌面，再按 `tools/smoke.py` 的端口和 profile 参数操作。使用测试数据，详见 [验证记录](apps/pantry-steward/VALIDATION.md)。

## 许可证与来源

本仓库使用 [Apache License 2.0](LICENSE)。第三方框架与素材的声明见 [NOTICE](NOTICE) 和 [LICENSES/](LICENSES/)。

冰箱管家应用由本项目开发，宿主基础来自 [官方 OctoSense](https://github.com/OctoSense-org/OctoSense)，发布路径参考 [OctoScript App Design Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow) 与 [OctoSense App Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)。官方桌面、手机与 ROM 的进一步说明分别见 [desktop/](desktop/README.zh-CN.md)、[phone/](phone/README.zh-CN.md) 和 [rom/](rom/README.zh-CN.md)。
