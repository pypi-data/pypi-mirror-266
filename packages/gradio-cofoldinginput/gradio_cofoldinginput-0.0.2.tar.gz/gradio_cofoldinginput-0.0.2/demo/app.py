
import gradio as gr
from gradio_cofoldinginput import CofoldingInput

import json


def predict(input):
    input = json.dumps(input)
    return input

with gr.Blocks() as demo:
    inp=CofoldingInput(label="Input")

    # preinput =  {"chains": [
    #     {
    #         "class": "DNA",
    #         "sequence": "ATGCGT",
    #         "chain": "A"
    #     }
    # ], "covMods":[]
    # }
    # inp2=CofoldingInput(preinput, label="Input prefilled")
    btn = gr.Button("Submit")
    out = gr.HTML()

    btn.click(predict, inputs=[inp], outputs=[out])

if __name__ == "__main__":
    demo.launch()
