from cvsvc_apirisk.score.base import ScoreNode, check_meta


class SpecSecSecurityAttr07(ScoreNode):

    def __init__(self, qspec, openapi_ver, target_obj=None, attr_wt=7):
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
        super().__init__()

        #self.fix_template = \
        #    '[CVSPS107] [%s]: Security scope not in "securityDefinitions".'
        #self.fix_template = {
        #        'ruleid': 'CVSPS100a',
        #        'description': 'Security scope not in "securityDefinitions".'
        #        }

        self.qspec = qspec
        self.openapi_ver = openapi_ver
        self.target_obj = target_obj
        self.attr_wt = attr_wt

        return

    def __repr__(self):
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
        return 'sps-sec-attr07'

    def compute_openapiv2(self):
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
        meta = []

        secdefn_node = '%s->securityDefinitions' % self.qspec.ROOT_NODE
        for security_node in self.qspec.get_security_objs():
            for security_idx_node in self.qspec.G.neighbors(security_node):
                for secschm_name_node in self.qspec.G.neighbors(security_idx_node):
                    secschm_name = self.qspec.G.nodes[secschm_name_node]['nodenameraw']
                    for scope_node_idx in self.qspec.G.neighbors(secschm_name_node):
                        for scope_node in self.qspec.G.neighbors(scope_node_idx):
                            scope_name = self.qspec.G.nodes[scope_node]['nodenameraw']
                            target_node = '%s->%s->scopes->%s' % \
                                        (secdefn_node, secschm_name, scope_name)

                            if not self.qspec.G.has_node(target_node):
                                #v = self.fix_template.copy()
                                #v['entity'] = scope_node
                                #v['score'] = self.attr_wt
                                #meta.append(v['entity'])
                                meta.append(scope_node)

        self.score = self.attr_wt*int(len(meta) > 0)
        if len(meta) > 0:
            self.meta = meta

        return

    def compute_openapiv3(self):
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
        meta = []

        all_scopes = set()
        # Collect all defined scopes
        secschms_node = '%s->components->securitySchemes' % self.qspec.ROOT_NODE
        for secschm_node in self.qspec.G.neighbors(secschms_node):
            type_oauth2_node = '%s->type->oauth2' % secschm_node
            if not self.qspec.G.has_node(type_oauth2_node):
                continue

            oauth_flows_node = '%s->flows' % secschm_node
            for oauth_flow_node in self.qspec.G.neighbors(oauth_flows_node):
                scopes_node = '%s->scopes' % oauth_flow_node
                for scope in self.qspec.G.neighbors(scopes_node):
                    all_scopes.add(self.qspec.G.nodes[scope]['nodenameraw'])

        for security_node in self.qspec.get_security_objs():
            for security_idx_node in self.qspec.G.neighbors(security_node):
                for secschm_name_node in self.qspec.G.neighbors(security_idx_node):
                    for scope_node_idx in self.qspec.G.neighbors(secschm_name_node):
                        for scope_node in self.qspec.G.neighbors(scope_node_idx):

                            scope_name = self.qspec.G.nodes[scope_node]['nodenameraw']

                            if scope_name not in all_scopes:
                                #v = self.fix_template.copy()
                                #v['v_entity'] = scope_node
                                #v['v_score'] = self.attr_wt
                                meta.append(scope_node)

        self.score = self.attr_wt*int(len(meta) > 0)
        if len(meta) > 0:
            self.meta = meta

        return

    @check_meta
    def compute(self):
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
        if self.openapi_ver == 'v2':
            self.compute_openapiv2()
        else:
            self.compute_openapiv3()
        return
