import type {Meta, StoryObj} from "storybook-solidjs";
import {Modal} from "./Modal";
import { Button } from "./Button";
import "../app.styl";
import { IconX } from "@tabler/icons-solidjs";

const meta: Meta<typeof Modal> = {
    component: Modal,
}

export default meta;

type Story = StoryObj<typeof Modal>;

export const Default: Story = {
    render: (args) => {
        return (
            <Modal title={args.title} content={<ModalBody />} open={args.open || undefined}>
                <Modal.Trigger as="div">
                    I'm the trigger
                </Modal.Trigger>
            </Modal>
        )
    },
    args: {
        title: "Settings",
        open: true,
    }
}

function ModalBody() {
    return (
        <>
            <section>
                <h3>Connection</h3>
                <label>
                    <span class="form-label">Polling Interval</span>
                    <input type="number" />
                    <span class="form-unit">seconds</span>
                </label>
            </section>
        </>
    )
}
