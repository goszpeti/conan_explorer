"""
These modules must be initializable without the usage of any internal dependencies, except each other and settings.
They should live for the whole lifetime of the program and cannot be destroyed. Usually they are singletons.
"""

from conan_app_launcher.base.logger import Logger
