"""Reads and write json files as a configuration file, supports nested json values."""
import json
import os
from typing import Union, Optional

class Config():
    """
    Create an instance of a configuration file.

    :params config_file_path: The path to the configuration file.
    :params file_must_exist: (optional) Raises a FileNotFoundError exception if file does not exist. (default: ``False``)
    """
    def __init__(
        self,
        config_file_path: str,
        file_must_exist: Optional[bool] = False
    ):
        # if file exists, attempt to load it
        # otherwise assume new config file
        if os.path.exists(config_file_path):
            if os.path.isfile(config_file_path):
                self._config_file_path = config_file_path

                self._load()
            else:
                raise FileNotFoundError(f'Config File {config_file_path} is not a file.')
        elif file_must_exist is False:
            # check that the file path is valid by attempting to open it real quick
            try:
                # FileExistsError if file exists or is invalid
                with open(config_file_path, 'x', encoding = 'utf-8'):
                    pass

                # Delete the file if it is empty
                if os.path.isfile(config_file_path):
                    with open(config_file_path, 'r', encoding = 'utf-8') as f:
                        contents = f.read()

                    if contents == '':
                        os.remove(config_file_path)
            except FileNotFoundError:
                pass

            self._settings = {}
            self._config_file_path = config_file_path
        else:
            raise FileNotFoundError(f'Config File {config_file_path} does not exist.')

    def _load(self):
        """Loads the configuration file."""

        if os.path.exists(self._config_file_path):
            # Open Config File, read the json information and close the file
            with open(self._config_file_path, 'r', encoding = 'utf-8') as f:

                settings = json.loads(f.read())

            self._settings = settings
        else:
            raise FileNotFoundError(f'Config File {self._config_file_path} does not exist.')

    def _convert_keys_to_list(
        self,
        keys: Union[str, tuple, list]
    ) -> list[str]:
        """
        Convert the keys to a list.

        :params keys: The keys to be converted.
        :return: The converted keys as a list.
        """
        if isinstance(keys[0], tuple):
            keys_list = list(*keys)
        else:
            keys_list = list(keys)

        return keys_list

    def save(
        self,
        indent: Optional[int] = 4
    ):
        """
        Saves the configuration file.

        :params indent: (optional) The number of spaces to indent the json file. (default: ``4``)
        """

        with open(self._config_file_path, "w", encoding='utf-8') as out_file:
            json.dump(self._settings, out_file, indent = indent)

    def get(
        self,
        *keys: str
    ):
        """
        Returns the specified setting.

        :params keys: The path to the setting.
        """

        return self._action(keys, action='get')

    def set(
        self,
        *keys: str,
        value
    ) -> None:
        """
        Sets the specified setting.

        :params keys: The path to the setting.
        :params value: The value to be set.
        """

        self._action(keys, action='set', value=value)

    def delete(
        self,
        *keys: str
    ) -> None:
        """
        Deletes the specified setting.

        :params keys: The path to the setting.
        """

        self._action(keys, action='delete')

    def exists(
        self,
        *keys: str
    ) -> bool:
        """
        Returns a boolean if a setting exists.

        :params keys: The path to the setting.
        """

        return self._action(keys, action='exists')

    def settings(self) -> dict:
        """Returns the current settings."""

        return self._settings

    def _action(
        self,
        keys: Union[str, tuple, list],
        action: str,
        value = None
    ):
        """
        Perform an action on a setting.

        :params keys: A list of keys that specify the path to the
            value to be accessed or modified in the dictionary. Each key in the list is either
            a string or a tuple of strings. If a tuple is used, it represents a sub-path within
            the dictionary.
        :params action: A string that specifies the action to be performed on the dictionary.
            Valid actions are ``get``, ``set``, ``delete``, and ``exists``.
        :params value: (optional) The value to be used in conjunction with the ``set`` action.
            This argument is ignored for all other actions. If the ``set`` action is specified and
            ``value`` is not provided, a TypeError is raised. (default: ``None``)
        """

        if action not in ['get', 'set', 'exists', 'delete']:
            raise ValueError(f"{action} was not a valid action. Only 'get', 'set', 'exists', and 'delete' can be used.")

        action_text = action

        # Pull off plural, only for exists action for now
        if action[-1] == 's':
            action_text = action[:-1]

        if keys == ():
            raise KeyError(f'No key specified to {action_text}.')

        keys_list = self._convert_keys_to_list(keys)

        if len(keys_list) == 0:
            raise KeyError(f'No key specified to {action_text}.')

        data = self._settings

        last_key = keys_list[-1]

        if last_key == []:
            raise KeyError(f'No key specified to {action_text}.')

        # When assigning drill down to *second* last key
        for k in keys_list[:-1]:
            if k in data:
                data = data[k]
            else:
                if action != 'exists':
                    raise KeyError(f'Setting {k} does not exist.')
                else:
                    return False

        # based on action, respond differently to the setting
        if action == 'get':
            return data[last_key]
        elif action == 'set':
            data[last_key] = value
        elif action == 'exists':
            if last_key in data:
                return True
            else:
                return False
        elif action == 'delete':
            if last_key in data:
                del data[last_key]
            else:
                raise KeyError(f'Setting {last_key} does not exist and cannot be deleted.')

    def __str__(self) -> str:
        return str(self._settings)

    def __repr__(self) -> str:
        return str(self._settings)

    def __getitem__(
        self,
        item: Union[str, tuple, list]
    ) -> str:
        return self.get(item)

    def __setitem__(
        self,
        item: Union[str, tuple, list],
        value
    ) -> None:
        self.set(item, value = value)

    def __delitem__(
        self,
        item: Union[str, tuple, list]
    ) -> None:
        self.delete(item)

    def __contains__(
        self,
        item: Union[str, tuple, list]
    ) -> bool:
        return self.exists(item)

    def __len__(self) -> int:
        return len(self._settings)
