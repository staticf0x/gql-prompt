import argparse
from dataclasses import dataclass

from graphql import build_ast_schema, parse
from graphql.type import GraphQLList
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter
from rich import print as rprint

parser = argparse.ArgumentParser()
parser.add_argument("schema", type=str, help="Path to the .graphql schema")

args = parser.parse_args()

with open(args.schema) as fread:
    type_def_ast = parse(fread.read())
    schema = build_ast_schema(type_def_ast)


@dataclass
class Field:
    name: str
    type_: type

    def __str__(self) -> str:
        if isinstance(self.type_, GraphQLList):
            field_type = f"[[i]{self.type_.of_type.name}[/i]]"
        else:
            field_type = f"[i]{self.type_.name}[/i]"

        return f"[b]{self.name}[/b]: {field_type}"

    def __lt__(self, other):
        return self.name < other.name


@dataclass
class Arg:
    name: str
    type_: type

    def __str__(self):
        if isinstance(self.type_.type, GraphQLList):
            field_type = f"[[i]{self.type_.type.of_type.name}[/i]]"
        else:
            field_type = f"[i]{self.type_.type.name}[/i]"

        return f"[b]{self.name}[/b]: {field_type}"


@dataclass
class GQLType:
    type_: type
    fields: list[Field]

    def __init__(self, type_):
        self.type_ = type_
        self.fields = [
            Field(field_name, field.type) for field_name, field in type_.fields.items()
        ]


@dataclass
class GQLMethod:
    name: str
    returns: str
    args: list[Arg]

    def __init__(self, name, gql_type):
        self.returns = gql_type.type.name
        self.args = [Arg(name, type_) for name, type_ in gql_type.args.items()]


choices = [
    *schema.type_map.keys(),
    *schema.query_type.fields.keys(),
    *schema.mutation_type.fields.keys(),
    *[".types", ".queries", ".mutations"],
]
completer = FuzzyWordCompleter(choices)
session = PromptSession()

while True:
    try:
        answer = session.prompt("> ", completer=completer)
    except (EOFError, KeyboardInterrupt):
        break

    if answer in schema.type_map:
        type_ = schema.type_map[answer]
        obj = GQLType(type_)

        for field in sorted(obj.fields):
            rprint(str(field))
    elif answer in schema.query_type.fields:
        method = schema.query_type.fields[answer]
        obj = GQLMethod(answer, method)

        rprint(f"[b]{answer}[/b] (")
        for arg in obj.args:
            rprint(f"  {str(arg)}")

        rprint(f") -> [i]{obj.returns}[/i]")
    elif answer in schema.mutation_type.fields:
        method = schema.mutation_type.fields[answer]
        obj = GQLMethod(answer, method)

        rprint(f"[b]{answer}[/b] (")
        for arg in obj.args:
            rprint(f"  {str(arg)}")

        rprint(f") -> [i]{obj.returns}[/i]")
    elif answer == ".types":
        for type_ in sorted(schema.type_map):
            rprint(f"[b]{type_}[/b]")
    elif answer == ".queries":
        for method in sorted(schema.query_type.fields):
            rprint(f"[b]{method}[/b]")
    elif answer == ".mutations":
        for method in sorted(schema.mutation_type.fields):
            rprint(f"[b]{method}[/b]")
