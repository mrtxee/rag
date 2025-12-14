# flow

## venv
``PowerShell
cd Task2\app
python -m venv .venv
#.venv\Scripts\activate.bat -- ЕСЛИ Shell, ЕСЛИ PowerShell ТОГДА:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
# (маркер) что мы находимся в виртуальное среде venv1
python -m pip install --upgrade pip
pip install django
```java

## regex
```bash
# регулярное выражение для поиска в notepad-plus-plus, которое найдет все многострочные фрагменты текста от первого вхождения <dl> до конца теста
<dl>[\s\S]*\z

# регулярное выражение для поиска в notepad-plus-plus, которое найдет все многострочные фрагменты текста от начала файла с текстом до строки <h2>Сюжет</h2>
\A[\s\S]*?(?=<h2>Сюжет<\/h2>)
\A[\s\S]*?(?=<h2>Биография<\/h2>)

```
## index page
https://rickandmorty.fandom.com/ru/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A1%D0%B5%D1%80%D0%B8%D0%B8
##
