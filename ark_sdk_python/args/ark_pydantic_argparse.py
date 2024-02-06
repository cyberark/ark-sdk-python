import argparse
import csv
import json
import re
import sys
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from ark_sdk_python.args.ark_args_formatter import ArkArgsFormatter


class ArkPydanticArgparse:
    @staticmethod
    def __populate_type(
        prop_type: str,
        snake_prop_name: str,
        default: Optional[str],
        required: bool,
        parser: argparse.ArgumentParser,
        prefix: str = '',
        description: str = '',
        ignore_keys: Optional[List[str]] = None,
        enum: Optional[List[str]] = None,
        key_prefix: str = '',
    ) -> None:
        if key_prefix:
            key_prefix = key_prefix + '-'
        if ignore_keys != None and snake_prop_name in ignore_keys:
            return
        if default != None:
            required = False
        if isinstance(default, Enum):
            default = default.value
        arg_type = None
        if prop_type == 'string':
            arg_type = str
        elif prop_type == 'integer':
            arg_type = int
        elif prop_type == 'boolean':
            arg_type = bool
        elif prop_type == 'object':
            arg_type = object
        else:
            arg_type = str
        long_name = key_prefix + prefix + snake_prop_name
        shorted_name = ''.join([s[0] for s in long_name.replace('.', '-').split('-')])
        for i in range(5):
            for action in parser._actions:  # pylint: disable=protected-access
                if f'-{shorted_name}' in action.option_strings:
                    shorted_name = ''.join([s[: i + 1] for s in long_name.split('-')])
                    break
        if arg_type == bool:
            parser.add_argument(
                '-' + shorted_name,
                '--' + long_name,
                required='--request-file' not in ' '.join(sys.argv) and required,
                action='store_true',
                help=description,
            )
            if long_name != 'poll':
                parser.add_argument(
                    '-n' + shorted_name,
                    '--no-' + long_name,
                    dest=long_name.replace('-', '_'),
                    required='--request-file' not in ' '.join(sys.argv) and required,
                    action='store_false',
                    help=description,
                )
            parser.set_defaults(**{f"{long_name.replace('-', '_')}": default})
        elif arg_type == object:
            parser.add_argument(
                '-' + shorted_name,
                '--' + long_name,
                required='--request-file' not in ' '.join(sys.argv) and required,
                metavar="KEY=VALUE",
                nargs='+',
                default=default,
                help=description,
            )
        else:
            parser.add_argument(
                '-' + shorted_name,
                '--' + long_name,
                required='--request-file' not in ' '.join(sys.argv) and required,
                type=arg_type,
                default=default,
                help=description,
                choices=enum,
            )

    @staticmethod
    def __schema_definition_to_argparse(
        schema: Dict[str, Any],
        defaults: Optional[Dict[str, str]],
        definitions: Optional[Dict[str, Any]],
        required: Optional[List[str]],
        prop_name: str,
        parser: argparse.ArgumentParser,
        prefix: str = '',
        ignore_keys: Optional[List[str]] = None,
        key_prefix: str = '',
    ) -> None:
        if not definitions:
            return
        snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('_', '-')
        def_prop_name = schema['properties'][prop_name]['$ref'].split('/')[2]
        def_prop = definitions[def_prop_name]
        if 'type' not in def_prop.keys():
            return
        prop_type = def_prop['type']
        desc = ''
        if 'description' in def_prop.keys():
            desc = def_prop['description']
        default: Optional[str] = None
        if 'default' in def_prop.keys():
            default = def_prop['default']
        elif defaults and prefix + snake_prop_name in defaults:
            default = defaults[snake_prop_name]
        if prop_type == 'object':
            ArkPydanticArgparse.schema_to_argparse(
                def_prop, parser, defaults, f'{snake_prop_name}.', definitions, required, ignore_keys, key_prefix
            )
        else:
            is_required = False
            if required and prop_name in required:
                is_required = True
            enum = None
            if 'enum' in def_prop:
                enum = def_prop
            ArkPydanticArgparse.__populate_type(
                prop_type, snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
            )

    @staticmethod
    def __schema_allof_to_argparse(
        schema: Dict[str, Any],
        defaults: Optional[Dict[str, str]],
        definitions: Optional[Dict[str, Any]],
        required: Optional[List[str]],
        prop_name: str,
        parser: argparse.ArgumentParser,
        prefix: str = '',
        ignore_keys: Optional[List[str]] = None,
        key_prefix: str = '',
    ) -> None:
        snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('_', '-')
        desc = ''
        default: Optional[str] = None
        if 'default' in schema['properties'][prop_name].keys():
            default = schema['properties'][prop_name]['default']
        elif defaults and prefix + snake_prop_name in defaults.keys():
            default = defaults[snake_prop_name]
        if 'description' in schema['properties'][prop_name].keys():
            desc = schema['properties'][prop_name]['description']
        for item in schema['properties'][prop_name]['allOf']:
            if '$ref' in item.keys() and definitions:
                def_prop_name = item['$ref'].split('/')[2]
                def_prop = definitions[def_prop_name]
                if 'type' not in def_prop.keys():
                    if 'enum' in def_prop.keys():
                        is_required = False
                        if required and prop_name in required:
                            is_required = True
                        enum = def_prop['enum']
                        ArkPydanticArgparse.__populate_type(
                            'string', snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                        )
                    continue
                prop_type = def_prop['type']
                if prop_type == 'object':
                    ArkPydanticArgparse.schema_to_argparse(
                        def_prop, parser, defaults, f'{prefix}{snake_prop_name}.', definitions, required, ignore_keys, key_prefix
                    )
                else:
                    is_required = False
                    if required and prop_name in required:
                        is_required = True
                    enum = None
                    if 'enum' in def_prop:
                        enum = def_prop['enum']
                    ArkPydanticArgparse.__populate_type(
                        prop_type, snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                    )
            else:
                if 'type' not in item.keys():
                    continue
                prop_type = item['type']
                if 'default' in item.keys():
                    default = item['default']
                elif defaults and prefix + snake_prop_name in defaults:
                    default = defaults[snake_prop_name]
                if 'description' in item.keys():
                    desc = item['description']
                if prop_type == 'object':
                    ArkPydanticArgparse.schema_to_argparse(
                        item, parser, defaults, f'{prefix}{snake_prop_name}.', definitions, required, ignore_keys, key_prefix
                    )
                else:
                    is_required = False
                    if required and prop_name in required:
                        is_required = True
                    enum = None
                    if 'enum' in item:
                        enum = item['enum']
                    ArkPydanticArgparse.__populate_type(
                        prop_type, snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                    )

    @staticmethod
    def __arg_in_schema(arg_key: str, schema: Dict[str, Any], definitions: Optional[Dict[str, Any]], prefix: str = '') -> Optional[str]:
        if 'properties' not in schema:
            prop_name = schema['title']
            snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('-', '_')
            if prefix + snake_prop_name == arg_key:
                return schema['type']
            else:
                return None
        for prop_name in schema['properties'].keys():
            snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('-', '_')
            if '$ref' in schema['properties'][prop_name].keys():
                def_prop_name = schema['properties'][prop_name]['$ref'].split('/')[2]
                def_prop = definitions[def_prop_name]
                if 'type' not in def_prop.keys():
                    if 'enum' in def_prop.keys():
                        return 'string'
                    continue
                if def_prop['type'] == 'object':
                    if ArkPydanticArgparse.__arg_in_schema(arg_key, def_prop, definitions, f'{prefix}{snake_prop_name}.'):
                        return def_prop['type']
                if prefix + snake_prop_name == arg_key:
                    return def_prop['type']
            elif 'allOf' in schema['properties'][prop_name].keys():
                for item in schema['properties'][prop_name]['allOf']:
                    if '$ref' in item.keys():
                        def_prop_name = item['$ref'].split('/')[2]
                        def_prop = definitions[def_prop_name]
                        if 'type' not in def_prop.keys():
                            if 'enum' in def_prop.keys():
                                return 'string'
                            continue
                        if def_prop['type'] == 'object':
                            if ArkPydanticArgparse.__arg_in_schema(arg_key, def_prop, definitions, f'{prefix}{snake_prop_name}.'):
                                return def_prop['type']
                        if prefix + snake_prop_name == arg_key:
                            return def_prop['type']
                    if 'type' in item.keys():
                        if item['type'] == 'object':
                            if ArkPydanticArgparse.__arg_in_schema(arg_key, item, definitions, f'{prefix}{snake_prop_name}.'):
                                return item['type']
                        if prefix + snake_prop_name == arg_key:
                            return item['type']
            elif (
                'anyOf' in schema['properties'][prop_name].keys()
                and isinstance(schema['properties'][prop_name]['anyOf'], list)
                and all('type' in t for t in schema['properties'][prop_name]['anyOf'])
            ):
                if prefix + snake_prop_name == arg_key:
                    return 'string'
            elif 'type' in schema['properties'][prop_name].keys():
                if prefix + snake_prop_name == arg_key:
                    return schema['properties'][prop_name]['type']
                if schema['properties'][prop_name]['type'] == 'object':
                    if ArkPydanticArgparse.__arg_in_schema(
                        arg_key, schema['properties'][prop_name], definitions, f'{prefix}{snake_prop_name}.'
                    ):
                        return schema['properties'][prop_name]['type']
        return None

    @staticmethod
    def __arg_to_schema(
        arg_key: str, arg_val: Any, args_map: Dict[str, Any], arg_type: str, keep_empty_values: bool = False, key_prefix: str = ''
    ) -> None:
        if key_prefix:
            key_prefix = key_prefix + '_'
        if '.' in arg_key:
            args = arg_key.split('.')
            key = args[0]
            if key not in args_map.keys() or args_map[key] == None:
                args_map[key] = {}
            ArkPydanticArgparse.__arg_to_schema('.'.join(args[1:]), arg_val, args_map[key], arg_type, key_prefix)
        elif arg_val != None or keep_empty_values:
            if arg_type == 'array':
                if isinstance(arg_val, list):
                    args_map[key_prefix + arg_key] = arg_val
                elif re.match('({.*},?)+', arg_val) != None:
                    objs = []
                    for m in re.finditer('{.*?}', arg_val):
                        objs.append(json.loads(m.group(0)))
                    args_map[key_prefix + arg_key] = objs
                else:
                    args_map[key_prefix + arg_key] = arg_val.split(',')
            elif arg_type == 'object' and not isinstance(arg_val, (int, bool, float)):
                if isinstance(arg_val, list):
                    arg_val = ','.join(arg_val)
                if '=' not in arg_val:
                    args_map[key_prefix + arg_key] = arg_val
                else:
                    args_dict = dict(
                        next(csv.reader([item], delimiter='=', quotechar="'", escapechar="\\", skipinitialspace=True))
                        for item in next(csv.reader([arg_val], delimiter=',', quotechar="'", escapechar="\\", skipinitialspace=True))
                    )
                    if len(args_dict) > 0:
                        args_map[key_prefix + arg_key] = args_dict
                    elif arg_key != 'extrafields':
                        args_map[key_prefix + arg_key] = arg_val
            else:
                args_map[key_prefix + arg_key] = arg_val

    @staticmethod
    def schema_to_argparse(
        schema: Dict[str, Any],
        parser: argparse.ArgumentParser,
        defaults: Optional[Dict[str, str]] = None,
        prefix: str = '',
        definitions: Optional[Dict[str, Any]] = None,
        required: Optional[List[str]] = None,
        ignore_keys: Optional[List[str]] = None,
        key_prefix: str = '',
    ) -> None:
        """
        Converts the given schema to argparse parameters.

        Recursively iterates over the JSON schema and adds parameters to the parser.
        The argparse parameters can then be parsed from the CLI and then converted back using argparse_to_schema function.

        This function does not return anything, but updates the parser itself.

        Args:
            schema (Dict[str, Any]): _description_
            parser (argparse.ArgumentParser): _description_
            defaults (Optional[Dict[str, str]], optional): _description_. Defaults to None.
            prefix (str, optional): _description_. Defaults to ''.
            definitions (Optional[Dict[str, Any]], optional): _description_. Defaults to None.
            required (Optional[List[str]], optional): _description_. Defaults to None.
            ignore_keys (Optional[List[str]], optional): _description_. Defaults to None.
            key_prefix (str, optional): _description_. Defaults to ''.
        """
        if not definitions and 'definitions' in schema.keys():
            definitions = schema['definitions']
        elif not definitions:
            definitions = {}
        if not required and 'required' in schema.keys():
            required = schema['required']
        elif not required:
            required = []
        if 'properties' not in schema.keys():
            prop_name = schema['title']
            snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('_', '-')
            is_required = False
            if prop_name in required:
                is_required = True
            default = None
            if 'default' in schema.keys():
                default = schema['default']
            desc = ''
            if 'description' in schema.keys():
                desc = schema['description']
            enum = None
            if 'enum' in schema:
                enum = schema['enum']
            ArkPydanticArgparse.__populate_type(
                schema['type'], snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
            )
            return
        for prop_name in schema['properties'].keys():
            snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('_', '-')
            if ignore_keys and snake_prop_name in ignore_keys:
                continue
            if '$ref' in schema['properties'][prop_name].keys():
                ArkPydanticArgparse.__schema_definition_to_argparse(
                    schema, defaults, definitions, required, prop_name, parser, prefix, ignore_keys, key_prefix
                )
                continue
            elif 'allOf' in schema['properties'][prop_name].keys():
                ArkPydanticArgparse.__schema_allof_to_argparse(
                    schema, defaults, definitions, required, prop_name, parser, prefix, ignore_keys, key_prefix
                )
                continue
            elif (
                'anyOf' in schema['properties'][prop_name].keys()
                and isinstance(schema['properties'][prop_name]['anyOf'], list)
                and all('type' in t for t in schema['properties'][prop_name]['anyOf'])
            ):
                snake_prop_name = re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('_', '-')
                is_required = False
                if prop_name in required:
                    is_required = True
                default = None
                if 'default' in schema['properties'][prop_name].keys():
                    default = schema['properties'][prop_name]['default']
                desc = ''
                if 'description' in schema['properties'][prop_name].keys():
                    desc = schema['properties'][prop_name]['description']
                enum = None
                if 'enum' in schema['properties'][prop_name]:
                    enum = schema['enum']
                ArkPydanticArgparse.__populate_type(
                    'string', snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                )
                continue
            desc = ''
            if 'description' in schema['properties'][prop_name].keys():
                desc = schema['properties'][prop_name]['description']
            default = None
            if 'default' in schema['properties'][prop_name].keys():
                default = schema['properties'][prop_name]['default']
            elif defaults and prefix + snake_prop_name in defaults.keys():
                default = defaults[snake_prop_name]
            if 'type' not in schema['properties'][prop_name].keys():
                if 'enum' in schema['properties'][prop_name].keys():
                    is_required = False
                    if required and prop_name in required:
                        is_required = True
                    enum = schema['properties'][prop_name]['enum']
                    ArkPydanticArgparse.__populate_type(
                        'string', snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                    )
                continue
            prop_type = schema['properties'][prop_name]['type']
            if prop_type == 'object':
                if (
                    'properties' not in schema['properties'][prop_name]
                    and (
                        'additionalProperties' in schema['properties'][prop_name]
                        and 'type' in schema['properties'][prop_name]['additionalProperties']
                        and len(schema['properties'][prop_name]['additionalProperties']) == 1
                    )
                    or (all(k in ['title', 'description', 'type'] for k in schema['properties'][prop_name]))
                ):
                    # Special use case for dicitionary
                    is_required = False
                    if required and prop_name in required:
                        is_required = True
                    enum = None
                    if 'enum' in schema['properties'][prop_name]:
                        enum = schema['properties'][prop_name]['enum']
                    ArkPydanticArgparse.__populate_type(
                        prop_type, snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                    )
                else:
                    ArkPydanticArgparse.schema_to_argparse(
                        schema['properties'][prop_name],
                        parser,
                        defaults,
                        f'{prefix}{snake_prop_name}.',
                        definitions,
                        required,
                        ignore_keys,
                        key_prefix,
                    )
            else:
                is_required = False
                if required and prop_name in required:
                    is_required = True
                enum = None
                if 'enum' in schema['properties'][prop_name]:
                    enum = schema['properties'][prop_name]['enum']
                ArkPydanticArgparse.__populate_type(
                    prop_type, snake_prop_name, default, is_required, parser, prefix, desc, ignore_keys, enum, key_prefix
                )

    @staticmethod
    def schema_to_aliases(
        schema: Dict[str, Any],
        override_aliases: Optional[Dict[str, str]] = None,
        ignore_keys: Optional[List[str]] = None,
        prefix: str = '',
        definitions: Optional[Dict[str, Any]] = None,
        key_prefix: str = '',
    ) -> Dict[str, str]:
        """
        Converts a schema to only a dictionary containing its aliases (title).
        Returns a string to string dictionary with the aliases.

        Args:
            schema (Dict[str, Any]): _description_
            override_aliases (Optional[Dict[str, str]], optional): _description_. Defaults to None.
            ignore_keys (Optional[List[str]], optional): _description_. Defaults to None.
            prefix (str, optional): _description_. Defaults to ''.
            definitions (Optional[Dict[str, Any]], optional): _description_. Defaults to None.
            key_prefix (str, optional): _description_. Defaults to ''.

        Returns:
            Dict[str, str]: _description_
        """
        if key_prefix:
            key_prefix = key_prefix + '_'
        if 'properties' not in schema:
            return {}
        if not definitions and 'definitions' in schema.keys():
            definitions = schema['definitions']
        elif not definitions:
            definitions = {}
        if not override_aliases:
            override_aliases = {}
        aliases_map: Dict[str, Any] = {}
        for prop_name in schema['properties']:
            snake_prop_name = prefix + re.sub(r'(?<!^)(?=[A-Z])', '_', prop_name).lower().replace('-', '_')
            if 'title' not in schema['properties'][prop_name] and snake_prop_name not in override_aliases:
                continue
            if ignore_keys and snake_prop_name in ignore_keys:
                continue
            if snake_prop_name in override_aliases:
                aliases_map[key_prefix + snake_prop_name] = override_aliases[snake_prop_name]
            else:
                aliases_map[key_prefix + snake_prop_name] = schema['properties'][prop_name]['title']
            if 'type' in schema['properties'][prop_name]:
                if schema['properties'][prop_name]['type'] == 'object':
                    aliases_map.update(
                        ArkPydanticArgparse.schema_to_aliases(
                            schema['properties'][prop_name], ignore_keys, f'{prefix}{snake_prop_name}.', key_prefix
                        )
                    )
        return aliases_map

    @staticmethod
    def argparse_to_schema(
        schema: Dict[str, Any],
        args: argparse.Namespace,
        keep_empty_values: bool = False,
        key_prefix: str = '',
        ignored_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Converts the given JSON schema and argparse args into a finalized dictionary.
        The conversion is recursive and converts keys according to snake case.

        Returns a finalized args dictionary.

        Args:
            schema (Dict[str, Any]): _description_
            args (argparse.Namespace): _description_
            keep_empty_values (bool, optional): _description_. Defaults to False.
            key_prefix (str, optional): _description_. Defaults to ''.
            ignored_keys (Optional[List[str]], optional): _description_. Defaults to None.

        Returns:
            Dict[str, Any]: _description_
        """
        file_args_map: Dict = {}
        args_map: Dict = {}
        definitions: Optional[Dict] = None
        if 'request_file' in args.__dict__.keys() and args.__dict__['request_file']:
            request_file = args.__dict__['request_file']
            with open(request_file, 'r', encoding='utf-8') as f:
                loaded_args_map = json.load(f)
                for key, value in loaded_args_map.items():
                    first, *others = key.split('_')
                    file_args_map[''.join([first.lower(), *map(str.title, others)])] = value
        if 'definitions' in schema.keys():
            definitions = schema['definitions']
        for arg_key, arg_val in args.__dict__.items():
            if ignored_keys and arg_key in ignored_keys:
                continue
            if key_prefix:
                arg_key = arg_key.replace(f'{key_prefix}_', '')
            arg_type = ArkPydanticArgparse.__arg_in_schema(arg_key, schema, definitions)
            if not arg_type:
                continue
            ArkPydanticArgparse.__arg_to_schema(arg_key, arg_val, args_map, arg_type, keep_empty_values, key_prefix)
        args_map.update(file_args_map)
        return args_map

    @staticmethod
    def argparse_to_schema_interactive(
        schema: Dict[str, Any],
        args: argparse.Namespace,
        ignored_keys: Optional[List[str]] = None,
        existing_values: Optional[Dict[str, Any]] = None,
        hidden_keys: Optional[List[str]] = None,
        override_aliases: Optional[Dict[str, str]] = None,
        key_prefix: str = '',
        empty_allowed_keys: Optional[List[str]] = None,
        default_values: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Converts the given schema and args into a finalized dictionary.
        The function interacts with the user and requests args that were not provided in the CLI.

        Returns a dict that combines the schema with the user inputs.

        Args:
            schema (Dict[str, Any]): _description_
            args (argparse.Namespace): _description_
            ignored_keys (Optional[List[str]], optional): _description_. Defaults to None.
            existing_values (Optional[Dict[str, Any]], optional): _description_. Defaults to None.
            hidden_keys (Optional[List[str]], optional): _description_. Defaults to None.
            override_aliases (Optional[Dict[str, str]], optional): _description_. Defaults to None.
            key_prefix (str, optional): _description_. Defaults to ''.
            empty_allowed_keys (Optional[List[str]], optional): _description_. Defaults to None.
            default_values (Optional[Dict[str, Any]], optional): _description_. Defaults to None.

        Returns:
            Dict[str, Any]: _description_
        """
        if key_prefix:
            existing_values = {f'{key_prefix}_{k}': v for k, v in existing_values.items()}
        args_map = {
            k: (
                existing_values[k]
                if existing_values and k in existing_values and existing_values[k] != None
                else v if v else default_values[k] if default_values and k in default_values else None
            )
            for k, v in ArkPydanticArgparse.argparse_to_schema(schema, args, True, key_prefix, ignored_keys).items()
        }
        aliases_map = {
            k: v
            for k, v in ArkPydanticArgparse.schema_to_aliases(
                schema, override_aliases=override_aliases, key_prefix=key_prefix, ignore_keys=ignored_keys
            ).items()
            if k in args_map
        }
        for k, v in aliases_map.items():
            if ignored_keys and k in ignored_keys:
                continue
            args_map[k] = ArkArgsFormatter.get_arg(
                args=args,
                key=k,
                prompt=v,
                existing_val=args_map[k],
                hidden=k in hidden_keys if hidden_keys else False,
                prioritize_existing_val=True,
                empty_value_allowed=k in empty_allowed_keys if empty_allowed_keys is not None else False,
            )
        if key_prefix:
            return {k.replace(f'{key_prefix}_', ''): v for k, v in args_map.items()}
        return args_map

    @staticmethod
    def merge_by_model(
        model: Type[BaseModel],
        existing_model: BaseModel,
        new_vals: Union[BaseModel, Dict[str, Any]],
        by_alias: bool = False,
        key_prefix: str = '',
        ignore_keys: Optional[List[str]] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """
        Merges the given existing model with new values.
        The new values can be either a base model or dictionary of values.
        When provided, the merging is based on the specified key prefix.

        Args:
            model (Type[BaseModel]): _description_
            existing_model (BaseModel): _description_
            new_vals (Union[BaseModel, Dict[str, Any]]): _description_
            by_alias (bool, optional): _description_. Defaults to False.
            key_prefix (str, optional): _description_. Defaults to ''.
            ignore_keys (Optional[List[str]], optional): _description_. Defaults to None.
            defaults (Optional[Dict[str, Any]], optional): _description_. Defaults to None.

        Returns:
            BaseModel: _description_
        """
        if key_prefix:
            new_vals = {k.replace(f'{key_prefix}_', ''): v for k, v in new_vals.items()}
        if isinstance(new_vals, BaseModel):
            new_vals = new_vals.dict(by_alias=by_alias)
        new_vals = {k: v for k, v in new_vals.items() if v is not None}
        vals_dict = existing_model.dict(by_alias=by_alias)
        if ignore_keys:
            new_vals = {k: v for k, v in new_vals.items() if k not in ignore_keys}
        vals_dict.update(new_vals)
        if defaults:
            vals_dict.update({k: v for k, v in defaults.items() if k not in vals_dict or vals_dict[k] is None})
        return model.parse_obj(vals_dict)

    @staticmethod
    def schema_to_simple_arguments(
        schema: Dict[str, Any], ignore_keys: Optional[List[str]] = None, extra_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Exports model's schema as task's input parameters dictionary.

        Args:
            schema (Dict[str, Any]): _description_
            ignore_keys (Optional[List[str]], optional): _description_. Defaults to None.
            extra_params (Optional[Dict[str, Any]], optional): _description_. Defaults to None.
        Returns:
            Dict[str, TaskInputParameter]: _description_
        """
        definitions: dict = None
        if 'definitions' in schema.keys():
            definitions = schema['definitions']
        parser = argparse.ArgumentParser()
        ArkPydanticArgparse.schema_to_argparse(schema, parser, ignore_keys=ignore_keys)
        input_args = {}
        if extra_params:
            input_args.update(extra_params)
        for action in parser._actions:  # pylint: disable=protected-access
            if '_HelpAction' not in str(type(action)):
                arg_info = ArkPydanticArgparse.__arg_in_schema(action.dest, schema, definitions)
                action_type = action.type if '_StoreTrueAction' not in str(type(action)) else bool
                if 'strtobool' in str(action_type):
                    action_type = bool
                if 'format' in arg_info and arg_info['format'] == 'password':
                    action_type = 'secret'
                default = action.default
                name = action.dest
                input_args[name] = {'type': action_type, 'description': action.help if action.help else ''}
                if default is not None:
                    input_args[name]['default'] = default
                if action.choices:
                    input_args[name]['choices'] = action.choices
        for _, val in input_args.items():
            if val['type'] == bool:
                val['type'] = 'boolean'
            elif 'choices' in val:
                val['type'] = 'choice'
                val['choices'] = [str(v) for v in val['choices']]
            elif val['type'] != 'secret':
                val['type'] = 'string'
            if 'default' not in val:
                val['default'] = '' if val['type'] in ['string', 'secret'] else [] if val['type'] == 'choice' else False
            if val['type'] == 'string':
                val['default'] = str(val['default'])
        return input_args
