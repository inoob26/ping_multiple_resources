# Ping multiple resources

Tool created for ping list of addresses + port

## Install & Run

### Requirements

Script requires [tcping](https://github.com/paradiseduo/tcping) as main util

You should change addresses inside `source_list.cvs`

Content example:
```
example.com;80
example.com;443
google.com;443
google.com;1234
127.0.0.1;2222
```

You can change the path to source file using `SOURCE_FILE_PATH` parameter inside `config.py`

### Run

```shell
python ./ping_multiple_resources.py
03-07-2023 09:54:59 : ERROR : successful: 0, failed: 4 address: 127.0.0.1:2222
03-07-2023 09:54:59 : INFO : successful: 4, failed: 0 address: google.com:443
03-07-2023 09:54:59 : INFO : successful: 4, failed: 0 address: example.com:80
03-07-2023 09:54:59 : INFO : successful: 4, failed: 0 address: example.com:443
03-07-2023 09:55:00 : ERROR : successful: 0, failed: 4 address: google.com:1234
```

Script reads csv file with addresses and ports, then pings resouces using tcping, parses and streams output to the files:
- success.csv
- partial_fail.csv
- total_fail.csv

You can change names for output files inside `config.py`
```
FILES_MAP: dict[int, str] = {
    0: "success.csv",
    1: "partial_fail.csv",
    2: "total_fail.csv",
}
```

Script pings each address 4 times

You can change `DEFAULT_PING_TIMES` parameter inside `config.py`

## Compatibility

This script tested only on Unix compatible OS and python3.11