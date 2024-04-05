from gym.envs.registration import register


register(
    id='gym_gui_tictactoe/tictactoe-gui-v0',
    entry_point='gym_gui_tictactoe.envs:TicTacToeEnv',
)