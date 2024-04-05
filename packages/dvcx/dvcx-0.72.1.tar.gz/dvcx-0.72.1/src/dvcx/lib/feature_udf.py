import inspect
import sys
import traceback
from collections.abc import Sequence
from typing import Optional, Union

from dvcx.lib.feature import Feature, FeatureClass, FeatureClassSeq
from dvcx.lib.udf import Aggregator, BatchMapper, Generator, Mapper, UDFBase
from dvcx.lib.utils import DvcxError
from dvcx.query import Stream


class ValidationError(DvcxError):
    pass


class SchemaError(ValidationError):
    def __init__(self, udf_name: str, context: str, message: str):
        super().__init__(
            f"'{udf_name}' {context} " f"schema validation error: {message}"
        )


class OutputError(ValidationError):
    def __init__(self, udf_name: str, message: str, num: Optional[int] = None):
        num_str = "" if num is None else f"#{num + 1} "
        super().__init__(f"Output {num_str}of '{udf_name}' error: {message}")


class UserCodeError(DvcxError):
    def __init__(self, class_name: str, message: str):
        super().__init__(f"Error in user code in class '{class_name}': {message}")


class FeatureConvertor:
    @property
    def udf_params_list(self):
        return self._udf_params_list

    @property
    def udf_output_spec(self):
        return self._udf_output_spec

    @property
    def has_stream(self):
        return self._has_stream

    @property
    def cache(self):
        return self._udf.catalog.cache

    def __init__(
        self,
        udf: UDFBase,
        inputs: Union[FeatureClass, FeatureClassSeq] = (),
        outputs: Union[FeatureClass, FeatureClassSeq] = (),
    ):
        self._udf = udf

        self._inputs, self._is_single_input = self._convert_to_sequence(inputs)
        self._outputs, self._is_single_output = self._convert_to_sequence(outputs)

        self._validate_schema("params", self._inputs)
        self._validate_schema("output", self._outputs)

        self._has_stream = any(
            f._is_file  # type: ignore[attr-defined]
            for f in self._inputs
        )

        udf_params_spec = Feature._features_to_udf_spec(self._inputs)
        stream_prm = [Stream()] if self._has_stream else []
        self._udf_params_list = stream_prm + list(udf_params_spec.keys())

        self._udf_output_spec = Feature._features_to_udf_spec(self._outputs)  # type: ignore[attr-defined]

    @staticmethod
    def _convert_to_sequence(
        arg: Union[FeatureClass, FeatureClassSeq],
    ) -> tuple[FeatureClassSeq, bool]:
        if not isinstance(arg, Sequence):
            return [arg], True
        else:
            return arg, False

    def deserialize_objs(self, params, args):
        streams = []
        if self._has_stream:
            streams = [arg[0] for arg in args]
            args = [arg[1:] for arg in args]

        obj_rows = [self._params_to_objects(params, arg) for arg in args]
        for row, stream in zip(obj_rows, streams):
            for feature in row:
                if feature._is_file:
                    feature.set_catalog(self._udf.catalog)
                    feature.set_file(stream, self._udf.caching_enabled)

        return obj_rows

    def _params_to_objects(self, params, args):
        new_params = params if not self._has_stream else params[1:]
        return [cls._unflatten(dict(zip(new_params, args))) for cls in self._inputs]

    def _validate_schema(self, context: str, features: FeatureClassSeq):
        for type_ in features:
            if not isinstance(type_, type):
                raise SchemaError(
                    self._udf.name,
                    context,
                    "cannot accept objects, a 'Feature' class must be provided",
                )
            if not issubclass(type_, Feature):
                raise SchemaError(
                    self._udf.name,
                    context,
                    f"cannot accept type '{type_.__name__}', "
                    f"the type must be a subclass of 'Feature'",
                )

    def validate_output_obj(self, result_objs, *args, **kwargs):
        for row in result_objs:
            if not isinstance(row, (list, tuple)) and isinstance(
                self._outputs, (list, tuple)
            ):
                raise OutputError(
                    self._udf.name,
                    f"expected list of objects, "
                    f"but found a single value of type '{type(row).__name__}'",
                )

            if len(row) != len(self._outputs):
                raise OutputError(
                    self._udf.name,
                    f"length mismatch - expected {len(self._outputs)} "
                    f"objects, but {len(row)} were provided",
                )

            for num, (o, type_) in enumerate(zip(row, self._outputs)):
                if not isinstance(o, type_):
                    raise OutputError(
                        self._udf.name,
                        f"expected type '{type_.__name__}',"
                        f" but found type '{type(o).__name__}'",
                        num=num,
                    )

    def process_rows(self, rows, is_input_batched=True, is_output_batched=True):
        obj_rows = self.deserialize_objs(self._udf.params, rows)
        if self._is_single_input:
            obj_rows = [objs[0] for objs in obj_rows]

        if not is_input_batched:
            assert (
                len(obj_rows) == 1
            ), f"{self._udf.name} takes {len(obj_rows)} rows while it's not batched"
            obj_rows = obj_rows[0]

        result_objs = self.run_user_code(obj_rows)

        if not is_output_batched:
            result_objs = [result_objs]

        if self._is_single_output:
            result_objs = [[x] for x in result_objs]

        self.validate_output_obj(result_objs)

        res = [Feature._flatten_list(objs) for objs in result_objs]

        if not is_output_batched:
            assert len(res) == 1, (
                f"{self._udf.name} returns {len(obj_rows)} "
                f"rows while it's not batched"
            )
            res = res[0]
        return res

    def run_user_code(self, obj_rows):
        try:
            result_objs = self._udf.process(obj_rows)
            if inspect.isgeneratorfunction(self._udf.process):
                result_objs = list(result_objs)
        except Exception as e:
            msg = (
                f"============== Error in user code: '{self._udf.name}' =============="
            )
            print(msg)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback.tb_next)
            print("=" * len(msg))
            raise UserCodeError(self._udf.name, str(e)) from None
        return result_objs


class FeatureAggregator(Aggregator):
    def __init__(
        self,
        inputs: Union[FeatureClass, FeatureClassSeq] = (),
        outputs: Union[FeatureClass, FeatureClassSeq] = (),
        batch=1,
    ):
        self._fc = FeatureConvertor(self, inputs, outputs)
        super().__init__(self._fc.udf_params_list, self._fc.udf_output_spec, batch)

    def __call__(self, rows):
        return self._fc.process_rows(rows)


class FeatureMapper(Mapper):
    def __init__(
        self,
        inputs: Union[FeatureClass, FeatureClassSeq] = (),
        outputs: Union[FeatureClass, FeatureClassSeq] = (),
        batch=1,
    ):
        self._fc = FeatureConvertor(self, inputs, outputs)
        super().__init__(self._fc.udf_params_list, self._fc.udf_output_spec, batch)

    def __call__(self, *row):
        return self._fc.process_rows([row], False, False)


class FeatureBatchMapper(BatchMapper):
    def __init__(
        self,
        inputs: Union[FeatureClass, FeatureClassSeq] = (),
        outputs: Union[FeatureClass, FeatureClassSeq] = (),
        batch=1,
    ):
        self._fc = FeatureConvertor(self, inputs, outputs)
        super().__init__(self._fc.udf_params_list, self._fc.udf_output_spec, batch)

    def __call__(self, rows):
        return self._fc.process_rows(rows)


class FeatureGenerator(Generator):
    def __init__(
        self,
        inputs: Union[FeatureClass, FeatureClassSeq] = (),
        outputs: Union[FeatureClass, FeatureClassSeq] = (),
        batch=1,
    ):
        self._fc = FeatureConvertor(self, inputs, outputs)
        super().__init__(self._fc.udf_params_list, self._fc.udf_output_spec, batch)

    def __call__(self, *row):
        return self._fc.process_rows([row], False)
