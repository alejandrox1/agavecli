#####
OAuth
#####

Basic authentication involves entering your username and password.
A more formal name for this is HTTP Basic Auth.

A problem with HTTP Basic Auth is that we have to pass our credentials into
every request.
This repeated usage of credentials makes it a little insecure.
Another problem is when we are using theird-party services to do some work for
us. In such a case, we wouldn't want Linkedin to have the our gmail password
but would rather prefer for this third-party service to have a simple
"permision" to do some task.

Another good example is when we are writing applications for others.
Users may love the functionality of our product but may be reluctant to provide
their facebook or google credentials and trust us not only to not mess around
with their accounts but to keep these credentials secure.

OAuth is the solutions to these and many other problems!

In OAuth there are three parties involved:
* The Oauth provider represents and authoritative source of identity
  information (i.e., facebook, google).

* An OAuth client, usually, represents an application. OAuth clients use a
  OAuth provider to interact with resources on behalf od the user. Which brings
  us to the third party of this process.

* The user is you.


OAuth provides different protocols called `grant types` to enable clients to
use different processes to gain access to a user's resources.

A successful OAuth authentication results in the client obtaining a short term
access token representing the user from the provider.
The client can then use this access token to access resources in the name of
the user until the token expires.
