import type {Meta, StoryObj} from "storybook-solidjs";
import {Tooltip} from "./Tooltip";

const meta: Meta<typeof Tooltip> = {
    component: Tooltip,
}

export default meta;

type Story = StoryObj<typeof Tooltip>;

export const Default: Story = {
    render: (args) => {
        return (
            <Tooltip content={args.content} open={args.open || undefined}>
                <Tooltip.Trigger as="div">
                    I'm the trigger
                </Tooltip.Trigger>
            </Tooltip>
        )
    },
    args: {
        content: "I'm a tooltip!",
        open: true,
    }
}
