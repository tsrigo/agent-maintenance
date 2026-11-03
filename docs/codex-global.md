# Codex 全局接入

将此 checkout 作为六项维护 Skill 和[协作习惯](../.agents/profiles/personal.md)的维护来源。用户级入口覆盖以后新开的 Codex 对话，项目仍使用各自已有的指令、工具链和验证入口。

## 安装与检查

在此 checkout 根目录运行，需要 Python 3.11+，只使用标准库：

```sh
python3.11 scripts/install_codex.py
python3.11 scripts/install_codex.py --check
```

安装会创建六个 `~/.agents/skills/<技能名>` 目录软链接，分别指向本仓 `.agents/skills/` 中的同名目录。Codex 的[用户级技能发现](https://developers.openai.com/codex/skills/)支持这个目录及软链接，技能正文和共享引用保持在源仓库。重复安装不改写已正确接入的文件；`--check` 只读检查链接、来源文件和配置。

协作习惯通过 `$CODEX_HOME/config.toml` 中一个带管理标记的 `developer_instructions` 字段接入，未设置 `CODEX_HOME` 时使用 `~/.codex/config.toml`。这段短引导要求新对话先读取本仓 `.agents/profiles/personal.md`，按任务应用相关偏好，并继续加载原全局与项目指令。[该配置字段](https://developers.openai.com/codex/config-reference/)用于附加开发者指令；实际习惯正文只在仓库保存。

当前用户请求和适用的 `AGENTS.md` 优先于个人习惯。安装入口不修改任何 `AGENTS.md`，不创建 `AGENTS.override.md`，也不向其他项目套用本仓的 `AGENTS.md`。原配置除新增管理块外保留原字节，模型、provider、hooks、权限和既有技能配置继续使用原设置。

同名入口指向其他来源、已有其他 `developer_instructions`、相关技能已被禁用或配置入口为软链接时，脚本会报错并保留原设置。先处理具体冲突，再运行安装；不要删除不属于本仓的入口。`--home` 和 `--codex-home` 可用于隔离目录验证。

## 日常维护

修改本仓 `.agents/skills/` 及其引用资源，或 `.agents/profiles/personal.md`。已有技能和习惯直接读取源文件；新增技能后重新运行安装入口以增加链接。安装后在新对话中核对技能列表和习惯读取。已有对话可能保留已加载的内容，新对话用于验证更新后的启动行为。

checkout 必须保留在可读的稳定位置。移动仓库后，核对并移除仍指向旧位置的本仓技能链接，再从新位置运行安装入口。撤销接入时，仅移除指向本仓的六个链接，以及配置中 `BEGIN agent-maintenance global integration` 至对应 `END` 的管理块；保留配置其他内容和所有 `AGENTS.md`。

隔离行为测试覆盖已有指令保留、共享引用、源文件更新、冲突拒绝、重复安装和只读检查：

```sh
python3.11 -m unittest discover -s scripts/tests -p test_codex_install.py -v
```

宿主验证使用本机 Codex 的 `debug prompt-input` 检查新会话的实际启动输入，核对六项 Skill、习惯读取引导以及原全局和项目指令同时存在。该命令不调用模型；启动输入核验不等同于已实测模型在任务中如何应用每条习惯。
