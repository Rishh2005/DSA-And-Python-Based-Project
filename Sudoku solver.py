def is_valid(board, row, col, num):
    # Check if the number exists in the current row
    for i in range(9):
        if board[row][i] == num:
            return False
    
    # Check if the number exists in the current column
    for i in range(9):
        if board[i][col] == num:
            return False
    
    # Check if the number exists in the 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    
    return True

def solve_sudoku(board):
    # Find the next empty spot (represented by 0)
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                # Try placing numbers 1 through 9
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        
                        # Recur to fill the rest of the board
                        if solve_sudoku(board):
                            return True
                        
                        # Backtrack
                        board[row][col] = 0
                        
                # If no valid number can be placed, return False (backtrack)
                return False
    
    # If no empty spot is found, the puzzle is solved
    return True

def print_board(board):
    for row in board:
        print(" ".join(str(num) if num != 0 else '.' for num in row))

# Test the Sudoku Solver
if __name__ == "__main__":
    # Example Sudoku board (0 represents an empty cell)
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    print("Original Sudoku Puzzle:")
    print_board(board)
    
    if solve_sudoku(board):
        print("\nSolved Sudoku Puzzle:")
        print_board(board)
    else:
        print("\nNo solution exists.")
