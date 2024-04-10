import type {Meta, StoryObj} from "storybook-solidjs";
import {NumberField, TextField} from "./Field";
import "../app.styl";
import { createSignal } from "solid-js";

const meta: Meta<typeof NumberField> = {
    component: NumberField,
}

export default meta;

type NumberStory = StoryObj<typeof NumberField>;

export const Number: NumberStory = {
    render: (args) => {
        const [v, set_v] = createSignal<number>((args.value ?? 0) as number);
        const format = { minimumFractionDigits: 0, maximumFractionDigits: 1, style: "unit", unit: "second", unitDisplay: "long" } as const;
        return (
            <NumberField label={args.label} formatOptions={format} placeholder={args.placeholder} rawValue={v()} onRawValueChange={set_v} />
        )
    },
    args: {
        label: "Poll interval",
        placeholder: "2 (seconds)",
        value: 10
    }
}


type TextStory = StoryObj<typeof TextField>;

export const Text: TextStory = {
    render: (args) => {
        const [v, set_v] = createSignal(args.value);
        return (
            <TextField label={args.label} placeholder={args.placeholder} value={v()} onChange={set_v} />
        )
    },
    args: {
        label: "debugger URL",
        placeholder: "ws://localhost:1234",
        value: "some text"
    }
}
