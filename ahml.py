#! /usr/bin/python
# -*- coding: utf8 -*-
from __future__ import print_function
import sys
import re

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

mdsection = re.compile("^=+$")
mdsubsec = re.compile("^-+$")

tagfind = re.compile('^(\\\\([a-zA-Z_-]+)(?:\\[([^]]+)])?\\{("([^"]+)"|[^}]+)})')

sectiontags = {
    'section':       '<div class="structuralheader sectionheader"><span>{1}</span></div><div class="structuralbody sectionbody">',
    'subsection':    '<div class="structuralheader subsectionheader"><span>{1}</span></div><div class="structuralbody subsectionbody">',
    'subsubsection': '<div class="structuralheader subsubsectionheader"><span>{1}</span></div><div class="structuralbody subsubsectionbody">',
    'paragraph':     '<div class="structuralheader paragraphheader"><span>{1}</span></div><div class="structuralbody paragraphbody">',
    'subparagraph':  '<div class="structuralheader subparagraphheader"><span>{1}</span></div><div class="structuralbody subparagraphbody">'
}
in_section = False

in_blocks = False
in_latex_block = False

in_bold = False
in_italics = False
in_underline = False
in_strike = False

skip_newline = False

listfind = re.compile('^(([ ]+)([-+*])([#*ia-]?)([)(/.]?)[ ]+)')
listcont = re.compile('^([ ]+)[^ ]')

styles = {'#':'list-decimal', '*': 'list-star', 'i': 'list-roman', 'a': 'list-latin', '-': 'list-dash', '': 'list-basic'}
sugar = {')': '-par', '(': '-bothpar', '/': '-slash',  '.': '-period', '': '-bare' }

input = sys.stdin.readlines()
lenin = len(input)

for lineno in range(0,len(input)):
    input[lineno] = input[lineno].replace("\n", "")

body = ""
listdepth = []
listcounter = []
extracss = []
default_css = True

lineno = -1
while True:
    lineno += 1
    #body += str(lineno)
    if (lineno == lenin):
        break
    line = input[lineno]
    #body += line
    if (len(line) == 0):
        if (len(listdepth) > 0):
            while len(listdepth) > 0:
                body += "</div></li></ul>\n"
                listdepth.pop(0)
        elif (in_blocks):
            body = body[:-6] + '</div>' # The -6 is to trim the last '<br/>\n'
            in_blocks = False
        else:
            body += "<br/>\n"
        continue
    if (line[0] == '#'):
        if (line[1] == '!'):
            continue
        elif(line[1] == '#'):
            # This will be the control instructions
            if (line.startswith('## include ')):
                fn = line[11:]
                ninpm = open(fn).readlines()
                lenin += len(ninpm)

                for lineno2 in range(0,len(ninpm)):
                    input.insert(lineno + 1 + lineno2, ninpm[lineno2].replace("\n", ""))
                continue
            # ## inject
            if (line.startswith('## inject ')):
                fn = line[10:]
                body += open(fn).read()
                continue
            # ## css
            if (line.startswith('## css ')):
                fn = line[7:]
                extracss.append(fn)
                continue
            # ## suppress default_css
            if (line.startswith('## suppress default_css')):
                default_css = False
                continue
            pass
        else:
            # This will be comments
            pass
        continue
    if (line.startswith("```")):
        search = lineno+1
        while True:
            if search == lenin:
                body += line
                break
            elif input[search] == "```":
                if (len(line) > 3):
                    lexer = get_lexer_by_name(line[3:], stripall=True)
                    formatter = HtmlFormatter(linenos='table', cssclass="code")
                    body += '<div class="mono">'+highlight('\n'.join(input[lineno+1:search]), lexer, formatter)+'</div>'
                else:
                    body += '<div class="mono code">%s</div>'%(
                              '<br/>\n'.join(input[lineno+1:search]))
                lineno = search
                break
            else:
                search += 1
        continue
    if (line.startswith(">")):
        line = line.lstrip('> ')
        if (not in_blocks):
            in_blocks = True
            body += '<div class="inblock">'
    elif (in_blocks):
        body = body[:-6] + '</div>' # the -6 is to trim the last '<br/>\n'
        in_blocks = False
    if ((lineno+1 < len(input)) and (len(line) == len(input[lineno+1]))):
        if (mdsection.match(input[lineno+1])):
            #print("section header!")
            lineno += 1
            body += sectiontags["section"].format("section",line)
            continue
        elif(mdsubsec.match(input[lineno+1])):
            #print("subsec header!")
            lineno += 1
            body += sectiontags["subsection"].format("subsection",line)
            continue
    try:
        c = -1
        lf = listfind.match(line)
        if (lf):
            lfg = lf.groups()
            lfli, lfcont = len(lfg[1]), len(lfg[0])
            sys.stderr.write("%s\n"%repr(lfg))

            if (len(listdepth) == 0) or (lfli > listdepth[0]):
                listdepth.insert(0, lfli)
                listcounter.insert(0, lineno)
                ulclass = styles[lfg[3]] + sugar[lfg[4]]
                body += '<ul class="%s"><li><div>'%(ulclass)
            else:
                last = listdepth[0]
                if (lfli < last):
                    while len(listdepth) > 0 and (lfli < listdepth[0]):
                        body += "</div></li></ul>"
                        listdepth.pop(0)
                body += "</div></li><li><div>"
            c += lfcont
        else:
            lc = listcont.match(line)
            if (lc):
                lcl = len(lc.groups()[0])
                while (len(listdepth) > 0) and (lcl <= listdepth[0]):
                    body += "</div></li></ul>"
                    listdepth.pop(0)
                if (len(listdepth) > 0) and (lcl > listdepth[0]):
                    # continuation
                    c += lcl
            elif (len(listdepth) > 0):
                while len(listdepth) > 0:
                    body += "</div></li></ul>"
                    listdepth.pop(0)
        lenline = len(line)
        while True:
            c += 1
            if c >= lenline:
                break
            if (line[c] == '`'):
                w = line[c+1:].find('`')
                if (w >= 0):
                    body += '<span class="mono">%s</span>'%(line[c+1:c+w+1])
                    c += w+1
                    continue
            # in_bold = False
            # in_italics = False
            # in_underline = False
            # in_strike
            if (c+1 < lenline) and (line[c] == '*') and (line[c+1] == '*'):
                if (in_bold):
                    if (c+2 < lenline) and (line[c+2] == '*'):
                        body += '*'
                        c += 1
                    body += '</span>'
                    c += 2
                    in_bold = False
                else:
                    if (line[c+2:].find('**')):
                        body += '<span class="embolden">'
                        if (len(line) > c+2) and line[c+2] == '*':
                            body += '*'
                            c += 3
                        else:
                            c += 2
                        in_bold = True
                if (c == lenline):
                    break
            if (c+1 < lenline) and (line[c] == '/') and (line[c+1] == '/'):
                if (in_italics):
                    if (c+2 < lenline) and (line[c+2] == '/'):
                        body += '/'
                        c += 1
                    body += '</span>'
                    c += 2
                    in_italics = False
                else:
                    if (line[c+2:].find('//')):
                        body += '<span class="italizie">'
                        if (len(line) > c+2) and line[c+2] == '/':
                            body += '/'
                            c += 3
                        else:
                            c += 2
                        in_italics = True
                if (c == lenline):
                    break
            if (c+1 < lenline) and (line[c] == '_') and (line[c+1] == '_'):
                if (in_underline):
                    if (c+2 < lenline) and (line[c+2] == '_'):
                        body += '_'
                        c += 1
                    body += '</span>'
                    c += 2
                    in_underline = False
                elif (c == 0) or (line[c-1] == ' '):
                    if (line[c+2:].find('__')):
                        body += '<span class="underbar">'
                        if (len(line) > c+2) and line[c+2] == '_':
                            body += '_'
                            c += 3
                        else:
                            c += 2
                        in_underline = True
                if (c == lenline):
                    break
            if (c+1 < lenline) and (line[c] == '+') and (line[c+1] == '+'):
                if (in_strike):
                    if (c+2 < lenline) and (line[c+2] == '+'):
                        body += '+'
                        c += 1
                    body += '</span>'
                    c += 2
                    in_strike = False
                else:
                    if (line[c+2:].find('++')):
                        body += '<span class="stricken">'
                        if (len(line) > c+2) and line[c+2] == '+':
                            body += '+'
                            c += 3
                        else:
                            c += 2
                        in_strike = True
                if (c == lenline):
                    break
            if (c+1 < lenline) and (line[c] == '-') and (line[c+1] == '-'):
                if (in_strike):
                    if (c+2 < lenline) and (line[c+2] == '-'):
                        body += '-'
                        c += 1
                    body += '</span>'
                    c += 1
                    in_strike = False
                    continue
                else:
                    if (line[c+2:].find('-')):
                        body += '<span class="stricken">'
                        if (len(line) > c+2) and line[c+2] == '-':
                            body += '-'
                            c += 2
                        else:
                            c += 1
                        in_strike = True
                        continue
            if (line[c] == '[') and (line[c+1] == '[') and (line[c+2:].find(']]')):
                link = re.match('\[\[([^|]+)\|([^\]]+)\]\]', line[c:])
                c += link.end() - 1
                body += link.expand('<a href="\\2">\\1</a>')
                continue
            if (line[c] == '\\'):
                if (lenline > c+1) and line[c+1] == '\\':
                    body += "\\"
                    c += 1
                    continue
                elif (lenline > c+1) and line[c+1:].startswith('newline'):
                    body += "<br/>\n"
                    c += 7
                    continue
                elif (lenline > c+1) and line[c+1] == 'n':
                    body += "<br/>\n"
                    c += 1
                    continue
                #print(line[c:])
                tf = tagfind.match(line[c:])
                if tf:
                    parts = tf.groups()
                    cont = parts[4] or parts[3]
                    tag = parts[1]
                    #print("<<<< %s :: %s ... %s"%(tag, cont, line[c+len(parts[0])-1]))
                    if (tag in sectiontags):
                        if in_section:
                            body += "</div>"
                        body += sectiontags[tag].format(tag,cont)
                        in_section = True
                    elif (tag == "begin"):
                        if (cont == "block"):
                            if (in_blocks or in_latex_block):
                                body += parts[0]
                            else:
                                in_latex_block = True
                                body += '<div class="inblock">'
                                if (c + len(parts[0]) == lenline):
                                    skip_newline = True
                        elif (cont == "code"):
                            search = lineno
                            while True:
                                if search == lenin:
                                    body += line
                                    break
                                else:
                                    w = input[search].find('\\end{code}')
                                    if (w >= 0) and ((search > lineno) or (w > c)):
                                        # hit
                                        codeparts = []
                                        if (c + len(parts[0]) < lenline):
                                            codeparts.append(line[c + len(parts[0]):])
                                        if (search > lineno + 1):
                                            codeparts.append('\n'.join(input[lineno+1:search]))
                                        if (search > lineno) and (w != 0):
                                            codeparts.append(input[search][:w])
                                        codechunk = '\n'.join(codeparts)
                                        if parts[2]:
                                            lexer = get_lexer_by_name(parts[2], stripall=True)
                                            formatter = HtmlFormatter(linenos='table', cssclass="code")
                                            body += '<div class="mono">'+highlight(codechunk, lexer, formatter)+'</div>'
                                        else:
                                            body += '<div class="mono code" language="%s">'%(parts[2] or "")
                                            body += codechunk.replace('\n', '<br/>\n')+'<br/>\n</div>\n'
                                        lineno = search
                                        chunk = input[search][w + len('\\end{code}'):]
                                        if chunk:
                                            input.insert(search+1, chunk)
                                            lenin += 1
                                        skip_newline = True
                                        break
                                    else:
                                        search += 1
                            break
                        elif (cont == "verbatim"):
                            search = lineno
                            while True:
                                if search == lenin:
                                    body += line
                                    break
                                else:
                                    w = input[search].find('\\end{verbatim}')
                                    if (w >= 0) and ((search > lineno) or (w > c)):
                                        # hit
                                        verbparts = []
                                        if (c + len(parts[0]) < lenline):
                                            verbparts.append(line[c + len(parts[0]):])
                                        if (search > lineno + 1):
                                            verbparts.append('<br/>\n'.join(input[lineno+1:search]))
                                        if (search > lineno) and (w != 0):
                                            verbparts.append(input[search][:w])
                                        body += '<br/>\n'.join(verbparts) + ''
                                        lineno = search
                                        chunk = input[search][w + len('\\end{verbatim}'):]
                                        if chunk:
                                            input.insert(search+1, chunk)
                                            lenin += 1
                                        break
                                    else:
                                        search += 1
                            break
                    elif (tag == "end"):
                        if (cont == "block") and (in_latex_block):
                            body += '</div>'
                            in_latex_block = False
                        else:
                            body += parts[0]
                    else:
                        body += "%s: %s"%(tag, cont)
                    c += len(parts[0])-1
                    continue
            body += line[c]
    finally:
        if (line[-1:] == '\\' and line[-2:] != '\\\\'):
            body = body[:-1]
        elif (skip_newline):
            skip_newline = False
        else:
            body += "<br/>\n"

# Just in case we're actually in a section still.
if in_section:
    body += "</div>"

styles = {'#':'list-decimal', '*': 'list-star', 'i': 'lower-roman', 'a': 'lower-latin', '-': 'list-dash', '': 'list-basic'}
sugar = {')': '-par', '(': '-bothpar', '/': '-slash',  '.': '-period', '': '-bare' }

print('''<html><head><meta charset="UTF-8"/><style>
'''+HtmlFormatter().get_style_defs('.code')+'''
</style>''')

if (default_css):
    print ('''
<style>
body {
    font: 16px/24px sans-serif;
    margin: 1em;
}

ul {
    counter-reset: listcounter;
    margin-left: 0px;
    padding-left: 0px;
}

ul > li {
    list-style-type: none;
    padding: 2px;
}
ul > li > div {
    margin-left: 2.3em;
}
ul > li:before {
    width: 2em;
    text-align: right;
    counter-increment: listcounter;
    float: left;
}

ul.list-decimal-par     > li:before { content: counter(listcounter) ') ';       }
ul.list-decimal-bothpar > li:before { content: '(' counter(listcounter) ') ';   }
ul.list-decimal-slash   > li:before { content: counter(listcounter) '/ ';       }
ul.list-decimal-period  > li:before { content: counter(listcounter) '. ';       }
ul.list-decimal-bare    > li:before { content: counter(listcounter) '  ';       }

ul.list-star-par     > li:before { content: '*) ';          }
ul.list-star-bothpar > li:before { content: '(*) ';         }
ul.list-star-slash   > li:before { content: '*/ ';          }
ul.list-star-period  > li:before { content: '*. ';          }
ul.list-star-bare    > li:before { content: '*  ';          }

ul.list-roman-par     > li:before { content: counter(listcounter, lower-roman) ') ';        }
ul.list-roman-bothpar > li:before { content: '(' counter(listcounter, lower-roman) ') ';    }
ul.list-roman-slash   > li:before { content: counter(listcounter, lower-roman) '/ ';        }
ul.list-roman-period  > li:before { content: counter(listcounter, lower-roman) '. ';        }
ul.list-roman-bare    > li:before { content: counter(listcounter, lower-roman) '  ';        }

ul.list-latin-par     > li:before { content: counter(listcounter, lower-latin) ') ';        }
ul.list-latin-bothpar > li:before { content: '(' counter(listcounter, lower-latin) ') ';    }
ul.list-latin-slash   > li:before { content: counter(listcounter, lower-latin) '/ ';        }
ul.list-latin-period  > li:before { content: counter(listcounter, lower-latin) '. ';        }
ul.list-latin-bare    > li:before { content: counter(listcounter, lower-latin) '  ';        }

ul.list-dash-par     > li:before { content: '–) ';          }
ul.list-dash-bothpar > li:before { content: '(–) ';         }
ul.list-dash-slash   > li:before { content: '–/ ';          }
ul.list-dash-period  > li:before { content: '–. ';          }
ul.list-dash-bare    > li:before { content: '–  ';          }

ul.list-basic-par     > li:before { content: '•) ';         }
ul.list-basic-bothpar > li:before { content: '(•) ';        }
ul.list-basic-slash   > li:before { content: '•/ ';         }
ul.list-basic-period  > li:before { content: '•. ';         }
ul.list-basic-bare    > li:before { content: '•  ';         }

div.structuralheader
{
    font-weight: bold;
    margin-bottom: 1rem;
}

div.structuralheader span {  }

div.sectionheader { font-size: 1.8em; }
div.sectionheader span { padding-bottom: 0.25rem; border-bottom: 1px dashed gray; display:block; }

div.subsectionheader { font-size: 1.6em; }
div.subsectionheader span { padding-bottom: 0.25rem; border-bottom: 1px dashed gray; }

div.subsubsectionheader { font-size:1.4em; margin-bottom: 0.5rem; }
div.subsubsectionheader span { margin-bottom: 0.5rem; }

div.paragraphheader { font-size:1.2em; margin-bottom: 0.25rem; }
div.paragraphheader span {  }

div.subparagraphheader { font-size:14px; margin-bottom: 0; }
div.subparagraphheader span {  }

div.structuralbody {  }

.mono {
    font-family: "Lucida Console", Monaco, monospace;
}

span.mono {
    border: 1px solid rgba(143, 49, 196, 0.35);
    padding: 2px 5px 2px 5px;
    border-radius: 10px;
}

div.mono, div.inblock {
    margin: 0.5em 1.5em;
    padding: 0.25em 0em 0.25em 1em;
}

div.mono {
    border-left: 1px solid rgba(143, 49, 196, 0.35);
}

div.inblock {
    border-left: 1px dotted rgba(143, 49, 196, 0.35);
}

span.embolden { font-weight: bold; }
span.italizie { font-style: italic; }
span.underbar { text-decoration: underline; }
span.stricken { text-decoration: line-through; }

</style>''')

for x in extracss:
    print('<link rel="stylesheet" href="'+x+'" type="text/css"/>')

print('''</head><body>
      ''')
print(body)
print('</body></html>')


