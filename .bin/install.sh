#!/usr/bin/env bash
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

repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
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

canonical_path() {
  realpath -m -- "$1"
}

canonical_location() {
  local path=$1

  printf '%s/%s\n' "$(realpath -m -- "$(dirname -- "$path")")" "$(basename -- "$path")"
}

paths_overlap() {
  local first=$1
  local second=$2

  [[ $first == "$second" || $first == "$second"/* || $second == "$first"/* ]]
}

validate_link_paths() {
  local source
  local target
  local canonical_source
  local canonical_target
  local canonical_repo
  local canonical_backup
  local index
  local -a sources=("$@")
  local -a targets=()

  canonical_repo=$(canonical_path "$repo_dir")
  canonical_backup=$(canonical_path "$backup_parent")
  if paths_overlap "$canonical_repo" "$canonical_backup"; then
    printf 'Unsafe backup path overlaps repository: %s\n' "$backup_parent" >&2
    exit 2
  fi

  for ((index = 0; index < ${#sources[@]}; index += 2)); do
    source=${sources[index]}
    target=${sources[index + 1]}
    canonical_source=$(canonical_path "$source")
    canonical_target=$(canonical_location "$target")

    if paths_overlap "$canonical_source" "$canonical_target"; then
      printf 'Unsafe source/target overlap: %s and %s\n' "$source" "$target" >&2
      exit 2
    fi
    if [[ $canonical_target == "$canonical_repo"/* ]]; then
      printf 'Unsafe target is inside repository: %s\n' "$target" >&2
      exit 2
    fi
    if paths_overlap "$canonical_source" "$canonical_backup" ||
      paths_overlap "$canonical_target" "$canonical_backup"; then
      printf 'Unsafe backup overlap for target: %s\n' "$target" >&2
      exit 2
    fi
    targets+=("$target")
  done

  for ((index = 0; index < ${#targets[@]}; index++)); do
    local other_index
    for ((other_index = index + 1; other_index < ${#targets[@]}; other_index++)); do
      if paths_overlap "$(canonical_location "${targets[index]}")" \
        "$(canonical_location "${targets[other_index]}")"; then
        printf 'Unsafe managed target overlap: %s and %s\n' \
          "${targets[index]}" "${targets[other_index]}" >&2
        exit 2
      fi
    done
  done
}

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

log() {
  printf '%s\n' "$*"
}

run() {
  if $dry_run; then
    printf '  +'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

ensure_backup_root() {
  if ! $backup_created; then
    if $dry_run; then
      backup_root="$backup_parent/$(date +%Y%m%d-%H%M%S).XXXXXX"
      log "Would allocate unique backup directory: $backup_root"
    else
      mkdir -p -- "$backup_parent"
      backup_root=$(mktemp -d -- "$backup_parent/$(date +%Y%m%d-%H%M%S).XXXXXX")
      log "Backing up conflicts to $backup_root"
    fi
    backup_created=true
  fi
}

backup_target() {
  local target=$1
  local relative_path=${target#"$target_home"/}
  local backup_path

  ensure_backup_root
  backup_path="$backup_root/$relative_path"

  if [[ -e $backup_path || -L $backup_path ]]; then
    printf 'Backup destination already exists: %s\n' "$backup_path" >&2
    exit 1
  fi

  run mkdir -p -- "$(dirname -- "$backup_path")"
  run mv -T -- "$target" "$backup_path"
}

link_item() {
  local source=$1
  local target=$2

  if [[ -L $target && $(readlink -f -- "$target") == $(readlink -f -- "$source") ]]; then
    log "Already linked: $target"
    return
  fi

  if [[ -e $target || -L $target ]]; then
    backup_target "$target"
  fi

  run mkdir -p -- "$(dirname -- "$target")"
  run ln -s -- "$source" "$target"
  $dry_run || log "Linked: $target -> $source"
}

install_xorg() {
  if [[ ! -f $repo_dir/xorg.conf ]]; then
    printf 'Missing Xorg source file: %s\n' "$repo_dir/xorg.conf" >&2
    exit 2
  fi

  if [[ -e $xorg_target || -L $xorg_target ]]; then
    if cmp -s -- "$repo_dir/xorg.conf" "$xorg_target"; then
      log "Already installed: $xorg_target"
      return
    fi

    printf 'Refusing to replace existing Xorg configuration: %s\n' "$xorg_target" >&2
    exit 3
  fi

  if [[ $xorg_dir == /etc/X11/xorg.conf.d ]]; then
    $dry_run || log "Installing $xorg_target (sudo may prompt for your password)"
    run sudo install -Dm644 -- "$repo_dir/xorg.conf" "$xorg_target"
  else
    $dry_run || log "Installing $xorg_target"
    run install -Dm644 -- "$repo_dir/xorg.conf" "$xorg_target"
  fi
}

select_group() {
  local selection=$1
  local source_array_name=$2
  local selected_array_name=$3
  local -n group_sources=$source_array_name
  local -n selected=$selected_array_name
  local choice
  local lookup
  local remaining
  local source
  local existing
  local -a choices

  selected=()
  selection=${selection#"${selection%%[![:space:]]*}"}
  selection=${selection%"${selection##*[![:space:]]}"}

  case $selection in
    all)
      selected=("${group_sources[@]}")
      return
      ;;
    none)
      return
      ;;
  esac

  remaining=$selection
  while [[ $remaining == *,* ]]; do
    choices+=("${remaining%%,*}")
    remaining=${remaining#*,}
  done
  choices+=("$remaining")

  for choice in "${choices[@]}"; do
    choice=${choice#"${choice%%[![:space:]]*}"}
    choice=${choice%"${choice##*[![:space:]]}"}
    if [[ -z $choice ]]; then
      printf 'Selection contains an empty name: %s\n' "$selection" >&2
      exit 2
    fi
    if [[ $choice == all || $choice == none ]]; then
      printf '%s must be used alone; use ./%s for a literal name\n' \
        "$choice" "$choice" >&2
      exit 2
    fi

    lookup=$choice
    [[ $lookup == ./* ]] && lookup=${lookup#./}
    source=
    for existing in "${group_sources[@]}"; do
      if [[ ${existing##*/} == "$lookup" ]]; then
        source=$existing
        break
      fi
    done

    if [[ -z $source ]]; then
      printf 'Invalid selection: %s\n' "$choice" >&2
      exit 2
    fi

    for existing in "${selected[@]}"; do
      [[ $existing == "$source" ]] && continue 2
    done
    selected+=("$source")
  done
}

prompt_with_checkboxes() {
  local key
  local sequence
  local tag
  local index
  local display_index
  local cursor=0
  local top=0
  local page_size
  local terminal_lines
  local rendered=false
  local rendered_lines
  local selected_count
  local checked_count
  local target_state
  local home_group_index=1
  local home_start=2
  local home_end
  local config_group_index
  local config_start
  local config_end
  local pointer
  local mark
  local accent=
  local bold=
  local dim=
  local reset=
  local -a labels
  local -a tags
  local -a checked

  if [[ ! -t 0 || ! -t 1 ]]; then
    printf '%s\n' 'Interactive selection requires a TTY.' >&2
    printf '%s\n' 'Use --all, --home, and --config for non-interactive installation.' >&2
    exit 1
  fi

  if [[ -z ${NO_COLOR:-} ]]; then
    accent=$'\033[36m'
    bold=$'\033[1m'
    dim=$'\033[2m'
    reset=$'\033[0m'
  fi

  labels=('All dotfiles' '  Home files')
  tags=(all home)
  checked=(1 1)
  for index in "${!home_files[@]}"; do
    labels+=("    ${home_files[index]}")
    tags+=("h$index")
    checked+=(1)
  done
  home_end=$((${#labels[@]} - 1))
  config_group_index=${#labels[@]}
  labels+=('  .config')
  tags+=(config)
  checked+=(1)
  config_start=${#labels[@]}
  for index in "${!config_sources[@]}"; do
    labels+=("    ${config_sources[index]##*/}")
    tags+=("c$index")
    checked+=(1)
  done
  config_end=$((${#labels[@]} - 1))

  while true; do
    if $rendered; then
      printf '\033[%dA' "$rendered_lines"
    fi
    terminal_lines=$(tput lines 2>/dev/null || printf '24')
    page_size=$((terminal_lines - 6))
    ((page_size < 5)) && page_size=5
    ((${#labels[@]} < page_size)) && page_size=${#labels[@]}
    rendered_lines=$((page_size + 3))

    ((cursor < top)) && top=$cursor
    ((cursor >= top + page_size)) && top=$((cursor - page_size + 1))

    rendered=true

    printf '\033[2K\r%s%sSelect dotfiles to install%s\n' "$bold" "$accent" "$reset"
    printf '\033[2K\r%sUp/Down move, Space toggles, Enter confirms%s\n' "$dim" "$reset"

    for ((display_index = 0; display_index < page_size; display_index++)); do
      index=$((top + display_index))
      pointer=' '
      ((index == cursor)) && pointer='>'
      mark='[ ]'
      case ${checked[index]} in
        1) mark='[x]' ;;
        2) mark='[-]' ;;
      esac

      if ((index == cursor)); then
        printf '\033[2K\r%s%s %s %s%s\n' "$accent" "$pointer" "$mark" "${labels[index]}" "$reset"
      else
        printf '\033[2K\r%s %s %s\n' "$pointer" "$mark" "${labels[index]}"
      fi
    done

    selected_count=0
    for ((index = home_start; index <= home_end; index++)); do
      ((checked[index] == 1)) && selected_count=$((selected_count + 1))
    done
    for ((index = config_start; index <= config_end; index++)); do
      ((checked[index] == 1)) && selected_count=$((selected_count + 1))
    done
    printf '\033[2K\r%s%d/%d selected, item %d/%d%s\n' \
      "$dim" "$selected_count" \
      "$((${#home_files[@]} + ${#config_sources[@]}))" \
      "$((cursor + 1))" "${#checked[@]}" "$reset"

    key=
    if ! IFS= read -rsn1 key; then
      printf '\nInstallation cancelled: input closed.\n' >&2
      exit 1
    fi
    case $key in
      '')
        break
        ;;
      ' ')
        case ${tags[cursor]} in
          all)
            target_state=1
            ((checked[0] == 1)) && target_state=0
            for index in "${!checked[@]}"; do
              checked[index]=$target_state
            done
            ;;
          home)
            target_state=1
            ((checked[home_group_index] == 1)) && target_state=0
            for ((index = home_start; index <= home_end; index++)); do
              checked[index]=$target_state
            done
            ;;
          config)
            target_state=1
            ((checked[config_group_index] == 1)) && target_state=0
            for ((index = config_start; index <= config_end; index++)); do
              checked[index]=$target_state
            done
            ;;
          *)
            checked[cursor]=$((1 - checked[cursor]))
            ;;
        esac

        checked_count=0
        for ((index = home_start; index <= home_end; index++)); do
          ((checked[index] == 1)) && checked_count=$((checked_count + 1))
        done
        if ((checked_count == 0)); then
          checked[home_group_index]=0
        elif ((checked_count == ${#home_files[@]})); then
          checked[home_group_index]=1
        else
          checked[home_group_index]=2
        fi

        checked_count=0
        for ((index = config_start; index <= config_end; index++)); do
          ((checked[index] == 1)) && checked_count=$((checked_count + 1))
        done
        if ((checked_count == 0)); then
          checked[config_group_index]=0
        elif ((checked_count == ${#config_sources[@]})); then
          checked[config_group_index]=1
        else
          checked[config_group_index]=2
        fi

        if ((checked[home_group_index] == 1 && checked[config_group_index] == 1)); then
          checked[0]=1
        elif ((checked[home_group_index] == 0 && checked[config_group_index] == 0)); then
          checked[0]=0
        else
          checked[0]=2
        fi
        ;;
      k)
        ((cursor > 0)) && cursor=$((cursor - 1))
        ;;
      j)
        ((cursor + 1 < ${#labels[@]})) && cursor=$((cursor + 1))
        ;;
      $'\033')
        sequence=
        if ! IFS= read -rsn1 -t 0.1 sequence; then
          printf '\nInstallation cancelled.\n'
          exit 1
        fi
        if [[ $sequence == '[' || $sequence == O ]]; then
          while IFS= read -rsn1 -t 0.1 key; do
            sequence+=$key
            [[ $key == [@-~] ]] && break
          done
        fi
        case $sequence in
          '[A'|OA)
            ((cursor > 0)) && cursor=$((cursor - 1))
            ;;
          '[B'|OB)
            ((cursor + 1 < ${#labels[@]})) && cursor=$((cursor + 1))
            ;;
          '[H'|'[1~'|OH)
            cursor=0
            ;;
          '[F'|'[4~'|OF)
            cursor=$((${#labels[@]} - 1))
            ;;
          '[5~')
            ((cursor > page_size)) && cursor=$((cursor - page_size)) || cursor=0
            ;;
          '[6~')
            ((cursor + page_size < ${#labels[@]})) &&
              cursor=$((cursor + page_size)) || cursor=$((${#labels[@]} - 1))
            ;;
        esac
        ;;
    esac
  done

  selected_home_files=()
  selected_config_sources=()

  for index in "${!tags[@]}"; do
    local selected_index

    ((checked[index] != 1)) && continue
    tag=${tags[index]}
    case $tag in
      all|home|config)
        ;;
      h*)
        selected_index=${tag#h}
        selected_home_files+=("${home_files[selected_index]}")
        ;;
      c*)
        selected_index=${tag#c}
        selected_config_sources+=("${config_sources[selected_index]}")
        ;;
    esac
  done
}

choose_sources() {
  if $install_all; then
    selected_home_files=("${home_files[@]}")
    selected_config_sources=("${config_sources[@]}")
  elif $home_selection_set || $config_selection_set; then
    if $home_selection_set; then
      select_group "$home_selection" home_files selected_home_files
    else
      selected_home_files=("${home_files[@]}")
    fi

    if $config_selection_set; then
      select_group "$config_selection" config_sources selected_config_sources
    else
      selected_config_sources=("${config_sources[@]}")
    fi

  else
    prompt_with_checkboxes
  fi
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