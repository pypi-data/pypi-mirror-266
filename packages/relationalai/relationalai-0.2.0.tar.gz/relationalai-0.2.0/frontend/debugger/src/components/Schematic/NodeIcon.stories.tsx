import type {Meta, StoryObj} from "storybook-solidjs";
import {NodeIcon, node_icons} from "./nodes/base";
import "./index";

const meta: Meta<typeof NodeIcon> = {
    component: NodeIcon,
    argTypes: {
        type: {
            control: {type: "select"},
            options: Object.keys(node_icons)
        }
    }
}

export default meta;

type Story = StoryObj<typeof NodeIcon>;

export const Default: Story = {
    render: (args) => {
        return (
            <div style="width: 20px; height: 20px;">
                <NodeIcon type={args.type} />
            </div>
        )
    },
    args: {
        type: "get"
    }
}
