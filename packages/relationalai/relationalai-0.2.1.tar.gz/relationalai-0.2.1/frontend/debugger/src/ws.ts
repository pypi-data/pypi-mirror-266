// In its own file to make it easy to ignore the connection failed spam it produces. :(
export function create_ws(url: string) {
    return new WebSocket(url);
}
