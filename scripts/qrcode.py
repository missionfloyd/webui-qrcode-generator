import modules.scripts as scripts
import gradio as gr
import io
import os

from modules import script_callbacks
from PIL import Image
import segno

def generate(data, is_micro):
    qrcode = segno.make(data, micro=is_micro)
    out = io.BytesIO()
    qrcode.save(out, scale=5, kind='png')
    return Image.open(out)

def on_ui_tabs():
    with gr.Blocks() as ui_component:
        with gr.Row():
            with gr.Column():
                text = gr.Text(label="Text")
                micro = gr.Checkbox(False, label="Micro")
                button_generate = gr.Button("Generate", variant="primary")
            with gr.Column():
                output = gr.Image(interactive=False).style(height=480)

        button_generate.click(generate, [text, micro], output)

        return [(ui_component, "QR Code", "qrcode_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)