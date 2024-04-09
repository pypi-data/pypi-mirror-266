function dispatch(name, params) {
    fetch("/mvlive", {
        method: "GET",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: name,
            params: params
        })
    })
}


export {
    dispatch
}