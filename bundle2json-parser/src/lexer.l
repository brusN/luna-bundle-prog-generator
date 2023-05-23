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

%}

%%
    /* Main blocks */
"define"                      { return KW_DEFINE; }
"df"                          { return KW_DF; }
"execution"                   { return KW_EXECUTION; }

    /* Sub blocks */
"run"                         { return KW_RUN; }
"from"                        { return KW_FROM; }
"to"                          { return KW_TO; }

"send"                        { return KW_SEND; }
"on"                          { return KW_ON; }
"rank"                        { return KW_RANK; }

"for"                         { return KW_FOR; }
".."                          { return KW_DOUBLE_DOT; }

    /* Symbols */
[0-9]+                        { yylval = std::string(yytext); return NUMBER; }
[A-Za-z_][A-Za-z0-9_]*        { yylval = std::string(yytext); return VARIABLE; }
"$"                           { return BUCK; }
"{"                           { return LCB; }
"}"                           { return RCB; }
"["                           { return LSB; }
"]"                           { return RSB; }
"+"                           { yylval = std::string(yytext); return PLUS; }
"-"                           { yylval = std::string(yytext); return MINUS; }
"*"                           { yylval = std::string(yytext); return MUL; }
"/"                           { yylval = std::string(yytext); return DIV; }
"("                           { return LP; }
")"                           { return RP; }
"="                           { return EQUAL; }
";"                           { return SEMICOLON; }

[ \n\t]                       {}
.                             {}

%%

int yywrap() {
    return 1;
}

int yyerror(char* s) {
    fprintf(stderr, "Error: %s\n", s);
    return 0;
}