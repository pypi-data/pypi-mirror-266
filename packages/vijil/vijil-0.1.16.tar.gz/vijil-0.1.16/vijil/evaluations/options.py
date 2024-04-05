MODEL_HUB_CHOICES = ['huggingface', 'replicate', 'octo', 'openai', 'together', 'anyscale', 'mistral']
MODEL_NAMES_MAPPING = {
    'huggingface': ['gpt2', 'bigscience/bloom-560m', 'other'],
    'replicate': ['replicate/llama-7b', 'replicate/llama-13b-lora', 'other'],
    'octo': ['llama-2-7b-chat', 'other'],
}
PROBES_CHOICES = [
            'Security', 'Toxicity', 'Hallucination', 
            'Ethics',"Privacy", "Stereotype", 
            "Fairness", "Robustness"
        ]
PROBES_DIMENSIONS_MAPPING = {
    'security': 'dan,encoding,gcg,glitch,knownbadsignatures,replay,malwaregen,packagehallucination,promptinject,xss',
    'toxicity': 'atkgen,continuation,realtoxicityprompts',
    'hallucination': 'goodside,snowball,misleading,packagehallucination',
    'ethics': 'lmrc,hendrycksethics',
    'privacy': 'leakreplay,replay',
    'stereotype': 'advstereo',
    'fairness': 'adultdata,winobias',
    'robustness': 'advglue'
}
DTYPE_CHOICES = ['private', 'public']

MODEL_TYPE_MAPPING = {
    'huggingface': 'HF',
    'replicate': 'Replicate',
    'octo': 'Octo',
    'openai': 'Open',
    'together': 'together',
    'anyscale': 'anyscale',
    'mistral': 'mistral',
}
