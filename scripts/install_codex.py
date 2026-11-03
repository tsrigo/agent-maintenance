"""Link this checkout's skills and preferences into Codex without editing AGENTS.

The standalone installer uses Python 3.11+ for the standard-library TOML parser.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    raise SystemExit("全局安装入口需要 Python 3.11 或以上。") from None

START = "# BEGIN agent-maintenance global integration\n"
END = "# END agent-maintenance global integration\n"


def guidance(root: Path) -> str:
    profile = root / ".agents/profiles/personal.md"
    return (
        f"At the start of each new conversation, before handling its task, read "
        f"the user's collaboration preferences from {profile}. "
        "Apply relevant preferences as supplementary user guidance: the current "
        "user request and applicable AGENTS.md instructions take precedence. "
        "Keep loading global and project AGENTS.md normally; do not replace them "
        "or apply the maintenance repository's own AGENTS.md to other projects. "
        f"The preferences and maintenance skills are maintained in {root}; "
        "update their sources there when the user requests changes. "
        "If the preference file is unavailable, continue with existing instructions "
        "and report the missing path when relevant."
    )


def configuration(raw: bytes, root: Path) -> bytes:
    text = raw.decode("utf-8")
    tomllib.loads(text)
    if text.startswith(START):
        boundary = text.find(END)
        if boundary < 0:
            raise ValueError("全局接入标记不完整，保留原配置。")
        base = text[boundary + len(END) :].removeprefix("\n")
    else:
        if START in text or END in text:
            raise ValueError("全局接入标记位置异常，保留原配置。")
        base = text
    original = tomllib.loads(base)
    if "developer_instructions" in original:
        raise ValueError("已有其他 developer_instructions，拒绝覆盖或自动合并。")
    value = guidance(root)
    block = START + "developer_instructions = " + json.dumps(value, ensure_ascii=False)
    result = (block + "\n" + END + "\n" + base).encode("utf-8")
    parsed = tomllib.loads(result.decode("utf-8"))
    if parsed.pop("developer_instructions") != value or parsed != original:
        raise ValueError("生成配置未保留原有设置，未执行接入。")
    return result


def write_configuration(path: Path, expected: bytes, updated: bytes) -> None:
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    handle, name = tempfile.mkstemp(prefix=".agent-maintenance-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "wb") as output:
            output.write(updated)
            output.flush()
            os.fsync(output.fileno())
        temporary.chmod(mode)
        actual = path.read_bytes() if path.exists() else b""
        if actual != expected:
            raise ValueError("config.toml 在接入期间改变，未覆盖并发修改。")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def install(root: Path, home: Path, codex_home: Path, check: bool = False) -> dict:
    root, home, codex_home = root.resolve(), home.resolve(), codex_home.resolve()
    profile = root / ".agents/profiles/personal.md"
    sources = sorted((root / ".agents/skills").glob("*/SKILL.md"))
    if not sources or not profile.is_file() or not profile.read_text().strip():
        raise ValueError("维护仓库缺少 Skill 或协作习惯文件。")
    config = codex_home / "config.toml"
    if config.is_symlink():
        raise ValueError("config.toml 是软链接，拒绝替换已有配置入口。")
    raw = config.read_bytes() if config.exists() else b""
    updated = configuration(raw, root)
    destination = home / ".agents/skills"
    links = [(destination / source.parent.name, source.parent) for source in sources]
    for link, target in links:
        if link.is_symlink() and link.resolve() == target:
            continue
        if link.exists() or link.is_symlink():
            raise ValueError(f"已有其他 Skill 入口，拒绝覆盖：{link}")
    settings = tomllib.loads(raw.decode("utf-8")).get("skills", {}).get("config", [])
    for entry in settings:
        if entry.get("enabled") is not False:
            continue
        for link, target in links:
            selector = entry.get("path")
            if entry.get("name") == target.name or (
                selector
                and Path(selector).expanduser().resolve()
                in ((target / "SKILL.md").resolve(), (link / "SKILL.md").resolve())
            ):
                raise ValueError(f"已有禁用规则，保留设置：{target.name}")
    missing = [str(link) for link, _ in links if not link.is_symlink()]
    if check:
        if missing or raw != updated:
            raise ValueError(
                "全局接入不完整；请运行安装入口。缺少链接：" + ", ".join(missing)
            )
    else:
        created = []
        try:
            destination.mkdir(parents=True, exist_ok=True)
            codex_home.mkdir(parents=True, exist_ok=True)
            for link, target in links:
                if not link.is_symlink():
                    link.symlink_to(target, target_is_directory=True)
                    created.append((link, target))
            if raw != updated:
                write_configuration(config, raw, updated)
        except Exception:
            for link, target in reversed(created):
                if link.is_symlink() and link.resolve() == target:
                    link.unlink()
            raise
    return {
        "skills": [target.name for _, target in links],
        "skills_directory": str(destination),
        "preferences": str(profile),
        "config": str(config),
        "mode": "check" if check else "install",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    codex_home = args.codex_home or Path(
        os.environ.get("CODEX_HOME", str(args.home / ".codex"))
    )
    try:
        result = install(
            Path(__file__).resolve().parents[1], args.home, codex_home, args.check
        )
    except (ValueError, OSError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
