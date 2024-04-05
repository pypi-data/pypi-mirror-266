from colorama import Fore, Style

def Info_Message(message):
    """
    Prints a message notifying the user of specific need to know information.
    Color: Blue
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.BLUE + Style.BRIGHT}Info{Style.RESET_ALL}: {message}")
    
def Error_Message(message):
    """
    Prints a message notifying the user of an error.
    Color: Red
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.RED}Error{Style.RESET_ALL}: {Fore.YELLOW + message + Style.RESET_ALL}")
    
def Connection_Error_Message(message):
    """
    Prints a message notifying the user of a connection error.
    Color: Red
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.RED}Connection Error{Style.RESET_ALL}: {Fore.YELLOW + message + Style.RESET_ALL}")
    
def Success_Message(message):
    """
    Prints a message notifying the user of a success.
    Color: Bright Green
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.GREEN + Style.BRIGHT}Success{Style.RESET_ALL}: {message}")
    
def Successful_Connection_Message(message):
    """
    Prints a message notifying the user of a successful connection.
    Color: Bright Green
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.GREEN + Style.BRIGHT}Successful Connection{Style.RESET_ALL}: {message}")
    
def Note_Message(message):
    """
    Prints a note notifying the user of something they should be made aware of.
    Color: Yellow
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.YELLOW}Note{Style.RESET_ALL}: {message}")
    
def Wait_Message(message):
    """
    Prints a wait message for the user indicating your code is running.
    Color: White
    Args:
        message (_type_): _description_
    """
    print(f"{Fore.LIGHTWHITE_EX}Wait{Style.RESET_ALL}: {message}")
    
def Title_Print(title):
    """
    Prints a title for grouping lists and anything else you can think of.
    Color: Bright Green
    Args:
        title (_type_): _description_
    """
    print(f"=== {Fore.GREEN + Style.BRIGHT + title + Style.RESET_ALL} ===")
     
def Redacted_Message(message):
    """
    Prints redacted message 
    Color: Bright Green
    Args:
        title (_type_): _description_
    """
    print(f"{Fore.RED + Style.BRIGHT}REDACTED{Style.RESET_ALL}: {message}")