import { Tooltip as KTooltip } from "@kobalte/core";
import type { TooltipRootProps } from "@kobalte/core/dist/types/tooltip";
import { JSXElement, splitProps } from "solid-js";
import "./Tooltip.styl";

export interface TooltipProps extends TooltipRootProps {
    content: JSXElement,
    children: JSXElement
}
export function Tooltip(props: TooltipProps) {
    const [local, remote] = splitProps(props, ["content", "children"]);
    return (
        <KTooltip.Root {...remote}>
            {local.children}
            <KTooltip.Portal>
                <KTooltip.Content class="tooltip">
                    <KTooltip.Arrow class="tooltip-arrow" />
                    <div class="tooltip-inner">
                        {local.content}
                    </div>
                </KTooltip.Content>
            </KTooltip.Portal>
        </KTooltip.Root>
    )
}

Tooltip.Trigger = KTooltip.Trigger;
