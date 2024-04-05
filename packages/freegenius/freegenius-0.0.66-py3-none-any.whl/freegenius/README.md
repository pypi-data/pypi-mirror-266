# FreeGenius AI

FreeGenius AI is an ambitious project sparked by the pioneering work of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit). It's designed with the primary objective of offering a comprehensive suite of AI solutions that mirror the capabilities of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit). However, FreeGenius AI is remarkably different in that all core features are completely free, and it doesn't require the use of an OpenAI key.

As with [LetMeDoIt AI](https://github.com/eliranwong/letmedoit), FreeGenius AI is designed to be capable of engaging in intuitive conversations, executing codes, providing up-to-date information, and performing a wide range of tasks. It's designed to learn, adapt, and grow with the user, offering personalized experiences and interactions.

# Status

This project is still in early development and testing, not for production yet.

# Beyond LetMeDoIt AI

The genesis of this project stems from our aspiration to augment the capabilities of [LetMeDoIt AI](https://github.com/eliranwong/letmedoit) significantly.

[LetMeDoIt AI](https://github.com/eliranwong/letmedoit) boasts advanced functionalities in both conversational interaction and task execution. However, its fundamental operations rely extensively on OpenAI's function calling capabilities. This reliance has led to a variety of user requests, including:

- Integration with open-source Large Language Models (LLMs), such as those available on [https://huggingface.co](https://huggingface.co). While LetMeDoIt AI currently facilitates chat interactions using open-source models, it does not utilize these models for essential tasks and operations.
- The ability to operate on offline local LLM servers, such as Ollama and Llama.cpp, is highly desirable. Enabling LetMeDoIt AI to function without an internet connection and to be fully self-contained on a local device would be a significant improvement.
- The option to use LetMeDoIt AI without the necessity for OpenAI ChatGPT API keys, addressing concerns related to privacy, cost, or other constraints. In commercial environments, there is a clear preference to avoid transmitting sensitive data to OpenAI servers for processing.
- Enhanced support for Google Gemini API for core functionalities. At present, LetMeDoIt AI utilizes Gemini Pro for chat and vision capabilities. However, due to [limited and inadequate support for function calling](https://github.com/eliranwong/letmedoit/issues/52) within the Gemini API, it has not been leveraged for the core features of LetMeDoIt AI.
- The capability to manage more complex, multi-stage, or multi-step tasks/projects. Our goal is to expand LetMeDoIt AI's ability to automate intricate tasks through the simple application of flexible plugins.

Beyond responding to user requests, the creator of LetMeDoIt AI harbors a vision that, in the near future, everyone will have access to a customizable, tailor-made and personal AI assistant, reminiscent of Iron Man's Jarvis. It is crucial that these personal AI assistants are compatible with standard computer hardware, removing the barrier of requiring expensive technological investments from users. This initiative is geared towards constructing FreeGenius AI that champions compatibility with readily available and affordable computing hardware.

# Goals

The author aims to equip FreeGenius AI, as an AI suite that is able to:

- run offline
- support local LLM servers
- support open-source large language models
- support optional, but not required, OpenAI ChatGPT and Google Gemini Pro API keys
- support current LetMeDoIt AI equivalent features
- devlops strategies plugin framework to execute multi-step generation or task execution
- run with common computer hardwares with reasonable and affordable cost

## For Testing and Contributions

Install FreeGenius AI, by running:

To set up virtual environment (recommended):

> mkdir -p ~/apps/freegenius

> cd ~/apps/freegenius

> python3 -m venv freegenius

> source freegenius/bin/activate

To install:

> pip install freegenius

To run:

> freegenius

We appreciate anyone who help testing / codeing.

Please kindly report of any issues at https://github.com/eliranwong/freegenius/issues

# Supported LLM Backend / Models

LLM Backend is determined by the value of config.llmBackend

Default: 'llamacpp'

Testing:

* [Llama.cpp](https://github.com/ggerganov/llama.cpp) / [Hugging Face models](https://huggingface.co/) + [Ollama Hosted models](https://ollama.com/library)

Remarks: From version 0.0.44, FreeGenius AI supports loading Ollama hosted models with "llamacpp" set as the backend.  It is recommended to use Ollama hosted models with Llama.cpp for two reasons.  First, Llama.cpp-compatible models are easily to be downloaded via Ollama. We added a prompt for user to easily choose models from numeral choices. Second, Llama.cpp loads and responses faster for the same model, compared against Ollama.  The speed advantage of Llama.cpp is more obvious with average hardware.

* [Ollama](https://ollama.com/) / [Ollama Hosted models](https://ollama.com/library)

* [Google Vertex AI](https://cloud.google.com/vertex-ai) / [Gemini Pro & Gemini Pro Vision](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

* [OpenAI API](https://platform.openai.com/) / [ChatGPT models](https://platform.openai.com/docs/models)

* [LetMeDoIt mode](https://github.com/eliranwong/freegenius/wiki/LetMeDoIt-Mode) / [ChatGPT models](https://platform.openai.com/docs/models)

Remarks: To use Ollama hosted models, installation [Ollama](https://ollama.com/) is required.

# How to Change LLM Backend?

https://github.com/eliranwong/freegenius/wiki/Change-LLM-Backend

# How to Change Models?

https://github.com/eliranwong/freegenius/wiki/Change-Model

# How to Set up Google or OpenAI Credentials? [Optional]

https://github.com/eliranwong/freegenius/wiki/Set-up-Optional-Credentials

# Approach to Run Function Calling Equivalent Features Offline with Affordable Hardwares

Currently, [LetMeDoIt AI](https://github.com/eliranwong/letmedoit) core features heavily reply on the strengths of OpenAI function calling features, which offer abilities:

- to organize structured data from unstructured query
- to accept multiple functions in a single guery
- to automatically choose an appropriate function from numerouse available functions specified, by using the "auto" option.

Challenges in Using Function Calling Features Without an OpenAI API Key:

- Many popular open-source AI models lack support for function calling capabilities.
- Utilizing function calling with these open-source models often demands high-end hardware to ensure smooth and timely operation.
- Although a limited number of models, including Gemini Pro and certain open-source options, do offer function calling, their capacity is significantly limited, typically handling only one function at a time. This limitation places them well behind the advanced functionality of OpenAI, which can intelligently and efficiently select from multiple user-specified functions in a single request.
- In our exploratory research and tests, we discovered [a viable workaround](https://medium.com/11tensors/connect-an-ai-agent-with-your-api-intel-neural-chat-7b-llm-can-replace-open-ai-function-calling-242d771e7c79). This method, however, is practical only for those willing to endure a wait of approximately 10 minutes [on a 64GB RAM device without GPU] for the execution of even a simple single task when numerous functions are specified simultaneously.

In essence, no existing solution matches the capabilities of OpenAI's function calling feature. There is a clear need for an innovative and efficient method to implement function calling features with open-source models on standard hardware. After extensive experimentation and overcoming numerous challenges, the author has developed a new approach:

This novel strategy involves breaking down the function calling process into several distinct steps for multiple generations:

1. Intent Screening (optional; config.intent_screening is set to False by default)
2. Tool Selection (config.tool_dependence is introduced from version 0.0.13; read next section)
3. Parameter Extraction
4. Function Execution
5. Chat Extension

This methodology has been found to work effectively with freely available open-source models, even on devices lacking a GPU.

In case you are interested, you may check, for example, [how we implement this approach with Llama.cpp](https://github.com/eliranwong/freegenius/blob/main/package/freegenius/utils/call_llamacpp.py)

We invite [further discussion and contributions](https://github.com/eliranwong/freegenius/issues) to refine and enhance this strategy.

# Tool Dependence

A new config item "tool_dependence" is introduced in FreeGenius AI from version 0.0.13.

This value helps the assistance to determine if a function call plugin is needed.

Its value ranges from 0.0 to 1.0:

* 0.0 means totally independent of function call plugins. Responses are totally depends on models' own abilities or knowledge base
* 1.0 means fually dependent on function call tools that at least a function call plugin, among available tools, is used to extend model's capabilities
* setting a value between 0.0 and 1.0 allow users to customise how they want to depends on function call plugins.

# Welcome Contributions

You are welcome to make contributions to this project by:

* joining the development collaboratively

* donations to show support and invest for the future

Support link: https://www.paypal.me/letmedoitai

# Documentation

Pending ...

Most current features follow https://github.com/eliranwong/letmedoit/wiki

Particularly, plugin structure follows https://github.com/eliranwong/letmedoit/wiki/Plugins-%E2%80%90-Overview

# TODO

https://github.com/eliranwong/freegenius/issues/4