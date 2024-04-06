import r from '@hat-open/renderer';
import * as u from '@hat-open/util';
function isMsgResponse(msg) {
    return msg.type == 'response';
}
function isMsgState(msg) {
    return msg.type == 'state';
}
function isMsgNotify(msg) {
    return msg.type == 'notify';
}
export class OpenEvent extends CustomEvent {
    constructor() {
        super('open');
    }
}
export class CloseEvent extends CustomEvent {
    constructor() {
        super('close');
    }
}
export class NotifyEvent extends CustomEvent {
    constructor(notification) {
        super('notify', { detail: notification });
    }
}
export class ChangeEvent extends CustomEvent {
    constructor(state) {
        super('change', { detail: state });
    }
}
export class ConnectedEvent extends CustomEvent {
    constructor() {
        super('connected');
    }
}
export class DisconnectedEvent extends CustomEvent {
    constructor() {
        super('disconnected');
    }
}
/**
 * Get default juggler server address
 */
export function getDefaultAddress() {
    const protocol = window.location.protocol == 'https:' ? 'wss' : 'ws';
    const hostname = window.location.hostname || 'localhost';
    const port = window.location.port;
    return `${protocol}://${hostname}` + (port ? `:${port}` : '') + '/ws';
}
/**
 * Juggler client connection
 *
 * Available events:
 *  - `OpenEvent` - connection is opened
 *  - `CloseEvent` - connection is closed
 *  - `NotifyEvent` - received new notification
 *  - `ChangeEvent` - remote state changed
 */
export class Connection extends EventTarget {
    _state = null;
    _nextId = 1;
    _futures = new Map();
    _ws;
    /**
     * Create connection
     *
     * Juggler server address is formatted as
     * ``ws[s]://<host>[:<port>][/<path>]``. If not provided, hostname
     * and port obtained from ``widow.location`` are used instead, with
     * ``ws`` as a path.
     */
    constructor(address = getDefaultAddress()) {
        super();
        this._ws = new WebSocket(address);
        this._ws.addEventListener('open', () => this._onOpen());
        this._ws.addEventListener('close', () => this._onClose());
        this._ws.addEventListener('message', evt => this._onMessage(evt.data));
    }
    /**
     * Remote server state
     */
    get state() {
        return this._state;
    }
    /**
     * WebSocket ready state
     */
    get readyState() {
        return this._ws.readyState;
    }
    /**
     * Close connection
     */
    close() {
        this._ws.close(1000);
    }
    /**
     * Send request and wait for response
     */
    async send(name, data) {
        if (this.readyState != WebSocket.OPEN) {
            throw new Error("connection not open");
        }
        const id = this._nextId++;
        this._ws.send(JSON.stringify({
            type: 'request',
            id: id,
            name: name,
            data: data
        }));
        const f = u.createFuture();
        try {
            this._futures.set(id, f);
            return await f;
        }
        finally {
            this._futures.delete(id);
        }
    }
    _onOpen() {
        this.dispatchEvent(new OpenEvent());
    }
    _onClose() {
        this.dispatchEvent(new CloseEvent());
        for (const f of this._futures.values())
            if (!f.done())
                f.setError(new Error("connection not open"));
    }
    _onMessage(data) {
        try {
            const msg = JSON.parse(data);
            if (isMsgState(msg)) {
                this._state = u.patch(msg.diff, this._state);
                this.dispatchEvent(new ChangeEvent(this._state));
            }
            else if (isMsgNotify(msg)) {
                this.dispatchEvent(new NotifyEvent({
                    name: msg.name,
                    data: msg.data
                }));
            }
            else if (isMsgResponse(msg)) {
                const f = this._futures.get(msg.id);
                if (f && !f.done()) {
                    if (msg.success) {
                        f.setResult(msg.data);
                    }
                    else {
                        f.setError(msg.data);
                    }
                }
            }
            else {
                throw new Error('unsupported message type');
            }
        }
        catch (e) {
            this._ws.close();
            throw e;
        }
    }
}
/**
 * Juggler based application
 *
 * Available events:
 *  - ConnectedEvent - connected to server
 *  - DisconnectedEvent - disconnected from server
 *  - NotifyEvent - received new notification
 */
export class Application extends EventTarget {
    _statePath;
    _renderer;
    _addresses;
    _next_address_index;
    _retryDelay;
    _pingDelay;
    _pingTimeout;
    _conn;
    /**
     * Create application
     *
     * If `statePath` is `null`, remote server state is not synced to renderer
     * state.
     *
     * Format of provided addresses is same as in `Connection` constructor.
     *
     * If `retryDelay` is `null`, once connection to server is closed,
     * new connection is not established.
     */
    constructor(statePath = null, renderer = r, addresses = [getDefaultAddress()], retryDelay = 5000, pingDelay = 5000, pingTimeout = 5000) {
        super();
        this._statePath = statePath;
        this._renderer = renderer;
        this._addresses = addresses;
        this._next_address_index = 0;
        this._retryDelay = retryDelay;
        this._pingDelay = pingDelay;
        this._pingTimeout = pingTimeout;
        this._conn = null;
        u.delay(() => this._connectLoop());
    }
    /**
     * Server addresses
     */
    get addresses() {
        return this._addresses;
    }
    /**
     * Set server addresses
     */
    setAddresses(addresses) {
        this._addresses = addresses;
        this._next_address_index = 0;
    }
    /**
     * Disconnect from current server
     *
     * After active connection is closed, application immediately tries to
     * establish connection using next server address or tries to connect
     * to  first server address after `retryDelay` elapses.
     */
    disconnect() {
        if (!this._conn)
            return;
        this._conn.close();
    }
    /**
     * Send request and wait for response
     */
    async send(name, data) {
        if (!this._conn)
            throw new Error("connection closed");
        return await this._conn.send(name, data);
    }
    async _connectLoop() {
        while (true) {
            while (this._next_address_index < this._addresses.length) {
                const address = this._addresses[this._next_address_index++];
                const closeFuture = u.createFuture();
                const conn = new Connection(address);
                conn.addEventListener('open', () => {
                    this._pingLoop(conn);
                    this.dispatchEvent(new ConnectedEvent());
                });
                conn.addEventListener('close', () => {
                    closeFuture.setResult();
                    if (this._statePath)
                        this._renderer.set(this._statePath, null);
                    this.dispatchEvent(new DisconnectedEvent());
                });
                conn.addEventListener('notify', evt => {
                    const notification = evt.detail;
                    this.dispatchEvent(new NotifyEvent(notification));
                });
                conn.addEventListener('change', evt => {
                    if (this._statePath == null)
                        return;
                    const data = evt.detail;
                    this._renderer.set(this._statePath, data);
                });
                this._conn = conn;
                await closeFuture;
                this._conn = null;
            }
            if (this._retryDelay == null)
                break;
            await u.sleep(this._retryDelay);
            this._next_address_index = 0;
        }
    }
    async _pingLoop(conn) {
        if (this._pingDelay == null)
            return;
        while (true) {
            await u.sleep(this._pingDelay);
            const timeout = setTimeout(() => {
                conn.close();
            }, this._pingTimeout);
            try {
                await conn.send('', null);
            }
            catch (e) {
                break;
            }
            finally {
                clearTimeout(timeout);
            }
        }
        conn.close();
    }
}
