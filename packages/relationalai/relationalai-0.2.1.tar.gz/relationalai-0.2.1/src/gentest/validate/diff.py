import re
import difflib
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# def diff_to_str(a, b):
#     matcher = difflib.SequenceMatcher(None, a, b)
#     output = []
#     for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
#         if opcode == 'equal':
#             output.append(a[a0:a1])
#         elif opcode == 'insert':
#             output.append(Fore.GREEN + b[b0:b1] + Fore.RESET)
#         elif opcode == 'delete':
#             output.append(Fore.RED + a[a0:a1] + Fore.RESET)
#         elif opcode == 'replace':
#             output.append(Fore.RED + a[a0:a1] + Fore.RESET)
#             output.append(Fore.GREEN + b[b0:b1] + Fore.RESET)
#     return ''.join(output)


def tokenize(s):
    # return re.findall(r'\w+|[^\w\s]|\s+', s)
    return re.findall(r'\S+|\s+', s)


def diff_to_str(a, b):
    # Tokenize the input strings while preserving whitespace
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)

    # Create a SequenceMatcher to compare the token lists
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)

    output = []
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            output.extend(tokens_a[a0:a1])
        elif opcode == 'insert':
            output.extend([Fore.GREEN + token + Fore.RESET for token in tokens_b[b0:b1]])
        elif opcode == 'delete':
            output.extend([Fore.RED + token + Fore.RESET for token in tokens_a[a0:a1]])
        elif opcode == 'replace':
            output.extend([Fore.RED + token + Fore.RESET for token in tokens_a[a0:a1]])
            output.extend([Fore.GREEN + token + Fore.RESET for token in tokens_b[b0:b1]])
    return ''.join(output)
