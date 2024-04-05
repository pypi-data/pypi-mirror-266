#!/usr/bin/python

# TODO:
# - for "conj" replace "" by $
# - Determine the location of the failure as well
# - read raw/json rules based on input
# - solve the issue around operator precedence
# - Add debug messages
# - Sort output by rule id

# Instructions:
# - Rules are case-sensitive
# - operations should be smaller case
# - value for "is-missing" has to be boolean
# - if one wildcard used, all should be wildcards
# - use "eq"/"ne" for string operations
# - all wildcard calls silently fail if the field is absent
# - identifier/condition/value separable only by a space

# - __key__ can only occur for the last node
# - also check that "parameters.*" should be same rather than only "parameters"


import sys
from argparse import ArgumentParser
import json
import re
#import ipdb
#import faulthandler

from networkx.exception import NetworkXError
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

from cvsvc_apirisk.score.spec_security.sps_main import SpecSecMain
from cvsvc_apirisk.score.spec_security.sps_common import get_severity, \
                                            parse_cvlrange


BNF_GRAMMAR = \
        """
        rule = (expr)+
        expr = identifier " " condition " " value conj
        identifier = ~r"[a-zA-Z0-9\.\/\#]+"
        condition = ~r"[a-z\-<>=!]+"
        value = ~r"[a-zA-Z0-9]+"
        conj = " AND " / " OR " / ""
        """
RULE_OPS = {'and', 'or'}


class SpecSecCustomRulesMain(object):

    def __init__(self, target_obj, openapi_ver, linenum_mapping=None):
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
        self.spec_main = SpecSecMain(target_obj=target_obj,
                                     openapi_ver=openapi_ver)
        self.num_evaluations = 0
        self.linenum_mapping = linenum_mapping

        return

    def read_rules_raw(self, rules_path):
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
        self.grammar = Grammar(BNF_GRAMMAR)
        rules = []
        with open(rules_path) as inf:
            for line in inf:
                name, score, rule = line.strip().split(',')
                print('-'*50)
                grammar_tree = self.grammar.parse(rule)
                sr_visitor = SpecRuleVisitor()
                rule = sr_visitor.visit(grammar_tree)
                print(rule)
                rules.append(rule)

        return rules

    def read_rules_json(self, rules_path):
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
        with open(rules_path) as inf:
            rules_dict = json.load(inf)

        rules = {}
        for rule_dict in rules_dict['rules']:
            rule_id = rule_dict['ruleid']
            rule_flt = []   # Flattened rule exp
            for rule in rule_dict['rule']:
                if type(rule) == dict:
                    rule_flt.append('%s %s %s' % (rule['identifier'],
                                                  rule['condition'],
                                                  rule['value']))
                else:
                    # should be str
                    rule_flt.append(rule)

            rule_dict['rule_flt'] = rule_flt
            rules[rule_id] = rule_dict

        return rules

    def is_keyword(self, identifier):
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
        prefix = identifier.split('->')[0]
        if identifier.startswith('__'):
            return False
        else:
            return not prefix.startswith(self.spec_main.qspec.ROOT_NODE)

    def determine_keywords_in_rule(self, rule, all_keywords):
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

        for idx, raw_expr in enumerate(rule):
            if raw_expr in RULE_OPS:
                continue

            identifier, condition, value = raw_expr.split(' ')
            identifier = re.sub(r'__key__$', '', identifier)

            if identifier.startswith('__rule__'):
                rule_id = identifier[len('__rule__'):]
                nested_rule = self.rules[rule_id]['rule_flt']
                self.determine_keywords_in_rule(nested_rule, all_keywords)
            else:
                # Identify if it is a keyword
                is_kw = self.is_keyword(identifier)
                if is_kw:
                    prefix = identifier.split('->')[0]
                    all_keywords.add(prefix)

        return

    def sanity_check(self, rule):
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
        #ipdb.set_trace()

        # Keyword prefixes, if any, should be the same.
        all_keywords = set()
        self.determine_keywords_in_rule(rule, all_keywords)

        if len(all_keywords) > 1:
            print(all_keywords)
            raise ValueError('[%s] All keyword prefixes should '
                             'be the same across the rule.' % rule)

        # Check if conditions are correct
        for raw_expr in rule:
            if raw_expr in RULE_OPS:
                continue
            identifier, condition, value = raw_expr.split(' ')
            if condition not in {'<', '>', '<=', '>=', '==', '!=', 'eq', 'ne',
                                 'pattern-match', 'is-missing', 'is-empty'}:
                raise ValueError('Unknown condition: %s ' % condition)

        # "is-*" value should be bool
        for raw_expr in rule:
            if raw_expr in RULE_OPS:
                continue
            identifier, condition, value = raw_expr.split(' ')
            if condition in {'is-missing', 'is-empty'}:
                if value.lower() not in {'true', 'false'}:
                    raise ValueError("[%s] Value for %s operator should be "
                                     "True/False" % (condition, raw_expr))

        return

    def get_expr(self, node, condition, value):
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
        identifier = node   #.replace('->', '.')
        #ipdb.set_trace()

        if condition in {'<', '>', '<=', '>=', '==', '!='}:
            try:
                if str(node).lower() in {'true', 'false'}:
                    id_value = node
                else:
                    id_value = int(self.spec_main.qspec.get_node_value(node))
                    value = int(value)
            except NetworkXError:
                raise ValueError('[%s] Unknown identifier' % identifier)

            return '(%s %s %s)' % (id_value, condition, value)

        elif condition in {'eq', 'ne'}:
            t_cond = '==' if condition == 'eq' else '!='
            try:
                id_value = self.spec_main.qspec.get_node_value(node)
            except NetworkXError:
                raise ValueError('[%s] Unknown identifier' % identifier)

            return '("%s" %s "%s")' % (id_value, t_cond, value)

        elif condition == 'pattern-match':
            #ipdb.set_trace()
            try:
                id_value = self.spec_main.qspec.get_node_value(node)
            except NetworkXError:
                raise ValueError('[%s] Unknown identifier' % identifier)

            return '(bool(re.search("%s", "%s")))' % (value, id_value)

        elif condition == 'is-missing':
            has_node = not self.spec_main.qspec.G.has_node(node)

            return '(%s == %s)' % (has_node, value)

        elif condition == 'is-empty':
            #ipdb.set_trace()
            try:
                num_nbrs = len(list(self.spec_main.qspec.G.neighbors(node)))
            except NetworkXError:
                raise ValueError('[%s] Unknown identifier' % identifier)
            has_no_nbrs = (num_nbrs == 0)

            return '(%s == %s)' % (has_no_nbrs, value)

        return

    def identifier2nodes(self, identifier, is_identifier_a_keyword,
                         is_identifier_nestedref, rule_dict):
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

        # When the identifier is a rule itself; return the boolean outcomes as
        # nodes 
        if is_identifier_nestedref:
            rule_id = identifier[len('__rule__'):]
            rule_dict = self.rules[rule_id]
            _, _, nested_pernode_outcome, nested_pernode_raw_rule = \
                    self.analyze_rule(rule_dict, list_node_outcomes=True)
            nodes = nested_pernode_outcome
            return (nodes, nested_pernode_raw_rule)

        key_enabled = False
        if re.search('__key__$', identifier):
            key_enabled = True
            identifier = re.sub(r'__key__$', '', identifier)

        for idx, field in enumerate(identifier.split('->')):
            if idx == 0:
                if field == '#':
                    # Not a keyword
                    nodes = ['#']
                else:
                    # a keyword
                    nodes = self.spec_main.qspec.get_keyword_objs(field)

            elif field == '*':
                # NOTE: We raise the exception here for "*" but for other
                # invalid nodes, we raise the exception in get_expr()
                new_nodes = []
                for node in nodes:
                    try:
                        for nbr_node in self.spec_main.qspec.G.neighbors(node):
                            new_nodes.append(nbr_node)
                    except NetworkXError:
                        if is_identifier_a_keyword:
                            pass
                        else:
                            raise ValueError('[%s] Unknown identifier' % identifier)

                nodes = new_nodes

            else:
                # Regular attribute access
                nodes = list(map(lambda n: '%s->%s' % (n, field), nodes))

        if key_enabled:
            nodes = list(map(lambda n: n + '__key__', nodes))

        # [] for pernode_raw_rule which is applicable only for nested rule
        return nodes, []

    def check_embd_rule(self, rule):
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
        if len(rule) == 1:
            identifier, condition, value = rule[0].split(' ')
            if condition == 'embedded-run':
                # It is an embedded rule
                self.spec_main.children[identifier].compute()
                meta = self.spec_main.children[identifier].meta

                return True, (meta is not None), meta

        # In every other case, return False
        return False, None, None

    def analyze_rule(self, rule_dict, list_node_outcomes=False):
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
        rule = rule_dict['rule_flt']

        #ipdb.set_trace()
        # Check if the rule is hard-coded
        ran_embdr, has_violation, violating_rules = self.check_embd_rule(rule)
        if ran_embdr:
            # Return False because the check_embd_rule() will add the
            # violation to meta

            return has_violation, violating_rules, None, None

        self.sanity_check(rule)

        # Need to handle two major cases
        # 1. An absolute identifier with a keyword-based identifier
        # 2. More than one keyword-based identifiers

        # TWO issues:
        # - the returned rule_nodes can be [] ; soln is assume false
        # - how to evaluate expr first before going to next

        # E.g. node_cache: [['#->security', '#->api'], None, ['#->parameters->0', '#->parameters->1']]

        violating_rules = []        # List of all checks violating the rule
        pernode_procd_rule = []     # per node processed rule. E.g. 200 < 400
        pernode_raw_rule = []       # per node raw rule. E.g. response.200 < 400
        evaled_part_rule = None     # Array; for this rule, holds the state of
                                    # evaluations done for the concat exprs
        num_node_iterations = 0     # Changes based on how many node does the
                                    # expr resolve to

        #faulthandler.enable()

        for rule_idx, raw_expr in enumerate(rule):

            if raw_expr in RULE_OPS:
                pernode_procd_rule.append(raw_expr)
                pernode_raw_rule.append(raw_expr)
                continue

            identifier, condition, value = raw_expr.split(' ')

            is_identifier_nestedref = identifier.startswith('__rule__')

            is_identifier_a_keyword = self.is_keyword(identifier)

            # Resolve the identifier to corresponding nodes;
            # "nested_pernode_raw_rule" gets populated if the identifier is a
            # rule.
            id_nodes, nested_pernode_raw_rule = \
                    self.identifier2nodes(identifier, is_identifier_a_keyword,
                                          is_identifier_nestedref, rule_dict)
            if len(id_nodes) == 0:
                #print('DEBUG: No nodes associated with identifier: %s' %
                #      identifier)
                pass

            num_node_iterations = max(num_node_iterations, len(id_nodes))

            # Each element in either of these lists represents data for the
            # node encountered for this expression within the rule
            evaled_part_rule_stg = []
            pernode_procd_rule_stg = []
            pernode_raw_rule_stg = []

            for itr_idx in range(num_node_iterations):

                # Get the correct node to analyze
                node_idx = min(len(id_nodes) - 1, itr_idx)
                try:
                    # IndexError possible when id_nodes is empty. In which case
                    # we assume the expression evaluated to False only in case
                    # of keyword-based identifiers
                    target_node = id_nodes[node_idx]
                    expr = self.get_expr(target_node, condition, value)

                    '''
                    if rule_dict['ruleid'] == 'CVSPS002':
                        print(expr)
                    '''

                    # evaled_expr used for operator precedence
                    evaled_expr = eval(expr)
                except Exception as e:
                    if not is_identifier_a_keyword:
                        if type(e) == IndexError:
                            # Raise ValueError to maintain consistency with
                            # unidentified nodes in get_expr()
                            raise ValueError('[%s] Unknown identifier' %
                                             identifier)
                        else:
                            raise
                    # In case of keyword-based identifiers, silently ignore
                    # the missing nodes. This is unlike the absolute identifier
                    expr = str(False)
                    evaled_expr = False

                procd_rule = expr
                if is_identifier_nestedref:
                    raw_rule = '(%s %s %s)' % \
                        (nested_pernode_raw_rule[node_idx], condition, value)
                else:
                    raw_rule = '(%s %s %s)%s' % \
                        (target_node, condition, value,
                                parse_cvlrange(self.linenum_mapping,
                                                  target_node))

                # To support expressions such as "True or undefined-var", we
                # need to evaluate every local expression
                # NOTE: With the implementation below, we evaluate all
                # operators from left to right and the operators AND/OR have
                # the same precedence
                if rule_idx == 0:
                    evaled_intm_expr = evaled_expr
                    intm_procd_rule = procd_rule
                    intm_raw_rule = raw_rule
                else:
                    # part rule column idx; 0 if the previous expression was an
                    # absolute identifier
                    part_rule_cidx = min(len(evaled_part_rule) - 1, itr_idx)
                    part_rule_bool = evaled_part_rule[part_rule_cidx]

                    # Get the intermediate expr using the previously evaluated
                    # sub-rule and the operator preceding this expression
                    intm_expr = '%s %s %s' % \
                        (part_rule_bool, rule[rule_idx - 1], evaled_expr)
                    evaled_intm_expr = eval(intm_expr)

                    # Get the intermediate procd/raw rules
                    intm_procd_rule = '%s %s %s' % \
                        (pernode_procd_rule[part_rule_cidx], rule[rule_idx - 1],
                         procd_rule)
                    intm_raw_rule = '%s %s %s' % \
                        (pernode_raw_rule[part_rule_cidx], rule[rule_idx - 1],
                         raw_rule)

                evaled_part_rule_stg.append(evaled_intm_expr)
                pernode_procd_rule_stg.append(intm_procd_rule)
                pernode_raw_rule_stg.append(intm_raw_rule)

                if (evaled_intm_expr and ((rule_idx + 1 == len(rule)) or
                        (rule[rule_idx + 1] == 'or'))):
                    # Break out if there is just one rule or if the next
                    # operator is an "or". Because "True or ...." makes it
                    # True.
                    # Else, keep evaluating the next expression.
                    violating_rules.append(intm_raw_rule)

            evaled_part_rule = evaled_part_rule_stg
            pernode_procd_rule = pernode_procd_rule_stg
            pernode_raw_rule = pernode_raw_rule_stg

            '''
            if rule_dict['ruleid'] == 'CVSPS002':
                print('per node procd/raw rule')
                print(pernode_procd_rule)
                print()
                print(pernode_raw_rule)
                print('+'*10)
            '''

            if len(evaled_part_rule) == len(violating_rules):
                # NO need to go to the next rule
                # print('DEBUG: Breaking out from further analysis...')
                break

        self.num_evaluations += num_node_iterations

        # Evaluate the final expression
        if len(pernode_procd_rule) != 0:
            intm_outcome = False
            for i in range(0, len(pernode_procd_rule), 100):
                expanded_rule = ' or '.join(pernode_procd_rule[i:i+100])
                intm_outcome = eval('%s or %s' % (intm_outcome, expanded_rule))
            outcome = intm_outcome
        else:
            outcome = False

        nested_pernode_outcome, nested_pernode_raw_rule = [], []
        if list_node_outcomes:
            for idx in range(len(pernode_raw_rule)):
                nested_pernode_outcome.append(eval(pernode_procd_rule[idx]))
                nested_pernode_raw_rule.append(pernode_raw_rule[idx])

        '''
        # Debug print
        if outcome:
            for vr in violating_rules:
                print('\t%s' % vr)
        '''

        return (outcome, violating_rules,
                nested_pernode_outcome, nested_pernode_raw_rule)

    def analyze_rules(self, rules):
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
        self.rules = rules
        self.spec_main.meta = []

        for _, rule_dict in self.rules.items():
            if not rule_dict.get('enabled', True):
                continue
            #print('-'*50)
            #print('Analyzing rule: [%s] %s' % (rule_dict['ruleid'],
            #                                   rule_dict['rule_flt']))
            has_violation, violating_rules, _, _ = self.analyze_rule(rule_dict)

            if has_violation:
                for vr in violating_rules:
                    violation = {}
                    violation['v_ruleid'] = rule_dict['ruleid']
                    violation['v_description'] = rule_dict['description']
                    violation['v_score'] = rule_dict['score']
                    violation['v_severity'] = get_severity(rule_dict['score'])
                    violation['v_risk_ctg'] = rule_dict['category']
                    violation['v_risk_subctg'] = rule_dict['sub_category']
                    violation['v_tags'] = rule_dict.get('tags', [])
                    violation['v_entity'] = vr

                    self.spec_main.meta.append(violation)

        # Set the max score
        self.spec_main.score = max([v['v_score'] for v in self.spec_main.meta],
                                   default=0)

        return


class SpecRuleVisitor(NodeVisitor):

    def __init__(self):
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
        return

    def visit_rule(self, node, visited_children):
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
        output = []
        print('reached rule')
        for ruleconj in node.children[:-1]:
            rulestr = ruleconj.text
            tokens = rulestr.split(' ')
            rule = ' '.join(tokens[:3])
            output.append(rule)
            conj = tokens[3]
            output.append(conj)

        # Analyze the last rule
        ruleconj = node.children[-1]
        rulestr = ruleconj.text
        rule = rulestr.strip()
        output.append(rule)

        return output

    def visit_expr(self, node, visited_children):
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
        print('reached expr')
        return

    def visit_identifier(self, node, visited_children):
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
        for child in visited_children:
            print(child)
        print('reached identifier: %s' % node.text)
        return

    def visit_condition(self, node, visited_children):
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
        print('reached condition: %s' % node.text)
        return

    def visit_value(self, node, visited_children):
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
        print('reached value: %s' % node.text)
        return

    def visit_conj(self, node, visited_children):
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
        print('reached conj')
        return

    def generic_visit(self, node, visited_children):
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
        print('reached genericvisit: %s' % node)
        return


def main(argv=sys.argv):
    apar = ArgumentParser()
    apar.add_argument('-s', dest='spec_path')
    apar.add_argument('-r', dest='rules_path')
    args = apar.parse_args()

    crules = SpecSecCustomRulesMain(args.spec_path)
    rules = crules.read_rules_json(args.rules_path)
    crules.analyze_rules(rules)

    return


if __name__ == '__main__':
    sys.exit(main())
