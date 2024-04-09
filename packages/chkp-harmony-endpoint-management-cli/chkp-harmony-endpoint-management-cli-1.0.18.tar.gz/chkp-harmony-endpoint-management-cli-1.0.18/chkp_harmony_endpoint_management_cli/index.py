import argparse
import os
from chkp_harmony_endpoint_management_cli.logger import sdk_logger as cli_logger, configure_logger, output_issue
from chkp_harmony_endpoint_management_cli import sdk_operations
from chkp_harmony_endpoint_management_cli.generated.build_info import print_cli_build_info
from chkp_harmony_endpoint_management_sdk import HarmonyEndpoint, HarmonyEndpointSaaS, InfinityPortalAuth, HarmonyEndpointSaaSOptions
import chkp_harmony_endpoint_management_sdk.core.harmony_endpoint as harmony_instance
import chkp_harmony_endpoint_management_sdk.core.session_manager as harmony_session
from html import unescape
import json
import inspect
import re
import sys

# Disable SDK message, to keep output with payload only when needed
harmony_instance.print_ea_message = False
# Set proper source header (instead of the py sdk)
harmony_session.SOURCE_HEADER = 'harmony-endpoint-cli'


def __clear_text(plain_text):
    return re.sub(r'<.*?>', '', unescape(plain_text.encode('utf-8').decode('unicode_escape')))


def main_function():
    parser = argparse.ArgumentParser(description='Check Point - Harmony Endpoint management CLI')

    parser.add_argument('--print-operations',
                        dest='print_operations',
                        required=False,
                        action='store_true',
                        help='Print available operations')
    parser.add_argument('--operation',
                        help='Operation to invoke, see --print-operations for all available operations')
    parser.add_argument('--client-id',
                        dest='client_id',
                        default=os.environ.get('CP_CI_CLIENT_ID'),
                        help='CloudInfra "Client ID", can also be passed by CP_CI_CLIENT_ID environment variable')
    parser.add_argument('--access-key',
                        dest='access_key',
                        default=os.environ.get('CP_CI_ACCESS_KEY'),
                        help='CloudInfra "Secret Key", can also be passed by CP_CI_ACCESS_KEY environment variable')
    parser.add_argument('--gateway',
                        dest='gateway',
                        default=os.environ.get('CP_CI_GATEWAY'),
                        help='CloudInfra "Authentication URL", can also be set by CP_CI_GATEWAY environment variable')
    parser.add_argument('--target',
                        choices=['cloud', 'saas'],
                        default='cloud',
                        help='The specification to use for operation')
    parser.add_argument('--header-params',
                        dest='header_params',
                        help='The Rest headers key-value object')
    parser.add_argument('--query-params',
                        dest='query_params',
                        help='The Rest query key-value object')
    parser.add_argument('--path-params',
                        dest='path_params',
                        help='The Rest path name-value object')
    parser.add_argument('--body',
                        dest='body',
                        help='The Rest body payload object')
    parser.add_argument('--verbose',
                        choices=['*', 'info', 'error', 'network'],
                        help='Turn on verbose logger')
    parser.add_argument('--info',
                        action='store_true',
                        help='Show CLI info')

    # Parse the command-line arguments
    args = parser.parse_args()

    print_operations = args.print_operations
    client_id = args.client_id
    access_key = args.access_key
    gateway = args.gateway
    operation = args.operation
    target = args.target
    body = args.body
    query_params = args.query_params
    path_params = args.path_params
    header_params = args.header_params
    verbose = args.verbose
    info = args.info

    if info:
        print('Check Point - Harmony Endpoint Management CLI')
        print(f'    CLI - {print_cli_build_info()}')
        print(f'    Cloud SDK - {HarmonyEndpoint.info()}')
        print(f'    SaaS SDK - {HarmonyEndpointSaaS.info()}')
        print()
        return

    configure_logger(verbose)

    if verbose:
        cli_logger.logger(f'Check Point - Harmony Endpoint Management CLI')
        cli_logger.logger(f'CLI - {print_cli_build_info()}')
        cli_logger.logger(f'Cloud SDK - {HarmonyEndpoint.info()}')
        cli_logger.logger(f'SaaS SDK - {HarmonyEndpointSaaS.info()}')

    if print_operations:
        for operation in sdk_operations.get_operations(target=target):
            for method in operation.get("methods"):
                print(f'- {method.get("method_name")}')
                method_description = method.get("method_description")
                if method_description:
                    print(f'    {__clear_text(method_description)}')
                print(f'')
        return

    if not operation:
        output_issue(verbose, 'Operation parameter is missing, see --print-operations for all available operations')
        sys.exit(1)

    class_name = sdk_operations.get_method_class(operation_method=operation, target=target)
    if not class_name:
        output_issue(
            verbose,
            f'Operation "{operation}" not found, see --print-operations for all available operations')
        sys.exit(1)

    if not client_id:
        output_issue(
            verbose,
            f'CloudInfra "Client ID" is missing, use --client-id or pass CP_CI_CLIENT_ID environment variable')
        sys.exit(1)

    if not access_key:
        output_issue(
            verbose,
            f'CloudInfra "Secret Key" is missing, use --access-key or pass CP_CI_ACCESS_KEY environment variable')
        sys.exit(1)

    if not gateway:
        output_issue(
            verbose,
            f'CloudInfra "Authentication URL" is missing, use --gateway or pass CP_CI_GATEWAY environment variable')
        sys.exit(1)




    try:
        if target == 'cloud':
            he = HarmonyEndpoint()
            he.connect(infinity_portal_auth=InfinityPortalAuth(
                client_id=client_id,
                access_key=access_key,
                gateway=gateway
            ))
        if target == 'saas':
            he = HarmonyEndpointSaaS()
            he.connect(infinity_portal_auth=InfinityPortalAuth(
                    client_id=client_id,
                    access_key=access_key,
                    gateway=gateway,
                    ),
                harmony_endpoint_saas_options=HarmonyEndpointSaaSOptions(
                    activate_mssp_session=True
                )
            )
    except Exception as e:
        output_issue(
            verbose,
            'Connection via CI gateway failed, make sure the keys are validated and Endpoint service is up ')
        output_issue(verbose, f'Error: {str(e)}')
        cli_logger.error_logger(e)
        sys.exit(1)

    class_instance = getattr(he, class_name)
    method = getattr(class_instance, operation)
    parameters = inspect.signature(method).parameters

    arguments = {}

    try:
        if 'header_params' in parameters:
            arguments['header_params'] = json.loads(header_params or '{}')
    except Exception as e:
        output_issue(verbose, 'Parsing header-params failed')
        output_issue(verbose, str(e))
        cli_logger.error_logger(e)
        sys.exit(1)

    try:
        if 'body' in parameters:
            arguments['body'] = json.loads(body or '{}')
    except Exception as e:
        output_issue(verbose, 'Parsing body failed')
        output_issue(verbose, str(e))
        cli_logger.error_logger(e)
        sys.exit(1)

    try:
        if 'path_params' in parameters:
            arguments['path_params'] = json.loads(path_params or '{}')
    except Exception as e:
        output_issue(verbose, 'Parsing path-params failed')
        output_issue(verbose, str(e))
        cli_logger.error_logger(e)
        sys.exit(1)

    try:
        if 'query_params' in parameters:
            arguments['query_params'] = json.loads(query_params or '{}')
    except Exception as e:
        output_issue(verbose, 'Parsing query-params failed')
        output_issue(verbose, str(e))
        cli_logger.error_logger(e)
        sys.exit(1)

    try:
        method_result = method(**arguments)
        if method_result.payload:
            print(method_result.payload)
    except Exception as e:
        output_issue(verbose, f'Calling {operation} failed')
        output_issue(verbose, str(e))
        cli_logger.error_logger(e)
        sys.exit(1)

    if verbose:
        cli_logger.logger(f'Calling {operation} succeeded')


if __name__ == "__main__":
    main_function()
