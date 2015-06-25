import sys
import inspect

from tornado.web import Application
from tornado import log

from tornado.ioloop import IOLoop

from vizydrop.sdk.application import Application as ThirdPartyApp
from vizydrop.rest.handlers import rest_handlers


class VizydropTPAHost(Application):
    """
    Tornado application to host a Vizydrop third-party application
    """
    app = None

    def __init__(self, app_module=None, *args, **kwargs):
        log.app_log.info("Initializing TPA module {}".format(app_module))
        try:
            __import__(app_module)
        except ImportError as e:
            log.app_log.error("Unable to import application module {}".format(app_module))
            log.app_log.error(str(e))
            exit()
        for name, cls in self.get_classes_in_module(app_module):
            if issubclass(cls, ThirdPartyApp) and cls is not ThirdPartyApp:
                self.app = cls
                break
        if self.app is None:
            log.app_log.error("Unable to find a Vizydrop Application in the module {}".format(app_module))
            exit()
        log.app_log.info("TPA for application '{}' started successfully!".format(self.app.Meta.name))
        super(VizydropTPAHost, self).__init__(rest_handlers, *args, tpa=self.app, **kwargs)

    def get_classes_in_module(self, module):
        """
        Gathers all classes in an application module
        :param module: Name of the app module (do not include apps.)
        :return: list of classes
        """
        classes = []
        return classes + inspect.getmembers(sys.modules[module], inspect.isclass)


if __name__ == '__main__':
    if sys.argv.__len__() == 1:
        print(u"You must specify an application module to host:")
        print(u"python -m vizydrop.tpa <application module> [port]".format(sys.argv[0]))
        exit()
    log.enable_pretty_logging()
    port = sys.argv[2] if sys.argv.__len__() >= 3 else 8080
    log.app_log.info("Vizydrop TPA host starting on port {}".format(port))
    VizydropTPAHost(app_module=sys.argv[1]).listen(port)
    IOLoop.instance().start()
