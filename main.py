import os

for i in range(6):
    names = os.listdir('./{}'.format(i + 1))
    with open("{}.txt".format(i + 1), "w", encoding="utf-8") as answer_file:
        for name in names:
            with open("{}/{}".format(i + 1, name), 'r', encoding='utf8') as f:
                answer_file.writelines(f.readlines())
