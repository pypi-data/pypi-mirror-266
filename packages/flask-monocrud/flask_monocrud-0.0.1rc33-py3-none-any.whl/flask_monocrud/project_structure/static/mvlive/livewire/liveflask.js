import {
    print_,
    attr_beginswith,
    get_model_prop_value,
    parse_interval,
    replace_undefined,
} from '../livewire/utils.js'


import {update_liveflask_model_attributes, init_model} from '../livewire/model.js'
import {init_action} from '../livewire/action.js'
import {init_polling} from '../livewire/polling.js'
import {dispatch} from "../livewire/events.js";


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// INITIALIZERS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
document.querySelectorAll('[data-component]').forEach(el => {
    let live_flask_children = [];

    el.__liveflask = JSON.parse(el.getAttribute('data-snapshot'));
    el.removeAttribute('data-snapshot')


    init_model(el)
    init_action(el)
    init_polling(el)

    console.log(el.__liveflask)

    //console.log(el.__liveflask)
    //init_wire_event_delegator(el)
})


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// EVENTS - DELEGATOR
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function init_wire_event_delegator(el) {
    [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(el.children[0], "wire:")
    if (ATTRIBUTES.includes(attribute)) return;

    el.addEventListener(modifier, function (e) {

        let attribute, raw_attribute, modifier, time, property, value
        [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(e.target, "wire:")

        if (MODIFIERS.includes(modifier) || modifier === undefined) {

        } else {
            value = e.target.getAttribute(raw_attribute)
            send_request(el, {'callMethod': JSON.stringify(value)})
        }

    })
}

export {
    dispatch
}