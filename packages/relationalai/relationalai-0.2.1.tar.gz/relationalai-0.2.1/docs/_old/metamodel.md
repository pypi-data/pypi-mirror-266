## V2

```typescript

//-------------------------------------------------
// Public Types - Data
//-------------------------------------------------

export interface Type {
    kind: "type"
    id: number,
    name: string,
    agent: Agent,
    properties: Property[],
    parents: Type[],
}

export interface Property {
    kind: "property"
    id: number,
    name: string,
    type: Type,
    is_input: boolean,
}

export interface Agent {
    kind: "agent"
    id: number,
    name: string,
    platform: string, // SQL, Rel, JS, OpenAI, etc
    info: any,
}

//-------------------------------------------------
// Public Types - Tasks
//-------------------------------------------------

export interface Task extends Type {
    kind: "task",
    behavior: "query"|"union"|"ordered_choice"|"sequence"|"catch"
    items: Action[],
    bindings: Record<Property, Var>
    inline?: boolean,
}

type Value = string|number|boolean|Task|Type|Property|(Value|Var)[];

export interface Var {
    kind: "var",
    id: number,
    type:Type,
    name?:string,
    value?:Value,
}

export interface Action {
    kind: "action",
    action: "get"|"call"|"bind"|"persist"|"unpersist"|"construct"
    entity: Var,
    types: Type[],
    bindings: Record<Property, Var>
}

export type AllNodes = Type|Property|Agent|Var|Task|Action;

//-------------------------------------------------
// Semantic Builtins
//-------------------------------------------------

const Types = [
    Type("Unknown"),
    Type("Any"),
    Type("String"),
    Type("Number"),
    Type("RawData"),
    Type("Quantifier"),
    Type("Aggregate"),
]

const Tasks = [
    Task("not", "query", [
        Property("group", Var[]),
        Property("task", Task)
    ], parents=[Types.Quantifier])
    Task("every", "query", [
        Property("group", Var[]),
        Property("task", Task)
    ], parents=[Types.Quantifier])
    Task("raw", "query", [
        Property("code", string),
        Property("inputs", Var[]),
        Property("outputs", Var[])
    ]),
    Task("return", "query", [
        Property("r1", Any),
        Property("r2", Any),
        Property("r3", Any),
        ...
    ])
]
```

## V1

```typescript

//-------------------------------------------------
// Public Types - Data
//-------------------------------------------------

export interface Type {
    kind: "type"
    id: number,
    name: string,
    agent: Agent,
    properties: Property[],
    parents: Type[],
}

export interface Property {
    kind: "property"
    id: number,
    name: string,
    type: Type,
    is_input: boolean,
}

export interface Agent {
    kind: "agent"
    id: number,
    name: string,
    platform: string, // SQL, Rel, JS, OpenAI, etc
    info: any,
}

//-------------------------------------------------
// Public Types - Tasks
//-------------------------------------------------

export interface Task {
    kind: "task",
    id: number,
    type: "query"|"concurrent"|"ordered_choice"|"sequential"|"catch"
    properties: Property[],
    items: TaskItem[],
    agent: Agent
    isolated_effects?: boolean,
    parent?: Task,
    name?: string,
    inline?: boolean,
    quantifier: "not"|"some"|"every"
}

export type TaskItem = Task|Action|Raw|Transition;

export interface Var {
    kind: "var",
    id: number,
    type:Type,
    name?:string,
    value?:string|number|boolean,
}

export interface ActionPart {
    parent: Action,
    item: Type|Property|Task|Agent|Var,
    var: Var,
}

export interface Action {
    kind: "action",
    id: number,
    action: "get"|"call"|"persist"|"unpersist"|"bind"|"install"|"uninstall"|"return",
    parts: ActionPart[],
}

export interface Raw {
    kind: "raw",
    id: number,
    value: string,
    inputs: Var[],
    outputs: Var[],
    agent: Agent,
}

export interface Transition {
    kind: "transition",
    id: number,
    to: TaskItem,
}

export type AllNodes = Type|Property|Agent|Var|TaskItem|Transition;




```
