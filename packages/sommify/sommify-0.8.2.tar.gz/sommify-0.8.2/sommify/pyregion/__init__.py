from collections import namedtuple

from thefuzz import fuzz, process

from .data import regions as data

flatten = lambda l: [item for sublist in l for item in sublist]

# create a namedtuple
Region = namedtuple(
    "Region",
    [
        "name",
        "synonyms",
        "parent",
        "subregions",
        "country",
    ],
)


def get_subregions(branch):
    obj = Region(
        name=branch["name"],
        synonyms=branch.get("synonyms", []),
        parent=branch.get("parent", None),
        subregions=list(map(lambda x: x["name"], branch.get("subregions", []))),
        country=branch["country"],
    )

    return [
        obj,
        *flatten(
            [
                get_subregions(
                    {
                        **subbranch,
                        "parent": branch["name"],
                        "country": branch["country"],
                    }
                )
                for subbranch in branch.get("subregions", [])
            ]
        ),
    ]


class ExistingRegions:
    __slots__ = ["regions", "region_tree", "_synonym_to_name"]

    def __init__(self):
        self.regions = sorted(
            flatten([get_subregions(branch) for branch in data]),
            key=lambda x: x.name,
        )
        self.region_tree = data
        self._synonym_to_name = {}
        for region in self.regions:
            self._synonym_to_name[region.name] = region.name
            for synonym in region.synonyms:
                self._synonym_to_name[synonym] = region.name

    def __getitem__(self, key):
        return self.regions[key]

    def __len__(self):
        return len(self.regions)

    def __iter__(self):
        yield from self.regions

    def __repr__(self):
        return f"ExistingRegions({self.regions})"

    def __str__(self):
        return f"ExistingRegions({self.regions})"

    def get(self, **kwargs):
        for region in self.regions:
            if all(getattr(region, key) == value for key, value in kwargs.items()):
                return region

    def flatten_branch(self, branch):
        return [
            self.get(name=branch["name"]),
            *flatten(
                [
                    self.flatten_branch(subregion)
                    for subregion in branch.get("subregions", [])
                ]
            ),
        ]

    def find_branch(self, name, branch=None):
        if branch == None:
            branch = self.region_tree

        for region in branch:
            if region["name"] == name:
                return region

            res = self.find_branch(name, region.get("subregions", []))

            if res != None:
                return res

        return None

    def get_descendants(self, region):
        branch = self.find_branch(region if isinstance(region, str) else region.name)

        if branch == None:
            return []

        return self.flatten_branch(branch)[1:]

    def search_fuzzy(self, name, threshold=82):
        name, distance = process.extractOne(
            name, self._synonym_to_name.keys(), scorer=fuzz.QRatio
        )

        if distance < threshold:
            return None

        return self.get(name=self._synonym_to_name[name])

    def find_closest_geo(self, region, subset=None):
        """Find geographically closest region to name in subset. Ordering of closeness is:
        0. regions that are children of name
        1. regions that are siblings of name (same parent)
        2. regions that are cousins of name (same grandparent)
        ...
        N. same country
        """

        if isinstance(region, str):
            region = self.get(name=region)

        if subset == None:
            subset = self.regions

        # check regional hierarchy
        current = region
        while current:
            descendants = self.get_descendants(current)
            descendants = [d for d in descendants if d in subset and d != region]
            if len(descendants) > 0:
                return descendants

            current = self.get(name=current.parent)

        # check country
        same_country = [
            r for r in subset if r.country == region.country and r != region
        ]
        if len(same_country) > 0:
            return same_country

        return None


regions = ExistingRegions()
