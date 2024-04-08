## Example

```python
import os
from FileSystemModel import FileSystemModel

fsm = FileSystemModel(os.getcwd())
fsm.show()
```

The program running result is as follows:

```text
+---------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                     C:\Users\Zhang Henghua\PycharmProjects\packaging                                                    |
+----+----------------+-------------------------------+-----------+--------+---------------------+---------------------+----------+----------+------------+
| ID | Basename       | Owner                         |      Size |  Type  |    Creation Time    |  Modification Time  | Readable | Writable | Executable |
+----+----------------+-------------------------------+-----------+--------+---------------------+---------------------+----------+----------+------------+
|  0 | .idea          | DESKTOP-O8I71AC\Zhang Henghua |           | <DIR>  | 2024/04/08 09:22:41 | 2024/04/08 09:37:23 |   True   |   True   |    True    |
|  1 | src            | DESKTOP-O8I71AC\Zhang Henghua |           | <DIR>  | 2024/04/08 09:23:02 | 2024/04/08 14:16:41 |   True   |   True   |    True    |
|  2 | LICENSE        | DESKTOP-O8I71AC\Zhang Henghua |   1.04 KB | <FILE> | 2024/04/08 14:41:49 | 2024/04/08 14:46:12 |   True   |   True   |    True    |
|  3 | main.py        | DESKTOP-O8I71AC\Zhang Henghua | 106.00  B | <FILE> | 2024/04/08 09:22:42 | 2024/04/08 14:53:12 |   True   |   True   |    True    |
|  4 | pyproject.toml | DESKTOP-O8I71AC\Zhang Henghua | 507.00  B | <FILE> | 2024/04/08 14:43:26 | 2024/04/08 14:52:38 |   True   |   True   |    True    |
|  5 | README.md      | DESKTOP-O8I71AC\Zhang Henghua |   0.00  B | <FILE> | 2024/04/08 14:43:33 | 2024/04/08 14:43:33 |   True   |   True   |    True    |
+----+----------------+-------------------------------+-----------+--------+---------------------+---------------------+----------+----------+------------+
```

More operations:

```python
fsm.cd('..')  # Return to the previous level directory.
fsm.show(owner=False, ctime=False, executable=False)
```

Result:

```text
+--------------------------------------------------------------------------------+
|                     C:\Users\Zhang Henghua\PycharmProjects                     |
+----+----------------+------+-------+---------------------+----------+----------+
| ID | Basename       | Size |  Type |  Modification Time  | Readable | Writable |
+----+----------------+------+-------+---------------------+----------+----------+
|  0 | AI             |      | <DIR> | 2024/03/29 23:36:13 |   True   |   True   |
|  1 | CheckParameter |      | <DIR> | 2024/03/05 17:04:45 |   True   |   True   |
|  2 | diff           |      | <DIR> | 2024/03/01 10:39:34 |   True   |   True   |
|  3 | diode_jagte    |      | <DIR> | 2024/02/28 10:23:07 |   True   |   True   |
|  4 | GenImage       |      | <DIR> | 2024/03/14 16:56:07 |   True   |   True   |
|  5 | moscap         |      | <DIR> | 2024/02/27 16:30:19 |   True   |   True   |
|  6 | packaging      |      | <DIR> | 2024/04/08 15:01:55 |   True   |   True   |
+----+----------------+------+-------+---------------------+----------+----------+
```

Using the `print()` instead of the `.show()`:

```python
fsm.cd('GenImage')
print(fsm)
```

Result:

```text
Dir(name='.idea', ctime=1709883190, mtime=1710503743, owner='DESKTOP-O8I71AC\\Zhang Henghua', readable=True, writable=True, executable=True)
Dir(name='images', ctime=1710138779, mtime=1710141138, owner='DESKTOP-O8I71AC\\Zhang Henghua', readable=True, writable=True, executable=True)
File(name='20240307_N1X V1.0 D.xlsx', size=11876, ctime=1709883343, mtime=1710141080, owner='DESKTOP-O8I71AC\\Zhang Henghua'), readable=True, writable=True, executable=True)
File(name='main.py', size=5933, ctime=1709883191, mtime=1710406567, owner='DESKTOP-O8I71AC\\Zhang Henghua'), readable=True, writable=True, executable=True)
File(name='test.py', size=279, ctime=1710138588, mtime=1710141548, owner='DESKTOP-O8I71AC\\Zhang Henghua'), readable=True, writable=True, executable=True)
```

## Installation

```shell
pip install FileSystemModel-Python
```
