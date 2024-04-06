# Code Generation

[JSON Schemas](https://github.com/charbonnierg/pytest-broadcaster/blob/main/schemas) are provided for the data models.

They can be used to generate code in various languages:

=== "Python Dataclasses"

    It' possible to generate Python [dataclasses][dataclasses.dataclass] from the JSON Schemas using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

    1. First clone the repository:

    <!-- termynal -->

    ```
    $ git clone https://github.com/charbonnierg/pytest-broadcaster
    $ cd pytest-broadcaster
    ```

    2. Then install [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

    <!-- termynal -->

    ```
    $ pip install --user datamodel-code-generator
    ```

    3. Then generate the code:

    <!-- termynal -->

    ```
    $ datamodel-codegen \
        --input docs/schemas/ \
        --output models/ \
        --input-file-type jsonschema \
        --disable-timestamp \
        --output-model-type=dataclasses.dataclass \
        --use-field-description \
        --use-schema-description
    ```

    The generated code will be in the `models` directory.

=== "Python Pydantic (v2)"

    It' possible to generate [Pydantic](https://docs.pydantic.dev/latest/) [BaseModel][pydantic.BaseModel] classes from the JSON Schemas using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

    1. First clone the repository:

    <!-- termynal -->

    ```
    $ git clone https://github.com/charbonnierg/pytest-broadcaster
    $ cd pytest-broadcaster
    ```

    2. Then install [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

    <!-- termynal -->

    ```
    $ pip install --user datamodel-code-generator
    ```

    3. Then generate the code:

    <!-- termynal -->

    ```
    $ datamodel-codegen \
        --input docs/schemas/ \
        --output models/ \
        --input-file-type jsonschema \
        --disable-timestamp \
        --output-model-type=pydantic_v2.BaseModel \
        --use-field-description \
        --use-schema-description
    ```

    The generated code will be in the `models` directory.

=== "Python Pydantic (v1)"

    It' possible to generate [Pydantic](https://docs.pydantic.dev/1.10/) [BaseModel](https://docs.pydantic.dev/1.10/usage/models/#basic-model-usage) classes from the JSON Schemas using [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

    1. First clone the repository:

    <!-- termynal -->

    ```
    $ git clone https://github.com/charbonnierg/pytest-broadcaster
    cd pytest-broadcaster
    ```

    2. Then install [`datamodel-code-generator`](https://github.com/koxudaxi/datamodel-code-generator):

    <!-- termynal -->

    ```
    $ pip install --user datamodel-code-generator
    ```

    3. Then generate the code:

    <!-- termynal -->

    ```
    $ datamodel-codegen \
        --input docs/schemas/ \
        --output models/ \
        --input-file-type jsonschema \
        --disable-timestamp \
        --output-model-type=pydantic_v1.BaseModel \
        --use-field-description \
        --use-schema-description
    ```

    The generated code will be in the `models/` directory.


=== "Typescript `.d.ts`"

    It's possible to generate `.d.ts` files for [Typescript](https://www.typescriptlang.org/) using [`json-schema-to-typescript`](https://github.com/bcherny/json-schema-to-typescript):

    1. First clone the repository:

    <!-- termynal -->

    ```
    $ git clone https://github.com/charbonnierg/pytest-broadcaster
    cd pytest-broadcaster
    ```

    2. Then install `json-schema-to-typescript`:

    <!-- termynal -->

    ```
    $ npm install -g json-schema-to-typescript
    ```

    3. Then generate the code:

    <!-- termynal -->

    ```
    $ json2ts -i docs/schemas/ -o types/
    ```

    The generated code will be in the `types/` directory.
