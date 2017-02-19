#!/usr/bin/env python
#
# Helper script for removing acme challenge
#
import os, sys
def main(token):
    os.unlink(
        "{0}/.well-known/acme-challenge/{1}".format(
            os.environ.get('WEBROOT', ''),
            token
        )
    )
if __name__ == "__main__": # pragma: no cover
    main(sys.argv[1:])
