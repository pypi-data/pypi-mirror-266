import gradio as gr
from gradio_log import Log
import os


with open("./test.log", "wb") as f:
    # write some random log to f, with colored and uncolored text
    f.write(b"[INFO] Everything is fine.\n")
    f.write(b"\x1b[34m[DEBUG] Debugging information.\x1b[0m\n")
    f.write(b"\x1b[32m[SUCCESS] Task completed successfully.\x1b[0m\n")
    f.write(b"\x1b[33m[WARNING] Something is not right.\x1b[0m\n")
    f.write(b"\x1b[31m[ERROR] Unexpected error occured.\x1b[0m\n")


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            Log("./test.log")
        with gr.Column(scale=1):
            Log(
                "./test.log",
                dark=True,
                tail=4,
                label="dark mode, read from last 4 lines of log",
            )


if __name__ == "__main__":
    demo.launch()
