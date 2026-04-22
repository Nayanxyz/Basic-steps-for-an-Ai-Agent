import gradio as gr

def chat_logic(message, history):
    return "You just said: " + message

app = gr.ChatInterface(fn=chat_logic)
app.launch() # for live share=True
