import csv
import requests
import os
import time

# --- НАЛАШТУВАННЯ ---
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
COL_GIT_NAME = 'git name'  # Як називається колонка з логіном

def get_repo_column(fieldnames):
    # Шукаємо колонку з назвою репозиторію
    if 'Repo Name' in fieldnames:
        return 'Repo Name'
    for col in fieldnames:
        if col and col.strip().isdigit() and len(col.strip()) == 3:
            return col
    return None

def check_repo_exists(username, repo_name):
    # Перевірка через запит до сайту
    if not username or not repo_name:
        return "EMPTY"
        
    url = f"https://github.com/{username}/{repo_name}"
    try:
        response = requests.get(url, timeout=5)
        return "OK" if response.status_code == 200 else "FAIL"
    except:
        return "ERROR"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(INPUT_DIR):
        print("❌ Папка input не знайдена")
        return

    csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
    
    for filename in csv_files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        print(f"\n📄 Обробка: {filename}")
        
        with open(input_path, mode='r', encoding='utf-8') as infile:
            # Читаємо файл, ігноруємо помилки нульових байтів якщо є
            reader = csv.DictReader((line.replace('\0','') for line in infile))
            fieldnames = reader.fieldnames
            
            repo_col = get_repo_column(fieldnames)
            
            if not repo_col:
                print(f"⚠️ У файлі немає колонки 'Repo Name' або номера групи. Пропускаю.")
                continue
                
            print(f"   🎯 Знайдено колонку з репозиторіями: '{repo_col}'")

            out_fieldnames = fieldnames + ['Status']
            rows_to_write = []
            
            for row in reader:
                # --- ОСЬ ТУТ БУЛА ПОМИЛКА, ТЕПЕР ВИПРАВЛЕНО ---
                # Використовуємо (row.get() or ''), щоб перетворити None на пустий текст
                git_user = (row.get(COL_GIT_NAME) or '').strip()
                repo_name = (row.get(repo_col) or '').strip()
                
                # Прибираємо зайві символи, якщо вони є
                git_user = git_user.replace('_', '')
                
                if git_user and repo_name:
                    status = check_repo_exists(git_user, repo_name)
                    print(f"   👉 {git_user}/{repo_name} -> {status}")
                else:
                    status = "EMPTY"
                
                row['Status'] = status
                rows_to_write.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)

if __name__ == "__main__":
    main()
