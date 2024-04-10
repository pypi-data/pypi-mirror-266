from .task import MBIOTask
from .xmlconfig import XMLConfig


class MBIOTaskVirtualIO(MBIOTask):
    def initName(self):
        return 'vio'

    def onInit(self):
        pass

    def onLoad(self, xml: XMLConfig):
        items=xml.children('digital')
        if items:
            for item in items:
                name=item.get('name')
                if name:
                    self.valueDigital(name, default=item.getBool('default'), writable=True)

        items=xml.children('analog')
        if items:
            for item in items:
                name=item.get('name')
                unit=item.get('unit')
                resolution=item.getFloat('resolution', 0.1)
                if name:
                    self.value(name, unit=unit, default=item.getBool('default'), writable=True, resolution=resolution)

    def poweron(self):
        return True

    def poweroff(self):
        return True

    def run(self):
        for value in self.values:
            # value.updateValue(value.value)
            if value.isPendingSync():
                value.clearSyncAndUpdateValue()
        return 5.0


if __name__ == "__main__":
    pass
