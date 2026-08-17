# shellcheck shell=bash disable=SC2154

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