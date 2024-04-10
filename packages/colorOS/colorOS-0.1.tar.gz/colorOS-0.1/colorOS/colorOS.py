"""
    This module helps you format your terminal using ANSI escape codes.
"""
# /--text color code--/
class color():
    """
    This function helps you color text.
    """
    def RGB(R, G, B):
        """
            This function allows you to color text according to RGB color codes.

            example;
                color = colorOS.color.RGB(255, 255, 0)
                print(color + "hi")
        """
        return f'\033[38;2;{R};{G};{B}m'
    def black():
        """
            This function makes the text black.
        """
        return "\033[0;30m"
    def red():
        """
            This function makes the text red.
        """
        return "\033[0;31m"
    def green():
        """
            This function makes the text green.
        """
        return "\033[0;32m"
    def brown():
        """
            This function makes the text brown.
        """
        return "\033[0;33m"
    def blue():
        """
            This function makes the text blue.
        """
        return "\033[0;34m"
    def purple():
        """
            This function makes the text purple.
        """
        return "\033[0;35m"
    def cyan():
        """
            This function makes the text cyan.
        """
        return "\033[0;36m"
    def lightgray():
        """
            This function makes the text light gray.
        """
        return "\033[0;37m"
    def darkgray():
        """
            This function makes the text dark gray.
        """
        return "\033[1;30m"
    def lightred():
        """
            This function makes the text light red.
        """
        return "\033[1;31m"
    def lightgreen():
        """
            This function makes the text light green.
        """
        return "\033[1;32m"
    def yellow():
        """
            This function makes the text yellow.
        """
        return "\033[1;33m"
    def lightblue():
        """
            This function makes the text light blue.
        """
        return "\033[1;34m"
    def lightpurple():
        """
            This function makes the text light purple.
        """
        return "\033[1;35m"
    def lightcyan():
        """
            This function makes the text light cyan.
        """
        return "\033[1;36m"
    def white():
        """
            This function makes the text white.
        """
        return "\033[1;37m"

#  /--text background color code--/ 
class background():
    """
    This function helps us color the background of the text.
    """
    def RGB(R, G, B):
        """
            This function allows you to color the background of the text according to RGB color codes.

            example;
                color = colorOS.background.RGB(255, 255, 0)
                print(color + "hello")
        """
        return f'\033[48;2;{R};{G};{B}m'
    def black():
        """
            This function makes the background of the text black.
        """
        return "\033[0;40m"
    def red():
        """
            This function makes the background of the text red.
        """
        return "\033[0;41m"
    def green():
        """
            This function makes the background of the text green.
        """
        return "\033[0;42m"
    def brown():
        """
            This function makes the background of the text brown.
        """
        return "\033[0;43m"
    def blue():
        """
            This function makes the background of the text blue.
        """
        return "\033[0;44m"
    def purple():
        """
            This function makes the background of the text purple.
        """
        return "\033[0;45m"
    def cyan():
        """
            This function makes the background of the text cyan.
        """
        return "\033[0;46m"
    def lightgray():
        """
            This function makes the background of the text light gray.
        """
        return "\033[0;47m"
    def darkgray():
        """
            This function makes the background of the text dark gray.
        """
        return "\033[1;40m"
    def lightred():
        """
            This function makes the background of the text light red.
        """
        return "\033[1;41m"
    def lightgreen():
        """
            This function makes the background of the text light green.
        """
        return "\033[1;42m"
    def yellow():
        """
            This function makes the background of the text yellow.
        """
        return "\033[1;43m"
    def lightblue():
        """
            This function makes the background of the text light blue.
        """
        return "\033[1;44m"
    def lightpurple():
        """
            This function makes the background of the text light purple.
        """
        return "\033[1;45m"
    def lightcyan():
        """
            This function makes the background of the text light cyan.
        """
        return "\033[1;46m"
    def white():
        """
            This function makes the background of the text white.
        """
        return "\033[1;47m"

#  /--text form code--/
class text():
    '''
        This function helps in editing the format of the text.
    '''
    def hide():
        '''
        This function helps in making the text invisible.
        '''
        return "\033[8m"
    def show():
        '''
        This function helps in making the text visible.
        '''
        return "\033[28m"
    def bold():
        '''
        This function helps in making the text bold.
        '''
        return "\033[1m"
    def faint():
        '''
        This function helps in making the text faint.
        '''
        return "\033[2m"
    def italic():
        '''
        This function helps in making the text italic.
        '''
        return "\033[3m"
    def underline():
        '''
        This function helps in making the text underline.
        '''
        return "\033[4m"
    def blink():
        '''
        This function helps in making the text blink.
        '''
        return "\033[5m"
    def negative():
        '''
        This function helps in making the text negative.
        '''
        return "\033[7m"
    def crossed():
        '''
        This function helps in making the text crossed.
        '''
        return "\033[9m"
    def normal():
        '''
        This function helps in making the text normal.
        '''
        return "\033[22m"
    def closeitalic():
        '''
            This function helps in making the text close italic.
        '''
        return "\033[23m"
    def closeunderline():
        '''
        This function helps in making the text close underline.
        '''
        return "\033[24m"
    def closenegative():
        '''
        This function helps in making the text close negative.
        '''
        return "\033[27m"
    def lettersunderline():
        '''
        This function helps to make the next letter of the text also underline.
        '''
        return '\033[4:1m'
    def letterstopline():
        '''
        This function helps to make the next letter of the text also cross out.
        '''
        return '\033[9:1m'
    def lettersbold():
        '''
        This function helps to make the next letter of the text also bold.
        '''
        return '\033[22m'

# /--text location code--/
def location(row, column):
    '''
        This function helps align text.

        example;
            align = colorOS.location(12, 24)
            print(f"{align} selam")
    '''
    return f"\033[{row};{column}H"

# /--terminal screen code--/
class screen():
    '''
    This function helps you organize the terminal screen.
    '''
    def clear():
        '''
        This function helps us clear the terminal screen.
        '''
        return "\033[2J"
    def rstart():
        '''
        This function also helps us return to the beginning of the terminal screen.
        '''
        return "\033[H"
    def rbase():
        '''
        This function also helps us return to the end on the terminal screen.
        '''
        return "\033[1H"

# /--text align code--/
class align():
    '''
    This function helps us scroll the texts.
    '''
    def right(n):
        '''
        This function helps us scroll text from the right.
        '''
        return f'\033[{n}C'
    def left(n):
        '''
        This function helps us scroll text from the left.
        '''
        return f'\033[{n}D'
    def top(n):
        '''
        This function helps us scroll text from the top.
        '''
        return f'\033[{n}D'
    def bottom(n):
        '''
        This function helps us scroll text from the bottom.
        '''
        return f'\033[nD'
    def textslide(n):
        '''
        This function helps us move the cursor down.
        '''
        return f'\033[{n}S'
    def textdelete(n):
        '''
        this function helps us delete the text
        '''
        return f'\033[{n}K'

# /--terminal size code--/
class terminal():
    '''
        This function helps us determine the terminal size.
    '''
    def size(rows, cols):
        '''
        This function helps us determine the terminal size.

        cols ==> x

        row ==> y

        example;
            size = colorOS.terminal.size(369, 400)
        '''
        return f'\033[8;{rows};{cols}t'

# /--reset--/
def reset():
    '''
    This function helps reset all edits.
    '''
    return "\033[0m"
