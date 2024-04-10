import { Component, For, Setter, Show, createSignal } from "solid-js";
import { IconAntennaBars5, IconAntennaBarsOff, IconBan, IconSettings, IconX } from "@tabler/icons-solidjs";
import { blocks, clear_messages, connection, is_compilation } from "./debugger_client";
import type { Block } from "./debugger_client";
import { Machine } from "./components/Schematic";
import { Sidebar } from "./components/Sidebar";
import { Button } from "./components/Button";
import { Tooltip } from "./components/Tooltip";
import "./app.styl";
import { Modal } from "./components/Modal";
import { Format, Field } from "./components/Field";


const App: Component = () => {
    const [block, set_block] = createSignal<Block>()
    const clear = () => {
        set_block(undefined);
        clear_messages();
    };
    return (
        <app-chrome>
            <Sidebar class="left" defaultOpen>
                <header>
                    <Modal title="Settings" content={<Settings />}>
                      <Modal.Trigger as={Button} class="icon" tooltip="settings">
                        <IconSettings />
                      </Modal.Trigger>
                    </Modal>
                    <span style="flex: 1">
                        {blocks().length} events
                    </span>
                    <Tooltip content={connection.connected() ? "Connected to program" : "Disconnected from program"}>
                        <Tooltip.Trigger as="span">
                            <Show when={connection.connected()} fallback={<IconAntennaBarsOff />}>
                                <IconAntennaBars5 />
                            </Show>
                        </Tooltip.Trigger>
                    </Tooltip>
                    <Button class="icon" onclick={clear} tooltip="clear events">
                        <IconBan />
                    </Button>
                </header>
                <search-bar>
                    {/* @TODO: Combine list + fuzzy searcher into component for selection (?) */}
                    <input placeholder="search..." />
                </search-bar>
                <event-list>
                    <For each={blocks()}>
                        {(block) => <BlockItem block={block} select={set_block} />}
                    </For>
                </event-list>
            </Sidebar>
            <main>
                <app-scroller>
                    <Show when={block()}>
                        <Machine machine={block()!.mech} />
                    </Show>
                </app-scroller>
            </main>
            <Show when={block()}>
              <Sidebar class="right">
                details
              </Sidebar>
            </Show>
        </app-chrome>
    );
};

export default App;

export function Settings() {
    /* const [poll_interval, _set_poll_interval] = createSignal(connection.reconnectInterval);
  * const set_poll_interval = (value: number) => {
  *   let v = (!isNaN(value) && value >= 1) ? value : 1;
  *   connection.reconnectInterval = v * 1000;
  *   _set_poll_interval(v * 1000);
  * }; */


  return (
        <>
            <section>
                <h3>Connection</h3>
                <Field.Number label="Polling Interval" formatOptions={Format.seconds} minValue={1}
                              defaultValue={connection.reconnectInterval / 1000}
                              onRawValueChange={(v) => connection.reconnectInterval = v * 1000} />
                <Field.Text label={"Debug URL"} placeholder={"ws://localhost:1234"}
                            defaultValue={connection.ws_url} onChange={(v) => connection.ws_url = v} />
            </section>

        </>
    )
}

export interface BlockProps {
    block: Block,
    select: Setter<Block | undefined>
}
export function BlockItem(props: BlockProps) {
    let compilation = () => props.block.events.find(is_compilation);
    let source = () => compilation()?.source;
    return (
        <block-item onclick={() => props.select(props.block)}>
            <header>
                <span class="file">{source()?.file}</span>
                <span class="line">L{source()?.line}</span>
            </header>
            <code>
                {source()?.block}
            </code>
        </block-item>
    )
}
