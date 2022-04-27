import tkinter
import PIL
from functools import partial
from tkinter import *
from tkinter import messagebox
from random import *
from PIL import ImageTk, Image

bg_color = '#B0E0E6'

root = Tk()
root.title("Find the spy!")
root.iconbitmap('img/Spy6.ico')
root.configure(bg=bg_color)

spy_image = []
for i in range(0, 8):
    spy_image.append(ImageTk.PhotoImage(Image.open("img/Spy" + str(i) + ".png").resize((100, 100), Image.ANTIALIAS)))

chooseSpyFrame = Frame(root, bg=bg_color)
chooseSpyFrame.grid(row=0, column=0, rowspan=16)

announcementsFrame = Frame(root, bg=bg_color)
announcementsFrame.grid(row=0, column=1, rowspan=3, columnspan=18, padx=15)

boardFrame = Frame(root, bg=bg_color)
boardFrame.grid(row=4, column=1, rowspan=15, columnspan=15)

rightFrame = Frame(root, bg=bg_color)
rightFrame.grid(row=4, column=16, rowspan=15, columnspan=3)


# Global variables
num_of_spies_to_be_chosen = {1: 5, 2: 2, 3: 2, 4: 1, 5: 1, 6: 1}
board, board_value, spies_to_pick = [], [], []
last_picked = 0
can_card_be_changed = True
points = 0
points_in_row, points_in_col = [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]
row_bonuses, col_bonuses = [], []
cards_to_assign = [1, 1, 1, 1, 1, 1, 1,  2, 2, 2, 2,  3, 3, 3, 3, 3,  4, 4, 4, 4, 4,  5, 5, 5,  6]
flashing_count = 6


def clear_frame(frame):
    for i in frame.winfo_children():
        i.destroy()


def restart_game():
    clear_frame(announcementsFrame)
    clear_frame(rightFrame)
    clear_frame(chooseSpyFrame)
    clear_frame(boardFrame)
    new_game()


class RightMenu:
    # Right menu - Picked card, Last revealed card, Points counter, Reset the game button
    def __init__(self):
        self.last_picked_label = Label(rightFrame, text="Picked card:", font=("Fixedsys", 14), bg=bg_color)
        self.last_picked_label.grid(row=5, column=16)
        self.last_picked_img = Label(rightFrame, image=spy_image[last_picked], bg=bg_color)
        self.last_picked_img.grid(row=6, column=16)

        self.last_revealed_label = Label(rightFrame, text="Last revealed\ncard:", font=("Fixedsys", 14), bg=bg_color)
        self.last_revealed_label.grid(row=8, column=16)
        self.last_revealed_img = Label(rightFrame, image=spy_image[0], bg=bg_color)
        self.last_revealed_img.grid(row=9, column=16)

        self.points_label = Label(rightFrame, text=" Points:", font=("Fixedsys", 20), bg=bg_color)
        self.points_label.grid(row=11, column=16)
        self.points = Label(rightFrame, text=str(points), font=("Fixedsys", 32), bg=bg_color)
        self.points.grid(row=12, column=16, pady=(0, 80))

        self.reset_game_button = Button(rightFrame, text="New game", font=("Fixedsys", 13),
                                        bg=bg_color, command=restart_game)
        self.reset_game_button.grid(row=14, column=16)


right_menu = RightMenu()


class Announcement:
    # Announcements that are displayed at the top of the game
    def __init__(self):
        self.top = Label(announcementsFrame, text="",
                         font=("Fixedsys", 12), bg=bg_color)
        self.top.grid(row=0, column=1, columnspan=8, pady=0)
        self.mid = Label(announcementsFrame, text="Welcome to the battlefield!",
                         font=("Fixedsys", 14), bg=bg_color)
        self.mid.grid(row=1, column=1, columnspan=8, pady=0)
        self.bot = Label(announcementsFrame, text="Pick your first Spy and choose your target!",
                         font=("Fixedsys", 20), bg=bg_color, width=64, fg='#D90000')
        self.bot.grid(row=2, column=1, columnspan=8, pady=0)

    def new_announcement(self, txt):
        self.top.config(text=self.mid['text'])
        self.mid.config(text=self.bot['text'])
        self.bot.config(text=txt)


announcement = Announcement()


class CardOnBoard:
    _five = False
    win_fight = True

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.button = Button(boardFrame, image=spy_image[0],
                             command=partial(reveal_card, self, x, y))
        self.button.grid(row=4 + x, column=1 + y)

    # Define if this card on the board has a five level spy in a neighbourhood
    def five_in_neighbourhood(self):
        for card_num in range(0, 25):
            if self.x - 1 <= board[card_num].x <= self.x + 1 and self.y - 1 <= board[card_num].y <= self.y + 1:
                # and board[card_num] != self - to avoid 5 thinking she has herself in neighbourhood
                if board_value[board[card_num].x][board[card_num].y] == 5 and board[card_num] != self:
                    self._five = True
                    return 1

    # Flashing the button, if it was clicked while having picked weaker spy
    # Also flashing the neighbours with exclamation marks, if there is 5 in neighbourhood
    def flashing(self):
        global flashing_count
        if flashing_count > 0:
            if flashing_count % 2 == 0:
                # There is 5 in neighbourhood - flashing neighbours that are hidden
                if self._five:
                    for card_num in range(0, 25):
                        if self.x - 1 <= board[card_num].x <= self.x + 1 and self.y - 1 <= board[card_num].y <= self.y + 1:
                            if board[card_num].button['relief'] != SUNKEN:
                                board[card_num].button.config(image=spy_image[7])

                # Fight was lost - flashing the card that was challenged and won
                if not self.win_fight:
                    self.button.config(image=spy_image[board_value[self.x][self.y]])

            else:
                if self._five:
                    for card_num in range(0, 25):
                        if self.x - 1 <= board[card_num].x <= self.x + 1 and self.y - 1 <= board[card_num].y <= self.y + 1:
                            if board[card_num].button['relief'] != SUNKEN:
                                board[card_num].button.config(image=spy_image[0])

                if not self.win_fight:
                    self.button.config(image=spy_image[0])
            flashing_count -= 1
            root.after(466, self.flashing)
        else:
            flashing_count = 6


class ChooseTheSpyButton:
    def __init__(self, x):
        self.button = Button(chooseSpyFrame,
                             text="x" + str(num_of_spies_to_be_chosen[x]),
                             font=("Fixedsys", 20), image=spy_image[x],
                             compound=LEFT, command=partial(pick_spy, x))
        self.button.grid(row=3 * (x - 1) + 1, column=0)


def new_game():

    global num_of_spies_to_be_chosen, right_menu, announcement, spies_to_pick, row_bonuses, col_bonuses
    global board, board_value, last_picked, can_card_be_changed, points, points_in_row, points_in_col
    global cards_to_assign, flashing_count

    num_of_spies_to_be_chosen = {1: 5, 2: 2, 3: 2, 4: 1, 5: 1, 6: 1}
    board = []
    board_value = []
    spies_to_pick = []
    last_picked = 0
    can_card_be_changed = True
    points = 0
    points_in_row = [0, 0, 0, 0, 0]
    row_bonuses = []
    points_in_col = [0, 0, 0, 0, 0]
    col_bonuses = []
    cards_to_assign = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 6]
    flashing_count = 6

    announcement = Announcement()
    right_menu = RightMenu()

    # Buttons to choose the spy
    for i in range(1, 7):
        spies_to_pick.append(ChooseTheSpyButton(i))
    choose_spy_label = Label(chooseSpyFrame, text="Pick a spy:", font=("Fixedsys", 14), bg=bg_color)
    choose_spy_label.grid(row=0, column=0)

    # Board cards
    for i in range(0, 5):
        for j in range(0, 5):
            board.append(CardOnBoard(i, j))

    # Hidden board cards' values
    for i in range(0, 5):
        board_value.append([0] * 5)
        for j in range(0, 5):
            rand = randint(0, len(cards_to_assign) - 1)
            board_value[i][j] = cards_to_assign[rand]
            cards_to_assign.remove(cards_to_assign[rand])

    # Empty texts that will be replaced with bonus points if all row or column will be defeated
    for i in range(0, 5):
        row_bonuses.append(Label(boardFrame, text="   ", font=("Fixedsys", 15), bg=bg_color))
        row_bonuses[i].grid(row=4+i, column=15)
        col_bonuses.append(Label(boardFrame, text="   ", font=("Fixedsys", 15), bg=bg_color))
        col_bonuses[i].grid(row=9, column=1+i)


def pick_spy(x):
    global last_picked, can_card_be_changed
    if can_card_be_changed == FALSE:
        messagebox.showinfo("Next mission awaits!", "You can't change a spy until you lose this one!")
    elif can_card_be_changed == TRUE and num_of_spies_to_be_chosen[x] > 0:
        if last_picked != x:
            right_menu.last_picked_img.config(image=spy_image[x])
            last_picked = x


def reveal_card(card, x, y):
    global points, can_card_be_changed, last_picked, end_game

    # win_fight - if the fight was lost, the flashing of the card will be needed
    win_fight = True
    five_got_defeated = False
    ultra_spy_duel = False
    end_game = True

    # fighter - to remember which lvl of spy was challenging the one on the board
    fighter = last_picked

    # User didn't choose a spy he wants to send to a fight
    if last_picked == 0:
        messagebox.showinfo("Choose a Spy!", "You need to choose a Spy first!")
        return 0

    # Ultra Spy - single use, defeats everyone, only him can defeat the enemy's Ultra Spy for 100 pts
    elif last_picked == 6:
        if board_value[x][y] == 6:
            points += 100
            ultra_spy_duel = True
        else:
            points += 10 * board_value[x][y]
        right_menu.points.config(text=str(points))
        card.button.config(image=spy_image[board_value[x][y]],
                           command=nothing, relief=SUNKEN)
        num_of_spies_to_be_chosen[6] = 0
        spies_to_pick[5].button.config(text="x0")
        can_card_be_changed = True
        last_picked = 0
        right_menu.last_picked_img.config(image=spy_image[0])

    # If spy level 5 tries to kill an enemy (strength doesn't matter) with a 5 level spy as a neighbour,
    # it dies thanks to help of enemy 5 lv spy and doesn't kill anyone
    elif last_picked == 5 and card.five_in_neighbourhood() == 1:
        if can_card_be_changed:
            num_of_spies_to_be_chosen[last_picked] = num_of_spies_to_be_chosen[last_picked] - 1
            spies_to_pick[last_picked - 1].button.config(text="x" + str(num_of_spies_to_be_chosen[last_picked]))
        can_card_be_changed = True
        last_picked = 0
        right_menu.last_picked_img.config(image=spy_image[0])
        win_fight = False
        five_got_defeated = True

    # 1-5 level Spy
    else:
        # better/same level spy - killing an enemy and assigning points
        if board_value[x][y] <= last_picked:
            points += 10 * board_value[x][y]
            right_menu.points.config(text=str(points))
            card.button.config(image=spy_image[board_value[x][y]],
                               command=nothing, relief=SUNKEN)
            if can_card_be_changed:
                num_of_spies_to_be_chosen[last_picked] = num_of_spies_to_be_chosen[last_picked] - 1
                spies_to_pick[last_picked - 1].button.config(text="x" + str(num_of_spies_to_be_chosen[last_picked]))
            # better spy
            if board_value[x][y] < last_picked:
                can_card_be_changed = False
            # same level spy - killing an enemy, assigning points, but dying in an even fight
            else:
                can_card_be_changed = True
                last_picked = 0
                right_menu.last_picked_img.config(image=spy_image[0])

        # worse spy
        else:
            right_menu.last_picked_img.config(image=spy_image[0])
            # TODO animation of flashing the card for 2-3 seconds
            # card.flashing - hidden card image is supposed to flash
            win_fight = False
            if can_card_be_changed:
                num_of_spies_to_be_chosen[last_picked] = num_of_spies_to_be_chosen[last_picked] - 1
                spies_to_pick[last_picked - 1].button.config(text="x" + str(num_of_spies_to_be_chosen[last_picked]))
            can_card_be_changed = True
            last_picked = 0
            right_menu.last_picked_img.config(image=spy_image[0])

    # updating Last Revealed Card
    right_menu.last_revealed_img.config(image=spy_image[board_value[x][y]])

    # Adding the point to row and column, checking the bonuses
    if win_fight:
        points_in_row[x] += 1
        if points_in_row[x] == 5:
            row_bonuses[x].config(text="+20")
            points += 20
            right_menu.points.config(text=str(points))

        points_in_col[y] += 1
        if points_in_col[y] == 5:
            col_bonuses[y].config(text="+20")
            points += 20
            right_menu.points.config(text=str(points))

    # Checking if there should be any flashing provided
    if card.five_in_neighbourhood() or (not win_fight):
        card.win_fight = win_fight
        card.flashing()

    # TODO announcements
    if ultra_spy_duel:
        announcement.new_announcement(f"Your Ultra Spy defeated enemy's Ultra Spy!")
    elif fighter == 6:
        announcement.new_announcement(f"Your Ultra Spy defeated enemy's {board_value[x][y]} lvl Spy!")
    elif win_fight and fighter == board_value[x][y]:
        announcement.new_announcement(f"Your and enemy's {fighter} lvl Spies defeated each other!")
    elif win_fight:
        announcement.new_announcement(f"Your {fighter} lvl Spy defeated enemy's {board_value[x][y]} lvl Spy!")
    elif five_got_defeated:
        announcement.new_announcement(f"Your 5 lvl Spy lost due to help of enemy's 5 lvl Spy!")
    else:
        announcement.new_announcement(f"Your {fighter} lvl Spy lost against enemy's {board_value[x][y]} lvl Spy!")

    for key, val in num_of_spies_to_be_chosen.items():
        if val > 0:
            end_game = False
            break

    if end_game and can_card_be_changed:
        if messagebox.askquestion("GG WP!", f"You gathered {points} points!\nDo you wish to play again?") == "yes":
            restart_game()
        else:
            exit()


def nothing():
    pass


new_game()
root.mainloop()
