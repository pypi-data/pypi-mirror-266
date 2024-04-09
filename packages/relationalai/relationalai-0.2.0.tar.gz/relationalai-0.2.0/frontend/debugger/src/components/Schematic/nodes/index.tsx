import { Dynamic } from "solid-js/web";
import * as Mech from "@src/types/mech";

import {GetNode} from "./GetNode";
import {FilterNode} from "./FilterNode";
import {ComputeNode} from "./ComputeNode";
import {EffectNode} from "./EffectNode";
import {ReturnNode} from "./ReturnNode";

import {UnknownNode} from "./UnknownNode";
import {SequenceNode} from "./SequenceNode";
import {UnionNode} from "./UnionNode";
import { QuantifyNode } from "./QuantifyNode";

// Actions
export * from "./GetNode";
export * from "./FilterNode";
export * from "./ComputeNode";
export * from "./EffectNode";
export * from "./ReturnNode";
export * from "./UnknownNode";

// Containers
export * from "./SequenceNode";
export * from "./UnionNode";

export {NodeIcon, DummyNode} from "./base";



const NODES = {
    // actions
    "get": GetNode,
    "filter": FilterNode,
    "compute": ComputeNode,
    "effect": EffectNode,
    "return": ReturnNode,

    "install": UnknownNode,
    "aggregate": UnknownNode,
    "quantify": QuantifyNode,

    "sequence": SequenceNode,
    "union": UnionNode,
    "choice": UnknownNode,
}

interface NodeProps {
    node: Mech.Node,
    ix: number,
    flipped?: boolean,
}

export function Node(props: NodeProps) {
    const component = () => NODES[props.node.type] ?? UnknownNode;
    return <Dynamic component={component()} node={props.node} ix={props.ix} flipped={props.flipped} />
}
