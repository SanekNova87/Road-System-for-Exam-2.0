import paths

class RoadObject:
    def __init__(self, kind, x, y, name, **props):
        self.kind = kind
        self.x = x
        self.y = y
        self.name = name
        self.rotation = 0
        self.props = dict(props) if props else {}

    def layer(self):
        return 2 if self.kind in ("car", "pedestrian") else 1

    def image_path(self):
        if self.kind == "car":
            return paths.car_image(self.props.get("color", "red"))
        return paths.IMAGE_FILES.get(self.kind, paths.BLOCK)

class RoadNetwork:
    def __init__(self):
        self.objects = {}
        self.grid = {}
        self._counter = 1

    def add(self, kind, x, y, **props):
        name = kind + "_" + str(self._counter)
        self._counter += 1
        if (x, y) in self.grid:
            old = self.grid[(x, y)]
            if old in self.objects:
                del self.objects[old]
        obj = RoadObject(kind, x, y, name, **props)
        self.objects[name] = obj
        self.grid[(x, y)] = name
        return obj

    def get(self, x, y):
        name = self.grid.get((x, y))
        return self.objects.get(name) if name else None

    def get_by_name(self, name):
        return self.objects.get(name)

    def remove(self, name):
        if name in self.objects:
            obj = self.objects[name]
            if self.grid.get((obj.x, obj.y)) == name:
                del self.grid[(obj.x, obj.y)]
            del self.objects[name]

    def sorted_by_layer(self):
        return sorted(self.objects.values(), key=lambda o: o.layer())
