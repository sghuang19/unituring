#!/usr/bin/python

import os
import sys
from time import sleep


# UTM Class
class UTM:

    def __init__(self, tape):
        self.tape = tape
        self.head = 0
        self.state = '0'

    def reset(self):
        self.head = 0
        self.state = '0'

    def init(self):
        # Initialize the machine if necessary
        if self.state == '0' and self.head == 0:
            self.head += 1
            while self.tape[self.head] != '$':
                self.head += 1
            self.head += 1

    def run_step(self):
        # Cross out the current symbol and memorize the state
        self.state = (self.state, self.tape[self.head])
        self.tape[self.head] = -1

        # Go back to the tape head for rules
        while self.tape[self.head - 1] != '$':
            self.head -= 1
        self.head -= 1
        while self.tape[self.head - 1] != '$':
            self.head -= 1

        # Matching the rules
        matched = False
        while self.tape[self.head] != '$':
            # Match the current state
            if self.tape[self.head] == self.state[0]:
                self.head += 1
            else:
                self.head += 5
                continue

            # Match the current symbol
            if self.tape[self.head] == self.state[1]:
                matched = True
                self.head += 1
            else:
                self.head += 4
                continue

            # Load the rules into state
            self.state = (*self.tape[self.head: self.head + 3],)
            break

        # Handle exception
        if not matched:
            print("Transition rule not found for ", end='')
            print(f"state {self.state[0]} and symbol {self.state[1]}.")
            sys.exit(1)

        # Forward the tape head to the previous symbol
        while self.tape[self.head] != -1:
            self.head += 1

        # Conduct the execution
        self.tape[self.head] = self.state[1]
        if self.state[0] == 'L':
            self.head -= 1
        elif self.state[0] == 'R':
            self.head += 1
        self.state = self.state[2]

    def run(self, auto=False, step=1):
        self.init()
        print("Tape head initialized")
        self.display()
        if auto:
            while True:
                self.run_step()
                if self.head < 0 or self.head >= len(self.tape):
                    print("Tape end reached, machine halts.")
                    exit(0)
                sleep(step)
                self.display()
        else:
            # TODO manual control
            pass

    pass

    def display(self):
        width, _ = os.get_terminal_size()
        # width = 80  # for debug only
        print(f"Current state: {self.state}")
        print(f"Tape head: {self.head}")
        half = (width - 1) // 5 // 2 - 1
        print('=' * ((half * 2 + 1) * 5 + 1))
        print('|', end='')
        for i in range(self.head - half, self.head + half + 1):
            if i < 0 or i >= len(self.tape):
                print('xxxx|', end='')
            else:
                print(f'{self.tape[i][:4]:^4}|', end='')
        print()
        print('=' * ((half * 2 + 1) * 5 + 1))
        print(" " * (half * 5 + 1), 'Λ')
        print(" " * (half * 5), '/ \\')
        print()


# Core Functions
def load_tape(path, delim=' ') -> list:
    """
    Load the tape from file
    """
    tape = ['$']
    with open(path, 'r') as f:
        for line in f:
            if line[0] == '#':
                continue
            if delim == ' ':
                tape += line.split()
            else:
                tape += line.split(delim)
    return tape


def DEBUG(*strings):
    print("DEBUG:\t", *strings)


# Script Functions
def usage(status=0, progname=os.path.basename(sys.argv[0])):
    print(f"""
UNITURING v1.0 - Universal Turing Machine Emulator
              by Samuel Huang
Usage: {progname} [-a -d DELIM -s TIME -v -t TAPE]
-a         Toggle automatic running mode, default off.
-d DELIM   Delimiter of the tape file.
-s TIME    Specify the time of each iteration when auto mode toggled,
           1s by default.
-v         Toggle verbose mode, trace the step for checking transition rules.
-t TAPE    The path to the tape file.
""")
    sys.exit(status)


# Main Execution
def main():
    auto = False
    delimiter = ' '
    step = 1
    verbose = False
    tape = []

    arguments = sys.argv[1:]
    if not arguments:
        usage(1)

    while arguments:
        argument = arguments.pop(0)
        if argument[0] == '-':
            if argument == '-a':
                auto = True
            elif argument == '-d':
                delimiter = arguments.pop(0)
            elif argument == '-s':
                step = int(arguments.pop(0))
            elif argument == '-t':
                tape = load_tape(arguments.pop(0), delim=delimiter)
            elif argument == '-v':
                verbose = True
            elif argument == '-h':
                usage(0)
            else:
                print(argument, "detected")
                usage(1)

    utm = UTM(tape)
    utm.run(auto, step)


if __name__ == '__main__':
    main()
