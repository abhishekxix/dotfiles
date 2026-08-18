from pathlib import Path

from .errors import InstallError


def canonical_path(path: Path) -> Path:
    return path.resolve(strict=False)


def canonical_location(path: Path) -> Path:
    return path.parent.resolve(strict=False) / path.name


def paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def validate_link_paths(
    repo_dir: Path,
    backup_parent: Path,
    managed_paths: list[tuple[Path, Path]],
) -> None:
    canonical_repo = canonical_path(repo_dir)
    canonical_backup = canonical_path(backup_parent)
    if paths_overlap(canonical_repo, canonical_backup):
        raise InstallError(
            f"Unsafe backup path overlaps repository: {backup_parent}", 2
        )

    targets: list[Path] = []
    for source, target in managed_paths:
        canonical_source = canonical_path(source)
        canonical_target = canonical_location(target)

        if paths_overlap(canonical_source, canonical_target):
            raise InstallError(
                f"Unsafe source/target overlap: {source} and {target}", 2
            )
        if canonical_repo in canonical_target.parents:
            raise InstallError(f"Unsafe target is inside repository: {target}", 2)
        if paths_overlap(canonical_source, canonical_backup) or paths_overlap(
            canonical_target, canonical_backup
        ):
            raise InstallError(f"Unsafe backup overlap for target: {target}", 2)
        targets.append(target)

    for index, target in enumerate(targets):
        canonical_target = canonical_location(target)
        for other_target in targets[index + 1 :]:
            if paths_overlap(canonical_target, canonical_location(other_target)):
                raise InstallError(
                    f"Unsafe managed target overlap: {target} and {other_target}",
                    2,
                )