# ✨ ChatGPT DMenu — Fast AI Assistant at Your Fingertips

**ChatGPT DMenu** is a minimalist AI-powered assistant that brings OpenAI's capabilities directly into your Linux desktop workflow via the fast `dmenu` launcher.

Whether you're rewriting emails, brainstorming, summarizing content, or translating text — just copy the text, hit your dmenu shortcut, and let ChatGPT do the rest. Responses open instantly in Neovim for review and editing. Your clipboard is updated automatically. It’s seamless and efficient.

---

## 🚀 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [💡 Usage](#-usage)
- [📁 Example Config](#-example-config)
- [📄 License](#-license)

---

## ✨ Features

- ⚡️ Invoke ChatGPT from `dmenu` with custom contexts
- 🧠 Rich contextual prompts for different use cases (e.g., Business Email)
- 💬 Dynamic audience, tone, and recipient input for fine-tuned responses
- 🖱️ Output appears instantly in a Neovim popup for fast editing
- 📋 Automatically updates your clipboard with the result
- 🪵 Configurable logging to `/tmp/chatgpt-dmenu.log`
- 🔧 Fully configurable through YAML

---

## 📦 Installation

Make sure you have the following dependencies installed:

- Python 3.10+
- `dmenu`, `xclip`, `nvim`, and a terminal like `alacritty`
- [OpenAI API Key](https://platform.openai.com/account/api-keys)

Then, clone and install the project:

```bash
git clone https://github.com/yourusername/chatgpt-dmenu.git
cd chatgpt-dmenu
pipx install .
```

This will install the CLI tool as chatgpt-dmenu.

## ⚙️ Configuration
Create a configuration file at:
```bash
~/.config/chatgpt-dmenu/config.yaml
```

This file should contain your API key, context definitions, preferred tones, audiences, and other runtime settings.

➡️ An example config file is provided at the root of this repository as config.yaml.
To get started:
```bash
mkdir -p ~/.config/chatgpt-dmenu/
cp config.yaml ~/.config/chatgpt-dmenu/
```
Then open and edit the file with your preferred settings.

## 💡 Usage
1. Copy the text you want to transform or analyze.

2. Run the command:

```bash
chatgpt-dmenu
```
3. Select the context (e.g., "Business Email").
4. Input any dynamic details (audience, tone, recipient).
5. ChatGPT rewrites, edits, or summarizes your content.
6. Neovim opens automatically so you can review and tweak.
7. Clipboard is updated — just paste and go!

> 💡Pro tip: bind chatgpt-dmenu to a shortcut key in your window manager for maximum speed.

## 📁 Example Config
```yaml
api_key: "sk-..."
model: "gpt-4o"
temperature: 0.7
terminal: "alacritty"
log_level: "INFO"
log_file: "/tmp/chatgpt-dmenu.log"

contexts:
  Business Email: |
    You are an expert English copy editor. Fix grammar and improve clarity...
  Creative Writing: |
    Write a creative short paragraph based on the user's input.

audiences:
  - My direct manager
  - Prospective client
  - Conference organizer

tones:
  - Friendly but professional
  - Formal and polite
  - Concise and direct

persons:
  - João
  - Fernanda
  - Dr. Silva
```

## 📄 License
This project is licensed under the [MIT License](LICENSE).
