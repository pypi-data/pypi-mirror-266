import { Collapsible } from "@kobalte/core";
import type { CollapsibleRootProps } from "@kobalte/core/dist/types/collapsible";
import { IconChevronLeft } from "@tabler/icons-solidjs";
import { JSXElement, splitProps } from "solid-js";
import { Button } from "./Button";
import "./Sidebar.styl";

export interface SidebarProps extends CollapsibleRootProps {
    class?: string,
    children: JSXElement
}
export function Sidebar(props: SidebarProps) {
    let [local, remote] = splitProps(props, ["class", "children"]);
    return (
        <Collapsible.Root {...remote} class={`sidebar ${local.class ?? ""}`}>
            <Collapsible.Trigger class="sidebar-trigger icon">
                <Button class="icon" tooltip="open/close sidebar">
                    <IconChevronLeft />
                </Button>
            </Collapsible.Trigger>
            <Collapsible.Content class="sidebar-content">
                <div class="sidebar-inner">
                    {local.children}
                </div>
            </Collapsible.Content>
        </Collapsible.Root>
    )
}
