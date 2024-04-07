Usage Sample
''''''''''''

.. code:: python

        from nlpx.text_token import Tokenizer

        if __name__ == '__main__':
            corpus = ...
            tokenizer = Tokenizer(corpus)
            sent = 'I love you'
            tokens = tokenizer.encode(sent, max_length=6, pad_begin_end=True)
            # [101, 66, 88, 99, 102, 0]
            sent = tokenizer.decode(sent)
            # ['<bos>', 'I', 'love', 'you', '<eos>', '<pad>']
