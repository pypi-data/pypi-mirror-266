import xmltodict
import json

from jnpr.junos import Device
from lxml import etree


def junos_ping(host, device_name, target, count='4', size='64', do_not_fragment=False):
    """
	TODO: write docstrings
	"""
    
    dev = Device(
        host=host.inventory.hosts[device_name].hostname, 
        user=host.inventory.hosts[device_name].username, 
        passwd=host.inventory.hosts[device_name].password,
        port=host.inventory.hosts[device_name].port
    )
    dev.open()
    
    test=dev.rpc.ping(host=target, count=count, size=size, do_not_fragment=do_not_fragment)
    o = xmltodict.parse(etree.tostring(test))
    dev.close()

    loss_number = o['ping-results']['probe-results-summary']['packet-loss']
    ping_success = True if loss_number == '0' else False

    ping_results = {
        'ping-results': o['ping-results'],
        'summary': o['ping-results']['probe-results-summary'],
        'loss-number': o['ping-results']['probe-results-summary']['packet-loss'],
        'ping-success': ping_success,
    }
    return ping_results


def junos_show_ospf_neigh(host, device_name):
    """ TODO translate to english

    Realiza a verificação da vizinhança OSPF entre o equipamento de Acesso e CPE.
    
    Recebe:
            host - nornir object em que será realizado o teste a ser realizado o teste
            device_name - nome do dispositivo em que será realizado o teste
            
    Retorna:
            show_ospf_neigh_results - resultados do comando de exibicao de vizinhos ospf
            em uma lista"""

    command = 'show ospf neighbor'
    
    
    dev = Device(
        host=host.inventory.hosts[device_name].hostname, 
        user=host.inventory.hosts[device_name].username, 
        passwd=host.inventory.hosts[device_name].password,
        port=host.inventory.hosts[device_name].port
    )
    dev.open()

    # Gets the result of the command entered into the respective equipment
    result=dev.rpc.cli(command, format='text')
    output_text = etree.tostring(result, encoding='unicode')
    dev.close()
    
    # Get for each neighbor IP address its neighbor state
    show_ospf_neigh_results = []
    output_lines = output_text.strip().split('\n')
    for line in output_lines[1:]:  # Ignore Header
        columns = line.split()
        if len(columns) >= 4 and (columns[0] != "Address" and columns[0] != ""):
            neigh = {}
            neigh['neighbor'] = columns[0]
            neigh['interface-connected'] = columns[1]
            neigh['state'] = columns[2]
            print("Neighboor: ", neigh)
            if columns[2] == 'Full':
                neigh['neighborhood-success'] = True
            else:
                neigh['neighborhood-success'] = False
            show_ospf_neigh_results.append(neigh)

    return show_ospf_neigh_results