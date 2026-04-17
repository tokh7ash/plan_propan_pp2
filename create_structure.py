import os

# Структура проекта
structure = {
    "Practice 9": {
        "mickeys_clock": {
            "main.py": "",
            "clock.py": "",
            "images": {
                "mickey_hand.png": ""
            },
            "README.md": ""
        },
        "music_player": {
            "main.py": "",
            "player.py": "",
            "music": {
                "sample_tracks": {}
            },
            "README.md": ""
        },
        "moving_ball": {
            "main.py": "",
            "ball.py": "",
            "README.md": ""
        },
        "requirements.txt": "",
        "README.md": ""
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # создаем файл
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

# запуск
if __name__ == "__main__":
    create_structure(".", structure)
    print("Структура создана!")