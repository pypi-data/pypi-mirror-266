# AIVOX

An easy-to-use API for generating music

# SETUP

pip install aivox

# EXAMPLE

client = APIClient(base_url="https://example.com")

response = client.play("username", "password", "/endpoint", {"key": "value"})

print(response)
