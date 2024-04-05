import os.path
import unittest
import tempfile
from dekgen.utils.yaml import yaml
from dekgen.utils.yaml.tags import tmpl_data_final
from dekgen.tmpl.render import render_dir
from dektools.output import pprint
from dektools.file import read_text


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_yaml(self):
        pprint(tmpl_data_final(yaml.load('./res/test.yaml')))

    def test_render(self):
        target = tempfile.mkdtemp()
        render_dir(target, './render', files=['./render/values.test.yaml'])
        print(read_text(os.path.join(target, 'main.txt')))
