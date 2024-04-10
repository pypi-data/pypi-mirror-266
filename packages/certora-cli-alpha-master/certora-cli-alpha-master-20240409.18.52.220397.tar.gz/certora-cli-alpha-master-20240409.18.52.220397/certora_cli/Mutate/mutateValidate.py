from pathlib import Path
import sys

scripts_dir_path = Path(__file__).parent.resolve()
sys.path.insert(0, str(scripts_dir_path))

from Mutate import mutateAttribute as Attr
import EVMVerifier.certoraContextAttribute as ProvAttr
from Shared import certoraAttrUtil as AttrUtil
from Shared import certoraUtils as Util
from typing import Tuple, Any
from Mutate import mutateApp as App
from Mutate import mutateConstants as Constants


class MutateValidator:
    def __init__(self, mutate_app: App.MutateApp):
        self.mutate_app = mutate_app

    def validate(self) -> None:
        self.mutation_attribute_in_prover()
        self.validate_arg_types()
        self.validate_gambit_objs()
        self.illegal_combinations()

    def mutation_attribute_in_prover(self) -> None:
        gambit_attrs = ['filename', 'contract', 'functions', 'seed', 'num_mutants']
        mutation_attrs = [str(attr) for attr in Attr.MutateAttribute]
        prover_attrs = [str(attr) for attr in ProvAttr.ContextAttribute]
        for key in self.mutate_app.prover_dict:
            if key not in prover_attrs:
                if key in mutation_attrs:
                    raise Util.CertoraUserInputError(f"{key} is a legal mutation key but illegal prover attribute, "
                                                     "should it be under the mutation section? ")
                if key in gambit_attrs:
                    raise Util.CertoraUserInputError(f"{key} is a legal gambit key but illegal prover attribute, "
                                                     "should it be under a gambit section? ")

    def illegal_combinations(self) -> None:
        #  TODO
        # if not self.mutate_app.gambit and self.mutate_app.outdir:
        #     raise Util.CertoraUserInputError("outdir should not be set if gambit is not called")
        if not self.mutate_app.gambit and not self.mutate_app.manual_mutants:
            raise Util.CertoraUserInputError("at least one gambit object or manual mutant "
                                             "must exist in the config file")

    def validate_gambit_objs(self) -> None:
        if self.mutate_app.gambit:
            for el in self.mutate_app.gambit:
                for key in el.keys():
                    lkey = key.lower()
                    if lkey.startswith(Constants.SOLC):
                        raise Util.CertoraUserInputError("flags to Solidity should be set from the original run not "
                                                         f"inside the gambit entry in the conf file ({lkey})")
                    if lkey in [str(Constants.OUTDIR), Constants.SKIP_VALIDATE, Constants.GAMBIT_NO_OVERWRITE]:
                        raise Util.CertoraUserInputError(f"{lkey} not allowed inside embedded gambit object when "
                                                         f"running certoraMutate")

    def validate_arg_types(self) -> None:

        for arg in Attr.MutateAttribute:
            attr = getattr(self.mutate_app, str(arg), None)
            if attr is None or (attr is False and AttrUtil.AttrArgType.BOOLEAN):
                continue

            if arg.value.arg_type == AttrUtil.AttrArgType.STRING:
                self.validate_type_string(arg)
            elif arg.value.arg_type == AttrUtil.AttrArgType.BOOLEAN:
                self.validate_type_boolean(arg)
            elif arg.value.arg_type == AttrUtil.AttrArgType.INT:
                self.validate_type_int(arg)
            elif arg.value.arg_type == AttrUtil.AttrArgType.MAP:
                self.validate_type_any(arg)
            else:
                raise RuntimeError(f"{attr.value.arg_type} - unknown arg type")

    def validate_type_string(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"calling validate_type_string with null value {key}")
        if not isinstance(value, str) and not isinstance(value, Path):
            raise Util.CertoraUserInputError(f"value of {key} {value} is not a string")
        attr.validate_value(str(value))

    def validate_type_any(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"calling validate_type_any with null value {key}")
        attr.validate_value(value)

    def validate_type_int(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"calling validate_type_string with null value {key}")
        if not isinstance(value, int):
            raise Util.CertoraUserInputError(f"value of {key} {value} is not an integer")
        attr.validate_value(str(value))

    def validate_type_boolean(self, attr: Attr.MutateAttribute) -> None:
        key, value = self.__get_key_and_value(attr)

        if value is None:
            raise RuntimeError(f"{key}: calling validate_type_boolean with None")
        elif type(value) is list and len(value) == 0:
            setattr(self.mutate_app, key, True)
        elif value not in [True, False]:
            raise Util.CertoraUserInputError(f"value of {key} {value} is not a boolean (true/false)")

    def __get_key_and_value(self, attr: Attr.MutateAttribute) -> Tuple[str, Any]:
        key = str(attr)
        value = getattr(self.mutate_app, key, None)
        return key, value
