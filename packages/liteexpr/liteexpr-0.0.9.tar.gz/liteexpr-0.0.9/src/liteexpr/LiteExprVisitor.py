# Generated from ../LiteExpr.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .LiteExprParser import LiteExprParser
else:
    from LiteExprParser import LiteExprParser

# This class defines a complete generic visitor for a parse tree produced by LiteExprParser.

class LiteExprVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LiteExprParser#file.
    def visitFile(self, ctx:LiteExprParser.FileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Call.
    def visitCall(self, ctx:LiteExprParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Variable.
    def visitVariable(self, ctx:LiteExprParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#UnaryOp.
    def visitUnaryOp(self, ctx:LiteExprParser.UnaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#PostfixOp.
    def visitPostfixOp(self, ctx:LiteExprParser.PostfixOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#String.
    def visitString(self, ctx:LiteExprParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Term.
    def visitTerm(self, ctx:LiteExprParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Double.
    def visitDouble(self, ctx:LiteExprParser.DoubleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Int.
    def visitInt(self, ctx:LiteExprParser.IntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#TernaryOp.
    def visitTernaryOp(self, ctx:LiteExprParser.TernaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Array.
    def visitArray(self, ctx:LiteExprParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Hex.
    def visitHex(self, ctx:LiteExprParser.HexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Object.
    def visitObject(self, ctx:LiteExprParser.ObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#AssignOp.
    def visitAssignOp(self, ctx:LiteExprParser.AssignOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#Paren.
    def visitParen(self, ctx:LiteExprParser.ParenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#PrefixOp.
    def visitPrefixOp(self, ctx:LiteExprParser.PrefixOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#BinaryOp.
    def visitBinaryOp(self, ctx:LiteExprParser.BinaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#IndexedVar.
    def visitIndexedVar(self, ctx:LiteExprParser.IndexedVarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#SimpleVar.
    def visitSimpleVar(self, ctx:LiteExprParser.SimpleVarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#MemberVar.
    def visitMemberVar(self, ctx:LiteExprParser.MemberVarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#pairlist.
    def visitPairlist(self, ctx:LiteExprParser.PairlistContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#pair.
    def visitPair(self, ctx:LiteExprParser.PairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LiteExprParser#list.
    def visitList(self, ctx:LiteExprParser.ListContext):
        return self.visitChildren(ctx)



del LiteExprParser