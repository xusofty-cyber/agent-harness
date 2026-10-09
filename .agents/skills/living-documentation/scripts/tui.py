"""tools/tui.py — shared terminal UI helpers for agent-harness maintenance scripts.

Single-select and multi-select arrow-key menus with numbered-prompt
fallback when stdin is not a TTY. Windows arrow keys (msvcrt two-byte
sequences) are handled.
"""

import sys


def tui_select(title: str, options: list[tuple[str, any]]) -> any:
    """Renders single-select interactive TUI or falls back to numbered prompt."""
    if not sys.stdin.isatty():
        print(title)
        for i, (label, _) in enumerate(options, 1):
            print(f"{i}) {label}")
        try:
            choice = input(f"Select [1-{len(options)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][1]
        except Exception:
            pass
        return options[0][1]

    cur = 0
    count = len(options)
    print(f"\n\033[36m{title}\033[0m")
    print("\033[2m↑↓ move, enter confirm\033[0m")

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        if sys.platform != "win32":
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while True:
                    for i, (label, _) in enumerate(options):
                        if i == cur:
                            sys.stdout.write(f"\033[36m> ● {label}\033[0m\n")
                        else:
                            sys.stdout.write(f"  \033[90m○\033[0m {label}\n")
                    sys.stdout.flush()

                    ch = sys.stdin.read(1)
                    if ch == "\x1b":
                        seq = sys.stdin.read(2)
                        if seq == "[A":
                            cur = (cur - 1 + count) % count
                        elif seq == "[B":
                            cur = (cur + 1) % count
                    elif ch in ("k", "K"):
                        cur = (cur - 1 + count) % count
                    elif ch in ("j", "J"):
                        cur = (cur + 1) % count
                    elif ch in ("\r", "\n"):
                        break
                    elif ch in ("q", "Q"):
                        sys.exit(0)

                    sys.stdout.write(f"\033[{count}A")
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        else:
            import msvcrt
            while True:
                for i, (label, _) in enumerate(options):
                    if i == cur:
                        sys.stdout.write(f"> ● {label}\n")
                    else:
                        sys.stdout.write(f"  ○ {label}\n")
                sys.stdout.flush()

                key = msvcrt.getch()
                if key in (b"\x00", b"\xe0"):
                    code = msvcrt.getch()
                    if code == b"H":
                        cur = (cur - 1 + count) % count
                    elif code == b"P":
                        cur = (cur + 1) % count
                elif key in (b"\r", b"\n"):
                    break
                elif key in (b"q", b"Q"):
                    sys.exit(0)

                sys.stdout.write(f"\033[{count}A")
                sys.stdout.flush()
    except Exception:
        pass
    finally:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()

    return options[cur][1]


def tui_multiselect(title: str, options: list[tuple[str, any, bool]]) -> list[any]:
    """Renders multi-select interactive TUI or falls back to numbered prompt.

    options: list of (label, value, default_checked)
    """
    labels = [opt[0] for opt in options]
    values = [opt[1] for opt in options]
    checked = [bool(opt[2]) for opt in options]
    count = len(options)

    if not sys.stdin.isatty():
        print(title)
        for i, (label, _, chk) in enumerate(options, 1):
            mark = "x" if chk else " "
            print(f"{i}) [{mark}] {label}")
        try:
            resp = input("Enter numbers separated by space (or press Enter for defaults): ").strip()
            if not resp:
                return [values[i] for i, c in enumerate(checked) if c]
            selected = []
            for num in resp.split():
                if num.isdigit():
                    idx = int(num) - 1
                    if 0 <= idx < count:
                        selected.append(values[idx])
            return selected
        except Exception:
            return [values[i] for i, c in enumerate(checked) if c]

    cur = 0
    print(f"\n\033[36m{title}\033[0m")
    print("\033[2m↑↓ move, space toggle, a toggle-all, enter confirm\033[0m")

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        if sys.platform != "win32":
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while True:
                    for i in range(count):
                        box = "[x]" if checked[i] else "[ ]"
                        if i == cur:
                            sys.stdout.write(f"\033[36m> {box} {labels[i]}\033[0m\n")
                        else:
                            color = "\033[32m" if checked[i] else "\033[90m"
                            sys.stdout.write(f"  {color}{box}\033[0m {labels[i]}\n")
                    sys.stdout.flush()

                    ch = sys.stdin.read(1)
                    if ch == "\x1b":
                        seq = sys.stdin.read(2)
                        if seq == "[A":
                            cur = (cur - 1 + count) % count
                        elif seq == "[B":
                            cur = (cur + 1) % count
                    elif ch in ("k", "K"):
                        cur = (cur - 1 + count) % count
                    elif ch in ("j", "J"):
                        cur = (cur + 1) % count
                    elif ch == " ":
                        checked[cur] = not checked[cur]
                    elif ch in ("a", "A"):
                        all_checked = all(checked)
                        checked = [not all_checked] * count
                    elif ch in ("\r", "\n"):
                        break
                    elif ch in ("q", "Q"):
                        sys.exit(0)

                    sys.stdout.write(f"\033[{count}A")
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        else:
            import msvcrt
            while True:
                for i in range(count):
                    box = "[x]" if checked[i] else "[ ]"
                    if i == cur:
                        sys.stdout.write(f"> {box} {labels[i]}\n")
                    else:
                        sys.stdout.write(f"  {box} {labels[i]}\n")
                sys.stdout.flush()

                key = msvcrt.getch()
                if key in (b"\x00", b"\xe0"):
                    code = msvcrt.getch()
                    if code == b"H":
                        cur = (cur - 1 + count) % count
                    elif code == b"P":
                        cur = (cur + 1) % count
                elif key == b" ":
                    checked[cur] = not checked[cur]
                elif key in (b"a", b"A"):
                    all_checked = all(checked)
                    checked = [not all_checked] * count
                elif key in (b"\r", b"\n"):
                    break
                elif key in (b"q", b"Q"):
                    sys.exit(0)

                sys.stdout.write(f"\033[{count}A")
                sys.stdout.flush()
    except Exception:
        pass
    finally:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()

    return [values[i] for i, c in enumerate(checked) if c]
