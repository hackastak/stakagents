"""README Generator — reads a local repo, writes a clean README.md."""

from pathlib import Path

from pydantic import BaseModel, Field

from stakagents.core.agent import Agent
from stakagents.core.llm import get_chat_model
from stakagents.core.registry import register

_KEY_FILES = [
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "requirements.txt",
    "README.md",
    "LICENSE",
]
_IGNORE = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    "dist",
    "build",
}
_MAX_FILE_CHARS = 4000
_MAX_TREE_ENTRIES = 200

_SYSTEM_PROMPT = (
    "You are a senior engineer writing a README.md for the repository below. "
    "Use ONLY the provided file tree and file contents. Do not include features, "
    "commands, or dependencies you cannot see in the repo. Produce a clean, well-structured "
    "README in Markdown with: a one-line description, key features, installation, "
    "usage, and project structure. Output only the README markdown, no preamble."
)


class ReadmeInput(BaseModel):
    repo_path: str = Field(description="Path to a local repository directory")


class ReadmeOutput(BaseModel):
    readme_markdown: str


def _gather_context(repo: Path) -> str:
    parts: list[str] = [f"# Repository: {repo.name}"]

    tree_lines: list[str] = []
    for path in sorted(repo.rglob("*")):
        rel = path.relative_to(repo)
        if any(part in _IGNORE for part in rel.parts):
            continue
        if len(tree_lines) >= _MAX_TREE_ENTRIES:
            tree_lines.append("... (truncated)")
            break
        depth = len(rel.parts) - 1
        tree_lines.append("  " * depth + rel.name + ("/" if path.is_dir() else ""))
    parts.append("## File tree\n" + "\n".join(tree_lines))

    for name in _KEY_FILES:
        f = repo / name
        if f.is_file():
            text = f.read_text(encoding="utf-8", errors="replace")[:_MAX_FILE_CHARS]
            parts.append(f"## {name}\n```\n{text}\n```")

    return "\n\n".join(parts)


@register
class ReadmeGenerator(Agent[ReadmeInput, ReadmeOutput]):
    name = "readme-generator"
    input_model = ReadmeInput
    output_model = ReadmeOutput

    def run(self, payload: ReadmeInput) -> ReadmeOutput:
        repo = Path(payload.repo_path).expanduser().resolve()
        if not repo.is_dir():
            raise ValueError(f"not a directory: {repo}")

        context = _gather_context(repo)
        reply = get_chat_model().invoke(
            [("system", _SYSTEM_PROMPT), ("human", context)]
        )
        return ReadmeOutput(readme_markdown=str(reply.content))
