"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
import multiprocessing
import shlex
import subprocess
import argparse
from web_render.tool import log


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Example:\n'
                    '======='
    )
    parser.add_argument('commands', nargs='+', help='Список комманд')
    return parser.parse_args()


logger = log(__name__)

def run_command(command):
    args = shlex.split(command)
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка выполнения команды: {e}", exc_info=True)

def cli():

    args = parse_arguments()
    for cmd in args.commands:
        print(f"Run: {cmd}")
    command1, command2 = args.commands
    # Запуск команд в разных процессах
    process1 = multiprocessing.Process(target=run_command, args=(command1,))
    process2 = multiprocessing.Process(target=run_command, args=(command2,))

    try:
        process1.start()
        process2.start()

        process1.join()
        process2.join()
    except KeyboardInterrupt:
        logger.info("\nПроцессы остановлены по запросу пользователя (Ctrl + C)")
        process1.terminate()
        process2.terminate()

if __name__ == "__main__":
    cli()