# rmma-2 api

First, please install the dependencies:
```zsh
pip install -r requirements.txt
```

Then, configure the environment variables. Create a file named .env in the current directory and copy the contents from .env.example. Modify the values of these environment variables according to your requirements:
```zsh
cp .env.example .env.local
```

Export your google api key
```zsh
export GOOGLE_API_KEY="your api key here"
```

Create x api token by run this command 
```zsh
python -m x.activate
```

Run server
```zsh
uvicorn main_api:app
```