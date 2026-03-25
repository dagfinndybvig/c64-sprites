#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRG="$ROOT_DIR/final.prg"

find_rom() {
    local name="$1"
    local candidates=(
        "/usr/lib/vice/$name"
        "/usr/lib/vice/data/C64/$name"
        "$HOME/.config/vice/data/C64/$name"
        "$HOME/.config/vice/C64/$name"
        "$HOME/.vice/data/C64/$name"
        "$HOME/.vice/C64/$name"
    )
    local path
    for path in "${candidates[@]}"; do
        if [[ -r "$path" ]]; then
            printf '%s\n' "$path"
            return 0
        fi
    done
    return 1
}

if ! command -v x64 >/dev/null 2>&1; then
    echo "Error: x64 (VICE) not found in PATH."
    exit 1
fi

echo "Building final.prg from final_sprite.c..."
"$ROOT_DIR/build.sh"

BASIC_ROM="$(find_rom basic)" || { echo "Error: could not find BASIC ROM."; exit 1; }
CHARGEN_ROM="$(find_rom chargen)" || { echo "Error: could not find CHARGEN ROM."; exit 1; }
KERNAL_ROM="$(find_rom kernal)" || { echo "Error: could not find KERNAL ROM."; exit 1; }

echo "Using ROMs:"
echo "  BASIC:   $BASIC_ROM"
echo "  CHARGEN: $CHARGEN_ROM"
echo "  KERNAL:  $KERNAL_ROM"

if [[ "${1:-}" == "--test" ]]; then
    echo "Running short non-interactive test launch..."
    tmp_log="$(mktemp)"
    set +e
    x64 \
        -basic "$BASIC_ROM" \
        -chargen "$CHARGEN_ROM" \
        -kernal "$KERNAL_ROM" \
        -sounddev dummy \
        -autostartprgmode 1 \
        -autostart "$PRG" \
        -warp \
        -limitcycles 3000000 >"$tmp_log" 2>&1
    x64_status=$?
    set -e

    if grep -qE "AUTOSTART: Done\.|recognized as program/p00 file\." "$tmp_log"; then
        echo "Test launch succeeded (PRG built and started in VICE)."
        rm -f "$tmp_log"
        exit 0
    fi

    echo "Test launch failed (VICE did not finish autostart)."
    tail -n 60 "$tmp_log"
    rm -f "$tmp_log"
    exit "$x64_status"
fi

echo "Launching VICE x64..."
exec x64 \
    -basic "$BASIC_ROM" \
    -chargen "$CHARGEN_ROM" \
    -kernal "$KERNAL_ROM" \
    -autostartprgmode 1 \
    -autostart "$PRG"
