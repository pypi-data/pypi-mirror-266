# Generated from ../LiteExpr.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,57,152,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,1,
        0,1,0,1,0,3,0,17,8,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,53,8,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,5,1,99,8,1,10,1,12,1,102,9,1,1,2,1,2,1,2,1,
        2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,5,2,115,8,2,10,2,12,2,118,9,2,1,3,
        1,3,1,3,5,3,123,8,3,10,3,12,3,126,9,3,1,3,3,3,129,8,3,1,3,3,3,132,
        8,3,1,4,1,4,1,4,1,4,1,5,1,5,1,5,5,5,141,8,5,10,5,12,5,144,9,5,1,
        5,3,5,147,8,5,1,5,3,5,150,8,5,1,5,0,2,2,4,6,0,2,4,6,8,10,0,8,1,0,
        7,8,1,0,9,12,1,0,31,45,1,0,14,16,1,0,11,12,1,0,17,19,1,0,20,23,1,
        0,24,25,180,0,16,1,0,0,0,2,52,1,0,0,0,4,103,1,0,0,0,6,131,1,0,0,
        0,8,133,1,0,0,0,10,149,1,0,0,0,12,13,3,2,1,0,13,14,5,0,0,1,14,17,
        1,0,0,0,15,17,5,0,0,1,16,12,1,0,0,0,16,15,1,0,0,0,17,1,1,0,0,0,18,
        19,6,1,-1,0,19,53,5,51,0,0,20,53,5,52,0,0,21,53,5,54,0,0,22,53,5,
        53,0,0,23,24,5,1,0,0,24,25,3,2,1,0,25,26,5,2,0,0,26,53,1,0,0,0,27,
        28,3,4,2,0,28,29,5,1,0,0,29,30,3,10,5,0,30,31,5,2,0,0,31,53,1,0,
        0,0,32,53,3,4,2,0,33,34,5,3,0,0,34,35,3,6,3,0,35,36,5,4,0,0,36,53,
        1,0,0,0,37,38,5,5,0,0,38,39,3,10,5,0,39,40,5,6,0,0,40,53,1,0,0,0,
        41,42,3,4,2,0,42,43,7,0,0,0,43,53,1,0,0,0,44,45,7,0,0,0,45,53,3,
        4,2,0,46,47,7,1,0,0,47,53,3,2,1,16,48,49,3,4,2,0,49,50,7,2,0,0,50,
        51,3,2,1,4,51,53,1,0,0,0,52,18,1,0,0,0,52,20,1,0,0,0,52,21,1,0,0,
        0,52,22,1,0,0,0,52,23,1,0,0,0,52,27,1,0,0,0,52,32,1,0,0,0,52,33,
        1,0,0,0,52,37,1,0,0,0,52,41,1,0,0,0,52,44,1,0,0,0,52,46,1,0,0,0,
        52,48,1,0,0,0,53,100,1,0,0,0,54,55,10,15,0,0,55,56,5,13,0,0,56,99,
        3,2,1,15,57,58,10,14,0,0,58,59,7,3,0,0,59,99,3,2,1,15,60,61,10,13,
        0,0,61,62,7,4,0,0,62,99,3,2,1,14,63,64,10,12,0,0,64,65,7,5,0,0,65,
        99,3,2,1,13,66,67,10,11,0,0,67,68,7,6,0,0,68,99,3,2,1,12,69,70,10,
        10,0,0,70,71,7,7,0,0,71,99,3,2,1,11,72,73,10,9,0,0,73,74,5,26,0,
        0,74,99,3,2,1,10,75,76,10,8,0,0,76,77,5,27,0,0,77,99,3,2,1,9,78,
        79,10,7,0,0,79,80,5,28,0,0,80,99,3,2,1,8,81,82,10,6,0,0,82,83,5,
        29,0,0,83,99,3,2,1,7,84,85,10,5,0,0,85,86,5,30,0,0,86,99,3,2,1,6,
        87,88,10,3,0,0,88,89,5,46,0,0,89,90,3,2,1,0,90,91,5,47,0,0,91,92,
        3,2,1,3,92,99,1,0,0,0,93,94,10,2,0,0,94,95,5,48,0,0,95,99,3,2,1,
        3,96,97,10,1,0,0,97,99,5,48,0,0,98,54,1,0,0,0,98,57,1,0,0,0,98,60,
        1,0,0,0,98,63,1,0,0,0,98,66,1,0,0,0,98,69,1,0,0,0,98,72,1,0,0,0,
        98,75,1,0,0,0,98,78,1,0,0,0,98,81,1,0,0,0,98,84,1,0,0,0,98,87,1,
        0,0,0,98,93,1,0,0,0,98,96,1,0,0,0,99,102,1,0,0,0,100,98,1,0,0,0,
        100,101,1,0,0,0,101,3,1,0,0,0,102,100,1,0,0,0,103,104,6,2,-1,0,104,
        105,5,55,0,0,105,116,1,0,0,0,106,107,10,3,0,0,107,108,5,49,0,0,108,
        115,3,4,2,4,109,110,10,2,0,0,110,111,5,5,0,0,111,112,3,2,1,0,112,
        113,5,6,0,0,113,115,1,0,0,0,114,106,1,0,0,0,114,109,1,0,0,0,115,
        118,1,0,0,0,116,114,1,0,0,0,116,117,1,0,0,0,117,5,1,0,0,0,118,116,
        1,0,0,0,119,124,3,8,4,0,120,121,5,50,0,0,121,123,3,8,4,0,122,120,
        1,0,0,0,123,126,1,0,0,0,124,122,1,0,0,0,124,125,1,0,0,0,125,128,
        1,0,0,0,126,124,1,0,0,0,127,129,5,50,0,0,128,127,1,0,0,0,128,129,
        1,0,0,0,129,132,1,0,0,0,130,132,1,0,0,0,131,119,1,0,0,0,131,130,
        1,0,0,0,132,7,1,0,0,0,133,134,5,55,0,0,134,135,5,47,0,0,135,136,
        3,2,1,0,136,9,1,0,0,0,137,142,3,2,1,0,138,139,5,50,0,0,139,141,3,
        2,1,0,140,138,1,0,0,0,141,144,1,0,0,0,142,140,1,0,0,0,142,143,1,
        0,0,0,143,146,1,0,0,0,144,142,1,0,0,0,145,147,5,50,0,0,146,145,1,
        0,0,0,146,147,1,0,0,0,147,150,1,0,0,0,148,150,1,0,0,0,149,137,1,
        0,0,0,149,148,1,0,0,0,150,11,1,0,0,0,12,16,52,98,100,114,116,124,
        128,131,142,146,149
    ]

class LiteExprParser ( Parser ):

    grammarFileName = "LiteExpr.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'", "'{'", "'}'", "'['", "']'", 
                     "'++'", "'--'", "'!'", "'~'", "'+'", "'-'", "'**'", 
                     "'*'", "'/'", "'%'", "'<<'", "'>>'", "'>>>'", "'<'", 
                     "'<='", "'>'", "'>='", "'=='", "'!='", "'&'", "'^'", 
                     "'|'", "'&&'", "'||'", "'='", "'**='", "'*='", "'/='", 
                     "'%='", "'+='", "'-='", "'<<='", "'>>='", "'>>>='", 
                     "'&='", "'^='", "'|='", "'&&='", "'||='", "'?'", "':'", 
                     "';'", "'.'", "','" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "STRING", "DOUBLE", 
                      "INT", "HEX", "ID", "WS", "COMMENT" ]

    RULE_file = 0
    RULE_expr = 1
    RULE_varname = 2
    RULE_pairlist = 3
    RULE_pair = 4
    RULE_list = 5

    ruleNames =  [ "file", "expr", "varname", "pairlist", "pair", "list" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    T__43=44
    T__44=45
    T__45=46
    T__46=47
    T__47=48
    T__48=49
    T__49=50
    STRING=51
    DOUBLE=52
    INT=53
    HEX=54
    ID=55
    WS=56
    COMMENT=57

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class FileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def EOF(self):
            return self.getToken(LiteExprParser.EOF, 0)

        def getRuleIndex(self):
            return LiteExprParser.RULE_file

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFile" ):
                return visitor.visitFile(self)
            else:
                return visitor.visitChildren(self)




    def file_(self):

        localctx = LiteExprParser.FileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_file)
        try:
            self.state = 16
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1, 3, 5, 7, 8, 9, 10, 11, 12, 51, 52, 53, 54, 55]:
                self.enterOuterAlt(localctx, 1)
                self.state = 12
                self.expr(0)
                self.state = 13
                self.match(LiteExprParser.EOF)
                pass
            elif token in [-1]:
                self.enterOuterAlt(localctx, 2)
                self.state = 15
                self.match(LiteExprParser.EOF)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return LiteExprParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class CallContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def varname(self):
            return self.getTypedRuleContext(LiteExprParser.VarnameContext,0)

        def list_(self):
            return self.getTypedRuleContext(LiteExprParser.ListContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCall" ):
                return visitor.visitCall(self)
            else:
                return visitor.visitChildren(self)


    class VariableContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def varname(self):
            return self.getTypedRuleContext(LiteExprParser.VarnameContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariable" ):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)


    class UnaryOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryOp" ):
                return visitor.visitUnaryOp(self)
            else:
                return visitor.visitChildren(self)


    class PostfixOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def varname(self):
            return self.getTypedRuleContext(LiteExprParser.VarnameContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPostfixOp" ):
                return visitor.visitPostfixOp(self)
            else:
                return visitor.visitChildren(self)


    class StringContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(LiteExprParser.STRING, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitString" ):
                return visitor.visitString(self)
            else:
                return visitor.visitChildren(self)


    class TermContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTerm" ):
                return visitor.visitTerm(self)
            else:
                return visitor.visitChildren(self)


    class DoubleContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def DOUBLE(self):
            return self.getToken(LiteExprParser.DOUBLE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDouble" ):
                return visitor.visitDouble(self)
            else:
                return visitor.visitChildren(self)


    class IntContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(LiteExprParser.INT, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInt" ):
                return visitor.visitInt(self)
            else:
                return visitor.visitChildren(self)


    class TernaryOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.op1 = None # Token
            self.op2 = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LiteExprParser.ExprContext)
            else:
                return self.getTypedRuleContext(LiteExprParser.ExprContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTernaryOp" ):
                return visitor.visitTernaryOp(self)
            else:
                return visitor.visitChildren(self)


    class ArrayContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def list_(self):
            return self.getTypedRuleContext(LiteExprParser.ListContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArray" ):
                return visitor.visitArray(self)
            else:
                return visitor.visitChildren(self)


    class HexContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def HEX(self):
            return self.getToken(LiteExprParser.HEX, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHex" ):
                return visitor.visitHex(self)
            else:
                return visitor.visitChildren(self)


    class ObjectContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def pairlist(self):
            return self.getTypedRuleContext(LiteExprParser.PairlistContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitObject" ):
                return visitor.visitObject(self)
            else:
                return visitor.visitChildren(self)


    class AssignOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def varname(self):
            return self.getTypedRuleContext(LiteExprParser.VarnameContext,0)

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignOp" ):
                return visitor.visitAssignOp(self)
            else:
                return visitor.visitChildren(self)


    class ParenContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParen" ):
                return visitor.visitParen(self)
            else:
                return visitor.visitChildren(self)


    class PrefixOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def varname(self):
            return self.getTypedRuleContext(LiteExprParser.VarnameContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrefixOp" ):
                return visitor.visitPrefixOp(self)
            else:
                return visitor.visitChildren(self)


    class BinaryOpContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LiteExprParser.ExprContext)
            else:
                return self.getTypedRuleContext(LiteExprParser.ExprContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBinaryOp" ):
                return visitor.visitBinaryOp(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = LiteExprParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                localctx = LiteExprParser.StringContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 19
                self.match(LiteExprParser.STRING)
                pass

            elif la_ == 2:
                localctx = LiteExprParser.DoubleContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 20
                self.match(LiteExprParser.DOUBLE)
                pass

            elif la_ == 3:
                localctx = LiteExprParser.HexContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 21
                self.match(LiteExprParser.HEX)
                pass

            elif la_ == 4:
                localctx = LiteExprParser.IntContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 22
                self.match(LiteExprParser.INT)
                pass

            elif la_ == 5:
                localctx = LiteExprParser.ParenContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 23
                self.match(LiteExprParser.T__0)
                self.state = 24
                self.expr(0)
                self.state = 25
                self.match(LiteExprParser.T__1)
                pass

            elif la_ == 6:
                localctx = LiteExprParser.CallContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 27
                self.varname(0)
                self.state = 28
                self.match(LiteExprParser.T__0)
                self.state = 29
                self.list_()
                self.state = 30
                self.match(LiteExprParser.T__1)
                pass

            elif la_ == 7:
                localctx = LiteExprParser.VariableContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 32
                self.varname(0)
                pass

            elif la_ == 8:
                localctx = LiteExprParser.ObjectContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 33
                self.match(LiteExprParser.T__2)
                self.state = 34
                self.pairlist()
                self.state = 35
                self.match(LiteExprParser.T__3)
                pass

            elif la_ == 9:
                localctx = LiteExprParser.ArrayContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 37
                self.match(LiteExprParser.T__4)
                self.state = 38
                self.list_()
                self.state = 39
                self.match(LiteExprParser.T__5)
                pass

            elif la_ == 10:
                localctx = LiteExprParser.PostfixOpContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 41
                self.varname(0)
                self.state = 42
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==7 or _la==8):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass

            elif la_ == 11:
                localctx = LiteExprParser.PrefixOpContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 44
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==7 or _la==8):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 45
                self.varname(0)
                pass

            elif la_ == 12:
                localctx = LiteExprParser.UnaryOpContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 46
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 7680) != 0)):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 47
                self.expr(16)
                pass

            elif la_ == 13:
                localctx = LiteExprParser.AssignOpContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 48
                self.varname(0)
                self.state = 49
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 70366596694016) != 0)):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 50
                self.expr(4)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 100
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 98
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
                    if la_ == 1:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 54
                        if not self.precpred(self._ctx, 15):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 15)")
                        self.state = 55
                        localctx.op = self.match(LiteExprParser.T__12)
                        self.state = 56
                        self.expr(15)
                        pass

                    elif la_ == 2:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 57
                        if not self.precpred(self._ctx, 14):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 14)")
                        self.state = 58
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 114688) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 59
                        self.expr(15)
                        pass

                    elif la_ == 3:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 60
                        if not self.precpred(self._ctx, 13):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 13)")
                        self.state = 61
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==11 or _la==12):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 62
                        self.expr(14)
                        pass

                    elif la_ == 4:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 63
                        if not self.precpred(self._ctx, 12):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 12)")
                        self.state = 64
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 917504) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 65
                        self.expr(13)
                        pass

                    elif la_ == 5:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 66
                        if not self.precpred(self._ctx, 11):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 11)")
                        self.state = 67
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 15728640) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 68
                        self.expr(12)
                        pass

                    elif la_ == 6:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 69
                        if not self.precpred(self._ctx, 10):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 10)")
                        self.state = 70
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==24 or _la==25):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 71
                        self.expr(11)
                        pass

                    elif la_ == 7:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 72
                        if not self.precpred(self._ctx, 9):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 9)")
                        self.state = 73
                        localctx.op = self.match(LiteExprParser.T__25)
                        self.state = 74
                        self.expr(10)
                        pass

                    elif la_ == 8:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 75
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 76
                        localctx.op = self.match(LiteExprParser.T__26)
                        self.state = 77
                        self.expr(9)
                        pass

                    elif la_ == 9:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 78
                        if not self.precpred(self._ctx, 7):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 7)")
                        self.state = 79
                        localctx.op = self.match(LiteExprParser.T__27)
                        self.state = 80
                        self.expr(8)
                        pass

                    elif la_ == 10:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 81
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 82
                        localctx.op = self.match(LiteExprParser.T__28)
                        self.state = 83
                        self.expr(7)
                        pass

                    elif la_ == 11:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 84
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 85
                        localctx.op = self.match(LiteExprParser.T__29)
                        self.state = 86
                        self.expr(6)
                        pass

                    elif la_ == 12:
                        localctx = LiteExprParser.TernaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 87
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 88
                        localctx.op1 = self.match(LiteExprParser.T__45)
                        self.state = 89
                        self.expr(0)
                        self.state = 90
                        localctx.op2 = self.match(LiteExprParser.T__46)
                        self.state = 91
                        self.expr(3)
                        pass

                    elif la_ == 13:
                        localctx = LiteExprParser.BinaryOpContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 93
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 94
                        localctx.op = self.match(LiteExprParser.T__47)
                        self.state = 95
                        self.expr(3)
                        pass

                    elif la_ == 14:
                        localctx = LiteExprParser.TermContext(self, LiteExprParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 96
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 97
                        self.match(LiteExprParser.T__47)
                        pass

             
                self.state = 102
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class VarnameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return LiteExprParser.RULE_varname

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class IndexedVarContext(VarnameContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.VarnameContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def varname(self):
            return self.getTypedRuleContext(LiteExprParser.VarnameContext,0)

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIndexedVar" ):
                return visitor.visitIndexedVar(self)
            else:
                return visitor.visitChildren(self)


    class SimpleVarContext(VarnameContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.VarnameContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(LiteExprParser.ID, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSimpleVar" ):
                return visitor.visitSimpleVar(self)
            else:
                return visitor.visitChildren(self)


    class MemberVarContext(VarnameContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LiteExprParser.VarnameContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def varname(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LiteExprParser.VarnameContext)
            else:
                return self.getTypedRuleContext(LiteExprParser.VarnameContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMemberVar" ):
                return visitor.visitMemberVar(self)
            else:
                return visitor.visitChildren(self)



    def varname(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = LiteExprParser.VarnameContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 4
        self.enterRecursionRule(localctx, 4, self.RULE_varname, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = LiteExprParser.SimpleVarContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 104
            self.match(LiteExprParser.ID)
            self._ctx.stop = self._input.LT(-1)
            self.state = 116
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,5,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 114
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
                    if la_ == 1:
                        localctx = LiteExprParser.MemberVarContext(self, LiteExprParser.VarnameContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_varname)
                        self.state = 106
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 107
                        self.match(LiteExprParser.T__48)
                        self.state = 108
                        self.varname(4)
                        pass

                    elif la_ == 2:
                        localctx = LiteExprParser.IndexedVarContext(self, LiteExprParser.VarnameContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_varname)
                        self.state = 109
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 110
                        self.match(LiteExprParser.T__4)
                        self.state = 111
                        self.expr(0)
                        self.state = 112
                        self.match(LiteExprParser.T__5)
                        pass

             
                self.state = 118
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class PairlistContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LiteExprParser.PairContext)
            else:
                return self.getTypedRuleContext(LiteExprParser.PairContext,i)


        def getRuleIndex(self):
            return LiteExprParser.RULE_pairlist

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPairlist" ):
                return visitor.visitPairlist(self)
            else:
                return visitor.visitChildren(self)




    def pairlist(self):

        localctx = LiteExprParser.PairlistContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_pairlist)
        self._la = 0 # Token type
        try:
            self.state = 131
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [55]:
                self.enterOuterAlt(localctx, 1)
                self.state = 119
                self.pair()
                self.state = 124
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 120
                        self.match(LiteExprParser.T__49)
                        self.state = 121
                        self.pair() 
                    self.state = 126
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

                self.state = 128
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==50:
                    self.state = 127
                    self.match(LiteExprParser.T__49)


                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 2)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(LiteExprParser.ID, 0)

        def expr(self):
            return self.getTypedRuleContext(LiteExprParser.ExprContext,0)


        def getRuleIndex(self):
            return LiteExprParser.RULE_pair

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPair" ):
                return visitor.visitPair(self)
            else:
                return visitor.visitChildren(self)




    def pair(self):

        localctx = LiteExprParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 133
            self.match(LiteExprParser.ID)
            self.state = 134
            self.match(LiteExprParser.T__46)
            self.state = 135
            self.expr(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LiteExprParser.ExprContext)
            else:
                return self.getTypedRuleContext(LiteExprParser.ExprContext,i)


        def getRuleIndex(self):
            return LiteExprParser.RULE_list

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitList" ):
                return visitor.visitList(self)
            else:
                return visitor.visitChildren(self)




    def list_(self):

        localctx = LiteExprParser.ListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_list)
        self._la = 0 # Token type
        try:
            self.state = 149
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1, 3, 5, 7, 8, 9, 10, 11, 12, 51, 52, 53, 54, 55]:
                self.enterOuterAlt(localctx, 1)
                self.state = 137
                self.expr(0)
                self.state = 142
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,9,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 138
                        self.match(LiteExprParser.T__49)
                        self.state = 139
                        self.expr(0) 
                    self.state = 144
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,9,self._ctx)

                self.state = 146
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==50:
                    self.state = 145
                    self.match(LiteExprParser.T__49)


                pass
            elif token in [2, 6]:
                self.enterOuterAlt(localctx, 2)

                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.expr_sempred
        self._predicates[2] = self.varname_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 15)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 14)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 13)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 12)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 11)
         

            if predIndex == 5:
                return self.precpred(self._ctx, 10)
         

            if predIndex == 6:
                return self.precpred(self._ctx, 9)
         

            if predIndex == 7:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 8:
                return self.precpred(self._ctx, 7)
         

            if predIndex == 9:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 10:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 11:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 12:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 13:
                return self.precpred(self._ctx, 1)
         

    def varname_sempred(self, localctx:VarnameContext, predIndex:int):
            if predIndex == 14:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 15:
                return self.precpred(self._ctx, 2)
         




