PORT_MAPPING_DB = 'port_mapping_'

PORTS_TABLE =  'PORTS'

PORTS_COLUMN_NAMES = ['id', 'po_interface', 'lo_interface']

INVALID_JUNOS_CONFIG_STATEMENTS = ['data', 'configuration-', 'version', 'forwarding-options']


def endpoint(host, interface):
    endpoint = {
        'host': host,
        'interface': interface
    }
    return endpoint


def link(link_id, host_a, interface_a, host_z, interface_z):
    link = {
        "id": link_id,
        "endpoint_a": endpoint(host_a, interface_a),
        "endpoint_z": endpoint(host_z, interface_z)
    }
    return link