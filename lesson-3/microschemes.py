class DigitalGate:
    def __init__(self):
        self._val_a = False
        self._val_b = False
        self._output = False
        self._target = None
        self._target_pin = 0

    def _broadcast(self):
        self.evaluate()
        if self._target:
            if self._target_pin == 1:
                self._target.In1 = self._output
            elif self._target_pin == 2:
                self._target.In2 = self._output

    @property
    def In1(self):
        return self._val_a

    @In1.setter
    def In1(self, value):
        self._val_a = bool(value)
        self._broadcast()

    @property
    def In2(self):
        return self._val_b

    @In2.setter
    def In2(self, value):
        self._val_b = bool(value)
        self._broadcast()

    @property
    def Res(self):
        return self._output

    def link(self, element, pin):
        self._target = element
        self._target_pin = pin

    def evaluate(self):
        raise NotImplementedError


class TNot(DigitalGate):
    def evaluate(self):
        self._output = not self._val_a


class TAnd(DigitalGate):
    def evaluate(self):
        self._output = self._val_a and self._val_b


class TOr(DigitalGate):
    def evaluate(self):
        self._output = self._val_a or self._val_b