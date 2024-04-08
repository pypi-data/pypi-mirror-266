[![PyPI](https://img.shields.io/pypi/v/tldrwl.svg)](https://pypi.python.org/pypi/tldrwl)

# tldrwl (too long, didn't read/watch/listen)

## Install

```
pip install tldrwl
```

## Usage

Summarize webpages, Youtube videos, and texts with a single api call

Setup:

```
export OPENAI_API_KEY="<your api key here>"
```

CLI:

```
python3 -m tldrwl '<webpage url | youtube url | text>'
```

Library:

```
from tldrwl.summarize import Summarizer

# Async API
await Summarizer().summarize_async("<webpage url | youtube url | text>")
# Sync API
Summarizer().summarize_sync("<webpage url | youtube url | text>")
```

Example:

```
python3 -m tldrwl 'https://www.youtube.com/watch?v=--khbXchTeE'
```

```
Summary: GPT-4 is an advanced AI system developed by OpenAI that can generate up to 25,000 words of text, eight times more than the previous model, ChatGPT. It can understand images and express logical ideas about them, making it a powerful tool for education and personalized learning. The development of GPT-4 has been focused on making it safer, more aligned, and more useful for society, with internal guardrails around adversarial usage, unwanted content, and privacy concerns. The partnership with Microsoft aims to shape this technology into something that's truly
useful for the world and can improve productivity, ultimately leading to a better quality of life. While limited, GPT-4 is an important step towards highly advanced and capable AI systems, and OpenAI hopes to make it useful to everyone, not just early adopters.
Estimated cost (usd): $0.0016
```

## Features

- [x] Summarize text with a single API call
- [x] Summarize webpages with a single API call
- [x] Summarize Youtube videos with a single API call
- [ ] Summarize basic plain text file with a single API call
- [ ] Summarize rich text file with a single API call
- [ ] Summarize audio with a single API call
- [x] Report number of tokens + cost per request
- [x] Sync APIs
- [x] Async APIs
- [x] CLI
- [x] CI/CD to publish to automatically PyPI

## Caveats

- Requires an OpenAI API key
  - Export to env: `export OPENAI_API_KEY="<your api key here>"`
- Slow
  - Small articles take ~20 seconds, longer articles and videos take a few minutes. There is probably some more optimization to be had.
- Cost
  - Can be expensive - by default, this uses the "gpt-3.5-turbo" model, which is much cheaper than gpt4
  - To minimize cost, the library currently limits the number of input characters to 120,000.

To illustrate speed and cost: [This wikipedia page](https://en.wikipedia.org/wiki/List_of_common_misconceptions) hits the maximum limit:

```
Running async
Summary(text='The Wikipedia page "List of common misconceptions" provides a comprehensive list of popular misconceptions and myths in various fields, including arts and culture, business, food and cooking, history, science and mathematics, and film and television. The page corrects commonly held false beliefs that arise from old wives\' tales, superstitions, pseudoscience, and fallacies, among others. The page is divided into sections that relate to different areas of knowledge with listed misconceptions and concise corrections. The page is dynamic and can be regularly updated by readers with reliable sources, and encourages people to be critical of information presented to distinguish fact from fiction. The article debunks several popular myths across fields, including the belief that Santa Claus\'s current image was created by The Coca-Cola Company, the association of the term "zombie" with beings from the film Dawn of the Dead, and the myth that Eskimos have a disproportionate number of words for snow. It also clarifies that sign languages are not universal, and each country has its own native sign language, and police officers are allowed to lie during undercover work. The page corrects misconceptions related to religion and history, such as Mary\'s immaculate conception, the paternity of Paul the Apostle, and the belief that the First Council of Nicaea established the books of the Bible. Additionally, the page debunks common historical myths, such as the belief that Christopher Columbus believed in a flat Earth and that the Plymouth Colony settlers wore Puritan attire. The page covers several misconceptions related to biology, evolution and paleontology, including the myth that cockroaches are radiation-resistant and that honey bees are essential to human food production. It also clarifies common misconceptions related to healthcare and nutrition, such as the belief that exercise-induced muscle soreness is caused by lactic acid build-up and that covering the head prevents heat loss more effectively than other body parts. The page concludes by emphasizing the importance of distinguishing fact from fiction and being critical of information presented.', num_tokens=30749, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.061498000000000004
Finished async in 108.65759706497192s
Running sync
Summary(text='The Wikipedia page on common misconceptions offers a comprehensive list of erroneous beliefs that people commonly hold in various fields such as arts and culture, business, food and cooking, science, mathematics, history, and more. The entries on the list are written as corrections of the misconceptions rather than statements of the myths themselves, and the page provides concise summaries with links to relevant articles for more elaboration. The page covers a plethora of topics from the history of Santa Claus to the spicy part of chili peppers, from legal tender laws to the tryptophan content of turkey. The page also debunks numerous myths related to film and television, language, and law, among other things. Other articles discussed on the Wikipedia page cover particular topics, such as debunking common misconceptions surrounding notable figures in history and religion, as well as science and evolution. Additional articles cover misconceptions in areas such as computing and the internet, geography, and health and nutrition. Overall, the Wikipedia page on common misconceptions serves as a valuable resource for people interested in exploring and dispelling common untruths across a wide range of fields.', num_tokens=30203, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.060406
Finished sync in 316.76091599464417s
```

## General Approach

OpenAI has a limit on maximum number of tokens per requests, so the following strategy is employed to generate the summaries:

1. Split message into chunks
2. Gather summaries for each chunk
3. Summarize the summaries

## Examples

See `tests/manual` for some examples.

### Setup API key

```
export OPENAI_API_KEY="<REDACTED>"
```

### Text summary

```
┌─jrodal@jrodal-850 tldrwl on  master [!+?] via 🐍 v3.10.6 (.venv) took 2m37s
└─> python3 tests/manual/text_test.py
Running async
Summary(text='The tutorial provides a detailed guide on how to automate the deployment of a Hugo site to GitHub pages using GitHub Actions. The tutorial includes step-by-step instructions on important tasks like committing the blog source to GitHub and enabling GitHub Pages. The tutorial also covers tips and troubleshooting advice making it a helpful resource for anyone looking to automate the deployment of their Hugo site. The steps include following the Hugo Quick Start guide, creating a new repository on Github, enabling Github Pages, and setting up Github Actions to automatically deploy the site. To deploy the Hugo site with Github Actions, users need to create a file named gh-pages.yml, which will contain configuration details. The tutorial also highlights the process for verifying that everything is working, including accessing the site after waiting a few minutes and refreshing the browser in incognito mode if nothing has changed. Overall, the tutorial is a comprehensive resource for anyone looking to automate deployment of their Hugo site using Github Actions.', num_tokens=888, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.001776
Finished async in 21.588400840759277s
Running sync
Summary(text='This tutorial provides a clear and detailed step-by-step guide on how to automate the deployment of a Hugo site to GitHub pages using GitHub Actions. The guide covers all the necessary steps, starting from committing the blog source to GitHub, enabling GitHub pages, and setting up GitHub Actions to automatically deploy the site. The tutorial also includes useful tips and troubleshooting advice, making it an ideal resource for anyone looking to automate the deployment of their Hugo site. The table of contents comprises four steps, namely: Following Hugo Quick Start, Committing Blog Source to Github, Enabling Github Pages, and Deploying Hugo Site with Github Actions. The first step assumes that readers have already gone through the Hugo quick start guide before proceeding. The second step involves creating a new repository on Github and pushing the local repository to Github. The third step entails enabling GitHub Pages, navigating to the repository settings, and clicking the Pages button. In the fourth step, readers are directed to put a file at ".github/workflows/gh-pages.yml," which contains detailed instructions on how to automate the deployment process using GitHub Actions. Finally, readers are advised to verify that everything is working by opening the site on a new browser or going into incognito mode.', num_tokens=944, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.0018880000000000001
Finished sync in 24.399686336517334s
```

### Webpage summary

```
┌─jrodal@jrodal-850 tldrwl on  master [!+?] via 🐍 v3.10.6 (.venv)
└─> python3 tests/manual/webpage_test.py
Running async
Summary(text='This tutorial is a comprehensive guide for deploying a Rocket Rust web application on a Virtual Private Server (VPS). The tutorial covers all the necessary steps and includes helpful tips and troubleshooting advice. It assumes the user is running something based on Debian and covers all the necessary software/packages to download, updating packages, and necessary installations like Certbot and Rust installation. The tutorial covers simple steps to point a domain to a server by creating an A record that points to the IP address allocated to the VPS. It also includes step-by-step instructions on how to set up an Nginx web server and generate self-signed SSL certificates. In addition, the article provides a guide for developers on securely adding secrets to their GitHub actions using encryption. It demonstrates how to execute remote commands using the appleboy/ssh-action tool and discusses how to establish safer and easier SSHing into a VPS by creating an SSH profile that uses RSA keys instead of passwords. The tutorial is adaptable to different VPS providers, and one can also get a free .tk domain from Dot.tk. Furthermore, it includes steps to disable text passwords to remote machines, ensuring only authorized persons can access them. Overall, this tutorial serves as a useful resource for anyone looking to deploy a Rocket Rust web application on a VPS.', num_tokens=3592, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.007184
Finished async in 57.69430732727051s
Running sync
Summary(text='This tutorial provides a comprehensive guide for deploying a Rocket Rust web application on a VPS. The tutorial covers all the essential steps in detail, starting from acquiring a VPS and domain to setting up domain settings, downloading and installing software on a VPS, and compiling the application. Additionally, it includes useful tips and troubleshooting advice, making it an excellent resource for anyone looking to deploy a Rocket Rust web application on a VPS. The tutorial consists of six main steps: acquiring a VPS and domain, setting up domain settings, downloading software on VPS, compiling the application, setting up an Nginx webserver, and CI/CD with Github actions. For each step, the tutorial provides detailed instructions and code snippets to ensure successful deployment. The article also includes a tutorial for securely deploying a project to a VPS using Github Actions and SSH. It emphasizes the use of encrypted secrets for securely storing sensitive information such as VPS host, username, port, and SSH key. It explains how to execute remote commands on the VPS using the appleboy/ssh-action package, specifying the previously stored secrets and the command to be executed. Furthermore, the tutorial provides optional instructions for safer and easier SSHing into a VPS using RSA keys. It provides a step-by-step guide to generating and copying RSA keys, editing the ssh config file, and disabling text passwords to the remote machine for increased security. Overall, the tutorial aims to guide developers through the process of securely and efficiently deploying their projects to a VPS using Github Actions and SSH, while emphasizing the importance of best security practices.', num_tokens=3607, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.007214000000000001
Finished sync in 78.10237240791321s
```

### Youtube Video Summary

```
┌─jrodal@jrodal-850 tldrwl on  master [!+?] via 🐍 v3.10.6 (.venv)
└─> python3 tests/manual/youtube_test.py
Running async
Summary(text='GPT-4 is a highly advanced AI system that can generate up to 25,000 words of text and can understand images and express logical ideas about them. While it is not perfect and can make mistakes, it has the potential to amplify human capabilities and be a helpful assistant in daily life. The most compelling use cases of these technologies will come from starting with a real human need, such as education. GPT-4 can be used as a personalized math tutor, bringing learning to everyone in a way that is personalized to their skill level. The partnership between OpenAI and Microsoft is aimed towards shaping this technology into something that is useful for the world and can ultimately lead to a better quality of life. Even though GPT-4 is highly capable and advanced, the developers are continuously working on making it safer, more aligned, and more useful for society. It is important to encourage as many people as possible to participate in the development and use of GPT-4 in order to learn more about how it can be helpful to everyone.', num_tokens=835, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.00167
Finished async in 25.515004873275757s
Running sync
Summary(text='GPT-4 is a highly advanced and sophisticated tool that can take in and generate up to 25,000 words of text, significantly more than previous versions. It can understand images and express logical ideas about them, making it a powerful tool for various applications. Although it is not perfect and can make mistakes, GPT-4 has enormous potential to amplify what every person is capable of doing. The most compelling use cases for these technologies will come from starting with a real human need. GPT-4 can teach a wide range of subjects and could be used to provide personalized learning to everyone. Its partnership with Microsoft aims to shape the technology into something that is useful for the world, leading to better quality of life. The development of AI technology is still limited, but it is easy to imagine its impact in future generations. As GPT-4 is an advanced AI system, it is important that it is useful to everyone, not just early adopters or people close to technology. OpenAI has put in internal guardrails around adversarial usage, unwanted content, and privacy concerns, and will continue to learn and update the system to make it suitable for society.', num_tokens=860, model=<Model.GPT35TURBO: 'gpt-3.5-turbo'>)
summary.estimated_cost_usd=0.00172
Finished sync in 29.253196239471436s
```

## Contributing

1. Setup a virtual env `python3 -m venv .venv`
2. Activate venv `source .venv/bin/activate`
3. Install requirements to venv `pip install -r requirements.txt`
4. Setup local import path resolution `make develop`
5. You can run `python tldrwl` to trigger the CLI or `python tests/<path to test>` to trigger a test file
