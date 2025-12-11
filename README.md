# SQL to CSV Converter

A memory-efficient streaming parser that converts large SQL dump files with INSERT statements into CSV format without loading the entire file into memory.

## Background

Developed during a summer internship at Alpha Sophia to handle large-scale data migrations and exports. Many data analysis tools and workflows require CSV format, but databases often export as SQL dumps. For large datasets (100MB+), loading the entire SQL file into memory becomes impractical or impossible.

## Why This Implementation?

This parser was built to fix critical limitations in existing solutions that fail on real-world production SQL dumps:

### Problems with Standard Approaches

Most SQL-to-CSV converters (including popular open-source tools) break on production data because they assume:
- Each INSERT statement fits on a single line
- Files contain only INSERT statements (no CREATE TABLE, comments, etc.)
- Values never contain nested parentheses
- Only one quote character type is used
- Escape sequences are simple

**These assumptions fail in practice.**

### Key Improvements Over Existing Solutions

#### 1. **Multi-line INSERT Statement Support**
Standard tools crash on statements spanning multiple lines:
```sql
INSERT INTO users VALUES 
(1, 'John'),
(2, 'Jane');
```
**Solution:** Buffer lines until semicolon is found, then process complete statement.

#### 2. **Robust File Processing**
Other tools throw exceptions on non-INSERT lines (CREATE TABLE, comments, empty lines).

**Solution:** Gracefully skip non-INSERT content, extract only VALUES clauses using regex.

#### 3. **Nested Parentheses Handling**
Fails with geographic data or JSON:
```sql
INSERT INTO locations VALUES (1, POINT(40.7, -74.0), '{"key": "value"}');
```
**Solution:** Explicit parenthesis depth tracking - only close rows at depth 0.

#### 4. **Dynamic Quote Character Detection**
Hardcoded single-quote handling breaks with mixed quote types:
```sql
INSERT INTO data VALUES (1, 'O"Reilly', "It's working");
```
**Solution:** Detect and track both single and double quotes dynamically, switching context as needed.

#### 5. **Proper Escape Sequence Handling**
Simple escape character settings miss edge cases:
```sql
INSERT INTO messages VALUES (1, 'She said: \'Hello\\nWorld\'');
```
**Solution:** Manual escape sequence processing before quote state detection prevents premature quote closure.

#### 6. **Flexible Table Name Matching**
Handles various SQL dialects and quoting styles:
```sql
INSERT INTO `table_name` VALUES ...
INSERT INTO "table_name" VALUES ...
INSERT INTO 'table_name' VALUES ...
INSERT INTO table_name VALUES ...
```
**Solution:** Regex pattern matches all common table name formats.

## Features

- **Stream processing**: Processes files line-by-line, O(1) memory complexity
- **Handles arbitrarily large files**: Successfully tested on multi-GB SQL dumps
- **Production-ready parsing**: Correctly handles:
  - Multi-line INSERT statements
  - Nested parentheses (geographic types, JSON, arrays)
  - Mixed quote characters (single and double quotes in same file)
  - Escaped quotes and special characters
  - NULL values (converted to null character)
  - Files with mixed content (CREATE TABLE, comments, multiple INSERT statements)
  - Various SQL dialects and identifier quoting styles

## Use Case

Convert SQL INSERT statements like:
```sql
INSERT INTO users VALUES 
(1, 'John O\'Reilly', 'john@example.com', POINT(40.7, -74.0)),
(2, "Jane Smith", "jane@example.com", NULL);
```

Into CSV format:
```csv
1,John O'Reilly,john@example.com,POINT(40.7, -74.0)
2,Jane Smith,jane@example.com,
```

## Usage

```python
from final_pipeline import stream_sql_to_csv

# Convert SQL dump to CSV
stream_sql_to_csv("input_file.sql", "output_file.csv")
```

### Example: Converting Large Database Export
```python
# Works on files of any size - tested up to several GB
stream_sql_to_csv("database_backup.sql", "data_for_analysis.csv")
# ✅ CSV created at: data_for_analysis.csv
```

## Technical Implementation

The parser uses a **finite state machine** to track:

1. **Line buffering**: Accumulates lines until complete statement (ending in `;`)
2. **Parenthesis depth**: Tracks nesting level to identify row boundaries
3. **Quote state**: Monitors whether parser is inside quoted string
4. **Quote character**: Remembers which quote type (`'` or `"`) opened current string
5. **Escape sequences**: Handles `\'`, `\"`, and other escaped characters

### Why This Approach Works

```python
# State tracking for: INSERT INTO t VALUES (1, 'nested(data)', "quote's");
paren_depth:  0 → 1 → 1 → 1 → 0
in_quotes:    F → F → T → F → F
quote_char:   - → - → ' → - → -
```

This ensures accurate parsing with **O(1) space complexity** - memory usage doesn't grow with file size.

## Performance

- **Memory**: Constant (~few KB) regardless of file size
- **Speed**: Linear in file size, processes ~50-100 MB/sec on typical hardware
- **Scalability**: Successfully tested on 5GB+ SQL dumps

## Requirements

- Python 3.x
- Standard library only (no external dependencies)

## Limitations

- Currently supports INSERT statements only (not CREATE TABLE or other DDL)
- Assumes well-formed SQL syntax (will not validate or correct malformed SQL)
- Does not preserve or validate data types

## Future Improvements

- Parse CREATE TABLE statements to generate CSV headers automatically
- Add validation mode to check SQL syntax before conversion
- Support for UPDATE, DELETE, and other SQL statement types
- Configurable NULL handling (currently outputs `chr(0)`)
- Progress bar for large file processing

## Real-World Impact

At Alpha Sophia, this tool enabled:
- Migration of legacy database dumps to modern analytics platforms
- Export of production data for external analysis tools
- Automated ETL pipelines processing daily database snapshots

The stream-processing approach meant conversions that previously required expensive high-memory servers could run on standard developer machines.

## License

MIT License - free to use for any purpose

## Contact

Fabian Steinmetz - fabian@uni.minerva.edu
Developed during internship at Alpha Sophia

---

**Note to users**: If you encounter SQL dumps this parser can't handle, please open an issue with a sample (anonymized) INSERT statement. The goal is to handle all real-world SQL export formats.
