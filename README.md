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
