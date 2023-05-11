import os
# set the directory where the JSON files are located
directory = 'D:/Documents/Coder/Top_Spotify/data'

# loop through all files in the directory
for filename in os.listdir(directory):

    # open the file and read its contents as a string
    with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
        content = file.read()
        
    # replace all occurrences of 'data' with 'songs'
    updated_content = content.replace('data', 'songs')
        
    # overwrite the original file with the updated content
    with open(os.path.join(directory, filename), 'w', encoding='utf-8') as file:
        file.write(updated_content)