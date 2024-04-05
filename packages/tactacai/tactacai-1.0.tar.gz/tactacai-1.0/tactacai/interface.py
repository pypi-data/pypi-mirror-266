#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click

from .game import Game

"""
This script provides a command-line interface for playing Tic Tac Toe.
"""

@click.group()
def tictactoe():
    """
    Command-line interface for playing Tic Tac Toe.
    """
    pass


@tictactoe.command()
def human():
    """
    Command to play Tic Tac Toe against another human player.
    """
    game = Game()
    game.symbols()
    game.play_game('h')


@tictactoe.command()
def ai():
    """
    Command to play Tic Tac Toe against an AI.
    """
    game = Game()
    game.symbols()
    game.play_game('c')


@tictactoe.command()
def scores():
    """
    Command to display game scores.
    """
    Game().score_card.display_statistics()


if __name__ == '__main__':
    tictactoe()
