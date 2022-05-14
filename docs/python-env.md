# Python Env

https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

## No Windows

Atualizar pip

```
py -m pip install --upgrade pip
```

Instalar lib

```
py -m pip install --user virtualenv
```

criar pasta env que será o dierotio do nosso env `env/`

```
py -m venv env
```

Ativar/Desativar

```
# activate
.\env\Scripts\activate
# no Power SHll talvez precise disso
set-executionpolicy remotesigned
# deactivate
deactivate
```

Instalar libs

```
py -m pip install requests
```

Salvar libs em arquivo

```
py -m pip freeze > requirements.txt
```

Instalar do `requirements.txt`

```
py -m pip install -r requirements.txt
```

**NESSE PROJETO FORAM USADOS AS SEGUINTES LIBS**

```
py -m pip install plotly
py -m pip install dash
py -m pip install gunicorn
py -m pip install pandas
py -m pip install dash_bootstrap_templates  
```

## Deploy no Heroku

fazzer login no heroku CLI

```
heroku login
```

Criar projeto heroku:

+  You have to change my-dash-app to a unique name. The name must start with a letter and can only contain lowercase letters, numbers, and dashes.

```
heroku create my-dash-app
```

Setar repo Heroku

```
 heroku git:remote -a dash-deputado-est-ba-2018
```

push heroku 

obs: `main` ao invez de `master`: isso depende do nome da branch original do priejto git original

```
git push heroku main
```

