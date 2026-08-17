# shellcheck shell=bash disable=SC2154

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