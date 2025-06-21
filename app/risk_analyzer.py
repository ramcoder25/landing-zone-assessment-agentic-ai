import networkx as nx

def analyze_for_risks_and_dependencies(resources, subscriptions):
    g = nx.DiGraph()
    for sub in subscriptions:
        g.add_node(sub['id'], label=sub['display_name'], type='Subscription', details=sub)
    for res in resources:
        res_id = res.get('id')
        res_type = res.get('type')
        res_name = res.get('name')
        if not res_id:
            continue
        node_attrs = {'label': res_name, 'type': res_type, 'details': res, 'risks': []}
        g.add_node(res_id, **node_attrs)
        sub_id_prefix = '/'.join(res_id.split('/')[:3])
        if g.has_node(sub_id_prefix):
            g.add_edge(sub_id_prefix, res_id)
        if res_type == 'Microsoft.Network/networkSecurityGroups':
            rules = res.get('security_rules', [])
            for rule in rules:
                if rule.get('access') == 'Allow' and rule.get('direction') == 'Inbound' and (rule.get('source_address_prefix') in ['*', 'Any', 'Internet']) and (rule.get('destination_port_range') in ['3389', '22']):
                    node_attrs['risks'].append({'level': 'High', 'description': f"Insecure rule '{rule.get('name')}' allows RDP/SSH from the Internet."})
        elif res_type == 'Microsoft.Network/virtualNetworks':
            for subnet in res.get('subnets', []):
                subnet_id = subnet.get('id')
                g.add_node(subnet_id, label=subnet.get('name'), type='Subnet', details=subnet)
                g.add_edge(res_id, subnet_id)
                if not subnet.get('network_security_group'):
                    g.nodes[subnet_id]['risks'] = [{'level': 'Medium', 'description': 'Subnet has no Network Security Group attached.'}]
                else:
                    nsg_id = subnet['network_security_group']['id']
                    if g.has_node(nsg_id):
                        g.add_edge(subnet_id, nsg_id)
        g.nodes[res_id].update(node_attrs)
    return g
