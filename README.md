
<a id="readme-top"></a>



<h3 align="center">Q - Virtual Assistant</h3>

  <<p align="center"> Your own station's AI virtual assistant. 
  <br />
   <br />
</p>
    Your own station's virtual assistant.
    <br />
    <!-- <a href="https://github.com/github_username/repo_name"><strong>Explore the docs »</strong></a> -->
    <br />
    <br />
    <!-- <a href="https://github.com/github_username/repo_name">View Demo</a> -->
    &middot;
    <!-- <a href="https://github.com/github_username/repo_name/issues/new?labels=bug&template=bug-report---.md">Report Bug</a> -->
    &middot;
    <!-- <a href="https://github.com/github_username/repo_name/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a> -->
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

This project is an experimental personal AI virtual assistant named Q, designed to help you manage tasks on your station.
- Uses **OpenAI GPT-40** for conversational AI.
- Integrates with **Spotify API** to play, stop, and queue music (requires **Spotify Premium account**).
- Provides a toolbox for future extensions (CLI commands, music, and more).
- Voice-controlled: speak commands, recognized via **Google Speech Recognition**, and executed by the AI.
<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
- Python 3.11.0
- Install [Winfetch](https://github.com/lptstr/winfetch) for terminal visualization.
- Install [eSpeak-ng](https://github.com/lptstr/winfetch) for TTS (text-to-speech).
- Spotify Premium account for music-related features.
- Install Windows Terminal from the **Microsoft Store** (recommended to customize appearance for better visualization)
- Microphone (Google recognizer requires a working mic).

### Installation

1. **Obtain OpenAI API Key** from [Github Models Marketplace](https://github.com/marketplace/models) for **OpenAI GPT-4o**.
- Default model in `main.py`:
 ```sh
  OPENAI_MODEL_NAME = "openai/gpt-4o"
  ```

2. **Clone this repository**:
   ```sh
   git clone [https://github.com/github_username/repo_name.git](https://github.com/scarflox/q_virtual_assistant)
   ```
   
3. **Create a Spotify API app** via  [new Spotify API app](https://developer.spotify.com/):
- Redirect URI: `http://127.0.0.1:8888/callback`
- Save the **Client ID** and **Client Secret**.

4. **Install dependencies**

   ```.sh
   pip install -r requirements.txt
   ```

5. **Create `.env` following `.env.example`:
   ```.env
    GITHUB_TOKEN="YOUR_PERSONAL_TOKEN_HERE"
    SPOTIFY_CLIENT_ID="YOUR_CLIENT_ID_HERE"
    SPOTIFY_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
    SPOTIFY_CACHE_PATH="~/.cache"
    OPENAI_API_KEY="YOUR_OPENAI_KEY"
    OPENAI_MODEL_NAME="openai/gpt-4o"
    OPENAI_BASE_URL="https://models.github.ai/inference"
    MIC_INDEX=None
    TRIGGER_WORD="Supporter"
    CONVERSATION_TIMEOUT=30
    SCOPE="user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-private"

   ```
7. (Optional) Change the Git remote URL to avoid accidental pushes:
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # Verify changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
1. Run `start_service.bat` **as administrator**.
- This wil open Windows Terminal, show system metrics at the top, and launch the AI listener.
2. Default mode for this program is chat, if you want to use your microphone, type: /voice.
- If you want to return to chat, type: /chat.
3. You are able to do the following:
- Give commands to the AI.
- If applicable, the AI may invoke tools from the toolbox.
- Responses and tool outputs are read out loud via TTS.

## Important Notes
- Early development: some bugs are expected.
- Make sure all prerequisites are installed and configure correctly.
- Spotify tools require **Premium account**. Non-premium users may encounter errors.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

T1M0R - Discord: t1m0r_

Project Link: [Q - Virtual Assistant.](https://github.com/scarflox/q_virtual_assistant)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
