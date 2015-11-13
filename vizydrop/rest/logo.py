from os import path
import inspect
from vizydrop.rest import VizydropAppRequestHandler
from . import TpaHandlerMixin


class LogoHandler(VizydropAppRequestHandler, TpaHandlerMixin):
    def get(self):
        # check for a local file
        d = path.dirname(path.realpath(inspect.getfile(self.tpa)))
        fp = path.join(d, 'logo.svg')
        if path.isfile(fp):
            self.set_header('Content-Type', 'image/svg+xml')
            with open(fp, 'r') as fh:
                return self.write(fh.read())
        # check our meta
        meta = self.tpa.Meta
        if hasattr(meta, 'logo'):
            # use our logo specified in our meta
            self.set_status(303)
            return self.set_header('Location', meta.logo)
        # and finally, if we have nothing...
        self.set_status(204)
        return self.finish('', encode=False)
