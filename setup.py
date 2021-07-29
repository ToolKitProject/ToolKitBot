import os
import platform
import shutil
import sys
import typing as p

term = shutil.get_terminal_size()
sep = "=" * term.columns

venv = False
default = 1
sample_files = ["data/database.sample.db"]
po_files = ["text.py", "buttons.py", "any.py"]

if os.name == "nt":
    print(f"Setup not supported on {platform.system()}")
    exit()


def _opt_selector(options: p.Dict[str, p.Any], default: p.Optional[int] = None, pmt: str = "") -> p.Tuple[int, p.Any]:
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


def _clear():
    print()
    print('\033c', end="")


def _enter():
    input("Press enter, to continue ...")


def systemd_unit_generator():
    global venv
    while True:
        username = os.environ["USER"]
        print(f"{username} - This your username ?")
        if not _yes():
            username = input("Your username -> ")

        path = os.path.dirname(os.path.abspath(__file__))
        print(f"{path} - This path to root of project ?")
        if not _yes():
            path = input("Path to root of project -> ")

        print(f"Use venv ?")
        venv = _yes()
        if venv:
            py_path = os.path.join(path, "venv", "bin", "python3.9")
        else:
            py_path = sys.executable
            print(f"{py_path} - This path to python 3.9 ?")
            if not _yes(py_path.endswith("3.9")):
                py_path = input("Path to python 3.9 -> ")

        print("Send kill (if SIGTERM Timeout)")
        send_kill = "off"
        if _yes(False):
            send_kill = "on"

        with open("ToolKit.sample.service", "r") as file:
            sample = file.read().format(username=username, path=path, py_path=py_path, send_kill=send_kill)

        _clear()
        print(
            f"{sep}",
            f"{sample}",
            f"{sep}",
            f"Your username - {username}",
            f"Path to root of project - {path}",
            f"Path to python 3.9 - {py_path}",
            f"Send kill - {send_kill}",
            f"{sep}",
            "",
            "All correct ?",
            sep="\n"
        )
        if _yes(False):
            with open("ToolKit.service", "w") as file:
                file.write(sample)
            _clear()

            print("Link unit from /etc/systemd/system/ ?")
            if _yes():
                print(sep)

                cmd = "sudo mv ToolKit.service /etc/systemd/system/"
                print(cmd)
                _enter()
                os.system(cmd)

                print(sep)

                cmd = "sudo ln /etc/systemd/system/ToolKit.service ./ -s"
                print(cmd)
                _enter()
                os.system(cmd)
            break
        else:
            venv = False
            _clear()
    print(sep)
    _enter()
    return True


def config_generator():
    while True:
        main_token = input("Main bot token -> ")
        test_token = input("Test bot token -> ")
        _clear()
        print("This can be found here https://my.telegram.org/apps")
        api_id = input("Api id -> ")
        api_hash = input("Api hash -> ")
        _clear()

        with open("config.sample.py", "r") as file:
            sample = file.read().format(main_token=main_token, test_token=test_token, api_id=api_id, api_hash=api_hash)

        print(
            f"{sep}",
            f"{sample}",
            f"{sep}",
            f"Main bot token - {main_token!r}",
            f"Test bot token - {test_token!r}",
            f"Api id - {api_id!r}",
            f"Api hash - {api_hash!r}",
            f"{sep}",
            f"",
            "All correct ?",
            sep="\n"
        )
        if _yes(False):
            with open("config.py", "w") as file:
                file.write(sample)
            break
        else:
            _clear()
    return True


def rename_sample_files():
    for file in sample_files:
        re_file = file.replace(".sample", "")
        print(f"Rename {file} -> {re_file}")
        shutil.copy(file, re_file)
    _enter()
    return True


def compile_po_files():
    path = "libs/locales/"
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
            print(f"{po!r} - file is not exist, skipping {local!r} folder \t(run \"Generate po files\")")
            continue
        if not os.path.isdir(local + lc):
            os.mkdir(local + lc)
            print(f"Folder {local + lc!r} created ")

        mo = local + lc + mo
        cmd = f"msgfmt {po} -o {mo}"
        print(f"Execute \t {cmd!r}")
        if os.system(cmd) == 0:
            print(f"{po!r} - file compiled to - {mo!r}")
        else:
            print("COMPILE ERROR")
        print(sep)

    _enter()
    return True


def install_dependencies():
    global venv
    with open("dependencies", "r") as file:
        dependencies = file.read()
    print(
        "Install this ?",
        f"{sep}",
        f"{dependencies}",
        f"{sep}",
        sep="\n"
    )
    if _yes(venv):
        os.system("pip install -r dependencies")
        print("\nSuccessfully installed")
        _enter()
    return True


def generate_locales_files(new_locale: p.Optional[str] = None):
    path = "libs/src/"
    out_path = "libs/locales/"
    locales = os.listdir(out_path)

    if not locales:
        print("Locales not found")

    for lc in locales:
        print(lc + "\n")
        local = out_path + lc
        if os.path.isfile(local):
            os.remove(local)
            continue

        if new_locale and new_locale != lc:
            print(new_locale, lc)
            continue

        po = ""
        pot = local + f"/{lc}.pot"

        if os.path.isfile(local + f"/{lc}.po"):
            print("Joined po")
            po = local + f"/{lc}.po"

        print("Overwritten pot")
        with open(pot, "w"):
            pass

        for f in po_files:
            if po:
                os.system(f"xgettext -j {path + f} -o {po}")
            os.system(f"xgettext -j {path + f} -o {pot}")

        print(sep)
    if not new_locale:
        _enter()
    return True


def create_locales():
    path = "libs/locales/"
    while True:
        print("Leave blank to exit")
        lc = input("Name of locale (telegram format) -> ")
        if lc == "":
            break
        locale = path + lc

        if os.path.isfile(locale):
            os.remove(locale)
        if os.path.isdir(locale):
            print("Locale exist, skipping")
            print(sep)
            continue

        os.mkdir(locale)
        generate_locales_files(lc)

        _clear()
    _clear()
    print("""
To create the locale, the following remains:
    1 - Fill in .pot file (libs/locales/)
    2 - Run "Compile po files"
        """)
    _enter()
    return True


def delete_locales():
    path = "libs/locales/"
    while True:
        _clear()
        print("Leave blank to exit")
        locale = input("Name of locale -> ")
        if locale == "":
            break

        locale = path + locale

        print(sep)
        print(locale)
        print(sep)

        if os.path.isfile(locale):
            os.remove(locale)
        if not os.path.isdir(locale):
            print("Locale doesn't exist, skipping")
            _enter()
            continue

        print("ARE YOU SURE ?")
        if _yes(False):
            print("You 100% sure ?")
            if _yes(False):
                cmd = f"rm -rf {locale}"
                print(cmd)
                os.system(cmd)
    _clear()
    return True


if __name__ == '__main__':
    opts = {
        "Setup systemd unit": systemd_unit_generator,
        "Setup config.py": config_generator,
        "Rename sample files": rename_sample_files,
        "Compile po files": compile_po_files,
        "Install dependencies": install_dependencies,
        "Exit": exit,
        "0": None,
        "Generate or join locales files": generate_locales_files,
        "Create locales": create_locales,
        "Delete locales": delete_locales,
    }
    exit_index = 6
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
    _clear()
