Fetching Key Vault secrets
==========================

To abstract secrets fetching from keyvault,
:class:`pfore-cloud-utilities.DatabricksWorkspace` was implemented,
you can directly use :func:`get_workspace_secret_value`
to securely retrieve secrets.

This requires provisioning a Databricks Secret Scope mirroring an Azure Keyvault
Scope, which is out-of-scope of this documentation and assumed to be
implemented for you by your organisation, so you'll only have to specify the
scope's name when retrieving the secret.

To list the existing scopes within a workspace, use
`databricks secrets list-scopes`, output will look like

.. code-block:: bash

    databricks secrets list-scopes --profile=<profile>

          Scope                Backend             KeyVault URL
    -------------------  -------------------   ---------------------
    <secret-scope-name>  <key-vault-backend>      <key-vault-url>


For the `databricks secrets` CLI command as well as the
:func:`get_workspace_secret_value` function to work, a connection to the
host needs to be set up, which is explained in the following section.

If there are no secret scopes provisioned by you organisation, follow the
`official tutorial`_ for setting up the secret scope.

.. _official tutorial: https://learn.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes

To set up a connection to a Databricks workspace, simply create a
:file:`.databrickscfg` file under your home directory. The file contains
information on the workspaces you'd like to connect to.

Example of how the file is structured for three workspaces, dev, qas and prod
is shown below.

.. code-block:: cfg

    [dev]
    host = <databricks-host-url, starts with https://>
    token = <your databricks personal access token>

    [qas]
    host = <databricks-host-url, starts with https://>
    token = <your databricks personal access token>

    [prod]
    host = <databricks-host-url, starts with https://>
    token = <your databricks personal access token>

Once the configuration file is set up, you can call the helper class method
to fetch the secrets present in your keyvault. Example is shown in the
code below.

.. code-block:: python

    from pfore_cloud_utilities import get_workspace_secret_value

    azure_spn_client_id = get_workspace_secret_value(
            secret_key='<secret-name-on-azure-key-vault>',
            workspace='dev',
            scope='<secret-scope>',
        )
