"use strict";
(self["webpackChunkimjoy_jupyterlab_extension"] = self["webpackChunkimjoy_jupyterlab_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/comm-connection.js":
/*!********************************!*\
  !*** ./lib/comm-connection.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Connection: () => (/* binding */ Connection),
/* harmony export */   putBuffers: () => (/* binding */ putBuffers),
/* harmony export */   removeBuffers: () => (/* binding */ removeBuffers)
/* harmony export */ });
/* eslint max-classes-per-file: "off" */
/* eslint no-underscore-dangle: "off" */
function isSerializable(object) {
    return typeof object === 'object' && object && object.toJSON;
}
function isObject(value) {
    return (value && typeof value === 'object' && value.constructor === Object);
}
// pub_buffers and removeBuffers are taken from
// https://github.com/jupyter-widgets/ipywidgets/blob/master/packages/base/src/utils.ts
// Author: IPython Development Team
// License: BSD
function putBuffers(state, bufferPaths, buffers) {
    buffers = buffers.map(b => {
        if (b instanceof DataView) {
            return b.buffer;
        }
        return b instanceof ArrayBuffer ? b : b.buffer;
    });
    for (let i = 0; i < bufferPaths.length; i++) {
        const bufferPath = bufferPaths[i];
        // say we want to set state[x][y][z] = buffers[i]
        let obj = state;
        // we first get obj = state[x][y]
        for (let j = 0; j < bufferPath.length - 1; j++) {
            obj = obj[bufferPath[j]];
        }
        // and then set: obj[z] = buffers[i]
        obj[bufferPath[bufferPath.length - 1]] = buffers[i];
    }
}
/**
 * The inverse of putBuffers, return an objects with the new state where all buffers(ArrayBuffer)
 * are removed. If a buffer is a member of an object, that object is cloned, and the key removed. If a buffer
 * is an element of an array, that array is cloned, and the element is set to null.
 * See putBuffers for the meaning of buffer_paths
 * Returns an object with the new state (.state) an array with paths to the buffers (.buffer_paths),
 * and the buffers associated to those paths (.buffers).
 */
function removeBuffers(state) {
    const buffers = [];
    const bufferPaths = [];
    // if we need to remove an object from a list, we need to clone that list, otherwise we may modify
    // the internal state of the widget model
    // however, we do not want to clone everything, for performance
    function remove(obj, path) {
        if (isSerializable(obj)) {
            // We need to get the JSON form of the object before recursing.
            // See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify#toJSON()_behavior
            obj = obj.toJSON();
        }
        if (Array.isArray(obj)) {
            let isCloned = false;
            for (let i = 0; i < obj.length; i++) {
                const value = obj[i];
                if (value) {
                    if (value instanceof ArrayBuffer ||
                        ArrayBuffer.isView(value)) {
                        if (!isCloned) {
                            obj = obj.slice();
                            isCloned = true;
                        }
                        buffers.push(ArrayBuffer.isView(value) ? value.buffer : value);
                        bufferPaths.push(path.concat([i]));
                        // easier to just keep the array, but clear the entry, otherwise we have to think
                        // about array length, much easier this way
                        obj[i] = null;
                    }
                    else {
                        const newValue = remove(value, path.concat([i]));
                        // only assigned when the value changes, we may serialize objects that don't support assignment
                        if (newValue !== value) {
                            if (!isCloned) {
                                obj = obj.slice();
                                isCloned = true;
                            }
                            obj[i] = newValue;
                        }
                    }
                }
            }
        }
        else if (isObject(obj)) {
            // eslint-disable-next-line no-restricted-syntax
            for (const key of Object.keys(obj)) {
                let isCloned = false;
                if (Object.prototype.hasOwnProperty.call(obj, key)) {
                    const value = obj[key];
                    if (value) {
                        if (value instanceof ArrayBuffer ||
                            ArrayBuffer.isView(value)) {
                            if (!isCloned) {
                                obj = {
                                    ...obj,
                                };
                                isCloned = true;
                            }
                            buffers.push(ArrayBuffer.isView(value) ? value.buffer : value);
                            bufferPaths.push(path.concat([key]));
                            delete obj[key]; // for objects/dicts we just delete them
                        }
                        else {
                            const newValue = remove(value, path.concat([key]));
                            // only assigned when the value changes, we may serialize objects that don't support assignment
                            if (newValue !== value) {
                                if (!isCloned) {
                                    obj = {
                                        ...obj,
                                    };
                                    isCloned = true;
                                }
                                obj[key] = newValue;
                            }
                        }
                    }
                }
            }
        }
        return obj;
    }
    const newState = remove(state, []);
    return {
        state: newState,
        buffers,
        buffer_paths: bufferPaths,
    };
}
class MessageEmitter {
    constructor(debug) {
        this._event_handlers = {};
        this._once_handlers = {};
        this._debug = debug;
    }
    emit() {
        throw new Error('emit is not implemented');
    }
    on(event, handler) {
        if (!this._event_handlers[event]) {
            this._event_handlers[event] = [];
        }
        this._event_handlers[event].push(handler);
    }
    once(event, handler) {
        handler.___event_run_once = true;
        this.on(event, handler);
    }
    off(event, handler) {
        if (!event && !handler) {
            // remove all events handlers
            this._event_handlers = {};
        }
        else if (event && !handler) {
            // remove all hanlders for the event
            if (this._event_handlers[event])
                this._event_handlers[event] = [];
        }
        else if (this._event_handlers[event]) {
            // remove a specific handler
            const idx = this._event_handlers[event].indexOf(handler);
            if (idx >= 0) {
                this._event_handlers[event].splice(idx, 1);
            }
        }
    }
    _fire(event, data) {
        if (this._event_handlers[event]) {
            let i = this._event_handlers[event].length;
            while (i--) {
                const handler = this._event_handlers[event][i];
                try {
                    handler(data);
                }
                catch (e) {
                    console.error(e);
                }
                finally {
                    if (handler.___event_run_once) {
                        this._event_handlers[event].splice(i, 1);
                    }
                }
            }
        }
        else if (this._debug) {
            console.warn('unhandled event', event, data);
        }
    }
}
class Connection extends MessageEmitter {
    constructor(config) {
        super(config && config.debug);
        const comm = config.kernel.createComm('imjoy_rpc');
        comm.open({});
        comm.onMsg = msg => {
            const { data } = msg.content;
            const bufferPaths = data.__buffer_paths__ || [];
            delete data.__buffer_paths__;
            putBuffers(data, bufferPaths, msg.buffers || []);
            if (data.type === 'log' || data.type === 'info') {
                console.log(data.message);
            }
            else if (data.type === 'error') {
                console.error(data.message);
            }
            else {
                if (data.peer_id) {
                    this._peer_id = data.peer_id;
                }
                this._fire(data.type, data);
            }
        };
        this.comm = comm;
    }
    connect() { }
    disconnect() { }
    emit(data) {
        data.peer_id = this._peer_id;
        const split = removeBuffers(data);
        split.state.__buffer_paths__ = split.buffer_paths;
        // NOTE: updated for newer kernels, the send signature is different
        this.comm.send(split.state, null, split.buffers);
    }
}


/***/ }),

/***/ "./lib/imjoy-extension.js":
/*!********************************!*\
  !*** ./lib/imjoy-extension.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ImjoyExtension: () => (/* binding */ ImjoyExtension),
/* harmony export */   parseURL: () => (/* binding */ parseURL)
/* harmony export */ });
/* harmony import */ var imjoy_core_dist_imjoy_loader__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! imjoy-core/dist/imjoy-loader */ "./node_modules/imjoy-core/dist/imjoy-loader.js");
/* harmony import */ var imjoy_core_dist_imjoy_loader__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(imjoy_core_dist_imjoy_loader__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var imjoy_core_dist_imjoy_rpc__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! imjoy-core/dist/imjoy-rpc */ "./node_modules/imjoy-core/dist/imjoy-rpc.js");
/* harmony import */ var imjoy_core_dist_imjoy_rpc__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(imjoy_core_dist_imjoy_rpc__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _utils_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./utils.js */ "./lib/utils.js");
/* harmony import */ var reflect_metadata__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! reflect-metadata */ "webpack/sharing/consume/default/reflect-metadata/reflect-metadata");
/* harmony import */ var reflect_metadata__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(reflect_metadata__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _comm_connection_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./comm-connection.js */ "./lib/comm-connection.js");
/**
 * Initialization data for the imjoy-jupyterlab-extension extension.
 */








// import { version } from '../package.json';

async function patchPyodideKernel(kernel) {
    const info = await kernel.info;
    // apply patch for pyolite to make sure we have the kernel id
    if (info.implementation === 'pyodide') {
        const kernel_patch = `
import os
import ipykernel
import micropip
import sys
await micropip.install([ "imjoy-rpc"])
import imjoy_rpc
if 'imjoy' not in sys.modules:
    sys.modules['imjoy'] = sys.modules['imjoy_rpc']
if 'IMJOY_RPC_CONNECTION' not in os.environ:
    os.environ['IMJOY_RPC_CONNECTION'] = 'jupyter'
class Connect():
    def __init__(self, kernel_id):
        self.kernel_id = kernel_id
    def get_connection_file(self):
        return f"kernel-{self.kernel_id}.json"
if not hasattr(ipykernel, 'connect'):
    ipykernel.connect = Connect("${kernel.id}")
`;
        const future = kernel.requestExecute({ code: kernel_patch });
        await future.done;
        console.log('Pyodide kernel patch applied');
    }
}
async function parseURL(queryString, app, browser, trans) {
    var _a;
    const urlParams = new URLSearchParams(queryString);
    const urls = urlParams.getAll("load");
    let lastFile = null;
    for (let url of urls) {
        let type = '';
        let blob;
        // fetch the file from the URL
        try {
            if (url.includes("//zenodo.org/record")) {
                url = await (0,_utils_js__WEBPACK_IMPORTED_MODULE_6__.convertZenodoFileUrl)(url);
            }
            else {
                url = await (0,_utils_js__WEBPACK_IMPORTED_MODULE_6__.githubUrlRaw)(url, ".ipynb") || url;
            }
            const req = await fetch(url);
            blob = await req.blob();
            type = (_a = req.headers.get('Content-Type')) !== null && _a !== void 0 ? _a : '';
            // upload the content of the file to the server
            try {
                const name = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_4__.PathExt.basename(url).split("?")[0];
                const file = new File([blob], name, { type });
                const model = await browser.model.upload(file);
                lastFile = model.path;
                console.log("File uploaded: " + model.path);
            }
            catch (error) {
                (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)(trans._p('showErrorMessage', 'Upload Error'), error);
            }
        }
        catch (reason) {
            if (reason.response && reason.response.status !== 200) {
                reason.message = trans.__('Could not open URL: %1', url);
            }
            return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.showErrorMessage)(trans.__('Cannot fetch'), reason);
        }
    }
    let file2Open = urlParams.get("open");
    if (file2Open === "1")
        file2Open = lastFile;
    if (file2Open) {
        await app.commands.execute('docmanager:open', {
            path: file2Open
        });
    }
}
class ImjoyExtension {
    constructor(jupyterBaseUrl, labApp, fileBrowser) {
        this.baseUrl = jupyterBaseUrl;
        const isIframe = window.self !== window.top;
        this.notebookHandlerPromise = new Promise((resolve, reject) => {
            this.resolveNotebookHandler = resolve;
            this.rejectNotebookHandler = reject;
        });
        // create an div with id= "window-container"
        const container = document.createElement('div');
        container.id = 'window-container';
        document.body.appendChild(container);
        let imjoy;
        (0,imjoy_core_dist_imjoy_loader__WEBPACK_IMPORTED_MODULE_0__.loadImJoyBasicApp)({
            process_url_query: true,
            show_window_title: false,
            show_progress_bar: true,
            show_empty_window: true,
            menu_style: { position: "absolute", right: 0, top: "2px" },
            window_style: { width: '100%', height: '100%' },
            main_container: null,
            menu_container: null,
            expose_api: false,
            // window_manager_container: "window-container",
            imjoy_api: {
                async createWindow(_plugin, w, extra_config) {
                    if (!document.getElementById(w.window_id)) {
                        if (!w.dialog) {
                            if (document.getElementById(_plugin.id)) {
                                const elem = document.createElement('div');
                                elem.id = w.window_id;
                                elem.classList.add('imjoy-inline-window');
                                document.getElementById(_plugin.id).appendChild(elem);
                            }
                        }
                    }
                    return await imjoy.pm.createWindow(_plugin, w, extra_config);
                },
            }
        }).then(async (app) => {
            console.log(`ImJoy Basic App loaded!`);
            imjoy = app.imjoy;
            const kernelInfo = {};
            if (isIframe) {
                const api = await (0,imjoy_core_dist_imjoy_rpc__WEBPACK_IMPORTED_MODULE_1__.setupRPC)({ name: "JupyterLite" });
                api.export({
                    setup() {
                    },
                    run(ctx) {
                        ctx = ctx || {};
                        ctx.config = ctx.config || {};
                        ctx.config.left_collapsed = ctx.config.left_collapsed === undefined ? true : false;
                        if (ctx.config.left_collapsed) {
                            if (!labApp.shell.leftCollapsed) {
                                labApp.commands.execute('application:toggle-left-area');
                            }
                        }
                        else {
                            if (labApp.shell.leftCollapsed) {
                                labApp.commands.execute('application:toggle-left-area');
                            }
                        }
                    },
                    async fileExists(path) {
                        try {
                            await fileBrowser.model.manager.services.contents.get(path);
                            return true;
                        }
                        catch (e) {
                            return false;
                        }
                    },
                    async getFile(path) {
                        return await fileBrowser.model.manager.services.contents.get(path);
                    },
                    async removeFile(path) {
                        return await fileBrowser.model.manager.deleteFile(path);
                    },
                    async loadFile(name, content, type) {
                        const file = new File([content], name, { type });
                        const model = await fileBrowser.model.upload(file);
                        return model.path;
                    },
                    async openFile(path) {
                        await labApp.commands.execute('docmanager:open', {
                            path: path
                        });
                    },
                    async closeLeft() {
                        if (!labApp.shell.leftCollapsed) {
                            labApp.commands.execute('application:toggle-left-area');
                        }
                    },
                    async openLeft() {
                        if (labApp.shell.leftCollapsed) {
                            labApp.commands.execute('application:toggle-left-area');
                        }
                    }
                });
            }
            async function connectPlugin(kernel_id) {
                if (!kernelInfo[kernel_id]) {
                    console.warn('Kernel is not ready: ' + kernel_id);
                    return;
                }
                const kernel = kernelInfo[kernel_id].kernel;
                await kernel.ready;
                const plugin = await imjoy.pm.connectPlugin(new _comm_connection_js__WEBPACK_IMPORTED_MODULE_7__.Connection({ kernel }));
                kernelInfo[kernel_id].plugin = plugin;
            }
            async function runNotebookPlugin(kernel_id) {
                if (!kernelInfo[kernel_id]) {
                    console.warn('Kernel is not ready: ' + kernel_id);
                    return;
                }
                try {
                    const plugin = kernelInfo[kernel_id].plugin;
                    if (plugin && plugin.api.run) {
                        let config = {};
                        if (plugin.config.ui &&
                            plugin.config.ui.indexOf('{') > -1) {
                            config = await app.imjoy.pm.imjoy_api.showDialog(plugin, plugin.config);
                        }
                        await plugin.api.run({
                            config: config,
                            data: {},
                        });
                    }
                }
                catch (e) {
                    console.error(e);
                    app.showMessage(`Failed to load the plugin, error: ${e}`);
                }
            }
            window.connectPlugin = async (kernel_id) => {
                if (!kernel_id) {
                    console.warn('Please upgrade imjoy-rpc(>=0.3.35) by running `pip install -U imjoy-rpc`');
                    return;
                }
                await connectPlugin(kernel_id);
                await runNotebookPlugin(kernel_id);
            };
            window._connectPlugin = async (kernel_id) => {
                await connectPlugin(kernel_id);
            };
            window._runPluginOnly = async (kernel_id) => {
                await runNotebookPlugin(kernel_id);
            };
            this.resolveNotebookHandler(async (sessionContext, panelNode, buttonNode) => {
                const { kernel } = sessionContext.session;
                buttonNode.style.minWidth = "25px";
                const _spinner = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.Spinner();
                _spinner.node.firstChild.style.width = "20px";
                _spinner.node.firstChild.style.height = "20px";
                sessionContext.kernelChanged.connect(() => {
                    buttonNode.appendChild(_spinner.node);
                    patchPyodideKernel(kernel).finally(() => {
                        buttonNode.removeChild(_spinner.node);
                    }).catch(() => {
                        console.error("Failed to apply pyodide patch");
                    });
                }, sessionContext);
                buttonNode.appendChild(_spinner.node);
                try {
                    await patchPyodideKernel(kernel);
                }
                catch (e) {
                    throw e;
                }
                finally {
                    buttonNode.removeChild(_spinner.node);
                }
                kernelInfo[kernel._id] = { kernel };
                buttonNode.firstChild.innerHTML = `<img src="https://imjoy.io/static/img/imjoy-logo-black.svg" style="height: 17px;">`;
                buttonNode.firstChild.onclick = () => {
                    runNotebookPlugin(kernel._id);
                };
            });
        })
            .catch(e => {
            console.error(e);
            this.rejectNotebookHandler(e);
        });
    }
    /**
     * Create a new extension object.
     */
    createNew(panel, context) {
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_3__.ToolbarButton({
            tooltip: `ImJoy JupyterLab Extension`, // (version: ${version})`,
        });
        panel.toolbar.insertItem(0, 'Run ImJoy Plugin', button);
        context.sessionContext.ready.then(async () => {
            const notebookHandler = await this.notebookHandlerPromise;
            notebookHandler(context.sessionContext, panel.node, button.node);
        });
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_5__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _imjoy_extension_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./imjoy-extension.js */ "./lib/imjoy-extension.js");



/**
 * Initialization data for the imjoy-jupyterlab-extension extension.
 */
const plugin = {
    id: 'imjoy-jupyterlab-extension',
    requires: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__.IFileBrowserFactory, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.ITranslator],
    autoStart: true,
    activate: async function (app, factory, translator) {
        const trans = translator.load('jupyterlab');
        // const { defaultBrowser: browser } = factory;
        // Manually restore and load the default file browser.
        const browser = factory.createFileBrowser('filebrowser', {
            auto: false,
            restore: false
        });
        const jupyterBaseUrl = app.serviceManager.settings.serverSettings.baseUrl;
        app.docRegistry.addWidgetExtension('Notebook', new _imjoy_extension_js__WEBPACK_IMPORTED_MODULE_2__.ImjoyExtension(jupyterBaseUrl, app, browser));
        console.log('JupyterLab extension imjoy-jupyterlab-extension is activated!');
        const currentLocation = new URL(window.location.href);
        app.started.then(() => {
            (0,_imjoy_extension_js__WEBPACK_IMPORTED_MODULE_2__.parseURL)(currentLocation.search, app, browser, trans).finally(() => {
                // restore location, since jupyterlab will force double slashes into single
                window.history.pushState(null, '', currentLocation.href);
            });
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   convertZenodoFileUrl: () => (/* binding */ convertZenodoFileUrl),
/* harmony export */   githubUrlRaw: () => (/* binding */ githubUrlRaw),
/* harmony export */   githubUrlToObject: () => (/* binding */ githubUrlToObject),
/* harmony export */   isUrl: () => (/* binding */ isUrl)
/* harmony export */ });
// from https://github.com/segmentio/is-url
/**
 * RegExps.
 * A URL must match #1 and then at least one of #2/#3.
 * Use two levels of REs to avoid REDOS.
 */
const protocolAndDomainRE = /^(?:\w+:)?\/\/([\s\S]+)$/;
const localhostDomainRE = /^localhost[\:?\d]*(?:[^\:?\d][\s\S]*)?$/;
const nonLocalhostDomainRE = /^[^\s\.]+\.[\s\S]{2,}$/;
/**
 * Loosely validate a URL `string`.
 *
 * @param {String} string
 * @return {Boolean}
 */
function isUrl(string) {
    if (typeof string !== "string") {
        return false;
    }
    var match = string.match(protocolAndDomainRE);
    if (!match) {
        return false;
    }
    var everythingAfterProtocol = match[1];
    if (!everythingAfterProtocol) {
        return false;
    }
    if (localhostDomainRE.test(everythingAfterProtocol) ||
        nonLocalhostDomainRE.test(everythingAfterProtocol)) {
        return true;
    }
    return false;
}
//from: https://github.com/github-modules/github-url-to-object/blob/master/index.js
const laxUrlRegex = /(?:(?:[^:]+:)?[/][/])?(?:.+@)?([^/]+)([/][^?#]+)/;
function githubUrlToObject(repoUrl, opts) {
    var obj = {};
    opts = opts || {};
    if (!repoUrl)
        return null;
    // Allow an object with nested `url` string
    // (common practice in package.json files)
    if (repoUrl.url)
        repoUrl = repoUrl.url;
    if (typeof repoUrl !== "string")
        return null;
    var shorthand = repoUrl.match(/^([\w-_]+)\/([\w-_\.]+)(?:#([\w-_\.]+))?$/);
    var mediumhand = repoUrl.match(/^github:([\w-_]+)\/([\w-_\.]+)(?:#([\w-_\.]+))?$/);
    var antiquated = repoUrl.match(/^git@[\w-_\.]+:([\w-_]+)\/([\w-_\.]+)$/);
    if (shorthand) {
        obj.user = shorthand[1];
        obj.repo = shorthand[2];
        obj.branch = shorthand[3] || "master";
        obj.host = "github.com";
    }
    else if (mediumhand) {
        obj.user = mediumhand[1];
        obj.repo = mediumhand[2];
        obj.branch = mediumhand[3] || "master";
        obj.host = "github.com";
    }
    else if (antiquated) {
        obj.user = antiquated[1];
        obj.repo = antiquated[2].replace(/\.git$/i, "");
        obj.branch = "master";
        obj.host = "github.com";
    }
    else {
        // Turn git+http URLs into http URLs
        repoUrl = repoUrl.replace(/^git\+/, "");
        if (!isUrl(repoUrl))
            return null;
        const [, hostname, pathname] = repoUrl.match(laxUrlRegex) || [];
        if (!hostname)
            return null;
        if (hostname !== "github.com" &&
            hostname !== "www.github.com" &&
            !opts.enterprise)
            return null;
        var parts = pathname.match(/^\/([\w-_]+)\/([\w-_\.]+)(\/tree\/[\w-_\.\/]+)?(\/blob\/[\s\w-_\.\/]+)?/);
        // ([\w-_\.]+)
        if (!parts)
            return null;
        obj.user = parts[1];
        obj.repo = parts[2].replace(/\.git$/i, "");
        obj.host = hostname || "github.com";
        if (parts[3] && /^\/tree\/master\//.test(parts[3])) {
            obj.branch = "master";
            obj.path = parts[3].replace(/\/$/, "");
        }
        else if (parts[3]) {
            obj.branch = parts[3]
                .replace(/^\/tree\//, "")
                .match(/[\w-_.]+\/{0,1}[\w-_]+/)[0];
        }
        else if (parts[4]) {
            obj.branch = parts[4]
                .replace(/^\/blob\//, "")
                .match(/[\w-_.]+\/{0,1}[\w-_]+/)[0];
        }
        else {
            obj.branch = "master";
        }
    }
    if (obj.host === "github.com") {
        obj.apiHost = "api.github.com";
    }
    else {
        obj.apiHost = `${obj.host}/api/v3`;
    }
    obj.tarball_url = `https://${obj.apiHost}/repos/${obj.user}/${obj.repo}/tarball/${obj.branch}`;
    obj.clone_url = `https://${obj.host}/${obj.user}/${obj.repo}`;
    if (obj.branch === "master") {
        obj.https_url = `https://${obj.host}/${obj.user}/${obj.repo}`;
        obj.travis_url = `https://travis-ci.org/${obj.user}/${obj.repo}`;
        obj.zip_url = `https://${obj.host}/${obj.user}/${obj.repo}/archive/master.zip`;
    }
    else {
        obj.https_url = `https://${obj.host}/${obj.user}/${obj.repo}/blob/${obj.branch}`;
        obj.travis_url = `https://travis-ci.org/${obj.user}/${obj.repo}?branch=${obj.branch}`;
        obj.zip_url = `https://${obj.host}/${obj.user}/${obj.repo}/archive/${obj.branch}.zip`;
    }
    // Support deep paths (like lerna-style repos)
    if (obj.path) {
        obj.https_url += obj.path;
    }
    obj.api_url = `https://${obj.apiHost}/repos/${obj.user}/${obj.repo}`;
    return obj;
}
// from: https://github.com/Elixirdoc/github-url-raw
async function githubUrlRaw(url, extFilter) {
    if (url.includes("gist.github.com")) {
        const gistId = url.split("/").slice(-1)[0];
        const blob = await fetch("https://api.github.com/gists/" + gistId).then(r => r.blob());
        const data = JSON.parse(await new Response(blob).text());
        // TODO: handle multiple files, e.g.: display them all
        if (extFilter) {
            const selected_file = Object.values(data.files).filter(file => {
                return file.filename.endsWith(extFilter);
            })[0];
            return selected_file && selected_file.raw_url;
        }
        else
            return data.files[Object.values(data.files)[0]].raw_url;
    }
    if (!url.includes("blob") || !url.includes("github")) {
        return null;
    }
    var ghObj = githubUrlToObject(url);
    var githubUser = ghObj.user;
    var githubRepo = ghObj.repo;
    // var githubBranch = ghObj.branch;
    var re = new RegExp("^https://github.com/" + githubUser + "/" + githubRepo + "/blob/", "g");
    var regStr = url.replace(re, "");
    return ("https://raw.githubusercontent.com/" +
        githubUser +
        "/" +
        githubRepo +
        "/" +
        regStr);
}
async function convertZenodoFileUrl(url) {
    const myRegexp = /https?:\/\/zenodo.org\/record\/([a-zA-Z0-9-]+)\/files\/(.*)/g;
    const match = myRegexp.exec(url);
    if (!match || match.length !== 3) {
        throw new Error("Invalid zenodo url");
    }
    const [fullUrl, depositId, fileName] = match;
    const blob = await fetch(`https://zenodo.org/api/records/${depositId}`).then(r => r.blob());
    const data = JSON.parse(await new Response(blob).text());
    const fn = fileName.split("?")[0];
    const fileObj = data.files.filter(file => {
        return file.key === fn;
    })[0];
    return fileObj.links.self;
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.9b49eabf628b7b47bd8a.js.map