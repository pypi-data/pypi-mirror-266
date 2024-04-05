#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 00:45:33 2024

@author: vivekdagar
"""
import json
import os
import platform
from os import system
from prettytable import PrettyTable


def get_stats_file_path():
    if os.name == 'posix':  # Linux
        return os.path.expanduser("~/Documents/TicTacAI/scores.json")
    elif os.name == 'nt':  # Windows
        return os.path.expanduser("~\\Documents\\TicTacAI\\scores.json")
    raise Exception()


def clean():
    os_name = platform.system().lower()
    if 'windows' in os_name:
        system('cls')
    else:
        system('clear')


class Statistics:
    def __init__(self):
        self.stats_file = get_stats_file_path()
        self.stats = self.load_statistics()

    def load_statistics(self):
        if not os.path.exists(self.stats_file):
            self.create_statistics_file()
        with open(self.stats_file, 'r') as file:
            return json.load(file)

    def create_statistics_file(self):
        stats_directory = os.path.dirname(self.stats_file)
        os.makedirs(stats_directory, exist_ok=True)  # Create directory if it doesn't exist
        initial_stats = {"total_matches": 0, "player_wins": 0, "player_wins_vs_computer": 0,
                         "player_wins_vs_human": 0, "draws": 0}
        with open(self.stats_file, 'w') as file:
            json.dump(initial_stats, file)

    def save_statistics(self):
        with open(self.stats_file, 'w') as file:
            json.dump(self.stats, file)

    def update_statistics(self, result, flag):
        if flag:
            self.stats["total_matches"] += 1
        if "Player 1 wins" in result:
            self.stats["player_wins"] += 1
        if result == "Player 1 wins against Computer":
            self.stats["player_wins_vs_computer"] += 1
        elif result == "Player 1 wins against Human":
            self.stats["player_wins_vs_human"] += 1
        elif result == "Draw":
            self.stats["draws"] += 1
        self.save_statistics()

    def display_statistics(self):
        clean()
        table = PrettyTable()
        table.field_names = ["Statistic", "Value"]
        table.add_row(["Total Matches", self.stats["total_matches"]])
        table.add_row(["Player 1 Total Wins", self.stats["player_wins"]])
        table.add_row(["Player 1 Wins vs Computer", self.stats["player_wins_vs_computer"]])
        table.add_row(["Player 1 Wins vs Human", self.stats["player_wins_vs_human"]])
        table.add_row(["Draws", self.stats["draws"]])
        print("\nPlayer Statistics:")
        print(table)
        print("\n")
