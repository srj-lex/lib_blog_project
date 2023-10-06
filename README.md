# LibBlog - социальная сеть

### Описание
Позволяет регистрироваться и менять данные своей учетной записи,

размещать и комментировать посты, 

подписываться на авторов и группы по интересам.

### Стэк технологий

- backend: Django = 2.2.16
- frontend: HTML + CSS (framework Bootstrap)

### Как запустить проект

Клонировать репозиторий:
```
git clone git@github.com:srj-lex/lib_blog_project.git
```

В корне проекта выполнить последовательно команды:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Далее перейти в папку lib_blog_project:
```
cd lib_blog_project
```

Запустить сервер разработки:
```
python3 manage.py runserver
```
