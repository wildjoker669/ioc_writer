"""
tests.py from ioc_writer
Created: 12/3/15

Purpose:

Examples:

Usage:

"""
# Stdlib
from __future__ import print_function
import logging
import os
import unittest
# Third Party code
from lxml import etree as et
# Custom Code
import ioc_writer.ioc_api as ioc_api
import ioc_writer.ioc_et as ioc_et
import ioc_writer.managers as managers
import ioc_writer.managers.downgrade_11 as downgrade_11


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s [%(filename)s:%(funcName)s]')
log = logging.getLogger(__name__)


OPENIOC_11_ASSETS = os.path.join(os.path.split(__file__)[0], 'assets/openioc_11_assets')


class TestIocEt(unittest.TestCase):
    def setUp(self):
        self.author = 'unittest'
        self.content_text = 'foobar.exe'
        self.content_type = 'string'
        self.context_document = 'FileItem'
        self.context_search = 'FileItem/Md5sum'
        self.context_type = 'testType'
        self.description = 'Test description'
        self.iocid = '1234'
        self.keywords = 'Foo Bar Baz'
        self.links = [('testRel', None, 'testValue'),
                      ('testRel2', 'https://www.fireeye.com', 'testValue2',)]
        self.name = 'Test name'
        self.params = [{'nid': '1234-5678',
                        'content': 'I am a string!'},
                       {'nid': '1234-9abc',
                        'content': 'I am a string!',
                        'name': 'comment',
                        'ptype': 'string'},
                       {'nid': '1234-def0',
                        'content': 'true',
                        'name': 'some_value',
                        'ptype': 'bool'},
                       ]

    def test_make_criteria_node(self):
        r = ioc_et.make_criteria_node()
        self.assertEqual(r.tag, 'criteria')

    def test_make_criteria_node_invalid(self):
        bad_node = et.Element('BadNode')
        with self.assertRaises(ValueError):
            r = ioc_et.make_criteria_node(indicator_node=bad_node)

    def test_make_content_node(self):
        r = ioc_et.make_content_node(ctype=self.content_type,
                                     content=self.content_text)
        self.assertEqual(r.tag, 'Content')
        self.assertEqual(r.text, self.content_text)
        self.assertEqual(r.attrib.get('type'), self.content_type)

    def test_make_context_node(self):
        r = ioc_et.make_context_node(document=self.context_document, search=self.context_search)
        self.assertEqual(r.tag, 'Context')
        self.assertEqual(r.text, None)
        self.assertEqual(r.attrib.get('document'), self.context_document)
        self.assertEqual(r.attrib.get('search'), self.context_search)
        self.assertEqual(r.attrib.get('type'), 'mir')

    def test_make_context_node_param(self):
        r = ioc_et.make_context_node(document=self.context_document, search=self.context_search,
                                     context_type=self.context_type)
        self.assertEqual(r.tag, 'Context')
        self.assertEqual(r.text, None)
        self.assertEqual(r.attrib.get('document'), self.context_document)
        self.assertEqual(r.attrib.get('search'), self.context_search)
        self.assertEqual(r.attrib.get('type'), self.context_type)

    def test_make_parameters_node(self):
        r = ioc_et.make_parameters_node()
        self.assertEqual(r.tag, 'parameters')

    def test_make_parm_node(self):
        for param in self.params:
            r = ioc_et.make_param_node(**param)
            self.assertEqual(r.tag, 'param')
            self.assertEqual(len(r.getchildren()), 1)
            vnode = r.getchildren()[0]
            self.assertEqual(vnode.tag, 'value')
            self.assertIn('id', r.attrib)
            self.assertEqual(r.attrib.get('ref-id'), param.get('nid'))
            self.assertEqual(vnode.text, param.get('content'))
            if 'name' in param:
                self.assertEqual(r.attrib.get('name'), param.get('name'))
            else:
                self.assertEqual(r.attrib.get('name'), 'comment')
            if 'ptype' in param:
                self.assertEqual(vnode.attrib.get('type'), param.get('ptype'))
            else:
                self.assertEqual(vnode.attrib.get('type'), 'string')

    def test_make_link_node(self):
        rel, href, value = self.links[0]
        r = ioc_et.make_link_node(rel, value, href)
        self.assertEqual(r.tag, 'link')
        self.assertEqual(r.attrib.get('rel'), rel)
        self.assertEqual(r.attrib.get('href'), href)
        self.assertEqual(r.text, value)

        rel2, href2, value2 = self.links[1]
        r2 = ioc_et.make_link_node(rel2, value2, href2)
        self.assertEqual(r2.tag, 'link')
        self.assertEqual(r2.attrib.get('rel'), rel2)
        self.assertEqual(r2.attrib.get('href'), href2)
        self.assertEqual(r2.text, value2)

    def test_make_links_node(self):
        r = ioc_et.make_links_node(self.links)
        self.assertEqual(r.tag, 'links')
        for i, link in enumerate(r.getchildren()):
            self.assertEqual(link.tag, 'link')
            rel, href, value = self.links[i]
            self.assertEqual(link.attrib['rel'], rel)
            self.assertEqual(link.attrib.get('href'), href)
            self.assertEqual(link.text, value)

    def test_make_authored_date_node(self):
        r = ioc_et.make_authored_date_node()
        self.assertEqual(r.tag, 'authored_date')

    def test_make_authored_by_node(self):
        r = ioc_et.make_authored_by_node()
        self.assertEqual(r.tag, 'authored_by')
        self.assertEqual(r.text, 'ioc_et')
        r2 = ioc_et.make_authored_by_node(author=self.author)
        self.assertEqual(r2.text, self.author)

    def test_make_description_node(self):
        r = ioc_et.make_description_node(self.description)
        self.assertEqual(r.tag, 'description')
        self.assertEqual(r.text, self.description)

    def test_make_short_description_node(self):
        r = ioc_et.make_short_description_node(self.name)
        self.assertEqual(r.tag, 'short_description')
        self.assertEqual(r.text, self.name)

    def test_make_keywords_node(self):
        r = ioc_et.make_keywords_node()
        self.assertEqual(r.tag, 'keywords')
        self.assertEqual(r.text, None)
        r2 = ioc_et.make_keywords_node(keywords=self.keywords)
        self.assertEqual(r2.text, self.keywords)

    def test_make_ioc_root(self):
        r = ioc_et.make_ioc_root()
        self.assertEqual(r.tag, 'OpenIOC')
        required_attribs = ['id', 'last-modified', 'published-date', 'xmlns']
        for attribute in required_attribs:
            self.assertIn(attribute, r.attrib)

    def test_make_ioc_root_provided_id(self):
        r = ioc_et.make_ioc_root(iocid=self.iocid)
        self.assertEqual(r.attrib['id'], self.iocid)

    def test_make_metadata_node(self):
        r = ioc_et.make_metadata_node()
        self.assertEqual(r.tag, 'metadata')
        child_note_tags = ['short_description',
                           'description',
                           'keywords',
                           'authored_by',
                           'authored_date',
                           'links']
        for tag in child_note_tags:
            n = r.find(tag)
            self.assertTrue(n is not None)
            self.assertEqual(n.tag, tag)

    def test_make_metadata_node_provided_data(self):
        r = ioc_et.make_metadata_node(name=self.name,
                                      description=self.description,
                                      author=self.author,
                                      links=self.links)
        self.assertEqual(r.find('description').text, self.description)
        self.assertEqual(r.find('short_description').text, self.name)
        self.assertEqual(r.find('authored_by').text, self.author)
        links = r.find('links')
        for i, link in enumerate(links.getchildren()):
            rel, href, value = self.links[i]
            self.assertEqual(link.attrib['rel'], rel)
            self.assertEqual(link.attrib.get('href'), href)
            self.assertEqual(link.text, value)


class TestIOCApi(unittest.TestCase):
    def setUp(self):
        self.author = 'unittest'
        self.content_text = 'foobar.exe'
        self.content_type = 'string'
        self.context_document = 'FileItem'
        self.context_search = 'FileItem/Md5sum'
        self.context_type = 'testType'
        self.description = 'Test description'
        self.iocid = '1234'
        self.keywords = 'Foo Bar Baz'
        self.links = [('testRel', None, 'testValue'),
                      ('testRel2', 'https://www.fireeye.com', 'testValue2',)]
        self.name = 'Test name'
        self.params = [{'nid': '1234-5678',
                        'content': 'I am a string!'},
                       {'nid': '1234-9abc',
                        'content': 'I am a string!',
                        'name': 'comment',
                        'ptype': 'string'},
                       {'nid': '1234-def0',
                        'content': 'true',
                        'name': 'some_value',
                        'ptype': 'bool'},
                       ]

    def test_ioc_class_creation_blank(self):
        ioc_obj = ioc_api.IOC()
        self.assertEqual(ioc_obj.metadata.findtext('authored_by'), 'IOC_api')
        self.assertEqual(ioc_obj.metadata.findtext('description'), 'Automatically generated IOC')
        self.assertEqual(ioc_obj.metadata.findtext('short_description'), '')
        self.assertEqual(ioc_obj.metadata.findtext('keywords'), '')
        self.assertEqual(len(ioc_obj.metadata.find('links').getchildren()), 0)

    def test_ioc_class_creation_provided_params(self):
        ioc_obj = ioc_api.IOC(name=self.name,
                              description=self.description,
                              author=self.author,
                              links=self.links,
                              keywords=self.keywords,
                              iocid=self.iocid)
        self.assertEqual(ioc_obj.metadata.findtext('authored_by'), self.author)
        self.assertEqual(ioc_obj.metadata.findtext('description'), self.description)
        self.assertEqual(ioc_obj.metadata.findtext('short_description'), self.name)
        self.assertEqual(ioc_obj.metadata.findtext('keywords'), self.keywords)
        self.assertEqual(len(ioc_obj.metadata.find('links').getchildren()), 2)

    def test_ioc_class_creation_file(self):
        iocid = '378f0cce-b8df-41d5-8189-3d7ec102e52f'
        fn = '{}.ioc'.format(iocid)
        fp = os.path.join(OPENIOC_11_ASSETS, fn)
        ioc_obj = ioc_api.IOC(fp)
        self.assertEqual(ioc_obj.iocid, iocid)
        self.assertEqual(len(ioc_obj.top_level_indicator.getchildren()), 7)


class TestIOCAPIFuncs(unittest.TestCase):
    def setUp(self):
        self.nid = '1234'
        self.operators = ['AND', 'OR', 'and', 'or']
        self.conditions = ['is',
                           'contains',
                           'matches',
                           'starts-with',
                           'ends-with',
                           'greater-than',
                           'less-than']
        self.context_document = 'FileItem'
        self.context_search = 'FileItem/Md5sum'
        self.context_type = 'testType'
        self.content = '5678'
        self.content_type = 'int'

    def test_make_i_node(self):
        for op in self.operators:
            inode = ioc_api.make_indicator_node(op)
            self.assertEqual(inode.get('operator'), op.upper())
            self.assertNotEqual(inode.get('id'), self.nid)
            inode = ioc_api.make_indicator_node(op, nid=self.nid)
            self.assertEqual(inode.get('operator'), op.upper())
            self.assertEqual(inode.get('id'), self.nid)

    def test_make_i_node_bad(self):
        op = 'FooBar'
        with self.assertRaises(ValueError):
            inode = ioc_api.make_indicator_node(op)

    def test_make_ii_node(self):
        for condition in self.conditions:
            ii_node = ioc_api.make_indicatoritem_node(condition=condition,
                                                      document=self.context_document,
                                                      search=self.context_search,
                                                      content_type=self.content_type,
                                                      content=self.content)
            self.assertEqual(ii_node.get('condition'), condition)
            self.assertEqual(ii_node.get('preserve-case'), 'false')
            self.assertEqual(ii_node.get('negate'), 'false')
            self.assertEqual(ii_node.findtext('Content'), self.content)
            self.assertEqual(ii_node.find('Content').get('type'), self.content_type)
            self.assertEqual(ii_node.find('Context').get('document'), self.context_document)
            self.assertEqual(ii_node.find('Context').get('search'), self.context_search)
            self.assertEqual(ii_node.find('Context').get('type'), 'mir')  # Default value

        ii_node = ioc_api.make_indicatoritem_node(condition='is',
                                                  document=self.context_document,
                                                  search=self.context_search,
                                                  content_type=self.content_type,
                                                  content=self.content,
                                                  context_type='notMir',
                                                  nid=self.nid)
        self.assertEqual(ii_node.find('Context').get('type'), 'notMir')
        self.assertEqual(ii_node.get('id'), self.nid)

        for preserve_case in [True, False]:
            for negate in [True, False]:
                ii_node = ioc_api.make_indicatoritem_node(condition='is',
                                                          document=self.context_document,
                                                          search=self.context_search,
                                                          content_type=self.content_type,
                                                          content=self.content,
                                                          preserve_case=preserve_case,
                                                          negate=negate)
                self.assertEqual(ii_node.get('preserve-case'), 'true' if preserve_case else 'false')
                self.assertEqual(ii_node.get('negate'), 'true' if negate else 'false')

    def test_make_ii_node_bad_condition(self):
        with self.assertRaises(ValueError) as cm:
            ii_node = ioc_api.make_indicatoritem_node(condition='foobarbaz',
                                                      document=self.context_document,
                                                      search=self.context_search,
                                                      content_type=self.content_type,
                                                      content=self.content)


class IOCTestManager(managers.IOCManager):
    """
    Test class for testing the parser callback functionality.
    """
    def __init__(self):
        managers.IOCManager.__init__(self)
        self.child_count = {}
        self.register_parser_callback(self.parse_callback)

    def parse_callback(self, ioc_obj):
        c = ioc_obj.top_level_indicator.getchildren()
        self.child_count[ioc_obj.iocid] = len(c)


class TestIOCManager(unittest.TestCase):
    def setUp(self):
        self.iocm = managers.IOCManager()
        self.test_iocm = IOCTestManager()


    def test_iocm(self):
        iocids = {'378f0cce-b8df-41d5-8189-3d7ec102e52f',
                  '55075e99-273a-4b81-b92b-672be6666474',
                  'c158ef8c-e664-43c5-b71d-3488a3325fcb'}
        self.iocm.insert(OPENIOC_11_ASSETS)
        self.assertEqual(len(self.iocm), 3)
        self.assertEqual(set(self.iocm.iocs.keys()), iocids)

    def test_custom_iocm(self):
        expected_dict = {'378f0cce-b8df-41d5-8189-3d7ec102e52f': 7,
                         '55075e99-273a-4b81-b92b-672be6666474': 1,
                         'c158ef8c-e664-43c5-b71d-3488a3325fcb': 2}
        self.test_iocm.insert(OPENIOC_11_ASSETS)
        self.assertDictEqual(self.test_iocm.child_count, expected_dict)

    def test_custom_iocm_fail(self):
        with self.assertRaises(TypeError):
            self.test_iocm.register_parser_callback('1234')


class TestDowngrade(unittest.TestCase):
    def setUp(self):
        self.iocm = managers.downgrade_11.DowngradeManager()

    def test_downgrade(self):
        self.iocm.insert(OPENIOC_11_ASSETS)
        self.iocm.convert_to_10()
        self.assertEqual(set(self.iocm.iocs_10.keys())-(self.iocm.pruned_11_iocs.union(self.iocm.null_pruned_iocs)),
                         {'c158ef8c-e664-43c5-b71d-3488a3325fcb'})
        self.assertEqual(self.iocm.pruned_11_iocs, {'378f0cce-b8df-41d5-8189-3d7ec102e52f'})
        self.assertEqual(self.iocm.null_pruned_iocs, {'55075e99-273a-4b81-b92b-672be6666474'})
        expected_dict = {'378f0cce-b8df-41d5-8189-3d7ec102e52f': 1,
                         '55075e99-273a-4b81-b92b-672be6666474': 0,
                         'c158ef8c-e664-43c5-b71d-3488a3325fcb': 2}
        for iocid, num_children in expected_dict.items():
            ioc_obj = self.iocm.iocs_10.get(iocid)
            self.assertEqual(len(ioc_obj.top_level_indicator.getchildren()), num_children)



if __name__ == '__main__':
    unittest.main()