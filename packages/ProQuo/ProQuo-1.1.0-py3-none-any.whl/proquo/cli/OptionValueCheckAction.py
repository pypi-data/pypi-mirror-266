from argparse import Action


class OptionValueCheckAction(Action):

    def __call__(self, parser, namespace, values, option_string=None):

        if option_string == '--max-num-processes':
            if int(values) <= 0:
                parser.error("{0} must be greater 0".format(option_string))

        setattr(namespace, self.dest, values)