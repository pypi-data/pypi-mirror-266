import {Button as KButton} from "@kobalte/core";
import type { ButtonRootProps } from "@kobalte/core/dist/types/button";
import { JSXElement, Match, Switch, splitProps } from "solid-js";
import {Tooltip} from "./Tooltip";
import "./Button.styl";

export interface ButtonProps extends ButtonRootProps {
    tooltip?: JSXElement
}
export function Button(props: ButtonProps) {
    const [local, remote] = splitProps(props, ["tooltip"]);
    return (
        <Switch>
            <Match when={local.tooltip}>
                <Tooltip content={local.tooltip}>
                    <Tooltip.Trigger as={KButton.Root} {...remote} />
                </Tooltip>
            </Match>
            <Match when={true}>
                <KButton.Root {...remote} />
            </Match>
        </Switch>
    )
}
