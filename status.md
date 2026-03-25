# C64 Sprite Project Status

## Current state

The workflow is working end-to-end and is now split cleanly between code and generated sprite data.

- Canonical app source: `final_sprite.c`
- Generated sprite module: `sprite_pokes.c` + `sprite_pokes.h`
- Build script: `build.sh`
- Run script: `run.sh`
- Output program: `final.prg`

## Restart quick-start

After a restart, run these in project root:

```bash
python3 simple_sprite_editor.py   # edit sprite, press S to save module
./build.sh                        # build final.prg
./run.sh                          # launch VICE in foreground
```

Smoke test only:

```bash
./run.sh --test
```

## Technical implementation

1. Sprite editing and generation:
   - `python3 simple_sprite_editor.py`
   - On startup, editor loads current `sprite_pokes.c` sprite data if file exists.
   - Controls:
      - Arrow keys: move cursor
      - `SPACE`: toggle current pixel on/off
      - `C`: clear sprite to empty
      - `1`/`2`/`3`: select sprite color slot
      - `S`: save generated module
      - `Q`: quit editor
   - Press `S` to generate:
      - `sprite_pokes.c` (`const unsigned char sprite_data[63]` + color constants)
      - `sprite_pokes.h` (`extern` declaration)
   - Editor now targets C64 multicolor sprite format (12x21 logical pixels, 2-bit packed data).
   - Color mapping is consistent end-to-end:
     - `1` -> `$D025` shared multicolor 0 (blue)
     - `2` -> `$D027` sprite color (red)
     - `3` -> `$D026` shared multicolor 1 (green)

2. Program linkage:
   - `final_sprite.c` includes `sprite_pokes.h`
   - `build.sh` compiles and links both modules:
     - `cl65 -t c64 -o final.prg final_sprite.c sprite_pokes.c`

3. Runtime behavior:
    - Sprite bytes are copied to `$3000`
    - Sprite pointer `$07F8` is set to `192` (`$3000 / 64`)
    - Sprite 0 is enabled in multicolor mode (`$D01C`)
    - Color registers are loaded from generated module (`$D025/$D026/$D027`)
    - Sprite is controlled with WASD

## Verified run behavior

- `./run.sh`:
  - Builds `final.prg`
  - Locates VICE ROMs (`basic`, `chargen`, `kernal`)
  - Launches `x64` in foreground using `exec`
  - Stays open until VICE is closed by the user

- `./run.sh --test`:
  - Runs short non-interactive launch with cycle limit
  - Exits automatically
  - Reports success from autostart log signals

## Verified result

- New sprite generated in editor is visible in VICE.
- Build and launch path is stable and repeatable.
- Multicolor rendering matches editor color selection (`1`/`2`/`3`).
