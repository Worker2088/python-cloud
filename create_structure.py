import os


def create_folder_structure(base_path, structure):
    """
    Создаёт структуру папок и файлов по заданному шаблону.

    Args:
        base_path (str): путь к базовой папке.
        structure (dict): шаблон структуры (папки и файлы).
    """
    for folder_name, content in structure.items():
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        if isinstance(content, dict):
            create_folder_structure(folder_path, content)
        elif isinstance(content, list):
            for file_name in content:
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Файл: {file_name}\nСоздан автоматически.\n")


# Шаблон структуры
template = {
    "src": {
        "auth": [
            "__init__.py",
            "exception.py",
            "models.py",
            "repository.py",
            "router.py",
            "schemas.py",
            "service.py",
        ],
        "core": ["__init__.py", "settings.py"],
        "db": ["__init__.py", "base.py", "models.py", "session.py", "database.py"],
    },
    "frontent": [],
    "storage": [],
    "logs": ["logging.json"],
    "tests": ["__init__.py", "conftest.py"],
    "data": ["config.json"],
}


# Создаём структуру в текущей директории
create_folder_structure(".", template)
print("Структура папок и файлов успешно создана!")
