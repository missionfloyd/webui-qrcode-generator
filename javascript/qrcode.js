function generateQRCode(keys, ...values) {
    const errorCorrection = {
        L: qrcodegen.QrCode.Ecc.LOW,
        M: qrcodegen.QrCode.Ecc.MEDIUM,
        Q: qrcodegen.QrCode.Ecc.QUARTILE,
        H: qrcodegen.QrCode.Ecc.HIGH,
    }

    const args = keys.reduce((obj, key, index) => ({ ...obj, [key]: values[index] }), {});
    
    if (args.selected_tab == "tab_wifi") {
        var data = wifi_data(args.wifi_ssid, args.wifi_password, security=args.wifi_security, args.wifi_hidden)
    } else {
        var data = args.text;
    }

    const qr = qrcodegen.QrCode.encodeText(data, errorCorrection[args.setting_error_correction]);

    const scale = args.size_mode == "size" ? 1 : args.setting_scale
    const border = args.setting_border
    const lightColor = args.setting_light
    const darkColor = args.setting_dark

    const canvas = document.createElement("canvas");
    const width = (qr.size + border * 2) * scale;
    canvas.width = width;
    canvas.height = width;
    const ctx = canvas.getContext("2d");

    for (let y = -border; y < qr.size + border; y++) {
        for (let x = -border; x < qr.size + border; x++) {
            ctx.fillStyle = qr.getModule(x, y) ? darkColor : lightColor;
            ctx.fillRect((x + border) * scale, (y + border) * scale, scale, scale);
        }
    }
    
    const resized = document.createElement("canvas");
    resized.width = args.setting_size;
    resized.height = args.setting_size;
    const ctxresized = resized.getContext("2d");
    ctxresized.imageSmoothingEnabled = false;
    ctxresized.drawImage(canvas, 0, 0, resized.width, resized.height);

    return resized.toDataURL();
}

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
    
    gradioApp().querySelector("#qrcode_geo_longitude input, #qrcode_geo_latitude input").addEventListener("focusout", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        if (target.value == "") {
            target.value = 0;
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

    await window["switch_to_" + tab]();

    const controlnet = gradioApp().querySelector(`#${tab}_script_container #controlnet`);
    const accordion = controlnet.querySelector(":scope > .label-wrap")

    if (!accordion.classList.contains("open")) {
        await accordion.click();
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
    
    controlnet.scrollIntoView();
}

function setImage(input, list) {
    try {
        input.previousElementSibling?.previousElementSibling?.querySelector("button[aria-label='Clear']")?.click();
    } catch (e) {
        console.error(e);
    }
    input.value = "";
    input.files = list;
    const event = new Event("change", { "bubbles": true, "composed": true });
    input.dispatchEvent(event);
}

function wifi_data(ssid, password, security, hidden) {
    const escape = {
        "\\": "\\\\",
        ";": "\\;",
        ":": "\\:",
        '"': '\\"',
    }

    ssid = ssid.replace(/\\|;|:|"/g, matched => {
        return escape[matched];
    });
    
    var data = `WIFI:S:${ssid};`;

    if (security != "None") {
        data += `T:${security.toUpperCase()};`
    }

    if (password) {
        password = password.replace(/\\|;|:|"/g, matched => {
            return escape[matched];
        });
        data += `P:${password};`
    }
    
    data += hidden ? "H:true;" : "";
    return data;
}
