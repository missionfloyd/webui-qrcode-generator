const qrcode_tooltips = {
    "#qrcode_scale": "Size of each module, in pixels",
    "#qrcode_border": "Border width, in modules",
    "#qrcode_error_correction label:nth-of-type(1)": "Low: 7% correctable",
    "#qrcode_error_correction label:nth-of-type(2)": "Medium: 15% correctable",
    "#qrcode_error_correction label:nth-of-type(3)": "Quartile: 25% correctable",
    "#qrcode_error_correction label:nth-of-type(4)": "High: 30% correctable",
}

onUiUpdate(function(){
    for (let [key, value] of Object.entries(qrcode_tooltips)) {
        e = gradioApp().querySelector(key)
        if (e) gradioApp().querySelector(key).title = value;
    }
})