from abc import ABC, abstractmethod

from pyconfig_extension.abstracts.binder.binder_options import BinderOptions


class IBinderOptionConfigure(ABC):

    @abstractmethod
    def on_config(self, options: BinderOptions):
        pass


class DefaultBinderOptionConfigure(IBinderOptionConfigure):

    def on_config(self, options: BinderOptions):
        pass
