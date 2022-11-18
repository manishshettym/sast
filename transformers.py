import gast as ast


class DropDecorators(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        new_node = node
        new_node.decorator_list = []

        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)
        self.generic_visit(node)

        return new_node


class CodeSpan(ast.NodeTransformer):
    def __init__(self, source):
        self.source = source
        self.lines = source.split('\n')
    
    def _get_char_index(self, lineno, col_offset):
        line_index = lineno - 1
        line_start = sum(len(line) + 1 for line in self.lines[:line_index])
        return line_start + col_offset

    def _add_span(self, node):
        try:
            lineno = node.lineno
            end_lineno = node.end_lineno
            col_offset = node.col_offset
            end_col_offset = node.end_col_offset

            span_start = self._get_char_index(lineno, col_offset)
            span_end = self._get_char_index(end_lineno, end_col_offset)
            node.range = (span_start, span_end)

            assert span_start >= 0 and span_start <= len(self.source)
            assert span_end >= 0 and span_end <= len(self.source)

        except (AttributeError, AssertionError, TypeError) as e:
            node.range = (0, 0)
        
        return node
    
    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        self._add_span(node)

        for key, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self._add_span(item)
                        self.visit(item)

            elif isinstance(value, ast.AST):
                self._add_span(value)
                self.visit(value)
            
        return node
