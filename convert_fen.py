import os

source_folder = "./filter_more/"
destination_folder = "./new_notation/"

count = 0

def decode_fen(fen):
    decoded_fen = ""
    space_encountered = False
    
    for char in fen:
        if char == ' ':
            space_encountered = True
        elif char == '\n':
            space_encountered = False

        if not space_encountered and char.isdigit():
            decoded_fen += "-" * int(char)
        else:
            decoded_fen += char
            
    return decoded_fen

for filename in os.listdir(source_folder):
    source_file = os.path.join(source_folder, filename)
    destination_file = os.path.join(destination_folder, filename)

    with open(source_file, 'r') as file:
        content = file.read()
        decoded_content = decode_fen(content)

    with open(destination_file, 'w+') as file:
        file.write(decoded_content)
    
    if count % 1000 == 0:
        print(count)
    count += 1