nice commands:

```bash
# bash
clear && pypapple -d -max_cycles=32 tests/test.papple
```

`-log=v` or `log=verbose` prints out info, logs, and critical logs
`-log=l` or `log=log` prints out logs, and critical logs
`-log=c` or `log=critical` prints out critical logs

```bash
# windows
cls && pypapple -log=v tests/test.papple
cls && pypapple -log=l tests/test.papple
cls && pypapple -log=c tests/test.papple
```