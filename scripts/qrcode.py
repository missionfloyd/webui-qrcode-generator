import modules.scripts as scripts
import gradio as gr
import io
import os

from modules import script_callbacks, generation_parameters_copypaste, extensions
from modules.shared import opts
from scripts import constants
from PIL import Image
import segno
from segno import helpers

controlnet_active = "sd-webui-controlnet" in [x.name for x in extensions.active()]

def generate(selected_tab, keys, *values):
    args = dict(zip(keys, values))
    if selected_tab == "tab_wifi":
        if args["wifi_security"] == "None":
            args["wifi_password"] = args["wifi_security"] = None
        data = helpers.make_wifi_data(ssid=args["wifi_ssid"], password=args["wifi_password"], security=args["wifi_security"], hidden=args["wifi_hidden"])
    elif selected_tab == "tab_vcard":
        data = helpers.make_vcard_data(name=args["vcard_name"], displayname=args["vcard_displayname"], nickname=args["vcard_nickname"], street=args["vcard_address"], city=args["vcard_city"], region=args["vcard_state"], zipcode=args["vcard_zipcode"], country=args["vcard_country"], birthday=args["vcard_birthday"], email=args["vcard_email"], phone=args["vcard_phone"], fax=args["vcard_fax"], memo=args["vcard_memo"])
    elif selected_tab == "tab_mecard":
        data = helpers.make_mecard_data(name=args["mecard_name"], reading=args["mecard_kananame"], nickname=args["mecard_nickname"], houseno=args["mecard_address"], city=args["mecard_city"], prefecture=args["mecard_state"], zipcode=args["mecard_zipcode"], country=args["mecard_country"], birthday=args["mecard_birthday"], email=args["mecard_email"], phone=args["mecard_phone"], memo=args["mecard_memo"])
    elif selected_tab == "tab_sms":
        data = f'smsto:{args["sms_number"]}:{args["sms_message"]}'
    elif selected_tab == "tab_email":
        data = helpers.make_make_email_data(to=args["email_address"], subject=args["email_subject"], body=args["email_body"])
    elif selected_tab == "tab_geo":
        data = f'geo:{"{0:.8f}".format(args["geo_latitude"]).rstrip(".0")},{"{0:.8f}".format(args["geo_longitude"]).rstrip(".0")}'
    else:
        data = args["text"]
    
    try: 
        qrcode = segno.make(data, micro=args["setting_micro"], error=args["setting_error_correction"], boost_error=args["setting_boost_error_correction"])
    except segno.encoder.DataOverflowError:
        qrcode = segno.make(data, micro=False, error=args["setting_error_correction"], boost_error=args["setting_boost_error_correction"])
    out = io.BytesIO()
    qrcode.save(out, kind='png', scale=args["setting_scale"], border=args["setting_border"], dark=args["setting_dark"], light=args["setting_light"])
    return Image.open(out)

def on_ui_tabs():
    with gr.Blocks() as ui_component:
        inputs = {}
        with gr.Row():
            with gr.Column():
                with gr.Tab("Text") as tab_text:
                    inputs["text"] = gr.Textbox(show_label=False, lines=3)

                with gr.Tab("WiFi") as tab_wifi:
                    inputs["wifi_ssid"] = gr.Text(label="SSID")
                    inputs["wifi_hidden"] = gr.Checkbox(False, label="Hidden SSID")
                    inputs["wifi_password"] = gr.Text(label="Password")
                    inputs["wifi_security"] = gr.Radio(value="None", label="Security", choices=["None", "WEP", "WPA"])

                with gr.Tab("vCard") as tab_vcard:
                    inputs["vcard_name"] = gr.Text(label="Name")
                    inputs["vcard_displayname"] = gr.Text(label="Display Name")
                    inputs["vcard_nickname"] = gr.Text(label="Nickname")
                    inputs["vcard_address"] = gr.Text(label="Address")
                    with gr.Row():
                        inputs["vcard_city"] = gr.Text(label="City")
                        inputs["vcard_state"] = gr.Text(label="State")
                    with gr.Row():
                        inputs["vcard_zipcode"] = gr.Text(label="ZIP Code")
                        inputs["vcard_country"] = gr.Dropdown(label="Country", allow_custom_value=True, choices=constants.countries)
                    inputs["vcard_birthday"] = gr.Text(label="Birthday")
                    inputs["vcard_email"] = gr.Text(label="Email")
                    inputs["vcard_phone"] = gr.Text(label="Phone")
                    inputs["vcard_fax"] = gr.Text(label="Fax")
                    inputs["vcard_memo"] = gr.Text(label="Memo")

                with gr.Tab("MeCard") as tab_mecard:
                    inputs["mecard_name"] = gr.Text(label="Name")
                    inputs["mecard_kananame"] = gr.Text(label="Kana Name")
                    inputs["mecard_nickname"] = gr.Text(label="Nickname")
                    inputs["mecard_address"] = gr.Text(label="Address")
                    with gr.Row():
                        inputs["mecard_city"] = gr.Text(label="City")
                        inputs["mecard_state"] = gr.Text(label="State")
                    with gr.Row():
                        inputs["mecard_zipcode"] = gr.Text(label="ZIP Code")
                        inputs["mecard_country"] = gr.Dropdown(label="Country", allow_custom_value=True, choices=constants.countries)
                    inputs["mecard_birthday"] = gr.Text(label="Birthday")
                    inputs["mecard_email"] = gr.Text(label="Email")
                    inputs["mecard_phone"] = gr.Text(label="Phone")
                    inputs["mecard_memo"] = gr.Text(label="Memo")

                with gr.Tab("SMS") as tab_sms:
                    inputs["sms_number"] = gr.Text(label="Number")
                    inputs["sms_message"] = gr.Textbox(label="Message", lines=3)

                with gr.Tab("Email") as tab_email:
                    inputs["email_address"] = gr.Text(label="Address")
                    inputs["email_subject"] = gr.Text(label="Subject")
                    inputs["email_body"] = gr.Textbox(label="Message", lines=3)

                with gr.Tab("Location") as tab_geo:
                    with gr.Row():
                        inputs["geo_latitude"] = gr.Number(0, label="Latitude", elem_id="qrcode_geo_latitude")
                        inputs["geo_longitude"] = gr.Number(0, label="Longitude", elem_id="qrcode_geo_longitude")

                with gr.Accordion("Settings", open=False):
                    inputs["setting_scale"] = gr.Slider(label="Scale", minimum=1, maximum=50, value=10, step=1)
                    inputs["setting_border"] = gr.Slider(label="Border", minimum=0, maximum=10, value=4, step=1)
                    with gr.Row():
                        inputs["setting_dark"] = gr.ColorPicker("#000000", label="Dark Color")
                        inputs["setting_light"] = gr.ColorPicker("#ffffff", label="Light Color")
                    inputs["setting_error_correction"] = gr.Radio(value="L", label="Error Correction Level", choices=["L", "M", "Q", "H"])
                    with gr.Row():
                        inputs["setting_boost_error_correction"] = gr.Checkbox(True, label="Boost Error Correction Level")
                        inputs["setting_micro"] = gr.Checkbox(False, label="Micro QR Code")

                button_generate = gr.Button("Generate", variant="primary")

            with gr.Column():
                output = gr.Image(interactive=False, show_label=False, type="pil", elem_id="qrcode_output").style(height=480)
                with gr.Row():
                    send_to_buttons = generation_parameters_copypaste.create_buttons(["img2img", "inpaint", "extras"])
                    for tabname, button in send_to_buttons.items():
                        generation_parameters_copypaste.register_paste_params_button(generation_parameters_copypaste.ParamBinding(paste_button=button, tabname=tabname, source_image_component=output))
                with gr.Row(visible=controlnet_active):
                    sendto_controlnet_txt2img = gr.Button("Send to ControlNet (txt2img)")
                    sendto_controlnet_img2img = gr.Button("Send to ControlNet (img2img)")
                    control_net_max_models_num = opts.data.get('control_net_max_models_num', 1)
                    sendto_controlnet_num = gr.Dropdown([str(i) for i in range(control_net_max_models_num)], label="ControlNet Unit", value="0", interactive=True, visible=(control_net_max_models_num > 1))
                    sendto_controlnet_txt2img.click(None, [output, sendto_controlnet_num], None, _js="(i, n) => {sendToControlnet(i, 'txt2img', n)}", show_progress=False)
                    sendto_controlnet_img2img.click(None, [output, sendto_controlnet_num], None, _js="(i, n) => {sendToControlnet(i, 'img2img', n)}", show_progress=False)

        selected_tab = gr.State("tab_text")
        input_keys = gr.State(list(inputs.keys()))

        button_generate.click(generate, [selected_tab, input_keys, *list(inputs.values())], output, show_progress=False)

        tab_text.select(lambda: "tab_text", None, selected_tab)
        tab_wifi.select(lambda: "tab_wifi", None, selected_tab)
        tab_vcard.select(lambda: "tab_vcard", None, selected_tab)
        tab_mecard.select(lambda: "tab_mecard", None, selected_tab)
        tab_sms.select(lambda: "tab_sms", None, selected_tab)
        tab_email.select(lambda: "tab_email", None, selected_tab)
        tab_geo.select(lambda: "tab_geo", None, selected_tab)

        return [(ui_component, "QR Code", "qrcode_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)