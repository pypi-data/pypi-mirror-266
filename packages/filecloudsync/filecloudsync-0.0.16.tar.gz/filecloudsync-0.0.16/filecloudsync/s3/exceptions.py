class S3ConnectionError(Exception):
    """ Exception for S3 connection errors """
    pass


class S3RequestTimeTooSkewed(Exception):
    """ When the difference between the request time and the server's time is too large. """
    pass


class TagsNotMatchError(Exception):
    """ Exception when two tags aren't equals """
    pass
