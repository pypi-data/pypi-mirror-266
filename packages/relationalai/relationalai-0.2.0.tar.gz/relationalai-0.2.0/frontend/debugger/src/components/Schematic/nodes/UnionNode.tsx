import { For, createComputed } from "solid-js";
import * as Mech from "@src/types/mech";
import { useScope } from "../ScopeProvider";
import { NodeBase, NodeProps, NodeIcon, DummyNode } from "./base";
import {Node} from ".";
import { Rail } from "..";

export function UnionNode(props: NodeProps<Mech.Node.Union>) {
    const scope = useScope()?.();
    createComputed(() => {
        for (let seq of props.node.items) {
            if("items" in seq) {
                let last_node = seq.items[seq.items.length - 1];
                if(last_node.type === "return") {
                    last_node.merge_result = true;
                }
            }
        }
    })
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type="branch" />
            <Rail items={props.node.items} nested out>
                <DummyNode type="spacer" ix={props.node.items.length} />
            </Rail>
            <node-gap>
                <schematic-rail-line />
                <NodeIcon type="union" class="bottom" />
                <section>
                    <span>{scope?.name(props.node.result)}</span>
                </section>
            </node-gap>
        </NodeBase>
    );
}

/* interface UnionRailProps {
*     items: Mech.Node[],
* }
* export function UnionRail(props: UnionRailProps) {
*     return (
*         <schematic-rail classList={{ nested: true, flipped: true, in: true }}>
*             <schematic-rail-line style={`--start-row: 2; --end-row: ${props.items.length * 3}`} />
*             <For each={props.items}>
*                 {(item, ix) => (
*                     <Node node={item} ix={ix()} flipped />
*                 )}
*             </For>
*         </schematic-rail>
*     )
* } */
