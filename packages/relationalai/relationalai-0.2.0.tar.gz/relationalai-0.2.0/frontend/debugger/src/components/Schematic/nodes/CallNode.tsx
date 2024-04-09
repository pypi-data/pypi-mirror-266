import { For, Match, Show, Switch } from "solid-js";
import * as Mech from "@src/types/mech";
import { useScope } from "../ScopeProvider";
import { NodeBase, NodeProps, NodeIcon, INFIX_OPS } from "./base";

export function CallNode(props: NodeProps<Mech.Node.Filter | Mech.Node.Compute>) {
    const scope = useScope()?.();
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type={props.node.type} />
            <section>
                <Show when={props.node.ret}>
                    <span class="arg ret">{scope?.name(props.node.ret!)}</span>
                    <span class="op infix"> = </span>
                </Show>
                <Switch>
                    <Match when={INFIX_OPS.has(props.node.op)}>
                        <span class="arg infix">{scope?.name(props.node.args[0])}</span>
                        <span class="op infix">{props.node.op}</span>
                        <span class="arg infix">{scope?.name(props.node.args[1])}</span>
                    </Match>
                    <Match when={true}>
                        <span class="fn">{props.node.op}</span>
                        <span class="op">(</span>
                        <For each={props.node.args}>
                            {(arg) => <span class="arg">{scope?.name(arg)}</span>}
                        </For>
                        <span class="op">)</span>
                    </Match>
                </Switch>
            </section>
        </NodeBase>
    );
}
