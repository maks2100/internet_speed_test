import json
import time
from pathlib import Path

import requests

CONFIG_FILE = "config.json"


def load_config() -> dict:
    """Загрузка конфигурации из файла."""
    config_path = Path(CONFIG_FILE)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Файл конфигурации '{CONFIG_FILE}' не найден"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def download_file(url: str, timeout: int) -> tuple[float, int]:
    """
    Выполняет один запрос.

    Returns:
        tuple:
            elapsed_time (секунды),
            downloaded_bytes (байты)
    """
    start_time = time.perf_counter()

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    content = response.content

    elapsed_time = time.perf_counter() - start_time

    return elapsed_time, len(content)


def main() -> None:
    config = load_config()

    url = config["url"]
    requests_count = config.get("requests_count", 10)
    timeout = config.get("timeout", 60)

    print(f"URL: {url}")
    print(f"Количество запросов: {requests_count}")
    print("-" * 50)

    total_time = 0.0
    total_bytes = 0

    for attempt in range(1, requests_count + 1):
        try:
            elapsed_time, downloaded_bytes = download_file(
                url=url,
                timeout=timeout
            )

            total_time += elapsed_time
            total_bytes += downloaded_bytes

            print(
                f"[{attempt}/{requests_count}] "
                f"Время: {elapsed_time:.2f} сек, "
                f"Размер: {downloaded_bytes / 1024 / 1024:.2f} МБ"
            )

        except requests.RequestException as error:
            print(f"[{attempt}/{requests_count}] Ошибка: {error}")

    if total_time == 0:
        print("\nНе удалось выполнить ни одного успешного запроса.")
        return

    average_time = total_time / requests_count

    # Скорость в мегабайтах в секунду
    speed_mb_s = (total_bytes / 1024 / 1024) / total_time

    print("\nРезультаты")
    print("-" * 50)
    print(f"Среднее время запроса: {average_time:.2f} сек")
    print(f"Общий объем данных: {total_bytes / 1024 / 1024:.2f} МБ")
    print(f"Средняя скорость: {speed_mb_s:.2f} МБ/с")


if __name__ == "__main__":
    main()
