# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Uses nearest neighbor search for similar examples."""

from typing import Optional

from lit_nlp.api import components as lit_components
from lit_nlp.api import dataset as lit_dataset
from lit_nlp.api import model as lit_model
from lit_nlp.api import types
from lit_nlp.components import index
from lit_nlp.lib import utils

JsonDict = types.JsonDict
IndexedInput = types.IndexedInput


class SimilaritySearcher(lit_components.Generator):
  """Searching by similarity."""

  def __init__(self, indexer: index.Indexer):
    self.index = indexer

  def _get_embedding(self, example: types.Input, model: lit_model.Model,
                     embedding_name: str):
    """Calls the model on the example to get the embedding."""
    model_output = model.predict([example])
    embedding = list(model_output)[0][embedding_name]
    return embedding

  def _find_nn(self, model_name, dataset_name, embedding_name, embedding):
    """wrapper around the Index() class api."""
    similar_examples = self.index.find_nn(
        model_name, dataset_name, embedding_name, embedding, num_neighbors=25)
    return similar_examples

  def is_compatible(self, model: lit_model.Model,
                    dataset: lit_dataset.Dataset) -> bool:
    dataset_embs = utils.spec_contains(dataset.spec(), types.Embeddings)
    model_in_embs = utils.spec_contains(model.input_spec(), types.Embeddings)
    model_out_embs = utils.spec_contains(model.output_spec(), types.Embeddings)
    return dataset_embs or model_in_embs or model_out_embs

  def generate(  # pytype: disable=signature-mismatch  # overriding-parameter-type-checks
      self,
      example: types.Input,
      model: lit_model.Model,
      dataset: lit_dataset.IndexedDataset,
      config: Optional[JsonDict] = None) -> list[JsonDict]:
    """Find similar examples for an example/model/dataset."""
    model_name = config['model_name']
    dataset_name = config['dataset_name']
    embedding_name = config['Embedding Field']
    embedding = self._get_embedding(example, model, embedding_name)
    neighbors = self._find_nn(model_name, dataset_name, embedding_name,
                              embedding)
    return neighbors

  def config_spec(self) -> types.Spec:
    return {
        # Requires an embedding layer specified from a model.
        'Embedding Field': types.SingleFieldMatcher(
            spec='output', types=['Embeddings'])
    }
