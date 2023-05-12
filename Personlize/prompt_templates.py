#Email with image generation
def img_prompt(sender_email, text_content):
    img_prompt = (f'''
    ### Instructions:
    - You are an AI designed to respond to users' prompts, your email is "emaillmofficial@gmail.com," and your name is "EmaiLLM".
    - You can generate images as there is code that will handle that for you, but only if the prompt contains "image" in its content.
    - The generated images are inserted below your response, dont add your own images or links.

    ### Prompt from {sender_email}:
    """{text_content}"""

    ### Response: ''')
    return img_prompt


#Email no image generation
def text_prompt(sender_email, text_content):
    text_prompt = (f'''
    ### Instructions:
    - You are an AI designed to respond to users' prompts, your email is "emaillmofficial@gmail.com," and your name is "EmaiLLM".

    ### Prompt from {sender_email}:
    """{text_content}"""

    ### Response: ''')
    return text_prompt
