# Easy Output 
```py 
# How to use 👽
from EasyOutput.EasyOutput import *
```
![PyPI - Version](https://img.shields.io/pypi/v/EasyOutput?style=for-the-badge&logo=pypi&label=EasyOutput&color=55%2C%20117%2C%20169)\
![PyPI - Downloads](https://img.shields.io/pypi/dm/EasyOutput?style=for-the-badge&logo=pypi&label=Monthly%20Downloads&color=358)\
![PyPI - Downloads](https://img.shields.io/pypi/dw/EasyOutput?style=for-the-badge&logo=pypi&label=Weekly%20Downloads&color=358)\
![PyPI - Downloads](https://img.shields.io/pypi/dd/EasyOutput?style=for-the-badge&logo=pypi&label=Daily%20Downloads&color=358)\
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/FrankAustin808/EasyOutput?style=for-the-badge&logo=github)\
![easyoutput](https://i.gyazo.com/e8c1bb4fe08ade9c2ce6856386f48e1f.png)

> [!IMPORTANT]
> I am always updating this and sometimes those updates can go sideways. Please use the [issues](https://github.com/FrankAustin808/EasyOutput/issues/new/choose) section on github to notify me of anything i have missed! If you would like me to add something, please use the [Feature Request](https://github.com/FrankAustin808/EasyOutput/issues/new/choose) option!


## Information
**EasyOutput** consists of easy colored print options without the extra work.

```py
# You can now highlight your message aswell! 
Success_Message("New Highlight!", highlight=True)

# Or keep it og 😄
Success_Message("No Highlight!")
# Same as
Success_Message("No Highlight!", highlight=False)

# As of v0.1.0 you can now change the color of your text.
from EasyOutput.EasyOutput import Colors, Success_Message

Success_Message("EasyOutput", color=Colors.Green)
```

In reality this is nothing special and just simply for my lazy use. You could easily make these yourself by doing:
```py
from colorama import Fore, Style

def Success(message):
    print(f"{Fore.GREEN + Style.BRIGHT}Success{Style.RESET_ALL}: {message}")

print(f"{Fore.GREEN + Style.BRIGHT}Success{Style.RESET_ALL}: {message}")
# and calling it like so

Success("Your Success Message")
```

If you would rather save time instead, you can always download it by entering **pip install EasyOutput** into your terminal! 

## Important Information 🥇
[colorama](https://pypi.org/project/colorama/) and It's creator has done all heavy lifting here please show him some love!

[Jonathan Hartley](https://github.com/tartley)\
[colorama repo](https://github.com/tartley/colorama)

## PYPI

[EasyOutput](https://pypi.org/project/EasyOutput/)


Badges from: [Shields.io](https://shields.io/badges)

<details>
<summary>Change-Log 📝</summary>

[comment]: <> (v0.0.1)
<details>
<summary>v0.0.1</summary>

    ADDED
    - Success Message
    - Error Message
    - Wait Message
</details>

[comment]: <> (v0.0.2)
<details>
<summary>v0.0.2</summary>
    
    ADDED
    - Connection Success Message
    - Connection Error Message

</details>

[comment]: <> (v0.0.3)
<details>
<summary>v0.0.3</summary>
    
    ADDED
    - Function Notes

    FIXED
    - Small Success Message Bugs
</details>

[comment]: <> (v0.0.4)
<details>
<summary>v0.0.4</summary>
    
    ADDED
    - Info Mesage
    - Note Message
</details>

[comment]: <> (v0.0.5)
<details>
<summary>v0.0.5</summary>

    ADDED
    - Title Print

    FIXED
    - Calling issues
</details>

[comment]: <> (v0.0.6)
<details>
<summary>v0.0.6</summary>

    ADDED
    - REDACTED Message

    REMOVED
    - Usless Classes
</details>

[comment]: <> (v0.0.7)
<details>
<summary>v0.0.7</summary>
    
    REMOVED
    - Wait Message 

    ADDED
    - Warning Message

    FIXED
    - imports
</details>

[comment]: <> (v0.0.7.1)
<details>
<summary>v0.0.7.1</summary>

    FIXED
    - 
</details>

[comment]: <> (v0.0.8)
<details>
<summary>v0.0.8</summary>

    ADDED
    - Highlight Message Option!
</details>

[comment]: <> (v0.0.8.1)
<details>
<summary>v0.0.8.1</summary>

    FIXED
    - Leaving all functions at the bottom of the file... IM SORRY
</details>

[comment]: <> (v0.0.9)
<details>
<summary>v0.0.9</summary>

    FIXED
    - Optioanl Highlight!
</details>

[comment]: <> (v0.0.9.1)
<details>
<summary>v0.0.9.1</summary>

    FIXED
    - Info message oddly popping up after every function
</details>

</details>
