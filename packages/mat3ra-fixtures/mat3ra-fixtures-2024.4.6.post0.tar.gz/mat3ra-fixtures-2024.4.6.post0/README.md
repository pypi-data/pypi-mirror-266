# Fixtures

A dual repository (JavaScript and Python) containing basic utils for development.

Minimum external dependencies should be used in order to keep the repository lightweight.

## 1. Overview

This repository contains the fixtures for the common applications, formats, databases that contain data.

## 2. Usage

### 2.1. Python

See example [test](tests/py/unit/test_get_from_manifest.py).

The files can be directly accessed through the filesystem, otherwise the content can be extracted by (a shortened) reference ("object path") from the top-level [manifest.yml](src/py/mat3ra/fixtures/manifest.yml).

```py
from mat3ra.fixtures import get_content_by_reference_path

PATH_IN_MANIFEST = "applications/espresso/v5.4.0/stdin"

content = get_content_by_reference_path(PATH_IN_MANIFEST)
print(content)
```

### 2.2. JavaScript/TypeScript

To be added. Only servier-side (Node.js) runtime to be supported due to having to rely on the filesystem.

## 3. Development

### 3.1. Folder Structure

Here's the folder structure of the repository:

```txt
data
├── applications
│   └── espresso
│       └── 5.4.0
│           ├── case-001
│           ├── case-002
│           ├── case-003
│           └── manifest.yml
├── db
└── formats
```

For each version of the application, there are multiple cases. Each case contains the data that is used for testing.  The manifest file is a YAML file that contains the metadata about all the cases.
