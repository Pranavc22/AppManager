.
├── LICENSE
├── README.md
├── database.py
├── main.py
├── rbac.db
├── requirements.txt
├── services
│   ├── bug_rca
│   │   ├── __init__.py
│   │   ├── agents
│   │   │   ├── __init__.py
│   │   │   └── agent1
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── prompt.py
│   │   │       └── tools.py
│   │   ├── config.py
│   │   ├── data
│   │   │   ├── scenario_10_cache_issues.json
│   │   │   ├── scenario_11_network_partition.json
│   │   │   ├── scenario_12_cpu_throttling.json
│   │   │   ├── scenario_13_disk_full.json
│   │   │   ├── scenario_14_ssl_cert_expired.json
│   │   │   ├── scenario_15_deadlock.json
│   │   │   ├── scenario_1_null_pointer.json
│   │   │   ├── scenario_2_database_cascade.json
│   │   │   ├── scenario_3_auth_failures.json
│   │   │   ├── scenario_4_timeout_errors.json
│   │   │   ├── scenario_5_memory_issues.json
│   │   │   ├── scenario_6_rate_limiting.json
│   │   │   ├── scenario_7_file_errors.json
│   │   │   ├── scenario_8_validation_errors.json
│   │   │   └── scenario_9_external_services.json
│   │   ├── graph.py
│   │   ├── integration.py
│   │   ├── quick_test.py
│   │   ├── router.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   └── base_schema.py
│   │   ├── test_agent.py
│   │   └── test_rca.py
│   ├── incident_triage
│   │   ├── agents
│   │   │   └── agent1
│   │   │       ├── main.py
│   │   │       ├── prompt.py
│   │   │       └── tools.py
│   │   ├── data
│   │   ├── graph.py
│   │   ├── router.py
│   │   └── schemas
│   │       └── base_schema.py
│   └── user_access
│       ├── agents
│       │   └── user_access_manager
│       │       ├── main.py
│       │       └── prompt.py
│       ├── data
│       │   ├── access_decisions.csv
│       │   ├── access_requests.csv
│       │   ├── permissions.csv
│       │   ├── resources.csv
│       │   ├── role_permissions.csv
│       │   ├── roles.csv
│       │   ├── studies.csv
│       │   ├── user_roles.csv
│       │   └── users.csv
│       ├── router.py
│       ├── schemas
│       │   └── base_schema.py
│       └── utils
│           ├── data_init.py
│           └── query.py
└── utils
    ├── llm.py
    └── llm_exp.py