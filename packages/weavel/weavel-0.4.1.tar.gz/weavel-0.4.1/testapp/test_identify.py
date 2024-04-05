from weavel import create_client, WeavelClient, Trace
from uuid import uuid4

client: WeavelClient = create_client()

user_identifier = "USER IDENTIFIER EXAMPLE"

client.identify(user_identifier, {"email": "test@email.com", "name": "testname", "gender": "male"})

client.close()