from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
import typer
from rich import print

app = typer.Typer(help="Self-service MLOps CLI (portfolio project).")


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"[bold cyan]$ {' '.join(cmd)}[/bold cyan]")
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


@app.command()
def init(name: str = typer.Argument(..., help="Project name under ./projects/")) -> None:
    """Create a new ML project from the golden-path template."""
    repo_root = Path(__file__).resolve().parents[3]
    template = repo_root / "platform" / "templates" / "ml-project"
    target = repo_root / "projects" / name

    if target.exists():
        raise typer.BadParameter(f"Target already exists: {target}")

    shutil.copytree(template, target)
    # Replace placeholder tokens
    for p in target.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py", ".toml", ".yml", ".yaml", ".txt", ""}:
            try:
                txt = p.read_text(encoding="utf-8")
            except Exception:
                continue
            txt = txt.replace("{{PROJECT_NAME}}", name)
            p.write_text(txt, encoding="utf-8")

    print(f"[green]Created project:[/green] {target}")


@app.command()
def train(project: str = "usedcar-price") -> None:
    """Run training in the project's training container."""
    repo_root = Path(__file__).resolve().parents[3]
    proj = repo_root / "projects" / project
    run(["make", "train-local"], cwd=proj)


@app.command()
def publish(project: str = "usedcar-price") -> None:
    """Publish trained model to S3 and update SSM model pointer."""
    repo_root = Path(__file__).resolve().parents[3]
    proj = repo_root / "projects" / project
    run(["bash", str(repo_root / "scripts" / "train_publish.sh")], cwd=proj)


@app.command()
def deploy(env: str = "prod") -> None:
    """Deploy/update AWS infra (Terraform apply)."""
    repo_root = Path(__file__).resolve().parents[3]
    tf = repo_root / "platform" / "infra" / "terraform"
    run(["terraform", "apply", "-auto-approve"], cwd=tf)
    print(f"[green]Deployed env:[/green] {env}")


@app.command()
def status() -> None:
    """Show key AWS outputs (Terraform)."""
    repo_root = Path(__file__).resolve().parents[3]
    tf = repo_root / "platform" / "infra" / "terraform"
    run(["terraform", "output"], cwd=tf)
