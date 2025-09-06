import time
import random
import os

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    RAINBOW = ['\033[31m', '\033[33m', '\033[32m', '\033[36m', '\033[34m', '\033[35m']

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, color=Colors.RESET, delay=0.1):
    for char in text:
        print(color + char + Colors.RESET, end='', flush=True)
        time.sleep(delay)

def rainbow_text(text, delay=0.15):
    for i, char in enumerate(text):
        color = Colors.RAINBOW[i % len(Colors.RAINBOW)]
        print(color + char + Colors.RESET, end='', flush=True)
        time.sleep(delay)

def sparkle_effect():
    sparkles = ['✨', '⭐', '🌟', '💫', '⚡', '🎆', '🎇']
    for _ in range(8):
        sparkle = random.choice(sparkles)
        print(Colors.YELLOW + sparkle + ' ', end='', flush=True)
        time.sleep(0.2)
    print(Colors.RESET)

def animated_border():
    print()
    border_lines = [
        '    ╔══════════════════════════╗',
        '    ║                          ║',
        '    ║                          ║',
        '    ╚══════════════════════════╝'
    ]
    for line in border_lines:
        print(Colors.CYAN + line + Colors.RESET)
        time.sleep(0.1)

def main():
    clear_screen()
    
    time.sleep(0.5)
    
    animated_border()
    
    print('\033[3A', end='')  
    print('      ', end='')  
    
    time.sleep(0.3)
    
    rainbow_text('✨ HELLO, WORLD! ✨', 0.12)
    
    print('\n\n')
    
    sparkle_effect()
    
    time.sleep(0.3)
    type_text('    🎉 Welcome to my hello world code! 🎉', Colors.GREEN, 0.06)
    
    print('\n')
    sparkle_effect()
    
    print('\n' + Colors.BOLD + '    Press Ctrl+C to exit' + Colors.RESET)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n' + Colors.YELLOW + '    ✨ Goodbye! ✨' + Colors.RESET)

if __name__ == "__main__":
    main()