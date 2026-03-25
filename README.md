# C64 Sprite (Simple Workflow)

This is a Commodore C64 preservation project, and it has been done in Ubuntu on WSL2.

This project uses one source file, one build script, and one output file.

Quick start (build + run on VICE):

```bash
./run.sh
```

Behavior:

- `./run.sh` builds and launches VICE in the foreground. It stays open until you close VICE.
- `./run.sh --test` does a short non-interactive smoke test and exits automatically.

Smoke test without leaving VICE open:

```bash
./run.sh --test
```

## 1) Edit the sprite

Use `simple_sprite_editor.py`, then press `S` to save.

The editor now uses true C64 **multicolor sprite** mode:

- 12x21 editable pixels (each editor pixel is double-width on C64)
- `1` = Blue (`$D025`, shared multicolor 0)
- `2` = Red (`$D027`, sprite color)
- `3` = Green (`$D026`, shared multicolor 1)
- `SPACE` toggles current pixel on/off

That writes:

- `sprite_pokes.c` (generated `sprite_data[63]` + sprite color constants)
- `sprite_pokes.h` (external declaration)

`final_sprite.c` includes this header and uses the linked data automatically.

In one terminal sequence:

```bash
python3 simple_sprite_editor.py   # press S in editor
./run.sh
```

## 2) Build

```bash
./build.sh
```

This creates `final.prg`.

## 3) Run in emulator

Load `final.prg` in your C64 emulator (for example C64 Forever or VICE `x64`).

### VICE (`x64`) ROM setup (verified)

VICE needs C64 ROM files named `basic`, `chargen`, and `kernal`.

Working locations on this system:

- `/usr/lib/vice/basic`
- `/usr/lib/vice/chargen`
- `/usr/lib/vice/kernal`

Also present in:

- `/usr/lib/vice/data/C64/basic`
- `/usr/lib/vice/data/C64/chargen`
- `/usr/lib/vice/data/C64/kernal`

These ROMs were found and verified as readable by `x64`.

Run with explicit ROM paths and autostart your program:

```bash
x64 -basic /usr/lib/vice/basic \
    -chargen /usr/lib/vice/chargen \
    -kernal /usr/lib/vice/kernal \
    -autostartprgmode 1 \
    -autostart /home/dagfinn/Programming/cc65/final.prg
```

If normal autostart fails for `.prg`, keep `-autostartprgmode 1` (direct PRG injection).

### Troubleshooting (VICE)

- `DriveROM: Error - ... ROM image not found` for 1541/1571/etc:
  - Safe to ignore for this simple `.prg` workflow.
  - This project does not require hardware-level drive ROM emulation.

- `AUTOSTART: ... not a valid disk image` when loading `final.prg`:
  - Use `-autostartprgmode 1` so VICE injects the PRG directly.

- `Sound buffer overflow` in fast/headless runs:
  - Usually harmless during quick command-line smoke tests.
  - Optional: add `-sounddev dummy` to reduce audio-related noise.

- Joystick warnings like `Cannot open /dev/input/js0`:
  - Harmless unless you intend to use a physical joystick.

## Controls

- `W`: move up
- `A`: move left
- `S`: move down
- `D`: move right
