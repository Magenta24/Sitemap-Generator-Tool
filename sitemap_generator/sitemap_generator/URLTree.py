from treelib import Node, Tree
import graphviz
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from django.conf import settings as django_settings
import sys

# increasing the recursion limit from 1000 to 10^6
sys.setrecursionlimit(10**6)


class URLTree(Tree):
    """
    This function inherits from Tree class from treelib library.
    Additional methods are as follows:
        - tree_structure_to_file - saving the tree structure to a txt file
        - tree_to_diagram - printing the tree structure to the console
        - tree_to_json - tree structure to JSON
        - tree_to_graphviz - saving the tree structure DOT file
        - tree_to_svg - saving the tree structure as an SVG image
        - save_xml_sitemap - creating a flat or hierarchical XML sitemap
    """

    def tree_structure_to_file(self, filepath_base=""):
        """
        Saving the visual URL tree structure to a file.

        :param filepath_base: contains base URL name and datetime
        :return: None
        """
        filename = filepath_base + '-url_tree.txt'
        filepath = os.path.join(django_settings.STATIC_ROOT, 'tree_structure', filename).replace("\\", "/")

        # if tree file already exist - delete
        if os.path.exists(filepath):
            os.remove(filepath)

        self.save2file(filepath)

    def tree_to_diagram(self):
        """
        Producing the URL tree structure that can be print in the console.

        :return: Visual URL tree structure.
        """
        return self.show(stdout=False)

    def tree_to_json(self):
        return self.to_json()

    def tree_to_graphviz(self, filepath_base=""):
        """
        Saving the URL tree structure to the DOT file.

        :param filepath_base: contains base URL name and datetime
        :return: None
        """
        filepath = os.path.join(django_settings.GRAPHVIZ_ROOT, (filepath_base + '-tree-graph.gv')).replace("\\", "/")

        # if gv file already exist - delete
        if os.path.exists(filepath):
            os.remove(filepath)

        # self.to_graphviz('tree-graph.gv', shape='plaintext')
        self.to_graphviz(filepath, shape='egg')

    def tree_to_svg(self, filepath_base=""):
        """
        Saving the tree structure as an SVG graph-like diagram.

        :param filepath_base: contains base URL name and datetime
        :return: None
        """
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

        :param filepath_base: contains base URL name and datetime
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
                depth.text = str(link.data['level'])

        elif sitemap_type == 'structured':
            root_node = self.all_nodes()[0]
            create_sitemap_recursively(root_node, xml_root)

        tree = ET.ElementTree(xml_root)

        try:
            xml_str = minidom.parseString(ET.tostring(xml_root)).toprettyxml(indent="   ", encoding="utf-8")
            path = os.path.join(django_settings.XML_SITEMAP_ROOT, (filepath_base + '-sitemap.xml'))

            with open(path, "wb") as fp:
                fp.write(xml_str)
        except Exception as e:
            print('XML SITEMAP SAVING ERROR!')
            print(e)
