"""Собирает ответ сервера обновлений для GitHub-релиза.

Источник правды по номеру и смысловой версии — version.json на
leshtm.run.place: он уже отвечает за текущий выпуск. Здесь он
превращается в тот же плоский формат, но со ссылкой на ассет
GitHub-релиза и с хешем файла.

Формат ответа разбирает UpdateInfo.parse в приложении: плоский объект
без вложенности, поля versionCode, versionName, url, notes, sha256.
"""

import json
import os
import sys

VERSION = os.environ["BUILD_VERSION"].strip()
REPO = os.environ["REPO_SLUG"].strip()
SHA = os.environ["EXPECTED_SHA"].strip().lower()

if len(SHA) != 64 or any(c not in "0123456789abcdef" for c in SHA):
    sys.exit("SHA-256 должен быть 64 шестнадцатеричных символа")

with open("upstream-version.json", encoding="utf-8") as f:
    up = json.load(f)

code = int(up["versionCode"])
name = up.get("versionName", "")
notes = up.get("notes", "")
upstream_url = up.get("url", "")

# Ответ сервера должен указывать ровно на ту сборку, которую публикуем.
# Иначе приложение предложило бы не то, что лежит в релизе.
if not upstream_url.endswith("energy-%s.apk" % VERSION):
    sys.exit("version.json на сервере указывает на %s, а ждём сборку %s"
             % (upstream_url, VERSION))

asset = "https://github.com/%s/releases/download/v%s/energy-%s.apk" % (
    REPO, VERSION, VERSION)

payload = {
    "versionCode": code,
    "versionName": name,
    "url": asset,
    "notes": notes,
    "sha256": SHA,
}

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)
    f.write("\n")

with open("notes.md", "w", encoding="utf-8") as f:
    f.write("%s\n\n" % (notes or "Сборка %s." % VERSION))
    f.write("Номер сборки %s, файл `energy-%s.apk`.\n" % (code, VERSION))
