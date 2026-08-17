#!/usr/bin/env bash
# shellcheck source-path=SCRIPTDIR
set -Eeuo pipefail

if ! (
  capability_value=supported
  declare -n capability_reference=capability_value &&
    [[ $capability_reference == "$capability_value" ]] &&
    mapfile -d '' -t capability_records < <(printf '\0') &&
    ((${#capability_records[@]} == 1))
) 2>/dev/null; then
  printf '%s\n' \
    'This installer requires Bash with nameref and NUL-delimited mapfile support.' >&2
  exit 2
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
repo_dir=$(cd -- "$script_dir/.." && pwd -P)
home_dir="$repo_dir/home"
config_dir="$repo_dir/.config"
target_home=${DOTFILES_HOME:-$HOME}
backup_parent=${DOTFILES_BACKUP_DIR:-"$target_home/.dotfiles-backup"}
backup_root=
xorg_dir=${DOTFILES_XORG_DIR:-/etc/X11/xorg.conf.d}
xorg_target="$xorg_dir/20-nvidia.conf"
dry_run=false
include_xorg=false
install_all=false
home_selection=
home_selection_set=false
config_selection=
config_selection_set=false
backup_created=false

# shellcheck source=install/paths.sh
source "$script_dir/install/paths.sh"
# shellcheck source=install/actions.sh
source "$script_dir/install/actions.sh"
# shellcheck source=install/selection.sh
source "$script_dir/install/selection.sh"

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Install this repository by creating symlinks in the home directory.

Options:
  -n, --dry-run       Show changes without modifying files
      --all           Install every home and .config entry
      --home LIST     Install comma-separated home file names
  -c, --config LIST   Install comma-separated .config names
      --include-xorg  Install xorg.conf in /etc/X11/xorg.conf.d (uses sudo)
  -h, --help          Show this help

Environment:
  DOTFILES_HOME        Override the target home directory
  DOTFILES_BACKUP_DIR  Override the parent directory for unique backups
  DOTFILES_XORG_DIR    Override the Xorg destination directory
EOF
}

while (($#)); do
  case $1 in
    -n|--dry-run)
      dry_run=true
      ;;
    --all)
      install_all=true
      ;;
    --home)
      if (($# < 2)) || [[ $2 == -* ]] || [[ -z ${2//[[:space:]]/} ]]; then
        printf '%s requires a non-empty selection\n' "$1" >&2
        exit 2
      fi
      home_selection=$2
      home_selection_set=true
      shift
      ;;
    --home=*)
      home_selection=${1#*=}
      if [[ -z ${home_selection//[[:space:]]/} ]]; then
        printf '%s requires a non-empty selection\n' "${1%%=*}" >&2
        exit 2
      fi
      home_selection_set=true
      ;;
    -c|--config)
      if (($# < 2)) || [[ $2 == -* ]] || [[ -z ${2//[[:space:]]/} ]]; then
        printf '%s requires a non-empty selection\n' "$1" >&2
        exit 2
      fi
      config_selection=$2
      config_selection_set=true
      shift
      ;;
    --config=*)
      config_selection=${1#*=}
      if [[ -z ${config_selection//[[:space:]]/} ]]; then
        printf '%s requires a non-empty selection\n' "${1%%=*}" >&2
        exit 2
      fi
      config_selection_set=true
      ;;
    --include-xorg)
      include_xorg=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if $install_all && ($home_selection_set || $config_selection_set); then
  printf '%s\n' '--all cannot be used with --home or --config' >&2
  exit 2
fi

if [[ ! -d $home_dir ]]; then
  printf 'Missing dotfiles source directory: %s\n' "$home_dir" >&2
  exit 2
fi
if [[ ! -d $config_dir ]]; then
  printf 'Missing dotfiles source directory: %s\n' "$config_dir" >&2
  exit 2
fi

mapfile -d '' -t home_files < <(
  find "$home_dir" -mindepth 1 -maxdepth 1 -type f -name '.*' -printf '%f\0' | sort -z
)
mapfile -d '' -t config_sources < <(
  find "$config_dir" -mindepth 1 -maxdepth 1 \
    ! -iname 'README*' ! -iname 'LICENSE*' ! -name .gitkeep -print0 | sort -z
)
selected_home_files=()
selected_config_sources=()
choose_sources

managed_paths=()
for path in "${selected_home_files[@]}"; do
  [[ -e $home_dir/$path ]] && managed_paths+=("$home_dir/$path" "$target_home/$path")
done
for source in "${selected_config_sources[@]}"; do
  name=${source##*/}
  managed_paths+=("$source" "$target_home/.config/$name")
done
$include_xorg && managed_paths+=("$repo_dir/xorg.conf" "$xorg_target")
validate_link_paths "${managed_paths[@]}"
$include_xorg && install_xorg

if $dry_run; then
  log "Previewing dotfiles from $repo_dir into $target_home"
else
  log "Installing dotfiles from $repo_dir into $target_home"
fi

for path in "${selected_home_files[@]}"; do
  [[ -e $home_dir/$path ]] && link_item "$home_dir/$path" "$target_home/$path"
done

for source in "${selected_config_sources[@]}"; do
  name=${source##*/}
  link_item "$source" "$target_home/.config/$name"
done

if $dry_run; then
  log 'Dry run complete. No changes were made.'
else
  log 'Dotfiles installed. Restart your shell or log in again to load them.'
fi