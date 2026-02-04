# Загрузка README в Confluence (персональное пространство)

Скрипт `upload_readme_to_confluence.py` создаёт новую страницу в вашем персональном пространстве Confluence (**zetes.atlassian.net**) с содержимым `README.md`.

## Что нужно

1. **API-токен Atlassian**  
   Создайте токен: [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)  
   (Log in with Google / email → Security → Create and manage API tokens.)

2. **Учётные данные** — либо в файле `.env` в корне проекта (рекомендуется), либо в переменных окружения:

   В `.env` (файл не коммитится, см. `.gitignore`):
   ```
   CONFLUENCE_EMAIL=your.email@company.com
   CONFLUENCE_API_TOKEN=your-api-token
   ```

   Или перед запуском:
   ```bash
   export CONFLUENCE_EMAIL="your.email@company.com"
   export CONFLUENCE_API_TOKEN="your-api-token"
   ```

   По желанию в `.env` или env:

   - `CONFLUENCE_BASE_URL` — по умолчанию `https://zetes.atlassian.net`
   - `CONFLUENCE_HOMEPAGE_ID` — id страницы в персональном пространстве (по нему определяется space). По умолчанию `1547698850` из вашей ссылки.
   - `CONFLUENCE_PAGE_TITLE` — заголовок новой страницы (по умолчанию: "Vendor-Independent PKI Model — Proposal for PKIC").

## Запуск

Если параметры в `.env`, достаточно:

```bash
cd /home/anton/projects/vendor-independent-pki
pip install -r scripts/requirements-confluence.txt   # один раз (или: python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements-confluence.txt)
python scripts/upload_readme_to_confluence.py        # или: .venv/bin/python scripts/upload_readme_to_confluence.py
```

В конце скрипт выведет ссылку на созданную страницу.

## Важно

- Скрипт **создаёт новую страницу** в том же пространстве, что и страница с `HOMEPAGE_ID`. Он не перезаписывает домашнюю страницу.
- Разметка переводится в HTML (заголовки, таблицы, ссылки, код). Если что-то отобразится некорректно, можно подправить страницу вручную в Confluence.
- Токен и email храните в `.env` (файл в `.gitignore`) или в переменных окружения — в репозиторий не попадают.

## Ваше персональное пространство

- Обзор: [https://zetes.atlassian.net/wiki/spaces/~7120209703f1ace64744f9866e1da808024940/overview?homepageId=1547698850](https://zetes.atlassian.net/wiki/spaces/~7120209703f1ace64744f9866e1da808024940/overview?homepageId=1547698850)
