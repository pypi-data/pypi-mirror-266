import { For } from "solid-js";
import * as Mech from "@src/types/mech";
import { useScope } from "../ScopeProvider";
import { LONG_SECTION_THRESHOLD, NodeBase, NodeProps, NodeIcon } from "./base";

export function EffectNode(props: NodeProps<Mech.Node.Effect>) {
    let section_el!: HTMLElement;

    const scope = useScope()?.();
    const types = () => props.node.types.filter(type => !scope?.named_after(props.node.entity, type));
    const is_long = () => (section_el?.textContent?.length ?? 0) > LONG_SECTION_THRESHOLD;
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type={props.node.type} />
            <section ref={section_el} classList={{ long: is_long() }}>
                <span class="entity">{scope?.name(props.node.entity)}</span>
                <span class="op">(</span>
                <For each={types()}>
                    {(type) => <span class="arg type">{type}</span>}
                </For>
                <For each={Object.keys(props.node.props)}>
                    {(prop) => <span class="arg kv">
                        <span class="property">{prop}</span>
                        <span class="op">=</span>
                        <span class="value">{scope?.name(props.node.props[prop])}</span>
                    </span>}
                </For>
                <span class="op">)</span>
            </section>
        </NodeBase>
    );
}
