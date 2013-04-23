from macropy.core.macros import expr_macro
from macropy.core.core import *
from ast import *
from macropy.core.util import *
"""
Aggregate Functions:
    http://www.sqlite.org/lang_aggfunc.html
    avg(x)                  linq.avg
    count(x)                linq.count
    group_concat(x)
    group_concat(x, y)
    max(x)                  max
    min(x)                  min
    sum(x)                  sum
    total(x)                linq.total

Core Functions:
    http://www.sqlite.org/lang_corefunc.html
    abs(x)                  abs
    changes()
    char(x1, x2, ..., xn)
    coalesce(x, y, ...)
    glob(x, y)
    ifnull(x, y)
    instr(x, y)
    hex(x)                  hex
    last_insert_rowid()
    length(x)               len
    like(x, y)
    like(x, y, z)
    load_extension(x)
    load_extension(x, y)
    lower(x)                str.lower
    ltrim(x)                str.lstrip
    ltrim(x, y)             str.lstrip
    max(x, y, ...)          max
    min(x, y, ...)          min
    nullif(x, y)
    quote(x)
    random()                linq.random
    randomblob(n)
    replace(x, y, z)        str.replace
    round(x)                round
    round(x, y)             round
    rtrim(x)                str.rstrip
    rtrim(x, y)             str.rstrip
    soundex(x)
    sqlite_compileoption_get(n)
    sqlite_comileoption_used(x)
    sqlite_source_id()
    sqlite_version()
    substr(x, y, z)         str[:]
    substr(x, y)            str[:]
    total_changes()
    trim(x)                 str.strip
    trim(x, y)              str.strip
    typeof(x)
    unicode(x)
    upper(x)                str.upper
    zeroblob(n)
"""

@expr_macro
def sql(tree):
    def handleExpr(tree):

        if type(tree) is BoolOp:
            boolop_map = {
                And: "AND",
                Or: "OR"
            }

            return (" " + boolop_map(tree.op) + " ").join(handleExpr(value) for value in tree.values)
        if type(tree) is BinOp:
            binop_map = type_dict({
                Add: "+",
                Sub: "-",
                Mult: "*",
                Div: "/",
                Mod: "%",
                Pow: "**",
                LShift: "<<",
                RShift: ">>",
                BitOr: "|",
                BitXor: "",
                BitAnd: "&",
                FloorDiv: "/"
            })
            return handleExpr(tree.left) + " " + binop_map(tree.op) + " " + handleExpr(tree.right)

        if type(tree) is UnaryOp:
            unaryop_map = type_dict({
                Invert: "~",
                Not: "NOT ",
                UAdd: "+",
                USub: "-"
            })
            return unaryop_map(tree.op) + handleExpr(tree.operand)

        if type(tree) is IfExp:
            return "CASE WHEN " + handleExpr(tree.test) + " THEN " + handleExpr(tree.body) + " ELSE " + handleExpr(tree.orelse) + " END"
        if type(tree) is Compare:

            cmpop_map = type_dict({
                Eq: "=",
                NotEq: "!=",
                Lt: "<",
                LtE: "<=",
                Gt: ">",
                GtE: ">=",
                Is: "=",
                IsNot: "!=",
                In: "IN",
                NotIn: "NOT IN"
            })


            return handleExpr(tree.left) + " " + cmpop_map(tree.ops[0]) + " " + handleExpr(tree.comparators[0])

        if type(tree) is Num:
            return repr(tree.n)

        if type(tree) is Str:
            return repr(tree.s)

        if type(tree) is Attribute:
            return tree.value.id + "." + tree.attr

        if type(tree) is Name:
            return tree.id

        if type(tree) is List: pass
        if type(tree) is Tuple:
            return ", ".join([handleExpr(e) for e in tree.elts])


    assert type(tree) is GeneratorExp
    elt = tree.elt

    if type(elt) is Attribute:
        sel = handleExpr(elt)

    if type(elt) is Tuple:
        sel = handleExpr(elt)

    frm = " JOIN ".join(
        gen.iter.id + " " + gen.target.id
        for gen in tree.generators
    )

    all_guards = "AND".join(
        handleExpr(ifexp)
        for gen in tree.generators
        for ifexp in gen.ifs
    )

    whr = "" if all_guards == "" else "WHERE " + all_guards

    return ast_repr("SELECT %s FROM %s %s" % (sel, frm, whr))
