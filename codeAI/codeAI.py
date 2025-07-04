import requests
import json
import gradio as gr

url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json'
}

history = []

def generate_response(prompt):
    history.append(prompt)
    final_prompt = "\n".join(history)

    data = {
        "model": "MrCoder",
        "prompt": final_prompt,
        "stream": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response = response.text
        data = json.loads(response)
        actual_response = data['response']
        return actual_response
    else:
        print("Error:", response.text)
        return "Something went wrong. Please check the server."

def clear_output():
    return ""

with gr.Blocks() as interface:
    # Smaller image at the top (scale=0.3 for small size)
    gr.Image(
        "D:\\python\\AgenticLangChain\\codeAI\\MrCoder.png", 
        show_label=False, 
        show_download_button=False,
        scale=300,
        height=300
    )

    gr.Markdown("## Welcome to MrCoder Assistant")

    gr.Markdown("Type your prompt below and get intelligent code responses from the MrCoder model.")

    with gr.Row():
        prompt_box = gr.Textbox(
            lines=4,
            placeholder="Enter your Prompt",
            label="Your Prompt"
        )

    output_text = gr.Textbox(
        label="Model Response",
        lines=6
    )

    with gr.Row():
        submit_button = gr.Button("Generate Response")
        clear_button = gr.Button("Clear Output")

    submit_button.click(fn=generate_response, inputs=prompt_box, outputs=output_text)
    clear_button.click(fn=clear_output, inputs=None, outputs=output_text)

interface.launch(share=True)  # Use share=True to allow public access
