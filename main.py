import os
import json
import hashlib


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "signed-files.json")


def sha256_file(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def load_data():
    if not os.path.exists(JSON_FILE):
        return []

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, list):
                return data

    except Exception:
        pass

    return []


def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_metadata():
    print()

    version = input("Version: ").strip()

    if not version:
        print("Version obligatoire.")
        return None

    description = input("Description: ").strip()

    if not description:
        print("Description obligatoire.")
        return None

    return version, description


def sign_file(file_path, version, description, relative_path=None):
    if not os.path.isfile(file_path):
        print("Fichier introuvable :", file_path)
        return None

    print("Signing:", file_path)

    file_size = os.path.getsize(file_path)
    file_hash = sha256_file(file_path)

    item = {
        "name": os.path.basename(file_path),
        "version": version,
        "description": description,
        "size": file_size,
        "sha256": file_hash
    }

    if relative_path is not None:
        item["path"] = relative_path

    return item


def sign_single_file():
    print()
    print("========================================")
    print("             SIGN A FILE")
    print("========================================")
    print()

    file_path = input("File path: ").strip().strip('"')

    if not os.path.isfile(file_path):
        print()
        print("ERROR: File not found.")
        return

    metadata = get_metadata()

    if metadata is None:
        return

    version, description = metadata

    print()
    item = sign_file(file_path, version, description)

    if item is None:
        return

    data = load_data()
    data.append(item)
    save_data(data)

    print()
    print("========================================")
    print("File signed successfully.")
    print("========================================")
    print()
    print("JSON:", JSON_FILE)


def sign_folder():
    print()
    print("========================================")
    print("          SIGN AN ENTIRE FOLDER")
    print("========================================")
    print()

    folder = input("Folder path: ").strip().strip('"')

    if not os.path.isdir(folder):
        print()
        print("ERROR: Folder not found.")
        return

    metadata = get_metadata()

    if metadata is None:
        return

    version, description = metadata

    print()
    print("Include subfolders?")
    print("[1] Yes")
    print("[2] No")
    print()

    choice = input("Choice: ").strip()

    if choice not in ("1", "2"):
        print("Invalid choice.")
        return

    recursive = choice == "1"

    files = []

    if recursive:
        for root, dirs, filenames in os.walk(folder):
            for filename in filenames:
                files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)

            if os.path.isfile(path):
                files.append(path)

    if not files:
        print()
        print("No files found.")
        return

    print()
    print("Found", len(files), "file(s).")
    print()

    data = load_data()

    for file_path in files:
        relative_path = os.path.relpath(file_path, folder)

        item = sign_file(
            file_path,
            version,
            description,
            relative_path
        )

        if item is not None:
            data.append(item)

    save_data(data)

    print()
    print("========================================")
    print("Folder signed successfully.")
    print("========================================")
    print()
    print("Files signed:", len(files))
    print("JSON:", JSON_FILE)


def list_signed_files():
    print()
    print("========================================")
    print("             SIGNED FILES")
    print("========================================")
    print()

    data = load_data()

    if not data:
        print("No signed files.")
        return

    for i, item in enumerate(data, 1):
        print(f"[{i}] {item.get('name', '')}")

        if "path" in item:
            print("    Path        :", item["path"])

        print("    Version     :", item.get("version", ""))
        print("    Size        :", item.get("size", 0), "bytes")
        print("    SHA-256     :", item.get("sha256", ""))
        print("    Description :", item.get("description", ""))
        print()


def main():
    while True:
        print()
        print("========================================")
        print("              VY SIGNER")
        print("========================================")
        print()
        print("[1] Sign a file")
        print("[2] Sign an entire folder")
        print("[3] List signed files")
        print("[4] Exit")
        print()

        choice = input("Choice: ").strip()

        if choice == "1":
            sign_single_file()

        elif choice == "2":
            sign_folder()

        elif choice == "3":
            list_signed_files()

        elif choice == "4":
            print()
            print("Bye.")
            break

        else:
            print()
            print("Invalid choice.")

        print()
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
