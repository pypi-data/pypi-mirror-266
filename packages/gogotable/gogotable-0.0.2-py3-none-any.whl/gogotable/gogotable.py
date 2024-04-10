def to_table(headers, rows) -> str:  # noqa

    header_size = []
    for i, _ in enumerate(headers):
        try:
            max_value_length = max(len(row[i]) for row in rows)
        except TypeError:  # TypeError: object of type 'bool' has no len()
            max_value_length = 10

        # Sometimes, the header size is greater than the value
        if len(headers[i]) > max_value_length:
            header_size.append(len(headers[i]))
            continue

        header_size.append(max_value_length)

    print(header_size)

    # Build table header line
    # header = f"| {headers[0]:^{n}} | {headers[1]:^{b}} | {headers[2]:^{7}} | {headers[3]:^{c}} |"

    header_line = "|"
    for i, header in enumerate(headers):
        header_line = header_line + f" {header:^{header_size[i]}} |"

    line_len = len(header_line) - 2

    # Print the upper line
    print("|", end="")
    for _ in range(line_len):
        print("-", end="")
    print("|")

    print(header_line)

    # Print the upper line
    print("|", end="")
    for _ in range(line_len):
        print("-", end="")
    print("|")

    for row in rows:
        print("|", end="")
        header_line = ""
        for i, _ in enumerate(headers):
            header_line = header_line + f" {row[i]:>{header_size[i]}} |"

        print(header_line)

    # Print the upper line
    print("|", end="")
    for _ in range(line_len):
        print("-", end="")
    print("|")
