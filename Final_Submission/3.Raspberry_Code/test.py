# a = ["2","3","4","5","1","23","45"]
# name = 3
# print("hello {}".format("   ".join(a)))
# def check(string):
#     try:
#         int(string)
#         print(int(string))
#         print("Digit")
#     except ValueError:
#         print("Not a Digit")
# check("fa")
# import datetime
# import ipywidgets as widgets
# from IPython.display import display

# today = datetime.date.today()
# print(today.ctime()[11:19])
# a = widgets.FloatText()
# display(a)

values = {"Two" : 2,"Three" : 3,"Four" : 4}
class Card:
    def __init__(self,suit,rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

three_of_clubs = Card("Clubs","Three")
print(three_of_clubs.value)
