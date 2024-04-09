from relationalai import metamodel as mm
from gentest.gen.context import GenContextBuilder

def person_place_thing(builder: GenContextBuilder):
    std = mm.Builtins
    place = builder.type("Place", [
        mm.Property("address", std.String),
        mm.Property("zip", std.Int),
        mm.Property("lat", std.Decimal),
        mm.Property("lng", std.Decimal),
    ])
    thing = builder.type("Thing", [
        mm.Property("name", std.String),
        mm.Property("at", place),
    ])
    person = builder.type("Person", [
        mm.Property("name", std.String),
        mm.Property("age", std.Number),
        mm.Property("height", std.Number),
        mm.Property("home", place),
        mm.Property("owns", thing),
    ])
    person.properties.append(mm.Property("friends", person))
