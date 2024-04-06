# Exploring LLM Priming Strategies for Few-Shot Stance Classification

How does priming affect prompt-based learing?
This project aims at analyzing this effect in stance classification.
We train a stance classifier on the ibm stance classification dataset by
fine-tuning an Alpaca model with a prompt and analyzing how does the selection
of the few shots used in the prompt affect the performance of the model.

1) To evaluate the prompt-fine-tuning, run the following command
* Hyperparamter optimization
```
python scripts/run_prompt_fine_tuning.py --validate --optimize 
```

* Best Hyperparameters
```
python scripts/run_prompt_fine_tuning.py --validate --optimize 
``` 
2) To evaluate the in-context (prompt) setup run
```
python scripts/run_prompting.py --validate --optimize 
```
3) To evaluate DeBERTa (a normal classifier) with all hyperparameters, run the following
```
python scripts/optimize_baseline.py 
```

4) To evaluate Alpaca in a instructional tuning model run the following:
```
/run_prompt_fine_tuning.py --validate --optimize --alpaca
```
5) to evaluate Alpaca in using prompting you can run

```
/run_prompt_fine_tuning.py --validate --no-fine-tuning --alpaca
```
6) ro run the majority baseline
```
 python baseline.py --vast --majority --offline
```


The results of the experiments will be logged to your home directory.
The parameters can be saved in [config.yaml](../blob/maser/config.yaml)
## Priming Sampling strategies
To run an experiment with a similar sampling strategy use the parameter ```--similar-examples```. This will retrieve
examples that are similar to each test instance. The similarity measure can be Sentence-Transformers ```--sentence-transformer```.
Example,

```python scripts/run_prompting.py --validate --topic-similar --sentence-transformer```


To run an experiment with a diversification sampling strategy use the parameter ```--diverse-examples```. This
will takes precomputed cluster centers of the training set as few shots. The number of clusters is then the few shot count
provided in the configuration.
## Topic Similarity
Examples on similar or diverse topics are sampled using a topic similarity, which relies on sentence transformer. 
the similarities can be used to apply the right sampling strategy.

1) To compute the similarities between all the validation and training arguments run the following
```
python scripts/run_develop_similarity_measure.py --compute-similarity --validate 
```
You have to specify the model used to compute the similarity to be ```--sentence-transformer``` 

To load similarities from the code you can use the

```similarities = load_similarities("ibmsc", "validation", similarity)```

which returns a dictionary of dictionary where the indices of the first dictionary are the test indices and the indeices
of the nested dictionary for each test index are the indices of the training set with the values being the similarity scores.

To find similar or diverse arguments for an argument in the validation or test set, you can use

```examples = sample_diverse_examples(experiment, experiment_type, few_shot_size)```

similar can be used for sample_similar

```examples = sample_similar_examples(test_istance_index, similarities, df_training, few_shot_size)```

Similar examples for both datasets are cached for efficiency and can be created by running the following commands
``` python scripts/save_similar_examples.py --ks --topic-count --vast  ```
## Topic Diversification

To sample diverse examples, we use ward hierarchical clustering algorithm to cluster the trianing examples into $k$ cluster.
The center of each cluster is then taken as an example. To find the diverse examples, we use the following command


```
python scripts/run_sample_diverse_examples --vast --validate --ibmsc 
```
This will precompute the cluster centers for k in  ```[2, 4, 8, 16, 32, 64]```
To sample diverse examples, you can use the following command

```examples = sample_diverse_examples(experiment, experiment_type, few_shot_size)``` where experiment is ibmsc or vast
and experiment_type is validation or test.

## Analysis

Mainly there are three types of analyses implemented on the prompting and instruction fine-tuning approaches. 
### Few shot size or training topic count effect on priming approaches
1. Run prompting or prompt-fine tuning approaches with anaylze k or analyze-topic-count as folows 
```
python scripts/run_prompt_fine_tuning.py --analyze-k  --k 16 --seed 488
``` 
or 
```
python scripts/run_prompt_fine_tuning.py --analyze-topic-count --topic-count 11 --seed 488
``` 

The ks or topic-counts are stored in [conf.yaml](conf) and the analysis will be run for multiple seeds and the 
performance will be averaged and saved in the corresponding entry in /bigwork/nhwpajjy.
To perform an analysis for one k or topic count instnance you can give it as a parameter using --k or --topic-count
to produce the results for one seed you can specify the seed using --k

2. Store the path of the produced csv feel in [conf.yaml](conf.yaml)
 ``` analyze-k or analyze-topic-count ```

3. Draw the visualization using by running
```
python script/run_visualize_over_k_performance.py --k --topic-count --prompting --prompt-fine-tuning
```

### Prime Anaylsis

To save the topically examples used for priming Alpaca, you can run the following. This will produce the test instances
and the sampled claims in the following file.
```/bigwork/nhwpajjy/few-shot-priming/results/prime-analysis.tsv```

```
python script/run_prompt_fine_tuning.py --analyze-primes
```
