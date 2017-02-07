import urllib.parse


class Request:
    @cached_property
    def url(self):
        pass

    @cached_property
    def parsed_url(self):
        return urllib.parse.urlparse(self.url)
