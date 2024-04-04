# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Placeholder docstring"""
from __future__ import absolute_import

XGBOOST_NAME = "xgboost"
XGBOOST_UNSUPPORTED_VERSIONS = {
    "1.1": (
        "XGBoost 1.1 is not supported on SageMaker because XGBoost 1.1 has broken capability to "
        "run prediction when the test input has fewer features than the training data in LIBSVM "
        "inputs. This capability has been restored in XGBoost 1.2 "
        "(https://github.com/dmlc/xgboost/pull/5955). Consider using SageMaker XGBoost 1.2-1."
    ),
}
