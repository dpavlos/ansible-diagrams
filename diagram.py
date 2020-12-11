# diagram.py
__author__ = 'Pavlos Daoglou'

from collections import defaultdict
from itertools import islice
from diagrams import Cluster, Diagram, Edge
from diagrams.elastic.elasticsearch import Beats, Elasticsearch as ES, Kibana, Logstash as LG

from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

elk = defaultdict(list)
loader = DataLoader()
inventory = InventoryManager(loader=loader, sources='/path/inventory')

lg_nodes = inventory.groups['logstash'].get_hosts()
kibana_nodes = inventory.groups['kibana'].get_hosts()
# Limit the number of returned nodes from ansible inventory to prevent creating too large diagrams
el_master_nodes = islice(inventory.groups['els_master'].get_hosts(),3)
el_data_nodes = islice(inventory.groups['els_data'].get_hosts(),6)

with Diagram(show=False, name="Elasticsearch Infrastructure", filename="es", direction="TB"):
    beats = [Beats("filebeat"), Beats("metricbeat"), Beats("winlogbeat")]

    for lg_node in lg_nodes:
        elk['logstash'].append(LG(str(lg_node).split('.')[0]))

    for kibana_node in kibana_nodes:
        elk['kibana'].append(Kibana(str(kibana_node).split('.')[0]))

    with Cluster("ES nodes"):
        with Cluster("master"):
            for el_master in el_master_nodes:
                elk['masternodes'].append(ES(str(el_master).split('.')[0]))
        with Cluster("data") as datanodes:
            for el_data in el_data_nodes:
                elk['datanodes'].append(ES(str(el_data).split('.')[0]))
    for lg in elk['logstash']:
        for beat in beats:
            beat >> lg
        lg >> elk['datanodes']
    #Shift operations are not supported between clusters, so connect the first item from kibana to datanodes subgraph
    elk['datanodes'] << elk['kibana'][0]
