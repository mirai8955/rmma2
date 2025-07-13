# rmma-2

First, please install the dependencies:
```bash
pip install -r requirements.txt
```

Then, configure the environment variables. Create a file named .env in the current directory and copy the contents from .env.example. Modify the values of these environment variables according to your requirements:
```bash
cp .env.example .env.local
```

Export your google api key
```bash
export GOOGLE_API_KEY="your api key here"
```

Create x api token by run this command 
```bash

```

Run server
```bash
uvicorn main_api:app
```