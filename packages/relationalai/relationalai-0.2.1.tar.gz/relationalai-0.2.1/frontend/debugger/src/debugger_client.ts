import { Accessor, Setter, createMemo, createSignal } from "solid-js";
import * as Mech from "./types/mech";
import { create_ws } from "./ws";

export namespace Message {
    export interface Base {
        event: string,
        span?: string[],
        [key: string]: unknown
    }

    export interface SpanStart extends Base {
        event: "span_start",
        span: string[],
        start_time: number,
    }
    export interface SpanEnd extends Base {
        event: "span_end",
        span: string[],
        start_time: number,
        end_time: number,
        elapsed: number,
    }

    export interface Time extends Base {
        event: "time",
        type: string,
        elapsed: number,
        results: Results
    }

    export interface Error extends Base {
        event: "error",
        err: any
    }

    export interface Compilation extends Base {
        event: "compilation",
        source: Source,
        passes: Pass[],
        emitted: string,
        emit_time: number,
        mech?: Mech.Machine
    }

    export type Event = Time | Error | Compilation;

    interface Pass {
        name: string,
        task: string,
        elapsed: number
    }

    interface Source {
        file: string,
        line: number,
        block: string,
    }

    interface Results {
        values: Record<string, any>[],
    }
}
export type Message =
    | Message.SpanStart
    | Message.SpanEnd
    | Message.Event

export interface Span {
    event: "span",
    span: string[];
    start_time: number,
    end_time?: number,
    elapsed?: number,

    events: (Span|Message.Event)[],

    [key: string]: unknown,
}

export const [messages, set_messages] = createSignal<Message[]>([], {equals: () => false})

export const spans = createMemo(() => {
    let stack: Span[] = [
        {event: "span", span: [], start_time: 0, events: []}
    ];

    for(let msg of messages()) {
        let cur = stack[stack.length - 1]!;

        if(msg.event === "span_start") {
            let sub: Span = {...msg, event: "span", events: []};
            cur.events.push(sub);
            stack.push(sub)
        } else if(msg.event === "span_end") {
            for(let key in msg) {
                if(key === "span" || key === "event") continue;
                (cur as any)[key] = msg[key];
            }
            stack.pop();
        } else {
            cur.events.push(msg);
        }
    }

    return stack[0].events;
});

function ends_in<T>(list: T[], one_of: T[]) {
    if(list.length === 0) return false;

    let last = list[list.length - 1];
    for(let v of one_of) {
        if(v === last) return true;
    }
    return false;
}

export interface Block extends Span {
    task: string,
    mech: Mech.Machine
}

export function is_block_span(span: Span|Message.Event): span is Block {
    return span.event === "span" && ends_in(span.span, ["rule", "query"]) && span?.name !== "pyrel_base";
}

export function is_compilation(span: Span|Message.Event): span is Message.Compilation {
    return span.event === "compilation";
}


export const blocks = () => spans().filter(is_block_span);

export function clear_messages() {
    set_messages([]);
}

function add_message(msg: any) {
    set_messages((prev) => {
        prev.push(msg);
        return prev;
    })
}

export class Connection {
    private socket: WebSocket | null;
    private shouldReconnect: boolean;
    private active = false;
    private set_connected: Setter<boolean>;

    ws_url: string;
    reconnectInterval: number;
    readonly connected: Accessor<boolean>;

    constructor(ws_url: string, reconnectInterval: number = 5_000) {
        this.ws_url = ws_url;
        this.socket = null;
        this.shouldReconnect = true;
        this.reconnectInterval = reconnectInterval;
        let [connected, set_connected] = createSignal<boolean>(false);
        this.connected = connected;
        this.set_connected = set_connected;
        this.connect();
    }

    private connect(): void {
        // @NOTE: I wasted an hour trying to figure out how to suppress the default error message and then gave up.
        this.socket = create_ws(this.ws_url);

        this.socket.addEventListener("open", () => {
            this.active = true;
            this.set_connected(true);
        });

        this.socket.addEventListener("message", (event) => {
            try {
                const msg = JSON.parse(event.data);
                if(msg.event === "program_complete") {
                    this.active = false;
                }
                add_message(msg);
            } catch (err) {
                console.warn("Failed to parse message:", event.data);
            }
        });

        this.socket.addEventListener("close", () => {
            this.set_connected(false);
            if(this.active) {
                console.warn("Disconnected unexpectedly from the WebSocket server");
                this.active = false;
            }

            if (this.shouldReconnect) {
                setTimeout(() => this.connect(), this.reconnectInterval);
            }
        });

        this.socket.addEventListener("error", (event) => {
            if (this.socket) {
                this.socket.close();
            }
        });
    }

    public close(): void {
        this.shouldReconnect = false;
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Usage:
export const connection = new Connection(`ws://${location.hostname}:5678`);
