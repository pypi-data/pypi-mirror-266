ROUTER = [
    {
        "router_path": "cloudforet.console_api_v2.interface.rest.api:router",
        "router_options": {
            "prefix": "/console-api/api",
            "tags": ["console-api > api"],
        },
    },
    {
        "router_path": "cloudforet.console_api_v2.interface.rest.auth:router",
        "router_options": {
            "prefix": "/console-api/auth",
            "tags": ["console-api > auth"],
        },
    },
    {
        "router_path": "cloudforet.console_api_v2.interface.rest.extension.service_account.agent:router",
        "router_options": {
            "prefix": "/console-api/extension/service-account/agent",
            "tags": ["console-api > extension > service-account" > "agent"],
        },
    },
    {
        "router_path": "cloudforet.console_api_v2.interface.rest.swagger:router",
    },
    {
        "router_path": "cloudforet.console_api_v2.interface.rest.proxy:router",
    },
]
