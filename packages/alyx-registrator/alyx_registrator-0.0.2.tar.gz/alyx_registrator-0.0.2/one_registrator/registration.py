from dataclasses import dataclass, field
from logging import getLogger
import os, shutil, pandas as pd, re, json, pkgutil
import one

from .utils import get_existing_datasets, find_files


@dataclass
class FileRecord:
    # source_path is the original path from disk scan. will never change
    source_path: str

    # dest_path is the path after renaming method calculated it. It is a frozen version of renamed_path
    # if it appears empty in a dataframe, it's because to_user_dict sets it to "" if rename is false, for clarity sake
    dest_path: str = ""

    _alf_info: dict = None

    match: bool = False
    matching_rules: list = field(default_factory=list)
    used_rule: str = ""

    valid_alf: bool = False
    path_conflicts: bool = False
    dataset_type_exists: bool = False
    rename: bool = False
    delete: bool = False
    include: bool = False
    abort: list = field(default_factory=list)

    def get_dataset_type(self, item="dest"):
        if item == "dest":
            return self.alf_info["object"] + "." + self.alf_info["attribute"]
        elif item == "source":
            return self.source_alf_info["object"] + "." + self.source_alf_info["attribute"]
        else:
            raise ValueError("Value must be 'dest' or 'source'")

    @property
    def alf_info(self) -> dict:
        if self._alf_info is None:
            self._alf_info = one.alf.files.full_path_parts(
                self.source_path, as_dict=True, absolute=True, assert_valid=False
            )
        return self._alf_info

    @property
    def source_alf_info(self) -> dict:
        return one.alf.files.full_path_parts(self.source_path, as_dict=True, absolute=True, assert_valid=False)

    # this is usefull to get the renamed path in a dynamically updated version in the bulding stages.
    # Do not use it in the apply stages.
    @property
    def renamed_path(self) -> str:
        return one.alf.spec.to_full_path(**self.alf_info)

    def finish_cascade(self, records_list):
        # change the values of the filre record after all other actions have been resolved.
        # finish actions include calculating ,
        # checking if dest_path conflicts with a file already existing of other file's dest_path.

        self.path_conflicts = self.check_path_conflicts(records_list)
        if self.path_conflicts:
            self.abort.append("filepath_conflicts")

    @property
    def inclusion_accepted(self):
        if (
            self.include
            and self.valid_alf
            and self.dataset_type_exists
            and not self.path_conflicts
            and not self.abort
            and not self.delete
        ):
            return True
        return False

    def check_path_conflicts(self, records_list) -> bool:
        final_path = self.dest_path if self.rename else self.source_path

        conflicts = False

        for record in records_list:
            if (
                record.delete or record == self
            ):  # don't compare to itself in the list, or something that we will delete anyway
                continue
            record_final_path = record.dest_path if record.rename else record.source_path
            if final_path == record_final_path:
                conflicts = True

        return conflicts

    def apply_changes(self, do_deletes=True, do_renames=True):  # apply changes to file_record
        if self.delete and self.rename:
            raise ValueError("Cannot rename AND delete the same entry.")

        if self.rename and do_renames:
            collec_dir = os.path.dirname(self.dest_path)
            if not os.path.isdir(collec_dir):
                os.makedirs(collec_dir, exist_ok=True)
            os.rename(self.source_path, self.dest_path)

        if self.delete and do_deletes:
            os.remove(self.source_path)
            self.include = False

    def to_user_dict(self):
        return {
            "source_path": self.source_path,
            "dest_path": self.dest_path if self.rename else "",
            "info": self.info_message,
        }

    @property
    def info_message(
        self,
    ):  # message to make from action booleans to help the use understand what happened
        message = ""
        if self.inclusion_accepted and not self.rename:
            message = "included without change"

        if self.inclusion_accepted and self.rename:
            message = "renamed and included"

        if not self.inclusion_accepted and self.rename:
            message = "renamed and excluded"

        if not self.inclusion_accepted and not self.rename:
            message = "excluded without change"

        if not self.valid_alf:
            message = message + " doesn't follow alf format "

        if not self.dataset_type_exists:
            message = message + " dataset_type not existing "

        if self.delete:
            message = "auto deleted"

        if self.abort:
            message_prefix = "Aborting due to errors : "
            abort_messages = []
            for ab_msg in self.abort:
                if ab_msg == "filepath_conflicts":
                    ab_msg = "File name conflicts with a current file or another file that will be renamed identically"
                abort_messages.append(ab_msg)

            message = (
                message_prefix
                + ", ".join(abort_messages)
                # + " --- Without Abort, would have been "
                # + message
            )
        else:
            message = "Will be " + message

        return message


class Statement:
    allowed_operations = ["exact", "contain", "match"]
    allowed_elements = [
        "source_path",
        "subject",
        "date",
        "number",
        "root",
        "object",
        "attribute",
        "extension",
        "extra",
        "collection",
        "revision",
    ]

    def __init__(self, element, operation_detail, parent):
        self.inverted = False
        self.parent = parent

        for el in self.allowed_elements:
            if element == el:
                self.tested_element = element
                break
        else:
            raise ValueError(
                f"Tested element is {self.tested_element} wich is invalid value. "
                f"If must be one of :({''.join(self.allowed_elements)})"
            )

        if isinstance(operation_detail, dict):
            if len(operation_detail) != 1:
                raise ValueError(
                    f"Content of tested element {self.tested_element} is a dict. "
                    "Then it must contain only one key ({''.join(self.allowed_operations)})"
                )

            operation = list(operation_detail.keys())[0]
            conditions = operation_detail[operation]

            for op in self.allowed_operations:
                if op in operation:
                    self.operation = op
                    self.inverted = True if "_not" in operation else False
                    break
            else:
                raise ValueError(
                    f"Content of tested element {self.tested_element} is a dict and the key present was : {operation}. "
                    "It must contain one of : ({''.join(self.allowed_operations)}). "
                )
        else:
            self.operation = "exact"
            conditions = operation_detail

        if not isinstance(conditions, list):
            conditions = [conditions]

        if self.operation == "match":
            existing_patterns = self.patterns
            patterns = []
            for pattern_name in conditions:
                try:
                    patterns.append(existing_patterns[pattern_name])
                except KeyError:
                    raise ValueError(
                        f"Pattern {pattern_name} was asked in condition statement {self.tested_element} "
                        "but was not defined in re_patterns."
                    )
            conditions = patterns

        # self.operation is a string name of a method of the class that handles boolean matchong a condition.
        # self.operation_method is the actual bound method object that corresponds to that string
        self.operation_method = getattr(self, self.operation)
        self.conditions = conditions

    @property
    def patterns(self):
        return self.parent.patterns

    def evaluate(self, file_record):
        if self.tested_element == "source_path":
            value = file_record.alf_info.source_path
        else:
            value = file_record.alf_info[self.tested_element]
        boolean_return = self.operation_method(value)
        return not boolean_return if self.inverted else boolean_return

    def exact(self, value):
        for item in self.conditions:
            if item == value:
                return True
        return False

    def contain(self, value):
        for item in self.conditions:
            if item in value:
                return True
        return False

    def match(self, value):
        for pattern in self.conditions:
            if pattern.search(value):
                return True
        return False

    def __str__(self):
        return (
            f"{self.tested_element} {'~' if self.inverted else ''}{self.operation} -> "
            f"{', '.join([str(value) for value in self.conditions])}"
        )


class RuleConditions:
    def __init__(self, rule_dict, parent, rule_name=None, rule_type="all", inverted=False):
        allowed_types = ["all", "any"]
        rule_methods = [all, any]
        if rule_type not in allowed_types:
            raise ValueError(f"rule_type must be one of : {','. join(allowed_types)}")

        self.parent = parent
        self.rule_name = rule_name
        self.rule_type = rule_type
        self.rule_method = rule_methods[
            allowed_types.index(self.rule_type)
        ]  # get the actual python object corresponding to the rule type
        self.inverted = inverted
        self.sub_rules = []

        for key, value in rule_dict.items():
            allowed_types = ["all", "any"]
            for ty in allowed_types:
                if ty in key:
                    _rule_type = ty
                    _inverted = True if "_not" in key else False
                    sub_rule = RuleConditions(value, self, rule_type=_rule_type, inverted=_inverted)
                    break
            else:
                sub_rule = Statement(key, value, self)

            self.sub_rules.append(sub_rule)

    @property
    def patterns(self):
        return self.parent.patterns

    def evaluate(self, file_record):
        if isinstance(file_record, str):
            file_record = FileRecord(file_record)
        evaluations = []
        for condition in self.sub_rules:
            boolean_return = condition.evaluate(file_record)
            evaluations.append(boolean_return)
        boolean_return = self.rule_method(evaluations)

        boolean_return = not boolean_return if self.inverted else boolean_return
        if self.rule_name is None:
            return boolean_return

        file_record.match |= boolean_return
        if boolean_return:
            file_record.matching_rules.append(self.rule_name)
        return file_record

    def __str__(self):
        spacer = "\n    -  "
        line_return = "\n"
        sub_rules_str = spacer + spacer.join(str(value) for value in self.sub_rules)
        type_str = self.rule_type
        type_str += "~" if self.inverted else ""
        return f"{'    Conditions :' if self.rule_name else '    ' + type_str}{sub_rules_str}"


class RuleActions:
    allowed_actions = ["rename", "include", "delete", "exclude", "abort"]
    allowed_triggers = [
        "match",
        "destination_exists",
        "rename_unchanged",
        "rename_error",
    ]

    def __init__(self, rule_dict, rule_name, parent):
        self.rule_name = rule_name
        self.parent = parent
        self.triggers = rule_dict.get("on", {})
        if "match" not in self.triggers.keys():
            raise ValueError(
                f"match action wath not defined in rule {rule_name}. Must be defined. "
                "Set on : match to null if you wish to keep the rule but make it inactive."
            )

        if self.triggers["match"] is None:
            self.parent.active = False

        for key, value in self.triggers.items():
            if value == "rename" and "rename" not in rule_dict.keys():
                raise ValueError(
                    f"Trigger {key} in rule {rule_name} was defined with action rename, "
                    "but rename rules are not defined"
                )
            if key not in self.allowed_triggers:
                raise ValueError(
                    f"Trigger {key} in rule {rule_name} is invalid. Valid keys are {','.join(self.allowed_triggers)}"
                )
            if value not in self.allowed_actions:
                raise ValueError(
                    f"Action {value} in trigger {key} in rule {rule_name} is invalid. Valid keys are"
                    f" {','.join(self.allowed_actions)}"
                )

        self.rename_rule = rule_dict.get("rename", {})
        for key, value in self.rename_rule.items():
            if not isinstance(value, (str, dict)):
                raise ValueError(
                    f"{rule_name} rule errror in 'rename' with {key}. The content of a renaming the rule must be either"
                    " a constant string or a dictionnary. See documentation for more details."
                )

    @property
    def patterns(self):
        return self.parent.patterns

    def actions_cascade(self, file_record):
        if not file_record.match:
            return file_record

        match_action = self.triggers.get("match", None)
        if match_action is None:
            return file_record

        if not self.is_matching_rule(file_record):
            return file_record

        file_record.used_rule += self.rule_name + " "

        match_action_method = getattr(self, match_action)

        file_record = match_action_method(file_record, "match")

        return file_record

    def is_matching_rule(self, file_record):
        matching_rules = file_record.matching_rules

        # no conflict between two matched rules, return the only matching rule
        if len(matching_rules) == 1:
            return self.rule_name == matching_rules[0]

        # get a dict of "rule" : "list of overriding rules"
        overrides_dict = {rule_name: self.parent.parent.rules[rule_name].overrides for rule_name in matching_rules}

        overriden_rules = set()
        for rule_name, overrides in overrides_dict.items():
            for overriden_name in overrides:
                if overriden_name in matching_rules:
                    overriden_rules.add(overriden_name)

        remaining_rules = set(matching_rules).difference(overriden_rules)
        if len(remaining_rules) == 0:
            raise ValueError(
                f"{','.join(set(matching_rules))} rules may be mutually overriding. Please double check your rules set."
            )
        if len(remaining_rules) > 1:
            raise ValueError(
                f"{','.join(set(remaining_rules))} rules are matched together for one file and overridings are not"
                " defined for such cases. Please double check."
            )

        if self.rule_name == list(remaining_rules)[0]:
            return True
        return False

    def rename_element(self, file_record, element, rule):
        if isinstance(rule, str):  # constant replacement
            return rule
        # then, it must be a dictionnary with pattern defined
        pattern_name = rule["pattern"]
        search_on = rule.get("search_on", "source_path")
        if search_on == "source_path":
            searched_string = file_record.source_path
        else:
            searched_string = file_record.source_alf_info[search_on]  # TODO make a list check in __init__ for that

        try:
            match = self.patterns[pattern_name].search(searched_string)
        except KeyError:
            # TODO : move that in __init__ to avoid errors at rule runtime, and indicate them at compile time.
            raise ValueError(
                f"Pattern {pattern_name} was specified in rename action of rule : {self.rule_name} but that pattern was"
                " not defined in re_patterns."
            )

        # we make objects that we can use in case there is a matching or evaluation error.
        # action_if_error is a bound method instance of the current class,
        # that corresponds by name to what the user entered in "rename_match_error" : "" in rule in the json file.
        # defaults to the abort method.
        action_if_error = getattr(self, self.triggers.get("rename_match_error", "abort"))
        message_error_prefix = (
            f"{element} matching error. Searched on {search_on}, with pattern {pattern_name}, matched {match}."
        )

        if eval_string := rule.get("eval", None):
            try:
                return eval(eval_string)
            # this occurs when there is most likely not match.
            # Examples : NoneType is not supscriptable if match = None (TypeError)
            # or match[3] does not exist because match contains only two elements (IndexError)
            except (IndexError, TypeError) as e:
                action_if_error(
                    file_record,
                    message_error_prefix + f" Error : {e}. No match have been found. Test on https://regex101.com/",
                )
                return ""

            # this occurs when there is probably an error with the eval statement of the rule.
            except Exception as e:
                action_if_error(
                    file_record,
                    message_error_prefix + f" Error : {e}. Evaluation string is probably invalid.",
                )
                return ""
        else:  # eval is not specified. We then expect to use the first element of match as rename
            try:
                return match[0]
            # this occurs when there is most likely not match.
            except (IndexError, TypeError) as e:
                action_if_error(
                    file_record,
                    message_error_prefix
                    + f" Error : {e}. No match have been found for first element. Test on https://regex101.com/",
                )
                return ""  # we backtrack and don't change the element's value

    # actions :
    def rename(self, file_record, source):
        file_record.rename = True
        for element, rule in self.rename_rule.items():
            file_record.alf_info[element] = self.rename_element(file_record, element, rule)

        valid_alf = one.alf.spec.is_valid(file_record.renamed_path, one.alf.spec.FULL_ABSOLUTE_SPEC)

        if file_record.renamed_path == file_record.source_path:
            file_record.rename = False
            source_dest_identical_action_method = getattr(self, self.triggers.get("source_dest_identical", "include"))
            file_record = source_dest_identical_action_method(file_record, "source_dest_identical")

        # Removig the ability to check for file already existing here as anyway,
        # we don't know here if we will rename other files/ delete some.
        # These conflicts are checked at the end, within FileRecord.finish_cascade
        # elif os.path.isfile(file_record.renamed_path):
        #     file_record.rename = False
        #     destination_conflict_action_method = getattr(self, self.triggers.get(
        #         "destination_conflict", "abort"
        #     ))
        #     file_record = destination_conflict_action_method(file_record, 'destination_conflict')

        if not valid_alf:
            file_record.include = False
            file_record.rename = False
            invalid_alf_format_action_method = getattr(self, self.triggers.get("invalid_alf_format", "abort"))
            file_record = invalid_alf_format_action_method(file_record, "invalid_alf_format")
        else:
            file_record.include = True

        file_record.dest_path = file_record.renamed_path
        file_record.valid_alf = valid_alf

        return file_record

    def exclude(self, file_record, source):
        file_record.include = False
        return file_record

    def include(self, file_record, source):
        file_record.include = True
        return file_record

    def delete(self, file_record, source):
        file_record.delete = True
        return file_record

    def abort(self, file_record, source):
        file_record.abort.append(source)
        return file_record

    def __str__(self):
        spacer = "\n    -  "
        triggers_str = spacer + spacer.join([str(key) + " : " + str(value) for key, value in self.triggers.items()])
        rename_rule = spacer.join([str(key) + " : " + str(value) for key, value in self.rename_rule.items()])
        if rename_rule:
            rename_rule = "\n    Rename Rule :" + spacer + rename_rule
        override_rule = spacer.join(self.parent.overrides)
        if override_rule:
            override_rule = "\n    Overrides :" + spacer + override_rule
        return f"    Actions triggers :{triggers_str}{rename_rule}{override_rule}"


class Rule:
    def __init__(self, rule_dict, rule_name, parent):
        if "if" not in rule_dict.keys():
            raise ValueError(f"An if field must be defined in the rule {rule_name}")
        self.rule_name = rule_name
        self.parent = parent
        self.rule_conditions = RuleConditions(rule_dict["if"], self, rule_name=rule_name)
        self.rule_actions = RuleActions(rule_dict, rule_name, self)
        overrides = rule_dict.get("overrides", [])
        self.overrides = overrides if isinstance(overrides, list) else [overrides]
        self.active = True

    @property
    def patterns(self):
        return self.parent.patterns

    def evaluate(self, file_record):
        return self.rule_conditions.evaluate(file_record) if self.active else file_record

    def actions_cascade(self, file_record):
        return self.rule_actions.actions_cascade(file_record) if self.active else file_record

    def __str__(self):
        return f"Rule : {self.rule_name}" + "\n" + str(self.rule_actions) + "\n" + str(self.rule_conditions)


class Config:
    def __init__(self, rules_path=None, one_connector=None):
        if rules_path is None:
            data = pkgutil.get_data(__name__, "./rules.json").decode("utf-8")
            rules_config = json.loads(data)
        else:
            rules_config = json.load(open(rules_path, "r"))

        if one_connector is None:
            one_connector = one.ONE(data_access_mode="remote")
        self.one_connector = one_connector

        patterns = rules_config.get("re_patterns", {})
        compiled_paterns = {}
        for pattern_name, pattern in patterns.items():
            compiled_paterns[pattern_name] = re.compile(pattern)
        self.patterns = compiled_paterns

        self.rules = {
            rule_name: Rule(rule_dict, rule_name, self) for rule_name, rule_dict in rules_config["rules"].items()
        }

        self.excluded_folders = rules_config.get("excluded_folders", [])

        self.excluded_filenames = rules_config.get("excluded_filenames", [])

        self.cleanup_folders = rules_config.get("cleanup_folders", [])

        self.dataset_types = get_existing_datasets(one_connector)
        if len(self.dataset_types) == 0:
            raise ValueError(
                "dataset_types is empty. Cannot register any dataset if no dataset type exists. Maybe one's connector"
                " has a problem ?"
            )

    def registration_pipeline(self, session):
        file_records = self.evaluate_session(session)
        file_records = self.actions_cascade(file_records)
        if not self.is_applicable(file_records):
            print("Some conflicts are present, cannot continue.")
            return file_records
        selected_records = self.apply_to_files(file_records)
        records_groups = self.apply_to_alyx(session, selected_records)
        return records_groups

    def evaluate_session(self, session):
        folder = getattr(session, "path", None)
        if folder is None:
            session = self.one_connector.search(id=session, no_cache=True, details=True)
            folder = session["path"]

        files_list = find_files(folder, relative=False, levels=-1, get="files")

        return self.evaluate(files_list)

    def evaluate(self, file_list):
        file_records = [FileRecord(file_path) for file_path in file_list]

        records = []
        for file_record in file_records:
            skip = (
                False  # If we find that a find is in the excluded folders, we just discard it (not even try to match)
            )
            for collection in os.path.normpath(file_record.alf_info["collection"]).split(os.path.sep):
                if collection in self.excluded_folders:
                    skip = True
            if os.path.basename(file_record.source_path) in self.excluded_filenames:  # same for filenames
                skip = True
            if skip:
                continue

            for rule in self.rules.values():
                file_record = rule.evaluate(file_record)
            records.append(file_record)

        return records

    def actions_cascade(self, file_records):
        records = []
        for file_record in file_records:
            for rule in self.rules.values():
                file_record = rule.actions_cascade(file_record)

            # if file was not match by anything but still is a valid alf, we include it
            if not file_record.match:
                file_record.include = False
            if one.alf.spec.is_valid(file_record.source_path, one.alf.spec.FULL_ABSOLUTE_SPEC):
                file_record.valid_alf = True

            if file_record.valid_alf:
                if file_record.get_dataset_type() in self.dataset_types:
                    file_record.dataset_type_exists = True

            records.append(file_record)

        [record.finish_cascade(records) for record in records]

        return records

    def is_applicable(self, file_records):
        status = [len(file_record.abort) >= 1 for file_record in file_records]
        return not (any(status))

    def apply_to_files(self, file_records, do_deletes=True, do_renames=True, do_cleanup=True):
        # DELETING and RENAMING

        for file_record in file_records:
            file_record.apply_changes(do_deletes, do_renames)

        # just cleaning up empty folders after renaming.
        # could be improved to do recursive search.
        # this implementation may miss nested empty folders
        if do_cleanup:
            session_path = str(one.alf.files.get_session_path(file_records[0].source_path))
            folders_list = find_files(session_path, relative=True, levels=-1, get="folders")
            for folder in folders_list:
                if folder in self.cleanup_folders:
                    _folder_path = os.path.join(session_path, folder)
                    files_in_dir = find_files(_folder_path, relative=True, levels=-1, get="files")
                    if len(files_in_dir):
                        continue  # folder is not empty, we cannot clean it up
                    shutil.rmtree(_folder_path, ignore_errors=True)

        return file_records

    def apply_to_alyx(self, session, file_records):
        selected_records = []
        for file_record in file_records:
            if file_record.inclusion_accepted:
                selected_records.append(file_record)

        files_list = [
            file_record.dest_path if file_record.rename else file_record.source_path for file_record in selected_records
        ]

        self.one_connector.register.files(session, files_list)

    def __str__(self):
        spacer = "\n- "
        rules_str = spacer + spacer.join([str(rule) + "\n" for rule in self.rules.values()])
        return f"One-Registrator with configured rules : \n{rules_str}"
