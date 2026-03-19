
import natsort

class Sort:

    class Natural:

        @staticmethod
        def sorted(iterable, key=None):
            '''
            Sort a list, via a key-string, according to criteria used by Windows Built-in Application(s) (e.g., File Explorer).
        
            Note that, similar to Python's built-in `sorted`, creates a new list.
            '''
            return natsort.natsorted(iterable, key=key)
        
        @staticmethod
        def sort(iterable, key=None):
            '''
            Sort a list, via a key-string, according to criteria used by Windows Built-in Application(s) (e.g., File Explorer).
        
            Note that, similar to Python's built-in `sort`, sorts in-place.
            '''
            natsort_key = natsort.natsort_keygen()
            kwargs = {}
            if key != None:
                kwargs['key'] = lambda x: natsort_key(key(x))
            iterable.sort(**kwargs)