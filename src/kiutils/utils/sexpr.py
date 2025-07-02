#!/usr/bin/env python
# code extracted from: http://rosettacode.org/wiki/S-Expressions
# Originally taken from: https://gitlab.com/kicad/libraries/kicad-library-utils/-/blob/master/common/sexpr.py

import re

dbg = False

term_regex = r'''(?mx)
    \s*(?:
        (?P<brackl>\()|
        (?P<brackr>\))|
        (?P<num>[+-]?\d+\.\d+(?=[\ \)])|\-?\d+(?=[\ \)]))|
        (?P<sq>"(?:[^"]|(?<=\\)")*"(?:(?=\))|(?=\s)))|
        (?P<s>[^(^)\s]+)
       )'''

def parse_sexp(sexp):
    stack = []
    out = []
    if dbg: print("%-6s %-14s %-44s %-s" % tuple("term value out stack".split()))
    for termtypes in re.finditer(term_regex, sexp):
        term, value = [(t,v) for t,v in termtypes.groupdict().items() if v][0]
        if dbg: print("%-7s %-14s %-44r %-r" % (term, value, out, stack))
        if   term == 'brackl':
            stack.append(out)
            out = []
        elif term == 'brackr':
            assert stack, "Trouble with nesting of brackets"
            tmpout, out = out, stack.pop(-1)
            out.append(tmpout)
        elif term == 'num':
            v = float(value)
            if v.is_integer(): v = int(v)
            out.append(v)
        elif term == 'sq':
            out.append(value[1:-1].replace(r'\"', '"'))
        elif term == 's':
            out.append(value)
        else:
            raise NotImplementedError("Error: (%r, %r)" % (term, value))
    assert not stack, "Trouble with nesting of brackets"
    return out[0]

"""
Nearly a line-by-line translation of KiCad's C++ "Prettify" function (commit id: 1ec47a053baf50c3d7b57a0efbbd2d4dfc03fb6e)
Source: https://gitlab.com/kicad/code/kicad/-/blob/master/common/io/kicad/kicad_io_utils.cpp
"""

def sexp_prettify(source: str, compact_save: bool = False) -> str:
    """
    Formatting rules:
     - All extra (non-indentation) whitespace is trimmed
     - Indentation is one tab
     - Starting a new list (open paren) starts a new line with one deeper indentation
     - Lists with no inner lists go on a single line
     - End of multi-line lists (close paren) goes on a single line
    """
    # Configuration
    quote_char = '"'
    indent_char = '\t'
    indent_size = 1

    # Special casing for "(xy ...)" lists
    xy_special_case_column_limit = 99

    # When tokens get long, wrap after this many columns
    consecutive_token_wrap_threshold = 72

    # Working buffers and state
    formatted = []
    length = len(source)
    cursor = 0

    list_depth = 0
    last_non_whitespace = ''
    in_quote = False
    has_inserted_space = False
    in_multi_line_list = False
    in_xy = False
    in_short_form = False
    short_form_depth = 0
    column = 0
    backslash_count = 0

    def is_whitespace(ch: str) -> bool:
        return ch in (' ', '\t', '\n', '\r')

    def next_non_whitespace(idx: int) -> str:
        i = idx
        while i < length and is_whitespace(source[i]):
            i += 1
        return source[i] if i < length else '\0'

    def detect_xy(idx: int) -> bool:
        # look for "(xy "
        if idx + 3 >= length:
            return False
        return source[idx + 1] == 'x' and source[idx + 2] == 'y' and source[idx + 3] == ' '

    def detect_short_form(idx: int) -> bool:
        # look for an alpha token following the '('
        i = idx + 1
        token = []
        while i < length and source[i].isalpha():
            token.append(source[i])
            i += 1
        tok = ''.join(token)
        return tok in ("font", "stroke", "fill", "teardrop",
                       "offset", "rotate", "scale")

    while cursor < length:
        ch = source[cursor]
        nxt = next_non_whitespace(cursor)

        # Whitespace handling outside of a quoted string
        if is_whitespace(ch) and not in_quote:
            if (not has_inserted_space and
                    list_depth > 0 and
                    last_non_whitespace != '(' and
                    nxt != ')' and
                    nxt != '('):

                if in_xy or column < consecutive_token_wrap_threshold:
                    formatted.append(' ')
                    column += 1
                elif in_short_form:
                    formatted.append(' ')
                    column += 1
                else:
                    # newline + indent
                    nl = '\n' + (indent_char * (list_depth * indent_size))
                    formatted.append(nl)
                    column = list_depth * indent_size
                    in_multi_line_list = True

                has_inserted_space = True
            # else: drop extra whitespace
        else:
            # reset multi-space guard
            has_inserted_space = False

            # Open paren
            if ch == '(' and not in_quote:
                current_is_xy = detect_xy(cursor)
                current_is_short = compact_save and detect_short_form(cursor)

                if not formatted:
                    # very first character
                    formatted.append('(')
                    column += 1
                elif in_xy and current_is_xy and column < xy_special_case_column_limit:
                    # special "(xy ..." inline
                    formatted.append(' (')
                    column += 2
                elif in_short_form:
                    formatted.append(' (')
                    column += 2
                else:
                    # new line + indent + '('
                    nl = '\n' + (indent_char * (list_depth * indent_size)) + '('
                    formatted.append(nl)
                    column = list_depth * indent_size + 1

                in_xy = current_is_xy
                if current_is_short:
                    in_short_form = True
                    short_form_depth = list_depth

                list_depth += 1

            # Close paren
            elif ch == ')' and not in_quote:
                if list_depth > 0:
                    list_depth -= 1

                if in_short_form:
                    formatted.append(')')
                    column += 1
                elif last_non_whitespace == ')' or in_multi_line_list:
                    # end multi-line
                    nl = '\n' + (indent_char * (list_depth * indent_size)) + ')'
                    formatted.append(nl)
                    column = list_depth * indent_size + 1
                    in_multi_line_list = False
                else:
                    formatted.append(')')
                    column += 1

                if short_form_depth == list_depth:
                    in_short_form = False
                    short_form_depth = 0

            # Any other character
            else:
                # track backslashes for proper quote toggling
                if ch == '\\':
                    backslash_count += 1
                elif ch == quote_char and (backslash_count % 2) == 0:
                    in_quote = not in_quote

                if ch != '\\':
                    backslash_count = 0

                formatted.append(ch)
                column += 1

            if not is_whitespace(ch):
                last_non_whitespace = ch

        cursor += 1

    # POSIX-style trailing newline
    formatted.append('\n')
    return ''.join(formatted)
