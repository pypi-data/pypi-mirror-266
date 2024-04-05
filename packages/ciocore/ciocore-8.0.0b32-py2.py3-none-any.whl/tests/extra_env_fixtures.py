

EXTRA_ENV = [
    {
      "account_id": "6649535867387904",
      "env": [],
    },
    {
      "account_id": "5767615549800448",
      "env": [
        {
          "merge_policy": "prepend",
          "name": "test",
          "value": "test"
        }
      ],
    },
    {
      "account_id": "6649535867387904",
      "env": [],
    },
    {
      "account_id": "5669544198668288",
      "env": [
        {
          "merge_policy": "append",
          "name": "PATH",
          "value": "/path/to/scripts"
        },
        {
          "merge_policy": "exclusive",
          "name": "RENDER_LOCATION",
          "value": "cloud"
        },
        {
          "merge_policy": "exclusive",
          "name": "VARIABLE_USED_IN_SCRIPTS",
          "value": "true"
        },
        {
          "merge_policy": "exclusive",
          "name": "testvar",
          "value": "somevalue"
        }
      ],
    },
    {
      "account_id": "6649535867387904",
      "env": [
        {
          "merge_policy": "exclusive",
          "name": "JMEYER",
          "value": "JMEYER_ENV_VALUE"
        }
      ],
    }
  ]