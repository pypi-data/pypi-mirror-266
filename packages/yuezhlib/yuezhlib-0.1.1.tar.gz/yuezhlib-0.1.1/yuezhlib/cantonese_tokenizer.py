import json
import pycantonese
from tokenizers.normalizers import Normalizer
#from tokenizers.decoders import Decoder
from tokenizers import (
    decoders,
    models,
    trainers,
    processors,
    Tokenizer,
    Regex, 
    NormalizedString, 
    PreTokenizedString
)
from tokenizers.pre_tokenizers import (
	BertPreTokenizer, 
	PreTokenizer
)
from transformers import PreTrainedTokenizerFast
from typing import List, Optional, Tuple


class CustomNormalizer:
    def normalize(self, normalized: NormalizedString):
        # Most of these can be replaced by a `Sequence` combining some provided Normalizer,
        # (ie Sequence([ NFKC(), Replace(Regex("\s+"), " "), Lowercase() ])
        # and it should be the prefered way. That being said, here is an example of the kind
        # of things that can be done here:
        normalized.nfkc()
        normalized.filter(lambda char: not char.isnumeric())
        normalized.replace(Regex("\s+"), " ")
        normalized.lowercase()


class PyCantonesePreTokenizer:
    def pyc_split(self, i: int, normalized_string: NormalizedString) -> List[NormalizedString]:
        # handle NoneType properly
        if normalized_string is None:
            noramlized_string = NormalizedString("")
        splits = []
        try:
            for token, start, stop in self.custom_segment(str(normalized_string)):
                splits.append(normalized_string[start:stop])
        except TypeError as te:
            print("PreTokenizer pyc_split TypeError:", te)
            print(normalized_string)
        return splits
    
    def custom_segment(self, input_str: str):
        #segmenter = Segmenter() # possible attributes: disallow, allow, max_word_length
        # if not used, max_word_length = 5 is used
        pyseg = pycantonese.segment(input_str) #, cls=segmenter
        tokenized = []
        for word in pyseg:
            start = input_str.find(word)
            end = start + len(word)
            if start > -1:
                tokenized.append((word, start, end))
        return tokenized

    def pre_tokenize(self, pretok: PreTokenizedString):
        # Let's call split on the PreTokenizedString to split using `self.pyc_split`
        if pretok is not None:
            try:
                pretok.split(self.pyc_split)
            except TypeError as te:
                print("PreTokenizer pre_tokenize TypeError:", te)
                print(pretok)
    

class CustomDecoder:
    def decode(self, tokens: List[str]) -> str:
        return "".join(tokens)
    
    def decode_chain(self, tokens: List[str]) -> List[str]:
        return [f" {t}" for t in tokens]
        

class CantoneseTokenizerFast(PreTrainedTokenizerFast):
    def __init__(
        self,
        vocab_file=None,
        tokenizer_file=None,
        do_lower_case=True,
        unk_token="<unk>",
        sep_token="<sep>",
        pad_token="<pad>",
        cls_token="<cls>",
        mask_token="<mask>",
        tokenize_chinese_chars=True,
        strip_accents=None,
        **kwargs,
    ):
        super().__init__(
            vocab_file,
            tokenizer_file=tokenizer_file,
            do_lower_case=do_lower_case,
            unk_token=unk_token,
            sep_token=sep_token,
            pad_token=pad_token,
            cls_token=cls_token,
            mask_token=mask_token,
            tokenize_chinese_chars=tokenize_chinese_chars,
            strip_accents=strip_accents,
            **kwargs,
        )
        
        normalizer_state = json.loads(self.backend_tokenizer.normalizer.__getstate__())
        if (
            normalizer_state.get("lowercase", do_lower_case) != do_lower_case
            or normalizer_state.get("strip_accents", strip_accents) != strip_accents
        ):
            normalizer_class = getattr(normalizers, normalizer_state.pop("type"))
            normalizer_state["lowercase"] = do_lower_case
            normalizer_state["strip_accents"] = strip_accents
            self.backend_tokenizer.normalizer = normalizer_class(**normalizer_state)

        #vocab = self.backend_tokenizer.get_vocab()
        self.backend_tokenizer.pre_tokenizer = PreTokenizer.custom(PyCantonesePreTokenizer())

        self.do_lower_case = do_lower_case
        
    def __get_state__(self):
        state = self.__dict__.copy()
        state["_tokenizer"].pre_tokenizer = BertPreTokenizer()
        return state
    
    def __set_state__(self, d):
        self.__dict__ = d
        #vocab = self.__dict__["_tokenizer"].get_vocab()
        self.__dict__["tokenizer"].pre_tokenizer = PreTokenizer.custom(PyCantonesePreTokenizer())
        
    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        output = [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        if token_ids_1 is not None:
            output += token_ids_1 + [self.sep_token_id]
            
        return output
    
    def create_token_type_ids_from_sequences(
        self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None
    ) -> List[int]:
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]
        if token_ids_1 is None:
            return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep) * [0] + len(token_ids_1 + sep) * [1]
    
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> Tuple[str]:
        files = self._tokenizer.model.save(save_directory, name=filename_prefix)
        return tuple(files)
    
    def save_pretrained(
        self,
        save_directory,
        legacy_format=None,
        filename_prefix=None,
        push_to_hub=False,
        **kwargs,
    ):
        self.backend_tokenizer.pre_tokenizer = BertPreTokenizer()
        return super().save_pretrained(save_directory, legacy_format, filename_prefix, push_to_hub, **kwargs)