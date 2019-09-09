rows = 6
columns = 7
board_state = [0] * (rows * columns)


def print_board():
    #create string that will hold boardstate
    output_string = ""
    new_char = ['X', '.', 'O']
    #loop through board
    for index, val in enumerate(board_state):
        if index % columns is 0 and index is not 0:
            output_string += '\n'
        output_string += new_char[val + 1]
            
    print(output_string)


def place_piece(player, column):
    #check if column is full
    if board_state[column] is not 0:
        print('invalid move')
        return False
    
    #assign a value for the player based on player order
    if player % 2 is 0:
        val = 1
    else:
        val = -1
    
    #go through each row, when it encounters a non-empty value in the array, set previous row to the state
    for index, entry in enumerate(board_state[column::columns]):
        k = index * columns + column
        #If it finds a non-zero entry, place token in previous row
        if entry is not 0:
            board_state[k - columns] = val
            return k - columns
        #if it goes through the entirety and only finds zeroes, but it's the last row, place a token
        elif index is rows - 1:
            board_state[k] = val
            return k


def check_if_win(position):
    #Only checks the last move made
    row = position // columns
    col = position % columns

    if check_horizontal(row):
        return True

    elif check_vertical(col):
        return True

    elif check_diagonal_1(row, col):
        return True

    elif check_diagonal_2(row, col):
        return True
    
    else:
        return False


def check_horizontal(row):
    #check entire row
    for i in range(columns - 3):
        tsum = 0
        #add four values next to each other
        for j in range(4):
            tsum += board_state[row * columns + i + j]
        #if their value is 4, they win
        if abs(tsum) is 4:
            return True
    
    return False

def check_vertical(column):
    for i in range(rows - 3):
        tsum = 0
        for j in range(4):
            tsum += board_state[(i+j) * columns + column]
        if abs(tsum) is 4:
            return True
    
    return False

def check_diagonal_1(row, column):
    diag = row + column
    if diag < 3 or diag > (columns + rows - 5):
        return False
    
    if diag < columns:
        start_col = diag
        start_row = 0
    else:
        start_col = columns - 1
        start_row = diag - columns + 1
    
    max_row = rows - start_row

    start_pos = start_row * columns + start_col

    for i in range(min([start_col, max_row]) - 3):
        tsum = 0
        for j in range(4):
            val = start_pos + (i + j) * (columns - 1)
            tsum += board_state[val]
        
        if abs(tsum) is 4:
            return True
    
    return False

def check_diagonal_2(row, column):
    diag = row + (columns - column)

    if diag < 3 or diag > (columns + rows - 5):
        return False
    
    if diag < columns:
        start_col = columns - diag - 1
        start_row = 0
    else:
        start_col = 0
        start_row = diag - columns + 1
    
    max_row = rows - start_row
    max_col = columns - start_col

    start_pos = start_row * columns + start_col

    for i in range(min([max_row, max_col]) - 3):
        tsum = 0
        for j in range(4):
            val = start_pos + (i + j) * (columns + 1)
            tsum += board_state[val]
        
        if abs(tsum) is 4:
            return True
    
    return False
    

    



place_piece(1, 3)
place_piece(2, 4)
place_piece(1, 4)
place_piece(2, 5)
place_piece(1, 6)
place_piece(2, 6)
place_piece(1, 6)
place_piece(2, 5)
place_piece(1, 5)
place_piece(2, 0)
place_piece(1, 6)

print(check_diagonal_1(2,6))
print_board()
    