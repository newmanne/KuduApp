# Keys for caching
class CacheKeys(object):
    FEASIBILITY_GRAPH = "FeasibilityGraph"
    FEASIBILITY_DATAFRAME = "FeasibilityDataFrame"

    TRAVEL_TIME_MATRIX = "TravelTimeMatrix"
    TRAVEL_TIME_PARISH_INDEX = "TravelTimeParishIndex"

    CLEARING_LOCK = "Clearing"

    @classmethod
    def __for_produce(self, k, produce_id):
        return "{}:{}".format(k, produce_id)

    @classmethod
    def feasibility_graph(cls, produce_id):
        return cls.__for_produce(cls.FEASIBILITY_GRAPH, produce_id)

    @classmethod
    def clearing_lock(cls, produce_id):
        return cls.__for_produce(cls.CLEARING_LOCK, produce_id)