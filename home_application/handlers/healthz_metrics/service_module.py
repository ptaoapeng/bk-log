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
import os
import time
import logging

import requests
from django.utils.translation import ugettext as _

from home_application.handlers.metrics import register_healthz_metric, HealthzMetric, NamespaceData

logger = logging.getLogger()


class HomeMetric(object):
    @staticmethod
    @register_healthz_metric(namespace="service_module")
    def check():
        namespace_data = NamespaceData(namespace="service_module", status=False, data=[])
        ping_result = HomeMetric().ping()
        namespace_data.status = [i.status for i in ping_result].count(True) == len(ping_result)
        if not namespace_data.status:
            namespace_data.message = _("服务模块检查失败, 请查看细节")

        namespace_data.data.extend(ping_result)
        return namespace_data

    @staticmethod
    def ping():
        data = []
        result = HealthzMetric(status=False, metric_name="home")
        start_time = time.time()
        try:
            import sys
            host = "localhost"
            port = os.environ.get("PORT", 8000)
            if "runserver" in sys.argv and len(sys.argv) > 2:
                addr = sys.argv[2]
                url = f"http://{addr}/"
            else:
                url = f"http://{host}:{port}/"
            resp = requests.get(url)
            if resp.status_code == 200:
                result.status = True
            else:
                result.message = f"failed to call {url}, status_code: {resp.status_code}, msg: {resp.text}"
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"failed to call {url}, err: {e}")
            return data
        spend_time = time.time() - start_time
        result.metric_value = "{}ms".format(int(spend_time * 1000))
        data.append(result)
        return data
