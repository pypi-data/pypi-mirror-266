///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ACTIONS & EVENTS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import {
    send_request,
    attr_beginswith,
    get_model_prop_value,
    parse_interval,
    replace_undefined
} from '../livewire/utils.js';

function init_action(el) {
    let component_name = el.__liveflask['class']
    let retrieved_actions = attr_beginswith('data-action', el);
    console.log(retrieved_actions)
    el.__liveflask['actions'] = [];
    let current_component;

    retrieved_actions.forEach(i => {
        current_component = i.parentNode.closest('[data-component]').getAttribute("data-component");
        if (current_component !== component_name) return;
        el.__liveflask['actions'].push(i)
    })


    el.__liveflask['actions'].forEach(i => {
        let property;
        let value;
        let modifier;


        [property, modifier, value] = get_model_prop_value(i, "data-action")

        if (!i.__data_action_click_registered) {
            i.addEventListener('click', event => {
                let method = property.split("(")[0];
                let args;
                try {
                    args = replace_undefined(property).match(/\(([^)]+)\)/)[1];
                    console.log(args)
                } catch (e) {
                    args = "__NOVAL__"
                }

                send_request(el, {'method': method, "args": args}, i)
            })
            i.__data_action_click_registered = true
        }
    })


}


export {
    init_action
}