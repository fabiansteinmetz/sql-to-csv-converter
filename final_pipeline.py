import re
import csv
import io

def stream_sql_to_csv(sql_file_path, output_file_path):
    """
    Stream-processes an SQL file with INSERT statements into a CSV file without loading the entire file into memory.
    """
    def extract_values(line_buffer):
        """
        Extracts the VALUES(...) part from a complete INSERT statement.
        """
        pattern = r'INSERT\s+INTO\s+(?:`[^`]+`|"[^"]+"|\'[^\']+\'|\w+).*?VALUES\s*(.+);'
        match = re.search(pattern, line_buffer, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        return None

    def parse_values_string(values_content, csv_writer):
        """
        Parses the VALUES content and writes rows to the CSV writer.
        """
        values_content = values_content.strip()
        if not values_content.startswith('('):
            values_content = '(' + values_content

        current_row = []
        paren_depth = 0
        current_value = ""
        in_quotes = False
        quote_char = None
        i = 0

        while i < len(values_content):
            char = values_content[i]

            if char == '\\' and i + 1 < len(values_content):
                current_value += char
                i += 1
                if i < len(values_content):
                    current_value += values_content[i]
                i += 1
                continue

            if char in ("'", '"') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None

            if not in_quotes:
                if char == '(':
                    if paren_depth == 0 and current_value.strip() and current_row:
                        csv_writer.writerow(current_row)
                        current_row = []
                        current_value = ""
                    paren_depth += 1
                    if paren_depth > 1:
                        current_value += char
                elif char == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        value = current_value.strip()
                        if value.upper() == 'NULL':
                            current_row.append(chr(0))
                        else:
                            if ((value.startswith("'") and value.endswith("'")) or 
                                (value.startswith('"') and value.endswith('"'))):
                                value = value[1:-1]
                            value = value.replace("\\'", "'").replace('\\"', '"')
                            current_row.append(value)
                        current_value = ""
                        if current_row:
                            csv_writer.writerow(current_row)
                            current_row = []
                    else:
                        current_value += char
                elif char == ',' and paren_depth == 1:
                    value = current_value.strip()
                    if value.upper() == 'NULL':
                        current_row.append(chr(0))
                    else:
                        if ((value.startswith("'") and value.endswith("'")) or 
                            (value.startswith('"') and value.endswith('"'))):
                            value = value[1:-1]
                        value = value.replace("\\'", "'").replace('\\"', '"')
                        current_row.append(value)
                    current_value = ""
                elif char == ',' and paren_depth == 0:
                    current_value = ""
                else:
                    if paren_depth > 0:
                        current_value += char
            else:
                current_value += char

            i += 1

        if current_row:
            csv_writer.writerow(current_row)

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file, open(output_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
            buffer = ""
            for line in sql_file:
                buffer += line
                if line.strip().endswith(';'):
                    values_content = extract_values(buffer)
                    if values_content:
                        parse_values_string(values_content, csv_writer)
                    buffer = ""
        print(f"✅ CSV created at: {output_file_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
stream_sql_to_csv("C03_AffiliationList.sql", "C03_AffiliationList.csv")