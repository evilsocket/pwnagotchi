#!/bin/bash

set -eu

DEPENDENCIES=( 'xgettext' 'msgfmt' 'msgmerge' )
COMMANDS=( 'add' 'update' 'delete' 'compile' )

REPO_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
LOCALE_DIR="${REPO_DIR}/sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/locale"
VOICE_FILE="${REPO_DIR}/sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/voice.py"

function usage() {
cat <<EOF

usage: $0 <command> [options]

  Commands:
    add <language>
    delete <language>
    compile <language>
    update <language>

EOF
}

for REQ in "${DEPENDENCIES[@]}"; do
  if ! type "$REQ" >/dev/null 2>&1; then
    echo "Dependency check failed for ${REQ}"
    exit 1
  fi
done


if [[ ! "${COMMANDS[*]}" =~ $1 ]]; then
  usage
fi


function add_lang() {
  mkdir -p "$LOCALE_DIR/$1/LC_MESSAGES"
  cp -n "$LOCALE_DIR/voice.pot" "$LOCALE_DIR/$1/LC_MESSAGES/voice.po"
}

function del_lang() {
  # set -eu is present; so not dangerous
  rm -rf "$LOCALE_DIR/$1"
}

function comp_lang() {
  msgfmt -o  "$LOCALE_DIR/$1/LC_MESSAGES/voice.mo"  "$LOCALE_DIR/$1/LC_MESSAGES/voice.po"
}

function update_lang() {
  xgettext --no-location -d voice -o "$LOCALE_DIR/voice.pot" "$VOICE_FILE"
  msgmerge --update "$LOCALE_DIR/$1/LC_MESSAGES/voice.po" "$LOCALE_DIR/voice.pot"
}


case "$1" in
  add)
    add_lang "$2"
    ;;
  delete)
    del_lang "$2"
    ;;
  compile)
    comp_lang "$2"
    ;;
  update)
    update_lang "$2"
    ;;
esac
