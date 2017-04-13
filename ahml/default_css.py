text = r'''
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

'''