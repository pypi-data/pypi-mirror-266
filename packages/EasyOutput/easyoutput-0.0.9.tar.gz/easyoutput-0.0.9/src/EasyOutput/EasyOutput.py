from colorama import Fore, Style, Back as bg
from typing import Optional

import colorama

reset = Style.RESET_ALL
brighten = Style.BRIGHT
dim = Style.DIM

def Info_Message(message, highlight: bool = False):  
    """
    Prints a message notifying the user of specific need to know information.
    
    Color: Blue
    
    Highlight: Blue
    """

    if highlight == True:
        print(f"{Fore.BLUE + brighten}Info{reset}: {bg.BLUE + message + reset}")
    elif highlight == False:    
        print(f"{Fore.BLUE + brighten}Info{reset}: {message}")
    
def Error_Message(message, highlight: bool = False):
    """
    Prints a message notifying the user of an error.
    
    Color: Red
    
    Highlight: Red
    """
    if highlight == True:
        print(f"{Fore.RED}Error{reset}: {bg.RED + message + reset}")
    elif highlight == False:
        print(f"{Fore.RED}Error{reset}: {Fore.YELLOW + message + reset}")
    
def Connection_Error_Message(message, highlight: bool = False):
    """
    Prints a message notifying the user of a connection error.
    
    Color: Red
    
    Highlight: Red
    """
    if highlight == True:
        print(f"{Fore.RED}Connection Error{reset}: {bg.RED + message + reset}")
        
    elif highlight == False:    
        print(f"{Fore.RED}Connection Error{reset}: {Fore.YELLOW + message + reset}")
    
def Success_Message(message, highlight: bool = False):
    """
    Prints a message notifying the user of a success.
    
    Color: Bright Green
    
    Highlight: Green
    """
    if highlight == True:
        print(f"{Fore.GREEN + brighten}Success{reset}: {bg.GREEN + message + reset}")
    elif highlight == False:
        print(f"{Fore.GREEN + brighten}Success{reset}: {message}")
    
def Successful_Connection_Message(message, highlight: bool = False):
    """
    Prints a message notifying the user of a successful connection.
    
    Color: Bright Green
    
    Highlight: Green
    """
    if highlight == True:
        print(f"{Fore.GREEN + brighten}Successful Connection{reset}: {bg.GREEN + message + reset}")
    elif highlight == False:
        print(f"{Fore.GREEN + brighten}Successful Connection{reset}: {message}")
    
def Note_Message(message, highlight: bool = False):
    """
    Prints a note notifying the user of something they should be made aware of.
    
    Color: Yellow
    
    Highlight: Yellow
    """
    if highlight == True:
        print(f"{Fore.YELLOW}Note{reset}: {bg.YELLOW + message + reset}")
    elif highlight == False:    
        print(f"{Fore.YELLOW}Note{reset}: {message}")
    
def Warning_Message(message, highlight: bool = False):
    """
    Prints a warning message for the user indicating your code is running.
    
    Color: Yellow
    
    Highlight: Yellow
    """
    if highlight == True:
        print(f"{Fore.YELLOW}Warning{reset}: {bg.YELLOW + message + reset}")    
    elif highlight == False:
        print(f"{Fore.YELLOW}Warning{reset}: {message}")
    
def Title_Print(title, highlight: bool = False):
    """
    Prints a title for grouping lists and anything else you can think of.
    
    Color: Bright Green
    
    Highlight: Green
    """
    if highlight == True:
        print(f"=== {bg.GREEN + brighten + title + reset} ===")    
    elif highlight == False:
        print(f"=== {Fore.GREEN + brighten + title + reset} ===")
     
def Redacted_Message(message, highlight: bool = False):
    """
    Prints redacted message 
    
    Color: Bright Green
    
    Highlight: Red
    """
    if highlight == True:
        print(f"{Fore.RED + brighten}REDACTED{reset}: {bg.RED + message + reset}")    
    elif highlight == False:
        print(f"{Fore.RED + brighten}REDACTED{reset}: {message}")
        
Info_Message("Test")