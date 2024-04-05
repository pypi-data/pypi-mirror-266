# 😺🚀RoCat

RoCat is a Python library that provides a simple and user-friendly interface for integrating AI services into your projects.

## Installation

You can install RoCat using pip:

​```
pip install rocat
​```

## Usage

How to use it

```python
# main.py
import streamlit as st
import rocat as rc

openai_api_key = "your-api-key-here"
claude_api_key = "your-api-key-here"

st.title("RoCat AI Chatbot Test App")

model = st.selectbox("Select LLM", ["OpenAI", "Claude"])

if model == "OpenAI":
    chatbot = rc.OpenAIChatbot(api_key=openai_api_key, model='gpt-3.5-turbo', max_tokens=512, temperature=0.7)
elif model == "Claude":
    chatbot = rc.ClaudeChatbot(api_key=claude_api_key, model='claude-3-haiku-20240307', max_tokens=512, temperature=0.7)

chatbot.set_system_prompt("you are helpful assistant")

user_prompt = st.text_input("User Input")
if st.button("Generate Response"):
    response = chatbot.generate_response(user_prompt)
    st.write("Assistant:", response)

```

Running in a streamlit environment

```bash
streamlit run main.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/Yumeta-Lab/rocat).

## Acknowledgements

RoCat is built on top of the following libraries:
- [OpenAI](https://openai.com/) - API for AI services
- [Streamlit](https://streamlit.io/) - Framework for building web applications

## Contact

If you have any questions or inquiries, please contact the author:

- Name: Faith6
- Email: root@yumeta.kr