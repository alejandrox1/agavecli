#######################
Agave API OAuth Clients
#######################

We will start by generating a set of Agave client keys, OAuth credentials.

Generating OAuth credentials uses HTTP Basic authentication.

Agave has a full OAuth provider server and supports 4 major grant types:
1. `password`
2. `authorization_code`
3. `refresh_token`
4. `implicit`

For more information, see `supported authorization flows<http://developer.agaveapi.co/#supported-authorization-flows>`_.

The OAuth client will have access to all basic Agave APIs.

To create a client, simply make a POST reuest to the clients endpoint. 
The request must include the `clientName`.
If successful, the response should include a 201 HTTP code.

Two important fields in the response are the `consumerKey` and
`consumerSecret`.
We will need these two values to interact with theAgave OAuth token service to
generate access tokens.
