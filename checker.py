import csv
import requests
import os

# НАЛАШТУВАННЯ
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
# Назви колонок, які додав викладач (перевір точні назви у CSV файлі!)
COL_GIT_NAME = 'git name'   # Колонка з нікнеймом
COL_REPO_NAME = 'Repo Name' # Колонка з назвою репозиторію (твоя generated колонка або нова від викладача)

def check_repo_exists(username, repo_name):
    """Перевіряє доступність публічного репозиторію."""
    url = f"https://github.com/{username}/{repo_name}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return "OK"
        else:
            return "FAIL" # 404 або інша помилка
    except:
        return "FAIL" # Помилка з'єднання

def process_files():
    # Створюємо папку output, якщо немає
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Перебираємо всі CSV файли в папці input
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith('.csv'):
            continue
            
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"Обробляю файл: {filename}...")
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['Status'] # Додаємо нову колонку
            
            rows_to_write = []
            
            for row in reader:
                # Отримуємо дані для перевірки
                git_user = row.get(COL_GIT_NAME, '').strip()
                repo_name = row.get(COL_REPO_NAME, '').strip()
                
                status = "FAIL"
                if git_user and repo_name:
                    status = check_repo_exists(git_user, repo_name)
                
                # Записуємо результат
                row['Status'] = status
                rows_to_write.append(row)
                print(f"   Check: github.com/{git_user}/{repo_name} -> {status}")

        # Записуємо новий CSV в output
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
        print(f"✅ Готово! Результат збережено в {output_path}")

if __name__ == "__main__":
    process_files()
