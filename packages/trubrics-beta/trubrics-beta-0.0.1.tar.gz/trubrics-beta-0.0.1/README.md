# trubrics-sdk

> [!IMPORTANT]  
> We are currently in beta.

To track events:

```python
trubrics = Trubrics(api_key="YOUR_TRUBRICS_API_KEY")

trubrics.track(
    event="User prompt",
    role="user",
    role_id="test_user_id",
    properties={"$text": "Hello, Trubrics! Tell me a joke?"},
    session_id="test_id",
)
```
