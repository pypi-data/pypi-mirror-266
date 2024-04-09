///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// UTILITIES
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

import {update_liveflask_model_attributes} from '../livewire/model.js';
import {init_action} from "../livewire/action.js";


const MODIFIERS = [
    "defer",
    "lazy",
    "debounce"
];

const ATTRIBUTES = [
    "wire:model",
    "wire:poll",
    "wire:snapshot"
];

const print_ = console.log;


function createElementFromHTML(htmlString) {
    const parser = new DOMParser();
    const htmlDoc = parser.parseFromString(htmlString, 'text/xml');


    // Change this to div.childNodes to support multiple top-level nodes.
    return htmlDoc;
}

const attr_beginswith = (prefix, target, exclude_children = true) =>
    Array.from(target.querySelectorAll('*'))
        .filter(
            (e) => Array.from(e.attributes).filter(
                ({name, value}) => name.startsWith(prefix)).length
        );

function get_model_prop_value(el, attribute) {
    let property = el.getAttribute(attribute);
    let value = el.value;
    let modifier = "";
    console.log(property, value, property.split("|").length)
    if (property.split("|").length === 1) {
        return [property, modifier, value];
    }

    if (property.split("|").length === 2) {
        modifier = value.split("|")[0];
        value = value.split("|")[1];
        return [property, modifier, value];
    }

}

export const parse_model_attributes = el => {
    let property = el.getAttribute("data-model");
    return [];
};

function resolve(path, obj = self, separator = '.') {
    if (path.includes('undefined')) {
        path = path.split('.')[0];
    }
    let properties = Array.isArray(path) ? path : path.split(separator);
    let res = properties.reduce((prev, curr) => prev?.[curr], obj);
    if (typeof res === 'object') {
        return res[`${path.split('.')}`];
    } else {
        return res;
    }
}

function replace_undefined(item) {
    var str = JSON.stringify(item, function (key, value) {
            return (value === undefined || value.includes('.')) ? "" : value;
        }
    );
    return JSON.parse(str);
}

function parse_interval(str) {
    if (str === undefined) {
        return undefined;
    }
    if (str.slice(-2) === "ms") {
        return parseFloat(str.slice(0, -2)) || undefined;
    }
    if (str.slice(-1) === "s") {
        return (parseFloat(str.slice(0, -1)) * 1000) || undefined;
    }
    if (str.slice(-1) === "m") {
        return (parseFloat(str.slice(0, -1)) * 1000 * 60) || undefined;
    }
    return parseFloat(str) || undefined;
}

var debounce = (function () {
    var timers = {};

    return function (callback, delay, id) {
        delay = delay || 500;
        id = id || "duplicated event";

        if (timers[id]) {
            clearTimeout(timers[id]);
        }

        timers[id] = setTimeout(callback, delay);
    };
})(); // note the call here so the call for `func_to_param` is omitted


export const debounceModel = _.debounce((el, payload) => {
    send_request(el, payload);
}, parse_interval('150ms'))


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SERVER CALL
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function send_request(el, add_to_payload, target) {
    let snapshot = el.__liveflask
    let children = attr_beginswith('data-component', el);
    fetch("/mvlive", {
        method: "POST",
        headers: {"Content-Type": "application/json", "X-CSRF-Token": csrfToken},
        body: JSON.stringify({
            snapshot: snapshot,
            ...add_to_payload
        })
    }).then(i => i.json()).then(response => {
        let {html, snapshot} = response
        el.__liveflask = snapshot
        el.__liveflask['children'] = children

        if (target.hasAttribute("data-poll") === true) {
            morphdom(target, createElementFromHTML(html).querySelector(`[data-poll=${target.getAttribute('data-poll')}]`).outerHTML)
            return;
        }


        html = `<div data-component="${snapshot.class}" id="${el.id}">${html}</div>`

        morphdom(el, html, {
            onBeforeElUpdated: function (fromEl, toEl) {
                // spec - https://dom.spec.whatwg.org/#concept-node-equals
                if (fromEl.isEqualNode(toEl)) {
                    return false
                }

                return true
            },

            onElUpdated: function (element) {
                if (el.__liveflask['children'].length !== 0) {
                    update_children(el.__liveflask['children'])
                }

            },

        });

        init_action(el)
        //update_liveflask_model_attributes(target)

    })
}

function update_children(children = []) {
    let matched_component;
    children.forEach(i => {
        matched_component = document.getElementById(`${i.__liveflask['key']}`);
        morphdom(matched_component, i.outerHTML)
        // Object.keys(i.__liveflask['data']).forEach(prop => {
        //     console.log(i)
        //     try {
        //         matched_component.querySelector(`[data-model=${prop}]`).innerHTML = i.__liveflask['data'][prop]
        //     } catch (error) {
        //         matched_component.querySelector(`[data-model=${prop}]`).value(i.__liveflask['data'][prop])
        //     }
        //
        // })
    })
}


export {
    ATTRIBUTES,
    MODIFIERS,
    send_request,
    attr_beginswith,
    debounce,
    parse_interval,
    print_,
    get_model_prop_value,
    replace_undefined,
    resolve
}
