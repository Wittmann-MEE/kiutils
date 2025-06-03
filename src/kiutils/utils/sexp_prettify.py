"""
Extracted from: https://github.com/mofosyne/sexp_prettify
"""

def sexp_prettify(source,
             compact_save=False,
             indent_char='\t',
             indent_size=1,
             consecutive_token_wrap_threshold=72,
             compact_list_prefixes={"pts"},
             compact_list_column_limit=99,
             shortform_prefixes={"font", "stroke", "fill", "offset", "rotate", "scale", "teardrop"}):
    """
    Reformats KiCad-like S-expressions to match a specific formatting style.

    Args:
        source (str): The source S-expression string.
        compact_save (bool): If True, enables compact mode formatting.

    Returns:
        str: The formatted S-expression.
    """

    # State tracking
    formatted = []
    list_depth = 0
    column = 0
    previous_non_space_output = ''
    in_quote = False
    escape_next_char = False
    singular_element = False
    space_pending = False
    wrapped_list = False
    scanning_for_prefix = False
    prefix_token = ''
    compact_list_mode = False
    compact_list_indent = 0
    shortform_mode = False
    shortform_indent = 0

    for c in source:

        # Parse quoted strings
        if c == '"' or in_quote:
            if space_pending:
                formatted.append(' ')
                column += 1
                space_pending = False

            if escape_next_char:
                escape_next_char = False
            elif c == '\\':
                escape_next_char = True
            elif c == '"':
                in_quote = not in_quote

            formatted.append(c)
            column += 1
            previous_non_space_output = c
            continue

        # Parse spaces and newlines
        if c.isspace():
            space_pending = True

            if scanning_for_prefix:
                if prefix_token in compact_list_prefixes:
                    compact_list_mode = True
                    compact_list_indent = list_depth
                elif compact_save and prefix_token in shortform_prefixes:
                    shortform_mode = True
                    shortform_indent = list_depth

                scanning_for_prefix = False
            continue

        # Parse opening parentheses
        if c == '(':
            space_pending = False
            if compact_list_mode:
                # In fixed listDepth, visually compact mode
                if column < compact_list_column_limit and previous_non_space_output == ')' or compact_list_column_limit == 0:
                    # Is a consecutive list and still within column limit (or column limit disabled)
                    formatted.append(' ')
                    column += 1
                else:
                    # List is either beyond column limit or not after another list move this list to the next line
                    formatted.append('\n')
                    formatted.append(indent_char * compact_list_indent * indent_size)
                    column = compact_list_indent * indent_size
            elif shortform_mode:
                # In one liner mode
                formatted.append(' ')
                column += 1
            else:
                # Start scanning for prefix for special list handling
                scanning_for_prefix = True
                prefix_token = ''
                if list_depth > 0:
                    # Print next line depth
                    formatted.append('\n')
                    formatted.append(indent_char * list_depth * indent_size)
                    column = list_depth * indent_size

            singular_element = True
            list_depth += 1

            formatted.append('(')
            column += 1

            previous_non_space_output = '('
            continue

        # Parse closing parentheses
        if c == ')':
            current_shortform_mode = shortform_mode
            space_pending = False
            scanning_for_prefix = False

            if list_depth > 0:
                list_depth -= 1

            if compact_list_mode and list_depth < compact_list_indent:
                compact_list_mode = False
            if shortform_mode and list_depth < shortform_indent:
                shortform_mode = False

            if wrapped_list:
                # This was a list with wrapped tokens so is already indented
                formatted.append('\n')
                formatted.append(indent_char * list_depth * indent_size)
                column = list_depth * indent_size
                if singular_element:
                    singular_element = False
                wrapped_list = False
            else:
                # Normal List
                if singular_element:
                    singular_element = False
                elif not current_shortform_mode:
                    formatted.append('\n')
                    formatted.append(indent_char * list_depth * indent_size)
                    column = list_depth * indent_size

            formatted.append(')')
            column += 1

            if list_depth <= 0:
                formatted.append('\n')
                column = 0

            previous_non_space_output = ')'
            continue

        # Parse characters
        if c != '\0':
            if previous_non_space_output == ')' and not shortform_mode:
                # Is Bare token after a list that should be on next line
                # Dev Note: In KiCAD this may indicate a flag bug
                formatted.append('\n')
                formatted.append(indent_char * list_depth * indent_size)
                column = list_depth * indent_size
                space_pending = False
            elif space_pending and not shortform_mode and not compact_list_mode and column >= consecutive_token_wrap_threshold:
                # Token is above wrap threshold. Move token to next line (If token wrap threshold is zero then this feature is disabled)
                wrapped_list = True
                formatted.append('\n')
                formatted.append(indent_char * list_depth * indent_size)
                column = list_depth * indent_size
                space_pending = False
            elif space_pending and previous_non_space_output != '(':
                formatted.append(' ')
                column += 1
                space_pending = False

            # Add to prefix scanning buffer if scanning for special list handling detection
            if scanning_for_prefix:
                prefix_token += c

            # Add character to list
            formatted.append(c)
            column += 1
            previous_non_space_output = c
            continue

    return ''.join(formatted)
