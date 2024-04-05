import requests
from requests_oauthlib import OAuth1Session

class TwitterAPI:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.session = OAuth1Session( consumer_key,
                                      client_secret = consumer_secret,
                                      resource_owner_key = access_token,
                                      resource_owner_secret = access_token_secret )

    def get_user_profile(self):
        url = "https://api.twitter.com/2/users/me"
        response = self.session.get( url )
        return response.json()
