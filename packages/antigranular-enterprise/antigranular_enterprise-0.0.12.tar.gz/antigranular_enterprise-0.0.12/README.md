# Antigranular Enterprise: Secure, Privacy-Preserving Data Science in Jupyter Environments

The `antigranular_enterprise` package is a specialized Jupyter client designed for secure and private interaction with the Antigranular Enterprise platform. It facilitates secure data analysis and model training within a Jupyter notebook environment, emphasizing privacy and data protection. This documentation guides you through installing, configuring, and utilizing the client package to integrate Antigranular Enterprise capabilities directly into your Jupyter notebooks.

## Installation

To integrate Antigranular Enterprise with your Jupyter environment, install the package using pip:

```bash
pip install antigranular_enterprise
```

This command installs the `antigranular_enterprise` package and its necessary dependencies, preparing your Jupyter environment for secure, privacy-preserving data analysis.

## Configuration

### Initial Configuration

The initial setup requires configuring the package to communicate with your Antigranular Enterprise instance. Required configuration parameters include:

- **AGENT Jupyter Server URL**: URL for the Proxy server that routes requests to the Antigranular platform.
- **AGENT Jupyter Server Port**: Port on which Proxy listens.
- **AGENT Console URL**: URL for the Antigranular management console.
- **AGENT Console API Key Parameter**: Name of the parameter used for the API key in requests.

### Creating a Configuration File

Configure your environment by creating a configuration file with the required parameters:

1. Import the package in a Jupyter notebook:

    ```python
    import antigranular_enterprise as ag
    ```

2. Define and write the configuration file using the `write_config` method. Replace placeholder values with those specific to your Antigranular Enterprise setup:

    ```python
    ag.write_config(profile='default', yaml_config="""
    agent_jupyter_url: <Jupyter URL>
    agent_jupyter_port: <Jupyter Port>
    agent_AGENT_CONSOLE_URL: <Console URL>
    agent_console_api_key_param: <Console API Key Parameter>
    """)
    ```

This configuration allows the `antigranular_enterprise` client to correctly route and authenticate requests to your Antigranular instance.

## Client Login

Access the Antigranular Enterprise services by logging in through the Jupyter notebook:

1. Login using your API key:

    ```python
    client = ag.login("<api_key>")
    ```

2. A UI notification or link will prompt you for approval. Upon approval, the session starts, allowing secure interaction with the Antigranular platform.

###  Switching to a Different Profile
Once you have multiple profiles configured, you can switch between them by reading the desired profile's configuration before initiating any operations or sessions. Use the read_config method to load the configuration for a specific profile:

```python
ag.read_config(profile='profile_name')
```

## Features and Usage

The `antigranular_enterprise` Jupyter client package offers a suite of features for data analysis and model training, prioritizing data privacy and security:

- **Session Management**: Easily manage your connection sessions to the Antigranular server.
- **Secure Data Analysis**: Perform data analysis operations within the secure confines of the Antigranular environment.
- **Privacy-Enhanced Machine Learning**: Train machine learning models while adhering to privacy regulations and standards.
- **Jupyter Notebook Integration**: Leverage the `%ag` cell magic for executing secure Python code directly in Jupyter notebooks, facilitating a seamless workflow with Antigranular services.

Refer to the in-package documentation or the Antigranular Enterprise platform for detailed examples and advanced usage instructions.

## Support

For assistance, troubleshooting, or to report issues with the `antigranular_enterprise` Jupyter client package, please reach out to the Antigranular support team or consult the comprehensive documentation provided on the Antigranular Enterprise platform.
