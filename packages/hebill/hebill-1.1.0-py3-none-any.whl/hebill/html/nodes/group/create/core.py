class Create:
    def __init__(self, sir):
        self.senior = sir
        self._nodes = None
        self._tags = None
        self._components = None

    @property
    def node(self):
        if self._nodes is None:
            from .nodes.core import Nodes
            self._nodes = Nodes(self.senior)
        return self._nodes

    @property
    def tag(self):
        if self._tags is None:
            from .tags.core import Tags
            self._tags = Tags(self.senior)
        return self._tags

    @property
    def component(self):
        if self._components is None:
            from .components.core import Components
            self._components = Components(self.senior)
        return self._components
