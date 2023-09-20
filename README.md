# GQL prompt

This little project servers as a quick introspection tool into a GQL schema.

## Usage

`poetry run python3 main.py my_schema.graphql`

Inside the prompt, you can write:

- `.types` to list all types in the schema
- `.queries` to list all queries
- `.mutations` to list all mutations
- Any type/query/mutation name to display its fields, args, returns values
- `_` to print the return type of a method you previously displayed
