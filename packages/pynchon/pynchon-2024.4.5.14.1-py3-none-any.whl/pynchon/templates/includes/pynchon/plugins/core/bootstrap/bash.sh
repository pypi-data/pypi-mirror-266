{# Template used to generate `pynchon bootstrap --bash` #}
printf "Loading pynchon completions..\n" > /dev/stderr
alias p=pynchon

_pynchon_completions_filter() {
  local words="$1"
  local cur=${COMP_WORDS[COMP_CWORD]}
  local result=()

  if [[ "${cur:0:1}" == "-" ]]; then
    echo "$words"

  else
    for word in $words; do
      [[ "${word:0:1}" != "-" ]] && result+=("$word")
    done

    echo "${result[*]}"

  fi
}

_pynchon_completions() {
  local cur=${COMP_WORDS[COMP_CWORD]}
  local compwords=("${COMP_WORDS[@]:1:$COMP_CWORD-1}")
  local compline="${compwords[*]}"

  case "$compline" in
    {#
    'apply'*'--protocol')
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "$(_pynchon_completions_filter "ssh telnet")" -- "$cur" )
      ;;

    'apply'*'--user')
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -A user -- "$cur" )
      ;;
    #}
{{rest}}
    'apply'*)
      while read -r; do COMPREPLY+=( "$REPLY" ); done < <( compgen -W "$(_pynchon_completions_filter "--help --protocol --user -h")" -- "$cur" )
      ;;



  esac
} &&
complete -F _pynchon_completions pynchon

# ex: filetype=sh
