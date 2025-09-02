
<a id="readme-top"></a>



<h3 align="center">Q - Virtual Assistant</h3>

  <p align="center">
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

This project is my own experimentation with making a personal AI virtual assistant for your station,
it currently utilizes OpenAI's gpt-4o model and Spotify's API.
The AI will navigate to ready-to-use tools from a toolbox made to handle different requests (e.g. play a track in spotify, stop current track, CLI tools and more coming)
Communication with Q will be done with voice prompts - User speaks, Google recognizer will identify the text and send it away as a prompt.

<!-- GETTING STARTED -->
## Getting Started

Before we run this project we must run the prerequisites.

### Prerequisites

- Download winfetch from the link below:

* github
  ```sh
  https://github.com/lptstr/winfetch
  ```

- In case you want to utilize the Spotify tools, you must log in with a **Premium Spotify account.** Currently, non-premium accounts are not handled gracefully.
(Also make sure you have Spotify ;))

- From the Microsoft store, download **"Windows Terminal"**, it is advised to changed it's appearance for better graphics and visualization (Color scheme, background transparency)

### Installation

1. Get a free API Key at [Github/marketplace/models]( https://github.com/marketplace/models) (OpenAI GPT-4o)
* In case you wish to use a different model, you will need to edit it in main.py:
* main.py
  ```sh
  model_name = "openai/gpt-4o"
  ```
  
2. Clone the repo
   ```sh
   git clone [https://github.com/github_username/repo_name.git](https://github.com/scarflox/q_virtual_assistant)
   ```
   
3. Make a [new Spotify API app](https://developer.spotify.com/) with the following callback: 
   ```sh
   http://127.0.0.1:8888/callback
   ```
   Select Web API usage, And save the Client ID, and Client Secret.
   
5. Install required packages
   ```.sh
   pip install -r requirements.txt
   ```
6. make a .env file in the format presented in the project files.
   ```.env
   GITHUB_TOKEN="YOUR_PERSONAL_TOKEN_HERE"
   CLIENT_ID="YOUR_CLIENT_ID_HERE"
   LIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
   ```
7. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

When running the program (Make sure it runs with administrator permissions) it will open a Windows terminal prompt, boot up winfetch and start the AI listener as well.
It will instruct you to say `Supporter` to your microphone (Make sure you have a functioning microphone!), After saying the wake-word, The AI will respond and wait
for your next prompt.
As for tool usage; If the AI finds it suitable to utilize one of the tools in the toolbox for a prompt given by the user, it will use it and return the function_return and read it out loud.

## Important
This program is still in very early development and is buggy and unforgiving, make sure you've done all of the prerequisites as necessary.

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
