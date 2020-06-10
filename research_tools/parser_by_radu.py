import ast
import builtins
import io
import sys
import token
from collections import defaultdict
from tokenize import TokenInfo, tokenize

# import astpretty
# from termcolor import colored
from pprint import pprint as pp
from ast import iter_fields, AST


class ASTVisitor(ast.NodeVisitor):

    def __init__(self):
        self.functions  = []
        self.modules    = {}

    def name_by_type(self, node):

        if isinstance(node, ast.Subscript):
            return "{}[]".format(self.name_by_type(node.value))

        if isinstance(node, ast.Attribute):
            if hasattr(node, "value"):
                object = self.name_by_type(node.value)
                if object:
                    if isinstance(object, str):
                        return object + "." + node.attr
                    elif isinstance(object, ast.Str):
                        return object.s + "." + node.attr
                    elif isinstance(object, ast.Num):
                        return str(object.n) + "." + node.attr
                    elif isinstance(object, ast.Subscript):
                        return node.attr
                    elif isinstance(object, ast.List):
                        return node.attr
                    elif isinstance(object, ast.Compare):
                        return node.attr
                    elif isinstance(object, ast.UnaryOp):
                        return node.attr
                    elif isinstance(object, ast.Tuple):
                        return node.attr
                    else:
                        print("FAIL", object, dir(object))
                        exit(0)

            return node.attr

        elif isinstance(node, ast.Name):
            return node.id

        elif isinstance(node, ast.Subscript):
            try:
                return node.slice.value.id
            except AttributeError:
                try:
                    return node.slice.value
                except AttributeError:
                    return None

        return None

    def generic_visit(self, node):

        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        if isinstance(item, ast.Call):
                            self.visit_Call(item)
                        else:
                            self.visit(item)
            elif isinstance(value, AST):
                if isinstance(value, ast.Call):
                    self.visit_Call(value)
                else:
                    self.visit(value)

    def visit_Call(self, node: ast.Call):

        name = self.name_by_type(node.func)
        if isinstance(name, ast.Str):
            name = name.s
        elif name is None:
            name = "<function>"

        function = {
            "name": name,
            "num_args": len(node.args),
            # "arguments": []
        }
        self.functions.append(function)

        if hasattr(node, 'keywords'):
            self.functions[-1]["num_args"] += len(node.keywords)

        if isinstance(node.func, ast.Attribute):
            self.visit(node.func)
        elif isinstance(node.func, ast.Call):
            self.visit_Call(node.func)

        for arg in node.args:
            if isinstance(arg, ast.Call):
                type = self.visit_Call(arg)
            else:
                self.visit(arg)

        return "return_{}".format(name)

        # if isinstance(node.func, ast.Call):
        #     print("bzz")
        #     self.visit_Call(node.func)
        # else:
        #     print("non_bzz")
        #     func_name = self.name_by_type(node.func)
        #
        #     function = {
        #         "name": func_name,
        #         "num_args": len(node.args),
        #         "arguments": []
        #     }
        #     # print(func_name)
        #     # print(dir(node))
        #
        #     self.functions[func_name] = function
        #     # self.call_stack.append(function)
        #
        #     if hasattr(node, 'keywords'):
        #         self.functions[func_name]["num_args"] += len(node.keywords)
        #
        #     for arg in node.args:
        #
        #         function["arguments"].append(None)
        #
        #         if isinstance(arg, ast.Call):
        #             print("call on!")
        #             self.visit_Call(arg)
        #         else:
        #             if isinstance(arg, ast.Str):
        #                 function["arguments"][-1] = arg.s
        #             elif isinstance(arg, ast.Num):
        #                 function["arguments"][-1] = arg.n
        #
        #             print("Seeking args: ", arg)
        #             self.visit(arg)

            # if getattr(node, "ctx"):
            #     self.visit(node.ctx)

            # self.call_stack.pop()

class SketchVocab:
    NAME_ID = "NAME"
    FUNC_ID = "FUNC"
    STR_LITERAL_ID = "STRING"
    NUM_LITERAL_ID = "NUMBER"
    RESERVED_ID = "<reserved>"
    ACCESSOR_ID = "<accessor>"
    ASSIGN_ID = "<assign>"
    ARITHMETIC_ID = "<arithmetic>"
    OP_ID = "<op>"


class Parser:

    def __init__(self, code_snippet: str, verbose=False):

        self.code_snippet = code_snippet
        self.names        = defaultdict(lambda: [])
        self.keywords     = defaultdict(lambda: [])
        self.literals     = set()
        self.operators    = set()
        self.sketch       = []
        self.canonic      = []

        if verbose:
            print(colored(" * tokenizing [%s]" % code_snippet, 'yellow'))
        self.tok_list = list(tokenize(io.BytesIO(self.code_snippet.encode('utf-8')).readline))

        self.ast_visitor = ASTVisitor()
        self.ast = None

        try:
            self.ast = self.ast_visitor.visit(ast.parse(self.code_snippet))
        except SyntaxError:
            if verbose:
                print(colored(" * skipping ast generation for [%s]" % code_snippet, 'red'))

    def refine_name(self, tok: TokenInfo):
        if self.is_reserved_keyword(tok.string):
            self.keywords[tok.string].append(tok.start[1])
            self.sketch.append(tok.string)
            self.canonic.append(tok.string)
        else:
            self.names[tok.string].append(tok.start[1])
            self.canonic.append(tok.string)

            for fun in self.ast_visitor.functions:
                if tok.string == fun["name"].split(".")[-1]:
                    self.sketch.append(SketchVocab.FUNC_ID + "#%d" % fun["num_args"])
                    break
            else:
                self.sketch.append(SketchVocab.NAME_ID)

    def generate(self):

        for tok in self.tok_list:
            tok_type = token.tok_name[tok.type]

            if tok_type == 'NAME':
                self.refine_name(tok)

            elif tok_type == 'STRING':
                self.literals.add(tok.string)
                self.sketch.append(SketchVocab.STR_LITERAL_ID)
                self.canonic.append(tok.string)

            elif tok_type == 'NUMBER':
                self.literals.add(tok.string)
                self.sketch.append(SketchVocab.NUM_LITERAL_ID)
                self.canonic.append(tok.string)

            elif tok_type == 'OP':
                self.operators.add(tok.string)
                self.sketch.append(tok.string)
                self.canonic.append(tok.string)

            elif tok_type == 'NEWLINE' or tok_type == "NL":
                self.sketch.append("\n")
                self.canonic.append("\n")

            elif tok_type == "INDENT":
                self.sketch.append("   ")
                self.canonic.append("   ")

            else:
                assert tok_type in ['ENCODING', 'NEWLINE', 'ENDMARKER',
                                    'ERRORTOKEN', 'INDENT', 'DEDENT'], "%s" % tok_type

        return self

    def details(self):
        return "names: %s\nkeywords: %s\nliterals: %s\noperators: %s\nfunctions: %s" % (
            str(list(self.names.keys())),
            str(list(self.keywords.keys())),
            str(list(self.literals)),
            str(list(self.operators)),
            str(self.ast_visitor.functions)
        )

    def get_canonic_form(self):
        return " ".join(self.canonic).strip()

    def split(self, delim=' '):
        return str(self).split(delim)

    def get_literals(self):
        return list(self.literals)

    def get_operators(self):
        return list(self.operators)

    def __str__(self):
        return ' '.join(self.sketch)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.sketch)

    @staticmethod
    def is_reserved_keyword(name):
        RESERVED_KEYWORDS = set(dir(builtins) + [
            "and", "assert", "break", "class", "continue", "def", "del", "elif",
            "else", "except", "exec", "finally", "for", "from", "global", "if",
            "import", "in", "is", "lambda", "not", "or", "pass", "print", "raise",
            "return", "try", "while", "yield", "None", "self"
        ])  # len = 182

        return name in RESERVED_KEYWORDS


def main():

    code_snippet = "a.aa.b(c.d(1)).d(2)"
    astpretty.pprint(ast.parse(code_snippet).body[0], indent=' ' * 4)
    sketch = Parser(code_snippet, verbose=True).generate()

    print(sketch.details())
    print(sketch.get_canonic_form())
    print(sketch)


if __name__ == '__main__':
    main()
