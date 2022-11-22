%{
#include <iostream>
#include <string>

// Define YYSTYPE type
#ifndef YYSTYPE
#define YYSTYPE std::string
#endif
extern YYSTYPE yylval;
// ---

#include "grammar.hpp"

int yyerror(char* msg);

%}

%%
    /* Main blocks */
"define"                      { return KW_DEFINE; }
"execution"                   { return KW_EXECUTION; }

    /* Sub blocks */
"run"                         { return KW_RUN; }
"from"                        { return KW_FROM; }
"to"                          { return KW_TO; }

"send"                        { return KW_SEND; }
"on"                          { return KW_ON; }
"rank"                       { return KW_RANKS; }

    /* Symbols */
[0-9]+                        { yylval = std::string(yytext); return DIGIT; }
[A-Za-z_][A-Za-z0-9_]*        { yylval = std::string(yytext); return VARIABLE; }
"$"                           { return BUCK; }
"{"                           { return LCB; }
"}"                           { return RCB; }
"["                           { return LSB; }
"]"                           { return RSB; }
"="                           { return EQUAL; }
";"                           { return SEMICOLON; }
[ \n\t]                       {}
.                             {}

%%

int yyerror(char* msg) {
    fprintf(stderr, "%s\n", msg);
    return 1;
}

int yywrap() {
    return 1;
}