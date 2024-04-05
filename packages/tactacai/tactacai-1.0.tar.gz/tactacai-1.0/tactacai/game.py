#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import inf as infinity
from random import choice
import platform
import time
from os import system
from tabulate import tabulate
from .statistics import Statistics


def wins(state, player):
    win_state = [
        [state[0][0], state[0][1], state[0][2]],
        [state[1][0], state[1][1], state[1][2]],
        [state[2][0], state[2][1], state[2][2]],
        [state[0][0], state[1][0], state[2][0]],
        [state[0][1], state[1][1], state[2][1]],
        [state[0][2], state[1][2], state[2][2]],
        [state[0][0], state[1][1], state[2][2]],
        [state[2][0], state[1][1], state[0][2]],
    ]
    return [player, player, player] in win_state


def empty_cells(state):
    cells = []
    for x in range(len(state)):
        for y in range(len(state[0])):
            if state[x][y] == ' ':
                cells.append([x, y])
    return cells


def clean():
    os_name = platform.system().lower()
    if 'windows' in os_name:
        system('cls')
    else:
        system('clear')


class Game:
    def __init__(self):
        self.HUMAN = 'X'
        self.COMP = 'O'
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.h_choice = ''
        self.c_choice = ''
        self.score_card = Statistics()

    def wipe_board(self):
        self.board = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
        ]

    def evaluate(self, state):
        if wins(state, self.COMP):
            score = +1
        elif wins(state, self.HUMAN):
            score = -1
        else:
            score = 0

        return score

    def game_over(self, state):
        return wins(state, self.HUMAN) or wins(state, self.COMP)

    def valid_move(self, x, y):
        return [x, y] in empty_cells(self.board)

    def set_move(self, x, y, player):
        if self.valid_move(x, y):
            self.board[x][y] = player
            return True
        return False

    def minimax(self, state, depth, player, alpha, beta):
        if player == self.COMP:
            best = [-1, -1, -infinity]
        else:
            best = [-1, -1, +infinity]

        if depth == 0 or self.game_over(state):
            score = self.evaluate(state)
            return [-1, -1, score]

        for cell in empty_cells(state):
            x, y = cell[0], cell[1]
            state[x][y] = player
            score = self.minimax(state, depth - 1, self.HUMAN if player == self.COMP else self.COMP, alpha, beta)
            state[x][y] = ' '
            score[0], score[1] = x, y

            if player == self.COMP:
                if score[2] > best[2]:
                    best = score
                alpha = max(alpha, best[2])
            else:
                if score[2] < best[2]:
                    best = score
                beta = min(beta, best[2])

            if alpha >= beta:
                break

        return best

    def render(self):
        chars = {'X': self.h_choice, 'O': self.c_choice, ' ': ' '}
        table = [[chars[cell] for cell in row] for row in self.board]

        print(tabulate(table, tablefmt="fancy_grid"))

    def ai_turn(self):
        depth = len(empty_cells(self.board))
        if depth == 0 or self.game_over(self.board):
            return

        clean()
        print(f'Computer turn [{self.c_choice}]')
        self.render()

        if depth == 9:
            x = choice([0, 1, 2])
            y = choice([0, 1, 2])
        else:
            move = self.minimax(self.board, depth, self.COMP, -infinity, infinity)
            x, y = move[0], move[1]

        self.set_move(x, y, self.COMP)
        time.sleep(1)

    def human_turn(self):
        depth = len(empty_cells(self.board))
        if depth == 0 or self.game_over(self.board):
            return

        move = -1
        moves = {
            1: [0, 0], 2: [0, 1], 3: [0, 2],
            4: [1, 0], 5: [1, 1], 6: [1, 2],
            7: [2, 0], 8: [2, 1], 9: [2, 2],
        }

        clean()
        print(f'Human turn [{self.h_choice}]')
        self.render()

        while move < 1 or move > 9:
            try:
                move = int(input('Use numpad (1..9): '))
                coord = moves[move]
                can_move = self.set_move(coord[0], coord[1], self.HUMAN)

                if not can_move:
                    print('Occupied cell')
                    move = -1
            except (EOFError, KeyboardInterrupt):
                print('Bye')
                exit()
            except (KeyError, ValueError):
                print('Bad choice')

    def play2_turn(self):
        depth = len(empty_cells(self.board))
        if depth == 0 or self.game_over(self.board):
            return

        move = -1
        moves = {
            1: [0, 0], 2: [0, 1], 3: [0, 2],
            4: [1, 0], 5: [1, 1], 6: [1, 2],
            7: [2, 0], 8: [2, 1], 9: [2, 2],
        }

        clean()
        print(f'Player 2 turn [{self.c_choice}]')
        self.render()

        while move < 1 or move > 9:
            try:
                move = int(input('Use numpad (1..9): '))
                coord = moves[move]
                can_move = self.set_move(coord[0], coord[1], self.COMP)

                if not can_move:
                    print('Bad move')
                    move = -1
            except (EOFError, KeyboardInterrupt):
                print('Bye')
                exit()
            except (KeyError, ValueError):
                print('Bad choice')

    def symbols(self):
        clean()
        self.h_choice = ''
        self.c_choice = ''

        while self.h_choice != 'O' and self.h_choice != 'X':
            try:
                print('')
                self.h_choice = input('Choose X or O\nChosen: ').upper()
            except (EOFError, KeyboardInterrupt):
                print('Bye')
                exit()
            except (KeyError, ValueError):
                print('Bad choice')

        if self.h_choice == 'X':
            self.c_choice = 'O'
        else:
            self.c_choice = 'X'

    def play_game(self, mode):
        first = ''
        self.wipe_board()
        while first != 'Y' and first != 'N':
            try:
                first = input('Player1/Human is first to start?[y/n]: ').upper()
            except (EOFError, KeyboardInterrupt):
                print('Bye')
                exit()
            except (KeyError, ValueError):
                print('Bad choice')

        while len(empty_cells(self.board)) > 0 and not self.game_over(self.board):
            if first == 'N':
                if mode == 'c':
                    self.ai_turn()
                elif mode == 'h':
                    self.play2_turn()
                first = ''

            self.human_turn()
            if mode == 'c':
                self.ai_turn()
            elif mode == 'h':
                self.play2_turn()

        if wins(self.board, self.HUMAN):
            clean()
            print(f'Human turn [{self.h_choice}]')
            self.render()
            if mode == 'c':
                print('YOU WIN!')
                Statistics().update_statistics("Player 1 wins against Computer", False)
            elif mode == 'h':
                print('PLAYER1 WINS!')
                self.score_card.update_statistics("Player 1 wins against Human", False)
            self.score_card.update_statistics('Updating total', True)  # Total
        elif wins(self.board, self.COMP):
            clean()
            if mode == 'c':
                print(f'Computer turn [{self.c_choice}]')
            else:
                print(f'Player 2 turn [{self.h_choice}]')
            self.render()
            if mode == 'c':
                print('YOU LOSE!')
            elif mode == 'h':
                print('PLAYER2 WINS!')
            self.score_card.update_statistics('Updating total', True)  # Total
        else:
            clean()
            self.render()
            print('DRAW!')
            self.score_card.update_statistics('Draw', False)
            self.score_card.update_statistics('Updating total', True)  # Total
        print("Going back to menu in 3 seconds")
        time.sleep(3)
        clean()
