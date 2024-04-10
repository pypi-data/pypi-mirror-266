//------------------------------------------------------------------------------
// Interfaces for Mechanical diagram components emitted from analyzer
//------------------------------------------------------------------------------

export interface Block {
    task: string,
    name: string,
    code?: string|null,
    err?: string|null,
    mech: Machine
}

export interface Machine {
    id: number,
    type: string,
    items: Node[]
}

export interface Var {
    id: number,
    name: string
}

export type Constant = string&{id?:undefined}; // |number|boolean; they're double json-ified for some reason

export type Value = Var|Constant;

export interface Bindings {
    [name: string]: Value
}

export namespace Node {
    interface Base {
        id: string,
        type: string
    }

    // Actions -----------------------------------------------------------------

    export interface Get extends Base {
        type: "get",
        entity: Var,
        types: string[],
        props: Bindings
    }

    export interface Filter extends Base {
        type: "filter",
        op: string,
        args: Value[]
        ret?: undefined
    }

    export interface Compute extends Base {
        type: "compute",
        op: string,
        args: Var[],
        ret: Value // @FIXME There can be multiple of these though...
    }

    export interface Effect extends Base {
        type: "effect",
        op: string,
        entity: Var,
        types: string[],
        props: Bindings
    }

    export interface Return extends Base {
        type: "return",
        values: Value[],
        merge_result?: boolean
    }

    export interface Install extends Base {
        type: "install",
        item: Var
    }

    export interface Aggregate extends Base {
        type: "aggregate",
        op: string,
        args: Value[],
        group: Value[],
        ret: Value // @FIXME There can be multiple of these though...
    }

    type Quantifier = string;
    export interface Quantify extends Base {
        type: "quantify",
        quantifier: Quantifier,
        group: Value[]
    }

    export type Action =
        | Get
        | Filter
        | Compute
        | Effect
        | Return
        | Install
        | Aggregate
        | Quantify

    // Containers --------------------------------------------------------------

    interface ContainerBase extends Base {
        items: Node[]
    }

    export interface Sequence extends ContainerBase {
        type: "sequence"
    }

    export interface Union extends ContainerBase {
        type: "union",
        result: Value
    }

    export interface Choice extends ContainerBase {
        type: "choice"
    }

    export type Container = Sequence | Union | Choice;
}
export type Node = Node.Action | Node.Container
export type NodeType = Node["type"]
