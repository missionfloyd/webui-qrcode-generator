onUiLoaded(function() {
    gradioApp().querySelector("#qrcode_geo_latitude input").addEventListener("input", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        if (target.value < -90) {
            target.value = -90;
        } else if (target.value > 90) {
            target.value = 90;
        } else {
            return;
        }
        updateInput(target);
    });

    gradioApp().querySelector("#qrcode_geo_longitude input").addEventListener("input", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        if (target.value < -180) {
            target.value = -180;
        } else if (target.value > 180) {
            target.value = 180;
        } else {
            return;
        }
        updateInput(target);
    });
});

async function sendToControlnet(img, tab, index) {
    const response = await fetch(img);
    const blob = await response.blob();
    const file = new File([blob], "image.png", { type: "image/png" });
    const dt = new DataTransfer();
    dt.items.add(file);
    const list = dt.files;

    const selector = `#${tab}_script_container`;

    if (tab === "txt2img"){
        switch_to_txt2img();
    } else if (tab === "img2img") {
        switch_to_img2img();
    }

    const accordion = gradioApp().querySelector(selector).querySelector("#controlnet > .label-wrap > .icon")
    if (accordion.style.transform == "rotate(90deg)") {
        accordion.click();
    }
    
    const controlnetDiv = gradioApp().querySelector(selector).querySelector("#controlnet");
    const tabs = controlnetDiv.querySelectorAll("div.tab-nav > button");

    if (tabs !== null && tabs.length > 1) {
        tabs[index].click();
    }
    
    let input = gradioApp().querySelector(selector).querySelector("#controlnet").querySelectorAll("input[type='file']")[index * 2];

    if (input == null) {
        const callback = (observer) => {
            input = gradioApp().querySelector(selector).querySelector("#controlnet").querySelector("input[type='file']");
            if (input == null) {
                console.error('input[type=file] NOT exists');
                return;
            } else {
                setImage(input, list);
                observer.disconnect();
            }
        }
        const observer = new MutationObserver(callback);
        observer.observe(gradioApp().querySelector(selector).querySelector("#controlnet"), { childList: true });
    } else {
        setImage(input, list);
    }
}

function setImage(input, list) {
    try {
        if (input.previousElementSibling  
           && input.previousElementSibling.previousElementSibling 
           && input.previousElementSibling.previousElementSibling.querySelector("button[aria-label='Clear']")) {
            input.previousElementSibling.previousElementSibling.querySelector("button[aria-label='Clear']").click()
        }
    } catch (e) {
        console.error(e)
    }
    input.value = "";
    input.files = list;
    const event = new Event('change', { 'bubbles': true, "composed": true });
    input.dispatchEvent(event);
}