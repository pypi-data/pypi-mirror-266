# -*- coding: utf-8 -*-

"""""""""""""""""""""""""""""""""
dart_fss 의 Table 클래스
"""""""""""""""""""""""""""""""""
# -*- coding: utf-8 -*-
import re
import numpy as np
import pandas as pd
import pydash as _
from dateutil.relativedelta import relativedelta

from arelle import XbrlConst
from .dartfss_utils import str_to_regex
from .dartfss_helper import cls_label_check, get_label_list, cls_merge_type, cls_datetime_check, get_max_depth, get_value_from_dataset, generate_df_columns, generate_df_rows, flatten, get_title, prefered_sign


class Table(object):
    def __init__(self, parent, xbrl, code, definition, uri):
        self.parent = parent
        self.code = code
        self.definition = definition
        self.uri = uri
        self._xbrl = xbrl
        self._facts = None
        self._dataset = None
        self._cls = None
        self._labels = None

    @property
    def facts(self):
        """list of modelFact: """
        if self._facts is None:
            arcrole = XbrlConst.parentChild
            relation = self._xbrl.relationshipSet(arcrole, self.uri)
            facts = []
            for fact in self._xbrl.facts:
                if relation.fromModelObject(fact.concept) \
                        or relation.toModelObject(fact.concept):
                    facts.append(fact)
            self._facts = facts
        return self._facts

    @property
    def dataset(self):
        """dict of modelFact: """
        if self._dataset is None:
            dataset = dict()
            for fact in self.facts:
                object_id = fact.context.objectId()
                if dataset.get(object_id) is None:
                    dataset[object_id] = []
                dataset[object_id].append(fact)

            self._dataset = dataset
        return self._dataset

    @property
    def cls(self):
        """classification 반환"""
        if self._cls is None:
            self._get_cls()
        return self._cls

    def cls_filter(self, start_dt=None, end_dt=None, label=None):
        return [item for item in self.cls
                if cls_datetime_check(item, start_dt, end_dt) and cls_label_check(item, label)]

    def _get_cls(self):
        """ classification 정보 추출 함수"""
        contexts = set()
        for data in self.facts:
            context = data.context
            contexts.add(context)

        cls = list()
        for context in contexts:
            object_id = context.objectId()

            # data가 없을때 무시
            if len(self.dataset[object_id]) < 1:
                continue

            instant_datetime = None
            start_datetime = None
            end_datetime = None
            if context.isInstantPeriod is True:
                instant_datetime = context.instantDatetime - relativedelta(days=1)

            else:
                start_datetime = context.startDatetime
                end_datetime = context.endDatetime - relativedelta(days=1)

            label = dict()
            dims = context.qnameDims
            if len(dims) > 0:
                for dimQname in sorted(dims.keys(), key=lambda d: str(d), reverse=True):
                    dim_value = dims[dimQname]
                    ko = dim_value.member.label(lang='ko')
                    ko = re.sub(r'\[.*?\]', '', ko)
                    en = dim_value.member.label(lang='en')
                    en = re.sub(r'\[.*?\]', '', en)
                    label[dimQname] = {
                        'ko': ko,
                        'en': en
                    }
            _cls = {
                'cls_id': object_id,
                'instant_datetime': instant_datetime,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'label': label
            }
            cls.append(_cls)
        cls.sort(key=lambda x: x.get('instant_datetime') or x.get('start_datetime'), reverse=True)
        self._cls = cls
        return self._cls

    @property
    def labels(self):
        """labels 반환"""
        if self._labels is None:
            self._labels = []
            arcrole = XbrlConst.parentChild
            relationship_set = self._xbrl.relationshipSet(arcrole, self.uri)
            for idx, root_concept in enumerate(relationship_set.rootConcepts):
                labels = get_label_list(relationship_set, root_concept, relationship_set.modelRelationships[idx])
                self._labels.append(labels)
        return self._labels

    def to_DataFrame(self, cls=None, lang='ko', start_dt=None, end_dt=None,
                     label=None, show_abstract=False, show_class=True, show_depth=10,
                     show_concept=True, separator=True, ignore_subclass=True):

        if cls is None:
            cls = self.cls_filter(start_dt, end_dt, label)
        cls = cls_merge_type(cls)

        depth = -1
        for label in self.labels:
            depth = max(depth, get_max_depth(label, show_abstract=show_abstract))
        depth = depth if depth < show_depth else show_depth

        table = self.parent.get_table_by_code('d999004')
        unit = get_value_from_dataset(table.cls, table.dataset, 'dart-gcd_EntityReportingCurrencyISOCode', ignore_case=True)

        definition = self.definition + ' (Unit: {})'.format(unit[0])
        columns = generate_df_columns(definition, cls, depth, lang,
                                      show_concept=show_concept, show_class=show_class)

        if separator:
            pd.options.display.float_format = '{:,}'.format
        else:
            pd.options.display.float_format = '{:}'.format
        df = pd.DataFrame(columns=columns)

        rows = []
        for label in self.labels:
            r = generate_df_rows(label, cls, self.dataset, depth, lang=lang,
                                 show_abstract=show_abstract, show_concept=show_concept, show_class=show_class)
            rows.append(r)
        rows = flatten(rows)
        data = flatten(rows)
        for idx, r in enumerate(data):
            df.loc[idx] = r

        regex_pass = str_to_regex('concept_id OR label_ko OR label_en OR class')
        df_count = df.count()
        drop_columns = []
        for key, count in df_count.items():
            if regex_pass.search(' '.join(key[1])):
                pass
            elif count < 1:
                drop_columns.append(key)
        df = df.drop(drop_columns, axis=1)

        if ignore_subclass:
            columns = np.array([x for x in df.columns if not isinstance(x[1], tuple) or len(x[1]) == 1], dtype=object)
            return df[columns]

        return df

    def get_value_by_concept_id(self, concept_id, start_dt=None, end_dt=None, label=None, lang='en'):
        cls = self.cls_filter(start_dt, end_dt, label)

        def search_concept_id(labels, concept):
            for l in labels:
                if l['concept_id'] == concept:
                    return True, l['preferred']
                elif l['children']:
                    result = search_concept_id(l['children'], concept)
                    if result[0]:
                        return result
            return False, None

        sign = 1.0
        retcode, preferred = search_concept_id(self.labels, concept_id)
        if retcode:
            sign = prefered_sign(preferred)

        data = get_value_from_dataset(classification=cls, dataset=self.dataset,
                                      concept_id=concept_id, sign=sign)
        results = dict()
        for c, d in zip(cls, data):
            title = get_title(c, lang=lang)
            results[title] = d
        return results
    def __repr__(self):
        info = {
            'code': self.code,
            'definition': self.definition
        }
        return str(info)


"""""""""""""""""""""""""""""""""
dart_fss 의 DartXbrl 클래스
"""""""""""""""""""""""""""""""""
import re
from typing import List, Union
from arelle import ModelXbrl, XbrlConst
from .dartfss_utils import str_compare
from .dartfss_helper import consolidated_code_to_role_number


class DartXbrl(object):
    def __init__(self, xbrl: ModelXbrl):
        self.xbrl = xbrl
        self._tables = None

    @property
    def tables(self) -> List[Table]:
        if self._tables is not None:
            return self._tables

        arcrole = XbrlConst.parentChild
        relationship = self.xbrl.relationshipSet(arcrole)

        tables = None
        if relationship is not None:
            tables = []
            for uri in relationship.linkRoleUris:
                role_types = self.xbrl.roleTypes.get(uri)

                if role_types is not None:
                    definition = (role_types[0].genLabel(lang='ko', strip=True)
                                  or role_types[0].definition or uri)
                else:
                    definition = uri

                role_code = re.search(r"(D?\d{6})", definition)
                role_code = role_code.group(1) if role_code else None
                tables.append(Table(self, self.xbrl, role_code, definition, uri))

        tables.sort(key=lambda x: x.code)
        self._tables = tables
        return tables

    def get_table_by_code(self, code: str) -> Union[Table, None]:
        for table in self.tables:
            if str_compare(table.code, code):
                return table
        return None

    def get_table_by_name(self, name: str, separate:bool = False) -> Union[List[Table], None]:
        regex = re.compile(name, re.IGNORECASE)
        regex2 = re.compile("consolidated" if not separate else "separate", re.IGNORECASE)

        tables = []
        for table in self.tables:
            if re.search(regex, table.definition) and re.search(regex2, table.definition):
                tables.append(table)
        return tables if len(tables) > 0 else None

    def _get_statement(self, concept_id: str, separate: bool = False) -> Union[List[Table], None]:
        table = self.get_table_by_code('d999007')
        if table is None:
            return None
        table_dict = table.get_value_by_concept_id(concept_id)
        compare_name = 'Separate' if separate else 'Consolidated'

        dataset_title = {
            'dart-gcd_StatementOfFinancialPosition': '재무상태표',
            'dart-gcd_StatementOfComprehensiveIncome': '손익계산서',
            'dart-gcd_StatementOfChangesInEquity': '자본변동표',
            'dart-gcd_StatementOfCashFlows': '현금흐름표',
        }

        try:
            for keys, value in table_dict.items():
                for key in keys:
                    title = ''.join(key)
                    if re.search(compare_name, title, re.IGNORECASE):
                        code_list = consolidated_code_to_role_number(value, separate=separate)
                        tables = [self.get_table_by_code(code) for code in code_list]
                        return tables
        except KeyError as e:
            print("KeyError: ", e)
            return self.get_table_by_name(dataset_title[concept_id], separate=separate)
        return None

    def get_financial_statement(self, separate: bool = False) -> Union[List[Table], None]:
        return self._get_statement('dart-gcd_StatementOfFinancialPosition', separate=separate)

    def get_income_statement(self, separate: bool = False) -> Union[List[Table], None]:
        return self._get_statement('dart-gcd_StatementOfComprehensiveIncome', separate=separate)

    def get_changes_in_equity(self, separate: bool = False) -> Union[List[Table], None]:
        return self._get_statement('dart-gcd_StatementOfChangesInEquity', separate=separate)

    def get_cash_flows(self, separate: bool = False) -> Union[List[Table], None]:
        return self._get_statement('dart-gcd_StatementOfCashFlows', separate=separate)
    
    
"""""""""""""""""""""""""""""""""
이 아래부터는 내가 직접 구현한 것들
"""""""""""""""""""""""""""""""""
import os, sys, logging
from arelle import Cntlr

def download_xbrl(api_key:str, download_dir:str, dart_report_id:str) -> str:
    import io
    import requests
    import zipfile

    url = 'https://opendart.fss.or.kr/api/fnlttXbrl.xml'
    params = {
        'crtfc_key': api_key,
        'rcept_no': dart_report_id,
    }
    # Request Download
    res = requests.get(url=url, params=params)
    try:
        if "파일이 존재하지 않습니다" in res.content.decode():
            print("[XBRL 파일이 존재하지 않습니다] URL: ", res.url)
            return
    except:
        pass
        
    with zipfile.ZipFile(io.BytesIO(res.content)) as f:
        f.extractall(download_dir)
    
    filepath = _.find(os.listdir(download_dir), lambda x: x.endswith("xbrl"))
    filepath = os.path.join(download_dir, filepath)
    return filepath


def get_dartfss_xbrl(api_key:str, dart_report_id:str) -> DartXbrl:
    import tempfile
    with tempfile.TemporaryDirectory(dir="/tmp") as tempdir:
        if filepath := download_xbrl(api_key, tempdir, dart_report_id):
            # PyPI를 통해 설치된 Arelle 라이브러리 사용시 발생하는 오류 수정을 위한코드
            if sys.platform == 'win32':
                pass
            elif sys.platform == 'darwin':
                arelle_app_dir = os.path.join(os.path.expanduser('~/Library/Application Support'), 'Arelle')
                if not os.path.exists(arelle_app_dir):
                    os.makedirs(arelle_app_dir)
            else:
                arelle_app_dir = os.path.join(os.path.expanduser("~/.config"), "arelle")
                if not os.path.exists(arelle_app_dir):
                    os.makedirs(arelle_app_dir)

            cntlr = Cntlr.Cntlr(logFileName='logToStdErr')
            cntlr.logger.setLevel(logging.CRITICAL)
            model_xbrl = cntlr.modelManager.load(filepath)
            xbrl = DartXbrl(model_xbrl)
            return xbrl
        

__all__ = ['get_xbrl']