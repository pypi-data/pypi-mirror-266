<br/>
<p align="center">
  <h3 align="center">TacTacAI</h3>

  <p align="center">
    A simple command-line version of the Tic Tac Toe game that allows users to play against each other or against an AI.
    <br/>
    <br/>
  </p>
</p>

![Issues](https://img.shields.io/github/issues/vivekkdagar/TicTacAI) &nbsp; ![License](https://img.shields.io/github/license/vivekkdagar/TicTacAI) &nbsp; ![Python 3 Logo](https://img.shields.io/badge/-Python%203-3776AB?logo=python&logoColor=white) &nbsp; ![Click Logo](https://img.shields.io/badge/-Click-3776AB?logo=python&logoColor=white) &nbsp; ![Tabulate Logo](https://img.shields.io/badge/-Tabulate-3776AB?logo=python&logoColor=white) &nbsp; ![PrettyTable Logo](https://img.shields.io/badge/-PrettyTable-3776AB?logo=python&logoColor=white)


![Workflow Status](https://github.com/vivekkdagar/TicTacAI/actions/workflows/python-publish.yml/badge.svg)&emsp; 
![Workflow Status](https://github.com/vivekkdagar/TicTacAI/actions/workflows/python-package.yml/badge.svg)&emsp;




## Table Of Contents

* [About the Project](#about-the-project)
* [Technical Implementation Highlights](#technical-implementation-highlights)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [License](#license)
* [Acknowledgements](#acknowledgements)

## About The Project

![Screen Shot](https://github.com/vivekkdagar/TicTacAI/blob/main/screenshots/screenshot.png)

## Gameplay

- The game is played on a 3x3 grid.
- Option to choose whether the human player or AI starts the game first. 
- Players take turns marking a cell with their symbol ('X' or 'O').
- To input their symbol, players use the numpad (1 to 9) corresponding to the grid cells as follows:
  
  ```
  1 | 2 | 3
  ---------
  4 | 5 | 6
  ---------
  7 | 8 | 9
  ```

  For example, to place their symbol in the top-left cell, a player would input '1', and for the bottom-right cell, they would input '9'.

- The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row wins the game.
- If all cells are filled and no player has won, the game ends in a draw.

## Technical Implementation Highlights

- Demonstrates a modular code structure that enhances readability, maintainability, and extensibility of the game.

- Showcases robust error handling mechanisms to gracefully handle invalid inputs and unexpected scenarios, enhancing user experience and software reliability.

- Scalability: Extendable codebase for future feature additions or modifications.


## Getting Started

To get started with this project, you have two options:

1. **Using PyPI**: Install the package directly from the Python Package Index (PyPI) using pip. PyPI always provides stable and tested versions.
2. **Local Build**: Build and install the package locally. Local builds may contain the newest features but could also be unstable and potentially buggy.

Choose the method that best suits your needs and follow the respective instructions below.

### Prerequisites

When using PyPI, pip automatically handles dependencies, ensuring that all required packages are installed.

For local builds, install dependencies with:

```sh
pip install -r requirements.txt
```

### Installation

#### When using Pypi
```commandline
pip install tictacai
```

#### Building locally

1. Clone the repo

```sh
git clone https://github.com/vivekkdagar/TicTacAI/tree/main
```

2. Go to the project directory

```sh
cd tictacai
```

3. Build the package

```JS
python3 -m build
```

4. Install the package

```commandline
cd dist
pip install *gz
```

## Usage

It provides the following command-line interface:

**1. Play against Human**
```commandline
tictacai human
```
This command starts a game where two humans can play against each other.

**2. Play against AI**
```commandline
tictacai ai
```
This command starts a game where a human can play against the AI.

3. Display Scores
```commandline
tictacai scores
```
This command displays statistics about the game, such as total matches played, player wins, draws, etc.

**One thing to note** is scores are stored in a JSON file in Document/TicTacAI so if it is deleted, scores are reset to 0.

## License

Distributed under the MIT License. See [LICENSE](https://github.com/vivekkdagar/TicTacAI/blob/main/LICENSE.md) for more information.

## Acknowledgements

* [README Generator](https://readme.shaankhan.dev/)
* [ImgShields](https://shields.io/)
