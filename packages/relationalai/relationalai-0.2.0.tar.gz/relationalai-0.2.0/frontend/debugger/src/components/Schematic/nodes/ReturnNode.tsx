import * as Mech from "@src/types/mech";
import { NodeBase, NodeProps, NodeIcon } from "./base";
import { useScope } from "../ScopeProvider";
import { For } from "solid-js";

export function ReturnNode(props: NodeProps<Mech.Node.Return>) {
    const scope = useScope()?.();
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type={props.node.merge_result ? "merge_result" : props.node.type} />
            <section>
                <For each={props.node.values}>
                    {(arg) => <span class="arg">{scope?.name(arg)}</span>}
                </For>
            </section>
        </NodeBase>
    );
}
