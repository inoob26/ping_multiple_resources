FILES_MAP: dict[int, str] = {
    0: "success.csv",
    1: "partial_fail.csv",
    2: "total_fail.csv",
}

DEFAULT_PING_TIMES: int = 4
SOURCE_FILE_PATH: str = "source_list.csv"
PING_TOOL: str = "tcping"
MAX_WORKERS: int = 5