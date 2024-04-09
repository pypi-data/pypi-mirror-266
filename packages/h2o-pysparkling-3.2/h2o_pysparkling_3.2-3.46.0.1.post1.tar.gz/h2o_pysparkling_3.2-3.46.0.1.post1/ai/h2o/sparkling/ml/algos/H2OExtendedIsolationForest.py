#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from warnings import warn
from pyspark import keyword_only
from ai.h2o.sparkling.Initializer import Initializer
from ai.h2o.sparkling.ml.Utils import Utils
from ai.h2o.sparkling.ml.algos.H2OTreeBasedUnsupervisedAlgorithm import H2OTreeBasedUnsupervisedAlgorithm
from ai.h2o.sparkling.ml.models.H2OExtendedIsolationForestMOJOModel import H2OExtendedIsolationForestMOJOModel
from ai.h2o.sparkling.ml.params.H2OExtendedIsolationForestParams import H2OExtendedIsolationForestParams


class H2OExtendedIsolationForest(H2OExtendedIsolationForestParams, H2OTreeBasedUnsupervisedAlgorithm):

    @keyword_only
    def __init__(self,
                 ignoredCols=None,
                 columnsToCategorical=[],
                 keepBinaryModels=False,
                 withContributions=False,
                 dataFrameSerializer="ai.h2o.sparkling.utils.JSONDataFrameSerializer",
                 withLeafNodeAssignments=False,
                 convertInvalidNumbersToNa=False,
                 detailedPredictionCol="detailed_prediction",
                 validationDataFrame=None,
                 featuresCols=[],
                 predictionCol="prediction",
                 convertUnknownCategoricalLevelsToNa=False,
                 splitRatio=1.0,
                 withStageResults=False,
                 ntrees=100,
                 sampleSize=256,
                 extensionLevel=0,
                 seed=-1,
                 scoreTreeInterval=0,
                 disableTrainingMetrics=True,
                 modelId=None,
                 categoricalEncoding="AUTO",
                 ignoreConstCols=True,
                 scoreEachIteration=False):
        Initializer.load_sparkling_jar()
        super(H2OExtendedIsolationForest, self).__init__()
        self._java_obj = self._new_java_obj("ai.h2o.sparkling.ml.algos.H2OExtendedIsolationForest", self.uid)
        self._setDefaultValuesFromJava()
        kwargs = Utils.getInputKwargs(self)
        kwargs = self._updateInitKwargs(kwargs)

        if 'interactionPairs' in kwargs:
            warn("Interaction pairs are not supported!")
        self._set(**kwargs)
        self._transfer_params_to_java()

    def _create_model(self, javaModel):
        return H2OExtendedIsolationForestMOJOModel(javaModel)
