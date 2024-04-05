import ast
import datetime
import time
from http.client import HTTPException
from typing import List, Tuple, Union

import requests
from django.utils.encoding import force_str
from haystack.backends import SQ
from haystack.backends.solr_backend import (
    SolrEngine,
    SolrSearchBackend,
    SolrSearchQuery,
)
from haystack.constants import DEFAULT_ALIAS, DOCUMENT_FIELD
from haystack.exceptions import NotHandled
from haystack.models import SearchResult
from haystack.query import SearchQuerySet
from pysolr import DATETIME_REGEX, IS_PY3, Solr, SolrError, force_bytes, force_unicode

from django_solr.models import EmptySearchResult

from .fields import NestedField

MAX_LOG_LENGTH = 25000


class DjangoSolr(Solr):
    def _send_request(self, method, path="", body=None, headers=None, files=None):
        url = self._create_full_url(path)
        method = method.lower()
        log_body = body

        if headers is None:
            headers = {}

        if log_body is None:
            log_body = ""
        elif not isinstance(log_body, str):
            log_body = repr(body)

        self.log.debug(
            "Starting request to '%s' (%s) with body '%s'...",
            url,
            method,
            log_body[:MAX_LOG_LENGTH],
        )
        start_time = time.time()

        session = self.get_session()

        try:
            requests_method = getattr(session, method)
        except AttributeError:
            raise SolrError("Unable to use unknown HTTP method '{0}.".format(method))

        # Everything except the body can be Unicode. The body must be
        # encoded to bytes to work properly on Py3.
        bytes_body = body

        if bytes_body is not None:
            bytes_body = force_bytes(body)
        try:
            resp = requests_method(
                url,
                data=bytes_body,
                headers=headers,
                files=files,
                timeout=self.timeout,
                auth=self.auth,
            )
        except requests.exceptions.Timeout as err:
            error_message = "Connection to server '%s' timed out: %s"
            self.log.exception(error_message, url, err)  # NOQA: G200
            raise SolrError(error_message % (url, err))
        except requests.exceptions.ConnectionError as err:
            error_message = "Failed to connect to server at %s: %s"
            self.log.exception(error_message, url, err)  # NOQA: G200
            raise SolrError(error_message % (url, err))
        except HTTPException as err:
            error_message = "Unhandled error: %s %s: %s"
            self.log.exception(error_message, method, url, err)  # NOQA: G200
            raise SolrError(error_message % (method, url, err))

        end_time = time.time()
        self.log.info(
            "Finished '%s' (%s) with body '%s' in %0.3f seconds, with status %s",
            url,
            method,
            log_body[:MAX_LOG_LENGTH],
            end_time - start_time,
            resp.status_code,
        )

        if int(resp.status_code) != 200:
            error_message = "Solr responded with an error (HTTP %s): %s"
            solr_message = self._extract_error(resp)
            self.log.error(
                error_message,
                resp.status_code,
                solr_message,
                extra={
                    "data": {
                        "headers": resp.headers,
                        "response": resp.content,
                        "request_body": bytes_body,
                        "request_headers": headers,
                    }
                },
            )
            raise SolrError(error_message % (resp.status_code, solr_message))

        return force_unicode(resp.content)

    def _to_python(self, value):
        """
        Converts values from Solr to native Python values.
        """
        if isinstance(value, (int, float, complex)):
            return value

        if isinstance(value, (list, tuple)):
            result = [self._to_python(v) for v in value]
            if isinstance(value, tuple):
                result = tuple(result)
            return result

        if value == "true":
            return True
        elif value == "false":
            return False

        is_string = False

        if IS_PY3:
            if isinstance(value, bytes):
                value = force_unicode(value)

            if isinstance(value, str):
                is_string = True
        else:
            if isinstance(value, str):
                value = force_unicode(value)

        if is_string:
            possible_datetime = DATETIME_REGEX.search(value)

            if possible_datetime:
                date_values = possible_datetime.groupdict()

                for dk, dv in date_values.items():
                    date_values[dk] = int(dv)

                return datetime.datetime(
                    date_values["year"],
                    date_values["month"],
                    date_values["day"],
                    date_values["hour"],
                    date_values["minute"],
                    date_values["second"],
                )

        try:
            # This is slightly gross but it's hard to tell otherwise what the
            # string's original type might have been.
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            # If it fails, continue on.
            pass

        return value


class ProjectSolrSearchBackend(SolrSearchBackend):
    def __init__(self, connection_alias, **connection_options):
        super().__init__(connection_alias, **connection_options)
        self.conn = DjangoSolr(connection_options["URL"], timeout=self.timeout, **connection_options.get("KWARGS", {}))

    TYPE_MAP = {
        "date": "pdate",
        "datetime": "pdate",
        "integer": "plong",
    }

    def build_schema(self, fields) -> Tuple[str, List[dict]]:
        """Метод используется для составления схемы данных.
        Перегружен только в части маппинга типов полей."""
        content_field_name = ""
        schema_fields = []

        for _, field_class in fields.items():
            field_data = {
                "field_name": field_class.index_fieldname,
                "type": "text",
                "indexed": "true",
                "stored": "true",
                "multi_valued": "false",
            }

            if field_class.document is True:
                content_field_name = field_class.index_fieldname

            if field_class.field_type in self.TYPE_MAP:
                field_data["type"] = self.TYPE_MAP[field_class.field_type]
            else:
                field_data["type"] = field_class.field_type

            if field_class.is_multivalued:
                field_data["multi_valued"] = "true"

            if field_class.stored is False:
                field_data["stored"] = "false"

            # Do this last to override `text` fields.
            if field_class.indexed is False:
                field_data["indexed"] = "false"

                # If it's text and not being indexed, we probably don't want
                # to do the normal lowercase/tokenize/stemming/etc. dance.
                if field_data["type"] == "text_en":
                    field_data["type"] = "string"

            # If it's a ``FacetField``, make sure we don't postprocess it.
            if hasattr(field_class, "facet_for"):
                # If it's text, it ought to be a string.
                if field_data["type"] == "text_en":
                    field_data["type"] = "string"

            schema_fields.append(field_data)

        return content_field_name, schema_fields


class SolrSearchResult(SearchResult):
    """
    Класс представления одной записи результата запроса.
    """

    def __getattr__(self, attr):
        return self.__dict__.get(attr, None)

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def django_id(self):
        """
        Возвращает значение первичного ключа результирующей модели,
        приведенного к типу данных в соответствии с полем модели.
        """
        *_, django_id = self.id.split(".")
        return self.model._meta.pk.to_python(django_id)

    def _nested_to_dict(
        self, field, nested: Union[dict, List[dict], None], fields_only: bool
    ) -> Union[dict, List[dict], None]:
        if nested is None:
            if field.has_default():
                return field.default
            return None
        if isinstance(nested, list):
            return self._multiple_nested_to_dict(field, nested=nested, fields_only=fields_only)
        if isinstance(nested, dict):
            value = self._single_nested_to_dict(field, nested=nested, fields_only=fields_only)
            if field.is_multivalued:
                return [value]
            return value
        raise ValueError("Nested field value must be dict or list of dict type")

    def _single_nested_to_dict(self, field, nested: dict, fields_only: bool) -> dict:
        _dict = {}
        if not nested:
            return _dict
        for field_name, field_instance in field.properties.items():
            if fields_only and not self.is_need_dump_field(field_name):
                continue
            value = nested.get(field_name)
            if isinstance(field_instance, NestedField):
                _dict[field_name] = self._nested_to_dict(field_instance, nested=value, fields_only=fields_only)
            else:
                if value is None and field_instance.has_default():
                    value = field_instance.default
                _dict[field_name] = field_instance.convert(value)
                if hasattr(field_instance, "model_field") and field_instance.model_field.primary_key:
                    _dict[field_instance.model_field.name] = _dict[field_name]

        return _dict

    def _multiple_nested_to_dict(self, field, nested: List[dict], fields_only: bool) -> List[dict]:
        _list = list()
        if not nested:
            return _list
        for single_nested in nested:
            _list.append(self._single_nested_to_dict(field, single_nested, fields_only))
        return _list

    def is_need_dump_field(self, field_name: str) -> bool:
        if self._fields:
            return field_name in self._fields
        return True

    def to_dict(self, fields_inheritance: bool = False) -> dict:
        """
        Метод приведения записи к словарю.
        По умолчанию в результирующий словарь добавляется поле `pk`
        со значением первичного ключа модели и атрибут, соответствующий имени
        первичного ключа, например:

            ---------------------------------------------------------------------
            class ModelWithGuidPk(models.Model):
                guid = models.CharField(default=uuid.uuid4, primary_key=True)
                ...

            instance = ModelWithGuidPk(guid="dc5017dd-6299-4957-8d07-b9daa5947956")
            ...

            Экземпляр строки для строки для индексированного экземпляра `instance`
            будет преобразован в словарь:
            {
                "pk": "dc5017dd-6299-4957-8d07-b9daa5947956",
                "guid": "dc5017dd-6299-4957-8d07-b9daa5947956",
                ...
            }
            ---------------------------------------------------------------------

            class ModelWithIdPk(models.Model):
                id = models.BigAutoField(primary_key=True)

            instance = ModelWithIdPk(id=123)
            ...

            Экземпляр строки для строки для индексированного экземпляра `instance`
            будет преобразован в словарь:
            {
                "pk": "123",
                "guid": 123,
                ...
            }
            ---------------------------------------------------------------------

        :param fields_inheritance: Учитывать перечень выводимых полей (`fields`) для вложенных объектов.
        """
        if self._dict is None:
            from haystack import connections

            try:
                index = connections[DEFAULT_ALIAS].get_unified_index().get_index(self.model)
            except NotHandled:
                return {}

            model_pk_field = self.model._meta.pk

            self._dict = {
                "pk": self.pk,
                model_pk_field.attname: self.django_id,
            }
            for field_name, field in index.fields.items():
                if not self.is_need_dump_field(field_name):
                    continue
                value = getattr(self, field_name, None)
                if field_name == DOCUMENT_FIELD and not value:
                    continue
                if isinstance(field, NestedField):
                    self._dict[field_name] = self._nested_to_dict(field, nested=value, fields_only=fields_inheritance)
                else:
                    if value is None and field.has_default():
                        value = field.default
                    self._dict[field_name] = field.convert(value)
        return self._dict


class SolrSearchQuerySet(SearchQuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._internal_fields = ["id", "django_ct", "django_id", "score"]
        self._fields = []

    def fields(self, *fields):
        """
        Метод ограничения полей для вывода результатов.

        :param fields: Перечень имен полей для включения в ответ.
        """
        self._fields = list(fields)
        return self

    def _clone(self, klass=None):
        """
        Внутренний метод клонирования себя с сохранением полей для вывода.
        """
        clone = super()._clone(klass)
        clone._fields = self._fields
        return clone

    def first(self) -> SolrSearchResult:
        """Получить первый элемент выборки."""
        return EmptySearchResult if not self.count() else self[0]

    def last(self) -> SolrSearchResult:
        """Получить последний элемент выборки."""
        return self[-1]

    def _fill_cache(self, start, end, **kwargs):
        if self._fields:
            query_fields = set(self._internal_fields)
            query_fields.update(self._fields)
            self.query.fields = list(query_fields)
        return super()._fill_cache(start, end, **kwargs)

    def nested(self, **kwargs):
        return self.narrow(ParentSQ(**kwargs))

    def nested_exists(self, nested: str):
        return self.narrow(ParentSQ(**{nested: None}))

    def post_process_results(self, results):
        """
        Метод пост-обработки результатов запроса.
        Метод перегружен присвоением атрибута `_fields` каждому результату для передачи полей,
        подлежащих включению в ответ.
        """
        results = super().post_process_results(results)
        for result in results:
            setattr(result, "_fields", self._fields)
        return results


class ProjectSolrSearchQuery(SolrSearchQuery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result_class = SolrSearchResult

    def build_params(self, spelling_query=None, **kwargs):
        kwargs = super().build_params(spelling_query, **kwargs)
        if "fields" not in kwargs:
            kwargs["fields"] = []
        kwargs["fields"].extend(["*", "score", "[child]"])
        return kwargs


class ProjectSolrEngine(SolrEngine):
    backend = ProjectSolrSearchBackend
    query = ProjectSolrSearchQuery


class EMPTY:
    pass


class ParentSQ(SQ):
    def __init__(self, **kwargs):
        self.exclude = kwargs.pop("exclude", False)
        super().__init__(**kwargs)
        self._full_path = EMPTY
        self._path = EMPTY
        self._value = EMPTY
        self._key = EMPTY
        if self.children:
            self._parse_args()

    def __repr__(self):
        return "<%s: %s %s>" % (
            self.__class__.__name__,
            self.connector,
            self.as_query_string(self._repr_query_fragment_callback),
        )

    def _parse_args(self):
        self._full_path, self._value = self.children[0]
        if isinstance(self.value, list):
            self._value = " ".join(self._value)
        *path_items, self._key = self._full_path.split(".")
        self._path = "/" + "/".join(path_items)

    @property
    def value(self):
        if self.children and self._value is EMPTY:
            self._parse_args()
        return self._value

    @property
    def path(self):
        if self.children and self._path is EMPTY:
            self._parse_args()
        return self._path

    @property
    def key(self):
        if self.children and self._key is EMPTY:
            self._parse_args()
        return self._key

    def _repr_query_fragment_callback(self, field, filter_type, value):
        parent = '{!parent which="*:* -_nest_path_:*"}'
        nest_path = f"/{self.key}" if self.path == "/" else self.path
        queries = [f'+_nest_path_:"{nest_path}"']  # noqa E231
        if value:
            if self.exclude:
                queries.append(f"-{field}:({force_str(value)})")  # noqa E231
            else:
                queries.append(f"+{field}:({force_str(value)})")  # noqa E231
        query = " ".join(queries)
        return f"{parent} ({query})"

    def as_query_string(self, *args, **kwargs):
        return self._repr_query_fragment_callback(self.key, self.connector, self.value)
