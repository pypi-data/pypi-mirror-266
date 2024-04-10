import { Dialog as KDialog } from "@kobalte/core";
import type { DialogRootProps } from "@kobalte/core/dist/types/dialog";
import { IconX } from "@tabler/icons-solidjs";
import { JSXElement, splitProps } from "solid-js";
import { Button } from "./Button";
import "./Modal.styl";

export interface ModalProps extends DialogRootProps {
    title?: string,
    class?: string,
    content?: JSXElement,
}
export function Modal(props: ModalProps) {
    const [local, remote] = splitProps(props, ["title", "content", "children", "class"]);
    return (
        <KDialog.Root modal {...remote}>
            {local.children}
            <KDialog.Portal>
                <div class="modal">
                    <KDialog.Overlay class="modal-overlay" />
                    <KDialog.Content class={`modal-content ${local.class || ""}`}>
                        <header class="modal-header">
                            <Modal.Title class="modal-title">{local.title}</Modal.Title>
                            <Modal.CloseButton as={Button} class="modal-close icon">
                                <IconX />
                            </Modal.CloseButton>
                        </header>
                        {local.content}
                    </KDialog.Content>
                </div>
            </KDialog.Portal>
        </KDialog.Root>
    )
}
Modal.Trigger = KDialog.Trigger;
Modal.Title = KDialog.Title;
Modal.CloseButton = KDialog.CloseButton;
Modal.Description = KDialog.Description;
