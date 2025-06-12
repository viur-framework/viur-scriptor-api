import json
from copy import deepcopy
from itertools import chain
from typing import Literal

from .module_parts import TreeModule
from .file import File
from ._utils import flatten_dict


def _preextractor_for_simple_bones(fieldname):
    def preextractor_for_simple_bones(data):
        return dict(data[fieldname])[fieldname]

    return preextractor_for_simple_bones


def _preextractor_for_translated_bones(fieldname, field_structure):
    languages = field_structure["languages"]

    def preextractor_for_language_bones(data):
        data = dict(data)
        field_data = dict(data[fieldname])
        res = {}
        for lang in languages:
            res[lang] = field_data[f"{fieldname}.{lang}"]
        return res

    return preextractor_for_language_bones


def _preextractor_for_multiple_bones(fieldname):
    def preextractor_for_multiple_bones(data):
        data = dict(data)
        field_data = dict(data[fieldname])
        try:
            del field_data[fieldname]
        except KeyError:
            pass
        field_data = [(int(k.rsplit('.', maxsplit=1)[-1]), v) for k, v in field_data.items() if v]
        field_data = [v for k, v in sorted(field_data)]
        if field_data:
            return field_data
        else:
            return None

    return preextractor_for_multiple_bones


def _preextractor_for_multiple_translated_bones(fieldname, field_structure):
    language_mapping = [(i, f"{fieldname}.{i}.") for i in field_structure["languages"]]

    def preextractor_for_multiple_translated_bones(data):
        field_data = data[fieldname]
        res = {key: [] for key, _ in language_mapping}
        for key, selector in language_mapping:
            for item_key, item_value in field_data:
                if item_key.startswith(selector) and item_value:
                    res[key].append((int(item_key.rsplit('.', maxsplit=1)[-1]), item_value))
        for key in res:
            res[key] = [i[1] for i in sorted(res[key])]
        return res

    return preextractor_for_multiple_translated_bones


def _preextractor_for_complex_bones(fieldname, field_structure):
    def preextractor_for_complex_bones(data):
        return data[fieldname]

    return preextractor_for_complex_bones


def _get_pre_extraction_converter(fieldname, field_structure):
    field_type = field_structure["type"]
    if any(field_type.startswith(i) for i in ["relational", "record", "spatial"]):
        return _preextractor_for_complex_bones(fieldname, field_structure)

    multiple = bool(field_structure.get('multiple', False))
    languages = bool(field_structure.get("languages", False))
    if languages:
        if multiple:
            return _preextractor_for_multiple_translated_bones(fieldname, field_structure)
        else:
            return _preextractor_for_translated_bones(fieldname, field_structure)
    else:
        if multiple:
            return _preextractor_for_multiple_bones(fieldname)
        else:
            return _preextractor_for_simple_bones(fieldname)


def _generate_pre_extraction_strategy(structure):
    s = structure["structure"]
    strat = {}
    for k, v in s.items():
        strat[k] = _get_pre_extraction_converter(k, v)
    return strat


def _format_for_table(data_from_db, structure):
    res = []
    raw_json_fields = []
    for key, props in structure["structure"].items():
        if props["type"] == "raw.json":
            raw_json_fields.append(key)

    for original_record in data_from_db:
        record = deepcopy(original_record)
        for raw_json_field in raw_json_fields:
            del record[raw_json_field]

        new = dict(flatten_dict(record))

        for raw_json_field in raw_json_fields:
            new[raw_json_field] = json.dumps(original_record[raw_json_field])
        res.append(new)
    return res


def _get_base_keys(d):
    base_keys = set()
    for k, v in d.items():
        base_keys.add(k.split('.', maxsplit=1)[0])
    return sorted(base_keys)


def _get_key_value_pairs_by_prefix_trucated(kvpairs, prefix):
    len_prefix_plus_one = len(prefix) + 1
    prefix_with_dot = f"""{prefix}."""
    res = []
    for k, v in kvpairs:
        if k.startswith(prefix_with_dot):
            res.append((k[len_prefix_plus_one:], v))
    return res


def _prepare_data_for_preextraction(d, fieldname):
    dotfieldname = f"{fieldname}."
    relevant_data = [(k, v) for k, v in d.items() if k == fieldname or k.startswith(dotfieldname)]
    return relevant_data


def _prepare_for_preextraction(row, base_keys=None):
    if base_keys is None:
        base_keys = _get_base_keys(row)
    res = {}
    for base_key in base_keys:
        res[base_key] = _prepare_data_for_preextraction(row, base_key)
    return res


def _pre_extract_with_strategy(prepared_data_for_preextraction, pre_extraction_strategy):
    res = {}
    for key, pre_extraction_converter in pre_extraction_strategy.items():
        res[key] = pre_extraction_converter(prepared_data_for_preextraction)
    return res


def _pre_extract_fields_from_using(using_fields_for_single_record):
    res = {}
    for key, value in using_fields_for_single_record:
        base_key, *suffix = key.split('.')
        if base_key not in res:
            res[base_key] = []
        res[base_key].append((key, value))
    return res


def _extractor_for_simple_bones(key, conversion_function=str, **kwargs):
    def extractor_for_simple_bones(data):
        yield key, conversion_function(data[key])

    return extractor_for_simple_bones


def _extractor_for_renamed_simple_bones(key, result_keys, conversion_function=str, **kwargs):
    def extractor_for_renamed_simple_bones(data):
        for result_key in result_keys:
            yield result_key, conversion_function(data[key])

    return extractor_for_renamed_simple_bones


def _extractor_for_translated_bones(key, bone_structure, conversion_function=str, **kwargs):
    languages = bone_structure["languages"]

    def extractor_for_translated_bones(data):
        for lang in languages:
            yield f"""{key}.{lang}""", conversion_function(data[key][lang])

    return extractor_for_translated_bones


def _extractor_for_multiple_bones(key, conversion_function=str, **kwargs):
    def extractor_for_multiple_bones(data):
        if data[key] is None:
            yield key, ''
        else:
            for item in data[key]:
                yield key, conversion_function(item)

    return extractor_for_multiple_bones


def _extractor_for_multiple_translated_bones(key, bone_structure, conversion_function=str, **kwargs):
    languages = bone_structure["languages"]

    def extractor_for_multiple_translated_bones(data):
        for lang in languages:
            for item in data[key][lang]:
                yield f"""{key}.{lang}""", conversion_function(item)

    return extractor_for_multiple_translated_bones


def _extractor_for_relational_bones(key, bone_structure):
    bone_multi = bone_structure["multiple"]
    languages = bone_structure["languages"]
    using = bone_structure["using"]
    using_extractor = None
    if using:
        using_extractor = _generate_extraction_strategy({"structure": using}, 'using')

    if languages:
        if bone_multi:
            def extractor_for_multiple_translated_relational_bones(data):
                if using:
                    d = dict(data[key])
                    for lang in languages:
                        lang_fields = dict(
                            _get_key_value_pairs_by_prefix_trucated(
                                d.items(), f"""{key}.{lang}"""))
                        indexes = set()
                        for k, v in lang_fields.items():
                            indexes.add(int(k.split('.', maxsplit=1)[0]))
                        is_none = True
                        for i in indexes:
                            if lang_fields[f"""{i}.dest.key"""]:
                                is_none = False
                                yield f"""{key}.{lang}.{i}.key""", lang_fields[f"""{i}.dest.key"""]
                                using_fields = dict(
                                    _get_key_value_pairs_by_prefix_trucated(lang_fields.items(), f"""{i}.rel"""))
                                extracted_using = _extract_with_strategy([using_fields], using_extractor)
                                final_using = [sum(d.values(), start=[]) for d in extracted_using][0]
                                for k, v in final_using:
                                    yield f"""{key}.{lang}.{i}.{k}""", v
                        if is_none:
                            yield f"""{key}.{lang}""", ""
                else:
                    extracted_languages = set(languages)
                    for k, v in sorted(data[key]):
                        if k.endswith('.dest.key'):
                            if v:
                                lang = k.split('.')[1]
                                yield f"""{key}.{lang}""", v
                                try:
                                    extracted_languages.remove(lang)
                                except:
                                    pass
                    for lang in extracted_languages:
                        yield f"""{key}.{lang}""", ""

            return extractor_for_multiple_translated_relational_bones
        else:

            def extractor_for_translated_relational_bones(data):
                d = dict(data[key])
                if using:
                    for lang in languages:
                        lang_fields = dict(
                            _get_key_value_pairs_by_prefix_trucated(
                                d.items(), f"""{key}.{lang}"""))
                        if not lang_fields.get("dest.key", None):
                            yield f"""{key}.{lang}""", ""
                            continue
                        else:
                            yield f"""{key}.{lang}.key""", lang_fields["dest.key"]
                        extractor_input = dict(_get_key_value_pairs_by_prefix_trucated(lang_fields.items(), f"""rel"""))
                        extracted_using = _extract_with_strategy([extractor_input], using_extractor)
                        final_using = [sum(d.values(), start=[]) for d in extracted_using][0]
                        for k, v in final_using:
                            yield f"""{key}.{lang}.{k}""", v
                else:
                    for lang in languages:
                        try:
                            yield f"""{key}.{lang}""", d[f"""{key}.{lang}.dest.key"""]
                        except KeyError:
                            yield f"""{key}.{lang}""", ""

            return extractor_for_translated_relational_bones
    else:
        if bone_multi:
            def extractor_for_multiple_relational_bones(data):
                if using:
                    extracted = dict(_get_key_value_pairs_by_prefix_trucated(dict(data)[key], key))
                    indexes = set()
                    for k, v in extracted.items():
                        indexes.add(int(k.split('.', maxsplit=1)[0]))
                    is_none = True
                    for i in sorted(indexes):
                        rel_key = extracted[f"""{i}.dest.key"""]
                        if not rel_key:
                            continue
                        is_none = False
                        yield f"""{key}.{i}.key""", extracted[f"""{i}.dest.key"""]
                        using_fields = dict(
                            _get_key_value_pairs_by_prefix_trucated(extracted.items(), f"""{i}.rel"""))
                        extracted_using = _extract_with_strategy([using_fields], using_extractor)
                        final_using = [sum(d.values(), start=[]) for d in extracted_using][0]
                        for k, v in final_using:
                            yield f"""{key}.{i}.{k}""", v
                    if is_none:
                        yield key, ""
                else:  # no using
                    has_yielded = False
                    for k, v in sorted(data[key]):
                        if k.endswith('.dest.key'):
                            if v:
                                yield key, v
                                has_yielded = True
                    if not has_yielded:
                        yield key, ""

            return extractor_for_multiple_relational_bones
        else:
            def extractor_for_simple_relational_bones(data):
                if using:
                    try:
                        val = dict(data[key])[f"""{key}.dest.key"""]
                        if val:
                            yield f"""{key}.key""", val
                        else:
                            yield f"""{key}""", ""
                            return
                    except KeyError:
                        yield f"""{key}.key""", ''
                    extraction_strategy_input = [
                        dict(_get_key_value_pairs_by_prefix_trucated(dict(data)[key], f"""{key}.rel"""))]
                    extracted_using = _extract_with_strategy(extraction_strategy_input, using_extractor)
                    final_using = [sum(d.values(), start=[]) for d in extracted_using][0]
                    for k, v in final_using:
                        yield f"""{key}.{k}""", v
                else:
                    try:
                        yield key, dict(data[key])[f"""{key}.dest.key"""]
                    except KeyError:
                        yield key, ''

            return extractor_for_simple_relational_bones


def _extractor_for_record_bones(key, bone_structure):
    bone_multi = bone_structure["multiple"]
    languages = bone_structure["languages"]
    using = bone_structure["using"]
    using_pre_extraction_strategy = _generate_pre_extraction_strategy({"structure": using})
    using_extractor_strategy = _generate_extraction_strategy({"structure": using}, 'using')

    if bone_multi:
        if languages:
            def extractor_for_translated_multiple_record_bones(data):
                d = dict(data[key])
                for lang in languages:
                    is_none = True
                    lang_fields = dict(
                        _get_key_value_pairs_by_prefix_trucated(
                            d.items(), f"""{key}.{lang}"""))
                    indexes = set()
                    for k, v in lang_fields.items():
                        indexes.add(int(k.split('.', maxsplit=1)[0]))
                    for i in indexes:
                        using_fields = dict(
                            _get_key_value_pairs_by_prefix_trucated(lang_fields.items(), f"""{i}"""))
                        if not any(using_fields.values()):
                            continue
                        packed_using_fields = _pack_subkeys(using_fields)
                        extracted_using = _extract_with_strategy([packed_using_fields], using_extractor_strategy)
                        final_using = [sum(d.values(), start=[]) for d in extracted_using][0]
                        for k, v in final_using:
                            is_none = False
                            yield f"""{key}.{lang}.{i}.{k}""", v
                    if is_none:
                        yield f"""{key}.{lang}""", ""

            return extractor_for_translated_multiple_record_bones
        else:
            def extractor_for_multiple_record_bones(data):
                d = data[key]
                extracted = dict(_get_key_value_pairs_by_prefix_trucated(d, key))
                indexes = set()
                for k, v in extracted.items():
                    indexes.add(int(k.split('.', maxsplit=1)[0]))
                is_none = True
                for i in sorted(indexes):
                    using_fields = dict(
                        _get_key_value_pairs_by_prefix_trucated(extracted.items(), f"""{i}"""))
                    if not any(using_fields.values()):
                        continue
                    packed_using_fields = _pack_subkeys(using_fields)
                    extracted_using = _extract_with_strategy([packed_using_fields], using_extractor_strategy)
                    final_using = [sum(d.values(), start=[]) for d in extracted_using][0]
                    for k, v in final_using:
                        is_none = False
                        yield f"""{key}.{i}.{k}""", v
                if is_none:
                    yield key, ''

            return extractor_for_multiple_record_bones
    else:
        if languages:
            def extractor_for_translated_record_bones(data):
                d = dict(data[key])
                is_none = True
                for lang in languages:
                    lang_fields = dict(
                        _get_key_value_pairs_by_prefix_trucated(
                            d.items(), f"""{key}.{lang}"""))
                    if not any(lang_fields.values()):
                        continue
                    packed_lang_fields = _pack_subkeys(lang_fields)
                    extracted_lang = _extract_with_strategy([packed_lang_fields], using_extractor_strategy)
                    final_lang = [sum(d.values(), start=[]) for d in extracted_lang][0]
                    for k, v in final_lang:
                        is_none = False
                        yield f"""{key}.{lang}.{k}""", v
                if is_none:
                    yield f"""{key}.{lang}""", ""

            return extractor_for_translated_record_bones
        else:
            def extractor_for_simple_record_bones(data):
                d = dict(data[key])
                if not any(v for k, v in d.items() if k.startswith(f"{key}.")):
                    yield key, ''
                    return
                initial_prepared_data_for_preextraction = _prepare_for_preextraction(d)
                second_prepared_data_for_preextraction = _get_key_value_pairs_by_prefix_trucated(
                    initial_prepared_data_for_preextraction[key], key)
                final_prepared_data_for_preextraction = _pre_extract_fields_from_using(
                    second_prepared_data_for_preextraction)
                pre_extracted_data_item = _pre_extract_with_strategy(final_prepared_data_for_preextraction,
                                                                     using_pre_extraction_strategy)
                extracted_data = _extract_with_strategy([pre_extracted_data_item], using_extractor_strategy)
                final_using = [sum(d.values(), start=[]) for d in extracted_data][0]
                for k, v in final_using:
                    yield f"""{key}.{k}""", v

            return extractor_for_simple_record_bones

    def dummy(*args, **kwargs):
        yield key, "NOT IMPLEMENTED"

    return dummy


_extractable_with_default_strategy_types = {  # this is a set, not a dict
    'key',
    'str',
    'date',
    'color',
    'numeric',
    'raw.json',
    'bool',
    'raw',
    'select',
    'text',
}
_extractable_with_default_strategy_type_prefixes = {  # this is a set, not a dict
    # the . at the end is important to prevent erroneous matches
    # with bones which have a type that is a prefix of other bones' types
    "str.",
    "select.",
    "numeric.",
}


def _generate_extraction_strategy(structure, module_type_name):
    extraction_strategy = {}
    for bone_name, bone_structure in structure["structure"].items():
        bone_type = bone_structure["type"]
        bone_multi = bone_structure["multiple"]
        bone_translated = bool(bone_structure["languages"])
        params = {
            "key": bone_name,
            "bone_structure": bone_structure,
        }
        if module_type_name == "TreeModule" and bone_name == "parententry":
            params["result_keys"] = ["node", "parententry"]
            extraction_strategy[bone_name] = _extractor_for_renamed_simple_bones(**params)
            continue
        # elif bone_name not in ["key", "parentrepo"] and bone_structure["readonly"]:
        #     continue
        elif bone_type in _extractable_with_default_strategy_types or any(
                bone_type.startswith(i) for i in _extractable_with_default_strategy_type_prefixes):
            # default strategy
            if bone_translated:
                if bone_multi:
                    extraction_strategy[bone_name] = _extractor_for_multiple_translated_bones(**params)
                else:
                    extraction_strategy[bone_name] = _extractor_for_translated_bones(**params)
            else:
                if bone_multi:
                    extraction_strategy[bone_name] = _extractor_for_multiple_bones(**params)
                else:
                    extraction_strategy[bone_name] = _extractor_for_simple_bones(**params)
            # end of default strategy
            # start of non-default-bones
        elif bone_type.startswith("relational"):
            extraction_strategy[bone_name] = _extractor_for_relational_bones(bone_name, bone_structure)
        elif bone_type.startswith("record"):
            extraction_strategy[bone_name] = _extractor_for_record_bones(bone_name, bone_structure)

        if bone_name not in extraction_strategy:
            raise NotImplementedError(
                f"""Bones of type '{bone_structure["type"]}' are not yet implemented. ({bone_name})""")
    return extraction_strategy


def _extract_with_strategy(pre_extracted_data, extraction_strategy):
    extracted_data = []
    for row in pre_extracted_data:
        row_extracted = {}
        for key, extractor in extraction_strategy.items():
            row_extracted[key] = []
            for item in extractor(row):
                row_extracted[key].append(item)
        extracted_data.append(row_extracted)
    return extracted_data


def export_to_table(data, structure, filename="export.csv"):
    csv_file = File.from_table(
        _format_for_table(data, structure),
        filename=filename,
        auto_str=True,
        fill_empty=True
    )
    return csv_file


def export_to_json(data, structure, filename="export.json"):
    return File(json.dumps(_format_for_table(data, structure), indent=4, sort_keys=True).encode(), filename)


def generate_key_replacement_mapping(table_header_keys, replacekeys):
    replace_bone_name_mapping = {}
    for table_header_key in table_header_keys:
        bone_name, *bone_name_suffix = table_header_key.split('.')
        if bone_name in replacekeys:
            if bone_name_suffix:  # prefix match
                replace_bone_name_mapping[
                    table_header_key] = f"""{replacekeys[bone_name]}.{'.'.join(bone_name_suffix)}"""
            else:  # key match
                replace_bone_name_mapping[bone_name] = replacekeys[bone_name]
    return replace_bone_name_mapping


def map_old_keys_to_new_keys(table_as_dicts, key_replacement_mapping):
    for item in table_as_dicts:
        out_item = {}
        for key, value in item.items():
            out_item[key_replacement_mapping.get(key, key)] = value
        yield out_item


def filter_module_structure_with_withelist(structure, whitelist):
    filtered_module_structure = deepcopy(structure)
    filtered_module_structure["structure"] = {}
    for key in whitelist:
        try:
            filtered_module_structure["structure"][key] = structure["structure"][key]
        except KeyError:
            pass
    return filtered_module_structure


def filter_module_structure_with_blacklist(structure, blacklist):
    filtered_module_structure = deepcopy(structure)
    for key in blacklist:
        try:
            del filtered_module_structure["structure"][key]
        except KeyError:
            pass
    return filtered_module_structure


def _do_nothing(*args, **kwargs):
    pass


def _pack_subkeys(data):
    res = {}
    for full_key, v in data.items():
        k, *suffix = full_key.split('.', maxsplit=1)
        if suffix:
            if k not in res or (isinstance(res[k], str) and not res[k]):
                res[k] = {}
            res[k][full_key] = v
        elif v:
            res[k] = v
    return res


async def import_from_table(
        table_as_dicts,
        module,
        structure=None,
        *,
        add_or_edit_mode: Literal["edit", "add_or_edit", "add"] = "edit",
        tree_skel_type=None,
        dry_run=False,
        progress_callback=None,
        query_params_callback=None,
        server_result_callback=None,
        exception_callback=None
):
    if progress_callback is None:
        progress_callback = _do_nothing
    if exception_callback is None:
        exception_callback = _do_nothing
    if query_params_callback is None:
        query_params_callback = _do_nothing
    if server_result_callback is None:
        server_result_callback = _do_nothing
    if isinstance(module, TreeModule):
        if tree_skel_type is None:
            raise ValueError('''For TreeModules you need to specify the tree_skel_type (either "leaf" or "node").''')
        elif tree_skel_type not in ["leaf", "node"]:
            raise ValueError('''The tree_skel_type needs to be either "leaf" or "node".''')
    else:
        tree_skel_type = None
    if structure is None:
        structure = await module.structure(renderer="vi", skel_type=tree_skel_type)
    table_iter = iter(table_as_dicts)
    first_item = next(table_iter)
    base_keys = _get_base_keys(first_item)
    pre_extraction_strategy = _generate_pre_extraction_strategy(structure)
    pre_extracted_data = []
    for row in chain([first_item], table_iter):
        prepared_data_for_preextraction = _prepare_for_preextraction(row, base_keys=base_keys)
        pre_extracted_data_item = _pre_extract_with_strategy(prepared_data_for_preextraction,
                                                             pre_extraction_strategy)
        pre_extracted_data.append(pre_extracted_data_item)
    extraction_strategy = _generate_extraction_strategy(structure, type(module).__name__)
    extracted_data = _extract_with_strategy(pre_extracted_data, extraction_strategy)
    data_prepared_for_db = [sum(d.values(), start=[]) for d in extracted_data]
    total_number_of_items = len(data_prepared_for_db)
    add_or_edit_function = {
        "edit": module.edit,
        "add_or_edit": module.add_or_edit,
        "add": module.add
    }[add_or_edit_mode]
    for index, writable_entry in enumerate(data_prepared_for_db):
        progress_callback(index=index, total=total_number_of_items)
        edit_params = {
            "params": writable_entry,
            "renderer": "vi"
        }
        if tree_skel_type:
            edit_params["skel_type"] = tree_skel_type

        query_params_callback(edit_params)
        if dry_run:
            server_result_callback({"action": "dry_run"})
        else:
            res = {"action": "something unexpected went wrong"}
            try:
                res = await add_or_edit_function(**edit_params)
            except Exception as e:
                exception_callback(e, edit_params)
                res = {"action": f"""{type(e).__name__}: {'\n'.join(e.args)}"""}
            server_result_callback(res)
