import * as Mech from "@src/types/mech";
import { NodeBase, NodeProps, NodeIcon } from "./base";
import { Rail } from "..";

//------------------------------------------------------------------------------
// Container Node
//------------------------------------------------------------------------------

export function SequenceNode(props: NodeProps<Mech.Node.Sequence>) {
    return (
        <NodeBase node={props.node} ix={props.ix}>
            <NodeIcon type="branch" />
            <Rail items={props.node.items} nested out={!props.flipped} in={props.flipped} flipped={props.flipped} />
        </NodeBase>
    );
}
