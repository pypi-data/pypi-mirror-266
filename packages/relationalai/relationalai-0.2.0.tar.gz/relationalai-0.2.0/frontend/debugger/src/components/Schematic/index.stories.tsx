import type {Meta, StoryObj} from "storybook-solidjs";
import {Schematic} from "./index";

import * as fixtures from "@src/fixtures"
import { Show } from "solid-js";

interface SchematicWrapperProps {
    fixture: keyof typeof fixtures,
    block_ix: number
}

function SchematicWrapper(props: SchematicWrapperProps) {
    let block = () => fixtures[props.fixture]?.[props.block_ix];
    return (
        <Show when={block()} fallback={<span>Fixture {props.fixture} only has {fixtures[props.fixture].length} blocks.</span>}>
            <Schematic block={block()} />
        </Show>
    );
}

const meta: Meta<typeof SchematicWrapper> = {
    component: SchematicWrapper,
    argTypes: {
        fixture: {
            control: {type: "select"},
            options: Object.keys(fixtures)
        },
        block_ix: {
            control: {type: "number"},
        }
    }
}

export default meta;

type Story = StoryObj<typeof SchematicWrapper>;

export const Default: Story = {
    render: (props) => <SchematicWrapper fixture={props.fixture} block_ix={props.block_ix} />,
    args: {
        fixture: "simple",
        block_ix: 1,
    }
}
