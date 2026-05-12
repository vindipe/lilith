#!/usr/bin/env bash

# Uso: ./fix_names.sh /percorso/directory
ROOT="${1:-.}"

# Carattere problematico: U+F03A -> UTF-8: EF 80 BA
BAD_CHAR=$'\xEF\x80\xBA'

# Carattere di sostituzione (puoi cambiare in "_" o altro)
REPL='-'

# Cerca in profondità e rinomina file e cartelle che contengono il carattere
find "$ROOT" -depth -name "*$BAD_CHAR*" -print0 |
while IFS= read -r -d '' path; do
    new_path=${path//$BAD_CHAR/$REPL}
    if [[ "$path" != "$new_path" ]]; then
        echo "Rinomino:"
        echo "  $path"
        echo "  -> $new_path"
        mv -- "$path" "$new_path"
    fi
done
