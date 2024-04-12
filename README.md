> [!WARNING]
> I don't play Lost Ark anymore but the bot actually work.
> You can only fish but your game must be in French.
> To run the bot you need to run the code. There is no executable.
> I'm not a Python developer so I know my code is not efficient. __Feel free to do pull request__ and complete this damn bot.

# Lost Ark trade skills utility tool
A Lost Ark trade skills utility tool using Python, OpenCV and Tesseract OCR.

Fishing in Lost Ark is one the most annoying/boring things you have to do in the game. But some of us may don't have time to farm fish and prefer do raids for golds (understandable) and do Una tasks instead. That's how this utility comes in.


# Disclaimers
This project is purely educational. I'm not responsible about what you will do with this utility tool within your game account. If you get ban, it will be entirely your fault. I give you the candy. You have the choice to take it or not.

![Choose](https://pyxis.nymag.com/v1/imgs/4db/9a9/78f0f50285dd11bef4946bc47283e49281-pills-lede.rhorizontal.w700.jpg)


# What the utility tool can do ?
## Fishing
- Auto fishing
- Auto play mini-game:
    - Focus orange zone to get more valuables (success not guaranted) (`Default`)
    - Focus yellow zone because its easier
- Choose a fishing stategy:
    - Simply use a fishing rod for both fishing and mini-game (`Default`)
    - Switch between 2 fishing rods, one for fishing and the other for mini-game
- Auto repair tools
- Repair strategy
    - Repair rod every X usages (`Default: 10`) ❗ **Crystalline Aura required**
    - Repair rod when it can't be used anymore ❗ **Crystalline Aura required**
    - No repair
- Stops when you don't have enough Work Energy

## Mining
TODO
## Gathering
TODO
## Hunting
TODO
## Excavating
TODO


# Installation
## Download
Download last version of the utility tool [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ).

## Prerequisites
### In utility tool
- Open the tool, and click on **Install OCR**. This will download and install _Tesseract OCR_ in the same folder of the utility tool executable. _Tesseract OCR_ is an tool that help to recognize text on image.
- Check whether the keybindings defined by default correspond to your in-game keybindings otherwise change it.
### In-game
- Language **MUST BE** set to **French** (Mandatory at the moment, other languages will be available in futur versions)
- Resolution screen **MUST BE 1920x1080** (Mandatory at the moment, other resolutions will be available in futur versions if needed)
- Be sure to have the camera **fully zoomed out**
- And for some action (see [this section](#What-the-utility-tool-can-do-?)), **Crystalline Aura** is required

# How to use
## Fishing
1. Run Lost Ark
2. Go to a fishing spot
3. Click on **Run** in the utility tool


# To developers

## Requirements
- Python 3
- Tesseract OCR 5 (in my case I have installed v5.0.0.20211201). Also check if Tesseract OCR has been added to your `PATH`. If not add it or set executable location path in the code with `pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'`

## Setup
1. Install all required libraries `pip install -r requirements.txt`
2. Run utility tool `python main.py`

## Tools
- [HSV range tool](https://github.com/hariangr/HsvRangeTool) : Use to find HSV range easily
