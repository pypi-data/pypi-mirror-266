import json

from jnpr.junos import Device
from lxml import etree

from ..infra.infra import import_infra_data
from ..api.netbox.netbox_manager import NetboxManager
from ..api.netbox.util import get_sot_filter_parameters
from ..utils.utils import convert_txt_to_pdf
from .junos.tests import junos_show_ospf_neigh


def run_device_tests(infra_file_path, test_context, infra_key, neighbor_ip, neighbor_int, results_file_path):
    """ TODO translate to english

    Realiza a verificação da vizinhança OSPF entre dois dispositivos.
    
    Recebe:
            infra_file_path - caminho do arquivo que descreve a infraestrutura
            test_context - contexto do teste a ser executado
            neighbor_ip - endereco do host a ser encontrado
            neighbor_int - interface onde o vizinho esta conectado
            results_file_path - caminho do arquivo de resultados
            
    Retorna:
            exit(0) - se testes foram bem sucedidos
            exit(1) - se testes foram mal sucedidos"""

    if infra_file_path is not None:
        infra, infra_dicts = import_infra_data(infra_file_path)

    if test_context == 'ospf_tests':
        device_name = infra[infra_key]
        filter_params = get_sot_filter_parameters()
        netbox_manager = NetboxManager(filter_params=filter_params)
        host = netbox_manager.get_nornir().filter(name=device_name)
        print("##################################################################################")
        print("Host: ", host)
        print("##################################################################################")

        result = junos_show_ospf_neigh(host, device_name)

        for neigh in result:
            if neigh['neighbor'] == neighbor_ip and neigh['interface-connected'] == neighbor_int and neigh['neighborhood-success'] == True:
                print(f"The IP {neighbor_ip} IS a neighbor of the host {device_name} through the interface {neighbor_int}!")
                print(f"OSPF neighbor tests was SUCCESSFULL!")
                json_object = json.dumps(result, indent = 4)
                with open(results_file_path, "w") as outfile:
                    outfile.write(json_object)
                convert_txt_to_pdf(results_file_path)
                exit(0)
                
        print(f"The IP {neighbor_ip} is NOT a neighbor of the host {device_name} through the interface {neighbor_int}!")
        print(f"OSPF neighbor tests FAILED!")
        json_object = json.dumps(result, indent = 4)
        with open(results_file_path, "w") as outfile:
            outfile.write(json_object)
        convert_txt_to_pdf(results_file_path)
        exit(1)
                
        return