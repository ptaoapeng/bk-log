# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
from collections import defaultdict
import json

from home_application.handlers.metrics import HealthzMetricCollector
from home_application.constants import HEALTHZ_METRICS_IMPORT_PATHS


class HealthzHandler(object):
    def __init__(self) -> None:
        super().__init__()
        self.data = []

    def get_data(self, format_type: str, include_namespaces: list = None, exclude_namespaces: list = None):
        """
        将已通过 register_healthz_metric 注册的对应metric收集, 按照format输出成不同的格式
        Attributes:
            format_type: 数据格式类型, json | k8s
            include_namespaces: 允许上报的namespace列表
            exclude_namespaces: 不允许上报的namespace列表
        """
        self.data = HealthzMetricCollector(import_paths=HEALTHZ_METRICS_IMPORT_PATHS).collect(
            include_namespaces=include_namespaces, exclude_namespaces=exclude_namespaces
        )

        if format_type == "json":
            return self._json_data()

        return self._k8s_data()

    def _k8s_data(self):
        output = []
        for namespace in self.data:
            for metric in self.data[namespace]:
                if not metric["status"]:
                    output.append("[-]{} {} failed\n".format(metric["metric_name"], metric["timestamp"]))
                    continue
                output.append(
                    "[+]{} {} {} ok\n".format(metric["metric_name"], metric["timestamp"], metric["metric_value"])
                )

        return "".join(output).encode("utf-8")

    def _json_data(self):
        result = defaultdict(lambda: defaultdict(dict))
        for namespace in self.data:
            for metric in self.data[namespace]:
                result[namespace][metric["metric_name"]] = metric

        return json.dumps(result)
