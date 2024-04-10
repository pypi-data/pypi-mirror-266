#!/bin/python

from .task import MBIOTask
from .xmlconfig import XMLConfig

import requests


# https://shelly-api-docs.shelly.cloud/cloud-control-api/
# api usage limited to 1 request per second


class MBIOTaskShelly(MBIOTask):
    def initName(self):
        return 'spush'

    def onInit(self):
        self.config.set('refreshperiod', 60)
        self._timeoutRefresh=0
        self._timeoutAPI=0
        self._retry=3
        self.valueDigital('comerr', default=False)

    def onLoad(self, xml: XMLConfig):
        self.config.set('server', xml.get('server'))
        self.config.set('token', xml.get('key'))
        self.config.update('refreshperiod', xml.getInt('refresh'))

    def url(self, path='/'):
        url='https://%s' % self.config.server
        return '%s/%s' % (url, path)

    def post(self, path, data=None):
        try:
            url=self.url(path)
            self.logger.debug(url)

            if data is None:
                data={}

            data['auth_key']=self.config.token

            self._timeoutAPI=self.timeout(1)
            r=requests.post(url,
                            payload=data,
                            verify=False, timeout=5.0)
            if r and r.ok:
                data=r.json
                self.logger.debug(data)
                return data
        except:
            self.logger.exception('post')

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def run(self):
        if not self.isTimeout(self._timeoutAPI):
            return 0.1

        if self.isTimeout(self._timeoutRefresh):
            self._timeoutRefresh=self.timeout(self.config.refreshperiod)
            error=False

            try:
                # TODO:
                pass
            except:
                # self.logger.exception('meteo')
                error=True

            if not error:
                self._timeoutRefresh=self.timeout(60*10)
                self._retry=3
                self.values.comerr.updateValue(False)
            else:
                self._timeoutRefresh=self.timeout(60)
                if self._retry>0:
                    self._retry-=1
                    if self._retry==0:
                        self.values.comerr.updateValue(True)
                        # TODO: set each error on each values

        return 5.0


if __name__ == "__main__":
    pass
