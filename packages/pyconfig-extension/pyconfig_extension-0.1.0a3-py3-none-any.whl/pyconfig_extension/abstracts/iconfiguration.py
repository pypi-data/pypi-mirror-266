from abc import ABC, abstractmethod
from typing import Callable

from multipledispatch import dispatch

from pyconfig_extension.abstracts.binder.binder_option_listener import IBinderOptionConfigure, DefaultBinderOptionConfigure
from pyconfig_extension.abstracts.binder.binder_options import BinderOptions
from pyconfig_extension.abstracts.binder.binding_point import BindingPoint


class IConfiguration(ABC):

    @abstractmethod
    def __getitem__(self, item: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key: str, value: str | None):
        raise NotImplementedError

    @abstractmethod
    def get_section(self, key: str) -> 'IConfigurationSection':
        raise NotImplementedError

    @abstractmethod
    def get_children(self) -> list['IConfigurationSection']:
        raise NotImplementedError

    def get_required_section(self, key: str):
        section = self.get_section(key)
        if section is not None and section.exists():
            return section
        raise Exception(f"section {key} is not found in configuration")

    @dispatch(object)
    def get(self, klass_type: type):
        def binder_function(x: BinderOptions):
            pass

        return self.get(klass_type, binder_function)

    @dispatch(str, object)
    def get(self, section_key: str, klass_type: type):
        def binder_function(x: BinderOptions):
            pass

        section = self.get_section(section_key)
        return section.get(klass_type, binder_function)

    @dispatch(object, object)
    def get(self, klass_type: type, configure_options: Callable[[BinderOptions], None]):
        options = BinderOptions()
        configure_options(options)

        from pyconfig_extension.abstracts.binder.binder_utils import get
        return get(self, klass_type, configure_options)

    @dispatch(str, object, object)
    def bind(self, section_key: str, instance, instance_typ: type):
        section: IConfigurationSection = self.get_section(section_key)
        section.bind(instance, instance_typ, DefaultBinderOptionConfigure())

    @dispatch(str, object)
    def bind(self, section_key: str, instance):
        section: IConfigurationSection = self.get_section(section_key)
        section.bind(instance, type(instance), DefaultBinderOptionConfigure())

    @dispatch(object, object)
    def bind(self, instance, instance_type: type):
        self.bind(instance, instance_type, DefaultBinderOptionConfigure())

    @dispatch(object)
    def bind(self, instance):
        self.bind(instance, type(instance), DefaultBinderOptionConfigure())

    @dispatch(object, object, IBinderOptionConfigure)
    def bind(self, instance, instance_type: type, configure_options: IBinderOptionConfigure):

        if instance is not None:
            options = BinderOptions()
            if configure_options is not None:
                configure_options.on_config(options)
            binding_point = BindingPoint(instance, True)

            from pyconfig_extension.abstracts.binder.binder_utils import bind_instance
            bind_instance(instance_type, binding_point, self, options)


class IConfigurationSection(IConfiguration, ABC):

    @property
    @abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self) -> str | None:
        raise NotImplementedError

    def exists(self):
        if self is None:
            return False
        return self.value is not None or len(self.get_children()) > 0
