# Easy Output 
```py 
# How to use 👽
from EasyOutput.EasyOutput import *
```
![PyPI - Version](https://img.shields.io/pypi/v/EasyOutput?style=for-the-badge&logo=pypi&label=EasyOutput&color=55%2C%20117%2C%20169)
![PyPI - Downloads](https://img.shields.io/pypi/dm/EasyOutput?style=for-the-badge&logo=pypi&color=55%2C%20117%2C%20169)

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/FrankAustin808/EasyOutput?style=for-the-badge&logo=github)

![easyoutput](https://i.gyazo.com/e8c1bb4fe08ade9c2ce6856386f48e1f.png)


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

# Information
**EasyOutput** consists of easy colored print options without the hassle of doing
```py
from colorama import Fore, Style

def Success(message):
    print(f"{Fore.GREEN + Style.BRIGHT}Success{Style.RESET_ALL}: {message}")

# and calling it like so

Success("Your Success Message")


# You can now highlight your message aswell! 
Success_Message("New Highlight!", highlight=True)

# Or keep it og 😄
Success_Message("No Highlight!")
# Same as
Success_Message("No Highlight!", highlight=False)
```

In reality this is nothing special and just simply for my lazy use. You could easily make these yourself by doing

If you would rather save time instead, you can always download it by entering **pip install EasyOutput** into your terminal!\
Feel free to use this in any way you like, all I ask is that you show me your project when finished! 😄

[Request a feature](https://github.com/FrankAustin808/EasyOutput/issues/new/choose)\
[Report an issue](https://github.com/FrankAustin808/EasyOutput/issues/new/choose)

**Updating as much as I can!**
# Functions

### Success
**Use:**
```py
Success_Message("EasyOutput")

```
**Shows:**

Success: EasyOutput 

### Error
**Use:**
```py
Error_Message("EasyOutput")

```
**Shows:**

Error: EasyOutput 

## PYPI

[EasyOutput](https://pypi.org/project/EasyOutput/)


Badges from: [Shields.io](https://shields.io/badges)
