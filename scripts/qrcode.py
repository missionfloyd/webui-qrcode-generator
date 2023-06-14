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

def generate(selected_tab, keys, more_colors, *values):
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
        data = f'geo:{"{0:.8f}".format(args["geo_latitude"]).rstrip("0").rstrip(".")},{"{0:.8f}".format(args["geo_longitude"]).rstrip("0").rstrip(".")}'
    else:
        data = args["text"]

    if more_colors:
        colors = {"alignment_dark": args["setting_dark_align"], "alignment_light": args["setting_light_align"], "data_dark": args["setting_dark_data"], "data_light": args["setting_light_data"], "finder_dark": args["setting_dark_finder"], "finder_light": args["setting_light_finder"],
                  "format_dark": args["setting_dark_format"], "format_light": args["setting_light_format"], "timing_dark": args["setting_dark_timing"], "timing_light": args["setting_light_timing"], "version_dark": args["setting_dark_version"], "version_light": args["setting_light_version"],
                  "dark_module": args["setting_dark_module"], "quiet_zone": args["setting_quiet_zone"], "separator": args["setting_separator"], }
    else:
        colors = {"dark": args["setting_dark"], "light": args["setting_light"]}

    qrcode = segno.make(data, micro=False, error=args["setting_error_correction"], boost_error=False)
    out = io.BytesIO()
    qrcode.save(out, kind='png', scale=args["setting_scale"], border=args["setting_border"], **colors)
    return Image.open(out)

def on_ui_tabs():
    with gr.Blocks() as ui_component:
        inputs = {}
        with gr.Row():
            with gr.Column():
                with gr.Tab("Text") as tab_text:
                    inputs["text"] = gr.Textbox(show_label=False, lines=3, placeholder="Plain text / URL / Custom format")

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
                        inputs["setting_dark"] = gr.ColorPicker("#000000", label="Module Color")
                        inputs["setting_light"] = gr.ColorPicker("#ffffff", label="Background Color")
                    more_colors = gr.Checkbox(False, label="More Colors")
                    with gr.Group(visible=False) as color_group:
                        with gr.Row():
                            inputs["setting_dark_align"] = gr.ColorPicker("#000000", label="Alignment Module")
                            inputs["setting_light_align"] = gr.ColorPicker("#ffffff", label="Alignment Background")
                        with gr.Row():
                            inputs["setting_dark_data"] = gr.ColorPicker("#000000", label="Data Module")
                            inputs["setting_light_data"] = gr.ColorPicker("#ffffff", label="Data Background")
                        with gr.Row():
                            inputs["setting_dark_finder"] = gr.ColorPicker("#000000", label="Finder Module")
                            inputs["setting_light_finder"] = gr.ColorPicker("#ffffff", label="Finder Background")
                        with gr.Row():
                            inputs["setting_dark_format"] = gr.ColorPicker("#000000", label="Format Module")
                            inputs["setting_light_format"] = gr.ColorPicker("#ffffff", label="Format Background")
                        with gr.Row():
                            inputs["setting_dark_timing"] = gr.ColorPicker("#000000", label="Timing Module")
                            inputs["setting_light_timing"] = gr.ColorPicker("#ffffff", label="Timing Background")
                        with gr.Row():
                            inputs["setting_dark_version"] = gr.ColorPicker("#000000", label="Version Module")
                            inputs["setting_light_version"] = gr.ColorPicker("#ffffff", label="Version Background Color")
                        with gr.Row():
                            inputs["setting_dark_module"] = gr.ColorPicker("#000000", label="Dark Module")
                            inputs["setting_quiet_zone"] = gr.ColorPicker("#ffffff", label="Quiet Zone")
                        with gr.Row():
                            inputs["setting_separator"] = gr.ColorPicker("#ffffff", label="Separator")
                    inputs["setting_error_correction"] = gr.Radio(value="H", label="Error Correction Level", choices=["L", "M", "Q", "H"])

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

        button_generate.click(generate, [selected_tab, input_keys, more_colors, *list(inputs.values())], output, show_progress=False)

        tab_text.select(lambda: "tab_text", None, selected_tab)
        tab_wifi.select(lambda: "tab_wifi", None, selected_tab)
        tab_vcard.select(lambda: "tab_vcard", None, selected_tab)
        tab_mecard.select(lambda: "tab_mecard", None, selected_tab)
        tab_sms.select(lambda: "tab_sms", None, selected_tab)
        tab_email.select(lambda: "tab_email", None, selected_tab)
        tab_geo.select(lambda: "tab_geo", None, selected_tab)
        
        more_colors.input(lambda x: gr.update(visible=x), more_colors, color_group)

        return [(ui_component, "QR Code", "qrcode_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)