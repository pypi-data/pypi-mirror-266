import os
from jinja2 import Environment
from dektools.file import read_text, read_file, write_file, list_relative_path, FileHitChecker, normal_path


class Template:
    template_suffix = '-tpl'
    target_suffix = None

    file_ignore_tpl = ['.ignoretpl', '.ignoretpl.tpl']
    file_ignore_override = ['.ignoreor', '.ignoreor.tpl']
    file_ignore = ['.ignore', '.ignore.tpl']

    default_env_kwargs = dict(
        autoescape=False
    )

    def __init__(self, variables, env=None, **kwargs):
        self.args_copy = [variables, kwargs]
        self.env = Environment(**{
            **self.default_env_kwargs,
            **kwargs
        })
        self.variables = variables
        if env:
            for k, data in env.items():
                getattr(self.env, k).update(data)

    def copy(self, variables=None):
        return self.__class__(
            {**self.args_copy[0], **(variables or {})},
            **self.args_copy[1]
        )

    def render(self, content):
        return self.env.from_string(content).render(self.variables)

    def render_string(self, template_file, close_tpl=False):
        if close_tpl:
            return read_file(template_file)
        else:
            return self.render(read_text(template_file))

    def render_file(self, target_file, template_file, close_tpl=False):
        content = self.render_string(template_file, close_tpl)
        write_file(target_file, sb=content)
        return content

    def render_dir(self, target_dir, template_path, force_close_tpl=False, open_ignore_override=True):
        ignore_tpl = FileHitChecker(template_path, self.file_ignore_tpl[0],
                                    rules=self.get_hit_rules(template_path, self.file_ignore_tpl[1]))
        ignore_override = FileHitChecker(template_path, self.file_ignore_override[0],
                                         rules=self.get_hit_rules(template_path, self.file_ignore_override[1]))
        ignore = FileHitChecker(template_path, self.file_ignore[0],
                                rules=[*self.get_hit_rules(template_path, self.file_ignore[1]),
                                       *[f'/{item}' for item in
                                         [*self.file_ignore_tpl, *self.file_ignore_override, *self.file_ignore]]])
        path_virtual = os.path.join(template_path, '__virtual__')
        variables_virtual = {}
        for rp, fp in list_relative_path(path_virtual).items():
            variables_virtual[rp.replace('\\', '/').replace('/', '__')] = self.render_string(fp)
        self.variables['__virtual__'] = variables_virtual
        for root, _, files in os.walk(template_path):
            for f in files:
                fp = os.path.join(root, f)
                if ignore.is_hit(fp):
                    continue
                fn, ext = splitext(fp)
                ext = ext.rsplit(self.template_suffix, 1)[0] if self.template_suffix else ext
                rp = (fn + ext)[len(template_path):]
                target_file = target_dir + self.render(rp)
                if open_ignore_override and os.path.exists(target_file) and ignore_override.is_hit(fp):
                    continue
                self.render_file(target_file, fp, force_close_tpl or ignore_tpl.is_hit(fp))

    def get_hit_rules(self, template_path, filepath):
        ignore_file = normal_path(os.path.join(template_path, filepath))
        if os.path.exists(ignore_file):
            content = self.render_string(ignore_file)
            return [line for line in content.split('\n') if line]
        else:
            return []


class TemplateWide(Template):
    default_env_kwargs = dict(
        **Template.default_env_kwargs,
        variable_start_string='(=(',
        variable_end_string=')=)'
    )


def splitext(s):
    lst = s.rsplit('/', 1)
    if len(lst) == 2:
        dp, fn = lst
        sep = '/'
    else:
        lst = s.rsplit('\\', 1)
        sep = '\\'
        if len(lst) == 2:
            dp, fn = lst
        else:
            dp, fn = None, lst[0]
    lst = fn.rsplit('.', 1)
    if len(lst) == 2:
        fp, ext = lst
    else:
        fp, ext = lst[0], None
    ext = '' if ext is None else f'.{ext}'
    if dp is None:
        return fp, ext
    else:
        return dp + sep + fp, ext
