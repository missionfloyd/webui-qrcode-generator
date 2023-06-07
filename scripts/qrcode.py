import modules.scripts as scripts
import gradio as gr
import io
import os

from modules import script_callbacks
from scripts import constants
from PIL import Image
import segno
from segno import helpers

def generate_text(text, micro, error):
    qrcode = segno.make(text, micro=micro, error=error)
    out = io.BytesIO()
    qrcode.save(out, scale=10, kind='png')
    return Image.open(out)

def generate_wifi(ssid, password, security, hidden):
    if security == "None":
        password = security = None

    qrcode = helpers.make_wifi(ssid=ssid, password=password, security=security, hidden=hidden)
    out = io.BytesIO()
    qrcode.save(out, scale=10, kind='png')
    return Image.open(out)

def generate_geo(latitude, longitude):
    qrcode = helpers.make_geo(latitude, longitude)
    out = io.BytesIO()
    qrcode.save(out, scale=10, kind='png')
    return Image.open(out)

def generate_vcard(name, displayname, nickname, street, city, region, zipcode, country, birthday, email, phone, fax):
    qrcode = helpers.make_vcard(name=name, displayname=displayname, nickname=nickname, street=street, city=city, region=region, zipcode=zipcode, country=country, birthday=birthday, email=email, phone=phone, fax=fax)
    out = io.BytesIO()
    qrcode.save(out, scale=10, kind='png')
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
                    hidden = gr.Checkbox(False, label="Hidden SSID")
                    password = gr.Text(label="Password")
                    security = gr.Radio(value="None", label="Security", choices=["None", "WEP", "WPA"])
                    button_generate_wifi = gr.Button("Generate", variant="primary")
                with gr.Tab("vCard"):
                    name = gr.Text(label="Name")
                    displayname = gr.Text(label="Display Name")
                    nickname = gr.Text(label="Nickname")
                    address = gr.Text(label="Address")
                    with gr.Row():
                        city = gr.Text(label="City")
                        state = gr.Text(label="State")
                    with gr.Row():
                        zipcode = gr.Text(label="ZIP Code")
                        country = gr.Dropdown(label="Country", choices=constants.countries)
                    birthday = gr.Text(label="Birthday")
                    email = gr.Text(label="email")
                    phone = gr.Text(label="Phone")
                    fax = gr.Text(label="Fax")
                    button_generate_vcard = gr.Button("Generate", variant="primary")
                with gr.Tab("Coordinates"):
                    with gr.Row():
                        latitude = gr.Number(0, label="Latitude")
                        longitude = gr.Number(0, label="Longitude")
                    button_generate_geo = gr.Button("Generate", variant="primary")
                with gr.Accordion("Settings", open=False):
                    error_correction = gr.Dropdown(value="L", label="Error Correction Level", choices=["L", "M", "Q", "H"])

            with gr.Column():
                output = gr.Image(interactive=False, show_label=False).style(height=480)

        button_generate_text.click(generate_text, [text, micro_code, error_correction], output, show_progress=False)
        text.submit(generate_text, [text, micro_code, error_correction], output, show_progress=False)
        button_generate_wifi.click(generate_wifi, [ssid, password, security, hidden], output, show_progress=False)
        button_generate_geo.click(generate_wifi, [latitude, longitude], output, show_progress=False)
        button_generate_vcard.click(generate_vcard, [name, displayname, nickname, address, city, state, zipcode, country, birthday, email, phone, fax], output, show_progress=False)

        return [(ui_component, "QR Code", "qrcode_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)