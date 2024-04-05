import os

from .port_mapping import get_junos_lo_configs
from ..api.netbox.netbox_manager import NetboxManager
from ..api.netbox.util import get_sot_filter_parameters
from ..configs.configs import ( 
    get_configs,
    describe_dev_config
)
from ..configs.models import config_descr
from ..utils.paths import CONFIG_ROOT_DIR
from ..infra.infra import (
    get_infra_attribute,
    import_infra_data
)


def los_config_generate(topo=None):
    """
    TODO: write docstrings
    
    Gera a descricao da configuracao de todos os dispositivos LO a partir dos PO.
    Recebe:
            topo: lista de links (dicionarios de {'id': <int>, 'endpoint_a': {'host': <str>, 'interface': <str>}}
    Retorna:
            dev_config_description - objeto dicionario (config.models.config_descr) contendo a 
            descricao das alteracoes de configuracao associadas a cada dispositivo"""
    dev_config_description = config_descr()

    filter_params = get_sot_filter_parameters()
    netbox_manager = NetboxManager(filter_params=filter_params)
    nr = netbox_manager.get_nornir()
    nr_inv = netbox_manager.get_inventory()

    for host in nr_inv.hosts:
        host_data = nr_inv.hosts[host].data
        manufacturer = host_data['device_type']['manufacturer']['name']
        con_ints=[]
        if topo:
            for link in topo:
                host_a = link['endpoint_a']['host']
                host_z = link['endpoint_z']['host']
                # Link ID is used to identify interface per link
                if host == host_a:
                    con_ints.append({'id': link['id'], 'iface': link['endpoint_a']['interface']})
                elif host == host_z:
                    con_ints.append({'id': link['id'], 'iface': link['endpoint_z']['interface']})
        if con_ints == []:
            con_ints=None 
        lo_configs = get_junos_lo_configs(nornir=nr, dev_name=host, connected_interfaces=con_ints).splitlines()
        dev_config_type = 'procedural'
        dev_full_config = describe_dev_config(
            device=host,
            platform=manufacturer,
            configs=[
                (dev_config_type, lo_configs)
            ]
        )
        dev_config_description['sequential'].append(dev_full_config)

    return dev_config_description




def test(infra_file_path, config_context):

    infra, infra_dicts = import_infra_data(infra_file_path)
    
    dev_config_description = config_descr()

    config_root_dir = CONFIG_ROOT_DIR + config_context + '/'

    for dirpath, dirnames, filenames in os.walk(config_root_dir):
        config_file_path, unconfig_file_path = False, False
                
        for file in filenames:
            if file == 'configure.j2':
                config_file_path = os.path.join(dirpath, file)
            elif file == 'unconfigure.j2':
                unconfig_file_path = os.path.join(dirpath, file)

        # Checa a existencia dos arquivos, pois pode entrar em diretorio que nao ha arquivos de configuracao (caso de ma configuracao)    
        if config_file_path or unconfig_file_path:
            dir_template_struct = dirpath.split(config_root_dir)[-1].split('/')
            fabricante_buscado = dir_template_struct[-1]
            dir_template_struct.remove(fabricante_buscado)
            dir_template_struct_2 = list(dir_template_struct)
            nome_dispositivo = get_infra_attribute(infra_dicts, dir_template_struct, 'nome')
            fabricante_dispositivo = get_infra_attribute(infra_dicts, dir_template_struct_2, 'fabricante')
    
            # Sempre deve haver arquivo de configuracao e por isso checa se ha arquivo de desconfiguracao
            if unconfig_file_path:
                dev_unconfig_type, dev_unconfig, dev_config_type, dev_config = get_configs(
                    infra, 
                    unconfig_path = unconfig_file_path, 
                    config_path = config_file_path
                )
        
                dev_full_config = describe_dev_config(
                    device=nome_dispositivo,
                    platform=fabricante_dispositivo,
                    configs=[
                        (dev_unconfig_type, dev_unconfig),
                        (dev_config_type, dev_config)
                    ]
                )
            else:
                dev_config_type, dev_config = get_configs(
                    infra, 
                    config_path = config_file_path
                )
        
                dev_full_config = describe_dev_config(
                    device=nome_dispositivo,
                    platform=fabricante_dispositivo,
                    configs=[
                        (dev_config_type, dev_config)
                    ]
                )
            dev_config_description['sequential'].append(dev_full_config)

    #TODO ADICIONAR INFORMACOES DE DESCONEXAO FISICA

    return dev_config_description