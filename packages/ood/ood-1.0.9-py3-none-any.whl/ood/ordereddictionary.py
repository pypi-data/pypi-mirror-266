import weakref

import ood.selectors as s
import ood.exceptions as e

class Observer():
    _type="item"
    _child_type="item"
    # Needs to accept a custom indexer
    def __init__(self, *args, **kwargs):
        self._strict_index = kwargs.pop('strict_index', None)
        self._name_conflict = kwargs.pop('name_conflict', None)
        self._redundant_add = kwargs.pop('redundant_add', None)

        self._items_ordered = []
        self._items_by_name = {}
        self._items_by_id = {}

        self._child_option_funcs = {}
        self._child_update_funcs = {}
        self._add_listener("old_name", self._child_options_new_name, self._child_update_new_name)

        super().__init__(*args, **kwargs)

    def set_strict_index(self, level):
        self._strict_index = level
    def set_name_conflict(self, level):
        self._name_conflict= level
    def set_redundant_add(self, level):
        self._redundant_add = level

    def __len__(self):
        return len(self._items_ordered)

    def __iter__(self):
        self._iterator_index = 0
        return self

    def __next__(self):
        if self._iterator_index < len(self._items_ordered):
            ret = self._items_ordered[self._iterator_index]
            self._iterator_index += 1
            return ret
        raise StopIteration

    def _add_item_to_by_name(self, item, name=None): # do we have verify this?
        if name is None:
            name = item.get_name()
        if name in self._items_by_name:
            self._items_by_name[name].append(item)
        else:
            self._items_by_name[name] = [item]

    def _remove_item_from_by_name(self, item, name=None):
        if name is None:
            name=item.get_name()
        if name in self._items_by_name:
            self._items_by_name[name].remove(item)
            if len(self._items_by_name[name]) == 0:
                del self._items_by_name[name]

    def _add_listener(self, kwarg, option, update):
        self._child_option_funcs[kwarg] = option
        self._child_update_funcs[kwarg] = update

    def _child_options_new_name(self, child, **kwargs):
        old_name = kwargs.get('old_name')
        if old_name is not None and old_name in self._items_by_name:
            if not isinstance(child.get_name(), str):
                raise TypeError(f"All {self._child_type} must have a get_name() function which returns a string.")
            elif self._check_key(child.get_name()):
                err = e.NameConflictException(kind=self._type, level=self._name_conflict)
                if err: raise err

    def _child_update_new_name(self, child, **kwargs):
        self._child_options_new_name(child, **kwargs)
        old_name = kwargs.get('old_name', None)
        if old_name is not None:
            self._remove_item_from_by_name(child, name=old_name)
            self._add_item_to_by_name(child)

    def _child_options(self, child, **kwargs):
        for arg in kwargs:
            if arg in self._child_option_funcs:
                self._child_option_funcs[arg](child, **{arg:kwargs[arg]})

    def _child_update(self, child, **kwargs):
        for arg in kwargs:
            if arg in self._child_option_funcs:
                self._child_update_funcs[arg](child, **{arg:kwargs[arg]})

    def _abs_index(self, index):
        return index if index >= 0 else len(self)+index

    # might take before or after as well
    def add_items(self, *items, **kwargs):
        position = kwargs.pop("position", len(self))
        if not position == len(self) and not self._check_index(position):
            raise IndexError("Cannot supply a index out of range")
        position = self._abs_index(position)

        if len(items) != len(set(items)):
            err = e.RedundantAddException({"args":items}, kind=self._type, level=self._redundant_add)
            if err: raise err
            items = list(dict.fromkeys(x for x in items).keys())
        names = {}
        for item in items:
            if not isinstance(item, Observed) or not hasattr(item, "get_name") or not hasattr(item, "_register_parent"):
                raise TypeError(f"All items added must of type {self._child_type}.")
            elif id(item) in self._items_by_id:
                err = e.RedundantAddException({self._type:item.get_name()}, kind=self._type, level=self._redundant_add)
                if err: raise err
                continue
            elif not isinstance(item.get_name(), str):
                raise TypeError(f"get_name() must always return a string")
            elif self._check_key(item.get_name()) or item.get_name() in names:
                err = e.NameConflictException({self._type:item.get_name()}, kind=self._type, level=self._name_conflict)
                if err: raise err
            item._register_parent(self)
            item._deregister_parent(self) # testing! 1 2 3
            names[item.get_name()] = True
        for i, item in enumerate(items):
            if id(item) in self._items_by_id:
                err = e.RedundantAddException({self._type:item.get_name()}, kind=self._type, level=self._redundant_add)
                if err: raise err
                continue
            item._register_parent(self)
            self._items_ordered.insert(position+i, item)
            self._add_item_to_by_name(item)
            self._items_by_id[id(item)] = item

    # Will throw IndexErrors if any number is out of range
    def _check_index(self, index, target = None):
        if not isinstance(index, (int, slice)): return False
        if target is None:
            target = self._items_ordered
        if isinstance(index, int):
            if not index == -len(target) and abs(index) >= len(target):
                return False
        elif isinstance(index, slice):
            if index.start is not None:
                if not self._check_index(index.start): return False
            if index.stop is not None:
                if not self._check_index(index.stop-1): return False
        return True

    def _count_dictionary(self):
        count = 0
        for v in self._items_by_name.values():
            count += len(v)
        return count

    # This should throw an error if name not in dictionary
    def _check_key(self, name):
        if name not in self._items_by_name:
            return False
        return True

    # Throws key/index errors
    def _get_items_by_name(self, name, index=slice(None)):
        if not self._check_key(name): return []
        if not self._check_index(index): return []
        items = self._items_by_name[name][index]
        if not isinstance(items, list):
            return [items]
        return items

    # Throws key/index errors
    def _get_items_by_slice(self, indices):
        if not self._check_index(indices): return []
        return self._items_ordered[indices]

    # Throws key/index errors
    def _get_item_by_index(self, index):
        if not self._check_index(index): return
        return self._items_ordered[index]

    # Can return an empty list if a) no selectors supplied or b) skip_bad=True.
    # If selector makes no sense (4.5), will still throw error.
    def get_items(self, *selectors, **kwargs):
        strict_index = kwargs.get('strict_index', self._strict_index)
        exclude = kwargs.pop('exclude', None)
        excluded = []
        if exclude:
            excluded = self.get_items(*exclude)
        sort = kwargs.get('sort', True)
        items = []
        if not selectors or selectors[0] is None:
            items = self._items_ordered.copy()
            selectors = []
        for i, selector in enumerate(selectors):
            new_items = None
            if isinstance(selector, int):
                new_items = [self._get_item_by_index(selector)]
            elif isinstance(selector, slice):
                new_items = self._get_items_by_slice(selector)
            elif isinstance(selector, str):
                new_items = self._get_items_by_name(selector)
            elif isinstance(selector, s.Selector):
                new_items = selector._process(self)
            else:
                raise e.SelectorTypeError(f"Selectors must be: str, int, slice, {self._child_type} or Selectors. Not {type(selector)}: {selector}")
            if new_items and len(new_items)>0:
                items.extend(new_items)
            else:
                err = e.StrictIndexException(f"Selector {i}, {selector}.", kind=self._type, level=strict_index)
                if err: raise err
        for to_exclude in excluded:
            while True:
                try:
                    items.remove(to_exclude)
                except ValueError:
                    break
        resulting_items_by_id = {}
        if sort == False: return items
        for item in items:
            if id(item) not in resulting_items_by_id:
                resulting_items_by_id[id(item)] = item
        sorted_items = []
        for ref_item in self._items_ordered:
            if id(ref_item) in resulting_items_by_id:
                sorted_items.append(ref_item)
        return sorted_items

    def get_item(self, selector, **kwargs):
        if selector is None: raise ValueError(f"get_{self._type}() not passed selector")
        match = kwargs.get('match', 0)
        strict_index = kwargs.get('strict_index', self._strict_index)
        items = self.get_items(selector, **kwargs)
        if len(items) <= match:
            err = e.StrictIndexException(kind=self._type, level=strict_index)
            if err: raise err
            return None
        return items[match]

    # Because we can't check to see if we've supplied a correct object type, we can only return true or false
    def has_item(self, selector):
        if selector is None: raise ValueError(f"has_{self._type}() not passed selector")
        try:
            self.get_item(selector, strict_index=True)
            return True
        except (e.StrictIndexException):
            return False

    # Can throw regular IndexError if one value of the keys is out of order
    def reorder_all_items(self, order): # take other selectors
        if not isinstance(order, list): raise TypeError("You must provide a list of selectors to reorder the items")
        positions_new = []
        for i, selector in enumerate(order):
            if isinstance(selector, int):
                positions_new.append(selector)
            else:
                # no name conflict setting would have trouble here
                positions_new.append(self._items_ordered.index(self.get_item(selector, strict_index=True)))
        if not ( len(set(positions_new)) == len(order) == len(positions_new) == len(set(order)) == len(self) ):
            raise e.SelectorError("You must provide a list of all objects by some selector.") from ValueError()
        self._items_ordered = [self._items_ordered[i] for i in positions_new]

    def move_items(self, *selectors, **kwargs):
        position = kwargs.pop("position", None)
        distance = kwargs.pop("distance", None)
        before = kwargs.pop("before", None)
        after = kwargs.pop("after", None)

        count_flags = bool(before) + bool(after) + bool(distance) + bool(position is not None)
        if count_flags != 1:
            raise ValueError("You must set ONE of 'position', 'distance', 'before', or 'after'")
        temp = self._strict_index
        if temp == e.ErrorLevel.IGNORE or not temp:
            temp = e.ErrorLevel.WARN
        items = self.get_items(*selectors, strict_index=temp)
        if not items or len(items) == 0: return
        if position is not None: # set position specifically
            if position != len(self) and not self._check_index(position):
                raise IndexError("Position must be a valid index")
            position = self._abs_index(position)
            if position != len(self):
                # rightmost items inserted first, they'll be pushed further right w/ each successive
                # insertion.
                # unless position == len(self), which is append()
                items = reversed(items)
            for item in items:
                original_index = self._items_ordered.index(item)
                self._items_ordered[original_index] = None # Don't change structure of list while playing with positions!
                self._items_ordered.insert(position, item)
                self._items_ordered.remove(None)
        elif isinstance(distance, int) and distance > 0: # Move to right
            distance += 1 # again, insert naturally puts you to the left of whatever was in the position you want
            wall = len(self) # We're moving to the right, so:
            for item in reversed(items): # Move rightmost items FIRST
                position = min(self._items_ordered.index(item) + distance, len(self)) # len is rightmost max
                if position > wall: position = wall # don't move farther right than and item that started farther right
                wall = position - 1
                self.move_items(item, position=position)
        elif isinstance(distance, int) and distance < 0: # Move to left
            wall = 0 # We're moving to the left
            for item in items: # move leftmost first
                position = max(self._items_ordered.index(item) + distance, 0) # Can't move farther left than 0
                if position < wall: position = wall # Shouldn't move father left than what started farther left
                wall = position + 1
                self.move_items(item, position=position)
        elif distance: # so do nothing if distance = 0
            raise TypeError("distance must be an integer")
        elif before: # Move items just before some item (this is exactly the same as position, to be honest)
            position = self._items_ordered.index(self.get_item(before, strict_index=True))
            self.move_items(*items, position=position)
        elif after: # It's before except +1
            position = self._items_ordered.index(self.get_item(after, strict_index=True)) + 1
            self.move_items(*items, position=position)

    def pop_items(self, *selectors, **kwargs):
        strict_index = kwargs.pop('strict_index', True) # Better strict here unless overridden
        items = self.get_items(*selectors, strict_index=strict_index, **kwargs)
        for item in items:
            item._deregister_parent(self)
            self._items_ordered.remove(item)
            self._remove_item_from_by_name(item)
            del self._items_by_id[id(item)]
        return items

    def abandon(self):
        self.pop_all()
        if hasattr(super(), "abandon"): super().abandon() # is this really necessary?

class Observed(s.Selector):
    _type="item"
    def __init__(self, *args, **kwargs):
        self._name = kwargs.pop('name', "unnamed")
        if not isinstance(self._name, str):
            raise TypeError(f"Name must be a string, please, not {self._name}")
        self._multi_parent = kwargs.pop('multi_parent', None)
        self._parents_by_id = weakref.WeakValueDictionary({})

        super().__init__(*args, **kwargs)

    def set_multi_parent(self, level):
        self._multi_parent = level

    ## Sort of an odd function here- could make a _get_item_by_id but it's overkill.
    def _process(self, parent):
        if id(self) in parent._items_by_id:
            return [self]
        return []

    def get_name(self):
        return self._name

    def set_name(self, name):
        if self._name == name: return
        old_name = self._name
        self._name = name
        try:
            self._notify_parents(old_name=old_name)
        except Exception as e:
            self._name = old_name
            raise e

    def _register_parent(self, parent):
        if id(parent) in self._parents_by_id: return
        if len(self._parents_by_id)>=1: # worried that weakref won't work fast enough
            err = e.MultiParentException(kind=self._type, level=self._multi_parent)
            if err: raise err
        self._parents_by_id[id(parent)] = parent

    def _deregister_parent(self, *parents): # should be plural
        for parent in parents:
            if id(parent) in self._parents_by_id:
                try:
                    del self._parents_by_id[id(parent)]
                except:
                    pass

    def _get_parents(self):
        return list(self._parents_by_id.values())

    def _notify_parents(self, **kwargs):
        if len(self._parents_by_id) == 0: return
        for parent in self._parents_by_id.values():
            parent._child_options(self, **kwargs)
        for parent in self._parents_by_id.values():
            parent._child_update(self, **kwargs)

    def abandon(self):
        self._deregister_parent(*self._get_parents())
        if hasattr(super(), "abandon"): super().abandon() # and is this really necessary?
