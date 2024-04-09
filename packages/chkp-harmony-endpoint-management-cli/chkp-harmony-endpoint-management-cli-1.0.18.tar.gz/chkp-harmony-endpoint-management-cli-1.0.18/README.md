# Check Point - Harmony Endpoint Management CLI

[![License](https://img.shields.io/github/license/CheckPointSW/harmony-endpoint-management-cli.svg?style=plastic)](https://github.com/CheckPointSW/harmony-endpoint-management-cli/blob/release/LICENSE) [![Latest Release](https://img.shields.io/github/v/release/CheckPointSW/harmony-endpoint-management-cli?style=plastic)](https://github.com/CheckPointSW/harmony-endpoint-management-cli/releases) [![PyPI version](https://img.shields.io/pypi/v/chkp-harmony-endpoint-management-cli.svg?style=plastic)](https://pypi.org/project/chkp-harmony-endpoint-management-cli/)


<!-- 
Coming soon :)

[![GitHub stars](https://img.shields.io/github/stars/CheckPointSW/harmony-endpoint-management-cli.svg?style=social&label=Star)](https://github.com/CheckPointSW/harmony-endpoint-management-cli/stargazers) -->

[![Build CLI](https://github.com/CheckPointSW/harmony-endpoint-management-cli/actions/workflows/build.yml/badge.svg)](https://github.com/CheckPointSW/harmony-endpoint-management-cli/actions/workflows/build.yml) [![Publish CLI](https://github.com/CheckPointSW/harmony-endpoint-management-cli/actions/workflows/release.yml/badge.svg)](https://github.com/CheckPointSW/harmony-endpoint-management-cli/actions/workflows/release.yml)

This is the Harmony Endpoint management CLI

The CLI is based on the public [Harmony Endpoint management OpenAPI](https://app.swaggerhub.com/apis/Check-Point/web-mgmt-external-api-production) specifications.

With the CLI, you do not have to manage log in, send keep alive requests, worry about session expiration or pull long processing jobs.

---
🚧🚧🚧

**Note that the CLI is in Early Availability (EA). Use with caution, as it may undergo changes and improvements. Feedback and contributions are highly encouraged.**

To report a bug, please go to [Report Bug](#-report-bug)

For feedback, please get in touch with us at [Check Point Software Technologies Ltd.](mailto:harmony-endpoint-external-api@checkpoint.com)

🚧🚧🚧

---

## ⬇️ CLI Download

To start using this CLI, install it via PIP (PyPi registry) as a global python command
```bash 
pip install chkp-harmony-endpoint-management-cli
```

## 🚀 Getting started

First of all, need to create CloudInfra API credentials, to obtain it, open the Infinity Portal and create a suitable API Key. Make sure to select `Endpoint` in the `Service` field. For more information, see [Infinity Portal Administration Guide](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/Infinity-Portal-Admin-Guide/Content/Topics-Infinity-Portal/API-Keys.htm?tocpath=Global%20Settings%7C_____7#API_Keys).

Once the Client ID, Secret Key, and Authentication URL are obtained, Harmony Endpoint CLI can be used.

Before starting, run the help command to understand how to pass the operation's parameters and payload with all the available options.
```bash
chkp_harmony_endpoint_management_cli --help
```

All available operations can be shown by the command:
```bash
chkp_harmony_endpoint_management_cli --print-operations
```

The credentials are recommended to be passed to the CLI by the environment variables `CP_CI_CLIENT_ID` `CP_CI_ACCESS_KEY` `CP_CI_GATEWAY`.

But CLI also supports passing by params `--client-id` `--access-key` `--gateway` params.

To call an operation, set `--operation` with value from one of the available operations and pass the herders/query/path/body params if required

For example, the operation `get_all_rules_metadata` requires header for job, so it will look like that:
```bash
chkp_harmony_endpoint_management_cli --operation get_all_rules_metadata --header-params "{ \"x-mgmt-run-as-job\": \"off\"}"
```

In case additional payload can be sent, in this example the rule family by query param: 
```bash
chkp_harmony_endpoint_management_cli --operation get_all_rules_metadata --query-params "{\"ruleFamily\" : \"Threat Prevention\"}" --header-params "{ \"x-mgmt-run-as-job\": \"off\"}"
```

All APIs and the optional/required parameters can be explored in [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/web-mgmt-external-api-production)

### ☁️ Cloud & MSSP services APIs

Harmony Endpoint also provides APIs for MSSP and Cloud service management (relevant to SaaS customers only)


The usage is similar to the management API, just need to change default target by `--target saas`

All available operations can be shown by the command:
```bash
chkp_harmony_endpoint_management_cli --print-operations --target saas
```

For example, the `public_machines_single_status` operation to get service state:
```bash
chkp_harmony_endpoint_management_cli --operation public_machines_single_status --target saas
```

Full API exploration available at [SwaggerHub](https://app.swaggerhub.com/apis/Check-Point/harmony-endpoint-cloud-api-prod)

## 🔍 Troubleshooting and logging

The full version and build info of the SDK is available by `--info` see example:
```bash
chkp_harmony_endpoint_management_cli --info
```
The output should be similar to:
```text
Check Point - Harmony Endpoint Management CLI
    CLI - version: "1.1.0" build: "11905935"
    Cloud SDK - sdk_build:"11902935", sdk_version:"1.1.28", spec:"web-mgmt-external-api-production", spec_version:"1.9.211", released_on:"2024-03-06T17:43:38.616492"
    SaaS SDK - sdk_build:"11902935", sdk_version:"1.1.28", spec:"harmony-endpoint-cloud-api-prod", spec_version:"1.0.665", released_on:"2024-03-06T17:43:38.618196"
```

Harmony Endpoint Management CLI allows to print verbose logs.

There are 3 loggers, for general info, errors and to inspect network.

As default, they will be disabled, to enable logging, pass `--verbose` param with the following value:
```bash
chkp_harmony_endpoint_management_cli --verbos *
```

And for a specific logger set the logger name followed by a command as following:
```bash
chkp_harmony_endpoint_management_cli --verbos info
chkp_harmony_endpoint_management_cli --verbos error
chkp_harmony_endpoint_management_cli --verbos network
```

## 🐞 Report Bug

In case of an issue or a bug found in the CLI, please open an [issue](https://github.com/CheckPointSW/harmony-endpoint-management-cli/issues) or report to us [Check Point Software Technologies Ltd](mailto:harmony-endpoint-external-api@checkpoint.com).

## 🤝 Contributors
- Haim Kastner - [chkp-haimk](https://github.com/chkp-haimk)
- Yuval Pomerchik - [chkp-yuvalpo](https://github.com/chkp-yuvalpo)
