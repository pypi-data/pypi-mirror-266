import chkp_harmony_endpoint_management_sdk.generated.cloud as cloud_operations_base
import chkp_harmony_endpoint_management_sdk.generated.saas as saas_operations_base


def get_operations(target):
    operations = cloud_operations_base.operations
    if target == 'saas':
        operations = saas_operations_base.operations

    available_operations = [item for item in operations if item.get('class_name') != 'session_api']
    return available_operations


def get_method_class(operation_method, target):
    reverse_mapping = {}
    for operation in get_operations(target):
        for method in operation.get('methods'):
            method_name = method.get('method_name')
            reverse_mapping[method_name] = operation.get('class_name')
    return reverse_mapping.get(operation_method)
