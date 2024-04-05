import functools
from .imports import Imports, ImportsStatement
from .template import TemplateFormatted
from .template.env import env_extend
from ...tmpl.generator import Generator, Repr


class ReprTS(Repr):
    def final_value(self):
        return f'_({repr(self.value)})'


class CodeGenerator(Generator):
    ReprTS = ReprTS
    template_cls = TemplateFormatted
    _imports_cls = Imports
    _imports_statement_cls = ImportsStatement

    env_default = {**env_extend.context}

    template_codes_body = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._imports_statement = None
        self.parent = None

    def get_codes_body(self):
        if self.template_codes_body:
            return self.render_tpl(self.template_codes_body)
        else:
            return ''

    @property
    @functools.lru_cache(None)
    def iss(self):
        if self.parent_root:
            return self.parent_root._imports_statement
        else:
            _imports_core = getattr(self.__class__, '_imports_core', None)
            if _imports_core is None:
                _imports_core = self.__class__._imports_core = self._imports_cls()
            imports_core = _imports_core.derive()
            imports_core.update(self.walk_imports(self))
            self._imports_statement = self._imports_statement_cls(imports_core)
            return self._imports_statement

    @property
    @functools.lru_cache(None)
    def parent_root(self):
        cursor = self.parent
        while cursor:
            if cursor.parent:
                cursor = cursor.parent
            else:
                return cursor
        return cursor

    def post_collect_children(self, children):
        for lst in children.values():
            for child in lst:
                child.parent = self
        return children

    def post_collect_variables(self, variables):
        children_data = {}
        all_filter_children = getattr(self, f'all_filter_children', lambda k, x, y: x)
        for key, array in self.children.items():
            r = self.tab_str([node.get_codes_body() for node in array], 0)
            filter_children = getattr(self, f'filter_children_{key}', None)
            if filter_children:
                children_data[key] = filter_children(r, array)
            else:
                children_data[key] = all_filter_children(key, r, array)

        if self.parent_root:
            imports_data = {}
        else:
            imports_data = dict(
                imports=self.iss.as_statements()
            )

        return self.post_post_collect_variables({
            **variables,
            **children_data,
            **imports_data
        })

    def pre_pre_collect_variables(self):
        return {}

    def post_post_collect_variables(self, variables):
        return variables

    @property
    @functools.lru_cache(None)
    def imports(self):
        return self.collect_data('imports', dict)

    @classmethod
    def walk_imports(cls, node):
        imports = {}
        imports.update(node.imports)
        for children in node.children.values():
            for child in children:
                imports.update(cls.walk_imports(child))
        return imports

    @property
    @functools.lru_cache(None)
    def children(self):
        return self.collect_data('children', dict)
