# gradio_app.py
import gradio as gr
import pandas as pd
from .utils import modify_csv, image_to_base64
import importlib.resources as pkg_resources
from . import resources

with pkg_resources.path(resources, "logo.png") as logo_path:
    logo_base64 = image_to_base64(str(logo_path))


logo_base64 = image_to_base64(logo_path)

def display_csv(file):
    df = pd.read_csv(file)
    return df

def export_csv(d):
    d.to_csv("output.csv")
    return gr.File(value="output.csv", visible=True)

custom_css = """
body { background-color: #1f1f1f; }
div { color: white; }
h1 { text-align: center; color: #ffffff; }
label { color: #ffffff; }
input, textarea { background-color: #333333; border-color: #555555; color: white; }
"""

def main():
    with gr.Blocks(css=custom_css) as demo:
        with gr.Row():
            gr.Markdown(f"""
                <div style='background-color: #f0eae3; padding: 10px; text-align: center; border-radius: 10px; margin-bottom: 90px;'>
                    <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="height: 100px; width: 100px; display: block; margin-left: auto; margin-right: auto;">
                </div>
            """)

        with gr.Column():
            csv_input = gr.File(label="Upload CSV File", file_types=['.csv'])
            csv_display = gr.Dataframe()
            csv_output = gr.Dataframe(headers=["Ticket ID",
                        "Customer Name",
                        "Customer Email",
                        "Customer Age",
                        "Customer Gender",
                        "Product Purchased",
                        "Date of Purchase",
                        "Ticket Type",
                        "Ticket Subject",
                        "Ticket Description",
                        "Ticket Status",
                        "Resolution",
                        "Ticket Priority",
                        "Ticket Channel",
                        "First Response Time",
                        "Time to Resolution",
                        "Customer Satisfaction Rating"], type="pandas", col_count=17)
            button = gr.Button("Export")
            csv = gr.File(interactive=False, visible=False)

        button.click(export_csv, csv_display, csv)
        csv_input.change(display_csv, inputs=csv_input, outputs=csv_display)
        csv_input.change(modify_csv, inputs=csv_input, outputs=csv_output)

    demo.launch()

if __name__ == "__main__":
    main()
