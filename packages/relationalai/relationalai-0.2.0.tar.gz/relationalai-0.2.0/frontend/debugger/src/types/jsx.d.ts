import "solid-js";
declare module "solid-js" {
    namespace JSX {
        interface IntrinsicElements {
            [name: string]: HTMLAttributes<HTMLElement>
        }
    }
}
