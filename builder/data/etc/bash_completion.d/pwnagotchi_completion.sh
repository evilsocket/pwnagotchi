_show_complete()
{
    local cur prev opts node_names
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    cmd="${COMP_WORDS[@]:0:${#COMP_WORDS[@]}-1}"
    if [[ ${cur} == -* ]] ; then
        opts="$($cmd --help | tr ' ' '\n' | awk '/^ *-/{gsub("[^a-zA-Z0-9-]","",$1);print $1}')"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    opts="$($cmd --help | sed -n '/positional arguments:/ {n;p}' | tr ',' '\n' | awk '{gsub("[^a-zA-Z0-9-]", "", $1); print $1}')"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}

complete -F _show_complete pwnagotchi
