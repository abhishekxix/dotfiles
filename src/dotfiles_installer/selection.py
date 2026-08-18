import os
from pathlib import Path
import select
import shutil
import sys
import termios
import tty

from .errors import InstallError


def select_group(selection: str, sources: list[Path]) -> list[Path]:
    selection = selection.strip()
    if selection == "all":
        return list(sources)
    if selection == "none":
        return []

    selected: list[Path] = []
    for choice in selection.split(","):
        choice = choice.strip()
        if not choice:
            raise InstallError(f"Selection contains an empty name: {selection}", 2)
        if choice in {"all", "none"}:
            raise InstallError(
                f"{choice} must be used alone; use ./{choice} for a literal name",
                2,
            )

        lookup = choice.removeprefix("./")
        source = next((item for item in sources if item.name == lookup), None)
        if source is None:
            raise InstallError(f"Invalid selection: {choice}", 2)
        if source not in selected:
            selected.append(source)
    return selected


def _group_state(checked: list[int], start: int, end: int) -> int:
    states = checked[start : end + 1]
    checked_count = states.count(1)
    if checked_count == 0:
        return 0
    if checked_count == len(states):
        return 1
    return 2


def _read_escape_sequence(input_fd: int) -> str:
    if not select.select([input_fd], [], [], 0.1)[0]:
        raise InstallError("Installation cancelled.")

    sequence = os.read(input_fd, 1).decode("ascii")
    if sequence in {"[", "O"}:
        while select.select([input_fd], [], [], 0.1)[0]:
            character = os.read(input_fd, 1).decode("ascii")
            if not character:
                break
            sequence += character
            if "@" <= character <= "~":
                break
    return sequence


def prompt_with_checkboxes(
    home_files: list[Path], config_sources: list[Path]
) -> tuple[list[Path], list[Path]]:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise InstallError(
            "Interactive selection requires a TTY.\n"
            "Use --all, --home, and --config for non-interactive installation."
        )

    labels = ["All dotfiles", "  Home files"]
    tags: list[tuple[str, int | None]] = [("all", None), ("home", None)]
    checked = [1, 1]
    for index, source in enumerate(home_files):
        labels.append(f"    {source.name}")
        tags.append(("home-item", index))
        checked.append(1)

    home_group_index = 1
    home_start = 2
    home_end = len(labels) - 1
    config_group_index = len(labels)
    labels.append("  .config")
    tags.append(("config", None))
    checked.append(1)
    config_start = len(labels)
    for index, source in enumerate(config_sources):
        labels.append(f"    {source.name}")
        tags.append(("config-item", index))
        checked.append(1)
    config_end = len(labels) - 1

    use_color = "NO_COLOR" not in os.environ
    accent = "\033[36m" if use_color else ""
    bold = "\033[1m" if use_color else ""
    dim = "\033[2m" if use_color else ""
    reset = "\033[0m" if use_color else ""
    cursor = 0
    top = 0
    rendered_lines = 0
    input_fd = sys.stdin.fileno()
    original_terminal = termios.tcgetattr(input_fd)

    try:
        tty.setraw(input_fd)
        while True:
            terminal_lines = shutil.get_terminal_size(fallback=(80, 24)).lines
            page_size = max(5, terminal_lines - 6)
            page_size = min(page_size, len(labels))
            if cursor < top:
                top = cursor
            if cursor >= top + page_size:
                top = cursor - page_size + 1

            output: list[str] = []
            if rendered_lines:
                output.append(f"\033[{rendered_lines}A")
            output.append(
                f"\033[2K\r{bold}{accent}Select dotfiles to install{reset}\n"
            )
            output.append(
                f"\033[2K\r{dim}Up/Down move, Space toggles, Enter confirms{reset}\n"
            )
            for index in range(top, top + page_size):
                pointer = ">" if index == cursor else " "
                mark = {0: "[ ]", 1: "[x]", 2: "[-]"}[checked[index]]
                color = accent if index == cursor else ""
                color_reset = reset if index == cursor else ""
                output.append(
                    f"\033[2K\r{color}{pointer} {mark} {labels[index]}"
                    f"{color_reset}\n"
                )

            selected_count = (
                checked[home_start : home_end + 1].count(1)
                + checked[config_start : config_end + 1].count(1)
            )
            total_count = len(home_files) + len(config_sources)
            output.append(
                f"\033[2K\r{dim}{selected_count}/{total_count} selected, "
                f"item {cursor + 1}/{len(checked)}{reset}\n"
            )
            rendered_lines = page_size + 3
            sys.stdout.write("".join(output))
            sys.stdout.flush()

            key = os.read(input_fd, 1).decode("ascii")
            if not key:
                raise InstallError("Installation cancelled: input closed.")
            if key in {"\r", "\n"}:
                break
            if key == "\x03":
                raise KeyboardInterrupt
            if key == " ":
                tag, _ = tags[cursor]
                if tag == "all":
                    target_state = 0 if checked[0] == 1 else 1
                    checked[:] = [target_state] * len(checked)
                elif tag == "home":
                    target_state = 0 if checked[home_group_index] == 1 else 1
                    checked[home_start : home_end + 1] = [target_state] * max(
                        0, home_end - home_start + 1
                    )
                elif tag == "config":
                    target_state = 0 if checked[config_group_index] == 1 else 1
                    checked[config_start : config_end + 1] = [target_state] * max(
                        0, config_end - config_start + 1
                    )
                else:
                    checked[cursor] = 1 - checked[cursor]

                checked[home_group_index] = _group_state(
                    checked, home_start, home_end
                )
                checked[config_group_index] = _group_state(
                    checked, config_start, config_end
                )
                group_states = {
                    checked[home_group_index], checked[config_group_index]
                }
                if group_states == {1}:
                    checked[0] = 1
                elif group_states == {0}:
                    checked[0] = 0
                else:
                    checked[0] = 2
            elif key == "k":
                cursor = max(0, cursor - 1)
            elif key == "j":
                cursor = min(len(labels) - 1, cursor + 1)
            elif key == "\x1b":
                sequence = _read_escape_sequence(input_fd)
                if sequence in {"[A", "OA"}:
                    cursor = max(0, cursor - 1)
                elif sequence in {"[B", "OB"}:
                    cursor = min(len(labels) - 1, cursor + 1)
                elif sequence in {"[H", "[1~", "OH"}:
                    cursor = 0
                elif sequence in {"[F", "[4~", "OF"}:
                    cursor = len(labels) - 1
                elif sequence == "[5~":
                    cursor = max(0, cursor - page_size)
                elif sequence == "[6~":
                    cursor = min(len(labels) - 1, cursor + page_size)
    finally:
        termios.tcsetattr(input_fd, termios.TCSADRAIN, original_terminal)

    selected_home = []
    selected_config = []
    for position, (tag, index) in enumerate(tags):
        if index is None or checked[position] != 1:
            continue
        if tag == "home-item":
            selected_home.append(home_files[index])
        elif tag == "config-item":
            selected_config.append(config_sources[index])
    return selected_home, selected_config


def choose_sources(
    home_files: list[Path],
    config_sources: list[Path],
    install_all: bool,
    home_selection: str | None,
    config_selection: str | None,
) -> tuple[list[Path], list[Path]]:
    if install_all:
        return list(home_files), list(config_sources)
    if home_selection is not None or config_selection is not None:
        selected_home = (
            select_group(home_selection, home_files)
            if home_selection is not None
            else list(home_files)
        )
        selected_config = (
            select_group(config_selection, config_sources)
            if config_selection is not None
            else list(config_sources)
        )
        return selected_home, selected_config
    return prompt_with_checkboxes(home_files, config_sources)