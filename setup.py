from __future__ import annotations

import os
import platform
import shutil
import sys
import traceback
import typing as p

term = shutil.get_terminal_size()
sep = "=" * term.columns

venv = False
default = 1
sample_files = ["data/database.sample.db"]
po_files = ["text.py", "buttons.py", "other.py"]

if os.name == "nt":
    print(f"Setup not supported on {platform.system()}")
    exit()


def _opt_selector(
    options: dict[str, p.Callable], default: int | None = None, pmt: str = ""
) -> tuple[int, p.Any]:
    _options = {}
    print("Choose variant")
    print(sep)

    num = 1
    for opt in options:
        if options[opt] is None:
            print()
            continue

        d = "*" if default == num else " "

        print(f"  {d}{num} - {opt}")
        _options[num] = options[opt]
        num += 1
    print(sep)

    while True:
        opt = input(f"{pmt}-> ")
        if opt.isdigit():
            opt = int(opt)
            if opt in _options:
                return opt, _options[opt]
        if opt == "" and default is not None:
            return default, _options[default]

        print("Incorrect answer")
        pmt = ""


def _yes(default: bool = True) -> bool:
    while True:
        if default:
            it = "[Y|n]"
        else:
            it = "[y|N]"

        i = input(f"{it} -> ")
        if i.lower() in ["y", "n"]:
            return i.lower() == "y"
        if i == "":
            return default

        print("Incorrect answer")


def _input(prompt: str, default: str = None, required: bool = True) -> str:
    if default:
        print(f"Default {default}")
    while True:
        result = input(f"{prompt} -> ")
        if not result:
            if default:
                result = default
                break
            elif required:
                print("Parameter required")
        else:
            break

    return result


def _cmd(cmd: str, show_cmd: bool = True) -> bool:
    if show_cmd:
        input(f"Press enter for execute {cmd}")
    result = os.system(cmd)
    return True if result == 0 else False


def _clear():
    print()
    print("\033c", end="")


def _enter():
    input("Press enter, to continue ...")


def config_generator():
    main_token = _input("Main bot token")
    test_token = _input("Test bot token")
    _clear()
    print("This can be found here https://my.telegram.org/apps")
    api_id = _input("Api id")
    api_hash = _input("Api hash")
    _clear()
    print("MySQL database setup")
    print("Check README.md for more information")
    sql_host = _input("Host")
    sql_user = _input("User")
    sql_password = _input("Password")
    sql_database = _input("Database name")

    with open("config.py", "r") as file:
        sample = file.read().format(
            main_token=main_token,
            test_token=test_token,
            api_id=api_id,
            api_hash=api_hash,
            sql_user=sql_user,
            sql_password=sql_password,
            sql_database=sql_database,
            sql_host=sql_host,
        )

    with open("data/docker/config.py", "w") as file:
        file.write(sample)
    return True


def compile_po_files():
    path = "i38n/"
    locales = os.listdir(path)
    lc = "LC_MESSAGES/"

    if not locales:
        print("Locales not found")
    for local in locales:
        po = f"{local}.po"
        local = path + local + "/"
        mo = "ToolKit.mo"

        if not os.path.isdir(local):
            local = local.removesuffix("/")
            print(f"{local!r} - is not folder, delete ?")
            if _yes():
                os.remove(local)
            continue
        po = local + po
        if not os.path.isfile(po):
            print(
                f'{po!r} - file is not exist, skipping {local!r} folder \t(run "Generate po files")'
            )
            continue
        if not os.path.isdir(local + lc):
            os.mkdir(local + lc)
            print(f"Folder {local + lc!r} created ")

        mo = local + lc + mo
        if _cmd(f"msgfmt {po} -o {mo}", False):
            print(f"{po!r} - file compiled to - {mo!r}")
        else:
            print("COMPILE ERROR")
        print(sep)

    _enter()
    return True


if __name__ == "__main__":
    opts = {
        "Setup config.py": config_generator,
        "Compile po files": compile_po_files,
        "Exit": exit,
    }
    exit_index = list(opts.keys()).index("Exit") + 1
    default = 1
    pmt = ""

    _clear()
    while True:
        if default >= exit_index:
            default = exit_index
        term = shutil.get_terminal_size()
        sep = "=" * term.columns
        try:
            _clear()
            num, opt = _opt_selector(opts, default, pmt)
            _clear()
            res = opt()
            _clear()

            if num != default:
                default = num + 1
            elif res is True:
                default += 1

            if res is not True:
                pmt = f"{res!r} "
                if num == default:
                    default = num + 1
            else:
                pmt = ""

        except KeyboardInterrupt:
            break
        except Exception as e:
            pmt = f"An error has occurred ({e.__class__.__name__}:{e.args[0]})"
            trc = traceback.format_exc()
            print(trc)
            _enter()
    _clear()
