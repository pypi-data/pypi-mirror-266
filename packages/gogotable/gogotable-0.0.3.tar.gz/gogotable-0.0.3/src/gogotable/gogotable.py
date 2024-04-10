def gogotable(headers, rows):  # noqa
    """
    Go Go Table

    :param headers: headers of the table
    :param rows: the data of the table
    :return: a list of strings representing the table
    """

    table = []

    # Find the size of each column
    columns_length = []
    for i, _ in enumerate(headers):
        try:
            column_length = max(len(str(row[i])) for row in rows)
        except IndexError:
            column_length = 0

        # Sometimes, the header size is greater than the value
        if len(headers[i]) > column_length:
            column_length = len(headers[i])

        columns_length.append(column_length)

    # Build the table header
    header_line = "|"
    for i, header in enumerate(headers):
        header_line = header_line + f" {header:^{columns_length[i]}} |"

    # Build the table border
    border = "|"
    for _ in range(len(header_line) - 2):  # 2 is the number of '|' characters
        border += "-"
    border += "|"

    table.append(border)
    table.append(header_line)
    table.append(border)

    # Build the table data rows
    for row in rows:
        data_line = "|"
        for i, _ in enumerate(headers):
            try:
                data_line = data_line + f" {row[i]:>{columns_length[i]}} |"
            except IndexError:
                data_line = data_line + f" {' ':>{columns_length[i]}} |"
        table.append(data_line)

    table.append(border)

    return table
