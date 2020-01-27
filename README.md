### Hare and Hounds
Play Hare and Hounds against computer who's gonna use basic minimax algorithm or improved alpha-beta prunning.

### How to Play
Just run in console and choose the algorithm computer is gonna use and your next move until game is finished.

### About the game
![image-sab](https://upload.wikimedia.org/wikipedia/commons/8/85/Hare_and_Hounds_board.png)
1. There are two players, one representing the hounds and the other represents the hare. Each player takes turn to make a move. The player representing the hounds can only move one hound at one time.
2. The three hounds try to corner the hare and the hare tries to escape to the left of all hounds.
3. The hounds can move up and down, straight forward, or diagonally forward toward the right end of the game board.
4. The hare can move horizontally, vertically, or diagonally in any direction.
5. The hounds win if they "trap" the hare so it can no longer move.
6. The hare wins if it "escapes" to the left of all three hounds.
7. If the hounds move vertically ten times in a row, they are considered to be "stalling" and the hare wins.

### Static evaluation function
```python
def static_evaluation(self, depth):
  winner = self.is_game_over(state=None)
  if winner == HARE_STR:
    return 99 + depth
  elif winner == HOUNDS_STR:
    return -99 - depth
  else:
    return self.get_hare_num_possible_moves() - self.get_hounds_num_possible_moves()
```
Hare is the MAX Player and Hounds is the MIN Players.
The best next move for the hare is where he can maximize(hare possible number of moves - hounds possible number of moves), same for the hounds but being the MIN Player it will try to minimize.
