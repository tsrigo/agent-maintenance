# 通用维护包的采用与来源

[tsrigo/agent-maintenance](https://github.com/tsrigo/agent-maintenance) 维护可跨项目采用的工程 Skill、文档规则与可选协作习惯。目标项目选择所需部分，继续拥有自己的代码、依赖、事实记录和验证入口。

## 采用范围

- 文档、文字与决策维护沿用 WncFht 上游的三个 Skill 及其引用资源。
- [review-code](../.agents/skills/review-code/SKILL.md)、[find-simplifications](../.agents/skills/find-simplifications/SKILL.md)、[pre-delivery-checks](../.agents/skills/pre-delivery-checks/SKILL.md)提供通用审查、简化和验证选择方法；具体命令从目标项目发现。
- [通用协作习惯](../.agents/profiles/personal.md)可单独选用。复制到其他人的项目或共享规则前，先判断是否符合实际需求；不将其自动升级为所有使用者的偏好。
- formatter、hooks、CI 与 MPE 预览分别按需接入，采用 Skill 不要求同时安装整套工具链。

向已有项目接入时，先读目标规则，选择 Skill 及其引用文件，修复相对链接，并复用现有验证。不整份覆盖目标 `AGENTS.md`，不复制本仓的过程 Notes、个人原始记录或项目专属运行配置。安装位置与宿主发现方式按实际环境验证；仓库内有文件不代表当前 Agent 已加载。

## WncFht 上游

fork 起点为 [WncFht/agent-maintenance @ 527af880](https://github.com/WncFht/agent-maintenance/tree/527af880f6feb0e352cae42b2c7601dc443b2b70)。原规则、工具链与预览资源的来源继续见[来源与取舍](../来源与取舍.md)，保留原有 MIT 许可。

`origin` 指向个人 fork，`upstream` 指向 WncFht 仓库。维护更新时先获取上游、读相关差异，再合并；检查个人配置、补充 Skill 及其引用是否仍然适用。只合并用户当前授权的更新，不自动同步、发布或写入其他项目。

在干净工作区可先检查上游差异：

```sh
git fetch upstream
git log --oneline HEAD..upstream/main
git diff HEAD...upstream/main -- README.md AGENTS.md .agents scripts
```

上游默认分支或 remote 配置改变时，先核对实际 ref。合并后按受影响内容选择本地检查，推送后核对远端提交和实际 CI 状态。

## DeepSeek Harness 方法

既有采用记录使用 [deepseek-ai/deepseek-harness @ c291e796](https://github.com/deepseek-ai/deepseek-harness/tree/c291e7961a515f6d7af9304e7fd1d257929aef26)。本 fork 从该公开版本重新整理通用方法，不复制既有研究项目的专用 Skill。

| 本仓入口                | 固定版本来源                                                                                                                                                               | 适配                                                                                                              |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| review-code             | [dsh-code-review](https://github.com/deepseek-ai/deepseek-harness/blob/c291e7961a515f6d7af9304e7fd1d257929aef26/.agents/skills/dsh-code-review/SKILL.md)                   | 保留真实入口、接口两侧、生命周期及模型视角；移除上游包结构、专用命令和产品检查。                                  |
| find-simplifications    | [dsh-find-simplifications](https://github.com/deepseek-ai/deepseek-harness/blob/c291e7961a515f6d7af9304e7fd1d257929aef26/.agents/skills/dsh-find-simplifications/SKILL.md) | 保留消费者证据、最强保留理由和净维护成本；不规定目录、PR 流程或必须委派子 Agent。                                 |
| pre-delivery-checks     | [dsh-pre-push-checks](https://github.com/deepseek-ai/deepseek-harness/blob/c291e7961a515f6d7af9304e7fd1d257929aef26/.agents/skills/dsh-pre-push-checks/SKILL.md)           | 保留按 diff 选择验证、复用已通过证据、精确 lease 和远端核验；移除 pnpm、stack 及仓库专属基线。                    |
| maintain-decision-notes | 上游维护包已整合 dsh-archive-agent-notes                                                                                                                                   | 复用现有记录技能；实验原件另按[证据规则](../.agents/references/experiment-reports.md)保护，不重复创建归档 Skill。 |

WncFht 的规则基线使用另一个 DeepSeek 固定提交，两者分别保留来源，不混称同一版。新增改写属于方法适配，未运行 DeepSeek harness 产品运行时，也不宣称与原 Skill 行为完全等价。来源许可见 [LICENSE](../LICENSE) 与[第三方声明](../THIRD_PARTY_NOTICES.md)。

## 维护边界

通用规则只保存可复用判断，运行参数和一次性授权留在目标项目。新经验先核实际案例和反例，再修订已有条目；没有新证据不机械追加规则。私有记录先在原位置保存，公开仓库只接收已选定且适合公开的通用表述，不携带凭据、主机细节或内部文档副本。

协作习惯依据本机可访问的原始用户输入整理，区分用户自写内容、粘贴材料、自动唤醒与分叉继承；候选按工作目录分层复核，并回读具体要求、纠正和边界反例。来源不明或尚未确认的推断留在私有研究记录，不直接写成常驻规则。问句归档及逐条证据保存在公开仓库之外。

维护本 fork 的提交身份见[个人 GitHub 规则](../.agents/profiles/personal.md#个人-github-提交身份)。克隆到新环境后核对实际 author、committer 与目标 remote，保留项目和公司仓库各自的身份配置。

本 fork 的范围选择与替代方案见[维护决定](../.agents/notes/implemented/process/2026-11-03-general-maintenance-fork.md)。
