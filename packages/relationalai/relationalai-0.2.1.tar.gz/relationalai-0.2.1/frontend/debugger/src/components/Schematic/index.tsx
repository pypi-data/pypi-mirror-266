import { For, JSXElement, Match, Show, Switch } from "solid-js"
import * as Mech from "@src/types/mech";

import "./index.styl";
import { ScopeProvider } from "./ScopeProvider";
import {Node} from "./nodes";
import { DummyNode, NodeIcon } from "./nodes/base";

//------------------------------------------------------------------------------
// Schematic
//------------------------------------------------------------------------------

interface SchematicProps {
    block: Mech.Block
}
export function Schematic(props: SchematicProps) {
    return <Machine machine={props.block.mech} />
}

//------------------------------------------------------------------------------
// Machine
//------------------------------------------------------------------------------

interface MachineProps {
    machine: Mech.Machine
}
export function Machine(props: MachineProps) {
    return (
        <schematic-machine>
            <ScopeProvider machine={props.machine}>
            <Rail items={props.machine.items} />
            </ScopeProvider>
        </schematic-machine>
    )
}

//------------------------------------------------------------------------------
// Rail
//------------------------------------------------------------------------------

interface RailProps {
    items: Mech.Node[],
    nested?: boolean,
    flipped?: boolean,
    in?: boolean,
    out?: boolean,
    children?: JSXElement
}
export function Rail(props: RailProps) {
    const should_merge = () => props.nested && props.items[props.items.length - 1].type == "quantify";
    const end_row = () => (props.items.length + (should_merge() ? 1 : 0)) * 3;
    return (
        <schematic-rail classList={{ nested: props.nested, flipped: props.flipped, in: props.in, out: props.out, merge: should_merge() }}>
            <schematic-rail-line style={`--end-row: ${end_row()}`} />
            <For each={props.items}>
                {(item, ix) => (
                    <Node node={item} ix={ix()} flipped={props.flipped} />
                )}
            </For>
            <Show when={should_merge()}>
                <DummyNode type="dummy" ix={props.items.length}>
                    <NodeIcon type="merge" />
                </DummyNode>
            </Show>
            {props.children}
        </schematic-rail>
    )
}
