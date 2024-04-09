import { NodeBase, NodeProps, NodeIcon } from "./base";

export function UnknownNode(props: NodeProps) {
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type={props.node.type} />
            <section>
                unknown node: {props.node.type}
            </section>
        </NodeBase>
    );
}
