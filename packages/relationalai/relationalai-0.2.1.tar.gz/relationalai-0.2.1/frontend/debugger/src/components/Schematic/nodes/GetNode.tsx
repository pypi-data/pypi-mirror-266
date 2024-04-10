import { For, Show } from "solid-js";
import * as Mech from "@src/types/mech";
import { useScope } from "../ScopeProvider";
import { NodeProps, NodeIcon, NodeBase } from "./base";

export function GetNode(props: NodeProps<Mech.Node.Get>) {
    const scope = useScope()?.();
    const types = () => props.node.types.filter(type => !scope?.named_after(props.node.entity, type));
    const keys = () => Object.keys(props.node.props);

    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type={keys().length === 0 ? props.node.type : "filter"} />
            <section>
                <Show when={types().length > 0 || keys().length === 0}>
                    <span class="entity">{scope?.name(props.node.entity)}</span>
                </Show>
                <Show when={types().length > 0}>
                    <span class="op">(</span>
                    <For each={types()}>
                        {(type) => <span class="arg type">{type}</span>}
                    </For>
                    <span class="op">)</span>
                </Show>

                <For each={keys()}>
                    {(prop) => scope?.name(props.node.props[prop])}
                </For>
            </section>
        </NodeBase>
    );
}
