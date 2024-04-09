import * as Mech from "@src/types/mech";
import { Component, JSXElement } from "solid-js";
import "./base.styl";
import { Dynamic } from "solid-js/web";

//------------------------------------------------------------------------------
// Constants
//------------------------------------------------------------------------------

export const LONG_SECTION_THRESHOLD = 120;

export const INFIX_OPS = new Set([
    ">",
    "<",
    ">=",
    "<=",
    "==",
    "+",
    "-",
    "*",
    "/"
]);

export interface NodeBaseProps<T extends Mech.Node = Mech.Node> {
    node: T,
    ix: number,
    children: JSXElement
}
export function NodeBase(props: NodeBaseProps) {
    return (
        <schematic-node class={props.node.type} style={`grid-row: ${1 + props.ix * 3} / span 3`}>
            {props.children}
        </schematic-node>
    )
}

interface DummyNodeProps {
    type: string,
    ix: number,
    children?: JSXElement
}
export function DummyNode(props: DummyNodeProps) {
    return (
        <schematic-node class={props.type} style={`grid-row: ${1 + props.ix * 3} / span 3`}>
            {props.children}
        </schematic-node>
    )
}


export interface NodeProps<T extends Mech.Node = Mech.Node> {
    node: T,
    ix: number,
    flipped?: boolean
}

//------------------------------------------------------------------------------
// Node Icons
//------------------------------------------------------------------------------

export function GetIconContent() {
    return <>
        <circle class="filled" cx={0} cy={0} r={32} />
    </>
}

export function FilterIconContent() {
    return <>
        <line class="tick" x1={0} x2={32} y1={0} y2={0} />
    </>
}

export function ComputeIconContent() {
    return <>
        <circle class="outline cutout" cx={0} cy={0} r={32} />
        <circle class="outline" cx={0} cy={0} r={32} />
        <circle class="filled" cx={0} cy={0} r={16} />
    </>
}

export function EffectIconContent() {
    return <>
        <line class="tick cutout" y1={0} y2={0} x1={-32} x2={32} />
        <line class="tick cutout" x1={0} x2={0} y1={-32} y2={32} />

        <line class="tick plus h" y1={0} y2={0} x1={-32} x2={32} />
        <line class="tick plus v" x1={0} x2={0} y1={-32} y2={32} />
    </>
}

export function ReturnIconContent() {
    return <>
        <polygon class="cutout" points="-32,0 32,32 32,-32" />

        <line class="tick cutout" x1={-32} x2={32} y1={0} y2={32} />
        <line class="tick cutout" x1={-32} x2={32} y1={0} y2={-32} />

        <line class="tick" x1={-32} x2={32} y1={0} y2={32} />
        <line class="tick" x1={-32} x2={32} y1={0} y2={-32} />
    </>
}

export function NotIconContent() {
    return <>
        <line class="tick cutout" x1={-32} y1={-32} x2={32} y2={32} />
        <circle class="outline cutout" cx={0} cy={0} r={32} />
        <circle class="outline" cx={0} cy={0} r={32} />

        <line class="tick" x1={-32} y1={-32} x2={32} y2={32} />
    </>
}

export function BranchIconContent() {
    return <>
        <line class="tick" x1={0} x2={88} y1={0} y2={0} />
    </>
}

export function MergeIconContent() {
    return <>
        <line class="tick" x1={0} x2={-88} y1={0} y2={0} />
    </>
}

export function QuantMergeIconContent() {
    return <>
        <line class="tick" x1={0} x2={-64} y1={0} y2={0} />
        <line class="tick square" x1={-48} x2={-68} y1={0} y2={0} />

        <line class="bridge-last square" x1={-68} x2={-112} y1={0} y2={0} />

        <line class="tick square" x1={-112} x2={-132} y1={0} y2={0} />
        <line class="tick" x1={-116} x2={-176} y1={0} y2={0} />

        <circle class="outline" cx={-179} cy={0} r={16} />

        <polygon class="tick cutout" points="20,-20 -20,0 20,20" />
        <polygon class="tick filled" points="16,-16 -16,0 16,16" />
    </>
}

export function DownIconContent() {
    return <>
        <polygon class="tick cutout" points="-32,-32 32,-32 0,32" />
        <polygon class="tick filled" points="-28,-28 28,-28 0,28" />
    </>
}

export function LeftIconContent() {
    return <>
        <polygon class="tick cutout" points="32,-32 -32,0 32,32" />
        <polygon class="tick filled" points="28,-28 -28,0 28,28" />
    </>
}

export function RightIconContent() {
    return <>
        <line class="tick" x1={-12} x2={-12} y1={0} y2={-64} />
        <line class="tick" x1={12} x2={12} y1={0} y2={-64} />

        <polygon class="tick cutout" points="-32,-32 32,0 -32,32" />
        <polygon class="tick filled" points="-28,-28 28,0 -28,28" />
    </>
}


export const node_icons: Record<string, Component | undefined> = {
    "get": GetIconContent,
    "filter": FilterIconContent,
    "compute": ComputeIconContent,
    "effect": EffectIconContent,
    "return": ReturnIconContent,

    "not": NotIconContent,

    "branch": BranchIconContent,
    "merge": MergeIconContent,
    "merge_result": QuantMergeIconContent,

    "union": RightIconContent,
}


interface NodeIconProps {
    type: string
    class?: string
}
export function NodeIcon(props: NodeIconProps) {
    const component = () => node_icons[props.type]
    return (
        <svg class={`schematic-node-icon ${props.type} ${props.class ?? ""}`} viewBox="-32 -32 64 64" vector-effect="non-scaling-stroke">
            <Dynamic component={component()} />
        </svg>
    )
}
