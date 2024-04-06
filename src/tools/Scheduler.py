import threading


class Scheduler:
    def __init__(self, time: float or None, action, *args, **kwargs):
        """
        :param time: Time between two execution of the action. Set it to 'None' to make the execution on-trigger.
        :param action: The action (callable) to be perfomed.
        :param args: The arguments to be passed to the action.
        :param kwargs: The keyword arguments to be passed to the action.
        """
        self.___event = threading.Event()
        self.___time = time
        self.___terminated = False

        self.___thread = threading.Thread(target=self.___run, args=(_CallableWrapper(action, *args, **kwargs),))
        self.___thread.start()

    def ___run(self, action):
        while True:
            self.___event.wait(self.___time)
            if self.___terminated:
                break
            action.run()
            self.___event.clear()

    def terminate(self):
        self.___terminated = True
        if not self.___event.is_set():
            self.___event.set()
        self.___thread.join()

    def trigger(self):
        if not self.___event.is_set():
            self.___event.set()


class _CallableWrapper:
    def __init__(self, call, *args, **kwargs):
        self.___call = call
        self.___args = args
        self.___kwargs = kwargs

    def run(self):
        self.___call(*self.___args, **self.___kwargs)
