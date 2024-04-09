class DashboardHooks:
    def before_create(self, data):
        return data

    def after_create(self, model):
        return model

    def before_edit(self, data):
        return data

    def after_edit(self, model):
        return model

    def before_delete(self, model):
        return model

    def after_delete(self, model):
        return model