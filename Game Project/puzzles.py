import random

def generate_math_puzzle():
    """Generates a simple math-based puzzle."""
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-", "*"])
    question = f"What is {num1} {operator} {num2}?"
    answer = eval(f"{num1} {operator} {num2}")
    choices = [str(answer), str(answer + 1), str(answer - 1), str(answer + 2)]
    random.shuffle(choices)  # Shuffle choices to randomize the correct answer's position
    correct_index = choices.index(str(answer))
    return {
        "question": question,
        "choices": choices,
        "answer": correct_index + 1,  # 1-based index for player input
        "reward": 50
    }

def load_static_puzzles():
    """Loads static puzzles from the JSON file."""
    import json
    with open("data/puzzles.json", "r") as file:
        return json.load(file)

def get_random_puzzle():
    """Returns a random puzzle (either static or dynamic)."""
    if random.random() < 0.5:  # 50% chance to generate a dynamic puzzle
        return generate_math_puzzle()
    else:
        return random.choice(load_static_puzzles())