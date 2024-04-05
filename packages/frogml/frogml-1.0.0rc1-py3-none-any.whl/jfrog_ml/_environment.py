import pkg_resources
import platform


class Recorder:
    @staticmethod
    def get_environment_dependencies():
        installed_packages = pkg_resources.working_set
        return sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])

    @staticmethod
    def get_environment_details():
        return [f"arch={platform.architecture()[0]}",
                f"cpu={platform.processor()}",
                f"platform={platform.platform()}",
                f"python_version={platform.python_version()}",
                f"python_implementation={platform.python_implementation()}",
                f"python_compiler={platform.python_compiler()}"]
