# shellcheck shell=bash disable=SC2154

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