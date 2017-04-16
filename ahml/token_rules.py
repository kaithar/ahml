import re
from ply.lex import TOKEN
from . import registry

states = []
tokens = []

matching_string = r'''
( \"([^"]|(?<=\\)\")*\"  
| \'([^']|(?<=\\)\')*\'
| \{([^\}]|(?<=\\)\})*\}
| [^"'\{][^})\]]*
)'''

states.append(('mdindent', 'inclusive'))
tokens.append('MARKDOWN_INDENT')
def t_mdindent_MARKDOWN_INDENT(t):
    r'^[ \t]*>[ \t]*'
    #t.value = len([x for x in t.value if x == '>'])
    return None

def t_MARKDOWN_INDENT(t):
    r'^[ \t]*>[ \t]*'
    #t.value = len([x for x in t.value if x == '>'])
    t.lexer.push_state('mdindent')
    return t

tokens.append('MARKDOWN_INDENT_END')
def t_mdindent_MARKDOWN_INDENT_END(t):
    r'^[ \t]*[^>]'
    t.lexer.pop_state()
    t.lexer.skip(-len(t.value))
    return t

def t_mdindent_eof(t):
    t.lexer.pop_state()
    t.type = 'MARKDOWN_INDENT_END'
    return t

states.append(('fenced', 'exclusive'))
def t_BEGIN_FENCE(t):
    r'^```([^\r\n]*)$'
    t.lexer.push_state('fenced')
    t.lexer.code = (t.lexer.lexmatch.group(3), []) # Note, group id is 1-indexed

def t_fenced_CODE(t):
    r'([^`\r\n]|`(?!``))+'
    t.lexer.code[1].append(t.value)

# Uses NEWLINE
def t_fenced_NEWLINE(t):
    r'\n\r?'
    t.lexer.code[1].append(t.value)
    t_NEWLINE(t)

tokens.append('COMPLETE_CODE')
def t_fenced_END_FENCE(t):
    r'^```(?=[\n\r]+)'
    t.lexer.pop_state()
    t.type = 'COMPLETE_CODE'
    t.value = (t.lexer.code[0], ''.join(t.lexer.code[1]).strip())
    return t

def t_fenced_error(t):
    print("Unexpected character '%s'"% t.value[0])
    return t

def t_ESCAPED_HASH(t):
    r'\\[#]'
    t.type = 'TEXT'
    t.value = '#'
    return t

# Some json matching...
states.append(('json', 'exclusive'))
tokens.append('JSON')
def t_json_OPEN(t):
    '{'
    t.lexer.block_depth += 1
    t.lexer.json_content += t.value

def t_json_CLOSE(t):
    '}'
    t.lexer.block_depth -= 1
    t.lexer.json_content += t.value
    if t.lexer.block_depth == 0:
        t.lexer.pop_state()
        t.type = 'JSON'
        t.value = t.lexer.json_content
        return t

def t_json_STUFF(t):
    '[^{}]+'
    if t.lexer.block_depth == 0:
        t.lexer.pop_state()
        t.lexer.skip(-1)
    t.lexer.json_content += t.value

def t_json_error(t):
    print('Probably impossible "{}"'.format(t.value))
    t.lexer.pop_state()
    t.lexer.skip(-1)
    return None

def t_json_eof(t):
    print('Probably impossible eof')
    t.lexer.pop_state()
    t.lexer.skip(-1)
    return None

states.append(('cmd', 'exclusive'))
def t_BEGIN_COMMAND(t):
    r'(?<!\\)\\(?![\\ \t\n\r])'
    t.lexer.push_state('cmd')
    t.lexer.command = []

tokens.append('FORCED_NEWLINE')
def t_cmd_FORCED_NEWLINE(t):
    r'n(ewline|[ \t]+|(?=[\n\r]))'
    t.lexer.pop_state()
    return t

def t_cmd_COMMAND(t):
    r'(?<=\\)[^ \t\n\r\[\{]+(?=[ \t\n\r\[\{])'
    l = t.value.lower()
    if (l in ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph', 'begin', 'end', 'sub']):
        t.lexer.command.append(l)
    elif (l == 'json'):
        t.lexer.json_content = ''
        t.lexer.block_depth = 0
        t.lexer.pop_state()
        t.lexer.push_state('json')
    else:
        t.lexer.command.append("plugin")
        t.lexer.command.append(l)

def t_cmd_error(t):
    print('Unknown command "{}"'.format(t.value))
    t.lexer.pop_state()
    return None

states.append(('opt', 'exclusive'))
def t_cmd_BEGIN_OPTION(t):
    r'\['
    t.lexer.push_state('opt')

def t_opt_END_OPTION(t):
    r'\]'
    t.lexer.pop_state()

@TOKEN(matching_string)
def t_opt_OPTION(t):
    t.lexer.command.append(('OPTION', t.value))

def t_opt_error(t):
    print('Unknown in option '+t.value)
    return None

states.append(('arg', 'exclusive'))
def t_cmd_BEGIN_ARGUMENT(t):
    r'\{'
    t.lexer.push_state('arg')

def t_arg_END_ARGUMENT(t):
    r'\}'
    t.lexer.pop_state()

@TOKEN(matching_string)
def t_arg_ARGUMENT(t):
    t.lexer.command.append(('ARGUMENT', t.value))

def t_arg_error(t):
    print('Unknown in option '+t.value)
    return None

tokens.append('COMMAND')
tokens.append('BEGIN_BLOCK')
tokens.append('BEGIN_BLOCK_CODE')
tokens.append('END_BLOCK')
states.append(('verbatim', 'exclusive'))
states.append(('begincode', 'exclusive'))
def t_cmd_END_COMMAND(t):
    r'(?=[ \t\n\r]|(?<=[}\]]))'
    t.lexer.pop_state()
    t.type = 'COMMAND'
    if (t.lexer.command[0] == 'begin'):
        if (t.lexer.command[-1][1] == 'verbatim'):
            t.lexer.push_state('verbatim')
            t.type = 'BEGIN_BLOCK_CODE'
        elif (t.lexer.command[-1][1] == 'code'):
            t.lexer.push_state('begincode')
            t.type = 'BEGIN_BLOCK_CODE'
        else:
            t.type = 'BEGIN_BLOCK'
    elif (t.lexer.command[0] == 'end'):
        t.type = 'END_BLOCK'
    t.value = t.lexer.command
    return t

tokens.append('CODE_FRAGMENT')
t_verbatim_CODE_FRAGMENT = r'([^\\\r\n]|\\(?!end\{\"?verbatim\"?\}))+'
t_begincode_CODE_FRAGMENT = r'([^\\\r\n]|\\(?!end\{\"?code\"?\}))+'

# Uses NEWLINE
def t_verbatim_NEWLINE(t):
    r'\n\r?'
    return t_NEWLINE(t)

def t_verbatim_END_BLOCK(t):
    r'^\\end\{[\'"]?verbatim[\'"]?\}'
    t.lexer.pop_state()
    t.lexer.skip(-len(t.value))

def t_verbatim_error(t):
    print("Unexpected character '%s'"% t.value[0])
    return t

# Uses NEWLINE
def t_begincode_NEWLINE(t):
    r'\n\r?'
    return t_NEWLINE(t)

def t_begincode_END_BLOCK(t):
    r'^\\end\{[\'"]?code[\'"]?\}'
    t.lexer.pop_state()
    t.lexer.skip(-len(t.value))

def t_begincode_error(t):
    print("Unexpected character '%s'"% t.value[0])
    return t

# Non prefixed lines are an exit
def t_list_HARD_EXIT(t):
    r'\n\r?(?=[ \t]*\n|[^ \t\r])'
    t.type = 'END_LIST'
    # Pop one layer
    t.lexer.list_prefix.pop()
    # Any more?
    if len(t.lexer.list_prefix):
        # There are, let's skip back one and spawn another end.
        t.lexer.skip(-len(t.value))
    else:
        # Nope, done.  Pop the state and eat this newline
        t.lexer.pop_state()
        t.lexer.lineno += 1
    # We don't care about value of this
    t.value = ''
    return t

tokens.append('LIST_ITEM')
tokens.append('END_LIST')
def t_list_LIST_PREFIX(t):
    r'(^([ \t]*)([-+*])([\#*\-ia]?)([\(\)/.]?)([ \t]*))'
    breakdown = re.compile(t_list_LIST_PREFIX.__doc__).search(t.value).groups()
    # ('    -*/ ', '    ', '-', '*', '/', ' ')
    L = len(breakdown[1])
    LL = t.lexer.list_prefix[-1][0]
    #print(t.value)
    #print(repr(t.lexer.list_prefix))
    # Unindent
    if (L < LL):
        t.type = 'END_LIST'
        t.lexer.list_prefix.pop()
        # More levels to consider
        if t.lexer.list_prefix:
            LL = t.lexer.list_prefix[-1][0]
            if (L > LL):
                # The depth is greater than we expected, this is a mismatch.
                raise Exception("List depth mismatch")
            # Skip back so we can process this again in the parent list
            t.lexer.skip(-len(t.value))
            t.value = '' 
            return t
        else:
            # We've emptied the list stack but we're still in a list, must be a mismatch
            raise Exception("List depth mismatch")
    elif (L > LL):
        # We're indenting!
        t.type = 'BEGIN_LIST'
        t.value = breakdown
        t.lexer.list_prefix.append((L, breakdown))
        return t
    else:
        # Continue previous list.
        t.type = 'LIST_ITEM'
        return t

# We do this one after t_list_LIST_PREFIX since anything that matches that will also match this.
def t_list_LIST_CONT_PREFIX(t):
    r'(^([ \t]+|(?=[\n\r]))([|][ \t]*)?)'
    vL = len(t.value)
    if vL:
        breakdown = re.compile(t_list_LIST_CONT_PREFIX.__doc__).search(t.value).groups()
    else:
        breakdown = ('','')
    # ('    | ', '    ', '| ')
    L = len(breakdown[1])
    LL = t.lexer.list_prefix[-1][0]
    #print(repr(t.value))
    #print(repr(t.lexer.list_prefix))
    #print(repr((L,LL,vL)))
    # Unindent
    if (L <= LL):
        t.type = 'END_LIST'
        t.lexer.list_prefix.pop()
        # More levels to consider
        if t.lexer.list_prefix:
            # Skip back so we can process this again in the parent list
            t.lexer.skip(-vL)
        else:
            # We've emptied the list stack, that means we're done with the list.
            t.lexer.pop_state()
        t.value = ''
        return t
    else:
        # Since it's a continuation we can indent or match, we don't care.
        # In both cases we discard the token completely.
        t.type = "WHITESPACE"


def t_list_eof(t):
    t.type = 'END_LIST'
    t.lexer.pop_state()
    return t

tokens.append('BEGIN_LIST')
states.append(('list', 'inclusive'))
def t_BEGIN_LIST(t):
    r'(^([ \t]*)([-+*])([\#*\-ia]?)([\(\)/.]?)([ \t]*))'
    breakdown = re.compile(t_BEGIN_LIST.__doc__).search(t.value).groups()
    # ('    -*/ ', '    ', '-', '*', '/', ' ')
    t.lexer.list_prefix = [(len(breakdown[1]), breakdown)]
    t.lexer.push_state('list')
    #print(repr(breakdown))
    t.value = breakdown
    return t 

tokens.append('DIRECTIVE')
def t_DIRECTIVE(t):
    r'^\#\#[ \t]*([^ \t].+)$'
    return t

tokens.append('COMMENT')
def t_COMMENT(t):
    r'^\#[ \t]*([^ \t].*)?$'
    return t

tokens.append('INLINE_CODE')
t_INLINE_CODE = r'(^|(?<=\W))`([^`\n\r]*)`($|(?=\W))'

tokens.append('BACKSLASH')
t_BACKSLASH = r'\\\\?'
tokens.append('LINE_CONTINUE')
t_LINE_CONTINUE = r'(?<!\\)\\(?=[ \t]*\n\r?)'

styled_text = r'''
    (?:(?<=\s)|^)                # Preceeded by whitespace or string start
    (?P<st_a> # 1st capture group
        (?P<st_b>[*/_\-+])       # These are the characters we care about
        (?P=st_b)(?P=st_b)?      # Match at least twice, optionally 3 times.
    )
    (?P<st_c> # 3rd capture group
        (?P<st_d>(?!(?P=st_b))[*/_\-+]) # Look ahead excludes previous match
        (?P=st_d)(?P=st_d)?             # The look-behind limits the match.
    )?                                  # Essentially requires to match both patterns
    (?P<st_e> # 5th capture group
        (?P<st_f>(?!(?P=st_b)|(?P=st_d))[*/_\-+]) 
        (?P=st_f)(?P=st_f)?             # Repeat for 3rd matcher
    )?
    (?P<st_g> # 7th capture group
        (?P<st_h>(?!(?P=st_b)|(?P=st_d)|(?P=st_f))[*/_\-+])
        (?P=st_h)(?P=st_h)?             # And a fourth, because why not.
    )?
    (?P<st_i> # 9th capture group
      (?:[^\\\s]         # Must not be followed by whitespace or a command
      |\\\\|\\[ \t]      # Other backslashes are fine 
      )
      (?:[^\\\n\r]       # Must not match newline or commands still 
      |[^ ]\\|\\[ ]|\\\\ # Non-command backslashes still fine 
      )*?                # Continue until we find an end pattern
    )
    (                   # Now we match the opening matches in reverse order
        (?(st_g)(?P=st_g)|)  # If the 7rd group matched then match here too
        (?(st_e)(?P=st_e)|)  # If the 5rd group matched then match here too
        (?(st_c)(?P=st_c)|)  # If the 3rd group matched then match here too
        (?P=st_a))           # 1st group is not optional, so match here too
    (?:(?=\s)|$)        # Followed by whitespace or string end
'''

tokens.append('STYLED_TEXT')
@TOKEN(styled_text)
def t_STYLED_TEXT(t):
    gs = [t.lexer.lexmatch.group('st_'+x) for x in ['a','c','e','g','i']]
    t.value = gs
    return t

tokens.append('URL')
def t_URL_BARE(t):
    r'(?P<url_a>https?://[^:/\s]+(:\d+)?(/([^?\s]+([?][^\s]+)?)?)?)'
    t.type = 'URL'
    t.value = (t.lexer.lexmatch.group('url_a'),
               t.lexer.lexmatch.group('url_a'))
    return t

def t_URL_MD(t):
    r'\[(?P<url_a>[^\]\n\r]*)\]\((?P<url_b>[^\)\n\r]*)\)'
    t.type = 'URL'
    t.value = (t.lexer.lexmatch.group('url_a'),
               t.lexer.lexmatch.group('url_b'))
    return t

def t_URL_WIKI(t):
    r'\[\[(?P<url_a>[^\]|\n\r]*)\|(?P<url_b>[^\]\n\r]*)\]\]'
    t.type = 'URL'
    t.value = (t.lexer.lexmatch.group('url_a'),
               t.lexer.lexmatch.group('url_b'))
    return t

tokens.append('TEXT')
t_TEXT = r'''
    ([^\\ \t\n#`]|\\\\)
    ([^ \t\n\r*/]|
     \*(?!\*[ \t\n\r])|
     /(?!/[ \t\n\r])
    )*'''

tokens.append('WHITESPACE')
def t_WHITESPACE(t):
    r'[ \t]+'
    return t

tokens.append('GRAVE')
t_GRAVE = r'`'

tokens.append('NEWLINE')
def t_D_NEWLINE(t):
    r'\n\r?(?=\n)'
    t.lexer.lineno += 1
    t.type = 'FORCED_NEWLINE'
    return t

def t_NEWLINE(t):
    r'\n\r?'
    t.lexer.lineno += 1
    return t

# Error handling rule
def t_error(t):
    print("Spotted character '%s'" % t.value[0])
    t.lexer.skip(1)
