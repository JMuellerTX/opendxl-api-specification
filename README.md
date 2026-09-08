# OpenDXL API Specification

The OpenDXL API Specification defines a standard interface description for
applications which connect to the
Data Exchange Layer (DXL) messaging fabric. The specification provides a mechanism for describing the
API for DXL-based solutions, including:

* [Services](https://opendxl.github.io/opendxl-client-python/pydoc/dxlclient.service.html)
  that solutions register with a DXL fabric.
* [Events](https://opendxl.github.io/opendxl-client-python/pydoc/dxlclient.message.html#dxlclient.message.Event)
  that solutions send to a DXL fabric.
* [Requests](https://opendxl.github.io/opendxl-client-python/pydoc/dxlclient.message.html#dxlclient.message.Request)
  which can be made to a service through a DXL fabric (and the
  corresponding [responses](https://opendxl.github.io/opendxl-client-python/pydoc/dxlclient.message.html#dxlclient.message.Response)
  that the service produces).

The OpenDXL API Specification is heavily inspired by the work done in the
[OpenAPI Specification](https://spec.openapis.org/) to describe
[REST APIs](https://en.wikipedia.org/wiki/Representational_state_transfer).
Where possible, schema definitions in the OpenDXL API Specification reuse the
corresponding definitions from the OpenAPI Specification. For example, the
[Schema Object](https://spec.openapis.org/oas/v3.2.0.html#schema-object)
defines the
[payload](https://opendxl.github.io/opendxl-client-python/pydoc/dxlclient.message.html#dxlclient.message.Message.payload)
of a DXL message.

Those definitions came from **Swagger 2.0** until 2026, referenced as
`http://swagger.io/v2/schema.json`. Swagger 2.0 was donated to the Linux
Foundation in 2015 and continued there as the OpenAPI Specification; the URL
stopped resolving somewhere along the way, which left this schema unusable for
validation without anyone noticing. It now points at **OpenAPI 3.2**, and the
dialect moved from JSON Schema draft-04 to **2020-12**, which is what OpenAPI
3.1 and later are built on.

| OpenDXL uses | was (Swagger 2.0) | is (OpenAPI 3.2) |
|---|---|---|
| message payload, `definitions` | `#/definitions/schema` | `#/$defs/schema` |
| `info` | `#/definitions/info` | `#/$defs/info` |
| `externalDocs` | `#/definitions/externalDocs` | `#/$defs/external-documentation` |
| references between documents | `#/definitions/jsonReference` | `#/$defs/reference` |
| `description` | JSON Schema draft-04 meta-schema | defined locally |

`description` is defined in this document rather than borrowed: 2020-12 splits
its meta-schema into vocabularies, so pointing at it would be a reference to
another document's implementation detail rather than to a stable definition.

## Draft Version - 0.1

The draft version of the OpenDXL API Specification is
[OpenDXL API Specification 0.1](versions/0.1.md).

## Schemas

[JSON Schema](https://json-schema.org) documents which can be used for
syntactic validation of an OpenDXL API document reside in the
[schemas](schemas) directory. The schema for the latest specification version
is [here](schemas/v0.1/schema.json).

### Validating a document

```bash
pip install jsonschema pyyaml
python tools/validate.py            # schema, its references, and every example
python tools/validate.py --online   # also: does the vendored OpenAPI schema still
                                    # match the published one?
```

The OpenAPI schema is resolved from `schemas/vendor/`, not over the network. A
validation whose outcome depends on a third-party host is a validation that can
change its mind without anyone editing anything - which is precisely how the
Swagger 2.0 reference rotted unnoticed. `--online` is the deliberate check that
the vendored copy still matches what the OpenAPI Initiative publishes.

This repository used to carry the OpenAPI-Specification repository as a git
submodule under `openapi-spec/`. It has been removed, for three reasons that
compound: the pointer stood at a commit from October 2018 (the OpenAPI 3.0.2
merge), `.gitmodules` tracked `master` while that repository's default branch is
now `main`, and nothing here referenced it. What this project needs from the
OpenAPI Specification is one schema document, which is now in
`schemas/vendor/` with its `$id` intact and checkable with `--online`.

## Examples

Current OpenDXL API document examples include:

* ACME [[json](examples/v0.1/json/acme.json)] [[yaml](examples/v0.1/yaml/acme.yaml)] -
  Simple example which utilizes each of the major schema components to describe
  an API - solutions, services, requests, and events.

## LICENSE

Copyright 2018 McAfee, LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
