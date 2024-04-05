from pathlib import Path
from functools import partial, lru_cache
from .template import Template


def tab_str(s, n, p=4, sl=False):  # s: list of str or str
    if isinstance(s, str):
        s = [s]
    r = []
    for x in s:
        if sl:
            x = x.strip()
            if x:
                r.append(x)
        else:
            r.append(x)
    r = '\n'.join(r).split('\n')
    return '\n'.join([' ' * n * p + x for x in r])


class Cache:
    def __init__(self, master):
        self.master = master
        self.caches = {}

    def __getitem__(self, method):
        return partial(self.__run, method)

    def __getattr__(self, method):
        return self[method]

    def __run(self, method):
        if method not in self.caches:
            self.caches[method] = getattr(self.master, method)()
        return self.caches[method]


class Repr:
    def __init__(self, value, delay=False):
        self.value = value
        self.delay = delay

    def final_value(self):
        return self.value

    def __repr__(self):
        value = self.final_value()
        return f'lambda: {value}' if self.delay else value

    def __copy__(self):
        return self.__class__(self.value, self.delay)

    def __deepcopy__(self, memo):
        return self.__class__(self.value, self.delay)


class ReprTuple(Repr):
    def __init__(self, value, delay=False):
        super().__init__(list(value), delay)

    def final_value(self):
        return repr(tuple(self.value))

    def __getattr__(self, item):
        return getattr(self.value, item)


class Generator:
    TEMPLATE_DIR = None

    template_name = None
    template_cls = Template
    template_ext = '.tpl'

    Repr = Repr
    ReprTuple = ReprTuple

    env_default = {}

    def __init__(self, target_dir, instance, kwargs=None):
        self.target_dir = str(target_dir)
        self.instance = instance
        self.kwargs = kwargs or {}
        self.cache = Cache(self)

    def check(self):
        return self.instance is not None

    def action(self):
        if self.check():
            self.render()
            self.on_rendered()

    def on_rendered(self):
        pass

    def render(self):
        self.template_cls(self.normalize_variables(
            {**self.variables, **self.kwargs}), self.env_default).render_dir(self.target_dir, self.template_path)

    def render_tpl(self, tpl, variables=None):
        return self.template_cls(self.normalize_variables(
            {**(self.variables if variables is None else variables), **self.kwargs}), self.env_default).render_string(
            str(Path(self.template_path) / (tpl + self.template_ext)))

    def normalize_variables(self, variables):
        return variables

    @property
    @lru_cache(None)
    def template_path(self):
        return str(Path(self.TEMPLATE_DIR) / self.template_name) if self.template_name else str(self.TEMPLATE_DIR)

    @property
    @lru_cache(None)
    def variables(self):
        return self.collect_data('variables')

    def get_variables(self, *args, **kwargs):
        return {
            **{k: self.variables[k] for k in args},
            **{k: self.variables[v] for k, v in kwargs.items()}
        }

    def collect_data(self, name, collection=dict):
        result = collection()
        pre_collect = f'pre_collect_{name}'
        post_collect = f"post_collect_{name}"
        if hasattr(self, pre_collect):
            result = collection(getattr(self, pre_collect)() or collection())
        for x in dir(self):
            if x.startswith(f'{name}_'):
                v = getattr(self, x)
                result.update(collection(self.cache[x]() if callable(v) else v))
        if hasattr(self, post_collect):
            result = collection(getattr(self, post_collect)(result))
        return result

    @staticmethod
    def tab_str(s, n, p=4, sl=False):  # s: list or str
        return tab_str(s, n, p, sl)
