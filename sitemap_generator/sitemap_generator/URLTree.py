from treelib import Node, Tree
import graphviz
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from urllib.parse import urlsplit

from django.conf import settings as django_settings


class URLTree(Tree):

    def tree_structure_to_file(self, filepath_base=""):
        filename = filepath_base + '-url_tree.txt'
        filepath = os.path.join(django_settings.STATIC_ROOT, 'tree_structure', filename).replace("\\", "/")

        # if tree file already exist - delete
        if os.path.exists(filepath):
            os.remove(filepath)

        self.save2file(filepath)

    def tree_to_diagram(self):
        return self.show(stdout=False)

    def tree_to_json(self):
        return self.to_json()

    def tree_to_graphviz(self, filepath_base=""):
        filepath = os.path.join(django_settings.GRAPHVIZ_ROOT, (filepath_base + '-tree-graph.gv')).replace("\\", "/")

        # if gv file already exist - delete
        if os.path.exists(filepath):
            os.remove(filepath)

        # self.to_graphviz('tree-graph.gv', shape='plaintext')
        self.to_graphviz(filepath, shape='egg')

    def tree_to_svg(self, filepath_base=""):
        filepath = os.path.join(django_settings.GRAPHVIZ_ROOT, (filepath_base + '-tree-graph.gv')).replace("\\", "/")
        img_path = os.path.join(django_settings.MEDIA_ROOT, (filepath_base + '-diagram')).replace("\\", "/")

        # if image already exist - delete
        if os.path.exists(img_path):
            os.remove(img_path)
            os.remove(img_path + '.svg')

        dot = graphviz.Source.from_file(filepath)
        dot.render((filepath_base + '-diagram'), format='svg', directory=django_settings.MEDIA_ROOT)

    def save_xml_sitemap(self, filepath_base="", sitemap_type='structured'):
        """
        Saving collected hyperlinks to XML sitemap.

        :param sitemap_type: might be 'structured' showing hierarchy or 'flat' listing hyperlinks
        :return: None
        """

        # helper function to create hierarchical sitemap from the tree
        def create_sitemap_recursively(node, parent):
            url = ET.SubElement(parent, 'url')

            loc = ET.SubElement(url, 'loc')
            loc.text = node.tag
            lastmod = ET.SubElement(url, 'lastmod')
            depth = ET.SubElement(url, 'depth')
            depth.text = str(node.data['level'])

            for child in self.children(node.identifier):
                create_sitemap_recursively(child, url)

        ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        xml_root = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')

        if sitemap_type == 'flat':
            for link in self.all_nodes():
                url = ET.SubElement(xml_root, 'url')

                loc = ET.SubElement(url, 'loc')
                loc.text = link.tag

                lastmod = ET.SubElement(url, 'lastmod')

                depth = ET.SubElement(url, 'depth')
                depth.text = link.data['level']

        elif sitemap_type == 'structured':
            root_node = self.all_nodes()[0]
            create_sitemap_recursively(root_node, xml_root)

        tree = ET.ElementTree(xml_root)

        try:
            xml_str = minidom.parseString(ET.tostring(xml_root)).toprettyxml(indent="   ")
            path = os.path.join(django_settings.XML_SITEMAP_ROOT, (filepath_base + '-sitemap.xml'))

            with open(path, "w") as f:
                f.write(xml_str)
        except Exception as e:
            print('XML SITEMAP SAVING ERROR!')
            print(e)
