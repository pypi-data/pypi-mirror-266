 <h1><a href="https://github.com/cslab/functions-sdk"><img src="https://www.contact-software.com/design/img/logo-icon.svg" width="50" alt="CONTACT Logo"></a> Functions-Client</h1>

This CLI tool is used for uploading and managing Functions in CIM Database Cloud.

Information on how build Functions can be found in the Functions-SDK documentation: https://cslab.github.io/functions-sdk-python/

## Requirements

Python 3.10+

## Installation

```console
$ pip install contactsoftware-functions-client
```

## Login
Before you can create environments or deploy Functions you need to login using your client-id and secret. Obtain your client credentials via the CONTACT Portal.

```console
$ cfc login --client-id <client_id> --client-secret <client_secret>
```

The credentials will be stored in a configuration file. The storage location of the configuration file depends on the OS:

- Windows: `C:\Users\<username>\AppData\Local\Contact\cfc\config.ini`
- Linux: `~/.config/cfc/config.ini`


## Features
### Manage Function environments
Functions are grouped into **environments**, which are the (Docker) container the code runs in. An environment contains a runtime for its specific programming language, the Function code and a configuration file describing the environment.

Create a new environment:

```console
$ cfc env create <environment_name>
```

Display a list of all environments:

```console
$ cfc env list
```

Display the details of an environment:

```console
$ cfc env describe <environment_name>
```


### Deploy Function code into an environment
To deploy Function code into an existing environment run:

```
$ cfc env deploy <environment_name>
```

Make sure you run the command from within the directory that contains the `environment.yaml` configuration file.

Information on how to build Function code can be found in the documentation of the Functions-SDK: https://cslab.github.io/functions-sdk-python/
