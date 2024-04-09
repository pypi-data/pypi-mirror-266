import os.path
import json
from jsonschema import RefResolver


class ExtendedRefResolver(RefResolver):
    def resolve_remote(self, uri):
        print(f"Resolving URI: '{uri}'")

        path = None

        if uri.startswith("file:"):
            path = uri[len("file:") :]
            if path.startswith("//"):
                path = path[len("//") :]

        elif os.path.isfile(uri):
            path = uri

        if path is not None:
            return self.resolve_local(path)
        else:
            return super().resolve_remote(uri)

    def resolve_local(self, path: str):
        with open(path) as file:
            schema = json.load(file)

        if self.cache_remote:
            self.store[path] = schema
        return schema
