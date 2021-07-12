import os

cwd = os.getcwd()
dirs = [dir for dir in os.scandir('.') if dir.is_dir()]

fileList = []

# with open('listDownloaded.txt', 'w') as f:
#
#     for dir in dirs:
#         files = [f for f in os.scandir(dir) if f.name.endswith('json')]
#
#         f.write(dir.name + '\n')
#         f.write('    ' + str([f.name for f in files]) + '\n')

for dir in dirs:
    files = [f for f in os.scandir(dir) if f.name.endswith('json')]

    for file in files:
        with open(file) as f:
            lines = f.read().splitlines()
            try:
                if 'REV' not in lines[-6] and '22' not in lines[-5] and '21' not in lines[-4]:
                    print(f'{lines[-6]} {lines[-5]}:{lines[-4]}')
                    print(file.name)
                    fileList.append((file.name, f'{lines[-6]} {lines[-5]}:{lines[-4]}'))
            except:
                fileList.append((file.name, 'ERROR'))

with open('filesCutShort.txt', 'w') as f:
    for i in fileList:
        f.write(f'{i[0]} :: {i[1]}\n')
