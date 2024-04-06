# # # # # SECRET_NUMBER = 7
# # # # # user_answer = int(input("Guess a number a number between 1 and 100: "))
# # # # # prev_answer = user_answer
# # # # # attempts = 1
# # # # # while user_answer != SECRET_NUMBER:
# # # # #     if user_answer < 1 or user_answer > 100:
# # # # #         print("FOCUS! I said between 1 and 100")
# # # # #     else:
# # # # #         if user_answer < SECRET_NUMBER:
# # # # #             if user_answer < prev_answer and prev_answer < SECRET_NUMBER:
# # # # #                 print("I told you greater than", prev_answer, "! So greater!")
# # # # #             else:
# # # # #                 print("Wrong, it's greater. Try again: ")
# # # # #         else:   # user_answer > SECRET_NUMBER
# # # # #             if user_answer > prev_answer and prev_answer > SECRET_NUMBER:
# # # # #                 print("I told you lower than ", prev_answer, "! So lower!")
# # # # #             else:
# # # # #                 print("Wrong, it's lower. Try again: ")
# # # # #     attempts = attempts + 1
# # # # #     prev_answer = user_answer
# # # # #     user_answer = int(input())
# # # # # print("You guessed it! It took you", attempts, "tries")
# # # #
# # # # print("1 - Add 3 numbers")
# # # # print("2 - Divide two numbers")
# # # # print("3 - Count from one to a number")
# # # # print("0 - Finish program")
# # # # option = input("Introduce an option: ")
# # # # while option != "0":
# # # #     if option == "1":
# # # #         number1 = int(input("Introduce the first number: "))
# # # #         number2 = int(input("Introduce the second number: "))
# # # #         number3 = int(input("Introduce the third number: "))
# # # #         print("The result is", number1 + number2 + number3)
# # # #     elif option == "2":
# # # #         number1 = float(input("Introduce the first number: "))
# # # #         number2 = float(input("Introduce the second number: "))
# # # #         print("The result is", number1 / number2)
# # # #     elif option == "3":
# # # #         target = int(input("Introduce a number: "))
# # # #         current = 1
# # # #         while current < target:
# # # #             print(current)
# # # #             current += 1
# # # #     print("1 - Add 3 numbers")
# # # #     print("2 - Divide two numbers")
# # # #     print("3 - Count from one to a number")
# # # #     print("0 - Finish program")
# # # #     option = input("Introduce another option: ")
# # #
# # # # list_of_numbers = []
# # # # a_number = int(input("Write a number: "))
# # # # while a_number != 0:
# # # #     list_of_numbers.append(a_number)
# # # #     a_number = int(input("Write a number: "))
# # # # total_sum = 0
# # # #
# # # # if len(list_of_numbers) == 0:
# # # #     print("There are no numbers")
# # # # else:
# # # #     for a_number in list_of_numbers:
# # # #         total_sum += a_number
# # # #     print("The average of the numbers is: " + str(total_sum/len(list_of_numbers)))
# # #
# # # # names = ["Harry", "Laura", "James", "Linda"]
# # # # greetings = ["Hi ", "Hola", "Ciao", "Bonjour"]
# # # #
# # # # for i in range(len(names)):
# # # #     print(greetings[i] + " " + names[i] + "!")
# # #
# # # # def print_area_rectangle(base, height):
# # # #     print(base * height)
# # # #
# # # #
# # # # print_area_rectangle(1, 3)  # Out: 3
# # # # base = 2
# # # # height = 4
# # # # print_area_rectangle(1, 3)  # Out: 3
# # # # print_area_rectangle(base, height)  # Out: 8
# # # # print(base)
# # # # print(height)
# # # # print_area_rectangle()  # ERROR!!
# # # #
# # # def area_rectangle(base, height):
# # #     """
# # #     :param base: a number --> base of the rectangle
# # #     :param height: a --> height of the rectangle
# # #
# # #     This function returns the area of a rectangle with the base and height indicated with the params
# # #     """
# # #     help(area_rectangle)
# # #
# # #
# # # area = area_rectangle(4,2)
# # # print("El area es ", area)
# # # # print(area)
# #
# #
# # def linea_vertical(cara, times):
# #     for i in range(times):
# #         print(cara)
# #
# # def linea_horizontal(char, times):
# #     return char*times
# #
# # resultado = linea_horizontal("s", 5)
# # print(resultado)
# #
# #
#
# # I read the file / Leo el contenido del archivo
# def get_file_lines_ignoring_headings(file_path):
#     """
#     This function receives a file path and returns a list with all the lines in that file
#     excluding the first one, which is supposed to contain headings.
#     Este función recibe una ruta a un archivo y devuelve una lista con todas las líneas del archivo
#     excluyendo la primera, que se supone que debería contener unos encabezados.
#     """
#     a_file = open(file_path)
#     rows = a_file.readlines()
#     a_file.close()
#     return rows[1:]
#
# def get_sentence_of_a_person(person_data_line):
#     """
#     This function expects to receive an str containing data about a person. The different pieces of
#     data are sepparated by ; characters. The function returns a sentence containing all this data.
#     Este función espera recibir un str conteniendo información de una persona. Las distintas piezas
#     de información deberían ir separadas por caracteres ;. La función devuelve una frase con todos los datos.
#     """
#     person_data_line = person_data_line.strip()
#     person_data_list = person_data_line.split(";")
#     pattern = "{} is {} years old and loves eating {} while listening to {}."
#     return pattern.format(person_data_list[0], person_data_list[1], person_data_list[3], person_data_list[2])
#
# data_lines = get_file_lines_ignoring_headings("people.csv")
# for a_person_line in data_lines:
#     print(get_sentence_of_a_person(a_person_line))
#
#

# matrix = [ [1, 2, 3],
#            [4, 5, 6],
#            [7, 8, 9] ]
#
# for i in range(len(matrix)):
#     for j in range(len(matrix[i])):
#         print(matrix[i][j])


# def print_matrix_in_a_nice_way(matrix):
#     for a_row in matrix:
#         line_to_print = ""
#         for a_value in a_row:
#             line_to_print += str(a_value) + "\t"
#         print(line_to_print)
#
#
# matrix1 = [[1,2],[3,4]]
# matrix2 = [[5,6],[7,8]]
#
# matrix_result = [[],[]]
#
# for i in range(len(matrix1)):
#     for j in range(len(matrix1[i])):
#         matrix_result[i].append(matrix1[i][j] + matrix2[i][j])
#
# print_matrix_in_a_nice_way(matrix_result)



def is_board_full(a_board):
    for a_row in a_board:
        for a_position in a_row:
            if a_position == ".":
                return False
    return True

def check_horizontal_win(a_board):
    for a_row in a_board:
        first_position_of_a_row = a_row[0]
        if first_position_of_a_row != ".":
            if a_row[1] == first_position_of_a_row and a_row[2] == first_position_of_a_row:
                return first_position_of_a_row
    return None

def check_vertical_win(a_board):
    for j in range(0,3):
        first_position_of_a_column = a_board[0][j]
        if first_position_of_a_column != ".":
            if a_board[1][j] == first_position_of_a_column and a_board[2][j] == first_position_of_a_column:
                return first_position_of_a_column
    return None

def check_diagonal_win(a_board):
    central_position = a_board[1][1]
    if central_position != ".":
        if a_board[0][0] == central_position and a_board[2][2] == central_position:
            return central_position
        if a_board[0][2] == central_position and a_board[2][0] == central_position:
            return central_position
    return None
def who_won(a_board):
    potential_win = check_horizontal_win(a_board)
    if potential_win != None:
        return potential_win
    potential_win = check_vertical_win(a_board)
    if potential_win != None:
        return potential_win
    potential_win = check_diagonal_win(a_board)
    return potential_win

def print_matrix_in_a_nice_way(matrix):
    for a_row in matrix:
        line_to_print = ""
        for a_value in a_row:
            line_to_print += str(a_value) + "\t"
        print(line_to_print)

def print_board(a_board):
    print("---------")
    print_matrix_in_a_nice_way(a_board)
    print("---------")

def is_a_valid_position(row, column, a_board):
    if row < 0 or row > 2:
        return False
    if column < 0 or column > 2:
        return False
    if a_board[row][column] != ".":
        return False
    return True

def ask_the_user_to_place_a_char(char_to_place, a_board):
    print()
    print("Turn for the", char_to_place, "!")
    row = int(input("Which row? (between 0 and 2): "))
    column = int(input("Which column? (between 0 and 2): "))
    while not is_a_valid_position(row, column, a_board):
        print("You can't place an", char_to_place, "there. Choose again.")
        row = int(input("Which row? (between 0 and 2): "))
        column = int(input("Which column? (between 0 and 2): "))
    a_board[row][column] = char_to_place

def execute_turn(turn_x, a_board):
    if turn_x:
        char_to_place = "X"
    else:
        char_to_place = "O"
    print_board(a_board)
    ask_the_user_to_place_a_char(char_to_place, a_board)


board = [[".", ".", "."],
         [".", ".", "."],
         [".", ".", "."]]



turn_X = True
while not is_board_full(board) and who_won(board) == None:
    execute_turn(turn_X, board)
    turn_X = not turn_X

victory_for = who_won(board)
print_board(board)
if victory_for != None:
    print("Victory for the", victory_for, "!")
else:
    print("Draw!!")



