# SQL to CSV Converter

A memory-efficient streaming parser that converts large SQL dump files with INSERT statements into CSV format without loading the entire file into memory.

## Background

Developed during a summer internship at Alpha Sophia to handle large-scale data migrations and exports. Many data analysis tools and workflows require CSV format, but databases often export as SQL dumps. For large datasets (100MB+), loading the entire SQL file into memory becomes impractical or impossible.

## Features

- **Stream processing**: Processes files line-by-line without loading everything into memory
- **Handles large files**: Successfully processes SQL dumps of any size
- **Robust parsing**: Correctly handles:
  - Nested parentheses in values
  - Escaped quotes and special characters
  - NULL values
  - Multi-line INSERT statements
  - Various SQL dialects and quote styles

## Use Case

Convert SQL INSERT statements like:
```sql
INSERT INTO users VALUES (1, 'John Doe', 'john@example.com'), (2, 'Jane Smith', 'jane@example.com');
```

Into CSV format:
```csv
1,John Doe,john@example.com
2,Jane Smith,jane@example.com
```

## Usage
```python
from final_pipeline import stream_sql_to_csv

# Convert SQL dump to CSV
stream_sql_to_csv("input_file.sql", "output_file.csv")
```

## Technical Implementation

The parser uses a finite state machine approach to track:
- Parenthesis depth for nested values
- Quote states to handle strings correctly  
- Escape sequences in SQL strings
- Row boundaries across multi-line statements

This ensures accurate parsing even with complex SQL data while maintaining O(1) memory complexity.

## Why This Matters

Standard approaches using regex or loading entire files fail on production-scale datasets. This implementation:
- Processes arbitrarily large files with constant memory usage
- Handles real-world SQL edge cases (escaped quotes, NULLs, nested data)
- Provides a practical solution for data migration and ETL workflows

## Requirements

- Python 3.x
- Standard library only (no external dependencies)

## Limitations

- Currently supports INSERT statements only (not CREATE TABLE or other DDL)
- Assumes well-formed SQL syntax
- Does not validate data types

## Future Improvements

- Add support for CREATE TABLE statements to generate CSV headers automatically
- Add validation mode to check SQL syntax before conversion
- Support for additional SQL statement types

## License

MIT License - feel free to use for any purpose

## Contact

Fabian Steinmetz - fabian@uni.minerva.edu
Developed during internship at Alpha Sophia
