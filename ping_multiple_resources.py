import csv
import subprocess
import functools
from dataclasses import dataclass
from typing import List
from concurrent.futures import ThreadPoolExecutor
import asyncio
from threading import Lock
from enum import Enum
from config import *
import logging

from logging import config as loging_config

log_config = {
    "version": 1,
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        }
    },
    "formatters": {
        "std_out": {
            "format": "%(asctime)s : %(levelname)s : %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S",
        }
    },
}

loging_config.dictConfig(log_config)
logger = logging.getLogger()

partial_lock = Lock()
total_fail_lock = Lock()
success_lock = Lock()


@dataclass
class Source:
    source: str
    port: str
    times: int = DEFAULT_PING_TIMES


class StatusCodeEnum(Enum):
    SUCCESS = 0
    PARSIAL_FAIL = 1
    TOTAL_FAIL = 2


def write_status(status_code: int, source: Source):
    """Write source to specific file by status

    Response status_code
        0 - success
        1 - partial fail
        2 - total fail

    Args:
        status_code (int): ping response status code
        source (Source): _description_
    """
    match status_code:
        case StatusCodeEnum.SUCCESS.value:
            with success_lock:
                write_result_to_file(status_code, source)
        case StatusCodeEnum.PARSIAL_FAIL.value:
            with partial_lock:
                write_result_to_file(status_code, source)
        case StatusCodeEnum.TOTAL_FAIL.value:
            with total_fail_lock:
                write_result_to_file(status_code, source)


def write_result_to_file(status_code: int, source: Source):
    with open(FILES_MAP[status_code], mode="a") as f:
        f.write(f"{source.source};{source.port}\n")


def run_ping(source: Source):
    proc = subprocess.run(
        [PING_TOOL, "-c", str(source.times), source.source, source.port],
        capture_output=True,
    )
    output_lst = proc.stderr.decode().split()
    for indx, val in enumerate(output_lst):
        if val != "failed.":
            continue
        
        # total failed
        sucess_counter = output_lst[indx - 3]
        failed_counter = int(output_lst[indx - 1])
        msg = f"successful: {sucess_counter}, failed: {failed_counter} address: {source.source}:{source.port}"
        if failed_counter == source.times:
            write_status(StatusCodeEnum.TOTAL_FAIL.value, source)
            logger.error(msg)
        # partial failed
        elif failed_counter != 0:
            write_status(StatusCodeEnum.PARSIAL_FAIL.value, source)
            logger.error(msg)
        else:
            write_status(StatusCodeEnum.SUCCESS.value, source)
            logger.info(msg)


def get_sources() -> List[Source]:
    result = []
    with open(SOURCE_FILE_PATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for row in csv_reader:
            result.append(Source(source=row[0], port=row[1]))

    return result


async def main():
    sources = get_sources()
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        tasks = tuple(
            loop.run_in_executor(pool, functools.partial(run_ping, source))
            for source in sources
        )
        await asyncio.gather(*tasks)


asyncio.run(main())
