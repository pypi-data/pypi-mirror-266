from .parser import Parser
from ..error import ErrorCode
from ..lexers import TokenType, PythonTokenType, PythonTokenSet
import re

from ..gdt import CSS, GlobalDescriptorTable
from ..asts.python_ast import *

GDT = GlobalDescriptorTable()

class PythonParser(Parser):
    def __init__(self, lexer, skip_invis_chars=True, skip_space=True):
        super().__init__(lexer, skip_invis_chars, skip_space)
        self.python_first_set = PythonTokenSet()

    def parse(self):
        self.root = self.python_program()
        self.skip_crlf()
        if self.current_token.type != TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN, message="should match EOF")
        GDT.reset()
        return self.root
    
    def python_program(self):
        python = Python()
        python.update(stmts=self.list_items(self.stmt, trailing_set=self.python_first_set.stmt, delimiter=None))
        
    def stmt(self):
        '''
        statement: compound_stmt  | simple_stmts
        '''
        
    def compound_stmt(self):
        '''
        compound_stmt:
                    | function_def
                    | if_stmt
                    | class_def
                    | with_stmt
                    | for_stmt
                    | try_stmt
                    | while_stmt
                    | match_stmt
        '''
        
    def simple_stmts(self):
        '''
        simple_stmt:
                    | assignment
                    | type_alias
                    | star_expressions 
                    | return_stmt
                    | import_stmt
                    | raise_stmt
                    | 'pass' 
                    | del_stmt
                    | yield_stmt
                    | assert_stmt
                    | 'break' 
                    | 'continue' 
                    | global_stmt
                    | nonlocal_stmt
        '''
        if self.current_token.type in (PythonTokenType.PASS, PythonTokenType.BREAK, PythonTokenType.CONTINUE):
            return self.get_keyword()
        