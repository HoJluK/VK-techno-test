import os
import subprocess
import sys

try:
    import gdown
    import ctypes
    import winreg
except ImportError:
    print("Устанавливаются необходимые библиотеки...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown", "ctypes", "winreg"])
    print("Библиотеки установлены.")

    import gdown
    import ctypes
    import winreg

url = "https://drive.google.com/uc?export=download&id=1IGENwFzLm8bBEboISadYSNEdxbnjz1fH"
reg_file_name = "game_settings.reg"
bat_file_name = "import_reg.bat"


def download_file(url, file_path):
    try:
        gdown.download(url, file_path, quiet=False)
        print(f"Файл скачан и сохранён как {file_path}")
    except Exception as e:
        print(f"Ошибка при скачивании файла {file_path}: {e}")


def create_and_run_bat(reg_file_path, bat_file_path):
    try:
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(f'reg import "{reg_file_path}"\n')
        subprocess.run(['cmd', '/c', bat_file_path], check=True)
        print("Настройки внесены в реестр")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при импорте файла {reg_file_path}: {e}")
    finally:
        os.remove(bat_file_path)


def find_steam():
    possible_paths = [
        os.path.join(os.getenv('ProgramFiles(x86)'), 'Steam'),
        os.path.join(os.getenv('ProgramFiles'), 'Steam'),
        "D:\\Program Files (x86)\\Steam",
        "D:\\Program Files\\Steam"
    ]
    for path in possible_paths:
        steam_executable = os.path.join(path, 'Steam.exe')
        if os.path.exists(steam_executable):
            return steam_executable
    return None


def find_game():
    def enum_keys(key, subkey):
        try:
            with winreg.OpenKey(key, subkey) as registry_key:
                for i in range(winreg.QueryInfoKey(registry_key)[0]):
                    subkey_name = winreg.EnumKey(registry_key, i)
                    yield subkey_name, registry_key
                    yield from enum_keys(key, subkey + "\\" + subkey_name)
        except WindowsError:
            pass

    def find_install_path(steam_id):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App {steam_id}") as key:
                return winreg.QueryValueEx(key, "InstallLocation")[0]
        except FileNotFoundError:
            return None

    game_steam_id = "1568590"
    install_path = find_install_path(game_steam_id)
    if install_path:
        game_executable = os.path.join(install_path, "Goose Goose Duck.exe")
        if os.path.exists(game_executable):
            return game_executable

    for subkey_name, registry_key in enum_keys(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE"):
        if "Goose Goose Duck" in subkey_name:
            try:
                install_path = winreg.QueryValueEx(registry_key, "InstallLocation")[0]
                game_executable = os.path.join(install_path, "Goose Goose Duck.exe")
                if os.path.exists(game_executable):
                    return game_executable
            except (FileNotFoundError, TypeError):
                pass

    return None


def launch_game():
    game_exe = find_game()

    if game_exe:
        subprocess.run([game_exe], shell=True)
        print("Игра запущена")
    else:
        steam_exe = find_steam()
        if steam_exe:
            subprocess.run([steam_exe])
            print("Steam запущен")
        else:
            print("Не удалось найти ни игру, ни Steam.")


def main():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Пожалуйста, запустите скрипт с правами администратора.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

    temp_dir = os.path.join(os.getenv('TEMP'), "GooseGooseDuckSetup")
    os.makedirs(temp_dir, exist_ok=True)
    reg_file_path = os.path.join(temp_dir, reg_file_name)
    bat_file_path = os.path.join(temp_dir, bat_file_name)

    download_file(url, reg_file_path)

    print("Попытка импорта настроек в реестр...")
    create_and_run_bat(reg_file_path, bat_file_path)
    os.remove(reg_file_path)

    print("Попытка запуска игры Goose Goose Duck...")
    launch_game()


if __name__ == "__main__":
    main()