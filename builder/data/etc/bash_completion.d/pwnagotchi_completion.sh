_show_complete()
{
    local cur opts node_names all_options opt_line
    all_options="
pwnagotchi -h --help -C --config -U --user-config --manual --skip-session --clear --debug --version --print-config {plugins}
pwnagotchi plugins -h --help {list,install,enable,disable,uninstall,update,upgrade}
pwnagotchi plugins list -i --installed -h --help
pwnagotchi plugins install -h --help
pwnagotchi plugins uninstall -h --help
pwnagotchi plugins enable -h --help
pwnagotchi plugins disable -h --help
pwnagotchi plugins update -h --help
pwnagotchi plugins upgrade -h --help
"
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    cmd="${COMP_WORDS[@]:0:${#COMP_WORDS[@]}-1}"
    opt_line="$(grep -m1 "$cmd" <<<$all_options)"
    if [[ ${cur} == -* ]] ; then
        opts="$(echo $opt_line | tr ' ' '\n' | awk '/^ *-/{gsub("[^a-zA-Z0-9-]","",$1);print $1}')"
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    opts="$(echo $opt_line | grep -Po '{\K[^}]+' | tr ',' '\n')"
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
}

complete -F _show_complete pwnagotchi
