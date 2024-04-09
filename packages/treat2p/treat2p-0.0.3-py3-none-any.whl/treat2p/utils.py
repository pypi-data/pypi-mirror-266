from functools import wraps
from collections import OrderedDict
import inspect
import contextlib
import joblib


def filter_save_kwargs(*excluded_save_kwargs, register=True):
    """Create decorator that wraps function, track its keyword arguments and output them along with the normal output
    of the function
    It also filters out any keyword argument that is not accepted by the input function.

    It can handle correctly (i.e. same behavior as raw python) :
      - functions with signatures containing **kwargs
      - positionnal/kwargs passed as keyword arguments

    For arguments to be saved in the output dictionnary :
      - their name must not appear in the excluded_save_kwargs items.
      - they must be keyword only (not positionnal or positionnal/keyword) or have a default value.
        (it is expected that default values are most of the time "small" variables such as
        text / numbers and that we want to register their values.
        If not, you can exclude them manually using excluded_save_kwargs.)
        To ensure that they are keyword only, you may place them after an asterisk separated by
        commas in your argument list (eg. arg1, arg2, *, kwarg1, kwarg2)
      - they must be present in the function signature (of course).
        Thus if you send arguments that are not in function signature and yet captured with a **kwargs,
        they can still be passed to child functions but will not be registered here.
        This is intended to be sure to have the actual values used by the proper functions saved as parameters
        that were used.
    That's all !

    Args:
        excluded_save_kwargs : any number of string representing wich argument to not include in the
        kwargs values saved and returned as second object of the wrapped function

    Returns:
        tuple: The wrapped funtion will return a two item tuple with :
          - item 1 = result of the wrapped function
          - item 2 = kwargs names and values entered as input to the wrapped function. (dictionnary type)
            This also includes the default values of the arguments that have a default value,
            and that have not beed supplied to the wrapped function.
    """

    def _filter_kwargs(func):
        sig = inspect.signature(func)
        ori_args = []
        ori_required_kwargs = []
        ori_kwargs = {}
        has_a_capture_all = False

        # iterate through function signature parameters
        for name, param in sig.parameters.items():
            # Check if parameters in signature are keyword or positionnal, with or without default value
            if param.default == inspect.Parameter.empty:
                if param.kind == param.KEYWORD_ONLY:
                    ori_required_kwargs.append(name)  # The parameter is a required keyword only argument
                elif param.kind == param.VAR_KEYWORD:
                    has_a_capture_all = True
                else:
                    ori_args.append(name)  # The parameter is a required positionnal argument
            else:
                ori_kwargs[name] = param.default  # The parameter is keyword with a default value

        # Use wraps to preserve the metadata of the original function
        @wraps(func)
        def wrap(*args, **kwargs):
            # Check for missing keyword arguments
            missing_kwargs = [name for name in ori_required_kwargs if name not in kwargs.keys()]
            if missing_kwargs:
                raise ValueError(f'Missing required keword arguments: {", ".join(missing_kwargs)}')

            # Filter kwargs to include original function required only kwargs
            filtered_kwargs = {name: kwargs[name] for name in ori_required_kwargs}

            # Update the filtered kwargs with optionnal only kwargs, that are in the function signature and in input
            filtered_kwargs.update(
                {
                    name: kwargs[name]
                    for name in kwargs
                    if name in ori_kwargs.keys() and name not in filtered_kwargs.keys()
                }
            )

            # Create an output dict with default kwargs, overriding default values if present as input.
            saved_kwargs = ori_kwargs.copy()
            saved_kwargs.update(filtered_kwargs)

            # Remove excluded kwargs
            for key in excluded_save_kwargs:
                saved_kwargs.pop(key, None)

            # if function has capture all, after we determined the saved_kwargs values
            # we can run it normally as python's default behaviour
            # already captures the used kwargs in their associated variables.
            if has_a_capture_all:
                if register:
                    ParameterRegistrator.register(saved_kwargs)
                    return func(*args, **kwargs)
                else:
                    return func(*args, **kwargs), saved_kwargs

            # if positionnal/kw arguments without defaults are passed as keyword arguments,
            # we add them into filtered_kwargs.
            # (otherwise they will be skipped and an error will be thrown)
            # note that since this happends after we created the saved_kwargs variable,
            # "recovering" args by name into filtered_kwargs doesn't save them. This is intended as saved_kargs must be
            # positionnal or having defaul values.
            if len(args) < len(ori_args):
                nb_missing = len(ori_args) - len(args)
                missing_args_indices = range(len(ori_args) - nb_missing, len(ori_args), 1)
                for index in missing_args_indices:
                    name = ori_args[index]
                    try:
                        filtered_kwargs[name] = kwargs[name]
                    except Exception as e:
                        pass
                        # we pass to raise the natural error (TypeError: missing X required positional arguments) below.

            # Return original result and the kwargs used
            if register:
                ParameterRegistrator.register(saved_kwargs)
                return func(*args, **filtered_kwargs)
            else:
                return func(*args, **filtered_kwargs), saved_kwargs

        return wrap

    return _filter_kwargs


def filter_kwargs(func):
    """
    Decorator function to wrap input function and filter out keyword arguments passed to it that
    are not present in the function signature. It raises a clear error if required kewords arguments are not passed.
    It can handle correctly (i.e. same behavior as raw python) :
      - functions with signatures containing **kwargs
      - positionnal/kwargs passed as keyword arguments

    Args:
        func (function): function to be wrapped.

    Raises:
        ValueError: Raises ValueError if keyword-only parameters without default values are not passed.

    Returns:
        function: A wrapped function which filters out non-related keyword parameters.
    """

    sig = inspect.signature(func)  # get function signature
    ori_args = []
    ori_required_kwargs = []
    ori_kwargs = {}
    has_a_capture_all = False

    # iterate through function signature parameters
    for name, param in sig.parameters.items():
        # Check if parameters in signature are keyword or positionnal, with or without default value
        if param.default == inspect.Parameter.empty:
            if param.kind == param.KEYWORD_ONLY:
                ori_required_kwargs.append(name)  # The parameter is a required keyword only argument
            elif param.kind == param.VAR_KEYWORD:
                has_a_capture_all = True
            else:
                ori_args.append(name)  # The parameter is a required positionnal argument
        else:
            ori_kwargs[name] = param.default  # The parameter is keyword with a default value

    @wraps(func)
    def wrap(*args, **kwargs):
        if has_a_capture_all:
            return func(*args, **kwargs)

        missing_kwargs = [name for name in ori_required_kwargs if name not in kwargs.keys()]
        if missing_kwargs:
            raise ValueError(f'Missing required keword arguments: {", ".join(missing_kwargs)}')

        # Filter kwargs to include original function required only kwargs
        filtered_kwargs = {name: kwargs[name] for name in ori_required_kwargs}

        # Update the filtered kwargs with optionnal only kwargs, that are in the function signature and in input
        filtered_kwargs.update(
            {name: kwargs[name] for name in kwargs if name in ori_kwargs.keys() and name not in filtered_kwargs.keys()}
        )

        # if positionnal/kw arguments without defaults are passed as keyword arguments,
        #  we add them into filtered_kwargs.
        # (otherwise they will be skipped and an error will be thrown)
        if len(args) < len(ori_args):
            nb_missing = len(ori_args) - len(args)
            missing_args_indices = range(len(ori_args) - nb_missing, len(ori_args), 1)
            for index in missing_args_indices:
                name = ori_args[index]
                try:
                    filtered_kwargs[name] = kwargs[name]
                except Exception as e:
                    pass
                    # we pass to raise the natural error (TypeError: missing X required positional arguments) below.

        return func(*args, **filtered_kwargs)

    return wrap


class ParameterRegistrator:
    """A class to manage the registration of parameters.
    It maintains a stack of ParameterRegistrators. The most recently created, but not yet exited,
    one is considered active and used for parameter registration.

    It is best used when working with a wrapper that creates a dictionnary to register function arguments automatically,
    such as filter_save_kwargs defined above.

    Attributes:
        _instance: A dictionary storing instances of the Registrator. This one is shared by the members of the class.
        _parameter_registry: A dictionary to register the parameters. This one is member specific.

    Example:
    ```python
    def function1(arg1, arg3 = None):
        ParameterRegistrator.register({"arg1": arg1, "arg3" : arg3})

    def function2(arg2="anotherone"):
        ParameterRegistrator.register({"arg2": arg2})
        with ParameterRegistrator("foo") as reg:
            function3()
            print(reg)

    def function3(arg5="an argument's value"):
        ParameterRegistrator.register({"arg5": arg5})

    with ParameterRegistrator("test") as reg:
        function1(arg1="value1")
        function2(arg2=12.45)
    print(reg)

    >>> {'arg5': "an argument's value"}
    >>> {'arg1': 'value1', 'arg3': None, 'arg2': 12.45}
    ```
    """

    _instance = OrderedDict()

    def __new__(cls, name, *args, **kwargs):
        obj = super(ParameterRegistrator, cls).__new__(cls)
        obj.name = name
        cls._instance[name] = (
            obj  # cls is the class object. So the _instance dict stays shared by the class members with this statement
        )
        return obj

    def __enter__(self):
        """Clear the _parameter_registry and return it for usage."""
        self._parameter_registry = {}
        self._parameter_registry["registrator_name"] = self.name
        return self._parameter_registry

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove the instance from _instance dictionary when it is not in use.
        Happends after a 'with' statement exits
        """
        self._instance.pop(self.name)

    @classmethod
    def get_registry(cls):
        """Get the parameter registry of the last created, but not yet exited, instance.
        If no instances are existing or all instances have exited, it returns an empty dictionary.

        Returns:
            dict: The last non-exited instance's registry or an empty dictionary.
        """
        try:
            last_instance_name, last_instance = list(cls._instance.items())[-1]  # Get the last Registrator instance
            return last_instance._parameter_registry  # Return last instance's registry
        except Exception as e:
            return {}  # Return empty dictionary if no non-exited instances are found

    @classmethod
    def register(cls, dictionnary):
        """Update the parameter registry of the last created, but not yet exited, instance with a new dictionary.

        Args:
            dictionnary (dict): The dictionary to combine with the last non-exited instance's registry.
        """
        try:
            last_instance_dict = cls.get_registry()  # Get the last non-exited instance's registry
            last_instance_dict.update(dictionnary)  # Update the registry using provided dictionary
        except Exception as e:
            pass  # Do nothing if no non-exited instances are found


# credits to featuredpeow : https://stackoverflow.com/questions/24983493/tracking-progress-of-joblib-parallel-execution


@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """Context manager to patch joblib to report into tqdm progress bar given as argument"""

    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()
