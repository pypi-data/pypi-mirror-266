import { Accessor, JSXElement, createContext, createEffect, createMemo, useContext } from "solid-js"
import * as Mech from "@src/types/mech";

//------------------------------------------------------------------------------
// Scope Context / Provider
//------------------------------------------------------------------------------

export const ScopeContext = createContext<Accessor<Scope>>();

interface ScopeProviderProps {
    machine: Mech.Machine,
    children: JSXElement
}
export function ScopeProvider(props: ScopeProviderProps) {
    const scope = createMemo(() => new Scope(props.machine));
    return (
        <ScopeContext.Provider value={scope}>
            {props.children}
        </ScopeContext.Provider>
    );
}

export function useScope() {
    return useContext(ScopeContext);
}

//------------------------------------------------------------------------------
// Scope Class
//------------------------------------------------------------------------------

export class Scope {
    names = new Map<number|Mech.Value, string>();
    base_names = new Map<number | Mech.Constant, string>();
    used_names = new Set<string>();

    constructor(public machine: Mech.Machine) {
        for(let item of machine.items) {
            this.process(item);
        }
    }

    protected process(item: Mech.Node) {
        if(item.type === "get") {
            if(item.types.length > 0) {
                this.suggest_name(item.entity, item.types[0], true);
            }

            let entity_name = this.name(item.entity);
            for(let prop in item.props) {
                this.suggest_name(item.props[prop], `${entity_name}.${prop}`);
            }

        } else if(item.type === "compute" || item.type === "aggregate") {
            this.suggest_name(item.ret, `${item.op}_result`);

        } else if(item.type === "effect") {
            if(item.types.length > 0) {
                this.suggest_name(item.entity, item.types[0], true);
            }
        } else if(item.type === "sequence" || item.type === "union" || item.type === "choice") {
            for(let child of item.items) {
                this.process(child);
            }
        }
    }

    protected suggest_name(value: Mech.Value, name: string, name_even_if_constant = false) {
        if (typeof value !== "object" && !name_even_if_constant) return;

        let key = value?.id ?? value;
        if (this.names.has(key)) return;
        let base_name = name;
        let ix = 2;
        while (this.used_names.has(name)) {
            name = `${base_name}#${ix++}`;
        }
        this.names.set(key, name);
        this.base_names.set(key, base_name);
        this.used_names.add(name);
    }

    name(value: Mech.Value): string {
        let key = value?.id ?? value;
        if (!this.names.has(key)) {
            if (typeof value !== "object") return value;
            throw new Error(`No name for variable ${value.id} is in scope!`);
        }
        return this.names.get(key)!;
    }

    named_after(value: Mech.Value, name: string) {
        let key = value?.id ?? value;
        // console.log("named after?", key, this.base_names.get(key), name);
        return this.base_names.get(key) === name;
    }
}
