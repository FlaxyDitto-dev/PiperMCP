# 🎙️ Piper TTS MCP Server

A lightweight, zero-dependency Model Context Protocol (MCP) server that gives your local AI agents a voice. 

Instead of fighting with complex Python bindings and C++ redistributables, this server uses Python's `subprocess` to act as a smart bridge to the standalone Piper CLI. It features **dynamic voice caching**—meaning it will automatically download voice models from Hugging Face on the fly the first time an AI requests them!

## ✨ Features
* **Zero Pre-installation:** Models are downloaded dynamically to a local `PiperMCP-voices` folder.
* **Fuzzy Matching:** Ask the AI for "a British female voice" or "Ryan", and the MCP will automatically match it to the correct model.
* **Bulletproof Execution:** Bypasses Python dependency hell by utilizing the native Piper CLI binary.
* **Smart Error Handling:** Provides detailed diagnostic tracebacks to the AI so it can self-correct issues.

---

## 🛠️ Prerequisites

Before connecting this to your AI agent, you need to have Python and the Piper standalone executable installed.

1. **Install Python Dependencies:**
   ```bash
   pip install mcp requests
Download the Piper CLI:

Download the standalone Piper executable for your OS (Windows/Mac/Linux) from the official Piper releases page.

Extract the folder and add it to your system's PATH, OR ensure the piper.exe (or piper binary) is accessible globally from your terminal. Test this by opening a terminal and typing piper --help.

Download this Server:

Clone this repository or download piper_mcp.py to a secure location on your hard drive (e.g., C:\mcp-servers\piper_mcp.py).

🚀 Connecting to Your AI Agent
Here is how to install the Piper MCP server on the most popular coding agents.

🔷 OpenCode
OpenCode has a built-in CLI tool for adding local MCP servers.

Open your terminal.

Run the following command (be sure to replace the path with the absolute path to where you saved the script):

Bash
opencode mcp add piper-tts -- python /absolute/path/to/piper_mcp.py
Restart OpenCode.

🔶 Claude Desktop
To add this to Claude Desktop, you need to edit your configuration JSON file.

Open your Claude Desktop configuration file:

Windows: %APPDATA%\Claude\claude_desktop_config.json

Mac: ~/Library/Application Support/Claude/claude_desktop_config.json

Add the server to your "mcpServers" block:

JSON
{
  "mcpServers": {
    "piper-tts": {
      "command": "python",
      "args": [
        "/absolute/path/to/piper_mcp.py"
      ]
    }
  }
}
Restart Claude Desktop.

🟦 Cursor / Windsurf
For IDEs like Cursor and Windsurf, MCP servers are usually added via the UI.

Open Cursor Settings (gear icon) > Features > MCP.

Click + Add new MCP server.

Choose command as the type.

Name it PiperTTS.

For the command, enter python /absolute/path/to/piper_mcp.py.

Click Save and ensure the status shows a green dot (Connected).

🗣️ How to Use It
Once installed, your AI agent automatically knows how to use the server. You can speak to it naturally!

Here are some example prompts you can try:

"Generate an audio file called 'greeting.wav' saying 'My systems are online and ready to write some code!' using the Ryan voice."

"Say 'The background build process has completed successfully' using a British female voice. Save it as 'alert.wav'."

"What text-to-speech voices do you currently have available for download?"

Where do the files go?

Models: The .onnx neural network models are downloaded and cached in a PiperMCP-voices folder directly next to the piper_mcp.py script.

Audio: If you don't provide an absolute path for the output .wav file, the MCP will automatically save the generated audio to your system's Downloads folder to prevent permission errors.

🐛 Troubleshooting
Error: "Piper CLI failed with error: 'piper' is not recognized..."

Cause: The Python script cannot find the piper executable.

Fix: You need to add the folder containing piper.exe to your system's PATH environment variable. Alternatively, you can edit line 111 of piper_mcp.py to point directly to the binary (e.g., "C:/path/to/piper/piper.exe" instead of just "piper").

Error: "Piper finished, but the audio file is empty."

Cause: This usually means the Piper standalone binary crashed during execution.

Fix: Try running echo "test" | piper --model ./PiperMCP-voices/en_US-lessac-medium.onnx --output_file test.wav manually in your terminal to see the exact C++ or hardware error your OS is throwing.
