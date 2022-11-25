import gradio as gr
import numpy as np
import torch.multiprocessing as mp
from schedulers import schedulers_names

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)

    from main import inference, MP as model_parallel, MODEL_ID, devices
    prompts = []
    def dream(
        prompt: str,
        *args
    ):
        if not len(prompt.strip()):
            return [], prompts
        images = inference(prompt, *args)
        if not len(prompts) or [prompt] != prompts[-1]:
            prompts.append([prompt])

        return images, prompts
    # default model does not have nsfw safety checker
    enable_nsfw_toggle=not model_parallel and MODEL_ID!="stabilityai/stable-diffusion-2-base"
    demo = gr.Interface(
        fn=dream,
        inputs=[
            gr.Textbox(placeholder="Place your input prompt here and start dreaming!", label="Input Prompt"),
            gr.Slider(1, max(24, len(devices)*2), 1, step=1, label="Number of Images"),
            gr.Slider(1, 200, 50, step=1, label="Steps"),
            gr.Slider(256, 1024, 512, step=64, label="Height"),
            gr.Slider(256, 1024, 512, step=64, label="Width"),
            gr.Slider(0, 20, 7.5, step=0.5, label="Guidance Scale"),
            gr.Number(label="Seed", precision=0),
            # gr.Checkbox(True, label="FP16"),
            # disable nsfw filter in mp mode
            gr.Checkbox(False, label="NSFW Filter", interactive=enable_nsfw_toggle),
            gr.Checkbox(False, label="Low VRAM mode"),
            gr.Dropdown(schedulers_names, value="PNDM", label="Noise Scheduler"),
            gr.Image(type="pil", tool='sketch', label="Input Image")
        ],
        # TODO set prompts as default value 
        outputs=[gr.Gallery(show_label=False).style(grid=2, container=True), gr.Dataframe(col_count=(1, "fixed"),headers=["Prompt History"], interactive=True).style(rounded=True)],
        allow_flagging="never",
        # sample prompt from https://strikingloo.github.io/DALL-E-2-prompt-guide
        examples=[
            ["A digital illustration of a medieval town, 4k, detailed, trending in artstation, fantasy"]
        ],
    )
    demo.launch(share=False)
