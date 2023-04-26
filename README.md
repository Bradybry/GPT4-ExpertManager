# GPT4-ExpertManager

# Readme for PromptParser

This module provides a manager and API wrapper for interacting with large language models to generate prompts and assistant definitions. It relies on the [langchain](https://github.com/langchain/langchain) library as well as the OpenAI and Anthropic APIs.

## Installation
This package is not currently available on PyPI. To install clone the repo and install Langchain, Anthropic, and OpenAI PyPI packages.

You will also need to obtain API keys for [OpenAI](https://openai.com/product) and [Anthropic](https://www.anthropic.com/product) to use their models.

## Usage
To define a new assistant, format an `assistant_definition` in markdown like this:
```markdown
<assistant_definition>
<name>Your Assistant Name</name> 
<role>Description of your assistant's purpose or role</role>
<system_message>A message from your assistant to the user explaining its purpose</system_message>
<example_input>An example user input or query</example_input>  
<example_output>Your assistant's response to the example input</example_output>
</assistant_definition> 
```

You can then generate a new `LanguageExpert` object from this definition using the `parse_assistant_definition()` function:
```python
definition_text = ...  # Your assistant definition markdown
expert = parse_assistant_definition(definition_text)
expert = LanguageExpert(**expert)
```

The `LanguageExpert` object can then be used to generate responses from your assistant model. You can also improve an existing assistant definition using the `improve()` function.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub with any bugs, feature requests, or changes. As is clearly evident I am not a very good programmer but I am a pretty good prompt engineer. I'm hoping to share what I've learned with others and improve both skillsets in the process.
