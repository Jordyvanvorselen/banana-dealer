def question(question):
    while True:
        print(question + " ")
        choice = input().lower()
        if choice is not None:
            return choice