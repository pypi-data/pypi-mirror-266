class Bootable:
    @staticmethod
    def init_bootable_hook(_class):
        if hasattr(_class, 'boot'):
            _class.boot()

        if hasattr(_class, 'booted'):
            _class.booted()