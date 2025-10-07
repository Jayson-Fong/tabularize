<!--suppress HtmlDeprecatedAttribute-->
<div align="center">
   <h1>🗂️ Tabularize</h1>
</div>

<hr />

<div align="center">

[💼 Purpose](#purpose)

</div>

<hr />

# Purpose

Tabularize aids in the parsing of semi-structured data in a table-like format into Python dictionaries given no
knowledge of the expected data format.

While packages such as [csv](https://docs.python.org/3/library/csv.html), [pandas](https://pypi.org/project/pandas/),
and [TextFSM](https://pypi.org/project/textfsm/) exist, they require the input data to be in a more structured form. For 
example, requiring clearly distinguishable delimiters, fixed column widths, or knowledge about the data to deduce the 
start and end of a column based on data types. Tabularize is designed for instances where there can be guess-work due to 
input data not following these constraints.

This package's design takes influence from the [Name/Finger protocol](https://datatracker.ietf.org/doc/html/rfc742) due
to its non-standardized, human-readable status reports that tend to give machines a harder time.

# Samples

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>📇 Name/Finger Protocol</summary>

Tabularize is particularly useful for parsing the Name/Finger Protocol given that the `fingerd` server implementation is 
unknown due to its lack of standardization. However, if the server implementation is known, consider using a 
regular expression-based solution instead such as [TextFSM](https://pypi.org/project/textfsm/) as the data types can
help indicate the start and end of output.

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>🐧 Debian fingerd</summary>

```terminaloutput
Login     Name       Tty      Idle  Login Time   Office     Office Phone
alfred              *pts/0      1d  Oct 06 19:56 (192.168.1.1)
bert                 pts/1      2d  Oct 06 12:34 (:pts/0:S.0)
chase                pts/2      3d  Oct 06 05:43 (:pts/0:S.1)
```

```json
[
  {"Login": "alfred", "Tty": "*pts/0", "Idle": "1d", "Login Time": "Oct 06 19:56", "Office": "(192.168.1.1)"},
  {"Login": "bert", "Tty": "pts/1", "Idle": "2d", "Login Time": "Oct 06 12:34", "Office": "(:pts/0:S.0)"},
  {"Login": "chase", "Tty": "pts/2", "Idle": "3d", "Login Time": "Oct 06 05:43", "Office": "(:pts/0:S.1)"}
]
```

</details>

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>📡 Cisco fingerd</summary>

```terminaloutput
    Line       User       Host(s)              Idle       Location
   1 vty 0                idle                 00:00:00 
```

```json
[
  {"Line": "1 vty 0", "Host(s)": "idle", "Idle": "00:00:00"}
]
```

</details>

</details>

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>🖥️ Terminal Commands</summary>

<details style="border: 1px solid; border-radius: 8px; padding: 8px; margin-top: 4px;">
<summary>📋 w</summary>

The `w` command would typically include uptime information, which Tabularize does not know how to interpret. As a 
result, this example excludes it.

```terminaloutput
USER TTY      FROM    LOGIN@  IDLE WHAT
dave console  -      Sun20   23:26 -
eric s005     -      14:20       - w
```

```json
[
  {"USER": "dave", "TTY": "console", "FROM": "-", "LOGIN@": "Sun20", "IDLE": "23:26", "WHAT": "-"},
  {"USER": "eric", "TTY": "s005", "FROM": "-", "LOGIN@": "14:20", "IDLE": "-", "WHAT": "w"}
]
```

</details>

</details>