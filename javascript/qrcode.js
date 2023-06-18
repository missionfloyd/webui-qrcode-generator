onUiLoaded(function() {
    gradioApp().querySelector("#qrcode_geo_latitude input").addEventListener("input", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        let value = target.value;
        if (value < -90 || value > 90) {
            target.value = clamp(value, -90, 90)
            updateInput(target);
        }
    });

    gradioApp().querySelector("#qrcode_geo_longitude input").addEventListener("input", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        let value = target.value;
        if (value < -180 || value > 180) {
            target.value = clamp(value, -180, 180)
            updateInput(target);
        }
    });
});

function clamp(num, min, max) {
    return Math.min(Math.max(num, min), max);
};

async function sendToControlnet(img, tab, index) {
    const response = await fetch(img);
    const blob = await response.blob();
    const file = new File([blob], "image.png", { type: "image/png" });
    const dt = new DataTransfer();
    dt.items.add(file);
    const list = dt.files;

    window["switch_to_" + tab]();

    const controlnet = gradioApp().querySelector(`#${tab}_script_container #controlnet`);
    const accordion = controlnet.querySelector(":scope > .label-wrap")
    if (!accordion.classList.contains("open")) {
        accordion.click();
    }
    
    const tabs = controlnet.querySelectorAll("div.tab-nav > button");

    if (tabs !== null && tabs.length > 1) {
        tabs[index].click();
    }
    
    const input = controlnet.querySelectorAll("input[type='file']")[index * 2];

    if (input == null) {
        const callback = (observer) => {
            input = controlnet.querySelector("input[type='file']");
            if (input == null) {
                return;
            } else {
                setImage(input, list);
                observer.disconnect();
            }
        }
        const observer = new MutationObserver(callback);
        observer.observe(controlnet, { childList: true });
    } else {
        setImage(input, list);
    }
}

function setImage(input, list) {
    try {
        if (input.previousElementSibling &&
            input.previousElementSibling.previousElementSibling &&
            input.previousElementSibling.previousElementSibling.querySelector("button[aria-label='Clear']")) {
            input.previousElementSibling.previousElementSibling.querySelector("button[aria-label='Clear']").click()
        }
    } catch (e) {
        console.error(e)
    }
    input.value = "";
    input.files = list;
    const event = new Event("change", { "bubbles": true, "composed": true });
    input.dispatchEvent(event);
}
