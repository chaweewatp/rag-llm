# rag-llm

### run milvus db

- https://milvus.io/docs/install_standalone-docker.md
- curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh
- bash standalone_embed.sh start

### run ollama

-
-
-

Test

```
curl -X POST http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama3.2",
           "messages": [
             {
               "role": "system",
               "content": "You are a helpful assistant."
             },
             {
               "role": "user",
               "content": "กระต่ายกับเต่าใครชนะ"
             }
           ],
           "temperature": 0,
           "stream": false
         }'
```

```
curl -X POST http://localhost:11434/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama3.2",
           "messages": [
             {
               "role": "system",
               "content": "You are a helpful assistant."
             },
             {
               "role": "user",
               "content": "กระต่ายกับเต่าใครชนะ"
             }
           ],
           "temperature": 0,
           "stream": true
         }'
```

```
curl -X POST http://192.168.1.51:11435/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama3.2:1b",
           "messages": [
             {
               "role": "system",
               "content": "You are a helpful assistant."
             },
             {
               "role": "user",
               "content": "กระต่ายกับเต่าใครชนะ"
             }
           ],
           "temperature": 0,
           "stream": false
         }'


```

```
curl -X POST http://localhost:11435/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
           "model": "llama3.2:1b",
           "messages": [
             {
               "role": "system",
               "content": "You are a helpful assistant."
             },
             {
               "role": "user",
               "content": "กระต่ายกับเต่าใครชนะ"
             }
           ],
           "temperature": 0,
           "stream": false
         }'

```

```
docker exec -it ollama_service ollama run llama3.2
```
