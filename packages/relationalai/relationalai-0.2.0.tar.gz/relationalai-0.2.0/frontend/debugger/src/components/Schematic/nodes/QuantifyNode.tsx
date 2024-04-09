import * as Mech from "@src/types/mech";
import { NodeBase, NodeProps, NodeIcon } from "./base";
import { useScope } from "../ScopeProvider";
import { For } from "solid-js";

export function QuantifyNode(props: NodeProps<Mech.Node.Quantify>) {
    const scope = useScope()?.();
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type={props.node.quantifier} />
            <section>
                <For each={props.node.group}>
                    {(arg) => <span class="arg">{scope?.name(arg)}</span>}
                </For>
            </section>
        </NodeBase>
    );
}
