from enum import Enum


class ConMethods(str, Enum):
    path = 'v1'
    get_cab_diagnostic = 'getCableDiagnostic'
    get_ports_count = 'getPortsCount'
    get_port_errors = 'getPortErrors'
    get_comm_info = 'getCommutatorInfo'
    get_port_info = 'getPortInfo'
    run_full_diagnostic = 'runFullDiagnostic'
    clear_port_errors = 'clearPortErrors'
