from viggocore.common.subsystem.driver import Driver
from viggocore.common.subsystem import operation
from viggocore.common import exception


class Manager(object):

    def __init__(self, driver: Driver) -> None:
        self.driver = driver

        self.create = operation.Create(self)
        self.get = operation.Get(self)
        self.list = operation.List(self)
        self.update = operation.Update(self)
        self.delete = operation.Delete(self)
        # NOTE(samueldmq): what do we use this for ?
        self.count = operation.Count(self)

    def init_query(self, session, order_by, resource):
        raise exception.BadRequest(
            f'Method _init_query() not implemented for {resource.__name__}.')

    def valid_dinamic_order_by(self, order_by):
        result = False
        count_points = order_by.count('.')
        if ('.' in order_by and count_points == 1) or count_points == 0:
            result = True
        elif count_points > 1:
            raise exception.BadRequest(
                'order_by item cannot have more than one point.')
        return result
