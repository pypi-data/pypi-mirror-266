from setuptools import setup, find_packages

setup(
    name='tactacai',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'prettytable~=3.5.0',
        'tabulate~=0.9.0',
        'click~=8.1.7',
        'setuptools~=68.0.0',
        'wheel'
    ],
    entry_points={
        'console_scripts': [
            'tactacai = tactacai.interface:tictactoe',
        ],
    },
    author='Vivek Dagar',
    author_email='vivekdagar2024@gmail.com',
    description='Tic Tac Toe game that allows you to play against a human or an AI powered by Minimax algorithm and '
                'also saves your score.',
    url='https://github.com/vivekkdagar/TicTacAI',
    long_description="""Please refer to the Github for usage guide and more {
    https://github.com/vivekkdagar/TicTacAI}""",
    long_description_content_type='text/markdown',
    license='MIT License',
)
