onUiLoaded(function() {
    gradioApp().querySelector("#qrcode_cal_start").addEventListener("change", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        let out = gradioApp().querySelector("#qrcode_cal_start_value textarea")
        out.value = target.value.replace(/[-:]/g, "")
        updateInput(out);
    });

    gradioApp().querySelector("#qrcode_cal_end").addEventListener("change", (event) => {
        let target = event.originalTarget || event.composedPath()[0];
        let out = gradioApp().querySelector("#qrcode_cal_end_value textarea")
        out.value = target.value.replace(/[-:]/g, "")
        updateInput(out);
    });
});

