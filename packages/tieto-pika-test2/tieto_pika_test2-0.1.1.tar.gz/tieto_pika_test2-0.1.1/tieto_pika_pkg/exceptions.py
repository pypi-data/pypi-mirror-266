class MessageHandleError(Exception):

    def __repr__(self):
        return '{}: An unspecified message handle error has occurred; {}'.format(
            self.__class__.__name__, self.args)