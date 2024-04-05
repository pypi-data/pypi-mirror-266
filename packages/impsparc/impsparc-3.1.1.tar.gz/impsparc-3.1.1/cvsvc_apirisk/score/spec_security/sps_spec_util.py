#!/usr/bin/python

import sys
from argparse import ArgumentParser
from configparser import ConfigParser

import networkx as nx


PATH_OPS_v2 = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch']


class QuerySpec(object):

    def __init__(self, spec_obj):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        self.ROOT_NODE = '#'
        self.spec_obj = spec_obj

        self.load_spec2graph()
        return

    def get_desc_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'description':
                node_names.append(self.G.nodes[node]['nodenamesp'])

        return node_names

    def get_param_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        data_types = {}
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'parameters':
                for param_obj_node in self.G.neighbors(node):
                    node_names.append(self.G.nodes[param_obj_node]['nodenamesp'])
                    for param_list in self.G.neighbors(param_obj_node):
                        if self.G.nodes[param_list]['nodenameraw'] == 'type':
                            for _type in  self.G.neighbors(param_list):
                                param_type = self.G.nodes[_type]['nodenamesp']
                                p_type = param_type.split('->')[-1]
                                if p_type in data_types:
                                    data_types[p_type] = data_types[p_type] + 1
                                else:
                                    data_types[p_type] = 1
        return node_names, data_types

    def get_op_objs_list(self):
        method_set = set()
        methods = self.get_op_objs()
        for method in methods:
            method_set.add(method.split('->')[-1])
        return list(method_set)

    def get_method_objs(self):
        node_names = {}
        for node in self.G.nodes:
            nodename = self.G.nodes[node].get('nodenameraw', '')
            if nodename in self.get_op_objs_list():
                if nodename in node_names:
                    node_names[nodename] = node_names[nodename] + 1
                else:
                    node_names[nodename] = 1
        return node_names

    def get_header_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'headers':
                node_names.append(self.G.nodes[node]['nodenamesp'])

        return node_names

    def get_item_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'items':
                node_names.append(self.G.nodes[node]['nodenamesp'])

        return node_names

    def get_schema_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'schema':
                # Check if 'allOf'/'anyof'/'oneOf' operator is being invoked 
                # in a schema. Note that the schema operations are not
                # applicable to items.
                opnode_present = False
                for schma_op in {'allOf', 'anyOf', 'oneOf'}:
                    schma_op_node = '%s->%s' % (node, schma_op)
                    if self.G.has_node(schma_op_node):
                        opnode_present = True
                        break

                if opnode_present:
                    for idx_node in self.G.neighbors(schma_op_node):
                        node_names.append(self.G.nodes[idx_node]['nodenamesp'])
                else:
                    node_names.append(self.G.nodes[node]['nodenamesp'])

        return node_names

    def get_response_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        response_code_count = {}
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'responses':
                for node in self.G.neighbors(node):
                    node_names.append(self.G.nodes[node]['nodenamesp'])
                    response_code = self.G.nodes[node]['nodenameraw']
                    if response_code in response_code_count:
                        response_code_count[response_code] = response_code_count[response_code] + 1
                    else:
                        response_code_count[response_code] = 1

        return node_names, response_code_count

    def incorrect_securityreq_node(self, nodenamesp):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        global_security_node = '%s->security' % self.ROOT_NODE
        if (nodenamesp == global_security_node):
            return False

        fields = nodenamesp.split('->')
        if ((len(fields) >= 5) and (fields[0] == self.ROOT_NODE)
                and (fields[1] == 'paths') and (fields[4] == 'security')):
            return False

        return True

    def get_security_objs(self, child_only=False):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        global_security_node = '%s->security' % self.ROOT_NODE

        node_names = []
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == 'security':
                if child_only and (node == global_security_node):
                    continue

                # Apply node filtering before checking
                nodenamesp = self.G.nodes[node]['nodenamesp']
                if self.incorrect_securityreq_node(nodenamesp):
                    continue

                node_names.append(nodenamesp)

        return node_names

    def get_securitydefn_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        global_secdefn_node = '%s->securityDefinitions' % self.ROOT_NODE

        node_names = []
        for node in self.G.neighbors(global_secdefn_node):
            node_names.append(self.G.nodes[node]['nodenamesp'])

        return node_names

    def get_op_objs(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        node_names = []
        paths_node = '%s->paths' % self.ROOT_NODE
        if self.G.has_node(paths_node):
            for pathitem_node in self.G.neighbors(paths_node):
                for op in PATH_OPS_v2:
                    op_node = '%s->%s' % (pathitem_node, op)
                    if self.G.has_node(op_node):
                        node_names.append(self.G.nodes[op_node]['nodenamesp'])

        return node_names

    def get_keyword_objs(self, keyword):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        if keyword == 'operation':
            return self.get_op_objs()
        if keyword == 'schema':
            return self.get_schema_objs()

        node_names = []
        for node in self.G.nodes:
            if self.G.nodes[node]['nodenameraw'] == keyword:
                node_names.append(self.G.nodes[node]['nodenamesp'])

        return node_names

    def build_graph_recurse(self, G, root_node, obj):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        if type(obj) in {str, int, float}:
            # Add the value
            curr_node = '%s->%s' % (root_node, obj)
            G.add_edge(root_node, curr_node)
            G.nodes[curr_node]['nodenamesp'] = curr_node
            G.nodes[curr_node]['nodenameraw'] = obj
            G.nodes[curr_node]['childtype'] = 'null'

        elif type(obj) == dict:
            for k, v in obj.items():
                curr_node = '%s->%s' % (root_node, k)
                G.add_edge(root_node, curr_node)
                G.nodes[curr_node]['nodenamesp'] = curr_node
                G.nodes[curr_node]['nodenameraw'] = k
                G.nodes[curr_node]['childtype'] = str(type(v))

                self.build_graph_recurse(G, curr_node, v)

        elif type(obj) == list:
            for idx, elem in enumerate(obj):
                curr_node = '%s->%d' % (root_node, idx)
                G.add_edge(root_node, curr_node)
                G.nodes[curr_node]['nodenamesp'] = curr_node
                G.nodes[curr_node]['nodenameraw'] = str(idx)
                G.nodes[curr_node]['childtype'] = str(type(elem))

                self.build_graph_recurse(G, curr_node, elem)

        return G

    def load_spec2graph(self):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        G = nx.DiGraph()
        G.add_node(self.ROOT_NODE)
        G.nodes[self.ROOT_NODE]['nodenamesp'] = self.ROOT_NODE
        G.nodes[self.ROOT_NODE]['nodenameraw'] = self.ROOT_NODE
        G.nodes[self.ROOT_NODE]['childtype'] = str(type(self.spec_obj))

        G = self.build_graph_recurse(G, self.ROOT_NODE, self.spec_obj)
        self.G = G

        return

    def get_node_value(self, node_key):
        """
        Description

        Params
        ------
        p1 : float
            Param description
        p2 : int, optional
            Param description

        Returns
        -------
        result: int
            Result desc
        """
        if node_key.endswith('__key__'):
            node = node_key[:-len('__key__')]
        else:
            node = list(self.G.neighbors(node_key))[0]

        return self.G.nodes[node]['nodenameraw']


def main(argv=sys.argv):
    apar = ArgumentParser()
    apar.add_argument('-c', dest='cfg_file')
    args = apar.parse_args()

    cpar = ConfigParser()
    cpar.read(args.cfg_file)

    return


if __name__ == '__main__':
    sys.exit(main())
