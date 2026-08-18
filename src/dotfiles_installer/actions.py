from dataclasses import dataclass
from datetime import datetime
import filecmp
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

from .errors import InstallError


@dataclass
class InstallerActions:
    repo_dir: Path
    target_home: Path
    backup_parent: Path
    xorg_dir: Path
    dry_run: bool
    backup_root: Path | None = None

    def log(self, message: str) -> None:
        print(message)

    def show_command(self, *arguments: object) -> None:
        if not self.dry_run:
            return
        command = shlex.join(str(argument) for argument in arguments)
        print(f"  + {command}")

    def ensure_backup_root(self) -> Path:
        if self.backup_root is not None:
            return self.backup_root

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if self.dry_run:
            self.backup_root = self.backup_parent / f"{timestamp}.XXXXXX"
            self.log(f"Would allocate unique backup directory: {self.backup_root}")
        else:
            self.backup_parent.mkdir(parents=True, exist_ok=True)
            self.backup_root = Path(
                tempfile.mkdtemp(prefix=f"{timestamp}.", dir=self.backup_parent)
            )
            self.log(f"Backing up conflicts to {self.backup_root}")
        return self.backup_root

    def backup_target(self, target: Path) -> None:
        backup_root = self.ensure_backup_root()
        backup_path = backup_root / target.relative_to(self.target_home)

        if backup_path.exists() or backup_path.is_symlink():
            raise InstallError(f"Backup destination already exists: {backup_path}")

        self.show_command("mkdir", "-p", "--", backup_path.parent)
        self.show_command("mv", "-T", "--", target, backup_path)
        if not self.dry_run:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(target, backup_path)

    def link_item(self, source: Path, target: Path) -> None:
        if target.is_symlink() and target.resolve(strict=False) == source.resolve(
            strict=False
        ):
            self.log(f"Already linked: {target}")
            return

        if target.exists() or target.is_symlink():
            self.backup_target(target)

        self.show_command("mkdir", "-p", "--", target.parent)
        self.show_command("ln", "-s", "--", source, target)
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source, target_is_directory=source.is_dir())
            self.log(f"Linked: {target} -> {source}")

    def install_xorg(self) -> None:
        source = self.repo_dir / "xorg.conf"
        target = self.xorg_dir / "20-nvidia.conf"

        if not source.is_file():
            raise InstallError(f"Missing Xorg source file: {source}", 2)

        if target.exists() or target.is_symlink():
            if target.is_file() and filecmp.cmp(source, target, shallow=False):
                self.log(f"Already installed: {target}")
                return
            raise InstallError(
                f"Refusing to replace existing Xorg configuration: {target}", 3
            )

        arguments = ("install", "-Dm644", "--", source, target)
        if self.xorg_dir == Path("/etc/X11/xorg.conf.d"):
            if not self.dry_run:
                self.log(f"Installing {target} (sudo may prompt for your password)")
            command = ("sudo", *arguments)
            self.show_command(*command)
            if not self.dry_run:
                subprocess.run(tuple(str(part) for part in command), check=True)
            return

        self.show_command(*arguments)
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            target.chmod(0o644)