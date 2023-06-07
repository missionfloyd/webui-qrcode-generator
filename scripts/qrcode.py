import modules.scripts as scripts
import gradio as gr
import io
import os

from modules import script_callbacks
from PIL import Image
import segno
from segno import helpers

def generate_text(text, is_micro):
    qrcode = segno.make(text, micro=is_micro)
    out = io.BytesIO()
    qrcode.save(out, scale=5, kind='png')
    return Image.open(out)

def generate_wifi(ssid, password, security):
    if security == "None":
        password = security = None

    qrcode = helpers.make_wifi(ssid=ssid, password=password, security=security)
    out = io.BytesIO()
    qrcode.save(out, scale=5, kind='png')
    return Image.open(out)

def generate_geo(latitude, longitude):
    qrcode = helpers.make_geo_data(latitude, longitude)
    out = io.BytesIO()
    qrcode.save(out, scale=5, kind='png')
    return Image.open(out)

def on_ui_tabs():
    with gr.Blocks() as ui_component:
        with gr.Row():
            with gr.Column():
                with gr.Tab("Text"):
                    text = gr.Text(label="Text")
                    micro_code = gr.Checkbox(False, label="Micro QR Code")
                    button_generate_text = gr.Button("Generate", variant="primary")
                with gr.Tab("WiFi"):
                    ssid = gr.Text(label="SSID")
                    password = gr.Text(label="Password")
                    security = gr.Radio(value="None", label="Security", choices=["None", "WEP", "WPA"])
                    button_generate_wifi = gr.Button("Generate", variant="primary")
                with gr.Tab("Coordinates"):
                    with gr.Row():
                        latitude = gr.Number(0, label="Latitude")
                        longitude = gr.Number(0, label="Longitude")
                    button_generate_geo = gr.Button("Generate", variant="primary")

            with gr.Column():
                output = gr.Image(interactive=False, show_label=False).style(height=480)

        button_generate_text.click(generate_text, [text, micro_code], output, show_progress=False)
        button_generate_wifi.click(generate_wifi, [ssid, password, security], output, show_progress=False)
        button_generate_geo.click(generate_wifi, [latitude, longitude], output, show_progress=False)

        return [(ui_component, "QR Code", "qrcode_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)