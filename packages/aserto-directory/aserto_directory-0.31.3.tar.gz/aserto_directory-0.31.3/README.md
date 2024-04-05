# Aserto Directory gRPC client
This is an automatically generated client for interacting with Aserto's
[Directory service](https://docs.aserto.com/docs/overview/directory) using the gRPC protocol.

## Installation
### Using Pip
```sh
pip install aserto-directory
```
### Using Poetry
```sh
poetry add aserto-directory
```
## Usage
```py
import grpc
from aserto.directory.reader.v2 import ReaderStub, GetObjectTypesRequest

with grpc.secure_channel(
    target="directory.prod.aserto.com:8443",
    credentials=grpc.ssl_channel_credentials(),
) as channel:
    reader = ReaderStub(channel)

    # List all object types in the directory
    response = reader.GetObjectTypes(
        GetObjectTypesRequest(),
        metadata=(
            ("authorization", f"basic {ASERTO_DIRECTORY_API_KEY}"),
            ("aserto-tenant-id", ASERTO_TENANT_ID),
        ),
    )

    for object_type in response.results:
        print("Object Type:", object_type.name)
