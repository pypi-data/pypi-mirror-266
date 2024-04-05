#!/usr/bin/python

import re


RISK_CTGS = {
            'Security': 0,
            'Data': 1,
            'Format': 2
            }
RISK_SUBCTGS = {
            'Security': {
                        'Authentication': 0,
                        'Authorization': 1,
                        'Transport': 2
                        },
            'Data': {},
            'Format': {}
            }
SEVERITY_CTGS = {
                'Critical': 0,
                'High': 1,
                'Medium': 2,
                'Low': 3,
                'NoRisk': 4
                }


def init_rules_ds(rule_exps):
    #print(rule_exps)
    RISK_CTGS = {}
    RISK_SUBCTGS = {}
    for rule in rule_exps.values():
        ctg = rule['category']
        sub_ctg = rule['sub_category']

        # Categories
        if ctg not in RISK_CTGS:
            idx = len(RISK_CTGS)
            RISK_CTGS[ctg] = idx

        # Sub-categories
        if ctg not in RISK_SUBCTGS:
            RISK_SUBCTGS[ctg] = {}
        if sub_ctg not in RISK_SUBCTGS[ctg]:
            idx = len(RISK_SUBCTGS[ctg])
            RISK_SUBCTGS[ctg][sub_ctg] = idx

    return RISK_CTGS, RISK_SUBCTGS


def isvalid_url(url):

    if not (url.startswith('http://') or url.startswith('https://')):
        return False

    return True


def get_severity(score):
    if 9 <= score <= 10:
        return 'Critical'
    elif 6 <= score <= 8:
        return 'High'
    elif 4 <= score <= 5:
        return 'Medium'
    elif 1 <= score <= 3:
        return 'Low'
    elif score == 0:
        return 'NoRisk'

    return 'Invalid'


def get_risk_ctg(v_ruleid):
    specrisk_code = v_ruleid[4:6]

    if specrisk_code == 'F0':
        risk_ctg, risk_subctg = 'Format', None
    elif specrisk_code == 'D0':
        risk_ctg, risk_subctg = 'Data', None
    elif specrisk_code == 'S0':
        risk_ctg, risk_subctg = 'Security', 'Authentication'
    elif specrisk_code == 'S1':
        risk_ctg, risk_subctg = 'Security', 'Authorization'
    elif specrisk_code == 'S2':
        risk_ctg, risk_subctg = 'Security', 'Transport'
    else:
        raise(ValueError('Invalid code'))

    return (risk_ctg, risk_subctg)


def get_api(remed_clue):
    fields = remed_clue.split(' ')
    if fields[3] == 'paths':
        api = fields[5]
        return api

    return None


def get_api_op(remed_clue):
    fields = remed_clue.split(' ')
    if fields[3] == 'paths':
        api_op = fields[7]
        return api_op.strip(']:')

    return None


def get_api_param(remed_clue):
    fields = remed_clue.split(' ')
    if fields[3] == 'paths' and fields[9] == 'parameters':
        api_param = fields[11]
        return api_param.strip(']:')

    return None


def get_api2(remed_clue):
    matches = re.findall('\((.*?)\)', remed_clue)
    # print(matches)
    for match in matches:
        identifier = match.split(' ')[0]
        if identifier.startswith('#->paths->'):
            api = identifier.split('->')[2]
            return api

    return None


def get_api2_op(remed_clue):
    matches = re.findall('\((.*?)\)', remed_clue)

    for match in matches:
        identifier = match.split(' ')[0]
        if identifier.startswith('#->paths->'):
            api_op = identifier.split('->')[3]
            return api_op

    return None


def get_api2_param(remed_clue):
    matches = re.findall('\((.*?)\)', remed_clue)

    for match in matches:
        identifier = match.split(' ')[0]
        fields = identifier.split('->')
        if identifier.startswith('#->paths->') and len(fields) > 5 and fields[4] == 'parameters':
            api_op = fields[5]
            return api_op

    return None


def parse_cvlrange(linenum_mapping, target_node, ret_cvlrangeds=False):

    if linenum_mapping is None:
        return ''

    try:
        target_node = re.sub(r'__key__$', '', target_node)
        cvlrange_ds = None      # cvlrange data structure
        nodes = target_node.split('->')
        level = 0

        while level < len(nodes):

            node = nodes[level]

            if level == 0 and node != '#':
                raise ValueError('[01] Problem while identifying line num for'
                                 'target %s...' % target_node)

            if level == 0:
                cvlrange_ds = linenum_mapping
                level += 1
                continue

            try:
                if type(cvlrange_ds) == list:
                    cvlrange_ds = cvlrange_ds[int(node)]
                else:
                    cvlrange_ds = cvlrange_ds[node]
            except KeyError:
                if '$ref' in cvlrange_ds:
                    # The key error could be because the spec points to another
                    # ref
                    ref_str = cvlrange_ds['$ref'][0].replace('/', '->')
                    cvlrange_ds = parse_cvlrange(linenum_mapping, ref_str,
                                                 ret_cvlrangeds=True)
                    continue
                else:
                    # If node not present, pass so that the line num of
                    # parent gets returned
                    pass

            level += 1

        if ret_cvlrangeds:
            return cvlrange_ds

        if type(cvlrange_ds) == dict:
            line_num = cvlrange_ds['cvlrange26uel7Ao'][0]
        else:
            line_num = cvlrange_ds[-1]['cvlrange26uel7Ao'][0]

        linenum_idstr = '[%d]' % line_num
    except:
        linenum_idstr = ''

    return linenum_idstr
