import { NumberField as KNumberField, TextField as KTextField } from "@kobalte/core";
import type { NumberFieldRootProps, } from "@kobalte/core/dist/types/number-field";
import type { TextFieldRootProps } from "@kobalte/core/dist/types/text-field";
import { IconCaretDownFilled, IconCaretUpFilled } from "@tabler/icons-solidjs";
import { JSXElement, Show, splitProps } from "solid-js";
import "./Field.styl";

//------------------------------------------------------------------------------
// Common Formats
//------------------------------------------------------------------------------

function coerce<const T extends Record<string, Intl.NumberFormatOptions>>(v: T) {
    return v;
}

export const Format = coerce({
    "seconds": {
        style: "unit",
        unit: "second",
        unitDisplay: "long",
        minimumFractionDigits: 0,
        maximumFractionDigits: 1,
    }
})

//------------------------------------------------------------------------------
// NumberField
//------------------------------------------------------------------------------

export interface NumberFieldProps extends NumberFieldRootProps {
    label: JSXElement,
    placeholder?: string
}
export function NumberField(props: NumberFieldProps) {
    let [local, remote] = splitProps(props, ["label", "class", "placeholder"]);
    return (
        <KNumberField.Root {...remote} class={`field number ${local.class ?? ""}`}>
            <KNumberField.Label>{local.label}</KNumberField.Label>
            <KNumberField.HiddenInput />
            <span class="field-input">
                <KNumberField.Input class="field-input-value" placeholder={local.placeholder} />
                <div class="field-controls">
                    <KNumberField.IncrementTrigger class="icon field-input-increment">
                        <IconCaretUpFilled size="0.66em" />
                    </KNumberField.IncrementTrigger>
                    <KNumberField.DecrementTrigger class="icon field-input-decrement">
                        <IconCaretDownFilled size="0.66em" />
                    </KNumberField.DecrementTrigger>
                </div>
            </span>
        </KNumberField.Root>
    )
}

//------------------------------------------------------------------------------
// TextField
//------------------------------------------------------------------------------

export interface TextFieldProps extends TextFieldRootProps {
    label: JSXElement,
    type?: string,
    placeholder?: string,
    multiline?: boolean,
    children?: JSXElement,
}
export function TextField(props: TextFieldProps) {
    let [local, remote] = splitProps(props, ["label", "type", "class", "placeholder", "multiline", "children"]);
    return (
        <KTextField.Root {...remote} class={`field ${local.type ?? "text"} ${local.class ?? ""}`}>
            <KTextField.Label>{local.label}</KTextField.Label>
            <span class="field-input">
                <Show when={!local.multiline}>
                    <KTextField.Input class="field-input-value" placeholder={local.placeholder} />
                </Show>
                <Show when={local.multiline}>
                    <KTextField.TextArea class="field-input-value multiline" placeholder={local.placeholder} />
                </Show>
            </span>
            {local.children}
        </KTextField.Root>
    )
}
TextField.Description = KTextField.Description;
TextField.ErrorMessage = KTextField.ErrorMessage

export namespace Field {
    export const Text = TextField;
    export const Number = NumberField;
}
